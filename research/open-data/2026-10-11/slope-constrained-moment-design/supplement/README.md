# Fourth-order asymptotics and monotonicity in slope-constrained moment design

Hüseyin Buldurgan — independent researcher.

This supplement accompanies the new preprint "moment_design_preprint_v1.pdf".
It is shared to invite mathematical criticism before journal submission.
AI assistance is disclosed. No external referee approval or formal proof
verification is represented.

## Start here

- The top-level PDF is the current paper.
- research/preprint_v1/ contains its LaTeX sources, figure script, and claim review.
- EVIDENCE_INDEX.json maps package identifiers to proofs and checkers.
- PUBLIC_COPY_PROVENANCE.json records bookkeeping transformations.
- verification/public_replay/report.json records the public-copy replay.
- SHA256SUMS.json records this release's checksums.

The general fourth-order theorem is followed by a theta-family application
with a uniform error bound and strict comparison of actual optimal values.
Useful review targets are the infinite-switch Taylor/repair argument,
the effective primal/dual estimates, and the transport inequality.

## Verify and run

Use Python 3.12 with assertions enabled; do not use python -O.

    python3 verify_release.py
    python3.12 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
    .venv/bin/python -B research/preprint_v1/run_audits.py --output-dir new-audit

The output directory must be new. Audits use temporary files rather than
overwriting reference certificates. The theta chain regenerates Arb enclosures
and performs rational reconstruction and independent diagnostics.
Pinned versions record the tested environment; installation on another
platform is a separate compatibility matter.

Focused non-rigorous integration cross-checks:

    .venv/bin/python -B research/finite_slope_fourth_order/crosscheck_integrals.py --output finite-integrals-new.json
    .venv/bin/python -B research/infinite_slope_fourth_order/crosscheck_integrals.py --certificate research/infinite_slope_fourth_order/results/certificate.json --output infinite-integrals-new.json

The paper compiles with Tectonic 0.17.0:

    .venv/bin/python -B research/preprint_v1/build_pdf.py --tectonic tectonic --output-dir new-paper-build

A PDF build checks presentation. Its binary can vary with typesetting
dependencies even when the text and equations are unchanged.

## Historical material and privacy transformation

The dependency tree contains 32 historical packages and diagnostics,
including earlier manuscript drafts. **Only the top-level PDF is the
current paper for review.** Historical scope statements describe their
own research stage. The original early buldurgan-A3-cusp-dBN.tex article,
a CV, account information, and personal screenshots are not included.

Local machine paths in bookkeeping are replaced by neutral placeholders.
Dependent SHA-256 references are propagated, including in compressed JSON.
Some Python files contain changed checksum constants; mathematical operations
are unchanged. Transformations are recorded and the original local archive
remains unchanged. The public snapshot has its own verified hashes and replay.

Old references to a desktop archive record provenance. That obsolete
article/archive is not a mathematical input for the four current replay
entry points. Use the commands above rather than historical commands
containing /PROJECT or /LOCAL_HOME.

## Licenses and publication status

The author selected CC BY 4.0 for the paper, text, figures, and research
data, and MIT for original code on 23 September 2026.
See LICENSE_STATUS.md and LICENSE_CODE_MIT.txt.
Third-party dependencies retain their own licenses and are not bundled.
A public identifier is recorded only after an actual deposit.
