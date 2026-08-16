from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def projected_atom(record: dict[str, Any], relevant: set[str]) -> str:
    accepted = record.get("accepted_skill_ids")
    if not isinstance(accepted, list):
        return "INVALID"
    values = sorted(relevant & {str(value) for value in accepted})
    return "+".join(values) if values else "NONE"


def validate_inputs(contract: dict[str, Any], p0a_result: dict[str, Any], raw_path: Path) -> dict[str, Any]:
    errors = []
    if p0a_result.get("decision") != "DYNAMIC_PARTIAL_OVERLAP_REPRESENTATION_SENSITIVITY_SUPPORTED":
        errors.append("p0a-not-go")
    if p0a_result.get("protocol_valid_for_scientific_update") is not True:
        errors.append("p0a-protocol-not-valid")
    expected_sha = str(p0a_result.get("raw_sha256") or "")
    actual_sha = sha256(raw_path)
    if not expected_sha or expected_sha != actual_sha:
        errors.append("raw-sha-mismatch")
    rows = load_jsonl(raw_path)
    if len(rows) != 72:
        errors.append("raw-shape-not-72")
    source_ids = ["skill_003", "skill_004", "skill_015"]
    counts = collections.Counter(str(row.get("source_skill_id") or "") for row in rows)
    for source in source_ids:
        if counts[source] != 24:
            errors.append(f"source-count-{source}-{counts[source]}")
    schedule = (contract.get("online_rejection_protocol") or {}).get("target_schedule") or []
    if len(schedule) != 15:
        errors.append("target-schedule-not-15")
    return {"pass": not errors, "errors": errors, "actual_raw_sha256": actual_sha, "rows": rows}


def replay(contract: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    relevant = set(contract["semantic_projection"]["relevant_skill_ids"])
    streams: dict[str, list[dict[str, Any]]] = {source: [] for source in relevant}
    for row in rows:
        source = str(row.get("source_skill_id") or "")
        if source in streams:
            streams[source].append(row)
    for source in streams:
        streams[source].sort(key=lambda row: int(row.get("source_index") or 0))
        indices = [int(row.get("source_index") or 0) for row in streams[source]]
        if indices != list(range(24)):
            raise ValueError(f"source indices are not exactly 0..23: {source}: {indices}")

    pointer = {source: 0 for source in streams}
    rejection_reasons = collections.Counter()
    accepted = []
    failed_target = None
    schedule = contract["online_rejection_protocol"]["target_schedule"]
    for schedule_index, target in enumerate(schedule):
        source = str(target["source_skill_id"])
        target_atom = str(target["target_atom"])
        matched = False
        while pointer[source] < len(streams[source]):
            row = streams[source][pointer[source]]
            pointer[source] += 1
            atom = projected_atom(row, relevant)
            valid = isinstance(row.get("contract"), dict) and float((row.get("contract") or {}).get("contract_valid", 0.0)) >= 1.0
            if not valid:
                rejection_reasons["invalid_contract"] += 1
                continue
            if atom != target_atom:
                rejection_reasons[f"wrong_atom:{atom}"] += 1
                continue
            accepted.append({
                "schedule_index": schedule_index,
                "cycle": int(target["cycle"]),
                "target_atom": target_atom,
                "source_skill_id": source,
                "source_index": int(row["source_index"]),
                "tool_name": str(row.get("tool_name") or "UNKNOWN"),
            })
            matched = True
            break
        if not matched:
            failed_target = {
                "schedule_index": schedule_index,
                "cycle": int(target["cycle"]),
                "target_atom": target_atom,
                "source_skill_id": source,
                "source_calls_consumed": pointer[source],
            }
            break

    atom_counts = collections.Counter(item["target_atom"] for item in accepted)
    total_calls = sum(pointer.values())
    target_per_atom = int(contract["online_rejection_protocol"]["target_accepts_per_atom"])
    all_atoms = list(contract["semantic_projection"]["projected_atoms"])
    complete = (
        failed_target is None
        and len(accepted) == int(contract["online_rejection_protocol"]["target_accepts_total"])
        and all(atom_counts[atom] == target_per_atom for atom in all_atoms)
        and total_calls <= int(contract["online_rejection_protocol"]["maximum_total_consumed_calls"])
        and all(pointer[source] <= int(contract["online_rejection_protocol"]["maximum_calls_per_source"]) for source in pointer)
    )
    return {
        "decision": "QUOTIENT_REJECTION_LOCAL_FEASIBILITY_PASS" if complete else "STOP_QUOTIENT_REJECTION_LOCAL_FEASIBILITY",
        "complete": complete,
        "accepted_total": len(accepted),
        "accepted_per_atom": {atom: int(atom_counts[atom]) for atom in all_atoms},
        "calls_consumed_total": total_calls,
        "calls_consumed_by_source": {source: int(value) for source, value in pointer.items()},
        "accepted_tasks_per_consumed_call": len(accepted) / max(1, total_calls),
        "failed_target": failed_target,
        "rejection_reasons": dict(rejection_reasons),
        "accepted": accepted,
    }


def run(*, contract_path: Path, p0a_result_path: Path, raw_path: Path, output_path: Path) -> dict[str, Any]:
    contract = load_json(contract_path)
    p0a_result = load_json(p0a_result_path)
    validation = validate_inputs(contract, p0a_result, raw_path)
    if not validation["pass"]:
        result = {
            "schema_version": "1.0",
            "experiment_id": contract["experiment_id"],
            "candidate_id": contract["candidate_id"],
            "decision": "INVALID_P0B_INPUT_BINDING",
            "scientific_result_available": False,
            "input_validation": {key: value for key, value in validation.items() if key != "rows"},
            "new_model_calls": 0,
            "new_gpu_hours": 0,
            "method_authorized": False,
            "paper_design_authorized": False,
            "scientific_authority": False,
        }
    else:
        replay_result = replay(contract, validation["rows"])
        result = {
            "schema_version": "1.0",
            "experiment_id": contract["experiment_id"],
            "candidate_id": contract["candidate_id"],
            **replay_result,
            "scientific_result_available": True,
            "input_validation": {key: value for key, value in validation.items() if key != "rows"},
            "new_model_calls": 0,
            "new_gpu_hours": 0,
            "method_authorized": False,
            "paper_design_authorized": False,
            "scientific_authority": False,
            "next_action": contract["next_if_go"] if replay_result["complete"] else contract["next_if_stop"],
        }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--p0a-result", type=Path, required=True)
    ap.add_argument("--raw", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = run(contract_path=args.contract, p0a_result_path=args.p0a_result, raw_path=args.raw, output_path=args.output)
    print(json.dumps({"decision": result["decision"], "accepted_total": result.get("accepted_total"), "calls": result.get("calls_consumed_total")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
