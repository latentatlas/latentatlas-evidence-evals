"""Strict local transport envelope, NOT a provider API wire format."""

import base64
import hashlib
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def encoded(value):
    raw = canonical(value)
    return {"body": value, "raw_b64": base64.b64encode(raw).decode(),
            "sha256": hashlib.sha256(raw).hexdigest()}


def decode_record(row):
    raw = base64.b64decode(row["raw_b64"], validate=True)
    if hashlib.sha256(raw).hexdigest() != row["sha256"]:
        raise ValueError("raw hash mismatch")
    if json.loads(raw) != row["body"]:
        raise ValueError("raw/body mismatch")
    return row["body"]


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


def validate_request(body):
    if body.get("format") != "langchain_local_bridge_v1_not_provider_wire":
        raise ValueError("not a supported local request")
    if body.get("tool_choice") != "auto" or body.get("parallel_tool_calls") is not False:
        raise ValueError("decision opportunity changed")
    if sorted(t["function"]["name"] for t in body.get("tools", [])) != ["read_file", "write_file"]:
        raise ValueError("wrong actual tool inventory")
    validate_history(body["messages"])
    if body["phase"] == "post_message":
        humans = [m for m in body["messages"] if m["type"] == "human"]
        if not humans or humans[-1]["content"] != body["operator_text"]:
            raise ValueError("operator message missing from actual input")
        if body["post_index"] == 1 and body["messages"][-1]["type"] != "human":
            raise ValueError("first decision does not end with operator message")


def validate_response(request, response):
    if (response.get("record_type") != "scripted_local_transport_response"
            or response.get("request_id") != request["request_id"]
            or response.get("request_sha256") != digest(request)):
        raise ValueError("response/request binding invalid")
    if response.get("status") != "completed":
        raise ValueError("incomplete response cannot become a terminal success")
    message = response["message"]
    if message.get("type") != "ai" or message.get("invalid_tool_calls"):
        raise ValueError("unsupported or invalid response")
    calls = message.get("tool_calls", [])
    if len(calls) > 1:
        raise ValueError("parallel calls outside declared slice")
    past = {c["id"] for m in request["messages"] for c in m.get("tool_calls", [])}
    for call in calls:
        if not isinstance(call.get("id"), str) or not call["id"] or call["id"] in past:
            raise ValueError("reused/absent response call ID")
        if call.get("name") not in {"read_file", "write_file"}:
            raise ValueError("unoffered tool")
        args = call.get("args", {})
        required = {"file_path", "content"} if call["name"] == "write_file" else {"file_path"}
        allowed = required if call["name"] == "write_file" else {"file_path", "offset", "limit"}
        if not required <= set(args) <= allowed or not isinstance(args["file_path"], str):
            raise ValueError("malformed local tool arguments")
        if call["name"] == "write_file" and not isinstance(args["content"], str):
            raise ValueError("non-text write")
        if call["name"] == "read_file" and (type(args.get("offset", 0)) is not int or type(args.get("limit", 2000)) is not int):
            raise ValueError("invalid read bounds")
    return message
