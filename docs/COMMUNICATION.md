# Commit-and-push communication protocol v1

## Transport and authorship

Each agent uses a separate workspace checkout and a durable branch:

| Author | Branch | Only mailbox it may append to |
| --- | --- | --- |
| Agent 1 | `agent1` | `messages/agent1_to_agent2.json` |
| Agent 2 | `agent2` | `messages/agent2_to_agent1.json` |

Agent 1 integrates reviewed implementation into `main`. Initial empty mailboxes
are scaffolding, not messages from an agent that has not started. Do not edit,
delete or reorder published messages, and do not edit the other sender's file.
Fix a mistake by appending a superseding message that references the old ID.

The mailbox on the sender's **remote branch** is authoritative. A local edit or
commit is not delivery. A successful push is delivery. A separate fetched reply
is the only evidence that the peer processed it. Mailbox changes merged into
`main` are snapshots; never use them as a substitute for fetching the sender.

## Message format

Each envelope has `protocol_version`, `from`, `to`, `branch`, `last_sequence`,
`ack_sequence`, and append-only `messages`. Each message has:

- `id`: `<sender>-<four-digit-sequence>`; unique and increasing from 1.
- `sequence`: an integer; exactly previous + 1, without gaps.
- `sent_at`: UTC ISO 8601 timestamp.
- `kind`: `request`, `accept`, `proposal`, `progress`, `blocked`, `handoff`,
  `review`, or `done`.
- `task`: stable task ID, such as `geometry-v1`.
- `in_reply_to`: peer message ID or null for a new conversation.
- `summary`: one sentence describing the action or result.
- `body`: an array of concrete instructions, evidence, decisions, or blockers.
- `commits`: existing implementation SHAs, not the containing message commit.
- `paths`: affected paths or ownership claims relative to repository root.
- `checks`: objects with `command`, `result` (`pass`, `fail`, `skip`) and
  `detail`. Do not label a skipped or unexecuted check as passing.
- `needs_reply`: boolean; true when waiting for acceptance/review/clarification.

`last_sequence` is the final message sequence, or 0 for an empty envelope.
`ack_sequence` is the highest contiguous peer sequence processed, not evidence of
accepting its proposal. Acceptance/rejection must be explicit in a reply.
Validate against [the schema](../messages/schema.json) and run
`python3 tools/mailbox.py validate` before publishing.

## Receiving

```sh
python3 tools/mailbox.py read agent2  # Agent 1 receives Agent 2
python3 tools/mailbox.py read agent1  # Agent 2 receives Agent 1
```

This fetches the named remote branch and reads its mailbox with `git show`.
Read messages beyond the last acknowledged sequence. A request gets one `accept`
or `blocked` reply; update `ack_sequence` and push the reply before substantial
work. A proposal needs explicit acceptance before changing a shared interface.
Do not send acknowledgments merely to acknowledge another acknowledgment.

Fetch at task start, before touching a shared contract, before integration, and
at each coding milestone (roughly every 10–20 minutes). A 60-second poll is
reasonable while awaiting a specific reply, but stop after ten attempts and
report the pending dependency to the human. Do independent owned work while
waiting. Do not create heartbeat commits or wait indefinitely.

## Publishing

1. Commit a coherent implementation and meaningful tests on your own branch.
2. Append a mailbox message, referencing that implementation's full SHA.
3. Record checks actually run, blockers, and any requested action.
4. Validate, commit the mailbox separately, and push your branch:

```sh
python3 tools/mailbox.py validate
git add messages/agent2_to_agent1.json  # example for Agent 2
git commit -m "chore(protocol): hand off geometry-v1"
git push origin agent2
```

If push fails, keep the local commit and retry after resolving the transport
problem. Tell the human it is queued, not delivered. Never force-push.

## Integration and conflicts

Agent 2 starts from the pushed `agent2` seed branch. Agent 1 works on `agent1`.
Before beginning a new task, Agent 2 fetches `main` and merges `origin/main` into
its branch in its own checkout. Use merge commits rather than rewriting history.

A `handoff` includes the ready implementation SHA, supported behavior, tests,
limits and a precise review request. Agent 1 fetches `agent2`, reviews the diff,
merges `origin/agent2` into `agent1`, reruns project checks/tests, and merges the
accepted result into `main`. Push `agent1` and `main`, then publish a `review` or
`done` message containing the integrated SHA. Mailbox-only changes remain valid
history even if included in integration. Never cherry-pick only a mailbox and
then claim its implementation was integrated.

If files conflict, pause changes to those files and send `blocked` with paths,
the two SHAs and a proposed resolution. Do not overwrite the peer's code or
resolve an interface dispute silently. For urgent human steering, the human's
instruction takes precedence; record the resulting agreement in the mailbox.
