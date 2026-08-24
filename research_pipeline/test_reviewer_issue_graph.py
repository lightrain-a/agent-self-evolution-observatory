from __future__ import annotations

import json
import unittest

from .config import PROJECT_ROOT
from .reviewer_issue_graph import build_meta_review, build_review_control_state_from_registry, build_reviewer_issue_graph


class ReviewerIssueGraphTest(unittest.TestCase):
    def receipts(self) -> list[dict]:
        return [{
            "review_sha256": "a" * 64,
            "objections": [
                {"objection_id": "R1", "category": "empirical-sufficiency", "text": "Need a decisive matched control.", "decision_critical": True, "evidence_state": "MISSING_DECISIVE_EVIDENCE", "claim_ids": ["C1"]},
                {"objection_id": "R2", "category": "clarity", "text": "Existing evidence is hard to locate.", "decision_critical": False, "evidence_state": "EXISTING_EVIDENCE", "claim_ids": ["C1"]},
                {"objection_id": "R3", "category": "scope", "text": "Please claim a broader setting.", "decision_critical": True, "evidence_state": "REQUIRES_NEW_CLAIM", "claim_ids": ["C2"]},
            ],
            "actions": [
                {"objection_id": "R1", "action_class": "TARGETED_EXPERIMENT", "claim_expansion_authorized": False},
                {"objection_id": "R2", "action_class": "NARRATIVE_REPAIR", "claim_expansion_authorized": False},
                {"objection_id": "R3", "action_class": "PRESERVE_LIMITATION", "claim_expansion_authorized": False},
            ],
        }]

    def test_issue_graph_prioritizes_without_granting_authority(self) -> None:
        graph = build_reviewer_issue_graph(paper_id="P1", review_receipts=self.receipts())
        self.assertEqual(graph["status"], "PASS_REVIEWER_ISSUE_GRAPH")
        self.assertEqual(graph["summary"]["issues"], 3)
        self.assertEqual(graph["summary"]["targeted_experiment_proposals"], 1)
        self.assertEqual(graph["summary"]["experiment_authorized"], 0)
        by_id = {row["issue_id"].split(":")[-1]: row for row in graph["nodes"]}
        self.assertTrue(by_id["R1"]["experiment_required"])
        self.assertFalse(by_id["R1"]["experiment_authorized"])
        self.assertFalse(by_id["R1"]["reviewer_prose_exposed"])
        self.assertFalse(graph["scientific_authority"])

    def test_method_incrementality_does_not_default_to_complexification_for_insight_paper(self) -> None:
        receipt = [{
            "review_sha256": "b" * 64,
            "objections": [{
                "objection_id": "M1",
                "category": "method-incrementality",
                "text": "The method is a simple filter and appears incremental.",
                "decision_critical": True,
                "evidence_state": "EXISTING_EVIDENCE",
                "claim_ids": ["C2"],
            }],
            "actions": [{"objection_id": "M1", "action_class": "NARRATIVE_REPAIR", "claim_expansion_authorized": False}],
        }]
        graph = build_reviewer_issue_graph(
            paper_id="P-insight",
            review_receipts=receipt,
            paper_contribution={"primary_contribution_type": "insight"},
        )
        issue = graph["nodes"][0]
        self.assertEqual(issue["attacked_contribution_layer"], "method")
        self.assertEqual(issue["repair_focus"], "strengthen-primary-contribution-evidence-not-method-complexity")
        self.assertFalse(issue["method_complexification_is_default_repair"])
        self.assertEqual(graph["summary"]["method_objections_redirected_from_complexification"], 1)

    def test_resolution_requires_verification_artifact(self) -> None:
        graph = build_reviewer_issue_graph(paper_id="P1", review_receipts=self.receipts(), resolutions={"R1": {"resolved": True}})
        self.assertEqual(graph["status"], "BLOCK_REVIEWER_ISSUE_GRAPH")
        self.assertTrue(any(x.startswith("resolved-issue-without-verification:") for x in graph["blockers"]))
        r1 = next(row for row in graph["nodes"] if row["issue_id"].endswith(":R1"))
        self.assertEqual(r1["status"], "OPEN")

    def test_meta_review_explains_disagreement_instead_of_voting(self) -> None:
        graph = build_reviewer_issue_graph(paper_id="P1", review_receipts=self.receipts())
        meta = build_meta_review(graph)
        self.assertEqual(meta["status"], "META_REVIEW_COMPILED")
        self.assertEqual(meta["disagreement_clusters"][0]["claim_id"], "C1")
        self.assertFalse(meta["vote_or_score_is_scientific_authority"])
        self.assertFalse(meta["experiment_authority"])

    def test_current_paper_registry_compiles_cross_paper_review_patterns(self) -> None:
        registry = json.loads((PROJECT_ROOT / "generated" / "paper-registry.json").read_text(encoding="utf-8"))
        state = build_review_control_state_from_registry(registry)
        self.assertEqual(state["status"], "REVIEW_CONTROL_STATE_COMPILED")
        self.assertEqual(state["summary"]["papers"], 5)
        self.assertGreaterEqual(state["summary"]["review_receipts"], 10)
        self.assertGreater(state["summary"]["repeated_cross_paper_patterns"], 0)
        self.assertEqual(state["summary"]["automatic_memory_promotions"], 0)
        self.assertTrue(all(row["reviewer_prose_exposed"] is False for row in state["papers"]))


if __name__ == "__main__":
    unittest.main()
