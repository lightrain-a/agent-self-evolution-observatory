from __future__ import annotations
import tempfile,unittest
from pathlib import Path
from .resource_lease import acquire_gpu_lease,active_gpu_uuids,release_gpu_lease

class ResourceLeaseTest(unittest.TestCase):
 def test_gpu_uuid_single_writer(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); a=acquire_gpu_lease(root,'60','GPU-X','run-a','test',60)
   self.assertIn('GPU-X',active_gpu_uuids(root))
   with self.assertRaisesRegex(RuntimeError,'already active'):
    acquire_gpu_lease(root,'60','GPU-X','run-b','test',60)
   release_gpu_lease(root,'60','GPU-X',a['lease_id'],'done')
   b=acquire_gpu_lease(root,'60','GPU-X','run-b','test',60)
   self.assertGreater(b['lease_epoch'],a['lease_epoch'])
if __name__=='__main__': unittest.main()
