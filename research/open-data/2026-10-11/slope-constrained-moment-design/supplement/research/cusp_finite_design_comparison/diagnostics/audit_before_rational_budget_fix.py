#!/usr/bin/env python3
"""R30 evidence/provenance audit with fresh arithmetic and optional Arb replay."""
import sys
sys.dont_write_bytecode=True
import argparse,ast,gzip,hashlib,json,re,struct,subprocess,tempfile
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def ends(x):
    m,e=x['mid_man_exp'];r,s=x['rad_man_exp'];v=F(m)*F(2)**e;d=F(r)*F(2)**s;return v-d,v+d
def inspect(with_arb):
    assert __debug__,'Keep assertions enabled.'
    base=read(HERE/'baseline.json');assert len(base['manifest_sha256'])==30;count=0
    for rel,digest in base['manifest_sha256'].items():
        p=RESEARCH/rel;assert sha(p)==digest,rel
        for row in read(p)['files']:
            assert sha(p.parent/row['path'])==row['sha256'],(rel,row['path']);count+=1
    assert count==base['frozen_entries']==1235
    cover=HERE/'results/cover';cp=cover/'certificate.json';c=read(cp)
    parent=RESEARCH/'cusp_motion_continuation/results/cover';old=read(parent/'certificate.json')
    assert c['status']=='R30_uniform_effective_remainder_cover' and c['dps']==120
    assert c['driver_interval']==old['driver_interval']==['-1/64','0']
    assert c['cell_count']==len(c['cells'])==len(list(cover.glob('*.json.gz')))==32
    assert c['minimum_slope_budget']=='2e-5' and c['source_sha256']==sha(HERE/'certify_remainder.py')
    inputs={'R29_cover':parent/'certificate.json','R27_remainder':RESEARCH/'cusp_uniform_remainder/remainder.py',
      'R27_model':RESEARCH/'cusp_uniform_remainder/model.py','R26_tail':RESEARCH/'theta_global_remainder/results/certificate.json',
      'R30_algebra':HERE/'results/algebra.json'}
    for name,p in inputs.items():assert c['input_sha256'][name]==sha(p),name
    max_km=F(0);max_kp=F(0)
    for i,(row,previous) in enumerate(zip(c['cells'],old['cells'])):
        assert row['index']==previous['index']==i and row['left']==previous['left'] and row['right']==previous['right']
        assert F(row['left'])==-(i+1)/F(2048) and F(row['right'])==-i/F(2048)
        p=cover/row['file'];q=parent/row['file'];assert sha(p)==row['sha256'] and sha(q)==row['input_cell_sha256']==previous['sha256']
        record=json.loads(gzip.decompress(p.read_bytes()));r=record['remainder'];prior=json.loads(gzip.decompress(q.read_bytes()))
        assert record['index']==i and record['input_cell_sha256']==sha(q)
        assert len(r['local'])==len(prior['cell']['dual']['tight_roots'])==28
        assert len(r['sign_cover'])==row['sign_cover_leaves']==354
        assert row['Kminus']==r['Kminus'] and row['Kplus']==r['Kplus']
        max_km=max(max_km,ends(r['Kminus'])[1]);max_kp=max(max_kp,ends(r['Kplus'])[1])
        assert ends(r['Kdual6'])[1]<655000 and ends(r['Kprimal6'])[1]<F('4.746e6')
        assert ends(r['amplitude_upper'])[1]<F('9.181e-10')
        assert ends(r['upper_scalar_margin'])[0]>F('1.7683e-15')
        assert ends(r['minimum_slope_budget'])==(F('2e-5'),F('2e-5'))
        for j in range(3):
            a,b=ends(r['repair_contraction'][j]),ends(r['repair_forcing'][j]);assert a[1]+b[1]<1
            assert a[1]<[F('.005731'),F('.007842'),F('.004703')][j]
            assert b[1]<[F('.328781'),F('.448496'),F('.267009')][j]
        segments=[]
        for leaf in r['sign_cover']:
            lo,hi=ends(leaf['lo'])[0],ends(leaf['hi'])[1];assert lo<hi
            a,b=ends(leaf['raw_residual']);assert a>0 if leaf['sign']==1 else b<0
            segments.append((lo,hi))
        for local,original in zip(r['local'],prior['cell']['dual']['tight_roots']):
            assert local['index']==original['index'] and local['orientation']==original['orientation']
            a,b=ends(local['root']);x,y=ends(original['root']);assert a<=x<=y<=b
            lo,hi=ends(local['neighborhood']);assert lo<a<b<hi;segments.append((lo,hi))
            assert local['root_jets']['at_true_root']
            assert len(local['root_jets']['residual_jets'])==6 and len(local['neighborhood_jets']['residual_jets'])==6
            assert ends(local['trial_derivative_lower'])[0]>0
        segments.sort();assert segments[0][0]==0 and segments[-1][1]==1
        assert all(a[1]>=b[0] for a,b in zip(segments,segments[1:]))
    assert max_km<F('1.001e-53') and max_kp<F('1.620e-53')
    alg=read(HERE/'results/algebra.json');rat=read(HERE/'results/rational_check.json');cmp=read(HERE/'results/comparisons.json')
    assert alg['status']=='R30_exact_sextic_tail_extension_passed' and alg['driver_width']=='1/64'
    assert alg['source_sha256']==sha(HERE/'check_algebra.py') and alg['check_groups']==len(alg['checks'])==12
    assert alg['R26_algebra_sha256']==sha(RESEARCH/'theta_global_remainder/results/algebra.json')
    assert all(x['passed'] for x in alg['checks']) and all(F(x)<1 for x in alg['potential_relative_bounds'])
    assert rat['status']=='R30_rational_remainder_and_three_derivatives_passed' and rat['rounding_bits']==512
    assert rat['check_count']==4064 and len(rat['cells'])==32
    for key,path in [('source_sha256',HERE/'check_bounds.py'),('derivative_source_sha256',HERE/'derivative_check.py'),
      ('rational_helper_sha256',RESEARCH/'theta_fourth_order/rational_intervals.py'),('certificate_sha256',cp)]:assert rat[key]==sha(path),key
    for i,row in enumerate(rat['cells']):
        assert row['index']==i and row['file_sha256']==c['cells'][i]['sha256'] and row['input_cell_sha256']==c['cells'][i]['input_cell_sha256']
        assert row['remainder']['check_count']==len(row['remainder']['checks'])==81
        assert row['derivative_AD']['check_count']==len(row['derivative_AD']['checks'])==46
        assert F(row['remainder']['Kminus_upper'])<F('1.001e-53') and F(row['remainder']['Kplus_upper'])<F('1.620e-53')
    assert cmp['status']=='R30_exact_finite_value_comparisons_passed' and cmp['check_count']==len(cmp['checks'])==146
    assert cmp['source_sha256']==sha(HERE/'compare_values.py') and cmp['rational_check_sha256']==sha(HERE/'results/rational_check.json')
    assert len(cmp['ordered_grid'])==33 and len(cmp['cases'])==8
    endpoint=cmp['cases'][0];a,b=map(F,endpoint['actual_difference']);assert F('4.21877890e-13')<a<b<F('4.68753399e-13')
    assert list(map(F,endpoint['normalized_fourth_difference']))==[F('2.90225e-42'),F('8.34775e-42')]
    check_figure(cmp)
    replay(with_arb,cover)
    proof=(HERE/'PROOF.md').read_text();assert re.findall(r'\\tag\{F(\d+)\}',proof)==list(map(str,range(1,11)))
    for marker in ['one-sided','separate function g','target f_ν depend on ν','arbitrarily close','No derivative','not a formal']:
        assert marker in proof,marker
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
    return {'status':'R30_finite_design_comparison_evidence_and_preservation_passed',
      'prior_manifests':30,'prior_frozen_file_entries':count,'closed_cells':32,'finite_roots_per_cell':28,'sign_leaves_per_cell':354,
      'exact_tail_check_groups':12,'rational_check_count':4064,'remainder_decisions':2592,'derivative_AD_decisions':1472,
      'exact_comparison_checks':146,'ordered_grid_nodes':33,'driver_interval':['-1/64','0'],'minimum_slope_budget':'2e-5',
      'uniform_remainder_constants':['1.02e-53','1.64e-53'],'remainder_interval_enlargement_factor':1024,
      'actual_value_comparison':True,'normalized_fourth_value_comparison':True,
      'monotonicity_at_arbitrarily_close_drivers_proved':False,'finite_M_optimum_derivative_proved':False,
      'same_target_or_profile_for_all_drivers_claimed':False,'numerical_finite_M_optimizer_computed':False,
      'C6_claimed':False,'whole_original_arc_covered':False,'previous_packages_modified':False,'manuscripts_modified':False,
      'external_referee_review':False,'formal_proof':False,'literature_priority_established':False,'public_release_or_submission':False,
      'audit_source_sha256':sha(__file__),
      'trust_boundary':'Hash preservation, exact and rational replay, optional Arb regeneration including R29, and exact finite-value comparisons. Transcendental enclosures are explicit rational-check inputs. The analytic support, contraction, summability, compactness and differentiation arguments require separate mathematical review.'}

def check_figure(cmp):
    from compare_values import M0,H,KS,LOW,pair_bounds
    plot=read(HERE/'results/plot_data.json');qa=read(HERE/'results/figure_qa.json')
    assert plot['source_sha256']==sha(HERE/'plot_results.py') and plot['comparison_source_sha256']==sha(HERE/'compare_values.py')
    assert plot['comparisons_sha256']==sha(HERE/'results/comparisons.json') and not plot['text_outside_canvas']
    assert not plot['finite_budget_optimizer_computed'] and len(plot['rows'])==len(plot['resolutions'])==257
    for i,row in enumerate(plot['rows']):
        nu=-H+H*i/256;assert F(row['nu'])==nu
        assert {k:row[k] for k in ['actual_difference','normalized_fourth_difference']}==pair_bounds(nu+H,M0)
    for i,row in enumerate(plot['resolutions']):
        m=M0*(1+F(99*i,256));assert F(row['budget'])==m
        assert F(row['actual_sufficient'])==F('1.54e-14')*(M0/m)**6
        assert F(row['fourth_threshold'])==KS/(LOW[2]*m**2)
    for name,digest in plot['figures'].items():assert sha(HERE/'figures'/name)==digest,name
    png=HERE/'figures/finite_design_comparison.png';assert qa['png_sha256']==sha(png)
    assert list(struct.unpack('>II',png.read_bytes()[16:24]))==qa['image_dimensions']==[3132,1026]
    assert qa['panels']==3 and qa['no_clipped_text'] and qa['no_overlapping_labels'] and qa['bounds_not_fitted_optimum'] and qa['fixed_budget_and_scope_labels_visible']
    failure=read(HERE/'diagnostics/plot_tick_failure.json')
    assert failure['source_sha256']==sha(HERE/'diagnostics/plot_before_tick_fix.py') and failure['status']=='failed_before_output'

def replay(with_arb,cover):
    with tempfile.TemporaryDirectory(prefix='r30-replay-') as tmp:
        tmp=Path(tmp)
        for script,name,extra in [('check_algebra.py','algebra.json',[]),('check_bounds.py','rational_check.json',['--cover-dir',str(cover)]),
          ('compare_values.py','comparisons.json',[])]:
            print('R30 replay:',script,file=sys.stderr,flush=True)
            output=tmp/name;r=subprocess.run([sys.executable,'-B',str(HERE/script),*extra,'--output',str(output)],cwd=tmp,capture_output=True,text=True)
            assert r.returncode==0,r.stdout+r.stderr
            assert sha(output)==sha(HERE/'results'/name),script
        if with_arb:
            print('R30 replay: fresh 32-cell Arb remainder',file=sys.stderr,flush=True)
            output=tmp/'cover';r=subprocess.run([sys.executable,'-B',str(HERE/'certify_remainder.py'),'--output-dir',str(output)],cwd=tmp,capture_output=True,text=True)
            assert r.returncode==0,r.stdout+r.stderr
            assert {p.name for p in output.iterdir()}=={p.name for p in cover.iterdir()}
            for p in output.iterdir():assert sha(p)==sha(cover/p.name),p.name
        print('R30 prerequisite replay: R29'+(' with Arb' if with_arb else ''),file=sys.stderr,flush=True)
        r=subprocess.run([sys.executable,'-B',str(RESEARCH/'cusp_motion_continuation/audit_snapshot.py'),*(['--with-arb'] if with_arb else [])],cwd=tmp,capture_output=True,text=True)
        assert r.returncode==0,r.stdout+r.stderr;previous=json.loads(r.stdout)
        assert previous['status']=='R29_recentered_continuation_evidence_and_preservation_passed'
        assert previous['Arb_replayed_in_this_run']==with_arb

def main():
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group();g.add_argument('--preflight',action='store_true');g.add_argument('--freeze',action='store_true')
    ap.add_argument('--with-arb',action='store_true');args=ap.parse_args();result=inspect(args.with_arb)
    if args.freeze:
        assert not (HERE/'manifest.json').exists(),'Already frozen.'
        result['closed_utc']=datetime.now(timezone.utc).isoformat();result['Arb_replayed_at_freeze']=args.with_arb
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps({'created_utc':result['closed_utc'],
          'scope':'Uniform effective fourth-order remainder and resolved finite-M optimal-value comparisons on the exact cusp arc [-1/64,0].',
          'files':files,'audit':result},indent=2)+'\n')
    elif not args.preflight:
        recorded=read(HERE/'audit_report.json')
        for key,value in result.items():assert recorded[key]==value,key
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {r['path'] for r in manifest['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='manifest.json'}
    print(json.dumps({**result,'Arb_replayed_in_this_run':args.with_arb},indent=2))
if __name__=='__main__':main()
