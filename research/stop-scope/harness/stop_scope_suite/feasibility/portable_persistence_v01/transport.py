"""Bounded Responses transport. Offline fixtures never create a network client."""
import asyncio
from contextvars import ContextVar
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import threading
import time

from comparison_config import LIMITS, REQUEST_LIMITS, authorization, max_requests, require
NETWORK_ALLOWED = ContextVar("portable_model_network", default=False)
ENDPOINT = "https://api.openai.com/v1/responses"
def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(value): return hashlib.sha256(value).hexdigest()
def save(path,value):
    with Path(path).open("x") as f: json.dump(value,f,indent=2,ensure_ascii=False)
def parse_events(raw):
    events=[]
    for block in raw.replace("\r\n","\n").split("\n\n"):
        data="\n".join(line[5:].lstrip() for line in block.splitlines() if line.startswith("data:"))
        if data and data!="[DONE]": events.append(json.loads(data))
    return events
def usage_of(response):
    usage=response.get("usage")
    require(isinstance(usage,dict), "Provider usage missing")
    for name in ("input_tokens","output_tokens","total_tokens"):
        require(type(usage.get(name)) is int and usage[name]>=0,"Invalid provider usage")
    require(usage["input_tokens"]+usage["output_tokens"]==usage["total_tokens"],"Usage sum differs")
    return deepcopy(usage)

class Transport:
    def __init__(self,out,record,*,arm="healthy",config=None,api_key=None,client=None):
        self.out,self.record,self.arm=Path(out),record,arm
        self.live=config is not None
        self.config=deepcopy(config)
        self.api_key=api_key
        require(not self.live or bool(api_key), "Explicit API key required")
        require(self.live or client is None, "Offline mode must not use a client")
        self.actor="live_api_provider" if self.live else "programmed_portable_fixture"
        self.client=client
        self.count=0; self.stopped=False; self.pending=set(); self.lock=threading.Lock()
        self.ledger=dict(authorization=authorization(17,arm,live=self.live),attempts=[],
            requests_attempted=0,actual_provider_calls=0,usage_is_synthetic=not self.live,
            per_role_requests={},status="open",unknown_usage_attempts=0,
            requested_configuration=self.config,endpoint=ENDPOINT if self.live else None,
            automatic_retry=False)
        if self.live and self.client is None:
            import httpx
            self.client=httpx.Client(transport=httpx.HTTPTransport(retries=0),follow_redirects=False,
                timeout=httpx.Timeout(LIMITS["stream_read_seconds"],connect=LIMITS["connect_seconds"]),trust_env=False)
    def halt(self,reason):
        self.stopped=True
        self.record("transport_halted",reason=reason)
    async def complete(self,request,wire,*,fixture_events=None):
        task=asyncio.create_task(asyncio.to_thread(self._complete,deepcopy(request),deepcopy(wire),fixture_events))
        self.pending.add(task)
        try: return await asyncio.shield(task)
        except asyncio.CancelledError:
            self.halt("awaiter_cancelled_usage_pending")
            try: await asyncio.shield(task)
            except Exception: pass
            raise
        finally:
            if task.done(): self.pending.discard(task)
    def _complete(self,request,wire,fixture_events):
        require(self.lock.acquire(blocking=False), "Concurrent provider dispatch prohibited")
        token=NETWORK_ALLOWED.set(self.live)
        try: return self._exchange(request,wire,fixture_events)
        finally:
            NETWORK_ALLOWED.reset(token); self.lock.release()
    def _exchange(self,request,wire,fixture_events):
        role=request["binding"]["role"]
        require(not self.stopped and role in REQUEST_LIMITS, "Transport halted or unknown role")
        require(not(role=="S" and self.arm=="healthy"),"Healthy summary not authorized")
        count=self.ledger["per_role_requests"].get(role,0)
        limit=self.config["max_requests"] if self.live else max_requests(self.arm)
        require(self.count<limit and count<REQUEST_LIMITS[role],"Request bound; no dispatch")
        require(request["request_index"]==count+1,"Role request order")
        payload=deepcopy(wire)
        if self.live:
            require(payload["model"]==self.config["model"] and payload["reasoning"]=={"effort":self.config["reasoning_effort"]},
                    "Configured model drift")
            payload["max_output_tokens"]=self.config["max_output_tokens"]
        body=canonical(payload)
        require(not self.live or len(body)<=self.config["max_request_bytes"],"Request byte limit; no dispatch")
        require(not self.api_key or self.api_key.encode() not in body,"Credential in request")
        self.count+=1
        self.ledger["per_role_requests"][role]=count+1
        folder=self.out/f"request-{self.count:02d}"; folder.mkdir(mode=0o700)
        save(folder/"bridge_request.json",request); save(folder/"wire_request.json",wire)
        save(folder/"api_request.json",payload)
        attempt=dict(index=self.count,request_id=request["request_id"],binding=request["binding"],
                     request_sha256=sha(body),status="dispatch_possible_usage_unknown")
        self.ledger["attempts"].append(attempt)
        # Write-ahead evidence remains even if process dies before a terminal usage event.
        save(folder/"DISPATCH.json",attempt)
        self.record("provider_dispatch",**attempt,actual_provider_calls=int(self.live))
        raw=bytearray(); started=time.monotonic()
        observation=dict(status="usage_unknown",actual_provider_calls=int(self.live))
        try:
            if self.live:
                with self.client.stream("POST",ENDPOINT,content=body,headers={
                    "Authorization":"Bearer "+self.api_key,"Content-Type":"application/json","Accept":"text/event-stream"
                }) as response:
                    observation.update(http_status=response.status_code,provider_request_id=response.headers.get("x-request-id"),
                                       content_type=response.headers.get("content-type"))
                    require(response.status_code==200, "Provider HTTP failure; no retry")
                    for chunk in response.iter_bytes():
                        raw.extend(chunk)
                        require(len(raw)<=LIMITS["max_response_bytes"] and
                                time.monotonic()-started<=LIMITS["stream_elapsed_seconds"],"Response observation bound")
            else:
                require(fixture_events is not None,"Offline fixture missing")
                raw.extend("".join("data: "+json.dumps(e)+"\n\n" for e in fixture_events).encode())
            require(not self.api_key or self.api_key.encode() not in raw,"Credential echo refused")
            with (folder/"response.sse").open("xb") as f: f.write(raw)
            events=parse_events(raw.decode())
            save(folder/"events.json",events)
            terminals=[e["response"] for e in events if e.get("type") in {"response.completed","response.incomplete","response.failed"}]
            require(len(terminals)==1,"Missing or multiple terminal events")
            terminal=terminals[0]
            usage=usage_of(terminal)
            observation.update(usage=usage,body_sha256=sha(raw),reported_model=terminal.get("model"),status="terminal_observed")
            attempt.update(status="terminal_observed",usage=usage,provider_status=terminal["status"])
            if self.live:
                require(usage["output_tokens"]<=self.config["max_output_tokens"],"Provider output exceeds configured bound")
            if terminal["status"]!="completed": self.halt("provider_"+terminal["status"])
            return events
        except BaseException as exc:
            self.halt("transport_observation_incomplete")
            observation["error_type"]=type(exc).__name__
            attempt["status"]="incomplete_or_transport_error"
            # Never log arbitrary HTTP error bodies, exception messages or credential headers.
            raise RuntimeError("Provider observation incomplete; inspect retained attempt; no retry") from None
        finally:
            observation["elapsed_seconds"]=time.monotonic()-started
            save(folder/"observation.json",observation)
            self.ledger.update(requests_attempted=self.count,actual_provider_calls=self.count if self.live else 0,
                unknown_usage_attempts=sum("usage" not in a for a in self.ledger["attempts"]))
    async def aclose(self):
        if self.pending:
            await asyncio.gather(*list(self.pending),return_exceptions=True)
            self.pending.clear()
        if self.client: await asyncio.to_thread(self.client.close)
        self.ledger["status"]="closed_needs_attention" if self.stopped or self.ledger["unknown_usage_attempts"] else "closed_clean"
        save(self.out/"USAGE.json",self.ledger)
        self.record("provider_client_closed",status=self.ledger["status"],actual_provider_calls=self.ledger["actual_provider_calls"])
        self.api_key=None
