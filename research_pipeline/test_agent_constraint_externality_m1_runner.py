from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
import unittest
import urllib.error
import warnings
from pathlib import Path

from research_pipeline.agent_constraint_externality_appworld_runtime import (
    AppWorldToolWorld,
    prepare_appworld_runtime_root,
)
from research_pipeline.agent_constraint_externality_capability_execute import (
    capability_gate,
    enumerate_capability_units,
)
from research_pipeline.agent_constraint_externality_f0_execute import (
    BRANCH_ORDER_SALT,
    enumerate_probe_units,
    enumerate_source_units,
    freeze_repair,
    frozen_branch_order,
    inject_repair,
)
from research_pipeline.agent_constraint_externality_runner_core import (
    MAX_RETRIES,
    REQUESTED_MODEL,
    AppendOnlyLedger,
    DictionaryWorld,
    DuplicateDispatchError,
    EpisodeUnit,
    FakeProvider,
    MalformedToolCallError,
    ProviderCallError,
    RunnerError,
    TypicalResponsesClient,
    UnknownAfterDispatchError,
    ensure_no_secret,
    function_calls,
    run_episode,
    sha256_file,
)
from research_pipeline.appworld_constraint_compiler import (
    build_snapshot,
    evaluate_binding,
    load_protected_spec,
)

ROOT = Path(__file__).resolve().parents[1]
APPWORLD_ROOT = ROOT / "cache/substrates/appworld-official-20260831"
BUNDLE = ROOT / "generated/agent-constraint-externality-appworld-pre-f0_5-protected-20260831.bundle"


def call(name: str = "set_value", arguments: str = '{"key":"x","value":1}') -> dict:
    return {
        "type": "function_call",
        "name": name,
        "arguments": arguments,
        "call_id": "call-1",
    }


def message() -> dict:
    return {"type": "message", "content": [{"type": "output_text", "text": "done"}]}


class AgentConstraintExternalityM1RunnerTest(unittest.TestCase):
    def test_01_exact_unit_enumeration(self) -> None:
        self.assertEqual(len(enumerate_capability_units()), 8)
        self.assertEqual(len(enumerate_source_units()), 8)
        self.assertEqual(len(enumerate_probe_units([
            "ACE-FG-01", "ACE-FG-02", "ACE-FG-03",
            "ACE-TNF-01", "ACE-TNF-02", "ACE-TNF-03",
        ])), 108)
        self.assertEqual(len(enumerate_probe_units([
            "ACE-FG-01", "ACE-FG-02", "ACE-FG-03", "ACE-FG-04",
            "ACE-TNF-01", "ACE-TNF-02", "ACE-TNF-03", "ACE-TNF-04",
        ])), 144)

    def test_02_no_duplicate_units(self) -> None:
        units = enumerate_capability_units() + enumerate_source_units()
        units += enumerate_probe_units([
            "ACE-FG-01", "ACE-FG-02", "ACE-FG-03",
            "ACE-TNF-01", "ACE-TNF-02", "ACE-TNF-03",
        ])
        self.assertEqual(len(units), len({unit.unit_id for unit in units}))

    def test_03_zero_retries_for_all_transport_and_parse_failures(self) -> None:
        failures = [
            urllib.error.HTTPError("https://x", 429, "rate", {}, None),
            urllib.error.HTTPError("https://x", 503, "server", {}, None),
            TimeoutError("timeout"),
            OSError("network"),
        ]
        for failure in failures:
            def opener(*args, failure=failure, **kwargs):
                raise failure
            client = TypicalResponsesClient("test-key", opener=opener)
            with self.assertRaises(ProviderCallError):
                client.create_response(
                    model=REQUESTED_MODEL,
                    instructions="x",
                    input_items=[],
                    tools=[],
                    temperature=0.0,
                )
            self.assertEqual(client.request_count, 1)
        class BadJSON:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return b"{"
        client = TypicalResponsesClient("test-key", opener=lambda *a, **k: BadJSON())
        with self.assertRaises(ProviderCallError):
            client.create_response(
                model=REQUESTED_MODEL, instructions="x",
                input_items=[], tools=[], temperature=0.0,
            )
        self.assertEqual(client.request_count, 1)
        self.assertEqual(MAX_RETRIES, 0)

    def test_04_branch_order_is_frozen_and_paired(self) -> None:
        first = frozen_branch_order("ACE-FG-01", "HIGH", 1201)
        second = frozen_branch_order("ACE-FG-01", "HIGH", 1201)
        self.assertEqual(first, second)
        self.assertEqual(set(first), {"NO_UPDATE", "UPDATE"})
        self.assertEqual(BRANCH_ORDER_SALT, "ACE-F0-BRANCH-ORDER-20260831-V1")

    def test_05_clean_snapshot_reset_is_byte_identical(self) -> None:
        spec = load_protected_spec(BUNDLE)
        family = next(item for item in spec["families"] if item["family_id"] == "ACE-FG-01")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hash_a, connections_a = build_snapshot(APPWORLD_ROOT, family, root / "a")
            for connection in connections_a.values():
                connection.close()
            hash_b, connections_b = build_snapshot(APPWORLD_ROOT, family, root / "b")
            for connection in connections_b.values():
                connection.close()
        self.assertEqual(hash_a, hash_b)

    def test_06_update_injects_exact_frozen_bytes(self) -> None:
        repair = b"keep exact bytes\nwith spacing"
        visible = inject_repair("task", "UPDATE", repair)
        self.assertTrue(visible.endswith(repair))
        self.assertEqual(visible.count(repair), 1)

    def test_07_no_update_contains_no_repair(self) -> None:
        repair = b"SECRET_REPAIR_SENTINEL"
        visible = inject_repair("task", "NO_UPDATE", repair)
        self.assertNotIn(repair, visible)
        self.assertEqual(visible, b"task")

    def test_08_target_non_target_evaluator_bindings(self) -> None:
        connection = sqlite3.connect(":memory:")
        connection.execute("CREATE TABLE items (id INTEGER, value TEXT)")
        connection.execute("INSERT INTO items VALUES (1, 'ok')")
        good = {"table": "items", "where": {"id": 1}, "expected_fields": {"value": "ok"}}
        bad = {"table": "items", "where": {"id": 1}, "expected_fields": {"value": "bad"}}
        self.assertTrue(evaluate_binding(connection, good))
        self.assertFalse(evaluate_binding(connection, bad))
        connection.close()

    def test_09_partial_aggregate_firewall(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ledger = AppendOnlyLedger(Path(directory) / "ledger.jsonl")
            units = enumerate_capability_units()[:2]
            ledger.dispatch(
                units[0], prompt_sha256="p", snapshot_sha256="s",
                repair_sha256=None, requested_model=REQUESTED_MODEL,
                provider="mock", base_url="mock://",
            )
            ledger.complete(units[0], receipts=[], result={})
            ledger.dispatch(
                units[1], prompt_sha256="p", snapshot_sha256="s",
                repair_sha256=None, requested_model=REQUESTED_MODEL,
                provider="mock", base_url="mock://",
            )
            with self.assertRaises(UnknownAfterDispatchError):
                ledger.assert_all_terminal(units)

    def test_10_crash_after_dispatch_is_not_replayed(self) -> None:
        unit = enumerate_capability_units()[0]
        with tempfile.TemporaryDirectory() as directory:
            ledger = AppendOnlyLedger(Path(directory) / "ledger.jsonl")
            provider = FakeProvider([[message()]])
            with self.assertRaises(UnknownAfterDispatchError):
                run_episode(
                    unit=unit, instruction="x", snapshot_sha256="s",
                    repair_sha256=None, world=DictionaryWorld(),
                    provider=provider, ledger=ledger, crash_after_dispatch=True,
                )
            self.assertEqual(provider.request_count, 0)
            with self.assertRaises(DuplicateDispatchError):
                run_episode(
                    unit=unit, instruction="x", snapshot_sha256="s",
                    repair_sha256=None, world=DictionaryWorld(),
                    provider=provider, ledger=ledger,
                )

    def test_11_malformed_tool_call_is_retained_failure(self) -> None:
        unit = enumerate_capability_units()[0]
        with tempfile.TemporaryDirectory() as directory:
            ledger = AppendOnlyLedger(Path(directory) / "ledger.jsonl")
            provider = FakeProvider([[call(arguments="{")]])
            with self.assertRaises(MalformedToolCallError):
                run_episode(
                    unit=unit, instruction="x", snapshot_sha256="s",
                    repair_sha256=None, world=DictionaryWorld(),
                    provider=provider, ledger=ledger,
                )
            self.assertEqual(provider.request_count, 1)
            self.assertEqual(ledger.states()[unit.unit_id], "FAILURE")

    def test_12_source_probe_namespaces_do_not_collide(self) -> None:
        source = enumerate_source_units()[0]
        probe = enumerate_probe_units([
            "ACE-FG-01", "ACE-FG-02", "ACE-FG-03",
            "ACE-TNF-01", "ACE-TNF-02", "ACE-TNF-03",
        ])[0]
        self.assertNotEqual(source.unit_id, probe.unit_id)
        self.assertTrue(source.unit_id.startswith("source:"))
        self.assertTrue(probe.unit_id.startswith("probe:"))

    def test_13_provider_and_model_identity_are_persisted(self) -> None:
        unit = enumerate_capability_units()[0]
        outputs = [[call()], [message()]]
        with tempfile.TemporaryDirectory() as directory:
            ledger = AppendOnlyLedger(Path(directory) / "ledger.jsonl")
            run_episode(
                unit=unit, instruction="x", snapshot_sha256="s",
                repair_sha256=None, world=DictionaryWorld(),
                provider=FakeProvider(outputs), ledger=ledger,
            )
            rows = ledger.rows()
        self.assertEqual(rows[0]["model_id"], REQUESTED_MODEL)
        receipts = rows[1]["provider_receipts"]
        self.assertEqual(receipts[-1]["resolved_model"], REQUESTED_MODEL)
        self.assertEqual(receipts[-1]["provider"], "M1_FAKE_PROVIDER")

    def test_14_secrets_are_rejected_from_artifacts(self) -> None:
        with self.assertRaises(RunnerError):
            ensure_no_secret({"authorization": "Bearer secret"})
        with self.assertRaises(RunnerError):
            ensure_no_secret({"key": "sk-test"})
        ensure_no_secret({"api_key_env": "AA_API_KEY", "configured": False})

    def test_15_artifacts_are_content_addressed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            record = freeze_repair(
                Path(directory), "ACE-FG-01", b"exact",
                {"generation_request_sha256": "abc"},
            )
            path = Path(record["repair_path"])
            self.assertEqual(record["repair_sha256"], sha256_file(path))
            self.assertEqual(record["repair_byte_length"], 5)
            self.assertEqual(record["record_sha256"], hashlib.sha256(
                json.dumps(
                    {key: value for key, value in record.items() if key != "record_sha256"},
                    ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest())

    def test_actual_appworld_direct_function_adapter_smoke(self) -> None:
        spec = load_protected_spec(BUNDLE)
        family = next(item for item in spec["families"] if item["family_id"] == "ACE-FG-05")
        arm = next(item for item in family["arms"] if item["coupling_level"] == "LOW")
        with tempfile.TemporaryDirectory() as directory, warnings.catch_warnings():
            warnings.simplefilter("ignore")
            runtime = Path(directory)
            prepare_appworld_runtime_root(
                APPWORLD_ROOT, runtime, family=family, arm=arm, task_id="acem1test_1"
            )
            world = AppWorldToolWorld(
                runtime_root=runtime,
                task_id="acem1test_1",
                experiment_name="ace-m1-test",
                seed=1,
            )
            try:
                tool = next(
                    item for item in world.tools
                    if item["name"] == "api_docs__show_app_descriptions"
                )
                result = world.execute(tool["name"], {})
                self.assertEqual(len(world.tools), 473)
                self.assertTrue(str(result).strip())
            finally:
                world.close()

    def test_capability_gate_boundaries_are_fixed(self) -> None:
        rows = [
            {
                "tool_loop_completed": True,
                "target_success": index < 6,
                "non_target_preservation": 1.0,
                "malformed_tool_calls": 0,
            }
            for index in range(8)
        ]
        self.assertEqual(capability_gate(rows)["verdict"], "CAPABILITY_CALIBRATION_PASS")
        rows[0]["malformed_tool_calls"] = 1
        self.assertEqual(
            capability_gate(rows)["verdict"],
            "CAPABILITY_CALIBRATION_FAIL_INTERFACE_STOP",
        )


if __name__ == "__main__":
    unittest.main()
