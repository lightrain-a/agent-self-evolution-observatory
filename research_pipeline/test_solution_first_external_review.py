from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from .idea_discovery_v3 import build_idea_discovery_v3
from .solution_first_external_review import build_prompt, prepare_batches, read_store


class SolutionFirstExternalReviewTest(unittest.TestCase):
    def test_prompt_contains_solution_specific_fields_and_bilingual_schema(self) -> None:
        bank = build_idea_discovery_v3()
        prompt = build_prompt(bank["shortlist"][:2], batch_index=1, batch_count=1)
        for marker in (
            "changed_assumption",
            "exact_mechanism",
            "learning_signal",
            "independent_ground_truth",
            "required_action_zh",
            "solution_quality",
        ):
            self.assertIn(marker, prompt)
        self.assertIn(bank["shortlist"][0]["id"], prompt)

    def test_batch_preparation_skips_reviewed_children(self) -> None:
        bank = build_idea_discovery_v3()
        reviewed_id = bank["shortlist"][0]["id"]
        store = read_store(Path("/nonexistent/solution-first-store.json"))
        store["reviews"] = {reviewed_id: [{"verdict": "revise"}]}
        with tempfile.TemporaryDirectory() as directory:
            manifest = prepare_batches(bank, Path(directory), batch_size=4, review_store=store)
        self.assertEqual(manifest["queued_ideas"], 9)
        self.assertEqual(len(manifest["batches"]), 3)
        self.assertNotIn(reviewed_id, [idea_id for batch in manifest["batches"] for idea_id in batch["idea_ids"]])


if __name__ == "__main__":
    unittest.main()
