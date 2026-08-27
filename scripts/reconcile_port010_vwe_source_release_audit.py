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
SOURCE_REF = "arXiv:2608.15265"
SOURCE_REPO = "https://github.com/usail-hkust/VibeWorlding-Gym"
AUDIT = PROJECT_ROOT / "generated" / "port010-vwe-source-release-audit-20260827.json"
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
    material = {k: deepcopy(v) for k, v in audit.items() if k not in {"schema_version", "generated_at", "audit_sha256"}}
    if audit.get("schema_version") != "port010-source-release-audit-v1" or audit.get("candidate_id") != CANDIDATE_ID:
        raise SystemExit("unexpected PORT-010 source-release audit identity")
    if audit.get("source_repo") != SOURCE_REPO or audit.get("audit_sha256") != sha256_json(material):
        raise SystemExit("PORT-010 source-release audit digest/source mismatch")
    if audit.get("disposition") != "RECHECKED_RELEASE_IRRELEVANT" or audit.get("admin_only_change") is not True:
        raise SystemExit("source release is not certified irrelevant; do not reconcile automatically")
    if audit.get("outcome_artifact_candidate_paths") not in ([], None) or audit.get("qualifying_author_outcome_artifact") is not False:
        raise SystemExit("source release contains an outcome candidate; HOLD-only reconciliation forbidden")
    if audit.get("support_qualified") is not False or any(audit.get(k) is not False for k in ("generator_reopen_authorized","problem_gate_authorized","method_authorized","experiment_authorized","p0_authorized","gpu_authorized","scientific_authority")):
        raise SystemExit("source-release audit leaked authority")


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    validate_audit(audit)
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    idx = next(i for i, item in enumerate(plan.get("entries") or []) if item.get("candidate_id") == CANDIDATE_ID)
    row = deepcopy(plan["entries"][idx])
    if row.get("status") != "HOLD_EVIDENCE_REVIEW_BLOCKED" or (row.get("evidence_review") or {}).get("verdict") != "BLOCK_BAKE_IN":
        raise SystemExit("PORT-010 effective HOLD changed; source-release reconciliation aborted")
    if row.get("execution_authorized") is not False or row.get("scientific_authority") is not False:
        raise SystemExit("PORT-010 HOLD unexpectedly carries authority")
    required = list((row.get("release_change_adjudication") or {}).get("required_reopen_components") or [])
    remaining = list((row.get("release_change_adjudication") or {}).get("remaining_reopen_components") or [])
    if required != audit.get("required_reopen_components") or remaining != audit.get("remaining_reopen_components"):
        raise SystemExit("source-release audit does not bind frozen reopen components")

    prior_history = list(row.get("source_release_audit_history") or [])
    if any(str(item.get("audit_sha256") or "") == audit["audit_sha256"] for item in prior_history if isinstance(item, dict)):
        print("PORT-010 source-release audit already reconciled")
        return

    target = {
        "source_ref": SOURCE_REF,
        "url": SOURCE_REPO,
        "declaration_kind": "FIRST_PARTY_REPOSITORY",
        "baseline_revision": audit["observed_revision"],
        "scientific_authority": False,
    }
    contract_sha = release_watch_contract_sha(
        candidate_id=CANDIDATE_ID,
        candidate_snapshot_sha256=str(row.get("candidate_snapshot_sha256") or ""),
        targets=[target],
        required_reopen_components=required,
    )
    row["release_watch_contract"] = {
        "candidate_id": CANDIDATE_ID,
        "candidate_snapshot_sha256": str(row.get("candidate_snapshot_sha256") or ""),
        "targets": [target],
        "required_reopen_components": required,
        "remaining_reopen_components": remaining,
        "contract_sha256": contract_sha,
        "scientific_authority": False,
    }
    row["source_release_audit_count"] = int(row.get("source_release_audit_count") or 0) + 1
    prior_history.append({
        "audited_at": audit.get("generated_at"),
        "audit_artifact": str(AUDIT.relative_to(PROJECT_ROOT)),
        "audit_sha256": audit["audit_sha256"],
        "source_repo": SOURCE_REPO,
        "baseline_revision": audit["baseline_revision"],
        "observed_revision": audit["observed_revision"],
        "ahead_by": int(audit.get("ahead_by") or 0),
        "changed_paths": [item.get("path") for item in audit.get("changed_files") or []],
        "outcome_artifact_candidate_paths": list(audit.get("outcome_artifact_candidate_paths") or []),
        "disposition": "RECHECKED_RELEASE_IRRELEVANT",
        "materialized_reopen_components_from_this_change": [],
        "remaining_reopen_components": remaining,
        "support_qualified": False,
        "scientific_reopen_authorized": False,
        "scientific_authority": False,
    })
    row["source_release_audit_history"] = prior_history
    row["latest_source_release_adjudication"] = {
        "observed_revision": audit["observed_revision"],
        "disposition": "RECHECKED_RELEASE_IRRELEVANT",
        "admin_only_change": True,
        "readme_change_citation_admin_only": True,
        "outcome_artifact_candidate_paths": [],
        "required_reopen_components": required,
        "materialized_reopen_components": list((row.get("release_change_adjudication") or {}).get("materialized_reopen_components") or []),
        "remaining_reopen_components": remaining,
        "effective_status": "HOLD_EVIDENCE_REVIEW_BLOCKED",
        "execution_authorized": False,
        "provider_authority": False,
        "gpu_authority": False,
        "scientific_authority": False,
    }
    row["release_change_feedback"] = "VibeWorlding-Gym source revision changed, but the exact Git diff is licensing/citation-only and materializes no frozen reopen component. PORT-010 remains HOLD; future source changes are watched from the new immutable baseline."
    plan["entries"][idx] = row
    plan.setdefault("policy", {})["effective_hold_release_watch_uses_current_reopen_contract"] = True
    plan["generated_at"] = now()
    plan["summary"] = _summary(plan["entries"])
    plan["status"] = _plan_status(plan["entries"])
    errors = validate_evidence_plan(plan)
    if errors:
        raise SystemExit("reconciled evidence plan invalid: " + ";".join(errors))
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    previous_public = json.loads(PUBLIC_JSON.read_text(encoding="utf-8"))
    control = control_snapshot(queue_path=QUEUE, support_path=SUPPORT, plan_path=PLAN)
    stage = {"stage":"source-release-audit","candidate_ids":[CANDIDATE_ID],"provider_calls_executed":0,"scientific_authority":False}
    public = _public_state(plan=plan, control=control, last_stage=stage)
    public["parent_control_snapshot_sha256"] = str(previous_public.get("control_snapshot_sha256") or "")
    _write_public(public, PUBLIC_JSON, PUBLIC_JS)
    project_into_research_system(public)
    print(json.dumps({
        "candidate_id":CANDIDATE_ID,
        "status":row["status"],
        "source_release_disposition":"RECHECKED_RELEASE_IRRELEVANT",
        "watch_baseline_revision":audit["observed_revision"],
        "release_watch_contract_sha256":contract_sha,
        "remaining_reopen_components":remaining,
        "execution_authorized":row["execution_authorized"],
        "control_snapshot_sha256":public["control_snapshot_sha256"],
    },indent=2))


if __name__ == "__main__":
    main()
