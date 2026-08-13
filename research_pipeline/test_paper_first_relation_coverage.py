from __future__ import annotations

import unittest

from .paper_first_relation_coverage import relation_universe_digest, source_pair_coverage


class RelationCoverageTest(unittest.TestCase):
    def receipt(self, run_id: str, refs: list[str]) -> dict:
        return {"run_id": run_id, "source_refs": refs, "scientific_authority": False}

    def test_duplicate_receipt_does_not_change_relation_universe_digest(self) -> None:
        base = [self.receipt("r1", ["arXiv:1", "arXiv:2", "arXiv:3"])]
        duplicate = base + [self.receipt("r2", ["arXiv:1", "arXiv:2", "arXiv:3"])]
        self.assertEqual(relation_universe_digest(base), relation_universe_digest(duplicate))
        self.assertEqual(source_pair_coverage(base)["coobserved_source_pairs"], source_pair_coverage(duplicate)["coobserved_source_pairs"])

    def test_new_coobserved_pair_changes_relation_universe_digest(self) -> None:
        base = [self.receipt("r1", ["arXiv:1", "arXiv:2"]), self.receipt("r2", ["arXiv:3", "arXiv:4"])]
        bridged = base + [self.receipt("r3", ["arXiv:2", "arXiv:3"])]
        self.assertNotEqual(relation_universe_digest(base), relation_universe_digest(bridged))
        self.assertEqual(source_pair_coverage(base)["coobserved_source_pairs"], 2)
        self.assertEqual(source_pair_coverage(bridged)["coobserved_source_pairs"], 3)

    def test_new_source_changes_relation_universe_digest(self) -> None:
        base = [self.receipt("r1", ["arXiv:1", "arXiv:2"])]
        extended = base + [self.receipt("r2", ["arXiv:2", "arXiv:3"])]
        self.assertNotEqual(relation_universe_digest(base), relation_universe_digest(extended))
        self.assertEqual(source_pair_coverage(extended)["reviewed_receipt_sources"], 3)


if __name__ == "__main__":
    unittest.main()
