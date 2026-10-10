# Concurrent Evidence Failure

Status: Level 3.5 research track
Generated at: `2026-07-16T10:48:28.158394+00:00`
Level 4 probability claim allowed: `false`

## Short Claim

```text
Many agentic AI failures are evidence-concurrency failures: the model acts on observations whose identity, freshness, authority, or materialization timing no longer align.
```

## Why It Matters

A model can use a true observation at the wrong action boundary. The failure is not simply bad reasoning; it is a mismatch between evidence time, target identity, authority, and materialization state.

## Local Frozen-Set Signals

| Family | Local Count | Local Rate | Observation | Boundary |
| --- | --- | --- | --- | --- |
| `stale_read` | 14/48 | 0.2917 | Latest-PDP temporal-authority packets produced local false-block observations where newer evidence superseded stale state. | Temporal-authority observation in frozen P0 only. |
| `identity_time_split` | 4/4 | 1.0000 | Packet-visible identity conflicts supported block-grade outcomes in the frozen P0 set. | Pattern-specific observation; not universal identity-guard accuracy. |
| `authority_expiry` | 25/146 | 0.1712 | Evidence-insufficient rows show that risk or prior state cannot be promoted into action authority without revalidation. | Descriptive unresolved-evidence rate only; not an error rate. |
| `materialization_race` | 14/48 | 0.2917 | Manual-review-before-materialization packets split across outcomes, showing that action-time state can change the verdict. | Local action-type observation; not a general materialization failure rate. |
| `visibility_truth_confusion` | 7/7 | 1.0000 | Blocked PDP cases stayed evidence-insufficient instead of being treated as product truth. | Blocked access is evidence state, not outcome truth. |
| `context_contamination` | qualitative | n/a | External mini-reviews are usable only after a grounding audit detects non-packet facts or imported ontology. | Qualitative protocol guard; no counted denominator in the frozen P0 pack. |

## Failure Family Definitions

- `stale_read`: A prior PDP, screenshot, cache, or state observation is treated as current action evidence. Test: Latest temporal-authority packets should expose false-block cases when a newer record supersedes stale state.
- `identity_time_split`: The target identity changes or conflicts between evidence capture and action-time judgment. Test: Explicit packet-visible identity conflicts should route to block-grade decisions; ambiguous identity should stay unresolved.
- `authority_expiry`: A risk signal or prior decision no longer authorizes the later action without revalidation. Test: Risk signals should prioritize review but should not become outcome evidence without packet-visible authority.
- `materialization_race`: Price, availability, seller, or workflow state changes while the decision is being materialized. Test: Manual-review/materialization packets should split across correct_block, false_block, and needs_more_evidence rather than collapse into one label.
- `visibility_truth_confusion`: Blocked access, timeout, empty page, or unavailable visibility is mistaken for product or workflow truth. Test: Blocked PDP cases should remain needs_more_evidence unless fresh unblock or outcome proof is visible.
- `context_contamination`: A reviewer or model imports outside memory, jargon, or domain ontology and replaces packet-visible evidence. Test: External mini-review responses with non-packet facts should be invalid for adjudication but useful as grounding-failure examples.

## Claim Boundary

Allowed:
- Concurrent Evidence Failure is a Level 3.5 research track grounded in frozen P0 observations.
- Local denominators can be reported with explicit frozen-set boundaries.
- Failure families can be used to define next tests, strata, and negative controls.

Blocked:
- Concurrency failure rates are known for a broader population.
- The frozen P0 set reaches Level 4 probability evidence.
- Qualitative mini-review contamination is an empirical outcome label.
- needs_more_evidence rows are successes or failures.

## Next Tests

- Stratify by action_type, temporal authority, operator visual verdict, and identity flag profile.
- Add baseline replay for stale-read and decision-time-only policies.
- Audit micro-review responses for context contamination before any label ingestion.
- Define negative controls where true evidence is current, identity-stable, and action-authorized.
