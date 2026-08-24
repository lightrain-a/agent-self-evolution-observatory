from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION = ROOT / "generated/asset-first-stri-autoskill-multitask-qualification-20260824.json"
QUALIFICATION_CSV = ROOT / "generated/asset-first-stri-autoskill-multitask-qualification-20260824.csv"
CONTRACT = ROOT / "generated/asset-first-stri-autoskill-multitask-pilot-contract-20260824.json"
RUN_MANIFEST = ROOT / "generated/asset-first-stri-autoskill-multitask-pilot-run-manifest-20260824.json"
STAGE1 = ROOT / "generated/asset-first-stri-autoskill-multitask-pilot-stage1-20260824.json"
STAGE1_CSV = ROOT / "generated/asset-first-stri-autoskill-multitask-pilot-stage1-20260824.csv"
FAILURE = ROOT / "generated/asset-first-stri-autoskill-multitask-pilot-failure-lesson-20260824.json"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(path)
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _selected_by_contract_rule(qualification: dict[str, Any]) -> list[str]:
    units = [str(row["unit_id"]) for row in qualification["units"] if row.get("qualified") is True]
    ranked = sorted((hashlib.sha256(unit.encode()).hexdigest(), unit) for unit in units)
    first = ranked[0][1]
    first_episode, first_pos = first.rsplit("-P", 1)
    second = next(unit for _, unit in ranked[1:] if unit.rsplit("-P", 1)[0] != first_episode and unit.rsplit("-P", 1)[1] != first_pos)
    return [first, second]


def build(project_root: Path = ROOT) -> dict[str, Any]:
    q = _load(project_root / QUALIFICATION.relative_to(ROOT))
    c = _load(project_root / CONTRACT.relative_to(ROOT))
    m = _load(project_root / RUN_MANIFEST.relative_to(ROOT))
    s = _load(project_root / STAGE1.relative_to(ROOT))
    f = _load(project_root / FAILURE.relative_to(ROOT))
    with (project_root / STAGE1_CSV.relative_to(ROOT)).open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))

    selected = [str(row["unit_id"]) for row in c["selected_units"]]
    expected_selected = _selected_by_contract_rule(q)
    signatures = {uid: row["signatures"] for uid, row in s["per_unit"].items()}
    all_csv_valid = len(csv_rows) == 8 and all(str(row["execution_valid"]).lower() == "true" for row in csv_rows)
    summary = {
        "qualified_units": int(q["summary"]["qualified_units"]),
        "screened_units": int(q["summary"]["screened_units"]),
        "selection_outcome_blind": q.get("selection_outcome_blind") is True,
        "selected_units": selected,
        "selection_rule_recomputed": selected == expected_selected,
        "stage1_runs": int(s["runs_completed"]),
        "all_executions_valid": s.get("all_executions_valid") is True and m.get("all_valid") is True and all_csv_valid,
        "stage1_gate_pass": s.get("stage1_gate_pass") is True,
        "stage2_authorized": s.get("stage2_repeat_runs_authorized") is True,
        "remaining_units_authorized": s.get("remaining_seven_units_authorized") is True,
        "decision": s.get("decision"),
        "unit_diagnoses": {uid: row["diagnosis"] for uid, row in s["per_unit"].items()},
        "unit_signatures": signatures,
        "failure_stop_class": f.get("stop_class"),
        "new_agent_runs": int(s.get("new_agent_runs") or 0),
        "judge_calls": int(s.get("judge_calls") or 0),
        "new_gpu_runs": int(s.get("new_gpu_runs") or 0),
        "claim_expansion": s.get("claim_expansion") is True,
    }
    checks = {
        "qualification_9_of_9": summary["screened_units"] == 9 and summary["qualified_units"] == 9,
        "selection_outcome_blind": summary["selection_outcome_blind"],
        "selection_rule_exact": summary["selection_rule_recomputed"],
        "stage1_8_of_8_valid": summary["stage1_runs"] == 8 and summary["all_executions_valid"],
        "stage1_stop_exact": summary["decision"] == "STOP_EXPANSION_STAGE1_GATE_NOT_MET" and summary["stage1_gate_pass"] is False,
        "no_illegal_expansion": summary["stage2_authorized"] is False and summary["remaining_units_authorized"] is False,
        "unit_22_control_nonconcordance": summary["unit_diagnoses"].get("skillmisevo-coding-22-P21") == "CONTROL_NONCONCORDANCE_NO_SPLIT_SPECIFIC_ATTRIBUTION",
        "unit_21_no_separation": summary["unit_diagnoses"].get("skillmisevo-coding-21-P19") == "NO_ACTION_SIGNATURE_SEPARATION",
        "no_judge_or_gpu": summary["judge_calls"] == 0 and summary["new_gpu_runs"] == 0,
        "no_claim_expansion": summary["claim_expansion"] is False,
        "failure_asset_bound": f.get("memory_class") == "FAILURE_ASSET" and f.get("failure_layer") == "behavioral_replication",
    }
    if not all(checks.values()):
        raise RuntimeError({k: v for k, v in checks.items() if not v})
    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "analysis": "autoskill-multitask-behavior-pilot-stage1-verification",
        "summary": summary,
        "checks": checks,
        "source_sha256": {
            str(path.relative_to(ROOT)): _sha(path)
            for path in (QUALIFICATION, QUALIFICATION_CSV, CONTRACT, RUN_MANIFEST, STAGE1, STAGE1_CSV, FAILURE)
        },
        "scientific_boundary": "The 9/9 retrieval qualification is not behavior evidence. The preregistered held-out behavior pilot stopped after 8 valid runs because no unit met split-specific first-repeat separation. No repeat-2 or seven-unit expansion is authorized, and P19 remains a bounded existence proof.",
        "scientific_authority": False,
    }


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
