from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from research_pipeline.e2_r17_reasoningbank_style import (
    RB_AGGREGATOR_MAX_OUTPUT_TOKENS,
    RB_AGGREGATOR_TEMPERATURE,
    RB_PER_TRAJECTORY_CAP_TOKENS,
    RB_PINNED_COMMIT,
    extract_literal_assignment,
    render_rb_style_aggregation_prompt,
)


class _CharEncoding:
    def encode(self, text: str) -> list[int]:
        return [ord(char) for char in text]

    def decode(self, tokens: list[int]) -> str:
        return "".join(chr(token) for token in tokens)


class _FakeRenderer:
    encoding = _CharEncoding()


class ReasoningBankStyleAdapterTest(unittest.TestCase):
    def test_extract_literal_assignment_without_importing_module(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "prompt.py"
            path.write_text('OTHER = "x"\nPARALLEL_SI = "hello"\n', encoding="utf-8")
            self.assertEqual(extract_literal_assignment(path, "PARALLEL_SI"), "hello")

    def test_render_prompt_binds_success_failure_and_all_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            prompt = root / "WebArena/prompts/memory_instruction.py"
            prompt.parent.mkdir(parents=True)
            prompt.write_text('PARALLEL_SI = "official prompt"\n', encoding="utf-8")
            common_user = "Task:\nCompute the correct spreadsheet total."
            payloads = [
                {
                    "rollout_index": 0,
                    "score": 1.0,
                    "score_message": "pass",
                    "messages": [
                        {"role": "system", "content": "common system"},
                        {"role": "user", "content": common_user},
                        {"role": "assistant", "content": "good path"},
                    ],
                },
                {
                    "rollout_index": 1,
                    "score": 0.0,
                    "score_message": "wrong total",
                    "messages": [
                        {"role": "system", "content": "common system"},
                        {"role": "user", "content": common_user},
                        {"role": "assistant", "content": "bad path"},
                    ],
                },
            ]
            system, user, receipt = render_rb_style_aggregation_prompt(
                trajectory_payloads=payloads,
                trajectory_sha256s=["a" * 64, "b" * 64],
                reasoningbank_root=root,
                renderer=_FakeRenderer(),  # type: ignore[arg-type]
            )
            self.assertEqual(system, "official prompt")
            self.assertIn("verifier=SUCCESS", user)
            self.assertIn("verifier=FAILURE", user)
            self.assertIn("good path", user)
            self.assertIn("bad path", user)
            self.assertNotIn("common system", user)
            self.assertEqual(len(receipt.sources), 2)
            self.assertEqual(receipt.sources[0].trajectory_sha256, "a" * 64)
            self.assertEqual(receipt.sources[1].trajectory_sha256, "b" * 64)
            self.assertEqual(receipt.baseline_commit, RB_PINNED_COMMIT)
            self.assertEqual(receipt.per_trajectory_cap_tokens, 512)
            self.assertEqual(receipt.aggregator_temperature, 0.7)
            self.assertEqual(receipt.aggregator_max_output_tokens, 1024)

    def test_rejects_cross_task_pool(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            prompt = root / "WebArena/prompts/memory_instruction.py"
            prompt.parent.mkdir(parents=True)
            prompt.write_text('PARALLEL_SI = "official prompt"\n', encoding="utf-8")
            payloads = [
                {"score": 1, "messages": [{"role": "user", "content": "task A"}]},
                {"score": 0, "messages": [{"role": "user", "content": "task B"}]},
            ]
            with self.assertRaisesRegex(ValueError, "multiple task texts"):
                render_rb_style_aggregation_prompt(
                    trajectory_payloads=payloads,
                    trajectory_sha256s=["a", "b"],
                    reasoningbank_root=root,
                    renderer=_FakeRenderer(),  # type: ignore[arg-type]
                )

    def test_frozen_parameters(self) -> None:
        self.assertEqual(RB_PINNED_COMMIT, "ed80611788292ea739f1effd31f16c53823b8a0d")
        self.assertEqual(RB_PER_TRAJECTORY_CAP_TOKENS, 512)
        self.assertEqual(RB_AGGREGATOR_MAX_OUTPUT_TOKENS, 1024)
        self.assertEqual(RB_AGGREGATOR_TEMPERATURE, 0.7)


if __name__ == "__main__":
    unittest.main()
