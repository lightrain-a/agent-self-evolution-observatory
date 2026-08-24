from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from .config import PROJECT_ROOT
from .research_control_plane import (
    build_experiment_tree,
    build_public_research_control_plane_projection,
    build_research_control_plane_state,
    evaluate_mode_action,
    inspect_artifact,
)


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
        self.assertIn("feynman_socratic_gate", state["component_snapshots"])
        self.assertIn("review_control", state["component_snapshots"])

    def test_public_projection_is_selective_and_does_not_mutate_source_snapshots(self) -> None:
        paths = [
            PROJECT_ROOT / "generated" / "research-system-state.json",
            PROJECT_ROOT / "generated" / "paper-registry.json",
            PROJECT_ROOT / "generated" / "research-governance-v2.json",
            PROJECT_ROOT / "generated" / "asset-first-stri-paper-quality-v2-20260816.json",
        ]
        before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        state = build_public_research_control_plane_projection(PROJECT_ROOT)
        after = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        self.assertEqual(before, after)
        self.assertEqual(state["status"], "CONTROL_PLANE_READY")
        self.assertTrue(state["projection_policy"]["selective_projection_only"])
        self.assertTrue(state["projection_policy"]["full_research_system_rebuild_forbidden"])
        self.assertFalse(state["scientific_authority"])
        self.assertEqual(len(state["source_artifact_sha256"]), 4)
        self.assertTrue(all(len(value) == 64 for value in state["source_artifact_sha256"].values()))
        self.assertEqual(state["component_snapshots"]["feynman_socratic_gate"]["false_reduction_alerts"], 0)
        self.assertGreaterEqual(state["component_snapshots"]["failure_differential_registry"]["historical_terminalized_labels"], 15)
        self.assertEqual(state["component_snapshots"]["failure_differential_registry"]["prospective_scored_cases"], 0)
        self.assertEqual(state["component_snapshots"]["research_skill_registry"]["skill_packs_catalogued_not_installed"], 8)
        self.assertEqual(state["component_snapshots"]["manuscript_integrity_layer"]["audit_surfaces"], 7)
        self.assertEqual(state["summary"]["catalogued_skill_packs"], 8)
        self.assertEqual(state["summary"]["post_draft_integrity_surfaces"], 7)
        self.assertFalse(state["shadow_extensions"]["shadow_extension_grants_scientific_authority"])

    def test_system_overview_loads_selective_control_plane_projection(self) -> None:
        html = (PROJECT_ROOT / "system-overview.html").read_text(encoding="utf-8")
        js = (PROJECT_ROOT / "system-overview-operations.js").read_text(encoding="utf-8")
        self.assertIn('generated/research-control-plane.js', html)
        self.assertIn('window.RESEARCH_CONTROL_PLANE || state.research_control_plane', js)
        self.assertIn('generated/research-control-plane.json/js', js)


if __name__ == "__main__":
    unittest.main()
