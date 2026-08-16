from __future__ import annotations

import unittest
from unittest.mock import patch

from .publication import (
    DAILY_ARTIFACTS,
    PUBLICATION_OK_STATES,
    WEEKLY_ARTIFACTS,
    _normalize,
    _normalized_text_digest,
    _push_with_timeout,
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
                "generated/emerging-niche-policy.json",
                "generated/ai-consultation-clinic.json",
                "generated/ai-consultation-clinic.js",
                "generated/ai-consultation-automation.json",
                "generated/ai-consultation-automation.js",
                "generated/emerging-niche-policy.js",
                "generated/human-terminal-idea-state.json",
                "generated/human-terminal-idea-state.js",
                "generated/p0-admission-state.json",
                "generated/p0-admission-state.js",
                "generated/p0-decision-ledger.json",
                "generated/p0-decision-ledger.js",
                "generated/research-governance-v2.json",
                "generated/research-governance-v2.js",
                "generated/p0-offline-qualification.json",
                "generated/p0-offline-qualification.js",
                "generated/p0-realizability-suite.json",
                "generated/p0-realizability-suite.js",
                "generated/p0-revived-batch-f0.json",
                "generated/p0-revived-batch-f0.js",
                "generated/p0-b10-cpu.json",
                "generated/p0-b10-cpu.js",
                "generated/p0-a1-soft-audit-f0.json",
                "generated/p0-a1-soft-audit-f0.js",
                "generated/p0-a2-evidence-depth-f0.json",
                "generated/p0-a2-evidence-depth-f0.js",
                "generated/p0-a3-substrate-stop.json",
                "generated/p0-a3-substrate-stop.js",
                "generated/p0-a4-composition-cpu.json",
                "generated/p0-a4-composition-cpu.js",
                "generated/p0-a5-history-cpu.json",
                "generated/p0-a5-history-cpu.js",
                "generated/p0-a6-cpu.json",
                "generated/p0-a6-cpu.js",
                "generated/p0-a7-counterfactual-cpu.json",
                "generated/p0-a7-counterfactual-cpu.js",
                "generated/p0-b2-support-stop.json",
                "generated/p0-b2-support-stop.js",
                "generated/p0-b3-interference-cpu.json",
                "generated/p0-b3-interference-cpu.js",
                "generated/p0-b3-fresh-support-stop.json",
                "generated/p0-b3-fresh-support-stop.js",
                "generated/p0-b3-real-cinteraction.json",
                "generated/p0-b3-real-cinteraction.js",
                "generated/p0-b5-applicability-cpu.json",
                "generated/p0-b5-applicability-cpu.js",
                "generated/p0-b6-memory-utility-cpu.json",
                "generated/p0-b6-memory-utility-cpu.js",
                "generated/p0-c2-evaluator-cpu.json",
                "generated/p0-c2-evaluator-cpu.js",
                "generated/p0-d1-minimal-curriculum-cpu.json",
                "generated/p0-d1-minimal-curriculum-cpu.js",
                "generated/p0-e1-edit-table-stop.json",
                "generated/p0-e1-edit-table-stop.js",
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
                "generated/asset-first-stri-paper-quality-v2-20260816.json",
                "generated/paper-first-p0-f0-state.json",
                "generated/paper-first-p0-f0-state.js",
                "generated/paper-first-design-adjudication.json",
                "generated/paper-first-design-adjudication.js",
                "generated/paper-first-pf1-problem-adjudication.json",
                "generated/paper-first-pf1-problem-adjudication.js",
                "generated/paper-first-pf2-method-adjudication.json",
                "generated/paper-first-pf2-method-adjudication.js",
                "generated/paper-first-pf357-problem-adjudication.json",
                "generated/paper-first-pf357-problem-adjudication.js",
                "generated/paper-first-fresh-saturation.json",
                "generated/paper-first-fresh-saturation.js",
                "generated/paper-first-primary-evidence-state.json",
                "generated/paper-first-primary-evidence-state.js",
                "generated/paper-first-problem-generator-state.json",
                "generated/paper-first-problem-generator-state.js",
                "generated/paper-first-problem-gate-queue.json",
                "generated/paper-first-problem-gate-queue.js",
                "generated/paper-first-search-portfolio-design-adjudication.json",
                "generated/paper-first-search-portfolio-design-adjudication.js",
                "generated/paper-first-sp15-identifiability-support.json",
                "generated/paper-first-sp15-identifiability-support.js",
                "generated/paper-first-paper-design-backlog.json",
                "generated/paper-first-paper-design-backlog.js",
                "generated/paper-first-post-c2-adjudication.json",
                "generated/paper-first-post-c2-adjudication.js",
                "generated/paper-first-premature-method-diagnostics.json",
                "generated/paper-first-premature-method-diagnostics.js",
            ),
        )

    def test_transient_network_deferral_is_non_fatal(self) -> None:
        self.assertIn("deferred", PUBLICATION_OK_STATES)
        self.assertNotIn("blocked", PUBLICATION_OK_STATES)

    def test_publication_pushes_current_checkout_head_to_main(self) -> None:
        with patch("research_pipeline.publication._run") as run:
            _push_with_timeout()
        args=run.call_args.args
        self.assertEqual(args[:7],("git","-c","http.proxy=","-c","https.proxy=","push","origin"))
        self.assertEqual(args[7],"HEAD:main")

    def test_weekly_publication_includes_literature_and_banks(self) -> None:
        self.assertTrue(set(DAILY_ARTIFACTS).issubset(WEEKLY_ARTIFACTS))
        self.assertIn("generated/s2-literature.js", WEEKLY_ARTIFACTS)
        self.assertIn("generated/iclr-low-resource-ideas.json", WEEKLY_ARTIFACTS)
        self.assertIn("generated/paper-first-paper-design-backlog.json", DAILY_ARTIFACTS)
        for artifact in (
            "generated/paper-first-problem-search-portfolio-state.json",
            "generated/paper-first-problem-search-portfolio-state.js",
            "generated/paper-first-problem-search-portfolio-queue-shadow.json",
            "generated/paper-first-problem-search-portfolio-queue-shadow.js",
        ):
            self.assertIn(artifact, WEEKLY_ARTIFACTS)
            self.assertNotIn(artifact, DAILY_ARTIFACTS)
        self.assertIn("generated/paper-first-global-relation-recall.json", WEEKLY_ARTIFACTS)
        self.assertNotIn("generated/paper-first-global-relation-recall.json", DAILY_ARTIFACTS)
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
