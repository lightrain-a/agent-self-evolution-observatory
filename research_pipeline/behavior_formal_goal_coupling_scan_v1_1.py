from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

from .behavior_formal_goal_coupling_v1_1 import analyze_goal_state
from .behavior_formal_goal_coupling_distribution import (
    MAX_ABS_COUPLING_SIZE_SPEARMAN,
    MAX_BRANCH_BEARING_TASK_FRACTION,
    MAX_DOMINANT_VALUE_FRACTION,
    MIN_NONTRIVIAL_TASKS,
    summarize_distribution,
)

SCHEMA_VERSION = "behavior-formal-goal-coupling-structure-scan-v1.1-post-gate-repair"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _load_official_parser(runtime_root: Path):
    sys.path.insert(0, str(runtime_root))
    try:
        return importlib.import_module("bddl.parsing").parse_problem
    finally:
        sys.path.pop(0)


def _assert_frozen_contract(qualification: dict[str, Any], project_root: Path) -> dict[str, str]:
    original_metric_path = project_root / "research_pipeline" / "behavior_formal_goal_coupling.py"
    metric_path = project_root / "research_pipeline" / "behavior_formal_goal_coupling_v1_1.py"
    distribution_path = project_root / "research_pipeline" / "behavior_formal_goal_coupling_distribution.py"
    expected_original = str(qualification["frozen_pre_scan_qualification"]["metric_v1_sha256"])
    actual_original = _sha(original_metric_path)
    if actual_original != expected_original:
        raise ValueError(f"original frozen v1 metric drift:{actual_original}!={expected_original}")
    expected_metric = str(qualification["repair_v1_1"]["metric_sha256"])
    actual_metric = _sha(metric_path)
    if actual_metric != expected_metric:
        raise ValueError(f"frozen v1.1 repair metric drift:{actual_metric}!={expected_metric}")
    frozen = qualification["frozen_distribution_gates"]
    expected_thresholds = {
        "min_nontrivial_tasks_atomic_goal_count_ge_2": MIN_NONTRIVIAL_TASKS,
        "max_dominant_value_fraction_atomic_goal_count": MAX_DOMINANT_VALUE_FRACTION,
        "max_dominant_value_fraction_shared_argument_edge_count": MAX_DOMINANT_VALUE_FRACTION,
        "max_abs_spearman_edges_vs_atomic_goal_count": MAX_ABS_COUPLING_SIZE_SPEARMAN,
        "max_branch_bearing_task_fraction": MAX_BRANCH_BEARING_TASK_FRACTION,
    }
    for key, expected in expected_thresholds.items():
        if frozen.get(key) != expected:
            raise ValueError(f"frozen distribution threshold drift:{key}:{frozen.get(key)}!={expected}")
    return {
        "original_v1_metric_sha256": actual_original,
        "metric_v1_1_sha256": actual_metric,
        "distribution_gate_sha256": _sha(distribution_path),
    }


def scan_activity_definitions(
    *,
    activity_root: Path,
    parser_runtime: Path,
    qualification_path: Path,
    source_revision: str,
) -> dict[str, Any]:
    project_root = Path(__file__).resolve().parents[1]
    qualification = json.loads(qualification_path.read_text(encoding="utf-8"))
    frozen_code = _assert_frozen_contract(qualification, project_root)
    if qualification.get("status") != "ALLOW_ONE_POST_GATE_OPERATIONALIZATION_REPAIR_QUALIFICATION":
        raise ValueError("v1.1 repair qualification status mismatch")
    if qualification.get("policy_results_read") is not False or qualification.get("policy_result_access_authorized") is not False:
        raise ValueError("v1.1 repair qualification must remain zero-outcome")
    parse_problem = _load_official_parser(parser_runtime)

    files = sorted(activity_root.glob("*/problem*.bddl"))
    if not files:
        raise ValueError("no BEHAVIOR activity problem files found")
    rows: list[dict[str, Any]] = []
    parser_errors: list[dict[str, str]] = []
    manifest: list[dict[str, Any]] = []
    for path in files:
        raw = path.read_bytes()
        rel = str(path.relative_to(activity_root))
        manifest.append({"path": rel, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        try:
            text = raw.decode("utf-8")
            _, objects, _, goal_state = parse_problem(
                path.parent.name,
                0,
                "behavior-1k",
                predefined_problem=text,
            )
            metrics = analyze_goal_state(goal_state, object_map=objects)
            rows.append({
                "activity": path.parent.name,
                "problem_file": path.name,
                "source_sha256": manifest[-1]["sha256"],
                **{key: value for key, value in metrics.items() if key != "schema_version"},
            })
        except Exception as error:
            parser_errors.append({
                "activity": path.parent.name,
                "problem_file": path.name,
                "error_type": type(error).__name__,
                "error": str(error)[:500],
            })

    summary = summarize_distribution(rows, parser_error_tasks=len(parser_errors))
    status = "STRUCTURE_DISTRIBUTION_PASS_AWAITING_INDEPENDENT_REVIEW" if summary["gates"]["pass"] else "STRUCTURE_DISTRIBUTION_HOLD"
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "provisional_key": qualification["provisional_key"],
        "new_canonical_id_required": True,
        "parent_candidate_id": "PORT-010",
        "parent_may_be_reopened": False,
        "status": status,
        "scientific_authority": False,
        "execution_authority": False,
        "policy_result_access_authorized": False,
        "policy_results_read": False,
        "task_distribution_inspected": True,
        "source": {
            "repo": qualification["source"]["repo"],
            "tag": qualification["source"]["tag"],
            "revision": source_revision,
            "activity_root": str(activity_root),
            "problem_file_count": len(files),
            "problem_manifest_sha256": _canonical_sha(manifest),
        },
        "repair_qualification_sha256": qualification["qualification_sha256"],
        "first_v1_hold_receipt_sha256": qualification["first_structure_scan_hold"]["receipt_sha256"],
        "repair_kind": "ONE_POST_GATE_SOURCE_SCHEMA_GROUNDING_OPERATIONALIZATION_REPAIR",
        "no_further_repair_from_this_distribution": True,
        "frozen_code": frozen_code,
        "distribution_summary": summary,
        "parser_errors": parser_errors,
        "task_structure_rows": rows,
        "next_gate": (
            "independent post-rerun review of the exact v1.1 repair receipt before any policy-result access"
            if summary["gates"]["pass"]
            else "HOLD/STOP fresh formal-goal-coupling lane; no further repair from this distribution and no policy-result access"
        ),
    }
    receipt["receipt_sha256"] = _canonical_sha({key: value for key, value in receipt.items() if key != "receipt_sha256"})
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="Single v1.1 post-gate repair scan of BEHAVIOR BDDL formal goal structure without policy results")
    parser.add_argument("--activity-root", type=Path, required=True)
    parser.add_argument("--parser-runtime", type=Path, required=True)
    parser.add_argument("--qualification", type=Path, required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("v1.1 repair structure receipt already exists; single rerun contract forbids overwrite/rerun")
    receipt = scan_activity_definitions(
        activity_root=args.activity_root,
        parser_runtime=args.parser_runtime,
        qualification_path=args.qualification,
        source_revision=args.source_revision,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "receipt_sha256": receipt["receipt_sha256"],
        "policy_results_read": receipt["policy_results_read"],
        "problem_file_count": receipt["source"]["problem_file_count"],
        "distribution_gates": receipt["distribution_summary"]["gates"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
