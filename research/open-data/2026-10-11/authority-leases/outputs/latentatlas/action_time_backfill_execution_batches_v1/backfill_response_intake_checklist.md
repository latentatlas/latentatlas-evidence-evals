# Backfill Response Intake Checklist

Status: `ready_for_returned_responses`

Required row fields:

- queue_id
- event_id
- reviewer_id_hash
- reviewed_at
- reviewed_outcome
- confidence
- adjudication_status
- notes_code
- rationale_short

Allowed reviewed_outcome values:

```text
correct_block | false_allow | false_block | missed_revalidation | needs_more_evidence | safe_allow
```

Allowed confidence values:

```text
low | medium | high
```

Hard stops:

- unknown queue_id
- duplicate queue_id in returned batch
- reviewed_outcome outside allowed labels
- confidence outside allowed values
- missing rationale_short
- raw URL, customer data, personal data, or source row included in notes
- treating response intake as Level 4 completion before adjudication

Expected pending rows in this execution pack: `2608`
