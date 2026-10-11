#!/usr/bin/env python3
"""R08 provenance closure, preservation checks and once-only snapshot."""
import argparse,hashlib,json,re,struct,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from xml.etree import ElementTree
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,msg):
    if not ok:raise ArithmeticError(msg)
def read(p):return json.loads((HERE/p).read_text())
def sources(d,scalar=None):
    h=d['source_sha256']
    if isinstance(h,dict):
        for n,v in h.items():require(sha(HERE/n)==v,'Changed source '+n)
    else:require(scalar is not None and sha(HERE/scalar)==h,'Changed checker '+str(scalar))
def files():return [p for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts]


def audit():
    packages=[]
    for name in ('cusp_verified','cusp_region','cusp_connection','cusp_geometry','cusp_width','cusp_literature','cusp_robustness'):
        base=HERE.parent/name;manifest=json.loads((base/'manifest.json').read_text())
        for row in manifest['files']:require(sha(base/row['path'])==row['sha256'],'Frozen input changed '+name+'/'+row['path'])
        packages.append({'package':name,'files':len(manifest['files']),'manifest_sha256':sha(base/'manifest.json')})
    originals=json.loads((HERE.parent/'cusp_verified/manifest.json').read_text())['original_files']
    for r in originals:require(sha(r['path'])==r['sha256'],'Original file changed '+r['path'])
    prior=subprocess.run([sys.executable,str(HERE.parent/'cusp_robustness/audit_snapshot.py')],capture_output=True,text=True,check=True)
    require('r07_evidence_links_and_preservation_checks_passed' in prior.stdout,'Prior chain audit failed')
    cert=read('results/family_certificate.json');sources(cert)
    require(cert['status']=='arb_full_two_parameter_domain_passed','Family status')
    require(len(cert['slabs'])==4 and all(len(s['cells'])==58 for s in cert['slabs']),'Incomplete cell cover')
    require(len(cert['nu_joins'])==228 and len(cert['rho_joins'])==174,'Incomplete join cover')
    for name,h in cert['input_certificates'].items():require(sha(HERE.parent/name)==h,'Changed family input '+name)
    index=read('cache/index.json');require(sha(HERE/'cache/index.json')==cert['H_cache_index_sha256'],'Changed H cache index')
    require(len(index['files'])==58 and index['derivatives_per_cell']==69,'Incomplete H jets')
    old=json.loads((HERE.parent/'cusp_connection/results/connection_certificate.json').read_text())
    kernel=sha(HERE.parent/'cusp_robustness/results/pinned_cusp_certificate.json')
    require(kernel==cert['kernel_certificate_sha256'],'Wrong kernel direction')
    for entry in index['files']:
        path=HERE/'cache'/entry['file'];require(sha(path)==entry['sha256'],'Changed cached jet')
        row=json.loads(path.read_text());sources(row);i=entry['index']
        require(row['index']==i and row['center']==old['cells'][i]['center'] and row['driver_center']==old['cells'][i]['driver_center'],'Wrong jet identity')
        require(len(row['H_derivatives'])==69 and row['kernel_certificate_sha256']==kernel,'Wrong H moment provenance')
    rat=read('results/rational_check.json');sources(rat,'check_family.py')
    require(rat['status']=='independent_rational_downstream_checks_passed','Rational continuum status')
    require((rat['cells'],rat['nu_joins'],rat['rho_joins'])==(232,228,174),'Incomplete rational cover')
    require(rat['certificate_sha256']==sha(HERE/'results/family_certificate.json'),'Stale rational input')
    require(rat['exact_symbolic_identities']==2,'Missing exact algebra')
    x=read('results/integral_crosscheck.json');sources(x)
    require(x['status']=='21_rigorous_shift_and_9_separate_numerical_checks_passed','Integral cross-check status')
    require(len(x['rigorous_shift_comparisons'])==21 and len(x['mpmath_checks'])==9,'Incomplete integral cross-check')
    require(x['kernel_certificate_sha256']==kernel,'Integral kernel mismatch')
    for row in x['rigorous_shift_comparisons']:require(row['cache_sha256']==sha(HERE/'cache'/f"cell_{row['cell']:02}.json"),'Stale cross-check input')
    points=read('results/point_certificates.json');sources(points)
    require(len(points['rows'])==21 and points['family_certificate_sha256']==sha(HERE/'results/family_certificate.json'),'Point identification provenance')
    folds=read('results/fold_samples.json');sources(folds)
    require(len(folds['models'])==9 and len(folds['samples'])==72 and len(folds['comparisons'])==24,'Incomplete finite folds')
    require(folds['point_certificate_sha256']==sha(HERE/'results/point_certificates.json'),'Stale fold input')
    require(folds['frozen_fold_engine_sha256']==sha(HERE.parent/'cusp_width/endpoint_folds.py'),'Changed frozen fold engine')
    samples=read('results/sample_check.json');sources(samples,'check_samples.py')
    require(samples['status']=='21_cusp_and_144_fold_rational_checks_passed','Sample checker status')
    for n,h in samples['input_sha256'].items():require(sha(HERE/'results'/n)==h,'Stale sample checker input')
    summary=read('results/key_results.json');sources(summary,'summarize_results.py')
    for n,h in summary['input_sha256'].items():require(sha(HERE/'results'/n)==h,'Stale readable summary')
    require(len(summary['rows'])==3,'Summary row count')
    proof=(HERE/'PROOF.md').read_text();tex=(HERE/'THEOREM_APPENDIX.tex').read_text()
    for row in summary['rows']:
        for number in row['finite_W_change_percent_interval']:
            require(number in proof and number in tex,'Manually copied number disagrees with computed summary')
    for p in (HERE/'diagnostics').glob('*.json'):
        data=json.loads(p.read_text())
        sources(data,'check_family.py' if p.name=='rational_sample.json' else None)
    plot=read('figures/metadata.json');sources(plot,'plot_results.py')
    for n,h in plot['input_sha256'].items():require(sha(HERE/'results'/n)==h,'Stale plot input')
    for n,h in plot['files'].items():require(sha(HERE/'figures'/n)==h,'Changed figure')
    visual=read('figures/visual_review.json')
    require(visual['status']=='visually_reviewed','Missing visual review')
    for n,h in visual['files'].items():require(sha(HERE/'figures'/n)==h,'Stale visual review')
    for name in ('pinned_cusp_sheet','finite_fold_comparison'):
        p=HERE/'figures'/(name+'.png');require(struct.unpack('>II',p.read_bytes()[16:24])==(2280,1064),'Unexpected figure dimensions')
        root=ElementTree.parse(HERE/'figures'/(name+'.svg')).getroot();require(root.tag.endswith('svg'),'Invalid vector figure')
    links=0
    for p in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^\n]+?)\)',p.read_text()):
            if target.startswith(('http://','https://','#')):continue
            require((p.parent/target.split('#',1)[0]).exists(),'Broken local link '+str(p)+': '+target);links+=1
    depth=0
    for c in tex:
        depth+=(c=='{')-(c=='}');require(depth>=0,'Unbalanced TeX brace')
    require(depth==0,'Unbalanced TeX braces')
    require(not list(HERE.rglob('__pycache__')),'Unrecorded Python caches')
    return {'status':'r08_evidence_links_and_preservation_checks_passed',
        'preserved_packages':packages,'preserved_scientific_files':sum(p['files'] for p in packages),
        'preserved_original_files':len(originals),'prior_dependency_audit':'passed',
        'continuum_cells':232,'nu_joins':228,'rho_joins':174,'new_central_H_moments':4002,
        'exact_polynomial_identities':2,'rigorous_shift_comparisons':21,'independent_numerical_moments':9,
        'narrow_cusp_contractions':21,'finite_fold_contractions':144,'finite_width_comparisons':24,
        'figures_reviewed':2,'local_markdown_links_checked':links,'latex_compiled':False,
        'external_mathematical_review':False,'literature_priority_established':False,
        'trust_boundary':'See PROOF.md section 8 and the checker reports. Provenance auditing does not independently establish the saved analytic/integral/Taylor enclosures.',
        'audit_source_sha256':sha(__file__)}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');args=ap.parse_args()
    path=HERE/'manifest.json'
    if args.freeze:require(not path.exists(),'R08 already frozen')
    report=audit()
    if args.freeze:
        (HERE/'audit_report.json').write_text(json.dumps(report,indent=2)+'\n')
        data={'created_utc':datetime.now(timezone.utc).isoformat(),
              'scope':'Selected Q-pinning four-cosine direction: full cusp sheet, uniform finite root geometry and strict fold nesting in nu and physical epsilon.',
              'audit':report,'files':[{'path':str(p.relative_to(HERE)),'sha256':sha(p)} for p in files()]}
        with path.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
    else:
        data=json.loads(path.read_text());require(data['audit']==report,'Audit report changed')
        require({r['path']:r['sha256'] for r in data['files']}=={str(p.relative_to(HERE)):sha(p) for p in files()},'Unrecorded or changed R08 files')
    print(json.dumps(report,indent=2))
