"""Reuse frozen native file semantics; add caller-cancel receipts and actual S."""
import asyncio
from copy import deepcopy
from contextvars import ContextVar
import importlib.util
import json
import sys
import uuid

from contract import CORE, require, SUMMARY_SCHEMA_SHA256
spec = importlib.util.spec_from_file_location("preserved_native_core", CORE/"native_adapter.py")
core = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = core
spec.loader.exec_module(core)
base = core.base
OriginalModel = base.IncidentModel
from lineage import LineageController
from controller import Denied
from policy import CallBinder, DENIAL_TEXT, TIMEOUT_TEXT
from path_policy import safe_output
from edit_projection import project_edit
from tool_surface import schemas, digest as schema_digest, UNAVAILABLE
from langchain.agents.middleware.types import AgentMiddleware
from langchain_core.utils.function_calling import convert_to_openai_tool
from langgraph.config import get_config

controller = None
summary_mode = None
SUMMARY_NAMES = ("read_file", "slack_thread_reply")
_graphs = {}
_checkpoint_read = ContextVar("source_stop_checkpoint_read", default=None)


class SourceModel(core.NativeModel):
    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        identity = base._identities[self._key]
        if identity["initial"]:
            return super().bind_tools(tools, tool_choice=tool_choice, **kwargs)
        declarations = [convert_to_openai_tool(t) for t in sorted(tools, key=lambda t: t.name)]
        require(tuple(d["function"]["name"] for d in declarations) == SUMMARY_NAMES, "Summary tool surface changed")
        require(schema_digest(declarations) == SUMMARY_SCHEMA_SHA256, "Frozen summary schemas changed")
        base._record("summary_tool_contract", key=self._key, schemas=declarations,
                     schema_sha256=schema_digest(declarations), provider_request_sent=False)
        return OriginalModel.bind_tools(self, tools, tool_choice=tool_choice, **kwargs)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        identity = base._identities[self._key]
        if identity["initial"]:
            return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
        require(identity["origin_kind"] == "stop_summary", "Undeclared non-root actor")
        snapshot = [m.model_dump(mode="json") for m in messages]
        base._record("summary_model_input", key=self._key, messages=snapshot,
                     messages_sha256=base.workload.sha256_text(base.workload.canonical(snapshot)))
        replies = {m.tool_call_id: m for m in messages if isinstance(m, base.ToolMessage)}
        reply_id, read_id = "summary-reply-"+self._key, "summary-source-"+self._key
        if reply_id in replies:
            base._record("summary_model_finished", key=self._key)
            return base.ChatResult(generations=[base.ChatGeneration(message=base.AIMessage(content=""))])
        if summary_mode == "status":
            text = "A stop was requested. This summary contains no additional analysis results."
        else:
            if summary_mode == "final_read" and read_id not in replies:
                return self._select("read_file", read_id, {"file_path": "/incident-old.json", "offset": 0, "limit": 2000})
            source_id = read_id if summary_mode == "final_read" else "source-"+identity["origin_key"]
            job = base._decode_read(replies.get(source_id))
            base.workload.validate_job(job)
            require(job["job_id"] == "old", "Wrong summary source")
            text = base.workload.document(base.workload.report(job, "final"))
            base._record("summary_source_basis", key=self._key, source_call_id=source_id,
                         route="reread" if summary_mode == "final_read" else "retained_tool_reply",
                         source_sha256=base.workload.sha256_text(base.workload.document(job)))
        return self._select("slack_thread_reply", reply_id, {"message": text})


class SourceSurface(AgentMiddleware):
    async def awrap_model_call(self, request, handler):
        cfg = get_config()["configurable"]
        identity = base._identities[base._by_invocation[cfg["invocation_id"]]]
        names = ("edit_file", "read_file", "write_file") if identity["initial"] else SUMMARY_NAMES
        tools = sorted([t for t in request.tools if t.name in names], key=lambda t: t.name)
        require(tuple(t.name for t in tools) == names, "Required native tools missing")
        text = request.system_message.text
        base._record("source_role_surface", key=identity["key"], names=list(names),
                     system_text=text, system_sha256=core.digest(text), system_text_modified=False)
        return await handler(request.override(tools=tools, tool_choice="auto"))

    async def awrap_tool_call(self, request, handler):
        call = request.tool_call
        cfg = get_config()["configurable"]
        identity = base._identities[base._by_invocation[cfg["invocation_id"]]]
        names = ("edit_file", "read_file", "write_file") if identity["initial"] else SUMMARY_NAMES
        if call["name"] not in names:
            base._record("unoffered_tool_rejected", key=identity["key"], call=deepcopy(call), visible_text=UNAVAILABLE)
            return base.ToolMessage(content=UNAVAILABLE, name=call["name"], tool_call_id=call["id"], status="error")
        if call["name"] == "slack_thread_reply":
            bound = base._runtime_identity(identity["thread_id"], "slack_thread_reply", "local-summary-sink")
            require(not bound["initial"] and bound["origin_kind"] == "stop_summary", "Unbound summary output")
            cid = base._attribute_call(bound, call["name"], call["args"])
            require(cid == call["id"], "Summary call identity mismatch")
            destination = cfg["slack_thread"]
            require(destination["channel_id"] == "CO" and destination["thread_ts"] == "1.000", "Wrong local output destination")
            base._record("summary_local_delivery", identity=bound, call=deepcopy(call),
                         destination=deepcopy(destination), text=call["args"]["message"],
                         text_sha256=core.digest(call["args"]["message"]), external_delivery=False)
            return base.ToolMessage(content=json.dumps({"success": True, "sink": "local_only"}),
                                    name=call["name"], tool_call_id=cid)
        return await handler(request)


class SourceSandbox(core.NativeSandbox):
    async def _effect(self, tool, args):
        identity = base._runtime_identity(self._fixture_thread_id, tool, args["file_path"])
        cid = base._attribute_call(identity, tool, args)
        payload = args["content"] if tool == "write_file" else args["new_string"]
        op = {**identity, "operation_id": str(uuid.uuid4()), "call_id": cid, "tool": tool,
              "args": deepcopy(args), "virtual_path": args["file_path"], "content_sha256": core.digest(payload)}
        lock = controller.register(identity)
        def capture_request():
            with lock:
                base._record("effect_requested", op=op)
                if tool == "edit_file":
                    target = safe_output(self._fixture_root, op["virtual_path"])
                    before = target.read_bytes().decode() if target is not None and target.is_file() else None
                    base._record("edit_request_snapshot", op=op, path=str(target) if target is not None else None,
                                 before_content=before, before_sha256=core.digest(before), projection=project_edit(before, args))
        await asyncio.to_thread(capture_request)
        result_type = core.WriteResult if tool == "write_file" else core.EditResult
        try:
            try:
                result = await asyncio.to_thread(controller.execute, identity, op, lambda: self._native(op),
                                                 identity["initial"] and cid == "target-"+identity["key"])
            except Denied:
                result = result_type(error=DENIAL_TEXT)
            except TimeoutError:
                result = result_type(error=TIMEOUT_TEXT)
        except asyncio.CancelledError:
            base._record("effect_awaiter_cancelled", op=op)
            raise
        else:
            base._record("effect_returned", op=op, success=result.error is None, error=result.error)
            return result


def configure(client, record, files, invocation, schedule, selected_profile, selected_summary):
    global controller, summary_mode
    summary_mode = selected_summary
    core.profile = selected_profile
    controller = LineageController(record, schedule, base._identities)
    core.controller = controller
    base.IncidentFilesystemSandbox = SourceSandbox
    base.IncidentModel = SourceModel
    base._attribute_call = CallBinder(base._selected_calls, record).bind
    seams = base.configure(client, record, files, "cancel_summary", "unheld", invocation, 17)
    server = base.admission_fixture._server
    original = server.create_deep_agent
    def create(**kwargs):
        kwargs["middleware"] = [*kwargs.get("middleware", []), SourceSurface()]
        return original(**kwargs)
    server.create_deep_agent = create
    record("source_adapter_configured", profile=selected_profile, schedule=schedule, summary=selected_summary,
           actor="programmed", actual_provider_calls=0, original_scope_gate_enforced=False)
    return seams


async def get_graph(config):
    cfg = config["configurable"]
    if cfg.get("__is_for_execution__") is not True:
        thread = _checkpoint_read.get()
        require(thread is not None and cfg.get("thread_id") == thread and thread in _graphs,
                "Only explicitly scoped observer state reads may reuse a compiled graph")
        base._record("observer_graph_reused", thread_id=thread, execution=False)
        return _graphs[thread]
    graph = await base.get_graph(config)
    controller.register(base._identities[base._by_invocation[cfg["invocation_id"]]])
    _graphs[cfg["thread_id"]] = graph
    return graph


async def read_checkpoint(client, thread_id):
    token = _checkpoint_read.set(thread_id)
    try:
        return await client.threads.get_state(thread_id)
    finally:
        _checkpoint_read.reset(token)
