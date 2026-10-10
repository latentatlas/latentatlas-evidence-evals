#!/usr/bin/env python3
"""Verify provenance and preserve a deliberate, immutable R05 snapshot.

Without --freeze this is read-only. --freeze refuses to overwrite an
existing manifest; it is intended only for a deliberately new snapshot.
"""
import argparse
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
if not __debug__:raise RuntimeError('Run without -O/-OO')
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def require(ok,msg):
    if not ok:raise ArithmeticError(msg)
def verify_source(record,name):
    require(record['source_sha256']==sha(HERE/name),f'Source changed: {name}')


def audit():
    packages=[]
    for name in ('cusp_verified','cusp_region','cusp_connection','cusp_geometry'):
        base=HERE.parent/name;manifest=read(base/'manifest.json')
        for entry in manifest['files']:
            require(sha(base/entry['path'])==entry['sha256'],f'Frozen input changed: {name}/{entry["path"]}')
        packages.append({'package':name,'manifest_sha256':sha(base/'manifest.json'),
                         'verified_files':len(manifest['files'])})
    original=read(HERE.parent/'cusp_verified/manifest.json')['original_files']
    for entry in original:
        require(sha(Path(entry['path']))==entry['sha256'],f'Original changed: {entry["path"]}')
    wpath=HERE/'results/width_certificate.json';epath=HERE/'results/endpoint_folds.json'
    w=read(wpath);e=read(epath)
    require(w['status']=='strict_nesting_and_finite_width_monotonicity_passed' and len(w['cells'])==58,'Width result incomplete')
    require(w['input_packages']==packages and e['input_packages']==packages,'Input provenance mismatch')
    for n,h in w['source_sha256'].items():require(sha(HERE/n)==h,f'Width source changed: {n}')
    require(sha(HERE.parent/'cusp_connection/results/connection_certificate.json')==w['connection_certificate_sha256'],'R03 link stale')
    require(sha(HERE.parent/'cusp_geometry/results/geometry_certificate.json')==w['geometry_certificate_sha256'],'R04 link stale')
    r=read(HERE/'results/rational_check.json');verify_source(r,'check_width.py')
    require(r['certificate_sha256']==sha(wpath) and r['cells_checked']==58,'Rational report stale')
    require(r['status']=='rational_ode_and_finite_width_checks_passed','Rational check failed')
    verify_source(e,'endpoint_folds.py')
    require(e['status']=='128_endpoint_fold_contractions_passed' and len(e['samples'])==32,'Endpoint certificate incomplete')
    ec=read(HERE/'results/endpoint_check.json');verify_source(ec,'check_endpoints.py')
    require(ec['certificate_sha256']==sha(epath) and len(ec['checks'])==128,'Endpoint check stale')
    require(ec['interval_arithmetic_sha256']==sha(HERE/'check_width.py'),'Endpoint arithmetic changed')
    require(ec['status']=='128_endpoint_rational_contraction_checks_passed','Endpoint check failed')
    tests=read(HERE/'results/test_report.json')
    require(tests['status']=='passed' and tests['test_groups']==5 and tests['direct_integral_comparisons']==96,'Tests incomplete')
    for n,h in tests['source_sha256'].items():require(sha(HERE/n)==h,f'Tested source changed: {n}')
    require(tests['certificate_sha256']==sha(wpath) and tests['endpoint_certificate_sha256']==sha(epath),'Test inputs stale')
    mp=read(HERE/'results/independent_check.json');verify_source(mp,'check_independent.py')
    require(mp['certificate_sha256']==sha(wpath) and mp['derivative_comparisons']==27,'Numerical support stale')
    require(mp['status']=='independent_transport_numerical_checks_passed','Numerical comparison failed')
    require(mp['connection_certificate_sha256']==w['connection_certificate_sha256'],'mpmath R03 input changed')
    require(mp['integrator_sha256']==sha(HERE.parent/'cusp_connection/check_independent.py'),'mpmath integrator changed')
    plot=read(HERE/'results/plot_metadata.json');verify_source(plot,'plot_paper.py')
    for n,h in plot['inputs'].items():require(sha(HERE.parent/n)==h,f'Plot input stale: {n}')
    for n,h in plot['outputs'].items():require(sha(HERE/n)==h,f'Plot output changed: {n}')
    qa=read(HERE/'results/figure_qa.json')
    require(qa['all_fonts_embedded'] and qa['visual_review_completed'],'Figure QA incomplete')
    for n,h in qa['pdf_sha256'].items():require(sha(HERE/n)==h,f'Reviewed PDF changed: {n}')
    return {'status':'all_snapshot_links_and_preservation_checks_passed',
            'input_packages':packages,'original_files_unchanged':len(original),
            'width_cells':58,'endpoint_fold_contractions':128,
            'test_groups':5,'direct_integral_comparisons':96,
            'mpmath_derivative_comparisons':27,'paper_figures':2,
            'source_sha256':sha(Path(__file__)),
            'trust_boundary':'Provenance and preservation audit; does not replace mathematical review or reintegration.',
            'ongoing_notebook':'../CALISMA_DEFTERI.md is intentionally outside this frozen snapshot.'}


def files():
    return [p for p in sorted(HERE.rglob('*')) if p.is_file()
            and '__pycache__' not in p.parts and 'tmp' not in p.relative_to(HERE).parts
            and p.name not in ('manifest.json','.DS_Store')]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');args=ap.parse_args()
    report=audit();mp=HERE/'manifest.json'
    if args.freeze:
        if mp.exists():raise RuntimeError('Snapshot already frozen; use a deliberate new copy/version, not an overwrite.')
        (HERE/'results/audit_report.json').write_text(json.dumps(report,indent=2)+'\n')
        manifest={'created_utc':datetime.now(timezone.utc).isoformat(),
                  'scope':'R05 finite-width monotonicity and centered nesting, nu in [-29,0], 0<ell<=1e-6; two paper figures.',
                  'audit':report,'files':[{'path':str(p.relative_to(HERE)),'sha256':sha(p)} for p in files()]}
        mp.write_text(json.dumps(manifest,indent=2)+'\n')
        print('Frozen R05 files:',len(manifest['files']))
    else:
        manifest=read(mp)
        recorded={e['path']:e['sha256'] for e in manifest['files']}
        actual={str(p.relative_to(HERE)):sha(p) for p in files()}
        require(recorded==actual,'R05 snapshot changed or has unrecorded files')
        require(manifest['audit']==report,'Snapshot audit differs')
        print('Verified R05 files:',len(recorded))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
