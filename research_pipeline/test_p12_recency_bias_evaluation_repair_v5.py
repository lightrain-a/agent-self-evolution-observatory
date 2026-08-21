from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .p12_recency_bias_evaluation_repair_v5 import (
    FAILED_UNIT,
    REPLACEMENT_PROVIDER_CALL_CAP,
    answer_first_prompt,
    build_repair_plan,
    parse_answer_v5,
    scientific_prompt_body,
)
from .p12_recency_bias_harness import mock_skills, rollout_prompt, rollout_units


class P12RecencyBiasEvaluationRepairV5Test(unittest.TestCase):
    def fixture(self, root: Path) -> list[dict]:
        units = rollout_units(mock_skills())
        self.assertEqual(len(units), 96)
        self.assertEqual(units[2]["unit_id"], FAILED_UNIT)
        (root / "rollout-manifest.json").write_text(json.dumps({"units": units}))
        (root / "runtime-failure-manifest-v4.json").write_text(json.dumps({
            "failure_manifest_sha256": "b" * 64,
            "provider_calls_charged": 14,
            "remaining_model_call_budget": 178,
        }))
        (root / "harness-implementation-manifest-v4.json").write_text(json.dumps({"harness_manifest_sha256": "a" * 64}))
        (root / "units").mkdir()
        for unit in units[:2]:
            (root / "units" / f"{unit['unit_id']}.json").write_text(json.dumps({"status": "UNIT_COMPLETE", "unit_id": unit["unit_id"], "valid_execution": True}))
        (root / "units" / f"{FAILED_UNIT}.json").write_text(json.dumps({"status": "UNIT_PROTOCOL_FAILURE", "unit_id": FAILED_UNIT}))
        return units

    def test_prompt_changes_only_return_protocol(self):
        unit = rollout_units(mock_skills())[2]
        base = rollout_prompt(unit)
        new = answer_first_prompt(unit)
        self.assertEqual(scientific_prompt_body(base), scientific_prompt_body(new))
        self.assertIn("P12_ANSWER=<integer>", new)

    def test_parser_prefers_function_then_exact_first_line(self):
        function = {"function_calls": [{"name": "submit_p12_answer", "arguments": json.dumps({"answer": 7})}], "text": "P12_ANSWER=3"}
        self.assertEqual(parse_answer_v5(function), (7, "FUNCTION_CALL"))
        text = {"function_calls": [], "text": "P12_ANSWER=-12\nreasoning continues"}
        self.assertEqual(parse_answer_v5(text), (-12, "ANSWER_FIRST_TEXT"))
        with self.assertRaisesRegex(ValueError, "exact first-line"):
            parse_answer_v5({"function_calls": [], "text": "Reasoning first\nP12_ANSWER=-12"})

    def test_plan_reuses_two_and_applies_one_protocol_to_all_remaining(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            units = self.fixture(root)
            plan = build_repair_plan(root)
            self.assertEqual(plan["reuse_completed_units"], [units[0]["unit_id"], units[1]["unit_id"]])
            self.assertEqual(plan["retry_failed_unit"], {"unit_id": FAILED_UNIT, "max_attempts": 1})
            self.assertEqual(len(plan["unstarted_units"]), 93)
            self.assertEqual(plan["execution_order"], [FAILED_UNIT, *[u["unit_id"] for u in units[3:]]])
            self.assertEqual(plan["replacement_provider_call_cap"], REPLACEMENT_PROVIDER_CALL_CAP)
            self.assertEqual(plan["provider_calls_already_charged"] + plan["replacement_provider_call_cap"], 108)
            self.assertLessEqual(108, 192)
            self.assertTrue(all(x["scientific_prompt_body_unchanged"] for x in plan["prompt_bindings"].values()))


if __name__ == "__main__":
    unittest.main()
