# Geometry work area — Agent 2

`slice.may` implements geometry API v1 from
[the architecture](../../docs/ARCHITECTURE.md):

```may
pub struct SliceResult { status: Str, pieces: List<Polygon> }
pub fun split_convex(shape: Polygon, start: Vec2, end: Vec2, epsilon: Float) -> SliceResult
```

It is pure, typed Maylang: no mutation of inputs, I/O, randomness, physics or
native calls. Tests are in [`tests/geometry/`](../../tests/geometry/README.md).
`numeric.may` holds the shared finite-coordinate guard (`MAX_COORDINATE`,
`finite_coordinate`, `finite_point`, `vector_length`) and the strict-convexity
rule `valid_convex(shape, epsilon)`. Every geometry module applies one range
and validation policy.

## Results

- `split`: two convex pieces with the input winding. `pieces[0]` lies left of
  the blade direction (`start` → `end`), `pieces[1]` right of it, so reversing
  the blade swaps them. Every vertex is a fresh `Vec2`. Each piece passes the
  same validation as the input, so it can be cut again.
- `miss`: the input is valid, but the blade does not cut through the interior.
  `pieces` is empty.
- `invalid`: the input or tolerance is rejected. `pieces` is empty.

## Tolerance policy

`epsilon` is a distance in world units. It does not scale with blade length.

- **Valid input** must be strictly convex with an epsilon margin. Every edge
  must be longer than `epsilon`, and every vertex not on an edge must lie more
  than `epsilon` inside that edge's line. This one rule rejects duplicate
  vertices, zero-length edges, collinear or near-collinear vertices, reflex
  corners, self-intersecting or doubly wound outlines, and shapes thinner than
  `epsilon`. Either winding is accepted.
- **Invalid** also covers: fewer than three vertices, a non-positive or
  non-finite `epsilon`, any coordinate that is NaN, infinite or larger than
  `1e9` in magnitude, and a blade no longer than `epsilon`.
- **Side of the blade line:** a vertex within `epsilon` of the line counts as
  on it. A cut needs vertices strictly on both sides. That means grazing a
  vertex, running along an edge, or passing within `epsilon` of the outline
  without crossing it is a `miss`.
- **Vertex hits:** when exactly one vertex lies on the line where the outline
  crosses it, that vertex becomes the crossing and no new vertex is made.
  Otherwise the crossing is interpolated on the edge, and is always more than
  `epsilon` from both of that edge's endpoints.
- **Finite blade:** both crossings must lie on the segment, extended by
  `epsilon` at each end. A blade that starts or ends inside the shape, or that
  stops short of it, is a `miss` even if its line would cut.
- **Slivers:** if either piece would fail input validation (for example, it
  would be thinner than `epsilon`), the result is a `miss` rather than a
  degenerate piece.

## Numeric limits

- Arithmetic is binary64 with no exact predicates. Classification error grows
  with coordinate magnitude, roughly `1e-16 × |coordinate|`. Choose `epsilon`
  well above that: at least about `1e-9` times the largest coordinate
  magnitude. Most tests use `epsilon = 1e-6` with coordinates up to `1e6`. The
  scale evidence also cuts a 1 mm square with `epsilon = 1e-9` and a 10 km
  square at `1e8` with `epsilon = 1e-3`.
- The coordinate limit of `1e9` keeps cross products far from overflow.
- Measured area conservation: `|area(left) + area(right) − area(input)|` stays
  below `1e-9 × area(input)` for every split in the tests. In the scale
  evidence, the observed relative error is at most about `2e-16`.
- Blade length does not change any decision. The same supporting line with
  reaches from `1.5` to `1e5` gives identical pieces, and the same
  `0.99e-6`/`1.01e-6` miss/split boundary. Very distant endpoints still cost
  precision, since the line's position is known only to about
  `1e-16 × |endpoint|`.
- Under the pinned runtime, NaN compares as true in every comparison. The
  finiteness check is written to reject NaN either way, but callers should not
  rely on NaN comparisons in other code. A minimal reproducer:

  ```may
  let huge: Float = 1.0e300;
  let infinity: Float = huge * huge;  // prints as 0e1
  let nan: Float = infinity - infinity;
  print(nan == nan, nan != nan, nan < 1.0, nan > 1.0);  // true false true true
  ```

  `x != x` therefore does not detect NaN here. The kernel rejects a coordinate
  when `x > 1e9 or x < -1e9`, and otherwise also requires
  `x <= 1e9 and x >= -1e9`. The first test catches NaN under this runtime and
  the second catches it under IEEE rules.
- Validation costs O(n²) in the vertex count. That is meant for small convex
  game outlines (tens of vertices), not large meshes.
- Concave input is rejected as `invalid`. It needs decomposition, which is a
  later milestone.

## Mass properties

`mass.may` implements geometry-mass-v1:

```may
pub struct MassProperties { area: Float, centroid: Vec2, inertia: Float }
pub fun mass_properties(shape: Polygon) -> MassProperties
pub fun recentred(shape: Polygon, origin: Vec2) -> Polygon
```

- `area` is unsigned, so either winding works. `centroid` is the area centroid
  in the input's space. `inertia` is the polar second moment of area about the
  centroid, per unit density. So `mass = density × area` and
  `I = density × inertia`.
- The sums run relative to the first vertex. Translating a shape to `1e6`
  changes nothing except the centroid.
- `mass_properties` calls `fail()`, never returns a zero sentinel, when:
  - there are fewer than three vertices;
  - any coordinate is non-finite or beyond `1e9`;
  - the area is not positive (collinear outlines, balanced bow ties);
  - the centroid or inertia comes out degenerate, for example a nearly
    cancelling self-intersecting outline.

  It does not check simplicity. Pass validated shapes or `split_convex`
  pieces.
- `recentred` returns fresh vertices translated by `-origin`, with the winding
  unchanged. Recentring on the centroid gives body-local vertices.
- Splits conserve area, the area-weighted centroid, and (by the parallel-axis
  theorem) inertia about the parent centroid. Tests require a relative error of
  `1e-9` or better; observed errors are about `1e-16` near the origin and about
  `7e-12` at `1e6`.

## Contacts

`contact.may` implements contacts-v1:

```may
pub struct ContactResult { status: Str, normal: Vec2, depth: Float, point: Vec2 }
pub fun contact_convex(a: Polygon, b: Polygon, epsilon: Float) -> ContactResult
```

- **Status** is `overlap`, `separate` or `invalid`. `separate` and `invalid`
  return a zero normal, depth and point.
- **Validation** is the same as `split_convex`: both outlines must pass
  `valid_convex` with the same `epsilon`, and the same finite-coordinate
  policy applies. Either winding works.
- **Separating axes:** the axes are the unit outward edge normals of both
  outlines. On each axis, A can escape along `+axis` by `max(B) − min(A)` or
  along `−axis` by `max(A) − min(B)`. The smaller distance is that axis's
  overlap, which stays correct under containment; the naive
  `min(max) − max(min)` interval would report the inner shape's width
  instead. `normal` is the escape direction for A, and `depth` is the
  smallest axis overlap. An overlap of `epsilon` or less on any axis
  (touching, or a gap) is `separate`.
- **Ties** keep the first minimal axis, A's edges before B's. Swapping
  operands therefore negates the normal exactly, except when two axes tie,
  for example a square centred inside a square.
- **Contact point:** the area centroid of A clipped by B's edge half-planes.
  It lies inside the overlap and is exact for the overlap region. For the
  first solver this is an approximation: it is one point, not a contact
  manifold. Resting stacks will want two clipped feature points later.
- **Cost** is O((n + m)²) with validation, and O((n + m)·m) for clipping. It is
  intended for small game outlines.
