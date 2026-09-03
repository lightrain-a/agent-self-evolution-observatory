from __future__ import annotations

import unittest

try:
    from research_pipeline.failure_memory_provenance_governance_method_r27 import build
except ModuleNotFoundError:
    from failure_memory_provenance_governance_method_r27 import build


class TestFailureMemoryProvenanceGovernanceMethodR27(unittest.TestCase):
    def test_method_closes_problem_without_prejudging_direction(self):
        d = build()
        self.assertEqual(d["method"]["short_name"], "PSMG")
        self.assertIn("phenomenon -> causal identification -> provenance-separated governance", d["problem_to_method_loop"]["paper_story"])
        self.assertTrue(d["claim_boundary"]["R27_does_not_assume_R19_direction"])
        self.assertIn("No universal hard blacklist", d["method"]["default_rule"])

    def test_new_mitigation_execution_remains_blocked(self):
        d = build()
        self.assertFalse(d["future_decisive_experiment_if_separately_authorized"]["execution_authorized_now"])
        self.assertTrue(all(v is False for v in d["authority"].values()))
        self.assertTrue(d["novelty_boundary"]["closest_work_audit_required_before_novelty_claim"])


if __name__ == "__main__":
    unittest.main()
