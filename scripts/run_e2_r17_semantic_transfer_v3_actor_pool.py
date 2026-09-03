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


def validate_authority(
    *,
    mode: str,
    authorization: Path | None,
    task_ids: list[str],
    split: dict[str, Any],
    k: int,
) -> tuple[dict[str, Any] | None, str | None]:
    development = {str(item) for item in split.get("development") or []}
    if mode == "protocol_smoke":
        if not set(task_ids).issubset(development):
            raise RuntimeError("protocol smoke may access development tasks only")
        if authorization is not None:
            raise RuntimeError("protocol smoke must not borrow scientific authorization")
        return None, None
    if authorization is None:
        raise RuntimeError("scientific actor execution requires --authorization")
    payload = json.loads(authorization.read_text(encoding="utf-8"))
    if payload.get("status") != "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A":
        raise RuntimeError("V3 Stage-A actor requires the exact V3 Stage-A authorization status")
    authority = payload.get("authority") or {}
    if authority.get("stage_a_provider_execution") is not True:
        raise RuntimeError("V3 Stage-A provider execution authority absent")
    for forbidden in (
        "stage_b_learning_execution",
        "updater",
        "heldout_evaluation",
        "analyzer",
        "second_backbone",
        "public_benchmark",
        "paper_promotion",
    ):
        if authority.get(forbidden) is not False:
            raise RuntimeError(f"V3 Stage-A authorization is overbroad or underspecified: {forbidden}")

    # New scoped authorizations fail closed. Historical artifacts without an
    # execution_scope remain readable/replayable, but any E1-A/E1-B tranche
    # minted after this guard must bind the exact mode, task IDs and K it grants.
    scope = payload.get("execution_scope")
    if scope is not None:
        allowed_modes = {str(value) for value in scope.get("allowed_modes") or []}
        if not allowed_modes or mode not in allowed_modes:
            raise RuntimeError(f"authorization does not allow mode={mode}")
        allowed_tasks = {str(value) for value in scope.get("allowed_task_ids") or []}
        if not allowed_tasks or not set(task_ids).issubset(allowed_tasks):
            raise RuntimeError("authorization does not allow one or more requested task IDs")
        exact_k = scope.get("exact_k")
        if exact_k is not None and int(exact_k) != int(k):
            raise RuntimeError(f"authorization requires exact K={exact_k}, requested K={k}")
        if scope.get("allow_noninitial_skill") is not False:
            raise RuntimeError("V3 Stage-A authorization must forbid non-initial skills")
    return payload, sha256(authorization)


def validate_stage_a_runner_context(
    *,
    authorization_payload: dict[str, Any] | None,
    authorization_sha: str | None,
    run_root: Path,
    prefix_ks: tuple[int, ...],
    concurrency: int,
) -> dict[str, Any] | None:
    if authorization_payload is None:
        return None
    if not authorization_sha:
        raise RuntimeError("scientific Stage-A invocation lacks authorization SHA")
    scope = authorization_payload.get("execution_scope") or {}
    required_run_root_raw = str(scope.get("required_run_root") or "")
    if not required_run_root_raw or run_root.resolve() != Path(required_run_root_raw).resolve():
        raise RuntimeError("V3 Stage-A actor run root is not the contract-bound first-run root")
    exact_prefix_ks = tuple(int(value) for value in scope.get("exact_prefix_ks") or [])
    if exact_prefix_ks != tuple(prefix_ks):
        raise RuntimeError(f"V3 Stage-A authorization requires prefix K={exact_prefix_ks}, requested {prefix_ks}")
    if int(scope.get("exact_concurrency") or 0) != int(concurrency):
        raise RuntimeError("V3 Stage-A actor concurrency drift")
    if scope.get("runner_lease_required") is not True:
        raise RuntimeError("V3 Stage-A authorization does not require the first-run runner lease")
    lease_path_raw = str(scope.get("global_lease_path") or "")
    if not lease_path_raw:
        raise RuntimeError("V3 Stage-A authorization lacks global lease path")
    lease_path = Path(lease_path_raw)
    if not lease_path.is_file():
        raise RuntimeError("V3 Stage-A actor requires the active first-run global lease")
    lease = json.loads(lease_path.read_text(encoding="utf-8"))
    if lease.get("status") != "RUNNING_STAGE_A_V3":
        raise RuntimeError("V3 Stage-A global lease is not in RUNNING state")
    if lease.get("contract_sha256") != authorization_payload.get("contract_sha256"):
        raise RuntimeError("V3 Stage-A global lease contract binding drift")
    if lease.get("authorization_sha256") != authorization_sha:
        raise RuntimeError("V3 Stage-A global lease authorization binding drift")
    lease_run_root = str(lease.get("run_root") or "")
    if not lease_run_root or Path(lease_run_root).resolve() != run_root.resolve():
        raise RuntimeError("V3 Stage-A global lease run-root binding drift")
    return lease


def validate_initial_skill_scope(
    *,
    authorization_payload: dict[str, Any] | None,
    skill_source: Path,
    default_skill_source: Path,
) -> None:
    if authorization_payload is None:
        return
    scope = authorization_payload.get("execution_scope") or {}
    if scope.get("allow_noninitial_skill") is False and skill_source.resolve() != default_skill_source.resolve():
        raise RuntimeError("V3 Stage-A authorization forbids any non-initial skill or updater receipt")


def _exclusive_json(path: Path, payload: dict[str, Any], *, replay_message: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError(replay_message) from exc
    try:
        view = memoryview(data)
        written = 0
        while written < len(data):
            written += os.write(fd, view[written:])
        os.fsync(fd)
    finally:
        os.close(fd)
    try:
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError:
        # The file itself is already fsynced. Some filesystems do not support
        # directory fsync; do not weaken O_EXCL replay protection for that.
        pass
    return path


def _scope_path(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def validate_exact_once_acquisition_scope(
    *,
    authorization_payload: dict[str, Any] | None,
    run_root: Path,
    requested_task_ids: list[str],
) -> dict[str, Any] | None:
    if authorization_payload is None:
        return None
    scope = authorization_payload.get("execution_scope") or {}
    policy = scope.get("exact_once_acquisition") or {}
    if policy.get("required") is not True:
        raise RuntimeError("V3 Stage-A authorization lacks actor-enforced exact-once acquisition")
    if policy.get("attempt_before_any_provider_io") is not True:
        raise RuntimeError("V3 Stage-A exact-once policy does not burn the task before provider I/O")
    if policy.get("replay_allowed") is not False or policy.get("ambiguous_recollection_allowed") is not False:
        raise RuntimeError("V3 Stage-A exact-once policy permits replay or ambiguous recollection")
    if int(policy.get("unit_count") or 0) != 160:
        raise RuntimeError("V3 Stage-A exact-once unit cardinality drift")

    manifest_raw = str(policy.get("unit_manifest_path") or "")
    manifest_sha = str(policy.get("unit_manifest_sha256") or "")
    if not manifest_raw or not manifest_sha:
        raise RuntimeError("V3 Stage-A exact-once unit manifest binding missing")
    manifest_path = _scope_path(manifest_raw)
    if not manifest_path.is_file() or sha256(manifest_path) != manifest_sha:
        raise RuntimeError("V3 Stage-A exact-once unit manifest drift")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_task_ids = [str(value) for value in manifest.get("ordered_task_ids") or []]
    if len(manifest_task_ids) != 160 or len(set(manifest_task_ids)) != 160:
        raise RuntimeError("V3 Stage-A exact-once unit manifest is not 160 unique task IDs")
    allowed_task_ids = [str(value) for value in scope.get("allowed_task_ids") or []]
    if set(manifest_task_ids) != set(allowed_task_ids):
        raise RuntimeError("V3 Stage-A exact-once unit manifest differs from authorization task universe")
    if not set(requested_task_ids).issubset(set(manifest_task_ids)):
        raise RuntimeError("requested task is absent from V3 exact-once acquisition universe")

    claim_root_raw = str(policy.get("required_claim_root") or "")
    if not claim_root_raw:
        raise RuntimeError("V3 Stage-A exact-once claim root missing")
    claim_root = Path(claim_root_raw)
    expected_claim_root = run_root / "checkpoints/stage_a_task_claims"
    if claim_root.resolve() != expected_claim_root.resolve():
        raise RuntimeError("V3 Stage-A exact-once claim root is not bound inside the contract run root")
    return {
        "claim_root": claim_root,
        "manifest_path": manifest_path,
        "manifest_sha256": manifest_sha,
        "unit_ids": tuple(manifest_task_ids),
    }


def task_claim_paths(claim_root: Path, task_id: str) -> tuple[Path, Path]:
    stem = hashlib.sha256(task_id.encode("utf-8")).hexdigest()
    return claim_root / f"{stem}.attempt.json", claim_root / f"{stem}.sealed.json"


def burn_task_attempt(
    *,
    exact_once_scope: dict[str, Any] | None,
    task_id: str,
    contract_sha256: str | None,
    authorization_sha256: str | None,
    k: int,
    prefix_ks: tuple[int, ...],
) -> Path | None:
    if exact_once_scope is None:
        return None
    claim_root = Path(exact_once_scope["claim_root"])
    attempt_path, sealed_path = task_claim_paths(claim_root, task_id)
    if sealed_path.exists():
        raise RuntimeError(f"V3 Stage-A task already sealed; replay forbidden before provider I/O: {task_id}")
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-task-attempt",
        "status": "ATTEMPTED_IN_FLIGHT_DO_NOT_REPLAY",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "task_id": task_id,
        "contract_sha256": contract_sha256,
        "authorization_sha256": authorization_sha256,
        "k": int(k),
        "prefix_ks": list(prefix_ks),
        "pid": os.getpid(),
        "provider_relaunch_authorized": False,
        "replacement_sampling_authorized": False,
        "ambiguous_recollection_authorized": False,
    }
    return _exclusive_json(
        attempt_path,
        payload,
        replay_message=f"V3 Stage-A task attempt already exists; replay forbidden before provider I/O: {task_id}",
    )


def seal_task_attempt(
    *,
    exact_once_scope: dict[str, Any] | None,
    task_id: str,
    attempt_path: Path | None,
    task_dir: Path,
    contract_sha256: str | None,
    authorization_sha256: str | None,
) -> Path | None:
    if exact_once_scope is None:
        return None
    if attempt_path is None or not attempt_path.is_file():
        raise RuntimeError(f"V3 Stage-A task cannot seal without immutable attempt marker: {task_id}")
    claim_root = Path(exact_once_scope["claim_root"])
    expected_attempt, sealed_path = task_claim_paths(claim_root, task_id)
    if attempt_path.resolve() != expected_attempt.resolve():
        raise RuntimeError(f"V3 Stage-A task attempt path drift: {task_id}")
    attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
    if attempt.get("status") != "ATTEMPTED_IN_FLIGHT_DO_NOT_REPLAY" or attempt.get("task_id") != task_id:
        raise RuntimeError(f"V3 Stage-A task attempt marker drift: {task_id}")
    if attempt.get("contract_sha256") != contract_sha256 or attempt.get("authorization_sha256") != authorization_sha256:
        raise RuntimeError(f"V3 Stage-A task attempt lineage drift: {task_id}")
    pool_k8 = task_dir / "pool_k8.json"
    if not pool_k8.is_file():
        raise RuntimeError(f"V3 Stage-A task cannot seal before frozen K8 pool exists: {task_id}")
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-task-seal",
        "status": "SEALED_EXACT_ONCE",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "task_id": task_id,
        "contract_sha256": contract_sha256,
        "authorization_sha256": authorization_sha256,
        "attempt_path": str(attempt_path),
        "attempt_sha256": sha256(attempt_path),
        "pool_k8_path": str(pool_k8),
        "pool_k8_sha256": sha256(pool_k8),
        "provider_relaunch_authorized": False,
        "replacement_sampling_authorized": False,
    }
    return _exclusive_json(
        sealed_path,
        payload,
        replay_message=f"V3 Stage-A task seal already exists; duplicate completion forbidden: {task_id}",
    )


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
    )
    contract_sha = (
        str(authorization_payload.get("contract_sha256") or "")
        if authorization_payload is not None
        else None
    )
    prefix_ks = tuple(int(value) for value in args.prefix_ks.split(",") if value.strip())
    validate_stage_a_runner_context(
        authorization_payload=authorization_payload,
        authorization_sha=authorization_sha,
        run_root=args.run_root,
        prefix_ks=prefix_ks,
        concurrency=args.concurrency,
    )
    exact_once_scope = validate_exact_once_acquisition_scope(
        authorization_payload=authorization_payload,
        run_root=args.run_root,
        requested_task_ids=task_ids,
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
            if int(provider_budget_scope.get("total_limit")) != int(args.provider_total_call_limit):
                raise RuntimeError("authorization provider total-call limit drift")
            if int(provider_budget_scope.get("per_unit_limit")) != int(args.provider_per_unit_call_limit):
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
        if scope.get("exact_concurrency") is not None and int(scope["exact_concurrency"]) != int(args.concurrency):
            raise RuntimeError("authorization concurrency drift")
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
    validate_initial_skill_scope(
        authorization_payload=authorization_payload,
        skill_source=skill_source,
        default_skill_source=default_skill_source,
    )
    if authorization_payload is not None and args.updater_receipt is not None:
        raise RuntimeError("V3 Stage-A authorization forbids updater receipts")
    skill_md = skill_source / "SKILL.md"
    if not skill_md.is_file():
        raise RuntimeError(f"skill source does not contain SKILL.md: {skill_source}")
    skill_sha = file_sha256(skill_md)
    if authorization_payload is not None:
        required_skill_sha = (authorization_payload.get("execution_scope") or {}).get("required_skill_pre_sha256")
        if required_skill_sha and skill_sha != required_skill_sha:
            raise RuntimeError("skill pre-state drifted after scientific authorization")
    updater_receipt_sha: str | None = None
    if skill_source != default_skill_source.resolve():
        if args.mode != "e1" or args.updater_receipt is None:
            raise RuntimeError("a non-initial skill is allowed only for E1 evaluation with --updater-receipt")
        updater_receipt = json.loads(args.updater_receipt.read_text(encoding="utf-8"))
        updater_receipt_sha = sha256(args.updater_receipt)
        if updater_receipt.get("status") != "COMPLETED":
            raise RuntimeError("updater receipt is not completed")
        if Path(updater_receipt.get("skill_post_path") or "").resolve() != skill_md.resolve():
            raise RuntimeError("updater receipt does not bind the supplied skill path")
        if updater_receipt.get("skill_post_sha256") != skill_sha:
            raise RuntimeError("updater receipt does not bind the supplied skill content")
        if updater_receipt.get("contract_sha256") != contract_sha:
            raise RuntimeError("updater receipt contract SHA differs from evaluation authorization")
        if updater_receipt.get("authorization_sha256") != authorization_sha:
            raise RuntimeError("updater receipt authorization SHA differs from evaluation authorization")
    elif args.updater_receipt is not None:
        raise RuntimeError("--updater-receipt must not be supplied for the frozen initial skill")
    evaluator_sources = [
        args.mindmemos_root / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/evaluator.py",
        args.mindmemos_root / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py",
    ]
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
                # V3 intentionally has no family label in the scientific suite.
                # A constant/hidden family code must not be reintroduced through
                # the actor path because it could later become a privileged router
                # input. Failure provenance is therefore unstratified at Stage A.
                failure_family=None,
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
    for task_id in task_ids:
        # Scientific Stage A irreversibly burns the task acquisition unit before
        # any provider coroutine is awaited. If execution becomes ambiguous
        # after this point, the marker remains and all replay/recollection fails
        # closed before external I/O.
        attempt_path = burn_task_attempt(
            exact_once_scope=exact_once_scope,
            task_id=task_id,
            contract_sha256=contract_sha,
            authorization_sha256=authorization_sha,
            k=args.k,
            prefix_ks=prefix_ks,
        )
        refs = await asyncio.gather(*(run_unit(task_id, index) for index in range(args.k)))
        task_dir = args.run_root / "cases" / task_id
        pools = freeze_nested_pools(task_dir=task_dir, trajectories=refs, prefix_ks=prefix_ks)
        sealed_path = seal_task_attempt(
            exact_once_scope=exact_once_scope,
            task_id=task_id,
            attempt_path=attempt_path,
            task_dir=task_dir,
            contract_sha256=contract_sha,
            authorization_sha256=authorization_sha,
        )
        task_rows.append(
            {
                "task_id": task_id,
                "failure_family": None,
                "exact_once_attempt_path": str(attempt_path) if attempt_path else None,
                "exact_once_attempt_sha256": sha256(attempt_path) if attempt_path else None,
                "exact_once_sealed_path": str(sealed_path) if sealed_path else None,
                "exact_once_sealed_sha256": sha256(sealed_path) if sealed_path else None,
                "scores": [ref.score for ref in refs],
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
        "exact_once_acquisition": (
            {
                "required": True,
                "unit_manifest_path": str(exact_once_scope["manifest_path"]),
                "unit_manifest_sha256": str(exact_once_scope["manifest_sha256"]),
                "claim_root": str(exact_once_scope["claim_root"]),
                "requested_units": len(task_rows),
                "attempted_units": sum(1 for row in task_rows if row.get("exact_once_attempt_path")),
                "sealed_units": sum(1 for row in task_rows if row.get("exact_once_sealed_path")),
                "replay_allowed": False,
                "ambiguous_recollection_allowed": False,
            }
            if exact_once_scope is not None
            else None
        ),
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
