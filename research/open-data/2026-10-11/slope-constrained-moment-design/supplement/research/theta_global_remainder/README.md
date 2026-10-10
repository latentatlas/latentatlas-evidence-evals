# R26 — Uniform fourth-order accuracy for the fixed theta problem

For the exact fixed cusp Q and coefficients δ₀,C₂,C₄ of R23/R24,

    −9.593×10⁻⁵⁴/M⁶ < δ(M)−δ₀−C₂/M²−C₄/M⁴ <1.488×10⁻⁵³/M⁶
    for every M≥2×10⁻⁵.

R25 established this inequality only on 2×10⁻⁵≤M≤2×10⁻³. This package
removes the upper budget restriction through a new analytic tail argument.
The fixed infinite theta problem, exact parameter uncertainty and moment
constraints are retained. M is the allowed Lipschitz slope of the kernel
perturbation, not a financial or training budget.

Consequently δ=δ₀+C₂/M²+C₄/M⁴+O(M⁻⁶) with explicit constants and a
sufficient onset. The leading approximation δ₀+C₂/M² underestimates the
true minimum amplitude for every M≥2×10⁻⁵. The sign of the remainder
after C₄/M⁴ and existence of a sixth-order coefficient remain open.

- [Türkçe bulgu ve sınır notu](BULGU_NOTU_TR.md)
- [Analytic proof, G1–G14](PROOF.md)
- [Evidence and adversarial review](REVIEW.md)
- [Numerical table](results/TABLE.md)
- [Scientific figure](figures/global_fourth_order.png)
- [Figure captions](FIGURE_CAPTIONS.md)
- [Audit](audit_report.json) and [frozen manifest](manifest.json)

Run from any working directory, retaining the complete research tree:

```sh
python3 /path/to/research/theta_global_remainder/audit_snapshot.py
python3 /path/to/research/theta_global_remainder/audit_snapshot.py --with-arb
```

The standard-library audit freshly replays exact algebra and outward
512-bit rational reconstruction, verifies recorded diagnostic inequalities,
and runs R25's audit. With `--with-arb`, both the new global certificate
and R25's finite-root certificate are freshly reproduced and compared
byte for byte. The direct numerical quadrature is a separate diagnostic;
it is not silently rerun on each audit.

Fresh-output commands, from this directory or with absolute script paths:

```sh
python3 check_algebra.py --output /tmp/r26-new-algebra.json
python3 certify_global.py --output /tmp/r26-new-certificate.json
python3 check_bounds.py --certificate /tmp/r26-new-certificate.json --output /tmp/r26-new-check.json
python3 crosscheck_tail.py --output /tmp/r26-new-direct.json
```

Output paths must not exist. The producers read the frozen prerequisite
packages and this package's recorded algebra as identified by their hashes.
Use a disposable copy for changes or plotting; frozen evidence is not to
be overwritten. [runtime.json](runtime.json) and [requirements.txt](requirements.txt)
record the versions used. Keep Python assertions enabled.

The rational checker accepts Arb transcendental enclosures and inherited
finite-root bounds as explicit inputs. The separate mpmath check uses
central parameters, twelve theta terms, four distant switches and two
widths per switch. It corroborates local estimates but does not establish
uniformity or enclose the full infinite problem.

The previous 26 manifests/1070 frozen entries remain unchanged. R19/R20
manuscripts are also unchanged. This package is an analytic proof supported
by validated numerical bounds; it is not proof-assistant formalization,
external referee approval or public release. See the precise
[certification terminology](../theta_effective_remainder/CERTIFICATION_TERMINOLOGY_TR.md).
