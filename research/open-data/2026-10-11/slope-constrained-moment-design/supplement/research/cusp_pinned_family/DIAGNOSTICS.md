# R08 diagnosis and retained unsuccessful bounds

All R01–R07 inputs are frozen. R08 calculations write only this new
package. None of the early discovery files is a continuum certificate.

1. The [six-point discovery](diagnostics/six_points.json) solved at
   nu=-1,-14.5,-29 with amplitudes -1/2,+1/2. It suggested persistent
   cusps, nu widening and amplitude narrowing, but did not prove them.
2. The common amplitude in F+epsilon H was separated exactly using
   alpha=H3(Q)/F3(Q). The normalized family F+rho(H-alpha F) has the
   same zeros. This made the shape-dependent interval error smaller.
3. A [single symmetric rho box](diagnostics/plane_full_rho.json) with
   radius 3/4 did not establish the required geometric bounds in the
   three sampled cells. Cells 0,28,57 stopped respectively at the
   quadratic, semicubical and cubic sufficient bounds. This is an
   inconclusive enclosure, not evidence of a failed mathematical claim.
4. [Two rho slabs](diagnostics/two_slabs.json) passed five of six sampled
   cells; the last cell of the second slab did not establish the
   semicubical bound. The formula and the target physical interval
   were unchanged.
5. [Four rho slabs](diagnostics/four_slabs.json) passed all twelve sampled
   cells. The full generator then passed all 232 cells, 228 nu joins
   and 174 rho joins. This is the first full-domain R08 certificate.
6. The [rational sample check](diagnostics/rational_sample.json) passed
   before the separate checker was run across the full domain.
7. The point/fold sample checker uses a 512-bit outward dyadic grid:
   its absolute residuals are much smaller than the 192-bit grid used
   for the dimensionless continuum tests. This choice was made before
   the point checks; no comparison tolerance was inserted.
8. The initial two figure previews placed legends on plotted lines.
   Legends were moved into blank areas and both figures regenerated.
   Only unfrozen figure artifacts were replaced; no scientific result
   was changed.

The continuum rational check treats saved correlated Taylor ranges as
input assumptions, as explicitly stated in its report. It independently
reconstructs the downstream inequalities and fold ODE calculations.
The numerical mpmath checks do not substitute for the rigorously bounded
quadrature.

The final full-domain certificate, point certificates, fold samples,
independent check reports and figures are linked by hashes in the
closing audit. An inability to prove a coarse interval bound is not
silently relabelled as a passed check.
