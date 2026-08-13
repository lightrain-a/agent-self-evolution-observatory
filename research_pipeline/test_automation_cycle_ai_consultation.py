from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from .automation_cycle import _advisory_step, _run_external_system_learning_review, _sync_literature, cycle_lock, run_cycle


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
            self.assertLess(names.index("paper-first-fresh-saturation"), names.index("human-terminal-idea-state"))
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
            self.assertIn("paper-first-primary-evidence-refresh", names)
            self.assertIn("paper-first-fresh-saturation", names)
            self.assertIn("paper-first-problem-generator", names)
            self.assertIn("paper-first-problem-gate-queue", names)
            self.assertIn("historical-paper-first-idea-incubation", names)
            self.assertIn("archival-solution-first-idea-discovery-v3", names)
            self.assertNotIn("solution-first-idea-discovery-v3", names)
            self.assertLess(names.index("paper-first-primary-evidence-refresh"), names.index("paper-first-fresh-saturation"))
            self.assertLess(names.index("paper-first-fresh-saturation"), names.index("paper-first-problem-generator"))
            self.assertLess(names.index("paper-first-problem-generator"), names.index("paper-first-problem-gate-queue"))
            self.assertLess(names.index("paper-first-problem-gate-queue"), names.index("archival-solution-first-idea-discovery-v3"))
            self.assertLess(names.index("paper-first-problem-gate-queue"), names.index("historical-paper-first-idea-incubation"))
            self.assertLess(names.index("external-research-system-learning-review"), names.index("project-web-gpt-repair-review"))

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
