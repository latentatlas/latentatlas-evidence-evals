# Scoped drain and evidence-bound confirmation — role_queue_v05

Question: what inventory and receipts justify a scoped stop confirmation, and can an incorrect confirmation be detected even when no late file appears?

This provider-free component qualification uses the real pinned local Open-SWE factory, Agent Server, Store, source Slack stop handler and native files. Actor choices are programmed. It continues the infrastructure stop-scope study.

## Frozen comparison

Sixteen fixed conditions: create profile, development input 17, eight controls and two phases of I's first mutation admission. The old O final-write candidate is accepted and held before native effect. Independent I's first partial-write candidate is either proposed but unadmitted, or accepted and waiting in the same FIFO.

The controls are defined exactly in contract.py: healthy, source only, source with immediate confirmation check, source with scoped drain and snapshot claim, receiver with immediate check, receiver with drain and file-effect closure claim, deliberate early confirmation, and deliberate omission of the live old worker from the producer inventory. The receiver arms check O-root authority at admission and native effect under one shared lock.

Experimental DRAIN and confirmation are separate from source-cancel acknowledgement and final cleanup. Source/S finish while the O native caller is still pending. DRAIN starts before releasing O. An additional fixture-only hold keeps I's first native effect unfinished until experimental assessment ends; in the pre-admission phase its admission is also held until then. This hold is a timing fixture, not a safety control.

## Two claim scopes

- **snapshot_quiescent:** the old-root mutation callers registered through the recorded inventory have finished. This does not close later admissions.
- **file_effects_closed:** snapshot quiescence plus O-root admission and effect gates, for write_file/edit_file through measurement_closed while policy remains unchanged.

Each inventory has a root, service, monotonic version, unique ID, member IDs, states and content hash. DRAIN resnapshots after waiting and includes old-root arrivals during the wait. Final membership check and receipt use the registration lock; confirmation takes a fresh atomic inventory. No waiter holds these locks while sleeping.

Independent replay reconstructs membership from native_worker_entered/finished, not the producer inventory. It scores missing members, live callers, claims, and later native effects separately. A false claim with intact underlying records is valid evidence of failed confirmation. Missing raw receipts or broken identity/hash/byte chains invalidate evidence.

## Preserved work and measurement

O/I/N/C share the frozen read_file, write_file, edit_file surface; S uses read_file and local slack_thread_reply. Later N has fresh fixture-human authority in O's thread; later C retains O authority and is explicitly programmed. N and I finals are checked against the same-phase healthy reference. Later C effects are reported but do not retroactively invalidate a claim limited to earlier snapshot members.

Native effect intervals are bounded by recorded attempt/result; these are not physical commit or crash-durability measurements. Scope is one trusted local process and native file service, not reads, internal computation, distributed descendants, real timers or provider state. These fixed conditions are instrument qualifications, not behavior prevalence estimates or 286-case completion.

## Reproduction and preservation

Use ../../../admission_probe/.venv/bin/python with -B:

- run_local.py --out local-NEW: new provider-free matrix; never overwrite output.
- run_tests.py: controller, mutation, scoped wait and raw-record negative tests.
- qualify.py: replay the selected local-matrix-v01 and healthy references.
- crosscheck_confirmation.py: separate stdlib-only lifecycle, claim and disk replay.
- verify_all.py: all checks plus preserved predecessor regressions.

Source/protocol files are hashed and copied before each run. Five initial smoke conditions are retained separately. Before the selected matrix, code review tightened the final drain inventory/receipt into one registration-lock boundary, and the new-member unit test explicitly waits for the initial inventory before adding C. Smoke records were not overwritten or pooled. No provider calls, publication or external delivery occurs.

Original core-card arm equivalence and G01–G10 bindings remain separate obligations. Findings and coverage progress are recorded after verification in RESULT_TR.md and CORE_BINDING_PROGRESS.json.
