from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from research_pipeline.e2_r17_repair2_manifest import (
    ARMS,
    REPLICATES,
    load_json,
    require,
    sha_file,
    validate_compatibility_manifest,
    validate_quarantine,
)


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


def _validate_eval_manifest_v3(
    path: Path,
    expected_sha: str,
    heldout: set[str],
    *,
    skill_sha: str,
    receipt_sha: str,
    contract_sha: str | None,
    authorization_sha: str | None,
    require_scores_withheld: bool,
) -> None:
    require(path.is_file() and sha_file(path) == expected_sha, f"eval manifest SHA drift: {path}")
    rows = rows_by(path, "task_id")
    require(set(rows) == heldout, f"heldout set drift: {path}")
    for task_id, row in rows.items():
        summary_path = Path(row["summary_path"])
        require(summary_path.is_file() and sha_file(summary_path) == row["summary_sha256"], f"eval summary drift: {task_id}")
        summary = load_json(summary_path)
        require(summary.get("status") == "COMPLETED" and int(summary.get("k")) == 1, f"eval status/K drift: {task_id}")
        require(summary.get("skill_pre_sha256") == skill_sha, f"eval skill drift: {task_id}")
        require(summary.get("updater_receipt_sha256") == receipt_sha, f"eval receipt drift: {task_id}")
        if contract_sha is not None:
            require(summary.get("contract_sha256") == contract_sha, f"eval contract drift: {task_id}")
        if authorization_sha is not None:
            require(summary.get("authorization_sha256") == authorization_sha, f"eval authorization drift: {task_id}")
        tasks = summary.get("tasks") or []
        require(len(tasks) == 1 and str(tasks[0].get("task_id")) == task_id, f"eval task drift: {task_id}")
        if require_scores_withheld:
            require(tasks[0].get("scores_withheld_from_measurement_summary") is True, f"M1 score boundary drift: {task_id}")
        ref_path = Path(row["trajectory_ref_path"])
        require(ref_path.is_file() and sha_file(ref_path) == row["trajectory_ref_sha256"], f"trajectory ref drift: {task_id}")
        ref = load_json(ref_path)
        trajectory = Path(ref["trajectory_path"])
        require(trajectory.is_file() and sha_file(trajectory) == ref["trajectory_sha256"], f"trajectory drift: {task_id}")
        # Deliberately do not inspect ref["score"].


def validate_v3_compatibility_manifest(
    *,
    path: Path,
    expected_sha: str,
    repair1_contract_sha: str,
    repair1_authorization_sha: str,
    m1_contract_sha: str,
    m1_authorization_sha: str,
    m1_pass_path: Path,
    m1_pass_sha: str,
    heldout_task_ids: Iterable[str],
) -> list[dict[str, Any]]:
    require(path.is_file() and sha_file(path) == expected_sha, "V3 compatibility manifest SHA drift")
    payload = load_json(path)
    require(payload.get("status") == "PASS_REPAIR2_V3_PREFIX_COMPATIBILITY_15_COMPLETE_PAIRS", "V3 compatibility status drift")
    require(payload.get("scientific_scores_read") is False, "V3 compatibility read scientific scores")
    require(payload.get("partial_effect_read") is False and payload.get("analyzer_run") is False, "V3 outcome boundary drift")
    require(int(payload.get("inherited_pair_count")) == 15, "V3 inherited pair cardinality drift")
    require(int(payload.get("repair1_inherited_pair_count")) == 14, "V3 Repair1 count drift")
    require(int(payload.get("repair2_m1_recovered_pair_count")) == 1, "V3 M1 count drift")
    require(int(payload.get("remaining_fresh_pair_count")) == 33, "V3 remaining pair count drift")
    require(int(payload.get("remaining_new_learned_states")) == 66, "V3 remaining state count drift")
    require(int(payload.get("remaining_heldout_units")) == 1188, "V3 remaining heldout count drift")

    repair1_path = path.parents[1] / str(payload["repair1_compatibility_manifest_path"])
    repair1_rows = validate_compatibility_manifest(
        path=repair1_path,
        expected_sha=str(payload["repair1_compatibility_manifest_sha256"]),
        repair1_contract_sha=repair1_contract_sha,
        repair1_authorization_sha=repair1_authorization_sha,
        heldout_task_ids=heldout_task_ids,
    )
    require(m1_pass_path.is_file() and sha_file(m1_pass_path) == m1_pass_sha, "M1 PASS artifact drift")
    m1_pass = load_json(m1_pass_path)
    require(m1_pass.get("status") == "REPAIR2_M1_MEASUREMENT_RECOVERY_PASS_INTEGRITY_AUDITED", "M1 PASS status drift")
    require(m1_pass.get("partial_effect_read") is False and m1_pass.get("analyzer_run") is False, "M1 PASS outcome boundary drift")
    require(m1_pass.get("contract_sha256") == m1_contract_sha, "M1 contract binding drift")
    require(m1_pass.get("authorization_sha256") == m1_authorization_sha, "M1 authorization binding drift")

    rows = payload.get("inherited_rows") or []
    require(len(rows) == 15 and len({str(row["unit_id"]) for row in rows}) == 15, "V3 inherited rows drift")
    repair1_expected = {str(row["unit_id"]): row for row in repair1_rows}
    repair1_actual = {str(row["unit_id"]): row for row in rows if row.get("source") == "repair1_inherited"}
    require(repair1_actual == repair1_expected, "V3 Repair1 inherited rows differ from original compatibility audit")
    recovered = [row for row in rows if row.get("source") == "repair2_m1_recovered"]
    require(len(recovered) == 1, "V3 must contain exactly one M1 recovered row")
    row = recovered[0]
    require(row.get("unit_id") == "e1-fmv-01/rep2" and row.get("stream_id") == "e1-fmv-01" and int(row.get("replicate_id")) == 2, "M1 recovered unit drift")
    pair_summary = path.parents[1] / str(payload["repair2_m1_pair_summary_path"])
    require(pair_summary.is_file() and sha_file(pair_summary) == payload["repair2_m1_pair_summary_sha256"], "M1 pair summary drift")
    pair = load_json(pair_summary)
    require(pair.get("status") == "COMPLETED" and pair.get("unit_id") == row["unit_id"], "M1 pair summary invalid")
    require(pair.get("partial_effect_read") is False and pair.get("analyzer_run") is False, "M1 pair summary outcome boundary drift")
    heldout = set(map(str, heldout_task_ids))
    for arm in ARMS:
        state = row["arms"][arm]
        receipt = Path(state["update_receipt_path"])
        skill = Path(state["state_root"]) / "update/skill_post/SKILL.md"
        require(receipt.is_file() and sha_file(receipt) == state["update_receipt_sha256"], f"M1 receipt drift: {arm}")
        require(skill.is_file() and sha_file(skill) == state["skill_sha256"], f"M1 skill drift: {arm}")
        receipt_payload = load_json(receipt)
        require(receipt_payload.get("contract_sha256") == "9e38bdbfc71186e3e58587169d8c619bff4ae24de4145fefafa63e49a6f148a3", f"M1 parent receipt contract drift: {arm}")
        require(receipt_payload.get("authorization_sha256") == "9643a0a30d0acc4f32607b217701b368a895b2fe1e86a0aa84da24aa0a80898b", f"M1 parent receipt authorization drift: {arm}")
        require(int(state.get("updater_calls")) == 10 and state.get("attempt0_success") is True and state.get("correction_required") is False, f"M1 updater prefix drift: {arm}")
        _validate_eval_manifest_v3(
            Path(state["eval_manifest_path"]),
            str(state["eval_manifest_sha256"]),
            heldout,
            skill_sha=str(state["skill_sha256"]),
            receipt_sha=str(state["update_receipt_sha256"]),
            contract_sha=m1_contract_sha,
            authorization_sha=m1_authorization_sha,
            require_scores_withheld=True,
        )
    return sorted(rows, key=lambda item: (str(item["stream_id"]), int(item["replicate_id"])))


def validate_valid_rows_v3(
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
    source_counts: Counter[str] = Counter()
    for row in rows:
        unit_id = str(row["unit_id"])
        require(unit_id not in seen, f"duplicate valid pair: {unit_id}")
        seen.add(unit_id)
        stream = str(row["stream_id"])
        replicate = int(row["replicate_id"])
        source = str(row.get("source"))
        require(stream in expected_streams and replicate in REPLICATES, f"out-of-design pair: {unit_id}")
        require(unit_id == f"{stream}/rep{replicate}", f"unit id mismatch: {unit_id}")
        require(source in {"repair1_inherited", "repair2_m1_recovered", "repair2_v3_fresh"}, f"invalid V3 source: {unit_id}")
        if unit_id == quarantine_unit:
            require(source == "repair2_m1_recovered", "quarantined Repair1 unit may enter V3 only through audited M1 recovery")
        elif source == "repair2_m1_recovered":
            raise RuntimeError("M1 recovery source attached to wrong unit")
        arms = row.get("arms") or {}
        require(set(arms) == set(ARMS), f"incomplete pair: {unit_id}")
        for arm in ARMS:
            require(str(arms[arm].get("state_root")) != quarantine_root, "quarantined Repair1 state cannot enter V3")
            require(all(arms[arm].get(key) for key in ("skill_sha256", "update_receipt_sha256", "eval_manifest_path", "eval_manifest_sha256")), f"incomplete arm binding: {unit_id}/{arm}")
        source_counts[source] += 1
        counts[stream] += 1
    if require_complete:
        require(len(rows) == 48, "V3 valid manifest must contain exactly 48 pairs")
        require(all(counts[stream] == 4 for stream in expected_streams), "V3 valid manifest must contain four pairs per stream")
        require(source_counts == Counter({"repair1_inherited": 14, "repair2_m1_recovered": 1, "repair2_v3_fresh": 33}), "V3 source counts drift")
