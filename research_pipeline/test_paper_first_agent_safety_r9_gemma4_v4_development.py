from __future__ import annotations

import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_gemma4_hbb_protocol_repair import (
    EXPECTED_V4_DEVELOPMENT_IDS,
    V4_REALIZATION_ID,
)
from .paper_first_agent_safety_r9_gemma4_v4_development import (
    DEFAULT_V4_CONTRACT,
    assert_probe_allowed,
    expected_server_command,
    final_chat_is_assistant,
    load_v4,
)


class Gemma4V4DevelopmentTest(unittest.TestCase):
    def test_repo_v4_contract_is_episode_only_and_fresh(self) -> None:
        state = load_v4(DEFAULT_V4_CONTRACT)
        self.assertEqual(state["realization_id"], V4_REALIZATION_ID)
        self.assertEqual(state["probe_panels"]["development_probe_ids"], EXPECTED_V4_DEVELOPMENT_IDS)
        self.assertTrue(state["authority"]["development_episode_execution"])
        self.assertFalse(state["authority"]["development_harmbench_execution"])
        self.assertFalse(state["authority"]["fresh_qualification_execution"])
        self.assertFalse(state["authority"]["heldout_future"])

    def test_probe_guard_refuses_v3_exposed_and_carried_qualification(self) -> None:
        state = load_v4(DEFAULT_V4_CONTRACT)
        for probe_id in EXPECTED_V4_DEVELOPMENT_IDS:
            assert_probe_allowed(probe_id, state)
        for probe_id in [37, 12, 4, 35, 20, 6, 34, 21, 1, 8, 11, 22, 13, 33]:
            with self.assertRaises(ValueError):
                assert_probe_allowed(probe_id, state)

    def test_assistant_terminal_semantics_are_narrow(self) -> None:
        self.assertTrue(final_chat_is_assistant([{"role": "user"}, {"role": "assistant"}]))
        self.assertFalse(final_chat_is_assistant([{"role": "assistant"}, {"role": "user"}]))
        self.assertFalse(final_chat_is_assistant([]))
        self.assertFalse(final_chat_is_assistant(None))

    def test_server_command_preserves_v3_runtime_without_extra_rescue(self) -> None:
        v3 = {
            "runtime_launch": {
                "host": "127.0.0.1", "port": 18002, "dtype": "bfloat16",
                "served_model_name": "google/gemma-4-26B-A4B-it",
                "max_num_batched_tokens": 2496,
                "max_model_len_override": None,
                "gpu_memory_utilization_override": None,
                "quantization": None,
            },
            "frozen_axes": {"runtime": {"runtime_path": "/tmp/runtime"}},
        }
        asset = {"destination": "/tmp/model"}
        command = expected_server_command(v3, asset)
        self.assertEqual(command[-2:], ["--max-num-batched-tokens", "2496"])
        self.assertNotIn("--max-model-len", command)
        self.assertNotIn("--gpu-memory-utilization", command)
        self.assertNotIn("--quantization", command)
        v3["runtime_launch"]["max_model_len_override"] = 8192
        with self.assertRaisesRegex(ValueError, "refuses additional runtime override"):
            expected_server_command(v3, asset)


if __name__ == "__main__":
    unittest.main()
