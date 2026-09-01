from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from scripts.run_e2_r17_actor_pool_measurement_compat_v1 import validate_authority
from scripts.run_e2_r17_deepseek_v2_repair2_m1_measurement import (
    validate_contract_authorization,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-measurement-contract-v2-20260831.json"
AUTH = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-preflight-authorization-v2-20260831.json"
OLD_AUTH = ROOT / "generated/e2-r17-deepseek-v2-repair2-authorization-20260831.json"
PARENT_ACTOR = Path(
    "/home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/"
    "scripts/run_e2_r17_actor_pool.py"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Repair2M1MeasurementTests(unittest.TestCase):
    def test_parent_actor_is_immutable(self) -> None:
        self.assertEqual(
            sha(PARENT_ACTOR),
            "20a81fbe06f3839cd17babfdb021407368493da61610bca33aae33df8d31ec14",
        )

    def test_m1_contract_and_parent_provenance_validate_without_execution_authority(self) -> None:
        contract, authorization, _, _ = validate_contract_authorization(
            CONTRACT, AUTH, execution=False
        )
        self.assertIs(authorization["authority"]["updater"], False)
        self.assertIs(authorization["authority"]["analyzer"], False)
        self.assertEqual(contract["measurement"]["heldout_evaluations"], 36)
        self.assertEqual(contract["measurement"]["measurement_states"], 2)
        self.assertEqual(contract["measurement"]["new_updater_calls"], 0)
        self.assertEqual(contract["measurement"]["replayed_updater_calls"], 0)
        self.assertIs(contract["measurement"]["partial_effect_read"], False)

    def test_actual_actor_authority_path_accepts_all_36_preflight_combinations(self) -> None:
        payload = json.loads(AUTH.read_text(encoding="utf-8"))
        tasks = payload["execution_scope"]["allowed_task_ids"]
        for task in tasks:
            for _arm in ("win_c", "mrw"):
                observed, observed_sha = validate_authority(
                    mode="e1",
                    authorization=AUTH,
                    task_ids=[task],
                    split={"development": []},
                    k=1,
                    stop_before_provider_io=True,
                )
                self.assertTrue(observed["status"].startswith("PREFLIGHT_ONLY_"))
                self.assertEqual(observed_sha, sha(AUTH))

    def test_preflight_authorization_cannot_reach_provider_io(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "cannot reach provider I/O"):
            validate_authority(
                mode="e1",
                authorization=AUTH,
                task_ids=["r17-b4-agj-p2"],
                split={"development": []},
                k=1,
                stop_before_provider_io=False,
            )

    def test_old_repair2_authorization_is_rejected_by_versioned_actor(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "not an M1 measurement-only authorization"):
            validate_authority(
                mode="e1",
                authorization=OLD_AUTH,
                task_ids=["r17-b4-agj-p2"],
                split={"development": []},
                k=1,
                stop_before_provider_io=True,
            )

    def test_m1_rejects_nonunit_k(self) -> None:
        for bad_k in (0, 2):
            with self.subTest(bad_k=bad_k):
                with self.assertRaisesRegex(RuntimeError, "exact K=1"):
                    validate_authority(
                        mode="e1",
                        authorization=AUTH,
                        task_ids=["r17-b4-agj-p2"],
                        split={"development": []},
                        k=bad_k,
                        stop_before_provider_io=True,
                    )


if __name__ == "__main__":
    unittest.main()
