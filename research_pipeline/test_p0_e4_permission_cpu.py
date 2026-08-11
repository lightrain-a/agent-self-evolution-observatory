from __future__ import annotations
import json, unittest
from .config import PROJECT_ROOT
from .p0_e4_permission_cpu import FEATURES, PERMS, _intervention_truth, _mutation

class P0E4PermissionCpuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.state=json.loads((PROJECT_ROOT/'generated'/'p0-e4-permission-cpu.json').read_text(encoding='utf-8'))
    def test_feature_combinations_are_held_out(self):
        key=lambda m:tuple(m['features'][x] for x in FEATURES)
        train={key(_mutation(i,'train')) for i in range(64)}
        test={key(_mutation(i,'test')) for i in range(32)}
        self.assertFalse(train & test); self.assertEqual(len(test),7)
    def test_matched_boolean_rule_falsifies_learned_q(self):
        m=self.state['metrics']; matched=self.state['matched_simplification']
        self.assertEqual(m['learned_missed_risky'],0); self.assertEqual(m['matched_rule_missed_risky'],0)
        self.assertLess(m['matched_rule_reauthorizations'],m['learned_reauthorizations'])
        self.assertTrue(matched['equivalent_or_better'])
        self.assertEqual(self.state['decision'],'STOP_MATCHED_BOOLEAN_RULE_EQUIVALENT')
        self.assertFalse(self.state['p1_authorized'])
    def test_test_labels_are_non_degenerate(self):
        rows=[_mutation(i,'test') for i in range(32)]
        labels=[_intervention_truth(m)[p] for m in rows for p in PERMS]
        self.assertGreater(sum(labels),0); self.assertGreater(len(labels)-sum(labels),0)
    def test_rule_is_induced_from_same_intervention_labels(self):
        rules=self.state['matched_monotone_dnf']
        self.assertEqual(rules['read'],[['memory_delta','callgraph_delta']])
        self.assertEqual(rules['network'],[['callgraph_delta','dependency_delta']])
        self.assertEqual(len(rules['write']),2)

if __name__=='__main__': unittest.main()
