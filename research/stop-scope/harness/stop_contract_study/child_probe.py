"""Integrated actual local API/stop/monitor experiment with explicit adapters."""
import asyncio
import base64
from contextlib import asynccontextmanager
from contextvars import ContextVar
import hashlib
import importlib.metadata
import json
import logging
from pathlib import Path
import sys
import threading
import time
import traceback
import uuid

ROOT=Path(__file__).resolve().parent
OUT=Path(sys.argv[1]).resolve()
ARM,SCHEDULE,SEED=sys.argv[2],sys.argv[3],int(sys.argv[4])
RECEIPT_FAULT=sys.argv[5] if len(sys.argv)>5 else 'none'
sys.dont_write_bytecode=True;sys.path.insert(0,str(ROOT))
JOURNAL=(OUT/'events.jsonl').open('x');ROWS=[];LOCK=threading.RLock()
def record(kind,**fields):
    with LOCK:
        row=json.loads(json.dumps({'seq':len(ROWS)+1,'monotonic_ns':time.monotonic_ns(),'kind':kind,**fields},default=str))
        ROWS.append(row);JOURNAL.write(json.dumps(row)+'\n');JOURNAL.flush()
def safety(event,args):
    if event in {'socket.connect','socket.bind','socket.getaddrinfo','subprocess.Popen','os.system','os.exec','os.posix_spawn'}:
        frames=traceback.extract_stack(limit=12)
        optional=(event=='socket.bind' and args[1]==('::1',0) and any(f.name=='_has_ipv6' and f.filename.endswith('urllib3/util/connection.py') for f in frames)) or (
            event=='subprocess.Popen' and args[0] in {'file','uname'} and any(f.name in {'_syscmd_file','from_subprocess'} and f.filename.endswith('/platform.py') for f in frames))
        record('optional_platform_probe_denied' if optional else 'safety_boundary_blocked',event=event,stack=traceback.format_list(frames))
        raise PermissionError('No external network/process in experiment: '+event)
sys.addaudithook(safety)
class SourceLogRecorder(logging.Handler):
    def emit(self,e):
        if e.levelno>=logging.WARNING and e.name.startswith('agent.'):
            record('source_warning_or_error',logger=e.name,level=e.levelname,message=e.getMessage(),
                   error_type=type(e.exc_info[1]).__name__ if e.exc_info else None,
                   error_message=str(e.exc_info[1]) if e.exc_info else None,
                   exception_trace=traceback.format_exception(*e.exc_info) if e.exc_info else None)
logging.getLogger().addHandler(SourceLogRecorder())
def inventory():
    return [{'path':str(p.relative_to(OUT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'content':p.read_text()}
            for p in sorted((OUT/'files').rglob('*')) if p.is_file()]
async def until(predicate,label,timeout=40):
    async def wait():
        while not predicate(): await asyncio.sleep(.005)
    await asyncio.wait_for(wait(),timeout)
    record('condition_observed',label=label)

async def main():
    import httpx
    from langgraph_sdk.client import LangGraphClient
    from langgraph_api.server import app
    import factory_support as factory
    class JournalTransport(httpx.AsyncBaseTransport):
        def __init__(self): self.inner=httpx.ASGITransport(app=app)
        async def handle_async_request(self,req):
            if req.url.host!='fixture.invalid' or 'authorization' in req.headers or 'x-api-key' in req.headers:
                raise AssertionError('Only credential-free in-process fixture URL allowed')
            rid=str(uuid.uuid4())
            record('real_http_request',request_id=rid,method=req.method,path=req.url.path,query=str(req.url.query),
                   body=json.loads(req.content) if req.content else None,body_b64=base64.b64encode(req.content).decode(),
                   body_sha256=hashlib.sha256(req.content).hexdigest())
            response=await self.inner.handle_async_request(req);await response.aread()
            try: body=response.json()
            except ValueError: body=response.text
            record('real_http_response',request_id=rid,method=req.method,path=req.url.path,status=response.status_code,
                   body=body,body_b64=base64.b64encode(response.content).decode(),body_sha256=hashlib.sha256(response.content).hexdigest())
            return response
        async def aclose(self): await self.inner.aclose()
    http=httpx.AsyncClient(base_url='http://fixture.invalid',transport=JournalTransport(),trust_env=False)
    client=LangGraphClient(http)
    tid,independent_tid,initial_id,independent_id=[str(uuid.uuid4()) for _ in range(4)]
    roles={};tasks={};receipts={};delivery_context=ContextVar('study_delivery_binding',default=None)
    release_task=None
    monitor_phase=None
    status={'execution_status':'incomplete','arm':ARM,'schedule':SCHEDULE,'seed':SEED,'receipt_fault':RECEIPT_FAULT,
            'thread_id':tid,'initial_invocation_id':initial_id,'independent_thread_id':independent_tid}
    def key(t,i): return hashlib.sha256(f'{t}:{i}'.encode()).hexdigest()[:24]
    def metadata(channel,ts):
        return {'visibility':'public','owner_type':'user','owner_login':'fixture-user','github_login':'fixture-user','source':'slack',
            'source_context':{'slack_thread':{'channel_id':channel,'thread_ts':ts,'triggering_user_id':'UFIXTURE'}},
            'agent_settings':{'model_id':'openai:gpt-5.6-sol','effort':'medium','subagent_model_id':'openai:gpt-5.6-sol',
                'subagent_effort':'low','model_routing_enabled':False,'repo_instructions':None}}
    def cfg(i,channel='CFIXTURE',ts='1.000'):
        return {'source':'slack','github_login':'fixture-user','repo_explicitly_none':True,'plan_mode':False,
            'slack_thread':{'channel_id':channel,'thread_ts':ts,'triggering_user_id':'UFIXTURE'},'invocation_id':i,'prepare_run_id':i}
    def role(name,t,run,inv,origin=None):
        item={'role':name,'thread_id':t,'run_id':run['run_id'],'invocation_id':inv,'origin_invocation_id':origin or inv,'key':key(t,inv)}
        storage=name
        if name in roles:
            if name not in {'old_completion','new_completion'}:raise RuntimeError('Ambiguous non-completion role '+name)
            storage=f'{name}_retry_{sum(entry["role"]==name for entry in roles.values())}'
        roles[storage]=item;record('invocation_role',**item)
        return item
    async def terminal(name):
        item=roles[name]
        response=await asyncio.wait_for(client.runs.join(item['thread_id'],item['run_id']),45)
        record('terminal_run_joined',**item,phase=item['role'],joined=response)
        current=await client.runs.get(item['thread_id'],item['run_id'])
        record('terminal_run_status',**item,run=current)
        return current
    try:
        record('factory_seams',**factory.configure(client,record,OUT/'files',ARM,SCHEDULE,initial_id,SEED))
        from agent.utils.event_loop import pin_single_event_loop
        pin_single_event_loop()
        from agent.slack import stop
        from agent import background_tasks as background
        from agent.dispatch import dispatch_agent_run
        async def ui_status(*args,**kwargs): record('synthetic_slack_ui_status',args=args,kwargs=kwargs)
        stop.set_session_status=ui_status
        original_stop_dispatch=stop.dispatch_agent_run
        async def summary_dispatch(t,content,configurable,**kwargs):
            inv=str(uuid.uuid4());effective={**configurable,'invocation_id':inv,'prepare_run_id':inv}
            factory.register_origin(inv,initial_id,'stop_summary')
            record('summary_origin_bound',thread_id=t,invocation_id=inv,origin_invocation_id=initial_id,
                   input_configurable=configurable,effective_configurable=effective)
            result=await original_stop_dispatch(t,content,effective,**kwargs)
            role('source_summary',t,result,inv,initial_id)
            return result
        stop.dispatch_agent_run=summary_dispatch
        original_notification=background._notification
        original_delivery=background.dispatch_agent_run
        def notification(task):
            task_id=task.get('task_id');binding=tasks.get(task_id)
            if not binding or task.get('output_path')!=f"/incident-{binding['job_id']}.json":
                raise RuntimeError('No trusted task-creation origin for notification')
            delivery_context.set(dict(binding))
            record('completion_notification_bound',task=dict(task),binding=dict(binding))
            return original_notification(task)+'\n'+factory.request_text(binding['job_id'])
        async def delivery(t,content,configurable,**kwargs):
            binding=delivery_context.get()
            if not binding or tasks.get(binding['task_id'])!=binding or t!=binding['thread_id']:
                raise RuntimeError('Delivery outside bound task origin')
            task_id=binding['task_id']
            bypass=(RECEIPT_FAULT=='bypass' and monitor_phase=='old_redelivery_after_new_human' and task_id=='cmd-study-old')
            if task_id in receipts and not bypass:
                record('completion_duplicate_consumed',binding=binding,previous=receipts[task_id],new_run_created=False)
                return None
            if bypass:record('explicit_receipt_bypass_fault',binding=binding,previous=receipts.get(task_id),phase=monitor_phase)
            inv=str(uuid.uuid4());origin=binding['origin_invocation_id']
            effective={**configurable,'invocation_id':inv,'prepare_run_id':inv}
            restricted=origin==initial_id and ARM!='scoped_no_summary'
            if restricted: effective['stop_summary']=True
            factory.register_origin(inv,origin,'background_completion')
            record('completion_policy_decision',binding=binding,invocation_id=inv,restricted_summary=restricted,
                   input_configurable=configurable,effective_configurable=effective,content=content)
            result=await original_delivery(t,content,effective,**kwargs)
            item=role('old_completion' if origin==initial_id else 'new_completion',t,result,inv,origin)
            receipts[task_id]={'run_id':result['run_id'],'invocation_id':inv,'origin_invocation_id':origin}
            record('completion_admission_receipt',binding=binding,receipt=receipts[task_id])
            return result
        background._notification=notification;background.dispatch_agent_run=delivery
        record('explicit_study_adapters',source_files_modified=False,
               adapters=['source-summary origin binding','task-creation/notification origin binding',
                         'old-completion summary policy','local duplicate delivery receipt','study stop confirmation'],
               authentication='native local-dev noop, not production ingress')
        def seed_task(task_id,job,origin):
            binding={'task_id':task_id,'job_id':job,'origin_invocation_id':origin,'thread_id':tid}
            if task_id in tasks: raise RuntimeError('Task origin overwrite forbidden')
            tasks[task_id]=binding
            factory.seed_background_task(tid,task_id,job,origin)
            record('trusted_task_created',**binding,provider='explicit synthetic task creation after actual originating run admission')
        async def tick(phase):
            nonlocal monitor_phase
            monitor_phase=phase;before=set(roles)
            record('monitor_started',thread_id=tid,phase=phase)
            response=await background.monitor_background_tasks(tid)
            record('monitor_returned',thread_id=tid,phase=phase,result=response,
                   tasks=factory.get_backend(tid).tasks,monitor_locked=factory.get_backend(tid).locked)
            for storage in roles.keys()-before:
                if '_retry_' in storage:await terminal(storage)
            monitor_phase=None
        @asynccontextmanager
        async def runtime():
            async with app.router.lifespan_context(app):
                record('real_server_lifespan_started',auth_type='noop',worker_concurrency=4)
                try: yield
                finally:
                    factory.cleanup()
                    if release_task is not None:
                        if not release_task.done(): release_task.cancel()
                        await asyncio.gather(release_task,return_exceptions=True)
                    record('worker_drain_cleanup',state=await factory.drain_workers())
            record('real_server_lifespan_closed')
        async with runtime():
            await client.threads.create(thread_id=tid,metadata=metadata('CFIXTURE','1.000'))
            await client.store.put_item(('slack_thread_map','CFIXTURE'),'1.000',{'thread_id':tid})
            factory.hold_invocation(initial_id)
            initial=await client.runs.create(tid,'agent',input={'messages':[{'role':'user','content':factory.request_text('old')}]},
                config={'configurable':cfg(initial_id)},durability='sync')
            role('initial',tid,initial,initial_id)
            await until(lambda:any(r['kind']=='scripted_model_waiting' and r.get('key')==key(tid,initial_id) for r in ROWS),'initial_model_waiting')
            await factory.seed_job(tid,'old')
            await client.threads.update(tid,metadata={'sandbox_id':factory.get_backend(tid).id})
            seed_task('cmd-study-old','old',initial_id)

            await client.threads.create(thread_id=independent_tid,metadata=metadata('CINDEPENDENT','2.000'))
            factory.hold_invocation(independent_id)
            independent=await client.runs.create(independent_tid,'agent',input={'messages':[{'role':'user','content':factory.request_text('independent')}]},
                config={'configurable':cfg(independent_id,'CINDEPENDENT','2.000')},durability='sync')
            role('independent',independent_tid,independent,independent_id)
            await until(lambda:any(r['kind']=='scripted_model_waiting' and r.get('key')==key(independent_tid,independent_id) for r in ROWS),'independent_model_waiting')
            await factory.seed_job(independent_tid,'independent')
            factory.release_invocation(initial_id)
            if SCHEDULE=='unheld':
                await until(lambda:any(r['kind']=='worker_entered' and r.get('invocation_id')==initial_id and r.get('stage')=='final' for r in ROWS),'unheld_final_worker_observed')
            else: await until(factory.barrier_reached,'initial_final_schedule_barrier')
            record('pre_stop_file_inventory',files=await asyncio.to_thread(inventory))
            factory.release_invocation(independent_id)
            record('concurrent_legitimate_work_released',**roles['independent'])
            record('stop_requested',**roles['initial'],kind_of_stop='reaction')
            await factory.revoke_initial()
            await stop.process_slack_stop_reaction({'reaction':'x','item':{'type':'message','channel':'CFIXTURE','ts':'1.000'}},event_id=str(uuid.uuid4()))
            record('stop_handler_returned',thread_id=tid)
            if SCHEDULE!='unheld':
                await until(lambda:any(r['kind']=='awrite_cancelled' and r.get('invocation_id')==initial_id and r.get('stage')=='final' for r in ROWS),'actual_native_awaiter_cancellation')
            current=await client.runs.get(tid,initial['run_id'])
            record('stopped_initial_run',run=current,**roles['initial'])
            async def controller():
                delay=1.0 if SCHEDULE=='drain_timeout' else .30
                record('release_controller_started',delay_seconds=delay,independent_of_stop_confirmation=True)
                await asyncio.sleep(delay)
                factory.release_barrier('independent_controller_delay_elapsed')
            if SCHEDULE!='unheld': release_task=asyncio.create_task(controller())
            if ARM=='drain_summary':
                deadline=.05 if SCHEDULE=='drain_timeout' else 10.0
                record('drain_requested',timeout_seconds=deadline,origin_invocation_id=initial_id)
                drained=await factory.drain_initial(deadline)
                record('drain_result',result=drained,origin_invocation_id=initial_id)
                record('study_stop_confirmation',status='complete' if drained['completed'] else 'pending',
                       basis='workers_quiescent' if drained['completed'] else 'drain_deadline',origin_invocation_id=initial_id)
            else:
                cancelled=any(r['kind']=='awrite_cancelled' and r.get('invocation_id')==initial_id for r in ROWS)
                observed_status=('scope_withdrawn' if ARM.startswith('scoped') else
                                 'cancellation_acknowledged' if cancelled else
                                 'initial_already_terminal' if current['status']=='success' else 'cancellation_requested')
                observed_basis=('origin_authority' if ARM.startswith('scoped') else
                                'coroutine_only' if cancelled else
                                'initial_already_terminal' if current['status']=='success' else 'cancellation_request_only')
                record('study_stop_confirmation',status=observed_status,basis=observed_basis,origin_invocation_id=initial_id)
            if 'source_summary' not in roles: raise RuntimeError('Source stop handler did not dispatch summary')
            await terminal('source_summary')
            await terminal('independent')
            if release_task is not None: await release_task
            record('worker_drain_after_stop',state=await factory.drain_workers())
            record('after_worker_drain_inventory',files=await asyncio.to_thread(inventory))
            await tick('old_completion_first')
            if 'old_completion' in roles: await terminal('old_completion')
            await tick('old_completion_duplicate_done')

            human_id=str(uuid.uuid4());await factory.seed_job(tid,'human')
            record('explicit_new_human_input',thread_id=tid,invocation_id=human_id,configurable=cfg(human_id))
            human=await dispatch_agent_run(tid,factory.request_text('human'),cfg(human_id),source='slack',client=client)
            role('new_human',tid,human,human_id);await terminal('new_human')
            await factory.seed_job(tid,'new_background')
            seed_task('cmd-study-new','new_background',human_id)
            await tick('new_human_completion')
            if 'new_completion' in roles: await terminal('new_completion')
            await tick('new_completion_duplicate_done')
            old_tasks=[t for t in factory.get_backend(tid).tasks if t['task_id']=='cmd-study-old']
            if len(old_tasks)!=1: raise RuntimeError('Original task disappeared from task inventory')
            previous=dict(old_tasks[0]);old_tasks[0]['notification']='pending'
            record('explicit_redelivery_fault',task_id='cmd-study-old',before=previous,after=dict(old_tasks[0]),
                   scope='synthetic provider re-delivers same logical task; local receipt remains')
            await tick('old_redelivery_after_new_human')
            record('worker_drain_final',state=await factory.drain_workers())
            for thread in (tid,independent_tid):
                record('final_server_state',thread_id=thread,runs=await client.runs.list(thread),thread=await client.threads.get(thread))
            record('final_task_registry',tasks=tasks,receipts=receipts,native_tasks=factory.get_backend(tid).tasks)
            status['execution_status']='completed'
            record('scenario_completed',execution_status='completed',preferred_outcome_required=False)
        status['files']=await asyncio.to_thread(inventory)
        record('final_file_inventory',files=status['files'])
    except BaseException as e:
        status['execution_status']='setup_or_execution_error';status['error']=f'{type(e).__name__}: {e}'
        record('diagnostic_error',error=status['error'],traceback=traceback.format_exc())
        print(traceback.format_exc(),file=sys.stderr)
    finally:
        await client.aclose()
        record('cleanup',http_client_closed=http.is_closed,external_connections_allowed=False)
        status['packages']={p.metadata['Name']:p.version for p in importlib.metadata.distributions()}
        with (OUT/'result.json').open('x') as f: json.dump(status,f,indent=2,default=str)
        JOURNAL.close()
    print(json.dumps({k:status.get(k) for k in ['arm','schedule','seed','execution_status','error']}))
    return 0 if status['execution_status']=='completed' else 1
if __name__=='__main__': raise SystemExit(asyncio.run(main()))
