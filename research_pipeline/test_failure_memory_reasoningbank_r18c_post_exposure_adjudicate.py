from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.failure_memory_reasoningbank_r18c_post_exposure_adjudicate import (
    EXPECTED_EXECUTOR_MANIFEST,
    build_receipt,
)


class TestR18cPostExposureAdjudication(unittest.TestCase):
    def _fixture(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        (root / "browsergym" / "exp0").mkdir(parents=True)
        (root / "attempts.jsonl").write_text(
            json.dumps({"sequence_index": 0, "status": "STARTED"}) + "\n",
            encoding="utf-8",
        )
        (root / "failure.json").write_text(
            json.dumps({"scientific_outcome_opened": True}), encoding="utf-8"
        )
        (root / "browsergym" / "exp0" / "summary_info.json").write_text(
            json.dumps(
                {
                    "n_steps": 1,
                    "cum_reward": 0,
                    "err_msg": "404 model 'gpt-4-1106-preview' not found",
                    "stack_trace": "x env.step(action) y self.evaluator( z",
                }
            ),
            encoding="utf-8",
        )
        (root / "browsergym" / "exp0" / "step_0.pkl.gz").write_bytes(b"opaque-step")
        return td, root

    def _r15(self):
        return {
            "completion_and_retry_policy": {
                "confirmatory_analysis_requires_all_144_terminal_episodes": True,
                "after_any_scientific_exposure": "no retry, no replacement, no endpoint switch; any unresolved support failure makes the whole confirmatory execution NO_VERDICT_SUPPORT_FAILURE",
            }
        }

    def _r16(self):
        return {"scope": {"single_confirmatory_attempt": True}}

    def _aliases(self):
        d = EXPECTED_EXECUTOR_MANIFEST
        return {
            "b1-qwen25-32b-l2b-executor:latest": d,
            "gpt-4:latest": d,
            "gpt-4-1106-preview:latest": d,
        }

    def test_post_exposure_failure_stops_current_attempt(self):
        td, root = self._fixture()
        try:
            r = build_receipt(self._r15(), self._r16(), root, self._aliases())
            self.assertTrue(r["failure"]["scientific_exposure_occurred"])
            self.assertFalse(r["frozen_policy_application"]["retry_sequence_0_under_R16"])
            self.assertFalse(r["adjudication"]["continue_current_144_episode_schedule"])
            self.assertEqual(r["scientific_verdict"], "NO_VERDICT_POST_EXPOSURE_SUPPORT_FAILURE")
        finally:
            td.cleanup()

    def test_alias_preflight_does_not_reauthorize(self):
        td, root = self._fixture()
        try:
            r = build_receipt(self._r15(), self._r16(), root, self._aliases())
            self.assertTrue(r["future_support_alias_preflight"]["all_aliases_manifest_identical"])
            self.assertTrue(r["future_support_alias_preflight"]["alias_does_not_reauthorize_current_R18"])
            self.assertFalse(r["authority"]["current_R18_execution"])
        finally:
            td.cleanup()

    def test_missing_future_alias_fails_closed(self):
        td, root = self._fixture()
        try:
            aliases = self._aliases()
            aliases.pop("gpt-4-1106-preview:latest")
            with self.assertRaises(RuntimeError):
                build_receipt(self._r15(), self._r16(), root, aliases)
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
