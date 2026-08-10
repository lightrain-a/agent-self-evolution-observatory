from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .a2_qualification_review import build


class A2QualificationReviewTest(unittest.TestCase):
    def _write(self, root: Path, *, count: int, archetype: bool, controller: bool, tiny: bool) -> tuple[Path, Path]:
        qualification = root / "qualification.json"
        sequences = root / "fixed-sequences.jsonl"
        qualification.write_text(json.dumps({
            "sequence_count": count,
            "archetype_pass": archetype,
            "controller_disagreement_pass": controller,
            "optimal_round_entropy_bits": 1.2,
            "oracle_success_bearing_sequences": 4,
            "non_early_optimal_sequences": 3,
            "rollback_or_harm_sequences": 2,
            "jackknife_min_entropy_bits": 0.8,
            "leave_one_sequence_out_continue_stop_auc": 0.7 if controller else 0.5,
            "controller_baseline_disagreement_sequences": 3,
            "tiny_real_subset": {"training_auc": 0.97 if tiny else 0.8, "pass": tiny},
        }), encoding="utf-8")
        rows = [
            {"task_id": f"/data/a/json_2.1.1/valid_seen/task-{index}/trial/game.tw-pddl", "rounds": []}
            for index in range(count)
        ]
        sequences.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        return qualification, sequences

    def test_incomplete_qualification_cannot_unblock(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            q, s = self._write(Path(td), count=7, archetype=True, controller=True, tiny=True)
            review = build(q, s)
            self.assertFalse(review["qualification_complete"])
            self.assertEqual(review["authorization_effect"], "may-block-only")
            self.assertFalse(review["independent_validation"])
            self.assertTrue(all(not row["pass"] for row in review["check_updates"].values()))

    def test_complete_qualification_can_unblock_only_the_checks_it_passed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            q, s = self._write(Path(td), count=9, archetype=True, controller=False, tiny=False)
            review = build(q, s)
            self.assertEqual(review["authorization_effect"], "may-unblock")
            self.assertTrue(review["independent_validation"])
            self.assertTrue(review["check_updates"]["target_variation"]["pass"])
            self.assertFalse(review["check_updates"]["baseline_disagreement"]["pass"])
            self.assertFalse(review["check_updates"]["tiny_overfit"]["pass"])
            self.assertEqual(review["excluded_qualification_task_count"], 9)
            self.assertTrue(all(key.startswith("valid_seen/") for key in review["excluded_qualification_task_keys"]))


if __name__ == "__main__":
    unittest.main()
