#!/usr/bin/env python3
"""Replay selected independent audit entry points without modifying frozen files."""
import sys
sys.dont_write_bytecode = True
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def integrity():
    packages = []
    for path in sorted((ROOT / 'research').glob('*/manifest.json')):
        data = json.loads(path.read_text())
        for row in data['files']:
            child = path.parent / row['path']
            if digest(child) != row['sha256']:
                raise RuntimeError(f'Frozen input changed: {child}')
        packages.append({'path': str(path.relative_to(ROOT)),
                         'sha256': digest(path), 'file_entries': len(data['files'])})
    return packages

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if out.exists():
        raise SystemExit('Choose a new audit output directory.')
    out.mkdir(parents=True)
    initial = integrity()
    (out / 'input_integrity.json').write_text(json.dumps(initial, indent=2)+'\n')
    jobs = [
        ('finite_optimum', ['research/finite_slope_optimum/audit_snapshot.py']),
        ('finite_fourth_order', ['research/finite_slope_fourth_order/audit_snapshot.py']),
        ('infinite_fourth_order', ['research/infinite_slope_fourth_order/audit_snapshot.py', '--with-arb']),
        ('theta_transport_dependency_chain', ['research/cusp_order_transport/audit_snapshot.py', '--with-arb']),
    ]
    def execute(job):
        name, argv = job
        cmd = [sys.executable, '-B'] + argv
        started = datetime.now(timezone.utc).isoformat()
        start = time.monotonic()
        with (out / (name + '.log')).open('w') as stream:
            process = subprocess.run(cmd, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
        record = {'name': name, 'command': cmd, 'started_utc': started,
                  'elapsed_seconds': time.monotonic()-start, 'exit_code': process.returncode,
                  'log_sha256': digest(out/(name+'.log'))}
        (out/(name+'.json')).write_text(json.dumps(record, indent=2)+'\n')
        print(json.dumps(record), flush=True)
        return record
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(execute, jobs))
    final = integrity()
    if final != initial:
        raise RuntimeError('Frozen manifest identities changed during audit.')
    report = {'created_utc': datetime.now(timezone.utc).isoformat(),
              'runs': results, 'frozen_packages': len(final),
              'frozen_file_entries': sum(p['file_entries'] for p in final),
              'frozen_inputs_unchanged': True,
              'all_selected_commands_passed': all(r['exit_code']==0 for r in results),
              'analytic_text_formally_verified': False,
              'external_expert_review_performed': False}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report), flush=True)
    if not report['all_selected_commands_passed']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
