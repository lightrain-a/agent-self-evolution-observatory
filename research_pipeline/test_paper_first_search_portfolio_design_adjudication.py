from __future__ import annotations

import unittest

from .paper_first_search_portfolio_design_adjudication import (
    _shadow_dead_end_memory,
    build_search_portfolio_design_adjudication,
    validate_search_portfolio_design_adjudication,
)


class SearchPortfolioPaperDesignAdjudicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_search_portfolio_design_adjudication()

    def test_shadow_counterfactual_survivors_are_conservatively_routed(self) -> None:
        self.assertEqual(validate_search_portfolio_design_adjudication(self.state), [])
        summary = self.state["summary"]
        self.assertEqual(
            (summary["reviewed"], summary["advance_to_method_design"], summary["revise_paper_problem"], summary["stop_standalone"]),
            (2, 0, 1, 1),
        )
        rows = {row["id"]: row for row in self.state["rows"]}
        self.assertEqual(rows["SP-09"]["verdict"], "STOP_STANDALONE_COLLISION_KEEP_CONTEXT_RISK_AXIS")
        self.assertEqual(rows["SP-15"]["verdict"], "REVISE_PAPER_PROBLEM_SUPPORT_INVENTORY_REQUIRED")
        self.assertIn("point-identifiable", rows["SP-15"]["revised_problem"])

    def test_shadow_counterfactual_pass_does_not_leak_downstream_authority(self) -> None:
        self.assertTrue(self.state["policy"]["source_is_shadow_search_portfolio"])
        self.assertTrue(self.state["policy"]["shadow_queue_has_zero_paper_design_authority"])
        self.assertTrue(self.state["policy"]["cannot_grant_or_revoke_live_paper_design_authority"])
        for row in self.state["rows"]:
            self.assertTrue(row["historical_counterfactual_problem_gate_pass"])
            self.assertFalse(row["live_paper_design_eligible"])
            self.assertTrue(row["counterfactual_problem_gate_pass_does_not_grant_live_paper_design"])
            for key in ("method_design_authorized", "experiment_blueprint_authorized", "local_validation_authorized", "p0_authorized", "gpu_authorized"):
                self.assertFalse(row[key])
        for key in ("method_design_authorized", "experiment_blueprint_authorized", "local_validation_authorized", "p0_authorized", "gpu_authorized"):
            self.assertEqual(self.state["summary"][key], 0)

    def test_shadow_dead_end_memory_cannot_touch_live_discovery(self) -> None:
        memory = self.state["shadow_dead_end_memory"]
        self.assertFalse(memory["scientific_authority"])
        self.assertFalse(memory["live_source_coverage_effect"])
        self.assertTrue(memory["cannot_mutate_canonical_generator_or_queue"])
        self.assertTrue({"SP-09", "SP-15"}.issubset({row["source_candidate_id"] for row in memory["blocked_objects"]}))

    def test_r2_near_miss_preflight_compiles_into_future_shadow_search_memory(self) -> None:
        memory=self.state["shadow_dead_end_memory"]
        rows={row["source_candidate_id"]:row for row in memory["blocked_objects"]}
        self.assertEqual(memory["near_miss_preflight_count"],4)
        self.assertEqual(self.state["summary"]["near_miss_support_holds"],1)
        self.assertEqual(self.state["summary"]["near_miss_current_primary_stops"],2)
        self.assertEqual(self.state["summary"]["near_miss_mature_theory_stops"],1)
        self.assertEqual(rows["SHADOW-P03-C01"]["disposition"],"HOLD_SUPPORT_UNAVAILABLE")
        self.assertEqual(rows["SHADOW-P09-C01"]["disposition"],"STOP_CURRENT_PRIMARY_COLLISION")
        self.assertEqual(rows["SHADOW-P05-C01"]["disposition"],"STOP_MATURE_THEORY_REDUCTION")
        self.assertEqual(rows["SHADOW-P12-C02"]["disposition"],"STOP_CURRENT_PRIMARY_COLLISION")
        for cid in ("SHADOW-P03-C01","SHADOW-P09-C01","SHADOW-P05-C01","SHADOW-P12-C02"):
            self.assertFalse(rows[cid]["scientific_authority"])

    def test_current_source_hard_veto_compiles_into_future_shadow_search_memory(self) -> None:
        memory=_shadow_dead_end_memory({"latest_run":{"candidates":[{"candidate_id":"SHADOW-X","title":"Retrieval attribution gap","search_primitive":"IDENTIFIABILITY_GAP","current_source_status":"complete","current_source_verdict":"BLOCK","current_source_reduction_class":"VALID_HARD_VETO","current_source_strongest_reduction":"generic identifiability over an omitted compiled-context variable","current_source_reason":"Current primary work already exposes retrieval and compilation as separate pipeline objects.","current_source_source_refs":["arXiv:2605.10114","arXiv:2608.05604"]}]}})
        dynamic=[row for row in memory["blocked_objects"] if row["source_candidate_id"]=="SHADOW-X"]
        self.assertEqual(len(dynamic),1)
        self.assertEqual(memory["current_source_hard_veto_count"],1)
        self.assertEqual(dynamic[0]["search_primitive"],"IDENTIFIABILITY_GAP")
        self.assertIn("omitted compiled-context variable",dynamic[0]["strongest_reduction"])
        self.assertEqual(dynamic[0]["current_source_refs"],["arXiv:2605.10114","arXiv:2608.05604"])
        self.assertFalse(dynamic[0]["scientific_authority"])
        self.assertIn("instrumenting",dynamic[0]["reopen_only_if"])

    def test_missing_domestic_reviewers_are_recorded_as_missing_not_pass(self) -> None:
        consultation = self.state["advisory_consultation"]
        self.assertFalse(consultation["scientific_authority"])
        self.assertTrue(consultation["failed_or_missing_review_is_not_pass"])
        self.assertTrue(all("missing:" in row["SP-09"] and "missing:" in row["SP-15"] for row in consultation["reviewers"]))

    def test_sp09_has_direct_governance_and_context_collisions(self) -> None:
        row = next(row for row in self.state["rows"] if row["id"] == "SP-09")
        refs = {source["ref"] for source in row["primary_sources"]}
        self.assertTrue({"arXiv:2602.12430", "arXiv:2607.01136", "arXiv:2608.09732", "arXiv:2605.30723"}.issubset(refs))
        self.assertIn("contextual constrained policy", row["cheapest_problem_falsifier"])

    def test_sp15_revision_requires_identifiability_support_before_method(self) -> None:
        row = next(row for row in self.state["rows"] if row["id"] == "SP-15")
        refs = {source["ref"] for source in row["primary_sources"]}
        self.assertTrue({"arXiv:2608.08640", "arXiv:2606.18051", "arXiv:2606.10388", "arXiv:2606.03565"}.issubset(refs))
        self.assertGreaterEqual(len(row["required_problem_revision"]), 6)
        self.assertIn("oracle ranker", " ".join(row["required_problem_revision"]))
        self.assertEqual(self.state["summary"]["support_inventory_required"], 1)


if __name__ == "__main__":
    unittest.main()
