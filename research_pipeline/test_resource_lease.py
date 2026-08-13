from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .experiment_authority import acquire_authority, release_authority
from .resource_lease import acquire_gpu_lease, active_gpu_uuids, reconcile_gpu_leases, release_gpu_lease


class ResourceLeaseTest(unittest.TestCase):
    def test_gpu_lease_requires_active_matching_experiment_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with self.assertRaisesRegex(RuntimeError,"requires active experiment authority"):
                acquire_gpu_lease(root,"60","GPU-X","run-a","idea-x",idea_id="idea-x",authority_id="",plan_hash="plan-a",ttl_minutes=60)
            authority=acquire_authority(root,"idea-x","plan-a","test","execute","run-a")
            lease=acquire_gpu_lease(
                root,"60","GPU-X","run-a","idea-x",
                idea_id="idea-x",authority_id=authority["authority_id"],plan_hash="plan-a",ttl_minutes=60,
            )
            self.assertIn("GPU-X",active_gpu_uuids(root))
            self.assertEqual(lease["authority_id"],authority["authority_id"])
            self.assertEqual(lease["authority_epoch"],authority["authority_epoch"])
            self.assertEqual(lease["plan_hash"],"plan-a")
            release_gpu_lease(
                root,"60","GPU-X",lease["lease_id"],
                idea_id="idea-x",authority_id=authority["authority_id"],plan_hash="plan-a",outcome="done",
            )
            release_authority(root,"idea-x",authority["authority_id"],"done")

    def test_gpu_uuid_single_writer_and_authority_run_binding(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            a_auth=acquire_authority(root,"idea-a","plan-a","test","execute","run-a")
            a=acquire_gpu_lease(root,"60","GPU-X","run-a","idea-a",idea_id="idea-a",authority_id=a_auth["authority_id"],plan_hash="plan-a",ttl_minutes=60)
            with self.assertRaisesRegex(RuntimeError,"authority run mismatch"):
                acquire_gpu_lease(root,"60","GPU-Y","run-b","idea-a",idea_id="idea-a",authority_id=a_auth["authority_id"],plan_hash="plan-a",ttl_minutes=60)
            b_auth=acquire_authority(root,"idea-b","plan-b","test","execute","run-b")
            with self.assertRaisesRegex(RuntimeError,"already active"):
                acquire_gpu_lease(root,"60","GPU-X","run-b","idea-b",idea_id="idea-b",authority_id=b_auth["authority_id"],plan_hash="plan-b",ttl_minutes=60)
            release_gpu_lease(root,"60","GPU-X",a["lease_id"],idea_id="idea-a",authority_id=a_auth["authority_id"],plan_hash="plan-a",outcome="done")
            release_authority(root,"idea-a",a_auth["authority_id"],"done")
            b=acquire_gpu_lease(root,"60","GPU-X","run-b","idea-b",idea_id="idea-b",authority_id=b_auth["authority_id"],plan_hash="plan-b",ttl_minutes=60)
            self.assertGreater(b["lease_epoch"],a["lease_epoch"])

    def test_controller_reconcile_can_release_orphan_without_expanding_capability(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            authority=acquire_authority(root,"idea-x","plan-a","test","execute","run-a")
            lease=acquire_gpu_lease(root,"60","GPU-X","run-a","idea-x",idea_id="idea-x",authority_id=authority["authority_id"],plan_hash="plan-a",ttl_minutes=60)
            path=root/"resource-leases"/"60-GPU-X.json"
            row=__import__('json').loads(path.read_text())
            row["acquired_at"]="2020-01-01T00:00:00+00:00"
            path.write_text(__import__('json').dumps(row))
            released=reconcile_gpu_leases(root,set(),0)
            self.assertEqual(len(released),1)
            self.assertEqual(released[0]["release_outcome"],"reconciled-no-active-run")
            self.assertNotIn("GPU-X",active_gpu_uuids(root))
            # Reconciliation only removes an orphan; it does not let an unauthorised caller acquire a new lease.
            with self.assertRaisesRegex(RuntimeError,"requires active experiment authority"):
                acquire_gpu_lease(root,"60","GPU-Z","run-z","idea-z",idea_id="idea-z",authority_id="",ttl_minutes=60)


if __name__=='__main__':
    unittest.main()
