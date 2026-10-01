"""Compare fresh measured records without forcing unheld race outcomes to match."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--id',required=True);parser.add_argument('--report',default='report-v02')
    args=parser.parse_args()
    if not args.id.startswith('clean-v') or not args.id[7:].isdigit():raise ValueError('Clean reproduction identifier required')
    original=ROOT/'reports'/args.report
    reproduction=ROOT/'reproductions'/args.id
    copied=reproduction/'lab/stop_contract_study'
    repeated=copied/'reports/report-clean-v01'
    outcome=read(reproduction/'REPRODUCTION.json')
    if not outcome['success'] or not outcome['bundle_unchanged']:raise RuntimeError('Fresh execution incomplete or bundle changed')
    left,right=read(original/'SUMMARY.json'),read(repeated/'SUMMARY.json')
    if not left['all_evidence_valid'] or not right['all_evidence_valid']:raise RuntimeError('Invalid evidence cannot be compared as outcomes')
    if left['paired_input_sha256']!=right['paired_input_sha256']:raise RuntimeError('Fresh experiment source bytes differ')
    lp,rp=read(original/'PROVENANCE.json'),read(repeated/'PROVENANCE.json')
    if lp['auditor_sha256']!=rp['auditor_sha256'] or lp['builder_sha256']!=rp['builder_sha256']:raise RuntimeError('Analysis implementation changed')
    cells=read(ROOT/'matrices'/left['matrix']/'PLAN.json')['cells']
    repeated_cells=read(copied/'matrices'/right['matrix']/'PLAN.json')['cells']
    if cells!=repeated_cells:raise RuntimeError('Matrix designs differ')
    comparison=[];controlled_differences=[];unheld_differences=[]
    for cell in cells:
        name=cell['run_id'];a=read(original/'audits'/f'{name}.json');b=read(repeated/'audits'/f'{name}.json')
        la={n:v['status'] for n,v in a['outcomes'].items()};lb={n:v['status'] for n,v in b['outcomes'].items()}
        changes={n:{'original':la.get(n),'fresh':lb.get(n)} for n in la.keys()|lb.keys() if la.get(n)!=lb.get(n)}
        entry={**cell,'outcome_statuses_match':not changes,'differences':changes,
               'original_audit_sha256':sha(original/'audits'/f'{name}.json'),'fresh_audit_sha256':sha(repeated/'audits'/f'{name}.json')}
        comparison.append(entry)
        if changes:(unheld_differences if cell['schedule']=='unheld' else controlled_differences).append(entry)
        lm=read(ROOT/'runs'/name/'manifest.json');rm=read(copied/'runs'/name/'manifest.json')
        if lm['source_sha256']!=rm['source_sha256'] or lm['locked_packages']!=rm['locked_packages']:raise RuntimeError('Environment/source mismatch in '+name)
    record={'completed_utc':datetime.now(timezone.utc).isoformat(),'scope':'same host/base Python; fresh installed environment and relocated source, not independent operator',
            'fresh_execution_success':True,'same_paired_input_bytes':True,'same_instrumentation_and_lock':True,
            'controlled_cells':sum(c['schedule']!='unheld' for c in cells),'unheld_cells':sum(c['schedule']=='unheld' for c in cells),
            'controlled_differences':controlled_differences,'unheld_differences':unheld_differences,
            'all_controlled_outcomes_match':not controlled_differences,'cells':comparison,
            'original_summary_sha256':sha(original/'SUMMARY.json'),'fresh_summary_sha256':sha(repeated/'SUMMARY.json'),
            'reproduction_sha256':sha(reproduction/'REPRODUCTION.json')}
    target=reproduction/'COMPARISON.json'
    with target.open('x') as f:json.dump(record,f,indent=2)
    print(json.dumps({'comparison':str(target),'controlled_differences':len(controlled_differences),'unheld_differences':len(unheld_differences)}))
    return 0 if not controlled_differences else 1
if __name__=='__main__':raise SystemExit(main())
