from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "generated" / "relational-constraint-capacity-pre-f0-20260830.json"
PORT_PLAN = ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"
EXPECTED_SHA256 = "7fedadef0553f2b564e4d7b12ab75666134a356be2ba51e4c16a259f5efcdc5a"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RelationalConstraintCapacityPreF0Test(unittest.TestCase):
    def setUp(self) -> None:
        self.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.port_plan = json.loads(PORT_PLAN.read_text(encoding="utf-8"))

    def test_artifact_is_content_addressed_and_independent(self) -> None:
        self.assertEqual(sha256_file(ARTIFACT), EXPECTED_SHA256)
        self.assertEqual(
            self.artifact["object_id"],
            "RELATIONAL-CONSTRAINT-CAPACITY-20260830",
        )
        self.assertIsNone(self.artifact["canonical_candidate_id"])
        self.assertEqual(
            self.artifact["status"],
            "PRE_F0_HOLD_ASSET_AND_CONSTRUCT_QUALIFICATION",
        )
        scope = self.artifact["scientific_object"]["scope_boundary"]
        self.assertIn("independent scientific object", scope)
        self.assertIn("not VWE reproduction", scope)
        self.assertIn("reopen PORT-010", scope)

    def test_port010_remains_exact_hold(self) -> None:
        rows = [
            row
            for row in self.port_plan.get("entries") or []
            if row.get("candidate_id") == "PORT-010"
            and row.get("title")
            == "Complex-description boundary in end-to-end 3D world construction"
        ]
        self.assertEqual(len(rows), 1)
        current = rows[0]
        snapshot = self.artifact["relation_to_port010"]["snapshot"]
        self.assertEqual(current["status"], "HOLD_EVIDENCE_REVIEW_BLOCKED")
        self.assertEqual(current["evidence_review"]["verdict"], "BLOCK_BAKE_IN")
        self.assertEqual(snapshot["status"], current["status"])
        self.assertEqual(snapshot["evidence_review"], "BLOCK_BAKE_IN")
        self.assertEqual(
            snapshot["required_reopen_components"],
            ["query_units", "per_case_outcomes"],
        )
        self.assertEqual(snapshot["materialized_reopen_components"], ["query_units"])
        self.assertEqual(
            snapshot["remaining_reopen_components"],
            ["per_case_outcomes"],
        )
        self.assertFalse(snapshot["offline_replay_tier_authorized"])
        self.assertFalse(snapshot["provider_authority"])
        self.assertFalse(snapshot["gpu_authority"])
        self.assertFalse(snapshot["scientific_execution_authority"])
        self.assertFalse(snapshot["changed_by_this_object"])

    def test_publication_and_source_pins_are_frozen(self) -> None:
        audit = self.artifact["source_and_publication_audit"]
        methods = {row["name"]: row for row in audit["methods"]}
        self.assertEqual(set(methods), {"ATISS", "DiffuScene", "InstructScene"})
        self.assertEqual(methods["ATISS"]["venue"], "NeurIPS 2021")
        self.assertEqual(
            methods["ATISS"]["repository_commit"],
            "0909ce0000e52bf1bf300a6a558109f7f8383fd9",
        )
        self.assertEqual(methods["DiffuScene"]["venue"], "CVPR 2024")
        self.assertEqual(
            methods["DiffuScene"]["repository_commit"],
            "d78a2890c6b806b61279463b1dbe7701f286a024",
        )
        self.assertEqual(methods["InstructScene"]["venue"], "ICLR 2024 Spotlight")
        self.assertEqual(
            methods["InstructScene"]["repository_commit"],
            "a9097a62c484c56ac7be5ec2928ef497cbbaaf24",
        )
        self.assertTrue(all(row["publication_qualified"] for row in methods.values()))
        self.assertFalse(methods["ATISS"]["free_form_relational_instruction_same_access"])
        self.assertFalse(
            methods["DiffuScene"]["free_form_relational_instruction_same_access"]
        )
        release = audit["instructscene_release"]
        self.assertEqual(
            release["huggingface_revision"],
            "c8cf0bd282699d56a7940ac588ea5e961b1260cb",
        )
        self.assertTrue(release["official_fvqvae_weights_declared"])
        self.assertFalse(release["official_end_to_end_two_stage_checkpoint_declared"])
        self.assertTrue(release["third_party_unofficial_two_stage_checkpoints_declared"])
        self.assertFalse(
            release["third_party_checkpoint_is_official_reproduction_evidence"]
        )

    def test_construct_and_intervention_are_fail_closed(self) -> None:
        construct = self.artifact["construct_contract"]
        self.assertEqual(construct["primary_dose"], "relation_count = |R|")
        self.assertIn("official iRecall", construct["primary_endpoint"])
        self.assertIn("linear", construct["model_comparison"])
        self.assertIn("segmented/change-point", construct["model_comparison"])
        self.assertIn("smooth capacity degradation", construct["smooth_decline_policy"])

        risks = {
            row["risk"]: row for row in self.artifact["known_identifiability_risks"]
        }
        self.assertEqual(
            set(risks),
            {
                "COUNT_LENGTH_AND_AUTHORED_DIFFICULTY_CONFOUND",
                "SAME_ACCESS_BASELINE_GAP",
                "INTERVENTION_NOT_IDENTIFIED",
                "NOVELTY_COLLISION",
            },
        )
        self.assertIn("rho=0.939932", risks["COUNT_LENGTH_AND_AUTHORED_DIFFICULTY_CONFOUND"]["evidence"])
        self.assertIn(
            "oracle structured-access intervention",
            risks["INTERVENTION_NOT_IDENTIFIED"]["evidence"],
        )

    def test_p0_through_p3_have_zero_execution_and_authority(self) -> None:
        gates = self.artifact["gates"]
        self.assertEqual(
            gates["P0"]["status"],
            "HOLD_ASSET_AND_CHECKPOINT_QUALIFICATION",
        )
        self.assertEqual(gates["P0"]["executed_cases"], 0)
        self.assertEqual(gates["P0"]["verdict"], "NOT_RUN_NO_SCIENTIFIC_RESULT")
        self.assertIn("NOT_AUTHORIZED", gates["P1"]["status"])
        self.assertEqual(gates["P1"]["executed_cases"], 0)
        self.assertEqual(gates["P2"]["status"], "NOT_AUTHORIZED")
        self.assertEqual(gates["P3"]["status"], "NOT_AUTHORIZED")

        self.assertFalse(any(self.artifact["authority"].values()))
        self.assertFalse(self.artifact["scientific_authority"])
        self.assertFalse(self.artifact["execution_authority"])
        policy = self.artifact["artifact_policy"]
        self.assertTrue(policy["no_outcomes_read_in_this_pre_f0"])
        self.assertEqual(policy["provider_calls_executed"], 0)
        self.assertEqual(policy["gpu_calls_executed"], 0)

    def test_failure_is_not_misclassified_as_mechanism_failure(self) -> None:
        differential = self.artifact["failure_differential"]
        self.assertTrue(differential["not_a_mechanism_failure"])
        self.assertIn(
            "EXECUTION_FAILURE_ASSET_NOT_MATERIALIZED",
            differential["current_classification"],
        )
        self.assertIn(
            "FORMULATION_HOLD_RELATION_COUNT_IDENTIFIABILITY",
            differential["current_classification"],
        )
        self.assertIn(
            "neither supported nor falsified",
            differential["scientific_belief_update"],
        )


if __name__ == "__main__":
    unittest.main()
