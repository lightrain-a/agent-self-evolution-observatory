from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from .posttrain_strategy_local_executor import EngineeringLocalToolExecutor, PersistentCapabilityLocalToolExecutor


class EngineeringLocalExecutorGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.workspace = root / "workspace"
        self.model = root / "model"
        self.overlay = root / "site-packages"
        self.templates = root / "templates"
        self.hf = root / "hf"
        for directory in (self.workspace, self.model, self.overlay, self.templates, self.hf):
            directory.mkdir(parents=True, exist_ok=True)
        self.training_python = root / "training-python"
        self.vllm = root / "vllm"
        self.eval_python = root / "eval-python"
        self.evaluator = root / "evaluate.py"
        for path in (self.training_python, self.vllm, self.eval_python, self.evaluator):
            path.write_text("stub\n", encoding="utf-8")
        (self.templates / "qwen3.jinja").write_text("stub\n", encoding="utf-8")
        self.executor = EngineeringLocalToolExecutor(
            workspace_root=self.workspace,
            model_path=self.model,
            training_python=self.training_python,
            vllm_bin=self.vllm,
            evaluator_python=self.eval_python,
            inspect_overlay=self.overlay,
            official_evaluator=self.evaluator,
            templates_dir=self.templates,
            hf_cache=self.hf,
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_virtualenv_executable_paths_are_not_symlink_resolved(self) -> None:
        # A venv's bin/python is normally a symlink to the base interpreter; resolving it would
        # bypass the venv site-packages when invoked as a subprocess.
        target = Path(self.tmp.name) / "base-python"
        target.write_text("stub\n", encoding="utf-8")
        link = Path(self.tmp.name) / "venv-python"
        link.symlink_to(target)
        executor = EngineeringLocalToolExecutor(
            workspace_root=self.workspace,
            model_path=self.model,
            training_python=link,
            vllm_bin=self.vllm,
            evaluator_python=self.eval_python,
            inspect_overlay=self.overlay,
            official_evaluator=self.evaluator,
            templates_dir=self.templates,
            hf_cache=self.hf,
        )
        self.assertEqual(link, executor.training_python)

    def test_workspace_inspection_is_root_confined(self) -> None:
        visible = self.workspace / "state.txt"
        visible.write_text("safe state", encoding="utf-8")
        receipt = self.executor.execute("inspect_workspace", {"path": "state.txt"})
        self.assertEqual("safe state", receipt["content"])
        self.assertTrue(receipt["executor_root_confined"])
        with self.assertRaisesRegex(ValueError, "escaped executor root"):
            self.executor.execute("inspect_workspace", {"path": "../outside.txt"})

    def test_symlink_escape_is_rejected(self) -> None:
        outside = Path(self.tmp.name) / "outside.txt"
        outside.write_text("secret", encoding="utf-8")
        link = self.workspace / "link.txt"
        link.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "escaped executor root|symlink"):
            self.executor.execute("inspect_workspace", {"path": "link.txt"})

    def test_engineering_training_refuses_rl(self) -> None:
        with self.assertRaisesRegex(ValueError, "real RL is not implemented"):
            self.executor.execute(
                "run_training",
                {"method": "rl", "stage": "main", "config": {"engineering_smoke": True}},
            )

    def test_engineering_training_requires_explicit_smoke_flag(self) -> None:
        with self.assertRaisesRegex(ValueError, "engineering_smoke=true"):
            self.executor.execute(
                "run_training",
                {"method": "sft", "stage": "warmup", "config": {"lr": 0.001}},
            )

    def test_engineering_training_rejects_unknown_config(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported engineering training config"):
            self.executor.execute(
                "run_training",
                {
                    "method": "sft",
                    "stage": "warmup",
                    "config": {"engineering_smoke": True, "shell": "echo nope"},
                },
            )

    def test_engineering_evaluator_is_one_sample_only(self) -> None:
        with self.assertRaisesRegex(ValueError, "hard-capped at one sample"):
            self.executor.execute("run_evaluation", {"model_ref": "base_model", "limit": 2})

    def test_engineering_evaluator_rejects_arbitrary_model_path(self) -> None:
        with self.assertRaisesRegex(ValueError, "pinned base model"):
            self.executor.execute("run_evaluation", {"model_ref": "/tmp/other-model", "limit": 1})

    def _persistent_executor(self, *, clean: bool = True, sha_match: bool = True) -> PersistentCapabilityLocalToolExecutor:
        train = Path(self.tmp.name) / "train.jsonl"
        train.write_text('{"question":"1+1?","answer":"#### 2"}\n', encoding="utf-8")
        actual_sha = hashlib.sha256(train.read_bytes()).hexdigest()
        contamination = Path(self.tmp.name) / "contamination.json"
        contamination.write_text(
            json.dumps(
                {
                    "clean": clean,
                    "checker_exit_code": 0,
                    "contaminated_documents": 0,
                    "total_matches": 0,
                    "training_sha256": actual_sha if sha_match else "0" * 64,
                }
            ),
            encoding="utf-8",
        )
        return PersistentCapabilityLocalToolExecutor(
            workspace_root=self.workspace,
            model_path=self.model,
            training_python=self.training_python,
            vllm_bin=self.vllm,
            evaluator_python=self.eval_python,
            inspect_overlay=self.overlay,
            official_evaluator=self.evaluator,
            templates_dir=self.templates,
            hf_cache=self.hf,
            train_data=train,
            contamination_receipt=contamination,
        )

    def test_persistent_executor_requires_clean_contamination_receipt(self) -> None:
        with self.assertRaisesRegex(ValueError, "not clean"):
            self._persistent_executor(clean=False)

    def test_persistent_executor_binds_training_data_sha(self) -> None:
        with self.assertRaisesRegex(ValueError, "SHA"):
            self._persistent_executor(sha_match=False)

    def test_persistent_executor_rejects_unbounded_training_config_before_subprocess(self) -> None:
        executor = self._persistent_executor()
        with self.assertRaisesRegex(ValueError, "steps must be in"):
            executor.execute(
                "run_training",
                {"method": "sft", "stage": "too-large", "config": {"steps": 99}},
            )
        with self.assertRaisesRegex(ValueError, "unsupported persistent training config"):
            executor.execute(
                "run_training",
                {"method": "rl", "stage": "bad", "config": {"command": "python train.py"}},
            )

    def test_persistent_executor_global_action_caps_fail_closed(self) -> None:
        executor = self._persistent_executor()
        executor._real_training_counter = 2
        with self.assertRaisesRegex(RuntimeError, "training-action budget exhausted"):
            executor.execute("run_training", {"method": "sft", "stage": "third", "config": {}})
        executor._evaluation_counter = 1
        with self.assertRaisesRegex(RuntimeError, "evaluation-action budget exhausted"):
            executor.execute("run_evaluation", {"model_ref": "current", "limit": 1})


if __name__ == "__main__":
    unittest.main()
