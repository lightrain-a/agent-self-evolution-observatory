from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.e2_r17_m3r4_execution_guard import (
    FINAL_CONTRACT_STATUS,
    FRESH_IDENTITY_STATUS,
    PREFLIGHT_AUTH_STATUS,
    validate_execution_authorization,
)
from research_pipeline.e2_r17_m3r4_execution_plan import sha256_file
from scripts.freeze_e2_r17_m3r4_final_contract import freeze


ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "generated/e2-r17-m3r4-execution-draft-contract-20260904.json"
SCIENTIFIC_RUN_ROOT = Path("/data/wyt/e2-r17-search-projection/runs/m3r4-frozen-state-localization-20260904")
SCIENTIFIC_LEASE = Path("/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-m3r4-frozen-state-localization-v1.json")


def fresh_identity(*, resolved: str = "deepseek-v4-pro-ga-260813") -> dict:
    return {
        "schema_version": "1.0",
        "status": FRESH_IDENTITY_STATUS,
        "scientific_tranche": "E2-R17-M3R4",
        "scientific_experiment": False,
        "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
        "requested_and_resolved": {
            "deepseek-v4-pro": {
                "requested": "deepseek-v4-pro",
                "resolved": resolved,
                "thinking_requested": "disabled",
            }
        },
        "provider_retry_limit": 0,
        "max_output_tokens_smoke": 8192,
    }


class M3R4FinalContractFreezeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.assertFalse(SCIENTIFIC_RUN_ROOT.exists())
        self.assertFalse(SCIENTIFIC_LEASE.exists())

    def test_freeze_creates_only_final_contract_and_preflight_authorization(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e2-r17-m3r4-final-freeze-") as tmp:
            temp = Path(tmp)
            identity_path = temp / "fresh_identity.json"
            identity_path.write_text(json.dumps(fresh_identity(), sort_keys=True), encoding="utf-8")
            contract_path = temp / "final_contract.json"
            auth_path = temp / "preflight_authorization.json"

            contract, auth = freeze(
                draft_path=DRAFT,
                identity_path=identity_path,
                contract_output=contract_path,
                preflight_authorization_output=auth_path,
            )

            self.assertEqual(contract["status"], FINAL_CONTRACT_STATUS)
            self.assertTrue(all(value is False for value in contract["authority"].values()))
            self.assertEqual(contract["fresh_model_identity"]["sha256"], sha256_file(identity_path))
            self.assertEqual(contract["parent_draft"]["sha256"], sha256_file(DRAFT))
            self.assertIn("final_contract_freezer", contract["bound_code"])
            self.assertEqual(auth["status"], PREFLIGHT_AUTH_STATUS)
            self.assertFalse(auth["authority"]["scientific_experiment"])
            self.assertFalse(auth["authority"]["provider_io"])
            self.assertFalse(auth["authority"]["actor_measurement"])
            self.assertFalse(auth["measurement_authorization_created"])
            self.assertEqual(auth["contract_sha256"], sha256_file(contract_path))
            validate_execution_authorization(
                contract_path=contract_path,
                authorization_path=auth_path,
                stop_before_provider_io=True,
            )
            self.assertFalse(SCIENTIFIC_RUN_ROOT.exists())
            self.assertFalse(SCIENTIFIC_LEASE.exists())

    def test_identity_drift_fails_closed_without_outputs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e2-r17-m3r4-final-freeze-drift-") as tmp:
            temp = Path(tmp)
            identity_path = temp / "fresh_identity.json"
            identity_path.write_text(json.dumps(fresh_identity(resolved="deepseek-v4-pro-drift"), sort_keys=True), encoding="utf-8")
            contract_path = temp / "final_contract.json"
            auth_path = temp / "preflight_authorization.json"
            with self.assertRaisesRegex(RuntimeError, "resolved model drift"):
                freeze(
                    draft_path=DRAFT,
                    identity_path=identity_path,
                    contract_output=contract_path,
                    preflight_authorization_output=auth_path,
                )
            self.assertFalse(contract_path.exists())
            self.assertFalse(auth_path.exists())
            self.assertFalse(SCIENTIFIC_RUN_ROOT.exists())
            self.assertFalse(SCIENTIFIC_LEASE.exists())

    def test_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e2-r17-m3r4-final-freeze-overwrite-") as tmp:
            temp = Path(tmp)
            identity_path = temp / "fresh_identity.json"
            identity_path.write_text(json.dumps(fresh_identity(), sort_keys=True), encoding="utf-8")
            contract_path = temp / "final_contract.json"
            auth_path = temp / "preflight_authorization.json"
            contract_path.write_text("existing", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "refuses to overwrite"):
                freeze(
                    draft_path=DRAFT,
                    identity_path=identity_path,
                    contract_output=contract_path,
                    preflight_authorization_output=auth_path,
                )
            self.assertEqual(contract_path.read_text(encoding="utf-8"), "existing")
            self.assertFalse(auth_path.exists())


if __name__ == "__main__":
    unittest.main()
