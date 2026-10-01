"""Portable locked-runtime parent; retains all outcomes, never overwrites evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys
import sysconfig
from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write_new(p, value):
    with p.open('x') as f:
        json.dump(value, f, indent=2)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run-id', required=True)
    p.add_argument('--arm', choices=['cancel_summary','drain_summary','scoped_summary','scoped_no_summary'], required=True)
    p.add_argument('--schedule', choices=['accepted_precommit','after_commit','unheld','drain_timeout'], required=True)
    p.add_argument('--seed', type=int, choices=[17,41], required=True)
    p.add_argument('--receipt-fault',choices=['none','bypass'],default='none',help='Explicit diagnostic only; bypass the old redelivery receipt')
    a = p.parse_args()
    if not re.fullmatch(r'[a-z][a-z0-9_-]{2,100}', a.run_id):
        raise ValueError('Unsafe run identifier')
    if sys.version_info[:2] != (3,14):
        raise RuntimeError('Pinned source requires Python 3.14')
    if a.schedule == 'drain_timeout' and a.arm != 'drain_summary':
        raise ValueError('Timeout control belongs to the drain arm')
    lock = LAB/'admission_probe/requirements.lock'
    requirements = [Requirement(line.rstrip(' \\')) for line in lock.read_text().splitlines()
                    if re.match(r'^[A-Za-z0-9_.-]+==', line)]
    wanted = {r.name:next(iter(r.specifier)).version for r in requirements
              if r.marker is None or r.marker.evaluate()}
    installed = {d.metadata['Name'].lower().replace('_','-'): d.version for d in importlib.metadata.distributions()}
    mismatches = {n: {'wanted':v,'installed':installed.get(n.lower().replace('_','-'))} for n,v in wanted.items()
                  if installed.get(n.lower().replace('_','-')) != v}
    if mismatches:
        raise RuntimeError('Runtime differs from locked distributions: '+json.dumps(mismatches))
    source = LAB/'application_probe'
    upstream = json.loads((source/'UPSTREAM_MANIFEST.json').read_text())
    if any(sha(source/'upstream'/n) != h for n,h in upstream['sha256'].items()):
        raise RuntimeError('Pinned upstream archive changed')
    native = Path(sysconfig.get_path('purelib'))/'deepagents'
    sources = {n:ROOT/n for n in ['run_probe.py','child_probe.py','factory_support.py','workload.py','PROTOCOL.md']}
    sources.update({'admission_factory_support.py':LAB/'admission_probe/factory_support.py',
                    'requirements.lock':lock,'UPSTREAM_MANIFEST.json':source/'UPSTREAM_MANIFEST.json',
                    'installed_backend_protocol.py':native/'backends/protocol.py',
                    'installed_filesystem.py':native/'backends/filesystem.py',
                    'installed_composite.py':native/'backends/composite.py',
                    'installed_filesystem_middleware.py':native/'middleware/filesystem.py'})
    hashes = {n:sha(f) for n,f in sources.items()}
    out = ROOT/'runs'/a.run_id
    out.mkdir(parents=True,exist_ok=False)
    (out/'files').mkdir(); (out/'instrument').mkdir()
    for n,f in sources.items():
        shutil.copy2(f,out/'instrument'/n)
        if sha(out/'instrument'/n)!=hashes[n]: raise RuntimeError('Snapshot changed')
    env = {'PATH':str(Path(sys.executable).parent)+':/usr/bin:/bin',
           'LANGGRAPH_RUNTIME_EDITION':'inmem','LANGSMITH_LANGGRAPH_API_VARIANT':'local_dev',
           'DATABASE_URI':':memory:','REDIS_URI':'fake','MIGRATIONS_PATH':'__inmem',
           'LANGGRAPH_AUTH_TYPE':'noop','LANGGRAPH_DISABLE_FILE_PERSISTENCE':'true',
           'LANGSMITH_TRACING':'false','LANGCHAIN_TRACING_V2':'false','OTEL_ENABLED':'false',
           'LANGGRAPH_LOGS_ENABLED':'false','LANGGRAPH_CLI_NO_ANALYTICS':'1','LANGGRAPH_NO_VERSION_CHECK':'true',
           'N_JOBS_PER_WORKER':'4','BG_JOB_ISOLATED_LOOPS':'false',
           'LANGSERVE_GRAPHS':json.dumps({'agent':'factory_support:get_graph','scheduler':'agent.scheduler:get_scheduler'}),
           'PYTHONNOUSERSITE':'1','PYTHONDONTWRITEBYTECODE':'1','LANGGRAPH_URL':'http://fixture.invalid','DISABLE_TRUSTSTORE':'true'}
    write_new(out/'manifest.json',{'started_utc':datetime.now(timezone.utc).isoformat(),'run_id':a.run_id,
        'arm':a.arm,'schedule':a.schedule,'seed':a.seed,'receipt_fault':a.receipt_fault,'source_sha256':hashes,'env':env,
        'python':sys.version,'executable':sys.executable,'locked_packages':wanted,
        'installed_packages':installed,'upstream_revision':upstream['revision'],
        'upstream_manifest_sha256':sha(source/'UPSTREAM_MANIFEST.json'),
        'scope':'local stop contracts; synthetic model/provider/task state; real source API/native files'})
    cmd=[sys.executable,'-I',str(ROOT/'child_probe.py'),str(out),a.arm,a.schedule,str(a.seed),a.receipt_fault]
    try:
        proc=subprocess.run(cmd,cwd=out,env=env,capture_output=True,text=True,timeout=180)
        result={'command':cmd,'exit_code':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'timeout':False}
    except subprocess.TimeoutExpired as e:
        result={'command':cmd,'exit_code':None,'stdout':(e.stdout or b'').decode(errors='replace'),
                'stderr':(e.stderr or b'').decode(errors='replace'),'timeout':True}
    result.update({'instrument_unchanged':all(sha(f)==hashes[n] for n,f in sources.items()),
                   'upstream_unchanged':all(sha(source/'upstream'/n)==h for n,h in upstream['sha256'].items()),
                   'finished_utc':datetime.now(timezone.utc).isoformat()})
    write_new(out/'PROCESS.json',result)
    print(json.dumps({'run':a.run_id,**{k:result[k] for k in ['exit_code','timeout','instrument_unchanged','upstream_unchanged']}}),flush=True)
    if result['exit_code']:
        print(result['stdout'][-2000:]+result['stderr'][-6000:])
    return 0 if result['exit_code']==0 and result['instrument_unchanged'] and result['upstream_unchanged'] else 1

if __name__=='__main__': raise SystemExit(main())
