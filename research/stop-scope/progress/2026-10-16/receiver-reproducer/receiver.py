"""Separate receiving executor. Accepted jobs outlive the source pipe."""
from copy import deepcopy
import os
from pathlib import Path
import threading
from multiprocessing.connection import wait
from common import Journal, offline, require, sha


class Service:
    def __init__(self, root, journal, grants, fault='none'):
        self.root, self.log, self.grants, self.fault = Path(root), journal, grants, fault
        self.lock = threading.RLock()
        self.jobs, self.revoked = {}, set()

    def view(self, job):
        return dict(operation_id=job['op']['operation_id'], role=job['op']['role'],
                    origin=job['op']['origin'], state=job['state'],
                    written=job['written'], done=job['done'].is_set())

    def submit(self, op, holds, channel):
        require(channel != 'source' or op['role'] == 'O', 'Source can only submit its O grant')
        require(op['role'] in self.grants, 'Unknown role')
        grant = self.grants[op['role']]
        require(all(op.get(k) == v for k,v in grant.items()), 'Grant/identity mismatch')
        require(op['content_sha256'] == sha(op['content']), 'Payload hash mismatch')
        require(op['file_name'] == op['role']+'-final.json', 'Unexpected output path')
        require(set(holds) <= {'claim','effect','return'}, 'Unknown hold')
        oid = op['operation_id']
        with self.lock:
            if oid in self.jobs:
                require(self.jobs[oid]['op'] == op, 'Conflicting operation replay')
                return dict(status='duplicate', **self.view(self.jobs[oid]))
            job = dict(op=deepcopy(op), state='accepted', written=False, cancelled=False,
                       claim=threading.Event(), effect=threading.Event(),
                       return_event=threading.Event(), done=threading.Event())
            for name,key in [('claim','claim'),('effect','effect'),('return','return_event')]:
                if name not in holds: job[key].set()
            self.jobs[oid] = job
            accepted = self.log.emit('job_accepted', op=op, channel=channel,
                                     holds=holds, acceptance_is_effect_receipt=False)
            worker = threading.Thread(target=self.work, args=(job,), daemon=True)
            job['thread'] = worker
            worker.start()
            return dict(status='accepted', operation_id=oid,
                        payload_sha256=op['content_sha256'], receiver_instance=self.log.instance,
                        acceptance_seq=accepted['seq'])

    def work(self, job):
        op = job['op']
        try:
            with self.lock:
                job['state'] = 'queued'
                self.log.emit('worker_entered', operation_id=op['operation_id'], thread=threading.get_ident())
            require(job['claim'].wait(30), 'Claim barrier timeout')
            with self.lock:
                job['state'] = 'claimed_before_effect'
                self.log.emit('job_claimed', operation_id=op['operation_id'])
            require(job['effect'].wait(30), 'Effect barrier timeout')
            with self.lock:
                allowed = not job['cancelled'] and op['origin'] not in self.revoked
                self.log.emit('effect_decision', operation_id=op['operation_id'], allowed=allowed,
                              cancelled=job['cancelled'], origin_revoked=op['origin'] in self.revoked)
                if not allowed:
                    job['state'] = 'denied'
                    self.log.emit('effect_denied', operation_id=op['operation_id'])
                    return
                path = self.root/op['file_name']
                require(path.parent.resolve() == self.root.resolve() and not path.is_symlink(), 'Unsafe output')
                self.log.emit('native_write_attempt', operation_id=op['operation_id'], file_name=path.name)
                with path.open('xb') as f:
                    f.write(op['content'].encode()); f.flush()
                job['written'] = True
                if not (self.fault == 'omit_receipt' and op['role'] == 'O'):
                    self.log.emit('native_write_receipt', operation_id=op['operation_id'], file_name=path.name,
                                  content_sha256=sha(path.read_bytes()), bytes=path.stat().st_size)
                job['state'] = 'after_effect_before_completion'
            require(job['return_event'].wait(30), 'Return barrier timeout')
            with self.lock: job['state'] = 'completed'
        except BaseException as exc:
            with self.lock:
                job['state'] = 'error'
                self.log.emit('worker_error', operation_id=op['operation_id'], error_type=type(exc).__name__, message=str(exc))
        finally:
            with self.lock:
                self.log.emit('worker_finished', operation_id=op['operation_id'], state=job['state'], written=job['written'])
                job['done'].set()

    def dispatch(self, request, channel):
        action = request['action']
        if channel == 'source': require(action == 'submit', 'Source lacks control channel')
        if action == 'submit': return self.submit(request['op'], request.get('holds', []), channel)
        if action == 'status':
            with self.lock: return dict(jobs={k:self.view(v) for k,v in self.jobs.items()})
        if action == 'boundary':
            row = self.log.emit('intervention_boundary', token=request['token'])
            return dict(boundary_seq=row['seq'], receiver_instance=self.log.instance)
        if action == 'cancel_job':
            with self.lock:
                job = self.jobs[request['operation_id']]
                if job['written']: result = 'too_late_effect_applied'
                elif job['done'].is_set(): result = 'already_terminal'
                else:
                    job['cancelled'] = True
                    result = 'cancellation_registered'
                    job['claim'].set(); job['effect'].set(); job['return_event'].set()
                row = self.log.emit('cancel_response', operation_id=request['operation_id'], status=result)
                return dict(status=result, receiver_seq=row['seq'], claim='request_disposition_not_quiescence')
        if action == 'revoke_origin':
            with self.lock:
                require(request['origin'] in {g['origin'] for g in self.grants.values()}, 'Unknown origin')
                if self.fault != 'noop_revoke':
                    self.revoked.update({g['origin'] for g in self.grants.values()} if self.fault == 'broad_revoke' else {request['origin']})
                row = self.log.emit('revocation_response', origin=request['origin'], status='revocation_registered')
                return dict(status='revocation_registered', receiver_seq=row['seq'], claim='future_local_effect_check_not_rollback')
        if action == 'release':
            with self.lock:
                job = self.jobs[request['operation_id']]
                for key in ('claim','effect','return_event'): job[key].set()
                self.log.emit('job_released', operation_id=request['operation_id'])
            return dict(status='released')
        if action == 'shutdown':
            with self.lock: require(all(j['done'].is_set() for j in self.jobs.values()), 'Cannot shutdown pending jobs')
            for j in self.jobs.values(): j['thread'].join(2)
            require(all(not j['thread'].is_alive() for j in self.jobs.values()), 'Worker still alive')
            return dict(status='closed', jobs={k:self.view(v) for k,v in self.jobs.items()})
        raise ValueError('Unknown action')


def main(control, source, root, log_path, grants, fault):
    offline()
    log = Journal(log_path, 'receiver')
    service = Service(root, log, grants, fault)
    log.emit('receiver_started', grants=grants, fault=fault)
    control.send(dict(ready=True, pid=os.getpid(), receiver_instance=log.instance))
    channels = {control:'control',source:'source'}
    try:
        while channels:
            for conn in wait(list(channels), timeout=1):
                try: request = conn.recv()
                except EOFError:
                    log.emit('channel_closed', channel=channels.pop(conn)); conn.close(); continue
                channel = channels[conn]
                log.emit('rpc_received', channel=channel, request=request)
                try: reply = dict(ok=True, **service.dispatch(request, channel))
                except Exception as exc:
                    reply = dict(ok=False, error_type=type(exc).__name__, error=str(exc))
                reply.update(rpc_id=request['rpc_id'], receiver_pid=os.getpid(), receiver_instance=log.instance)
                log.emit('rpc_replied', rpc_id=request['rpc_id'], reply=reply)
                conn.send(reply)
                if request['action'] == 'shutdown' and reply['ok']:
                    log.emit('receiver_closed'); return
    finally:
        for conn in channels: conn.close()
        log.close()
