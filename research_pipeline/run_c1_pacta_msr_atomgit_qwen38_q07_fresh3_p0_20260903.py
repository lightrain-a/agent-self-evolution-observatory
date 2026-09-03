#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from research_pipeline.c1_pacta_rb_qwen397 import atomic_bytes, atomic_json, sha256_file
from research_pipeline.c1_pacta_msr_qwen397_p0_core import load, sha
from research_pipeline.c1_pacta_msr_atomgit_qwen38_fresh3_bridge_source_runtime import Fresh3Container
from research_pipeline import c1_pacta_msr_atomgit_qwen38_q07_provider as qprov
from research_pipeline import run_c1_pacta_msr_qwen397_p0_stages_20260902 as legacy
from research_pipeline import run_c1_pacta_msr_qwen397_p0_final_20260902 as legacy_final

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q07-fresh3-p0-contract-20260903.json"
POOL = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-pool-20260903.json"
POOL_SHA = "3780fa80ee0bbfce01e3fd4f6bcabe6aaaa21111c0aa910ea7ce1bde302a9257"
SPLIT = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-split-20260903.json"
SPLIT_SHA = "d71f48910e531e62de2d056342c0c17ce17872503f089a29b16182fca3c1b2d9"
PROBES = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-probe-specs-20260903.json"
PROBES_SHA = "19f119fdb80e58427809a565d515900a14455394e79c31126645521702940c97"
SOURCE_SCHEDULE = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-fresh3-source-schedule-20260903.json"
SOURCE_SCHEDULE_SHA = "2e78838a46b3a37c09e07e2f0abdf0d9eb82d271e53d91245a41306d0e5b273f"
Q05 = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q05-downstream-budget-closure-20260903.json"
Q05_SHA = "5ed5205f5b68aa2f5ab6f7a254509335e13b46378204bef8ba97568be4b67b51"
Q06 = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-atomgit-qwen38-q06-downstream-estimand-closure-20260903.json"
Q06_SHA = "31e8dc0e5ce4c280ba0331c9e18861b4223641ad5beb866a31e761c0e6862e2c"
ORIGINAL_P0 = ROOT / "paper_drafts/c1-manuscript-strengthening-20260825/c1-pacta-msr-qwen397-p0-execution-contract-20260902.json"
ORIGINAL_P0_SHA = "5bc3daf779dd7facd45881080d846ccdf847814fecc6150e8b0d4fcc0db46f32"
RUNTIME = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh3-runtime-20260903-v2/normalization-qualification.json")
RUNTIME_SHA = "85d294f49d389601c10042fb0fd11096c82c93ddb2f0571ccd955f031937a5fe"
SOURCE_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh3-source-20260903-v2")
DEFAULT = Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh3-p0-20260903-v1")
SHADOW_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH3-DUAL-SHADOW-v1"
FINAL_SALT = "C1-PACTA-MSR-ATOMGIT-QWEN38-FRESH3-FINAL-v1"
SELECTORS = ("G0_STEP0", "GPLUS_MATCHED_REVEAL")
BRANCHES = ("success", "failure")


def verify_static() -> dict[str, str]:
    rows = (
        (POOL, POOL_SHA, "pool"), (SPLIT, SPLIT_SHA, "split"), (PROBES, PROBES_SHA, "probes"),
        (SOURCE_SCHEDULE, SOURCE_SCHEDULE_SHA, "source schedule"), (Q05, Q05_SHA, "q05"),
        (Q06, Q06_SHA, "q06"), (ORIGINAL_P0, ORIGINAL_P0_SHA, "original p0"),
        (RUNTIME, RUNTIME_SHA, "runtime"),
    )
    observed = {}
    for path, expected, label in rows:
        if not path.is_file() or sha256_file(path) != expected:
            raise RuntimeError("STOP_Q07_STATIC_HASH_DRIFT:" + label)
        observed[label] = expected
    pool = load(POOL); split = load(SPLIT); probes = load(PROBES); runtime = load(RUNTIME)
    q05 = load(Q05); q06 = load(Q06)
    if pool.get("status") != "FRESH3_PAIR_POOL_FROZEN_PRE_PROVIDER" or pool.get("candidate_count") != 10:
        raise RuntimeError("STOP_Q07_POOL_DRIFT")
    if split.get("status") != "FRESH3_PILOT_SPLIT_FROZEN_PRE_PROVIDER" or len(split.get("pilot") or []) != 8 or len(split.get("sealed") or []) != 2:
        raise RuntimeError("STOP_Q07_SPLIT_DRIFT")
    if probes.get("status") != "FRESH3_MSR_10_PROBE_COMMANDS_FROZEN_PRE_SOURCE_OUTCOME" or len(probes.get("rows") or []) != 10:
        raise RuntimeError("STOP_Q07_PROBE_DRIFT")
    if runtime.get("status") != "FRESH3_MSR_20_RUNTIME_READY_AFTER_TARGETED_BUILD_CLEAN" or runtime.get("source_qualified") != 10 or runtime.get("future_qualified") != 10:
        raise RuntimeError("STOP_Q07_RUNTIME_DRIFT")
    if q05.get("status") != "ATOMGIT_QWEN38_Q05_DOWNSTREAM_BUDGET_PASS" or q05.get("writer_selected_max_tokens") != 4096 or q05.get("binder_selected_max_tokens") != 2048:
        raise RuntimeError("STOP_Q07_Q05_DRIFT")
    if q06.get("status") != "ATOMGIT_QWEN38_Q06_DOWNSTREAM_ESTIMAND_PASS" or q06.get("selected_action_max_tokens") != 4096:
        raise RuntimeError("STOP_Q07_Q06_DRIFT")
    return observed


def source_support() -> dict[str, dict[str, Any]]:
    verify_static()
    audit_path = SOURCE_ROOT / "support-audit.json"
    if not audit_path.is_file():
        raise RuntimeError("HOLD_Q07_FRESH3_SOURCE_GATE_PENDING")
    audit = load(audit_path)
    if (
        audit.get("decision") != "FRESH3_ATOMGIT_MSR_SOURCE_POOL_10_QUALIFIED"
        or audit.get("attempted") != 10 or audit.get("valid") != 10
        or audit.get("valid_repositories") != 10 or audit.get("stop_reason") is not None
        or audit.get("replacement") is not False or audit.get("top_up") is not False
    ):
        raise RuntimeError("HOLD_Q07_FRESH3_SOURCE_GATE_NOT_10_OF_10")
    pool = load(POOL); by_source = {u["source_task_id"]: u for u in pool["units"]}; out = {}
    for row in audit.get("rows") or []:
        if row.get("validity_status") != "TRAJECTORY_BACKED_VALID" or row.get("failure_layer") is not None:
            raise RuntimeError("HOLD_Q07_INVALID_SOURCE_RECEIPT")
        unit = by_source.get(row.get("source_task_id"))
        if unit is None:
            raise RuntimeError("STOP_Q07_SOURCE_POOL_BINDING")
        trajectory = Path(row["source_trajectory_path"]); writer_input = Path(row["writer_input_trajectory_path"])
        if not trajectory.is_file() or sha256_file(trajectory) != row["source_trajectory_sha256"]:
            raise RuntimeError("STOP_Q07_SOURCE_TRAJECTORY_HASH_DRIFT")
        if not writer_input.is_file() or sha256_file(writer_input) != row["writer_input_trajectory_sha256"]:
            raise RuntimeError("STOP_Q07_WRITER_INPUT_HASH_DRIFT")
        out[unit["unit_id"]] = {**unit, "source_run": row}
    if len(out) != 10:
        raise RuntimeError("STOP_Q07_SOURCE_SUPPORT_GEOMETRY")
    return out


def pilot_units() -> tuple[list[dict[str, Any]], list[str], list[str]]:
    all_units = source_support(); split = load(SPLIT)
    pilot = list(split["pilot"]); sealed = list(split["sealed"]); ranking = list(split["random_ranking_pre_shadow"])
    if set(pilot) | set(sealed) != set(all_units) or set(pilot) & set(sealed) or set(ranking) != set(pilot):
        raise RuntimeError("STOP_Q07_SPLIT_BINDING")
    return [all_units[uid] for uid in pilot], sealed, ranking


def bound_probe_specs() -> dict[str, dict[str, Any]]:
    verify_static(); runtime = load(RUNTIME); probes = load(PROBES)
    future = {row["instance_id"]: row for row in runtime["rows"] if row.get("role") == "future" and row.get("exact_base_normalization_pass")}
    out = {}
    for row in probes["rows"]:
        rt = future.get(row["future_task_id"])
        if rt is None or rt.get("base_commit") != row["future_base_commit"]:
            raise RuntimeError("STOP_Q07_FUTURE_RUNTIME_BINDING")
        out[row["unit_id"]] = {**row, "future_digest_ref": rt["digest_ref"]}
    if len(out) != 10:
        raise RuntimeError("STOP_Q07_PROBE_BINDING_GEOMETRY")
    return out


def schedule_shadow(pilot_ids: list[str]) -> list[dict[str, Any]]:
    out = []
    for uid in pilot_ids:
        for selector in SELECTORS:
            for branch in BRANCHES:
                for block in (1, 2):
                    for replicate in range(1, 7):
                        case_id = f"{uid}__{selector}__{branch}__b{block}__r{replicate}"
                        out.append({"case_id": case_id, "unit_id": uid, "selector": selector, "branch": branch, "block": block, "replicate": replicate, "order_key": sha(SHADOW_SALT + "|" + case_id)})
    out.sort(key=lambda row: (row["order_key"], row["case_id"]))
    if len(out) != 384:
        raise AssertionError("Q07 shadow geometry")
    return out


def bind_legacy() -> None:
    legacy.Provider = qprov.Provider
    legacy.require_key = lambda: "ATOMGIT_LOCAL_OAUTH"
    legacy.pilot_units = pilot_units
    legacy.probe_specs = bound_probe_specs
    legacy.Container = Fresh3Container
    legacy.phase_usage = qprov.phase_usage
    legacy.SHADOW_SALT = SHADOW_SALT
    legacy.DEFAULT = DEFAULT
    legacy_final.Provider = qprov.Provider
    legacy_final.require_key = lambda: "ATOMGIT_LOCAL_OAUTH"
    legacy_final.pilot_units = pilot_units
    legacy_final.phase_usage = qprov.phase_usage
    legacy_final.SALT = FINAL_SALT
    legacy_final.DEFAULT = DEFAULT


def prepare(root: Path) -> dict[str, Any]:
    if root.exists():
        raise RuntimeError("Q07 root exists; no overwrite")
    hashes = verify_static(); root.mkdir(parents=True)
    split = load(SPLIT); pilot_ids = list(split["pilot"]); sealed = list(split["sealed"]); ranking = list(split["random_ranking_pre_shadow"])
    configs = qprov.write_configs(root)
    bound = bound_probe_specs()
    atomic_json(root / "bound-probe-specs.json", {"schema_version": 1, "status": "Q07_FRESH3_PROBE_RUNTIME_BOUND", "rows": list(bound.values()), "provider_calls": 0, "scientific_calls": 0})
    shadow = schedule_shadow(pilot_ids)
    atomic_bytes(root / "shadow-schedule.jsonl", "".join(json.dumps(row, sort_keys=True) + "\n" for row in shadow).encode())
    internal = {
        "schema_version": 1, "status": "Q07_FRESH3_P0_PREPARE_PASS",
        "execution_contract_sha256": sha256_file(CONTRACT), "static_hashes": hashes,
        "pilot": pilot_ids, "sealed": sealed, "random_ranking": ranking,
        "provider_config_sha256": configs, "bound_probe_specs_sha256": sha256_file(root / "bound-probe-specs.json"),
        "shadow_schedule_sha256": sha256_file(root / "shadow-schedule.jsonl"),
        "source_gate_at_prepare": "DEFERRED_MANDATORY_10_OF_10_BEFORE_ANY_PHASE",
        "writer_calls": 0, "binder_calls": 0, "probe_provider_calls": 0, "shadow_calls": 0, "final_calls": 0,
    }
    atomic_json(root / "contract.json", internal)
    result = {"schema_version": 1, "status": "Q07_FRESH3_P0_PREPARE_PASS", "contract_sha256": sha256_file(root / "contract.json"), "shadow_schedule_sha256": sha256_file(root / "shadow-schedule.jsonl"), "pilot_count": 8, "sealed_count": 2, "shadow_calls_planned": 384, "scientific_provider_calls": 0}
    atomic_json(root / "prepare-audit.json", result); return result


def run_phase(root: Path, phase: str) -> dict[str, Any]:
    if phase != "prepare":
        source_support()  # Mandatory revalidation before every downstream phase.
    bind_legacy()
    if phase == "prepare":
        return prepare(root)
    if not (root / "prepare-audit.json").is_file():
        raise RuntimeError("Q07 prepare first")
    if phase == "probe": return legacy.probe(root)
    if phase == "writer": return legacy.writer(root)
    if phase == "binder": return legacy.binder(root)
    if phase == "shadow": return legacy.shadow(root)
    if phase == "final": return legacy_final.final(root)
    raise ValueError(phase)


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, default=DEFAULT)
    parser.add_argument("--phase", choices=("prepare", "probe", "writer", "binder", "shadow", "final"), required=True)
    args = parser.parse_args(); print(json.dumps(run_phase(args.root, args.phase), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__": main()
