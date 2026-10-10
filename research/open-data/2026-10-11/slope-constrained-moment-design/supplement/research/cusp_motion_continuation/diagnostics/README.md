# R29 — Attempts and corrections

`probe_wide.json` is the first successful recentered derivative attempt,
center −1/4096, half-width 1/4096. Its anchor is `anchor_probe.json`.
The derivative lower bound is positive on [−1/2048,0], already 32 times
longer than R28's range.

`probe_coarse.json` uses center −1/1024, half-width 1/1024, with anchor
`anchor_coarse.json`. The dual contraction passes, but the resulting
C₄' interval includes zero. Its status is `derivative_sign_unresolved`,
not a negative derivative or a failed mathematical hypothesis. The first
four final cells cover this exact same [−1/512,0] interval and prove
positive derivative. No unsuccessful run was relabeled successful.

`continuation_probe_version.py` and `differentiate_probe_version.py` are
the source versions that generated those attempts. The production source
adds an explicit three-switch rank check for the R23 interpretation;
the probe equations and tolerances were not weakened. These snapshots
are retained for source inspection, not as standalone entry points.

The first rational checker stopped on an API error: the inherited RI
class has no `contains` method. `check_bounds_before_interval_api_fix.py`
and `rational_interval_api_failure.json` retain this error and its exact
source identity. Testing the rational endpoints on one side of zero
replaced that call. No mathematical acceptance threshold changed.
`rational_run.log` records the successful 32-cell pass.

`direct_run.log` records the independent original-integral solves.
The first complete audit additionally assumed every recursive sign-cover
endpoint had radius zero. Arb subdivision sometimes stores an endpoint
as a narrow ball. `audit_before_endpoint_interval_fix.py` and the
`endpoint_interval_audit_failure` JSON/log retain this failed assumption.
The corrected audit checks coverage using each leaf's outer endpoint
intervals and overlap, justified by the leaf's actual evaluation ball.
All cells have no gaps. The producer and numerical thresholds are unchanged.
Neither that log nor the coarse probe is a substitute for the final
certificate and analytic proof. A figure revision removed interval-midpoint
markers so that orange diagnostic points cannot be confused with bar centers.

[Current evidence index](../results/cover/certificate.json),
[scope](../REVIEW.md), [reproduction](../README.md).
