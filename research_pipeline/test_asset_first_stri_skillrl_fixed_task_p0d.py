from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
from . import asset_first_stri_skillrl_fixed_task_p0d as p0d

class SkillRLP0DTest(unittest.TestCase):
    def test_mcnemar_six_one_direction_flips_is_significant(self):
        a=[1]*12+[0]*12;b=[0]*6+[1]*6+[0]*12
        p,x,y=p0d.mcnemar(a,b)
        self.assertEqual((x,y),(0,6));self.assertLess(p,.05)

    def test_step_seed_is_deterministic_and_step_specific(self):
        a=p0d.step_seed(2026081601,'abc',2)
        self.assertEqual(a,p0d.step_seed(2026081601,'abc',2))
        self.assertNotEqual(a,p0d.step_seed(2026081601,'abc',3))

    def _write_case(self,root:Path,kind:str,break_quotient:bool=False):
        families=['f0','f1','f2','f3','f4','f5'];rows=[]
        for i in range(24):
            uid=f'u{i:02d}';a_won=1 if i<12 else 0
            if kind=='go':b_won=0 if i<6 else a_won
            else:b_won=a_won
            for arm in p0d.ARMS:
                won={'A_pristine':a_won,'B_displacement_clone':b_won,'C_identity_placebo':a_won,'D_exact_quotient':a_won}[arm]
                set_sha={'A_pristine':'setA','B_displacement_clone':'setB','C_identity_placebo':'setA','D_exact_quotient':'setA'}[arm]
                mem_sha={'A_pristine':'memA','B_displacement_clone':'memB','C_identity_placebo':'memC','D_exact_quotient':'memA'}[arm]
                actions='trajA' if arm in {'A_pristine','D_exact_quotient'} else f'traj-{arm}-{i}'
                responses=['r1','r2'] if arm in {'A_pristine','D_exact_quotient'} else [f'r-{arm}-{i}']
                if break_quotient and i==0 and arm=='D_exact_quotient':actions='broken'
                rows.append({'unit_id':uid,'arm':arm,'won':won,'task_family':families[i%6],'general_semantic_set_sha256':set_sha,'memory_prompt_sha256':mem_sha,'projected_actions_sha256':actions,'response_sha256s':responses,'steps':2})
        raw=root/'raw.jsonl';raw.write_text(''.join(json.dumps(r)+'\n' for r in rows))
        agg=root/'aggregate.json';agg.write_text(json.dumps({'status':'COMPLETE','within_budget':True,'completed_units':24,'gpu_allocation_seconds':100.0,'gpu_hours':.0278,'raw_rows_path':str(raw)}))
        return agg

    def test_analyzer_go_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);agg=self._write_case(root,'go');out=root/'analysis.json';r=p0d.analyze(root,agg,out)
            self.assertTrue(r['qualified']);self.assertEqual(r['outcome'],'GO_C4_FIXED_POLICY_DOWNSTREAM_EVIDENCE');self.assertLess(r['metrics']['B_vs_A_mcnemar_p'],.05);self.assertGreaterEqual(r['metrics']['family_replicated_flip_count'],2)

    def test_analyzer_stop_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);agg=self._write_case(root,'stop');out=root/'analysis.json';r=p0d.analyze(root,agg,out)
            self.assertTrue(r['qualified']);self.assertEqual(r['outcome'],'STOP_FIXED_POLICY_DYNAMIC_BRIDGE');self.assertEqual(r['metrics']['paired_disagreement']['B_vs_A'],0)

    def test_analyzer_fails_closed_on_quotient_trajectory_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);agg=self._write_case(root,'go',True);out=root/'analysis.json';r=p0d.analyze(root,agg,out)
            self.assertFalse(r['qualified']);self.assertEqual(r['outcome'],'INCONCLUSIVE');self.assertTrue(any('A-D-trajectory-not-identical' in x for x in r['qualification_errors']))

if __name__=='__main__':unittest.main()
