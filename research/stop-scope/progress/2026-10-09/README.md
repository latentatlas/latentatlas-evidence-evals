# Stop Scope — Research progress and evidence snapshot

**9 October 2026 · v0.1.0 · Huseyin Buldurgan, Independent Researcher**

Status: development evidence and component qualification; not a preregistered pilot or a replacement manuscript. [Türkçe kısa özet](README_TR.md).

**Research question:** What evidence supports a claim that a stopped task can no longer produce effects, while newly authorized and independent work can still proceed?

The [Apart sprint paper](https://apartresearch.com/sprints/projects/verifying-stop-scope-in-agent-workflows-lpj9) compared cancellation, waiting for worker completion, and origin-scoped file-write control. This snapshot adds inspectable progress on two questions: which work an additional cancellation actually targets, and what a scoped stop confirmation must establish. A small, separate live-model development set checks task completion and response to an explicit stop message.

## What is available now

| Evidence set | Included records | Result within the tested setting |
|---|---:|---|
| Live A development, 6 October | 3 healthy + 5 stop episodes; 27 provider requests | All three healthy episodes produced correct final reports. The five stop episodes produced no post-stop tool call or final file. Author-reviewed responses contained acknowledgement and file status, not final analysis results. |
| Scoped waiting and confirmation, 9 October | 16 programmed conditions | Waiting for the recorded workers to finish and closing the route for later old-origin work were distinguishable. The verifier also rejected an intentionally false confirmation whose inventory omitted a live worker, even though no late file was produced. |
| Cancellation-target preflight, 9 October | 8 programmed conditions | After source stop, cancelling the saved old run returned 404; refreshing active targets selected the new summary run and returned 204. The previously accepted native write completed in both cases. |

The two local matrices preserve legitimate new work **N** and independent work **I**: their final file hashes match their healthy references in all **40 non-reference role comparisons** (28 + 12). These are matched file comparisons, not independent statistical samples.

The practical distinction is between **a stop request, the scope it targets, remaining effects, and evidence for a completion claim**. A missing final file alone cannot establish that every relevant worker has stopped. Conversely, a confirmation that currently recorded workers finished does not close future admissions from the same origin.

## How to inspect it

1. Read the [claim–evidence map](CLAIMS.md), including the intentionally failing controls.
2. Inspect [recomputed findings](FINDINGS.json), [live responses and author reviews](data/live/AUTHOR_REVIEWS.json), and [method and selection details](METHODS_AND_SCOPE.md).
3. Browse the frozen [confirmation code](source/confirmation) and [cancellation code](source/cancellation). Full event streams and native file bytes are in [data](data); compressed event streams are included, not external download placeholders.
4. Recompute the snapshot using Python 3.11 or newer:

```sh
cd research/stop-scope/progress/2026-10-09
python3 -B verify_snapshot.py
python3 -B -m unittest test_snapshot -v
```

No account, API key, network request, model call, or framework installation is needed. See [replay and sharing details](REPRODUCTION.md).

## Scope and next work

The live set is exploratory: one reported model identifier (`gpt-6-astra`), the ChatGPT-plan preview route, two development inputs, and a short recorded observation window. It did not challenge the write gate with a live continuation attempt. The 24 native conditions use programmed actors, a trusted local runtime and a research-owned file queue; they qualify controls rather than measure model resistance. These selected sets neither complete the **286-case design** nor constitute independent replication. Other S/N and queue-development work remains outside this release.

The next task is to integrate the original F07 arms without conflating saved-target cancellation, waiting, admission control, effect control, and confirmation. Their claim scope must stay fixed across comparisons. Reversed native-effect order and a fresh same-protocol repeat follow. Broader child, scheduling and recovery mechanisms retain their own evidence requirements; deeper behavioral stress testing remains a later branch. The [dated open-requirements record](historical/open_requirements_2026_10_09.json) preserves these gaps.

## Version and provenance

Reference this snapshot as `stop-scope-progress-2026-10-09-v0.1.0`. It leaves the [original supplement](https://github.com/latentatlas/latentatlas-evidence-evals/releases/tag/stop-scope-supplement-v1.0.0) and [v1.1.0 browsable sprint export](https://github.com/latentatlas/latentatlas-evidence-evals/tree/stop-scope-review-export-v1.1.0/research/stop-scope) unchanged. Snapshot versions are separate from paper versions.

[EXPORT_MANIFEST.json](EXPORT_MANIFEST.json) maps sharing files to retained source digests. Local personal paths, account/authorization metadata, opaque duplicate transport and reasoning items were removed from the public copy. Original records were retained unchanged. Research direction and author reviews are Huseyin Buldurgan's; implementation, checks and this progress text used LLM assistance. Automated replay is not an independent human review.
