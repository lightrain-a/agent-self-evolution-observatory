from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from .research_control_plane import build_experiment_tree, build_research_control_plane_state, evaluate_mode_action, inspect_artifact


class ResearchControlPlaneTest(unittest.TestCase):
    def test_modes_never_grant_direct_scientific_authority(self) -> None:
        self.assertTrue(evaluate_mode_action("DISCOVERY", "draft-candidate")["allowed"])
        forbidden = evaluate_mode_action("DISCOVERY", "write-validated-evidence")
        self.assertFalse(forbidden["allowed"])
        self.assertFalse(forbidden["mode_grants_scientific_authority"])
        self.assertFalse(evaluate_mode_action("PAPER", "write-validated-evidence")["allowed"])

    def test_reproduction_execution_requires_external_authority(self) -> None:
        self.assertFalse(evaluate_mode_action("REPRODUCTION", "execute-reproduction")["allowed"])
        allowed = evaluate_mode_action("REPRODUCTION", "execute-reproduction", execution_authority=True)
        self.assertTrue(allowed["allowed"])
        self.assertFalse(allowed["mode_grants_execution_authority"])

    def test_experiment_tree_preserves_all_branches_and_score_is_scheduling_only(self) -> None:
        tree = build_experiment_tree([
            {"experiment_id": "E0", "phase": "smoke", "status": "PASS", "scheduling_score": 1.0},
            {"experiment_id": "E1", "parent_experiment_id": "E0", "phase": "pilot", "status": "NEGATIVE", "scheduling_score": 0.1},
            {"experiment_id": "E2", "parent_experiment_id": "E0", "phase": "pilot", "status": "POSITIVE", "scheduling_score": 0.9},
        ])
        self.assertEqual(tree["status"], "EXPERIMENT_TREE_VALID")
        self.assertEqual(len(tree["nodes"]), 3)
        self.assertTrue(tree["selection_score_is_scheduling_only"])
        self.assertTrue(tree["completed_results_remain_visible"])
        self.assertTrue(all(row["evidence_selected_by_score"] is False for row in tree["nodes"]))

    def test_artifact_inspector_is_read_only_content_addressed_and_blocks_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); path = root / "a.txt"; path.write_text("evidence", encoding="utf-8")
            sha = hashlib.sha256(b"evidence").hexdigest()
            ok = inspect_artifact(root, "a.txt", expected_sha256=sha)
            bad = inspect_artifact(root, "../outside.txt")
        self.assertEqual(ok["status"], "PASS")
        self.assertTrue(ok["read_only"])
        self.assertEqual(bad["status"], "BLOCK")
        self.assertIn("path-traversal-forbidden", bad["blockers"])

    def test_control_plane_aggregates_but_does_not_authorize(self) -> None:
        state = build_research_control_plane_state(
            research_execution_kernel={"status": "KERNEL_CONTRACTS_INSTALLED"},
            research_reasoning_layer={"status": "REASONING_CONTRACTS_INSTALLED"},
            feynman_socratic_gate={"status": "Feynman_Socratic_GATE_INSTALLED"},
            reproduction_gate={"status": "REPRODUCTION_GATE_INSTALLED"},
            review_control={"status": "REVIEW_CONTROL_STATE_COMPILED", "summary": {"papers": 5}},
            figure_claim_graph={"status": "PASS_FIGURE_CLAIM_GRAPH"},
            experiment_nodes=[], research_states=[],
            governance_state={"runtime": {"active_gpu_leases": 2}},
            paper_registry_summary={"papers": 5, "submission_ready": 5},
        )
        self.assertEqual(state["status"], "CONTROL_PLANE_READY")
        self.assertEqual(state["summary"]["component_checks_passed"], state["summary"]["component_checks_total"])
        self.assertEqual(state["summary"]["active_research_states"], 0)
        self.assertEqual(state["resource_snapshot"]["active_gpu_leases"], 2)
        self.assertFalse(state["resource_snapshot"]["control_plane_can_grant_gpu"])
        self.assertEqual(state["summary"]["automatic_scientific_authority"], 0)


if __name__ == "__main__":
    unittest.main()
