# Roadmap

## 0 — Reproducible scaffold — complete

Typed Maylang model, pinned sibling compiler, workspace-local artifacts,
two-agent branches and commit/push JSON communication.

## 1 — Convex geometry — complete

Finite-segment splitting, shared validation, area/centroid/inertia and SAT
contacts. Agent 2 owns these kernels and their numerical tests. Agent 1 has
independently reproduced analytic cases and deterministic fuzz results.

## 2 — The workshop — playable prototype

Native rendering, movement, aiming and a finite blade; physical cut fragments;
convex character and rigid-body contacts; cable release, pause/reset/exit;
headless and native autoplay. Mass and linear/angular momentum are conserved
when creating fragments. Foundations are protected. The course permits cutting
but does not yet require constructing a bridge to solve it.

Next: review Agent 2's additive two-point manifold, improve stacking, then
build a room that requires a cut ramp or bridge. Discrete collisions and a
kinematic character remain prototype limits.

## 3 — Physical consequences

Swinging cable constraints, machine power, material toughness, impact damage,
enemies sharing the same body/cutting model, and debris used as weapons.

## 4 — Dismantle the boss

Articulated destructible machinery, detachable weapons and weak points,
checkpoints, audio, puzzle progression and performance budgets.

“Cut anything” is the direction. Current geometry is convex; concave terrain
needs decomposition and connectivity reconstruction. Unsupported shapes must
report a clear result rather than corrupt the world.
