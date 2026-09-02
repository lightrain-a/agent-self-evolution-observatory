#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ARMS = ("win_c", "mrw")
CONTRACT_STATUS = "FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2"
AUTH_STATUS = "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION_V2"
SUMMARY_STATUS = "COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION"
AUDIT_STATUS = "PASS_REPAIR2_CONTINUATION_V2_FULL_INTEGRITY_READY_FOR_SINGLE_USE_ANALYSIS"
EXPECTED_SOURCES = Counter({
    "repair1_inherited": 14,
    "repair2_m1_recovered": 1,
    "repair2_v3_fresh": 13,
    "repair2_v3_pair29_recovered": 1,
    "repair2_continuation_v2_fresh": 19,
})
DUPLICATE_V1_ROOT = Path("/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-continuation-v1-20260831")
OLD_429_FAILURE = Path(
    "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-v3-20260831/"
    "states/e1-msp-01/replicate_0/win_c/checkpoints/eval_failure_r17-b4-ska-p8.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def rows_by(path: Path, key: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        value = str(row[key])
        require(value not in out, f"duplicate {key}={value}: {path}")
        out[value] = row
    return out


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    require(not path.exists(), f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def receipt_path(state_root: Path, arm: dict[str, Any]) -> Path:
    return Path(str(arm.get("update_receipt_path") or state_root / "update/update_receipt.json"))


def validate_v2_fresh_ledger(db: Path, contract_sha: str, auth_sha: str) -> int:
    require(db.is_file(), f"missing V2 provider ledger: {db}")
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        metadata = {str(k): str(v) for k, v in con.execute("SELECT key,value FROM metadata")}
        claims = [(str(unit), int(index)) for unit, index in con.execute("SELECT unit_id,unit_call_index FROM claims")]
    finally:
        con.close()
    require(metadata.get("contract_sha256") == contract_sha, f"V2 ledger contract drift: {db}")
    require(metadata.get("authorization_sha256") == auth_sha, f"V2 ledger authorization drift: {db}")
    require(int(metadata.get("total_limit", -1)) == 191, f"V2 ledger total-limit drift: {db}")
    require(int(metadata.get("per_unit_limit", -1)) == 11, f"V2 ledger per-unit-limit drift: {db}")
    require(len(claims) == len(set(claims)), f"duplicate V2 provider claim: {db}")
    counts = Counter(unit for unit, _ in claims)
    require(all(v <= 11 for v in counts.values()), f"V2 per-unit provider budget exceeded: {db}")
    for unit, count in counts.items():
        seq = sorted(index for claim_unit, index in claims if claim_unit == unit)
        require(seq == list(range(1, count + 1)), f"V2 non-contiguous claims: {db}/{unit}")
    return len(claims)


def validate_eval_row(
    *, unit_id: str, arm_name: str, task_id: str, row: dict[str, Any], arm: dict[str, Any], duplicate_refs: set[str]
) -> tuple[str, str]:
    summary_path = Path(str(row["summary_path"]))
    ref_path = Path(str(row["trajectory_ref_path"]))
    require(summary_path.is_file() and sha(summary_path) == row["summary_sha256"], f"eval summary SHA drift: {unit_id}/{arm_name}/{task_id}")
    require(ref_path.is_file() and sha(ref_path) == row["trajectory_ref_sha256"], f"trajectory-ref SHA drift: {unit_id}/{arm_name}/{task_id}")
    require(not under(summary_path, DUPLICATE_V1_ROOT), f"quarantined V1 summary admitted: {unit_id}/{arm_name}/{task_id}")
    require(not under(ref_path, DUPLICATE_V1_ROOT), f"quarantined V1 ref admitted: {unit_id}/{arm_name}/{task_id}")
    require(str(summary_path.resolve()) not in duplicate_refs, f"duplicate V1 summary path admitted: {summary_path}")

    summary = load(summary_path)
    require(summary.get("status") == "COMPLETED", f"eval status drift: {unit_id}/{arm_name}/{task_id}")
    require(int(summary.get("k", -1)) == 1, f"eval K drift: {unit_id}/{arm_name}/{task_id}")
    require(summary.get("skill_pre_sha256") == arm["skill_sha256"], f"eval skill binding drift: {unit_id}/{arm_name}/{task_id}")
    require(summary.get("updater_receipt_sha256") == arm["update_receipt_sha256"], f"eval updater-receipt binding drift: {unit_id}/{arm_name}/{task_id}")
    tasks = summary.get("tasks") or []
    require(len(tasks) == 1 and str(tasks[0].get("task_id")) == task_id, f"eval task binding drift: {unit_id}/{arm_name}/{task_id}")

    ref = load(ref_path)
    trajectory = Path(str(ref["trajectory_path"]))
    require(trajectory.is_file() and sha(trajectory) == ref["trajectory_sha256"], f"trajectory SHA drift: {unit_id}/{arm_name}/{task_id}")
    require(not under(trajectory, DUPLICATE_V1_ROOT), f"quarantined V1 trajectory admitted: {unit_id}/{arm_name}/{task_id}")
    # Deliberately do not access ref['score'] or trajectory scientific outcome fields.
    return str(summary_path.resolve()), str(trajectory.resolve())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--authorization", type=Path, required=True)
    ap.add_argument("--run-summary", type=Path, required=True)
    ap.add_argument("--inheritance", type=Path, required=True)
    ap.add_argument("--remaining", type=Path, required=True)
    ap.add_argument("--pia-canonical", type=Path, required=True)
    ap.add_argument("--pia-quarantine", type=Path, required=True)
    ap.add_argument("--pair29-pass", type=Path, required=True)
    ap.add_argument("--lease", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--analysis-output", type=Path)
    args = ap.parse_args()
    require(not args.output.exists(), "final integrity audit already exists")
    if args.analysis_output:
        require(not args.analysis_output.exists(), "analysis output exists before final integrity audit")

    contract = load(args.contract)
    auth = load(args.authorization)
    summary = load(args.run_summary)
    inheritance = load(args.inheritance)
    remaining = load(args.remaining)
    pia = load(args.pia_canonical)
    quarantine = load(args.pia_quarantine)
    pair29 = load(args.pair29_pass)
    lease = load(args.lease)
    contract_sha, auth_sha = sha(args.contract), sha(args.authorization)

    require(contract.get("status") == CONTRACT_STATUS, "V2 contract status drift")
    require(auth.get("status") == AUTH_STATUS, "V2 authorization status drift")
    require(auth.get("contract_sha256") == contract_sha, "V2 authorization/contract drift")
    require((auth.get("authority") or {}).get("analyzer") is False, "execution authorization unexpectedly permits analyzer")
    require(summary.get("status") == SUMMARY_STATUS, "V2 terminal summary missing/incomplete")
    require(summary.get("contract_sha256") == contract_sha and summary.get("authorization_sha256") == auth_sha, "V2 terminal summary binding drift")
    require(summary.get("inference_performed") is False, "V2 runner performed scientific inference")
    require(summary.get("paper_promotion_authority") is False, "V2 runner had paper-promotion authority")
    require(int(summary.get("paired_replicate_units", -1)) == 48, "pair cardinality drift")
    require(int(summary.get("learned_states", -1)) == 96, "learned-state cardinality drift")
    require(int(summary.get("heldout_rollout_units", -1)) == 1728, "heldout cardinality drift")
    require(int(summary.get("inherited_paired_units", -1)) == 29 and int(summary.get("fresh_paired_units", -1)) == 19, "29+19 provenance cardinality drift")

    require(inheritance.get("status") == "PASS_CONTINUATION_V2_CANONICAL_INHERITANCE_29_PAIRS", "inheritance not passing")
    require(sha(args.inheritance) == "9c55423ae7683a910e1c500cc72ae7e82f1f480a3ea6b1f04d341f7b045867ef", "inheritance SHA drift")
    require(remaining.get("status") == "PASS_CONTINUATION_V2_REMAINING_SET_19_PAIRS", "remaining set not passing")
    require(sha(args.remaining) == "50eede0b3d8459b6f598dad6c9cd9d2efcdee1647a2a491ae683251698203878", "remaining-set SHA drift")
    require(pia.get("status") == "PIA1_PASS_V3_RESUME_CANONICAL_LINEAGE", "PIA canonical lineage not passing")
    require(quarantine.get("status") == "PERMANENTLY_QUARANTINED_DUPLICATE_CONTINUATION_V1", "duplicate V1 not permanently quarantined")
    require(quarantine.get("scientific_inclusion") is False and quarantine.get("analysis") == "forbidden", "duplicate V1 quarantine semantics drift")
    require(int(quarantine.get("duplicate_heldout_evaluations", -1)) == 12, "duplicate V1 count drift")
    require(pair29.get("status") == "PAIR29_MEASUREMENT_RECOVERY_PASS", "pair29 recovery not passing")
    require(int(pair29.get("new_updater_calls", -1)) == 0 and int(pair29.get("new_heldout_evaluations", -1)) == 7, "pair29 recovery cardinality drift")
    require(int(pair29.get("unique_429_logical_unit_recoveries", -1)) == 1, "pair29 429 recovery count drift")
    require(pair29.get("partial_effect_read") is False and pair29.get("analyzer_run") is False, "pair29 recovery crossed effect boundary")

    require(lease.get("status") == "COMPLETED_CONTINUATION_V2", "global lineage lease not terminal-complete")
    require(lease.get("contract_sha256") == contract_sha and lease.get("authorization_sha256") == auth_sha, "lease binding drift")
    require(lease.get("exactly_once") is True and lease.get("partial_effect_read") is False, "lease exactly-once/effect boundary drift")
    require(lease.get("lineage_inheritance_manifest_sha256") == sha(args.inheritance), "lease inheritance drift")
    require(lease.get("remaining_set_manifest_sha256") == sha(args.remaining), "lease remaining-set drift")
    require(lease.get("pair29_recovery_pass_sha256") == sha(args.pair29_pass), "lease pair29-recovery drift")

    valid_path = Path(str(summary["valid_replicate_manifest"]))
    completed_path = Path(str(summary["completed_replicate_manifest"]))
    require(valid_path.is_file() and sha(valid_path) == summary["valid_replicate_manifest_sha256"], "valid manifest SHA drift")
    require(completed_path.is_file() and sha(completed_path) == summary["completed_replicate_manifest_sha256"], "completed manifest SHA drift")
    valid = rows_by(valid_path, "unit_id")
    completed = rows_by(completed_path, "unit_id")
    require(len(valid) == len(completed) == 48 and set(valid) == set(completed), "completed/valid unit-set mismatch")

    expected_units = [f"{stream}/rep{rep}" for stream in contract["streams"] for rep in range(4)]
    require(set(valid) == set(expected_units), "48-unit design set drift")
    source_counts = Counter(str(row["source"]) for row in valid.values())
    require(source_counts == EXPECTED_SOURCES, f"source provenance drift: {source_counts}")

    inherited_rows = {str(row["unit_id"]): row for row in inheritance["valid_rows"]}
    require(len(inherited_rows) == 29, "inheritance row count drift")
    for unit_id, row in inherited_rows.items():
        require(valid.get(unit_id) == row, f"inherited canonical row mutated in V2 manifest: {unit_id}")
    remaining_units = [str(x) for x in remaining["remaining_units"]]
    require(len(remaining_units) == 19, "remaining unit count drift")
    require(set(remaining_units) == {u for u, r in valid.items() if r["source"] == "repair2_continuation_v2_fresh"}, "V2 fresh unit set drift")

    duplicate_refs = {str(Path(str(row["child_summary_path"])).resolve()) for row in quarantine["duplicate_rows"]}
    heldout = {str(x) for x in contract["heldout"]["task_ids"]}
    logical_measurements: set[tuple[str, str, str]] = set()
    state_keys: set[tuple[str, str]] = set()
    admitted_summaries: set[str] = set()
    admitted_trajectories: set[str] = set()
    v2_provider_claims = 0
    v2_ledgers = 0

    for unit_id in expected_units:
        row = valid[unit_id]
        pair_summary = Path(str(row["pair_summary_path"]))
        require(pair_summary.is_file() and sha(pair_summary) == row["pair_summary_sha256"], f"pair summary SHA drift: {unit_id}")
        require(not under(pair_summary, DUPLICATE_V1_ROOT), f"quarantined V1 pair summary admitted: {unit_id}")
        for arm_name in ARMS:
            key = (unit_id, arm_name)
            require(key not in state_keys, f"duplicate state key: {key}")
            state_keys.add(key)
            arm = row["arms"][arm_name]
            state_root = Path(str(arm["state_root"]))
            skill = state_root / "update/skill_post/SKILL.md"
            receipt = receipt_path(state_root, arm)
            require(skill.is_file() and sha(skill) == arm["skill_sha256"], f"skill SHA drift: {unit_id}/{arm_name}")
            require(receipt.is_file() and sha(receipt) == arm["update_receipt_sha256"], f"update receipt SHA drift: {unit_id}/{arm_name}")
            require(int(arm["updater_calls"]) in (10, 11), f"updater call count outside frozen path: {unit_id}/{arm_name}")
            require((int(arm["updater_calls"]) == 11) == bool(arm.get("correction_required")), f"correction flag mismatch: {unit_id}/{arm_name}")

            eval_manifest = Path(str(arm["eval_manifest_path"]))
            require(eval_manifest.is_file() and sha(eval_manifest) == arm["eval_manifest_sha256"], f"eval manifest SHA drift: {unit_id}/{arm_name}")
            require(not under(eval_manifest, DUPLICATE_V1_ROOT), f"quarantined V1 eval manifest admitted: {unit_id}/{arm_name}")
            eval_rows = rows_by(eval_manifest, "task_id")
            require(set(eval_rows) == heldout and len(eval_rows) == 18, f"heldout set drift: {unit_id}/{arm_name}")
            for task_id, erow in eval_rows.items():
                logical = (unit_id, arm_name, task_id)
                require(logical not in logical_measurements, f"duplicate scientific logical measurement: {logical}")
                logical_measurements.add(logical)
                s, t = validate_eval_row(unit_id=unit_id, arm_name=arm_name, task_id=task_id, row=erow, arm=arm, duplicate_refs=duplicate_refs)
                require(s not in admitted_summaries, f"same eval summary admitted twice: {s}")
                admitted_summaries.add(s)
                admitted_trajectories.add(t)

            if row["source"] == "repair2_continuation_v2_fresh":
                v2_provider_claims += validate_v2_fresh_ledger(state_root / "checkpoints/provider_budget.sqlite3", contract_sha, auth_sha)
                v2_ledgers += 1

    require(len(state_keys) == 96, "state cardinality drift after artifact audit")
    require(len(logical_measurements) == 1728, "logical heldout cardinality drift after artifact audit")
    require(len(admitted_summaries) == 1728, "eval-summary uniqueness drift")
    require(v2_ledgers == 38, "V2 fresh provider-ledger count drift")

    # Pair29's failed mid-trajectory attempt must remain evidence-only; the final admitted
    # ska-p8 WIN-C measurement must point to the dedicated recovery run, never the old V3 failure directory.
    require(OLD_429_FAILURE.is_file(), "old 429 technical failure evidence missing")
    pair29_row = valid["e1-msp-01/rep0"]
    p29_win = rows_by(Path(pair29_row["arms"]["win_c"]["eval_manifest_path"]), "task_id")["r17-b4-ska-p8"]
    require("deepseek-v2-repair2-pair29-recovery-m1-20260901" in str(p29_win["summary_path"]), "recovered 429 unit is not bound to recovery root")
    require(not under(Path(str(p29_win["summary_path"])), OLD_429_FAILURE.parent.parent), "old 429 partial attempt admitted")

    # V2 run itself must be technically clean. Historical canonical roots can contain sealed
    # failure evidence, so do not use directory-wide discovery outside this run root.
    v2_run_root = Path(str(contract["run_root"]))
    require(not list(v2_run_root.rglob("*failure*.json")), "V2 fresh run contains failure artifacts")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-continuation-v2-final-integrity-audit",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": AUDIT_STATUS,
        "contract_path": str(args.contract),
        "contract_sha256": contract_sha,
        "execution_authorization_path": str(args.authorization),
        "execution_authorization_sha256": auth_sha,
        "run_summary_path": str(args.run_summary),
        "run_summary_sha256": sha(args.run_summary),
        "valid_replicate_manifest_path": str(valid_path),
        "valid_replicate_manifest_sha256": sha(valid_path),
        "completed_replicate_manifest_path": str(completed_path),
        "completed_replicate_manifest_sha256": sha(completed_path),
        "paired_replicate_units": 48,
        "learned_states": 96,
        "heldout_rollout_units": 1728,
        "source_pair_counts": dict(source_counts),
        "inheritance_rows_exact_match": True,
        "remaining_19_exact_match": True,
        "duplicate_v1_excluded": True,
        "duplicate_v1_heldout_evaluations_quarantined": 12,
        "old_429_partial_attempt_excluded": True,
        "pair29_recovery_admitted": True,
        "global_lineage_lease_terminal_status": lease["status"],
        "global_lineage_exactly_once": True,
        "v2_fresh_provider_ledgers": v2_ledgers,
        "v2_fresh_provider_claims": v2_provider_claims,
        "provider_budget_binding_pass": True,
        "scientific_scores_read": False,
        "partial_effect_read": False,
        "analyzer_run": False,
        "authority": {
            "mint_single_use_analysis_authorization": True,
            "scientific_execution": False,
            "provider_io": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
        },
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
