from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .alfworld_react_scaffold import task_family_from_gamefile
from .p0_alfworld_adapter import ALFWorldGameRunner, load_config


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _rank(value: str, seed: int, label: str) -> str:
    return hashlib.sha256(f"{seed}|{label}|{value}".encode()).hexdigest()


def _round_robin(values: list[str], seed: int, label: str) -> list[str]:
    groups: dict[str, list[str]] = {}
    for value in values:
        groups.setdefault(task_family_from_gamefile(value), []).append(value)
    for family in groups:
        groups[family] = sorted(groups[family], key=lambda x: _rank(x, seed, f"{label}|{family}"))
    families = sorted(groups, key=lambda x: _rank(x, seed, f"{label}|family"))
    output: list[str] = []
    while families:
        keep: list[str] = []
        for family in families:
            if groups[family]:
                output.append(groups[family].pop(0))
            if groups[family]:
                keep.append(family)
        families = keep
    return output


def build_plan(
    alfworld_config: Path,
    *,
    seed: int = 42,
    shards: int = 2,
    source_pool_per_shard: int = 44,
    failures_per_shard: int = 20,
    c5_candidates_per_shard: int = 12,
    probe_count: int = 8,
    hidden_count: int = 24,
    hidden_per_candidate: int = 4,
    max_steps: int = 30,
) -> dict[str, Any]:
    cfg = load_config(alfworld_config)
    runner = ALFWorldGameRunner(cfg)
    seen = _round_robin(runner.available_game_files("eval_in_distribution"), seed, "c-shared-seen")
    unseen = _round_robin(runner.available_game_files("eval_out_of_distribution"), seed, "c-shared-unseen")
    source_total = shards * source_pool_per_shard
    if len(seen) < source_total + probe_count:
        raise RuntimeError("insufficient eval_in_distribution tasks for frozen source/probe split")
    if len(unseen) < hidden_count:
        raise RuntimeError("insufficient eval_out_of_distribution tasks for frozen hidden split")
    source = seen[:source_total]
    probes = seen[source_total:source_total + probe_count]
    hidden = unseen[:hidden_count]
    shard_rows = []
    for shard in range(shards):
        shard_source = source[shard * source_pool_per_shard:(shard + 1) * source_pool_per_shard]
        shard_rows.append({
            "shard": shard,
            "source_pool": shard_source,
            "failure_target": failures_per_shard,
            "c5_candidate_target": c5_candidates_per_shard,
        })
    return {
        "schema_version": "1.0",
        "generated_at": _now(),
        "seed": seed,
        "scientific_role": "shared upstream substrate qualification for C-1/C-4/C-5; no method PASS/FAIL authority",
        "policy": {
            "hidden_outcome_used_for_candidate_generation": False,
            "self_labels_frozen_before_probe_hidden_execution": True,
            "same_task_same_step_cap_across_intervention_arms": True,
            "persistent_updater_program_rescue_forbidden": True,
            "max_gpus_per_shard": 1,
            "shared_collection_max_concurrent_shards": shards,
        },
        "contracts": {
            "C-1": {"lineage_rounds": 5, "independent_roots_per_candidate": 2, "minimum_label_decisions": 200},
            "C-4": {"minimum_failures": failures_per_shard * shards, "modes": ["rewrite", "replan", "retrieve", "rollback", "stop"], "order_pair_target": 12},
            "C-5": {"candidate_target": c5_candidates_per_shard * shards, "probe_count": probe_count, "hidden_pool": hidden_count, "hidden_per_candidate": hidden_per_candidate},
        },
        "max_steps": max_steps,
        "probe_tasks": probes,
        "hidden_tasks": hidden,
        "shards": shard_rows,
    }


def write_plan(plan: dict[str, Any], path: Path) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return plan
