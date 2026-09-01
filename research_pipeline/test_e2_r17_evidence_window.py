from __future__ import annotations

import importlib.metadata
import json
import unittest
from unittest import mock

from research_pipeline.e2_r17_evidence_window import (
    DEFAULT_CAP_TOKENS,
    HEAD_FRACTION,
    TOKENIZER_ENCODING,
    TOKENIZER_PACKAGE,
    TOKENIZER_VERSION,
    MatchedEvidenceWindowRenderer,
    canonical_trajectory_text,
    select_head_tail,
)


class EvidenceWindowTest(unittest.TestCase):
    def test_canonical_text_excludes_common_system_and_provenance(self) -> None:
        payload = {
            "messages": [
                {"role": "system", "content": "common system prompt"},
                {"role": "user", "content": "do task"},
                {"role": "assistant", "content": "attempt"},
                {"role": "tool", "content": "tool result"},
            ],
            "score": 0.0,
            "score_message": "failed verifier",
            "provider_receipts": [{"secret": "must not render"}],
            "workdir": "/private/path",
            "response_id": "opaque-provider-id",
        }
        text = canonical_trajectory_text(payload)
        decoded = json.loads(text)
        self.assertEqual([row["role"] for row in decoded["messages"]], ["user", "assistant", "tool"])
        self.assertEqual(decoded["score"], 0.0)
        self.assertEqual(decoded["score_message"], "failed verifier")
        self.assertNotIn("common system prompt", text)
        self.assertNotIn("secret", text)
        self.assertNotIn("private/path", text)
        self.assertNotIn("opaque-provider-id", text)

    def test_canonical_text_is_key_order_stable(self) -> None:
        first = {
            "messages": [{"content": "x", "role": "user"}],
            "score": 1.0,
            "score_message": "ok",
        }
        second = {
            "score_message": "ok",
            "score": 1.0,
            "messages": [{"role": "user", "content": "x"}],
        }
        self.assertEqual(canonical_trajectory_text(first), canonical_trajectory_text(second))

    def test_select_head_tail_exact_budget(self) -> None:
        tokens = list(range(100))
        selected = select_head_tail(tokens, 12)
        self.assertEqual(len(selected), 12)
        self.assertEqual(selected[:4], [0, 1, 2, 3])
        self.assertEqual(selected[4:], list(range(92, 100)))
        self.assertAlmostEqual(HEAD_FRACTION, 1.0 / 3.0)

    def test_select_head_tail_preserves_short_evidence(self) -> None:
        tokens = [1, 2, 3]
        self.assertEqual(select_head_tail(tokens, 10), tokens)

    def test_renderer_refuses_missing_or_wrong_pinned_tokenizer(self) -> None:
        with mock.patch("importlib.metadata.version", side_effect=importlib.metadata.PackageNotFoundError):
            with self.assertRaisesRegex(RuntimeError, "tiktoken==0.11.0"):
                MatchedEvidenceWindowRenderer()
        with mock.patch("importlib.metadata.version", return_value="9.9.9"):
            with self.assertRaisesRegex(RuntimeError, "observed 9.9.9"):
                MatchedEvidenceWindowRenderer()

    def test_frozen_constants(self) -> None:
        self.assertEqual(TOKENIZER_PACKAGE, "tiktoken")
        self.assertEqual(TOKENIZER_VERSION, "0.11.0")
        self.assertEqual(TOKENIZER_ENCODING, "cl100k_base")
        self.assertEqual(DEFAULT_CAP_TOKENS, 3072)


if __name__ == "__main__":
    unittest.main()
