#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def choose_four(stream_id: str, mixed_task_ids: list[str]) -> list[str]:
    require(len(mixed_task_ids) >= 4, f"stream has insufficient mixed pools: {stream_id}")
    return sorted(
        mixed_task_ids,
        key=lambda task_id: hashlib.sha256(
            f"semantic-transfer-mrw4-v2|{stream_id}|{task_id}".encode("utf-8")
        ).hexdigest(),
    )[:4]


def choose_nine_streams(stream_ids: list[str], scores: dict[str, int], *, descending: bool, salt: str) -> list[str]:
    require(len(stream_ids) == 18 and set(stream_ids) == set(scores), "reduction-router stream universe drift")
    def key(stream_id: str) -> tuple[int, str]:
        score = int(scores[stream_id])
        primary = -score if descending else score
        tie = hashlib.sha256(f"{salt}|{stream_id}".encode("utf-8")).hexdigest()
        return primary, tie
    return sorted(stream_ids, key=key)[:9]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    require(not args.output.exists(), "Stage-A support adjudication already exists")
    contract = load_json(args.contract)
    auth = load_json(args.authorization)
    summary = load_json(args.summary)
    contract_sha = sha_file(args.contract)
    auth_sha = sha_file(args.authorization)

    require(contract.get("status") == "FROZEN_SEMANTIC_TRANSFER_V2_STAGE_A_V4", "Stage-A V4 contract status invalid")
    require(auth.get("status") == "AUTHORIZED_SEMANTIC_TRANSFER_V2_STAGE_A_V4", "Stage-A V4 authorization status invalid")
    require(auth.get("contract_sha256") == contract_sha, "authorization contract binding drift")
    require(summary.get("status") == "COMPLETED_ALL_144_POOLS_PENDING_EQUAL_DOSE_ADJUDICATION", "Stage-A pool freeze incomplete")
    require(summary.get("contract_sha256") == contract_sha, "Stage-A summary contract drift")
    require(summary.get("authorization_sha256") == auth_sha, "Stage-A summary authorization drift")
    require(int(summary.get("streams") or 0) == 18, "Stage-A stream cardinality drift")
    require(int(summary.get("tasks") or 0) == 144, "Stage-A task cardinality drift")
    require(int(summary.get("actor_rollouts") or 0) == 1152, "Stage-A rollout cardinality drift")
    require(summary.get("updater_calls") == 0, "Stage-A must have zero updater calls")
    require(summary.get("heldout_evaluations") == 0, "Stage-A must have zero heldout evaluations")
    require(summary.get("partial_effect_read") is False, "Stage-A crossed effect boundary")

    suite_root = Path(contract["suite"]["root"])
    split_path = suite_root / "r17_split_manifest.json"
    split = load_json(split_path)
    streams = {str(k): [str(x) for x in v] for k, v in split["e1_update_streams"].items()}
    require(list(streams) == list(contract["suite"]["streams"]), "Stage-A stream order drift")
    all_tasks = [task for stream_id in streams for task in streams[stream_id]]
    require(len(all_tasks) == 144 and len(set(all_tasks)) == 144, "Stage-A task set drift")
    forbidden_heldout = set(map(str, split["e1_common_heldout_probe"]))
    require(len(forbidden_heldout) == 18 and forbidden_heldout.isdisjoint(all_tasks), "heldout/update overlap")

    run_root = Path(contract["run_root"])
    mixed_by_stream: dict[str, int] = {}
    mixed_tasks_by_stream: dict[str, list[str]] = {}
    success_rollouts_by_stream: dict[str, int] = {}
    pool_sha256: dict[str, str] = {}
    all_trajectory_refs_revalidated = True
    for stream_id, task_ids in streams.items():
        mixed_tasks: list[str] = []
        stream_success_rollouts = 0
        for task_id in task_ids:
            pool_path = run_root / "cases" / task_id / "pool_k8.json"
            require(pool_path.is_file(), f"missing frozen K8 pool: {task_id}")
            pool = load_json(pool_path)
            require(pool.get("task_id") == task_id, f"pool task identity drift: {task_id}")
            require(int(pool.get("k") or 0) == 8, f"pool K drift: {task_id}")
            trajectories = pool.get("trajectories") or []
            require(len(trajectories) == 8, f"pool trajectory cardinality drift: {task_id}")
            scores: list[float] = []
            seen_indices: set[int] = set()
            for row in trajectories:
                idx = int(row["rollout_index"])
                require(idx not in seen_indices, f"duplicate rollout index: {task_id}/{idx}")
                seen_indices.add(idx)
                trajectory = Path(row["trajectory_path"])
                require(trajectory.is_file(), f"missing trajectory: {task_id}/{idx}")
                require(sha_file(trajectory) == row["trajectory_sha256"], f"trajectory SHA drift: {task_id}/{idx}")
                score = float(row["score"])
                require(score in (0.0, 1.0), f"Stage-A endpoint score must be binary: {task_id}/{idx}")
                scores.append(score)
            is_mixed = min(scores) < 1.0 and max(scores) >= 1.0
            if is_mixed:
                mixed_tasks.append(task_id)
            stream_success_rollouts += int(sum(scores))
            pool_sha256[task_id] = sha_file(pool_path)
        mixed_by_stream[stream_id] = len(mixed_tasks)
        mixed_tasks_by_stream[stream_id] = sorted(mixed_tasks)
        success_rollouts_by_stream[stream_id] = stream_success_rollouts

    required = int(contract["equal_dose_support"]["required_mixed_pools_per_stream"])
    require(required == 4, "equal-dose support threshold drift")
    failing_streams = sorted(stream_id for stream_id, count in mixed_by_stream.items() if count < required)
    support_pass = not failing_streams

    treated_by_stream: dict[str, list[str]] = {}
    treated_rows: list[dict[str, Any]] = []
    if support_pass:
        for stream_id in streams:
            selected = choose_four(stream_id, mixed_tasks_by_stream[stream_id])
            require(len(selected) == 4, f"treated mixed-pool cardinality drift: {stream_id}")
            treated_by_stream[stream_id] = selected
            for task_id in selected:
                treated_rows.append(
                    {
                        "stream_id": stream_id,
                        "task_id": task_id,
                        "pool_k8_path": str(run_root / "cases" / task_id / "pool_k8.json"),
                        "pool_k8_sha256": pool_sha256[task_id],
                        "selection_key_sha256": hashlib.sha256(
                            f"semantic-transfer-mrw4-v2|{stream_id}|{task_id}".encode("utf-8")
                        ).hexdigest(),
                    }
                )
        require(len(treated_rows) == 72, "equal-dose treated-pool total must be exactly 72")
    else:
        require(not treated_by_stream and not treated_rows, "failed support must not emit treated pool IDs")

    reduction_routers: dict[str, Any] = {}
    if support_pass:
        stream_ids = list(streams)
        difficulty_mrw = choose_nine_streams(
            stream_ids,
            success_rollouts_by_stream,
            descending=False,
            salt="semantic-transfer-difficulty-v2",
        )
        mixedness_mrw = choose_nine_streams(
            stream_ids,
            mixed_by_stream,
            descending=True,
            salt="semantic-transfer-mixedness-v2",
        )
        require(len(difficulty_mrw) == len(set(difficulty_mrw)) == 9, "difficulty router cardinality drift")
        require(len(mixedness_mrw) == len(set(mixedness_mrw)) == 9, "mixedness router cardinality drift")
        reduction_routers = {
            "difficulty_only": {
                "score": "Stage-A successful rollouts / 64; lower success means harder",
                "ordering": "ascending success count; SHA256(semantic-transfer-difficulty-v2|stream_id) tie-break",
                "mrw4_streams": difficulty_mrw,
                "win_c_streams": [stream_id for stream_id in stream_ids if stream_id not in set(difficulty_mrw)],
                "success_rollouts_per_stream": success_rollouts_by_stream,
            },
            "mixedness_only": {
                "score": "Stage-A mixed K=8 pools / 8; higher count means more mixedness",
                "ordering": "descending mixed-pool count; SHA256(semantic-transfer-mixedness-v2|stream_id) tie-break",
                "mrw4_streams": mixedness_mrw,
                "win_c_streams": [stream_id for stream_id in stream_ids if stream_id not in set(mixedness_mrw)],
                "mixed_pools_per_stream": mixed_by_stream,
            },
            "freeze_before_stage_b_outcomes": True,
            "extra_updater_calls": 0,
            "extra_heldout_evaluations": 0,
        }

    # The heldout namespace must remain untouched by Stage A.
    touched_heldout: list[str] = []
    for task_id in sorted(forbidden_heldout):
        if (run_root / "cases" / task_id).exists():
            touched_heldout.append(task_id)
    require(not touched_heldout, f"Stage-A touched forbidden heldout tasks: {touched_heldout}")

    status = (
        "PASS_SEMANTIC_TRANSFER_EQUAL_DOSE_SUPPORT_READY_FOR_STAGE_B_DESIGN"
        if support_pass
        else "HOLD_SEMANTIC_TRANSFER_INSUFFICIENT_EQUAL_DOSE_SUPPORT"
    )
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-v2-stage-a-equal-dose-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "contract_path": str(args.contract),
        "contract_sha256": contract_sha,
        "authorization_path": str(args.authorization),
        "authorization_sha256": auth_sha,
        "summary_path": str(args.summary),
        "summary_sha256": sha_file(args.summary),
        "integrity": {
            "streams": 18,
            "tasks": 144,
            "actor_rollouts": 1152,
            "frozen_k8_pools": 144,
            "all_trajectory_refs_revalidated": all_trajectory_refs_revalidated,
            "heldout_tasks_touched": 0,
            "updater_calls": 0,
            "heldout_evaluations": 0,
            "partial_effect_read": False
        },
        "support": {
            "required_mixed_pools_per_stream": required,
            "mixed_pools_per_stream": mixed_by_stream,
            "failing_streams": failing_streams,
            "pass": support_pass,
        },
        "equal_dose_treatment_manifest": {
            "selection_rule": "lowest SHA256(semantic-transfer-mrw4-v2|stream_id|task_id) among mixed pools",
            "treated_pools_per_stream": 4 if support_pass else 0,
            "treated_pool_total": len(treated_rows),
            "treated_task_ids_by_stream": treated_by_stream,
            "rows": treated_rows,
            "scientific_inclusion": support_pass,
        },
        "stage_a_reduction_routers": reduction_routers,
        "interpretation": (
            "This adjudication reads only complete Stage-A search-pool success/failure support after all 144 pools are sealed. "
            "It does not read or infer any WIN-C/MRW4 learned-skill effect. Passing support freezes an equal-dose 72-pool treatment manifest and two same-information reduction routers before any Stage-B outcome for a separately contracted Stage B."
        ),
        "authority": {
            "prepare_stage_b_contract": support_pass,
            "execute_stage_b": False,
            "heldout_evaluation": False,
            "analyzer": False,
            "paper_promotion": False,
        },
        "next_gate": (
            "SEPARATE_STAGE_B_CONTRACT_AND_PREEXECUTION_REVIEW"
            if support_pass
            else "CLOSE_SEMANTIC_TRANSFER_CHILD_SUPPORT_HOLD"
        ),
    }
    atomic_json(args.output, payload)
    print(json.dumps({
        "status": status,
        "support": payload["support"],
        "treated_pool_total": len(treated_rows),
        "next_gate": payload["next_gate"],
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if support_pass else 3


if __name__ == "__main__":
    raise SystemExit(main())
