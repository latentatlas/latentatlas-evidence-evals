# Concept Boundary Engine

Status: seed research lane  
Date: 2026-05-12

## Thesis

LLM systems are often good at detecting that two things are related. They are
less reliable at deciding what authority that relation grants.

The boundary chain is:

```text
related
-> same_identity
-> evidence_support
-> action_ready
-> publish_safe
-> customer_safe
```

Skipping a boundary creates false authority.

## Initial Proof

The seed probe compares:

- a naive similarity baseline: allow high-similarity candidates
- a deterministic boundary engine: allow only when the requested authority is
  supported by the relation, source authority, freshness, and action scope

Run:

```bash
python3 research/concept_boundary_engine/concept_boundary_probe.py
```

Outputs:

- `outputs/latentatlas/concept_boundary_engine/summary.json`
- `outputs/latentatlas/concept_boundary_engine/decisions.csv`
- `outputs/latentatlas/concept_boundary_engine/report.md`

## Expansion Plan

The 12-case seed pack is not a commercial benchmark. The next planned expansion
is a 500-sample hard-negative pack for 3-LLM boundary benchmarking and
deterministic guard comparison.

See:

- `research/concept_boundary_engine/500_sample_expansion_plan.md`

Build and run the 500-row fixture:

```bash
python3 research/concept_boundary_engine/build_concept_boundary_500_fixture.py
```

Outputs:

- `research/concept_boundary_engine/concept_boundary_500_cases.jsonl`
- `outputs/latentatlas/concept_boundary_engine_500/manifest.json`
- `outputs/latentatlas/concept_boundary_engine_500/summary.json`
- `outputs/latentatlas/concept_boundary_engine_500/decisions.csv`
- `outputs/latentatlas/concept_boundary_engine_500/archetype_counts.csv`

Build the 1000-row customer-readable test content set:

```bash
python3 research/concept_boundary_engine/build_concept_boundary_1000_test_content.py
```

Outputs:

- `research/concept_boundary_engine/concept_boundary_1000_test_content.jsonl`
- `outputs/latentatlas/concept_boundary_engine_1000_content/content_catalog.csv`
- `outputs/latentatlas/concept_boundary_engine_1000_content/sample_cases.md`
- `outputs/latentatlas/concept_boundary_engine_1000_content/manifest.json`

## Model Benchmark Presentation

Run the offline before/after benchmark and sales-report generator:

```bash
python3 research/concept_boundary_engine/run_concept_boundary_model_benchmark.py
```

This does not call external LLM services. It scores three explicit
model-behavior profiles and also emits a prompt pack for future real-LLM runs.

Outputs:

- `outputs/latentatlas/concept_boundary_model_benchmark/benchmark_manifest.json`
- `outputs/latentatlas/concept_boundary_model_benchmark/model_summary.csv`
- `outputs/latentatlas/concept_boundary_model_benchmark/error_category_summary.csv`
- `outputs/latentatlas/concept_boundary_model_benchmark/before_after_summary.csv`
- `outputs/latentatlas/concept_boundary_model_benchmark/presentation_brief.md`
- `outputs/latentatlas/concept_boundary_model_benchmark/sellable_insights.md`
- `outputs/latentatlas/concept_boundary_model_benchmark/real_llm_prompt_pack.jsonl`

Score real LLM outputs after the external model calls are collected:

```bash
python3 research/concept_boundary_engine/score_real_llm_boundary_outputs.py \
  --input path/to/real_llm_outputs.jsonl \
  --cases research/concept_boundary_engine/concept_boundary_1000_test_content.jsonl
```

Expected real-output rows:

```json
{"model_id":"provider-model","case_id":"cbe500-0001","decision":"block_false_authority","reason":"short reason"}
```

Run a controlled real-LLM benchmark directly from the 1000-row content set:

```bash
OPENAI_API_KEY=... OPENAI_MODEL=gpt-5.5 \
ANTHROPIC_API_KEY=... ANTHROPIC_MODEL=claude-opus-4-7 \
COHERE_API_KEY=... COHERE_MODEL=command-a-reasoning-08-2025 \
VOYAGE_API_KEY=... VOYAGE_RERANK_MODEL=rerank-2.5 \
python3 research/concept_boundary_engine/run_real_llm_boundary_benchmark.py \
  --limit 10 \
  --confirm-third-party
```

Or use the interactive local prompt script:

```bash
bash research/concept_boundary_engine/prompt_for_api_keys_and_run_smoke.sh
```

OpenAI `gpt-5.5`, Anthropic `claude-opus-4-7`, and Cohere
`command-a-reasoning-08-2025` are scored as decision-classification LLMs. They
are not embedding models. Voyage `rerank-2.5` is scored as a rerank/relevance
baseline, because Voyage's hosted API is for embedding and reranking rather than
final boundary decisions.

Limited runs default to stratified sampling across archetypes instead of taking
only the first rows. Use `--selection first` only when reproducing a specific
prefix. Use `--full` only after the stratified smoke run is accepted, because
the full run sends 1000 synthetic packets to every configured provider. The
runner writes no API key values to artifacts and fails closed when required
provider config is missing.

Outputs:

- `outputs/latentatlas/concept_boundary_real_llm_runs/manifest.json`
- `outputs/latentatlas/concept_boundary_real_llm_runs/real_llm_outputs.jsonl`
- `outputs/latentatlas/concept_boundary_real_llm_runs/voyage_rerank_outputs.jsonl`
- `outputs/latentatlas/concept_boundary_real_llm_scores_1000/manifest.json`
- `outputs/latentatlas/concept_boundary_real_llm_scores_1000/model_summary.csv`

If a resumed full run intentionally skips rows from an earlier smoke run, write
a separate cleaned scoring input instead of mutating the raw artifact:

```bash
python3 research/concept_boundary_engine/merge_real_llm_boundary_outputs.py
```

Outputs:

- `outputs/latentatlas/concept_boundary_real_llm_runs/real_llm_outputs_cleaned.jsonl`
- `outputs/latentatlas/concept_boundary_real_llm_runs/real_llm_outputs_cleaned_manifest.json`

Build the real-LLM sales evidence pack from cleaned outputs:

```bash
python3 research/concept_boundary_engine/audit_real_llm_boundary_coverage.py
python3 research/concept_boundary_engine/build_real_llm_boundary_evidence_pack.py \
  --raw-outputs outputs/latentatlas/concept_boundary_real_llm_runs/real_llm_outputs_cleaned.jsonl
```

Outputs:

- `outputs/latentatlas/concept_boundary_real_llm_coverage_audit/manifest.json`
- `outputs/latentatlas/concept_boundary_real_llm_coverage_audit/coverage_by_model.csv`
- `outputs/latentatlas/concept_boundary_real_llm_coverage_audit/missing_cases.csv`
- `outputs/latentatlas/concept_boundary_real_llm_evidence_pack/manifest.json`
- `outputs/latentatlas/concept_boundary_real_llm_evidence_pack/real_llm_executive_brief.md`
- `outputs/latentatlas/concept_boundary_real_llm_evidence_pack/real_model_scorecard.csv`
- `outputs/latentatlas/concept_boundary_real_llm_evidence_pack/real_category_solution_matrix.csv`
- `outputs/latentatlas/concept_boundary_real_llm_evidence_pack/real_example_failures.csv`

Build the detailed OpenAI/Anthropic research readout:

```bash
python3 research/concept_boundary_engine/build_openai_anthropic_boundary_analysis.py
```

Outputs:

- `outputs/latentatlas/concept_boundary_openai_anthropic_analysis/manifest.json`
- `outputs/latentatlas/concept_boundary_openai_anthropic_analysis/openai_anthropic_detailed_analysis.md`
- `outputs/latentatlas/concept_boundary_openai_anthropic_analysis/openai_anthropic_model_detail.csv`
- `outputs/latentatlas/concept_boundary_openai_anthropic_analysis/openai_anthropic_error_categories.csv`
- `outputs/latentatlas/concept_boundary_openai_anthropic_analysis/openai_anthropic_archetypes.csv`

## Sales Evidence Pack

Build the customer-facing proof package from the 1000-row content set:

```bash
python3 research/concept_boundary_engine/build_boundary_sales_evidence_pack.py
```

This regenerates the 1000-row content proof, scores three offline
model-behavior profiles, then writes categorized before/after sales artifacts.

Outputs:

- `outputs/latentatlas/concept_boundary_sales_evidence_pack/manifest.json`
- `outputs/latentatlas/concept_boundary_sales_evidence_pack/executive_sales_brief.md`
- `outputs/latentatlas/concept_boundary_sales_evidence_pack/category_solution_matrix.md`
- `outputs/latentatlas/concept_boundary_sales_evidence_pack/category_solution_matrix.csv`
- `outputs/latentatlas/concept_boundary_sales_evidence_pack/model_failure_scorecard.csv`
- `outputs/latentatlas/concept_boundary_sales_evidence_pack/sales_example_cases.csv`
- `outputs/latentatlas/concept_boundary_sales_evidence_pack/customer_examples.md`

## Product Claim Under Test

> Similarity is useful for candidate retrieval, but it must not authorize
> identity, evidence, action, publish, or customer claims without a boundary
> check.

## Promotion Gate

This research lane can become product behavior only after:

- hard-negative fixtures cover all boundary types
- the baseline false-authority rate is measurable
- the boundary engine reduces false-authority cases without hiding allowed cases
- decision rows include reason codes and requested authority
- no production truth or customer surface is mutated by the probe
