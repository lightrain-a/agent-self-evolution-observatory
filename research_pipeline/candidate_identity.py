from __future__ import annotations

import hashlib
import json
import re
from typing import Any

CANDIDATE_IDENTITY_VERSION = "candidate-content-v1"


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _primary_refs(candidate: dict[str, Any]) -> list[str]:
    refs = {
        str(ref).strip()
        for ref in candidate.get("primary_refs") or []
        if str(ref).strip().startswith("arXiv:")
    }
    evidence = candidate.get("empirical_evidence") or {}
    if isinstance(evidence, dict):
        for key in ("source_a", "source_b"):
            ref = str((evidence.get(key) or {}).get("ref") or "").strip()
            if ref.startswith("arXiv:"):
                refs.add(ref)
    return sorted(refs)


def candidate_identity_payload(candidate: dict[str, Any]) -> dict[str, Any]:
    """Return the stable scientific identity of one exact candidate formulation.

    ``candidate_id`` is deliberately excluded: PORT-* values are run-local display
    ordinals and are reused by later search generations. Timestamps, routing state,
    and authority are also excluded so an exact candidate keeps the same identity
    across zero-provider replay or downstream compilation.
    """
    return {
        "identity_version": CANDIDATE_IDENTITY_VERSION,
        "title": _text(candidate.get("title")),
        "discovery_lane": str(candidate.get("discovery_lane") or "").strip().upper(),
        "source_branch_id": str(candidate.get("source_branch_id") or "").strip(),
        "primary_refs": _primary_refs(candidate),
        "exact_prediction": _text(candidate.get("exact_prediction")),
        "strongest_same_information_baseline": _text(candidate.get("strongest_same_information_baseline")),
        "cheapest_problem_falsifier": _text(candidate.get("cheapest_problem_falsifier") or candidate.get("falsifier_expression")),
        "endpoint_headroom_requirement": _text(candidate.get("endpoint_headroom_requirement")),
    }


def candidate_snapshot_sha256(candidate: dict[str, Any]) -> str:
    payload = json.dumps(
        candidate_identity_payload(candidate),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def attach_candidate_identity(candidate: dict[str, Any]) -> dict[str, Any]:
    out = dict(candidate)
    out["candidate_identity_version"] = CANDIDATE_IDENTITY_VERSION
    out["candidate_snapshot_sha256"] = candidate_snapshot_sha256(out)
    return out


def validate_candidate_identity(candidate: dict[str, Any], *, required: bool = True) -> bool:
    version = str(candidate.get("candidate_identity_version") or "").strip()
    digest = str(candidate.get("candidate_snapshot_sha256") or "").strip().lower()
    if not version and not digest and not required:
        return False
    if version != CANDIDATE_IDENTITY_VERSION:
        raise ValueError("candidate identity version mismatch")
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("candidate snapshot identity must be sha256")
    expected = candidate_snapshot_sha256(candidate)
    if digest != expected:
        raise ValueError("candidate snapshot identity mismatch")
    return True
