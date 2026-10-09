"""Read-only local replay and preserved downstream regressions."""
import argparse
from datetime import datetime, timezone
import json
import subprocess
import sys
from contract import ROOT, PREDECESSOR
from audit import sha

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--write",action="store_true")
    args=p.parse_args()
    jobs=[
      ("cancellation_and_arm_binding_tests",ROOT,["run_tests.py"]),
      ("cancellation_raw_qualification",ROOT,["qualify.py"]),
      ("separate_stdlib_http_lifecycle_bytes",ROOT,["crosscheck_cancel.py"]),
      ("original_eight_arm_binding",ROOT,["bind_arms.py"]),
      ("preserved_drain_confirmation_and_predecessor_regressions",PREDECESSOR,["verify_all.py"]),
    ]
    paths=[p for p in ROOT.iterdir() if p.suffix in {".py",".md",".json"} and p.name!="VALIDATION.json"]
    hashes={p.name:sha(p) for p in paths};results=[]
    for name,cwd,parts in jobs:
        cmd=[sys.executable,"-B",*parts]
        child=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=360)
        results.append(dict(name=name,cwd=str(cwd),command=cmd,exit_code=child.returncode,stdout=child.stdout,stderr=child.stderr))
        print(json.dumps(dict(check=name,exit_code=child.returncode)),flush=True)
    unchanged=all(sha(ROOT/n)==h for n,h in hashes.items())
    result=dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),
                status="passed" if unchanged and all(r["exit_code"]==0 for r in results) else "failed",
                checks=results,local_artifact_hashes=hashes,local_artifacts_unchanged=unchanged,
                provider_calls=0,new_native_episodes=0,catalogue_completion_changed=False)
    if args.write:
        with (ROOT/"VALIDATION.json").open("x") as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(dict(status=result["status"],checks=len(results),artifacts_unchanged=unchanged)))
    return 0 if result["status"]=="passed" else 1

if __name__=="__main__":raise SystemExit(main())

