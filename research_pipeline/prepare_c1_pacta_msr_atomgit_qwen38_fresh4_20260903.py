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
CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh4-contract-20260903.json"
FRESH1 = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-fresh-pool-20260902.json"
FRESH2 = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh2-pool-20260903.json"
FRESH3 = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-pool-20260903.json"
FRESH3_CLOSEOUT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-source-v2-closeout-20260903.json"
Q03_CONTROLLED = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q03-output-mcp-closure-20260903.json"
OUT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh4-pool-20260903.json"
SPLIT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh4-split-20260903.json"
RUN = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh4-preflight-20260903-v1")

SOURCE_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH4-SOURCE-v1"
FUTURE_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH4-FUTURE-v1"
PILOT_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH4-PILOT-v1"
RANDOM_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH4-RANDOM-v1"
DUPLICATE_REPO_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH4-DUPLICATE-REPO-v1"

EXPECTED = {
    "fresh1": "2391967a3da363bcbbe87403599970854d7cf7ed82b249078b0469b36a8de59e",
    "fresh2": "1e52b3e00d7c8d82cf0846d66c87223c44bc137765cbd10e4ca139809134c3b1",
    "fresh3": "3780fa80ee0bbfce01e3fd4f6bcabe6aaaa21111c0aa910ea7ce1bde302a9257",
    "fresh3_closeout": "c651d079d72df31c9a8d9ff12e9ea855c0bd6dd87c4cf52773c2d5798f533a45",
    "q03_controlled": "af311a6a2785bff2d06cc12febf5288de5f4759a156d3ca4ac0407cd550837ea",
}


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
    checks = [
        (FRESH1, EXPECTED["fresh1"], "fresh1"),
        (FRESH2, EXPECTED["fresh2"], "fresh2"),
        (FRESH3, EXPECTED["fresh3"], "fresh3"),
        (FRESH3_CLOSEOUT, EXPECTED["fresh3_closeout"], "fresh3 closeout"),
        (Q03_CONTROLLED, EXPECTED["q03_controlled"], "Q0.3 controlled output closure"),
    ]
    for path, expected, label in checks:
        if not path.is_file() or sha_file(path) != expected:
            raise RuntimeError(f"{label} hash drift")
    close = json.loads(FRESH3_CLOSEOUT.read_text())
    if close.get("status") != "HOLD_FRESH3_SOURCE_POOL_RETIRED_PROVIDER_TIMEOUT" or close.get("pool_retired") is not True:
        raise RuntimeError("fresh3 is not formally retired")
    q03 = json.loads(Q03_CONTROLLED.read_text())
    if q03.get("status") != "ATOMGIT_QWEN38_Q03_CONTROLLED_OUTPUT_MCP_PASS" or q03.get("qualified") != 12:
        raise RuntimeError("controlled output Q0.3 not qualified")
    pools = [pool_ids(FRESH1), pool_ids(FRESH2), pool_ids(FRESH3)]
    sets = [base, *pools]
    for i, left in enumerate(sets):
        for right in sets[i + 1:]:
            if left & right:
                raise RuntimeError("unexpected exclusion overlap")
    excluded = set().union(*sets)
    if len(base) != 29 or len(excluded) != 89:
        raise RuntimeError(f"exclusion count drift base={len(base)} total={len(excluded)}")
    return excluded, {
        "historical_prior_count": len(base),
        "fresh1_count": 20,
        "fresh2_count": 20,
        "fresh3_count": 20,
        "total_unique_excluded": len(excluded),
        "historical_prior_provenance": base_prov,
        "fresh1_ids": sorted(pools[0]),
        "fresh2_ids": sorted(pools[1]),
        "fresh3_ids": sorted(pools[2]),
        "input_sha256": EXPECTED,
    }


def select_pool() -> dict[str, Any]:
    excluded, provenance = exclusion_ids()
    rows = pq.read_table(DATASET, columns=["instance_id", "repo", "problem_statement", "base_commit"]).to_pylist()
    by: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["instance_id"] not in excluded:
            by[str(row["repo"])].append(row)
    eligible = {repo: items for repo, items in by.items() if len(items) >= 2}
    if len(eligible) != 9:
        raise RuntimeError(f"expected nine pair-eligible repositories after 89-ID exclusion, got {len(eligible)}")

    def make_unit(repo: str, items: list[dict[str, Any]], *, second: bool) -> dict[str, Any]:
        suffix = "|SECOND" if second else ""
        source = min(items, key=lambda r: (sha_text(SOURCE_SALT + suffix + "|" + r["instance_id"]), r["instance_id"]))
        future = min(
            (r for r in items if r["instance_id"] != source["instance_id"]),
            key=lambda r: (sha_text(FUTURE_SALT + suffix + "|" + source["instance_id"] + "|" + r["instance_id"]), r["instance_id"]),
        )
        unit_id = source["instance_id"] + "=>" + future["instance_id"]
        return {
            "unit_id": unit_id,
            "task_family": repo,
            "sampling_stratum": "duplicate_repo_second_pair" if second else "primary_repo_pair",
            "source_task_id": source["instance_id"],
            "source_task": source["problem_statement"],
            "source_task_sha256": sha_text(source["problem_statement"]),
            "source_base_commit": source["base_commit"],
            "future_task_id": future["instance_id"],
            "future_task": future["problem_statement"],
            "future_task_sha256": sha_text(future["problem_statement"]),
            "future_base_commit": future["base_commit"],
            "source_rank": sha_text(SOURCE_SALT + suffix + "|" + source["instance_id"]),
            "future_rank": sha_text(FUTURE_SALT + suffix + "|" + source["instance_id"] + "|" + future["instance_id"]),
            "pilot_rank": sha_text(PILOT_SALT + "|" + unit_id),
            "random_gate_rank": sha_text(RANDOM_SALT + "|" + unit_id),
            "prior_id_overlap": False,
            "provider_interface": "controlled-output-mcp-q03",
        }

    units = [make_unit(repo, items, second=False) for repo, items in sorted(eligible.items())]
    used = {task for unit in units for task in (unit["source_task_id"], unit["future_task_id"])}
    duplicate_candidates = [repo for repo, items in eligible.items() if len([r for r in items if r["instance_id"] not in used]) >= 2]
    if not duplicate_candidates:
        raise RuntimeError("no repository has two unused tasks for the tenth pair")
    duplicate_repo = min(duplicate_candidates, key=lambda repo: (sha_text(DUPLICATE_REPO_SALT + "|" + repo), repo))
    remaining = [row for row in eligible[duplicate_repo] if row["instance_id"] not in used]
    units.append(make_unit(duplicate_repo, remaining, second=True))

    ids = [task for unit in units for task in (unit["source_task_id"], unit["future_task_id"])]
    repo_counts: dict[str, int] = defaultdict(int)
    for unit in units:
        repo_counts[unit["task_family"]] += 1
    if len(units) != 10 or len(ids) != 20 or len(set(ids)) != 20 or set(ids) & excluded:
        raise RuntimeError("fresh4 disjointness/geometry failure")
    if len(repo_counts) != 9 or sorted(repo_counts.values()) != [1] * 8 + [2] or repo_counts[duplicate_repo] != 2:
        raise RuntimeError("fresh4 9-repository/10-pair weighting drift")
    return {
        "schema_version": 1,
        "created_at_utc": now(),
        "experiment": "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH4-20260903",
        "status": "FRESH4_PAIR_POOL_FROZEN_PRE_PROVIDER",
        "dataset": {"path": str(DATASET), "sha256": sha_file(DATASET), "rows": len(rows)},
        "contract_sha256": sha_file(CONTRACT),
        "prior_exclusion_count": len(excluded),
        "prior_provenance": provenance,
        "selection": {
            "source_salt": SOURCE_SALT,
            "future_salt": FUTURE_SALT,
            "pilot_salt": PILOT_SALT,
            "random_salt": RANDOM_SALT,
            "duplicate_repo_salt": DUPLICATE_REPO_SALT,
            "sampling_rule": "one pair from each of nine pair-eligible repositories plus one fully disjoint second pair from a hash-selected repository",
            "duplicate_repository": duplicate_repo,
            "equal_pair_weighting": True,
            "outcome_fields_read": False,
        },
        "candidate_count": len(units),
        "repository_count": len(repo_counts),
        "repository_pair_counts": dict(sorted(repo_counts.items())),
        "units": units,
        "provider_calls": 0,
        "scientific_source_calls": 0,
    }


def split(pool: dict[str, Any]) -> dict[str, Any]:
    ranked = sorted(pool["units"], key=lambda u: (u["pilot_rank"], u["unit_id"]))
    pilot, sealed = ranked[:8], ranked[8:]
    if len(pilot) != 8 or len(sealed) != 2:
        raise RuntimeError("fresh4 pilot geometry")
    random_ranking = [u["unit_id"] for u in sorted(pilot, key=lambda u: (u["random_gate_rank"], u["unit_id"]))]
    return {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "FRESH4_PILOT_SPLIT_FROZEN_PRE_PROVIDER",
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
        raise RuntimeError("fresh4 targets exist; no overwrite")
    pool = select_pool(); split_doc = split(pool)
    pool_sha = atomic_json(OUT, pool); split_sha = atomic_json(SPLIT, split_doc)
    RUN.mkdir(parents=True)
    atomic_json(RUN / "fresh4-pool.json", pool)
    atomic_json(RUN / "fresh4-split.json", split_doc)
    atomic_json(RUN / "manifest.json", {
        "schema_version": 1,
        "created_at_utc": now(),
        "status": "ZERO_PROVIDER_FRESH4_READY",
        "fresh4_pool_sha256": pool_sha,
        "fresh4_split_sha256": split_sha,
        "provider_calls": 0,
        "scientific_source_calls": 0,
    })
    print(json.dumps({
        "status": pool["status"],
        "candidate_count": pool["candidate_count"],
        "repository_count": pool["repository_count"],
        "prior_exclusion_count": pool["prior_exclusion_count"],
        "fresh4_pool_sha256": pool_sha,
        "fresh4_split_sha256": split_sha,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
