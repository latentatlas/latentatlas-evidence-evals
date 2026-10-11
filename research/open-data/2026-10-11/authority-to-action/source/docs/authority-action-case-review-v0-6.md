# Authority-Action v0.6 Internal Case Review

Review date: 2026-07-26

Status: internal author review complete; independent human review pending

## Review scope

The review covered:

- all 25 valid-neutral source authorization records;
- the proof-contract state of all 100 factorial cells;
- the two source-binding modes used by the dataset;
- proof-record namespace isolation;
- the draft, unverified, expired, future, revoked, superseded, conflict, actor,
  target, and parameter negative-control families; and
- representative neutral/treatment pairs from all four behavior families.

## Observed proof-state distribution

| Proof state | All cases | Execute cases | Withhold cases |
|---|---:|---:|---:|
| verified and final | 90 | 50 | 40 |
| verified but not final | 6 | 0 | 6 |
| unverified | 4 | 0 | 4 |

Digest binding uses a computed source-record hash in 94 cases, an existing
signature-linked canonical digest in two cases, and remains unresolved in the
four intended unverified-source controls.

## Findings and corrections

1. Every execute cell now contains a resolvable source record, canonical
   digest, current signer registry, successful verification result, and
   committed finality record.
2. Draft controls retain successful verification but explicit pending
   finality; unverified-source controls remain unresolved; other negative cells
   receive a valid proof path so the proof layer does not add a second defect.
3. Existing signer and signature fields are reused when present. The
   procurement example also reuses its signature-linked ledger digest, avoiding
   a contradictory second digest.
4. The first implementation used generic `REG-*` proof identifiers. This
   collided with existing registry evidence. The final candidate uses a
   dedicated `PF-*` namespace, and the validator now rejects missing,
   unexpected, or mistyped proof records.
5. Regression tests deliberately tamper with a digest, signer, proof record,
   and positive finality state; all are rejected fail-closed.

## Remaining risks to test empirically

- The proof records may make some previously difficult positive controls too
  easy, producing a ceiling effect.
- The `evaluation_sandbox_capability` wording may continue to trigger the
  Anthropic provider's cyber filter independently of model reasoning.
- A structurally complete proof path does not guarantee that every case reads
  as realistic to an external domain reviewer.
- Protocol omissions after a correct tool decision remain separately
  measurable and should not be collapsed into authorization accuracy.

The next acceptable step is the frozen 20-case, two-epoch, two-model pilot.
Its transcripts must be audited before any full run or model comparison.
