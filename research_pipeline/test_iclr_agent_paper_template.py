from __future__ import annotations

import copy
import hashlib
import json
import unittest

from .iclr_agent_paper_template import TEMPLATE_ID, TEMPLATE_VERSION, audit_template_binding, template_payload


class ICLRAgentPaperTemplateTest(unittest.TestCase):
    def test_template_structure_and_authority(self) -> None:
        payload = template_payload()
        self.assertEqual(payload["template_id"], TEMPLATE_ID)
        self.assertEqual(payload["template_version"], TEMPLATE_VERSION)
        self.assertEqual(len(payload["derived_from"]), 8)
        self.assertTrue(all(str(row.get("url") or "").startswith("https://") for row in payload["derived_from"]))
        self.assertAlmostEqual(sum(float(row["pages"]) for row in payload["page_budget_main_body"]), 9.0)
        self.assertEqual([row["id"] for row in payload["introduction_paragraphs"]], [f"I{i}" for i in range(1, 8)])
        self.assertEqual([row["id"] for row in payload["experiment_lanes"]], [f"E{i}" for i in range(1, 8)])
        self.assertEqual(sum(row["required"] is True for row in payload["experiment_lanes"]), 6)
        self.assertEqual(len(payload["method"]["component_questions"]), 6)
        self.assertTrue(all(value is False for value in payload["authority"].values()))
        expected = copy.deepcopy(payload); expected.pop("template_sha256")
        self.assertEqual(payload["template_sha256"], hashlib.sha256(json.dumps(expected, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest())

    def test_required_binding_fails_closed(self) -> None:
        missing = audit_template_binding({}, required=True)
        self.assertFalse(missing["passed"])
        self.assertIn("iclr-template-id-missing-or-stale", missing["blockers"])

    def test_required_experiment_lanes_bind_or_use_archetype_na(self) -> None:
        binding = {
            "template_id": TEMPLATE_ID,
            "template_version": TEMPLATE_VERSION,
            "experiment_lane_plan": {f"E{i}": {"status": "PLANNED"} for i in range(1, 7)},
        }
        self.assertTrue(audit_template_binding(binding, required=True)["passed"])
        missing = copy.deepcopy(binding);missing["experiment_lane_plan"].pop("E3")
        self.assertFalse(audit_template_binding(missing, required=True)["passed"])
        na = copy.deepcopy(binding);na["experiment_lane_plan"]["E3"]={"status":"NOT_APPLICABLE_WITH_ARCHETYPE_REASON","reason":"exact certificate replaces an empirical mechanism lane"}
        self.assertTrue(audit_template_binding(na, required=True)["passed"])

    def test_template_is_advisory_and_planning_is_not_execution(self) -> None:
        payload = template_payload()
        policy = payload["policy"]
        self.assertTrue(policy["template_cannot_authorize_experiments"])
        self.assertTrue(policy["experiment_lane_planning_is_not_execution"])
        self.assertTrue(policy["historical_manuscripts_are_not_retroactively_demoted"])


if __name__ == "__main__":
    unittest.main()
