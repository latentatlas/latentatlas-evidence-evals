# R17 — Joint review of R15–R16 and focused literature comparison

This package adds no research theorem. It preserves the certified
constants, expands two analytic explanations, corrects one sentence
about a finite versus infinite sum, and records a limited primary-source
comparison. No retraction-level error was found in the reviewed scope;
external review and literature priority remain open.

- [Turkish audit report](DENETIM_RAPORU.md).
- [27-claim review](CLAIM_REVIEW.md).
- [Proof clarifications and wording correction](PROOF_ADDENDUM.md).
- [Literature comparison](LITERATURE.md), [search/access record](SEARCH_LOG.md).
- [Proposed manuscript contribution](MANUSCRIPT_POSITION.md).
- [Fresh computation replay](replays/report.json), [all jobs](replays/runs.json).
- [Targeted independent exact checks](results/review_algebra.json).
- [Closure audit](audit_report.json), [frozen package](manifest.json).

## Verify existing evidence

From the research/project root, using the recorded math environment:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/slope_chain_review/audit_snapshot.py
```

The closure verifier uses the Python standard library. It checks source,
input, output and manifest identities, reconstructs replay comparisons,
and checks that documentation links exist. It does not certify the
analytic review or the literature conclusions by itself. Do not use -O.

## Recompute without modifying frozen files

```sh
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/slope_chain_review/replay_chain.py --output-dir /tmp/r17-fresh-replay
PYTHONDONTWRITEBYTECODE=1 .venv-math/bin/python research/slope_chain_review/check_review_algebra.py --output /tmp/r17-fresh-algebra.json
```

Both refuse existing destinations. The first needs python-flint and
mpmath, recorded in replays/inputs.json. It makes and removes its own
temporary research tree and installs fresh results before dependent
checks. The second needs only Python's standard library. The original
R15/R16 results and earlier certificates are never overwritten.

The replay runner verifies every other frozen package found beside it;
future additional packages may increase its preservation counts. The
recorded R17 review covers the 17 preceding manifests and 811 entries.

Evidence distinction: exact arithmetic checks and identical output
replay are confirmed computations; the mathematical proof review and
the literature mapping are reasoned assessments of explicitly stated
scope. They are not an external referee report or a formal proof.
