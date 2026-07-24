# Contributing

Contributions that improve reproducibility, evaluation coverage, auditability,
or the clarity of the architecture are welcome.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

The package supports Python 3.11 and newer and has no runtime dependencies.

## Contribution standard

A contribution should:

- include a focused explanation of the decision or failure mode it addresses;
- preserve deterministic outputs and stable audit fields;
- add or update negative controls for changed behavior;
- keep semantic similarity, identity, evidence, and action authority as
  independently inspectable signals;
- include tests for both the expected path and the relevant failure path;
- use synthetic or deliberately public data only;
- pass `python -m unittest discover -s tests -v`.

## Pull requests

Keep pull requests focused. Describe the architecture or behavior change, the
reason codes or output fields affected, and the validation performed. Update
the examples or architecture notes when a public contract changes.

## Security reports

Do not open public issues containing credentials, customer data, private
communications, or unpublished evaluation packets. Follow
[SECURITY.md](SECURITY.md) for private reporting.
