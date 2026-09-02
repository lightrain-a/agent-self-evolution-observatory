#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_e2_r17_semantic_transfer_stage_a_review as review

CONTRACT = ROOT / "generated/e2-r17-semantic-transfer-v1-stage-a-r2-contract-20260902.json"
OUT_ROOT = ROOT / "generated/e2-r17-semantic-transfer-stage-a-r2-review-20260902"
DOSSIER = (
    ("paper_method_design", ROOT / "consultations/e2-r17-selective-mrw-semantic-transfer-v1-20260902.md"),
    ("stage_a_r2_contract", CONTRACT),
    ("stage_a_r2_preflight", ROOT / "generated/e2-r17-semantic-transfer-v1-stage-a-r2-preflight-20260902.json"),
    ("review_quota_hold", ROOT / "generated/e2-r17-semantic-transfer-stage-a-review-quota-hold-20260902.json"),
    ("runtime_compat_audit", ROOT / "generated/e2-r17-semantic-transfer-v1-runtime-compat-r1-audit-20260902.json"),
    ("parent_static_audit", ROOT / "generated/e2-r17-selective-mrw-semantic-transfer-v1-static-audit-20260902.json"),
    ("model_identity_adjudication", ROOT / "generated/e2-r17-semantic-transfer-v1-model-identity-adjudication-20260902.json"),
    ("semantic_builders", ROOT / "research_pipeline/e2_r17_semantic_transfer_builders.py"),
    ("suite_builder", ROOT / "scripts/build_e2_r17_semantic_transfer_suite_v1.py"),
    ("generic_actor", ROOT / "scripts/run_e2_r17_actor_pool.py"),
    ("stage_a_r2_runner", ROOT / "scripts/run_e2_r17_semantic_transfer_stage_a_v1.py"),
    ("equal_dose_adjudicator", ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_stage_a_v1.py"),
    ("authorization_minter", ROOT / "scripts/authorize_e2_r17_semantic_transfer_stage_a_r2.py"),
    ("r2_preflight_code", ROOT / "scripts/preflight_e2_r17_semantic_transfer_stage_a_r2.py"),
    ("semantic_builder_tests", ROOT / "research_pipeline/test_e2_r17_semantic_transfer_builders.py"),
)

review.CONTRACT = CONTRACT
review.OUT_ROOT = OUT_ROOT
review.DOSSIER = DOSSIER
review.base.REPAIR = CONTRACT
review.base.OUT_ROOT = OUT_ROOT
review.base.DOSSIER = DOSSIER

if __name__ == "__main__":
    raise SystemExit(review.main())
