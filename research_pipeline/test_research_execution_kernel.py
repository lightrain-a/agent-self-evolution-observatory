from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from .atomic_checkpoint import AtomicCheckpointStore
from .research_execution_kernel import (
    build_experiment_manifest, build_research_execution_kernel_state, build_research_state,
    evaluate_reanchor, validate_experiment_manifest, validate_research_state,
)
from .research_sandbox_contract import (
    build_execution_job, build_research_sandbox_contract, validate_executor_receipt,
)
from .scientific_metacognition import (
    classify_failure, evaluate_metacognition, validate_failure_interpretation,
)


class ResearchExecutionKernelTest(unittest.TestCase):
    def manifest(self, **overrides):
        args = {
            "experiment_id": "EXP-E2-PILOT", "research_item_code": "E-2",
            "scientific_object": "matched temporal intervention effect",
            "hypothesis": "targeted intervention leaves a residual beyond the matched baseline",
            "decisive_test": "frozen paired comparison", "primary_metric": "paired success delta",
            "strongest_baseline": "behavior-neutral generic helper", "controls": ["no-skill", "generic-helper"],
            "task_snapshot": {"split": "frozen-v1", "n": 3}, "model_provider": "local-test",
            "seeds": [1, 2, 3], "code_commit": "d741248", "config_sha256": "a" * 64,
            "runtime_sha256": "b" * 64, "unit_ids": ["u1", "u2", "u3"],
            "estimated_cost": {"gpu_hours": 1.0}, "stop_conditions": ["provider failure > 20%"],
            "artifact_root": "runs/exp-e2-pilot",
        }
        args.update(overrides)
        return build_experiment_manifest(**args)

    def test_manifest_freezes_science_execution_and_phase_promotion(self):
        manifest = self.manifest()
        audit = validate_experiment_manifest(manifest)
        self.assertTrue(audit["passed"], audit["blockers"])
        self.assertNotEqual(manifest["scientific_contract_sha256"], manifest["execution_identity_sha256"])
        self.assertEqual(list(manifest["phases"]), ["smoke", "pilot", "full"])
        self.assertTrue(all(row["automatic_promotion"] is False for row in manifest["phases"].values()))
        self.assertTrue(manifest["atomic_progress"])
        self.assertFalse(manifest["automatic_full_scale_authority"])

    def test_manifest_tampering_is_detected(self):
        manifest = self.manifest()
        manifest["scientific_contract"]["hypothesis"] = "changed after outcomes"
        audit = validate_experiment_manifest(manifest)
        self.assertFalse(audit["passed"])
        self.assertIn("scientific-contract-digest-mismatch", audit["blockers"])

    def test_atomic_checkpoint_resumes_only_incomplete_units(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = AtomicCheckpointStore(Path(tmp))
            manifest = self.manifest()
            progress = store.initialize(manifest)
            self.assertEqual(progress["next_unit_id"], "u1")
            first = store.append_unit("u1", {"score": 0.5}, artifact_refs=["u1.csv"])
            self.assertFalse(first["scientific_authority"])
            progress = store.resume_cursor()
            self.assertEqual(progress["completed"], 1)
            self.assertEqual(progress["next_unit_id"], "u2")
            self.assertEqual(progress["remaining_unit_ids"], ["u2", "u3"])
            same = store.append_unit("u1", {"score": 0.5}, artifact_refs=["u1.csv"])
            self.assertEqual(same["receipt_sha256"], first["receipt_sha256"])
            with self.assertRaises(ValueError): store.append_unit("u1", {"score": 0.7}, artifact_refs=["u1.csv"])

    def test_resume_rejects_runtime_or_config_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = AtomicCheckpointStore(Path(tmp)); store.initialize(self.manifest())
            with self.assertRaisesRegex(ValueError, "resume identity mismatch"):
                store.initialize(self.manifest(runtime_sha256="c" * 64))

    def test_research_state_is_recoverable_but_zero_authority(self):
        state = build_research_state(
            research_item_code="E-2", scientific_state="ACTIVE", branch_status="PILOT",
            workspace_ref="worktree:test", code_commit="d741248", environment_sha256="d" * 64,
            config_sha256="a" * 64, task_snapshot={"split": "v1"}, memory_snapshot={"wiki": "h1"},
            validated_evidence=["receipt:smoke"], unresolved_questions=["residual?"],
            experiment_execution_identity_sha256=self.manifest()["execution_identity_sha256"],
        )
        self.assertTrue(validate_research_state(state)["passed"])
        self.assertFalse(state["state_object_has_scientific_authority"])
        resume = evaluate_reanchor(state, purpose="execution_resume",
                                   current_execution_identity_sha256=self.manifest()["execution_identity_sha256"])
        self.assertEqual(resume["status"], "RESUME_ALLOWED")
        self.assertFalse(resume["machine_actionable"])

    def test_stop_or_hold_cannot_be_bypassed_by_rollback(self):
        state = build_research_state(
            research_item_code="F-12", scientific_state="STOPPED", branch_status="CLOSED",
            workspace_ref="archive:F12", reopen_condition="new pre-outcome observable leaves residual",
            experiment_execution_identity_sha256=self.manifest()["execution_identity_sha256"],
        )
        resume = evaluate_reanchor(state, purpose="execution_resume",
                                   current_execution_identity_sha256=self.manifest()["execution_identity_sha256"])
        self.assertEqual(resume["status"], "RESUME_BLOCKED")
        self.assertIn("scientific-reopen-required-before-execution-resume", resume["blockers"])
        failed = evaluate_reanchor(state, purpose="scientific_reopen", reopen_receipt={
            "condition_satisfied": False, "new_evidence_refs": [], "independent_scientific_review_required": True})
        self.assertFalse(failed["reanchor_allowed"])
        eligible = evaluate_reanchor(state, purpose="scientific_reopen", reopen_receipt={
            "condition_satisfied": True, "new_evidence_refs": ["receipt:new-observable"],
            "independent_scientific_review_required": True})
        self.assertEqual(eligible["status"], "ELIGIBLE_FOR_SCIENTIFIC_REVIEW")
        self.assertTrue(eligible["eligible_for_scientific_review"])
        self.assertFalse(eligible["scientific_authority"])
        self.assertFalse(eligible["machine_actionable"])

    def test_sandbox_blocks_evaluator_and_secret_mutation(self):
        good = build_research_sandbox_contract(
            readable_paths=["/run/input"], writable_paths=["/run/output"], executable_tools=["python"],
            evaluator_paths=["/eval"], secret_paths=["/secrets"], network_mode="deny",
            gpu_budget={"max_gpu_hours": 1}, api_budget={"max_usd": 2}, wallclock_budget={"hours": 2})
        self.assertTrue(good["validation"]["passed"], good["validation"]["blockers"])
        bad = build_research_sandbox_contract(
            readable_paths=["/run/input"], writable_paths=["/eval/results"], executable_tools=["python"],
            evaluator_paths=["/eval"], secret_paths=["/secrets"], network_mode="deny")
        self.assertFalse(bad["validation"]["passed"])
        self.assertIn("executor-write-overlaps-evaluator-surface", bad["validation"]["blockers"])

    def test_executor_cannot_mutate_or_self_validate_scientific_contract(self):
        manifest = self.manifest(); job = build_execution_job(manifest, planner_actor="planner", phase="pilot", authority_ref="auth:1")
        receipt = {"job_sha256": job["job_sha256"], "execution_identity_sha256": job["execution_identity_sha256"],
                   "scientific_contract_sha256": job["scientific_contract_sha256"], "scientific_authority": False}
        self.assertTrue(validate_executor_receipt(job, receipt)["passed"])
        mutated = copy.deepcopy(receipt); mutated["scientific_contract"] = {**job["scientific_contract"], "primary_metric": "best observed metric"}
        mutated["scientific_validity_pass"] = True
        audit = validate_executor_receipt(job, mutated)
        self.assertFalse(audit["passed"])
        self.assertIn("executor-attempted-scientific-contract-mutation", audit["blockers"])
        self.assertIn("executor-cannot-self-acquit-scientific-validity", audit["blockers"])

    def test_metacognition_catches_claim_evidence_and_protocol_drift(self):
        expected = {"scientific_object": "object-a", "hypothesis": "h1", "primary_metric": "m1", "protocol_sha256": "p1"}
        observed = {"scientific_object": "object-a", "hypothesis": "h1", "primary_metric": "m2", "protocol_sha256": "p1",
                    "validated_evidence_refs": ["e1"], "claim_evidence_refs": ["e1", "e2"],
                    "unsupported_inferences": ["generalize to all models"], "protocol_deviations": ["changed exclusion after outcomes"],
                    "alternative_explanations": ["provider effect"]}
        receipt = evaluate_metacognition(expected, observed)
        self.assertEqual(receipt["status"], "REVISE")
        self.assertFalse(receipt["transition_allowed"])
        self.assertTrue(any("primary_metric" in row for row in receipt["mismatches"]))
        self.assertIn("e2", receipt["unsupported_evidence_refs"])

    def test_failure_taxonomy_prevents_support_failure_becoming_scientific_stop(self):
        failure = classify_failure("infrastructure-error")
        self.assertEqual(failure["family"], "INFRASTRUCTURE")
        self.assertFalse(failure["scientific_belief_update_allowed"])
        audit = validate_failure_interpretation("infrastructure-error", "SCIENTIFIC_NEGATIVE", proposed_core_stop=True)
        self.assertFalse(audit["passed"])
        self.assertIn("failure-family-mismatch:INFRASTRUCTURE", audit["blockers"])
        self.assertIn("execution-kernel-never-authorizes-core-principle-stop", audit["blockers"])

    def test_kernel_projection_has_zero_automatic_authority(self):
        state = build_research_execution_kernel_state()
        self.assertEqual(state["summary"]["contracts"], 6)
        self.assertGreaterEqual(state["summary"]["legacy_atomic_configs_detected"], 2)
        self.assertTrue(state["policy"]["hold_stop_merge_and_paper_handoff_cannot_be_bypassed_by_state_rollback"])
        self.assertEqual(state["summary"]["automatic_scientific_authority"], 0)
        self.assertFalse(state["scientific_authority"])


if __name__ == "__main__": unittest.main()
