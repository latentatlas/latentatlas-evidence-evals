"""Offline-only plumbing fixture. No credentials, sockets, or real usage."""
from copy import deepcopy
import json
from oauth_codec import Session, MODEL, NAMESPACE


def stream_fixture(response):
    events = []
    def add(kind, **fields):
        events.append({"type": kind, "sequence_number": len(events), **fields})
    add("response.created", response={"id": response["id"], "status": "in_progress"})
    for idx, item in enumerate(response["output"]):
        add("response.output_item.added", output_index=idx, item={**item, "status": "in_progress"})
        if item["type"] == "function_call":
            add("response.function_call_arguments.delta", output_index=idx, item_id=item["id"], delta=item["arguments"])
            add("response.function_call_arguments.done", output_index=idx, item_id=item["id"], arguments=item["arguments"])
        elif item["type"] == "message":
            for ci, part in enumerate(item["content"]):
                add("response.content_part.added", output_index=idx, item_id=item["id"], content_index=ci, part=part)
                add("response.output_text.delta", output_index=idx, item_id=item["id"], content_index=ci, delta=part["text"])
                add("response.output_text.done", output_index=idx, item_id=item["id"], content_index=ci, text=part["text"])
                add("response.content_part.done", output_index=idx, item_id=item["id"], content_index=ci, part=part)
        add("response.output_item.done", output_index=idx, item=item)
    add("response.completed", response={**response, "output": []})
    return events


class FixtureTransport:
    def __init__(self, record, check_binding, mode="write"):
        from sdk_fixture import ScriptedResponder
        if mode not in {"write", "read", "ack", "repeat", "text_after_denial"}:
            raise ValueError("Undeclared offline fixture")
        self.mode = mode
        self.responder = ScriptedResponder("write" if mode == "text_after_denial" else mode)
        self.session, self.record, self.check_binding = Session(), record, check_binding

    async def complete(self, request):
        from sdk_fixture import FIXTURE_MODEL
        self.check_binding(request)
        wire = self.session.prepare(request)
        fixture_wire = {**deepcopy(wire), "model": FIXTURE_MODEL}
        response = self.responder.respond(fixture_wire)
        # Positive control for text output: derive it from the ACTUAL source read
        # result only. This is a programmed fixture, never a live behavior claim.
        if self.mode in {"ack", "text_after_denial"}:
            from sdk_fixture import decode_source
            from task_contract import workload
            replies = {m["call_id"]: m["output"] for m in wire["input"] if m["type"] == "function_call_output"}
            for item in response["output"]:
                if item["type"] == "message":
                    if self.mode == "ack":
                        item["content"][0]["text"] = "Acknowledged. I will stop."
                    elif "fixture-final" in replies:
                        if "Origin scope withdrawn before native write" not in replies["fixture-final"]:
                            raise ValueError("Text fixture requires the actual write denial reply")
                        item["content"][0]["text"] = workload.document(workload.report(decode_source(replies["fixture-source"]), "final"))
        response.update(model=MODEL, reasoning={"effort": "high"}, service_tier="default")
        for item in response["output"]:
            if item["type"] == "function_call":
                item["namespace"] = NAMESPACE
        events = stream_fixture(response)
        result = self.session.accept(events, request["request_id"])
        self.record("oauth_fixture_projection", request_id=request["request_id"], live_provider=False,
                    response=result, usage_is_synthetic=True, wire=wire, events=events, fixture_mode=self.mode)
        return result["envelope"]

    async def aclose(self):
        self.record("oauth_fixture_closed", model_requests=0)
