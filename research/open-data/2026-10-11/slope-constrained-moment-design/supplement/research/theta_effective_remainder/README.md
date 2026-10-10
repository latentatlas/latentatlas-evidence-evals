# R25 — Effective fourth-order bounds for the fixed theta problem

For the exact fixed Q, δ₀,C₂,C₄ of R24, the new analytic argument gives

    −9.593×10⁻⁵⁴/M⁶ < δ(M)−δ₀−C₂/M²−C₄/M⁴ <1.488×10⁻⁵³/M⁶
    for every 2×10⁻⁵≤M≤2×10⁻³.

This is a **finite-window** optimal-value error bound. The original
infinite theta family, parameter uncertainty and infinite tails are kept.
It is not an all-large-M sixth-order expansion.

- [Analytic proof](PROOF.md)
- [“Certified” terminology and its precise scope](CERTIFICATION_TERMINOLOGY_TR.md)
- [Evidence, limits and review](REVIEW.md)
- [Numerical table](results/TABLE.md)
- [Scientific figure](figures/effective_fourth_order.png)
- [Figure caption](FIGURE_CAPTIONS.md)
- [Audit record](audit_report.json)

Run from any working directory, preserving the complete research tree:

```sh
python3 /path/to/research/theta_effective_remainder/audit_snapshot.py
python3 /path/to/research/theta_effective_remainder/audit_snapshot.py --with-arb
```

The standard-library audit freshly replays exact algebra and the independent
rational checker in a temporary directory. With `--with-arb`, it also freshly
reproduces the interval certificate and compares exact output bytes. The
separate numerical crosscheck is checked from its recorded evidence; it is
not silently rerun on every audit. Hash checks establish artifact integrity,
not analytic correctness.

Fresh output commands (each output path must not exist):

```sh
python3 check_algebra.py --output /tmp/r25-new-algebra.json
python3 certify_remainder.py --output /tmp/r25-new-certificate.json
python3 check_bounds.py --certificate /tmp/r25-new-certificate.json --output /tmp/r25-new-check.json
python3 crosscheck.py --certificate /tmp/r25-new-certificate.json --output /tmp/r25-new-direct.json
```

Run these from this package directory or replace script names with absolute
paths. The certificate needs python-flint; the diagnostic needs mpmath.
The plot uses mpmath, NumPy and Matplotlib. Versions are recorded in
[runtime.json](runtime.json) and [requirements.txt](requirements.txt).

The implementation imports frozen R22/R24 interval/algebra helpers. The
rational checker accepts transcendental derivative and tail enclosures as
inputs; its independent part is the reconstruction of the quantitative
inequalities. The mpmath check uses central inputs and twelve theta terms.
Its agreement corroborates, but does not certify, the infinite exact problem.

The previous 25 manifests/1043 frozen entries remain unchanged. R25 has its
own [manifest](manifest.json). The R19/R20 manuscript files are preserved.
This is a local publication-preparation package, not an external certification,
peer-reviewed publication, formal proof or public release.
