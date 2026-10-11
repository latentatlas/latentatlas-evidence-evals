# R31 — Strict order by moment-preserving transport

The actual finite-slope optimal amplitude is strictly increasing on the
exact cusp arc [−1/64,0], for every M≥2×10⁻⁵, with no minimum driver
separation. The proof uses exact feasible transport and a validated
contraction inequality on the whole half-line. Earlier packages remain
immutable. This is a local publication-preparation package.

- [Türkçe bulgu](BULGU_NOTU_TR.md)
- [Analytic proof](PROOF.md)
- [Constants and outcomes](results/TABLE.md)
- [Scientific figure](figures/order_transport.png) and [caption](FIGURE_CAPTIONS.md)
- [Review and limits](REVIEW.md), [development failures](diagnostics/README.md)
- [Limited literature check](LITERATURE.md)
- [Audit](audit_report.json), [frozen manifest](manifest.json)

Use Python and the exact package versions in [requirements.txt](requirements.txt).
Run from the project root, with the project's Python environment active:

```sh
python -B research/cusp_order_transport/audit_snapshot.py
python -B research/cusp_order_transport/audit_snapshot.py --with-arb
```

The default audit replays the exact algebra, independent rational
reconstruction and direct numerical diagnostics, and calls the R30
prerequisite audit. `--with-arb` also regenerates all 1,024 whole u-cell
transcendental enclosures in a temporary directory and calls R30's
Arb-enabled prerequisite chain. Successful output must match the stored
mathematical artifacts byte for byte. The runtime environment is recorded
in [runtime.json](runtime.json). No network or private data are required.

To generate separate outputs for inspection (choose paths that do not exist):

```sh
python -B research/cusp_order_transport/check_algebra.py --output /tmp/r31-algebra-new.json
python -B research/cusp_order_transport/certify_transport.py --output-dir /tmp/r31-cover-new
python -B research/cusp_order_transport/check_bounds.py --cover-dir /tmp/r31-cover-new --output /tmp/r31-rational-new.json
python -B research/cusp_order_transport/direct_check.py --output /tmp/r31-direct-new.json
```

The rational checker accepts Arb transcendental enclosures as explicit
inputs; it does not independently prove the exp/pi implementation.
The direct mpmath checks use rounded previously computed points and a
truncated theta sum; they diagnose identities, not the infinite-domain
claim. The analytic proof, Arb/rational inequalities and frozen prior
results together support the theorem. This is not formal verification
or an external referee review. `--freeze` is an internal one-time creation
command and refuses to overwrite a frozen manifest.
