# sever

A physics platformer about cutting the world apart. Slice platforms into ramps,
drop machinery by severing cables, dismantle enemies, and turn debris into weapons.

**Status: scaffold, not a playable game.** The initial executable runs a
deterministic model demonstration. Arbitrary cuts, collision response, enemies,
and a playable level are milestones, not completed features.

Gameplay and simulation use high-level, strictly typed Maylang. Python is limited
to development tooling. The first graphical client will use Maylang's native UI;
C FFI is reserved for a small adapter if profiling justifies it.

## Start

Keep the existing Maylang checkout alongside this repository:

```text
workspace/
    maylang/        # pinned source checkout; do not modify its source
    sever/
```

From `sever/`, build the checkout's compiler and workspace runner, then run:

```sh
python3 tools/dev.py bootstrap
python3 tools/dev.py check
python3 tools/dev.py test
python3 tools/dev.py run
```

All generated files and temporary data stay in this workspace. The helper ignores
the inherited `MAYC` and `MAYLANG_STDLIB`, which may point at an older installation.
Bootstrap requires the host Rust/Cargo and C toolchains; it uses no registry
dependencies and runs Cargo offline. See [the toolchain pin](toolchain.json).

## Two-agent development

- Agent 1 owns gameplay, rendering, integration, and shared contracts.
- Agent 2 owns cutting geometry and its numerical tests.
- Each has an independent workspace, clone, pinned Maylang checkout and GitHub
  authentication, and writes only its outbound mailbox on its own branch.
- A message is delivered only after its commit is pushed. Read the peer's
  mailbox from their fetched remote branch, not from a stale local file.

Read [AGENTS.md](AGENTS.md), [the protocol](docs/COMMUNICATION.md),
[the architecture](docs/ARCHITECTURE.md), and [the roadmap](docs/ROADMAP.md).
The complete second-agent prompt is in [docs/AGENT2_PROMPT.md](docs/AGENT2_PROMPT.md).
Recorded checks and current limitations are in [docs/STATUS.md](docs/STATUS.md).

No project license has been selected yet. The sibling Maylang checkout and any
future native dependencies retain their own licenses.
