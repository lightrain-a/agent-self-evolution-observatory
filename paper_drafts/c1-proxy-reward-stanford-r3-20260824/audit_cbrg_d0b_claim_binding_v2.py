#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
AUDIT_ID = "C1-CBRG-D0B-CLAIM-BINDING-V2"
AUDIT_VERSION = "C1_D0B_CLAIM_BINDING_AUDIT_V2"

HERE = Path(__file__).resolve().parent
V1 = HERE / "cbrg-d0b-receipt-structural-audit-20260824.json"
OUT = HERE / "cbrg-d0b-claim-binding-audit-v2-20260824.json"
EXPECTED_V1_SHA256 = "3f245fb99237c0da8f0ca34cd2c619b2d92bf0dc44245b53319f172e02c921ef"

PROCEDURAL_MARKER = re.compile(
    r"\b(always|when|before|after|use|ensure|verify|check|navigate|click|extract|report|if|only|avoid|first|then|instead|rather|should|must|do not|don't|complete|return|open|select|scan|look|find)\b",
    re.I,
)
GENERALIZATION_MARKER = re.compile(
    r"\b(because|ensur\w*|prevent\w*|lead\w*|caus\w*|help\w*|reduc\w*|improv\w*|reliable|necessary|likely|usually|successful|so that|allows?|makes?)\b",
    re.I,
)


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def read_memory_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return raw
        if isinstance(payload, dict) and str(payload.get("text") or "").strip():
            return str(payload["text"])
    return raw


def parse_memory_fields(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        match = re.match(r"^##\s+(Title|Description|Content):\s*(.+?)\s*$", line.strip())
        if match and match.group(2):
            rows.append({"field": match.group(1).lower(), "text": match.group(2).strip()})
    if not rows:
        for match in re.finditer(r"(?:Title|Description|Content):\s*([^\n#]+)", text):
            rows.append({"field": "unknown", "text": match.group(1).strip()})
    require(bool(rows), "memory schema parsing produced zero fields")
    return rows


def main() -> None:
    require(V1.is_file(), f"missing historical D0-B structural audit: {V1}")
    v1_sha = sha_file(V1)
    require(v1_sha == EXPECTED_V1_SHA256, f"historical D0-B v1 SHA drift: {v1_sha}")
    v1 = load_json(V1)
    require(v1.get("paper_id") == PAPER_ID, "historical D0-B audit paper_id drift")
    receipts = v1.get("receipts") or []
    require(len(receipts) == 24, f"expected 24 receipt envelopes, found {len(receipts)}")

    candidate_atoms = 0
    reconstructed_atoms = 0
    procedural_marker_atoms = 0
    generalization_marker_atoms = 0
    claim_specific_evidence_refs = 0
    certified_branch_residual_atoms = 0
    per_claim_validity_atoms = 0
    packet_level_evidence_receipts = 0
    claim_level_evidence_receipts = 0
    nonzero_branch_authority_receipts = 0
    receipt_rows: list[dict[str, Any]] = []

    residual_identity_keys = {
        "residual_weight",
        "opposite_explainability",
        "residual_membership",
        "is_residual",
        "branch_specificity",
        "counterfactual_difference_ref",
    }
    claim_evidence_keys = {
        "evidence_refs",
        "evidence_ref",
        "evidence_sha256",
        "evidence_hashes",
        "claim_evidence_refs",
    }

    for receipt in receipts:
        domain = str(receipt.get("domain") or "")
        source_task = int(receipt.get("source_task"))
        evidence = receipt.get("outcome_independent_evidence") or {}
        packet_bound = bool(evidence.get("released_evidence_sha256")) and bool(evidence.get("released_state_sha256"))
        if packet_bound:
            packet_level_evidence_receipts += 1

        has_claim_level_section = any(
            key in receipt for key in ("claim_evidence", "claim_evidence_refs", "evidence_by_claim")
        )
        if has_claim_level_section:
            claim_level_evidence_receipts += 1

        if str(receipt.get("authority_decision") or "") != "WITHHOLD_ALL_BRANCH_AUTHORITY":
            nonzero_branch_authority_receipts += 1

        claims_by_branch = ((receipt.get("residual_claim_identity") or {}).get("claims") or {})
        branch_memories = receipt.get("branch_memories") or {}
        receipt_candidate_atoms = 0
        receipt_claim_refs = 0
        receipt_certified_residuals = 0

        for condition in ("success", "failure"):
            claim_rows = claims_by_branch.get(condition) or []
            memory_info = branch_memories.get(condition) or {}
            memory_path = Path(str(memory_info.get("path") or ""))
            require(memory_path.is_file(), f"missing branch memory: {domain}/{source_task}/{condition}")
            memory_text = read_memory_text(memory_path)
            require(sha_text(memory_text) == str(memory_info.get("sha256") or ""), f"branch-memory SHA drift: {domain}/{source_task}/{condition}")
            units = parse_memory_fields(memory_text)
            require(len(units) == len(claim_rows), f"field-count drift: {domain}/{source_task}/{condition}")

            for row, unit in zip(claim_rows, units):
                require(str(row.get("text_sha256") or "") == sha_text(unit["text"]), f"claim atom SHA drift: {domain}/{source_task}/{condition}")
                candidate_atoms += 1
                reconstructed_atoms += 1
                receipt_candidate_atoms += 1
                if PROCEDURAL_MARKER.search(unit["text"]):
                    procedural_marker_atoms += 1
                if GENERALIZATION_MARKER.search(unit["text"]):
                    generalization_marker_atoms += 1

                row_keys = set(row)
                current_claim_refs = sum(1 for key in claim_evidence_keys if row.get(key))
                claim_specific_evidence_refs += current_claim_refs
                receipt_claim_refs += current_claim_refs

                is_certified_residual = any(row.get(key) not in (None, False, "", 0, 0.0) for key in residual_identity_keys)
                if is_certified_residual:
                    certified_branch_residual_atoms += 1
                    receipt_certified_residuals += 1

                if row.get("validity") not in (None, "", "UNADJUDICATED_STRUCTURAL_ONLY"):
                    per_claim_validity_atoms += 1

        receipt_rows.append(
            {
                "domain": domain,
                "source_task": source_task,
                "candidate_memory_atoms": receipt_candidate_atoms,
                "packet_level_evidence_bound": packet_bound,
                "claim_level_evidence_section_present": has_claim_level_section,
                "claim_specific_evidence_refs": receipt_claim_refs,
                "certified_branch_residual_atoms": receipt_certified_residuals,
                "authority_decision": str(receipt.get("authority_decision") or ""),
            }
        )

    require(candidate_atoms == 423, f"expected 423 candidate memory atoms, found {candidate_atoms}")
    require(reconstructed_atoms == 423, "not all candidate atoms were reconstructed")
    require(packet_level_evidence_receipts == 24, "packet-level evidence envelope binding is incomplete")
    require(claim_level_evidence_receipts == 0, "historical audit unexpectedly contains claim-level evidence sections")
    require(claim_specific_evidence_refs == 0, "historical audit unexpectedly contains claim-specific evidence refs")
    require(certified_branch_residual_atoms == 0, "historical audit unexpectedly certifies residual membership")
    require(per_claim_validity_atoms == 0, "historical audit unexpectedly adjudicates per-claim validity")
    require(nonzero_branch_authority_receipts == 0, "historical audit unexpectedly grants branch authority")

    payload: dict[str, Any] = {
        "schema_version": "2.0",
        "artifact_type": "c1-d0b-claim-binding-correction-audit",
        "audit_id": AUDIT_ID,
        "audit_version": AUDIT_VERSION,
        "paper_id": PAPER_ID,
        "status": "D0B_RECEIPT_ENVELOPE_COMPLETE_CLAIM_BINDING_HOLD",
        "decision": "D0B_ENVELOPE_GO_CLAIM_BINDING_HOLD",
        "historical_v1": {
            "artifact": str(V1.relative_to(HERE.parents[1])),
            "sha256": v1_sha,
            "interpretation": "Historical v1 establishes content-addressed receipt-envelope lineage only. Its top-level binds_evidence_refs_and_sha256 flag is interpreted as packet-level evidence hashing, not per-claim evidence binding.",
        },
        "summary": {
            "receipt_envelopes_expected": 24,
            "receipt_envelopes_packet_bound": packet_level_evidence_receipts,
            "candidate_memory_atoms": candidate_atoms,
            "candidate_memory_atoms_reconstructed": reconstructed_atoms,
            "certified_branch_residual_atoms": certified_branch_residual_atoms,
            "claim_specific_evidence_refs_bound": claim_specific_evidence_refs,
            "claim_level_evidence_receipts": claim_level_evidence_receipts,
            "per_claim_validity_adjudicated_atoms": per_claim_validity_atoms,
            "nonzero_branch_authority_receipts": nonzero_branch_authority_receipts,
            "procedural_marker_atoms_descriptive_only": procedural_marker_atoms,
            "generalization_marker_atoms_descriptive_only": generalization_marker_atoms,
        },
        "binding_semantics": {
            "packet_level_evidence_binding": True,
            "claim_level_evidence_binding": False,
            "candidate_memory_atom_is_not_yet_a_certified_residual_claim": True,
            "residual_identity_certified": False,
            "semantic_validity_adjudicated": False,
            "evidence_authority_available": False,
            "treatment_label_used_as_evidence": False,
            "terminal_reward_or_rubric_used_as_evidence": False,
        },
        "reviewer_correction": {
            "problem": "The v1 receipt envelope bound each trajectory and a whole released evidence packet, but did not bind an exact evidence ref to each memory atom and did not certify that each parsed Title/Description/Content atom belongs to the same-trajectory branch residual.",
            "forbidden_upgrade": "A packet SHA, field-level atom ID, or semantic-similarity score cannot be interpreted as claim-level evidence validity or branch-specific residual identity.",
            "required_next_gate": "D0-B1 zero-call residual-identity plus claim-specific evidence-locator audit. Only after both are content-addressed may a separately versioned semantic adjudicator assign SUPPORTED/CONTRADICTED/UNVERIFIABLE.",
            "stop_condition": "If exact residual identity or claim-specific outcome-independent evidence cannot be bound without outcome leakage, stop/merge CBRG and preserve C1 as the stage-resolved identification/measurement paper.",
        },
        "descriptive_marker_boundary": "Procedural/generalization regex counts are diagnostics of the memory-atom surface only. They are not semantic labels, causal evidence, residual membership, or validity judgments.",
        "receipts": receipt_rows,
        "provider_calls": 0,
        "gpu_runs": 0,
        "scientific_authority": False,
        "experiment_authority": False,
        "provider_call_authority": False,
        "gpu_authority": False,
        "claim_expansion_authority": False,
        "submission_authority": False,
    }

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "decision": payload["decision"], **payload["summary"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
