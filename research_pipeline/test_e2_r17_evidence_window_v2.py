from __future__ import annotations

import importlib.metadata
import unittest

from research_pipeline.e2_r17_evidence_window_v2 import (
    BLOCK_BOUNDARY,
    BLOCK_HEADER,
    FINAL_BLOCK_CAP_TOKENS,
    TOKENIZER_ENCODING,
    TOKENIZER_VERSION,
    ExactMatchedEvidenceBlockRenderer,
    _candidate_block,
    canonical_trajectory_text,
)


class _CharEncoding:
    def encode(self, text: str) -> list[int]:
        return [ord(char) for char in text]

    def decode(self, tokens: list[int]) -> str:
        return "".join(chr(token) for token in tokens)

    def decode_bytes(self, tokens: list[int]) -> bytes:
        return self.decode(tokens).encode("utf-8")


class EvidenceWindowV2Test(unittest.TestCase):
    def test_canonical_text_is_arm_blinded(self) -> None:
        payload = {
            "rollout_index": 7,
            "projection": "mixed_rejected_witness",
            "trajectory_path": "/secret/path",
            "provider_receipt": "opaque",
            "score": 0.0,
            "score_message": "formula mismatch",
            "messages": [
                {"role": "system", "content": "common system"},
                {"role": "user", "content": "fix workbook"},
                {"role": "assistant", "content": "attempt"},
            ],
        }
        text = canonical_trajectory_text(payload)
        self.assertIn("formula mismatch", text)
        self.assertIn("fix workbook", text)
        for forbidden in ["mixed_rejected_witness", "rollout_index", "/secret/path", "opaque", "common system"]:
            self.assertNotIn(forbidden, text)

    def test_candidate_always_uses_same_arm_blinded_wrapper(self) -> None:
        encoding = _CharEncoding()
        text, actual = _candidate_block(encoding, encoding.encode("abcdefghijklmnopqrstuvwxyz" * 10), 120)
        self.assertTrue(text.startswith(BLOCK_HEADER))
        self.assertIn(BLOCK_BOUNDARY, text)
        self.assertEqual(actual, len(encoding.encode(text)))
        self.assertNotIn("WIN", text)
        self.assertNotIn("MRW", text)

    def test_actual_tiktoken_pair_is_exact_when_dependency_available(self) -> None:
        try:
            observed = importlib.metadata.version("tiktoken")
        except importlib.metadata.PackageNotFoundError:
            self.skipTest("pinned tiktoken is intentionally absent from shared Python")
        if observed != TOKENIZER_VERSION:
            self.skipTest(f"requires tiktoken {TOKENIZER_VERSION}, observed {observed}")
        renderer = ExactMatchedEvidenceBlockRenderer()
        left = "A short spreadsheet execution. " * 800
        right = "A different failure trajectory with formula mismatch. " * 500
        left_block, right_block, receipt = renderer.render_pair(left, right)
        self.assertEqual(len(renderer.encoding.encode(left_block)), len(renderer.encoding.encode(right_block)))
        self.assertEqual(len(renderer.encoding.encode(left_block)), receipt.matched_final_block_tokens)
        self.assertLessEqual(receipt.matched_final_block_tokens, FINAL_BLOCK_CAP_TOKENS)
        self.assertFalse(receipt.padding_used)
        self.assertFalse(receipt.arm_metadata_visible)

    def test_identical_sources_remain_identical(self) -> None:
        try:
            observed = importlib.metadata.version("tiktoken")
        except importlib.metadata.PackageNotFoundError:
            self.skipTest("pinned tiktoken is intentionally absent from shared Python")
        if observed != TOKENIZER_VERSION:
            self.skipTest(f"requires tiktoken {TOKENIZER_VERSION}, observed {observed}")
        renderer = ExactMatchedEvidenceBlockRenderer()
        source = "same evidence " * 1000
        left, right, receipt = renderer.render_pair(source, source)
        self.assertEqual(left, right)
        self.assertEqual(receipt.left_selected_source_tokens, receipt.right_selected_source_tokens)

    def test_frozen_constants(self) -> None:
        self.assertEqual(TOKENIZER_VERSION, "0.11.0")
        self.assertEqual(TOKENIZER_ENCODING, "cl100k_base")
        self.assertEqual(FINAL_BLOCK_CAP_TOKENS, 3072)


if __name__ == "__main__":
    unittest.main()
