# Native spell integration — review candidate

The five-spell library remains owned by Agent 2. Agent 1 has connected it through
`src/game/magic.may`, keeping spellbook state outside Training to avoid the
library's existing Player/Training import dependency becoming a cycle. Ordinary
cuts and spells share the cutter's fragment ID allocator and result counters.

**Review status:** native integration works, but approval for main is pending the
empty-world clearance guard requested in `agent1-0017` and reproduced again in
`agent1-0019`. Library snapshot `a8e0f3c` corrects invalid contact results and
invalid caster origins; its public `clear_at` still accepts invalid centres in
an empty world. The candidate is not a promotion approval.

## Controls and behavior

Mouse aims, J uses the ordinary blade, 1–5 selects arc/lance/shatter/blink/rift,
and F casts the selected spell. Mana, per-spell cooldowns in seconds, selection,
cast status and resonance are visible. Trails show every fired blade; blink and
rift show their actual landing displacement. R reconstructs the world and
spellbook. Pausing/focus loss prevents casting and freezes simulation-clock
regeneration, cooldowns and trails. Finished runs reject new casts.

`--spell-demo` casts blink, then a resonating lance, then shatters the overhead
slab while traversing the room. `--demo` and `--cut-demo` remain available.
Reports include spell casts, last spell, mana and cast status.

## Executed evidence

- `python3 tools/dev.py check`: valid mailboxes, 15 protocol checks, all targets
  type-check in the integration review checkout.
- `python3 tools/dev.py test`: 16 executable Maylang suites pass, including 20
  native adapter assertions and the library's 168 assertions at `a8e0f3c`.
- `python3 tools/dev.py run render-check`: ten software-render assertions pass,
  including mana, selection and a cast trail.
- Headless `workshop -- --spell-demo --ticks 600`: three casts, five cuts,
  one respawn, exit reached at approximately (10.8456877, 4.25).
- Native OpenGL `workshop -- --spell-demo --ticks 600`: exactly 600 ticks and
  `tick_limit`; the cast count, cuts, deaths, exit, mana and final coordinates
  match headless. The native valid-input run used the original library snapshot;
  the later guard fix was independently checked and tested separately.

The native report records 548 rendered frames, 1236 event polls, about 11.68
application seconds and 1.61 discarded catch-up seconds. Desktop timing remains
variable. Opening and completion reference snapshots were visually inspected;
these are software reference images, not GPU readbacks. Manual keyboard/mouse
play and external input automation were not performed. Autoplay calls the same
casting adapter used by the native F binding.

The adapter tests cover selection bounds, owned aim coordinates, shared cable
counters, cooldown refusals, regeneration, actual blink trails, resonance,
completion gating, fragment IDs, reset, effect expiry and full-room traversal.

The single-point rigid solver and convex-only cutting limits remain. A spell
cast can consume mana without hitting a body. Blink checks destination clearance
and can cross intervening obstacles; rift additionally cuts its path. No enemy,
spell damage, audio or continuous collision detection is claimed.
