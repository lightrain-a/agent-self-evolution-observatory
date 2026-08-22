from __future__ import annotations

import unittest

from research_pipeline.research_item_state import (
    build_paper_registry,
    build_research_item_state,
    validate_paper_registry,
    validate_research_item_state,
)


class ResearchItemStateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_research_item_state()
        cls.registry = build_paper_registry(cls.state)
        cls.by_code = {row["code"]: row for row in cls.state["research_items"]}

    def test_projection_counts_and_categories(self) -> None:
        self.assertEqual(validate_research_item_state(self.state), [])
        summary = self.state["summary"]
        self.assertEqual(summary["research_items"], 86)
        self.assertEqual(summary["experiment_records"], 30)
        self.assertEqual(summary["portfolio_experiment_contexts"], 3)
        self.assertEqual(summary["evidence_contexts"], 2)
        self.assertEqual(summary["portfolio_objects"], 91)
        self.assertEqual(
            {key: value["portfolio_total"] for key, value in summary["by_category"].items()},
            {"A": 12, "B": 20, "C": 10, "D": 3, "E": 27, "F": 6, "G": 13},
        )

    def test_support_stop_is_not_scientific_stop(self) -> None:
        self.assertEqual(self.state["summary"]["parent_scientific_states"], {"HOLD": 4, "MERGED": 6, "STOPPED": 16})
        for code in ("A-3", "B-2", "B-3", "E-1"):
            self.assertEqual(self.by_code[code]["scientific_state"], "HOLD")
            self.assertFalse(self.by_code[code]["principle_dead_end_certified"])
            self.assertFalse(self.by_code[code]["execution_authority"]["gpu"])

    def test_stri_handoff_and_paper_registry(self) -> None:
        self.assertEqual(validate_paper_registry(self.registry, self.state), [])
        e7 = self.by_code["E-7"]
        self.assertEqual(e7["scientific_state"], "PAPER_READY")
        self.assertEqual(e7["paper_transition"]["paper_id"], "STRI")
        self.assertEqual(e7["paper_transition"]["status"], "SUBMISSION_READY")
        papers = {row["paper_id"]: row for row in self.registry["papers"]}
        paper = papers["STRI"]
        self.assertEqual(paper["source_research_item"], "E-7")
        self.assertEqual(paper["paper_stage"], "SUBMISSION_READY")
        self.assertTrue(paper["submission_ready"])
        self.assertGreaterEqual(self.registry["summary"]["papers"], 2)
        self.assertGreaterEqual(self.registry["summary"]["submission_ready"], 2)
        self.assertEqual(self.registry["summary"]["scientific_holds"], 0)
        self.assertEqual((paper["claims_supported"], paper["claims_total"], paper["paper_quality_evidence_debt"]), (3, 3, 0))
        safety = papers["AGENT-SAFETY-R9"]
        self.assertEqual((safety["source_research_item"], safety["paper_stage"], safety["scientific_status"]), ("G-1", "SUBMISSION_READY", "READY"))
        self.assertTrue(safety["submission_ready"])
        self.assertEqual(self.by_code["G-1"]["scientific_state"], "HOLD")
        temporal = papers.get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK")
        if temporal:
            self.assertEqual(temporal["paper_stage"], "SUBMISSION_READY")
            self.assertTrue(temporal["submission_ready"])
            self.assertEqual(temporal["source_kind"], "paper-first-discovery-candidate")
            self.assertIsNone(temporal["source_research_item"])
            self.assertEqual(temporal["source_candidates"], ["D2-C06"])
            self.assertEqual(self.registry["summary"]["papers"], 5)
            self.assertEqual(self.registry["summary"]["submission_ready"], 4)
            failure = papers["D2-PAPER-FAILURE-MEMORY-PROVENANCE"]
            self.assertEqual(failure["paper_stage"], "TARGETED_REPAIR")
            self.assertFalse(failure["submission_ready"])

    def test_experiments_are_zero_authority_evidence_events(self) -> None:
        self.assertTrue(all(row["scientific_authority"] is False for row in self.state["experiment_records"]))
        self.assertTrue(all(row["principle_update_authority"] is False for row in self.state["experiment_records"]))
        portfolio = [row for row in self.state["experiment_records"] if row.get("portfolio_context")]
        self.assertEqual({row["portfolio_code"] for row in portfolio}, {"E-7a", "E-7b", "E-7c"})

    def test_agent_safety_support_stop_is_not_principle_dead_end(self) -> None:
        g1 = self.by_code["G-1"]
        self.assertEqual(g1["scientific_state"], "HOLD")
        self.assertFalse(g1["principle_dead_end_certified"])
        self.assertEqual(g1["execution_authority"], {"method": False, "experiment": False, "p0": False, "gpu": False})


if __name__ == "__main__":
    unittest.main()
