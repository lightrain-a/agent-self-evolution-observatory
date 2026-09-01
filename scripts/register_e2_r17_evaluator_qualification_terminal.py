#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "generated/e2-r17-failure-differential-registry-v7-20260829.json"
OUTPUT = ROOT / "generated/e2-r17-failure-differential-registry-v8-20260830.json"
ASSETS = ROOT / "research_pipeline/e2_r17_reusable_failure_assets_20260829.json"
EXTERNAL = ROOT / "research_pipeline/external_failure_assets.json"
LOCAL_ANALYSIS = (
    ROOT
    / "generated/e2-r17-local-qwen3-evaluator-qualification-failure-analysis-20260830.json"
)
LOCAL_V2 = (
    ROOT / "generated/e2-r17-local-qwen3-evaluator-qualification-v2-20260830.json"
)
KIMI_ANALYSIS = (
    ROOT / "generated/e2-r17-kimi-evaluator-qualification-failure-analysis-20260830.json"
)
KIMI_QUALIFICATION = (
    ROOT / "generated/e2-r17-kimi-evaluator-development-qualification-20260830.json"
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def write(path: Path, payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if path == ASSETS:
        compact_keys = (
            "final_visible_budget_asset",
            "causal_provenance_asset",
            "provider_budget_asset",
            "role_runtime_asset",
            "zero_missing_asset",
            "review_layer_asset",
            "execution_faithful_preflight_asset",
            "duplicate_launch_asset",
        )
        for key in compact_keys:
            for field in ("reuse_scope", "reuse_effectiveness"):
                value = payload[key][field]
                pretty = (
                    f'    "{field}": '
                    + json.dumps(value, ensure_ascii=False, indent=2).replace(
                        "\n", "\n    "
                    )
                )
                compact = f'    "{field}": ' + json.dumps(
                    value,
                    ensure_ascii=False,
                    separators=(", ", ": "),
                )
                text = text.replace(pretty, compact, 1)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    for path in (SOURCE, ASSETS, EXTERNAL, LOCAL_ANALYSIS, LOCAL_V2, KIMI_ANALYSIS, KIMI_QUALIFICATION):
        if not path.is_file():
            raise RuntimeError(f"missing terminal evidence: {path}")

    registry = load(SOURCE)
    if any(
        row.get("failure_id") in {
            "R17-F014-LOCAL-QWEN3-EVALUATOR-FLOOR",
            "R17-F015-KIMI-EVALUATOR-CEILING",
        }
        for row in registry["entries"]
    ):
        raise RuntimeError("evaluator qualification failures already registered")

    registry["schema_version"] = "1.6"
    registry["date"] = "2026-08-30"
    registry["supersedes"] = {"path": rel(SOURCE), "sha256": sha(SOURCE)}
    registry["current_scientific_state"][
        "evaluator_replacement_qualification"
    ] = "STOP_LOCAL_QWEN3_FLOOR_AND_KIMI_K3_CEILING_NO_HELDOUT_EXECUTION"
    registry["entries"].extend(
        [
            {
                "failure_id": "R17-F014-LOCAL-QWEN3-EVALUATOR-FLOOR",
                "stage": "local replacement evaluator development qualification",
                "classification": ["MEASUREMENT_ANALYSIS", "RUNTIME_INFRA"],
                "terminal_status": "FAIL_LOCAL_EVALUATOR_RUNTIME_QUALIFICATION",
                "symptom": (
                    "The exact local Qwen3-8B runtime was transport-stable after "
                    "pre-outcome tool-call-ID canonicalization but solved 0/6 fixed "
                    "development tasks."
                ),
                "root_cause": (
                    "The candidate lacks the minimum multi-task competence needed for "
                    "the frozen SpreadsheetBench nuisance endpoint under the fixed "
                    "runtime, skill and turn budget."
                ),
                "contamination": (
                    "NONE; development tasks only, no heldout probes, updater, MRW or "
                    "scientific outcome."
                ),
                "provider_calls": (
                    "62 local HTTP requests; zero hosted provider requests for this candidate"
                ),
                "scientific_endpoint_reached": False,
                "scientific_data_observed_for_effectiveness": False,
                "scientific_belief_update": "NONE",
                "repair_or_stop": (
                    "Stop the local-Qwen3 evaluator branch. Stable transport is not "
                    "evaluator qualification when the fixed competence floor fails."
                ),
                "rerun_policy": (
                    "NO HELDOUT EXECUTION OR SAME-CANDIDATE RERUN UNDER THIS "
                    "QUALIFICATION; NO MODEL SHOPPING"
                ),
                "reusable_rule": (
                    "Canonicalize irrelevant transport entropy before outcomes, then "
                    "require task competence and headroom; byte-stable responses alone "
                    "do not qualify a scientific evaluator."
                ),
                "preserved_artifacts": [
                    {"path": rel(LOCAL_ANALYSIS), "sha256": sha(LOCAL_ANALYSIS)},
                    {"path": rel(LOCAL_V2), "sha256": sha(LOCAL_V2)},
                ],
            },
            {
                "failure_id": "R17-F015-KIMI-EVALUATOR-CEILING",
                "stage": "hosted replacement evaluator development qualification",
                "classification": ["MEASUREMENT_ANALYSIS", "RUNTIME_INFRA"],
                "terminal_status": "FAIL_HOSTED_EVALUATOR_DEVELOPMENT_QUALIFICATION",
                "symptom": (
                    "Kimi-K3 scored 18/18 on the fixed six-family development sample, "
                    "leaving no nondegenerate headroom; one of 102 calls was provider-"
                    "incomplete at the 4096-token cap."
                ),
                "root_cause": (
                    "The frozen development sample is saturated for this candidate and "
                    "cannot demonstrate the discrimination needed for the nuisance-"
                    "equivalence endpoint. Provider completion also failed its exact gate."
                ),
                "contamination": (
                    "NONE; development tasks only. No heldout probes, updater, negative-"
                    "control outcome, MRW, or central-mechanism outcome were accessed."
                ),
                "provider_calls": 102,
                "scientific_endpoint_reached": False,
                "scientific_data_observed_for_effectiveness": False,
                "scientific_belief_update": (
                    "NONE; the historical negative-control HOLD and UNKNOWN central "
                    "mechanism are preserved."
                ),
                "repair_or_stop": (
                    "Stop the evaluator-switch branch. Do not replace tasks, relax the "
                    "gate, rerun Kimi, shop another model, or access heldout data."
                ),
                "rerun_policy": (
                    "NO SAME-CANDIDATE RERUN, TASK REPLACEMENT, MODEL SHOPPING, "
                    "MARGIN CHANGE, OR HELDOUT EXECUTION"
                ),
                "reusable_rule": (
                    "Evaluator qualification requires both competence and nondegenerate "
                    "task headroom plus completed provider states. A perfect score can "
                    "be a qualification failure when it destroys measurement resolution."
                ),
                "preserved_artifacts": [
                    {"path": rel(KIMI_ANALYSIS), "sha256": sha(KIMI_ANALYSIS)},
                    {
                        "path": rel(KIMI_QUALIFICATION),
                        "sha256": sha(KIMI_QUALIFICATION),
                    },
                ],
            },
        ]
    )
    registry["permanent_rules"].append(
        "Before a replacement evaluator can touch heldout scientific data, its fixed "
        "development qualification must show competence, nondegenerate headroom, "
        "repeat stability, and completed provider states. Both floor and ceiling "
        "saturation fail; observed failure cannot be repaired by task/model shopping."
    )
    registry["predeclared_next_endpoint_policy"][
        "evaluator_switch_branch"
    ] = {
        "status": "STOP_AFTER_TWO_PREDECLARED_CANDIDATE_FAILURES",
        "local_qwen3": "FAIL_COMPETENCE_FLOOR",
        "hosted_kimi_k3": "FAIL_HEADROOM_CEILING_AND_PROVIDER_COMPLETION",
        "heldout_accessed": False,
        "scientific_belief_update": "NONE",
        "mrw_authorized": False,
    }
    write(OUTPUT, registry)

    assets = load(ASSETS)
    assets["source_registry"] = {
        "path": rel(OUTPUT),
        "role": (
            "R17 terminal attempt ledger through local and hosted replacement-evaluator "
            "development qualification; institutional assets remain zero-authority"
        ),
    }
    assets["evaluator_qualification_asset"] = {
        "signature": (
            "measurement:evaluator-qualification-needs-competence-headroom-and-completion"
        ),
        "idea_id": "E2-R17",
        "diagnosis": "replacement-evaluator-floor-or-ceiling-saturation",
        "affected_layer": "measurement",
        "reusable_precheck": (
            "Before a replacement evaluator sees heldout data, freeze a development "
            "sample and require multi-task competence, nondegenerate pooled headroom, "
            "repeat stability, and completed provider states. Canonicalize only "
            "outcome-irrelevant transport entropy before the test. Fail closed at either "
            "0% or 100% saturation and do not retune tasks or shop models after outcomes."
        ),
        "evidence_ref": (
            "generated/e2-r17-failure-differential-registry-v8-20260830.json"
            "#R17-F014-LOCAL-QWEN3-EVALUATOR-FLOOR,"
            "#R17-F015-KIMI-EVALUATOR-CEILING"
        ),
        "does_not_imply": (
            "central-mechanism failure, historical negative-control invalidity, or "
            "permission to access heldout data with an unqualified evaluator"
        ),
        "memory_scope": "institutional-research-memory",
        "reuse_scope": {
            "diagnosis": "evaluator-qualification-resolution-failure",
            "affected_layer": "measurement",
            "applies_to": "agent benchmarks and stochastic evaluator substitutions",
        },
        "reuse_effectiveness": {
            "reuse_count": 0,
            "helped_count": 0,
            "hurt_count": 0,
            "status": "newly-recorded-policy-not-yet-reused",
        },
        "superseded_by": "",
        "last_revalidated": "2026-08-30",
        "source_decision": "STOP_EVALUATOR_SWITCH_BRANCH",
        "scientific_authority": False,
    }
    asset_keys = [
        "final_visible_budget_asset",
        "causal_provenance_asset",
        "provider_budget_asset",
        "role_runtime_asset",
        "zero_missing_asset",
        "review_layer_asset",
        "execution_faithful_preflight_asset",
        "duplicate_launch_asset",
        "negative_control_identifiability_asset",
        "evaluator_qualification_asset",
    ]
    field_order = [
        "signature",
        "idea_id",
        "diagnosis",
        "affected_layer",
        "reusable_precheck",
        "evidence_ref",
        "does_not_imply",
        "memory_scope",
        "reuse_scope",
        "reuse_effectiveness",
        "superseded_by",
        "last_revalidated",
        "source_decision",
        "scientific_authority",
    ]
    ordered_assets: dict[str, Any] = {
        "schema_version": assets["schema_version"],
        "source_registry": {
            "path": assets["source_registry"]["path"],
            "role": assets["source_registry"]["role"],
        },
    }
    for key in asset_keys:
        row = assets[key]
        ordered_row = {field: row[field] for field in field_order if field in row}
        if "reuse_scope" in ordered_row:
            scope = ordered_row["reuse_scope"]
            ordered_row["reuse_scope"] = {
                field: scope[field]
                for field in ("diagnosis", "affected_layer", "applies_to")
                if field in scope
            }
        if "reuse_effectiveness" in ordered_row:
            effect = ordered_row["reuse_effectiveness"]
            ordered_row["reuse_effectiveness"] = {
                field: effect[field]
                for field in ("reuse_count", "helped_count", "hurt_count", "status")
                if field in effect
            }
        ordered_assets[key] = ordered_row
    ordered_assets["scientific_authority"] = assets["scientific_authority"]
    assets = ordered_assets
    write(ASSETS, assets)

    external = load(EXTERNAL)
    item = {
        "source_path": rel(ASSETS),
        "source_key": "evaluator_qualification_asset",
    }
    if item not in external["assets"]:
        external["assets"].append(item)
    external = {
        "schema_version": external["schema_version"],
        "policy": {
            field: external["policy"][field]
            for field in (
                "entries_are_zero_authority_institutional_memory_inputs",
                "entries_cannot_create_or_promote_candidates",
                "entries_cannot_authorize_problem_gate_method_experiment_provider_or_gpu",
                "entries_must_be_scope_bound_and_layer_typed",
                "external_or_auxiliary_negative_runs_may_enter_memory_without_mutating_active_scientific_state",
            )
        },
        "assets": [
            {
                "source_path": row["source_path"],
                "source_key": row["source_key"],
            }
            for row in external["assets"]
        ],
        "scientific_authority": external["scientific_authority"],
    }
    write(EXTERNAL, external)

    print(
        json.dumps(
            {
                "registry": rel(OUTPUT),
                "registry_sha256": sha(OUTPUT),
                "entries": len(registry["entries"]),
                "assets": rel(ASSETS),
                "assets_sha256": sha(ASSETS),
                "external_assets": rel(EXTERNAL),
                "external_assets_sha256": sha(EXTERNAL),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
