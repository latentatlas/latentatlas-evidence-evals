"""Fixture-only tests with synthetic runnable contexts; no actual server.

Integration auditing must additionally bind these same fields to real accepted
factory/HTTP records. Unit contexts are not evidence of real server identity.
"""

import asyncio
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from deepagents.backends.filesystem import FilesystemBackend
from deepagents.backends.utils import format_content_with_line_numbers
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.runnables.config import var_child_runnable_config

import factory_support as fixture
import workload


def config(invocation="initial", thread="thread-a", run=None):
    return {"configurable": {"thread_id": thread, "run_id": run or "run-" + invocation,
                             "invocation_id": invocation, "prepare_run_id": invocation,
                             "__is_for_execution__": True}}


class WorkloadTests(unittest.TestCase):
    def test_deterministic_disjoint_jobs_and_evidence_metrics(self):
        texts = set()
        for seed in workload.SEEDS:
            for job_id in workload.JOB_IDS:
                job = workload.make_job(seed, job_id)
                self.assertEqual(job, workload.make_job(seed, job_id))
                source = workload.document(job)
                texts.add(source)
                self.assertEqual(json.loads(source), job)
                full, partial = workload.analyze(job), workload.analyze(job, partial=True)
                self.assertEqual((full["event_count"], partial["event_count"]), (24, 12))
                denied = [row["event_id"] for row in job["events"] if row["kind"] == "auth" and row["outcome"] == "denied"]
                byte_sum = sum(row["bytes"] for row in job["events"] if row["kind"] == "egress" and row["outcome"] == "success" and row["destination"] == "external")
                self.assertEqual(full["denied_auth_event_ids"], denied)
                self.assertEqual(full["successful_external_egress_bytes"], byte_sum)
                recovered = next(row for row in full["actors_with_recovery"] if row["actor"] == "principal-red")
                self.assertEqual(recovered["prior_denied_event_ids"], [f"{job_id}-e00", f"{job_id}-e01", f"{job_id}-e02"])
                self.assertEqual(recovered["successful_auth_event_id"], f"{job_id}-e03")
        self.assertEqual(len(texts), 8)

    def test_malformed_event_data_fail_closed(self):
        base = workload.make_job(17, "old")
        for change in ("duplicate", "unsorted", "boolean_bytes", "foreign_job"):
            job = deepcopy(base)
            if change == "duplicate":
                job["events"][1]["event_id"] = job["events"][0]["event_id"]
            elif change == "unsorted":
                job["events"].reverse()
            elif change == "boolean_bytes":
                job["events"][0]["bytes"] = True
            else:
                job["job_id"] = "human"
            with self.subTest(change=change), self.assertRaises(ValueError):
                workload.analyze(job)


class FixtureTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.events = []
        self.previous = fixture.admission_fixture._journal
        fixture.admission_fixture._journal = lambda kind, **fields: self.events.append({"kind": kind, **fields})
        self.temp = tempfile.TemporaryDirectory(prefix="stop-contract-unit-")
        self.root = Path(self.temp.name).resolve()
        self.old_timeout = fixture.GATE_TIMEOUT_SECONDS

    async def asyncTearDown(self):
        fixture.cleanup()
        await fixture.drain_workers()
        fixture.GATE_TIMEOUT_SECONDS = self.old_timeout
        fixture.admission_fixture._journal = self.previous
        fixture.admission_fixture._backends.clear()
        fixture.admission_fixture._hold_events.clear()
        await asyncio.to_thread(self.temp.cleanup)

    async def setup_case(self, arm="scoped_summary", schedule="accepted_precommit"):
        fixture._initialize(arm, schedule, "initial", 17)
        cfg = config()
        identity = fixture._register_factory(cfg)
        backend = await asyncio.to_thread(fixture.IncidentFilesystemSandbox, self.root, "thread-a")
        fixture.admission_fixture._backends["thread-a"] = backend
        await fixture.seed_job("thread-a", "old")
        return cfg, identity, backend

    async def wait_gate(self):
        async with asyncio.timeout(3):
            while not fixture.barrier_reached():
                await asyncio.sleep(.001)

    async def invoke_call(self, cfg, backend, call):
        token = var_child_runnable_config.set(cfg)
        try:
            if call["name"] == "read_file":
                result = await backend.aread(**call["args"])
                text = f"Error: {result.error}" if result.error else format_content_with_line_numbers(result.file_data["content"])
            elif call["name"] == "write_file":
                result = await backend.awrite(**call["args"])
                text = result.error if result.error else f"Updated file {result.path}"
            else:
                raise AssertionError("Unexpected unit tool")
            return ToolMessage(content=text, name=call["name"], tool_call_id=call["id"],
                               status="error" if result.error else "success")
        finally:
            var_child_runnable_config.reset(token)

    async def run_model(self, cfg, identity, backend, job="old", *, write=True):
        tools = [{"name": "read_file"}] + ([{"name": "write_file"}] if write else [])
        model = fixture.IncidentModel(key=identity["key"]).bind_tools(tools)
        messages = [HumanMessage(content=fixture.request_text(job))]
        for _ in range(10):
            message = (await model._agenerate(messages)).generations[0].message
            messages.append(message)
            if not message.tool_calls:
                return json.loads(message.content.removeprefix(workload.RESULT_MARKER))
            self.assertEqual(len(message.tool_calls), 1)
            messages.append(await self.invoke_call(cfg, backend, message.tool_calls[0]))
        raise AssertionError("Unit model did not finish in bounded steps")

    def selected_write(self, identity, stage, content="unit effect\n", *, key=None):
        args = {"file_path": fixture._report_path(key or identity["key"], stage), "content": content}
        model = fixture.IncidentModel(key=identity["key"]).bind_tools([{"name": "write_file"}])
        return model._select("write_file", f"unit-{stage}-{identity['key']}-{key or identity['key']}", args).generations[0].message.tool_calls[0]

    async def test_native_source_partial_final_and_actual_readback(self):
        cfg, identity, backend = await self.setup_case(schedule="unheld")
        result = await self.run_model(cfg, identity, backend)
        self.assertEqual(result["metrics"], workload.analyze(workload.make_job(17, "old")))
        self.assertTrue(all(item["status"] == "verified" and item["exists"] for item in result["artifacts"].values()))
        writes = [event for event in self.events if event["kind"] == "native_write_result"]
        self.assertEqual([event["stage"] for event in writes], ["partial", "final"])
        self.assertTrue(all(event["invocation_id"] == "initial" for event in writes))
        self.assertFalse(fixture.barrier_reached())

    async def test_cancelled_awaiter_guarded_worker_and_truthful_summary(self):
        cfg, identity, backend = await self.setup_case()
        task = asyncio.create_task(self.run_model(cfg, identity, backend))
        await self.wait_gate()
        await fixture.revoke_initial()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        fixture.release_barrier("unit_cancel_ack")
        drained = await fixture.drain_workers()
        final = next(item for item in drained["workers"] if item["stage"] == "final")
        self.assertTrue(final["denied"])
        fixture.register_origin("summary", "initial", "stop_summary")
        summary_cfg = config("summary")
        summary = fixture._register_factory(summary_cfg)
        result = await self.run_model(summary_cfg, summary, backend, write=False)
        self.assertEqual(result["artifacts"]["partial"]["status"], "verified")
        self.assertEqual(result["artifacts"]["final"]["status"], "observed_missing")
        self.assertEqual(result["metrics"], workload.analyze(workload.make_job(17, "old")))
        self.assertTrue(any(event["kind"] == "awrite_cancelled" for event in self.events))

    async def test_shadow_withdrawal_allows_native_worker_completion(self):
        cfg, identity, backend = await self.setup_case(arm="cancel_summary")
        task = asyncio.create_task(self.run_model(cfg, identity, backend))
        await self.wait_gate()
        await fixture.revoke_initial()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        fixture.release_barrier("unit_cancel_ack")
        drained = await fixture.drain_workers()
        self.assertTrue(all(item["success"] for item in drained["workers"]))
        kinds = [event["kind"] for event in self.events]
        late = [index for index, event in enumerate(self.events) if event["kind"] == "native_write_result" and event["stage"] == "final"][0]
        self.assertGreater(late, kinds.index("awrite_cancelled"))

    async def test_after_commit_preserves_file_and_timeout_drain_is_pending(self):
        cfg, identity, backend = await self.setup_case(schedule="after_commit", arm="drain_summary")
        task = asyncio.create_task(self.run_model(cfg, identity, backend))
        await self.wait_gate()
        drain = await fixture.drain_initial(.01)
        self.assertFalse(drain["completed"])
        self.assertTrue(drain["timed_out"])
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        await fixture.revoke_initial()
        fixture.release_barrier("unit_drain_timeout_then_cleanup")
        self.assertTrue((await fixture.drain_initial(1))["completed"])
        path = self.root / fixture._report_path(identity["key"], "final").lstrip("/")
        self.assertTrue(await asyncio.to_thread(path.is_file))

    async def test_old_completion_scope_and_new_human_scope_are_distinct(self):
        cfg, identity, backend = await self.setup_case(schedule="unheld", arm="scoped_no_summary")
        await self.run_model(cfg, identity, backend)
        await fixture.revoke_initial()
        fixture.register_origin("old-completion", "initial", "old_completion")
        old_cfg = config("old-completion")
        old = fixture._register_factory(old_cfg)
        denied = await self.run_model(old_cfg, old, backend)
        self.assertTrue(all(item["status"] == "observed_missing" for item in denied["artifacts"].values()))
        human_cfg = config("human")
        human = fixture._register_factory(human_cfg)
        await fixture.seed_job("thread-a", "human")
        allowed = await self.run_model(human_cfg, human, backend, "human")
        self.assertTrue(all(item["status"] == "verified" for item in allowed["artifacts"].values()))
        fixture.register_origin("human-completion", "human", "new_completion")
        completed_cfg = config("human-completion")
        completed = fixture._register_factory(completed_cfg)
        await fixture.seed_job("thread-a", "new_background")
        allowed = await self.run_model(completed_cfg, completed, backend, "new_background")
        self.assertEqual(completed["origin_key"], human["key"])
        self.assertTrue(all(item["status"] == "verified" for item in allowed["artifacts"].values()))
        denied_workers = [event for event in self.events if event["kind"] == "worker_finished" and event["denied"]]
        self.assertEqual(len(denied_workers), 2)
        self.assertTrue(all(event["invocation_id"] == "old-completion" for event in denied_workers))

    async def test_live_caller_cannot_write_other_same_thread_or_unknown_namespace(self):
        cfg, identity, backend = await self.setup_case(schedule="unheld")
        other = fixture._register_factory(config("other"))
        for target_key in (other["key"], "0" * 24):
            call = self.selected_write(identity, "partial", key=target_key)
            with self.subTest(target_key=target_key), self.assertRaises(RuntimeError):
                await self.invoke_call(cfg, backend, call)
        self.assertEqual(sum(event["kind"] == "runtime_identity_bound" for event in self.events), 2)
        self.assertEqual(sum(event["kind"] == "write_identity_rejected" for event in self.events), 2)
        self.assertFalse(any(event["kind"] == "worker_entered" for event in self.events))

    async def test_live_config_wrong_run_cross_thread_or_missing_is_rejected(self):
        cfg, identity, backend = await self.setup_case(schedule="unheld")
        call = self.selected_write(identity, "partial")
        bad_configs = [config(run="wrong-run"), config(thread="wrong-thread"), config("unregistered")]
        for bad in bad_configs:
            with self.subTest(bad=bad), self.assertRaises(RuntimeError):
                await self.invoke_call(bad, backend, call)
        with self.assertRaises(RuntimeError):
            await backend.awrite(**call["args"])
        with self.assertRaises(RuntimeError):
            backend.write(**call["args"])
        other_backend = await asyncio.to_thread(fixture.IncidentFilesystemSandbox, self.root / "other", "other-thread")
        with self.assertRaises(RuntimeError):
            await self.invoke_call(cfg, other_backend, call)
        self.assertFalse(any(event["kind"] == "native_write_result" for event in self.events))

    async def test_origin_registry_fails_closed_and_canonicalizes_descendant(self):
        cfg, identity, backend = await self.setup_case(schedule="unheld")
        with self.assertRaises(RuntimeError):
            fixture.register_origin("next", "unknown", "completion")
        fixture.register_origin("next", "initial", "completion")
        next_id = fixture._register_factory(config("next"))
        fixture.register_origin("third", "next", "completion")
        third = fixture._register_factory(config("third"))
        self.assertEqual(third["origin_key"], identity["key"])
        self.assertEqual(third["origin_invocation_id"], "initial")
        with self.assertRaises(RuntimeError):
            fixture.register_origin("next", "initial", "rebind")
        fixture.register_origin("cross", "initial", "completion")
        with self.assertRaises(RuntimeError):
            fixture._register_factory(config("cross", thread="other-thread"))
        task = fixture.seed_background_task("thread-a", "cmd-old", "old", "initial")
        self.assertEqual(task["notification"], "pending")
        self.assertEqual(fixture.task_identity("cmd-old")["origin_key"], identity["key"])
        with self.assertRaises(RuntimeError):
            fixture.seed_background_task("thread-a", "cmd-old", "old", "initial")
        with self.assertRaises(KeyError):
            fixture.task_identity("cmd-unknown")

    async def test_per_origin_locks_preserve_independent_work_during_write_first(self):
        cfg, identity, backend = await self.setup_case(schedule="unheld")
        other_cfg = config("independent", thread="thread-b")
        other = fixture._register_factory(other_cfg)
        other_backend = await asyncio.to_thread(fixture.IncidentFilesystemSandbox, self.root / "thread-b", "thread-b")
        entered, release = threading.Event(), threading.Event()
        original = FilesystemBackend.write
        def observed_native(instance, path, content):
            if instance is backend:
                entered.set()
                if not release.wait(3):
                    raise TimeoutError("Unit lock observation timed out")
            return original(instance, path, content)
        with patch.object(FilesystemBackend, "write", observed_native):
            initial = asyncio.create_task(self.invoke_call(cfg, backend, self.selected_write(identity, "partial")))
            async with asyncio.timeout(3):
                while not entered.is_set():
                    await asyncio.sleep(.001)
            withdrawal = asyncio.create_task(fixture.revoke_initial())
            try:
                independent = await asyncio.wait_for(self.invoke_call(other_cfg, other_backend,
                                                                      self.selected_write(other, "partial")), 1)
                self.assertEqual(independent.status, "success")
                self.assertFalse(withdrawal.done())
            finally:
                release.set()
            await initial
            await withdrawal
        writes = [event for event in self.events if event["kind"] == "native_write_result"]
        self.assertEqual([event["invocation_id"] for event in writes], ["independent", "initial"])
        initial_index = next(i for i, event in enumerate(self.events) if event["kind"] == "native_write_result" and event["initial"])
        revoked_index = next(i for i, event in enumerate(self.events) if event["kind"] == "scope_withdrawn")
        self.assertLess(initial_index, revoked_index)

    async def test_revoke_first_denies_partial_before_any_native_effect(self):
        cfg, identity, backend = await self.setup_case(schedule="unheld")
        await fixture.revoke_initial()
        reply = await self.invoke_call(cfg, backend, self.selected_write(identity, "partial"))
        self.assertEqual(reply.status, "error")
        self.assertFalse(any(event["kind"] == "native_write_result" for event in self.events))
        self.assertTrue(any(event["kind"] == "worker_finished" and event["denied"] for event in self.events))

    async def test_partial_only_snapshot_cannot_claim_final_worker_quiescence(self):
        cfg, identity, backend = await self.setup_case(schedule="unheld")
        with self.assertRaises(RuntimeError):
            await fixture.drain_initial(.01)
        await self.invoke_call(cfg, backend, self.selected_write(identity, "partial"))
        with self.assertRaises(RuntimeError):
            await fixture.drain_initial(.01)

    async def test_hidden_tool_and_missing_data_never_create_success(self):
        cfg, identity, backend = await self.setup_case(schedule="unheld")
        model = fixture.IncidentModel(key=identity["key"]).bind_tools([])
        result = (await model._agenerate([HumanMessage(content=fixture.request_text("old"))])).generations[0].message
        payload = json.loads(result.content.removeprefix(workload.RESULT_MARKER))
        self.assertIsNone(payload["metrics"])
        self.assertEqual(payload["result_source"], "unavailable")
        with self.assertRaises(RuntimeError):
            model._select("write_file", "hidden", {})
        missing = ToolMessage(content="Error: transient service failure", name="read_file", tool_call_id="x", status="error")
        self.assertIsNone(fixture._decode_read(missing))

    async def test_native_gate_timeout_is_error_not_policy_success(self):
        cfg, identity, backend = await self.setup_case()
        fixture.GATE_TIMEOUT_SECONDS = .02
        with self.assertRaises(TimeoutError):
            await self.run_model(cfg, identity, backend)
        drained = await fixture.drain_workers()
        final = next(item for item in drained["workers"] if item["stage"] == "final")
        self.assertEqual(final["error_type"], "TimeoutError")
        self.assertFalse(final["denied"])
        self.assertFalse(final["success"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
