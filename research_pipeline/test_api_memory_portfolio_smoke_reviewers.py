from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .api_memory_portfolio_smoke_reviewers import _parse_review_payload


class PortfolioSmokeReviewerParserTest(unittest.TestCase):
    def test_valid_json_needs_no_repair(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = json.dumps({"reviews": [{"blind_id": "B1", "reason": "ok"}]})
            payload, repair = _parse_review_payload(
                raw, run_root=root, name="reduction", raw_sha256="a" * 64
            )
            self.assertEqual(payload["reviews"][0]["blind_id"], "B1")
            self.assertIsNone(repair)
            self.assertEqual(list(root.glob("repair-*.json")), [])

    def test_only_missing_final_review_object_brace_is_repaired(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = '{"reviews":[{"blind_id":"B1","reason":"complete string"]}'
            payload, repair = _parse_review_payload(
                raw, run_root=root, name="reduction", raw_sha256="b" * 64
            )
            self.assertEqual(payload, {"reviews": [{"blind_id": "B1", "reason": "complete string"}]})
            self.assertEqual(repair["repair_type"], "TRAILING_REVIEW_OBJECT_CLOSE_ONLY")
            self.assertEqual(repair["inserted_text"], "}")
            self.assertFalse(repair["string_content_mutation_allowed"])
            files = list(root.glob("repair-reduction-review-*.json"))
            self.assertEqual(len(files), 1)
            persisted = json.loads(files[0].read_text(encoding="utf-8"))
            self.assertEqual(persisted["raw_sha256"], "b" * 64)
            self.assertEqual(persisted["repaired_sha256"], repair["repaired_sha256"])

    def test_other_malformed_json_is_not_salvaged(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = '{"reviews":[{"blind_id":"B1","reason":"truncated'
            with self.assertRaises(Exception):
                _parse_review_payload(
                    raw, run_root=root, name="reduction", raw_sha256="c" * 64
                )
            self.assertEqual(list(root.glob("repair-*.json")), [])


if __name__ == "__main__":
    unittest.main()
