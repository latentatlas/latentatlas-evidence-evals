# Real API vs Offline Boundary Benchmark Comparison

Date: 2026-05-13

Scope: compare the earlier 500-row/offline Concept Boundary benchmark with the
current real API benchmark for OpenAI and Anthropic.

## Short Answer

The newer OpenAI and Anthropic results are better mainly because they are real
latest-model API outputs, while the earlier 500-row benchmark used explicit
offline behavior profiles designed to expose failure modes.

The tests are related but not identical. The 1000-row content set is slightly
less hostile than the 500-row fixture by base-rate composition, but that
difference is small compared with the gap between offline stress profiles and
real API models.

## What The Earlier 500 Benchmark Measured

Artifact:

- `outputs/latentatlas/concept_boundary_model_benchmark/model_summary.csv`
- `outputs/latentatlas/concept_boundary_engine_500/manifest.json`

It did not measure OpenAI or Anthropic. It measured three explicit behavior
profiles:

| Profile | Rows | Accuracy | False authority before guard | Valid cases over-reviewed | Primary failure |
| --- | ---: | ---: | ---: | ---: | --- |
| Similarity-first LLM profile | 500 | 24.0% | 380 | 0 | freshness_blindness |
| Evidence-aggressive LLM profile | 500 | 36.8% | 316 | 0 | peer_identity_confusion |
| Cautious-review LLM profile | 500 | 32.2% | 4 | 56 | review_routing_instead_of_hard_block |

Purpose: prove systematic failure categories and show the LatentAtlas guard can
block false authority while preserving valid allows.

Guard result:

| Metric | Value |
| --- | ---: |
| False authority after guard | 0 |
| Expected mismatch after guard | 0 |
| Valid allows preserved | 120/120 |

## What The Current Real API Snapshot Measures

Artifact:

- `outputs/latentatlas/concept_boundary_openai_anthropic_analysis_snapshot/openai_anthropic_model_detail.csv`
- `outputs/latentatlas/concept_boundary_real_llm_scores_1000_snapshot/model_summary.csv`

It measures real decision-classification outputs from OpenAI and Anthropic on
the 1000-row synthetic Concept Boundary content set.

| Model | Rows | Accuracy | False authority | Valid cases over-blocked/reviewed | Parse failures | False authority after guard |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OpenAI gpt-5.5 | 1000 | 92.4% | 31 | 5 | 0 | 0 |
| Anthropic claude-opus-4-7 | 1000 | 78.9% | 44 | 51 | 0 | 0 |

Guard result:

| Metric | Value |
| --- | ---: |
| False authority after guard | 0 |
| Expected mismatch after guard | 0 |
| Valid allows preserved | 270/270 |

## Dataset Difference

The datasets are the same research family but not the exact same fixture.

| Dataset | Rows | Valid allow count | Valid allow rate | Naive false authority | Naive false authority rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| 500-row fixture | 500 | 120 | 24.0% | 380 | 76.0% |
| 1000-row content set | 1000 | 270 | 27.0% | 730 | 73.0% |

Interpretation: the 1000-row set is slightly less hostile by composition, but
only by about three percentage points. That does not explain the jump from
24.0-36.8% offline profile accuracy to 78.9-92.4% real API accuracy.

## Commercial Interpretation

Do not claim:

- "OpenAI improved from 24% to 92%."
- "Claude improved from the 500-row benchmark."
- "The benchmark proves all real customer accuracy."

Allowed claim:

- The offline benchmark proves the failure taxonomy and guard behavior.
- The real API benchmark shows that even strong current models still create
  measurable boundary failures.
- LatentAtlas converts those failures into counted categories and reduces
  false-authority decisions to zero under the synthetic guard contract while
  preserving valid allows.

## Cleanest Next Verification

For strict apples-to-apples evidence, run OpenAI and Anthropic on the 500-row
fixture as well, or preserve this comparison as a two-layer proof:

1. Offline stress profiles: failure taxonomy and guard mechanics.
2. Real API models: current model behavior and buyer-facing evidence examples.
