from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "generated"
    / "relational-constraint-capacity-pre-f0-adjudication-20260830.json"
)
CONSTRUCT = (
    ROOT / "generated" / "relational-constraint-capacity-construct-v2-20260830.json"
)
PORT_PLAN = ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"
SMOKE_RUNNER = ROOT / "scripts" / "run_instructscene_non_scientific_execution_smoke.py"
EXPECTED_ARTIFACT_SHA256 = "cfc91edee5e6315f2e765628316a6ffa61f2521da4c5cfb557dd5c5b8edad92b"
EXPECTED_SMOKE_RUNNER_SHA256 = "fe9978ada3504f81793cfb4fab23215846dbe0037fc89055deb3478277f82511"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RelationalConstraintCapacityPreF0AdjudicationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.construct = json.loads(CONSTRUCT.read_text(encoding="utf-8"))

    def test_artifact_is_content_addressed_and_remains_pre_f0(self) -> None:
        self.assertEqual(sha256_file(ARTIFACT), EXPECTED_ARTIFACT_SHA256)
        self.assertEqual(
            self.artifact["object_id"], "RELATIONAL-CONSTRAINT-CAPACITY-20260830"
        )
        self.assertIsNone(self.artifact["canonical_candidate_id"])
        self.assertEqual(self.artifact["lifecycle_phase"], "PRE_F0")
        self.assertEqual(
            self.artifact["status"],
            "PRE_F0_DUAL_QUALIFICATION_PASS_PROPOSAL_ONLY",
        )
        self.assertFalse(self.artifact["scientific_authority"])
        self.assertFalse(self.artifact["execution_authority"])

    def test_dual_key_passes_but_only_opens_proposal(self) -> None:
        gate = self.artifact["dual_key_adjudication"]
        self.assertEqual(gate["construct_qualification_v2"]["verdict"], "PASS")
        self.assertEqual(
            gate["non_scientific_execution_smoke"]["verdict"], "PASS"
        )
        self.assertEqual(
            gate["non_scientific_execution_smoke"]["case_count"], 5
        )
        self.assertEqual(set(gate["non_scientific_execution_smoke"]["components"].values()), {"PASS"})
        self.assertEqual(
            gate["non_scientific_execution_smoke"]["invocation_history"],
            [
                {"processed_cases": 5, "resume_skipped_cases": 0},
                {"processed_cases": 0, "resume_skipped_cases": 5},
            ],
        )
        self.assertTrue(gate["both_pass"])
        self.assertEqual(gate["gate_effect"], "OPEN_FOR_PRE_F0_PROPOSAL_ONLY")
        self.assertTrue(gate["does_not_grant_authority"])

    def test_unofficial_checkpoint_smoke_cannot_enter_p1(self) -> None:
        smoke = self.artifact["dual_key_adjudication"][
            "non_scientific_execution_smoke"
        ]
        self.assertFalse(smoke["scientific_evidence_eligible"])
        self.assertTrue(smoke["p1_projection_forbidden"])
        self.assertFalse(smoke["official_reproduction_evidence"])
        self.assertEqual(smoke["scientific_metrics_exported"], [])
        self.assertEqual(smoke["data_archives_downloaded_or_used"], [])

        firewall = self.artifact["scientific_evidence_firewall"]
        self.assertEqual(firewall["p1_evidence_inputs"], [])
        self.assertEqual(firewall["smoke_case_outcomes_projected_to_p1"], 0)
        self.assertEqual(firewall["smoke_metrics_projected_to_p1"], [])
        self.assertEqual(firewall["scientific_belief_update_from_smoke"], "NONE")
        self.assertIn("execution plumbing only", firewall["unofficial_checkpoint_role"])
        self.assertEqual(
            sha256_file(SMOKE_RUNNER), EXPECTED_SMOKE_RUNNER_SHA256
        )

    def test_construct_v2_endpoint_and_factorial_freeze_survive(self) -> None:
        qualification = self.construct["construct_qualification_v2"]
        self.assertEqual(qualification["verdict"], "PASS")
        endpoints = qualification["endpoint_freeze"]
        self.assertEqual(endpoints["primary"]["name"], "relation_level_iRecall")
        self.assertEqual(endpoints["secondary"]["name"], "exact_all_success")
        self.assertTrue(endpoints["hierarchy_change_after_outcomes_forbidden"])
        factorial = qualification["length_disentanglement"]["factorial_audit"]
        self.assertTrue(factorial["complete_factorial"])
        self.assertTrue(factorial["equal_replication"])
        self.assertEqual(
            factorial["pearson_relation_count_vs_target_tokens"], 0.0
        )
        self.assertTrue(
            qualification["relation_type_balanced_nested_permutations"][
                "balance_audit"
            ]["pass"]
        )
        formula = qualification["analysis_preregistration"]["primary_model"][
            "formula"
        ]
        self.assertIn("relation_count_c * clip_token_count_c", formula)
        self.assertIn("(1 + relation_count_c | base_scene_id)", formula)

    def test_license_and_gpu_are_proposed_not_granted(self) -> None:
        proposal = self.artifact["pre_f0_next_authority_proposal"]
        self.assertEqual(
            proposal["status"],
            "PROPOSED_AWAITS_EXPLICIT_HUMAN_CONFIRMATION_AND_GRANT",
        )
        self.assertFalse(proposal["proposal_is_authority"])
        license_row = proposal["data_license_confirmation"]
        self.assertEqual(license_row["current_state"], "NOT_CONFIRMED")
        self.assertEqual(
            license_row["data_materialization_before_confirmation"], "FORBIDDEN"
        )
        gpu = proposal["official_two_stage_training_gpu_authority"]
        self.assertEqual(gpu["current_state"], "NOT_GRANTED")
        self.assertFalse(gpu["can_start_now"])
        self.assertEqual(len(gpu["stages"]), 2)
        self.assertIn("2-6 GPU-days", gpu["proposed_budget"])

        self.assertFalse(any(self.artifact["authority"].values()))
        gates = self.artifact["gates"]
        self.assertEqual(
            gates["data_license_confirmation"],
            "AWAITING_EXPLICIT_CONFIRMATION",
        )
        self.assertEqual(
            gates["official_two_stage_training_gpu_authority"],
            "PROPOSED_NOT_GRANTED",
        )
        self.assertEqual(gates["official_checkpoint_qualification"], "NOT_RUN")
        self.assertEqual(gates["P1"], "NOT_AUTHORIZED")
        self.assertEqual(gates["P2"], "NOT_AUTHORIZED")
        self.assertEqual(gates["P3"], "NOT_AUTHORIZED")

    def test_port010_remains_bytewise_semantically_unchanged(self) -> None:
        plan = json.loads(PORT_PLAN.read_text(encoding="utf-8"))
        rows = [
            row
            for row in plan.get("entries") or []
            if row.get("candidate_id") == "PORT-010"
            and row.get("title")
            == "Complex-description boundary in end-to-end 3D world construction"
        ]
        self.assertEqual(len(rows), 1)
        current = rows[0]
        snapshot = self.artifact["relation_to_port010"]
        self.assertEqual(current["status"], "HOLD_EVIDENCE_REVIEW_BLOCKED")
        self.assertEqual(current["evidence_review"]["verdict"], "BLOCK_BAKE_IN")
        self.assertEqual(snapshot["status"], current["status"])
        self.assertEqual(snapshot["evidence_review"], "BLOCK_BAKE_IN")
        self.assertEqual(
            snapshot["required_reopen_components"],
            ["query_units", "per_case_outcomes"],
        )
        self.assertEqual(snapshot["materialized_reopen_components"], ["query_units"])
        self.assertEqual(snapshot["remaining_reopen_components"], ["per_case_outcomes"])
        for key in (
            "offline_replay_tier_authorized",
            "provider_authority",
            "gpu_authority",
            "scientific_execution_authority",
        ):
            self.assertFalse(snapshot[key])
        self.assertFalse(snapshot["changed_by_this_object"])


if __name__ == "__main__":
    unittest.main()
