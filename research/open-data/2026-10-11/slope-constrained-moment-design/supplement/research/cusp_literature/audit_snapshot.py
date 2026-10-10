#!/usr/bin/env python3
"""Read-only R06 provenance audit; --freeze creates a new manifest once.

This verifies preserved files and reproducibility of an exact algebraic
example. It cannot establish literature priority or validate web claims.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise ArithmeticError(message)


def files():
    return [p for p in sorted(HERE.rglob('*')) if p.is_file()
            and '__pycache__' not in p.parts and p.name != 'manifest.json']


def audit():
    packages = []
    for name in ('cusp_verified', 'cusp_region', 'cusp_connection',
                 'cusp_geometry', 'cusp_width'):
        base = HERE.parent / name
        m = json.loads((base/'manifest.json').read_text())
        for row in m['files']:
            require(sha(base/row['path']) == row['sha256'],
                    f'Changed frozen file: {name}/{row["path"]}')
        packages.append({'package': name, 'files': len(m['files']),
                         'manifest_sha256': sha(base/'manifest.json')})
    originals = json.loads((HERE.parent/'cusp_verified/manifest.json').read_text())['original_files']
    for row in originals:
        require(sha(Path(row['path'])) == row['sha256'],
                f'Changed original file: {row["path"]}')
    old_audit = subprocess.run([sys.executable, str(HERE.parent/'cusp_width/audit_snapshot.py')],
                               capture_output=True, text=True, check=True)
    require('all_snapshot_links_and_preservation_checks_passed' in old_audit.stdout,
            'R05 provenance audit did not pass')
    fresh = json.loads(subprocess.run([sys.executable, str(HERE/'check_structural_example.py')],
                                     capture_output=True, text=True, check=True).stdout)
    require(fresh == json.loads((HERE/'structural_example.json').read_text()),
            'Exact algebra report is stale')
    sources = json.loads((HERE/'sources.json').read_text())['sources']
    require(len(sources) == len({s['id'] for s in sources}) == 9, 'Source identity mismatch')
    bib = (HERE/'references.bib').read_text()
    bibkeys = set(re.findall(r'@\w+\{([^,]+),', bib))
    require(bibkeys == {s['bibkey'] for s in sources}, 'Bibliography/source catalog mismatch')
    fragment = (HERE/'RELATED_WORK_DRAFT.tex').read_text()
    cites = set()
    for group in re.findall(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}', fragment):
        cites.update(k.strip() for k in group.split(','))
    require(cites <= bibkeys, 'Unresolved TeX citation')
    for name in ('RELATED_WORK_DRAFT.tex', 'references.bib'):
        depth = 0
        for char in (HERE/name).read_text():
            depth += (char == '{') - (char == '}')
            require(depth >= 0, f'Unmatched closing brace in {name}')
        require(depth == 0, f'Unmatched opening brace in {name}')
    local_links = 0
    for path in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^\n]+?)\)', path.read_text()):
            if target.startswith(('https://', 'http://', '#')):
                continue
            target = target.split('#', 1)[0]
            require((path.parent/target).exists(), f'Broken local link: {path.name}: {target}')
            local_links += 1
    return {'status': 'r06_provenance_and_exact_algebra_passed',
            'preserved_packages': packages,
            'preserved_scientific_files': sum(p['files'] for p in packages),
            'preserved_original_files': len(originals),
            'r05_dependency_audit': 'passed', 'exact_polynomial_examples': 2,
            'source_records': len(sources), 'resolved_tex_citations': len(cites),
            'local_markdown_links_checked': local_links,
            'latex_compiled': False,
            'external_mathematical_review': False,
            'exhaustive_literature_priority_proved': False,
            'audit_source_sha256': sha(Path(__file__))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    manifest = HERE/'manifest.json'
    if args.freeze:
        require(not manifest.exists(), 'R06 snapshot already exists; do not overwrite it')
    report = audit()
    if args.freeze:
        (HERE/'audit_report.json').write_text(json.dumps(report, indent=2)+'\n')
        data = {'created_utc': datetime.now(timezone.utc).isoformat(),
                'scope': 'R06 literature positioning and exact structural comparison; no new integral certificate.',
                'audit': report,
                'files': [{'path': str(p.relative_to(HERE)), 'sha256': sha(p)} for p in files()]}
        with manifest.open('x') as f:
            f.write(json.dumps(data, indent=2)+'\n')
    else:
        data = json.loads(manifest.read_text())
        require(data['audit'] == report, 'Audit metadata changed')
        expected = {r['path']: r['sha256'] for r in data['files']}
        actual = {str(p.relative_to(HERE)): sha(p) for p in files()}
        require(expected == actual, 'R06 files changed or unrecorded files exist')
    print(json.dumps(report, indent=2))
