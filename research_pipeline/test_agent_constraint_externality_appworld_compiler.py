from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OBJECT_ID = "AGENT-CONSTRAINT-EXTERNALITY-20260831"
APPWORLD_SHA = "a072b7a86e7c1d5b1d7175659d750ebb9b79f10a"

PATHS = {
    "contract": GENERATED / "agent-constraint-externality-appworld-compiler-contract-20260831.json",
    "schema": GENERATED / "agent-constraint-externality-constraint-schema-20260831.json",
    "graph": GENERATED / "agent-constraint-externality-resource-graph-schema-20260831.json",
    "families": GENERATED / "agent-constraint-externality-matched-family-manifest-20260831.json",
    "diff": GENERATED / "agent-constraint-externality-topology-arm-diff-20260831.json",
    "source": GENERATED / "agent-constraint-externality-appworld-source-manifest-20260831.json",
    "qualification": GENERATED / "agent-constraint-externality-appworld-compiler-qualification-20260831.json",
    "manifest": GENERATED / "agent-constraint-externality-appworld-compiler-manifest-20260831.json",
    "bundle": GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AppWorldConstraintCompilerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data = {
            key: load(path)
            for key, path in PATHS.items()
            if key != "bundle"
        }

    def test_object_identity_and_static_authority_boundary(self) -> None:
        for payload in self.data.values():
            self.assertEqual(payload["object_id"], OBJECT_ID)
        contract = self.data["contract"]
        self.assertEqual(contract["stage"], "PRE_F0_5_STATIC_COMPILER")
        self.assertFalse(contract["outcome_read_authority"])
        self.assertFalse(contract["provider_authority"])
        self.assertFalse(contract["gpu_authority"])
        self.assertFalse(contract["scientific_episode_authority"])
        self.assertEqual(
            contract["primary_update_surface"],
            "PERSISTENT_PROCEDURAL_REPAIR_NOTE",
        )
        self.assertEqual(
            contract["structural_context_intervention"],
            "AGENT_VISIBLE_MATCHED_NON_TARGET_OBLIGATION_BINDING",
        )
        self.assertTrue(contract["evaluator_only_topology_change_forbidden"])
        self.assertEqual(
            contract["instruction_matching"],
            ["UTF8_BYTE_LENGTH", "WHITESPACE_WORD_COUNT"],
        )

    def test_constraint_schema_is_semantic_not_raw_assertion_count(self) -> None:
        schema = self.data["schema"]
        self.assertFalse(schema["raw_assertion_is_scientific_constraint"])
        self.assertTrue(schema["outcome_blind"])
        self.assertIn("semantic_description", schema["required_fields"])
        self.assertIn("evaluator_binding", schema["required_fields"])
        self.assertIn("affected_entities", schema["required_fields"])
        self.assertIn("prerequisite_resources", schema["required_fields"])

    def test_graph_uses_only_predeclared_structural_edges(self) -> None:
        graph = self.data["graph"]
        self.assertTrue(graph["outcome_blind"])
        self.assertTrue(graph["edge_witness_required"])
        self.assertEqual(graph["motif_status"], "SECONDARY_SUMMARY_ONLY")
        self.assertEqual(
            set(graph["edge_types"]),
            {
                "SHARED_MUTABLE_STATE",
                "SHARED_STATE_CHANGING_API_RESOURCE",
                "READ_AFTER_WRITE_DEPENDENCY",
                "PREREQUISITE_DEPENDENCY",
                "TEMPORAL_DEPENDENCY",
            },
        )
        forbidden = set(self.data["contract"]["forbidden_edge_sources"])
        self.assertIn("observed_co_failure", forbidden)
        self.assertIn("observed_regression", forbidden)
        self.assertIn("llm_semantic_relatedness", forbidden)

    def test_twelve_three_level_matched_families_qualify(self) -> None:
        families = self.data["families"]
        self.assertEqual(families["family_count"], 12)
        rows = families["families"]
        self.assertEqual(
            {row["category"] for row in rows},
            {"FILE_GMAIL", "TODO_NOTE_FILE"},
        )
        self.assertEqual(
            sum(row["category"] == "FILE_GMAIL" for row in rows), 6
        )
        self.assertEqual(
            sum(row["category"] == "TODO_NOTE_FILE" for row in rows), 6
        )
        for row in rows:
            self.assertEqual(row["arm_count"], 3)
            self.assertEqual(row["constraint_count"], 3)
            self.assertEqual(
                row["shared_resource_exposure"],
                {"INDEPENDENT": 0, "LOW": 1, "HIGH": 2},
            )
            self.assertTrue(row["initial_non_target_constraints_satisfied"])
            self.assertEqual(len(row["target_instruction_sha256"]), 64)
            arm_instruction_hashes = row["arm_instruction_sha256_by_arm"]
            self.assertEqual(len(arm_instruction_hashes), 3)
            self.assertEqual(len(set(arm_instruction_hashes.values())), 3)
            self.assertTrue(all(len(value) == 64 for value in arm_instruction_hashes.values()))
            self.assertGreater(row["instruction_byte_length"], 0)
            self.assertGreater(row["instruction_word_count"], 0)
            self.assertEqual(len(row["target_semantics_sha256"]), 64)
            self.assertEqual(len(row["target_resource_footprint_sha256"]), 64)
            self.assertEqual(len(row["update_interface_sha256"]), 64)
            self.assertEqual(len(row["initial_snapshot_sha256"]), 64)
            self.assertTrue(row["residual_confounds"])

    def test_topology_diff_never_claims_fake_same_base_state(self) -> None:
        diff = self.data["diff"]
        self.assertEqual(diff["comparison_count"], 36)
        self.assertEqual(
            diff["forbidden_claim"], "SAME_BASE_STATE_ACROSS_TOPOLOGY_ARMS"
        )
        self.assertEqual(
            diff["allowed_claim"],
            "EXACT_SAME_UPDATE_ARTIFACT_PLUS_MATCHED_TOPOLOGY_CONTEXT",
        )
        for row in diff["comparisons"]:
            self.assertIn(
                "target_resource_footprint", row["target_invariant_fields"]
            )
            self.assertIn(
                "persistent_update_interface", row["target_invariant_fields"]
            )
            self.assertTrue(row["residual_confounds"])

    def test_source_revision_and_protected_redistribution_boundary(self) -> None:
        source = self.data["source"]
        self.assertEqual(source["appworld_repo_sha"], APPWORLD_SHA)
        self.assertEqual(
            set(source["base_db_sha256"]),
            {"file_system", "gmail", "todoist", "simple_note"},
        )
        self.assertEqual(len(source["protected_bundle_sha256"]), 4)
        self.assertIn("remain encrypted", source["public_redistribution_boundary"])
        protected = source["protected_compiler_bundle"]
        self.assertEqual(protected["sha256"], sha256(PATHS["bundle"]))
        self.assertEqual(
            protected["path"],
            "generated/agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle",
        )

    def test_qualification_pass_has_zero_scientific_outcomes(self) -> None:
        qualification = self.data["qualification"]
        self.assertEqual(qualification["verdict"], "PRE_F0_5_PASS")
        self.assertEqual(qualification["family_count"], 12)
        self.assertEqual(
            qualification["category_counts"],
            {"FILE_GMAIL": 6, "TODO_NOTE_FILE": 6},
        )
        self.assertTrue(all(qualification["pass_conditions"].values()))
        self.assertTrue(
            qualification["pass_conditions"]["agent_visible_structural_context"]
        )
        self.assertEqual(qualification["scientific_outcomes_observed"], 0)
        self.assertEqual(qualification["provider_calls"], 0)
        self.assertEqual(qualification["gpu_runs"], 0)
        self.assertTrue(qualification["f0_authority_opened"])

    def test_content_addressed_manifest_is_self_consistent(self) -> None:
        manifest = self.data["manifest"]
        self.assertEqual(manifest["verdict"], "PRE_F0_5_PASS")
        self.assertFalse(manifest["authority"]["provider"])
        self.assertFalse(manifest["authority"]["gpu"])
        self.assertTrue(manifest["authority"]["f0"])
        self.assertFalse(manifest["authority"]["p1"])
        for relative, metadata in manifest["files"].items():
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(sha256(path), metadata["sha256"])
            self.assertEqual(path.stat().st_size, metadata["bytes"])

    def test_public_jsons_contain_no_scientific_effect_fields(self) -> None:
        forbidden = {
            "collateral_regression", "crr_update", "crr_no_update",
            "update_attributable_externality", "target_repair_gain",
            "effect_estimate", "observed_model_outcome",
        }
        for key, payload in self.data.items():
            text = json.dumps(payload, sort_keys=True).lower()
            for field in forbidden:
                self.assertNotIn(field, text, f"{field} leaked into {key}")


if __name__ == "__main__":
    unittest.main()
