from __future__ import annotations
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class StabilityCloseoutTests(unittest.TestCase):
    def test_audit_outcome_blind(self):
        s=(ROOT/'scripts/audit_e2_r17_single_case_stability_completion.py').read_text()
        self.assertNotIn('ref["score"]',s); self.assertIn("'scientific_scores_read':False",s); self.assertIn("'partial_effect_read':False",s); self.assertIn("'analyzer_run':False",s)
    def test_analyzer_gate_before_score(self):
        s=(ROOT/'scripts/analyze_e2_r17_single_case_stability.py').read_text(); score=s.index("value=float(ref['score'])"); self.assertLess(s.index("req(au.get('status')==AUDIT"),score); self.assertLess(s.index("req(aa.get('status')==AUTH"),score)
    def test_stability_gate_frozen(self):
        s=(ROOT/'scripts/analyze_e2_r17_single_case_stability.py').read_text(); self.assertIn("rep_pass={rep:diffs[rep]>=EPS-1e-15 for rep in REPS}",s); self.assertIn("passed=all(rep_pass.values()) and mean_diff>=EPS-1e-15",s); self.assertIn("historical_s1_replicate_used_for_gate':False",s)
    def test_analysis_auth_nonexecution(self):
        s=(ROOT/'scripts/authorize_e2_r17_single_case_stability_analysis.py').read_text()
        for x in ("'scientific_experiment':False","'provider_io':False","'updater':False","'heldout_evaluation':False","'paper_promotion':False","'submission':False"): self.assertIn(x,s)
if __name__=='__main__': unittest.main()
