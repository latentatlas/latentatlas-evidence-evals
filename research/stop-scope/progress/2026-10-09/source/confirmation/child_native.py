"""Real local source handler, native file worker and summary; no provider."""
import asyncio
from copy import deepcopy
import hashlib
import json
import logging
from pathlib import Path
import sys
import threading
import time
import traceback
import uuid

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from contract import require, SEEDS, ARMS, ARM_CONFIG, JOBS, ORDERS, PROFILES, SCHEDULES, ADMISSION_PHASES

require(len(sys.argv) == 8, "Require output, seed, arm, queue order, mutation profile, schedule, I admission phase")
OUT, SEED, ARM, ORDER = Path(sys.argv[1]).resolve(), int(sys.argv[2]), sys.argv[3], sys.argv[4]
PROFILE = sys.argv[5]
SCHEDULE = sys.argv[6]
ADMISSION_PHASE = sys.argv[7]
require(SEED in SEEDS and ARM in ARMS and ORDER in ORDERS and PROFILE in PROFILES and SCHEDULE in SCHEDULES and ADMISSION_PHASE in ADMISSION_PHASES, "Unknown condition")
rows, lock = [], threading.RLock()
journal = (OUT/"events.jsonl").open("x")


def record(kind, **fields):
    with lock:
        row = json.loads(json.dumps({"seq": len(rows)+1, "monotonic_ns": time.monotonic_ns(), "kind": kind, **fields}, default=str))
        rows.append(row); journal.write(json.dumps(row)+"\n"); journal.flush()


def inventory(phase):
    files = []
    for p in sorted((OUT/"files").rglob("*")):
        if p.is_file():
            content = p.read_bytes()
            files.append({"path": str(p.relative_to(OUT)), "content": content.decode(), "sha256": hashlib.sha256(content).hexdigest()})
    record("observer_inventory", phase=phase, files=files)


def safety(event, args):
    if event in {"socket.connect", "socket.bind", "socket.getaddrinfo", "subprocess.Popen", "os.system", "os.exec", "os.posix_spawn"}:
        stack = traceback.extract_stack(limit=12)
        optional = ((event == "socket.bind" and args[1] == ("::1", 0) and any(f.name == "_has_ipv6" for f in stack)) or
                    (event == "subprocess.Popen" and args[0] in {"file", "uname"} and any(f.filename.endswith("/platform.py") for f in stack)))
        record("optional_platform_probe_denied" if optional else "external_operation_blocked", event=event)
        raise PermissionError("Source-stop qualification is offline")


class SourceErrors(logging.Handler):
    def emit(self, event):
        if event.levelno >= logging.WARNING and event.name == "agent.slack.stop":
            record("source_handler_error", logger=event.name, level=event.levelname,
                   message=event.getMessage(), error_type=type(event.exc_info[1]).__name__ if event.exc_info else None,
                   error=str(event.exc_info[1]) if event.exc_info else None)


sys.addaudithook(safety)
logging.getLogger().addHandler(SourceErrors())


async def until(predicate, timeout=45):
    async def wait():
        while not predicate(): await asyncio.sleep(.01)
    await asyncio.wait_for(wait(), timeout)


async def main():
    import httpx
    from langgraph_sdk.client import LangGraphClient
    from langgraph_api.server import app
    import native_adapter as a
    class Transport(httpx.AsyncBaseTransport):
        def __init__(self): self.inner = httpx.ASGITransport(app=app)
        async def handle_async_request(self, request):
            require(request.url.host == "fixture.invalid" and not any(k in request.headers for k in ("authorization", "x-api-key")), "Local credential-free transport only")
            rid = str(uuid.uuid4())
            record("native_http_request", request_id=rid, method=request.method, path=request.url.path,
                   query=request.url.query.decode(), body=request.content.decode())
            response = await self.inner.handle_async_request(request)
            await response.aread()
            record("native_http_response", request_id=rid, status=response.status_code, body=response.text)
            return response
        async def aclose(self): await self.inner.aclose()
    http = httpx.AsyncClient(base_url="http://fixture.invalid", transport=Transport(), trust_env=False)
    client = LangGraphClient(http)
    old = {"thread_id": str(uuid.uuid4()), "invocation_id": str(uuid.uuid4()), "job_id": "old"}
    independent = {"thread_id": str(uuid.uuid4()), "invocation_id": str(uuid.uuid4()), "job_id": "independent"}
    roles = {"O": old, "I": independent}
    held_invocations = set()
    result = {"completed": False, "profile": PROFILE, "schedule": SCHEDULE, "arm": ARM, "summary": "status",
              "seed": SEED, "order": ORDER, "admission_phase": ADMISSION_PHASE, "roles": roles, "actor": "programmed", "actual_provider_calls": 0, "external_slack_deliveries": 0}
    configured = False

    async def terminal(label):
        r = roles[label]
        await asyncio.wait_for(client.runs.join(r["thread_id"], r["run_id"]), 45)
        state = await client.runs.get(r["thread_id"], r["run_id"])
        record("graph_terminal", role=label, run_id=r["run_id"], state=state)
        record("graph_thread_record", role=label, thread_id=r["thread_id"], state=await client.threads.get(r["thread_id"]))
        record("graph_checkpoint", role=label, thread_id=r["thread_id"], state=await a.read_checkpoint(client, r["thread_id"]))
        require(state["status"] in {"success", "error", "interrupted"}, "Graph not terminal")

    def ready(inv):
        key = a.base._by_invocation.get(inv)
        return key is not None and any(r["kind"] == "scripted_model_waiting" and r.get("key") == key for r in rows)

    async def deferred_snapshot(phase):
        items = []
        for prefix, key in (("queue", "pending_messages"), ("autofix", "pending_event")):
            namespace = (prefix, old["thread_id"])
            items.append({"namespace": list(namespace), "key": key, "item": await client.store.get_item(namespace, key)})
        record("deferred_snapshot", phase=phase, items=items)

    def metadata(channel, ts):
        return {"visibility": "public", "owner_type": "user", "owner_login": "fixture-user", "github_login": "fixture-user", "source": "slack",
                "source_context": {"slack_thread": {"channel_id": channel, "thread_ts": ts, "triggering_user_id": "UFIXTURE"}},
                "agent_settings": {"model_id": "openai:gpt-6-astra", "effort": "high", "subagent_model_id": "openai:gpt-6-astra", "subagent_effort": "high", "model_routing_enabled": False, "repo_instructions": None}}

    async def start_work(label, *, hold=False, derived=False):
        r = roles[label]
        grant = a.ledger.declare(label, r["thread_id"], r["invocation_id"], parent=old["invocation_id"] if derived else None)
        if derived: a.base.register_origin(r["invocation_id"], old["invocation_id"], "continuation_probe")
        if hold:
            a.base.hold_invocation(r["invocation_id"]); held_invocations.add(r["invocation_id"])
        context = metadata("CI", "2.000") if label == "I" else metadata("CO", "1.000")
        cfg = {"source": "slack", "github_login": "fixture-user", "repo_explicitly_none": True, "plan_mode": False, "stop_summary": False,
               "invocation_id": r["invocation_id"], "prepare_run_id": r["invocation_id"],
               "slack_thread": context["source_context"]["slack_thread"]}
        content = a.base.request_text(r["job_id"])
        record("work_dispatch", role=label, grant=grant, content=content, content_sha256=a.core.digest(content), configurable=cfg,
               wire_role="user", actual_autonomous_spawn=False)
        run = await client.runs.create(r["thread_id"], "agent", input={"messages": [{"role": "user", "content": content}]}, config={"configurable": cfg}, durability="sync")
        r["run_id"] = run["run_id"]
        record("work_accepted", role=label, **r)

    try:
        record("fixture_configured", seams=a.configure(client, record, OUT/"files", old["invocation_id"], SEED, PROFILE, SCHEDULE, ADMISSION_PHASE))
        configured = True
        from agent.utils.event_loop import pin_single_event_loop
        pin_single_event_loop()
        from agent.slack import stop
        native_dispatch = stop.dispatch_agent_run
        async def dispatch_summary(t, content, configurable, **kwargs):
            require(t == old["thread_id"] and configurable.get("stop_summary") is True, "Unexpected summary dispatch")
            sid = str(uuid.uuid4())
            a.ledger.declare("S", t, sid, parent=old["invocation_id"])
            a.base.register_origin(sid, old["invocation_id"], "stop_summary")
            a.base.hold_invocation(sid); held_invocations.add(sid)
            effective = {**configurable, "invocation_id": sid, "prepare_run_id": sid}
            record("source_summary_dispatch", thread_id=t, invocation_id=sid, origin_invocation_id=old["invocation_id"],
                   content=content, content_sha256=a.core.digest(content), source_configurable=configurable,
                   effective_configurable=effective, source_content_unmodified=True)
            run = await native_dispatch(t, content, effective, **kwargs)
            roles["S"] = {"thread_id": t, "invocation_id": sid, "origin_invocation_id": old["invocation_id"], "run_id": run["run_id"]}
            record("source_summary_accepted", **roles["S"])
            return run
        stop.dispatch_agent_run = dispatch_summary
        async with app.router.lifespan_context(app):
            record("native_runtime_started")
            try:
                await client.threads.create(thread_id=old["thread_id"], metadata=metadata("CO", "1.000"))
                await client.threads.create(thread_id=independent["thread_id"], metadata=metadata("CI", "2.000"))
                await client.store.put_item(("slack_thread_map", "CO"), "1.000", {"thread_id": old["thread_id"]})
                await start_work("O", hold=True)
                await start_work("I", hold=True)
                await until(lambda: all(ready(roles[k]["invocation_id"]) for k in ("O", "I")))
                for job in ("old", "human", "new_background"): await a.base.seed_job(old["thread_id"], job)
                await a.base.seed_job(independent["thread_id"], "independent")
                for r in (old, independent):
                    await client.threads.update(r["thread_id"], metadata={"sandbox_id": a.base.get_backend(r["thread_id"]).id})
                await asyncio.to_thread(inventory, "before_actor")
                for r in (old, independent):
                    a.base.release_invocation(r["invocation_id"]); held_invocations.remove(r["invocation_id"])
                async def boundary_or_terminal():
                    while not all(e.is_set() for e in a.controller.role_holds.values()):
                        for label in ("O", "I"):
                            r = roles[label]
                            state = await client.runs.get(r["thread_id"], r["run_id"])
                            if state["status"] in {"success", "error", "interrupted"} and not a.controller.role_holds[label].is_set():
                                return {"role": label, "state": state}
                        await asyncio.sleep(.02)
                    return None
                early = await asyncio.wait_for(boundary_or_terminal(), 45)
                if early is None:
                    a.controller.release_role("O", "old_target_first_admission")
                    await until(lambda: a.controller.queue_held.is_set())
                    if ADMISSION_PHASE == "after_I_admission":
                        a.controller.release_role("I", "independent_first_admission_before_policy")
                        await until(lambda: any(j["operation_id"] == a.controller.targets["I"]["operation_id"] for j in a.controller.snapshot()["waiting"]))
                await asyncio.to_thread(inventory, "checkpoint")
                if early is not None:
                    record("checkpoint_not_reached", **early)
                    a.controller.release_all("checkpoint_not_reached")
                    await terminal("O"); await terminal("I")
                else:
                    record("intervention_checkpoint", ops=deepcopy(a.controller.targets), schedule=SCHEDULE, arm=ARM,
                           order=ORDER, admission_phase=ADMISSION_PHASE, queue=a.controller.snapshot())
                    if ARM != "healthy":
                        for prefix, key in (("queue", "pending_messages"), ("autofix", "pending_event")):
                            await client.store.put_item((prefix, old["thread_id"]), key, {"fixture_marker": "deferred-cleanup-witness", "messages": []})
                        await deferred_snapshot("before_source")
                    await asyncio.to_thread(a.controller.activate, ARM, a.base._identities[a.base._by_invocation[old["invocation_id"]]])
                    if ARM != "healthy":
                        event = {"reaction": "x", "item": {"type": "message", "channel": "CO", "ts": "1.000"}}
                        record("source_stop_requested", role=deepcopy(old), event=event, event_id=(event_id := str(uuid.uuid4())))
                        await asyncio.wait_for(stop.process_slack_stop_reaction(event, event_id=event_id), 30)
                        record("source_stop_handler_returned")
                        await deferred_snapshot("after_source")
                        await until(lambda: any(r["kind"] == "effect_awaiter_cancelled" and r["op"]["operation_id"] == a.controller.targets["O"]["operation_id"] for r in rows))
                        await terminal("O")
                        if "S" in roles:
                            await until(lambda: ready(roles["S"]["invocation_id"]))
                            a.base.release_invocation(roles["S"]["invocation_id"]); held_invocations.remove(roles["S"]["invocation_id"])
                            await terminal("S")
                        await asyncio.to_thread(inventory, "after_source_before_new")
                        record("source_observation_complete", summary_observed="S" in roles,
                               old_worker_still_pending=not a.controller.jobs[a.controller.targets["O"]["operation_id"]].future.done(),
                               independent_admission_observed=a.controller.targets["I"]["operation_id"] in a.controller.jobs,
                               independent_queue_future_pending=(not a.controller.jobs[a.controller.targets["I"]["operation_id"]].future.done()) if a.controller.targets["I"]["operation_id"] in a.controller.jobs else None,
                               queue=a.controller.snapshot())
                    cfg = ARM_CONFIG[ARM]
                    root = a.controller.targets["O"]["origin_key"]
                    omitted = (a.controller.targets["O"]["operation_id"],) if cfg["fault"] == "omit_target" else ()
                    if cfg["fault"]:
                        record("confirmation_fault_activated", fault=cfg["fault"], root=root,
                               omitted_operation_ids=list(omitted))
                    if cfg["drain"]:
                        started = threading.Event()
                        draining = asyncio.create_task(asyncio.to_thread(a.controller.drain_scope, root,
                                                       omit_ids=omitted, started=started))
                        await until(started.is_set)
                        # Deliberate omitted-worker countercontrol must assess BEFORE releasing O.
                        if not omitted:
                            a.controller.release_queue("experimental_scoped_drain")
                        await asyncio.wait_for(draining, 15)
                        if not omitted and ADMISSION_PHASE == "after_I_admission":
                            await until(a.controller.independent_held.is_set)
                    if cfg["claim"]:
                        await asyncio.to_thread(a.controller.confirm_scope, root, cfg["claim"],
                                                omit_ids=omitted, force_issue=cfg["fault"] == "force_early")
                    record("experimental_assessment_closed", arm=ARM, root=root,
                           drain_requested=cfg["drain"], claim_scope=cfg["claim"],
                           independent_fixture_released=a.controller.independent_release.is_set())
                    if ADMISSION_PHASE == "before_I_admission":
                        a.controller.release_role("I", "independent_first_admission_after_policy")
                        iid = a.controller.targets["I"]["operation_id"]
                        await until(lambda: iid in a.controller.jobs or any(r["kind"] == "queue_admission_denied" and r["op"]["operation_id"] == iid for r in rows))
                    a.controller.release_queue("source_and_admission_observed" if ARM != "healthy" else "healthy_reference")
                    a.controller.release_independent("experimental_assessment_complete")
                    if ARM == "healthy": await terminal("O")
                    await terminal("I")
                    # Close accepted O/I native callers before minting new-human authority.
                    await asyncio.to_thread(a.controller.drain)
                    roles["N"] = {"thread_id": old["thread_id"], "invocation_id": str(uuid.uuid4()), "job_id": "human"}
                    await start_work("N")
                    await terminal("N")
                    await asyncio.to_thread(inventory, "after_new_human")
                    roles["C"] = {"thread_id": old["thread_id"], "invocation_id": str(uuid.uuid4()), "job_id": "new_background"}
                    await start_work("C", derived=True)
                    await terminal("C")
                    await asyncio.to_thread(inventory, "after_continuation_probe")
                await asyncio.to_thread(a.controller.drain)
                await asyncio.to_thread(a.controller.finish)
                await asyncio.to_thread(inventory, "measurement_closed")
                record("measurement_closed")
                result["infrastructure_timing_deviation"] = bool(a.controller.deadline_failures)
                result["completed"] = True
            finally:
                if not result["completed"]:
                    for r in roles.values():
                        if "run_id" in r:
                            try:
                                state = await client.runs.get(r["thread_id"], r["run_id"])
                                if state["status"] in {"pending", "running"}:
                                    await client.runs.cancel(r["thread_id"], r["run_id"], action="interrupt")
                                    record("abort_graph_interrupt_requested", run_id=r["run_id"])
                            except Exception as exc: record("abort_graph_cleanup_error", run_id=r["run_id"], error=str(exc))
                a.controller.release_all("safety_cleanup")
                for inv in list(held_invocations):
                    if inv in a.base._by_invocation:
                        a.base.release_invocation(inv); held_invocations.remove(inv)
                await asyncio.to_thread(a.controller.drain)
                await asyncio.to_thread(a.controller.finish)
                a.base.cleanup(); await a.base.drain_workers()
        record("native_runtime_closed")
    except BaseException as exc:
        result.update(completed=False, error_type=type(exc).__name__, error=str(exc))
        record("execution_error", error_type=type(exc).__name__, error=str(exc), traceback=traceback.format_exc())
        if configured: a.controller.release_all("abort")
    finally:
        await http.aclose(); record("http_client_closed", closed=http.is_closed)
        await asyncio.to_thread(inventory, "final")
        with (OUT/"result.json").open("x") as f: json.dump(result, f, indent=2)
        journal.close()
    return 0 if result["completed"] else 1


if __name__ == "__main__": raise SystemExit(asyncio.run(main()))
