# F07 cancellation-target preflight v01

## Question and status

After the pinned source stop has already interrupted O and launched stop-summary S,
does an additional interrupt of the same saved O run change the measured lifecycle
and file outcomes? What happens if the active thread targets are instead refreshed?

This is a local component preflight and original-arm mapping, not the complete
F07 experiment. The original eight arms and G01–G10 remain in the design card.
No provider calls, live-model behavior samples, external Slack deliveries or
publication are part of this step.

## Fixed local matrix

Eight conditions: four arms × two independent-I first-mutation admission phases.
The development input is 17; every condition starts a fresh process on this host.

| Arm | Source stop | Additional action |
| --- | --- | --- |
| healthy | None | None |
| source_baseline | Actual pinned handler | Observe O/S state only |
| source_plus_exact_cancel | Actual pinned handler | Repeat its saved O thread/run target with interrupt |
| source_plus_refresh_probe | Actual pinned handler | Re-run the source active-run lookup, then interrupt its current targets |

At the probe checkpoint O's final mutation has been accepted and is held before
the native write; O's graph is terminal; S has been factory-bound and is held
before its first programmed response. I's first partial mutation is either not yet
admitted or accepted/waiting. N (fresh human authority in the same thread) and C
(programmed continuation with old authority) start later. Only one native effect
order, O-first, is used: two admission phases are not two effect orders.

The source pin is e0d9aff59925a4da55ec8d6c31fa723651c24909. Source stop, SDK
cancel implementation and original card hashes are bound in PLAN.json. Native
effects use the previous research-owned FIFO and native FilesystemBackend adapter.
Their relation to the original executor topology is recorded as an open binding.

## Evidence and comparison rules

- Copy the original source HTTP cancellation target and action, not an inferred ID.
  Every selected ID must resolve to an actual accepted O or S run.
- An empty active target list sends no cancel request: the SDK otherwise omits an
  empty run_ids field, potentially changing the request's scope.
- Record raw HTTP status/body and before/after run state separately from caller and
  file effect state. HTTP rejection is an outcome; this fixture records it and
  continues. Uncaught-rejection handling is not tested.
- Keep the original source handler's completion distinct from S's own terminal
  status and emitted summary. Source dispatch completion does not mean S finished.
- Compare saved-target outcomes with baseline: old graph state, native pending
  state, old-root effects, final bytes, S output and N/I/C. Equal projections never
  imply full API/protocol equivalence.
- Refreshing targets after S dispatch is a different operation if the target set
  changes. Do not deduplicate it as the original CANCEL component.
- The generic auditor validates identities, receipts, chronology, closure and
  bytes. Expected programmed outcomes belong only to qualification tests.
- All callers/consumer are joined; prior evidence and smoke snapshots remain
  immutable. Native file attempt/result bound an effect; no physical-commit or
  provider-side quiescence claim is inferred.

## Development observations already known before this matrix

local-smoke-v01 observed HTTP404 for the same saved O ID, with S completing and
the pending native O write later completing. local-smoke-v02 observed HTTP204
after refreshed targets selected S; S was interrupted while O's native write still
completed. These observations motivated this fixed qualification and are not
hidden or described as an unseen preregistered test. v01's source snapshot predates
the added explicit S-hold score witness; its original files remain unchanged.

## Recompute

Use the existing admission_probe virtual environment's Python. From this directory:

```sh
../../../admission_probe/.venv/bin/python -B qualify.py
../../../admission_probe/.venv/bin/python -B crosscheck_cancel.py
../../../admission_probe/.venv/bin/python -B bind_arms.py
../../../admission_probe/.venv/bin/python -B verify_all.py
```

Saved qualification/crosscheck/binding records are created once with --write.
A new native run requires a new local-* output directory via run_local.py --out.
The selected fixed matrix is local-matrix-v01. Verification never repeats native
episodes and never calls a provider.

The separate standard-library crosscheck imports neither the harness nor scorer;
it is an additional code path, not an independent human review. See RESULT_TR.md
for observations and F07_ARM_BINDING.json for exact original-arm gaps.

