from __future__ import annotations

import unittest

from research_pipeline.asset_first_stri_dynamic_mixture_falsifier import adjudicate_dynamic_gate


class DynamicMixtureAdjudicationTest(unittest.TestCase):
    def test_zero_qualified_units_is_inconclusive_not_scientific_stop(self) -> None:
        checks = {
            "contract_valid_per_source": {"actual": 0, "required_min": 16, "pass": False},
            "validator_pattern_tv": {"actual": 0.0, "required_min": 0.05, "pass": False},
            "validator_pattern_tv_bootstrap_lower95": {"actual": 0.0, "required_min": 0.025, "pass": False},
            "max_single_pattern_shift": {"actual": 0.0, "required_min": 0.04, "pass": False},
        }
        out = adjudicate_dynamic_gate(checks)
        self.assertEqual(out["decision"], "INCONCLUSIVE_PROPOSER_QUALIFICATION_FAILED")
        self.assertFalse(out["scientific_result_available"])
        self.assertFalse(out["protocol_valid_for_scientific_update"])
        self.assertFalse(out["qualification_pass"])

    def test_qualified_negative_can_support_scientific_stop(self) -> None:
        checks = {
            "contract_valid_per_source": {"actual": 18, "required_min": 16, "pass": True},
            "validator_pattern_tv": {"actual": 0.03, "required_min": 0.05, "pass": False},
            "validator_pattern_tv_bootstrap_lower95": {"actual": 0.02, "required_min": 0.025, "pass": False},
            "max_single_pattern_shift": {"actual": 0.03, "required_min": 0.04, "pass": False},
        }
        out = adjudicate_dynamic_gate(checks)
        self.assertEqual(out["decision"], "STOP_DYNAMIC_PROPAGATION_GATE_NOT_MET")
        self.assertTrue(out["scientific_result_available"])
        self.assertTrue(out["protocol_valid_for_scientific_update"])
        self.assertTrue(out["qualification_pass"])

    def test_all_qualified_gates_support_positive(self) -> None:
        checks = {
            "contract_valid_per_source": {"actual": 20, "required_min": 16, "pass": True},
            "validator_pattern_tv": {"actual": 0.08, "required_min": 0.05, "pass": True},
            "validator_pattern_tv_bootstrap_lower95": {"actual": 0.04, "required_min": 0.025, "pass": True},
            "max_single_pattern_shift": {"actual": 0.06, "required_min": 0.04, "pass": True},
        }
        out = adjudicate_dynamic_gate(checks)
        self.assertEqual(out["decision"], "DYNAMIC_CURRICULUM_REPRESENTATION_SENSITIVITY_SUPPORTED")
        self.assertTrue(out["scientific_result_available"])
        self.assertTrue(out["protocol_valid_for_scientific_update"])
        self.assertTrue(out["primary_mechanism_positive"])


if __name__ == "__main__":
    unittest.main()
