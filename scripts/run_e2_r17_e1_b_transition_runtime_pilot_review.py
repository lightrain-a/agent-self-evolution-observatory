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

DRAFT = ROOT / "generated/e2-r17-e1-b-transition-runtime-pilot-draft-contract-20260829.json"
IDENTITY = ROOT / "generated/e2-r17-v31-provider-pilot-v2-model-identity-qualification-20260829.json"
OUT_ROOT = ROOT / "generated/e2-r17-e1-b-transition-runtime-pilot-review-20260829"


def schema() -> dict[str, Any]:
    return {
        "draft_contract_sha256_acknowledged": "",
        "verdict": "PASS_TO_SEPARATELY_AUTHORIZED_E1_B_TRANSITION_RUNTIME_PILOT|REVISE_TRANSITION_PILOT|STOP_TRANSITION_PILOT",
        "historical_update_selection_assessment": "",
        "development_task_selection_assessment": "",
        "updater_causal_purity_assessment": "",
        "noninitial_skill_receipt_handoff_assessment": "",
        "actor_runtime_and_verifier_assessment": "",
        "shared_provider_budget_assessment": "",
        "checkpoint_failure_preservation_assessment": "",
        "scientific_boundary_assessment": "",
        "failure_learning_policy_assessment": "",
        "remaining_blockers": [{"priority": "P0|P1", "issue": "", "why_blocking": "", "exact_repair": ""}],
        "nonblocking_notes": [""],
        "transition_runtime_pilot_recommendation": "ALLOW_SEPARATE_FROZEN_TRANSITION_RUNTIME_PILOT_AUTHORIZATION|HOLD|STOP",
        "e1_b_negative_control_recommendation": "HOLD|STOP",
        "mrw_causal_comparison_recommendation": "HOLD|STOP",
        "paper_claim_authority": False,
        "single_sentence_verdict": "",
    }


def prompt_for(model: str, bound: str, repair_sha: str) -> str:
    spec = json.dumps(schema(), ensure_ascii=False, indent=2)
    return f"""You are an independent adversarial pre-execution reviewer for the E2-R17 E1-B transition runtime Pilot. You are blind to the other reviewer. This Pilot is NOT the E1-B negative-control scientific experiment and cannot authorize MRW, held-out future-skill inference, paper claims, frontend promotion, or submission.

Reviewer endpoint: {model}
Exact draft contract SHA-256: {repair_sha}

The immediately preceding hosted provider-runtime Pilot passed 3/3 updater arms and established real SkillEvolver runtime/measurability. One execution boundary is still untested: whether a content-addressed learned SKILL.md produced under the dedicated updater runtime can be handed to the frozen actor/evaluator runtime through the exact updater-receipt provenance path, loaded as a noninitial skill, and evaluated by the same SpreadsheetBench verifier.

The proposed transition Pilot does exactly one such handoff. It generates one WIN-only learned skill from the same eight historical E0 pools used by the provider-runtime Pilot, then evaluates that learned skill at K=1 on the lexicographically first pre-existing development task `r17-b0-agj-p4`. The development result may not select or promote any method/model/runtime and is not reported as scientific effectiveness.

Audit the exact contract/code and answer:

1. HISTORICAL UPDATE SELECTION: Are the exact same eight historical E0 pool SHAs/order reused without outcome-driven reselection? Is the update WIN-only and V3.1 arm-blinded/selected-evidence-score semantics unchanged?

2. DEVELOPMENT TASK SELECTION: Is `r17-b0-agj-p4` fixed by lexicographic development task ID before learned-skill outcome is observed? Does any path access E1 common held-out tasks or select the development task based on performance?

3. UPDATER CAUSAL PURITY: Does the updater path still use ExactMatchedEvidenceBlockRenderer, BlindedEvidenceUnit, selected evidence score, pinned SkillEvolver, dedicated updater runtime, temperature=0, retry=0, thinking disabled, max_parse_attempts=1? No MRW or A/B comparison should occur.

4. NONINITIAL SKILL RECEIPT HANDOFF: After the WIN update, does the actor receive exactly `skill_post/SKILL.md` plus the matching `update_receipt.json`? Does the actor runner revalidate skill path, skill SHA, contract SHA and authorization SHA before accepting a noninitial skill? Is omission of a pre-known learned-skill SHA from authorization scope scientifically acceptable because the learned SHA is only known after the provider update and is instead content-addressed by the bound update receipt?

5. ACTOR RUNTIME / VERIFIER: Is actor execution under the independently frozen actor/evaluator venv, exact DeepSeek resolved identity, K=1, max_turns=10, same controlled suite and SpreadsheetBench verifier? Does the transition runner validate that the actor summary loaded the learned skill SHA and updater receipt SHA, without promoting the task score?

6. SHARED BUDGET: One contract-bound ProviderBudgetLedger is shared across the updater and actor subprocess. Is 20 total / 10 per unit fail-closed, with the updater nominally consuming 10 and the single actor rollout allowed at most 10? Can either role reset/reinitialize the ledger or bypass pre-I/O claims?

7. CHECKPOINT / FAILURE PRESERVATION: If updater completes, may it be safely reused for the evaluation stage using content-addressed update checkpoint? If either update or evaluation is partial/ambiguous, does the runner preserve the stale lock and refuse automatic rerun? Is this consistent with the failure-differential policy?

8. SCIENTIFIC BOUNDARY: Confirm 0 E1 common held-out access, 0 WIN-A/WIN-B equivalence inference, 0 MRW execution, 0 learned-skill effect promotion, and 0 paper authority. The single development outcome is allowed only to prove that the verifier completes with a receipt-bound noninitial skill.

9. FAILURE LEARNING: Does the contract appropriately separate runtime/implementation failure from scientific-mechanism failure? A transition Pilot failure cannot be used against R17's mechanism; it must be diagnosed and versioned. Conversely this Pilot PASS cannot support the R17 mechanism either.

10. DECISION: PASS only if no P0/P1 blocker remains. Even PASS must keep E1-B negative-control execution HOLD, MRW HOLD, and paper_claim_authority=false.

Return exactly one JSON object and no markdown using this schema:
{spec}

Set `draft_contract_sha256_acknowledged` exactly to the SHA above. For PASS use verdict `PASS_TO_SEPARATELY_AUTHORIZED_E1_B_TRANSITION_RUNTIME_PILOT` and transition recommendation `ALLOW_SEPARATE_FROZEN_TRANSITION_RUNTIME_PILOT_AUTHORIZATION`. Keep both scientific recommendations HOLD and paper_claim_authority=false.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""


base.REPAIR = DRAFT
base.IDENTITY = IDENTITY
base.OUT_ROOT = OUT_ROOT
base.DOSSIER = (
    ("transition_pilot_draft", DRAFT),
    ("transition_pilot_runner", ROOT / "scripts/run_e2_r17_e1_b_transition_runtime_pilot.py"),
    ("actor_runner", ROOT / "scripts/run_e2_r17_actor_pool.py"),
    ("provider_runtime_helpers", ROOT / "scripts/run_e2_r17_v31_provider_runtime_pilot.py"),
    ("updater_adapter", ROOT / "research_pipeline/e2_r17_mindmemos_ark_adapter.py"),
    ("updater_wrapper", ROOT / "research_pipeline/e2_r17_mindmemos_updater.py"),
    ("renderer", ROOT / "research_pipeline/e2_r17_evidence_window_v2.py"),
    ("provider_budget", ROOT / "research_pipeline/e2_r17_provider_budget.py"),
    ("actor_runtime_validator", ROOT / "scripts/run_e2_r17_e1_a_pool_support.py"),
    ("updater_runtime_qualification", ROOT / "generated/e2-r17-updater-runtime-qualification-20260829.json"),
    ("actor_runtime_qualification", ROOT / "generated/e2-r17-runtime-dependency-qualification-r2-20260828.json"),
    ("provider_runtime_adjudication", ROOT / "generated/e2-r17-v31-provider-runtime-pilot-v2-adjudication-20260829.json"),
    ("failure_registry", ROOT / "generated/e2-r17-failure-differential-registry-v2-20260829.json"),
    ("fresh_model_identity_adjudication", ROOT / "generated/e2-r17-v31-provider-pilot-v2-model-identity-adjudication-20260829.json"),
    ("fresh_model_identity_qualification", IDENTITY),
    ("split_manifest", Path("/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2/r17_split_manifest.json")),
)
base.schema = schema
base.prompt_for = prompt_for


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--max-output-tokens", type=int, default=6000)
    args = parser.parse_args()
    expected = base.identity_map()
    bound, hashes = base.dossier()
    draft_sha = base.sha_file(DRAFT)
    base.load_env_file(args.env_file)
    source = base.ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != base.PLAN_BASE_URL:
        raise RuntimeError("transition Pilot review refuses non-Ark-Plan route")
    settings = base.ArkSettings(api_key=source.api_key, base_url=source.base_url, default_model=source.default_model, timeout_seconds=300.0, max_retries=0)
    client = base.ArkResponsesClient(settings)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for model in base.MODELS:
        row = base.call(client, model=model, expected_resolved=expected[model], bound=bound, hashes=hashes, repair_sha=draft_sha, max_output_tokens=args.max_output_tokens)
        base.atomic_json(OUT_ROOT / f"{base.slug(model)}.json", row)
        rows.append(row)
    completed = [row for row in rows if row.get("status") == "COMPLETED"]
    allow = (
        len(completed) == len(rows)
        and all(
            row.get("review", {}).get("verdict") == "PASS_TO_SEPARATELY_AUTHORIZED_E1_B_TRANSITION_RUNTIME_PILOT"
            and row.get("review", {}).get("transition_runtime_pilot_recommendation") == "ALLOW_SEPARATE_FROZEN_TRANSITION_RUNTIME_PILOT_AUTHORIZATION"
            and row.get("review", {}).get("e1_b_negative_control_recommendation") == "HOLD"
            and row.get("review", {}).get("mrw_causal_comparison_recommendation") == "HOLD"
            and row.get("review", {}).get("paper_claim_authority") is False
            and not row.get("review", {}).get("remaining_blockers")
            for row in completed
        )
    )
    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-e1-b-transition-runtime-pilot-dual-review",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "draft_contract_sha256": draft_sha,
        "statuses": {row["requested_model"]: row.get("status") for row in rows},
        "resolved_models": {row["requested_model"]: row.get("resolved_model") for row in rows},
        "verdicts": {row["requested_model"]: row.get("review", {}).get("verdict") for row in completed},
        "all_allow_separate_transition_runtime_pilot_authorization": allow,
        "independent": True,
        "exposed_to_other_review": False,
        "scientific_authority": False,
        "e1_b_negative_control_authority": False,
        "mrw_authority": False,
        "paper_claim_authority": False,
    }
    base.atomic_json(OUT_ROOT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if len(completed) == len(rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
