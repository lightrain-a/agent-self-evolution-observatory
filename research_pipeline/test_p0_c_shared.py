from __future__ import annotations
import json, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from .p0_c_shared_analyze import analyze_c1, analyze_c4, analyze_c5
from .p0_revived_c_f0 import run_c1_f0, run_c4_f0, run_c5_f0

class CSharedAnalyzeTest(unittest.TestCase):
    def _fixture(self):
        effects={}; labels=[]; modes=[]
        families=['pick_and_place_simple','pick_clean_then_place_in_recep','pick_cool_then_place_in_recep','pick_heat_then_place_in_recep']
        for i in range(32):
            cid=f'c{i:03d}'; benefit=i%2==0
            effects[cid]={'candidate_id':cid,'task_family':families[i%4],'source_steps':20+i%7,'source_invalid_rate':0.01*(i%3),'patch_words':12+i%5,'rewrite_success':int(i%3==0),'replan_success':int(i%4==0),'retrieve_success':int(i%5==0) if i>=8 else None,'rewrite_replan_success':int(i%3==0),'replan_rewrite_success':int(i%4==0),'probe_delta':[0]*8,'hidden_delta':[1 if benefit else -1,0,0,0],'hidden_sum':1 if benefit else -1,'hidden_mean':0.25 if benefit else -0.25,'probe_mean':0.0,'probe_harm':0}
            for root in (0,1):
                truth='ACCEPT' if benefit else 'QUARANTINE'
                root_dec=truth if root==0 else ('QUARANTINE' if truth=='ACCEPT' else 'ACCEPT')
                parent=None
                for r in range(5):
                    dec=root_dec
                    row={'label_id':f'{cid}:{root}:{r}','lineage_id':f'{cid}:root{root}','candidate_id':cid,'root':root,'round':r,'parent_label_id':parent,'decision':dec,'confidence':0.8,'lens':'x'}
                    labels.append(row); parent=row['label_id']
            for mode,key in [('rewrite','rewrite_success'),('replan','replan_success')]:
                modes.append({'candidate_id':cid,'mode':mode,'trace':{'success':effects[cid][key],'steps':10+i%6}})
            if effects[cid]['retrieve_success'] is not None:
                modes.append({'candidate_id':cid,'mode':'retrieve','trace':{'success':effects[cid]['retrieve_success'],'steps':12}})
        return {'candidates':list(effects.values()),'labels':labels,'future':[],'modes':modes},effects

    def test_c1_counts_real_lineage_contract(self):
        data,effects=self._fixture(); out=analyze_c1(data,effects)
        self.assertGreaterEqual(out['labels_with_future_truth'],200)
        self.assertEqual(out['candidates_with_future_truth'],32)
        self.assertIn(out['decision'],{'F0_LINEAGE_SIGNAL_CONTINUE','STOP_SIMPLE_LINEAGE_WEIGHTING_NO_HEADROOM','HOLD_C1_TARGET_OR_LINEAGE_SUPPORT_INSUFFICIENT'})

    def test_c4_and_c5_emit_typed_decisions(self):
        data,effects=self._fixture(); c4=analyze_c4(data,effects); c5=analyze_c5(data,effects)
        self.assertEqual(c4['failures'],32); self.assertGreaterEqual(c4['order_pairs'],1)
        self.assertTrue(c4['decision'].startswith(('F0_','STOP_','HOLD_')))
        self.assertEqual(c5['candidates'],32); self.assertEqual(c5['future_accept']+c5['future_quarantine'],32)
        self.assertTrue(c5['decision'].startswith(('F0_','STOP_','HOLD_')))

    def test_shared_analysis_replaces_missing_substrate_hold(self):
        data,effects=self._fixture(); shared={'candidates_total':40,'C-1':analyze_c1(data,effects),'C-4':analyze_c4(data,effects),'C-5':analyze_c5(data,effects)}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'analysis.json').write_text(json.dumps(shared),encoding='utf-8')
            with patch.dict(os.environ,{'P0_C_SHARED_ROOT':td}):
                cards=[run_c1_f0(),run_c4_f0(),run_c5_f0()]
        self.assertTrue(all(c['decision']!='HOLD_REAL_TRACE_SUBSTRATE_MISSING' for c in cards))
        self.assertEqual(cards[0]['substrate_inventory']['observed_effective_candidates'],40)
        self.assertEqual(cards[2]['substrate_inventory']['observed_effective_candidates'],32)

if __name__=='__main__': unittest.main()
