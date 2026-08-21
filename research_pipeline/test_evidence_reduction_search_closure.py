from __future__ import annotations

import unittest

from .evidence_reduction_search_closure import build_evidence_reduction_search_closure


def plan() -> dict:
    return {"entries":[{"candidate_id":"C1","title":"candidate","status":"STOP_EXACT_REDUCTION_SUPPORTED","execution_authorized":False,"contract_sha256":"a"*64,"frozen_exact_prediction":"prediction","frozen_same_information_baseline":"baseline","source_refs":["arXiv:1"],"evidence_receipt":{"outcome":"REDUCTION_SUPPORTED","protocol_valid":True,"qualified_units":12,"evidence_manifest_sha256":"b"*64,"metric_summary":"metric"}}]}


class EvidenceReductionSearchClosureTest(unittest.TestCase):
    def test_uses_candidate_specific_reopen_condition_from_manifest(self):
        manifest={"candidate_id":"C1","contract_sha256":"a"*64,"evidence_manifest_sha256":"b"*64,"reopen_condition":"Reopen only if phase interaction survives on held-out matched tasks.","search_closure_avoid":["do not retune phase threshold"]}
        out=build_evidence_reduction_search_closure(evidence_plan=plan(),candidate_id="C1",evidence_manifest=manifest,evidence_manifest_uri="research-data://evidence.json")
        self.assertEqual(out["reopen_condition"],manifest["reopen_condition"])
        self.assertEqual(out["search_closure_avoid"],manifest["search_closure_avoid"])

    def test_generic_fallback_does_not_hardcode_skill_order_problem(self):
        manifest={"candidate_id":"C1","contract_sha256":"a"*64,"evidence_manifest_sha256":"b"*64}
        out=build_evidence_reduction_search_closure(evidence_plan=plan(),candidate_id="C1",evidence_manifest=manifest,evidence_manifest_uri="research-data://evidence.json")
        self.assertIn("same frozen scientific object",out["reopen_condition"])
        self.assertNotIn("same fixed skill set",out["reopen_condition"])


if __name__=="__main__": unittest.main()
