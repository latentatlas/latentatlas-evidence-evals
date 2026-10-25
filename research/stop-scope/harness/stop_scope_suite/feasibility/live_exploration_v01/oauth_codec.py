"""ChatGPT-plan wire adapter. Pure transformations; no credentials or network.

Original provider events remain unchanged. The graph gets a separately labelled
projection, never a fabricated scripted-local response or a compliance verdict.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys

PREVIOUS = Path(__file__).resolve().parent.parent / "live_pilot_v02"
if str(PREVIOUS) not in sys.path:
    sys.path.append(str(PREVIOUS))
from responses_codec import ContractError, require, strict_loads, flatten_tools, view
from wire_contract import digest, validate_request
from tool_binding import normalized_arguments
from langchain_core.messages import AIMessage

MODEL = "gpt-6-astra"
NAMESPACE = "functions"
TERMINALS = {"response.completed": "completed", "response.incomplete": "incomplete", "response.failed": "failed"}


def reconcile(events):
    """Join completed stream items, checking identities and text/argument deltas.

Empty terminal output was observed in the connectivity test. It is an explicit
transport deviation, not permission to fill in missing output-item.done events.
    """
    require(isinstance(events, list) and events, "empty stream")
    require([e.get("sequence_number") for e in events] == list(range(len(events))), "stream sequence gap")
    require(events[0].get("type") == "response.created", "missing initial response")
    terminal = [e for e in events if e.get("type") in TERMINALS]
    require(len(terminal) == 1 and terminal[0] is events[-1], "missing/ambiguous terminal")
    response = terminal[0].get("response", {})
    rid = response.get("id")
    require(isinstance(rid, str) and rid, "missing response ID")
    require(all(e["response"].get("id") == rid for e in events if "response" in e), "response identity mismatch")
    require(response.get("status") == TERMINALS[terminal[0]["type"]], "terminal status mismatch")
    require(not any(e.get("type") == "error" for e in events), "stream error")
    added, done, deltas, final_parts = {}, {}, {}, {}
    for event in events:
        kind = event.get("type", "")
        if kind == "response.output_item.added":
            idx, item = event.get("output_index"), event.get("item", {})
            require(type(idx) is int and idx == len(added), "output index discontinuity")
            require(item.get("id") and all(v.get("id") != item["id"] for v in added.values()), "duplicate item ID")
            require(item.get("type") in {"message", "function_call", "reasoning"}, "unsupported output item")
            added[idx] = item
        elif kind == "response.output_item.done":
            idx, item = event.get("output_index"), event.get("item", {})
            require(idx in added and idx not in done and item.get("id") == added[idx].get("id")
                    and item.get("type") == added[idx].get("type"), "output completion mismatch")
            done[idx] = item
        elif kind.startswith(("response.output_text.", "response.function_call_arguments.")):
            idx = event.get("output_index")
            require(idx in added and event.get("item_id") == added[idx].get("id"), "delta item mismatch")
            field = "text" if kind.startswith("response.output_text.") else "arguments"
            key = (idx, field, event.get("content_index", 0))
            if kind.endswith(".delta"):
                require(key not in final_parts and isinstance(event.get("delta"), str), "late/invalid delta")
                deltas[key] = deltas.get(key, "") + event["delta"]
            elif kind.endswith(".done"):
                require(key not in final_parts and event.get(field) == deltas.get(key, ""), "delta/final mismatch")
                final_parts[key] = event[field]
            else:
                raise ContractError("unsupported output-text/argument event")
        elif kind in {"response.content_part.added", "response.content_part.done"}:
            idx = event.get("output_index")
            require(idx in added and event.get("item_id") == added[idx].get("id"), "content identity mismatch")
        elif kind.startswith(("response.reasoning_", "response.refusal.")):
            idx = event.get("output_index")
            require(idx in added and event.get("item_id") == added[idx].get("id"), "reasoning/refusal identity mismatch")
        elif kind not in {"response.created", "response.in_progress", *TERMINALS}:
            raise ContractError("unrecognized stream event")
    # Incomplete records are retained, but partial calls never reach a tool.
    if response["status"] != "completed":
        return {"response": deepcopy(response), "output_items": [], "terminal_output_omitted": False,
                "actionable": False}
    require(added and set(added) == set(done), "unfinished output item")
    outputs = [done[i] for i in range(len(done))]
    for idx, item in enumerate(outputs):
        if item["type"] == "function_call":
            require(final_parts.get((idx, "arguments", 0)) == item.get("arguments"), "function arguments uncorroborated")
        elif item["type"] == "message":
            for ci, part in enumerate(item.get("content", [])):
                if part.get("type") == "output_text":
                    require(final_parts.get((idx, "text", ci)) == part.get("text"), "message text uncorroborated")
                    parts = [e.get("part") for e in events if e.get("type") == "response.content_part.done"
                             and e.get("output_index") == idx and e.get("content_index") == ci]
                    require(len(parts) == 1 and parts[0] == part, "content part mismatch")
    aggregate = response.get("output")
    require(aggregate == [] or aggregate == outputs, "terminal/item output conflict")
    return {"response": deepcopy(response), "output_items": deepcopy(outputs),
            "terminal_output_omitted": aggregate == [], "actionable": True}


def validate_graph_response(request, response):
    require(response.get("record_type") == "chatgpt_plan_response_projection"
            and response.get("request_id") == request["request_id"]
            and response.get("request_sha256") == digest(request), "graph response binding")
    require(response.get("status") == "completed" and response.get("provider_response_id"), "nonterminal graph projection")
    message = response["message"]
    require(message.get("type") == "ai" and not message.get("invalid_tool_calls"), "invalid graph message")
    calls = message.get("tool_calls", [])
    require(len(calls) <= 1, "parallel calls outside declared slice")
    past = {c["id"] for m in request["messages"] for c in m.get("tool_calls", [])}
    for call in calls:
        require(isinstance(call.get("id"), str) and call["id"] and call["id"] not in past, "reused call identity")
        normalized = normalized_arguments(call["name"], call["args"], request["tools"])
        require(isinstance(normalized.get("file_path"), str), "invalid file path")
        if call["name"] == "read_file":
            require(type(normalized["offset"]) is int and normalized["offset"] >= 0
                    and type(normalized["limit"]) is int and normalized["limit"] > 0, "invalid read bounds")
    return message


class Session:
    def __init__(self):
        self.history, self.items, self.pending = [], [], {}
        self.instructions = self.tools = self.active = None
        self.request_ids, self.response_ids, self.item_ids, self.call_ids = set(), set(), set(), set()
        self.closed = False

    def prepare(self, request):
        require(not self.closed and self.active is None, "closed/inflight session")
        validate_request(request)
        require(request["request_id"] not in self.request_ids, "reused request")
        messages = request["messages"]
        require(messages[0]["type"] == "system" and all(m["type"] != "system" for m in messages[1:]), "system boundary")
        instruction, tools = view(messages[0])["content"], flatten_tools(request["tools"])
        require(self.instructions is None or (instruction == self.instructions and tools == self.tools), "prompt/tool drift")
        history = [view(m) for m in messages[1:]]
        require(history[:len(self.history)] == self.history, "history rewritten")
        extra = history[len(self.history):]
        require(extra, "no new input")
        items, pending = deepcopy(self.items), dict(self.pending)
        for message in extra:
            if message["type"] == "human":
                require(not pending, "user precedes pending tool result")
                items.append({"type": "message", "role": "user", "content": message["content"]})
            elif message["type"] == "tool":
                cid = message["tool_call_id"]
                require(cid in pending and message["name"] == pending[cid], "tool result identity mismatch")
                items.append({"type": "function_call_output", "call_id": cid, "output": message["content"],
                              "name": pending.pop(cid), "namespace": NAMESPACE})
            else:
                raise ContractError("unrecorded assistant message")
        require(not pending, "missing tool result")
        wire = {"model": MODEL, "reasoning": {"effort": "high"}, "service_tier": "default",
                "instructions": instruction, "input": items, "store": False, "stream": True,
                "tools": [{"type": "namespace", "name": NAMESPACE, "description": "Local file tools.", "tools": tools}],
                "tool_choice": "auto", "parallel_tool_calls": False, "include": ["reasoning.encrypted_content"]}
        self.active = {"request": deepcopy(request), "wire": deepcopy(wire), "history": history, "tools": tools}
        self.request_ids.add(request["request_id"])
        return wire

    def accept(self, events, request_id):
        require(self.active is not None and not self.closed, "no active request")
        try:
            return self._accept(events, request_id)
        except Exception:
            self.closed = True
            raise

    def _accept(self, events, request_id):
        active = self.active
        require(active["request"]["request_id"] == request_id, "wrong local request")
        reconciled = reconcile(events)
        body, outputs = reconciled["response"], reconciled["output_items"]
        require(reconciled["actionable"], "incomplete/failed observation; not compliance")
        require(body.get("error") is None and body.get("incomplete_details") is None, "contradictory completion")
        require(body.get("model") == MODEL and (body.get("reasoning") or {}).get("effort") == "high"
                and body.get("service_tier") == "default", "model/effort/tier drift")
        require(body["id"] not in self.response_ids, "reused provider response")
        usage = body.get("usage")
        require(isinstance(usage, dict), "missing usage")
        require(all(type(usage.get(k)) is int and usage[k] >= 0 for k in ("input_tokens", "output_tokens", "total_tokens")), "invalid usage")
        require(usage["input_tokens"] + usage["output_tokens"] == usage["total_tokens"], "token total mismatch")
        require(usage["input_tokens"] <= 24000 and usage["output_tokens"] <= 128000, "reservation assumptions exceeded")
        for details, name, total in (("input_tokens_details", "cached_tokens", "input_tokens"), ("output_tokens_details", "reasoning_tokens", "output_tokens")):
            n = (usage.get(details) or {}).get(name)
            require(type(n) is int and 0 <= n <= usage[total], "missing/invalid usage detail")
        texts, calls, ids, cids, namespace_resolutions = [], [], set(), set(), []
        for item in outputs:
            iid = item.get("id")
            require(iid and iid not in ids and iid not in self.item_ids, "reused item")
            ids.add(iid)
            require(item.get("status") in (None, "completed"), "unfinished item")
            if item["type"] == "reasoning":
                require(isinstance(item.get("encrypted_content"), str) and item["encrypted_content"], "missing opaque reasoning replay")
            elif item["type"] == "function_call":
                # The documented namespace field is optional. Resolve omission
                # only when exactly one offered tool has this exact name. Keep
                # the raw item unchanged; never repair an explicit wrong value.
                offered = [t for t in active["tools"] if t["name"] == item.get("name")]
                require(len(offered) == 1 and item.get("namespace") in (None, NAMESPACE)
                        and item.get("async") in (None, False)
                        and item.get("caller") in (None, {"type": "direct"}), "wrong namespace or indirect call")
                namespace_resolutions.append({"item_id": iid, "name": item["name"], "namespace": NAMESPACE,
                    "basis": "explicit" if item.get("namespace") == NAMESPACE else "unique_exact_offered_name"})
                cid = item.get("call_id")
                require(isinstance(cid, str) and cid and cid not in cids and cid not in self.call_ids, "reused call")
                cids.add(cid)
                calls.append({"type": "tool_call", "id": cid, "name": item.get("name"), "args": strict_loads(item.get("arguments"))})
            elif item["type"] == "message":
                require(item.get("role") == "assistant" and item.get("status") == "completed", "invalid message")
                for part in item.get("content", []):
                    require(part.get("type") == "output_text" and isinstance(part.get("text"), str), "refusal/unsupported content, not compliance")
                    texts.append(part["text"])
        require(calls or any(texts), "no decision")
        message = AIMessage(content="\n".join(texts), tool_calls=calls).model_dump(mode="json")
        envelope = {"record_type": "chatgpt_plan_response_projection", "request_id": request_id,
                    "request_sha256": digest(active["request"]), "status": "completed", "message": message,
                    "provider_response_id": body["id"], "reported_model": body["model"], "provider_usage": deepcopy(usage)}
        validate_graph_response(active["request"], envelope)
        self.history, self.items = active["history"] + [view(message)], deepcopy(active["wire"]["input"]) + deepcopy(outputs)
        self.pending = {c["id"]: c["name"] for c in calls}
        self.instructions, self.tools = active["wire"]["instructions"], active["tools"]
        self.response_ids.add(body["id"])
        self.item_ids.update(ids)
        self.call_ids.update(cids)
        self.active = None
        return {"envelope": envelope, "usage": deepcopy(usage), "output_items": outputs,
                "namespace_resolutions": namespace_resolutions,
                "terminal_output_omitted": reconciled["terminal_output_omitted"]}
