#!/usr/bin/env python3
"""R17: immutable-input audit and fresh R15 -> R16 computation replay.

Run without -O, using the recorded math environment. All producers and
dependent checks run in a disposable research tree, not on frozen originals.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read(p):
    return json.loads(Path(p).read_text())

def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

def frozen_state():
    manifests = sorted(p for p in RESEARCH.glob('*/manifest.json') if p.parent != HERE)
    rows = {}
    for p in manifests:
        content = read(p)
        for row in content['files']:
            assert sha(p.parent / row['path']) == row['sha256'], (p, row['path'])
        rows[str(p.relative_to(RESEARCH))] = dict(sha256=sha(p), files=len(content['files']))
    return rows

def endpoints(v):
    m, e = v['mid_man_exp']
    r, f = v['rad_man_exp']
    c, d = Fraction(m) * Fraction(2)**e, Fraction(r) * Fraction(2)**f
    return c-d, c+d

METADATA = {'input_sha256', 'certificate_sha256', 'elapsed_seconds'}

def compare(a, b, path, out):
    if isinstance(a, dict):
        assert isinstance(b, dict) and set(a) == set(b), path
        if 'mid_man_exp' in a and 'rad_man_exp' in a:
            out['dyadic_balls'] += 1
            assert endpoints(a) == endpoints(b), ('Changed mathematical enclosure', path)
            return
        for key in a:
            if key in METADATA:
                if a[key] != b[key]:
                    out['changed_metadata_paths'].append(path + '/' + key)
            else:
                compare(a[key], b[key], path + '/' + key, out)
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), path
        for i, (x, y) in enumerate(zip(a, b)):
            compare(x, y, path + '/' + str(i), out)
    else:
        assert a == b, ('Changed nonmetadata value', path, a, b)
        out['equal_other_values'] += 1

JOBS = [
    ('R15_producer', 'kernel_slope_asymptotics', 'certify_asymptotics.py', 'asymptotic_certificate.json'),
    ('R15_rational', 'kernel_slope_asymptotics', 'check_asymptotics.py', 'asymptotic_check.json'),
    ('R15_algebra', 'kernel_slope_asymptotics', 'check_algebra.py', 'algebra_check.json'),
    ('R15_numerical', 'kernel_slope_asymptotics', 'crosscheck_coefficient.py', 'coefficient_crosscheck.json'),
    ('R16_producer', 'kernel_slope_remainder', 'certify_remainder.py', 'remainder_certificate.json'),
    ('R16_rational', 'kernel_slope_remainder', 'check_remainder.py', 'remainder_check.json'),
    ('R16_algebra', 'kernel_slope_remainder', 'check_algebra.py', 'algebra_check.json'),
    ('R16_derivatives', 'kernel_slope_remainder', 'crosscheck_derivatives.py', 'derivative_crosscheck.json'),
    ('R16_design', 'kernel_slope_remainder', 'crosscheck_design.py', 'design_crosscheck.json'),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    assert not sys.flags.optimize, 'Do not disable assertions.'
    outdir = args.output_dir.absolute()
    assert not outdir.exists(), 'Refuse overwrite.'
    baseline = frozen_state()
    outdir.mkdir(parents=True)
    import flint, mpmath
    write(outdir/'inputs.json', dict(started_utc=datetime.now(timezone.utc).isoformat(),
        prior_manifests=baseline, source_sha256=sha(__file__), python=sys.version,
        executable=str(Path(sys.executable).absolute()), platform=platform.platform(),
        python_flint=flint.__version__, mpmath=mpmath.__version__))
    records = []
    comparisons = []
    # Original audit scripts are read-only; their manifests refer to original bytes.
    for package in ['kernel_slope_asymptotics', 'kernel_slope_remainder']:
        t = time.monotonic()
        script = RESEARCH/package/'audit_snapshot.py'
        result = subprocess.run([sys.executable, '-B', str(script)], capture_output=True, text=True)
        logfile = outdir/(package+'_frozen_audit.log')
        logfile.write_text(result.stdout + result.stderr)
        record = dict(id=package+'_frozen_audit', exit_code=result.returncode,
            elapsed_seconds=time.monotonic()-t, source_sha256=sha(script), log=logfile.name)
        records.append(record)
        write(outdir/'runs.json', records)
        assert result.returncode == 0, record
        print(record['id'], 'passed', flush=True)
    with tempfile.TemporaryDirectory(prefix='r17-slope-replay-') as temporary:
        temp = Path(temporary)
        copy = temp/'research'
        shutil.copytree(RESEARCH, copy,
            ignore=shutil.ignore_patterns(HERE.name, '__pycache__', '*.pyc', 'full_chain_audit'))
        for job, package, scriptname, filename in JOBS:
            t = time.monotonic()
            script = copy/package/scriptname
            assert sha(script) == sha(RESEARCH/package/scriptname)
            target = outdir/(job+'.json')
            result = subprocess.run([sys.executable, '-B', str(script), '--output', str(target)],
                cwd=temp, capture_output=True, text=True)
            logfile = outdir/(job+'.log')
            logfile.write_text(result.stdout + result.stderr)
            record = dict(id=job, package=package, script=scriptname,
                source_sha256=sha(script), exit_code=result.returncode,
                elapsed_seconds=time.monotonic()-t, output=target.name, log=logfile.name)
            if target.exists():
                record['output_sha256'] = sha(target)
            records.append(record)
            write(outdir/'runs.json', records)
            assert result.returncode == 0, record
            original = RESEARCH/package/'results'/filename
            row = dict(job=job, original=str(original.relative_to(RESEARCH)),
                original_sha256=sha(original), replay_sha256=sha(target),
                dyadic_balls=0, equal_other_values=0, changed_metadata_paths=[])
            compare(read(original), read(target), '', row)
            comparisons.append(row)
            # Downstream jobs read this regenerated result, with its actual hash.
            shutil.copyfile(target, copy/package/'results'/filename)
            write(outdir/'comparisons.json', comparisons)
            print(job, 'passed; exact ball matches:', row['dyadic_balls'], flush=True)
    assert frozen_state() == baseline, 'Frozen source changed during replay.'
    report = dict(status='R15_R16_fresh_chain_replay_passed', jobs=len(records),
        fresh_results=len(comparisons), dyadic_balls=sum(r['dyadic_balls'] for r in comparisons),
        equal_other_values=sum(r['equal_other_values'] for r in comparisons),
        changed_metadata_entries=sum(len(r['changed_metadata_paths']) for r in comparisons),
        mathematical_changes=0, prior_manifest_count=len(baseline),
        prior_frozen_file_entries=sum(r['files'] for r in baseline.values()),
        original_files_unchanged=True, temporary_tree_removed=not temp.exists(),
        source_sha256=sha(__file__), completed_utc=datetime.now(timezone.utc).isoformat(),
        trust_boundary='Reproducibility plus separate arithmetic and numerical checks; '
        'not an independent implementation of every enclosure or formal verification of the proofs.')
    write(outdir/'report.json', report)
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
