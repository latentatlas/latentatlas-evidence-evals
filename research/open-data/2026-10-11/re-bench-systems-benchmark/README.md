# RE-Bench systems review — open source-contract audit

Original paper: DOI 10.5281/zenodo.22089195; v0.1.
`source/` is the unchanged public v0.1 package, containing the review,
evidence manifest, executable checks, requirements, receipt and checksums.
The review source commit is 35835f8a8c0f90abb785aff8f3ddce3e99e659d9.
The audited upstream commit is 93b98062e55f6945d4a7e213a3226dd419896170.

`upstream/RE-Bench/` contains the four exact audited input files, upstream
README and complete MIT licence with METR's benchmark integrity notice.
They are copied from that immutable upstream commit. Source provenance and
the top-level verifier check their byte identities.

From this directory, install the pinned numerical dependency and run the
eight local contract checks:

```sh
python3 -m pip install -r source/source/requirements-audit.txt
python3 source/source/contract_checks_v0_1.py --source-root upstream/RE-Bench
```

This is a bounded source-contract audit, not a historical benchmark rerun.
Eight checks concern four files in three explanatory task families. Protected
upstream solutions and unrelated private review excerpts are not research
inputs of the public package and are not redistributed. Original review
source retains its MIT licence; the paper is CC BY 4.0.
