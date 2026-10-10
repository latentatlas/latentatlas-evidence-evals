# R25 development record

`first_bounds.json` is the first successful development calculation before
the producer's explicit inherited parameter-range assertion was added. It
is retained as a diagnostic and is not the authoritative certificate.
The final entrypoint and input hashes are those of
`../results/certificate.json`. The numerical constants did not change.

No failed mathematical assertion was encountered during this package's
initial algebra, interval, rational or two-precision direct-integral checks.
This is a development observation, not a claim that no error can remain.

The main limitation identified before implementation was that the trial
dual b*+v a² exits the tiny prior localization cube at the intended widths.
The new code validates the expanded coefficient cube and its full finite
root complement instead of reusing that old cube beyond its scope.

Another deliberate scope choice is the finite budget window: replacing the
infinite transition profile by a constant tail is accompanied by an explicit
tail integral. Dividing that bound by a_min⁶ is valid on the stated interval
and must not be silently extended to a→0.
