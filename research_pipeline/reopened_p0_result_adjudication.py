from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

from .pre_experiment_specs import TYPED_OUTCOMES
from .reopened_p0_plan import validate_p0_plan

SCHEMA_VERSION = "1.0"
PACKET_STATUS = "P0_RESULT_PACKET_FROZEN_AWAITING_INDEPENDENT_ADJUDICATION"
METHOD_PASS = "P0_METHOD_PASS_CURRENT_REALIZATION_ONLY"
METHOD_FAIL = "P0_METHOD_FAIL_CURRENT_REALIZATION_ONLY"
PROTOCOL_STOP = "P0_PROTOCOL_STOP_NO_METHOD_OR_PRINCIPLE_VERDICT"
SUPPORT_STOP = "P0_SUPPORT_STOP_NO_METHOD_OR_PRINCIPLE_VERDICT"
RUNTIME_STOP = "P0_RUNTIME_STOP_NO_METHOD_OR_PRINCIPLE_VERDICT"
IMPLEMENTATION_STOP = "P0_IMPLEMENTATION_STOP_NO_METHOD_OR_PRINCIPLE_VERDICT"
BUDGET_STOP = "P0_BUDGET_STOP_NO_METHOD_OR_PRINCIPLE_VERDICT"
BASELINE_BOUNDARY = "P0_BASELINE_BOUNDARY_METHOD_REALIZATION_REVIEW"
INCONCLUSIVE = "P0_INCONCLUSIVE_NO_METHOD_OR_PRINCIPLE_VERDICT"

ADJUDICATOR_ROLE = "INDEPENDENT_CONFIRMATORY_P0_ADJUDICATOR"
REQUIRED_CHECKS = (
    "artifact_manifest_integrity_pass",
    "fresh_confirmatory_split_pass",
    "local_f0_data_excluded_pass",
    "protocol_validity_pass",
    "support_qualification_pass",
    "truth_source_valid_pass",
    "plan_conformance_pass",
    "same_information_baseline_parity_pass",
    "statistical_plan_followed_pass",
    "no_outcome_selection_pass",
    "budget_compliant_pass",
)
ZERO_AUTHORITY = {
    "scientific": False,
    "principle": False,
    "claim_update": False,
    "experiment": False,
    "gpu": False,
    "submission": False,
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")[:180] or "unknown"


def result_packet_identity(packet: Mapping[str, Any]) -> dict[str, Any]:
    return {key: packet.get(key) for key in (
        "contract_id", "contract_sha256", "p0_plan_sha256", "run_id",
        "typed_execution_outcome", "artifact_manifest_sha256", "analysis_receipt_sha256",
        "recompute_receipt_sha256", "completed_units", "provider_calls", "gpu_hours_used",
        "primary_metric_name", "primary_metric_value", "primary_test_p_value",
        "same_information_baseline_summary_sha256", "status",
    )}


def build_p0_result_packet(*, p0_plan: Mapping[str, Any], packet: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_p0_plan(p0_plan):
        raise RuntimeError("valid frozen confirmatory P0 plan required")
    data = dict(packet or {})
    required = (
        "run_id", "typed_execution_outcome", "artifact_manifest_sha256", "analysis_receipt_sha256",
        "recompute_receipt_sha256", "primary_metric_name", "same_information_baseline_summary_sha256",
    )
    for key in required:
        if not _text(data.get(key)):
            raise RuntimeError(f"P0 result packet field required: {key}")
    outcome = _text(data.get("typed_execution_outcome"))
    if outcome not in TYPED_OUTCOMES:
        raise RuntimeError("P0 result packet typed outcome unknown")
    if outcome in {"SCREENING-SIGNAL", "SCREENING-NO-SIGNAL"}:
        raise RuntimeError("confirmatory P0 result cannot use screening-only outcomes")
    completed_units = int(data.get("completed_units") or 0)
    provider_calls = int(data.get("provider_calls") or 0)
    gpu_hours_used = float(data.get("gpu_hours_used") or 0.0)
    if completed_units < 0 or provider_calls < 0 or gpu_hours_used < 0:
        raise RuntimeError("P0 result packet usage counters must be nonnegative")
    manifest = data.get("artifact_manifest") or []
    if not isinstance(manifest, list) or not manifest:
        raise RuntimeError("P0 result packet requires content-addressed artifact manifest")
    for index, row in enumerate(manifest):
        if not isinstance(row, Mapping) or not _text(row.get("role")) or not _text(row.get("sha256")) or int(row.get("bytes") or 0) <= 0:
            raise RuntimeError(f"P0 result artifact incomplete: {index}")
    if _digest(manifest) != _text(data.get("artifact_manifest_sha256")):
        raise RuntimeError("P0 result artifact manifest SHA mismatch")
    baseline = data.get("same_information_baseline_summary") or {}
    if not isinstance(baseline, Mapping) or not baseline:
        raise RuntimeError("P0 result packet requires same-information baseline summary")
    if _digest(baseline) != _text(data.get("same_information_baseline_summary_sha256")):
        raise RuntimeError("P0 result same-information baseline SHA mismatch")
    metric_value = data.get("primary_metric_value")
    p_value = data.get("primary_test_p_value")
    if outcome in {"METHOD-PASS", "METHOD-FAIL"}:
        if metric_value is None or p_value is None:
            raise RuntimeError("P0 method outcome requires primary metric and test p-value")
        p_value = float(p_value)
        if not (0.0 <= p_value <= 1.0):
            raise RuntimeError("P0 result p-value out of range")
    plan_spec = p0_plan.get("plan_spec") or {}
    if _text(data.get("evaluation_split")) != _text(plan_spec.get("evaluation_split")):
        raise RuntimeError("P0 result evaluation split differs from frozen plan")
    if data.get("local_f0_data_excluded_from_confirmatory_statistic") is not True:
        raise RuntimeError("P0 result must exclude local-F0 data from confirmatory statistic")
    if data.get("outcome_driven_selection_used") is not False:
        raise RuntimeError("P0 result packet forbids outcome-driven selection")
    row = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "reopen-p0-result-packet",
        "contract_id": _text(p0_plan.get("contract_id")),
        "contract_sha256": _text(p0_plan.get("contract_sha256")),
        "p0_plan_sha256": _text(p0_plan.get("p0_plan_sha256")),
        "run_id": _text(data.get("run_id")),
        "typed_execution_outcome": outcome,
        "artifact_manifest": [dict(x) for x in manifest],
        "artifact_manifest_sha256": _text(data.get("artifact_manifest_sha256")),
        "analysis_receipt_sha256": _text(data.get("analysis_receipt_sha256")),
        "recompute_receipt_sha256": _text(data.get("recompute_receipt_sha256")),
        "completed_units": completed_units,
        "provider_calls": provider_calls,
        "gpu_hours_used": gpu_hours_used,
        "evaluation_split": _text(data.get("evaluation_split")),
        "local_f0_data_excluded_from_confirmatory_statistic": True,
        "outcome_driven_selection_used": False,
        "primary_metric_name": _text(data.get("primary_metric_name")),
        "primary_metric_value": metric_value,
        "primary_test_p_value": p_value,
        "same_information_baseline_summary": dict(baseline),
        "same_information_baseline_summary_sha256": _text(data.get("same_information_baseline_summary_sha256")),
        "status": PACKET_STATUS,
        "independent_adjudication_required": True,
        "method_verdict_authorized": False,
        "principle_update_allowed": False,
        "claim_update_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    row["p0_result_packet_sha256"] = _digest(result_packet_identity(row))
    if not validate_p0_result_packet(row):
        raise RuntimeError("generated P0 result packet invalid")
    return row


def validate_p0_result_packet(packet: Mapping[str, Any]) -> bool:
    if packet.get("receipt_type") != "reopen-p0-result-packet" or packet.get("status") != PACKET_STATUS:
        return False
    if packet.get("independent_adjudication_required") is not True:
        return False
    if any(packet.get(key) is not False for key in (
        "method_verdict_authorized", "principle_update_allowed", "claim_update_authorized",
        "scientific_authority", "experiment_authority", "gpu_authority", "submission_authority",
    )):
        return False
    if _digest(packet.get("artifact_manifest") or []) != _text(packet.get("artifact_manifest_sha256")):
        return False
    if _digest(packet.get("same_information_baseline_summary") or {}) != _text(packet.get("same_information_baseline_summary_sha256")):
        return False
    if packet.get("local_f0_data_excluded_from_confirmatory_statistic") is not True or packet.get("outcome_driven_selection_used") is not False:
        return False
    return _text(packet.get("p0_result_packet_sha256")) == _digest(result_packet_identity(packet))


def adjudication_identity(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: receipt.get(key) for key in (
        "contract_id", "contract_sha256", "p0_plan_sha256", "p0_result_packet_sha256",
        "adjudicator_ref_sha256", "adjudicated_at", "checks", "failed_checks", "failure_layer",
        "status", "method_verdict", "method_verdict_authorized", "principle_update_allowed",
    )}


def build_p0_adjudication(*, p0_plan: Mapping[str, Any], result_packet: Mapping[str, Any], packet: Mapping[str, Any]) -> dict[str, Any]:
    if not validate_p0_plan(p0_plan) or not validate_p0_result_packet(result_packet):
        raise RuntimeError("valid frozen P0 plan and result packet required")
    if _text(result_packet.get("p0_plan_sha256")) != _text(p0_plan.get("p0_plan_sha256")):
        raise RuntimeError("P0 adjudication plan lineage mismatch")
    data = dict(packet or {})
    if _text(data.get("adjudicator_role")) != ADJUDICATOR_ROLE:
        raise RuntimeError("independent confirmatory P0 adjudicator role required")
    ref = _text(data.get("adjudicator_ref")); at = _text(data.get("adjudicated_at"))
    if not ref or not at:
        raise RuntimeError("P0 adjudicator identity and timestamp required")
    checks_in = data.get("checks") or {}
    if not isinstance(checks_in, Mapping) or set(checks_in.keys()) != set(REQUIRED_CHECKS):
        raise RuntimeError("P0 adjudication checks must match required set exactly")
    checks = {key: checks_in.get(key) is True for key in REQUIRED_CHECKS}
    failed = [key for key in REQUIRED_CHECKS if not checks[key]]
    outcome = _text(result_packet.get("typed_execution_outcome"))

    protocol_keys = {
        "artifact_manifest_integrity_pass", "fresh_confirmatory_split_pass", "local_f0_data_excluded_pass",
        "protocol_validity_pass", "truth_source_valid_pass", "plan_conformance_pass", "no_outcome_selection_pass",
    }
    if any(not checks[key] for key in protocol_keys):
        status, failure_layer, verdict = PROTOCOL_STOP, "experiment_identifiability", "NO_METHOD_VERDICT"
    elif not checks["support_qualification_pass"]:
        status, failure_layer, verdict = SUPPORT_STOP, "assumption_scope", "NO_METHOD_VERDICT"
    elif outcome == "RUNTIME-ERROR":
        status, failure_layer, verdict = RUNTIME_STOP, "execution", "NO_METHOD_VERDICT"
    elif outcome == "IMPLEMENTATION-ERROR":
        status, failure_layer, verdict = IMPLEMENTATION_STOP, "execution", "NO_METHOD_VERDICT"
    elif outcome == "BUDGET-STOP" or not checks["budget_compliant_pass"]:
        status, failure_layer, verdict = BUDGET_STOP, "optimization", "NO_METHOD_VERDICT"
    elif outcome in {"BASELINE-FLOOR", "BASELINE-CEILING"} or not checks["same_information_baseline_parity_pass"]:
        status, failure_layer, verdict = BASELINE_BOUNDARY, "method_realization", "NO_METHOD_VERDICT"
    elif not checks["statistical_plan_followed_pass"]:
        status, failure_layer, verdict = INCONCLUSIVE, "experiment_identifiability", "NO_METHOD_VERDICT"
    elif outcome == "METHOD-PASS" and not failed:
        status, failure_layer, verdict = METHOD_PASS, None, "METHOD-PASS"
    elif outcome == "METHOD-FAIL" and not failed:
        status, failure_layer, verdict = METHOD_FAIL, "method_realization", "METHOD-FAIL"
    else:
        status, failure_layer, verdict = INCONCLUSIVE, "experiment_identifiability", "NO_METHOD_VERDICT"

    method_authorized = status in {METHOD_PASS, METHOD_FAIL}
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "reopen-p0-independent-adjudication",
        "contract_id": _text(result_packet.get("contract_id")),
        "contract_sha256": _text(result_packet.get("contract_sha256")),
        "p0_plan_sha256": _text(p0_plan.get("p0_plan_sha256")),
        "p0_result_packet_sha256": _text(result_packet.get("p0_result_packet_sha256")),
        "adjudicator_role": ADJUDICATOR_ROLE,
        "adjudicator_ref": ref,
        "adjudicator_ref_sha256": hashlib.sha256(ref.encode()).hexdigest(),
        "adjudicated_at": at,
        "checks": checks,
        "failed_checks": failed,
        "typed_execution_outcome": outcome,
        "status": status,
        "failure_layer": failure_layer,
        "method_verdict": verdict,
        "method_verdict_authorized": method_authorized,
        "current_method_realization_only": True,
        "principle_update_allowed": False,
        "principle_falsified": False,
        "principle_dead_end_certified": False,
        "claim_update_authorized": False,
        "parent_paper_claim_status_unchanged": True,
        "positive_method_evidence_does_not_prove_principle": True,
        "method_fail_does_not_falsify_principle": True,
        "principle_adjudication_required_for_any_principle_update": True,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    receipt["p0_adjudication_sha256"] = _digest(adjudication_identity(receipt))
    if not validate_p0_adjudication(receipt):
        raise RuntimeError("generated P0 adjudication invalid")
    return receipt


def validate_p0_adjudication(receipt: Mapping[str, Any]) -> bool:
    allowed = {METHOD_PASS, METHOD_FAIL, PROTOCOL_STOP, SUPPORT_STOP, RUNTIME_STOP, IMPLEMENTATION_STOP, BUDGET_STOP, BASELINE_BOUNDARY, INCONCLUSIVE}
    if receipt.get("receipt_type") != "reopen-p0-independent-adjudication" or receipt.get("status") not in allowed:
        return False
    ref = _text(receipt.get("adjudicator_ref"))
    if not ref or hashlib.sha256(ref.encode()).hexdigest() != _text(receipt.get("adjudicator_ref_sha256")):
        return False
    checks = receipt.get("checks") or {}
    if not isinstance(checks, Mapping) or set(checks.keys()) != set(REQUIRED_CHECKS):
        return False
    failed = [key for key in REQUIRED_CHECKS if checks.get(key) is not True]
    if failed != list(receipt.get("failed_checks") or []):
        return False
    method_authorized = receipt.get("status") in {METHOD_PASS, METHOD_FAIL}
    if receipt.get("method_verdict_authorized") is not method_authorized:
        return False
    if receipt.get("current_method_realization_only") is not True:
        return False
    if any(receipt.get(key) is not False for key in (
        "principle_update_allowed", "principle_falsified", "principle_dead_end_certified", "claim_update_authorized",
        "scientific_authority", "experiment_authority", "gpu_authority", "submission_authority",
    )):
        return False
    if any(receipt.get(key) is not True for key in (
        "parent_paper_claim_status_unchanged", "positive_method_evidence_does_not_prove_principle",
        "method_fail_does_not_falsify_principle", "principle_adjudication_required_for_any_principle_update",
    )):
        return False
    return _text(receipt.get("p0_adjudication_sha256")) == _digest(adjudication_identity(receipt))


def _directory(root: Path) -> Path:
    root = Path(root)
    return root if root.name == "scientific-contract-p0-results" else root / "scientific-contract-p0-results"


def _receipt_sha(receipt: Mapping[str, Any]) -> str:
    if receipt.get("receipt_type") == "reopen-p0-independent-adjudication":
        return _text(receipt.get("p0_adjudication_sha256"))
    return _text(receipt.get("p0_result_packet_sha256"))


def validate_p0_result_ledger(ledger: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []; seen: set[str] = set(); packets: set[str] = set()
    cid = _text(ledger.get("contract_id")); csha = _text(ledger.get("contract_sha256"))
    if (ledger.get("authority") or {}) != ZERO_AUTHORITY:
        errors.append("p0-result-ledger-authority-leak")
    for index, event in enumerate(ledger.get("events") or []):
        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        typ = _text(receipt.get("receipt_type")) if isinstance(receipt, Mapping) else ""
        valid = validate_p0_result_packet(receipt) if typ == "reopen-p0-result-packet" else validate_p0_adjudication(receipt) if typ == "reopen-p0-independent-adjudication" else False
        if not valid:
            errors.append("p0-result-receipt-invalid"); continue
        if _text(receipt.get("contract_id")) != cid or _text(receipt.get("contract_sha256")) != csha:
            errors.append("p0-result-contract-lineage-mismatch")
        sha = _receipt_sha(receipt)
        if sha in seen:
            errors.append("p0-result-duplicate-receipt")
        if typ == "reopen-p0-result-packet":
            packets.add(sha)
        elif _text(receipt.get("p0_result_packet_sha256")) not in packets:
            errors.append("p0-adjudication-missing-prior-result-packet")
        recorded = _text(event.get("recorded_at"))
        expected = _digest([cid, index, typ, sha, recorded])[:24]
        if _text(event.get("event_id")) != expected:
            errors.append("p0-result-event-id-invalid")
        seen.add(sha)
    return list(dict.fromkeys(errors))


def publish_p0_result_receipt(root: Path, receipt: Mapping[str, Any], *, recorded_at: str) -> dict[str, Any]:
    typ = _text(receipt.get("receipt_type"))
    valid = validate_p0_result_packet(receipt) if typ == "reopen-p0-result-packet" else validate_p0_adjudication(receipt) if typ == "reopen-p0-independent-adjudication" else False
    if not valid:
        raise RuntimeError("invalid P0 result/adjudication receipt")
    at = _text(recorded_at)
    if not at:
        raise RuntimeError("P0 result receipt recorded_at required")
    directory = _directory(root); directory.mkdir(parents=True, exist_ok=True)
    cid = _text(receipt.get("contract_id")); path = directory / f"{_slug(cid)}.json"; lock = directory / f".{_slug(cid)}.lock"
    with lock.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        ledger = json.loads(path.read_text()) if path.exists() else {"schema_version": SCHEMA_VERSION, "contract_id": cid, "contract_sha256": _text(receipt.get("contract_sha256")), "events": [], "authority": dict(ZERO_AUTHORITY)}
        sha = _receipt_sha(receipt)
        for event in ledger.get("events") or []:
            prior = event.get("receipt") or {} if isinstance(event, Mapping) else {}
            if isinstance(prior, Mapping) and _receipt_sha(prior) == sha:
                return ledger
        if typ == "reopen-p0-independent-adjudication":
            prior_packets = {_text((event.get("receipt") or {}).get("p0_result_packet_sha256")) for event in ledger.get("events") or [] if isinstance(event, Mapping) and (event.get("receipt") or {}).get("receipt_type") == "reopen-p0-result-packet"}
            if _text(receipt.get("p0_result_packet_sha256")) not in prior_packets:
                raise RuntimeError("P0 adjudication requires published result packet")
        event = {"event_type": typ, "receipt": dict(receipt), "recorded_at": at, "scientific_authority": False, "principle_authority": False, "claim_update_authority": False}
        event["event_id"] = _digest([cid, len(ledger.get("events") or []), typ, sha, at])[:24]
        ledger.setdefault("events", []).append(event); ledger["updated_at"] = at
        errors = validate_p0_result_ledger(ledger)
        if errors:
            raise RuntimeError(errors)
        tmp = path.with_suffix(".json.tmp"); tmp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"); os.replace(tmp, path)
        return ledger


def public_p0_result(root: Path, contract_id: str) -> dict[str, Any]:
    empty = {"status": "P0_RESULT_PACKET_REQUIRED", "p0_result_packet_sha256": "", "p0_adjudication_sha256": "", "typed_execution_outcome": "", "method_verdict": "", "method_verdict_authorized": False, "failure_layer": "", "principle_update_allowed": False, "authority": dict(ZERO_AUTHORITY)}
    path = _directory(root) / f"{_slug(contract_id)}.json"
    if not path.exists():
        return empty
    try:
        ledger = json.loads(path.read_text())
    except Exception:
        return {**empty, "status": "P0_RESULT_LEDGER_INVALID"}
    if validate_p0_result_ledger(ledger):
        return {**empty, "status": "P0_RESULT_LEDGER_INVALID"}
    result: Mapping[str, Any] = {}; adjudication: Mapping[str, Any] = {}
    for event in ledger.get("events") or []:
        receipt = event.get("receipt") or {} if isinstance(event, Mapping) else {}
        if receipt.get("receipt_type") == "reopen-p0-result-packet": result = receipt
        elif receipt.get("receipt_type") == "reopen-p0-independent-adjudication": adjudication = receipt
    if adjudication:
        return {**empty, "status": _text(adjudication.get("status")), "p0_result_packet_sha256": _text(result.get("p0_result_packet_sha256")), "p0_adjudication_sha256": _text(adjudication.get("p0_adjudication_sha256")), "typed_execution_outcome": _text(result.get("typed_execution_outcome")), "method_verdict": _text(adjudication.get("method_verdict")), "method_verdict_authorized": adjudication.get("method_verdict_authorized") is True, "failure_layer": _text(adjudication.get("failure_layer")), "principle_update_allowed": False}
    if result:
        return {**empty, "status": PACKET_STATUS, "p0_result_packet_sha256": _text(result.get("p0_result_packet_sha256")), "typed_execution_outcome": _text(result.get("typed_execution_outcome"))}
    return empty
