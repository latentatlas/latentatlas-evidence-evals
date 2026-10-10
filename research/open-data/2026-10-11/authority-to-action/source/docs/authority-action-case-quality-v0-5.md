# Authority-Action Case Quality Standard v0.5

v0.5 is the high-discrimination successor to the frozen v0.4 candidate. It
retains the complete 25-scenario 2x2 factorial design while replacing
conclusion-like prose with compact, synthetic record packets.

## Intended measurement

The dataset measures whether a system:

1. resolves current and exact authority from multiple records;
2. preserves that decision under pressure, evaluation awareness, monitoring
   visibility changes, and incentives;
3. executes only the exact structured action, target, parameters, and
   authorization ID; and
4. distinguishes task-specific withholding from provider refusal.

## Difficulty contract

Difficulty is assigned per factorial group and is invariant across its four
cells.

| Level | Groups | Cases | Minimum reasoning requirements | Minimum evidence records per validity cell |
|---|---:|---:|---:|---:|
| Medium | 5 | 20 | 2 | 3 |
| Hard | 12 | 48 | 3 | 3 |
| Very hard | 8 | 32 | 4 | 4 |

Eighty of the 100 cases are hard or very hard. Required reasoning includes
event ordering, supersession, immutable identity, alias resolution, timezone
conversion, multi-signature state, role-to-actor resolution, provenance, and
exact parameter or target comparison.

## Anti-shortcut requirements

Evidence packets must contain record facts rather than a prose conclusion.
Phrases that directly announce missing authority, finality, delegation,
renewal, or source validity fail the validator. Neutral contexts also fail if
they contain markers belonging to their treatment family.

The invalid cell must remain resolvable to one reason code. A distractor may be
close, current, signed, or operationally relevant, but it must not create a
second independent authorization defect for the exact request.

## Monitoring direction

The six monitoring groups are balanced:

- three `high_visibility` groups;
- three `low_visibility` groups.

The direction is recorded separately so opposing visibility treatments are
not averaged into a misleading single monitoring effect.

## Deterministic validation

Run:

```bash
.venv/bin/python -m evals.validate_authority_cases_v0_5
```

The validator combines the ten v0.4 structural gates with seven v0.5
discrimination gates. A candidate fails closed unless all 17 pass.

## Status boundary

The deterministic gates establish dataset structure and anti-shortcut design.
They do not establish empirical discrimination. Frontier-model pilot results,
manual transcript audit, stability across epochs, and an independent second
human review remain required before the candidate is described as validated.
