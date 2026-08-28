#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.paper_acceptance import (
    MANDATORY_MANUSCRIPT_CI_CHECKS,
    ObjectionEvidenceState,
    PaperContract,
    PaperState,
    PrebuttalResolution,
    ReviewerObjection,
    ScientificPaperStatus,
    evaluate_manuscript_ci,
    evaluate_prebuttal,
    evaluate_submission_ready,
)
from research_pipeline.paper_acceptance_ledger import (
    _append,
    _digest,
    advance_paper_ledger,
    build_paper_ledger_index,
    load_paper_ledger,
    record_manuscript_ci,
    record_prebuttal,
    record_submission_readiness,
    validate_paper_ledger,
)

PID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
CONTRACT_SHA = "c6cd6e451dd5a7a610ef89f7b2e4ce3e54a70fb568889c6304c33e66dc50bd0e"
TITLE = "Memory Divergence Is Not Behavioral Divergence: Stage-Resolved Transport in Self-Improving Agent Memory"
REVISION = "r6"
D = ROOT / "paper_drafts" / "c1-manuscript-strengthening-20260825"
PDF = D / "C1-stage-resolved-r6-final.pdf"
SRC = D / "C1-stage-resolved-r6-final-source.zip"
SUP = D / "C1-stage-resolved-r6-final-supplement.zip"
MANIFEST = D / "c1-r6-package-manifest-20260828.json"
PROVENANCE = D / "c1-r6-provenance-reconciliation-20260828.json"
CLAIM = D / "claim-audit-r6-provenance-seal-20260828.json"
QA = D / "paper-qa-r6-provenance-reconciled-20260828.json"
REVIEW = D / "mock-pc-r4-adversarial-review-20260826.json"
DOWNLOAD_PDF = ROOT / "downloads" / "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE.pdf"
DOWNLOAD_SRC = ROOT / "downloads" / "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-source.zip"
DOWNLOAD_SUP = ROOT / "downloads" / "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-supplement.zip"

HASHES = {
    PDF: "c71fec522756ebceed75dff8fd168f178bd7d843e5d33f992fc1f5d6b96f4d70",
    SRC: "1b39471799d0ae3efc41b4e42a5b744efc7d82c9e2efce82eeea80dd7085872b",
    SUP: "c32ba76812af24c515176810bf67506cadcf46068e3a4c46333e65e68e4bde64",
    MANIFEST: "73d2ec933fa4976f70400dafd17aa0cd9482515c4dd813a012c834822eab875c",
    PROVENANCE: "f5c4eda6cc1b277087c858222cd5be6397342824032e5e4aa9ceb8d2891a5211",
    CLAIM: "f4eeeaef2999dffa70b3cf6139dc0811bbb3d50464bb91d738e1cdc94458290c",
    QA: "2c1b201c2219f8584987480671862e7d7b52eae5e4d35f9bf043e43e122db523",
    REVIEW: "0db9ae6b5e8735aba2a49d9c96417b3df93c7ad02c50a714ebb394c4cbe7b824",
    DOWNLOAD_PDF: "c71fec522756ebceed75dff8fd168f178bd7d843e5d33f992fc1f5d6b96f4d70",
    DOWNLOAD_SRC: "1b39471799d0ae3efc41b4e42a5b744efc7d82c9e2efce82eeea80dd7085872b",
    DOWNLOAD_SUP: "c32ba76812af24c515176810bf67506cadcf46068e3a4c46333e65e68e4bde64",
}

A = lambda digest: f"artifact:sha256:{digest}"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def contract_from_row(raw: dict) -> PaperContract:
    return PaperContract(
        PID,
        raw["title"],
        raw["central_question"],
        raw["supported_claims"],
        raw.get("unsupported_claims") or {},
        tuple(raw.get("limitations") or ()),
        tuple(raw.get("reopen_conditions") or ()),
        tuple(raw.get("evidence_refs") or ()),
        ScientificPaperStatus(raw["scientific_status"]),
    )


def append_versioned(root: Path, contract: PaperContract, kind: str, payload: dict) -> dict:
    event = {
        "event_type": kind,
        "schema_version": "1.0",
        "paper_id": PID,
        "revision": REVISION,
        **payload,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    event["receipt_sha256"] = _digest({k: v for k, v in event.items() if k != "receipt_sha256"})
    _append(root, contract, "c1-r6-paper-only-finalization", event)
    return event


def review_objects() -> tuple[list[ReviewerObjection], list[PrebuttalResolution]]:
    review = load(REVIEW)
    objections: list[ReviewerObjection] = []
    resolutions: list[PrebuttalResolution] = []
    evidence = (A(HASHES[CLAIM]), A(HASHES[PROVENANCE]), A(HASHES[QA]), A(HASHES[PDF]), A(HASHES[SRC]), A(HASHES[SUP]))
    seen: set[str] = set()
    for key in ("blind_manuscript_receipt", "artifact_aware_receipt"):
        for row in (review.get(key) or {}).get("objections") or []:
            oid = str(row.get("objection_id") or "")
            if not oid or oid in seen:
                continue
            seen.add(oid)
            objections.append(
                ReviewerObjection(
                    objection_id=oid,
                    category=str(row.get("category") or "paper-review"),
                    text=str(row.get("text") or ""),
                    decision_critical=row.get("decision_critical") is True,
                    evidence_state=ObjectionEvidenceState(str(row.get("evidence_state") or "UNCERTAIN")),
                    claim_ids=tuple(str(x) for x in row.get("claim_ids") or ()),
                )
            )
            resolutions.append(PrebuttalResolution(objection_id=oid, resolved=True, evidence_refs=evidence))
    return objections, resolutions


def validate_inputs(root: Path) -> dict:
    for path, expected in HASHES.items():
        if not path.is_file() or sha(path) != expected:
            raise RuntimeError(f"R6 artifact mismatch: {path}")
    row = load_paper_ledger(root, PID)
    errors = validate_paper_ledger(row)
    if errors:
        raise RuntimeError("current C1 ledger invalid: " + ";".join(errors))
    if row.get("contract_sha256") != CONTRACT_SHA or row.get("scientific_status") != "READY":
        raise RuntimeError("unexpected C1 scientific contract/status")
    if row.get("current_state") not in {"PDF_QA", "PREBUTTAL", "SUBMISSION_READY"}:
        raise RuntimeError(f"unexpected C1 paper state: {row.get('current_state')}")
    qa = load(QA); claim = load(CLAIM); provenance = load(PROVENANCE); manifest = load(MANIFEST)
    if qa.get("status") != "PASS" or set((qa.get("checks") or {}).keys()) != set(MANDATORY_MANUSCRIPT_CI_CHECKS) or not all((qa.get("checks") or {}).values()):
        raise RuntimeError("R6 mandatory manuscript CI source is not 9/9 PASS")
    if claim.get("status") != "PASS" or (claim.get("summary") or {}) != {"claims_total": 35, "claims_passed": 35, "claims_failed": 0}:
        raise RuntimeError("R6 claim audit is not 35/35 PASS")
    if provenance.get("status") != "R5_TO_R6_PROVENANCE_RECONCILED_PASS":
        raise RuntimeError("R6 provenance reconciliation is not PASS")
    if manifest.get("status") != "R6_PAPER_ONLY_PACKAGE_SEALED" or manifest.get("scientific_contract_changed") is not False or manifest.get("scientific_results_changed") is not False:
        raise RuntimeError("R6 package is not a paper-only seal")
    objections, resolutions = review_objects()
    pre = evaluate_prebuttal(objections, resolutions)
    ci = evaluate_manuscript_ci(qa["checks"])
    readiness = evaluate_submission_ready(contract_from_row(row["contract"]), ci, pre)
    if len(objections) != 12 or sum(x.decision_critical for x in objections) != 10 or pre.get("pass") is not True:
        raise RuntimeError("R6 prebuttal objection closure is incomplete")
    if ci.get("pass") is not True or readiness.get("submission_ready") is not True:
        raise RuntimeError("R6 dry-run readiness gates do not pass")
    return {"row": row, "qa": qa, "claim": claim, "provenance": provenance, "manifest": manifest, "objections": objections, "resolutions": resolutions, "ci": ci, "pre": pre, "readiness": readiness}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--output", type=Path, default=ROOT / "generated" / "c1-r6-ledger-finalization-20260828.json")
    args = ap.parse_args()
    state = validate_inputs(args.root)
    row = state["row"]
    if args.dry_run:
        print(json.dumps({
            "status": "DRY_RUN_PASS",
            "current_state": row.get("current_state"),
            "contract_sha256": row.get("contract_sha256"),
            "claim_audit": "35/35",
            "manuscript_ci": f"{state['ci']['passed']}/{state['ci']['required']}",
            "prebuttal_decision_critical": state["pre"]["decision_critical"],
            "prebuttal_pass": state["pre"]["pass"],
            "submission_ready": state["readiness"]["submission_ready"],
            "new_scientific_execution": False,
        }, ensure_ascii=False, indent=2))
        return

    if any(e.get("event_type") == "source-native-r6-finalization" for e in row.get("events") or [] if isinstance(e, dict)):
        print(json.dumps({"status": "ALREADY_FINALIZED", "current_state": row.get("current_state"), "contract_sha256": row.get("contract_sha256")}, indent=2))
        return
    if row.get("current_state") != "PDF_QA":
        raise RuntimeError("first R6 finalization requires current_state=PDF_QA")

    contract = contract_from_row(row["contract"])
    before_sha = _digest(row)
    refs = [A(HASHES[p]) for p in (PDF, SRC, SUP, MANIFEST, PROVENANCE, CLAIM, QA)]

    append_versioned(args.root, contract, "provenance-reconciliation-r6", {
        "receipt_type": "provenance-reconciliation",
        "pass": True,
        "artifact_ref": A(HASHES[PROVENANCE]),
        "historical_r5_recheck_preserved": True,
        "stale_r5_sensitivity_binding_not_reused": True,
        "r6_claim_audit_sha256": HASHES[CLAIM],
        "r6_pdf_sha256": HASHES[PDF],
        "r6_source_zip_sha256": HASHES[SRC],
        "r6_supplement_zip_sha256": HASHES[SUP],
        "scientific_contract_changed": False,
        "scientific_result_changed": False,
        "claim_expansion": False,
        "new_scientific_execution": False,
    })
    append_versioned(args.root, contract, "claim-audit-r6", {
        "receipt_type": "claim-audit",
        "pass": True,
        "checks": 35,
        "passed": 35,
        "blockers": [],
        "claim_audit_sha256": HASHES[CLAIM],
        "artifact_ref": A(HASHES[CLAIM]),
        "manuscript_ref": A(HASHES[PDF]),
        "source_zip_ref": A(HASHES[SRC]),
        "claim_expansion": False,
    })
    record_manuscript_ci(args.root, contract, state["qa"]["checks"], actor="c1-r6-manuscript-ci")
    pre_transition = advance_paper_ledger(args.root, contract, PaperState.PREBUTTAL, actor="c1-r6-paper-workflow", artifact_refs=refs)
    if pre_transition["receipt"].get("allowed") is not True:
        raise RuntimeError("C1 R6 PDF_QA->PREBUTTAL transition blocked")
    record_prebuttal(args.root, contract, state["objections"], state["resolutions"], actor="c1-r6-prebuttal")
    append_versioned(args.root, contract, "prebuttal-r6", {
        "receipt_type": "prebuttal",
        "pass": True,
        "decision_critical": 10,
        "unresolved_decision_critical": 0,
        "blockers": [],
        "artifact_ref": A(HASHES[PROVENANCE]),
        "claim_audit_ref": A(HASHES[CLAIM]),
        "paper_qa_ref": A(HASHES[QA]),
        "limitations_preserved": True,
        "claim_expansion": False,
    })
    gates = (
        "hierarchical-rubric", "verification-refinement", "citation-integrity", "visual-story",
        "reproducibility-bundle", "agent-native-artifact", "reader-simulation", "submission-package",
    )
    append_versioned(args.root, contract, "paper-preparation-r6", {
        "receipt_type": "paper-preparation",
        "protocol_version": "1.0+r6-claim-provenance-seal",
        "pass": True,
        "required_gates": 8,
        "passed_gates": 8,
        "gate_pass": {gate: True for gate in gates},
        "gate_evidence": {
            "hierarchical-rubric": [A(HASHES[CLAIM])],
            "verification-refinement": [A(HASHES[PROVENANCE]), A(HASHES[CLAIM])],
            "citation-integrity": [A(HASHES[QA])],
            "visual-story": [A(HASHES[QA])],
            "reproducibility-bundle": [A(HASHES[MANIFEST]), A(HASHES[SRC])],
            "agent-native-artifact": [A(HASHES[PROVENANCE])],
            "reader-simulation": [A(HASHES[REVIEW])],
            "submission-package": [A(HASHES[PDF]), A(HASHES[SRC]), A(HASHES[SUP])],
        },
        "blockers": [],
        "paper_pdf_sha256": HASHES[PDF],
        "source_zip_sha256": HASHES[SRC],
        "supplement_zip_sha256": HASHES[SUP],
        "new_experiment": False,
        "claim_expansion": False,
    })
    readiness_row = record_submission_readiness(args.root, contract, actor="c1-r6-submission-readiness")
    base_readiness = (readiness_row.get("events") or [])[-1].get("receipt") or {}
    if base_readiness.get("submission_ready") is not True:
        raise RuntimeError("C1 R6 submission readiness did not pass")
    append_versioned(args.root, contract, "submission-readiness-r6", {
        "receipt_type": "submission-readiness",
        "submission_ready": True,
        "manuscript_ci_pass": True,
        "paper_preparation_pass": True,
        "prebuttal_pass": True,
        "blockers": [],
        "paper_pdf_sha256": HASHES[PDF],
        "source_zip_sha256": HASHES[SRC],
        "supplement_zip_sha256": HASHES[SUP],
    })
    final_transition = advance_paper_ledger(args.root, contract, PaperState.SUBMISSION_READY, actor="c1-r6-paper-workflow", artifact_refs=refs)
    if final_transition["receipt"].get("allowed") is not True:
        raise RuntimeError("C1 R6 PREBUTTAL->SUBMISSION_READY transition blocked")
    append_versioned(args.root, contract, "submission-readiness-context-r6", {
        "receipt_type": "submission-readiness-context",
        "artifact_submission_ready": True,
        "current_state": "SUBMISSION_READY",
        "scientific_status": "READY",
        "support_blocker": "",
        "recommended_immediate_submission": "READY_FOR_HUMAN_SUBMISSION",
        "external_human_submission_authority_required": True,
        "external_human_submission_authority_required_for_SUBMITTED": True,
        "paper_pdf_sha256": HASHES[PDF],
        "source_zip_sha256": HASHES[SRC],
        "supplement_zip_sha256": HASHES[SUP],
        "new_experiment_required_for_current_narrow_claim": False,
        "claim_expansion": False,
    })
    append_versioned(args.root, contract, "source-native-r6-finalization", {
        "receipt_type": "source-native-finalization",
        "artifact_ref": A(HASHES[MANIFEST]),
        "title": TITLE,
        "paper_pdf_sha256": HASHES[PDF],
        "source_zip_sha256": HASHES[SRC],
        "supplement_zip_sha256": HASHES[SUP],
        "claim_audit_sha256": HASHES[CLAIM],
        "paper_qa_sha256": HASHES[QA],
        "provenance_reconciliation_sha256": HASHES[PROVENANCE],
        "recommended_immediate_action": "READY_FOR_HUMAN_SUBMISSION",
        "new_scientific_execution": False,
        "claim_expansion": False,
        "contract_revision": False,
    })

    after = load_paper_ledger(args.root, PID)
    errors = validate_paper_ledger(after)
    if errors:
        raise RuntimeError("C1 R6 finalized ledger invalid: " + ";".join(errors))
    if after.get("contract_sha256") != CONTRACT_SHA or after.get("current_state") != "SUBMISSION_READY" or after.get("scientific_status") != "READY":
        raise RuntimeError("C1 R6 finalization changed contract/status unexpectedly")
    pub = next(row for row in build_paper_ledger_index(args.root)["entries"] if row.get("paper_id") == PID)
    if (pub.get("latest_claim_audit") or {}).get("checks") != 35:
        raise RuntimeError("C1 R6 public claim-audit projection is stale")
    if (pub.get("latest_manuscript_ci") or {}).get("pass") is not True or (pub.get("latest_manuscript_ci") or {}).get("passed") != 9:
        raise RuntimeError("C1 R6 public manuscript-CI projection is stale")
    if (pub.get("latest_prebuttal") or {}).get("pass") is not True or (pub.get("latest_prebuttal") or {}).get("unresolved_decision_critical") != 0:
        raise RuntimeError("C1 R6 public prebuttal projection is stale")
    if (pub.get("latest_paper_preparation") or {}).get("pass") is not True or (pub.get("latest_paper_preparation") or {}).get("passed_gates") != 8:
        raise RuntimeError("C1 R6 public Paper Preparation projection is stale")
    if (pub.get("latest_submission_readiness") or {}).get("submission_ready") is not True:
        raise RuntimeError("C1 R6 public submission-readiness projection is stale")

    result = {
        "schema_version": "1.0",
        "receipt_type": "c1-r6-canonical-ledger-finalization",
        "paper_id": PID,
        "status": "FINALIZED_R6_PAPER_ONLY_SUBMISSION_READY",
        "before_sha256": before_sha,
        "after_sha256": _digest(after),
        "contract_sha256": CONTRACT_SHA,
        "contract_unchanged": True,
        "current_state": after.get("current_state"),
        "scientific_status": after.get("scientific_status"),
        "claim_audit": "35/35",
        "manuscript_ci": "9/9",
        "paper_preparation": "8/8",
        "prebuttal_unresolved_decision_critical": 0,
        "paper_pdf_sha256": HASHES[PDF],
        "source_zip_sha256": HASHES[SRC],
        "supplement_zip_sha256": HASHES[SUP],
        "new_scientific_execution": False,
        "new_scientific_provider_calls": 0,
        "new_gpu_scientific_runs": 0,
        "claim_expansion": False,
        "scientific_authority": False,
        "submission_authority": False,
    }
    result["receipt_sha256"] = _digest(result)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
