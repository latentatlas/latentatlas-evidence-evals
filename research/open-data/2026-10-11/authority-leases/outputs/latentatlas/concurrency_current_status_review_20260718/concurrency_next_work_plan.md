# Concurrency Next Work Plan

Generated at: `2026-07-18T05:16:59.095818+00:00`
Recommended start: `schema_required_fields`

| Step | Workstream | Objective | Deliverable | Acceptance |
| --- | --- | --- | --- | --- |
| 1 | `schema_required_fields` | Make every concurrency family measurable from packet-visible evidence. | Masked packet schema extension plus validation failure report. | Rows missing family-required fields fail fast and remain excluded from stronger claims. |
| 2 | `negative_control_fixtures` | Prove the detector does not call every temporal mismatch a concurrency failure. | Negative-control fixture CSV/JSON plus unit tests. | Each family has at least one passing negative control and one failing positive fixture. |
| 3 | `baseline_replay` | Measure decision-time-only vs action-time freshness policy behavior. | Replay report for stale_read and materialization_race. | Replay outputs deltas by action_type and keeps unresolved cases separate. |
| 4 | `stratified_backfill_review` | Fill weak families and strata without overclaiming. | Active sampling plan and validated batch review outputs. | Meaningful family/stratum floors are met before any stronger rate language. |
| 5 | `reviewer_strategy_pivot` | Stop waiting for free full reviewer while preserving external validation path. | Reviewer path policy: internal replication first, blind micro-reviews as qualitative only, partner/paid review later if budgeted. | No mini-review, consulting reply, or referral is counted as Level 4 reviewer02 evidence. |

## Reviewer Strategy

Do not keep waiting for a free full reviewer as the main path. Continue with internal replication, schema enforcement, negative controls, and replay. Treat external mini-review replies as qualitative grounding signals unless they return a validated full reviewer02 response sheet.
