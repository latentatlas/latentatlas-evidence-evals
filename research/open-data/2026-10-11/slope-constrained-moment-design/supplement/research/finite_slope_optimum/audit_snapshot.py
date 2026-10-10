#!/usr/bin/env python3
"""R21 identity, exact replay and recorded-numerics audit; not a proof assistant."""
import sys
sys.dont_write_bytecode=True
import argparse,ast,hashlib,json,re,subprocess,tempfile
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path

HERE=Path(__file__).resolve().parent
RESEARCH=HERE.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def inspect():
    assert __debug__,'Do not run with -O.'
    baseline=read(HERE/'baseline.json');count=0
    assert len(baseline['manifest_sha256'])==21
    for rel,digest in baseline['manifest_sha256'].items():
        p=RESEARCH/rel;assert sha(p)==digest,rel
        for row in read(p)['files']:
            assert sha(p.parent/row['path'])==row['sha256'],(rel,row['path'])
            count+=1
    assert count==baseline['frozen_entries']==943
    inp=read(HERE/'inputs.json')
    assert inp['beta']=='1/4' and inp['target']=='1/8' and inp['domain']==['-1','1']
    assert inp['q0']=='1' and inp['q1']=='(x^2-1/4)*(1+beta*x)'
    assert inp['half_widths']==['1/5','1/10','1/20','1/50','1/100','1/200']
    assert inp['bisection_steps']==210
    certpath=HERE/'results/certificate.json';cert=read(certpath)
    algpath=HERE/'results/algebra.json';alg=read(algpath)
    assert cert['producer_sha256']==sha(HERE/'certify_example.py')
    assert cert['inputs_sha256']==sha(HERE/'inputs.json')
    assert cert['interval_substrate_sha256']==sha(HERE/'exact_interval.py')
    assert alg['source_sha256']==sha(HERE/'check_algebra.py')
    assert alg['interval_substrate_sha256']==sha(HERE/'exact_interval.py')
    assert alg['certificate_sha256']==sha(certpath)
    assert len(cert['rows'])==6 and sum(len(r['intervals']) for r in cert['rows'])==66
    assert alg['check_groups']==8 and len(alg['checks'])==8 and all(c['passed'] for c in alg['checks'])
    # Fresh output paths and a foreign cwd exercise portability and preserve frozen files.
    with tempfile.TemporaryDirectory(prefix='r21-exact-replay-') as tmp:
        tmp=Path(tmp);freshcert=tmp/'certificate.json';freshalg=tmp/'algebra.json'
        commands=[([str(HERE/'certify_example.py'),'--output',str(freshcert)],certpath,freshcert),
                  ([str(HERE/'check_algebra.py'),'--certificate',str(freshcert),'--output',str(freshalg)],algpath,freshalg)]
        for argv,recorded,fresh in commands:
            run=subprocess.run([sys.executable,'-B',*argv],cwd=tmp,capture_output=True,text=True)
            assert run.returncode==0,run.stdout+run.stderr
            assert sha(recorded)==sha(fresh),recorded.name
    quad=read(HERE/'results/quadrature.json')
    assert quad['source_sha256']==sha(HERE/'crosscheck_quadrature.py')
    assert quad['certificate_sha256']==sha(certpath) and quad['precisions']==[80,120]
    assert len(quad['rows'])==6
    compared=0
    for c,q in zip(cert['rows'],quad['rows']):
        assert c['a']==q['a'] and len(q['comparisons'])==7
        lo=q['lower_precision'];hi=q['higher_precision']
        assert lo['dps']==80 and hi['dps']==120
        assert F(lo['max_integral_residual'])<F('1e-60')
        assert F(hi['max_integral_residual'])<F('1e-100')
        assert lo['sampled_primitive_signs_passed']==hi['sampled_primitive_signs_passed']==38
        for key,value in hi['values'].items():
            value=F(value);a,b=map(F,c['intervals'][key])
            assert a<value<b,(c['a'],key)
            assert abs(value-F(lo['values'][key]))<F('1e-70')
            assert q['comparisons'][key]['inside_rational_interval']
            assert F(q['comparisons'][key]['precision_difference'])<F('1e-70')
            compared+=1
    assert compared==42
    plot=read(HERE/'results/plot_data.json');qa=read(HERE/'results/figure_qa.json')
    assert plot['certificate_sha256']==sha(certpath) and plot['plotter_sha256']==sha(HERE/'plot_results.py')
    assert len(plot['samples'])==360
    assert set(plot['figures'])=={'finite_optimum.png','finite_optimum.svg'}
    for name,digest in plot['figures'].items():assert sha(HERE/'figures'/name)==digest
    assert qa['png_sha256']==sha(HERE/'figures/finite_optimum.png')
    assert qa['visual_review']=='All three panels inspected after correcting overlapping logarithmic-axis labels.'
    assert qa['panels']==3 and qa['overlapping_tick_labels']==False and qa['clipped_text']==False
    table=(HERE/'results/NUMERICAL_TABLE.md').read_text()
    for row in cert['rows']:
        for k in ['amplitude','slope_budget','dual_coefficient','center_shift']:
            assert row['approximate_midpoints'][k] in table
    for doc,prefix,n in [('PROOF.md','T',17),('EXAMPLE.md','E',12)]:
        tags=re.findall(r'\\tag\{'+prefix+r'(\d+)\}',(HERE/doc).read_text())
        assert tags==[str(i) for i in range(1,n+1)],(doc,tags)
    assert len(re.findall(r'^\d+\. `',(HERE/'SEARCH_LOG.md').read_text(),re.M))==4
    for p in HERE.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))
    for p in HERE.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('http://','https://','#')):continue
            q=p.parent/target.split('#')[0]
            if q.name in ['audit_report.json','manifest.json'] and not q.exists():continue
            assert q.exists(),(str(p.relative_to(HERE)),target)
    return {'status':'R21_finite_slope_evidence_and_preservation_passed',
            'prior_manifests':21,'prior_frozen_file_entries':count,
            'exact_algebra_check_groups':8,'rational_example_widths':6,'rational_interval_records':66,
            'independent_precision_solves':12,'independent_values_compared':compared,
            'exact_replay_outputs_byte_identical':2,'general_equation_blocks':17,'example_equation_blocks':12,
            'scientific_figures':1,'figure_panels':3,'figure_formats':['PNG','SVG'],
            'previous_frozen_packages_modified':False,'manuscript_modified':False,
            'formal_proof':False,'external_referee_review':False,'novelty_priority_established':False,
            'new_theta_optimum_certificate':False,'general_fourth_order_coefficient':False,
            'public_release_or_submission':False,'audit_source_sha256':sha(Path(__file__)),
            'trust_boundary':'Analytic proof recorded separately. This audit verifies provenance, exact finite algebra, reproducible rational enclosures and recorded numerical comparisons; it does not automatically certify the theorem or originality.'}
def main():
    ap=argparse.ArgumentParser();group=ap.add_mutually_exclusive_group()
    group.add_argument('--preflight',action='store_true');group.add_argument('--freeze',action='store_true');args=ap.parse_args()
    result=inspect()
    if args.freeze:
        assert not (HERE/'manifest.json').exists(),'Already frozen.'
        result['closed_utc']=datetime.now(timezone.utc).isoformat()
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size}
               for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps({'created_utc':result['closed_utc'],
            'scope':'Compact finite-switch exact finite-slope optimum theorem and two-switch rational example; theta and higher-order extension open.',
            'files':files,'audit':result},indent=2)+'\n')
    elif not args.preflight:
        recorded=read(HERE/'audit_report.json')
        for k,v in result.items():assert recorded[k]==v,k
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {r['path'] for r in manifest['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='manifest.json'}
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
