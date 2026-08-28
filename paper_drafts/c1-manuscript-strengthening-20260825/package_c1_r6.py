#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = HERE / "source"
OUT_PDF = HERE / "C1-stage-resolved-r6-final.pdf"
OUT_ZIP = HERE / "C1-stage-resolved-r6-final-source.zip"
OUT_MANIFEST = HERE / "c1-r6-package-manifest-20260828.json"
SUPPLEMENT = HERE / "C1-stage-resolved-r6-final-supplement.zip"
SUPPLEMENT_RUNNER = HERE / "package_c1_r6_supplement.py"
CLAIM_RUNNER = HERE / "run_claim_audit_r6.py"
CLAIM_AUDIT = HERE / "claim-audit-r6-provenance-seal-20260828.json"
SENSITIVITY = HERE / "stage-evidence-sensitivity-audit-20260826.json"
STAGE = HERE / "stage-evidence-ladder-analysis-20260825.json"
SOURCE_DATE_EPOCH = "1787875200"  # 2026-08-28T00:00:00Z; fixed for reproducible PDF metadata.

SOURCE_FILES = (
    "main.tex", "references.bib", "iclr2027_conference.sty", "iclr2027_conference.bst",
    "fancyhdr.sty", "natbib.sty", "build_figures.py", "build_stage_transport_figure.py",
    "sections/00_abstract.tex", "sections/01_intro.tex", "sections/02_mechanism.tex",
    "sections/03_f0.tex", "sections/03a_prompt_control.tex", "sections/04_variance_protocol.tex",
    "sections/05_related.tex", "sections/06_limitations_conclusion.tex", "sections/07_appendix.tex",
    "figures/fig1_reward_write_channel.pdf", "figures/fig2_write_and_prompt_control.pdf",
    "figures/fig3_downstream_variance.pdf", "figures/fig4_stage_resolved_transport.pdf",
)

EXPECTED = {
    "contract": "c6cd6e451dd5a7a610ef89f7b2e4ce3e54a70fb568889c6304c33e66dc50bd0e",
    "claim_audit": "f4eeeaef2999dffa70b3cf6139dc0811bbb3d50464bb91d738e1cdc94458290c",
    "sensitivity": "f1bc7555674d1a7c363d05054cf55ffc686e148cf4f5b1fc24bf7a4002b55bba",
    "stage": "d3c5341d1d6064cac5b7f8164c72af77433ef10d79d35338806f0784be49effa",
    "pdf": "c71fec522756ebceed75dff8fd168f178bd7d843e5d33f992fc1f5d6b96f4d70",
    "source_zip": "1b39471799d0ae3efc41b4e42a5b744efc7d82c9e2efce82eeea80dd7085872b",
    "supplement": "c32ba76812af24c515176810bf67506cadcf46068e3a4c46333e65e68e4bde64",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    proc = subprocess.run(args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(args)}\n{proc.stdout[-4000:]}")
    return proc.stdout


def main() -> None:
    for rel in SOURCE_FILES:
        if not (SRC / rel).is_file():
            raise RuntimeError(f"missing R6 source file: {rel}")
    for path in (CLAIM_RUNNER, CLAIM_AUDIT, SENSITIVITY, STAGE):
        if not path.is_file():
            raise RuntimeError(f"missing R6 evidence input: {path}")
    if sha(CLAIM_AUDIT) != EXPECTED["claim_audit"]:
        raise RuntimeError("claim-audit SHA drift")
    if sha(SENSITIVITY) != EXPECTED["sensitivity"]:
        raise RuntimeError("sensitivity SHA drift")
    if sha(STAGE) != EXPECTED["stage"]:
        raise RuntimeError("stage-evidence SHA drift")
    replay = run([sys.executable, str(CLAIM_RUNNER), "--check"], cwd=HERE)
    if '"status": "REPLAY_PASS"' not in replay:
        raise RuntimeError("35/35 claim audit is not replayable on the R6 source")

    env = dict(os.environ)
    env["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    for cmd in (
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        ["bibtex", "main"],
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
    ):
        run(cmd, cwd=SRC, env=env)
    shutil.copyfile(SRC / "main.pdf", OUT_PDF)

    fixed_date = (2026, 8, 28, 0, 0, 0)
    with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for rel in sorted(SOURCE_FILES):
            data = (SRC / rel).read_bytes()
            info = zipfile.ZipInfo(rel, date_time=fixed_date)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    if sha(OUT_PDF) != EXPECTED["pdf"] or sha(OUT_ZIP) != EXPECTED["source_zip"]:
        raise RuntimeError("R6 sealed PDF/source hash drift")
    run([sys.executable, str(SUPPLEMENT_RUNNER)], cwd=HERE)
    if not SUPPLEMENT.is_file() or sha(SUPPLEMENT) != EXPECTED["supplement"]:
        raise RuntimeError("R6 supplement projection hash drift")

    source_hashes = {rel: sha(SRC / rel) for rel in sorted(SOURCE_FILES)}
    payload = {
        "schema_version": "1.0",
        "artifact_type": "c1-r6-paper-only-package-manifest",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "revision_id": "C1-STAGE-SIGNATURE-R6-CLAIM-PROVENANCE-SEAL-20260828",
        "title": "Memory Divergence Is Not Behavioral Divergence: Stage-Resolved Transport in Self-Improving Agent Memory",
        "contract_sha256": EXPECTED["contract"],
        "status": "R6_PAPER_ONLY_PACKAGE_SEALED",
        "paper_only_revision": True,
        "scientific_contract_changed": False,
        "scientific_results_changed": False,
        "claim_expansion": False,
        "artifacts": {
            "pdf": {"path": str(OUT_PDF.relative_to(ROOT)), "sha256": sha(OUT_PDF)},
            "source_zip": {"path": str(OUT_ZIP.relative_to(ROOT)), "sha256": sha(OUT_ZIP)},
            "supplement_zip": {"path": str(SUPPLEMENT.relative_to(ROOT)), "sha256": sha(SUPPLEMENT)},
            "claim_audit": {"path": str(CLAIM_AUDIT.relative_to(ROOT)), "sha256": EXPECTED["claim_audit"], "replay": "35/35 PASS", "revision": "R6"},
            "sensitivity_audit": {"path": str(SENSITIVITY.relative_to(ROOT)), "sha256": EXPECTED["sensitivity"]},
            "stage_evidence": {"path": str(STAGE.relative_to(ROOT)), "sha256": EXPECTED["stage"]},
        },
        "source_files": source_hashes,
        "build": {
            "source_date_epoch": SOURCE_DATE_EPOCH,
            "latex_sequence": ["pdflatex", "bibtex", "pdflatex", "pdflatex"],
            "source_zip_fixed_timestamp": "2026-08-28T00:00:00Z",
            "source_zip_files": len(SOURCE_FILES),
        },
        "execution": {
            "new_scientific_provider_calls": 0,
            "new_gpu_scientific_runs": 0,
            "new_scientific_experiments": 0,
            "network_required": False,
        },
        "authority": {"scientific": False, "experiment": False, "provider": False, "gpu": False, "submission": False},
    }
    payload["manifest_sha256"] = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    OUT_MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "pdf_sha256": sha(OUT_PDF), "source_zip_sha256": sha(OUT_ZIP), "manifest_sha256": payload["manifest_sha256"], "claim_audit": "REPLAY_PASS"}, sort_keys=True))


if __name__ == "__main__":
    main()
