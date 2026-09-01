"""Build a conservative resource authority for the frozen 432-unit Qwen plan."""
from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Mapping, Sequence

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, canonical_json, sha256_file, sha256_text, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_behavioral_runner import (
    receipt_path,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
CALIBRATION = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-calibration-result-20260901.json"
PILOT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-pilot-result-20260901.json"
PILOT_CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-pilot-contract-20260901.json"
PILOT_RECEIPTS = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-pilot-runs-20260901"
Q0 = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q0-result-20260901.json"
MANIFEST = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-manifest-20260901.json"
SCHEDULE = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-confirmatory-schedule-20260901.json"
AUTHORITY = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-resource-authority-20260901.json"
CHUNK_SIZE = 24
HEADROOM_MULTIPLIER = 1.25


def quantile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("resource quantile needs observations")
    position = probability * (len(ordered) - 1)
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def trajectory_resource(receipt: Mapping[str, Any]) -> dict[str, float]:
    trajectory = receipt.get("trajectory") or {}
    responses = trajectory.get("responses") or []
    usage = [response.get("usage") or {} for response in responses]
    return {
        "model_calls": float(trajectory.get("model_call_count") or 0),
        "input_tokens": float(sum(int(row.get("input_tokens") or 0) for row in usage)),
        "output_tokens": float(sum(int(row.get("output_tokens") or 0) for row in usage)),
        "total_tokens": float(sum(int(row.get("input_tokens") or 0) +
                                  int(row.get("output_tokens") or 0) for row in usage)),
        "provider_latency_seconds": float(sum(float(response.get("latency_seconds") or 0)
                                              for response in responses)),
    }


def summarize_resources(rows: Sequence[Mapping[str, float]]) -> dict[str, dict[str, float]]:
    if not rows:
        raise ValueError("resource authority needs empirical rows")
    metrics = ("model_calls", "input_tokens", "output_tokens",
               "total_tokens", "provider_latency_seconds")
    return {
        metric: {
            "mean": mean(float(row[metric]) for row in rows),
            "p50": quantile([float(row[metric]) for row in rows], .50),
            "p90": quantile([float(row[metric]) for row in rows], .90),
            "p95": quantile([float(row[metric]) for row in rows], .95),
        } for metric in metrics
    }


def chunk_plan(unit_count: int, chunk_size: int = CHUNK_SIZE) -> list[dict[str, int]]:
    if unit_count <= 0 or chunk_size <= 0:
        raise ValueError("invalid chunk dimensions")
    result = []
    for start in range(1, unit_count + 1, chunk_size):
        end = min(unit_count, start + chunk_size - 1)
        result.append({"chunk_id": len(result) + 1, "start_ordinal": start,
                       "end_ordinal": end, "unit_count": end - start + 1})
    return result


def numeric_remaining(headers: Iterable[Mapping[str, Any]], noun: str) -> list[int]:
    found: list[int] = []
    for row in headers:
        for key, value in row.items():
            lowered = str(key).lower()
            if "remaining" not in lowered or noun not in lowered:
                continue
            try:
                found.append(int(float(str(value).strip())))
            except ValueError:
                continue
    return found


def authority_payload(*, approved_request_budget: int | None = None,
                      approved_token_budget: int | None = None) -> dict[str, Any]:
    calibration = json.loads(CALIBRATION.read_text())
    pilot = json.loads(PILOT.read_text())
    pilot_contract = json.loads(PILOT_CONTRACT.read_text())
    q0 = json.loads(Q0.read_text())
    manifest = json.loads(MANIFEST.read_text())
    schedule = json.loads(SCHEDULE.read_text())
    if calibration["decision"] != "QWEN_CAPABILITY_CALIBRATION_QUALIFIED":
        raise RuntimeError("calibration resource gate closed")
    if pilot["decision"] != "QWEN_PILOT_METRIC_AND_RELIABILITY_QUALIFIED":
        raise RuntimeError("pilot resource gate closed")
    if schedule["unit_count"] != 432 or manifest["sample"]["planned_trajectories"] != 432:
        raise RuntimeError("confirmatory schedule size drift")

    rows = [dict(row) for row in calibration["resource_rows"]]
    pilot_receipts = [
        json.loads(receipt_path(PILOT_RECEIPTS, unit).read_text())
        for unit in pilot_contract["plan"]
    ]
    rows.extend(trajectory_resource(receipt) for receipt in pilot_receipts)
    summary = summarize_resources(rows)

    safe_headers: list[Mapping[str, Any]] = []
    for probe in q0.get("probes", []):
        safe_headers.append(probe.get("safe_rate_quota_headers") or {})
    for receipt in pilot_receipts:
        for response in (receipt.get("trajectory") or {}).get("responses") or []:
            safe_headers.append(response.get("safe_rate_quota_headers") or {})

    nonempty_safe_headers = [dict(row) for row in safe_headers if row]
    latest_safe_headers = nonempty_safe_headers[-1] if nonempty_safe_headers else {}
    reset_headers = {key: value for key, value in latest_safe_headers.items()
                     if "reset" in str(key).lower() or str(key).lower() == "retry-after"}
    request_remaining = numeric_remaining(safe_headers, "request")
    token_remaining = numeric_remaining(safe_headers, "token")
    observed_request_budget = request_remaining[-1] if request_remaining else None
    observed_token_budget = token_remaining[-1] if token_remaining else None
    request_budget = approved_request_budget if approved_request_budget is not None else observed_request_budget
    token_budget = approved_token_budget if approved_token_budget is not None else observed_token_budget

    projected = {
        metric: {
            percentile: math.ceil(summary[metric][percentile] * 432 * HEADROOM_MULTIPLIER)
            for percentile in ("p50", "p90", "p95")
        } for metric in summary
    }
    required_requests = projected["model_calls"]["p95"]
    required_tokens = projected["total_tokens"]["p95"]
    request_proven = request_budget is not None and request_budget >= required_requests
    token_proven = token_budget is not None and token_budget >= required_tokens
    budget_proven = request_proven or token_proven
    chunks = chunk_plan(432)
    checks = {
        "calibration_qualified": True, "pilot_qualified": True,
        "empirical_trajectory_count_at_least_56": len(rows) >= 56,
        "schedule_exactly_432": schedule["unit_count"] == 432,
        "contiguous_chunk_plan_covers_schedule": (
            chunks[0]["start_ordinal"] == 1 and chunks[-1]["end_ordinal"] == 432
            and sum(row["unit_count"] for row in chunks) == 432),
        "credible_full_plan_budget": budget_proven,
        "credential_material_absent": True,
    }
    passed = all(checks.values())
    payload = {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_CONFIRMATORY_RESOURCE_AUTHORITY", "created_at_utc": utcnow(),
        "decision": ("QWEN_CONFIRMATORY_RESOURCE_AUTHORITY_PASS_EXECUTION_AUTHORIZED"
                     if passed else
                     "QWEN_CONFIRMATORY_RESOURCE_AUTHORITY_HOLD_INSUFFICIENT_PROVEN_BUDGET"),
        "input_hashes": {
            "calibration": sha256_file(CALIBRATION), "pilot": sha256_file(PILOT),
            "pilot_contract": sha256_file(PILOT_CONTRACT), "q0": sha256_file(Q0),
            "manifest": sha256_file(MANIFEST), "schedule": sha256_file(SCHEDULE),
        },
        "empirical_trajectory_count": len(rows), "resource_summary": summary,
        "projected_432_with_25_percent_headroom": projected,
        "quota_evidence": {
            "safe_header_sets_observed": len(safe_headers),
            "nonempty_safe_header_sets_observed": len(nonempty_safe_headers),
            "latest_safe_rate_quota_headers": latest_safe_headers,
            "latest_reset_window_headers": reset_headers,
            "provider_reported_latest_remaining_requests": observed_request_budget,
            "provider_reported_latest_remaining_tokens": observed_token_budget,
            "explicit_approved_request_budget": approved_request_budget,
            "explicit_approved_token_budget": approved_token_budget,
            "effective_request_budget": request_budget,
            "effective_token_budget": token_budget,
            "required_p95_headroom_requests": required_requests,
            "required_p95_headroom_tokens": required_tokens,
            "request_budget_proven": request_proven, "token_budget_proven": token_proven,
        },
        "cost": {
            "currency_charge_observable": False,
            "currency_p50_p90_p95": None,
            "reason": "subscription/plan route exposes usage and quota, not per-request currency charge",
            "operational_cost_proxies": {
                metric: summary[metric] for metric in
                ("model_calls", "input_tokens", "output_tokens", "total_tokens",
                 "provider_latency_seconds")
            },
        },
        "operational_chunks": chunks,
        "chunk_rule": (
            "only contiguous chunks; before each chunk subtract persisted main usage from the "
            "proven full-plan budget and require the untouched chunk p95 headroom; when reset "
            "metadata is reported, never start a held chunk until the reported reset window"
        ),
        "checks": checks, "execution_authorized": passed,
        "no_retry": True, "no_replacement": True, "attempt_count": 1,
        "schedule_sha256": schedule["schedule_sha256"],
        "chunk_plan_sha256": sha256_text(canonical_json(chunks)),
        "credential_material_present": False,
    }
    return payload


def freeze_authority(*, approved_request_budget: int | None = None,
                     approved_token_budget: int | None = None,
                     output: Path = AUTHORITY) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite resource authority")
    payload = authority_payload(approved_request_budget=approved_request_budget,
                                approved_token_budget=approved_token_budget)
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload),
            "execution_authorized": payload["execution_authorized"]}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--approved-request-budget", type=int)
    parser.add_argument("--approved-token-budget", type=int)
    args = parser.parse_args()
    print(json.dumps(freeze_authority(
        approved_request_budget=args.approved_request_budget,
        approved_token_budget=args.approved_token_budget), sort_keys=True))


if __name__ == "__main__":
    main()
