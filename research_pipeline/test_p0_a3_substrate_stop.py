from __future__ import annotations

import unittest
from .p0_a3_substrate_stop import build_state


class P0A3SubstrateStopTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state=build_state()

    def test_current_substrate_stops_before_fresh_collection(self):
        s=self.state
        self.assertEqual(s['decision'],'STOP_CURRENT_SUBSTRATE_UPDATER_INCOMPETENT')
        self.assertFalse(s['updater_competence']['passed'])
        self.assertEqual(s['updater_competence']['candidate_count'],8)
        self.assertEqual(s['updater_competence']['positive_target_gain_candidates'],1)
        self.assertAlmostEqual(s['updater_competence']['effective_candidate_fraction'],0.125)
        self.assertFalse(s['fresh_final_a3_test']['execution_authorized'])
        self.assertFalse(s['fresh_final_a3_test']['fresh_outputs_present'])

    def test_does_not_overclaim_method_failure(self):
        s=self.state
        self.assertTrue(s['mastered_panel']['passed'])
        self.assertEqual(s['mastered_panel']['panel_size'],6)
        self.assertFalse(s['legacy_probe_fidelity']['passed'])
        self.assertFalse(s['method_failure_authorized'])
        self.assertFalse(s['exact_method_stop_fired'])
        self.assertFalse(s['fresh_final_a3_test']['hidden_original_opened'])
        self.assertFalse(s['fresh_final_a3_test']['method_result_available'])

if __name__=='__main__': unittest.main()
