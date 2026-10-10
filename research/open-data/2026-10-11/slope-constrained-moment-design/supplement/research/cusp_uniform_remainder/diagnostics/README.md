# R27 diagnostic history

- `probe_initial.json`: TypeError from `Arb // int`. The factorial ratio
  is now formed in integer arithmetic before multiplication by Arb.
  `model_before_integer_coefficient_fix.py` preserves the initial source.
- `probe_coefficient.json`: dual contraction passed, but the combined
  C₄>0 and Xi>0 acceptance test failed with a coarse coefficient box.
  The record does not distinguish which individual sign test failed.
  It does not show a negative true coefficient.
  `model_before_localization_refinement.py` preserves that source.
- `probe_refined.json`: the same driver width passed after contraction
  tightening and improved centering of the validated matrix solve.
- `certificate_before_explicit_solve_seed.json`: successful early full
  certificate. The dyadic solve seed was then recorded explicitly for
  rational reconstruction; recording it did not change the numbers.

Historical hashes identify their respective versions. These files are not
current entrypoints or replay targets. Restoring historical code requires
a disposable copy at the original package location. Current authoritative
results are in `../results/`.

A documentation patch initially failed to match a malformed `,+and`
line. The patch tool made no changes in that attempt. The line was then
corrected; no mathematical expression or computed output changed.
