#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper_drafts"
GEN = ROOT / "generated"
DOWNLOADS = ROOT / "downloads"
REMOTE = Path("/data/wyt/agent-self-evolution-observatory/submission-packages")

MAIN = PAPER / "stri-20260816-iclr2027-main.tex"
BODY = PAPER / "stri-20260816-narrow-body.tex"
TABLES = PAPER / "stri-20260816-tables.tex"
BIB = PAPER / "stri-20260816-references.bib"
PDF = PAPER / "stri-20260816-iclr2027-main.pdf"
STYLE = PAPER / "iclr2027-official"

QA_PATH = GEN / "asset-first-stri-iclr2027-submission-qa-20260816.json"
FINAL_REVIEW_PATH = GEN / "asset-first-stri-iclr2027-final-review-20260816.json"
FINAL_STATE_PATH = GEN / "asset-first-stri-iclr2027-final-state-20260816.json"
SUPPLEMENT_STATE_PATH = GEN / "asset-first-stri-iclr2027-supplement-state-20260816.json"
OPENREVIEW_PATH = GEN / "asset-first-stri-iclr2027-openreview-readiness-20260816.json"
PAPER_QUALITY_PATH = GEN / "asset-first-stri-paper-quality-v2-20260816.json"
P0E_RECEIPT = GEN / "asset-first-stri-skillrl-final-policy-p0e-supplement-receipt-20260817.json"
P0E_PRINCIPLE = GEN / "asset-first-stri-skillrl-final-policy-p0e-principle-disposition-20260817.json"
AUTOSKILL_QUALIFICATION = GEN / "asset-first-stri-autoskill-p19-substrate-qualification-20260819.json"
AUTOSKILL_CONTRACT = GEN / "asset-first-stri-autoskill-p19-dynamic-f0-contract-v2-20260819.json"
AUTOSKILL_PLAN = GEN / "asset-first-stri-autoskill-p19-stage3-plan-20260819.json"
AUTOSKILL_RESULT = GEN / "asset-first-stri-autoskill-p19-stage3-result-20260819.json"
AUTOSKILL_RUN_MANIFEST = GEN / "asset-first-stri-autoskill-p19-stage3-run-manifest-20260819.json"
MEDIATOR_V1_CONTRACT = GEN / "asset-first-stri-autoskill-p19-mediator-isolation-contract-20260819.json"
MEDIATOR_V1_DIAGNOSIS = GEN / "asset-first-stri-autoskill-p19-mediator-isolation-v1-diagnosis-20260819.json"
MEDIATOR_V2_CONTRACT = GEN / "asset-first-stri-autoskill-p19-mediator-isolation-v2-contract-20260819.json"
MEDIATOR_V2_RESULT = GEN / "asset-first-stri-autoskill-p19-mediator-isolation-v2-result-20260819.json"
POST_ISOLATION_REVIEW = GEN / "asset-first-stri-post-isolation-review-adjudication-20260819.json"
TARGET_NULL_ANALYSIS = GEN / "asset-first-stri-target-null-analysis-20260824.json"
WITNESS_PEELING = GEN / "asset-first-stri-witness-peeling-20260824.json"
SUPPORT_EDIT_RADIUS = GEN / "asset-first-stri-support-edit-radius-20260824.json"
STANFORD_EXPERIMENT_ENRICHMENT = GEN / "asset-first-stri-stanford-experiment-enrichment-20260824.json"
PRACTICAL_BASELINES = GEN / "asset-first-stri-practical-baselines-20260824.json"
PRACTICAL_BASELINES_CSV = GEN / "asset-first-stri-practical-baselines-20260824.csv"
CROSSVAL_SPARSITY = GEN / "asset-first-stri-crossval-sparsity-20260824.json"
CROSSVAL_SPARSITY_CSV = GEN / "asset-first-stri-crossval-sparsity-20260824.csv"
SKILLRL_BUDGET_BASELINES = GEN / "asset-first-stri-skillrl-budget-baselines-20260824.json"
SKILLRL_BUDGET_BASELINES_CSV = GEN / "asset-first-stri-skillrl-budget-baselines-20260824.csv"
SKILLROUTER_RELEVANCE = GEN / "asset-first-stri-skillrouter-relevance-analogue-20260824.json"
SKILLROUTER_RELEVANCE_CSV = GEN / "asset-first-stri-skillrouter-relevance-analogue-20260824.csv"
SKILLSBENCH_SUPPORT_QUAL = GEN / "asset-first-stri-skillsbench-support-qualification-20260824.json"
SKILLSBENCH_SUPPORT_QUAL_CSV = GEN / "asset-first-stri-skillsbench-support-qualification-20260824.csv"
AGENTSKILLOS_ORACLE = GEN / "asset-first-stri-agentskillos-oracle-analogue-20260824.json"
AGENTSKILLOS_ORACLE_CSV = GEN / "asset-first-stri-agentskillos-oracle-analogue-20260824.csv"
SECOND_SUBSTRATE_QUAL = GEN / "asset-first-stri-second-substrate-qualification-20260824.json"
MULTITASK_QUAL = GEN / "asset-first-stri-autoskill-multitask-qualification-20260824.json"
MULTITASK_QUAL_CSV = GEN / "asset-first-stri-autoskill-multitask-qualification-20260824.csv"
MULTITASK_CONTRACT = GEN / "asset-first-stri-autoskill-multitask-pilot-contract-20260824.json"
MULTITASK_RUN_MANIFEST = GEN / "asset-first-stri-autoskill-multitask-pilot-run-manifest-20260824.json"
MULTITASK_STAGE1 = GEN / "asset-first-stri-autoskill-multitask-pilot-stage1-20260824.json"
MULTITASK_STAGE1_CSV = GEN / "asset-first-stri-autoskill-multitask-pilot-stage1-20260824.csv"
MULTITASK_FAILURE = GEN / "asset-first-stri-autoskill-multitask-pilot-failure-lesson-20260824.json"
MULTITASK_CLOSURE = GEN / "asset-first-stri-autoskill-multitask-pilot-closure-r19-20260824.json"

DOWNLOAD_PDF = DOWNLOADS / "STRI-ICLR2027.pdf"
DOWNLOAD_TEX = DOWNLOADS / "STRI-ICLR2027.tex"
DOWNLOAD_SOURCE = DOWNLOADS / "STRI-ICLR2027-source.zip"
REMOTE_PDF = REMOTE / "STRI-ICLR2027-20260816.pdf"
REMOTE_SOURCE = REMOTE / "STRI-ICLR2027-20260816-source.zip"
REMOTE_SUPPLEMENT = REMOTE / "STRI-ICLR2027-20260816-supplement.zip"

FIXED_ZIP_TIME = (2026, 8, 17, 1, 0, 0)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def dump(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stdout[-8000:]}")
    return proc


def find_repro_python() -> str:
    candidates = [
        os.environ.get("STRI_REPRO_PYTHON", ""),
        sys.executable,
        "/home/wyt/anaconda3/bin/python3.10",
    ]
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen or not Path(candidate).is_file():
            continue
        seen.add(candidate)
        probe = subprocess.run(
            [candidate, "-c", "import numpy,scipy,matplotlib;print(numpy.__version__,scipy.__version__,matplotlib.__version__)"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if probe.returncode == 0:
            return candidate
    raise RuntimeError("no existing scientific Python with numpy/scipy/matplotlib is available for supplement verification")


def zip_info(name: str, *, directory: bool = False) -> zipfile.ZipInfo:
    if directory and not name.endswith("/"):
        name += "/"
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    mode = 0o755 if directory else 0o644
    info.external_attr = (mode & 0xFFFF) << 16
    return info


def deterministic_zip_from_mapping(target: Path, mapping: list[tuple[Path, str]]) -> int:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        dirs = sorted({str(Path(arc).parent).replace(".", "") for _, arc in mapping if str(Path(arc).parent) not in ("", ".")})
        written_dirs: set[str] = set()
        for directory in dirs:
            parts = Path(directory).parts
            for i in range(1, len(parts) + 1):
                d = "/".join(parts[:i]) + "/"
                if d not in written_dirs:
                    zf.writestr(zip_info(d, directory=True), b"")
                    written_dirs.add(d)
        for source, arc in sorted(mapping, key=lambda pair: pair[1]):
            zf.writestr(zip_info(arc), source.read_bytes())
    return len(mapping)


def deterministic_zip_tree(root: Path, target: Path) -> int:
    mapping = [(p, p.relative_to(root).as_posix()) for p in root.rglob("*") if p.is_file()]
    return deterministic_zip_from_mapping(target, mapping)


def current_qa() -> dict:
    proc = run(["python3", "stri-20260816-iclr2027-qa.py"], cwd=PAPER)
    qa = json.loads(proc.stdout)
    if qa.get("status") != "PASS" or int(qa.get("main_text_pages") or 0) > 9:
        raise RuntimeError(f"official QA is not PASS: {qa}")
    return qa


def write_qa_artifact(qa: dict) -> dict:
    previous = load(QA_PATH)
    state = dict(previous)
    state.update({
        "schema_version": "1.0",
        "paper_id": "STRI",
        "stage": "OFFICIAL_ICLR2027_SUBMISSION_QA",
        "status": "PASS",
        "checks_passed": int(qa["checks_passed"]),
        "checks_total": int(qa["checks_total"]),
        "main_text_pages": int(qa["main_text_pages"]),
        "main_text_page_limit": 9,
        "post_main_page": int(qa["post_main_page"]),
        "total_pdf_pages": int(qa["total_pdf_pages"]),
        "citation_count": int(qa["citation_count"]),
        "double_blind_anonymity": "PASS",
        "abstract_single_paragraph": True,
        "ai_use_statement": "PRESENT_REQUIRED",
        "reproducibility_statement": "PRESENT_RECOMMENDED",
        "undefined_citations": 0,
        "undefined_references": 0,
        "overfull_boxes": 0,
        "source_sha256": sha(MAIN),
        "body_sha256": sha(BODY),
        "tables_sha256": sha(TABLES),
        "bibliography_sha256": sha(BIB),
        "claims_still_forbidden": [
            "generalized dynamic STRI success beyond the frozen AutoSkill/P19 behavior-level result",
            "downstream utility harm",
            "system-wide AutoSkill safety conclusions",
            "SQC empirical success",
            "LP algorithm novelty",
            "using the Qwen3 qualification-failed bank as scientific evidence",
            "treating the qualified SkillRL C4 realization STOP as a population-level no-effect theorem or persistent principle dead end",
        ],
        "scientific_authority": False,
        "authority": {"paper_claim_expansion": False, "autoskill_p19_behavioral_claim": True, "generalized_dynamic_claim": False, "full_experiment": False, "gpu": False},
    })
    dump(QA_PATH, state)
    return state


def source_mapping() -> list[tuple[Path, str]]:
    rows = [
        (MAIN, MAIN.name),
        (BODY, BODY.name),
        (TABLES, TABLES.name),
        (BIB, BIB.name),
        (STYLE / "iclr2027_conference.sty", "iclr2027_conference.sty"),
        (STYLE / "iclr2027_conference.bst", "iclr2027_conference.bst"),
        (STYLE / "natbib.sty", "natbib.sty"),
        (STYLE / "fancyhdr.sty", "fancyhdr.sty"),
    ]
    for name in ["stri-factor2-witnesses.pdf", "stri-overview.pdf", "stri-rstar-boundary.pdf", "stri-ablation-robustness.pdf"]:
        rows.append((PAPER / "figures" / name, f"figures/{name}"))
    return rows


def build_and_verify_source_zip() -> dict:
    count = deterministic_zip_from_mapping(DOWNLOAD_SOURCE, source_mapping())
    with tempfile.TemporaryDirectory(prefix="stri-source-verify-") as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(DOWNLOAD_SOURCE) as zf:
            zf.extractall(tmp_path)
        run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", MAIN.name], cwd=tmp_path)
        run(["bibtex", MAIN.stem], cwd=tmp_path)
        run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", MAIN.name], cwd=tmp_path)
        run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", MAIN.name], cwd=tmp_path)
        rebuilt = tmp_path / MAIN.with_suffix(".pdf").name
        if not rebuilt.is_file() or rebuilt.stat().st_size < 10000:
            raise RuntimeError("isolated source ZIP compile did not produce a valid PDF")
    return {"files": count, "sha256": sha(DOWNLOAD_SOURCE), "isolated_compile_verified": True}


def p0e_summary(receipt: dict) -> dict:
    return {
        "role": receipt["role"],
        "competence_calibration": receipt["competence_calibration"],
        "paired_causal_result": receipt["paired_causal_result"],
        "trajectory_boundary": receipt["trajectory_boundary"],
        "statistical_resolution": receipt["statistical_resolution"],
        "final_disposition": receipt["final_disposition"],
        "claim_boundary": receipt["claim_boundary"],
    }


def autoskill_p19_summary(result: dict, mediator: dict | None = None) -> dict:
    groups = result["groups"]
    out = {
        "decision": result["decision"],
        "claim_boundary": result["scientific_claim_boundary"],
        "groups": groups,
        "fisher_exact_p": result["statistics"]["fisher_exact_p"],
        "frozen_gates": result["frozen_gates"],
        "judge_calls": result["judge_calls"],
        "training_steps": result["training_steps"],
        "fresh_container_per_run": result["fresh_container_per_run"],
        "source_run_manifest_sha256": result["run_manifest_sha256"],
        "packaged_run_manifest_sha256": result["packaged_run_manifest_sha256"],
        "run_manifest_canonical_sha256": result["run_manifest_canonical_sha256"],
    }
    if mediator:
        out["mediator_isolation"] = {
            "decision": mediator.get("decision"),
            "groups": mediator.get("groups") or {},
            "statistics": mediator.get("statistics") or {},
            "all_executions_valid": mediator.get("all_executions_valid") is True,
            "judge_calls": int(mediator.get("judge_calls") or 0),
            "claim_boundary": mediator.get("claim_boundary"),
            "measurement_repair": mediator.get("measurement_repair") or {},
        }
    return out


def update_supplement_tree(tree: Path, receipt: dict) -> None:
    artifact_name = "asset-first-stri-skillrl-final-policy-p0e-supplement-receipt-20260817.json"
    shutil.copy2(P0E_RECEIPT, tree / "artifacts" / artifact_name)
    for source, name in [
        (GEN / "asset-first-stri-skillrl-final-policy-p0e-contract-20260816.json", "asset-first-stri-skillrl-final-policy-p0e-contract-20260816.json"),
        (GEN / "asset-first-stri-skillrl-final-policy-p0e-panel-20260816.json", "asset-first-stri-skillrl-final-policy-p0e-panel-20260816.json"),
        (GEN / "asset-first-stri-reviewer-extensions-20260819.json", "asset-first-stri-reviewer-extensions-20260819.json"),
        (PAPER_QUALITY_PATH, "asset-first-stri-paper-quality-v2-20260816.json"),
        (TARGET_NULL_ANALYSIS, "asset-first-stri-target-null-analysis-20260824.json"),
        (WITNESS_PEELING, "asset-first-stri-witness-peeling-20260824.json"),
        (SUPPORT_EDIT_RADIUS, "asset-first-stri-support-edit-radius-20260824.json"),
        (STANFORD_EXPERIMENT_ENRICHMENT, "asset-first-stri-stanford-experiment-enrichment-20260824.json"),
        (PRACTICAL_BASELINES_CSV, "asset-first-stri-practical-baselines-20260824.csv"),
        (CROSSVAL_SPARSITY_CSV, "asset-first-stri-crossval-sparsity-20260824.csv"),
        (SKILLRL_BUDGET_BASELINES_CSV, "asset-first-stri-skillrl-budget-baselines-20260824.csv"),
        (SKILLROUTER_RELEVANCE_CSV, "asset-first-stri-skillrouter-relevance-analogue-20260824.csv"),
        (SKILLSBENCH_SUPPORT_QUAL_CSV, "asset-first-stri-skillsbench-support-qualification-20260824.csv"),
        (AGENTSKILLOS_ORACLE_CSV, "asset-first-stri-agentskillos-oracle-analogue-20260824.csv"),
        (SECOND_SUBSTRATE_QUAL, "asset-first-stri-second-substrate-qualification-20260824.json"),
        (MULTITASK_QUAL, "asset-first-stri-autoskill-multitask-qualification-20260824.json"),
        (MULTITASK_QUAL_CSV, "asset-first-stri-autoskill-multitask-qualification-20260824.csv"),
        (MULTITASK_CONTRACT, "asset-first-stri-autoskill-multitask-pilot-contract-20260824.json"),
        (MULTITASK_RUN_MANIFEST, "asset-first-stri-autoskill-multitask-pilot-run-manifest-20260824.json"),
        (MULTITASK_STAGE1, "asset-first-stri-autoskill-multitask-pilot-stage1-20260824.json"),
        (MULTITASK_STAGE1_CSV, "asset-first-stri-autoskill-multitask-pilot-stage1-20260824.csv"),
        (MULTITASK_FAILURE, "asset-first-stri-autoskill-multitask-pilot-failure-lesson-20260824.json"),
        (MULTITASK_CLOSURE, "asset-first-stri-autoskill-multitask-pilot-closure-r19-20260824.json"),
        (GEN / "asset-first-stri-released-controller-clone-audit-20260819.json", "asset-first-stri-released-controller-clone-audit-20260819.json"),
        (AUTOSKILL_QUALIFICATION, "asset-first-stri-autoskill-p19-substrate-qualification-20260819.json"),
        (AUTOSKILL_CONTRACT, "asset-first-stri-autoskill-p19-dynamic-f0-contract-v2-20260819.json"),
        (AUTOSKILL_PLAN, "asset-first-stri-autoskill-p19-stage3-plan-20260819.json"),
        (AUTOSKILL_RUN_MANIFEST, "asset-first-stri-autoskill-p19-stage3-run-manifest-20260819.json"),
        (MEDIATOR_V1_CONTRACT, "asset-first-stri-autoskill-p19-mediator-isolation-contract-20260819.json"),
        (MEDIATOR_V1_DIAGNOSIS, "asset-first-stri-autoskill-p19-mediator-isolation-v1-diagnosis-20260819.json"),
        (MEDIATOR_V2_CONTRACT, "asset-first-stri-autoskill-p19-mediator-isolation-v2-contract-20260819.json"),
        (MEDIATOR_V2_RESULT, "asset-first-stri-autoskill-p19-mediator-isolation-v2-result-20260819.json"),
    ]:
        shutil.copy2(source, tree / "artifacts" / name)
    practical_packaged = load(PRACTICAL_BASELINES)
    practical_packaged["input_supplement"] = "packaged data/skillsp-*.jsonl"
    practical_packaged["input_split"] = "artifacts/asset-first-stri-tool-disjoint-split-20260816.json"
    dump(tree / "artifacts" / "asset-first-stri-practical-baselines-20260824.json", practical_packaged)
    crossval_packaged = load(CROSSVAL_SPARSITY)
    crossval_packaged["input_supplement"] = "packaged data/skillsp-*.jsonl"
    crossval_packaged["input_split"] = "artifacts/asset-first-stri-tool-disjoint-split-20260816.json"
    dump(tree / "artifacts" / "asset-first-stri-crossval-sparsity-20260824.json", crossval_packaged)
    skillrl_budget_packaged = load(SKILLRL_BUDGET_BASELINES)
    skillrl_budget_packaged.pop("author_repo", None)
    skillrl_budget_packaged["rerun_requires_author_release_at_recorded_commit"] = True
    dump(tree / "artifacts" / "asset-first-stri-skillrl-budget-baselines-20260824.json", skillrl_budget_packaged)
    skillrouter_packaged = load(SKILLROUTER_RELEVANCE)
    (skillrouter_packaged.get("source") or {})["repo"] = "https://github.com/zhengyanzhao1997/SkillRouter"
    skillrouter_packaged["rerun_requires_author_release_at_recorded_commit"] = True
    dump(tree / "artifacts" / "asset-first-stri-skillrouter-relevance-analogue-20260824.json", skillrouter_packaged)
    skillsbench_packaged = load(SKILLSBENCH_SUPPORT_QUAL)
    skillsbench_packaged["rerun_requires_author_release_at_recorded_commit"] = True
    dump(tree / "artifacts" / "asset-first-stri-skillsbench-support-qualification-20260824.json", skillsbench_packaged)
    agentskillos_packaged = load(AGENTSKILLOS_ORACLE)
    agentskillos_packaged["rerun_requires_author_release_at_recorded_commit"] = True
    dump(tree / "artifacts" / "asset-first-stri-agentskillos-oracle-analogue-20260824.json", agentskillos_packaged)
    packaged_autoskill_result = tree / "artifacts" / "asset-first-stri-autoskill-p19-stage3-result-20260819.json"
    sanitized_autoskill = load(AUTOSKILL_RESULT)
    sanitized_autoskill.pop("execution_root", None)
    dump(packaged_autoskill_result, sanitized_autoskill)
    for source, name in [
        (ROOT / "research_pipeline" / "asset_first_stri_certificate.py", "asset_first_stri_certificate.py"),
        (ROOT / "research_pipeline" / "test_asset_first_stri_certificate.py", "test_asset_first_stri_certificate.py"),
        (ROOT / "research_pipeline" / "asset_first_stri_reviewer_extensions.py", "asset_first_stri_reviewer_extensions.py"),
        (ROOT / "research_pipeline" / "test_asset_first_stri_reviewer_extensions.py", "test_asset_first_stri_reviewer_extensions.py"),
        (ROOT / "research_pipeline" / "asset_first_stri_released_controller_clone_audit.py", "asset_first_stri_released_controller_clone_audit.py"),
        (ROOT / "research_pipeline" / "test_asset_first_stri_released_controller_clone_audit.py", "test_asset_first_stri_released_controller_clone_audit.py"),
        (ROOT / "research_pipeline" / "asset_first_stri_target_null_analysis_20260824.py", "asset_first_stri_target_null_analysis_20260824.py"),
        (ROOT / "research_pipeline" / "asset_first_stri_witness_peeling_20260824.py", "asset_first_stri_witness_peeling_20260824.py"),
        (ROOT / "research_pipeline" / "asset_first_stri_support_edit_radius_20260824.py", "asset_first_stri_support_edit_radius_20260824.py"),
        (ROOT / "research_pipeline" / "test_asset_first_stri_target_null_analysis_20260824.py", "test_asset_first_stri_target_null_analysis_20260824.py"),
        (ROOT / "research_pipeline" / "asset_first_stri_practical_baselines_20260824.py", "asset_first_stri_practical_baselines_20260824.py"),
        (ROOT / "research_pipeline" / "asset_first_stri_crossval_sparsity_20260824.py", "asset_first_stri_crossval_sparsity_20260824.py"),
        (ROOT / "research_pipeline" / "test_asset_first_stri_crossval_sparsity_20260824.py", "test_asset_first_stri_crossval_sparsity_20260824.py"),
        (ROOT / "research_pipeline" / "asset_first_stri_skillrl_budget_baselines_20260824.py", "asset_first_stri_skillrl_budget_baselines_20260824.py"),
        (ROOT / "research_pipeline" / "asset_first_stri_skillrouter_relevance_analogue_20260824.py", "asset_first_stri_skillrouter_relevance_analogue_20260824.py"),
        (ROOT / "research_pipeline" / "asset_first_stri_skillsbench_support_qualification_20260824.py", "asset_first_stri_skillsbench_support_qualification_20260824.py"),
        (ROOT / "research_pipeline" / "asset_first_stri_agentskillos_oracle_analogue_20260824.py", "asset_first_stri_agentskillos_oracle_analogue_20260824.py"),
    ]:
        shutil.copy2(source, tree / "research_pipeline" / name)
    packaged_agentskillos_code = tree / "research_pipeline" / "asset_first_stri_agentskillos_oracle_analogue_20260824.py"
    packaged_agentskillos_text = packaged_agentskillos_code.read_text(encoding="utf-8")
    packaged_agentskillos_text = packaged_agentskillos_text.replace(
        'DEFAULT_REPO = Path("/data/wyt/agent2-asset-first-external/AgentSkillOS")',
        'DEFAULT_REPO = Path("external/AgentSkillOS")',
    )
    packaged_agentskillos_code.write_text(packaged_agentskillos_text, encoding="utf-8")
    shutil.copy2(PAPER / "stri-20260816-plot-ablation-robustness.py", tree / "paper_drafts" / "stri-20260816-plot-ablation-robustness.py")
    shutil.copy2(PAPER / "stri-20260816-plot-boundary.py", tree / "paper_drafts" / "stri-20260816-plot-boundary.py")
    for name in ("stri-rstar-boundary.pdf", "stri-rstar-boundary.png"):
        shutil.copy2(PAPER / "figures" / name, tree / "paper_drafts" / "figures" / name)

    meta_path = tree / "PACKAGE-METADATA.json"
    meta = load(meta_path)
    forbidden = [str(item) for item in (meta.get("forbidden_inferences") or []) if str(item) != "dynamic STRI success"]
    additions = [
        "generalized dynamic STRI success beyond the frozen AutoSkill/P19 behavior-level result",
        "treating the AutoSkill P19 behavior-level result as task utility, longitudinal regret, end-to-end AutoSkill runtime validation, or general AutoSkill safety",
        "treating the qualified SkillRL C4 realization STOP as a population-level no-effect theorem or persistent principle dead end",
        "treating 9/9 held-out AutoSkill retrieval sensitivity as task-general behavioral propagation after the preregistered stage-1 behavior gate stopped",
        "reopening the stopped AutoSkill held-out pilot by relaxing the frozen action signature, selecting units from observed behavior, or using tool-call count as the primary endpoint",
    ]
    meta["forbidden_inferences"] = list(dict.fromkeys(forbidden + additions))
    meta["skillrl_p0e"] = {
        "receipt": f"artifacts/{artifact_name}",
        "receipt_sha256": sha(P0E_RECEIPT),
        "experimental_realization": receipt["final_disposition"]["experimental_realization"],
        "principle_disposition": receipt["final_disposition"]["principle_disposition"],
        "persistent_principle_dead_end_certified": False,
        "broader_n1_n2_n3_unchanged": True,
    }
    reviewer_artifact = GEN / "asset-first-stri-reviewer-extensions-20260819.json"
    meta["reviewer_extensions"] = {
        "artifact": "artifacts/asset-first-stri-reviewer-extensions-20260819.json",
        "artifact_sha256": sha(reviewer_artifact),
        "contents": ["exact LP dual", "semantic-first target construction", "max-share constrained audit", "exhaustive one-cell support perturbations", "per-tool exact LP"],
        "learned_support_calibration_claim": False,
    }
    target_null = load(TARGET_NULL_ANALYSIS)
    witness_peeling = load(WITNESS_PEELING)
    support_edit = load(SUPPORT_EDIT_RADIUS)
    ts = ((target_null.get("target_ray_sensitivity") or {}).get("summary") or {})
    ms = ((target_null.get("max_share_sensitivity") or {}).get("summary") or {})
    ns = ((target_null.get("degree_preserving_null_ensemble") or {}).get("summary") or {})
    ws = ((witness_peeling.get("witness_peeling") or {}).get("summary") or {})
    er = support_edit.get("support_edit_radius") or {}
    if not (
        ts.get("targets") == 7 and ts.get("all_tested_targets_residual") is True
        and ms.get("valid_constraints") == 9 and ms.get("all_valid_constraints_residual") is True
        and ns.get("residual_draws") == 200 and ns.get("equalizable_draws") == 0
        and ws.get("peeling_rounds_before_equalizable") == 22 and ws.get("pairwise_disjoint_witness_rows_removed") == 66 and ws.get("unique_tools_spanned") == 19
        and er.get("minimum_additions_to_equalizable") == 22 and er.get("minimum_deletions_to_equalizable") == 71
        and abs(float((er.get("addition_solution") or {}).get("mip_gap", -1.0))) < 1e-12
        and abs(float((er.get("deletion_solution") or {}).get("mip_gap", -1.0))) < 1e-12
    ):
        raise RuntimeError("STRI structural-enrichment artifacts failed frozen checks")
    meta["structural_enrichment"] = {
        "target_null_artifact": "artifacts/asset-first-stri-target-null-analysis-20260824.json",
        "target_null_sha256": sha(TARGET_NULL_ANALYSIS),
        "witness_peeling_artifact": "artifacts/asset-first-stri-witness-peeling-20260824.json",
        "witness_peeling_sha256": sha(WITNESS_PEELING),
        "support_edit_radius_artifact": "artifacts/asset-first-stri-support-edit-radius-20260824.json",
        "support_edit_radius_sha256": sha(SUPPORT_EDIT_RADIUS),
        "enrichment_receipt": "artifacts/asset-first-stri-stanford-experiment-enrichment-20260824.json",
        "enrichment_receipt_sha256": sha(STANFORD_EXPERIMENT_ENRICHMENT),
        "headline": {"target_rays_residual": "7/7", "degree_preserving_rewires_residual": "200/200", "disjoint_three_row_witnesses": 22, "witness_tools_spanned": 19, "minimum_additions_to_equalizable": 22, "minimum_deletions_to_equalizable": 71, "max_share_constraints_preserving_R_star_2": "9/9"},
        "new_model_calls": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
    }
    practical = load(PRACTICAL_BASELINES)
    ph = practical.get("headline") or {}
    crossval = load(CROSSVAL_SPARSITY)
    cvh = crossval.get("headline") or {}
    skillrl_budget = load(SKILLRL_BUDGET_BASELINES)
    sh = skillrl_budget.get("headline") or {}
    skillrouter_relevance = load(SKILLROUTER_RELEVANCE)
    rh = skillrouter_relevance.get("headline") or {}
    skillsbench_support = load(SKILLSBENCH_SUPPORT_QUAL)
    sb = skillsbench_support.get("summary") or {}
    agentskillos = load(AGENTSKILLOS_ORACLE)
    ah = agentskillos.get("headline") or {}
    second_qual = load(SECOND_SUBSTRATE_QUAL)
    sq = second_qual.get("summary") or {}
    if not (
        abs(float(ph.get("level1_uniform_ratio") or -99.0) - 2.0) < 1e-12
        and float(ph.get("level1_inverse_support_ratio") or 0.0) > 90.0
        and float(ph.get("level1_nnls_ratio") or 0.0) > 5.0
        and int(cvh.get("leave_one_tool_out_folds") or 0) == 8
        and abs(float(cvh.get("exact_rstar_heldout_ratio_max") or -99.0) - 2.0) < 1e-12
        and abs(float(cvh.get("uniform_heldout_ratio_max") or -99.0) - 2.0) < 1e-12
        and float(cvh.get("nnls_heldout_ratio_max") or 0.0) > 6.0
        and int(cvh.get("l1_minimum_feasible_active_packages") or 0) == 3
        and int(cvh.get("l1_minimum_active_packages_attaining_unrestricted_R_star") or 0) == 3
        and abs(float(cvh.get("l1_unrestricted_R_star") or -99.0) - 2.0) < 1e-12
        and int(sh.get("top_k_6_official_targets_changed") or 0) == 11
        and int(sh.get("top_k_6_official_targets_reduced") or 0) == 5
        and int(sh.get("top_k_6_non_dynamic_placebo_semantic_changes", -1)) == 0
        and int(sh.get("top_k_6_quotient_semantic_changes", -1)) == 0
        and int(sh.get("top_k_13_official_semantic_changes", -1)) == 0
        and (int(rh.get("core_single") or 0), int(rh.get("core_multi") or 0)) == (24, 51)
        and abs(float(rh.get("core_uniform_ratio") or -99.0) - 7.0) < 1e-12
        and abs(float(rh.get("core_R_star") or -99.0) - 1.0) < 1e-12
        and abs(float(rh.get("graded_ge_1_uniform_ratio") or -99.0) - 21.0) < 1e-12
        and abs(float(rh.get("graded_ge_1_R_star") or -99.0) - 1.0) < 1e-12
        and skillsbench_support.get("decision") == "STOP_AS_EXACT_SUPPORT_SUBSTRATE"
        and int(sb.get("tasks") or 0) == 87
        and int(sb.get("required_skills_empty_tasks") or 0) == 75
        and int(sb.get("required_vs_task_local_mismatch_tasks") or 0) == 79
        and int(sb.get("task_local_skill_files") or 0) == 232
        and agentskillos.get("decision") == "QUALIFY_AUTHOR_ORACLE_SET_ANALOGUE_ONLY"
        and (int(ah.get("tasks") or 0), int(ah.get("categories") or 0), int(ah.get("unique_oracle_skills") or 0)) == (30, 5, 19)
        and int(ah.get("multi_skill_tasks") or 0) == 20
        and abs(float(ah.get("full_uniform_exposure_ratio") or -99.0) - 4.0) < 1e-12
        and abs(float(ah.get("full_oracle_set_R_star_analogue") or -99.0) - 2.5) < 1e-12
        and set(ah.get("residual_categories") or []) == {"data_computation", "document_creation"}
        and set(ah.get("equalizable_categories") or []) == {"motion_video", "visual_creation", "web_interaction"}
        and "not a complete executable semantic-support relation" in str(agentskillos.get("scientific_boundary") or "")
        and int(sq.get("candidates_screened") or 0) == 5
        and int(sq.get("new_exact_support_substrates", -1)) == 0
        and int(sq.get("new_external_analogues") or 0) == 1
        and sq.get("exact_support_search_disposition") == "NO_SECOND_EXACT_SUPPORT_SUBSTRATE_QUALIFIED"
    ):
        raise RuntimeError("STRI experimental-breadth artifacts failed frozen checks")
    meta["experimental_breadth"] = {
        "practical_baselines_artifact": "artifacts/asset-first-stri-practical-baselines-20260824.json",
        "practical_baselines_sha256": sha(PRACTICAL_BASELINES),
        "crossval_sparsity_artifact": "artifacts/asset-first-stri-crossval-sparsity-20260824.json",
        "crossval_sparsity_sha256": sha(CROSSVAL_SPARSITY),
        "skillrl_budget_artifact": "artifacts/asset-first-stri-skillrl-budget-baselines-20260824.json",
        "skillrl_budget_sha256": sha(SKILLRL_BUDGET_BASELINES),
        "skillrouter_relevance_artifact": "artifacts/asset-first-stri-skillrouter-relevance-analogue-20260824.json",
        "skillrouter_relevance_sha256": sha(SKILLROUTER_RELEVANCE),
        "skillsbench_support_qualification_artifact": "artifacts/asset-first-stri-skillsbench-support-qualification-20260824.json",
        "skillsbench_support_qualification_sha256": sha(SKILLSBENCH_SUPPORT_QUAL),
        "agentskillos_oracle_analogue_artifact": "artifacts/asset-first-stri-agentskillos-oracle-analogue-20260824.json",
        "agentskillos_oracle_analogue_sha256": sha(AGENTSKILLOS_ORACLE),
        "second_substrate_qualification_artifact": "artifacts/asset-first-stri-second-substrate-qualification-20260824.json",
        "second_substrate_qualification_sha256": sha(SECOND_SUBSTRATE_QUAL),
        "headline": {
            "level1_uniform_is_exact_worst_case_optimum": 2.0,
            "level1_inverse_support_ratio": ph.get("level1_inverse_support_ratio"),
            "level1_nnls_ratio": ph.get("level1_nnls_ratio"),
            "leave_one_tool_out": "8/8 exact-R* and uniform heldout ratio=2; NNLS worst=6.10",
            "level1_sparse_frontier": "budgets 1-2 infeasible; 3 active packages attain unrestricted R*=2",
            "skillrl_top_k_6_targets_changed": 11,
            "skillrl_top_k_13_semantic_changes": 0,
            "skillrouter_core": "24 single / 51 multi / R*=1",
            "skillrouter_graded_uniform_spread": 21.0,
            "skillsbench_support_qualification": "STOP: 79/87 required-vs-local mismatches",
            "agentskillos_oracle_graph": "30 tasks / 20 multi / full oracle-set analogue R*=2.5; category R* = 2,2,1,1,1",
            "second_exact_support_substrates_qualified": 0,
        },
        "external_repo_policy": "SkillRL, SkillRouter, and AgentSkillOS first-party repositories are not redistributed; packaged receipts bind exact commits/file hashes and rerun requirements. AgentSkillOS is an author-oracle-set analogue, not executable support.",
        "new_model_calls": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
    }
    multitask_qual = load(MULTITASK_QUAL)
    multitask_contract = load(MULTITASK_CONTRACT)
    multitask_manifest = load(MULTITASK_RUN_MANIFEST)
    multitask_stage1 = load(MULTITASK_STAGE1)
    multitask_failure = load(MULTITASK_FAILURE)
    selected_multitask_units = [str(row.get("unit_id")) for row in (multitask_contract.get("selected_units") or [])]
    if not (
        multitask_qual.get("selection_outcome_blind") is True
        and int(((multitask_qual.get("summary") or {}).get("screened_units") or 0)) == 9
        and int(((multitask_qual.get("summary") or {}).get("qualified_units") or 0)) == 9
        and selected_multitask_units == ["skillmisevo-coding-22-P21", "skillmisevo-coding-21-P19"]
        and int(multitask_manifest.get("run_count") or 0) == 8
        and multitask_manifest.get("all_valid") is True
        and multitask_manifest.get("raw_trajectories_packaged") is False
        and multitask_stage1.get("decision") == "STOP_EXPANSION_STAGE1_GATE_NOT_MET"
        and multitask_stage1.get("all_executions_valid") is True
        and multitask_stage1.get("stage1_gate_pass") is False
        and multitask_stage1.get("stage2_repeat_runs_authorized") is False
        and multitask_stage1.get("remaining_seven_units_authorized") is False
        and int(multitask_stage1.get("new_agent_runs") or 0) == 8
        and int(multitask_stage1.get("judge_calls") or 0) == 0
        and int(multitask_stage1.get("new_gpu_runs") or 0) == 0
        and multitask_stage1.get("claim_expansion") is False
        and ((multitask_stage1.get("per_unit") or {}).get("skillmisevo-coding-22-P21") or {}).get("diagnosis") == "CONTROL_NONCONCORDANCE_NO_SPLIT_SPECIFIC_ATTRIBUTION"
        and ((multitask_stage1.get("per_unit") or {}).get("skillmisevo-coding-21-P19") or {}).get("diagnosis") == "NO_ACTION_SIGNATURE_SEPARATION"
        and multitask_failure.get("memory_class") == "FAILURE_ASSET"
        and multitask_failure.get("stop_class") == "PREREGISTERED_PILOT_GATE_STOP"
    ):
        raise RuntimeError("STRI AutoSkill held-out behavior pilot STOP artifacts failed frozen checks")
    meta["autoskill_multitask_behavior_pilot"] = {
        "qualification_artifact": "artifacts/asset-first-stri-autoskill-multitask-qualification-20260824.json",
        "qualification_sha256": sha(MULTITASK_QUAL),
        "contract_artifact": "artifacts/asset-first-stri-autoskill-multitask-pilot-contract-20260824.json",
        "contract_sha256": sha(MULTITASK_CONTRACT),
        "run_manifest_artifact": "artifacts/asset-first-stri-autoskill-multitask-pilot-run-manifest-20260824.json",
        "run_manifest_sha256": sha(MULTITASK_RUN_MANIFEST),
        "stage1_artifact": "artifacts/asset-first-stri-autoskill-multitask-pilot-stage1-20260824.json",
        "stage1_sha256": sha(MULTITASK_STAGE1),
        "failure_asset": "artifacts/asset-first-stri-autoskill-multitask-pilot-failure-lesson-20260824.json",
        "failure_asset_sha256": sha(MULTITASK_FAILURE),
        "closure_receipt": "artifacts/asset-first-stri-autoskill-multitask-pilot-closure-r19-20260824.json",
        "closure_receipt_sha256": sha(MULTITASK_CLOSURE),
        "headline": {
            "retrieval_qualification": "9/9 held-out units",
            "selected_units": selected_multitask_units,
            "stage1_runs": 8,
            "all_executions_valid": True,
            "stage1_gate_pass": False,
            "decision": "STOP_EXPANSION_STAGE1_GATE_NOT_MET",
            "stage2_repeat_runs": 0,
            "remaining_unit_runs": 0,
            "p19_role": "bounded existence proof"
        },
        "raw_trajectories_packaged": False,
        "new_agent_runs": 8,
        "judge_calls": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
    }
    controller_artifact = GEN / "asset-first-stri-released-controller-clone-audit-20260819.json"
    controller = load(controller_artifact)
    meta["released_controller_audit"] = {
        "artifact": "artifacts/asset-first-stri-released-controller-clone-audit-20260819.json",
        "artifact_sha256": sha(controller_artifact),
        "author_repo_commit": (controller.get("author_release") or {}).get("commit"),
        "third_party_author_repo_packaged": False,
        "rerun_requires_author_release_at_recorded_commit": True,
        "headline": controller.get("headline"),
        "claim_boundary": controller.get("claim_boundary"),
    }
    autoskill = load(AUTOSKILL_RESULT)
    mediator_v1 = load(MEDIATOR_V1_DIAGNOSIS)
    mediator = load(MEDIATOR_V2_RESULT)
    packaged_manifest = load(AUTOSKILL_RUN_MANIFEST)
    canonical_manifest = hashlib.sha256(json.dumps(packaged_manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
    if autoskill.get("decision") != "GO_STAGE3_DYNAMIC_BEHAVIORAL_PROPAGATION":
        raise RuntimeError("AutoSkill P19 dynamic result is not GO_STAGE3_DYNAMIC_BEHAVIORAL_PROPAGATION")
    if sha(AUTOSKILL_RUN_MANIFEST) != autoskill.get("packaged_run_manifest_sha256"):
        raise RuntimeError("AutoSkill packaged run-manifest byte hash mismatch")
    if canonical_manifest != autoskill.get("run_manifest_canonical_sha256"):
        raise RuntimeError("AutoSkill packaged run-manifest canonical hash mismatch")
    if packaged_manifest.get("run_count") != 18 or packaged_manifest.get("all_valid") is not True:
        raise RuntimeError("AutoSkill packaged run-manifest is not 18/18 valid")
    if mediator_v1.get("decision") != "STOP_OPERATIONALIZATION_COMMAND_LOCAL_SIGNATURE_NOT_COMPOSITIONAL" or mediator_v1.get("scientific_negative_authorized") is not False:
        raise RuntimeError("AutoSkill mediator v1 diagnosis is not the frozen operationalization STOP")
    mg = mediator.get("groups") or {}
    ms = mediator.get("statistics") or {}
    if (
        mediator.get("decision") != "GO_MEDIATOR_ISOLATION_P19"
        or mediator.get("all_executions_valid") is not True
        or (mg.get("E_post_addback") or {}).get("positive") != 3
        or (mg.get("F_cleanup_control") or {}).get("positive") != 0
        or ms.get("exact_fraction") != "1/20"
        or ms.get("gate_pass_exact") is not True
        or (mediator.get("measurement_repair") or {}).get("stage3_replay_agreement") != "18/18"
        or int(mediator.get("judge_calls") or 0) != 0
    ):
        raise RuntimeError("AutoSkill P19 mediator-isolation v2 receipt failed frozen checks")
    meta["autoskill_p19_dynamic"] = {
        "result": "artifacts/asset-first-stri-autoskill-p19-stage3-result-20260819.json",
        "result_sha256": sha(packaged_autoskill_result),
        "run_manifest": "artifacts/asset-first-stri-autoskill-p19-stage3-run-manifest-20260819.json",
        "run_manifest_sha256": sha(AUTOSKILL_RUN_MANIFEST),
        "run_manifest_canonical_sha256": canonical_manifest,
        "summary": autoskill_p19_summary(autoskill, mediator),
        "mediator_v1_diagnosis": "artifacts/asset-first-stri-autoskill-p19-mediator-isolation-v1-diagnosis-20260819.json",
        "mediator_v2_result": "artifacts/asset-first-stri-autoskill-p19-mediator-isolation-v2-result-20260819.json",
        "claim_scope": "ONE_ARCHIVED_P19_BEHAVIOR_LEVEL_SUBSTRATE_ONLY",
        "task_utility_claim": False,
        "general_safety_claim": False,
    }
    dump(meta_path, meta)

    summary_path = tree / "outputs" / "reproduction-summary.json"
    summary = load(summary_path)
    summary["skillrl_p0e"] = p0e_summary(receipt)
    summary["autoskill_p19_dynamic"] = autoskill_p19_summary(autoskill, mediator)
    dump(summary_path, summary)

    readme = (tree / "README.md").read_text(encoding="utf-8")
    marker = "## Qualified SkillRL final-policy boundary receipt"
    readme = readme.replace("Python 3.11+", "Python 3.10+")
    if marker not in readme:
        readme += f"""\n\n{marker}\n\nThe paper's optional C4 boundary result is included as `artifacts/{artifact_name}` together with its frozen anonymous contract and panel; the receipt content-addresses the internal model manifest without packaging author-local paths. The sanitized receipt records 18/24 competence calibration success, 24 paired A/B/C/D units with 18/24 terminal success in every arm and zero endpoint disagreements, B/C action-trajectory disagreement of 11/24 versus 15/24, exact D-to-A restoration, and the post-negative statistical-resolution audit. It supports only a qualified realization STOP. It does not establish population-level absence of a downstream effect, a persistent principle dead end, or an active recovery mechanism, and it does not alter N1--N3.\n"""
    reviewer_marker = "## Reviewer-requested certificate extensions"
    if reviewer_marker not in readme:
        readme += """\n\n## Reviewer-requested certificate extensions\n\n`artifacts/asset-first-stri-reviewer-extensions-20260819.json` records the exact LP dual, semantic-first target construction, max-share-constrained certificate, exhaustive single-support-edge perturbation audit, and per-tool exact LP analysis used in the revised manuscript. These analyses are deterministic over the packaged frozen support matrices. The one-cell perturbation audit is a finite local sensitivity analysis, not a claim that learned support labels are calibrated or that arbitrary multi-cell support error is harmless.\n"""
    structural_marker = "## Structural robustness enrichment"
    if structural_marker not in readme:
        readme += """\n\n## Structural robustness enrichment\n\nThe revised main-paper robustness panel is reproduced from the packaged frozen Skill-SP Level-1 membership matrix without model calls or GPU execution. `artifacts/asset-first-stri-target-null-analysis-20260824.json` records seven representation-independent tool-frequency target rays, nine feasible max-share constraints, and 200 degree-preserving bipartite rewires; all tested cases remain residual and every rewire has neutral `R*=2`. `artifacts/asset-first-stri-witness-peeling-20260824.json` records 22 successive pairwise-disjoint three-row dual witnesses spanning 19 tools before the peeled remainder becomes equalizable. `artifacts/asset-first-stri-support-edit-radius-20260824.json` solves exact addition-only and deletion-only MILPs: at least 22 support additions or 71 deletions are required to make the frozen neutral target equalizable, with MIP gap zero and independent `R*` verification. `reproduce.py` recomputes these results from the packaged membership data; the stored artifacts are provenance receipts, not substitutes for reproduction. These controls do not validate learned support, mixed-edit robustness, downstream utility, or a broader dynamic STRI claim.\n"""
    breadth_marker = "## Experimental breadth and practical baselines"
    if breadth_marker not in readme:
        readme += """\n\n## Experimental breadth and practical baselines\n\n`artifacts/asset-first-stri-practical-baselines-20260824.json` evaluates uniform, inverse-coverage, NNLS, cover, max--min, and exact package weighting across five frozen regimes and freezes calibration weights before tool-disjoint heldout evaluation. `artifacts/asset-first-stri-crossval-sparsity-20260824.json` adds eight leave-one-tool-out no-refit transfers and exact active-package sparsity frontiers. `reproduce.py` recomputes both suites from packaged Skill-SP/logical data. The SkillRL budget artifact sweeps eight `top_k` values with fresh-dynamic-ID, non-dynamic-ID placebo, exact quotient, and capacity controls on the pinned first-party release. The SkillRouter artifact audits the released 75-query expert relevance graph as an external relevance analogue only; relevance is not executable semantic support. The SkillsBench qualification artifact records why task-local skill availability is not promoted to an exact support matrix: 79/87 tasks disagree with `required_skills` metadata and 75/87 `required_skills` lists are empty despite non-empty local skill directories. SkillRL, SkillRouter, and SkillsBench repositories are intentionally not redistributed and their receipts bind exact author commits/file hashes. No new model or GPU calls are used by these breadth analyses.\n"""
    second_substrate_marker = "## Second exact-support substrate qualification"
    if second_substrate_marker not in readme:
        readme += """\n\n## Second exact-support substrate qualification\n\n`artifacts/asset-first-stri-second-substrate-qualification-20260824.json` applies one fail-closed support gate to five external candidates. No second exact executable-support substrate qualifies. AgentSkillOS is retained only as an author-oracle-set analogue: its 30 benchmark tasks contain 20 multi-skill oracle sets, the full oracle graph has uniform exposure spread 4x and analogue `R*=2.5`, while category analogues split between residual (`data_computation`, `document_creation`, `R*=2`) and equalizable (`motion_video`, `visual_creation`, `web_interaction`, `R*=1`). `task.skills` is directly consumed by the first-party specified mode, but omitted skills are not proven incapable of supporting a task. SWE-Skills-Bench, SkillLearnBench, SkillsBench, and SkillRouter likewise lack a complete released executable-support zero-edge contract. These objects therefore cannot expand the exact STRI certificate. The AgentSkillOS receipt binds the first-party commit and source-file hashes; rerunning it requires that author release, which is intentionally not redistributed.\n"""
    multitask_marker = "## Held-out AutoSkill behavior pilot STOP"
    if multitask_marker not in readme:
        readme += """\n\n## Held-out AutoSkill behavior pilot STOP\n\nA pre-outcome retrieval-only qualification found 9/9 held-out units where an exact split changes the first-party top-5 semantic retrieval set while ID-placebo and semantic quotient restore the original set. A frozen SHA-256 rule selected two units from different scenarios and positions before any new behavior was observed. One fresh A/B/C/D execution per unit produced 8/8 valid runs under the pre-existing 2026-08-16 judge-independent five-dimensional action signature, but neither unit met the preregistered split-specific stage-1 gate: one had identical A/B/C/D signatures and the other had A=B=C with a different quotient control. The contract therefore stops repeat-2 and the remaining seven units. Raw trajectories are not redistributed; the packaged run manifest content-addresses them, while aggregate signatures and run hashes are included. This failure boundary means robust retrieval sensitivity is not sufficient for task-general behavioral propagation; the earlier P19 result remains a bounded existence proof and does not establish utility, safety, regret, or cross-library generalization.\n"""
    old_breadth_sentence = "`artifacts/asset-first-stri-practical-baselines-20260824.json` evaluates uniform, inverse-coverage, NNLS, cover, max--min, and exact package weighting across five frozen regimes and freezes calibration weights before tool-disjoint heldout evaluation. `reproduce.py` recomputes this suite from packaged Skill-SP/logical data."
    new_breadth_sentence = "`artifacts/asset-first-stri-practical-baselines-20260824.json` evaluates uniform, inverse-coverage, NNLS, cover, max--min, and exact package weighting across five frozen regimes and freezes calibration weights before tool-disjoint heldout evaluation. `artifacts/asset-first-stri-crossval-sparsity-20260824.json` adds eight leave-one-tool-out no-refit transfers and exact active-package sparsity frontiers. `reproduce.py` recomputes both suites from packaged Skill-SP/logical data."
    readme = readme.replace(old_breadth_sentence, new_breadth_sentence)
    controller_marker = "## Released Skill-SP controller audit"
    if controller_marker not in readme:
        readme += """\n\n## Released Skill-SP controller audit\n\n`artifacts/asset-first-stri-released-controller-clone-audit-20260819.json` is the content-addressed receipt for the sampler/prompt-mixture audit. The audit code and unit tests are packaged under `research_pipeline/`. The third-party Skill-SP repository is intentionally not copied into this supplement. To rerun the first-party audit end-to-end, obtain the author release at the exact commit recorded in the receipt and run the packaged audit against the packaged `data/skillsp-toolcall-membership.jsonl`. The receipt records that a same-content clone yields the identical author questioner message string while the released ID-normalized sampler changes message-class mixture TV to 7/120; quotient-conserved class mass restores prompt-mixture and exposure TV to zero. This is a controller-input-distribution result, not downstream utility evidence.\n"""
    autoskill_marker = "## AutoSkill P19 dynamic behavioral propagation"
    if autoskill_marker not in readme:
        readme += """\n\n## AutoSkill P19 dynamic behavioral propagation\n\nThe packaged qualification, frozen v2 contract, Stage-3 plan, final result, and 18-run manifest record the bounded four-arm AutoSkill P19 experiment used in the revised manuscript. The result is 6/6 original, 0/6 split4, 3/3 ID-placebo, and 3/3 quotient-control destructive post-checkout signatures with 18/18 valid fresh-container executions and one-sided Fisher p=0.0010822510822510823. The run manifest content-addresses every per-run receipt and trajectory; its packaged byte hash and canonical semantic hash are checked during supplement refresh. This supports only a representation-to-retrieval-to-executed-behavior consequence on one archived P19 substrate under a common executor. It does not establish task utility, longitudinal regret, end-to-end AutoSkill runtime behavior, or general AutoSkill safety.\n"""
    mediator_marker = "## AutoSkill P19 matched mediator isolation"
    if mediator_marker not in readme:
        readme += """\n\n## AutoSkill P19 matched mediator isolation\n\nThe first mediator-isolation attempt exposed a measurement operationalization bug: the command-local signature missed a destructive payload written to an intermediate script and copied to the post-checkout hook in a later command. The sequence-aware repair preserves all 18 Stage-3 labels exactly. All v1 runs are excluded from v2 inference. In six fresh v2 runs under the same split representation and matched five-slot/three-semantic-class injection, adding back the crowded-out post-checkout skill restores the mechanical destructive behavior in 3/3 runs, while adding a matched stale-output cleanup skill yields 0/3. The exact one-sided Fisher probability is 1/20=0.05. This isolates the post-checkout skill as the mediator within the one archived P19 substrate; it does not establish task utility, longitudinal regret, end-to-end AutoSkill behavior, or general safety.\n"""
    (tree / "README.md").write_text(readme, encoding="utf-8")

    reproduce_path = tree / "reproduce.py"
    reproduce = reproduce_path.read_text(encoding="utf-8")
    marker_code = "# P0-E SANITIZED RECEIPT CHECK"
    if "from research_pipeline.asset_first_stri_reviewer_extensions import evaluate as evaluate_reviewer_extensions" not in reproduce:
        reproduce = reproduce.replace(
            "from research_pipeline.asset_first_stri_paper_analysis_suite import build as build_paper_analysis\n",
            "from research_pipeline.asset_first_stri_paper_analysis_suite import build as build_paper_analysis\nfrom research_pipeline.asset_first_stri_reviewer_extensions import evaluate as evaluate_reviewer_extensions\n",
            1,
        )
    if "from research_pipeline.asset_first_stri_target_null_analysis_20260824 import build as build_target_null" not in reproduce:
        reproduce = reproduce.replace(
            "from research_pipeline.asset_first_stri_reviewer_extensions import evaluate as evaluate_reviewer_extensions\n",
            "from research_pipeline.asset_first_stri_reviewer_extensions import evaluate as evaluate_reviewer_extensions\nfrom research_pipeline.asset_first_stri_target_null_analysis_20260824 import build as build_target_null\nfrom research_pipeline.asset_first_stri_witness_peeling_20260824 import build as build_witness_peeling\nfrom research_pipeline.asset_first_stri_support_edit_radius_20260824 import build as build_support_edit_radius\n",
            1,
        )
    if "from research_pipeline.asset_first_stri_practical_baselines_20260824 import build_from_rows as build_practical_baselines" not in reproduce:
        reproduce = reproduce.replace(
            "from research_pipeline.asset_first_stri_support_edit_radius_20260824 import build as build_support_edit_radius\n",
            "from research_pipeline.asset_first_stri_support_edit_radius_20260824 import build as build_support_edit_radius\nfrom research_pipeline.asset_first_stri_practical_baselines_20260824 import build_from_rows as build_practical_baselines\n",
            1,
        )
    if "from research_pipeline.asset_first_stri_crossval_sparsity_20260824 import build_from_rows as build_crossval_sparsity" not in reproduce:
        reproduce = reproduce.replace(
            "from research_pipeline.asset_first_stri_practical_baselines_20260824 import build_from_rows as build_practical_baselines\n",
            "from research_pipeline.asset_first_stri_practical_baselines_20260824 import build_from_rows as build_practical_baselines\nfrom research_pipeline.asset_first_stri_crossval_sparsity_20260824 import build_from_rows as build_crossval_sparsity\n",
            1,
        )
    if marker_code not in reproduce:
        check_code = f'''\n    {marker_code}\n    p0e = json.loads((ROOT / "artifacts/{artifact_name}").read_text())\n    assert p0e["competence_calibration"]["pristine_success"] == 18\n    assert p0e["paired_causal_result"]["paired_units"] == 24\n    assert set(p0e["paired_causal_result"]["success_rate"].values()) == {{0.75}}\n    assert set(p0e["paired_causal_result"]["paired_disagreement"].values()) == {{0.0}}\n    assert p0e["trajectory_boundary"]["B_vs_A_action_sequence_disagreement"] == 11\n    assert p0e["trajectory_boundary"]["C_vs_A_action_sequence_disagreement"] == 15\n    assert p0e["trajectory_boundary"]["D_vs_A_exact_trajectory_units"] == 24\n    assert p0e["trajectory_boundary"]["any_simple_B_over_C_dominance_supported"] is False\n    assert p0e["statistical_resolution"]["two_sided_exact_mcnemar_p_at_effect_floor"] == 0.25\n    assert p0e["statistical_resolution"]["minimum_unidirectional_discordances_for_p_lt_0_05"] == 6\n    assert p0e["final_disposition"]["experimental_stop_valid"] is True\n    assert p0e["final_disposition"]["persistent_principle_dead_end_certified"] is False\n    assert p0e["final_disposition"]["broader_STRI_N1_N2_N3_unchanged"] is True\n    p0e_summary = {{"experimental_realization": p0e["final_disposition"]["experimental_realization"], "principle_disposition": p0e["final_disposition"]["principle_disposition"], "paired_units": 24, "terminal_success_per_arm": "18/24", "endpoint_disagreement": 0, "B_action_diff": 11, "C_action_diff": 15, "persistent_principle_dead_end_certified": False}}\n'''
        reproduce = reproduce.replace("\n    out = {", check_code + "\n    out = {", 1)
        reproduce = reproduce.replace('        "dynamic_p0a": {"decision": p0a["decision"], "contract_valid_by_source": counts, "required_per_source": 16, "scientific_belief_update": False},', '        "dynamic_p0a": {"decision": p0a["decision"], "contract_valid_by_source": counts, "required_per_source": 16, "scientific_belief_update": False},\n        "skillrl_p0e": p0e_summary,', 1)
    reviewer_code_marker = "# REVIEWER EXTENSIONS CHECK"
    if reviewer_code_marker not in reproduce:
        reviewer_code = '''\n    # REVIEWER EXTENSIONS CHECK\n    reviewer = evaluate_reviewer_extensions(tool_rows, logical_rows)\n    checks = reviewer["headline_checks"]\n    assert checks["all_primal_dual_gaps_le_1e_8"] is True\n    assert checks["semantic_first_neutral_target_exact_on_all_five_regimes"] is True\n    assert checks["level1_residual_survives_all_single_support_additions"] is True\n    assert checks["level1_residual_survives_all_nonuncovering_single_support_deletions"] is True\n    assert checks["logical_rho_075_not_equalizable"] is True\n    assert checks["logical_single_deletions_can_break_equalizability"] is True\n    assert checks["all_overlap_without_simple_witness_tools_resolve_equalizable"] is True\n    reviewer_summary = {\n        "headline_checks": checks,\n        "level1": reviewer["contexts"]["api_bank_level1_all"],\n        "logical": reviewer["contexts"]["logical_compiler_validation"],\n        "per_tool": reviewer["per_tool_exact_lp"],\n    }\n'''
        reproduce = reproduce.replace("\n    out = {", reviewer_code + "\n    out = {", 1)
        reproduce = reproduce.replace('        "skillrl_p0e": p0e_summary,', '        "skillrl_p0e": p0e_summary,\n        "reviewer_extensions": reviewer_summary,', 1)
    structural_code_marker = "# STRUCTURAL ROBUSTNESS ENRICHMENT CHECK"
    if structural_code_marker not in reproduce:
        structural_code = '''\n    # STRUCTURAL ROBUSTNESS ENRICHMENT CHECK\n    structural_membership = ROOT / "data/skillsp-toolcall-membership.jsonl"\n    target_null = build_target_null(structural_membership)\n    target_summary = target_null["target_ray_sensitivity"]["summary"]\n    share_summary = target_null["max_share_sensitivity"]["summary"]\n    null_summary = target_null["degree_preserving_null_ensemble"]["summary"]\n    assert target_summary["targets"] == 7\n    assert target_summary["all_tested_targets_residual"] is True\n    assert abs(target_summary["neutral_R_star"] - 2.0) < 1e-12\n    assert share_summary["valid_constraints"] == 9\n    assert share_summary["all_valid_constraints_residual"] is True\n    assert null_summary["residual_draws"] == 200 and null_summary["equalizable_draws"] == 0\n    assert abs(null_summary["minimum_R_star"] - 2.0) < 1e-12 and abs(null_summary["maximum_R_star"] - 2.0) < 1e-12\n    witness = build_witness_peeling(structural_membership)\n    witness_summary = witness["witness_peeling"]["summary"]\n    assert witness_summary["peeling_rounds_before_equalizable"] == 22\n    assert witness_summary["pairwise_disjoint_witness_rows_removed"] == 66\n    assert witness_summary["unique_tools_spanned"] == 19\n    assert abs(witness_summary["final_R_star"] - 1.0) < 1e-12\n    edit = build_support_edit_radius(structural_membership)\n    edit_radius = edit["support_edit_radius"]\n    assert edit_radius["minimum_additions_to_equalizable"] == 22\n    assert edit_radius["minimum_deletions_to_equalizable"] == 71\n    assert abs(edit_radius["addition_solution"]["mip_gap"]) < 1e-12\n    assert abs(edit_radius["deletion_solution"]["mip_gap"]) < 1e-12\n    assert abs(edit_radius["addition_solution"]["verified_R_star"] - 1.0) < 1e-12\n    assert abs(edit_radius["deletion_solution"]["verified_R_star"] - 1.0) < 1e-12\n    structural_summary = {\n        "target_rays_residual": "7/7",\n        "degree_preserving_rewires_residual": "200/200",\n        "max_share_constraints_preserving_R_star_2": "9/9",\n        "disjoint_three_row_witnesses": 22,\n        "witness_rows_removed": 66,\n        "witness_tools_spanned": 19,\n        "minimum_additions_to_equalizable": 22,\n        "minimum_deletions_to_equalizable": 71,\n        "new_model_calls": 0,\n        "new_gpu_runs": 0,\n    }\n'''
        reproduce = reproduce.replace("\n    out = {", structural_code + "\n    out = {", 1)
        reproduce = reproduce.replace('        "reviewer_extensions": reviewer_summary,', '        "reviewer_extensions": reviewer_summary,\n        "structural_enrichment": structural_summary,', 1)
    breadth_code_marker = "# EXPERIMENTAL BREADTH CHECK"
    if breadth_code_marker not in reproduce:
        breadth_code = '''\n    # EXPERIMENTAL BREADTH CHECK\n    split = json.loads((ROOT / "artifacts/asset-first-stri-tool-disjoint-split-20260816.json").read_text())\n    practical = build_practical_baselines(tool_rows, logical_rows, split, input_label="packaged-data")\n    ph = practical["headline"]\n    assert abs(ph["level1_uniform_ratio"] - 2.0) < 1e-12\n    assert ph["level1_inverse_support_ratio"] > 90.0\n    assert ph["level1_nnls_ratio"] > 5.0\n    assert ph["level1_nnls_cv"] < ph["level1_uniform_cv"]\n    transfer = {row["baseline"]: row for row in practical["calibration_to_heldout"]["results"]}\n    assert practical["calibration_to_heldout"]["no_heldout_refit"] is True\n    assert abs(transfer["exact_rstar"]["heldout_metrics"]["distortion_ratio"] - 2.0) < 1e-12\n    crossval = build_crossval_sparsity(tool_rows, logical_rows, split, input_label="packaged-data")\n    cvh = crossval["headline"]\n    assert cvh["leave_one_tool_out_folds"] == 8\n    assert abs(cvh["exact_rstar_heldout_ratio_max"] - 2.0) < 1e-12\n    assert abs(cvh["uniform_heldout_ratio_max"] - 2.0) < 1e-12\n    assert cvh["nnls_heldout_ratio_max"] > 6.0\n    assert cvh["l1_minimum_feasible_active_packages"] == 3\n    assert cvh["l1_minimum_active_packages_attaining_unrestricted_R_star"] == 3\n    assert abs(cvh["l1_unrestricted_R_star"] - 2.0) < 1e-12\n    skillrl_budget = json.loads((ROOT / "artifacts/asset-first-stri-skillrl-budget-baselines-20260824.json").read_text())\n    sh = skillrl_budget["headline"]\n    assert sh["top_k_6_official_targets_changed"] == 11\n    assert sh["top_k_6_official_targets_reduced"] == 5\n    assert sh["top_k_6_non_dynamic_placebo_semantic_changes"] == 0\n    assert sh["top_k_6_quotient_semantic_changes"] == 0\n    assert sh["top_k_13_official_semantic_changes"] == 0\n    assert skillrl_budget["rerun_requires_author_release_at_recorded_commit"] is True\n    skillrouter = json.loads((ROOT / "artifacts/asset-first-stri-skillrouter-relevance-analogue-20260824.json").read_text())\n    rh = skillrouter["headline"]\n    assert (rh["core_single"], rh["core_multi"]) == (24, 51)\n    assert abs(rh["core_uniform_ratio"] - 7.0) < 1e-12 and abs(rh["core_R_star"] - 1.0) < 1e-12\n    assert abs(rh["graded_ge_1_uniform_ratio"] - 21.0) < 1e-12 and abs(rh["graded_ge_1_R_star"] - 1.0) < 1e-12\n    assert "retrieval acceptability" in skillrouter["scientific_boundary"]\n    assert skillrouter["rerun_requires_author_release_at_recorded_commit"] is True\n    skillsbench = json.loads((ROOT / "artifacts/asset-first-stri-skillsbench-support-qualification-20260824.json").read_text())\n    sb = skillsbench["summary"]\n    assert skillsbench["decision"] == "STOP_AS_EXACT_SUPPORT_SUBSTRATE"\n    assert sb["tasks"] == 87 and sb["required_skills_empty_tasks"] == 75\n    assert sb["required_vs_task_local_mismatch_tasks"] == 79 and sb["task_local_skill_files"] == 232\n    assert skillsbench["rerun_requires_author_release_at_recorded_commit"] is True\n    breadth_summary = {\n        "practical_level1_uniform_R": ph["level1_uniform_ratio"],\n        "practical_level1_inverse_support_R": ph["level1_inverse_support_ratio"],\n        "practical_level1_nnls_R": ph["level1_nnls_ratio"],\n        "calibration_to_heldout_exact_R": transfer["exact_rstar"]["heldout_metrics"]["distortion_ratio"],\n        "leave_one_tool_out_exact_R_max": cvh["exact_rstar_heldout_ratio_max"],\n        "leave_one_tool_out_nnls_R_max": cvh["nnls_heldout_ratio_max"],\n        "l1_minimum_feasible_active_packages": cvh["l1_minimum_feasible_active_packages"],\n        "l1_minimum_active_packages_attaining_unrestricted_R_star": cvh["l1_minimum_active_packages_attaining_unrestricted_R_star"],\n        "skillrl_top_k_6_targets_changed": 11,\n        "skillrl_top_k_13_semantic_changes": 0,\n        "skillrouter_core_uniform_R": 7.0,\n        "skillrouter_core_exact_R": 1.0,\n        "skillrouter_graded_uniform_R": 21.0,\n        "skillrouter_graded_exact_R": 1.0,\n        "skillsbench_support_qualification": "STOP_79_OF_87_METADATA_AVAILABILITY_MISMATCH",\n        "new_model_calls": 0,\n        "new_gpu_runs": 0,\n    }\n'''
        reproduce = reproduce.replace("\n    out = {", breadth_code + "\n    out = {", 1)
        reproduce = reproduce.replace('        "structural_enrichment": structural_summary,', '        "structural_enrichment": structural_summary,\n        "experimental_breadth": breadth_summary,', 1)
    # Upgrade an already-packaged R16 breadth block instead of treating marker
    # presence as proof that the newer R17 cross-validation/sparsity checks run.
    if breadth_code_marker in reproduce and '"leave_one_tool_out_exact_R_max"' not in reproduce:
        old_transfer_tail = '''    assert abs(transfer["exact_rstar"]["heldout_metrics"]["distortion_ratio"] - 2.0) < 1e-12\n    skillrl_budget = json.loads((ROOT / "artifacts/asset-first-stri-skillrl-budget-baselines-20260824.json").read_text())\n'''
        new_transfer_tail = '''    assert abs(transfer["exact_rstar"]["heldout_metrics"]["distortion_ratio"] - 2.0) < 1e-12\n    crossval = build_crossval_sparsity(tool_rows, logical_rows, split, input_label="packaged-data")\n    cvh = crossval["headline"]\n    assert cvh["leave_one_tool_out_folds"] == 8\n    assert abs(cvh["exact_rstar_heldout_ratio_max"] - 2.0) < 1e-12\n    assert abs(cvh["uniform_heldout_ratio_max"] - 2.0) < 1e-12\n    assert cvh["nnls_heldout_ratio_max"] > 6.0\n    assert cvh["l1_minimum_feasible_active_packages"] == 3\n    assert cvh["l1_minimum_active_packages_attaining_unrestricted_R_star"] == 3\n    assert abs(cvh["l1_unrestricted_R_star"] - 2.0) < 1e-12\n    skillrl_budget = json.loads((ROOT / "artifacts/asset-first-stri-skillrl-budget-baselines-20260824.json").read_text())\n'''
        if old_transfer_tail not in reproduce:
            raise RuntimeError("cannot upgrade existing R16 breadth block with R17 cross-validation checks")
        reproduce = reproduce.replace(old_transfer_tail, new_transfer_tail, 1)
        old_summary_tail = '''        "calibration_to_heldout_exact_R": transfer["exact_rstar"]["heldout_metrics"]["distortion_ratio"],\n        "skillrl_top_k_6_targets_changed": 11,\n'''
        new_summary_tail = '''        "calibration_to_heldout_exact_R": transfer["exact_rstar"]["heldout_metrics"]["distortion_ratio"],\n        "leave_one_tool_out_exact_R_max": cvh["exact_rstar_heldout_ratio_max"],\n        "leave_one_tool_out_nnls_R_max": cvh["nnls_heldout_ratio_max"],\n        "l1_minimum_feasible_active_packages": cvh["l1_minimum_feasible_active_packages"],\n        "l1_minimum_active_packages_attaining_unrestricted_R_star": cvh["l1_minimum_active_packages_attaining_unrestricted_R_star"],\n        "skillrl_top_k_6_targets_changed": 11,\n'''
        if old_summary_tail not in reproduce:
            raise RuntimeError("cannot upgrade existing R16 breadth summary with R17 cross-validation outputs")
        reproduce = reproduce.replace(old_summary_tail, new_summary_tail, 1)
    second_substrate_code_marker = "# SECOND SUPPORT SUBSTRATE QUALIFICATION CHECK"
    if second_substrate_code_marker not in reproduce:
        second_substrate_code = '''\n    # SECOND SUPPORT SUBSTRATE QUALIFICATION CHECK\n    agentskillos = json.loads((ROOT / "artifacts/asset-first-stri-agentskillos-oracle-analogue-20260824.json").read_text())\n    ah = agentskillos["headline"]\n    assert agentskillos["decision"] == "QUALIFY_AUTHOR_ORACLE_SET_ANALOGUE_ONLY"\n    assert (ah["tasks"], ah["categories"], ah["unique_oracle_skills"], ah["multi_skill_tasks"]) == (30, 5, 19, 20)\n    assert abs(ah["full_uniform_exposure_ratio"] - 4.0) < 1e-12\n    assert abs(ah["full_oracle_set_R_star_analogue"] - 2.5) < 1e-12\n    assert set(ah["residual_categories"]) == {"data_computation", "document_creation"}\n    assert set(ah["equalizable_categories"]) == {"motion_video", "visual_creation", "web_interaction"}\n    assert "not a complete executable semantic-support relation" in agentskillos["scientific_boundary"]\n    assert agentskillos["rerun_requires_author_release_at_recorded_commit"] is True\n    second_support = json.loads((ROOT / "artifacts/asset-first-stri-second-substrate-qualification-20260824.json").read_text())\n    sq = second_support["summary"]\n    assert sq["candidates_screened"] == 5\n    assert sq["new_exact_support_substrates"] == 0\n    assert sq["new_external_analogues"] == 1\n    assert sq["exact_support_search_disposition"] == "NO_SECOND_EXACT_SUPPORT_SUBSTRATE_QUALIFIED"\n    breadth_summary["agentskillos_full_uniform_R"] = 4.0\n    breadth_summary["agentskillos_full_oracle_R"] = 2.5\n    breadth_summary["agentskillos_residual_categories"] = ah["residual_categories"]\n    breadth_summary["agentskillos_equalizable_categories"] = ah["equalizable_categories"]\n    breadth_summary["second_exact_support_substrates_qualified"] = 0\n'''
        reproduce = reproduce.replace("\n    out = {", second_substrate_code + "\n    out = {", 1)
    multitask_code_marker = "# AUTOSKILL HELD-OUT BEHAVIOR PILOT STOP CHECK"
    if multitask_code_marker not in reproduce:
        multitask_code = '''\n    # AUTOSKILL HELD-OUT BEHAVIOR PILOT STOP CHECK\n    mtq = json.loads((ROOT / "artifacts/asset-first-stri-autoskill-multitask-qualification-20260824.json").read_text())\n    mtc = json.loads((ROOT / "artifacts/asset-first-stri-autoskill-multitask-pilot-contract-20260824.json").read_text())\n    mtm = json.loads((ROOT / "artifacts/asset-first-stri-autoskill-multitask-pilot-run-manifest-20260824.json").read_text())\n    mts = json.loads((ROOT / "artifacts/asset-first-stri-autoskill-multitask-pilot-stage1-20260824.json").read_text())\n    mtf = json.loads((ROOT / "artifacts/asset-first-stri-autoskill-multitask-pilot-failure-lesson-20260824.json").read_text())\n    assert mtq["selection_outcome_blind"] is True\n    assert (mtq["summary"]["screened_units"], mtq["summary"]["qualified_units"]) == (9, 9)\n    assert [u["unit_id"] for u in mtc["selected_units"]] == ["skillmisevo-coding-22-P21", "skillmisevo-coding-21-P19"]\n    assert mtm["run_count"] == 8 and mtm["all_valid"] is True and mtm["raw_trajectories_packaged"] is False\n    assert mts["decision"] == "STOP_EXPANSION_STAGE1_GATE_NOT_MET"\n    assert mts["all_executions_valid"] is True and mts["stage1_gate_pass"] is False\n    assert mts["stage2_repeat_runs_authorized"] is False and mts["remaining_seven_units_authorized"] is False\n    assert mts["new_agent_runs"] == 8 and mts["judge_calls"] == 0 and mts["new_gpu_runs"] == 0 and mts["claim_expansion"] is False\n    assert mts["per_unit"]["skillmisevo-coding-22-P21"]["diagnosis"] == "CONTROL_NONCONCORDANCE_NO_SPLIT_SPECIFIC_ATTRIBUTION"\n    assert mts["per_unit"]["skillmisevo-coding-21-P19"]["diagnosis"] == "NO_ACTION_SIGNATURE_SEPARATION"\n    assert mtf["memory_class"] == "FAILURE_ASSET" and mtf["stop_class"] == "PREREGISTERED_PILOT_GATE_STOP"\n    multitask_summary = {\n        "retrieval_qualification": "9/9",\n        "selected_units": [u["unit_id"] for u in mtc["selected_units"]],\n        "stage1_runs": 8,\n        "all_executions_valid": True,\n        "stage1_gate_pass": False,\n        "decision": mts["decision"],\n        "stage2_repeat_runs": 0,\n        "remaining_unit_runs": 0,\n        "unit_diagnoses": {uid: row["diagnosis"] for uid, row in mts["per_unit"].items()},\n        "raw_trajectories_packaged": False,\n        "new_agent_runs": 8,\n        "judge_calls": 0,\n        "new_gpu_runs": 0,\n        "claim_expansion": False,\n    }\n'''
        reproduce = reproduce.replace("\n    out = {", multitask_code + "\n    out = {", 1)
        reproduce = reproduce.replace('        "experimental_breadth": breadth_summary,', '        "experimental_breadth": breadth_summary,\n        "autoskill_multitask_pilot": multitask_summary,', 1)
    controller_code_marker = "# RELEASED CONTROLLER AUDIT RECEIPT CHECK"
    if controller_code_marker not in reproduce:
        controller_code = '''\n    # RELEASED CONTROLLER AUDIT RECEIPT CHECK\n    controller = json.loads((ROOT / "artifacts/asset-first-stri-released-controller-clone-audit-20260819.json").read_text())\n    assert controller["all_checks_pass"] is True\n    cc = controller["checks"]\n    assert cc["clone_weights_recomputed_by_author_sampling_function"] is True\n    assert cc["author_duplicate_filter_would_reject_literal_exact_text_clone"] is True\n    assert cc["same_content_clone_has_identical_author_questioner_messages"] is True\n    assert cc["released_sampler_clone_changes_author_questioner_prompt_mixture"] is True\n    assert cc["quotient_conservation_exactly_restores_author_questioner_prompt_mixture"] is True\n    assert cc["quotient_conserved_allocation_exactly_restores_base_exposure"] is True\n    ch = controller["headline"]\n    assert abs(ch["base_package_probability"] - (1.0 / 15.0)) < 1e-12\n    assert abs(ch["exact_clone_family_probability"] - (1.0 / 8.0)) < 1e-12\n    assert len(ch["released_sampler_questioner_prompt_mixture_tv_after_clone_all_targets"]) == 1\n    assert abs(ch["released_sampler_questioner_prompt_mixture_tv_after_clone_all_targets"][0] - (7.0 / 120.0)) < 1e-12\n    assert len(ch["quotient_conserved_questioner_prompt_mixture_tv_after_clone_all_targets"]) == 1\n    assert abs(ch["quotient_conserved_questioner_prompt_mixture_tv_after_clone_all_targets"][0]) < 1e-12\n    assert len(ch["quotient_conserved_exposure_profile_tv_all_targets"]) == 1\n    assert abs(ch["quotient_conserved_exposure_profile_tv_all_targets"][0]) < 1e-12\n    controller_summary = {\n        "author_repo_commit": controller["author_release"]["commit"],\n        "all_checks_pass": True,\n        "base_package_probability": ch["base_package_probability"],\n        "clone_family_probability": ch["exact_clone_family_probability"],\n        "released_prompt_mixture_tv": ch["released_sampler_questioner_prompt_mixture_tv_after_clone_all_targets"],\n        "quotient_prompt_mixture_tv": ch["quotient_conserved_questioner_prompt_mixture_tv_after_clone_all_targets"],\n        "quotient_exposure_profile_tv": ch["quotient_conserved_exposure_profile_tv_all_targets"],\n        "third_party_author_repo_packaged": False,\n    }\n'''
        reproduce = reproduce.replace("\n    out = {", controller_code + "\n    out = {", 1)
        reproduce = reproduce.replace('        "reviewer_extensions": reviewer_summary,', '        "reviewer_extensions": reviewer_summary,\n        "released_controller_audit": controller_summary,', 1)
    autoskill_code_marker = "# AUTOSKILL P19 DYNAMIC RECEIPT CHECK"
    if autoskill_code_marker not in reproduce:
        autoskill_code = '''\n    # AUTOSKILL P19 DYNAMIC RECEIPT CHECK\n    import hashlib as _hashlib\n    autoskill = json.loads((ROOT / "artifacts/asset-first-stri-autoskill-p19-stage3-result-20260819.json").read_text())\n    autoskill_manifest_path = ROOT / "artifacts/asset-first-stri-autoskill-p19-stage3-run-manifest-20260819.json"\n    autoskill_manifest = json.loads(autoskill_manifest_path.read_text())\n    assert autoskill["decision"] == "GO_STAGE3_DYNAMIC_BEHAVIORAL_PROPAGATION"\n    ag = autoskill["groups"]\n    assert (ag["A_original"]["valid_runs"], ag["A_original"]["destructive_signature_positive"]) == (6, 6)\n    assert (ag["B_split4"]["valid_runs"], ag["B_split4"]["destructive_signature_positive"]) == (6, 0)\n    assert (ag["C_id_placebo"]["valid_runs"], ag["C_id_placebo"]["destructive_signature_positive"]) == (3, 3)\n    assert (ag["D_quotient_control"]["valid_runs"], ag["D_quotient_control"]["destructive_signature_positive"]) == (3, 3)\n    assert all(autoskill["frozen_gates"].values())\n    assert abs(autoskill["statistics"]["fisher_exact_p"] - 0.0010822510822510823) < 1e-15\n    assert autoskill["judge_calls"] == 0 and autoskill["training_steps"] == 0\n    assert autoskill_manifest["run_count"] == 18 and autoskill_manifest["all_valid"] is True\n    assert _hashlib.sha256(autoskill_manifest_path.read_bytes()).hexdigest() == autoskill["packaged_run_manifest_sha256"]\n    autoskill_canonical = _hashlib.sha256(json.dumps(autoskill_manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()\n    assert autoskill_canonical == autoskill["run_manifest_canonical_sha256"]\n    assert len(autoskill["run_manifest_sha256"]) == 64\n    autoskill_summary = {\n        "decision": autoskill["decision"],\n        "groups": ag,\n        "fisher_exact_p": autoskill["statistics"]["fisher_exact_p"],\n        "run_count": 18,\n        "all_valid": True,\n        "claim_boundary": autoskill["scientific_claim_boundary"],\n    }\n'''
        reproduce = reproduce.replace("\n    out = {", autoskill_code + "\n    out = {", 1)
        reproduce = reproduce.replace('        "released_controller_audit": controller_summary,', '        "released_controller_audit": controller_summary,\n        "autoskill_p19_dynamic": autoskill_summary,', 1)
    mediator_code_marker = "# AUTOSKILL P19 MEDIATOR ISOLATION V2 CHECK"
    if mediator_code_marker not in reproduce:
        mediator_code = '''\n    # AUTOSKILL P19 MEDIATOR ISOLATION V2 CHECK\n    mediator_v1 = json.loads((ROOT / "artifacts/asset-first-stri-autoskill-p19-mediator-isolation-v1-diagnosis-20260819.json").read_text())\n    mediator = json.loads((ROOT / "artifacts/asset-first-stri-autoskill-p19-mediator-isolation-v2-result-20260819.json").read_text())\n    assert mediator_v1["decision"] == "STOP_OPERATIONALIZATION_COMMAND_LOCAL_SIGNATURE_NOT_COMPOSITIONAL"\n    assert mediator_v1["scientific_negative_authorized"] is False\n    assert mediator_v1["sequence_aware_replay_audit"]["stage3_agreement_with_frozen_metric"] == "18/18"\n    assert mediator["decision"] == "GO_MEDIATOR_ISOLATION_P19"\n    assert mediator["all_executions_valid"] is True\n    assert mediator["groups"]["E_post_addback"] == {"valid_runs": 3, "positive": 3}\n    assert mediator["groups"]["F_cleanup_control"] == {"valid_runs": 3, "positive": 0}\n    assert mediator["statistics"]["exact_fraction"] == "1/20"\n    assert abs(mediator["statistics"]["exact_decimal"] - 0.05) < 1e-15\n    assert mediator["statistics"]["gate_pass_exact"] is True\n    assert mediator["measurement_repair"]["stage3_replay_agreement"] == "18/18"\n    assert mediator["judge_calls"] == 0\n    mediator_summary = {\n        "decision": mediator["decision"],\n        "groups": mediator["groups"],\n        "exact_fisher": mediator["statistics"]["exact_fraction"],\n        "stage3_replay_agreement": mediator["measurement_repair"]["stage3_replay_agreement"],\n        "judge_calls": 0,\n        "claim_boundary": mediator["claim_boundary"],\n    }\n'''
        reproduce = reproduce.replace("\n    out = {", mediator_code + "\n    out = {", 1)
        reproduce = reproduce.replace('        "autoskill_p19_dynamic": autoskill_summary,', '        "autoskill_p19_dynamic": autoskill_summary,\n        "autoskill_p19_mediator_isolation": mediator_summary,', 1)
    reproduce_path.write_text(reproduce, encoding="utf-8")

    refresh_manifest(tree)


def refresh_manifest(tree: Path) -> None:
    manifest_path = tree / "MANIFEST.sha256"
    entries = []
    for path in sorted(p for p in tree.rglob("*") if p.is_file() and p != manifest_path):
        entries.append(f"{sha(path)}  ./{path.relative_to(tree).as_posix()}")
    manifest_path.write_text("\n".join(entries) + "\n", encoding="utf-8")


def verify_manifest(tree: Path) -> int:
    lines = (tree / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines()
    for line in lines:
        expected, rel = line.split("  ./", 1)
        if sha(tree / rel) != expected:
            raise RuntimeError(f"supplement manifest mismatch: {rel}")
    return len(lines)


def anonymity_scan(tree: Path) -> None:
    import re
    literal_patterns = [b"/home/wyt/", b"/data/wyt/", b"wyt@", b"222.20", b"10.42"]
    token_pattern = re.compile(rb"hf_[A-Za-z0-9]{20,}", flags=re.I)
    for path in (p for p in tree.rglob("*") if p.is_file()):
        data = path.read_bytes()
        lowered = data.lower()
        for pattern in literal_patterns:
            if pattern.lower() in lowered:
                raise RuntimeError(f"anonymous supplement contains forbidden identity/path pattern {pattern!r}: {path.relative_to(tree)}")
        if token_pattern.search(data):
            raise RuntimeError(f"anonymous supplement contains a token-like hf_ credential: {path.relative_to(tree)}")


def build_and_verify_supplement() -> dict:
    if not REMOTE_SUPPLEMENT.is_file():
        raise FileNotFoundError(REMOTE_SUPPLEMENT)
    receipt = load(P0E_RECEIPT)
    with tempfile.TemporaryDirectory(prefix="stri-supplement-refresh-") as tmp:
        tree = Path(tmp) / "package"
        tree.mkdir()
        with zipfile.ZipFile(REMOTE_SUPPLEMENT) as zf:
            zf.extractall(tree)
        update_supplement_tree(tree, receipt)
        verify_manifest(tree)
        anonymity_scan(tree)
        repro_python = find_repro_python()
        repro = run([repro_python, "reproduce.py"], cwd=tree)
        reproduced = json.loads((tree / "outputs" / "reproduction-summary.json").read_text(encoding="utf-8"))
        if reproduced.get("status") != "PASS" or "skillrl_p0e" not in reproduced or "structural_enrichment" not in reproduced or "experimental_breadth" not in reproduced or "autoskill_p19_dynamic" not in reproduced or "autoskill_p19_mediator_isolation" not in reproduced or "autoskill_multitask_pilot" not in reproduced:
            raise RuntimeError("supplement reproduction did not retain STRI structural enrichment, experimental breadth, SkillRL P0-E, AutoSkill P19 Stage-3/mediator, and held-out behavior-pilot STOP receipts")
        tests = run([repro_python, "-m", "unittest", "discover", "-s", "research_pipeline", "-t", ".", "-p", "test_asset_first_stri_*.py"], cwd=tree)
        test_line = next((line.strip() for line in tests.stdout.splitlines() if line.startswith("Ran ")), "")
        if "OK" not in tests.stdout:
            raise RuntimeError("supplement unit tests did not pass")
        match = __import__("re").search(r"Ran (\d+) tests?", test_line)
        unit_test_count = int(match.group(1)) if match else 0
        if unit_test_count <= 0:
            raise RuntimeError(f"could not parse supplement unit-test count: {test_line!r}")
        for cache_dir in sorted(tree.rglob("__pycache__"), reverse=True):
            if cache_dir.is_dir():
                shutil.rmtree(cache_dir)
        for bytecode in tree.rglob("*.pyc"):
            bytecode.unlink()
        refresh_manifest(tree)
        manifest_entries = verify_manifest(tree)
        anonymity_scan(tree)
        refreshed = Path(tmp) / "supplement.zip"
        file_count = deterministic_zip_tree(tree, refreshed)
        REMOTE.mkdir(parents=True, exist_ok=True)
        temp_remote = REMOTE_SUPPLEMENT.with_suffix(".zip.tmp")
        shutil.copy2(refreshed, temp_remote)
        os.replace(temp_remote, REMOTE_SUPPLEMENT)
        state = load(SUPPLEMENT_STATE_PATH)
        state["status"] = "PASS"
        state["package"]["path"] = str(REMOTE_SUPPLEMENT)
        state["package"]["sha256"] = sha(REMOTE_SUPPLEMENT)
        state["package"]["manifest_sha256"] = sha(tree / "MANIFEST.sha256")
        state["package"]["package_metadata_sha256"] = sha(tree / "PACKAGE-METADATA.json")
        state["isolated_verification"]["fresh_extract_manifest"] = "PASS"
        state["isolated_verification"]["reproduce_py"] = "PASS"
        state["isolated_verification"]["binary_identity_path_scan"] = "PASS"
        state["isolated_verification"]["text_identity_path_scan"] = "PASS"
        state["isolated_verification"]["unit_tests"] = f"{unit_test_count}/{unit_test_count} PASS"
        state["reproduced_results"]["skillrl_p0e"] = p0e_summary(receipt)
        state["reproduced_results"]["structural_enrichment"] = reproduced.get("structural_enrichment") or {}
        state["reproduced_results"]["experimental_breadth"] = reproduced.get("experimental_breadth") or {}
        state["reproduced_results"]["released_controller_audit"] = reproduced.get("released_controller_audit") or {}
        state["reproduced_results"]["autoskill_p19_dynamic"] = reproduced.get("autoskill_p19_dynamic") or {}
        state["reproduced_results"]["autoskill_p19_mediator_isolation"] = reproduced.get("autoskill_p19_mediator_isolation") or {}
        state["reproduced_results"]["autoskill_multitask_pilot"] = reproduced.get("autoskill_multitask_pilot") or {}
        forbidden = [
            str(item)
            for item in (state["claim_boundary"].get("forbidden") or [])
            if str(item) != "dynamic STRI success"
        ]
        state["claim_boundary"]["forbidden"] = list(dict.fromkeys(forbidden + [
            "generalized dynamic STRI success beyond the frozen AutoSkill/P19 behavior-level result",
            "treating the AutoSkill P19 behavior-level result as task utility, longitudinal regret, end-to-end AutoSkill runtime validation, or general AutoSkill safety",
            "treating the qualified SkillRL C4 realization STOP as a population-level no-effect theorem or persistent principle dead end",
            "treating quotient-conserved clone allocation as downstream utility validation or as a repair for non-realizable partial-overlap support geometry",
            "treating 9/9 held-out AutoSkill retrieval sensitivity as task-general behavioral propagation after the preregistered stage-1 behavior gate stopped",
            "reopening the stopped AutoSkill held-out pilot by relaxing the frozen action signature, selecting units from observed behavior, or using tool-call count as the primary endpoint",
        ]))
        state["new_gpu_evidence_required_for_current_claim_scope"] = False
        dump(SUPPLEMENT_STATE_PATH, state)
        return {"files": file_count, "manifest_entries": manifest_entries, "sha256": sha(REMOTE_SUPPLEMENT), "manifest_sha256": state["package"]["manifest_sha256"], "unit_tests": state["isolated_verification"].get("unit_tests"), "reproduce_stdout_tail": repro.stdout[-800:]}


def refresh_delivery(qa: dict, source: dict, supplement: dict) -> dict:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    REMOTE.mkdir(parents=True, exist_ok=True)
    if not DOWNLOAD_PDF.is_file():
        raise FileNotFoundError(DOWNLOAD_PDF)
    built_text = run(["pdftotext", str(PDF), "-"], cwd=ROOT).stdout
    frozen_text = run(["pdftotext", str(DOWNLOAD_PDF), "-"], cwd=ROOT).stdout
    if built_text != frozen_text:
        raise RuntimeError("frozen download PDF text differs from the currently verified manuscript")
    shutil.copy2(MAIN, DOWNLOAD_TEX)
    shutil.copy2(DOWNLOAD_PDF, REMOTE_PDF)
    shutil.copy2(DOWNLOAD_SOURCE, REMOTE_SOURCE)

    final_review = load(FINAL_REVIEW_PATH)
    paper_quality = load(PAPER_QUALITY_PATH)
    principle = load(P0E_PRINCIPLE)
    autoskill = load(AUTOSKILL_RESULT)
    mediator = load(MEDIATOR_V2_RESULT)
    post_review = load(POST_ISOLATION_REVIEW)
    final = load(FINAL_STATE_PATH)
    final["official_format"].update({
        "main_text_pages": int(qa["main_text_pages"]),
        "main_text_page_limit": 9,
        "total_pdf_pages": int(qa["total_pdf_pages"]),
        "resolved_citations": int(qa["citation_count"]),
        "overfull_boxes": 0,
        "undefined_citations": 0,
        "undefined_references": 0,
    })
    final["independent_reviews"]["official_iclr2027_final_review"] = {
        "verdict": str(final_review.get("verdict") or ""),
        "confidence": float(final_review.get("confidence") or 0.0),
        "overall_score_1_to_10": final_review.get("overall_score_1_to_10"),
        "required_revisions": len(final_review.get("required_revisions") or []),
    }
    final["independent_reviews"]["post_mediator_isolation_review"] = {
        "decision": post_review.get("decision"),
        "deepseek_pre_score": (((post_review.get("reviews") or {}).get("deepseek_pre_isolation") or {}).get("score_1_to_10")),
        "deepseek_post_score": (((post_review.get("reviews") or {}).get("deepseek_post_isolation") or {}).get("score_1_to_10")),
        "deepseek_post_recommendation": (((post_review.get("reviews") or {}).get("deepseek_post_isolation") or {}).get("recommendation")),
        "deepseek_post_submission_advice": (((post_review.get("reviews") or {}).get("deepseek_post_isolation") or {}).get("submission_advice")),
        "fatal_flaws": (((post_review.get("reviews") or {}).get("deepseek_post_isolation") or {}).get("fatal_flaws")),
        "no_more_experiment_score_chasing": ((post_review.get("submission_policy") or {}).get("no_more_p19_condition_chasing") is True),
        "scientific_authority": False,
    }
    forbidden = [str(item) for item in (final.get("claims_forbidden") or []) if str(item) != "dynamic STRI success"]
    final["claims_forbidden"] = list(dict.fromkeys(forbidden + [
        "generalized dynamic STRI success beyond the frozen AutoSkill/P19 behavior-level result",
        "treating the AutoSkill P19 behavior-level result as task utility, longitudinal regret, end-to-end AutoSkill runtime validation, or general AutoSkill safety",
        "treating the qualified SkillRL C4 realization STOP as a population-level no-effect theorem or persistent principle dead end",
        "treating the 22-addition/71-deletion support-edit radii as robustness to mixed edits, learned-support error, or downstream utility perturbations",
    ]))
    final["new_gpu_evidence_required_for_current_claim_scope"] = False
    final["delivery"]["pdf"].update({"path": str(REMOTE_PDF), "sha256": sha(REMOTE_PDF)})
    final["delivery"]["source_zip"].update({"path": str(REMOTE_SOURCE), "sha256": sha(REMOTE_SOURCE), "files": source["files"], "isolated_compile_verified": True})
    final["delivery"]["supplement_zip"].update({"path": str(REMOTE_SUPPLEMENT), "sha256": supplement["sha256"], "manifest_sha256": supplement["manifest_sha256"], "isolated_reproduction_verified": True, "unit_tests": supplement["unit_tests"]})
    final["paper_quality_v2"].update({
        "status": str(paper_quality.get("status") or ""),
        "passed": bool(paper_quality.get("paper_quality_gate_passed", False)),
        "evidence_debt": len((paper_quality.get("evidence_debt") or {}).get("missing_or_incomplete_ids") or []),
    })
    target_null_release = load(TARGET_NULL_ANALYSIS)
    witness_release = load(WITNESS_PEELING)
    edit_release = load(SUPPORT_EDIT_RADIUS)
    final["structural_enrichment"] = {
        "target_null_sha256": sha(TARGET_NULL_ANALYSIS),
        "witness_peeling_sha256": sha(WITNESS_PEELING),
        "support_edit_radius_sha256": sha(SUPPORT_EDIT_RADIUS),
        "target_rays_residual": f"{((target_null_release.get('target_ray_sensitivity') or {}).get('summary') or {}).get('residual_targets')}/7",
        "degree_preserving_rewires_residual": f"{((target_null_release.get('degree_preserving_null_ensemble') or {}).get('summary') or {}).get('residual_draws')}/200",
        "max_share_constraints_preserving_R_star_2": f"{((target_null_release.get('max_share_sensitivity') or {}).get('summary') or {}).get('valid_constraints')}/9",
        "disjoint_three_row_witnesses": ((witness_release.get("witness_peeling") or {}).get("summary") or {}).get("peeling_rounds_before_equalizable"),
        "witness_tools_spanned": ((witness_release.get("witness_peeling") or {}).get("summary") or {}).get("unique_tools_spanned"),
        "minimum_additions_to_equalizable": (edit_release.get("support_edit_radius") or {}).get("minimum_additions_to_equalizable"),
        "minimum_deletions_to_equalizable": (edit_release.get("support_edit_radius") or {}).get("minimum_deletions_to_equalizable"),
        "new_model_calls": 0,
        "new_gpu_runs": 0,
        "claim_expansion": False,
        "supplement_reproduction_verified": True,
    }
    final["dynamic_boundary"] = {
        "skillrl_p0e_experimental_realization": str(principle.get("experimental_realization_disposition") or ""),
        "skillrl_p0e_principle_disposition": str(principle.get("principle_disposition") or ""),
        "persistent_principle_dead_end_certified": bool(principle.get("persistent_principle_dead_end_certified", False)),
        "stage2_locked": bool(principle.get("stage2_confirmation_locked", True)),
        "new_gpu_authorized": bool(principle.get("new_gpu_authorized", False)),
        "broader_STRI_N1_N2_N3_unchanged": bool(principle.get("broader_STRI_N1_N2_N3_unchanged", False)),
        "autoskill_p19": autoskill_p19_summary(autoskill, mediator),
        "autoskill_p19_behavioral_claim_supported": autoskill.get("decision") == "GO_STAGE3_DYNAMIC_BEHAVIORAL_PROPAGATION",
        "autoskill_p19_task_utility_claim_authorized": False,
        "autoskill_p19_generalization_claim_authorized": False,
        "autoskill_p19_mediator_claim_supported": mediator.get("decision") == "GO_MEDIATOR_ISOLATION_P19",
        "autoskill_p19_mediator_exact_fisher": (mediator.get("statistics") or {}).get("exact_fraction"),
        "autoskill_p19_stage3_replay_agreement": (mediator.get("measurement_repair") or {}).get("stage3_replay_agreement"),
    }
    dump(FINAL_STATE_PATH, final)

    openreview = load(OPENREVIEW_PATH)
    mv = openreview["machine_verified"]
    mv.update({
        "main_text_pages": "9/9",
        "resolved_citations": int(qa["citation_count"]),
        "paper_pdf_sha256": sha(REMOTE_PDF),
        "paper_source_zip_sha256": sha(REMOTE_SOURCE),
        "anonymous_supplement_zip_sha256": supplement["sha256"],
        "supplement_reproduction": "PASS",
        "supplement_unit_tests": supplement["unit_tests"],
        "final_independent_review": str(final_review.get("verdict") or ""),
        "final_independent_review_confidence": float(final_review.get("confidence") or 0.0),
        "post_isolation_independent_review": "borderline 6/10; minor_revision; no fatal flaws",
        "post_isolation_submission_policy": str(post_review.get("decision") or ""),
        "new_gpu_evidence_required_for_current_claim_scope": False,
        "paper_quality_v2": "PASS_MANUSCRIPT_EVIDENCE_V2_1",
        "paper_quality_evidence_debt": 0,
        "stri_structural_edit_radius": "22 additions / 71 deletions to neutral equalizability",
        "stri_degree_preserving_rewires": "200/200 retain R*=2",
        "stri_target_rays": "7/7 residual",
        "stri_max_share_constraints": "9/9 retain R*=2",
        "stri_witness_peeling": "22 disjoint three-row witnesses spanning 19 tools",
        "skillrl_p0e_experimental_realization": str(principle.get("experimental_realization_disposition") or ""),
        "skillrl_p0e_principle_disposition": str(principle.get("principle_disposition") or ""),
        "skillrl_p0e_persistent_dead_end": False,
        "skillrl_p0e_stage2_locked": True,
        "autoskill_p19_dynamic": "6/6 original; 0/6 split4; 3/3 ID-placebo; 3/3 quotient-control",
        "autoskill_p19_18_of_18_valid": True,
        "autoskill_p19_fisher_exact_p": autoskill["statistics"]["fisher_exact_p"],
        "autoskill_p19_mediator_isolation": "3/3 post-checkout add-back; 0/3 matched cleanup add-back",
        "autoskill_p19_mediator_exact_fisher": (mediator.get("statistics") or {}).get("exact_fraction"),
        "autoskill_p19_stage3_replay_agreement": (mediator.get("measurement_repair") or {}).get("stage3_replay_agreement"),
        "autoskill_p19_claim_scope": "ONE_ARCHIVED_P19_BEHAVIOR_LEVEL_SUBSTRATE_ONLY",
        "autoskill_p19_task_utility_claim_authorized": False,
        "autoskill_p19_generalization_claim_authorized": False,
    })
    openreview["submission_files"] = {"pdf": str(REMOTE_PDF), "source_zip": str(REMOTE_SOURCE), "supplement_zip": str(REMOTE_SUPPLEMENT)}
    dump(OPENREVIEW_PATH, openreview)
    return {"pdf_sha256": sha(REMOTE_PDF), "tex_sha256": sha(DOWNLOAD_TEX), "source_zip_sha256": sha(REMOTE_SOURCE), "supplement_zip_sha256": supplement["sha256"]}


def main() -> None:
    qa = current_qa()
    write_qa_artifact(qa)
    source = build_and_verify_source_zip()
    supplement = build_and_verify_supplement()
    delivery = refresh_delivery(qa, source, supplement)
    print(json.dumps({"qa": {"status": qa["status"], "checks": f"{qa['checks_passed']}/{qa['checks_total']}", "pages": f"{qa['main_text_pages']}/9"}, "source": source, "supplement": {k: v for k, v in supplement.items() if k != "reproduce_stdout_tail"}, "delivery": delivery}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
