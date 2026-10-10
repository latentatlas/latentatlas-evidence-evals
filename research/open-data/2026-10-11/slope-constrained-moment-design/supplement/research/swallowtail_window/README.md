# R10 — Reproduction and evidence map

[Turkish research note](ARASTIRMA_NOTU.md) · [Proof](PROOF.md) ·
[Theorem fragment](THEOREM_APPENDIX.tex) · [Diagnostics](DIAGNOSTICS.md)

This package fixes the **modified** R09 kernel at its exact order-four
amplitude. It certifies a finite box in original t,λ,μ,ν coordinates,
all its multiple roots via an auxiliary fold surface, a cusp curve,
open regions with 0/2/4 roots, and a partially classified section grid.
Gray grid cells are explicitly unresolved. Earlier R01–R09 files and
the original manuscript are preserved.

## Run order

Use the workspace `.venv-math/bin/python`, with
`PYTHONDONTWRITEBYTECODE=1` and assertions enabled. Versions are
recorded in [runtime.json](runtime.json). Existing mathematical output
files are intentionally not overwritten.

To reproduce, use a scratch copy with the adjacent R01–R09 dependencies
and the R10 source files. Remove only the copied generated R10 results,
figures and manifest. Run the following from the copied project root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/swallowtail_window/build_model_v2.py --output research/swallowtail_window/results/model_v2.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/swallowtail_window/certify_window.py --output research/swallowtail_window/results/window_certificate.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/swallowtail_window/check_window.py --output research/swallowtail_window/results/window_check.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/swallowtail_window/certify_samples.py --output research/swallowtail_window/results/sample_certificate.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/swallowtail_window/check_samples.py --output research/swallowtail_window/results/sample_check.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/swallowtail_window/certify_chart.py --output research/swallowtail_window/results/chart_certificate.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/swallowtail_window/check_chart.py --output research/swallowtail_window/results/chart_check.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/swallowtail_window/crosscheck_integrals.py --output research/swallowtail_window/results/integral_crosscheck.json
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/swallowtail_window/summarize_results.py
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/swallowtail_window/plot_results.py
```

The `v1` model and probes are historical diagnostics. They are not
needed for reproduction of the final results. Reproduced outputs can
have different timings and hashes; compare mathematical enclosures
and pass conditions rather than timed whole-file hashes. The published
manifest identifies one recorded run.

Read-only preservation and provenance check:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/swallowtail_window/audit_snapshot.py
```

The audit verifies this snapshot and its earlier dependency chain;
it is not a substitute for rerunning the arithmetic checks or reviewing
the analytic proof. The original project paths recorded by R01 must
be accessible for its preservation audit.

## Evidence roles

| Files under `results/` | Mathematical role |
|---|---|
| `model_v2.json` | Frozen integral jets, exact normalization and new majorants including ν variation |
| `window_certificate.json`, `window_check.json` | Whole finite box, uniform fold and cusp graphs, three open 0/2/4 boxes |
| `sample_certificate.json`, `sample_check.json` | Two cusp points, simultaneous two-double-root point, 81 folds and six simple roots |
| `chart_certificate.json`, `chart_check.json` | 2804 whole-cell root counts and 780 explicitly unclassified cells |
| `integral_crosscheck.json` | 27 direct rigorous integrations and nine separate numerical checks at two precisions |
| `key_results.json` | Outward decimal summaries from rational endpoints |

The three rational checkers import no FLINT or R10 generating module.
They reconstruct normalized jets and the new Taylor bounds, using
the prior integral enclosures and the new unnormalized majorants as
trusted inputs. The chart checker preserves the explicitly affine
control directions. The sample checker computes its own tighter
boxes within the common uniqueness boxes.

Two PNG/SVG figure pairs are provided. The LaTeX theorem and figure
caption fragments have balanced braces but were not compiled in this
environment. A final visual review records the PNG hashes.

[manifest.json](manifest.json) and [audit_report.json](audit_report.json)
close this recorded package. External mathematical review, literature
priority and a full manuscript submission are not claimed.
