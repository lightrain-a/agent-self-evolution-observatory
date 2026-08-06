from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .idea_discovery_v4 import build_idea_discovery_v4
from .solution_first_v4_external_review import build_prompt, prepare_batches


class V4ReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bank = build_idea_discovery_v4()

    def test_prompt_has_combination_fields(self) -> None:
        text = build_prompt(self.bank["tournament_finalists"][:2], batch_index=1, batch_count=1)
        for marker in ("all_atoms_necessary", "removable_atoms", "revival_assessment", "required_action_zh"):
            self.assertIn(marker, text)

    def test_prepare_four_batches(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = prepare_batches(self.bank, Path(directory), batch_size=4, review_store={"reviews": {}})
        self.assertEqual(result["total_finalists"], 16)
        self.assertEqual(result["queued_ideas"], 16)
        self.assertEqual(len(result["batches"]), 4)


if __name__ == "__main__":
    unittest.main()
