from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REDUCTION = ROOT / "generated/asset-first-stri-r2-credit-fragmentation-novelty-reduction-20260825.json"
P0 = ROOT / "generated/asset-first-stri-r2-credit-fragmentation-result-20260825.json"
P1 = ROOT / "generated/asset-first-stri-r2-credit-fragmentation-phase-result-20260825.json"
P15 = ROOT / "generated/p15-pathbench-task-order-closure-readjudication-20260824.json"


class CreditFragmentationNoveltyReductionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.state = json.loads(REDUCTION.read_text(encoding="utf-8"))
        cls.p0 = json.loads(P0.read_text(encoding="utf-8"))
        cls.p1 = json.loads(P1.read_text(encoding="utf-8"))

    def test_survivor_is_narrow_and_does_not_claim_absorbed_general_novelties(self) -> None:
        self.assertEqual(self.state["status"], "SURVIVES_NARROWLY_AS_STAGE_LOCAL_CREDIT_FRAGMENTATION")
        not_novel = set(self.state["formal_residual"]["not_claimed_as_novel"])
        self.assertIn("quotient dynamics or lumpability in general", not_novel)
        self.assertIn("identity fragmentation as a generic statistical phenomenon", not_novel)
        self.assertIn("replication-proof action selection in bandits", not_novel)
        self.assertIn("representation-dependent optimization trajectories", not_novel)

    def test_reduction_matrix_covers_required_neighbor_classes(self) -> None:
        rows = self.state["reduction_matrix"]
        self.assertEqual(len(rows), 10)
        names = "\n".join(row["neighbor"] for row in rows).lower()
        for marker in (
            "strategic replication", "action redundancy", "homomorphism", "representation-dependent optimization",
            "identity fragmentation", "path-bench", "reconvergence", "skillos", "rethinking self-evolving", "skillsvote",
        ):
            self.assertIn(marker, names)
        self.assertTrue(all(row.get("same_information_test") for row in rows))
        self.assertTrue(all(row.get("disposition") for row in rows))
        self.assertTrue(all(row.get("novelty_implication") for row in rows))

    def test_p0_and_p1_are_bound_without_claim_expansion(self) -> None:
        evidence = self.state["deterministic_evidence"]
        self.assertEqual(self.p0["decision"], evidence["p0_decision"])
        self.assertEqual(self.p1["decision"], evidence["p1_decision"])
        self.assertEqual(self.p1["grid"]["cells"], 882)
        self.assertEqual(self.p1["headline"]["analytic_mismatches"], 0)
        self.assertEqual(evidence["new_model_calls"], 0)
        self.assertEqual(evidence["new_agent_runs"], 0)
        self.assertEqual(evidence["new_gpu_runs"], 0)

    def test_p15_closure_is_preserved(self) -> None:
        p15 = json.loads(P15.read_text(encoding="utf-8"))
        row = next(row for row in self.state["reduction_matrix"] if "P15" in row["neighbor"])
        self.assertEqual(row["disposition"], "DISTINCT_INTERVENTION_OBJECT")
        same_info = row["same_information_test"].lower()
        self.assertIn("feedback sequence/content", same_info)
        self.assertIn("fixed", same_info)
        self.assertIn("remove retrieval/order", same_info)
        self.assertTrue(p15.get("scientific_authority") is False)

    def test_current_gate_allows_only_zero_model_decomposition(self) -> None:
        gate = self.state["gate"]
        self.assertEqual(gate["decision"], "GO_ZERO_MODEL_2X2_CONTROLLER_DECOMPOSITION")
        forbidden = "\n".join(gate["not_authorized"]).lower()
        self.assertIn("llm or agent", forbidden)
        self.assertIn("gpu", forbidden)
        self.assertIn("task-utility", forbidden)
        self.assertIn("r2 title/manuscript replacement", forbidden)
        self.assertFalse(self.state["scientific_authority"])
        self.assertFalse(self.state["experiment_authority"])
        self.assertFalse(self.state["gpu_authority"])
        self.assertFalse(self.state["submission_authority"])

    def test_prevalence_and_behavior_boundaries_remain_explicit(self) -> None:
        realization = self.state["first_party_realization"]
        self.assertFalse(realization["natural_prevalence_resolved"])
        why_not = self.state["reduction_summary"]["why_not_yet_main_story"]
        self.assertIn("Natural prevalence", why_not)
        self.assertIn("one released system", why_not)
        self.assertIn("no downstream task-utility", why_not.lower())
        self.assertIn("R19", why_not)


if __name__ == "__main__":
    unittest.main()
