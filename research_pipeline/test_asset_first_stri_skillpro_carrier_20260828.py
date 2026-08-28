from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class STRISkillProCarrierArtifactsTest(unittest.TestCase):
    def test_qualification_binds_p0_receipts_and_keeps_claims_closed(self) -> None:
        qualification = json.loads(
            (GENERATED / "asset-first-stri-skillpro-carrier-qualification-20260828.json").read_text(encoding="utf-8")
        )
        p0 = GENERATED / "asset-first-stri-skillpro-p0-projection-result-20260828.json"
        p0b = GENERATED / "asset-first-stri-skillpro-author-p0b-result-20260828.json"
        self.assertEqual(qualification["p0_evidence"]["independent_projection"]["sha256"], sha256(p0))
        self.assertEqual(qualification["p0_evidence"]["author_scheduler_probe"]["sha256"], sha256(p0b))
        self.assertEqual(
            qualification["decision"],
            "QUALIFY_SKILLPRO_AS_PRIMARY_RECENT_FLAGSHIP_CARRIER_FOR_P1_P2_DESIGN",
        )
        boundary = qualification["scientific_boundary"]
        self.assertFalse(boundary["claim_expansion"])
        self.assertFalse(boundary["behavioral_claim_authorized"])
        self.assertFalse(boundary["manuscript_primary_carrier_replacement_authorized"])
        self.assertFalse(boundary["p1_model_execution_authorized_by_this_receipt"])

    def test_p1_p2_contract_is_outcome_blind_and_has_no_execution_authority(self) -> None:
        contract = json.loads(
            (GENERATED / "asset-first-stri-skillpro-p1-p2-contract-20260828.json").read_text(encoding="utf-8")
        )
        focal = contract["p1a_real_evidence_collection"]["focal_seed_skill_selection"]
        self.assertEqual(focal["selected"], "HypothesisElimination")
        self.assertEqual(
            focal["selected_name_sha256"],
            hashlib.sha256(b"HypothesisElimination").hexdigest(),
        )
        arms = [row["name"] for row in contract["p1b_identity_attribution_intervention"]["arms"]]
        self.assertEqual(
            arms,
            ["A_canonical", "B_id_placebo", "C_exact_split", "D_pre_gate_quotient", "E_late_identity_dedup"],
        )
        boundary = contract["scientific_boundary"]
        self.assertFalse(boundary["model_call_authority"])
        self.assertFalse(boundary["gpu_authority"])
        self.assertFalse(boundary["p1_execution_authority"])
        self.assertFalse(boundary["p2_execution_authority"])
        self.assertFalse(boundary["claim_expansion"])

    def test_p0_and_p0b_results_pass_without_behavioral_claims(self) -> None:
        for filename in (
            "asset-first-stri-skillpro-p0-projection-result-20260828.json",
            "asset-first-stri-skillpro-author-p0b-result-20260828.json",
        ):
            result = json.loads((GENERATED / filename).read_text(encoding="utf-8"))
            self.assertTrue(result["all_checks_pass"], filename)
            boundary = result["scientific_boundary"]
            self.assertFalse(boundary["claim_expansion"], filename)
            self.assertFalse(boundary.get("downstream_behavior_claim", boundary.get("behavioral_claim_authorized", False)), filename)
            self.assertEqual(boundary["new_model_calls"], 0, filename)
            self.assertEqual(boundary["new_gpu_runs"], 0, filename)

    def test_runtime_preflight_blocks_model_execution_until_environment_is_qualified(self) -> None:
        preflight = json.loads(
            (GENERATED / "asset-first-stri-skillpro-p1-runtime-preflight-20260828.json").read_text(encoding="utf-8")
        )
        self.assertEqual(preflight["decision"], "P1_MODEL_EXECUTION_BLOCKED_RUNTIME_NOT_QUALIFIED")
        self.assertFalse(preflight["execution_integrity"]["full_author_run_import_ready"])
        self.assertIn("textarena", preflight["best_existing_python_base"]["missing"])
        self.assertEqual(preflight["backend_preflight"]["local_backend"]["released_LocalLLM_vllm_tensor_parallel_size"], 4)
        boundary = preflight["scientific_boundary"]
        self.assertFalse(boundary["p1_execution_authority"])
        self.assertFalse(boundary["runtime_install_authority"])
        self.assertEqual(boundary["new_model_calls"], 0)
        self.assertEqual(boundary["new_gpu_runs"], 0)

    def test_ace_preaudit_is_candidate_only_until_commit_and_operator_are_pinned(self) -> None:
        audit = json.loads(
            (GENERATED / "asset-first-stri-ace-precarrier-audit-20260828.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            audit["decision"],
            "QUALIFY_ACE_AS_SECONDARY_POSITIVE_CONTROL_CANDIDATE_PENDING_PIN_AND_OPERATOR_AUDIT",
        )
        boundary = audit["scientific_boundary"]
        self.assertFalse(boundary["source_pin_complete"])
        self.assertFalse(boundary["ace_experiment_authority"])
        self.assertFalse(boundary["cross_system_generality_authorized"])
        self.assertEqual(boundary["new_model_calls"], 0)
        self.assertEqual(boundary["new_gpu_runs"], 0)


if __name__ == "__main__":
    unittest.main()
