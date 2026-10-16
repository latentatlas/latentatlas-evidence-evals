"""Read-only verification of this package and recorded receiver experiments."""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def need(condition, message):
    if not condition:
        raise ValueError(message)


def safe_path(root, name):
    root = Path(root).resolve()
    part = Path(name)
    need(not part.is_absolute() and '..' not in part.parts, 'Unsafe manifest entry')
    path = root / part
    need(path.resolve().is_relative_to(root), 'Manifest escapes its root')
    need(not any(p.is_symlink() for p in [path, *path.parents] if p != root and p.is_relative_to(root)),
         'Symlink in manifest path')
    return path


def verify_hashes(root, hashes):
    for name, expected in hashes.items():
        path = safe_path(root, name)
        need(path.is_file() and sha(path) == expected, 'File hash mismatch: ' + name)
    return len(hashes)


def package_check(root=HERE):
    root = Path(root).resolve()
    seal = root / 'RELEASE_MANIFEST.json'
    need(seal.is_file(), 'Release manifest missing')
    hashes = load(seal)['artifact_hashes']
    count = verify_hashes(root, hashes)
    actual = set()
    for p in root.rglob('*'):
        relative = p.relative_to(root)
        if relative.parts[0].startswith('local-'):
            continue  # New runs are outside the immutable release inventory.
        need(not p.is_symlink(), 'Unexpected package symlink')
        if p.is_file() and p != seal:
            actual.add(relative.as_posix())
    need(actual == set(hashes), 'Release inventory differs from manifest')
    return dict(status='passed', release_files_verified=count)


def completion_check(root):
    root = Path(root).resolve()
    hashes = load(root / 'COMPLETION.json')['artifact_hashes']
    actual = set()
    for p in root.rglob('*'):
        need(not p.is_symlink(), 'Unexpected evidence symlink')
        if p.is_file() and p != root / 'COMPLETION.json':
            actual.add(p.relative_to(root).as_posix())
    need(actual == set(hashes), 'Evidence inventory differs from completion record')
    return verify_hashes(root, hashes)


def compare_expectations(records, expected):
    """A regression difference is not permission to relabel evidence invalid."""
    differences = []
    for row in records:
        reference = expected.get(row['cell'])
        actual = {k: row.get(k) for k in ('status', 'evidence_valid', 'outcomes')}
        if reference != actual:
            differences.append(row['cell'])
    return differences


def verify_run(folder, package_root=HERE):
    from audit import audit
    folder = Path(folder).resolve()
    root = Path(package_root).resolve()
    manifest_count = completion_check(folder)
    plan, result = load(folder / 'PLAN.json'), load(folder / 'RESULTS.json')
    planned = ['--'.join(c) for c in plan['conditions']]
    need(len(planned) == len(set(planned)), 'Duplicate planned cell')
    need([r['cell'] for r in result['records']] == planned, 'Planned denominator changed')
    expected = load(root / 'EXPECTED_MECHANISM_OUTCOMES.json')
    need(set(planned) <= set(expected), 'Unknown condition')
    need(len(planned) in (1, 16), 'Unexpected matrix size')
    if len(planned) == 16:
        need(set(planned) == set(expected), 'Incomplete full matrix')
    else:
        need(planned == ['claimed_before_effect--source_stop--none'], 'Wrong smoke condition')
    need(plan['actual_provider_calls'] == result['actual_provider_calls'] == 0, 'Provider-free scope changed')
    verify_hashes(root, plan['source_hashes'])
    verify_hashes(folder / 'instrument', plan['source_hashes'])
    verify_hashes(root, plan['protected_hashes'])
    need(plan['fixture_source'] == 'fixtures/ROLE_PAYLOADS.json', 'Nonportable fixture source')
    need(sha(root / plan['fixture_source']) == plan['fixture_sha256'], 'Fixture changed')
    payloads = load(root / plan['fixture_source'])
    cases, raw_counts, children = [], [], []
    for saved in result['records']:
        episode = safe_path(folder, saved['cell'])
        manifest_count += completion_check(episode)
        episode_plan = load(episode / 'PLAN.json')
        need(episode_plan['reference_payloads'] == payloads, 'Episode fixture mismatch')
        computed = audit(episode)
        need(computed == load(episode / 'AUDIT.json'), 'Recomputed audit differs: ' + saved['cell'])
        need(computed == {k: v for k, v in saved.items() if k != 'cell'}, 'Summary mismatch')
        process = load(episode / 'PROCESS.json')
        need(process['episode_error'] is None and not process['cleanup_actions'], 'Infrastructure/cleanup failure')
        need(all(process[r]['reaped'] for r in ('source', 'receiver', 'observer')), 'Unreaped process')
        children.extend(process[r]['pid'] for r in ('source', 'receiver', 'observer'))
        # This path counts raw receipts, not the control's success label.
        events = [json.loads(x) for x in (episode / 'receiver.jsonl').read_text().splitlines()]
        jobs = {e['op']['operation_id']: e['op']['role'] for e in events if e['kind'] == 'job_accepted'}
        boundaries = [e for e in events if e['kind'] == 'intervention_boundary']
        need(len(boundaries) == 1, 'Missing causal boundary')
        counts = Counter(jobs[e['operation_id']] for e in events
                         if e['kind'] == 'native_write_receipt' and e['seq'] > boundaries[0]['seq'])
        outcome = computed['outcomes']
        if computed['evidence_valid'] and outcome['source_was_stopped']:
            for role in ('O', 'C'):
                need(outcome[role + '_receipts_after_boundary'] == counts[role], 'Raw effect count mismatch')
        raw_counts.append(dict(cell=saved['cell'], receipt_counts=dict(counts),
                               trusted_attribution=computed['evidence_valid']))
        cases.append(dict(cell=saved['cell'], **computed))
    references = []
    if len(planned) == 16:
        for row in cases:
            cut, arm, fault = row['cell'].split('--')
            if fault != 'none' or arm == 'healthy':
                continue
            for role in ('I', 'N'):
                current = folder / row['cell'] / 'store' / (role + '-final.json')
                healthy = folder / (cut + '--healthy--none') / 'store' / (role + '-final.json')
                need(sha(current) == sha(healthy), 'Legitimate-work/reference mismatch')
                references.append(dict(cell=row['cell'], role=role, sha256=sha(current)))
    differences = compare_expectations(cases, expected)
    return dict(status='passed' if not differences else 'recorded_outcome_differs_needs_review',
        conditions=len(cases), evidence_statuses=dict(Counter(r['status'] for r in cases)),
        artifact_hashes_verified=manifest_count, legitimate_reference_matches=len(references),
        outcome_differences=differences, actual_provider_calls=0, new_catalogue_acceptances=0,
        independent_replication=False, child_pids_recorded=children,
        raw_receipt_crosschecks=raw_counts, legitimate_reference_checks=references)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', action='store_true')
    parser.add_argument('--run', type=Path)
    args = parser.parse_args()
    try:
        report = package_check()
        if args.run:
            report['run'] = verify_run(args.run)
        elif not args.package:
            report['run'] = verify_run(HERE / 'example-evidence')
        print(json.dumps(report, indent=2))
        if report.get('run', {}).get('status', 'passed') != 'passed':
            sys.exit(1)
    except Exception as exc:
        print(json.dumps(dict(status='failed_verification', error_type=type(exc).__name__, error=str(exc))))
        sys.exit(1)
