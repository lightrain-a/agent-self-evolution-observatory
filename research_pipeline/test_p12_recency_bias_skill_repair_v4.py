from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .p12_recency_bias_harness import skill_compilation_prompt, skill_calibration_bundles
from .p12_recency_bias_skill_repair_v4 import (
    FAILED_BUNDLE,
    REPLACEMENT_PROVIDER_CALL_CAP,
    build_repair_plan,
    parse_skills_v4,
    scientific_prompt_body,
    skill_prompt_v4,
)


class P12RecencyBiasSkillRepairV4Test(unittest.TestCase):
    def fixture(self, root: Path) -> None:
        (root / "runtime-failure-manifest-v3.json").write_text(json.dumps({
            "failure_manifest_sha256": "b" * 64,
            "provider_calls_charged": 8,
            "remaining_model_call_budget": 184,
        }))
        (root / "harness-implementation-manifest-v3.json").write_text(json.dumps({"harness_manifest_sha256": "a" * 64}))

    def test_skill_prompt_changes_only_return_protocol(self):
        bundle = next(row for row in skill_calibration_bundles() if row["bundle_id"] == FAILED_BUNDLE)
        base = skill_compilation_prompt(bundle)
        new = skill_prompt_v4(bundle)
        self.assertEqual(scientific_prompt_body(base), scientific_prompt_body(new))
        self.assertIn('"older_skill_text":"..."', new)

    def test_skill_parser_prefers_function_then_json_first(self):
        function = {"function_calls": [{"name": "submit_p12_skills", "arguments": json.dumps({"older_skill_text": "Use robust pattern A.", "newer_skill_text": "Use robust pattern B."})}], "text": ""}
        self.assertEqual(parse_skills_v4(function)[1], "FUNCTION_CALL")
        text = {"function_calls": [], "text": '{"older_skill_text":"Use robust pattern A.","newer_skill_text":"Use robust pattern B."}\nextra reasoning'}
        values, source = parse_skills_v4(text)
        self.assertEqual(source, "JSON_FIRST_TEXT")
        self.assertNotEqual(values["older_skill_text"], values["newer_skill_text"])
        with self.assertRaisesRegex(ValueError, "first-line JSON"):
            parse_skills_v4({"function_calls": [], "text": 'Reasoning first\n{"older_skill_text":"A skill long enough here.","newer_skill_text":"Another skill long enough."}'})

    def test_plan_reuses_linear_and_bounds_remaining_calls(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.fixture(root)
            plan = build_repair_plan(root)
            self.assertEqual(plan["reuse_completed_skill_bundles"], ["SKILL-BUNDLE-LINEAR"])
            self.assertEqual(plan["retry_failed_skill_bundle"]["bundle_id"], FAILED_BUNDLE)
            self.assertEqual(plan["unstarted_skill_bundles"], ["SKILL-BUNDLE-ALTERNATING2", "SKILL-BUNDLE-CYCLIC3"])
            self.assertEqual(plan["replacement_provider_call_cap"], REPLACEMENT_PROVIDER_CALL_CAP)
            self.assertEqual(plan["provider_calls_already_charged"] + plan["replacement_provider_call_cap"], 107)
            self.assertLessEqual(107, 192)
            self.assertTrue(all(x["scientific_prompt_body_unchanged"] for x in plan["prompt_bindings"].values()))


if __name__ == "__main__":
    unittest.main()
