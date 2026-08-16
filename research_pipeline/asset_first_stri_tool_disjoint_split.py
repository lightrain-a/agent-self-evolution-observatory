from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any

SALT = "STRI-TOOL-SPLIT-v1"
FOCAL_SPECIFIC = ("skill_003", "skill_004")
GENERIC = "skill_015"
FIVE_ATOMS = ("skill_003", "skill_004", "skill_015", "skill_003+skill_015", "skill_004+skill_015")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def pattern(row: dict[str, Any]) -> str:
    values = sorted(str(value) for value in row.get("accepted_skill_ids") or [])
    return "+".join(values) if values else "NONE"


def tool_hash(tool: str) -> str:
    return hashlib.sha256(f"{SALT}|{tool}".encode("utf-8")).hexdigest()


def build_split(rows: list[dict[str, Any]]) -> dict[str, Any]:
    level1 = [row for row in rows if int(row.get("level") or 0) == 1]
    by_tool: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    for row in level1:
        by_tool[str(row["tool"])][pattern(row)] += 1

    tool_roles: dict[str, str] = {}
    focal_tool_groups: dict[str, list[str]] = {}
    for specific in FOCAL_SPECIFIC:
        overlap = "+".join(sorted((specific, GENERIC)))
        eligible = sorted(
            [tool for tool, counts in by_tool.items() if counts[specific] > 0 and counts[overlap] > 0],
            key=lambda tool: tool_hash(tool),
        )
        if len(eligible) < 4:
            raise RuntimeError(f"fewer than four unique+overlap tools for {specific}: {eligible}")
        if len(eligible) % 2:
            raise RuntimeError(f"odd focal tool count for {specific}: {len(eligible)}")
        focal_tool_groups[specific] = eligible
        for index, tool in enumerate(eligible):
            role = "calibration" if index % 2 == 0 else "heldout"
            if tool in tool_roles and tool_roles[tool] != role:
                raise RuntimeError(f"tool assigned conflicting roles: {tool}")
            tool_roles[tool] = role

    selected_tools = set(tool_roles)
    selected_rows = [row for row in level1 if str(row["tool"]) in selected_tools]
    partitions: dict[str, dict[str, Any]] = {}
    for role in ("calibration", "heldout"):
        tools = sorted(tool for tool, assigned in tool_roles.items() if assigned == role)
        part_rows = [row for row in selected_rows if tool_roles[str(row["tool"])] == role]
        counts = collections.Counter(pattern(row) for row in part_rows)
        focal_counts = {atom: int(counts[atom]) for atom in FIVE_ATOMS}
        if any(value <= 0 for value in focal_counts.values()):
            raise RuntimeError(f"partition lacks a frozen semantic atom: {role}: {focal_counts}")
        witnesses = {}
        for specific in FOCAL_SPECIFIC:
            overlap = "+".join(sorted((specific, GENERIC)))
            witnesses[specific] = {
                "unique_rows": int(counts[specific]),
                "overlap_rows": int(counts[overlap]),
                "pass": counts[specific] > 0 and counts[overlap] > 0,
            }
        partitions[role] = {
            "tools": tools,
            "tool_hashes": {tool: tool_hash(tool) for tool in tools},
            "rows": len(part_rows),
            "row_ids": [f"L{int(row['level'])}:{int(row['index'])}:{row['tool']}" for row in part_rows],
            "five_atom_counts": focal_counts,
            "none_rows": int(counts["NONE"]),
            "other_pattern_counts": {
                key: int(value) for key, value in sorted(counts.items()) if key not in set(FIVE_ATOMS) | {"NONE"}
            },
            "mandatory_overlap_witnesses": witnesses,
        }

    if set(partitions["calibration"]["tools"]) & set(partitions["heldout"]["tools"]):
        raise RuntimeError("tool leakage between calibration and heldout")
    if set(partitions["calibration"]["row_ids"]) & set(partitions["heldout"]["row_ids"]):
        raise RuntimeError("row leakage between calibration and heldout")

    return {
        "schema_version": "1.0",
        "candidate_id": "skill-taxonomy-representation-invariance",
        "split_id": "STRI-API-BANK-L1-TOOL-DISJOINT-v1",
        "selection_rule": {
            "level": 1,
            "focal_specific_skills": list(FOCAL_SPECIFIC),
            "generic_skill": GENERIC,
            "eligible_tool_rule": "For each focal specific skill, include every Level-1 tool having at least one specific-only row and at least one specific+skill_015 overlap row under the frozen released validators.",
            "partition_rule": f"Within each focal-specific eligible-tool set, sort by SHA256('{SALT}|<tool>') and alternate calibration, heldout starting with calibration.",
            "selection_reads_model_or_method_outcomes": False,
            "selection_reads_p0_outcomes": False,
        },
        "level1_rows_total": len(level1),
        "selected_tools_total": len(selected_tools),
        "selected_rows_total": len(selected_rows),
        "focal_tool_groups_hash_order": focal_tool_groups,
        "partitions": partitions,
        "leakage_checks": {
            "tool_disjoint": True,
            "row_disjoint": True,
            "five_atoms_present_in_both": True,
            "two_mandatory_overlap_witnesses_present_in_both": True,
        },
        "scientific_role": "Leakage-safe method/full-experiment calibration versus heldout split. The earlier all-530-row phenomenon/theory audit remains valid descriptive evidence but must not be treated as heldout method evaluation.",
        "authority": {
            "paper_design": False,
            "method_execution": False,
            "p0": False,
            "gpu": False,
        },
        "scientific_authority": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--membership", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = build_split(load_jsonl(args.membership))
    result["membership_sha256"] = sha256(args.membership)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "split_id": result["split_id"],
        "calibration_tools": result["partitions"]["calibration"]["tools"],
        "heldout_tools": result["partitions"]["heldout"]["tools"],
        "calibration_atoms": result["partitions"]["calibration"]["five_atom_counts"],
        "heldout_atoms": result["partitions"]["heldout"]["five_atom_counts"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
