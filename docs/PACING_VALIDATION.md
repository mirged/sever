# Native render pacing — 2026-10-18

The event loop previously rebuilt and submitted the entire scene on every poll,
including polls between simulation ticks. A dedicated typed Maylang render pacer
now schedules 60 Hz deadlines independently of input and physics. Event delivery
can wake the 0..17 ms poll early without forcing a redraw. Missed frames are not
queued for catch-up. The final tick-limited scene is always drawn.

## Checks executed

- `python3 tools/dev.py check`: valid mailboxes, 15 protocol checks and all target
  type checks pass.
- `python3 tools/dev.py test`: 14 Maylang suites pass, including 21 new pacing
  assertions. They cover early events, exact deadlines, slight lateness, long
  stalls, backward clock jumps, the pinned NaN behavior and recovery. A synthetic
  1000-poll second schedules exactly 60 frames.
- `python3 tools/dev.py run render-check`: seven software render checks pass.
- Native `workshop -- --cut-demo --ticks 600`: completes exactly 600 ticks with
  `stop_reason: tick_limit`, one cut, one respawn and the exit reached. All game
  outcome fields match a headless run of the same scenario.

The native report records 733 event polls and 389 rendered frames, demonstrating
that input polling no longer implies a full redraw. Renderer: Sokol/OpenGL on
Mesa Intel Iris Xe (RPL-P). Application time was about 31.95 seconds with 20.83
seconds discarded by the existing bounded simulation clock. A preceding uncapped
120-tick baseline took 11.09 seconds with 9.08 discarded seconds. These differently
sized runs under variable desktop load do not establish a wall-time speedup.
This change bounds redundant rendering; it does not resolve all native stalls or
guarantee a frame rate. Native keyboard/mouse automation was not performed.

A separate five-second, three-block stack probe (2-by-0.5 m wood rectangles,
centres initially (0,.25), (.12,.75), (.24,1.25), gravity -24) stayed finite, but
ended with vertical speeds approximately -.0131, -.1113 and -.1434 m/s. The
single-point contact solver remains a stability limitation. Agent 2 owns the
pending two-point manifold; this change does not alter geometry or impulses.

Build and measurement outputs remain ignored inside the workspace.
