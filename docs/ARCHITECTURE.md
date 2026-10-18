# Architecture and shared contracts

## Modules

| Module | Owner | Responsibility |
| --- | --- | --- |
| `src/core/types.may` | Agent 1 | Vec2, Polygon, Body, Cable, World |
| `src/core/math.may` | Agent 1 | Vector helpers, polygon area, rectangle construction |
| `src/game/world.may` | Agent 1 | Initial room data |
| `src/physics/step.may` | Agent 1 | Fixed-step free flight; contacts come later |
| `src/geometry/slice.may` | Agent 2 | Convex polygon validation and splitting |
| `src/game/training.may` | Agent 1 | Kinematic movement, static rectangle contacts, reset/exit course |
| `src/game/timing.may` | Agent 1 | Fixed-step accumulator with bounded catch-up |
| `src/render/` | Agent 1 | Camera projection and native UI draw commands |
| `desktop.may` | Agent 1 | Native window, input, headless preview, report and lifecycle |
| `main.may` | Agent 1 | Original headless model smoke demo |

Maylang structs are shared mutable references. Functions that compute geometry
must return fresh vertices and must not mutate input polygons. Bodies store
local vertices; position/angle transform them into world space. Rendering never
owns simulation state. Geometry receives all coordinates in one caller-selected
space and does not transform body state.

## Coordinates and simulation

Use Float world coordinates, positive X right, positive Y up, radians
counterclockwise. A rectangle's vertices are counterclockwise. Physics uses
`1.0 / 60.0` seconds per fixed tick. The native loop accumulates wall time,
clamps each elapsed frame to 0..0.25 seconds, and takes at most eight fixed ticks
per frame. Excess whole ticks are discarded and reported. Pausing/focus loss
clears the backlog; normal play buffers a short jump press until the next tick.
The wall clock can jump, so negative deltas are ignored. This is not a monotonic
timing guarantee. Autoplay intentionally runs without keyboard focus.

The original free-flight demonstration remains semi-implicit Euler. The movement
lab is a separate kinematic controller: a 0.6-by-1.3 player, four substeps per
fixed tick, horizontal/vertical swept boundary crossings against static,
axis-aligned rectangles, ground/ceiling/side response, a fall reset and exit.
These contact rules do not support rotated, dynamic, or arbitrary convex
fragments. Do not feed cut pieces into this controller as bounding boxes; add
convex contacts before integrating physical cuts.

Rendering transforms local polygon vertices by angle and position, then fits the
room into a clipped camera. Convex fill is high-level Maylang scan conversion;
the thin typed FFI calls only the existing native UI drawing primitives. No
pixel-pointer buffer or C gameplay implementation is involved. The renderer can
draw convex pieces independently of the controller's current contact limits.

`Body.dynamic` controls integration. `Body.cuttable` is independent: static
terrain can be cut, while some dynamic objects may be protected by design.
Materials are strings for now; a later material table will own density/toughness.
Cables identify an attached body and use world-space anchors. An intact cable
does not yet constrain physics; that work belongs to milestone 3.

## Geometry API v1 (authorized for Agent 2)

Implemented in `src/geometry/slice.may` with these public declarations:

```may
pub struct SliceResult {
    status: Str,
    pieces: List<Polygon>
}

pub fun split_convex(shape: Polygon, start: Vec2, end: Vec2, epsilon: Float) -> SliceResult
```

Import `../core/types.may` and `../core/math.may` as needed. `Polygon` wraps
`vertices: List<Vec2>`. `status` is exactly `split`, `miss`, or `invalid`.
`split` returns two positive-area convex polygons with the original winding.
`miss` and `invalid` return an empty pieces list. No mutation, I/O, randomness,
physics, or native calls. Agent 1 accepts this interface now; changes need a
mailbox proposal and acceptance.

Validate finite coordinates, at least three distinct vertices, simple convex
input, positive tolerance and a nondegenerate blade. Either winding is allowed.
Reject duplicate/zero-length edges. Document a consistent collinearity policy.
The finite blade must reach both boundary intersections: its infinite supporting
line alone is not sufficient. Starting inside and ending outside is a `miss`;
grazing or cutting along an edge is a `miss`. Boundary-to-boundary traversal
through the interior can split. Compare tolerances in world-distance units,
independent of blade length. Use epsilon-aware checks and compare areas within
a scale-appropriate tolerance.

Tests must include horizontal/vertical/diagonal splits, reversed winding and
blade direction, misses, grazing, vertex hits, a finite segment too short to
cross the shape, invalid inputs, tiny slivers, and area conservation. Report
the supported numeric range; do not claim robust exact arithmetic.
