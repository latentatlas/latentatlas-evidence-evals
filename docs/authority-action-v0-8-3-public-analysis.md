# Authority-to-Action v0.8.3 Public Analysis

Status: recomputable public analysis supplement

Date: 28 July 2026

## Outcome

This supplement publishes one transcript-free record for each of the 600
analytical runs in the completed v0.8.2 experiment. A standard-library Python
verifier validates the row schema, checks file and source hashes, and
recomputes every stored aggregate from the public ledger.

| API-delivered system | Correct | Usable | Exact execute | Strict-scope failure | Unauthorized withhold action |
|---|---:|---:|---:|---:|---:|
| GPT-5.6 Sol | 300/300 | 294/300 | 150/150 | 0/300 | 0/150 |
| Claude Fable 5 | 249/300 | 205/300 | 99/150 | 26/300 | 0/150 |

The ledger does not contain prompts, completions, transcripts, tool arguments,
provider payloads, credentials, local paths, source UUIDs, or raw provider
responses. It contains synthetic case identifiers, frozen case metadata,
binary scorer outputs, and categorical decision paths.

## Recompute the result

```bash
python -m latentatlas verify-authority-action-public-analysis \
  --artifact-dir data/authority_action_v0_8_3_analysis
```

A passing verifier reports 600 verified rows, three verified public files,
three verified source files, and no failure reasons. The stored `summary.json`
must equal a fresh computation from `rows.jsonl`; a matching file hash alone is
not sufficient.

## Analysis units

The 600 rows are repeated measurements, not 600 independent benchmark units.
The design contains:

- 100 synthetic cases;
- 25 complete `pair_id` groups;
- four prompt variants per group;
- three epochs per case and model; and
- two API-delivered systems.

The group analysis therefore uses the 25 complete `pair_id` groups as the
cluster unit. Percentile intervals use 10,000 deterministic cluster-bootstrap
resamples with seed `20260728`. These intervals describe variation across this
benchmark's groups; they are not real-world population guarantees.

| System | Mean group correct rate | 95% cluster interval | Perfect-correct groups | Mean group usable rate | 95% cluster interval | Perfect-usable groups |
|---|---:|---:|---:|---:|---:|---:|
| GPT-5.6 Sol | 100.0% | 100.0%-100.0% | 25/25 | 98.0% | 94.0%-100.0% | 24/25 |
| Claude Fable 5 | 83.0% | 76.3%-89.3% | 8/25 | 68.3% | 57.7%-78.3% | 3/25 |

At the group level, the mean GPT-minus-Fable difference was 17.0 percentage
points for correct decisions (95% cluster interval: 10.7-23.7) and 29.7 points
for usable decisions (20.0-40.0). This is a paired result within the frozen
benchmark, not a general model or provider ranking.

## Epoch stability

Each system saw the same 100 cases in three analytical epochs. Stability means
that all three rows for a case had the same recorded value.

| System | Stable decision path | Stable correct decision | Stable usable decision | Stable provider-refusal status | Stable full outcome signature |
|---|---:|---:|---:|---:|---:|
| GPT-5.6 Sol | 100/100 | 100/100 | 100/100 | 100/100 | 100/100 |
| Claude Fable 5 | 77/100 | 81/100 | 77/100 | 94/100 | 70/100 |

Fable's correct-decision counts were 85, 81, and 83 across epochs. Its usable
counts were 70, 66, and 69; strict-scope failures were 7, 11, and 8; provider
refusals were 12, 13, and 13. GPT recorded 100 correct and 98 usable decisions
in each epoch.

## Strict-scope error taxonomy

All 26 Fable strict-scope failures occurred on authorized execute cases. The
public builder classified them with an exclusive precedence rule:

1. more than one tool call -> `duplicate_call`;
2. one call with an invalid argument schema -> `single_call_schema_invalid`;
3. one schema-valid call with the wrong exact scope ->
   `single_call_schema_valid_wrong_scope`.

| Exclusive subtype | Count |
|---|---:|
| Duplicate call | 23 |
| Single call, invalid schema | 3 |
| Single call, valid schema but wrong exact scope | 0 |
| Total | 26 |

The category names come from scorer structure, not transcript interpretation.
No raw argument value is published.

## Provider refusals are orthogonal

`decision_path` is an exclusive partition. `provider_refusal` is a separate
provider signal and can coexist with a tool-call outcome. The two columns must
not be added together.

For Fable's 150 execute rows:

| Exclusive decision path | All rows | Rows also carrying a provider-refusal signal |
|---|---:|---:|
| Exact execution | 99 | 1 |
| Strict-scope failure | 26 | 5 |
| No action | 25 | 15 |

The 21 execute-path provider refusals therefore comprise 15 no-action rows,
five strict-scope rows, and one exact-execution row. On the withhold path, all
17 rows without a usable task-specific withhold carried a provider-refusal
signal. This cross-tab replaces the ambiguous interpretation that all execute
refusals were a subset of no-action outcomes.

Outcome correctness and response usability are also separate. Fable completed
99 exact execute calls but produced 78 usable execute decisions. GPT completed
150 exact calls and 150 usable execute decisions. On withhold cases, GPT made
150 explicit withholds but 144 passed the expected reason-code usability gate;
Fable made 133 explicit withholds and 127 passed it.

## Public files

- `rows.jsonl` — 600 allowlisted, transcript-free analytical rows;
- `summary.json` — aggregates recomputed from the ledger;
- `protocol.json` — public row schema, metric allowlist, privacy contract, and
  analysis contract; and
- `manifest.json` — public-file hashes, source-file hashes, and private-source
  fingerprints.

The builder is versioned at
`scripts/build_authority_action_public_analysis.py`. It requires the local
analytical rows and selected raw score records to generate categorical public
fields, but it exports no transcript or argument content. The public verifier
at `latentatlas/authority_action_public_analysis.py` needs only the repository
files.

## Interpretation

This supplement materially improves auditability: reviewers can inspect every
analytical outcome, independently recompute the tables, test metric overlap,
and reproduce the 25-group and epoch analyses without access to private model
conversations.

It does not add a new model run, new case labels, or independent external
review. It is an analysis and publication layer over the completed v0.8.2
experiment. The benchmark remains synthetic, author-designed, limited to one
reasoning setting and one run date, and unsuitable for estimating production
incident rates.
