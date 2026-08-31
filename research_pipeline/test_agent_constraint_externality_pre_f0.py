from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
PRE_F0 = GENERATED / "agent-constraint-externality-pre-f0-20260831.json"
SUBSTRATE = GENERATED / "agent-constraint-externality-substrate-audit-20260831.json"
SOURCE = GENERATED / "agent-constraint-externality-source-audit-20260831.json"
NOVELTY = GENERATED / "agent-constraint-externality-novelty-audit-20260831.json"
BOUNDARY = GENERATED / "agent-constraint-externality-paper-boundary-contract-20260831.json"
MANIFEST = GENERATED / "agent-constraint-externality-manifest-20260831.json"
OBJECT_ID = "AGENT-CONSTRAINT-EXTERNALITY-20260831"
CANONICAL = "c8e8c24698e08ce7b25787617fdf739d2bff304e"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AgentConstraintExternalityPreF0Test(unittest.TestCase):
    def setUp(self) -> None:
        self.pre = load(PRE_F0)
        self.substrate = load(SUBSTRATE)
        self.source = load(SOURCE)
        self.novelty = load(NOVELTY)
        self.boundary = load(BOUNDARY)
        self.manifest = load(MANIFEST)

    def test_independent_object_and_proposal_only_gate(self) -> None:
        for artifact in (
            self.pre,
            self.substrate,
            self.source,
            self.novelty,
            self.boundary,
        ):
            self.assertEqual(artifact["object_id"], OBJECT_ID)
        self.assertEqual(self.pre["canonical_base_sha"], CANONICAL)
        self.assertEqual(
            self.pre["worktree_branch"],
            "research/agent-constraint-externality-20260831",
        )
        self.assertEqual(
            self.pre["status"], "PRE_F0_AGENT_CHILD_PASS_PROPOSAL_ONLY"
        )
        self.assertEqual(self.pre["scientific_object"]["claim_stage"], "HYPOTHESIS_ONLY")

    def test_all_pre_f0_gates_pass_without_authority(self) -> None:
        expected = {
            "A_INTERNAL_NOVELTY_RESIDUAL",
            "B_EXTERNAL_NOVELTY_RESIDUAL",
            "C_QUALIFIED_AGENT_SUBSTRATE",
            "D_PERSISTENT_UPDATE_IDENTIFIABLE",
            "E_CONSTRAINT_GRAPH_IDENTIFIABLE",
            "F_COLLATERAL_OUTCOME_PROGRAMMATIC",
            "G_UPDATE_TARGET_IDENTIFIABLE",
            "H_UPDATE_MAGNITUDE_CONTROL_IDENTIFIABLE",
            "I_GENERIC_FORGETTING_DISTINGUISHABLE",
            "J_CAPABILITY_MASKING_RULES_DEFINED",
            "K_DECISIVE_EXPERIMENT_IDENTIFIABLE",
            "L_3D_PAPER_BOUNDARY_PASS",
            "M_AUTHORITY_ZERO",
            "N_NO_SCIENTIFIC_OUTCOME_USED",
        }
        self.assertEqual(set(self.pre["gates"]), expected)
        self.assertTrue(all(v["status"] == "PASS" for v in self.pre["gates"].values()))
        self.assertFalse(any(self.pre["authority"].values()))
        policy = self.pre["artifact_policy"]
        self.assertEqual(policy["scientific_outcomes_observed"], 0)
        self.assertEqual(policy["scientific_provider_calls"], 0)
        self.assertEqual(policy["scientific_gpu_runs"], 0)
        self.assertTrue(policy["no_unrelated_trajectory_reuse"])
        self.assertTrue(policy["no_3d_evidence_projection"])

    def test_substrate_matrix_is_complete_and_ranked(self) -> None:
        self.assertEqual(len(self.substrate["criteria"]), 34)
        universe = set(range(1, 35))
        for row in self.substrate["matrix"]:
            strong, partial, weak = map(set, (row["strong"], row["partial"], row["weak"]))
            self.assertFalse(strong & partial)
            self.assertFalse(strong & weak)
            self.assertFalse(partial & weak)
            self.assertEqual(strong | partial | weak, universe)
        ranking = self.substrate["ranking"]
        self.assertEqual([r["rank"] for r in ranking], [1, 2, 3])
        self.assertEqual(ranking[0]["name"], "AppWorld + AppWorld-UL semantics")
        self.assertEqual(ranking[1]["name"], "ToolSandbox")
        self.assertEqual(ranking[2]["name"], "WorkArena++ on BrowserGym")
        selected = self.substrate["selected"]
        self.assertEqual(selected["name"], "AppWorld-Externality")
        self.assertEqual(selected["classification"], "BENCHMARK-DERIVED_CONTROLLED_SUBSTRATE")
        self.assertEqual(selected["leaderboard_identity"], "NOT_APPWORLD_LEADERBOARD")
        self.assertFalse(selected["persistent_update_native"])
        self.assertFalse(selected["scientific_execution_authorized"])

    def test_source_pins_and_fresh_lineage_are_explicit(self) -> None:
        sources = {row["id"]: row for row in self.source["sources"]}
        self.assertEqual(
            sources["APPWORLD-ACL24"]["repo_sha"],
            "a072b7a86e7c1d5b1d7175659d750ebb9b79f10a",
        )
        self.assertEqual(
            sources["TOOLSANDBOX-NAACL25"]["repo_sha"],
            "165848b9a78cead7ca7fe7c89c688b58e6501219",
        )
        self.assertEqual(
            sources["WORKARENA-PLUSPLUS-NIPS24"]["repo_sha"],
            "a772230a94cf1caf4166b8ead3983f3b3786455b",
        )
        tau = sources["TAU-BENCH-ICLR25-TAU3-CURRENT"]
        self.assertEqual(tau["repo_sha"], "a2c024725189473d2d7cea3a5cfdbcc67478e41f")
        self.assertEqual(tau["publication_status"], "MIXED_LINEAGE")
        self.assertIn("active successor", tau["freshness_note"])
        self.assertEqual(self.source["scientific_outcomes_observed"], 0)
        self.assertEqual(self.source["provider_calls"], 0)
        self.assertEqual(self.source["gpu_runs"], 0)

    def test_novelty_residual_is_narrow_and_collision_aware(self) -> None:
        self.assertEqual(self.novelty["internal_verdict"], "PASS_WITH_HARD_BOUNDARY")
        self.assertEqual(self.novelty["external_verdict"], "PASS_WITH_NARROWING")
        direct = self.novelty["direct_collision_search_adjudication"]
        self.assertEqual(direct["result"], "NO_DIRECT_COLLISION_LOCATED_IN_BOUNDED_AUDIT")
        self.assertIn("bounded novelty audit", direct["caveat"])
        forbidden = set(direct["forbidden_novelty_claims"])
        self.assertIn("self-evolution can be harmful", forbidden)
        self.assertIn("catastrophic forgetting occurs in agents", forbidden)
        external = {row["work"]: row for row in self.novelty["external_collision_matrix"]}
        self.assertIn("Your Agent May Misevolve: Emergent Risks in Self-evolving LLM Agents", external)
        self.assertIn("Agent-Dice: Disentangling Knowledge Updates via Geometric Consensus for Agent Continual Learning", external)
        self.assertIn("Agent Skills Can Be Harmful: An Empirical Study of Skill-Induced Failures in LLM Agents", external)

    def test_constraint_graph_is_outcome_blind_and_not_raw_count(self) -> None:
        constraint = self.pre["constructs"]["constraint"]
        edge = self.pre["constructs"]["interaction_edge"]
        self.assertTrue(constraint["outcome_blind"])
        self.assertIn("semantic task obligation", constraint["definition"])
        self.assertIn("grouped into one ConstraintSpec", constraint["definition"])
        self.assertIn("post-update co-failure", edge["forbidden_edge_sources"])
        self.assertIn("terminal outcome correlation", edge["forbidden_edge_sources"])
        self.assertEqual(
            set(edge["edge_types"]),
            {
                "SHARED_MUTABLE_STATE",
                "SHARED_STATE_CHANGING_API_RESOURCE",
                "TEMPORAL_PREREQUISITE",
                "READ_AFTER_WRITE_DEPENDENCY",
            },
        )

    def test_primary_surface_is_single_and_same_update_is_decisive(self) -> None:
        update = self.pre["constructs"]["local_benign_update"]
        self.assertEqual(update["primary_surface"], "PERSISTENT_PROCEDURAL_REPAIR_NOTE")
        self.assertIn("exact bytes reused inside same-update pairs", update["scope_controls"])
        experiment = self.pre["decisive_experiment"]
        self.assertEqual(experiment["name"], "MATCHED_LOCAL_REPAIR_EXTERNALITY")
        text = " ".join(experiment["same_update_design"])
        self.assertIn("Freeze u_r by SHA-256", text)
        self.assertIn("no-update counterfactual replay", text)
        self.assertIn("Keep all zero/negative target gains", text)
        controls = set(experiment["required_controls"])
        self.assertIn("same candidate update within paired family", controls)
        self.assertIn("same constraint count", controls)
        self.assertIn("outcome-blind topology assignment", controls)

    def test_metrics_separate_target_gain_collateral_and_spontaneous_drift(self) -> None:
        metrics = self.pre["metrics"]
        self.assertIn("no-update counterfactual replay", metrics["target_repair_gain"])
        self.assertIn("S_i", metrics["collateral_regression_rate"])
        self.assertIn("CRR_i - CRR0_i", metrics["spontaneous_regression_control"])
        self.assertEqual(metrics["global_task_success"], "SECONDARY_ONLY")
        self.assertTrue(metrics["per_case_per_constraint_required"])

    def test_hypotheses_and_falsifier_include_alternatives(self) -> None:
        hypotheses = {row["id"]: row for row in self.pre["competing_hypotheses"]}
        self.assertEqual(set(hypotheses), {"H1", "H2", "H3", "H4", "H5", "H6"})
        self.assertEqual(hypotheses["H5"]["name"], "CONSTRAINT_COUPLING_EXTERNALITY")
        falsifiers = " ".join(self.pre["falsification"]["H5_clear_falsifiers"])
        self.assertIn("shared mutable-resource exposure", falsifiers)
        self.assertIn("beta_coupling is null", falsifiers)
        self.assertIn("Do not create Coupling-Aware Update Scoping", self.pre["falsification"]["if_H5_fails"])

    def test_3d_boundary_is_hard_and_authority_namespaces_do_not_merge(self) -> None:
        self.assertEqual(self.boundary["boundary_status"], "PASS")
        self.assertEqual(self.boundary["agent_object"], "SELF_UPDATE_TO_BEHAVIORAL_EXTERNALITY")
        self.assertEqual(self.boundary["three_d_object"], "RELATIONAL_COMPLEXITY_TO_GENERATION_FAILURE")
        self.assertFalse(self.boundary["shared_scientific_authority"])
        self.assertEqual(self.boundary["authority_namespace"], OBJECT_ID)
        self.assertIn("3D-FRONT", self.boundary["forbidden_as_agent_core"])
        self.assertIn("principal claim", self.boundary["must_not_share"])
        self.assertEqual(
            self.boundary["only_allowed_high_level_intuition"],
            "raw count may not equal effective structural complexity",
        )

    def test_manifest_content_addresses_all_primary_artifacts(self) -> None:
        files = self.manifest["files"]
        for rel in (
            "generated/agent-constraint-externality-pre-f0-20260831.json",
            "generated/agent-constraint-externality-substrate-audit-20260831.json",
            "generated/agent-constraint-externality-source-audit-20260831.json",
            "generated/agent-constraint-externality-novelty-audit-20260831.json",
            "generated/agent-constraint-externality-paper-boundary-contract-20260831.json",
        ):
            self.assertIn(rel, files)
            self.assertEqual(files[rel]["sha256"], sha256(ROOT / rel))
        self.assertEqual(self.manifest["scientific_outcomes_observed"], 0)
        self.assertFalse(any(self.manifest["authority"].values()))


if __name__ == "__main__":
    unittest.main()
