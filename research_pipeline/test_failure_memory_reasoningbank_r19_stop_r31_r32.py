from __future__ import annotations

import json
import unittest
from pathlib import Path

R31 = Path("generated/d2-failure-memory-provenance-l2b-r19-seq029-preexposure-retry-exhaustion-r31.json")
R32 = Path("generated/d2-failure-memory-provenance-l2b-r19-public-stop-r32.json")


class TestR19StopR31R32(unittest.TestCase):
    def test_r31_exhausts_retry_and_stops_current_attempt(self) -> None:
        d = json.loads(R31.read_text(encoding="utf-8"))
        self.assertEqual(d["status"], "SEQ029_PREEXPOSURE_SUPPORT_FAILURE_EXACT_RETRY_EXHAUSTED_R19_STOPPED")
        self.assertEqual(d["scientific_verdict"], "NO_VERDICT_PREOUTCOME_SUPPORT_FAILURE_RETRY_EXHAUSTED")
        self.assertTrue(d["support_failure_chain"]["exact_retry_consumed"])
        self.assertFalse(d["support_failure_chain"]["additional_retry_permitted"])
        self.assertTrue(d["adjudication"]["current_R19_confirmatory_execution_stopped"])
        self.assertFalse(d["adjudication"]["resume_sequence29_under_current_R19"])
        self.assertFalse(d["adjudication"]["execute_sequence30_or_later_under_current_R19"])
        self.assertFalse(d["adjudication"]["partial_29_episode_prefix_may_enter_confirmatory_analysis"])
        self.assertFalse(d["adjudication"]["support_failure_is_scientific_negative"])

    def test_r32_public_stop_has_no_interim_inference_or_resume(self) -> None:
        d = json.loads(R32.read_text(encoding="utf-8"))
        self.assertEqual(d["status"], "R19_CONFIRMATORY_EXECUTION_STOPPED_RETRY_EXHAUSTED_NO_VERDICT")
        self.assertEqual(d["stopped_partial_prefix"]["episodes_complete"], 29)
        self.assertEqual(d["stopped_partial_prefix"]["complete_independent_tasks"], 7)
        self.assertEqual(d["stopped_partial_prefix"]["current_incomplete_task_completed_episodes"], 1)
        self.assertFalse(d["current_R19"]["resume_permitted"])
        self.assertFalse(d["current_R19"]["current_attempt_retriable"])
        self.assertFalse(d["interim_policy"]["partial_prefix_confirmatory_analysis_permitted"])
        for key in ["terminal_scores_exposed_in_projection", "task_deltas_computed", "effect_mean_computed", "p_value_computed", "confidence_interval_computed", "claim_update_allowed", "no_effect_claim_authorized"]:
            self.assertFalse(d["interim_policy"][key])
        self.assertTrue(all(v is False for v in d["redaction"].values()))

    def test_public_stop_contains_no_private_path_or_authority_source(self) -> None:
        text = R32.read_text(encoding="utf-8")
        for needle in ["/data/", "/home/", "wyt@", "192.168.", "source_message_ref", "source_message_sha256"]:
            self.assertNotIn(needle, text)


if __name__ == "__main__":
    unittest.main()
