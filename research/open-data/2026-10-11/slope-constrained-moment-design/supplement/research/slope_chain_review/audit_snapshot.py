#!/usr/bin/env python3
"""R17 one-time freeze and read-only provenance/computation audit."""
import sys
sys.dont_write_bytecode=True
import argparse, ast, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from replay_chain import compare, JOBS
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())

def inspect():
    assert not sys.flags.optimize
    inputs=read(HERE/'replays/inputs.json');prior=inputs['prior_manifests']
    assert len(prior)==17 and sum(v['files'] for v in prior.values())==811
    for name,item in prior.items():
        p=HERE.parent/name;assert sha(p)==item['sha256'],name;m=read(p)
        assert len(m['files'])==item['files']
        for row in m['files']:assert sha(p.parent/row['path'])==row['sha256'],row['path']
    assert inputs['source_sha256']==sha(HERE/'replay_chain.py')
    runs=read(HERE/'replays/runs.json');assert len(runs)==11
    assert all(r['exit_code']==0 and (HERE/'replays'/r['log']).exists() for r in runs)
    for row in runs[:2]:
        package=row['id'].removesuffix('_frozen_audit')
        assert row['source_sha256']==sha(HERE.parent/package/'audit_snapshot.py')
    stored=read(HERE/'replays/comparisons.json');assert len(stored)==9
    results={}
    for (job,package,script,filename),run,previous in zip(JOBS,runs[2:],stored):
        assert run['id']==job and run['package']==package and run['script']==script
        source=HERE.parent/package/script
        assert run['source_sha256']==sha(source)
        replay=HERE/'replays'/run['output'];original=HERE.parent/package/'results'/filename
        assert sha(replay)==run['output_sha256']==previous['replay_sha256']
        assert sha(original)==previous['original_sha256']
        assert previous['original']==str(original.relative_to(HERE.parent))
        row=dict(dyadic_balls=0,equal_other_values=0,changed_metadata_paths=[])
        compare(read(original),read(replay),'',row)
        for k,v in row.items():assert previous[k]==v,(job,k)
        data=read(replay);results[job]=data
        if isinstance(data['source_sha256'],dict):
            for name,digest in data['source_sha256'].items():assert sha(source.parent/name)==digest
        else:assert data['source_sha256']==sha(source)
    # Verify fresh outputs are really linked by content identity, not merely
    # numerically similar to the original dependent files.
    fresh15=sha(HERE/'replays/R15_producer.json');fresh16=sha(HERE/'replays/R16_producer.json')
    assert results['R15_rational']['certificate_sha256']==fresh15
    assert results['R15_numerical']['input_sha256']['certificate']==fresh15
    assert results['R16_producer']['input_sha256']['R15']==fresh15
    assert results['R16_producer']['input_sha256']['R15_check']==sha(HERE/'replays/R15_rational.json')
    assert results['R16_rational']['certificate_sha256']==fresh16
    for name in ['R16_derivatives','R16_design']:
        assert results[name]['input_sha256']['certificate']==fresh16
        assert results[name]['input_sha256']['R15']==fresh15
    known={'Q':HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json',
        'jets':HERE.parent/'cusp_shape_design/results/local_jets.json',
        'R12':HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json',
        'R14':HERE.parent/'kernel_slope_threshold/results/slope_threshold_certificate.json'}
    for result in results.values():
        for k,v in result.get('input_sha256',{}).items():
            if k in known:assert sha(known[k])==v
    report=read(HERE/'replays/report.json')
    assert report['status']=='R15_R16_fresh_chain_replay_passed'
    assert report['jobs']==11 and report['fresh_results']==9
    assert report['dyadic_balls']==sum(r['dyadic_balls'] for r in stored)==2966
    assert report['equal_other_values']==sum(r['equal_other_values'] for r in stored)==832
    assert report['changed_metadata_entries']==sum(len(r['changed_metadata_paths']) for r in stored)==14
    assert report['mathematical_changes']==0 and report['original_files_unchanged'] and report['temporary_tree_removed']
    assert report['source_sha256']==sha(HERE/'replay_chain.py')
    algebra=read(HERE/'results/review_algebra.json')
    assert algebra['source_sha256']==sha(HERE/'check_review_algebra.py')
    assert algebra['certificate_sha256']==sha(HERE.parent/'kernel_slope_remainder/results/remainder_certificate.json')
    assert algebra['status']=='targeted_independent_exact_review_passed'
    assert algebra['check_count']==len(algebra['checks'])==19
    assert algebra['preconditioner_determinant_sign'] in [-1,1]
    assert len(re.findall(r'^\| A\d\d \|', (HERE/'CLAIM_REVIEW.md').read_text(),re.M))==27
    for p in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('https://','http://','#')):continue
            dest=p.parent/target.split('#')[0]
            if dest.name in ['audit_report.json','manifest.json'] and not dest.exists():continue
            assert dest.exists(),(p.name,target)
    for p in HERE.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))
    return dict(status='R17_review_evidence_and_preservation_checks_passed',
        prior_manifest_count=17,prior_frozen_file_entries=811,unchanged_dyadic_balls=2966,
        successful_replay_jobs=11,fresh_result_files=9,equal_other_values=832,
        targeted_exact_checks=19,reviewed_claims=27,primary_sources_compared=6,
        original_scientific_files_changed=False,new_research_results=False,
        scientific_constants_changed=False,expository_clarifications=2,wording_corrections=1,
        analytic_review='No invalidating error found in the reviewed R15-R16 proof chain; see explicit scope and addendum.',
        literature_status='Focused comparison only; priority remains unresolved.',
        formal_verification=False,external_review=False,publication_acceptance_claimed=False,
        trust_boundary='This script checks recorded computation/provenance. The proof review and source comparison remain reasoned assessments, not machine-verified theorems.',
        audit_source_sha256=sha(__file__))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');args=ap.parse_args();out=inspect()
    if args.freeze:
        assert not (HERE/'manifest.json').exists(),'Refuse second freeze'
        out['closed_utc']=datetime.now(timezone.utc).isoformat()
        (HERE/'audit_report.json').write_text(json.dumps(out,indent=2)+'\n')
        files=[dict(path=str(p.relative_to(HERE)),sha256=sha(p),bytes=p.stat().st_size)
            for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps(dict(created_utc=out['closed_utc'],
            scope='Audit-only R15-R16 replay, analytic clarification and focused literature positioning.',
            audit=out,files=files),indent=2)+'\n')
    else:
        old=read(HERE/'audit_report.json')
        for k,v in out.items():assert old[k]==v,k
        m=read(HERE/'manifest.json')
        for row in m['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        actual={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p!=HERE/'manifest.json'}
        assert actual=={row['path'] for row in m['files']}
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
