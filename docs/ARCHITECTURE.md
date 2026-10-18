# Architecture and shared contracts

## Modules

| Module | Owner | Responsibility |
| --- | --- | --- |
| `src/core/types.may` | Agent 1 | Vec2, Polygon, Body, Cable, World |
| `src/core/math.may` | Agent 1 | Vector helpers, polygon area, rectangle construction |
| `src/game/world.may` | Agent 1 | Initial room data |
| `src/physics/step.may` | Agent 1 | Fixed-step free flight; contacts come later |
| `src/geometry/slice.may` | Agent 2 | Convex polygon validation and splitting |
| `src/render/` (future) | Agent 1 | Native UI rendering and input |
| `main.may` | Agent 1 | Headless smoke demo, later game entry |

Maylang structs are shared mutable references. Functions that compute geometry
must return fresh vertices and must not mutate input polygons. Bodies store
local vertices; position/angle transform them into world space. Rendering never
owns simulation state. Geometry receives all coordinates in one caller-selected
space and does not transform body state.

## Coordinates and simulation

Use Float world coordinates, positive X right, positive Y up, radians
counterclockwise. A rectangle's vertices are counterclockwise. Physics uses
`1.0 / 60.0` seconds per fixed tick; a future render loop accumulates wall time,
clamps large pauses and limits catch-up steps. Free flight is semi-implicit Euler.
The scaffold has no collision detection, angular integration or player movement.

`Body.dynamic` controls integration. `Body.cuttable` is independent: static
terrain can be cut, while some dynamic objects may be protected by design.
Materials are strings for now; a later material table will own density/toughness.
Cables identify an attached body and use world-space anchors. An intact cable
does not yet constrain physics; that work belongs to milestone 3.

## Geometry API v1 (authorized for Agent 2)

Implement `src/geometry/slice.may` with these public declarations:

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
