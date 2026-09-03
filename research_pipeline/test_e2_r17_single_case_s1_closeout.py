from __future__ import annotations
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class SingleCaseS1CloseoutTests(unittest.TestCase):
    def test_audit_is_outcome_blind(self)->None:
        s=(ROOT/'scripts/audit_e2_r17_single_case_s1_completion.py').read_text()
        self.assertNotIn('ref["score"]',s)
        self.assertIn('"scientific_scores_read":False',s)
        self.assertIn('"partial_effect_read":False',s)
        self.assertIn('"analyzer_run":False',s)
    def test_analyzer_crosses_score_boundary_after_gate(self)->None:
        s=(ROOT/'scripts/analyze_e2_r17_single_case_s1.py').read_text()
        self.assertLess(s.index('req(au.get("status")==AUDIT_STATUS'),s.index('value=float(ref["score"])'))
        self.assertLess(s.index('req(aa.get("status")==AUTH_STATUS'),s.index('value=float(ref["score"])'))
    def test_candidate_tie_break_and_gate_are_frozen(self)->None:
        s=(ROOT/'scripts/analyze_e2_r17_single_case_s1.py').read_text()
        self.assertIn('candidate="progress_fail" if gains["progress_fail"]>=gains["progress_contrast"] else "progress_contrast"',s)
        self.assertIn('gate_gain=gains[candidate]>=EPS-1e-15',s)
        self.assertIn('gate_control=j[candidate]>=j["win_c"]-1e-15',s)
    def test_analysis_authorization_is_nonexecution(self)->None:
        s=(ROOT/'scripts/authorize_e2_r17_single_case_s1_analysis.py').read_text()
        for marker in ('"scientific_experiment":False','"provider_io":False','"updater":False','"heldout_evaluation":False','"paper_promotion":False','"submission":False'):
            self.assertIn(marker,s)

if __name__=='__main__': unittest.main()
