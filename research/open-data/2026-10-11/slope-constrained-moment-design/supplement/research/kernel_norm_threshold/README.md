# R12 — Certified near-minimum kernel change

21 September 2026. This package answers the numerical continuation of
R11's fixed-Q relative-norm problem. Start with the Turkish
[research note](ARASTIRMA_NOTU.md) or the detailed [proof](PROOF.md).
The exact theorem fragment is in [THEOREM_APPENDIX.tex](THEOREM_APPENDIX.tex).

The common certified bracket is

`0.00000000091787079603827 < delta_star < 0.00000000091787079608363`.

Its relative gap is below `5e-11`. The lower bound applies to every
real bounded measurable multiplier satisfying the four fixed-Q moment
constraints. The upper bound is realized within that budget by an
explicitly defined even real-analytic multiplier with positive kernel,
exact order four and rank-three controls. No derivative or frequency
budget is imposed. The construction uses narrow transitions of width
2^-32, and should not be interpreted as small in a derivative norm.

The full-support equality condition from R11 additionally implies
nonattainment of the exact minimum in the continuous class. The
smooth class has the same infimum, approached by feasible designs;
the particular design here is certified near that infimum.

## Inputs and evidence

- Frozen R01 exact Q and absolute derivative bounds.
- Frozen R09 exact-Q jets.
- Frozen R11 four-cosine moment matrix for correction, and its standard
  library-only rational interval primitives for the independent check.
- A floating-point optimization probe supplies fixed rational candidates,
  not proof of optimality or complete root enumeration.
- 28 new residual-root boxes and 113 sign leaves cover [0,1].
- 261 new Arb finite-interval integrals: nine orders on 29 sign intervals.
- Global positive derivative envelopes on [0,2] and an analytic tail
  establish a quadratic moment-smoothing error bound.
- A separate rational adjugate solve, full control determinant, sign
  partition and norm-bound calculation reproduce the algebraic claims.
- Three mpmath step moments at 50 and 80 digits provide numerical
  corroboration, with twelve rather than eight theta terms.

The narrow smooth transitions are not directly integrated numerically.
Their moments are enclosed by the analytic N*M_j*eta^2 bound. The
rational checker trusts the integral enclosures and analytic majorants.
The analytic proof has not had external expert or formal verification.

## Reproduction and preservation

From the workspace root, the read-only closure check is

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_norm_threshold/audit_snapshot.py
```

The [runtime record](runtime.json) lists the environment. The
[audit report](audit_report.json) records evidence links, prior-package
preservation and the scope of its checks. A provenance audit is not
another mathematical proof.

For a calculation rerun, copy the complete research tree to a disposable
directory. In that copy remove only the three R12 JSON files under
`results/`, retaining the recorded probe, then run in this order:

```sh
PYTHONDONTWRITEBYTECODE=1 python research/kernel_norm_threshold/certify_threshold.py --output research/kernel_norm_threshold/results/threshold_certificate.json
PYTHONDONTWRITEBYTECODE=1 python research/kernel_norm_threshold/check_threshold.py --output research/kernel_norm_threshold/results/threshold_check.json
PYTHONDONTWRITEBYTECODE=1 python research/kernel_norm_threshold/crosscheck_moments.py --output research/kernel_norm_threshold/results/moment_crosscheck.json
```

The programs refuse to overwrite their result files. The downstream
programs intentionally read the canonical result path in that copy.
Compare candidate identities, interval overlap and final inequalities;
elapsed times and enclosure widths need not reproduce byte-for-byte.
Rerunning the floating-point probe may select slightly different binary
rationals; that is a different candidate and needs its own certificate.

Two unsuccessful implementation versions are retained as historical
sources in `diagnostics/`; they are not the current entrypoints. The
[cost guard record](diagnostics/interval_cost_guard.json) explains why
the outward upper endpoint must be used for a feasible budget. The
[rational decoding record](diagnostics/rational_point_decode.json)
explains why exact dyadics must be decoded before interval-grid rounding.
The final outputs passed both checks.

## Scientific scope

This is a new modified kernel, separate from R10's finite root window.
No old root-region figures or finite-box constants are transferred.
The old manuscript remains an archive; the eventual paper will be
written from the research notes. Classical weak duality, smoothing and
moment correction are not claimed as new methods. The quantitative
result's literature priority and external mathematical review remain
open; [REFERENCES.md](REFERENCES.md) records the targeted source check.

Two scientific figures are included. Their floating-point rendering is
illustrative; the rigorous intervals and exact coefficient definitions
are in the JSON evidence. The TeX theorem and caption fragments have
not been compiled and are not a complete paper.
