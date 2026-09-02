#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

FIELDS = (
    "primary_failure_family",
    "profile_index",
    "procedure_depth_level",
    "distractor_level",
    "schema_ambiguity_level",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def flatten_split(split: dict[str, Any]) -> set[str]:
    used: set[str] = set()
    metadata_keys = {"rules", "selection_algorithm", "selection_is_outcome_blind", "suite_id", "schema_version"}

    def add(value: Any) -> None:
        if isinstance(value, list):
            used.update(map(str, value))
        elif isinstance(value, dict):
            for child in value.values():
                add(child)

    for key, value in split.items():
        if key not in metadata_keys:
            add(value)
    return used


def count_field(meta: dict[str, dict[str, Any]], task_ids: list[str], field: str) -> dict[str, int]:
    counts = Counter(str(meta[task][field]) for task in task_ids)
    return dict(sorted(counts.items()))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "panel-shift audit already exists")

    split = load_json(args.suite_root / "r17_split_manifest.json")
    metadata_rows = load_json(args.suite_root / "r17_controlled_metadata.json")
    meta = {str(row["id"]): row for row in metadata_rows}
    require(split.get("selection_is_outcome_blind") is True, "split is not outcome-blind")

    used = flatten_split(split)
    v2_panel = list(map(str, split["e1_common_heldout_probe"]))
    b4_universe = sorted(task for task, row in meta.items() if int(row["block"]) == 4)
    c0_panel = sorted(task for task in b4_universe if task not in used)

    require(len(b4_universe) == 54, "B4 universe must contain 54 tasks")
    require(len(v2_panel) == 18 and len(set(v2_panel)) == 18, "V2 panel cardinality drift")
    require(len(c0_panel) == 36 and len(set(c0_panel)) == 36, "C0 complement cardinality drift")
    require(not (set(v2_panel) & set(c0_panel)), "V2/C0 panels overlap")
    require(set(v2_panel) | set(c0_panel) == set(b4_universe), "V2+C0 do not partition the B4 universe")

    distributions = {
        field: {
            "v2_18": count_field(meta, v2_panel, field),
            "c0_36": count_field(meta, c0_panel, field),
        }
        for field in FIELDS
    }
    family = distributions["primary_failure_family"]
    require(set(family["v2_18"].values()) == {3}, "V2 family balance drift")
    require(set(family["c0_36"].values()) == {6}, "C0 family balance drift")

    profile_match = distributions["profile_index"]["v2_18"] == distributions["profile_index"]["c0_36"]
    factor_match = all(distributions[field]["v2_18"] == distributions[field]["c0_36"] for field in FIELDS[1:])

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-e3-b4-heldout-panel-shift-audit",
        "status": "PASS_ZERO_OUTCOME_CROSS_PANEL_SHIFT_EXPLICIT",
        "scientific_outcomes_read": False,
        "provider_calls": 0,
        "selection_is_outcome_blind": True,
        "b4_universe_count": 54,
        "v2_panel_count": 18,
        "c0_panel_count": 36,
        "v2_c0_overlap": 0,
        "panels_partition_b4_universe": True,
        "v2_panel_task_ids": v2_panel,
        "c0_panel_task_ids": c0_panel,
        "metadata_distributions": distributions,
        "profile_distribution_identical": profile_match,
        "factor_distributions_all_identical": factor_match,
        "interpretation": (
            "The V2 18-task and C0 36-task panels are disjoint outcome-blind complementary subsets of the same "
            "pre-existing 54-task B4 universe and are family-balanced, but their profile/factor distributions are not identical. "
            "C0 must therefore be interpreted as cross-stream plus cross-heldout-panel generalization."
        ),
        "authority": {
            "d0": False,
            "c0": False,
            "provider_io": False,
            "paper_promotion": False,
            "submission": False,
        },
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "b4_universe_count": 54,
        "v2_panel_count": 18,
        "c0_panel_count": 36,
        "profile_distribution_identical": profile_match,
        "factor_distributions_all_identical": factor_match,
        "scientific_outcomes_read": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
