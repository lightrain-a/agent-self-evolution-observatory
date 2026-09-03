from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r2-20260903.json"
ADAPTER = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_model_identity.py"
AUTHORIZER = ROOT / "scripts/authorize_e2_r17_semantic_transfer_v3_stage_a.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SemanticTransferV3IdentityAdapterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = load_module(ADAPTER, "semantic_transfer_v3_identity_adapter_test")
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.contract_created = datetime.fromisoformat(cls.contract["created_at_utc"])

    def _qualification(self, path: Path, **row_updates) -> Path:
        row = {
            "requested_model": "deepseek-v4-pro",
            "status": "PASS",
            "resolved_model": "deepseek-v4-pro-ga-260813",
            "thinking_requested": "disabled",
            "provider_retry_limit": 0,
            "hidden_provider_retry_used": False,
            "scientific_outcome": False,
            "benchmark_data_accessed": False,
            "checks": {
                "text_exact": True,
                "resolved_model_present": True,
                "resolved_model_matches_requested_family": True,
            },
        }
        row.update(row_updates)
        payload = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-current-ark-plan-model-identity-qualification",
            "created_at_utc": (self.contract_created + timedelta(seconds=10)).isoformat(),
            "status": "PASS",
            "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
            "models": [row],
            "private_credentials_included": False,
            "raw_response_ids_included": False,
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_single_deepseek_qualification_normalizes_exact_authorizer_schema(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            q = self._qualification(Path(td) / "qualification.json")
            identity = self.adapter.build_identity(
                contract_path=CONTRACT,
                qualification_path=q,
                created_at_utc=(self.contract_created + timedelta(seconds=20)).isoformat(),
            )
        self.assertEqual("PASS_CURRENT_REVIEW_TRANCHE", identity["status"])
        row = identity["requested_and_resolved"]["deepseek-v4-pro"]
        self.assertEqual("deepseek-v4-pro-ga-260813", row["resolved"])
        self.assertEqual("disabled", row["thinking"])
        self.assertEqual(0, row["provider_retry_limit"])
        self.assertFalse(identity["authority"]["mint_stage_a_authorization"])
        self.assertFalse(identity["authority"]["stage_a_provider_execution"])
        source = AUTHORIZER.read_text(encoding="utf-8")
        self.assertIn('identity_row.get("thinking") == "disabled"', source)
        self.assertIn('identity_row.get("provider_retry_limit")', source)

    def test_wrong_exact_release_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            q = self._qualification(Path(td) / "qualification.json", resolved_model="deepseek-v4-pro-ga-WRONG")
            with self.assertRaises(RuntimeError):
                self.adapter.build_identity(contract_path=CONTRACT, qualification_path=q)

    def test_retry_or_thinking_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            q1 = self._qualification(Path(td) / "retry.json", provider_retry_limit=1)
            with self.assertRaises(RuntimeError):
                self.adapter.build_identity(contract_path=CONTRACT, qualification_path=q1)
            q2 = self._qualification(Path(td) / "thinking.json", thinking_requested="enabled")
            with self.assertRaises(RuntimeError):
                self.adapter.build_identity(contract_path=CONTRACT, qualification_path=q2)

    def test_pre_contract_qualification_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            q = self._qualification(Path(td) / "qualification.json")
            payload = json.loads(q.read_text(encoding="utf-8"))
            payload["created_at_utc"] = (self.contract_created - timedelta(seconds=1)).isoformat()
            q.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(RuntimeError):
                self.adapter.build_identity(contract_path=CONTRACT, qualification_path=q)


if __name__ == "__main__":
    unittest.main()
