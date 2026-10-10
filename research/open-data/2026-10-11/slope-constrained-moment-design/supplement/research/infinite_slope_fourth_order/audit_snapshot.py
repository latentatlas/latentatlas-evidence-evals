#!/usr/bin/env python3
"""R23 portable provenance/recorded-arithmetic audit; analytic proofs stay explicit."""
import sys
sys.dont_write_bytecode=True
import argparse,ast,hashlib,json,re,subprocess,tempfile
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent
sys.path.insert(0,str(RESEARCH/'finite_slope_optimum'))
from exact_interval import QI
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def dy(pair):return F(pair[0])*F(2)**pair[1]
def interval(v):
    lo,hi=dy(v['lower']),dy(v['upper']);assert lo<=hi
    return QI(lo,hi)
def match(x,y):
    v=x-y;assert v.lo<=0<=v.hi
def inspect(with_arb):
    assert __debug__,'Assertions must be enabled.'
    base=read(HERE/'baseline.json');count=0
    assert len(base['manifest_sha256'])==23
    for rel,digest in base['manifest_sha256'].items():
        p=RESEARCH/rel;assert sha(p)==digest,rel
        for row in read(p)['files']:
            assert sha(p.parent/row['path'])==row['sha256'],(rel,row['path']);count+=1
    assert count==base['frozen_entries']==991
    alg=read(HERE/'results/algebra.json');cert=read(HERE/'results/certificate.json');quad=read(HERE/'results/integrals.json')
    assert alg['check_groups']==len(alg['checks'])==12 and all(r['passed'] for r in alg['checks'])
    assert alg['source_sha256']==sha(HERE/'check_algebra.py')
    assert alg['R22_algebra_helper_sha256']==sha(RESEARCH/'finite_slope_fourth_order/check_fourth_order.py')
    assert alg['theta_derivative_polynomials'][3]==[-375,3270,-4232,1440,-128]
    assert alg['theta_envelope_constant']==4980928512
    assert cert['source_sha256']==sha(HERE/'certify_example.py') and cert['algebra_sha256']==sha(HERE/'results/algebra.json')
    assert cert['dps']==100 and len(cert['rows'])==6
    cc={k:interval(v) for k,v in cert['coefficients'].items()}
    assert cc['delta'].lo==cc['delta'].hi==F(1,4)
    match(cc['C2'],cc['delta']**3*cc['Gamma']/(3*cc['D']))
    match(cc['C4'],cc['delta']**5*(cc['Gamma']**2/(3*cc['D']**2)-cc['Xi']/cc['D']))
    match(cc['P'],cc['B']**2/(2*cc['G']));match(cc['Xi'],cc['R']-cc['P'])
    assert cc['C4'].lo>0
    nvalues=0;ncoef=0
    assert quad['source_sha256']==sha(HERE/'crosscheck_integrals.py')
    assert quad['certificate_sha256']==sha(HERE/'results/certificate.json') and quad['precisions']==[80,120]
    assert len(quad['rows'])==6
    table=(HERE/'results/TABLE.md').read_text()
    for cr,qr in zip(cert['rows'],quad['rows']):
        assert cr['a']==qr['a'] and cr['bisection_steps']==220
        assert interval(cr['initial_moment_derivative']).lo>0
        assert interval(cr['endpoint_moments'][0]).hi<0 and interval(cr['endpoint_moments'][1]).lo>0
        assert interval(cr['residual_cell_endpoints'][0]).lo>0 and interval(cr['residual_cell_endpoints'][1]).hi<0
        bal=interval(cr['balanced_cell_check']);assert bal.lo<=0<=bal.hi
        vals={k:interval(v) for k,v in cr['intervals'].items()};a=F(cr['a'])
        match(vals['M'],vals['A']/a);match(vals['A'],cc['f']/vals['S'])
        match(vals['leading_error'],vals['A']-cc['delta']-cc['C2']/vals['M']**2)
        match(vals['fourth_error'],vals['leading_error']-cc['C4']/vals['M']**4)
        match(vals['scaled_fourth_residual'],vals['leading_error']*vals['M']**4)
        assert vals['leading_error'].lo>vals['fourth_error'].hi>0
        assert 0<vals['error_ratio'].lo<vals['error_ratio'].hi<1
        assert set(vals)==set(qr['high']['values'])==set(qr['checks'])
        assert F(qr['low']['max_residual'])<F('1e-65') and F(qr['high']['max_residual'])<F('1e-105')
        for key,v in vals.items():
            x=F(qr['high']['values'][key]);assert v.lo<x<v.hi,(cr['a'],key)
            assert abs(x-F(qr['low']['values'][key]))<F('1e-70') and qr['checks'][key]['inside'];nvalues+=1
        for key,x in qr['high']['coefficients'].items():
            x=F(x);v=cc[key];assert v.lo<=x<=v.hi,key
            assert abs(x-F(qr['low']['coefficients'][key]))<F('1e-70');ncoef+=1
        for key in ['M','A','scaled_fourth_residual','leading_error','fourth_error','error_ratio']:
            assert format(float((vals[key].lo+vals[key].hi)/2),'.12g') in table
    assert nvalues==quad['sample_value_comparisons']==54 and ncoef==quad['coefficient_comparisons']==78
    th=cert['theta_weighted_tail'];assert th['E_constant']==alg['theta_envelope_constant']
    assert interval(th['weighted_decay_c']).lo>F(97,100)
    assert interval(th['theta_derivative_term_ratio_upper']).hi<F(1,2)
    assert interval(th['weighted_majorant_tail_upper']).hi<F(10)**-3500
    assert th['not_a_theta_C4_enclosure'] and th['tail_starts_at']==2
    assert len(cert['geometric_series_truncation'])==7
    for r in cert['geometric_series_truncation']:
        fac=1-interval(r['omitted_fraction'])
        expected=cc['delta']**5*((cc['Gamma']*fac)**2/(3*cc['D']**2)-cc['Xi']*fac/cc['D'])
        match(interval(r['C4_partial']),expected)
        match(interval(r['C4_error']),cc['C4']-interval(r['C4_partial']))
        assert interval(r['C4_error']).lo>0
    with tempfile.TemporaryDirectory(prefix='r23-replay-') as tmp:
        tmp=Path(tmp)
        jobs=[('check_algebra.py','algebra.json')]
        if with_arb:jobs.append(('certify_example.py','certificate.json'))
        for script,out in jobs:
            fresh=tmp/out
            result=subprocess.run([sys.executable,'-B',str(HERE/script),'--output',str(fresh)],cwd=tmp,capture_output=True,text=True)
            assert result.returncode==0,result.stdout+result.stderr
            assert sha(fresh)==sha(HERE/'results'/out),out
    plot=read(HERE/'results/plot_data.json');qa=read(HERE/'results/figure_qa.json')
    assert plot['source_sha256']==sha(HERE/'plot_results.py') and plot['certificate_sha256']==sha(HERE/'results/certificate.json')
    assert len(plot['value_curve'])==180 and len(plot['tail_curve'])==64 and plot['profile_samples']==1800
    for name,digest in plot['figures'].items():assert sha(HERE/'figures'/name)==digest
    assert qa['png_sha256']==sha(HERE/'figures/infinite_switches.png')
    assert qa['panels']==3 and not qa['clipped_text'] and not qa['overlapping_labels']
    for name,prefix,n in [('PROOF.md','W',17),('THETA.md','T',9),('EXAMPLE.md','E',6)]:
        tags=re.findall(r'\\tag\{'+prefix+r'(\d+)\}',(HERE/name).read_text())
        assert tags==list(map(str,range(1,n+1))),(name,tags)
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))
    for p in HERE.rglob('*'):
        if p.is_file() and p.suffix in ['.md','.json','.py','.txt']:
            assert all(b>=32 or b in (9,10,13) for b in p.read_bytes()),p.name
        if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
    for p in HERE.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('https://','http://','#')):continue
            q=p.parent/target.split('#')[0]
            if q.name in ['audit_report.json','manifest.json'] and not q.exists():continue
            assert q.exists(),(p.name,target)
    return {'status':'R23_infinite_switch_evidence_and_preservation_passed','prior_manifests':23,
      'prior_frozen_file_entries':count,'exact_check_groups':12,'sample_budgets':6,'sample_value_enclosures':54,
      'independent_precision_runs':12,'independent_sample_comparisons':54,'independent_coefficient_comparisons':78,
      'theta_weighted_majorant_tail_bound':'10^-3500 beyond root position 2',
      'general_equations':17,'theta_equations':9,'example_equations':6,'scientific_figure_panels':3,
      'theta_fourth_order_analytic_corollary':True,'theta_numerical_fourth_order_coefficient_enclosure':False,
      'explicit_uniform_fourth_order_remainder':False,'exact_theta_finite_M_optimizer_identified':False,
      'previous_packages_modified':False,'manuscripts_modified':False,'formal_proof':False,
      'external_referee_review':False,'literature_priority_established':False,'public_release_or_submission':False,
      'audit_source_sha256':sha(__file__),
      'trust_boundary':'Provenance, fresh exact algebra, stored interval arithmetic and independent numerical comparisons; --with-arb also replays Arb. The weighted analytic proof is documented, not mechanically verified.'}
def main():
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group();g.add_argument('--preflight',action='store_true');g.add_argument('--freeze',action='store_true')
    ap.add_argument('--with-arb',action='store_true');args=ap.parse_args();result=inspect(args.with_arb)
    if args.freeze:
        assert not (HERE/'manifest.json').exists(),'Already frozen.'
        result['closed_utc']=datetime.now(timezone.utc).isoformat();result['Arb_replayed_at_freeze']=args.with_arb
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps({'created_utc':result['closed_utc'],
            'scope':'Weighted infinite-switch fourth-order value theorem, fixed theta analytic corollary, and separate periodic control example.',
            'files':files,'audit':result},indent=2)+'\n')
    elif not args.preflight:
        recorded=read(HERE/'audit_report.json')
        for key,val in result.items():assert recorded[key]==val,key
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {row['path'] for row in manifest['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='manifest.json'}
    print(json.dumps({**result,'Arb_replayed_in_this_run':args.with_arb},indent=2))
if __name__=='__main__':main()
