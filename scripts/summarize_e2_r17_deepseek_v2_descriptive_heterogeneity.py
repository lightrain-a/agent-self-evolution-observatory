#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PRIMARY_STATUS = "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS"
SUPPORT_STATUS = "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT"
OUTPUT_STATUS = "DESCRIPTIVE_HETEROGENEITY_ONLY_PRIMARY_HOLD_UNCHANGED"
FAMILY_BY_PREFIX = {
    "agj": "aggregation_join",
    "fmv": "formula_materialization",
    "ioc": "input_output_contract",
    "msp": "multi_step_pipeline",
    "ska": "schema_key_alignment",
    "tsr": "target_sheet_range",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    require(not path.exists(), f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def family_for(stream_id: str) -> str:
    prefix = stream_id.split("-")[1]
    require(prefix in FAMILY_BY_PREFIX, f"unknown stream family prefix: {stream_id}")
    return FAMILY_BY_PREFIX[prefix]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", type=Path, required=True)
    ap.add_argument("--support", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    analysis = load(args.analysis)
    support = load(args.support)
    require(analysis.get("status") == PRIMARY_STATUS, "primary analysis is not the frozen HOLD result")
    require(support.get("status") == SUPPORT_STATUS, "pre-outcome E1-A support artifact is not passing")
    mixed = support["primary_support"]["per_stream_mixed_recomputed"]
    require(len(mixed) == 12, "expected 12 pre-outcome mixed-dose streams")
    require(support["family_generalization"].get("pass") is True, "pre-outcome family support not qualified")

    stream_rows: list[dict[str, Any]] = []
    family_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in analysis["per_stream"]:
        stream_id = str(row["stream_id"])
        require(stream_id in mixed, f"missing pre-outcome mixed dose: {stream_id}")
        family = family_for(stream_id)
        out = {
            "stream_id": stream_id,
            "family": family,
            "mixed_pools_out_of_8_pre_outcome": int(mixed[stream_id]),
            "mixed_fraction_pre_outcome": int(mixed[stream_id]) / 8.0,
            "mean_difference_mrw_minus_win_c": float(row["mean_difference_mrw_minus_win_c"]),
            "replicate_differences": [float(x) for x in row["replicate_differences"]],
        }
        stream_rows.append(out)
        family_rows[family].append(out)

    family_summary = []
    for family in sorted(family_rows):
        rows = family_rows[family]
        require(len(rows) == 2, f"family must contain exactly two descriptive streams: {family}")
        family_summary.append({
            "family": family,
            "streams": [r["stream_id"] for r in rows],
            "pre_outcome_mixed_pools_total_out_of_16": sum(r["mixed_pools_out_of_8_pre_outcome"] for r in rows),
            "mean_stream_effect_mrw_minus_win_c": sum(r["mean_difference_mrw_minus_win_c"] for r in rows) / 2.0,
            "stream_effects": [r["mean_difference_mrw_minus_win_c"] for r in rows],
        })

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-descriptive-heterogeneity-report",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": OUTPUT_STATUS,
        "primary_scientific_status": PRIMARY_STATUS,
        "primary_status_changed": False,
        "pre_outcome_support_artifact": str(args.support),
        "analysis_artifact": str(args.analysis),
        "predeclared_role": "per-stream mixed dose and effect; descriptive family grouping only",
        "stream_rows": stream_rows,
        "family_summary": family_summary,
        "direction_counts_from_frozen_primary_analysis": analysis["direction_counts"],
        "restrictions": {
            "new_significance_tests": False,
            "family_specific_significance_claim": False,
            "favorable_subset_selection": False,
            "posthoc_regime_law_claim": False,
            "primary_hold_rescue": False,
            "second_backbone_authority": False,
            "public_benchmark_authority": False,
            "e3_prospective_regime_prediction_authority": False,
        },
        "interpretation": (
            "The preregistered descriptive view shows substantial stream/family variation around a positive aggregate point estimate. "
            "It is compatible with heterogeneity but does not establish a moderator, dose-response law, family-specific effect, or causal regime law, "
            "and it cannot change the frozen HOLD primary verdict."
        ),
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
