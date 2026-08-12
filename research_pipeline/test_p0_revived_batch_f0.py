from __future__ import annotations
import unittest
from .p0_revived_batch_f0 import build_revived_batch_f0

class P0RevivedBatchF0Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = build_revived_batch_f0()
        cls.by = {row['idea_id']: row for row in cls.state['revived']}

    def test_twenty_parent_batch_is_complete(self):
        s = self.state['summary']
        self.assertEqual((s['parent_p0'], s['reused_existing_p0'], s['fresh_cpu_f0']), (20, 13, 7))
        self.assertEqual((s['fresh_matched_simplification_stop'], s['fresh_upstream_hold'], s['fresh_signal_continue']), (7, 0, 0))
        self.assertEqual(s['fresh_matched_simplification_stop'] + s['fresh_upstream_hold'] + s['fresh_signal_continue'], s['fresh_cpu_f0'])
        self.assertEqual(len({row['code'] for row in self.state['parent_batch']}), 20)

    def test_real_c_f0s_are_terminal_without_method_failure_authority(self):
        expected = {
            'self-label-confidence-flow': 'STOP_SIMPLE_LINEAGE_WEIGHTING_NO_HEADROOM',
            'self-correction-collapse-detector': 'STOP_C4_SHALLOW_RULE_NO_HEADROOM',
            'intervention-validated-self-correction': 'STOP_C5_A3_SIMPLE_THRESHOLD_NO_HEADROOM',
        }
        for idea_id, decision in expected.items():
            row = self.by[idea_id]
            self.assertEqual(row['decision'], decision)
            self.assertFalse(row['method_failure_authorized'])
            self.assertTrue(row['gpu0']['status'].startswith('stop-'))

    def test_programmatic_f0s_are_killed_by_same_information_baselines(self):
        expected = {
            'failure-frontier-curriculum': 'STOP_MATCHED_DIRECT_YIELD_EQUIVALENT',
            'world-model-error-gated-learning': 'STOP_MATCHED_DIRECT_ACTION_DISAGREEMENT_EQUIVALENT',
            'irreversible-action-counterfactuals': 'STOP_MATCHED_DIRECT_SHIELD_EQUIVALENT',
            'recovery-conditioned-experience': 'STOP_MATCHED_DIRECT_RECOVERY_POLICY_EQUIVALENT',
        }
        for idea_id, decision in expected.items():
            row = self.by[idea_id]
            self.assertEqual(row['decision'], decision)
            self.assertTrue(row['matched_simplification']['equivalent'])
            self.assertFalse(row['method_failure_authorized'])

if __name__ == '__main__': unittest.main()
