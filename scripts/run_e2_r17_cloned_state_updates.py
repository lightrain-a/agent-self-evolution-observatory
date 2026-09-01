#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import atomic_json, load_frozen_pool
from research_pipeline.e2_r17_mindmemos_ark_adapter import MindMemOSArkPlanChatAdapter, PLAN_BASE_URL
from research_pipeline.e2_r17_mindmemos_updater import run_projection_update
from research_pipeline.e2_r17_search_projection_runner import ProjectionName, project_stream

DEFAULT_ARMS = (
    ProjectionName.WINNER_ONLY,
    ProjectionName.PRECOMMITTED_ALWAYS,
    ProjectionName.REJECTED_WITNESS,
    ProjectionName.DUPLICATED_WINNER,
    ProjectionName.WINNER_RANDOM_NONWINNER,
    ProjectionName.SKILLCAT_STYLE_CONTRAST,
)
ARM_SALT = "E2-R17-F0-R4-CLONED-ARM-ORDER-v1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bind_mindmemos(root: Path) -> None:
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    for source in reversed(
        [root / "src/mindmemos_eval", root / "src/mindmemos_sdk", root / "src/mindmemos"]
    ):
        if str(source) not in sys.path:
            sys.path.insert(0, str(source))


def validate_authorization(path: Path, contract: Path, identity: Path) -> dict[str, Any]:
    auth = json.loads(path.read_text(encoding="utf-8"))
    if auth.get("status") != "AUTHORIZED_E1":
        raise RuntimeError("cloned-state updater requires AUTHORIZED_E1")
    if not auth.get("authority", {}).get("scientific_experiment"):
        raise RuntimeError("authorization has zero scientific authority")
    if auth.get("contract_sha256") != sha256(contract):
        raise RuntimeError("authorization/contract SHA mismatch")
    if auth.get("model_identity_sha256") != sha256(identity):
        raise RuntimeError("authorization/model-identity SHA mismatch")
    return auth


def ordered_arms(stream_id: str, arms: list[ProjectionName]) -> list[ProjectionName]:
    return sorted(
        arms,
        key=lambda arm: hashlib.sha256(f"{ARM_SALT}|{stream_id}|{arm.value}".encode("utf-8")).hexdigest(),
    )


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    bind_mindmemos(args.mindmemos_root)
    load_env_file(args.env_file)
    raw = ArkSettings.from_env(required=True)
    if raw.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("E2-R17 updater refuses any non-Ark-Plan route")
    settings = ArkSettings(
        api_key=raw.api_key,
        base_url=raw.base_url,
        default_model=raw.default_model,
        timeout_seconds=300,
        max_retries=0,
    )
    identity = json.loads(args.identity.read_text(encoding="utf-8"))
    if identity.get("status") != "PASS_CURRENT_REVIEW_TRANCHE":
        raise RuntimeError("current model identity adjudication is not passing")
    model_row = identity["requested_and_resolved"]["deepseek-v4-pro"]
    requested = str(model_row["requested"])
    resolved = str(model_row["resolved"])
    auth = validate_authorization(args.authorization, args.contract, args.identity)

    split = json.loads((args.suite_root / "r17_split_manifest.json").read_text(encoding="utf-8"))
    task_ids = split.get("e1_update_streams", {}).get(args.stream_id)
    if not task_ids:
        raise RuntimeError(f"unknown E1 stream: {args.stream_id}")
    pools = [load_frozen_pool(args.actor_pool_root / "cases" / task_id / f"pool_k{args.k}.json") for task_id in task_ids]
    if [pool.task_id for pool in pools] != [str(task_id) for task_id in task_ids]:
        raise RuntimeError("actor pool task order drifted from frozen stream manifest")
    initial_skill_path = args.mindmemos_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md"
    initial_skill_md = initial_skill_path.read_text(encoding="utf-8")
    initial_skill_sha = sha256(initial_skill_path)
    substrate_head = __import__("subprocess").check_output(
        ["git", "-C", str(args.mindmemos_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if substrate_head != auth.get("mindmemos_commit"):
        raise RuntimeError("MindMemOS commit drifted after authorization")

    requested_arms = [ProjectionName(value) for value in args.arm]
    arm_order = ordered_arms(args.stream_id, requested_arms)
    rows: list[dict[str, Any]] = []
    for arm in arm_order:
        stream = project_stream(
            stream_id=args.stream_id,
            initial_skill_sha256=initial_skill_sha,
            pools=pools,
            projection=arm,
        )
        arm_dir = args.run_root / args.stream_id / arm.value
        adapter = MindMemOSArkPlanChatAdapter(
            settings=settings,
            requested_model=requested,
            required_resolved_model=resolved,
            max_parse_attempts=args.max_parse_attempts,
            record_dir=arm_dir / "provider_calls",
        )
        result = await run_projection_update(
            stream=stream,
            pools=pools,
            initial_skill_md=initial_skill_md,
            run_dir=arm_dir,
            llm_adapter=adapter,
            mindmemos_commit=substrate_head,
            contract_sha256=sha256(args.contract),
            authorization_sha256=sha256(args.authorization),
            slot_char_budget=args.slot_char_budget,
            transcript_max_chars=args.transcript_max_chars,
        )
        rows.append(
            {
                "arm": arm.value,
                "stream_sha256": stream.stream_sha256,
                "update_receipt_path": result.update_receipt_path,
                "update_receipt_sha256": result.update_receipt_sha256,
                "skill_post_path": result.skill_post_path,
                "skill_post_sha256": result.skill_post_sha256,
                "evolved": result.evolved,
                "new_version_ids": list(result.new_version_ids),
                "provider_calls": result.provider_calls,
                "provider_total_tokens": result.provider_total_tokens,
            }
        )
    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-cloned-state-update-stream-summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "COMPLETED",
        "stream_id": args.stream_id,
        "task_ids": [str(item) for item in task_ids],
        "pool_ids": [pool.pool_id for pool in pools],
        "k": args.k,
        "arm_order_algorithm": f"SHA256({ARM_SALT}|stream_id|arm)",
        "arm_order": [arm.value for arm in arm_order],
        "random_nonwinner_salt": "e2-r17-r4-random-nonwinner-v1",
        "initial_skill_sha256": initial_skill_sha,
        "mindmemos_commit": substrate_head,
        "requested_model": requested,
        "resolved_model": resolved,
        "provider_retry_limit": 0,
        "max_parse_attempts": args.max_parse_attempts,
        "slot_char_budget": args.slot_char_budget,
        "transcript_max_chars": args.transcript_max_chars,
        "contract_path": str(args.contract),
        "contract_sha256": sha256(args.contract),
        "authorization_path": str(args.authorization),
        "authorization_sha256": sha256(args.authorization),
        "identity_path": str(args.identity),
        "identity_sha256": sha256(args.identity),
        "arms": rows,
        "scientific_outcome": True,
        "authority": {"paper_promotion": False, "submission": False},
        "private_credentials_included": False,
        "raw_response_ids_included": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--suite-root", type=Path, required=True)
    parser.add_argument("--mindmemos-root", type=Path, required=True)
    parser.add_argument("--actor-pool-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--stream-id", required=True)
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--arm", action="append", choices=[arm.value for arm in DEFAULT_ARMS])
    parser.add_argument("--max-parse-attempts", type=int, default=1)
    parser.add_argument("--slot-char-budget", type=int, default=6000)
    parser.add_argument("--transcript-max-chars", type=int, default=16000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.arm:
        args.arm = [arm.value for arm in DEFAULT_ARMS]
    summary = asyncio.run(main_async(args))
    atomic_json(args.output, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
