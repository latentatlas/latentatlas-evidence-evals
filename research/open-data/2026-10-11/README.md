# Open research data — 11 October 2026

This additive release opens the available data, original research code,
methods, figures and reproduction paths for six Huseyin Buldurgan / LatentAtlas
research papers. Original DOI manuscripts and historical sealed artifacts
remain unchanged. New access does not imply new experiments or peer review.

| Paper | Start here |
|---|---|
| Relevance Is Not Authority | [Full synthetic benchmark, guard and retained decisions](relevance-is-not-authority/README.md) |
| Authority-to-Action | [Full run records, 100 cases and 600-row analysis](authority-to-action/README.md) |
| Authority Leases | [Masked study rows, review instrument, replay and figures](authority-leases/README.md) |
| Evidence Authority After Retrieval | [Framework manuscript and reference-code map](evidence-authority-after-retrieval/README.md) |
| RE-Bench systems review | [Pinned source-contract audit and executable checks](re-bench-systems-benchmark/README.md) |
| Slope-constrained moment design | [Complete mathematical reproducibility supplement](slope-constrained-moment-design/README.md) |

Original code: [MIT](LICENSE_CODE_MIT.txt). Author-owned research data, papers and
explanatory material: [CC BY 4.0](LICENSE_DATA_CC_BY_4_0.md). Third-party licences
remain in force, including the retained METR RE-Bench licence and its benchmark
integrity notice.

`CATALOG.json` identifies each DOI and original PDF. `SOURCE_PROVENANCE.json`
records source and released hashes, including explicit bookkeeping-only
transformations. `SHA256SUMS.json` lists the released files. No credentials,
customer exports, unrelated private projects or new paid API runs are included.
The empirical scope and unavailable/uncollected evidence are stated per paper.

From this directory, verify the complete release and recompute the recorded
benchmark summaries using Python 3.10 or later, without provider API calls:

```sh
python3 verify_release.py
```

This checks the released file identities, the historical 17-file seal, the
2,990 recorded decisions, the 600-row log provenance, the masked-study
denominators, the four pinned RE-Bench inputs and the mathematical supplement's
inner checksums. Per-paper READMEs give additional reproduction commands.
Artifact integrity is separate from independent replication and scientific
validation.
