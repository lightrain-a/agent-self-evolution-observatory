from __future__ import annotations

import json
import pathlib
import unittest

from . import failure_memory_memrl_fresh_utilization_r55 as r55
from . import failure_memory_memrl_fresh_ab_r56 as r56

ROOT=pathlib.Path(__file__).resolve().parents[1]


class FreshR55R56Test(unittest.TestCase):
    def _load(self,name): return json.loads((ROOT/'generated'/name).read_text())
    def _sealed(self,obj):
        return obj['receipt_sha256']==r55.r47.digest({k:v for k,v in obj.items() if k!='receipt_sha256'})

    def test_r55_manifest_and_authority_are_sealed(self):
        m=self._load('d2-failure-memory-provenance-r55-fresh-utilization-manifest.json')
        a=self._load('d2-failure-memory-provenance-r55-fresh-utilization-authority.json')
        self.assertTrue(self._sealed(m)); self.assertTrue(self._sealed(a))
        e=m['execution_manifest']; ids=e['utilization_qualification']['representative_ids']
        self.assertEqual(ids,['110','438','456','258','427','183','388','16'])
        self.assertEqual(r55.ids_hash(ids),e['utilization_qualification']['representative_ids_sha256'])
        self.assertTrue(a['authorized_scope']['utilization_qualification']['authorized'])
        self.assertFalse(a['authorized_scope']['primary_A_B']['authorized'])
        self.assertEqual(a['bindings']['runner_sha256'],r55.r47.sha(ROOT/'research_pipeline/failure_memory_memrl_fresh_utilization_r55.py'))

    def test_r56_is_frozen_before_utilization_and_conditional(self):
        c=self._load('d2-failure-memory-provenance-r56-fresh-ab-confirmatory-contract.json')
        a=self._load('d2-failure-memory-provenance-r56-fresh-ab-conditional-authority.json')
        self.assertTrue(self._sealed(c)); self.assertTrue(self._sealed(a))
        self.assertEqual(c['prevalidation_accounting']['utilization_treatment_outcomes_observed'],0)
        self.assertEqual(c['prevalidation_accounting']['A_B_treatment_outcomes_observed'],0)
        self.assertEqual(c['units']['count'],32)
        self.assertEqual(len(c['units']['representative_ids']),32)
        self.assertEqual(c['analysis']['bootstrap_repetitions'],100000)
        self.assertEqual(c['analysis']['effect_relevance_floor_abs'],0.15)
        self.assertTrue(a['authority']['A_B_execution_conditionally_after_R55_PASS'])
        self.assertFalse(a['authority']['C_D_execution'])
        self.assertEqual(a['bindings']['runner_sha256'],r55.r47.sha(ROOT/'research_pipeline/failure_memory_memrl_fresh_ab_r56.py'))

    def test_r55_plan_has_exactly_40_arm_runs(self):
        m=self._load('d2-failure-memory-provenance-r55-fresh-utilization-manifest.json')
        ids=m['execution_manifest']['utilization_qualification']['representative_ids']
        by={tid:{'selected':[{'memory_id':f'm-{tid}','content':'x','source_outcome_success':True}]} for tid in ids}
        p=r55.build_plan(m,by)
        self.assertEqual(len(p['schedule']),40)
        self.assertEqual(set(x['arm'] for x in p['schedule']),set(r55.ARMS))

    def test_r56_arm_order_is_two_arm_deterministic(self):
        a=r56.r48.arm_order(20260825,'150')
        b=r56.r48.arm_order(20260825,'150')
        self.assertEqual(a,b); self.assertEqual(set(a),set(r56.ARMS))


if __name__=='__main__': unittest.main()
