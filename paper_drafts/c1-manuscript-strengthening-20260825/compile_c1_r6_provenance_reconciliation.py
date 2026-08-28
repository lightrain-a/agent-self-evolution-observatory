#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = HERE / "source"
R5_PDF = HERE / "C1-stage-resolved-r5-review-repair.pdf"
R5_ZIP = HERE / "C1-stage-resolved-r5-review-repair-source.zip"
R5_RECHECK = HERE / "mock-pc-r4-targeted-repair-recheck-20260826.json"
R6_PDF = HERE / "C1-stage-resolved-r6-final.pdf"
R6_ZIP = HERE / "C1-stage-resolved-r6-final-source.zip"
R6_MANIFEST = HERE / "c1-r6-package-manifest-20260828.json"
SENSITIVITY = HERE / "stage-evidence-sensitivity-audit-20260826.json"
CLAIM_AUDIT = HERE / "claim-audit-r6-provenance-seal-20260828.json"
CLAIM_RUNNER = HERE / "run_claim_audit_r6.py"
OUT = HERE / "c1-r6-provenance-reconciliation-20260828.json"

EXPECTED = {
    "contract": "c6cd6e451dd5a7a610ef89f7b2e4ce3e54a70fb568889c6304c33e66dc50bd0e",
    "r5_pdf": "b38ed9c4397ad0b475649bbb9c5010304cbc4470d2e3096b28093f107ceb8f96",
    "r5_zip": "05429d5314907c4041ad4cdba5fb8c025cd46f8e5bebe474f57413415ac69c10",
    "r5_recheck": "4cf54f084d96a9079f46e3008acfd5489b6c478aff67a3421bd69cc5467bb3c5",
    "stale_sensitivity": "22ffb994b77a32b309da4d0bf945a3b5ad4fe43ce96476b11e5ecb98a1ea9ef0",
    "current_sensitivity": "f1bc7555674d1a7c363d05054cf55ffc686e148cf4f5b1fc24bf7a4002b55bba",
    "claim_audit": "715721a221a2bfb942fffa43c65aba52f1754ce3d1f99006f13bc32ef4b6e332",
    "r6_pdf": "c71fec522756ebceed75dff8fd168f178bd7d843e5d33f992fc1f5d6b96f4d70",
    "r6_zip": "1b39471799d0ae3efc41b4e42a5b744efc7d82c9e2efce82eeea80dd7085872b",
    "r6_manifest_file": "e969630c51c64cf75e97f435ff386dff6c4d35e711e2b9ec5b5ba1c219eff27f",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def run(args: list[str]) -> str:
    proc = subprocess.run(args, cwd=HERE, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(args)}\n{proc.stdout[-3000:]}")
    return proc.stdout


def zip_sha_map(path: Path) -> dict[str, str]:
    with zipfile.ZipFile(path) as archive:
        return {
            name: hashlib.sha256(archive.read(name)).hexdigest()
            for name in archive.namelist()
            if not name.endswith("/")
        }


def main() -> None:
    for path in (R5_PDF, R5_ZIP, R5_RECHECK, R6_PDF, R6_ZIP, R6_MANIFEST, SENSITIVITY, CLAIM_AUDIT, CLAIM_RUNNER):
        require(path.is_file(), f"missing provenance input: {path}")
    for key, path in (
        ("r5_pdf", R5_PDF), ("r5_zip", R5_ZIP), ("r5_recheck", R5_RECHECK),
        ("current_sensitivity", SENSITIVITY), ("claim_audit", CLAIM_AUDIT),
        ("r6_pdf", R6_PDF), ("r6_zip", R6_ZIP), ("r6_manifest_file", R6_MANIFEST),
    ):
        require(sha(path) == EXPECTED[key], f"{key} SHA drift")

    historical = load(R5_RECHECK)
    r6_manifest = load(R6_MANIFEST)
    claim_audit = load(CLAIM_AUDIT)
    require(str(historical.get("contract_sha256") or "") == EXPECTED["contract"], "R5 recheck contract drift")
    require(historical.get("status") == "TARGETED_REPAIR_RECHECK_PASS", "R5 repair disposition is not PASS")
    historical_sensitivity = str((historical.get("sensitivity_audit_binding") or {}).get("sha256") or "")
    require(historical_sensitivity == EXPECTED["stale_sensitivity"], "historical stale sensitivity binding changed")
    require(historical_sensitivity != EXPECTED["current_sensitivity"], "no sensitivity supersession exists")

    replay = run([sys.executable, str(CLAIM_RUNNER), "--check"])
    require('"status": "REPLAY_PASS"' in replay, "35/35 claim audit is not replayable")
    replay_payload = json.loads(replay.strip().splitlines()[-1])
    claim_cas = replay_payload.get("cas") or {}
    require(set(claim_cas) == {"artifact", "runner", "registry"}, "claim-audit CAS inventory drift")
    for key, rel in claim_cas.items():
        require((ROOT / str(rel)).is_file(), f"missing claim-audit CAS object: {key}={rel}")
    require(claim_audit.get("status") == "PASS", "claim audit status drift")
    require((claim_audit.get("summary") or {}) == {"claims_total": 35, "claims_passed": 35, "claims_failed": 0}, "claim audit summary drift")

    r5_zip_map = zip_sha_map(R5_ZIP)
    for row in historical.get("repaired_source_bindings") or []:
        full = str(row.get("path") or "")
        require("/source/" in full, f"unexpected historical source path: {full}")
        member = full.split("/source/", 1)[1]
        require(r5_zip_map.get(member) == str(row.get("sha256") or ""), f"R5 sealed ZIP does not reproduce historical repaired source: {member}")

    r6_zip_map = zip_sha_map(R6_ZIP)
    claim_inputs = {str(row.get("path") or ""): str(row.get("sha256") or "") for row in ((claim_audit.get("provenance") or {}).get("inputs") or [])}
    source_rows: list[dict[str, str]] = []
    for full, digest in sorted(claim_inputs.items()):
        prefix = "paper_drafts/c1-manuscript-strengthening-20260825/source/"
        if not full.startswith(prefix):
            continue
        member = full[len(prefix):]
        require(r6_zip_map.get(member) == digest, f"R6 source ZIP does not reproduce claim-audited source: {member}")
        require(sha(SRC / member) == digest, f"working R6 source does not reproduce claim audit: {member}")
        source_rows.append({"member": member, "sha256": digest})
    require(len(source_rows) >= 9, "too few claim-audited R6 source bindings")
    sensitivity_rel = str(SENSITIVITY.relative_to(ROOT))
    require(claim_inputs.get(sensitivity_rel) == EXPECTED["current_sensitivity"], "claim audit does not bind current sensitivity")

    require(r6_manifest.get("status") == "R6_PAPER_ONLY_PACKAGE_SEALED", "R6 package manifest status drift")
    require(r6_manifest.get("scientific_contract_changed") is False and r6_manifest.get("scientific_results_changed") is False, "R6 is not paper-only")
    artifacts = r6_manifest.get("artifacts") or {}
    require(str((artifacts.get("pdf") or {}).get("sha256") or "") == EXPECTED["r6_pdf"], "R6 manifest PDF binding drift")
    require(str((artifacts.get("source_zip") or {}).get("sha256") or "") == EXPECTED["r6_zip"], "R6 manifest source-ZIP binding drift")
    require(str((artifacts.get("claim_audit") or {}).get("sha256") or "") == EXPECTED["claim_audit"], "R6 manifest claim-audit binding drift")

    payload = {
        "schema_version": "1.0",
        "artifact_type": "c1-r6-provenance-reconciliation",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "contract_sha256": EXPECTED["contract"],
        "status": "R5_TO_R6_PROVENANCE_RECONCILED_PASS",
        "historical_r5": {
            "pdf_sha256": EXPECTED["r5_pdf"],
            "source_zip_sha256": EXPECTED["r5_zip"],
            "targeted_repair_recheck_sha256": EXPECTED["r5_recheck"],
            "repair_disposition_preserved": True,
            "stale_internal_sensitivity_sha256": EXPECTED["stale_sensitivity"],
            "stale_dependency_replayable_in_current_repository": False,
            "historical_bytes_rewritten": False,
            "final_claim_audited_revision": False,
        },
        "canonical_r6": {
            "pdf_sha256": EXPECTED["r6_pdf"],
            "source_zip_sha256": EXPECTED["r6_zip"],
            "package_manifest_file_sha256": EXPECTED["r6_manifest_file"],
            "sensitivity_sha256": EXPECTED["current_sensitivity"],
            "claim_audit_sha256": EXPECTED["claim_audit"],
            "claim_audit_replay": "35/35 PASS",
            "claim_audit_content_addressing": claim_cas,
            "claim_audited_source_bindings": source_rows,
            "paper_only_revision": True,
        },
        "adjudication": {
            "why_r6_is_required": "The sealed R5 PDF/source package predates paper-only source edits and final page-layout repair. R6 re-audits all 35 claims after those edits and seals PDF, source, sensitivity evidence, and claim audit into one deterministic revision.",
            "old_r5_recheck_not_used_as_complete_current_provenance": True,
            "r5_repair_disposition_retained": True,
            "scientific_contract_changed": False,
            "scientific_result_changed": False,
            "claim_expansion": False,
            "new_scientific_execution": False,
        },
        "authority": {"scientific": False, "experiment": False, "provider": False, "gpu": False, "submission": False},
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "r6_source_bindings": len(source_rows), "claim_audit": "REPLAY_PASS", "scientific_change": False}, sort_keys=True))


if __name__ == "__main__":
    main()
