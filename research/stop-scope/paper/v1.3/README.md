# Manuscript v1.3

**Verifying Stop Scope in Agent Workflows** — Huseyin Buldurgan, 23 October 2026.

- [PDF, 9 pages](Verifying_Stop_Scope_v1.3.pdf)
- [Editable Word](Verifying_Stop_Scope_v1.3.docx)
- [Markdown source](MANUSCRIPT.md)
- [What changed since v1.2](CHANGES.md)
- [Evidence, scope, provenance and reproduction](../../progress/2026-10-16/README.md)
- [Revision checks and artifact digests](REVISION_CHECKS.json)

This is an explanatory revision of the v1.2 research preprint, not a new experimental release. It sharpens the contribution, adds the live event sequence, makes legitimate-work preservation visible in the results table, and reports the observed fault-control outcomes. The original sprint release, v1.2 paper and 16 October evidence snapshot are unchanged. No DOI is assigned by this GitHub publication.

## Inspect and verify

From this directory, with Python 3.10 or newer:

```sh
python3 -B verify_revision.py
python3 -B -m unittest test_revision -v
```

The first command checks the revision digests, calls the unchanged snapshot auditor, and compares Tables 2 and 3 with its preserved result records. It invokes no model or experiment runner. An integrity check is not an independent authentication of the historical provider calls.

For a fresh provider-free experiment, follow the [receiver reproducer instructions](../../progress/2026-10-16/receiver-reproducer/README.md). That experiment complements the archived live restart comparison; it does not regenerate live responses. Existing CI also reruns that provider-free regression matrix. Its reruns are not additional observations reported by this manuscript.

## Rebuild the document

Install `python-docx` in a suitable environment and run `python3 -B build_docx.py` here. The sequence figure is native editable Word content, with the same wording in the Markdown source. Convert the resulting DOCX to PDF using an office renderer. Pagination depends on fonts and renderer; the released nine-page PDF was rendered with the bundled LibreOffice environment and every page was visually inspected by the assistant. Document-generation dependencies are separate from the standard-library evidence verifier.
