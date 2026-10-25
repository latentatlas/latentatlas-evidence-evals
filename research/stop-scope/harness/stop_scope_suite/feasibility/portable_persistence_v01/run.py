"""Fresh persistent-receiver experiments; offline unless --live is explicit."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ARMS = ("healthy", "source_stop", "memory_revoke", "durable_cancel", "durable_revoke")
PROFILES = ("normal", "alternate_final", "edit_final", "wrong_final", "early_O", "early_I")
FAULTS = ("none", "skip_restore_revocation", "broad_revoke", "omit_receipt")
CONDITIONS = tuple((a,"normal","none") for a in ARMS) + (
    ("durable_revoke","normal","skip_restore_revocation"),
    ("durable_revoke","normal","broad_revoke"), ("healthy","normal","omit_receipt"),
    ("healthy","wrong_final","none"), ("healthy","alternate_final","none"),
    ("durable_revoke","alternate_final","none"), ("healthy","edit_final","none"),
    ("durable_revoke","edit_final","none"), ("healthy","early_O","none"),
    ("healthy","early_I","none"),
)
def require(value, message):
    if not value: raise ValueError(message)
def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path, value):
    with Path(path).open("x") as f: json.dump(value, f, indent=2, ensure_ascii=False)
def inventory(root):
    result = {}
    for p in sorted(root.rglob("*")):
        require(not p.is_symlink(), "Symlink in evidence")
        if p.is_file() and "__pycache__" not in p.parts:
            result[str(p.relative_to(root))] = sha(p)
    return result
def verify_sources():
    hashes = read(HERE/"SOURCE_MANIFEST.json")["files"]
    actual = {str(p.relative_to(ROOT)) for p in (ROOT/"harness").rglob("*")
              if p.is_file() and p.name != "SOURCE_MANIFEST.json" and "__pycache__" not in p.parts}
    require(actual == set(hashes), "Source inventory has missing or extra files")
    for rel, digest in hashes.items():
        p = ROOT/rel
        require(p.resolve().is_relative_to(ROOT) and not p.is_symlink() and sha(p)==digest,
                "Source drift: " + rel)
    return hashes
def environment():
    return {"PATH":str(Path(sys.executable).parent)+":/usr/bin:/bin",
        "LANGGRAPH_RUNTIME_EDITION":"inmem","LANGSMITH_LANGGRAPH_API_VARIANT":"local_dev",
        "DATABASE_URI":":memory:","REDIS_URI":"fake","MIGRATIONS_PATH":"__inmem",
        "LANGGRAPH_AUTH_TYPE":"noop","LANGGRAPH_DISABLE_FILE_PERSISTENCE":"true",
        "LANGSMITH_TRACING":"false","LANGCHAIN_TRACING_V2":"false","OTEL_ENABLED":"false",
        "LANGGRAPH_LOGS_ENABLED":"false","LANGGRAPH_CLI_NO_ANALYTICS":"1","LANGGRAPH_NO_VERSION_CHECK":"true",
        "N_JOBS_PER_WORKER":"4","BG_JOB_ISOLATED_LOOPS":"false",
        "LANGSERVE_GRAPHS":json.dumps({"agent":"native_adapter:get_graph","scheduler":"agent.scheduler:get_scheduler"}),
        "PYTHONNOUSERSITE":"1","PYTHONDONTWRITEBYTECODE":"1","LANGGRAPH_URL":"http://fixture.invalid",
        "DISABLE_TRUSTSTORE":"true"}
def validate_live(config, arm):
    from comparison_config import max_requests
    required = {"model","reasoning_effort","max_requests","max_output_tokens","max_request_bytes"}
    require(set(config)==required, "Live config must contain exactly: " + ", ".join(sorted(required)))
    require(isinstance(config["model"],str) and 0<len(config["model"])<100, "Explicit model required")
    require(config["reasoning_effort"] in {"low","medium","high"}, "Unsupported reasoning effort")
    for field, minimum, maximum in (("max_requests",1,max_requests(arm)),("max_output_tokens",16,32768),
                                     ("max_request_bytes",1024,200000)):
        require(type(config[field]) is int and minimum<=config[field]<=maximum, "Invalid " + field)
    return config
def execute(out, arm="healthy", profile="normal", fault="none", *, live_config=None, api_key=None):
    from comparison_config import PROPOSAL, LIMITS, authorization, protocol_digest
    from bridge_dependencies import workload
    from review import audit
    require(arm in ARMS and profile in PROFILES and fault in FAULTS, "Unknown condition")
    require(fault not in {"skip_restore_revocation","broad_revoke"} or arm=="durable_revoke", "Fault needs durable revoke")
    require(not out.exists() and not out.is_symlink(), "Existing attempts are immutable; use a fresh output")
    require(out.parent.is_dir() and not out.parent.is_symlink(), "Existing real output parent required")
    require(not out.resolve().is_relative_to(ROOT), "Write outputs outside the frozen source tree")
    live = live_config is not None
    if live:
        validate_live(live_config, arm)
        require(profile=="normal" and fault=="none", "Live deviations are not supported")
        require(isinstance(api_key,str) and api_key.strip() and "\n" not in api_key, "Explicit API key required")
    require(sys.version_info[:2]==(3,14), "Use Python 3.14 for the pinned Open-SWE runtime")
    frozen = verify_sources()
    os.umask(0o077)
    out.mkdir(); (out/"files").mkdir()
    plan = dict(version="portable-persistence-v0.1", arm=arm,profile=profile,fault=fault,seed=17,
        live=live,live_config=live_config,protocol=PROPOSAL,protocol_sha256=protocol_digest(),
        authorization=authorization(17,arm,live=live),source_hashes=frozen,automatic_retry=False,
        created_at_utc=datetime.now(timezone.utc).isoformat(),source_pin=PROPOSAL["source_pin"],
        actual_provider_calls=None if live else 0, actor="live O/I/N/S; programmed C" if live else "programmed O/I/N/S/C",
        restart="clean_receiver_process_restart",
        expected_final={r:workload.report(workload.make_job(17,j),"final")
            for r,j in {"O":"old","I":"independent","N":"human","C":"new_background"}.items()},
        expected_partial={r:workload.report(workload.make_job(17,j),"partial")
            for r,j in {"O":"old","I":"independent","N":"human","C":"new_background"}.items()},
        environment=dict(python=sys.version,platform=platform.platform(),executable=sys.executable))
    save(out/"PLAN.json",plan)
    env=environment()
    # Only this explicit branch passes the key. Never serialize the key or inherited environment.
    if live: env["STOP_SCOPE_API_KEY"]=api_key
    command=[sys.executable,"-B","-I",str(HERE/"supervisor.py"),str(out)]
    save(out/"PROCESS_PLAN.json",dict(command=command,environment=environment(),credential_passed=live))
    timed=False
    with (out/"stdout.txt").open("x") as stdout,(out/"stderr.txt").open("x") as stderr:
        proc=subprocess.Popen(command,cwd=out,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
        try: code=proc.wait(timeout=LIMITS["process_watchdog_seconds"] if live else 360)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            timed=True
            os.killpg(proc.pid,signal.SIGTERM)
            try: proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGKILL); proc.wait(timeout=10)
            code=proc.returncode
    save(out/"PROCESS.json",dict(supervisor_pid=proc.pid,exit_code=code,timed_out=timed))
    report=audit(out)
    save(out/"AUDIT.json",report)
    unchanged = verify_sources()==frozen
    save(out/"COMPLETION.json",dict(exit_code=code,timed_out=timed,sources_unchanged=unchanged,
         evidence_status=report["evidence_status"],transport_status=report["transport_status"],
         artifact_hashes=inventory(out)))
    print(json.dumps(dict(folder=str(out),exit_code=code,evidence=report["evidence_status"],
          transport=report["transport_status"],errors=report["errors"]+report["transport_errors"])),flush=True)
    return report,code
def batch(out, smoke=False, full=False):
    require(not out.exists(), "Use a fresh batch output")
    out.mkdir()
    conditions=CONDITIONS if full else CONDITIONS[:2] if smoke else CONDITIONS[:5]
    save(out/"PLAN.json",dict(conditions=conditions,actual_provider_calls=0,source_hashes=verify_sources(),
         automatic_retry=False,version="portable-persistence-v0.1"))
    records=[]
    for arm,profile,fault in conditions:
        name="--".join((arm,profile,fault))
        report,code=execute(out/name,arm,profile,fault)
        records.append(dict(cell=name,**report))
        if code or report["transport_status"]!="recorded" or (report["evidence_status"]!="recorded" and fault!="omit_receipt"):
            break
    attempted={r["cell"] for r in records}
    for c in conditions:
        name="--".join(c)
        if name not in attempted: records.append(dict(cell=name,evidence_status="not_attempted"))
    save(out/"RESULTS.json",dict(records=records,actual_provider_calls=0,new_live_episodes=0,independent_replication=False))
    save(out/"COMPLETION.json",dict(artifact_hashes=inventory(out)))
    return all(r["evidence_status"]=="recorded" or ("omit_receipt" in r["cell"] and r["evidence_status"]=="needs_review")
               for r in records) and all(r.get("transport_status")=="recorded" for r in records)
def cli():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,required=True)
    group=p.add_mutually_exclusive_group()
    group.add_argument("--batch",action="store_true")
    group.add_argument("--smoke",action="store_true")
    group.add_argument("--qualification",action="store_true")
    p.add_argument("--arm",choices=ARMS,default="healthy")
    p.add_argument("--profile",choices=PROFILES,default="normal")
    p.add_argument("--fault",choices=FAULTS,default="none")
    p.add_argument("--live",action="store_true")
    p.add_argument("--live-config",type=Path)
    p.add_argument("--acknowledge-api-cost",action="store_true")
    p.add_argument("--healthy-reference",type=Path)
    a=p.parse_args()
    require(not a.live_config or a.live, "--live-config requires --live")
    require(not a.live or (a.live_config and a.acknowledge_api_cost), "Live requires config and explicit API cost acknowledgement")
    require(not a.live or not(a.batch or a.smoke or a.qualification), "Run live cells separately, after inspecting each result")
    config=read(a.live_config) if a.live else None
    key=None
    if a.live:
        validate_live(config,a.arm)
        key=os.environ.get("OPENAI_API_KEY")
        require(key, "Set your own OPENAI_API_KEY explicitly; local account stores are never read")
        if a.arm!="healthy":
            require(a.healthy_reference is not None, "A fresh live healthy reference is required")
            from verify import verify_episode
            ref=verify_episode(a.healthy_reference.resolve())
            plan=read(a.healthy_reference/"PLAN.json")
            require(plan["source_hashes"]==verify_sources(), "Healthy reference uses different experiment sources")
            require(plan["live"] and plan["arm"]=="healthy" and plan["live_config"]==config,
                    "Reference must use the same live configuration")
            require(ref["evidence_status"]==ref["transport_status"]=="recorded" and
                    ref["outcomes"]["planned_checkpoint_observed"] and
                    all(ref["outcomes"]["roles"][r]["final_correct_at_close"] for r in ("O","I","N")),
                    "Healthy reference is not qualified")
    if a.batch or a.smoke or a.qualification:
        ok=batch(a.out.resolve(),smoke=a.smoke,full=a.qualification)
    else:
        report,code=execute(a.out.resolve(),a.arm,a.profile,a.fault,live_config=config,api_key=key)
        ok=code==0 and report["transport_status"]=="recorded" and (report["evidence_status"]=="recorded" or a.fault=="omit_receipt")
    return 0 if ok else 1
if __name__=="__main__": raise SystemExit(cli())
