#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = HERE / "C1-stage-resolved-r5-evidence-supplement.zip"
OUT = HERE / "C1-stage-resolved-r6-final-supplement.zip"
VERIFY_NAME = "supplement/verify_current_supplement.py"
EXPECTED_PARENT = "92cd7e476d944a9ec8b3acb60b7aaf2d17d65f9a6d32fe50c145ef8040c79943"
PDF_SHA = "c71fec522756ebceed75dff8fd168f178bd7d843e5d33f992fc1f5d6b96f4d70"
SOURCE_SHA = "1b39471799d0ae3efc41b4e42a5b744efc7d82c9e2efce82eeea80dd7085872b"
CLAIM_AUDIT_SHA = "f4eeeaef2999dffa70b3cf6139dc0811bbb3d50464bb91d738e1cdc94458290c"
SENSITIVITY_SHA = "f1bc7555674d1a7c363d05054cf55ffc686e148cf4f5b1fc24bf7a4002b55bba"
TITLE = "Memory Divergence Is Not Behavioral Divergence: Stage-Resolved Transport in Self-Improving Agent Memory"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not PARENT.is_file() or sha(PARENT) != EXPECTED_PARENT:
        raise RuntimeError("historical C1 supplement parent drift")
    with zipfile.ZipFile(PARENT) as archive:
        members = {name: archive.read(name) for name in archive.namelist() if not name.endswith("/")}
    if VERIFY_NAME not in members:
        raise RuntimeError("historical supplement verifier missing")

    old_projection = json.loads(members["supplement/CURRENT-PROJECTION.json"].decode("utf-8"))
    projection = {
        "schema_version": "1.0",
        "receipt_type": "supplement-current-projection",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "revision": "r6",
        "current_title": TITLE,
        "current_pdf_sha256": PDF_SHA,
        "current_source_zip_sha256": SOURCE_SHA,
        "scientific_parent_supplement": "C1-stage-resolved-r5-evidence-supplement.zip",
        "scientific_parent_supplement_sha256": EXPECTED_PARENT,
        "retained_scientific_evidence": list((old_projection.get("curation") or {}).get("retained_scientific_evidence") or []),
        "retained_existing_data_diagnostics": list((old_projection.get("curation") or {}).get("added_postready_existing_data_diagnostics") or []),
        "r6_paper_only_evidence": {
            "claim_audit_sha256": CLAIM_AUDIT_SHA,
            "sensitivity_audit_sha256": SENSITIVITY_SHA,
            "claim_audit": "35/35 REPLAY_PASS",
            "scientific_values_changed": False,
            "claim_expansion": False,
        },
        "scientific_values_changed": False,
        "new_experiment": False,
        "claim_expansion": False,
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
        "submission_authority": False,
    }
    readme = """# Proxy Reward Memory Variance — R6 supplement projection

This archive preserves the frozen scientific evidence and existing-data diagnostics from the prior C1 supplement. R6 changes only the paper layer: it seals the stage-resolved manuscript, claim provenance, and page-compliant submission artifacts without changing scientific values or authorizing new experiments.

The scientific evidence files are byte-preserved from the historical supplement. The current R6 PDF/source hashes are recorded in CURRENT-PROJECTION.json; the replayable 35/35 claim audit and sensitivity audit remain repository artifacts outside this evidence archive.
"""
    members["supplement/CURRENT-PROJECTION.json"] = (json.dumps(projection, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    members["supplement/README.md"] = readme.encode("utf-8")

    fixed_date = (2026, 8, 28, 0, 0, 0)
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, date_time=fixed_date)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, members[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    with tempfile.TemporaryDirectory(prefix="c1-r6-supplement-") as td:
        td_path = Path(td)
        with zipfile.ZipFile(OUT) as archive:
            archive.extractall(td_path)
        proc = subprocess.run([sys.executable, str(td_path / VERIFY_NAME)], cwd=td_path / "supplement", text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if proc.returncode != 0 or "'pass': True" not in proc.stdout:
            raise RuntimeError("R6 supplement evidence verifier failed: " + proc.stdout[-2000:])

    print(json.dumps({"status": "R6_SUPPLEMENT_PROJECTION_PASS", "sha256": sha(OUT), "scientific_values_changed": False, "claim_expansion": False}, sort_keys=True))


if __name__ == "__main__":
    main()
