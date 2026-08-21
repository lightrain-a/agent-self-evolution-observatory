from __future__ import annotations

import unittest

from .discovery_engine_terminal_adjudication import compile_terminal_state,validate_candidate_adjudication


class TerminalAdjudicationTest(unittest.TestCase):
    def test_missing_evidence_keeps_candidate_active(self):
        tx={"transaction_id":"t","candidates":[{"candidate_id":"D5-C01","engine_id":"D5"},{"candidate_id":"D2-C01","engine_id":"D2"}]}
        out=compile_terminal_state(tx,[])
        self.assertEqual(out["status"],"TERMINAL_IN_PROGRESS")
        self.assertFalse(out["winner_declared"])
        self.assertTrue(all(r["retain_in_manuscript"] for r in out["candidate_adjudications"]))

    def test_scientific_stop_requires_counterevidence(self):
        with self.assertRaisesRegex(ValueError,"closure-authority"):
            validate_candidate_adjudication({"terminal_state":"SCIENTIFIC_STOP","closure_authority":"","evidence_refs":["E1"],"retain_in_manuscript":False})

    def test_winner_requires_all_terminal_and_unique_paper_credit(self):
        tx={"transaction_id":"t","candidates":[{"candidate_id":"D5-C01","engine_id":"D5"},{"candidate_id":"D2-C01","engine_id":"D2"}]}
        ads=[
            {"candidate_id":"D5-C01","terminal_state":"COMPLETE_PAPER","unique_paper_credit":True,"manuscript_artifact":"paper.pdf","paper_qa_pass":True,"closure_authority":"","evidence_refs":["E1"]},
            {"candidate_id":"D2-C01","terminal_state":"SCIENTIFIC_STOP","unique_paper_credit":False,"closure_authority":"same_information_reduction","evidence_refs":["E2"],"retain_in_manuscript":False},
        ]
        out=compile_terminal_state(tx,ads)
        self.assertEqual(out["status"],"TERMINAL_COMPLETE")
        self.assertEqual(out["winner"],"D5")


if __name__=="__main__":unittest.main()
