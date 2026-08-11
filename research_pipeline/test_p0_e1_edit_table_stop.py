from __future__ import annotations
import unittest
from .p0_e1_edit_table_stop import build_state

class P0E1EditTableStopTest(unittest.TestCase):
    def test_current_table_stops_without_opening_hidden(self):
        s=build_state(); t=s['source_table']
        self.assertEqual(s['decision'],'STOP_CURRENT_EDIT_TABLE_RANKING_DEGENERATE')
        self.assertEqual((t['effective_workflows'],t['workflows']),(4,16))
        self.assertEqual(t['uniquely_ranked_workflows'],3)
        self.assertFalse(t['identifiable'])
        self.assertFalse(s['hidden_workflows_opened'])
        self.assertFalse(s['method_failure_authorized'])

if __name__=='__main__': unittest.main()
