from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.e2_r17_repair2_v3_manifest import (
    validate_v3_compatibility_manifest,
    validate_valid_rows_v3,
)
from scripts.run_e2_r17_actor_pool_repair2_v3 import validate_authority

ROOT = Path(__file__).resolve().parents[1]
REPAIR1_CONTRACT_SHA = "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80"
REPAIR1_AUTH_SHA = "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Repair2V3Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.m1_contract_path = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-measurement-contract-v2-20260831.json"
        self.m1_authorization_path = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-single-use-authorization-20260831.json"
        self.m1_pass_path = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-measurement-recovery-pass-adjudication-20260831.json"
        self.compatibility_path = ROOT / "generated/e2-r17-deepseek-v2-repair2-v3-compatibility-manifest-20260831.json"
        self.m1_contract = json.loads(self.m1_contract_path.read_text())
        self.repair2_contract = json.loads((ROOT / "generated/e2-r17-deepseek-v2-repair2-contract-20260831.json").read_text())
        self.quarantine = json.loads((ROOT / "generated/e2-r17-deepseek-v2-repair1-technical-quarantine-20260831.json").read_text())

    def scoped_authorization(self, *, status: str = "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_V3") -> dict:
        return {
            "status": status,
            "contract_sha256": "a" * 64,
            "authority": {
                "scientific_experiment": True,
                "repair2_continuation_v3": True,
                "analyzer": False,
                "paper_promotion": False,
            },
            "execution_scope": {
                "continuation_version": "repair2_v3",
                "allowed_modes": ["e1"],
                "allowed_task_ids": list(self.m1_contract["heldout"]["task_ids"]),
                "exact_k": 1,
                "allow_noninitial_skill": True,
            },
        }

    def call_validate_authority(self, payload: dict) -> None:
        split = {"development": [], "e1_common_heldout_probe": self.m1_contract["heldout"]["task_ids"]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "authorization.json"
            path.write_text(json.dumps(payload))
            validate_authority(
                mode="e1",
                authorization=path,
                task_ids=[self.m1_contract["heldout"]["task_ids"][0]],
                split=split,
                k=1,
            )

    def test_actor_accepts_only_v3_authorization(self) -> None:
        self.call_validate_authority(self.scoped_authorization())
        for rejected in (
            "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2",
            "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_M1_MEASUREMENT",
            "AUTHORIZED_E1",
        ):
            with self.subTest(status=rejected):
                with self.assertRaises(RuntimeError):
                    self.call_validate_authority(self.scoped_authorization(status=rejected))

    def test_actor_rejects_analyzer_or_unscoped_skill(self) -> None:
        payload = self.scoped_authorization()
        payload["authority"]["analyzer"] = True
        with self.assertRaises(RuntimeError):
            self.call_validate_authority(payload)
        payload = self.scoped_authorization()
        payload["execution_scope"]["allow_noninitial_skill"] = False
        with self.assertRaises(RuntimeError):
            self.call_validate_authority(payload)

    def test_real_15_pair_prefix_validates_without_effect_read(self) -> None:
        rows = validate_v3_compatibility_manifest(
            path=self.compatibility_path,
            expected_sha=sha_file(self.compatibility_path),
            repair1_contract_sha=REPAIR1_CONTRACT_SHA,
            repair1_authorization_sha=REPAIR1_AUTH_SHA,
            m1_contract_sha=sha_file(self.m1_contract_path),
            m1_authorization_sha=sha_file(self.m1_authorization_path),
            m1_pass_path=self.m1_pass_path,
            m1_pass_sha=sha_file(self.m1_pass_path),
            heldout_task_ids=self.m1_contract["heldout"]["task_ids"],
        )
        self.assertEqual(len(rows), 15)
        self.assertEqual(sum(row["source"] == "repair1_inherited" for row in rows), 14)
        recovered = [row for row in rows if row["source"] == "repair2_m1_recovered"]
        self.assertEqual([row["unit_id"] for row in recovered], ["e1-fmv-01/rep2"])
        validate_valid_rows_v3(
            rows,
            streams=self.repair2_contract["streams"],
            quarantine=self.quarantine,
            require_complete=False,
        )

    def test_quarantine_unit_requires_m1_recovery_source(self) -> None:
        row = {
            "unit_id": "e1-fmv-01/rep2",
            "stream_id": "e1-fmv-01",
            "replicate_id": 2,
            "source": "repair2_v3_fresh",
            "arms": {
                arm: {
                    "state_root": f"/safe/{arm}",
                    "skill_sha256": "a",
                    "update_receipt_sha256": "b",
                    "eval_manifest_path": "/safe/eval",
                    "eval_manifest_sha256": "c",
                }
                for arm in ("win_c", "mrw")
            },
        }
        with self.assertRaises(RuntimeError):
            validate_valid_rows_v3(
                [row],
                streams=self.repair2_contract["streams"],
                quarantine=self.quarantine,
                require_complete=False,
            )

    def test_complete_manifest_requires_14_1_33_sources(self) -> None:
        rows = []
        units = [
            (stream, replicate)
            for stream in self.repair2_contract["streams"]
            for replicate in (0, 1, 2, 3)
        ]
        repair1_left = 14
        for stream, replicate in units:
            unit_id = f"{stream}/rep{replicate}"
            if unit_id == "e1-fmv-01/rep2":
                source = "repair2_m1_recovered"
            elif repair1_left:
                source = "repair1_inherited"
                repair1_left -= 1
            else:
                source = "repair2_v3_fresh"
            rows.append(
                {
                    "unit_id": unit_id,
                    "stream_id": stream,
                    "replicate_id": replicate,
                    "source": source,
                    "arms": {
                        arm: {
                            "state_root": f"/safe/{unit_id}/{arm}",
                            "skill_sha256": "a",
                            "update_receipt_sha256": "b",
                            "eval_manifest_path": "/safe/eval",
                            "eval_manifest_sha256": "c",
                        }
                        for arm in ("win_c", "mrw")
                    },
                }
            )
        validate_valid_rows_v3(
            rows,
            streams=self.repair2_contract["streams"],
            quarantine=self.quarantine,
            require_complete=True,
        )
        rows[-1]["source"] = "repair1_inherited"
        with self.assertRaises(RuntimeError):
            validate_valid_rows_v3(
                rows,
                streams=self.repair2_contract["streams"],
                quarantine=self.quarantine,
                require_complete=True,
            )

    def test_v3_runner_is_versioned_and_outcome_blind(self) -> None:
        text = (ROOT / "scripts/run_e2_r17_deepseek_v2_repair2_continuation_v3.py").read_text()
        self.assertIn("run_e2_r17_actor_pool_repair2_v3.py", text)
        self.assertIn('"source":"repair2_v3_fresh"', text)
        self.assertIn('"inference_performed":False', text)
        self.assertNotIn('str(ROOT / "scripts/run_e2_r17_actor_pool.py")', text)


if __name__ == "__main__":
    unittest.main()
