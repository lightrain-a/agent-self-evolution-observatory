from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.agent_constraint_externality_qwen37plus_capability import (
    ALLOWED_ALIAS,
    REQUESTED_MODEL,
    build_addendum,
    capture_provider_snapshot,
    enumerate_units,
)
from research_pipeline.agent_constraint_externality_runner_core import sha256_value


class Qwen37PlusCapabilityA1Test(unittest.TestCase):
    def test_fixed_panel_is_exactly_eight_and_alias_is_distinct(self) -> None:
        units = enumerate_units(ALLOWED_ALIAS)
        self.assertEqual(len(units), 8)
        self.assertEqual(len({u.unit_id for u in units}), 8)
        self.assertTrue(all(ALLOWED_ALIAS in u.unit_id for u in units))

    def test_addendum_is_post_floor_not_fake_original_prereg(self) -> None:
        addendum = build_addendum(catalog_sha256="abc", catalog_model_count=200)
        self.assertTrue(addendum["change_boundary"]["post_floor_sequential_escalation"])
        self.assertTrue(addendum["change_boundary"]["not_claimed_as_original_zero-outcome_prereg"])
        self.assertFalse(addendum["panel_reuse"]["threshold_change"])
        self.assertFalse(addendum["panel_reuse"]["item_dropping"])
        self.assertFalse(addendum["panel_reuse"]["item_replacement"])
        self.assertFalse(addendum["authority"]["f0"])
        claimed = addendum["content_sha256"]
        unsigned = dict(addendum)
        unsigned.pop("content_sha256")
        self.assertEqual(claimed, sha256_value(unsigned))

    def test_exact_unavailable_resolves_only_allowed_alias(self) -> None:
        class Catalog:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self):
                return json.dumps({"data": [{"id": ALLOWED_ALIAS}, {"id": "qwen3.8-flash"}]}).encode()
        snapshot = capture_provider_snapshot(
            api_key="placeholder",
            base_url="https://example.invalid/api/v1",
            opener=lambda *args, **kwargs: Catalog(),
        )
        self.assertFalse(snapshot["requested_model_available"])
        self.assertTrue(snapshot["allowed_alias_available"])
        self.assertEqual(snapshot["resolved_request_model"], ALLOWED_ALIAS)
        self.assertFalse(snapshot["secrets_persisted"])

    def test_exact_snapshot_wins_if_available(self) -> None:
        class Catalog:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self):
                return json.dumps({"data": [{"id": ALLOWED_ALIAS}, {"id": REQUESTED_MODEL}]}).encode()
        snapshot = capture_provider_snapshot(
            api_key="placeholder",
            base_url="https://example.invalid/api/v1",
            opener=lambda *args, **kwargs: Catalog(),
        )
        self.assertEqual(snapshot["resolved_request_model"], REQUESTED_MODEL)

    def test_gate_and_execution_settings_remain_frozen(self) -> None:
        addendum = build_addendum(catalog_sha256="abc", catalog_model_count=200)
        gate = addendum["frozen_gate"]
        self.assertEqual(gate["tool_loop_completion_rate_min"], 0.75)
        self.assertEqual(gate["target_success_rate_min"], 0.50)
        self.assertEqual(gate["target_success_rate_max"], 0.875)
        self.assertEqual(gate["non_target_preservation_rate_min"], 0.85)
        self.assertEqual(gate["tool_call_cap"], 12)
        self.assertEqual(gate["provider_max_retries"], 0)
        self.assertFalse(gate["application_retry"])
        self.assertFalse(gate["replacement"])


if __name__ == "__main__":
    unittest.main()
