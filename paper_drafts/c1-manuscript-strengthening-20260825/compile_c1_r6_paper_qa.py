#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = HERE / "source"
PDF = HERE / "C1-stage-resolved-r6-final.pdf"
SOURCE_ZIP = HERE / "C1-stage-resolved-r6-final-source.zip"
MANIFEST = HERE / "c1-r6-package-manifest-20260828.json"
PROVENANCE = HERE / "c1-r6-provenance-reconciliation-20260828.json"
PROVENANCE_RUNNER = HERE / "compile_c1_r6_provenance_reconciliation.py"
SENSITIVITY = HERE / "stage-evidence-sensitivity-audit-20260826.json"
STAGE = HERE / "stage-evidence-ladder-analysis-20260825.json"
CLAIM_AUDIT = HERE / "claim-audit-r6-provenance-seal-20260828.json"
CLAIM_RUNNER = HERE / "run_claim_audit_r6.py"
CLAIM_REGISTRY = HERE / "claim-audit-r6-registry-20260828.json"
OUT = HERE / "paper-qa-r6-provenance-reconciled-20260828.json"
SOURCE_DATE_EPOCH = "1787875200"

EXPECTED = {
    "pdf": "c71fec522756ebceed75dff8fd168f178bd7d843e5d33f992fc1f5d6b96f4d70",
    "source_zip": "1b39471799d0ae3efc41b4e42a5b744efc7d82c9e2efce82eeea80dd7085872b",
    "manifest_file": "6d0b0b21be4be841c9d1300145cfeaf06d5502a90cb26e8a60e33b434c9c8a76",
    "sensitivity": "f1bc7555674d1a7c363d05054cf55ffc686e148cf4f5b1fc24bf7a4002b55bba",
    "stage": "d3c5341d1d6064cac5b7f8164c72af77433ef10d79d35338806f0784be49effa",
    "claim_audit": "f4eeeaef2999dffa70b3cf6139dc0811bbb3d50464bb91d738e1cdc94458290c",
    "claim_runner": "51599cc126a5bf35e05f6ac956f4a24d6bd5c774f04458ed045288115d9727ee",
    "claim_registry": "ad034d2da0bc99af0506aca1686c9adb5e8247875fb10a3de5b63cda1397cfbc",
}

MANDATORY = (
    "citation-reference-consistency",
    "numeric-consistency",
    "figure-table-consistency",
    "forbidden-claim-detection",
    "anonymity",
    "page-constraint",
    "rendered-pdf-visual-qa",
    "artifact-hashes",
    "statement-evidence-binding",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    proc = subprocess.run(args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(args)}\n{proc.stdout[-4000:]}")
    return proc.stdout


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def first_meaningful_page_line(pdf: Path, page: int) -> str:
    raw = run(["pdftotext", "-f", str(page), "-l", str(page), "-layout", str(pdf), "-"])
    for line in raw.splitlines():
        s = " ".join(line.split())
        if not s or s.lower().startswith("under review as a conference paper") or re.fullmatch(r"\d+", s):
            continue
        return s
    return ""


def main() -> None:
    for path in (PDF, SOURCE_ZIP, MANIFEST, PROVENANCE_RUNNER, SENSITIVITY, STAGE, CLAIM_AUDIT, CLAIM_RUNNER, CLAIM_REGISTRY):
        if not path.is_file():
            raise RuntimeError(f"missing R6 QA input: {path}")

    run([sys.executable, str(PROVENANCE_RUNNER)], cwd=HERE)
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    if provenance.get("status") != "R5_TO_R6_PROVENANCE_RECONCILED_PASS":
        raise RuntimeError("R6 provenance reconciliation is not PASS")
    claim_replay = run([sys.executable, str(CLAIM_RUNNER), "--check"], cwd=HERE)
    if '"status": "REPLAY_PASS"' not in claim_replay:
        raise RuntimeError("R6 claim audit replay is not PASS")

    sections = "\n".join(text(path) for path in sorted((SRC / "sections").glob("*.tex")))
    lower = sections.lower()
    log = text(SRC / "main.log")
    aux = text(SRC / "main.aux")
    blg = text(SRC / "main.blg")
    sensitivity = json.loads(text(SENSITIVITY))
    stage = json.loads(text(STAGE))
    claim_audit = json.loads(text(CLAIM_AUDIT))
    manifest = json.loads(text(MANIFEST))

    hard_warning_patterns = ("undefined citations", "undefined references", "citation `", "reference `")
    citation_ok = not any(pat in log.lower() for pat in hard_warning_patterns) and "warning--" not in blg.lower()

    required_numeric = (
        "20/20", "0.673", "0.105", "0.0078", "0.15625", "0.00074",
        "125/172", "0.06944", "0.5801", "0/36", "0.02083", "0.4289", "34/36",
        "4/4", "0.125", "0.2253", "6/8",
    )
    numeric_ok = all(value in sections for value in required_numeric)

    required_labels = (
        "fig:write-control", "fig:stage-transport", "tab:evidence-ladder",
        "tab:alternative-audit", "tab:prompt-control-full", "tab:f2r1-cells",
    )
    figure_table_ok = all(f"\\newlabel{{{label}}}" in aux for label in required_labels) and "undefined" not in log.lower()

    forbidden = (
        "true causal bottleneck", "identified attenuation onset", "largest attenuation can occur",
        "first to distinguish retrieval", "first to separate retrieval from use", "first to separate retrieval from reuse",
        "reddit replicates the shopping evidence boundary",
    )
    forbidden_ok = not any(item in lower for item in forbidden)

    manuscript_files = [SRC / "main.tex", *sorted((SRC / "sections").glob("*.tex"))]
    manuscript_text = "\n".join(text(path) for path in manuscript_files)
    anonymity_ok = (
        "\\author{" not in manuscript_text
        and "\\iclrfinalcopy" not in manuscript_text.lower()
        and not re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", manuscript_text)
    )

    pdfinfo = run(["pdfinfo", str(PDF)])
    total_pages_match = re.search(r"^Pages:\s+(\d+)$", pdfinfo, re.MULTILINE)
    total_pages = int(total_pages_match.group(1)) if total_pages_match else 0
    refs_first = first_meaningful_page_line(PDF, 10).replace(" ", "").upper().startswith("REFERENCES")
    conclusion_on_nine = "CONCLUSION" in run(["pdftotext", "-f", "9", "-l", "9", "-layout", str(PDF), "-"]).replace(" ", "").upper()
    page_constraint_ok = total_pages == 13 and refs_first and conclusion_on_nine

    with tempfile.TemporaryDirectory(prefix="c1-r6-render-") as td:
        td_path = Path(td)
        run(["pdftoppm", "-png", "-r", "100", str(PDF), str(td_path / "page")])
        imgs = sorted(td_path.glob("page-*.png"))
        visual_ok = len(imgs) == total_pages
        visual_rows = []
        for image_path in imgs:
            im = Image.open(image_path).convert("L")
            w, h = im.size
            coords = []
            for y in range(0, h, 4):
                for x in range(0, w, 4):
                    if im.getpixel((x, y)) < 245:
                        coords.append((x, y))
            if not coords:
                visual_ok = False
                bbox = None
            else:
                xs = [x for x, _ in coords]; ys = [y for _, y in coords]
                bbox = [min(xs), min(ys), max(xs), max(ys)]
                if bbox[0] < 40 or bbox[2] > w - 40 or bbox[1] < 20 or bbox[3] > h - 20:
                    visual_ok = False
            visual_rows.append({"page": int(image_path.stem.split("-")[-1]), "size": [w, h], "sampled_nonwhite_bbox": bbox})
    font_lines = run(["pdffonts", str(PDF)]).splitlines()[2:]
    fonts_embedded = bool(font_lines) and all(
        re.search(r"\s+yes\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$", line) is not None
        for line in font_lines if line.strip()
    )
    visual_ok = visual_ok and fonts_embedded

    artifact_ok = (
        sha(PDF) == EXPECTED["pdf"]
        and sha(SOURCE_ZIP) == EXPECTED["source_zip"]
        and sha(MANIFEST) == EXPECTED["manifest_file"]
        and sha(SENSITIVITY) == EXPECTED["sensitivity"]
        and sha(STAGE) == EXPECTED["stage"]
        and sha(CLAIM_AUDIT) == EXPECTED["claim_audit"]
        and sha(CLAIM_RUNNER) == EXPECTED["claim_runner"]
        and sha(CLAIM_REGISTRY) == EXPECTED["claim_registry"]
        and provenance.get("canonical_r6", {}).get("pdf_sha256") == EXPECTED["pdf"]
        and provenance.get("canonical_r6", {}).get("source_zip_sha256") == EXPECTED["source_zip"]
    )

    statement_ok = (
        sensitivity.get("status") == "EVIDENCE_LOCALIZATION_SUPPORTED_LATENT_BOTTLENECK_NOT_IDENTIFIED"
        and sensitivity.get("identifiability", {}).get("latent_causal_attenuation_onset_is_identified") is False
        and sensitivity.get("exposure_semantics", {}).get("treatment_specific_residual_exposure_measured") is False
        and stage.get("status") == "SUPPORTED_ORDINAL_POST_EXPOSURE_PRE_UPTAKE_LOCALIZATION"
        and claim_audit.get("status") == "PASS"
        and (claim_audit.get("summary") or {}).get("claims_total") == 35
        and (claim_audit.get("summary") or {}).get("claims_passed") == 35
        and (claim_audit.get("summary") or {}).get("claims_failed") == 0
        and manifest.get("scientific_contract_changed") is False
        and manifest.get("scientific_results_changed") is False
        and "bundled writer-protocol intervention" in lower
        and "first unsupported measured native stage" in lower
        and "evidence-localization boundary" in lower
    )

    rebuild_byte_equal = False
    with tempfile.TemporaryDirectory(prefix="c1-r6-source-rebuild-") as td:
        td_path = Path(td)
        run(["unzip", "-q", str(SOURCE_ZIP), "-d", str(td_path)])
        env = dict(os.environ); env["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
        for command in (
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
            ["bibtex", "main"],
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        ):
            run(command, cwd=td_path, env=env)
        rebuilt = td_path / "main.pdf"
        rebuild_byte_equal = rebuilt.read_bytes() == PDF.read_bytes()
        artifact_ok = artifact_ok and rebuild_byte_equal

    checks = {
        "citation-reference-consistency": citation_ok,
        "numeric-consistency": numeric_ok,
        "figure-table-consistency": figure_table_ok,
        "forbidden-claim-detection": forbidden_ok,
        "anonymity": anonymity_ok,
        "page-constraint": page_constraint_ok,
        "rendered-pdf-visual-qa": visual_ok,
        "artifact-hashes": artifact_ok,
        "statement-evidence-binding": statement_ok,
    }
    if set(checks) != set(MANDATORY):
        raise RuntimeError("mandatory CI check set drift")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "c1-r6-paper-qa",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "revision_id": "C1-STAGE-SIGNATURE-R6-CLAIM-PROVENANCE-SEAL-20260828",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "summary": {
            "checks_passed": sum(checks.values()), "checks_total": len(checks),
            "total_pdf_pages": total_pages, "main_text_pages": 9, "main_text_page_limit": 9,
            "references_start_page": 10, "undefined_citations": 0 if citation_ok else None,
            "undefined_references": 0 if citation_ok else None,
            "overfull_boxes": 0 if "overfull" not in log.lower() else None,
            "rendered_pages": len(visual_rows), "fonts_embedded": fonts_embedded,
            "source_rebuild_byte_equal": rebuild_byte_equal,
            "claim_audit_replay_pass": True,
            "provenance_reconciliation_pass": True,
        },
        "bindings": {
            "pdf": {"path": str(PDF.relative_to(ROOT)), "sha256": sha(PDF)},
            "source_zip": {"path": str(SOURCE_ZIP.relative_to(ROOT)), "sha256": sha(SOURCE_ZIP)},
            "package_manifest": {"path": str(MANIFEST.relative_to(ROOT)), "sha256": sha(MANIFEST)},
            "provenance_reconciliation": {"path": str(PROVENANCE.relative_to(ROOT)), "sha256": sha(PROVENANCE)},
            "sensitivity_audit": {"path": str(SENSITIVITY.relative_to(ROOT)), "sha256": sha(SENSITIVITY)},
            "stage_evidence": {"path": str(STAGE.relative_to(ROOT)), "sha256": sha(STAGE)},
            "claim_audit": {"path": str(CLAIM_AUDIT.relative_to(ROOT)), "sha256": sha(CLAIM_AUDIT)},
            "claim_audit_replay": claim_replay.strip(),
        },
        "visual_sample": [row for row in visual_rows if row["page"] in {1, 9, 10, total_pages}],
        "execution": {"new_scientific_provider_calls": 0, "new_gpu_scientific_runs": 0, "new_scientific_experiments": 0, "network_required": False},
        "authority": {"scientific": False, "experiment": False, "provider": False, "gpu": False, "submission": False},
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks_passed": sum(checks.values()), "checks_total": len(checks), "source_rebuild_byte_equal": rebuild_byte_equal}, sort_keys=True))
    if payload["status"] != "PASS":
        raise RuntimeError("R6 paper QA failed: " + ",".join(k for k, v in checks.items() if not v))


if __name__ == "__main__":
    main()
