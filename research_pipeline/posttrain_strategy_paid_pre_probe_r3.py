from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

from .ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings
from .config import load_env_file
from .posttrain_strategy_adherence import RUBRIC_VERSION, assess_transcript_adherence
from .posttrain_strategy_deepseek_driver import ActionTurnContract, AgentLoopBudget, run_deepseek_tool_loop
from .posttrain_strategy_intervention import ARM_PRE_STRATEGY
from .posttrain_strategy_l1_zero_api import BASE, CONFLICT_FREE, EXECUTION, STRATEGY
from .posttrain_strategy_local_executor import PersistentCapabilityLocalToolExecutor
from .posttrain_strategy_sequential_gate import adjudicate_sequential_paid_gate

CANDIDATE_ID = "V19R-003-BOUNDARY-REPAIR-R2"
MODEL = "deepseek-v4-pro"
EXPECTED_CONTRACT_SHA256 = "3acdc57a2252d6e35b33d3b76d9e0724166280db886da1379587500ddcbabba6"
EXPECTED_AUTH_SHA256 = "ed68ed211def11638b53502457a5041022ff861bfa24ea5ca76f81fbeb8e6028"
EXPECTED_PREREG_SHA256 = "0ddbf339e62418648d065964e0d9c51564bf6dada894f7d5a961767449d06039"
EXPECTED_DRIVER_SHA256 = "23b5a1e11616e76b8cee74292877b43daf57dd64894372533428daaadd87559d"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_error(error: BaseException) -> str:
    text = str(error).replace("\n", " ").strip()
    return text[:800]


class AuditedArkClient:
    """Count every provider POST and permit GET-only recovery of an in-flight response."""

    def __init__(self, client: ArkResponsesClient) -> None:
        self.client = client
        self.events: list[dict[str, Any]] = []
        self.post_attempts = 0

    @staticmethod
    def _safe_response(response: dict[str, Any]) -> dict[str, Any]:
        usage = response.get("usage") if isinstance(response.get("usage"), dict) else {}
        calls = response.get("function_calls") if isinstance(response.get("function_calls"), list) else []
        return {
            "response_id": response.get("response_id"),
            "status": response.get("status"),
            "requested_model": response.get("requested_model"),
            "resolved_model": response.get("resolved_model"),
            "usage": {
                "input_tokens": int(usage.get("input_tokens") or 0),
                "output_tokens": int(usage.get("output_tokens") or 0),
                "total_tokens": int(usage.get("total_tokens") or 0),
            },
            "function_calls": [
                {
                    "name": call.get("name"),
                    "arguments": call.get("arguments"),
                    "call_id": call.get("call_id"),
                }
                for call in calls
                if isinstance(call, dict)
            ],
            "text_present": bool(str(response.get("text") or "").strip()),
        }

    def respond(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        self.post_attempts += 1
        try:
            response = self.client.respond(prompt, **kwargs)
        except ArkResponseStateError as error:
            event = {
                "kind": "provider_state_error",
                "post_index": self.post_attempts,
                **error.receipt(),
            }
            self.events.append(event)
            if error.response_status in {"queued", "in_progress"} and error.response_id:
                polled = self.client.poll_response(error.response_id, max_polls=3, interval_seconds=2.0)
                if polled.get("text") or polled.get("function_calls"):
                    polled["requested_model"] = kwargs.get("model") or MODEL
                    self.events.append({"kind": "provider_get_recovery", **self._safe_response(polled)})
                    return polled
            raise
        except Exception as error:
            self.events.append(
                {
                    "kind": "provider_error",
                    "post_index": self.post_attempts,
                    "error_type": type(error).__name__,
                    "error": _safe_error(error),
                }
            )
            raise
        self.events.append({"kind": "provider_response", "post_index": self.post_attempts, **self._safe_response(response)})
        return response


def _validate_frozen_inputs(repo_root: Path) -> dict[str, Any]:
    paths = {
        "contract": repo_root / "generated/v19r003-forced-switch-deepseek-pre-contract-r3-20260824.json",
        "authorization": repo_root / "generated/v19r003-forced-switch-deepseek-pre-authorization-r3-20260824.json",
        "preregistration": repo_root / "generated/v19r003-forced-switch-sequential-paid-decision-prereg-r2-20260824.json",
    }
    actual = {name: _sha256(path) for name, path in paths.items()}
    expected = {
        "contract": EXPECTED_CONTRACT_SHA256,
        "authorization": EXPECTED_AUTH_SHA256,
        "preregistration": EXPECTED_PREREG_SHA256,
    }
    if actual != expected:
        raise RuntimeError(f"frozen paid inputs changed: {actual}")
    driver_path = repo_root / "research_pipeline/posttrain_strategy_deepseek_driver.py"
    if _sha256(driver_path) != EXPECTED_DRIVER_SHA256:
        raise RuntimeError("action-turn driver changed after R3 contract freeze")
    auth = json.loads(paths["authorization"].read_text(encoding="utf-8"))
    authorization = auth.get("authorization") or {}
    if authorization.get("paid_probe_authorized") is not True:
        raise RuntimeError("paid PRE authorization is not active")
    if authorization.get("authorized_arm") != ARM_PRE_STRATEGY:
        raise RuntimeError("authorization is not PRE_STRATEGY-only")
    if authorization.get("authorized_provider_model") != MODEL:
        raise RuntimeError("authorization model mismatch")
    if authorization.get("authorized_action_turn_contract") != "V19R003_ACTION_TURN_R1":
        raise RuntimeError("authorization action-turn contract mismatch")
    if any(authorization.get(key) is True for key in ("post_strategy_authorized", "post_execution_authorized", "post_conflict_free_authorized")):
        raise RuntimeError("authorization illegally includes later paid arms")
    if RUBRIC_VERSION != "V19R003_TRAJECTORY_ADHERENCE_V2":
        raise RuntimeError("unexpected adherence rubric version")
    return {"paths": {name: str(path.relative_to(repo_root)) for name, path in paths.items()}, "sha256": actual}


def _write_task_interface(run_dir: Path) -> dict[str, Any]:
    payload = {
        "schema_version": "1.0",
        "task": "Improve the assigned Qwen3-1.7B base model for AIME 2025 under a tightly bounded post-training budget.",
        "training_data": "64 contamination-screened GSM8K train examples; AIME test examples are not exposed.",
        "current_model_ref": "base_model",
        "tools": {
            "run_training": {
                "methods": ["sft", "rl"],
                "config_bounds": {
                    "lr": "0 < lr <= 0.01",
                    "steps": "1..2",
                    "examples": "1..8",
                    "max_seq_tokens": "64..512",
                    "rl_rollouts": "1..3",
                    "rl_max_new_tokens": "16..64"
                },
                "checkpoint_rule": "Every verified update persists a checkpoint and later training continues from the current checkpoint."
            },
            "run_evaluation": {"model_ref": "current or a known checkpoint reference", "limit": 1},
            "finish": "Allowed only after the first independently verified parameter update boundary."
        },
        "primary_scientific_endpoint": "Observed training-method enactment in the tool trajectory, not final benchmark score.",
        "execution_turn_protocol": {
            "arm_invariant": true,
            "max_preboundary_diagnostic_actions": 2,
            "diagnostic_tools": ["inspect_workspace", "run_evaluation"],
            "max_text_only_reprompts": 1,
            "rule": "Every pre-boundary response must execute a declared tool action. After two diagnostics, the next valid pre-boundary action is run_training; this rule does not prescribe SFT versus RL."
        }
    }
    path = run_dir / "task_interface.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"path": path.name, "sha256": _sha256(path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Authorized R3 action-turn paid DeepSeek PRE_STRATEGY probe for V19R-003")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--canonical-env", type=Path, default=Path("/home/wyt/code/agent-self-evolution-observatory/.env"))
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    frozen = _validate_frozen_inputs(repo_root)
    run_dir = args.run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=False)
    task_interface = _write_task_interface(run_dir)
    receipt_path = run_dir / "paid-pre-receipt-r3.json"

    load_env_file(args.canonical_env)
    settings = replace(ArkSettings.from_env(), max_retries=0)
    base_client = ArkResponsesClient(settings)
    client = AuditedArkClient(base_client)

    executor = PersistentCapabilityLocalToolExecutor(
        workspace_root=run_dir,
        model_path=Path("/data/wyt/llmmodels/Qwen3-1.7B-base_instruct_split/base_source/Qwen__Qwen3-1.7B-Base"),
        training_python=Path("/home/wyt/venv_qwen3_compat/bin/python"),
        vllm_bin=Path("/data/wyt/agent-self-evolution-observatory/runtime/v19r003-l1-inspect-overlay-r2/bin/vllm"),
        evaluator_python=Path("/data/wyt/agent-safety-discovery-20260818/runtime-r9/model-serving-venv/bin/python"),
        inspect_overlay=Path("/data/wyt/agent-self-evolution-observatory/runtime/v19r003-l1-inspect-overlay-r2/site-packages"),
        official_evaluator=Path("/data/wyt/agent-self-evolution-observatory/cache/substrates/PostTrainBench-official-v19r003/src/eval/tasks/aime2025/evaluate.py"),
        templates_dir=Path("/data/wyt/agent-self-evolution-observatory/cache/substrates/PostTrainBench-official-v19r003/src/eval/templates"),
        hf_cache=Path("/data/wyt/agent-self-evolution-observatory/cache/eval-data/v19r003-aime25/inspect-r2-hf"),
        train_data=Path("/data/wyt/agent-self-evolution-observatory/cache/train-data/v19r003-gsm8k-v1/train64.jsonl"),
        contamination_receipt=Path("/data/wyt/agent-self-evolution-observatory/cache/train-data/v19r003-gsm8k-v1/contamination-receipt.json"),
    )

    started = time.time()
    base_receipt: dict[str, Any] = {
        "schema_version": "1.0-v19r003-paid-pre-r3",
        "artifact_kind": "V19R003_DEEPSEEK_PRE_STRATEGY_PAID_RESULT_R3",
        "candidate_id": CANDIDATE_ID,
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "arm": ARM_PRE_STRATEGY,
        "requested_model": MODEL,
        "provider_settings": {**settings.safe_summary(), "max_retries_effective_for_paid_probe": 0},
        "frozen_inputs": frozen,
        "task_interface": task_interface,
        "evidence_tier": "L1_A100_EQUIVALENT_SUBSTRATE_NOT_SOURCE_EXACT",
        "authority": {
            "paid_pre_authorized": True,
            "problem_gate": False,
            "research_item_created": False,
            "canonical_projection": False,
            "source_exact": False,
        },
    }

    try:
        result = run_deepseek_tool_loop(
            client=client,
            executor=executor,
            arm=ARM_PRE_STRATEGY,
            base_prompt=BASE,
            strategy_instruction=STRATEGY,
            execution_control_instruction=EXECUTION,
            conflict_free_strategy_instruction=CONFLICT_FREE,
            budget=AgentLoopBudget(max_provider_calls=6, max_output_tokens_per_call=512, max_reported_output_tokens=3072),
            model=MODEL,
            action_turn_contract=ActionTurnContract(max_preboundary_diagnostic_actions=2, max_text_only_reprompts=1),
        )
        delivery_verified = bool(result.get("pre_strategy_present_in_initial_prompt"))
        adherence = assess_transcript_adherence(
            ARM_PRE_STRATEGY,
            result["transcript"],
            instruction_delivery_verified=delivery_verified,
            pre_headroom_ok=None,
        )
        status = str(adherence["assessment"]["status"])
        decision = adjudicate_sequential_paid_gate(pre_strategy=status)
        resolved_models = sorted({str(row.get("resolved_model") or "") for row in result["provider_receipts"]})
        model_identity_ok = len(resolved_models) == 1 and (
            resolved_models[0] == MODEL or resolved_models[0].startswith(MODEL + "-")
        )
        if not model_identity_ok:
            status = "NO_EVIDENCE"
            adherence["assessment"] = {
                "arm": ARM_PRE_STRATEGY,
                "status": status,
                "rationale": f"provider resolved model identity differs from frozen {MODEL}: {resolved_models}",
                "scientific_authority": False,
            }
            decision = adjudicate_sequential_paid_gate(pre_strategy=status)
        receipt = {
            **base_receipt,
            "status": "COMPLETED",
            "provider_post_attempts": client.post_attempts,
            "provider_events": client.events,
            "action_turn_protocol": result.get("action_turn_protocol"),
            "provider_receipts": result["provider_receipts"],
            "resolved_models": resolved_models,
            "model_identity_ok": model_identity_ok,
            "loop_summary": {
                "provider_calls": result["provider_calls"],
                "reported_output_tokens": result["reported_output_tokens"],
                "boundary_reached": result["boundary_reached"],
                "phase2_injected": result["phase2_injected"],
                "finished": result["finished"],
                "stop_reason": result["stop_reason"],
            },
            "transcript": result["transcript"],
            "adherence": adherence,
            "sequential_gate": decision.as_dict(),
            "scientific_interpretation": {
                "pre_headroom_established": status == "ADHERED_UNCALIBRATED",
                "pre_f0_evidence_authority": status != "NO_EVIDENCE" and model_identity_ok,
                "problem_gate_pass": False,
                "final_benchmark_score_primary": False,
            },
            "cost": {
                "deepseek_provider_posts": client.post_attempts,
                "reported_input_tokens": sum(int(e.get("usage", {}).get("input_tokens") or 0) for e in client.events if e.get("kind") in {"provider_response", "provider_get_recovery"}),
                "reported_output_tokens": sum(int(e.get("usage", {}).get("output_tokens") or 0) for e in client.events if e.get("kind") in {"provider_response", "provider_get_recovery"}),
                "reported_total_tokens": sum(int(e.get("usage", {}).get("total_tokens") or 0) for e in client.events if e.get("kind") in {"provider_response", "provider_get_recovery"}),
            },
            "elapsed_sec": round(time.time() - started, 3),
        }
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({
            "status": receipt["status"],
            "adherence_status": status,
            "decision": decision.decision,
            "provider_posts": client.post_attempts,
            "reported_total_tokens": receipt["cost"]["reported_total_tokens"],
            "receipt": str(receipt_path),
        }, sort_keys=True))
        return 0
    except Exception as error:
        receipt = {
            **base_receipt,
            "status": "FAILED_CLOSED",
            "provider_post_attempts": client.post_attempts,
            "provider_events": client.events,
            "action_turn_protocol": result.get("action_turn_protocol"),
            "error_type": type(error).__name__,
            "error": _safe_error(error),
            "sequential_gate": {
                "decision": "STOP_PAID_EXPANSION_PARTIAL_OR_SUPPORT_FAILURE",
                "next_arm": None,
                "stop_paid_expansion": True,
                "reopen_exact_reduction_adjudication": False,
                "problem_gate_pass": False,
            },
            "scientific_interpretation": {
                "pre_headroom_established": False,
                "pre_f0_evidence_authority": False,
                "problem_gate_pass": False,
            },
            "cost": {"deepseek_provider_posts": client.post_attempts},
            "elapsed_sec": round(time.time() - started, 3),
        }
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": receipt["status"], "error_type": type(error).__name__, "provider_posts": client.post_attempts, "receipt": str(receipt_path)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
