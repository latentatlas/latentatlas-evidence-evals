"""Actual Open-SWE source process; durable receiver lifecycle stays in supervisor."""
import asyncio
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import time
import traceback
import uuid

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
FEAS = HERE.parent
sys.path.insert(0, str(HERE))
from bridge_dependencies import common, verify_adapter
Journal, require, save = common.Journal, common.require, common.save
from comparison_config import authorization, LIMITS
sys.path.append(str(FEAS/"f07_live_bridge_v01"))
import bridge_codec
from transport import Transport as ProviderTransport, NETWORK_ALLOWED
ALLOWED_IPS = set()
LIVE = False


def safety(event, args):
    if LIVE and NETWORK_ALLOWED.get():
        if event == "socket.getaddrinfo" and args[0] in {"api.openai.com"} and args[1] == 443:
            return
        if event == "socket.connect" and args[1][0] in ALLOWED_IPS and args[1][1] == 443:
            return
    if event in {"socket.connect", "socket.bind", "socket.getaddrinfo", "subprocess.Popen",
                 "os.system", "os.exec", "os.posix_spawn"}:
        raise PermissionError("Network/process action outside authorized model transport")


async def until(predicate, timeout=120):
    async def loop():
        while not predicate(): await asyncio.sleep(.02)
    await asyncio.wait_for(loop(), timeout)


async def run(out, conn, log, api_key=None):
    # Import precedence preserves the pinned native adapter and frozen codec.
    sys.path[:0] = [str(HERE), str(FEAS/"f07_direct_after_v01"), str(FEAS/"f07_live_bridge_v01")]
    from bridge_codec import Session
    import native_adapter as a
    verify_adapter(a)
    from runtime_link import install
    import httpx
    from langgraph_sdk.client import LangGraphClient
    from langgraph_api.server import app
    plan = json.loads((out/"PLAN.json").read_text())
    arm, profile = plan["arm"], plan["profile"]
    rows = []
    store, transport = None, None
    def record(kind, **fields):
        if "actor" in fields: fields["model_actor"] = fields.pop("actor")
        rows.append(log.emit(kind, **fields))
    async def snapshot(label):
        value = await asyncio.to_thread(a.controller.rpc, "snapshot", label=label)
        record("source_snapshot_bound", label=label, observation=value["observation"])
    class LocalHTTP(httpx.AsyncBaseTransport):
        def __init__(self): self.inner = httpx.ASGITransport(app=app)
        async def handle_async_request(self, request):
            require(request.url.host == "fixture.invalid" and "authorization" not in request.headers,
                    "Credential-free in-process HTTP only")
            rid = str(uuid.uuid4())
            record("native_http_request", request_id=rid, method=request.method,
                   path=request.url.path, body=request.content.decode())
            response = await self.inner.handle_async_request(request)
            await response.aread()
            record("native_http_response", request_id=rid, status=response.status_code, body=response.text)
            return response
        async def aclose(self): await self.inner.aclose()
    http = httpx.AsyncClient(base_url="http://fixture.invalid", transport=LocalHTTP(), trust_env=False)
    client = LangGraphClient(http)
    old = dict(thread_id=str(uuid.uuid4()), invocation_id=str(uuid.uuid4()), job_id="old")
    roles = {"O":old, "I":dict(thread_id=str(uuid.uuid4()), invocation_id=str(uuid.uuid4()), job_id="independent")}
    held = set()
    result = dict(completed=False, actual_provider_calls=0, new_live_episodes=0, arm=arm,
                  profile=profile, fault=plan["fault"], roles=roles, live_model=LIVE, seed=17)
    def metadata(label):
        return dict(visibility="public", owner_type="user", owner_login="fixture-user", github_login="fixture-user",
                    source="slack", source_context={"slack_thread":dict(channel_id="CI" if label=="I" else "CO",
                    thread_ts="2.000" if label=="I" else "1.000", triggering_user_id="UFIXTURE")},
                    agent_settings=dict(model_id="openai:"+(plan["live_config"]["model"] if LIVE else "gpt-6-astra"),
                    effort=plan["live_config"]["reasoning_effort"] if LIVE else "high",
                    subagent_model_id="openai:"+(plan["live_config"]["model"] if LIVE else "gpt-6-astra"),
                    subagent_effort=plan["live_config"]["reasoning_effort"] if LIVE else "high",
                    model_routing_enabled=False, repo_instructions=None))
    async def start(label, hold=False, derived=False):
        r = roles[label]
        grant = a.ledger.declare(label, r["thread_id"], r["invocation_id"],
                                 parent=old["invocation_id"] if derived else None)
        if derived: a.base.register_origin(r["invocation_id"], old["invocation_id"], "continuation_probe")
        if hold: a.base.hold_invocation(r["invocation_id"]); held.add(r["invocation_id"])
        cfg = dict(source="slack", github_login="fixture-user", repo_explicitly_none=True,
                   plan_mode=False, stop_summary=False, invocation_id=r["invocation_id"],
                   prepare_run_id=r["invocation_id"], slack_thread=metadata(label)["source_context"]["slack_thread"])
        content = a.base.request_text(r["job_id"])
        record("work_dispatch", role=label, grant=grant, content=content,
               configurable=cfg, actual_autonomous_spawn=False)
        run = await client.runs.create(r["thread_id"], "agent",
                input={"messages":[{"role":"user","content":content}]}, config={"configurable":cfg}, durability="sync")
        r["run_id"] = run["run_id"]
        record("work_accepted", role=label, **r)
    def ready(inv):
        key = a.base._by_invocation.get(inv)
        return key is not None and any(r["kind"]=="scripted_model_waiting" and r.get("key")==key for r in rows)
    async def terminal(label, join_seconds=None):
        r = roles[label]
        await asyncio.wait_for(client.runs.join(r["thread_id"],r["run_id"]),
                               join_seconds or LIMITS["graph_join_seconds"])
        state = await client.runs.get(r["thread_id"],r["run_id"])
        record("graph_terminal", role=label, state=state, run_id=r["run_id"])
        record("graph_checkpoint", role=label, state=await a.read_checkpoint(client,r["thread_id"]))
        require(state["status"] in {"success","error","interrupted"}, "Nonterminal graph")
    try:
        config = plan.get("live_config")
        if LIVE:
            bridge_codec.MODEL = config["model"]
            bridge_codec.EFFORT = config["reasoning_effort"]
            def resolve_provider():
                import socket
                token = NETWORK_ALLOWED.set(True)
                try:
                    ALLOWED_IPS.update(r[4][0] for r in socket.getaddrinfo("api.openai.com",443,type=socket.SOCK_STREAM))
                finally: NETWORK_ALLOWED.reset(token)
            await asyncio.to_thread(resolve_provider)
        transport = await asyncio.to_thread(ProviderTransport,out,record,arm=arm,config=config,api_key=api_key)
        capture, transport = install(a, conn, log, out/"files", record, profile, transport)
        record("fixture_configured", seams=a.configure(client,capture,out/"files",old["invocation_id"],
                    17,"create","before_effect","O_before_I_before_workers_pending","O_first"))
        from agent.utils.event_loop import pin_single_event_loop
        pin_single_event_loop()
        from agent.slack import stop
        original_dispatch = stop.dispatch_agent_run
        async def summary(t, content, configurable, **kwargs):
            require(t==old["thread_id"] and configurable.get("stop_summary") is True, "Unexpected summary")
            inv = str(uuid.uuid4())
            a.ledger.declare("S", t, inv, parent=old["invocation_id"])
            a.base.register_origin(inv, old["invocation_id"], "stop_summary")
            effective = {**configurable,"invocation_id":inv,"prepare_run_id":inv}
            record("source_summary_dispatch", invocation_id=inv, content=content, configurable=effective)
            run = await original_dispatch(t,content,effective,**kwargs)
            roles["S"] = dict(thread_id=t,invocation_id=inv,run_id=run["run_id"])
            return run
        stop.dispatch_agent_run = summary
        async with app.router.lifespan_context(app):
            record("native_runtime_started")
            try:
                for label in ("O","I"):
                    await client.threads.create(thread_id=roles[label]["thread_id"], metadata=metadata(label))
                await client.store.put_item(("slack_thread_map","CO"),"1.000",{"thread_id":old["thread_id"]})
                await start("O",hold=True); await start("I",hold=True)
                setup_deadline = time.monotonic() + 120
                while not all(ready(roles[r]["invocation_id"]) for r in ("O","I")):
                    for label in ("O","I"):
                        r = roles[label]
                        state = await client.runs.get(r["thread_id"],r["run_id"])
                        if state["status"] in {"success","error","interrupted"}:
                            record("setup_terminal_before_barrier",role=label,state=state)
                            record("setup_checkpoint",role=label,state=await a.read_checkpoint(client,r["thread_id"]))
                            raise RuntimeError("Setup ended before the model barrier; inspect setup_checkpoint")
                    require(time.monotonic() < setup_deadline,"Setup observation timeout")
                    await asyncio.sleep(.05)
                for job in ("old","human","new_background"): await a.base.seed_job(old["thread_id"],job)
                await a.base.seed_job(roles["I"]["thread_id"],"independent")
                for r in (old,roles["I"]):
                    await client.threads.update(r["thread_id"],metadata={"sandbox_id":a.base.get_backend(r["thread_id"]).id})
                await snapshot("initial")
                for inv in list(held): a.base.release_invocation(inv); held.remove(inv)
                early = None
                deadline = time.monotonic()+LIMITS["checkpoint_seconds"]
                while not all(r in a.controller.targets for r in ("O","I")):
                    for label in ("O","I"):
                        r=roles[label]
                        state=await client.runs.get(r["thread_id"],r["run_id"])
                        if label not in a.controller.targets and state["status"] in {"success","error","interrupted"}:
                            early = dict(role=label,state=state)
                            break
                    if early: break
                    require(time.monotonic()<deadline,"Checkpoint observation timeout")
                    await asyncio.sleep(.05)
                await snapshot("checkpoint")
                if early:
                    record("checkpoint_not_reached",**early)
                    await asyncio.to_thread(a.controller.release_all)
                    await terminal("O"); await terminal("I")
                else:
                    pending = await asyncio.to_thread(a.controller.rpc,"status")
                    record("intervention_checkpoint",targets=deepcopy(a.controller.targets),receiver=pending)
                    if arm != "healthy":
                        event={"reaction":"x","item":{"type":"message","channel":"CO","ts":"1.000"}}
                        record("source_stop_requested",event=event,role=old)
                        await asyncio.wait_for(stop.process_slack_stop_reaction(event,event_id=str(uuid.uuid4())),30)
                        record("source_stop_handler_returned")
                        await terminal("O", LIMITS["source_cancel_join_seconds"])
                        if "S" in roles: await terminal("S")
                        oid=a.controller.targets["O"]["operation_id"]
                        pending=await asyncio.to_thread(a.controller.rpc,"status")
                        record("source_stop_pending_receiver",operation_id=oid,state=pending["jobs"][oid])
                        if arm=="durable_cancel":
                            await asyncio.to_thread(a.controller.rpc,"control",kind="cancel",target=oid,durable=True)
                        if arm in {"memory_revoke","durable_revoke"}:
                            await asyncio.to_thread(a.controller.rpc,"control",kind="revoke",
                                target=old["invocation_id"],durable=arm=="durable_revoke")
                    restart = await asyncio.to_thread(a.controller.rpc,"restart",
                        targets=deepcopy(a.controller.targets))
                    record("receiver_restart_bound", receipt=restart)
                    await asyncio.to_thread(a.controller.release_all)
                    await asyncio.to_thread(a.controller.drain)
                    if arm=="healthy": await terminal("O")
                    await terminal("I")
                    old_op = deepcopy(a.controller.targets["O"])
                    duplicate = await asyncio.to_thread(a.controller.rpc,"submit",op=old_op)
                    duplicate_result = await asyncio.to_thread(a.controller.rpc,"execute",operation_id=old_op["operation_id"])
                    record("duplicate_probe",op=old_op,receipt=duplicate,result=duplicate_result)
                    roles["N"]=dict(thread_id=old["thread_id"],invocation_id=str(uuid.uuid4()),job_id="human")
                    await start("N"); await terminal("N")
                    roles["C"]=dict(thread_id=old["thread_id"],invocation_id=str(uuid.uuid4()),job_id="new_background")
                    await start("C",derived=True); await terminal("C")
                await asyncio.to_thread(a.controller.finish)
                record("measurement_closed")
                result["completed"]=True
            finally:
                if not result["completed"]:
                    transport.halt("runtime_abort")
                    for r in roles.values():
                        if "run_id" in r:
                            try: await client.runs.cancel(r["thread_id"],r["run_id"],action="interrupt")
                            except Exception as exc: record("abort_run_cancel_error",error=str(exc))
                await asyncio.to_thread(a.controller.release_all)
                for inv in list(held):
                    if inv in a.base._by_invocation:
                        a.base.release_invocation(inv); held.remove(inv)
                a.base.cleanup()
                await asyncio.to_thread(a.controller.finish)
                await a.base.drain_workers()
        record("native_runtime_closed")
        result["synthetic_wire_requests"]=0 if LIVE else transport.count
        result["wire_requests"]=transport.count
    except BaseException as exc:
        if transport: transport.halt("driver_incomplete")
        record("execution_error",error_type=type(exc).__name__,
               traceback_locations=[dict(file=Path(f.filename).name,line=f.lineno,function=f.name)
                                    for f in traceback.extract_tb(exc.__traceback__)])
        result["error_type"]=type(exc).__name__
    finally:
        if transport:
            await transport.aclose()
            result.update(actual_provider_calls=transport.count if LIVE else 0,
                          new_live_episodes=int(LIVE and transport.count > 0),
                          usage_status=transport.ledger["status"])
        if store: await asyncio.to_thread(store.close)
        await http.aclose()
        record("http_client_closed",closed=http.is_closed)
        await snapshot("final")
        save(out/"result.json",result)
    return result["completed"]


def main(out, conn, api_key=None):
    global LIVE
    plan=json.loads((out/"PLAN.json").read_text())
    LIVE=plan["live"]
    authorization(17, plan["arm"], live=LIVE)
    if LIVE: require(plan["profile"]=="normal" and plan["fault"]=="none","Live deviation not authorized")
    sys.addaudithook(safety)
    log = Journal(out/"source.jsonl","source")
    completed = False
    try:
        log.emit("source_started", provider_access=LIVE)
        completed = asyncio.run(run(out,conn,log,api_key))
        common.call(conn,log,"source_done",completed=completed)
    except BaseException as exc:
        log.emit("source_process_error",error_type=type(exc).__name__)
        raise
    finally:
        log.emit("source_closed",completed=completed)
        conn.close()
        log.close()
    if not completed:
        raise SystemExit(1)
