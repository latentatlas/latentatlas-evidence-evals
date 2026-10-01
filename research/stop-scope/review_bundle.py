"""Verify this export, optionally re-audit the full retained evidence offline.

No SDK, experiment, package installer, network client, or model is used.
Exit zero means consistent evidence, not that every stop obligation passed.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_file(root, name):
    """Reject traversal, non-canonical paths and symlinked path components."""
    relative = PurePosixPath(name)
    require(isinstance(name, str) and name and not relative.is_absolute()
            and '..' not in relative.parts and relative.as_posix() == name,
            'Unsafe relative file: ' + repr(name))
    current = root
    for part in relative.parts:
        current = current / part
        require(not current.is_symlink(), 'Symlinked evidence path: ' + name)
    require(current.is_file() and current.resolve().is_relative_to(root.resolve()),
            'Missing or out-of-root file: ' + name)
    return current


def verify_files(root, expected, exact=False):
    require(isinstance(expected, dict) and expected, 'Empty or invalid file manifest')
    for name, digest in expected.items():
        require(sha(safe_file(root, name)) == digest, 'Hash mismatch: ' + name)
    if exact:
        actual = {p.relative_to(root).as_posix() for p in root.rglob('*')
                  if p.is_file() and '__pycache__' not in p.parts
                  and p.relative_to(root).as_posix() != 'SHA256SUMS.json'}
        require(actual == set(expected), 'Missing or unexpected package file')


def check_export(root):
    index = json.loads(safe_file(root, 'provenance/EXPORT_INDEX.json').read_text())
    entries = index['files']
    names = [entry['path'] for entry in entries]
    require(len(names) == len(set(names)), 'Duplicate export path')
    verify_files(root, {entry['path']: entry['sha256'] for entry in entries})
    plan = json.loads((root / 'provenance/MATRIX_PLAN.json').read_text())
    provenance = json.loads((root / 'results/canonical/ORIGINAL_PROVENANCE.json').read_text())
    require(sha(root / 'provenance/MATRIX_PLAN.json') == provenance['plan_sha256'],
            'Plan does not match original report provenance')
    for name, expected in plan['source_sha256'].items():
        require(sha(safe_file(root, 'harness/stop_contract_study/' + name)) == expected,
                'Frozen source changed: ' + name)
    require(sha(root / 'harness/stop_contract_study/PROTOCOL.md') == plan['protocol_sha256'],
            'Frozen protocol changed')
    original_sums = json.loads((root / 'provenance/SUPPLEMENT_SHA256SUMS.json').read_text())
    for entry in entries:
        if entry['source_kind'] == 'supplement-v1' and entry['source_path'] != 'SHA256SUMS.json':
            require(original_sums.get(entry['source_path']) == entry['sha256'],
                    'Export does not match released supplement: ' + entry['path'])
    return {'export_hashes_valid': True, 'exported_files_verified': len(entries),
            'frozen_harness_source_files_verified': len(plan['source_sha256']),
            'upstream_revision': index['upstream_revision'],
            'raw_evidence_reaudited': False, 'new_experiments_run': 0,
            'independent_human_validation': False}


def check_summary(summary, rows):
    """Recompute stored counts and every grouped verdict from fresh audits."""
    require(summary.get('all_evidence_valid') is True, 'Summary not marked evidence-valid')
    totals = Counter()
    by_group = defaultdict(list)
    for cell, audit in rows:
        require(audit.get('evidence_valid') is True, 'Invalid record cannot enter a summary')
        totals.update(audit['counts'])
        by_group[(cell['schedule'], cell['arm'])].append(audit)
    require(dict(totals) == summary['totals'], 'Recomputed summary totals differ')
    group_keys = [(group['schedule'], group['arm']) for group in summary['groups']]
    require(len(group_keys) == len(set(group_keys)) and set(group_keys) == set(by_group),
            'Missing or duplicate summary group')
    for group in summary['groups']:
        audits = by_group[(group['schedule'], group['arm'])]
        require(group['cells'] == len(audits), 'Summary group size differs')
        for outcome, expected in group['outcomes'].items():
            observed = dict(Counter(audit['outcomes'][outcome]['status'] for audit in audits))
            require(observed == expected, 'Grouped outcome differs: ' + outcome)
    return dict(totals)


def audit_bundle(root, bundle):
    sums_file = root / 'provenance/SUPPLEMENT_SHA256SUMS.json'
    require(sha(safe_file(bundle, 'SHA256SUMS.json')) == sha(sums_file),
            'Bundle is not the released evidence version')
    sums = json.loads(sums_file.read_text())
    verify_files(bundle, sums, exact=True)
    require(sha(bundle / 'EXPORT_MANIFEST.json') == sha(root / 'provenance/SUPPLEMENT_EXPORT_MANIFEST.json'),
            'Unexpected export manifest')
    module_path = root / 'harness/stop_contract_study/audit_study.py'
    require(sha(module_path) == sums['audit_study.py'], 'Auditor differs from released auditor')
    spec = importlib.util.spec_from_file_location('retained_stop_scope_audit', module_path)
    require(spec is not None and spec.loader is not None, 'Auditor cannot be loaded')
    auditor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auditor)
    manifest = json.loads((bundle / 'EXPORT_MANIFEST.json').read_text())
    plan = json.loads((root / 'provenance/MATRIX_PLAN.json').read_text())
    cells = {cell['run_id']: cell for cell in plan['cells']}
    require(len(cells) == 26, 'Expected 26 distinct matrix conditions')
    grouped = defaultdict(list)
    diagnostics = []
    seen = set()
    for record in manifest['runs']:
        key = (record['environment'], record['run_id'])
        require(key not in seen, 'Repeated evidence identity')
        seen.add(key)
        run_dir = safe_file(bundle, record['path'] + '/manifest.json').parent
        audit = auditor.audit_run(run_dir, bundle / 'upstream')
        require(audit.get('evidence_valid') is True,
                'Invalid evidence for ' + record['path'] + ': ' + repr(audit.get('evidence_errors')))
        require(audit['counts'] == record['expected_counts'], 'Record counts differ: ' + record['path'])
        outcomes = {name: value['status'] for name, value in audit['outcomes'].items()}
        require(outcomes == record['expected_outcomes'], 'Record outcomes differ: ' + record['path'])
        if record['matrix_condition']:
            require(record['run_id'] in cells, 'Unplanned matrix identity')
            grouped[record['environment']].append((cells[record['run_id']], audit))
        else:
            diagnostics.append({'environment': record['environment'], 'run_id': record['run_id'],
                                'evidence_valid': True, 'outcomes': outcomes})
    require(set(grouped) == {'canonical', 'repeat'}, 'Expected original and same-host repeat')
    totals, contracts = {}, {}
    for environment, rows in grouped.items():
        require({cell['run_id'] for cell, _ in rows} == set(cells) and len(rows) == 26,
                'Missing matrix condition: ' + environment)
        summary = json.loads((root / 'results' / environment / 'SUMMARY.json').read_text())
        require(sha(root / 'results' / environment / 'SUMMARY.json') == sha(bundle / environment / 'SUMMARY.json'),
                'Browsable summary differs from retained summary')
        totals[environment] = check_summary(summary, rows)
        contracts[environment] = {
            name: dict(Counter(audit['outcomes'][name]['status'] for _, audit in rows))
            for name in ['R_request_no_old_final_effect', 'V_withdrawal_no_old_native_start',
                         'C_quiescent_confirmation']}
    require(len(diagnostics) == 2, 'Expected two separate receipt-fault diagnostics')
    return {'raw_evidence_reaudited': True, 'package_files_verified': len(sums),
            'matrix_evidence_valid': 52, 'separate_diagnostics_valid': len(diagnostics),
            'recomputed_counts': totals, 'recomputed_stop_outcomes': contracts,
            'summary_checks': 'All aggregate counts and grouped verdicts; no new experiments.',
            'success_meaning': 'Evidence consistency, not universal success of stop controls.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, help='Extracted stop-scope-supplement-v1 directory')
    parser.add_argument('--output', type=Path, help='New audit JSON; refuses to overwrite')
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error('--output already exists; choose a new audit filename')
    report = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'success': False,
              'new_experiments_run': 0, 'independent_human_validation': False}
    try:
        report.update(check_export(ROOT))
        if args.bundle:
            require(args.bundle.is_dir() and not args.bundle.is_symlink(), 'Invalid bundle directory')
            report.update(audit_bundle(ROOT, args.bundle.resolve()))
        report['success'] = True
    except (OSError, ValueError, KeyError, TypeError, ImportError) as error:
        report['error'] = f'{type(error).__name__}: {error}'
    encoded = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as output:
            output.write(encoded)
    print(encoded, end='')
    return 0 if report['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
