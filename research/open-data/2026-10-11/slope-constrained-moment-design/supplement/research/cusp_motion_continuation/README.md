# R29 — Recentered continuation of cusp coefficient motion

For the exact R03 graph Q(ν), the exact fourth asymptotic coefficient satisfies

    1.9×10⁻⁴⁰ < C₄'(ν) < 5.3×10⁻⁴⁰,  −1/64 ≤ ν ≤ 0.

This gives strict increase on an interval 1024 times longer than R28's.
The endpoint anchor gives 2.48374879×10⁻³⁹<C₄(ν)<2.49203006×10⁻³⁹.
The derivative uses the original ν coordinate. R23's pointwise coefficient
interpretation extends to this arc; R27's finite-M remainder constants do not.

- [Türkçe bulgu notu](BULGU_NOTU_TR.md)
- [Analytic proof](PROOF.md) and [numbers](results/TABLE.md)
- [Review and evidence limits](REVIEW.md)
- [Figure](figures/continuation.png) and [caption](FIGURE_CAPTIONS.md)
- [Audit](audit_report.json) and [frozen manifest](manifest.json)
- [Failed attempts and corrections](diagnostics/README.md)

There are 32 independently re-integrated cusp anchors and 32 closed driver
cells. The cusp identity follows from containment in R03 uniqueness tubes;
the dual identity at seams follows from uniqueness of the global minimizer.
Each cell retains its full quadrature, contractions, sign cover, root jets,
coefficient sums and derivative bounds in deterministic gzip-compressed JSON.
Compression changes no numerical content. A readable index is
[cover/certificate.json](results/cover/certificate.json).

Run with the full research tree preserved, keeping assertions enabled:

```sh
python3 /path/to/research/cusp_motion_continuation/audit_snapshot.py
python3 /path/to/research/cusp_motion_continuation/audit_snapshot.py --with-arb
```

The default audit checks frozen provenance, all recorded diagnostic arithmetic
and figures, replays exact and rational checks, and runs the R28 audit. With
`--with-arb` it also rebuilds all 32 anchors and cells from fresh integrals in
a temporary directory and compares the compressed evidence bytes, then runs
the inherited Arb audits. It does not mechanically prove the analytic
arguments. Independent diagnostic integrals were freshly run at construction;
the audit checks their recorded identities rather than silently rerunning
mpmath. A separate fresh diagnostic run is available below.

For separate reproduction choose unused output paths:

```sh
python3 certify_continuation.py --output-dir /tmp/r29-fresh-cover
python3 check_bounds.py --cover-dir /tmp/r29-fresh-cover --output /tmp/r29-fresh-rational.json
python3 check_algebra.py --output /tmp/r29-fresh-algebra.json
python3 crosscheck.py --output /tmp/r29-fresh-diagnostics.json
```

`crosscheck.py` compares against the recorded cover in this package and solves
the original cusp/dual equations at 23 driver values, using both 80 and 110
digits and two finite-difference steps. The finite theta sum, finite integral
cutoff and unbounded finite-difference truncation error make this diagnostic
corroboration, not the continuum proof.

[Requirements](requirements.txt), [runtime](runtime.json). The previous
29 manifests and 1162 frozen entries are preserved. No manuscript replacement,
public release, journal submission, external review or novelty verdict is
part of this package. The specific use of validated or certified enclosures
follows the [terminology note](../theta_effective_remainder/CERTIFICATION_TERMINOLOGY_TR.md).
