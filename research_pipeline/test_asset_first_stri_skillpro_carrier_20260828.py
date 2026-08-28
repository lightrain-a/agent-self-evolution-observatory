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


if __name__ == "__main__":
    unittest.main()
