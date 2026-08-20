from __future__ import annotations

import copy
import unittest

from .claim_evidence_traceability import (
    build_claim_evidence_traceability,
    validate_claim_evidence_traceability,
)
from .paper_first_agent_safety_r9_memory_graph import compile_memory_graph_inputs
from .paper_first_agent_safety_r9_reopen_control import compile_reopen_control_design
from .scientific_research_graph import build_scientific_research_graph


class ClaimEvidenceTraceabilityTest(unittest.TestCase):
    def build(self):
        table, memory = compile_memory_graph_inputs()
        control = compile_reopen_control_design()
        return build_claim_evidence_traceability(
            program_id="AGENT-SAFETY-R9",
            candidate_id="SHADOW-P01-C01",
            claim_table=table,
            memory_bundle=memory,
            receipt_ref=memory["receipt_ref"],
            control_design=control,
        )

    def test_claim_evidence_limitation_and_counterevidence_are_explicit(self) -> None:
        bundle = self.build()
        summary = bundle["summary"]
        self.assertEqual(summary["supported_claims_bound"], 1)
        self.assertEqual(summary["not_supported_claim_boundaries"], 4)
        self.assertEqual(summary["limitations_bound"], 4)
        self.assertEqual(summary["counterevidence_bound"], 2)
        self.assertEqual(summary["control_designs_bound"], 1)
        relations = {row["relation"] for row in bundle["edges"]}
        self.assertIn("supports_claim", relations)
        self.assertIn("limits_claim", relations)
        self.assertIn("challenges_claim", relations)
        self.assertIn("tests_identification_for", relations)
        self.assertIn("gates_control_design", relations)
        self.assertEqual(validate_claim_evidence_traceability(bundle), [])

    def test_traceability_is_zero_authority(self) -> None:
        bundle = self.build()
        self.assertFalse(bundle["scientific_authority"])
        self.assertTrue(all(row["scientific_authority"] is False for row in bundle["nodes"]))
        self.assertTrue(all(row["scientific_authority"] is False for row in bundle["edges"]))
        control_nodes = [
            row for row in bundle["nodes"]
            if row["kind"] in {"control_design", "authorization_gate"}
        ]
        self.assertTrue(control_nodes)
        self.assertTrue(all(row["execution_authorized"] is False for row in control_nodes))

    def test_memory_graph_21_materializes_traceability_without_authority(self) -> None:
        table, memory = compile_memory_graph_inputs()
        trace = self.build()
        graph = build_scientific_research_graph(
            evidence_graph={"nodes": [], "edges": []},
            candidate_portfolio={"rows": []},
            scientific_meta_trace={},
            failure_asset_library={},
            pilot_registry={},
            claim_ledger=memory["claim_ledger"],
            claim_evidence_traceability=trace,
        )
        self.assertEqual(graph["status"], "RESEARCH_GRAPH_COMPILED")
        self.assertEqual(graph["lint"]["summary"]["errors"], 0)
        bindings = graph["claim_evidence_bindings"]
        self.assertEqual(bindings["source_bundle_sha256"], trace["bundle_sha256"])
        self.assertEqual(bindings["limitations_bound"], 4)
        self.assertEqual(bindings["counterevidence_bound"], 2)
        self.assertEqual(graph["summary"]["control_design_nodes"], 1)
        self.assertEqual(graph["summary"]["authorization_gate_nodes"], 1)
        self.assertFalse(graph["scientific_authority"])

    def test_hash_mutation_is_detected(self) -> None:
        bundle = self.build()
        mutated = copy.deepcopy(bundle)
        mutated["nodes"][0]["label"] = "drift"
        self.assertIn(
            "claim/evidence traceability hash drift",
            validate_claim_evidence_traceability(mutated),
        )


if __name__ == "__main__":
    unittest.main()
