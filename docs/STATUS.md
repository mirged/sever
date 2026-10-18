# Scaffold validation — 2026-10-18

This records the original scaffold. See
[the movement lab validation](WORKSHOP_VALIDATION.md) for the subsequent native
window, player controller and rendering milestone.
The cutting kernel's subsequent acceptance is recorded in
[Agent 1's geometry review](GEOMETRY_REVIEW.md).

Maylang was built from the sibling source checkout at
`beb593cdcffb2ff4c30db060686c3eb312807d62`. The resulting compiler reports
`mayc 0.13.102`. The inherited installed compiler was not used.

| Command | Observed result |
| --- | --- |
| `python3 tools/dev.py bootstrap` | Rust → C → native compiler and May runner built successfully |
| `python3 tools/dev.py check` | Both mailboxes valid; 12 protocol tests passed; all Maylang targets type-checked |
| `python3 tools/dev.py test` | 1 Maylang test executable passed, with 21 model assertions |
| `python3 tools/dev.py run` | 60 ticks; debris position approximately `(-1, -1.98675)` |

Markdown relative links and repository JSON syntax were also checked locally.
Generated build outputs and workspace-local GitHub configuration are ignored.
Maylang source was not modified; its generated compiler/target artifacts remain
in ignored paths inside the workspace.

No window or interactive gameplay was tested: neither is implemented yet.
There are no geometry tests until Agent 2 implements the cutting kernel.
The model currently simulates free flight only; the cable and static slab are
seed data, not functioning constraints. CI uses the same source pin and commands;
its hosted result must be checked separately after publication.

The initial GitHub repository was created through the human's terminal because
shell networking is blocked in this agent session. Subsequent publication uses
the connected GitHub Git Data API: upload the staged tree, create a commit and
advance the branch with an expected-head check. Local commit objects are
reconstructed and hash-verified to match those remote commits exactly. No
published history is rewritten.
