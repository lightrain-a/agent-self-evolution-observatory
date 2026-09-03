from __future__ import annotations
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ExactReplayMeasurementTests(unittest.TestCase):
    def test_actor_requires_measurement_only_state_binding(self)->None:
        s=(ROOT/'scripts/run_e2_r17_actor_pool_first_fail_exact_replay_measurement.py').read_text()
        self.assertIn("{'win_c','first_fail'}",s)
        self.assertIn("PREFLIGHT_ONLY_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT",s)
        self.assertIn("AUTHORIZED_E2_R17_FIRST_FAIL_EXACT_REPLAY_MEASUREMENT_ONLY",s)
    def test_actual_path_preflight_stops_before_provider(self)->None:
        s=(ROOT/'scripts/preflight_e2_r17_first_fail_exact_replay_measurement_actual_path.py').read_text()
        self.assertIn("'--stop-before-provider-io'",s)
        self.assertIn("d.get('provider_calls')==0",s)
        self.assertIn("'scientific_outcomes_read':False",s)
    def test_measurement_runner_has_no_updater(self)->None:
        s=(ROOT/'scripts/run_e2_r17_first_fail_exact_replay_measurement.py').read_text()
        self.assertNotIn('run_projection_update',s)
        self.assertIn("'new_learned_states':0",s)
        self.assertIn("'heldout_rollout_units':72",s)
    def test_completion_audit_is_outcome_blind(self)->None:
        s=(ROOT/'scripts/audit_e2_r17_first_fail_exact_replay_measurement_completion.py').read_text()
        self.assertNotIn("ref['score']",s)
        self.assertIn("'scientific_scores_read':False",s)
        self.assertIn("'heldout_rollout_units':72",s)
    def test_analyzer_gate_is_before_score(self)->None:
        s=(ROOT/'scripts/analyze_e2_r17_first_fail_exact_replay_measurement.py').read_text()
        self.assertLess(s.index("req(au.get('status')==AUDIT"),s.index("v=float(ref['score'])"))
        self.assertIn('EPS=1.0/18.0',s)
        self.assertIn('FIRST_FAIL_EXACT_EVIDENCE_UPDATER_REPLICATION_PASS',s)
        self.assertIn('FIRST_FAIL_EXACT_EVIDENCE_UPDATER_REPLICATION_FAIL_STATE_GENERATION_VARIANCE',s)
if __name__=='__main__': unittest.main()
