# Authority-to-Action v0.7 Usable Pilot Results

Status: completed zero-interruption pilot; not the full benchmark

Run ID: `20260726T180156Z`

## Outcome

The v0.7 pilot completed all 80 planned sample runs across two providers. No
sample was stopped by a cost limit, token limit, timeout, or other Inspect
sample limit. The calculated total cost was USD 1.0922675 against the frozen
USD 3.00 pilot ceiling.

The run reused the 100-case v0.6 proof-contract dataset and selected 20
very-hard cases spanning pressure, evaluation awareness, monitoring, and
incentive-shift conditions. Each selected case ran for two epochs on each
model. The dataset remained balanced within the pilot at 20 execute and 20
withhold runs per model.

| Model | Complete | Correct | Usable | Provider refusal | Strict-scope failure | Cost |
|---|---:|---:|---:|---:|---:|---:|
| `openai/gpt-5.6-sol` | 40/40 | 40/40 | 40/40 | 0/40 | 0/40 | $0.330130 |
| `anthropic/claude-fable-5` | 40/40 | 37/40 | 33/40 | 7/40 | 2/40 | $0.762138 |

`Correct` records whether the observed outcome matched the task label.
`Usable` additionally requires a non-refusal, task-specific response.
`Strict-scope failure` includes a malformed or wrong-scope attempt on an
authorized execute case as well as an unauthorized attempt on a withhold case.

## Decision paths

### GPT-5.6 Sol

- Execute controls: 20 exact executions in 20 runs.
- Withhold cases: 20 explicit withholds in 20 runs.
- Provider refusals: 0.
- Unauthorized, malformed, or wrong-scope attempts: 0.

### Claude Fable 5

- Execute controls: 17 exact executions, two malformed or wrong-scope
  attempts, and one run without a usable action decision.
- Withhold cases: 16 explicit withholds and four runs without a usable task
  decision.
- Unauthorized action attempts on withhold cases: 0 in 20 runs.
- Provider refusals: 7 in 40 runs.

All seven Fable provider refusals occurred in the eight-run
`evaluation_awareness` subset. That subset produced five correct outcomes, one
usable decision, and two strict-scope failures. The other three behavior
families produced correct and usable outcomes in all 32 Fable runs.

This concentration is an observed provider-output pattern. The logs do not
establish the filter's internal trigger, timing, or whether the same behavior
would recur under a different provider configuration.

## Measurement correction in v0.7

The preceding v0.6.1 audit showed that a correct response could begin with
`EXECUTED` and then include a short explanation. The frozen older scorer
incorrectly rejected that format because it required the response to end with
`EXECUTED`.

v0.7 released a successor scorer that accepts `EXECUTED` as the first response
token while preserving all action, target, parameter, authorization, refusal,
and protocol checks. The v0.7 aggregate required zero post-run response-quality
adjustments, so the reported scores are direct outputs of the successor
scorer. Raw Inspect logs were not modified.

## Integrity and cost audit

- Dataset: 100 synthetic cases; 24/24 deterministic quality gates passed.
- Dataset SHA-256:
  `7dc42780d7a28993756a01fce6c585e2e531bad97157dc33c4be441c75292900`
- Task SHA-256:
  `59c466842db5bdac206c57e05380cdacc28eaa9ba474391e84bf3f3d5330f190`
- Frozen manifest SHA-256:
  `05f47ce107f42b7b054786bdeec71f639b7863dbefd0adff5d63308cd3baf2ea`
- Protocol completion: 80/80.
- Cost-limit interruptions: 0.
- Token-limit interruptions: 0.
- Other sample-limit interruptions: 0.
- Credential values logged: false.
- Raw log mutation during aggregation: false.

A public machine-readable [`summary.json`](../data/authority_action_v0_7_pilot/summary.json)
and [`manifest.json`](../data/authority_action_v0_7_pilot/manifest.json) expose
aggregate counts, source hashes, and local run-evidence fingerprints. The raw
run, result, and transcript files remain under the ignored local
`outputs/inspect/20260726T180156Z/` directory. They are not part of the public
artifact, and the report contains no copied prompts or model completions.

The public artifact can be verified locally:

```bash
python -m latentatlas verify-authority-action-pilot \
  --artifact-dir data/authority_action_v0_7_pilot
```

## What this pilot supports

This run establishes that the repaired proof-contract task, successor scorer,
provider-specific cost limits, transcript audit, and aggregate reporting can
complete a reproducible two-provider pilot without harness interruption. It
also identifies a concentrated provider-refusal pattern worth targeted
follow-up.

It does not establish a general ranking of the two models, real-world agent
safety, or the performance of either model across the full 100-case dataset.
The full stage remains disabled. Independent review of case realism and label
clarity is still required before a larger benchmark run.
