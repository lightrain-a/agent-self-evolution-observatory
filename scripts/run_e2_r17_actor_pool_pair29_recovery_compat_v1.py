#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import platform
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
    freeze_nested_pools,
    run_actor_rollout,
)
from research_pipeline.e2_r17_ark_plan_react import ArkPlanReactLLM, PLAN_BASE_URL
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger


def load_mindmemos(root: Path) -> tuple[Any, Any]:
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    source_roots = [root / "src/mindmemos_eval", root / "src/mindmemos_sdk", root / "src/mindmemos"]
    for source in reversed(source_roots):
        if str(source) not in sys.path:
            sys.path.insert(0, str(source))
    from mindmemos_eval.skills.agents import ReactAgentFactory
    from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv

    return ReactAgentFactory, SpreadsheetBenchEnv


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def task_ids_from_args(args: argparse.Namespace, split: dict[str, Any]) -> list[str]:
    if args.task_id:
        return [str(value) for value in args.task_id]
    if args.stream_id:
        for key in ("e1_update_streams", "e3_future_streams"):
            if args.stream_id in split.get(key, {}):
                return [str(value) for value in split[key][args.stream_id]]
        raise ValueError(f"unknown stream id: {args.stream_id}")
    if args.lane:
        value = split.get(args.lane)
        if not isinstance(value, list):
            raise ValueError(f"lane is not a task list: {args.lane}")
        return [str(item) for item in value]
    raise ValueError("one of --task-id, --stream-id, or --lane is required")


PAIR29_PREFLIGHT_STATUS = "PREFLIGHT_ONLY_E2_R17_DEEPSEEK_V2_REPAIR2_PAIR29_RECOVERY_M1"
PAIR29_AUTHORIZED_STATUS = "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_PAIR29_RECOVERY_M1_MEASUREMENT_ONLY"


def validate_authority(
    *,
    mode: str,
    authorization: Path | None,
    task_ids: list[str],
    split: dict[str, Any],
    k: int,
    stop_before_provider_io: bool,
) -> tuple[dict[str, Any], str]:
    if mode != "e1":
        raise RuntimeError("M1 compatibility actor permits exact mode=e1 only")
    if authorization is None:
        raise RuntimeError("M1 compatibility actor requires --authorization")
    payload = json.loads(authorization.read_text(encoding="utf-8"))
    contract_path = Path(str(payload.get("contract_path") or ""))
    if not contract_path.is_file() or sha256(contract_path) != payload.get("contract_sha256"):
        raise RuntimeError("M1 authorization/contract binding drift")
    status = payload.get("status")
    if status not in {PAIR29_PREFLIGHT_STATUS, PAIR29_AUTHORIZED_STATUS}:
        raise RuntimeError("authorization artifact is not a pair29 measurement-only recovery authorization")
    if status == PAIR29_PREFLIGHT_STATUS and not stop_before_provider_io:
        raise RuntimeError("preflight-only pair29 authorization cannot reach provider I/O")

    authority = payload.get("authority") or {}
    if authority.get("measurement_only") is not True:
        raise RuntimeError("M1 measurement-only authority bit absent")
    if authority.get("updater") is not False:
        raise RuntimeError("M1 updater authority must be false")
    if authority.get("analyzer") is not False:
        raise RuntimeError("M1 analyzer authority must be false")
    if status == PAIR29_AUTHORIZED_STATUS and authority.get("scientific_experiment") is not True:
        raise RuntimeError("authorized pair29 measurement authority absent")
    if status == PAIR29_PREFLIGHT_STATUS and authority.get("scientific_experiment") is not False:
        raise RuntimeError("pair29 preflight must have zero scientific authority")

    scope = payload.get("execution_scope") or {}
    if scope.get("measurement_child") != "E2-R17-DEEPSEEK-V2-REPAIR2-PAIR29-RECOVERY-M1":
        raise RuntimeError("pair29 measurement child identity drift")
    if scope.get("allowed_modes") != ["e1"]:
        raise RuntimeError("M1 authorization must bind exact mode=e1")
    allowed_measurements = scope.get("allowed_measurements") or []
    allowed_tasks = [str(row.get("task_id")) for row in allowed_measurements]
    if len(allowed_measurements) != 7 or len(task_ids) != 1 or task_ids[0] not in allowed_tasks:
        raise RuntimeError("pair29 actor invocation must select exactly one task from its frozen seven-unit recovery set")
    if int(scope.get("exact_k", -1)) != int(k) or int(k) != 1:
        raise RuntimeError("M1 authorization requires exact K=1")
    if scope.get("allow_noninitial_skill") is not True:
        raise RuntimeError("M1 must authorize only its exact frozen non-initial skills")
    learned_states = scope.get("learned_states") or []
    if len(learned_states) != 2 or {str(row.get("arm")) for row in learned_states} != {"win_c", "mrw"}:
        raise RuntimeError("pair29 authorization must bind exactly two learned states")
    return payload, sha256(authorization)


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    ReactAgentFactory, SpreadsheetBenchEnv = load_mindmemos(args.mindmemos_root)
    load_env_file(args.env_file)
    settings = ArkSettings.from_env(required=True)
    if settings.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("E2-R17 actor refuses any non-Ark-Plan route")
    settings = ArkSettings(
        api_key=settings.api_key,
        base_url=settings.base_url,
        default_model=settings.default_model,
        timeout_seconds=300,
        max_retries=0,
    )
    identity = json.loads(args.identity.read_text(encoding="utf-8"))
    if identity.get("status") != "PASS_CURRENT_REVIEW_TRANCHE":
        raise RuntimeError("current model identity adjudication is not passing")
    model_row = identity["requested_and_resolved"][args.model]
    requested_model = str(model_row["requested"])
    required_resolved = str(model_row["resolved"])

    split_path = args.suite_root / "r17_split_manifest.json"
    split = json.loads(split_path.read_text(encoding="utf-8"))
    task_ids = task_ids_from_args(args, split)
    authorization_payload, authorization_sha = validate_authority(
        mode=args.mode,
        authorization=args.authorization,
        task_ids=task_ids,
        split=split,
        k=args.k,
        stop_before_provider_io=args.stop_before_provider_io,
    )
    contract_sha = (
        str(authorization_payload.get("contract_sha256") or "")
        if authorization_payload is not None
        else None
    )
    provider_budget_ledger: ProviderBudgetLedger | None = None
    budget_args_present = any(
        value is not None
        for value in (args.provider_budget_ledger, args.provider_total_call_limit, args.provider_per_unit_call_limit)
    )
    if budget_args_present:
        if authorization_payload is None or not authorization_sha or not contract_sha:
            raise RuntimeError("provider budget ledger is allowed only for a bound scientific authorization")
        if args.provider_budget_ledger is None or args.provider_total_call_limit is None or args.provider_per_unit_call_limit is None:
            raise RuntimeError("provider budget ledger path, total limit and per-unit limit must be supplied together")
        provider_budget_ledger = ProviderBudgetLedger(
            path=args.provider_budget_ledger,
            contract_sha256=contract_sha,
            authorization_sha256=authorization_sha,
            total_limit=int(args.provider_total_call_limit),
            per_unit_limit=int(args.provider_per_unit_call_limit),
            allow_create=not args.provider_budget_ledger.exists(),
        )
    if authorization_payload is not None:
        scope = authorization_payload.get("execution_scope") or {}
        provider_budget_scope = scope.get("provider_budget") or {}
        if provider_budget_scope.get("required") is True:
            if provider_budget_ledger is None:
                raise RuntimeError("authorization requires a fail-closed provider budget ledger")
            allowed_totals = [int(value) for value in provider_budget_scope.get("allowed_total_limits") or []]
            if int(args.provider_total_call_limit) not in allowed_totals or sorted(allowed_totals) != [74, 98]:
                raise RuntimeError("authorization provider total-call limit drift")
            if int(provider_budget_scope.get("per_unit_limit")) != int(args.provider_per_unit_call_limit) or int(args.provider_per_unit_call_limit) != 11:
                raise RuntimeError("authorization provider per-unit limit drift")
        expected_resolved = scope.get("required_resolved_model")
        if expected_resolved and str(expected_resolved) != required_resolved:
            raise RuntimeError("authorization resolved-model identity drift")
        expected_identity_sha = scope.get("identity_artifact_sha256")
        if expected_identity_sha and sha256(args.identity) != expected_identity_sha:
            raise RuntimeError("authorization model-identity artifact drift")
        if scope.get("max_turns") is not None and int(scope["max_turns"]) != int(args.max_turns):
            raise RuntimeError("authorization max_turns drift")
        if scope.get("max_output_tokens") is not None and int(scope["max_output_tokens"]) != int(args.max_output_tokens):
            raise RuntimeError("authorization max_output_tokens drift")
    metadata_rows = json.loads((args.suite_root / "r17_controlled_metadata.json").read_text(encoding="utf-8"))
    metadata = {str(row["id"]): row for row in metadata_rows}
    missing = [task_id for task_id in task_ids if task_id not in metadata]
    if missing:
        raise RuntimeError(f"tasks absent from controlled metadata: {missing}")

    env = SpreadsheetBenchEnv(args.suite_root, args.run_root)
    cases = {case.id: case for case in env.load_cases("all")}
    mindmemos_commit = __import__("subprocess").check_output(
        ["git", "-C", str(args.mindmemos_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if authorization_payload is not None and mindmemos_commit != authorization_payload.get("mindmemos_commit"):
        raise RuntimeError("MindMemOS commit drifted after scientific authorization")
    if authorization_payload is not None:
        scope = authorization_payload.get("execution_scope") or {}
        expected_suite_sha = scope.get("suite_manifest_sha256")
        expected_split_sha = scope.get("split_manifest_sha256")
        if expected_suite_sha and file_sha256(args.suite_root / "suite_manifest.json") != expected_suite_sha:
            raise RuntimeError("suite manifest drifted after scientific authorization")
        if expected_split_sha and file_sha256(split_path) != expected_split_sha:
            raise RuntimeError("split manifest drifted after scientific authorization")

    default_skill_source = args.mindmemos_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx"
    skill_source = (args.skill_source or default_skill_source).resolve()
    skill_md = skill_source / "SKILL.md"
    if not skill_md.is_file():
        raise RuntimeError(f"skill source does not contain SKILL.md: {skill_source}")
    skill_sha = file_sha256(skill_md)
    if authorization_payload is not None:
        required_skill_sha = (authorization_payload.get("execution_scope") or {}).get("required_skill_pre_sha256")
        if required_skill_sha and skill_sha != required_skill_sha:
            raise RuntimeError("skill pre-state drifted after scientific authorization")
    updater_receipt_sha: str | None = None
    if skill_source == default_skill_source.resolve() or args.updater_receipt is None:
        raise RuntimeError("M1 accepts only one of its exact frozen parent learned states with --updater-receipt")
    updater_receipt = json.loads(args.updater_receipt.read_text(encoding="utf-8"))
    updater_receipt_sha = sha256(args.updater_receipt)
    scope = authorization_payload.get("execution_scope") or {}
    matching_states = [
        row
        for row in scope.get("learned_states") or []
        if Path(str(row.get("skill_post_path") or "")).resolve() == skill_md.resolve()
    ]
    if len(matching_states) != 1:
        raise RuntimeError("supplied learned-skill path is not uniquely authorized by pair29 recovery")
    learned_state = matching_states[0]
    arm = str(learned_state.get("arm"))
    allowed_matches = [row for row in scope.get("allowed_measurements") or [] if str(row.get("arm")) == arm and str(row.get("task_id")) == task_ids[0]]
    if len(allowed_matches) != 1:
        raise RuntimeError("arm/task combination is not uniquely authorized for pair29 recovery")
    if int(learned_state.get("child_provider_total_limit", -1)) != int(args.provider_total_call_limit):
        raise RuntimeError("pair29 learned-state residual provider budget drift")
    if learned_state.get("skill_post_sha256") != skill_sha:
        raise RuntimeError("M1 learned-state SHA drift")
    if Path(str(learned_state.get("update_receipt_path") or "")).resolve() != args.updater_receipt.resolve():
        raise RuntimeError("M1 parent updater-receipt path drift")
    if learned_state.get("update_receipt_sha256") != updater_receipt_sha:
        raise RuntimeError("M1 parent updater-receipt SHA drift")
    if updater_receipt.get("status") != "COMPLETED":
        raise RuntimeError("parent updater receipt is not completed")
    if Path(updater_receipt.get("skill_post_path") or "").resolve() != skill_md.resolve():
        raise RuntimeError("parent updater receipt does not bind the supplied skill path")
    if updater_receipt.get("skill_post_sha256") != skill_sha:
        raise RuntimeError("parent updater receipt does not bind the supplied skill content")

    parent = authorization_payload.get("parent_v3_provenance") or {}
    parent_contract_path = Path(str(parent.get("contract_path") or ""))
    parent_authorization_path = Path(str(parent.get("authorization_path") or ""))
    if not parent_contract_path.is_file() or sha256(parent_contract_path) != parent.get("contract_sha256"):
        raise RuntimeError("parent Repair2 contract provenance drift")
    if not parent_authorization_path.is_file() or sha256(parent_authorization_path) != parent.get("authorization_sha256"):
        raise RuntimeError("parent Repair2 authorization provenance drift")
    if updater_receipt.get("contract_sha256") != parent.get("contract_sha256"):
        raise RuntimeError("parent updater receipt contract provenance drift")
    if updater_receipt.get("authorization_sha256") != parent.get("authorization_sha256"):
        raise RuntimeError("parent updater receipt authorization provenance drift")
    evaluator_sources = [
        args.mindmemos_root / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/evaluator.py",
        args.mindmemos_root / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py",
    ]
    if args.stop_before_provider_io:
        snapshot = provider_budget_ledger.snapshot() if provider_budget_ledger is not None else None
        if snapshot is None or snapshot.total_claimed != 0:
            raise RuntimeError("M1 pre-provider stop requires a bound zero-claim provider ledger")
        return {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-repair2-pair29-recovery-actual-actor-authorization-path-preflight-unit",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "STOPPED_IMMEDIATELY_BEFORE_PROVIDER_IO",
            "mode": args.mode,
            "task_id": task_ids[0],
            "k": args.k,
            "requested_model": requested_model,
            "resolved_model": required_resolved,
            "skill_source": str(skill_source),
            "skill_pre_sha256": skill_sha,
            "updater_receipt_path": str(args.updater_receipt),
            "updater_receipt_sha256": updater_receipt_sha,
            "parent_contract_sha256": updater_receipt.get("contract_sha256"),
            "parent_authorization_sha256": updater_receipt.get("authorization_sha256"),
            "measurement_contract_sha256": contract_sha,
            "measurement_authorization_sha256": authorization_sha,
            "provider_claims": 0,
            "provider_calls": 0,
            "provider_budget": snapshot.to_dict(),
            "scientific_outcome": False,
        }
    semaphore = asyncio.Semaphore(max(1, args.concurrency))

    async def run_unit(task_id: str, rollout_index: int):
        async with semaphore:
            adapter = ArkPlanReactLLM(
                settings=settings,
                requested_model=requested_model,
                required_resolved_model=required_resolved,
                max_output_tokens=args.max_output_tokens,
                temperature=0,
                thinking="disabled",
                provider_budget_ledger=provider_budget_ledger,
                provider_budget_unit_id=(f"{task_id}/rollout_{rollout_index}" if provider_budget_ledger is not None else None),
            )
            factory = ReactAgentFactory(
                adapter,
                max_turns=args.max_turns,
                skill_sources=[skill_source],
                python_path=sys.executable,
            )
            config = ActorRolloutConfig(
                requested_model=requested_model,
                required_resolved_model=required_resolved,
                max_turns=args.max_turns,
                skill_source=str(skill_source),
                skill_pre_sha256=skill_sha,
                failure_family=str(metadata[task_id]["primary_failure_family"]),
                experiment_mode=args.mode,
                contract_sha256=contract_sha,
                authorization_sha256=authorization_sha,
            )
            return await run_actor_rollout(
                env=env,
                case=cases[task_id],
                rollout_index=rollout_index,
                agent_factory=factory,
                adapter=adapter,
                config=config,
                evaluator_sources=evaluator_sources,
            )

    task_rows: list[dict[str, Any]] = []
    prefix_ks = tuple(int(value) for value in args.prefix_ks.split(",") if value.strip())
    for task_id in task_ids:
        refs = await asyncio.gather(*(run_unit(task_id, index) for index in range(args.k)))
        task_dir = args.run_root / "cases" / task_id
        pools = freeze_nested_pools(task_dir=task_dir, trajectories=refs, prefix_ks=prefix_ks)
        task_rows.append(
            {
                "task_id": task_id,
                "failure_family": metadata[task_id]["primary_failure_family"],
                "scores_withheld_from_measurement_summary": True,
                "provider_calls": sum(
                    len(json.loads(Path(ref.trajectory_path).read_text(encoding="utf-8"))["adapter_receipts"])
                    for ref in refs
                ),
                "pools": {
                    str(k): {
                        "pool_id": pool.pool_id,
                        "acting_success": pool.acting_success,
                        "precommitted_success": pool.precommitted_success,
                        "rescue_event": pool.rescue_event,
                        "winner_index": pool.winner.rollout_index,
                    }
                    for k, pool in pools.items()
                },
            }
        )
    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-actor-pool-run-summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "COMPLETED",
        "mode": args.mode,
        "suite_root": str(args.suite_root),
        "suite_manifest_sha256": file_sha256(args.suite_root / "suite_manifest.json"),
        "split_manifest_sha256": file_sha256(split_path),
        "mindmemos_root": str(args.mindmemos_root),
        "mindmemos_commit": mindmemos_commit,
        "identity_artifact": str(args.identity),
        "identity_artifact_sha256": sha256(args.identity),
        "requested_model": requested_model,
        "resolved_model": required_resolved,
        "provider_retry_limit": 0,
        "thinking": "disabled",
        "k": args.k,
        "prefix_ks": list(prefix_ks),
        "max_turns": args.max_turns,
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "skill_source": str(skill_source),
        "skill_pre_sha256": skill_sha,
        "updater_receipt_path": str(args.updater_receipt) if args.updater_receipt else None,
        "updater_receipt_sha256": updater_receipt_sha,
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "provider_budget": provider_budget_ledger.snapshot().to_dict() if provider_budget_ledger is not None else None,
        "tasks": task_rows,
        "scientific_outcome": args.mode != "protocol_smoke",
        "authority": {
            "paper_promotion": False,
            "submission": False,
        },
        "private_credentials_included": False,
        "raw_response_ids_included": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--suite-root", type=Path, required=True)
    parser.add_argument("--mindmemos-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--skill-source", type=Path)
    parser.add_argument("--updater-receipt", type=Path)
    parser.add_argument("--mode", choices=("protocol_smoke", "e0", "e1", "public_externality"), required=True)
    parser.add_argument("--model", choices=("deepseek-v4-pro",), default="deepseek-v4-pro")
    parser.add_argument("--task-id", action="append")
    parser.add_argument("--lane")
    parser.add_argument("--stream-id")
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--prefix-ks", default="1,2,4,8")
    parser.add_argument("--max-turns", type=int, default=10)
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--provider-budget-ledger", type=Path)
    parser.add_argument("--provider-total-call-limit", type=int)
    parser.add_argument("--provider-per-unit-call-limit", type=int)
    parser.add_argument("--stop-before-provider-io", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.k < 1 or args.k > 8:
        raise SystemExit("K must be in 1..8")
    summary = asyncio.run(main_async(args))
    atomic_json(args.output, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
