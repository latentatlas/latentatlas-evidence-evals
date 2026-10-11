# Concept Boundary 500-Sample Expansion Plan

Status: research expansion plan  
Date: 2026-05-13

## Purpose

The current 12-case seed pack is a thesis canary. It proves the boundary idea is
measurable, but it is not a commercial benchmark.

The next research step is a 500-sample hard-negative pack that can support:

- 3-LLM boundary benchmarking
- deterministic LatentAtlas guard comparison
- buyer-facing diagnostic examples
- regression checks before product claims

## Current Seed Result

Source artifact:

- `outputs/latentatlas/concept_boundary_engine/summary.json`

Seed result:

- total cases: 12
- high-similarity cases: 12
- naive similarity allows: 12
- naive false-authority allows: 9
- boundary false-authority allows: 0
- allowed expected cases preserved: 3 of 3
- truth/customer surface mutation allowed: 0

## Expansion Shape

Use 12 archetypes as the base and generate controlled variations.

| Boundary archetype | Target rows | Purpose |
| --- | ---: | --- |
| related does not grant publish | 40 | prevent topic similarity from customer-facing claims |
| peer comparison does not grant identity | 50 | prevent similar products/entities from same-identity claims |
| bridge context does not grant evidence | 40 | prevent glossary/index/landing pages from becoming proof |
| evidence does not grant action | 45 | prevent answer support from becoming automation permission |
| evidence does not grant publish | 45 | prevent answer support from becoming customer-surface approval |
| stale/superseded evidence blocks use | 45 | test freshness and authority gates |
| contradiction blocks allow | 45 | test negative evidence and conflict handling |
| privacy blocks all downstream use | 40 | test customer-safe and data-minimization stop conditions |
| valid evidence support | 45 | preserve true positive evidence cases |
| valid action-ready | 40 | preserve true action cases |
| valid publish-safe | 35 | preserve true publish cases |
| adversarial mixed cases | 30 | combine high similarity with multiple conflicting signals |

Total: 500 rows.

## Required Fields

Each generated case must include:

- `case_id`
- `query`
- `candidate`
- `similarity_score`
- `requested_authority`
- `boundary_type`
- `source_authority`
- `freshness_state`
- `action_scope`
- `contains_sensitive_data`
- `expected_decision`
- `archetype`
- `variation_id`
- `expected_reason_family`

## 3-LLM Benchmark Protocol

For each model:

1. Provide the packet and boundary definitions.
2. Ask for:
   - boundary label
   - allowed action
   - reason
   - required missing proof if blocked
3. Score output against expected label and expected decision.
4. Count:
   - false-authority transfer
   - false block of valid cases
   - unnecessary review
   - missing proof explanation
   - privacy leak or unsafe reuse

The benchmark must report false-authority separately from aggregate accuracy.

## Deterministic Guard Protocol

Run the same 500 rows through `concept_boundary_probe.py` or its expanded
successor.

Required proof:

- boundary false-authority count: 0
- expected mismatch count: 0 or row-level justified
- valid allow cases preserved
- truth mutation allowed: 0
- customer surface mutation allowed: 0

## Commercial Readiness Gate

The 500-sample pack becomes buyer-facing only when:

- the generator is reproducible
- expected labels are stored in a manifest
- row-level examples are sanitized
- no customer data is used
- 3-LLM scoring output is separated from deterministic guard output
- customer-facing claims say "measured on this benchmark", not "guarantees truth"

## Implementation Artifacts

The expansion is implemented by:

- `build_concept_boundary_500_fixture.py`
- `concept_boundary_500_cases.jsonl`
- `outputs/latentatlas/concept_boundary_engine_500/summary.json`
- `outputs/latentatlas/concept_boundary_engine_500/decisions.csv`
- `outputs/latentatlas/concept_boundary_engine_500/report.md`
- `outputs/latentatlas/concept_boundary_engine_500/manifest.json`
- `outputs/latentatlas/concept_boundary_engine_500/archetype_counts.csv`
