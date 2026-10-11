# R13 — Slope-constrained relative kernel cost

Start with the [Turkish research note](ARASTIRMA_NOTU.md) or the
[analytic proof](PROOF.md). This asks how the same fixed-Q target changes
when a Lipschitz bound on the relative multiplier is added.

Analytic proof drafts establish attainment in the closed Lipschitz moment
class, a strict gap above the unrestricted threshold at every finite
budget, and a convex strictly decreasing cost profile. Smooth positive
nondegenerate designs have the same infimum for each positive budget;
attainment in that smaller class is not asserted.

The numerical package supplies two globally bounded-slope witnesses,
certified nondegenerate interpolation between them, an explicit lower
cost from one dual residual crossing, and a bound near zero slope.
It does not compute the exact finite-budget optimum curve. No mass
normalization or Fourier cutoff is imposed.

## Reproduction

Keep assertions enabled and bytecode disabled. In a disposable complete
research-tree copy, use new output paths or remove only this package's
result files in that copy before these canonical commands:

```sh
PYTHONDONTWRITEBYTECODE=1 python research/kernel_slope_budget/certify_budget.py --output research/kernel_slope_budget/results/budget_certificate.json
PYTHONDONTWRITEBYTECODE=1 python research/kernel_slope_budget/check_budget.py --output research/kernel_slope_budget/results/budget_check.json
PYTHONDONTWRITEBYTECODE=1 python research/kernel_slope_budget/crosscheck_moment.py --output research/kernel_slope_budget/results/moment_crosscheck.json
PYTHONDONTWRITEBYTECODE=1 python research/kernel_slope_budget/plot_results.py
```

The checker uses rational arithmetic without FLINT but accepts local
transcendental enclosures and integral values as inputs. The generator
uses existing exact-Q data, a new local interval enclosure, and one new
positive moment with a second precision/partition. mpmath corroboration
is numerical, not a proof. The analytic results await external review;
standard compactness, convexity and moment methods are not claimed new.

Read-only closure:

```sh
PYTHONDONTWRITEBYTECODE=1 python research/kernel_slope_budget/audit_snapshot.py
```

This verifies hashes/evidence links, not every analytic proof. The
`diagnostics/` directory retains the failed metadata-path helper and a
pre-cleanup decimal-formatting checker/output. Neither is a current
entrypoint. Prior frozen research packages are unchanged.
