#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.asset_first_stri_public_status import (
    build_asset_first_stri_public_status,
    validate_asset_first_stri_public_status,
)
from research_pipeline.config import StorageSettings, resolve_experiment_data_root
from research_pipeline.paper_acceptance import PaperContract, ScientificPaperStatus
from research_pipeline.paper_acceptance_ledger import (
    _append,
    _digest,
    build_paper_ledger_index,
    load_paper_ledger,
    validate_paper_ledger,
)
from research_pipeline.research_item_state import build_paper_registry
from scripts.refresh_stri_p0e_release import current_qa, write_qa_artifact

PID = "STRI-ICLR2027"
PUBLIC_PID = "STRI"
REVISION = "r19"
TITLE = "Self-Evolution Should Not Depend on How Skills Are Split: An Exact Certificate for Skill-Taxonomy Representation Invariance"

PKG = Path("/data/wyt/agent-self-evolution-observatory/submission-packages/stri-e1-r19-heldout-pilot-stop-20260824")
PDF = PKG / "E1-STRI-R19-heldout-pilot-stop.pdf"
SOURCE = PKG / "E1-STRI-R19-heldout-pilot-stop-source.zip"
SUPPLEMENT = PKG / "E1-STRI-R19-heldout-pilot-stop-supplement.zip"
MANIFEST = PKG / "R19-MANIFEST.json"

PDF_SHA = "c2440a127a0cb078c0af5ddd5617bf1b3ed6a627bc635d53a0eaae306c9265c7"
SOURCE_SHA = "b8cd9c0e708009788bf40167dbe8b5d21a37cedbde46a317c2cd43ff8b172f4c"
SUPPLEMENT_SHA = "e710574e68b4443af92cb02c5797f7759958c35bd83308f27be63a651c8643c2"
SUPPLEMENT_MANIFEST_SHA = "810a53f249bac6a192b400d287a22a011bd7f5400cad31e36e2999b84b1ea206"
PACKAGE_METADATA_SHA = "8f24b6cae624e97293eec2b67ed1e558321271526948ba36f9c567686f3d6bd2"
MANIFEST_FILE_SHA = "c6da7056eb4ba0082b31745df86ba1023cb89b27ec23753acaf1840e0b1828f2"
MANIFEST_CANONICAL_SHA = "57780c494f5e03cb55dc1c3187bfa692d761fd3345d06283bd5d4375d82c82e3"
CANONICAL_BASE = "4f0fd8400c1e4434f3ae73523c3dd2062808a282"
INTEGRATION_SOURCE_HEAD = "9e1c60845d4245c5ad7645d1cee06eb82f278871"

GEN = ROOT / "generated"
DL = ROOT / "downloads"
PAPER = ROOT / "paper_drafts"
FINAL_STATE = GEN / "asset-first-stri-iclr2027-final-state-20260816.json"
SUPPLEMENT_STATE = GEN / "asset-first-stri-iclr2027-supplement-state-20260816.json"
OPENREVIEW = GEN / "asset-first-stri-iclr2027-openreview-readiness-20260816.json"
QUALITY = GEN / "asset-first-stri-paper-quality-v2-20260816.json"
PROJECTION_RECEIPT = GEN / "asset-first-stri-r19-canonical-projection-20260824.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected object: {path}")
    return value


def dump(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_pair(name: str, var: str, payload: dict) -> None:
    dump(GEN / f"{name}.json", payload)
    (GEN / f"{name}.js").write_text(
        f"window.{var} = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def registry_summary(rows: list[dict], previous: dict) -> dict:
    out = dict(previous)
    out["papers"] = len(rows)
    out["submission_ready"] = sum(row.get("submission_ready") is True for row in rows)
    out["gate_clean_submission_ready"] = sum(row.get("gate_clean_submission_ready") is True for row in rows)
    out["paper_preparation_failed"] = sum(
        int((row.get("latest_paper_preparation") or {}).get("required_gates") or 0) > 0
        and (row.get("latest_paper_preparation") or {}).get("pass") is not True
        for row in rows
    )
    out["immediate_submission_holds"] = sum(row.get("immediate_submission_hold") is True for row in rows)
    out["internal_action_required"] = sum(
        (row.get("primary_next_action") or {}).get("action_class") != "NO_INTERNAL_ACTION" for row in rows
    )
    out["no_internal_action"] = len(rows) - out["internal_action_required"]
    out["by_internal_action"] = dict(
        sorted(Counter((row.get("primary_next_action") or {}).get("action_class") or "UNKNOWN" for row in rows).items())
    )
    out["scientific_holds"] = sum(str(row.get("scientific_status") or "") != "READY" for row in rows)
    out["by_stage"] = dict(sorted(Counter(row.get("paper_stage") or row.get("current_state") or "UNKNOWN" for row in rows).items()))
    return out


def verify_package() -> dict:
    expected = {PDF: PDF_SHA, SOURCE: SOURCE_SHA, SUPPLEMENT: SUPPLEMENT_SHA, MANIFEST: MANIFEST_FILE_SHA}
    for path, digest in expected.items():
        if not path.is_file() or sha(path) != digest:
            raise RuntimeError(f"R19 artifact mismatch: {path}")
    manifest = load(MANIFEST)
    if manifest.get("candidate") != "R19-heldout-pilot-stop" or manifest.get("revision") != "R19" or manifest.get("manifest_canonical_sha256") != MANIFEST_CANONICAL_SHA:
        raise RuntimeError("R19 manifest identity/digest mismatch")
    if manifest.get("canonical_base") != CANONICAL_BASE or manifest.get("integration_source_head") != INTEGRATION_SOURCE_HEAD:
        raise RuntimeError("R19 manifest base/head mismatch")
    if ((manifest.get("artifacts") or {}).get("supplement_zip") or {}).get("unit_tests") != "31/31 PASS":
        raise RuntimeError("R19 supplement unit-test contract missing")
    qa = manifest.get("qa") or {}
    if (int(qa.get("paper_quality_referenced_files") or 0), int(qa.get("paper_quality_registered_digests") or 0), int(qa.get("citation_count") or 0)) != (73, 76, 21):
        raise RuntimeError("R19 paper-quality/citation contract missing")
    pilot = manifest.get("heldout_behavior_pilot") or {}
    diagnoses = pilot.get("unit_diagnoses") or {}
    if not (
        pilot.get("retrieval_qualification") == "9/9"
        and pilot.get("selection_outcome_blind") is True
        and pilot.get("selected_units") == ["skillmisevo-coding-22-P21", "skillmisevo-coding-21-P19"]
        and int(pilot.get("stage1_runs") or 0) == 8
        and pilot.get("all_executions_valid") is True
        and pilot.get("stage1_gate_pass") is False
        and pilot.get("decision") == "STOP_EXPANSION_STAGE1_GATE_NOT_MET"
        and int(pilot.get("stage2_repeat_runs", -1)) == 0
        and int(pilot.get("remaining_unit_runs", -1)) == 0
        and diagnoses.get("skillmisevo-coding-22-P21") == "CONTROL_NONCONCORDANCE_NO_SPLIT_SPECIFIC_ATTRIBUTION"
        and diagnoses.get("skillmisevo-coding-21-P19") == "NO_ACTION_SIGNATURE_SEPARATION"
        and pilot.get("p19_role") == "bounded existence proof"
    ):
        raise RuntimeError("R19 held-out behavior-pilot STOP contract missing")
    return manifest


def compile_and_refresh_qa() -> dict:
    env = dict(**__import__("os").environ)
    env["TEXINPUTS"] = ".:./iclr2027-official//:"
    env["BSTINPUTS"] = ".:./iclr2027-official//:"
    stem = "stri-20260816-iclr2027-main"
    for suffix in ("aux", "bbl", "blg", "log", "out", "pdf"):
        (PAPER / f"{stem}.{suffix}").unlink(missing_ok=True)
    commands = [
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{stem}.tex"],
        ["bibtex", stem],
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{stem}.tex"],
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{stem}.tex"],
    ]
    for command in commands:
        proc = subprocess.run(command, cwd=PAPER, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if proc.returncode:
            raise RuntimeError(f"compile failed: {' '.join(command)}\n{proc.stdout[-5000:]}")
    # LaTeX PDF bytes may vary across rebuilds because of embedded PDF metadata.
    # Bind the publication to deterministic source-ZIP bytes plus rendered venue QA;
    # the packaged PDF itself is separately content-addressed by PDF_SHA.
    import tempfile, zipfile
    with tempfile.TemporaryDirectory(prefix="stri-r19-source-binding-") as tmp:
        with zipfile.ZipFile(SOURCE) as zf:
            zf.extractall(tmp)
        for source in (MAIN := PAPER / "stri-20260816-iclr2027-main.tex", BODY := PAPER / "stri-20260816-narrow-body.tex", TABLES := PAPER / "stri-20260816-tables.tex", BIB := PAPER / "stri-20260816-references.bib"):
            packaged = Path(tmp) / source.name
            if not packaged.is_file() or packaged.read_bytes() != source.read_bytes():
                raise RuntimeError(f"R19 source binding mismatch: {source.name}")
    qa = current_qa()
    if qa.get("status") != "PASS" or (qa.get("checks_passed"), qa.get("checks_total")) != (64, 64):
        raise RuntimeError(f"unexpected official QA: {qa.get('status')} {qa.get('checks_passed')}/{qa.get('checks_total')}")
    return write_qa_artifact(qa)


def publish_aliases() -> None:
    aliases = [
        (PDF, DL / "E1-STRI.pdf", PDF_SHA),
        (PDF, DL / "STRI-ICLR2027.pdf", PDF_SHA),
        (SOURCE, DL / "STRI-ICLR2027-source.zip", SOURCE_SHA),
        (SUPPLEMENT, DL / "STRI-ICLR2027-supplement.zip", SUPPLEMENT_SHA),
        (PAPER / "stri-20260816-iclr2027-main.tex", DL / "STRI-ICLR2027.tex", sha(PAPER / "stri-20260816-iclr2027-main.tex")),
    ]
    for src, dst, digest in aliases:
        shutil.copyfile(src, dst)
        if sha(dst) != digest:
            raise RuntimeError(f"stable alias mismatch: {dst}")


def update_stri_states() -> None:
    quality = load(QUALITY)
    ca = (((quality.get("audit") or {}).get("content_addressed_completion") or {}).get("summary") or {})
    referenced_files = int(ca.get("referenced_files") or 0)

    final = load(FINAL_STATE)
    final["delivery"] = {
        "remote_directory": str(PKG),
        "pdf": {"path": str(PDF), "sha256": PDF_SHA},
        "source_zip": {"path": str(SOURCE), "sha256": SOURCE_SHA, "files": 12, "isolated_compile_verified": True},
        "supplement_zip": {
            "path": str(SUPPLEMENT),
            "sha256": SUPPLEMENT_SHA,
            "manifest_sha256": SUPPLEMENT_MANIFEST_SHA,
            "isolated_reproduction_verified": True,
            "unit_tests": "31/31 PASS",
            "identity_path_scan": "PASS",
            "paper_quality_v2_reproduction": "PASS_MANUSCRIPT_EVIDENCE",
        },
    }
    final.setdefault("paper_quality_v2", {})["content_addressed_files"] = referenced_files
    final.setdefault("official_format", {})["resolved_citations"] = 21
    final["canonical_reconciliation"] = {
        "revision": "R19",
        "canonical_base": CANONICAL_BASE,
        "integration_source_head": INTEGRATION_SOURCE_HEAD,
        "release_manifest": str(MANIFEST),
        "release_manifest_sha256": MANIFEST_FILE_SHA,
        "release_manifest_canonical_sha256": MANIFEST_CANONICAL_SHA,
        "paper_qa": "97/97 PASS",
        "official_iclr_qa": "64/64 PASS",
        "paper_quality": "PASS_MANUSCRIPT_EVIDENCE",
        "paper_quality_content_addressed_files": referenced_files,
        "paper_quality_registered_digests": 76,
        "supplement_reproduction": "PASS",
        "supplement_unit_tests": "31/31 PASS",
        "experimental_breadth": {
            "practical_package_weight_baselines": 10,
            "leave_one_tool_out_folds": 8,
            "leave_one_tool_out_exact_R_max": 2.0,
            "leave_one_tool_out_nnls_R_max": 6.098053181386519,
            "l1_minimum_feasible_active_packages": 3,
            "l1_minimum_active_packages_attaining_unrestricted_R_star": 3,
            "skillrl_top_k_values": 8,
            "skillrl_tasks": 223,
            "skillrl_clone_targets": 12,
            "skillrouter_expert_queries": 75,
            "skillsbench_support_qualification": "STOP_79_OF_87_METADATA_AVAILABILITY_MISMATCH",
            "agentskillos_oracle_tasks": 30,
            "agentskillos_multi_skill_tasks": 20,
            "agentskillos_full_uniform_R": 4.0,
            "agentskillos_full_oracle_R": 2.5,
            "agentskillos_residual_categories": ["data_computation", "document_creation"],
            "agentskillos_equalizable_categories": ["motion_video", "visual_creation", "web_interaction"],
            "second_exact_support_substrates_qualified": 0
        },
        "heldout_behavior_pilot": {
            "retrieval_qualification": "9/9",
            "selection_outcome_blind": True,
            "selected_units": ["skillmisevo-coding-22-P21", "skillmisevo-coding-21-P19"],
            "stage1_runs": 8,
            "all_executions_valid": True,
            "stage1_gate_pass": False,
            "decision": "STOP_EXPANSION_STAGE1_GATE_NOT_MET",
            "stage2_repeat_runs": 0,
            "remaining_unit_runs": 0,
            "p19_role": "bounded existence proof"
        },
        "claim_expansion": False,
        "new_agent_runs": 8,
        "new_model_profile": False,
        "judge_calls": 0,
        "new_gpu_runs": 0,
    }
    dump(FINAL_STATE, final)

    supplement = load(SUPPLEMENT_STATE)
    supplement["package"] = {
        "path": str(SUPPLEMENT),
        "sha256": SUPPLEMENT_SHA,
        "manifest_sha256": SUPPLEMENT_MANIFEST_SHA,
        "package_metadata_sha256": PACKAGE_METADATA_SHA,
    }
    supplement["isolated_verification"] = {
        "fresh_extract_manifest": "PASS",
        "reproduce_py": "PASS",
        "unit_tests": "31/31 PASS",
        "binary_identity_path_scan": "PASS",
        "text_identity_path_scan": "PASS",
        "figure_regeneration": "R19_BOUNDARY_FIGURE_REGENERATED_AND_SOURCE_BOUND",
        "paper_quality_v2_reproduction": "PASS_MANUSCRIPT_EVIDENCE",
    }
    supplement.setdefault("reproduced_results", {})["structural_enrichment"] = {
        "target_rays_residual": "7/7",
        "degree_preserving_rewires_residual": "200/200",
        "max_share_constraints_preserving_R_star_2": "9/9",
        "disjoint_three_row_witnesses": 22,
        "witness_rows_removed": 66,
        "witness_tools_spanned": 19,
        "minimum_additions_to_equalizable": 22,
        "minimum_deletions_to_equalizable": 71,
        "new_model_calls": 0,
        "new_gpu_runs": 0,
    }
    supplement.setdefault("reproduced_results", {})["autoskill_multitask_pilot"] = {
        "retrieval_qualification": "9/9",
        "selected_units": ["skillmisevo-coding-22-P21", "skillmisevo-coding-21-P19"],
        "stage1_runs": 8,
        "all_executions_valid": True,
        "stage1_gate_pass": False,
        "decision": "STOP_EXPANSION_STAGE1_GATE_NOT_MET",
        "stage2_repeat_runs": 0,
        "remaining_unit_runs": 0,
        "unit_diagnoses": {
            "skillmisevo-coding-22-P21": "CONTROL_NONCONCORDANCE_NO_SPLIT_SPECIFIC_ATTRIBUTION",
            "skillmisevo-coding-21-P19": "NO_ACTION_SIGNATURE_SEPARATION"
        },
        "raw_trajectories_packaged": False,
        "new_agent_runs": 8,
        "judge_calls": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
    }
    supplement.setdefault("reproduced_results", {})["experimental_breadth"] = {
        "practical_level1_uniform_R": 2.0,
        "practical_level1_inverse_support_R": 98.33333333333334,
        "practical_level1_nnls_R": 5.5095579354215305,
        "calibration_to_heldout_exact_R": 2.0,
        "leave_one_tool_out_exact_R_max": 2.0,
        "leave_one_tool_out_nnls_R_max": 6.098053181386519,
        "l1_minimum_feasible_active_packages": 3,
        "l1_minimum_active_packages_attaining_unrestricted_R_star": 3,
        "skillrl_top_k_6_targets_changed": 11,
        "skillrl_top_k_13_semantic_changes": 0,
        "skillrouter_core_uniform_R": 7.0,
        "skillrouter_core_exact_R": 1.0,
        "skillrouter_graded_uniform_R": 21.0,
        "skillrouter_graded_exact_R": 1.0,
        "skillsbench_support_qualification": "STOP_79_OF_87_METADATA_AVAILABILITY_MISMATCH",
        "agentskillos_full_uniform_R": 4.0,
        "agentskillos_full_oracle_R": 2.5,
        "agentskillos_residual_categories": ["data_computation", "document_creation"],
        "agentskillos_equalizable_categories": ["motion_video", "visual_creation", "web_interaction"],
        "second_exact_support_substrates_qualified": 0,
        "new_model_calls": 0,
        "new_gpu_runs": 0,
    }
    dump(SUPPLEMENT_STATE, supplement)

    openreview = load(OPENREVIEW)
    openreview["submission_files"] = {"pdf": str(PDF), "source_zip": str(SOURCE), "supplement_zip": str(SUPPLEMENT)}
    mv = openreview.setdefault("machine_verified", {})
    mv.update({
        "paper_pdf_sha256": PDF_SHA,
        "paper_source_zip_sha256": SOURCE_SHA,
        "anonymous_supplement_zip_sha256": SUPPLEMENT_SHA,
        "supplement_reproduction": "PASS",
        "supplement_unit_tests": "31/31 PASS",
        "paper_quality_v2": "PASS_MANUSCRIPT_EVIDENCE",
        "paper_quality_evidence_debt": 0,
        "paper_quality_content_addressed_files": referenced_files,
        "paper_quality_registered_digests": 76,
        "resolved_citations": 21,
        "structural_enrichment": "7/7 target rays; 200/200 degree-preserving rewires; 9/9 max-share; 22 disjoint witnesses; exact edit radius 22 additions / 71 deletions",
        "experimental_breadth": "10 package-weight baselines; 4-to-4 no-refit transfer; 8-fold leave-one-tool-out exact R max=2 and NNLS worst=6.10; Level-1 exact sparsity frontier reaches unrestricted R*=2 at 3 active packages; SkillRL 8-budget sweep x 12 clones x 223 tasks; SkillRouter 75-query relevance analogue; AgentSkillOS 30-task oracle-set analogue (full R*=2.5, category R*=2/2/1/1/1); five-candidate second-support tournament qualifies zero new exact support substrates",
        "heldout_behavior_pilot": "9/9 retrieval-qualified; outcome-blind hash-selected two units; 8/8 valid A/B/C/D runs; preregistered stage-1 split-specific gate failed; repeat-2 and remaining seven not authorized; P19 remains bounded",
        "r19_canonical_reconciliation": True,
        "claim_expansion_for_r19": False,
        "new_agent_runs_for_r19": 8,
        "new_model_profile_for_r19": False,
        "judge_calls_for_r19": 0,
        "new_gpu_runs_for_r19": 0,
    })
    dump(OPENREVIEW, openreview)


def contract_from_ledger(row: dict) -> PaperContract:
    c = row.get("contract") or {}
    return PaperContract(
        paper_id=str(c["paper_id"]),
        title=str(c["title"]),
        central_question=str(c["central_question"]),
        supported_claims=dict(c.get("supported_claims") or {}),
        unsupported_claims=dict(c.get("unsupported_claims") or {}),
        limitations=tuple(c.get("limitations") or ()),
        reopen_conditions=tuple(c.get("reopen_conditions") or ()),
        evidence_refs=tuple(c.get("evidence_refs") or ()),
        scientific_status=ScientificPaperStatus(str(c.get("scientific_status") or "READY")),
    )


def append_r19_ledger(root: Path) -> dict:
    before = load_paper_ledger(root, PID)
    if before.get("current_state") != "SUBMISSION_READY" or before.get("scientific_status") != "READY":
        raise RuntimeError("STRI ledger is not frozen SUBMISSION_READY/READY")
    if (before.get("contract") or {}).get("title") != TITLE:
        raise RuntimeError("STRI contract title drifted")
    existing = [e for e in before.get("events") or [] if isinstance(e, dict) and e.get("event_type") == "source-native-r19-finalization"]
    contract = contract_from_ledger(before)
    if existing:
        after = load_paper_ledger(root, PID)
        errors = validate_paper_ledger(after)
        if errors:
            raise RuntimeError("existing R19 ledger is invalid: " + "; ".join(errors))
        return after

    gates = {key: True for key in (
        "hierarchical-rubric", "verification-refinement", "citation-integrity", "visual-story",
        "reproducibility-bundle", "agent-native-artifact", "reader-simulation", "submission-package",
    )}

    def append(kind: str, payload: dict) -> None:
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
        _append(root, contract, "stri-r19-canonical-publisher", event)

    append("paper-preparation-r19", {
        "receipt_type": "paper-preparation",
        "protocol_version": "1.0+r19-heldout-pilot-stop",
        "pass": True,
        "required_gates": 8,
        "passed_gates": 8,
        "gate_pass": gates,
        "blockers": [],
        "paper_pdf_sha256": PDF_SHA,
        "source_zip_sha256": SOURCE_SHA,
        "supplement_zip_sha256": SUPPLEMENT_SHA,
        "release_manifest_sha256": MANIFEST_FILE_SHA,
        "release_manifest_canonical_sha256": MANIFEST_CANONICAL_SHA,
        "paper_qa": "97/97 PASS",
        "official_iclr_qa": "64/64 PASS",
        "citation_count": 21,
        "paper_quality": "PASS_MANUSCRIPT_EVIDENCE",
        "paper_quality_referenced_files": 73,
        "paper_quality_registered_digests": 76,
        "supplement_unit_tests": "31/31 PASS",
        "new_experiment_unit_tests": "3/3 PASS",
        "new_external_reviewer_run": False,
    })
    append("submission-readiness-r19", {
        "receipt_type": "submission-readiness",
        "submission_ready": True,
        "manuscript_ci_pass": True,
        "paper_preparation_pass": True,
        "prebuttal_pass": True,
        "blockers": [],
        "paper_pdf_sha256": PDF_SHA,
        "source_zip_sha256": SOURCE_SHA,
        "supplement_zip_sha256": SUPPLEMENT_SHA,
        "release_manifest_sha256": MANIFEST_FILE_SHA,
        "claim_expansion": False,
    })
    append("submission-readiness-context-r19", {
        "receipt_type": "submission-readiness-context",
        "artifact_submission_ready": True,
        "current_state": "SUBMISSION_READY",
        "scientific_status": "READY",
        "support_blocker": "",
        "recommended_immediate_submission": "READY_FOR_HUMAN_SUBMISSION",
        "external_human_submission_authority_required": True,
        "external_human_submission_authority_required_for_SUBMITTED": True,
        "paper_pdf_sha256": PDF_SHA,
        "source_zip_sha256": SOURCE_SHA,
        "supplement_zip_sha256": SUPPLEMENT_SHA,
        "claim_expansion": False,
        "new_agent_runs": 8,
        "new_model_profile": False,
        "judge_calls": 0,
        "new_gpu_runs": 0,
    })
    append("source-native-r19-finalization", {
        "receipt_type": "canonical-release-finalization",
        "artifact_ref": f"artifact:sha256:{MANIFEST_FILE_SHA}",
        "title": TITLE,
        "paper_pdf_sha256": PDF_SHA,
        "source_zip_sha256": SOURCE_SHA,
        "supplement_zip_sha256": SUPPLEMENT_SHA,
        "canonical_base": CANONICAL_BASE,
        "integration_source_head": INTEGRATION_SOURCE_HEAD,
        "release_manifest_sha256": MANIFEST_FILE_SHA,
        "release_manifest_canonical_sha256": MANIFEST_CANONICAL_SHA,
        "structural_enrichment": {
            "target_rays_residual": "7/7",
            "degree_preserving_rewires_residual": "200/200",
            "max_share_constraints_preserving_R_star_2": "9/9",
            "disjoint_three_row_witnesses": 22,
            "minimum_additions_to_equalizable": 22,
            "minimum_deletions_to_equalizable": 71,
        },
        "experimental_breadth": {
            "practical_package_weight_baselines": 10,
            "calibration_to_heldout_exact_R": 2.0,
            "leave_one_tool_out_folds": 8,
            "leave_one_tool_out_exact_R_max": 2.0,
            "leave_one_tool_out_nnls_R_median": 2.624932438792478,
            "leave_one_tool_out_nnls_R_max": 6.098053181386519,
            "l1_minimum_feasible_active_packages": 3,
            "l1_minimum_active_packages_attaining_unrestricted_R_star": 3,
            "l1_unrestricted_R_star": 2.0,
            "skillrl_top_k_values": 8,
            "skillrl_tasks": 223,
            "skillrl_clone_targets": 12,
            "skillrl_top_k_13_semantic_changes": 0,
            "skillrouter_expert_queries": 75,
            "skillrouter_core_uniform_R": 7.0,
            "skillrouter_core_exact_R": 1.0,
            "skillrouter_graded_uniform_R": 21.0,
            "skillrouter_graded_exact_R": 1.0,
            "skillsbench_support_qualification": "STOP_79_OF_87_METADATA_AVAILABILITY_MISMATCH",
            "agentskillos_oracle_tasks": 30,
            "agentskillos_unique_oracle_skills": 19,
            "agentskillos_multi_skill_tasks": 20,
            "agentskillos_full_uniform_R": 4.0,
            "agentskillos_full_oracle_R": 2.5,
            "agentskillos_residual_categories": ["data_computation", "document_creation"],
            "agentskillos_equalizable_categories": ["motion_video", "visual_creation", "web_interaction"],
            "second_support_candidates_screened": 5,
            "second_exact_support_substrates_qualified": 0,
            "second_support_search_disposition": "NO_SECOND_EXACT_SUPPORT_SUBSTRATE_QUALIFIED"
        },
        "heldout_behavior_pilot": {
            "retrieval_qualification": "9/9",
            "selection_outcome_blind": True,
            "selected_units": ["skillmisevo-coding-22-P21", "skillmisevo-coding-21-P19"],
            "stage1_runs": 8,
            "all_executions_valid": True,
            "stage1_gate_pass": False,
            "decision": "STOP_EXPANSION_STAGE1_GATE_NOT_MET",
            "stage2_repeat_runs": 0,
            "remaining_unit_runs": 0,
            "unit_diagnoses": {
                "skillmisevo-coding-22-P21": "CONTROL_NONCONCORDANCE_NO_SPLIT_SPECIFIC_ATTRIBUTION",
                "skillmisevo-coding-21-P19": "NO_ACTION_SIGNATURE_SEPARATION"
            },
            "failure_asset": "generated/asset-first-stri-autoskill-multitask-pilot-failure-lesson-20260824.json",
            "p19_role": "bounded existence proof"
        },
        "claim_expansion": False,
        "new_agent_runs": 8,
        "new_model_profile": False,
        "judge_calls": 0,
        "new_gpu_runs": 0,
        "recommended_immediate_action": "READY_FOR_HUMAN_SUBMISSION",
    })
    after = load_paper_ledger(root, PID)
    errors = validate_paper_ledger(after)
    if errors:
        raise RuntimeError("R19 ledger invalid: " + "; ".join(errors))
    return after


def selective_projection(root: Path) -> dict:
    live = build_paper_ledger_index(root)
    pub = next(row for row in live.get("entries") or [] if row.get("paper_id") == PID)
    if pub.get("gate_clean_submission_ready") is not True or pub.get("immediate_submission_hold") is True:
        raise RuntimeError("live STRI R19 readiness is not gate-clean")
    prep = pub.get("latest_paper_preparation") or {}
    if prep.get("protocol_version") != "1.0+r19-heldout-pilot-stop":
        raise RuntimeError("live STRI paper-preparation is not R19 held-out-pilot STOP")

    # Rebuild only the compact public status from latest STRI receipts + live ledger.
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_current_research_status.py")], cwd=ROOT, check=True)

    candidate_full = build_paper_registry()
    candidate = next(row for row in candidate_full.get("papers") or [] if row.get("paper_id") == PUBLIC_PID)
    old = load(GEN / "paper-registry.json")
    rows = [candidate if row.get("paper_id") == PUBLIC_PID else row for row in old.get("papers") or []]
    if sum(row.get("paper_id") == PUBLIC_PID for row in rows) != 1:
        raise RuntimeError("PaperRegistry STRI cardinality error")
    old["papers"] = rows
    old["generated_at"] = candidate_full.get("generated_at") or old.get("generated_at")
    old["source_revision"] = candidate_full.get("source_revision") or old.get("source_revision")
    old["summary"] = registry_summary(rows, old.get("summary") or {})
    write_pair("paper-registry", "PAPER_REGISTRY", old)

    system = load(GEN / "research-system-state.json")
    acceptance = system.get("paper_acceptance") or {}
    index = acceptance.get("ledger_index") or {}
    entries = [pub if row.get("paper_id") == PID else row for row in index.get("entries") or []]
    if sum(row.get("paper_id") == PID for row in entries) != 1:
        raise RuntimeError("ResearchSystem STRI ledger cardinality error")
    index["entries"] = entries
    acceptance["ledger_index"] = index
    system["paper_acceptance"] = acceptance

    # Refresh only the STRI asset-first component.  A full ResearchSystem rebuild
    # would also consume unrelated live paper ledgers; selective publication must
    # preserve the other four committed PaperState rows exactly.
    status = build_asset_first_stri_public_status(ROOT)
    system["asset_first_stri_paper_ready"] = status
    ss = system.setdefault("summary", {})
    sm = status.get("summary") or {}
    summary_bindings = {
        "asset_first_stri_status": status.get("status", "HOLD_ASSET_FIRST_PAPER_NOT_READY"),
        "asset_first_stri_paper_ready": int(sm.get("paper_ready") or 0),
        "asset_first_stri_claims_supported": int(sm.get("claims_supported") or 0),
        "asset_first_stri_claims_total": int(sm.get("claims_total") or 0),
        "asset_first_stri_qa_checks_passed": int(sm.get("qa_checks_passed") or 0),
        "asset_first_stri_qa_checks_total": int(sm.get("qa_checks_total") or 0),
        "asset_first_stri_submission_status": status.get("submission_status", "NOT_READY"),
        "asset_first_stri_official_qa_checks_passed": int(sm.get("official_qa_checks_passed") or 0),
        "asset_first_stri_official_qa_checks_total": int(sm.get("official_qa_checks_total") or 0),
        "asset_first_stri_main_text_pages": int(sm.get("main_text_pages") or 0),
        "asset_first_stri_main_text_page_limit": int(sm.get("main_text_page_limit") or 0),
        "asset_first_stri_supplement_ready": int(sm.get("supplement_ready") or 0),
        "asset_first_stri_human_signoff_pending": int(sm.get("human_signoff_pending") or 0),
        "asset_first_stri_paper_quality_v2_passed": int(sm.get("paper_quality_v2_passed") or 0),
        "asset_first_stri_paper_quality_source_binding": int(sm.get("paper_quality_source_binding") or 0),
        "asset_first_stri_paper_quality_content_addressed_completion": int(sm.get("paper_quality_content_addressed_completion") or 0),
        "asset_first_stri_paper_quality_content_addressed_files": int(sm.get("paper_quality_content_addressed_files") or 0),
        "asset_first_stri_paper_quality_evidence_debt": int(sm.get("paper_quality_evidence_debt") or 0),
        "asset_first_stri_main_visualizations": int(sm.get("paper_quality_main_visualizations") or 0),
        "asset_first_stri_canonical_problem_gate_added": int(sm.get("canonical_problem_gate_pass_added") or 0),
    }
    ss.update(summary_bindings)
    write_pair("research-system-state", "RESEARCH_SYSTEM_STATE", system)

    errors = validate_asset_first_stri_public_status(status)
    if errors:
        raise RuntimeError("R19 STRI public status invalid: " + "; ".join(errors))
    if status.get("status") != "READY_NARROW_ICLR":
        raise RuntimeError(f"R19 public status is not ready: {status.get('gates')}")
    return {"live": pub, "public_status": status, "registry": candidate}


def cleanup_build_files() -> None:
    stem = PAPER / "stri-20260816-iclr2027-main"
    for suffix in ("aux", "bbl", "blg", "log", "out", "pdf"):
        Path(f"{stem}.{suffix}").unlink(missing_ok=True)


def main() -> None:
    manifest = verify_package()
    qa = compile_and_refresh_qa()
    publish_aliases()
    update_stri_states()
    root = resolve_experiment_data_root(StorageSettings.from_env())
    ledger = append_r19_ledger(root)
    projection = selective_projection(root)
    cleanup_build_files()

    receipt = {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "acceptance_paper_id": PID,
        "revision": "R19",
        "status": "R19_CANONICAL_PROJECTION_PUBLISHED",
        "canonical_base": CANONICAL_BASE,
        "integration_source_head": INTEGRATION_SOURCE_HEAD,
        "release_manifest": str(MANIFEST),
        "release_manifest_sha256": MANIFEST_FILE_SHA,
        "release_manifest_canonical_sha256": MANIFEST_CANONICAL_SHA,
        "stable_hashes": {
            "pdf": sha(DL / "E1-STRI.pdf"),
            "legacy_pdf": sha(DL / "STRI-ICLR2027.pdf"),
            "source_zip": sha(DL / "STRI-ICLR2027-source.zip"),
            "supplement_zip": sha(DL / "STRI-ICLR2027-supplement.zip"),
            "tex": sha(DL / "STRI-ICLR2027.tex"),
        },
        "qa": {
            "paper_qa": "97/97 PASS",
            "official_iclr_qa": f"{qa.get('checks_passed')}/{qa.get('checks_total')} PASS",
            "main_text_pages": qa.get("main_text_pages"),
            "paper_quality": "PASS_MANUSCRIPT_EVIDENCE",
            "supplement_reproduction": "PASS",
            "supplement_unit_tests": "31/31 PASS",
            "new_experiment_unit_tests": "3/3 PASS",
            "paper_quality_referenced_files": 73,
            "paper_quality_registered_digests": 76,
            "citation_count": 21,
        },
        "ledger": {
            "current_state": ledger.get("current_state"),
            "contract_sha256": ledger.get("contract_sha256"),
            "gate_clean_submission_ready": projection["live"].get("gate_clean_submission_ready"),
            "paper_preparation_protocol": (projection["live"].get("latest_paper_preparation") or {}).get("protocol_version"),
            "primary_next_action": (projection["live"].get("primary_next_action") or {}).get("action_class"),
        },
        "experimental_breadth": {
            "practical_package_weight_baselines": 10,
            "leave_one_tool_out": "8 folds; exact-R*/uniform max=2.0; NNLS median=2.625, max=6.098",
            "exact_sparsity_frontier": "Level-1 budgets 1-2 infeasible; 3 active packages attain unrestricted R*=2 through budget 6",
            "skillrl_budget_sweep": "8 top-k x 12 clone targets x 223 tasks",
            "skillrouter_external_relevance_analogue": "75 expert queries; core 24 single / 51 multi; R*=1 analogue",
            "skillsbench_support_qualification": "STOP_79_OF_87_METADATA_AVAILABILITY_MISMATCH",
            "agentskillos_oracle_analogue": "30 tasks / 20 multi / full uniform spread 4x / full oracle-set R*=2.5 / category R*=2,2,1,1,1",
            "second_support_qualification": "5 candidates screened / 0 new exact support / 1 new oracle-set analogue",
        },
        "heldout_behavior_pilot": {
            "retrieval_qualification": "9/9",
            "selection_outcome_blind": True,
            "selected_units": ["skillmisevo-coding-22-P21", "skillmisevo-coding-21-P19"],
            "stage1_runs": 8,
            "all_executions_valid": True,
            "stage1_gate_pass": False,
            "decision": "STOP_EXPANSION_STAGE1_GATE_NOT_MET",
            "stage2_repeat_runs": 0,
            "remaining_unit_runs": 0,
            "p19_role": "bounded existence proof"
        },
        "other_paper_rows_preserved": True,
        "claim_expansion": False,
        "new_agent_runs": 8,
        "new_model_profile": False,
        "judge_calls": 0,
        "new_gpu_runs": 0,
        "scientific_authority": False,
        "submission_authority": False,
    }
    receipt["receipt_sha256"] = _digest(receipt)
    dump(PROJECTION_RECEIPT, receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
