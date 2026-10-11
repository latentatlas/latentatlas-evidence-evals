#!/usr/bin/env python3
"""Create a portable public copy; never edit the frozen source evidence.

Only local machine paths and their dependent SHA-256 references are rewritten.
The dependency graph is resolved before writing, so no stale hash is ignored.
Public replay is mandatory before release.
"""
import sys
sys.dont_write_bytecode=True
import argparse
import hashlib
import gzip
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
HEX=re.compile(rb"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
TEXT={".json",".md",".py",".txt",".tex",".log",".csv",".svg"}
def sha(b):return hashlib.sha256(b).hexdigest().encode()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args();out=args.output_dir.resolve()
    if out.exists():raise SystemExit("Choose a new public staging directory.")
    paths=set()
    for manifest in sorted((ROOT/"research").glob("*/manifest.json")):
        paths.add(manifest)
        for row in json.loads(manifest.read_text())["files"]:
            p=manifest.parent/row["path"]
            assert sha(p.read_bytes()).decode()==row["sha256"],str(p)
            paths.add(p)
    contents={};by_hash={};rels={}
    for p in sorted(paths):
        b=p.read_bytes();h=sha(b);rel=str(p.relative_to(ROOT));rels[rel]=h
        by_hash.setdefault(h,[]).append(rel)
        contents[h]=b
    # Exact strings only; numerical values and unrelated text are unchanged.
    cleaned={};payloads={};compressed=set()
    for h,b in contents.items():
        if any(n.endswith(".json.gz") for n in by_hash[h]):
            compressed.add(h)
            b=gzip.decompress(b)
            assert gzip.compress(b,compresslevel=9,mtime=0)==contents[h],by_hash[h]
        payloads[h]=b
        if h in compressed or any(Path(n).suffix in TEXT for n in by_hash[h]):
            b=b.replace(str(ROOT).encode(),b"/PROJECT")
            b=re.sub(rb"/Users/[^/\s\"'\\]+",b"/LOCAL_HOME",b)
        cleaned[h]=b
    final={};new_hash={};active=set()
    def resolve(h):
        if h in final:return
        if h in active:raise RuntimeError("Cyclic content-hash dependency")
        active.add(h)
        deps=set(HEX.findall(cleaned[h]))&set(contents)
        for dep in deps:resolve(dep)
        b=HEX.sub(lambda m:new_hash.get(m.group(),m.group()),cleaned[h])
        if h in compressed:b=gzip.compress(b,compresslevel=9,mtime=0)
        final[h]=b;new_hash[h]=sha(b);active.remove(h)
    for h in contents:resolve(h)
    changed=[]
    for rel,h in sorted(rels.items()):
        p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(final[h])
        if new_hash[h]!=h:
            changed.append({"path":rel,"original_sha256":h.decode(),
                            "public_sha256":new_hash[h].decode(),
                            "local_paths_replaced":cleaned[h]!=payloads[h],
                            "compressed_json":h in compressed})
    for manifest in (out/"research").glob("*/manifest.json"):
        for row in json.loads(manifest.read_text())["files"]:
            assert sha((manifest.parent/row["path"]).read_bytes()).decode()==row["sha256"]
    for p in out.rglob("*"):
        if p.is_file() and p.suffix in TEXT:
            assert b"/Users/" not in p.read_bytes(),str(p)
    report={"scope":"Metadata-only public derivative; mathematical assertions unchanged",
            "frozen_source_modified":False,"files":len(paths),
            "transformations":changed,
            "changed_python_files":[x["path"] for x in changed if x["path"].endswith(".py")],
            "all_public_manifest_entries_verified":True,
            "public_replay_pending":True}
    (out/"PUBLIC_COPY_PROVENANCE.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"files":len(paths),"changed":len(changed),
                      "changed_python_files":report["changed_python_files"],
                      "all_public_manifest_entries_verified":True}))
if __name__=="__main__":main()
