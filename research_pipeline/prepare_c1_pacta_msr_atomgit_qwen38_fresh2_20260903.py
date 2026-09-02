#!/usr/bin/env python3
"""Zero-provider fresh2 compiler for AtomGit Qwen3.8 PACTA-MSR."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from research_pipeline.prepare_c1_pacta_msr_qwen397_20260902 import DATASET, prior_ids

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh2-contract-20260903.json"
RETIRED_POOL = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-fresh-pool-20260902.json"
T0_CLOSEOUT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-t0-source-closeout-20260902.json"
Q02_CLOSEOUT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q02-source-budget-closure-20260902.json"
OUT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh2-pool-20260903.json"
SPLIT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh2-split-20260903.json"
RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh2-preflight-20260903-v1")

SOURCE_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH2-SOURCE-v1"
FUTURE_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH2-FUTURE-v1"
PILOT_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH2-PILOT-v1"
RANDOM_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH2-RANDOM-v1"
EXPECTED_RETIRED_POOL_SHA = "2391967a3da363bcbbe87403599970854d7cf7ed82b249078b0469b36a8de59e"
EXPECTED_T0_CLOSEOUT_SHA = "1796b9739e85065405d70f2f1f5e60376a38d2f66bc048bea99f57cbed388db4"
EXPECTED_Q02_CLOSEOUT_SHA = "c41ebc9df5a28b1e6f2643195be2cdfd170318de5577ef2aff3b1891819959b6"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canon(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def atomic_json(path: Path, payload: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = dict(payload)
    body["payload_sha256"] = sha_text(canon(payload))
    raw = (json.dumps(body, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
    return hashlib.sha256(raw).hexdigest()


def exclusion_ids() -> tuple[set[str], dict[str, Any]]:
    base, provenance = prior_ids()
    if sha_file(RETIRED_POOL) != EXPECTED_RETIRED_POOL_SHA:
        raise RuntimeError("retired pool hash drift")
    if sha_file(T0_CLOSEOUT) != EXPECTED_T0_CLOSEOUT_SHA:
        raise RuntimeError("T0 closeout hash drift")
    if sha_file(Q02_CLOSEOUT) != EXPECTED_Q02_CLOSEOUT_SHA:
        raise RuntimeError("Q0.2 closeout hash drift")
    retired_doc = json.loads(RETIRED_POOL.read_text())
    retired = {task for unit in retired_doc["units"] for task in (unit["source_task_id"], unit["future_task_id"])}
    if len(retired) != 20:
        raise RuntimeError("retired pool geometry drift")
    if base & retired:
        raise RuntimeError("unexpected exclusion overlap")
    all_ids = base | retired
    if len(base) != 29 or len(all_ids) != 49:
        raise RuntimeError(f"exclusion count drift base={len(base)} total={len(all_ids)}")
    return all_ids, {
        "base_prior_count": len(base),
        "retired_pool_count": len(retired),
        "total_unique_excluded": len(all_ids),
        "retired_pool_ids": sorted(retired),
        "base_prior_provenance": provenance,
        "retired_pool_sha256": EXPECTED_RETIRED_POOL_SHA,
        "t0_closeout_sha256": EXPECTED_T0_CLOSEOUT_SHA,
        "q02_closeout_sha256": EXPECTED_Q02_CLOSEOUT_SHA,
    }


def select_pool() -> dict[str, Any]:
    excluded, provenance = exclusion_ids()
    rows = pq.read_table(DATASET, columns=["instance_id", "repo", "problem_statement", "base_commit"]).to_pylist()
    by: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["instance_id"] not in excluded:
            by[str(row["repo"])].append(row)
    eligible = {repo: items for repo, items in by.items() if len(items) >= 2}
    if len(eligible) != 10:
        raise RuntimeError(f"expected ten eligible repositories, got {len(eligible)}")
    units = []
    for repo, items in sorted(eligible.items()):
        source = min(items, key=lambda r: (sha_text(SOURCE_SALT + "|" + r["instance_id"]), r["instance_id"]))
        future = min(
            (r for r in items if r["instance_id"] != source["instance_id"]),
            key=lambda r: (
                sha_text(FUTURE_SALT + "|" + source["instance_id"] + "|" + r["instance_id"]),
                r["instance_id"],
            ),
        )
        unit_id = source["instance_id"] + "=>" + future["instance_id"]
        units.append(
            {
                "unit_id": unit_id,
                "task_family": repo,
                "source_task_id": source["instance_id"],
                "source_task": source["problem_statement"],
                "source_task_sha256": sha_text(source["problem_statement"]),
                "source_base_commit": source["base_commit"],
                "future_task_id": future["instance_id"],
                "future_task": future["problem_statement"],
                "future_task_sha256": sha_text(future["problem_statement"]),
                "future_base_commit": future["base_commit"],
                "source_rank": sha_text(SOURCE_SALT + "|" + source["instance_id"]),
                "future_rank": sha_text(FUTURE_SALT + "|" + source["instance_id"] + "|" + future["instance_id"]),
                "pilot_rank": sha_text(PILOT_SALT + "|" + unit_id),
                "random_gate_rank": sha_text(RANDOM_SALT + "|" + unit_id),
                "prior_id_overlap": False,
                "prior_reasoningbank_scientific_output": False,
            }
        )
    ids = [task for u in units for task in (u["source_task_id"], u["future_task_id"])]
    if len(ids) != 20 or len(set(ids)) != 20 or set(ids) & excluded:
        raise RuntimeError("fresh2 disjointness failure")
    return {
        "schema_version": 1,
        "created_at_utc": now(),
        "experiment": "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH2-20260903",
        "status": "FRESH2_PAIR_POOL_FROZEN_PRE_PROVIDER",
        "dataset": {"path": str(DATASET), "sha256": sha_file(DATASET), "rows": len(rows)},
        "contract_sha256": sha_file(CONTRACT),
        "prior_exclusion_count": len(excluded),
        "prior_provenance": provenance,
        "selection": {
            "source_salt": SOURCE_SALT,
            "future_salt": FUTURE_SALT,
            "pilot_salt": PILOT_SALT,
            "random_salt": RANDOM_SALT,
            "one_pair_per_repository": True,
            "outcome_fields_read": False,
        },
        "candidate_count": len(units),
        "repository_count": len({u["task_family"] for u in units}),
        "units": units,
        "provider_calls": 0,
        "scientific_source_calls": 0,
    }


def split(pool: dict[str, Any]) -> dict[str, Any]:
    ranked = sorted(pool["units"], key=lambda u: (u["pilot_rank"], u["unit_id"]))
    pilot, sealed = ranked[:8], ranked[8:]
    if len(pilot) != 8 or len(sealed) != 2:
        raise RuntimeError("fresh2 pilot geometry")
    random_ranking = [u["unit_id"] for u in sorted(pilot, key=lambda u: (u["random_gate_rank"], u["unit_id"]))]
    return {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "FRESH2_PILOT_SPLIT_FROZEN_PRE_PROVIDER",
        "pilot": [u["unit_id"] for u in pilot],
        "sealed": [u["unit_id"] for u in sealed],
        "random_ranking_pre_shadow": random_ranking,
        "pilot_salt": PILOT_SALT,
        "random_salt": RANDOM_SALT,
        "provider_calls": 0,
        "scientific_source_calls": 0,
    }


def main() -> None:
    if OUT.exists() or SPLIT.exists() or RUN.exists():
        raise RuntimeError("fresh2 targets exist; no overwrite")
    pool = select_pool()
    split_doc = split(pool)
    pool_sha = atomic_json(OUT, pool)
    split_sha = atomic_json(SPLIT, split_doc)
    RUN.mkdir(parents=True)
    atomic_json(RUN / "fresh2-pool.json", pool)
    atomic_json(RUN / "fresh2-split.json", split_doc)
    atomic_json(
        RUN / "manifest.json",
        {
            "schema_version": 1,
            "created_at_utc": now(),
            "status": "ZERO_PROVIDER_FRESH2_READY",
            "fresh2_pool_sha256": pool_sha,
            "fresh2_split_sha256": split_sha,
            "provider_calls": 0,
            "scientific_source_calls": 0,
        },
    )
    print(
        json.dumps(
            {
                "status": pool["status"],
                "candidate_count": pool["candidate_count"],
                "repository_count": pool["repository_count"],
                "prior_exclusion_count": pool["prior_exclusion_count"],
                "fresh2_pool_sha256": pool_sha,
                "fresh2_split_sha256": split_sha,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
