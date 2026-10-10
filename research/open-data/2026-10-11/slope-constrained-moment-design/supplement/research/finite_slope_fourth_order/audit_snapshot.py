#!/usr/bin/env python3
"""R22 evidence/provenance audit. Analytic asymptotics are documented separately."""
import sys
sys.dont_write_bytecode=True
import argparse,ast,hashlib,json,re,subprocess,tempfile
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path

HERE=Path(__file__).resolve().parent;RESEARCH=HERE.parent;PREV=RESEARCH/'finite_slope_optimum'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def inspect():
    assert __debug__,'Assertions must be enabled.'
    baseline=read(HERE/'baseline.json');n=0
    assert len(baseline['manifest_sha256'])==22
    for rel,digest in baseline['manifest_sha256'].items():
        p=RESEARCH/rel;assert sha(p)==digest,rel
        for row in read(p)['files']:
            assert sha(p.parent/row['path'])==row['sha256'],(rel,row['path'])
            n+=1
    assert n==baseline['frozen_entries']==968
    cp=HERE/'results/certificate.json';ap=HERE/'results/algebra.json'
    cert=read(cp);alg=read(ap);quad=read(HERE/'results/integrals.json')
    assert cert['source_sha256']==sha(HERE/'certify_fourth_order.py')
    assert cert['R21_certificate_sha256']==sha(PREV/'results/certificate.json')
    assert cert['R21_producer_sha256']==sha(PREV/'certify_example.py')
    assert cert['rational_interval_source_sha256']==sha(PREV/'exact_interval.py')
    assert cert['R21_fresh_replay_identical']
    assert alg['source_sha256']==sha(HERE/'check_fourth_order.py')
    assert alg['direct_integral_helper_sha256']==sha(PREV/'exact_interval.py')
    assert alg['check_groups']==len(alg['checks'])==12 and all(r['passed'] for r in alg['checks'])
    for case in ['two_switch','negative_C4']:
        for key in ['C2','C4']:assert cert['coefficients'][case][key]==alg[case][key]
    for key in ['fractional_exponent','fractional_coefficient']:
        assert cert['coefficients']['C2_only'][key]==alg['C2_only'][key]
    assert F(cert['coefficients']['two_switch']['C4'])==F(253,49152)
    assert F(cert['coefficients']['negative_C4']['C4'])==F(-1,15360)
    assert alg['matrix_stress_test']['not_an_additional_integral_example']
    with tempfile.TemporaryDirectory(prefix='r22-exact-replay-') as tmp:
        tmp=Path(tmp)
        for script,recorded,name in [('check_fourth_order.py',ap,'algebra.json'),
                                     ('certify_fourth_order.py',cp,'certificate.json')]:
            fresh=tmp/name
            run=subprocess.run([sys.executable,'-B',str(HERE/script),'--output',str(fresh)],cwd=tmp,capture_output=True,text=True)
            assert run.returncode==0,run.stdout+run.stderr
            assert sha(fresh)==sha(recorded),name
    assert len(cert['rows'])==len(quad['rows'])==16
    assert quad['source_sha256']==sha(HERE/'crosscheck_integrals.py')
    assert quad['R21_integral_solver_sha256']==sha(PREV/'crosscheck_quadrature.py')
    assert quad['certificate_sha256']==sha(cp) and quad['precisions']==[90,130]
    counts={};compared=0;improved=0
    for cr,qr in zip(cert['rows'],quad['rows']):
        assert cr['case']==qr['case'] and cr['a']==qr['a']
        counts[cr['case']]=counts.get(cr['case'],0)+1
        assert set(cr['intervals'])==set(qr['checks'])==set(qr['high']['values'])
        assert qr['low']['dps']==90 and qr['high']['dps']==130
        assert F(qr['low']['max_moment_balance_residual'])<F('1e-70')
        assert F(qr['high']['max_moment_balance_residual'])<F('1e-110')
        for key,value in qr['high']['values'].items():
            lo,hi=map(F,cr['intervals'][key]);value=F(value)
            assert lo<value<hi,(cr['case'],cr['a'],key)
            assert (2**180)%lo.denominator==0 and (2**180)%hi.denominator==0
            assert abs(value-F(qr['low']['values'][key]))<F('1e-70')
            assert qr['checks'][key]['inside_rational_interval']
            assert F(qr['checks'][key]['precision_difference'])<F('1e-70')
            compared+=1
        if 'error_ratio' in cr['intervals']:
            lo,hi=map(F,cr['intervals']['error_ratio']);assert 0<lo<hi<1;improved+=1
    assert counts=={'two_switch':6,'negative_C4':6,'C2_only':4}
    assert compared==132 and improved==12
    plot=read(HERE/'results/plot_data.json');qa=read(HERE/'results/figure_qa.json')
    assert plot['certificate_sha256']==sha(cp) and plot['source_sha256']==sha(HERE/'plot_results.py')
    assert plot['sample_precision_digits']==80 and sum(map(len,plot['curves'].values()))==540
    assert set(plot['figures'])=={'fourth_order.png','fourth_order.svg'}
    for name,digest in plot['figures'].items():assert sha(HERE/'figures'/name)==digest
    assert qa['png_sha256']==sha(HERE/'figures/fourth_order.png')
    assert qa['panels']==3 and qa['visual_review']=='All three panels inspected; signs, scientific-axis multipliers, legends and scope caption are readable.'
    assert not qa['clipped_text'] and not qa['overlapping_tick_labels']
    table=(HERE/'results/TABLE.md').read_text()
    for row in cert['rows']:
        for key in ['slope_budget','scaled_fourth_residual']:
            assert format(float(row['approximate_midpoints'][key]),'.10g') in table
    for doc,prefix,num in [('PROOF.md','F',18),('EXAMPLES.md','E',8)]:
        tags=re.findall(r'\\tag\{'+prefix+r'(\d+)\}',(HERE/doc).read_text())
        assert tags==list(map(str,range(1,num+1))),(doc,tags)
    assert len(re.findall(r'^\d+\. `',(HERE/'SEARCH_LOG.md').read_text(),re.M))==3
    for p in HERE.rglob('*'):
        if p.is_file() and p.suffix in ['.md','.py','.json','.txt']:
            assert all(c>=32 or c in (9,10,13) for c in p.read_bytes()),p.name
        if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
    assert not list(HERE.rglob('*.pyc')) and not list(HERE.rglob('__pycache__'))
    for p in HERE.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('http://','https://','#')):continue
            q=p.parent/target.split('#')[0]
            if q.name in ['audit_report.json','manifest.json'] and not q.exists():continue
            assert q.exists(),(p.name,target)
    return {'status':'R22_fourth_order_evidence_and_preservation_passed',
        'prior_manifests':22,'prior_frozen_file_entries':n,
        'exact_algebra_check_groups':12,'sample_budgets':16,'rational_interval_records':132,
        'independent_precision_runs':32,'independent_values_compared':132,
        'sampled_smooth_budgets_with_lower_approximation_error':12,
        'exact_replay_outputs_byte_identical':2,'general_equation_blocks':18,'example_equation_blocks':8,
        'scientific_figures':1,'figure_panels':3,'theta_fourth_order_certificate':False,
        'uniform_numerical_fourth_order_remainder_bound':False,
        'previous_frozen_packages_modified':False,'manuscript_modified':False,
        'formal_proof':False,'external_referee_review':False,'novelty_priority_established':False,
        'public_release_or_submission':False,'audit_source_sha256':sha(Path(__file__)),
        'trust_boundary':'Exact finite algebra, pointwise rational enclosures, reproducibility and recorded numerical comparisons. Analytic remainders and originality are not automatically certified.'}
def main():
    parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group()
    g.add_argument('--preflight',action='store_true');g.add_argument('--freeze',action='store_true');args=parser.parse_args()
    result=inspect()
    if args.freeze:
        assert not (HERE/'manifest.json').exists(),'Already frozen.'
        result['closed_utc']=datetime.now(timezone.utc).isoformat()
        (HERE/'audit_report.json').write_text(json.dumps(result,indent=2)+'\n')
        files=[{'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size}
               for p in sorted(HERE.rglob('*')) if p.is_file()]
        (HERE/'manifest.json').write_text(json.dumps({'created_utc':result['closed_utc'],
            'scope':'Finite-switch fourth-order coefficient, moment penalty and regularity/sign counterexamples. No infinite-tail/theta extension.',
            'files':files,'audit':result},indent=2)+'\n')
    elif not args.preflight:
        recorded=read(HERE/'audit_report.json')
        for key,val in result.items():assert recorded[key]==val,key
        manifest=read(HERE/'manifest.json')
        for row in manifest['files']:assert sha(HERE/row['path'])==row['sha256'],row['path']
        assert {r['path'] for r in manifest['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='manifest.json'}
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
