"""Offline projection only. Bodies below are extracted unchanged from pinned sources.

AIMessage is a serialization adapter, not LangChain or a model implementation.
Its output is checked against all 64 archived native messages in this package.
No HTTP, token store, SDK or credential module is imported.
"""
from copy import deepcopy
from decimal import Decimal
import hashlib
import json

MODEL = 'gpt-6-astra'
EFFORT = 'high'
VERSION = 'f07-chatgpt-wire-v01-development'
NAMESPACE = 'functions'
TERMINALS = {'response.completed': 'completed', 'response.incomplete': 'incomplete', 'response.failed': 'failed'}
TOOLS = {'O': {'read_file', 'write_file', 'edit_file'},
         'I': {'read_file', 'write_file', 'edit_file'},
         'N': {'read_file', 'write_file', 'edit_file'},
         'S': {'read_file', 'slack_thread_reply'}}


class AIMessage:
    def __init__(self, *, content, tool_calls):
        self.content, self.tool_calls = content, tool_calls

    def model_dump(self, *, mode):
        if mode != 'json': raise ValueError('Only saved JSON messages are supported')
        return dict(content=self.content, additional_kwargs={}, response_metadata={}, type='ai',
                    name=None, id=None, tool_calls=deepcopy(self.tool_calls), invalid_tool_calls=[],
                    usage_metadata=None)


class ConnectionError(ValueError):
    """Local malformed-stream error. No connection is opened."""


class ContractError(ValueError):
    pass


def require(value, reason):
    if not value:
        raise ContractError(reason)


def strict_loads(raw):
    require(isinstance(raw, (str, bytes)) and len(raw) <= 2_000_000, "unbounded or non-JSON payload")
    def pairs(items):
        output = {}
        for key, value in items:
            require(key not in output, "duplicate JSON property")
            output[key] = value
        return output
    def reject_constant(value):
        raise ContractError("non-finite JSON number: " + value)
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=reject_constant)
    except (ValueError, UnicodeError) as exc:
        raise ContractError(str(exc)) from exc


def view(message):
    """Only transport semantics, not IDs/metadata later assigned by the graph."""
    require(isinstance(message.get("content"), str), "this slice supports text messages only")
    result = {"type": message["type"], "content": message["content"]}
    if message["type"] == "ai":
        require(not message.get("invalid_tool_calls"), "invalid graph tool calls")
        result["tool_calls"] = deepcopy(message.get("tool_calls", []))
    if message["type"] == "tool":
        result.update(tool_call_id=message["tool_call_id"], name=message.get("name"), status=message.get("status", "success"))
    return result

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def validate_history(messages):
    pending, seen = set(), set()
    for message in messages:
        kind = message.get("type")
        if pending and kind != "tool":
            raise ValueError("unanswered tool call before another message")
        if kind == "ai":
            for call in message.get("tool_calls", []):
                cid = call.get("id")
                if not isinstance(cid, str) or not cid or cid in seen:
                    raise ValueError("duplicate or absent tool call ID")
                seen.add(cid)
                pending.add(cid)
        elif kind == "tool":
            cid = message.get("tool_call_id")
            if cid not in pending:
                raise ValueError("orphan or duplicate tool result")
            pending.remove(cid)
        elif kind not in {"system", "human"}:
            raise ValueError("unsupported message role")
    if pending:
        raise ValueError("pending tool result at model boundary")

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

def parse_events(lines):
    """SSE data blocks, including multi-line JSON and a final block without LF."""
    pending = []
    for line in [*lines, ""]:
        if not line:
            if pending:
                data = "\n".join(pending)
                pending = []
                if data != "[DONE]":
                    event = json.loads(data)
                    if not isinstance(event, dict) or not isinstance(event.get("type"), str):
                        raise ConnectionError("invalid_stream_event")
                    yield event
        elif line.startswith("data:"):
            pending.append(line[5:].lstrip(" "))


def usage_quote(response):
    usage = response.get("usage")
    unknown = {"status": "unknown", "standard_credit_equivalent": None}
    if not isinstance(usage, dict):
        return unknown
    counts = [usage.get(k) for k in ("input_tokens", "output_tokens", "total_tokens")]
    if any(type(n) is not int or n < 0 for n in counts) or counts[0] + counts[1] != counts[2]:
        return {**unknown, "status": "invalid_usage"}
    inp, output, _ = counts
    details = usage.get("input_tokens_details") or {}
    out_details = usage.get("output_tokens_details") or {}
    if not isinstance(details, dict) or not isinstance(out_details, dict):
        return {**unknown, "status": "invalid_usage"}
    cache = details.get("cached_tokens")
    reasoning = out_details.get("reasoning_tokens")
    if ((cache is not None and (type(cache) is not int or not 0 <= cache <= inp))
            or (reasoning is not None and (type(reasoning) is not int or not 0 <= reasoning <= output))):
        return {**unknown, "status": "invalid_usage"}
    if response.get("service_tier") != "default":
        return {**unknown, "status": "reported_tier_not_confirmed_standard"}
    if not str(response.get("model", "")).startswith(MODEL) or inp > 272000:
        return {**unknown, "status": "outside_rate_assumptions"}
    cached = cache or 0
    quote = Decimal((inp - cached) * 250 + cached * 25 + output * 1250) / Decimal(1000000)
    return {"status": "provider_usage_observed", "input_tokens": inp,
            "cached_input_tokens": cache, "output_tokens": output,
            "reasoning_tokens": reasoning, "total_tokens": counts[2],
            "standard_credit_equivalent": str(quote),
            "quote_is_upper_estimate_if_cache_detail_missing": cache is None,
            "actual_purchased_credit_debit_known": False}

def flatten(schemas, role):
    require(role in TOOLS, "Only O/I/N/S use the model transport; C is programmed")
    names = [s["function"]["name"] for s in schemas]
    require(len(names) == len(TOOLS[role]) and set(names) == TOOLS[role], "Role tool drift")
    return [{"type": "function", **deepcopy(s["function"]), "strict": False} for s in schemas]


def imported_history(history):
    """Import framework history, explicitly not old provider reasoning replay."""
    validate_history(history)
    items, pending = [], {}
    for m in history:
        if m["type"] == "human":
            items.append({"type": "message", "role": "user", "content": m["content"]})
        elif m["type"] == "ai":
            if m["content"]:
                items.append({"type": "message", "role": "assistant", "content": m["content"]})
            for c in m.get("tool_calls", []):
                pending[c["id"]] = c["name"]
                items.append({"type": "function_call", "name": c["name"], "call_id": c["id"],
                              "namespace": NAMESPACE, "arguments": json.dumps(c["args"], ensure_ascii=False)})
        elif m["type"] == "tool":
            name = pending.pop(m["tool_call_id"], None)
            require(name is not None and m.get("name") in (None, name), "Imported tool identity")
            items.append({"type": "function_call_output", "call_id": m["tool_call_id"],
                          "name": name, "namespace": NAMESPACE, "output": m["content"]})
    require(not pending, "Unanswered imported call")
    return items


class Session:
    def __init__(self, binding, *, request_limit):
        require(binding["role"] in TOOLS and request_limit > 0, "Invalid transport grant")
        self.binding = deepcopy(binding)
        self.limit = request_limit
        self.history, self.items, self.pending = [], [], {}
        self.instructions = self.tools = self.active = None
        self.count = 0
        self.response_ids, self.item_ids, self.call_ids = set(), set(), set()
        self.closed = False

    def prepare(self, request):
        require(not self.closed and self.active is None, "Closed/inflight session")
        require(request["format"] == VERSION and request["binding"] == self.binding, "Request authority mismatch")
        require(self.count < self.limit, "Observation request bound reached")
        require(request["request_index"] == self.count + 1 and request["request_id"] ==
                f"{self.binding['invocation_id']}:{self.count + 1}", "Request identity/order")
        messages = request["messages"]
        require(messages and messages[0]["type"] == "system" and
                all(m["type"] != "system" for m in messages[1:]), "System boundary")
        instruction = view(messages[0])["content"]
        tools = flatten(request["tools"], self.binding["role"])
        history = [view(m) for m in messages[1:]]
        validate_history(history)
        if self.count == 0:
            items = imported_history(history)
            self.call_ids.update(c["id"] for m in history for c in m.get("tool_calls", []))
        else:
            require(instruction == self.instructions and tools == self.tools, "In-session prompt/tool drift")
            require(history[:len(self.history)] == self.history, "Native history changed")
            extra = history[len(self.history):]
            require(extra, "No new input")
            items, pending = deepcopy(self.items), dict(self.pending)
            for m in extra:
                if m["type"] == "tool":
                    name = pending.pop(m["tool_call_id"], None)
                    require(name is not None and m.get("name") in (None, name), "Tool result identity")
                    items.append({"type": "function_call_output", "call_id": m["tool_call_id"],
                                  "name": name, "namespace": NAMESPACE, "output": m["content"]})
                elif m["type"] == "human":
                    require(not pending, "Human message precedes tool reply")
                    items.append({"type": "message", "role": "user", "content": m["content"]})
                else:
                    raise ValueError("Unrecorded assistant output")
            require(not pending, "Missing native tool result")
        wire = {"model": MODEL, "reasoning": {"effort": EFFORT}, "service_tier": "default",
                "instructions": instruction, "input": items, "store": False, "stream": True,
                "tools": [{"type": "namespace", "name": NAMESPACE,
                           "description": "Local synthetic research tools.", "tools": tools}],
                "tool_choice": "auto", "parallel_tool_calls": False,
                "include": ["reasoning.encrypted_content"]}
        self.active = dict(request=deepcopy(request), history=history, wire=deepcopy(wire), tools=tools)
        self.count += 1
        return wire

    def accept(self, events, request_id):
        require(self.active is not None and not self.closed, "No inflight request")
        active = self.active
        require(request_id == active["request"]["request_id"], "Response owner mismatch")
        joined = reconcile(events)
        body = joined["response"]
        require(body["id"] not in self.response_ids, "Reused provider response")
        self.response_ids.add(body["id"])
        common = dict(record_type=VERSION + "-projection", request_id=request_id,
                      request_sha256=digest(active["request"]), binding=deepcopy(self.binding),
                      provider_response_id=body["id"], reported_model=body.get("model"),
                      provider_usage=deepcopy(body.get("usage")), status=body["status"])
        if not joined["actionable"]:
            self.closed, self.active = True, None
            return {**common, "message": None, "observation_status": "provider_" + body["status"]}
        require(body.get("error") is None and body.get("incomplete_details") is None, "Conflicting terminal state")
        if (body.get("model") != MODEL or (body.get("reasoning") or {}).get("effort") != EFFORT
                or body.get("service_tier") != "default"):
            self.closed, self.active = True, None
            return {**common, "message": None, "observation_status": "provider_configuration_drift"}
        texts, calls, choices, items_seen, calls_seen = [], [], [], set(), set()
        for item in joined["output_items"]:
            iid = item["id"]
            require(iid not in items_seen and iid not in self.item_ids, "Reused output item")
            items_seen.add(iid)
            if item["type"] == "reasoning":
                require(item.get("encrypted_content"), "Missing opaque reasoning replay")
            elif item["type"] == "function_call":
                require(item.get("namespace") in (None, NAMESPACE), "Unexpected namespace")
                cid = item.get("call_id")
                require(isinstance(cid, str) and cid and cid not in calls_seen and cid not in self.call_ids,
                        "Reused/absent call identity")
                require(item.get("async") in (None, False) and item.get("caller") in (None, {"type": "direct"}),
                        "Unsupported indirect call")
                args = strict_loads(item["arguments"])
                require(isinstance(args, dict), "Non-object arguments require separate response inspection")
                # Record unoffered names as model choices. The actual middleware
                # returns a denial; they are not executed or silently discarded.
                choices.append({"name": item["name"], "offered": item["name"] in TOOLS[self.binding["role"]]})
                calls.append({"id": cid, "name": item["name"], "args": args, "type": "tool_call"})
                calls_seen.add(cid)
            elif item["type"] == "message":
                require(item.get("role") == "assistant", "Unexpected output role")
                for part in item.get("content", []):
                    if part["type"] == "output_text": texts.append(part["text"])
                    elif part["type"] == "refusal":
                        texts.append(part["refusal"]); choices.append({"refusal": True})
                    else: raise ValueError("Unsupported output content")
        require(len(calls) <= 1, "Parallel call outside this observation contract")
        message = AIMessage(content="\n".join(texts), tool_calls=calls).model_dump(mode="json")
        self.history = active["history"] + [view(message)]
        self.items = deepcopy(active["wire"]["input"]) + deepcopy(joined["output_items"])
        self.pending = {c["id"]: c["name"] for c in calls}
        self.instructions, self.tools = active["wire"]["instructions"], active["tools"]
        self.item_ids.update(items_seen); self.call_ids.update(calls_seen)
        self.active = None
        self.closed = not calls
        return {**common, "message": message, "choices": choices, "observation_status": "completed",
                "terminal_output_omitted": joined["terminal_output_omitted"]}

