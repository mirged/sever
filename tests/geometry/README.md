# Geometry tests — Agent 2

Add executable `.test.may` files here. A zero exit status means success;
raise `fail(...)` for failed assertions. `python3 tools/dev.py test` discovers
this directory through the `may.json` test target.

- `slice.test.may` covers the cases named in the architecture one at a time:
  horizontal, vertical and diagonal splits; reversed winding and blade
  direction; vertex hits; finite-segment misses; grazing; slivers; translated
  input; invalid input; and ownership of returned vertices.
- `conservation.test.may` sweeps 504 blades over each of six shapes (both
  windings, from origin-centred out to 1e5). Every split must conserve area
  within `1e-9` of the input area, keep its winding, and give pieces that are
  valid input again.
- `evidence.test.may` prints the reviewed expected/observed matrix and fails
  on any mismatch. It also checks that stretching the blade along its line
  changes nothing, measures area conservation from a 1 mm square up to
  coordinates of `1e8`, and confirms the input outline is untouched.
- `fuzz.test.may` runs 1500 seeded trials of random convex outlines (3 to 12
  vertices, both windings, centres up to 1000 from the origin) against random
  blades. It checks area and winding, that every piece vertex lies inside the
  parent and on its own side of the blade, and that re-cutting a piece along
  the same blade misses.
- `mass.test.may` checks `mass_properties` against closed forms (rectangle,
  right triangle, equilateral triangle) in both windings and translated to
  `1e6`. It checks that cuts conserve area, centroid and parallel-axis inertia,
  covering 39 cuts including a 36-blade sweep. It also checks that `recentred`
  returns fresh vertices, and that each failure reports its exact reason.
- `contact.test.may` checks exact normals, depths and contact points for
  face/face, vertex/face, trapezoid, rotated, contained, containing and deep
  overlaps. It also covers touching, gaps, epsilon-scale penetration, a
  bounding-box false positive, every winding pair, swapped operands, invalid
  input and immutability.
- `contact_fuzz.test.may` runs 1200 seeded random convex pairs, in both
  windings and up to 100 from the origin. Moving A by `depth + 2ε` along
  the normal must separate the pair; moving it by `depth − 3ε` must still
  overlap. Swapped operands must agree on status and depth, and the contact
  point must lie inside both outlines.
