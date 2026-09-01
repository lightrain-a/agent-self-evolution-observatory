#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import (
    ActorRolloutConfig,
    atomic_json,
    file_sha256,
    run_actor_rollout,
)
from research_pipeline.e2_r17_ark_plan_react import ArkPlanReactLLM, PLAN_BASE_URL
from research_pipeline.e2_r17_evaluator_qualification import (
    decide_evaluator_qualification,
)
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger

MODEL = "kimi-k3"
MINDMEMOS_COMMIT = "90491828726e1540442b17cd445d0308d0b8093c"
SUITE_MANIFEST_SHA256 = "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4"
SPLIT_MANIFEST_SHA256 = "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9"
QUALIFICATION_TASK_IDS = (
    "r17-b0-agj-p4",
    "r17-b0-fmv-p1",
    "r17-b0-ioc-p3",
    "r17-b0-msp-p3",
    "r17-b0-ska-p3",
    "r17-b0-tsr-p3",
)
REPEATS = 3
MAX_PROVIDER_CALLS_PER_ROLLOUT = 10
MAX_PROVIDER_CALLS_TOTAL = len(QUALIFICATION_TASK_IDS) * REPEATS * MAX_PROVIDER_CALLS_PER_ROLLOUT


def canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_mindmemos(root: Path) -> tuple[Any, Any]:
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    source_roots = [root / "src/mindmemos_eval", root / "src/mindmemos_sdk", root / "src/mindmemos"]
    for source in reversed(source_roots):
        if str(source) not in sys.path:
            sys.path.insert(0, str(source))
    from mindmemos_eval.skills.agents import ReactAgentFactory
    from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv

    return ReactAgentFactory, SpreadsheetBenchEnv


def identity_row(path: Path) -> tuple[dict[str, Any], str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "PASS":
        raise RuntimeError("fresh Kimi evaluator model identity is not passing")
    rows = [
        row for row in payload.get("models") or []
        if row.get("requested_model") == MODEL and row.get("status") == "PASS"
    ]
    if len(rows) != 1:
        raise RuntimeError("fresh identity must contain exactly one passing Kimi row")
    row = rows[0]
    if row.get("resolved_model") != MODEL:
        raise RuntimeError("Kimi evaluator resolved-model drift")
    if row.get("provider_retry_limit") != 0 or row.get("hidden_provider_retry_used"):
        raise RuntimeError("Kimi evaluator identity violates retry policy")
    if row.get("thinking_requested") != "disabled":
        raise RuntimeError("Kimi evaluator identity violates thinking policy")
    return row, file_sha256(path)


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    ReactAgentFactory, SpreadsheetBenchEnv = load_mindmemos(args.mindmemos_root)
    identity, identity_sha = identity_row(args.identity)
    load_env_file(args.env_file)
    raw_settings = ArkSettings.from_env(required=True)
    if raw_settings.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("Kimi evaluator qualification refuses non-Ark-Plan route")
    settings = ArkSettings(
        api_key=raw_settings.api_key,
        base_url=raw_settings.base_url,
        default_model=raw_settings.default_model,
        timeout_seconds=300.0,
        max_retries=0,
    )

    mind_head = subprocess.check_output(
        ["git", "-C", str(args.mindmemos_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if mind_head != MINDMEMOS_COMMIT:
        raise RuntimeError("MindMemOS qualification commit drift")
    if subprocess.check_output(
        ["git", "-C", str(args.mindmemos_root), "status", "--short"], text=True
    ).strip():
        raise RuntimeError("MindMemOS qualification tree is dirty")

    split_path = args.suite_root / "r17_split_manifest.json"
    if file_sha256(args.suite_root / "suite_manifest.json") != SUITE_MANIFEST_SHA256:
        raise RuntimeError("controlled suite manifest drift")
    if file_sha256(split_path) != SPLIT_MANIFEST_SHA256:
        raise RuntimeError("controlled split manifest drift")
    split = json.loads(split_path.read_text(encoding="utf-8"))
    if not set(QUALIFICATION_TASK_IDS).issubset(set(map(str, split["development"]))):
        raise RuntimeError("Kimi qualification escaped the development split")

    initial_skill = args.mindmemos_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx"
    skill_md = initial_skill / "SKILL.md"
    if not skill_md.is_file():
        raise RuntimeError("frozen initial SpreadsheetBench skill missing")
    skill_sha = file_sha256(skill_md)
    metadata_rows = json.loads(
        (args.suite_root / "r17_controlled_metadata.json").read_text(encoding="utf-8")
    )
    metadata = {str(row["id"]): row for row in metadata_rows}
    env = SpreadsheetBenchEnv(args.suite_root, args.run_root)
    cases = {case.id: case for case in env.load_cases("all")}
    evaluator_sources = [
        args.mindmemos_root / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/evaluator.py",
        args.mindmemos_root / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py",
    ]

    qualification_spec = {
        "artifact_type": "e2-r17-kimi-evaluator-development-qualification-spec",
        "model": MODEL,
        "resolved_model": identity["resolved_model"],
        "identity_sha256": identity_sha,
        "task_ids": list(QUALIFICATION_TASK_IDS),
        "repeats": REPEATS,
        "max_turns": args.max_turns,
        "max_output_tokens": args.max_output_tokens,
        "temperature": 0,
        "thinking": "disabled",
        "provider_retry_limit": 0,
        "suite_manifest_sha256": SUITE_MANIFEST_SHA256,
        "split_manifest_sha256": SPLIT_MANIFEST_SHA256,
        "mindmemos_commit": mind_head,
        "initial_skill_sha256": skill_sha,
        "decision_rule": {
            "required_successful_tasks": 2,
            "required_exactly_stable_tasks": 5,
            "pooled_successes_strictly_between_zero_and_eighteen": True,
            "all_provider_calls_completed": True,
        },
    }
    qualification_spec_sha = canonical_sha(qualification_spec)
    ledger_path = args.run_root / "provider_budget.sqlite3"
    ledger = ProviderBudgetLedger(
        path=ledger_path,
        contract_sha256=qualification_spec_sha,
        authorization_sha256=identity_sha,
        total_limit=MAX_PROVIDER_CALLS_TOTAL,
        per_unit_limit=MAX_PROVIDER_CALLS_PER_ROLLOUT,
        allow_create=not ledger_path.exists(),
    )

    task_rows: list[dict[str, Any]] = []
    all_provider_statuses: list[str] = []
    scores_by_task: dict[str, list[float]] = {}
    for task_id in QUALIFICATION_TASK_IDS:
        scores: list[float] = []
        repeats: list[dict[str, Any]] = []
        for repeat in range(REPEATS):
            adapter = ArkPlanReactLLM(
                settings=settings,
                requested_model=MODEL,
                required_resolved_model=MODEL,
                max_output_tokens=args.max_output_tokens,
                temperature=0,
                thinking="disabled",
                provider_budget_ledger=ledger,
                provider_budget_unit_id=f"{task_id}/repeat_{repeat}",
            )
            factory = ReactAgentFactory(
                adapter,
                max_turns=args.max_turns,
                skill_sources=[initial_skill],
                python_path=sys.executable,
            )
            config = ActorRolloutConfig(
                requested_model=MODEL,
                required_resolved_model=MODEL,
                max_turns=args.max_turns,
                skill_source=str(initial_skill),
                skill_pre_sha256=skill_sha,
                failure_family=str(metadata[task_id]["primary_failure_family"]),
                experiment_mode="hosted_evaluator_development_qualification",
            )
            ref = await run_actor_rollout(
                env=env,
                case=cases[task_id],
                rollout_index=repeat,
                agent_factory=factory,
                adapter=adapter,
                config=config,
                evaluator_sources=evaluator_sources,
            )
            trajectory = json.loads(Path(ref.trajectory_path).read_text(encoding="utf-8"))
            receipts = list(trajectory.get("adapter_receipts") or [])
            statuses = [str(row.get("provider_status") or "") for row in receipts]
            all_provider_statuses.extend(statuses)
            scores.append(float(ref.score))
            ref_path = (
                args.run_root / "cases" / task_id / f"rollout_{repeat}" / "r17_trajectory_ref.json"
            )
            repeats.append(
                {
                    "repeat": repeat,
                    "score": float(ref.score),
                    "provider_calls": len(receipts),
                    "provider_statuses": statuses,
                    "trajectory_ref_path": str(ref_path),
                    "trajectory_ref_sha256": file_sha256(ref_path),
                    "trajectory_sha256": ref.trajectory_sha256,
                }
            )
        scores_by_task[task_id] = scores
        task_rows.append(
            {
                "task_id": task_id,
                "failure_family": metadata[task_id]["primary_failure_family"],
                "scores": scores,
                "exactly_stable": len(set(scores)) == 1,
                "repeats": repeats,
            }
        )

    decision = decide_evaluator_qualification(
        scores_by_task=scores_by_task,
        provider_statuses=all_provider_statuses,
    )
    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-kimi-evaluator-development-qualification",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": decision.status,
        "scientific_outcome": False,
        "central_mechanism_adjudicated": False,
        "historical_hold_reinterpreted": False,
        "selection_rule": (
            "Before outcomes, use the first lexicographic development task from each "
            "of the six controlled task families and exactly three task-major repeats."
        ),
        "qualification_spec": qualification_spec,
        "qualification_spec_sha256": qualification_spec_sha,
        "decision": decision.to_dict(),
        "tasks": task_rows,
        "provider_budget": ledger.snapshot().to_dict(),
        "identity": {
            "path": str(args.identity),
            "sha256": identity_sha,
            "requested_model": MODEL,
            "resolved_model": identity["resolved_model"],
        },
        "runtime": {
            "python_executable": sys.executable,
            "python_version": platform.python_version(),
            "mindmemos_root": str(args.mindmemos_root),
            "mindmemos_commit": mind_head,
            "bound_code": {
                "qualification_runner": {
                    "path": str(Path(__file__).resolve()),
                    "sha256": file_sha256(Path(__file__).resolve()),
                },
                "qualification_decision": {
                    "path": str((ROOT / "research_pipeline/e2_r17_evaluator_qualification.py").resolve()),
                    "sha256": file_sha256(
                        ROOT / "research_pipeline/e2_r17_evaluator_qualification.py"
                    ),
                },
                "actor_adapter": {
                    "path": str((ROOT / "research_pipeline/e2_r17_ark_plan_react.py").resolve()),
                    "sha256": file_sha256(ROOT / "research_pipeline/e2_r17_ark_plan_react.py"),
                },
                "actor_rollout": {
                    "path": str((ROOT / "research_pipeline/e2_r17_actor_pool.py").resolve()),
                    "sha256": file_sha256(ROOT / "research_pipeline/e2_r17_actor_pool.py"),
                },
            },
        },
        "authority": {
            "freeze_kimi_negative_control_protocol": decision.status.startswith("PASS_"),
            "execute_scientific_negative_control": False,
            "execute_mrw": False,
            "paper_promotion": False,
        },
        "private_credentials_included": False,
        "raw_response_ids_included": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--suite-root", type=Path, required=True)
    parser.add_argument("--mindmemos-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--max-turns", type=int, default=10)
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        summary = asyncio.run(main_async(args))
    except Exception as exc:  # noqa: BLE001 - qualification failures must survive
        summary = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-kimi-evaluator-development-qualification",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "FAIL_HOSTED_EVALUATOR_DEVELOPMENT_QUALIFICATION",
            "technical_error": f"{type(exc).__name__}: {exc}"[:2000],
            "scientific_outcome": False,
            "central_mechanism_adjudicated": False,
            "historical_hold_reinterpreted": False,
            "authority": {
                "freeze_kimi_negative_control_protocol": False,
                "execute_scientific_negative_control": False,
                "execute_mrw": False,
                "paper_promotion": False,
            },
        }
    atomic_json(args.output, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["status"].startswith("PASS_") else 3


if __name__ == "__main__":
    raise SystemExit(main())
