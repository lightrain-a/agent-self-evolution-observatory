from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .paper_preparation_protocol import PAPER_PREPARATION_GATE_KEYS
from .presubmission_freeze import artifact

IMPACT_SCHEMA_VERSION = "1.0"

IMPACT_POLICY: dict[str, dict[str, tuple[str, ...]]] = {
    "PACKAGING_ONLY": {
        "preparation": ("submission-package",),
        "acceptance": (),
    },
    "RENDERED_OUTPUT_ONLY": {
        "preparation": ("visual-story", "submission-package"),
        "acceptance": ("manuscript-ci",),
    },
    "FORMAT_ONLY": {
        "preparation": ("visual-story", "submission-package"),
        "acceptance": ("manuscript-ci",),
    },
    "LAYOUT_STYLE": {
        "preparation": ("visual-story", "submission-package"),
        "acceptance": ("manuscript-ci",),
    },
    "CITATION": {
        "preparation": ("verification-refinement", "citation-integrity", "reader-simulation", "submission-package"),
        "acceptance": ("claim-audit", "manuscript-ci"),
    },
    "MANUSCRIPT_TEXT": {
        "preparation": ("hierarchical-rubric", "verification-refinement", "citation-integrity", "visual-story", "reader-simulation", "submission-package"),
        "acceptance": ("claim-audit", "manuscript-ci", "prebuttal"),
    },
    "VISUAL_ARTIFACT": {
        "preparation": ("visual-story", "reproducibility-bundle", "reader-simulation", "submission-package"),
        "acceptance": ("manuscript-ci",),
    },
    "EVIDENCE_DATA": {
        "preparation": ("hierarchical-rubric", "verification-refinement", "visual-story", "reproducibility-bundle", "agent-native-artifact", "reader-simulation", "submission-package"),
        "acceptance": ("claim-audit", "manuscript-ci", "prebuttal"),
    },
    "REPRODUCTION_CODE": {
        "preparation": ("reproducibility-bundle", "agent-native-artifact", "reader-simulation", "submission-package"),
        "acceptance": (),
    },
    "REPRODUCTION_METADATA": {
        "preparation": ("reproducibility-bundle", "submission-package"),
        "acceptance": (),
    },
    "PACKAGE_SUPPORT": {
        "preparation": ("reproducibility-bundle", "submission-package"),
        "acceptance": (),
    },
    "UNCLASSIFIED_LEGACY_FREEZE": {
        "preparation": tuple(PAPER_PREPARATION_GATE_KEYS),
        "acceptance": ("claim-audit", "manuscript-ci", "prebuttal", "mock-pc-review"),
    },
    "UNKNOWN": {
        "preparation": tuple(PAPER_PREPARATION_GATE_KEYS),
        "acceptance": ("claim-audit", "manuscript-ci", "prebuttal", "mock-pc-review"),
    },
}


def _digest(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _expanded(spec: Mapping[str, Any]) -> dict[str, Any]:
    value = spec.get("expanded_manifest") or {}
    return dict(value) if isinstance(value, Mapping) else {}


def _entries(manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("path") or ""): dict(row)
        for row in manifest.get("entries") or []
        if isinstance(row, Mapping) and str(row.get("path") or "")
    }


def _role_impact(role: str) -> str:
    return role if role in IMPACT_POLICY else "UNKNOWN"


def _artifact_changes(frozen: Mapping[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    label = str(frozen.get("label") or "unnamed")
    kind = str(frozen.get("kind") or "file")
    path = Path(str(frozen.get("path") or ""))
    if not path.exists():
        return {}, [{"artifact": label, "change": "MISSING", "impact": "UNKNOWN"}], ["UNKNOWN"]
    try:
        current = artifact(label, path, tree=(kind == "tree"))
    except Exception:
        return {}, [{"artifact": label, "change": "UNREADABLE", "impact": "UNKNOWN"}], ["UNKNOWN"]
    if current.get("sha256") == frozen.get("sha256") and int(current.get("bytes") or 0) == int(frozen.get("bytes") or 0):
        return current, [], []

    frozen_expanded = _expanded(frozen)
    current_expanded = _expanded(current)
    if not frozen_expanded:
        lower = f"{label} {path.name}".lower()
        if path.suffix.lower() == ".pdf" or "pdf" in lower:
            return current, [{"artifact": label, "change": "TOP_LEVEL_BYTES", "impact": "RENDERED_OUTPUT_ONLY"}], ["RENDERED_OUTPUT_ONLY"]
        if kind == "tree" or path.suffix.lower() == ".zip":
            return current, [{"artifact": label, "change": "TOP_LEVEL_BYTES", "impact": "UNCLASSIFIED_LEGACY_FREEZE"}], ["UNCLASSIFIED_LEGACY_FREEZE"]
        return current, [{"artifact": label, "change": "TOP_LEVEL_BYTES", "impact": "UNKNOWN"}], ["UNKNOWN"]

    if not current_expanded:
        return current, [{"artifact": label, "change": "EXPANDED_MANIFEST_UNAVAILABLE", "impact": "UNKNOWN"}], ["UNKNOWN"]
    if frozen_expanded.get("sha256") == current_expanded.get("sha256"):
        return current, [{"artifact": label, "change": "CONTAINER_BYTES_ONLY", "impact": "PACKAGING_ONLY"}], ["PACKAGING_ONLY"]

    old = _entries(frozen_expanded)
    new = _entries(current_expanded)
    changes: list[dict[str, Any]] = []
    impacts: list[str] = []
    for rel in sorted(set(old) | set(new)):
        before = old.get(rel)
        after = new.get(rel)
        if before is None:
            impact = _role_impact(str(after.get("role") or "UNKNOWN"))
            changes.append({"artifact": label, "path": rel, "change": "ADDED", "impact": impact})
        elif after is None:
            impact = _role_impact(str(before.get("role") or "UNKNOWN"))
            changes.append({"artifact": label, "path": rel, "change": "REMOVED", "impact": impact})
        elif before.get("sha256") != after.get("sha256"):
            role = str(after.get("role") or before.get("role") or "UNKNOWN")
            semantic_before = str(before.get("semantic_sha256") or "")
            semantic_after = str(after.get("semantic_sha256") or "")
            if role in {"MANUSCRIPT_TEXT", "CITATION"} and semantic_before and semantic_before == semantic_after:
                impact = "FORMAT_ONLY"
            else:
                impact = _role_impact(role)
            changes.append({
                "artifact": label,
                "path": rel,
                "change": "MODIFIED",
                "impact": impact,
                "role": role,
                "semantic_unchanged": bool(semantic_before and semantic_before == semantic_after),
            })
        else:
            continue
        if impact not in impacts:
            impacts.append(impact)
    if not changes:
        changes.append({"artifact": label, "change": "EXPANDED_MANIFEST_CHANGED_UNEXPLAINED", "impact": "UNKNOWN"})
        impacts.append("UNKNOWN")
    return current, changes, impacts


def audit_freeze_receipt(freeze_receipt: Mapping[str, Any]) -> dict[str, Any]:
    all_changes: list[dict[str, Any]] = []
    impact_classes: list[str] = []
    current_artifacts: list[dict[str, Any]] = []
    for frozen in freeze_receipt.get("frozen_artifacts") or []:
        if not isinstance(frozen, Mapping):
            all_changes.append({"artifact": "unknown", "change": "INVALID_SPEC", "impact": "UNKNOWN"})
            if "UNKNOWN" not in impact_classes:
                impact_classes.append("UNKNOWN")
            continue
        current, changes, impacts = _artifact_changes(frozen)
        if current:
            current_artifacts.append(current)
        all_changes.extend(changes)
        for impact in impacts:
            if impact not in impact_classes:
                impact_classes.append(impact)
    prep: list[str] = []
    acceptance: list[str] = []
    for impact in impact_classes:
        policy = IMPACT_POLICY.get(impact, IMPACT_POLICY["UNKNOWN"])
        for gate in policy["preparation"]:
            if gate not in prep:
                prep.append(gate)
        for check in policy["acceptance"]:
            if check not in acceptance:
                acceptance.append(check)
    no_change = not all_changes
    result: dict[str, Any] = {
        "schema_version": IMPACT_SCHEMA_VERSION,
        "paper_id": str(freeze_receipt.get("paper_id") or ""),
        "baseline_freeze_sha256": str(freeze_receipt.get("freeze_sha256") or ""),
        "status": "NO_CHANGE" if no_change else "REVISION_DETECTED",
        "impact_classes": impact_classes,
        "changes": all_changes,
        "minimum_rerun_paper_preparation_gates": prep,
        "minimum_rerun_paper_acceptance_checks": acceptance,
        "invalidate_pre_submission_freeze": not no_change,
        "invalidate_machine_handoff": not no_change,
        "invalidate_human_signoff": not no_change,
        "requires_full_preparation_reaudit": any(x in {"UNCLASSIFIED_LEGACY_FREEZE", "UNKNOWN"} for x in impact_classes),
        "scientific_evidence_review_required": "EVIDENCE_DATA" in impact_classes,
        "new_scientific_experiment_authorized": False,
        "claim_expansion_authorized": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    result["impact_sha256"] = _digest({k: v for k, v in result.items() if k != "impact_sha256"})
    return result
