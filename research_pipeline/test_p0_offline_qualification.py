from __future__ import annotations

import unittest
from pathlib import Path

from .config import StorageSettings, resolve_experiment_data_root
from .p0_offline_qualification import build_p0_offline_qualification_state


class P0OfflineQualificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root=resolve_experiment_data_root(StorageSettings.from_env())
        required=root/"pre-experiment-a1-screening-review-20260810.json"
        if not required.exists():
            raise unittest.SkipTest("machine-local P0 evidence is unavailable")
        cls.state=build_p0_offline_qualification_state()

    def test_real_and_synthetic_evidence_stay_separate(self) -> None:
        s=self.state["summary"]
        self.assertEqual(s["ideas"],16)
        self.assertGreaterEqual(s["checks_passed"],20)
        self.assertGreaterEqual(s["checks_failed"],3)
        self.assertEqual(s["checks_synthetic_pass"],14)
        self.assertTrue(self.state["policy"]["method_result_from_offline_qualification_forbidden"])
        self.assertTrue(self.state["policy"]["same_batch_self_authorization_forbidden"])

    def test_a3_and_e1_failures_are_not_overridden_by_synthetic_harnesses(self) -> None:
        by_id={row["idea_id"]:row for row in self.state["cards"]}
        self.assertEqual(by_id["regression-gated-self-evolution"]["checks"]["representability"]["status"],"fail")
        self.assertEqual(by_id["workflow-generalization-certificate"]["checks"]["target_variation"]["status"],"fail")
        self.assertEqual(by_id["workflow-generalization-certificate"]["checks"]["effect_variation"]["status"],"fail")
        self.assertEqual(by_id["compositional-update-compatibility"]["gpu0"]["status"],"stop-direct-order-aware-risk-equivalent")
        self.assertEqual(by_id["compositional-update-compatibility"]["checks"]["baseline_disagreement"]["status"],"fail")
        self.assertEqual(by_id["lineage-aware-rollback"]["gpu0"]["status"],"stop-matched-generic-state-diff-dominates")
        self.assertEqual(by_id["lineage-aware-rollback"]["checks"]["baseline_disagreement"]["status"],"fail")
        self.assertEqual(by_id["counterfactual-evolution-decision-controller"]["checks"]["representability"]["status"],"synthetic-pass")
        self.assertEqual(by_id["counterfactual-evolution-decision-controller"]["checks"]["baseline_disagreement"]["status"],"fail")
        self.assertEqual(by_id["counterfactual-evolution-decision-controller"]["gpu0"]["status"],"stop-matched-shallow-rule-equivalent")
        self.assertEqual(by_id["constraint-complete-typed-memory-order-logic"]["checks"]["baseline_disagreement"]["status"],"fail")
        self.assertEqual(by_id["constraint-complete-typed-memory-order-logic"]["gpu0"]["status"],"stop-matched-nary-equivalent")
        self.assertEqual(by_id["active-causal-minimal-rollback"]["checks"]["baseline_disagreement"]["status"],"fail")
        self.assertEqual(by_id["active-causal-minimal-rollback"]["gpu0"]["status"],"stop-matched-group-testing-equivalent")
        self.assertEqual(by_id["bounded-probe-api-transition-operator"]["checks"]["baseline_disagreement"]["status"],"fail")
        self.assertEqual(by_id["bounded-probe-api-transition-operator"]["gpu0"]["status"],"stop-stateful-deterministic-pex-ceiling")
        self.assertEqual(by_id["interventional-permission-triage-under-ceiling"]["gpu0"]["status"],"stop-matched-boolean-rule-equivalent")
        self.assertEqual(by_id["workflow-branch-credit"]["gpu0"]["status"],"stop-matched-e1-direct-edit-equivalent")
        self.assertEqual(by_id["evaluator-coadaptation-guard"]["gpu0"]["status"],"stop-simple-anchor-residual-calibration-equivalent")
        self.assertEqual(by_id["evaluator-coadaptation-guard"]["checks"]["baseline_disagreement"]["status"],"fail")
        self.assertEqual(by_id["counterexample-generating-curriculum"]["gpu0"]["status"],"stop-matched-intersection-filter-equivalent")
        self.assertEqual(by_id["counterexample-generating-curriculum"]["checks"]["baseline_disagreement"]["status"],"fail")
        self.assertEqual(by_id["local-counterexample-memory-repair"]["gpu0"]["status"],"stop-complexity-matched-ilp-equivalent")
        self.assertEqual(by_id["local-counterexample-memory-repair"]["checks"]["baseline_disagreement"]["status"],"fail")
        self.assertEqual(by_id["memory-half-life"]["gpu0"]["status"],"stop-recency-frequency-policy-dominates")
        self.assertEqual(by_id["memory-half-life"]["checks"]["baseline_disagreement"]["status"],"fail")
        self.assertEqual(self.state["summary"]["gpu0_stop"],12)

    def test_reused_artifacts_capture_current_blockers(self) -> None:
        shared=self.state["shared_evidence"]
        self.assertTrue(shared["a3_mastered_panel"]["passed"])
        self.assertEqual(shared["a3_mastered_panel"]["panel_size"],6)
        self.assertEqual(shared["a3_mastered_panel"]["mastered_candidates"],41)
        self.assertEqual(shared["a6_a7_dataset"]["a6_nonprefix_interventions"],0)
        self.assertEqual(shared["a6_a7_dataset"]["a7_same_state_four_action_rows"],0)
        self.assertEqual(shared["a6_a7_dataset"]["max_rounds_per_sequence"],4)
        self.assertFalse(shared["e1"]["identifiable"])
        self.assertEqual(shared["memory_full"]["status"],"complete")
        self.assertEqual(shared["memory_full"]["full_completed_executions"],216)
        self.assertEqual(shared["memory_full"]["full_completed_units"],72)
        self.assertEqual(shared["memory_full"]["controlled_nonzero"],11)
        self.assertEqual(shared["memory_full"]["co_retrieval_pair_arms"],0)
        self.assertEqual(shared["memory_full"]["longitudinal_reuse_sequences"],0)
        self.assertFalse(shared["updater_competence"]["a1"]["passed"])
        self.assertEqual(shared["updater_competence"]["a1"]["status"],"stop-substrate")
        self.assertFalse(shared["updater_competence"]["a2"]["passed"])
        self.assertAlmostEqual(shared["updater_competence"]["a2"]["evidence"]["nonzero_update_effect_fraction"],7/36)
        self.assertEqual(shared["a7_counterfactual_cpu"]["decision"],"STOP_MATCHED_SHALLOW_RULE_EQUIVALENT")
        self.assertEqual(shared["b3_interference_cpu"]["decision"],"SCREENING_SIGNAL_REAL_COINTERACTION_REQUIRED")
        self.assertEqual(shared["b3_interference_cpu"]["runtime_preflight_snapshot"]["decision"],"HOLD_RUNTIME_ENVIRONMENT_DRIFT")
        self.assertEqual(shared["b5_applicability_cpu"]["decision"],"STOP_COMPLEXITY_MATCHED_ILP_EQUIVALENT")
        self.assertEqual(shared["b6_memory_utility_cpu"]["decision"],"STOP_RECENCY_FREQUENCY_POLICY_DOMINATES")

    def test_exact_data_deficits_are_explicit_holds(self) -> None:
        by_id={row["idea_id"]:row for row in self.state["cards"]}
        expected={
            "regression-gated-self-evolution":"hold",
            "contradiction-preserving-consolidation":"hold-support-cardinality-insufficient",
            "retrieval-interference-auditor":"hold-real-cinteraction-runtime",
            "workflow-generalization-certificate":"hold",
        }
        for idea_id,status in expected.items():
            self.assertEqual(by_id[idea_id]["gpu0"]["status"],status,idea_id)
        self.assertEqual(self.state["summary"]["gpu0_hold_or_conditional"],4)


if __name__=="__main__":
    unittest.main()
