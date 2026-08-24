from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist
from typing import Any

from research_pipeline.failure_memory_reasoningbank_status_l2_preflight import PRIOR_D2_IDS

EXPECTED_PARQUET_SHA = "fc9b0011d384403f21534529da0397ca2aabf29fcb30c2dbb5a3c01c30b1387e"
EXPECTED_CONFIG_SHA = "d25e83078ec728adc82bd43871338a24a3907e101b5a5fdb1ae81bb7f72f36a6"
EXPECTED_R17_SHA = "58de4f998b16aace4ddfeef0693d88a347b293c032d997e0da471e6b92c69235"
EXPOSED_TEMPLATE = "136"
EXPOSED_DOWNSTREAM = "166"
TARGET_EFFECT = 0.15
ALPHA = 0.05


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_parquet(path: Path) -> list[dict[str, Any]]:
    import pandas as pd

    return pd.read_parquet(path).to_dict("records")


def parse_trajectory(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            x = json.loads(value)
        except Exception:
            return None
        return x if isinstance(x, dict) else None
    return None


def normal_two_sided_power(n: int, sd: float, effect: float = TARGET_EFFECT, alpha: float = ALPHA) -> float:
    nd = NormalDist()
    z = nd.inv_cdf(1 - alpha / 2)
    mu = effect * math.sqrt(n) / sd
    return (1 - nd.cdf(z - mu)) + nd.cdf(-z - mu)


def build_candidate(
    records: list[dict[str, Any]],
    configs: list[dict[str, Any]],
    r9: dict[str, Any],
    r17: dict[str, Any],
    r18c: dict[str, Any],
) -> dict[str, Any]:
    if r18c["scientific_verdict"] != "NO_VERDICT_POST_EXPOSURE_SUPPORT_FAILURE":
        raise RuntimeError("R18c STOP verdict drift")
    if r18c["frozen_policy_application"]["single_confirmatory_attempt_consumed"] is not True:
        raise RuntimeError("R18c did not consume prior confirmatory attempt")
    if r18c["authority"]["new_experiment"] is not False:
        raise RuntimeError("R18c unexpectedly authorizes a new experiment")
    if r17["status"] != "UNIFORM_36_MEMORY_REALIZATION_COMPLETE_EXACT_BYTES_BOUND":
        raise RuntimeError("R17 writer realization not complete")

    r9_rows = list(r9["cohort"])
    if len(r9_rows) != 36:
        raise RuntimeError("R9 cohort drift")
    cfg = {str(x["task_id"]): dict(x) for x in configs}
    by_template: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in records:
        tid = str(row.get("task_id") or "").strip()
        if not tid or tid not in cfg:
            continue
        c = cfg[tid]
        template = str(c.get("intent_template_id") or "").strip()
        eval_types = list((c.get("eval") or {}).get("eval_types") or [])
        if not template or not eval_types or parse_trajectory(row.get("trajectory_json")) is None:
            continue
        by_template[template].append(
            {
                "task_id": tid,
                "eval_types": eval_types,
                "sites": list(c.get("sites") or []),
                "prior_d2": tid in PRIOR_D2_IDS,
            }
        )

    old_downstream = {str(x["downstream_task_id"]) for x in r9_rows}
    memory_by_source = {str(x["source_task_id"]): x for x in r17["source_memory_manifest"]}
    if len(memory_by_source) != 36:
        raise RuntimeError("R17 source-memory manifest drift")

    rows: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for old in r9_rows:
        template = str(old["template_id"])
        source = str(old["source_task_id"])
        old_down = str(old["downstream_task_id"])
        if template == EXPOSED_TEMPLATE or old_down == EXPOSED_DOWNSTREAM:
            excluded.append(
                {
                    "template_id": template,
                    "source_task_id": source,
                    "old_downstream_task_id": old_down,
                    "reason": "R18c scientific exposure occurred in this template; exclude the entire template from any R19 candidate.",
                }
            )
            continue
        if source not in memory_by_source:
            raise RuntimeError(f"R17 memory missing source {source}")

        alternatives = sorted(
            [
                x
                for x in by_template[template]
                if not x["prior_d2"]
                and x["task_id"] not in old_downstream
                and x["task_id"] != source
                and x["task_id"] != EXPOSED_DOWNSTREAM
            ],
            key=lambda x: int(x["task_id"]),
        )
        if alternatives:
            chosen = alternatives[0]
            selection = "SECOND_FRESH_CANDIDATE_SOURCE_AND_R9_DOWNSTREAM_EXCLUDED"
            changed = True
        else:
            retained = next(
                (
                    x
                    for x in by_template[template]
                    if x["task_id"] == old_down and x["task_id"] != source and x["task_id"] != EXPOSED_DOWNSTREAM
                ),
                None,
            )
            if retained is None:
                raise RuntimeError(f"No legal R19 downstream candidate for template {template}")
            chosen = retained
            selection = "RETAIN_UNEXPOSED_R9_DOWNSTREAM_NO_LEGAL_SECOND_CANDIDATE"
            changed = False

        mem = memory_by_source[source]
        rows.append(
            {
                "template_id": template,
                "source_task_id": source,
                "source_native_status": old["source_native_status"],
                "source_memory_record_sha256": mem["memory_record_sha256"],
                "source_memory_joined_bytes_sha256": mem["joined_memory_bytes_sha256"],
                "r9_downstream_task_id": old_down,
                "r19_downstream_task_id": chosen["task_id"],
                "downstream_changed_from_r9": changed,
                "selection_rule": selection,
                "official_eval_types": chosen["eval_types"],
                "sites": chosen["sites"],
                "legal_alternative_count_after_exclusions": len(alternatives),
                "downstream_equals_source": chosen["task_id"] == source,
                "downstream_was_r18c_exposed": chosen["task_id"] == EXPOSED_DOWNSTREAM,
                "downstream_was_prior_d2": chosen["task_id"] in PRIOR_D2_IDS,
                "selection_uses_r18c_action_or_outcome": False,
                "selection_uses_any_downstream_outcome": False,
            }
        )

    if len(rows) != 35 or len(excluded) != 1:
        raise RuntimeError(f"Unexpected R19 capacity: {len(rows)} rows / {len(excluded)} excluded")
    downstream_ids = [x["r19_downstream_task_id"] for x in rows]
    if len(set(downstream_ids)) != 35:
        raise RuntimeError("R19 downstream IDs are not unique")
    if any(x["downstream_equals_source"] or x["downstream_was_r18c_exposed"] or x["downstream_was_prior_d2"] for x in rows):
        raise RuntimeError("R19 leakage/freshness invariant failed")
    if any(x["sites"] != ["shopping"] for x in rows):
        raise RuntimeError("R19 contains a non-Shopping downstream task")
    changed = sum(bool(x["downstream_changed_from_r9"]) for x in rows)
    retained = len(rows) - changed
    if changed != 30 or retained != 5:
        raise RuntimeError(f"R19 changed/retained drift: {changed}/{retained}")

    eval_counts = collections.Counter("+".join(x["official_eval_types"]) for x in rows)
    status_counts = collections.Counter(x["source_native_status"] for x in rows)
    sensitivity = [
        {
            "task_level_sd": sd,
            "independent_tasks": 35,
            "approx_two_sided_power": round(normal_two_sided_power(35, sd), 6),
        }
        for sd in (0.2, 0.3, 0.4)
    ]

    return {
        "schema_version": "1.0",
        "paper_id": "D2-PAPER-FAILURE-MEMORY-PROVENANCE",
        "receipt_id": "D2-FAILURE-MEMORY-PROVENANCE-L2B-R19-HYBRID-FRESH-COHORT-CANDIDATE",
        "recorded_date": "2026-08-24",
        "status": "R19_35_TEMPLATE_HYBRID_FRESH_COHORT_AVAILABLE_NEW_AUTHORITY_REQUIRED",
        "role": "ZERO_OUTCOME_POST_STOP_REOPEN_CAPACITY_CENSUS",
        "scientific_relationship": "NEW_EXPERIMENT_CANDIDATE_NOT_R18_RETRY_NOT_R5_RESCUE",
        "parent_state": {
            "R18c_status": r18c["status"],
            "R18c_scientific_verdict": r18c["scientific_verdict"],
            "prior_single_confirmatory_attempt_consumed": True,
            "prior_exposed_template_id": EXPOSED_TEMPLATE,
            "prior_exposed_downstream_task_id": EXPOSED_DOWNSTREAM,
        },
        "selection_contract": {
            "one_downstream_per_intent_template": True,
            "exclude_entire_R18c_exposed_template": True,
            "exclude_all_PRIOR_D2_IDS_from_new_alternatives": True,
            "exclude_all_R9_downstream_ids_from_new_alternatives": True,
            "exclude_frozen_source_task_id_from_its_downstream_candidate": True,
            "for_each_remaining_template_choose_smallest_legal_new_task_id": True,
            "if_no_legal_new_candidate_retain_original_R9_downstream_only_if_never_exposed_and_source_distinct": True,
            "outcome_blind": True,
            "R18c_step_action_or_reward_read_for_selection": False,
            "threshold_or_effect_used_for_selection": False,
        },
        "capacity": {
            "R9_templates": 36,
            "R18c_exposed_templates_excluded": 1,
            "R19_independent_template_units": 35,
            "new_downstream_ids_relative_to_R9": changed,
            "retained_unexposed_R9_downstream_ids": retained,
            "all_source_distinct_from_downstream": True,
            "all_downstream_ids_unique": True,
            "all_downstream_ids_have_official_evaluator": True,
            "all_downstream_tasks_shopping_only": True,
            "official_evaluator_counts": dict(sorted(eval_counts.items())),
            "source_native_status_counts": dict(sorted(status_counts.items())),
        },
        "excluded_templates": excluded,
        "retained_original_downstreams": [
            {
                "template_id": x["template_id"],
                "source_task_id": x["source_task_id"],
                "downstream_task_id": x["r19_downstream_task_id"],
            }
            for x in rows
            if not x["downstream_changed_from_r9"]
        ],
        "cohort": rows,
        "source_memory_policy": {
            "reuse_R17_exact_frozen_memory_bytes": True,
            "reason": "R17 memories were generated and frozen before any downstream L2 outcome; R19 changes only downstream inference units and does not regenerate or select memory content from R18c results.",
            "memory_regeneration_for_R19": False,
            "memory_edit_for_R19": False,
            "R17_sha256": EXPECTED_R17_SHA,
        },
        "power_sensitivity_only": {
            "target_absolute_effect": TARGET_EFFECT,
            "alpha": ALPHA,
            "approximation": "normal approximation for the paired task-level mean; confirmatory inference would require a newly frozen randomization contract",
            "scenarios": sensitivity,
            "unconditional_80pct_power_claim": False,
        },
        "support_preflight": {
            "executor_evaluator_aliases_prepared": True,
            "required_executor_manifest_digest": "sha256:5bce411d829007ce344871ae10ea7f02f91d86c932617a7f982e2380bbb1c216",
            "required_aliases": ["b1-qwen25-32b-l2b-executor:latest", "gpt-4:latest", "gpt-4-1106-preview:latest"],
            "must_reverify_alias_manifest_equality_immediately_before_any_future_execution": True,
        },
        "reopen_gate": {
            "new_pre_outcome_execution_contract_required": True,
            "new_explicit_scientific_and_experiment_authority_required": True,
            "current_R16_authority_reusable": False,
            "current_R18_schedule_reusable_as_authority": False,
            "R18_R18b_R18c_failure_chain_must_be_disclosed": True,
            "R18c_exposed_artifacts_must_not_enter_R19_selection_analysis_or_thresholds": True,
            "execution_permitted_now": False,
        },
        "strongest_allowed_current_statement": "After the R18 confirmatory attempt was stopped by a post-exposure evaluator support failure, a zero-outcome census identifies a 35-template candidate for a genuinely new L2B experiment: 30 downstream tasks are new relative to R9/R18, five retained tasks were never scientifically executed, the exposed template is excluded, and every downstream task is distinct from its frozen R17 source-memory task. This is capacity evidence only and does not authorize or establish a provenance effect.",
        "scientific_verdict": "NO_VERDICT_REOPEN_CAPACITY_ONLY",
        "scientific_authority": False,
        "experiment_authority": False,
        "submission_authority": False,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--parquet", type=Path, required=True)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--r9", type=Path, required=True)
    p.add_argument("--r17", type=Path, required=True)
    p.add_argument("--r18c", type=Path, required=True)
    p.add_argument("--output", type=Path, default=Path("generated/d2-failure-memory-provenance-l2b-r19-reopen-candidate.json"))
    args = p.parse_args()
    if sha256_file(args.parquet) != EXPECTED_PARQUET_SHA:
        raise RuntimeError("frozen parquet digest mismatch")
    if sha256_file(args.config) != EXPECTED_CONFIG_SHA:
        raise RuntimeError("frozen config digest mismatch")
    if sha256_file(args.r17) != EXPECTED_R17_SHA:
        raise RuntimeError("R17 receipt digest mismatch")
    records = load_parquet(args.parquet)
    configs = json.loads(args.config.read_text(encoding="utf-8"))
    r9 = json.loads(args.r9.read_text(encoding="utf-8"))
    r17 = json.loads(args.r17.read_text(encoding="utf-8"))
    r18c = json.loads(args.r18c.read_text(encoding="utf-8"))
    receipt = build_candidate(records, configs, r9, r17, r18c)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "units": receipt["capacity"]["R19_independent_template_units"],
        "new_downstreams": receipt["capacity"]["new_downstream_ids_relative_to_R9"],
        "retained_unexposed": receipt["capacity"]["retained_unexposed_R9_downstream_ids"],
        "execution_permitted": receipt["reopen_gate"]["execution_permitted_now"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
