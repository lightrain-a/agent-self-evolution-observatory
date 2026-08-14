from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUEST_FILENAME = "problem-falsifier-support-inventory-request.json"
PREFLIGHT_FILENAME = "problem-falsifier-preflight.json"
ALLOWED_DISPOSITIONS = {"SUPPORT_QUALIFIED", "HOLD_SUPPORT_UNAVAILABLE"}
SUPPORT_MODES = {"RELEASED_UNITS", "FIRST_PARTY_CODE_RECONSTRUCTION", "EXISTING_PROVENANCE_SUBSTRATE"}
RECONSTRUCTED_SUPPORT_MODES = {"FIRST_PARTY_CODE_RECONSTRUCTION", "EXISTING_PROVENANCE_SUBSTRATE"}
AUTHORITY = {
    "canonical_generator": False,
    "canonical_problem_gate": False,
    "paper_design": False,
    "method": False,
    "experiment": False,
    "p0": False,
    "gpu": False,
}
REQUEST_POLICY = {
    "problem_falsifier_queue_is_zero_authority": True,
    "support_inventory_precedes_falsifier_execution": True,
    "support_inventory_request_cannot_claim_asset_availability": True,
    "synthetic_or_invented_units_cannot_substitute_for_required_source_units": True,
    "support_unavailable_is_not_scientific_falsification": True,
    "direct_released_unit_table_not_required_for_reconstructible_truth": True,
    "first_party_code_may_materialize_independent_support_truth": True,
    "existing_provenance_substrate_may_materialize_independent_support_truth": True,
    "reconstruction_must_freeze_operationalization_before_outcome_readout": True,
    "reconstruction_cannot_use_synthetic_substitution_or_candidate_mechanism_injection": True,
    "reconstruction_cannot_retune_on_hidden_outcomes_or_change_candidate_pool": True,
    "support_inventory_is_one_acquisition_route_not_a_global_prerequisite": True,
    "support_unavailable_may_route_to_bounded_first_party_evidence_design": True,
    "first_party_evidence_requires_independent_truth_and_same_information_baseline": True,
    "canonical_generator_and_queue_untouched": True,
    "automatic_problem_gate_authority": False,
    "automatic_paper_design_authority": False,
    "automatic_method_authority": False,
    "automatic_experiment_authority": False,
    "automatic_p0_authority": False,
    "automatic_gpu_authority": False,
}
PREFLIGHT_POLICY = {
    **REQUEST_POLICY,
    "support_qualification_precedes_falsifier_execution": True,
    "support_qualified_does_not_authorize_falsifier_execution": True,
    "support_inventory_receipt_must_cover_every_queued_candidate_exactly_once": True,
    "hold_requires_explicit_reopen_condition": True,
    "no_gpu": True,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bounded(value: Any, limit: int = 1800) -> str:
    return " ".join(str(value or "").split())[:limit]


def _candidate_index(machine: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for key in ("reviewable", "reduction_pending", "blocked"):
        for row in machine.get(key) or []:
            if not isinstance(row, dict):
                continue
            candidate = row.get("candidate") or {}
            if not isinstance(candidate, dict):
                continue
            candidate_id = str(row.get("candidate_id") or candidate.get("candidate_id") or "").strip()
            if candidate_id:
                index[candidate_id] = candidate
    return index


def _primary_refs(candidate: dict[str, Any]) -> list[str]:
    evidence = candidate.get("empirical_evidence") or {}
    return sorted({
        str((evidence.get(key) or {}).get("ref") or "").strip()
        for key in ("source_a", "source_b")
        if str((evidence.get(key) or {}).get("ref") or "").startswith("arXiv:")
    })


def build_support_inventory_request(machine_audit: dict[str, Any], *, run_id: str = "") -> dict[str, Any]:
    if machine_audit.get("scientific_authority") is not False:
        raise ValueError("machine audit must be zero-authority")
    authority = machine_audit.get("authority") or {}
    if any(authority.get(key) is not False for key in ("paper_design", "method", "experiment", "p0", "gpu")):
        raise ValueError("machine audit cannot authorize downstream execution")
    queue = [row for row in machine_audit.get("problem_falsifier_queue") or [] if isinstance(row, dict)]
    index = _candidate_index(machine_audit)
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in queue:
        candidate_id = str(row.get("candidate_id") or "").strip()
        if not candidate_id or candidate_id in seen:
            raise ValueError("problem falsifier queue candidate ids must be nonempty and unique")
        seen.add(candidate_id)
        candidate = index.get(candidate_id) or {}
        refs = _primary_refs(candidate)
        exact_prediction = _bounded(row.get("exact_prediction"), 2000)
        strongest = _bounded(row.get("strongest_same_information_baseline"), 1200)
        falsifier = _bounded(row.get("cheapest_problem_falsifier"), 2200)
        if not exact_prediction or not strongest or not falsifier:
            raise ValueError(f"problem falsifier queue missing frozen decision fields: {candidate_id}")
        rows.append({
            "candidate_id": candidate_id,
            "title": _bounded(row.get("title") or candidate.get("title"), 500),
            "discovery_lane": str(row.get("discovery_lane") or candidate.get("discovery_lane") or "").strip(),
            "source_branch_id": str(row.get("source_branch_id") or candidate.get("source_branch_id") or "").strip(),
            "primary_refs": refs,
            "exact_prediction": exact_prediction,
            "strongest_same_information_baseline": strongest,
            "falsifier_expression": falsifier,
            "support_inventory_question": (
                "Determine whether primary/author-released artifacts directly expose the observational/interventional units and fields "
                "needed for this frozen falsifier, or whether author-released first-party code / an existing provenance-audited substrate "
                "can materialize those units as independent truth under the frozen operationalization. A reconstructed unit is admissible only "
                "after materialization and provenance hashing, without synthetic substitution, candidate-mechanism injection, candidate-pool "
                "changes, or hidden-outcome retuning."
            ),
            "required_receipt_dispositions": sorted(ALLOWED_DISPOSITIONS),
            "scientific_authority": False,
        })
    return {
        "schema_version": "1.0-shadow",
        "generated_at": _now(),
        "run_id": run_id,
        "status": "PROBLEM_FALSIFIER_SUPPORT_INVENTORY_REQUEST_READY" if rows else "NO_PROBLEM_FALSIFIER_QUEUE",
        "policy": dict(REQUEST_POLICY),
        "summary": {"queued": len(queue), "inventory_requests": len(rows), "problem_gate_authorized": 0, "paper_design_authorized": 0, "method_authorized": 0, "experiment_authorized": 0, "p0_authorized": 0, "gpu_authorized": 0},
        "rows": rows,
        "authority": dict(AUTHORITY),
        "scientific_authority": False,
    }


def write_support_inventory_request(*, run_root: Path, output_path: Path | None = None) -> dict[str, Any]:
    machine_path = run_root / "machine-audit.json"
    request = build_support_inventory_request(_load(machine_path), run_id=run_root.name)
    target = output_path or (run_root / REQUEST_FILENAME)
    target.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return request


def _validate_receipt_row(request: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    candidate_id = str(request.get("candidate_id") or "")
    disposition = str(receipt.get("disposition") or "").strip().upper()
    if disposition not in ALLOWED_DISPOSITIONS:
        raise ValueError(f"invalid support disposition for {candidate_id}: {disposition or 'EMPTY'}")
    required_unit = _bounded(receipt.get("required_unit"), 1800)
    asset_audit = _bounded(receipt.get("asset_audit"), 2200)
    refs = sorted({str(ref) for ref in receipt.get("primary_refs") or [] if str(ref).startswith("arXiv:")})
    request_refs = set(str(ref) for ref in request.get("primary_refs") or [] if str(ref).startswith("arXiv:"))
    if not required_unit or not asset_audit or not refs:
        raise ValueError(f"support receipt missing required unit/audit/primary refs: {candidate_id}")
    if request_refs and not request_refs.intersection(refs):
        raise ValueError(f"support receipt is not grounded to the candidate primary refs: {candidate_id}")
    out = {
        "candidate_id": candidate_id,
        "title": _bounded(request.get("title"), 500),
        "disposition": disposition,
        "required_unit": required_unit,
        "asset_audit": asset_audit,
        "primary_refs": refs,
        "scientific_authority": False,
    }
    if disposition == "HOLD_SUPPORT_UNAVAILABLE":
        reopen = _bounded(receipt.get("reopen_only_if"), 1800)
        if not reopen:
            raise ValueError(f"support HOLD requires reopen condition: {candidate_id}")
        out["reopen_only_if"] = reopen
        out["bounded_first_party_evidence_design_allowed"] = True
        out["next_route"] = "BOUNDED_EVIDENCE_DESIGN_OR_WAIT_PRIMARY_ASSET"
        return out
    qualified_units = receipt.get("qualified_units")
    manifest_sha = str(receipt.get("unit_manifest_sha256") or "").strip().lower()
    support_scope = _bounded(receipt.get("support_scope"), 1600)
    support_mode = str(receipt.get("support_mode") or "RELEASED_UNITS").strip().upper()
    if support_mode not in SUPPORT_MODES:
        raise ValueError(f"support-qualified receipt has invalid support_mode: {candidate_id}")
    if not isinstance(qualified_units, int) or qualified_units <= 0:
        raise ValueError(f"support-qualified receipt requires positive qualified_units: {candidate_id}")
    if not re.fullmatch(r"[0-9a-f]{64}", manifest_sha):
        raise ValueError(f"support-qualified receipt requires unit_manifest_sha256: {candidate_id}")
    if not support_scope:
        raise ValueError(f"support-qualified receipt requires support_scope: {candidate_id}")
    out.update({
        "support_mode": support_mode,
        "qualified_units": qualified_units,
        "unit_manifest_sha256": manifest_sha,
        "support_scope": support_scope,
        "falsifier_execution_authorized": False,
    })
    if support_mode in RECONSTRUCTED_SUPPORT_MODES:
        reconstruction = receipt.get("reconstruction_receipt")
        if not isinstance(reconstruction, dict):
            raise ValueError(f"reconstructed support requires reconstruction_receipt: {candidate_id}")
        substrate_id = _bounded(reconstruction.get("substrate_id"), 800)
        revision = _bounded(reconstruction.get("source_or_substrate_revision"), 800)
        command = _bounded(reconstruction.get("materialization_command"), 1800)
        provenance_sha = str(reconstruction.get("provenance_sha256") or "").strip().lower()
        if not substrate_id or not revision or not command or not re.fullmatch(r"[0-9a-f]{64}", provenance_sha):
            raise ValueError(f"reconstructed support requires substrate/revision/command/provenance_sha256: {candidate_id}")
        required_true = ("operationalization_frozen_before_outcomes", "independent_truth")
        required_false = ("synthetic_substitution", "candidate_mechanism_injected", "candidate_pool_changed", "hidden_outcome_retuning")
        if any(reconstruction.get(key) is not True for key in required_true):
            raise ValueError(f"reconstructed support requires frozen operationalization and independent truth: {candidate_id}")
        if any(reconstruction.get(key) is not False for key in required_false):
            raise ValueError(f"reconstructed support violates anti-leakage reconstruction contract: {candidate_id}")
        out["reconstruction_receipt"] = {
            "substrate_id": substrate_id,
            "source_or_substrate_revision": revision,
            "materialization_command": command,
            "provenance_sha256": provenance_sha,
            "operationalization_frozen_before_outcomes": True,
            "independent_truth": True,
            "synthetic_substitution": False,
            "candidate_mechanism_injected": False,
            "candidate_pool_changed": False,
            "hidden_outcome_retuning": False,
        }
    return out


def compile_problem_falsifier_preflight(machine_audit: dict[str, Any], support_inventory: dict[str, Any], *, run_id: str = "", inventory_sha256: str = "") -> dict[str, Any]:
    request = build_support_inventory_request(machine_audit, run_id=run_id)
    requested = {str(row.get("candidate_id") or ""): row for row in request.get("rows") or [] if isinstance(row, dict)}
    receipt_rows = [row for row in support_inventory.get("rows") or [] if isinstance(row, dict)]
    receipts: dict[str, dict[str, Any]] = {}
    for row in receipt_rows:
        candidate_id = str(row.get("candidate_id") or "").strip()
        if not candidate_id or candidate_id in receipts:
            raise ValueError("support inventory candidate ids must be nonempty and unique")
        receipts[candidate_id] = row
    if set(receipts) != set(requested):
        missing = sorted(set(requested) - set(receipts))
        extra = sorted(set(receipts) - set(requested))
        raise ValueError(f"support inventory must cover problem falsifier queue exactly; missing={missing}; extra={extra}")
    compiled = [_validate_receipt_row(requested[candidate_id], receipts[candidate_id]) for candidate_id in sorted(requested)]
    support_qualified = sum(row["disposition"] == "SUPPORT_QUALIFIED" for row in compiled)
    holds = sum(row["disposition"] == "HOLD_SUPPORT_UNAVAILABLE" for row in compiled)
    return {
        "schema_version": "1.0-shadow",
        "generated_at": _now(),
        "run_id": run_id,
        "status": "PROBLEM_FALSIFIER_PREFLIGHT_COMPLETE",
        "support_inventory_origin": _bounded(support_inventory.get("inventory_origin"), 800),
        "support_inventory_sha256": inventory_sha256,
        "policy": dict(PREFLIGHT_POLICY),
        "summary": {"queued": len(requested), "support_qualified": support_qualified, "hold_support_unavailable": holds, "falsifier_executed": 0, "problem_gate_authorized": 0, "paper_design_authorized": 0, "method_authorized": 0, "experiment_authorized": 0, "p0_authorized": 0, "gpu_authorized": 0},
        "rows": compiled,
        "authority": dict(AUTHORITY),
        "scientific_authority": False,
    }


def write_problem_falsifier_preflight(*, run_root: Path, support_inventory_path: Path, output_path: Path | None = None) -> dict[str, Any]:
    machine = _load(run_root / "machine-audit.json")
    support_inventory = _load(support_inventory_path)
    state = compile_problem_falsifier_preflight(machine, support_inventory, run_id=run_root.name, inventory_sha256=_sha(support_inventory_path))
    target = output_path or (run_root / PREFLIGHT_FILENAME)
    target.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    request = sub.add_parser("request")
    request.add_argument("--run-root", type=Path, required=True)
    request.add_argument("--out", type=Path)
    compile_cmd = sub.add_parser("compile")
    compile_cmd.add_argument("--run-root", type=Path, required=True)
    compile_cmd.add_argument("--support-inventory", type=Path, required=True)
    compile_cmd.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.command == "request":
        result = write_support_inventory_request(run_root=args.run_root, output_path=args.out)
    else:
        result = write_problem_falsifier_preflight(run_root=args.run_root, support_inventory_path=args.support_inventory, output_path=args.out)
    print(json.dumps({"status": result.get("status"), "summary": result.get("summary"), "scientific_authority": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
