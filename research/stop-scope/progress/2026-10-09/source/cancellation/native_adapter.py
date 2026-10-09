"""O/N/I/C factory execution; preserved native files and source S dispatch."""
import asyncio
from copy import deepcopy
import importlib.util
import sys
import uuid
from contract import SOURCE, PROFILES, require

_before_import = list(sys.path)
spec = importlib.util.spec_from_file_location("preserved_source_adapter", SOURCE/"native_adapter.py")
source = importlib.util.module_from_spec(spec); sys.modules[spec.name] = source; spec.loader.exec_module(source)
base, core = source.base, source.core
# Retain the upstream dependency paths, but never shadow this adapter module.
sys.path.insert(0, _before_import[0])
from authority import AuthorityLedger
from scope_controller import ScopeController
from policy import CallBinder

ledger = None
controller = None
profile = None


def grant_for(identity): return ledger.check_identity(identity)


class RoleModel(source.SourceModel):
    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        if grant_for(base._identities[self._key])["role"] == "S":
            return super().bind_tools(tools, tool_choice=tool_choice, **kwargs)
        declarations = core.schemas(tools)
        base._record("three_tool_contract", key=self._key, schemas=declarations,
                     schema_sha256=core.schema_digest(declarations), provider_request_sent=False)
        return source.OriginalModel.bind_tools(self, tools, tool_choice=tool_choice, **kwargs)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        grant = grant_for(base._identities[self._key])
        if grant["role"] == "S": return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
        snapshot = [m.model_dump(mode="json") for m in messages]
        base._record("model_input", key=self._key, messages=snapshot, messages_sha256=base.workload.sha256_text(base.workload.canonical(snapshot)))
        request, index = base._request(messages)
        base._record("model_request_selected", key=self._key, request=request, message_index=index)
        require(request is not None and request["job_id"] == grant["job_id"], "Task differs from dispatch grant")
        replies = {m.tool_call_id: m for m in messages if isinstance(m, base.ToolMessage)}
        read_id, partial_id, final_id, inspect_id = [p+self._key for p in ("source-", "write-partial-", "target-", "inspect-target-")]
        if read_id not in replies:
            return self._select("read_file", read_id, {"file_path": request["input_path"], "offset": 0, "limit": 2000})
        job = base._decode_read(replies[read_id]); base.workload.validate_job(job)
        require(job["job_id"] == grant["job_id"], "Source/job mismatch")
        base._record("model_source_consumed", key=self._key, call_id=read_id, decoded_job=job, tool_message=replies[read_id].model_dump(mode="json"))
        if partial_id not in replies:
            return self._select("write_file", partial_id, {"file_path": base._report_path(self._key, "partial"), "content": base.workload.document(base.workload.report(job, "partial"))})
        target_path = base._report_path(self._key, "partial" if grant["role"] == "O" and profile != "create" else "final")
        if final_id not in replies:
            partial, final = (base.workload.report(job, stage) for stage in ("partial", "final"))
            if grant["role"] != "O" or profile in {"create", "overwrite"}:
                return self._select("write_file", final_id, {"file_path": target_path, "content": base.workload.document(final)})
            if profile == "edit_full":
                old, new = base.workload.document(partial), base.workload.document(final)
            else:
                metric = "successful_external_egress_bytes"
                old = '"'+metric+'":'+str(partial["metrics"][metric])
                new = '"'+metric+'":'+str(final["metrics"][metric])
            return self._select("edit_file", final_id, {"file_path": target_path, "old_string": old,
                                "new_string": new, "replace_all": False})
        if inspect_id not in replies:
            return self._select("read_file", inspect_id, {"file_path": target_path, "offset": 0, "limit": 2000})
        return self._finish({"fixture_status": "attempts_and_file_observation_complete"})


class RoleSurface(source.SourceSurface):
    async def awrap_model_call(self, request, handler):
        cfg = source.get_config()["configurable"]
        identity = base._identities[base._by_invocation[cfg["invocation_id"]]]
        names = source.SUMMARY_NAMES if grant_for(identity)["role"] == "S" else ("edit_file", "read_file", "write_file")
        tools = sorted([t for t in request.tools if t.name in names], key=lambda t: t.name)
        require(tuple(t.name for t in tools) == names, "Missing role tools")
        text = request.system_message.text
        base._record("source_role_surface", key=identity["key"], names=list(names), system_text=text, system_sha256=core.digest(text), system_text_modified=False)
        return await handler(request.override(tools=tools, tool_choice="auto"))

    async def awrap_tool_call(self, request, handler):
        cfg = source.get_config()["configurable"]
        identity = base._identities[base._by_invocation[cfg["invocation_id"]]]
        if grant_for(identity)["role"] == "S": return await super().awrap_tool_call(request, handler)
        call = request.tool_call
        if call["name"] not in ("edit_file", "read_file", "write_file"):
            base._record("unoffered_tool_rejected", key=identity["key"], call=call, visible_text=source.UNAVAILABLE)
            return base.ToolMessage(content=source.UNAVAILABLE, name=call["name"], tool_call_id=call["id"], status="error")
        return await handler(request)


class RoleSandbox(source.SourceSandbox):
    """Preserve native tool semantics and record every proposal's byte basis."""
    async def _effect(self, tool, args):
        identity = base._runtime_identity(self._fixture_thread_id, tool, args["file_path"])
        cid = base._attribute_call(identity, tool, args)
        payload = args["content"] if tool == "write_file" else args["new_string"]
        op = {**identity, "operation_id": str(uuid.uuid4()), "call_id": cid, "tool": tool,
              "args": deepcopy(args), "virtual_path": args["file_path"], "content_sha256": core.digest(payload)}
        controller.register(identity)
        def capture_request():
            # The same lock protects the byte snapshot, policy transition and native effect.
            with controller.policy_lock:
                target = source.safe_output(self._fixture_root, op["virtual_path"])
                before = target.read_bytes().decode() if target is not None and target.is_file() else None
                candidate = ({"status": "proposed_write", "candidate_content": args["content"],
                              "candidate_sha256": core.digest(args["content"])} if tool == "write_file"
                             else source.project_edit(before, args))
                base._record("effect_requested", op=op)
                base._record("mutation_request_snapshot", op=op, path=str(target) if target is not None else None,
                             before_content=before, before_sha256=core.digest(before), projection=candidate)
                if tool == "edit_file":
                    base._record("edit_request_snapshot", op=op, path=str(target) if target is not None else None,
                                 before_content=before, before_sha256=core.digest(before), projection=candidate)
        await asyncio.to_thread(capture_request)
        result_type = core.WriteResult if tool == "write_file" else core.EditResult
        try:
            try:
                result = await asyncio.to_thread(controller.execute, identity, op, lambda: self._native(op),
                                                cid == "target-"+identity["key"])
            except source.Denied:
                result = result_type(error=source.DENIAL_TEXT)
            except TimeoutError:
                result = result_type(error=source.TIMEOUT_TEXT)
        except asyncio.CancelledError:
            base._record("effect_awaiter_cancelled", op=op)
            raise
        else:
            base._record("effect_returned", op=op, success=result.error is None, error=result.error)
            return result


def configure(client, record, files, invocation, seed, selected_profile, schedule, admission_phase):
    global ledger, controller, profile
    require(selected_profile in PROFILES, "Unknown mutation profile")
    profile = selected_profile
    ledger = AuthorityLedger(record)
    controller = ScopeController(record, base._identities, ledger, schedule)
    source.controller = core.controller = controller
    source.summary_mode = "status"
    base.IncidentFilesystemSandbox = RoleSandbox
    base.IncidentModel = RoleModel
    base._attribute_call = CallBinder(base._selected_calls, record).bind
    seams = base.configure(client, record, files, "cancel_summary", "unheld", invocation, seed)
    server = base.admission_fixture._server; original = server.create_deep_agent
    def create(**kwargs):
        kwargs["middleware"] = [*kwargs.get("middleware", []), RoleSurface()]
        return original(**kwargs)
    server.create_deep_agent = create
    record("source_adapter_configured", profile=profile, schedule=schedule, admission_phase=admission_phase, summary="status", seed=seed,
           actor="programmed", actual_provider_calls=0, original_scope_gate_enforced=False)
    return seams


async def get_graph(config):
    cfg = config["configurable"]
    if cfg.get("__is_for_execution__") is True: ledger.lookup(cfg["invocation_id"], cfg["thread_id"])
    graph = await source.get_graph(config)
    if cfg.get("__is_for_execution__") is True:
        identity = base._identities[base._by_invocation[cfg["invocation_id"]]]
        grant = ledger.check_identity(identity)
        base._record("authority_factory_bound", grant=grant, identity=identity)
    return graph


read_checkpoint = source.read_checkpoint
