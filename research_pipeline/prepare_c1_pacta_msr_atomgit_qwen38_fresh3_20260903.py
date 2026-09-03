#!/usr/bin/env python3
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
CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-contract-20260903.json"
FRESH1 = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-fresh-pool-20260902.json"
FRESH2 = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh2-pool-20260903.json"
FRESH2_CLOSEOUT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh2-source-closeout-20260903.json"
Q03_CLOSEOUT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q03-text-bridge-closure-20260903.json"
OUT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-pool-20260903.json"
SPLIT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-split-20260903.json"
RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh3-preflight-20260903-v1")

SOURCE_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH3-SOURCE-v1"
FUTURE_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH3-FUTURE-v1"
PILOT_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH3-PILOT-v1"
RANDOM_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH3-RANDOM-v1"
EXPECTED_FRESH1_SHA = "2391967a3da363bcbbe87403599970854d7cf7ed82b249078b0469b36a8de59e"
EXPECTED_FRESH2_SHA = "1e52b3e00d7c8d82cf0846d66c87223c44bc137765cbd10e4ca139809134c3b1"
EXPECTED_FRESH2_CLOSEOUT_SHA = "c218f298069cbc9238c7c831bc09cb96808ece0bb0c736f29f2977088942a4d0"
EXPECTED_Q03_CLOSEOUT_SHA = "077383ca894abc1c3986e01ef90b16628d2580a3058d66c2838a63796208fdac"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def atomic_json(path: Path, payload: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = dict(payload)
    body["payload_sha256"] = sha_text(canonical(payload))
    raw = (json.dumps(body, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
    return hashlib.sha256(raw).hexdigest()


def pool_ids(path: Path) -> set[str]:
    doc = json.loads(path.read_text())
    ids = {task for unit in doc["units"] for task in (unit["source_task_id"], unit["future_task_id"])}
    if len(ids) != 20:
        raise RuntimeError(f"pool geometry drift: {path}")
    return ids


def exclusion_ids() -> tuple[set[str], dict[str, Any]]:
    base, base_prov = prior_ids()
    for path, expected, label in (
        (FRESH1, EXPECTED_FRESH1_SHA, "fresh1"),
        (FRESH2, EXPECTED_FRESH2_SHA, "fresh2"),
        (FRESH2_CLOSEOUT, EXPECTED_FRESH2_CLOSEOUT_SHA, "fresh2 closeout"),
        (Q03_CLOSEOUT, EXPECTED_Q03_CLOSEOUT_SHA, "Q0.3 closeout"),
    ):
        if not path.is_file() or sha_file(path) != expected:
            raise RuntimeError(f"{label} hash drift")
    q03 = json.loads(Q03_CLOSEOUT.read_text())
    if q03.get("status") != "ATOMGIT_QWEN38_Q03_TEXT_BRIDGE_PASS" or q03.get("fresh3_authorized") is not True:
        raise RuntimeError("Q0.3 does not authorize fresh3")
    fresh1 = pool_ids(FRESH1); fresh2 = pool_ids(FRESH2)
    if base & fresh1 or base & fresh2 or fresh1 & fresh2:
        raise RuntimeError("unexpected exclusion overlap")
    excluded = base | fresh1 | fresh2
    if len(base) != 29 or len(excluded) != 69:
        raise RuntimeError(f"exclusion count drift base={len(base)} total={len(excluded)}")
    return excluded, {
        "historical_prior_count": len(base),
        "fresh1_count": len(fresh1),
        "fresh2_count": len(fresh2),
        "total_unique_excluded": len(excluded),
        "historical_prior_provenance": base_prov,
        "fresh1_ids": sorted(fresh1),
        "fresh2_ids": sorted(fresh2),
        "fresh1_sha256": EXPECTED_FRESH1_SHA,
        "fresh2_sha256": EXPECTED_FRESH2_SHA,
        "fresh2_closeout_sha256": EXPECTED_FRESH2_CLOSEOUT_SHA,
        "q03_closeout_sha256": EXPECTED_Q03_CLOSEOUT_SHA,
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
    units: list[dict[str, Any]] = []
    for repo, items in sorted(eligible.items()):
        source = min(items, key=lambda r: (sha_text(SOURCE_SALT + "|" + r["instance_id"]), r["instance_id"]))
        future = min(
            (r for r in items if r["instance_id"] != source["instance_id"]),
            key=lambda r: (sha_text(FUTURE_SALT + "|" + source["instance_id"] + "|" + r["instance_id"]), r["instance_id"]),
        )
        unit_id = source["instance_id"] + "=>" + future["instance_id"]
        units.append({
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
        })
    ids = [task for unit in units for task in (unit["source_task_id"], unit["future_task_id"])]
    if len(ids) != 20 or len(set(ids)) != 20 or set(ids) & excluded:
        raise RuntimeError("fresh3 disjointness failure")
    return {
        "schema_version": 1,
        "created_at_utc": now(),
        "experiment": "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH3-20260903",
        "status": "FRESH3_PAIR_POOL_FROZEN_PRE_PROVIDER",
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
        "repository_count": len({unit["task_family"] for unit in units}),
        "units": units,
        "provider_calls": 0,
        "scientific_source_calls": 0,
    }


def make_split(pool: dict[str, Any]) -> dict[str, Any]:
    ranked = sorted(pool["units"], key=lambda u: (u["pilot_rank"], u["unit_id"]))
    pilot, sealed = ranked[:8], ranked[8:]
    if len(pilot) != 8 or len(sealed) != 2:
        raise RuntimeError("fresh3 pilot geometry")
    random_ranking = [u["unit_id"] for u in sorted(pilot, key=lambda u: (u["random_gate_rank"], u["unit_id"]))]
    return {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "FRESH3_PILOT_SPLIT_FROZEN_PRE_PROVIDER",
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
        raise RuntimeError("fresh3 targets exist; no overwrite")
    pool = select_pool(); split = make_split(pool)
    pool_sha = atomic_json(OUT, pool); split_sha = atomic_json(SPLIT, split)
    RUN.mkdir(parents=True)
    atomic_json(RUN / "fresh3-pool.json", pool)
    atomic_json(RUN / "fresh3-split.json", split)
    atomic_json(RUN / "manifest.json", {
        "schema_version": 1, "created_at_utc": now(), "status": "ZERO_PROVIDER_FRESH3_READY",
        "fresh3_pool_sha256": pool_sha, "fresh3_split_sha256": split_sha,
        "provider_calls": 0, "scientific_source_calls": 0,
    })
    print(json.dumps({
        "status": pool["status"], "candidate_count": pool["candidate_count"],
        "repository_count": pool["repository_count"], "prior_exclusion_count": pool["prior_exclusion_count"],
        "fresh3_pool_sha256": pool_sha, "fresh3_split_sha256": split_sha,
    }, sort_keys=True))


if __name__ == "__main__": main()
