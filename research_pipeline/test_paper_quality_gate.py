from __future__ import annotations

import copy
import unittest

from .paper_design_contract import audit_paper_design_contract
from .paper_quality_gate import audit_manuscript_evidence_completion, audit_paper_evidence_plan


def method_quality() -> dict:
    return {
        "schema_version": "2.0",
        "paper_archetype": "method",
        "claims": [{
            "id": "C1",
            "claim_type": "mechanism",
            "statement": "The mechanism improves held-out decisions beyond a matched simplification.",
            "why_better_or_why_matters": "The mechanism preserves a decision-relevant variable that the simplification discards.",
            "alternative_explanations": ["extra information", "extra compute", "a shallow same-feature predictor is sufficient"],
            "ruling_out_experiments": ["match information and compute", "remove the core mechanism"],
            "baseline_ids": ["B1"],
            "ablation_ids": ["A1"],
            "analysis_ids": ["M1", "R1", "F1", "S1", "U1"],
            "output_ids": ["O1", "O2", "O3", "O4", "O5"],
        }],
        "baselines": [{
            "id": "B1",
            "role": "same_information_simplification",
            "evidence_type": "empirical",
            "target_claim_ids": ["C1"],
            "purpose": "Test residual value beyond the strongest matched simplification.",
            "matched_dimensions": ["data", "information", "model", "inference budget"],
        }],
        "ablations": [{
            "id": "A1",
            "ablation_type": "component",
            "target_claim_ids": ["C1"],
            "purpose": "Remove the novelty-carrying component while holding the rest fixed.",
            "decision_rule": "No degradation means the component-level mechanism claim is unsupported.",
        }],
        "analyses": [
            {"id": "M1", "analysis_type": "mechanism", "target_claim_ids": ["C1"], "purpose": "Locate gains on mechanism-predicted disagreement cases.", "decision_rule": "No disagreement-stratified effect means no mechanism claim."},
            {"id": "R1", "analysis_type": "alternative_explanation", "target_claim_ids": ["C1"], "purpose": "Rule out information and budget advantages.", "decision_rule": "Any unmatched resource invalidates an algorithmic-superiority claim."},
            {"id": "F1", "analysis_type": "failure", "target_claim_ids": ["C1"], "purpose": "Report tie, failure, and non-identifiable regimes.", "decision_rule": "Keep negative strata in the evidence chain."},
            {"id": "S1", "analysis_type": "sensitivity", "target_claim_ids": ["C1"], "purpose": "Stress task families and registered thresholds.", "decision_rule": "Narrow the claim if it survives only one setting."},
            {"id": "U1", "analysis_type": "uncertainty", "target_claim_ids": ["C1"], "purpose": "Quantify paired uncertainty.", "decision_rule": "No headline comparison from point estimates alone."},
        ],
        "planned_outputs": [
            {"id": "O1", "output_type": "main_comparison", "purpose": "Main baseline table."},
            {"id": "O2", "output_type": "ablation", "purpose": "Ablation table."},
            {"id": "O3", "output_type": "mechanism", "purpose": "Mechanism analysis."},
            {"id": "O4", "output_type": "failure", "purpose": "Failure analysis."},
            {"id": "O5", "output_type": "sensitivity", "purpose": "Sensitivity analysis."},
        ],
    }


def paper_design_with_quality() -> dict:
    return {
        "schema_version": "2.3",
        "pre_experiment": {
            "paper_design": {
                "novelty": {
                    "paper_problem": "paper problem",
                    "closest_work": [{"identity": "nearest", "difference": "different mechanism", "source_ref": "primary"}],
                    "novelty_axis": "mechanism",
                    "contribution_claim": "mechanism claim",
                    "irreducible_difference": "residual beyond matched simplification",
                    "collision_status": "reviewed",
                },
                "method": {
                    "method_name": "method",
                    "core_mechanism": "mechanism",
                    "novelty_to_method_mapping": [{"novelty": "mechanism", "component": "core"}],
                    "components": ["core", "certificate"],
                    "strongest_simplification": "matched baseline",
                    "method_change_rule": "core changes reset the contract",
                },
                "evidence_quality": method_quality(),
                "experiment_blueprint": {
                    "claim_experiment_matrix": [{"claim_id": "C1", "claim": "mechanism claim", "local_test": "local", "full_test": "full", "metric": "metric", "strongest_baseline": "matched baseline"}],
                    "local_validation_scope": "local",
                    "full_experiment_scope": "full",
                    "baseline_matrix": ["matched baseline"],
                    "ablation_matrix": ["remove core"],
                    "freeze_rule": "freeze",
                    "experimental_integrity": {
                        "model_and_inference": "freeze",
                        "prompt_tool_policy": "freeze",
                        "task_sample_split": "freeze",
                        "metric_analysis_plan": "freeze",
                        "randomness_replication_plan": "freeze",
                        "stopping_exclusion_rules": "freeze",
                        "allowed_adaptations": "implementation only",
                        "hidden_evaluation_access_policy": "sealed",
                    },
                },
            }
        },
    }


class PaperQualityGateTest(unittest.TestCase):
    def test_complete_method_plan_passes(self) -> None:
        audit = audit_paper_evidence_plan(method_quality(), method_components=2)
        self.assertTrue(audit["passed"], audit["blockers"])
        self.assertEqual(audit["summary"]["baselines"], 1)
        self.assertEqual(audit["summary"]["ablations"], 1)
        self.assertEqual(audit["summary"]["analyses"], 5)

    def test_baseline_name_without_empirical_role_is_not_enough(self) -> None:
        quality = method_quality()
        quality["baselines"][0]["evidence_type"] = "analytical"
        audit = audit_paper_evidence_plan(quality, method_components=2)
        self.assertFalse(audit["passed"])
        self.assertIn("paper-quality-empirical-claim-without-empirical-baseline:C1", audit["blockers"])

    def test_mechanism_claim_requires_ruling_out_analysis(self) -> None:
        quality = method_quality()
        quality["analyses"] = [row for row in quality["analyses"] if row["id"] != "R1"]
        quality["claims"][0]["analysis_ids"].remove("R1")
        audit = audit_paper_evidence_plan(quality, method_components=2)
        self.assertFalse(audit["passed"])
        self.assertIn("paper-quality-ruling-out-analysis-missing:C1", audit["blockers"])

    def test_multi_component_method_requires_component_ablation(self) -> None:
        quality = method_quality()
        quality["ablations"][0]["ablation_type"] = "representation"
        audit = audit_paper_evidence_plan(quality, method_components=2)
        self.assertFalse(audit["passed"])
        self.assertIn("paper-quality-multi-component-method-without-component-ablation", audit["blockers"])

    def test_schema_2_3_paper_design_cannot_bypass_quality_v2(self) -> None:
        config = paper_design_with_quality()
        self.assertTrue(audit_paper_design_contract(config)["passed"])
        broken = copy.deepcopy(config)
        broken["pre_experiment"]["paper_design"].pop("evidence_quality")
        audit = audit_paper_design_contract(broken)
        self.assertFalse(audit["passed"])
        self.assertIn("paper-quality-schema-version-missing-or-stale", audit["blockers"])

    def test_manuscript_ready_requires_completed_artifacts(self) -> None:
        quality = method_quality()
        missing = audit_manuscript_evidence_completion(quality, {}, method_components=2)
        self.assertFalse(missing["passed"])
        evidence = []
        for row in quality["baselines"] + quality["ablations"] + quality["analyses"] + quality["planned_outputs"]:
            evidence.append({"id": row["id"], "status": "PASS", "artifact_refs": [f"generated/{row['id']}.json"]})
        completion = {"evidence": evidence, "claims": {"C1": {"status": "SUPPORTED", "evidence_ids": [row["id"] for row in evidence]}}}
        passed = audit_manuscript_evidence_completion(quality, completion, method_components=2)
        self.assertTrue(passed["passed"], passed["blockers"])


if __name__ == "__main__":
    unittest.main()
