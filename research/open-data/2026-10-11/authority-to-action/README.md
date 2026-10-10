# Authority-to-Action — full open evidence

Original paper: DOI 10.5281/zenodo.21957491; v0.8.3.
The source snapshot is cca8f80ae6ef98ccf98049e36bd4be02d0529127.
This dated addendum adds the retained full-medium run records to that snapshot.
The original v0.8.3 manifests retain their historical
`raw_transcripts_published: false` declarations for the transcript-free analysis
package. The 11 October 2026 addendum makes the retained full run logs directly
available below; it does not rewrite those frozen manifests.

- `source/evals/data/authority_action_cases_v0_6.jsonl`: all 100 synthetic cases.
- `source/evals/authority_action_eval_v0_7.py`: task and scorer; earlier modules are retained dependencies.
- `source/data/authority_action_v0_8_3_analysis/`: transcript-free 600-row ledger, protocol, summary and hashes.
- `source/outputs/inspect/20260727T152524Z-full-medium-authorized/`: original provider transcripts, three repaired slots, checkpoints, analysis and final audit.
- `source/evals/experiment_manifest_v0_8_2.json`: full-run configuration; execution and repair authorizations accompany it.

From `source/`, recompute locally:

```sh
python3 -m latentatlas verify-authority-action-public-analysis --artifact-dir data/authority_action_v0_8_3_analysis
python3 -m latentatlas verify-authority-action-full-result --artifact-dir data/authority_action_v0_8_2_full_medium
```

The completed run contains 600 analytical slots from 603 gross attempts.
Repeated runs are clustered in 25 four-variant groups, not 600 independent cases.
API calls are not part of local verification. The result does not establish
independent validation, population safety or a universal model ranking.
Original code: MIT; author-owned data and explanatory material: CC BY 4.0.
