#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_e2_r17_e1_a_preexecution_review as review

DRAFT = ROOT / "generated/e2-r17-e1-a-pool-support-v2-draft-contract-20260828.json"
IDENTITY = ROOT / "generated/e2-r17-e1-a-v2-model-identity-qualification-20260828.json"
OUT_ROOT = ROOT / "generated/e2-r17-e1-a-preexecution-review-v2-20260828"
SUITE = Path("/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2")

review.DRAFT = DRAFT
review.IDENTITY = IDENTITY
review.OUT_ROOT = OUT_ROOT
review.DOSSIER = (
    ("e1_a_v2_draft_contract", DRAFT),
    ("provider_budget_repair_memo", ROOT / "consultations/e2-r17-e1-a-provider-budget-repair-v2-20260828.md"),
    ("v3_plan", ROOT / "consultations/e2-r17-experiment-plan-v3-20260828.md"),
    ("v3_1_mechanical_adjudication", ROOT / "generated/e2-r17-v3-1-mechanical-pilot-adjudication-20260828.json"),
    ("provider_budget_ledger", ROOT / "research_pipeline/e2_r17_provider_budget.py"),
    ("ark_plan_react", ROOT / "research_pipeline/e2_r17_ark_plan_react.py"),
    ("actor_pool", ROOT / "research_pipeline/e2_r17_actor_pool.py"),
    ("search_projection_runner", ROOT / "research_pipeline/e2_r17_search_projection_runner.py"),
    ("actor_runner", ROOT / "scripts/run_e2_r17_actor_pool.py"),
    ("e1_a_orchestrator", ROOT / "scripts/run_e2_r17_e1_a_pool_support.py"),
    ("support_adjudicator", ROOT / "scripts/adjudicate_e2_r17_e1_a_pool_support.py"),
    ("provider_budget_tests", ROOT / "research_pipeline/test_e2_r17_provider_budget.py"),
    ("authority_scope_tests", ROOT / "research_pipeline/test_e2_r17_actor_authority_scope.py"),
    ("actor_model_identity_adjudication", ROOT / "generated/e2-r17-e1-a-v2-model-identity-adjudication-20260828.json"),
    ("review_identity_qualification", IDENTITY),
    ("suite_manifest", SUITE / "suite_manifest.json"),
    ("split_manifest", SUITE / "r17_split_manifest.json"),
    ("controlled_metadata", SUITE / "r17_controlled_metadata.json"),
)


if __name__ == "__main__":
    raise SystemExit(review.main())
