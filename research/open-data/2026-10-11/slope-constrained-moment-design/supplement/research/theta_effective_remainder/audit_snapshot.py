#!/usr/bin/env python3
"""R25 evidence audit, exact replay, optional fresh Arb reproduction and freezing."""
import sys
sys.dont_write_bytecode=True
import argparse,ast,hashlib,json,re,subprocess,tempfile
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def ends(v):
    m,e=v['mid_man_exp'];r,s=v['rad_man_exp'];c=F(m)*F(2)**e;rr=F(r)*F(2)**s;return c-rr,c+rr
def inside(v,x):
    a,b=ends(v);return a<=F(x)<=b
def inspect(with_arb):
    assert __debug__,'Assertions must be enabled.'
    baseline=read(HERE/'baseline.json');n=0
    assert len(baseline['manifest_sha256'])==25
    for rel,digest in baseline['manifest_sha256'].items():
        p=RESEARCH/rel;assert sha(p)==digest,rel
        for row in read(p)['files']:
            assert sha(p.parent/row['path'])==row['sha256'],(rel,row['path']);n+=1
    assert n==baseline['frozen_entries']==1043
    cp=HERE/'results/certificate.json';ap=HERE/'results/algebra.json';rp=HERE/'results/rational_check.json'
    cert,alg,rat,direct=read(cp),read(ap),read(rp),read(HERE/'results/direct_check.json')
    assert cert['dps']==120 and len(cert['local'])==28 and len(cert['sign_cover'])==354
    for name,digest in cert['source_sha256'].items():assert sha(HERE/name)==digest
    assert cert['R24_certificate_sha256']==sha(RESEARCH/'theta_fourth_order/results/certificate.json')
    assert alg['source_sha256']==sha(HERE/'check_algebra.py') and alg['helper_sha256']==sha(RESEARCH/'finite_slope_fourth_order/check_fourth_order.py')
    assert alg['check_groups']==len(alg['checks'])==15 and all(x['passed'] for x in alg['checks'])
    assert rat['certificate_sha256']==sha(cp) and rat['source_sha256']==sha(HERE/'check_bounds.py')
    assert rat['rational_helper_sha256']==sha(RESEARCH/'theta_fourth_order/rational_intervals.py')
    assert rat['rounding_bits']==512 and rat['check_count']==len(rat['checks'])==74
    published=[F('9.593e-54'),F('1.488e-53')]
    assert list(map(F,rat['published_constants']))==published
    for key,val in zip(['Kminus','Kplus'],published):
        assert 0<ends(cert['result'][key])[1]<val
        assert 0<F(rat[key+'_upper'])<val
    for x,y in zip(cert['repair_contraction'],cert['repair_forcing']):assert ends(x)[1]+ends(y)[1]<1
    assert [ends(x) for x in cert['budget_interval']]==[(F('2e-5'),F('2e-5')),(F('2e-3'),F('2e-3'))] or all(inside(x,y) for x,y in zip(cert['budget_interval'],['2e-5','2e-3']))
    assert direct['certificate_sha256']==sha(cp) and direct['source_sha256']==sha(HERE/'crosscheck.py')
    assert [(r['dps'],r['quadrature_order']) for r in direct['runs']]==[(80,20),(110,28)]
    jets=0;inequalities=0;comparisons=0
    for run in direct['runs']:
        assert run['theta_terms']==12 and len(run['rows'])==28
        assert run['jet_comparisons']==812 and run['local_remainder_inequalities']==420
        for nr,cr in zip(run['rows'],cert['local']):
            assert inside(cr['root'],nr['root']) and inside(cr['kappa'],nr['kappa'])
            for j in range(4):
                for l in range(6):assert inside(cr['root_jets']['moment_jets'][j][l],nr['moment_jets'][j][l]);jets+=1
            for l in range(1,6):assert inside(cr['root_jets']['residual_jets'][l],nr['residual_jets'][l]);jets+=1
            assert len(nr['samples'])==3
            for sample,exp in zip(nr['samples'],[14,18,22]):
                assert F(sample['half_width'])==F(2)**-exp
                for j in range(3):assert abs(F(sample['scaled_moment_remainders'][j]))<ends(cr['moment_fourth_bound'][j])[1];inequalities+=1
                assert abs(F(sample['scaled_residual_remainder']))<ends(cr['residual_sixth_bound'])[1];inequalities+=1
                assert abs(F(sample['scaled_balance_defect']))<ends(cr['balance_fourth_bound'])[1];inequalities+=1
    for lo,hi in zip(direct['runs'][0]['rows'],direct['runs'][1]['rows']):
        for l,h in zip(lo['samples'],hi['samples']):
            lv=l['scaled_moment_remainders']+[l['scaled_residual_remainder'],l['scaled_balance_defect']]
            hv=h['scaled_moment_remainders']+[h['scaled_residual_remainder'],h['scaled_balance_defect']]
            for x,y in zip(lv,hv):
                x,y=F(x),F(y);assert abs(x-y)/max(abs(y),F('1e-100'))<F('1e-40');comparisons+=1
    assert jets==1624 and inequalities==840 and comparisons==direct['precision_comparisons']==420
    assert F(direct['max_relative_precision_difference'])<F('1e-40')
    with tempfile.TemporaryDirectory(prefix='r25-replay-') as td:
        td=Path(td);jobs=[('check_algebra.py',ap,[]),('check_bounds.py',rp,['--certificate',str(cp)])]
        if with_arb:jobs.append(('certify_remainder.py',cp,[]))
        for script,recorded,extra in jobs:
            fresh=td/recorded.name
            r=subprocess.run([sys.executable,'-B',str(HERE/script),*extra,'--output',str(fresh)],cwd=td,capture_output=True,text=True)
            assert r.returncode==0,r.stdout+r.stderr
            assert sha(fresh)==sha(recorded),script
    plot=read(HERE/'results/plot_data.json');qa=read(HERE/'results/figure_qa.json')
    assert plot['source_sha256']==sha(HERE/'plot_results.py') and plot['certificate_sha256']==sha(cp)
    assert len(plot['bound_curves'])==201 and plot['precision_digits']==80 and plot['finite_window_only'] and plot['not_sampled_optimum_values']
    for row in plot['bound_curves']:
        M=F(row['M']);c4=F('2.49203004e-39')
        expected={'ratio_deviation_lower_ppm':-10**6*published[0]/(c4*M*M),
                  'ratio_deviation_upper_ppm':10**6*published[1]/(c4*M*M),
                  'absolute_error_upper':published[1]/M**6,'fourth_term_lower':c4/M**4}
        for key,value in expected.items():assert abs(F(row[key])-value)/abs(value)<F('1e-45')
    for name,digest in plot['figures'].items():assert sha(HERE/'figures'/name)==digest
    assert qa['png_sha256']==sha(HERE/'figures/effective_fourth_order.png') and qa['panels']==2
    assert qa['no_clipped_text'] and qa['no_overlapping_labels'] and qa['unknown_optimum_not_plotted_as_known']
    proof=(HERE/'PROOF.md').read_text();assert re.findall(r'\\tag\{E(\d+)\}',proof)==list(map(str,range(1,16)))
    for term in ['finite-window','a_min','Arzelà','not'] :assert term in proof
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
    return {'status':'R25_effective_finite_window_evidence_and_preservation_passed','prior_manifests':25,'prior_frozen_file_entries':n,
       'exact_check_groups':15,'rational_inequalities_checked':74,'finite_root_neighborhoods':28,'finite_sign_leaves':354,
       'independent_precision_runs':2,'independent_jet_comparisons':jets,'independent_local_remainder_inequalities':inequalities,
       'precision_comparisons':comparisons,'budget_interval':['2e-5','2e-3'],'published_remainder_constants':['9.593e-54','1.488e-53'],
       'effective_fourth_order_remainder_on_finite_window':True,'leading_approximation_underestimates_on_window':True,
       'whole_integral_tail_included':True,'exact_moment_repair_proved_by_contraction':True,'scientific_figure_panels':2,
       'all_large_M_sixth_order_remainder':False,'sixth_order_coefficient_claimed':False,'global_numerical_asymptotic_onset':False,
       'cusp_curve_uniformity':False,'exact_finite_M_optimizer_identified':False,'previous_packages_modified':False,
       'manuscripts_modified':False,'formal_proof':False,'external_referee_review':False,'literature_priority_established':False,
       'public_release_or_submission':False,'audit_source_sha256':sha(__file__),
       'trust_boundary':'Fresh exact/rational replay and optionally Arb; recorded independent local numerical checks. The analytic support, contraction, Taylor and tail arguments and inherited Q/b* localization require mathematical review and are not mechanically proved by this script.'}
def main():
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group();g.add_argument('--preflight',action='store_true');g.add_argument('--freeze',action='store_true')
    ap.add_argument('--with-arb',action='store_true');a=ap.parse_args();result=inspect(a.with_arb)
    if a.freeze:
        assert not (HERE/'manifest.json').exists(),'Already frozen.'
        result['closed_utc']=datetime.now(timezone.utc).isoformat();result['Arb_replayed_at_freeze']=a.with_arb
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps({'created_utc':result['closed_utc'],
          'scope':'Finite-window fourth-order error theorem, validated bounds and explicit certification terminology.',
          'files':files,'audit':result},indent=2)+'\n')
    elif not a.preflight:
        recorded=read(HERE/'audit_report.json')
        for key,val in result.items():assert recorded[key]==val,key
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {row['path'] for row in manifest['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='manifest.json'}
    print(json.dumps({**result,'Arb_replayed_in_this_run':a.with_arb},indent=2))
if __name__=='__main__':main()
