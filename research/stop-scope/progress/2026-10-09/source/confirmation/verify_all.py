"""Read-only replay and predecessor regressions; optional new validation record."""
import argparse
from datetime import datetime, timezone
import json
import subprocess
import sys

from contract import ROOT, SOURCE, PREDECESSOR, HELPERS
from audit import sha


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--write", action="store_true")
    args = p.parse_args()
    jobs = [
        ("role_queue_tests", ROOT, ["run_tests.py"]),
        ("role_queue_raw_qualification_replay", ROOT, ["qualify.py"]),
        ("separate_stdlib_confirmation_bytes", ROOT, ["crosscheck_confirmation.py"]),
        ("preserved_role_source_core_cards_coverage_regressions", PREDECESSOR, ["verify_all.py"]),
        ("preserved_shared_fifo_qualification", HELPERS, ["verify_qualification.py"]),
    ]
    paths = [p for p in ROOT.iterdir() if p.suffix in {".py", ".md", ".json"} and p.name != "VALIDATION.json"]
    hashes = {p.name: sha(p) for p in paths}; results = []
    for name, cwd, parts in jobs:
        cmd = [sys.executable, "-B", *parts]
        child = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
        results.append({"name": name, "cwd": str(cwd), "command": cmd, "exit_code": child.returncode, "stdout": child.stdout, "stderr": child.stderr})
        print(json.dumps({"check": name, "exit_code": child.returncode}), flush=True)
    unchanged = all(sha(ROOT/n) == h for n, h in hashes.items())
    result = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "status": "passed" if unchanged and all(r["exit_code"] == 0 for r in results) else "failed",
              "checks": results, "local_artifact_hashes": hashes, "local_artifacts_unchanged": unchanged,
              "provider_calls": 0, "new_native_episodes": 0, "catalogue_completion_changed": False}
    if args.write:
        with (ROOT/"VALIDATION.json").open("x") as f: json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps({"status": result["status"], "checks": len(results), "artifacts_unchanged": unchanged}))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__": raise SystemExit(main())
