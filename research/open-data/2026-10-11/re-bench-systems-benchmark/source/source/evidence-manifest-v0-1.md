# RE-Bench review methods and evidence manifest v0.1

**State:** Public working-review support artifact

**Evidence cutoff:** 2026-08-25

**Review type:** Unaffiliated, source-grounded, single-owner technical audit

**Reproduction state:** No benchmark-hardware or headline-score reproduction

**Publisher and maintainer:** [LatentAtlas](https://github.com/latentatlas),
with corrections accepted through the repository's [issue tracker](https://github.com/latentatlas/latentatlas-evidence-evals/issues)

## Review question and maximum claim

The review asks what RE-Bench directly measures, what its reported results
support, and which stronger inferences require evidence outside the benchmark.
Its unit of analysis is the evaluated model-scaffold-tool-environment protocol,
including feedback, resources, attempt allocation, and selection.

The maximum suite-level interpretation is:

> Under the declared task versions, scaffold, prompts, tools, compute,
> feedback, attempt allocation, selection rule, and time budget, the evaluated
> system produced task artifacts whose scorer-accepted normalized results were
> combined under the declared per-task rules.

This does not establish base-model-only capability, reliable single-run
autonomy, long-horizon research ownership, or general frontier-R&D automation.

## Primary evidence surfaces

| ID | Surface | Version or cutoff | Role |
|---|---|---|---|
| `PAPER-V2` | [RE-Bench arXiv paper](https://arxiv.org/html/2411.15114v2) | v2, 2025-05-27 | Historical methods, results, and limitations |
| `PMLR-2025` | [ICML/PMLR publication](https://proceedings.mlr.press/v267/wijk25a.html) | PMLR 267 | Archival publication identity |
| `METR-RELEASE` | [METR release report](https://metr.org/blog/2024-11-22-evaluating-r-d-capabilities-of-llms/) | 2024-11-22 | Author-organization summary |
| `RELEASE-2024` | [Official public release](https://github.com/METR/RE-Bench/commit/e961ef72d46064ace2ab5a4fbd8c6582962be7a3) | `e961ef72…` | First identified public repository release; not proven paper-run code |
| `REFRESH-2024` | [Task refresh](https://github.com/METR/RE-Bench/commit/736ead76193fa933b622992321d006d9836d2f53) | `736ead76…` | Later public task surface |
| `AUDIT-2025` | [Pinned audit snapshot](https://github.com/METR/RE-Bench/commit/93b98062e55f6945d4a7e213a3226dd419896170) | `93b98062…` | Source-contract audit surface |
| `METR-RH-2025` | [Reward-hacking report](https://metr.org/blog/2025-06-05-recent-reward-hacking/) | 2025-06-05 | Separate later o3 evaluation; no transfer to 2024 runs |
| `TPS-021` | [task-protected-scoring v0.2.1](https://github.com/METR/task-protected-scoring/tree/v0.2.1) | v0.2.1 | Aggregation and invalid-score semantics |

The paper experiments predate the official public repository release. The
public sequence `e961ef72…` -> `736ead76…` -> `93b98062…` establishes source
evolution, not the exact package identity or effect size for the historical
paper runs.

## Evidence-state vocabulary

| State | Meaning | Prohibited transfer |
|---|---|---|
| `paper_reported` | A result or method attributed to the historical paper | Do not call it independently reproduced |
| `release_source_confirmed` | A property of the identified 2024 public release | Do not assume the paper runs used it |
| `pinned_source_confirmed` | A property of commit `93b98062…` | Do not assign it to historical runs |
| `locally_executed_contract_check` | A bounded behavior reproduced against hash-pinned public files | Do not call it a task, model, H100, or headline rerun |
| `later_author_reported_evaluation` | A separate later result reported by METR | Do not retroactively classify 2024 runs |
| `needs_historical_mapping` | Exact historical linkage is absent | Do not encode the gap as pass, fail, zero, or invalidity |
| `not_run` | The named runtime experiment was not executed | Do not treat absence of execution as a negative result |
| `not_independently_reviewed` | No human second reviewer has adjudicated the claim | Do not claim peer review, agreement, or independent verification |

## Inspection and example-selection procedure

All seven task packages at the pinned commit were statically inspected for:

1. prose, input, output, resource, and dependency contracts;
2. the code path that produces a score or validity verdict;
3. participant-visible feedback and its timing;
4. within-run aggregation and across-run selection;
5. historical paper claims versus pinned implementation properties;
6. the narrowest supported claim; and
7. the next test needed to discriminate unresolved interpretations.

Kernel, Scaling Law, and LLM Foundry were selected for public explanation
because they expose different measurement risks. This is purposive explanatory
sampling, not a defect-prevalence estimate.

## Bounded executable checks

The published [contract checks](contract_checks_v0_1.py) inspect or load four
public files from the pinned snapshot. They fail closed if source hashes drift.
The optional check requires Python 3.11 or newer and the separately pinned
[`numpy==2.3.5`](requirements-audit.txt); this is an audit-only dependency, not
a runtime dependency of the core repository package.

| Pinned source file | SHA-256 |
|---|---|
| `ai_rd_small_scaling_law/ai_rd_small_scaling_law.py` | `bfee000890adb8c1b9097e41aa0cde6535d8a8d21e2eb19bd9b6ea371f1b5f73` |
| `ai_rd_triton_cumsum/ai_rd_triton_cumsum.py` | `50ae825d7f3390eceac2dad25b4594b5c1ccd1bc493f578e33da6307412c82b5` |
| `ai_rd_optimize_llm_foundry/ai_rd_optimize_llm_foundry.py` | `f87048633f30fd10b3af7243160b00e554d3e434e4d18b14bde8d91ebb8dc900` |
| `ai_rd_optimize_llm_foundry/assets/score.py` | `27803f2c25bdf34287f04189e0a4930b93db412eafcf1ee09129834a225ffa17` |

The 2026-08-25 execution completed `8/8` tests. It confirmed:

- Scaling loss independence from `n_embd` at fixed `max_iters`;
- implemented score `1.0` for one under-budget width/step pair using less than
  0.1% of target FLOPs;
- Kernel preservation of a stubbed valid aggregate and conversion of a stubbed
  all-invalid `NaN` aggregate to numeric `0`; that fallback is not a measured
  timing;
- the duplicated LLM Foundry `hidden_score` literal and surviving second value;
- per-tensor `torch.norm` accumulation alongside the L1 label; and
- all four pinned source hashes.

The checks did not execute a participant solution, protected scorer service,
H100 workload, model trajectory, historical run, or official solution archive.
See the [execution receipt](contract-audit-result-v0-1.md).

## Claim boundaries added during red-team review

- For six tasks, paper-level `score@k` samples recorded attempt results with
  replacement and selects the maximum. Scaling Law randomly selects one sampled
  result because the target score is hidden.
- A high suite score aggregates task-level artifacts under per-task rules; it
  is not one seven-task work product from one continuous run.
- Kernel and LLM Foundry runtime interpretations are conditional score
  semantics because this review did not execute those tasks.
- The duplicate LLM Foundry `hidden_score` key is confirmed, but the pinned
  suite manifest selects only `main`.
- The 2025 reward-hacking counts concern reviewed runs with an earlier version
  of o3; the reported `39/128` total excludes Restricted MLM, whose
  classification was uncertain.

## Contamination and protected-material boundary

The official solution archive was not opened or used for this audit, and no
protected solution material is reproduced. Model pretraining contamination and
all prior exposure remain unknown; procedure-level control is not proof of
global absence. Repeated evaluator access, pretraining contamination, and
same-process evaluator subversion are separate mechanisms and are not merged
into one label.

## Open evidence gaps

| Gap | State | Consequence |
|---|---|---|
| Exact paper-run task, runner, base-image, dependency, and artifact mapping | `unresolved` | Pinned findings cannot be assigned to 2024 runs |
| H100 task and headline-score reproduction | `not_run` | No independent numerical replication claim |
| Preregistered trajectory sample and prevalence estimate | `not_run` | Illustrative process findings are not frequency estimates |
| Independent human adjudication | `not_completed_post_publication_review_welcome` | No peer-review, agreement, consensus, or independent-verification claim |

## Authorship, release, and correction policy

Research synthesis, source navigation, contract-test preparation, and drafting
were AI-assisted under human direction. An AI-generated interpretation is not
evidence. The owner authorized v0.1 for public release on 2026-08-25 without
prior independent human adjudication. That decision permits public availability
but does not upgrade the assurance label.

Corrections must name the affected claim, evidence state, contradicting or
narrowing source/version, replacement wording, and remaining gap. Material
changes are dated in the [changelog](changelog.md); they are not silently
overwritten.
