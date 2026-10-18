#!/usr/bin/env python3
"""Validate mailboxes and receive them from the sender's fetched remote branch."""
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "messages/schema.json").read_text())


def validate_schema(value, schema, path="mailbox"):
    # Only the JSON Schema vocabulary used by this repository's schema.
    types = {"object": dict, "array": list, "string": str, "integer": int,
             "boolean": bool, "null": type(None)}
    allowed = schema.get("type")
    if allowed:
        names = allowed if isinstance(allowed, list) else [allowed]
        if not any(type(value) is types[name] for name in names):
            raise ValueError(f"{path}: expected {allowed}")
    if "const" in schema and (type(value) is not type(schema["const"]) or value != schema["const"]):
        raise ValueError(f"{path}: invalid constant")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path}: value outside enum")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        if set(schema.get("required", [])) - value.keys():
            raise ValueError(f"{path}: missing required fields")
        if schema.get("additionalProperties") is False and value.keys() - props.keys():
            raise ValueError(f"{path}: unknown fields")
        for key, item in value.items():
            validate_schema(item, props.get(key, {}), f"{path}.{key}")
    elif isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            raise ValueError(f"{path}: empty list")
        for index, item in enumerate(value):
            validate_schema(item, schema.get("items", {}), f"{path}[{index}]")
    elif isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or (
            "pattern" in schema and not re.search(schema["pattern"], value)
        ):
            raise ValueError(f"{path}: invalid string")
        if schema.get("format") == "date-time":
            parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError(f"{path}: timestamp requires a UTC offset")
    elif type(value) is int and value < schema.get("minimum", value):
        raise ValueError(f"{path}: below minimum")


def validate(mailbox, sender):
    validate_schema(mailbox, SCHEMA)
    recipient = "agent2" if sender == "agent1" else "agent1"
    if (mailbox["from"], mailbox["to"], mailbox["branch"]) != (sender, recipient, sender):
        raise ValueError("Mailbox sender, recipient or branch is inconsistent")
    if mailbox["last_sequence"] != len(mailbox["messages"]):
        raise ValueError("last_sequence must equal the final contiguous sequence")
    for index, message in enumerate(mailbox["messages"], 1):
        if message["sequence"] != index or message["id"] != f"{sender}-{index:04d}":
            raise ValueError("Messages must have consecutive sender-owned IDs")
        reply = message["in_reply_to"]
        if reply is not None and not reply.startswith(recipient + "-"):
            raise ValueError("Reply must reference the peer's message")
        for path in message["paths"]:
            if Path(path).is_absolute() or ".." in Path(path).parts:
                raise ValueError("Message path escapes repository")
    return mailbox


def filename(sender):
    recipient = "agent2" if sender == "agent1" else "agent1"
    return f"messages/{sender}_to_{recipient}.json"


def main():
    if sys.argv[1:] == ["validate"]:
        for sender in ("agent1", "agent2"):
            validate(json.loads((ROOT / filename(sender)).read_text()), sender)
        print("PASS: both mailboxes match schema and sequence rules")
    elif len(sys.argv) == 3 and sys.argv[1] == "read" and sys.argv[2] in ("agent1", "agent2"):
        sender = sys.argv[2]
        env = os.environ.copy()
        env["GH_CONFIG_DIR"] = str(ROOT / ".tools/gh")
        env["GIT_CONFIG_NOSYSTEM"] = "1"
        env["GIT_CONFIG_GLOBAL"] = str(ROOT / ".tools/gitconfig")
        subprocess.run(["git", "fetch", "origin", f"{sender}:refs/remotes/origin/{sender}"],
                       cwd=ROOT, env=env, check=True)
        raw = subprocess.check_output(["git", "show", f"origin/{sender}:{filename(sender)}"],
                                      cwd=ROOT, env=env, text=True)
        print(json.dumps(validate(json.loads(raw), sender), indent=4))
    else:
        raise ValueError("Usage: python3 tools/mailbox.py validate | read agent1|agent2")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"mailbox: {error}", file=sys.stderr)
        sys.exit(1)
