# R28 diagnostic history

`first_derivative_probe.json` is the first completed derivative enclosure.
It already proved a positive lower bound on the full R27 arc. It uses the
same `motion.py` source as the final certificate and is retained separately
from the authoritative `results/certificate.json`.

No failed numerical sign verdict was silently replaced in this package.
The later rational automatic-differentiation calculation and original-
integral finite differences both supported the derivative band.

A documentation patch was rejected atomically because an added line lacked
its patch marker. It changed no files; the patch was then split and applied
correctly. A joined prose line and figure prime notation were corrected
before generation/freeze. No computed result changed in these edits.

The first audit passed the mathematical checks and fresh replays, then
failed its literal prose marker `original ν`: the proof says
`original driver ν`. The old audit source and structured failure are
preserved in `audit_before_scope_marker_fix.py` and
`audit_scope_marker_failure.json`. The marker was corrected to the actual
wording; no evidence inequality was relaxed. A combined patch first failed
to match this README's wrapped line and made no changes; the exact line
was then read and patched. Historical audit source is not an entrypoint.
