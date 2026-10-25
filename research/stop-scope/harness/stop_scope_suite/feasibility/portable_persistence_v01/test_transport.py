"""Real negative checks for network opt-in, limits, incomplete usage and evidence corruption."""
import asyncio
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import httpx
from transport import Transport, ENDPOINT
from run import validate_live

sys.path.append(str(Path(__file__).resolve().parent.parent/"live_exploration_v01"))
from oauth_fixture import stream_fixture

CONFIG={"model":"gpt-6-astra","reasoning_effort":"high","max_requests":1,
        "max_output_tokens":256,"max_request_bytes":4096}
REQUEST={"binding":{"role":"O","invocation_id":"inv-1"},"request_index":1,"request_id":"inv-1:1"}
WIRE={"model":"gpt-6-astra","reasoning":{"effort":"high"},"stream":True,"store":False,"input":[]}
def events(status="completed",usage=True):
    r=dict(id="test-response",status=status,output=[],model="gpt-6-astra",
           reasoning={"effort":"high"},service_tier="default",error=None,incomplete_details=None)
    if usage:r["usage"]=dict(input_tokens=10,output_tokens=20,total_tokens=30)
    es=stream_fixture(r)
    es[-1]["type"]="response."+status
    return es
class TransportTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.calls=[]
    async def asyncTearDown(self): self.tmp.cleanup()
    def client(self, es=None, status=200):
        def response(req):
            self.calls.append(req)
            self.assertEqual(str(req.url),ENDPOINT)
            return httpx.Response(status,content="".join("data: "+json.dumps(e)+"\n\n" for e in (es or events())))
        return httpx.Client(transport=httpx.MockTransport(response))
    def transport(self,**kw):
        return Transport(self.root,lambda *a,**k:None,config=CONFIG,api_key="TEST-ONLY-KEY",**kw)
    async def test_offline_does_not_create_client_or_read_key(self):
        with patch.dict(os.environ,{"OPENAI_API_KEY":"MUST-NOT-BE-USED"}), patch("httpx.Client",side_effect=AssertionError("network client")):
            t=Transport(self.root,lambda *a,**k:None)
            await t.complete(REQUEST,WIRE,fixture_events=events());await t.aclose()
        self.assertEqual(t.ledger["actual_provider_calls"],0)
        self.assertNotIn("MUST-NOT-BE-USED", "".join(p.read_text() for p in self.root.rglob("*") if p.is_file()))
    async def test_live_request_limits_and_key_not_retained(self):
        t=self.transport(client=self.client())
        await t.complete(REQUEST,WIRE)
        r=deepcopy(REQUEST);r.update(request_index=2,request_id="inv-1:2")
        with self.assertRaisesRegex(ValueError,"Request bound"):await t.complete(r,WIRE)
        await t.aclose()
        self.assertEqual(len(self.calls),1)
        self.assertEqual(json.loads(self.calls[0].content)["max_output_tokens"],256)
        self.assertNotIn("TEST-ONLY-KEY","".join(p.read_text() for p in self.root.rglob("*") if p.is_file()))
    async def test_incomplete_terminal_is_preserved_and_stops(self):
        t=self.transport(client=self.client(events("incomplete")))
        result=await t.complete(REQUEST,WIRE)
        self.assertEqual(result[-1]["type"],"response.incomplete")
        self.assertTrue(t.stopped);await t.aclose()
        self.assertEqual(t.ledger["status"],"closed_needs_attention")
        self.assertEqual(t.ledger["unknown_usage_attempts"],0)
    async def test_missing_usage_is_unknown_and_no_retry(self):
        t=self.transport(client=self.client(events(usage=False)))
        with self.assertRaises(RuntimeError):await t.complete(REQUEST,WIRE)
        await t.aclose()
        self.assertEqual(len(self.calls),1);self.assertEqual(t.ledger["unknown_usage_attempts"],1)
        self.assertTrue((self.root/"request-01/DISPATCH.json").is_file())
    async def test_http_failure_does_not_retry_or_save_error_body(self):
        t=self.transport(client=self.client(status=429))
        with self.assertRaises(RuntimeError):await t.complete(REQUEST,WIRE)
        await t.aclose()
        self.assertEqual(len(self.calls),1)
        self.assertFalse((self.root/"request-01/response.sse").exists())
    async def test_oversize_request_refused_before_dispatch(self):
        t=self.transport(client=self.client())
        with self.assertRaisesRegex(ValueError,"byte limit"):await t.complete(REQUEST,WIRE|{"input":"x"*5000})
        await t.aclose()
        self.assertEqual(self.calls,[]);self.assertEqual(t.count,0)
    async def test_explicit_key_required(self):
        with self.assertRaisesRegex(ValueError,"API key"):Transport(self.root,lambda *a,**k:None,config=CONFIG)
    def test_live_configuration_rejects_unbounded_or_hidden_fields(self):
        for bad in (CONFIG|{"max_requests":100},CONFIG|{"max_requests":True},CONFIG|{"max_output_tokens":0},
                    CONFIG|{"base_url":"https://other.invalid"},CONFIG|{"api_key":"not-a-setting"}):
            with self.assertRaises(ValueError):validate_live(bad,"healthy")

if __name__=="__main__":unittest.main()
