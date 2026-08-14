from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from .automation_cycle import _advisory_step, _run_external_system_learning_review, _run_global_relation_control, _run_shadow_search_admission_control, _step, _sync_literature, cycle_lock, run_cycle


class AutomationCycleAIConsultationTest(unittest.TestCase):
    def test_orphan_pid_cycle_lock_is_reclaimed_immediately(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            lock=Path(td)/"cycle.lock"; lock.write_text(json.dumps({"pid":12345,"started_at":"old"}),encoding="utf-8")
            with patch("research_pipeline.automation_cycle.os.kill",side_effect=ProcessLookupError):
                with cycle_lock(lock):
                    self.assertTrue(lock.exists())
            self.assertFalse(lock.exists())

    def test_live_pid_cycle_lock_still_blocks_concurrent_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            lock=Path(td)/"cycle.lock"; lock.write_text(json.dumps({"pid":12345,"started_at":"active"}),encoding="utf-8")
            with patch("research_pipeline.automation_cycle.os.kill",return_value=None):
                with self.assertRaises(RuntimeError):
                    with cycle_lock(lock):
                        pass

    def test_missing_s2_key_degrades_to_arxiv_primary_fallback_without_calling_s2(self) -> None:
        settings=SimpleNamespace(api_key="")
        with patch("research_pipeline.automation_cycle.SemanticScholarSettings.from_env", return_value=settings), patch("research_pipeline.automation_cycle.sync_semantic_scholar") as sync:
            result=_sync_literature()
        self.assertEqual(result["status"],"SKIPPED_PROVIDER_UNCONFIGURED")
        self.assertEqual(result["fallback"],"paper-first-primary-evidence will use low-rate arXiv primary discovery")
        self.assertFalse(result["scientific_authority"])
        sync.assert_not_called()

    def test_cycle_places_ai_consultation_between_pre_state_and_final_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            storage = SimpleNamespace(run_dir=root / "runs", lock_dir=root / "locks", ensure=lambda: None)
            def fake_step(name, function):
                return {"name": name, "status": "pass", "duration_seconds": 0.0, "summary": {}}
            with patch("research_pipeline.automation_cycle.StorageSettings.from_env", return_value=storage), patch("research_pipeline.automation_cycle._step", side_effect=fake_step):
                report = run_cycle(mode="daily", ai_consultations=True, ai_consultation_limit=1, publish=False)
            names = [row["name"] for row in report["steps"]]
            self.assertIn("ai-consultation-automation", names)
            self.assertIn("paper-first-fresh-saturation", names)
            self.assertNotIn("paper-first-problem-gate-queue", names)
            self.assertNotIn("paper-first-primary-evidence-refresh", names)
            self.assertNotIn("paper-first-problem-generator", names)
            self.assertIn("paper-first-relation-cache-maintenance", names)
            self.assertNotIn("paper-first-relation-cache-backfill", names)
            self.assertNotIn("paper-first-global-relation-recall", names)
            self.assertNotIn("paper-first-scientific-object-shadow-maintenance", names)
            self.assertNotIn("paper-first-support-release-watch", names)
            self.assertLess(names.index("paper-first-fresh-saturation"), names.index("paper-first-relation-cache-maintenance"))
            self.assertLess(names.index("paper-first-relation-cache-maintenance"), names.index("human-terminal-idea-state"))
            self.assertLess(names.index("research-system-pre-ai"), names.index("ai-consultation-automation"))
            self.assertLess(names.index("ai-consultation-automation"), names.index("research-system-state"))
            self.assertEqual(report["ai_consultation_limit"], 1)
            self.assertTrue(report["ai_consultations"])

    def test_weekly_web_cycle_includes_external_system_learning_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            storage = SimpleNamespace(run_dir=root / "runs", lock_dir=root / "locks", ensure=lambda: None)
            def fake_step(name, function):
                return {"name": name, "status": "pass", "duration_seconds": 0.0, "summary": {}}
            with patch("research_pipeline.automation_cycle.StorageSettings.from_env", return_value=storage), patch("research_pipeline.automation_cycle._step", side_effect=fake_step), patch("research_pipeline.automation_cycle._advisory_step", side_effect=fake_step):
                report = run_cycle(mode="weekly", web_review_limit=1, ai_consultations=False, publish=False)
            names = [row["name"] for row in report["steps"]]
            self.assertIn("external-research-system-learning-review", names)
            self.assertIn("project-web-gpt-repair-review", names)
            self.assertIn("paper-first-fresh-saturation", names)
            self.assertIn("paper-first-discovery-transaction", names)
            self.assertIn("paper-first-shadow-search-admission", names)
            self.assertIn("paper-first-scientific-object-shadow-maintenance", names)
            self.assertIn("paper-first-support-release-watch", names)
            self.assertIn("paper-first-relation-cache-backfill", names)
            self.assertIn("paper-first-global-relation-recall", names)
            self.assertNotIn("paper-first-primary-evidence-refresh", names)
            self.assertNotIn("paper-first-problem-generator", names)
            self.assertNotIn("paper-first-problem-gate-queue", names)
            self.assertIn("historical-paper-first-idea-incubation", names)
            self.assertIn("archival-solution-first-idea-discovery-v3", names)
            self.assertNotIn("solution-first-idea-discovery-v3", names)
            self.assertLess(names.index("paper-first-fresh-saturation"), names.index("paper-first-discovery-transaction"))
            self.assertLess(names.index("paper-first-discovery-transaction"), names.index("paper-first-shadow-search-admission"))
            self.assertLess(names.index("paper-first-shadow-search-admission"), names.index("paper-first-scientific-object-shadow-maintenance"))
            self.assertLess(names.index("paper-first-scientific-object-shadow-maintenance"), names.index("paper-first-support-release-watch"))
            self.assertLess(names.index("paper-first-support-release-watch"), names.index("paper-first-relation-cache-backfill"))
            self.assertLess(names.index("paper-first-relation-cache-backfill"), names.index("paper-first-global-relation-recall"))
            self.assertLess(names.index("paper-first-global-relation-recall"), names.index("archival-solution-first-idea-discovery-v3"))
            self.assertLess(names.index("paper-first-discovery-transaction"), names.index("historical-paper-first-idea-incubation"))
            self.assertLess(names.index("external-research-system-learning-review"), names.index("project-web-gpt-repair-review"))

    def test_shadow_search_admission_step_never_creates_qualification_or_model_authority(self) -> None:
        admission={"schema_version":"1.0","status":"READY_FOR_SHADOW_QUALIFICATION","reason":"new source","policy":{"scientific_authority":False},"summary":{"qualification_allowed":True,"automatic_provider_calls_authorized":0},"source_identity":{},"scientific_authority":False}
        with patch("research_pipeline.automation_cycle.build_shadow_search_admission",return_value=admission), patch("research_pipeline.automation_cycle.public_shadow_search_admission_summary",return_value=dict(admission)):
            result=_run_shadow_search_admission_control()
        self.assertEqual(result["status"],"READY_FOR_SHADOW_QUALIFICATION")
        self.assertFalse(result["model_calls_authorized"])
        self.assertFalse(result["qualification_created"])
        self.assertTrue(result["handoff"]["required"])
        self.assertEqual(result["handoff"]["role"],"canonical-private-pool-shadow-qualifier")
        self.assertEqual(result["handoff"]["launcher_entrypoint"],"research_pipeline.problem_search_shadow_launcher")
        self.assertTrue(result["summary"]["handoff_required"])
        self.assertEqual(result["summary"]["handoff_role"],"canonical-private-pool-shadow-qualifier")
        self.assertEqual(result["summary"]["handoff_launcher_entrypoint"],"research_pipeline.problem_search_shadow_launcher")
        self.assertEqual(result["summary"]["handoff_provider_calls_authorized"],0)
        self.assertFalse(result["summary"]["handoff_automatic_remote_execution_authorized"])
        self.assertFalse(result["handoff"]["provider_calls_authorized"])
        self.assertFalse(result["handoff"]["automatic_remote_execution_authorized"])
        self.assertFalse(result["handoff"]["scientific_authority"])
        self.assertFalse(result["scientific_authority"])

    def test_shadow_search_skip_emits_no_cross_host_handoff(self) -> None:
        admission={"schema_version":"1.0","status":"SKIPPED_SHADOW_SOURCE_TRANSACTION_ALREADY_TERMINAL","reason":"same source","policy":{"scientific_authority":False},"summary":{"qualification_allowed":False,"automatic_provider_calls_authorized":0},"source_identity":{},"scientific_authority":False}
        with patch("research_pipeline.automation_cycle.build_shadow_search_admission",return_value=admission), patch("research_pipeline.automation_cycle.public_shadow_search_admission_summary",return_value=dict(admission)):
            result=_run_shadow_search_admission_control()
        self.assertFalse(result["handoff"]["required"])
        self.assertEqual(result["handoff"]["role"],"none")
        self.assertEqual(result["handoff"]["launcher_entrypoint"],"")
        self.assertFalse(result["summary"]["handoff_required"])
        self.assertEqual(result["summary"]["handoff_role"],"none")
        self.assertEqual(result["summary"]["handoff_launcher_entrypoint"],"")
        self.assertFalse(result["model_calls_authorized"])
        self.assertFalse(result["qualification_created"])

    def test_shadow_handoff_survives_cycle_step_summary_compaction(self) -> None:
        admission={"schema_version":"1.0","status":"READY_FOR_SHADOW_QUALIFICATION","reason":"new source","policy":{"scientific_authority":False},"summary":{"qualification_allowed":True,"automatic_provider_calls_authorized":0},"source_identity":{},"scientific_authority":False}
        with patch("research_pipeline.automation_cycle.build_shadow_search_admission",return_value=admission), patch("research_pipeline.automation_cycle.public_shadow_search_admission_summary",return_value=dict(admission)):
            step=_step("paper-first-shadow-search-admission",_run_shadow_search_admission_control)
        self.assertEqual(step["status"],"pass")
        self.assertTrue(step["summary"]["handoff_required"])
        self.assertEqual(step["summary"]["handoff_role"],"canonical-private-pool-shadow-qualifier")
        self.assertEqual(step["summary"]["handoff_launcher_entrypoint"],"research_pipeline.problem_search_shadow_launcher")
        self.assertEqual(step["summary"]["handoff_provider_calls_authorized"],0)
        self.assertFalse(step["summary"]["handoff_automatic_remote_execution_authorized"])

    def test_global_relation_scan_is_deferred_by_default_without_model_writer(self) -> None:
        storage=SimpleNamespace()
        freshness={"status":"STALE_RELATION_UNIVERSE","summary":{"model_scan_deferred":True},"scientific_authority":False}
        delta={"status":"RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE","summary":{"new_reviewed_sources":12,"new_failure_sources":11,"model_scan_authorized":False},"pair_slots":{},"interpretation":{},"scientific_authority":False}
        writer=Mock()
        delta_writer=Mock(return_value=delta)
        admission={"status":"ELIGIBLE_FOR_EXPLICIT_MANUAL_RELATION_SCAN","summary":{"manual_scan_eligible":True},"failed_checks":[],"scientific_authority":False}
        admission_builder=Mock(return_value=admission)
        with patch("research_pipeline.automation_cycle.load_primary_evidence_state",return_value={}), patch("research_pipeline.automation_cycle.load_problem_generator_state",return_value={}), patch("research_pipeline.automation_cycle.load_global_relation_recall_state",return_value={}), patch("research_pipeline.automation_cycle.relation_recall_freshness",return_value=freshness):
            result=_run_global_relation_control(storage=storage,mode="weekly",allow_model_scan=False,relation_writer=writer,delta_writer=delta_writer,admission_builder=admission_builder)
        self.assertEqual(result["status"],"DEFERRED_RELATION_MODEL_SCAN")
        self.assertEqual(result["freshness"],freshness)
        self.assertFalse(result["model_calls_authorized"])
        self.assertFalse(result["scientific_authority"])
        self.assertEqual(result["manual_scan_admission"],admission)
        self.assertEqual(result["delta_preflight"]["summary"]["new_reviewed_sources"],12)
        self.assertFalse(result["delta_preflight"]["policy"]["pair_slots_are_not_lane_valid_pairs"] is False)
        writer.assert_not_called(); delta_writer.assert_called_once_with(storage=storage); admission_builder.assert_called_once()

    def test_global_relation_model_scan_requires_explicit_manual_mode(self) -> None:
        with self.assertRaises(ValueError):
            run_cycle(mode="weekly",global_relation_model_scan=True,publish=False)
        storage=SimpleNamespace()
        freshness={"status":"STALE_RELATION_UNIVERSE","scientific_authority":False}
        writer=Mock(return_value={"status":"GLOBAL_RELATION_RECALL_COMPLETE","scientific_authority":False})
        delta_writer=Mock(return_value={"status":"RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE","summary":{"new_reviewed_sources":12},"pair_slots":{},"interpretation":{},"scientific_authority":False})
        admission={"status":"ELIGIBLE_FOR_EXPLICIT_MANUAL_RELATION_SCAN","summary":{"manual_scan_eligible":True},"failed_checks":[],"scientific_authority":False}
        admission_builder=Mock(return_value=admission)
        with patch("research_pipeline.automation_cycle.load_primary_evidence_state",return_value={}), patch("research_pipeline.automation_cycle.load_problem_generator_state",return_value={}), patch("research_pipeline.automation_cycle.load_global_relation_recall_state",return_value={}), patch("research_pipeline.automation_cycle.relation_recall_freshness",return_value=freshness):
            result=_run_global_relation_control(storage=storage,mode="manual",allow_model_scan=True,relation_writer=writer,delta_writer=delta_writer,admission_builder=admission_builder)
        self.assertEqual(result["status"],"GLOBAL_RELATION_RECALL_COMPLETE")
        self.assertEqual(result["delta_preflight"]["summary"]["new_reviewed_sources"],12)
        self.assertEqual(result["manual_scan_admission"],admission)
        writer.assert_called_once_with(storage=storage,explicit_manual_scan_intent=True); delta_writer.assert_called_once_with(storage=storage); admission_builder.assert_called_once()

    def test_manual_relation_scan_is_blocked_before_writer_when_admission_fails(self) -> None:
        storage=SimpleNamespace(); writer=Mock(); delta_writer=Mock(return_value={"status":"RELATION_DELTA_TYPED_PREFLIGHT_COMPLETE","summary":{},"pair_slots":{},"interpretation":{},"scientific_authority":False})
        admission_builder=Mock(return_value={"status":"HOLD_MANUAL_RELATION_SCAN","summary":{"manual_scan_eligible":False},"failed_checks":["new-typed-evidence-delta-nonzero"],"scientific_authority":False})
        with patch("research_pipeline.automation_cycle.load_primary_evidence_state",return_value={}), patch("research_pipeline.automation_cycle.load_problem_generator_state",return_value={}), patch("research_pipeline.automation_cycle.load_global_relation_recall_state",return_value={}), patch("research_pipeline.automation_cycle.relation_recall_freshness",return_value={}):
            with self.assertRaisesRegex(RuntimeError,"admission blocked"):
                _run_global_relation_control(storage=storage,mode="manual",allow_model_scan=True,relation_writer=writer,delta_writer=delta_writer,admission_builder=admission_builder)
        writer.assert_not_called()

    def test_external_system_learning_is_bounded_delta_scan_with_dedicated_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            storage=SimpleNamespace(run_dir=Path(td)/"runs")
            completed=SimpleNamespace(returncode=1,stderr="timeout",stdout="")
            with patch.dict("os.environ",{"AUTOMATION_SYSTEM_LEARNING_TIMEOUT":"300"},clear=False), patch("research_pipeline.automation_cycle.subprocess.run",return_value=completed) as run:
                result=_run_external_system_learning_review(storage)
            command=run.call_args.args[0]
            self.assertIn("--timeout",command)
            self.assertEqual(command[command.index("--timeout")+1],"300")
            self.assertIn("at most FOUR",command[-1])
            self.assertIn("under 900 words",command[-1])
            self.assertEqual(run.call_args.kwargs["timeout"],360)
            self.assertFalse(result["ok"])

    def test_failed_advisory_external_review_is_warning_not_pass(self) -> None:
        step=_advisory_step("external-review",lambda:{"ok":False,"returncode":1,"exists":False})
        self.assertEqual(step["status"],"warning")
        self.assertTrue(step["advisory"])
        self.assertEqual(step["summary"]["ok"],False)

    def test_advisory_warning_yields_pass_with_warnings_without_masking_core_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); storage=SimpleNamespace(run_dir=root/"runs",lock_dir=root/"locks",ensure=lambda:None)
            def hard_pass(name,function): return {"name":name,"status":"pass","duration_seconds":0.0,"summary":{}}
            def advisory_warning(name,function): return {"name":name,"status":"warning","advisory":True,"duration_seconds":0.0,"summary":{"ok":False}}
            with patch("research_pipeline.automation_cycle.StorageSettings.from_env",return_value=storage), patch("research_pipeline.automation_cycle._step",side_effect=hard_pass), patch("research_pipeline.automation_cycle._advisory_step",side_effect=advisory_warning):
                report=run_cycle(mode="weekly",web_review_limit=1,ai_consultations=False,publish=False)
            self.assertEqual(report["status"],"pass_with_warnings")
            self.assertEqual(sum(step["status"]=="warning" for step in report["steps"]),2)


if __name__ == "__main__":
    unittest.main()
