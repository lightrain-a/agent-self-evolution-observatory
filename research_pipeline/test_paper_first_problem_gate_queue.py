from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_problem_gate_queue import build_problem_gate_queue
from .test_paper_first_problem_discovery_contract import valid_candidate


def write_primary_pool(root: Path) -> Path:
    candidate=valid_candidate(); sources=candidate["empirical_contradiction"]
    records=[]
    for key in ("source_a","source_b"):
        src=sources[key]
        records.append({
            "ref":src["ref"],
            "title":src["title"],
            "primary_url":src["primary_url"],
            "source_sha256":src["source_sha256"],
            "primary_source_verified":True,
            "abstract":"private abstract",
        })
    path=root/"primary.json"; path.write_text(json.dumps({"records":records}),encoding="utf-8"); return path


class PaperFirstProblemGateQueueTest(unittest.TestCase):
    def test_missing_inboxes_are_valid_empty_queue(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            state=build_problem_gate_queue(root/"missing.json",auto_inbox_path=root/"auto-missing.json",primary_pool_path=root/"primary-missing.json")
        self.assertEqual((state["summary"]["submitted"],state["summary"]["passed_problem_gate"],state["summary"]["blocked_problem_gate"]),(0,0,0))
        self.assertEqual(state["inbox_errors"],[])
        self.assertTrue(state["policy"]["zero_candidates_or_zero_passes_is_valid"])
        self.assertEqual((state["summary"]["method_authorized"],state["summary"]["experiment_authorized"],state["summary"]["p0_authorized"]),(0,0,0))

    def test_valid_candidate_only_enters_human_paper_design_queue_with_verified_primary_registry(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); path=root/"inbox.json"; path.write_text(json.dumps({"candidates":[valid_candidate()]}),encoding="utf-8")
            state=build_problem_gate_queue(path,auto_inbox_path=root/"none.json",primary_pool_path=write_primary_pool(root))
        self.assertEqual((state["summary"]["submitted"],state["summary"]["passed_problem_gate"],state["summary"]["paper_design_eligible"]),(1,1,1))
        self.assertEqual(state["passed"][0]["status"],"AWAIT_HUMAN_PAPER_DESIGN_REVIEW")
        self.assertEqual(state["summary"]["primary_evidence_records"],2)
        self.assertEqual(state["summary"]["method_authorized"],0)
        self.assertEqual(state["summary"]["experiment_authorized"],0)
        self.assertEqual(state["summary"]["p0_authorized"],0)

    def test_candidate_without_primary_registry_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); path=root/"inbox.json"; path.write_text(json.dumps({"candidates":[valid_candidate()]}),encoding="utf-8")
            state=build_problem_gate_queue(path,auto_inbox_path=root/"none.json",primary_pool_path=root/"missing-primary.json")
        self.assertEqual((state["summary"]["passed_problem_gate"],state["summary"]["blocked_problem_gate"]),(0,1))
        self.assertTrue(any(x.startswith("primary-source-not-in-registry:") for x in state["blocked"][0]["blockers"]))

    def test_saturation_match_is_blocked_before_paper_design(self) -> None:
        candidate=valid_candidate(); candidate["saturation_scan"]={"checked":True,"matched_patterns":["externalization-internalization-portability"]}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); path=root/"inbox.json"; path.write_text(json.dumps({"candidates":[candidate]}),encoding="utf-8")
            state=build_problem_gate_queue(path,auto_inbox_path=root/"none.json",primary_pool_path=write_primary_pool(root))
        self.assertEqual((state["summary"]["passed_problem_gate"],state["summary"]["blocked_problem_gate"]),(0,1))
        self.assertTrue(any(x.startswith("saturation-pattern-match:") for x in state["blocked"][0]["blockers"]))

    def test_manual_and_auto_inboxes_merge_but_duplicate_ids_are_never_eligible(self) -> None:
        a=valid_candidate(); b=valid_candidate(); b["title"]="duplicate"
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); manual=root/"manual.json"; auto=root/"auto.json"
            manual.write_text(json.dumps({"candidates":[a]}),encoding="utf-8"); auto.write_text(json.dumps({"candidates":[b]}),encoding="utf-8")
            state=build_problem_gate_queue(manual,auto_inbox_path=auto,primary_pool_path=write_primary_pool(root))
        self.assertEqual(state["summary"]["submitted"],2)
        self.assertEqual(state["summary"]["paper_design_eligible"],0)
        self.assertEqual(state["summary"]["inbox_errors"],1)
        self.assertTrue(state["inbox_errors"][0].startswith("duplicate-candidate-ids:"))

    def test_primary_sha_mismatch_is_blocked(self) -> None:
        c=valid_candidate(); c["empirical_contradiction"]["source_a"]["source_sha256"]="d"*64
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); path=root/"inbox.json"; path.write_text(json.dumps({"candidates":[c]}),encoding="utf-8")
            pool=write_primary_pool(root)
            # Restore registry to the expected original hash rather than candidate's forged hash.
            payload=json.loads(pool.read_text()); payload["records"][0]["source_sha256"]="a"*64; pool.write_text(json.dumps(payload))
            state=build_problem_gate_queue(path,auto_inbox_path=root/"none.json",primary_pool_path=pool)
        self.assertIn("primary-source-sha-mismatch:1",state["blocked"][0]["blockers"])


if __name__=="__main__": unittest.main()
