from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from .automation_cycle import run_cycle


class AutomationCycleAIConsultationTest(unittest.TestCase):
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
            self.assertLess(names.index("research-system-pre-ai"), names.index("ai-consultation-automation"))
            self.assertLess(names.index("ai-consultation-automation"), names.index("research-system-state"))
            self.assertEqual(report["ai_consultation_limit"], 1)
            self.assertTrue(report["ai_consultations"])


if __name__ == "__main__":
    unittest.main()
