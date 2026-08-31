from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
R2 = GENERATED / "agent-constraint-externality-pre-f0-redteam-r2-20260831.json"
BASE = GENERATED / "agent-constraint-externality-pre-f0-20260831.json"
MANIFEST = GENERATED / "agent-constraint-externality-manifest-r2-20260831.json"
OBJECT_ID = "AGENT-CONSTRAINT-EXTERNALITY-20260831"
LIVE_START = "4da10aa7a8d2c2acdd0a8fbe2bbca6e48ff7d83b"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class AgentConstraintExternalityRedTeamR2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.r2 = load(R2)
        self.base = load(BASE)
        self.manifest = load(MANIFEST)

    def test_object_gate_and_zero_authority_are_preserved(self) -> None:
        self.assertEqual(self.r2["object_id"], OBJECT_ID)
        self.assertEqual(self.r2["live_canonical_sha_at_start"], LIVE_START)
        self.assertEqual(self.r2["retained_gate"], "PRE_F0_AGENT_CHILD_PASS_PROPOSAL_ONLY")
        self.assertEqual(self.r2["verdict"], "PRE_F0_AGENT_CHILD_PASS_PROPOSAL_ONLY")
        self.assertEqual(self.r2["scientific_outcomes_observed"], 0)
        self.assertFalse(any(self.r2["authority"].values()))
        self.assertEqual(self.base["status"], "PRE_F0_AGENT_CHILD_PASS_PROPOSAL_ONLY")
        self.assertFalse(any(self.base["authority"].values()))

    def test_recap_forces_stronger_novelty_narrowing(self) -> None:
        rows = {row["work"]: row for row in self.r2["external_novelty_redteam"]}
        recap = rows["RECAP: Regression Evaluation for Continual Adaptation of Prompts"]
        self.assertEqual(recap["collision"], "NEAR_DIRECT_EVALUATION_CONSTRUCT_COLLISION")
        self.assertIn("collateral damage", recap["already_covers"])
        self.assertIn("stateful", recap["required_narrowing"])
        direct = self.r2["direct_collision_adjudication"]
        self.assertEqual(
            direct["result"],
            "NO_DIRECT_SAME_UPDATE_STATEFUL_CONSTRAINT_TOPOLOGY_COLLISION_LOCATED_IN_BOUNDED_AUDIT",
        )
        self.assertIn("constraint-level collateral damage is new", direct["forbidden_novelty_claims"])

    def test_graph_and_capability_prior_art_are_explicit(self) -> None:
        rows = {row["work"]: row for row in self.r2["external_novelty_redteam"]}
        self.assertIn(
            "Self-Evolving Agents as Dynamic Graph Transformation: A Survey and New Perspective",
            rows,
        )
        self.assertIn(
            "Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents",
            rows,
        )
        self.assertIn("not the contribution", rows[
            "Harness Updating Is Not Harness Benefit: Disentangling Evolution Capabilities in Self-Evolving LLM Agents"
        ]["required_narrowing"])

    def test_internal_graph_collisions_do_not_merge_objects(self) -> None:
        objects = {row["existing_local_object"] for row in self.r2["internal_collision_addendum"]}
        self.assertIn("feedback-to-write-coupling-topology", objects)
        self.assertIn("compositional-update-compatibility / Typed Update-Interaction Rule Registry", objects)
        self.assertIn("memory-interaction-clause-learner / B-3 interaction family", objects)

    def test_substrate_ranking_is_decisive(self) -> None:
        rank = self.r2["substrate_adjudication_r2"]
        self.assertEqual(rank["rank_1"]["name"], "AppWorld-Externality")
        self.assertEqual(rank["rank_1"]["verdict"], "PRIMARY")
        self.assertEqual(rank["rank_2"]["name"], "ToolSandbox")
        self.assertEqual(rank["rank_3"]["name"], "WorkArena++ on BrowserGym")
        self.assertEqual(rank["reference_only"]["name"], "RECAP")

    def test_identification_is_exact_update_not_fake_same_state(self) -> None:
        ident = self.r2["identification_corrections"]
        self.assertIn("EXACT_UPDATE_ARTIFACT", ident["same_update"])
        self.assertIn("not literal same full world state", ident["same_update"])
        self.assertIn("shared mutable-resource exposure count", ident["simpler_mechanism_falsifier"])
        self.assertIn("automatically generated", ident["self_evolution_definition"])

    def test_static_source_witnesses_are_content_addressed(self) -> None:
        sources = self.r2["static_source_reverification"]
        self.assertEqual(sources["AppWorld"]["repo_sha"], "a072b7a86e7c1d5b1d7175659d750ebb9b79f10a")
        self.assertEqual(sources["ToolSandbox"]["repo_sha"], "165848b9a78cead7ca7fe7c89c688b58e6501219")
        self.assertEqual(sources["WorkArena++"]["repo_sha"], "a772230a94cf1caf4166b8ead3983f3b3786455b")
        for source in sources.values():
            for witness in source["witnesses"]:
                self.assertEqual(len(witness["sha256"]), 64)

    def test_registry_is_checked_without_premature_paper_registration(self) -> None:
        reg = self.r2["registry_adjudication"]
        self.assertFalse(reg["paper_registry_direct_entry"])
        self.assertFalse(reg["research_system_exact_object_id_entry"])
        self.assertEqual(reg["decision"], "NO_REGISTRY_SCHEMA_MUTATION_AT_PRE_F0")
        self.assertEqual(reg["independent_scientific_authority_namespace"], OBJECT_ID)
        self.assertTrue(reg["collision_scan_completed"])

    def test_manifest_hashes_are_self_consistent(self) -> None:
        self.assertEqual(self.manifest["object_id"], OBJECT_ID)
        self.assertEqual(self.manifest["live_canonical_sha_at_start"], LIVE_START)
        self.assertEqual(self.manifest["scientific_outcomes_observed"], 0)
        self.assertFalse(any(self.manifest["authority"].values()))
        import hashlib
        for rel, meta in self.manifest["files"].items():
            data = (ROOT / rel).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), meta["sha256"])
            self.assertEqual(len(data), meta["bytes"])


if __name__ == "__main__":
    unittest.main()
