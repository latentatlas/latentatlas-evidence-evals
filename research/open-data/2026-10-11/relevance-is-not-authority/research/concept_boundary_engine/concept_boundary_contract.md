# Concept Boundary Contract

Status: seed contract  
Date: 2026-05-12

## Boundary Types

| boundary_type | Meaning | Authority granted |
| --- | --- | --- |
| `related` | The candidate shares terms, topic, or semantic neighborhood. | Discovery only. |
| `same_identity` | Required identity slots match and no variant collision is present. | Identity candidate; evidence still required. |
| `evidence_support` | Source text directly supports the claim with current authority. | Answer support; not action by itself. |
| `peer_comparison` | Similar object or market peer, not the same identity. | Comparison only. |
| `bridge_context` | Landing page, glossary, index, trend, or navigation context. | Context only. |
| `contradiction` | Candidate directly conflicts with the requested claim. | Block or manual review. |
| `action_ready` | Evidence, authority, freshness, and action contract all pass. | Governed action allowed. |
| `publish_safe` | Action-ready plus publish/customer-surface gates pass. | Governed publish allowed. |
| `privacy_blocked` | Sensitive or customer data boundary is crossed. | Stop until reviewed. |

## Core Rule

The requested authority must be less than or equal to the granted authority.

Examples:

- `related` cannot answer a factual claim.
- `peer_comparison` cannot prove identity.
- `evidence_support` cannot trigger customer action.
- `action_ready` cannot become `publish_safe` without publish checks.
- `privacy_blocked` stops all downstream use.

## Required Decision Fields

Every decision row must include:

- `case_id`
- `requested_authority`
- `boundary_type`
- `similarity_score`
- `source_authority`
- `freshness_state`
- `action_scope`
- `expected_decision`
- `boundary_decision`
- `reason_code`
- `authority_transfer_allowed`
- `truth_mutation_allowed`
- `customer_surface_mutation_allowed`

## Stop Conditions

Stop if:

- requested authority exceeds granted boundary authority
- source authority is unknown, low, stale, draft, or deprecated
- action is requested but action scope is absent
- publish/customer output is requested without publish-safe status
- sensitive or private data is present
- the case is only a bridge, peer, or related context

