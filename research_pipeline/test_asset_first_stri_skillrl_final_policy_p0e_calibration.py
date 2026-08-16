from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
from research_pipeline import asset_first_stri_skillrl_final_policy_p0e_calibration as p0e

class SkillRLP0ECalibrationTest(unittest.TestCase):
    def _aggregate(self,root:Path,successes:int,families:int=3,complete:bool=True):
        rows=[]
        fams=['f0','f1','f2','f3','f4','f5']
        success_fams=fams[:families]
        for i in range(24):
            won=int(i<successes)
            fam=success_fams[i%max(1,len(success_fams))] if won and success_fams else fams[i%6]
            rows.append({'unit_id':f'u{i}','task_family':fam,'won':won})
        raw=root/'raw.jsonl';raw.write_text(''.join(json.dumps(r)+'\n' for r in rows))
        agg=root/'agg.json';agg.write_text(json.dumps({'status':'COMPLETE' if complete else 'INCOMPLETE','within_budget':True,'raw_rows_path':str(raw)}))
        return agg

    def test_support_go_requires_headroom_and_family_support(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);agg=self._aggregate(root,6,3);out=root/'analysis.json';r=p0e.analyze(agg,out)
            self.assertEqual(r['outcome'],'GO_COMPETENT_POLICY_SUPPORT');self.assertTrue(r['qualified_support'])

    def test_floor_is_stop_not_stri_negative(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);agg=self._aggregate(root,1,1);out=root/'analysis.json';r=p0e.analyze(agg,out)
            self.assertEqual(r['outcome'],'STOP_NO_COMPETENT_POLICY_SUPPORT');self.assertFalse(r['qualified_support'])
            self.assertIn('pristine-success-headroom:1',r['qualification_errors'])
            self.assertIn('forbids policy/task/checkpoint rescue',r['claim_boundary'])

    def test_family_support_gate_is_independent_of_count(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);agg=self._aggregate(root,6,1);out=root/'analysis.json';r=p0e.analyze(agg,out)
            self.assertEqual(r['outcome'],'STOP_NO_COMPETENT_POLICY_SUPPORT');self.assertIn('pristine-success-family-support:1',r['qualification_errors'])

    def test_incomplete_is_infrastructure_not_support_stop(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);agg=self._aggregate(root,6,3,False);out=root/'analysis.json';r=p0e.analyze(agg,out)
            self.assertEqual(r['outcome'],'INCONCLUSIVE_INFRASTRUCTURE');self.assertFalse(r['qualified_support'])

if __name__=='__main__':unittest.main()
