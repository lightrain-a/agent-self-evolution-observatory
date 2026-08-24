import unittest

from research_pipeline.failure_memory_reasoningbank_r19_authority_packet import build


class TestR19AuthorityPacket(unittest.TestCase):
    def test_packet_is_not_authority(self):
        d = build()
        self.assertEqual(d["status"], "R19_AUTHORITY_DECISION_PACKET_READY_NOT_AUTHORIZED")
        self.assertFalse(any(d["current_authority"].values()))
        self.assertIn("generic continuation language", d["not_authorized_by"])

    def test_scope_matches_frozen_budget(self):
        d = build()
        s = d["exact_scope_if_authorized"]
        self.assertEqual(s["independent_tasks"], 35)
        self.assertEqual(s["terminal_episodes"], 140)
        self.assertEqual(s["maximum_new_local_model_completions"], 4802)

    def test_r18_retry_is_not_authorized(self):
        d = build()
        self.assertTrue(d["decision_context"]["R18_attempt_consumed_and_not_retriable"])
        self.assertIn("Do not authorize R18 retry", d["authorization_text_for_human_decision"])


if __name__ == "__main__":
    unittest.main()
