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

DRAFT = ROOT / "generated/e2-r17-deepseek-v2-repair2-draft-contract-20260831.json"
IDENTITY = ROOT / "generated/e2-r17-deepseek-v2-repair2-model-identity-adjudication-20260831.json"
OUT_ROOT = ROOT / "generated/e2-r17-deepseek-v2-repair2-review-20260831"
MODELS = ("deepseek-v4-pro", "kimi-k3")


def schema() -> dict[str, Any]:
    return {
        "draft_contract_sha256_acknowledged": "",
        "verdict": "PASS_TO_SEPARATELY_AUTHORIZED_REPAIR2|REVISE_REPAIR2|STOP_REPAIR2_INHERITANCE",
        "selection_bias_assessment": "",
        "prefix_compatibility_assessment": "",
        "arm_symmetry_assessment": "",
        "fresh_failed_pair_assessment": "",
        "valid_manifest_assessment": "",
        "runtime_reliability_reporting_assessment": "",
        "provider_budget_assessment": "",
        "scientific_cardinality_assessment": "",
        "remaining_blockers": [{"priority": "P0|P1", "issue": "", "why_blocking": "", "exact_repair": ""}],
        "nonblocking_notes": [""],
        "execution_recommendation": "ALLOW_SEPARATE_REPAIR2_AUTHORIZATION|HOLD|STOP",
        "second_backbone_recommendation": "HOLD",
        "paper_claim_authority": False,
        "single_sentence_verdict": "",
    }


def prompt_for(model: str, bound: str, repair_sha: str) -> str:
    spec = json.dumps(schema(), ensure_ascii=False, indent=2)
    return f"""You are an independent protocol reviewer for E2-R17 DeepSeek V2 Repair2. You are a reviewer only, not a scientific backbone. No partial MRW/WIN-C effect or score is supplied or may be inferred. Review the exact bound dossier, not a summary.

Reviewer endpoint: {model}
Exact Repair2 draft SHA-256: {repair_sha}

The frozen history is: Repair1 completed 14/48 paired units (28 learned states, 504 heldout units). A later partial MRW state e1-fmv-01/rep2 completed 10/10 provider responses but deterministic SkillEvolver patch application failed with SkillEditError before skill_post/update_completed/heldout; paired WIN-C never started. Provider ambiguity is FALSE, scientific endpoint FALSE, belief update NONE. That state is quarantined.

Audit all eight gates:
A. SELECTION BIAS: The 14 inherited pairs are selected only by pre-outcome completeness/provenance and attempt0-success prefix identity. The treatment-dependent failed pair is not completed or analyzed and Repair2 fresh-runs both arms. Does this avoid unacceptable post-treatment selection/protocol-version bias? If not, return STOP_REPAIR2_INHERITANCE with a P0 blocker.
B. PREFIX COMPATIBILITY: For an attempt0-success state, max_parse_attempts=1 and =2 follow the identical execution path through the endpoint; the extra branch exists only after attempt0 fails. Is inheritance scientifically valid?
C. SYMMETRY: max_parse_attempts=2 and budgets apply identically to WIN-C and MRW, without arm/stream/failure-conditioned allowance.
D. FRESH FAILED PAIR: Repair2 never resumes old MRW; it fresh-runs both WIN-C and MRW for e1-fmv-01/rep2 under the same current identity, pools, initial skill, policy, and time-balanced schedule.
E. MANIFEST: Only the frozen 14-pair compatibility manifest may seed inheritance. Analysis reads a content-addressed valid_replicates manifest that must contain exactly 48 complete paired rows and exactly four per stream. No directory discovery or single-arm row is allowed.
F. RELIABILITY: correction required/success/failure counts are secondary runtime reliability outcomes by arm, cannot filter the primary estimand, and the Repair1 MRW patch-apply failure remains separately reported.
G. BUDGET: nominal updater=10, one explicit correction yields max=11, actor remains <=180 (18 probes x 10 turns), state max=191; claims are visible and fail-closed, provider retry=0, no third attempt.
H. CARDINALITY/SCIENCE: exactly 12 stream D_s, four valid pairs per stream, same treatment/control/pools/initial skill/renderer/updater/verifier/heldout/K=1/8192/statistics/epsilon. GPT/Kimi/Qwen scientific execution and public benchmark remain forbidden.

PASS only if all gates pass and remaining_blockers is exactly []. PASS authorizes only a separately SHA-bound Repair2 contract/authorization after zero-provider preflight. If either inheritance or protocol versioning is unacceptable, STOP_REPAIR2_INHERITANCE; do not recommend silently rerunning or cherry-picking.

Return exactly one JSON object and no markdown using this schema:
{spec}
Set draft_contract_sha256_acknowledged exactly to the SHA above.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""


base.REPAIR = DRAFT
base.IDENTITY = IDENTITY
base.OUT_ROOT = OUT_ROOT
base.MODELS = MODELS
base.DOSSIER = (
    ("repair2_draft", DRAFT),
    ("repair1_contract", ROOT / "generated/e2-r17-deepseek-v2-replicated-paired-repair1-contract-20260830.json"),
    ("repair1_authorization", ROOT / "generated/e2-r17-deepseek-v2-replicated-paired-repair1-authorization-20260830.json"),
    ("compatibility_manifest", ROOT / "generated/e2-r17-deepseek-v2-repair1-compatibility-manifest-20260831.json"),
    ("technical_quarantine", ROOT / "generated/e2-r17-deepseek-v2-repair1-technical-quarantine-20260831.json"),
    ("superseding_failure", ROOT / "generated/e2-r17-deepseek-v2-repair1-updater-patch-apply-failure-20260831.json"),
    ("runner", ROOT / "scripts/run_e2_r17_deepseek_v2_repair2_continuation.py"),
    ("analyzer", ROOT / "scripts/analyze_e2_r17_deepseek_v2_repair2.py"),
    ("preflight", ROOT / "scripts/preflight_e2_r17_deepseek_v2_repair2.py"),
    ("manifest_validator", ROOT / "research_pipeline/e2_r17_repair2_manifest.py"),
    ("tests", ROOT / "research_pipeline/test_e2_r17_deepseek_v2_repair2.py"),
    ("test_adjudication", ROOT / "generated/e2-r17-deepseek-v2-repair2-test-adjudication-20260831.json"),
    ("model_identity", IDENTITY),
)
base.schema = schema
base.prompt_for = prompt_for


def identity_map() -> dict[str, str]:
    payload = json.loads(IDENTITY.read_text(encoding="utf-8"))
    if payload.get("status") != "PASS_CURRENT_REVIEW_TRANCHE":
        raise RuntimeError("Repair2 reviewer identity adjudication is not PASS")
    rows = payload.get("requested_and_resolved") or {}
    resolved = {model: str(rows[model]["resolved"]) for model in MODELS}
    if len(set(resolved.values())) != len(MODELS):
        raise RuntimeError("Repair2 reviewer identities are not distinct")
    return resolved


base.identity_map = identity_map


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--max-output-tokens", type=int, default=5000)
    args = parser.parse_args()
    expected = base.identity_map()
    bound, hashes = base.dossier()
    draft_sha = base.sha_file(DRAFT)
    base.load_env_file(args.env_file)
    source = base.ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != base.PLAN_BASE_URL:
        raise RuntimeError("Repair2 review refuses non-Ark-Plan route")
    settings = base.ArkSettings(
        api_key=source.api_key,
        base_url=source.base_url,
        default_model=source.default_model,
        timeout_seconds=300.0,
        max_retries=0,
    )
    client = base.ArkResponsesClient(settings)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for model in MODELS:
        row = base.call(
            client,
            model=model,
            expected_resolved=expected[model],
            bound=bound,
            hashes=hashes,
            repair_sha=draft_sha,
            max_output_tokens=args.max_output_tokens,
        )
        base.atomic_json(OUT_ROOT / f"{base.slug(model)}.json", row)
        rows.append(row)
    completed = [row for row in rows if row.get("status") == "COMPLETED"]
    allow = len(completed) == len(rows) and all(
        row.get("review", {}).get("draft_contract_sha256_acknowledged") == draft_sha
        and row.get("review", {}).get("verdict") == "PASS_TO_SEPARATELY_AUTHORIZED_REPAIR2"
        and row.get("review", {}).get("execution_recommendation") == "ALLOW_SEPARATE_REPAIR2_AUTHORIZATION"
        and row.get("review", {}).get("second_backbone_recommendation") == "HOLD"
        and row.get("review", {}).get("paper_claim_authority") is False
        and not row.get("review", {}).get("remaining_blockers")
        for row in completed
    )
    stop_inheritance = any(
        row.get("review", {}).get("verdict") == "STOP_REPAIR2_INHERITANCE"
        for row in completed
    )
    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-dual-review",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "draft_contract_sha256": draft_sha,
        "statuses": {row["requested_model"]: row.get("status") for row in rows},
        "resolved_models": {row["requested_model"]: row.get("resolved_model") for row in rows},
        "verdicts": {row["requested_model"]: row.get("review", {}).get("verdict") for row in completed},
        "remaining_blockers": {row["requested_model"]: row.get("review", {}).get("remaining_blockers") for row in completed},
        "all_pass_to_separately_authorized_repair2": allow,
        "stop_repair2_inheritance": stop_inheritance,
        "scientific_backbone": "deepseek-v4-pro only",
        "reviewers_only": list(MODELS),
        "second_backbone_authority": False,
        "paper_claim_authority": False,
    }
    base.atomic_json(OUT_ROOT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if len(completed) == len(rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
