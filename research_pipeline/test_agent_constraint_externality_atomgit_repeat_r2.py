from __future__ import annotations

import json, unittest
from collections import Counter

from research_pipeline import agent_constraint_externality_atomgit_repeat_common as c
from research_pipeline import agent_constraint_externality_atomgit_repeat_mcp_bridge as b
from research_pipeline import agent_constraint_externality_atomgit_repeat_adjudicate as adj
from research_pipeline.agent_constraint_externality_runner_core import sha256_value

class AtomGitRepeatR2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls)->None:
        cls.close,cls.manifest,cls.freeze=c.parents(); cls.ids=c.selected_ids(cls.manifest); cls.index=c.family_index(); cls.units=c.units()

    def test_exact_72_unit_geometry(self):
        self.assertEqual(72,len(self.units)); self.assertEqual(72,len({u['unit_id'] for u in self.units}))
        counts=Counter((u['family_id'],u['arm'],u['repeat']) for u in self.units); self.assertEqual({2},set(counts.values())); self.assertEqual(36,len(counts))
        self.assertEqual({1,2},{u['repeat'] for u in self.units}); self.assertEqual({1201,1202},{u['seed'] for u in self.units})

    def test_family_balance_and_exact_repair_set(self):
        self.assertEqual(3,sum('-FG-' in x for x in self.ids)); self.assertEqual(3,sum('-TNF-' in x for x in self.ids)); self.assertEqual(set(self.ids),set(self.manifest['repairs']))

    def test_branch_order_is_pairwise_and_frozen(self):
        for fid in self.ids:
            for arm in c.ARMS:
                for repeat in c.REPEATS:
                    order=c.frozen_branch_order(fid,arm,repeat); self.assertEqual(set(c.BRANCHES),set(order)); self.assertEqual(order,c.frozen_branch_order(fid,arm,repeat))

    def test_real_repair_is_exact_append_and_no_update_clean(self):
        for fid in self.ids:
            rb=c.repair_bytes(fid)
            for arm in c.ARMS:
                no=c.visible_instruction(fid,arm,'NO_UPDATE').encode(); real=c.visible_instruction(fid,arm,'REAL_REPAIR').encode()
                self.assertEqual(no+c.INJECTION_PREFIX+rb,real); self.assertNotIn(c.INJECTION_PREFIX,no)

    def test_crr_uses_per_constraint_new_failure_rate(self):
        self.assertEqual(0.0,c.crr({'non_target':{'a':True,'b':True}})); self.assertEqual(0.5,c.crr({'non_target':{'a':True,'b':False}})); self.assertEqual(1.0,c.crr({'non_target':{'a':False,'b':False}}))
        with self.assertRaises(c.RepeatStop): c.crr({'non_target':{'a':True}})

    def test_wrapper_changes_instruction_not_scientific_fixture(self):
        fid=self.ids[0]; arm='HIGH'
        no=b.transformed_spec(fid,arm,'NO_UPDATE')['families'][0]['source_case']; real=b.transformed_spec(fid,arm,'REAL_REPAIR')['families'][0]['source_case']
        self.assertEqual(sha256_value(no['fixture']),sha256_value(real['fixture'])); self.assertNotEqual(no['task_instruction'],real['task_instruction']); self.assertEqual(c.visible_instruction(fid,arm,'REAL_REPAIR'),real['task_instruction'])

    def test_selected_families_are_initially_matched_three_arm_objects(self):
        for fid,family in self.index.items():
            arms={a['coupling_level']:a for a in family['arms']}; self.assertEqual(set(c.ARMS),set(arms))
            self.assertEqual([0,1,2],[arms[x]['structure']['shared_resource_exposure_count'] for x in c.ARMS])
            for arm in arms.values(): self.assertEqual(2,sum(z['role']=='NON_TARGET' for z in arm['constraints']))

    def _synthetic_rows(self):
        rows=[]
        for u in self.units:
            pair=sha256_value([u['family_id'],u['arm'],u['repeat']])
            rows.append({'family_id':u['family_id'],'arm':u['arm'],'branch':u['branch'],'repeat':u['repeat'],'valid':True,'target_success':True,'crr':0.0,'scientific_state_sha256':pair,'repair_sha256':c.repair_record(u['family_id'])['repair_sha256'] if u['branch']=='REAL_REPAIR' else None})
        return rows

    def test_direction_blind_adjudicator_accepts_exact_paired_matrix(self):
        out=adj.adjudicate_rows(self._synthetic_rows()); self.assertEqual('ATOMGIT_REPEAT_DEV_R2_PASS_PRECISION_FROZEN_CONFIRMATORY_EXECUTION_CLOSED',out['status']); self.assertEqual(2,out['R_star']); self.assertEqual(12,out['precision_decision']['N_star'])

    def test_adjudicator_rejects_pair_state_or_repair_drift(self):
        rows=self._synthetic_rows(); rows[0]['scientific_state_sha256']='drift'
        with self.assertRaises(adj.AdjudicationError): adj.adjudicate_rows(rows)
        rows=self._synthetic_rows(); real=next(r for r in rows if r['branch']=='REAL_REPAIR'); real['repair_sha256']='0'*64
        with self.assertRaises(adj.AdjudicationError): adj.adjudicate_rows(rows)

    def test_authority_is_still_closed_before_readiness(self):
        self.assertFalse(self.close['authority']['development_repeat_qualification']); self.assertFalse(self.close['authority']['rq1_rq2'])

if __name__=='__main__': unittest.main()
