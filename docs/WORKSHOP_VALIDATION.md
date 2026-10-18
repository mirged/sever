# Movement lab validation — 2026-10-18

The game model, controller, timing, projection, input handling and polygon fill
are typed Maylang. The native target builds the pinned Maylang UI adapter;
no C gameplay or Maylang source changes were made.

## Checks actually executed

- `python3 tools/dev.py check`: mailboxes valid, 12 protocol tests pass, all
  application and test targets type-check.
- `python3 tools/dev.py test`: three Maylang executables pass: 21 original
  model assertions, 23 movement/timing assertions, and 5 projection assertions.
- `python3 tools/dev.py run render-check`: 7 native software rendering checks
  pass, covering player visibility, convex fill, reversed winding, clipping,
  and input immutability.
- `python3 tools/dev.py run workshop -- --headless --demo --ticks 600
  --snapshot build/workshop.png --report build/workshop.json`: completed,
  zero deaths, final position approximately `(10.8667, 4.25)`.
- `python3 tools/dev.py run workshop -- --demo --ticks 600
  --snapshot build/native-workshop.png --report build/native-workshop.json`:
  completed in about 11 seconds including the build/run helper, zero deaths,
  using `Sokol GPU / OpenGL · Mesa Intel(R) Iris(R) Xe Graphics (RPL-P)`.

The headless screenshot was visually inspected. Native snapshots use the UI
adapter's software reference renderer; they are not GPU readbacks. The live
native run verifies window/context lifecycle and automatic traversal. External
keyboard/mouse automation and manual keyboard play were not performed in this
session. Early native autoplay attempts timed out; after separating autoplay
from focus gating, a 60-tick and final 600-tick run completed successfully.

## Current limits

The room is a movement course with static rectangle contacts. Cables and the
overhead slab are scenery. Cutting is deliberately offline in the native UI;
the geometry kernel must be reviewed and connected to convex contact handling
before fragments can become gameplay. No enemies, angular dynamics, cable
constraints, audio, or saved progress are implemented.

Default CI validates model/protocol/type checks without needing native graphics
development packages. Native checks are explicit targets and require the host
dependencies listed in the README. Build outputs, reports and previews remain
ignored beneath `build/` and `.may/`.
