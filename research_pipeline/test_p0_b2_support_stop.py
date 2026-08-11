from __future__ import annotations
import unittest
from .p0_b2_support_stop import build_state

class P0B2SupportStopTest(unittest.TestCase):
    def test_current_substrate_stops_without_method_failure(self):
        s=build_state(); g=s['frozen_support_gate']
        self.assertEqual(s['decision'],'STOP_CURRENT_SUBSTRATE_CONCLUSION_CHANGE_SUPPORT_INSUFFICIENT')
        self.assertEqual(g['current_controlled_nonzero_memory_effects'],11)
        self.assertEqual(g['required_reproducible_conclusion_change_cases'],30)
        self.assertEqual(g['dedicated_conclusion_change_deletion_cases_available'],0)
        self.assertFalse(s['method_failure_authorized'])
        self.assertFalse(s['exact_method_stop_fired'])

if __name__=='__main__': unittest.main()
