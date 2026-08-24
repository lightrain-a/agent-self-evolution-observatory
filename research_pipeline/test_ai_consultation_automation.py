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

    def test_post_screen_dossier_hides_final_diagnosis_from_differential_reviewers(self) -> None:
        from .ai_consultation_automation import _diagnosis_candidates
        synthetic = {
            "experiment_iteration": {
                "nodes": [{
                    "idea_id": "x", "code": "X-1", "qualification_pass": True,
                    "experiment_identifiable": False, "scientific_belief_update_allowed": False,
                    "scale_up_allowed": False, "diagnosis": "inconclusive",
                    "diagnosis_layer": "experiment_identifiability", "evidence": {"trace": "pre"},
                    "repair_children": [{"id": "hidden-repair"}],
                }]
            },
            "mem_xfer_workflow": {},
        }
        with patch("research_pipeline.ai_consultation_automation._load", return_value=synthetic):
            weak, _ = _diagnosis_candidates()
        self.assertEqual(len(weak), 1)
        self.assertNotIn("diagnosis", weak[0]["dossier"])
        self.assertNotIn("diagnosis_layer", weak[0]["dossier"])
        self.assertNotIn("repair_children", weak[0]["dossier"])
        self.assertEqual(weak[0]["single_diagnosis_baseline"]["diagnosis_layer"], "experiment_identifiability")
        self.assertTrue(weak[0]["single_diagnosis_baseline"]["not_exposed_to_differential_reviewers"])

    def test_failure_differential_freezes_before_final_label_then_scores_later(self) -> None:
        from .ai_consultation_automation import _freeze_failure_differential, _sync_failure_differential_scores
        case = {
            "case_id": "aic-prospective", "checkpoint": "post_screen_differential_diagnosis", "subject_id": "x",
            "input_hash": "1" * 64, "status": "complete", "single_diagnosis_baseline": {"diagnosis_layer": "experiment_identifiability"},
            "reviews": {
                "r1": {"status": "complete", "reviewer": "r1", "payload": {"ranked_failure_hypotheses": [
                    {"failure_layer": "experiment_identifiability", "rationale": "support is weak", "repair_route": "repair substrate"},
                    {"failure_layer": "method_realization", "rationale": "simple baseline may absorb", "repair_route": "simplify"},
                ]}},
                "r2": {"status": "complete", "reviewer": "r2", "payload": {"ranked_failure_hypotheses": [
                    {"failure_layer": "method_realization", "rationale": "matched reduction is plausible", "repair_route": "merge"},
                ]}},
                "r3": {"status": "complete", "reviewer": "r3", "payload": {"ranked_failure_hypotheses": [
                    {"failure_layer": "operationalization", "rationale": "measurement bridge may be wrong", "repair_route": "recompile"},
                ]}},
            },
        }
        with patch("research_pipeline.ai_consultation_automation._final_failure_row", return_value={}):
            _freeze_failure_differential(case)
        frozen = case["failure_differential_hypothesis_set"]
        self.assertEqual(frozen["status"], "HYPOTHESIS_SET_FROZEN")
        self.assertTrue(frozen["frozen_before_final_adjudication"])
        self.assertFalse(frozen["scientific_authority"])
        state = {"cases": {"aic-prospective": case}}
        final = {"failure_layer": "method_realization", "failure_evidence": {"evidence_sha256": "a" * 64}}
        with patch("research_pipeline.ai_consultation_automation._final_failure_row", return_value=final):
            _sync_failure_differential_scores(state)
        score = case["failure_differential_score"]
        self.assertEqual(score["status"], "PROSPECTIVE_CASE_SCORED")
        self.assertTrue(score["topk_contains_truth"])
        self.assertTrue(score["top1_correct"])
        self.assertFalse(score["single_diagnosis_correct"])
        self.assertFalse(score["scientific_authority"])

    def test_old_final_label_is_snapshotted_and_cannot_score_a_new_case(self) -> None:
        from .ai_consultation_automation import _freeze_failure_differential, _sync_failure_differential_scores
        case = {
            "case_id": "aic-new-cycle", "checkpoint": "post_screen_differential_diagnosis", "subject_id": "x",
            "input_hash": "2" * 64, "status": "complete",
            "reviews": {"r1": {"status": "complete", "reviewer": "r1", "payload": {"ranked_failure_hypotheses": [
                {"failure_layer": "method_realization", "rationale": "baseline absorbs", "repair_route": "merge"}
            ]}}},
        }
        old_final = {
            "failure_layer": "method_realization", "failure_class": "METHOD_FAIL", "decision_source": "old-cycle",
            "p0_decision": "OLD", "failure_evidence": {"evidence_sha256": "b" * 64},
        }
        with patch("research_pipeline.ai_consultation_automation._final_failure_row", return_value=old_final):
            _freeze_failure_differential(case)
        self.assertEqual(case["failure_differential_hypothesis_set"]["status"], "HYPOTHESIS_SET_FROZEN")
        self.assertEqual(case["failure_differential_status"], "HYPOTHESIS_SET_FROZEN_WAIT_NEW_FINAL_EVIDENCE")
        state = {"cases": {"aic-new-cycle": case}}
        with patch("research_pipeline.ai_consultation_automation._final_failure_row", return_value=old_final):
            _sync_failure_differential_scores(state)
        self.assertNotIn("failure_differential_score", case)
        new_final = {**old_final, "decision_source": "new-cycle", "p0_decision": "NEW", "failure_evidence": {"evidence_sha256": "c" * 64}}
        with patch("research_pipeline.ai_consultation_automation._final_failure_row", return_value=new_final):
            _sync_failure_differential_scores(state)
        self.assertEqual(case["failure_differential_score"]["status"], "PROSPECTIVE_CASE_SCORED")
        self.assertTrue(case["failure_differential_score"]["final_failure_identity_differs_from_freeze"])

    def test_partial_panel_does_not_freeze_failure_hypotheses(self) -> None:
        from .ai_consultation_automation import _freeze_failure_differential
        case = {"case_id": "aic-partial", "checkpoint": "post_screen_differential_diagnosis", "subject_id": "x", "status": "partial"}
        _freeze_failure_differential(case)
        self.assertEqual(case["failure_differential_status"], "WAIT_COMPLETE_INDEPENDENT_PANEL")
        self.assertNotIn("failure_differential_hypothesis_set", case)

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
