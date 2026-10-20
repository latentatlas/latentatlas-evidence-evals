# RE-Bench source-contract review changelog

## 2026-10-21 — upstream status note (20 October 2026 decision)

METR has [deprecated the RE-Bench tasks](https://github.com/METR/RE-Bench/commit/a0cc6d4a91b20f84ebef505d5c72358f88b3b389)
and [archived the original repository](https://github.com/METR/RE-Bench), stating
that contributions and bug reports are no longer accepted. This review concerns
the fixed upstream revision
[`93b98062e55f6945d4a7e213a3226dd419896170`](https://github.com/METR/RE-Bench/tree/93b98062e55f6945d4a7e213a3226dd419896170)
and retains its original evidence cutoff of 25 August 2026.

[Issue #44](https://github.com/METR/RE-Bench/issues/44), opened on 28 September
2026 to report the documented L1 / implemented norm discrepancy, was closed as
“not planned” on 20 October without a technical response. The public record does
not establish a causal connection between this report and the deprecation
decision. Neither the deprecation nor the issue closure constitutes independent
validation or refutation of this review’s findings.

The original v0.1 manuscript and its evidential scope remain unchanged. This is
a dated status addendum to the
[LatentAtlas publication page](https://latentatlas.ai/research/re-bench-systems-benchmark/#upstream-status)
and this changelog. The v0.1 PDF, DOI, citation files and archived research
artifacts are unchanged.

## 2026-08-25 — public working review v0.1

- Published an unaffiliated, AI-assisted pinned-source review of RE-Bench.
- Labelled the work not peer reviewed, not independently adjudicated, and not
  an independent benchmark or headline-score reproduction.
- Recorded the owner's decision to publish before independent human review;
  future review remains an assurance upgrade rather than a v0.1 release gate.
- Added exact paper, release, refresh, pinned-source, and later-evaluation
  evidence surfaces.
- Published three source-contract findings: selected Kernel timing and contract
  drift; the Scaling Law static curve and one-sided FLOP gate; and the LLM
  Foundry norm mismatch and parameter-proxy boundary.
- Added an eight-test bounded contract-check receipt over four hash-pinned
  public files.
- Published the audit-only `numpy==2.3.5` dependency pin, an exact clean-venv
  rerun command, and a fail-fast missing-dependency message.
- After separate AI-assisted editorial, methodological, and outside-reader
  passes, corrected the `score@k` exception, conditional runtime wording,
  suite-level artifact interpretation, duplicate-key suite scope, and 2025
  reward-hacking qualifiers.
- Conditioned Kernel timing language on the presence of a valid registered
  score, exposed the all-invalid `NaN -> 0` fallback, and replaced unsupported
  “near-ceiling” wording with “high normalized performance.”
- Preserved the exact historical-to-pinned mapping gap and prohibited backward
  transfer of current source findings to the 2024 paper runs.
- Kept separate exploratory theory work outside the evidence base for this
  review.
