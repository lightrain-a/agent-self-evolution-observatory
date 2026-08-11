from __future__ import annotations
import unittest
from .p0_b3_real_state import build_state

class P0B3RealStateTest(unittest.TestCase):
    def test_overlap_run_is_invalid_development_only(self):
        s=build_state()
        self.assertEqual(s['status'],'invalid-development')
        self.assertIsNone(s['decision'])
        self.assertEqual(s['invalid_development']['status'],'INVALID_TARGET_OVERLAP_DEVELOPMENT_ONLY')
        self.assertFalse(s['method_failure_authorized'])

if __name__=='__main__': unittest.main()
