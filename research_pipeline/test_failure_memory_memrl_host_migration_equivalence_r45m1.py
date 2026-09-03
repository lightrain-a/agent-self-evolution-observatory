from __future__ import annotations

import unittest

from .failure_memory_memrl_host_migration_equivalence_r45m1 import (
    REPEATS,
    TRAIN_INSTRUCTION_SHA,
    TRAIN_SHA,
    digest,
    embedding_evidence,
    ids,
    mos_config,
)


def expanded(index: int) -> list[float]:
    native = [0.0] * 768
    native[index] = 1.0
    chunk = [value * 0.5 for value in native]
    return chunk * 4


class MigrationEquivalenceTests(unittest.TestCase):
    def test_isometric_bridge_evidence(self) -> None:
        row = embedding_evidence([expanded(0), expanded(1)])
        self.assertEqual(row["max_cosine_bridge_error"], 0.0)
        self.assertEqual(row["norms"], [1.0, 1.0])

    def test_nonrepeated_bridge_is_closed(self) -> None:
        vector = expanded(0)
        vector[768] = 0.25
        with self.assertRaisesRegex(RuntimeError, r"Q2-(norm|repeat-bridge)"):
            embedding_evidence([vector])

    def test_retrieval_ids_preserve_order(self) -> None:
        self.assertEqual(ids([{"memory_id": "b"}, {"memory_id": "a"}]), ["b", "a"])
        with self.assertRaisesRegex(RuntimeError, "Q3-missing-id"):
            ids([{"memory_id": ""}])

    def test_mos_config_is_loopback_and_frozen(self) -> None:
        row = mos_config(__import__("pathlib").Path("/tmp/q"), "http://127.0.0.1:18143/v1")
        self.assertEqual(row["top_k"], 5)
        self.assertEqual(row["mem_reader"]["config"]["chunker"]["config"]["tokenizer_or_token_counter"], "character")

    def test_frozen_support_constants(self) -> None:
        self.assertEqual(REPEATS, 3)
        self.assertEqual(len(TRAIN_SHA), 64)
        self.assertEqual(len(TRAIN_INSTRUCTION_SHA), 64)
        self.assertEqual(digest({"b": 1, "a": 2}), digest({"a": 2, "b": 1}))


if __name__ == "__main__":
    unittest.main()
