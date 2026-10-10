# Concurrency Reviewer Strategy Policy

Generated at: `2026-07-18T16:41:28.671413+00:00`

## Decision

Free full reviewer acquisition is no longer the primary blocking path for the concurrency workstream.

Mini-reviews, paid-consulting-shaped replies, referrals, and informal comments may be logged only as qualitative method-fit or grounding signals. They do not count as reviewer02 completion, inter-reviewer agreement, kappa, Level 4 evidence, or population probability support.

## Current Reviewer State

| Signal | State |
| --- | --- |
| Full reviewer02 | waiting_for_second_reviewer |
| Agreement calculable | False |
| P0 reviewer02 rows | 0 complete / 146 missing |
| Independent reviews | 386/3000 |
| Decision | do_not_count_mini_review_or_paid_consulting_replies_as_level4_reviewer02_evidence |

## Allowed Use

- Use internal replication, schema enforcement, negative controls, and local replay now.
- If a mini-review response arrives, audit every rationale for packet-only grounding.
- Count external labels only if the exact full reviewer02 scope, response sheet, and validation gates are satisfied.

## Blocked Use

- Do not call mini-review a second review.
- Do not compute agreement or kappa from informal responses.
- Do not use consulting discovery calls as evidence labels.
- Do not promote Level 4 or population claims without the Level 4 gates.
