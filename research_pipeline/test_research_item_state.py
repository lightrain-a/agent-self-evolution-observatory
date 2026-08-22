from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from research_pipeline.research_item_state import (
    build_paper_registry,
    build_research_item_state,
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
        self.assertEqual(summary["research_items"], 87)
        self.assertEqual(summary["experiment_records"], 30)
        self.assertEqual(summary["portfolio_experiment_contexts"], 3)
        self.assertEqual(summary["evidence_contexts"], 2)
        self.assertEqual(summary["portfolio_objects"], 92)
        self.assertEqual(
            {key: value["portfolio_total"] for key, value in summary["by_category"].items()},
            {"A": 12, "B": 21, "C": 10, "D": 3, "E": 27, "F": 6, "G": 13},
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
        self.assertEqual(counts, {"NO_INTERNAL_ACTION": 71, "MERGED_NO_STANDALONE_ACTION": 10, "REOPEN_CONDITION_REQUIRED": 5, "PAPERSTATE_HANDOFF": 1})
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
        self.assertEqual((p04["scientific_state"], p04["failure_layer"]), ("STOPPED", "problem_novelty"))
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
            self.assertTrue(temporal["gate_clean_submission_ready"])
            self.assertFalse(temporal["immediate_submission_hold"])
            self.assertEqual(temporal["source_kind"], "paper-first-discovery-candidate")
            self.assertIsNone(temporal["source_research_item"])
            self.assertEqual(temporal["source_candidates"], ["D2-C06"])
            self.assertEqual(temporal["title"], "When Reusable Temporal Skills Become Causal Bottlenecks in Evolving Time-Series Agents")
            preparation = temporal["latest_paper_preparation"]
            self.assertTrue(preparation["pass"])
            self.assertEqual((preparation["passed_gates"], preparation["required_gates"]), (8, 8))
            context = temporal["submission_readiness_context"]
            self.assertEqual(context["recommended_immediate_submission"], "READY_FOR_HUMAN_SUBMISSION")
            self.assertEqual(context["support_blocker"], "")
            self.assertEqual((temporal["source_native_evidence"]["runtime_valid_rows"], temporal["source_native_evidence"]["distinct_endpoints"], temporal["source_native_evidence"]["institutional_systems"]), (1326, 35, 3))
            self.assertEqual((temporal["latest_mock_review"]["summary"] or {}).get("scores"), [8, 8, 7])
            self.assertEqual(self.registry["summary"]["papers"], 5)
            self.assertEqual(self.registry["summary"]["submission_ready"], 5)
            self.assertEqual(self.registry["summary"]["gate_clean_submission_ready"], 5)
            self.assertEqual(self.registry["summary"]["paper_preparation_failed"], 0)
            self.assertEqual(self.registry["summary"]["immediate_submission_holds"], 0)
            self.assertEqual(self.registry["summary"]["internal_action_required"], 0)
            self.assertEqual(self.registry["summary"]["no_internal_action"], 5)
            self.assertEqual(self.registry["summary"]["by_internal_action"], {"NO_INTERNAL_ACTION": 5})
            self.assertEqual(temporal["primary_next_action"]["action_class"], "NO_INTERNAL_ACTION")
            self.assertEqual(temporal["primary_next_action"]["blocking_on"], "")
            for paper_id, candidate in papers.items():
                self.assertTrue(candidate["gate_clean_submission_ready"], paper_id)
                self.assertTrue(candidate["latest_paper_preparation"]["pass"], paper_id)
                self.assertEqual(candidate["primary_next_action"]["action_class"], "NO_INTERNAL_ACTION", paper_id)
            failure = papers["D2-PAPER-FAILURE-MEMORY-PROVENANCE"]
            self.assertEqual(failure["paper_stage"], "SUBMISSION_READY")
            self.assertEqual(failure["active_unrefuted_claims"], 2)
            serialized = json.dumps(self.registry, ensure_ascii=False)
            for private_marker in ("/home/wyt", "/data/wyt", "10.42.8.52", "222.20.126.69"):
                self.assertNotIn(private_marker, serialized)

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
