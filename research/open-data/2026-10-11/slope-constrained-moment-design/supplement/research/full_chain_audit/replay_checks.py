#!/usr/bin/env python3
"""Audit existing R01--R12 in disposable copies, preserving frozen sources.

No scientific extensions. Each job starts from exactly the recorded bytes;
changed outputs and complete logs are retained here, temporary clones removed.
"""
import sys
sys.dont_write_bytecode = True
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PACKAGES = ['cusp_verified','cusp_region','cusp_connection','cusp_geometry',
 'cusp_width','cusp_literature','cusp_robustness','cusp_pinned_family',
 'cusp_shape_design','swallowtail_window','kernel_design_principle',
 'kernel_norm_threshold']
PYTHON = ROOT / '.venv-math/bin/python'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def jobs(generators=False):
    out = []
    def add(pkg, script, *args):
        out.append(dict(id=f'{PACKAGES.index(pkg)+1:02}_{script.removesuffix(".py")}'
                        + ('_'+'_'.join(args).replace('--','') if args else ''),
                        package=pkg, script=script, args=list(args)))
    if generators:
        add('cusp_verified','certify_cusp.py','--family','quartic')
        add('cusp_verified','certify_cusp.py','--family','sextic')
        add('cusp_verified','local_roots.py')
        for pkg, scripts in {
            'cusp_region':['certify_region.py'],
            'cusp_connection':['certify_connection.py'],
            'cusp_geometry':['certify_geometry.py'],
            'cusp_width':['certify_width.py','endpoint_folds.py'],
            'cusp_robustness':['certify_robustness.py','condition_witness.py','pinned_cusp.py'],
            'cusp_pinned_family':['build_moment_cache.py','certify_family.py','certify_points.py','certify_fold_samples.py'],
            'cusp_shape_design':['moment_dictionary.py','certify_design.py','build_local_jets.py','certify_boundaries.py','certify_local_v2.py','certify_samples.py'],
            'swallowtail_window':['build_model_v2.py','certify_window.py','certify_samples.py','certify_chart.py'],
            'kernel_design_principle':['certify_candidate.py'],
            'kernel_norm_threshold':['certify_threshold.py'],
        }.items():
            for script in scripts: add(pkg,script)
        return out
    for pkg in PACKAGES:
        for p in sorted((ROOT/'research'/pkg).glob('*.py')):
            if p.name.startswith(('check_', 'crosscheck_', 'test_')):
                add(pkg, p.name)
    return out

def run_job(job, baseline, phase):
    saved = HERE/phase/job['id']
    saved.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='cusp-chain-audit-') as temp:
        clone = Path(temp)/'research'
        for pkg in PACKAGES:
            shutil.copytree(ROOT/'research'/pkg, clone/pkg,
                            ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        script=clone/job['package']/job['script']
        args=job['args'].copy()
        if job['script']=='build_moment_cache.py':
            for p in (script.parent/'cache').glob('*.json'): p.unlink()
            args+=['--workers','1']
        if job['script']=='certify_region.py':
            (script.parent/'results/center_derivatives.json').unlink()
        if "add_argument('--output'" in script.read_text() or 'add_argument("--output"' in script.read_text():
            args += ['--output', str(saved/'result.json')]
        command=[str(PYTHON),str(script)]+args
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        with (saved/'stdout.log').open('w') as log:
            process=subprocess.run(command,cwd=script.parent,env=env,stdout=log,
                                   stderr=subprocess.STDOUT,check=False)
        changes=[]
        for pkg in PACKAGES:
            for p in sorted((clone/pkg).rglob('*')):
                if not p.is_file() or '__pycache__' in p.parts: continue
                rel=str(p.relative_to(clone))
                digest=sha(p)
                if baseline.get(rel)!=digest:
                    target=saved/'generated'/rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p,target)
                    changes.append(dict(path=rel,sha256=digest,
                                        previous_sha256=baseline.get(rel)))
        record=dict(**job, exit_code=process.returncode,
                    elapsed_seconds=time.monotonic()-start,
                    source_sha256=sha(ROOT/'research'/job['package']/job['script']),
                    command_template=[str(PYTHON),f'<fresh-clone>/research/{job["package"]}/{job["script"]}']+args,
                    changed_clone_files=changes,
                    completed_utc=datetime.now(timezone.utc).isoformat())
        (saved/'run.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ('id','exit_code','elapsed_seconds')}),flush=True)
    return record

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--workers',type=int,default=3)
    ap.add_argument('--phase',default='replays')
    ap.add_argument('--only',nargs='*')
    ap.add_argument('--generators',action='store_true')
    args=ap.parse_args()
    manifest={str(p.relative_to(ROOT/'research')):sha(p)
              for pkg in PACKAGES for p in (ROOT/'research'/pkg).rglob('*')
              if p.is_file() and '__pycache__' not in p.parts}
    chosen=jobs(args.generators)
    if args.only: chosen=[j for j in chosen if j['id'] in args.only]
    (HERE/args.phase).mkdir(parents=True,exist_ok=True)
    (HERE/args.phase/'inputs.json').write_text(json.dumps(manifest,indent=2)+'\n')
    records=[]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(run_job,j,manifest,args.phase) for j in chosen]
        for f in as_completed(futures):
            records.append(f.result())
            (HERE/args.phase/'summary.json').write_text(json.dumps(records,indent=2)+'\n')
    changed=[p for p,h in manifest.items() if sha(ROOT/'research'/p)!=h]
    assert not changed, changed
    report=dict(status='passed' if all(r['exit_code']==0 for r in records) else 'failures_need_review',
                jobs=len(records),passed=sum(r['exit_code']==0 for r in records),
                failed=[r['id'] for r in records if r['exit_code']!=0],
                original_frozen_files_unchanged=len(manifest),
                completed_utc=datetime.now(timezone.utc).isoformat())
    (HERE/args.phase/'status.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__': main()
