# R04 — Uniform cusp neighborhoods and changing opening coefficient

This package builds on the frozen R01, R02 and R03 packages. It proves
a finite root-region theorem at every ν∈[−29,0], using coordinates
relative to the exact cusp, and proves strict monotonicity of the
leading three-root width coefficient C(ν). See the
[Turkish research note](ARASTIRMA_NOTU.md) and [analytic proof](PROOF.md).

The uniform window is |s|≤0.003, |ℓ|≤10^-6, |m|≤2×10^-9.
The finite width is bounded by 0.98ℓ^(3/2) and 1.72ℓ^(3/2).
The leading coefficient increases by about 2.494633% from the quartic
to the sextic cusp. Monotonicity of finite Wν(ℓ) for every nonzero
ℓ in the rectangle is not asserted.

## Reproduction

Preserve the three sibling packages and their manifests. They supply
76 recorded files, checked before new computations. Use Python 3.12.14,
python-flint 0.9.0, mpmath 1.4.1 and matplotlib 3.11.2 as in the existing
.venv-math; pinned dependencies are in the frozen R01 package.

From /PROJECT:

~~~sh
.venv-math/bin/python research/cusp_geometry/certify_geometry.py
.venv-math/bin/python research/cusp_geometry/check_geometry.py
.venv-math/bin/python research/cusp_geometry/test_geometry.py
.venv-math/bin/python research/cusp_geometry/check_independent.py
.venv-math/bin/python research/cusp_geometry/plot_geometry.py
~~~

The first command produces the complete certificate. The other commands
read it. The full generating run took about 12 seconds; the independent
exact-Fraction expansion takes substantially longer. Adding --trial
to the first command checks only cells 0,28,57 and writes to diagnostics/.
It is not a complete path certificate.

Do not use -O/-OO, which disable assertions. The rational checker
rejects them. Use a fresh project copy to preserve this result snapshot.
Runtime fields may change hashes on a fresh run; regenerate dependent
checks and plots after changing the certificate. The supplied manifest
records this snapshot and is not automatically rewritten by those
commands. Logs capture the recorded terminal output; rerunning the
commands without redirection displays output instead of recreating logs.

## Code and evidence

- geometry_model.py: preserves the shared driver in four-variable
  Taylor bounds; adds derivative orders 51–56 and majorants 57–62;
  supplies exact-cusp-centered local Taylor formulas.
- width_shape.py: a factored degree-five numerator for the derivative
  of −D3/D4, polynomial jets and separate error bounds.
- certify_geometry.py: all local implicit fold surfaces, finite
  bounds, root witnesses, and the monotone opening result.
- check_geometry.py: no FLINT import; exact rational inequality
  checks, expanded eleven-monomial width polynomial, independent
  multinomial predictor coefficients and partial derivatives.
- test_geometry.py: four regression groups, 72 total direct integral
  comparisons, algebra identities and invalid-domain behavior.
- check_independent.py: reuses only the frozen R03 mpmath integrator;
  24 derivative checks and C/C' comparisons. Numerical support only.
- plot_geometry.py: common certified inner/outer fold bands and the
  leading coefficient along the path. Candidate center lines illustrate
  the curve; interval inequalities establish the claims.
- results/geometry_certificate.json: complete new witnesses, extra
  integral enclosures, domain bounds, provenance and source hashes.
- results/exact_check.json, results/independent_check.json,
  results/plot_metadata.json: checks linked to their source files and
  the exact input certificate.
- diagnostics/: the development failure and successful three-cell trial.

## Trust boundary

The analytic arguments, the frozen FLINT/Arb integration and tail
implementation, and Python execution are trusted. The separate rational
checker assumes the new saved oscillatory derivative enclosures and
local Taylor values; it does not independently certify their integration.
Direct integral tests sample the new formulas and do not replace their
uniform remainder argument. The mpmath checks are not interval proofs.
External expert review and literature priority remain open.
