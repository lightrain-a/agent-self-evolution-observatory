#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = HERE / "source-r8"
PDF_OUT = HERE / "C1-stage-resolved-r8-negative-repair.pdf"
ZIP_OUT = HERE / "C1-stage-resolved-r8-negative-repair-source.zip"
QA_OUT = HERE / "paper-qa-r8-20260829.json"
MANIFEST_OUT = HERE / "c1-r8-package-manifest-20260829.json"
CLAIM_AUDIT = HERE / "claim-audit-r8-provenance-seal-20260829.json"
CLAIM_RUNNER = HERE / "run_claim_audit_r8.py"
CLAIM_REGISTRY = HERE / "claim-audit-r8-registry-20260829.json"
PILOT_CLOSURE = HERE / "c1-tgrp-pilot-closure-20260829.json"
PILOT_CLAIM_UPDATE = HERE / "c1-tgrp-pilot-claim-update-20260829.json"
THEORY = HERE / "c1-prerequisite-diagnostic-completeness-20260828.json"
R7_PDF = HERE / "C1-stage-resolved-r7-review-repair.pdf"
R7_ZIP = HERE / "C1-stage-resolved-r7-review-repair-source.zip"
SOURCE_DATE_EPOCH = "1787961600"  # 2026-08-29T00:00:00Z
FIXED_ZIP_TIME = (2026, 8, 29, 0, 0, 0)

SOURCE_FILES = [
    "build_figures.py",
    "build_stage_transport_figure.py",
    "fancyhdr.sty",
    "figures/fig1_reward_write_channel.pdf",
    "figures/fig2_write_and_prompt_control.pdf",
    "figures/fig3_downstream_variance.pdf",
    "figures/fig4_stage_resolved_transport.pdf",
    "iclr2027_conference.bst",
    "iclr2027_conference.sty",
    "main.tex",
    "natbib.sty",
    "references.bib",
    "sections/00_abstract.tex",
    "sections/01_intro.tex",
    "sections/02_mechanism.tex",
    "sections/03_f0.tex",
    "sections/03a_prompt_control.tex",
    "sections/04_variance_protocol.tex",
    "sections/05_related.tex",
    "sections/06_limitations_conclusion.tex",
    "sections/07_appendix.tex",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> str:
    p = subprocess.run(args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(args)}\n{p.stdout[-6000:]}")
    return p.stdout


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def make_zip() -> None:
    if ZIP_OUT.exists():
        ZIP_OUT.unlink()
    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in SOURCE_FILES:
            data = (SRC / rel).read_bytes()
            zi = zipfile.ZipInfo(rel, FIXED_ZIP_TIME)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            zf.writestr(zi, data)


def page_text(pdf: Path, page: int) -> str:
    return run(["pdftotext", "-f", str(page), "-l", str(page), "-layout", str(pdf), "-"], cwd=HERE)


def main() -> None:
    for rel in SOURCE_FILES:
        if not (SRC / rel).is_file():
            raise RuntimeError(f"missing source file: {rel}")

    claim = load(CLAIM_AUDIT)
    if claim.get("status") != "PASS" or claim.get("summary") != {"claims_total": 26, "claims_passed": 26, "claims_failed": 0}:
        raise RuntimeError("R8 claim audit is not 26/26 PASS")
    replay = run([sys.executable, str(CLAIM_RUNNER), "--check"], cwd=HERE)
    if '"status": "REPLAY_PASS"' not in replay:
        raise RuntimeError("R8 claim audit replay failed")

    env = dict(os.environ)
    env["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    with tempfile.TemporaryDirectory(prefix="c1-r8-build-") as td:
        build = Path(td)
        for rel in SOURCE_FILES:
            dst = build / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SRC / rel, dst)
        run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=build, env=env)
        biblog = run(["bibtex", "main"], cwd=build, env=env)
        run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=build, env=env)
        final_log_text = run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=build, env=env)
        final_pdf = build / "main.pdf"
        if not final_pdf.is_file():
            raise RuntimeError("clean R8 build produced no PDF")
        shutil.copy2(final_pdf, PDF_OUT)

    make_zip()

    info = run(["pdfinfo", str(PDF_OUT)], cwd=HERE)
    m = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
    pages = int(m.group(1)) if m else 0
    if pages != 12:
        raise RuntimeError(f"unexpected R8 page count: {pages}")

    lower_log = final_log_text.lower()
    hard_latex = ["undefined citations", "undefined references", "citation `", "reference `", "overfull \\hbox", "overfull \\vbox"]
    latex_clean = not any(x in lower_log for x in hard_latex)
    bib_clean = "warning--" not in biblog.lower() and "error" not in biblog.lower()

    p7 = page_text(PDF_OUT, 7)
    p8 = page_text(PDF_OUT, 8)
    p9 = page_text(PDF_OUT, 9)
    compact7 = re.sub(r"\s+", "", p7).upper()
    compact8 = re.sub(r"\s+", "", p8).upper()
    compact9 = re.sub(r"\s+", "", p9).upper()
    conclusion_heading_page7 = "CONCLUSION" in compact7
    conclusion_continues_page8 = "DIAGNOSISISNOTREPAIR" in compact8
    references_page8 = "REFERENCES" in compact8
    appendix_begins_page8 = "F0REPRODUCTIONDETAILS" in compact8
    appendix_continues_page9 = "MEMORYCONSTRUCTIONINTERVENTION" in compact9

    with tempfile.TemporaryDirectory(prefix="c1-r8-render-") as td:
        render = Path(td)
        run(["pdftoppm", "-png", "-r", "100", str(PDF_OUT), str(render / "page")], cwd=HERE)
        imgs = sorted(render.glob("page-*.png"))
        visual_ok = len(imgs) == pages
        bboxes = []
        for i, path in enumerate(imgs, start=1):
            im = Image.open(path).convert("L")
            w, h = im.size
            xs: list[int] = []
            ys: list[int] = []
            for y in range(0, h, 4):
                for x in range(0, w, 4):
                    if im.getpixel((x, y)) < 245:
                        xs.append(x); ys.append(y)
            if not xs:
                visual_ok = False
                bbox = None
            else:
                bbox = [min(xs), min(ys), max(xs), max(ys)]
                if bbox[0] < 35 or bbox[2] > w - 35 or bbox[1] < 18 or bbox[3] > h - 18:
                    visual_ok = False
            bboxes.append({"page": i, "size": [w, h], "sampled_nonwhite_bbox": bbox})

    fonts = run(["pdffonts", str(PDF_OUT)], cwd=HERE).splitlines()[2:]
    font_rows = [line for line in fonts if line.strip()]
    fonts_embedded = bool(font_rows) and all(re.search(r"\s+yes\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$", line) for line in font_rows)

    qa = {
        "schema_version": "1.0",
        "artifact_kind": "C1_R8_PAPER_QA",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "revision": "R8",
        "status": "PASS" if all([latex_clean, bib_clean, conclusion_heading_page7, conclusion_continues_page8, references_page8, appendix_begins_page8, appendix_continues_page9, visual_ok, fonts_embedded]) else "FAIL",
        "checks": {
            "claim_audit_replay": "26/26 PASS",
            "total_pdf_pages": pages,
            "main_text_with_conclusion_within_9_pages": conclusion_heading_page7 and conclusion_continues_page8,
            "references_begin_page_8": references_page8,
            "appendix_begins_page_8_after_references": appendix_begins_page8,
            "appendix_continues_page_9": appendix_continues_page9,
            "latex_undefined_or_overfull_warnings": 0 if latex_clean else 1,
            "bibtex_warnings": 0 if bib_clean else 1,
            "rendered_pages": len(bboxes),
            "render_margin_smoke": "PASS" if visual_ok else "FAIL",
            "fonts_embedded": fonts_embedded,
        },
        "render_bboxes": bboxes,
    }
    QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if qa["status"] != "PASS":
        raise RuntimeError(f"R8 QA failed: {qa['checks']}")

    pilot_closure = load(PILOT_CLOSURE)
    pilot_claim = load(PILOT_CLAIM_UPDATE)
    source_hashes = {rel: sha(SRC / rel) for rel in SOURCE_FILES}
    manifest = {
        "schema_version": "1.0",
        "artifact_type": "c1-r8-negative-repair-pilot-package-manifest",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "revision_id": "C1-STAGE-RESOLVED-R8-NEGATIVE-REPAIR-PILOT-20260829",
        "title": "Memory Divergence Is Not Behavioral Divergence: Stage-Resolved Transport in Self-Improving Agent Memory",
        "status": "R8_NEGATIVE_REPAIR_PILOT_PAPER_PACKAGE_SEALED",
        "source_base_revision": "R7",
        "source_base_pdf_sha256": sha(R7_PDF),
        "source_base_zip_sha256": sha(R7_ZIP),
        "scientific_results_changed": True,
        "scientific_contract_changed": False,
        "claim_expansion": False,
        "claim_narrowing": True,
        "new_scientific_evidence": {
            "experiment_id": pilot_closure["experiment_id"],
            "pilot_calls_complete": pilot_closure["execution"]["completed_scientific_provider_calls"],
            "pilot_failed_cases": pilot_closure["execution"]["failed_cases"],
            "pilot_gate_pass": pilot_closure["frozen_gate_result"]["pilot_gate_pass"],
            "repair_actionability": pilot_closure["adjudication"]["repair_actionability"],
            "confirmatory_full_executed": pilot_closure["execution"]["confirmatory_full_executed"],
            "confirmatory_holdout_new_calls": pilot_closure["execution"]["confirmatory_holdout_new_calls"],
            "claim_update_status": pilot_claim["primary_result"]["status"],
        },
        "execution": {
            "scientific_pilot_provider_calls": 312,
            "paper_build_provider_calls": 0,
            "new_gpu_scientific_runs": 0,
            "confirmatory_provider_calls": 0,
        },
        "build": {
            "latex_sequence": ["pdflatex", "bibtex", "pdflatex", "pdflatex"],
            "source_date_epoch": SOURCE_DATE_EPOCH,
            "source_zip_files": len(SOURCE_FILES),
            "source_zip_fixed_timestamp": "2026-08-29T00:00:00Z",
        },
        "artifacts": {
            "pdf": {"path": str(PDF_OUT.relative_to(HERE.parents[1])), "sha256": sha(PDF_OUT)},
            "source_zip": {"path": str(ZIP_OUT.relative_to(HERE.parents[1])), "sha256": sha(ZIP_OUT)},
            "claim_audit": {"path": str(CLAIM_AUDIT.relative_to(HERE.parents[1])), "sha256": sha(CLAIM_AUDIT), "replay": "26/26 PASS"},
            "paper_qa": {"path": str(QA_OUT.relative_to(HERE.parents[1])), "sha256": sha(QA_OUT)},
            "pilot_closure": {"path": str(PILOT_CLOSURE.relative_to(HERE.parents[1])), "sha256": sha(PILOT_CLOSURE)},
            "pilot_claim_update": {"path": str(PILOT_CLAIM_UPDATE.relative_to(HERE.parents[1])), "sha256": sha(PILOT_CLAIM_UPDATE)},
            "theory": {"path": str(THEORY.relative_to(HERE.parents[1])), "sha256": sha(THEORY)},
        },
        "source_files": source_hashes,
        "paper_boundary": "R8 preserves the W/E/U/O/F diagnostic result and operational post-exposure/pre-uptake localization, while adding the qualified negative pilot boundary: the tested explicit memory-use-check realization does not support diagnosis-guided repair actionability. The pilot is not confirmatory evidence and does not justify a broader repair-impossibility claim.",
        "authority": {"scientific_claim_expansion": False, "confirmatory_full": False, "new_repair_experiment": False, "provider": False, "gpu": False, "submission": False},
    }
    base = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    manifest["manifest_content_sha256_without_self"] = hashlib.sha256(base).hexdigest()
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": manifest["status"],
        "pdf_sha256": sha(PDF_OUT),
        "source_zip_sha256": sha(ZIP_OUT),
        "claim_audit": claim["summary"],
        "qa_status": qa["status"],
        "pages": pages,
        "confirmatory_full_executed": pilot_closure["execution"]["confirmatory_full_executed"],
    }, indent=2))

if __name__ == "__main__":
    main()
