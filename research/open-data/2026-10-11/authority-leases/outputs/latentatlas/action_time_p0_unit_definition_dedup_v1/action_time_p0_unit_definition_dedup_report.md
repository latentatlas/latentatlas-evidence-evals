# Action-Time P0 Unit Definition And Dedup Audit

Generated at: `2026-07-13T13:39:49.307479+00:00`
Status: `pass`
Freeze id: `p0_review_freeze_6c1465ff0c315da6`
Freeze hash: `738101038e03bd8d0fe4b1b24c69907ed5ce561226f758ae115fe64c674fb2a3`

## Unit Decision

- Current Paper A primary unit: `action_attempt_event`
- Level 4 sensitivity unit: `subject_cluster`
- Second-reviewer gate: `ready_for_second_reviewer_queue`

## Denominators

- event-level count: `146`
- subject-cluster count: `146`
- subject/event ratio: `1.0`
- workflow-family count: `3`
- duplicate subject clusters: `0`
- missing subject cluster hash: `0`

## Unit Definitions

### `action_attempt_event`

- key fields: `queue_id,event_id,action_type`
- current count: `146`
- recommended use: Primary unit for the current frozen P0 descriptive Paper A denominator.
- boundary: Descriptive frozen-set unit; not a population probability denominator.

### `subject_cluster`

- key fields: `subject_cluster_hash`
- current count: `146`
- recommended use: Independence sensitivity denominator before Level 4 probability language.
- boundary: If lower than event count, report both and pre-register duplicate treatment.

### `workflow_family`

- key fields: `action_type`
- current count: `3`
- recommended use: Stratification axis, not a denominator by itself.
- boundary: Do not use workflow-family count as event or subject denominator.

## Duplicate Or Missing Subject Clusters

No duplicate or missing subject clusters in the frozen P0 reviewed set.

## Claim Boundary

This artifact defines denominator policy for the frozen P0 set. It does not create a population probability claim and does not mutate production truth.
