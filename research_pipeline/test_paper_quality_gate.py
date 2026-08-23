from __future__ import annotations

import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from .iclr_agent_paper_template import TEMPLATE_ID, TEMPLATE_VERSION
from .paper_design_contract import audit_paper_design_contract
from .paper_quality_gate import audit_manuscript_evidence_completion, audit_paper_evidence_plan


def method_quality() -> dict:
    return {
        "schema_version": "2.1",
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
            "visualization_ids": ["V1", "V2", "V3", "V4"],
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
        "visualizations": [
            {"id": "V1", "placement": "main", "visual_type": "multi_panel", "panel_roles": ["main_comparison", "uncertainty"], "target_claim_ids": ["C1"], "source_evidence_ids": ["B1", "U1", "O1"], "reviewer_question": "Does the method beat the strongest matched baseline under uncertainty?", "takeaway": "The comparison is visible with uncertainty rather than point estimates alone.", "quantitative": True, "uncertainty_required": True, "negative_or_failure_visible": False},
            {"id": "V2", "placement": "main", "visual_type": "bar", "panel_roles": ["ablation"], "target_claim_ids": ["C1"], "source_evidence_ids": ["A1", "O2"], "reviewer_question": "Which component carries the claimed gain?", "takeaway": "Removing the novelty-carrying component changes the registered metric.", "quantitative": True, "uncertainty_required": False, "negative_or_failure_visible": False},
            {"id": "V3", "placement": "main", "visual_type": "multi_panel", "panel_roles": ["mechanism", "failure"], "target_claim_ids": ["C1"], "source_evidence_ids": ["M1", "F1", "O3", "O4"], "reviewer_question": "Why and where does the mechanism work or fail?", "takeaway": "Mechanism-predicted disagreement and failure strata are exposed together.", "quantitative": True, "uncertainty_required": False, "negative_or_failure_visible": True},
            {"id": "V4", "placement": "main", "visual_type": "distribution", "panel_roles": ["sensitivity"], "target_claim_ids": ["C1"], "source_evidence_ids": ["S1", "O5"], "reviewer_question": "Does the conclusion survive registered perturbations?", "takeaway": "The conclusion is shown across the sensitivity family.", "quantitative": True, "uncertainty_required": False, "negative_or_failure_visible": False},
        ],
    }


def completed_quality(quality: dict) -> dict:
    evidence = [{"id": row["id"], "status": "PASS", "artifact_refs": [f"generated/{row['id']}.json"]} for row in quality["baselines"] + quality["ablations"] + quality["analyses"] + quality["planned_outputs"]]
    visualizations = []
    for row in quality["visualizations"]:
        review = {
            "caption_claim_aligned": True,
            "legible_labels": True,
            "legend_or_direct_labels": True,
            "non_deceptive_scale": True,
            "source_data_versioned": True,
        }
        if row["uncertainty_required"]:
            review["uncertainty_visible"] = True
        if row["negative_or_failure_visible"]:
            review["negative_or_failure_visible"] = True
        visualizations.append({"id": row["id"], "status": "PASS", "artifact_refs": [f"paper/{row['id']}.pdf"], "data_refs": [f"generated/{row['id']}.json"], "script_refs": [f"paper/{row['id']}.py"], "caption_ref": f"fig:{row['id']}", "visual_review": review})
    return {"evidence": evidence, "visualizations": visualizations, "claims": {"C1": {"status": "SUPPORTED", "evidence_ids": [row["id"] for row in evidence]}}}


def development_quality() -> dict:
    return {
        "manuscript_template": {
            "template_id": TEMPLATE_ID,
            "template_version": TEMPLATE_VERSION,
            "experiment_lane_plan": {f"E{i}": {"status": "PLANNED"} for i in range(1, 7)},
        },
        "problem_related_work": {
            "necessity_argument": "important recurring failure with concrete consequences",
            "challenge_statement": "the problem is hard because the relevant variable is only partially observable",
            "current_paradigm_map": ["baseline family", "closest method family"],
            "closest_work_boundaries": ["closest work solves retrieval but not the identified persistent mechanism"],
            "residual_problem": "identify the residual mechanism under matched information",
        },
        "method_exposition": {
            "core_intuition": "preserve the missing decision variable explicitly",
            "design_principles": ["match information", "change one load-bearing mechanism"],
            "input_output_contract": "input state -> mechanism-specific decision object -> output decision",
            "step_by_step_flow": ["read input", "compute mechanism object", "apply decision rule"],
            "component_rationales": [{"component": "core", "why": "carries the new variable"}],
            "assumptions_and_held_fixed": ["same data", "same model", "same budget"],
            "implementation_surface": "one deterministic module plus a frozen evaluator",
            "failure_modes": ["no headroom", "variable not identifiable"],
        },
        "experiment_program": {
            "prior_work_inspired_baselines": ["strongest closest-work baseline"],
            "main_effects": ["held-out matched comparison"],
            "component_ablations": ["remove the core mechanism"],
            "method_characteristic_tests": ["disagreement-stratified stress test"],
            "mechanism_tests": ["mechanism-predicted subgroup"],
            "robustness_and_generalization": ["seed", "domain"],
            "negative_and_failure_cases": ["ceiling", "incompatible domain"],
            "efficiency_and_cost": ["calls", "tokens"],
            "statistical_plan": "paired interval and preregistered unit",
        },
        "writing_clarity": {
            "plain_language_summary": "A simple explanation of the problem, method, and result.",
            "term_definitions": {"mechanism object": "the decision-relevant variable preserved by the method"},
            "topic_sentence_rule": "state the point before details",
            "one_sentence_one_job": True,
            "concrete_subject_verb_rule": True,
            "jargon_justification": "new jargon only when no ordinary term is precise enough",
            "reader_simulation": "a reader without project context can restate problem, method, experiments, and limits",
        },
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
        audit_current = audit_paper_design_contract(config)
        self.assertTrue(audit_current["passed"])
        self.assertEqual(audit_current["development_quality"]["status"], "INITIAL_DRAFT_GUIDANCE_NOT_YET_BOUND")
        broken = copy.deepcopy(config)
        broken["pre_experiment"]["paper_design"].pop("evidence_quality")
        audit = audit_paper_design_contract(broken)
        self.assertFalse(audit["passed"])
        self.assertIn("paper-quality-schema-version-missing-or-stale", audit["blockers"])

    def test_schema_2_4_requires_development_quality_contract(self) -> None:
        config = paper_design_with_quality();config["schema_version"]="2.4"
        audit = audit_paper_design_contract(config)
        self.assertFalse(audit["passed"]);self.assertTrue(any(x.startswith("paper-development-field-missing:") for x in audit["blockers"]))
        config["pre_experiment"]["paper_design"]["development_quality"] = development_quality()
        repaired = audit_paper_design_contract(config)
        self.assertTrue(repaired["passed"], repaired["blockers"]);self.assertTrue(repaired["development_quality"]["passed"])
        self.assertEqual(repaired["summary"]["paper_development_dimensions_passed"],4)
        self.assertEqual(repaired["development_quality"]["template_binding"]["status"], "ICLR_TEMPLATE_BOUND")

    def test_schema_2_4_development_contract_requires_iclr_template_lanes(self) -> None:
        config = paper_design_with_quality();config["schema_version"]="2.4"
        dev = development_quality();dev.pop("manuscript_template")
        config["pre_experiment"]["paper_design"]["development_quality"] = dev
        missing = audit_paper_design_contract(config)
        self.assertFalse(missing["passed"]);self.assertIn("iclr-template-id-missing-or-stale", missing["blockers"])
        dev = development_quality();dev["manuscript_template"]["experiment_lane_plan"].pop("E3")
        config["pre_experiment"]["paper_design"]["development_quality"] = dev
        missing_lane = audit_paper_design_contract(config)
        self.assertFalse(missing_lane["passed"]);self.assertIn("iclr-template-experiment-lane-unbound:E3", missing_lane["blockers"])
        dev = development_quality();dev["manuscript_template"]["experiment_lane_plan"]["E3"] = {"status": "NOT_APPLICABLE_WITH_ARCHETYPE_REASON", "reason": "theory certificate uses exact negative control instead"}
        config["pre_experiment"]["paper_design"]["development_quality"] = dev
        allowed_na = audit_paper_design_contract(config)
        self.assertTrue(allowed_na["passed"], allowed_na["blockers"])

    def test_manuscript_ready_requires_completed_artifacts(self) -> None:
        quality = method_quality()
        missing = audit_manuscript_evidence_completion(quality, {}, method_components=2)
        self.assertFalse(missing["passed"])
        evidence = []
        for row in quality["baselines"] + quality["ablations"] + quality["analyses"] + quality["planned_outputs"]:
            evidence.append({"id": row["id"], "status": "PASS", "artifact_refs": [f"generated/{row['id']}.json"]})
        visualizations = []
        for row in quality["visualizations"]:
            review = {
                "caption_claim_aligned": True,
                "legible_labels": True,
                "legend_or_direct_labels": True,
                "non_deceptive_scale": True,
                "source_data_versioned": True,
            }
            if row["uncertainty_required"]:
                review["uncertainty_visible"] = True
            if row["negative_or_failure_visible"]:
                review["negative_or_failure_visible"] = True
            visualizations.append({"id": row["id"], "status": "PASS", "artifact_refs": [f"paper/{row['id']}.pdf"], "data_refs": [f"generated/{row['id']}.json"], "script_refs": [f"paper/{row['id']}.py"], "caption_ref": f"fig:{row['id']}", "visual_review": review})
        completion = {"evidence": evidence, "visualizations": visualizations, "claims": {"C1": {"status": "SUPPORTED", "evidence_ids": [row["id"] for row in evidence]}}}
        passed = audit_manuscript_evidence_completion(quality, completion, method_components=2)
        self.assertTrue(passed["passed"], passed["blockers"])
        self.assertEqual(len(passed["claim_ledger"]), 1)
        ledger = passed["claim_ledger"][0]
        self.assertEqual(ledger["claim_id"], "C1")
        self.assertEqual(ledger["manuscript_surface"], "AFFIRMATIVE_SUPPORTED")
        self.assertTrue(ledger["affirmative_claim_allowed"])
        self.assertTrue(ledger["trace_complete"])
        self.assertFalse(ledger["scientific_authority"])

    def test_claim_ledger_preserves_refuted_and_inconclusive_surface(self) -> None:
        quality = method_quality()
        completion = completed_quality(quality)
        completion["claims"]["C1"]["status"] = "REFUTED"
        audit = audit_manuscript_evidence_completion(quality, completion, method_components=2)
        self.assertTrue(audit["passed"], audit["blockers"])
        ledger = audit["claim_ledger"][0]
        self.assertEqual(ledger["manuscript_surface"], "NEGATIVE_OR_REFUTED_ONLY")
        self.assertFalse(ledger["affirmative_claim_allowed"])
        self.assertTrue(ledger["must_preserve_negative_or_inconclusive"])

    def test_claim_adjudication_rejects_unregistered_evidence_id(self) -> None:
        quality = method_quality()
        completion = completed_quality(quality)
        completion["claims"]["C1"]["evidence_ids"] = ["FAKE-EVIDENCE"]
        audit = audit_manuscript_evidence_completion(quality, completion, method_components=2)
        self.assertFalse(audit["passed"])
        self.assertIn("paper-quality-claim-evidence-id-unregistered:C1:FAKE-EVIDENCE", audit["blockers"])

    def test_claim_adjudication_rejects_registered_but_unlinked_evidence_id(self) -> None:
        quality = method_quality()
        quality["planned_outputs"].append({"id": "O-OTHER", "output_type": "failure", "purpose": "Evidence registered for another claim or auxiliary analysis."})
        completion = completed_quality(quality)
        completion["claims"]["C1"]["evidence_ids"] = ["O-OTHER"]
        audit = audit_manuscript_evidence_completion(quality, completion, method_components=2)
        self.assertFalse(audit["passed"])
        self.assertIn("paper-quality-claim-evidence-id-not-linked:C1:O-OTHER", audit["blockers"])

    def test_content_addressed_completion_rejects_missing_or_stale_artifacts(self) -> None:
        quality = method_quality()
        completion = completed_quality(quality)
        refs = set()
        for row in completion["evidence"]:
            refs.update(row.get("artifact_refs") or [])
        for row in completion["visualizations"]:
            for key in ("artifact_refs", "data_refs", "script_refs"):
                refs.update(row.get(key) or [])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registry = {}
            for ref in sorted(refs):
                path = root / ref
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"bound:{ref}\n", encoding="utf-8")
                registry[ref] = hashlib.sha256(path.read_bytes()).hexdigest()
            passed = audit_manuscript_evidence_completion(
                quality,
                completion,
                method_components=2,
                source_sha256=registry,
                project_root=root,
                require_content_addressed=True,
            )
            self.assertTrue(passed["passed"], passed["blockers"])
            victim = sorted(refs)[0]
            (root / victim).write_text("mutated after receipt\n", encoding="utf-8")
            stale = audit_manuscript_evidence_completion(
                quality,
                completion,
                method_components=2,
                source_sha256=registry,
                project_root=root,
                require_content_addressed=True,
            )
            self.assertFalse(stale["passed"])
            self.assertIn(f"paper-quality-artifact-digest-mismatch:{victim}", stale["blockers"])

    def test_missing_visual_reviewer_question_blocks(self) -> None:
        quality = method_quality()
        quality["visualizations"][0]["reviewer_question"] = ""
        audit = audit_paper_evidence_plan(quality, method_components=2)
        self.assertFalse(audit["passed"])
        self.assertIn("paper-quality-visual-question-or-takeaway-missing:V1", audit["blockers"])

    def test_visual_completion_requires_data_script_caption_and_review(self) -> None:
        quality = method_quality()
        evidence = [{"id": row["id"], "status": "PASS", "artifact_refs": [f"generated/{row['id']}.json"]} for row in quality["baselines"] + quality["ablations"] + quality["analyses"] + quality["planned_outputs"]]
        visualizations = [{"id": row["id"], "status": "PASS", "artifact_refs": [f"paper/{row['id']}.pdf"]} for row in quality["visualizations"]]
        completion = {"evidence": evidence, "visualizations": visualizations, "claims": {"C1": {"status": "SUPPORTED", "evidence_ids": [row["id"] for row in evidence]}}}
        audit = audit_manuscript_evidence_completion(quality, completion, method_components=2)
        self.assertFalse(audit["passed"])
        self.assertIn("paper-quality-visual-script-missing:V1", audit["blockers"])
        self.assertIn("paper-quality-visual-data-binding-missing:V1", audit["blockers"])
        self.assertIn("paper-quality-visual-caption-binding-missing:V1", audit["blockers"])


if __name__ == "__main__":
    unittest.main()
