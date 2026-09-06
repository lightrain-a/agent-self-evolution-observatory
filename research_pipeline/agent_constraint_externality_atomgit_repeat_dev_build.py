from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_family import (
    SELECTION_SALT,
    family_from_case,
    select_case_ids,
)
from research_pipeline.agent_constraint_externality_direct_sfq_a0_build import (
    OUTPUT_BUNDLE as DIRECT_SFQ_BUNDLE,
    load_cases as load_direct_sfq_cases,
)
from research_pipeline.agent_constraint_externality_runner_core import OBJECT_ID, sha256_file, sha256_value
from research_pipeline.appworld_constraint_compiler import EXPECTED_APPWORLD_SHA, validate_family, validate_source

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
DIRECT_RESULT = GENERATED / "agent-constraint-externality-direct-sfq-a0-atomgit-mimo25pro-result-20260906.json"
DIRECT_RUN = Path("/data/wyt/agent-constraint-externality/runs/direct-sfq-a0-atomgit-mimo25pro-20260906-v1")
DIRECT_LEDGER = DIRECT_RUN / "ledger.jsonl"
APPWORLD_ROOT = Path("/data/wyt/agent-self-evolution-observatory/worktrees/agent-constraint-externality-20260831/cache/substrates/appworld-official-20260831")
DEV_ID = "ACE-ATOMGIT-REPEAT-DEV-V1-20260906"
OUTPUT_BUNDLE = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-protected-20260906.bundle"
CONTRACT_OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-contract-20260906.json"
QUAL_OUTPUT = GENERATED / "agent-constraint-externality-atomgit-repeat-dev-static-qualification-20260906.json"


def _verified_result() -> dict[str, Any]:
    payload = json.loads(DIRECT_RESULT.read_text(encoding="utf-8"))
    claimed = payload.pop("content_sha256")
    if sha256_value(payload) != claimed:
        raise RuntimeError("Direct-SFQ result content hash drift")
    payload["content_sha256"] = claimed
    if payload.get("object_id") != OBJECT_ID or payload.get("status") != "DIRECT_SFQ_A0_ATOMGIT_TARGET_FAILURE_QUALIFICATION_PASS":
        raise RuntimeError("Direct-SFQ parent is not frozen PASS")
    if payload.get("development_only") is not True or payload.get("confirmatory_reuse") is not False:
        raise RuntimeError("Direct-SFQ parent boundary drift")
    if sha256_file(DIRECT_LEDGER) != payload.get("ledger_sha256"):
        raise RuntimeError("Direct-SFQ ledger hash drift")
    return payload


def _completion_rows() -> list[dict[str, Any]]:
    rows = []
    for line in DIRECT_LEDGER.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        if item.get("event") == "COMPLETION":
            rows.append(item)
    if len(rows) != 12 or sum(bool(row.get("usable_target_failure")) for row in rows) != 9:
        raise RuntimeError("Direct-SFQ completion geometry drift")
    if any(row.get("technical_failure") for row in rows):
        raise RuntimeError("Direct-SFQ technical failure cannot seed repeat development")
    return rows


def _pack(families: list[dict[str, Any]], selection: dict[str, Any]) -> None:
    from appworld.common.constants import PASSWORD, SALT
    from appworld.common.crypto import pack_bundle
    payload = {
        "schema_version": "ace-atomgit-repeat-dev-protected-v1",
        "object_id": OBJECT_ID,
        "dev_id": DEV_ID,
        "appworld_repo_sha": EXPECTED_APPWORLD_SHA,
        "construction": "DIRECT_SFQ_DEVELOPMENT_FAILURE_TEMPLATES_PLUS_OUTCOME_BLIND_MATCHED_RESOURCE_TOPOLOGY",
        "selection_salt": SELECTION_SALT,
        "selection": selection,
        "family_count": 6,
        "families": families,
        "scientific_topology_outcomes_observed": 0,
        "provider_calls_created_by_build": 0,
    }
    with tempfile.TemporaryDirectory(prefix="ace-repeat-dev-bundle-") as directory:
        path = Path(directory) / "repeat_dev" / "family_spec.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        pack_bundle(str(OUTPUT_BUNDLE), str(path.parents[1]), ["repeat_dev"], PASSWORD, SALT, include_license=False)


def load_dev_spec() -> dict[str, Any]:
    from appworld.common.constants import PASSWORD, SALT
    from appworld.common.crypto import bundle_file_path_to_content
    contents = bundle_file_path_to_content(
        str(OUTPUT_BUNDLE), PASSWORD, SALT, include_file_paths=["repeat_dev/family_spec.json"]
    )
    payload = json.loads(contents["repeat_dev/family_spec.json"])
    if payload.get("object_id") != OBJECT_ID or payload.get("dev_id") != DEV_ID:
        raise RuntimeError("repeat development protected bundle identity mismatch")
    return payload


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    parent = _verified_result()
    selected, ranking = select_case_ids(_completion_rows())
    case_index = {case["case_id"]: case for case in load_direct_sfq_cases(DIRECT_SFQ_BUNDLE)}
    if set(selected) - set(case_index):
        raise RuntimeError("selected template missing from protected Direct-SFQ bundle")
    families = [family_from_case(case_index[cid], ordinal) for ordinal, cid in enumerate(selected, 1)]
    if len(families) != 6 or len({f["family_id"] for f in families}) != 6:
        raise RuntimeError("development family cardinality drift")

    source_manifest = validate_source(APPWORLD_ROOT)
    with tempfile.TemporaryDirectory(prefix="ace-repeat-dev-static-") as directory:
        summaries = [validate_family(family, APPWORLD_ROOT, Path(directory)) for family in families]
    if not all(
        row["shared_resource_exposure"] == {"INDEPENDENT": 0, "LOW": 1, "HIGH": 2}
        and row["initial_non_target_constraints_satisfied"] is True
        for row in summaries
    ):
        raise RuntimeError("matched topology static qualification failed")
    _pack(families, {"selected_case_ids": selected, "ranking": ranking})
    replay = load_dev_spec()
    if sha256_value(replay["families"]) != sha256_value(families):
        raise RuntimeError("protected development bundle replay drift")

    target_equivalence = {}
    for family in families:
        targets = [next(c for c in arm["constraints"] if c["role"] == "TARGET") for arm in family["arms"]]
        if len({sha256_value(target) for target in targets}) != 1:
            raise RuntimeError("target constraint drift across topology arms")
        if family["source_case"]["task_instruction"] != family["target_instruction"]:
            raise RuntimeError("source/probe target instruction drift")
        target_equivalence[family["family_id"]] = {
            "template_case_id": family["template_case_id"],
            "source_target_instruction_sha256": sha256_value(family["source_case"]["task_instruction"]),
            "probe_target_instruction_sha256": sha256_value(family["target_instruction"]),
            "target_constraint_sha256": sha256_value(targets[0]),
        }

    contract: dict[str, Any] = {
        "schema_version": "ace-atomgit-repeat-dev-contract-v1",
        "object_id": OBJECT_ID,
        "dev_id": DEV_ID,
        "status": "ATOMGIT_REPEAT_DEV_STATIC_DESIGN_READY_ZERO_PROVIDER",
        "purpose": "DEVELOPMENT_ONLY_REPEAT_AND_PRECISION_QUALIFICATION_PRE_CONFIRMATORY",
        "static_repair_lineage": {
            "superseded_git_commit": "23ffffbb99c80d5894bc76b7b95eaceb65bed8ce",
            "superseded_bundle_sha256": "edbed772435d58fb211acf97b57f250caf721f0662c5e510deccb5585d119a6d",
            "failure_class": "STATIC_TOPOLOGY_WITNESS_SEMANTIC_MISMATCH_ZERO_PROVIDER",
            "defect": "TNF target-shared witnesses were fixed to adjust-01.txt/modifier-01.txt rather than the files actually selected by the frozen target routing rule.",
            "repair": "Derive TNF shared-resource witnesses deterministically from the frozen route/policy/adjustment/modifier selection rule before topology construction.",
            "provider_requests_in_superseded_freeze": 0,
            "scientific_topology_outcomes_in_superseded_freeze": 0,
        },
        "parent_direct_sfq_result_content_sha256": parent["content_sha256"],
        "parent_direct_sfq_ledger_sha256": parent["ledger_sha256"],
        "selection": {"salt": SELECTION_SALT, "selected_case_ids": selected, "ranking": ranking},
        "development_family_count": 6,
        "category_balance": {"FILE_GMAIL": 3, "TODO_NOTE_FILE": 3},
        "permanently_excluded_from_confirmatory": True,
        "selected_backbone": {
            "provider": "ATOMGIT_CODINGPLAN_SIGNED_GATEWAY",
            "model_profile": "AtomGit-mimo-v2.5-pro",
            "model_id": "mimo-v2.5-pro",
            "harness": "ATOMCODE_CODINGPLAN_MCP_V1",
        },
        "source_policy": {
            "new_source_unit_per_family": True,
            "old_direct_sfq_calls_count_as_new_source_units": False,
            "old_outcome_use": "TEMPLATE_ADMISSION_TO_DEVELOPMENT_CONDITIONAL_FAILURE_POPULATION_ONLY",
            "replacement_or_top_up": False,
            "all_six_new_sources_must_be_semantic_failures": True,
            "trajectory_persistence_required_before_repair": True,
        },
        "repair_policy": {
            "one_frozen_repair_per_family": True,
            "target_failure_evidence_only": True,
            "topology_or_non_target_outcomes_visible": False,
            "human_edit": False,
            "same_exact_bytes_across_all_replays": True,
        },
        "repeat_policy": {
            "initial_R": 2,
            "arms": ["INDEPENDENT", "LOW", "HIGH"],
            "branches": ["NO_UPDATE", "REAL_REPAIR"],
            "planned_initial_episodes": 72,
            "R2_rule": "target disagreement <= 0.10 AND mean absolute CRR repeat difference <= 0.10",
            "R3_trigger": "R2 fails but both metrics <= 0.20",
            "R_gt_3_forbidden": True,
            "selection_uses_treatment_direction": False,
        },
        "protected_bundle": {"path": str(OUTPUT_BUNDLE.relative_to(ROOT)), "sha256": sha256_file(OUTPUT_BUNDLE)},
        "appworld_source": source_manifest,
        "family_summaries": summaries,
        "target_equivalence": target_equivalence,
        "provider_requests_created": 0,
        "scientific_topology_outcomes_observed": 0,
        "authority": {
            "source_execution": False,
            "repair_generation": False,
            "development_repeat_qualification": False,
            "target_only_verification": False,
            "rq1_rq2": False,
            "rq3": False,
            "rq4": False,
            "paper_claim": False,
        },
    }
    contract["content_sha256"] = sha256_value(contract)
    qualification: dict[str, Any] = {
        "schema_version": "ace-atomgit-repeat-dev-static-qualification-v1",
        "object_id": OBJECT_ID,
        "dev_id": DEV_ID,
        "status": "ATOMGIT_REPEAT_DEV_STATIC_QUALIFICATION_PASS_EXECUTION_CLOSED",
        "contract_content_sha256": contract["content_sha256"],
        "protected_bundle_sha256": sha256_file(OUTPUT_BUNDLE),
        "family_count": 6,
        "category_counts": {"FILE_GMAIL": 3, "TODO_NOTE_FILE": 3},
        "all_three_level_topology_valid": True,
        "all_initial_non_targets_satisfied": True,
        "source_probe_target_instruction_exact": True,
        "target_constraint_exact_across_arms": True,
        "arm_instruction_byte_and_word_matched": True,
        "confirmatory_reuse": False,
        "provider_requests_created": 0,
        "scientific_topology_outcomes_observed": 0,
        "next_required_action": "INDEPENDENT_PREEXEC_REVIEW_THEN_SEPARATE_EXECUTION_AUTHORITY",
        "authority": {"source_execution": False, "repair_generation": False, "development_repeat_qualification": False},
    }
    qualification["content_sha256"] = sha256_value(qualification)
    CONTRACT_OUTPUT.write_text(json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    QUAL_OUTPUT.write_text(json.dumps(qualification, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return contract, qualification


def main() -> None:
    contract, qualification = build()
    print(json.dumps({
        "status": qualification["status"],
        "selected_case_ids": contract["selection"]["selected_case_ids"],
        "family_count": qualification["family_count"],
        "protected_bundle_sha256": qualification["protected_bundle_sha256"],
        "provider_requests_created": 0,
        "authority": qualification["authority"],
    }, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
