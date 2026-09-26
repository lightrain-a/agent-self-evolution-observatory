"""Evidence-driven discovery planning, not scientific adjudication or execution.

HEIRS retrospective motivates the workflow, not the empirical truth of any case.
The bounded contract is shared by the legacy and canonical formulation prompts.
Existing primary grounding, scoped memory, budget and scientific gates stay intact.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
AXES = ("object", "update", "feedback", "selection", "deployment_shift", "budget")
AUTHORITY = {key: False for key in ("scientific", "method", "experiment", "p0", "gpu", "human_judgment")}
WORKFLOW = (
    "Existing system + literature", "Audited anomaly", "Structural analogy",
    "Competing hypotheses", "Cheapest distinguishing test", "Scoped evidence decision",
    "Minimal method", "Frozen prospective evaluation", "Claim–evidence closure",
)
POLICY = {
    "analogy_is_inspiration_not_target_evidence": True,
    "method_primitive_reuse_is_not_automatic_novelty": True,
    "missing_or_weak_evidence_is_not_falsification": True,
    "execution_failure_does_not_kill_scientific_hypothesis": True,
    "generated_plans_cannot_assert_experiment_results": True,
    "human_advisor_judgment_is_not_simulated": True,
    "existing_problem_budget_and_execution_gates_unchanged": True,
    "historical_cases_require_original_artifact_verification": True,
    "no_provider_calls_or_experiment_launches": True,
}
ANALOGY_ROUTES = (
    {"domain": "optimization trajectories", "query": "checkpoint selection temporal diversity deployment shift", "caution": "Text artifacts have no guaranteed weight-space averaging geometry."},
    {"domain": "adversarial transfer", "query": "transferability surrogate ensemble source target model", "caution": "Attack objectives and gradients do not establish Skill transferability."},
    {"domain": "adaptive evaluation", "query": "fixed budget best arm identification successive halving", "caution": "A standard selector is a baseline or reusable primitive, not automatic novelty."},
    {"domain": "software evolution", "query": "compatibility regression historical versions environment change", "caution": "A compatibility analogy still needs matched evidence in the target system."},
)


def _text(value: Any, limit: int = 1200) -> str:
    return value.strip()[:limit] if isinstance(value, str) else ""


def _obj(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _rows(value: Any, limit: int = 8) -> list[dict[str, Any]]:
    return [row for row in value[:limit] if isinstance(row, dict)] if isinstance(value, list) else []


def _strings(value: Any, limit: int = 24) -> list[str]:
    return list(dict.fromkeys(_text(v, 400) for v in value[:limit] if _text(v, 400))) if isinstance(value, list) else []


def _number(value: Any) -> int | float | None:
    if type(value) not in (int, float):
        return None
    return value if math.isfinite(value) and value >= 0 else None


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def formation_shape() -> dict[str, Any]:
    """Small planning schema; two to four hypotheses, at most two analogies."""
    return {
        "intuition": "plain-language intuition; not a result",
        "example": "one concrete example, explicitly hypothetical unless evidenced",
        "observation": {"claim": "observed anomaly, not its explanation", "evidence_refs": ["provided primary ref"], "scope": "model/task/protocol boundary"},
        "system": {axis: "concrete source-system description" for axis in AXES},
        "analogies": [{"source_domain": "source field", "source_refs": ["provided ref or unresolved citation to retrieve"], "mapping": {axis: "source -> target mapping" for axis in AXES}, "breaks": ["assumption that does not transfer"], "prediction": "falsifiable target-domain prediction"}],
        "no_analogy_reason": "empty if mapped analogies exist; otherwise explain the unsuccessful search",
        "hypotheses": [{"id": "H1", "kind": "MECHANISM|ALTERNATIVE", "claim": "testable explanation", "scope": "bounded claim", "prediction": "observable prediction", "falsifier": "observation contradicting this exact claim", "evidence_refs": []}],
        "p0": {"mode": "OFFLINE_REPLAY|NEW_EXECUTIONS", "intervention": "what changes", "controls": ["what is fixed"], "comparator": "strongest simple same-information alternative", "observable": "measured quantity", "hypothesis_predictions": {"H1": "outcome under H1", "H2": "different outcome under H2"}, "data_source": "audited dataset/artifact ref", "budget": {"candidates": 2, "tasks": 16, "repeats": 1, "provider_calls_per_evaluation": 1, "retry_call_allowance": 0, "max_new_calls": 32, "estimated_wall_seconds": None, "estimate_basis": "measured or assumed throughput; unknown stays null"}, "decision_rule": "criterion for support vs counterevidence", "inconclusive_rule": "what insufficient/noisy evidence means", "integrity_checks": ["parser", "label validity", "timeouts", "matched tasks"], "stop_rule": "bounded budget/invalid execution rule"},
        "claim_boundary": "what is and is not claimed",
        "prospective_requirement": "what must be frozen and held out before method confirmation",
    }


def formation_prompt() -> str:
    return (
        "\nMETHOD-FORMATION PLANNING CONTRACT (zero scientific/execution authority): "
        "Attach method_formation to each emitted problem candidate, using the schema below. "
        "Separate observed evidence from explanation. Give a plain-language intuition and concrete example. "
        "Inspect the existing system's object/update/feedback/selection/deployment shift/budget. "
        "Try structural analogies, including optimization checkpoints, adversarial transfer, and budgeted selection when relevant; "
        "never force an analogy. Use at most two, with all six mappings, source references, broken assumptions and a falsifiable prediction. "
        "A source-domain citation does NOT prove target-domain validity. An unresolved citation becomes a retrieval request, not evidence. "
        "Provide two to four distinct competing hypotheses, including a non-favored alternative. "
        "Specify one cheapest test with DIFFERENT predictions under these hypotheses, fixed controls, strongest simple comparator, "
        "data provenance, candidate×task×repeat logical evaluations, provider calls per evaluation plus retry allowance, "
        "estimated time with an explicit basis or null, decision/inconclusive/stop rules, and integrity checks. "
        "A multi-turn agent evaluation can make many provider calls; never equate these two cost units. "
        "Prefer existing audited offline artifacts before new calls. A proposed test is NOT an executed test. "
        "Do not invent outcomes, call receipts, p-values, human feedback, PASS or scientific STOP. "
        "Weak correlation/low power is inconclusive, not automatic falsification. An infrastructure failure is not a failed scientific principle. "
        "Do not compose a new method or launch P0 before existing gates. Human advisor judgment remains external. "
        "Historical HEIRS chat summaries are workflow inspiration only and cannot serve as measured evidence. "
        "Use the method_formation schema in the output shape. Keep the entire card below approximately 500 words, "
        "using two hypotheses and one analogy unless additional entries are essential. Unknown quantities stay null instead of fabricated.\n"
    )


def normalize_formation(raw: Any) -> dict[str, Any]:
    """Allowlist planning fields. Never trust model-supplied status or authority."""
    if not isinstance(raw, dict) or not raw:
        return {}
    obs, p0 = _obj(raw.get("observation")), _obj(raw.get("p0"))
    budget = _obj(p0.get("budget"))
    analogies = []
    for row in _rows(raw.get("analogies"), 2):
        analogies.append({
            "source_domain": _text(row.get("source_domain")), "source_refs": _strings(row.get("source_refs")),
            "mapping": {axis: _text(_obj(row.get("mapping")).get(axis)) for axis in AXES},
            "breaks": _strings(row.get("breaks")), "prediction": _text(row.get("prediction")),
        })
    hypotheses = [{**{k: _text(row.get(k)) for k in ("id", "kind", "claim", "scope", "prediction", "falsifier")},
                   "evidence_refs": _strings(row.get("evidence_refs")), "status": "PROPOSED"}
                  for row in _rows(raw.get("hypotheses"), 4)]
    return {
        "schema_version": SCHEMA_VERSION,
        **{k: _text(raw.get(k)) for k in ("intuition", "example", "no_analogy_reason", "claim_boundary", "prospective_requirement")},
        "observation": {"claim": _text(obs.get("claim")), "scope": _text(obs.get("scope")), "evidence_refs": _strings(obs.get("evidence_refs"))},
        "system": {axis: _text(_obj(raw.get("system")).get(axis)) for axis in AXES},
        "analogies": analogies, "hypotheses": hypotheses,
        "p0": {
            **{k: _text(p0.get(k)) for k in ("mode", "intervention", "comparator", "observable", "data_source", "decision_rule", "inconclusive_rule", "stop_rule")},
            "controls": _strings(p0.get("controls")), "integrity_checks": _strings(p0.get("integrity_checks")),
            "hypothesis_predictions": {_text(k, 80): _text(v) for k, v in list(_obj(p0.get("hypothesis_predictions")).items())[:4]},
            "budget": {**{k: _number(budget.get(k)) for k in ("candidates", "tasks", "repeats", "provider_calls_per_evaluation", "retry_call_allowance", "max_new_calls", "estimated_wall_seconds")}, "estimate_basis": _text(budget.get("estimate_basis"))},
            "execution_status": "NOT_EXECUTED",
        },
        "scientific_status": "NOT_EVALUATED", "authority": dict(AUTHORITY),
    }


def audit_formation(raw: Any, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Audit planning completeness only; never decide scientific validity."""
    card = normalize_formation(raw)
    registry = registry or {}
    missing: list[str] = []
    retrieval: list[str] = []
    if not card:
        return {"status": "NEEDS_PLAN", "missing": ["method_formation"], "retrieval_refs": [], "scientific_status": "NOT_EVALUATED", "authority": dict(AUTHORITY)}
    for key in ("intuition", "example", "claim_boundary", "prospective_requirement"):
        if not card[key]: missing.append(key)
    for key in ("claim", "scope", "evidence_refs"):
        if not card["observation"][key]: missing.append("observation." + key)
    for ref in card["observation"]["evidence_refs"]:
        if ref not in registry: retrieval.append(ref)
    for axis in AXES:
        if not card["system"][axis]: missing.append("system." + axis)
    if not card["analogies"] and not card["no_analogy_reason"]:
        missing.append("analogy-or-explicit-no-analogy-reason")
    for i, row in enumerate(card["analogies"]):
        for key in ("source_domain", "source_refs", "breaks", "prediction"):
            if not row[key]: missing.append(f"analogies.{i}.{key}")
        for axis in AXES:
            if not row["mapping"][axis]: missing.append(f"analogies.{i}.mapping.{axis}")
        retrieval.extend(ref for ref in row["source_refs"] if ref not in registry)
    hypotheses = card["hypotheses"]
    ids = [h["id"] for h in hypotheses]
    if len(hypotheses) < 2: missing.append("at-least-two-competing-hypotheses")
    if len(set(ids)) != len(ids) or "" in ids: missing.append("unique-hypothesis-ids")
    claims = [" ".join(h["claim"].lower().split()) for h in hypotheses]
    if len(set(claims)) != len(claims): missing.append("distinct-hypothesis-claims")
    if not any(h["kind"] == "ALTERNATIVE" for h in hypotheses): missing.append("alternative-hypothesis")
    for i, h in enumerate(hypotheses):
        for key in ("claim", "scope", "prediction", "falsifier"):
            if not h[key]: missing.append(f"hypotheses.{i}.{key}")
        if h["kind"] not in {"MECHANISM", "ALTERNATIVE"}: missing.append(f"hypotheses.{i}.kind")
        retrieval.extend(ref for ref in h["evidence_refs"] if ref not in registry)
    p0 = card["p0"]
    for key in ("intervention", "controls", "comparator", "observable", "data_source", "decision_rule", "inconclusive_rule", "integrity_checks", "stop_rule"):
        if not p0[key]: missing.append("p0." + key)
    predictions = p0["hypothesis_predictions"]
    if set(predictions) != set(ids) or any(not v for v in predictions.values()): missing.append("p0.prediction-for-each-hypothesis")
    if len({" ".join(v.lower().split()) for v in predictions.values()}) < 2: missing.append("p0.distinguishing-predictions")
    b = p0["budget"]
    counts_valid = all(type(b[k]) is int and b[k] > 0 for k in ("candidates", "tasks", "repeats"))
    if not counts_valid: missing.append("p0.budget-positive-integer-counts")
    if type(b["max_new_calls"]) is not int: missing.append("p0.budget.max_new_calls")
    if b["estimated_wall_seconds"] is None or not b["estimate_basis"]: missing.append("p0.budget.time-estimate-and-basis")
    logical_evaluations = math.prod(b[k] for k in ("candidates", "tasks", "repeats")) if counts_valid else None
    if p0["mode"] not in {"OFFLINE_REPLAY", "NEW_EXECUTIONS"}: missing.append("p0.mode")
    if p0["mode"] == "OFFLINE_REPLAY" and b["max_new_calls"] != 0: missing.append("offline-replay-cannot-budget-new-calls")
    calls_per_eval, retries = b["provider_calls_per_evaluation"], b["retry_call_allowance"]
    estimated_new_calls = 0 if p0["mode"] == "OFFLINE_REPLAY" else None
    if p0["mode"] == "NEW_EXECUTIONS":
        if type(calls_per_eval) is not int or calls_per_eval < 1 or type(retries) is not int:
            missing.append("p0.provider-call-estimate-and-retry-allowance")
        elif counts_valid:
            estimated_new_calls = logical_evaluations * calls_per_eval + retries
            if type(b["max_new_calls"]) is int and b["max_new_calls"] < estimated_new_calls:
                missing.append("p0.call-budget-below-estimated-provider-calls")
    return {
        "status": "PLAN_FIELDS_COMPLETE" if not missing and not retrieval else "NEEDS_PLAN_OR_RETRIEVAL",
        "missing": sorted(set(missing)), "retrieval_refs": sorted(set(retrieval)),
        "logical_evaluations": logical_evaluations, "estimated_new_provider_calls": estimated_new_calls,
        "reference_check": "PRESENT_IN_REGISTRY_ONLY_NOT_SEMANTIC_GROUNDING",
        "scientific_status": "NOT_EVALUATED", "authority": dict(AUTHORITY),
    }


def public_formation_summary(raw: Any, audit: Any) -> dict[str, Any]:
    """Publish plan metadata, never its private source text or unresolved refs."""
    card, checked = normalize_formation(raw), _obj(audit)
    status = checked.get("status")
    if status not in {"NEEDS_PLAN", "NEEDS_PLAN_OR_RETRIEVAL", "PLAN_FIELDS_COMPLETE"}:
        status = "NEEDS_PLAN"
    return {"schema_version": SCHEMA_VERSION, "planning_status": status,
            "hypotheses": len(card.get("hypotheses", [])), "analogies": len(card.get("analogies", [])),
            "missing": _strings(checked.get("missing"), 100),
            "retrieval_count": len(_strings(checked.get("retrieval_refs"))),
            "card_sha256": _digest(card), "scientific_status": "NOT_EVALUATED", "authority": dict(AUTHORITY)}


def build_method_formation_state(generator_state: dict[str, Any], primary_state: dict[str, Any]) -> dict[str, Any]:
    registry = {r["ref"]: r for r in _rows(primary_state.get("records"), 2000) if r.get("ref") and r.get("primary_source_verified") is True}
    rows, seen = [], set()
    candidates = _rows(generator_state.get("candidates"), 100) + _rows(generator_state.get("pre_f0_candidates"), 100)
    for candidate in candidates:
        cid = _text(candidate.get("candidate_id"), 120)
        if not cid or cid in seen: continue
        seen.add(cid)
        card = normalize_formation(candidate.get("method_formation"))
        published = _obj(candidate.get("method_formation_summary"))
        if not card and published.get("schema_version") == SCHEMA_VERSION:
            status = published.get("planning_status")
            meta = {"planning_status": status if status in {"NEEDS_PLAN", "NEEDS_PLAN_OR_RETRIEVAL", "PLAN_FIELDS_COMPLETE"} else "NEEDS_PLAN",
                    "hypotheses": min(4, int(_number(published.get("hypotheses")) or 0)),
                    "analogies": min(2, int(_number(published.get("analogies")) or 0)),
                    "missing": _strings(published.get("missing"), 100),
                    "retrieval_count": int(_number(published.get("retrieval_count")) or 0),
                    "card_sha256": _text(published.get("card_sha256"), 64)}
        else:
            meta = public_formation_summary(card, audit_formation(card, registry))
        rows.append({"candidate_id": cid, **meta, "scientific_status": "NOT_EVALUATED"})
    return {
        "schema_version": SCHEMA_VERSION, "status": "PLANNING_AUDIT_AVAILABLE" if rows else "WAIT_CANDIDATE",
        "source_run_id": _text(generator_state.get("run_id")), "workflow": list(WORKFLOW),
        "policy": dict(POLICY), "analogy_routes": list(ANALOGY_ROUTES), "rows": rows,
        "summary": {"candidates": len(rows), "plans_complete": sum(r["planning_status"] == "PLAN_FIELDS_COMPLETE" for r in rows),
                    "needs_work": sum(r["planning_status"] != "PLAN_FIELDS_COMPLETE" for r in rows),
                    "model_calls": 0, "experiments_launched": 0, "automatic_promotions": 0},
        "authority": dict(AUTHORITY),
        "existing_integrations": ["primary evidence registry", "scoped failure memory", "problem and pre-F0 gates", "budget authorization", "claim contribution attribution"],
        "human_consultation": "External human judgment; preparation only, no advisor simulation.",
    }


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".method-formation-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)


def write_method_formation_state(*, project_root: Path = PROJECT_ROOT, generator_state: dict[str, Any] | None = None, primary_state: dict[str, Any] | None = None) -> dict[str, Any]:
    """Deterministic projection only. Malformed source JSON fails without replacing state."""
    def load(filename: str) -> dict[str, Any]:
        path = project_root / "generated" / filename
        if not path.exists(): return {}
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict): raise ValueError(f"Expected object: {filename}")
        return value
    state = build_method_formation_state(
        generator_state if generator_state is not None else load("paper-first-problem-generator-state.json"),
        primary_state if primary_state is not None else load("paper-first-primary-evidence-state.json"),
    )
    target = project_root / "generated" / "discovery-method-formation"
    _atomic_write(target.with_suffix(".json"), json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    _atomic_write(target.with_suffix(".js"), "window.DISCOVERY_METHOD_FORMATION = " + json.dumps(state, ensure_ascii=False, separators=(",", ":")) + ";\n")
    return state


if __name__ == "__main__":
    print(json.dumps(write_method_formation_state()["summary"], ensure_ascii=False))
