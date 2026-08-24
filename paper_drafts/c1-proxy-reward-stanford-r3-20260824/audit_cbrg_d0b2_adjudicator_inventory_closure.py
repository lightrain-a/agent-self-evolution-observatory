#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
AUDIT_ID = "C1-CBRG-D0B2-ADJUDICATOR-INVENTORY-CLOSURE-V1"
STATUS = "D0B2_BOUNDED_ADJUDICATOR_INVENTORY_EXHAUSTED_CURRENT_EXTENSION_STOP_MERGE"
DECISION = "STOP_MERGE_CBRG_EXTENSION_NO_QUALIFIED_OUTCOME_INDEPENDENT_VALIDITY_SIGNAL"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
B2 = HERE / "cbrg-d0b2-semantic-readiness-audit-20260824.json"
OUT = HERE / "cbrg-d0b2-adjudicator-inventory-closure-20260825.json"
B2_SHA256 = "f854b1957d884ba6528cf860b4d39e90689ff580072ad9373505578f1c8052ab"

SCAN_ROOTS = (
    ROOT / "research_pipeline",
    ROOT / "scripts",
    ROOT / "paper_drafts",
)
TEXT_SUFFIXES = {".py", ".json", ".md"}
TRISTATE_TERMS = ("supported", "contradicted", "unverifiable")


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve()))


def is_contract_or_self_reference(path: Path) -> bool:
    resolved = path.resolve()
    if HERE.resolve() in resolved.parents:
        return True
    if resolved == (ROOT / "research_pipeline" / "methodology_controls.py").resolve():
        return True
    return False


def scan_repository() -> dict[str, Any]:
    tristate_hits: list[dict[str, Any]] = []
    nli_vocab_hits: list[dict[str, Any]] = []
    external_executable_candidates: list[dict[str, Any]] = []
    scanned = 0

    for base in SCAN_ROOTS:
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if path.resolve() == OUT.resolve():
                continue
            if "__pycache__" in path.parts or path.name.startswith("test_"):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            scanned += 1
            lower = text.lower()
            tri = all(term in lower for term in TRISTATE_TERMS)
            nli = "entail" in lower and "contrad" in lower
            if not (tri or nli):
                continue
            self_reference = is_contract_or_self_reference(path)
            row = {
                "path": rel(path),
                "contains_all_required_tristate_terms": tri,
                "contains_entailment_and_contradiction_vocab": nli,
                "classification": "C1_SELF_OR_GATE_CONTRACT_ONLY" if self_reference else "EXTERNAL_TEXTUAL_CANDIDATE_REQUIRES_QUALIFICATION",
            }
            # Do not hash the C1 gate/program into its own terminal receipt: the
            # gate binds this receipt later, so a self-hash would create a cycle.
            # External candidates, if any, must still be content-addressed.
            if not self_reference:
                row["sha256"] = sha_file(path)
            if tri:
                tristate_hits.append(row)
            if nli:
                nli_vocab_hits.append(row)
            if not is_contract_or_self_reference(path):
                external_executable_candidates.append(row)

    qualification_receipts = sorted(
        rel(path)
        for base in SCAN_ROOTS
        if base.is_dir()
        for path in base.rglob("*.json")
        if "semantic" in path.name.lower()
        and "qualification" in path.name.lower()
        and HERE.resolve() not in path.resolve().parents
    )

    return {
        "scan_roots": [rel(path) for path in SCAN_ROOTS],
        "text_files_scanned": scanned,
        "tri_state_vocabulary_hits": tristate_hits,
        "tri_state_vocabulary_hit_count": len(tristate_hits),
        "entailment_contradiction_vocabulary_hits": nli_vocab_hits,
        "entailment_contradiction_vocabulary_hit_count": len(nli_vocab_hits),
        "external_textual_candidates": external_executable_candidates,
        "external_textual_candidate_count": len(external_executable_candidates),
        "external_semantic_qualification_receipts": qualification_receipts,
        "external_semantic_qualification_receipt_count": len(qualification_receipts),
        "admissible_qualified_repository_adjudicators": 0,
    }


def main() -> None:
    require(B2.is_file(), "missing D0-B2 semantic-readiness receipt")
    require(sha_file(B2) == B2_SHA256, "D0-B2 semantic-readiness receipt SHA drift")
    b2 = load_json(B2)
    require(
        b2.get("decision") == "D0B2_READINESS_HOLD_NO_ADMISSIBLE_OUTCOME_INDEPENDENT_VALIDITY_SIGNAL",
        "D0-B2 readiness decision drift",
    )
    local = b2.get("local_asset_audit") or {}
    ready = b2.get("readiness_summary") or {}
    require(local.get("admissible_qualified_adjudicators") == 0, "B2 already has a qualified local adjudicator")
    require(ready.get("qualified_semantic_adjudicators_bound") == 0, "B2 already bound a qualified adjudicator")
    require(ready.get("semantic_validity_adjudicated_units") == 0, "B2 already ran semantic adjudication")
    require(ready.get("provider_calls") == 0 and ready.get("gpu_runs") == 0, "B2 readiness was not zero-call")

    inventory = scan_repository()
    require(inventory["external_textual_candidate_count"] == 0, "repository contains a non-C1 textual adjudicator candidate; inventory closure must be reconsidered")
    require(inventory["external_semantic_qualification_receipt_count"] == 0, "repository contains an external semantic qualification receipt; inventory closure must be reconsidered")
    require(inventory["admissible_qualified_repository_adjudicators"] == 0, "qualified repository adjudicator unexpectedly available")

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "artifact_type": "c1-d0b2-adjudicator-inventory-closure",
        "audit_id": AUDIT_ID,
        "paper_id": PAPER_ID,
        "status": STATUS,
        "decision": DECISION,
        "scope": "CURRENT_FROZEN_ZERO_CALL_CBRG_EXTENSION_ONLY",
        "input_binding": {
            "semantic_readiness_artifact": rel(B2),
            "semantic_readiness_sha256": B2_SHA256,
            "semantic_readiness_local_qualified_adjudicators": 0,
            "semantic_readiness_bound_adjudicators": 0,
        },
        "repository_inventory": inventory,
        "closure_reasoning": {
            "local_model_inventory_has_admissible_adjudicator": False,
            "repository_inventory_has_admissible_adjudicator": False,
            "task_specific_preoutcome_qualification_receipt_exists": False,
            "similarity_or_locator_may_be_promoted_to_validity": False,
            "self_referential_c1_gate_may_qualify_itself": False,
            "new_semantic_rule_may_be_invented_after_outcome_to_avoid_stop": False,
            "therefore_current_extension_may_advance_to_semantic_execution": False,
        },
        "terminal_routing": {
            "cbrg_method_extension": "STOP_MERGE_CURRENT_EXTENSION",
            "c1_stage_resolved_identification_measurement_paper": "RETAIN",
            "c1_existing_measurement_evidence_invalidated": False,
            "scientific_failure_declared": False,
            "provider_method_experiment": "LOCKED_NOT_AUTHORIZED",
            "fresh_experiment": "LOCKED_NOT_AUTHORIZED",
        },
        "reopen_contract": {
            "automatic_reopen": False,
            "generic_nli_model_existence_is_sufficient": False,
            "renamed_similarity_or_common_residual_is_sufficient": False,
            "required_all": [
                "new content-addressed adjudicator candidate with explicit SUPPORTED/CONTRADICTED/UNVERIFIABLE semantics",
                "independent task-specific pre-outcome C1 qualification receipt bound to the exact adjudicator SHA",
                "non-reducibility evidence against lexical locator and embedding/applicability baselines on the same frozen information",
                "fresh collision clearance showing the surviving residual is still not subsumed by closest work",
            ],
            "reopen_authority_granted_by_this_receipt": False,
        },
        "provider_calls_added": 0,
        "gpu_runs_added": 0,
        "scientific_authority": False,
        "experiment_authority": False,
        "provider_call_authority": False,
        "gpu_authority": False,
        "claim_expansion_authority": False,
        "submission_authority": False,
    }

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": STATUS,
                "decision": DECISION,
                "scope": payload["scope"],
                "text_files_scanned": inventory["text_files_scanned"],
                "tri_state_vocabulary_hit_count": inventory["tri_state_vocabulary_hit_count"],
                "entailment_contradiction_vocabulary_hit_count": inventory["entailment_contradiction_vocabulary_hit_count"],
                "external_textual_candidate_count": inventory["external_textual_candidate_count"],
                "external_semantic_qualification_receipt_count": inventory["external_semantic_qualification_receipt_count"],
                "admissible_qualified_repository_adjudicators": inventory["admissible_qualified_repository_adjudicators"],
                "provider_calls_added": 0,
                "gpu_runs_added": 0,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
