"""Read-only verification; invokes no model or experiment runner."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def coverage_check(data):
    rows = data['cases']
    need(len(rows) == 286 and len({r['case_id'] for r in rows}) == 286, 'Case identity denominator')
    need(all(len(r['original_case_sha256']) == 64 for r in rows), 'Original case identity hash')
    counts = dict(Counter(r['assessment'] for r in rows))
    need(counts == data['summary']['counts'], 'Coverage counts differ')
    need(counts == {'T': 2, 'D': 27, 'P': 39, 'C': 125, 'N': 78, 'B': 15}, 'Assessment version changed')
    need(not any(r['original_registry_promotion'] or r['author_acceptance_recorded'] for r in rows), 'Undeclared case acceptance')
    direct = counts['T'] + counts['D']
    need(direct == data['summary']['direct']['cases'] == 29, 'Direct evidence denominator')
    need(direct + counts['P'] == data['summary']['direct_or_partial']['cases'] == 68, 'Partial evidence denominator')
    need(data['summary']['formal_catalogue_acceptance']['cases'] == 0, 'Formal acceptance changed')
    for family in data['families']:
        members = [r for r in rows if r['family'] == family['id']]
        need(len(members) == family['total'] and dict(Counter(r['assessment'] for r in members)) == family['counts'], 'Family identity mismatch')
    return dict(cases=286, direct=direct, direct_or_partial=68, formal_acceptance=0,
                verification_scope='Internal mapping consistency, not re-audit of unpublished evidence')


def live_headlines(result):
    expected = {'healthy': (1, 2), 'source_stop': (1, 2), 'memory_revoke': (1, 2),
                'durable_cancel': (0, 2), 'durable_revoke': (0, 0)}
    rows = result['records']
    need(len(rows) == 5 and len({r['arm'] for r in rows}) == 5, 'Live condition denominator')
    actual = {r['arm']: (r['old_effects_after_restart'], r['continuation_effects_after_restart']) for r in rows}
    need(actual == expected, 'Live result differs; inspect evidence, do not discard the condition')
    need(result['requests'] == sum(r['requests'] for r in rows) == 64, 'Live request count')
    need(len(result['reference_comparisons']) == 8 and result['author_approved_summaries'] == 4, 'Secondary result count')
    return dict(conditions=5, historical_requests=64, reference_pairs=8, reviewed_summaries=4)


def package_inventory(root, packages):
    count = 0
    for package in packages:
        folder = root / package['directory']
        expected = package['exported_hashes']
        actual = {}
        for p in folder.rglob('*'):
            rel = p.relative_to(folder)
            if rel.parts[0].startswith('local-'):
                continue
            need(not p.is_symlink(), 'Symlink in package')
            if p.is_file():
                actual[rel.as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
        need(actual == expected, 'Reviewed archive extraction changed: ' + package['directory'])
        need(len(actual) == package['files'], 'Package count mismatch')
        count += len(actual)
    return count


def run_reader(folder):
    result = subprocess.run([sys.executable, '-B', 'verify.py'], cwd=folder,
                            capture_output=True, text=True, timeout=90)
    need(result.returncode == 0, 'Package verification failed: ' + folder.name + '\n' + result.stdout + result.stderr)
    return json.loads(result.stdout)


def publication_check(root):
    checks = json.loads((root / 'PUBLICATION_CHECKS.json').read_text())
    scope = root.parent.parent
    for name, digest in checks['artifact_hashes'].items():
        rel = Path(name)
        need(not rel.is_absolute() and '..' not in rel.parts, 'Unsafe publication path')
        file = scope / rel
        need(file.is_file() and not file.is_symlink(), 'Missing publication file')
        need(hashlib.sha256(file.read_bytes()).hexdigest() == digest, 'Publication digest mismatch: ' + name)
    return dict(files_verified=len(checks['artifact_hashes']), paper_pages=checks['paper']['pages'])


def main():
    need(not sys.flags.optimize, 'Do not use -O')
    provenance = json.loads((HERE / 'PACKAGE_PROVENANCE.json').read_text())
    count = package_inventory(HERE, provenance['packages'])
    coverage = coverage_check(json.loads((HERE / 'COVERAGE_MAP.json').read_text()))
    live = run_reader(HERE / 'live-persistence')
    receiver = run_reader(HERE / 'receiver-reproducer')
    headline = live_headlines(live)
    run = receiver['run']
    need(run['conditions'] == 16 and run['evidence_statuses'] == {'recorded': 15, 'needs_review': 1}, 'Receiver evidence statuses')
    need(run['legitimate_reference_matches'] == 18 and run['outcome_differences'] == [], 'Receiver outcomes')
    publication = publication_check(HERE)
    report = dict(status='passed', package_files_verified=count, live=headline, publication=publication,
        receiver=dict(conditions=16, evidence_statuses=run['evidence_statuses'], legitimate_reference_pairs=18),
        coverage=coverage, new_provider_calls=0, new_experiments=0,
        independent_human_validation=False)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
