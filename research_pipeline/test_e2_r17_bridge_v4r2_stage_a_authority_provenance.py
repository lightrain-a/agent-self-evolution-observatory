from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.e2_r17_bridge_v4r2_stage_a_capability import CONTROL_PLANE_REVISION, PRODUCTION_PUBLIC_KEY_SHA256
from scripts.authorize_e2_r17_bridge_v4r2_stage_a import AUTH_STATUS, build_authorization
from scripts.sign_e2_r17_bridge_v4r2_stage_a_capability import build_payload


def dump(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BridgeStageAAuthorityProvenanceTests(unittest.TestCase):
    def fixture(self, root: Path):
        contract = root / "contract.json"
        preflight = root / "preflight.json"
        review = root / "review.json"
        auth = root / "auth.json"
        run_root = root / "run"
        lease = root / "lease.json"
        marker = root / "consume.json"
        contract_payload = {
            "status": "FROZEN_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_SUPPORT",
            "authority": {
                "scientific_experiment": False,
                "provider_io": False,
                "search_pool_acquisition": False,
                "support_inspection": False,
                "free_updater": False,
                "deterministic_state_materialization": False,
                "actor_evaluation": False,
                "screen_outcome_opening": False,
                "validation_opening": False,
                "analysis": False,
                "paper_promotion": False,
            },
            "control_plane_revision": CONTROL_PLANE_REVISION,
            "search": {"unit_ids": ["u1", "u2"], "task_ids": ["t1"]},
            "actor": {"required_resolved_model": "deepseek-v4-pro-ga-260813", "max_turns": 10, "max_output_tokens": 8192},
            "model_identity": {"sha256": "1" * 64},
            "initial_skill": {"sha256": "2" * 64},
            "budget": {"search_provider_call_ceiling": 3840, "per_search_unit_call_ceiling": 10},
            "run_root": str(run_root),
            "lineage_lease_path": str(lease),
            "signed_capability_control": {"consumption_marker_path": str(marker), "production_public_key_sha256": PRODUCTION_PUBLIC_KEY_SHA256},
            "bound_code": {
                "runner": {"sha256": "3" * 64},
                "runtime": {"sha256": "4" * 64},
                "support": {"sha256": "5" * 64},
            },
        }
        dump(contract, contract_payload)
        contract_sha = sha(contract)
        preflight_payload = {
            "status": "PASS_ZERO_PROVIDER_BRIDGE_V4R2_STAGE_A_CONTRACT_PREFLIGHT",
            "contract_sha256": contract_sha,
            "provider_calls": 0,
            "provider_claims": 0,
            "scientific_outcomes_read": False,
            "method_effect_read": False,
            "updater_calls": 0,
            "heldout_actor_calls": 0,
        }
        dump(preflight, preflight_payload)
        preflight_sha = sha(preflight)
        review_payload = {
            "status": "COMPLETED",
            "surface": "ChatGPT web",
            "model": "GPT-5.6 Sol",
            "verdict": "PASS_TO_SEPARATE_BRIDGE_V4R2_STAGE_A_AUTHORIZATION",
            "control_plane_revision": CONTROL_PLANE_REVISION,
            "contract_sha256_acknowledged": contract_sha,
            "preflight_sha256_acknowledged": preflight_sha,
            "scientific_authority_now": False,
            "stage_a_execution_recommendation": "ALLOW_SEPARATE_AUTHORIZATION",
            "remaining_blockers": [],
            "scientific_geometry": "PASS",
            "stage_separation": "PASS",
            "support_gate": "PASS",
            "identity_runtime_budget": "PASS",
            "exactly_once_fail_closed": "PASS",
            "causal_integrity": "PASS",
            "m3r4_dependency": "PASS",
            "r1_supersession_clean": "PASS",
            "r2_supersession_clean": "PASS",
            "authority_provenance": "PASS",
        }
        dump(review, review_payload)
        return contract, preflight, review, auth

    def test_structural_authorization_requires_exact_review_and_remains_capability_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            contract, preflight, review, _ = self.fixture(Path(td))
            auth = build_authorization(contract_path=contract, preflight_path=preflight, review_path=review)
            self.assertEqual(auth["status"], AUTH_STATUS)
            self.assertTrue(auth["authority_requires_external_signed_capability"])
            self.assertEqual(auth["production_public_key_sha256"], PRODUCTION_PUBLIC_KEY_SHA256)
            self.assertEqual(auth["independent_review"]["sha256"], sha(review))
            self.assertIn("consumption_marker_path", auth["execution_scope"])

    def test_review_with_remaining_blocker_cannot_mint_structural_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            contract, preflight, review, _ = self.fixture(Path(td))
            row = json.loads(review.read_text())
            row["remaining_blockers"] = ["forged blocker"]
            dump(review, row)
            with self.assertRaisesRegex(RuntimeError, "retains blockers"):
                build_authorization(contract_path=contract, preflight_path=preflight, review_path=review)

    def test_review_without_authority_provenance_pass_cannot_mint(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            contract, preflight, review, _ = self.fixture(Path(td))
            row = json.loads(review.read_text())
            row["authority_provenance"] = "FAIL"
            dump(review, row)
            with self.assertRaisesRegex(RuntimeError, "authority_provenance"):
                build_authorization(contract_path=contract, preflight_path=preflight, review_path=review)

    def test_signer_binds_exact_review_and_structural_authorization_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            contract, preflight, review, auth_path = self.fixture(Path(td))
            auth = build_authorization(contract_path=contract, preflight_path=preflight, review_path=review)
            dump(auth_path, auth)
            payload = build_payload(contract_path=contract, preflight_path=preflight, review_path=review, authorization_path=auth_path, capability_id="cap", issued_at_utc="2026-09-07T00:00:00Z")
            self.assertEqual(payload["contract_sha256"], sha(contract))
            self.assertEqual(payload["preflight_sha256"], sha(preflight))
            self.assertEqual(payload["review_receipt_sha256"], sha(review))
            self.assertEqual(payload["structural_authorization_sha256"], sha(auth_path))
            self.assertEqual(payload["control_plane_revision"], CONTROL_PLANE_REVISION)
            self.assertTrue(payload["single_use"])

    def test_signer_rejects_review_modified_after_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            contract, preflight, review, auth_path = self.fixture(Path(td))
            auth = build_authorization(contract_path=contract, preflight_path=preflight, review_path=review)
            dump(auth_path, auth)
            row = json.loads(review.read_text())
            row["nonblocking_note"] = "changed after structural authorization"
            dump(review, row)
            with self.assertRaisesRegex(RuntimeError, "review drift"):
                build_payload(contract_path=contract, preflight_path=preflight, review_path=review, authorization_path=auth_path)


if __name__ == "__main__":
    unittest.main()
