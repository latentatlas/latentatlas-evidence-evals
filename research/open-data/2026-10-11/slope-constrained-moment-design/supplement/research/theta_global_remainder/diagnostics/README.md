# R26 development diagnostics

The first independent distant-switch run passed the same 600 numerical
inequalities and 40 precision comparisons, but stored only its check
count for the root jets. Before freezing, the producer was improved to
store all normalized root jets explicitly. It was then rerun at both
precision levels. The initial successful output is preserved as
[direct_check_before_explicit_jet_records.json](direct_check_before_explicit_jet_records.json).
Its historical source hash does not match the improved current producer;
it is not the authoritative replay target. The complete new evidence is
[results/direct_check.json](../results/direct_check.json).

The first plot render failed because Matplotlib mathtext did not support
the `\tfrac` command in an annotation. It was replaced with `\frac{1}{4}`.
No mathematical bound or plotted data formula changed. The figure was
regenerated and visually inspected. This was a rendering failure, not
a failed mathematical inequality or a discarded adverse numerical result.

No mathematical assertion failure was observed in the retained R26 runs.
That statement records the checks made; it is not a claim that every
analytic error has been excluded.
