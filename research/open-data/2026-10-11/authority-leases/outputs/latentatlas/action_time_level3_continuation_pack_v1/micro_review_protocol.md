# Low-Friction Micro-Review Protocol

Status: qualitative support only

Purpose: use 10-15 case packs to test whether an external reader can apply the LatentAtlas label rubric without importing outside domain context. This protocol does not produce full reviewer02 completion, inter-rater agreement, kappa, or Level 4 probability evidence.

## Valid Response Requirements

- Reviewer must use only packet-visible evidence.
- Any invented domain scenario, external jargon, or non-packet fact invalidates the response for adjudication.
- 15-case mini-reviews are qualitative method-fit checks, not full reviewer02 completion.
- Confidence should be low/medium/high unless the pack explicitly requests another scale.
- Returned labels must include case_id, reviewed_outcome, confidence, and rationale_short.
- Responses must be audited for grounding before any label is counted.

## Invalidation Rules

- If the response adds non-packet facts, mark `invalid_for_outcome_adjudication`.
- If the response uses a different domain ontology to replace the masked evidence, mark `context_contaminated_response`.
- If confidence uses a non-requested scoring scale, keep it as qualitative only unless normalized by a reviewer.
- If case IDs are transformed or dropped, do not ingest the labels.

## Allowed Use

- method-fit signal
- rubric clarity feedback
- prompt/packet guardrail failure example
- qualitative evidence for why stronger reviewer protocols need grounding checks

## Not Allowed Use

- full reviewer02 replacement
- inter-reviewer agreement computation
- Level 4 probability claim
- empirical label count without grounding audit

## Return Format

```text
case_id | reviewed_outcome | confidence(low/medium/high) | rationale_short
```
