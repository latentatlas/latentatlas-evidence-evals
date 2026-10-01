"""Freeze and execute the entire plan; invalid cells remain in the record."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
ARMS=['cancel_summary','drain_summary','scoped_summary','scoped_no_summary']
def plan(version):
    cells=[{'run_id':f'matrix-s{s}-{t}-{a}-{version}','seed':s,'schedule':t,'arm':a}
           for s in [17,41] for t in ['accepted_precommit','after_commit','unheld']
           for a in (ARMS if s==17 else ARMS[::-1])]
    return cells+[{'run_id':f'matrix-s{s}-drain_timeout-drain_summary-{version}',
                   'seed':s,'schedule':'drain_timeout','arm':'drain_summary'} for s in [17,41]]
def main():
    p=argparse.ArgumentParser(); p.add_argument('--version',required=True); a=p.parse_args()
    if not re.fullmatch(r'v\d{2}',a.version): raise ValueError('Fresh vNN required')
    cells=plan(a.version); dest=ROOT/'matrices'/a.version
    if any((ROOT/'runs'/c['run_id']).exists() for c in cells): raise FileExistsError('Run already exists')
    dest.mkdir(parents=True,exist_ok=False)
    source_hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in ROOT.glob('*.py')}
    with (dest/'PLAN.json').open('x') as f:
        json.dump({'created_utc':datetime.now(timezone.utc).isoformat(),'cells':cells,'source_sha256':source_hashes,
                   'protocol_sha256':hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest()},f,indent=2)
    failures=0
    with (dest/'EXECUTIONS.jsonl').open('x') as journal:
        for c in cells:
            cmd=[sys.executable,'-B',str(ROOT/'run_probe.py'),'--run-id',c['run_id'],'--seed',str(c['seed']),
                 '--arm',c['arm'],'--schedule',c['schedule']]
            try:
                proc=subprocess.run(cmd,capture_output=True,text=True,timeout=195)
                result={**c,'command':cmd,'exit_code':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'timeout':False}
            except subprocess.TimeoutExpired as e:
                result={**c,'command':cmd,'exit_code':None,'stdout':(e.stdout or b'').decode(errors='replace'),
                        'stderr':(e.stderr or b'').decode(errors='replace'),'timeout':True}
            result['finished_utc']=datetime.now(timezone.utc).isoformat()
            journal.write(json.dumps(result)+'\n');journal.flush()
            failures+=result['exit_code']!=0
            print(json.dumps({**c,'exit_code':result['exit_code']}),flush=True)
            if any(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h for n,h in source_hashes.items()):
                raise RuntimeError('Source changed during frozen matrix; retain all records and stop')
    return 1 if failures else 0
if __name__=='__main__': raise SystemExit(main())
