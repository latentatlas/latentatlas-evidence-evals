#!/usr/bin/env python3
"""R13 provenance/scope closure; --freeze once, read-only by default."""
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
    prior=read(HERE/'inputs.json')['prior_manifest_sha256'];counts={}
    assert len(prior)==13
    for name,digest in prior.items():
        p=HERE.parent/name;assert sha(p)==digest,name
        m=read(p)
        for row in m['files']:assert sha(p.parent/row['path'])==row['sha256'],row['path']
        counts[p.parent.name]=len(m['files'])
    c=read(HERE/'results/budget_certificate.json')
    for name,digest in c['source_sha256'].items():assert sha(HERE/name)==digest
    paths={'Q':HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json',
           'jets':HERE.parent/'cusp_shape_design/results/local_jets.json',
           'R11':HERE.parent/'kernel_design_principle/results/candidate_certificate.json',
           'R12':HERE.parent/'kernel_norm_threshold/results/threshold_certificate.json'}
    for k,p in paths.items():assert c['input_sha256'][k]==sha(p)
    ck=read(HERE/'results/budget_check.json');cross=read(HERE/'results/moment_crosscheck.json')
    assert c['status']=='slope_anchors_and_finite_budget_separation_passed'
    assert ck['status']=='independent_rational_slope_budget_checks_passed'
    assert ck['certificate_sha256']==sha(HERE/'results/budget_certificate.json')
    assert ck['source_sha256']==sha(HERE/'check_budget.py')
    assert cross['source_sha256']==sha(HERE/'crosscheck_moment.py')
    assert cross['status']=='separate_positive_moment_numerics_agree'
    assert [r['dps'] for r in cross['values']]==[90,115]
    assert len(c['positive_moment_4_integrals'])==8
    assert len(c['positive_moment_4_high_precision_integrals'])==12
    assert ck['mixture_rank_bernstein_positive'] and ck['strict_separation_from_unconstrained_upper']
    assert Q(ck['readable_M_2e_minus5_bracket'][0])>Q(c['unconstrained_readable_bracket'][1])
    assert Q(ck['readable_M_2e_minus5_bracket'][0])<Q(ck['M_2e_minus5_lower'])
    for p in HERE.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))
    links=0
    for p in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('http://','https://','#')):continue
            assert (p.parent/target.split('#')[0]).exists(),(p.name,target)
            links+=1
    assert (HERE/'figures/slope_budget_bounds.png').stat().st_size>10000
    assert (HERE/'figures/slope_budget_bounds.svg').stat().st_size>10000
    for name in ['ARASTIRMA_NOTU.md','PROOF.md']:
        text=(HERE/name).read_text()
        assert '0.000000000917870847' in text and '0.00000023803280902557' in text
    return dict(status='R13_evidence_and_prior_preservation_checks_passed',
        prior_package_file_counts=counts,prior_manifests_unchanged=13,
        numeric_anchors=2,positive_moments=1,rigorous_integral_panels=20,
        separate_mpmath_precisions=[90,115],rational_checker_passed=True,
        strict_finite_budget_gap_certified=True,mixture_rank_all_parameters=True,
        local_links_checked=links,scientific_figures_visually_reviewed=1,
        metadata_helper_failure_retained=True,decimal_formatting_cleanup_retained=True,
        exact_finite_budget_optimum_computed=False,
        smooth_minimizer_attainment_claimed=False,mass_normalization_imposed=False,
        physical_time_or_noise_model=False,R10_window_transferred=False,
        external_mathematical_review=False,literature_priority_established=False,
        analytic_status='Proof draft with explicit assumptions; not formal or external verification.',
        trust_boundary='Arb local/integral enclosures, prior exact moment certificates, '
                       'and analytic compactness/duality arguments. Closure is not a new proof.',
        audit_source_sha256=sha(__file__))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');args=ap.parse_args()
    result=inspect()
    if args.freeze:
        assert not (HERE/'manifest.json').exists()
        result['closed_utc']=datetime.now(timezone.utc).isoformat()
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[dict(path=str(p.relative_to(HERE)),sha256=sha(p),bytes=p.stat().st_size)
               for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps(dict(created_utc=result['closed_utc'],
            scope='Slope-constrained fixed-Q amplitude cost: analytic draft and certified bounds.',
            audit=result,files=files),indent=2)+'\n')
    else:
        old=read(HERE/'audit_report.json')
        for k,v in result.items():assert old[k]==v,k
        m=read(HERE/'manifest.json')
        for row in m['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert set(r['path'] for r in m['files'])=={
            str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p!=HERE/'manifest.json'}
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
