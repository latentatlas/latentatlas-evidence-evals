"""No model calls. Check boundary admission, explicit reuse and credential absence."""
import asyncio
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import bridge_dependencies as dep
from runtime_link import PersistentController
from run import environment, CONDITIONS


class LinkTests(unittest.TestCase):
    def test_declared_matrix(self):
        self.assertEqual(len(CONDITIONS),15)
        self.assertEqual(len(set(CONDITIONS)),15)

    def test_environment_does_not_inherit_key(self):
        with patch.dict("os.environ",{"OPENAI_API_KEY":"test-secret","ANTHROPIC_API_KEY":"test-secret"}):
            env=environment()
        self.assertNotIn("OPENAI_API_KEY",env)
        self.assertNotIn("ANTHROPIC_API_KEY",env)
        self.assertEqual(env["LANGGRAPH_URL"],"http://fixture.invalid")

    def test_dependency_module_conflict_rejected(self):
        with patch.dict(sys.modules,{"bridge_durable_receiver":SimpleNamespace(__file__=__file__)}):
            with self.assertRaisesRegex(ValueError,"Module identity conflict"):
                dep.load("bridge_durable_receiver")

    def test_dependency_byte_drift_rejected(self):
        path,expected=dep.PINS["bridge_durable_receiver"]
        with patch.dict(dep.PINS,{"bridge_durable_receiver":(path,"0"*64)}):
            with self.assertRaisesRegex(ValueError,"Pinned dependency changed"):
                dep.load("bridge_durable_receiver")

    def test_wrong_native_adapter_binding(self):
        with self.assertRaises(ValueError):
            dep.verify_adapter(SimpleNamespace(__file__=__file__))

    def controller(self):
        records=[]
        c=PersistentController(lambda kind,**fields:records.append((kind,fields)),{},None,None,None,
                               Path("/unused"),None,None,{})
        return c,records

    def test_release_prevents_new_holds_before_listing(self):
        c,records=self.controller()
        def rpc(action,**kw):
            self.assertTrue(c.releasing)
            return {"jobs":{}}
        c.rpc=rpc; c.release_all()
        self.assertEqual(records[0][0],"receiver_future_holds_disabled")

    def test_release_only_queued_not_uncertain(self):
        c,_=self.controller(); commands=[]
        def rpc(action,**kw):
            commands.append((action,kw))
            return {"jobs":{"a":{"state":"queued"},"b":{"state":"uncertain"},"c":{"state":"completed"}}}
        c.rpc=rpc; c.release_all()
        self.assertEqual(commands,[("status",{}),("execute",{"operation_id":"a"})])

    def test_uncertain_blocks_drain(self):
        c,_=self.controller()
        c.rpc=lambda *a,**kw:{"jobs":{"a":{"state":"uncertain","done":False}}}
        with self.assertRaisesRegex(ValueError,"remains unresolved"): c.drain()


if __name__=="__main__": unittest.main()
