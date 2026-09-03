from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.agent_constraint_externality_sq0_build import load_cases as load_v1_cases
from research_pipeline.agent_constraint_externality_sq0_v2r1_build import load_cases as load_v2r1_cases
from research_pipeline.agent_constraint_externality_sq0_v3_build import load_cases as load_v3_cases
from research_pipeline.agent_constraint_externality_sq0_v4_cases import build_cases
from research_pipeline.agent_constraint_externality_sq0_v4_oracle import TOOL_CALL_CAP, public_oracle
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OLD_F0_BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle"
V3_CLOSEOUT = GENERATED / "agent-constraint-externality-sq0-v3-closeout-20260903.json"
V3_ROOT_CAUSE = GENERATED / "agent-constraint-externality-sq0-v3-root-cause-20260903.json"
OUTPUT_BUNDLE = GENERATED / "agent-constraint-externality-sq0-v4-target-challenge-protected-20260903.bundle"
CONTRACT_OUTPUT = GENERATED / "agent-constraint-externality-sq0-v4-target-challenge-contract-20260903.json"
QUAL_OUTPUT = GENERATED / "agent-constraint-externality-sq0-v4-static-qualification-20260903.json"
SQ0_ID = "ACE-SQ0-V4-TNF-CALIBRATED-TARGET-CHALLENGE-20260903"
CASE_COUNT = 12


def _verified(path: Path, status: str) -> dict[str, Any]:
    x = json.loads(path.read_text(encoding="utf-8"))
    if x.get("object_id") != OBJECT_ID or x.get("status") != status:
        raise RuntimeError(f"Invalid prerequisite {path}")
    c = x.get("content_sha256"); u = dict(x); u.pop("content_sha256", None)
    if c != sha256_value(u):
        raise RuntimeError(f"Hash mismatch {path}")
    return x


def _pack(cases: list[dict[str, Any]]) -> None:
    from appworld.common.constants import PASSWORD, SALT
    from appworld.common.crypto import pack_bundle
    with tempfile.TemporaryDirectory(prefix="ace-sq0-v4-") as directory:
        root = Path(directory)
        p = root / "sq0v4" / "case_spec.json"
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps({"object_id": OBJECT_ID, "sq0_id": SQ0_ID, "cases": cases}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        pack_bundle(str(OUTPUT_BUNDLE), str(root), ["sq0v4"], PASSWORD, SALT, include_license=False)


def load_cases(path: Path = OUTPUT_BUNDLE) -> list[dict[str, Any]]:
    from appworld.common.constants import PASSWORD, SALT
    from appworld.common.crypto import bundle_file_path_to_content
    content = bundle_file_path_to_content(str(path), PASSWORD, SALT, include_file_paths=["sq0v4/case_spec.json"])
    spec = json.loads(content["sq0v4/case_spec.json"])
    if spec.get("object_id") != OBJECT_ID or spec.get("sq0_id") != SQ0_ID:
        raise RuntimeError("SQ0-V4 protected bundle identity mismatch.")
    return list(spec["cases"])


def _freshness(cases: list[dict[str, Any]]) -> dict[str, Any]:
    prior_sets = {
        "v1": load_v1_cases(),
        "v2r1": load_v2r1_cases(),
        "v3": load_v3_cases(),
    }
    old = load_protected_spec(OLD_F0_BUNDLE)
    prior_ids = {c["case_id"] for rows in prior_sets.values() for c in rows} | {f["family_id"] for f in old["families"]}
    prior_instruction_hashes = {sha256_value(c["task_instruction"]) for rows in prior_sets.values() for c in rows}
    prior_instruction_hashes |= {sha256_value(t) for f in old["families"] for t in [f["target_instruction"], *[a["task_instruction"] for a in f["arms"]]]}
    prior_fixture_hashes = {sha256_value(c["fixture"]) for rows in prior_sets.values() for c in rows}
    prior_resource_hashes = {sha256_value(x) for rows in prior_sets.values() for c in rows for x in c.get("target_local_resources", [])}
    current_ids = [c["case_id"] for c in cases]
    current_instruction_hashes = [sha256_value(c["task_instruction"]) for c in cases]
    current_fixture_hashes = [sha256_value(c["fixture"]) for c in cases]
    current_resource_hashes = [sha256_value(x) for c in cases for x in c.get("target_local_resources", [])]
    return {
        "case_ids_unique": len(current_ids) == len(set(current_ids)) == CASE_COUNT,
        "case_id_overlap_count": len(set(current_ids) & prior_ids),
        "instruction_hash_overlap_count": len(set(current_instruction_hashes) & prior_instruction_hashes),
        "fixture_hash_overlap_count": len(set(current_fixture_hashes) & prior_fixture_hashes),
        "target_local_resource_hash_overlap_count": len(set(current_resource_hashes) & prior_resource_hashes),
        "prior_development_sets_checked": ["SQ0_V1", "SQ0_V2R1", "SQ0_V3", "OLD_F0"],
    }


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    close = _verified(V3_CLOSEOUT, "SQ0_V3_TOO_EASY_FUTILITY_CLOSEOUT")
    root = _verified(V3_ROOT_CAUSE, "SQ0_V3_TNF_TOO_EASY_FG_NEAR_TARGET_WINDOW")
    if root.get("prospective_v4_constraints", {}).get("fg_mechanism_change") != "NONE; FRESH_PARAMETERIZATION_ONLY":
        raise RuntimeError("V4 no longer follows frozen FG-localization rule.")
    cases = build_cases()
    if len(cases) != CASE_COUNT or len({c["case_id"] for c in cases}) != CASE_COUNT:
        raise RuntimeError("SQ0-V4 cardinality drifted.")
    freshness = _freshness(cases)
    if not freshness["case_ids_unique"] or any(freshness[k] != 0 for k in ("case_id_overlap_count", "instruction_hash_overlap_count", "fixture_hash_overlap_count", "target_local_resource_hash_overlap_count")):
        raise RuntimeError(f"SQ0-V4 freshness audit failed: {freshness}")
    _pack(cases)
    replay = load_cases()
    if sha256_value(cases) != sha256_value(replay):
        raise RuntimeError("SQ0-V4 encrypted replay drifted.")
    oracles = [public_oracle(c) for c in replay]
    if not all(r["target_success"] and not r["private_fixture_ids_used"] for r in oracles):
        raise RuntimeError("SQ0-V4 public oracle failed.")
    max_calls = max(r["public_tool_calls"] for r in oracles)
    min_headroom = min(r["headroom"] for r in oracles)
    if max_calls > 48 or min_headroom < 32:
        raise RuntimeError("SQ0-V4 public reachability/headroom drifted.")
    public = [
        {
            "case_id": c["case_id"],
            "kind": c["kind"],
            "instruction_sha256": sha256_value(c["task_instruction"]),
            "fixture_sha256": sha256_value(c["fixture"]),
            "target_local_resource_hashes": [sha256_value(x) for x in c["target_local_resources"]],
        }
        for c in cases
    ]
    contract: dict[str, Any] = {
        "schema_version": "ace-sq0-v4-contract-v1",
        "object_id": OBJECT_ID,
        "sq0_id": SQ0_ID,
        "status": "SQ0_V4_STATIC_DESIGN_READY",
        "development_iteration": 4,
        "purpose": "DEVELOPMENT_ONLY_SOURCE_FAILURE_QUALIFICATION_NOT_CONFIRMATORY_F0_EVIDENCE",
        "v3_closeout_content_sha256": close["content_sha256"],
        "v3_root_cause_content_sha256": root["content_sha256"],
        "design_change": {
            "FG_SEMANTIC_V4": "V3_FG_MECHANISM_UNCHANGED_FRESH_PARAMETERIZATION_ONLY",
            "TNF_SEMANTIC_V4": "ADD_DYNAMIC_POLICY_TIEBREAK_DUAL_CONTENT_SELECTION_SECOND_STAGE_MODIFIER_AND_COMPOSITE_TOTAL",
            "difficulty_not_from_tool_budget": True,
        },
        "case_count": CASE_COUNT,
        "case_kinds": {"FG_SEMANTIC_V4": 6, "TNF_SEMANTIC_V4": 6},
        "cases": public,
        "freshness_audit": freshness,
        "protected_bundle": {"path": str(OUTPUT_BUNDLE.relative_to(ROOT)), "sha256": sha256_file(OUTPUT_BUNDLE)},
        "tool_call_cap": TOOL_CALL_CAP,
        "usable_failure_window": {"min": 0.75, "max": 0.90},
        "acceptable_final_failure_counts": [9, 10],
        "semantic_failure_definition": [
            "NORMAL_SCIENTIFIC_TERMINAL",
            "TARGET_EVALUATOR_FALSE_WITH_TERMINAL_NEWLINE_NORMALIZATION_ONLY",
            "NO_PROVIDER_INTERFACE_OR_HARNESS_FAILURE",
            "COMPLETE_TARGET_RELEVANT_TRAJECTORY_AVAILABLE",
        ],
        "target_app_families": {"FG": ["file_system", "gmail"], "TNF": ["file_system", "simple_note", "todoist"]},
        "confirmatory_reuse": False,
        "old_f0_case_reuse": False,
        "v1_case_reuse": False,
        "v2r1_case_reuse": False,
        "v3_case_reuse": False,
        "coupling_visible_to_sq0_model": False,
        "non_target_outcomes_visible_to_sq0_model": False,
        "provider_requests": 0,
        "scientific_outcomes_observed": 0,
        "authority": {"sq0_v4_execution": False, "f0_r1": False, "probe": False, "p1": False, "toolsandbox": False, "appworld_ul": False, "paper_claim": False},
    }
    contract["content_sha256"] = sha256_value(contract)
    qualification: dict[str, Any] = {
        "schema_version": "ace-sq0-v4-static-qualification-v1",
        "object_id": OBJECT_ID,
        "sq0_id": SQ0_ID,
        "status": "SQ0_V4_PUBLIC_REACHABILITY_AND_FRESHNESS_PASS",
        "contract_content_sha256": contract["content_sha256"],
        "protected_bundle_sha256": sha256_file(OUTPUT_BUNDLE),
        "case_count": CASE_COUNT,
        "public_oracles": oracles,
        "max_public_tool_calls": max_calls,
        "minimum_headroom": min_headroom,
        "private_fixture_ids_used": False,
        "freshness_audit": freshness,
        "provider_requests": 0,
        "scientific_outcomes_observed": 0,
        "authority": {"sq0_v4_execution": False, "f0_r1": False, "probe": False, "p1": False, "toolsandbox": False, "appworld_ul": False, "paper_claim": False},
    }
    qualification["content_sha256"] = sha256_value(qualification)
    CONTRACT_OUTPUT.write_text(json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    QUAL_OUTPUT.write_text(json.dumps(qualification, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return contract, qualification


def main() -> None:
    _, q = build()
    print(json.dumps({"status": q["status"], "case_count": q["case_count"], "max_public_tool_calls": q["max_public_tool_calls"], "minimum_headroom": q["minimum_headroom"], "provider_requests": 0, "sq0_v4_execution_authorized": False}, sort_keys=True))


if __name__ == "__main__":
    main()
