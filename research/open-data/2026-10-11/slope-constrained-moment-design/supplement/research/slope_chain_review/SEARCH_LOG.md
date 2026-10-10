# R17 — Search coverage and access record

Date: 21 September 2026. Purpose: positioning of R15–R16, not a
systematic or exhaustive priority review. Only primary research texts
were used for mathematical comparison; search snippets and secondary
aggregators were discovery aids. Results not listed in LITERATURE.md
were not promoted to supporting references.

Query families actually used:

- optimal control hard derivative rate constraint bang bang asymptotic value smoothing switching function
- minimum amplitude moment problem bounded derivative perfect spline asymptotics
- "bang-bang" "rate constraints" approximation
- "rate constrained" "bang" "optimal control" asymptotic
- "moment" "Lipschitz" "perfect splines"
- "Interpolation properties of generalized perfect splines" Karlin
- "Smooth Regularization of Bang-Bang Optimal Control Problems" Trélat
- "control derivative" "asymptotic" "bang-bang"
- "optimal control" "bounded derivatives" "approximation"
- "bang-bang" "Lipschitz" "regularization"
- "minimum norm" "moment" "Lipschitz" optimization
- "Karlin" "0367512" ams.org
- "moment problem" "minimum" "L∞" sign function duality
- "optimal control" "rate limits" "convergence"
- "A note on the minimum-norm in dual space" Zhou 2023 pdf
- "On the L1 extremal problem for entire functions" authors
- "bang-bang" "H1" "regularization" asymptotic
- "bang-bang" "derivative constraint" approximation
- "rate-constrained" "minimum-norm"
- "Near-minimum-time control design for flexible structures" pdf
- "Rate-Constrained" "Maximum Principle" arxiv

## Access and exclusions

- Karlin 1975: AMS PDF and article page failed; local HTTP request
  returned 403. The web tool could read the primary article PDF hosted
  on SciSpace. A local request to that mirror also returned 403;
  PDF screenshots failed. Used only the extracted §§7–8 text, not a
  secondary summary. Avoided relying on OCR-sensitive knot counts.
- Silva–Trélat 2010: initial no-tilde university link timed out;
  the author's tilde link succeeded. Download SHA-256 was
  `19c5ac2ffee2dbc0b29f83796a338ef51d96df1c127bb8b93bba8f2c12731e85`.
  Text extraction used bundled pdfplumber; p.2490 was rendered with
  Poppler and inspected. An initial optional PyMuPDF import was absent;
  no package was installed and the supported reader was used instead.
  Temporary paper and image were removed after review.
- Wachsmuth 2013: official ETNA full PDF accessible.
- von Daniels 2017: author arXiv full PDF accessible; this improves on
  R15's abstract-only reading, but does not mean every proof was audited.
- Yuditskii: publisher redirect failed; author arXiv primary text
  accessible. University metadata confirms journal year 2014; the
  preprint PDF's internally printed date is not used as publication year.
- Albassam 2002: DOI/publisher fetch failed. Author-uploaded full article
  text on ResearchGate used for §§II–IV; no downstream citing articles
  or generated related-publication summaries used as primary evidence.
- Zhou et al., DOI 10.1049/tje2.12277: publisher timed out. Discovery
  record only; no theorem from it was used to support the comparison.
- The 2016 implicit Euler paper retained in R15 was not upgraded from
  its earlier abstract/intro coverage. No negative novelty conclusion
  was based on not finding a matching title.

Read coverage and conclusions are recorded source by source in
[LITERATURE.md](LITERATURE.md). Full copyrighted papers and web outputs
are not redistributed in this package. No assertion is made that the
query list covers all terminology, languages or equivalent formulations.
