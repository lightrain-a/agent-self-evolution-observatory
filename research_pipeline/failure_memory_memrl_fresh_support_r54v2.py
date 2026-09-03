#!/usr/bin/env python3
"""R54-v2: interface-only repair for full350 fresh support qualification.

R54-v1 stopped before any fresh retrieval because the R53 source manifest
intentionally freezes the full source universe by rule/hash rather than storing
an explicit 350-element ``selected_ids`` list, while the inherited service
builder expects that field.  This wrapper materializes the exact frozen IDs
from the already-hashed train split *in memory only* before calling that builder.
No source file, threshold, retrieval rule, validation unit, or treatment changes.
"""
from __future__ import annotations

import argparse
import copy
import json
import pathlib
from typing import Any

try:
    from . import failure_memory_memrl_fresh_support_r54 as v1
except ImportError:
    import failure_memory_memrl_fresh_support_r54 as v1  # type: ignore

INTERFACE_REVISION = "R54V2_IN_MEMORY_FULL350_ID_MATERIALIZATION"
_ORIGINAL_BUILDER = v1.r53._build_service_and_runner


def materialized_service_builder(manifest: dict[str, Any], outdir: pathlib.Path):
    runtime_manifest = copy.deepcopy(manifest)
    execution = runtime_manifest.get("execution_manifest") or {}
    source = execution.get("source") or {}
    source_build = execution.get("source_build") or {}
    split_path = pathlib.Path(str(source.get("checkout") or "")) / str(source_build.get("split") or "")
    if not split_path.is_file() or v1.r53._sha(split_path) != source_build.get("split_sha256"):
        raise RuntimeError("R54V2-source-split-drift")
    dataset = v1.r53._load(split_path)
    selected = v1.r53._materialize_full350_ids(dataset, source_build)
    source_build["selected_ids"] = selected
    execution["source_build"] = source_build
    runtime_manifest["execution_manifest"] = execution
    if len(selected) != 350 or v1._ids_hash(selected) != source_build.get("selected_ids_sha256"):
        raise RuntimeError("R54V2-materialized-source-id-drift")
    return _ORIGINAL_BUILDER(runtime_manifest, outdir)


def build(program_path: pathlib.Path, manifest_path: pathlib.Path, source_receipt_path: pathlib.Path,
          completed_path: pathlib.Path, old_evidence_path: pathlib.Path,
          qualification_contract_path: pathlib.Path, repair_contract_path: pathlib.Path,
          outdir: pathlib.Path) -> dict[str, Any]:
    repair = v1.r53._load(repair_contract_path)
    if repair.get("paper_id") != v1.PAPER_ID or not v1.r53._verify_receipt_hash(repair):
        raise RuntimeError("R54V2-repair-contract-invalid")
    bindings = repair.get("bindings") or {}
    if bindings.get("v1_qualification_contract_file_sha256") != v1.r53._sha(qualification_contract_path):
        raise RuntimeError("R54V2-v1-contract-binding-drift")
    if bindings.get("v2_runner_sha256") != v1.r53._sha(pathlib.Path(__file__).resolve()):
        raise RuntimeError("R54V2-runner-binding-drift")
    v1.r53._build_service_and_runner = materialized_service_builder
    result = v1.build(program_path, manifest_path, source_receipt_path, completed_path,
                      old_evidence_path, qualification_contract_path, outdir)
    out = dict(result)
    out.pop("receipt_sha256", None)
    out.update({
        "qualification_interface_revision": INTERFACE_REVISION,
        "R54_v1_result_admissible": False,
        "source_manifest_file_changed": False,
        "source_universe_changed": False,
        "retrieval_algorithm_changed": False,
        "retrieval_threshold_changed": False,
        "fresh_validation_rule_changed": False,
        "validation_environment_resets": 0,
        "validation_evaluator_calls": 0,
        "validation_treatment_outcomes_observed": 0,
    })
    out["receipt_sha256"] = v1.r53._digest({k: v for k, v in out.items() if k != "receipt_sha256"})
    (outdir / "fresh-support-qualification-r54v2-receipt.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--program-contract", type=pathlib.Path, required=True)
    p.add_argument("--source-manifest", type=pathlib.Path, required=True)
    p.add_argument("--source-receipt", type=pathlib.Path, required=True)
    p.add_argument("--completed-ledger", type=pathlib.Path, required=True)
    p.add_argument("--old-selection-evidence", type=pathlib.Path, required=True)
    p.add_argument("--qualification-contract", type=pathlib.Path, required=True)
    p.add_argument("--interface-repair-contract", type=pathlib.Path, required=True)
    p.add_argument("--output-dir", type=pathlib.Path, required=True)
    a = p.parse_args()
    r = build(a.program_contract.resolve(), a.source_manifest.resolve(), a.source_receipt.resolve(),
              a.completed_ledger.resolve(), a.old_selection_evidence.resolve(),
              a.qualification_contract.resolve(), a.interface_repair_contract.resolve(),
              a.output_dir.resolve())
    print(json.dumps({
        "status": r["status"],
        "qualification_interface_revision": r["qualification_interface_revision"],
        "eligible_fresh_cluster_count": r["eligible_fresh_cluster_count"],
        "primary_selected_count": r["primary_selected_count"],
        "utilization_selected_count": r["utilization_selected_count"],
        "both_source_provenance_polarities_retrievable": r["both_source_provenance_polarities_retrievable"],
        "validation_treatment_outcomes_observed": 0,
        "receipt_sha256": r["receipt_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
