# Real API Model Performance Breakdown

Date: 2026-05-13

Scope: final readout from the paid Concept Boundary real API benchmark.

Locked artifact folder:

- `outputs/latentatlas/locked_benchmarks/concept_boundary_real_api_20260513`

Primary evidence:

- `outputs/latentatlas/concept_boundary_real_llm_evidence_pack/real_model_scorecard.csv`
- `outputs/latentatlas/concept_boundary_real_llm_scores_1000_full/error_category_summary.csv`
- `outputs/latentatlas/concept_boundary_openai_anthropic_analysis/openai_anthropic_detailed_analysis.md`
- `outputs/latentatlas/concept_boundary_voyage_rerank_analysis/voyage_rerank_analysis.md`
- `outputs/latentatlas/concept_boundary_real_llm_coverage_audit/manifest.json`

## Executive Summary

OpenAI was the strongest decision model on this benchmark. Anthropic was safer
than Cohere on false authority, but created more over-review / wrong-route drag.
Cohere produced the highest false-authority count and has 99% coverage because
10 rows were blocked by provider quota/rate-limit `429`.

Voyage should not be compared as a decision model. It is the rerank baseline.
Its value is architectural: relevance and authority are not the same layer.

## Overall Decision Model Scorecard

| Model | Coverage | Accuracy | False authority before guard | False valid block/review | False authority after guard | Valid allows preserved |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OpenAI `gpt-5.5` | 1000/1000 | 92.4% | 31 | 5 | 0 | 270/270 |
| Anthropic `claude-opus-4-7` | 1000/1000 | 78.9% | 44 | 51 | 0 | 270/270 |
| Cohere `command-a-reasoning-08-2025` | 990/1000 | 73.03% | 139 | 21 | 0 | 268/268 |

Interpretation:

- OpenAI: best overall balance; remaining weakness is mostly bridge-context and
  limited evidence/action boundary overreach.
- Anthropic: moderate false authority, high routing drag; strongest on privacy,
  contradiction, same-identity, and customer-safe boundaries.
- Cohere: useful but materially riskier for false authority; weakest on bridge
  context, same-identity, publish-safe, and evidence-to-action jumps.

## Error Groups

| Error group | Total rows | Affected models | Commercial meaning |
| --- | ---: | --- | --- |
| Wrong block or route | 228 | all decision models | The model picked the wrong lane even when it did not unsafe-allow. |
| Bridge context treated as evidence | 91 | all decision models | Glossary/navigation/context was treated as proof. |
| Evidence promoted into action permission | 65 | all decision models | True fact became unauthorized operational action. |
| Valid evidence support unnecessarily reviewed | 55 | all decision models | Valid evidence was slowed down by unnecessary review. |
| Hard blocks diluted into manual review | 35 | all decision models | Blocked cases were made ambiguous instead of hard-stopped. |
| Evidence promoted into publish-safe output | 24 | all decision models | Supported fact became customer-facing/publish-safe claim. |
| Peer comparison treated as same identity | 20 | Anthropic, Cohere | Similar object was treated as same object. |
| Topic similarity promoted into publish/customer-safe authority | 14 | Cohere | Related document became publish/customer-safe permission. |

Model-specific pattern:

- OpenAI false authority: 31 total.
  - bridge context as evidence: 19
  - evidence to action: 7
  - evidence to publish: 5
- Anthropic false authority: 44 total.
  - evidence to action: 32
  - bridge context as evidence: 8
  - evidence to publish: 3
  - peer identity confusion: 1
- Cohere false authority: 139 total.
  - bridge context as evidence: 64
  - evidence to action: 26
  - peer identity confusion: 19
  - evidence to publish: 16
  - topic similarity to publish/customer-safe: 14

## Requested Authority Breakdown

| Model | Boundary | Rows | Accuracy | False authority | False valid block/review | Main weakness |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| OpenAI | action_ready | 188 | 96.28% | 7 | 0 | evidence_to_action_overreach |
| OpenAI | evidence_support | 368 | 85.05% | 19 | 5 | bridge_context_as_evidence / wrong route |
| OpenAI | publish_safe | 258 | 96.51% | 5 | 0 | evidence_to_publish_overreach |
| OpenAI | customer_safe | 96 | 95.83% | 0 | 0 | review routing |
| OpenAI | same_identity | 90 | 98.89% | 0 | 0 | rare review routing |
| Anthropic | action_ready | 188 | 71.28% | 32 | 10 | evidence_to_action_overreach |
| Anthropic | evidence_support | 368 | 67.39% | 8 | 31 | wrong route / over-review |
| Anthropic | publish_safe | 258 | 86.43% | 3 | 10 | wrong route / over-review |
| Anthropic | customer_safe | 96 | 98.96% | 0 | 0 | rare wrong route |
| Anthropic | same_identity | 90 | 98.89% | 1 | 0 | peer identity confusion |
| Cohere | action_ready | 186 | 72.58% | 26 | 1 | evidence_to_action_overreach |
| Cohere | evidence_support | 367 | 71.12% | 64 | 19 | bridge_context_as_evidence |
| Cohere | publish_safe | 254 | 70.47% | 27 | 1 | wrong route / review / publish overreach |
| Cohere | customer_safe | 93 | 95.7% | 3 | 0 | topic_similarity_to_customer_safe |
| Cohere | same_identity | 90 | 65.56% | 19 | 0 | peer_identity_confusion |

## Archetype Breakdown

Strong across all decision models:

- contradiction blocks: OpenAI 100%, Anthropic 100%, Cohere 100%
- privacy blocks: OpenAI 100%, Anthropic 100%, Cohere 100%

OpenAI weakest archetypes:

| Archetype | Rows | Accuracy | False authority | Main issue |
| --- | ---: | ---: | ---: | --- |
| bridge_context_does_not_grant_evidence | 80 | 71.25% | 19 | bridge context treated as evidence |
| stale_or_superseded_evidence_blocks_use | 90 | 70.0% | 0 | wrong block/route, not unsafe allow |
| evidence_does_not_grant_action | 90 | 92.22% | 7 | evidence promoted into action |
| evidence_does_not_grant_publish | 90 | 92.22% | 5 | evidence promoted into publish |

Anthropic weakest archetypes:

| Archetype | Rows | Accuracy | False authority | Main issue |
| --- | ---: | ---: | ---: | --- |
| stale_or_superseded_evidence_blocks_use | 90 | 15.56% | 0 | wrong block/route, not unsafe allow |
| evidence_does_not_grant_action | 90 | 53.33% | 32 | evidence promoted into action |
| valid_evidence_support | 100 | 69.0% | 0 | over-review valid evidence |
| bridge_context_does_not_grant_evidence | 80 | 83.75% | 8 | bridge context treated as evidence |

Cohere weakest archetypes:

| Archetype | Rows | Accuracy | False authority | Main issue |
| --- | ---: | ---: | ---: | --- |
| bridge_context_does_not_grant_evidence | 80 | 8.75% | 64 | bridge context treated as evidence |
| evidence_does_not_grant_action | 90 | 48.89% | 26 | evidence promoted into action |
| evidence_does_not_grant_publish | 90 | 58.89% | 16 | evidence promoted into publish |
| related_does_not_grant_publish | 80 | 60.0% | 11 | topic similarity promoted into publish |
| peer_comparison_does_not_grant_identity | 90 | 65.56% | 19 | peer treated as identity |

## Voyage Rerank Breakdown

Voyage `rerank-2.5` completed 1000/1000 rows. It is not a decision model.

Score distribution:

| Avg | Median | P75 | P90 | P95 | Max |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.4683 | 0.439453125 | 0.55859375 | 0.70703125 | 0.765625 | 0.9140625 |

Threshold pressure:

| Threshold | High relevance rows | False-authority pressure rows | Pressure rate |
| ---: | ---: | ---: | ---: |
| 0.8 | 22 | 0 | 0.0% |
| 0.7 | 105 | 24 | 22.86% |
| 0.6 | 206 | 68 | 33.01% |
| 0.5 | 342 | 140 | 40.94% |
| 0.4 | 603 | 366 | 60.7% |
| 0.3 | 906 | 636 | 70.2% |

Voyage interpretation:

> Voyage supports the architecture thesis: retrieval/rerank quality can be good
> while decision authority remains a separate control. At a strict 0.8 threshold
> the high-relevance set is clean, but at 0.7 and below the retrieval layer begins
> surfacing many rows that still require a boundary block.

## Sales Thesis

The strongest claim is not that models are bad. The strongest claim is:

> Relevance, evidence, action, publish safety, customer safety, and identity are
> separate authority layers. Current strong models still cross those boundaries.
> LatentAtlas turns the crossings into measured categories and blocks
> false-authority while preserving valid allows.

Do not rerun this paid benchmark unless there is a new model, new benchmark
version, or explicit retry need for Cohere's quota-blocked 10 rows.
