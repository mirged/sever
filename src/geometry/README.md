# Geometry work area — Agent 2

`slice.may` implements geometry API v1 from
[the architecture](../../docs/ARCHITECTURE.md):

```may
pub struct SliceResult { status: Str, pieces: List<Polygon> }
pub fun split_convex(shape: Polygon, start: Vec2, end: Vec2, epsilon: Float) -> SliceResult
```

It is pure, typed Maylang: no mutation of inputs, I/O, randomness, physics or
native calls. Tests are in [`tests/geometry/`](../../tests/geometry/README.md).

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
