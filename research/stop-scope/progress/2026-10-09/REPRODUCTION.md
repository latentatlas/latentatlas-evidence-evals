# Offline replay and sharing policy

## Check the published package

Use Python 3.11 or newer. From this directory:

```sh
python3 -B verify_snapshot.py
python3 -B -m unittest test_snapshot -v
```

Expected main counts: 8 completed live episodes / 27 recorded provider requests; 16 confirmation conditions / 174 native inventory files; 8 cancellation conditions / 96 native inventory files. The verification itself makes **zero new provider calls** and runs **zero new native experiments**.

The verifier checks the export manifest; decompresses the complete selected streams into a temporary directory; runs the frozen standard-library lifecycle/cancellation crosschecks; rehashes every selected native and live file; recomputes live oracle results; binds live projections, tool selections, stop delivery and author reviews; compares the result with `FINDINGS.json`. Temporary replay directories are cleaned automatically. An exit code of zero means the published record and its stated outcomes agree, including intentionally failing controls.

The 14 packaging tests inject altered claims, cancellation targets, bytes, reviews, stop input and other defects. They are release QA, not 14 additional agent experiments. For a readable stream:

```sh
gzip -dc data/confirmation/local-matrix-v01/create-17-before_I_admission-false_omitted_worker_confirm/events.jsonl.gz
```

That optional viewing command prints the decompressed events without changing the packaged file. It is not a new experiment.

## What the files mean

- `EXPORT_MANIFEST.json`: SHA-256, byte size and original-source digest for every exported data/source/historical file. Event entries also include the decompressed digest and event count.
- `data/`: full selected streams, final native bytes, live request/response sharing copies, method fields and completion records.
- `FINDINGS.json`: freshly recomputed output from this package. `--write-findings` is a preparation option, not required for review.
- `source/confirmation/` and `source/cancellation/`: frozen matrix instrumentation and protocols. The two `crosscheck_*.py` files are portable offline checkers; the runners depend on other development modules and are supplied for inspection, not advertised as a turnkey fresh-execution package.
- `source/live/`: export-time adapter, codec and observation implementation for inspection. No login tool, credential, authenticated session or account state is redistributed.
- `historical/`: retained audit results, a projected incomplete attempt and dated open requirements. Historical original event hashes differ from privacy-transformed public event hashes. The portable verifier compares their audited counts and independently rechecks the sharing copy; it does not pretend the byte streams are identical.

## Transformation policy

`export_snapshot.py` reads retained sources, rechecks their digests after export and writes only the sharing directory. Original sources are never edited. It is needed only to prepare an export, not to review it.

1. The experiment-root prefix is mapped to `/workspace/stop-scope`; remaining personal home/temporary paths cause export to fail.
2. Account-preflight and batch-authorization events retain their sequence, timestamp and type but omit their private content.
3. Duplicate opaque `raw_b64`, billing-attribution fields, encrypted or other reasoning items are omitted. Omitted reasoning items retain an item digest. Raw SSE and authentication transport are not redistributed.
4. Method metadata is selected explicitly. Author reviews retain the exact reviewed response and hash, not private approval conversations.
5. Protection inventories for unrelated local files are omitted. Full original plan digests remain in the export manifest. `COMPLETION.json` event hashes are updated only to identify the sharing streams.
6. Native synthetic file bytes, role identities, event order, tool arguments, relevant HTTP receipts, output text and outcomes are retained. The published synthetic identifiers are experiment identities, not account credentials.

Hashes support traceability and detect changes against a pinned version; they do not provide a third-party signature, historical timestamp proof, provider-authentication proof or independent replication. Local raw originals remain retained by the author.

## License and contribution

Study-specific material uses the repository's [MIT license](source/licenses/PROJECT.txt). Embedded Open-SWE prompts and source-derived material retain [LangChain's MIT notice](source/licenses/OPEN_SWE.txt). The existing [pinned upstream tree](../../harness/application_probe/upstream) is available in the repository, not duplicated in this standalone snapshot.

Huseyin Buldurgan provided the research direction and explicit author reviews. LLM assistance contributed implementation, analysis support, packaging and writing. The replay paths are separate software checks, not independent human validation. No manuscript text or old release tag is changed by this snapshot.
