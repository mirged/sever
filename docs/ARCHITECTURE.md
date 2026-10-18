# Architecture and shared contracts

## Modules

| Module | Owner | Responsibility |
| --- | --- | --- |
| `src/core/types.may` | Agent 1 | Vec2, Polygon, Body, Cable, World |
| `src/core/math.may` | Agent 1 | Vector helpers, polygon area, rectangle construction |
| `src/game/world.may` | Agent 1 | Initial room data |
| `src/physics/step.may` | Agent 1 | Original model free flight; workshop uses rigid.may |
| `src/geometry/slice.may` | Agent 2 | Convex polygon validation and splitting |
| `src/game/training.may` | Agent 1 | Kinematic convex movement, aim/cut binding, reset/exit course |
| `src/geometry/mass.may` | Agent 2 | Polygon area, centroid, centroidal polar inertia, recentering |
| `src/geometry/contact.may` | Agent 2 | SAT escape normal/depth and overlap-centroid point |
| `src/physics/transforms.may` | Agent 1 | Body/world transforms and finite motion guards |
| `src/physics/material.may` | Agent 1 | Material density |
| `src/physics/rigid.may` | Agent 1 | Broad phase, rigid integration, impulses and convex character contacts |
| `src/game/cutter.may` | Agent 1 | Fragment construction, ownership, velocity, budgets and cable release |
| `src/game/timing.may` | Agent 1 | Fixed-step accumulator with bounded catch-up |
| `src/render/` | Agent 1 | Camera projection, 60 Hz render deadlines and native UI draw commands |
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

Native rendering has its own 60 Hz deadline. Event polling waits at most 17 ms
and can wake early for input, while early polls skip full-scene reconstruction.
Slight lateness preserves cadence; a long stall discards render backlog instead
of drawing stale catch-up frames. Backward/non-finite clock samples reset the
pacer. Supported absolute render times are bounded to ±1e12 seconds to keep the
1/60-second increment representable. A tick-limited run forces its final draw.
The cap limits submissions; it is not a promise of 60 presented frames per second.

The original free-flight demonstration remains semi-implicit Euler. The workshop
uses four 1/240-second substeps per fixed tick. Rigid bodies integrate their
centre of mass, then resolve convex contacts through six positional/impulse
passes with angular lever arms, low restitution and Coulomb friction. Cached
world outlines and AABBs provide the broad phase. The upright 0.6-by-1.3
kinematic character resolves against actual convex outlines in three passes;
it receives surface velocity but does not push bodies back. Speed limits are
20 m/s per linear component and 30 rad/s angular. This is a discrete prototype
solver, with one representative contact point and no continuous collision
detection, sleeping or full contact manifold. Thin/fast fragments and stacks
remain limitations. Agent 2 is implementing an additive two-point manifold.

Cuts transform the finite world blade into body-local coordinates and use
Agent 2's splitting, mass and recentering modules. Density scales area and
centroidal inertia. Each fresh fragment inherits the parent angle and spin,
and its COM velocity includes the parent's angular velocity crossed with the
COM offset. Fragment IDs are unique; failed sliver/budget checks retain the
whole parent. The minimum piece area is 0.025 m² and body budget is 24. Only
dynamic pieces outside x ±40 m or below y -12 m are retired. No polygon
integral is duplicated in gameplay or physics.

Rendering transforms local polygon vertices by angle and position, then fits the
room into a clipped camera. Convex fill is high-level Maylang scan conversion;
the thin typed FFI calls only the existing native UI drawing primitives. No
pixel-pointer buffer or C gameplay implementation is involved. The renderer can
draw convex pieces independently of the controller's current contact limits.

`Body.dynamic` controls integration. `Body.cuttable` is independent: static
terrain can be cut, while some dynamic objects may be protected by design.
Materials are strings: steel density 7.8, wood 0.7 and default 2.4 in consistent
prototype units. Cables identify a supported body and use world-space anchors.
A suspended body stays static until its last cable is severed. Cutting the
body detaches its cables and creates dynamic pieces. No rope swing or joint
solver is claimed.

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
