from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.failure_memory_reasoningbank_r19_execute_r22 import completion_count_from_agent_info, require_no_confirmatory_stop


class TestR19ExecuteR22(unittest.TestCase):
    def test_initial_valid_action_is_one_completion(self):
        self.assertEqual(completion_count_from_agent_info({"n_retry": 0.0, "action": "x"}), 1)

    def test_valid_after_two_parse_retries_is_three_completions(self):
        self.assertEqual(completion_count_from_agent_info({"n_retry": 2.0, "action": "x"}), 3)

    def test_exhausted_six_retries_is_six_completions(self):
        self.assertEqual(completion_count_from_agent_info({"n_retry": 6, "action": None, "err_msg": "parse"}), 6)

    def test_confirmatory_stop_marker_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "confirmatory-stop.json").write_text(json.dumps({"status": "R19_CONFIRMATORY_EXECUTION_PERMANENTLY_STOPPED", "reason": "retry-exhausted"}) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "execution permanently stopped"):
                require_no_confirmatory_stop(root)

    def test_absent_confirmatory_stop_marker_allows_preflight(self):
        with tempfile.TemporaryDirectory() as td:
            require_no_confirmatory_stop(Path(td))


if __name__ == "__main__":
    unittest.main()
