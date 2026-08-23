from __future__ import annotations

import unittest

from research_pipeline.failure_memory_reasoningbank_status_l2_contract import build_contract, build_power


def preflight() -> dict:
    return {
        "cohort_summary": {
            "template_independent_units": 36,
            "downstream_task_ids": [str(i) for i in range(36)],
            "source_task_ids": [str(i + 100) for i in range(36)],
        },
        "first_party_reasoningbank_binding": {
            "commit": "ed80611788292ea739f1effd31f16c53823b8a0d",
            "file_sha256": {"a": "b"},
        },
        "frozen_downstream_asset": {"sha256": "asset", "config_sha256": "config"},
        "runtime_materialization": {"current_69_exact_runtime_found": False},
    }


class TestReasoningBankStatusL2Contract(unittest.TestCase):
    def test_power_sensitivity_has_expected_medium_variance_case(self) -> None:
        p = build_power(preflight(), preflight_sha="pre", census_sha="cen")
        medium = next(x for x in p["planning_scenarios"] if x["task_level_sd"] == 0.30)
        self.assertEqual(medium["independent_tasks"], 36)
        self.assertAlmostEqual(medium["approx_two_sided_power"], 0.850839, places=6)
        self.assertTrue(medium["two_sided_target_0_80_met"])
        high = next(x for x in p["planning_scenarios"] if x["task_level_sd"] == 0.40)
        self.assertFalse(high["two_sided_target_0_80_met"])
        self.assertFalse(p["planning_decision"]["claim_80_percent_power_unconditionally"])

    def test_contract_is_two_sided_and_fail_closed(self) -> None:
        pf = preflight()
        power = build_power(pf, preflight_sha="pre", census_sha="cen")
        c = build_contract(pf, power, preflight_sha="pre", power_path=__import__("pathlib").Path("power.json"))
        self.assertEqual(c["primary_analysis"]["primary_test"], "two-sided task-level paired randomization/sign-flip test")
        self.assertFalse(c["primary_analysis"]["directional_sign_claim_predeclared"])
        self.assertTrue(c["intervention"]["memory_items_bytes_identical_across_arms"])
        self.assertTrue(c["intervention"]["single_character_treatment_difference"])
        self.assertFalse(c["execution_gate"]["execution_permitted"])
        self.assertFalse(c["separate_from_historical_objects"]["pooling_with_R5_or_bridge"])

    def test_exact_runtime_cannot_be_substituted(self) -> None:
        pf = preflight()
        power = build_power(pf, preflight_sha="pre", census_sha="cen")
        c = build_contract(pf, power, preflight_sha="pre", power_path=__import__("pathlib").Path("power.json"))
        self.assertEqual(c["downstream_runtime"]["required_browsergym"], "0.14.1")
        self.assertFalse(c["downstream_runtime"]["installed_0_4_0_runtime_may_substitute"])
        self.assertFalse(c["execution_gate"]["exact_runtime_materialized"])


if __name__ == "__main__":
    unittest.main()
