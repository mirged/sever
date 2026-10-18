# Native cutting prototype — 2026-10-18

Implementation milestone: `bad00dd` on `agent1`. Gameplay, fragment creation,
rigid impulses, character contacts and rendering use high-level typed Maylang.
The compiler remains pinned to `beb593cdcffb2ff4c30db060686c3eb312807d62`
(Maylang 0.13.102); no Maylang source was changed.

## Executed checks

| Command | Observed result |
| --- | --- |
| `python3 tools/dev.py check` | 15 protocol checks pass, mailboxes valid, all targets type-check |
| `python3 tools/dev.py test` | 13 Maylang executable suites pass |
| `python3 tools/dev.py run render-check` | 7 native software-render checks pass |
| `python3 tools/dev.py run workshop -- --headless --demo --ticks 600 --report build/traversal.json` | Exit reached, zero deaths, no cuts |
| `python3 tools/dev.py run workshop -- --headless --cut-demo --ticks 600 --snapshot build/cutting.png --report build/cutting.json` | One cut, one respawn, exit reached |
| `python3 tools/dev.py run workshop -- --headless --cut-demo --ticks 100 --snapshot build/cutting-action.png --report build/cutting-action.json` | One cut, two dynamic fragments, zero deaths at this point |

The Maylang suites include 46 cutter/conservation checks, 22 rigid/character
checks, 37 training/timing checks, 93 analytic contact checks, 195 mass checks,
198 slicing checks, 49 geometry evidence rows, 2012 conservation splits,
1500 slicing fuzz trials and 1200 contact fuzz pairs. Contact fuzz reproduced
700 overlaps, 500 separations and zero invalid pairs independently before merge.

Fragment tests verify material-scaled mass, centroid, linear momentum and angular
momentum, including a rotating parent with an off-centre local origin. They cover
recutting, IDs, body budgets, paired sliver rejection, cable intersections and
release, cooldown and non-finite input. Contact integration checks falling/resting
boxes, head-on impacts, angular response, an actual triangular slope instead of
its AABB, cleanup, finite state and unsafe timestep rejection. The traversal
regression verifies replacement of slab 16 by two dynamic bodies and detachment
of both supports before cleanup, then recovery to the exit.

## Native verification

The final native OpenGL cut-demo completed exactly 600 requested ticks with
`stop_reason: tick_limit`, one cut, one respawn and the exit reached. Its report
records 1332 frames, about 27.06 application seconds and 14.94 discarded
catch-up seconds. The tick-limit/result assertions passed. This validates the
native lifecycle and gameplay path, while the discarded time remains a
performance limitation under the observed desktop load.

A preceding 120-tick run completed with two dynamic fragments and no
respawn yet: 251 frames, approximately 3.01 application seconds, 0.94 discarded
seconds. Another native run reached the exit and closed at tick 595: one cut,
one respawn, 2762 frames, about 17.19 application seconds and no discarded time.
That early close is not recorded as a completed 600-tick check. A first longer
attempt was terminated at its 50-second process limit after reaching tick 487.
Native timing has varied, so these observations are not a frame-rate guarantee.

Renderer: `Sokol GPU / OpenGL · Mesa Intel(R) Iris(R) Xe Graphics (RPL-P)`.
Native snapshots use the adapter's software reference renderer, not GPU readback.
The headless action and completion snapshots were visually inspected. External
keyboard/mouse automation and manual input play were not performed; autoplay
uses the same aim/cut/controller functions but bypasses keyboard focus gating.
Reports now distinguish `tick_limit`, `window_closed` and `escape`, include the
requested limit, and prevent fixed-step catch-up from overshooting that limit.

## Current limits

The blade traverses convex polygons only, with 3.5 m range and a 12-tick cooldown.
Fragments below 0.025 m² reject the entire split, and the room caps at 24 bodies.
Protected foundations retain a usable room. Cutting a supported body releases
its fragments; severing its last cable releases the original. Cables currently
model static support rather than swinging ropes or powered machinery.

The solver uses discrete 1/240-second substeps, six impulse passes and one
representative overlap point. Stable stacking and thin/fast fragments need more
work; a two-point manifold is assigned to Agent 2. The kinematic character
responds to moving surfaces but does not push rigid bodies back. Linear/angular
speed caps and out-of-room debris retirement bound the prototype. There is no
continuous collision detection, sleeping, articulated boss, enemy damage, audio
or save system. The current exit does not require constructing a bridge.

Hosted CI passed implementation `bad00dd`:
[scaffold checks](https://github.com/mirged/sever/actions/runs/39089961794).
It checks protocol, types and headless suites. Native checks remain
explicit local targets requiring the host graphics dependencies in the README.
Generated binaries, logs, reports, snapshots and credentials stay ignored inside
the workspace. Regular Git fetch/merge/commit/push is now available; the earlier
Git Data API publication workaround is historical.
