# LatentAtlas Evidence Evals

A deterministic Python research package for evaluating evidence quality and
action-time authority in LLM and agentic workflows.

[![Tests](https://github.com/latentatlas/latentatlas-evidence-evals/actions/workflows/tests.yml/badge.svg)](https://github.com/latentatlas/latentatlas-evidence-evals/actions/workflows/tests.yml)

The repository demonstrates a complete local pipeline: source indexing,
candidate retrieval, schema validation, evidence qualification, decision
verification, authority-lease revalidation, audit hashing, and pass/fail
manifests. Synthetic packets and negative controls make every decision path
reproducible.

## Technical highlights

- Standard-library Python with no runtime dependencies.
- Deterministic verdicts and stable input hashes for reproducible evaluation.
- Separate semantic similarity, identity, evidence, and action-authority
  signals.
- Machine-readable reason codes and explicit review/revalidation routes.
- End-to-end CLI workflows, synthetic datasets, unit tests, and GitHub Actions.
- A frozen masked review covering 151 evaluation packets, including 146
  outcome-ready packets.
- An applied six-kernel CategoryVantage architecture for identity, evidence,
  truth, publication, action, and learning.

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
- Synthetic examples, negative controls, and unit tests.

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

## Implementation profile

The package runs locally on Python 3.11+, uses deterministic evaluation rules,
and operates on the included synthetic examples. Risk scores provide
consistent prioritization across the evaluation set; verdicts remain
traceable to their evidence identifiers and reason codes.

## Author

Huseyin Buldurgan — [LatentAtlas](https://latentatlas.ai/) ·
[LinkedIn](https://www.linkedin.com/in/hbuldurgan)
