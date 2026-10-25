"""Install the pinned research runtime in a NEW directory; never reads model credentials."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import venv

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MAIN=Path("harness/stop_scope_suite/feasibility/portable_persistence_v01")
KNOWN_CONFLICTS={
    "langchain-e2b 0.0.6 has requirement deepagents<0.7.0,>=0.6.0, but you have deepagents 0.7.13.",
    "e2b 2.34.0 has requirement wcmatch<11,>=10.1, but you have wcmatch 11.0.",
}
def save(path,value):
    with path.open("x") as f: json.dump(value,f,indent=2)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def setup(dest):
    if sys.version_info[:2]!=(3,14) or os.name!="posix":
        raise ValueError("This pinned runtime requires Python 3.14 on macOS/Linux")
    if dest.exists() or dest.is_symlink(): raise ValueError("Destination must be new; failed attempts are retained")
    manifest=json.loads((ROOT/MAIN/"SOURCE_MANIFEST.json").read_text())
    for rel,h in manifest["files"].items():
        p=ROOT/rel
        if not p.resolve().is_relative_to(ROOT) or p.is_symlink() or sha(p)!=h:
            raise ValueError("Source inventory differs: "+rel)
    dest.mkdir(mode=0o700)
    report=dict(status="started",python=sys.version,platform=platform.platform(),
        started_at_utc=datetime.now(timezone.utc).isoformat(),
        source_manifest_sha256=sha(ROOT/MAIN/"SOURCE_MANIFEST.json"),provider_calls=0,
        historical_dependency_overrides=sorted(KNOWN_CONFLICTS))
    save(dest/"SETUP_PLAN.json",report)
    runtime=dest/"runtime"
    env={"PATH":os.environ.get("PATH","/usr/bin:/bin"),"PYTHONNOUSERSITE":"1",
         "PYTHONDONTWRITEBYTECODE":"1","PIP_DISABLE_PIP_VERSION_CHECK":"1"}
    try:
        for rel in [*manifest["files"],str(MAIN/"SOURCE_MANIFEST.json")]:
            target=runtime/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,target)
        venv.EnvBuilder(with_pip=True).create(dest/".venv")
        python=dest/".venv/bin/python"
        lock=runtime/"harness/admission_probe/requirements.lock"
        command=[str(python),"-m","pip","install","--require-hashes","--no-deps","-r",str(lock)]
        with (dest/"install.log").open("x") as log:
            result=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
        if result.returncode: raise ValueError("Pinned dependency installation failed; see install.log")
        check=subprocess.run([str(python),"-m","pip","check"],env=env,text=True,capture_output=True,timeout=60)
        (dest/"pip-check.txt").write_text(check.stdout+check.stderr)
        conflicts=set(check.stdout.strip().splitlines()) if check.returncode else set()
        if conflicts!=KNOWN_CONFLICTS: raise ValueError("Dependency check differs from documented historical overrides")
        packages=subprocess.run([str(python),"-m","pip","list","--format=json"],env=env,text=True,capture_output=True,check=True,timeout=60)
        save(dest/"PACKAGES.json",json.loads(packages.stdout))
        (dest/"runs").mkdir()
        report.update(status="installed_with_documented_historical_overrides",dependency_check_exit_code=check.returncode,
                      manifest_verified=all(sha(runtime/r)==h for r,h in manifest["files"].items()))
        if not report["manifest_verified"]: raise ValueError("Runtime source changed during setup")
        print(json.dumps(dict(python=str(python),runner=str(runtime/MAIN/"run.py"),
             verifier=str(runtime/MAIN/"verify.py"),runs=str(dest/"runs"),status=report["status"]),indent=2))
    except BaseException as exc:
        report.update(status="setup_failed",error_type=type(exc).__name__,error=str(exc))
        raise
    finally: save(dest/"SETUP_RESULT.json",report)
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--dest",type=Path,required=True)
    a=p.parse_args();setup(a.dest.resolve())
