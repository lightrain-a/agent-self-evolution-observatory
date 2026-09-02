from __future__ import annotations

import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class SingleCaseStabilityCloseoutTests(unittest.TestCase):
    def test_completion_audit_is_outcome_blind(self)->None:
        s=(ROOT/'scripts/audit_e2_r17_single_case_stability_completion.py').read_text()
        self.assertNotIn('ref["score"]',s)
        self.assertIn('"scientific_scores_read":False',s)
        self.assertIn('"new_learned_states":0',s)
        self.assertIn('"mint_single_use_stability_analysis_authorization":True',s)

    def test_analysis_authorization_has_no_execution_power(self)->None:
        s=(ROOT/'scripts/authorize_e2_r17_single_case_stability_analysis.py').read_text()
        for x in ('"scientific_experiment":False','"provider_io":False','"updater":False','"heldout_evaluation":False','"second_backbone":False','"public_benchmark":False','"e3_confirmation":False','"s2_execution":False','"paper_promotion":False','"submission":False'):
            self.assertIn(x,s)

    def test_analyzer_gates_before_score_access(self)->None:
        s=(ROOT/'scripts/analyze_e2_r17_single_case_stability.py').read_text()
        gate=s.index('req(au.get("status")==AUDIT_STATUS')
        score=s.index('value=float(ref["score"])')
        self.assertLess(gate,score)
        self.assertIn('REPS=(1,2)',s)
        self.assertIn('EPS=1.0/18.0',s)
        self.assertIn('FIRST_FAIL_FROZEN_STATE_STABILITY_FAIL_MEASUREMENT_INSTABILITY',s)


if __name__=='__main__': unittest.main()
