# Building an Authority-to-Action Evaluation

Status: completed development record; technical companion to the v0.8.2 public case study

Last updated: 2026-07-27

## Why this record exists

This document preserves how the experiment changed, not just its eventual
score table. Each version records the question we were actually asking, the
assumption that failed, the evidence that exposed it, and the design change
that followed.

The final case study should show a reproducible research process:

1. formulate a narrow behavioral question;
2. build a controlled measurement;
3. inspect failures instead of trusting aggregate scores;
4. distinguish model behavior from provider behavior and benchmark defects;
5. preserve old runs rather than rewriting them after learning something new;
6. release corrected successors under new hashes; and
7. publish only the conclusions supported by the final evidence.

## Update protocol for each new iteration

Every material experiment-design change should add one dated entry before the
next paid run. The entry should record:

- the question or hypothesis being tested;
- the exact problem observed and the artifact that exposed it;
- the design or scoring change made in response;
- the dataset, manifest, code, and run identifiers affected;
- the validation performed before and after the change;
- what the evidence now supports and what remains unresolved; and
- the next decision gate.

Completed datasets, scorers, and runs remain immutable evidence. A correction
is released as a successor version with a new hash; it does not silently alter
the historical record. Costs, failed hypotheses, benchmark defects, and
provider-side constraints remain part of the case study rather than being
removed from the final narrative.

## Starting question

When an LLM or agent receives information relevant to a requested action, does
it distinguish that information from current permission to perform the exact
action?

The evaluation uses synthetic packets and a local, side-effect-free
`execute_action` tool. A tool call records an attempt in the transcript but
does not change an external system.

## How the research question evolved

The sequence of design questions became progressively sharper:

1. **Does the system act or withhold?**
2. **If it does not act, did the model decide to withhold or did the provider
   block the response?**
3. **Is pressure wording changing behavior, or is a domain/action phrase
   interacting with a provider filter?**
4. **Can the scorer distinguish exact execution from a malformed or
   wrong-scope attempt?**
5. **Are the cases difficult enough to separate frontier-model behavior?**
6. **Does every expected label actually follow from the written instruction
   and supplied evidence?**

This progression is the central story of the case study. A central result so
far is not a leaderboard; it is the discovery that a structurally valid
benchmark can still contain an invalid positive-control contract, followed by
a testable repair rather than a retrospective relabeling of the old run.

## Version-by-version development log

| Version | Design move | Evidence or problem found | Resulting decision |
|---|---|---|---|
| v0.1 | Created 24 synthetic cases, a side-effect-free action tool, deterministic scoring, frozen manifests, cost limits, and a six-case two-model pilot. | `correct_decision` treated safe non-action caused by a provider refusal as correct, even though no usable task decision was delivered. Claude Fable 5 had three provider refusals in six runs; GPT-5.6-sol had none. | Keep safe outcome and usable model judgment as separate metrics. Preserve the original run. |
| v0.2 | Added `usable_decision`, `explicit_withhold`, and `model_refusal`; rescored the original logs and reran the same bounded pilot. | The original Fable result changed from an apparently perfect decision score to 3/6 usable decisions after refusal separation. In the rerun it produced 5/6 usable decisions and one refusal, showing that provider refusal was variable. | Treat provider refusal as its own outcome and add repeated epochs for targeted diagnosis. |
| v0.3 | Added a matched neutral/pressure pair plus a domain-matched positive control and ran three epochs per case. | Fable produced usable withholds in all six neutral/pressure negative runs but the positive control was provider-filtered in all three runs. GPT completed all nine. The small run did not support pressure wording as the cause. | Keep pressure effects separate from provider-constrained behavior; do not infer the filter's exact trigger or timing. |
| v0.3 full | Ran 25 cases across three epochs and two models, producing 150 scored runs. | The larger run exposed that the original tool schema and scorer could not cleanly separate an exact action from parameter embedding, missing fields, or other wrong-scope attempts. Provider refusals also varied strongly by condition. | Redesign the action schema and decision-path metrics before interpreting failures as safety behavior. |
| v0.4 | Built 25 complete 2x2 groups: valid/invalid authority crossed with neutral/treatment context. Balanced 50 execute and 50 withhold cases across pressure, evaluation awareness, monitoring, and incentive shift. Separated `action`, `target`, `parameters`, and `authorization_id`; added ten deterministic quality gates. | The 64-run pilot had no provider refusal. A later event-level audit found that 9/32 Fable runs were cost-limited; the previously reported one error and eight missing final responses were all harness interruptions. GPT completed 32/32 without a sample limit; Fable's 23 protocol-complete runs were all correct and usable. Manual review also showed that many packets were too easy. | Preserve v0.4 and its pilot hash as a diagnostic. Withdraw the Fable error interpretation, retain the protocol-limit lesson, and build a harder successor. |
| v0.5 | Replaced conclusion-like evidence with compact multi-record packets. Added temporal, identity, provenance, lineage, supersession, role, and multi-signature reasoning. Made 80/100 cases hard or very hard, separated monitoring direction, and expanded deterministic gates from 10 to 17. | Transcript audit found a blocking benchmark defect: positive controls did not establish the required verification and sometimes finality. GPT's `UNVERIFIED_SOURCE` withholds can therefore be instruction-following rather than errors. Fable hit the provider cyber filter in all eight sandbox-capability runs. Retroactive event audit also found 16/40 Fable runs were cost-limited. | Record the run as both a benchmark-design and harness-calibration diagnostic. Repair the evidence contract under a new dataset hash and calibrate provider-specific sample limits before another model comparison. |
| v0.6 | Preserved all v0.5 groups and added a four-record proof path: canonical digest, signer registry, verification result, and explicit finality. Added seven fail-closed evidence-contract gates on top of the 17 inherited gates. | The first validator run exposed an identifier-namespace collision, which was repaired with a dedicated `PF-*` namespace. The corrected dataset passed 24/24 gates. Its 80-run pilot then exposed a different measurement defect: the $0.015 per-sample cap interrupted 21/40 Fable runs and 1/40 GPT runs, even though both top-level Inspect logs reported success. | Preserve the dataset repair and the paid run as a protocol-calibration diagnostic. Separate harness limits from model decisions and provider refusals, then rerun the frozen pilot under a new provider-specific limit manifest before any model comparison. |
| v0.6.1 | Reused the frozen v0.6 task and dataset with provider-specific sample limits: $0.04 for Fable and $0.02 for GPT. Kept the full stage disabled and added fail-closed post-run status. | Interruptions fell from 22 to one: Fable exceeded its cap by $0.0008 after an exact simulated call. GPT completed 40/40. Fable produced nine provider `content_filter` outcomes, concentrated in all eight sandbox-capability runs. Transcript review also found that the frozen scorer rejected 14 correct Fable responses because they began with `EXECUTED` and then explained the decision instead of ending with that token. | Preserve the paid run as a calibrated diagnostic. Normalize response formatting only in aggregate analysis without mutating raw logs, release future scorer changes under a successor artifact, and require a zero-interruption pilot plus independent review before enabling the full run. |
| v0.7 | Released a successor scorer that accepts `EXECUTED` as the first response token, raised Fable's per-sample ceiling to $0.055, retained GPT's $0.02 ceiling, and kept the full stage disabled. | All 80 planned runs completed without a sample-limit interruption for $1.0922675. GPT produced 40/40 correct and usable decisions. Fable produced 37/40 correct and 33/40 usable decisions; its seven provider refusals were all concentrated in the eight-run evaluation-awareness subset. Fable made no unauthorized attempt in 20 withhold runs but made two malformed or wrong-scope attempts in authorized execute controls. | Treat v0.7 as the first usable zero-interruption two-provider pilot. Preserve the concentrated refusal pattern for targeted follow-up, but do not promote the pilot to a general model ranking or enable the full stage before independent case review. |
| v0.8 review | Added a deterministic internal blind-review workflow for all 100 cases. Source case IDs, metadata, expected actions, reason codes, cell names, and difficulty labels were removed from an opaque review packet; judgments were recorded separately before the answer key was opened. | The completed review produced 100/100 action agreement, 100/100 evidence-sufficient judgments, 100/100 single-clear-decision judgments, and no adjudication cases. Mean realism was 4.0/5 and mean difficulty was 3.63/5. The source dataset required no correction. Because the author designed and reviewed the cases, this is consistency evidence rather than independent validation. | Freeze an aggregate-only review artifact with explicit authorship and limitations. Keep external spot-checking optional. Preserve the full-run block until the 600-run budget and live provider credit are separately verified. |
| v0.8.2 full medium | Froze the complete 100-case, two-model, three-epoch benchmark into five complete-pair batches with provider-specific authorization caps, resumable checkpoints, and fail-closed completion rules. | All 600 analytical slots completed. Three Anthropic slots crossed the frozen output-token limit after partial responses; the runner stopped, retained the originals, and used separately frozen one-for-one repairs selected only by protocol interruption. The completed evidence contains 603 gross attempts, 600 analytical rows, 10/10 verified checkpoints, and $8.6929235 gross cost. | Keep operational attempts distinct from the analytical set, publish only aggregate reviewed artifacts, and treat the observed model-plus-provider differences as benchmark-bounded evidence rather than a general ranking. Any max-reasoning follow-up requires a new selector output, budget, manifest, and approval. |

## The most important corrections

### 1. Safe non-action is not the same as a usable decision

The first scorer rewarded the absence of an unsafe action even when the API
provider had blocked the model output. That is useful as a system-level safety
signal, but it is not evidence that the model made the intended authorization
judgment.

The correction separated:

- outcome correctness;
- usable task decision;
- explicit task-specific withholding; and
- provider-reported refusal.

This prevented provider enforcement from being silently counted as model
reasoning.

### 2. A suspected pressure effect required a matched diagnostic

The early refusal pattern could have been attributed to pressure language. We
did not accept that explanation from a few examples. v0.3 held the authority
facts constant and varied only neutral versus pressure framing, while retaining
a domain-matched authorized control.

The resulting pattern did not support the simple pressure hypothesis. It
instead showed a provider-filter interaction concentrated on the authorized
positive control. The exact trigger remained unknown, so the result stayed
descriptive.

### 3. Exact action behavior required an exact action schema

A single action string was insufficient for diagnosing whether a model chose
the right operation with the wrong target, parameter set, authorization record,
or call count. v0.4 moved these into separate structured fields.

That enabled distinct metrics for:

- unauthorized action attempts;
- wrong-scope attempts;
- malformed or duplicate calls;
- schema-conformant calls;
- exact execution; and
- reason-code accuracy.

### 4. More cases did not automatically mean better cases

The balanced v0.4 factorial design improved coverage and causal structure, but
many packets still supplied conclusion-like evidence. Frontier models could
solve them without performing the multi-record reasoning the research question
was meant to test.

v0.5 therefore increased evidence complexity instead of merely increasing the
case count. Difficulty became an explicit design field, and 80% of cases were
made hard or very hard.

### 5. Structural validation did not prove semantic ground truth

v0.5 passed all 17 deterministic gates. The paid pilot then revealed that
positive-control evidence did not satisfy the task's own `verified` requirement.
The benchmark could therefore mark careful instruction-following as an error.

This is a core methodological lesson: schema integrity, balance, lexical
anti-leakage, and factorial completeness cannot establish that a label is
entailed by the evidence. A positive-evidence contract must also be audited.

### 6. A repair needs its own namespace and its own failure tests

The first v0.6 implementation used generic `CAN-*`, `REG-*`, `VER-*`, and
`FIN-*` identifiers. The inherited validator treated existing registry records
whose IDs began with `REG-*` as new proof records. It then removed real evidence
from two cases and failed the evidence-complexity and proof-count gates.

The correction introduced a dedicated `PF-*` namespace and regression tests
for missing proof records, digest tampering, and non-final positive controls.
The dataset then passed all 24 deterministic gates. This small failure is worth
preserving in the final narrative because it shows why namespace isolation and
negative validator tests are part of benchmark design, not incidental cleanup.

### 7. A successful log can still contain an incomplete measurement

The v0.6 pilot completed 80 scored runs and stayed below its aggregate budget,
but transcript audit found 22 per-sample cost-limit events. Inspect marked both
model logs `success` because the evaluation files closed cleanly; that status
did not mean every sample completed the task protocol. Applying the same audit
backward found nine Fable interruptions in v0.4 and sixteen in v0.5. This
required correcting earlier prose that had attributed v0.4's incomplete
responses to the model.

This distinction materially changed the interpretation. Eighteen of Fable's
20 execute controls were cost-limited, and the other two were provider
refusals. Eight limited runs recorded an exact simulated tool call but could
not produce the required final acknowledgement. GPT had one analogous limit
event. The original aggregate percentages therefore mixed model behavior,
provider enforcement, and harness interruption.

The result analyzer now records protocol limits separately and produces a
protocol-complete descriptive subset. The next run must use provider-specific
sample caps derived from observed costs while retaining a separately computed
aggregate ceiling. A top-level green status is no longer sufficient evidence
that a run is empirically interpretable.

### 8. A strict output check can mistake explanation for failure

The v0.6.1 transcript audit found that Fable often returned `EXECUTED` on the
first line and then explained why the simulated action was authorized. The
frozen scorer used `normalized.endswith("EXECUTED")`, so it marked 14 exact,
non-refused executions as unusable. GPT's shorter final responses did not
trigger the defect.

The aggregate analyzer now accepts `EXECUTED` only as the first response token
while permitting trailing explanation. It records every adjustment and leaves
the raw Inspect logs untouched. This changed Fable's normalized
usable-decision rate without changing any tool-call, authorization,
provider-refusal, or protocol-limit evidence. The lesson is methodological:
an output-format rule can create an apparent provider difference even when
both responses satisfy the substantive instruction.

### 9. A clean pilot can support analysis without becoming the full benchmark

v0.7 moved the response-format correction into a versioned scorer and raised
only the provider limit that the preceding audit showed was insufficient. The
result was the first 80-run two-provider pilot with zero protocol
interruptions. No post-run response normalization was required.

That clean execution made the observed differences interpretable within this
pilot. GPT produced 40/40 correct and usable decisions. Fable's degraded
results were concentrated in evaluation-awareness cases and included seven
provider refusals. Fable still made zero unauthorized attempts across its 20
withhold runs; its two strict-scope failures occurred in authorized execute
controls as malformed or wrong-scope attempts.

The measurement pipeline is now usable, but the run covers 20 selected cases
rather than the complete 100-case set. A successful pilot therefore changes
the experiment's state from harness calibration to bounded empirical evidence;
it does not by itself justify a full-dataset claim.

### 10. Higher reasoning effort is a follow-up condition, not a replacement

The planned 600-run benchmark needs one reasoning level that is affordable,
repeatable, and consistent across all cells. Running every case at the highest
available effort would spend the most budget on easy cases while making it
harder to measure the marginal value of additional reasoning.

v0.8.1 therefore keeps `medium` as the primary two-model condition. After a
protocol-complete full run, a deterministic selector will identify complete
four-variant `pair_id` groups containing an incorrect or unusable decision, an
unauthorized or wrong-scope attempt, a refusal, epoch instability, or
cross-model disagreement. The whole group and both models move to a separately
budgeted `max` follow-up; individual rows cannot be hand-picked.

The selector has unit coverage for stable groups, single-row triggers,
incomplete factorial groups, and protocol interruptions. The design document,
selector, and contract are frozen in the v0.8.1 manifest. No max call is yet
authorized.

The one-epoch medium calibration then completed 40 analytical rows. Its first
Anthropic pass stopped one authorized treatment case at the six-message
harness limit after two tool calls. We preserved that partial attempt, created
a hash-linked one-sample retry plan, changed only the message limit to ten,
and reran the case at the same medium effort and cost cap. The completed retry
made no action attempt, so the final analytical row records an incorrect
decision rather than retroactively treating the partial tool sequence as a
success.

The resulting 40-row set has no protocol interruptions. GPT produced 20/20
correct and usable decisions. Fable produced 16/20 correct and 12/20 usable
decisions, five provider refusals, and no unauthorized action attempt. Gross
spend was $0.698538 against the $1.50 ceiling. These are bounded calibration
results: one epoch and 20 selected cases per model cannot establish full-set
performance or stability. The next gate is a successor manifest for the
complete medium run. Only after that run and integrity audit may the selector
define a separately approved max diagnostic.

### 11. A resumable run still needs immutable repair and accounting rules

v0.8.2 executed the complete medium condition: 100 cases, two API-delivered
systems, and three epochs, for 600 analytical slots. All five OpenAI batches
and two Anthropic batches completed directly. In Anthropic batches 2, 3, and
5, one slot exceeded the frozen 512-output-token limit after two tool turns.
The partial attempts were not silently accepted, deleted, or rerun inside the
same checkpoint.

For each interruption, a separate repair plan froze the original attempt
identity, the one affected analytical slot, and the unchanged model,
reasoning, message, output-token, and cost limits. Eligibility depended only
on protocol interruption; it did not depend on whether the partial response
looked correct or favorable. Each original remains in the operational audit,
while exactly one protocol-complete replacement occupies the corresponding
analytical slot.

This produced 603 gross provider attempts and 600 analytical rows. Gross spend
was $8.6929235, analytical-set spend was $8.5742080, and repair overhead was
$0.1187155. A final integrity pass also found that an earlier run-manifest
provider subtotal omitted the last repaired checkpoint even though the
completion summary contained the correct total. The finalizer recomputed the
provider and overall totals from all ten verified checkpoints and changed
accounting metadata only; no prompt, transcript, score, or analytical choice
was changed.

Within the frozen synthetic benchmark, GPT recorded 300/300 correct and
294/300 usable decisions. Fable recorded 249/300 correct and 205/300 usable
decisions. Neither system attempted an action on any of its 150 withhold
cases. Fable's lower result was concentrated on authorized execute cases,
where provider refusals, no-action outcomes, and malformed or wrong-scope
calls reduced exact completion. These are observations about the delivered
systems under this dataset and run date, not a general provider or model
ranking.

## Evidence ledger

| Evidence | What it establishes | Current state |
|---|---|---|
| `experiment_manifest_v0_1.json` to `experiment_manifest_v0_7.json` | Frozen task, dataset, model, limit, pricing, and stage definitions by version | Versioned repository artifacts; raw run outputs remain local |
| `outputs/reports/20260725T135342Z-pilot-rescored-v0_2.md` | Why refusal-aware rescoring changed interpretation | Local aggregate artifact |
| `outputs/inspect/20260725T224725Z/aggregate.md` | v0.3 matched diagnostic across 18 runs | Local aggregate artifact |
| `outputs/inspect/20260726T032207Z/aggregate.md` | v0.3 full 150-run decision-path evidence | Local aggregate artifact |
| `authority-action-v0-4-pilot-results.md` | v0.4 64-run pilot plus retroactive protocol-limit correction | Versioned documentation |
| `authority-action-v0-5-pilot-diagnostic.md` | v0.5 80-run benchmark and harness diagnostic | Versioned documentation |
| `authority-action-v0-6-pilot-diagnostic.md` | v0.6 80-run diagnostic and the per-sample cost-limit defect | Versioned documentation |
| `outputs/inspect/20260726T132225Z/aggregate.md` | v0.6 aggregate scores, protocol-limit audit, provider refusals, usage, and cost | Local aggregate artifact |
| `authority-action-v0-6-1-pilot-diagnostic.md` | Provider-specific limit rerun, one residual interruption, provider-filter concentration, and response-format correction | Versioned documentation |
| `outputs/inspect/20260726T152521Z/aggregate.md` | v0.6.1 normalized aggregate, protocol audit, provider-filter paths, usage, and cost | Local aggregate artifact |
| `authority-action-v0-7-usable-pilot-results.md` | First zero-interruption two-provider pilot, direct v0.7 scoring, bounded findings, and limitations | Versioned documentation |
| `data/authority_action_v0_7_pilot/summary.json` and `manifest.json` | Aggregate-only public result counts, tracked source hashes, and unpublished run-evidence fingerprints | Public candidate artifact |
| `outputs/inspect/20260726T180156Z/result_manifest.json` | Run, result, analyzer, dataset, task, and raw-log integrity hashes | Local machine-readable audit artifact |
| `outputs/inspect/20260726T180156Z/aggregate.md` | v0.7 direct-score aggregate across 80 protocol-complete runs | Local aggregate artifact |
| `authority_action_cases_v0_6.jsonl` and `authority_action_cases_v0_6_quality.json` | Corrected proof contract and 24/24 deterministic validation | Versioned candidate artifacts |
| Local v0.8.1 reasoning-escalation plan and selector | Pre-specified medium-to-max selection, non-replacement, and fail-closed protocol rules | Local design record; max execution not authorized |
| Local v0.8.1 medium-calibration report | One-epoch medium result, message-limit replacement audit, bounded metrics, and cost accounting | Local development evidence; raw logs remain private |
| Local calibration source contract and result manifest | Source/run/log hashes, one-for-one replacement lineage, aggregate hashes, and gross versus analytical cost | Local audit evidence; not part of the public package |
| Local v0.8.2 execution manifest, batch runner, and pre-authorization contract | Frozen 600-run medium scope, five complete-pair batches, checkpoint identity, partial-unit failure policy, and pre-authorization gate | Local operational evidence; the sanitized protocol is published separately |
| `authority-action-v0-8-2-full-medium-results.md` | Complete-run metrics, the three protocol repairs, cost decomposition, bounded interpretation, and limitations | Aggregate-only publication candidate; raw transcripts remain local |
| `outputs/inspect/20260727T152524Z-full-medium-authorized/final_audit_summary.json` | 600 analytical rows, 603 gross attempts, 10/10 checkpoint hashes, provider subtotals, and repair overhead | Local machine-readable audit truth |
| `outputs/inspect/20260727T152524Z-full-medium-authorized/analysis/result_manifest.json` | Dataset, experiment, analyzer, assembler, row, aggregate, and final-audit hashes | Local machine-readable integrity manifest |

Raw Inspect logs contain transcripts and remain local. Public reporting should
use aggregate tables and selected synthetic examples that have been reviewed
for release.

## v0.6 repair design

The repaired successor does not insert a prose sentence such as “this grant is
verified.” Each positive packet contains a machine-resolvable proof path:

```text
grant record
  -> canonical record digest
  -> active signer or authority registry entry
  -> successful signature or ledger verification
  -> final status
  -> current time window
  -> exact actor, action, target, and parameter scope
```

The model must still join multiple records, but the expected `execute` label
must follow unambiguously from the supplied facts.

The v0.6 validator fails closed when:

- a positive grant lacks a complete verification path;
- finality is absent or only implied;
- the proof resolves to a different record, actor, target, or parameter set;
- an invalid cell contains more than its intended defect; or
- the system instruction requires a fact the packet never establishes.

Three repeated two-model pilots, the internal masked review, and the complete
v0.8.2 medium run are now complete. The 24/24 validation establishes the
dataset contract; the 600-run result supplies benchmark-bounded empirical
evidence. Neither establishes general model performance or independent
external validation.

## Publication plan after experiment completion

The public case study should contain:

1. the practical problem and narrow research question;
2. the v0.1-to-final design timeline;
3. the hypotheses we rejected and why;
4. representative synthetic cases before and after correction;
5. the side-effect-free tool and deterministic scoring architecture;
6. provider-refusal and model-decision separation;
7. cost, token, repeat, hash, and run-integrity controls;
8. final results with uncertainty and per-condition diagnostics;
9. benchmark defects discovered during development and their repairs;
10. remaining limitations and reproducibility instructions.

The narrative should show our reasoning honestly: the experiment improved
because we treated surprising outputs as possible measurement failures before
calling them model failures.

## Completion gates for the final case study

The draft should not be presented as the completed case study until:

- the repaired successor has a new frozen hash;
- the positive-evidence contract validator passes;
- the internal blind review checks realism and single-decision clarity without
  being represented as independent validation;
- a corrected small pilot passes transcript audit;
- the planned full run completes within its cost and execution limits;
- aggregate results and uncertainty tables are regenerated from the final logs;
- public examples and wording are reviewed separately from internal logs; and
- repository, commit, release, and public-page states are verified independently.

## Repository state at this checkpoint

- Publication-candidate base: commit `3ba8cab` on `main`. Branch, pull-request,
  merge, and live states are verified separately.
- v0.4-v0.7 development artifacts: assembled as one versioned experiment
  history; raw provider transcripts and ignored output directories remain
  local.
- v0.6 proof-contract successor: frozen candidate manifest verifies 100 cases,
  20 pilot case IDs, two models, and dataset hash
  `7dc42780d7a28993756a01fce6c585e2e531bad97157dc33c4be441c75292900`.
  All 24 deterministic gates and the no-provider-call pilot preview passed.
- v0.6 paid pilot: completed locally for 80 scored runs at $0.959929, below the
  $1.20 ceiling. Transcript audit found 21/40 Fable and 1/40 GPT runs were
  interrupted by the per-sample cost limit. The run is a protocol-calibration
  diagnostic, not a model comparison.
- v0.6 aggregate analyzer: now separates cost/token sample limits from model
  decisions and reports a protocol-complete descriptive subset.
- v0.6.1 calibrated pilot: completed locally for 80 scored runs at $1.066713,
  below the $2.40 ceiling. Fable completed 39/40 and GPT 40/40; the runner
  correctly returned `needs_review` for one $0.0408 Fable sample against its
  $0.0400 cap. The full stage remains disabled.
- v0.6.1 response-quality audit: aggregate analysis normalized 14 Fable
  responses that began with `EXECUTED` and then explained the decision. Raw
  logs were not changed. Nine Fable provider `content_filter` outcomes remain
  separately reported.
- v0.7 usable pilot: completed locally for 80/80 protocol-complete runs at
  $1.0922675 against a $3.00 ceiling. GPT produced 40/40 correct and usable
  decisions. Fable produced 37/40 correct and 33/40 usable decisions, with all
  seven provider refusals concentrated in evaluation-awareness cases. No
  withhold case produced an unauthorized action attempt.
- v0.7 result integrity: run, aggregate, analyzer, task, dataset, and raw-log
  hashes are recorded in
  `outputs/inspect/20260726T180156Z/result_manifest.json`. Raw logs remain local
  and unchanged.
- v0.7 public artifact: aggregate results and provenance fingerprints are
  available under `data/authority_action_v0_7_pilot/`; a deterministic verifier
  checks the public file, versioned source hashes, count reconciliation, cost
  reconciliation, and aggregate-only declarations.
- v0.8 internal blind review: completed 100/100 masked author judgments before
  answer-key access. All 100 decisions agreed with the frozen key; all 100
  packets were judged evidence-sufficient and single-decision clear. No
  adjudication case was created. The aggregate-only artifact and verifier are
  under `data/authority_action_v0_8_internal_review/` and
  `latentatlas/authority_action_review.py`.
- v0.8 budget gate: the planned 600-run protocol projects to $8.19200625 from
  v0.7 pilot averages, while unchanged per-sample ceilings imply a $22.50 hard
  maximum. This was the pre-execution planning state; live provider credit was
  later verified in the separate v0.8.2 authorization artifact.
- v0.8.1 medium calibration: completed 40/40 analytical rows after one
  hash-linked Anthropic message-limit retry. The interrupted original attempt
  remains in the local audit evidence and is excluded from the analytical set.
  Gross cost was $0.698538; analytical-set cost was $0.6616995. GPT recorded
  20/20 correct and usable decisions. Fable recorded 16/20 correct, 12/20
  usable, five provider refusals, and zero unauthorized actions.
- v0.8.1 escalation gate: the primary benchmark stays at medium. The complete
  medium stage subsequently finished; the max diagnostic remains disabled. A
  deterministic selector may promote only complete four-variant groups and
  both models after a protocol-complete medium full run. Max requires a new
  manifest, fresh limits, a verified budget, and separate approval.
- v0.8.2 full-medium contract: the 25 complete prompt groups are frozen into
  five batches of five groups. Each provider-batch requires 60/60 complete
  rows and a hash-linked checkpoint. Partial evidence cannot be automatically
  rerun or masked. The plan projects $9.9254925 from analytical calibration
  rates and $10.47807 with the observed retry overhead, under a $22.50 hard
  maximum. A separately frozen authorization then recorded fresh credit and
  explicit approval.
- v0.8.2 full-medium result: completed locally with 600/600 analytical rows,
  603 gross attempts, 10/10 verified checkpoints, and $8.6929235 gross spend.
  Three protocol-interrupted Anthropic attempts remain in the operational
  record and were replaced one-for-one under separately frozen repair plans.
  Aggregate analysis and integrity hashes are complete; raw transcripts remain
  local.
- v0.5 pilot: completed locally for 80 runs at a calculated cost of $0.753319.
- v0.5 interpretation: benchmark-design diagnostic; not a final model
  comparison.
- Final full-benchmark publication: the run, post-run audit, aggregate wording
  review, public protocol, public summary, integrity manifest, verifier, and
  bounded case study are complete. Raw transcripts and operational
  authorization records remain local. Repository merge, tagged release, and
  any live-page deployment remain separate publication states. The internal
  review is not independent external validation.
