import tempfile
import unittest
from pathlib import Path

from research_pipeline.failure_memory_reasoningbank_writer_adjudicate_r17 import atomic_write, canonical_json, sha_bytes


class TestReasoningBankWriterAdjudicateR17(unittest.TestCase):
    def test_canonical_json_is_stable(self):
        a = canonical_json({"b": 2, "a": 1})
        b = canonical_json({"a": 1, "b": 2})
        self.assertEqual(a, b)
        self.assertEqual(sha_bytes(a.encode()), sha_bytes(b.encode()))

    def test_atomic_write_replaces_file(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "x.jsonl"
            atomic_write(p, b"one\n")
            atomic_write(p, b"two\n")
            self.assertEqual(p.read_bytes(), b"two\n")
            self.assertFalse(p.with_suffix(p.suffix + ".tmp").exists())


if __name__ == "__main__":
    unittest.main()
