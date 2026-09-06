from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from scripts import run_e2_r17_actor_pool_constrained_state_micro as actor
from scripts import run_e2_r17_constrained_state_micro_recovery2 as recovery

ROOT = Path(__file__).resolve().parents[1]
GATE = "2026-09-07T00:00:00+08:00"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Recovery2RuntimeGateTests(unittest.TestCase):
    def _contract_payload(self) -> dict:
        return {
            "recovery2": {"quota_reset_not_before": GATE},
            "bound_code": {
                "actor_wrapper": {
                    "path": "scripts/run_e2_r17_actor_pool_constrained_state_micro.py",
                    "sha256": sha(ROOT / "scripts/run_e2_r17_actor_pool_constrained_state_micro.py"),
                },
                "compat_actor": {
                    "path": "scripts/run_e2_r17_actor_pool_repair2_continuation_v2.py",
                    "sha256": sha(ROOT / "scripts/run_e2_r17_actor_pool_repair2_continuation_v2.py"),
                },
            },
        }

    def _authorization_payload(self) -> dict:
        return {"execution_scope": {"execution_not_before": GATE}}

    def test_recovery_gate_rejects_before_reset(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "quota reset gate not reached"):
            recovery._require_runtime_gate(
                self._contract_payload(),
                self._authorization_payload(),
                now=datetime.fromisoformat("2026-09-06T23:59:59+08:00"),
            )

    def test_recovery_gate_accepts_exact_boundary(self) -> None:
        recovery._require_runtime_gate(
            self._contract_payload(),
            self._authorization_payload(),
            now=datetime.fromisoformat(GATE),
        )

    def test_recovery_gate_rejects_authorization_without_not_before_binding(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "not-before binding drift"):
            recovery._require_runtime_gate(
                self._contract_payload(),
                {"execution_scope": {}},
                now=datetime.fromisoformat(GATE),
            )

    def test_actor_gate_rejects_before_reset(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "contract.json"
            path.write_text(json.dumps(self._contract_payload()), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "quota reset gate not reached"):
                actor._require_recovery_runtime_gate(
                    contract_path=path,
                    authorization_payload=self._authorization_payload(),
                    now=datetime.fromisoformat("2026-09-06T23:59:59+08:00"),
                )

    def test_actor_gate_accepts_exact_boundary_and_bound_code(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "contract.json"
            path.write_text(json.dumps(self._contract_payload()), encoding="utf-8")
            actor._require_recovery_runtime_gate(
                contract_path=path,
                authorization_payload=self._authorization_payload(),
                now=datetime.fromisoformat(GATE),
            )

    def test_actor_gate_rejects_bound_code_drift(self) -> None:
        payload = self._contract_payload()
        payload["bound_code"]["actor_wrapper"]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "contract.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "bound-code drift: actor_wrapper"):
                actor._require_recovery_runtime_gate(
                    contract_path=path,
                    authorization_payload=self._authorization_payload(),
                    now=datetime.fromisoformat(GATE),
                )


if __name__ == "__main__":
    unittest.main()
