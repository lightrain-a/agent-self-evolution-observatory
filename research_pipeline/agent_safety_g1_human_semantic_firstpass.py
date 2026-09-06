from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

PAPER_ID = "AGENT-SAFETY-R9"
SCHEMA_VERSION = "1.0"
PACKET_SHA256 = "2603fd7043761ad75ff3dafddf2845bee209eefc8d70bc1899b9dc6c1feefa4a"
EXPECTED_IDS = tuple(f"S{i:02d}" for i in range(1, 25))
EXPECTED_ID_SET = frozenset(EXPECTED_IDS)
ROLES = ("RATER_A", "RATER_B")
LABELS = (
    "TASK_DIRECTED_INTERACTION",
    "REFUSAL_OR_SAFE_HANDLING",
    "OTHER_OR_DRIFT",
)
CONFIDENCE = ("HIGH", "MEDIUM", "LOW")
REQUIRED_ATTESTATIONS = (
    "human_reviewer",
    "independent_first_pass",
    "no_ai_assistance_for_labels",
    "did_not_view_private_key_or_machine_labels",
    "did_not_discuss_labels_with_other_first_pass_rater_before_freeze",
    "all_24_items_labeled_without_replacement",
)


class HumanSemanticError(RuntimeError):
    pass


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as h:
            json.dump(value, h, ensure_ascii=False, indent=2, sort_keys=True)
            h.write("\n")
            h.flush()
            os.fsync(h.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HumanSemanticError(f"invalid JSON response:{path}") from exc
    if not isinstance(value, dict):
        raise HumanSemanticError(f"response must be a JSON object:{path}")
    return value


def _validate_label_row(row: Any, *, role: str) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise HumanSemanticError(f"{role}: label row must be object")
    blind_id = row.get("blind_id")
    if blind_id not in EXPECTED_ID_SET:
        raise HumanSemanticError(f"{role}: unexpected blind_id:{blind_id}")
    primary = row.get("primary_label")
    if primary not in LABELS:
        raise HumanSemanticError(f"{role}:{blind_id}: invalid primary_label")
    confidence = row.get("confidence")
    if confidence not in CONFIDENCE:
        raise HumanSemanticError(f"{role}:{blind_id}: invalid confidence")
    insufficient = row.get("insufficient_context")
    if not isinstance(insufficient, bool):
        raise HumanSemanticError(f"{role}:{blind_id}: insufficient_context must be boolean")
    notes = row.get("notes", "")
    if not isinstance(notes, str):
        raise HumanSemanticError(f"{role}:{blind_id}: notes must be string")
    if insufficient and (primary != "OTHER_OR_DRIFT" or confidence != "LOW"):
        raise HumanSemanticError(
            f"{role}:{blind_id}: insufficient_context requires OTHER_OR_DRIFT + LOW"
        )
    return {
        "blind_id": blind_id,
        "primary_label": primary,
        "confidence": confidence,
        "insufficient_context": insufficient,
        "notes": notes,
    }


def validate_response(value: dict[str, Any], *, expected_role: str) -> dict[str, Any]:
    if expected_role not in ROLES:
        raise HumanSemanticError(f"invalid expected role:{expected_role}")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise HumanSemanticError(f"{expected_role}: response schema drift")
    if value.get("paper_id") != PAPER_ID:
        raise HumanSemanticError(f"{expected_role}: paper_id drift")
    if value.get("packet_sha256") != PACKET_SHA256:
        raise HumanSemanticError(f"{expected_role}: packet SHA mismatch")
    if value.get("response_role") != expected_role:
        raise HumanSemanticError(f"{expected_role}: response_role mismatch")
    rater_id = value.get("rater_id")
    if not isinstance(rater_id, str) or not rater_id.strip():
        raise HumanSemanticError(f"{expected_role}: rater_id missing")
    rows = value.get("labels")
    if not isinstance(rows, list) or len(rows) != len(EXPECTED_IDS):
        raise HumanSemanticError(f"{expected_role}: exactly 24 label rows required")
    normalized = [_validate_label_row(row, role=expected_role) for row in rows]
    ids = [row["blind_id"] for row in normalized]
    if len(ids) != len(set(ids)):
        raise HumanSemanticError(f"{expected_role}: duplicate blind_id")
    if set(ids) != EXPECTED_ID_SET:
        raise HumanSemanticError(f"{expected_role}: incomplete/replaced blind panel")
    attestation = value.get("attestation")
    if not isinstance(attestation, dict):
        raise HumanSemanticError(f"{expected_role}: attestation missing")
    for key in REQUIRED_ATTESTATIONS:
        if attestation.get(key) is not True:
            raise HumanSemanticError(f"{expected_role}: attestation false/missing:{key}")
    completed_at = value.get("completed_at_local")
    if not isinstance(completed_at, str) or not completed_at.strip():
        raise HumanSemanticError(f"{expected_role}: completed_at_local missing")
    by_id = {row["blind_id"]: row for row in normalized}
    return {
        "response_role": expected_role,
        "rater_id": rater_id.strip(),
        "completed_at_local": completed_at,
        "labels": [by_id[blind_id] for blind_id in EXPECTED_IDS],
        "attestation": {key: True for key in REQUIRED_ATTESTATIONS},
    }


def cohen_kappa(a_labels: list[str], b_labels: list[str]) -> float | None:
    if len(a_labels) != len(b_labels) or not a_labels:
        raise HumanSemanticError("kappa inputs must be same nonzero length")
    n = len(a_labels)
    po = sum(a == b for a, b in zip(a_labels, b_labels)) / n
    ca, cb = Counter(a_labels), Counter(b_labels)
    pe = sum((ca[label] / n) * (cb[label] / n) for label in LABELS)
    if math.isclose(pe, 1.0):
        return 1.0 if math.isclose(po, 1.0) else None
    return (po - pe) / (1.0 - pe)


def merge_first_pass(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    a = validate_response(a, expected_role="RATER_A")
    b = validate_response(b, expected_role="RATER_B")
    if a["rater_id"] == b["rater_id"]:
        raise HumanSemanticError("RATER_A and RATER_B must have distinct anonymous rater IDs")

    a_by = {row["blind_id"]: row for row in a["labels"]}
    b_by = {row["blind_id"]: row for row in b["labels"]}
    rows: list[dict[str, Any]] = []
    disagreements: list[str] = []
    insufficient: list[str] = []
    robust_consensus: list[str] = []
    for blind_id in EXPECTED_IDS:
        ra, rb = a_by[blind_id], b_by[blind_id]
        exact = ra["primary_label"] == rb["primary_label"]
        has_insufficient = ra["insufficient_context"] or rb["insufficient_context"]
        consensus = ra["primary_label"] if exact and not has_insufficient else None
        if not exact:
            disagreements.append(blind_id)
        if has_insufficient:
            insufficient.append(blind_id)
        if consensus is not None:
            robust_consensus.append(blind_id)
        rows.append({
            "blind_id": blind_id,
            "rater_a_label": ra["primary_label"],
            "rater_a_confidence": ra["confidence"],
            "rater_a_insufficient_context": ra["insufficient_context"],
            "rater_b_label": rb["primary_label"],
            "rater_b_confidence": rb["confidence"],
            "rater_b_insufficient_context": rb["insufficient_context"],
            "exact_label_agreement": exact,
            "first_pass_consensus_label": consensus,
        })

    a_labels = [a_by[i]["primary_label"] for i in EXPECTED_IDS]
    b_labels = [b_by[i]["primary_label"] for i in EXPECTED_IDS]
    agreement_count = sum(x == y for x, y in zip(a_labels, b_labels))
    needs_blind_adjudication = sorted(set(disagreements) | set(insufficient))
    status = (
        "HUMAN_FIRST_PASS_FROZEN_BLIND_ADJUDICATION_REQUIRED"
        if needs_blind_adjudication
        else "HUMAN_FIRST_PASS_FROZEN_READY_FOR_MACHINE_UNBLINDING"
    )
    return {
        "schema_version": "g1-human-semantic-firstpass-v1",
        "paper_id": PAPER_ID,
        "packet_sha256": PACKET_SHA256,
        "status": status,
        "first_pass_frozen": True,
        "rater_a": {
            "rater_id": a["rater_id"],
            "completed_at_local": a["completed_at_local"],
        },
        "rater_b": {
            "rater_id": b["rater_id"],
            "completed_at_local": b["completed_at_local"],
        },
        "panel_size": len(EXPECTED_IDS),
        "exact_agreement_count": agreement_count,
        "exact_agreement_rate": agreement_count / len(EXPECTED_IDS),
        "cohen_kappa": cohen_kappa(a_labels, b_labels),
        "rater_a_class_counts": dict(Counter(a_labels)),
        "rater_b_class_counts": dict(Counter(b_labels)),
        "robust_first_pass_consensus_count": len(robust_consensus),
        "robust_first_pass_consensus_ids": robust_consensus,
        "label_disagreement_ids": disagreements,
        "insufficient_context_ids": insufficient,
        "blind_adjudication_required_ids": needs_blind_adjudication,
        "machine_label_unblinding_authorized": not needs_blind_adjudication,
        "machine_label_comparison_performed": False,
        "paper_claim_upgrade_authorized": False,
        "provider_or_gpu_calls": 0,
        "rows": rows,
        "frozen_rules": {
            "two_independent_human_first_passes_required": True,
            "no_ai_assistance_attestation_required": True,
            "no_machine_label_access_before_first_pass_freeze": True,
            "two_rater_disagreement_is_not_majority_vote": True,
            "either_rater_insufficient_context_blocks_first_pass_consensus": True,
            "disagreement_or_insufficient_items_require_blind_adjudication_before_machine_unblinding": True,
            "only_exact_same_label_without_insufficient_context_forms_first_pass_consensus": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rater-a", type=Path, required=True)
    parser.add_argument("--rater-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise HumanSemanticError(f"output overwrite forbidden:{args.output}")
    result = merge_first_pass(load_json(args.rater_a), load_json(args.rater_b))
    atomic_json(args.output, result)
    print(json.dumps({
        "status": result["status"],
        "exact_agreement_count": result["exact_agreement_count"],
        "cohen_kappa": result["cohen_kappa"],
        "blind_adjudication_required_ids": result["blind_adjudication_required_ids"],
        "machine_label_unblinding_authorized": result["machine_label_unblinding_authorized"],
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
