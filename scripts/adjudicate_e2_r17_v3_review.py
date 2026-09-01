#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW_ROOT = ROOT / "generated/e2-r17-experiment-plan-v3-review-20260828"
PLAN = ROOT / "generated/e2-r17-experiment-plan-v3-20260828.json"
OUT = ROOT / "generated/e2-r17-experiment-plan-v3-review-adjudication-20260828.json"
MODELS = ("deepseek-v4-pro", "kimi-k3")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    rows = []
    for model in MODELS:
        path = REVIEW_ROOT / f"{model}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        review = payload.get("review") or {}
        rows.append(
            {
                "requested_model": model,
                "resolved_model": payload.get("resolved_model"),
                "artifact": str(path.relative_to(ROOT)),
                "artifact_sha256": sha(path),
                "status": payload.get("status"),
                "verdict": review.get("verdict"),
                "runtime_pilot_recommendation": review.get("runtime_pilot_recommendation"),
                "e1_a_recommendation": review.get("e1_a_recommendation"),
                "e1_b_recommendation": review.get("e1_b_recommendation"),
                "paper_claim_authority": review.get("paper_claim_authority"),
            }
        )
    checks = {
        "both_completed": all(row["status"] == "COMPLETED" for row in rows),
        "both_v3_pass": all(row["verdict"] == "PASS_TO_OUTCOME_BLIND_RUNTIME_PILOT" for row in rows),
        "both_allow_runtime_pilot": all(row["runtime_pilot_recommendation"] == "ALLOW_OUTCOME_BLIND_RUNTIME_PILOT" for row in rows),
        "both_hold_e1_a": all(row["e1_a_recommendation"] == "HOLD_UNTIL_SEPARATE_IMMUTABLE_CONTRACT" for row in rows),
        "both_hold_e1_b": all(row["e1_b_recommendation"] == "HOLD_UNTIL_SUPPORT_GATE_AND_SEPARATE_CONTRACT" for row in rows),
        "paper_claim_authority_false": all(row["paper_claim_authority"] is False for row in rows),
    }
    status = "PASS_TO_OUTCOME_BLIND_RUNTIME_PILOT_ONLY" if all(checks.values()) else "HOLD"
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-dual-review-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "plan": str(PLAN.relative_to(ROOT)),
        "plan_sha256": sha(PLAN),
        "reviewers": rows,
        "checks": checks,
        "transport_note": "The MCP call returned 502 after remote execution. Process/output inspection showed both reviewer artifacts complete. No provider call was relaunched.",
        "summary_bug_note": "The inherited V2 summary script checked the plural enum ALLOW_OUTCOME_BLIND_RUNTIME_PILOTS, while the V3 schema uses singular ALLOW_OUTCOME_BLIND_RUNTIME_PILOT. Therefore its all_allow_runtime_pilot=false field is a renderer/adjudicator bug and is not used as authority.",
        "authority": {
            "outcome_blind_runtime_pilot": status == "PASS_TO_OUTCOME_BLIND_RUNTIME_PILOT_ONLY",
            "e1_a_pool_generation": False,
            "e1_b_updater": False,
            "scientific_outcomes": False,
            "paper_promotion": False,
            "submission": False
        }
    }
    temp = OUT.with_suffix(".json.tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(OUT)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if status.startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
