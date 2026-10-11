#!/usr/bin/env python3
"""R15 evidence closure and prior-frozen-package preservation audit."""
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
    prior=read(HERE/'inputs.json')['prior_manifest_sha256'];assert len(prior)==15;counts={}
    for name,digest in prior.items():
        p=HERE.parent/name;assert sha(p)==digest,name;manifest=read(p)
        for row in manifest['files']:assert sha(p.parent/row['path'])==row['sha256'],row['path']
        counts[p.parent.name]=len(manifest['files'])
    assert sum(counts.values())==747
    cp=HERE/'results/asymptotic_certificate.json';c=read(cp)
    paths={'Q':HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json',
        'jets':HERE.parent/'cusp_shape_design/results/local_jets.json',
        'R12':HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json',
        'R14':HERE.parent/'kernel_slope_threshold/results/slope_threshold_certificate.json'}
    for k,p in paths.items():assert c['input_sha256'][k]==sha(p),k
    for k,digest in c['source_sha256'].items():assert sha(HERE/k)==digest,k
    ck=read(HERE/'results/asymptotic_check.json');cross=read(HERE/'results/coefficient_crosscheck.json');algebra=read(HERE/'results/algebra_check.json')
    assert c['status']=='asymptotic_hypotheses_and_leading_coefficient_certified'
    assert ck['status']=='independent_rational_asymptotic_hypotheses_passed'
    assert cross['status']=='separate_roots_and_quadratures_agree'
    assert algebra['status']=='exact_rational_asymptotic_identities_passed'
    assert ck['certificate_sha256']==sha(cp) and ck['source_sha256']==sha(HERE/'check_asymptotics.py')
    assert cross['source_sha256']==sha(HERE/'crosscheck_coefficient.py') and cross['input_sha256']['certificate']==sha(cp)
    for k in ['R12','jets']:assert cross['input_sha256'][k]==sha(paths[k])
    assert algebra['source_sha256']==sha(HERE/'check_algebra.py') and len(algebra['identities'])==6
    assert algebra['paired_loss_coefficient']=='1/3' and algebra['unit_step_linear_moment_coefficient']=='-1/6'
    assert [(v['dps'],v['gauss_order']) for v in cross['values']]==[(80,48),(110,64)]
    assert all(v['all_checked_quantities_inside_certificate'] for v in cross['values'])
    assert Q(cross['maximum_gradient_difference'])<Q('1e-45') and Q(cross['gamma_difference'])<Q('1e-60')
    assert len(c['uniform_roots'])==28 and len(c['uniform_sign_cover'])==113
    assert all(len(row['contractions'])==2 and row['stopped_proposal'] is not None for row in c['uniform_roots'])
    assert all(exact(row['stopped_proposal']['proposed_radius'])==exact(row['root_radius']) for row in c['uniform_roots'])
    assert ck['coefficient_readable_bracket']==['9.20340371e-25','9.20340375e-25']
    assert ck['gamma_readable_bracket']==['1.297542117','1.297542121']
    assert ck['finite_budget_absolute_constant_lower']=='9.13976214e-25'
    assert exact(c['dual_localization_radius'])==Q(2)**-40
    for p in HERE.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))
    for p in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('http://','https://','#')):continue
            item=p.parent/target.split('#')[0]
            if item.name in ['audit_report.json','manifest.json'] and not item.exists():continue
            assert item.exists(),(p.name,target)
    for stem in ['linear_transition_loss','switch_contributions']:
        for ext in ['png','svg']:assert (HERE/'figures'/(stem+'.'+ext)).stat().st_size>10000
    for name in ['ARASTIRMA_NOTU.md','PROOF.md']:
        content=(HERE/name).read_text();assert '9.20340371' in content and '9.20340375' in content
    return dict(status='R15_evidence_and_prior_preservation_checks_passed',
        prior_manifest_count=15,prior_package_file_counts=counts,prior_frozen_file_entries=sum(counts.values()),
        exact_dual_optimizer_localized=True,dual_optimizer_uniqueness_argument='Positive local curvature plus convexity, analytic proof draft.',
        root_count_on_unit_interval=28,sign_cover_leaves=113,tail_roots_covered_by='Strictly increasing phase with speed between 81 and 85.',
        general_theorem_hypotheses='Simple separated switches, summable local density derivatives, selected-switch moment rank.',
        law='delta(M)=delta_star+C_star/M^2+o(M^-2)',coefficient_bracket=ck['coefficient_readable_bracket'],
        finite_budget_lower_constant=ck['finite_budget_absolute_constant_lower'],finite_budget_lower_for_M_at_least='0.00002',
        explicit_finite_budget_remainder=False,exact_finite_budget_optimizer_claimed=False,
        independent_rational_check_passed=True,separate_mpmath_precisions=[80,110],separate_gauss_orders=[48,64],exact_algebra_identities=6,
        scientific_figures_visually_reviewed=2,previous_certificates_modified=False,mass_constraint_added=False,
        physical_application_claimed=False,R10_window_transferred=False,external_review=False,literature_priority_established=False,
        analytic_status='Written lower/upper matching proof draft; hypotheses numerically certified for theta example. Not a formal or externally reviewed proof.',
        trust_boundary='Inherited moment enclosures and fresh Arb local/tail enclosures. Rational reconstruction and separate numerical corroboration validate only their stated portions.',
        audit_source_sha256=sha(__file__))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');args=ap.parse_args();result=inspect()
    if args.freeze:
        assert not (HERE/'manifest.json').exists();result['closed_utc']=datetime.now(timezone.utc).isoformat()
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[dict(path=str(p.relative_to(HERE)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps(dict(created_utc=result['closed_utc'],scope='Sharp large-slope cost law and certified hypotheses at the original exact Q.',audit=result,files=files),indent=2)+'\n')
    else:
        old=read(HERE/'audit_report.json')
        for k,v in result.items():assert old[k]==v,k
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {row['path'] for row in manifest['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p!=HERE/'manifest.json'}
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
