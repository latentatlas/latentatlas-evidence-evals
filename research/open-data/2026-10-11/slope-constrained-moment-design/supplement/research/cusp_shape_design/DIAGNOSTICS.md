# R09 — Exploration and unsuccessful intermediate steps

The final evidence chain is in `results/`. Exploratory reports and
failed intermediate bounds are retained separately in `diagnostics/`.

1. `explore_directions.py` enumerated the 1820 four-column supports
   among sixteen modes with floating-point arithmetic. This supplied
   the candidate J=(10,13,15,16), not its optimality proof. The final
   dual certificate bounds every feasible sixteen-mode vector,
   including vectors with more than four nonzero entries.
2. `certify_local.py` used an auxiliary fold μ radius 2^-20. Its
   three-cell diagnostic `local_16_sample.json` failed a sufficient
   contraction inequality in the first sampled cell. That failure
   means the selected bound did not prove contraction, not that a
   cusp disappeared. The original source and report are preserved.
3. `certify_local_v2.py` changes that auxiliary radius to 2^-19 and
   adjusts the enclosing auxiliary majorant box accordingly. The
   requested physical window |s|≤0.003, |ℓ|≤10^-6, |m|≤2×10^-9
   stays the same. The three-cell check and then all sixteen cells
   pass. The separate rational checker uses the successful bounds.
4. Two first executions of the rational local checker stopped on
   Python type errors: a scalar Fraction was passed to an interval
   sign helper, and int/interval division lacked the required reverse
   method. The notes `local_checker_type_failure.json` and
   `local_checker_division_failure.json` record the pre-fix source
   hashes. Wrapping the respective scalars in D fixed these dispatch
   errors. No mathematical tolerance or target inequality was weakened.
5. The first provenance preflight rejected an otherwise identical
   copied negative bound because the Markdown used a Unicode minus
   and the JSON used an ASCII hyphen. The audit now normalizes that
   one typographical character before comparing displayed numbers.
   No numerical bound or mathematical output was changed.

The historical pre-fix source hashes in item 4 are an identification
record, not reconstructible full source snapshots. The final checker
source is the one hashed in `results/local_check.json`. This limit is
explicit; the diagnostics must not be treated as final passed outputs.

All three proof stages have different scopes: optimum of an initial
derivative in a finite class; actual finite fold narrowing on a compact
amplitude interval; and local analytic behavior at two amplitudes
outside that interval. They are not interchangeable confirmations.
