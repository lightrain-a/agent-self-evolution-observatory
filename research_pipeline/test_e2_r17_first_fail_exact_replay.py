from __future__ import annotations

import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class FirstFailExactReplayTests(unittest.TestCase):
    def test_preflight_requires_exact_s1_evidence_before_provider(self)->None:
        s=(ROOT/'scripts/preflight_e2_r17_first_fail_exact_replay.py').read_text()
        self.assertIn("require(actual==expected",s)
        self.assertIn("'provider_calls':0",s)
        self.assertIn("'scientific_outcomes_read':False",s)
        self.assertNotIn("['score']",s)

    def test_runner_checks_exact_evidence_before_run_root_and_updates(self)->None:
        s=(ROOT/'scripts/run_e2_r17_first_fail_exact_replay.py').read_text()
        evidence=s.index('verify_exact_evidence(c,units)')
        run_root=s.index('run=Path(c["run_root"])')
        update_loop=s.index('for rep in REPS:')
        self.assertLess(evidence,run_root)
        self.assertLess(evidence,update_loop)
        self.assertIn('ARMS=("win_c","first_fail")',s)
        self.assertIn('REPS=(1,2)',s)

    def test_completion_audit_is_outcome_blind(self)->None:
        s=(ROOT/'scripts/audit_e2_r17_first_fail_exact_replay_completion.py').read_text()
        self.assertNotIn("ref['score']",s)
        self.assertIn("'scientific_scores_read':False",s)
        self.assertIn("'exact_evidence_identity_pass':True",s)

    def test_analysis_gate_is_frozen(self)->None:
        s=(ROOT/'scripts/analyze_e2_r17_first_fail_exact_replay.py').read_text()
        audit=s.index("req(au.get('status')==AUDIT")
        score=s.index("value=float(ref['score'])")
        self.assertLess(audit,score)
        self.assertIn('EPS=1.0/18.0',s)
        self.assertIn('FIRST_FAIL_EXACT_EVIDENCE_UPDATER_REPLICATION_PASS',s)
        self.assertIn('FIRST_FAIL_EXACT_EVIDENCE_UPDATER_REPLICATION_FAIL_STATE_GENERATION_VARIANCE',s)

    def test_analysis_authorization_forbids_followup(self)->None:
        s=(ROOT/'scripts/authorize_e2_r17_first_fail_exact_replay_analysis.py').read_text()
        for marker in ("'scientific_experiment':False","'provider_io':False","'updater':False","'heldout_evaluation':False","'s2_execution':False","'second_backbone':False","'public_benchmark':False","'e3_confirmation':False","'paper_promotion':False","'submission':False"):
            self.assertIn(marker,s)


if __name__=='__main__': unittest.main()
