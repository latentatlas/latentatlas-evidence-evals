# RE-Bench source-contract review v0.1

This directory contains an unaffiliated, AI-assisted technical review of
RE-Bench. It is a version-bounded public working review, not a new benchmark
result, a peer-reviewed paper, an independent reproduction, or an artifact
endorsed by METR or the paper authors.

**Publisher and maintainer:** [LatentAtlas](https://github.com/latentatlas).
Corrections can be submitted through the repository's [issue tracker](https://github.com/latentatlas/latentatlas-evidence-evals/issues).

## Start here

- [Reader-facing review](re-bench-systems-benchmark-review-v0-1.md)
- [Methods and evidence manifest](evidence-manifest-v0-1.md)
- [Bounded contract checks](contract_checks_v0_1.py)
- [Audit-only dependency pin](requirements-audit.txt)
- [Contract-check receipt](contract-audit-result-v0-1.md)
- [Changelog](changelog.md)
- [Release checksums](SHA256SUMS)

## What is new here

The review combines three source-level findings under one evidence discipline:

1. when a valid score exists, the pinned Kernel package selects one registered
   single-call timing; an all-invalid aggregate instead becomes numeric `0`,
   and the public package also has documentation and aggregation drift;
2. the pinned Scaling Law evaluator scores JSON against an embedded curve
   without executing the proposed target-scale training run; and
3. the pinned LLM Foundry gate uses a sum of per-tensor norms rather than the
   declared global L1 quantity, while parameter distance remains narrower than
   behavioral equivalence.

All findings are scoped to the pinned public source. The exact mapping to the
historical paper-run environments remains unresolved.

## Reproduce the bounded checks

The core LatentAtlas package remains dependency-free. This optional audit
script separately requires Python 3.11 or newer and NumPy `2.3.5`.

```bash
python3 -m venv .venv-rebench-audit
.venv-rebench-audit/bin/python -m pip install \
  -r docs/re-bench/requirements-audit.txt
.venv-rebench-audit/bin/python docs/re-bench/contract_checks_v0_1.py \
  --source-root /path/to/METR-RE-Bench
```

## Assurance state

The owner authorized public release on 2026-08-25 without prior independent
human adjudication. Independent review remains welcome as a future assurance
upgrade. Until that happens, this package must remain labelled AI-assisted,
not peer reviewed, not independently adjudicated, and not an independent
benchmark reproduction.
