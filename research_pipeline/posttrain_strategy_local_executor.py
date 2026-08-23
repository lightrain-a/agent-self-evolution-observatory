from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any


class EngineeringLocalToolExecutor:
    """Zero-API executor for L1 engineering preflight only.

    It intentionally does not implement scientific SFT/RL.  ``run_training`` performs a one-step
    SGD surrogate solely to prove that the structured tool path can open a boundary from an
    independently observed parameter delta.  Paid/scientific runs must use a different executor.
    """

    def __init__(
        self,
        *,
        workspace_root: Path,
        model_path: Path,
        training_python: Path,
        vllm_bin: Path,
        evaluator_python: Path,
        inspect_overlay: Path,
        official_evaluator: Path,
        templates_dir: Path,
        hf_cache: Path,
    ) -> None:
        self.workspace_root = workspace_root.resolve()
        self.model_path = model_path.resolve()
        # Do not Path.resolve() virtualenv executables: resolving venv/bin/python follows its
        # interpreter symlink and silently bypasses the virtualenv's sys.prefix/site-packages.
        self.training_python = Path(os.path.abspath(training_python))
        self.vllm_bin = Path(os.path.abspath(vllm_bin))
        self.evaluator_python = Path(os.path.abspath(evaluator_python))
        self.inspect_overlay = inspect_overlay.resolve()
        self.official_evaluator = official_evaluator.resolve()
        self.templates_dir = templates_dir.resolve()
        self.hf_cache = hf_cache.resolve()
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        (self.workspace_root / "receipts").mkdir(exist_ok=True)
        for path in (
            self.model_path,
            self.training_python,
            self.vllm_bin,
            self.evaluator_python,
            self.inspect_overlay,
            self.official_evaluator,
            self.templates_dir,
            self.hf_cache,
        ):
            if not path.exists():
                raise FileNotFoundError(path)
        self._training_counter = 0
        self._evaluation_counter = 0

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    @staticmethod
    def _clean_env() -> dict[str, str]:
        env = os.environ.copy()
        for key in (
            "ANTHROPIC_API_KEY",
            "ANTHROPIC_AUTH_TOKEN",
            "CLAUDE_CODE_OAUTH_TOKEN",
            "OPENAI_API_KEY",
            "DEEPSEEK_API_KEY",
            "ARK_API_KEY",
            "VOLCENGINE_API_KEY",
            "GOOGLE_API_KEY",
            "GEMINI_API_KEY",
        ):
            env.pop(key, None)
        return env

    def _safe_workspace_file(self, raw_path: str) -> Path:
        if not raw_path:
            raise ValueError("workspace path is empty")
        candidate = (self.workspace_root / raw_path).resolve()
        try:
            candidate.relative_to(self.workspace_root)
        except ValueError as exc:
            raise ValueError("workspace path escaped executor root") from exc
        if candidate.is_symlink():
            raise ValueError("symlink inspection is forbidden")
        return candidate

    def execute(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "inspect_workspace":
            return self._inspect_workspace(arguments)
        if name == "run_training":
            return self._run_training(arguments)
        if name == "run_evaluation":
            return self._run_evaluation(arguments)
        raise ValueError(f"unsupported executor tool:{name}")

    def _inspect_workspace(self, arguments: dict[str, Any]) -> dict[str, Any]:
        path = self._safe_workspace_file(str(arguments.get("path") or "").strip())
        if path.is_dir():
            entries = []
            for child in sorted(path.iterdir(), key=lambda item: item.name)[:64]:
                if child.is_symlink():
                    kind = "symlink"
                elif child.is_dir():
                    kind = "directory"
                elif child.is_file():
                    kind = "file"
                else:
                    kind = "other"
                entries.append({"name": child.name, "kind": kind})
            return {
                "path": "." if path == self.workspace_root else str(path.relative_to(self.workspace_root)),
                "kind": "directory",
                "entries": entries,
                "entry_count_returned": len(entries),
                "entry_cap": 64,
                "executor_root_confined": True,
                "scientific_authority": False,
            }
        if not path.is_file():
            raise FileNotFoundError(path)
        size = path.stat().st_size
        if size > 64 * 1024:
            raise ValueError("workspace file exceeds 64 KiB inspection cap")
        content = path.read_text(encoding="utf-8")
        return {
            "path": str(path.relative_to(self.workspace_root)),
            "kind": "file",
            "size_bytes": size,
            "sha256": self._sha256(path),
            "content": content,
            "executor_root_confined": True,
            "scientific_authority": False,
        }

    def _run_training(self, arguments: dict[str, Any]) -> dict[str, Any]:
        method = str(arguments.get("method") or "").strip().lower()
        stage = str(arguments.get("stage") or "").strip()
        config = arguments.get("config")
        if method != "sft":
            raise ValueError("engineering executor supports only the SFT-labelled boundary smoke; real RL is not implemented")
        if not stage:
            raise ValueError("training stage is required")
        if not isinstance(config, dict):
            raise ValueError("training config must be an object")
        allowed = {"lr", "max_tokens", "engineering_smoke"}
        unknown = sorted(set(config) - allowed)
        if unknown:
            raise ValueError("unsupported engineering training config fields:" + ",".join(unknown))
        if config.get("engineering_smoke") is not True:
            raise ValueError("engineering_smoke=true is required; this executor cannot run scientific training")
        lr = float(config.get("lr", 0.001))
        max_tokens = int(config.get("max_tokens", 48))
        if not (0.0 < lr <= 0.01):
            raise ValueError("engineering lr must be in (0, 0.01]")
        if not (8 <= max_tokens <= 128):
            raise ValueError("engineering max_tokens must be in [8, 128]")

        self._training_counter += 1
        output = self.workspace_root / "receipts" / f"training-{self._training_counter:02d}.json"
        env = self._clean_env()
        env.update({"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "HF_DATASETS_OFFLINE": "1"})
        proc = subprocess.run(
            [
                str(self.training_python),
                "-m",
                "research_pipeline.posttrain_strategy_training_worker",
                "--model-path",
                str(self.model_path),
                "--learning-rate",
                str(lr),
                "--max-tokens",
                str(max_tokens),
                "--output",
                str(output),
            ],
            cwd=str(Path(__file__).resolve().parents[1]),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180,
            check=False,
        )
        if proc.returncode != 0 or not output.is_file():
            raise RuntimeError("engineering training worker failed:" + proc.stderr[-1200:])
        receipt = json.loads(output.read_text(encoding="utf-8"))
        if receipt.get("scientific_use_forbidden") is not True:
            raise RuntimeError("training worker receipt lost zero-authority marker")
        return {
            "exit_code": proc.returncode,
            "method_label": method,
            "stage": stage,
            "parameter_update_verified": receipt.get("parameter_update_verified") is True,
            "changed_probe_elements": receipt.get("changed_probe_elements"),
            "training_semantics": receipt.get("training_semantics"),
            "receipt": str(output.relative_to(self.workspace_root)),
            "receipt_sha256": self._sha256(output),
            "checkpoint": None,
            "checkpoint_persisted": False,
            "scientific_use_forbidden": True,
            "external_api_calls": 0,
            "deepseek_calls": 0,
        }

    @staticmethod
    def _wait_vllm(port: int, process: subprocess.Popen[str], timeout_sec: int = 90) -> None:
        deadline = time.time() + timeout_sec
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}/v1/models", headers={"Authorization": "Bearer inspectai"}
        )
        while time.time() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"local vLLM exited early with code {process.returncode}")
            try:
                with urllib.request.urlopen(request, timeout=2) as response:
                    if response.status == 200:
                        return
            except Exception:
                pass
            time.sleep(1)
        raise TimeoutError("local vLLM did not become ready")

    @staticmethod
    def _terminate_process_group(process: subprocess.Popen[str]) -> None:
        if process.poll() is not None:
            return
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        deadline = time.time() + 10
        while time.time() < deadline and process.poll() is None:
            time.sleep(0.2)
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    def _run_evaluation(self, arguments: dict[str, Any]) -> dict[str, Any]:
        model_ref = str(arguments.get("model_ref") or "").strip()
        limit = int(arguments.get("limit") or 0)
        if model_ref not in {"base_model", str(self.model_path)}:
            raise ValueError("engineering evaluator allows only the pinned base model")
        if limit != 1:
            raise ValueError("engineering evaluator smoke is hard-capped at one sample")
        return self._official_evaluator_smoke(self.model_path, model_ref="base_model")

    def _official_evaluator_smoke(self, model_path: Path, *, model_ref: str) -> dict[str, Any]:
        model_path = model_path.resolve()
        if not model_path.is_dir():
            raise FileNotFoundError(model_path)
        self._evaluation_counter += 1
        run_dir = self.workspace_root / "evaluator" / f"run-{self._evaluation_counter:02d}"
        run_dir.mkdir(parents=True, exist_ok=True)
        log_path = run_dir / "vllm-server.log"
        metrics_path = run_dir / "metrics.json"
        inspect_logs = run_dir / "logs"
        inspect_logs.mkdir(exist_ok=True)
        port = 31900 + self._evaluation_counter

        server_env = self._clean_env()
        server_env.pop("PYTHONPATH", None)
        server_env["CUDA_VISIBLE_DEVICES"] = "0"
        template = self.templates_dir / "qwen3.jinja"
        with log_path.open("w", encoding="utf-8") as log_handle:
            server = subprocess.Popen(
                [
                    str(self.vllm_bin),
                    "serve",
                    str(model_path),
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                    "--api-key",
                    "inspectai",
                    "--gpu-memory-utilization",
                    "0.25",
                    "--max-model-len",
                    "4096",
                    "--chat-template",
                    str(template),
                ],
                cwd=str(run_dir),
                env=server_env,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
            )
            try:
                self._wait_vllm(port, server)
                eval_env = self._clean_env()
                eval_env.update(
                    {
                        "PYTHONPATH": str(self.inspect_overlay),
                        "VLLM_BASE_URL": f"http://127.0.0.1:{port}/v1",
                        "VLLM_API_KEY": "inspectai",
                        "HF_HOME": str(self.hf_cache),
                        "HF_DATASETS_CACHE": str(self.hf_cache / "datasets"),
                        "HF_HUB_OFFLINE": "1",
                        "HF_DATASETS_OFFLINE": "1",
                        "INSPECT_LOG_DIR": str(inspect_logs),
                        "CUDA_VISIBLE_DEVICES": "0",
                    }
                )
                proc = subprocess.run(
                    [
                        str(self.evaluator_python),
                        str(self.official_evaluator),
                        "--model-path",
                        str(model_path),
                        "--templates-dir",
                        str(self.templates_dir),
                        "--limit",
                        "1",
                        "--max-tokens",
                        "96",
                        "--max-connections",
                        "1",
                        "--gpu-memory-utilization",
                        "0.25",
                        "--json-output-file",
                        str(metrics_path),
                    ],
                    cwd=str(run_dir),
                    env=eval_env,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=120,
                    check=False,
                )
            finally:
                self._terminate_process_group(server)
        if proc.returncode != 0 or not metrics_path.is_file():
            raise RuntimeError("official evaluator smoke failed:" + proc.stderr[-1600:] + proc.stdout[-800:])
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        safe_metric_values = {
            key: value for key, value in metrics.items() if isinstance(value, (int, float, bool)) or value is None
        }
        return {
            "completed": True,
            "model_ref": model_ref,
            "sample_limit": 1,
            "metrics_keys": sorted(metrics),
            "metric_values": safe_metric_values,
            "test_examples_disclosed": False,
            "metrics_sha256": self._sha256(metrics_path),
            "evaluator_sha256": self._sha256(self.official_evaluator),
            "template_sha256": self._sha256(template),
            "runtime_mode": "PRESTARTED_LOCAL_VLLM_PLUS_OFFICIAL_PTB_INSPECT_SCORER",
            "scientific_evaluation": False,
            "scientific_claim_use_forbidden": True,
            "receipt": str(metrics_path.relative_to(self.workspace_root)),
            "external_api_calls": 0,
            "deepseek_calls": 0,
        }


class PersistentCapabilityLocalToolExecutor(EngineeringLocalToolExecutor):
    """Zero-API real-method executor for persistent SFT→RL capability validation.

    Unlike ``EngineeringLocalToolExecutor``, this class invokes the real training worker and
    persists each full checkpoint.  It is still capability-only: one-sample evaluation and tight
    training caps intentionally prevent it from being mistaken for the paid/scientific runner.
    """

    def __init__(
        self,
        *,
        train_data: Path,
        contamination_receipt: Path,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.train_data = train_data.resolve()
        self.contamination_receipt = contamination_receipt.resolve()
        if not self.train_data.is_file():
            raise FileNotFoundError(self.train_data)
        if not self.contamination_receipt.is_file():
            raise FileNotFoundError(self.contamination_receipt)
        contamination = json.loads(self.contamination_receipt.read_text(encoding="utf-8"))
        if contamination.get("clean") is not True:
            raise ValueError("training data contamination receipt is not clean")
        if contamination.get("checker_exit_code") != 0:
            raise ValueError("training data contamination checker did not exit cleanly")
        if contamination.get("contaminated_documents") != 0 or contamination.get("total_matches") != 0:
            raise ValueError("training data contamination receipt reports matches")
        if contamination.get("training_sha256") != self._sha256(self.train_data):
            raise ValueError("training data SHA does not match contamination receipt")
        self.current_model_path = self.model_path
        self.current_checkpoint_ref = "base_model"
        self._checkpoint_paths: dict[str, Path] = {"base_model": self.model_path}
        self._real_training_counter = 0

    def _run_training(self, arguments: dict[str, Any]) -> dict[str, Any]:
        if self._real_training_counter >= 2:
            raise RuntimeError("persistent capability training-action budget exhausted")
        method = str(arguments.get("method") or "").strip().lower()
        stage = str(arguments.get("stage") or "").strip()
        config = arguments.get("config")
        if method not in {"sft", "rl"}:
            raise ValueError("persistent capability executor supports only sft or rl")
        if not stage:
            raise ValueError("training stage is required")
        if not isinstance(config, dict):
            raise ValueError("training config must be an object")
        allowed = {
            "lr",
            "steps",
            "examples",
            "max_seq_tokens",
            "rl_rollouts",
            "rl_max_new_tokens",
        }
        unknown = sorted(set(config) - allowed)
        if unknown:
            raise ValueError("unsupported persistent training config fields:" + ",".join(unknown))

        lr = float(config.get("lr", 0.001))
        steps = int(config.get("steps", 1))
        examples = int(config.get("examples", 2))
        max_seq_tokens = int(config.get("max_seq_tokens", 256))
        rl_rollouts = int(config.get("rl_rollouts", 2))
        rl_max_new_tokens = int(config.get("rl_max_new_tokens", 32))
        if not (0.0 < lr <= 0.01):
            raise ValueError("persistent capability lr must be in (0, 0.01]")
        if not (1 <= steps <= 2):
            raise ValueError("persistent capability steps must be in [1, 2]")
        if not (1 <= examples <= 8):
            raise ValueError("persistent capability examples must be in [1, 8]")
        if not (64 <= max_seq_tokens <= 512):
            raise ValueError("persistent capability max_seq_tokens must be in [64, 512]")
        if not (1 <= rl_rollouts <= 3):
            raise ValueError("persistent capability rl_rollouts must be in [1, 3]")
        if not (16 <= rl_max_new_tokens <= 64):
            raise ValueError("persistent capability rl_max_new_tokens must be in [16, 64]")

        self._real_training_counter += 1
        checkpoint_ref = f"checkpoint-{self._real_training_counter:02d}"
        checkpoint_dir = self.workspace_root / "checkpoints" / f"{self._real_training_counter:02d}-{method}"
        receipt_path = self.workspace_root / "receipts" / f"real-training-{self._real_training_counter:02d}.json"
        if checkpoint_dir.exists() or receipt_path.exists():
            raise FileExistsError("append-only checkpoint/receipt path already exists")

        env = self._clean_env()
        env.update({"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "HF_DATASETS_OFFLINE": "1"})
        command = [
            str(self.training_python),
            "-m",
            "research_pipeline.posttrain_strategy_real_training_worker",
            "--method",
            method,
            "--input-model-path",
            str(self.current_model_path),
            "--output-model-path",
            str(checkpoint_dir),
            "--train-data",
            str(self.train_data),
            "--receipt",
            str(receipt_path),
            "--learning-rate",
            str(lr),
            "--steps",
            str(steps),
            "--examples",
            str(examples),
            "--max-seq-tokens",
            str(max_seq_tokens),
            "--seed",
            "19003",
        ]
        if method == "rl":
            command.extend(
                [
                    "--rl-rollouts",
                    str(rl_rollouts),
                    "--rl-max-new-tokens",
                    str(rl_max_new_tokens),
                ]
            )
        proc = subprocess.run(
            command,
            cwd=str(Path(__file__).resolve().parents[1]),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=240,
            check=False,
        )
        if proc.returncode != 0 or not receipt_path.is_file():
            raise RuntimeError("persistent real training failed:" + proc.stderr[-1800:])
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("parameter_update_verified") is not True or receipt.get("checkpoint_persisted") is not True:
            raise RuntimeError("real training did not verify both parameter delta and persistent checkpoint")
        if receipt.get("train_data_sha256") != self._sha256(self.train_data):
            raise RuntimeError("real training receipt used an unexpected training dataset")
        if receipt.get("external_api_calls") != 0 or receipt.get("deepseek_calls") != 0:
            raise RuntimeError("real training capability receipt unexpectedly used an external API")

        input_ref = self.current_checkpoint_ref
        self.current_model_path = checkpoint_dir.resolve()
        self.current_checkpoint_ref = checkpoint_ref
        self._checkpoint_paths[checkpoint_ref] = self.current_model_path
        return {
            "exit_code": proc.returncode,
            "method": receipt.get("method"),
            "method_semantics": receipt.get("method_semantics"),
            "stage": stage,
            "input_checkpoint_ref": input_ref,
            "checkpoint_ref": checkpoint_ref,
            "parameter_update_verified": True,
            "changed_probe_elements": receipt.get("changed_probe_elements"),
            "checkpoint_persisted": True,
            "receipt": str(receipt_path.relative_to(self.workspace_root)),
            "receipt_sha256": self._sha256(receipt_path),
            "training_data_sha256": receipt.get("train_data_sha256"),
            "capability_preflight_only": True,
            "scientific_authority": False,
            "paid_probe_authorized": False,
            "external_api_calls": 0,
            "deepseek_calls": 0,
        }

    def _run_evaluation(self, arguments: dict[str, Any]) -> dict[str, Any]:
        if self._evaluation_counter >= 1:
            raise RuntimeError("persistent capability evaluation-action budget exhausted")
        model_ref = str(arguments.get("model_ref") or "").strip()
        limit = int(arguments.get("limit") or 0)
        if limit != 1:
            raise ValueError("persistent capability evaluator is hard-capped at one sample")
        if model_ref == "current":
            checkpoint_ref = self.current_checkpoint_ref
            model_path = self.current_model_path
        elif model_ref in self._checkpoint_paths:
            checkpoint_ref = model_ref
            model_path = self._checkpoint_paths[model_ref]
        else:
            raise ValueError("unknown persistent checkpoint reference")
        result = self._official_evaluator_smoke(model_path, model_ref=checkpoint_ref)
        result.update(
            {
                "evaluated_current_checkpoint": checkpoint_ref == self.current_checkpoint_ref,
                "capability_preflight_only": True,
                "scientific_authority": False,
                "paid_probe_authorized": False,
            }
        )
        return result
