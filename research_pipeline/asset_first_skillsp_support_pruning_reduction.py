from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--membership", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    rows = load_jsonl(args.membership)
    support = defaultdict(set)
    covered = set()
    for idx, row in enumerate(rows):
        for skill_id in row["accepted_skill_ids"]:
            support[skill_id].add(idx)
            covered.add(idx)
    skills = sorted(support)

    baseline_multi = sum(1 for idx in covered if sum(idx in support[s] for s in skills) > 1)
    full_cover_subsets = []
    for r in range(1, len(skills) + 1):
        for subset in itertools.combinations(skills, r):
            union = set().union(*(support[s] for s in subset))
            if union != covered:
                continue
            multi = sum(1 for idx in covered if sum(idx in support[s] for s in subset) > 1)
            full_cover_subsets.append((r, multi, subset))
        if full_cover_subsets:
            break

    min_size = min(x[0] for x in full_cover_subsets)
    min_multi = min(x[1] for x in full_cover_subsets if x[0] == min_size)
    best = [x for x in full_cover_subsets if x[0] == min_size and x[1] == min_multi]
    selected = list(best[0][2])

    mandatory = []
    for skill_id in skills:
        others = set().union(*(support[s] for s in skills if s != skill_id))
        unique = support[skill_id] - others
        if unique:
            mandatory.append({"skill_id": skill_id, "unique_rows": len(unique)})

    selected_pair_overlap = []
    for left, right in itertools.combinations(selected, 2):
        inter = support[left] & support[right]
        if inter:
            selected_pair_overlap.append({"left": left, "right": right, "shared_rows": len(inter)})

    result = {
        "schema_version": "1.0",
        "analysis_type": "strongest-simple-baseline deterministic reduction audit",
        "candidate_id": "skill-taxonomy-representation-invariance",
        "baseline": "minimum-cardinality whole-package support pruning under exact coverage preservation",
        "rows_total": len(rows),
        "covered_rows": len(covered),
        "active_skills_before": len(skills),
        "active_skill_ids_before": skills,
        "multi_membership_rows_before": baseline_multi,
        "minimum_full_coverage_skill_count": min_size,
        "minimum_multi_membership_rows_among_minimum_full_coverage_subsets": min_multi,
        "selected_skill_ids": selected,
        "selected_pair_overlap": selected_pair_overlap,
        "mandatory_skills_with_globally_unique_support": mandatory,
        "multi_membership_rows_after": min_multi,
        "multi_membership_fraction_of_covered_after": min_multi / len(covered),
        "overlap_removed_fraction": (baseline_multi - min_multi) / baseline_multi,
        "full_coverage_preserved": True,
        "reduction_verdict": "PARTIAL_REDUCTION_RESIDUAL_REMAINS" if min_multi else "SIMPLE_PRUNING_FULLY_ABSORBS",
        "interpretation": "Whole-package pruning is allowed to use the full released validator-support matrix and is therefore stronger than the author text dedup filter. Any residual overlap after exact coverage preservation cannot be removed by deleting whole packages without losing at least one benchmark-supported region; it requires task-conditional arbitration, support splitting/quotienting, or another overlap-aware control law.",
        "paper_design_authorized": False,
        "method_authorized": False,
        "gpu_authorized": False
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": result["reduction_verdict"],
        "before": baseline_multi,
        "after": min_multi,
        "removed_fraction": result["overlap_removed_fraction"],
        "min_skills": min_size,
        "selected": selected,
        "pair_overlap": selected_pair_overlap,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
