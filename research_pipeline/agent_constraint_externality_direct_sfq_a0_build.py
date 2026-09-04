from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_direct_flash_v4_closeout import OUTPUT as FLASH_CREDIT_STOP
from research_pipeline.agent_constraint_externality_direct_sfq_a0_cases import build_cases
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.agent_constraint_externality_sq0_build import load_cases as load_v1_cases
from research_pipeline.agent_constraint_externality_sq0_v2r1_build import load_cases as load_v2r1_cases
from research_pipeline.agent_constraint_externality_sq0_v3_build import load_cases as load_v3_cases
from research_pipeline.agent_constraint_externality_sq0_v4_build import load_cases as load_v4_cases
from research_pipeline.agent_constraint_externality_sq0_v4_oracle import public_oracle
from research_pipeline.agent_constraint_externality_sq0_v5_build import load_cases as load_v5_cases
from research_pipeline.appworld_constraint_compiler import load_protected_spec

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OLD_F0_BUNDLE = GENERATED / "agent-constraint-externality-appworld-pre-f0_5-protected-v4-20260902.bundle"
OUTPUT_BUNDLE = GENERATED / "agent-constraint-externality-direct-sfq-a0-protected-20260903.bundle"
CONTRACT_OUTPUT = GENERATED / "agent-constraint-externality-direct-sfq-a0-contract-20260903.json"
QUAL_OUTPUT = GENERATED / "agent-constraint-externality-direct-sfq-a0-static-qualification-20260903.json"
SFQ_ID = "ACE-DIRECT-SFQ-A0-20260903"
CASE_COUNT = 12
TOOL_CALL_CAP = 80
FAILURE_RATE_MIN = 0.75
FAILURE_RATE_MAX = 0.90


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verified(path: Path, status: str | None = None) -> dict[str, Any]:
    payload = read_json(path)
    if payload.get("object_id") != OBJECT_ID:
        raise RuntimeError(f"Object mismatch: {path}")
    claimed = payload.get("content_sha256")
    unsigned = dict(payload); unsigned.pop("content_sha256", None)
    if claimed != sha256_value(unsigned):
        raise RuntimeError(f"Content hash mismatch: {path}")
    if status is not None and payload.get("status") != status:
        raise RuntimeError(f"Status mismatch: {path}: {payload.get('status')}")
    return payload


def pack_cases(cases: list[dict[str, Any]]) -> None:
    from appworld.common.constants import PASSWORD, SALT
    from appworld.common.crypto import pack_bundle

    with tempfile.TemporaryDirectory(prefix="ace-direct-sfq-a0-") as directory:
        root = Path(directory)
        spec = root / "direct-sfq-a0" / "case_spec.json"
        spec.parent.mkdir(parents=True)
        spec.write_text(
            json.dumps(
                {"object_id": OBJECT_ID, "sfq_id": SFQ_ID, "cases": cases},
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        pack_bundle(
            str(OUTPUT_BUNDLE),
            str(root),
            ["direct-sfq-a0"],
            PASSWORD,
            SALT,
            include_license=False,
        )


def load_cases(path: Path = OUTPUT_BUNDLE) -> list[dict[str, Any]]:
    from appworld.common.constants import PASSWORD, SALT
    from appworld.common.crypto import bundle_file_path_to_content

    content = bundle_file_path_to_content(
        str(path),
        PASSWORD,
        SALT,
        include_file_paths=["direct-sfq-a0/case_spec.json"],
    )
    payload = json.loads(content["direct-sfq-a0/case_spec.json"])
    if payload.get("object_id") != OBJECT_ID or payload.get("sfq_id") != SFQ_ID:
        raise RuntimeError("Direct SFQ-A0 bundle identity mismatch.")
    return list(payload["cases"])


def freshness(cases: list[dict[str, Any]]) -> dict[str, Any]:
    priors = {
        "SQ0_V1": load_v1_cases(),
        "SQ0_V2R1": load_v2r1_cases(),
        "SQ0_V3": load_v3_cases(),
        "SQ0_V4": load_v4_cases(),
        "SQ0_V5": load_v5_cases(),
    }
    old = load_protected_spec(OLD_F0_BUNDLE)
    prior_ids = {case["case_id"] for rows in priors.values() for case in rows}
    prior_ids |= {family["family_id"] for family in old["families"]}
    prior_instruction_hashes = {
        sha256_value(case["task_instruction"])
        for rows in priors.values()
        for case in rows
    }
    prior_instruction_hashes |= {
        sha256_value(text)
        for family in old["families"]
        for text in [family["target_instruction"], *[arm["task_instruction"] for arm in family["arms"]]]
    }
    prior_fixture_hashes = {
        sha256_value(case["fixture"])
        for rows in priors.values()
        for case in rows
    }
    prior_resource_hashes = {
        sha256_value(resource)
        for rows in priors.values()
        for case in rows
        for resource in case.get("target_local_resources", [])
    }
    current_ids = [case["case_id"] for case in cases]
    current_instruction_hashes = [sha256_value(case["task_instruction"]) for case in cases]
    current_fixture_hashes = [sha256_value(case["fixture"]) for case in cases]
    current_resource_hashes = [
        sha256_value(resource)
        for case in cases
        for resource in case.get("target_local_resources", [])
    ]
    return {
        "case_ids_unique": len(current_ids) == len(set(current_ids)) == CASE_COUNT,
        "case_id_overlap_count": len(set(current_ids) & prior_ids),
        "instruction_hash_overlap_count": len(set(current_instruction_hashes) & prior_instruction_hashes),
        "fixture_hash_overlap_count": len(set(current_fixture_hashes) & prior_fixture_hashes),
        "target_local_resource_hash_overlap_count": len(set(current_resource_hashes) & prior_resource_hashes),
        "prior_development_sets_checked": list(priors),
        "old_f0_checked": True,
    }


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    credit = verified(
        FLASH_CREDIT_STOP,
        "DIRECT_QWEN37FLASH_V4_R1_PROVIDER_CREDIT_EXHAUSTED_STOP",
    )
    cases = build_cases()
    if len(cases) != CASE_COUNT:
        raise RuntimeError("Direct SFQ-A0 must contain exactly 12 cases.")
    fresh = freshness(cases)
    for key in (
        "case_id_overlap_count",
        "instruction_hash_overlap_count",
        "fixture_hash_overlap_count",
        "target_local_resource_hash_overlap_count",
    ):
        if fresh[key] != 0:
            raise RuntimeError(f"Direct SFQ-A0 freshness failed at {key}: {fresh[key]}")
    if not fresh["case_ids_unique"]:
        raise RuntimeError("Direct SFQ-A0 case IDs are not unique.")
    pack_cases(cases)
    replay = load_cases()
    if sha256_value(cases) != sha256_value(replay):
        raise RuntimeError("Direct SFQ-A0 encrypted replay drifted.")
    oracles = [public_oracle(case) for case in replay]
    if not all(row["target_success"] and not row["private_fixture_ids_used"] for row in oracles):
        raise RuntimeError("Direct SFQ-A0 public oracle failed.")
    max_calls = max(int(row["public_tool_calls"]) for row in oracles)
    min_headroom = min(TOOL_CALL_CAP - int(row["public_tool_calls"]) for row in oracles)
    if max_calls >= TOOL_CALL_CAP or min_headroom <= 0:
        raise RuntimeError("Direct SFQ-A0 lacks positive public-oracle tool headroom.")
    public_cases = [
        {
            "case_id": case["case_id"],
            "kind": case["kind"],
            "instruction_sha256": sha256_value(case["task_instruction"]),
            "fixture_sha256": sha256_value(case["fixture"]),
            "target_local_resource_hashes": [
                sha256_value(resource) for resource in case.get("target_local_resources", [])
            ],
        }
        for case in cases
    ]
    contract: dict[str, Any] = {
        "schema_version": "ace-direct-sfq-a0-contract-v1",
        "object_id": OBJECT_ID,
        "sfq_id": SFQ_ID,
        "status": "DIRECT_SFQ_A0_STATIC_DESIGN_READY_PROVIDER_CREDIT_BLOCKED",
        "purpose": "DEVELOPMENT_ONLY_SOURCE_FAILURE_QUALIFICATION_FOR_CLEAN_DIRECT_API_ACTOR",
        "case_count": CASE_COUNT,
        "case_kinds": {
            "FG_DIRECT_SEMANTIC_A0": 6,
            "TNF_DIRECT_SEMANTIC_A0": 6,
        },
        "cases": public_cases,
        "freshness_audit": fresh,
        "protected_bundle": {
            "path": str(OUTPUT_BUNDLE.relative_to(ROOT)),
            "sha256": sha256_file(OUTPUT_BUNDLE),
        },
        "tool_call_cap": TOOL_CALL_CAP,
        "usable_failure_window": {"min": FAILURE_RATE_MIN, "max": FAILURE_RATE_MAX},
        "acceptable_final_failure_counts": [9, 10],
        "semantic_failure_definition": [
            "NORMAL_SCIENTIFIC_TERMINAL",
            "TARGET_EVALUATOR_FALSE_WITH_TERMINAL_NEWLINE_NORMALIZATION_ONLY",
            "NO_PROVIDER_INTERFACE_OR_HARNESS_FAILURE",
            "COMPLETE_TARGET_RELEVANT_TRAJECTORY_AVAILABLE",
        ],
        "development_lineage": {
            "uses_prior_sq0_semantic_design_lessons": True,
            "reuses_prior_case_instances": False,
            "reuses_prior_model_outcomes_as_current_measurements": False,
            "sq0_v5_final_invalid_status_preserved": True,
            "direct_flash_credit_stop_content_sha256": credit["content_sha256"],
        },
        "execution_preconditions": {
            "direct_provider_credit_available": False,
            "direct_qwen37flash_v4_capability_pass_required": True,
            "fresh_execution_contract_required": True,
            "current_execution_authorized": False,
        },
        "confirmatory_reuse": False,
        "f0_r1_confirmatory_instances_must_be_fresh_again": True,
        "coupling_visible_to_model": False,
        "non_target_outcomes_visible_to_model": False,
        "provider_requests": 0,
        "scientific_outcomes_observed": 0,
        "authority": {
            "direct_sfq_a0_execution": False,
            "f0_r1": False,
            "probe": False,
            "p1": False,
            "paper_claim": False,
            "static_design": True,
        },
    }
    contract["content_sha256"] = sha256_value(contract)
    qualification: dict[str, Any] = {
        "schema_version": "ace-direct-sfq-a0-static-qualification-v1",
        "object_id": OBJECT_ID,
        "sfq_id": SFQ_ID,
        "status": "DIRECT_SFQ_A0_PUBLIC_REACHABILITY_AND_FRESHNESS_PASS_EXECUTION_BLOCKED",
        "contract_content_sha256": contract["content_sha256"],
        "protected_bundle_sha256": sha256_file(OUTPUT_BUNDLE),
        "case_count": CASE_COUNT,
        "public_oracles": oracles,
        "max_public_tool_calls": max_calls,
        "minimum_tool_headroom": min_headroom,
        "private_fixture_ids_used": False,
        "freshness_audit": fresh,
        "provider_requests": 0,
        "scientific_outcomes_observed": 0,
        "execution_blocker": "DIRECT_PROVIDER_INSUFFICIENT_CREDIT_AND_FLASH_V4_CAPABILITY_NOT_YET_VALIDLY_MEASURED",
        "authority": {
            "direct_sfq_a0_execution": False,
            "f0_r1": False,
            "p1": False,
            "paper_claim": False,
        },
    }
    qualification["content_sha256"] = sha256_value(qualification)
    CONTRACT_OUTPUT.write_text(
        json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    QUAL_OUTPUT.write_text(
        json.dumps(qualification, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return contract, qualification


def main() -> None:
    contract, qualification = build()
    print(json.dumps({
        "contract_status": contract["status"],
        "qualification_status": qualification["status"],
        "case_count": qualification["case_count"],
        "max_public_tool_calls": qualification["max_public_tool_calls"],
        "minimum_tool_headroom": qualification["minimum_tool_headroom"],
        "provider_requests": 0,
        "execution_authorized": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
