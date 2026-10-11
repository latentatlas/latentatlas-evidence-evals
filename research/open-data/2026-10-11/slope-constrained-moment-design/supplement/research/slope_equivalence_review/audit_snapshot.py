#!/usr/bin/env python3
"""Freeze once, then verify R18 evidence and preserved predecessors read-only."""
import sys
sys.dont_write_bytecode=True
import argparse
import ast
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from check_normalization import run_checks


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def inspect():
    assert not sys.flags.optimize, 'Assertions must be enabled'
    inputs=read(HERE/'inputs.json')
    prior=inputs['prior_manifests']
    assert len(prior)==18 and sum(x['files'] for x in prior.values())==847
    for name,row in prior.items():
        path=HERE.parent/name
        assert sha(path)==row['sha256'],name
        manifest=read(path)
        assert len(manifest['files'])==row['files']
        for item in manifest['files']:
            assert sha(path.parent/item['path'])==item['sha256'],(name,item['path'])
    for name in inputs['mathematical_sources']:
        assert (HERE.parent/name).is_file(),name
    saved=read(HERE/'results/normalization_checks.json')
    assert saved==run_checks(), 'Fresh exact diagnostics disagree with saved output'
    assert saved['check_groups']==6
    sources=read(HERE/'sources.json')
    assert not sources['full_source_files_redistributed']
    assert sources['temporary_sources_removed_at_closure']
    assert {s['id'] for s in sources['sources']}=={f'L{i:02}' for i in range(7,14)}
    assert len(sources['sources'])==7
    for source in sources['sources']:
        assert source['primary_source'] and not source['full_paper_review_claimed']
        assert source['read_url'].startswith('https://') and source['reviewed_scope']
        identity=source['download_identity']
        if identity is not None:
            assert re.fullmatch('[0-9a-f]{64}',identity['sha256'])
            assert identity['bytes']>0 and identity['pages']>0
    assert sum(s['download_identity'] is not None for s in sources['sources'])==6
    log=(HERE/'SEARCH_LOG.md').read_text()
    assert len(re.findall(r'^\d+\. `',log,re.M))==41
    for path in HERE.glob('*.md'):
        for link in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if link.startswith(('https://','http://','#')):
                continue
            target=path.parent/link.split('#')[0]
            if target.name in ('manifest.json','audit_report.json') and not target.exists():
                continue
            assert target.exists(),(path.name,link)
    for path in HERE.rglob('*.py'):
        ast.parse(path.read_text(),filename=str(path))
    assert not list(HERE.rglob('*.pdf')), 'Full source papers must not enter this package'
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))
    return dict(status='R18_equivalence_review_evidence_checks_passed',
                prior_manifest_count=18,prior_frozen_file_entries=847,
                primary_sources_compared=7,downloaded_PDF_identities=6,
                recorded_search_queries=41,exact_diagnostic_groups=6,
                original_scientific_files_changed=False,
                scientific_constants_changed=False,new_research_theorem_claimed=False,
                auxiliary_norm_equivalence='Exact by matching definitions; see E2.',
                moment_value_equivalence='Classical minimax application; analytic argument in E3, not machine formalized.',
                literature_priority='Unresolved; no equivalent full R15 theorem identified in the reviewed results.',
                external_review=False,formal_verification=False,
                publication_acceptance_claimed=False,
                full_source_files_redistributed=False,
                trust_boundary='Hashes and rational examples are checked; source interpretation and minimax reasoning are not automatically verified.',
                audit_source_sha256=sha(__file__))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--freeze',action='store_true')
    args=ap.parse_args(); result=inspect()
    if args.freeze:
        assert not (HERE/'manifest.json').exists(), 'Refuse a second freeze'
        result['closed_utc']=datetime.now(timezone.utc).isoformat()
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[dict(path=str(p.relative_to(HERE)),sha256=sha(p),bytes=p.stat().st_size)
               for p in sorted(HERE.rglob('*')) if p.is_file()]
        manifest=dict(created_utc=result['closed_utc'],
                      scope='Focused KR/flat norm equivalence review; no new scientific theorem or changed certificate.',
                      audit=result,files=files)
        (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        old=read(HERE/'audit_report.json')
        for key,value in result.items():
            assert old[key]==value,key
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:
            path=HERE/row['path']
            assert sha(path)==row['sha256'],row['path']
            assert path.stat().st_size==row['bytes']
        actual={str(p.relative_to(HERE)) for p in HERE.rglob('*')
                if p.is_file() and p.name!='manifest.json'}
        assert actual=={row['path'] for row in manifest['files']}
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
