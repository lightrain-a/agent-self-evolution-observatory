#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_e2_r17_v3_1_review as base

CONTRACT = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-measurement-contract-v2-20260831.json"
PREFLIGHT_AUTH = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-preflight-authorization-v2-20260831.json"
PREFLIGHT = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-actual-actor-path-preflight-v2-20260831.json"
IDENTITY = ROOT / "generated/e2-r17-deepseek-v2-repair2-model-identity-adjudication-20260831.json"
OUT_ROOT = ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-review-20260831"
MODELS = ("deepseek-v4-pro", "kimi-k3")


def schema() -> dict[str, Any]:
    return {
        "contract_sha256_acknowledged": "",
        "preflight_sha256_acknowledged": "",
        "verdict": "PASS_TO_SINGLE_USE_M1_AUTHORIZATION|REVISE_M1|STOP_M1",
        "measurement_only_authority_assessment": "",
        "cross_authorization_provenance_assessment": "",
        "actual_actor_path_assessment": "",
        "provider_budget_assessment": "",
        "v1_local_repair_assessment": "",
        "exactly_once_assessment": "",
        "no_partial_effect_assessment": "",
        "remaining_blockers": [
            {"priority": "P0|P1", "issue": "", "why_blocking": "", "exact_repair": ""}
        ],
        "nonblocking_notes": [""],
        "execution_recommendation": "ALLOW_SINGLE_USE_M1_AUTHORIZATION|HOLD|STOP",
        "paper_claim_authority": False,
        "single_sentence_verdict": "",
    }


def prompt_for(model: str, bound: str, contract_sha: str) -> str:
    preflight_sha = base.sha_file(PREFLIGHT)
    spec = json.dumps(schema(), ensure_ascii=False, indent=2)
    return f"""You are an independent fail-closed protocol reviewer for E2-R17 Repair2-M1.
You are a reviewer only, not a scientific backbone. No WIN-C/MRW score or partial effect is supplied.
Reviewer endpoint: {model}
Exact M1 contract SHA-256: {contract_sha}
Exact actual-path preflight SHA-256: {preflight_sha}

Review these gates against the bound dossier:
A. M1 is measurement-only: exactly two frozen parent Repair2 learned states x 18 heldout tasks; new/replayed updater calls=0; analyzer=false; partial-effect reading=false.
B. The child authorization binds its own measurement contract and provider ledger, while each parent updater receipt must remain bound to parent Repair2 contract 9e38... and authorization 9643.... No receipt rewriting or ordinary AUTHORIZED_E1 aliasing is allowed.
C. The versioned actor, not the historical actor, verifies current child scope plus exact learned-state path/SHA and parent updater receipt path/SHA/contract/auth provenance.
D. ACTUAL_ACTOR_AUTHORIZATION_PATH_PREFLIGHT must be 36/36, provider claims=0, provider calls=0, and stop only after status/scope/task/K/model/identity/suite/skill/receipt/parent provenance/budget checks.
E. Actor-only provider budget is exact 180 per learned state and 10 per heldout unit; updater authority remains zero.
F. Preflight V1 failed before ledger creation because a relative ignored .env was absent in the isolated worktree. V2 changes only env_file to the exact absolute historical ignored .env path; it must not alter any scientific variable.
G. Production execution root is new and exactly-once. Parent Repair2 root, lock, failure artifacts, 20 updater calls and two learned states remain immutable.
H. A PASS may authorize only 36 heldout measurements and must seal REPAIR2_M1_MEASUREMENT_RECOVERY_PASS without analysis. It may not authorize V3, analyzer, paper promotion, other streams/replicates/models/tasks/K, or public benchmarks.

Return STOP_M1 for any P0 provenance, authority, hidden-provider, cardinality, or sample-integrity defect.
PASS only if remaining_blockers is exactly [] and execution_recommendation is ALLOW_SINGLE_USE_M1_AUTHORIZATION.
Return exactly one JSON object and no markdown:
{spec}
Set both acknowledged SHA fields exactly.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""


base.REPAIR = CONTRACT
base.IDENTITY = IDENTITY
base.OUT_ROOT = OUT_ROOT
base.MODELS = MODELS
base.DOSSIER = (
    ("m1_contract", CONTRACT),
    ("m1_preflight_authorization", PREFLIGHT_AUTH),
    ("m1_actual_actor_path_preflight", PREFLIGHT),
    ("m1_actor", ROOT / "scripts/run_e2_r17_actor_pool_measurement_compat_v1.py"),
    ("m1_orchestrator", ROOT / "scripts/run_e2_r17_deepseek_v2_repair2_m1_measurement.py"),
    ("m1_tests", ROOT / "research_pipeline/test_e2_r17_repair2_m1_measurement.py"),
    ("m1_v1_failure_adjudication", ROOT / "generated/e2-r17-deepseek-v2-repair2-m1-actual-path-preflight-v1-failure-adjudication-20260831.json"),
    ("parent_repair2_contract", ROOT / "generated/e2-r17-deepseek-v2-repair2-contract-20260831.json"),
    ("parent_repair2_authorization", ROOT / "generated/e2-r17-deepseek-v2-repair2-authorization-20260831.json"),
    ("parent_execution_blocker", ROOT / "generated/e2-r17-deepseek-v2-repair2-execution-blocker-20260831.json"),
    ("parent_stop_diagnosis", ROOT / "consultations/e2-r17-deepseek-v2-repair2-execution-stop-20260831.md"),
    ("model_identity", IDENTITY),
)
base.schema = schema
base.prompt_for = prompt_for


def identity_map() -> dict[str, str]:
    payload = json.loads(IDENTITY.read_text(encoding="utf-8"))
    if payload.get("status") != "PASS_CURRENT_REVIEW_TRANCHE":
        raise RuntimeError("M1 reviewer identity adjudication is not PASS")
    rows = payload.get("requested_and_resolved") or {}
    resolved = {model: str(rows[model]["resolved"]) for model in MODELS}
    if len(set(resolved.values())) != len(MODELS):
        raise RuntimeError("M1 reviewer identities are not distinct")
    return resolved


base.identity_map = identity_map


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--max-output-tokens", type=int, default=5000)
    args = parser.parse_args()
    expected = base.identity_map()
    bound, hashes = base.dossier()
    contract_sha = base.sha_file(CONTRACT)
    preflight_sha = base.sha_file(PREFLIGHT)
    base.load_env_file(args.env_file)
    source = base.ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != base.PLAN_BASE_URL:
        raise RuntimeError("M1 review refuses non-Ark-Plan route")
    settings = base.ArkSettings(
        api_key=source.api_key,
        base_url=source.base_url,
        default_model=source.default_model,
        timeout_seconds=300.0,
        max_retries=0,
    )
    client = base.ArkResponsesClient(settings)
    OUT_ROOT.mkdir(parents=True, exist_ok=False)
    rows = []
    for model in MODELS:
        row = base.call(
            client,
            model=model,
            expected_resolved=expected[model],
            bound=bound,
            hashes=hashes,
            repair_sha=contract_sha,
            max_output_tokens=args.max_output_tokens,
        )
        base.atomic_json(OUT_ROOT / f"{base.slug(model)}.json", row)
        rows.append(row)
    completed = [row for row in rows if row.get("status") == "COMPLETED"]
    allow = len(completed) == len(rows) and all(
        row.get("review", {}).get("contract_sha256_acknowledged") == contract_sha
        and row.get("review", {}).get("preflight_sha256_acknowledged") == preflight_sha
        and row.get("review", {}).get("verdict") == "PASS_TO_SINGLE_USE_M1_AUTHORIZATION"
        and row.get("review", {}).get("execution_recommendation") == "ALLOW_SINGLE_USE_M1_AUTHORIZATION"
        and row.get("review", {}).get("paper_claim_authority") is False
        and not row.get("review", {}).get("remaining_blockers")
        for row in completed
    )
    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-m1-independent-dual-review",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "contract_sha256": contract_sha,
        "preflight_sha256": preflight_sha,
        "statuses": {row["requested_model"]: row.get("status") for row in rows},
        "resolved_models": {row["requested_model"]: row.get("resolved_model") for row in rows},
        "verdicts": {row["requested_model"]: row.get("review", {}).get("verdict") for row in completed},
        "remaining_blockers": {row["requested_model"]: row.get("review", {}).get("remaining_blockers") for row in completed},
        "all_pass_to_single_use_m1_authorization": allow,
        "reviewers_only": list(MODELS),
        "scientific_backbone": "deepseek-v4-pro only",
        "paper_claim_authority": False,
    }
    base.atomic_json(OUT_ROOT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if len(completed) == len(rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
