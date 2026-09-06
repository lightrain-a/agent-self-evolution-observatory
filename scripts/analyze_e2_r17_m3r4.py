#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

from research_pipeline.e2_r17_m3r4_execution_plan import TASK_IDS, logical_units, state_binding_map
from research_pipeline.e2_r17_regeneration_metrics_v4 import compute_prospective_regeneration_metrics_v4

ANALYSIS_AUTH_STATUS = "AUTHORIZED_E2_R17_M3R4_ANALYSIS_ONLY"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_manifest(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def classify(metrics: dict[str, Any]) -> str:
    if metrics["state_sha_alias"]:
        return "M3R4_STATE_SHA_ALIAS_ZERO_LOCALIZATION"
    if not metrics["within_task_iid_stationarity_qualified"]:
        return "M3R4_WITHIN_TASK_INFERENCE_ASSUMPTION_BLOCKED"
    if not metrics["cross_task_factorization_qualified"]:
        return "M3R4_CROSS_TASK_FACTORIZATION_BLOCKED"
    if float(metrics["e_real"]) <= 0.0:
        return "ACTOR_NOISE_NOT_EXCLUDED / DOWNGRADE_STATE_REGENERATION_MECHANISM"
    if float(metrics["exact_one_sided_p"]) > 0.05:
        return "M3R4_OBSERVED_EXCESS_ONLY_NO_PROPENSITY_LOCALIZATION"
    return "M3R4_SELECTED_CASE_STATE_REALIZATION_LOCALIZATION_PASS"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--measurement-authorization", type=Path, required=True)
    parser.add_argument("--completion-audit", type=Path, required=True)
    parser.add_argument("--analysis-authorization", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    require(not args.output.exists(), "M3R4 analysis output already exists")
    contract = load_json(args.contract)
    measurement_auth = load_json(args.measurement_authorization)
    audit = load_json(args.completion_audit)
    analysis_auth = load_json(args.analysis_authorization)
    contract_sha = sha256_file(args.contract)
    measurement_auth_sha = sha256_file(args.measurement_authorization)
    audit_sha = sha256_file(args.completion_audit)
    analysis_auth_sha = sha256_file(args.analysis_authorization)

    require(contract.get("status") == "FROZEN_E2_R17_M3R4_EXECUTION", "M3R4 contract status drift")
    require(measurement_auth.get("status") == "AUTHORIZED_E2_R17_M3R4_ACTOR_MEASUREMENT_ONLY", "M3R4 measurement auth drift")
    require(measurement_auth.get("contract_sha256") == contract_sha, "M3R4 measurement auth/contract drift")
    require(audit.get("status") == "PASS_M3R4_COMPLETION_INTEGRITY_READY_FOR_SEPARATE_ANALYSIS_AUTHORIZATION", "M3R4 audit not PASS")
    require(audit.get("contract_sha256") == contract_sha, "M3R4 audit contract drift")
    require(audit.get("measurement_authorization_sha256") == measurement_auth_sha, "M3R4 audit measurement-auth drift")
    require(analysis_auth.get("status") == ANALYSIS_AUTH_STATUS, "M3R4 analysis auth status drift")
    require(analysis_auth.get("contract_sha256") == contract_sha, "M3R4 analysis auth contract drift")
    require(analysis_auth.get("measurement_authorization_sha256") == measurement_auth_sha, "M3R4 analysis auth measurement drift")
    require(analysis_auth.get("completion_audit_sha256") == audit_sha, "M3R4 analysis auth audit drift")
    require((analysis_auth.get("authority") or {}).get("analysis") is True, "M3R4 analysis authority missing")
    require((analysis_auth.get("authority") or {}).get("provider_io") is False, "M3R4 analysis must be provider-free")
    require(analysis_auth.get("scientific_outcomes_read_before_authorization") is False, "M3R4 outcomes were read before analysis authorization")

    analyzer_row = analysis_auth["analysis_code"]
    require(Path(analyzer_row["path"]).resolve() == Path(__file__).resolve(), "M3R4 analysis auth points to different analyzer")
    require(sha256_file(Path(__file__).resolve()) == analyzer_row["sha256"], "M3R4 analyzer SHA drift")
    metric_path = ROOT / contract["bound_code"]["analysis_metric"]["path"]
    require(metric_path.is_file(), "M3R4 frozen metric missing")
    require(sha256_file(metric_path) == contract["bound_code"]["analysis_metric"]["sha256"], "M3R4 metric drift")
    require(analysis_auth["frozen_metric"]["sha256"] == sha256_file(metric_path), "M3R4 analysis-auth metric drift")

    manifest_path = Path(audit["completed_manifest_path"])
    require(manifest_path.is_file() and sha256_file(manifest_path) == audit["completed_manifest_sha256"], "M3R4 manifest drift after analysis authorization")
    rows = read_manifest(manifest_path)
    expected = logical_units()
    require(len(rows) == len(expected) == 72, "M3R4 analysis manifest cardinality drift")

    values: dict[tuple[str, int], dict[str, int]] = {
        ("ff_r1", 1): {},
        ("ff_r1", 2): {},
        ("ff_r2", 1): {},
        ("ff_r2", 2): {},
    }
    score_reads = 0
    for row, unit in zip(rows, expected, strict=True):
        require(row["unit_id"] == unit.unit_id, f"M3R4 analysis unit-order drift: {unit.unit_id}")
        trajectory_path = Path(row["trajectory_ref_path"])
        require(trajectory_path.is_file() and sha256_file(trajectory_path) == row["trajectory_ref_sha256"], f"M3R4 trajectory drift: {unit.unit_id}")
        trajectory = load_json(trajectory_path)
        require(trajectory.get("contract_sha256") == contract_sha, f"M3R4 trajectory contract drift: {unit.unit_id}")
        require(trajectory.get("authorization_sha256") == measurement_auth_sha, f"M3R4 trajectory authorization drift: {unit.unit_id}")
        require(trajectory.get("requested_model") == "deepseek-v4-pro", f"M3R4 requested-model drift: {unit.unit_id}")
        require(trajectory.get("resolved_model") == "deepseek-v4-pro-ga-260813", f"M3R4 resolved-model drift: {unit.unit_id}")
        require(int(trajectory.get("provider_retry_limit", -1)) == 0, f"M3R4 provider retry drift: {unit.unit_id}")
        require(trajectory.get("hidden_provider_retry_used") is False, f"M3R4 hidden provider retry observed: {unit.unit_id}")
        raw_score = trajectory.get("score")
        require(float(raw_score) in (0.0, 1.0), f"M3R4 score must be binary: {unit.unit_id}")
        values[(unit.state_id, unit.actor_replicate)][unit.task_id] = int(float(raw_score))
        score_reads += 1

    require(score_reads == 72, "M3R4 must read exactly 72 sealed scores")
    for key, mapping in values.items():
        require(set(mapping) == set(TASK_IDS), f"M3R4 task set drift in analysis vector {key}")

    assumptions = analysis_auth["inference_assumptions"]
    states = state_binding_map()
    result = compute_prospective_regeneration_metrics_v4(
        ff_r1_rep1=values[("ff_r1", 1)],
        ff_r1_rep2=values[("ff_r1", 2)],
        ff_r2_rep1=values[("ff_r2", 1)],
        ff_r2_rep2=values[("ff_r2", 2)],
        ff_r1_sha256=states["ff_r1"].skill_sha256,
        ff_r2_sha256=states["ff_r2"].skill_sha256,
        within_task_iid_stationarity_qualified=assumptions["within_task_iid_stationarity_qualified"],
        cross_task_factorization_qualified=assumptions["cross_task_factorization_qualified"],
        alpha=0.05,
    )
    metrics = asdict(result)
    verdict = classify(metrics)

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-m3r4-scientific-analysis",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": verdict,
        "contract_sha256": contract_sha,
        "measurement_authorization_sha256": measurement_auth_sha,
        "completion_audit_sha256": audit_sha,
        "analysis_authorization_sha256": analysis_auth_sha,
        "analysis_code_sha256": sha256_file(Path(__file__).resolve()),
        "frozen_metric_sha256": sha256_file(metric_path),
        "scientific_outcomes_read": True,
        "score_reads": 72,
        "historical_actor_outcomes_read_for_gate": False,
        "provider_calls": 0,
        "new_actor_measurements": 0,
        "new_updater_calls": 0,
        "inference_assumptions": assumptions,
        "metrics": metrics,
        "decision": {
            "verdict": verdict,
            "selected_case_only": True,
            "population_generalization": False,
            "variance_component_claim": False,
            "automatic_rerun": False,
            "bridge_authority": False,
            "paper_promotion": False,
        },
        "next_gate": "ADJUDICATE_M3R4_RESULT_AND_ONLY_THEN_DECIDE_BRIDGE_STAGE_A_ELIGIBILITY",
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
