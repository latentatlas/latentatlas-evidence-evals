#!/usr/bin/env python3
"""R07 provenance/link audit. --freeze records the package once.

This checks evidence connections and preserved files. It does not replace
the mathematical checkers or establish literature priority.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,msg):
    if not ok:raise ArithmeticError(msg)
def read(name):return json.loads((HERE/name).read_text())
def own_sources(data):
    h=data['source_sha256']
    if isinstance(h,dict):
        for p,expected in h.items():require(sha(HERE/p)==expected,'Stale source '+p)
def files():return [p for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts]


def audit():
    packages=[]
    for name in ('cusp_verified','cusp_region','cusp_connection','cusp_geometry','cusp_width','cusp_literature'):
        base=HERE.parent/name;m=json.loads((base/'manifest.json').read_text())
        for row in m['files']:require(sha(base/row['path'])==row['sha256'],'Changed frozen file '+name+'/'+row['path'])
        packages.append({'package':name,'files':len(m['files']),'manifest_sha256':sha(base/'manifest.json')})
    originals=json.loads((HERE.parent/'cusp_verified/manifest.json').read_text())['original_files']
    for row in originals:require(sha(row['path'])==row['sha256'],'Changed original '+row['path'])
    prior=subprocess.run([sys.executable,str(HERE.parent/'cusp_literature/audit_snapshot.py')],capture_output=True,text=True,check=True)
    require('r06_provenance_and_exact_algebra_passed' in prior.stdout,'R06 dependency audit did not pass')
    cert=read('results/robustness_certificate.json');own_sources(cert)
    require(len(cert['cells'])==58 and len(cert['seams'])==57,'Incomplete full-arc certificate')
    for p,h in cert['input_certificates'].items():require(sha(HERE.parent/p)==h,'Changed input certificate '+p)
    require(cert['epsilon_requested_rational']=='1/1000000000000000000','Unexpected proof budget')
    rational=read('results/rational_check.json')
    require(rational['status']=='independent_rational_robustness_checks_passed','Rational proof status')
    require(rational['cells_checked']==58 and rational['joins_checked']==57,'Incomplete rational proof')
    require(rational['certificate_sha256']==sha(HERE/'results/robustness_certificate.json'),'Stale rational certificate')
    require(rational['source_sha256']==sha(HERE/'check_robustness.py'),'Stale rational source')
    condition=read('results/condition_witness.json');own_sources(condition)
    pinned=read('results/pinned_cusp_certificate.json');own_sources(pinned)
    quartic=sha(HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json')
    require(condition['quartic_certificate_sha256']==pinned['quartic_certificate_sha256']==quartic,'Quartic identity mismatch')
    numerical_rows=0
    for cp,rp,sp,status,rows in (
        ('results/condition_witness.json','results/condition_check.json','check_condition.py','rational_sensitivity_and_independent_numerical_agreement',3),
        ('results/pinned_cusp_certificate.json','results/pinned_check.json','check_pinned.py','exact_identity_rational_bounds_and_numerical_check_passed',5)):
        check=read(rp);require(check['status']==status,'Checker status '+rp)
        key='condition_certificate_sha256' if rows==3 else 'certificate_sha256'
        require(check[key]==sha(HERE/cp),'Stale checker input '+rp)
        require(check['source_sha256']==sha(HERE/sp),'Stale checker source '+sp)
        require(len(check['rows'])==rows,'Incomplete independent numerics '+rp);numerical_rows+=rows
    require(len(condition['shifted_integrals'])==2 and all(len(r)==3 for r in condition['shifted_integrals']),'Condition integral count')
    require(len(pinned['shifted_integrals'])==4 and all(len(pair)==2 and all(len(r)==5 for r in pair) for pair in pinned['shifted_integrals']),'Pinned integral count')
    plot=read('figures/metadata.json')
    require(plot['source_sha256']==sha(HERE/'plot_results.py'),'Stale plot source')
    for p,h in plot['inputs'].items():require(sha(HERE.parent/p)==h,'Stale plot input '+p)
    for p,h in plot['files'].items():require(sha(HERE/'figures'/p)==h,'Changed figure '+p)
    visual=read('figures/visual_review.json')
    require(visual['status']=='visually_reviewed','Figures not reviewed')
    for p,h in visual['files'].items():require(sha(HERE/'figures'/p)==h,'Visual review stale '+p)
    links=0
    for p in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^\n]+?)\)',p.read_text()):
            if target.startswith(('http://','https://','#')):continue
            require((p.parent/target.split('#',1)[0]).exists(),'Broken local link '+str(p)+':'+target);links+=1
    tex=(HERE/'THEOREM_APPENDIX.tex').read_text();depth=0
    for char in tex:
        depth+=(char=='{')-(char=='}');require(depth>=0,'Unbalanced TeX closing brace')
    require(depth==0,'Unbalanced TeX braces')
    require(not list(HERE.rglob('__pycache__')),'Unrecorded Python cache in R07')
    return {'status':'r07_evidence_links_and_preservation_checks_passed',
        'preserved_packages':packages,'preserved_scientific_files':sum(p['files'] for p in packages),
        'preserved_original_files':len(originals),'prior_dependency_audit':'passed',
        'uniform_cells':58,'root_containment_joins':57,'new_rigorous_shifted_integrals':46,
        'direct_independent_numerical_moments':numerical_rows,'exact_cofactor_identities':3,
        'figures_reviewed':2,'local_markdown_links_checked':links,'latex_compiled':False,
        'external_mathematical_review':False,'literature_priority_established':False,
        'audit_source_sha256':sha(Path(__file__))}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    manifest=HERE/'manifest.json'
    if args.freeze:require(not manifest.exists(),'R07 already frozen; do not overwrite')
    report=audit()
    if args.freeze:
        (HERE/'audit_report.json').write_text(json.dumps(report,indent=2)+'\n')
        data={'created_utc':datetime.now(timezone.utc).isoformat(),
              'scope':'R07 full-arc kernel robustness, an infinitesimal sensitivity direction, and a separate finite-amplitude direction pinning one exact cusp.',
              'audit':report,'files':[{'path':str(p.relative_to(HERE)),'sha256':sha(p)} for p in files()]}
        with manifest.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
    else:
        data=json.loads(manifest.read_text());require(data['audit']==report,'Audit report changed')
        require({r['path']:r['sha256'] for r in data['files']}=={str(p.relative_to(HERE)):sha(p) for p in files()},'R07 files changed or unrecorded files exist')
    print(json.dumps(report,indent=2))
