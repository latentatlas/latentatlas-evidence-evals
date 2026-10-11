RE-Bench systems-benchmark review v0.1 — source and reproducibility archive
============================================================================

This archive accompanies the Zenodo technical-note deposit:

  RE-Bench Is a Systems Benchmark:
  What Its Scorers and Selection Rules Actually Support

Version: 0.1
DOI: https://doi.org/10.5281/zenodo.22089195
Publication date: 2026-08-25
Creator: Huseyin Buldurgan (LatentAtlas)

Canonical public source
-----------------------

The source/ directory is a byte-for-byte copy of the eight files published at:

  https://github.com/latentatlas/latentatlas-evidence-evals/tree/35835f8a8c0f90abb785aff8f3ddce3e99e659d9/docs/re-bench

The canonical public commit is:

  35835f8a8c0f90abb785aff8f3ddce3e99e659d9

The pinned METR/RE-Bench implementation examined by the review is:

  93b98062e55f6945d4a7e213a3226dd419896170

Archive layout
--------------

  source/                  Exact eight-file public package
  metadata/                Zenodo metadata and release manifest
  LICENSE-MIT.txt          License retained by the public source package
  RIGHTS.md                File-level license and status mapping

Verification
------------

From source/:

  shasum -a 256 -c SHA256SUMS
  python -m pip install -r requirements-audit.txt
  python contract_checks_v0_1.py

The published harness is expected to report eight passing bounded contract
checks. These checks inspect pinned source behavior only. They do not execute a
participant submission, protected scorer service, H100 benchmark workload,
historical model trajectory, official solution archive, or RE-Bench headline-
result reproduction.

Scope and status
----------------

This is an unaffiliated, AI-assisted public working review. It has not undergone
peer review or independent human adjudication. The archive intentionally omits
private working notes, internal adjudication material, EEC/K-WEP research files,
local worktree metadata, provider payloads, protected solutions, and benchmark
hardware artifacts.

