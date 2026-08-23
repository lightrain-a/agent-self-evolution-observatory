from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from research_pipeline.research_item_state import (
    PUBLICATION_PAPER_REGISTRATIONS,
    build_discovery_provenance,
    build_paper_registry,
    build_publication_identities,
    build_research_item_state,
    discovery_candidate_alias,
    paper_acceptance_state,
    validate_paper_registry,
    validate_research_item_state,
)


class ResearchItemStateTest(unittest.TestCase):
    def test_empty_machine_local_ledger_uses_portable_registry_even_when_system_snapshot_is_newer(self) -> None:
        with open("generated/paper-registry.json", encoding="utf-8") as handle:
            registry = json.load(handle)
        self.assertGreaterEqual(int((registry.get("summary") or {}).get("papers") or 0), 2)
        empty_index = {
            "summary": {"papers": 0, "invalid_ledgers": 0, "scientific_holds": 0, "submission_ready": 0},
            "entries": [], "invalid": [], "scientific_authority": False,
        }
        system = {
            "generated_at": "9999-01-01T00:00:00+00:00",
            "paper_acceptance": {"summary": {}, "ledger_index": empty_index},
        }
        def load(name: str):
            if name == "research-system-state.json": return system
            if name == "paper-registry.json": return registry
            raise AssertionError(name)
        with patch("research_pipeline.research_item_state.load_generated", side_effect=load), patch("research_pipeline.research_item_state.build_paper_ledger_index", return_value=empty_index):
            acceptance, by_id = paper_acceptance_state()
        self.assertEqual(acceptance["projection_source"], "generated/paper-registry.json")
        self.assertIn("STRI-ICLR2027", by_id)
        self.assertIn("AGENT-SAFETY-R9", by_id)
        self.assertEqual(by_id["STRI-ICLR2027"]["current_state"], "SUBMISSION_READY")

    @classmethod
    def setUpClass(cls) -> None:
        cls.state = build_research_item_state()
        cls.registry = build_paper_registry(cls.state)
        cls.by_code = {row["code"]: row for row in cls.state["research_items"]}

    def test_projection_counts_and_categories(self) -> None:
        self.assertEqual(validate_research_item_state(self.state), [])
        summary = self.state["summary"]
        self.assertEqual(summary["research_items"], 88)
        self.assertEqual(summary["experiment_records"], 30)
        self.assertEqual(summary["portfolio_experiment_contexts"], 3)
        self.assertEqual(summary["evidence_contexts"], 2)
        self.assertEqual(summary["portfolio_objects"], 93)
        self.assertEqual(
            {key: value["portfolio_total"] for key, value in summary["by_category"].items()},
            {"A": 13, "B": 21, "C": 10, "D": 3, "E": 27, "F": 6, "G": 13},
        )

    def test_every_research_item_has_one_zero_authority_next_action(self) -> None:
        expected = {
            "STOPPED": "NO_INTERNAL_ACTION",
            "MERGED": "MERGED_NO_STANDALONE_ACTION",
            "HOLD": "REOPEN_CONDITION_REQUIRED",
            "PAPER_READY": "PAPERSTATE_HANDOFF",
        }
        counts = {}
        for row in self.state["research_items"]:
            action = row["primary_next_action"]
            self.assertEqual(action["action_class"], expected[row["scientific_state"]], row["code"])
            self.assertFalse(action["machine_actionable"], row["code"])
            self.assertFalse(any(action[key] for key in ("scientific_authority", "experiment_authority", "p0_authority", "gpu_authority")), row["code"])
            counts[action["action_class"]] = counts.get(action["action_class"], 0) + 1
        self.assertEqual(counts, {"NO_INTERNAL_ACTION": 72, "MERGED_NO_STANDALONE_ACTION": 10, "REOPEN_CONDITION_REQUIRED": 5, "PAPERSTATE_HANDOFF": 1})
        self.assertEqual(self.state["summary"]["primary_next_action_counts"], counts)
        self.assertEqual(self.state["summary"]["active_research_items"], 0)
        self.assertTrue(self.state["policy"]["zero_active_research_items_is_valid"])
        self.assertTrue(self.state["policy"]["visibility_tracking_does_not_create_active_slot"])
        self.assertEqual(self.state["summary"]["machine_actionable_research_items"], 0)
        self.assertEqual(self.by_code["F-4"]["scientific_state"], "STOPPED")
        self.assertNotEqual(self.by_code["F-4"]["portfolio_disposition"], "ACTIVE_RESEARCH")
        self.assertEqual(self.by_code["E-7"]["primary_next_action"]["paper_id"], "STRI")
        self.assertEqual(self.by_code["E-7"]["primary_next_action"]["paper_next_action_class"], "NO_INTERNAL_ACTION")

    def test_latest_shadow_search_memory_closure_is_projected(self) -> None:
        p04 = next(row for row in self.state["research_items"] if row["id"] == "SHADOW-P04-C01")
        self.assertEqual((p04["code"], p04["category"], p04["source_kind"]), ("B-21", "B", "shadow_closed"))
        self.assertEqual((p04["scientific_state"], p04["closure_layer"], p04["failure_layer"]), ("STOPPED", "problem_novelty", None))
        self.assertFalse(p04["principle_dead_end_certified"])
        self.assertIn(p04["provenance_refs"][0]["role"], {"typed_shadow_closure", "append_only_shadow_search_memory_closure"})

    def test_support_stop_is_not_scientific_stop(self) -> None:
        self.assertEqual(self.state["summary"]["parent_scientific_states"], {"HOLD": 4, "MERGED": 6, "STOPPED": 16})
        for code in ("A-3", "B-2", "B-3", "E-1"):
            self.assertEqual(self.by_code[code]["scientific_state"], "HOLD")
            self.assertFalse(self.by_code[code]["principle_dead_end_certified"])
            self.assertFalse(self.by_code[code]["execution_authority"]["gpu"])

    def test_stri_handoff_and_paper_registry(self) -> None:
        self.assertEqual(validate_paper_registry(self.registry, self.state), [])
        e7 = self.by_code["E-7"]
        self.assertEqual(e7["scientific_state"], "PAPER_READY")
        self.assertEqual(e7["paper_transition"]["paper_id"], "STRI")
        self.assertEqual(e7["paper_transition"]["status"], "SUBMISSION_READY")
        papers = {row["paper_id"]: row for row in self.registry["papers"]}
        paper = papers["STRI"]
        self.assertEqual(paper["source_research_item"], "E-7")
        self.assertEqual(paper["paper_stage"], "SUBMISSION_READY")
        self.assertTrue(paper["submission_ready"])
        self.assertGreaterEqual(self.registry["summary"]["papers"], 2)
        self.assertGreaterEqual(self.registry["summary"]["submission_ready"], 2)
        self.assertEqual(self.registry["summary"]["scientific_holds"], 0)
        self.assertEqual((paper["claims_supported"], paper["claims_total"], paper["paper_quality_evidence_debt"]), (3, 3, 0))
        safety = papers["AGENT-SAFETY-R9"]
        self.assertEqual((safety["source_research_item"], safety["paper_stage"], safety["scientific_status"]), ("G-1", "SUBMISSION_READY", "READY"))
        self.assertTrue(safety["submission_ready"])
        self.assertEqual(self.by_code["G-1"]["scientific_state"], "HOLD")
        temporal = papers.get("D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK")
        if temporal:
            self.assertEqual(temporal["paper_stage"], "SUBMISSION_READY")
            self.assertTrue(temporal["submission_ready"])
            self.assertEqual(temporal["source_kind"], "paper-first-discovery-candidate")
            self.assertIsNone(temporal["source_research_item"])
            self.assertEqual(temporal["source_candidates"], ["D2-C06"])
            self.assertEqual(temporal["title"], "When Reusable Temporal Skills Become Causal Bottlenecks in Evolving Time-Series Agents")
            preparation = temporal["latest_paper_preparation"]
            prep_pass = preparation.get("pass") is True
            self.assertEqual(temporal["gate_clean_submission_ready"], prep_pass)
            self.assertEqual(temporal["immediate_submission_hold"], not prep_pass)
            context = temporal["submission_readiness_context"]
            self.assertEqual(context["recommended_immediate_submission"], "READY_FOR_HUMAN_SUBMISSION")
            self.assertEqual(context["support_blocker"], "")
            self.assertEqual((temporal["source_native_evidence"]["runtime_valid_rows"], temporal["source_native_evidence"]["distinct_endpoints"], temporal["source_native_evidence"]["institutional_systems"]), (1326, 35, 3))
            self.assertEqual((temporal["latest_mock_review"]["summary"] or {}).get("scores"), [8, 8, 7])
            expected_action = "NO_INTERNAL_ACTION" if prep_pass else "PAPER_REPAIR_REQUIRED"
            self.assertEqual(temporal["primary_next_action"]["action_class"], expected_action)
            self.assertEqual(temporal["primary_next_action"]["blocking_on"], "" if prep_pass else "PAPER_PREPARATION_FAILED")
            summary = self.registry["summary"]
            self.assertEqual(summary["papers"], len(papers))
            self.assertEqual(summary["submission_ready"], sum(candidate.get("submission_ready") is True for candidate in papers.values()))
            self.assertEqual(summary["gate_clean_submission_ready"], sum(candidate.get("gate_clean_submission_ready") is True for candidate in papers.values()))
            self.assertEqual(summary["paper_preparation_failed"], sum((candidate.get("latest_paper_preparation") or {}).get("pass") is not True for candidate in papers.values()))
            self.assertEqual(summary["immediate_submission_holds"], sum(candidate.get("immediate_submission_hold") is True for candidate in papers.values()))
            self.assertEqual(summary["internal_action_required"], sum((candidate.get("primary_next_action") or {}).get("action_class") != "NO_INTERNAL_ACTION" for candidate in papers.values()))
            self.assertEqual(summary["no_internal_action"], sum((candidate.get("primary_next_action") or {}).get("action_class") == "NO_INTERNAL_ACTION" for candidate in papers.values()))
            for paper_id, candidate in papers.items():
                candidate_prep = (candidate.get("latest_paper_preparation") or {}).get("pass") is True
                self.assertEqual(candidate.get("gate_clean_submission_ready"), candidate_prep, paper_id)
                self.assertEqual((candidate.get("primary_next_action") or {}).get("action_class"), "NO_INTERNAL_ACTION" if candidate_prep else "PAPER_REPAIR_REQUIRED", paper_id)
            failure = papers["D2-PAPER-FAILURE-MEMORY-PROVENANCE"]
            self.assertEqual(failure["paper_stage"], "SUBMISSION_READY")
            self.assertEqual(failure["active_unrefuted_claims"], 2)
            serialized = json.dumps(self.registry, ensure_ascii=False)
            for private_marker in ("/home/wyt", "/data/wyt", "10.42.8.52", "222.20.126.69"):
                self.assertNotIn(private_marker, serialized)

    def test_publication_identity_is_category_local_and_does_not_replace_provenance(self) -> None:
        self.assertEqual(validate_paper_registry(self.registry, self.state), [])
        papers = {row["paper_id"]: row for row in self.registry["papers"]}
        expected_codes = {
            "STRI": "E1",
            "AGENT-SAFETY-R9": "G1",
            "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE": "C1",
            "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK": "E2",
            "D2-PAPER-FAILURE-MEMORY-PROVENANCE": "B1",
        }
        self.assertEqual({paper_id: row["publication_identity"]["code"] for paper_id, row in papers.items()}, expected_codes)
        self.assertEqual(self.registry["summary"]["publication_codes"], ["E1", "G1", "C1", "E2", "B1"])
        self.assertEqual(self.registry["summary"]["by_publication_category"], {"B": 1, "C": 1, "E": 2, "G": 1})
        self.assertEqual(papers["STRI"]["source_research_item"], "E-7")
        self.assertEqual(papers["AGENT-SAFETY-R9"]["source_research_item"], "G-1")
        for paper_id, row in papers.items():
            identity = row["publication_identity"]
            self.assertEqual(row["downloads"]["pdf"], identity["pdf"], paper_id)
            self.assertNotIn("-", identity["code"], paper_id)
            self.assertTrue(identity["label_zh"].startswith(f"{identity['code']} {identity['category_zh']} · "), paper_id)
            self.assertTrue(identity["label_en"].startswith(f"{identity['code']} {identity['category_en']} · "), paper_id)

        broken = json.loads(json.dumps(self.registry))
        broken["papers"][0]["publication_identity"]["code"] = "E7"
        self.assertTrue(any("publication identity drifted:STRI" in error or "invalid publication code/category:STRI" in error for error in validate_paper_registry(broken, self.state)))
        identities = build_publication_identities()
        self.assertEqual(identities["STRI"]["ordinal"], 1)
        self.assertEqual(identities["D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK"]["ordinal"], 2)
        appended = [*PUBLICATION_PAPER_REGISTRATIONS, {"paper_id": "FUTURE-E", "category": "E", "method": "Future Skill", "pdf_slug": "Future-Skill", "idea": {"zh": "未来技能论文", "en": "Future skill paper"}}]
        with patch("research_pipeline.research_item_state.PUBLICATION_PAPER_REGISTRATIONS", appended):
            future = build_publication_identities()["FUTURE-E"]
        self.assertEqual((future["code"], future["category_zh"], future["pdf"]), ("E3", "技能", "downloads/E3-Future-Skill.pdf"))

    def test_discovery_aliases_separate_historical_candidate_ids_from_public_categories(self) -> None:
        self.assertEqual(discovery_candidate_alias("D2-C02"), "DISC2-02")
        self.assertEqual(discovery_candidate_alias("D2-C6"), "DISC2-06")
        with self.assertRaises(ValueError):
            discovery_candidate_alias("PF-2")
        papers = {row["paper_id"]: row for row in self.registry["papers"]}
        proxy = papers["D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"]
        temporal = papers["D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK"]
        failure = papers["D2-PAPER-FAILURE-MEMORY-PROVENANCE"]
        self.assertEqual(proxy["discovery_provenance"]["candidate_aliases"], ["DISC2-02", "DISC2-05"])
        self.assertEqual(temporal["discovery_provenance"]["candidate_aliases"], ["DISC2-06"])
        self.assertEqual(failure["discovery_provenance"]["candidate_aliases"], ["DISC2-01", "DISC2-04"])
        self.assertEqual(temporal["discovery_provenance"]["historical_candidate_ids"], ["D2-C06"])
        self.assertTrue(temporal["discovery_provenance"]["historical_ids_hidden_by_default"])
        self.assertEqual(self.registry["summary"]["discovery_aliases"], ["DISC2-02", "DISC2-05", "DISC2-06", "DISC2-01", "DISC2-04"])
        self.assertEqual(build_discovery_provenance(["D2-C06"])["campaign_en"], "Paper-first Discovery Round 2")
        broken = json.loads(json.dumps(self.registry))
        broken_temporal = next(row for row in broken["papers"] if row["paper_id"] == "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK")
        broken_temporal["discovery_provenance"]["candidate_aliases"] = ["E2"]
        self.assertTrue(any("discovery provenance alias drifted" in error or "reader discovery alias collides" in error for error in validate_paper_registry(broken, self.state)))

    def test_experiments_are_zero_authority_evidence_events(self) -> None:
        self.assertTrue(all(row["scientific_authority"] is False for row in self.state["experiment_records"]))
        self.assertTrue(all(row["principle_update_authority"] is False for row in self.state["experiment_records"]))
        portfolio = [row for row in self.state["experiment_records"] if row.get("portfolio_context")]
        self.assertEqual({row["portfolio_code"] for row in portfolio}, {"E-7a", "E-7b", "E-7c"})

    def test_agent_safety_support_stop_is_not_principle_dead_end(self) -> None:
        g1 = self.by_code["G-1"]
        self.assertEqual(g1["scientific_state"], "HOLD")
        self.assertFalse(g1["principle_dead_end_certified"])
        self.assertEqual(g1["execution_authority"], {"method": False, "experiment": False, "p0": False, "gpu": False})


if __name__ == "__main__":
    unittest.main()
