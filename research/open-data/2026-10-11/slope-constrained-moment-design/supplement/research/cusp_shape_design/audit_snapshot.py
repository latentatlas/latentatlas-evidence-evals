#!/usr/bin/env python3
"""R09 provenance closure and once-only immutable snapshot."""
import argparse,hashlib,json,re,struct,subprocess,sys
from datetime import datetime,timezone
from fractions import Fraction as Q
from pathlib import Path
from xml.etree import ElementTree
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PREVIOUS={
 'cusp_verified':'345ef0004aad060f9d7746f6a085126b4e857937384dbe29dc298be3578c7b96',
 'cusp_region':'62da00f67be0c34236b8529f2377258991c0320ee9bc7f1ab882c39e3cfafbe5',
 'cusp_connection':'45ee9d3d287fad9bbf6752d144de9bd6257c07649ba8e4c9f57a3ca2e387fdd1',
 'cusp_geometry':'b3a1846431be58d2f3c5d45749f218aa4efebaca431e3ebd2ffe454ff7e22621',
 'cusp_width':'eb7847154285acfa09fecb73aece53863409e29c62ed8045bde87f4974cf6dc8',
 'cusp_literature':'2d48fc9cfa5e40c376e1adf8f09b6ff62f9312dc515787d4dba37745d1bf40ab',
 'cusp_robustness':'0036bd2da3d52098743149eb645e934a088bb7a437d72cfa8e97ef7d326489c6',
 'cusp_pinned_family':'b8119dd3f334ab697a7cf3f31ba18c515c0315bcf70a5a706b25dbb406a95aad'}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,msg):
    if not v:raise ArithmeticError(msg)
def read(p):return json.loads((HERE/p).read_text())
def sources(d,name=None):
    s=d['source_sha256']
    if isinstance(s,dict):
        for n,h in s.items():need(sha(HERE/n)==h,'Changed source '+n)
    else:need(name is not None and sha(HERE/name)==s,'Changed source '+str(name))
def upstream(d):
    for n,h in d['input_sha256'].items():need(sha(HERE/'results'/n)==h,'Changed result input '+n)
def pair(d,key,path):need(d[key]==sha(path),'Stale input '+key)
def own_files():return [p for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts]


def audit():
    packages=[]
    for name,h in PREVIOUS.items():
        base=HERE.parent/name;mp=base/'manifest.json'
        need(sha(mp)==h,'Changed frozen manifest '+name)
        manifest=json.loads(mp.read_text())
        for row in manifest['files']:need(sha(base/row['path'])==row['sha256'],'Changed frozen file '+name+'/'+row['path'])
        packages.append({'package':name,'manifest_sha256':h,'files':len(manifest['files'])})
    originals=json.loads((HERE.parent/'cusp_verified/manifest.json').read_text())['original_files']
    for row in originals:need(sha(row['path'])==row['sha256'],'Changed original '+row['path'])
    prior=subprocess.run([sys.executable,str(HERE.parent/'cusp_pinned_family/audit_snapshot.py')],capture_output=True,text=True,check=True)
    need('r08_evidence_links_and_preservation_checks_passed' in prior.stdout,'Previous chain audit failed')
    qpath=HERE.parent/'cusp_verified/results/quartic_cusp_certificate.json';q=json.loads(qpath.read_text())
    dictionary=read('results/dictionary_16.json');sources(dictionary,'moment_dictionary.py')
    need(dictionary['status']=='rigorous_Q_cosine_moment_dictionary','Dictionary status')
    need(dictionary['input_packages']==packages,'Dictionary frozen input identity')
    pair(dictionary,'quartic_certificate_sha256',qpath)
    need(dictionary['max_frequency']==16 and dictionary['orders']==list(range(9)),'Dictionary scope')
    need([r['frequency'] for r in dictionary['rows']]==list(range(1,17)),'Dictionary frequency identity')
    need(all(len(r['moments'])==9 and len(r['shifted_integrals'])==9 and all(len(p)==2 for p in r['shifted_integrals']) for r in dictionary['rows']),'Incomplete dictionary')
    design=read('results/design_certificate.json');sources(design,'certify_design.py')
    need(design['status']=='exact_pinned_direction_dual_optimality_and_quartic_boundary_certified','Design status')
    need(design['input_packages']==packages and design['frequencies']==[10,13,15,16],'Design identity')
    pair(design,'dictionary_sha256',HERE/'results/dictionary_16.json');pair(design,'quartic_certificate_sha256',qpath)
    dcheck=read('results/design_check.json');sources(dcheck,'check_design.py')
    need(dcheck['status']=='rational_exact_pinning_dual_optimality_and_quartic_rank_passed','Design checker status')
    pair(dcheck,'certificate_sha256',HERE/'results/design_certificate.json');pair(dcheck,'dictionary_sha256',HERE/'results/dictionary_16.json')
    need(Q(dcheck['smallest_inactive_dual_margin'])>Q('10.51'),'Wrong dual margin')
    need(Q(dcheck['quartic_control_determinant'][1])<0 and Q(dcheck['quartic_fourth_derivative'][1])<0,'Unresolved quartic nondegeneracy')
    jets=read('results/local_jets.json');sources(jets)
    need(jets['input_packages']==packages and jets['center']==q['center_exact_dyadic'] and jets['root_radius']==q['root_radius'],'Wrong exact Q provenance')
    pair(jets,'design_certificate_sha256',HERE/'results/design_certificate.json')
    need(jets['status']=='55_direct_F_and_H_jets_with_exact_Q_enclosures','Jet status')
    need(all(len(jets[n])==55 for n in ('F_at_center','H_at_center','F_at_exact_Q','H_at_exact_Q')) and len(jets['absolute_F_bounds'])==59,'Incomplete direct jets')
    need(jets['direct_shift_crosschecks']==9,'Missing integral identity checks')
    cert=read('results/local_certificate.json');sources(cert)
    pair(cert,'jet_certificate_sha256',HERE/'results/local_jets.json')
    need(cert['status']=='uniform_fixed_Q_finite_geometry_and_nesting_passed' and cert['slab_count']==16,'Local continuum status')
    need([r['index'] for r in cert['cells']]==list(range(16)),'Incomplete amplitude coverage')
    rat=read('results/local_check.json');sources(rat,'check_local.py')
    pair(rat,'certificate_sha256',HERE/'results/local_certificate.json');pair(rat,'jet_certificate_sha256',HERE/'results/local_jets.json')
    need(rat['status']=='rational_Taylor_geometry_and_finite_transport_passed','Rational local status')
    need((rat['cells'],rat['adjacent_joins'])==(16,15) and rat['rate_bounds']==['10','500'],'Rational local scope')
    samples=read('results/fold_samples.json');sources(samples)
    pair(samples,'jet_certificate_sha256',HERE/'results/local_jets.json')
    pair(samples,'reference_kernel_certificate_sha256',HERE.parent/'cusp_robustness/results/pinned_cusp_certificate.json')
    need(samples['status']=='176_finite_fold_contractions_with_equal_amplitude_comparison_passed','Sample status')
    need(len(samples['models'])==11 and len(samples['samples'])==88 and len(samples['comparisons'])==16,'Sample count')
    need({(s['model'],s['j']) for s in samples['samples']}=={(i,j) for i in range(11) for j in range(1,9)},'Missing/duplicate finite samples')
    need(len(samples['reference_H_at_center'])==34 and len(samples['reference_H_at_exact_Q'])==34,'Reference jet scope')
    sc=read('results/sample_check.json');sources(sc,'check_samples.py');pair(sc,'certificate_sha256',HERE/'results/fold_samples.json')
    need(sc['status']=='176_rational_fold_contractions_and_16_width_comparisons_passed','Rational sample status')
    need((sc['fold_contractions'],sc['finite_width_comparisons'])==(176,16),'Rational sample scope')
    boundary=read('results/boundary_certificate.json');sources(boundary,'certify_boundaries.py')
    pair(boundary,'design_certificate_sha256',HERE/'results/design_certificate.json');pair(boundary,'design_check_sha256',HERE/'results/design_check.json')
    need(boundary['status']=='rational_boundary_signs_and_prescribed_opening_corollary_passed','Boundary status')
    cross=read('results/integral_crosscheck.json');sources(cross,'crosscheck_integrals.py');upstream(cross)
    need(cross['status']=='9_independent_direct_moments_at_two_precisions_passed','Separate quadrature status')
    need([r['order'] for r in cross['rows']]==list(range(9)) and all(r['dps']==[90,115] and r['inside_rigorous_center_ball'] for r in cross['rows']),'Separate quadrature scope')
    summary=read('results/key_results.json');sources(summary,'summarize_results.py');upstream(summary)
    proof=(HERE/'PROOF.md').read_text().replace('\u2212','-')
    tex=(HERE/'THEOREM_APPENDIX.tex').read_text().replace('\u2212','-')
    for key in ('a','b','S','selected_finite_W_change_percent','reference_finite_W_change_percent',
                'selected_leading_C_change_percent','mu_unfolding_boundary','quartic_boundary',
                'quartic_fourth_derivative_times_1e12','quartic_control_det_times_1e38'):
        for number in summary[key]:need(number in proof and number in tex,'Manually copied number mismatch '+key)
    diag1=read('diagnostics/local_16_sample.json');sources(diag1)
    diag2=read('diagnostics/local_16_sample_v2.json');sources(diag2)
    need(any(r.get('status')=='bound_not_proved' for r in diag1['cells']),'Missing original failed bound')
    need(all(r.get('status')!='bound_not_proved' for r in diag2['cells']),'Failed v2 sample')
    search=read('diagnostics/search_16.json');sources(search,'explore_directions.py')
    pair(search,'dictionary_sha256',HERE/'results/dictionary_16.json')
    need(search['status']=='numerical_candidate_search_only' and search['candidate_count']==1820,'Exploration scope')
    plot=read('figures/metadata.json');sources(plot,'plot_results.py');upstream(plot)
    for n,h in plot['files'].items():need(sha(HERE/'figures'/n)==h,'Changed plot '+n)
    visual=read('figures/visual_review.json')
    need(visual['status']=='visually_reviewed','Missing visual review')
    for n,h in visual['files'].items():need(sha(HERE/'figures'/n)==h,'Stale visual review')
    for name in ('finite_shape_design','opening_boundaries'):
        p=HERE/'figures'/(name+'.png')
        need(struct.unpack('>II',p.read_bytes()[16:24])==(2280,1064),'Figure dimensions')
        need(ElementTree.parse(HERE/'figures'/(name+'.svg')).getroot().tag.endswith('svg'),'Invalid SVG')
    links=0
    for p in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^\n]+?)\)',p.read_text()):
            if target.startswith(('https://','http://','#')):continue
            path=p.parent/target.split('#',1)[0]
            need(path.exists() or path in (HERE/'manifest.json',HERE/'audit_report.json'),'Broken local link '+str(path));links+=1
    for p in HERE.glob('*.tex'):
        depth=0
        for c in p.read_text():
            depth+=(c=='{')-(c=='}');need(depth>=0,'TeX brace ordering '+p.name)
        need(depth==0,'TeX braces '+p.name)
    for p in HERE.glob('*.py'):compile(p.read_text(),str(p),'exec')
    need(not list(HERE.rglob('__pycache__')),'Unrecorded Python cache')
    return {'status':'r09_evidence_links_and_preservation_checks_passed',
        'preserved_packages':packages,'preserved_scientific_files':sum(r['files'] for r in packages),
        'preserved_original_files':len(originals),'previous_chain_audit':'passed',
        'rigorous_shift_integrals':288,'direct_F_H_integrals':110,'reference_H_integrals':34,
        'exact_Q_H_shift_comparisons':9,'exact_Q_F_old_certificate_comparisons':9,
        'independent_mpmath_moments_two_precisions':9,'finite_dictionary_modes':16,
        'dual_optimality_and_quartic_rank':'rational_check_passed','amplitude_cells':16,'uniqueness_joins':15,
        'finite_fold_contractions':176,'equal_amplitude_width_comparisons':16,
        'figures_visually_reviewed':2,'local_links_checked':links,'latex_compiled':False,
        'external_mathematical_review':False,'literature_priority_established':False,
        'scope':'New direction: exact pinned Q at nu=0. Finite window only for |epsilon|<=1/128. Quartic zero in a modified kernel, not the original fixed-Phi family.',
        'trust_boundary':'See PROOF.md section 6 and checker reports. This provenance audit does not itself prove integral enclosures or replace mathematical review.',
        'audit_source_sha256':sha(__file__)}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--preflight',action='store_true');args=ap.parse_args()
    need(not (args.freeze and args.preflight),'Choose freeze or preflight')
    path=HERE/'manifest.json'
    if args.freeze:need(not path.exists(),'R09 already frozen')
    report=audit()
    if args.freeze:
        (HERE/'audit_report.json').write_text(json.dumps(report,indent=2)+'\n')
        data={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':report['scope'],
            'audit':report,'files':[{'path':str(p.relative_to(HERE)),'sha256':sha(p)} for p in own_files()]}
        with path.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
    elif not args.preflight:
        data=json.loads(path.read_text());need(data['audit']==report,'Audit report changed')
        need({r['path']:r['sha256'] for r in data['files']}=={str(p.relative_to(HERE)):sha(p) for p in own_files()},'Unrecorded or changed R09 files')
    print(json.dumps(report,indent=2))
