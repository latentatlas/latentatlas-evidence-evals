"""Read-only publication checks against unchanged, re-audited evidence."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE.parents[1] / 'progress' / '2026-10-16'
LABELS = {
    'healthy': 'Healthy reference',
    'source_stop': 'Source stop',
    'memory_revoke': 'In-memory origin revocation',
    'durable_cancel': 'Persistent operation cancellation',
    'durable_revoke': 'Persistent origin revocation',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def table_rows(text, number):
    start = text.index('**Table ' + str(number) + '.')
    block = text[start:].split('\n\n', 2)[1]
    rows = [[cell.strip() for cell in line.strip('|').split('|')]
            for line in block.splitlines()
            if line.startswith('|') and not re.fullmatch(r'[| :\-]+', line)]
    return rows[1:]


def compare_live_table(text, live):
    rows = live['records']
    need(len(rows) == 5 and {row['arm'] for row in rows} == set(LABELS),
         'Live identities differ')
    reference = next(row for row in rows if row['arm'] == 'healthy')['legitimate_final_files']
    expected = []
    for row in rows:
        arm = row['arm']
        need(row['evidence_status'] == 'recorded', 'Unrecorded live evidence')
        states = []
        for role in ('I', 'N'):
            value = row['legitimate_final_files'].get(role)
            need(value and value == reference[role], 'I/N reference mismatch')
            states.append('reference' if arm == 'healthy' else 'match')
        expected.append([LABELS[arm], str(row['old_effects_after_restart']),
                         str(row['continuation_effects_after_restart']),
                         ' / '.join(states).capitalize()])
    need(table_rows(text, 2) == expected, 'Manuscript Table 2 differs from evidence')
    return len(expected)


def compare_fault_table(text, receiver):
    faults = {row['cell'].rsplit('--', 1)[1]: row for row in receiver['records']
              if not row['cell'].endswith('--none')}
    need(set(faults) == {'noop_revoke', 'broad_revoke', 'omit_receipt', 'wrong_payload'},
         'Fault identity set changed')
    for name, row in faults.items():
        need(row['cell'].startswith('claimed_before_effect--'), 'Fault timing changed')
    noop = faults['noop_revoke']; broad = faults['broad_revoke']
    omitted = faults['omit_receipt']; wrong = faults['wrong_payload']
    for row in (noop, broad):
        need('--receiver_revoke--' in row['cell'], 'Revocation arm changed')
    need('--source_stop--' in omitted['cell'] and '--healthy--' in wrong['cell'],
         'Receipt/content arm changed')
    n = noop['outcomes']; b = broad['outcomes']; o = omitted['outcomes']; w = wrong['outcomes']
    need(noop['status'] == broad['status'] == wrong['status'] == 'recorded',
         'Control/task failure incorrectly marked invalid')
    need(n['O_receipts_after_boundary'] == n['C_receipts_after_boundary'] == 1 and
         n['final_payload_matches_reference']['I'] and n['final_payload_matches_reference']['N'],
         'No-op revocation outcome changed')
    need(b['O_receipts_after_boundary'] == b['C_receipts_after_boundary'] == 0 and
         not any(b['final_files_observed'].values()), 'Broad revocation outcome changed')
    need(omitted['status'] == 'needs_review' and not omitted['evidence_valid'] and
         o['final_files_observed']['O'] and o['O_receipts_after_boundary'] is None and
         'observed_file_without_receipt:O-final.json' in omitted['evidence_issues'],
         'Missing receipt incorrectly attributed')
    need(w['final_files_observed']['O'] and w['final_payload_matches_reference']['O'] is False
         and w['final_payload_matches_reference']['I'] and w['final_payload_matches_reference']['N'],
         'Wrong-content outcome changed')
    expected = [
        ['Revocation has no effect', 'O and F each write once; I/N match', 'Recorded control failure'],
        ['Revocation covers unrelated origins', 'No O/F effects; I/N files also absent', 'Recorded collateral damage'],
        ["O's native write receipt omitted", "O's file exists; its receipt is missing", 'needs_review; no attributed effect count'],
        ['Incorrect O report content', "O's file exists but differs from its reference; I/N match", 'Recorded task-quality failure'],
    ]
    need(table_rows(text, 3) == expected, 'Manuscript Table 3 differs from checked fault records')
    return len(expected)


def check_artifacts(root, checks):
    for name, digest in checks['artifact_hashes'].items():
        path = Path(name)
        need(not path.is_absolute() and '..' not in path.parts, 'Unsafe artifact path')
        file = root / path
        need(file.is_file() and not file.is_symlink(), 'Missing revision artifact: ' + name)
        need(hashlib.sha256(file.read_bytes()).hexdigest() == digest, 'Revision digest mismatch: ' + name)
    return len(checks['artifact_hashes'])


def main():
    need(not sys.flags.optimize, 'Do not use -O')
    checks = json.loads((HERE / 'REVISION_CHECKS.json').read_text())
    count = check_artifacts(HERE, checks)
    result = subprocess.run([sys.executable, '-B', 'verify_snapshot.py'], cwd=SNAPSHOT,
                            capture_output=True, text=True, timeout=180)
    need(result.returncode == 0, 'Frozen snapshot audit failed:\n' + result.stdout + result.stderr)
    evidence = json.loads(result.stdout)
    text = (HERE / 'MANUSCRIPT.md').read_text()
    live = json.loads((SNAPSHOT / 'live-persistence' / 'RESULTS.json').read_text())
    receiver = json.loads((SNAPSHOT / 'receiver-reproducer' / 'example-evidence' / 'RESULTS.json').read_text())
    live_rows = compare_live_table(text, live)
    fault_rows = compare_fault_table(text, receiver)
    need('The archived role label remains C; F avoids confusion' in text, 'Role mapping missing')
    need('before receiver control' in text and 'adds no experimental observations' in text,
         'Revision or summary chronology qualifier missing')
    report = dict(status='passed', revision='1.3', revision_files_verified=count,
                  table_2_rows_checked=live_rows, table_3_rows_checked=fault_rows,
                  frozen_snapshot=evidence, new_provider_calls=0, new_experiments=0,
                  independent_human_validation=False)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
