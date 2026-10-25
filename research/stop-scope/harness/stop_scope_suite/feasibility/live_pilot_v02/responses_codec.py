"""Fail-closed, stateless Responses conversion. No client, key, or network here.

The graph sees a text/tool projection. Full response output items are separately
retained and replayed unchanged; the projection is never used to rebuild them.
"""

import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
from langchain_core.messages import AIMessage

from wire_contract import digest, validate_request, validate_response


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


def raw_record(raw):
    return {"raw_b64": base64.b64encode(raw).decode(), "sha256": hashlib.sha256(raw).hexdigest(),
            "body": strict_loads(raw)}


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


def flatten_tools(tools):
    result = []
    for tool in tools:
        require(tool.get("type") == "function" and set(tool) == {"type", "function"}, "unsupported tool envelope")
        fn = tool["function"]
        require(set(fn) <= {"name", "description", "parameters", "strict"}, "unsupported function field")
        require(fn.get("strict") in (None, False), "strict schema changes require a new contract")
        Draft202012Validator.check_schema(fn["parameters"])
        result.append({"type": "function", "name": fn["name"], "description": fn.get("description", ""),
                       "parameters": deepcopy(fn["parameters"]), "strict": False})
    require(sorted(t["name"] for t in result) == ["read_file", "write_file"], "unexpected tool inventory")
    return result


def local_response(request, message):
    # Outer bridge evidence remains explicitly local even when SDK format is used.
    return {"record_type": "scripted_local_transport_response", "request_id": request["request_id"],
            "request_sha256": digest(request), "status": "completed", "message": message,
            "provider": None, "model_revision": None, "provider_usage": None, "paid_calls": 0}


class ResponsesSession:
    def __init__(self, model, expected_response_model=None, max_output_tokens=4096):
        require(isinstance(model, str) and model, "explicit model identifier required")
        require(type(max_output_tokens) is int and 1 <= max_output_tokens <= 4096, "invalid output cap")
        self.model = model
        self.expected_response_model = expected_response_model or model
        self.max_output_tokens = max_output_tokens
        self.history, self.items = [], []
        self.instructions = self.tools = self.inflight = None
        self.call_ids, self.response_ids, self.item_ids, self.request_ids = set(), set(), set(), set()
        self.pending_calls = {}
        self.closed = False

    def prepare(self, request):
        require(not self.closed and self.inflight is None, "closed or already in-flight session")
        validate_request(request)
        require(request["request_id"] not in self.request_ids, "reused local request ID")
        messages = request["messages"]
        require(messages and messages[0]["type"] == "system", "leading system instruction required")
        require(all(m["type"] != "system" for m in messages[1:]), "unexpected later system message")
        instruction = view(messages[0])["content"]
        tools = flatten_tools(request["tools"])
        if self.instructions is not None:
            require(instruction == self.instructions and tools == self.tools, "instructions or tools changed")
        history = [view(m) for m in messages[1:]]
        require(history[:len(self.history)] == self.history, "history rewritten or truncated")
        extra = history[len(self.history):]
        require(extra, "no new input since last output")
        if not self.history:
            require(extra and all(m["type"] == "human" for m in extra), "initial user task and application-owned context required")
        items, pending = deepcopy(self.items), dict(self.pending_calls)
        for message in extra:
            if message["type"] == "human":
                require(not pending, "operator/task precedes pending tool reply")
                items.append({"type": "message", "role": "user", "content": message["content"]})
            elif message["type"] == "tool":
                cid = message["tool_call_id"]
                require(cid in pending and message["name"] == pending[cid], "tool result name/identity mismatch")
                require(message["status"] in {"success", "error"}, "unknown tool status")
                items.append({"type": "function_call_output", "call_id": cid, "output": message["content"]})
                pending.pop(cid)
            else:
                raise ContractError("unrecorded assistant output or unsupported role")
        require(not pending, "unanswered tool calls")
        wire = {"model": self.model, "instructions": instruction, "input": items, "tools": tools,
                "tool_choice": "auto", "parallel_tool_calls": False, "store": False, "stream": False,
                "truncation": "disabled", "max_output_tokens": self.max_output_tokens,
                "include": ["reasoning.encrypted_content"]}
        require(len(json.dumps(wire).encode()) <= 1_000_000, "request byte safety cap; not a token-budget check")
        self.inflight = {"request": deepcopy(request), "wire": deepcopy(wire), "history": history}
        self.request_ids.add(request["request_id"])
        return deepcopy(wire)

    def accept(self, raw, *, request_id, status_code=200):
        require(self.inflight is not None and not self.closed, "no active request")
        try:
            return self._accept(raw, request_id, status_code)
        except Exception:
            # Unknown/incomplete responses cannot accidentally become graph success.
            self.closed = True
            raise

    def _accept(self, raw, request_id, status_code):
        active = self.inflight
        require(request_id == active["request"]["request_id"], "response bound to wrong request")
        require(status_code == 200, "HTTP failure; no retry or obedience classification")
        body = strict_loads(raw)
        require(isinstance(body, dict) and body.get("object") == "response", "not a Responses object")
        require(body.get("status") == "completed" and body.get("error") is None and body.get("incomplete_details") is None,
                "incomplete/failed response is not a completed decision")
        rid = body.get("id")
        require(isinstance(rid, str) and rid and rid not in self.response_ids, "missing/reused response ID")
        require(body.get("model") == self.expected_response_model, "unapproved response model; alias resolution needs explicit review")
        usage = body.get("usage")
        require(isinstance(usage, dict), "missing usage")
        for name in ("input_tokens", "output_tokens", "total_tokens"):
            require(type(usage.get(name)) is int and usage[name] >= 0, "invalid token accounting")
        require(usage["total_tokens"] == usage["input_tokens"] + usage["output_tokens"], "inconsistent total tokens")
        require(usage["output_tokens"] <= self.max_output_tokens, "output budget exceeded")
        for parent, key, total in (("input_tokens_details", "cached_tokens", "input_tokens"),
                                   ("output_tokens_details", "reasoning_tokens", "output_tokens")):
            count = (usage.get(parent) or {}).get(key)
            require(type(count) is int and 0 <= count <= usage[total], "invalid/missing token subcount")
        outputs = body.get("output")
        require(isinstance(outputs, list) and outputs, "no output items")
        texts, calls, ids, refusal = [], [], set(), False
        offered = {t["name"]: t for t in active["wire"]["tools"]}
        for item in outputs:
            iid = item.get("id")
            require(isinstance(iid, str) and iid and iid not in ids and iid not in self.item_ids, "duplicate/missing output item ID")
            ids.add(iid)
            kind = item.get("type")
            if kind == "reasoning":
                require(isinstance(item.get("encrypted_content"), str) and item["encrypted_content"], "missing opaque reasoning carry-forward")
                require(item.get("status") in (None, "completed"), "unfinished reasoning item")
                # Do not inspect/decode opaque content or solicit chain of thought.
            elif kind == "function_call":
                require(item.get("status") == "completed", "unfinished function call")
                cid, name = item.get("call_id"), item.get("name")
                require(isinstance(cid, str) and cid and cid not in self.call_ids, "missing/reused call ID")
                require(name in offered, "unknown function")
                args = strict_loads(item.get("arguments"))
                Draft202012Validator(offered[name]["parameters"]).validate(args)
                if name == "read_file":
                    require(type(args.get("offset", 0)) is int and args.get("offset", 0) >= 0
                            and type(args.get("limit", 2000)) is int and args.get("limit", 2000) > 0, "invalid read bounds")
                calls.append({"type": "tool_call", "id": cid, "name": name, "args": args})
            elif kind == "message":
                require(item.get("status") == "completed" and item.get("role") == "assistant", "unfinished/wrong-role output")
                require(isinstance(item.get("content"), list), "malformed content")
                for part in item["content"]:
                    if part.get("type") == "refusal":
                        refusal = True
                    else:
                        require(part.get("type") == "output_text" and isinstance(part.get("text"), str), "unsupported output content")
                        texts.append(part["text"])
            else:
                raise ContractError("unsupported output item; never silently drop: " + str(kind))
        require(not refusal, "refusal is a distinct censored outcome, not stop compliance")
        require(calls or any(texts), "no actionable or textual output")
        message = AIMessage(content="\n".join(texts), tool_calls=calls).model_dump(mode="json")
        envelope = local_response(active["request"], message)
        validate_response(active["request"], envelope)  # exact call count/allowlist/argument shape
        self.instructions, self.tools = active["wire"]["instructions"], active["wire"]["tools"]
        self.history = active["history"] + [view(message)]
        self.items = deepcopy(active["wire"]["input"]) + deepcopy(outputs)
        self.pending_calls = {c["id"]: c["name"] for c in calls}
        self.call_ids.update(self.pending_calls)
        self.response_ids.add(rid)
        self.item_ids.update(ids)
        self.inflight = None
        return {"envelope": envelope, "response_id": rid, "usage": deepcopy(usage),
                "all_output_items_retained": True, "text_is_compliance_verdict": False}
