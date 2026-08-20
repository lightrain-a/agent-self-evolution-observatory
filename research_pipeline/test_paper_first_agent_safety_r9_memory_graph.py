from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_memory_graph import (
    CAUSAL_HOLD_CLAIM_ID,
    REOPEN_CONDITION,
    SUPPORTED_CLAIM_ID,
    build_memory_graph_inputs,
    build_paper_claim_table,
    compile_memory_graph_inputs,
    load_receipt,
    render_claim_table_tex,
)
from .research_memory_wiki import build_research_memory_wiki
from .scientific_research_graph import build_scientific_research_graph


class AgentSafetyR9MemoryGraphTest(unittest.TestCase):
    def test_real_receipt_compiles_paper_claim_table(self) -> None:
        table, bundle = compile_memory_graph_inputs()
        self.assertEqual(table["status"], "READY_AGENT_SAFETY_R9_PAPER_CLAIM_TABLE")
        self.assertEqual(
            table["columns"],
            ["supported_claim", "not_supported_claim", "limitation"],
        )
        self.assertEqual(len(table["rows"]), 4)
        self.assertTrue(table["rows"][0]["supported_claim"])
        self.assertTrue(all(row["not_supported_claim"] for row in table["rows"]))
        self.assertTrue(all(row["limitation"] for row in table["rows"]))
        self.assertEqual(
            bundle["status"], "READY_AGENT_SAFETY_R9_MEMORY_GRAPH_2_1_INPUTS"
        )
        self.assertEqual(bundle["summary"]["supported_narrowly"], 1)
        self.assertEqual(bundle["summary"]["method_holds"], 1)
        self.assertEqual(bundle["summary"]["scientific_closures"], 0)
        self.assertEqual(bundle["reopen_condition"]["condition"], REOPEN_CONDITION)
        self.assertFalse(bundle["reopen_condition"]["automatic_reopen"])
        self.assertFalse(bundle["reopen_condition"]["new_behavior_execution_authorized"])
        tex = render_claim_table_tex(table)
        self.assertIn("Supported claim & Not supported claim & Limitation", tex)
        self.assertIn("tab:r9-future-hazard-claim-boundary", tex)

    def test_receipt_inputs_materialize_typed_claim_hold_and_reopen_nodes(self) -> None:
        table, bundle = compile_memory_graph_inputs()
        wiki = build_research_memory_wiki(
            search_design_state={},
            failure_asset_library={},
            scientific_meta_trace={},
            candidate_portfolio={},
            experiment_iteration={},
            generator_state={},
            claim_ledger=bundle["claim_ledger"],
            supplemental_entries=bundle["supplemental_memory_entries"],
            generated_at="2026-08-20T00:00:00+00:00",
        )
        self.assertEqual(wiki["status"], "MEMORY_COMPILED")
        self.assertEqual(wiki["lint"]["status"], "PASS")
        self.assertEqual(wiki["summary"]["holds"], 1)
        self.assertEqual(wiki["summary"]["success_assets"], 1)
        self.assertEqual(wiki["summary"]["scientific_closures"], 0)

        graph = build_scientific_research_graph(
            evidence_graph={"nodes": [], "edges": []},
            candidate_portfolio={},
            scientific_meta_trace={},
            failure_asset_library={},
            pilot_registry={},
            research_memory_wiki=wiki,
            claim_ledger=bundle["claim_ledger"],
        )
        self.assertEqual(graph["schema_version"], "2.1")
        self.assertEqual(graph["status"], "RESEARCH_GRAPH_COMPILED")
        self.assertEqual(graph["lint"]["status"], "PASS")
        by_id = {row["id"]: row for row in graph["overlay_nodes"]}
        self.assertEqual(
            by_id[f"claim:{SUPPORTED_CLAIM_ID}"]["adjudication_status"],
            "SUPPORTED_NARROWLY",
        )
        self.assertEqual(
            by_id[f"claim:{CAUSAL_HOLD_CLAIM_ID}"]["adjudication_status"],
            "HOLD_METHOD_IDENTIFICATION",
        )
        hold = by_id["closure:MEM-HOLD-AGENT-SAFETY-R9-UPDATE-VS-SCHEDULE"]
        reopen = by_id["reopen:MEM-HOLD-AGENT-SAFETY-R9-UPDATE-VS-SCHEDULE"]
        self.assertEqual(hold["kind"], "hold")
        self.assertEqual(hold["affected_layer"], "method")
        self.assertEqual(reopen["kind"], "reopen_condition")
        self.assertEqual(reopen["label"], REOPEN_CONDITION)
        self.assertEqual(graph["summary"]["scientific_closure_nodes"], 0)
        self.assertEqual(graph["summary"]["principle_closure_edges"], 0)
        self.assertTrue(
            any(
                edge["source"] == hold["id"]
                and edge["target"] == reopen["id"]
                and edge["relation"] == "reopens_if"
                for edge in graph["overlay_edges"]
            )
        )
        self.assertTrue(
            any(
                edge["source"] == hold["id"]
                and edge["target"] == f"claim:{CAUSAL_HOLD_CLAIM_ID}"
                and edge["relation"] == "search_control_for"
                for edge in graph["overlay_edges"]
            )
        )
        self.assertEqual(table["table_sha256"], bundle["claim_table_sha256"])

    def test_tampered_receipt_cannot_enter_memory(self) -> None:
        receipt = load_receipt()
        tampered = copy.deepcopy(receipt)
        tampered["future_first_violation"]["branches_with_first_violation"] = 7
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            import json

            path.write_text(json.dumps(tampered), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "future hazard evidence drift"):
                load_receipt(path)

    def test_builders_preserve_zero_authority(self) -> None:
        receipt = load_receipt()
        table = build_paper_claim_table(receipt, receipt_ref="receipt#sha256=x")
        bundle = build_memory_graph_inputs(
            receipt,
            receipt_ref="receipt#sha256=x",
            claim_table_sha256=table["table_sha256"],
        )
        self.assertFalse(table["scientific_authority"])
        self.assertFalse(bundle["scientific_authority"])
        self.assertTrue(
            all(row["scientific_authority"] is False for row in bundle["claim_ledger"])
        )
        self.assertTrue(
            all(
                row["scientific_authority"] is False
                for row in bundle["supplemental_memory_entries"]
            )
        )


if __name__ == "__main__":
    unittest.main()
