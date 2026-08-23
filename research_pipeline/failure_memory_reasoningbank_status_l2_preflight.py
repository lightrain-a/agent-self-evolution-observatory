"""Zero-call preflight for a native ReasoningBank status-metadata L2 extension.

This module does not execute a model or a browser. It verifies the pinned
first-party ReasoningBank source contract and constructs a fresh,
template-independent downstream cohort from the frozen WebArena Shopping asset.

The new object is separate from historical R5. R5 remains a 5/10 support stop.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable

PAPER_ID = "D2-PAPER-FAILURE-MEMORY-PROVENANCE"
PREFLIGHT_ID = "D2-C45-REASONINGBANK-STATUS-L2-PREFLIGHT-R9"
EXPECTED_PARQUET_SHA256 = "fc9b0011d384403f21534529da0397ca2aabf29fcb30c2dbb5a3c01c30b1387e"
EXPECTED_PARQUET_ROWS = 187
EXPECTED_REASONINGBANK_COMMIT = "ed80611788292ea739f1effd31f16c53823b8a0d"
EXPECTED_SOURCE_SHAS = {
    "WebArena/induce_memory.py": "97d7da3fe5bd3e37d05e4aa07c050b1154334951cc2cad20619774ae77e0912c",
    "WebArena/memory_management.py": "35b8b800180024f3446c4a295fe9d7c19d4aa2cddd0b2f2a44b6680e4d6bc4f9",
    "WebArena/run.py": "f9edcac62cc612f48db9859c60f71b7479aa126beda802437dd82d81030817b3",
}

# Any task considered by a prior D2 downstream experiment/support gate is kept
# out of the new inference cohort. A prior task may be used as an upstream
# source-memory episode because it is not a new downstream inference unit.
PRIOR_D2_IDS = frozenset(
    map(
        str,
        [
            # R4 outcome-blind candidates, including pre-outcome exclusions.
            385, 387, 167, 23, 388, 164,
            # Historical explicit-cue bridge.
            125, 360, 228, 126, 362, 229,
            # R6 candidate cohort, including the support-failed verifier unit.
            48, 49, 117, 145, 148, 149, 150, 159, 162, 190, 191, 225, 226,
            227, 230, 231, 233, 234, 235, 298, 299, 301, 302, 313,
            # R5 support-audited but unexecuted units; exclude for maximal freshness.
            21, 25, 26, 163, 165,
        ],
    )
)
EXPECTED_DOWNSTREAM_IDS = [
    "166", "351", "238", "269", "431", "329", "653", "528", "146", "436",
    "124", "319", "141", "689", "571", "334", "158", "506", "300", "465",
    "511", "794", "585", "516", "47", "279", "358", "284", "324", "260",
    "274", "232", "188", "509", "22", "384",
]
EXPECTED_SOURCE_IDS = [
    "163", "352", "239", "270", "432", "330", "654", "529", "148", "437",
    "125", "320", "145", "690", "572", "335", "159", "507", "298", "466",
    "512", "795", "586", "517", "48", "280", "360", "285", "325", "261",
    "275", "231", "190", "510", "21", "385",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def _json_object(value: Any) -> bool:
    try:
        obj = json.loads(value) if isinstance(value, str) else value
    except Exception:
        return False
    return isinstance(obj, dict)


def verify_reasoningbank_source(root: Path) -> dict[str, Any]:
    head = _git_head(root)
    if head != EXPECTED_REASONINGBANK_COMMIT:
        raise ValueError(f"ReasoningBank commit drift: {head}")
    shas = {rel: sha256(root / rel) for rel in EXPECTED_SOURCE_SHAS}
    if shas != EXPECTED_SOURCE_SHAS:
        raise ValueError(f"ReasoningBank source digest drift: {shas}")

    induce = (root / "WebArena/induce_memory.py").read_text(encoding="utf-8")
    select = (root / "WebArena/memory_management.py").read_text(encoding="utf-8")
    run = (root / "WebArena/run.py").read_text(encoding="utf-8")
    checks = {
        "status_is_derived_from_reward": 'status = "success"' in induce and 'status = "fail"' in induce,
        "status_is_stored_separately": '"status": ex["status"]' in induce and '"memory_items": generated_memory_item.split' in induce,
        "selection_maps_id_back_to_full_record": "out.append(reasoning_bank[i])" in select,
        "default_recall_serializes_memory_items": 'for i in item["memory_items"]' in run,
        "default_recall_does_not_serialize_status": 'item["status"]' not in run,
    }
    if not all(checks.values()):
        raise ValueError(f"ReasoningBank source contract failed: {checks}")
    return {
        "repository": "https://github.com/google-research/reasoning-bank.git",
        "commit": head,
        "file_sha256": shas,
        "contract_checks": checks,
        "interpretation": (
            "The first-party WebArena writer stores source outcome in a separate status field; "
            "select_memory returns the full record; the default run path exposes only memory_items "
            "to the agent and therefore drops status."
        ),
    }


def build_cohort(
    records: Iterable[dict[str, Any]],
    configs: Iterable[dict[str, Any]],
    *,
    prior_ids: frozenset[str] = PRIOR_D2_IDS,
) -> list[dict[str, Any]]:
    """Build one fresh downstream unit per intent template without using its outcome.

    Source assignment is deterministic: prefer the smallest prior-D2 task from
    the same template, otherwise use the smallest other task. Source outcome is
    read only *after* source/downstream IDs are fixed, to describe the native
    status that would be stored in the source memory record.
    """
    cfg = {str(x["task_id"]): dict(x) for x in configs}
    raw = [dict(x) for x in records]
    by_template: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)

    for row in raw:
        tid = str(row.get("task_id") or "").strip()
        if not tid or tid not in cfg:
            continue
        c = cfg[tid]
        template = str(c.get("intent_template_id") or "").strip()
        prompt = str(row.get("task_prompt") or "").strip()
        eval_types = list((c.get("eval") or {}).get("eval_types") or [])
        if not template or not prompt or not _json_object(row.get("trajectory_json")):
            continue
        # Do not carry the downstream outcome into candidate selection.
        by_template[template].append(
            {
                "task_id": tid,
                "template_id": template,
                "task_prompt": prompt,
                "eval_types": eval_types,
                "prior_d2": tid in prior_ids,
                "trajectory_parseable": True,
                "_source_status": "success" if bool(row.get("is_successful")) else "fail",
            }
        )

    out: list[dict[str, Any]] = []
    for template, items in sorted(by_template.items(), key=lambda kv: int(kv[0])):
        downstream_candidates = sorted(
            [x for x in items if not x["prior_d2"] and x["eval_types"]],
            key=lambda x: int(x["task_id"]),
        )
        if not downstream_candidates:
            continue
        downstream = downstream_candidates[0]

        prior_sources = sorted(
            [x for x in items if x["task_id"] != downstream["task_id"] and x["prior_d2"]],
            key=lambda x: int(x["task_id"]),
        )
        other_sources = sorted(
            [x for x in items if x["task_id"] != downstream["task_id"] and not x["prior_d2"]],
            key=lambda x: int(x["task_id"]),
        )
        source_pool = prior_sources or other_sources
        if not source_pool:
            continue
        source = source_pool[0]

        out.append(
            {
                "template_id": template,
                "downstream_task_id": downstream["task_id"],
                "downstream_task_prompt": downstream["task_prompt"],
                "downstream_eval_types": downstream["eval_types"],
                "source_task_id": source["task_id"],
                "source_task_was_prior_d2": bool(source["prior_d2"]),
                "source_native_status": source["_source_status"],
                "template_task_count": len(items),
                "fresh_downstream_candidates_in_template": len(downstream_candidates),
                "selection_uses_downstream_outcome": False,
                "selection_uses_source_outcome": False,
            }
        )
    return out


def build_preflight(
    records: list[dict[str, Any]],
    configs: list[dict[str, Any]],
    *,
    parquet_path: Path,
    config_path: Path,
    reasoningbank_root: Path,
) -> dict[str, Any]:
    source_sha = sha256(parquet_path)
    if source_sha != EXPECTED_PARQUET_SHA256:
        raise ValueError("frozen parquet digest mismatch")
    if len(records) != EXPECTED_PARQUET_ROWS:
        raise ValueError("frozen parquet row-count drift")

    rb = verify_reasoningbank_source(reasoningbank_root)
    cohort = build_cohort(records, configs)
    downstream_ids = [x["downstream_task_id"] for x in cohort]
    source_ids = [x["source_task_id"] for x in cohort]
    if downstream_ids != EXPECTED_DOWNSTREAM_IDS or source_ids != EXPECTED_SOURCE_IDS:
        raise ValueError("cohort drift")

    eval_counts = collections.Counter("+".join(x["downstream_eval_types"]) for x in cohort)
    status_counts = collections.Counter(x["source_native_status"] for x in cohort)
    source_prior = sum(1 for x in cohort if x["source_task_was_prior_d2"])

    return {
        "schema_version": "1.0",
        "paper_id": PAPER_ID,
        "preflight_id": PREFLIGHT_ID,
        "recorded_date": "2026-08-24",
        "status": "NATIVE_STATUS_FIELD_AND_36_UNIT_COHORT_VERIFIED_EXECUTION_BLOCKED",
        "role": "ZERO_CALL_SUPPORT_AND_DESIGN_PREFLIGHT_NO_SCIENTIFIC_AUTHORITY",
        "scientific_relationship": "NEW_L2B_R9_EXTENSION_NOT_R5_RESCUE_NOT_L3_TRANSPORT",
        "first_party_reasoningbank_binding": rb,
        "frozen_downstream_asset": {
            "path_role": "content-addressed WebArena Shopping trajectory/task universe",
            "sha256": source_sha,
            "rows": len(records),
            "config_sha256": sha256(config_path),
        },
        "native_metadata_fact": {
            "field": "status",
            "native_values": ["success", "fail"],
            "meaning": "terminal outcome of the trajectory from which the ReasoningBank memory record was written",
            "stored_separately_from_actionable_memory": True,
            "used_by_default_retrieval_selection": False,
            "visible_to_default_downstream_agent": False,
            "adapter_required": True,
        },
        "candidate_intervention": {
            "estimand": "Delta_L(status; m, x') with actionable memory m held byte-identical",
            "treatment": "Expose the already-native source-outcome status field as success versus fail while holding the selected record and memory_items bytes fixed.",
            "paired_hold_fixed": [
                "downstream task/query and WebArena initial state",
                "source memory record ID",
                "ordered memory_items bytes",
                "retrieval/admission result and order",
                "all non-status prompt bytes",
                "executor/model/version/decoding settings",
                "WebArena evaluator and reset protocol",
            ],
            "forbidden_changes": [
                "re-run retrieval separately by arm",
                "change memory text or source memory ID by arm",
                "let status alter ranking/admission",
                "use downstream outcomes to replace tasks",
                "pool with R5 or the historical six-task explicit-cue bridge",
            ],
            "draft_renderer": {
                "L_S": "status: success\\n<memory_items bytes unchanged>",
                "L_F": "status: fail\\n<memory_items bytes unchanged>",
                "note": "Renderer is a preflight proposal, not yet a frozen execution contract.",
            },
        },
        "cohort_contract": {
            "independent_unit": "one fresh downstream task per intent_template_id",
            "prior_d2_downstream_ids_excluded": sorted(PRIOR_D2_IDS, key=int),
            "source_assignment": "within template: prefer smallest prior-D2 source task, else smallest other task; source assignment ignores source outcome",
            "downstream_assignment": "smallest fresh task ID with a non-empty official WebArena evaluator",
            "downstream_selection_uses_outcome": False,
            "source_selection_uses_outcome": False,
            "source_outcome_read_after_assignment_only": True,
            "state_mutating_tasks_allowed": True,
            "state_mutation_reason": "The planned endpoint is the source-native WebArena runtime/evaluator with environment reset; read-only was a static-evidence bridge restriction, not a WebArena scientific requirement.",
        },
        "cohort_summary": {
            "template_independent_units": len(cohort),
            "downstream_task_ids": downstream_ids,
            "source_task_ids": source_ids,
            "official_evaluator_counts": dict(sorted(eval_counts.items())),
            "source_native_status_counts": dict(sorted(status_counts.items())),
            "sources_reusing_prior_d2_as_upstream_only": source_prior,
            "sources_from_other_noninference_tasks": len(cohort) - source_prior,
            "historical_r5_support_floor": 10,
            "r7_l1_power_reference_one_sided_sd_0_30": 25,
            "r7_l1_power_reference_two_sided_sd_0_30": 32,
            "l2_power_claim_from_l1_reference_allowed": False,
        },
        "cohort": cohort,
        "runtime_materialization": {
            "required_first_party_versions": {
                "python": ">=3.13",
                "browsergym-core": "0.14.1",
                "browsergym-experiments": "0.14.1",
                "browsergym-webarena": "0.14.1",
                "browsergym": "0.14.1",
            },
            "current_69_exact_runtime_found": False,
            "current_69_exact_runtime_cached": False,
            "current_69_nearby_runtime": "Agent-Safety runtime-r9 has browsergym-core 0.4.0 / Python 3.12.3; version-mismatched and forbidden as a source-faithful substitute.",
            "support_engineering_materialization_requires_scientific_authority": False,
            "materialization_attempted": False,
            "dependency_download_deferred": True,
            "reason": "No Python 3.13 or BrowserGym/WebArena 0.14.1 package cache was found on 69. Import-only runtime materialization is support engineering, but a new dependency download was deferred in this zero-call preflight; no browser task was started.",
        },
        "analysis_gate_before_execution": {
            "support_capacity_dead_end": False,
            "cohort_frozen_pre_outcome": True,
            "l2_specific_power_plan_still_required": True,
            "runtime_0_14_1_materialization_still_required": True,
            "memory_generation_and_embedding_or_fixed_source_selection_binding_still_required": True,
            "exact_executor_and_request_budget_still_required": True,
            "terminal_randomization_test_and_effect_gate_still_required": True,
            "scientific_reopen_still_required": True,
            "experiment_model_call_authority_still_required": True,
        },
        "strongest_allowed_current_statement": (
            "At the pinned first-party ReasoningBank commit, source trajectory outcome is a native metadata field separate from memory_items and omitted only by the default downstream serialization. "
            "A deterministic zero-call census identifies 36 fresh template-independent WebArena Shopping downstream units for a new adapter-level L2 experiment. "
            "This removes the historical R5 support-capacity dead-end but does not itself establish a provenance-metadata effect or authorize execution."
        ),
        "scientific_verdict": "NO_VERDICT_PREFLIGHT_ONLY",
        "authority": {
            "scientific": False,
            "experiment": False,
            "model_calls": False,
            "gpu": False,
            "submission": False,
        },
    }


def load_parquet(path: Path) -> list[dict[str, Any]]:
    import pandas as pd  # type: ignore
    return [dict(x) for x in pd.read_parquet(path).to_dict(orient="records")]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source-parquet", type=Path, required=True)
    p.add_argument("--task-config", type=Path, required=True)
    p.add_argument("--reasoningbank-root", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-reasoningbank-status-l2-preflight-r9.json"))
    args = p.parse_args()

    records = load_parquet(args.source_parquet)
    configs = json.loads(args.task_config.read_text(encoding="utf-8"))
    payload = build_preflight(
        records,
        configs,
        parquet_path=args.source_parquet,
        config_path=args.task_config,
        reasoningbank_root=args.reasoningbank_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "units": payload["cohort_summary"]["template_independent_units"],
        "source_status_counts": payload["cohort_summary"]["source_native_status_counts"],
        "runtime_exact_found": payload["runtime_materialization"]["current_69_exact_runtime_found"],
        "scientific_authority": payload["authority"]["scientific"],
        "model_calls": payload["authority"]["model_calls"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
