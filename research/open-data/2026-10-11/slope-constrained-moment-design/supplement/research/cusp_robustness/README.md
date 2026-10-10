# R07 — Uniform kernel perturbation and cusp sensitivity

This package answers the next research question after R06: quantitative
persistence of the whole certified local cusp/fold geometry under
bounded relative kernel errors. It retains the original packages and
does not modify or publish the original manuscript.

- [Türkçe araştırma notu](ARASTIRMA_NOTU.md)
- [Analytic theorem and proof](PROOF.md)
- [Diagnostic history](DIAGNOSTICS.md)
- [Generating certificate](results/robustness_certificate.json)
- [Independent rational audit](results/rational_check.json)
- [Explicit conditioning witness](results/condition_witness.json)
- [Separate sensitivity and numerical check](results/condition_check.json)
- [Finite-amplitude exact cusp pinning](results/pinned_cusp_certificate.json)
- [Exact identity, rational and direct numerical pinning check](results/pinned_check.json)
- [English theorem fragment](THEOREM_APPENDIX.tex)
- [Figures and English captions](FIGURE_CAPTIONS.md)
- [Read-only provenance audit](audit_snapshot.py)

The proved budget is |h|≤10^-18 for one fixed real measurable h,
independent of all four controls, in Φ_h=Φ(1+h). It covers every such h,
not only sampled kernels. See the proof for the original-coordinate
windows, the distinction between recentering and absolute geometry,
and the limits of the sensitivity statement.

Run from the project root with the existing `.venv-math` runtime.
Every computational command refuses to overwrite its output. For
example, choose unused paths outside the frozen package:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_robustness/certify_robustness.py --output /tmp/r07_new_certificate.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_robustness/check_robustness.py --certificate /tmp/r07_new_certificate.json --output /tmp/r07_new_rational_check.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_robustness/condition_witness.py --output /tmp/r07_new_condition.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_robustness/check_condition.py --output /tmp/r07_new_condition_check.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_robustness/pinned_cusp.py --output /tmp/r07_new_pinned_certificate.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/cusp_robustness/check_pinned.py --output /tmp/r07_new_pinned_check.json
```

The condition-check command checks the retained conditioning certificate by a
fresh direct cos-modulated mpmath integral and rational tangent bounds.
The independent full checker rebuilds the new Taylor enclosures and
both nonlinear cusp polynomials, using saved original-kernel jets,
majorants and R03 contraction witnesses as input assumptions. It does
not import FLINT or the R07 generating code. These trust boundaries
are recorded in the JSON reports.

No second quadrature of an arbitrary h is needed or attempted: its
error is bounded analytically. The explicit cosine witness has six
new rigorously enclosed original-kernel integrals and three separate
direct numerical checks. All claims remain subject to external
mathematical review; no literature priority, journal acceptance or
physical dynamics claim is made. The final two commands concern a separate
result: a single specially constructed direction keeps the exact quartic
cusp fixed and nondegenerate for amplitudes in [-1/2,1/2]. This larger
amplitude result is local to Q; it does not extend the full-arc theorem
to all such perturbations or to these larger amplitudes.

After freezing, `PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python
research/cusp_robustness/audit_snapshot.py` checks every retained file,
the evidence links and R01–R06/original preservation. The `--freeze`
option is for the first snapshot only and refuses to replace one.
The English TeX fragment was checked for brace balance, not compiled.
