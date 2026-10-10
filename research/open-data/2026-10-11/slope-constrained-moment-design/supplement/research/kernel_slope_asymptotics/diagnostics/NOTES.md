# R15 diagnostic history

No earlier frozen package was edited. These are development checks of
the new R15 producer/checker, not corrections to R12–R14 mathematics.

1. The first producer required three strict root-radius contractions.
   It stopped before writing a certificate when the third proposed
   radius equaled the second. Finite-precision interval radii can
   stabilize. The revised algorithm accepts only strict improvements,
   stores the non-improving proposal, and retains the last proved root
   enclosure. At least one accepted contraction remains mandatory.
   In the successful output all 28 roots had two improvements and an
   equal third proposal. Archived source:
   `certify_before_contraction_stop.py`; log:
   `first_contraction_failure.log`.

2. The first rational checker tried to parse the product of two lower
   bounds as an exact Arb scalar. Multiplication at finite precision
   produces an interval, although its operands are exact dyadics.
   The product must be read as an enclosing interval and its lower
   endpoint used as a lower bound. Archived source:
   `check_before_product_interval.py`; log:
   `product_interval_failure.log`.

3. Requiring the separately reconstructed product to lie in the
   recorded product enclosure was also too strong. Arb `.lower()`
   rounds down before multiplication, while the rational interval
   helper rounds all values outward to a fixed 2^-512 grid. On the
   last three tiny tail densities that fixed absolute grid enlarges
   the reconstructed lower-bound error more than the Arb product
   width. The final check therefore reads the original dyadic ball
   endpoints as exact Fractions for this comparison, verifies that
   the recorded lower coefficient is no greater than their exact
   product, and then uses a conservative rational lower endpoint.
   Archived intermediate source:
   `check_before_lower_endpoint_rounding.py`; log:
   `lower_endpoint_rounding_failure.log`.

The last two failures concern the representation and comparison of
bounds; the recorded coefficient and asymptotic certificate did not
need to change. The final rational check reconstructs the positive
lower constant and all displayed coefficient brackets successfully.
It does not silently replace a failed inequality with a tolerance.
