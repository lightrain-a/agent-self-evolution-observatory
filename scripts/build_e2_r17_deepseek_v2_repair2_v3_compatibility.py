#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_repair2_manifest import validate_compatibility_manifest

REPAIR1_COMPAT = ROOT / "generated/e2-r17-deepseek-v2-repair1-compatibility-manifest-20260831.json"
REPAIR1_CONTRACT_SHA = "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80"
REPAIR1_AUTH_SHA = "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5"
M1_CONTRACT = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-measurement-contract-v2-20260831.json"
M1_AUTH = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-single-use-authorization-20260831.json"
M1_PASS = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-measurement-recovery-pass-adjudication-20260831.json"
M1_RUN = Path("/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-m1-measurement-20260831")
M1_MANIFEST = M1_RUN / "checkpoints/completed_measurements.jsonl"
PAIR_SUMMARY = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-recovered-pair-summary-20260831.json"
COMBINED = ROOT / "generated/e2-r17-deepseek-v2-repair2-v3-compatibility-manifest-20260831.json"
EVAL_MANIFESTS = {
    "win_c": ROOT / "generated/e2-r17-deepseek-v2-repair2-v3-m1-win-c-eval-manifest-20260831.jsonl",
    "mrw": ROOT / "generated/e2-r17-deepseek-v2-repair2-v3-m1-mrw-eval-manifest-20260831.jsonl",
}


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_text(path: Path, content: str) -> None:
    require(not path.exists(), f"refusing to overwrite frozen artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(content, encoding="utf-8")
    temp.replace(path)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_text(path, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    m1_contract = load_json(M1_CONTRACT)
    m1_pass = load_json(M1_PASS)
    require(m1_pass.get("status") == "REPAIR2_M1_MEASUREMENT_RECOVERY_PASS_INTEGRITY_AUDITED", "M1 PASS gate missing")
    require(m1_pass.get("partial_effect_read") is False and m1_pass.get("analyzer_run") is False, "M1 outcome boundary drift")
    heldout = list(m1_contract["heldout"]["task_ids"])
    repair1_rows = validate_compatibility_manifest(
        path=REPAIR1_COMPAT,
        expected_sha=sha_file(REPAIR1_COMPAT),
        repair1_contract_sha=REPAIR1_CONTRACT_SHA,
        repair1_authorization_sha=REPAIR1_AUTH_SHA,
        heldout_task_ids=heldout,
    )
    require(len(repair1_rows) == 14, "Repair1 inherited prefix drift")
    m1_rows = [
        json.loads(line)
        for line in M1_MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    require(len(m1_rows) == 36, "M1 manifest cardinality drift")
    state_by_arm = {str(row["arm"]): row for row in m1_contract["learned_states"]}
    arm_bindings: dict[str, Any] = {}
    for arm in ("win_c", "mrw"):
        rows = sorted(
            (row for row in m1_rows if row.get("arm") == arm),
            key=lambda row: heldout.index(str(row["task_id"])),
        )
        require([str(row["task_id"]) for row in rows] == heldout, f"M1 heldout order/set drift: {arm}")
        eval_rows = []
        provider_calls = 0
        for row in rows:
            task_id = str(row["task_id"])
            summary_path = Path(row["summary_path"])
            require(summary_path.is_file() and sha_file(summary_path) == row["summary_sha256"], f"M1 summary drift: {arm}/{task_id}")
            summary = load_json(summary_path)
            require(summary.get("status") == "COMPLETED" and summary.get("k") == 1, f"M1 summary incomplete: {arm}/{task_id}")
            tasks = summary.get("tasks") or []
            require(len(tasks) == 1 and tasks[0].get("task_id") == task_id, f"M1 summary task drift: {arm}/{task_id}")
            require(tasks[0].get("scores_withheld_from_measurement_summary") is True, f"M1 summary score boundary drift: {arm}/{task_id}")
            provider_calls += int(tasks[0]["provider_calls"])
            ref = summary_path.parent / "cases" / task_id / "rollout_0" / "r17_trajectory_ref.json"
            require(ref.is_file(), f"M1 trajectory ref missing: {arm}/{task_id}")
            ref_payload = load_json(ref)
            trajectory = Path(ref_payload["trajectory_path"])
            require(trajectory.is_file() and sha_file(trajectory) == ref_payload["trajectory_sha256"], f"M1 trajectory drift: {arm}/{task_id}")
            eval_rows.append({
                "task_id": task_id,
                "summary_path": str(summary_path),
                "summary_sha256": sha_file(summary_path),
                "trajectory_ref_path": str(ref),
                "trajectory_ref_sha256": sha_file(ref),
                "source": "repair2_m1_recovered",
            })
        eval_manifest = EVAL_MANIFESTS[arm]
        atomic_text(
            eval_manifest,
            "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in eval_rows),
        )
        state = state_by_arm[arm]
        checkpoint = Path(state["update_completed_path"])
        checkpoint_payload = load_json(checkpoint)
        require(checkpoint_payload.get("provider_calls") == 10, f"M1 parent updater call count drift: {arm}")
        arm_bindings[arm] = {
            "state_root": str(Path(state["skill_post_path"]).parents[2]),
            "skill_sha256": state["skill_post_sha256"],
            "update_receipt_sha256": state["update_receipt_sha256"],
            "update_receipt_path": state["update_receipt_path"],
            "eval_manifest_path": str(eval_manifest),
            "eval_manifest_sha256": sha_file(eval_manifest),
            "updater_calls": 10,
            "attempt0_success": True,
            "correction_required": False,
            "measurement_provider_calls": provider_calls,
            "measurement_source_contract_sha256": sha_file(M1_CONTRACT),
            "measurement_source_authorization_sha256": sha_file(M1_AUTH),
        }

    pair = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-m1-recovered-paired-unit",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "COMPLETED",
        "unit_id": "e1-fmv-01/rep2",
        "stream_id": "e1-fmv-01",
        "replicate": 2,
        "source": "repair2_m1_recovered",
        "arms": arm_bindings,
        "heldout_task_ids": heldout,
        "new_updater_calls": 0,
        "replayed_updater_calls": 0,
        "partial_effect_read": False,
        "analyzer_run": False,
        "paper_promotion_authority": False,
    }
    atomic_json(PAIR_SUMMARY, pair)
    recovered_row = {
        "unit_id": "e1-fmv-01/rep2",
        "stream_id": "e1-fmv-01",
        "replicate_id": 2,
        "source": "repair2_m1_recovered",
        "pair_summary_path": str(PAIR_SUMMARY),
        "pair_summary_sha256": sha_file(PAIR_SUMMARY),
        "arms": arm_bindings,
    }
    inherited = sorted(
        [*repair1_rows, recovered_row],
        key=lambda row: (str(row["stream_id"]), int(row["replicate_id"])),
    )
    require(len(inherited) == 15 and len({row["unit_id"] for row in inherited}) == 15, "V3 inherited set drift")
    combined = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-v3-compatibility-manifest",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_REPAIR2_V3_PREFIX_COMPATIBILITY_15_COMPLETE_PAIRS",
        "scientific_scores_read": False,
        "partial_effect_read": False,
        "analyzer_run": False,
        "inherited_pair_count": 15,
        "repair1_inherited_pair_count": 14,
        "repair2_m1_recovered_pair_count": 1,
        "remaining_fresh_pair_count": 33,
        "remaining_new_learned_states": 66,
        "remaining_heldout_units": 1188,
        "repair1_compatibility_manifest_path": str(REPAIR1_COMPAT.relative_to(ROOT)),
        "repair1_compatibility_manifest_sha256": sha_file(REPAIR1_COMPAT),
        "repair2_m1_pass_path": str(M1_PASS.relative_to(ROOT)),
        "repair2_m1_pass_sha256": sha_file(M1_PASS),
        "repair2_m1_pair_summary_path": str(PAIR_SUMMARY.relative_to(ROOT)),
        "repair2_m1_pair_summary_sha256": sha_file(PAIR_SUMMARY),
        "inherited_rows": inherited,
        "authority": {
            "prepare_v3": True,
            "execute_v3": False,
            "run_analyzer": False,
            "read_partial_effect": False,
            "paper_promotion": False,
        },
    }
    atomic_json(COMBINED, combined)
    print(json.dumps({
        "status": combined["status"],
        "compatibility_manifest": str(COMBINED),
        "compatibility_manifest_sha256": sha_file(COMBINED),
        "pair_summary_sha256": sha_file(PAIR_SUMMARY),
        "eval_manifest_sha256": {arm: sha_file(path) for arm, path in EVAL_MANIFESTS.items()},
        "inherited_pairs": 15,
        "remaining_fresh_pairs": 33,
        "partial_effect_read": False,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
