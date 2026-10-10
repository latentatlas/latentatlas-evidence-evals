# Reviewer Adjudication Codebook

## Labels

| Label | Use When | Do Not Use When |
| --- | --- | --- |
| `correct_block` | Packet-visible evidence supports the conservative block or revalidation decision. | The packet merely has a risk signal without outcome-grade evidence. |
| `false_block` | Packet-visible evidence shows the conservative block or revalidation was not warranted. | The process context is missing and could change the answer. |
| `needs_more_evidence` | The packet lacks enough evidence to decide correctness or falseness. | You can identify a clear packet-visible contradiction or support. |

## Confidence

- `high`: packet-visible evidence directly supports the label.
- `medium`: packet-visible evidence supports the label with some context dependency.
- `low`: label is possible but the packet is thin; prefer `needs_more_evidence` when uncertainty is material.

## Notes Code Examples

- `masked_identity_conflict_supports_block`
- `blocked_pdp_not_outcome_evidence`
- `latest_pdp_supports_false_block`
- `workflow_context_required_for_price_change`
- `availability_revalidation_supported`
- `all_visual_flags_true_conflict`
