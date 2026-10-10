# R16 development diagnosis

The first rational checker compared inherited parameter/root boxes
by complete JSON equality. Reconstructing an Arb ball can round its
radius outward by one magnitude unit, even when the exact midpoint
and inherited data identity are unchanged. For example, one radius
changed from 971687265·2^-319 to 485843633·2^-318, which is a slightly
larger enclosing radius.

The appropriate mathematical requirement is containment of the
inherited interval, together with the input-file hash. The revised
checker verifies both. The producer, its recorded certificate and
the stated scientific constants did not change.

Archived first checker: `check_before_enclosure_identity.py`.
Archived failure log: `enclosure_identity_failure.log`.

All later rational, separate-derivative, numerical-design and algebra
checks passed. Earlier frozen research packages were not edited.
