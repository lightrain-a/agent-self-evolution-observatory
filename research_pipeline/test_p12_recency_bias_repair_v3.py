from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .p12_recency_bias_harness import difficulty_calibration_pairs, difficulty_prompt
from .p12_recency_bias_repair_v3 import (
    FAILED_PAIR,
    REPLACEMENT_PROVIDER_CALL_CAP,
    answer_first_prompt,
    build_repair_plan,
    parse_v3_difficulty_answers,
    scientific_prompt_body,
)


class P12RecencyBiasRepairV3Test(unittest.TestCase):
    def fixture(self, root: Path) -> None:
        (root / "runtime-failure-manifest-v2.json").write_text(json.dumps({
            "failure_manifest_sha256": "b" * 64,
            "provider_calls_charged": 5,
            "remaining_model_call_budget": 187,
        }))
        (root / "harness-implementation-manifest-v2.json").write_text(json.dumps({"harness_manifest_sha256": "a" * 64}))

    def test_answer_first_changes_only_return_protocol(self):
        pair = next(row for row in difficulty_calibration_pairs() if row["pair_id"] == FAILED_PAIR)
        base = difficulty_prompt(pair)
        new = answer_first_prompt(pair)
        self.assertEqual(scientific_prompt_body(base), scientific_prompt_body(new))
        self.assertNotEqual(base, new)
        self.assertIn("P12_ANSWERS backward=<integer> forward=<integer>", new)

    def test_parser_prefers_function_then_accepts_exact_first_line(self):
        function = {"function_calls": [{"name": "submit_p12_difficulty_answers", "arguments": json.dumps({"backward_answer": 7, "forward_answer": 9})}], "text": "P12_ANSWERS backward=1 forward=2"}
        self.assertEqual(parse_v3_difficulty_answers(function), ({"backward_answer": 7, "forward_answer": 9}, "FUNCTION_CALL"))
        text = {"function_calls": [], "text": "P12_ANSWERS backward=-3 forward=8\nreasoning continues"}
        self.assertEqual(parse_v3_difficulty_answers(text), ({"backward_answer": -3, "forward_answer": 8}, "ANSWER_FIRST_TEXT"))
        with self.assertRaisesRegex(ValueError, "exact first-line"):
            parse_v3_difficulty_answers({"function_calls": [], "text": "Reasoning first\nP12_ANSWERS backward=-3 forward=8"})

    def test_plan_is_single_retry_and_budget_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.fixture(root)
            plan = build_repair_plan(root)
            self.assertEqual(plan["retry"]["pair_id"], FAILED_PAIR)
            self.assertEqual(plan["retry"]["max_attempts"], 1)
            self.assertTrue(plan["scientific_prompt_body_unchanged"])
            self.assertEqual(plan["replacement_provider_call_cap"], REPLACEMENT_PROVIDER_CALL_CAP)
            self.assertEqual(plan["provider_calls_already_charged"] + plan["replacement_provider_call_cap"], 106)
            self.assertLessEqual(106, 192)


if __name__ == "__main__":
    unittest.main()
