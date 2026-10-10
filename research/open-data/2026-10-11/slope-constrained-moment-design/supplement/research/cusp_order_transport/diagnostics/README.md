# Development failures retained

Four development checks stopped execution before a successful rational
result or freeze. All original sources and the reasons for correction
are retained; no failed run was labeled as evidence.

1. [Negative power API](negative_power_api_failure.json): the old exact
   polynomial helper only accepts nonnegative integer powers; use its
   supported division by a monomial for inverse factors.
2. [Tiny input rounding](tiny_input_rounding_failure.json): after outward
   rounding to a fixed 512-bit grid, a ~10⁻²¹⁴ positive tail upper bound
   becomes about 7.46×10⁻¹⁵⁵. An auxiliary <10⁻²⁰⁰ check was therefore
   invalid. The entire enlarged error is propagated, and <10⁻¹⁴⁰ is the
   corrected auxiliary size check.
3. [Exponential interval sign](exponential_sign_failure.json): an enclosing
   ball of a positive exponential can cross zero. Requiring its lower
   endpoint to be positive rejected a valid over-enclosure. Retain the
   entire interval in the computation, including its negative endpoint.

4. [Audit whitespace](audit_whitespace_failure.json): the scope disclaimer
   was present across a line break; the text check now normalizes whitespace.
   The failed audit stopped before freezing any files.

In all four cases the generator requirement remains **strictly below
−1/50** on every whole cell. No producer value, cusp data, previous
frozen package, or mathematical acceptance threshold was changed.
The corrected checker passes 19,017 decisions. These are software
validation issues; their correction is not evidence that all analytic
arguments have received an independent expert review.
