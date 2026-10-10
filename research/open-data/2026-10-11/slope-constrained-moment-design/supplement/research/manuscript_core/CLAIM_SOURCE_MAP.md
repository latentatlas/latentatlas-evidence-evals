# R19 — Claim-to-source map

21 September 2026. Section and label identifiers refer to `manuscript.tex`.
This map documents a new exposition of existing research, not a new
computation or a claim that an audit substitutes for proof. Exact SHA-256
identities are in [inputs.json](inputs.json). All paths below resolve within
the accompanying research archive.

| Manuscript claim | Primary research source | Evidence and limitation |
|---|---|---|
| Equations `target`, `cost`: coordinate, moments, amplitude, slope | [R11 §§1,3](../kernel_design_principle/PROOF.md), [R13 §1](../kernel_slope_budget/PROOF.md) | Definitions; no mass normalization or relocated zero |
| Equation `bangbang`: δ*=f/D* and sign witness | [R11 Theorem 2](../kernel_design_principle/PROOF.md), [R15 §1](../kernel_slope_asymptotics/PROOF.md) | Classical duality; uniqueness only with residual nonzero almost everywhere |
| Equations `krdual`, `normalization` | [R18 complete equivalence](../slope_equivalence_review/EQUIVALENCE_MAP.md) | Classical Sion argument on locally uniform compact test class; no finite-M dual-attainment claim |
| H1–H3 and Theorem `thm:asymptotic` | [R15 §§1–3](../kernel_slope_asymptotics/PROOF.md) | Conditional theorem, not all positive kernels |
| Lower bound `gap` and finite-subset limiting order | [R15 §2](../kernel_slope_asymptotics/PROOF.md) | Applies to every feasible h; does not presuppose optimal ramp form |
| Exact center correction and summable C² smoothing | [R15 §3](../kernel_slope_asymptotics/PROOF.md), [R17 §1](../slope_chain_review/PROOF_ADDENDUM.md) | Explicit majorants; no C³ assumption |
| Every sufficiently large slope, not only a subsequence | [R15 §3](../kernel_slope_asymptotics/PROOF.md) | α′=O(a), local inversion of α/a |
| Kernel, family, analyticity and heat identities | [R01 §§1–2](../cusp_verified/PROOF.md), [R11 §1](../kernel_design_principle/PROOF.md) | h is fixed independently of moving parameters |
| Exact Q, f₃>0, f₄<0 and cusp rank | [R01 §3](../cusp_verified/PROOF.md), [C1](../cusp_verified/results/quartic_cusp_certificate.json) | Exact dyadic center, uniqueness box and smaller localization radius distinguished |
| Rank-three determinant `rank` | [R11 §4](../kernel_design_principle/PROOF.md) | Derived from derivative identities; order ≥4 alone is insufficient |
| Proposition `prop:smooth` | [R11 §4](../kernel_design_principle/PROOF.md), [R13 §4](../kernel_slope_budget/PROOF.md) | Same infimum at every M>0; no smooth attainment claimed |
| Dual optimizer localization and global uniqueness | [R15 §4](../kernel_slope_asymptotics/PROOF.md), [C3](../kernel_slope_asymptotics/results/asymptotic_certificate.json) | Uniform local strong convexity plus global convexity; not finite-M primal uniqueness |
| 28 switches, 113 sign leaves, selected rank | [C3 checker](../kernel_slope_asymptotics/results/asymptotic_check.json) | Bounds uniform in exact-Q and optimizer enclosure |
| Infinite tail switches, separation, summability | [R15 §§4–5](../kernel_slope_asymptotics/PROOF.md) | Analytic phase argument and double exponential derivative envelopes |
| Table `tab:cert`, δ* bracket | [C2 checker](../kernel_norm_threshold/results/threshold_check.json) | Generated TeX constants; dual/primal enclosure directions preserved |
| Table `tab:cert`, Γ and C* | [C3 checker](../kernel_slope_asymptotics/results/asymptotic_check.json) | Generated TeX constants; includes infinite tail |
| Theorem `thm:remainder` | [R16 §§1–6](../kernel_slope_remainder/PROOF.md), [C4 checker](../kernel_slope_remainder/results/remainder_check.json) | All M≥0.00002; no sharp M⁻³ assertion |
| Definitions B₂, A₃, A₄ and their index sets | [R16 §2](../kernel_slope_remainder/PROOF.md), [R17 §3 correction](../slope_chain_review/PROOF_ADDENDUM.md) | A₄ is a finite three-center sum, unlike B₂ and A₃ |
| Contraction implies S=0; continuous parameter family | [R16 §3](../kernel_slope_remainder/PROOF.md), [R17 §2](../slope_chain_review/PROOF_ADDENDUM.md) | B invertibility and continuous extension at a=0 written explicitly |
| Upper absorption and lower positive-part argument | [R16 §§4–5](../kernel_slope_remainder/PROOF.md), [R17 §4](../slope_chain_review/PROOF_ADDENDUM.md) | α factor retained; negative Taylor lower weights cause no sign reversal |
| Total threshold and relative-excess error | [C4 checker](../kernel_slope_remainder/results/remainder_check.json), [R19 arithmetic](data_checks.json) | Exact rational recombination checks printed endpoints and 0.1178% |
| Appendix derivative tails and trusted arithmetic | [R01 §2](../cusp_verified/PROOF.md), [R16 §6](../kernel_slope_remainder/PROOF.md) | Analytic bounds + Arb; hashes and mpmath checks are not a formal proof |
| Background, nearest literature and priority limit | [R17 literature](../slope_chain_review/LITERATURE.md), [R18 literature](../slope_equivalence_review/LITERATURE.md) | Read portions recorded; not an exhaustive novelty proof |
| Figures 1–2 | [R15 captions](../kernel_slope_asymptotics/FIGURE_CAPTIONS.md) | Unchanged source PNGs; schematic and certified-interval midpoint plot |
| Figure 3 | [R16 captions](../kernel_slope_remainder/FIGURE_CAPTIONS.md) | Unchanged PNG; rigorous band with separate numerical witness |

## Bibliography additions for numerical software

The two Johansson references document the arithmetic and quadrature used
by the existing producer code. They do not supply our analytic theorem.

- Fredrik Johansson, *Arb: efficient arbitrary-precision midpoint-radius
  interval arithmetic*, IEEE Transactions on Computers 66(8) (2017),
  1281–1292, DOI 10.1109/TC.2017.2690633. Checked against the
  [author's publication listing](https://fredrikj.net/) and
  [author's preprint record](https://arxiv.org/abs/1611.02831).
- Fredrik Johansson, *Numerical integration in arbitrary-precision ball
  arithmetic*, Mathematical Software — ICMS 2018, LNCS, 255–263.
  [Author's preprint record](https://arxiv.org/abs/1802.07942).

Access on 21 September 2026. The `www` author-page live fetch returned 403
after a search result supplied its publication metadata; the arXiv record
was directly accessible. No external full-text PDF is copied into this
manuscript package. R17/R18 record the versions and access limitations for
the other references.

## Deliberate exclusions

The earlier fold-region diagrams and cusp-continuation results remain in
the archive. Their detailed root windows are not transplanted to the
optimized kernels. Neither the flawed legacy TeX nor its old unvalidated
global claims are sources for this manuscript. No physical application,
AI training model, global cusp-curve theorem or degree equivalence is added.
