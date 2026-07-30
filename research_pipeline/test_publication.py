from __future__ import annotations

import unittest

from .publication import DAILY_ARTIFACTS, PUBLICATION_OK_STATES, WEEKLY_ARTIFACTS, _normalize


class PublicationTest(unittest.TestCase):
    def test_volatile_metadata_is_removed_from_digest_input(self) -> None:
        payload = {
            "generated_at": "now",
            "summary": {"papers": 281},
            "automation": {
                "daily": {"schedule": "02:15"},
                "latest_report": {"started_at": "x", "completed_at": "y", "status": "pass"},
            },
            "pilot_registry": {
                "phases": [{"idea_id": "a", "result": {"completed_at": "z", "metrics": {"gain": 1}}}]
            },
        }
        normalized = _normalize(payload, root=True)
        self.assertNotIn("generated_at", normalized)
        self.assertNotIn("latest_report", normalized["automation"])
        self.assertEqual(normalized["pilot_registry"]["phases"][0]["result"]["metrics"]["gain"], 1)
        self.assertNotIn("completed_at", normalized["pilot_registry"]["phases"][0]["result"])

    def test_daily_publication_is_state_only(self) -> None:
        self.assertEqual(
            DAILY_ARTIFACTS,
            ("generated/research-system-state.json", "generated/research-system-state.js"),
        )

    def test_transient_network_deferral_is_non_fatal(self) -> None:
        self.assertIn("deferred", PUBLICATION_OK_STATES)
        self.assertNotIn("blocked", PUBLICATION_OK_STATES)

    def test_weekly_publication_includes_literature_and_banks(self) -> None:
        self.assertTrue(set(DAILY_ARTIFACTS).issubset(WEEKLY_ARTIFACTS))
        self.assertIn("generated/s2-literature.js", WEEKLY_ARTIFACTS)
        self.assertIn("generated/iclr-low-resource-ideas.json", WEEKLY_ARTIFACTS)


if __name__ == "__main__":
    unittest.main()
