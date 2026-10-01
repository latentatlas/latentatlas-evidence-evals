"""Local stop-contract study with runtime-bound callers and native effects.

No upstream code is changed. Provider/model/sandbox seams reuse the preserved
admission fixture. Caller authority comes from live RunnableConfig, not a path.
Call IDs are separately attributed to a same-caller selected call; the external
auditor must corroborate them with actual checkpoint/terminal ToolCalls.
"""

from __future__ import annotations

import asyncio
from contextvars import ContextVar
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import threading
import time
from typing import Any
import uuid

from deepagents.backends.filesystem import FilesystemBackend
from deepagents.backends.protocol import ReadResult, WriteResult
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.config import get_config

import workload

ADMISSION_FIXTURE_PATH = Path(__file__).resolve().parents[1] / "admission_probe" / "factory_support.py"
_spec = importlib.util.spec_from_file_location("stop_study_admission_fixture", ADMISSION_FIXTURE_PATH)
if _spec is None or _spec.loader is None or _spec.name in sys.modules:
    raise RuntimeError("Load preserved admission fixture in a fresh process")
admission_fixture = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = admission_fixture
_spec.loader.exec_module(admission_fixture)
SOURCE_ROOT = admission_fixture.SOURCE_ROOT
EXPECTED_SERVER_SHA256 = admission_fixture.EXPECTED_SERVER_SHA256
SYNTHETIC_TOKEN = admission_fixture.SYNTHETIC_TOKEN
REQUEST_MARKER, RESULT_MARKER = workload.REQUEST_MARKER, workload.RESULT_MARKER
ARMS = frozenset({"cancel_summary", "drain_summary", "scoped_summary", "scoped_no_summary"})
SCHEDULES = frozenset({"accepted_precommit", "after_commit", "unheld", "drain_timeout"})
GATE_TIMEOUT_SECONDS = 45.0
DRAIN_TIMEOUT_SECONDS = 20.0
_configured = False
_arm = _schedule = _initial_invocation = _initial_key = None
_seed: int | None = None
_identities: dict[str, dict[str, Any]] = {}
_by_invocation: dict[str, str] = {}
_origin_registrations: dict[str, dict[str, str]] = {}
_selected_calls: dict[tuple[str, str], dict[str, Any]] = {}
_operation: ContextVar[dict[str, Any] | None] = ContextVar("stop_study_operation", default=None)
_track = threading.RLock()
_scope_locks: dict[str, threading.RLock] = {}
_revoked: set[str] = set()
_workers: dict[str, dict[str, Any]] = {}
_done: dict[str, threading.Event] = {}
_gate, _reached = threading.Event(), threading.Event()
_barrier_op: dict[str, Any] | None = None
_released = False
_tasks: dict[str, dict[str, Any]] = {}


def _record(kind: str, **fields: Any) -> None:
    admission_fixture._record(kind, **fields)


def _initialize(arm, schedule, initial_invocation_id, seed):
    global _arm, _schedule, _initial_invocation, _initial_key, _seed, _gate, _reached, _barrier_op, _released
    if arm not in ARMS or schedule not in SCHEDULES or seed not in workload.SEEDS:
        raise ValueError("Use declared arm, schedule and seed")
    if not isinstance(initial_invocation_id, str) or not initial_invocation_id:
        raise ValueError("Require exact initial invocation")
    if any(not event.is_set() for event in _done.values()):
        raise RuntimeError("Cannot replace a schedule with unfinished workers")
    _arm, _schedule, _initial_invocation, _seed = arm, schedule, initial_invocation_id, seed
    _initial_key, _barrier_op, _released = None, None, False
    _gate, _reached = threading.Event(), threading.Event()
    for registry in (_identities, _by_invocation, _origin_registrations, _selected_calls,
                     _scope_locks, _workers, _done, _tasks):
        registry.clear()
    _revoked.clear()


def register_origin(invocation_id: str, origin_invocation_id: str, kind: str) -> dict[str, str]:
    """Trusted local dispatch binding, not a production authentication service."""
    if any(not isinstance(value, str) or not value or len(value) > 200
           for value in (invocation_id, origin_invocation_id, kind)):
        raise ValueError("Origin registration requires bounded explicit identities")
    with _track:
        if invocation_id in _by_invocation:
            raise RuntimeError("Register origin before its actual factory dispatch")
        if origin_invocation_id not in _by_invocation:
            raise RuntimeError("Origin must already have an actual factory identity")
        origin = _identities[_by_invocation[origin_invocation_id]]
        binding = {"invocation_id": invocation_id, "origin_invocation_id": origin["origin_invocation_id"],
                   "immediate_origin_invocation_id": origin_invocation_id, "origin_kind": kind}
        previous = _origin_registrations.get(invocation_id)
        if previous is not None and previous != binding:
            raise RuntimeError("Origin binding cannot be overwritten")
        _origin_registrations[invocation_id] = binding
        _record("origin_registered", **binding)
        return dict(binding)


def _register_factory(config):
    global _initial_key
    cfg = config.get("configurable") or {}
    if cfg.get("__is_for_execution__") is not True:
        raise ValueError("Only actual execution factory contexts are admitted")
    thread_id, run_id = cfg.get("thread_id"), cfg.get("run_id")
    invocation_id = cfg.get("invocation_id") or cfg.get("prepare_run_id") or run_id
    if any(not isinstance(value, str) or not value for value in (thread_id, run_id, invocation_id)):
        raise ValueError("Require actual thread, run and invocation IDs")
    if cfg.get("invocation_id") and cfg.get("prepare_run_id") and cfg["invocation_id"] != cfg["prepare_run_id"]:
        raise ValueError("Invocation and preparation identities differ")
    key = hashlib.sha256(f"{thread_id}:{invocation_id}".encode()).hexdigest()[:24]
    with _track:
        binding = _origin_registrations.get(invocation_id)
        origin_id = binding["origin_invocation_id"] if binding else invocation_id
        if origin_id == invocation_id:
            origin_key = key
        else:
            if origin_id not in _by_invocation:
                raise RuntimeError("Unknown registered origin")
            origin = _identities[_by_invocation[origin_id]]
            if origin["thread_id"] != thread_id:
                raise RuntimeError("Study origin cannot cross thread identity")
            origin_key = origin["key"]
        identity = {"key": key, "thread_id": thread_id, "run_id": run_id,
                    "invocation_id": invocation_id, "origin_invocation_id": origin_id,
                    "origin_key": origin_key, "origin_kind": binding["origin_kind"] if binding else "self",
                    "initial": invocation_id == _initial_invocation}
        if key in _identities and _identities[key] != identity:
            raise RuntimeError("Factory identity was reused with changed fields")
        if invocation_id in _by_invocation and _by_invocation[invocation_id] != key:
            raise RuntimeError("Invocation reused across threads")
        _identities[key], _by_invocation[invocation_id] = identity, key
        _scope_locks.setdefault(origin_key, threading.RLock())
        if identity["initial"]:
            if _initial_key is not None and _initial_key != key:
                raise RuntimeError("Initial identity changed")
            _initial_key = key
        _record("factory_identity_registered", **identity)
        return dict(identity)


def initial_identity() -> dict[str, Any]:
    if _initial_key is None:
        raise RuntimeError("Initial factory identity has not been observed")
    return dict(_identities[_initial_key])


def _runtime_identity(backend_thread_id, operation_kind, virtual_path):
    # Resolve authority before interpreting any model-supplied path or content.
    live = get_config()
    cfg = live.get("configurable") or {}
    snapshot = {name: cfg.get(name) for name in ("thread_id", "run_id", "invocation_id", "prepare_run_id")}
    invocation = snapshot["invocation_id"] or snapshot["prepare_run_id"] or snapshot["run_id"]
    with _track:
        key = _by_invocation.get(invocation)
        if key is None:
            _record("runtime_identity_rejected", operation_kind=operation_kind, virtual_path=virtual_path,
                    runtime_config_snapshot=snapshot, reason="unknown_invocation")
            raise RuntimeError("Live tool caller is not an admitted factory invocation")
        identity = dict(_identities[key])
    if (snapshot["thread_id"] != identity["thread_id"] or snapshot["run_id"] != identity["run_id"]
            or backend_thread_id != identity["thread_id"]
            or (snapshot["prepare_run_id"] and snapshot["prepare_run_id"] != invocation)):
        _record("runtime_identity_rejected", operation_kind=operation_kind, virtual_path=virtual_path,
                runtime_config_snapshot=snapshot, reason="factory_or_backend_mismatch")
        raise RuntimeError("Live tool caller does not match factory/backend identity")
    _record("runtime_identity_bound", **identity, operation_kind=operation_kind,
            virtual_path=virtual_path, runtime_config_snapshot=snapshot,
            authority_source="live_runnable_config_and_actual_factory_registry")
    return identity


def _report_path(key, stage):
    return f"/report-{key}-{stage}.json"


def _attribute_call(identity, tool, args):
    with _track:
        matches = [call for (key, _), call in _selected_calls.items()
                   if key == identity["key"] and call["tool"] == tool and call["args"] == args]
    if len(matches) != 1:
        raise RuntimeError("Effect attribution requires one same-caller selected tool call")
    return matches[0]["call_id"]


def _text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(item if isinstance(item, str) else item.get("text", "")
                         for item in content if isinstance(item, str) or
                         (isinstance(item, dict) and isinstance(item.get("text"), str)))
    return ""


def _decode_read(message):
    if not isinstance(message, ToolMessage) or message.name != "read_file" or message.status != "success":
        return None
    text = _text(message.content)
    try:
        return json.loads(text)
    except ValueError:
        logical, last_line, last_part = [], 0, 0
        for row in text.splitlines():
            match = re.fullmatch(r"\s*(\d+)(?:\.(\d+))?(?:  |\t)(.*)", row)
            if match is None:
                return None
            line, part = int(match[1]), int(match[2] or 0)
            if part == 0 and line == last_line + 1:
                logical.append(match[3])
            elif part > 0 and line == last_line and part == last_part + 1:
                logical[-1] += match[3]
            else:
                return None
            last_line, last_part = line, part
        try:
            return json.loads("\n".join(logical))
        except ValueError:
            return None


def _request(messages):
    for index in range(len(messages) - 1, -1, -1):
        for line in reversed(_text(messages[index].content).splitlines()):
            if line.strip().startswith(REQUEST_MARKER):
                try:
                    request = json.loads(line.strip()[len(REQUEST_MARKER):])
                    if (set(request) != {"job_id", "input_path"}
                            or request["input_path"] != workload.source_path(request["job_id"])):
                        raise ValueError("Invalid request identity")
                    return request, index
                except (ValueError, TypeError, KeyError):
                    return None, index
    return None, None


class IncidentModel(admission_fixture.PresentedToolCanaryModel):
    def _select(self, tool, call_id, args):
        if tool not in self._presented:
            raise RuntimeError("Never select a hidden tool")
        call = {"tool": tool, "call_id": call_id, "args": deepcopy(args)}
        with _track:
            previous = _selected_calls.get((self._key, call_id))
            if previous is not None and previous != call:
                raise RuntimeError("Selected call identity changed")
            _selected_calls[(self._key, call_id)] = call
        _record("model_tool_selected", key=self._key, **call)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content="", tool_calls=[
            {"id": call_id, "name": tool, "type": "tool_call", "args": args}]))])

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        if self._key in admission_fixture._hold_events and not admission_fixture._hold_events[self._key].is_set():
            raise RuntimeError("Held setup uses the cancellable async model method")
        snapshots = [message.model_dump(mode="json") for message in messages]
        _record("model_input", key=self._key, messages=snapshots,
                messages_sha256=workload.sha256_text(workload.canonical(snapshots)))
        request, request_index = _request(messages)
        _record("model_request_selected", key=self._key, request=request, message_index=request_index)
        own_calls = {call["id"]: call for message in messages if isinstance(message, AIMessage)
                     for call in message.tool_calls if (self._key, call.get("id")) in _selected_calls}
        replies = {message.tool_call_id: message for message in messages if isinstance(message, ToolMessage)
                   and message.tool_call_id in own_calls}
        job, source_message = None, None
        source_call = f"source-{self._key}"
        if request is not None:
            if source_call not in own_calls and "read_file" in self._presented:
                return self._select("read_file", source_call,
                                    {"file_path": request["input_path"], "offset": 0, "limit": 2000})
            source_message = replies.get(source_call)
            candidate = _decode_read(source_message)
            if candidate is not None:
                try:
                    workload.validate_job(candidate)
                    if candidate["job_id"] != request["job_id"]:
                        raise ValueError("Read job differs from latest request")
                    job = candidate
                except (ValueError, TypeError, KeyError):
                    pass
        if job is None:
            return self._finish({"job_id": request["job_id"] if request else None, "metrics": None,
                                 "source_sha256": None, "result_source": "unavailable", "artifacts": {}})
        _record("model_source_consumed", key=self._key, call_id=source_call,
                tool_message=source_message.model_dump(mode="json"), decoded_job=job)
        metrics = workload.analyze(job)
        _record("model_computed", key=self._key, job_id=job["job_id"], metrics=metrics,
                source_sha256=workload.sha256_text(workload.document(job)))
        identity = _identities[self._key]
        # Only namespace comes from trusted binding, never source values or
        # expected answers. Restricted summaries inspect their origin files.
        artifact_key = self._key if "write_file" in self._presented else identity["origin_key"]
        if "write_file" in self._presented:
            for stage in ("partial", "final"):
                call_id = f"write-{stage}-{self._key}"
                if call_id not in own_calls:
                    return self._select("write_file", call_id,
                                        {"file_path": _report_path(self._key, stage),
                                         "content": workload.document(workload.report(job, stage))})
        artifacts = {}
        for stage in ("partial", "final"):
            path = _report_path(artifact_key, stage)
            call_id = f"inspect-{stage}-{self._key}"
            if call_id not in own_calls and "read_file" in self._presented:
                return self._select("read_file", call_id, {"file_path": path, "offset": 0, "limit": 2000})
            reply = replies.get(call_id)
            decoded = _decode_read(reply)
            expected = workload.report(job, stage)
            if decoded == expected:
                observation = {"path": path, "status": "verified", "exists": True,
                               "sha256": workload.sha256_text(workload.document(decoded))}
            elif (reply is not None and reply.name == "read_file" and reply.status == "error"
                  and _text(reply.content) == f"Error: File '{path}' not found"):
                observation = {"path": path, "status": "observed_missing", "exists": False, "sha256": None}
            else:
                observation = {"path": path, "status": "unverified", "exists": None, "sha256": None}
            artifacts[stage] = observation
            _record("model_artifact_observed", key=self._key, stage=stage, call_id=call_id,
                    observation=observation, tool_message=reply.model_dump(mode="json") if reply else None)
        return self._finish({"job_id": job["job_id"], "metrics": metrics, "result_source": "read_file",
                             "source_sha256": workload.sha256_text(workload.document(job)), "artifacts": artifacts})

    def _finish(self, result):
        content = RESULT_MARKER + workload.canonical(result)
        _record("model_finished", key=self._key, result=result, content=content)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])


class IncidentFilesystemSandbox(admission_fixture.SyntheticFilesystemSandbox):
    async def awrite(self, file_path, content):
        identity = _runtime_identity(self._fixture_thread_id, "write", file_path)
        match = re.fullmatch(r"/report-([0-9a-f]{24})-(partial|final)\.json", file_path)
        if match is None or match[1] != identity["key"]:
            _record("write_identity_rejected", **identity, virtual_path=file_path, reason="target_namespace_not_caller")
            raise RuntimeError("Report target must belong to actual runtime caller")
        call_id = _attribute_call(identity, "write_file", {"file_path": file_path, "content": content})
        op_id = str(uuid.uuid4())
        op = {**identity, "operation_id": op_id, "worker_id": op_id, "call_id": call_id,
              "stage": match[2], "virtual_path": file_path, "content_sha256": workload.sha256_text(content)}
        _record("write_awaiter_entered", **op, call_id_binding="same_caller_full_args_selection_corroborated_by_auditor")
        token = _operation.set(op)
        try:
            result = await super().awrite(file_path, content)
        except asyncio.CancelledError:
            _record("awrite_cancelled", **op)
            raise
        else:
            _record("write_awaiter_returned", **op, success=result.error is None, error=result.error)
            return result
        finally:
            _operation.reset(token)

    def write(self, file_path, content):
        op = _operation.get()
        if op is None or op["thread_id"] != self._fixture_thread_id or op["virtual_path"] != file_path:
            raise RuntimeError("Native write requires propagated runtime-bound operation")
        if op["content_sha256"] != workload.sha256_text(content):
            raise RuntimeError("Native payload changed after runtime binding")
        done, state = threading.Event(), {**op, "finished": False, "success": False, "denied": False, "error_type": None}
        with _track:
            if op["operation_id"] in _workers:
                raise RuntimeError("Operation may enter native worker only once")
            _workers[op["operation_id"]], _done[op["operation_id"]] = state, done
            _record("worker_entered", **op)
        try:
            target = self._fixture_root / file_path.lstrip("/")
            schedule_target = op["key"] == _initial_key and op["stage"] == "final"
            if schedule_target:
                partial = self._fixture_root / _report_path(op["key"], "partial").lstrip("/")
                if not partial.is_file():
                    raise RuntimeError("Initial final write requires an existing partial report")
                _record("initial_partial_verified", **op, partial_path=str(partial),
                        partial_sha256=hashlib.sha256(partial.read_bytes()).hexdigest())
                if _schedule in {"accepted_precommit", "drain_timeout"}:
                    _wait_gate(op)
            _record("scope_lock_requested", **op)
            requested_ns = time.monotonic_ns()
            with _scope_locks[op["origin_key"]]:
                acquired_ns = time.monotonic_ns()
                _record("scope_lock_acquired", **op, wait_ns=acquired_ns - requested_ns)
                revoked, enforced = op["origin_key"] in _revoked, _arm in {"scoped_summary", "scoped_no_summary"}
                allowed = not (revoked and enforced)
                _record("scope_check", **op, revoked=revoked, enforced=enforced, allowed=allowed)
                if not allowed:
                    state["denied"] = True
                    result = WriteResult(error="Origin scope withdrawn before native write")
                else:
                    if target.exists():
                        raise RuntimeError("Report overwrite forbidden")
                    _record("native_write_attempt", **op, path=str(target), content=content)
                    result = FilesystemBackend.write(self, file_path, content)
                    _record("native_write_result", **op, path=str(target), content=content,
                            success=result.error is None, error=result.error,
                            sha256=hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None)
                state["success"] = result.error is None
            _record("scope_lock_released", **op)
            if schedule_target and _schedule == "after_commit":
                if not state["success"]:
                    raise RuntimeError("After-commit schedule requires successful native effect")
                _wait_gate(op)
            return result
        except BaseException as exc:
            state["error_type"] = type(exc).__name__
            raise
        finally:
            with _track:
                state["finished"] = True
                _record("worker_finished", **op, success=state["success"], denied=state["denied"], error_type=state["error_type"])
                done.set()

    async def aread(self, file_path, offset=0, limit=2000):
        if file_path in {"/AGENTS.md", "/CLAUDE.md"}:
            return await super().aread(file_path, offset, limit)
        identity = _runtime_identity(self._fixture_thread_id, "read", file_path)
        call_id = _attribute_call(identity, "read_file", {"file_path": file_path, "offset": offset, "limit": limit})
        op = {**identity, "operation_id": str(uuid.uuid4()), "call_id": call_id, "virtual_path": file_path,
              "stage": "source" if file_path.startswith("/incident-") else "inspection"}
        token = _operation.set(op)
        try:
            return await super().aread(file_path, offset, limit)
        finally:
            _operation.reset(token)

    def read(self, file_path, offset=0, limit=2000):
        benign = file_path in {"/AGENTS.md", "/CLAUDE.md"}
        op = _operation.get() or {}
        allowed_source = file_path in {workload.source_path(job) for job in workload.JOB_IDS}
        match = re.fullmatch(r"/report-([0-9a-f]{24})-(partial|final)\.json", file_path)
        allowed_report = bool(match and match[1] in _identities
                              and _identities[match[1]]["thread_id"] == self._fixture_thread_id)
        if not benign and (not op or op.get("thread_id") != self._fixture_thread_id or not (allowed_source or allowed_report)):
            raise RuntimeError("Read outside named local workload files")
        target = self._fixture_root / file_path.lstrip("/")
        fields = dict(op) if op else {"thread_id": self._fixture_thread_id, "virtual_path": file_path}
        _record("native_read_attempt", **fields, path=str(target), offset=offset, limit=limit, benign_probe=benign)
        result = FilesystemBackend.read(self, file_path, offset, limit)
        _record("native_read_result", **fields, path=str(target), offset=offset, limit=limit,
                benign_probe=benign, success=result.error is None, error=result.error,
                file_data=deepcopy(result.file_data),
                sha256=hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None)
        return result

    def edit(self, *args, **kwargs):
        raise RuntimeError("Study backend forbids edit")

    def delete(self, *args, **kwargs):
        raise RuntimeError("Study backend forbids deletion")


def _wait_gate(op):
    global _barrier_op
    with _track:
        if _reached.is_set() or _released:
            raise RuntimeError("Initial final barrier can be reached only once")
        _barrier_op = dict(op)
        _record("barrier_reached", **op, schedule=_schedule)
        _reached.set()
    if not _gate.wait(GATE_TIMEOUT_SECONDS):
        _record("barrier_timeout", **op, schedule=_schedule)
        raise TimeoutError("Scheduling fixture timed out; invalid experiment")


def barrier_reached():
    return _reached.is_set()


def release_barrier(reason):
    global _released
    if not isinstance(reason, str) or not reason:
        raise ValueError("Barrier release reason required")
    with _track:
        if _schedule != "unheld" and not _reached.is_set() and reason != "cleanup":
            raise RuntimeError("Barrier not yet reached")
        if not _released:
            _record("barrier_released", **(_barrier_op or {}), schedule=_schedule, reason=reason)
            _released = True
        _gate.set()


async def revoke_initial():
    identity = initial_identity()
    def revoke():
        _record("withdrawal_requested", **identity)
        requested_ns = time.monotonic_ns()
        with _scope_locks[identity["origin_key"]]:
            acquired_ns = time.monotonic_ns()
            if identity["origin_key"] in _revoked:
                raise RuntimeError("Origin already withdrawn")
            _revoked.add(identity["origin_key"])
            result = {**identity, "revoked": True, "enforced": _arm in {"scoped_summary", "scoped_no_summary"},
                      "wait_ns": acquired_ns - requested_ns, "arm": _arm}
            _record("scope_withdrawn", **result)
            return result
    return await asyncio.to_thread(revoke)


async def drain_initial(timeout):
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0 or timeout > 60:
        raise ValueError("Use a finite drain deadline in (0,60]")
    identity = initial_identity()
    def drain():
        started = time.monotonic_ns()
        deadline = time.monotonic() + timeout
        with _track:
            targets = [(op_id, event) for op_id, event in _done.items() if _workers[op_id]["key"] == identity["key"]]
            if not any(_workers[op_id]["stage"] == "final" for op_id, _ in targets):
                raise RuntimeError("Initial drain requires an observed final worker; partial-only is not quiescence")
        completed = all(event.wait(max(0, deadline - time.monotonic())) for _, event in targets)
        result = {"completed": completed, "timed_out": not completed,
                  "operation_ids": [op_id for op_id, _ in targets],
                  "wait_ns": time.monotonic_ns() - started, "timeout_seconds": timeout}
        _record("initial_drain_result", **identity, **result)
        return result
    return await asyncio.to_thread(drain)


async def drain_workers():
    def drain():
        deadline = time.monotonic() + DRAIN_TIMEOUT_SECONDS
        while True:
            with _track:
                targets = list(_done.items())
            for op_id, event in targets:
                if not event.wait(max(0, deadline - time.monotonic())):
                    raise TimeoutError(f"Worker not drained: {op_id}")
            with _track:
                if len(targets) == len(_done) and all(event.is_set() for event in _done.values()):
                    result = {"workers": deepcopy(list(_workers.values())), "all_finished": True,
                              "scope_count": len(_scope_locks), "revoked_count": len(_revoked),
                              "identity_count": len(_identities), "origin_binding_count": len(_origin_registrations),
                              "task_binding_count": len(_tasks)}
                    _record("workers_drained", **result)
                    return result
    return await asyncio.to_thread(drain)


def cleanup():
    release_barrier("cleanup")
    for event in admission_fixture._hold_events.values():
        event.set()


def configure(client, record, files_root, arm, schedule, initial_invocation_id, seed):
    global _configured
    if _configured:
        raise RuntimeError("Use fresh isolated process")
    _initialize(arm, schedule, initial_invocation_id, seed)
    admission_fixture.PresentedToolCanaryModel = IncidentModel
    admission_fixture.SyntheticFilesystemSandbox = IncidentFilesystemSandbox
    result = admission_fixture.configure(client, record, files_root)
    _configured = True
    _record("study_fixture_configured", arm=arm, schedule=schedule, seed=seed,
            initial_invocation_id=initial_invocation_id, dependency_path=str(ADMISSION_FIXTURE_PATH),
            authority_source="live_runnable_config_and_actual_factory_registry",
            call_id_source="same_caller_full_args_selection_corroborated_by_auditor",
            per_origin_locks=True, inherited_async_write_delegated=True, cancellation_suppressed=False)
    return result


async def get_graph(config):
    _register_factory(config)
    return await admission_fixture.get_graph(config)


def get_backend(thread_id):
    return admission_fixture.get_backend(thread_id)


def hold_invocation(invocation_id):
    return admission_fixture.hold_invocation(invocation_id)


def release_invocation(invocation_id):
    key = _by_invocation.get(invocation_id)
    event = admission_fixture._hold_events.get(key)
    if event is None or event.is_set():
        raise ValueError("No unreleased held invocation")
    event.set()
    _record("scripted_hold_released", invocation_id=invocation_id, key=key)


async def seed_job(thread_id, job_id):
    backend = get_backend(thread_id)
    job = workload.make_job(_seed, job_id)
    path, content = workload.source_path(job_id), workload.document(job)
    target = backend._fixture_root / path.lstrip("/")
    def seed():
        with target.open("x", encoding="utf-8", newline="") as handle:
            handle.write(content)
        _record("job_seeded", thread_id=thread_id, job_id=job_id, virtual_path=path,
                path=str(target), content=content, sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    await asyncio.to_thread(seed)
    return path


def request_text(job_id):
    return workload.request_text(job_id)


def seed_background_task(thread_id, task_id, job_id, origin_invocation_id):
    if not isinstance(task_id, str) or not re.fullmatch(r"cmd-[a-z0-9-]{1,80}", task_id):
        raise ValueError("Use bounded synthetic cmd task ID")
    workload.source_path(job_id)
    with _track:
        if origin_invocation_id not in _by_invocation:
            raise RuntimeError("Task origin not admitted")
        origin = _identities[_by_invocation[origin_invocation_id]]
        if origin["thread_id"] != thread_id:
            raise RuntimeError("Task origin belongs to another thread")
        binding = {"thread_id": thread_id, "task_id": task_id, "job_id": job_id,
                   "origin_invocation_id": origin["origin_invocation_id"], "origin_key": origin["origin_key"]}
        if task_id in _tasks:
            raise RuntimeError("Task identity cannot be reseeded; use a distinct retry ID")
        backend = get_backend(thread_id)
        previous = deepcopy(backend.tasks)
        task = {"task_id": task_id, "status": "completed", "exit_code": 0, "duration_seconds": 1,
                "output_path": workload.source_path(job_id), "notification": "pending"}
        _tasks[task_id] = binding
        backend.tasks.append(task)
        _record("background_task_seeded", **binding, previous=previous, task=deepcopy(task))
        return deepcopy(task)


def task_identity(task_id):
    with _track:
        if task_id not in _tasks:
            raise KeyError("Unknown task identity")
        return dict(_tasks[task_id])


def task_registry():
    with _track:
        return deepcopy(_tasks)
