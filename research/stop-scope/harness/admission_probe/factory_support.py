"""Local service seams for the unchanged Open-SWE cloud graph factory.

Requires the upstream locked environment and a dedicated, externally confined
process. This module does not implement network/subprocess confinement; the
runner must deny external access and permit only its local SDK service. It does
not replace credential_scope, auth resolvers, admin decisions, graph assembly,
PrepareAgentRunMiddleware, or any security middleware. Provider answers below
are synthetic; no claim about real credentials or deployed access is supported.

configure(client, journal, root) loads the full source module; get_graph(config)
delegates to its real factory. Journal signature: journal(kind, **fields).
"""

from __future__ import annotations

import asyncio
from contextvars import ContextVar
from copy import deepcopy
from datetime import UTC, datetime, timedelta
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import shlex
import sys
from typing import Any

from deepagents.backends.filesystem import FilesystemBackend
from deepagents.backends.protocol import ExecuteResponse, WriteResult
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import PrivateAttr


SOURCE_ROOT = Path(__file__).resolve().parents[1] / "application_probe" / "upstream"
EXPECTED_SERVER_SHA256 = "a864def43d5d3ba27fe4d9a34229a338e94326fa26c51352aa2872e574dfd314"
SYNTHETIC_TOKEN = "fixture-installation-token-not-a-real-credential"
_server: Any = None
_ready = False
_journal: Any = None
_canary_root: Path | None = None
_backends: dict[str, Any] = {}
_held_invocations: set[str] = set()
_hold_events: dict[str, asyncio.Event] = {}
_monitor_list_command: str | None = None
_task_root: str | None = None
_factory_key: ContextVar[str | None] = ContextVar("canary_factory_key", default=None)
_restores: list[tuple[Any, str, Any]] = []


def _record(kind: str, **fields: Any) -> None:
    if _journal is not None:
        _journal(kind, **fields)


def _replace(owner: Any, name: str, value: Any) -> None:
    _restores.append((owner, name, getattr(owner, name)))
    setattr(owner, name, value)


def _tool_name(value: Any) -> str | None:
    if isinstance(value, dict):
        function = value.get("function")
        return function.get("name") if isinstance(function, dict) else value.get("name")
    return getattr(value, "name", None) or getattr(value, "__name__", None)


def hold_invocation(invocation_id: str) -> None:
    """Fixture-only selection; never add a hold flag to persisted run config."""
    if not isinstance(invocation_id, str) or not invocation_id:
        raise ValueError("Hold requires the exact initial invocation identifier")
    _held_invocations.add(invocation_id)
    _record("scripted_hold_registered", invocation_id=invocation_id)


def get_backend(thread_id: str) -> SyntheticFilesystemSandbox:
    """Return an already-created fixture; do not implicitly provision a sandbox."""
    if thread_id not in _backends:
        raise KeyError("No synthetic sandbox exists for this thread")
    return _backends[thread_id]


def seed_background_task(thread_id: str, status="completed", notification="pending"):
    """Explicit synthetic record, not evidence that a real command executed."""
    if status not in {"running", "completed", "failed", "timed_out", "stopped", "lost"}:
        raise ValueError("Unsupported synthetic task status")
    if notification not in {"pending", "claimed", "done"}:
        raise ValueError("Unsupported synthetic notification state")
    backend = get_backend(thread_id)
    task = {"task_id": "cmd-synthetic-old", "status": status,
            "exit_code": 0 if status == "completed" else None, "duration_seconds": 1,
            "output_path": "/synthetic/output.log", "notification": notification}
    previous = deepcopy(backend.tasks)
    backend.tasks = [task]
    _record("background_task_seeded", thread_id=thread_id, previous=previous, task=deepcopy(task))
    return deepcopy(task)


class PresentedToolCanaryModel(BaseChatModel):
    """Scripted choice from actually presented tools, never a hidden-tool probe."""

    _key: str = PrivateAttr()
    _presented: tuple[str, ...] = PrivateAttr(default=())

    def __init__(self, *, key: str):
        super().__init__(profile={"max_input_tokens": 200000, "tool_calling": True})
        self._key = key

    @property
    def _llm_type(self) -> str:
        return "local-presented-tool-canary"

    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        bound = self.model_copy()
        bound._presented = tuple(sorted(filter(None, (_tool_name(tool) for tool in tools))))
        _record("model_tools_presented", key=self._key, tools=list(bound._presented))
        return bound

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        if self._key in _hold_events and not _hold_events[self._key].is_set():
            raise RuntimeError("Held fixture must use cancellable asynchronous model invocation")
        call_id = f"canary-{self._key}"
        already_attempted = any(
            isinstance(message, AIMessage)
            and any(call.get("id") == call_id for call in message.tool_calls)
            for message in messages
        )
        if "write_file" in self._presented and not already_attempted:
            path = f"/canary-{self._key}.txt"
            message = AIMessage(content="", tool_calls=[{
                "name": "write_file", "id": call_id, "type": "tool_call",
                "args": {"file_path": path, "content": f"Harmless local canary {self._key}\n"},
            }])
            _record("scripted_canary_selected", key=self._key, tool="write_file", path=path)
        else:
            reason = "already_attempted" if already_attempted else "write_file_not_presented"
            message = AIMessage(content="Local scripted diagnostic complete.")
            _record("scripted_model_finished", key=self._key, reason=reason)
        return ChatResult(generations=[ChatGeneration(message=message)])

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        if event := _hold_events.get(self._key):
            _record("scripted_model_waiting", key=self._key)
            try:
                await event.wait()
            except asyncio.CancelledError:
                _record("scripted_model_wait_cancelled", key=self._key)
                raise
        return self._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

    def get_num_tokens(self, text: str) -> int:
        # Deterministic local estimate; not an empirical provider-token claim.
        return max(1, (len(text) + 3) // 4)


class SyntheticFilesystemSandbox(FilesystemBackend):
    """Native virtual-root file writes; no shell or external service execution.

    Open-SWE's real SandboxBackendProxy wraps this object, and its real
    CompositeBackend retains the skill routes. Exact monitor protocol strings
    and benign directory probes receive synthetic responses; no shell runs.
    """

    def __init__(self, root: Path, thread_id: str):
        root.mkdir(parents=True, exist_ok=True)
        super().__init__(root_dir=root, virtual_mode=True)
        self._fixture_root = root
        self._fixture_thread_id = thread_id
        self._fixture_id = "fixture-" + hashlib.sha256(thread_id.encode()).hexdigest()[:16]
        self.tasks: list[dict[str, Any]] = []
        self.locked = False

    @property
    def id(self) -> str:
        return self._fixture_id

    def get_work_dir(self) -> str:
        return "/"

    async def aexecute(self, command: str, *, timeout=None, **kwargs):
        _record("sandbox_protocol_request", thread_id=self._fixture_thread_id,
                command_sha256=hashlib.sha256(command.encode()).hexdigest(), timeout=timeout)
        if _monitor_list_command is not None and command == _monitor_list_command:
            return ExecuteResponse(output=json.dumps({"tasks": deepcopy(self.tasks)}), exit_code=0)
        for task in self.tasks:
            prefix = f"{_task_root}/{task['task_id']}"
            claim, done = shlex.quote(prefix + "/notify.claim"), shlex.quote(prefix + "/notify.done")
            if command == f"mkdir {claim} 2>/dev/null":
                if task["notification"] != "pending":
                    return ExecuteResponse(output="", exit_code=1)
                task["notification"] = "claimed"
            elif command == f"mv {claim} {done}":
                if task["notification"] != "claimed":
                    return ExecuteResponse(output="", exit_code=1)
                task["notification"] = "done"
            elif command == f"rmdir {claim} 2>/dev/null || true":
                if task["notification"] == "claimed":
                    task["notification"] = "pending"
            else:
                continue
            _record("sandbox_notification_state", thread_id=self._fixture_thread_id,
                    task_id=task["task_id"], notification=task["notification"])
            return ExecuteResponse(output="", exit_code=0)
        lock = shlex.quote(f"{_task_root}/monitor.lock")
        if _task_root and command == f"mkdir -p {shlex.quote(_task_root)} && mkdir {lock} 2>/dev/null":
            if self.locked:
                return ExecuteResponse(output="", exit_code=1)
            self.locked = True
        elif _task_root and command == f"rmdir {lock} 2>/dev/null || true":
            self.locked = False
        else:
            return await asyncio.to_thread(self._directory_probe, command)
        _record("sandbox_monitor_lock", thread_id=self._fixture_thread_id, locked=self.locked)
        return ExecuteResponse(output="", exit_code=0)

    def _directory_probe(self, command):
        allowed = command in {"pwd", "test -d / && test -w /"}
        _record("sandbox_command_probe", thread_id=self._fixture_thread_id,
                allowed=allowed, command=command)
        if not allowed:
            raise RuntimeError("Synthetic backend forbids unrecognized shell commands")
        if command == "pwd":
            return ExecuteResponse(output="/\n", exit_code=0)
        writable = self._fixture_root.is_dir() and os.access(self._fixture_root, os.W_OK)
        return ExecuteResponse(output="", exit_code=0 if writable else 1)

    def execute(self, command: str, **kwargs):
        raise RuntimeError("Synthetic backend forbids synchronous shell execution")

    def write(self, file_path: str, content: str) -> WriteResult:
        if not re.fullmatch(r"/canary-[0-9a-f]{24}\.txt", file_path):
            raise RuntimeError("Synthetic effect fixture permits only its canary filenames")
        target = self._fixture_root / file_path.lstrip("/")
        if target.exists():
            raise RuntimeError("Canary overwrite forbidden; use a fresh invocation identifier")
        _record("canary_write_attempt", thread_id=self._fixture_thread_id, path=str(target))
        result = super().write(file_path, content)
        _record("canary_write_result", thread_id=self._fixture_thread_id, path=str(target),
                success=result.error is None,
                sha256=hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None)
        return result


def configure(real_sdk_client, journal_callable, canary_root) -> dict[str, Any]:
    """Configure once, before the server imports agent.server in this process.

    Required synthetic thread metadata: visibility=public, owner_type=user,
    owner_login=fixture-user, no title_seed; ordinary empty Store namespaces
    must return proper SDK missing/search-empty replies, not fabricated grants.
    Recommended agent_settings: valid supported model/effort, routing disabled,
    repo_instructions=None. Seed no MCP connections, environments or admins.
    A caller may test mismatched/private ownership; the real resolver then owns
    the failure. This adapter does not convert such failures into success.
    """
    global _server, _journal, _canary_root, _ready, _monitor_list_command, _task_root
    if _server is not None or _restores:
        raise RuntimeError("Factory support is already configured; use a fresh worker process")
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("Upstream factory requires the locked Python 3.14 environment")
    _journal = journal_callable
    if not callable(_journal):
        raise TypeError("journal_callable must accept kind and keyword fields")
    _canary_root = Path(canary_root).resolve(strict=True)
    if not _canary_root.is_dir() or _canary_root == Path(_canary_root.anchor):
        raise ValueError("canary_root must be a pre-created dedicated directory")
    source = SOURCE_ROOT / "agent/server.py"
    if hashlib.sha256(source.read_bytes()).hexdigest() != EXPECTED_SERVER_SHA256:
        raise RuntimeError("Upstream server.py differs from the reviewed snapshot")
    if "agent.server" in sys.modules:
        raise RuntimeError("Configure before importing agent.server; do not reuse partial/stub loaders")
    import langgraph_sdk
    from langgraph_sdk.client import LangGraphClient
    if not isinstance(real_sdk_client, LangGraphClient):
        raise TypeError("Use a real LangGraphClient connected only to the local fixture service")
    sys.path.insert(0, str(SOURCE_ROOT))
    _replace(langgraph_sdk, "get_client", lambda *args, **kwargs: real_sdk_client)
    stage = "import_external_provider"
    try:
        app = importlib.import_module("agent.github.app")

        async def installation_fixture(*args, **kwargs):
            _record("synthetic_installation_provider_answer", principal="workspace-bot")
            expires = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
            return SYNTHETIC_TOKEN, expires

        # Only the provider answer changes: token choice, private owner checks,
        # token cache/principal binding, and admin guards remain upstream code.
        _replace(app, "get_github_app_installation_token_with_expiry", installation_fixture)
        import httpx2

        def github_get_fixture(url, **kwargs):
            if (url != "https://api.github.com/user"
                    or kwargs.get("headers", {}).get("Authorization") != f"Bearer {SYNTHETIC_TOKEN}"):
                raise RuntimeError("Unexpected synchronous HTTP request outside synthetic /user fixture")
            _record("synthetic_github_user_answer", status=403)
            return httpx2.Response(403, json={"message": "Synthetic installation identity has no user"},
                                   request=httpx2.Request("GET", url))

        _replace(httpx2, "get", github_get_fixture)
        stage = "import_full_factory"
        _server = importlib.import_module("agent.server")
        if Path(_server.__file__).resolve() != source.resolve():
            raise RuntimeError("Imported factory is not the pinned source file")

        async def sandbox_provider(thread_id, **kwargs):
            if not isinstance(thread_id, str) or not thread_id:
                raise ValueError("Synthetic backend requires an explicit thread identity")
            if thread_id not in _backends:
                directory = _canary_root / hashlib.sha256(thread_id.encode()).hexdigest()[:24]
                _backends[thread_id] = await asyncio.to_thread(SyntheticFilesystemSandbox, directory, thread_id)
            _record("synthetic_sandbox_provider_answer", thread_id=thread_id,
                    sandbox_id=_backends[thread_id].id)
            return _backends[thread_id]

        def model_provider(model_id, **kwargs):
            key = _factory_key.get()
            if key is None:
                raise RuntimeError("Model construction occurred outside recorded get_graph factory call")
            _record("scripted_model_provider", key=key, configured_model_id=model_id)
            return PresentedToolCanaryModel(key=key)

        _replace(_server, "ensure_sandbox_for_thread", sandbox_provider)
        _replace(_server, "make_model", model_provider)
        registry = importlib.import_module("agent.sandboxes.providers.registry")

        async def reconnect_provider(sandbox_id=None, *, snapshot_id=None, mem_bytes=None,
                                     vcpus=None, fs_capacity_bytes=None, create_params=None):
            if any(option is not None for option in
                   (snapshot_id, mem_bytes, vcpus, fs_capacity_bytes, create_params)):
                raise RuntimeError("Synthetic reconnect does not provision new resources")
            matches = [backend for backend in _backends.values() if backend.id == sandbox_id]
            if len(matches) != 1:
                raise RuntimeError("Synthetic reconnect requires one exact existing sandbox identity")
            _record("synthetic_sandbox_reconnected", sandbox_id=sandbox_id,
                    thread_id=matches[0]._fixture_thread_id)
            return matches[0]

        _replace(registry, "create_sandbox", reconnect_provider)
        background = importlib.import_module("agent.background_tasks")
        if background.create_sandbox is not reconnect_provider:
            _replace(background, "create_sandbox", reconnect_provider)
        _task_root = background.TASK_ROOT
        _monitor_list_command = (
            f"printf %s {shlex.quote(background.encoded(background.control_script('list', None)))}"
            " | base64 -d | python3"
        )
        _record("factory_support_configured", source_sha256=EXPECTED_SERVER_SHA256,
                guard_replacements=[], preparation_replaced=False)
        _ready = True
        return {"source_sha256": EXPECTED_SERVER_SHA256,
                "seams": ["SDK client construction", "GitHub installation provider answer",
                          "synthetic /user HTTP answer", "sandbox lifecycle provider",
                          "existing-id sandbox reconnect provider", "exact monitor protocol fixture",
                          "model provider"],
                "source_factory": str(source), "canary_root": str(_canary_root)}
    except BaseException as exc:
        _record("factory_support_blocked", stage=stage, error_type=type(exc).__name__)
        raise


async def get_graph(config):
    """Pass the server's actual config to get_agent without rewriting its gates."""
    if _server is None or not _ready:
        raise RuntimeError("configure must succeed before get_graph")
    cfg = config.get("configurable") or {}
    if cfg.get("__is_for_execution__") is not True:
        raise ValueError("Refuse introspection graph: __is_for_execution__ must be true")
    thread_id = cfg.get("thread_id")
    invocation = cfg.get("invocation_id") or cfg.get("prepare_run_id") or cfg.get("run_id")
    if not isinstance(thread_id, str) or not isinstance(invocation, str) or not invocation:
        raise ValueError("Real thread_id and unique invocation_id are required for canary attribution")
    if cfg.get("source") == "desktop" or cfg.get("local_project_path"):
        raise ValueError("Do not substitute the desktop branch for the cloud factory")
    key = hashlib.sha256(f"{thread_id}:{invocation}".encode()).hexdigest()[:24]
    if invocation in _held_invocations:
        _hold_events.setdefault(key, asyncio.Event())
    token = _factory_key.set(key)
    _record("real_factory_entered", key=key, thread_id=thread_id, invocation_id=invocation,
            run_id=cfg.get("run_id"),
            configurable_snapshot={name: cfg.get(name) for name in (
                "thread_id", "run_id", "invocation_id", "prepare_run_id", "source", "stop_summary",
                "background_task_completion", "plan_mode", "github_login", "repo_explicitly_none",
                "__is_for_execution__", "langgraph_auth_user_id", "langgraph_auth_permissions")},
            stop_summary=cfg.get("stop_summary"), background_task_completion=cfg.get("background_task_completion"))
    try:
        graph = await _server.get_agent(config)
        _record("real_factory_returned", key=key, graph_type=type(graph).__name__)
        return graph
    except BaseException as exc:
        _record("real_factory_blocked", key=key, error_type=type(exc).__name__)
        raise
    finally:
        _factory_key.reset(token)
