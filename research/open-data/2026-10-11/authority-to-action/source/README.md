# LatentAtlas Evidence Evals

A deterministic Python research package for evaluating evidence quality and
action-time authority in LLM and agentic workflows.

[![Tests](https://github.com/latentatlas/latentatlas-evidence-evals/actions/workflows/tests.yml/badge.svg)](https://github.com/latentatlas/latentatlas-evidence-evals/actions/workflows/tests.yml)

The repository demonstrates a complete local pipeline: source indexing,
candidate retrieval, schema validation, evidence qualification, decision
verification, authority-lease revalidation, audit hashing, and pass/fail
manifests. Synthetic packets and negative controls make every decision path
reproducible.

## Start here

- See the latest verified result below: 600 protocol-complete analytical rows,
  zero unauthorized actions across 300 withhold runs, and a public row ledger
  whose aggregates can be recomputed locally.
- Read the
  [public case study](docs/authority-action-v0-8-2-full-medium-case-study.md)
  for the research question, development stages, corrections, results, and
  lessons learned.
- Read the
  [full technical results](docs/authority-action-v0-8-2-full-medium-results.md)
  for the complete metric definitions and condition-level findings.
- Read the
  [v0.8.3 public analysis](docs/authority-action-v0-8-3-public-analysis.md)
  for row-level recomputation, 25-group statistics, epoch stability, and the
  strict-scope error taxonomy.

## Latest verified result

| API-delivered system | Correct | Usable | Exact authorized execution | Unauthorized action in withhold runs |
|---|---:|---:|---:|---:|
| GPT-5.6 Sol | 300/300 | 294/300 | 150/150 | 0/150 |
| Claude Fable 5 | 249/300 | 205/300 | 99/150 | 0/150 |

The result comes from 100 synthetic cases, two systems, and three epochs. All
600 analytical rows are public without prompts, completions, tool arguments,
provider payloads, credentials, UUIDs, or raw transcripts. The public verifier
recomputes the complete summary from those rows and checks their file and
source hashes.

```bash
python -m latentatlas verify-authority-action-full-result \
  --artifact-dir data/authority_action_v0_8_2_full_medium
python -m latentatlas verify-authority-action-public-analysis \
  --artifact-dir data/authority_action_v0_8_3_analysis
```

## Technical highlights

- Standard-library Python, deterministic verdicts, stable hashes, unit tests,
  and GitHub Actions.
- A side-effect-free Inspect evaluation with exact action scope, explicit
  reason codes, provider-refusal separation, and protocol-limit auditing.
- A complete 100-case factorial benchmark with 24 dataset-quality gates,
  internal masked author review, three epochs, and checkpointed repair
  accounting.
- A transcript-free 600-row public ledger, deterministic aggregate
  recomputation, 25-group cluster analysis, epoch-stability analysis, and an
  exclusive strict-scope error taxonomy, backed by an
  [executable verifier](latentatlas/authority_action_public_analysis.py).
- Versioned result verifiers remain available for the
  [v0.7 pilot](latentatlas/authority_action_pilot.py),
  [v0.8 review](latentatlas/authority_action_review.py), and
  [v0.8.2 full run](latentatlas/authority_action_full_result.py).
- Separate modules for evidence qualification, action-time revalidation,
  frozen review, and a six-kernel CategoryVantage application architecture.

## What is included

- `EvidenceGuard`: qualifies candidate evidence separately from semantic
  similarity.
- `EvidenceIndex`: creates a local, audit-friendly candidate index while
  preserving source identity and governance metadata.
- `EvidenceVectorLayer`: runs index build, retrieval, schema validation,
  qualification, verification, and manifest generation as one pipeline.
- `ActionTimeRevalidation`: checks an authority lease immediately before a
  planned action and routes the case to dry-run execution, revalidation,
  blocking, or manual review.
- A [LatentAtlas technical architecture](docs/latentatlas-evidence-and-action-architecture.md)
  that connects evidence qualification, action-time authority, and masked
  review to the runnable modules.
- A [CategoryVantage governed-kernel case study](docs/categoryvantage-governed-kernel-architecture.md)
  showing how the same control discipline can separate identity, evidence,
  truth, publication, action, and learning in a commercial system.
- A [frozen masked-review artifact](docs/frozen-masked-review.md) containing
  aggregate counts, a source-snapshot digest, a public manifest, and an
  executable verifier.
- Synthetic examples, negative controls, and unit tests.
- An [Inspect authority-to-action behavioral evaluation](docs/inspect-authority-action-eval.md)
  with 24 frozen baseline cases, a paired neutral diagnostic case, a
  side-effect-free action tool, transcript scoring, and mock-model integration
  tests.
- The [v0.4 case-quality standard](docs/authority-action-case-quality-v0-4.md),
  which defines structural, counterfactual, diversity, safety, human-review,
  and empirical-validation gates for the 100-case candidate set.
- The [v0.4 two-model pilot report](docs/authority-action-v0-4-pilot-results.md),
  with aggregate decision paths, run integrity, a retroactive sample-limit
  audit, and calculated cost for 64 scored runs.
- The [v0.5 quality standard](docs/authority-action-case-quality-v0-5.md),
  [preliminary human review](docs/authority-action-case-review-v0-5.md), and
  [pilot diagnostic](docs/authority-action-v0-5-pilot-diagnostic.md).
- The [v0.6 proof-contract quality standard](docs/authority-action-case-quality-v0-6.md),
  [internal case review](docs/authority-action-case-review-v0-6.md),
  [paid-pilot diagnostic](docs/authority-action-v0-6-pilot-diagnostic.md),
  [provider-specific limit diagnostic](docs/authority-action-v0-6-1-pilot-diagnostic.md),
  [v0.7 usable pilot results](docs/authority-action-v0-7-usable-pilot-results.md),
  [aggregate-only v0.7 summary](data/authority_action_v0_7_pilot/summary.json),
  [integrity manifest](data/authority_action_v0_7_pilot/manifest.json),
  [v0.8 internal blind-review record](docs/authority-action-internal-blind-review-v0-8.md),
  [aggregate-only v0.8 review summary](data/authority_action_v0_8_internal_review/summary.json),
  [v0.8 review integrity manifest](data/authority_action_v0_8_internal_review/manifest.json),
  [v0.8.2 full-medium results](docs/authority-action-v0-8-2-full-medium-results.md),
  [v0.8.2 public case study](docs/authority-action-v0-8-2-full-medium-case-study.md),
  [v0.8.3 public analysis](docs/authority-action-v0-8-3-public-analysis.md),
  [public v0.8.2 protocol](data/authority_action_v0_8_2_full_medium/protocol.json),
  [aggregate-only v0.8.2 summary](data/authority_action_v0_8_2_full_medium/summary.json),
  [v0.8.2 result integrity manifest](data/authority_action_v0_8_2_full_medium/manifest.json),
  [v0.8.3 transcript-free row ledger](data/authority_action_v0_8_3_analysis/rows.jsonl),
  [recomputed v0.8.3 summary](data/authority_action_v0_8_3_analysis/summary.json),
  [v0.8.3 analysis protocol](data/authority_action_v0_8_3_analysis/protocol.json),
  [v0.8.3 integrity manifest](data/authority_action_v0_8_3_analysis/manifest.json),
  and
  [complete experiment-development record](docs/authority-action-evaluation-development-case-study.md).

## System flow

```text
source excerpts
    -> local evidence index
    -> candidate packets
    -> schema validation
    -> evidence qualification
    -> decision verification
    -> pass/fail manifest

prior decision + authority lease + current state
    -> action-time revalidation
    -> execute dry run | request revalidation | block | manual review
```

Each stage returns inspectable data structures, reason codes, hashes, and
summary metrics that can be tested independently or composed as one pipeline.

## Architecture notes

- [LatentAtlas Evidence and Action Architecture](docs/latentatlas-evidence-and-action-architecture.md)
  connects the evidence pipeline, action-time authority leases, and masked
  review workflow to the runnable Python modules.
- [CategoryVantage Governed-Kernel Architecture](docs/categoryvantage-governed-kernel-architecture.md)
  applies the same engineering discipline to a six-kernel commercial system
  design with explicit state ownership, event contracts, and replayable audit
  state.

## Quick start

Python 3.11 or newer is required. The package has no runtime dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

Run the complete local evidence pipeline:

```bash
python -m latentatlas run-vector-layer \
  --sources examples/evidence_sources.jsonl \
  --queries examples/evidence_queries.jsonl \
  --out-dir outputs/vector-layer
```

Qualify a prepared set of evidence packets:

```bash
python -m latentatlas qualify \
  --input examples/sample_decisions.jsonl \
  --output outputs/decisions.jsonl \
  --summary outputs/decision-verification.json
```

Revalidate current authority immediately before an action:

```bash
python -m latentatlas revalidate-actions \
  --input examples/action_packets.jsonl \
  --output outputs/action-decisions.jsonl \
  --summary outputs/action-summary.json
```

Verify the frozen masked-review artifact:

```bash
python -m latentatlas verify-frozen-review \
  --artifact-dir data/frozen_masked_review_v1
```

Verify the aggregate-only Authority-to-Action v0.7 pilot artifact and its
versioned source hashes:

```bash
python -m latentatlas verify-authority-action-pilot \
  --artifact-dir data/authority_action_v0_7_pilot
```

Verify the aggregate-only Authority-to-Action v0.8 internal review artifact:

```bash
python -m latentatlas verify-authority-action-review \
  --artifact-dir data/authority_action_v0_8_internal_review
```

Verify the aggregate-only Authority-to-Action v0.8.2 full-medium result and its
versioned source hashes:

```bash
python -m latentatlas verify-authority-action-full-result \
  --artifact-dir data/authority_action_v0_8_2_full_medium
```

Recompute the Authority-to-Action v0.8.3 public analysis from all 600
transcript-free rows and verify its integrity chain:

```bash
python -m latentatlas verify-authority-action-public-analysis \
  --artifact-dir data/authority_action_v0_8_3_analysis
```

Install and test the optional Inspect behavioral evaluation:

```bash
python -m pip install -e '.[eval]'
python -m unittest discover -s tests_inspect -v
inspect eval evals/authority_action_eval_v0_3.py \
  --model anthropic/claude-fable-5 \
  -T case_type=all \
  --epochs 1 \
  --sample-id allow_current_release_dataset,withhold_similarity_pressure,withhold_similarity_neutral \
  --max-tokens 256 \
  --cost-limit 0.05 \
  --model-cost-config evals/model_costs_20260725.json \
  --log-format json \
  --log-dir outputs/inspect/claude-fable-5
python -m evals.analyze_authority_results \
  outputs/inspect/claude-fable-5 \
  --format markdown
```

The default frozen pilot repeats a domain-matched positive control plus pressure
and neutral variants of the same authorization case. Preview its verified
commands without making API calls:

```bash
.venv/bin/python scripts/run_authority_action_experiment.py --stage pilot
```

Validate the v0.4 100-case candidate and preview its 16-case balanced pilot
without making provider calls:

```bash
.venv/bin/python -m evals.validate_authority_cases_v0_4
.venv/bin/python scripts/run_authority_action_experiment.py \
  --stage pilot \
  --manifest evals/experiment_manifest_v0_4.json
```

The v0.4 task keeps `action`, `target`, structured `parameters`, and
`authorization_id` in separate tool fields. This prevents an otherwise valid
parameter value from being embedded in the action name and lets the scorer
separate unauthorized action, wrong scope, schema conformance, reason-code
accuracy, provider refusal, and exact execution.

Build and validate the v0.5 high-discrimination successor without changing the
frozen v0.4 artifacts:

```bash
.venv/bin/python scripts/build_authority_cases_v0_5.py
.venv/bin/python -m evals.validate_authority_cases_v0_5
.venv/bin/python scripts/run_authority_action_experiment.py \
  --stage pilot \
  --manifest evals/experiment_manifest_v0_5.json
```

The v0.5 pilot exposed a positive-control contract defect: execution required
a verified, final grant, but the packets did not always establish those facts.
Build, validate, and preview the corrected v0.6 successor without provider
calls:

```bash
.venv/bin/python scripts/build_authority_cases_v0_6.py
.venv/bin/python -m evals.validate_authority_cases_v0_6
.venv/bin/python scripts/run_authority_action_experiment.py \
  --stage pilot \
  --manifest evals/experiment_manifest_v0_6.json
```

The 80-run paid pilot stayed below its aggregate ceiling, but transcript audit
found that the $0.015 per-sample cap interrupted 21 Fable runs and one GPT run.
The [pilot diagnostic](docs/authority-action-v0-6-pilot-diagnostic.md) therefore
keeps harness limits, provider refusals, and model decisions separate; it does
not report a model ranking.

The provider-specific v0.6.1 successor reduced protocol interruptions from 22
to one. GPT completed 40/40 selected runs; Fable completed 39/40 and produced
nine separately reported provider `content_filter` outcomes. The runner
returned `needs_review`, the full stage stayed disabled, and transcript audit
also corrected a response-format rule that had rejected 14 exact Fable
executions solely because they added explanation after `EXECUTED`. See the
[v0.6.1 diagnostic](docs/authority-action-v0-6-1-pilot-diagnostic.md).

The v0.7 successor moved the response-format repair into a versioned scorer and
completed the same 80-run selected-case protocol with zero sample-limit
interruptions for $1.0922675. GPT produced 40/40 correct and usable decisions.
Fable produced 37/40 correct and 33/40 usable decisions; its seven provider
refusals were concentrated in evaluation-awareness cases, while no Fable
withhold case produced an unauthorized action attempt. The
[v0.7 report](docs/authority-action-v0-7-usable-pilot-results.md) records the
bounded result and integrity audit. The public
[`summary.json`](data/authority_action_v0_7_pilot/summary.json) and
[`manifest.json`](data/authority_action_v0_7_pilot/manifest.json) expose only
aggregate counts and evidence fingerprints; raw transcripts remain local.

The v0.8 successor then completed an author-side blind review of all 100 cases
before answer-key access. All 100 judgments agreed with the frozen key and all
100 packets were judged evidence-sufficient and single-decision clear. This is
an internal review, not independent validation. At that review gate the full
600-run stage remained disabled; it was later separately authorized and
completed under v0.8.2.

The v0.8.1 medium calibration produced 40/40 protocol-complete analytical rows
after one narrowly scoped Anthropic message-limit retry. Gross spend was
$0.698538 against the $1.50 ceiling. GPT produced 20/20 correct and usable
decisions; Fable produced 16/20 correct and 12/20 usable decisions, with five
provider refusals and no unauthorized action attempt. This remains a
one-epoch selected-case calibration, not the full benchmark.

The v0.8.2 successor freezes the complete 600-run medium design into five
resume-safe, complete-pair batches. It preserves the calibrated ten-message
limit, separates verified checkpoints from partial evidence, and refuses paid
execution until a separately frozen successor records fresh provider credit
and explicit approval.

The authorized v0.8.2 run then completed all 600 analytical slots across the
100-case, two-model, three-epoch design. Three Anthropic attempts crossed the
frozen output-token protocol limit; their original evidence was retained and
three one-for-one replacements were admitted under separately frozen,
protocol-only repair plans. The final audit records 603 gross attempts, 10/10
verified provider-batch checkpoints, $8.6929235 gross spend, and no action on
any withhold case from either delivered system. The
[v0.8.2 results report](docs/authority-action-v0-8-2-full-medium-results.md)
contains the bounded findings, accounting, and limitations; raw provider
transcripts remain local. The shorter
[public case study](docs/authority-action-v0-8-2-full-medium-case-study.md)
explains the research question, design corrections, final result, and
publication boundary. The public
[`protocol.json`](data/authority_action_v0_8_2_full_medium/protocol.json),
[`summary.json`](data/authority_action_v0_8_2_full_medium/summary.json), and
[`manifest.json`](data/authority_action_v0_8_2_full_medium/manifest.json)
contain the sanitized experiment contract, aggregate results, and integrity
fingerprints only. Internal execution authorization, provider payloads, and
live credit records are not published.

## Example decision surfaces

Evidence qualification returns fields such as:

- `semantic_similarity`
- `evidence_verdict`
- `identity_verdict`
- `recommended_action`
- `reason_codes`
- `audit.input_hash`
- selected and rejected evidence identifiers when applicable

Action-time revalidation returns:

- `execution_verdict`
- `recommended_action`
- `followup_lane`
- `action_impact`
- `risk_assessment`
- `risk_exposure`
- `reason_codes`
- an audit hash and the evidence identifiers bound to the lease

## Evaluation principles

- Evidence is qualified by authority, freshness, sufficiency, and identity.
- Action permission is revalidated against the current execution state.
- Stale, contradictory, malformed, and weakly sourced inputs receive explicit
  verdicts and reason codes.
- Missing information remains a measurable outcome.
- Retrieval, decision support, action routing, and learning use separate state
  transitions.
- Negative controls are first-class evaluation cases.

## Research context

This implementation accompanies three public research notes:

- [Relevance Is Not Authority](https://doi.org/10.5281/zenodo.20161629)
- [Evidence Authority After Retrieval](https://doi.org/10.5281/zenodo.21243387)
- [Authority Leases and Concurrent Evidence Failure in Safe Agentic Execution](https://doi.org/10.5281/zenodo.21432540)

The latest public findings and the frozen masked-review summary are available
at [latentatlas.ai/authority-leases](https://latentatlas.ai/authority-leases/).
The repository also includes the machine-readable
[`summary.json`](data/frozen_masked_review_v1/summary.json),
[`outcomes.csv`](data/frozen_masked_review_v1/outcomes.csv), and
[`manifest.json`](data/frozen_masked_review_v1/manifest.json).

## Citation

Software and research-note citation metadata is available in
[`CITATION.cff`](CITATION.cff). GitHub also exposes this metadata through its
**Cite this repository** control.

## Implementation profile

The package runs locally on Python 3.11+, uses deterministic evaluation rules,
and operates on the included synthetic examples. Risk scores provide
consistent prioritization across the evaluation set; verdicts remain
traceable to their evidence identifiers and reason codes.

## Author

Huseyin Buldurgan — [LatentAtlas](https://latentatlas.ai/) ·
[LinkedIn](https://www.linkedin.com/in/hbuldurgan)
