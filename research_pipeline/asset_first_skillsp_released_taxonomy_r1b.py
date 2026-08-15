from __future__ import annotations

import argparse, collections, json, re, statistics, subprocess, sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def skill_metadata(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        raise RuntimeError(f"missing front matter: {path}")
    return json.loads(match.group(1))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    c = load_json(args.contract)
    parent = load_json(Path(c["inputs"]["parent_result"]))
    rows = load_jsonl(Path(c["inputs"]["parent_membership"]))
    repo = Path(c["inputs"]["author_repo"])
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    if commit != c["inputs"]["author_commit"]:
        raise RuntimeError(f"author commit drift: {commit}")
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from skill_library.library import jaccard_similarity

    probs = parent["representation_counterfactual"]["base_probabilities"]
    covered = [r for r in rows if r["accepted_skill_ids"]]
    single = [r for r in covered if len(r["accepted_skill_ids"]) == 1]
    multi = [r for r in covered if len(r["accepted_skill_ids"]) > 1]

    def mass(row: dict[str, Any]) -> float:
        return sum(float(probs[s]) for s in row["accepted_skill_ids"])

    single_masses = [mass(r) for r in single]
    multi_masses = [mass(r) for r in multi]
    median_single = statistics.median(single_masses)
    median_multi = statistics.median(multi_masses)
    ratio = median_multi / median_single

    pair_rows: collections.Counter[tuple[str, str]] = collections.Counter()
    for r in rows:
        for s in r.get("specific_skill_ids", []):
            for g in r.get("generic_skill_ids", []):
                pair_rows[(s, g)] += 1

    pair_audit = []
    for (left, right), count in sorted(pair_rows.items()):
        lm = skill_metadata(repo / "tool_call/packages" / left / "SKILL.md")
        rm = skill_metadata(repo / "tool_call/packages" / right / "SKILL.md")
        ltext = f"{lm.get('name','')} {lm.get('description','')}"
        rtext = f"{rm.get('name','')} {rm.get('description','')}"
        sim = float(jaccard_similarity(ltext, rtext))
        pair_audit.append({
            "left": left, "right": right, "shared_benchmark_rows": count,
            "name_description_jaccard": sim,
            "author_duplicate_threshold": 0.33,
            "author_text_duplicate_filter_flags": sim >= 0.33,
        })

    missed = sum(not p["author_text_duplicate_filter_flags"] for p in pair_audit)
    missed_fraction = missed / max(1, len(pair_audit))
    gate = c["frozen_gate"]
    checks = {
        "released_overlap_rows": {"actual": len(multi), "required_min": gate["released_overlap_rows_min"], "pass": len(multi) >= gate["released_overlap_rows_min"]},
        "distinct_released_overlap_pairs": {"actual": len(pair_audit), "required_min": gate["distinct_released_overlap_pairs_min"], "pass": len(pair_audit) >= gate["distinct_released_overlap_pairs_min"]},
        "eligibility_mass_ratio": {"actual": ratio, "required_min": gate["median_multi_to_single_eligibility_mass_ratio_min"], "pass": ratio >= gate["median_multi_to_single_eligibility_mass_ratio_min"]},
        "text_dedup_miss_fraction": {"actual": missed_fraction, "required_min": gate["released_overlap_pairs_missed_by_text_filter_fraction_min"], "pass": missed_fraction >= gate["released_overlap_pairs_missed_by_text_filter_fraction_min"]},
    }
    positive = all(v["pass"] for v in checks.values())
    result = {
        "schema_version": "1.0",
        "experiment_id": c["experiment_id"],
        "candidate_id": c["candidate_id"],
        "decision": "RELEASED_TAXONOMY_MULTIPLICITY_SUPPORTED" if positive else "STOP_RELEASED_TAXONOMY_GATE_NOT_MET",
        "scientific_result_available": True,
        "primary_mechanism_positive": positive,
        "scientific_disposition": "POSITIVE_MECHANISM_NOVELTY_UNRESOLVED" if positive else "REDUCE_TO_EXACT_CLONE_PATHOLOGY",
        "covered_rows": len(covered),
        "single_membership_rows": len(single),
        "multi_membership_rows": len(multi),
        "median_single_membership_eligibility_exposure_mass": median_single,
        "median_multi_membership_eligibility_exposure_mass": median_multi,
        "median_multi_to_single_eligibility_mass_ratio": ratio,
        "eligibility_exposure_definition": c["frozen_definitions"]["eligibility_exposure_mass"],
        "realized_task_probability_claimed": False,
        "pair_audit": pair_audit,
        "released_overlap_pairs_missed_by_text_filter": missed,
        "released_overlap_pairs_total": len(pair_audit),
        "released_overlap_pairs_missed_fraction": missed_fraction,
        "checks": checks,
        "paper_design_authorized": False,
        "method_authorized": False,
        "p0_authorized": False,
        "gpu_authorized": False,
        "gpu_hours": 0,
        "model_calls": 0,
        "new_task_generation": 0,
        "author_commit": commit,
        "next_action": c["next_if_positive"] if positive else c["next_if_negative"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"decision": result["decision"], "ratio": ratio, "missed_fraction": missed_fraction, "checks": checks}, ensure_ascii=False))

if __name__ == "__main__":
    main()
