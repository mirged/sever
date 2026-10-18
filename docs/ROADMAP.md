# Roadmap

## 0 — Reproducible scaffold

- Typed model, fixed-step free-flight smoke demo, Maylang tests.
- Pinned sibling toolchain and workspace-local artifacts.
- Two-agent branches, JSON protocol, explicit ownership and executable checks.

## 1 — The first cut (Agent 2)

Split a convex polygon using a finite blade segment. Produce two valid convex
pieces only when the blade traverses the interior. Handle winding, tolerances,
vertex hits, grazing, parallel edges and invalid shapes. Preserve area and
prove it with deterministic tests. Keep geometry free of rendering and FFI.

## 2 — The workshop (Agent 1)

Native Maylang UI window, fixed-step accumulator, keyboard movement/jump,
blade aiming, player/world collision, camera and reset. Integrate the geometry
API, conserve mass and linear/angular momentum when making dynamic fragments,
then add convex collision detection and resting contacts. First playable room:
cut a suspended slab, form a bridge, cross a gap and reach an exit.

## 3 — Physical consequences

Severable cables and machine power, bounded debris lifetime/count, materials and
blade feedback, fragment impacts, enemies sharing the same body/cutting model.

## 4 — Dismantle the boss

Articulated, destructible machinery; detachable weapons and weak points; puzzle
rooms that teach mechanics; checkpoints, audio and performance budgets.

The first milestone deliberately uses convex geometry. Concave terrain needs
decomposition and connectivity reconstruction. “Cut anything” is the direction;
unsupported shapes must report a clear result, never silently corrupt the world.
