from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import scripts.run_e2_r17_semantic_transfer_v3_actor_pool_r3_recovery as actor
from research_pipeline.e2_r17_semantic_transfer_v3_stage_b_order_r3_recovery import update_pool_order

BURNED = "r17-b21-cgwb-p0"
CENSOR = "r17-b21-cgwp-p0"


class R3RecoveryControlTests(unittest.TestCase):
    def test_stage_b_order_accepts_7_and_8_only(self):
        seven = [f"t{i}" for i in range(7)]
        eight = [f"u{i}" for i in range(8)]
        self.assertEqual(set(update_pool_order("s7", 0, seven, expected_count=7)), set(seven))
        self.assertEqual(set(update_pool_order("s8", 0, eight, expected_count=8)), set(eight))
        with self.assertRaises(ValueError):
            update_pool_order("s6", 0, six := [f"x{i}" for i in range(6)], expected_count=len(six))
        with self.assertRaises(ValueError):
            update_pool_order("s7", 0, seven, expected_count=8)

    def test_r3_authority_rejects_burned_and_censor(self):
        tasks = [f"allowed-{i:03d}" for i in range(158)]
        payload = {
            "status": "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY",
            "authority": {
                "stage_a_provider_execution": True,
                "stage_b_learning_execution": False,
                "updater": False,
                "heldout_evaluation": False,
                "analyzer": False,
                "second_backbone": False,
                "public_benchmark": False,
                "paper_promotion": False,
            },
            "execution_scope": {
                "recovery_mode": "MATCHED_CENSOR_158",
                "allowed_modes": ["e1"],
                "allowed_task_ids": tasks,
                "exact_k": 8,
                "allow_noninitial_skill": False,
            },
        }
        split = {"development": []}
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "auth.json"
            p.write_text(json.dumps(payload), encoding="utf-8")
            actor.validate_authority(mode="e1", authorization=p, task_ids=tasks[:7], split=split, k=8)
            for forbidden in (BURNED, CENSOR):
                with self.assertRaises(RuntimeError):
                    actor.validate_authority(mode="e1", authorization=p, task_ids=[forbidden], split=split, k=8)
            with self.assertRaises(RuntimeError):
                actor.validate_authority(mode="e1", authorization=p, task_ids=tasks[:1], split=split, k=4)

    def test_exact_once_scope_requires_158_manifest(self):
        tasks = [f"allowed-{i:03d}" for i in range(158)]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"ordered_task_ids": tasks}), encoding="utf-8")
            import hashlib
            mh = hashlib.sha256(manifest.read_bytes()).hexdigest()
            run_root = root / "run"
            payload = {
                "execution_scope": {
                    "allowed_task_ids": tasks,
                    "exact_once_acquisition": {
                        "required": True,
                        "attempt_before_any_provider_io": True,
                        "replay_allowed": False,
                        "ambiguous_recollection_allowed": False,
                        "unit_count": 158,
                        "unit_manifest_path": str(manifest),
                        "unit_manifest_sha256": mh,
                        "required_claim_root": str(run_root / "checkpoints/stage_a_task_claims"),
                    },
                }
            }
            scope = actor.validate_exact_once_acquisition_scope(
                authorization_payload=payload,
                run_root=run_root,
                requested_task_ids=tasks[:8],
            )
            self.assertEqual(len(scope["unit_ids"]), 158)
            bad = json.loads(json.dumps(payload))
            bad["execution_scope"]["exact_once_acquisition"]["unit_count"] = 159
            with self.assertRaises(RuntimeError):
                actor.validate_exact_once_acquisition_scope(
                    authorization_payload=bad,
                    run_root=run_root,
                    requested_task_ids=tasks[:8],
                )


if __name__ == "__main__":
    unittest.main()
