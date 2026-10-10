# R11 — Pinned kernel design and its relative-norm cost

21 September 2026. This is an additional research package. It uses the
original theta example and exact R01 cusp point Q as its base, identifies
general sufficient assumptions, and selects one extension: the least
L-infinity relative kernel change needed to make Q a nondegenerate
order-four zero while keeping its coordinates fixed.

Start with [ARASTIRMA_NOTU.md](ARASTIRMA_NOTU.md) in Turkish or
[PROOF.md](PROOF.md) for the complete analytic arguments. A reusable
English [TeX theorem fragment](THEOREM_APPENDIX.tex) and one
[scientific figure](figures/minimum_relative_change.png) are provided.
The TeX fragment is not the new paper and has not been compiled.

## Evidence and scope

- The general right inverse, minimum-norm formula and smooth-infimum
  argument are analytic proof drafts using classical tools. They have
  not received external mathematical review or a priority assessment.
- The theta example has the certified bracket
  3.96e-10 < delta_star < 2.381e-7. The ratio of its endpoints is about
  601.04. The optimum has not been numerically located.
- The upper bound is furnished by a new smooth four-cosine multiplier
  with frequencies 40,41,42,43. Its exact coefficients are defined by a
  nonsingular moment system. It keeps the exact Q fixed and has a
  nonzero fourth derivative and a rank-three control unfolding.
- The budget is ||h||_infinity over all real bounded measurable h,
  with no bandwidth or derivative restriction. The feasible coefficient
  l1 sum is an upper bound on this norm, not an equality claim.
- R09 optimized a different objective in a different subspace. R10's
  modified kernel is different, so its finite window and figures do
  not apply to this candidate without another proof.
- All R01–R10 frozen packages and the forty original files remain
  inputs. No existing research package or old manuscript was edited.

## Recorded calculation

The generator evaluates 72 shifted moments and one positive moment
using Arb, analytic series/domain tails and the exact-Q displacement.
The separate rational checker recomputes the 4×4 linear solve by Cramer
determinants and checks the full 3×3 control determinant and its reduced
formula. The crosscheck evaluates nine direct product-form integrals,
plus three midpoint values at both 90 and 115 mpmath digits.

The rational checker trusts the integral enclosures and original exact-Q
identification. mpmath checks are corroboration, not certified bounds.
Recorded sources and inputs have SHA-256 identities. The provenance
audit is not a substitute for mathematical review of the quadrature
assumptions or the analytical theorems.

One incorrect provenance rule was corrected at two preflight locations:
reloading an Arb ball can round its radius outward, so identical
serialized balls were an invalid requirement. Exact midpoints and
containment of the input intervals are now checked. All six reused base
jets and nine repacked crosscheck values passed; no calculation output
changed. The [diagnostic](diagnostics/audit_repacking_check.json),
[first audit source](diagnostics/audit_v1.py) and
[second audit source](diagnostics/audit_v2.py) preserve this history.

## Reproduction

Run from the workspace root with the recorded Python environment:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/kernel_design_principle/audit_snapshot.py
```

This command is read-only. It checks the frozen file identities and
evidence links, then verifies the preceding audit chain. See
[runtime.json](runtime.json) for library versions and
[audit_report.json](audit_report.json) for the recorded scope.

The calculation programs deliberately refuse to overwrite existing
outputs. For a full reproduction, copy the research tree, including
all R01–R10 inputs, to a disposable directory and remove only the three
R11 result JSON files from that disposable copy. Run these in order
using an interpreter with the recorded packages:

```sh
PYTHONDONTWRITEBYTECODE=1 python research/kernel_design_principle/certify_candidate.py --output research/kernel_design_principle/results/candidate_certificate.json
PYTHONDONTWRITEBYTECODE=1 python research/kernel_design_principle/check_candidate.py --output research/kernel_design_principle/results/candidate_check.json
PYTHONDONTWRITEBYTECODE=1 python research/kernel_design_principle/crosscheck_integrals.py --output research/kernel_design_principle/results/integral_crosscheck.json
```

The two downstream programs deliberately read the certificate at the
canonical R11 result path in that copy. Compare interval overlap,
mathematical inequalities and exact model identity. Elapsed-time fields
and potentially valid enclosure widths can differ; reproduced files
should not be expected to have the frozen output hashes.

`plot_results.py` reads only the rational checker report. It refuses
to replace recorded figure files. Its floating-point coordinates are
for rendering; rigorous endpoints remain in the JSON evidence.

## Selected continuation

Compute the three-variable weighted L1 distance D in PROOF.md with
rigorous residual-zero and tail control, and compare its induced lower
bound with efficient feasible smooth designs. Neither an additional
kernel survey nor another finite-root atlas is part of this package.

Source-reading limits and the classical nature of the tools are
recorded in [REFERENCES.md](REFERENCES.md). The original manuscript
is an archive; a future paper will be written from the research notes.
