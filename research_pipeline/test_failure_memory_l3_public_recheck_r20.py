import unittest

from research_pipeline.failure_memory_l3_public_recheck_r20 import build


class TestFailureMemoryL3PublicRecheckR20(unittest.TestCase):
    def test_recheck_keeps_l3_blocked(self):
        d = build()
        self.assertEqual(d["status"], "NO_FIRST_PARTY_FINANCIAL_L3_RELEASE_SURFACE_DELTA_DISCOVERED")
        self.assertFalse(d["adjudication"]["l3_support_unblocked"])
        self.assertFalse(d["availability"]["all_required_l3_surface_available"])

    def test_absence_is_not_scientific_negative(self):
        d = build()
        self.assertFalse(d["adjudication"]["absence_of_public_release_is_scientific_negative"])
        self.assertEqual(d["adjudication"]["scientific_verdict"], "NO_VERDICT_SUPPORT_FAILURE")
        self.assertFalse(any(d["authority"].values()))

    def test_primary_source_remains_v1_with_future_release_statement(self):
        d = build()
        s = d["primary_source_snapshot"]
        self.assertEqual(s["version_observed"], "v1")
        self.assertFalse(s["later_arxiv_version_observed"])
        self.assertIn("released upon publication", s["release_statement"])


if __name__ == "__main__":
    unittest.main()
