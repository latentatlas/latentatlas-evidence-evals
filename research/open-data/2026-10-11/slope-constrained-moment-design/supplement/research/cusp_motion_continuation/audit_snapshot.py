#!/usr/bin/env python3
"""R29 frozen evidence, arithmetic replay and optional fresh Arb reconstruction."""
import sys
sys.dont_write_bytecode=True
import argparse,ast,gzip,hashlib,json,re,subprocess,tempfile
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def ends(x):
    m,e=x['mid_man_exp'];r,s=x['rad_man_exp'];v=F(m)*F(2)**e;d=F(r)*F(2)**s;return v-d,v+d
def inside(x,y):
    lo,hi=ends(x);return lo<=F(y)<=hi
def exact(x):
    a,b=ends(x);assert a==b;return a
def inspect(with_arb):
    assert __debug__,'Keep assertions enabled.'
    base=read(HERE/'baseline.json');assert len(base['manifest_sha256'])==29;count=0
    for rel,digest in base['manifest_sha256'].items():
        p=RESEARCH/rel;assert sha(p)==digest,rel
        for row in read(p)['files']:
            assert sha(p.parent/row['path'])==row['sha256'],(rel,row['path']);count+=1
    assert count==base['frozen_entries']==1162
    cover=HERE/'results/cover';cp=cover/'certificate.json';c=read(cp)
    assert c['status']=='R29_recentered_positive_derivative_cover' and c['dps']==120
    assert c['driver_interval']==['-1/64','0'] and c['half_width']=='1/4096' and c['cell_count']==32
    assert c['published_derivative_bounds']==['1.9e-40','5.3e-40']
    assert c['published_coefficient_bounds']==['2.48374879e-39','2.49203006e-39']
    for name,digest in c['source_sha256'].items():assert sha(HERE/name)==digest,name
    parents={'R03':RESEARCH/'cusp_connection/results/connection_certificate.json','R09':RESEARCH/'cusp_shape_design/results/local_jets.json',
      'R24':RESEARCH/'theta_fourth_order/results/certificate.json','R26_algebra':RESEARCH/'theta_global_remainder/results/algebra.json',
      'R28':RESEARCH/'cusp_coefficient_motion/results/certificate.json'}
    for key,p in parents.items():assert c['input_sha256'][key]==sha(p),key
    L=F(1,64);h=F(1,4096);slo,shi=map(F,c['published_derivative_bounds']);cells=[]
    for i,row in enumerate(c['cells']):
        assert row['index']==i and F(row['left'])==-(i+1)/F(2048) and F(row['right'])==-i/F(2048)
        p=cover/row['file'];assert sha(p)==row['sha256'];record=json.loads(gzip.decompress(p.read_bytes()));cells.append(record)
        assert record['index']==i;a=record['anchor'];cell=record['cell'];m=record['motion'];arc=cell['arc'];dual=cell['dual']
        assert exact(a['nu'])==-(2*i+1)*h and exact(arc['driver_half_width'])==h
        assert exact(arc['driver_left'])==F(row['left']) and exact(arc['driver_right'])==F(row['right'])
        assert row['C4_prime']==m['derivatives']['C4'] and row['C4']==cell['coefficients']['C4']
        low,high=ends(row['C4_prime']);assert slo<low<high<shi
        assert len(a['central_derivatives'])==40 and len(a['B'])==59 and len(a['knots'])==28
        assert len(a['template_quadrature']['segments'])==29 and len(a['template_moments'])==10
        seg=a['template_quadrature']['segments'];assert exact(seg[0]['left'])==0 and exact(seg[-1]['right'])==1
        for k,s in enumerate(seg):
            assert s['sign']==(-1)**k and len(s['finite_integrals'])==10 and exact(s['left'])<exact(s['right'])
            if k:assert exact(seg[k-1]['right'])==exact(s['left'])
        assert ends(a['cusp_validation']['q_plus_eta'])[1]<1
        assert len(dual['roots'])==len(dual['tight_roots'])==len(m['root_derivatives'])==28
        assert len(dual['sign_cover'])==row['sign_cover_leaves']==354
        for j in range(3):
            assert ends(dual['contraction_rows'][j])[1]+ends(dual['scaled_forcing'][j])[1]<1
            assert max(map(abs,ends(m['b_prime'][j])))<10
            assert max(map(abs,ends(arc['refined_velocity'][j])))<1
        assert ends(arc['refined_velocity'][1])[0]>0 and ends(arc['refined_velocity'][2])[0]>0
        assert ends(arc['derivatives'][3])[0]>0 and ends(arc['derivatives'][4])[1]<0 and ends(arc['derivatives'][6])[1]<0
        for j,(lo,hi) in enumerate([(41,42),(-4,0),(0,9)]):
            a0,b0=ends(arc['parameter_box'][j]);assert lo<a0<b0<hi
        for j,lim in enumerate([F(1,1000),F(1,10),F(1,200)]):assert max(map(abs,ends(dual['box'][j])))<lim
        det=ends(cell['coefficients']['first_three_switch_determinant']);assert det[0]*det[1]>0
        # Check that root brackets plus the sign leaves really cover [0,1]
        # with no gaps. Each individual sign assertion is also rationally replayed.
        segments=[(ends(x['lo'])[0],ends(x['hi'])[1]) for x in dual['sign_cover']]
        segments += [ends(x['coarse']) for x in dual['roots']];segments.sort()
        assert segments[0][0]==0 and segments[-1][1]==1
        assert all(a0<b0 for a0,b0 in segments)
        assert all(a0[1]>=b0[0] for a0,b0 in zip(segments,segments[1:]))
        for rr in m['root_derivatives']:assert inside(rr['total_residual_derivatives'][0],0)
    assert len(cells)==32 and len(list(cover.glob('*.json.gz')))==32
    alg=read(HERE/'results/algebra.json');rat=read(HERE/'results/rational_check.json');direct=read(HERE/'results/direct_check.json')
    assert alg['source_sha256']==sha(HERE/'check_algebra.py') and alg['check_count']==len(alg['checks'])==14
    assert all(x['passed'] for x in alg['checks']) and alg['enlargement_factor']==1024
    assert alg['R28_derivative_algebra_sha256']==sha(RESEARCH/'cusp_coefficient_motion/results/algebra.json')
    assert rat['source_sha256']==sha(HERE/'check_bounds.py') and rat['certificate_sha256']==sha(cp)
    assert rat['rational_helper_sha256']==sha(RESEARCH/'theta_fourth_order/rational_intervals.py')
    assert rat['rounding_bits']==512 and rat['check_count']==17088 and len(rat['cells'])==32
    for i,r in enumerate(rat['cells']):
        assert r['index']==i and r['file_sha256']==c['cells'][i]['sha256']
        assert r['continuation']['check_count']==len(r['continuation']['checks'])==490
        assert r['derivative_AD']['check_count']==len(r['derivative_AD']['checks'])==44
        lo,hi=map(F,r['derivative_AD']['C4_prime_interval']);assert slo<lo<hi<shi
    assert direct['source_sha256']==sha(HERE/'crosscheck.py') and direct['input_sha256']['cover_certificate']==sha(cp)
    assert direct['input_sha256']['previous_direct']==sha(RESEARCH/'cusp_uniform_remainder/results/direct_check.json')
    assert [(r['dps'],r['cusp_gauss_order_per_quarter'],r['sign_gauss_order_per_cell']) for r in direct['runs']]==[(80,64,32),(110,80,40)]
    band=direct['derivative_comparison_bands']
    for name,bb in band['derivatives'].items():
        union=(min(ends(z['motion']['derivatives'][name])[0] for z in cells),max(ends(z['motion']['derivatives'][name])[1] for z in cells));assert ends(bb)==union
    for j,bb in enumerate(band['b_prime']):assert ends(bb)==(min(ends(z['motion']['b_prime'][j])[0] for z in cells),max(ends(z['motion']['b_prime'][j])[1] for z in cells))
    comparisons=0;residuals=0;values_compared=0;step_checks=0
    for run in direct['runs']:
        assert run['theta_terms']==12 and run['cutoff']==1 and len(run['evaluations'])==23 and len(run['rows'])==5
        ev={F(x['nu']):x for x in run['evaluations']};assert len(ev)==23
        for nu,e in ev.items():
            assert -L<=nu<=0;target=cells[min(int(-nu*2048),31)]['cell']
            for name in ['maximum_cusp_residual','maximum_sign_residual']:assert abs(F(e[name]))<F('1e-55');residuals+=1
            for name,value in e['coefficients'].items():assert inside(target['coefficients'][name],value),(name,nu);values_compared+=1
            for j in range(3):
                assert inside(target['dual']['tight_box'][j],e['b'][j]);values_compared+=1
                assert inside(target['arc']['parameter_box'][j],e['cusp'][j]);values_compared+=1
        for index,row in enumerate(run['rows']):
            nu=-L+index*L/4;assert F(row['nu'])==nu and len(row['steps'])==2
            for denom,step in zip([1024,2048],row['steps']):
                e=L/denom;assert F(step['step'])==e
                if index==0:offsets=[0,e,2*e];weights=[-3,4,-1];stencil='forward_second_order'
                elif index==4:offsets=[0,-e,-2*e];weights=[3,-4,1];stencil='backward_second_order'
                else:offsets=[-e,e];weights=[-1,1];stencil='central_second_order'
                assert step['stencil']==stencil
                for name,value in step['derivatives'].items():
                    v=F(value);calc=sum(F(w)*F(ev[nu+off]['coefficients'][name]) for off,w in zip(offsets,weights))/(2*e)
                    assert abs(calc-v)/max(abs(v),F('1e-100'))<F('1e-55') and inside(band['derivatives'][name],v);comparisons+=1
                for j,value in enumerate(step['b_derivative']):
                    v=F(value);calc=sum(F(w)*F(ev[nu+off]['b'][j]) for off,w in zip(offsets,weights))/(2*e)
                    assert abs(calc-v)/max(abs(v),F('1e-100'))<F('1e-55') and inside(band['b_prime'][j],v);comparisons+=1
            x,y=[F(s['derivatives']['C4']) for s in row['steps']];change=abs(x-y)/abs(y)
            assert change<F('1.25e-12') and abs(change-F(row['relative_C4_step_change']))/change<F('1e-30');step_checks+=1
        assert run['comparison_count']==120
    assert comparisons==240 and residuals==92 and values_compared==690 and step_checks==10
    dif=[]
    for lr,hr in zip(direct['runs'][0]['rows'],direct['runs'][1]['rows']):
        for l,r in zip(lr['steps'],hr['steps']):
            for x,y in zip(list(l['derivatives'].values())+l['b_derivative'],list(r['derivatives'].values())+r['b_derivative']):
                x,y=F(x),F(y);v=abs(x-y)/max(abs(y),F('1e-100'));assert v<F('1e-35');dif.append(v)
    assert len(dif)==direct['precision_comparisons']==120
    assert abs(max(dif)-F(direct['maximum_relative_precision_difference']))/max(dif)<F('1e-30')
    return finish(cells,c,alg,rat,direct,count,with_arb,comparisons,residuals,values_compared,step_checks)

def finish(cells,c,alg,rat,direct,count,with_arb,comparisons,residuals,values_compared,step_checks):
    cover=HERE/'results/cover';cp=cover/'certificate.json';L=F(1,64);slo,shi=map(F,c['published_derivative_bounds'])
    p=read(HERE/'diagnostics/probe_coarse.json');small=read(HERE/'diagnostics/probe_wide.json')
    assert p['status']=='derivative_sign_unresolved' and p['center']=='-1/1024' and p['half_width']=='1/1024'
    low,high=ends(p['motion']['derivatives']['C4']);assert low<0<high
    assert small['status']=='positive_derivative_enclosed' and ends(small['motion']['derivatives']['C4'])[0]>0
    for probe in [p,small]:
        for name,copy in [('continuation.py','continuation_probe_version.py'),('differentiate.py','differentiate_probe_version.py')]:
            assert probe['source_sha256'][name]==sha(HERE/'diagnostics'/copy)
        assert probe['source_sha256']['probe.py']==sha(HERE/'probe.py')
    failure=read(HERE/'diagnostics/rational_interval_api_failure.json')
    assert failure['source_sha256']==sha(HERE/'diagnostics/check_bounds_before_interval_api_fix.py')
    endpoint_failure=read(HERE/'diagnostics/endpoint_interval_audit_failure.json')
    assert endpoint_failure['source_sha256']==sha(HERE/'diagnostics/audit_before_endpoint_interval_fix.py')
    plot=read(HERE/'results/plot_data.json');qa=read(HERE/'results/figure_qa.json')
    assert plot['source_sha256']==sha(HERE/'plot_results.py') and plot['certificate_sha256']==sha(cp)
    assert plot['direct_check_sha256']==sha(HERE/'results/direct_check.json') and plot['coarse_probe_sha256']==sha(HERE/'diagnostics/probe_coarse.json')
    assert len(plot['grid'])==201 and len(plot['samples'])==5 and len(plot['bands'])==32 and not plot['text_outside_canvas']
    grid=list(map(F,plot['grid']));assert grid[0]==-L and grid[-1]==0
    for nu,lo,hi in zip(grid,plot['lower_percent'],plot['upper_percent']):
        assert F(lo)==100*nu*shi/F('2.49203004e-39') and F(hi)==100*nu*slo/F('2.49203006e-39')
    ev={F(x['nu']):x for x in direct['runs'][1]['evaluations']};C0=F(ev[F(0)]['coefficients']['C4'])
    for sample,row in zip(plot['samples'],direct['runs'][1]['rows']):
        nu=F(sample['nu']);v=F(ev[nu]['coefficients']['C4']);assert F(sample['C4'])==v and F(sample['relative_percent'])==100*(v/C0-1)
        assert sample['C4_prime_diagnostic']==row['steps'][1]['derivatives']['C4']
    assert list(map(F,plot['coarse_comparison']))==list(ends(p['motion']['derivatives']['C4']))
    assert list(map(F,plot['refined_comparison']))==[min(ends(x['C4_prime'])[0] for x in c['cells'][:4]),max(ends(x['C4_prime'])[1] for x in c['cells'][:4])]
    for rel,digest in plot['figures'].items():assert sha(HERE/'figures'/rel)==digest
    assert qa['png_sha256']==sha(HERE/'figures/continuation.png') and qa['panels']==3
    assert qa['no_clipped_text'] and qa['no_overlapping_labels'] and qa['proved_bounds_and_diagnostics_distinguished']
    endpoint=read(RESEARCH/'theta_fourth_order/results/certificate.json')['coefficients']['C4']
    a,b=ends(endpoint);assert F('2.49203004e-39')<a<b<F('2.49203006e-39')
    assert F('2.48374879e-39')==F('2.49203004e-39')-L*shi
    assert alg['endpoint_gain_bounds']==['2.96875e-42','8.28125e-42']
    with tempfile.TemporaryDirectory(prefix='r29-replay-') as tmp:
        tmp=Path(tmp)
        for script,name,extra in [('check_algebra.py','algebra.json',[]),('check_bounds.py','rational_check.json',['--cover-dir',str(cover)])]:
            output=tmp/name;run=subprocess.run([sys.executable,'-B',str(HERE/script),*extra,'--output',str(output)],cwd=tmp,capture_output=True,text=True)
            assert run.returncode==0,run.stdout+run.stderr
            assert sha(output)==sha(HERE/'results'/name),script
        if with_arb:
            out=tmp/'cover';run=subprocess.run([sys.executable,'-B',str(HERE/'certify_continuation.py'),'--output-dir',str(out)],cwd=tmp,capture_output=True,text=True)
            assert run.returncode==0,run.stdout+run.stderr
            assert {p.name for p in out.iterdir()}=={p.name for p in cover.iterdir()}
            for p in out.iterdir():assert sha(p)==sha(cover/p.name),p.name
        run=subprocess.run([sys.executable,'-B',str(RESEARCH/'cusp_coefficient_motion/audit_snapshot.py'),*(['--with-arb'] if with_arb else [])],cwd=tmp,capture_output=True,text=True)
        assert run.returncode==0,run.stdout+run.stderr
        previous=json.loads(run.stdout);assert previous['status']=='R28_coefficient_motion_evidence_and_preservation_passed'
        assert previous['Arb_replayed_in_this_run']==with_arb
    proof=(HERE/'PROOF.md').read_text();assert re.findall(r'\\tag\{E(\d+)\}',proof)==list(map(str,range(1,13)))
    for marker in ['one-sided','no maximality','not extended','original driver ν']:
        # Markdown emphasis is irrelevant to this scope guard.
        assert marker in proof.replace('**',''),marker
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))
    for p in HERE.rglob('*'):
        if p.is_file() and p.suffix in ['.py','.md','.json','.txt']:assert all(x>=32 or x in [9,10,13] for x in p.read_bytes()),p
        if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
    for p in HERE.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('http://','https://','#')):continue
            path=p.parent/target.split('#')[0]
            if path.name in ['audit_report.json','manifest.json'] and not path.exists():continue
            assert path.exists(),(p,target)
    return {'status':'R29_recentered_continuation_evidence_and_preservation_passed','prior_manifests':29,'prior_frozen_file_entries':count,
      'cusp_anchors':32,'closed_cells':32,'finite_roots_per_cell':28,'sign_leaves_per_cell':354,
      'exact_check_groups':14,'rational_check_count':17088,'derivative_AD_decisions':1408,
      'diagnostic_distinct_drivers':23,'diagnostic_integral_solves':46,'diagnostic_derivative_comparisons':comparisons,
      'diagnostic_value_comparisons':values_compared,'recorded_residual_checks':residuals,'two_step_checks':step_checks,'precision_comparisons':120,
      'driver_interval':['-1/64','0'],'enlargement_factor':1024,'published_C4_prime_bounds':['1.9e-40','5.3e-40'],
      'pointwise_asymptotic_interpretation':True,'previous_finite_M_remainder_extended':False,'maximal_arc_claimed':False,
      'coarse_inconclusiveness_resolved_on_same_interval':True,'C4_convexity_claimed':False,'finite_M_optimum_monotonicity_claimed':False,
      'new_sixth_coefficient':False,'whole_original_arc_covered':False,'previous_packages_modified':False,'manuscripts_modified':False,
      'external_referee_review':False,'formal_proof':False,'literature_priority_established':False,'public_release_or_submission':False,
      'audit_source_sha256':sha(__file__),
      'trust_boundary':'Provenance, exact and rational replay, fresh optional Arb regeneration and recorded independent diagnostics. Banach, convexity, graph identification, weighted summability and differentiation of infinite sums remain analytic arguments rather than a formal proof checked by this program.'}
def main():
    ap=argparse.ArgumentParser();group=ap.add_mutually_exclusive_group();group.add_argument('--preflight',action='store_true');group.add_argument('--freeze',action='store_true')
    ap.add_argument('--with-arb',action='store_true');args=ap.parse_args();result=inspect(args.with_arb)
    if args.freeze:
        assert not (HERE/'manifest.json').exists(),'Already frozen.'
        result['closed_utc']=datetime.now(timezone.utc).isoformat();result['Arb_replayed_at_freeze']=args.with_arb
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps({'created_utc':result['closed_utc'],'scope':'C4 sensitivity on the exact cusp arc [-1/64,0], with recentered validated continuation.','files':files,'audit':result},indent=2)+'\n')
    elif not args.preflight:
        recorded=read(HERE/'audit_report.json')
        for key,value in result.items():assert recorded[key]==value,key
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {r['path'] for r in manifest['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='manifest.json'}
    print(json.dumps({**result,'Arb_replayed_in_this_run':args.with_arb},indent=2))
if __name__=='__main__':main()
