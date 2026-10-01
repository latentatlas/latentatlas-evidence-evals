"""Fresh locked installation and relocated execution, not independent human review."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
LAB=ROOT.parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,value):
    with p.open('x') as f: json.dump(value,f,indent=2)
def dependency_review(step):
    expected={
        'The package `langchain-e2b` requires `deepagents>=0.6.0,<0.7.0`, but `0.7.13` is installed',
        'The package `e2b` requires `wcmatch>=10.1,<11`, but `11.0` is installed'}
    observed={line.strip() for line in step.get('stderr','').splitlines() if line.startswith('The package ')}
    if step['exit_code']==0 and not step['timeout']:
        return {'accepted':True,'classification':'no_conflicts','conflicts':[]}
    known=(step['exit_code']==1 and not step['timeout'] and observed==expected
           and 'Found 2 incompatibilities' in step.get('stderr',''))
    return {'accepted':known,'classification':'known_upstream_override_conflicts' if known else 'unexpected_dependency_failure',
            'conflicts':sorted(observed),'full_dependency_compatibility_claimed':False}
def run(cmd,cwd,timeout=600):
    env={'PATH':str(Path(cmd[0]).parent)+':/usr/bin:/bin','LANGSMITH_TRACING':'false',
         'LANGCHAIN_TRACING_V2':'false','PYTHONDONTWRITEBYTECODE':'1',
         'UV_NO_PROGRESS':'1','UV_PYTHON_DOWNLOADS':'never'}
    try:
        p=subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,text=True,timeout=timeout)
        return {'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'timeout':False}
    except subprocess.TimeoutExpired as e:
        return {'command':cmd,'exit_code':None,'stdout':(e.stdout or b'').decode(errors='replace'),
                'stderr':(e.stderr or b'').decode(errors='replace'),'timeout':True}
def main():
    p=argparse.ArgumentParser(); p.add_argument('--id',required=True);p.add_argument('--mode',choices=['prepare','run'],required=True)
    a=p.parse_args()
    if not re.fullmatch(r'clean-v\d{2}',a.id): raise ValueError('Fresh clean-vNN ID required')
    dest=ROOT/'reproductions'/a.id
    if a.mode=='prepare':
        dest.mkdir(parents=True,exist_ok=False)
        lock=dest/'requirements.lock';shutil.copy2(LAB/'admission_probe/requirements.lock',lock)
        uv=shutil.which('uv')
        if not uv: raise RuntimeError('uv not found; no alternative implicit installer')
        original=LAB/'admission_probe/.venv/bin/python'
        prep=run([uv,'venv','--python',str(original.resolve()),str(dest/'.venv')],dest)
        steps=[prep]
        if prep['exit_code']==0:
            steps.append(run([uv,'pip','sync','--python',str(dest/'.venv/bin/python'),'--require-hashes',str(lock)],dest))
            steps.append(run([uv,'pip','check','--python',str(dest/'.venv/bin/python')],dest))
        review=dependency_review(steps[2]) if len(steps)==3 else {'accepted':False,'classification':'incomplete_setup'}
        save(dest/'SETUP.json',{'created_utc':datetime.now(timezone.utc).isoformat(),
             'requirements_sha256':sha(lock),'steps':steps,
             'dependency_review':review,
             'scope':'fresh venv on same host/base Python; public package cache may be reused; not independent operator'})
        print(json.dumps({'destination':str(dest),'steps':[{'exit_code':x['exit_code'],'tail':x['stderr'][-1400:]} for x in steps]}))
        return 0 if len(steps)==3 and steps[0]['exit_code']==steps[1]['exit_code']==0 and review['accepted'] else 1
    setup=json.loads((dest/'SETUP.json').read_text())
    if setup['steps'][0]['exit_code'] or setup['steps'][1]['exit_code']:
        raise RuntimeError('Fresh installation incomplete')
    review=dependency_review(setup['steps'][2])
    if not review['accepted']: raise RuntimeError('Unexpected dependency check failure: '+json.dumps(review))
    save(dest/'DEPENDENCY_REVIEW.json',{'setup_sha256':sha(dest/'SETUP.json'),**review})
    if sha(dest/'requirements.lock')!=setup['requirements_sha256'] or sha(LAB/'admission_probe/requirements.lock')!=setup['requirements_sha256']:
        raise RuntimeError('Lock changed after installation')
    relocated=dest/'lab';relocated.mkdir(exist_ok=False)
    targets=[]
    for f in ROOT.iterdir():
        if f.is_file() and f.suffix in {'.py','.md','.json'}: targets.append((f,Path('stop_contract_study')/f.name))
    for n in ['factory_support.py','requirements.lock']:
        targets.append((LAB/'admission_probe'/n,Path('admission_probe')/n))
    targets.append((LAB/'application_probe/UPSTREAM_MANIFEST.json',Path('application_probe/UPSTREAM_MANIFEST.json')))
    manifest=json.loads((LAB/'application_probe/UPSTREAM_MANIFEST.json').read_text())
    for n,h in manifest['sha256'].items():
        f=LAB/'application_probe/upstream'/n
        if sha(f)!=h: raise RuntimeError('Upstream changed')
        targets.append((f,Path('application_probe/upstream')/n))
    files={}
    for source,relative in targets:
        target=relocated/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        files[str(relative)]=sha(target)
        if sha(source)!=files[str(relative)]: raise RuntimeError('Copy mismatch')
    save(dest/'BUNDLE.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'files_sha256':files})
    python=str(dest/'.venv/bin/python');stage=relocated/'stop_contract_study'
    commands=[[python,'-B',str(stage/'verify.py'),'--qa-id','qa-pre-clean-v01'],
              [python,'-B',str(stage/'run_matrix.py'),'--version','v02'],
              [python,'-B',str(stage/'run_probe.py'),'--run-id','receipt-fault-v02','--arm','cancel_summary','--schedule','accepted_precommit','--seed','17','--receipt-fault','bypass'],
              [python,'-B',str(stage/'verify.py'),'--qa-id','qa-clean-v01','--record',str(stage/'runs/matrix-s17-accepted_precommit-cancel_summary-v02'),'--source-root',str(relocated/'application_probe/upstream')],
              [python,'-B',str(stage/'build_report.py'),'--matrix','v02','--report-id','report-clean-v01','--qa-id','qa-clean-v01','--delivery-counterexample','receipt-fault-v02']]
    results=[]
    for i,cmd in enumerate(commands):
        result=run(cmd,stage,timeout=3600)
        save(dest/f'EXECUTION-{i+1}.json',result);results.append(result)
        print(json.dumps({'step':i+1,'exit_code':result['exit_code'],'tail':result['stdout'][-1100:]}),flush=True)
        if result['exit_code'] != 0: break
    save(dest/'REPRODUCTION.json',{'finished_utc':datetime.now(timezone.utc).isoformat(),
        'steps_completed':len(results),'success':len(results)==len(commands) and all(x['exit_code']==0 for x in results),
        'bundle_unchanged':all(sha(relocated/n)==h for n,h in files.items()),
        'scope':'same host, newly installed venv and relocated copied source; no second operator/OS claim'})
    return 0 if len(results)==len(commands) and all(x['exit_code']==0 for x in results) else 1
if __name__=='__main__': raise SystemExit(main())
