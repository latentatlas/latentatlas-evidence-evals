"""Explicit live transport seam. Native Open-SWE and historical files unedited."""
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / "live_pilot_v02"
sys.path.insert(0, str(PREVIOUS))
import bridge_adapter as bridge
from task_contract import manifest, prompt
from contract import envelope
from tool_binding import normalized_arguments
from oauth_codec import validate_graph_response
from exploration_plan import validate_episode
from stop_observation import StopWindow

_contract = _schemas = _transport = None
_stop_observer = None


def __getattr__(name):
    return getattr(bridge, name)


def attribute_defaults(identity, tool, args):
    active = bridge._active_call.get()
    if not active or active["key"] != identity["key"] or active["tool"] != tool:
        raise RuntimeError("No matching active tool call")
    selected = bridge.base._selected_calls.get((identity["key"], active["call_id"]))
    if not selected or selected["tool"] != tool or _schemas is None:
        raise RuntimeError("Missing selected call/schema")
    if normalized_arguments(tool, selected["args"], _schemas) != args:
        raise RuntimeError("Selected/actual arguments differ")
    bridge.base._record("schema_default_argument_binding", key=identity["key"], call_id=active["call_id"],
                        tool=tool, selected_args=selected["args"], actual_args=args, schema_defaults_verified=True)
    return active["call_id"]


def configure(client, record, files_root, invocation, seed, transport_builder, *, stop_episode=False):
    arm = "instruction_local_gate" if stop_episode else "continue_local_gate"
    validate_episode(seed, "A", arm)
    # Only this fresh process's in-memory seam changes. Do not relabel genuine
    # provider responses as scripted to satisfy the previous test-only validator.
    bridge.validate_response = validate_graph_response
    bridge.BridgeModel._llm_type = property(lambda self: "chatgpt-plan-oauth-exploration-bridge")
    def staged_record(kind, **fields):
        # Observe every visible model-message string, not only selected tools.
        # Selection, text and file effects remain separate observations.
        if kind == "bridge_request" and fields["body"]["phase"] == "post_message":
            from contract import unwrap, operator_message
            body = fields["body"]
            if unwrap(body["operator_text"]) == operator_message(seed, True):
                if _stop_observer is None:
                    raise RuntimeError("Missing source-bound stop observer")
                _stop_observer.begin(body)
        if kind in {"bridge_graph_assembled", "bridge_configured"}:
            record("inherited_setup_description", inherited_kind=kind, fields=fields,
                   note="Preserved factory template labels, not final transport provenance")
        else:
            record(kind, **fields)
        if kind == "bridge_response" and _stop_observer is not None and _stop_observer.pending is not None:
            decision = _stop_observer.complete(fields["body"])
            record("stop_output_decision", observer_version="stop-output-observation-v01", decision=decision)
    result = bridge.configure(client, staged_record, files_root, arm, "write", invocation,
                              None, seed, "A", PREVIOUS / "runs/dev-matrix-v01/prompts")

    def check_binding(request):
        global _schemas
        from copy import deepcopy
        if _schemas is not None and request["tools"] != _schemas:
            raise RuntimeError("Actual schemas changed")
        _schemas = deepcopy(request["tools"])
        identity = bridge.base.initial_identity()
        if _contract is None or any(_contract[s + "_path"] != bridge.base._report_path(identity["key"], s)
                                   for s in ("partial", "final")):
            raise RuntimeError("Task/runtime identity mismatch")
        source = bridge.base.get_backend(identity["thread_id"])._fixture_root / "incident-old.json"
        if hashlib.sha256(source.read_bytes()).hexdigest() != _contract["source_sha256"]:
            raise RuntimeError("Source hash mismatch")
        tasks = [m for m in request["messages"] if m["type"] == "human" and "TASK_CONTRACT_JSON:" in m["content"]]
        if len(tasks) != 1 or tasks[0]["content"] != envelope(prompt(_contract)):
            raise RuntimeError("Actual task text mismatch")
        record("task_contract_runtime_bound", request_id=request["request_id"], key=identity["key"],
               source_sha256=_contract["source_sha256"], task_targets_match=True)

    global _transport
    _transport = transport_builder(check_binding)
    bridge._transport = _transport
    bridge.base._attribute_call = attribute_defaults
    record("oauth_transport_installed", transport=type(_transport).__name__, native_factory=True,
           namespace="functions", tools=["read_file", "write_file"], source_files_modified=False,
           scope="trusted local runtime; not OS sandboxing or full Open-SWE deployed tool inventory")
    return result


def bind_task(thread_id, invocation, seed):
    global _contract, _stop_observer
    if _contract is not None:
        raise RuntimeError("One task per fresh process")
    validate_episode(seed, "A", "continue_local_gate")
    _contract = manifest(thread_id, invocation, seed)
    _stop_observer = StopWindow(seed)
    if _stop_observer.oracle["source_sha256"] != _contract["source_sha256"]:
        raise RuntimeError("Observer source differs from actual task")
    bridge.base._record("task_contract_created", thread_id=thread_id, invocation_id=invocation,
                        contract=_contract, text=prompt(_contract), answers_included=False)


def task_text():
    if _contract is None:
        raise RuntimeError("Bind task first")
    return envelope(prompt(_contract))


async def close_transport(interruption=None):
    if _transport is not None:
        await _transport.aclose()
    if _stop_observer is not None:
        result = _stop_observer.finish(interruption)
        bridge.base._record("stop_output_observation", result=result)
        return result


async def get_graph(config):
    return await bridge.get_graph(config)
