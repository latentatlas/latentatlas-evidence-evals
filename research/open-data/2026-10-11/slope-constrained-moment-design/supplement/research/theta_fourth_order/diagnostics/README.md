# Exploratory finite-root calculation

`finite_probe.json` was produced before the full certificate, using the
unchanged R15 coefficient cube and its 28 finite root boxes. It omitted
the infinite root tail and used the direct Arb inverse. Its own status
marks it diagnostic only. It is not an input to any certified result.

The final computation instead tightens the exact-dual localization using
the inherited strong-convexity inequality, records accepted root-box
contractions, adds all four analytical tail enclosures, and validates
the matrix solve by a Neumann residual estimate. The published bounds
are checked by a separate rational reconstruction.

No failed mathematics check occurred in producing the final R24
certificate. The preliminary finite-root output is retained so that its
different uncertainty width cannot be confused with the final result.
