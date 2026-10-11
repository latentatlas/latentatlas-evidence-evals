# LatentAtlas Action-Time P0 Reviewer Pack v1

## Purpose

This is a blind second-review pack for the frozen masked P0 action-time set. The reviewer sees masked packet evidence and writes an independent outcome label. The pack does not expose reviewer01 labels, raw source rows, URLs, customer data, personal data, or production credentials.

## Outcome Labels

- `correct_block`: the conservative block or revalidation decision is supported by packet-visible evidence.
- `false_block`: packet-visible evidence indicates the conservative block or revalidation was not warranted.
- `needs_more_evidence`: the packet does not contain enough evidence to judge correctness or falseness.

## Review Principles

- Risk signal is not outcome evidence.
- Decision-time evidence is not execution-time authority.
- A blocked PDP or unavailable page can justify revalidation pressure, but it does not by itself prove the final outcome.
- If the workflow context is material and missing, use `needs_more_evidence` instead of guessing.
- Do not infer identity, price, availability, or permission from semantic similarity alone.

## Required Response Fields

- `reviewed_outcome`: one of `correct_block`, `false_block`, `needs_more_evidence`.
- `confidence`: `low`, `medium`, or `high`.
- `adjudication_status`: use `independent_reviewed` for completed rows.
- `notes_code`: short machine-readable reason code.
- `rationale_short`: one short sentence explaining the decision.
- `evidence_requested_if_needs_more_evidence`: fill only when the label is `needs_more_evidence`.

## Pack Counts

- cases: `146`
- response rows: `146`
- source freeze id: `p0_review_freeze_6c1465ff0c315da6`
- unit/dedup status: `pass`
