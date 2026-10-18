# Spells

`spells.may` gives the player five cutting-themed spells. It is pure, typed
Maylang, built on the existing cutter (`sever_world`, `sever_cables`), body
transforms and the geometry contact kernel. It edits no other module.

| Spell | Effect | Mana | Cooldown |
| --- | --- | --- | --- |
| `arc` | Three 3 m blades from the caster in a fan at −0.35, 0 and +0.35 rad | 20 | 30 ticks |
| `lance` | One 8 m blade toward the aim | 25 | 45 ticks |
| `shatter` | Three 2.4 m blades crossing at the target, 60° apart; target within 6 m | 40 | 75 ticks |
| `blink` | Teleport up to 4 m toward the aim, to the farthest spot where the player's box is clear | 30 | 60 ticks |
| `rift` | Blink that first severs everything along its path | 45 | 90 ticks |

- **Spellbook:** mana starts at 100, is capped at 100 and regenerates 0.25 per
  fixed tick. `tick_spellbook` also counts cooldowns down.
- **Resonance:** casting a different spell within 30 ticks of the previous
  cast refunds 25% of its cost. The full cost must still be available when
  casting. Repeating the same spell never resonates.
- **Blink clearance:** `clear_at` checks the player's 0.6 × 1.3 box against
  every body with `contact_convex`, and only a `separate` result counts as
  clear. An `invalid` contact (a malformed body or a non-finite box) is never
  treated as clear. Touching counts as separate, so landing on top of a floor
  works. Blink backs off in 0.25 m steps and reports `blocked`
  when nothing beyond 0.5 m is clear. It arrives at rest and airborne.
- **Cuts** go through `sever_world` with a 24-body budget, so they inherit its
  conservation rules: no piece under 0.025 m², fragments are dynamic, and each
  body is cut at most once per blade. Later blades in the same spell can cut
  fragments made by earlier ones. That is how `shatter` splinters a platform
  with 5 cuts.
- **Failure checks run in this order:** `unknown spell`, `invalid aim`
  (a non-finite aim or caster position, or one beyond 1000), `no aim`, `out of range`, `cooldown`,
  `no mana`, `blocked`. A failure changes only `book.status`; the world,
  player, mana and cooldowns are untouched.

## Not done yet

The spells are not bound to keys or drawn in the native workshop. Doing that
means editing `desktop.may` and `src/game/`, which belong to Agent 1. Tests are
in [`tests/spells/spells.test.may`](../../tests/spells/spells.test.may).
