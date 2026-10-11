# Action-Time V2 Outcome Adjudication Finding

Generated at UTC: `2026-07-13T06:45:10.688362+00:00`

## Verdict

- Status: `pass`
- Finding verdict: `v2_masked_evidence_outcome_adjudication_pilot_completed`
- Reviewer: `reviewer01_hsyn`
- Review scope: `P0 masked-evidence sidecar outcome review`
- Outcome-ready P0 packets reviewed: `146` / `146`
- Unreviewed outcome-ready packets: `0`

## Adapter And Sufficiency Surface

- Input V2 packets: `2614`
- P0 packets: `151`
- Sidecar rows supplied: `151`
- Merged packets: `151`
- Outcome-adjudication allowed: `146`
- Outcome-adjudication blocked: `2468`
- Sidecar validation: `pass`

Packet sufficiency counts:
- `insufficient_for_outcome_adjudication`: `2468`
- `sufficient_for_outcome_adjudication`: `146`

## Human Outcome Review Result

- Reviewed packets: `146`
- Resolved outcome count: `121`
- Resolved outcome rate: `0.8288`
- `needs_more_evidence` count: `25`
- `needs_more_evidence` rate: `0.1712`
- `correct_block` count: `99`
- `false_block` count: `22`

Outcome counts:
- `correct_block`: `99`
- `false_block`: `22`
- `needs_more_evidence`: `25`

## Outcome By Observed Change Type

- `availability_or_access_uncertain_masked`: `correct_block`=`77`, `false_block`=`12`, `needs_more_evidence`=`23`
- `identity_conflict_masked`: `correct_block`=`4`
- `not_action_grade_masked`: `correct_block`=`18`, `false_block`=`10`
- `price_or_materialization_conflict_masked`: `needs_more_evidence`=`2`

## Principle Observations

### identity change is action-grade block evidence

- Measured signal: `identity_conflict_masked`
- Pilot observation: 4 of 4 reviewed identity-conflict packets were labeled correct_block.
- Claim boundary: Pilot observation only; not a population probability.

### PDP block is not outcome evidence

- Measured signal: `blocked_pdp`
- Pilot observation: 7 reviewed packet(s) with blocked PDP reasoning remained needs_more_evidence.
- Claim boundary: A blocked PDP supports evidence insufficiency, not correctness or falseness.

### latest PDP state can supersede stale state when current PDP evidence exists

- Measured signal: `false_block with packet-visible PDP temporal authority evidence`
- Pilot observation: 14 reviewed packet(s) were labeled false_block with latest PDP temporal authority evidence present.
- Claim boundary: Requires packet-visible temporal authority evidence before generalization.

## Experimental Interpretation

V2 changed the experiment from a risk-signal review into a gated outcome-adjudication review. The masked evidence sidecar made a small P0 subset reviewable without exposing raw URLs, titles, prices, sellers, customer data, prompts, transcripts, or source text.

The result is mixed in the useful sense: some packets became resolved outcomes, while other packets remained explicitly evidence-insufficient. This shows that `needs_more_evidence` is not a fallback label; it is still an active epistemic boundary when the masked evidence does not support a correctness judgment.

## Claim Boundary

Allowed claims:
- The V2 masked evidence sidecar made a subset of packets outcome-adjudication-ready.
- In this P0 sidecar review set, 146 of 146 outcome-ready packets were reviewed.
- The pilot produced both resolved outcome labels and explicit evidence-insufficiency labels.
- The result is suitable as a protocol finding and article section, not as a production probability claim.

Blocked claims:
- The pilot proves a population false-block rate.
- The pilot proves an empirical false-authorization probability.
- The pilot proves all guard decisions are correct.
- A risk signal or blocked PDP is outcome evidence by itself.
- The review mutated production truth.

## Audit Controls

- Internal index read: `false`
- External calls used: `false`
- Production truth mutation: `false`
