from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper_drafts" / "c1-manuscript-strengthening-20260825"


class TestC1PactaV11Closure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.closure = json.loads((PAPER / "c1-pacta-v11-pilot-closure-20260830.json").read_text())
        cls.audit = json.loads((PAPER / "c1-pacta-v11-claim-audit-20260830.json").read_text())
        cls.asset = json.loads((ROOT / "research_pipeline" / "c1_pacta_v11_schema_repair_failure_asset_20260830.json").read_text())["asset"]
        cls.registry = json.loads((ROOT / "research_pipeline" / "external_failure_assets.json").read_text())

    def test_v1_and_v11_are_separate(self):
        lineage = self.closure["lineage"]
        self.assertEqual(lineage["PACTA_v1"]["status"], "INVALID_UNQUALIFIED_EXECUTION")
        self.assertEqual(lineage["PACTA_v1"]["partial_policy_responses_excluded"], 18)
        self.assertEqual(lineage["PACTA_v11"]["status"], "SINGLE_VARIABLE_ACTION_SCHEMA_EXTRACTION_REPAIR")
        self.assertFalse(lineage["PACTA_v11"]["scientific_object_changed"])

    def test_schema_hashes_and_qualification(self):
        repair = self.closure["repair"]
        self.assertNotEqual(repair["source_system_instruction_sha256"], repair["action_schema_sha256"])
        self.assertTrue(repair["hashes_persisted_separately"])
        q = self.closure["zero_science_schema_qualification"]
        self.assertEqual(q["exact_schema_pass"], "40/40")
        self.assertEqual(q["model_drift"], 0)
        self.assertEqual(q["thinking_fallback"], 0)

    def test_fresh_outcome_blind_pilot(self):
        pool = self.closure["prospective_pool"]
        self.assertEqual(pool["states"], 23)
        self.assertEqual(pool["templates"], 7)
        self.assertEqual([x["future_task"] for x in pool["pilot"]], [353, 238, 272, 653, 440, 792, 264])
        self.assertEqual(pool["prior_v1_overlap"], 0)
        self.assertTrue(pool["selection_outcome_blind"])
        self.assertFalse(pool["unused_states_outcomes_read"])

    def test_projection_stop_and_gate_geometry(self):
        pilot = self.closure["pilot"]
        realization = pilot["projection_realization"]
        self.assertEqual(realization["exact_top_level_action_next_goal"], "28/28")
        self.assertEqual(realization["current_state_field"], "0/28")
        self.assertEqual(realization["strict_exact_schema"], "27/28")
        self.assertEqual(realization["failure_states"], [238])
        self.assertTrue(realization["original_v1_inherited_response_envelope_repaired"])
        self.assertEqual(pilot["gate_geometry"]["open"], "0/7")
        self.assertEqual(pilot["gate_geometry"]["closed"], "7/7")
        self.assertEqual(pilot["execution"]["policy_calls"], 0)
        self.assertTrue(all(value is None for key, value in pilot["U"].items() if key != "reason"))

    def test_claim_boundary_and_downstream_locks(self):
        authority = self.closure["claim_authority"]
        self.assertEqual(authority["method_status"], "PACTA_V11_NOT_QUALIFIED")
        self.assertFalse(authority["negative_mechanism_result"])
        self.assertEqual(authority["active_manuscript"], "R9")
        self.assertFalse(authority["R10_created"])
        self.assertFalse(self.closure["confirmatory"]["executed"])
        self.assertFalse(self.closure["terminal"]["executed"])
        self.assertEqual(self.audit["status"], "PASS")
        self.assertTrue(all(row["pass"] for row in self.audit["checks"]))
        self.assertFalse(any(self.audit["authority"].values()))

    def test_research_os_lesson_and_registry(self):
        expected = (
            "Passing a native system instruction as an action schema can cause the projector "
            "to follow a stronger inherited response envelope. Action-schema qualification "
            "must separate tool affordance specification from policy/output instructions "
            "before scientific execution."
        )
        self.assertEqual(self.asset["institutional_lesson"], expected)
        self.assertEqual(
            self.asset["signature"],
            "operationalization:pacta-scientific-projection-cardinality-and-gate-realization",
        )
        self.assertEqual(self.asset["affected_layer"], "operationalization")
        self.assertTrue(self.asset["reusable_precheck"])
        entry = {
            "source_path": "research_pipeline/c1_pacta_v11_schema_repair_failure_asset_20260830.json",
            "source_key": "asset",
        }
        self.assertEqual(self.registry["assets"].count(entry), 1)
        self.assertFalse(self.asset["scientific_authority"])
        self.assertFalse(self.registry["scientific_authority"])


if __name__ == "__main__":
    unittest.main()
