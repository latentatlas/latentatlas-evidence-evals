#!/usr/bin/env python3
"""R24 evidence/provenance audit with optional fresh Arb reproduction."""
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
def contains(v,x):
    a,b=ends(v);return a<=F(x)<=b
def inspect(with_arb):
    assert __debug__,'Assertions must be enabled.'
    baseline=read(HERE/'baseline.json');n=0
    assert len(baseline['manifest_sha256'])==24
    for rel,digest in baseline['manifest_sha256'].items():
        p=RESEARCH/rel;assert sha(p)==digest,rel
        for row in read(p)['files']:
            assert sha(p.parent/row['path'])==row['sha256'],(rel,row['path']);n+=1
    assert n==baseline['frozen_entries']==1016
    cp=HERE/'results/certificate.json';ap=HERE/'results/algebra.json';rp=HERE/'results/rational_check.json'
    cert,alg,rat,direct=read(cp),read(ap),read(rp),read(HERE/'results/direct_check.json')
    assert cert['dps']==120 and len(cert['finite_roots'])==28
    for name,digest in cert['source_sha256'].items():assert sha(HERE/name)==digest
    source_inputs={'R15':RESEARCH/'kernel_slope_asymptotics/results/asymptotic_certificate.json',
        'jets':RESEARCH/'cusp_shape_design/results/local_jets.json','R23':RESEARCH/'infinite_slope_fourth_order/manifest.json','algebra':ap}
    for key,p in source_inputs.items():assert cert['input_sha256'][key]==sha(p)
    assert alg['source_sha256']==sha(HERE/'check_algebra.py')
    assert alg['algebra_helper_sha256']==sha(RESEARCH/'finite_slope_fourth_order/check_fourth_order.py')
    assert alg['check_groups']==len(alg['checks'])==15 and all(x['passed'] for x in alg['checks'])
    assert rat['input_certificate_sha256']==sha(cp) and rat['source_sha256']==sha(HERE/'check_certificate.py')
    assert rat['rational_interval_source_sha256']==sha(HERE/'rational_intervals.py')
    assert rat['base_interval_helper_sha256']==sha(RESEARCH/'finite_slope_optimum/exact_interval.py')
    assert rat['rounding_bits']==512 and rat['root_count']==28
    assert rat['contractions_checked']==sum(len(r['contractions']) for r in cert['finite_roots'])==31
    assert rat['local_quantities_compared']==588 and rat['negative_control_wrong_moment_sign_rejected']
    lo,hi=map(F,rat['published_C4_strict_bounds']);assert (lo,hi)==(F('2.49203004e-39'),F('2.49203006e-39'))
    for a,b in [ends(cert['coefficients']['C4']),tuple(map(F,rat['reconstructed_intervals']['C4']))]:assert 0<lo<a<b<hi
    assert ends(cert['improved_dual_radius'])[1]<F('4.130e-14')
    assert ends(cert['linear_solve']['eta'])[1]<F('9.27e-9')
    assert all(ends(x)[0]>0 for x in cert['shifted_Gram_principal_minors'])
    for key,bound in {'Gamma':'1.674e-62','G_entry':'1.057e-66','B_entry':'1.892e-61','R':'1.148e-55'}.items():
        assert 0<ends(cert['tail_absolute_bounds'][key])[0]<=ends(cert['tail_absolute_bounds'][key])[1]<F(bound)
    assert cert['formal_reference_terms']['not_a_finite_M_error_certificate']
    assert direct['source_sha256']==sha(HERE/'crosscheck_direct.py') and direct['certificate_sha256']==sha(cp)
    assert [(r['dps'],r['quadrature_order']) for r in direct['runs']]==[(80,72),(120,96)]
    root_comparisons=0;scalar_comparisons=0;matrix_comparisons=0
    for run in direct['runs']:
        assert run['theta_terms']==12 and run['cutoff']==1 and len(run['rows'])==28
        for qr,cr in zip(run['rows'],cert['finite_roots']):
            assert contains(cr['root_interval'],qr['root']);root_comparisons+=1
            for x,b in zip(qr['q_root_jets'],cr['density_root_jets']):assert contains(b,x);root_comparisons+=1
            for key in ['Gamma','R']:assert contains(cr[key],qr[key]);root_comparisons+=1
            for i in range(3):
                assert contains(cr['B'][i],qr['B'][i]);root_comparisons+=1
                for j in range(3):assert contains(cr['G'][i][j],qr['G'][i][j]);root_comparisons+=1
        for key,val in run['values'].items():
            if key=='f':continue
            assert contains(cert['coefficients'][key],val),(run['dps'],key);scalar_comparisons+=1
        for i in range(3):
            assert contains(cert['infinite_sums']['B'][i],run['B'][i]);matrix_comparisons+=1
            assert contains(cert['linear_solve']['v_enclosure'][i],run['v'][i]);matrix_comparisons+=1
            for j in range(3):assert contains(cert['infinite_sums']['G'][i][j],run['G'][i][j]);matrix_comparisons+=1
    assert root_comparisons==1008 and scalar_comparisons==24 and matrix_comparisons==30
    assert direct['per_run_root_values_compared']==504 and direct['per_run_final_values_compared']==12
    low,high=direct['runs']
    for key,x in high['values'].items():
        x=F(x);diff=abs(x-F(low['values'][key]))/max(abs(x),F('1e-100'))
        assert diff<F('1e-55') and F(direct['relative_precision_differences'][key])<F('1e-55')
    with tempfile.TemporaryDirectory(prefix='r24-replay-') as td:
        td=Path(td)
        jobs=[('check_algebra.py',ap,[]),('check_certificate.py',rp,['--certificate',str(cp)])]
        if with_arb:jobs.append(('certify_coefficient.py',cp,[]))
        for script,recorded,extra in jobs:
            fresh=td/recorded.name
            run=subprocess.run([sys.executable,'-B',str(HERE/script),*extra,'--output',str(fresh)],cwd=td,capture_output=True,text=True)
            assert run.returncode==0,run.stdout+run.stderr
            assert sha(fresh)==sha(recorded),script
    plot=read(HERE/'results/plot_data.json');qa=read(HERE/'results/figure_qa.json')
    assert plot['source_sha256']==sha(HERE/'plot_results.py') and plot['certificate_sha256']==sha(cp)
    assert len(plot['formal_ratio_curve'])==200 and plot['precision_digits']==80
    assert plot['not_a_plot_of_the_finite_budget_optimum']
    for name,digest in plot['figures'].items():assert sha(HERE/'figures'/name)==digest
    assert qa['panels']==2 and not qa['clipped_text'] and not qa['overlapping_labels']
    assert qa['png_sha256']==sha(HERE/'figures/theta_fourth_order.png')
    table=(HERE/'results/TABLE.md').read_text()
    for key in ['delta0','D','Gamma','R','P','Xi','C2','C4','C4_amplitude_part','C4_shape_part','C4_moment_part','C4_over_C2']:
        a,b=ends(cert['coefficients'][key]);assert format(float((a+b)/2),'.12g') in table
    assert re.findall(r'\\tag\{C(\d+)\}',(HERE/'PROOF.md').read_text())==list(map(str,range(1,15)))
    assert read(HERE/'diagnostics/finite_probe.json')['status']=='diagnostic_only_tail_not_yet_included'
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))
    for p in HERE.rglob('*'):
        if p.is_file() and p.suffix in ['.md','.py','.json','.txt']:
            assert all(x>=32 or x in (9,10,13) for x in p.read_bytes()),p.name
        if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
    for p in HERE.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('http://','https://','#')):continue
            q=p.parent/target.split('#')[0]
            if q.name in ['audit_report.json','manifest.json'] and not q.exists():continue
            assert q.exists(),(p.name,target)
    return {'status':'R24_theta_C4_evidence_and_preservation_passed','prior_manifests':24,'prior_frozen_file_entries':n,
       'exact_check_groups':15,'finite_roots':28,'accepted_root_contractions':31,'rational_local_checks':588,
       'independent_precision_runs':2,'independent_root_jet_comparisons':root_comparisons,
       'independent_scalar_comparisons':scalar_comparisons,'independent_matrix_vector_comparisons':matrix_comparisons,
       'independent_total_comparisons':root_comparisons+scalar_comparisons+matrix_comparisons,
       'published_C4_strict_bounds':['2.49203004e-39','2.49203006e-39'],'C4_positive':True,
       'whole_root_tail_included':True,'validated_matrix_solve':True,'scientific_figure_panels':2,'proof_equations':14,
       'effective_fourth_order_remainder':False,'numerical_asymptotic_onset':False,'cusp_curve_uniformity':False,
       'exact_finite_M_optimizer_identified':False,'previous_packages_modified':False,'manuscripts_modified':False,
       'formal_proof':False,'external_referee_review':False,'literature_priority_established':False,'public_release_or_submission':False,
       'audit_source_sha256':sha(__file__),
       'trust_boundary':'Hashes, fresh exact/rational arithmetic and recorded independent numerical comparisons; --with-arb also freshly reproduces transcendental enclosures. The analytic R23 theorem, root localization and tail derivations are explicit dependencies, not mechanically proved by this audit.'}
def main():
    ap=argparse.ArgumentParser();group=ap.add_mutually_exclusive_group();group.add_argument('--preflight',action='store_true');group.add_argument('--freeze',action='store_true')
    ap.add_argument('--with-arb',action='store_true');args=ap.parse_args();result=inspect(args.with_arb)
    if args.freeze:
        assert not (HERE/'manifest.json').exists(),'Already frozen.'
        result['closed_utc']=datetime.now(timezone.utc).isoformat();result['Arb_replayed_at_freeze']=args.with_arb
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps({'created_utc':result['closed_utc'],
           'scope':'Fixed exact theta fourth-order coefficient and sign, whole-tail bounds, independent arithmetic and numerical checks.',
           'files':files,'audit':result},indent=2)+'\n')
    elif not args.preflight:
        rec=read(HERE/'audit_report.json')
        for key,val in result.items():assert rec[key]==val,key
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {row['path'] for row in manifest['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='manifest.json'}
    print(json.dumps({**result,'Arb_replayed_in_this_run':args.with_arb},indent=2))
if __name__=='__main__':main()
