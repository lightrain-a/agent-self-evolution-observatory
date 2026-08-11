from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from .ai_consultation_automation import (
    consultation_launch_clearance,
    execute_pending,
    public_state,
    record_finding_disposition,
    sync_triggers,
    write_residual_risk_waiver,
)


class AIConsultationAutomationTest(unittest.TestCase):
    def _storage(self, root: Path):
        return SimpleNamespace(run_dir=root / "runs", site_artifact_dir=root / "generated", ensure=lambda: None)

    def test_first_observation_is_baseline_and_changed_hash_triggers_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            storage = self._storage(Path(tmp))
            first = [{"checkpoint": "idea_premortem", "subject_id": "x", "dossier": {"claim": "v1"}}]
            with patch("research_pipeline.ai_consultation_automation.detect_candidates", return_value=first):
                state, created = sync_triggers(storage)
                self.assertEqual(created, [])
                self.assertTrue(state["baseline_initialized"])
                self.assertEqual(state["baseline_subjects"], 1)
            changed = [{"checkpoint": "idea_premortem", "subject_id": "x", "dossier": {"claim": "v2"}}]
            with patch("research_pipeline.ai_consultation_automation.detect_candidates", return_value=changed):
                state, created = sync_triggers(storage)
                self.assertEqual(len(created), 1)
                _, created_again = sync_triggers(storage)
                self.assertEqual(created_again, [])
                self.assertEqual(len(state["cases"]), 1)

    def test_changed_prelaunch_case_blocks_until_explicit_waiver(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            storage = self._storage(Path(tmp))
            baseline = [{"checkpoint": "pre_launch_stress_review", "subject_id": "x", "dossier": {"plan": "v1"}}]
            with patch("research_pipeline.ai_consultation_automation.detect_candidates", return_value=baseline):
                sync_triggers(storage)
            changed = [{"checkpoint": "pre_launch_stress_review", "subject_id": "x", "dossier": {"plan": "v2"}}]
            with patch("research_pipeline.ai_consultation_automation.detect_candidates", return_value=changed):
                state, created = sync_triggers(storage)
                case_id = created[0]
                case = state["cases"][case_id]
                case["status"] = "complete"
                case["machine_check_requests"] = [{"severity": "high", "disposition": "unresolved"}]
                from .ai_consultation_automation import _atomic_json, _state_path
                _atomic_json(_state_path(storage), state)
                blocked = consultation_launch_clearance(storage, "x")
                self.assertFalse(blocked["pass"])
                self.assertTrue(any("unresolved-high-risk" in item for item in blocked["blockers"]))
                write_residual_risk_waiver(storage, case_id, "accepted because an independent machine gate covers this risk")
                cleared = consultation_launch_clearance(storage, "x")
                self.assertTrue(cleared["pass"])

    def test_machine_disposition_clears_high_risk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            storage = self._storage(Path(tmp))
            baseline = [{"checkpoint": "pre_launch_stress_review", "subject_id": "x", "dossier": {"plan": "v1"}}]
            with patch("research_pipeline.ai_consultation_automation.detect_candidates", return_value=baseline):
                sync_triggers(storage)
            changed = [{"checkpoint": "pre_launch_stress_review", "subject_id": "x", "dossier": {"plan": "v2"}}]
            with patch("research_pipeline.ai_consultation_automation.detect_candidates", return_value=changed):
                state, created = sync_triggers(storage)
                case_id = created[0]
                case = state["cases"][case_id]
                case["status"] = "complete"
                case["machine_check_requests"] = [{"severity": "high", "disposition": "unresolved"}]
                from .ai_consultation_automation import _atomic_json, _state_path
                _atomic_json(_state_path(storage), state)
                result = record_finding_disposition(storage, case_id, 0, "cheap_falsifier_run", "CPU falsifier artifact sha256=abc")
                self.assertEqual(result["unresolved_high_risk"], 0)
                cleared = consultation_launch_clearance(storage, "x")
                self.assertTrue(cleared["pass"])

    def test_reviewer_failure_is_missing_and_ai_never_authorizes_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            storage = self._storage(Path(tmp))
            state = {
                "cases": {
                    "aic-test": {
                        "case_id": "aic-test", "checkpoint": "economy_red_team", "subject_id": "x",
                        "created_at": "2026-08-11T00:00:00+00:00", "status": "pending", "dossier": {},
                    }
                }
            }
            good = {"status": "complete", "reviewer": "glm-5.2", "payload": {"risk_level": "high", "findings": [{"type": "baseline", "severity": "high", "claim": "simple rule may tie", "cheapest_falsifier": "CPU rule fit", "compile_to": "matched_simplification_compiler"}]}}
            missing = {"status": "missing", "reviewer": "web-gpt-current-source-review", "error": "timeout"}
            with patch("research_pipeline.ai_consultation_automation._review_web", return_value=missing), patch("research_pipeline.ai_consultation_automation._review_ark", return_value=good):
                executed = execute_pending(storage, state, max_cases=1, domestic_models=["glm-5.2", "deepseek-v4-pro"])
            self.assertEqual(executed, ["aic-test"])
            case = state["cases"]["aic-test"]
            self.assertEqual(case["status"], "partial")
            self.assertEqual(case["completed_reviewers"], 2)
            self.assertEqual(case["missing_reviewers"], 1)
            self.assertGreater(case["unresolved_high_risk"], 0)
            self.assertFalse(case["execution_authorized"])
            self.assertFalse(case["scientific_authority"])
            public = public_state(state, [], executed)
            self.assertGreater(public["summary"]["unresolved_high_risk"], 0)
            self.assertTrue(public["policy"]["ai_output_never_authorizes_execution"])
            recovered_web = {"status": "complete", "reviewer": "web-gpt-current-source-review", "payload": {"risk_level": "low", "findings": []}}
            with patch("research_pipeline.ai_consultation_automation._review_web", return_value=recovered_web), patch("research_pipeline.ai_consultation_automation._review_ark") as ark:
                execute_pending(storage, state, max_cases=1, domestic_models=["glm-5.2", "deepseek-v4-pro"])
            ark.assert_not_called()
            self.assertEqual(case["status"], "complete")
            self.assertEqual(case["completed_reviewers"], 3)
            self.assertEqual(case["attempt_count"], 2)


if __name__ == "__main__":
    unittest.main()
