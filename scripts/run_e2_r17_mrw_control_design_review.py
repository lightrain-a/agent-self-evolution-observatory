#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkResponsesClient, ArkSettings, extract_json_object
from research_pipeline.config import load_env_file

PLAN_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"
MODELS = ("deepseek-v4-pro", "kimi-k3")
DESIGN = ROOT / "consultations/e2-r17-mrw-control-design-preoutcome-20260829.md"
IDENTITY = ROOT / "generated/e2-r17-e1-b-negative-control-model-identity-adjudication-20260829.json"
OUT_ROOT = ROOT / "generated/e2-r17-mrw-control-design-review-20260829"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def schema() -> dict[str, Any]:
    return {
        "design_sha256_acknowledged": "",
        "preferred_option": "A_REUSE_WIN_AB|B_FRESH_CONTEMPORANEOUS_WIN_C",
        "causal_identification_assessment": "",
        "temporal_drift_assessment": "",
        "historical_control_usage": "",
        "primary_estimand": "",
        "primary_decision_rule": "",
        "cost_benefit_assessment": "",
        "remaining_blockers": [{"priority": "P0|P1", "issue": "", "exact_repair": ""}],
        "nonblocking_notes": [""],
        "negative_control_fail_policy": "MRW_REMAINS_UNAUTHORIZED",
        "paper_claim_authority": False,
        "single_sentence_recommendation": "",
    }


def prompt_for(model: str, design_text: str, design_sha: str) -> str:
    spec = json.dumps(schema(), ensure_ascii=False, indent=2)
    return f"""You are an independent causal-design reviewer for E2-R17. You are blind to the other reviewer. The current WIN-A/WIN-B negative-control full run is still executing, and its outcome must remain unknown to this design decision. This consultation has zero experiment, MRW, paper, frontend, or submission authority.

Reviewer endpoint: {model}
Exact design memo SHA-256: {design_sha}

Choose between two pre-outcome MRW primary-control designs:
A) reuse already-collected WIN-A/WIN-B after negative-control equivalence PASS, preferably as WIN-A alone or their mean;
B) after negative-control PASS, run a fresh contemporaneous WIN-C clone together with MRW and use WIN-C as the primary paired control, retaining WIN-A/WIN-B only as nuisance/stability evidence.

Judge from causal identification, hosted-provider temporal drift, statistical estimand cleanliness, cost, and top-conference reviewer robustness. Do not use or speculate about the still-unopened negative-control outcome. Do not change tasks, K, model, held-out probes, renderer, failure taxonomy, or the negative-control equivalence margin. If the negative control fails equivalence, MRW remains unauthorized regardless of your preference.

Return exactly one JSON object and no markdown using this schema:
{spec}

Set `design_sha256_acknowledged` exactly to the memo SHA. `paper_claim_authority` must be false and `negative_control_fail_policy` must be `MRW_REMAINS_UNAUTHORIZED`.

DESIGN MEMO START
{design_text}
DESIGN MEMO END
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--max-output-tokens", type=int, default=3500)
    args = parser.parse_args()

    identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
    if identity.get("status") != "PASS_CURRENT_REVIEW_TRANCHE":
        raise RuntimeError("review model identity is not current-pass")
    expected = {k: str(v["resolved"]) for k, v in identity["requested_and_resolved"].items() if k in MODELS}
    design_text = DESIGN.read_text(encoding="utf-8")
    design_sha = sha_file(DESIGN)

    load_env_file(args.env_file)
    source = ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("MRW design review refuses non-Ark-Plan route")
    client = ArkResponsesClient(ArkSettings(api_key=source.api_key, base_url=source.base_url, default_model=source.default_model, timeout_seconds=300.0, max_retries=0))
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    required_fields = set(schema())
    for model in MODELS:
        prompt = prompt_for(model, design_text, design_sha)
        result = client.respond(prompt, model=model, max_output_tokens=args.max_output_tokens, temperature=0, thinking="disabled", allow_thinking_compatibility_fallback=False)
        raw = str(result.get("text") or "")
        resolved = str(result.get("resolved_model") or "")
        review = extract_json_object(raw)
        missing = sorted(required_fields - set(review))
        if review.get("design_sha256_acknowledged") != design_sha:
            missing.append("design_sha256_acknowledged_exact")
        if review.get("paper_claim_authority") is not False:
            missing.append("paper_claim_authority_false")
        if review.get("negative_control_fail_policy") != "MRW_REMAINS_UNAUTHORIZED":
            missing.append("negative_control_fail_policy")
        row = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-mrw-control-design-independent-review",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "requested_model": model,
            "resolved_model": resolved,
            "expected_resolved_model": expected[model],
            "resolved_model_matches_qualification": resolved == expected[model],
            "design_sha256": design_sha,
            "provider_retry_limit": 0,
            "thinking_requested": "disabled",
            "raw_text_sha256": sha_text(raw),
            "response_id_sha256": sha_text(str(result.get("response_id") or "")),
            "usage": result.get("usage") or {},
            "review": review,
            "missing_required_fields": missing,
            "status": "COMPLETED" if not missing and resolved == expected[model] else "FAIL_SCHEMA_OR_IDENTITY",
            "independent": True,
            "exposed_to_other_review": False,
            "scientific_authority": False,
            "paper_claim_authority": False,
        }
        atomic_json(OUT_ROOT / f"{slug(model)}.json", row)
        rows.append(row)

    completed = [r for r in rows if r["status"] == "COMPLETED"]
    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-mrw-control-design-dual-review",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "design_path": str(DESIGN.relative_to(ROOT)),
        "design_sha256": design_sha,
        "statuses": {r["requested_model"]: r["status"] for r in rows},
        "resolved_models": {r["requested_model"]: r["resolved_model"] for r in rows},
        "preferred_options": {r["requested_model"]: r.get("review", {}).get("preferred_option") for r in completed},
        "all_completed": len(completed) == 2,
        "negative_control_outcome_used": False,
        "mrw_authority": False,
        "paper_claim_authority": False,
    }
    atomic_json(OUT_ROOT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["all_completed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
