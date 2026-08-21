from __future__ import annotations

import copy
import unittest

from .governance_protocol import build_governance_state
from .paper_first_problem_discovery_contract import build_problem_discovery_contract_state
from .paper_first_problem_generator import installed_problem_generator_policy
from .paper_quality_gate import POLICY as PAPER_QUALITY_POLICY
from .premium_model_policy import policy_summary as premium_model_policy_summary
from .research_candidate_portfolio import build_research_candidate_portfolio
from .research_harness_assurance import build_research_harness_assurance
from .scientific_research_graph import build_scientific_research_graph
from .search_funnel_telemetry import build_search_funnel_telemetry


def _portfolio() -> dict:
    return build_research_candidate_portfolio(
        generator_state={"status": "GENERATED_PRE_F0_EVIDENCE_ACQUISITION", "candidates": []},
        pre_f0_state={
            "status": "PRE_F0_QUEUE_READY",
            "rows": [
                {"candidate_id": "C1", "title": "one", "discovery_lane": "ASSUMPTION_BREAK", "reduction_blockers": ["unresolved-exact-reduction-test:1"]},
                {"candidate_id": "C2", "title": "two", "discovery_lane": "ASSUMPTION_BREAK", "reduction_blockers": ["support-missing:asset"]},
            ],
        },
        problem_gate_state={"audited": [], "passed": [], "blocked": []},
        paper_design_backlog_state={"entries": []},
    )


def _telemetry(portfolio: dict) -> dict:
    return build_search_funnel_telemetry(
        primary_state={"summary": {"verified": 32, "selected": 5}},
        generator_state={
            "status": "GENERATED_PRE_F0_EVIDENCE_ACQUISITION",
            "summary": {"raw_seeds": 2, "semantic_unique_seeds": 2, "breadth_archive": 2, "pre_f0_eligible": 2, "semantic_clear": 0},
        },
        pre_f0_state={
            "summary": {"queued": 2},
            "rows": [
                {"reduction_blockers": ["unresolved-exact-reduction-test:1"]},
                {"reduction_blockers": ["support-missing:asset"]},
            ],
        },
        pre_f0_support_state={"summary": {"support_qualified": 0, "hold_support_unavailable": 2}},
        problem_gate_state={"summary": {"submitted": 0, "passed_problem_gate": 0, "paper_design_eligible": 0}},
        discovery_frontier_state={"status": "LIVE_SOURCE_DISCOVERY_PENDING"},
        candidate_portfolio_state=portfolio,
    )


class ResearchHarnessAlignmentTest(unittest.TestCase):
    def test_persistent_portfolio_keeps_multiple_holds_without_promotion(self) -> None:
        portfolio = _portfolio()
        self.assertEqual(portfolio["summary"]["visible_candidates"], 2)
        self.assertEqual(portfolio["summary"]["search_holds"], 2)
        self.assertEqual(portfolio["summary"]["active_problem_lines"], 0)
        self.assertEqual(portfolio["summary"]["automatic_promotions"], 0)
        self.assertFalse(portfolio["scientific_authority"])
        self.assertEqual({row["candidate_id"] for row in portfolio["rows"]}, {"C1", "C2"})

    def test_funnel_does_not_call_pre_f0_support_hold_an_idea_generation_failure(self) -> None:
        portfolio = _portfolio()
        telemetry = _telemetry(portfolio)
        self.assertEqual(telemetry["bottleneck"]["key"], "PRE_F0_SUPPORT_PROVENANCE")
        self.assertIn("not an idea-generation or scientific failure", telemetry["bottleneck"]["explanation"])
        adaptation = telemetry["search_adaptation"]
        self.assertEqual(adaptation["status"], "PROPOSE_SUPPORT_AWARE_NEW_SEARCH_FRAME")
        self.assertFalse(adaptation["provider_calls_authorized"])
        self.assertIn("retain_current_candidates_as_support_holds", adaptation["allowed_effects"])
        self.assertIn("convert_support_hold_to_scientific_failure", adaptation["forbidden_effects"])
        self.assertEqual(telemetry["loss_reason_counts"]["unresolved-exact-reduction-test"], 1)
        self.assertEqual(telemetry["loss_reason_counts"]["support-missing"], 1)
        self.assertFalse(telemetry["scientific_authority"])

    def test_harness_assurance_requires_independent_jury_and_zero_authority_controls(self) -> None:
        portfolio = _portfolio()
        telemetry = _telemetry(portfolio)
        assurance = build_research_harness_assurance(
            discovery_contract_state=build_problem_discovery_contract_state(),
            generator_state={"candidates": []},
            installed_generator_policy=installed_problem_generator_policy(portfolio=True),
            premium_model_policy=premium_model_policy_summary(),
            governance_state=build_governance_state(),
            paper_quality_policy=PAPER_QUALITY_POLICY,
            candidate_portfolio_state=portfolio,
            search_telemetry_state=telemetry,
        )
        self.assertEqual(assurance["status"], "PASS_HARNESS_ASSURANCE")
        self.assertEqual(assurance["summary"]["passed"], assurance["summary"]["checks"])
        self.assertFalse(assurance["scientific_authority"])

        bad_policy = installed_problem_generator_policy(portfolio=True)
        bad_policy["same_resolved_model_cannot_count_as_independent_review"] = False
        blocked = build_research_harness_assurance(
            discovery_contract_state=build_problem_discovery_contract_state(),
            generator_state={"candidates": []},
            installed_generator_policy=bad_policy,
            premium_model_policy=premium_model_policy_summary(),
            governance_state=build_governance_state(),
            paper_quality_policy=PAPER_QUALITY_POLICY,
            candidate_portfolio_state=portfolio,
            search_telemetry_state=telemetry,
        )
        self.assertEqual(blocked["status"], "HOLD_HARNESS_ASSURANCE")
        self.assertGreater(blocked["summary"]["failed"], 0)

    def test_failure_asset_does_not_become_principle_closure_without_certificate(self) -> None:
        portfolio = _portfolio()
        graph = build_scientific_research_graph(
            evidence_graph={"nodes": [{"id": "idea:X", "kind": "idea", "text": "X"}], "edges": []},
            candidate_portfolio=portfolio,
            scientific_meta_trace={"principles": [{"principle_id": "P", "idea_id": "X", "mechanism": "m", "belief_state": "unresolved"}]},
            failure_asset_library={
                "assets": [{"idea_id": "X", "signature": "method_realization:bad", "affected_layer": "method_realization", "does_not_imply": "core-principle failure"}],
                "dead_end_registry": {"certified_principle_dead_ends": []},
            },
            pilot_registry={"phases": [{"idea_id": "X", "phase": "P0", "title": "P0", "status": "stopped"}]},
        )
        self.assertEqual(graph["summary"]["failure_asset_nodes"], 1)
        self.assertEqual(graph["summary"]["scientific_closure_nodes"], 0)
        self.assertEqual(graph["summary"]["principle_closure_edges"], 0)

        certified_library = {
            "assets": [],
            "dead_end_registry": {"certified_principle_dead_ends": [{"principle_id": "P", "principle_dead_end_certified": True, "counter_explanation": "same-information reduction"}]},
        }
        closed = build_scientific_research_graph(
            evidence_graph={"nodes": [{"id": "idea:X", "kind": "idea", "text": "X"}], "edges": []},
            candidate_portfolio={"rows": []},
            scientific_meta_trace={"principles": [{"principle_id": "P", "idea_id": "X", "mechanism": "m", "belief_state": "closed"}]},
            failure_asset_library=certified_library,
            pilot_registry={"phases": []},
        )
        self.assertEqual(closed["summary"]["scientific_closure_nodes"], 1)
        self.assertEqual(closed["summary"]["principle_closure_edges"], 1)


if __name__ == "__main__":
    unittest.main()
