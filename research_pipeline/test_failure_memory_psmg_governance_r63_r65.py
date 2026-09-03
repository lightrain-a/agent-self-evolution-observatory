from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import unittest

from research_pipeline import failure_memory_psmg_governance_common_r63 as c
from research_pipeline import failure_memory_psmg_calibration_r64 as r64
from research_pipeline import failure_memory_psmg_test_r65 as r65


class PSMGGovernanceR63R65Test(unittest.TestCase):
    def _feature_rows(self):
        rows=[]
        for i,t in enumerate(c.CALIBRATION_IDS):
            z={k:float(((i+1)*(j+3))%17)/8.0 for j,k in enumerate(c.Z_FEATURE_NAMES)}
            p={k:float(((i+2*j)%7))/6.0 for j,k in enumerate(c.P_FEATURE_NAMES)}
            rows.append({'task_id':t,'Z':z,'P':p,'Z_sha256':c.digest(z),'P_sha256':c.digest(p)})
        return rows

    def _test_rows(self):
        rows=[]
        for i,t in enumerate(c.TEST_IDS):
            z={k:float(((i+2)*(j+5))%19)/9.0 for j,k in enumerate(c.Z_FEATURE_NAMES)}
            p={k:float(((i+3*j)%9))/8.0 for j,k in enumerate(c.P_FEATURE_NAMES)}
            rows.append({'task_id':t,'Z':z,'P':p,'Z_sha256':c.digest(z),'P_sha256':c.digest(p)})
        return rows

    def test_unit_hashes_and_disjointness(self):
        self.assertEqual(c.ids_hash(c.CALIBRATION_IDS),c.CALIBRATION_IDS_SHA256)
        self.assertEqual(c.ids_hash(c.TEST_IDS),c.TEST_IDS_SHA256)
        self.assertEqual(c.ids_hash(c.RESERVE_IDS),c.RESERVE_IDS_SHA256)
        self.assertFalse(set(c.CALIBRATION_IDS)&set(c.TEST_IDS))
        self.assertFalse((set(c.CALIBRATION_IDS)|set(c.TEST_IDS))&set(c.RESERVE_IDS))
        self.assertEqual(len(c.CALIBRATION_IDS),24); self.assertEqual(len(c.TEST_IDS),32); self.assertEqual(len(c.RESERVE_IDS),10)

    def test_feature_schema_and_provenance_separation(self):
        row={'representative_id':'x','signature':['cp','chmod'],'member_count':2,'task_instruction':'do thing','selected':[
            {'rank':0,'eligible':True,'source_outcome_success':True,'content':'SCRIPT:\nhello','similarity':0.8,'q_estimate':0.7,'score':1.1},
            {'rank':1,'eligible':True,'source_outcome_success':False,'content':'TASK REFLECTION:\nWhat went wrong:\nhello','similarity':0.6,'q_estimate':0.3,'score':0.8},
        ]}
        z,p=c.extract_features(row)
        self.assertEqual(len(z),28); self.assertEqual(len(p),5)
        # Z contains no direct source-outcome bit; changing P alone must not change Z.
        row2=copy.deepcopy(row); row2['selected'][0]['source_outcome_success']=False
        z2,p2=c.extract_features(row2)
        self.assertEqual(z,z2); self.assertNotEqual(p,p2)

    def test_fit_is_deterministic_and_g0_is_p_blind(self):
        rows=self._feature_rows()
        y={t:(1.0 if i in {0,7,14} else -1.0 if i in {3,11,19} else 0.0) for i,t in enumerate(c.CALIBRATION_IDS)}
        m1=c.fit_controller(rows,y); m2=c.fit_controller(rows,y)
        self.assertEqual(m1,m2); self.assertTrue(m1['calibration_support']['route_support_pass'])
        f=self._test_rows()[0]
        s1=c.score_controller(m1,f)
        alt={k:1.0-f['P'][k] for k in c.P_FEATURE_NAMES}
        s2=c.score_controller(m1,f,p_override=alt)
        self.assertAlmostEqual(s1['g0_score'],s2['g0_score'],places=12)
        # Provenance is allowed to alter only the residual/PSMG score.
        self.assertAlmostEqual(s1['psmg_score']-s1['g0_score'],s1['provenance_residual_score'],places=12)

    def test_calibration_gate_fails_without_two_sided_route_support(self):
        rows=self._feature_rows()
        y={t:(1.0 if i==0 else -1.0 if i==1 else 0.0) for i,t in enumerate(c.CALIBRATION_IDS)}
        m=c.fit_controller(rows,y)
        self.assertFalse(m['calibration_support']['route_support_pass'])
        self.assertEqual(m['calibration_support']['beneficial_memory_units'],1)
        self.assertEqual(m['calibration_support']['harmful_memory_units'],1)

    def test_test_decisions_are_frozen_and_shuffle_has_no_self_donor(self):
        rows=self._feature_rows(); y={t:(1.0 if i%7==0 else -1.0 if i%11==0 else 0.0) for i,t in enumerate(c.CALIBRATION_IDS)}
        m=c.fit_controller(rows,y); d=c.freeze_test_decisions(m,self._test_rows())
        self.assertEqual(d['test_outcomes_observed_when_frozen'],0)
        self.assertEqual(d['decision_plan_sha256'],c.digest({k:v for k,v in d.items() if k!='decision_plan_sha256'}))
        self.assertTrue(all(r['task_id']!=r['shuffled_P_donor_task_id'] for r in d['rows']))
        self.assertTrue(all(set(r['decisions'])=={'g0','psmg','shuffled_psmg','naive_success_prior','always_memory','never_memory'} for r in d['rows']))

    def test_complete_only_policy_analysis(self):
        rows=self._feature_rows(); y={t:(1.0 if i%7==0 else -1.0 if i%11==0 else 0.0) for i,t in enumerate(c.CALIBRATION_IDS)}
        m=c.fit_controller(rows,y); d=c.freeze_test_decisions(m,self._test_rows())
        # Supply both potential outcomes for every task.  Analysis must be exact offline policy evaluation.
        po={}
        for i,t in enumerate(c.TEST_IDS):
            po[t]={'N_no_memory':bool(i%3==0),'M_content_only':bool(i%4==0)}
        out=c.analyze_test(d,po)
        self.assertEqual(out['units'],32)
        self.assertEqual(out['primary_estimand'],'policy_value(psmg)-policy_value(g0)')
        self.assertEqual(out['bootstrap_repetitions'],100000)
        self.assertEqual(out['effect_relevance_floor_abs'],0.15)
        self.assertIn(out['status'],{'PSMG_INCREMENTAL_GOVERNANCE_VALUE_SUPPORTED','PSMG_INCREMENTAL_GOVERNANCE_HARM_SUPPORTED','PSMG_EFFICACY_NOT_ESTABLISHED'})
        self.assertFalse(out['raw_provenance_executor_visible'])

    def test_runner_contract_constants(self):
        self.assertEqual(r64.ARMS,['N_no_memory','M_content_only'])
        self.assertEqual(r65.ARMS,['N_no_memory','M_content_only'])
        self.assertNotIn('B_raw_provenance',r64.ARMS+r65.ARMS)
        self.assertNotEqual(r64.ARM_SEED_STRING,r65.ARM_SEED_STRING)

    def test_sealed_program_and_authority_bindings(self):
        root=pathlib.Path(__file__).resolve().parents[1]
        def load(name): return json.loads((root/'generated'/name).read_text())
        def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
        program=load('d2-failure-memory-provenance-r63-psmg-hidden-governance-program.json')
        a64=load('d2-failure-memory-provenance-r64-psmg-calibration-authority.json')
        a65=load('d2-failure-memory-provenance-r65-psmg-test-conditional-authority.json')
        for obj in [program,a64,a65]:
            self.assertEqual(obj['receipt_sha256'],c.digest({k:v for k,v in obj.items() if k!='receipt_sha256'}))
        common_path=root/'research_pipeline/failure_memory_psmg_governance_common_r63.py'
        r64_path=root/'research_pipeline/failure_memory_psmg_calibration_r64.py'
        r65_path=root/'research_pipeline/failure_memory_psmg_test_r65.py'
        self.assertEqual(program['bindings']['common_module_sha256'],sha(common_path))
        self.assertEqual(program['bindings']['r64_runner_sha256'],sha(r64_path))
        self.assertEqual(program['bindings']['r65_runner_sha256'],sha(r65_path))
        self.assertEqual(a64['bindings']['common_module_sha256'],sha(common_path)); self.assertEqual(a64['bindings']['runner_sha256'],sha(r64_path))
        self.assertEqual(a65['bindings']['common_module_sha256'],sha(common_path)); self.assertEqual(a65['bindings']['runner_sha256'],sha(r65_path))
        self.assertEqual(program['controller']['g0_lambda'],c.G0_RIDGE_LAMBDA)
        self.assertEqual(program['controller']['residual_lambda'],c.RESIDUAL_RIDGE_LAMBDA)
        self.assertEqual(program['primary_analysis']['effect_relevance_floor_abs'],c.EFFECT_RELEVANCE_FLOOR_ABS)
        self.assertEqual(program['feature_schema']['Z_feature_names'],c.Z_FEATURE_NAMES)
        self.assertEqual(program['feature_schema']['P_feature_names'],c.P_FEATURE_NAMES)
        self.assertFalse(program['executor_potential_actions']['raw_source_outcome_success_in_executor_prompt'])


if __name__=='__main__': unittest.main()
