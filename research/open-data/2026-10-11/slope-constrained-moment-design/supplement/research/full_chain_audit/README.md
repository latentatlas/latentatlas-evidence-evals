# R01–R12 audit only

21 September 2026. This folder records a comprehensive recheck requested
by the user. It is not a new scientific result package. Start with the
Turkish [audit report](DENETIM_RAPORU.md) and
[83-item claim inventory](IDDIA_ENVANTERI.md).

The audit found no error requiring withdrawal or numerical alteration of
the existing scoped results. This is an internal audit, not an external
expert report, a proof-assistant verification or a literature-priority
claim. Shared arithmetic/integration dependencies remain a trust boundary.

## Evidence

- [34 existing checker/test/crosscheck reruns](replays/status.json).
- [27 certificate/moment regeneration jobs](regenerations/status.json).
- [An additional R01 higher-precision generation](precision_comparison.json).
- [84 main JSON comparisons](regeneration_comparison.json), plus the
  precision comparison: 85 comparisons and 201023 identical dyadic balls.
- [32 exact symbolic identities](symbolic_checks.json).
- [R12 fresh input and smooth-transition audit](threshold_input_audit.json).
- [Analytic reasoning audit](ANALITIK_DENETIM.md).
- [Targeted primary-source checks](KAYNAK_DENETIMI.md).
- [One resolved new audit-implementation comparison issue](diagnostics/threshold_input_envelope_comparison.json).

All existing source/result files are frozen. Production jobs ran in
disposable complete copies; only the extra R01 precision run used the
original read-only source with an explicit output in this audit folder.
Temporary copies were removed. No new cache is part of this folder.
The old manuscript is preserved but is outside the current proof chain.

## Read-only audit verification

From the workspace root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/full_chain_audit/audit_snapshot.py
```

This checks source identities, frozen inputs, evidence links, claimed
counts and the audit manifest. It is a provenance/closure check, not a
rerun of every mathematical calculation. A successful report must not
be described as another independent mathematical proof.

For a complete calculation rerun, use a separate copy of the workspace
with the same Python environment. Existing job directories intentionally
cannot be overwritten. In that separate copy, start with empty
`full_chain_audit/replays/` and `full_chain_audit/regenerations/` output
directories while retaining the audit source programs; run:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/full_chain_audit/replay_checks.py --workers 3
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/full_chain_audit/replay_checks.py --generators --phase regenerations --workers 3
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/full_chain_audit/compare_replays.py
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_verified/certify_cusp.py --family quartic --dps 130 --terms 20 --pieces 16 --output research/full_chain_audit/quartic_precision_replay.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/full_chain_audit/check_precision_replay.py
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/full_chain_audit/check_symbolic_identities.py
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/full_chain_audit/check_threshold_inputs.py
```

The thread pool executes separate processes/copies, not shared-precision
Arb computations inside a common Python process. The 34 reruns use the
frozen canonical inputs. Each mathematical regenerated output is compared
separately to its frozen counterpart. Timing and source-provenance metadata
may differ legitimately; interval endpoints happened to match exactly in
this run. Approximate optimizer probes and plot renderers are not used as
proof and were not part of the certificate regeneration count.

The supplemental R12 computation rewrites the integrand, uses 140 decimal
digits and 12 theta terms, recomputes all nine sign moments, and evaluates
smooth corrections in the scaled variable v=(u−b)/η. It retains the
original upper budget rather than promoting a new tighter theorem.
It does not import the research computation modules, but still relies on
Arb and on separately replayed exact-Q and correction-matrix inputs.
