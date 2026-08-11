from __future__ import annotations
import tempfile, unittest
from pathlib import Path
from .experiment_authority import acquire_authority, validate_authority, release_authority

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

if __name__=='__main__': unittest.main()
