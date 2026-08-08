from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ark_provider import ArkResponsesClient, extract_json_object
from .config import PROJECT_ROOT

SOURCE = PROJECT_ROOT / "generated" / "ark-model-tournament.json"
DEFAULT_JSON = PROJECT_ROOT / "generated" / "ark-model-tournament-judged.json"
JUDGES = ("deepseek-v4-pro", "glm-5.2", "doubao-seed-evolving")


def _candidates() -> list[dict[str, Any]]:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for result in payload.get("results") or []:
        if not result.get("valid"):
            continue
        model = result["requested_model"]
        for repair in (result.get("response") or {}).get("repairs") or []:
            rows.append({"model": model, **repair})
    return rows


def _prompt(idea_id: str, candidates: list[dict[str, Any]], judge: str) -> str:
    anonymous = []
    for i, row in enumerate(candidates):
        anonymous.append({
            "candidate_id": f"C{i+1:02d}",
            "material_change": row.get("material_change"),
            "why_not_reducible": row.get("why_not_reducible"),
            "persistent_frozen_object": row.get("persistent_frozen_object"),
            "strongest_matched_baseline": row.get("strongest_matched_baseline"),
            "shared_information_budget": row.get("shared_information_budget"),
            "independent_truth": row.get("independent_truth"),
            "decisive_pilot": row.get("decisive_pilot"),
            "stop_rule": row.get("stop_rule"),
            "surviving_claim": row.get("surviving_claim"),
            "remaining_risk": row.get("remaining_risk"),
        })
    return f"""Act as a strict ICLR mechanism reviewer selecting the strongest repair design for one already-failed R3 boundary.

Idea id: {idea_id}
Judge model: {judge}

The candidates are anonymous. Score every candidate 0-5 on exactly these dimensions:
- material_change: changes the mechanism rather than only wording/experiment.
- simplification_resistance: the strongest simpler baseline gets the SAME observations/features/labels/traces/capacity/calls/tokens/optimization/wall-clock and still cannot trivially implement the same object.
- persistent_learning: a frozen learned object changes future behavior after evolution context is removed.
- independent_truth: final truth is external/independent of the learner and its judge.
- pilot_identifiability: one crossed/factorial pilot can attribute the surviving mechanism.
- claim_discipline: does not infer more than the evidence/certificate proves.

Important failure rule: if a candidate says the baseline cannot reproduce it only because the baseline is artificially denied input features, capacity, structure, or supervision that the proposal receives, simplification_resistance must be 0 or 1.

Return JSON only:
{{"idea_id":"{idea_id}","scores":[{{"candidate_id":"C01","material_change":0,"simplification_resistance":0,"persistent_learning":0,"independent_truth":0,"pilot_identifiability":0,"claim_discipline":0,"fatal_issue":"","best_feature":""}}],"top_candidate_id":"C01","top_reason":""}}

Candidates:
{json.dumps(anonymous, ensure_ascii=False, indent=2)}
"""


def run() -> dict[str, Any]:
    rows = _candidates()
    by_idea: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_idea[row["idea_id"]].append(row)
    reviews: list[dict[str, Any]] = []
    client = ArkResponsesClient()
    for idea_id, candidates in by_idea.items():
        mapping = {f"C{i+1:02d}": row["model"] for i, row in enumerate(candidates)}
        for judge in JUDGES:
            response = client.respond(_prompt(idea_id, candidates, judge), model=judge, max_output_tokens=7000, thinking="disabled")
            parsed = extract_json_object(response["text"])
            parsed["judge"] = judge
            parsed["candidate_model_map"] = mapping
            reviews.append(parsed)
    totals: dict[str, list[float]] = defaultdict(list)
    dimensions = ("material_change", "simplification_resistance", "persistent_learning", "independent_truth", "pilot_identifiability", "claim_discipline")
    per_case: list[dict[str, Any]] = []
    for review in reviews:
        for score in review.get("scores") or []:
            model = review["candidate_model_map"].get(score.get("candidate_id"))
            if not model:
                continue
            values = [float(score.get(key, 0)) for key in dimensions]
            mean = sum(values) / len(values)
            totals[model].append(mean)
            per_case.append({"idea_id": review["idea_id"], "judge": review["judge"], "model": model, "mean": round(mean, 3), **{key: score.get(key) for key in dimensions}, "fatal_issue": score.get("fatal_issue", "")})
    ranking = []
    for model, scores in totals.items():
        ranking.append({"model": model, "mean_score": round(sum(scores)/len(scores), 3), "judgments": len(scores), "min_score": round(min(scores), 3), "max_score": round(max(scores), 3)})
    ranking.sort(key=lambda row: (-row["mean_score"], -row["min_score"], row["model"]))
    return {"schema_version":"1.0","generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"judges":list(JUDGES),"dimensions":list(dimensions),"ranking":ranking,"per_case":per_case,"raw_reviews":reviews}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--json", type=Path, default=DEFAULT_JSON); args=parser.parse_args()
    payload=run(); args.json.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(payload["ranking"],ensure_ascii=False,indent=2))
    return 0


if __name__ == "__main__": raise SystemExit(main())
