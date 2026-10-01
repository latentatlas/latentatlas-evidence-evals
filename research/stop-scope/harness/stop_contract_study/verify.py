"""Recorded unit/negative-control QA, distinct from a fresh experiment matrix."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser();p.add_argument('--qa-id',required=True)
    p.add_argument('--record',type=Path);p.add_argument('--source-root',type=Path);a=p.parse_args()
    if bool(a.record)!=bool(a.source_root):raise ValueError('Record and source root must be supplied together')
    if not re.fullmatch(r'qa-[a-z0-9_-]{2,80}',a.qa_id):raise ValueError('Fresh QA ID required')
    out=ROOT/'qa'/f'{a.qa_id}.json';out.parent.mkdir(exist_ok=True)
    if out.exists():raise FileExistsError(out)
    def hashes():return {f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(ROOT.glob('*.py'))}
    before=hashes();cmd=[sys.executable,'-I',str(ROOT/'qa_entry.py')]
    record_hashes={}
    if a.record:
        a.record=a.record.resolve();a.source_root=a.source_root.resolve()
        if not (a.record/'manifest.json').is_file():raise ValueError('Actual immutable run record required')
        record_hashes={str(f.relative_to(a.record)):hashlib.sha256(f.read_bytes()).hexdigest() for f in a.record.rglob('*') if f.is_file()}
        cmd.extend(['--record',str(a.record),'--source-root',str(a.source_root)])
    env={'PATH':str(Path(sys.executable).parent)+':/usr/bin:/bin','LANGSMITH_TRACING':'false',
         'LANGCHAIN_TRACING_V2':'false','PYTHONDONTWRITEBYTECODE':'1'}
    try:
        q=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=150)
        result={'exit_code':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'timeout':False}
    except subprocess.TimeoutExpired as e:
        result={'exit_code':None,'stdout':(e.stdout or b'').decode(errors='replace'),
                'stderr':(e.stderr or b'').decode(errors='replace'),'timeout':True}
    result.update({'command':cmd,'completed_utc':datetime.now(timezone.utc).isoformat(),
                   'source_sha256':before,'source_unchanged':before==hashes(),
                   'artifact_record':str(a.record) if a.record else None,'artifact_source_root':str(a.source_root) if a.source_root else None,
                   'record_sha256':record_hashes,
                   'record_unchanged':not a.record or record_hashes=={str(f.relative_to(a.record)):hashlib.sha256(f.read_bytes()).hexdigest() for f in a.record.rglob('*') if f.is_file()}})
    with out.open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps({'qa_id':a.qa_id,'exit_code':result['exit_code'],'source_unchanged':result['source_unchanged'],
                      'test_tail':result['stderr'][-5000:]}))
    return 0 if result['exit_code']==0 and result['source_unchanged'] and result['record_unchanged'] else 1
if __name__=='__main__':raise SystemExit(main())
