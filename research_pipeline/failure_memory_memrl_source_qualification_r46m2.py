#!/usr/bin/env python3
"""Strict R46 adjudication for the R45-M1 replacement lineage.

The original R46 implementation counts eligible retrieval support across all 40
(primary + utilization) representatives.  Frozen R43 is stricter: every one of
the 32 primary confirmatory clusters must retain at least one eligible frozen
retrieval before any validation treatment outcome is opened.  This zero-outcome
adapter preserves R46 retrieval bytes and only corrects that adjudication.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

try:
    from . import failure_memory_memrl_source_qualification_r46m1 as base
    from .failure_memory_memrl_source_execute_r45m1 import _digest, _load, _sha, _verify_receipt_hash
except ImportError:
    import failure_memory_memrl_source_qualification_r46m1 as base  # type: ignore
    from failure_memory_memrl_source_execute_r45m1 import _digest, _load, _sha, _verify_receipt_hash  # type: ignore

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
STATUS_PASS = "SOURCE_QUALIFICATION_PASS_RETRIEVAL_FROZEN_VALIDATION_STILL_SEALED"
STATUS_STOP = "SUPPORT_STOP_SOURCE_QUALIFICATION_FAILED_NO_VALIDATION_TREATMENT"
ROLE = "R46M2_STRICT_PRIMARY_SUPPORT_ADJUDICATION_ZERO_VALIDATION_OUTCOME"


def strict_adjudicate(base_receipt: dict[str, Any], frozen: dict[str, Any]) -> dict[str, Any]:
    if base_receipt.get("paper_id") != PAPER_ID or frozen.get("paper_id") != PAPER_ID:
        raise RuntimeError("paper-id-drift")
    if not _verify_receipt_hash(base_receipt) or not _verify_receipt_hash(frozen):
        raise RuntimeError("receipt-hash-drift")
    if int(base_receipt.get("validation_treatment_outcomes_observed") or 0) != 0:
        raise RuntimeError("validation-outcome-already-opened")
    if int(frozen.get("validation_treatment_outcomes_observed") or 0) != 0:
        raise RuntimeError("frozen-retrieval-opened-validation")

    rows = list(frozen.get("rows") or [])
    primary = [r for r in rows if r.get("cohort") == "primary"]
    utilization = [r for r in rows if r.get("cohort") == "utilization"]
    if len(primary) != 32 or len(utilization) != 8 or len(rows) != 40:
        raise RuntimeError("frozen-retrieval-cohort-shape-drift")

    primary_supported = [r for r in primary if bool(r.get("has_eligible_frozen_retrieval"))]
    utilization_supported = [r for r in utilization if bool(r.get("has_eligible_frozen_retrieval"))]
    primary_all = len(primary_supported) == 32
    both = base_receipt.get("both_source_provenance_polarities_retrievable") is True
    passed = primary_all and both

    out = dict(base_receipt)
    out.update({
        "role": ROLE,
        "status": STATUS_PASS if passed else STATUS_STOP,
        "base_r46_receipt_sha256": base_receipt.get("receipt_sha256"),
        "base_r46_file_semantics": "diagnostic retrieval construction; strict R43 primary-support adjudication supersedes its >=32/40 aggregate pass rule",
        "primary_confirmatory_clusters": 32,
        "primary_clusters_with_eligible_frozen_retrieval": len(primary_supported),
        "all_32_primary_clusters_supported": primary_all,
        "utilization_clusters": 8,
        "utilization_clusters_with_eligible_frozen_retrieval": len(utilization_supported),
        "utilization_support_is_diagnostic_until_R47_preflight": True,
        "strict_R43_support_rule": "32/32 primary confirmatory clusters each have >=1 eligible frozen retrieval AND both source provenance polarities are retrievable",
        "utilization_execution_authorized_by_this_receipt": passed,
        "primary_confirmatory_execution_authorized_by_this_receipt": False,
        "validation_environment_resets": 0,
        "validation_evaluator_calls": 0,
        "validation_treatment_outcomes_observed": 0,
        "failure_route": None if passed else "SUPPORT_STOP_NO_BEHAVIORAL_VERDICT",
        "next_action": "RUN_ONLY_THE_FROZEN_8_CLUSTER_UTILIZATION_QUALIFICATION" if passed else "STOP_WITHOUT_OPENING_ANY_VALIDATION_TREATMENT",
        "scientific_authority": False,
    })
    out.pop("receipt_sha256", None)
    out["receipt_sha256"] = _digest(out)
    return out


def build(manifest: pathlib.Path, source_receipt: pathlib.Path, completed: pathlib.Path, outdir: pathlib.Path) -> dict[str, Any]:
    base_result = base.build(manifest, source_receipt, completed, outdir)
    frozen_path = pathlib.Path(str(base_result.get("frozen_retrieval_path") or ""))
    frozen = _load(frozen_path)
    strict = strict_adjudicate(base_result, frozen)
    path = outdir / "source-qualification-strict-r46m2-receipt.json"
    path.write_text(json.dumps(strict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if _sha(path) == "":
        raise RuntimeError("strict-receipt-write-failed")
    return strict


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=pathlib.Path, required=True)
    p.add_argument("--source-receipt", type=pathlib.Path, required=True)
    p.add_argument("--completed-ledger", type=pathlib.Path, required=True)
    p.add_argument("--output-dir", type=pathlib.Path, required=True)
    a = p.parse_args()
    r = build(a.manifest.resolve(), a.source_receipt.resolve(), a.completed_ledger.resolve(), a.output_dir.resolve())
    print(json.dumps({
        "status": r["status"],
        "primary_clusters_with_eligible_frozen_retrieval": r["primary_clusters_with_eligible_frozen_retrieval"],
        "all_32_primary_clusters_supported": r["all_32_primary_clusters_supported"],
        "utilization_clusters_with_eligible_frozen_retrieval": r["utilization_clusters_with_eligible_frozen_retrieval"],
        "both_source_provenance_polarities_retrievable": r["both_source_provenance_polarities_retrievable"],
        "validation_treatment_outcomes_observed": 0,
        "receipt_sha256": r["receipt_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
