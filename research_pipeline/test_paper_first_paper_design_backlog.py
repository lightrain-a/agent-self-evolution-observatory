from __future__ import annotations

import unittest

from .paper_first_paper_design_backlog import build_paper_design_backlog


class PaperDesignBacklogTest(unittest.TestCase):
    def passed(self, cid: str, a: str, b: str) -> dict:
        candidate={"candidate_id":cid,"title":f"Title {cid}","discovery_lane":"UNEXPLAINED_BOUNDARY","empirical_evidence":{"source_a":{"ref":a},"source_b":{"ref":b}}}
        return {"candidate_id":cid,"title":candidate["title"],"discovery_lane":candidate["discovery_lane"],"status":"AWAIT_HUMAN_PAPER_DESIGN_REVIEW","source_inbox":"private-or-staged","candidate":candidate}

    def queue(self, rows: list[dict]) -> dict:
        return {"discovery_transaction_id":"txn-1","summary":{"passed_problem_gate":len(rows)},"passed":rows}

    def test_problem_gate_pass_becomes_durable_pending_entry(self) -> None:
        state=build_paper_design_backlog(self.queue([self.passed("SP-1","arXiv:1","arXiv:2")]),{})
        self.assertEqual(state["summary"]["pending_human_paper_design"],1)
        entry=state["entries"][0]
        self.assertTrue(entry["paper_design_eligible"])
        self.assertEqual(entry["status"],"AWAIT_HUMAN_PAPER_DESIGN_REVIEW")
        self.assertTrue(entry["authority"]["paper_design_review"])
        self.assertFalse(entry["authority"]["method"])

    def test_empty_future_queue_cannot_erase_pending_entry(self) -> None:
        first=build_paper_design_backlog(self.queue([self.passed("SP-1","arXiv:1","arXiv:2")]),{})
        second=build_paper_design_backlog(self.queue([]),first)
        self.assertEqual(second["summary"]["pending_human_paper_design"],1)
        self.assertEqual(second["entries"][0]["candidate_id"],"SP-1")

    def test_new_pass_appends_without_reauthorizing_old_entry(self) -> None:
        first=build_paper_design_backlog(self.queue([self.passed("SP-1","arXiv:1","arXiv:2")]),{})
        second=build_paper_design_backlog(self.queue([self.passed("SP-2","arXiv:3","arXiv:4")]),first)
        self.assertEqual(second["summary"]["pending_human_paper_design"],2)
        self.assertEqual({row["candidate_id"] for row in second["entries"]},{"SP-1","SP-2"})
        self.assertTrue(all(row["authority"]["method"] is False for row in second["entries"]))

    def test_backlog_never_authorizes_downstream_execution(self) -> None:
        state=build_paper_design_backlog(self.queue([self.passed("SP-1","arXiv:1","arXiv:2")]),{})
        self.assertEqual((state["summary"]["method_authorized"],state["summary"]["experiment_authorized"],state["summary"]["p0_authorized"],state["summary"]["gpu_authorized"]),(0,0,0,0))
        self.assertFalse(state["scientific_authority"])


if __name__=="__main__":unittest.main()
