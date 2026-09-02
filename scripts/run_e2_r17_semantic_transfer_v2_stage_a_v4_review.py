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

CONTRACT = ROOT / "generated/e2-r17-semantic-transfer-v2-stage-a-v4-contract-20260903.json"
DEFAULT_OUT_ROOT = ROOT / "generated/e2-r17-semantic-transfer-v2-stage-a-v4-review-20260903"
MODELS = ("deepseek-v4-pro", "kimi-k3")

DOSSIER = (
    ("paper_method_design_v2", ROOT / "consultations/e2-r17-selective-mrw-semantic-transfer-v2-20260903.md"),
    ("pre_f0_v2", ROOT / "generated/e2-r17-selective-mrw-semantic-transfer-v2-pre-f0-20260903.json"),
    ("static_audit_v2", ROOT / "generated/e2-r17-selective-mrw-semantic-transfer-v2-static-audit-20260903.json"),
    ("prompt_leakage_audit_v2", ROOT / "generated/e2-r17-semantic-transfer-v2-prompt-leakage-audit-20260903.json"),
    ("static_nuisance_balance_v2", ROOT / "generated/e2-r17-semantic-transfer-v2-static-nuisance-balance-20260903.json"),
    ("stage_a_v4_contract", CONTRACT),
    ("stage_a_v4_preflight", ROOT / "generated/e2-r17-semantic-transfer-v2-stage-a-v4-preflight-20260903.json"),
    ("semantic_builders", ROOT / "research_pipeline/e2_r17_semantic_transfer_builders.py"),
    ("suite_builder_v2", ROOT / "scripts/build_e2_r17_semantic_transfer_suite_v2.py"),
    ("generic_actor", ROOT / "scripts/run_e2_r17_actor_pool.py"),
    ("stage_a_v4_runner", ROOT / "scripts/run_e2_r17_semantic_transfer_v2_stage_a_v4.py"),
    ("equal_dose_adjudicator_v2", ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v2_stage_a.py"),
    ("authorization_minter_v4", ROOT / "scripts/authorize_e2_r17_semantic_transfer_v2_stage_a_v4.py"),
    ("preflight_code_v4", ROOT / "scripts/preflight_e2_r17_semantic_transfer_v2_stage_a_v4.py"),
    ("semantic_builder_tests", ROOT / "research_pipeline/test_e2_r17_semantic_transfer_builders.py"),
    ("superseded_v1_review_readiness", ROOT / "generated/e2-r17-semantic-transfer-stage-a-review-readiness-20260903.json"),
)


def schema() -> dict[str, Any]:
    return {
        "contract_sha256_acknowledged": "",
        "verdict": "PASS_TO_SEPARATE_STAGE_A_AUTHORIZATION|REVISE_BEFORE_STAGE_A|STOP_SEMANTIC_TRANSFER_CHILD",
        "discovery_confirmation_assessment": "",
        "family_identity_reduction_assessment": "",
        "matched_skeleton_assessment": "",
        "equal_dose_assessment": "",
        "stage_a_support_selection_assessment": "",
        "projection_causal_purity_assessment": "",
        "statistics_assessment": "",
        "actor_runtime_scope_assessment": "",
        "checkpoint_budget_failclosed_assessment": "",
        "paper_story_assessment": "",
        "remaining_blockers": [{"priority": "P0|P1", "issue": "", "why_blocking": "", "exact_repair": ""}],
        "nonblocking_notes": [""],
        "execution_recommendation": "ALLOW_SEPARATE_STAGE_A_AUTHORIZATION|HOLD|STOP",
        "paper_claim_authority": False,
        "stage_b_authority": False,
        "single_sentence_verdict": "",
    }


def prompt_for(model: str, bound: str, contract_sha: str) -> str:
    spec = json.dumps(schema(), ensure_ascii=False, indent=2)
    return f"""You are an independent adversarial pre-execution reviewer for E2-R17 Selective-MRW Semantic-Transfer V2. You are a reviewer only. No V2 Stage-A search-pool outcomes and no Stage-B learning outcomes are supplied. You may recommend at most a separately SHA-bound Stage-A V4 pool-acquisition authorization. You may NOT authorize Stage B, heldout evaluation, analyzer, second backbone, public benchmark, or paper claims.

Reviewer endpoint: {model}
Exact Stage-A V4 contract SHA-256: {contract_sha}

Scientific history and intent:
- The closed 48-pair DeepSeek result remains HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS and is never pooled into V2 inference.
- Semantic-Transfer V1 reached only pre-provider review readiness and is superseded before provider execution. V2 increases independent streams from 12 to 18 and reduces Stage-B replicates from 8 to 7; this is a prospective power-allocation repair with zero V1 Stage-A outcomes.
- V2 uses six new failure-family identities arranged as three matched structural skeletons and a mechanical semantic rule: reusable procedural transformation -> MRW4; instance binding/localization -> WIN-C.
- Stage A only acquires K=8 pools for 18 streams x 8 tasks = 144 pools = 1152 actor rollouts. It has no updater, no heldout evaluation, and no treatment-effect read.
- Equal-dose support requires ALL 18 streams to have >=4 mixed pools. If any stream fails, the whole child HOLDS. For a passing child, exactly four mixed pools/stream are selected by frozen SHA salt `semantic-transfer-mrw4-v2`, yielding 72 treated pool IDs before Stage B.
- Stage B is not authorized. If later separately authorized, it freezes R=7 paired replicates/stream. The primary selector claim requires BOTH: MRW4>WIN-C over nine procedural streams and WIN-C>MRW4 over nine binding streams, each by exact one-sided 2^9 sign-flip plus positive 95% stream-bootstrap lower bound.
- V2 predeclares difficulty-only and mixedness-only routing reductions from Stage-A data, plus a three-skeleton directional consistency falsifier. These do not add provider calls.
- The contract must NOT bind an old provider identity as execution authority. Authorization requires a fresh post-contract DeepSeek identity artifact resolving exactly to deepseek-v4-pro-ga-260813, retry=0, thinking disabled.

Audit the exact dossier against these questions:
1. DISCOVERY -> CONFIRMATION: Is the post-HOLD semantic hypothesis transparently treated as discovery and prospectively tested only on new family/task identities?
2. FAMILY-ID / LABEL LEAKAGE: Do task-ID/content disjointness plus the all-task prompt-leakage audit rule out old-family lookup and explicit semantic-label leakage to the actor?
3. MATCHED SKELETON / NUISANCE BALANCE: Do the three crossed skeletons and static balance audit sufficiently reduce obvious task-class/depth/ambiguity/size confounds? What remains only a limitation rather than a P0/P1 blocker?
4. EQUAL DOSE / SUPPORT: Is the all-18-stream >=4 mixed gate a legitimate support condition rather than favorable-subset selection, given that no stream/task/model/K replacement is allowed after support inspection?
5. STAGE-A SEPARATION: Does Stage A make zero updater/heldout/effect claim and seal all 144 pools before support is opened?
6. CAUSAL PURITY: Is MRW4 truly matched-budget branch replacement rather than additive winner+failure evidence, with acting winner fixed and exact token parity reserved for the later updater runtime?
7. STATISTICS / POWER: Are nine independent streams per semantic group the proper units? Is the two-gate intersection-union logic valid? Is the explicit statement that R=7 is cost-bounded and does NOT claim 80% joint power scientifically acceptable?
8. REDUCTION BASELINES: Are the frozen difficulty-only and mixedness-only routers adequate same-information reductions for obvious capability/mixedness explanations without becoming outcome-tuned Stage-B baselines?
9. SKELETON CONSISTENCY: Is requiring proc>binding direction in each of three skeletons as a non-p-value mechanism falsifier coherent, and is the downgrade rule appropriate if pooled gates pass but one skeleton reverses?
10. ACTOR/RUNTIME SCOPE: Does the compatibility alias preserve the exact 144 update tasks and 18 forbidden b20 heldout tasks? Do mode/task/K authorization guards fail closed before provider I/O?
11. BUDGET/CHECKPOINT/LEASE: Stage A is 1152 rollouts with max 10 provider claims each (<=11520), retry=0. Are global lease, local lock, pre-I/O budget claims, first-run-only semantics, and separate resume adjudication sufficient?
12. FRESH IDENTITY: Does the control plane correctly require a fresh post-contract identity artifact before authorization rather than reusing the September 2 identity receipt?
13. PAPER STORY: If both future gates and reduction/consistency diagnostics support it, is the defensible contribution 'acting projection and learning projection should be decoupled; reusable rejected evidence should be selectively exposed' rather than 'failures help'?
14. AUTHORITY: PASS may recommend only a separate single-use Stage-A V4 authorization. Stage B and paper_claim_authority must remain false.

PASS only if remaining_blockers is exactly [] and there is no P0/P1 issue that must be repaired before spending the 1152 Stage-A rollouts. Do not demand Stage-B outcomes as a precondition for Stage A.

Return exactly one JSON object and no markdown using this schema:
{spec}
Set contract_sha256_acknowledged exactly to the SHA above.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""


base.REPAIR = CONTRACT
base.MODELS = MODELS
base.DOSSIER = DOSSIER
base.schema = schema
base.prompt_for = prompt_for


def identity_map(deepseek_path: Path, kimi_path: Path, contract_created_at: str) -> dict[str, str]:
    deepseek = json.loads(deepseek_path.read_text(encoding="utf-8"))
    kimi = json.loads(kimi_path.read_text(encoding="utf-8"))
    if deepseek.get("status") != "PASS" or kimi.get("status") != "PASS":
        raise RuntimeError("fresh reviewer identity qualification not passing")
    contract_time = datetime.fromisoformat(contract_created_at)
    if datetime.fromisoformat(str(deepseek["created_at_utc"])) <= contract_time or datetime.fromisoformat(str(kimi["created_at_utc"])) <= contract_time:
        raise RuntimeError("reviewer identity qualification must occur after Stage-A V4 contract freeze")
    drow = deepseek["models"][0]
    krow = kimi["models"][0]
    if drow.get("requested_model") != "deepseek-v4-pro" or drow.get("resolved_model") != "deepseek-v4-pro-ga-260813":
        raise RuntimeError("fresh DeepSeek reviewer identity drift")
    if drow.get("thinking_requested") != "disabled" or int(drow.get("provider_retry_limit") or -1) != 0:
        raise RuntimeError("fresh DeepSeek reviewer runtime flags drift")
    if krow.get("requested_model") != "kimi-k3" or not str(krow.get("resolved_model") or "").startswith("kimi-k3"):
        raise RuntimeError("fresh Kimi reviewer identity drift")
    if krow.get("thinking_requested") != "disabled" or int(krow.get("provider_retry_limit") or -1) != 0:
        raise RuntimeError("fresh Kimi reviewer runtime flags drift")
    resolved = {"deepseek-v4-pro": str(drow["resolved_model"]), "kimi-k3": str(krow["resolved_model"])}
    if len(set(resolved.values())) != 2:
        raise RuntimeError("reviewer identities are not distinct")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--deepseek-identity", type=Path, required=True)
    parser.add_argument("--kimi-identity", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--max-output-tokens", type=int, default=4500)
    args = parser.parse_args()
    if args.out_root.exists():
        raise RuntimeError("review output root already exists; use a fresh root for each dual-review attempt")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    expected = identity_map(args.deepseek_identity, args.kimi_identity, str(contract["created_at_utc"]))
    bound, hashes = base.dossier()
    contract_sha = base.sha_file(CONTRACT)
    base.load_env_file(args.env_file)
    source = base.ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != base.PLAN_BASE_URL:
        raise RuntimeError("semantic-transfer review refuses non-Ark-Plan route")
    settings = base.ArkSettings(
        api_key=source.api_key,
        base_url=source.base_url,
        default_model=source.default_model,
        timeout_seconds=300.0,
        max_retries=0,
    )
    client = base.ArkResponsesClient(settings)
    args.out_root.mkdir(parents=True, exist_ok=False)
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
        base.atomic_json(args.out_root / f"{base.slug(model)}.json", row)
        rows.append(row)
    completed = [row for row in rows if row.get("status") == "COMPLETED"]
    allow = len(completed) == len(rows) and all(
        row.get("review", {}).get("contract_sha256_acknowledged") == contract_sha
        and row.get("review", {}).get("verdict") == "PASS_TO_SEPARATE_STAGE_A_AUTHORIZATION"
        and row.get("review", {}).get("execution_recommendation") == "ALLOW_SEPARATE_STAGE_A_AUTHORIZATION"
        and row.get("review", {}).get("paper_claim_authority") is False
        and row.get("review", {}).get("stage_b_authority") is False
        and not row.get("review", {}).get("remaining_blockers")
        for row in completed
    )
    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-stage-a-dual-review",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "contract_sha256": contract_sha,
        "statuses": {row["requested_model"]: row.get("status") for row in rows},
        "resolved_models": {row["requested_model"]: row.get("resolved_model") for row in rows},
        "verdicts": {row["requested_model"]: row.get("review", {}).get("verdict") for row in completed},
        "remaining_blockers": {row["requested_model"]: row.get("review", {}).get("remaining_blockers") for row in completed},
        "all_pass_to_separate_stage_a_authorization": allow,
        "stage_b_authority": False,
        "paper_claim_authority": False,
    }
    summary["reviewer_identity_artifacts"] = {
        "deepseek-v4-pro": {"path": str(args.deepseek_identity), "sha256": base.sha_file(args.deepseek_identity)},
        "kimi-k3": {"path": str(args.kimi_identity), "sha256": base.sha_file(args.kimi_identity)},
    }
    base.atomic_json(args.out_root / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if len(completed) == len(rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
