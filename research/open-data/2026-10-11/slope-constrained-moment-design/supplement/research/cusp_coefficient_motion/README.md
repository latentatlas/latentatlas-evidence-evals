# R28 — Motion of the fourth coefficient on a short cusp arc

For the exact R27 cusp family and its exact fourth-order coefficient,

    2.82×10⁻⁴⁰<C₄'(ν)<4.35×10⁻⁴⁰,  −2⁻¹⁶≤ν≤0.

The derivative is in the original ν coordinate, one-sided at the endpoints.
This proves strict increase and bounds the gain between any two points on
this arc. Anchoring at R24's exact Q(0) yields
2.49202340×10⁻³⁹<C₄(ν)<2.49203006×10⁻³⁹. It does not prove
monotonicity of the true finite-M optimum or of the remainder.

- [Türkçe bulgu notu](BULGU_NOTU_TR.md)
- [Analytic proof](PROOF.md)
- [Numbers](results/TABLE.md)
- [Review and trust boundary](REVIEW.md)
- [Scientific figure](figures/coefficient_motion.png) and [caption](FIGURE_CAPTIONS.md)
- [Audit](audit_report.json) and [manifest](manifest.json)
- [Diagnostic history](diagnostics/README.md)

With the full research tree preserved, these commands can run from any
working directory:

```sh
python3 /path/to/research/cusp_coefficient_motion/audit_snapshot.py
python3 /path/to/research/cusp_coefficient_motion/audit_snapshot.py --with-arb
```

The default audit replays exact algebra and the rational automatic-
differentiation checker, verifies the recorded independent diagnostics and
all previous frozen packages, and replays R27's audit. The optional flag
also reproduces the new ninth template moment and derivative certificate
and the inherited R27/R26/R25 Arb certificates. It does not mechanically
prove the analytic differentiation and summability arguments.

For separate runs choose new output paths; existing evidence is not overwritten:

```sh
python3 sign_moment.py --output /tmp/r28-fresh-moment9.json
python3 check_algebra.py --output /tmp/r28-fresh-algebra.json
python3 certify_motion.py --output /tmp/r28-fresh-certificate.json
python3 check_bounds.py --certificate /tmp/r28-fresh-certificate.json --output /tmp/r28-fresh-rational.json
python3 crosscheck.py --output /tmp/r28-fresh-direct.json
```

The producer uses recorded prerequisite and new moment/algebra files. The
fresh audit compares their recomputed bytes. The direct numerical check is
separate: it re-solves the original integral equations at 13 drivers for
each of two precisions, then takes two-step finite differences at three
drivers. It does not use the analytic C₄' formula. Its finite theta sum,
finite integration cutoff and unbounded finite-difference error make it
diagnostic corroboration, not an interval proof.

Keep assertions enabled. Dependencies are in [requirements.txt](requirements.txt)
and [runtime.json](runtime.json). Use a disposable copy for source or plot
changes. The previous 28 manifests/1130 frozen entries are preserved.
No manuscript revision, external approval, public release or submission is
part of this package. The
[certification terminology](../theta_effective_remainder/CERTIFICATION_TERMINOLOGY_TR.md)
continues to apply to specific validated enclosures.
