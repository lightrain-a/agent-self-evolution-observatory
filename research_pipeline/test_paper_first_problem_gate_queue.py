from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_problem_gate_queue import build_problem_gate_queue
from .test_paper_first_problem_discovery_contract import valid_candidate


class PaperFirstProblemGateQueueTest(unittest.TestCase):
    def test_missing_inbox_is_valid_empty_queue(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            state=build_problem_gate_queue(Path(td)/"missing.json")
        self.assertEqual((state["summary"]["submitted"],state["summary"]["passed_problem_gate"],state["summary"]["blocked_problem_gate"]),(0,0,0))
        self.assertEqual(state["inbox_errors"],[])
        self.assertTrue(state["policy"]["zero_candidates_or_zero_passes_is_valid"])
        self.assertEqual((state["summary"]["method_authorized"],state["summary"]["experiment_authorized"],state["summary"]["p0_authorized"]),(0,0,0))

    def test_valid_candidate_only_enters_human_paper_design_queue(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"inbox.json"; path.write_text(json.dumps({"candidates":[valid_candidate()]}),encoding="utf-8")
            state=build_problem_gate_queue(path)
        self.assertEqual((state["summary"]["submitted"],state["summary"]["passed_problem_gate"],state["summary"]["paper_design_eligible"]),(1,1,1))
        self.assertEqual(state["passed"][0]["status"],"AWAIT_HUMAN_PAPER_DESIGN_REVIEW")
        self.assertEqual(state["summary"]["method_authorized"],0)
        self.assertEqual(state["summary"]["experiment_authorized"],0)
        self.assertEqual(state["summary"]["p0_authorized"],0)

    def test_saturation_match_is_blocked_before_paper_design(self) -> None:
        candidate=valid_candidate(); candidate["saturation_scan"]={"checked":True,"matched_patterns":["externalization-internalization-portability"]}
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"inbox.json"; path.write_text(json.dumps({"candidates":[candidate]}),encoding="utf-8")
            state=build_problem_gate_queue(path)
        self.assertEqual((state["summary"]["passed_problem_gate"],state["summary"]["blocked_problem_gate"]),(0,1))
        self.assertTrue(any(x.startswith("saturation-pattern-match:") for x in state["blocked"][0]["blockers"]))

    def test_duplicate_candidate_ids_are_never_eligible(self) -> None:
        a=valid_candidate(); b=valid_candidate(); b["title"]="duplicate"
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"inbox.json"; path.write_text(json.dumps({"candidates":[a,b]}),encoding="utf-8")
            state=build_problem_gate_queue(path)
        self.assertEqual(state["summary"]["paper_design_eligible"],0)
        self.assertEqual(state["summary"]["inbox_errors"],1)
        self.assertTrue(state["inbox_errors"][0].startswith("duplicate-candidate-ids:"))


if __name__=="__main__": unittest.main()
