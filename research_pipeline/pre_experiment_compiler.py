from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .pre_experiment_execution import compute_graph, measured_throughput, observability_recovery, outcome_semantics
from .pre_experiment_science import baseline_competence, mechanism_identifiability, parameter_provenance, qualification_path, statistical_resolution
from .pre_experiment_specs import GATES, POLICY
from .paper_design_contract import audit_paper_design_contract
from .internal_research_skills import route_internal_skills
from .principle_adjudication import audit_principle_certificate
from .protocol_validity import audit_protocol_validity


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _hash_payload(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _updater_competence_prerequisite(config: dict[str, Any]) -> dict[str, Any]:
    contract = (config.get("pre_experiment") or {}).get("updater_competence") or {}
    if not isinstance(contract, dict) or not contract:
        return {
            "required": True,
            "is_formal_gate": False,
            "passed": False,
            "status": "missing-contract",
            "blockers": ["updater-competence-contract-missing"],
            "scientific_role": "hard prerequisite before Gate 1; failure blocks execution without counting as method failure",
        }
    passed = contract.get("passed") is True
    blockers = [] if passed else ["updater-competence-prerequisite-failed"]
    return {
        **contract,
        "required": True,
        "is_formal_gate": False,
        "passed": passed,
        "blockers": blockers,
        "scientific_role": str(contract.get("scientific_role") or "hard prerequisite before Gate 1; failure blocks execution without counting as method failure"),
    }


def _research_execution_plan(
    idea_id: str,
    principle_certificate: dict[str, Any],
    protocol_validity: dict[str, Any],
    updater_competence: dict[str, Any],
    gates: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    """Compile scientific intent into an auditable execution plan without adding launch authority."""
    contract = principle_certificate.get("contract") or {}
    prediction_ids = [str(row.get("id") or "") for row in contract.get("predictions") or [] if row.get("id")]
    skill_spec = ((config.get("pre_experiment") or {}).get("skill_requirements") or {}) if isinstance(config, dict) else {}
    explicit_skill_caps = [str(x).strip().lower() for x in skill_spec.get("capability_types") or [] if str(x).strip()]
    inferred_skill_caps = set(explicit_skill_caps)
    inferred_skill_caps.update({"statistics", "experiment"})
    if config.get("models"):
        inferred_skill_caps.update({"ml-research", "coding"})
    task_family = str(skill_spec.get("task_family") or ("ai-ml-experiment" if "ml-research" in inferred_skill_caps else "experiment-analysis"))
    internal_skill_route = route_internal_skills({"task_family": task_family, "capability_types": sorted(inferred_skill_caps)})
    plan_core = {
        "idea_id": idea_id,
        "prediction_ids": prediction_ids,
        "dependencies": ["principle-certificate", "protocol-validity", "updater-competence", "pre-experiment-8-of-8"],
        "capability_requirements": ["cpu-falsifier", "gpu-experiment", "independent-analysis"],
        "internal_skill_requirements": sorted(inferred_skill_caps),
        "internal_skill_ids": [str(row.get("skill_id") or "") for row in internal_skill_route.get("selected_skills") or []],
        "expected_artifacts": ["frozen-config", "plan-hash", "incremental-raw-trace", "metric-table", "analysis-provenance", "decision-ledger-update", "persistent-update-effect-realization-audit-when-applicable"],
    }
    checkpoints = [
        {"id": "principle-certificate", "passed": principle_certificate.get("passed") is True},
        {"id": "protocol-validity", "passed": protocol_validity.get("passed") is True},
        {"id": "updater-competence", "passed": updater_competence.get("passed") is True},
        *[{"id": f"gate:{gate['key']}", "passed": gate.get("pass") is True} for gate in gates],
    ]
    return {
        "schema_version": "1.0",
        "source_design": "SCION Research Execution Plan",
        "plan_hash": _hash_payload(plan_core),
        "objective": "Generate decision-relevant evidence for the registered principle predictions under the frozen protocol.",
        "prediction_ids": prediction_ids,
        "dependencies": plan_core["dependencies"],
        "verification_checkpoints": checkpoints,
        "capability_requirements": plan_core["capability_requirements"],
        "internal_skill_requirements": plan_core["internal_skill_requirements"],
        "internal_skill_route": internal_skill_route,
        "expected_artifacts": plan_core["expected_artifacts"],
        "fallback_conditions": [
            {"if": "execution-or-runtime-invalid", "action": "repair execution only; preserve scientific contract"},
            {"if": "protocol-invalid-or-shortcut-detected", "action": "invalidate scientific interpretation and repair protocol"},
            {"if": "experiment-nonidentifiable", "action": "repair substrate/variation before method interpretation"},
            {"if": "operationalization-invalid", "action": "repair measurement bridge before principle update"},
            {"if": "persistent-update-decision-context-support-or-effect-realization-fails", "action": "classify as protocol/operationalization mismatch before method or principle failure; do not rescue by changing scientific thresholds"},
            {"if": "registered-principle-prediction-contradicted-under-all-preconditions", "action": "route to principle adjudicator and human scientific review"},
        ],
        "execution_authority": False,
        "rule": "This plan makes objectives, dependencies, tools, artifacts, checkpoints, and fallback conditions explicit; it never authorizes execution by itself.",
    }


def compile_pre_experiment_card(idea_id: str, config: dict[str, Any], data_root: Path) -> dict[str, Any]:
    if str(config.get("idea_id") or "") != idea_id:
        raise ValueError(f"config idea_id mismatch: {config.get('idea_id')} != {idea_id}")
    paper_design = audit_paper_design_contract(config)
    principle_certificate = audit_principle_certificate(config)
    protocol_validity = audit_protocol_validity(config)
    updater_competence = _updater_competence_prerequisite(config)
    gates = [
        parameter_provenance(config),
        baseline_competence(config, data_root),
        mechanism_identifiability(idea_id, config),
        statistical_resolution(idea_id, config),
        compute_graph(idea_id, config),
        measured_throughput(config),
        observability_recovery(config),
        outcome_semantics(config),
    ]
    if [gate["key"] for gate in gates] != [gate["key"] for gate in GATES]:
        raise RuntimeError("pre-experiment gate order drift")
    research_execution_plan = _research_execution_plan(idea_id, principle_certificate, protocol_validity, updater_competence, gates, config)
    skill_route_ready = (research_execution_plan.get("internal_skill_route") or {}).get("status") == "INTERNAL_SKILL_ROUTE_READY"
    blockers = list(paper_design.get("blockers") or []) + list(principle_certificate.get("blockers") or []) + list(protocol_validity.get("blockers") or []) + list(updater_competence.get("blockers") or []) + [blocker for gate in gates for blocker in gate["blockers"]]
    if not skill_route_ready:
        blockers.append("research-skill-route-hold")
    passed = sum(bool(gate["pass"]) for gate in gates)
    gates_passed = passed == len(gates)
    paper_design_ready = paper_design.get("passed") is True
    principle_ready = principle_certificate.get("passed") is True
    protocol_ready = protocol_validity.get("passed") is True
    updater_competent = updater_competence.get("passed") is True
    config_hash = _hash_payload(config)
    scope = config.get("scope") or {}
    competence = (config.get("pre_experiment") or {}).get("competence") or {}
    return {
        "schema_version": "2.2",
        "compiled_at": _now(),
        "idea_id": idea_id,
        "phase": str(config.get("phase") or "P0"),
        "expected_runtime": {
            "model_names": list(config.get("models") or []),
            "competence_model_name": str(competence.get("model_name") or ""),
            "policy_mode": str(scope.get("policy_mode") or ""),
        },
        "config_hash": config_hash,
        "policy": POLICY,
        "paper_design_prerequisite": paper_design,
        "principle_certificate_prerequisite": principle_certificate,
        "protocol_validity_prerequisite": protocol_validity,
        "updater_competence_prerequisite": updater_competence,
        "research_execution_plan": research_execution_plan,
        "gate_count": len(gates),
        "passed_gates": passed,
        "execution_authorized": paper_design_ready and principle_ready and protocol_ready and updater_competent and gates_passed and skill_route_ready,
        "status": "pass" if paper_design_ready and principle_ready and protocol_ready and updater_competent and gates_passed and skill_route_ready else "blocked",
        "blockers": blockers,
        "gates": gates,
        "compute_graph": next(gate["detail"] for gate in gates if gate["key"] == "compute_graph"),
        "qualification_evidence_path": str(qualification_path(data_root, config) or ""),
    }


def compile_from_path(idea_id: str, config_path: Path, data_root: Path) -> dict[str, Any]:
    return compile_pre_experiment_card(idea_id, _load_json(config_path), data_root)


def write_card(card: dict[str, Any], data_root: Path) -> Path:
    target = data_root / "pre-experiment" / "cards" / str(card["idea_id"]) / f"{str(card['config_hash'])[:16]}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(target)
    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile the eight pre-experiment gates before a scientific GPU launch.")
    parser.add_argument("idea_id")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    card = compile_from_path(args.idea_id, args.config, args.data_root)
    if args.write:
        card = {**card, "card_path": str(write_card(card, args.data_root))}
    print(json.dumps(card, ensure_ascii=False, indent=2))
    if not card["execution_authorized"]:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
