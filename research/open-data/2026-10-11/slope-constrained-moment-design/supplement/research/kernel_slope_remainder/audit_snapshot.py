#!/usr/bin/env python3
"""R16 one-time freeze and read-only evidence verification."""
import sys
sys.dont_write_bytecode=True
import argparse,ast,hashlib,json,re
from datetime import datetime,timezone
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def inspect():
    prior=read(HERE/'inputs.json')['prior_manifest_sha256'];assert len(prior)==16;counts={}
    for name,digest in prior.items():
        p=HERE.parent/name;assert sha(p)==digest,name;m=read(p)
        for row in m['files']:assert sha(p.parent/row['path'])==row['sha256'],row['path']
        counts[p.parent.name]=len(m['files'])
    assert sum(counts.values())==780
    cp=HERE/'results/remainder_certificate.json';c=read(cp)
    paths={'R15':HERE.parent/'kernel_slope_asymptotics/results/asymptotic_certificate.json',
        'R15_check':HERE.parent/'kernel_slope_asymptotics/results/asymptotic_check.json',
        'jets':HERE.parent/'cusp_shape_design/results/local_jets.json'}
    for k,p in paths.items():assert c['input_sha256'][k]==sha(p),k
    for k,v in c['source_sha256'].items():assert sha(HERE/k)==v,k
    ck=read(HERE/'results/remainder_check.json');cross=read(HERE/'results/derivative_crosscheck.json')
    design=read(HERE/'results/design_crosscheck.json');algebra=read(HERE/'results/algebra_check.json')
    assert c['status']=='uniform_large_slope_remainder_constants_certified'
    assert ck['status']=='independent_rational_uniform_remainder_passed'
    assert cross['status']=='separate_differentiation_samples_agree'
    assert design['status']=='separate_numerical_ramp_design_agrees'
    assert algebra['status']=='exact_rational_remainder_factors_passed'
    for record,source in [(ck,'check_remainder.py'),(cross,'crosscheck_derivatives.py'),(design,'crosscheck_design.py'),(algebra,'check_algebra.py')]:
        assert record['source_sha256']==sha(HERE/source)
    assert ck['certificate_sha256']==sha(cp)
    for record in [cross,design]:
        assert record['input_sha256']['certificate']==sha(cp)
        for k,v in record['input_sha256'].items():
            if k!='certificate':assert v==sha(paths[k]),k
    assert [v['dps'] for v in cross['values']]==[80,110]
    assert all(v['derivative_comparisons']==1680 and v['all_samples_inside_certificate'] for v in cross['values'])
    assert Q(cross['maximum_center_jet_difference'])<Q('1e-60')
    assert [(v['dps'],v['base_gauss_order'],v['local_gauss_order']) for v in design['values']]==[(80,48,8),(110,64,12)]
    assert all(v['numerical_design_within_certified_remainder'] and Q(v['first_three_moment_residual'])<Q('1e-40') and Q(v['relative_budget_residual'])<Q('1e-30') for v in design['values'])
    assert Q(design['cross_precision_amplitude_difference'])<Q('1e-40')
    assert len(algebra['identities'])==5 and algebra['one_step_remainder']=='1/24' and algebra['all_jump_remainder']=='1/12' and algebra['lower_pair_remainder']=='-1/12'
    assert ck['minimum_slope_budget']=='0.00002' and ck['lower_remainder_constant_readable']=='9.624e-33' and ck['upper_remainder_constant_readable']=='2.167e-32'
    assert ck['relative_error_upper_at_minimum_budget']=='0.001178'
    assert len(c['local_derivative_enclosures'])==len(c['center_derivative_enclosures'])==28
    assert all(Q(k)+Q(e)<1 for k,e in zip(ck['contraction_constants_upper'],ck['selfmap_center_constants_upper']))
    bracket=ck['certified_budget_examples'][0]['total_threshold_bracket']
    assert bracket==['0.00000000091787309568619750','0.00000000091787309964331750']
    assert Q(ck['threshold_width_improvement_factor_lower'])>870
    for p in HERE.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))
    for p in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('http://','https://','#')):continue
            item=p.parent/target.split('#')[0]
            if item.name in ['audit_report.json','manifest.json'] and not item.exists():continue
            assert item.exists(),(p.name,target)
    for stem in ['remainder_envelope','threshold_comparison']:
        for ext in ['png','svg']:assert (HERE/'figures'/(stem+'.'+ext)).stat().st_size>10000
    for name in ['ARASTIRMA_NOTU.md','PROOF.md','README.md']:
        content=(HERE/name).read_text();assert all(v in content for v in bracket)
    return dict(status='R16_evidence_and_prior_preservation_checks_passed',prior_manifest_count=16,
        prior_package_file_counts=counts,prior_frozen_file_entries=sum(counts.values()),
        scope='Uniform explicit remainder for every M>=0.00002 at the original exact Q.',
        minimum_slope_budget='0.00002',lower_remainder_constant=ck['lower_remainder_constant_readable'],upper_remainder_constant=ck['upper_remainder_constant_readable'],
        relative_excess_error_upper_at_minimum_budget='0.001178',threshold_bracket_at_minimum_budget=bracket,
        threshold_width_improvement_factor_lower=ck['threshold_width_improvement_factor_lower'],
        contraction_checked_for_all_half_widths_up_to='1/16384',three_center_box=[512,768,384],
        independent_rational_check_passed=True,separate_differentiation_comparisons=3360,separate_precisions=[80,110],
        numerical_ramp_reconstruction_passed=True,numerical_ramp_is_rigorous_witness=False,exact_algebra_factors=5,
        scientific_figures_visually_reviewed=2,previous_certificates_modified=False,
        exact_finite_budget_optimizer_claimed=False,sharp_remainder_order_claimed=False,physical_application_claimed=False,mass_constraint_added=False,R10_window_transferred=False,
        external_review=False,literature_priority_established=False,
        analytic_status='Explicit quantitative fixed-point and remainder proof draft supported by rigorous numerical enclosures; no formal or external review.',
        trust_boundary='R15 exact optimizer/zero identities plus local Arb derivative and infinite-tail envelopes. Independent rational implications and numerical corroboration do not replace the analytic proof.',
        audit_source_sha256=sha(__file__))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');args=ap.parse_args();result=inspect()
    if args.freeze:
        assert not (HERE/'manifest.json').exists();result['closed_utc']=datetime.now(timezone.utc).isoformat()
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[dict(path=str(p.relative_to(HERE)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps(dict(created_utc=result['closed_utc'],scope=result['scope'],audit=result,files=files),indent=2)+'\n')
    else:
        old=read(HERE/'audit_report.json')
        for k,v in result.items():assert old[k]==v,k
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {row['path'] for row in manifest['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p!=HERE/'manifest.json'}
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
