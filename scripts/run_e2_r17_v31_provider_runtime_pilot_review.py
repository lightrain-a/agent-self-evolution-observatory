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

DRAFT = ROOT / "generated/e2-r17-v31-provider-runtime-pilot-draft-contract-20260828.json"
IDENTITY = ROOT / "generated/e2-r17-v31-provider-pilot-model-identity-qualification-20260828.json"
OUT_ROOT = ROOT / "generated/e2-r17-v31-provider-runtime-pilot-review-20260828"


def schema() -> dict[str, Any]:
    return {
        "draft_contract_sha256_acknowledged": "",
        "verdict": "PASS_TO_SEPARATELY_AUTHORIZED_PROVIDER_RUNTIME_PILOT|REVISE_PROVIDER_RUNTIME_PILOT|STOP_PROVIDER_RUNTIME_PILOT",
        "outcome_blind_selection_assessment": "",
        "win_clone_identity_assessment": "",
        "arm_blinding_assessment": "",
        "token_parity_assessment": "",
        "updater_semantics_assessment": "",
        "provider_budget_assessment": "",
        "checkpoint_resume_assessment": "",
        "runtime_and_model_identity_assessment": "",
        "scientific_boundary_assessment": "",
        "remaining_blockers": [
            {"priority": "P0|P1", "issue": "", "why_blocking": "", "exact_repair": ""}
        ],
        "nonblocking_notes": [""],
        "provider_runtime_pilot_recommendation": "ALLOW_SEPARATE_FROZEN_PROVIDER_RUNTIME_PILOT_AUTHORIZATION|HOLD|STOP",
        "e1_b_recommendation": "HOLD|STOP",
        "paper_claim_authority": False,
        "single_sentence_verdict": "",
    }


def prompt_for(model: str, bound: str, repair_sha: str) -> str:
    spec = json.dumps(schema(), ensure_ascii=False, indent=2)
    return f"""You are an independent adversarial pre-execution reviewer for E2-R17 V3.1 provider-runtime Pilot. You are blind to the other reviewer. This review is runtime/measurability only and cannot authorize E1-B scientific execution, held-out future-skill evaluation, paper claims, frontend promotion, or submission.

Reviewer endpoint: {model}
Exact draft contract SHA-256: {repair_sha}

Context: E1-A has already frozen 96 exact K=8 pools and independently passed its pre-treatment support gate. This new Pilot is NOT allowed to inspect E1 held-out future-skill outcomes. It uses eight historical E0 pools chosen by the predeclared rule "lexicographically first eight pool_k8 paths" and exists only because V3.1 previously passed a zero-provider mechanical Pilot but has not yet passed a real hosted SkillEvolver runtime Pilot.

Audit the exact contract and source code. Answer:

1. OUTCOME-BLIND SELECTION: Is the eight-pool selection rule fixed by path order rather than mixed/rescue/effect outcome? Does the Pilot avoid using any E1 held-out probe or learned-skill quality to select pools/model/renderer?

2. WIN-A / WIN-B IDENTICAL TREATMENT: Before provider calls, do WIN-A and WIN-B reuse the same pre-rendered winner BlindedEvidenceUnit list and same winner StreamProjection from the same initial skill and exact eight pools? Is the initial evidence byte-identical and score-identical? Hosted stochasticity may change later generated prompts; that is precisely what the later negative control measures and must not be confused with pre-provider treatment drift.

3. ARM BLINDING: Trace the actual first-party SkillEvolver path. Are updater-visible messages restricted to BlindedEvidenceUnit.evidence_text, with arm/projection/rollout/path/provider/provenance metadata outside model-visible messages? Does selected-evidence score, not served acting score, enter the updater's score field?

4. TOKEN PARITY: Is ExactMatchedEvidenceBlockRenderer used to match actual final re-tokenized WIN/MRW evidence length under frozen tiktoken 0.11.0 cl100k_base, with no padding? On nonmixed pools, does MRW equal WIN byte-for-byte? Is transcript_max_chars=100000 nonbinding and explicitly checked?

5. UPDATER SEMANTICS: Does the Pilot exercise real first-party MindMemOS SkillEvolver at pinned commit 9049182..., batch=8, temperature=0, retry=0, thinking disabled, max_parse_attempts=1, while measuring calls/tokens/latency/parse errors only? No learned-skill quality comparison may be performed.

6. PROVIDER BUDGET: Inspect the updater adapter and shared ProviderBudgetLedger. Does every hosted generation claim budget transactionally before provider I/O? Are limits 10 per arm / 30 total, contract+authorization bound, and claims never released after ambiguous failures? Are claims reflected in receipts? Could any parse-correction or poll recovery bypass the claim ceiling?

7. CHECKPOINT/RESUME: Is each completed arm persisted/content-addressed and placed in completed_arms.jsonl? On resume are completed receipt/skill SHAs and contract/auth/causal-purity mode revalidated? Most importantly, if a provider-call directory exists for an incomplete arm, does the Pilot STOP instead of automatically rerunning that arm?

8. RUNTIME / IDENTITY: Must the Pilot itself run under the exact frozen MindMemOS venv; are runtime freeze/qualification, bound code SHAs, MindMemOS commit/clean state, selected pool SHAs and fresh DeepSeek resolved identity validated before provider calls?

9. SCIENTIFIC BOUNDARY: Confirm zero new actor rollouts, zero E1 held-out evaluation, zero method-effect GO/HOLD/STOP, and zero E1-B authority. A PASS may recommend only minting a separate SHA-bound provider-runtime Pilot authorization.

10. DECISION: PASS only if there is no P0/P1 blocker. Keep E1-B HOLD and paper_claim_authority=false regardless of Pilot readiness.

Return exactly one JSON object and no markdown using this schema:
{spec}

Set `draft_contract_sha256_acknowledged` exactly to the SHA above. For PASS use verdict `PASS_TO_SEPARATELY_AUTHORIZED_PROVIDER_RUNTIME_PILOT` and recommendation `ALLOW_SEPARATE_FROZEN_PROVIDER_RUNTIME_PILOT_AUTHORIZATION`. Keep e1_b_recommendation=HOLD and paper_claim_authority=false.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""


base.REPAIR = DRAFT
base.IDENTITY = IDENTITY
base.OUT_ROOT = OUT_ROOT
base.DOSSIER = (
    ("provider_runtime_pilot_draft", DRAFT),
    ("provider_runtime_pilot_runner", ROOT / "scripts/run_e2_r17_v31_provider_runtime_pilot.py"),
    ("updater_adapter", ROOT / "research_pipeline/e2_r17_mindmemos_ark_adapter.py"),
    ("updater_wrapper", ROOT / "research_pipeline/e2_r17_mindmemos_updater.py"),
    ("renderer", ROOT / "research_pipeline/e2_r17_evidence_window_v2.py"),
    ("provider_budget", ROOT / "research_pipeline/e2_r17_provider_budget.py"),
    ("runtime_validator", ROOT / "scripts/run_e2_r17_e1_a_pool_support.py"),
    ("adapter_tests", ROOT / "research_pipeline/test_e2_r17_mindmemos_ark_adapter.py"),
    ("updater_v31_tests", ROOT / "research_pipeline/test_e2_r17_mindmemos_updater_v31.py"),
    ("renderer_tests", ROOT / "research_pipeline/test_e2_r17_evidence_window_v2.py"),
    ("provider_budget_tests", ROOT / "research_pipeline/test_e2_r17_provider_budget.py"),
    ("fresh_model_identity_adjudication", ROOT / "generated/e2-r17-v31-provider-pilot-model-identity-adjudication-20260828.json"),
    ("fresh_model_identity_qualification", IDENTITY),
    ("e1_a_support_adjudication", ROOT / "generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json"),
    ("v31_mechanical_contract", ROOT / "generated/e2-r17-v3-1-mechanical-pilot-contract-20260828.json"),
)
base.schema = schema
base.prompt_for = prompt_for


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
        raise RuntimeError("provider runtime Pilot review refuses non-Ark-Plan route")
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
    for model in base.MODELS:
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
    allow = (
        len(completed) == len(rows)
        and all(
            row.get("review", {}).get("draft_contract_sha256_acknowledged") == draft_sha
            and row.get("review", {}).get("verdict") == "PASS_TO_SEPARATELY_AUTHORIZED_PROVIDER_RUNTIME_PILOT"
            and row.get("review", {}).get("provider_runtime_pilot_recommendation") == "ALLOW_SEPARATE_FROZEN_PROVIDER_RUNTIME_PILOT_AUTHORIZATION"
            and row.get("review", {}).get("e1_b_recommendation") == "HOLD"
            and row.get("review", {}).get("paper_claim_authority") is False
            and not row.get("review", {}).get("remaining_blockers")
            for row in completed
        )
    )
    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v31-provider-runtime-pilot-dual-review",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "draft_contract_sha256": draft_sha,
        "statuses": {row["requested_model"]: row.get("status") for row in rows},
        "resolved_models": {row["requested_model"]: row.get("resolved_model") for row in rows},
        "verdicts": {row["requested_model"]: row.get("review", {}).get("verdict") for row in completed},
        "all_allow_separate_provider_runtime_pilot_authorization": allow,
        "independent": True,
        "exposed_to_other_review": False,
        "scientific_authority": False,
        "e1_b_authority": False,
        "paper_claim_authority": False
    }
    base.atomic_json(OUT_ROOT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if len(completed) == len(rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
