from __future__ import annotations

import unittest

from research_pipeline.agent_constraint_externality_execution_readiness_v2 import build, check


class ExecutionReadinessV2Test(unittest.TestCase):
    def test_sequence_is_explicit_and_authority_false(self):
        payload = build()
        check(payload)
        self.assertEqual(payload["status"], "EXECUTION_SEQUENCE_MECHANICALLY_CLOSED_AUTHORITY_FALSE")
        self.assertTrue(all(v is False for v in payload["authority"].values()))
        stages = [x["stage"] for x in payload["execution_sequence"]]
        self.assertLess(stages.index("TARGET_ONLY_VERIFICATION"), stages.index("RQ1_RQ2_LOCKED_PANEL_EXECUTION"))
        self.assertLess(stages.index("CONFIRMATORY_PANEL_FREEZE"), stages.index("RQ1_RQ2_LOCKED_PANEL_EXECUTION"))
        self.assertLess(stages.index("SHAM_ARTIFACT_AND_SUBSET_FREEZE"), stages.index("RQ1_RQ2_LOCKED_PANEL_EXECUTION"))

    def test_rq1_rq2_collect_once_analyze_sequentially(self):
        payload = build()
        by_stage = {x["stage"]: x for x in payload["execution_sequence"]}
        self.assertTrue(by_stage["RQ1_RQ2_LOCKED_PANEL_EXECUTION"]["collect_once_analyze_sequentially"])
        self.assertFalse(by_stage["RQ1_RQ2_LOCKED_PANEL_EXECUTION"]["post_treatment_target_filtering"])
        self.assertTrue(by_stage["RQ2_ANALYSIS_IF_RQ1_PASS"]["uses_same_locked_panel_outcomes"])
        self.assertEqual(by_stage["RQ1_ANALYSIS_GATE"]["new_actor_episodes"], 0)
        self.assertEqual(by_stage["RQ2_ANALYSIS_IF_RQ1_PASS"]["new_actor_episodes"], 0)

    def test_readiness_does_not_create_scientific_work(self):
        payload = build()
        self.assertEqual(payload["scientific_provider_calls_created"], 0)
        self.assertEqual(payload["scientific_outcomes_created"], 0)
        self.assertEqual(
            payload["next_legal_action"],
            "EXPLICIT_SEPARATE_HUMAN_AUTHORITY_FOR_PROVIDER_READINESS_ONLY; SCIENTIFIC DISPATCH REMAINS CLOSED",
        )


if __name__ == "__main__":
    unittest.main()
