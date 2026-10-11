#!/usr/bin/env python3
"""R27 integrity, arithmetic replay, recorded diagnostics, and frozen closure."""
import sys
sys.dont_write_bytecode=True
import argparse,ast,hashlib,json,re,subprocess,tempfile
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def ends(x):
    m,e=x['mid_man_exp'];r,s=x['rad_man_exp'];c=F(m)*F(2)**e;rad=F(r)*F(2)**s
    return c-rad,c+rad
def inside(x,y):
    lo,hi=ends(x);return lo<=F(y)<=hi
def inspect(with_arb):
    assert __debug__,'Python assertions must be enabled.'
    base=read(HERE/'baseline.json');count=0;assert len(base['manifest_sha256'])==27
    for rel,digest in base['manifest_sha256'].items():
        p=RESEARCH/rel;assert sha(p)==digest,rel
        for row in read(p)['files']:
            assert sha(p.parent/row['path'])==row['sha256'],(rel,row['path']);count+=1
    assert count==base['frozen_entries']==1096
    cp=HERE/'results/certificate.json';ap=HERE/'results/algebra.json';rp=HERE/'results/rational_check.json';dp=HERE/'results/direct_check.json'
    c,a,r,d=map(read,[cp,ap,rp,dp]);assert c['dps']==120
    for name,digest in c['source_sha256'].items():assert sha(HERE/name)==digest
    paths={'R03':'cusp_connection/results/connection_certificate.json','R09_jets':'cusp_shape_design/results/local_jets.json',
      'R15':'kernel_slope_asymptotics/results/asymptotic_certificate.json','R24':'theta_fourth_order/results/certificate.json',
      'R26':'theta_global_remainder/results/certificate.json','R27_algebra':'cusp_uniform_remainder/results/algebra.json'}
    for name,path in paths.items():assert c['input_sha256'][name]==sha(RESEARCH/path)
    assert a['source_sha256']==sha(HERE/'check_algebra.py')
    assert a['R26_algebra_sha256']==sha(RESEARCH/'theta_global_remainder/results/algebra.json')
    assert a['check_groups']==len(a['checks'])==12 and all(x['passed'] for x in a['checks'])
    assert a['inherited_R26_check_groups']==22 and F(a['driver_width'])==F(1,65536)
    assert r['certificate_sha256']==sha(cp) and r['source_sha256']==sha(HERE/'check_bounds.py')
    assert r['rational_helper_sha256']==sha(RESEARCH/'theta_fourth_order/rational_intervals.py')
    assert r['rounding_bits']==512 and r['check_count']==len(r['checks'])==116
    M0=F('2e-5');C4lo=F('2.47e-39');C4hi=F('2.52e-39');pub=[F('1.02e-53'),F('1.64e-53')]
    lo,hi=ends(c['coefficients']['C4']);assert C4lo<lo<hi<C4hi
    lo,hi=map(F,r['C4_interval']);assert C4lo<lo<hi<C4hi
    for name,value in zip(['Kminus','Kplus'],pub):
        assert 0<ends(c['remainder'][name])[1]<value and 0<F(r[name+'_upper'])<value
    assert pub[0]/(C4lo*M0*M0)<F('1.033e-5') and pub[1]/(C4lo*M0*M0)<F('1.660e-5')
    assert pub[1]/M0**6==F('2.5625e-25')
    old=read(RESEARCH/paths['R24'])
    for current,prior in zip(c['dual']['box'],old['dual_box']):
        cl,ch=ends(current);pl,ph=ends(prior);assert cl<pl<ph<ch
    assert len(c['dual']['roots'])==len(c['dual']['tight_roots'])==len(c['remainder']['local'])==28
    assert len(c['dual']['sign_cover'])==len(c['remainder']['sign_cover'])==354
    for key1,key2,container in [('contraction_rows','scaled_forcing',c['dual']),('repair_contraction','repair_forcing',c['remainder'])]:
        for x,y in zip(container[key1],container[key2]):assert ends(x)[1]+ends(y)[1]<1
    assert ends(c['remainder']['tail_gap_residual'])[0]>0
    assert d['source_sha256']==sha(HERE/'crosscheck.py') and d['certificate_sha256']==sha(cp)
    assert d['R24_certificate_sha256']==sha(RESEARCH/paths['R24'])
    assert [(x['dps'],x['cusp_gauss_order_per_quarter'],x['sign_gauss_order_per_cell']) for x in d['runs']]==[(90,64,32),(130,96,48)]
    checks=0;residual_checks=0
    for run in d['runs']:
        assert run['theta_terms']==12 and run['integration_cutoff']=='1' and run['enclosure_checks']==590
        assert len(run['rows'])==5;before=checks
        for row,numerator in zip(run['rows'],[-4,-3,-2,-1,0]):
            assert F(row['nu'])==F(numerator,4*65536)
            assert len(row['cusp'])==len(row['b'])==len(row['v'])==3
            for j in range(3):assert inside(c['arc']['parameter_box'][j],row['cusp'][j]);checks+=1
            assert len(row['roots'])==28
            for root,record in zip(row['roots'],c['dual']['tight_roots']):assert inside(record['root'],root);checks+=1
            assert [x['index'] for x in row['checked_root_jets']]==[0,1,27]
            for jet in row['checked_root_jets']:
                recorded=c['remainder']['local'][jet['index']]['root_jets']['moment_jets']
                assert len(jet['moment_jets'])==4
                for j in range(4):
                    assert len(jet['moment_jets'][j])==6
                    for l in range(6):assert inside(recorded[j][l],jet['moment_jets'][j][l]);checks+=1
            assert len(row['coefficients'])==9
            for key,value in row['coefficients'].items():assert inside(c['coefficients'][key],value);checks+=1
            for j in range(3):
                assert inside(c['dual']['tight_box'][j],row['b'][j]);checks+=1
                assert inside(c['coefficients']['v'][j],row['v'][j]);checks+=1
            for x in row['cusp_residuals']+row['sign_moment_residuals']:assert abs(F(x))<F('1e-60');residual_checks+=1
        assert checks-before==590
    diff=[]
    for low,high in zip(d['runs'][0]['rows'],d['runs'][1]['rows']):
        l=low['cusp']+low['b']+low['v']+list(low['coefficients'].values())
        h=high['cusp']+high['b']+high['v']+list(high['coefficients'].values())
        for x,y in zip(l,h):
            x,y=F(x),F(y);value=abs(x-y)/max(abs(y),F('1e-100'));assert value<F('1e-40');diff.append(value)
    assert checks==1180 and residual_checks==60 and len(diff)==d['precision_comparisons']==90
    assert abs(max(diff)-F(d['maximum_relative_precision_difference']))/max(diff)<F('1e-30')
    with tempfile.TemporaryDirectory(prefix='r27-replay-') as td:
        td=Path(td);jobs=[('check_algebra.py',ap,[]),('check_bounds.py',rp,['--certificate',str(cp)])]
        if with_arb:jobs.append(('certify_uniform.py',cp,[]))
        for script,recorded,extra in jobs:
            fresh=td/recorded.name
            result=subprocess.run([sys.executable,'-B',str(HERE/script),*extra,'--output',str(fresh)],cwd=td,capture_output=True,text=True)
            assert result.returncode==0,result.stdout+result.stderr
            assert sha(fresh)==sha(recorded),script
        result=subprocess.run([sys.executable,'-B',str(RESEARCH/'theta_global_remainder/audit_snapshot.py'),
                    *(['--with-arb'] if with_arb else [])],cwd=td,capture_output=True,text=True)
        assert result.returncode==0,result.stdout+result.stderr
        parent=json.loads(result.stdout);assert parent['status']=='R26_global_remainder_evidence_and_preservation_passed'
        assert parent['Arb_replayed_in_this_run']==with_arb
    plot=read(HERE/'results/plot_data.json');qa=read(HERE/'results/figure_qa.json')
    assert plot['source_sha256']==sha(HERE/'plot_results.py') and plot['certificate_sha256']==sha(cp) and plot['direct_check_sha256']==sha(dp)
    assert plot['band_is_enclosure_not_exact_range'] and plot['trend_is_diagnostic_not_monotonicity_proof']
    assert len(plot['points'])==5 and plot['precision_digits']==80
    base=F(d['runs'][1]['rows'][-1]['coefficients']['C4'])
    for row,source in zip(plot['points'],d['runs'][1]['rows']):
        assert F(row['nu'])==F(source['nu'])
        expected=F(10**6)*(F(source['coefficients']['C4'])/base-1)
        assert abs(F(row['relative_C4_change_ppm'])-expected)<F('1e-40')
        assert abs(F(row['C4'])-F(source['coefficients']['C4']))/F(source['coefficients']['C4'])<F('1e-40')
    for name,digest in plot['figures'].items():assert sha(HERE/'figures'/name)==digest
    assert qa['png_sha256']==sha(HERE/'figures/cusp_uniformity.png') and qa['panels']==2
    assert qa['no_clipped_text'] and qa['no_overlapping_labels'] and qa['proved_band_and_diagnostic_trend_distinguished']
    proof=(HERE/'PROOF.md').read_text();assert re.findall(r'\\tag\{U(\d+)\}',proof)==list(map(str,range(1,13)))
    for term in ['separate','negative','monotonicity','whole infinite tail','Arzelà']:assert term in proof,term
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
    return {'status':'R27_uniform_cusp_subarc_evidence_and_preservation_passed','prior_manifests':27,'prior_frozen_file_entries':count,
      'new_exact_check_groups':12,'rational_decision_inequalities':116,'parent_R26_and_R25_evidence_replayed':True,
      'independent_enclosure_checks':checks,'recorded_small_residual_checks':residual_checks,'precision_comparisons':90,
      'driver_interval':['-1/65536','0'],'minimum_slope_budget':'2e-5','upper_slope_budget':None,
      'uniform_positive_C4_bounds':['2.47e-39','2.52e-39'],'uniform_remainder_constants':['1.02e-53','1.64e-53'],
      'moving_dual_localization':True,'uniform_all_large_M_remainder_on_subarc':True,
      'whole_original_arc_covered':False,'one_shared_design_for_all_cusps':False,'C4_monotonicity_proved':False,
      'sixth_order_coefficient_claimed':False,'modified_kernel_geometric_nondegeneracy_checked_uniformly':False,
      'scientific_figure_panels':2,'previous_packages_modified':False,'manuscripts_modified':False,
      'formal_proof':False,'external_referee_review':False,'literature_priority_established':False,'public_release_or_submission':False,
      'audit_source_sha256':sha(__file__),
      'trust_boundary':'Evidence integrity, fresh exact/rational replay and optional Arb reproduction, plus recorded direct-integral diagnostics. The analytic cusp transport, dual localization, root tails, support and scalar arguments are not mechanically proved by this audit.'}
def main():
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group();g.add_argument('--preflight',action='store_true');g.add_argument('--freeze',action='store_true')
    ap.add_argument('--with-arb',action='store_true');args=ap.parse_args();result=inspect(args.with_arb)
    if args.freeze:
        assert not (HERE/'manifest.json').exists(),'Already frozen.'
        result['closed_utc']=datetime.now(timezone.utc).isoformat();result['Arb_replayed_at_freeze']=args.with_arb
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps({'created_utc':result['closed_utc'],
          'scope':'Uniform positive fourth coefficient and explicit all-large-M remainder on the short exact cusp arc [-2^-16,0].',
          'files':files,'audit':result},indent=2)+'\n')
    elif not args.preflight:
        recorded=read(HERE/'audit_report.json')
        for key,value in result.items():assert recorded[key]==value,key
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {row['path'] for row in manifest['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='manifest.json'}
    print(json.dumps({**result,'Arb_replayed_in_this_run':args.with_arb},indent=2))
if __name__=='__main__':main()
