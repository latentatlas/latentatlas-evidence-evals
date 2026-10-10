# R05 development diagnostics

`probe.log` records three-cell tests of a coarse global fourth-derivative
bound. Its margin is negative for S=0.001 and S=0.0001, and positive
for S=0.00001. A negative bound here is failure of that estimate to
certify positivity, not a negative actual transport derivative or a
counterexample to monotonicity.

`refined_probe.log` uses the correlated fourth derivative at the cusp,
plus a fifth-derivative remainder. It obtains positive bounds already
at S=0.001 on those three cells. We chose S=0.00075 for the final
whole-path proof because it suffices to cover all 0<ell<=10^-6 by the
R04 quadratic lower bound, and keeps additional margin.

`trial_certificate.json` and `trial_run.log` concern only cells 0,28,57.
They are retained as diagnostics. The final theorem uses all 58 cells
in `../results/width_certificate.json`, plus the separate rational
check, and the analytic proof. Trial source hashes reflect the version
that produced them; the final certificate determines the final sources.

The development chronology is recorded in the ongoing research notebook
`../../CALISMA_DEFTERI.md`. Failed estimates are retained so a later
review can distinguish loss of a bound from a counterexample.
