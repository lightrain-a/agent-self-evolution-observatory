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
from .principle_adjudication import audit_principle_certificate


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


def compile_pre_experiment_card(idea_id: str, config: dict[str, Any], data_root: Path) -> dict[str, Any]:
    if str(config.get("idea_id") or "") != idea_id:
        raise ValueError(f"config idea_id mismatch: {config.get('idea_id')} != {idea_id}")
    principle_certificate = audit_principle_certificate(config)
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
    blockers = list(principle_certificate.get("blockers") or []) + list(updater_competence.get("blockers") or []) + [blocker for gate in gates for blocker in gate["blockers"]]
    passed = sum(bool(gate["pass"]) for gate in gates)
    gates_passed = passed == len(gates)
    principle_ready = principle_certificate.get("passed") is True
    updater_competent = updater_competence.get("passed") is True
    config_hash = _hash_payload(config)
    scope = config.get("scope") or {}
    competence = (config.get("pre_experiment") or {}).get("competence") or {}
    return {
        "schema_version": "2.1",
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
        "principle_certificate_prerequisite": principle_certificate,
        "updater_competence_prerequisite": updater_competence,
        "gate_count": len(gates),
        "passed_gates": passed,
        "execution_authorized": principle_ready and updater_competent and gates_passed,
        "status": "pass" if principle_ready and updater_competent and gates_passed else "blocked",
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
