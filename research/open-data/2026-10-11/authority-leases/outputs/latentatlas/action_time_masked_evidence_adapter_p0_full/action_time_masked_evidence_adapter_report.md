# LatentAtlas Action-Time Masked Evidence Adapter

Generated at: `2026-07-13T01:29:38.291477+00:00`

## Boundary

This adapter merges only allowed masked evidence sidecar fields into V2 review packets. It does not read the internal index, call external services, execute actions, or mutate production truth.

## Summary

- status: `pass`
- adapter status: `merged_sidecar`
- input V2 packets: `2614`
- P0 packets: `151`
- sidecar rows: `151`
- merged packets: `151`
- outcome-adjudication allowed: `146`
- outcome-adjudication blocked: `2468`
- sidecar validation: `pass`

## Packet Sufficiency Counts

- `insufficient_for_outcome_adjudication`: `2468`
- `sufficient_for_outcome_adjudication`: `146`

## Missing Outcome-Evidence Fields

- `decision_causal_link`: `2463`
- `lease_validity_relationship`: `2463`
- `masked_state_after`: `2463`
- `masked_state_before`: `2463`
- `observed_change_type`: `2463`
- `pdp_temporal_authority_evidence`: `2463`
- `reviewer_visible_contradiction_marker`: `2463`
- `reviewer_visible_insufficiency_marker`: `2463`

## Claim Boundary

- allowed: Masked evidence sidecar readiness or merge status was measured.
- not claimed: The adapter does not prove outcomes unless sufficient masked evidence is present.
