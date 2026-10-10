#!/usr/bin/env python3
"""R28 provenance, arithmetic replay, finite differences and frozen closure."""
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
    a,b=ends(x);return a<=F(y)<=b
def overlap(x,y):
    a,b=ends(x);c,d=ends(y);return a<=d and c<=b
def inspect(with_arb):
    assert __debug__,'Keep assertions enabled.'
    base=read(HERE/'baseline.json');count=0;assert len(base['manifest_sha256'])==28
    for rel,digest in base['manifest_sha256'].items():
        p=RESEARCH/rel;assert sha(p)==digest,rel
        for row in read(p)['files']:
            assert sha(p.parent/row['path'])==row['sha256'],(rel,row['path']);count+=1
    assert count==base['frozen_entries']==1130
    paths={k:HERE/'results'/v for k,v in {'cert':'certificate.json','algebra':'algebra.json','rational':'rational_check.json','direct':'direct_check.json','moment':'sign_moment9.json'}.items()}
    c,a,r,d,m=[read(paths[k]) for k in ['cert','algebra','rational','direct','moment']]
    assert c['dps']==120 and c['driver_interval']==['-1/65536','0']
    assert c['published_derivative_bounds']==['2.82e-40','4.35e-40']
    assert c['published_anchored_coefficient_bounds']==['2.49202340e-39','2.49203006e-39']
    parents={'R27':RESEARCH/'cusp_uniform_remainder/results/certificate.json','R12':RESEARCH/'kernel_norm_threshold/results/threshold_certificate.json',
      'moment9':paths['moment'],'algebra':paths['algebra']}
    for name,p in parents.items():assert c['input_sha256'][name]==sha(p),name
    for name,digest in c['source_sha256'].items():assert sha(HERE/name)==digest,name
    assert a['source_sha256']==sha(HERE/'check_algebra.py') and a['check_groups']==len(a['checks'])==26
    assert all(x['passed'] for x in a['checks'])
    assert a['symbolic_helper_sha256']==sha(RESEARCH/'finite_slope_fourth_order/check_fourth_order.py')
    assert a['R26_algebra_sha256']==sha(RESEARCH/'theta_global_remainder/results/algebra.json')
    assert r['source_sha256']==sha(HERE/'check_bounds.py') and r['rounding_bits']==512
    assert r['certificate_sha256']==sha(paths['cert']) and r['R27_certificate_sha256']==sha(parents['R27'])
    assert r['rational_helper_sha256']==sha(RESEARCH/'theta_fourth_order/rational_intervals.py')
    assert r['check_count']==len(r['checks'])==44
    lo,hi=ends(c['derivatives']['C4']);slo,shi=F('2.82e-40'),F('4.35e-40');assert slo<lo<hi<shi
    lo,hi=map(F,r['C4_prime_interval']);assert slo<lo<hi<shi
    endpoint=read(RESEARCH/'theta_fourth_order/results/certificate.json')['coefficients']['C4']
    lo,hi=ends(endpoint);Clo,Chi=F('2.49203004e-39'),F('2.49203006e-39');assert Clo<lo<hi<Chi
    h=F(1,65536);assert F('2.49202340e-39')<Clo-h*shi
    assert list(map(F,a['endpoint_gain_interval']))==[h*slo,h*shi]
    for key,p in {'R12':parents['R12'],'Q':RESEARCH/'cusp_verified/results/quartic_cusp_certificate.json','R09':RESEARCH/'cusp_shape_design/results/local_jets.json'}.items():
        assert m['input_sha256'][key]==sha(p),key
    for rel,digest in m['source_sha256'].items():assert sha(HERE/rel)==digest,rel
    assert m['dps']==120 and m['order']==9 and m['theta_terms']==8 and m['cutoff']==1
    assert len(m['segments'])==29 and [x['sign'] for x in m['segments']]==[(-1)**i for i in range(29)]
    intervals=[(ends(row['left']),ends(row['right'])) for row in m['segments']]
    assert all(l[0]==l[1] and rr[0]==rr[1] and l[0]<rr[0] for l,rr in intervals)
    assert intervals[0][0][0]==0 and intervals[-1][1][0]==1
    assert all(x[1]==y[0] for x,y in zip(intervals,intervals[1:]))
    assert len(c['root_derivatives'])==28 and len(c['sign_transport'])==10
    assert len(c['b_prime'])==3 and all(max(map(abs,ends(x)))<10 for x in c['b_prime'])
    parent=read(parents['R27'])
    for row,previous in zip(c['root_derivatives'],parent['dual']['tight_roots']):
        assert row['index']==previous['index'] and row['orientation']==previous['orientation']
        assert overlap(row['root'],previous['root'])
        at=row['jets'];assert at['at_true_root'] and len(at['moment_jets_extended'])==10
        assert all(len(q)==5 for q in at['moment_jets_extended'])
        assert inside(row['total_residual_derivatives'][0],0)
    assert ends(c['dual_derivative_solve']['eta'])[1]<1
    assert d['source_sha256']==sha(HERE/'crosscheck.py')
    for key,p in {'certificate':paths['cert'],'previous_direct':RESEARCH/'cusp_uniform_remainder/results/direct_check.json','moment9':paths['moment']}.items():
        assert d['input_sha256'][key]==sha(p)
    assert [(x['dps'],x['cusp_gauss_order_per_quarter'],x['sign_gauss_order_per_cell']) for x in d['runs']]==[(80,64,32),(110,80,40)]
    comparisons=0;residuals=0;differences=[];step_checks=0
    for run in d['runs']:
        assert run['theta_terms']==12 and run['cutoff']==1 and len(run['evaluations'])==13
        assert run['comparison_count']==73 and len(run['rows'])==3
        values={F(x['nu']):x for x in run['evaluations']};assert len(values)==13
        for nu,ev in values.items():
            assert -h<=nu<=0 and len(ev['coefficients'])==9 and len(ev['b'])==len(ev['cusp'])==3
            for name in ['maximum_cusp_residual','maximum_sign_residual']:
                assert abs(F(ev[name]))<F('1e-55');residuals+=1
        for row,nu in zip(run['rows'],[-h,-h/2,F(0)]):
            assert F(row['nu'])==nu and len(row['steps'])==2
            for record,denom in zip(row['steps'],[16,32]):
                step=h/denom;assert F(record['step'])==step
                if nu==-h:offsets=[0,step,2*step];weights=[-3,4,-1];mode='forward_second_order'
                elif nu==0:offsets=[0,-step,-2*step];weights=[3,-4,1];mode='backward_second_order'
                else:offsets=[-step,step];weights=[-1,1];mode='central_second_order'
                assert record['stencil']==mode
                for key,value in record['derivatives'].items():
                    calc=sum(F(w)*F(values[nu+offset]['coefficients'][key]) for offset,w in zip(offsets,weights))/(2*step)
                    val=F(value);assert abs(calc-val)/max(abs(val),F('1e-100'))<F('1e-55')
                    assert inside(c['derivatives'][key],val);comparisons+=1
                for j,value in enumerate(record['b_derivative']):
                    calc=sum(F(w)*F(values[nu+offset]['b'][j]) for offset,w in zip(offsets,weights))/(2*step)
                    val=F(value);assert abs(calc-val)/max(abs(val),F('1e-100'))<F('1e-55')
                    assert inside(c['b_prime'][j],val);comparisons+=1
            x,y=[F(s['derivatives']['C4']) for s in row['steps']];rel=abs(x-y)/abs(y)
            assert rel<F('5e-15') and abs(rel-F(row['relative_C4_step_change']))/rel<F('1e-30');step_checks+=1
        assert inside(m['moment_at_exact_Q'],run['ninth_template_moment']);comparisons+=1
    for lrun,hrun in zip(d['runs'][0]['rows'],d['runs'][1]['rows']):
        for l,hrow in zip(lrun['steps'],hrun['steps']):
            lv=list(l['derivatives'].values())+l['b_derivative'];hv=list(hrow['derivatives'].values())+hrow['b_derivative']
            for x,y in zip(lv,hv):
                x,y=F(x),F(y);rel=abs(x-y)/max(abs(y),F('1e-100'));assert rel<F('1e-35');differences.append(rel)
    assert comparisons==146 and residuals==52 and step_checks==6
    assert len(differences)==d['precision_comparisons']==72
    worst=max(differences);assert abs(worst-F(d['maximum_relative_precision_difference']))/worst<F('1e-30')
    plot=read(HERE/'results/plot_data.json');qa=read(HERE/'results/figure_qa.json')
    assert plot['source_sha256']==sha(HERE/'plot_results.py') and plot['certificate_sha256']==sha(paths['cert']) and plot['direct_check_sha256']==sha(paths['direct'])
    assert plot['green_regions_are_uniform_bounds'] and plot['orange_points_are_diagnostics'] and not plot['finite_M_optimum_monotonicity_claimed']
    grid=list(map(F,plot['cone_grid']));assert len(grid)==201 and grid[0]==-h and grid[-1]==0
    for nu,l,u in zip(grid,plot['cone_lower_ppm'],plot['cone_upper_ppm']):
        assert F(l)==10**6*nu*shi/Clo and F(u)==10**6*nu*slo/Chi
    high={F(x['nu']):x for x in d['runs'][1]['evaluations']};C0=F(high[F(0)]['coefficients']['C4'])
    assert len(plot['samples'])==13 and len(plot['derivative_diagnostics'])==3
    for sample in plot['samples']:
        val=F(high[F(sample['nu'])]['coefficients']['C4']);assert F(sample['C4'])==val
        expected=10**6*(val/C0-1);assert abs(F(sample['relative_change_ppm'])-expected)<F('1e-60')
    for sample,row in zip(plot['derivative_diagnostics'],d['runs'][1]['rows']):
        assert F(sample['nu'])==F(row['nu']) and F(sample['C4_prime_finite_difference'])==F(row['steps'][1]['derivatives']['C4'])
    for rel,digest in plot['figures'].items():assert sha(HERE/'figures'/rel)==digest
    assert qa['png_sha256']==sha(HERE/'figures/coefficient_motion.png') and qa['panels']==2
    assert qa['no_clipped_text'] and qa['no_overlapping_labels'] and qa['proved_bounds_and_diagnostic_points_distinguished']
    probe=read(HERE/'diagnostics/first_derivative_probe.json')
    assert probe['status']=='positive_derivative_enclosed' and probe['motion_source_sha256']==sha(HERE/'motion.py')
    with tempfile.TemporaryDirectory(prefix='r28-replay-') as td:
        td=Path(td);jobs=[('check_algebra.py',paths['algebra'],[]),('check_bounds.py',paths['rational'],['--certificate',str(paths['cert'])])]
        if with_arb:jobs += [('sign_moment.py',paths['moment'],[]),('certify_motion.py',paths['cert'],[])]
        for script,recorded,extra in jobs:
            output=td/recorded.name
            result=subprocess.run([sys.executable,'-B',str(HERE/script),*extra,'--output',str(output)],cwd=td,capture_output=True,text=True)
            assert result.returncode==0,result.stdout+result.stderr
            assert sha(output)==sha(recorded),script
        result=subprocess.run([sys.executable,'-B',str(RESEARCH/'cusp_uniform_remainder/audit_snapshot.py'),*(['--with-arb'] if with_arb else [])],cwd=td,capture_output=True,text=True)
        assert result.returncode==0,result.stdout+result.stderr
        previous=json.loads(result.stdout);assert previous['status']=='R27_uniform_cusp_subarc_evidence_and_preservation_passed'
        assert previous['Arb_replayed_in_this_run']==with_arb
    proof=(HERE/'PROOF.md').read_text();assert re.findall(r'\\tag\{V(\d+)\}',proof)==list(map(str,range(1,13)))
    for term in ['one-sided','no circular','uniformly summable','not claim','original driver ν']:assert term in proof,term
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))
    for p in HERE.rglob('*'):
        if p.is_file() and p.suffix in ['.py','.md','.json','.txt']:assert all(x>=32 or x in [9,10,13] for x in p.read_bytes()),p
        if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
    for p in HERE.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('https://','http://','#')):continue
            q=p.parent/target.split('#')[0]
            if q.name in ['audit_report.json','manifest.json'] and not q.exists():continue
            assert q.exists(),(p,target)
    return {'status':'R28_coefficient_motion_evidence_and_preservation_passed','prior_manifests':28,'prior_frozen_file_entries':count,
      'exact_check_groups':26,'rational_AD_decisions':44,'diagnostic_integral_solves':26,'diagnostic_comparisons':comparisons,
      'recorded_residual_checks':residuals,'two_step_comparisons':step_checks,'precision_comparisons':len(differences),
      'published_C4_prime_bounds':['2.82e-40','4.35e-40'],'driver_interval':['-1/65536','0'],
      'strict_increase_of_C4_on_this_arc':True,'uniform_finite_M_optimum_monotonicity':False,
      'whole_original_arc_covered':False,'C4_convexity_claimed':False,'new_sixth_coefficient':False,
      'previous_packages_modified':False,'manuscripts_modified':False,'external_referee_review':False,
      'formal_proof':False,'literature_priority_established':False,'public_release_or_submission':False,
      'audit_source_sha256':sha(__file__),
      'trust_boundary':'Provenance, fresh exact and rational AD replay, recorded independent finite differences and optional Arb reproduction. Analytic implicit differentiation, moving boundaries and infinite-series differentiation are not mechanically proved by this audit.'}
def main():
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group();g.add_argument('--preflight',action='store_true');g.add_argument('--freeze',action='store_true')
    ap.add_argument('--with-arb',action='store_true');args=ap.parse_args();result=inspect(args.with_arb)
    if args.freeze:
        assert not (HERE/'manifest.json').exists(),'Already frozen.'
        result['closed_utc']=datetime.now(timezone.utc).isoformat();result['Arb_replayed_at_freeze']=args.with_arb
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps({'created_utc':result['closed_utc'],'scope':'Strict increase and quantified derivative of exact C4 along nu in [-2^-16,0].','files':files,'audit':result},indent=2)+'\n')
    elif not args.preflight:
        recorded=read(HERE/'audit_report.json')
        for key,value in result.items():assert recorded[key]==value,key
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {r['path'] for r in manifest['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='manifest.json'}
    print(json.dumps({**result,'Arb_replayed_in_this_run':args.with_arb},indent=2))
if __name__=='__main__':main()
