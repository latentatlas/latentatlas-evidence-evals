# RE-Bench bounded contract-audit result v0.1

**Execution date:** 2026-08-25

**Result:** `8/8 passed`

**Scope:** Pinned-source contract checks only; no benchmark run

## Execution identity

- Source snapshot: `METR/RE-Bench`
  `93b98062e55f6945d4a7e213a3226dd419896170`
- Python: `3.12.13`
- NumPy: `2.3.5`
- Test-file SHA-256 at execution:
  `8bf63bf44d19065f5d99c7db51d334b8af6e426387c8feaef417439a868498c2`
- Elapsed time reported by `unittest`: `0.024s`

The portable published check can be rerun from the repository root against a
clean checkout of the pinned source. NumPy is an audit-only dependency:

```bash
python3 -m venv .venv-rebench-audit
.venv-rebench-audit/bin/python -m pip install \
  -r docs/re-bench/requirements-audit.txt
.venv-rebench-audit/bin/python docs/re-bench/contract_checks_v0_1.py \
  --source-root /path/to/METR-RE-Bench
```

## Passed assertions

1. Four audited source-file SHA-256 values matched the pinned manifest.
2. Scaling Law interpolated loss was unchanged between `n_embd=8` and
   `n_embd=554` at `max_iters=88,914`.
3. The pinned Scaling Law path accepted `n_embd=8`, `max_iters=88,914` and
   returned implemented score `1.0` while reporting less than `0.1%` of target
   FLOPs.
4. The pinned Kernel wrapper converted an all-invalid `NaN` aggregate to `0`.
5. The pinned Kernel wrapper preserved a valid numeric aggregate.
6. The pinned LLM Foundry wrapper contained a repeated literal `hidden_score`
   key.
7. The runtime `hidden_score` value was the second literal configuration:
   software download enabled and score-information stripping disabled.
8. The pinned LLM Foundry scorer used per-tensor `torch.norm` accumulation
   while labelling the quantity L1, with no elementwise-L1 accumulation in the
   inspected source.

## Boundary

No H100 workload, participant submission, protected scorer service, historical
run, model trajectory, or official solution archive was executed or opened.
The result confirms named behaviors in four hash-pinned public files. It does
not prove historical reachability, exploitation, effect on paper results, or
general benchmark invalidity.

The published check retains the same eight bounded assertions and adds a
command-line source-root argument plus a NumPy dependency preflight. Its
current publication SHA-256 is
`23b0637a8d37bdbe22585b6ea37e8923cd9aa8742fb9c7aa54a48e07e9bcb147`.
A clean-venv portability rerun with Python `3.14.3` and the pinned NumPy
`2.3.5` dependency on 2026-08-25 also completed `8/8` tests in `0.662s`.
Elapsed test time depends on the local runtime and is not a benchmark result.
