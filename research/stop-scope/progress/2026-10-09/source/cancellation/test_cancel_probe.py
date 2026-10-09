from copy import deepcopy
from types import SimpleNamespace
import unittest
import httpx
from cancel_probe import saved_target, validate_targets, run_probe


class TargetTests(unittest.TestCase):
    def setUp(self):
        self.old = dict(thread_id="T", run_id="O")
        self.req = dict(kind="native_http_request", method="POST", path="/runs/cancel",
                        body='{"thread_id":"T","run_ids":["O"]}', query="action=interrupt", request_id="source")
    def test_saved_id_and_action(self):
        self.assertEqual(saved_target(self.req, self.old), dict(thread_id="T", run_ids=["O"], action="interrupt"))
    def test_wrong_thread_rejected(self):
        self.req["body"] = '{"thread_id":"X","run_ids":["O"]}'
        with self.assertRaises(ValueError): saved_target(self.req,self.old)
    def test_extra_target_rejected(self):
        self.req["body"] = '{"thread_id":"T","run_ids":["O","S"]}'
        with self.assertRaises(ValueError): saved_target(self.req,self.old)
    def test_rollback_not_assumed_equivalent(self):
        self.req["query"] = "action=rollback"
        with self.assertRaises(ValueError): saved_target(self.req,self.old)
    def test_unknown_target_rejected(self):
        with self.assertRaises(ValueError): validate_targets(["N"], {"O":"O","S":"S"})
    def test_duplicate_target_rejected(self):
        with self.assertRaises(ValueError): validate_targets(["S","S"], {"S":"S"})
    def test_empty_target_is_explicit_list(self):
        self.assertEqual(validate_targets([], {"O":"O"}), [])
    def test_non_list_rejected(self):
        with self.assertRaises(ValueError): validate_targets("O", {"O":"O"})


class ProbeTests(unittest.IsolatedAsyncioTestCase):
    async def execute(self, mode, refreshed=("S",), reject=False):
        calls, log = [], []
        state = {"O":"interrupted", "S":"running"}
        async def get(t,r): return dict(thread_id=t,run_id=r,status=state[r])
        async def cancel_many(**kw):
            calls.append(kw)
            if reject:
                request=httpx.Request("POST","http://fixture.invalid/runs/cancel")
                raise httpx.HTTPStatusError("fixture rejection", request=request, response=httpx.Response(404,request=request))
            for rid in kw["run_ids"]: state[rid]="interrupted"
        async def join(t,r): return None
        async def active(client,t): return list(refreshed)
        client=SimpleNamespace(runs=SimpleNamespace(get=get,cancel_many=cancel_many,join=join))
        source=SimpleNamespace(_active_run_ids=active)
        rows=[dict(kind="native_http_request",method="POST",path="/runs/cancel",
                   body='{"thread_id":"T","run_ids":["O"]}',query="action=interrupt",request_id="r1")]
        await run_probe(client,source,lambda kind,**fields: log.append(dict(kind=kind,**deepcopy(fields))),
                        rows,dict(thread_id="T",run_id="O"),dict(thread_id="T",run_id="S"),mode,lambda:True)
        return calls,log
    async def test_baseline_sends_nothing(self):
        calls,log=await self.execute("none")
        self.assertEqual(calls,[])
        self.assertTrue(any(r.get("disposition")=="not_sent" for r in log))
    async def test_empty_refresh_does_not_expand_to_all_thread(self):
        calls,_=await self.execute("refresh_active_thread",())
        self.assertEqual(calls,[])
    async def test_rejection_is_an_observed_result(self):
        calls,log=await self.execute("same_saved_targets",reject=True)
        self.assertEqual(calls,[dict(thread_id="T",run_ids=["O"],action="interrupt")])
        self.assertTrue(any(r.get("disposition")=="http_rejected" for r in log))
        self.assertEqual(log[-1]["kind"],"cancel_probe_finished")
    async def test_refresh_selects_summary_not_old_run(self):
        calls,log=await self.execute("refresh_active_thread")
        self.assertEqual(calls,[dict(thread_id="T",run_ids=["S"],action="interrupt")])
        self.assertTrue(any(r.get("status")=="join_returned" for r in log))
    async def test_unknown_refreshed_id_blocks_execution(self):
        with self.assertRaises(ValueError): await self.execute("refresh_active_thread",("foreign",))


if __name__=="__main__": unittest.main()
