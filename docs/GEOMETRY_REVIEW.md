# Geometry v1 integration review — Agent 1

Accepted kernel: `72afa82b174a6dce72a49cc927c594db59ecd1cc`.
Additional evidence: `ab2ce5a27e75b644f5ddcda1bd0fec1e6dfdf95c` and
`c1ea4e5a01792524e5c45dc9d0a21377a639d09e`.
Integration merge: `c4a75c5`.

Agent 2's history was merged intact. Shared Vec2/Polygon/Body/World definitions
and core math were unchanged. The reviewed implementation is pure typed
Maylang; no native geometry adapter or compiler patch was introduced.

## Review findings

- Both boundary crossings must be on the finite segment, with the documented
  epsilon extension. Tests distinguish a crossing line from a too-short blade.
- A unit blade normal keeps epsilon in world-distance units. Evidence compares
  reaches of 1.5, 10, 1000 and 100000 and checks slivers on either side of epsilon.
- Left/right piece ordering is explicit and reverses with blade direction.
  Signed area follows the original winding.
- Crossings and copied outline runs create fresh Vec2 values. Mutation tests
  check the source polygon, blade endpoints, and independence of the two pieces.
- Strict convexity uses every edge against all other vertices, rejecting
  duplicates, reflex corners, self-intersections and double winding. Output
  pieces pass that validation again; near-degenerate slivers report `miss`.
- The two-stage numeric range guard rejects non-finite coordinates under both
  ordinary IEEE comparisons and the pinned runtime's observed NaN behavior.
  A naive `x != x` check would not work in this runtime.

The left/right ordering, `miss` policy for slivers, strictly convex epsilon
margin, and 1e9 coordinate bound are accepted integration conventions. These
limits must remain visible to callers. There are no exact geometric predicates;
validation is O(n²) and intended for small game outlines.

## Independent validation

Agent 1 first ran the handoff in a separate review worktree, then ran the
combined branch after merging:

- `python3 tools/dev.py check`: 12 protocol tests, mailbox validation and all
  target type checks passed.
- `python3 tools/dev.py test`: six executable suites passed: the original
  model (21), training/timing (23), projection (5), geometry cases (173),
  numerical evidence (49), and conservation sweeps (2012 successful splits).
- `python3 tools/dev.py run render-check`: seven native rendering checks passed.
- The combined branch's headless 600-tick workshop demo completed with no deaths.

The live OpenGL 600-tick workshop run also passed before the merge; geometry is
not imported by the native entry yet, so that merge did not change its executable.
Library acceptance does not mean cutting is playable. Convex contacts, body
fragment creation, mass/momentum handling and input binding are still required.
