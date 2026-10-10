# R19 — Editorial and verification record

21 September 2026. Scope: write a new manuscript core from the existing
research, preserving its hypotheses, constants and limits. No interval
producer was altered and no new mathematical result was introduced.

## Mathematical transfer review

The main asymptotic argument was checked against the R15 proof and the R17
addendum during writing. In particular the lower bound takes finite switch
sets before its limiting passage; the upper construction corrects moments
with selected centers; and its C² summability bounds do not assume C³ data.
The factor-two jumps and the unit-step coefficient -1/6 give Γ/3.

The explicit remainder was checked against R16 and R17. B is shown
invertible, the parameter fixed point extends continuously to a=0, and the
intermediate-value argument covers every M≥M₀. B₂ and A₃ use infinite
sums; A₄ uses only the three shifted centers. The lower-bound positive-part
argument and upper-bound identity D*e=αL are both retained.

The smooth geometric bridge combines the already recorded R11 right
inverse and R13 slope-margin/mollification argument. No new smooth-attainment
or finite-M optimizer uniqueness statement was added. The main text gives
the right inverse explicitly so a reader need not infer it from an internal
package number.

The KR support functional and Sion minimax step follow R18, with the
half-line compactness and integrable-tail argument stated. Classical tools
and the exponent alone are not presented as novel. The old TeX, RH claims,
unvalidated legacy continuation and an unproved physical application are
not imported.

## Fresh checks in this turn

1. All 19 previous manifests and 859 recorded entries matched their hashes.
2. The R15 rational checker was rerun into `verification/asymptotic_check.json`.
3. The R16 rational checker was rerun into `verification/remainder_check.json`.
4. The R18 exact normalization diagnostics were rerun into
   `verification/normalization_checks.json` (six groups).
5. The source constants were converted into TeX macros by code. Independent
   exact-rational recombination recovered both printed δ(M₀) endpoints
   and checked the relative-excess bound below 0.001178.
6. The final source has complete internal references and ten cited
   bibliography entries. The final compiler log contains no overfull boxes,
   missing characters, undefined control sequences or unresolved references.
7. The final 13-page PDF was rendered with Poppler. Every rendered page
   was inspected visually, including the three figures, both tables,
   inequality directions, numerical endpoints, page breaks and references.
   No clipping, overlap or missing glyph was observed. All extracted
   characters lie inside their page boundaries, and required theorem labels
   and printed numerical endpoints are present.

The recorded reruns reconstruct rational implications from existing
transcendental enclosures. They are not new Arb producer runs, independent
expert review or proof-assistant verification. The manuscript-specific
integrity checker validates provenance and successful recorded checks;
it cannot establish the analytic theorem by hashing files.

## Corrections made before closing this draft

The first build exposed four long display lines extending into the margin.
The locator coordinates were shortened (without changing exact inputs),
and multi-part bounds were split over lines. A Python string escape in the
generated M₀ macro was fixed before final rendering. The lower-gap display
lost a TeX spacing escape during initial authoring; its stray comma was
removed. The product `(w r*)(z±v)` was parenthesized explicitly. The first
figure caption now says a sign profile with values ±1, avoiding confusion
with the magnitude-one step used in the proof. Nonnegative parameter-box
upper coefficients in the tail bound are explicitly defined.

These were transcription, notation and layout fixes within the new draft;
the frozen mathematical results and numerical constants were unchanged.
Intermediate builds and page images are temporary and are removed after
the final review; their final-page hashes are recorded in `pdf_qa.json`.

## Remaining work before a public submission

External mathematical criticism and a deeper theorem-level priority
comparison remain open. The public research archive needs its license,
persistent identifier and metadata review. Author affiliation/contact and
any assistance disclosure must be finalized with the author and the chosen
journal. No affiliation, funding statement, public DOI or publication
acceptance has been invented. This turn performs no external submission.
