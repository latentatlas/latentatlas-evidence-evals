# Authority-to-Action v0.8 Internal Blind Review

Status: 100/100 internal blind judgments complete; full provider run remains disabled

## Purpose

The v0.7 pilot established that the selected-case evaluation can run without
harness interruption. Before a 600-run full experiment, v0.8 adds a complete
internal blind review of the 100-case proof-contract dataset. The goal is to
identify ambiguous decisions, insufficient evidence, unrealistic packets, and
case-label disagreements before spending provider credits.

This is an internal author review, not an external or independent validation.
An external spot-check can be added later without blocking the internal review
or replacing its recorded status.

## Masking design

The builder creates three local working artifacts:

- `review_packet.jsonl`: opaque `IR-*` IDs and case prompts only;
- `review_responses.csv`: a blank structured response sheet; and
- `answer_key.jsonl`: source IDs and expected outcomes, stored separately from
  the packet used during review.

The packet removes source case IDs, metadata, expected actions, expected reason
codes, factorial-cell names, and difficulty labels. Its order is deterministic
but opaque. The prompt evidence remains intact because judging that evidence is
the purpose of the review.

## Review fields

Each case requires:

- `reviewed_action`: `execute`, `withhold`, or `unclear`;
- whether the written evidence is sufficient;
- whether exactly one decision is clear;
- realism and difficulty scores from 1 to 5;
- zero or more controlled issue codes; and
- a short rationale written before opening the answer key.

Allowed issue codes are `ambiguous_authority`, `evidence_conflict`,
`evidence_missing`, `label_leakage`, `multiple_decisions_plausible`,
`terminology_unclear`, `unrealistic_packet`, `other`, and `none`.

## Local workflow

No provider API call is made by either command.

```bash
.venv/bin/python scripts/run_authority_internal_review.py build

# Complete outputs/internal_review/authority_action_v0_8/review_responses.csv
# while consulting review_packet.jsonl but not answer_key.jsonl.

.venv/bin/python scripts/run_authority_internal_review.py analyze \
  --require-complete
```

The analyzer fails closed:

- blank rows keep the review `incomplete`;
- disagreements, unclear decisions, insufficient evidence, realism below 3,
  or issue codes create an adjudication queue; and
- only a complete review with no unresolved flags becomes
  `ready_to_freeze_successor`.

Even that status does not enable a provider run automatically. Dataset changes,
the new v0.8 hash, the full-run budget, and the execution manifest must be
reviewed and frozen separately.

## Completed review result

The author completed all 100 judgments from the opaque packet before opening
the answer key. The analyzer then reported:

- 100/100 reviewed cases;
- 100/100 action-label agreement;
- 100/100 packets judged evidence-sufficient;
- 100/100 packets judged to have one clear decision;
- zero issue codes and zero adjudication cases;
- mean realism score 4.0/5; and
- mean difficulty score 3.63/5 across 20 medium, 48 hard, and 32 very-hard
  cases.

The source dataset did not require a correction after review, so its SHA-256
remains
`7dc42780d7a28993756a01fce6c585e2e531bad97157dc33c4be441c75292900`.
Perfect agreement shows consistency between the masked author judgments and
the frozen answer key. It does not convert this review into independent
validation or prove real-world validity.

The aggregate-only public record is available as
[`summary.json`](../data/authority_action_v0_8_internal_review/summary.json)
and [`manifest.json`](../data/authority_action_v0_8_internal_review/manifest.json).
The local packet, answer key, response sheet, and rationales remain unpublished
under ignored `outputs/` paths. Verify the public artifact with:

```bash
python -m latentatlas verify-authority-action-review \
  --artifact-dir data/authority_action_v0_8_internal_review
```

## Full-run budget gate

The planned full protocol contains 600 sample runs: 100 cases, three epochs,
and two models. Extrapolating the v0.7 pilot averages gives a descriptive cost
projection of $8.19200625. The unchanged per-sample safety ceilings imply a
much higher $22.50 hard maximum.

The projection is not a spending guarantee. Live provider credit was not
rechecked while creating this artifact, so the v0.8 full stage remains
disabled. Enabling it requires a separate live-balance check and an explicit
manifest change; neither the review analyzer nor its verifier can make paid
provider calls.

## Data handling

The working review directory is under ignored `outputs/`. It contains only
synthetic cases and reviewer judgments; it contains no provider transcripts,
credentials, customer data, or personal data. The public artifact contains
aggregate review results and integrity fingerprints only; it does not copy the
local working directory.
