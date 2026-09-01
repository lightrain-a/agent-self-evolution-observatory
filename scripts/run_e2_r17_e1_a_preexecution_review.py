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
DRAFT = ROOT / "generated/e2-r17-e1-a-pool-support-draft-contract-20260828.json"
IDENTITY = ROOT / "generated/e2-r17-e1-a-model-identity-qualification-20260828.json"
OUT_ROOT = ROOT / "generated/e2-r17-e1-a-preexecution-review-20260828"
SUITE = Path("/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2")
MODELS = ("deepseek-v4-pro", "kimi-k3")

DOSSIER = (
    ("e1_a_draft_contract", DRAFT),
    ("v3_plan", ROOT / "consultations/e2-r17-experiment-plan-v3-20260828.md"),
    ("v3_1_mechanical_adjudication", ROOT / "generated/e2-r17-v3-1-mechanical-pilot-adjudication-20260828.json"),
    ("actor_runner", ROOT / "scripts/run_e2_r17_actor_pool.py"),
    ("e1_a_orchestrator", ROOT / "scripts/run_e2_r17_e1_a_pool_support.py"),
    ("support_adjudicator", ROOT / "scripts/adjudicate_e2_r17_e1_a_pool_support.py"),
    ("authority_scope_tests", ROOT / "research_pipeline/test_e2_r17_actor_authority_scope.py"),
    ("actor_model_identity_adjudication", ROOT / "generated/e2-r17-e1-a-model-identity-adjudication-20260828.json"),
    ("review_identity_qualification", IDENTITY),
    ("suite_manifest", SUITE / "suite_manifest.json"),
    ("split_manifest", SUITE / "r17_split_manifest.json"),
    ("controlled_metadata", SUITE / "r17_controlled_metadata.json"),
)


def schema() -> dict[str, Any]:
    return {
        "draft_contract_sha256_acknowledged": "",
        "repair_sha256_acknowledged": "",
        "verdict": "PASS_TO_SEPARATELY_BOUND_E1_A_AUTHORIZATION|REVISE_E1_A_BEFORE_AUTHORIZATION|STOP_E1_A",
        "support_gate_assessment": "",
        "outcome_selection_assessment": "",
        "split_and_unit_assessment": "",
        "authorization_scope_assessment": "",
        "checkpoint_resume_assessment": "",
        "stale_lock_assessment": "",
        "provider_budget_assessment": "",
        "model_identity_assessment": "",
        "support_adjudicator_assessment": "",
        "updater_separation_assessment": "",
        "remaining_blockers": [
            {"priority": "P0|P1", "issue": "", "why_blocking": "", "exact_repair": ""}
        ],
        "nonblocking_notes": [""],
        "e1_a_recommendation": "ALLOW_SEPARATE_FROZEN_E1_A_AUTHORIZATION|HOLD|STOP",
        "e1_b_recommendation": "HOLD|STOP",
        "paper_claim_authority": False,
        "single_sentence_verdict": "",
    }


def prompt_for(model: str, bound: str, draft_sha: str) -> str:
    spec = json.dumps(schema(), ensure_ascii=False, indent=2)
    return f"""You are an independent adversarial pre-execution reviewer for E2-R17 E1-A. You are blind to the other reviewer. This review has zero authority by itself. It may at most recommend minting a separately SHA-bound authorization for E1-A pool generation/support measurement. It cannot authorize E1-B updater calls, held-out future-skill evaluation, paper claims, frontend promotion, or submission.

Reviewer endpoint: {model}
Exact E1-A draft contract SHA-256: {draft_sha}

E1-A's scientific role is deliberately narrow: freeze the predeclared 96 update-task search pools (12 streams x 8 tasks, K=8 = 768 actor rollouts) and evaluate only a pre-treatment identifiability/support gate. No updater call, MRW/WIN comparison, RB aggregation, future-skill evaluation, or method-effectiveness statistic occurs in E1-A.

Audit the actual code and frozen split. Answer these questions:

1. SUPPORT GATE: Is `mixed>=24/96 AND exposed_streams>=8/12 with each exposed stream >=2 mixed pools` a legitimate predeclared identifiability/support gate rather than method-outcome selection, given that all 96 pools must be frozen before the gate, no task/pool may be replaced/dropped afterward, borderline values fail, and the thresholds were frozen in V3 before E1-A outcomes? The separate >=4/6 family gate must not control pooled E1-B authority.

2. OUTCOME SELECTION: Identify any path in the orchestrator or adjudicator that could inspect mixed/support outcomes early and selectively stop, replace, rerun, or omit tasks to improve support. Technical failures may stop execution but cannot be treated as scientific failures or replaced based on scores.

3. UNITS/SPLIT: Verify the bound split contains exactly 12 e1_update_streams, 8 unique tasks each, 96 unique tasks total, and that it is separated from development and held-out future probes as represented in the bound suite artifacts.

4. AUTHORITY SCOPE: Inspect the new fail-closed execution_scope check in run_e2_r17_actor_pool.py. A final E1-A authorization must bind allowed_modes=['e1'], the exact 96 allowed_task_ids, exact_k=8, suite/split SHAs, initial-skill SHA, e1_a=true and e1_b=false. Can the proposed authorization still be trivially misused to run out-of-scope tasks/K/noninitial skills?

5. CHECKPOINT/RESUME: Inspect both layers. run_actor_rollout should immediately persist a trajectory and content-addressed ref and reuse it if valid. The E1-A orchestrator should persist per-task prefix/K pools, per-stream summaries, append+fsync completed_streams.jsonl, SHA-revalidate completed streams/rollouts before reuse, and execute only missing work. If interrupted inside an 8-rollout task, would resuming after explicit stale-lock adjudication avoid duplicate completed provider calls?

6. STALE LOCK: The orchestrator intentionally leaves `.exclusive.lock` after any failed subprocess so an operator must inspect process/checkpoints before resuming. Is this appropriately fail-closed for known MCP 502/timeout semantics? Flag if successful completion or ordinary exception handling can accidentally remove a lock that should remain.

7. BUDGET: K=8, max_turns=10, retry=0 gives 768 actor rollouts and a declared ceiling of 7680 provider calls with max_output_tokens=4096 per call. Is that ceiling structurally enforced by the agent runtime, or does the contract/runner need another pre-call accounting guard before scientific execution? If P0, specify a repair.

8. MODEL IDENTITY: The E1-A qualification immediately before this review resolves deepseek-v4-pro to deepseek-v4-pro-ga-260813 and retry=0/thinking disabled. Does the bound actor runner enforce that resolved identity on every provider receipt and fail on drift?

9. SUPPORT ADJUDICATOR: Does adjudicate_e2_r17_e1_a_pool_support.py independently recompute the 96 exact K=8 pools, trajectory SHAs, mixed total, exposed streams, and no-updater condition before returning support PASS/STOP? Does it accidentally grant E1-B execution authority?

10. UPDATER SEPARATION: Verify E1-A cannot call MindMemOS SkillEvolver or evaluate learned skills. Its output is only frozen pools + support. Even a support PASS must require a separate immutable E1-B contract with fresh updater identity and WIN-A/WIN-B negative-control-first logic.

11. SELECTION DISCIPLINE: Do not recommend changing the support thresholds, tasks, K, or model based on E1-A outcomes. If the frozen support gate fails, the current E1 mechanism is not identifiable on this controlled substrate and E1 must stop before updater calls.

Return exactly one JSON object and no markdown using this schema:
{spec}

Set both `draft_contract_sha256_acknowledged` and the transport-alias field `repair_sha256_acknowledged` exactly to the SHA above. Keep `paper_claim_authority` false and `e1_b_recommendation` HOLD on any PASS. A PASS recommends only that a final contract/authorization be minted with the reviewed semantics and exact code/data bindings.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--max-output-tokens", type=int, default=5000)
    args = parser.parse_args()

    base.IDENTITY = IDENTITY
    base.DOSSIER = DOSSIER
    base.OUT_ROOT = OUT_ROOT
    base.schema = schema
    base.prompt_for = prompt_for

    expected = base.identity_map()
    bound, hashes = base.dossier()
    draft_sha = base.sha_file(DRAFT)
    base.load_env_file(args.env_file)
    source = base.ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != base.PLAN_BASE_URL:
        raise RuntimeError("E1-A review refuses non-Ark-Plan route")
    settings = base.ArkSettings(
        api_key=source.api_key,
        base_url=source.base_url,
        default_model=source.default_model,
        timeout_seconds=300.0,
        max_retries=0,
    )
    client = base.ArkResponsesClient(settings)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
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
        # base.call names this field repair_sha256; retain it as transport metadata,
        # while the embedded review schema binds the exact draft contract SHA.
        base.atomic_json(OUT_ROOT / f"{base.slug(model)}.json", row)
        rows.append(row)

    completed = [row for row in rows if row.get("status") == "COMPLETED"]
    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-e1-a-dual-preexecution-review-summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "draft_contract_sha256": draft_sha,
        "statuses": {row["requested_model"]: row.get("status") for row in rows},
        "resolved_models": {row["requested_model"]: row.get("resolved_model") for row in rows},
        "verdicts": {row["requested_model"]: row.get("review", {}).get("verdict") for row in completed},
        "e1_a_recommendations": {row["requested_model"]: row.get("review", {}).get("e1_a_recommendation") for row in completed},
        "e1_b_recommendations": {row["requested_model"]: row.get("review", {}).get("e1_b_recommendation") for row in completed},
        "independent": True,
        "exposed_to_other_review": False,
        "scientific_authority": False,
        "paper_claim_authority": False,
        "all_completed": len(completed) == len(rows),
        "all_allow_separate_e1_a_authorization": (
            len(completed) == len(rows)
            and all(
                row.get("review", {}).get("verdict") == "PASS_TO_SEPARATELY_BOUND_E1_A_AUTHORIZATION"
                and row.get("review", {}).get("e1_a_recommendation") == "ALLOW_SEPARATE_FROZEN_E1_A_AUTHORIZATION"
                and row.get("review", {}).get("e1_b_recommendation") == "HOLD"
                and row.get("review", {}).get("paper_claim_authority") is False
                for row in completed
            )
        ),
    }
    base.atomic_json(OUT_ROOT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["all_completed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
