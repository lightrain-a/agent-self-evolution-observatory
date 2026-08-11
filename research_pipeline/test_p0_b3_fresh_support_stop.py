from __future__ import annotations
import unittest
from .p0_b3_fresh_support_stop import build_state

class P0B3FreshSupportStopTest(unittest.TestCase):
    def test_fresh_reality_support_is_insufficient_without_method_failure(self):
        s=build_state()
        self.assertEqual(s['decision'],'STOP_CURRENT_SUBSTRATE_FRESH_CINTERACTION_SUPPORT_INSUFFICIENT')
        self.assertEqual(s['required_unique_fresh_pair_targets'],6)
        self.assertEqual(s['available_unique_fresh_pair_targets'],5)
        self.assertEqual(s['family_support']['pick_and_place_simple']['fresh'],0)
        self.assertFalse(s['method_failure_authorized'])

if __name__=='__main__': unittest.main()
