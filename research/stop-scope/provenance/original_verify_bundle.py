"""Read-only verification of retained evidence. No models, network, or experiment execution."""
from pathlib import Path
import hashlib
import json
import sys
import audit_study

ROOT = Path(__file__).resolve().parent
def main():
    sums = json.loads((ROOT / 'SHA256SUMS.json').read_text())
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != 'SHA256SUMS.json'}
    assert actual == set(sums), 'Missing or unexpected package file'
    for name, expected in sums.items():
        p = ROOT / name
        assert not p.is_symlink() and p.resolve().is_relative_to(ROOT), 'Unsafe package path'
        assert hashlib.sha256(p.read_bytes()).hexdigest() == expected, 'Hash mismatch: ' + name
    manifest = json.loads((ROOT / 'EXPORT_MANIFEST.json').read_text())
    matrix, diagnostics = 0, 0
    for run in manifest['runs']:
        report = audit_study.audit_run(ROOT / run['path'], ROOT / 'upstream')
        assert report['evidence_valid'], (run['path'], report['evidence_errors'])
        outcomes = {key: value['status'] for key, value in report['outcomes'].items()}
        assert outcomes == run['expected_outcomes'], 'Outcome mismatch: ' + run['path']
        assert report['counts'] == run['expected_counts'], 'Count mismatch: ' + run['path']
        if run['matrix_condition']: matrix += 1
        else: diagnostics += 1
    assert matrix == 52
    print(json.dumps({'package_hashes_valid': True, 'matrix_evidence_valid': matrix,
                      'separate_diagnostics_valid': diagnostics, 'upstream_files_hashed': 427,
                      'new_experiments_run': 0, 'independent_human_validation': False}, indent=2))
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
