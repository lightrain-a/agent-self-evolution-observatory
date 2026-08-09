from __future__ import annotations

import copy
import inspect
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .p0_a1 import analyze as analyze_a1, synthetic_rows as synthetic_a1
from .p0_a2 import analyze as analyze_a2, synthetic_rows as synthetic_a2
from .p0_alfworld_adapter import action_family_shift, normalized_edit_distance, parse_admissible_choice
from .p0_alfworld_collect import generate_a1_candidates
from .p0_common import balanced_assignments, config_hash, load_json, result_payload, runtime_preflight, validate_collection_manifest, validate_measured_cost
from .p0_runner import config_path, p0_execution_lock


class P0RunnerTest(unittest.TestCase):
    def test_a1_dry_fixture_clears_gate_without_extra_acceptance(self) -> None:
        config = load_json(config_path("update-trust-region"))
        result = analyze_a1(synthetic_a1(), config)
        self.assertTrue(result["go"])
        self.assertEqual(result["matched_acceptance_count"], 6)
        table = {row["policy"]: row for row in result["table"]}
        self.assertEqual(table["gain+behavior-drift"]["accepted"], table["prompt-edit-size"]["accepted"])
        self.assertEqual(table["gain+behavior-drift"]["harmful_updates"], 0)
        self.assertGreaterEqual(table["gain+behavior-drift"]["mean_current_task_gain"], table["behavior-drift"]["mean_current_task_gain"])

    def test_a2_dry_fixture_is_allowed_to_fail_against_tuned_rule(self) -> None:
        config = load_json(config_path("budgeted-evolution-controller"))
        result = analyze_a2(synthetic_a2(), config)
        self.assertFalse(result["go"])
        self.assertEqual(result["strongest_simple_baseline"], "tuned-heuristic")
        self.assertEqual(result["calls_saved_fraction"], 0.0)
        table = {row["policy"]: row for row in result["table"]}
        self.assertEqual(table["tuned-heuristic"]["mean_calls"], 10.5)
        self.assertGreater(table["tuned-heuristic"]["mean_observed_round"], table["tuned-heuristic"]["mean_round"])

    def test_a1_candidate_generator_has_no_probe_or_hidden_input(self) -> None:
        self.assertEqual(list(inspect.signature(generate_a1_candidates).parameters), ["policy", "failure_traces", "target_range", "seed"])

        class FakePolicy:
            def propose_patch(self, trace, *, seed, previous_patch="", variant=0):
                return f"general rule {variant}"

            def token_count(self, text):
                return len(text.split())

        failures = [{"task_id": "discovery-task", "success": 0}]
        rows, attempts = generate_a1_candidates(FakePolicy(), failures, [2, 3], 42)
        self.assertEqual(len(rows), 3)
        self.assertEqual(attempts, 3)
        self.assertTrue(all(row["source_task_id"] == "discovery-task" for row in rows))

    def test_a2_hidden_sequences_cannot_change_fitted_controller(self) -> None:
        config = load_json(config_path("budgeted-evolution-controller"))
        original = synthetic_a2()
        reference = analyze_a2(original, config)
        changed = copy.deepcopy(original)
        for sequence in changed:
            if sequence["split"] == "hidden":
                for row in sequence["rounds"]:
                    row["marginal_gain"] = -999.0
                    row["probe_regression"] = 999.0
                    row["disagreement"] = 999.0
        result = analyze_a2(changed, config)
        self.assertEqual(result["frozen_heuristic"], reference["frozen_heuristic"])
        self.assertEqual(result["frozen_linear_controller"], reference["frozen_linear_controller"])

    def test_alfworld_choice_parser_never_invents_an_action(self) -> None:
        commands = ["look", "go to fridge 1", "open fridge 1"]
        self.assertEqual(parse_admissible_choice("3", commands), ("open fridge 1", False))
        self.assertEqual(parse_admissible_choice("open fridge 1", commands), ("open fridge 1", False))
        self.assertEqual(parse_admissible_choice("I would dance", commands), ("look", True))
        self.assertGreater(normalized_edit_distance(["look"], ["open fridge 1"]), 0)
        self.assertGreater(action_family_shift(["look", "look"], ["open fridge 1", "go to fridge 1"]), 0)

    def test_balanced_hidden_assignment_is_deterministic_and_nearly_even(self) -> None:
        assignments = balanced_assignments([f"c{i}" for i in range(30)], [f"t{i}" for i in range(40)], 12, 42)
        self.assertEqual(assignments, balanced_assignments([f"c{i}" for i in range(30)], [f"t{i}" for i in range(40)], 12, 42))
        counts = {f"t{i}": 0 for i in range(40)}
        for chosen in assignments.values():
            self.assertEqual(len(chosen), 12)
            for task_id in chosen:
                counts[task_id] += 1
        self.assertLessEqual(max(counts.values()) - min(counts.values()), 1)

    def test_real_p0_execution_lock_is_exclusive_and_blocks_unresolved_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with p0_execution_lock(root):
                with self.assertRaisesRegex(RuntimeError, "execution lock"):
                    with p0_execution_lock(root):
                        pass
            (root / "p0-execution-state.json").write_text(
                json.dumps({"status": "collected", "idea_id": "update-trust-region"}), encoding="utf-8"
            )
            with self.assertRaisesRegex(RuntimeError, "unresolved"):
                with p0_execution_lock(root):
                    pass

    def test_p0_pass_requires_human_approval_next(self) -> None:
        config = load_json(config_path("update-trust-region"))
        analysis = analyze_a1(synthetic_a1(), config)
        payload = result_payload(analysis, config)
        self.assertEqual(payload["result"], "pass")
        self.assertEqual(payload["next_action"], "await-human-approval")

    def test_cost_and_manifest_audit_rejects_incomplete_real_results(self) -> None:
        config = load_json(config_path("update-trust-region"))
        cost = {
            "gpu_hours": 0.5,
            "model_calls": 20,
            "tokens": 1200,
            "input_tokens": 1000,
            "output_tokens": 200,
            "wall_clock_hours": 0.5,
            "environment_episodes": 20,
            "patch_generation_calls": 3,
            "accounting_consistent": True,
        }
        manifest = {
            "idea_id": "update-trust-region",
            "phase": "P0",
            "experiment_config_hash": config_hash(config),
            "analysis_input": "candidate-evaluation.jsonl",
            "actual_environment_episodes": 20,
            "candidate_generation_contract": {
                "forbidden_inputs": ["behavior-probe-results", "hidden-original-task-results"],
                "generation_completed_before_probe_and_hidden_execution": True,
            },
        }
        self.assertEqual(validate_measured_cost(config, cost), [])
        self.assertEqual(validate_collection_manifest("update-trust-region", config, Path("candidate-evaluation.jsonl"), cost, manifest), [])

        bad_cost = dict(cost, tokens=0)
        self.assertTrue(validate_measured_cost(config, bad_cost))
        over_cap = dict(cost, environment_episodes=int(config["resource_cap"]["episodes"]) + 1)
        self.assertTrue(validate_measured_cost(config, over_cap))
        bad_manifest = copy.deepcopy(manifest)
        bad_manifest["candidate_generation_contract"]["forbidden_inputs"] = []
        self.assertTrue(validate_collection_manifest("update-trust-region", config, Path("candidate-evaluation.jsonl"), cost, bad_manifest))

        a2_config = load_json(config_path("budgeted-evolution-controller"))
        a2_manifest = {
            "idea_id": "budgeted-evolution-controller",
            "phase": "P0",
            "experiment_config_hash": config_hash(a2_config),
            "analysis_input": "fixed-sequences.jsonl",
            "actual_environment_episodes": 20,
            "sequence_generation_contract": {
                "controller_access_during_generation": True,
                "all_controllers_reuse_identical_saved_sequences": True,
                "controller_fit_splits": ["discovery", "calibration"],
                "controller_test_split": "hidden",
            },
        }
        self.assertTrue(validate_collection_manifest("budgeted-evolution-controller", a2_config, Path("fixed-sequences.jsonl"), cost, a2_manifest))

    def test_launch_readiness_requires_real_smoke_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            model = root / "model"
            model.mkdir()
            for name in ("config.json", "tokenizer.json", "model.safetensors.index.json"):
                (model / name).write_text("{}", encoding="utf-8")
            python_path = root / "python"
            python_path.write_text("", encoding="utf-8")
            alf = root / "alfworld"
            for relative in ("json_2.1.1/train", "json_2.1.1/valid_seen", "json_2.1.1/valid_unseen"):
                (alf / relative).mkdir(parents=True, exist_ok=True)
            for relative in ("logic/alfred.pddl", "logic/alfred.twl2"):
                target = alf / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("", encoding="utf-8")
            smoke = root / "p0-runtime-smoke.json"
            disk = type("Disk", (), {"free": 100 * 1024**3})()
            with patch("research_pipeline.p0_common._python_modules", return_value=({"torch": True, "transformers": True, "alfworld": True, "textworld": True}, {"alfworld": "0.4.2", "textworld": "1.7.0"})), patch("research_pipeline.p0_common.gpu_summary", return_value=[{"name": "GPU", "memory_total_mib": 1, "memory_free_mib": 1}]), patch("research_pipeline.p0_common.shutil.disk_usage", return_value=disk):
                before = runtime_preflight(model, root, python_path, root / "site", alf, smoke)
                self.assertTrue(before["environment_ready"])
                self.assertFalse(before["launch_ready"])
                smoke.write_text(json.dumps({"status": "pass", "model_path": str(model), "runtime_contract_hash": before["runtime_contract_hash"]}), encoding="utf-8")
                after = runtime_preflight(model, root, python_path, root / "site", alf, smoke)
                self.assertTrue(after["launch_ready"])
                self.assertTrue(after["stages"]["smoke_rollout_ready"])


if __name__ == "__main__":
    unittest.main()
