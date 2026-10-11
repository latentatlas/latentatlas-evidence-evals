# RE-Bench source-contract review changelog

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
