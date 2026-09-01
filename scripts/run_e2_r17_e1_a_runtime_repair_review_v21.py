#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_e2_r17_e1_a_preexecution_review as review

DRAFT = ROOT / "generated/e2-r17-e1-a-pool-support-v2-1-draft-contract-20260828.json"
IDENTITY = ROOT / "generated/e2-r17-e1-a-v2-1-model-identity-qualification-20260828.json"
OUT_ROOT = ROOT / "generated/e2-r17-e1-a-runtime-repair-review-v21-20260828"
SUITE = Path("/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2")


def schema() -> dict[str, Any]:
    return {
        "draft_contract_sha256_acknowledged": "",
        "repair_sha256_acknowledged": "",
        "verdict": "PASS_TO_SEPARATELY_BOUND_E1_A_AUTHORIZATION|REVISE_E1_A_BEFORE_AUTHORIZATION|STOP_E1_A",
        "failed_v2_contamination_assessment": "",
        "runtime_binding_assessment": "",
        "runtime_freeze_and_import_assessment": "",
        "provider_budget_preservation_assessment": "",
        "authorization_runtime_scope_assessment": "",
        "checkpoint_resume_assessment": "",
        "support_gate_and_selection_assessment": "",
        "model_identity_assessment": "",
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
    return f"""You are an independent adversarial pre-execution reviewer for E2-R17 E1-A V2.1. You are blind to the other reviewer. This review has zero execution authority by itself. It may at most recommend minting a separately SHA-bound E1-A pool-generation authorization. It cannot authorize E1-B updater calls, held-out future-skill evaluation, paper claims, frontend promotion, or submission.

Reviewer endpoint: {model}
Exact V2.1 draft contract SHA-256: {draft_sha}

History: the prior V2 E1-A contract was properly authorized after dual review, but its first stream failed before any rollout because the orchestrator spawned the actor with ambient `/usr/bin/python3` instead of the already-qualified MindMemOS virtual environment. The preserved failed root has 0 completed streams, 0 trajectory refs, and the SQLite provider ledger has 0 claims. No mixed/rescue/support outcome was inspected. The failed V2 contract/root is not retryable. V2.1 is a fresh contract/root whose only intended semantic change is explicit frozen-runtime binding; the previously reviewed fail-closed provider-budget repair and E1-A support design must remain intact.

Audit the actual bound code/artifacts and answer:

1. FAILED V2 CONTAMINATION: Does the failure adjudication establish a pre-provider technical failure rather than a scientific result? Are zero provider claims, zero completed rollouts, zero updater calls/evaluations, no support inspection, and preservation of the stale lock sufficient to permit a fresh contract without outcome selection? The old V2 root/lock must remain untouched and V2 itself must not be retried.

2. RUNTIME BINDING: Inspect `validate_runtime` and the E1-A orchestrator. Before spawning any actor, does it require the exact contract-bound venv, exact `venv/bin/python`, runtime freeze SHA, runtime qualification artifact SHA/status, and a fresh import smoke? Does the actor subprocess use that exact runtime python and an environment with `VIRTUAL_ENV` and `PATH` bound to the venv, rather than ambient `sys.executable`?

3. RUNTIME FREEZE: Is the bound runtime the same previously qualified E0/MindMemOS runtime (`mindmemos-eval-venv`, freeze SHA ed0e...044e, qualification SHA 38a1...44e) and does the zero-provider smoke require pydantic/openpyxl plus the exact MindMemOS actor/environment imports? Flag any path where an ambient Python can still execute the actor/provider path.

4. PROVIDER BUDGET: Confirm V2.1 preserves the pre-I/O SQLite provider budget ledger from V2: transactional claim before generation I/O, exact contract+authorization binding, 10-call per-rollout ceiling, 7680 global ceiling, claims never released after ambiguity/crash, budget provenance in successful receipts/trajectory refs, and resume validation. The prior zero-provider tests blocked the 11th and 7681st attempts before provider I/O. Has the runtime repair weakened any of this?

5. AUTHORIZATION SCOPE: The final V2.1 authorization must bind the exact 96 tasks, mode=e1, K=8, initial skill, resolved model and identity SHA, max_turns/output tokens, provider budget, plus runtime_python_executable, runtime_freeze_sha256, and runtime_qualification_sha256. Does the orchestrator fail closed on runtime-scope drift before actor spawn?

6. CHECKPOINT/RESUME: Given the shared budget ledger and content-addressed rollout refs, does V2.1 still avoid duplicate completed provider calls on an explicitly adjudicated resume? Claims from ambiguous crashed calls are conservatively consumed and are not reset. Flag any counter-reset or cross-contract reuse path.

7. SUPPORT / OUTCOME SELECTION: Has the runtime repair changed the frozen pre-treatment gate (`mixed>=24/96`, >=8/12 streams each >=2 mixed), tasks, K, model, support adjudication, or no-replacement rule? The support adjudicator must recompute per-stream/per-family support directly from all 96 frozen pools and must not grant E1-B.

8. MODEL IDENTITY: Fresh V2.1 qualification must bind deepseek-v4-pro to deepseek-v4-pro-ga-260813 and kimi-k3 to kimi-k3 with retry=0/thinking disabled. The actor scientific path uses DeepSeek and must fail on resolved-model drift.

9. UPDATER SEPARATION: E1-A remains pool generation/support only. Verify the repair adds no updater or learned-skill evaluation path. Even support PASS only permits preparation of a separate E1-B contract.

10. DECISION: PASS only if there is no P0/P1 blocker to separately mint E1-A V2.1 authorization. Do not recommend changing tasks/K/model/support thresholds based on any observed outcome. Keep E1-B HOLD and paper_claim_authority=false.

Return exactly one JSON object and no markdown using this schema:
{spec}

Set both `draft_contract_sha256_acknowledged` and `repair_sha256_acknowledged` exactly to the SHA above. Keep `paper_claim_authority` false.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""


review.DRAFT = DRAFT
review.IDENTITY = IDENTITY
review.OUT_ROOT = OUT_ROOT
review.schema = schema
review.prompt_for = prompt_for
review.DOSSIER = (
    ("e1_a_v21_draft_contract", DRAFT),
    ("failed_v2_runtime_adjudication", ROOT / "generated/e2-r17-e1-a-v2-runtime-failure-adjudication-20260828.json"),
    ("prior_v2_dual_review", ROOT / "generated/e2-r17-e1-a-preexecution-review-v2-20260828/summary.json"),
    ("runtime_qualification", ROOT / "generated/e2-r17-runtime-dependency-qualification-r2-20260828.json"),
    ("runtime_freeze", Path("/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt")),
    ("provider_budget_ledger", ROOT / "research_pipeline/e2_r17_provider_budget.py"),
    ("ark_plan_react", ROOT / "research_pipeline/e2_r17_ark_plan_react.py"),
    ("actor_pool", ROOT / "research_pipeline/e2_r17_actor_pool.py"),
    ("actor_runner", ROOT / "scripts/run_e2_r17_actor_pool.py"),
    ("e1_a_orchestrator", ROOT / "scripts/run_e2_r17_e1_a_pool_support.py"),
    ("support_adjudicator", ROOT / "scripts/adjudicate_e2_r17_e1_a_pool_support.py"),
    ("provider_budget_tests", ROOT / "research_pipeline/test_e2_r17_provider_budget.py"),
    ("fresh_model_identity_adjudication", ROOT / "generated/e2-r17-e1-a-v2-1-model-identity-adjudication-20260828.json"),
    ("fresh_model_identity_qualification", IDENTITY),
    ("suite_manifest", SUITE / "suite_manifest.json"),
    ("split_manifest", SUITE / "r17_split_manifest.json"),
)


if __name__ == "__main__":
    raise SystemExit(review.main())
