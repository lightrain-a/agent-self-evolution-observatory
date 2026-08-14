from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from . import problem_search_stage_runner as runner


class ProblemSearchStageRunnerMemoryTest(unittest.TestCase):
    def memory(self, candidate_id: str = "SHADOW-P12-C01") -> dict:
        return {
            "shadow_dead_end_memory": {
                "memory_id": "test-shadow-memory",
                "blocked_objects": [
                    {
                        "source_candidate_id": candidate_id,
                        "basin": "current-source-hard-veto-test",
                        "strongest_reduction": "generic identifiability over an omitted compiled-context variable",
                        "current_source_refs": ["arXiv:2605.10114"],
                        "reopen_only_if": "A same-information residual survives explicit instrumentation.",
                        "scientific_authority": False,
                    }
                ],
                "live_source_coverage_effect": False,
                "cannot_mutate_canonical_generator_or_queue": True,
                "scientific_authority": False,
            }
        }

    def test_missing_explicit_memory_uses_generated_design_adjudication_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "design.json"
            path.write_text(json.dumps(self.memory()), encoding="utf-8")
            with patch.object(runner, "DEFAULT_SHADOW_DEAD_END_MEMORY_PATH", path):
                memory = runner._shadow_dead_end_memory(None)
        self.assertEqual(memory["blocked_objects"][0]["source_candidate_id"], "SHADOW-P12-C01")
        self.assertFalse(memory["scientific_authority"])

    def test_explicit_memory_path_overrides_default(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            default = root / "default.json"
            explicit = root / "explicit.json"
            default.write_text(json.dumps(self.memory("DEFAULT")), encoding="utf-8")
            explicit.write_text(json.dumps(self.memory("EXPLICIT")), encoding="utf-8")
            with patch.object(runner, "DEFAULT_SHADOW_DEAD_END_MEMORY_PATH", default):
                memory = runner._shadow_dead_end_memory(explicit)
        self.assertEqual(memory["blocked_objects"][0]["source_candidate_id"], "EXPLICIT")

    def test_missing_default_memory_is_empty_search_control(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / "missing.json"
            with patch.object(runner, "DEFAULT_SHADOW_DEAD_END_MEMORY_PATH", missing):
                self.assertEqual(runner._shadow_dead_end_memory(None), {})

    def test_illegal_default_memory_authority_fails_closed(self) -> None:
        payload = self.memory()
        payload["shadow_dead_end_memory"]["scientific_authority"] = True
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with patch.object(runner, "DEFAULT_SHADOW_DEAD_END_MEMORY_PATH", path):
                with self.assertRaisesRegex(ValueError, "zero-authority"):
                    runner._shadow_dead_end_memory(None)


if __name__ == "__main__":
    unittest.main()
