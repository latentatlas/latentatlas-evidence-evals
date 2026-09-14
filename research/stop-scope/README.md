# Verifying Stop Scope in Agent Workflows

Huseyin Buldurgan · Offline evidence supplement · Version 1.0.0

This supplement accompanies a local Open-SWE comparison of cancellation, waiting for worker completion, and origin-scoped file-write control. It is a separate research artifact within this repository; it does not change the Evidence Evals package or its results.

## Download and verify

Download `stop-scope-supplement-v1.zip` from the [versioned release](https://github.com/latentatlas/latentatlas-evidence-evals/releases/tag/stop-scope-supplement-v1.0.0). The archive is 122,408,188 bytes. Its SHA-256 is:

```text
3c05757cd20d1e736b67ce509325316e8ffd0b5a6fcb901d701e02aa58e2ac43
```

Extract the archive, enter `stop-scope-supplement-v1`, and run:

```sh
python3 -B verify_bundle.py
```

The verifier uses only the Python standard library (Python 3.12 or later recommended). It does not install software, make network requests, call a model, or run new experiments. An exit code of zero means the retained evidence is internally consistent, not that all stopping requirements passed.

## Evidence and scope

- 26 canonical conditions and their 26 same-host repeat executions, with file bytes, events, instrumentation snapshots, summaries, and audits.
- Two separate diagnostic executions outside the main matrix.
- A complete, hash-verified 427-file Open-SWE snapshot at commit `e0d9aff59925a4da55ec8d6c31fa723651c24909`.
- Four single queue-path trials and one combined delegation/scheduling feasibility trial, clearly separated from the main comparison. Child stopping was not tested; scheduled execution did not establish a healthy baseline.
- A broader, unexecuted draft design of 286 cases across 24 families. These are not completed experimental findings.

All 52 matrix records and both diagnostic records passed the unchanged offline auditor after export and again after extraction at a fresh location. Programmed, deterministic model responses were used in the original experiment, not a live LLM. The repeat was on the same computer and is not an independent laboratory replication or independent human validation.

## Sharing and reuse

This is a derived sharing copy. Unnecessary local paths were minimized; native evidence file bytes, event identities, timing, outcome classifications, and counts were preserved. Original-to-export digests and the transformation policy are included. Original evidence remains retained unchanged by the author.

The archive is an offline audit package, **not** a turnkey environment for fresh experimental execution. It does not establish a production safety rate, distributed shutdown guarantee, or adversarial-runtime honesty. The paper manuscript is not included.

Study-specific code and documentation follow the repository's MIT license. Upstream source and installed backend snapshots retain their own copyright notices; see the archive's `LICENSE`, `upstream/LICENSE`, and `THIRD_PARTY_NOTICES.md`.
