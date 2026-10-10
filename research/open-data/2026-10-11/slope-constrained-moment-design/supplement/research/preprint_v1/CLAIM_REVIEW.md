# Claim-by-claim internal review

23 September 2026. This is an internal mathematical/editorial check, not an
external referee report or formal verification. Numbering refers to the new
preprint. The original early .tex article is not the paper being presented.

| Claim | Argument checked | Computational evidence | Remaining limit |
|---|---|---|---|
| δ₀ = f/D | Sign certificate realizes the bound f ≤ D‖g‖∞. | Theta sign equations and D bounds. | Needs the stated certificate. |
| Balanced ramp lemma 2.2 | Opposite endpoint signs; primitive vanishes at both ends; correct integration-by-parts inequality. | Exact finite cases and R21. | Free endpoints, disjoint neighborhoods. |
| Γ,G,B,R converge | Common root derivative controls Q/r; crossing bound controls t/r; weighted E(1+K)² is summable. | R23 and theta tail algebra. | Not a consequence of L¹ alone. |
| Main theorem 2.1 | Two displacement bounds give domination of summed Taylor terms and the normalized remainder. | Exact R22/R23 algebra. | Analytic interchange needs expert review. |
| Exact moment repair | Finite invertible center Jacobian, shrinking contraction ball, e=o(a²), target change o(a⁴). | R21; effective theta contraction. | No infinite optimizer uniqueness claim. |
| Fourth coefficient | Target R−½vᵀGv; lower moment B−Gv; a=A/M yields scalar coefficient 3t²−e. | Fresh exact algebra and integrals. | General remainder is little-o. |
| P≥0 and basis invariance | Positive definite G and congruence under a basis change. | Algebraic identity. | Fixed-residual support interpretation. |
| Finite unique optimizer | Exact implicit moment solve and support equality case. | R21 replay. | Large M and finite simple switches. |
| Examples | Polynomial/odd integrals; C² non-C³ example has M⁻⁷ᐟ² term. | Fresh R22 integrals: 16 budgets, 32 runs, 132 value comparisons. | Figure curves are diagnostics. |
| Theta theorem 4.1 | Derivative dictionary, connected branch, phase/tail bounds, primal/dual estimates. | R24–R30, fresh Arb dependency chain. | Only ν∈[−1/64,0], M≥2e−5. |
| Every-budget error bound | Fix a during repair; auxiliary scalar polynomial avoids prefix-continuity assumption. | 32 whole driver cells. | No M⁻⁶ coefficient identified. |
| Coefficient motion | Differentiate dual and roots; D′ cancellation; retain root motion in Γ′. | R28/R29 and R30 rational AD. | Not the derivative of δν(M). |
| Transport theorem 5.1 | Includes Jacobian η⁻¹, η^(m+1), positive commutator, W=ηT+a₀|Tᵤ|. | R31 algebra/composition diagnostics. | Explicit regularity and full-domain bound. |
| Strict order corollary 5.2 | Apply transport to attained optimizer; U/M₀<a₀; integrate κ bound. | 1024 spatial cells and analytic tail. | Does not require a smooth optimizer selection. |
| M₀ error and rate | Exact rational divisions and products. | New fraction checks. | Coefficient rounding is additional. |
| Reproducibility | Frozen originals and public derivative are checked separately. | Logs, hashes, transformation map. | Scripts do not certify all analytic prose. |

## Corrections during assembly

- The initial caption described an unnormalized residual although the graph
  divided by |C₄|. It now states the actual normalization and limits ±1.
- Two overlong equations were split; references were moved to a final page.
- The transport theorem now spells out regularity and integrability.
- The current Lessard–Pugliese record gives Linear Algebra and its Applications
  728 (2026), 26–46; the bibliography follows that record.
- The first public-copy replay caught old checksum references inside compressed
  JSON. Those payloads are now transformed before deterministic recompression;
  dependent hashes are propagated. The failed attempt is retained locally.
  No mathematical inequality was weakened to obtain a passing check.

No counterexample or mathematical contradiction was found in the selected
current theorem chain during this pass. This is a bounded internal finding,
not a guarantee. Literature priority and the infinite-switch proof need
independent expert scrutiny.
