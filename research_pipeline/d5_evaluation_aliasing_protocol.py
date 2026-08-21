from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .d5_state_sufficiency_f0 import (
    ARMS,
    MEMORY_IDS,
    SOURCE_FAMILY,
    _read_jsonl,
    _sha_file,
    _stable_hash,
    _task_rel_id,
    historical_task_exposure,
    model_fingerprint,
)

EXPERIMENT_ID = "D5-EVALUATION-ALIASING-QWEN-v2"


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compile_contract(*, source_memories_path: Path, v1_contract_path: Path, historical_runs_root: Path,
                     alfworld_root: Path, alfworld_config: Path, model_path: Path) -> dict[str, Any]:
    memories = {str(row["memory_id"]): row for row in _read_jsonl(source_memories_path)}
    if any(mid not in memories for mid in MEMORY_IDS):
        raise ValueError("frozen memory missing")
    if any(str(memories[mid].get("source_family") or "") != SOURCE_FAMILY for mid in MEMORY_IDS):
        raise ValueError("frozen memory source-family mismatch")

    v1 = json.loads(v1_contract_path.read_text(encoding="utf-8"))
    selected = list((v1.get("task_selection") or {}).get("selected_tasks") or [])
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        by_family[str(row["target_family"])].append(row)
    families = tuple(sorted(by_family))
    if len(families) != 3 or any(len(by_family[f]) != 2 for f in families):
        raise ValueError(f"legacy frozen set is not 3 families x 2 tasks: { {f: len(by_family[f]) for f in families} }")
    for family in families:
        by_family[family].sort(key=lambda row: str(row["task_relpath"]))

    exposed = historical_task_exposure(historical_runs_root)
    frozen_paths = {_task_rel_id(row["task_relpath"]) for row in selected}
    leaked = sorted(frozen_paths & exposed)
    if leaked:
        raise ValueError(f"pre-frozen tasks acquired execution outcomes after v1 freeze: {leaked}")

    stage_a = [{"target_family": f, "task_relpath": _task_rel_id(by_family[f][0]["task_relpath"])} for f in families]
    stage_b = [{"target_family": f, "task_relpath": _task_rel_id(by_family[f][1]["task_relpath"])} for f in families]
    if {x["task_relpath"] for x in stage_a} & {x["task_relpath"] for x in stage_b}:
        raise ValueError("stage overlap")
    if any(not (alfworld_root / row["task_relpath"]).is_file() for row in stage_a + stage_b):
        raise FileNotFoundError("one or more frozen ALFWorld tasks are missing")

    frozen_memories = []
    for mid in MEMORY_IDS:
        row = memories[mid]
        text = str(row.get("text") or "")
        frozen_memories.append({
            "memory_id": mid,
            "source_family": SOURCE_FAMILY,
            "source_task_relpath": _task_rel_id(row.get("source_task_id") or ""),
            "memory_text_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "candidate_index": int(row.get("candidate_index") or 0),
            "candidate_role": str(row.get("candidate_role") or ""),
        })

    invalidation = Path("generated/d5-state-sufficiency-v1-invalidation.json")
    freeze_receipt = Path("generated/d5-state-sufficiency-v1-freeze-receipt.json")
    freeze = json.loads(freeze_receipt.read_text(encoding="utf-8"))
    if freeze.get("original_contract_file_sha256") != _sha_file(v1_contract_path):
        raise ValueError("legacy v1 private contract no longer matches the public freeze receipt")
    if freeze.get("original_contract_material_sha256") != v1.get("contract_sha256"):
        raise ValueError("legacy v1 material hash drift")
    material = {
        "schema_version": "1.0",
        "experiment_id": EXPERIMENT_ID,
        "status": "FROZEN_BEFORE_COMMON_PANEL_OUTCOMES",
        "working_term": "evaluation aliasing",
        "scientific_question": "Can distinct persistent memories be exactly indistinguishable on the same non-degenerate current evaluation panel yet have different future controlled transfer effects?",
        "claim_boundary": "Tests insufficiency of a finite observable evaluation signature as a behavioral state descriptor; does not claim history has an effect after byte-identical complete internal-state equality.",
        "frozen_history_object": {
            "source_family": SOURCE_FAMILY,
            "memory_ids": list(MEMORY_IDS),
            "selection_note": "The trio predates all Qwen-v2 common-panel outcomes. Legacy v1 equivalence is invalidated and contributes no support.",
            "memories": frozen_memories,
        },
        "stage_a": {
            "name": "COMMON_CURRENT_EVALUATION_QUALIFICATION",
            "tasks": stage_a,
            "episodes": len(stage_a) * len(MEMORY_IDS) * len(ARMS),
            "arms": list(ARMS),
            "pass_rule": "Every memory must have exactly the same (retrieved, placebo, no-memory) success triple on every identical task; no-memory success+actions must reproduce; the full common signature cannot be all-zero or all-one.",
            "failure_action": "STOP_QWEN_REALIZATION_WITHOUT_OPENING_STAGE_B",
        },
        "stage_b": {
            "name": "SEALED_FUTURE_ALIASING_TEST",
            "tasks": stage_b,
            "episodes": len(stage_b) * len(MEMORY_IDS) * len(ARMS),
            "arms": list(ARMS),
            "sealed_before_stage_a_outcomes": True,
            "unlock_requires_stage_a_pass": True,
            "controlled_delta": "retrieved_success-placebo_success",
            "go_min_divergent_tasks": 2,
            "go_min_divergent_target_families": 2,
            "go_requires_no_memory_success_and_actions_reproducible": True,
        },
        "task_selection": {
            "origin": "The six identities were frozen outcome-independently in D5-STATE-SUFFICIENCY-F0-v1 and have no execution-bearing outcomes in the historical run store.",
            "legacy_v1_freeze_receipt": str(freeze_receipt),
            "legacy_v1_freeze_receipt_sha256": _sha_file(freeze_receipt),
            "legacy_v1_private_contract_file_sha256": _sha_file(v1_contract_path),
            "legacy_v1_private_contract_material_sha256": v1.get("contract_sha256"),
            "split_rule": "Within each frozen family, lexicographically first task is Stage A and second is sealed Stage B.",
            "historical_exposed_task_count": len(exposed),
            "historical_exposure_sha256": _stable_hash(sorted(exposed)),
        },
        "runtime": {
            "alfworld_asset": "ALFWorld json_2.1.1 valid_unseen",
            "alfworld_config": str(alfworld_config),
            "alfworld_config_sha256": _sha_file(alfworld_config),
            "policy_mode": "react-family",
            "max_steps": 50,
            "decoding": "temperature=0",
            "placebo": "token-matched, absolute token-count gap <=1",
            "outcome_truth": "ALFWorld won/success; no LLM judge",
        },
        "model": {key: value for key, value in model_fingerprint(model_path, full_weights=False).items() if key != "path"},
        "source_artifacts": {
            "source_memories_asset": "p0-mem-xfer-support-enriched-qwen-v1/source-memories.jsonl",
            "source_memories_sha256": _sha_file(source_memories_path),
            "legacy_v1_invalidation": str(invalidation),
            "legacy_v1_invalidation_sha256": _sha_file(invalidation),
        },
        "authority": {"scientific": False, "paper_design": False, "canonical_gpu": False},
    }
    out = dict(material)
    out["contract_sha256"] = _stable_hash(material)
    out["created_at"] = _now()
    out["scientific_authority"] = False
    return out


def _no_memory_repro(rows: list[dict[str, Any]], task: str) -> bool:
    selected = [r for r in rows if r["task_relpath"] == task and r["arm"] == "no-memory"]
    return len(selected) == len(MEMORY_IDS) and len({(int(r["success"]), tuple(r.get("actions") or [])) for r in selected}) == 1


def analyze_stage_a(rows: list[dict[str, Any]], contract: dict[str, Any]) -> dict[str, Any]:
    expected = int(contract["stage_a"]["episodes"])
    by: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        by[(row["memory_id"], row["task_relpath"])][row["arm"]] = row
    details = []
    for spec in contract["stage_a"]["tasks"]:
        task = str(spec["task_relpath"])
        if any(set(by.get((mid, task), {})) != set(ARMS) for mid in MEMORY_IDS):
            continue
        triples = {}
        for mid in MEMORY_IDS:
            arms = by[(mid, task)]
            triples[mid] = (int(arms["retrieved"]["success"]), int(arms["placebo"]["success"]), int(arms["no-memory"]["success"]))
        equivalent = len(set(triples.values())) == 1
        reproducible = _no_memory_repro(rows, task)
        details.append({"task_relpath": task, "target_family": spec["target_family"], "triples": {k: list(v) for k, v in triples.items()}, "exact_score_equivalent": equivalent, "no_memory_reproducible": reproducible})
        if not equivalent or not reproducible:
            return {"schema_version": "1.0", "experiment_id": EXPERIMENT_ID, "stage": "A", "status": "EARLY_STOP_QUALIFICATION_FAILED", "rows": len(rows), "expected": expected, "tasks": details, "decision": "STOP_QWEN_REALIZATION_NO_COMMON_EVALUATION_EQUIVALENCE", "stage_b_authorized": False, "remaining_rows_not_required": expected - len(rows), "scientific_authority": False}
    if len(rows) != expected:
        return {"schema_version": "1.0", "experiment_id": EXPERIMENT_ID, "stage": "A", "status": "INCOMPLETE", "rows": len(rows), "expected": expected, "completed_tasks": len(details), "tasks": details, "scientific_authority": False}
    signature = [tuple(next(iter(row["triples"].values()))) for row in details]
    flat = [v for triple in signature for v in triple]
    nondegenerate = not (all(v == 0 for v in flat) or all(v == 1 for v in flat))
    return {"schema_version": "1.0", "experiment_id": EXPERIMENT_ID, "stage": "A", "status": "COMPLETE", "rows": len(rows), "tasks": details, "common_signature": [list(x) for x in signature], "nondegenerate": nondegenerate, "decision": "PASS_OPEN_SEALED_STAGE_B" if nondegenerate else "STOP_QWEN_REALIZATION_DEGENERATE_CURRENT_SIGNATURE", "stage_b_authorized": nondegenerate, "scientific_authority": False}


def analyze_stage_b(rows: list[dict[str, Any]], contract: dict[str, Any]) -> dict[str, Any]:
    expected = int(contract["stage_b"]["episodes"])
    if len(rows) != expected:
        return {"status": "INCOMPLETE", "rows": len(rows), "expected": expected, "scientific_authority": False}
    by: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        by[(row["memory_id"], row["task_relpath"])][row["arm"]] = row
    table = []
    reproducible = True
    for spec in contract["stage_b"]["tasks"]:
        task = str(spec["task_relpath"])
        deltas = {mid: int(by[(mid, task)]["retrieved"]["success"]) - int(by[(mid, task)]["placebo"]["success"]) for mid in MEMORY_IDS}
        n = _no_memory_repro(rows, task)
        reproducible &= n
        table.append({"task_relpath": task, "target_family": spec["target_family"], "controlled_deltas": deltas, "divergent": len(set(deltas.values())) > 1, "no_memory_reproducible": n})
    divergent = [row for row in table if row["divergent"]]
    families = sorted({row["target_family"] for row in divergent})
    gate = contract["stage_b"]
    passed = reproducible and len(divergent) >= int(gate["go_min_divergent_tasks"]) and len(families) >= int(gate["go_min_divergent_target_families"])
    return {"schema_version": "1.0", "experiment_id": EXPERIMENT_ID, "stage": "B", "status": "COMPLETE", "rows": len(rows), "effect_table": table, "divergent_task_count": len(divergent), "divergent_target_families": families, "decision": "GO_PROSPECTIVE_CONFIRMATION" if passed else "STOP_CURRENT_EVALUATION_ALIASING_PAPER_ON_QWEN", "paper_authorized": False, "scientific_authority": False}
