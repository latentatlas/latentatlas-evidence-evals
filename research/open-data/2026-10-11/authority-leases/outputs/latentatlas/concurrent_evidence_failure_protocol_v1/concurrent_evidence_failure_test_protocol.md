# Concurrent Evidence Failure Test Protocol

Generated at: `2026-07-16T21:04:19.486266+00:00`
Status: `pass`

## Boundary

This is a Level 3.5 test protocol. It defines what to measure next; it does not claim Level 4 probability, broader population rates, production readiness, or customer-facing verdict authority.

## Core Claim

Many agentic AI failures are evidence-concurrency failures: the model acts on observations whose identity, freshness, authority, or materialization timing no longer align.

## Family Tests

| Family | Local Count | Positive Test | Negative Control | Promotion Gate |
| --- | --- | --- | --- | --- |
| `stale_read` | 14/48 | Decision used an older PDP, screenshot, cache, or state snapshot while a newer packet-visible state superseded it. | Current evidence timestamp is newer than or equal to action time, identity is stable, and no newer superseding record exists. | Baseline replay comparing stale-read policy vs action-time freshness policy. |
| `identity_time_split` | 4/4 | Packet-visible identity conflict exists between evidence capture and action-time target identity. | Stable canonical identity across capture, review packet, and action target with no conflicting aliases. | Independent reviewer agreement on identity-conflict labels and ambiguous-identity quarantine handling. |
| `authority_expiry` | 25/146 | Risk signal or prior decision is present, but packet-visible authority is expired, missing, or unresolved at action time. | Lease-like authority fields are present, unexpired, permission-stable, and policy-stable at action time. | Pre-registered unresolved-case treatment and second-reviewer agreement for needs_more_evidence rows. |
| `materialization_race` | 14/48 | Price, availability, seller, stock, or workflow state changes while the decision is being materialized. | Materialized output matches the latest packet-visible state and no later conflicting state appears before action. | Action-type stratification and replay of manual-review-before-materialization baseline. |
| `visibility_truth_confusion` | 7/7 | Blocked access, timeout, empty page, or unavailable visibility is treated as product/workflow truth. | Fresh accessible page or independent source confirms the product/workflow state after visibility is restored. | Negative controls proving blocked visibility is not counted as correctness or falseness without fresh proof. |
| `context_contamination` | 0/0 | Reviewer or model imports outside memory, jargon, or ontology not present in the packet. | Reviewer rationale cites only packet-visible fields and uses no non-packet factual additions. | Grounding audit before any external mini-review label can enter adjudication. |

## Execution Order

1. Add required evidence fields to the masked review packet schema.
2. Build negative-control fixtures for every family before expanding counts.
3. Run baseline replay for stale_read and materialization_race.
4. Collect second-reviewer agreement before any reliability language.
5. Only then consider Level 4 promotion review.

## Blocked Claims

- Broader concurrency failure rates.
- Level 4 population probability.
- External mini-review labels without grounding audit.
- Production truth mutation or customer-facing verdict generation.
