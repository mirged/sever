#!/usr/bin/env python3
"""Run the pinned sibling Maylang toolchain without using a home installation."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
TOOLS = ROOT / ".tools"


def inside(path):
    resolved = path.resolve()
    if not resolved.is_relative_to(WORKSPACE):
        raise ValueError(f"Path escapes workspace: {path}")
    return resolved


def environment():
    env = os.environ.copy()
    for name, directory in {
        "TMPDIR": TOOLS / "tmp",
        "CARGO_HOME": TOOLS / "cargo",
        "CARGO_TARGET_DIR": SOURCE / "target",
        "XDG_CACHE_HOME": TOOLS / "cache",
        "GH_CONFIG_DIR": TOOLS / "gh",
    }.items():
        inside(directory).mkdir(parents=True, exist_ok=True)
        env[name] = str(directory)
    env["MAYC"] = str(COMPILER)
    env["MAYLANG_STDLIB"] = str(inside(SOURCE / "stdlib"))
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    config = inside(TOOLS / "gitconfig")
    config.touch(exist_ok=True)
    env["GIT_CONFIG_GLOBAL"] = str(config)
    return env


def run(command, cwd=ROOT):
    print("+ " + " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), cwd=inside(cwd), env=environment(), check=True)


def verify_pin():
    inside(SOURCE)
    actual = subprocess.check_output(
        ["git", "-C", str(SOURCE), "rev-parse", "HEAD"],
        env=environment(), text=True,
    ).strip()
    if actual != PIN["source_commit"]:
        raise ValueError(f"Maylang revision mismatch: {actual}; expected {PIN['source_commit']}")
    release = json.loads(inside(SOURCE / "RELEASE.json").read_text())
    if release["version"] != PIN["version"]:
        raise ValueError("Maylang version does not match toolchain.json")


def bootstrap():
    verify_pin()
    run(["sh", "compiler/rust/build.sh"], cwd=SOURCE)
    inside(RUNNER.parent).mkdir(parents=True, exist_ok=True)
    run([COMPILER, SOURCE / "tools/may/main.may", "-o", RUNNER])
    run([COMPILER, "--version"])


def main():
    commands = {"bootstrap", "check", "test", "run", "build", "tasks"}
    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        raise ValueError("Usage: python3 tools/dev.py bootstrap|check|test|run|build|tasks [args]")
    action = sys.argv[1]
    if action == "bootstrap":
        bootstrap()
        return
    verify_pin()
    if not inside(COMPILER).is_file() or not inside(RUNNER).is_file():
        raise ValueError("Toolchain not bootstrapped; run python3 tools/dev.py bootstrap")
    if action == "check":
        run([sys.executable, ROOT / "tools/mailbox.py", "validate"])
        run([sys.executable, "-m", "unittest", "discover", "-s", "tests/tooling", "-v"])
        run([RUNNER, "check", "--all", *sys.argv[2:]])
    else:
        run([RUNNER, action, *sys.argv[2:]])


PIN = json.loads((ROOT / "toolchain.json").read_text())
SOURCE = inside(ROOT / PIN["checkout"])
COMPILER = SOURCE / "compiler/mayc/build/bin/mayc_new"
RUNNER = TOOLS / "bin/may"

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"sever: {error}", file=sys.stderr)
        sys.exit(1)
