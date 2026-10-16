"""Reconcile IPC, separate disk observations and receipts; no controller imports."""
from collections import Counter
import hashlib
import json
from pathlib import Path


def digest(data):
    return hashlib.sha256(data.encode() if isinstance(data,str) else data).hexdigest()


def load(path): return json.loads(Path(path).read_text())


def rows(path):
    data=[json.loads(line) for line in Path(path).read_text().splitlines()]
    if not data or [r['seq'] for r in data]!=list(range(1,len(data)+1)):
        raise ValueError('Missing/reordered journal: '+str(path))
    if len({(r['actor'],r['instance'],r['pid']) for r in data})!=1:
        raise ValueError('Journal process identity changed')
    return data


def inspect_data(plan, process, coord, source, receiver, observer, actual_files):
    """Invalid attribution leaves raw disk observations available, never a zero."""
    issues=[]
    def check(value,message):
        if not value: issues.append(message)
    snapshot_rows=[r for r in observer if r['kind']=='snapshot']
    snapshots={r['label']:r for r in snapshot_rows}
    check(len(snapshot_rows)==len(snapshots)==4 and set(snapshots)=={'initial','checkpoint','after_control','final'},'snapshot_inventory_mismatch')
    for snap in snapshot_rows:
        req=[r for r in coord if r['kind']=='observer_requested' and r['request_id']==snap['request_id']]
        ret=[r for r in coord if r['kind']=='observer_returned' and r['observation'].get('request_id')==snap['request_id']]
        check(len(req)==len(ret)==1,'observer_rpc_chain_missing')
        if len(req)==len(ret)==1:
            check(req[0]['label']==snap['label'] and ret[0]['observation']==snap,'observer_rpc_mismatch')
        for f in snap['files']:
            check(digest(f['content'])==f['sha256'] and len(f['content'].encode())==f['bytes'],'snapshot_bytes_mismatch')
    final=snapshots.get('final')
    raw={r:None for r in ('O','I','N','C')}
    correct=raw.copy()
    if final:
        files={f['path']:f for f in final['files']}
        for role in raw:
            f=files.get(role+'-final.json')
            raw[role]=f is not None
            correct[role]=bool(f and f['sha256']==plan['reference_payloads'][role]['sha256'])
        check(len(files)==len(final['files']),'duplicate_observer_path')
        check(files==actual_files,'observer_disk_mismatch')
    else: issues.append('final_observer_snapshot_missing')
    check(len({process[k]['pid'] for k in ('source','receiver','observer')} | {coord[0]['pid']})==4,'processes_not_distinct')
    for role,log in [('source',source),('receiver',receiver),('observer',observer)]:
        check(log and log[0]['pid']==process[role]['pid'],'process_pid_mismatch:'+role)
        check(process[role]['reaped'],'process_not_reaped:'+role)
    stopped=any(r['kind']=='source_stopped_and_reaped' for r in coord)
    check(process['source']['exit_code']==(-15 if stopped else 0),'unexpected_source_exit')
    check(all(process[r]['exit_code']==0 for r in ('receiver','observer')),'unclean_child_exit')
    check(process.get('episode_error') is None,'episode_execution_error')
    check(any(r['kind']=='receiver_closed' for r in receiver),'receiver_closure_missing')
    check(any(r['kind']=='observer_closed' for r in observer),'observer_closure_missing')
    requests=[r for r in receiver if r['kind']=='rpc_received']
    replies=[r for r in receiver if r['kind']=='rpc_replied']
    for client,channel in ((coord,'control'),(source,'source')):
        sent=[r for r in client if r['kind']=='rpc_sent']
        returned=[r for r in client if r['kind']=='rpc_returned']
        for r in sent:
            rid=r['request']['rpc_id']
            got=[x for x in requests if x['request']['rpc_id']==rid]
            done=[x for x in replies if x['rpc_id']==rid]
            back=[x for x in returned if x['rpc_id']==rid]
            check(len(got)==len(done)==len(back)==1,'rpc_chain_missing:'+rid)
            if len(got)==len(done)==len(back)==1:
                check(got[0]['request']==r['request'] and got[0]['channel']==channel,'rpc_request_mismatch:'+rid)
                check(done[0]['reply']==back[0]['reply'],'rpc_reply_mismatch:'+rid)
                check(done[0]['reply']['receiver_instance']==receiver[0]['instance'],'receiver_lifetime_mismatch')
    accepted=[r for r in receiver if r['kind']=='job_accepted']
    jobs={r['op']['operation_id']:r for r in accepted}
    check(len(jobs)==len(accepted)==4,'accepted_job_inventory_mismatch')
    receipts=[r for r in receiver if r['kind']=='native_write_receipt']
    denied=[r for r in receiver if r['kind']=='effect_denied']
    boundary=[r for r in receiver if r['kind']=='intervention_boundary']
    check(len(boundary)==1,'boundary_missing_or_ambiguous')
    boundaries=[r for r in coord if r['kind']=='causal_boundary_acknowledged']
    check(len(boundaries)==1,'coordinator_boundary_missing')
    if len(boundary)==len(boundaries)==1:
        check(boundary[0]['token']==boundaries[0]['token'] and boundary[0]['seq']==boundaries[0]['receiver_seq'],'boundary_link_mismatch')
    source_accept=[r for r in source if r['kind']=='acceptance_received']
    check(len(source_accept)==1,'source_acceptance_missing')
    if source_accept:
        ack=source_accept[0]['receipt']; job=jobs.get(ack['operation_id'])
        check(job is not None and job['op']['role']=='O','foreign_source_acceptance')
        if job:
            check(job['seq']==ack['acceptance_seq'] and job['op']['content_sha256']==ack['payload_sha256'],'acceptance_identity_mismatch')
    check(sorted(r['op']['role'] for r in accepted)==['C','I','N','O'],'role_inventory_mismatch')
    for oid,row in jobs.items():
        op=row['op']; role=op['role']
        if role not in plan['grants']:
            issues.append('unknown_grant:'+role); continue
        check(all(op.get(k)==v for k,v in plan['grants'][role].items()),'grant_mismatch:'+role)
        check(op['file_name']==role+'-final.json','unexpected_output_path:'+role)
        submitted=[r for r in requests if r['request']['action']=='submit' and r['request']['op'].get('operation_id')==oid]
        check(len(submitted)==1 and submitted[0]['request']['op']==op,'acceptance_submission_mismatch:'+role)
        check(digest(op['content'])==op['content_sha256'],'payload_hash_mismatch:'+role)
        lifecycle=[r for r in receiver if r.get('operation_id')==oid]
        starts=[r for r in lifecycle if r['kind']=='worker_entered']
        ends=[r for r in lifecycle if r['kind']=='worker_finished']
        effects=[r for r in receipts if r['operation_id']==oid]
        rejections=[r for r in denied if r['operation_id']==oid]
        check(len(starts)==len(ends)==1,'worker_lifecycle_gap:'+role)
        check(len(effects)+len(rejections)==1,'effect_disposition_gap:'+role)
        if len(starts)==len(ends)==1:
            check(row['seq']<starts[0]['seq']<ends[0]['seq'],'worker_order_mismatch:'+role)
        for rec in effects:
            check(rec['file_name']==op['file_name'] and rec['content_sha256']==op['content_sha256'],'receipt_identity_mismatch:'+role)
            check(rec['bytes']==len(op['content'].encode()),'receipt_byte_count_mismatch:'+role)
            attempts=[r for r in lifecycle if r['kind']=='native_write_attempt']
            check(len(attempts)==1 and attempts[0]['seq']<rec['seq'],'native_attempt_gap:'+role)
            f=(final and next((f for f in final['files'] if f['path']==rec['file_name']),None))
            check(f is not None and f['sha256']==rec['content_sha256'],'receipt_not_on_disk:'+role)
        if len(ends)==1:
            check(ends[0]['written']==bool(effects),'worker_receipt_mismatch:'+role)
    for rec in receipts+denied:
        check(rec['operation_id'] in jobs,'unattributed_disposition')
    if final:
        for f in final['files']:
            check(digest(f['content'])==f['sha256'] and len(f['content'].encode())==f['bytes'],'observer_byte_mismatch')
            check(any(r['file_name']==f['path'] and r['content_sha256']==f['sha256'] for r in receipts),'observed_file_without_receipt:'+f['path'])
    checkpoints=[r for r in coord if r['kind']=='checkpoint']
    timing=False
    if len(checkpoints)==1 and 'checkpoint' in snapshots:
        cp=checkpoints[0]; o=cp['roles']['O']; i=cp['roles']['I']
        timing=(o['state']==plan['condition']['cut'] and not o['done'] and i['state']=='claimed_before_effect' and not i['done'])
        cp_files={f['path'] for f in snapshots['checkpoint']['files']}
        timing=timing and ('O-final.json' in cp_files)==(plan['condition']['cut']=='after_effect_before_completion') and 'I-final.json' not in cp_files
    else: issues.append('checkpoint_evidence_missing')
    outcome=dict(final_files_observed=raw,final_payload_matches_reference=correct,
                 timing_matched=timing,source_was_stopped=stopped,
                 source_terminal_while_receiver_O_pending=None,
                 O_receipts_after_boundary=None,C_receipts_after_boundary=None,
                 cancel_disposition=[r['status'] for r in receiver if r['kind']=='cancel_response'],
                 revocation_claim_but_old_effect_observed=None)
    pending=[r for r in coord if r['kind']=='receiver_after_source_exit']
    if stopped and len(pending)==1:
        outcome['source_terminal_while_receiver_O_pending']=not pending[0]['old_job']['done']
    elif stopped: issues.append('receiver_liveness_after_source_exit_missing')
    if not issues and len(boundary)==1:
        for role in ('O','C'):
            outcome[role+'_receipts_after_boundary']=(sum(jobs[r['operation_id']]['op']['role']==role and r['seq']>boundary[0]['seq'] for r in receipts) if stopped else None)
        rev=[r for r in receiver if r['kind']=='revocation_response']
        if rev:
            outcome['revocation_claim_but_old_effect_observed']=any(jobs[r['operation_id']]['op']['origin']==plan['grants']['O']['origin'] and r['seq']>rev[0]['seq'] for r in receipts)
    if issues:
        outcome['final_payload_matches_reference']={role:None for role in raw}
    return dict(status='recorded' if not issues else 'needs_review',evidence_valid=not issues,
                evidence_issues=issues,outcomes=outcome,
                observation_scope='persistent create-only files at declared snapshots',
                control_success_is_not_evidence_validity=True,actual_provider_calls=0)


def audit(folder):
    folder=Path(folder)
    try:
        logs={name:rows(folder/(name+'.jsonl')) for name in ('coordinator','source','receiver','observer')}
        actual={}
        for p in sorted((folder/'store').rglob('*')):
            if p.is_symlink(): raise ValueError('Unexpected store symlink')
            if not p.is_file(): continue
            b=p.read_bytes(); key=str(p.relative_to(folder/'store'))
            actual[key]=dict(path=key,bytes=len(b),sha256=digest(b),content=b.decode())
        return inspect_data(load(folder/'PLAN.json'),load(folder/'PROCESS.json'),logs['coordinator'],logs['source'],logs['receiver'],logs['observer'],actual)
    except Exception as exc:
        disk={}
        for name in ('O-final.json','I-final.json','N-final.json','C-final.json'):
            p=folder/'store'/name
            try:
                disk[name]=(dict(present=True,sha256=digest(p.read_bytes())) if p.is_file() and not p.is_symlink()
                            else dict(present=False) if not p.exists() else dict(present=None,error='nonregular_or_symlink'))
            except Exception as issue:
                disk[name]=dict(present=None,error=type(issue).__name__)
        return dict(status='needs_review',evidence_valid=False,evidence_issues=[type(exc).__name__+': '+str(exc)],
                    outcomes=None,raw_disk_by_declared_name=disk,
                    raw_disk_is_trusted_origin_attribution=False,actual_provider_calls=0)
