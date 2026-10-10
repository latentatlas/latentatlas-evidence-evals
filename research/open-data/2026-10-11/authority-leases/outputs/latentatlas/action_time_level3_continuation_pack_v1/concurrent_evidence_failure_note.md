# Concurrent Evidence Failure - Research Note Seed

Status: active Level 3.5 research wedge

Short claim:

```text
Many agentic AI failures are not reasoning failures alone. They are evidence-concurrency failures: the model acts on observations whose identity, freshness, authority, or materialization timing no longer align.
```

## Failure Families

- `stale_read`: a prior PDP, screenshot, cache, or policy state is treated as current.
- `identity_time_split`: the target identity changes between evidence capture and action.
- `authority_expiry`: a prior permission or evidence lease no longer authorizes execution.
- `materialization_race`: price, availability, seller, or action state changes before the decision is materialized.
- `visibility_truth_confusion`: blocked access, timeout, or empty page is treated as product or workflow truth.
- `context_contamination`: a reviewer or model imports outside memory/jargon and replaces packet-visible evidence.

## Testable Predictions

- Packets with latest temporal authority will produce a different false-block profile than stale or not-observed packets.
- Blocked PDP and access-wall cases should route to `needs_more_evidence` unless fresh unblock or outcome proof exists.
- Identity conflicts should support block-grade decisions only when the packet-visible identity guard is explicit.
- Context-contaminated external reviews will produce plausible but unsupported rationales.

## Evidence Needed For Stronger Claims

- reviewed strata by action type, timing, identity state, and access state
- second-reviewer or partner-side replication
- baseline replay against stale-evidence and decision-time-only policies
- explicit unresolved-case handling
- holdout or later-period replication

Boundary: this note is a research wedge. It does not claim population failure rates.
