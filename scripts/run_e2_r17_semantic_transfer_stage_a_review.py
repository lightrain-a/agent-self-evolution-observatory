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

CONTRACT = ROOT / "generated/e2-r17-semantic-transfer-v1-stage-a-contract-20260902.json"
DEEPSEEK_ID = ROOT / "generated/e2-r17-selective-mrw-semantic-transfer-v1-deepseek-identity-qualification-20260902.json"
KIMI_ID = ROOT / "generated/e2-r17-semantic-transfer-stage-a-kimi-reviewer-identity-20260902.json"
OUT_ROOT = ROOT / "generated/e2-r17-semantic-transfer-stage-a-review-20260902"
MODELS = ("deepseek-v4-pro", "kimi-k3")

DOSSIER = (
    ("paper_method_design", ROOT / "consultations/e2-r17-selective-mrw-semantic-transfer-v1-20260902.md"),
    ("stage_a_contract", CONTRACT),
    ("stage_a_preflight", ROOT / "generated/e2-r17-semantic-transfer-v1-stage-a-preflight-20260902.json"),
    ("runtime_compat_audit", ROOT / "generated/e2-r17-semantic-transfer-v1-runtime-compat-r1-audit-20260902.json"),
    ("parent_static_audit", ROOT / "generated/e2-r17-selective-mrw-semantic-transfer-v1-static-audit-20260902.json"),
    ("parent_pre_f0", ROOT / "generated/e2-r17-selective-mrw-semantic-transfer-v1-pre-f0-20260902.json"),
    ("semantic_builders", ROOT / "research_pipeline/e2_r17_semantic_transfer_builders.py"),
    ("suite_builder", ROOT / "scripts/build_e2_r17_semantic_transfer_suite_v1.py"),
    ("stage_a_preparer", ROOT / "scripts/prepare_e2_r17_semantic_transfer_stage_a_v1.py"),
    ("generic_actor", ROOT / "scripts/run_e2_r17_actor_pool.py"),
    ("semantic_builder_tests", ROOT / "research_pipeline/test_e2_r17_semantic_transfer_builders.py"),
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
    return f"""You are an independent adversarial pre-execution reviewer for E2-R17 Selective-MRW Semantic-Transfer V1. You are a reviewer only. No Stage-A search-pool outcomes and no Stage-B learning outcomes are supplied. You may recommend at most a separately SHA-bound Stage-A pool-acquisition authorization. You may NOT authorize Stage B, heldout evaluation, analyzer, second backbone, public benchmark, or paper claims.

Reviewer endpoint: {model}
Exact Stage-A contract SHA-256: {contract_sha}

Scientific history and intent:
- The closed 48-pair DeepSeek experiment is immutable HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS.
- A previous same-family Selective-MRW V3 design was superseded before provider execution because family-ID lookup remained a reduction.
- This child uses SIX COMPLETELY NEW failure-family identities arranged as three matched structural skeletons. A mechanical pre-outcome semantic rule routes reusable procedural transformations to MRW4 and instance-binding/localization tasks to WIN-C.
- Stage A only acquires K=8 pools. It has no updater and no heldout evaluation.
- Stage B is not authorized. If later authorized, MRW4 would replace winner evidence on EXACTLY FOUR hash-frozen mixed pools per stream; every passing stream has the same treatment dose.
- The proposed selector earns a method claim only if, on untouched new family identities, (A) MRW4 beats WIN-C over six procedural streams AND (B) WIN-C beats MRW4 over six binding streams. Both exact one-sided 2^6 sign-flip tests plus positive bootstrap lower bounds must pass. This is an intersection-union claim.

Audit the exact dossier against these questions:
1. DISCOVERY -> CONFIRMATION: Is it scientifically legitimate to discover the procedural-vs-binding hypothesis after the closed HOLD, then test it only on new family identities without pooling old outcomes? Does the manuscript boundary make the post-hoc discovery transparent enough?
2. FAMILY-ID REDUCTION: Do the six new family identities plus the mechanical structural rule actually prevent an old-family lookup from routing TEST? Is there any hidden family label or metadata path that makes the test merely same-family memorization?
3. MATCHED SKELETONS: Are the three paired structural skeletons a meaningful control, or are procedural and binding families still so different that a task-class confound trivially explains the result? If a blocker remains, state the smallest pre-outcome repair.
4. EQUAL DOSE: Stage A requires every stream to have >=4 mixed pools, then chooses exactly four by frozen hash. Is this a valid pre-treatment support condition that equalizes learning-treatment dose, or does conditioning on mixedness create an unacceptable selection/collider problem for the intended claim? Note: no task/stream is dropped; if ANY stream fails support, the entire child HOLDS.
5. SUPPORT GATE: Is all-12-stream >=4 mixed support a legitimate identifiability gate, not an outcome-selected favorable subset? K/model/tasks/families cannot be changed after Stage A.
6. CAUSAL PURITY: Verify from the dossier that MRW is matched-budget branch replacement, NOT winner+failure; acting winner stays fixed; non-treated pools use winner; exact evidence-token parity is inherited from the frozen renderer. Does Stage A itself make no causal-effect claim?
7. STATISTICS: Are six independent procedural stream effects and six independent binding stream effects legitimate scientific units for their separate exact sign-flip tests? Is requiring both gates at alpha=.05 a valid intersection-union rule for the joint selector claim? Are two streams/family correctly prevented from becoming family-specific p-values?
8. SAME-INFORMATION FIXED POLICY BASELINES: Does the joint gate really establish that the structural selector beats BOTH always-WIN and universal-MRW4 without a third execution arm? Or is another same-information baseline required before Stage A?
9. ACTOR/RUNTIME SCOPE: Does the compatibility alias preserve exact task mappings? Does the unmodified generic actor enforce mode/task/K scope? The actual-path preflight says K=4, b16 heldout, and wrong mode are rejected before provider I/O. Check for a bypass.
10. BUDGET/CHECKPOINT/FAIL-CLOSED: Stage A is 96 pools x 8 rollouts, max 10 turns = <=7680 provider claims, retry=0. Is the proposed contract sufficiently fail-closed for exactly-once execution? Does any resume or quota failure need another control before authorization?
11. PAPER STORY: Is the coherent contribution now 'acting projection and learning projection should be decoupled, and rejected evidence should be selectively exposed when it carries reusable procedural information', rather than 'failures help'? Is that story supported if both future gates pass, while clearly NOT claiming a production-ready classifier or universal semantic law?
12. AUTHORITY: PASS can only recommend separately minting a single-use Stage-A authorization. Stage B and paper_claim_authority must remain false.

PASS only if remaining_blockers is exactly [] and there is no P0/P1 issue that must be repaired before spending the 768 Stage-A rollouts. Do not demand Stage-B results as a precondition for Stage A; review whether Stage A is a valid, necessary support-acquisition step.

Return exactly one JSON object and no markdown using this schema:
{spec}
Set contract_sha256_acknowledged exactly to the SHA above.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""


base.REPAIR = CONTRACT
base.OUT_ROOT = OUT_ROOT
base.MODELS = MODELS
base.DOSSIER = DOSSIER
base.schema = schema
base.prompt_for = prompt_for


def identity_map() -> dict[str, str]:
    deepseek = json.loads(DEEPSEEK_ID.read_text(encoding="utf-8"))
    kimi = json.loads(KIMI_ID.read_text(encoding="utf-8"))
    if deepseek.get("status") != "PASS" or kimi.get("status") != "PASS":
        raise RuntimeError("reviewer identity qualification not passing")
    drow = deepseek["models"][0]
    krow = kimi["models"][0]
    if drow.get("requested_model") != "deepseek-v4-pro" or drow.get("resolved_model") != "deepseek-v4-pro-ga-260813":
        raise RuntimeError("DeepSeek reviewer identity drift")
    if krow.get("requested_model") != "kimi-k3" or not str(krow.get("resolved_model") or "").startswith("kimi-k3"):
        raise RuntimeError("Kimi reviewer identity drift")
    resolved = {"deepseek-v4-pro": str(drow["resolved_model"]), "kimi-k3": str(krow["resolved_model"])}
    if len(set(resolved.values())) != 2:
        raise RuntimeError("reviewer identities are not distinct")
    return resolved


base.identity_map = identity_map


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--max-output-tokens", type=int, default=4500)
    args = parser.parse_args()
    expected = base.identity_map()
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
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
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
    base.atomic_json(OUT_ROOT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if len(completed) == len(rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
