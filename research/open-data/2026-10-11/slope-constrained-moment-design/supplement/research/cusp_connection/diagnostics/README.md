# Development trials, not the final curve certificate

The first uniform trial at ν=−0.25 bounded each derivative separately
before multiplying by the preconditioner. Its conservative interval
bound was q≈1.281135>1, so the required contraction test failed and the
program stopped. The recorded traceback is in
`coarse_interval_bound_failure.log`. This is a failure to prove
contraction with that enclosure, not a proof that the cusp branch fails
to exist.

The refined method first combines central derivatives in each
preconditioned Taylor entry, preserving their known correlation. It
retains absolute remainder bounds and the same contraction requirement.
The trial then gave q≈0.501706 and η+q≈0.559274; its log and saved cell
are `refined_trial.log` and `trial_cell.json`.

The initial source version was not separately frozen, and line numbers
in its traceback are historical. The final implementation still records
the coarse bound as `uncorrelated_q_bound` in every cell. The successful
full result and independent arithmetic checks are in `../results/`;
neither trial alone establishes a connected curve or endpoint identity.
