# Authority-Action Case Quality Standard v0.6

Status: candidate design; deterministic validation passed; empirical review pending

## Purpose

v0.6 repairs the evidence-contract defect found during the v0.5 pilot. The task
instruction permits execution only from a current, final, verified grant, so an
`execute` label is valid only when every one of those facts can be resolved from
the supplied packet.

The repair preserves the 100-case v0.5 factorial design and its multi-record
difficulty. It adds four compact proof records to each cell:

1. `PF-CAN`: binds the candidate authorization record to a canonical digest;
2. `PF-REG`: identifies the signer and its active registry window;
3. `PF-VER`: resolves the canonical record, signer, signature result, registry
   match, and verification time; and
4. `PF-FIN`: states the finality status of the canonical record.

These are structured records, not prose conclusions. A model must still join
the proof chain to the actor, action, target, parameters, current time, and any
revocation, conflict, or supersession evidence in the original packet.

## Defect isolation

- Positive controls require a resolvable digest, current signer registry,
  successful signature result, registry match, and committed finality.
- `draft_not_final` controls keep a valid verification chain but use pending
  finality.
- `unverified_source` controls keep an unresolved canonical record and failed
  verification path.
- Other negative controls receive a valid, final proof path so their intended
  actor, time, target, parameter, revocation, conflict, or supersession defect
  remains the only decision-relevant failure introduced by the proof layer.

## Deterministic gates

v0.6 inherits the 17 v0.5 structure and discrimination gates, then adds seven
fail-closed proof-contract gates:

1. proof metadata is complete;
2. exactly four typed proof records are present;
3. the canonical digest binds the source authorization record;
4. the signer registry covers the case's current time;
5. verification references and states resolve consistently;
6. finality matches the intended factorial cell; and
7. the proof layer does not add an unintended authority defect.

Passing 24/24 gates establishes structural and evidence-contract integrity. It
does not establish model discrimination or comparative performance.

## Remaining empirical gates

Before a full run or public result:

- conduct an independent human review of a stratified sample;
- run a small two-model pilot with repeated epochs;
- audit raw transcripts for proof-chain interpretation, protocol completion,
  wrong-scope calls, and provider refusals;
- inspect floor and ceiling effects by difficulty and factorial cell; and
- freeze the corrected artifacts under a new manifest hash before paid calls.
