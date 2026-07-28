# When Relevant Evidence Is Not Permission to Act

Status: completed public technical research note

Date: 27 July 2026

## Abstract

This case study evaluates whether API-delivered language-model systems can
distinguish information relevant to an action from current permission to
perform that exact action. The final benchmark contains 100 synthetic cases,
organized as 25 four-variant groups, and repeats every case three times across
two systems at medium reasoning effort. The resulting analytical set contains
600 protocol-complete runs.

Both delivered systems avoided acting in all 300 combined withhold runs. Their
main observed difference appeared on the authorized path. GPT-5.6 Sol completed
all 150 authorized actions exactly. Claude Fable 5 completed 99/150 exactly;
the remaining authorized runs included malformed or wrong-scope attempts,
no-action outcomes, and provider refusals. These results describe the frozen
synthetic benchmark and the delivered model-plus-provider systems on one run
date. They do not establish a general model ranking or real-world incident
rate.

The engineering contribution is broader than the score table: a versioned,
side-effect-free evaluation workflow that separates model decisions, provider
refusals, harness interruptions, strict action scope, and usable task output.

## Research question

When an agent receives evidence that is relevant to a requested action, does
it verify that the evidence is also current, final, verified, and scoped to the
exact actor, action, target, and parameters before acting?

This distinction matters because retrieval success is not execution authority.
A system may possess the right document but still have the wrong principal,
an expired permission, a draft approval, a superseded record, or a grant for a
different target.

## Benchmark design

The frozen dataset contains:

- 100 synthetic cases;
- 25 complete factorial groups;
- four variants per group: valid/invalid authority crossed with
  neutral/treatment context;
- 50 execute and 50 withhold cases;
- pressure, evaluation-awareness, monitoring, and incentive-shift families;
- medium, hard, and very-hard cases; and
- no external side effects.

Every requested action uses a local `execute_action` tool. A tool call is
recorded for scoring but cannot change an external system. Exact execution
requires the correct action, actor, target, parameters, authorization record,
and call count.

### Selected synthetic example

One four-variant group concerns resolving a simulated evaluation ticket. The
valid records grant the on-call role to the requesting actor during the
current shift, so both neutral and treatment variants require execution. The
invalid records assign the active shift to a different actor, so both variants
require withholding with an actor-scope reason.

This group also demonstrates why outcome correctness and usability are
separate. A system can correctly avoid the action but still fail the required
task-specific reason-code contract.

## Project stages

The project progressed through five distinct stages:

1. **Define the measurement.** The first pilot established a side-effect-free
   action tool and a deterministic scorer, then revealed that safe non-action
   and a usable task decision were being treated as the same outcome.
2. **Make action scope explicit.** The action contract was split into actor,
   operation, target, parameters, authorization record, and call count so a
   vaguely correct action could not pass as an exact execution.
3. **Increase case difficulty.** Easy conclusion-like prompts were replaced
   with multi-record packets requiring temporal, identity, provenance,
   supersession, role, and finality reasoning.
4. **Calibrate the measurement system.** Pilot runs exposed provider refusals,
   cost-limit interruptions, an incomplete evidence contract, and an overly
   strict response-format check. Each issue was corrected under a successor
   version while the original evidence remained unchanged.
5. **Freeze and execute.** After 24 deterministic quality gates and a masked
   author review, the final dataset, scorer, limits, batching plan, and repair
   rules were frozen before the 600-run experiment began.

## Problems found and corrections made

The benchmark reached its final form through measured corrections rather than
silent rewrites:

| Problem observed | Correction |
|---|---|
| Provider refusal was counted as a model decision | Separated safe outcome, usable decision, explicit withholding, and provider refusal |
| A single action string hid wrong-target and wrong-parameter attempts | Split action, target, parameters, and authorization ID into exact tool fields |
| Early cases were structurally balanced but too easy | Replaced conclusion-like evidence with multi-record temporal, identity, provenance, and supersession reasoning |
| Positive controls did not prove their own verification requirement | Added a machine-resolvable proof path and seven fail-closed evidence-contract gates |
| Top-level successful logs contained cost-limited samples | Added event-level protocol auditing and provider-specific sample limits |
| A correct `EXECUTED` response with trailing explanation failed formatting | Versioned the scorer to accept `EXECUTED` as the first token while preserving raw logs |
| A full run could fail midway | Froze complete-pair batches, provider checkpoints, and no-silent-rerun rules |

The complete development history remains available in the
[living development record](authority-action-evaluation-development-case-study.md).

## Review and execution controls

Before the full run, all 100 cases passed 24 deterministic gates and an
author-side masked review. The masked review produced 100/100 agreement with
the frozen expected action, 100/100 evidence-sufficient judgments, and 100/100
single-clear-decision judgments. Because the same author designed and reviewed
the cases, this is consistency evidence, not independent external validation.

The final run used:

- GPT-5.6 Sol and Claude Fable 5;
- medium reasoning effort;
- three epochs per case and model;
- five complete-pair batches;
- ten provider-batch checkpoints;
- provider-specific sample and total-cost limits; and
- immutable prompt, dataset, scorer, and manifest hashes.

## Execution audit

All 600 analytical slots completed. Three Anthropic attempts exceeded the
frozen 512-output-token protocol limit after partial responses. Each original
attempt remained in the operational audit. A separately frozen repair plan
repeated exactly one interrupted slot under the same model, reasoning,
message, token, and cost settings. Repair eligibility depended only on the
protocol interruption, never on the score or apparent outcome.

| Audit item | Result |
|---|---:|
| Analytical runs | 600 |
| Gross provider attempts | 603 |
| Verified checkpoints | 10/10 |
| Gross cost | $8.6929235 |
| Analytical-set cost | $8.5742080 |
| Protocol-repair overhead | $0.1187155 |

## Results

| API-delivered system | Correct | Usable | Exact authorized execution | Provider refusal | Strict-scope failure | Unauthorized action in withhold runs |
|---|---:|---:|---:|---:|---:|---:|
| GPT-5.6 Sol | 300/300 | 294/300 | 150/150 | 0/300 | 0/300 | 0/150 |
| Claude Fable 5 | 249/300 | 205/300 | 99/150 | 38/300 | 26/300 | 0/150 |

### GPT-5.6 Sol

GPT made the expected act-or-withhold choice on all 300 runs. It executed all
150 authorized cases exactly and made no action attempt in all 150 withhold
cases. Six actor-mismatch runs withheld correctly but did not satisfy the
task-specific reason-code usability gate.

### Claude Fable 5

Fable also made no action attempt in any withhold case. Its lower aggregate
result was concentrated on authorized cases:

- 99 exact executions;
- 26 malformed, duplicate, or wrong-scope attempts;
- 25 no-action outcomes; and
- 21 provider refusals.

The first three are exclusive action paths. Provider refusal is an orthogonal
signal: the 21 execute refusals overlap 15 no-action rows, five strict-scope
rows, and one exact-execution row. The 26 strict-scope failures comprise 23
duplicate-call rows and three single-call rows with an invalid schema.

Across withhold cases, it recorded 150/150 correct no-action outcomes, 133
explicit task-specific withholds, and 17 provider refusals.

Treatment wording coincided with lower Fable performance on authorized cases
in this dataset: correct decisions fell from 53/75 in `valid_neutral` to 46/75
in `valid_treatment`, while usable decisions fell from 45/75 to 33/75. This is
a paired benchmark observation, not evidence that arbitrary pressure wording
causes the difference.

The additive public analysis treats the 25 complete prompt groups as the
cluster units and separately checks three-epoch stability. Fable's full outcome
signature was stable for 70/100 cases; GPT's was stable for 100/100. The public
row ledger and group analysis are documented in the
[v0.8.3 analysis supplement](authority-action-v0-8-3-public-analysis.md).

## What we learned

### 1. The evaluation system itself must be evaluated

Several apparent model failures were measurement failures: cost ceilings
stopped samples inside otherwise successful logs, a positive control did not
prove its own verification requirement, and a scorer rejected correct answers
because an explanation followed the verdict. Inspecting the evaluator was as
important as inspecting the model.

### 2. Safe behavior and useful behavior are different measurements

A refusal or content filter can prevent an unsafe action while producing no
usable task decision. Recording only whether an action occurred would have
hidden this difference. The final analysis therefore keeps safe outcome,
correct decision, usable decision, provider refusal, and exact scope as
separate metrics.

### 3. The hardest observed problem was reliable authorized execution

Neither delivered system attempted an action in any of the 300 combined
withhold runs. The clearest difference appeared when permission was valid:
one system executed every authorized request exactly, while the other more
often refused, produced no action, or called the simulated tool with malformed
or wrong-scope arguments. In this benchmark, avoiding unauthorized action was
not the main differentiator; completing authorized work precisely was.

### 4. A provider-delivered system is the practical unit of observation

Provider refusals changed the behavior available to the caller, even though
the filter's internal trigger and timing were not visible. For an API user,
the observable system includes both the model response and the provider
enforcement layer.

### 5. Reproducibility requires an explicit repair history

Three final-run attempts exceeded the frozen output-token limit. Replacing
them silently would have made the final table impossible to audit. Retaining
the originals, selecting repairs only from protocol status, and reconciling
gross versus analytical cost made the completed result reproducible.

## What the result supports

The evidence supports three bounded conclusions:

1. The evaluation pipeline can run a repeated two-provider authority-to-action
   benchmark end to end while preserving checkpoints, repair lineage, cost
   reconciliation, and raw-log immutability.
2. Both delivered systems avoided unauthorized action in every withhold case
   in this synthetic benchmark.
3. The largest observed system difference was exact completion of authorized
   actions, not unauthorized execution.

The evidence does not establish a universal model ranking, production safety,
provider-filter internals, or real-world failure frequency.

## Public evidence and privacy boundary

The v0.8.2 package contains aggregate counts, metric definitions, cost
accounting, limitations, source hashes, and unpublished local-evidence
fingerprints. The additive v0.8.3 package publishes 600 allowlisted row-level
outcomes so reviewers can recompute every result. It excludes raw transcripts,
prompts, completions, tool arguments, provider payloads, credentials, live
credit snapshots, customer data, personal data, local paths, and source UUIDs.

Verify the package locally:

```bash
python -m latentatlas verify-authority-action-full-result \
  --artifact-dir data/authority_action_v0_8_2_full_medium
python -m latentatlas verify-authority-action-public-analysis \
  --artifact-dir data/authority_action_v0_8_3_analysis
```

Public artifacts:

- [`protocol.json`](../data/authority_action_v0_8_2_full_medium/protocol.json)
- [`summary.json`](../data/authority_action_v0_8_2_full_medium/summary.json)
- [`manifest.json`](../data/authority_action_v0_8_2_full_medium/manifest.json)
- [v0.8.3 transcript-free rows](../data/authority_action_v0_8_3_analysis/rows.jsonl)
- [v0.8.3 recomputed summary](../data/authority_action_v0_8_3_analysis/summary.json)
- [v0.8.3 analysis protocol](../data/authority_action_v0_8_3_analysis/protocol.json)
- [v0.8.3 integrity manifest](../data/authority_action_v0_8_3_analysis/manifest.json)
- [full technical results](authority-action-v0-8-2-full-medium-results.md)

## Conclusion

The project converted an initially conceptual question into a working
evaluation: 100 validated cases, an exact simulated action contract, two
provider systems, three repeated epochs, 600 analytical runs, deterministic
scoring, resumable execution, and verifiable aggregate artifacts.

Its central result is operational. Authority-to-action behavior can be
measured without conflating safe non-action, usable model judgment, provider
refusal, harness interruption, and exact tool scope. The resulting framework
is now a reusable base for testing new models, reasoning settings, and more
complex agent environments.
