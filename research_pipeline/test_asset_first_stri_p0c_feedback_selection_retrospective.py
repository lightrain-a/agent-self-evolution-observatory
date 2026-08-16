from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .asset_first_stri_p0c_feedback_selection_retrospective import (
    _apply_stats_update,
    decision_reversals,
    first_party_accepted,
    load_solver_rows,
    run,
)


def normalize_stats(value):
    raw = dict(value or {})
    return {
        "attempts": int(raw.get("attempts", 0)),
        "consistent": int(raw.get("consistent", 0)),
        "boundary": int(raw.get("boundary", 0)),
        "verified": int(raw.get("verified", 0)),
        "too_easy": int(raw.get("too_easy", 0)),
        "too_hard": int(raw.get("too_hard", 0)),
        "inconsistent": int(raw.get("inconsistent", 0)),
        "avg_p_hat": float(raw.get("avg_p_hat", 0.0)),
        "last_updated_iteration": int(raw.get("last_updated_iteration", -1)),
    }


class P0CFeedbackSelectionRetrospectiveTests(unittest.TestCase):
    def test_first_party_default_acceptance_keeps_only_medium_p_hat_with_valid_candidate(self) -> None:
        self.assertTrue(first_party_accepted({"p_hat": 1 / 3, "candidate_count": 3}))
        self.assertTrue(first_party_accepted({"p_hat": 2 / 3, "candidate_count": 1}))
        self.assertFalse(first_party_accepted({"p_hat": 0.0, "candidate_count": 3}))
        self.assertFalse(first_party_accepted({"p_hat": 1.0, "candidate_count": 3}))
        self.assertFalse(first_party_accepted({"p_hat": 1 / 3, "candidate_count": 0}))

    def test_in_memory_update_matches_first_party_stats_semantics(self) -> None:
        skills = [{"id": "skill_003", "added_iteration": 0, "stats": normalize_stats({})}]
        rows = [
            {"source_skill_id": "skill_003", "p_hat": 1 / 3, "consistency": True},
            {"source_skill_id": "skill_003", "p_hat": 1.0, "consistency": True},
            {"source_skill_id": "skill_003", "p_hat": 0.0, "consistency": False},
        ]
        updated = _apply_stats_update(skills, rows, normalize_stats=normalize_stats)
        stats = updated[0]["stats"]
        self.assertEqual(stats["attempts"], 3)
        self.assertEqual(stats["consistent"], 2)
        self.assertEqual(stats["boundary"], 1)
        self.assertEqual(stats["verified"], 1)
        self.assertEqual(stats["too_easy"], 1)
        self.assertEqual(stats["too_hard"], 1)
        self.assertEqual(stats["inconsistent"], 1)
        self.assertAlmostEqual(stats["avg_p_hat"], 4 / 9)

    def test_strict_pairwise_flip_counts_but_tie_to_nontie_does_not(self) -> None:
        def snapshot(weights):
            total = sum(weights.values())
            return {"source": {key: {"weight": value, "probability": value / total, "pruned_by_default_policy": False} for key, value in weights.items()}}

        a = snapshot({"skill_003": 2.0, "skill_004": 1.0, "skill_015": 1.0})
        b = snapshot({"skill_003": 0.5, "skill_004": 1.5, "skill_015": 1.0})
        out = decision_reversals(a, b, ["skill_003", "skill_004", "skill_015"])
        self.assertTrue(out["any_real_decision_reversal"])
        self.assertEqual(len(out["strict_pairwise_sampling_ranking_reversals"]), 2)

        tie = snapshot({"skill_003": 1.0, "skill_004": 1.0, "skill_015": 1.0})
        nontie = snapshot({"skill_003": 2.0, "skill_004": 1.0, "skill_015": 1.0})
        out2 = decision_reversals(tie, nontie, ["skill_003", "skill_004", "skill_015"])
        self.assertFalse(out2["any_real_decision_reversal"])

    def test_solver_rows_require_exact_p_hat_correct_count_binding(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "solver-results.jsonl"
            path.write_text(json.dumps({
                "source_skill_id": "skill_003",
                "source_index": 0,
                "p_hat": 1 / 3,
                "consistency": 1,
                "candidate_count": 3,
                "correct_count": 1,
            }) + "\n", encoding="utf-8")
            rows = load_solver_rows(path, source_ids=["skill_003"], samples_per_task=3)
            self.assertEqual(rows[0]["correct_count"], 1)
            path.write_text(json.dumps({**rows[0], "p_hat": 2 / 3}) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "p_hat/correct_count mismatch"):
                load_solver_rows(path, source_ids=["skill_003"], samples_per_task=3)

    def test_missing_p0c_raw_is_fail_closed_not_empirical_no_reversal(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract = root / "contract.json"
            output = root / "result.json"
            contract.write_text(json.dumps({
                "experiment_id": "P0C",
                "candidate_id": "C",
                "units": {"source_skill_ids": ["skill_003", "skill_004", "skill_015"]},
                "solver": {"samples_per_task": 3},
            }), encoding="utf-8")
            out = run(contract_path=contract, p0c_result_path=None, solver_results_path=None, author_repo=root / "author", output_path=output)
            persisted = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(out["decision"], "HOLD_MISSING_AUDITABLE_P0C_RESULTS")
        self.assertFalse(out["decision_reversal_evaluated"])
        self.assertFalse(out["empirical_no_reversal_established"])
        self.assertFalse(out["baseline_authorized"])
        self.assertEqual(persisted["decision"], out["decision"])


if __name__ == "__main__":
    unittest.main()
