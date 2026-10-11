# Frozen Masked-Review Artifact

This repository includes a machine-readable, aggregate-only record of the
completed masked human review described in the LatentAtlas research notes.

## Snapshot

- 151 high-priority evaluation packets;
- 146 outcome-ready packets;
- 146 reviewed outcome-ready packets;
- 5 packets that did not enter outcome adjudication;
- 99 packet-supported blocks;
- 22 packet-unsupported blocks;
- 25 insufficient-evidence outcomes.

The three outcome counts sum to the 146 reviewed outcome-ready packets. The
reported rates use 146 as their denominator.

## Public Files

- [`summary.json`](../data/frozen_masked_review_v1/summary.json) records the
  selection counts, outcome counts, rates, and source snapshot identity.
- [`outcomes.csv`](../data/frozen_masked_review_v1/outcomes.csv) provides the
  same outcome distribution in a compact tabular format.
- [`manifest.json`](../data/frozen_masked_review_v1/manifest.json) records
  SHA-256 digests, byte sizes, data-handling choices, and research references.

The source snapshot is identified by a freeze ID and the SHA-256 digest of its
canonical masked rows. Row-level records are not included in this repository.
The public files contain no reviewer identifiers, raw text, prompts, source
URLs, product attributes, customer data, tenant data, or personal data.

## Verification

Run the verifier from the repository root:

```bash
python -m latentatlas verify-frozen-review \
  --artifact-dir data/frozen_masked_review_v1
```

The verifier checks:

1. public file SHA-256 digests and byte sizes;
2. agreement between the CSV and JSON results;
3. selection and outcome-count arithmetic;
4. outcome-rate calculations;
5. agreement on the source snapshot identity; and
6. the aggregate-only data-handling declaration.

A changed file, count, rate, or snapshot identity produces a failing result
and a non-zero command exit status.

## Interpretation

These are descriptive results for the frozen review sample. The public
artifact makes the reported counts inspectable and tamper-evident without
publishing the underlying row-level review records.
