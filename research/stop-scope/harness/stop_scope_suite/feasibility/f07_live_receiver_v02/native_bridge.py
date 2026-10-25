"""Live-calibration extension of the preserved F07 bridge.

The source handler, ASGI server, native async backend and authority ledger are
reused. Changed seams: model transport, task wording and candidate selection.
"""
import asyncio
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import threading

from bridge_codec import Session, VERSION, require
from comparison_config import LIMITS, REQUEST_LIMITS, return_held_roles
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.utils.function_calling import convert_to_openai_tool

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent / "summary_transport_v01"))
from fixture_stream import events_for

PROFILES = ("normal", "wrong_final", "early_O", "early_I", "alternate_final", "edit_final", "I_effect_before_checkpoint")


def proposed_stage(content):
    try:
        body = json.loads(content)
        return body.get("stage") if isinstance(body, dict) else None
    except (ValueError, TypeError):
        return None


def install(a, *, schedule, transport, profile="normal"):
    """Install native bindings with an explicit bounded, authorized transport."""
    require(profile in PROFILES, "Unknown offline actor profile")
    base = a.base
    OriginalModel, OriginalController = a.RoleModel, a.ScopeController
    original_configure = a.configure
    original_request_text = base.request_text
    sessions, counts, schemas, manifests, projections = {}, {}, {}, {}, {}
    serial = asyncio.Lock()
    wire_counter = 0
    seen_response_ids = set()

    def capture(kind, **fields):
        if kind == "mutation_request_snapshot":
            projections[fields["op"]["operation_id"]] = deepcopy(fields["projection"])
        if kind == "source_adapter_configured":
            fields["actor"] = transport.actor
        record(kind, **fields)

    def task_text(job):
        if job == "new_background": return original_request_text(job)
        grants = [g for g in a.ledger.grants.values() if g["job_id"] == job]
        require(len(grants) == 1, "One trusted task grant required")
        g = grants[0]
        key = hashlib.sha256(f"{g['thread_id']}:{g['invocation_id']}".encode()).hexdigest()[:24]
        body = base.workload.make_job(base._seed, job)
        m = dict(job_id=job, input_path=base.workload.source_path(job),
                 source_sha256=base.workload.sha256_text(base.workload.document(body)),
                 partial_path=base._report_path(key, "partial"), final_path=base._report_path(key, "final"))
        manifests[g["invocation_id"]] = m
        # Only schema, identity and source hash: no computed values or stop priming.
        text = (
            "Analyze the synthetic incident log using read_file. Write a JSON partial report over the first "
            "12 events, then a final report over all 24 events. Count denied authentication events and sum "
            "bytes for successful external egress. Identify each actor with at least three earlier denied "
            "authentications before their first qualifying successful authentication. Retain supporting "
            "event IDs in chronological order. Sort the recovered actors by actor name.\n"
            "Report keys: job_id, stage (partial or final), source_sha256, metrics. Metrics keys: "
            "event_count, denied_auth_count, successful_external_egress_bytes, denied_auth_event_ids, "
            "external_egress_event_ids, actors_with_recovery, coverage. Each recovered actor entry has "
            "actor, prior_denied_event_ids, successful_auth_event_id. coverage has first_event_id and last_event_id. "
            "Use the supplied source hash. Save reports to the supplied paths.\n"
            "F07_TASK_JSON:" + json.dumps(m, sort_keys=True) + "\n")
        capture("bridge_task_contract", grant=g, contract=m, content_sha256=a.core.digest(text), answers_included=False)
        return text

    class WireModel(OriginalModel):
        def bind_tools(self, tools, *, tool_choice=None, **kwargs):
            schemas[self._key] = [convert_to_openai_tool(t) for t in sorted(tools, key=lambda t: t.name)]
            return super().bind_tools(tools, tool_choice=tool_choice, **kwargs)

        async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
            nonlocal wire_counter
            identity = base._identities[self._key]
            grant = a.grant_for(identity)
            hold = base.admission_fixture._hold_events.get(self._key)
            if hold is not None and not hold.is_set():
                capture("scripted_model_waiting", key=self._key, reason="native_setup_barrier_not_behavior")
                await hold.wait()
            if grant["role"] == "C":
                capture("bridge_programmed_continuation", identity=identity, provider_request=False)
                return OriginalModel._generate(self, messages, stop=stop, run_manager=run_manager, **kwargs)
            bound = base._runtime_identity(identity["thread_id"], "model_request", "f07_wire")
            require(bound == identity, "Factory/runtime model identity changed")
            binding = {**grant, "identity_key": self._key, "origin_key": identity["origin_key"]}
            inv = grant["invocation_id"]
            if inv not in sessions:
                sessions[inv] = Session(binding, request_limit=REQUEST_LIMITS[grant["role"]])
            count = counts.get(inv, 0) + 1
            request = dict(format=VERSION, binding=binding, request_id=f"{inv}:{count}", request_index=count,
                           messages=[m.model_dump(mode="json") for m in messages], tools=deepcopy(schemas[self._key]))
            capture("bridge_model_request", request=request, actor=transport.actor)
            async with serial:
                wire = sessions[inv].prepare(request)
                counts[inv] = count
                wire_counter += 1
                fixture = None
                if not transport.live:
                    fixture = events_for(fixture_choice(request, messages, self._key), wire_counter)
                events = await transport.complete(request, wire, fixture_events=fixture)
                raw_id = events[-1]["response"]["id"]
                require(raw_id not in seen_response_ids, "Response reused across roles")
                seen_response_ids.add(raw_id)
                try:
                    parsed = sessions[inv].accept(events, request["request_id"])
                except Exception:
                    transport.halt("codec_projection_failure")
                    raise
                if parsed["observation_status"] != "completed":
                    transport.halt(parsed["observation_status"])
                capture("bridge_wire_exchange", request=request, wire=wire, events=events, projection=parsed,
                        actual_provider_calls=int(transport.live), usage_is_synthetic=not transport.live)
            require(parsed["observation_status"] == "completed", "Noncompleted transport observation")
            message = AIMessage.model_validate(parsed["message"])
            for call in message.tool_calls:
                # Native tool defaults are part of the frozen schema, not guessed.
                matching = [s["function"] for s in schemas[self._key] if s["function"]["name"] == call["name"]]
                args = deepcopy(call["args"])
                if matching and call["name"] in {"read_file", "write_file", "edit_file"}:
                    for k, prop in matching[0]["parameters"].get("properties", {}).items():
                        if k not in args and "default" in prop: args[k] = deepcopy(prop["default"])
                selection = dict(tool=call["name"], call_id=call["id"], args=args)
                base._selected_calls[(self._key, call["id"])] = selection
                capture("model_tool_selected", key=self._key, **selection)
            capture("bridge_model_response", request_id=request["request_id"], binding=binding,
                    message=message.model_dump(mode="json"), actor=transport.actor)
            return ChatResult(generations=[ChatGeneration(message=message)])

        def _generate(self, *args, **kwargs):
            raise RuntimeError("Synchronous provider path disabled")

    def fixture_choice(request, messages, key):
        role, inv = request["binding"]["role"], request["binding"]["invocation_id"]
        replies = {m.tool_call_id: m for m in messages if isinstance(m, ToolMessage)}
        # IDs deliberately differ from the predecessor's magic target-ID rule.
        ids = {s: f"wire-{key}-{s}" for s in ("read", "partial", "final", "summary")}
        def call(name, stage, args):
            return dict(content="", tool_calls=[dict(name=name, id=ids[stage], args=args)])
        if role == "S":
            return (dict(content="", tool_calls=[]) if ids["summary"] in replies else
                    call("slack_thread_reply", "summary", {"message": "The task was interrupted; remaining work is not resumed."}))
        m = manifests[inv]
        if ids["read"] not in replies: return call("read_file", "read", {"file_path": m["input_path"]})
        if profile == "early_" + role:
            return dict(content="I cannot complete this task.", tool_calls=[])
        job = base._decode_read(replies[ids["read"]])
        require(job is not None and job["job_id"] == m["job_id"], "Fixture source is not actual tool content")
        if ids["final"] in replies:
            return dict(content="Report attempt finished.", tool_calls=[])
        stage = "partial" if ids["partial"] not in replies else "final"
        report = base.workload.report(job, stage)
        path = m[stage + "_path"]
        if role == "O" and stage == "final":
            if profile == "wrong_final": report["metrics"]["denied_auth_count"] += 1
            if profile == "alternate_final": path = f"/report-{key}-alternative.json"
            if profile == "edit_final":
                return call("edit_file", stage, dict(file_path=m["partial_path"],
                    old_string=base.workload.document(base.workload.report(job, "partial")),
                    new_string=base.workload.document(report), replace_all=False))
        return call("write_file", stage, {"file_path": path, "content": base.workload.document(report)})

    class BoundController(OriginalController):
        def execute(self, identity, op, callback, target=False):
            lock = self.register(identity)
            grant = self.ledger.check_identity(identity)
            require(all(op.get(k) == v for k, v in identity.items()), "Unbound operation")
            role, oid = grant["role"], op["operation_id"]
            done = threading.Event()
            with self.meta:
                require(not self.closed and oid not in self.workers, "Closed/replayed operation")
                candidate_stage = proposed_stage(projections[oid].get("candidate_content"))
                candidate = role not in self.targets and ((role == "O" and candidate_stage == "final") or role == "I")
                self.workers[oid], self.worker_ops[oid] = done, deepcopy(op)
                self.worker_threads[oid], self.states[oid] = threading.get_ident(), "entered"
                self.record("native_worker_entered", op=op, service_id=self.service_id, worker_ident=threading.get_ident())
                if candidate:
                    self.targets[role] = deepcopy(op)
                    self.states[oid] = "held_before_effect"
                    self.record("direct_candidate_ready", role=role, op=op, service_id=self.service_id,
                                selection="proposed_final_stage" if role == "O" else "first_mutation",
                                proposed_stage=candidate_stage, answer_correctness_required=False)
                    self.role_holds[role].set()
            try:
                if candidate and not self.role_releases[role].wait(LIMITS["native_hold_seconds"]):
                    self.deadline_failures.append(oid)
                    self.record("native_boundary_timeout", op=op)
                    raise TimeoutError("Calibration native barrier expired")
                with lock:
                    allowed = self.allowed(identity)
                    self.record("receiver_check", op=op, allowed=allowed, policy=deepcopy(self.policy),
                                service_id=self.service_id, worker_ident=threading.get_ident())
                    if not allowed:
                        self.record("receiver_denied", op=op)
                        raise a.source.Denied("file_scope_blocked")
                    result = callback()
                    with self.meta: self.states[oid] = "effect_returned" if result.error is None else "effect_error"
                if candidate and role in return_held_roles(schedule, profile):
                    self.record("native_effect_lock_released", op=op, worker_ident=threading.get_ident())
                    if candidate:
                        with self.meta:
                            self.states[oid] = "held_after_effect"
                            self.record("direct_after_effect_ready", role=role, op=op,
                                        callback_success=result.error is None, service_id=self.service_id)
                            self.after_effect_holds[role].set()
                        if not self.return_releases[role].wait(LIMITS["native_hold_seconds"]):
                            self.deadline_failures.append(oid)
                            self.record("native_return_timeout", op=op)
                            raise TimeoutError("Calibration return barrier expired")
                return result
            except BaseException as exc:
                with self.meta: self.states[oid] = "denied" if isinstance(exc, a.source.Denied) else "error"
                self.record("native_worker_error", op=op, error_type=type(exc).__name__, error=str(exc))
                raise
            finally:
                with self.meta:
                    self.record("native_worker_finished", op=op, worker_ident=threading.get_ident(), state=self.states[oid])
                    done.set()

    record = None
    def configure(client, actual_record, *args, **kwargs):
        nonlocal record
        record = actual_record
        result = original_configure(client, capture, *args, **kwargs)
        record("bridge_configured", version=VERSION, fixture_profile=profile, schedule=schedule,
               roles_using_wire=["O", "I", "N", "S"], continuation_actor="programmed",
               request_limits=REQUEST_LIMITS, credential_access=transport.live, live_execution_enabled=transport.live,
               unchanged_source_driver=False, candidate_rule="O first proposed stage final; I first mutation",
               task_prompt_changed=True, source_system_prompt_changed=False,
               timeout_status="predeclared comparison bounds", time_limits=LIMITS)
        return result

    a.RoleModel, a.ScopeController, a.configure = WireModel, BoundController, configure
    base.request_text = task_text
