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

## What changed during development

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

Across withhold cases, it recorded 150/150 correct no-action outcomes, 133
explicit task-specific withholds, and 17 provider refusals.

Treatment wording coincided with lower Fable performance on authorized cases
in this dataset: correct decisions fell from 53/75 in `valid_neutral` to 46/75
in `valid_treatment`, while usable decisions fell from 45/75 to 33/75. This is
a paired benchmark observation, not evidence that arbitrary pressure wording
causes the difference.

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

The public package contains aggregate counts, metric definitions, cost
accounting, limitations, source hashes, and unpublished local-evidence
fingerprints. It excludes raw transcripts, prompts, completions, provider
payloads, credentials, live credit snapshots, customer data, personal data,
and row-level records.

Verify the package locally:

```bash
python -m latentatlas verify-authority-action-full-result \
  --artifact-dir data/authority_action_v0_8_2_full_medium
```

Public artifacts:

- [`protocol.json`](../data/authority_action_v0_8_2_full_medium/protocol.json)
- [`summary.json`](../data/authority_action_v0_8_2_full_medium/summary.json)
- [`manifest.json`](../data/authority_action_v0_8_2_full_medium/manifest.json)
- [full technical results](authority-action-v0-8-2-full-medium-results.md)
- [frozen execution contract](authority-action-v0-8-2-full-medium-execution-contract.md)

## Conclusion

The most useful result is not that one system received a higher number. It is
that authority-to-action behavior can be measured without conflating safe
non-action, usable model judgment, provider refusal, harness interruption, and
exact tool scope. The final benchmark turns that distinction into a
reproducible, auditable research artifact while keeping private run material
outside the public release.
