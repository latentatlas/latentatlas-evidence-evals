# Reproduction boundaries

There are three distinct activities: reading the source, auditing retained observations, and executing new experiments. Only the last creates new experimental evidence.

## Offline audit

The commands in [README.md](README.md) use the standard library. The original auditor is unchanged. `review_bundle.py` is a new packaging wrapper that verifies frozen sources, checks the released evidence inventory, calls that auditor, and compares recomputed counts and grouped verdicts with the published summaries.

The export has 461 byte-identical copied files, including 14 study Python files and 427 upstream files. The export index does not cover subsequently authored explanatory documents or the new wrapper; those are reviewable repository changes, not historical instrumentation. The old supplement's 2,103-file inventory remains separately verified.

The eight new packaging tests check missing, modified, extra, and symlinked files; path traversal; altered counts or verdicts; invalid evidence; and missing or duplicated summary groups. These are not additions to the paper's 26 conditions or its original 45-test QA result.

## Fresh experiment prerequisites

The frozen runner requires Python 3.14, originally 3.14.3. Its dependency versions must match [requirements.lock](harness/admission_probe/requirements.lock). The code is not installed into this repository's general Python environment. Do not use a production environment or attach real credentials.

The `harness` directory preserves the expected layout:

```text
harness/
  stop_contract_study/   # experiment, matrix, report builder, auditor, tests
  admission_probe/      # supporting factory and hash-pinned dependency lock
  application_probe/    # upstream manifest and exact Open-SWE source
```

For a new execution, copy this directory to a new, empty working directory, create a dedicated Python 3.14 environment, and explicitly install the lock using a hash-checking installer. Installation requires package access and is not performed by the offline verifier. Record the interpreter, platform, installer output, package versions, and source hashes. Do not write into retained run directories.

The historical environment reported two known dependency conflicts: `langchain-e2b` requested `deepagents>=0.6.0,<0.7.0` while 0.7.13 was installed; `e2b` requested `wcmatch>=10.1,<11` while 11.0 was installed. The historical local workflow ran with these upstream overrides. This is **not** a claim that the environment is generally dependency-compatible. The precise historical review is in `reproduce.py`; unexpected conflicts must not be silently accepted.

From the copied `stop_contract_study` directory, the relevant entry points are:

```sh
# Use the dedicated, locked Python 3.14 interpreter, not an arbitrary python.
python -B run_matrix.py --version v03
python -B run_probe.py --run-id receipt-fault-v03 --arm cancel_summary --schedule accepted_precommit --seed 17 --receipt-fault bypass
python -B verify.py --qa-id qa-v03 --record runs/matrix-s17-accepted_precommit-cancel_summary-v03 --source-root ../application_probe/upstream
python -B build_report.py --matrix v03 --report-id report-v03 --qa-id qa-v03 --delivery-counterexample receipt-fault-v03
```

These commands generate new records and must be reviewed as such. The matrix retains failed and incomplete conditions; the report builder refuses incomplete evidence. Run IDs and report IDs must be fresh. The old `reproduce.py` is preserved as historical orchestration code: its preparation mode expects the original lab's `.venv` location, so it is not advertised as a one-command installer for an arbitrary checkout.

The experiment scripts use deterministic model responses and an in-process server. Their Python audit hook denies external network operations and subprocess activity within the experiment child, with logged exceptions for optional platform probes. This is a test-fixture restriction, not an OS-enforced security sandbox against hostile Python code.

## What has and has not been verified

The original study executed 26 conditions and repeated them in a fresh environment on the same host. The October repository work re-audited retained evidence and tested the packaging layer. It did not add a new experimental replication, live model, operating system, or independent operator.

No fresh-install portability claim should be made until another clean installation and execution produces its own setup, run, QA, and report records. A live-model extension needs a separate protocol and denominator; it cannot be inferred from the deterministic results.
