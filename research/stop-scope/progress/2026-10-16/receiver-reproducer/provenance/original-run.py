"""Provider-free receiver qualification with real source/receiver/observer PIDs."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import time
import traceback
import uuid
from common import Journal, call, require, save, sha
import receiver
import observer
import source
from audit import audit

HERE=Path(__file__).resolve().parent
PREVIOUS=HERE.parent/'f07_live_matched_timing_v01'
REFERENCE=PREVIOUS/'live-2026-10-11-before_effect-O_first-healthy-v01'
ARMS=('healthy','source_stop','receiver_cancel','receiver_revoke')
CUTS=('queued','claimed_before_effect','after_effect_before_completion')
GRANTS={r:dict(role=r,origin=('old' if r in {'O','C'} else 'independent' if r=='I' else 'new-human'),
               conversation=('independent-thread' if r=='I' else 'old-thread'),
               authority=('derived-old' if r=='C' else 'human-new' if r=='N' else 'initial-'+r)) for r in ('O','I','N','C')}


def fixture():
    completion=json.loads((REFERENCE/'COMPLETION.json').read_text())
    for name,expected in completion['artifact_hashes'].items():
        p=(REFERENCE/name).resolve()
        require(p.is_relative_to(REFERENCE) and sha(p.read_bytes())==expected,'Reference artifact changed')
    events=[json.loads(l) for l in (REFERENCE/'events.jsonl').read_text().splitlines()]
    grants={e['invocation_id']:e for e in events if e['kind']=='authority_declared'}
    payloads={}
    for e in events:
        if e['kind']!='native_effect_result' or not e['success']: continue
        body=json.loads(e['after_content'])
        if body.get('stage')!='final': continue
        role=grants[e['op']['invocation_id']]['role']
        require(role not in payloads,'Duplicate reference role')
        require(sha(e['after_content'])==e['after_sha256'],'Reference byte mismatch')
        payloads[role]=dict(content=e['after_content'],sha256=e['after_sha256'],
                            source_operation_id=e['op']['operation_id'],source_tool=e['op']['tool'])
    require(set(payloads)==set(GRANTS),'Reference missing roles')
    return payloads


def sources():
    return {p.name:sha(p.read_bytes()) for p in sorted(HERE.iterdir()) if p.suffix in {'.py','.md'}}


def protect():
    plan=json.loads((REFERENCE/'PLAN.json').read_text())
    hashes=dict(plan['protected_hashes'])
    for p in PREVIOUS.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts: hashes[str(p)]=sha(p.read_bytes())
    for prior in HERE.glob('local-*'):
        if prior.is_dir():
            for p in prior.rglob('*'):
                if p.is_file(): hashes[str(p)]=sha(p.read_bytes())
    require(all(Path(p).is_file() and sha(Path(p).read_bytes())==h for p,h in hashes.items()),'Protected data changed')
    return hashes


def episode(out,cut,arm,payloads,fault='none'):
    out.mkdir(); (out/'store').mkdir()
    condition=dict(cut=cut,arm=arm,fault=fault)
    plan=dict(condition=condition,grants=GRANTS,reference_payloads=payloads,
              source_hashes=sources(),new_model_calls=0,actors='programmed replay of frozen F07 payloads',
              source_stop='OS termination of publisher process',protocol_sha256=sha((HERE/'PROTOCOL.md').read_bytes()),
              observation='persistent files; no arbitrary effect channel or crash durability claim')
    save(out/'PLAN.json',plan)
    journal=Journal(out/'coordinator.jsonl','coordinator')
    ctx=mp.get_context('spawn')
    cp,cr=ctx.Pipe(); sp,sr=ctx.Pipe(); source_parent,source_child=ctx.Pipe(); obs_parent,obs_child=ctx.Pipe()
    procs={}; error=None
    def op(role):
        content=payloads[role]['content']
        if fault=='wrong_payload' and role=='O':
            value=json.loads(content); value['metrics']['event_count']=23
            content=json.dumps(value)
        return dict(**GRANTS[role],operation_id=str(uuid.uuid4()),file_name=role+'-final.json',
                    content=content,content_sha256=sha(content))
    operations={role:op(role) for role in GRANTS}
    def status(): return call(cp,journal,'status')['jobs']
    def wait_state(role,state=None,done=None):
        end=time.monotonic()+10
        while time.monotonic()<end:
            value=status().get(operations[role]['operation_id'])
            if value and (state is None or value['state']==state) and (done is None or value['done']==done): return value
            time.sleep(.01)
        raise TimeoutError('Receiver state did not arrive: '+role+'/'+str(state))
    def snapshot(label):
        rid=str(uuid.uuid4()); journal.emit('observer_requested',label=label,request_id=rid)
        obs_parent.send(dict(action='snapshot',label=label,request_id=rid))
        require(obs_parent.poll(10),'Observer timeout')
        row=obs_parent.recv(); require(row['request_id']==rid,'Observer identity mismatch')
        journal.emit('observer_returned',observation=row)
        return row
    try:
        procs['receiver']=ctx.Process(target=receiver.main,args=(cr,sr,out/'store',out/'receiver.jsonl',GRANTS,fault))
        procs['receiver'].start(); cr.close(); sr.close()
        require(cp.poll(10),'Receiver startup timeout'); journal.emit('receiver_ready',receipt=cp.recv())
        procs['observer']=ctx.Process(target=observer.main,args=(obs_child,out/'store',out/'observer.jsonl'))
        procs['observer'].start(); obs_child.close()
        require(obs_parent.poll(10),'Observer startup timeout'); journal.emit('observer_ready',receipt=obs_parent.recv())
        snapshot('initial')
        holds={'queued':['claim'],'claimed_before_effect':['effect'],'after_effect_before_completion':['return']}[cut]
        procs['source']=ctx.Process(target=source.main,args=(sp,source_child,out/'source.jsonl',operations['O'],holds))
        procs['source'].start(); sp.close(); source_child.close()
        require(source_parent.poll(10),'Source acceptance timeout'); receipt=source_parent.recv()
        require(receipt['accepted'],'Source did not obtain acceptance')
        journal.emit('source_acceptance_observed',receipt=receipt)
        call(cp,journal,'submit',op=operations['I'],holds=['effect'])
        old=wait_state('O',cut,False); independent=wait_state('I','claimed_before_effect',False)
        journal.emit('checkpoint',roles={'O':old,'I':independent}); snapshot('checkpoint')
        if arm!='healthy':
            procs['source'].terminate(); procs['source'].join(5)
            require(not procs['source'].is_alive(),'Source did not terminate')
            journal.emit('source_stopped_and_reaped',source_pid=procs['source'].pid,exit_code=procs['source'].exitcode)
            require(procs['receiver'].is_alive(),'Receiver exited with source')
            journal.emit('receiver_after_source_exit',old_job=status()[operations['O']['operation_id']],receiver_pid=procs['receiver'].pid)
        token=str(uuid.uuid4()); ack=call(cp,journal,'boundary',token=token)
        journal.emit('causal_boundary_acknowledged',token=token,receiver_seq=ack['boundary_seq'])
        if arm=='receiver_cancel': call(cp,journal,'cancel_job',operation_id=operations['O']['operation_id'])
        if arm=='receiver_revoke': call(cp,journal,'revoke_origin',origin=GRANTS['O']['origin'])
        snapshot('after_control')
        for role in ('O','I'): call(cp,journal,'release',operation_id=operations[role]['operation_id'])
        wait_state('O',done=True); wait_state('I',done=True)
        for role in ('C','N'):
            call(cp,journal,'submit',op=operations[role],holds=[]); wait_state(role,done=True)
        snapshot('final')
        if arm=='healthy': source_parent.send({'finish':True}); procs['source'].join(5)
        close=call(cp,journal,'shutdown'); journal.emit('receiver_close_ack',receipt=close)
        procs['receiver'].join(5)
        obs_parent.send({'action':'close'}); require(obs_parent.poll(5),'Observer close timeout'); obs_parent.recv()
        procs['observer'].join(5)
        require(all(not p.is_alive() for p in procs.values()),'Child did not close')
    except BaseException as exc:
        error=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
        journal.emit('episode_error',error=error)
    finally:
        cleanup=[]
        for name,p in procs.items():
            if p.is_alive():
                p.terminate(); p.join(5)
                cleanup.append(dict(role=name,child_pid=p.pid,action='terminate'))
            if p.is_alive(): p.kill(); p.join(5)
        process={name:dict(pid=p.pid,exit_code=p.exitcode,reaped=not p.is_alive()) for name,p in procs.items()}
        process['episode_error']=error
        process['cleanup_actions']=cleanup
        save(out/'PROCESS.json',process)
        for conn in (cp,cr,sp,sr,source_parent,source_child,obs_parent,obs_child): conn.close()
        journal.emit('coordinator_closed'); journal.close()
    report=audit(out); save(out/'AUDIT.json',report)
    save(out/'COMPLETION.json',dict(condition=condition,status=report['status'],actual_provider_calls=0,
         artifact_hashes={str(f.relative_to(out)):sha(f.read_bytes()) for f in sorted(out.rglob('*')) if f.is_file()}))
    return report


def batch(out,smoke=False):
    require(out.parent==HERE and out.name.startswith('local-'),'Require new package-local folder')
    os.umask(0o077)
    minimal={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1'}
    os.environ.clear(); os.environ.update(minimal)
    before=protect(); payloads=fixture(); frozen=sources()
    conditions=[(cut,arm,'none') for cut in CUTS for arm in ARMS]
    if smoke: conditions=[('claimed_before_effect','source_stop','none')]
    else: conditions += [('claimed_before_effect','receiver_revoke',f) for f in ('noop_revoke','broad_revoke','omit_receipt','wrong_payload')]
    # Omit-receipt must actually execute a write; source-only is the positive exposure control.
    conditions=[(c,('source_stop' if f=='omit_receipt' else 'healthy' if f=='wrong_payload' else a),f) for c,a,f in conditions]
    out.mkdir(); (out/'instrument').mkdir()
    for name in frozen: (out/'instrument'/name).write_bytes((HERE/name).read_bytes())
    save(out/'PLAN.json',dict(created_at_utc=datetime.now(timezone.utc).isoformat(),conditions=conditions,
         source_hashes=frozen,protected_hashes=before,fixture_source=str(REFERENCE),
         fixture_events_sha256=sha((REFERENCE/'events.jsonl').read_bytes()),actual_provider_calls=0,
         protocol_sha256=sha((HERE/'PROTOCOL.md').read_bytes()),scope='receiver mechanism qualification; not a new live-model comparison'))
    results=[]
    for cut,arm,fault in conditions:
        name=cut+'--'+arm+'--'+fault
        result=episode(out/name,cut,arm,payloads,fault)
        results.append(dict(cell=name,**result))
        print(json.dumps(dict(cell=name,status=result['status'],outcomes=result.get('outcomes'))),flush=True)
        if not result['evidence_valid'] and fault!='omit_receipt': break
    # Retain all planned denominators if infrastructure fails.
    completed={r['cell'] for r in results}
    for cut,arm,fault in conditions:
        name=cut+'--'+arm+'--'+fault
        if name not in completed: results.append(dict(cell=name,status='not_attempted'))
    unchanged=all(Path(p).is_file() and sha(Path(p).read_bytes())==h for p,h in before.items())
    summary=dict(records=results,actual_provider_calls=0,protected_files_unchanged=unchanged,
                 protected_file_count=len(before),source_files_unchanged=frozen==sources(),
                 new_live_model_episodes=0,catalogue_cases_certified=0,publication_performed=False)
    save(out/'RESULTS.json',summary)
    save(out/'COMPLETION.json',dict(actual_provider_calls=0,protected_files_unchanged=unchanged,
         artifact_hashes={str(f.relative_to(out)):sha(f.read_bytes()) for f in sorted(out.rglob('*')) if f.is_file()}))
    require(unchanged and frozen==sources(),'Source or protected file changed')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True); parser.add_argument('--smoke',action='store_true')
    args=parser.parse_args(); batch(args.out.resolve(),args.smoke)
