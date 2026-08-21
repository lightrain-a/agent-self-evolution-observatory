from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.d5_state_sufficiency_f0 import MEMORY_IDS, TARGET_FAMILIES, analyze_rows, compile_contract, historical_task_exposure


class D5StateSufficiencyF0Test(unittest.TestCase):
    def _fixture(self, root: Path, *, common_panel: bool = True):
        src = root / "mem.jsonl"
        src.write_text("\n".join(json.dumps({
            "memory_id": mid,
            "source_family": "pick_heat_then_place_in_recep",
            "candidate_index": i,
            "candidate_role": "heldout_candidate" if i == 3 else "development",
            "source_task_id": str(root / f"source-{i}" / "game.tw-pddl"),
            "text": f"memory {i}",
        }) for i, mid in enumerate(MEMORY_IDS, 1)) + "\n", encoding="utf-8")

        main = root / "main.csv"
        fields = ["memory_id", "evaluation_role", "target_family", "target_task_id", "retrieved_success", "placebo_success", "no_memory_success"]
        with main.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for mid_index, mid in enumerate(MEMORY_IDS):
                for fam_index, fam in enumerate(TARGET_FAMILIES):
                    task_name = f"common-{fam}" if common_panel else f"different-{mid_index}-{fam}"
                    value = 1 if fam_index == 0 else 0
                    writer.writerow({
                        "memory_id": mid,
                        "evaluation_role": "probe_development",
                        "target_family": fam,
                        "target_task_id": str(root / "json_2.1.1" / "valid_unseen" / task_name / "trial" / "game.tw-pddl"),
                        "retrieved_success": value,
                        "placebo_success": value,
                        "no_memory_success": value,
                    })
                writer.writerow({
                    "memory_id": mid,
                    "evaluation_role": "future_eval",
                    "target_family": "pick_heat_then_place_in_recep",
                    "target_task_id": str(root / f"oldfuture-{mid}" / "game.tw-pddl"),
                    "retrieved_success": 0,
                    "placebo_success": 0,
                    "no_memory_success": 0,
                })

        alfworld = root / "alf"
        for fam in TARGET_FAMILIES:
            for i in range(3):
                path = alfworld / "json_2.1.1" / "valid_unseen" / f"{fam}-Obj-None-Recep-{i}" / f"trial-{i}" / "game.tw-pddl"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("x", encoding="utf-8")

        model = root / "model"
        model.mkdir()
        for name in ("config.json", "model.safetensors.index.json", "tokenizer_config.json", "tokenizer.json"):
            (model / name).write_text(name, encoding="utf-8")
        (model / "model-00001-of-00001.safetensors").write_bytes(b"weights")
        cfg = root / "cfg.yaml"
        cfg.write_text("x", encoding="utf-8")
        return src, main, alfworld, model, cfg

    def test_contract_requires_common_nondegenerate_panel(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src, main, alfworld, model, cfg = self._fixture(Path(tmp), common_panel=True)
            contract = compile_contract(source_memories_path=src, historical_main_table_path=main, alfworld_root=alfworld, model_path=model, config_path=cfg)
            self.assertEqual(contract["episodes"], 54)
            self.assertEqual(len(contract["task_selection"]["selected_tasks"]), 6)
            self.assertEqual(len(contract["development_equivalence"]["common_panel"]), 3)
            self.assertTrue(contract["development_equivalence"]["nondegenerate_required"])

    def test_contract_rejects_same_scores_on_different_probe_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src, main, alfworld, model, cfg = self._fixture(Path(tmp), common_panel=False)
            with self.assertRaisesRegex(ValueError, "common development panel"):
                compile_contract(source_memories_path=src, historical_main_table_path=main, alfworld_root=alfworld, model_path=model, config_path=cfg)

    def test_execution_exposure_includes_stage_raw_but_not_plan_only_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = "json_2.1.1/valid_unseen/pick_and_place_simple-Mug-None-Desk-1/trial/game.tw-pddl"
            (root / "stage-a-raw.jsonl").write_text(json.dumps({"task_relpath": task}) + "\n", encoding="utf-8")
            (root / "candidate-plan.json").write_text(json.dumps({"task_relpath": "json_2.1.1/valid_unseen/pick_and_place_simple-Plan-None-Desk-1/trial/game.tw-pddl"}), encoding="utf-8")
            exposed = historical_task_exposure(root)
            self.assertIn(task, exposed)
            self.assertFalse(any("-Plan-" in item for item in exposed))

    def test_analysis_requires_two_tasks_two_families(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src, main, alfworld, model, cfg = self._fixture(Path(tmp), common_panel=True)
            contract = compile_contract(source_memories_path=src, historical_main_table_path=main, alfworld_root=alfworld, model_path=model, config_path=cfg)
            rows = []
            tasks = contract["task_selection"]["selected_tasks"]
            for task_index, task in enumerate(tasks):
                for memory_index, mid in enumerate(MEMORY_IDS):
                    for arm in ("no-memory", "placebo", "retrieved"):
                        success = int(arm == "retrieved" and task_index in {0, 2} and memory_index == 2)
                        rows.append({"memory_id": mid, "task_relpath": task["task_relpath"], "arm": arm, "success": success, "actions": ["look"]})
            result = analyze_rows(rows, contract)
            self.assertEqual(result["decision"], "GO_PROSPECTIVE_CONFIRMATION")
            self.assertEqual(result["divergent_task_count"], 2)
            self.assertEqual(result["divergent_target_family_count"], 2)

    def test_analysis_stops_on_one_family_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src, main, alfworld, model, cfg = self._fixture(Path(tmp), common_panel=True)
            contract = compile_contract(source_memories_path=src, historical_main_table_path=main, alfworld_root=alfworld, model_path=model, config_path=cfg)
            rows = []
            tasks = contract["task_selection"]["selected_tasks"]
            for task_index, task in enumerate(tasks):
                for memory_index, mid in enumerate(MEMORY_IDS):
                    for arm in ("no-memory", "placebo", "retrieved"):
                        success = int(arm == "retrieved" and task_index in {0, 1} and memory_index == 2)
                        rows.append({"memory_id": mid, "task_relpath": task["task_relpath"], "arm": arm, "success": success, "actions": ["look"]})
            result = analyze_rows(rows, contract)
            self.assertEqual(result["decision"], "STOP_CURRENT_STATE_SUFFICIENCY_PAPER")
            self.assertEqual(result["divergent_task_count"], 2)
            self.assertEqual(result["divergent_target_family_count"], 1)


if __name__ == "__main__":
    unittest.main()
