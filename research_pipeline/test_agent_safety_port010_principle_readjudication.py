from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from .agent_safety_port010_principle_readjudication import build_readjudication, validate_readjudication
from .paper_first_search_portfolio_design_adjudication import _principle_readjudication_rows
from .principle_adjudication import audit_dead_end_counter_explanation


class AgentSafetyPort010PrincipleReadjudicationTest(unittest.TestCase):
    def test_current_immutable_chain_certifies_only_exact_scoped_residual(self):
        state = build_readjudication()
        self.assertEqual(validate_readjudication(state), [])
        self.assertEqual(state["stop_class"], "PRINCIPLE_STOP")
        self.assertTrue(state["principle_dead_end_certified"])
        self.assertFalse(state["benchmark_level_dead_end_certified"])
        self.assertFalse(state["broader_core_principle_falsified"])
        self.assertEqual(state["provenance_status"], "IMMUTABLE_ZERO_PROVIDER_REPLAY_BOUND")
        self.assertEqual(state["replay_binding"]["provider_calls_executed"], 0)
        self.assertTrue(state["replay_binding"]["byte_identical_to_adjudicated_result"])
        counter = state["principle_diagnosis"]["counter_explanation"]
        self.assertTrue(audit_dead_end_counter_explanation(counter)["passed"])
        self.assertIn("framing", counter["statement"].lower())
        self.assertIn("fresh preregistered evidence", counter["reopen_condition"].lower())
        self.assertFalse(state["scientific_interpretation"]["negative_experiment_alone_authorized_dead_end"])
        self.assertFalse(state["scientific_interpretation"]["port013_port014_automatically_closed"])

    def test_compiler_projects_port010_as_core_principle_only(self):
        state = build_readjudication()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "agent-safety-port010-principle-readjudication-20260819.json"
            path.write_text(json.dumps(state), encoding="utf-8")
            rows = _principle_readjudication_rows([path])
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["source_candidate_id"], "PORT-010")
        self.assertEqual(row["failure_layer"], "core_principle")
        self.assertTrue(row["dead_end_certified"])
        self.assertTrue(row["principle_update_allowed"])
        self.assertFalse(row["broader_core_principle_falsified"])
        self.assertFalse(row["scientific_authority"])

    def test_metric_drift_fails_closed(self):
        state = build_readjudication()
        broken = copy.deepcopy(state)
        broken["registered_f0"]["word"]["raw_framed_within_detection_rate"] = 0.94
        self.assertIn("word evidence drift", validate_readjudication(broken))


if __name__ == "__main__":
    unittest.main()
