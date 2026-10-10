# LatentAtlas P0 Empirical Finding Pack

Generated at: `2026-07-13T08:03:07.494785+00:00`
Freeze id: `p0_review_freeze_6c1465ff0c315da6`
Freeze hash: `738101038e03bd8d0fe4b1b24c69907ed5ce561226f758ae115fe64c674fb2a3`

## Boundary

This is a descriptive empirical finding pack over a frozen masked P0 human-review set. It is not a population probability claim and does not mutate production truth.

## Denominators

- `p0_rows`: `151`
- `outcome_ready_p0_rows`: `146`
- `frozen_reviewed_rows`: `146`
- `resolved_reviewed_rows`: `121`
- `insufficient_for_outcome_adjudication_p0_rows`: `5`

## Outcome Distribution

- `correct_block`: `99` (0.6781)
- `false_block`: `22` (0.1507)
- `needs_more_evidence`: `25` (0.1712)

## Metrics

- `review_completion`: `146/146` rate=`1.0`, Wilson95=`0.9744-1.0`
- `correct_block_all_reviewed`: `99/146` rate=`0.6781`, Wilson95=`0.5986-0.7485`
- `false_block_all_reviewed`: `22/146` rate=`0.1507`, Wilson95=`0.1017-0.2176`
- `needs_more_evidence_all_reviewed`: `25/146` rate=`0.1712`, Wilson95=`0.1188-0.2406`
- `correct_block_resolved_only`: `99/121` rate=`0.8182`, Wilson95=`0.74-0.8768`
- `false_block_resolved_only`: `22/121` rate=`0.1818`, Wilson95=`0.1232-0.26`
- `identity_conflict_correct_block`: `4/4` rate=`1.0`, Wilson95=`0.5101-1.0`
- `blocked_pdp_needs_more_evidence`: `7/7` rate=`1.0`, Wilson95=`0.6457-1.0`
- `latest_pdp_temporal_false_block`: `14/48` rate=`0.2917`, Wilson95=`0.1824-0.4318`

## Finding Cards

### `F1_review_complete`

146 of 146 P0 outcome-ready packets were reviewed and frozen.

- evidence: `freeze_summary + frozen_rows`
- boundary: Review completeness only.

### `F2_outcome_distribution`

Outcome distribution: correct_block=99, false_block=22, needs_more_evidence=25.

- evidence: `frozen_rows.reviewed_outcome`
- boundary: Frozen-set descriptive distribution only.

### `F3_resolved_vs_unresolved`

121 packets were resolved and 25 remained evidence-insufficient.

- evidence: `resolved outcome taxonomy`
- boundary: Unresolved cases are not coerced into binary success/failure.

### `F4_identity_conflict`

4 of 4 identity_conflict_masked packets were labeled correct_block.

- evidence: `observed_change_type=identity_conflict_masked`
- boundary: Pattern-specific observation, not universal identity-guard accuracy.

### `F5_blocked_pdp_boundary`

7 of 7 blocked_pdp packets remained needs_more_evidence.

- evidence: `operator_visual_verdict=blocked_pdp`
- boundary: Blocked PDP supports evidence insufficiency, not correctness or falseness.

### `F6_temporal_authority`

14 of 48 latest-PDP temporal-authority packets were labeled false_block.

- evidence: `pdp_temporal_authority_evidence=latest_pdp_review_pool_snapshot_present`
- boundary: Requires packet-visible temporal authority evidence.

## Level 4 Missing

- independent second reviewer and inter-rater agreement
- pre-declared random or stratified sampling frame beyond P0 reviewed packets
- workflow-family denominators and unresolved-case treatment
- holdout or later-period replication
- claim approval separating descriptive frozen-set rates from population probability

## Claim Boundary

Allowed:
- A completed masked P0 human-review outcome set was frozen.
- The frozen set has descriptive empirical outcome counts and rates.
- Pattern-level findings can be reported with explicit denominators.

Blocked:
- These rates are population probabilities.
- The review proves general system accuracy.
- Unresolved needs_more_evidence rows are failures or successes.
- The pack mutates production truth or customer-facing output.
