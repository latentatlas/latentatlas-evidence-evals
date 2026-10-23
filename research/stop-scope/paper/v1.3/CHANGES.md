# v1.3 revision record — 23 October 2026

## Changes to presentation and interpretation

1. The abstract, introduction and related-work positioning state the contribution as paired, auditable counterexamples to overly broad stop claims. They do not claim a new revocation principle, priority over related work, or an implemented comparison with SOUNDGATE or root-scoped quiescence.
2. Figure 1 makes the event order explicit: accepted operations, O-run interruption, S-summary delivery, receiver control and clean restart, resumed work/follow-ups, then audit. S delivers before receiver control. The healthy-arm differences are stated below the figure.
3. Programmed follow-ups are called **F** in the manuscript. Their archived role remains **C**. The original R/V/C requirement names and all raw records are unchanged.
4. Table 2 shows I/N byte-level reference matches beside the O/F effect counts. Provider request counts remain in the adjacent text.
5. Table 3 reports the observed outcomes of ineffective revocation, broad revocation, a missing native receipt and incorrect content, together with the corresponding audit interpretation. All four are tied to their actual condition identities by `verify_revision.py`.
6. Repeated framing was shortened; the author decisions and the role of AI assistance remain explicit. The one-host, one-model, development-stage scope and open independent-validation work remain visible.

## Unchanged empirical basis

| Evidence layer | Retained scope |
| --- | --- |
| Original study | 26 programmed conditions plus 26 same-host repeat executions |
| Live persistence comparison | 5 episodes; 64 archived requests; 8 I/N reference matches; 4 author-reviewed summaries |
| Provider-free receiver example | 12 main cells plus 4 fault checks; 15 recorded and 1 needs_review; 18 main-cell I/N reference matches |
| Dated catalogue assessment | 286 identities; 29 with direct evidence; 68 with direct or partial evidence including those 29; 0 formal catalogue acceptances |

No new model call, task, seed, model, host or catalogue acceptance is added to the reported study. Offline verification and any automated provider-free regression rerun are checks of the package, not extra scientific observations pooled into these counts.

## Retained evidence identities

- Previous release: `stop-scope-research-v1.2.0`, commit `a28ab93bb998c11b7d8d976ce1c6ebcce6d76d78`.
- Previous paper PDF SHA-256: `b200aa36757287ffea6aaf5157c5c41e718f1bd9a96551c140f487a270aee9f8`.
- Frozen evidence and coverage: `research/stop-scope/progress/2026-10-16/`.
- Original sprint release: `stop-scope-supplement-v1.0.0`.

The release keeps those files byte-for-byte. Revision-specific files are added under `paper/v1.3/`; navigation and CI are updated to expose and check them. The v1.3 PDF/Word are research preprint artifacts, not a new journal acceptance or a completed 286-case benchmark.
