from __future__ import annotations

import unittest

from .asset_first_stri_autoskill_multitask_pilot_20260824 import build


class AutoSkillMultitaskPilotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = build()

    def test_qualification_and_selection_are_outcome_blind(self) -> None:
        s = self.result["summary"]
        self.assertEqual((s["qualified_units"], s["screened_units"]), (9, 9))
        self.assertTrue(s["selection_outcome_blind"])
        self.assertTrue(s["selection_rule_recomputed"])
        self.assertEqual(s["selected_units"], ["skillmisevo-coding-22-P21", "skillmisevo-coding-21-P19"])

    def test_stage1_stop_is_exact_and_no_expansion_is_authorized(self) -> None:
        s = self.result["summary"]
        self.assertEqual(s["stage1_runs"], 8)
        self.assertTrue(s["all_executions_valid"])
        self.assertEqual(s["decision"], "STOP_EXPANSION_STAGE1_GATE_NOT_MET")
        self.assertFalse(s["stage1_gate_pass"])
        self.assertFalse(s["stage2_authorized"])
        self.assertFalse(s["remaining_units_authorized"])

    def test_unit_diagnoses_and_authority_boundary(self) -> None:
        s = self.result["summary"]
        self.assertEqual(s["unit_diagnoses"]["skillmisevo-coding-22-P21"], "CONTROL_NONCONCORDANCE_NO_SPLIT_SPECIFIC_ATTRIBUTION")
        self.assertEqual(s["unit_diagnoses"]["skillmisevo-coding-21-P19"], "NO_ACTION_SIGNATURE_SEPARATION")
        self.assertEqual(s["new_agent_runs"], 8)
        self.assertEqual(s["judge_calls"], 0)
        self.assertEqual(s["new_gpu_runs"], 0)
        self.assertFalse(s["claim_expansion"])
        self.assertEqual(s["failure_stop_class"], "PREREGISTERED_PILOT_GATE_STOP")


if __name__ == "__main__":
    unittest.main()
