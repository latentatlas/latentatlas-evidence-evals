#!/usr/bin/env python3
"""Verify exactly the release-listed bytes; this does not prove the theorems."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/"SHA256SUMS.json").read_text())
for row in data["files"]:
    p=ROOT/row["path"]
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=row["sha256"]:
        raise SystemExit("Mismatch: "+row["path"])
print(json.dumps({"listed_files_verified":len(data["files"]),
                  "mathematical_proof_verified":False}))
