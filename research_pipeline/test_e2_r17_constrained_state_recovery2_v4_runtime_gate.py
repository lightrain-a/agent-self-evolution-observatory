from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V3 = ROOT / "generated/e2-r17-single-case-constrained-state-micro-recovery2-v3-contract-20260903.json"
V4 = ROOT / "generated/e2-r17-single-case-constrained-state-micro-recovery2-v4-contract-20260906.json"
PREFLIGHT = ROOT / "generated/e2-r17-single-case-constrained-state-micro-recovery2-v4-preflight-20260906.json"
AUTH = ROOT / "generated/e2-r17-single-case-constrained-state-micro-recovery2-v4-authorization-20260906.json"
SUPERSESSION = ROOT / "generated/e2-r17-single-case-constrained-state-micro-recovery2-v3-runtime-gate-supersession-20260906.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Recovery2V4RuntimeGateArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.v3 = load(V3)
        cls.v4 = load(V4)
        cls.preflight = load(PREFLIGHT)
        cls.auth = load(AUTH)
        cls.supersession = load(SUPERSESSION)

    def test_v4_preserves_scientific_geometry(self) -> None:
        for key in ("actor", "actor_runtime", "budget", "case_stream", "heldout_task_ids", "initial_skill", "mindmemos", "model_identity", "suite", "states"):
            self.assertEqual(self.v4[key], self.v3[key], key)
        for key in (
            "child_provider_total_limit",
            "completed_unit_replay",
            "cumulative_claims_before_child",
            "explicit_429_recovery_units",
            "inherited_completed_measurements",
            "never_started_measurements",
            "new_measurements",
            "order_policy",
            "order_salt",
            "parent_authorization_sha256",
            "parent_boundary_sha256",
            "parent_claims_by_arm",
            "parent_contract_sha256",
            "parent_failure_sha256",
            "parent_lease_sha256",
            "parent_manifests",
            "parent_run_root",
            "quota_reset_not_before",
            "remaining_execution_order",
            "remaining_execution_order_sha256",
        ):
            self.assertEqual(self.v4["recovery2"][key], self.v3["recovery2"][key], key)

    def test_v4_changes_only_child_control_plane_paths_and_runtime_gate_metadata(self) -> None:
        self.assertNotEqual(self.v4["run_root"], self.v3["run_root"])
        self.assertNotEqual(self.v4["lineage_lease_path"], self.v3["lineage_lease_path"])
        revision = self.v4["recovery2"]["runtime_gate_revision"]
        self.assertEqual(revision["revision"], "V4_POINT_OF_USE_RESET_GATE")
        self.assertTrue(revision["orchestrator_enforces_not_before"])
        self.assertTrue(revision["actor_wrapper_enforces_not_before"])
        self.assertFalse(revision["scientific_geometry_changed"])

    def test_v3_is_explicitly_superseded_without_calls(self) -> None:
        self.assertEqual(self.supersession["status"], "PASS_RECOVERY2_V4_SUPERSEDES_UNUSED_V3_AUTHORITY_RUNTIME_GATE_REPAIR")
        self.assertEqual(self.supersession["v3_provider_calls"], 0)
        self.assertEqual(self.supersession["v3_scientific_outcomes"], 0)
        self.assertTrue(self.supersession["v3_execution_authority_revoked"])
        self.assertTrue(self.supersession["v3_run_root_absent"])
        self.assertTrue(self.supersession["v3_lineage_lease_absent"])
        self.assertEqual(self.v4["recovery2"]["superseded_v3"]["sha256"], sha(SUPERSESSION))

    def test_v4_bound_code_is_current(self) -> None:
        for key, row in self.v4["bound_code"].items():
            path = ROOT / row["path"]
            self.assertTrue(path.is_file(), key)
            self.assertEqual(sha(path), row["sha256"], key)

    def test_v4_preflight_and_authorization_bind_not_before(self) -> None:
        gate = self.v4["recovery2"]["quota_reset_not_before"]
        self.assertEqual(self.preflight["status"], "PASS_CONSTRAINED_STATE_MICRO_ZERO_PROVIDER_PREFLIGHT")
        self.assertEqual(self.preflight["contract_sha256"], sha(V4))
        self.assertEqual(self.preflight["execution_not_before"], gate)
        self.assertTrue(self.preflight["runtime_gate_enforced_at_point_of_use"])
        self.assertEqual(self.auth["contract_sha256"], sha(V4))
        self.assertEqual(self.auth["preflight_sha256"], sha(PREFLIGHT))
        self.assertEqual(self.auth["execution_scope"]["execution_not_before"], gate)
        self.assertTrue(self.auth["execution_scope"]["exactly_once"])
        self.assertFalse(self.auth["execution_scope"]["automatic_retry"])

    def test_v4_child_paths_are_fresh(self) -> None:
        self.assertFalse(Path(self.v4["run_root"]).exists())
        self.assertFalse(Path(self.v4["lineage_lease_path"]).exists())


if __name__ == "__main__":
    unittest.main()
