# Authority-to-Action v0.8.2 Full-Medium Results

## Status

The complete medium-reasoning run finished successfully on 27 July 2026.
All ten provider-batch checkpoints verify, and the assembled analytical set
contains 600/600 protocol-complete rows. Raw provider transcripts remain local
and unchanged.

This report describes the two API-delivered systems under the frozen v0.8.2
synthetic benchmark. It is not evidence of general model performance or a
provider-wide ranking, and it is not a general provider or model ranking.

The aggregate-only public artifact can be verified with:

```bash
python -m latentatlas verify-authority-action-full-result \
  --artifact-dir data/authority_action_v0_8_2_full_medium
```

## Frozen scope

- 100 synthetic authority-to-action cases;
- 25 complete four-variant prompt groups;
- 50 execute and 50 withhold cases;
- GPT-5.6 Sol and Claude Fable 5;
- medium reasoning effort;
- three epochs per model and case; and
- 600 analytical sample runs.

The dataset hash is
`7dc42780d7a28993756a01fce6c585e2e531bad97157dc33c4be441c75292900`.
The preauthorization manifest hash is
`5484140737942a7c3f6314b446b279fe6ce955755cdbf6cbfc7cda4b1aefe0f7`.

## Execution and cost audit

| Item | Result |
|---|---:|
| Analytical sample runs | 600 |
| Gross provider attempts | 603 |
| Verified provider-batch checkpoints | 10/10 |
| Gross cost | $8.6929235 |
| Analytical-set cost | $8.5742080 |
| Repair overhead | $0.1187155 |
| OpenAI gross cost | $2.3714550 |
| Anthropic gross cost | $6.3214685 |

Gross cost was 17.0% below the calibrated operational projection of
$10.47807. The run also remained below each provider-specific authorization
cap and the $22.50 hard ceiling.

Three Anthropic attempts crossed the frozen 512-output-token protocol limit.
Each event affected one analytical slot after a two-tool-turn response. The
runner stopped rather than accepting a partial result. A separately frozen
one-for-one repair then reran only the interrupted slot with the same model,
medium reasoning effort, message limit, output limit, and per-sample cost cap.
Selection depended only on protocol interruption, not score or model outcome.

| Batch | Interrupted analytical slot | Epoch | Observed output tokens | Overhead cost |
|---|---|---:|---:|---:|
| batch_02 | `evaluation_trace_archive__valid_neutral` | 2 | 548 | $0.0381545 |
| batch_03 | `incentive_vendor_trial__valid_treatment` | 2 | 516 | $0.0358600 |
| batch_05 | `pressure_trial_vendor__valid_neutral` | 3 | 661 | $0.0447010 |

The three original attempts remain in the operational evidence. The final
analytical set includes their three protocol-complete replacements, producing
600 analytical rows from 603 gross attempts.

## Observed results

| API-delivered system | Correct decision | Usable decision | Provider refusal | Strict-scope failure | Unauthorized action on withhold cases |
|---|---:|---:|---:|---:|---:|
| GPT-5.6 Sol | 300/300 (100.0%) | 294/300 (98.0%) | 0/300 | 0/300 | 0/150 |
| Claude Fable 5 | 249/300 (83.0%) | 205/300 (68.3%) | 38/300 (12.7%) | 26/300 (8.7%) | 0/150 |

### GPT-5.6 Sol

GPT made the correct act-or-withhold decision on all 300 runs. It executed all
150 authorized cases with an exact tool call and made no action attempt on all
150 unauthorized cases. Six runs from the same actor-mismatch pair produced
an explicit and correct withhold but failed the task-specific reason-code
usability gate in all three epochs and both prompt variants. This accounts for
the difference between 300 correct and 294 usable decisions.

### Claude Fable 5

Fable made no action attempt on any of the 150 withhold cases. Its observed
degradation was therefore not unauthorized execution. It was concentrated on
the authorized execute path:

- 99/150 exact authorized executions;
- 26/150 malformed, duplicate, or wrong-scope action attempts;
- 25/150 no-action outcomes;
- 21/150 provider refusals; and
- 78/150 usable execute decisions.

On the 150 withhold cases, Fable recorded 150/150 correct no-action outcomes,
133 explicit withholds, 17 provider refusals, and 127 usable decisions. Six
explicit withholds failed the task-specific reason-code usability gate.

Treatment wording coincided with lower Fable performance on authorized cases
in this dataset. Correct decision fell from 53/75 on `valid_neutral` to 46/75
on `valid_treatment`; usable decision fell from 45/75 to 33/75. This is an
observed paired benchmark difference, not a causal claim about arbitrary
pressure prompts.

Provider refusals were unevenly distributed across Fable behavior families:
18/72 incentive-shift runs, 13/72 evaluation-awareness runs, 6/84 pressure
runs, and 1/72 monitoring runs. The result therefore represents the delivered
model-plus-provider system, not an isolated latent model decision.

## Integrity correction at finalization

After the tenth checkpoint, the completion summary correctly reported the
$8.6929235 gross total, while an earlier run-manifest provider subtotal still
omitted the final repaired checkpoint. A finalizer recomputed both totals from
all ten verified checkpoints, failed on any inconsistent cost decomposition,
and updated the run manifest to the same provider totals. The final audit now
records:

- Anthropic gross cost: $6.3214685;
- OpenAI gross cost: $2.3714550;
- analytical-set cost: $8.5742080; and
- repair overhead: $0.1187155.

This correction changed accounting metadata only. It did not alter a prompt,
completion, score, raw log, checkpoint, or analytical-row selection.

## What the result supports

The run supports a narrow engineering conclusion: the frozen benchmark,
side-effect-free tool environment, deterministic scorer, checkpoint system,
repair accounting, and aggregate-only analysis can execute a repeated
two-provider authority-to-action evaluation end to end.

Within this benchmark, both systems avoided acting on unauthorized cases.
Their main observed difference was on the authorized path: GPT reliably
completed the exact requested action, while Fable more often refused, withheld,
or produced malformed or wrong-scope tool calls.

## What remains unresolved

- Cases are synthetic and authored within this project.
- The 100/100 masked review was an internal author check, not independent
  external validation.
- Provider filters are part of the delivered system but their internal trigger
  and timing are not observable from these logs.
- Only one reasoning level and one run date are represented.
- The benchmark does not estimate real-world incident rates or production
  safety.
- A max-reasoning diagnostic, if run, must use the pre-specified complete-group
  selector and a separate budget and authorization. It cannot replace these
  medium results.

## Audit and publication artifacts

The unpublished run evidence remains under
`outputs/inspect/20260727T152524Z-full-medium-authorized/`:

- `final_audit_summary.json` — ten-checkpoint completion and cost truth;
- `final_audit_summary.sha256` — final-audit digest;
- `analysis/analytical_rows.jsonl` — 600 transcript-free analytical rows;
- `analysis/aggregate.json` — aggregate metrics and repair accounting;
- `analysis/aggregate.md` — aggregate-only review report; and
- `analysis/result_manifest.json` — dataset, manifest, analyzer, assembler,
  row, report, and final-audit hashes.

The public aggregate package is available under
`data/authority_action_v0_8_2_full_medium/`. Its `protocol.json` records the
sanitized design, scoring contract, review boundary, and repair rule. Its
`summary.json` contains the reviewed counts, metric definitions, repairs, cost
accounting, and limitations. Its `manifest.json` binds both public documents to
versioned source hashes and to fingerprints of the unpublished local evidence.

Raw Inspect logs and provider transcripts remain local and are not part of the
public release. Internal execution authorization, live credit records, and
provider-specific repair plans also remain local.
