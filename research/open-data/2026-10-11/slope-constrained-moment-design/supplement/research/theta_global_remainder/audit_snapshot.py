#!/usr/bin/env python3
"""R26 evidence integrity, exact/rational replay, optional Arb replay and freeze."""
import sys
sys.dont_write_bytecode=True
import argparse,ast,hashlib,json,re,subprocess,tempfile
from datetime import datetime,timezone
from decimal import Decimal,localcontext
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def ends(v):
    m,e=v['mid_man_exp'];r,s=v['rad_man_exp'];c=F(m)*F(2)**e;rr=F(r)*F(2)**s
    return c-rr,c+rr
def inside(v,x):
    lo,hi=ends(v);return lo<=F(x)<=hi
def inspect(with_arb):
    assert __debug__,'Assertions must be enabled.'
    base=read(HERE/'baseline.json');n=0
    assert len(base['manifest_sha256'])==26
    for rel,digest in base['manifest_sha256'].items():
        p=RESEARCH/rel;assert sha(p)==digest,rel
        for row in read(p)['files']:
            assert sha(p.parent/row['path'])==row['sha256'],(rel,row['path']);n+=1
    assert n==base['frozen_entries']==1070
    cp=HERE/'results/certificate.json';ap=HERE/'results/algebra.json';rp=HERE/'results/rational_check.json'
    oldp=RESEARCH/'theta_effective_remainder/results/certificate.json'
    c,a,r,d=read(cp),read(ap),read(rp),read(HERE/'results/direct_check.json')
    old=read(oldp)
    assert c['source_sha256']==sha(HERE/'certify_global.py') and c['dps']==120
    assert c['algebra_sha256']==sha(ap) and c['R25_certificate_sha256']==sha(oldp)
    assert a['source_sha256']==sha(HERE/'check_algebra.py')
    assert a['check_groups']==len(a['checks'])==22 and all(x['passed'] for x in a['checks'])
    assert r['source_sha256']==sha(HERE/'check_bounds.py') and r['rounding_bits']==512
    assert r['rational_helper_sha256']==sha(RESEARCH/'theta_fourth_order/rational_intervals.py')
    assert r['certificate_sha256']==sha(cp) and r['R25_certificate_sha256']==sha(oldp) and r['algebra_sha256']==sha(ap)
    assert r['check_count']==len(r['checks'])==22
    M0=F('2e-5');published=[F('9.593e-54'),F('1.488e-53')];c4=F('2.49203004e-39')
    assert list(map(F,c['published_constants']))==published
    assert F(a['epsilon'])==F(1,4096) and F(a['a_max'])==F(1,16384)
    assert inside(c['minimum_slope_budget'],M0) and ends(c['tail_gap_raw_residual'])[0]>0
    assert all(ends(x)[0]>0 for x in [c['lower_endpoint_coefficient'],c['upper_endpoint_margin'],
                    c['auxiliary_derivative_lower'],c['inversion_derivative_lower'],c['positive_quartic_dominance_margin']])
    for k,v in zip(['Kminus','Kplus'],published):
        assert 0<ends(c[k])[1]<v and 0<F(r[k+'_upper'])<v
    for x,y in zip(c['repair_contraction'],c['repair_forcing']):assert ends(x)[1]+ends(y)[1]<1
    assert 0<ends(c['target_sixth_tail'])[1]<F('8.411e-35')
    assert 0<ends(c['dual_eighth_tail'])[1]<F('3.366e-40')
    assert published[0]/(c4*M0*M0)<F('9.624e-6')
    assert published[1]/(c4*M0*M0)<F('1.493e-5')
    assert published[1]/M0**6==F('2.325e-25')
    assert d['source_sha256']==sha(HERE/'crosscheck_tail.py') and d['R25_certificate_sha256']==sha(oldp) and d['algebra_sha256']==sha(ap)
    assert [(x['dps'],x['quadrature_order']) for x in d['runs']]==[(90,20),(130,28)]
    E=[list(map(F,row)) for row in a['q_relative_constants']];W=list(map(F,a['weight_relative_constants']))
    H=list(map(F,a['active_moment_constants']));A4=F(a['residual_neighborhood_fourth_constant']);A5=F(a['residual_neighborhood_fifth_constant'])
    Cs=F(a['active_residual_sixth_constant']);Ch=F(a['active_balance_fourth_constant']);inequalities=0
    for run in d['runs']:
        assert run['theta_terms']==12 and run['inequalities_checked']==300
        assert [x['phase_index'] for x in run['rows']]==[27,40,53,80]
        before=inequalities
        for row in run['rows']:
            assert F(row['root'])>1 and len(row['normalized_moment_jets'])==4
            for j in range(4):
                assert len(row['normalized_moment_jets'][j])==6
                for l in range(6):assert abs(F(row['normalized_moment_jets'][j][l]))<=E[j][l];inequalities+=1
            assert abs(F(row['kappa_over_exp4z']))<46;inequalities+=1
            assert len(row['samples'])==2
            for sample,factor in zip(row['samples'],[F(1,2),F(1)]):
                assert F(sample['active_fraction'])==factor and len(sample['endpoint_checks'])==2
                for ep in sample['endpoint_checks']:
                    assert len(ep['normalized_weight_derivatives'])==6
                    for l,x in enumerate(ep['normalized_weight_derivatives']):assert abs(F(x))<=W[l];inequalities+=1
                    assert abs(F(ep['normalized_residual_fourth']))<A4;inequalities+=1
                    assert abs(F(ep['normalized_residual_fifth']))<A5;inequalities+=1
                    assert F(ep['normalized_trial_derivative'])>200;inequalities+=1
                    assert F(1,2)<F(ep['weight_ratio'])<2;inequalities+=1
                assert len(sample['normalized_moment_remainders'])==3
                for j,x in enumerate(sample['normalized_moment_remainders']):assert abs(F(x))<H[j];inequalities+=1
                assert abs(F(sample['normalized_target_remainder']))<Cs;inequalities+=1
                assert abs(F(sample['normalized_balance_defect']))<Ch;inequalities+=1
        assert inequalities-before==300
    differences=[]
    for lo,hi in zip(d['runs'][0]['rows'],d['runs'][1]['rows']):
        for l,h in zip(lo['samples'],hi['samples']):
            lv=l['normalized_moment_remainders']+[l['normalized_target_remainder'],l['normalized_balance_defect']]
            hv=h['normalized_moment_remainders']+[h['normalized_target_remainder'],h['normalized_balance_defect']]
            for x,y in zip(lv,hv):
                x,y=F(x),F(y);error=abs(x-y)/max(abs(y),F('1e-100'))
                assert error<F('1e-40');differences.append(error)
    assert inequalities==600 and len(differences)==d['precision_comparisons']==40
    assert abs(max(differences)-F(d['maximum_relative_precision_difference']))/max(differences)<F('1e-30')
    with tempfile.TemporaryDirectory(prefix='r26-replay-') as td:
        td=Path(td);jobs=[('check_algebra.py',ap,[]),('check_bounds.py',rp,['--certificate',str(cp)])]
        if with_arb:jobs.append(('certify_global.py',cp,[]))
        for script,recorded,extra in jobs:
            fresh=td/recorded.name
            result=subprocess.run([sys.executable,'-B',str(HERE/script),*extra,'--output',str(fresh)],cwd=td,capture_output=True,text=True)
            assert result.returncode==0,result.stdout+result.stderr
            assert sha(fresh)==sha(recorded),script
        result=subprocess.run([sys.executable,'-B',str(RESEARCH/'theta_effective_remainder/audit_snapshot.py'),
                   *(['--with-arb'] if with_arb else [])],cwd=td,capture_output=True,text=True)
        assert result.returncode==0,result.stdout+result.stderr
        parent= json.loads(result.stdout)
        assert parent['status']=='R25_effective_finite_window_evidence_and_preservation_passed'
        assert parent['Arb_replayed_in_this_run']==with_arb
    plot=read(HERE/'results/plot_data.json');qa=read(HERE/'results/figure_qa.json')
    assert plot['source_sha256']==sha(HERE/'plot_results.py') and plot['certificate_sha256']==sha(cp)
    assert plot['precision_digits']==80 and len(plot['curve_points'])==241
    assert plot['global_theorem'] and not plot['sampled_optimum'] and plot['root_coordinate_is_upper_bound']
    assert F(plot['curve_points'][0]['M'])==M0 and F(plot['curve_points'][-1]['M'])==20
    for row in plot['curve_points']:
        M=F(row['M']);expected=100*published[1]/(c4*M*M)
        assert abs(F(row['relative_error_percent_upper'])-expected)/expected<F('1e-45')
        with localcontext() as context:
            context.prec=70
            x=Decimal(row['M'])/Decimal(4096)/Decimal('0.00000000091787079603827')
            cut=max(Decimal(1),x.ln()/4)
            assert abs(Decimal(row['active_root_coordinate_upper'])-cut)<Decimal('1e-45')
    for name,digest in plot['figures'].items():assert sha(HERE/'figures'/name)==digest
    assert qa['png_sha256']==sha(HERE/'figures/global_fourth_order.png') and qa['panels']==2
    assert qa['no_clipped_text'] and qa['no_overlapping_labels'] and qa['unknown_optimum_not_plotted_as_known']
    proof=(HERE/'PROOF.md').read_text();assert re.findall(r'\\tag\{G(\d+)\}',proof)==list(map(str,range(1,15)))
    for term in ['a_min','discontinuously','No continuity of S','sixth-order coefficient','all M≥M₀']:assert term in proof,term
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))
    for p in HERE.rglob('*'):
        if p.is_file() and p.suffix in ['.md','.py','.json','.txt']:assert all(x>=32 or x in (9,10,13) for x in p.read_bytes()),p.name
        if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
    for p in HERE.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('https://','http://','#')):continue
            q=p.parent/target.split('#')[0]
            if q.name in ['audit_report.json','manifest.json'] and not q.exists():continue
            assert q.exists(),(p.name,target)
    return {'status':'R26_global_remainder_evidence_and_preservation_passed','prior_manifests':26,'prior_frozen_file_entries':n,
       'exact_check_groups':22,'rational_decision_inequalities':22,'parent_R25_evidence_replayed':True,
       'independent_precision_runs':2,'independent_local_inequalities':inequalities,'precision_comparisons':len(differences),
       'minimum_slope_budget':'2e-5','upper_slope_budget':None,'published_remainder_constants':['9.593e-54','1.488e-53'],
       'global_sixth_order_remainder_bound':True,'sixth_order_coefficient_claimed':False,
       'positive_fourth_order_correction_for_all_M_above_onset':True,'onset_claimed_minimal':False,
       'adaptive_finite_prefix':True,'infinite_tail_retained':True,'prefix_continuity_required':False,
       'scientific_figure_panels':2,'figure_curve_points':241,'cusp_curve_uniformity':False,
       'exact_finite_M_optimizer_identified':False,'previous_packages_modified':False,'manuscripts_modified':False,
       'formal_proof':False,'external_referee_review':False,'literature_priority_established':False,
       'public_release_or_submission':False,'audit_source_sha256':sha(__file__),
       'trust_boundary':'Fresh exact/rational replay and optional fresh Arb for R26 and R25; recorded independent numerical corroboration. Hashes and arithmetic checks do not mechanically prove the adaptive-prefix, weighted-tail, support, repair or scalar-feasibility arguments, nor the inherited analytic chain.'}
def main():
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group();g.add_argument('--preflight',action='store_true');g.add_argument('--freeze',action='store_true')
    ap.add_argument('--with-arb',action='store_true');args=ap.parse_args();result=inspect(args.with_arb)
    if args.freeze:
        assert not (HERE/'manifest.json').exists(),'Already frozen.'
        result['closed_utc']=datetime.now(timezone.utc).isoformat();result['Arb_replayed_at_freeze']=args.with_arb
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps({'created_utc':result['closed_utc'],
            'scope':'Fixed-theta fourth-order expansion with a uniform explicit O(M^-6) remainder for all M>=2e-5.',
            'files':files,'audit':result},indent=2)+'\n')
    elif not args.preflight:
        recorded=read(HERE/'audit_report.json')
        for key,value in result.items():assert recorded[key]==value,key
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {row['path'] for row in manifest['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='manifest.json'}
    print(json.dumps({**result,'Arb_replayed_in_this_run':args.with_arb},indent=2))
if __name__=='__main__':main()
