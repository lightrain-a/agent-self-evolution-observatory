from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone

from .paper_first_scientific_object_ontology import load_scientific_object_config
from .paper_first_scientific_object_retrieval_audit import audit_candidate_retrieval, public_shadow_scientific_object_retrieval_summary


class ScientificObjectRetrievalAuditTest(unittest.TestCase):
    NOW = datetime(2026, 8, 14, tzinfo=timezone.utc)

    def reviewed(self, idx: int, text: str) -> dict:
        return {
            "ref": f"arXiv:reviewed-{idx}",
            "title": text,
            "abstract": text,
            "primary_source_verified": True,
            "lane_keys": [],
            "empirical_facts": [{"text": "result"}],
            "typed_evidence": {
                "operational_assumptions": [],
                "measured_failures": [{"text": "failure"}],
                "boundary_observations": [],
            },
        }

    def paper(self, aid: str, title: str, date: str) -> dict:
        return {
            "paper_id": f"arxiv:{aid}",
            "title": title,
            "abstract": f"{title}. A self-evolving agent updates this state from interaction evidence.",
            "year": 2026,
            "metadata": {
                "externalIds": {"ArXiv": aid},
                "publicationDate": date,
                "citationCount": 0,
                "retrievalScore": 0.0,
                "matches": [{"route": "topic"}],
            },
        }

    def test_cutoff_crossing_old_page_rows_do_not_count_as_support(self) -> None:
        fresh = self.paper("2607.10001", "Self-Evolving Agent Knowledge Graph", "2026-07-10")
        old = self.paper("2605.10002", "Self-Evolving Agent Knowledge Graph", "2026-05-10")
        def searcher(**kwargs):
            return [fresh, old], []
        audit = audit_candidate_retrieval(
            candidate_key="knowledge_retrieval_state",
            queries=("q",),
            reviewed_records=[],
            reviewed_refs=set(),
            config=load_scientific_object_config(),
            searcher=searcher,
            now=self.NOW,
        )
        self.assertEqual(audit["fresh_candidate_support_refs"], 1)
        self.assertEqual(audit["new_candidate_support_refs"], 1)
        self.assertEqual([row["ref"] for row in audit["rows"]], ["arXiv:2607.10001"])
        self.assertEqual(audit["status"], "RECALL_GAP_FOUND_SUPPORT_STILL_INSUFFICIENT")

    def test_metadata_recall_gap_cannot_count_as_verified_support(self) -> None:
        reviewed = [self.reviewed(i, "Self-evolving knowledge graph") for i in range(1, 5)]
        new = self.paper("2608.20001", "Self-Evolving Agent Knowledge Graph", "2026-08-10")
        def searcher(**kwargs):
            return [new], []
        audit = audit_candidate_retrieval(
            candidate_key="knowledge_retrieval_state",
            queries=("q",),
            reviewed_records=reviewed,
            reviewed_refs={row["ref"] for row in reviewed},
            config=load_scientific_object_config(),
            searcher=searcher,
            now=self.NOW,
        )
        self.assertEqual(audit["current_verified_support"], 4)
        self.assertEqual(audit["potential_support_after_primary_verification"], 5)
        self.assertEqual(audit["status"], "PRIMARY_VERIFICATION_THRESHOLD_CANDIDATE")
        self.assertTrue(audit["primary_verification_required_before_support_count_changes"])
        self.assertFalse(audit["lane_preregistration_authorized"])
        self.assertFalse(audit["scientific_authority"])

    def test_incomplete_shadow_query_is_not_negative_evidence(self) -> None:
        new = self.paper("2608.30001", "Self-Evolving Agent Knowledge Graph", "2026-08-08")
        def searcher(**kwargs):
            return [new], ["q:FreshnessWindowTruncated:oldest=2026-07-01:cutoff=2026-06-15"]
        audit = audit_candidate_retrieval(
            candidate_key="knowledge_retrieval_state",
            queries=("q",),
            reviewed_records=[],
            reviewed_refs=set(),
            config=load_scientific_object_config(),
            searcher=searcher,
            now=self.NOW,
        )
        self.assertEqual(audit["status"], "SHADOW_RETRIEVAL_INCOMPLETE")
        self.assertEqual(audit["new_candidate_support_refs"], 1)
        self.assertTrue(audit["errors"])
        self.assertFalse(audit["live_query_set_change_authorized"])

    def test_public_summary_exposes_only_counts_and_zero_authority(self) -> None:
        private={"status":"SHADOW_OBJECT_RETRIEVAL_AUDIT_COMPLETE","results":{"knowledge_retrieval_state":{"status":"RECALL_GAP_FOUND_SUPPORT_STILL_INSUFFICIENT","current_verified_support":1,"minimum_verified_support":5,"potential_support_after_primary_verification":3,"new_candidate_support_refs":2,"new_direct_object_refs":2,"errors":[],"rows":[{"ref":"arXiv:secret","title":"private title"}],"queries":[{"query":"private query"}]}}}
        public=public_shadow_scientific_object_retrieval_summary(private)
        self.assertEqual(public["summary"]["recall_gap_support_insufficient"],1)
        self.assertEqual(public["summary"]["activation_authorized"],0)
        self.assertFalse(public["scientific_authority"])
        self.assertNotIn("rows",public["results"]["knowledge_retrieval_state"])
        self.assertNotIn("queries",public["results"]["knowledge_retrieval_state"])
        self.assertNotIn('"ref":',json.dumps(public))
        self.assertNotIn("private title",json.dumps(public))
        self.assertFalse(public["policy"]["live_query_set_changed"])

    def test_frozen_pairwise_validator_is_not_direct_evaluator_recall(self) -> None:
        pairwise = self.paper("2607.14408", "Reward-Free Evolving Agents via Pairwise Validator", "2026-07-15")
        pairwise["abstract"] += " The pairwise validator is a frozen LLM and requires no training of its own."
        def searcher(**kwargs):
            return [pairwise], []
        audit = audit_candidate_retrieval(
            candidate_key="evaluator_reward_verifier",
            queries=("q",),
            reviewed_records=[],
            reviewed_refs=set(),
            config=load_scientific_object_config(),
            searcher=searcher,
            now=self.NOW,
        )
        self.assertEqual(audit["new_candidate_support_refs"], 1)
        self.assertEqual(audit["new_direct_object_refs"], 0)
        self.assertEqual(audit["status"], "RECALL_GAP_FOUND_SUPPORT_STILL_INSUFFICIENT")


if __name__ == "__main__":
    unittest.main()
