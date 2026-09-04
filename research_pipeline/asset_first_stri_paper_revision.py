from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT

SCHEMA_VERSION = "asset-first-stri-paper-revision-v1"
REVISION_ID = "stri-e1-paper-revision-20260904-skillzip-reframe"
OUTPUT_REL = "generated/asset-first-stri-paper-revision-20260904.json"
PARENT_FINAL_REL = "generated/asset-first-stri-iclr2027-final-state-20260816.json"
PARENT_QUALITY_REL = "generated/asset-first-stri-paper-quality-v2-20260816.json"
COHERENCE_REL = "generated/asset-first-stri-narrow-paper-coherence-20260816.json"
SUPPLEMENT_REL = "downloads/STRI-ICLR2027-supplement.zip"

SOURCE_ARTIFACTS = [
    "paper_drafts/stri-20260816-iclr2027-main.tex",
    "paper_drafts/stri-20260816-narrow-body.tex",
    "paper_drafts/stri-20260816-tables.tex",
    "paper_drafts/stri-20260816-references.bib",
    "paper_drafts/stri-20260816-sources.json",
    "paper_drafts/stri-20260816-outline.md",
    "paper_drafts/stri-20260816-paper-qa.py",
    "paper_drafts/stri-20260816-iclr2027-qa.py",
]
DELIVERY = {
    "tex": "downloads/STRI-ICLR2027.tex",
    "pdf": "downloads/STRI-ICLR2027.pdf",
    "source_zip": "downloads/STRI-ICLR2027-source.zip",
    "supplement_zip": SUPPLEMENT_REL,
}

AUTHORITY = {
    "scientific_claims": False,
    "method": False,
    "experiment": False,
    "p0": False,
    "gpu": False,
    "canonical_problem_gate": False,
    "canonical_generator": False,
    "canonical_queue": False,
    "manuscript_delivery": True,
}


def _sha(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _run_json(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stdout}\n{proc.stderr}")
    try:
        value = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"command did not return JSON: {' '.join(cmd)}\n{proc.stdout}\n{proc.stderr}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"command returned non-object JSON: {' '.join(cmd)}")
    return value


def _latex_env() -> dict[str, str]:
    env = dict(os.environ)
    env["TEXINPUTS"] = ".:iclr2027-official//:"
    env["BSTINPUTS"] = ".:iclr2027-official//:"
    env["BIBINPUTS"] = ".:"
    return env


def _compile_main(project_root: Path) -> None:
    paper = project_root / "paper_drafts"
    env = _latex_env()
    main = "stri-20260816-iclr2027-main.tex"
    commands = [
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", main],
        ["bibtex", "stri-20260816-iclr2027-main"],
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", main],
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", main],
    ]
    for cmd in commands:
        proc = subprocess.run(cmd, cwd=paper, env=env, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"manuscript compile failed: {' '.join(cmd)}\n{proc.stdout}\n{proc.stderr}")


def _pdf_text_sha(path: Path) -> str:
    text = subprocess.check_output(["pdftotext", str(path), "-"], text=True)
    normalized = "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").splitlines()).strip() + "\n"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _source_zip_bindings(project_root: Path) -> dict[str, bool]:
    mapping = {
        "stri-20260816-iclr2027-main.tex": "paper_drafts/stri-20260816-iclr2027-main.tex",
        "stri-20260816-narrow-body.tex": "paper_drafts/stri-20260816-narrow-body.tex",
        "stri-20260816-tables.tex": "paper_drafts/stri-20260816-tables.tex",
        "stri-20260816-references.bib": "paper_drafts/stri-20260816-references.bib",
    }
    result: dict[str, bool] = {}
    with zipfile.ZipFile(project_root / DELIVERY["source_zip"]) as archive:
        names = set(archive.namelist())
        for arc, rel in mapping.items():
            result[rel] = arc in names and hashlib.sha256(archive.read(arc)).hexdigest() == _sha(project_root / rel)
    return result


def _independent_source_compile(project_root: Path) -> dict[str, Any]:
    source_zip = project_root / DELIVERY["source_zip"]
    with tempfile.TemporaryDirectory(prefix="stri-revision-source-") as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(source_zip) as archive:
            archive.extractall(tmp_path)
        main = "stri-20260816-iclr2027-main.tex"
        commands = [
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", main],
            ["bibtex", "stri-20260816-iclr2027-main"],
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", main],
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", main],
        ]
        for cmd in commands:
            proc = subprocess.run(cmd, cwd=tmp_path, text=True, capture_output=True, check=False)
            if proc.returncode != 0:
                return {"status": "FAIL", "command": cmd, "stderr": proc.stderr[-4000:]}
        pdf = tmp_path / "stri-20260816-iclr2027-main.pdf"
        log = (tmp_path / "stri-20260816-iclr2027-main.log").read_text(encoding="utf-8", errors="replace")
        info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
        total_pages = -1
        for line in info.splitlines():
            if line.startswith("Pages:"):
                total_pages = int(line.split(":", 1)[1].strip())
                break
        return {
            "status": "PASS",
            "total_pdf_pages": total_pages,
            "no_overfull_boxes": "Overfull" not in log,
            "no_undefined_citations": "undefined citations" not in log.lower(),
            "no_undefined_references": "undefined references" not in log.lower(),
            "pdf_sha256": _sha(pdf),
            "pdf_text_sha256": _pdf_text_sha(pdf),
        }


def build_asset_first_stri_paper_revision(
    project_root: Path = PROJECT_ROOT,
    *,
    compile_manuscript: bool = True,
    visual_status: str = "PENDING_MANUAL_VISUAL_REVIEW",
    visual_pages: list[int] | None = None,
) -> dict[str, Any]:
    if compile_manuscript:
        _compile_main(project_root)

    paper_qa = _run_json(
        ["python3", "stri-20260816-paper-qa.py"], cwd=project_root / "paper_drafts"
    )
    iclr_qa = _run_json(
        ["python3", "stri-20260816-iclr2027-qa.py"], cwd=project_root / "paper_drafts"
    )
    source_compile = _independent_source_compile(project_root)
    source_zip_bindings = _source_zip_bindings(project_root)

    parent_final = _load(project_root / PARENT_FINAL_REL)
    parent_quality = _load(project_root / PARENT_QUALITY_REL)
    coherence = _load(project_root / COHERENCE_REL)
    claims = coherence.get("claims") if isinstance(coherence.get("claims"), dict) else {}
    inherited_claims = {
        claim_id: str((claims.get(claim_id) or {}).get("status") or "UNKNOWN")
        for claim_id in ("N1", "N2", "N3")
    }

    source_sha = {rel: _sha(project_root / rel) for rel in SOURCE_ARTIFACTS}
    delivery_sha = {key: _sha(project_root / rel) for key, rel in DELIVERY.items()}
    main_source_sha = _sha(project_root / "paper_drafts/stri-20260816-iclr2027-main.tex")
    active_tex_sha = delivery_sha["tex"]
    source_compile_matches_download = (
        source_compile.get("total_pdf_pages") == 12
        and source_compile.get("pdf_text_sha256") == _pdf_text_sha(project_root / DELIVERY["pdf"])
    )

    status = "READY_PAPER_REVISION" if (
        paper_qa.get("status") == "PASS"
        and int(paper_qa.get("checks_passed") or 0) == int(paper_qa.get("checks_total") or -1)
        and iclr_qa.get("status") == "PASS"
        and int(iclr_qa.get("checks_passed") or 0) == int(iclr_qa.get("checks_total") or -1)
        and int(iclr_qa.get("main_text_pages") or 99) <= int(iclr_qa.get("main_text_page_limit") or 0)
        and source_compile.get("status") == "PASS"
        and source_compile.get("no_overfull_boxes") is True
        and source_compile.get("no_undefined_citations") is True
        and source_compile.get("no_undefined_references") is True
        and source_compile_matches_download
        and all(source_zip_bindings.values())
        and main_source_sha == active_tex_sha
        and all(len(v) == 64 for v in source_sha.values())
        and all(len(v) == 64 for v in delivery_sha.values())
        and all(inherited_claims.get(k) == "SUPPORTED" for k in ("N1", "N2", "N3"))
    ) else "HOLD_PAPER_REVISION"

    return {
        "schema_version": SCHEMA_VERSION,
        "paper_id": "STRI",
        "revision_id": REVISION_ID,
        "status": status,
        "date": "2026-09-04",
        "purpose": "manuscript architecture and delivery revision after SkillZip/SkillZip Pro methodology review; no scientific claim expansion",
        "parent": {
            "official_final_state": {"path": PARENT_FINAL_REL, "sha256": _sha(project_root / PARENT_FINAL_REL)},
            "paper_quality_v2": {"path": PARENT_QUALITY_REL, "sha256": _sha(project_root / PARENT_QUALITY_REL)},
            "inherited_claims": inherited_claims,
        },
        "scope": {
            "paper_architecture_only": True,
            "scientific_execution": False,
            "new_evidence": False,
            "claim_expansion": False,
            "claims_unchanged": True,
            "future_iterative_agent_p0_required_for_current_claim": False,
            "skillzip_methods_adopted": False,
            "skillzip_methodology_and_writing_lessons_used": True,
        },
        "revision_summary": {
            "runtime_object": "A_theta(H_t,U_t,P_t^(r),B_t,xi_t)->E_t^(r); compare phi(E_t^(r))",
            "experiment_story": "RQ1 local access -> RQ2 structural boundary -> RQ3 bounded downstream propagation + held-out STOP",
            "claim_boundary": "behavioral propagation beyond P19 is not established",
            "related_work_added": ["SkillZip arXiv:2608.11079", "SkillZip Pro arXiv:2608.30785"],
            "supporting_analyses_demoted_to_supplement": ["factor-2 witness visualization", "structural robustness figure", "external graph analogue rows"],
        },
        "source_artifacts": {rel: {"sha256": source_sha[rel], "bytes": (project_root / rel).stat().st_size} for rel in SOURCE_ARTIFACTS},
        "delivery": {
            key: {"path": rel, "sha256": delivery_sha[key], "bytes": (project_root / rel).stat().st_size}
            for key, rel in DELIVERY.items()
        },
        "qa": {
            "scientific_paper": paper_qa,
            "iclr2027": iclr_qa,
            "independent_source_compile": source_compile,
            "source_compile_matches_active_pdf_text_and_pages": source_compile_matches_download,
            "source_zip_source_bindings": source_zip_bindings,
            "active_tex_matches_main_source": main_source_sha == active_tex_sha,
            "visual_inspection": {
                "status": visual_status,
                "pages": list(visual_pages or []),
                "scope": "layout/cropping/overlap/legibility only; no scientific authority",
            },
        },
        "independent_review": {
            "model": "GPT-5.6 Sol + Extra High via Oracle Browser",
            "verdicts": ["READY_NARROW_NO_NEW_EXPERIMENT", "KEEP_CURRENT_NARROW"],
            "future_p0_is_claim_expansion_only": True,
        },
        "scientific_authority": False,
        "authority": dict(AUTHORITY),
    }


def validate_asset_first_stri_paper_revision(
    state: dict[str, Any], project_root: Path = PROJECT_ROOT, *, require_visual_pass: bool = True
) -> list[str]:
    errors: list[str] = []
    if state.get("schema_version") != SCHEMA_VERSION:
        errors.append("paper revision schema mismatch")
    if state.get("paper_id") != "STRI" or state.get("revision_id") != REVISION_ID:
        errors.append("paper revision identity mismatch")
    if state.get("status") != "READY_PAPER_REVISION":
        errors.append("paper revision is not READY_PAPER_REVISION")
    if state.get("scientific_authority") is not False:
        errors.append("paper revision cannot carry scientific authority")
    authority = state.get("authority") or {}
    for key, expected in AUTHORITY.items():
        if authority.get(key) is not expected:
            errors.append(f"paper revision authority mismatch:{key}")

    scope = state.get("scope") or {}
    expected_scope = {
        "paper_architecture_only": True,
        "scientific_execution": False,
        "new_evidence": False,
        "claim_expansion": False,
        "claims_unchanged": True,
        "future_iterative_agent_p0_required_for_current_claim": False,
        "skillzip_methods_adopted": False,
        "skillzip_methodology_and_writing_lessons_used": True,
    }
    for key, expected in expected_scope.items():
        if scope.get(key) is not expected:
            errors.append(f"paper revision scope mismatch:{key}")

    parent = state.get("parent") or {}
    for key, rel in (("official_final_state", PARENT_FINAL_REL), ("paper_quality_v2", PARENT_QUALITY_REL)):
        row = parent.get(key) or {}
        if row.get("path") != rel or row.get("sha256") != _sha(project_root / rel):
            errors.append(f"paper revision parent binding drift:{key}")
    inherited = parent.get("inherited_claims") or {}
    if {key: inherited.get(key) for key in ("N1", "N2", "N3")} != {"N1": "SUPPORTED", "N2": "SUPPORTED", "N3": "SUPPORTED"}:
        errors.append("paper revision inherited claims drift")

    source_rows = state.get("source_artifacts") or {}
    if set(source_rows) != set(SOURCE_ARTIFACTS):
        errors.append("paper revision source artifact set drift")
    else:
        for rel in SOURCE_ARTIFACTS:
            row = source_rows.get(rel) or {}
            if row.get("sha256") != _sha(project_root / rel):
                errors.append(f"paper revision source digest drift:{rel}")

    delivery = state.get("delivery") or {}
    for key, rel in DELIVERY.items():
        row = delivery.get(key) or {}
        if row.get("path") != rel or row.get("sha256") != _sha(project_root / rel):
            errors.append(f"paper revision delivery digest drift:{key}")

    qa = state.get("qa") or {}
    paper_qa = qa.get("scientific_paper") or {}
    iclr_qa = qa.get("iclr2027") or {}
    source_compile = qa.get("independent_source_compile") or {}
    if paper_qa.get("status") != "PASS" or int(paper_qa.get("checks_passed") or 0) != int(paper_qa.get("checks_total") or -1):
        errors.append("paper revision scientific-paper QA failed")
    if iclr_qa.get("status") != "PASS" or int(iclr_qa.get("checks_passed") or 0) != int(iclr_qa.get("checks_total") or -1):
        errors.append("paper revision ICLR QA failed")
    if (int(iclr_qa.get("main_text_pages") or 99), int(iclr_qa.get("main_text_page_limit") or 0)) != (9, 9):
        errors.append("paper revision main-text page gate drift")
    if source_compile.get("status") != "PASS" or source_compile.get("no_overfull_boxes") is not True or source_compile.get("no_undefined_citations") is not True or source_compile.get("no_undefined_references") is not True:
        errors.append("paper revision independent source compile failed")
    if qa.get("source_compile_matches_active_pdf_text_and_pages") is not True:
        errors.append("paper revision source compile does not match active PDF text/pages")
    bindings = qa.get("source_zip_source_bindings") or {}
    if not bindings or not all(bindings.get(rel) is True for rel in bindings):
        errors.append("paper revision source zip is not bound to current manuscript sources")
    if qa.get("active_tex_matches_main_source") is not True:
        errors.append("paper revision active TeX does not match main source")
    visual = qa.get("visual_inspection") or {}
    if require_visual_pass and (visual.get("status") != "PASS" or not visual.get("pages")):
        errors.append("paper revision visual inspection is incomplete")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-compile", action="store_true")
    parser.add_argument("--visual-pass", action="store_true")
    parser.add_argument("--visual-pages", default="1,5,9")
    parser.add_argument("--output", default=OUTPUT_REL)
    args = parser.parse_args()
    pages = [int(value) for value in args.visual_pages.split(",") if value.strip()]
    state = build_asset_first_stri_paper_revision(
        PROJECT_ROOT,
        compile_manuscript=not args.no_compile,
        visual_status="PASS" if args.visual_pass else "PENDING_MANUAL_VISUAL_REVIEW",
        visual_pages=pages if args.visual_pass else [],
    )
    output = PROJECT_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    errors = validate_asset_first_stri_paper_revision(state, PROJECT_ROOT, require_visual_pass=args.visual_pass)
    print(json.dumps({"output": str(output), "status": state.get("status"), "validation_errors": errors}, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
