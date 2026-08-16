from __future__ import annotations

import unittest

from .pf4_diagnostic_equivalence_analysis import generic, qualification, sequence

class PF4DiagnosticEquivalenceTest(unittest.TestCase):
    def rows(self):
        rows=[]
        for condition in ("none","prompt","workflow","tool"):
            for i in range(6):
                repeat=1 if condition=="none" and i==0 else 0
                actions=["look","look"] if repeat else ["look","inventory"]
                rows.append({"condition":condition,"task_id":f"t{i}","success":1,"steps":len(actions),"immediate_repeat_count":repeat,"update_intervention_count":1 if condition in {"workflow","tool"} and i==0 else 0,"executed_actions":actions,"invalid_actions":0})
        return rows

    def test_functional_equivalence_qualification_passes_only_with_active_contract(self):
        report=qualification(self.rows())
        self.assertTrue(report["passed"])
        self.assertEqual(report["checks"]["identical_success_tasks"],6)
        rows=self.rows()
        for row in rows:
            if row["condition"]=="none":row["immediate_repeat_count"]=0;row["executed_actions"]=["look","inventory"]
        self.assertFalse(qualification(rows)["passed"])

    def test_sequence_features_strictly_extend_generic_trace_composition(self):
        row={"executed_actions":["open fridge","take apple from fridge","move apple to table","look"],"invalid_actions":0}
        self.assertEqual(len(generic(row)),9)
        self.assertEqual(len(sequence(row)),58)
        self.assertEqual(sequence(row)[:9],generic(row))


if __name__=="__main__":unittest.main()
