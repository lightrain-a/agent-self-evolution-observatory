from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOVELTY = ROOT / "c1-transport-engineering-novelty-audit-20260828.json"
CONTRACT = ROOT / "c1-transport-guided-repair-pilot-contract-20260828.json"
PREFLIGHT = ROOT / "c1-transport-guided-repair-data-preflight-20260828.json"
PILOT_FREEZE = ROOT / "c1-transport-guided-repair-pilot-freeze-20260828.json"
SMOKE_ADJUDICATION = ROOT / "c1-transport-guided-repair-smoke-adjudication-20260828.json"


class C1TransportGuidedRepairDesignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.novelty = json.loads(NOVELTY.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
        cls.pilot_freeze = json.loads(PILOT_FREEZE.read_text(encoding="utf-8"))
        cls.smoke = json.loads(SMOKE_ADJUDICATION.read_text(encoding="utf-8"))

    def test_zero_authority_and_no_fake_execution(self) -> None:
        self.assertTrue(self.contract["status"].startswith("FROZEN_DESIGN_"))
        self.assertFalse(any(self.contract["authority"].values()))
        self.assertEqual(self.contract["pilot_sequence"]["pilot"]["execution_status"], "NOT_AUTHORIZED_BY_THIS_CONTRACT")
        self.assertEqual(self.contract["pilot_sequence"]["full"]["execution_status"], "LOCKED")
        self.assertFalse(any(self.novelty["authority"].values()))

    def test_novelty_does_not_relabel_published_utilization_work(self) -> None:
        rows = {row["work"]: row for row in self.novelty["published_nearest_work"]}
        self.assertIn("Mem2ActBench: A Benchmark for Evaluating Long-Term Memory Utilization in Task-Oriented Autonomous Agents", rows)
        self.assertIn("MemCoRL: Alternating Co-Optimization of Memory Retrieval and Utilization via Collaborative Reinforcement Learning", rows)
        self.assertIn("Chain-of-Memory: Lightweight Memory Construction with Dynamic Evolution for LLM Agents", rows)
        self.assertEqual(
            self.novelty["adjudication"]["generic_utilization_method"],
            "REJECT_COLLISION_WITH_MEMCORL_AND_CHAIN_OF_MEMORY",
        )
        forbidden = "\n".join(self.novelty["forbidden_claims"]).lower()
        self.assertIn("retrieval is not utilization is new", forbidden)
        self.assertIn("post-retrieval utilization optimization is new", forbidden)

    def test_current_signature_targets_only_post_retrieval_integration(self) -> None:
        design = self.contract["design"]
        frozen = set(design["frozen_across_arms"])
        self.assertIn("retriever output", frozen)
        self.assertIn("retrieved packet bytes and order", frozen)
        self.assertIn("memory bank content", frozen)
        self.assertIn("policy model and revision", frozen)
        arms = {row["id"]: row for row in design["arms"]}
        self.assertEqual(set(arms), {"A0_NATIVE", "A1_MEMORY_BLIND_DECISION_CHECK", "A2_MEMORY_USE_CHECK"})
        self.assertNotIn("REUSABLE MEMORY", arms["A1_MEMORY_BLIND_DECISION_CHECK"]["clause"])
        self.assertIn("REUSABLE MEMORY", arms["A2_MEMORY_USE_CHECK"]["clause"])
        self.assertIn("exposure-to-uptake", arms["A2_MEMORY_USE_CHECK"]["purpose"])

    def test_credit_rule_does_not_promote_write_or_exposure_to_behavior(self) -> None:
        credits = {row["stage"]: row for row in self.contract["engineering_principle_under_test"]["credit_rule"]}
        self.assertEqual(credits["write"]["credit"], "STATE_CHANGE_ONLY")
        self.assertEqual(credits["exposure"]["credit"], "AVAILABILITY_ONLY")
        self.assertEqual(credits["uptake"]["credit"], "BEHAVIORAL_CONTROL")
        self.assertEqual(credits["outcome"]["credit"], "UTILITY_VALIDATION")
        self.assertIn("do not infer policy use", credits["exposure"]["meaning"].lower())

    def test_adjudication_is_falsifiable(self) -> None:
        adjudication = self.contract["adjudication"]
        self.assertIn("NARROW", adjudication["A2_realized_but_U_not_moved"])
        self.assertIn("GENERIC_DECISION_CHECK_SENSITIVITY", adjudication["A2_equals_A1_or_both_move"])
        self.assertIn("boundary shifts downstream", adjudication["U_moves_but_O_does_not"])
        self.assertIn("INVALID_EXECUTION", adjudication["packet_invariance_fails"])

    def test_persistence_contract_requires_per_case_evidence(self) -> None:
        during = "\n".join(self.contract["artifact_persistence_contract"]["during_run"])
        self.assertIn("per-case", during)
        self.assertIn("retrieved-packet hash", during)
        self.assertIn("raw output", during)
        self.assertIn("resume cursor", during)

    def test_offline_packet_replay_preflight_is_exact_and_zero_provider(self) -> None:
        self.assertEqual(self.preflight["status"], "OFFLINE_PACKET_REPLAY_PREFLIGHT_PASS_NO_EXECUTION_AUTHORITY")
        checks = self.preflight["checks"]
        self.assertEqual(checks["frozen_task_units"], 36)
        self.assertEqual(checks["memory_wrappers_verified"], 72)
        self.assertEqual(checks["archived_native_prompt_hash_checks"], 288)
        self.assertTrue(checks["native_prompt_exact_replay"])
        self.assertEqual(checks["provider_calls"], 0)
        self.assertEqual(checks["new_scientific_outcomes"], 0)
        self.assertFalse(any(self.preflight["authority"].values()))
        self.assertEqual(len(self.preflight["rows"]), 36)
        arms = {row["id"]: row for row in self.contract["design"]["arms"]}
        import hashlib
        self.assertEqual(
            self.preflight["decision_check_clauses"]["A1_MEMORY_BLIND_DECISION_CHECK"]["sha256"],
            hashlib.sha256(arms["A1_MEMORY_BLIND_DECISION_CHECK"]["clause"].encode()).hexdigest(),
        )
        self.assertEqual(
            self.preflight["decision_check_clauses"]["A2_MEMORY_USE_CHECK"]["sha256"],
            hashlib.sha256(arms["A2_MEMORY_USE_CHECK"]["clause"].encode()).hexdigest(),
        )
        for row in self.preflight["rows"]:
            for branch in ("success", "failure"):
                prompts = row["prompt_sha256"][branch]
                self.assertEqual(len(set(prompts.values())), 3)

    def test_smoke_pass_does_not_unlock_pilot(self) -> None:
        self.assertEqual(self.smoke["attempt0"]["failure_layer"], "operationalization")
        self.assertEqual(self.smoke["attempt1"]["status"], "PASS_ZERO_PROVIDER_ENGINEERING_SMOKE_ONLY")
        self.assertEqual(self.smoke["attempt1"]["checks"]["provider_calls"], 0)
        self.assertEqual(self.smoke["adjudication"]["pilot_execution"], "LOCKED_NO_EXPLICIT_CURRENT_AUTHORITY")
        self.assertEqual(self.smoke["adjudication"]["scientific_claim_update"], "NONE")
        self.assertFalse(any(self.smoke["authority"].values()))

    def test_pilot_and_confirmatory_sets_are_frozen_disjoint_and_outcome_blind(self) -> None:
        freeze = self.pilot_freeze
        self.assertEqual(freeze["status"], "PILOT_PROTOCOL_FROZEN_EXECUTION_LOCKED")
        selection = freeze["selection"]
        self.assertEqual(selection["pilot_units"], 13)
        self.assertEqual(selection["confirmatory_holdout_units"], 23)
        pilot_ids = {row["future_task"] for row in selection["pilot"]}
        holdout_ids = {row["future_task"] for row in selection["confirmatory_holdout"]}
        self.assertTrue(pilot_ids.isdisjoint(holdout_ids))
        self.assertEqual(len(pilot_ids | holdout_ids), 36)
        self.assertIn("no B10 action or terminal outcome", selection["selection_input"])
        self.assertEqual(freeze["execution_geometry"]["pilot_provider_calls_if_authorized"], 312)
        self.assertEqual(freeze["execution_geometry"]["confirmatory_provider_calls_if_later_authorized"], 552)
        self.assertTrue(freeze["execution_geometry"]["pilot_never_pooled_into_confirmatory_inference"])
        self.assertFalse(any(freeze["authority"].values()))


if __name__ == "__main__":
    unittest.main()
