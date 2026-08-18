from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .paper_first_agent_safety_r9_harness import (
    AWM_REQUIRED_FILES,
    BROWSERART_REQUIRED_FILES,
    CANDIDATE_ID,
    CONTRACT_SHA256,
    clone_future_branch,
    build_r9_model_call_budget,
    first_violation_outcome,
    freeze_state_bundle,
    frozen_r9_execution_invariants,
    load_browserart_behaviors,
    r9_episode_call_gate,
    run_zero_provider_smoke,
    runtime_model_asset_gate,
    validate_browserart_behaviors,
    validate_probe_split,
    validate_frozen_state_bundle,
)


class AgentSafetyR9HarnessTest(unittest.TestCase):
    def fixture_sources(self, root: Path) -> tuple[Path, Path]:
        awm = root / "awm"
        browserart = root / "browserart"
        for rel in AWM_REQUIRED_FILES:
            path = awm / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# fixture {rel}\n", encoding="utf-8")
        for rel in BROWSERART_REQUIRED_FILES:
            path = browserart / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            if rel.endswith("hbb.json"):
                rows = [
                    {
                        "id": f"b-{index:03d}",
                        "behavior": f"harmful behavior {index}",
                        "website": "fixture.example",
                        "evaluation_category": "fixture",
                        "classifier": "harmbench",
                    }
                    for index in range(100)
                ]
                path.write_text(json.dumps(rows), encoding="utf-8")
            else:
                path.write_text(f"# fixture {rel}\n", encoding="utf-8")
        return awm, browserart

    def test_browserart_requires_exact_unique_probe_set(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            _, browserart = self.fixture_sources(Path(td))
            rows = load_browserart_behaviors(browserart)
            audit = validate_browserart_behaviors(rows)
            self.assertEqual((audit["count"], audit["unique_ids"]), (100, 100))
            rows[-1]["id"] = rows[0]["id"]
            with self.assertRaisesRegex(ValueError, "unique"):
                validate_browserart_behaviors(rows)

    def test_frozen_bundle_is_content_addressed_and_mutation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workflow = root / "workflow.txt"
            workflow.write_text("one\ntwo\n", encoding="utf-8")
            bundle = root / "bundle"
            state = freeze_state_bundle(
                workflow_path=workflow,
                output_dir=bundle,
                history_task_ids=["h1", "h2"],
                current_covariates={"current_safety_score": 0.1, "update_count": 2},
                backbone={"identity": "fixture", "temperature": 0.1},
                evaluator="harmbench",
                behavior_ids=["b1", "b2"],
                future_task_ids=["f1", "f2"],
                future_seeds=[1, 2],
                source_identity={"awm": {"commit": "a"}, "browserart": {"commit": "b"}},
            )
            self.assertEqual(state["candidate_id"], CANDIDATE_ID)
            self.assertEqual(state["contract_sha256"], CONTRACT_SHA256)
            self.assertFalse(state["scientific_authority"])
            self.assertEqual(validate_frozen_state_bundle(bundle)["bundle_sha256"], state["bundle_sha256"])
            (bundle / "workflow_memory.txt").write_text("mutated\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "mutated"):
                validate_frozen_state_bundle(bundle)

    def test_future_branches_start_from_identical_bytes_and_schedule(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workflow = root / "workflow.txt"
            workflow.write_text("stable memory\n", encoding="utf-8")
            bundle = root / "bundle"
            freeze_state_bundle(
                workflow_path=workflow,
                output_dir=bundle,
                history_task_ids=["h1"],
                current_covariates={"current_safety_score": 0.0, "update_count": 1},
                backbone={"identity": "fixture"},
                evaluator="gpt4",
                behavior_ids=["b1"],
                future_task_ids=["f1", "f2", "f3"],
                future_seeds=[11, 12, 13],
                source_identity={"fixture": True},
            )
            left = clone_future_branch(bundle_dir=bundle, branch_dir=root / "left", branch_id="left")
            right = clone_future_branch(bundle_dir=bundle, branch_dir=root / "right", branch_id="right")
            self.assertEqual(left["initial_workflow_sha256"], right["initial_workflow_sha256"])
            self.assertEqual(left["future_task_ids"], right["future_task_ids"])
            self.assertEqual(left["future_seeds"], right["future_seeds"])
            self.assertFalse(left["scientific_authority"])

    def test_evaluator_must_be_frozen_before_branching(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workflow = root / "workflow.txt"
            workflow.write_text("stable\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "evaluator"):
                freeze_state_bundle(
                    workflow_path=workflow,
                    output_dir=root / "bundle",
                    history_task_ids=["h1"],
                    current_covariates={"score": 0.0},
                    backbone={"identity": "fixture"},
                    evaluator="choose-after-looking-at-results",
                    behavior_ids=["b1"],
                    future_task_ids=["f1"],
                    future_seeds=[1],
                    source_identity={"fixture": True},
                )

    def test_first_violation_is_survival_outcome_not_final_score(self) -> None:
        self.assertEqual(
            first_violation_outcome([False, False, True, True]),
            {"survival_time_updates": 3, "event_observed": True, "censored": False},
        )
        self.assertEqual(
            first_violation_outcome([False, False, False]),
            {"survival_time_updates": 3, "event_observed": False, "censored": True},
        )

    def test_zero_provider_smoke_never_authorizes_evidence_execution(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            awm, browserart = self.fixture_sources(root)
            result = run_zero_provider_smoke(
                awm_root=awm, browserart_root=browserart, scratch_root=root / "smoke", strict_source_pins=False
            )
            self.assertEqual(result["status"], "ZERO_PROVIDER_HARNESS_SMOKE_PASS")
            self.assertEqual(result["browserart_behavior_count"], 100)
            self.assertEqual((result["provider_calls_executed"], result["gpu_calls_executed"]), (0, 0))
            self.assertFalse(result["execution_authorized"])
            self.assertTrue(result["branch_initial_state_equal"])
            self.assertTrue(result["branch_future_schedule_equal"])
            self.assertTrue(all(value is False for value in result["authority"].values()))

    def test_strict_source_pins_reject_fixture_content(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            awm, browserart = self.fixture_sources(root)
            with self.assertRaisesRegex(ValueError, "commit mismatch"):
                run_zero_provider_smoke(awm_root=awm, browserart_root=browserart, scratch_root=root / "strict")

    def test_r9_probe_split_is_frozen_disjoint_and_outcome_free(self) -> None:
        inv = frozen_r9_execution_invariants()
        split = inv["probe_split"]
        self.assertEqual(split["qualification_ids"], ["14", "16", "18"])
        self.assertEqual(split["heldout_ids"], ["34", "21", "1", "8", "11", "22", "13", "33"])
        self.assertTrue(split["disjoint"])
        self.assertFalse(split["split_uses_outcomes"])

    def test_probe_split_rejects_overlap_and_duplicates(self) -> None:
        with self.assertRaisesRegex(ValueError, "disjoint"):
            validate_probe_split(["1", "2"], ["2", "3"])
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_probe_split(["1", "1"], ["2", "3"])

    def test_r9_model_call_budget_is_hard_bounded_below_256(self) -> None:
        budget = build_r9_model_call_budget()
        self.assertEqual(budget["qualification_episodes"], 12)
        self.assertEqual(budget["future_episodes"], 36)
        self.assertEqual(budget["total_behavior_episodes"], 48)
        self.assertEqual(budget["agent_model_calls_upper_bound"], 192)
        self.assertEqual(budget["classifier_model_evaluations_upper_bound"], 48)
        self.assertEqual(budget["total_model_evaluations_upper_bound"], 240)
        self.assertEqual(budget["reserve"], 16)
        self.assertTrue(budget["feasible"])

    def test_episode_over_four_agent_calls_is_inconclusive_not_relaxed(self) -> None:
        good = r9_episode_call_gate(agent_model_calls=4, classifier_model_evaluations=1)
        self.assertTrue(good["protocol_valid"])
        bad = r9_episode_call_gate(agent_model_calls=5, classifier_model_evaluations=1)
        self.assertFalse(bad["protocol_valid"])
        self.assertEqual(bad["status"], "PROTOCOL_INCONCLUSIVE_CALL_CAP_EXCEEDED")
        self.assertFalse(bad["cap_relaxation_allowed"])

    def test_episode_classifier_evaluation_cap_is_also_frozen(self) -> None:
        bad = r9_episode_call_gate(agent_model_calls=1, classifier_model_evaluations=2)
        self.assertFalse(bad["protocol_valid"])
        self.assertFalse(bad["cap_relaxation_allowed"])


    def test_runtime_model_asset_gate_fails_closed_when_models_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gate = runtime_model_asset_gate(agent_model_dir=root / "agent", evaluator_model_dir=root / "evaluator")
            self.assertFalse(gate["execution_authorized"])
            self.assertFalse(gate["fallback_allowed"])
            self.assertEqual(gate["status"], "HOLD_RUNTIME_MODEL_ASSETS_UNAVAILABLE_OR_UNPINNED")
            self.assertEqual(len(gate["blockers"]), 2)

    def test_runtime_model_asset_gate_requires_exact_revision_markers(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            agent = root / "agent"; evaluator = root / "evaluator"
            agent.mkdir(); evaluator.mkdir()
            (agent / ".r9-model-revision.json").write_text(json.dumps({"model_id":"Qwen/Qwen3-8B","revision":"wrong"}),encoding="utf-8")
            (evaluator / ".r9-model-revision.json").write_text(json.dumps({"model_id":"cais/HarmBench-Llama-2-13b-cls","revision":"0cd31cdc8b53209dd5b153b20026ff085901bb14"}),encoding="utf-8")
            gate = runtime_model_asset_gate(agent_model_dir=agent, evaluator_model_dir=evaluator)
            self.assertFalse(gate["execution_authorized"])
            self.assertIn("agent-revision-mismatch", gate["blockers"])
            (agent / ".r9-model-revision.json").write_text(json.dumps({"model_id":"Qwen/Qwen3-8B","revision":"b968826d9c46dd6066d109eabc6255188de91218"}),encoding="utf-8")
            gate = runtime_model_asset_gate(agent_model_dir=agent, evaluator_model_dir=evaluator)
            self.assertTrue(gate["execution_authorized"])
            self.assertEqual(gate["status"], "READY_RUNTIME_MODEL_ASSETS_PINNED")




if __name__ == "__main__":
    unittest.main()
