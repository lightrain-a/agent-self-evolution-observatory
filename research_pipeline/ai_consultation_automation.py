from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ai_consultation_clinic import CHECKPOINTS, POLICY as CLINIC_POLICY
from .ark_provider import ArkResponsesClient, ArkSettings, extract_json_object
from .config import PROJECT_ROOT, StorageSettings
from .failure_differential_registry import build_failure_hypothesis_set, score_failure_hypothesis_set
from .p0_decision_ledger import build_p0_decision_ledger
from .principle_adjudication import FAILURE_LAYER_SPECS

DEFAULT_JSON = PROJECT_ROOT / "generated" / "ai-consultation-automation.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "ai-consultation-automation.js"
WEAK_DIAGNOSES = {
    "infrastructure-error", "budget-plan-mismatch", "substrate-degenerate",
    "no-label-variation", "underfit", "representation-signal-mismatch",
    "objective-claim-mismatch", "baseline-floor", "baseline-ceiling", "inconclusive",
}
ALLOWED_DISPOSITIONS = {
    "machine_gate_added", "matched_baseline_added", "cheap_falsifier_run",
    "evidence_resolves_risk", "human_accepts_residual_risk_with_reason",
    "stop_or_merge_before_expensive_transition",
}
PUBLIC_POLICY = {
    "schema_version": "1.0",
    "content_addressed_triggers": True,
    "first_observation_is_baseline_only": True,
    "default_max_cases_per_cycle": 1,
    "default_reviewers_per_case": 3,
    "default_max_reviewer_attempts": 2,
    "raw_reviews_backend_only": True,
    "failed_reviewer_is_missing_not_pass": True,
    "ai_output_never_authorizes_execution": True,
    "unresolved_high_risk_requires_structured_disposition": True,
    "post_screen_differential_hypotheses_are_frozen_before_final_adjudication": True,
    "historical_final_labels_cannot_backfill_differential_hypotheses": True,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _clinic_by_key() -> dict[str, dict[str, Any]]:
    return {str(row["key"]): dict(row) for row in CHECKPOINTS}


def _final_failure_row(subject_id: str) -> dict[str, Any]:
    """Return the latest canonical typed failure row, which may predate a new differential case."""
    try:
        ledger = build_p0_decision_ledger(
            _load(PROJECT_ROOT / "generated" / "p0-admission-state.json", {}),
            _load(PROJECT_ROOT / "generated" / "p0-offline-qualification.json", {}),
            _load(PROJECT_ROOT / "generated" / "human-terminal-idea-state.json", {}),
            _load(PROJECT_ROOT / "generated" / "p0-four-direction-iteration.json", {}),
        )
    except Exception:
        return {}
    return next(
        (dict(row) for row in ledger.get("rows") or [] if isinstance(row, dict) and str(row.get("idea_id") or "") == str(subject_id) and row.get("failure_diagnosis_complete") is True),
        {},
    )


def _final_failure_identity(row: dict[str, Any]) -> str:
    if not isinstance(row, dict):
        return ""
    evidence = row.get("failure_evidence") or {}
    evidence_sha = str(evidence.get("evidence_sha256") or "")
    layer = str(row.get("failure_layer") or "")
    if not evidence_sha or layer not in FAILURE_LAYER_SPECS:
        return ""
    return _hash({
        "failure_layer": layer,
        "failure_class": str(row.get("failure_class") or ""),
        "evidence_sha256": evidence_sha,
        "decision_source": str(row.get("decision_source") or ""),
        "p0_decision": str(row.get("p0_decision") or ""),
    })


def _idea_index() -> dict[str, dict[str, Any]]:
    payload = _load(PROJECT_ROOT / "generated" / "iclr-low-resource-ideas.json", {})
    rows = list(payload.get("passed_ideas") or []) + list(payload.get("blocked_ideas") or [])
    return {str(row.get("id")): row for row in rows if row.get("id")}


def _premortem_candidates() -> list[dict[str, Any]]:
    portfolio = _load(PROJECT_ROOT / "generated" / "discussion-ready-ideas.json", {})
    index = _idea_index()
    keep = (
        "id", "title", "purpose", "core_idea", "core_intuition", "rationale", "method_logic",
        "collision_boundary", "hypothesis", "nearest_work", "strongest_baseline", "pilot",
        "decisive_metric", "stop_condition", "budget",
    )
    out = []
    for ref in portfolio.get("ideas") or []:
        idea = index.get(str(ref.get("id"))) or ref
        dossier = {key: idea.get(key) for key in keep if idea.get(key) not in (None, "")}
        out.append({"checkpoint": "idea_premortem", "subject_id": str(ref.get("id")), "dossier": dossier})
    return out


def _admission_candidates() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    state = _load(PROJECT_ROOT / "generated" / "p0-admission-state.json", {})
    economy, launch = [], []
    for card in state.get("cards") or []:
        subject = str(card.get("idea_id") or "")
        if not subject:
            continue
        pre = card.get("execution_preflight") or {}
        econ = pre.get("economy_gate") or {}
        dossier = {
            "idea_id": subject, "code": card.get("code"), "title": card.get("title"),
            "contract": card.get("contract"), "setup": card.get("setup"), "economy_gate": econ,
        }
        economy.append({"checkpoint": "economy_red_team", "subject_id": subject, "dossier": dossier})
        if econ.get("execution_compilation_authorized") is True:
            launch.append({
                "checkpoint": "pre_launch_stress_review", "subject_id": subject,
                "dossier": {**dossier, "execution_preflight": pre},
            })
    return economy, launch


def _diagnosis_candidates() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    state = _load(PROJECT_ROOT / "generated" / "research-system-state.json", {})
    weak, scale = [], []
    iteration = state.get("experiment_iteration") or {}
    for node in iteration.get("nodes") or []:
        subject = str(node.get("idea_id") or "")
        if not subject:
            continue
        diagnosis = str(node.get("diagnosis") or "").lower()
        dossier = {key: node.get(key) for key in (
            "idea_id", "code", "qualification_pass", "experiment_identifiable",
            "scientific_belief_update_allowed", "scale_up_allowed", "evidence",
        )}
        if diagnosis in WEAK_DIAGNOSES or (not node.get("experiment_identifiable") and not node.get("scale_up_allowed")):
            weak.append({
                "checkpoint": "post_screen_differential_diagnosis",
                "subject_id": subject,
                "dossier": dossier,
                "single_diagnosis_baseline": {
                    "diagnosis": node.get("diagnosis"),
                    "diagnosis_layer": node.get("diagnosis_layer"),
                    "not_exposed_to_differential_reviewers": True,
                },
            })
        if node.get("scale_up_allowed") is True:
            scale.append({"checkpoint": "pre_scale_collision_recheck", "subject_id": subject, "dossier": dossier})
    mem = state.get("mem_xfer_workflow") or {}
    second = mem.get("second_model") or {}
    if second.get("authorized") is True:
        scale.append({
            "checkpoint": "pre_scale_collision_recheck", "subject_id": "p0-mem-xfer-causal",
            "dossier": {"second_model": second, "workflow": mem.get("support_enriched_analysis")},
        })
    return weak, scale


def detect_candidates() -> list[dict[str, Any]]:
    economy, launch = _admission_candidates()
    weak, scale = _diagnosis_candidates()
    rows = _premortem_candidates() + economy + launch + weak + scale
    seen, out = set(), []
    for row in rows:
        key = (row["checkpoint"], row["subject_id"])
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def _state_path(storage: StorageSettings) -> Path:
    return storage.run_dir / "ai-consultation" / "automation-state.json"


def _empty_state() -> dict[str, Any]:
    return {
        "schema_version": "1.0", "initialized_at": _now(), "updated_at": _now(),
        "baseline_initialized": False, "seen": {}, "cases": {},
    }


def _case_id(checkpoint: str, subject_id: str, input_hash: str) -> str:
    raw = f"{checkpoint}|{subject_id}|{input_hash}".encode("utf-8")
    return "aic-" + hashlib.sha256(raw).hexdigest()[:20]


def _atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def sync_triggers(storage: StorageSettings, *, bootstrap_execute: bool = False) -> tuple[dict[str, Any], list[str]]:
    path = _state_path(storage)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = _load(path, _empty_state())
    candidates = detect_candidates()
    created: list[str] = []
    if not state.get("baseline_initialized") and not bootstrap_execute:
        for row in candidates:
            state.setdefault("seen", {}).setdefault(row["checkpoint"], {})[row["subject_id"]] = _hash(row["dossier"])
        state["baseline_initialized"] = True
        state["baseline_subjects"] = len(candidates)
        state["baseline_at"] = _now()
    else:
        state["baseline_initialized"] = True
        for row in candidates:
            input_hash = _hash(row["dossier"])
            prior = (state.get("seen") or {}).get(row["checkpoint"], {}).get(row["subject_id"])
            if prior == input_hash:
                continue
            case_id = _case_id(row["checkpoint"], row["subject_id"], input_hash)
            if case_id not in state.setdefault("cases", {}):
                state["cases"][case_id] = {
                    "case_id": case_id, "checkpoint": row["checkpoint"], "subject_id": row["subject_id"],
                    "input_hash": input_hash, "created_at": _now(), "status": "pending",
                    "dossier": row["dossier"], "reviews": {}, "machine_check_requests": [], "unresolved_high_risk": 0,
                    "single_diagnosis_baseline": dict(row.get("single_diagnosis_baseline") or {}),
                }
                created.append(case_id)
            state.setdefault("seen", {}).setdefault(row["checkpoint"], {})[row["subject_id"]] = input_hash
    _sync_failure_differential_scores(state)
    state["updated_at"] = _now()
    _atomic_json(path, state)
    return state, created


PRELAUNCH_CHECKPOINTS = ("idea_premortem", "economy_red_team", "pre_launch_stress_review")


def _waiver_path(storage: StorageSettings, case_id: str) -> Path:
    return storage.run_dir / "ai-consultation" / "waivers" / f"{case_id}.json"


def _valid_waiver(storage: StorageSettings, case_id: str) -> bool:
    payload = _load(_waiver_path(storage, case_id), {})
    return bool(payload.get("accepted") is True and str(payload.get("reason") or "").strip())


def consultation_launch_clearance(storage: StorageSettings, subject_id: str) -> dict[str, Any]:
    path = _state_path(storage)
    if not path.exists():
        return {"pass": False, "subject_id": subject_id, "blockers": ["ai-consultation-baseline-not-initialized"], "checkpoints": []}
    state, created = sync_triggers(storage)
    if created:
        write_public_state(public_state(state, created, []), storage=storage)
    current = [row for row in detect_candidates() if row.get("subject_id") == subject_id and row.get("checkpoint") in PRELAUNCH_CHECKPOINTS]
    blockers, details = [], []
    for row in current:
        checkpoint = str(row["checkpoint"])
        input_hash = _hash(row["dossier"])
        matching = [case for case in (state.get("cases") or {}).values() if case.get("checkpoint") == checkpoint and case.get("subject_id") == subject_id and case.get("input_hash") == input_hash]
        if not matching:
            details.append({"checkpoint": checkpoint, "status": "baseline-grandfathered"})
            continue
        case = matching[-1]
        case_id = str(case.get("case_id") or "")
        if _valid_waiver(storage, case_id):
            details.append({"checkpoint": checkpoint, "status": "human-waiver", "case_id": case_id})
            continue
        status = str(case.get("status") or "pending")
        unresolved = [request for request in case.get("machine_check_requests") or [] if request.get("severity") == "high" and request.get("disposition") == "unresolved"]
        if status != "complete":
            blockers.append(f"ai-consultation-{checkpoint}-{status}")
        if unresolved:
            blockers.append(f"ai-consultation-{checkpoint}-unresolved-high-risk")
        details.append({"checkpoint": checkpoint, "status": status, "case_id": case_id, "unresolved_high_risk": len(unresolved)})
    return {"pass": not blockers, "subject_id": subject_id, "blockers": blockers, "checkpoints": details, "created_pending_cases": created}


def write_residual_risk_waiver(storage: StorageSettings, case_id: str, reason: str) -> dict[str, Any]:
    if not reason.strip():
        raise ValueError("residual-risk waiver requires an explicit reason")
    payload = {"schema_version": "1.0", "case_id": case_id, "accepted": True, "reason": reason.strip(), "created_at": _now(), "scientific_authority": "human-explicit-residual-risk-acceptance"}
    _atomic_json(_waiver_path(storage, case_id), payload)
    state = _load(_state_path(storage), _empty_state())
    case = (state.get("cases") or {}).get(case_id)
    if case:
        for request in case.get("machine_check_requests") or []:
            if request.get("severity") == "high" and request.get("disposition") == "unresolved":
                request["disposition"] = "human_accepts_residual_risk_with_reason"
                request["disposition_evidence"] = reason.strip()
                request["disposed_at"] = _now()
        case["unresolved_high_risk"] = 0
        case["human_waiver"] = {"reason": reason.strip(), "created_at": payload["created_at"]}
        case["updated_at"] = _now()
        state["updated_at"] = _now()
        _atomic_json(_state_path(storage), state)
    write_public_state(public_state(state, [], []), storage=storage)
    return payload


def record_finding_disposition(
    storage: StorageSettings,
    case_id: str,
    request_index: int,
    disposition: str,
    evidence: str,
) -> dict[str, Any]:
    if disposition not in ALLOWED_DISPOSITIONS:
        raise ValueError(f"unsupported AI finding disposition: {disposition}")
    if not evidence.strip():
        raise ValueError("AI finding disposition requires evidence")
    path = _state_path(storage)
    state = _load(path, _empty_state())
    case = (state.get("cases") or {}).get(case_id)
    if not case:
        raise KeyError(case_id)
    requests = case.get("machine_check_requests") or []
    if request_index < 0 or request_index >= len(requests):
        raise IndexError(request_index)
    requests[request_index]["disposition"] = disposition
    requests[request_index]["disposition_evidence"] = evidence.strip()
    requests[request_index]["disposed_at"] = _now()
    case["unresolved_high_risk"] = sum(
        1 for request in requests
        if request.get("severity") == "high" and request.get("disposition") == "unresolved"
    )
    case["updated_at"] = _now()
    state["updated_at"] = _now()
    _atomic_json(path, state)
    write_public_state(public_state(state, [], []), storage=storage)
    return {"case_id": case_id, "request_index": request_index, "disposition": disposition, "unresolved_high_risk": case["unresolved_high_risk"]}


def _prompt(case: dict[str, Any], reviewer: str) -> str:
    spec = _clinic_by_key()[str(case["checkpoint"])]
    source_rule = " Use current web search and primary/official sources for collision claims." if reviewer.startswith("web-gpt") else " Do not invent literature facts you cannot verify."
    differential_rule = ""
    if str(case.get("checkpoint") or "") == "post_screen_differential_diagnosis":
        differential_rule = (
            " Also return ranked_failure_hypotheses: a list of 1-3 objects with failure_layer, rationale, and repair_route. "
            f"failure_layer must be one of {sorted(FAILURE_LAYER_SPECS)}. Treat the dossier as pre-adjudication evidence: do not infer or assume a final failure label."
        )
    return (
        f"You are {reviewer}, an independent research red-team reviewer. Do not see other reviewers' answers. "
        "This consultation is diagnostic only: you cannot authorize GPU, a second backbone, METHOD-PASS, or METHOD-FAIL."
        + source_rule + "\n\n"
        f"CHECKPOINT: {case['checkpoint']}\nPURPOSE: {spec['purpose']}\n"
        f"QUESTIONS: {json.dumps(spec['questions'], ensure_ascii=False)}\n"
        f"MACHINE TARGETS: {json.dumps(spec['compile_to'], ensure_ascii=False)}\n"
        f"DOSSIER: {json.dumps(case['dossier'], ensure_ascii=False)}\n\n"
        "Return JSON only with keys reviewer, risk_level(low|medium|high), summary, findings, recommended_action"
        + (", ranked_failure_hypotheses" if differential_rule else "") + ". "
        "findings is a list of objects with type, severity(low|medium|high), claim, cheapest_falsifier, compile_to. "
        + differential_rule + " Never use majority vote or say the experiment is authorized."
    )


def _review_web(case: dict[str, Any], output_dir: Path, timeout: int) -> dict[str, Any]:
    output = output_dir / "web-gpt.md"
    command = [
        sys.executable, str(PROJECT_ROOT / "scripts" / "project_web_gpt.py"),
        "--json", "--timeout", str(timeout), "--slug", f"ai-clinic-{case['case_id'][:24]}",
        "--output", str(output), _prompt(case, "web-gpt-current-source-review"),
    ]
    try:
        run = subprocess.run(command, cwd=PROJECT_ROOT, text=True, capture_output=True, timeout=timeout + 60, check=False)
        if run.returncode != 0 or not output.exists():
            return {"status": "missing", "reviewer": "web-gpt-current-source-review", "error": (run.stderr or run.stdout)[-1200:]}
        text = output.read_text(encoding="utf-8").strip()
        return {"status": "complete", "reviewer": "web-gpt-current-source-review", "payload": extract_json_object(text), "raw_path": str(output)}
    except Exception as error:
        return {"status": "missing", "reviewer": "web-gpt-current-source-review", "error": f"{type(error).__name__}: {error}"}


def _review_ark(case: dict[str, Any], output_dir: Path, model: str) -> dict[str, Any]:
    try:
        base = ArkSettings.from_env()
        settings = ArkSettings(
            api_key=base.api_key,
            base_url=base.base_url,
            default_model=base.default_model,
            timeout_seconds=float(os.getenv("AUTOMATION_AI_CLINIC_ARK_TIMEOUT", "60")),
            max_retries=int(os.getenv("AUTOMATION_AI_CLINIC_ARK_RETRIES", "0")),
        )
        response = ArkResponsesClient(settings).respond(_prompt(case, model), model=model, max_output_tokens=2200, temperature=0.1)
        text = response.get("text") or ""
        payload = extract_json_object(text)
        raw = output_dir / f"{model}.txt"
        raw.write_text(text + "\n", encoding="utf-8")
        return {"status": "complete", "reviewer": model, "resolved_model": response.get("resolved_model"), "payload": payload, "raw_path": str(raw)}
    except Exception as error:
        return {"status": "missing", "reviewer": model, "error": f"{type(error).__name__}: {error}"}


def _diagnostic_hypotheses_from_reviews(case: dict[str, Any]) -> list[dict[str, Any]]:
    """Aggregate independent reviewer hypotheses for diagnostic ranking only, never as truth."""
    by_layer: dict[str, dict[str, Any]] = {}
    for review in (case.get("reviews") or {}).values():
        if review.get("status") != "complete":
            continue
        reviewer = str(review.get("reviewer") or "unknown")
        for rank, raw in enumerate((review.get("payload") or {}).get("ranked_failure_hypotheses") or [], start=1):
            if not isinstance(raw, dict):
                continue
            layer = str(raw.get("failure_layer") or "")
            if layer not in FAILURE_LAYER_SPECS:
                continue
            rationale = str(raw.get("rationale") or "").strip()
            route = str(raw.get("repair_route") or "").strip()
            if not rationale or not route:
                continue
            row = by_layer.setdefault(layer, {"failure_layer": layer, "supporting_reviewers": [], "best_rank": rank, "rationales": [], "repair_routes": []})
            row["supporting_reviewers"].append(reviewer)
            row["best_rank"] = min(int(row["best_rank"]), rank)
            row["rationales"].append(rationale)
            row["repair_routes"].append(route)
    ranked = sorted(by_layer.values(), key=lambda row: (-len(set(row["supporting_reviewers"])), int(row["best_rank"]), row["failure_layer"]))[:3]
    evidence_ref = f"ai-consultation:{case.get('case_id')}:input:{case.get('input_hash')}"
    return [
        {
            "failure_layer": row["failure_layer"],
            "rationale": " | ".join(dict.fromkeys(row["rationales"]))[:1400],
            "evidence_refs": [evidence_ref],
            "repair_route": " | ".join(dict.fromkeys(row["repair_routes"]))[:800],
            "diagnostic_support_count": len(set(row["supporting_reviewers"])),
        }
        for row in ranked
    ]


def _freeze_failure_differential(case: dict[str, Any]) -> None:
    if str(case.get("checkpoint") or "") != "post_screen_differential_diagnosis":
        return
    # Freeze only after the full independent panel is complete; a partial panel is missing evidence,
    # not permission to lock a lower-budget hypothesis set. The final failure label must still be hidden.
    if str(case.get("status") or "") != "complete":
        case["failure_differential_status"] = "WAIT_COMPLETE_INDEPENDENT_PANEL"
        return
    # An idea may already have an older terminal label from a prior experiment cycle. Record that
    # identity at freeze time, but do not expose it to reviewers and do not use it as the target.
    # A prospective score is allowed only after a *new* independent terminal-evidence identity appears.
    prior_final = _final_failure_row(str(case.get("subject_id") or ""))
    case["failure_differential_final_identity_at_freeze"] = _final_failure_identity(prior_final)
    hypothesis_set = build_failure_hypothesis_set(
        case_id=str(case.get("case_id") or ""),
        evidence_refs=[f"ai-consultation:{case.get('case_id')}:input:{case.get('input_hash')}"],
        hypotheses=_diagnostic_hypotheses_from_reviews(case),
        final_label_visible=False,
    )
    case["failure_differential_hypothesis_set"] = hypothesis_set
    case["failure_differential_status"] = (
        "HYPOTHESIS_SET_FROZEN_WAIT_NEW_FINAL_EVIDENCE"
        if hypothesis_set.get("status") == "HYPOTHESIS_SET_FROZEN"
        else hypothesis_set.get("status")
    )


def _sync_failure_differential_scores(state: dict[str, Any]) -> None:
    for case in (state.get("cases") or {}).values():
        if not isinstance(case, dict) or str(case.get("checkpoint") or "") != "post_screen_differential_diagnosis":
            continue
        hypothesis_set = case.get("failure_differential_hypothesis_set") or {}
        if hypothesis_set.get("status") != "HYPOTHESIS_SET_FROZEN" or case.get("failure_differential_score"):
            continue
        final = _final_failure_row(str(case.get("subject_id") or ""))
        layer = str(final.get("failure_layer") or "")
        evidence = final.get("failure_evidence") or {}
        sha = str(evidence.get("evidence_sha256") or "")
        final_identity = _final_failure_identity(final)
        frozen_identity = str(case.get("failure_differential_final_identity_at_freeze") or "")
        if not layer or not sha or not final_identity or final_identity == frozen_identity:
            case["failure_differential_status"] = "HYPOTHESIS_SET_FROZEN_WAIT_NEW_FINAL_EVIDENCE"
            continue
        score = score_failure_hypothesis_set(
            hypothesis_set,
            final_failure_layer=layer,
            final_evidence_refs=[f"p0-decision:{case.get('subject_id')}:sha256:{sha}"],
            final_label_independently_adjudicated=True,
        )
        baseline_layer = str((case.get("single_diagnosis_baseline") or {}).get("diagnosis_layer") or "")
        score["final_failure_identity"] = final_identity
        score["final_failure_identity_differs_from_freeze"] = True
        score["single_diagnosis_layer"] = baseline_layer
        score["single_diagnosis_correct"] = (baseline_layer == layer) if baseline_layer in FAILURE_LAYER_SPECS else None
        score["scientific_authority"] = False
        case["failure_differential_score"] = score
        case["failure_differential_status"] = score.get("status")


def _synthesize(case: dict[str, Any]) -> None:
    requests: list[dict[str, Any]] = []
    high = 0
    completed = 0
    allowed_targets = set(_clinic_by_key()[str(case["checkpoint"])].get("compile_to") or [])
    for review in (case.get("reviews") or {}).values():
        if review.get("status") != "complete":
            continue
        completed += 1
        payload = review.get("payload") or {}
        for finding in payload.get("findings") or []:
            if not isinstance(finding, dict):
                continue
            severity = str(finding.get("severity") or "").lower()
            if severity == "high":
                high += 1
            requested_target = finding.get("compile_to")
            candidates = requested_target if isinstance(requested_target, list) else [requested_target]
            mapped = next((str(item) for item in candidates if item in allowed_targets), "manual_mapping_required")
            requests.append({
                "reviewer": review.get("reviewer"), "type": finding.get("type"),
                "severity": severity or "unknown", "claim": finding.get("claim"),
                "cheapest_falsifier": finding.get("cheapest_falsifier"), "compile_to": mapped,
                "allowed_targets": sorted(allowed_targets), "disposition": "unresolved",
            })
    case["completed_reviewers"] = completed
    case["missing_reviewers"] = 3 - completed
    case["machine_check_requests"] = requests
    case["unresolved_high_risk"] = high
    case["status"] = "complete" if completed == 3 else ("partial" if completed else "reviewer-unavailable")
    case["scientific_authority"] = False
    case["execution_authorized"] = False
    _freeze_failure_differential(case)
    case["updated_at"] = _now()


def execute_pending(
    storage: StorageSettings,
    state: dict[str, Any],
    *,
    max_cases: int = 1,
    web_enabled: bool = True,
    domestic_models: list[str] | None = None,
) -> list[str]:
    domestic_models = domestic_models or ["glm-5.3", "deepseek-v4-pro", "minimax-m3", "kimi-k3"]
    completed: list[str] = []
    max_attempts = int(os.getenv("AUTOMATION_AI_CLINIC_MAX_ATTEMPTS", "2"))
    pending = [
        row for row in (state.get("cases") or {}).values()
        if row.get("status") in {"pending", "partial", "reviewer-unavailable"}
        and int(row.get("attempt_count") or 0) < max_attempts
    ]
    pending.sort(key=lambda row: (row.get("created_at", ""), row.get("case_id", "")))
    root = storage.run_dir / "ai-consultation" / "cases"
    for case in pending[:max(0, max_cases)]:
        out = root / case["case_id"]
        out.mkdir(parents=True, exist_ok=True)
        case["status"] = "running"
        case["started_at"] = _now()
        case["attempt_count"] = int(case.get("attempt_count") or 0) + 1
        reviews: dict[str, Any] = dict(case.get("reviews") or {})
        if (reviews.get("web-gpt") or {}).get("status") != "complete":
            if web_enabled:
                reviews["web-gpt"] = _review_web(case, out, int(os.getenv("AUTOMATION_AI_CLINIC_WEB_TIMEOUT", "180")))
            else:
                reviews["web-gpt"] = {"status": "missing", "reviewer": "web-gpt-current-source-review", "error": "disabled"}
        for index, model in enumerate(domestic_models[:2], start=1):
            key = f"domestic-{index}"
            if (reviews.get(key) or {}).get("status") != "complete":
                reviews[key] = _review_ark(case, out, model)
        configured = len([key for key in reviews if key.startswith("domestic-")])
        for index in range(configured + 1, 3):
            reviews[f"domestic-{index}"] = {"status": "missing", "reviewer": f"domestic-{index}", "error": "not-configured"}
        case["reviews"] = reviews
        _synthesize(case)
        completed.append(case["case_id"])
    _sync_failure_differential_scores(state)
    state["updated_at"] = _now()
    _atomic_json(_state_path(storage), state)
    return completed


def public_state(state: dict[str, Any], created: list[str], executed: list[str]) -> dict[str, Any]:
    cases = list((state.get("cases") or {}).values())
    counts: dict[str, int] = {}
    for row in cases:
        key = str(row.get("status") or "unknown")
        counts[key] = counts.get(key, 0) + 1
    differential_frozen = [row for row in cases if (row.get("failure_differential_hypothesis_set") or {}).get("status") == "HYPOTHESIS_SET_FROZEN"]
    differential_scored = [row for row in cases if (row.get("failure_differential_score") or {}).get("status") == "PROSPECTIVE_CASE_SCORED"]
    differential_waiting_final = [row for row in differential_frozen if row.get("failure_differential_status") == "HYPOTHESIS_SET_FROZEN_WAIT_NEW_FINAL_EVIDENCE"]
    differential_single_evaluable = [row for row in differential_scored if (row.get("failure_differential_score") or {}).get("single_diagnosis_correct") in {True, False}]
    recent = []
    for row in sorted(cases, key=lambda item: item.get("created_at", ""), reverse=True)[:8]:
        recent.append({
            "case_id": row.get("case_id"), "checkpoint": row.get("checkpoint"),
            "subject_id": row.get("subject_id"), "status": row.get("status"),
            "completed_reviewers": row.get("completed_reviewers", 0),
            "missing_reviewers": row.get("missing_reviewers", 0),
            "unresolved_high_risk": row.get("unresolved_high_risk", 0),
            "human_waiver": bool(row.get("human_waiver")),
            "failure_differential_status": row.get("failure_differential_status"),
        })
    return {
        "schema_version": "1.0", "generated_at": _now(), "policy": PUBLIC_POLICY,
        "clinic_policy": {key: CLINIC_POLICY[key] for key in (
            "ai_vote_can_authorize_gpu", "ai_vote_can_authorize_second_backbone",
            "ai_vote_can_emit_method_pass_fail", "high_risk_findings_must_be_compiled_into_machine_checks",
        )},
        "summary": {
            "baseline_initialized": bool(state.get("baseline_initialized")),
            "baseline_subjects": int(state.get("baseline_subjects") or 0),
            "cases": len(cases), "created_this_cycle": len(created), "executed_this_cycle": len(executed),
            "pending": counts.get("pending", 0), "partial": counts.get("partial", 0),
            "complete": counts.get("complete", 0), "reviewer_unavailable": counts.get("reviewer-unavailable", 0),
            "retryable": sum(1 for row in cases if row.get("status") in {"pending", "partial", "reviewer-unavailable"} and int(row.get("attempt_count") or 0) < int(os.getenv("AUTOMATION_AI_CLINIC_MAX_ATTEMPTS", "2"))),
            "waived_cases": sum(1 for row in cases if row.get("human_waiver")),
            "unresolved_high_risk": sum(int(row.get("unresolved_high_risk") or 0) for row in cases),
            "failure_differential_frozen": len(differential_frozen),
            "failure_differential_scored": len(differential_scored),
            "failure_differential_waiting_new_final": len(differential_waiting_final),
            "failure_differential_top1_correct": sum(bool((row.get("failure_differential_score") or {}).get("top1_correct")) for row in differential_scored),
            "failure_differential_topk_contains_truth": sum(bool((row.get("failure_differential_score") or {}).get("topk_contains_truth")) for row in differential_scored),
            "failure_differential_single_diagnosis_evaluable": len(differential_single_evaluable),
            "failure_differential_single_diagnosis_correct": sum((row.get("failure_differential_score") or {}).get("single_diagnosis_correct") is True for row in differential_single_evaluable),
        },
        "finding_dispositions": sorted(ALLOWED_DISPOSITIONS),
        "recent_cases": recent,
    }


def write_public_state(
    payload: dict[str, Any],
    *,
    storage: StorageSettings | Any | None = None,
    json_path: Path | None = None,
    js_path: Path | None = None,
) -> dict[str, Any]:
    artifact_dir = Path(getattr(storage, "site_artifact_dir", PROJECT_ROOT / "generated")) if storage is not None else PROJECT_ROOT / "generated"
    json_path = json_path or artifact_dir / "ai-consultation-automation.json"
    js_path = js_path or artifact_dir / "ai-consultation-automation.js"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_path.write_text("window.AI_CONSULTATION_AUTOMATION = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    return payload


def run_ai_consultation_automation(
    storage: StorageSettings | None = None,
    *,
    execute: bool = True,
    max_cases: int = 1,
    bootstrap_execute: bool = False,
) -> dict[str, Any]:
    storage = storage or StorageSettings.from_env()
    storage.ensure()
    state, created = sync_triggers(storage, bootstrap_execute=bootstrap_execute)
    executed: list[str] = []
    if execute and state.get("baseline_initialized"):
        models = [
            item.strip()
            for item in os.getenv("AUTOMATION_AI_CLINIC_ARK_MODELS", "glm-5.3,deepseek-v4-pro,minimax-m3,kimi-k3").split(",")
            if item.strip()
        ]
        executed = execute_pending(
            storage, state, max_cases=max_cases,
            web_enabled=os.getenv("AUTOMATION_AI_CLINIC_WEB", "1") != "0",
            domestic_models=models,
        )
    return write_public_state(public_state(state, created, executed), storage=storage)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync/execute content-addressed AI consultation checkpoints.")
    parser.add_argument("--execute", action="store_true", help="Execute bounded external reviewers after trigger sync.")
    parser.add_argument("--max-cases", type=int, default=1)
    parser.add_argument("--waive-case", default="")
    parser.add_argument("--waiver-reason", default="")
    parser.add_argument("--dispose-case", default="")
    parser.add_argument("--request-index", type=int, default=-1)
    parser.add_argument("--disposition", choices=sorted(ALLOWED_DISPOSITIONS), default=None)
    parser.add_argument("--evidence", default="")
    args = parser.parse_args()
    storage = StorageSettings.from_env()
    if args.waive_case:
        payload = write_residual_risk_waiver(storage, args.waive_case, args.waiver_reason)
    elif args.dispose_case:
        if args.disposition is None:
            parser.error("--dispose-case requires --disposition")
        payload = record_finding_disposition(storage, args.dispose_case, args.request_index, args.disposition, args.evidence)
    else:
        payload = run_ai_consultation_automation(storage, execute=args.execute, max_cases=max(0, args.max_cases))
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
