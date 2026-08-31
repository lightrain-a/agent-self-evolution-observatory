from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PAPER=ROOT/"paper_drafts/c1-manuscript-strengthening-20260825"

def load(name):return json.loads((PAPER/name).read_text())

def test_reasoningbank_deepseek_stop_is_pre_scientific():
 d=load("c1-pacta-rb-deepseek-pilot-closure-20260831.json")
 assert d["status"]=="STOP_MODEL_BINDING"
 assert d["scientific_provider_calls"]==0
 assert d["binder_completion"]=="0/12"
 assert d["shadow_completion"]=="0/144"
 assert d["final_completion"]=="0/288"
 assert d["active_manuscript"]=="R9"

def test_exact_model_mismatch_is_preserved():
 d=load("c1-pacta-rb-deepseek-model-binding-20260831.json")
 assert d["expected_requested_model"]=="deepseek-v4-pro"
 assert d["expected_resolved_model"]=="deepseek-v4-pro-260425"
 assert d["requested_model"]=="deepseek-v4-pro"
 assert d["resolved_model"]=="deepseek-v4-pro-ga-260813"
 assert d["raw_response_persisted_before_parse"] is True
 assert d["substitution_attempted"] is False

def test_action_budget_and_method_remain_unadjudicated():
 q=load("c1-pacta-rb-deepseek-action-availability-qualification-20260831.json")
 c=load("c1-pacta-rb-deepseek-claim-update-20260831.json")
 assert q["status"]=="NOT_RUN_DUE_STOP_MODEL_BINDING"
 assert q["selected_scientific_max_output_tokens"] is None
 assert c["PACTA_method_claim_authority"]=="NO_NEW_SCIENTIFIC_EVIDENCE"
 assert c["writer_twin_realization"]=="NOT_RUN"
 assert c["gate_realization"]=="NOT_RUN"
