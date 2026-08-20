from __future__ import annotations

import copy
import unittest

from .scientific_research_graph import (
    build_scientific_research_graph,
    can_propagate_closure,
    lint_scientific_research_graph,
)


def _graph(**overrides):
    data = {
        "evidence_graph": {
            "nodes": [{"id": "paper:P", "kind": "paper"}, {"id": "idea:I", "kind": "idea"}],
            "edges": [],
        },
        "candidate_portfolio": {
            "rows": [{
                "candidate_id": "I",
                "title": "typed candidate",
                "phenomenon": "persistent-state divergence",
                "problem_text": "Does persistence change future hazard?",
                "scientific_object": "persistent-agent",
                "mechanism": "state-carryover",
                "claim_type": "mechanism",
                "method": "matched longitudinal audit",
            }]
        },
        "scientific_meta_trace": {
            "principles": [{
                "principle_id": "PR",
                "idea_id": "I",
                "mechanism": "state-carryover",
                "belief_state": "closed",
            }]
        },
        "failure_asset_library": {
            "assets": [{
                "idea_id": "I",
                "phase": "F0",
                "signature": "runtime:ssh-timeout",
                "affected_layer": "runtime",
                "does_not_imply": "scientific failure",
            }],
            "dead_end_registry": {
                "certified_principle_dead_ends": [{
                    "principle_id": "PR",
                    "principle_dead_end_certified": True,
                    "counter_explanation": "same-information reduction",
                    "scientific_object": "persistent-agent",
                    "mechanism": "state-carryover",
                    "claim_type": "mechanism",
                    "reopen_condition": "new matched evidence defeats the reduction",
                }]
            },
        },
        "pilot_registry": {
            "phases": [{"idea_id": "I", "phase": "F0", "title": "F0", "status": "stopped"}]
        },
        "research_memory_wiki": {
            "entries": [{
                "memory_id": "S1",
                "kind": "SUCCESS_ASSET",
                "title": "narrow success",
                "candidate_id": "C-SAME",
                "scope": "matched only",
                "affected_layer": "mechanism",
                "source_refs": ["E1"],
            }]
        },
        "claim_ledger": [
            {
                "claim_id": "C-SAME",
                "claim_text": "same scoped claim",
                "claim_type": "mechanism",
                "scientific_object": "persistent-agent",
                "mechanism": "state-carryover",
                "adjudication_status": "SUPPORTED_NARROWLY",
                "trace_complete": True,
                "evidence_ids": ["E1"],
            },
            {
                "claim_id": "C-OTHER",
                "claim_text": "other object claim",
                "claim_type": "mechanism",
                "scientific_object": "memoryless-agent",
                "mechanism": "state-carryover",
                "adjudication_status": "UNRESOLVED",
                "trace_complete": False,
                "evidence_ids": [],
            },
        ],
        "experiment_iteration": {},
    }
    data.update(overrides)
    return build_scientific_research_graph(**data)


class ResearchMemoryGraphV2Test(unittest.TestCase):
    def test_typed_pipeline_and_failure_boundaries(self):
        graph = _graph()
        self.assertEqual(graph["schema_version"], "2.0")
        self.assertEqual(graph["status"], "RESEARCH_GRAPH_COMPILED")
        self.assertEqual(graph["lint"]["status"], "PASS")
        self.assertGreaterEqual(graph["summary"]["phenomenon_nodes"], 1)
        self.assertGreaterEqual(graph["summary"]["problem_contract_nodes"], 1)
        self.assertGreaterEqual(graph["summary"]["method_nodes"], 1)
        failure = next(row for row in graph["overlay_nodes"] if row["kind"] == "failure_asset")
        self.assertEqual(failure["failure_class"], "runtime")
        self.assertFalse(failure["scientific_negative"])
        self.assertFalse(any(edge["source"] == failure["id"] and edge["relation"].startswith("closes_") for edge in graph["overlay_edges"]))

    def test_closure_propagates_only_on_exact_three_key_scope(self):
        graph = _graph()
        propagation = [edge for edge in graph["overlay_edges"] if edge["relation"] == "propagates_closure"]
        self.assertEqual(len(propagation), 1)
        self.assertEqual(propagation[0]["target"], "claim:C-SAME")
        closure = next(row for row in graph["overlay_nodes"] if row["id"] == propagation[0]["source"])
        same = next(row for row in graph["overlay_nodes"] if row["id"] == "claim:C-SAME")
        other = next(row for row in graph["overlay_nodes"] if row["id"] == "claim:C-OTHER")
        self.assertTrue(can_propagate_closure(closure, same))
        self.assertFalse(can_propagate_closure(closure, other))
        reopen = next(row for row in graph["overlay_nodes"] if row["id"] == closure["reopen_condition_id"])
        self.assertEqual(reopen["kind"], "reopen_condition")

    def test_missing_scope_key_blocks_propagation(self):
        library = copy.deepcopy(_graph()["base_graph"])
        del library
        failure_library = {
            "assets": [],
            "dead_end_registry": {
                "certified_principle_dead_ends": [{
                    "principle_id": "PR",
                    "principle_dead_end_certified": True,
                    "counter_explanation": "underspecified closure",
                    "scientific_object": "persistent-agent",
                    "mechanism": "state-carryover",
                }]
            },
        }
        graph = _graph(failure_asset_library=failure_library)
        self.assertEqual(graph["summary"]["exact_scope_propagation_edges"], 0)
        self.assertEqual(graph["lint"]["status"], "PASS")

    def test_claim_conflict_is_visible_but_not_resolved(self):
        claims = [
            {
                "claim_id": "A", "claim_text": "x", "claim_type": "mechanism",
                "scientific_object": "o", "mechanism": "m",
                "adjudication_status": "SUPPORTED", "trace_complete": True,
            },
            {
                "claim_id": "B", "claim_text": "x", "claim_type": "mechanism",
                "scientific_object": "o", "mechanism": "m",
                "adjudication_status": "REJECTED", "trace_complete": True,
            },
        ]
        graph = _graph(claim_ledger=claims)
        self.assertEqual(graph["summary"]["claim_conflicts"], 1)
        self.assertFalse(graph["claim_conflicts"][0]["automatic_resolution"])

    def test_lint_rejects_scope_mismatched_propagation(self):
        graph = _graph()
        bad = copy.deepcopy(graph)
        edge = next(row for row in bad["overlay_edges"] if row["relation"] == "propagates_closure")
        edge["target"] = "claim:C-OTHER"
        lint = lint_scientific_research_graph(bad)
        self.assertEqual(lint["status"], "FAIL")
        self.assertIn("closure-propagation-scope-mismatch", {row["code"] for row in lint["errors"]})


if __name__ == "__main__":
    unittest.main()
