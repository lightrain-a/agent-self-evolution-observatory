#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from research_pipeline.paper_acceptance import paper_contract_digest
from research_pipeline.paper_acceptance_ledger import (
    _append,
    load_paper_ledger,
    public_paper_ledger_summary,
    record_review_learning,
    validate_paper_ledger,
)

PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
REVISION_ID = "C1-STAGE-SIGNATURE-R6-CLAIM-PROVENANCE-SEAL-20260828"
EXPECTED_CONTRACT_SHA256 = "c6cd6e451dd5a7a610ef89f7b2e4ce3e54a70fb568889c6304c33e66dc50bd0e"
EXPECTED = {
    "claim_audit": "715721a221a2bfb942fffa43c65aba52f1754ce3d1f99006f13bc32ef4b6e332",
    "claim_runner": "7e4bde4dafdecb9d2fa0d39e98e889382dd47661c78ab7d33c997bcad0eb5743",
    "claim_registry": "ad034d2da0bc99af0506aca1686c9adb5e8247875fb10a3de5b63cda1397cfbc",
    "r4_review": "0db9ae6b5e8735aba2a49d9c96417b3df93c7ad02c50a714ebb394c4cbe7b824",
    "sensitivity": "f1bc7555674d1a7c363d05054cf55ffc686e148cf4f5b1fc24bf7a4002b55bba",
}
LESSON_CODES = (
    "measurement-boundary-coarsening-test",
    "operational-localization-not-causal-onset",
    "bundled-writer-intervention-not-atom-pure",
    "scope-stage-boundary-to-measured-substrate",
    "stopped-method-no-behavioral-efficacy",
    "method-extension-stop-does-not-negate-measurement-result",
    "claim-audit-needs-replayable-content-addressed-provenance",
)
LESSON_SOURCE_REFS = tuple(
    f"artifact:sha256:{EXPECTED[key]}" for key in ("r4_review", "sensitivity", "claim_audit")
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def contract() -> Any:
    script = HERE / "reopen_c1_stage_resolved_contract.py"
    spec = importlib.util.spec_from_file_location("c1_r6_contract", script)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load C1 stage-resolved contract")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    value = module.contract()
    require(paper_contract_digest(value) == EXPECTED_CONTRACT_SHA256, "C1 R6 contract digest drift")
    return value


def verify_local_provenance() -> dict[str, str]:
    files = {
        "claim_audit": HERE / "claim-audit-r6-provenance-seal-20260828.json",
        "claim_runner": HERE / "run_claim_audit_r6.py",
        "claim_registry": HERE / "claim-audit-r6-registry-20260828.json",
        "r4_review": HERE / "mock-pc-r4-adversarial-review-20260826.json",
        "sensitivity": HERE / "stage-evidence-sensitivity-audit-20260826.json",
    }
    actual = {key: sha(path) for key, path in files.items()}
    require(actual == EXPECTED, f"C1 R6 provenance hash drift: {actual}")
    cas = {
        "artifact": HERE / "provenance" / "sha256" / f"{EXPECTED['claim_audit']}.json",
        "runner": HERE / "provenance" / "runners" / "sha256" / f"{EXPECTED['claim_runner']}.py",
        "registry": HERE / "provenance" / "registries" / "sha256" / f"{EXPECTED['claim_registry']}.json",
    }
    require(cas["artifact"].read_bytes() == files["claim_audit"].read_bytes(), "claim-audit CAS artifact drift")
    require(cas["runner"].read_bytes() == files["claim_runner"].read_bytes(), "claim-audit CAS runner drift")
    require(cas["registry"].read_bytes() == files["claim_registry"].read_bytes(), "claim-audit CAS registry drift")
    payload = json.loads(files["claim_audit"].read_text(encoding="utf-8"))
    require(payload.get("status") == "PASS", "claim audit is not PASS")
    require((payload.get("summary") or {}) == {"claims_failed": 0, "claims_passed": 35, "claims_total": 35}, "claim audit is not exactly 35/35")
    return {key: str(path.relative_to(PROJECT_ROOT)) for key, path in cas.items()}


def latest_current_contract_audit(row: dict[str, Any]) -> dict[str, Any]:
    for event in reversed(row.get("events") or []):
        if not isinstance(event, dict) or event.get("event_type") != "claim-audit-r6":
            continue
        if event.get("contract_sha256") not in (None, "", EXPECTED_CONTRACT_SHA256):
            continue
        return event
    return {}


def integrate(root: Path, *, apply: bool) -> dict[str, Any]:
    cas = verify_local_provenance()
    c = contract()
    row = load_paper_ledger(root, PAPER_ID)
    require(bool(row), "canonical C1 paper ledger is missing")
    require(row.get("contract_sha256") == EXPECTED_CONTRACT_SHA256, "canonical C1 contract does not match R6")
    require(not validate_paper_ledger(row), "canonical C1 ledger is invalid before integration")

    already = any(
        isinstance(event, dict)
        and event.get("event_type") == "claim-audit-r6"
        and event.get("artifact_ref") == f"artifact:sha256:{EXPECTED['claim_audit']}"
        and event.get("pass") is True
        and int(event.get("checks") or 0) == 35
        and int(event.get("passed") or 0) == 35
        for event in row.get("events") or []
    )
    if apply and not already:
        row = _append(
            root,
            c,
            "c1-r6-claim-provenance-hardening-20260828",
            {
                "event_type": "claim-audit-r6",
                "revision_id": REVISION_ID,
                "contract_sha256": EXPECTED_CONTRACT_SHA256,
                "pass": True,
                "checks": 35,
                "passed": 35,
                "blockers": [],
                "artifact_ref": f"artifact:sha256:{EXPECTED['claim_audit']}",
                "runner_ref": f"artifact:sha256:{EXPECTED['claim_runner']}",
                "registry_ref": f"artifact:sha256:{EXPECTED['claim_registry']}",
                "content_addressed": True,
                "deterministic_replay_required": True,
            },
        )
    if apply:
        row = record_review_learning(
            root,
            c,
            lesson_codes=LESSON_CODES,
            source_refs=LESSON_SOURCE_REFS,
            actor="c1-r6-review-learning-20260828",
        )

    require(not validate_paper_ledger(row), "canonical C1 ledger is invalid after integration")
    latest = latest_current_contract_audit(row)
    public = public_paper_ledger_summary(row)
    learning = public.get("review_learning") or {}
    audit_ok = latest.get("artifact_ref") == f"artifact:sha256:{EXPECTED['claim_audit']}" and latest.get("pass") is True and int(latest.get("checks") or 0) == 35 and int(latest.get("passed") or 0) == 35
    lessons_ok = set(learning.get("lesson_codes") or []) == set(LESSON_CODES) and int(learning.get("structured_lesson_receipts") or 0) >= 1
    require(audit_ok if apply or already else True, "canonical ledger does not point at the hardened R6 claim audit")
    require(lessons_ok if apply else True, "canonical ledger does not expose the structured R6 review lesson")
    return {
        "status": "INTEGRATED" if apply else ("ALREADY_INTEGRATED" if already and lessons_ok else "READY_TO_INTEGRATE"),
        "paper_id": PAPER_ID,
        "revision_id": REVISION_ID,
        "contract_sha256": EXPECTED_CONTRACT_SHA256,
        "claim_audit_sha256": EXPECTED["claim_audit"],
        "claim_audit_35_of_35": audit_ok,
        "claim_audit_cas": cas,
        "review_learning_sha256": next((str((event.get("receipt") or {}).get("review_learning_sha256") or "") for event in reversed(row.get("events") or []) if isinstance(event, dict) and event.get("event_type") == "review-learning"), ""),
        "structured_lesson_codes": sorted(learning.get("lesson_codes") or []),
        "ledger_events": len(row.get("events") or []),
        "ledger_validation_errors": [],
        "new_scientific_provider_calls": 0,
        "new_gpu_scientific_runs": 0,
        "new_scientific_experiments": 0,
        "authority": {"scientific": False, "experiment": False, "gpu": False, "submission": False},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Idempotently integrate the provenance-hardened C1 R6 audit and structured review lesson into the append-only canonical paper ledger")
    parser.add_argument("--root", type=Path, default=Path("/data/wyt/agent-self-evolution-observatory"))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    print(json.dumps(integrate(args.root, apply=args.apply), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
