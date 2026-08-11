from __future__ import annotations

import unittest

from .publication import (
    DAILY_ARTIFACTS,
    PUBLICATION_OK_STATES,
    WEEKLY_ARTIFACTS,
    _normalize,
    _normalized_text_digest,
)


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

    def test_generated_js_digest_ignores_volatile_cycle_metadata(self) -> None:
        left = 'window.RESEARCH_SYSTEM_STATE = {"generated_at":"a","automation":{"daily":{"schedule":"02:15"},"latest_report":{"status":"pass","completed_at":"a"}},"lineage":{"nodes":[{"created_at":"a","id":"idea-a"}]},"pilot_registry":{"phases":[{"metrics":{"gain":1}}]}};\n'
        right = 'window.RESEARCH_SYSTEM_STATE = {"generated_at":"b","automation":{"daily":{"schedule":"02:15"},"latest_report":{"status":"deferred","completed_at":"b"}},"lineage":{"nodes":[{"created_at":"b","id":"idea-a"}]},"pilot_registry":{"phases":[{"metrics":{"gain":1}}]}};\n'
        changed = 'window.RESEARCH_SYSTEM_STATE = {"generated_at":"b","automation":{"daily":{"schedule":"02:15"},"latest_report":{"status":"pass","completed_at":"b"}},"lineage":{"nodes":[{"created_at":"b","id":"idea-a"}]},"pilot_registry":{"phases":[{"metrics":{"gain":2}}]}};\n'
        self.assertEqual(
            _normalized_text_digest("generated/research-system-state.js", left),
            _normalized_text_digest("generated/research-system-state.js", right),
        )
        self.assertNotEqual(
            _normalized_text_digest("generated/research-system-state.js", left),
            _normalized_text_digest("generated/research-system-state.js", changed),
        )

    def test_daily_publication_is_state_only(self) -> None:
        self.assertEqual(
            DAILY_ARTIFACTS,
            (
                "generated/human-terminal-idea-state.json",
                "generated/human-terminal-idea-state.js",
                "generated/p0-admission-state.json",
                "generated/p0-admission-state.js",
                "generated/p0-offline-qualification.json",
                "generated/p0-offline-qualification.js",
                "generated/p0-realizability-suite.json",
                "generated/p0-realizability-suite.js",
                "generated/p0-b10-cpu.json",
                "generated/p0-b10-cpu.js",
                "generated/p0-a5-history-cpu.json",
                "generated/p0-a5-history-cpu.js",
                "generated/p0-a6-cpu.json",
                "generated/p0-a6-cpu.js",
                "generated/p0-a7-counterfactual-cpu.json",
                "generated/p0-a7-counterfactual-cpu.js",
                "generated/p0-b3-interference-cpu.json",
                "generated/p0-b3-interference-cpu.js",
                "generated/p0-e2-workflow-cpu.json",
                "generated/p0-e2-workflow-cpu.js",
                "generated/p0-e3-real-api.json",
                "generated/p0-e3-real-api.js",
                "generated/p0-e3-stateful.json",
                "generated/p0-e3-stateful.js",
                "generated/p0-e4-permission-cpu.json",
                "generated/p0-e4-permission-cpu.js",
                "generated/research-system-state.json",
                "generated/research-system-state.js",
            ),
        )

    def test_transient_network_deferral_is_non_fatal(self) -> None:
        self.assertIn("deferred", PUBLICATION_OK_STATES)
        self.assertNotIn("blocked", PUBLICATION_OK_STATES)

    def test_weekly_publication_includes_literature_and_banks(self) -> None:
        self.assertTrue(set(DAILY_ARTIFACTS).issubset(WEEKLY_ARTIFACTS))
        self.assertIn("generated/s2-literature.js", WEEKLY_ARTIFACTS)
        self.assertIn("generated/iclr-low-resource-ideas.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/machine-school-inspired-ideas.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/machine-school-external-reviews.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/idea-discovery-v3.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/idea-discovery-v3-external-reviews.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/idea-discovery-v31.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/idea-discovery-v31-external-reviews.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/idea-discovery-v4.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/idea-discovery-v4-external-reviews.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/idea-discovery-v5.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/idea-discovery-v5-external-reviews.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/idea-discovery-v51-external-reviews.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/idea-discovery-v52-external-reviews.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/idea-discovery-v53-external-reviews.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/discussion-ready-ideas.json", WEEKLY_ARTIFACTS)


if __name__ == "__main__":
    unittest.main()
