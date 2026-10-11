# Level 4 Weak-Strata Fill Plan

Status: `pass`
Generated at: `2026-07-15T17:15:18.012715+00:00`

## Boundary

This plan identifies masked source-collection and review targets. It does not create data, mark rows reviewed, compute Level 4 readiness, publish claims, or mutate production truth.

## Counts

- total stratum target rows: `5`
- independent-review stratum target rows: `7`
- sum of total stratum gaps, not additive: `229`
- sum of independent-review gaps, not additive: `518`
- additional eligible source events needed for 5,000 target: `542`
- Level 4 probability claim allowed: `false`

The gap sums are not additive because a single masked event can fill multiple strata at once.

## Priority Targets

| Target | Source | Current | Gap | Priority | Collection lane | Negative controls |
| --- | --- | ---: | ---: | --- | --- | ---: |
| `action_type=confirm_visual_price_before_update` | `independent_review` | 1 | 99 | `P0` | `visual_price_before_update_shadow_event` | 10 |
| `action_type=resolve_official_truth_identity_guard` | `total` | 4 | 96 | `P0` | `official_truth_identity_guard_shadow_event` | 10 |
| `exposure_band=material` | `independent_review` | 8 | 92 | `P0` | `material_exposure_shadow_event` | 10 |
| `likelihood_band=possible` | `independent_review` | 8 | 92 | `P0` | `possible_likelihood_shadow_event` | 10 |
| `action_type=resolve_seller_comparability_before_materialization` | `independent_review` | 20 | 80 | `P1` | `seller_comparability_shadow_event` | 8 |
| `action_type=confirm_offer_condition_comparability` | `independent_review` | 25 | 75 | `P1` | `condition_comparability_shadow_event` | 8 |
| `action_type=confirm_offer_condition_comparability` | `total` | 25 | 75 | `P1` | `condition_comparability_shadow_event` | 8 |
| `action_type=recheck_identity_and_source_before_materialization` | `independent_review` | 29 | 71 | `P1` | `identity_source_recheck_shadow_event` | 8 |
| `action_type=manual_review_before_materialization` | `total` | 52 | 48 | `P2` | `manual_review_before_materialization_shadow_event` | 5 |
| `timing=scheduled` | `independent_review` | 91 | 9 | `P2` | `scheduled_action_shadow_event` | 5 |
| `action_type=recheck_primary_offer_availability` | `total` | 95 | 5 | `P2` | `availability_recheck_shadow_event` | 5 |
| `timing=scheduled` | `total` | 95 | 5 | `P2` | `scheduled_action_shadow_event` | 5 |

## Claim Boundary

- allowed: describe which strata are under-covered and what masked events would fill them.
- not allowed: claiming the missing events exist, claiming reviewed coverage before review intake, or making Level 4 probability claims.
