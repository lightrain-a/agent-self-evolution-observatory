from __future__ import annotations
import tempfile, unittest
from pathlib import Path
from .experiment_authority import acquire_authority, reconcile_authority, validate_authority, release_authority

class ExperimentAuthorityTest(unittest.TestCase):
 def test_single_writer_lease_blocks_conflicting_run(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); a=acquire_authority(root,'idea-x','plan-a','test','execute','run-a')
   self.assertTrue(validate_authority(root,'idea-x',a['authority_id'],'plan-a')['valid'])
   with self.assertRaisesRegex(RuntimeError,'already active'):
    acquire_authority(root,'idea-x','plan-b','other','execute','run-b')
   release_authority(root,'idea-x',a['authority_id'],'done')
   b=acquire_authority(root,'idea-x','plan-b','other','execute','run-b')
   self.assertGreater(b['authority_epoch'],a['authority_epoch'])
 def test_reconcile_releases_stale_authority_without_active_run(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); a=acquire_authority(root,'idea-y','plan-a','test','execute','run-a')
   path=root/'experiment-authority'/'idea-y.json'; row=__import__('json').loads(path.read_text())
   row['acquired_at']='2020-01-01T00:00:00+00:00'; path.write_text(__import__('json').dumps(row))
   rec=reconcile_authority(root,'idea-y',set(),0)
   self.assertEqual(rec['status'],'released'); self.assertEqual(rec['release_outcome'],'reconciled-no-active-run')
   self.assertFalse(validate_authority(root,'idea-y',a['authority_id'])['valid'])

if __name__=='__main__': unittest.main()
