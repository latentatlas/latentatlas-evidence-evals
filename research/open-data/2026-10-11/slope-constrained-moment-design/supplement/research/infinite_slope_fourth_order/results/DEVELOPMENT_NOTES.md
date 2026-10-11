# Pre-freeze diagnostics

The first exact recurrence check rejected a hand-entered expected coefficient
2970 for x in the third theta derivative polynomial. Directly applying
T(P)=(5−4x)P+4xP' to P₂ gives 1650+300+1320=3270. The expected
constant was corrected to 3270 before writing any successful algebra or
numerical output. The recurrence implementation did not change. Earlier
frozen packages and their derivative formulas through order two were untouched.
This is a caught transcription/calculation error, not a successful first pass.

The first figure rendering placed its legends too close to the footer and
clipped the third legend entry. The canvas height and lower margin were
increased; the final figure was inspected again before freezing.
