from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import research_pipeline.agent_constraint_externality_sq0_build as sq0_build
from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_build import load_dev_spec
from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_reserve_family import reserve_family
from research_pipeline.agent_constraint_externality_direct_sfq_a0_build import load_cases as load_direct_cases
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.agent_constraint_externality_sq0_v4_oracle import public_oracle
from research_pipeline.appworld_constraint_compiler import EXPECTED_APPWORLD_SHA, validate_family, validate_source

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
APPWORLD_ROOT = Path("/data/wyt/agent-self-evolution-observatory/worktrees/agent-constraint-externality-20260831/cache/substrates/appworld-official-20260831")
CLOSEOUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-source-closeout-20260906.json"
OUTPUT_BUNDLE = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-protected-20260906.bundle"
CONTRACT_OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-contract-20260906.json"
QUAL_OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-reserve-static-qualification-20260906.json"
RESERVE_ID = "ACE-ATOMGIT-REPEAT-DEV-RESERVE-V1-20260906"
ORDER_SALT = "ACE-REPEAT-DEV-RESERVE-ORDER-20260906-V1"
PER_CATEGORY = 8
SELECT_PER_CATEGORY = 3
FG_ORDINALS = tuple(range(101, 109))
TNF_ORDINALS = tuple(range(109, 117))


class ReserveBuildError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verified_closeout() -> dict[str, Any]:
    payload = read_json(CLOSEOUT)
    claimed = payload.pop("content_sha256")
    if sha256_value(payload) != claimed:
        raise ReserveBuildError("fixed-six closeout content hash drift")
    payload["content_sha256"] = claimed
    if payload.get("status") != "ATOMGIT_REPEAT_DEV_FIXED_SIX_SOURCE_SUPPORT_FAIL_STOP_NO_REPAIR":
        raise ReserveBuildError("reserve repair requires fixed-six support stop")
    if payload.get("repair_generation_executed") or payload.get("topology_execution_executed"):
        raise ReserveBuildError("fixed-six closeout crossed downstream boundary")
    return payload


def _direct_index() -> dict[str, dict[str, Any]]:
    return {case["case_id"]: case for case in load_direct_cases()}


def _template_mapping() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pos, ordinal in enumerate(FG_ORDINALS, start=1):
        rows.append({"category": "FG", "ordinal": ordinal, "template_case_id": f"DIRECT-SFQ-A0-FG-{((pos - 1) % 6) + 1:02d}"})
    for pos, ordinal in enumerate(TNF_ORDINALS, start=1):
        rows.append({"category": "TNF", "ordinal": ordinal, "template_case_id": f"DIRECT-SFQ-A0-TNF-{((pos - 1) % 6) + 1:02d}"})
    return rows


def _rank(fid: str) -> str:
    return hashlib.sha256(f"{ORDER_SALT}|{fid}".encode("utf-8")).hexdigest()


def _prior_source_cases() -> list[dict[str, Any]]:
    prior = list(load_direct_cases())
    prior.extend(family["source_case"] for family in load_dev_spec()["families"])
    return prior


def freshness(source_cases: list[dict[str, Any]]) -> dict[str, Any]:
    prior = _prior_source_cases()
    prior_ids = {str(case["case_id"]) for case in prior}
    prior_instruction = {sha256_value(case["task_instruction"]) for case in prior}
    prior_fixture = {sha256_value(case["fixture"]) for case in prior}
    prior_resources = {
        sha256_value(resource)
        for case in prior for resource in case.get("target_local_resources", [])
    }
    ids = [str(case["case_id"]) for case in source_cases]
    instructions = [sha256_value(case["task_instruction"]) for case in source_cases]
    fixtures = [sha256_value(case["fixture"]) for case in source_cases]
    resources = [
        sha256_value(resource)
        for case in source_cases for resource in case.get("target_local_resources", [])
    ]
    return {
        "source_case_ids_unique": len(ids) == len(set(ids)) == 16,
        "source_instruction_hashes_unique": len(instructions) == len(set(instructions)) == 16,
        "source_fixture_hashes_unique": len(fixtures) == len(set(fixtures)) == 16,
        "case_id_overlap_count": len(set(ids) & prior_ids),
        "instruction_hash_overlap_count": len(set(instructions) & prior_instruction),
        "fixture_hash_overlap_count": len(set(fixtures) & prior_fixture),
        "target_local_resource_hash_overlap_count": len(set(resources) & prior_resources),
        "prior_direct_sfq_cases_checked": 12,
        "prior_fixed_six_cases_checked": 6,
    }


def _pack(payload: dict[str, Any]) -> None:
    from appworld.common.constants import PASSWORD, SALT
    from appworld.common.crypto import pack_bundle
    with tempfile.TemporaryDirectory(prefix="ace-repeat-dev-reserve-") as directory:
        path = Path(directory) / "repeat_dev_reserve" / "family_spec.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        pack_bundle(str(OUTPUT_BUNDLE), str(path.parents[1]), ["repeat_dev_reserve"], PASSWORD, SALT, include_license=False)


def load_reserve_spec() -> dict[str, Any]:
    from appworld.common.constants import PASSWORD, SALT
    from appworld.common.crypto import bundle_file_path_to_content
    contents = bundle_file_path_to_content(
        str(OUTPUT_BUNDLE), PASSWORD, SALT,
        include_file_paths=["repeat_dev_reserve/family_spec.json"],
    )
    payload = json.loads(contents["repeat_dev_reserve/family_spec.json"])
    if payload.get("object_id") != OBJECT_ID or payload.get("reserve_id") != RESERVE_ID:
        raise ReserveBuildError("reserve bundle identity mismatch")
    return payload


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    closeout = verified_closeout()
    direct = _direct_index()
    mapping = _template_mapping()
    families = [reserve_family(direct[row["template_case_id"]], int(row["ordinal"])) for row in mapping]
    if len(families) != 16 or len({family["family_id"] for family in families}) != 16:
        raise ReserveBuildError("reserve family cardinality drift")
    source_cases = [family["source_case"] for family in families]
    fresh = freshness(source_cases)
    if not fresh["source_case_ids_unique"] or not fresh["source_instruction_hashes_unique"] or not fresh["source_fixture_hashes_unique"]:
        raise ReserveBuildError("reserve internal freshness failed")
    if any(fresh[key] != 0 for key in ("case_id_overlap_count", "instruction_hash_overlap_count", "fixture_hash_overlap_count", "target_local_resource_hash_overlap_count")):
        raise ReserveBuildError(f"reserve overlaps prior development objects: {fresh}")

    source = validate_source(APPWORLD_ROOT)
    with tempfile.TemporaryDirectory(prefix="ace-repeat-dev-reserve-static-") as directory:
        summaries = [validate_family(family, APPWORLD_ROOT, Path(directory)) for family in families]
    if not all(
        summary["shared_resource_exposure"] == {"INDEPENDENT": 0, "LOW": 1, "HIGH": 2}
        and summary["initial_non_target_constraints_satisfied"] is True
        for summary in summaries
    ):
        raise ReserveBuildError("reserve matched-topology static qualification failed")

    sq0_build.APPWORLD_ROOT = APPWORLD_ROOT
    oracles = [public_oracle(case) for case in source_cases]
    if not all(row["target_success"] and not row["private_fixture_ids_used"] and int(row["headroom"]) > 0 for row in oracles):
        raise ReserveBuildError("reserve public source oracle failed")

    category_ids = {
        "FG": [family["family_id"] for family in families if family["category"] == "FILE_GMAIL"],
        "TNF": [family["family_id"] for family in families if family["category"] == "TODO_NOTE_FILE"],
    }
    ranked = {
        key: [{"family_id": fid, "rank_sha256": _rank(fid)} for fid in sorted(ids, key=_rank)]
        for key, ids in category_ids.items()
    }
    payload = {
        "schema_version": "ace-repeat-dev-reserve-protected-v1",
        "object_id": OBJECT_ID,
        "reserve_id": RESERVE_ID,
        "appworld_repo_sha": EXPECTED_APPWORLD_SHA,
        "construction": "FRESH_INSTANCE_ONLY_DIRECT_SFQ_RECIPE_PLUS_OUTCOME_BLIND_MATCHED_RESOURCE_TOPOLOGY",
        "template_mapping": mapping,
        "order_salt": ORDER_SALT,
        "ranked_source_order_by_category": ranked,
        "family_count": 16,
        "families": families,
        "provider_calls_created_by_build": 0,
        "scientific_topology_outcomes_observed": 0,
    }
    _pack(payload)
    replay = load_reserve_spec()
    if sha256_value(replay["families"]) != sha256_value(families):
        raise ReserveBuildError("reserve protected replay drift")

    contract: dict[str, Any] = {
        "schema_version": "ace-repeat-dev-reserve-contract-v1",
        "object_id": OBJECT_ID,
        "reserve_id": RESERVE_ID,
        "status": "ATOMGIT_REPEAT_DEV_RESERVE_STATIC_READY_EXECUTION_CLOSED",
        "repair_class": "QUALIFICATION_SUPPORT_DESIGN_REPAIR_NO_MECHANISM_OUTCOME_READ",
        "parent_fixed_six_closeout_content_sha256": closeout["content_sha256"],
        "parent_fixed_six_reuse": False,
        "parent_fixed_six_completed_failures_carried_forward": False,
        "reason": "The fixed-six development set made any single normally completed target success terminal even though source-failure status is a pre-topology eligibility fact. The reserve moves that eligibility rule before topology execution without using repair, collateral, or topology outcomes.",
        "reserve": {
            "family_count": 16,
            "per_category": PER_CATEGORY,
            "needed_per_category": SELECT_PER_CATEGORY,
            "categories": ["FG", "TNF"],
            "order_salt": ORDER_SALT,
            "ranked_source_order_by_category": ranked,
            "selection_rule": "Within each category, dispatch fresh source families in frozen rank order. Target success is pre-topology ineligibility; continue to the next never-dispatched reserve family. Freeze the first three normally completed semantic target failures in each category. Stop once 3 FG + 3 TNF failures are frozen.",
            "maximum_source_dispatches": 16,
            "technical_invalidity_after_dispatch": "HARD_STOP_NO_REPLAY_NO_SKIP",
            "pre_dispatch_operational_hold": "RESUMABLE_WITHOUT_BURNING_UNIT",
            "retry": False,
            "replacement_outside_frozen_reserve": False,
            "challenge_recipe_change_after_first_dispatch": False,
        },
        "selected_development_panel_after_source": {
            "family_count": 6,
            "category_balance": {"FG": 3, "TNF": 3},
            "permanently_excluded_from_confirmatory": True,
            "repair_generation_only_after_panel_freeze": True,
            "same_exact_repair_bytes_for_all_later_topology_replays": True,
        },
        "freshness": fresh,
        "public_source_oracles": oracles,
        "max_public_tool_calls": max(int(row["public_tool_calls"]) for row in oracles),
        "minimum_public_tool_headroom": min(int(row["headroom"]) for row in oracles),
        "family_summaries": summaries,
        "appworld_source": source,
        "protected_bundle": {"path": str(OUTPUT_BUNDLE.relative_to(ROOT)), "sha256": sha256_file(OUTPUT_BUNDLE)},
        "provider_requests_created": 0,
        "scientific_topology_outcomes_observed": 0,
        "authority": {
            "reserve_source_execution": False,
            "repair_generation": False,
            "development_repeat_qualification": False,
            "target_only_verification": False,
            "rq1_rq2": False,
            "rq3": False,
            "rq4": False,
            "paper_claim": False,
        },
        "next_required_action": "ZERO_PROVIDER adversarial protocol review; then separate human execution authority if review passes.",
    }
    contract["content_sha256"] = sha256_value(contract)
    qualification: dict[str, Any] = {
        "schema_version": "ace-repeat-dev-reserve-static-qualification-v1",
        "object_id": OBJECT_ID,
        "reserve_id": RESERVE_ID,
        "status": "ATOMGIT_REPEAT_DEV_RESERVE_STATIC_QUALIFICATION_PASS_AUTHORITY_CLOSED",
        "contract_content_sha256": contract["content_sha256"],
        "protected_bundle_sha256": sha256_file(OUTPUT_BUNDLE),
        "family_count": 16,
        "category_counts": {"FILE_GMAIL": 8, "TODO_NOTE_FILE": 8},
        "freshness_pass": True,
        "public_oracle_pass": True,
        "matched_topology_pass": True,
        "initial_non_target_satisfaction_pass": True,
        "provider_requests_created": 0,
        "scientific_topology_outcomes_observed": 0,
        "authority": {"reserve_source_execution": False, "repair_generation": False, "development_repeat_qualification": False},
    }
    qualification["content_sha256"] = sha256_value(qualification)
    CONTRACT_OUTPUT.write_text(json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    QUAL_OUTPUT.write_text(json.dumps(qualification, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return contract, qualification


def main() -> None:
    contract, qualification = build()
    print(json.dumps({
        "status": qualification["status"],
        "family_count": qualification["family_count"],
        "category_counts": qualification["category_counts"],
        "max_public_tool_calls": contract["max_public_tool_calls"],
        "minimum_public_tool_headroom": contract["minimum_public_tool_headroom"],
        "protected_bundle_sha256": qualification["protected_bundle_sha256"],
        "provider_requests_created": 0,
        "authority": qualification["authority"],
    }, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
