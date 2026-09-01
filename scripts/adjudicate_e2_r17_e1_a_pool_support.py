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


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    contract = load_json(args.contract)
    authorization = load_json(args.authorization)
    summary = load_json(args.summary)
    contract_sha = sha_file(args.contract)
    authorization_sha = sha_file(args.authorization)

    require(contract.get("status") == "FROZEN_E1_A_POOL_SUPPORT", "E1-A contract status invalid")
    require(authorization.get("status") == "AUTHORIZED_E1", "E1-A authorization status invalid")
    require(authorization.get("contract_sha256") == contract_sha, "authorization does not bind exact E1-A contract")
    require(summary.get("status") == "COMPLETED_ALL_96_POOLS_PENDING_SEPARATE_SUPPORT_ADJUDICATION", "E1-A pool freeze incomplete")
    require(summary.get("contract_sha256") == contract_sha, "summary contract SHA mismatch")
    require(summary.get("authorization_sha256") == authorization_sha, "summary authorization SHA mismatch")
    require(int(summary.get("streams") or 0) == 12, "E1-A stream cardinality invalid")
    require(int(summary.get("tasks") or 0) == 96, "E1-A task cardinality invalid")
    require(int(summary.get("actor_rollouts") or 0) == 768, "E1-A rollout cardinality invalid")
    require(int(summary.get("updater_calls") or -1) == 0, "E1-A must contain zero updater calls")
    require(summary.get("e1_b_authority") is False, "E1-A summary cannot inherit E1-B authority")

    support = summary.get("support") or {}
    stream_rows = support.get("stream_rows") or []
    require(len(stream_rows) == 12, "support summary must include 12 stream rows")
    mixed = int(support.get("mixed_pool_count") or 0)
    exposed = int(support.get("exposed_stream_count") or 0)
    supported_families = int(support.get("supported_families") or 0)
    thresholds = contract["support_gate"]
    min_mixed = int(thresholds["mixed_pool_count_minimum"])
    min_exposed = int(thresholds["exposed_stream_minimum"])
    min_per_stream = int(thresholds["mixed_pools_per_exposed_stream_minimum"])
    min_families = int(thresholds["supported_families_minimum"])

    run_root = Path(contract["run_root"])
    split = load_json(Path(contract["suite"]["root"]) / "r17_split_manifest.json")
    frozen_streams = list(contract["streams"])
    require(list(split["e1_update_streams"].keys()) == frozen_streams, "stream manifest drift")
    expected_tasks = [str(task) for stream_id in frozen_streams for task in split["e1_update_streams"][stream_id]]
    require(len(expected_tasks) == 96 and len(set(expected_tasks)) == 96, "frozen update set must contain 96 unique tasks")
    task_to_stream = {
        str(task): stream_id
        for stream_id in frozen_streams
        for task in split["e1_update_streams"][stream_id]
    }
    metadata_rows = load_json(Path(contract["suite"]["root"]) / "r17_controlled_metadata.json")
    metadata = {str(row["id"]): row for row in metadata_rows}

    pool_sha: dict[str, str] = {}
    mixed_recomputed = 0
    per_stream_mixed = {stream_id: 0 for stream_id in frozen_streams}
    per_family_mixed: dict[str, int] = {}
    for task_id in expected_tasks:
        pool_path = run_root / "cases" / task_id / "pool_k8.json"
        require(pool_path.exists(), f"missing frozen K8 pool: {task_id}")
        pool = load_json(pool_path)
        require(pool.get("task_id") == task_id and int(pool.get("k") or 0) == 8, f"invalid K8 pool identity: {task_id}")
        trajectories = pool.get("trajectories") or []
        require(len(trajectories) == 8, f"K8 pool missing trajectory refs: {task_id}")
        scores = [float(row["score"]) for row in trajectories]
        is_mixed = int(min(scores) < 1.0 and max(scores) >= 1.0)
        mixed_recomputed += is_mixed
        per_stream_mixed[task_to_stream[task_id]] += is_mixed
        family = str(metadata[task_id]["primary_failure_family"])
        per_family_mixed[family] = per_family_mixed.get(family, 0) + is_mixed
        for row in trajectories:
            trajectory = Path(row["trajectory_path"])
            require(trajectory.exists() and sha_file(trajectory) == row["trajectory_sha256"], f"trajectory SHA drift: {task_id}/{row['rollout_index']}")
        pool_sha[task_id] = sha_file(pool_path)
    require(mixed_recomputed == mixed, "mixed-pool total does not recompute from exact frozen pools")
    exposed_recomputed = sum(int(value >= min_per_stream) for value in per_stream_mixed.values())
    require(exposed_recomputed == exposed, "exposed-stream count does not recompute directly from exact frozen pools")
    supported_families_recomputed = sum(int(value > 0) for value in per_family_mixed.values())
    require(supported_families_recomputed == supported_families, "supported-family count does not recompute directly from exact frozen pools")
    summary_stream_map = {str(row["stream_id"]): int(row["mixed_pools"]) for row in stream_rows}
    require(summary_stream_map == per_stream_mixed, "summary per-stream mixed counts drift from exact frozen pools")
    require(dict(sorted((support.get("family_mixed_counts") or {}).items())) == dict(sorted(per_family_mixed.items())), "summary family mixed counts drift from exact frozen pools")
    require(bool(support.get("primary_hard_gate_pass")) == (mixed >= min_mixed and exposed >= min_exposed), "hard-gate flag is inconsistent")
    require(bool(support.get("family_generalization_gate_pass")) == (supported_families >= min_families), "family gate flag is inconsistent")

    hard_pass = mixed >= min_mixed and exposed >= min_exposed
    family_pass = supported_families >= min_families
    status = "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT" if hard_pass else "STOP_E1_SUPPORT_INSUFFICIENT"
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-e1-a-pool-support-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "summary_path": str(args.summary),
        "summary_sha256": sha_file(args.summary),
        "integrity": {
            "streams": 12,
            "tasks": 96,
            "actor_rollouts": 768,
            "frozen_k8_pools": 96,
            "all_trajectory_shas_revalidated": True,
            "task_replacement_after_support_observation": False,
            "waiver_or_rounding": False,
            "updater_calls": 0,
        },
        "primary_support": {
            "mixed_pools": mixed,
            "required_mixed_pools": min_mixed,
            "exposed_streams": exposed,
            "required_exposed_streams": min_exposed,
            "mixed_per_exposed_stream": min_per_stream,
            "per_stream_mixed_recomputed": per_stream_mixed,
            "pass": hard_pass,
        },
        "family_generalization": {
            "supported_families": supported_families,
            "required_supported_families": min_families,
            "pass": family_pass,
            "per_family_mixed_recomputed": dict(sorted(per_family_mixed.items())),
            "controls_primary_e1_b_authorization": False,
            "claim_if_failed": "Block family-generalization and prospective family-ranking claims; pooled E1-B may still be contracted only if primary support passes."
        },
        "pool_sha256": pool_sha,
        "interpretation": (
            "This adjudication evaluates only pre-treatment mixed-pool support and protocol integrity. "
            "It does not evaluate MRW, WIN, RB-AGG, future skill utility, or paper effectiveness."
        ),
        "authority": {
            "prepare_e1_b_contract": hard_pass,
            "execute_e1_b": False,
            "provider_runtime_pilot": False,
            "paper_promotion": False,
            "submission": False,
        },
        "next_gate": (
            "SEPARATE_IMMUTABLE_E1_B_CONTRACT_WITH_FRESH_UPDATER_IDENTITY_AND_NEGATIVE_CONTROL_FIRST"
            if hard_pass
            else "STOP_CENTRAL_R17_ON_CURRENT_CONTROLLED_SUBSTRATE_SUPPORT"
        ),
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if hard_pass else 3


if __name__ == "__main__":
    raise SystemExit(main())
