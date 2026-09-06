from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import sha256_value

SELECTION_SALT = "ACE-REPEAT-DEVELOPMENT-SELECTION-20260906-V1"
DEV_PER_CATEGORY = 3
TOOL_CALL_CAP = 80


def binding(app: str, table: str, where: dict[str, Any], expected_fields=None, expected_count: int = 1) -> dict[str, Any]:
    return {
        "app": app,
        "table": table,
        "where": where,
        "expected_fields": expected_fields or {},
        "expected_count": expected_count,
    }


def select_case_ids(completions: list[dict[str, Any]]) -> tuple[list[str], list[dict[str, Any]]]:
    usable = [str(row["case_id"]) for row in completions if row.get("usable_target_failure") is True]
    ranked: dict[str, list[tuple[str, str]]] = {}
    for kind in ("FG", "TNF"):
        ranked[kind] = sorted(
            (hashlib.sha256(f"{SELECTION_SALT}|{cid}".encode()).hexdigest(), cid)
            for cid in usable if f"-{kind}-" in cid
        )
        if len(ranked[kind]) < DEV_PER_CATEGORY:
            raise RuntimeError(f"insufficient {kind} semantic failures")
    selected = [cid for _, cid in ranked["FG"][:3]] + [cid for _, cid in ranked["TNF"][:3]]
    audit = [
        {"category": kind, "case_id": cid, "rank_sha256": digest, "selected": cid in selected}
        for kind in ("FG", "TNF") for digest, cid in ranked[kind]
    ]
    if len(selected) != 6 or len(set(selected)) != 6:
        raise RuntimeError("development selection geometry drift")
    return selected, audit


def _one_file(case: dict[str, Any], filename: str) -> dict[str, Any]:
    rows = [
        row for row in case["fixture"]["rows"]
        if row["app"] == "file_system"
        and row["table"] == "files"
        and Path(str(row["values"].get("tilde_path", ""))).name == filename
    ]
    if len(rows) != 1:
        raise RuntimeError(f"expected exactly one {filename}")
    return rows[0]


def _dummy_name(target_name: str, tag: str) -> str:
    if not target_name.endswith(".txt"):
        raise RuntimeError("shared target file must be .txt")
    stem_len = len(target_name) - 4
    seed = f"spare-{tag}-neutral-preserve-marker"
    stem = (seed + "x" * stem_len)[:stem_len]
    name = stem + ".txt"
    if len(name.encode()) != len(target_name.encode()):
        raise RuntimeError("dummy filename length mismatch")
    return name


def _resource(row: dict[str, Any]) -> str:
    return f"file_system.files:{int(row['values']['id'])}"


def _preserve(fid: str, suffix: str, row: dict[str, Any]) -> dict[str, Any]:
    values = row["values"]
    resource = _resource(row)
    return {
        "constraint_id": f"{fid}-C-{suffix}",
        "role": "NON_TARGET",
        "semantic_description": "Preserve the designated file entity's content and path exactly.",
        "evaluator_binding": binding(
            "file_system", "files", {"id": int(values["id"])},
            {"path": str(values["path"]), "content": str(values.get("content", ""))},
        ),
        "affected_entities": [resource],
        "read_resources": [resource],
        "write_resources": [],
        "prerequisite_resources": [],
    }


def _target_binding(case: dict[str, Any]) -> dict[str, Any]:
    expected = case["expected"]
    if case["kind"].startswith("FG_"):
        return {
            "app": "gmail",
            "table": "emails",
            "where": {"sender_id": 99, "subject": expected["subject"]},
            "expected_fields": {},
            "expected_count": 1,
            "semantic_kind": "EMAIL_EXACT_RECIPIENT_BODY_ATTACHMENTS_V1",
            "semantic_expected": copy.deepcopy(expected),
        }
    return binding(
        "file_system", "files",
        {"tilde_path": expected["output_path"], "user_id": 99},
        {"content": expected["output_content"]},
    )


def _target(fid: str, case: dict[str, Any], shared_rows: list[dict[str, Any]]) -> dict[str, Any]:
    shared = [_resource(row) for row in shared_rows]
    if case["kind"].startswith("FG_"):
        description = "Resolve the frozen routing challenge and send exactly the required email with exact recipient, body, and attachments."
        writes = [f"gmail.email:{case['expected']['subject']}"]
    else:
        description = "Resolve the frozen routing challenge and create exactly the required output file."
        writes = [f"file_system.file:{case['expected']['output_path']}"]
    return {
        "constraint_id": f"{fid}-C-TARGET",
        "role": "TARGET",
        "semantic_description": description,
        "evaluator_binding": _target_binding(case),
        "affected_entities": [*shared, *writes],
        "read_resources": [*case.get("target_local_resources", []), *shared],
        "write_resources": writes,
        "prerequisite_resources": shared,
    }


def _arm(fid: str, level: str, target: dict[str, Any], nt1: dict[str, Any], nt2: dict[str, Any], source_instruction: str, path1: str, path2: str) -> dict[str, Any]:
    tr = set(target["read_resources"] + target["write_resources"] + target["prerequisite_resources"])
    edges: list[dict[str, Any]] = []
    exposure: set[str] = set()
    for nt in (nt1, nt2):
        nr = set(nt["read_resources"] + nt["write_resources"] + nt["prerequisite_resources"])
        shared = sorted(tr & nr)
        exposure.update(shared)
        if shared:
            edges.append({
                "source": nt["constraint_id"], "target": target["constraint_id"],
                "edge_type": "PREREQUISITE_DEPENDENCY", "resource_witnesses": shared,
                "outcome_blind": True,
            })
    return {
        "arm_id": f"{fid}-{level.lower()}", "coupling_level": level,
        "constraints": [copy.deepcopy(target), copy.deepcopy(nt1), copy.deepcopy(nt2)],
        "edges": edges,
        "structure": {
            "shared_resource_exposure_count": len(exposure),
            "motif": "DISCONNECTED" if not edges else ("SINGLE_EXPOSURE" if len(exposure) == 1 else "TWO_EXPOSURE"),
        },
        "matching": {
            "constraint_count": 3, "task_complexity": 6, "tool_budget": TOOL_CALL_CAP,
            "expected_task_length": 40, "instruction_template_budget": 1024,
            "update_surface": "PERSISTENT_PROCEDURAL_REPAIR_NOTE",
            "backbone_slot": "ATOMGIT_MIMO25PRO_FROZEN", "harness_slot": "ATOMCODE_APPWORLD_MCP_V1",
        },
        "task_instruction": source_instruction + f" Preserve {path1} and {path2} exactly.",
    }


def family_from_case(case: dict[str, Any], ordinal: int) -> dict[str, Any]:
    kind = "FG" if case["kind"].startswith("FG_") else "TNF"
    fid = f"ACE-DEV-{kind}-{ordinal:02d}"
    case = copy.deepcopy(case)
    case["fixture"] = copy.deepcopy(case["fixture"])
    target_names = ["dispatch-route.txt", "policy-b.txt"] if kind == "FG" else ["adjust-01.txt", "modifier-01.txt"]
    target_rows = [_one_file(case, name) for name in target_names]
    directory = str(target_rows[0]["values"]["tilde_path"]).rsplit("/", 1)[0]
    absolute = str(target_rows[0]["values"]["path"]).rsplit("/", 1)[0]
    dummy_rows: list[dict[str, Any]] = []
    for slot, target_row in enumerate(target_rows, start=1):
        target_name = Path(str(target_row["values"]["tilde_path"])).name
        dummy_name = _dummy_name(target_name, f"{kind.lower()}{slot}")
        dummy_rows.append({
            "app": "file_system", "table": "files",
            "values": {
                "id": 9_600_000 + ordinal * 20 + slot,
                "path": f"{absolute}/{dummy_name}", "tilde_path": f"{directory}/{dummy_name}",
                "user_id": 99, "content": f"ACE-DEV-DUMMY-{kind}-{ordinal:02d}-{slot}",
            },
        })
    case["fixture"]["rows"].extend(dummy_rows)
    for row in [*target_rows, *dummy_rows]:
        v = row["values"]
        case["fixture"].setdefault("initial_checks", []).append(
            binding("file_system", "files", {"id": int(v["id"])}, {"path": str(v["path"]), "content": str(v.get("content", ""))})
        )
    target_paths = [str(row["values"]["tilde_path"]) for row in target_rows]
    dummy_paths = [str(row["values"]["tilde_path"]) for row in dummy_rows]
    if any(len(a.encode()) != len(b.encode()) for a, b in zip(target_paths, dummy_paths, strict=True)):
        raise RuntimeError("target/dummy full-path byte matching drift")
    target = _target(fid, case, target_rows)
    target_nt = [_preserve(fid, f"NT-TARGET-{i}", row) for i, row in enumerate(target_rows, 1)]
    dummy_nt = [_preserve(fid, f"NT-DUMMY-{i}", row) for i, row in enumerate(dummy_rows, 1)]
    arms = [
        _arm(fid, "INDEPENDENT", target, dummy_nt[0], dummy_nt[1], case["task_instruction"], dummy_paths[0], dummy_paths[1]),
        _arm(fid, "LOW", target, target_nt[0], dummy_nt[1], case["task_instruction"], target_paths[0], dummy_paths[1]),
        _arm(fid, "HIGH", target, target_nt[0], target_nt[1], case["task_instruction"], target_paths[0], target_paths[1]),
    ]
    source_case = copy.deepcopy(case)
    source_case["case_id"] = f"{fid}-SOURCE"
    source_case["kind"] = f"{kind}_ATOMGIT_REPEAT_DEV_SOURCE_V1"
    family = {
        "family_id": fid, "category": "FILE_GMAIL" if kind == "FG" else "TODO_NOTE_FILE",
        "template_case_id": case["case_id"], "target_instruction": case["task_instruction"],
        "source_case": source_case,
        "update_interface": {
            "surface": "PERSISTENT_PROCEDURAL_REPAIR_NOTE",
            "injection_position": "SYSTEM_AFTER_BASE_POLICY_BEFORE_TASK",
            "exposure_rule": "UPDATE_ONLY_EXACT_BYTES", "repair_source_scope": "TARGET_FAILURE_ONLY",
            "non_target_outcomes_visible_to_updater": False, "human_edit_after_freeze": False,
        },
        "fixture": copy.deepcopy(case["fixture"]), "arms": arms,
        "residual_confounds": ["non_target_entity_identity", "resource_role_salience", "lexical_preserve_entity_identity"],
    }
    hashes = {sha256_value(next(c for c in arm["constraints"] if c["role"] == "TARGET")) for arm in arms}
    if len(hashes) != 1 or family["target_instruction"] != source_case["task_instruction"]:
        raise RuntimeError("source/probe target equivalence drift")
    return family
