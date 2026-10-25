"""Programmed stream for wire tests. Token counts here are synthetic."""
from copy import deepcopy
import json
from bridge_codec import MODEL, NAMESPACE
from oauth_fixture import stream_fixture


def events_for(message, index):
    output = [{"type": "reasoning", "id": f"fixture-reasoning-{index}", "summary": [],
               "encrypted_content": "fixture-opaque-not-provider-reasoning"}]
    if message.get("content") or not message.get("tool_calls"):
        output.append({"type": "message", "id": f"fixture-message-{index}", "role": "assistant",
                       "status": "completed", "content": [{"type": "output_text",
                       "text": message.get("content", ""), "annotations": []}]})
    for i, call in enumerate(message.get("tool_calls", [])):
        output.append({"type": "function_call", "id": f"fixture-call-{index}-{i}", "status": "completed",
                       "name": call["name"], "call_id": call["id"], "namespace": NAMESPACE,
                       "arguments": json.dumps(call["args"], ensure_ascii=False)})
    body = {"id": f"fixture-response-{index}", "object": "response", "status": "completed",
            "model": MODEL, "reasoning": {"effort": "high"}, "service_tier": "default",
            "error": None, "incomplete_details": None, "output": output,
            "usage": {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120,
                      "input_tokens_details": {"cached_tokens": 0},
                      "output_tokens_details": {"reasoning_tokens": 1}}}
    return stream_fixture(deepcopy(body))
