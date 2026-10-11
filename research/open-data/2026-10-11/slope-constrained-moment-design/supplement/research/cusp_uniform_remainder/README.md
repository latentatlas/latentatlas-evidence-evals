# R27 — Uniform fourth-order accuracy on a cusp subarc

For the exact original cusp graph Q(ν), I=[−2⁻¹⁶,0] has a common
positive coefficient bound and a common error bound:

    2.47×10⁻³⁹<C₄(ν)<2.52×10⁻³⁹,
    −1.02×10⁻⁵³/M⁶ < δ_ν(M)−δ₀(ν)−C₂(ν)/M²−C₄(ν)/M⁴
                     <1.64×10⁻⁵³/M⁶,   for all ν∈I, M≥2×10⁻⁵.

All coefficients are parameter-dependent exact quantities. Each ν permits
a separate kernel perturbation; one common design for the arc is not
asserted. The full curve [−29,0], monotonic C₄ and a C₆ coefficient
remain outside this statement.

- [Türkçe bulgu notu](BULGU_NOTU_TR.md)
- [Analytic proof](PROOF.md)
- [Review and dependencies](REVIEW.md)
- [Numbers](results/TABLE.md)
- [Scientific figure](figures/cusp_uniformity.png) and [caption](FIGURE_CAPTIONS.md)
- [Audit](audit_report.json) and [manifest](manifest.json)
- [Diagnostic history](diagnostics/README.md)

Run from any working directory, retaining the full research tree:

```sh
python3 /path/to/research/cusp_uniform_remainder/audit_snapshot.py
python3 /path/to/research/cusp_uniform_remainder/audit_snapshot.py --with-arb
```

The first command freshly replays exact algebra and the rational checker,
checks recorded direct-integral comparisons, and audits R26. The second
also freshly produces this package's Arb certificate and R26/R25's
certificates, comparing output bytes. These audits do not mechanically
prove the analytic argument. Direct numerical quadrature is not silently
rerun on every audit.

Separate commands with fresh output paths, run here or with absolute paths:

```sh
python3 check_algebra.py --output /tmp/r27-new-algebra.json
python3 certify_uniform.py --output /tmp/r27-new-certificate.json
python3 check_bounds.py --certificate /tmp/r27-new-certificate.json --output /tmp/r27-new-rational.json
python3 crosscheck.py --output /tmp/r27-new-direct.json
```

The producer reads the recorded algebra and frozen prerequisite enclosures.
The mpmath crosscheck solves the original truncated integral equations at
five drivers and compares with the recorded certificate. It uses central
inputs, twelve theta terms and cutoff 1; its agreement does not establish
the continuum or infinite-tail claims. Use a disposable copy for source or
plot changes. Keep assertions enabled. Versions are in [runtime.json](runtime.json)
and [requirements.txt](requirements.txt).

The new model includes νu⁶ and derivatives through order five. The moving
dual contraction, tightened roots, coefficient sums, finite-cell remainder
and moment repair are recomputed over the parameter interval. The exact
cusp graph and positive-moment bounds from R03/R09 are inherited inputs.
The rational checker reconstructs bounds from explicit interval inputs;
it does not independently reintegrate the kernel.

The previous 27 manifests/1096 frozen entries and existing manuscripts
remain unchanged. No external referee approval, formal proof, priority
or journal acceptance is implied. The precise
[certification terminology](../theta_effective_remainder/CERTIFICATION_TERMINOLOGY_TR.md)
continues to apply to individual validated enclosures.
