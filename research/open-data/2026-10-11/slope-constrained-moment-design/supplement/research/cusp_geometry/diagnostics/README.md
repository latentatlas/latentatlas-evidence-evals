# Development record

first_geometry_trial.log records an early rejected calculation.
Squaring a zero-crossing real ball through the general power API
produced a nonfinite value in a remainder bound. The calculation stopped;
no certificate was accepted. The final implementation uses exact
nonnegative upper magnitudes and multiplication for that remainder.
The regression test explicitly exercises zero-crossing control balls.
The historical source line numbers in the log are not current.

A separate initial domain guard also rejected a request whose rounded
ball slightly exceeded the nominal rational half-width. The local
derivative domain now has explicit larger dyadic bounds, and actual
ball magnitudes are checked against the larger majorant domain. That
earliest terminal output was not saved as a separate file.

trial_certificate.json and trial_run.log are the subsequent successful
three-cell trial, covering only cell indices 0,28,57. The complete
58-cell result is in ../results/geometry_certificate.json.
Trials do not imply coverage between tested cells.
