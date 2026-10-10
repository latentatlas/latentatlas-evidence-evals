# Relevance Is Not Authority — open research data

Original paper: DOI 10.5281/zenodo.20161629 (13 May 2026).
Open-data addendum: 11 October 2026. The original PDF and sealed records are unchanged.

The former paid-access restriction described in section 8.2 of the historical
paper is superseded for the author-owned research material in this release.
Research data, original explanatory material and figures: CC BY 4.0.
Original research software: MIT. Third-party material retains its licence.

## Inspect

- `research/concept_boundary_engine/concept_boundary_1000_test_content.jsonl`: all 1,000 synthetic packets and expected labels.
- `research/concept_boundary_engine/concept_boundary_probe.py`: deterministic authority guard.
- `research/concept_boundary_engine/run_real_llm_boundary_benchmark.py`: provider runner and prompt construction.
- `research/concept_boundary_engine/score_real_llm_boundary_outputs.py`: decision scorer.
- `locked/`: the exact 17-file historical seal, including 2,990 cleaned decisions, 1,000 Voyage results, coverage and reported tables.
- `outputs/latentatlas/concept_boundary_real_llm_runs/`: retained original output, failures, cleaned output and merge provenance.

The sealed manifest is exactly the SHA-256 printed in the paper. The fixture
was not included in that 17-file seal. Its earliest tracked Git version is
14 May 2026; this release records its own byte identity separately. Rebuilt
fixture metadata has a later timestamp. Do not treat that metadata as a new
model experiment. Missing provider rows and retained failures stay visible.

## Recompute without API calls

From this directory:

```sh
python3 research/concept_boundary_engine/score_real_llm_boundary_outputs.py --input locked/outputs__latentatlas__concept_boundary_real_llm_runs__real_llm_outputs_cleaned.jsonl --cases research/concept_boundary_engine/concept_boundary_1000_test_content.jsonl --out-dir fresh-score
```

The guard uses packet attributes, not an independent human adjudication.
Public access permits inspection; it does not establish generalization or
independent validation. Running provider APIs is separate, incurs cost, and
requires the runner's explicit confirmation. No new API experiment was run.
