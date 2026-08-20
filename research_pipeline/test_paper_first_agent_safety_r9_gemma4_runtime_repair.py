from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_gemma4_runtime_repair import (
    V2_STOP_STATUS,
    V3_MAX_NUM_BATCHED_TOKENS,
    V3_STATUS,
    build_v2_runtime_stop,
    build_v3,
    validate_v3,
)


class Gemma4RuntimeRepairTest(unittest.TestCase):
    def test_current_runtime_error_builds_zero_inference_protocol_stop(self) -> None:
        state = build_v2_runtime_stop(
            v2_path=Path("generated/agent-safety-r9-gemma4-benign-gate-v2-preregistration-20260819.json"),
            log_path=Path("/data/wyt/agent-safety-discovery-20260818/r9-gemma4-benign-v2-server-20260819.log"),
            generated_at="2026-08-19T14:50:00+00:00",
        )
        self.assertEqual(state["status"], V2_STOP_STATUS)
        self.assertEqual(state["stop_class"], "PROTOCOL_STOP")
        self.assertEqual(state["model_inference_calls_executed"], 0)
        self.assertEqual(state["minimal_protocol_repair"]["to"], V3_MAX_NUM_BATCHED_TOKENS)

    def test_v3_changes_only_exact_runtime_lower_bound(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            stop_path = Path(td) / "stop.json"
            stop = build_v2_runtime_stop(
                v2_path=Path("generated/agent-safety-r9-gemma4-benign-gate-v2-preregistration-20260819.json"),
                log_path=Path("/data/wyt/agent-safety-discovery-20260818/r9-gemma4-benign-v2-server-20260819.log"),
            )
            stop_path.write_text(json.dumps(stop), encoding="utf-8")
            state = build_v3(
                v2_path=Path("generated/agent-safety-r9-gemma4-benign-gate-v2-preregistration-20260819.json"),
                stop_path=stop_path,
            )
            self.assertEqual(validate_v3(state), [])
            self.assertEqual(state["status"], V3_STATUS)
            self.assertEqual(state["runtime_launch"]["max_num_batched_tokens"], 2496)
            self.assertIsNone(state["runtime_launch"]["max_model_len_override"])
            self.assertIsNone(state["runtime_launch"]["gpu_memory_utilization_override"])
            self.assertFalse(state["authority"]["development_safety_execution"])

    def test_validator_rejects_max_model_len_rescue(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            stop_path = Path(td) / "stop.json"
            stop = build_v2_runtime_stop(
                v2_path=Path("generated/agent-safety-r9-gemma4-benign-gate-v2-preregistration-20260819.json"),
                log_path=Path("/data/wyt/agent-safety-discovery-20260818/r9-gemma4-benign-v2-server-20260819.log"),
            )
            stop_path.write_text(json.dumps(stop), encoding="utf-8")
            state = build_v3(v2_path=Path("generated/agent-safety-r9-gemma4-benign-gate-v2-preregistration-20260819.json"), stop_path=stop_path)
            state["runtime_launch"]["max_model_len_override"] = 32768
            self.assertIn("Gemma4 v3 runtime repair drift", validate_v3(state))


if __name__ == "__main__":
    unittest.main()
