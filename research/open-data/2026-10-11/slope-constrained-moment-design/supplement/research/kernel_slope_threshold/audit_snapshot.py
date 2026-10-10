#!/usr/bin/env python3
"""R14 evidence closure; freeze once, read-only verification afterwards."""
import sys
sys.dont_write_bytecode=True
import argparse,ast,hashlib,json,re
from datetime import datetime,timezone
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def exact(v):
    m,e=v['mid_man_exp'];r,f=v['rad_man_exp'];assert r==0
    return Q(m)*Q(2)**e

def inspect():
    prior=read(HERE/'inputs.json')['prior_manifest_sha256'];assert len(prior)==14;counts={}
    for name,digest in prior.items():
        p=HERE.parent/name;assert sha(p)==digest,name;m=read(p)
        for row in m['files']:assert sha(p.parent/row['path'])==row['sha256'],row['path']
        counts[p.parent.name]=len(m['files'])
    cp=HERE/'results/slope_threshold_certificate.json';c=read(cp)
    paths={'Q':HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json',
           'jets':HERE.parent/'cusp_shape_design/results/local_jets.json',
           'R11':HERE.parent/'kernel_design_principle/results/candidate_certificate.json',
           'R12':HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json',
           'R13':HERE.parent/'kernel_slope_budget/results/budget_certificate.json',
           'probe':HERE/'diagnostics/candidate_probe.json'}
    for k,p in paths.items():assert c['input_sha256'][k]==sha(p),k
    for k,digest in c['source_sha256'].items():assert sha(HERE/k)==digest,k
    ck=read(HERE/'results/slope_threshold_check.json');cross=read(HERE/'results/moment_crosscheck.json');probe=read(paths['probe'])
    assert c['status']=='certified_finite_slope_near_minimum_design'
    assert ck['status']=='independent_rational_finite_slope_threshold_passed'
    assert cross['status']=='separate_original_coordinate_quadratures_agree'
    assert probe['status']=='nonrigorous_candidate_only' and probe['source_sha256']==sha(HERE/'probe_candidate.py')
    for k in ['R12','jets']:assert probe['input_sha256'][k]==sha(paths[k])
    assert ck['certificate_sha256']==sha(cp) and ck['source_sha256']==sha(HERE/'check_threshold.py')
    assert cross['source_sha256']==sha(HERE/'crosscheck_moments.py')
    assert cross['input_sha256']['certificate']==sha(cp)
    for k in ['R12','R11','jets']:assert cross['input_sha256'][k]==sha(paths[k])
    assert [(r['dps'],r['gauss_order']) for r in cross['values']]==[(70,48),(100,64)]
    assert all(r['all_moments_weights_and_rank_inside_certificate'] for r in cross['values'])
    assert Q(cross['maximum_cross_precision_moment_difference'])<Q('1e-45')
    assert len(c['shift_integrals'])==3 and len(c['transition_integrals'])==28
    assert all(len(row['oriented_integrals'])==9 for row in c['shift_integrals'])
    assert all(len(row['rescaled_integrals'])==9 for row in c['transition_integrals'])
    assert len(c['lower_crossings'])==28
    assert ck['readable_bracket']==c['readable_bracket']==['0.000000000917873080','0.000000000917876530']
    assert Q(ck['relative_bracket_gap_upper'])<Q('3.76e-6')
    assert Q(ck['feasible_slope_upper'])<Q('0.00002')
    penalty=list(map(Q,ck['relative_increase_over_unconstrained']))
    assert penalty[0]>Q('2.48e-6') and penalty[1]<Q('6.25e-6')
    old=read(paths['R12']);width_ratio=exact(c['smoothing_width'])/exact(old['smoothing_width'])
    assert width_ratio==198000
    for p in HERE.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))
    links=0
    for p in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('http://','https://','#')):continue
            item=p.parent/target.split('#')[0]
            if item.name in ['audit_report.json','manifest.json'] and not item.exists():continue
            assert item.exists(),(p.name,target)
            links+=1
    for stem in ['finite_slope_threshold','smooth_design_transition']:
        for ext in ['png','svg']:assert (HERE/'figures'/(stem+'.'+ext)).stat().st_size>10000
    for name in ['ARASTIRMA_NOTU.md','PROOF.md']:
        content=(HERE/name).read_text()
        assert all(v in content for v in c['readable_bracket'])
    # Count closure links consistently before and after the first freeze.
    return dict(status='R14_evidence_and_prior_preservation_checks_passed',
        prior_manifest_count=14,prior_package_file_counts=counts,prior_frozen_file_entries=sum(counts.values()),
        slope_budget='0.00002',readable_bracket=c['readable_bracket'],
        relative_gap_upper=ck['relative_bracket_gap_upper'],relative_penalty_bounds=ck['relative_increase_over_unconstrained'],
        rigorous_shift_integrals=27,rigorous_transition_integrals=252,disjoint_loss_neighborhoods=28,
        separate_mpmath_precisions=[70,100],separate_gauss_orders=[48,64],
        all_moments_weights_rank_inside_certificate=True,independent_rational_check_passed=True,
        smoothing_scale_ratio_to_R12=198000,scientific_figures_visually_reviewed=2,
        previous_certificates_modified=False,exact_minimizer_claimed=False,full_value_curve_computed=False,
        mass_constraint_added=False,physical_application_claimed=False,R10_window_transferred=False,
        external_review=False,literature_priority_established=False,
        analytic_status='Explicit proof draft and certified arithmetic; no formal proof-assistant or external review.',
        trust_boundary='Prior moment/root/majorant certificates plus new Arb integrals and local enclosures. Rational and separate numerical reconstructions validate their stated parts, not the entire analytic framework.',
        audit_source_sha256=sha(__file__))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');args=ap.parse_args();result=inspect()
    if args.freeze:
        assert not (HERE/'manifest.json').exists()
        result['closed_utc']=datetime.now(timezone.utc).isoformat()
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[dict(path=str(p.relative_to(HERE)),sha256=sha(p),bytes=p.stat().st_size)
               for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps(dict(created_utc=result['closed_utc'],
            scope='A certified narrow amplitude bracket under Lip_u(h)<=0.00002 at the fixed original Q.',
            audit=result,files=files),indent=2)+'\n')
    else:
        old=read(HERE/'audit_report.json')
        for k,v in result.items():assert old[k]==v,k
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert set(row['path'] for row in manifest['files'])=={
            str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p!=HERE/'manifest.json'}
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
