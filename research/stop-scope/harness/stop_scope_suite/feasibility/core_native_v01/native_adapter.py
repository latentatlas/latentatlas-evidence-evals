"""Real local Open-SWE with programmed actor and a common native file gate."""
import asyncio
from copy import deepcopy
import hashlib
import importlib.util
import json
import sys
import uuid

from contract import LAB
from controller import NativeController, Denied
from policy import CallBinder, DENIAL_TEXT, TIMEOUT_TEXT
from path_policy import safe_output
from tool_surface import ThreeToolMiddleware, schemas, namespace_tools, digest as schema_digest
from edit_projection import project_edit

sys.path.insert(0, str(LAB / "stop_contract_study"))
spec = importlib.util.spec_from_file_location("core_preserved_base", LAB / "stop_contract_study/factory_support.py")
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
from deepagents.backends.filesystem import FilesystemBackend
from deepagents.backends.protocol import WriteResult, EditResult

controller = None
profile = None


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest() if text is not None else None


class NativeModel(base.IncidentModel):
    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        declarations = schemas(tools)
        base._record("three_tool_contract", key=self._key, schemas=declarations,
                     schema_sha256=schema_digest(declarations), wire_tools=namespace_tools(declarations),
                     provider_request_sent=False)
        return super().bind_tools(tools, tool_choice=tool_choice, **kwargs)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        replies = {m.tool_call_id: m for m in messages if isinstance(m, base.ToolMessage)}
        partial_id = "write-partial-" + self._key
        if partial_id not in replies:
            return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
        snapshot = [m.model_dump(mode="json") for m in messages]
        base._record("model_input", key=self._key, messages=snapshot,
                     messages_sha256=base.workload.sha256_text(base.workload.canonical(snapshot)))
        target_id, inspect_id = "target-"+self._key, "inspect-target-"+self._key
        path = base._report_path(self._key, "final" if profile == "create" else "partial")
        if target_id not in replies:
            job = base._decode_read(replies["source-"+self._key])
            base.workload.validate_job(job)
            partial = base.workload.document(base.workload.report(job, "partial"))
            final = base.workload.document(base.workload.report(job, "final"))
            if profile in {"create", "overwrite"}:
                return self._select("write_file", target_id, {"file_path": path, "content": final})
            old, new = (partial, final) if profile == "edit_full" else ('"event_count":12', '"event_count":24')
            return self._select("edit_file", target_id, {"file_path": path, "old_string": old,
                                "new_string": new, "replace_all": False})
        if inspect_id not in replies:
            return self._select("read_file", inspect_id, {"file_path": path, "offset": 0, "limit": 2000})
        return self._finish({"fixture_status": "target_reply_and_read_observed"})


class NativeSandbox(base.IncidentFilesystemSandbox):
    async def _effect(self, tool, args):
        identity = base._runtime_identity(self._fixture_thread_id, tool, args["file_path"])
        cid = base._attribute_call(identity, tool, args)
        payload = args["content"] if tool == "write_file" else args["new_string"]
        op = {**identity, "operation_id": str(uuid.uuid4()), "call_id": cid, "tool": tool,
              "args": deepcopy(args), "virtual_path": args["file_path"], "content_sha256": digest(payload)}
        lock = controller.register(identity)
        def capture_request():
            with lock:
                base._record("effect_requested", op=op)
                if tool == "edit_file":
                    target = safe_output(self._fixture_root, op["virtual_path"])
                    before = target.read_bytes().decode() if target is not None and target.is_file() else None
                    base._record("edit_request_snapshot", op=op, path=str(target) if target is not None else None,
                                 before_content=before, before_sha256=digest(before), projection=project_edit(before, args))
        await asyncio.to_thread(capture_request)
        result_type = WriteResult if tool == "write_file" else EditResult
        try:
            result = await asyncio.to_thread(controller.execute, identity, op, lambda: self._native(op),
                                             cid == "target-"+identity["key"])
        except Denied:
            result = result_type(error=DENIAL_TEXT)
        except TimeoutError:
            result = result_type(error=TIMEOUT_TEXT)
        base._record("effect_returned", op=op, success=result.error is None, error=result.error)
        return result

    async def awrite(self, file_path, content):
        return await self._effect("write_file", {"file_path": file_path, "content": content})

    async def aedit(self, file_path, old_string, new_string, replace_all=False):
        return await self._effect("edit_file", {"file_path": file_path, "old_string": old_string,
                                  "new_string": new_string, "replace_all": replace_all})

    def write(self, *args, **kwargs):
        raise RuntimeError("Model writes require runtime-bound awrite")

    def edit(self, *args, **kwargs):
        raise RuntimeError("Model edits require runtime-bound aedit")

    def _native(self, op):
        target = safe_output(self._fixture_root, op["virtual_path"])
        result_type = WriteResult if op["tool"] == "write_file" else EditResult
        if target is None:
            base._record("output_boundary_denied", op=op)
            return result_type(error="Output path is outside the permitted local output area.")
        before = target.read_bytes().decode() if target.is_file() else None
        base._record("native_effect_attempt", op=op, path=str(target), before_content=before,
                     before_sha256=digest(before))
        fn = FilesystemBackend.write if op["tool"] == "write_file" else FilesystemBackend.edit
        result = fn(self, **op["args"])
        after = target.read_bytes().decode() if target.is_file() else None
        base._record("native_effect_result", op=op, path=str(target), success=result.error is None,
                     error=result.error, after_content=after, after_sha256=digest(after))
        return result


def configure(client, record, files, invocation, schedule, selected_profile):
    global controller, profile
    profile = selected_profile
    controller = NativeController(record, schedule)
    base.IncidentModel = NativeModel
    base.IncidentFilesystemSandbox = NativeSandbox
    base._attribute_call = CallBinder(base._selected_calls, record).bind
    seams = base.configure(client, record, files, "cancel_summary", "unheld", invocation, 17)
    server = base.admission_fixture._server
    original = server.create_deep_agent
    def create_with_surface(**kwargs):
        kwargs["middleware"] = [*kwargs.get("middleware", []), ThreeToolMiddleware(record)]
        return original(**kwargs)
    server.create_deep_agent = create_with_surface
    record("native_core_configured", actor="programmed", schedule=schedule, profile=profile,
           original_scope_gate_enforced=False, all_file_mutations_receiver_checked=True,
           actual_provider_calls=0)
    return seams


async def get_graph(config):
    return await base.get_graph(config)
