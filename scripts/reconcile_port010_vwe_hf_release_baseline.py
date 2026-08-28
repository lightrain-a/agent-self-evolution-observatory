from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from research_pipeline.config import PROJECT_ROOT
from research_pipeline.paper_first_evidence_acquisition import _plan_status, _summary, validate_evidence_plan
from research_pipeline.paper_first_pre_f0_evidence_control import _public_state, _write_public, control_snapshot
from research_pipeline.paper_first_support_release_watch import release_watch_contract_sha
from reconcile_port010_vwe_release_change_hold import project_into_research_system

CANDIDATE_ID = "PORT-010"
TITLE = "Complex-description boundary in end-to-end 3D world construction"
SOURCE_REF = "arXiv:2608.15265"
HF_DATASET = "https://huggingface.co/datasets/usail-hkust/VWE-Bench"
AUDIT = PROJECT_ROOT / "generated" / "port010-vwe-hf-release-baseline-audit-20260828.json"
PLAN = PROJECT_ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"
PUBLIC_JSON = PROJECT_ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-state.json"
PUBLIC_JS = PROJECT_ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-state.js"
QUEUE = PROJECT_ROOT / "generated" / "paper-first-pre-f0-queue.json"
SUPPORT = PROJECT_ROOT / "generated" / "paper-first-pre-f0-problem-falsifier-preflight.json"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_json(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_audit(audit: dict) -> None:
    material = {k: deepcopy(v) for k, v in audit.items() if k != "audit_sha256"}
    if audit.get("schema_version") != "port010-hf-release-baseline-audit-v1":
        raise SystemExit("unexpected HF baseline audit schema")
    if audit.get("candidate_id") != CANDIDATE_ID or audit.get("candidate_title") != TITLE:
        raise SystemExit("unexpected PORT-010 HF baseline audit identity")
    if audit.get("dataset_url") != HF_DATASET or audit.get("source_ref") != SOURCE_REF:
        raise SystemExit("HF baseline audit source mismatch")
    if audit.get("audit_sha256") != sha256_json(material):
        raise SystemExit("HF baseline audit digest mismatch")
    if audit.get("revision_verified") is not True or len(str(audit.get("observed_revision") or "")) != 40:
        raise SystemExit("HF baseline revision is not independently pinned")
    if audit.get("disposition") != "BASELINE_PINNED_NO_REOPEN":
        raise SystemExit("HF surface is not certified as baseline-only")
    if audit.get("qualifying_author_outcome_artifact") is not False or audit.get("qualifying_original_trajectory_artifact") is not False:
        raise SystemExit("HF surface contains a qualifying artifact; baseline-only reconciler forbidden")
    if audit.get("remaining_reopen_components") != ["per_case_outcomes"]:
        raise SystemExit("HF audit does not preserve frozen reopen blocker")
    if audit.get("scientific_authority") is not False or any((audit.get("authority") or {}).values()):
        raise SystemExit("HF baseline audit leaked authority")


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    validate_audit(audit)
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    matches = [i for i, item in enumerate(plan.get("entries") or []) if item.get("candidate_id") == CANDIDATE_ID and item.get("title") == TITLE]
    if len(matches) != 1:
        raise SystemExit("expected exactly one current PORT-010 VWE object")
    idx = matches[0]
    row = deepcopy(plan["entries"][idx])
    review = row.get("evidence_review") or {}
    adjudication = row.get("release_change_adjudication") or {}
    watch = row.get("release_watch_contract") or {}
    if row.get("status") != "HOLD_EVIDENCE_REVIEW_BLOCKED" or review.get("verdict") != "BLOCK_BAKE_IN":
        raise SystemExit("PORT-010 HOLD/review state drifted")
    if row.get("execution_authorized") is not False or row.get("scientific_authority") is not False:
        raise SystemExit("PORT-010 unexpectedly carries authority")
    for key in ("offline_replay_tier_authorized", "provider_authority", "gpu_authority", "scientific_execution_authority", "scientific_authority"):
        if adjudication.get(key) is not False:
            raise SystemExit(f"PORT-010 zero-authority inversion: {key}")
    required = list(adjudication.get("required_reopen_components") or [])
    remaining = list(adjudication.get("remaining_reopen_components") or [])
    if required != audit.get("required_reopen_components") or remaining != audit.get("remaining_reopen_components"):
        raise SystemExit("HF baseline audit does not bind frozen reopen components")

    targets = [dict(x) for x in watch.get("targets") or [] if isinstance(x, dict)]
    if any(x.get("url") == HF_DATASET for x in targets):
        print("PORT-010 HF release baseline already reconciled")
        return
    targets.append({
        "source_ref": SOURCE_REF,
        "url": HF_DATASET,
        "declaration_kind": "FIRST_PARTY_DATASET",
        "baseline_revision": audit["observed_revision"],
        "scientific_authority": False,
    })
    contract_sha = release_watch_contract_sha(
        candidate_id=CANDIDATE_ID,
        candidate_snapshot_sha256=str(row.get("candidate_snapshot_sha256") or ""),
        targets=targets,
        required_reopen_components=required,
    )
    row["release_watch_contract"] = {
        "candidate_id": CANDIDATE_ID,
        "candidate_snapshot_sha256": str(row.get("candidate_snapshot_sha256") or ""),
        "targets": targets,
        "required_reopen_components": required,
        "remaining_reopen_components": remaining,
        "contract_sha256": contract_sha,
        "scientific_authority": False,
    }
    baseline_audits = list(row.get("release_surface_baseline_audits") or [])
    baseline_audits.append({
        "surface": "HUGGING_FACE_DATASET",
        "url": HF_DATASET,
        "baseline_revision": audit["observed_revision"],
        "audit_artifact": str(AUDIT.relative_to(PROJECT_ROOT)),
        "audit_sha256": audit["audit_sha256"],
        "disposition": audit["disposition"],
        "qualifying_author_outcome_artifact": False,
        "remaining_reopen_components": remaining,
        "scientific_authority": False,
    })
    row["release_surface_baseline_audits"] = baseline_audits
    row["release_change_feedback"] = (
        "Both declared first-party release surfaces are now content-addressed. The Hugging Face VWE-Bench head is pinned, "
        "but the audited dataset surface exposes query/training assets rather than author-released per-case outcomes. "
        "PORT-010 therefore remains HOLD; release changes on either surface route only to zero-authority release audit."
    )
    plan["entries"][idx] = row
    plan.setdefault("policy", {})["release_watch_covers_all_verified_first_party_surfaces"] = True
    plan["generated_at"] = now()
    plan["summary"] = _summary(plan["entries"])
    plan["status"] = _plan_status(plan["entries"])
    errors = validate_evidence_plan(plan)
    if errors:
        raise SystemExit("reconciled evidence plan invalid: " + ";".join(errors))
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    previous_public = json.loads(PUBLIC_JSON.read_text(encoding="utf-8"))
    control = control_snapshot(queue_path=QUEUE, support_path=SUPPORT, plan_path=PLAN)
    stage = {
        "stage": "hf-release-baseline-audit",
        "candidate_ids": [CANDIDATE_ID],
        "provider_calls_executed": 0,
        "scientific_authority": False,
    }
    public = _public_state(plan=plan, control=control, last_stage=stage)
    public["parent_control_snapshot_sha256"] = str(previous_public.get("control_snapshot_sha256") or "")
    _write_public(public, PUBLIC_JSON, PUBLIC_JS)
    project_into_research_system(public)
    print(json.dumps({
        "candidate_id": CANDIDATE_ID,
        "status": row["status"],
        "hf_baseline_revision": audit["observed_revision"],
        "release_watch_target_count": len(targets),
        "release_watch_contract_sha256": contract_sha,
        "remaining_reopen_components": remaining,
        "execution_authorized": row["execution_authorized"],
        "provider_calls_executed": 0,
        "control_snapshot_sha256": public["control_snapshot_sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
