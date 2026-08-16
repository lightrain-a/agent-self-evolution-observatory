from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def selected_memberships(rows: Iterable[dict[str, Any]], selected_skills: set[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        members = [str(skill) for skill in row.get("accepted_skill_ids") or [] if str(skill) in selected_skills]
        if not members:
            continue
        out.append({**row, "selected_skill_ids": sorted(members)})
    return out


def structural_lower_bound(rows: Iterable[dict[str, Any]], selected_skills: set[str]) -> dict[str, Any]:
    """Certify a >=2 exposure-distortion lower bound for global package weights.

    Let E_w(x)=sum_{s:x in A_s} w_s for nonnegative, context-independent
    package weights. If package a has a context supported only by a, package b
    has a context supported only by b, and some context is supported by both,
    then for m=min_x E_w(x)>0 we have w_a>=m and w_b>=m, while the overlap
    context has exposure at least w_a+w_b>=2m. Hence max_x E_w(x)/m >= 2.

    The certificate is purely combinatorial: no optimizer, model, or outcome
    threshold is involved.
    """
    filtered = selected_memberships(rows, selected_skills)
    unique: dict[str, list[dict[str, Any]]] = defaultdict(list)
    pair_overlap: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in filtered:
        members = list(row["selected_skill_ids"])
        # The lower-bound proof requires a true singleton support cell over the
        # full released validator universe, not merely uniqueness after pruning
        # or projecting to selected_skills. Otherwise an unselected positive
        # package could contribute to the purported exclusive cell.
        all_members = [str(skill) for skill in row.get("accepted_skill_ids") or []]
        if len(all_members) == 1 and all_members[0] in selected_skills:
            unique[all_members[0]].append(row)
        for i, left in enumerate(members):
            for right in members[i + 1 :]:
                pair_overlap[(left, right)].append(row)

    witnesses: list[dict[str, Any]] = []
    for (left, right), overlaps in sorted(pair_overlap.items()):
        if not unique[left] or not unique[right]:
            continue
        a = unique[left][0]
        b = unique[right][0]
        o = overlaps[0]
        witnesses.append(
            {
                "left_skill": left,
                "right_skill": right,
                "left_unique_row": {"level": a.get("level"), "index": a.get("index"), "tool": a.get("tool")},
                "right_unique_row": {"level": b.get("level"), "index": b.get("index"), "tool": b.get("tool")},
                "overlap_row": {"level": o.get("level"), "index": o.get("index"), "tool": o.get("tool")},
                "exposure_ratio_lower_bound": 2.0,
            }
        )

    return {
        "covered_rows": len(filtered),
        "selected_skills": sorted(selected_skills),
        "unique_support_counts": {skill: len(unique[skill]) for skill in sorted(selected_skills)},
        "unique_support_scope": "exact singleton accepted_skill_ids over the full released validator universe",
        "witness_count": len(witnesses),
        "witnesses": witnesses,
        "global_nonnegative_package_weight_exposure_ratio_lower_bound": 2.0 if witnesses else None,
        "proof": (
            "For any witness (a,b), let m be the minimum positive task exposure. "
            "The globally singleton a-only row implies w_a>=m and the globally singleton b-only row implies w_b>=m. "
            "Their overlap row has exposure at least w_a+w_b>=2m, so max/min>=2."
            if witnesses
            else "No mandatory-overlap witness was found."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--membership", type=Path, required=True)
    parser.add_argument("--selected-skills", required=True, help="comma-separated skill IDs")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    selected = {item.strip() for item in args.selected_skills.split(",") if item.strip()}
    result = structural_lower_bound(load_jsonl(args.membership), selected)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"witness_count": result["witness_count"], "lower_bound": result["global_nonnegative_package_weight_exposure_ratio_lower_bound"]}))


if __name__ == "__main__":
    main()
