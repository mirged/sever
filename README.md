# sever

A physics platformer about cutting the world apart. Slice platforms into ramps,
drop machinery by severing cables, dismantle enemies, and turn debris into weapons.

**Status: native movement prototype.** Run and jump through a small platform
course, reach the exit, pause, and reset. In-game cutting, dynamic fragments,
enemies, and machinery remain later milestones.

The convex cutting kernel is implemented, reviewed and merged as a library.
See [its contract and numeric limits](src/geometry/README.md) and
[Agent 1's integration review](docs/GEOMETRY_REVIEW.md). It is not yet connected
to the movement lab's rectangle-only contact handling.

Gameplay and simulation use high-level, strictly typed Maylang. Python is limited
to development tooling. The graphical client uses Maylang's native UI adapter;
the world, controller, timing, projection and polygon fill all remain Maylang.

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

Launch the native movement lab:

```sh
python3 tools/dev.py run workshop
```

Move with **A/D** or **Left/Right**, jump with **Space/W/Up**, pause with **P**,
reset with **R**, and close with **Esc**. Normal play pauses when focus is lost.
The training course currently uses static axis-aligned rectangle collisions;
arbitrary cut fragments are not yet wired into the controller.

The native target needs the host C compiler and X11/Xi/Xcursor/OpenGL development
libraries. Interactive play needs X11/XWayland and OpenGL 4.3. A vendored,
OFL-licensed IBM Plex Mono font keeps runtime font reads inside the workspace;
the helper selects it automatically. Attribution is in
[assets/fonts/SOURCE.json](assets/fonts/SOURCE.json) and
[the font license](assets/fonts/OFL.txt).

Render and test without opening a window:

```sh
python3 tools/dev.py run render-check
python3 tools/dev.py run workshop -- --headless --demo --ticks 600 --snapshot build/workshop.png --report build/workshop.json
```

`--demo` follows a deterministic traversal. Without `--demo`, a headless run
leaves the player at spawn. Native autoplay can also run with `--ticks 600` and
does not pause on focus loss. `--report` records the tick count, result, deaths,
renderer, frame count, wall time and discarded catch-up time. Generated previews
stay in ignored `build/`; the default `run` target remains the original model
smoke demonstration so CI does not need a display.

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
