# Authority-Action v0.5 Preliminary Human Review

Review date: 2026-07-26

This is a first-pass author review, not an independent review. It checks whether
the generated cases are coherent enough for a paid pilot and records remaining
risks before empirical use.

## Review outcome

- All 25 groups preserve a single requested action and complete 2x2 structure.
- All invalid cells map to one intended reason code.
- Treatment text does not alter authority facts.
- Eighty cases require hard or very-hard multi-record reasoning.
- Direct conclusion phrases found in v0.4 were removed.
- Monitoring direction is balanced and separately encoded.

## Group inventory

| Group | Family | Difficulty | Primary reasoning |
|---|---|---|---|
| pressure_incident_publication | pressure | hard | role resolution, actor scope, record status |
| pressure_customer_appeal | pressure | very hard | time boundary, pending renewal, scope distractor |
| pressure_staging_feature | pressure | hard | approval policy, two-signature finality |
| pressure_sandbox_refund | pressure | medium | request amount versus granted amount |
| pressure_dataset_export | pressure | very hard | alias versus immutable digest |
| pressure_test_account_quarantine | pressure | hard | ledger order and target-specific revocation |
| pressure_trial_vendor | pressure | very hard | signature trust and canonical digest provenance |
| evaluation_dataset_release | evaluation awareness | hard | activation time and version scope |
| evaluation_model_card | evaluation awareness | medium | two-signature publication state |
| evaluation_ticket_resolution | evaluation awareness | hard | on-call role at the current time |
| evaluation_sandbox_capability | evaluation awareness | very hard | equal content but distinct immutable target |
| evaluation_review_report | evaluation awareness | hard | equal-rank current conflict |
| evaluation_trace_archive | evaluation awareness | hard | supersession chain |
| monitoring_sandbox_credential | monitoring | very hard | timezone normalization and expiry boundary |
| monitoring_demo_account | monitoring | medium | current on-call actor |
| monitoring_canary_deploy | monitoring | medium | release plan versus authorization parameter |
| monitoring_audit_export | monitoring | hard | time-window digest and target binding |
| monitoring_dashboard_publication | monitoring | hard | preview state versus releasable state |
| monitoring_incident_closure | monitoring | very hard | near-target revocation distractor and ledger order |
| incentive_priority_ticket | incentive shift | hard | annotation versus signed source chain |
| incentive_sandbox_credit | incentive shift | medium | requested amount versus grant amount |
| incentive_research_snapshot | incentive shift | very hard | timezone activation and version scope |
| incentive_test_quota | incentive shift | hard | canonical service identity |
| incentive_vendor_trial | incentive shift | hard | equal-rank unresolved conflict |
| incentive_archive_batch | incentive shift | very hard | supersession chain and near-target distractor |

## Remaining gates

The dataset is ready for a small discrimination pilot, not yet for a full run.
The pilot must determine whether medium, hard, and very-hard cells produce a
useful performance gradient without creating systematic ambiguity or provider
refusal. Any changed case must be released under a new dataset hash.
