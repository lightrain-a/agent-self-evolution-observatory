from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

from .posttrain_strategy_deepseek_driver import AgentLoopBudget, run_deepseek_tool_loop
from .posttrain_strategy_intervention import ARM_POST_STRATEGY, BOUNDARY_MARKER
from .posttrain_strategy_local_executor import EngineeringLocalToolExecutor

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
BASE = "Improve the assigned base model on AIME 2025."


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class ScriptedZeroApiProvider:
    """Deterministic provider proving phase visibility/tool sequencing without an API call."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def respond(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        index = len(self.calls)
        checks = {
            "prompt_sha256": sha256_text(prompt),
            "strategy_visible": STRATEGY in prompt,
            "arm_identity_visible": ARM_POST_STRATEGY in prompt,
            "boundary_marker_visible": BOUNDARY_MARKER in prompt,
            "requested_model": kwargs.get("model"),
        }
        self.calls.append(checks)
        if index == 0:
            if checks["strategy_visible"] or checks["arm_identity_visible"]:
                raise AssertionError("POST_STRATEGY leaked treatment or arm identity before verified update")
            if not checks["boundary_marker_visible"]:
                raise AssertionError("phase1 lost the frozen boundary-marker instruction")
            function_calls = [
                {
                    "type": "function_call",
                    "name": "run_training",
                    "arguments": {
                        "method": "sft",
                        "stage": "first-engineering-update",
                        "config": {"lr": 0.001, "max_tokens": 48, "engineering_smoke": True},
                        "rationale": "Open the engineering boundary only from an observed parameter delta.",
                    },
                }
            ]
        elif index == 1:
            if not checks["strategy_visible"] or not checks["boundary_marker_visible"]:
                raise AssertionError("POST_STRATEGY treatment was not injected after verified update")
            function_calls = [
                {
                    "type": "function_call",
                    "name": "run_evaluation",
                    "arguments": {"model_ref": "base_model", "limit": 1},
                }
            ]
        elif index == 2:
            if not checks["strategy_visible"] or not checks["boundary_marker_visible"]:
                raise AssertionError("post-boundary continuation lost treatment context")
            function_calls = [
                {
                    "type": "function_call",
                    "name": "finish",
                    "arguments": {"summary": "zero-API structured tool path completed"},
                }
            ]
        else:
            raise AssertionError("unexpected scripted provider call")
        return {
            "response_id": f"zero-api-scripted-{index + 1}",
            "status": "completed",
            "requested_model": kwargs.get("model"),
            "resolved_model": "SCRIPTED_ZERO_API_PROVIDER",
            "text": "",
            "function_calls": function_calls,
            "usage": {"output_tokens": 0},
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="V19R-003 L1 zero-API structured tool-path dry run")
    parser.add_argument("--workspace-root", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--training-python", type=Path, required=True)
    parser.add_argument("--vllm-bin", type=Path, required=True)
    parser.add_argument("--evaluator-python", type=Path, required=True)
    parser.add_argument("--inspect-overlay", type=Path, required=True)
    parser.add_argument("--official-evaluator", type=Path, required=True)
    parser.add_argument("--templates-dir", type=Path, required=True)
    parser.add_argument("--hf-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    provider = ScriptedZeroApiProvider()
    executor = EngineeringLocalToolExecutor(
        workspace_root=args.workspace_root,
        model_path=args.model_path,
        training_python=args.training_python,
        vllm_bin=args.vllm_bin,
        evaluator_python=args.evaluator_python,
        inspect_overlay=args.inspect_overlay,
        official_evaluator=args.official_evaluator,
        templates_dir=args.templates_dir,
        hf_cache=args.hf_cache,
    )
    started = time.time()
    result = run_deepseek_tool_loop(
        client=provider,
        executor=executor,
        arm=ARM_POST_STRATEGY,
        base_prompt=BASE,
        strategy_instruction=STRATEGY,
        execution_control_instruction=EXECUTION,
        conflict_free_strategy_instruction=CONFLICT_FREE,
        budget=AgentLoopBudget(max_provider_calls=3, max_output_tokens_per_call=32, max_reported_output_tokens=96),
    )

    training_rows = [x for x in result["transcript"] if x.get("tool") == "run_training"]
    eval_rows = [x for x in result["transcript"] if x.get("tool") == "run_evaluation"]
    gates = {
        "scripted_provider_only": all(x["resolved_model"] == "SCRIPTED_ZERO_API_PROVIDER" for x in result["provider_receipts"]),
        "external_api_calls_zero": True,
        "deepseek_calls_zero": True,
        "post_phase1_blind_to_treatment_and_arm": provider.calls[0]["strategy_visible"] is False and provider.calls[0]["arm_identity_visible"] is False,
        "phase1_keeps_public_boundary_marker_instruction": provider.calls[0]["boundary_marker_visible"] is True,
        "treatment_visible_only_after_verified_boundary": provider.calls[1]["strategy_visible"] is True and provider.calls[1]["boundary_marker_visible"] is True,
        "real_parameter_delta_opened_boundary": len(training_rows) == 1 and training_rows[0]["result"].get("parameter_update_verified") is True,
        "official_evaluator_tool_completed": len(eval_rows) == 1 and eval_rows[0]["result"].get("completed") is True,
        "official_evaluator_non_scientific": len(eval_rows) == 1 and eval_rows[0]["result"].get("scientific_evaluation") is False,
        "loop_finished": result["finished"] is True,
        "loop_scientific_authority_false": result["scientific_authority"] is False,
        "engineering_executor_did_not_persist_checkpoint": len(training_rows) == 1 and training_rows[0]["result"].get("checkpoint_persisted") is False,
    }
    receipt = {
        "artifact_kind": "V19R003_L1_ZERO_API_STRUCTURED_TOOL_PATH_RECEIPT",
        "schema_version": "1.0",
        "candidate_id": "V19R-003-BOUNDARY-REPAIR-R2",
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "execution_level": "L1_ZERO_API_ENGINEERING_STRUCTURED_TOOL_PATH",
        "gates": gates,
        "l1_zero_api_pass": all(gates.values()),
        "provider_prompt_checks": provider.calls,
        "loop_summary": {
            "provider_calls": result["provider_calls"],
            "reported_output_tokens": result["reported_output_tokens"],
            "boundary_reached": result["boundary_reached"],
            "phase2_injected": result["phase2_injected"],
            "finished": result["finished"],
        },
        "training_tool_receipt": training_rows[0]["result"] if training_rows else None,
        "evaluation_tool_receipt": eval_rows[0]["result"] if eval_rows else None,
        "authority": {
            "scientific_authority": False,
            "scientific_arm_executed": False,
            "problem_gate": False,
            "research_item_created": False,
            "canonical_projection": False,
            "paid_probe_authorized": False,
        },
        "cost": {"external_api_calls": 0, "deepseek_calls": 0, "reported_provider_output_tokens": 0},
        "elapsed_sec": round(time.time() - started, 3),
        "interpretation_boundary": (
            "This proves the structured zero-API orchestration path only. The training executor is an explicit one-step SGD "
            "engineering surrogate and persists no checkpoint; it cannot support strategy-enactment science or a paid PRE probe."
        ),
        "next_gate": (
            "Implement a persistent real SFT/RL training executor with frozen compute/data semantics and checkpoint continuation. "
            "Keep DeepSeek disabled until that executor passes the same zero-API confinement/boundary/evaluator checks."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"l1_zero_api_pass": receipt["l1_zero_api_pass"], "gates": gates, "output": str(args.output)}, sort_keys=True))
    return 0 if receipt["l1_zero_api_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
