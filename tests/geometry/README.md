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
