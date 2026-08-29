from __future__ import annotations

import unittest

from research_pipeline.asset_first_stri_reasoningbank_p1_adjudicate import (
    DECISION,
    build_adjudication,
    validate_adjudication,
)


class ReasoningBankP1MinimalPilotAdjudicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_adjudication(adjudicated_at_utc="2026-08-29T00:00:00+00:00")

    def test_terminal_decision_preserves_complete_but_unqualified_pilot(self) -> None:
        self.assertEqual(self.state["decision"], DECISION)
        self.assertTrue(self.state["execution_complete"])
        self.assertFalse(self.state["implementation_qualified"])
        self.assertFalse(self.state["scientific_population_claim_authorized"])
        self.assertFalse(self.state["full_p1_authorized"])
        self.assertFalse(self.state["reruns_or_replacements_performed"])
        self.assertEqual(validate_adjudication(self.state), [])

    def test_all_raw_artifacts_and_treatments_are_content_address_valid(self) -> None:
        checks = self.state["qualification_checks"]
        self.assertTrue(checks["all_10_planned_runs_persisted_without_replacement"])
        self.assertTrue(checks["all_index_file_sha256_values_valid"])
        self.assertTrue(checks["index_payload_sha256_valid"])
        self.assertTrue(checks["all_run_payload_sha256_values_valid"])
        self.assertTrue(checks["treatments_match_frozen_manifest"])
        self.assertTrue(all(self.state["treatment_checks"].values()))

    def test_reunion_and_case_id_placebo_are_equal_at_r1_then_diverge_at_r2(self) -> None:
        for rows in self.state["comparisons"].values():
            for pair in ("A_vs_B", "B_vs_E"):
                comparison = rows[pair]
                self.assertTrue(comparison["R0_selected_memory_equal"])
                self.assertTrue(comparison["R1_first_request_byte_equal"])
                self.assertFalse(comparison["R2_equal_excluding_timestamps"])
                self.assertEqual(comparison["first_model_visible_divergence"], "R2")

    def test_timeout_bug_chain_is_preserved_and_not_retroactively_repaired(self) -> None:
        failure = self.state["failure_adjudication"]
        self.assertEqual(failure["observed_terminal_provider_failure_count"], 3)
        self.assertEqual(
            set(failure["affected_runs"]),
            {
                "pilot-sympy__sympy-17318-A",
                "pilot-sympy__sympy-17318-B",
                "pilot-sympy__sympy-17318-C",
            },
        )
        self.assertTrue(failure["causal_chain_confirmed_from_persisted_runs_and_frozen_source"])
        self.assertFalse(
            self.state["qualification_checks"]["no_blank_model_visible_message_content"]
        )
        repair = self.state["repair_receipt"]
        self.assertFalse(repair["historical_run_artifacts_changed"])
        self.assertFalse(repair["rerun_performed"])
        self.assertFalse(repair["qualification_restored"])

    def test_r4_is_flat_within_each_case_without_overclaiming_d(self) -> None:
        outcomes = self.state["descriptive_outcomes"]
        self.assertEqual(outcomes["all_runs"]["resolved"], 5)
        self.assertEqual(outcomes["all_runs"]["provider_failures"], 3)
        self.assertEqual(outcomes["all_runs"]["valid_evaluators"], 10)
        self.assertEqual(
            outcomes["by_instance"]["pytest-dev__pytest-5631"]["resolved_count"], 5
        )
        self.assertEqual(
            outcomes["by_instance"]["sympy__sympy-17318"]["resolved_count"], 0
        )
        self.assertTrue(
            all(row["all_five_R4_outcomes_equal"] for row in outcomes["by_instance"].values())
        )
        self.assertTrue(
            self.state["scientific_interpretation"]["D_is_not_a_performance_advantage"]
        )


if __name__ == "__main__":
    unittest.main()
