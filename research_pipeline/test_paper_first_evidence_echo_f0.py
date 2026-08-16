from __future__ import annotations

import unittest

from research_pipeline.paper_first_evidence_echo_f0 import (
    ANSWERABLE_TARGET,
    ARMS,
    UNANSWERABLE_TARGET,
    _arm_note_drafts,
    analyze_rows,
    arm_note,
    select_units,
)


class FakeTokenizer:
    def encode(self, text, add_special_tokens=False):
        # Deterministic character-level tokenizer is enough to test exact note-budget locking.
        return [ord(ch) for ch in str(text)]

    def decode(self, ids, skip_special_tokens=True):
        return "".join(chr(int(i)) for i in ids)


class EvidenceEchoF0Test(unittest.TestCase):
    def test_nonraw_arms_are_exactly_note_token_matched(self) -> None:
        tok = FakeTokenizer()
        pages = ["alpha beta gamma " * 200, "target evidence delta " * 200, "other page " * 200]
        ids = [1, 2, 3]
        counts = {}
        for arm in ARMS:
            _, n = arm_note(tok, arm, pages, ids)
            counts[arm] = n
        nonraw = {counts[arm] for arm in ARMS if arm != "RAW_ONLY"}
        self.assertEqual(1, len(nonraw))
        self.assertNotEqual(counts["RAW_ONLY"], counts["ECHO_EXTRACTIVE"])
        drafts, _, payload = _arm_note_drafts(tok, pages, ids)
        self.assertIn(payload, drafts["ECHO_EXTRACTIVE"])
        self.assertIn(payload, drafts["DEDUP_WARNING"])

    def test_selection_is_outcome_blind_parent_order_by_truth_class(self) -> None:
        units = []
        for i in range(80):
            units.append({"unit_id": f"U{i:03d}", "class": "unanswerable", "sample_index": i})
        for i in range(80, 160):
            units.append({"unit_id": f"U{i:03d}", "class": "answerable", "sample_index": i})
        chosen = select_units({"units": units})
        self.assertEqual(UNANSWERABLE_TARGET + ANSWERABLE_TARGET, len(chosen))
        self.assertEqual(UNANSWERABLE_TARGET, sum(row["class"] == "unanswerable" for row in chosen))
        self.assertEqual(ANSWERABLE_TARGET, sum(row["class"] == "answerable" for row in chosen))
        self.assertEqual("U000", chosen[0]["unit_id"])
        self.assertEqual("U080", chosen[UNANSWERABLE_TARGET]["unit_id"])

    def _rows(self, *, echo_false: set[int], verbatim_false: set[int], neutral_false: set[int], dedup_false: set[int]):
        rows = []
        for i in range(UNANSWERABLE_TARGET):
            for arm in ARMS:
                false = {
                    "RAW_ONLY": i < 2,
                    "ECHO_EXTRACTIVE": i in echo_false or i < 2,
                    "VERBATIM_DUPLICATE": i in verbatim_false or i < 2,
                    "TOKEN_MATCHED_NEUTRAL": i in neutral_false or i < 2,
                    "DEDUP_WARNING": i in dedup_false or i < 2,
                }[arm]
                rows.append({"unit_id": f"U{i:03d}", "class": "unanswerable", "arm": arm, "false_answer_unanswerable": false, "exact_correct": False})
        for i in range(ANSWERABLE_TARGET):
            for arm in ARMS:
                rows.append({"unit_id": f"A{i:03d}", "class": "answerable", "arm": arm, "false_answer_unanswerable": False, "exact_correct": True})
        return rows

    def test_analysis_can_identify_double_counting_go(self) -> None:
        # 8 raw-safe units become false under both evidence-duplication arms, none under neutral,
        # and the warning prevents the transitions. 8 discordant pairs gives exact p=0.0078125.
        induced = set(range(2, 10))
        out = analyze_rows(self._rows(echo_false=induced, verbatim_false=induced, neutral_false=set(), dedup_false=set()))
        self.assertEqual("GO_CORRELATED_EVIDENCE_DOUBLE_COUNTING_TO_CURRENT_SOURCE_REVIEW", out["status"])
        self.assertFalse(out["paper_problem_authorized"])
        self.assertFalse(out["gpu_authorized"])

    def test_analysis_stops_when_neutral_padding_matches_echo(self) -> None:
        induced = set(range(2, 10))
        out = analyze_rows(self._rows(echo_false=induced, verbatim_false=induced, neutral_false=induced, dedup_false=set()))
        self.assertEqual("STOP_OR_HOLD_GENERIC_PROMPT_REDUCTION_NOT_BEATEN", out["status"])


if __name__ == "__main__":
    unittest.main()
