from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# This runner is deliberately zero-API.  Remove provider credentials before importing
# model/runtime libraries and force local-only Hugging Face behavior.
_PROVIDER_ENV_KEYS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "CLAUDE_CODE_OAUTH_TOKEN",
    "OPENAI_API_KEY",
    "DEEPSEEK_API_KEY",
    "ARK_API_KEY",
    "VOLCENGINE_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
)
for _key in _PROVIDER_ENV_KEYS:
    os.environ.pop(_key, None)
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

from .posttrain_strategy_intervention import (  # noqa: E402
    ARM_POST_CONFLICT_FREE,
    ARM_POST_EXECUTION,
    ARM_POST_STRATEGY,
    ARM_PRE_STRATEGY,
    ARMS,
    BOUNDARY_MARKER,
    TrajectorySignals,
    assess_strategy_adherence,
    compose_segmented_prompts,
    first_successful_parameter_update_index,
    verify_phase1_boundary,
)

STRATEGY = (
    "Use supervised fine-tuning only as a small formatting warm-up. Reserve the main training "
    "budget for reinforcement learning, and omit SFT if the base model already satisfies the "
    "required output-format contract."
)
EXECUTION = (
    "Keep the training paradigm, data-source type, and stage structure fixed. For the next training "
    "only, halve the current learning rate and leave the rest of the strategy unchanged."
)
CONFLICT_FREE = (
    "Preserve the current checkpoint and completed training. Add a reinforcement-learning stage for "
    "the remaining budget without requiring rollback of already completed work."
)
BASE_PROMPT = "Improve the assigned base model on AIME 2025."


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_head(repo_root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()


def _parameter_update_smoke(model_path: Path, learning_rate: float) -> dict[str, Any]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for the L0 A100 parameter-update smoke")
    torch.manual_seed(0)
    started = time.time()
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        local_files_only=True,
        torch_dtype=torch.bfloat16,
    ).cuda().train()
    ids = tokenizer(
        "A minimal post-training smoke test verifies a real optimizer update on the local model.",
        return_tensors="pt",
    ).input_ids.cuda()[:, :48]

    probes: list[tuple[str, Any, Any]] = []
    for name, parameter in model.named_parameters():
        if parameter.requires_grad and parameter.ndim >= 2:
            probes.append((name, parameter, parameter.detach().view(-1)[:4096].clone()))
            if len(probes) >= 6:
                break
    if not probes:
        raise RuntimeError("no trainable matrix probes found")

    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
    output = model(input_ids=ids, labels=ids)
    loss = float(output.loss.detach().float().cpu())
    output.loss.backward()

    rows: list[dict[str, Any]] = []
    for name, parameter, _before in probes:
        rows.append(
            {
                "name": name,
                "grad_norm": float(parameter.grad.detach().float().norm().cpu())
                if parameter.grad is not None
                else 0.0,
            }
        )
    optimizer.step()

    total_changed = 0
    for row, (_name, parameter, before) in zip(rows, probes):
        after = parameter.detach().view(-1)[:4096]
        delta = after.float() - before.float()
        changed = int(torch.count_nonzero(after != before).cpu())
        row.update(
            {
                "changed_elements": changed,
                "abs_delta_sum": float(delta.abs().sum().cpu()),
                "max_abs_delta": float(delta.abs().max().cpu()),
            }
        )
        total_changed += changed

    verified = total_changed > 0 and any(row["grad_norm"] > 0 for row in rows)
    result = {
        "model_path": str(model_path),
        "device": torch.cuda.get_device_name(0),
        "torch_version": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "dtype": "bfloat16",
        "learning_rate": learning_rate,
        "sequence_tokens": int(ids.numel()),
        "loss": loss,
        "probe_count": len(rows),
        "changed_elements_across_probes": total_changed,
        "parameter_update_verified": verified,
        "probes": rows,
        "elapsed_sec": round(time.time() - started, 3),
        "peak_gpu_allocated_gib": round(torch.cuda.max_memory_allocated() / 1024**3, 3),
    }
    del output, optimizer, model, tokenizer
    torch.cuda.empty_cache()
    return result


def _four_arm_timing_audit() -> dict[str, Any]:
    prompts = {
        arm: compose_segmented_prompts(
            base_prompt=BASE_PROMPT,
            arm=arm,
            strategy_instruction=STRATEGY,
            execution_control_instruction=EXECUTION,
            conflict_free_strategy_instruction=CONFLICT_FREE,
        )
        for arm in ARMS
    }
    strategy_hash = prompts[ARM_PRE_STRATEGY].strategy_instruction_sha256
    checks = {
        "same_strategy_payload_pre_vs_post": strategy_hash
        == prompts[ARM_POST_STRATEGY].strategy_instruction_sha256,
        "pre_strategy_only_before_boundary": STRATEGY in prompts[ARM_PRE_STRATEGY].phase1_prompt
        and STRATEGY not in prompts[ARM_PRE_STRATEGY].phase2_prompt,
        "post_strategy_only_after_boundary": STRATEGY not in prompts[ARM_POST_STRATEGY].phase1_prompt
        and STRATEGY in prompts[ARM_POST_STRATEGY].phase2_prompt,
        "post_execution_only_after_boundary": EXECUTION not in prompts[ARM_POST_EXECUTION].phase1_prompt
        and EXECUTION in prompts[ARM_POST_EXECUTION].phase2_prompt,
        "post_conflict_free_only_after_boundary": CONFLICT_FREE not in prompts[ARM_POST_CONFLICT_FREE].phase1_prompt
        and CONFLICT_FREE in prompts[ARM_POST_CONFLICT_FREE].phase2_prompt,
        "all_phase1_prompts_require_boundary_marker": all(
            BOUNDARY_MARKER in prompts[arm].phase1_prompt for arm in ARMS
        ),
    }
    return {
        "checks": checks,
        "passed": all(checks.values()),
        "strategy_instruction_sha256": strategy_hash,
        "phase_prompt_sha256": {
            arm: {
                "phase1": prompts[arm].phase1_prompt_sha256,
                "phase2": prompts[arm].phase2_prompt_sha256,
            }
            for arm in ARMS
        },
    }


def _boundary_wiring_audit(parameter_update_verified: bool) -> dict[str, Any]:
    trace = "\n".join(
        (
            "Command: python train_sft.py --model Qwen3-1.7B-Base",
            "training finished successfully",
            BOUNDARY_MARKER,
        )
    )
    mechanical = verify_phase1_boundary(trace)
    structured_events = [
        {"kind": "setup", "exit_code": 0, "parameter_update": False},
        {"kind": "evaluation", "exit_code": 0, "parameter_update": False},
        {
            "kind": "first_training",
            "exit_code": 0,
            "parameter_update": bool(parameter_update_verified),
            "verification_source": "local-A100-observed-parameter-delta",
        },
    ]
    boundary_index = first_successful_parameter_update_index(structured_events)
    checks = {
        "mechanical_marker_and_training_candidate": mechanical["mechanical_probe_passed"],
        "semantic_parameter_update_required": mechanical["requires_semantic_parameter_update_verification"],
        "first_verified_update_index_is_training_event": boundary_index == 2,
        "failed_or_unverified_event_cannot_open_boundary": first_successful_parameter_update_index(
            [{"kind": "train", "exit_code": 0, "parameter_update": False}]
        )
        is None,
    }
    return {
        "checks": checks,
        "passed": all(checks.values()),
        "first_successful_parameter_update_index": boundary_index,
        "structured_events": structured_events,
        "mechanical_probe": mechanical,
    }


def _adherence_rubric_audit() -> dict[str, Any]:
    cases = {
        "textual_acceptance_only": assess_strategy_adherence(
            ARM_POST_STRATEGY,
            TrajectorySignals(instruction_delivered=True),
            pre_headroom_ok=True,
        ).as_dict(),
        "clean_post_strategy_enactment": assess_strategy_adherence(
            ARM_POST_STRATEGY,
            TrajectorySignals(instruction_delivered=True, strategy_change_observed=True),
            pre_headroom_ok=True,
        ).as_dict(),
        "post_strategy_reversion": assess_strategy_adherence(
            ARM_POST_STRATEGY,
            TrajectorySignals(
                instruction_delivered=True,
                strategy_change_observed=True,
                reversion_or_mixing_observed=True,
            ),
            pre_headroom_ok=True,
        ).as_dict(),
        "execution_control_enacted": assess_strategy_adherence(
            ARM_POST_EXECUTION,
            TrajectorySignals(instruction_delivered=True, execution_parameter_change_observed=True),
            pre_headroom_ok=True,
        ).as_dict(),
        "post_without_pre_headroom": assess_strategy_adherence(
            ARM_POST_STRATEGY,
            TrajectorySignals(instruction_delivered=True, strategy_change_observed=True),
            pre_headroom_ok=False,
        ).as_dict(),
    }
    expected = {
        "textual_acceptance_only": "NOT_ADHERED",
        "clean_post_strategy_enactment": "ADHERED",
        "post_strategy_reversion": "PARTIAL_OR_REVERTED",
        "execution_control_enacted": "ADHERED",
        "post_without_pre_headroom": "NO_EVIDENCE",
    }
    checks = {key: cases[key]["status"] == status for key, status in expected.items()}
    return {"checks": checks, "passed": all(checks.values()), "cases": cases}


def _evaluator_surface_audit(ptb_root: Path, model_path: Path) -> dict[str, Any]:
    evaluator = ptb_root / "src/eval/tasks/aime2025/evaluate.py"
    info = ptb_root / "src/eval/tasks/aime2025/info.json"
    template = ptb_root / "src/eval/templates/qwen3.jinja"
    model_config = model_path / "config.json"
    config = json.loads(model_config.read_text(encoding="utf-8"))
    info_payload = json.loads(info.read_text(encoding="utf-8"))
    architectures = [str(value).lower() for value in config.get("architectures", [])]
    checks = {
        "pinned_aime_evaluator_present": evaluator.is_file(),
        "aime_requires_no_external_grading_api": not bool(info_payload.get("required_api_keys", [])),
        "base_model_identifies_as_qwen": any("qwen" in value for value in architectures),
        "qwen3_template_present": template.is_file(),
        "evaluator_uses_vllm_aime2025": "model=f\"vllm/{args.model_path}\"" in evaluator.read_text(encoding="utf-8")
        and 'task = "inspect_evals/aime2025"' in evaluator.read_text(encoding="utf-8"),
    }
    return {
        "checks": checks,
        "passed": all(checks.values()),
        "scientific_evaluation_executed": False,
        "dependency_install_deferred_to_l1": True,
        "files": {
            "evaluate.py": {"path": str(evaluator), "sha256": _sha_file(evaluator)},
            "info.json": {"path": str(info), "sha256": _sha_file(info)},
            "qwen3.jinja": {"path": str(template), "sha256": _sha_file(template)},
            "model_config.json": {"path": str(model_config), "sha256": _sha_file(model_config)},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V19R-003 L0 zero-API mechanical falsifier on local A100")
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--ptb-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    model_path = args.model_path.resolve()
    ptb_root = args.ptb_root.resolve()
    if not model_path.is_dir():
        raise FileNotFoundError(model_path)
    if not ptb_root.is_dir():
        raise FileNotFoundError(ptb_root)

    parameter_update = _parameter_update_smoke(model_path, args.learning_rate)
    timing = _four_arm_timing_audit()
    boundary = _boundary_wiring_audit(bool(parameter_update["parameter_update_verified"]))
    adherence = _adherence_rubric_audit()
    evaluator = _evaluator_surface_audit(ptb_root, model_path)

    gates = {
        "real_local_parameter_update_on_a100": bool(parameter_update["parameter_update_verified"])
        and parameter_update["device"] == "NVIDIA A100-SXM4-80GB",
        "boundary_wiring": boundary["passed"],
        "four_arm_timing": timing["passed"],
        "adherence_rubric": adherence["passed"],
        "pinned_aime_evaluator_surface": evaluator["passed"],
        "zero_external_api_by_construction": True,
    }
    receipt: dict[str, Any] = {
        "artifact_kind": "V19R003_L0_ZERO_API_ENGINEERING_RECEIPT",
        "schema_version": "1.0",
        "candidate_id": "V19R-003-BOUNDARY-REPAIR-R2",
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "repo_head": _git_head(repo_root),
        "execution_level": "L0_ZERO_API_ENGINEERING_FALSIFIER",
        "authority": {
            "scientific_authority": False,
            "scientific_arm_executed": False,
            "problem_gate": False,
            "research_item_created": False,
            "canonical_projection": False,
        },
        "network_policy": {
            "provider_credentials_removed_from_process_environment": list(_PROVIDER_ENV_KEYS),
            "huggingface_offline": True,
            "external_api_calls": 0,
            "deepseek_calls": 0,
        },
        "runtime": {
            "python": sys.version.split()[0],
            "python_executable": sys.executable,
            "platform": platform.platform(),
        },
        "gates": gates,
        "l0_pass": all(gates.values()),
        "parameter_update_smoke": parameter_update,
        "boundary_audit": boundary,
        "four_arm_timing_audit": timing,
        "adherence_rubric_audit": adherence,
        "evaluator_surface_audit": evaluator,
        "interpretation_boundary": (
            "Engineering-only receipt. It validates A100 parameter-update capacity and frozen intervention mechanics; "
            "it contains no autonomous agent outcome and cannot support the candidate claim."
        ),
        "next_cost_gate": (
            "Keep API disabled. Build and run the native L1 task/training/evaluator dry path with a deterministic scripted "
            "agent before authorizing a single DeepSeek PRE_STRATEGY call."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"l0_pass": receipt["l0_pass"], "gates": gates, "output": str(args.output)}, sort_keys=True))
    return 0 if receipt["l0_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
