# R19 — A new manuscript core

21 September 2026. **Amplitude cost of slope-constrained moment design:
sharp asymptotics and a validated theta example.**

This is a research manuscript for review, newly written from the R01/R11–R18
notes. It is not a revision of the legacy TeX, a submitted paper, an external
referee report, or a new scientific computation. The contribution is stated
as a conditional general coefficient theorem, a validated infinite-switch
theta example and an explicit uniform remainder.

- `output/pdf/manuscript.pdf`: English manuscript, with three scientific figures.
- [LaTeX source](manuscript.tex).
- [Turkish reading note](OKUMA_NOTU_TR.md).
- [Claim-to-source map](CLAIM_SOURCE_MAP.md).
- [Input identities](inputs.json) and [exact decimal-transfer checks](data_checks.json).
- [Review notes](REVIEW_NOTES.md) and [closure audit](audit_report.json).
- [Source and output manifest](manifest.json).

The arithmetic results and earlier packages remain unchanged. The complete
research archive is needed for certificate checking; this folder alone is
not a replacement for C1–C4 or their producers. The manuscript explicitly
states the dependence on its companion data and the absence of a public
archive DOI at this stage.

## Read-only integrity check

From any working directory, pass the full path to this script:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 /path/to/research/manuscript_core/audit_snapshot.py
```

This checks the prior 19 manifests and 859 entries, linked inputs, printed
constant transfer, references, source/PDF identity and the frozen package.
It checks provenance and recorded validation, not a formalization of the
analytic proof. Do not run Python with `-O`.

## Rebuild the PDF

Use Tectonic 0.17.0 (or adapt the ordinary LaTeX source for a TeX installation).
The compiler is local. It may fetch its public TeX package bundle; it does
not upload the manuscript. The official compiler release is
[Tectonic 0.17.0](https://github.com/tectonic-typesetting/tectonic/releases/tag/tectonic%400.17.0).
No compiler binary or downloaded TeX package is distributed in this archive.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 /path/to/research/manuscript_core/build_pdf.py \
  --tectonic /path/to/tectonic --output-dir /tmp/slope-paper-new-build
```

The output directory must not exist. The builder uses a temporary working
directory and retains only the PDF, final TeX log/auxiliary record, build
metadata and compiler transcript in the selected output directory.
It fails if the final log reports overfull boxes, missing glyphs or undefined
references. Rendered-page inspection is still required after a layout change.
PDF timestamps and compiler versions can change bytes without changing the
scientific content; do not overwrite frozen outputs to compare builds.

`prepare_inputs.py` generated the small TeX constants file directly from
frozen checker outputs, copied the three source figures unchanged and
recomputed the printed threshold endpoints in exact rational arithmetic.
It refuses to edit a frozen R19. To repeat that preparation, work in a
disposable copy of the whole research tree and remove only that copy's
R19 manifest. Earlier packages must remain byte-identical.

## Repeat the scientific arithmetic checks

The original package READMEs give the full producer and crosscheck commands.
For this editorial step, fresh copies of the R15 and R16 rational checks and
the R18 normalization check are recorded under `verification/`. These accept
the certified transcendental enclosures as inputs. A fresh interval producer
run was not necessary for a manuscript-only change and is not claimed.

Public distribution still needs a selected code/data license, finalized
author information, archive metadata review and a persistent repository
identifier. This local preparation does not submit or publish the work.
