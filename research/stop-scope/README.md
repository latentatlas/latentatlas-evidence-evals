# Verifying Stop Scope in Agent Workflows

Huseyin Buldurgan · Retained evidence v1.0.0 · Browsable export prepared 1 October 2026

This supplement accompanies a local Open-SWE comparison of cancellation, waiting for worker completion, and origin-scoped file-write control. It is a separate research artifact within this repository; it does not change the Evidence Evals package or its results.

The [Apart sprint submission](https://apartresearch.com/sprints/projects/verifying-stop-scope-in-agent-workflows-lpj9) reports a deterministic local control experiment, not a test of a model's willingness to stop. The original submission and evidence release remain unchanged. This directory now exposes the code and summaries without requiring a large archive download.

**Later development:** the [9 October 2026 research progress and evidence snapshot](progress/2026-10-09/README.md) separately publishes live A development observations, scoped-confirmation controls and cancellation-target checks. It includes its own records, scope statement and portable verifier; the sprint results below remain unchanged.

## Read the experiment

| Question | Start here |
|---|---|
| What was planned and measured? | [Frozen protocol](harness/stop_contract_study/PROTOCOL.md), [26-condition plan](provenance/MATRIX_PLAN.json) |
| How are the conditions run? | [Matrix runner](harness/stop_contract_study/run_matrix.py), [locked-runtime runner](harness/stop_contract_study/run_probe.py), [local API experiment](harness/stop_contract_study/child_probe.py) |
| Where are identity and write controls implemented? | [Factory and controls](harness/stop_contract_study/factory_support.py) |
| What is the synthetic task? | [Workload](harness/stop_contract_study/workload.py) |
| How are observations checked independently of the execution helpers? | [Offline auditor](harness/stop_contract_study/audit_study.py), [audit tests](harness/stop_contract_study/test_audit.py) |
| What are the results? | [Original summary](results/canonical/SUMMARY.json), [same-host repeat](results/repeat/SUMMARY.json), [comparison](results/ORIGINAL_COMPARISON.json) |
| How were summaries produced? | [Report builder](harness/stop_contract_study/build_report.py) |
| Can I trace these files to the old evidence? | [Export index](provenance/EXPORT_INDEX.json), [original-to-sharing-copy manifest](provenance/SUPPLEMENT_EXPORT_MANIFEST.json) |

The 14 study Python files match the hashes in the original frozen matrix plan. The plan's hash matches the original report provenance. The upstream source, dependency lock, and supporting factory are included in their expected relative layout. This is byte-level provenance, not an independent signature or proof of the historical execution.

## Three different checks

Run these commands from `research/stop-scope` with Python 3.12 or later:

```sh
# Check exported code, summaries, and their provenance links only.
python3 -B review_bundle.py

# Check the packaging layer's negative controls (no agent experiments).
python3 -B -m unittest test_review_bundle -v

# With the extracted release below: re-audit all retained records and
# recompute aggregate counts and grouped verdicts from those records.
python3 -B review_bundle.py --bundle /path/to/stop-scope-supplement-v1
```

Without `--bundle`, the check explicitly reports `raw_evidence_reaudited: false`. With the complete release, it checks 52 matrix records plus two separate diagnostics. Neither command installs dependencies, contacts a provider, or runs a new agent experiment. `--output /path/to/new-audit.json` optionally saves the report and refuses to overwrite an existing file.

**Fresh execution is a separate operation.** See [reproduction instructions and limitations](REPRODUCTION.md). The retained evidence does not become an independent replication merely because it passes another offline audit.

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

The archive remains an offline audit package, **not** a turnkey environment for fresh experimental execution. The browsable harness is supplied separately in this directory; it still requires the pinned Python and dependency environment. Neither artifact establishes a production safety rate, distributed shutdown guarantee, or adversarial-runtime honesty. The paper manuscript is not included in the evidence archive.

Study-specific code and documentation follow the repository's MIT license. The browsable Open-SWE tree retains its [upstream license](harness/application_probe/upstream/LICENSE). [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) is a byte-identical copy of the old archive notice: its `upstream/` and `instrument/` paths refer to the archive layout, not this browsable layout. Installed backend snapshots remain in the full archive; this checkout does not redistribute an installed Python environment.

The [October verification record](verification/REVIEW_CHECKS_2026_10_01.json) distinguishes re-auditing retained experiments, rerunning the existing 45-test QA suite, and the eight new packaging tests. The [live-summary extension](NEXT_EXPERIMENT.md) is a proposed next experiment, not an additional result.
