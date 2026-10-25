"""Credential-free F07 projection for the ChatGPT-plan Responses route.

This is a new contract, not a patch to the two-tool exploration codec. Raw
response events and imported native history remain separately attributable.
Model choices are not evidence-validity criteria.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
for name in ("live_pilot_v02", "live_exploration_v01"):
    sys.path.append(str(HERE.parent / name))
from oauth_codec import reconcile
from responses_codec import require, strict_loads, view
from wire_contract import digest, validate_history
from langchain_core.messages import AIMessage

VERSION = "f07-chatgpt-wire-v01-development"
MODEL = "gpt-6-astra"
EFFORT = "high"
NAMESPACE = "functions"
TOOLS = {"O": {"read_file", "write_file", "edit_file"},
         "I": {"read_file", "write_file", "edit_file"},
         "N": {"read_file", "write_file", "edit_file"},
         "S": {"read_file", "slack_thread_reply"}}


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
        if (not isinstance(body.get("model"), str) or not body["model"] or (body.get("reasoning") or {}).get("effort") != EFFORT
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
