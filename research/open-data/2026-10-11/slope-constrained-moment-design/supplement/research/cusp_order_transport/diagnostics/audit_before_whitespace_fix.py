#!/usr/bin/env python3
"""R31 evidence, fresh arithmetic replay, prerequisites and frozen preservation."""
import sys
sys.dont_write_bytecode=True
import argparse,ast,hashlib,json,re,struct,subprocess,tempfile
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent
EXPECTED_CAPS={'kappa':['.00259','.00260'],'f_log_derivative':['.0437','.0451'],'lambda':['-3.651','-3.645'],'mu':['8.330','8.336'],'nu':['-1/64','0'],'lambda_prime':['.3260','.3264'],'mu_prime':['.2939','.2942']}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def ends(x):
    m,e=x['mid_man_exp'];r,s=x['rad_man_exp'];v=F(m)*F(2)**e;d=F(r)*F(2)**s;return v-d,v+d

def figure_check(rat):
    p=read(HERE/'results/plot_data.json');qa=read(HERE/'results/figure_qa.json')
    assert p['source_sha256']==sha(HERE/'plot_results.py') and p['rational_check_sha256']==sha(HERE/'results/rational_check.json')
    assert p['finite_rows']==rat['finite_cells'] and not p['optimizer_computed'] and p['text_outside_canvas']==[]
    M=F('2e-5');L=F('2.7e-11')+F('7.4e-26')/M**2+F('1.9e-40')/M**4;KS=F('2.66e-53')
    for row in p['comparison_rows']:
        d=F(row['distance']);assert 0<d<=F(1,64)
        assert F(row['R30_lower_per_distance'])==L-KS/M**6/d and F(row['R31_lower_per_distance'])==F('2.07e-11')
    for name,digest in p['figures'].items():assert sha(HERE/'figures'/name)==digest
    png=HERE/'figures/order_transport.png';assert qa['png_sha256']==sha(png)
    assert list(struct.unpack('>II',png.read_bytes()[16:24]))==qa['image_dimensions']==[2592,1080]
    assert qa['panels']==2 and all(qa[k] for k in ['no_clipped_text','no_overlapping_labels','bounds_not_fitted_optimum','domains_and_open_question_visible'])

def replay(with_arb):
    with tempfile.TemporaryDirectory(prefix='r31-replay-') as tmp:
        tmp=Path(tmp)
        for script,name,extra in [('check_algebra.py','algebra.json',[]),('check_bounds.py','rational_check.json',['--cover-dir',str(HERE/'results/cover')]),('direct_check.py','direct_check.json',[])]:
            print('R31 replay:',script,file=sys.stderr,flush=True)
            output=tmp/name;r=subprocess.run([sys.executable,'-B',str(HERE/script),*extra,'--output',str(output)],cwd=tmp,capture_output=True,text=True)
            assert r.returncode==0,r.stdout+r.stderr
            assert sha(output)==sha(HERE/'results'/name),script
        if with_arb:
            print('R31 replay: fresh 1024-cell Arb theta logarithmic jets',file=sys.stderr,flush=True)
            output=tmp/'cover';r=subprocess.run([sys.executable,'-B',str(HERE/'certify_transport.py'),'--output-dir',str(output)],cwd=tmp,capture_output=True,text=True)
            assert r.returncode==0,r.stdout+r.stderr
            assert {p.name for p in output.iterdir()}=={p.name for p in (HERE/'results/cover').iterdir()}
            for p in output.iterdir():assert sha(p)==sha(HERE/'results/cover'/p.name),p.name
        print('R31 prerequisite replay: R30'+(' with Arb' if with_arb else ''),file=sys.stderr,flush=True)
        r=subprocess.run([sys.executable,'-B',str(RESEARCH/'cusp_finite_design_comparison/audit_snapshot.py'),*(['--with-arb'] if with_arb else [])],cwd=tmp,capture_output=True,text=True)
        assert r.returncode==0,r.stdout+r.stderr;previous=json.loads(r.stdout)
        assert previous['status']=='R30_finite_design_comparison_evidence_and_preservation_passed' and previous['Arb_replayed_in_this_run']==with_arb

def inspect(with_arb):
    assert __debug__,'Keep assertions enabled.'
    base=read(HERE/'baseline.json');assert len(base['manifest_sha256'])==31;count=0
    for rel,digest in base['manifest_sha256'].items():
        p=RESEARCH/rel;assert sha(p)==digest,rel
        for row in read(p)['files']:
            assert sha(p.parent/row['path'])==row['sha256'],(rel,row['path']);count+=1
    assert count==base['frozen_entries']==1298
    c=read(HERE/'results/cover/certificate.json');a=read(HERE/'results/algebra.json');r=read(HERE/'results/rational_check.json');d=read(HERE/'results/direct_check.json')
    assert c['status']=='R31_generator_cover_computed' and c['dps']==120 and c['subdivisions']==1024 and c['theta_terms']==12
    assert c['driver_interval']==['-1/64','0'] and c['finite_u_interval']==['0','1'] and c['a0']=='1/16384' and c['caps']==EXPECTED_CAPS
    assert c['source_sha256']==sha(HERE/'certify_transport.py') and c['payload_sha256']==sha(HERE/'results/cover/finite_cover.json.gz')
    assert c['R29_cover_sha256']==sha(RESEARCH/'cusp_motion_continuation/results/cover/certificate.json')
    assert ends(c['maximum_finite_dissipativity_upper'])[1]<F('-.0217069') and c['worst_cell']==461
    assert a['status']=='R31_exact_transport_and_tail_algebra_passed' and a['check_groups']==len(a['checks'])==31 and all(v['passed'] for v in a['checks'])
    assert a['source_sha256']==sha(HERE/'check_algebra.py') and a['symbolic_helper_sha256']==sha(RESEARCH/'finite_slope_fourth_order/check_fourth_order.py')
    assert F(a['tail_dissipativity_upper_at_one'])<F('-.0511166') and F(a['tail_derivative_margin'])>0
    assert a['contraction_rate']=='1/50' and F(a['logarithmic_value_rate'])==F('.02259') and a['linear_value_rate']=='2.07e-11'
    assert r['status']=='R31_rational_generator_and_transport_inputs_passed' and r['rounding_bits']==512 and r['check_count']==len(r['checks'])==19017
    assert len(r['parameters'])==32 and len(r['finite_cells'])==1024 and r['all_u_and_all_nu'] and r['strict_rate']=='1/50'
    for key,p in [('source_sha256',HERE/'check_bounds.py'),('rational_helper_sha256',RESEARCH/'theta_fourth_order/rational_intervals.py'),('cover_sha256',HERE/'results/cover/certificate.json'),('algebra_sha256',HERE/'results/algebra.json'),('R30_cover_sha256',RESEARCH/'cusp_finite_design_comparison/results/cover/certificate.json')]:assert r[key]==sha(p),key
    assert F(r['maximum_finite_upper'])<F('-.0217085') and F(r['tail_upper'])==F(a['tail_dissipativity_upper_at_one'])
    assert F(r['amplitude_upper'])<F('9.181e-10') and F(r['delta_lower'])>F('9.17e-10')
    assert d['status']=='R31_independent_transport_diagnostics_passed' and not d['rigorous_interval_evidence'] and not d['tail_infinite_integral_verified_by_diagnostic']
    assert d['source_sha256']==sha(HERE/'direct_check.py') and d['input_sha256']==sha(RESEARCH/'cusp_motion_continuation/results/direct_check.json')
    assert [x['dps'] for x in d['runs']]==[60,90]
    for row in d['runs']:
        assert row['moment_comparisons']==12 and row['derivative_checks']==15 and row['semigroup_checks']==5
        for key in ['max_relative_moment_error','max_scaled_derivative_error','max_scaled_semigroup_error']:assert F(row[key])<F(10)**(-row['dps']+12)
    for name in ['negative_power_api_failure','tiny_input_rounding_failure','exponential_sign_failure']:
        failure=read(HERE/'diagnostics'/(name+'.json'));assert failure['status']=='development_failure_preserved' and (HERE/'diagnostics'/failure['original_source']).exists()
    figure_check(r)
    proof=(HERE/'PROOF.md').read_text();assert re.findall(r'\\tag\{T(\d+)\}',proof)==list(map(str,range(1,12)))
    for marker in ['separate function g','target f_ν depends on ν','No derivative','whole-half-line bound','absolute value inequality','There is no positive minimum separation','not a formal','Still open here']:assert marker in proof,marker
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
    replay(with_arb)
    return {'status':'R31_strict_optimal_value_transport_evidence_and_preservation_passed','prior_manifests':31,'prior_frozen_file_entries':count,
      'closed_driver_cells':32,'closed_u_cells':1024,'whole_half_line_included':True,'exact_algebra_groups':31,'rational_check_count':19017,
      'diagnostic_integral_checks':24,'diagnostic_derivative_checks':30,'diagnostic_composition_checks':10,
      'driver_interval':['-1/64','0'],'minimum_slope_budget':'2e-5','contraction_rate':'1/50','logarithmic_value_rate':'.02259','linear_value_rate':'2.07e-11',
      'actual_value_strict_monotonicity_at_arbitrarily_close_drivers':True,'normalized_fourth_value_full_monotonicity_proved':False,'finite_M_optimum_derivative_proved':False,
      'same_target_or_profile_for_all_drivers_claimed':False,'numerical_finite_M_optimizer_computed':False,'C6_claimed':False,'whole_original_arc_covered':False,
      'previous_packages_modified':False,'manuscripts_modified':False,'external_referee_review':False,'formal_proof':False,'literature_priority_established':False,'public_release_or_submission':False,
      'audit_source_sha256':sha(__file__),'trust_boundary':'Analytic moment transport and characteristic comparison with validated whole-domain bounds. Rational checker takes explicit Arb transcendental enclosures as inputs. Frozen R29/R30 analytic results are prerequisites. Numerical replay is not formal verification or external expert review.'}

def main():
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group();g.add_argument('--preflight',action='store_true');g.add_argument('--freeze',action='store_true');ap.add_argument('--with-arb',action='store_true');args=ap.parse_args()
    if args.freeze:assert not (HERE/'manifest.json').exists(),'Already frozen.'
    result=inspect(args.with_arb)
    if args.freeze:
        result['closed_utc']=datetime.now(timezone.utc).isoformat();result['Arb_replayed_at_freeze']=args.with_arb
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps({'created_utc':result['closed_utc'],'scope':'Strict monotonicity of actual finite-slope optimal amplitude on the exact cusp arc [-1/64,0] by moment-preserving contractive transport.','files':files,'audit':result},indent=2)+'\n')
    elif not args.preflight:
        recorded=read(HERE/'audit_report.json')
        for key,value in result.items():assert recorded[key]==value,key
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {r['path'] for r in manifest['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='manifest.json'}
    print(json.dumps({**result,'Arb_replayed_in_this_run':args.with_arb},indent=2))
if __name__=='__main__':main()
