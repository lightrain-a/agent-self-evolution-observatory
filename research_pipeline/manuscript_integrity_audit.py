from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "1.0"

POLICY: dict[str, Any] = {
    "post_draft_integrity_precedes_independent_model_review": True,
    "deterministic_checks_precede_agentic_review": True,
    "every_publishable_number_requires_content_addressed_source_binding": True,
    "every_table_cell_requires_source_field_provenance": True,
    "citation_existence_metadata_passage_direction_numeric_and_scope_are_distinct_checks": True,
    "content_inventory_requires_complete_versioned_extraction_receipt": True,
    "claim_evidence_binding_is_checked_again_after_manuscript_drafting": True,
    "machine_like_prose_lint_is_editorial_not_ai_detector_evasion": True,
    "reader_comprehension_requires_first_use_definition_and_component_io_explanation": True,
    "integrity_audit_cannot_create_evidence_or_authorize_new_experiments": True,
    "independent_reviewer_cannot_self_resolve_integrity_findings": True,
    "all_outputs_have_zero_scientific_experiment_gpu_and_submission_authority": True,
}

MACHINE_LIKE_PHRASES = (
    "it is worth noting that",
    "in today's rapidly evolving",
    "delve into",
    "a myriad of",
    "this comprehensive framework",
    "this novel and robust",
    "paves the way for",
    "underscores the importance of",
)


def _sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_sha(value: Any) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{64}", str(value or "").strip().lower()))


def _value_equal(observed: Any, source: Any) -> bool:
    if isinstance(observed, bool) or isinstance(source, bool):
        return observed is source
    try:
        a = float(observed)
        b = float(source)
        if math.isnan(a) or math.isnan(b):
            return False
        return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)
    except (TypeError, ValueError):
        return str(observed).strip() == str(source).strip()


def _artifact_blockers(row: dict[str, Any], project_root: Path | None, *, prefix: str) -> list[str]:
    blockers: list[str] = []
    artifact = str(row.get("source_artifact") or row.get("artifact_ref") or "").strip()
    expected = str(row.get("source_artifact_sha256") or row.get("artifact_sha256") or "").strip().lower()
    if not artifact:
        blockers.append(f"{prefix}:source-artifact-missing")
        return blockers
    if not _is_sha(expected):
        blockers.append(f"{prefix}:source-artifact-sha256-missing-or-invalid")
    if project_root is None:
        return blockers
    raw = Path(artifact)
    if raw.is_absolute():
        blockers.append(f"{prefix}:absolute-source-artifact-forbidden")
        return blockers
    root = project_root.resolve()
    path = (root / raw).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        blockers.append(f"{prefix}:source-artifact-path-traversal")
        return blockers
    if not path.is_file():
        blockers.append(f"{prefix}:source-artifact-missing-on-disk")
        return blockers
    if _is_sha(expected) and _sha_file(path) != expected:
        blockers.append(f"{prefix}:source-artifact-sha256-mismatch")
    return blockers


def lint_machine_like_prose(text: str) -> dict[str, Any]:
    lowered = str(text or "").lower()
    hits = [{"code": "stock-machine-like-phrase", "phrase": phrase, "count": lowered.count(phrase)} for phrase in MACHINE_LIKE_PHRASES if phrase in lowered]
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", str(text or "")) if part.strip()]
    connector_pattern = re.compile(r"\b(moreover|furthermore|additionally|consequently|therefore|notably)\b", re.I)
    connector_sentences = sum(bool(connector_pattern.search(sentence)) for sentence in sentences)
    density = connector_sentences / max(1, len(sentences))
    warnings = list(hits)
    if len(sentences) >= 8 and density > 0.35:
        warnings.append({"code": "transition-word-density-high", "density": round(density, 4)})
    return {
        "schema_version": SCHEMA_VERSION,
        "warnings": warnings,
        "warning_count": len(warnings),
        "ai_detector_evasion_goal": False,
        "scientific_authority": False,
    }


def audit_post_draft_integrity(manifest: dict[str, Any], *, project_root: Path | None = None) -> dict[str, Any]:
    hard: list[str] = []
    editorial: list[str] = []
    manuscript_ref = str(manifest.get("manuscript_ref") or "").strip()
    manuscript_sha = str(manifest.get("manuscript_sha256") or "").strip().lower()
    if not manuscript_ref:
        hard.append("manuscript-ref-missing")
    if not _is_sha(manuscript_sha):
        hard.append("manuscript-sha256-missing-or-invalid")

    facts = [row for row in manifest.get("facts") or [] if isinstance(row, dict)]
    citations = [row for row in manifest.get("citations") or [] if isinstance(row, dict)]
    numbers = [row for row in manifest.get("numbers") or [] if isinstance(row, dict)]
    tables = [row for row in manifest.get("tables") or [] if isinstance(row, dict)]
    claims = [row for row in manifest.get("claims") or [] if isinstance(row, dict)]
    inventory = manifest.get("content_inventory") if isinstance(manifest.get("content_inventory"), dict) else {}
    if not inventory:
        hard.append("content-inventory-missing")
    if inventory.get("extraction_complete") is not True:
        hard.append("content-inventory-extraction-not-complete")
    if not str(inventory.get("extractor_version") or "").strip():
        hard.append("content-inventory-extractor-version-missing")
    if not _is_sha(inventory.get("extractor_sha256")):
        hard.append("content-inventory-extractor-sha256-missing-or-invalid")
    for key, rows in (("facts", facts), ("citations", citations), ("numbers", numbers), ("tables", tables), ("claims", claims)):
        expected = inventory.get(key)
        if not isinstance(expected, int) or expected < 0:
            hard.append(f"content-inventory-invalid:{key}")
        elif expected != len(rows):
            hard.append(f"content-inventory-count-mismatch:{key}:{expected}!={len(rows)}")
    if not claims:
        hard.append("manuscript-claim-ledger-empty")

    for index, row in enumerate(facts):
        fid = str(row.get("fact_id") or index)
        prefix = f"fact:{fid}"
        if not str(row.get("source_ref") or "").strip():
            hard.append(f"{prefix}:source-ref-missing")
        if row.get("source_verified") is not True:
            hard.append(f"{prefix}:source-not-verified")
        if row.get("passage_support_verified") is not True:
            hard.append(f"{prefix}:passage-support-not-verified")

    for index, row in enumerate(citations):
        cid = str(row.get("citation_id") or index)
        prefix = f"citation:{cid}"
        for field in ("existence_verified", "metadata_identity_verified", "passage_support_verified", "directionality_verified", "scope_verified"):
            if row.get(field) is not True:
                hard.append(f"{prefix}:{field.replace('_', '-')}-failed")
        if row.get("contains_numeric_claim") is True and row.get("numeric_match_verified") is not True:
            hard.append(f"{prefix}:numeric-match-not-verified")
        if not str(row.get("source_ref") or "").strip():
            hard.append(f"{prefix}:source-ref-missing")

    for index, row in enumerate(numbers):
        nid = str(row.get("number_id") or index)
        prefix = f"number:{nid}"
        hard.extend(_artifact_blockers(row, project_root, prefix=prefix))
        if not str(row.get("source_field") or "").strip():
            hard.append(f"{prefix}:source-field-missing")
        if "observed_value" not in row or "source_value" not in row:
            hard.append(f"{prefix}:observed-or-source-value-missing")
        elif not _value_equal(row.get("observed_value"), row.get("source_value")):
            hard.append(f"{prefix}:value-mismatch")

    for index, table in enumerate(tables):
        tid = str(table.get("table_id") or index)
        script = table.get("generation_script") if isinstance(table.get("generation_script"), dict) else {}
        hard.extend(_artifact_blockers(script, project_root, prefix=f"table:{tid}:generation-script"))
        cells = [row for row in table.get("cells") or [] if isinstance(row, dict)]
        if not cells:
            hard.append(f"table:{tid}:cells-missing")
        for cell_index, cell in enumerate(cells):
            cell_id = str(cell.get("cell_id") or cell_index)
            prefix = f"table:{tid}:cell:{cell_id}"
            hard.extend(_artifact_blockers(cell, project_root, prefix=prefix))
            if not str(cell.get("source_field") or "").strip():
                hard.append(f"{prefix}:source-field-missing")
            if "observed_value" not in cell or "source_value" not in cell:
                hard.append(f"{prefix}:observed-or-source-value-missing")
            elif not _value_equal(cell.get("observed_value"), cell.get("source_value")):
                hard.append(f"{prefix}:value-mismatch")

    expected_claim_ids = {str(x) for x in manifest.get("expected_claim_ids") or [] if str(x)}
    seen_claims: set[str] = set()
    for index, row in enumerate(claims):
        cid = str(row.get("claim_id") or "").strip()
        prefix = f"claim:{cid or index}"
        if not cid:
            hard.append(f"{prefix}:claim-id-missing")
            continue
        seen_claims.add(cid)
        if not str(row.get("statement_ref") or "").strip():
            hard.append(f"{prefix}:statement-ref-missing")
        if not [x for x in row.get("evidence_refs") or [] if str(x)]:
            hard.append(f"{prefix}:evidence-binding-missing")
        if row.get("supported") is not True:
            hard.append(f"{prefix}:unsupported-or-unverified")
    missing_claims = sorted(expected_claim_ids - seen_claims)
    if missing_claims:
        hard.append("expected-claims-not-audited:" + ",".join(missing_claims))

    reader = manifest.get("reader_comprehension") if isinstance(manifest.get("reader_comprehension"), dict) else {}
    for row in reader.get("terms") or []:
        if not isinstance(row, dict):
            continue
        term = str(row.get("term") or "UNKNOWN")
        if row.get("first_use_defined") is not True:
            editorial.append(f"term-first-use-not-defined:{term}")
    for row in reader.get("components") or []:
        if not isinstance(row, dict):
            continue
        component = str(row.get("component") or "UNKNOWN")
        if row.get("input_explained") is not True:
            editorial.append(f"component-input-not-explained:{component}")
        if row.get("output_explained") is not True:
            editorial.append(f"component-output-not-explained:{component}")

    prose = lint_machine_like_prose(str(manifest.get("manuscript_text") or ""))
    integrity_pass = not hard
    editorial_pass = not editorial
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS_POST_DRAFT_INTEGRITY" if integrity_pass and editorial_pass else "BLOCK_POST_DRAFT_INTEGRITY",
        "policy": dict(POLICY),
        "manuscript_ref": manuscript_ref,
        "manuscript_sha256": manuscript_sha,
        "integrity_pass": integrity_pass,
        "editorial_pass": editorial_pass,
        "pass": integrity_pass and editorial_pass,
        "hard_blockers": sorted(set(hard)),
        "editorial_blockers": sorted(set(editorial)),
        "prose_lint": prose,
        "summary": {
            "facts": len(facts), "citations": len(citations), "numbers": len(numbers), "tables": len(tables), "claims": len(claims),
            "hard_blockers": len(set(hard)), "editorial_blockers": len(set(editorial)), "prose_warnings": int(prose.get("warning_count") or 0),
        },
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }


def build_post_draft_integrity_receipt(manifest: dict[str, Any], *, project_root: Path | None = None) -> dict[str, Any]:
    audit = audit_post_draft_integrity(manifest, project_root=project_root)
    identity = {
        "manuscript_ref": audit["manuscript_ref"],
        "manuscript_sha256": audit["manuscript_sha256"],
        "integrity_pass": audit["integrity_pass"],
        "editorial_pass": audit["editorial_pass"],
        "pass": audit["pass"],
        "hard_blockers": audit["hard_blockers"],
        "editorial_blockers": audit["editorial_blockers"],
        "summary": audit["summary"],
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "receipt_type": "post-draft-integrity",
        **identity,
        "receipt_sha256": _sha(identity),
        "prose_lint": audit["prose_lint"],
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }


def build_manuscript_integrity_layer_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "MANUSCRIPT_INTEGRITY_CONTRACTS_INSTALLED",
        "policy": dict(POLICY),
        "audit_surfaces": [
            "fact-source-support", "citation-existence-metadata-passage-direction", "numeric-artifact-binding",
            "table-cell-provenance", "claim-evidence-binding", "reader-comprehension", "machine-like-prose-editorial-lint",
        ],
        "review_sequence": [
            "deterministic-post-draft-integrity", "independent-model-review", "reviewer-issue-graph",
            "targeted-repair", "deterministic-re-audit", "claim-audit",
        ],
        "summary": {
            "audit_surfaces": 7,
            "deterministic_before_agentic_review": 1,
            "automatic_scientific_authority": 0,
            "automatic_experiment_authority": 0,
            "automatic_gpu_authority": 0,
            "automatic_submission_authority": 0,
        },
        "scientific_authority": False,
    }


def integrity_findings_to_reviewer_receipt(audit: dict[str, Any]) -> dict[str, Any]:
    """Compile deterministic integrity failures into ReviewerIssueGraph input without experiment authority."""
    objections = []
    actions = []
    blockers = list(audit.get("hard_blockers") or []) + list(audit.get("editorial_blockers") or [])
    for index, blocker in enumerate(blockers, start=1):
        oid = f"INT-{index:03d}"
        hard = blocker in set(audit.get("hard_blockers") or [])
        category = (
            "citation-integrity" if blocker.startswith("citation:") else
            "numeric-integrity" if blocker.startswith("number:") or ":value-mismatch" in blocker else
            "table-integrity" if blocker.startswith("table:") else
            "claim-evidence-integrity" if blocker.startswith("claim:") or blocker.startswith("expected-claims-") else
            "fact-integrity" if blocker.startswith("fact:") else
            "reader-comprehension"
        )
        objections.append({
            "objection_id": oid,
            "category": category,
            "text": blocker,
            "decision_critical": hard,
            "evidence_state": "EXISTING_EVIDENCE" if hard else "UNCERTAIN",
            "claim_ids": [],
        })
        actions.append({
            "objection_id": oid,
            "action_class": "NARRATIVE_REPAIR" if not hard or "mismatch" in blocker else "PRESERVE_LIMITATION",
            "claim_expansion_authorized": False,
        })
    review_sha = _sha({"manuscript_sha256": audit.get("manuscript_sha256"), "blockers": blockers})
    return {
        "review_sha256": review_sha,
        "review_kind": "DETERMINISTIC_POST_DRAFT_INTEGRITY",
        "objections": objections,
        "actions": actions,
        "reviewer_prose_exposed": False,
        "experiment_authority": False,
        "scientific_authority": False,
    }
