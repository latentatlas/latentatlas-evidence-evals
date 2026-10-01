# Stop contracts: completion study protocol

13 September 2026. Written before this stage's experiments. Builds on, but does not overwrite, admission/intervention/commit exploratory records. This is a bounded local systems case study, not a novel cancellation protocol, adversarial-model benchmark, production vulnerability, or reconstruction of the OpenAI–Hugging Face incident.

## Questions and outcome-independent completion criteria

RQ1: Which stop contract does immediate coroutine cancellation, worker drain, or local origin-scoped effect checking satisfy under the same schedule?
RQ2: Can a restricted existing-summary path preserve verified prior information while old native effects and completion-originated writes are treated separately from new human-authorized work?
RQ3: What observed waiting, output loss, mistaken blocking, retry/delivery state and extra control state accompany these choices?

Successful research is valid evidence for any outcome, including a valid intervention failure. Do not condition inclusion on the scoped arm winning. Evidence validity (identity, byte integrity, schedule prerequisites, observation completeness) and contract verdicts (pass/fail/unknown/not applicable) are separate outputs. Preserve invalid development runs with reasons; never add them as confirming replications.

## Contracts

R: no old final effect after the operator's stop request. This is deliberately stronger than mere cancellation, and is not promised by every arm.
V: no old-origin native write started after effective scope withdrawal. Withdrawal linearizes under the same per-origin lock as the scope check/native write. A write holding the lock first may finish before withdrawal, even after the stop request. This is not physical rollback or instantaneous stop.
C: no late old native effect after a declared worker-quiescent stop confirmation. Confirmation must identify what it covers; a coroutine cancellation ACK alone is not worker quiescence. A timeout yields pending/unknown, never successful completion.
F: permission to report genuinely available old evidence is separate from permission to write new old-origin artifacts. New human, new human-origin completion, and independently authorized tasks should remain usable within the tested adapter's origin model.

Monotonic milestones: operator request, cancel API request/ACK, actual coroutine cancellation, API interrupted observation, withdrawal requested/effective, worker completion, restricted-summary terminal response, explicit study stop confirmation. Milestones are not interchangeable. "Commit" is local native open/write/close visibility, not fsync/crash durability/distributed atomicity.

## Comparison

Four arms use identical pinned source factory, real local Agent Server and workload:

- `cancel_summary`: source stop+summary and existing-summary routing for old completion. No enforced origin revocation; record withdrawal in shadow for paired observations.
- `drain_summary`: same, but study worker-quiescent confirmation waits for the initial native worker. This is an explicit local lifecycle adapter, not a claim that upstream emits this confirmation. The fair alternative can finish old writes before confirming stop.
- `scoped_summary`: same source stop+summary, local trusted-origin check immediately before native writes, and restricted old-completion summary routing.
- `scoped_no_summary`: same scoped check, but leave old completion's offered tools unrestricted. This ablation separates presentation from enforcement. No hidden tool is forced; selection remains limited to offered tools.

Core schedule matrix: four arms × three schedules (`accepted_precommit`, `after_commit`, `unheld`) × two fixed data seeds (17,41): 24 cells. Reverse arm order on the second seed. Two additional `drain_summary/drain_timeout` cells exercise pending rather than false success. Fresh child process/server per cell. Frozen canonical plan precedes execution; development probes remain separate.

`accepted_precommit`: initial final-report native worker entered and held before lock/check/write. After actual coroutine cancellation, a controller independent of the compared stop-confirmation routine releases the same barrier. `after_commit`: final file already written, worker held before return; this is not a prevention failure for V. `unheld`: no write barrier, stop triggered on observed final-worker entry; actual order is measured, never assumed or converted to a natural-world frequency estimate. `drain_timeout`: a bounded controller delay exceeds the declared drain deadline, then releases and cleans up; timeout is an observed lifecycle outcome, not fixture timeout.

Do not hold a scheduling gate inside the revocation/write lock. Use per-origin locks and measure acquisition waiting. The scope-control unit suite also exercises write-first/revoke-first ordering, same-thread wrong-caller identity, unknown origin, and independent work. An ordinary drain cleanup after measurement is required for every arm, but does not retroactively upgrade an earlier confirmation.

## Workload and integration

A deterministic small incident-log task uses 24 synthetic timestamped authentication/egress records. Read through the real read_file tool, compute evidence-linked metrics, write a partial report for the first half, then a final report. The initial final write is the schedule target; the partial must already be native and verifiable. A summary identifies available partial/final artifacts by actual read results, never treats cancelled ToolMessage success status as file proof. No money, scientific research value, or unobserved incident harm is inferred.

The same integrated workflow includes initial stop/source summary, a concurrent independent legitimate task, old completion notification, duplicate monitor tick, new explicit human task in the same thread, that new task's completion, and another old-notification delivery attempt. Every call is linked to its actual admitted run. Use the source monitor/dispatch/delivery protocol with an explicit synthetic task-provider seam. Bind task origin at controlled task creation and validate it at delivery; do not infer origin from current thread stop state or latest human message. This is a local origin registry, not authenticated deployment ingress or durable multi-agent lineage.

Caller identity must be obtained from the live runtime configuration at the tool boundary, corroborated against the actual factory admission, and propagated to the native thread independently of model-supplied filepath. A same-thread other-invocation pathname is a mismatch, not a grant. Scope is attributed to the registered origin, while the native artifact and terminal response retain their actual caller run.

Measure separately: correct available analysis, observed partial/final files, old-origin late effects, new-work results/files, false blocks, controller-induced waiting, observed stop-confirmation time, worker drain time, new-work latency, delivery/retry counts, state objects. Controlled waits are not production overhead. Unheld traces are descriptive case observations, not percentile or safety-probability estimates. Do not collapse these into an arbitrarily weighted net-benefit score.

## Validity, reproduction and boundaries

Pure-stdlib auditor independently reads raw HTTP bytes/hashes, actual admission/factory/tool identities, native worker events, file bytes, immediate run-specific terminal responses and final inventories after workers finish. It must accept a well-recorded counterexample as evidence-valid while marking its contract failed. Missing evidence gives unknown/invalid, never implicit success.

Pin/snapshot new instrumentation, preserved fixture dependencies, 427 upstream files and native backend implementation. Never modify an earlier stage to fit a desired result. Root parent sanitizes environment; child denies external sockets, arbitrary subprocesses and credentialed requests. Local in-process ASGI only; no real LLM API/private data/paid cloud resources/public message/submission.

Reproduction target: fresh environment installation from exact retained dependency versions and fresh full matrix/QA/report, not merely re-auditing v01. The pinned source requires Python >=3.14; its known explicit E2B override conflicts and PydanticV1 warning must remain disclosed or be studied as a separate declared sensitivity environment. A second local environment is not an independent operator/machine review. Preserve both claims accurately.

Close the six scoped gaps with artifacts: contribution/prior-art table; declared stop contracts and strong drain comparison; runtime-bound identity; integrated origin/retry controls; evidence-linked useful task and measured cost vector; separated validation/outcomes plus clean replication. If a criterion is not met, record an open limitation and do not mark it closed. Restart/durable revocation, remote effects, actual LLM behavior, second framework and independent human review are follow-up scope, not silently achieved deliverables.
