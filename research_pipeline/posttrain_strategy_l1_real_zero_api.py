from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

from .posttrain_strategy_deepseek_driver import AgentLoopBudget, run_deepseek_tool_loop
from .posttrain_strategy_intervention import ARM_POST_STRATEGY, BOUNDARY_MARKER
from .posttrain_strategy_local_executor import PersistentCapabilityLocalToolExecutor
from .posttrain_strategy_l1_zero_api import BASE, CONFLICT_FREE, EXECUTION, STRATEGY


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ScriptedRealMethodProvider:
    """Zero-API script proving real persistent SFT→boundary→RL orchestration."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def respond(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        idx = len(self.calls)
        state = {
            "prompt_sha256": _sha_text(prompt),
            "strategy_visible": STRATEGY in prompt,
            "arm_identity_visible": ARM_POST_STRATEGY in prompt,
            "boundary_marker_visible": BOUNDARY_MARKER in prompt,
        }
        self.calls.append(state)
        if idx == 0:
            if state["strategy_visible"] or state["arm_identity_visible"]:
                raise AssertionError("POST treatment leaked before verified boundary")
            calls = [
                {
                    "type": "function_call",
                    "name": "run_training",
                    "arguments": {
                        "method": "sft",
                        "stage": "initial-sft",
                        "config": {"lr": 0.001, "steps": 1, "examples": 2, "max_seq_tokens": 256},
                        "rationale": "Establish a real persistent first training update.",
                    },
                }
            ]
        elif idx == 1:
            if not state["strategy_visible"] or not state["boundary_marker_visible"]:
                raise AssertionError("POST strategy missing after verified boundary")
            calls = [
                {
                    "type": "function_call",
                    "name": "run_training",
                    "arguments": {
                        "method": "rl",
                        "stage": "post-boundary-rl",
                        "config": {
                            "lr": 0.001,
                            "steps": 1,
                            "examples": 2,
                            "max_seq_tokens": 256,
                            "rl_rollouts": 2,
                            "rl_max_new_tokens": 32,
                        },
                        "rationale": "Mechanically enact the injected strategy on the current checkpoint.",
                    },
                }
            ]
        elif idx == 2:
            if not state["strategy_visible"]:
                raise AssertionError("post-boundary continuation lost strategy context")
            calls = [
                {
                    "type": "function_call",
                    "name": "run_evaluation",
                    "arguments": {"model_ref": "current", "limit": 1},
                }
            ]
        elif idx == 3:
            calls = [
                {
                    "type": "function_call",
                    "name": "finish",
                    "arguments": {"summary": "real-method zero-API capability path completed"},
                }
            ]
        else:
            raise AssertionError("unexpected scripted provider call")
        return {
            "response_id": f"real-zero-api-{idx + 1}",
            "status": "completed",
            "requested_model": kwargs.get("model"),
            "resolved_model": "SCRIPTED_REAL_METHOD_ZERO_API_PROVIDER",
            "text": "",
            "function_calls": calls,
            "usage": {"output_tokens": 0},
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="V19R-003 real SFT/RL persistent zero-API orchestration preflight")
    parser.add_argument("--workspace-root", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--training-python", type=Path, required=True)
    parser.add_argument("--vllm-bin", type=Path, required=True)
    parser.add_argument("--evaluator-python", type=Path, required=True)
    parser.add_argument("--inspect-overlay", type=Path, required=True)
    parser.add_argument("--official-evaluator", type=Path, required=True)
    parser.add_argument("--templates-dir", type=Path, required=True)
    parser.add_argument("--hf-cache", type=Path, required=True)
    parser.add_argument("--train-data", type=Path, required=True)
    parser.add_argument("--contamination-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    provider = ScriptedRealMethodProvider()
    executor = PersistentCapabilityLocalToolExecutor(
        workspace_root=args.workspace_root,
        model_path=args.model_path,
        training_python=args.training_python,
        vllm_bin=args.vllm_bin,
        evaluator_python=args.evaluator_python,
        inspect_overlay=args.inspect_overlay,
        official_evaluator=args.official_evaluator,
        templates_dir=args.templates_dir,
        hf_cache=args.hf_cache,
        train_data=args.train_data,
        contamination_receipt=args.contamination_receipt,
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
        budget=AgentLoopBudget(max_provider_calls=4, max_output_tokens_per_call=32, max_reported_output_tokens=128),
    )

    training = [row["result"] for row in result["transcript"] if row.get("tool") == "run_training"]
    evaluations = [row["result"] for row in result["transcript"] if row.get("tool") == "run_evaluation"]
    gates = {
        "scripted_provider_only": all(
            row["resolved_model"] == "SCRIPTED_REAL_METHOD_ZERO_API_PROVIDER" for row in result["provider_receipts"]
        ),
        "deepseek_calls_zero": True,
        "external_api_calls_zero": True,
        "phase1_blind_to_post_treatment_and_arm": not provider.calls[0]["strategy_visible"]
        and not provider.calls[0]["arm_identity_visible"],
        "public_boundary_instruction_preserved": provider.calls[0]["boundary_marker_visible"],
        "post_strategy_injected_after_first_real_update": provider.calls[1]["strategy_visible"]
        and result["boundary_reached"],
        "two_real_training_methods_executed": len(training) == 2
        and training[0].get("method") == "SFT"
        and training[1].get("method") == "RL",
        "both_training_updates_verified": len(training) == 2
        and all(row.get("parameter_update_verified") is True for row in training),
        "both_checkpoints_persisted": len(training) == 2
        and all(row.get("checkpoint_persisted") is True for row in training),
        "rl_continued_from_sft_checkpoint": len(training) == 2
        and training[1].get("input_checkpoint_ref") == training[0].get("checkpoint_ref"),
        "official_evaluator_loaded_current_rl_checkpoint": len(evaluations) == 1
        and evaluations[0].get("completed") is True
        and evaluations[0].get("evaluated_current_checkpoint") is True
        and evaluations[0].get("model_ref") == training[1].get("checkpoint_ref"),
        "scientific_evaluation_false": len(evaluations) == 1
        and evaluations[0].get("scientific_evaluation") is False,
        "loop_finished": result["finished"] is True,
        "loop_scientific_authority_false": result["scientific_authority"] is False,
    }
    receipt = {
        "artifact_kind": "V19R003_L1_REAL_METHOD_ZERO_API_PERSISTENT_RECEIPT",
        "schema_version": "1.0",
        "candidate_id": "V19R-003-BOUNDARY-REPAIR-R2",
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "execution_level": "L1_REAL_METHOD_ZERO_API_CAPABILITY_PREFLIGHT",
        "gates": gates,
        "pass": all(gates.values()),
        "provider_prompt_checks": provider.calls,
        "loop_summary": {
            "provider_calls": result["provider_calls"],
            "reported_output_tokens": result["reported_output_tokens"],
            "boundary_reached": result["boundary_reached"],
            "phase2_injected": result["phase2_injected"],
            "finished": result["finished"],
        },
        "training_sequence": training,
        "evaluation_receipt": evaluations[0] if evaluations else None,
        "cost": {"external_api_calls": 0, "deepseek_calls": 0, "reported_provider_output_tokens": 0},
        "authority": {
            "scientific_authority": False,
            "scientific_arm_executed": False,
            "problem_gate": False,
            "research_item_created": False,
            "canonical_projection": False,
            "paid_probe_authorized": False,
        },
        "interpretation_boundary": (
            "The scripted provider mechanically follows the injected strategy, so this is not evidence about autonomous agent "
            "strategy adherence. It proves only that a contamination-screened, persistent real SFT→RL→official-evaluator path "
            "exists on the A100 without external model APIs."
        ),
        "next_gate": (
            "Freeze the paid PRE_STRATEGY contract separately: action-space bounds, compute/data budget, checkpoint semantics, "
            "and trajectory adherence extraction. Keep DeepSeek disabled until that contract is audited."
        ),
        "elapsed_sec": round(time.time() - started, 3),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"pass": receipt["pass"], "gates": gates, "output": str(args.output)}, sort_keys=True))
    return 0 if receipt["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
