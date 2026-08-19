from __future__ import annotations

import unittest
from pathlib import Path

from research_pipeline.paper_first_agent_safety_r9_harmbench_server import _llm_kwargs, _tokenization_kwargs


class HarmBenchServerCompatibilityTest(unittest.TestCase):
    def test_vllm_020_uses_same_local_slow_tokenizer(self) -> None:
        model_dir = Path("/tmp/frozen-harmbench")
        kwargs = _llm_kwargs(model_dir, 0.9)
        self.assertEqual(kwargs["model"], str(model_dir))
        self.assertEqual(kwargs["tokenizer"], str(model_dir))
        self.assertEqual(kwargs["tokenizer_mode"], "slow")
        self.assertEqual(kwargs["dtype"], "bfloat16")
        self.assertEqual(kwargs["tensor_parallel_size"], 2)
        self.assertNotIn("max_model_len", kwargs)
        self.assertEqual(kwargs["gpu_memory_utilization"], 0.9)

    def test_prompt_truncation_reserves_one_output_token(self) -> None:
        self.assertEqual(_tokenization_kwargs(2048, 1), {"max_length": 2047, "truncation": True})
        with self.assertRaisesRegex(ValueError, "invalid HarmBench prompt budget"):
            _tokenization_kwargs(1, 1)


if __name__ == "__main__":
    unittest.main()
