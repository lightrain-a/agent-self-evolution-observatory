from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from research_pipeline.e2_r17_m3r4_execution_guard import (
    FINAL_CONTRACT_STATUS,
    FRESH_IDENTITY_STATUS,
    PREFLIGHT_AUTH_STATUS,
)
from research_pipeline.e2_r17_m3r4_execution_plan import TASK_IDS, sha256_file, structural_provider_budget


ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "generated/e2-r17-m3r4-execution-draft-contract-20260904.json"
RUNNER = ROOT / "scripts/run_e2_r17_m3r4.py"


class M3R4ActualPathPreflightTest(unittest.TestCase):
    def test_synthetic_final_contract_traverses_real_actor_path_and_stops_before_provider_io(self) -> None:
        draft = json.loads(DRAFT.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(prefix="e2-r17-m3r4-actual-path-test-") as tmp:
            temp = Path(tmp)
            identity_path = temp / "fresh_identity.json"
            identity = {
                "schema_version": "1.0",
                "status": FRESH_IDENTITY_STATUS,
                "scientific_tranche": "E2-R17-M3R4",
                "scientific_experiment": False,
                "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
                "requested_and_resolved": {
                    "deepseek-v4-pro": {
                        "requested": "deepseek-v4-pro",
                        "resolved": "deepseek-v4-pro-ga-260813",
                        "thinking_requested": "disabled",
                    }
                },
                "provider_retry_limit": 0,
                "max_output_tokens_smoke": 8192,
            }
            identity_path.write_text(json.dumps(identity, sort_keys=True), encoding="utf-8")

            contract = copy.deepcopy(draft)
            contract["status"] = FINAL_CONTRACT_STATUS
            contract["fresh_model_identity"] = {
                "path": str(identity_path),
                "sha256": sha256_file(identity_path),
            }
            contract["run_root"] = str(temp / "scientific_run_must_not_exist")
            contract["lineage_lease_path"] = str(temp / "scientific_lease_must_not_exist.json")
            contract_path = temp / "final_contract.json"
            contract_path.write_text(json.dumps(contract, sort_keys=True), encoding="utf-8")

            authorization = {
                "schema_version": "1.0",
                "status": PREFLIGHT_AUTH_STATUS,
                "contract_sha256": sha256_file(contract_path),
                "authority": {
                    "scientific_experiment": False,
                    "provider_io": False,
                    "actor_measurement": False,
                    "updater": False,
                    "analysis": False,
                },
                "execution_scope": {
                    "scientific_object": contract["scientific_object"],
                    "allowed_task_ids": list(TASK_IDS),
                    "state_ids": ["ff_r1", "ff_r2"],
                    "actor_replicates": [1, 2],
                    "logical_units": 72,
                    "completed_unit_replay": False,
                    "automatic_retry": False,
                    "partial_effect_read": False,
                    "required_resolved_model": "deepseek-v4-pro-ga-260813",
                    "max_turns": 10,
                    "max_output_tokens": 8192,
                    "provider_budget": structural_provider_budget(),
                },
            }
            authorization_path = temp / "preflight_authorization.json"
            authorization_path.write_text(json.dumps(authorization, sort_keys=True), encoding="utf-8")
            output = temp / "actual_path_preflight.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--contract",
                    str(contract_path),
                    "--authorization",
                    str(authorization_path),
                    "--stop-before-provider-io",
                    "--preflight-output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )
            if completed.returncode != 0:
                self.fail(f"actual-path preflight failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}")
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "PASS_M3R4_ACTUAL_PATH_ZERO_PROVIDER_PREFLIGHT")
            self.assertEqual(payload["logical_units_checked"], 72)
            self.assertEqual(payload["tasks_checked"], 18)
            self.assertEqual(payload["provider_calls"], 0)
            self.assertFalse(payload["provider_budget_ledger_created"])
            self.assertFalse(payload["run_root_created"])
            self.assertFalse(payload["lineage_lease_created"])
            self.assertFalse(Path(contract["run_root"]).exists())
            self.assertFalse(Path(contract["lineage_lease_path"]).exists())


if __name__ == "__main__":
    unittest.main()
