from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_e2_r17_actor_pool import validate_authority


class ActorAuthorityScopeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.split = {"development": ["dev-1"], "e1_update_streams": {"s0": ["t0", "t1"]}}

    def _auth(self, root: Path, *, tasks: list[str], exact_k: int = 8) -> Path:
        path = root / "auth.json"
        path.write_text(
            json.dumps(
                {
                    "status": "AUTHORIZED_E1",
                    "authority": {"scientific_experiment": True, "e1_b": False},
                    "execution_scope": {
                        "allowed_modes": ["e1"],
                        "allowed_task_ids": tasks,
                        "exact_k": exact_k,
                        "allow_noninitial_skill": False,
                    },
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_scoped_authority_accepts_exact_task_subset_and_k(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = self._auth(Path(tmp), tasks=["t0", "t1"])
            payload, digest = validate_authority(
                mode="e1", authorization=auth, task_ids=["t0"], split=self.split, k=8
            )
            self.assertEqual(payload["status"], "AUTHORIZED_E1")
            self.assertEqual(len(digest), 64)

    def test_scoped_authority_rejects_out_of_scope_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = self._auth(Path(tmp), tasks=["t0"])
            with self.assertRaises(RuntimeError):
                validate_authority(
                    mode="e1", authorization=auth, task_ids=["t1"], split=self.split, k=8
                )

    def test_scoped_authority_rejects_wrong_k_or_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = self._auth(Path(tmp), tasks=["t0"])
            with self.assertRaises(RuntimeError):
                validate_authority(
                    mode="e1", authorization=auth, task_ids=["t0"], split=self.split, k=4
                )
            with self.assertRaises(RuntimeError):
                validate_authority(
                    mode="public_externality", authorization=auth, task_ids=["t0"], split=self.split, k=8
                )

    def test_protocol_smoke_still_requires_development_only(self) -> None:
        payload, digest = validate_authority(
            mode="protocol_smoke", authorization=None, task_ids=["dev-1"], split=self.split, k=1
        )
        self.assertIsNone(payload)
        self.assertIsNone(digest)
        with self.assertRaises(RuntimeError):
            validate_authority(
                mode="protocol_smoke", authorization=None, task_ids=["t0"], split=self.split, k=1
            )


if __name__ == "__main__":
    unittest.main()
