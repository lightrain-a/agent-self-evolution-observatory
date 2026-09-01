from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

ARMS = ("win_c", "mrw")
REPLICATES = (0, 1, 2, 3)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rows_by(path: Path, key: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        value = str(row[key])
        require(value not in rows, f"duplicate {key}: {value}")
        rows[value] = row
    return rows


def _validate_eval_manifest(path: Path, expected_sha: str, heldout: set[str]) -> None:
    require(path.is_file() and sha_file(path) == expected_sha, f"eval manifest SHA drift: {path}")
    rows = rows_by(path, "task_id")
    require(set(rows) == heldout, f"heldout set drift: {path}")
    for task_id, row in rows.items():
        summary_path = Path(row["summary_path"])
        require(summary_path.is_file() and sha_file(summary_path) == row["summary_sha256"], f"eval summary drift: {task_id}")
        summary = load_json(summary_path)
        require(summary.get("status") == "COMPLETED" and int(summary.get("k")) == 1, f"eval status/K drift: {task_id}")
        ref_path = Path(row["trajectory_ref_path"])
        require(ref_path.is_file() and sha_file(ref_path) == row["trajectory_ref_sha256"], f"trajectory ref drift: {task_id}")
        ref = load_json(ref_path)
        trajectory = Path(ref["trajectory_path"])
        require(trajectory.is_file() and sha_file(trajectory) == ref["trajectory_sha256"], f"trajectory drift: {task_id}")
        # Deliberately do not read ref["score"] here. Inheritance is pre-outcome.


def validate_compatibility_manifest(
    *,
    path: Path,
    expected_sha: str,
    repair1_contract_sha: str,
    repair1_authorization_sha: str,
    heldout_task_ids: Iterable[str],
) -> list[dict[str, Any]]:
    require(path.is_file() and sha_file(path) == expected_sha, "compatibility manifest SHA drift")
    payload = load_json(path)
    require(payload.get("status") == "PASS_REPAIR1_PREFIX_COMPATIBILITY_14_COMPLETE_PAIRS", "compatibility status not PASS")
    require(payload.get("scientific_scores_read") is False, "compatibility audit read scientific scores")
    require(payload.get("repair1_contract_sha256") == repair1_contract_sha, "Repair1 contract binding drift")
    require(payload.get("repair1_authorization_sha256") == repair1_authorization_sha, "Repair1 authorization binding drift")
    pairs = payload.get("pairs") or []
    require(len(pairs) == 14 and int(payload.get("inherited_pair_count")) == 14, "inherited pair cardinality drift")
    heldout = set(map(str, heldout_task_ids))
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for pair in pairs:
        unit_id = str(pair["unit_id"])
        require(unit_id not in seen, f"duplicate inherited pair: {unit_id}")
        seen.add(unit_id)
        require(pair.get("source") == "inherited_repair1", f"inheritance source drift: {unit_id}")
        require(pair.get("prefix_compatibility") == "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL", f"prefix incompatibility: {unit_id}")
        summary_path = Path(pair["pair_summary_path"])
        require(summary_path.is_file() and sha_file(summary_path) == pair["pair_summary_sha256"], f"pair summary drift: {unit_id}")
        summary = load_json(summary_path)
        require(summary.get("status") == "COMPLETED" and summary.get("unit_id") == unit_id, f"pair summary invalid: {unit_id}")
        evidence_path = Path(pair["evidence_windows_path"])
        require(evidence_path.is_file() and sha_file(evidence_path) == pair["evidence_windows_sha256"], f"evidence window drift: {unit_id}")
        arms = pair.get("arms") or {}
        require(set(arms) == set(ARMS), f"paired arms missing: {unit_id}")
        out_arms: dict[str, Any] = {}
        for arm in ARMS:
            state = arms[arm]
            require(int(state.get("provider_calls")) == 10 and int(state.get("parse_errors")) == 0, f"non-prefix provider path: {unit_id}/{arm}")
            require(state.get("patch_apply_correction_required") is False, f"correction used in Repair1 prefix: {unit_id}/{arm}")
            checkpoint = Path(state["update_checkpoint_path"])
            receipt = Path(state["update_receipt_path"])
            skill = Path(state["skill_post_path"])
            require(checkpoint.is_file() and sha_file(checkpoint) == state["update_checkpoint_sha256"], f"update checkpoint drift: {unit_id}/{arm}")
            require(receipt.is_file() and sha_file(receipt) == state["update_receipt_sha256"], f"update receipt drift: {unit_id}/{arm}")
            require(skill.is_file() and sha_file(skill) == state["skill_post_sha256"], f"skill drift: {unit_id}/{arm}")
            receipt_payload = load_json(receipt)
            require(receipt_payload.get("contract_sha256") == repair1_contract_sha, f"receipt contract drift: {unit_id}/{arm}")
            require(receipt_payload.get("authorization_sha256") == repair1_authorization_sha, f"receipt auth drift: {unit_id}/{arm}")
            calls = state.get("provider_call_receipts") or []
            require(len(calls) == 10, f"nominal call count drift: {unit_id}/{arm}")
            require(all(c.get("provider_status") == "completed" and int(c.get("attempt")) == 0 and not c.get("parse_error") for c in calls), f"provider prefix drift: {unit_id}/{arm}")
            eval_path = Path(state["eval_manifest_path"])
            _validate_eval_manifest(eval_path, state["eval_manifest_sha256"], heldout)
            out_arms[arm] = {
                "state_root": state["state_root"],
                "skill_sha256": state["skill_post_sha256"],
                "update_receipt_sha256": state["update_receipt_sha256"],
                "eval_manifest_path": state["eval_manifest_path"],
                "eval_manifest_sha256": state["eval_manifest_sha256"],
                "updater_calls": 10,
                "attempt0_success": True,
                "correction_required": False,
            }
        rows.append({
            "unit_id": unit_id,
            "stream_id": str(pair["stream_id"]),
            "replicate_id": int(pair["replicate_id"]),
            "source": "repair1_inherited",
            "pair_summary_path": pair["pair_summary_path"],
            "pair_summary_sha256": pair["pair_summary_sha256"],
            "arms": out_arms,
        })
    return sorted(rows, key=lambda row: (row["stream_id"], row["replicate_id"]))


def validate_quarantine(path: Path, expected_sha: str) -> dict[str, Any]:
    require(path.is_file() and sha_file(path) == expected_sha, "quarantine SHA drift")
    payload = load_json(path)
    require(payload.get("status") == "TECHNICAL_QUARANTINE_UPDATER_PATCH_APPLY_FAILURE", "quarantine status drift")
    require(payload.get("provider_response_ambiguity") is False, "provider response incorrectly ambiguous")
    require(payload.get("scientific_pair_outcome_exists") is False, "quarantined scientific outcome exists")
    require(payload.get("single_arm_resume_authorized") is False, "single-arm resume must remain forbidden")
    require(payload.get("operator_semantic_patch_authorized") is False, "operator semantic patch must remain forbidden")
    return payload


def validate_valid_rows(
    rows: list[dict[str, Any]],
    *,
    streams: Iterable[str],
    quarantine: dict[str, Any],
    require_complete: bool,
) -> None:
    expected_streams = list(map(str, streams))
    seen: set[str] = set()
    counts: Counter[str] = Counter()
    quarantine_unit = f"{quarantine['stream_id']}/rep{int(quarantine['replicate_id'])}"
    quarantine_root = str(quarantine["state_root"])
    for row in rows:
        unit_id = str(row["unit_id"])
        require(unit_id not in seen, f"duplicate valid pair: {unit_id}")
        seen.add(unit_id)
        stream = str(row["stream_id"])
        replicate = int(row["replicate_id"])
        require(stream in expected_streams and replicate in REPLICATES, f"out-of-design pair: {unit_id}")
        require(unit_id == f"{stream}/rep{replicate}", f"unit id mismatch: {unit_id}")
        require(row.get("source") in {"repair1_inherited", "repair2_fresh"}, f"invalid source: {unit_id}")
        arms = row.get("arms") or {}
        require(set(arms) == set(ARMS), f"incomplete pair: {unit_id}")
        if row.get("source") == "repair1_inherited":
            require(unit_id != quarantine_unit, "quarantined pair cannot be inherited")
        for arm in ARMS:
            require(str(arms[arm].get("state_root")) != quarantine_root, "quarantined state cannot enter valid manifest")
            require(all(arms[arm].get(key) for key in ("skill_sha256", "update_receipt_sha256", "eval_manifest_path", "eval_manifest_sha256")), f"incomplete arm binding: {unit_id}/{arm}")
        counts[stream] += 1
    if require_complete:
        require(len(rows) == 48, "valid manifest must contain exactly 48 pairs")
        require(set(counts) == set(expected_streams), "valid manifest stream set drift")
        require(all(counts[stream] == 4 for stream in expected_streams), "valid manifest must contain exactly four pairs per stream")
