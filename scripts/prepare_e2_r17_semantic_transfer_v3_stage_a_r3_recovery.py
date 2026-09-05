#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
R2_CONTRACT=ROOT/"generated/e2-r17-semantic-transfer-v3-stage-a-contract-r2-20260903.json"
R2_SHA="f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234"
BURNED="r17-b21-cgwb-p0";CENSOR="r17-b21-cgwp-p0"
R2_RUN=Path("/data/wyt/e2-r17-search-projection/runs/semantic-transfer-v3-stage-a-r2-20260903")
R2_LEASE=Path("/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-semantic-transfer-v3-stage-a-r2.json")
R3_RUN=Path("/data/wyt/e2-r17-search-projection/runs/semantic-transfer-v3-stage-a-r3-matched-censor-20260905")
R3_LEASE=Path("/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-semantic-transfer-v3-stage-a-r3-matched-censor.json")

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text(encoding="utf-8"))
def req(c:bool,m:str)->None:
    if not c:raise RuntimeError(m)
def atomic(p:Path,x:dict[str,Any])->None:
    req(not p.exists(),f"refuse overwrite: {p}");p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+".tmp");t.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8");os.replace(t,p)
def rel(p:Path)->str:
    try:return str(p.relative_to(ROOT))
    except ValueError:return str(p)
def file_row(p:Path)->dict[str,str]:return {"path":str(p),"sha256":sha(p)}

def main()->int:
    req(R2_CONTRACT.is_file() and sha(R2_CONTRACT)==R2_SHA,"R2 contract drift")
    r2=load(R2_CONTRACT);suite=Path(r2["suite"]["root"]);splitp=suite/"r17_split_manifest.json";metap=suite/"r17_controlled_metadata.json"
    req(sha(splitp)==r2["suite"]["split_manifest_sha256"] and sha(metap)==r2["suite"]["metadata_sha256"],"suite drift")
    split=load(splitp);meta={r["id"]:r for r in load(metap)};stream_ids=list(r2["suite"]["streams"]);orig={sid:[str(x) for x in split["e1_update_streams"][sid]] for sid in stream_ids};all_orig=[t for sid in stream_ids for t in orig[sid]];req(len(all_orig)==len(set(all_orig))==160,"original task universe drift")
    req(BURNED in all_orig and CENSOR in all_orig,"recovery exceptions absent from original task universe")
    b,c=meta[BURNED],meta[CENSOR];req(b["pair_key"]==c["pair_key"]=="semantic-transfer-v3-pair|b21|cross_group_window|p0","pair-key drift");req(b["semantic_type"]=="INSTANCE_BINDING_LOCALIZATION" and c["semantic_type"]=="PROCEDURAL_TRANSFORMATION","semantic counterpart drift")
    init_b=suite/"spreadsheetbench_verified_400/spreadsheet"/BURNED/f"{BURNED}_init.xlsx";init_c=suite/"spreadsheetbench_verified_400/spreadsheet"/CENSOR/f"{CENSOR}_init.xlsx";matched_sha=sha(init_b);req(matched_sha==sha(init_c)=="66e26351d4f79e022d0988a20f8409a0364d0eead932f8c7e6f81698c8a1cd7d","matched initial workbook drift")

    incident={
      "failure_receipt":file_row(R2_RUN/"checkpoints/failures/stv3-cgwb-00.json"),
      "burned_attempt":file_row(R2_RUN/"checkpoints/stage_a_task_claims/4d2bb0107f8fadaac6de979d1efcb6b52b4acb00b08b8b3497955c5b92f31d92.attempt.json"),
      "provider_budget_ledger":file_row(R2_RUN/"checkpoints/provider_budget.sqlite3"),
      "r2_local_lock":file_row(R2_RUN/".exclusive.lock"),
      "r2_global_lease":file_row(R2_LEASE),
      "partial_failure_artifact":file_row(R2_RUN/"cases"/BURNED/"rollout_0/r17_technical_failure.json"),
    }
    req(not (R2_RUN/"cases"/BURNED/"pool_k8.json").exists(),"burned task has complete K8 pool")
    censor_stem=hashlib.sha256(CENSOR.encode()).hexdigest();req(not (R2_RUN/"checkpoints/stage_a_task_claims"/f"{censor_stem}.attempt.json").exists(),"matched censor had prior provider attempt")

    review1=ROOT/"generated/e2-r17-v3-stage-a-technical-missing-recovery-gpt56-review-20260905.json";review2=ROOT/"generated/e2-r17-v3-r3-matched-censor-gpt56-review-20260905.json";req(load(review1)["verdict"]=="PASS_RECOVER_WITH_ONE_TERMINAL_TECHNICAL_MISSING","recovery review 1 drift");req(load(review2)["verdict"]=="PASS_R3_MATCHED_CENSOR_RECOVERY","matched-censor review drift")

    burnp=ROOT/"generated/e2-r17-semantic-transfer-v3-stage-a-r3-burn-receipt-20260905.json";censorp=ROOT/"generated/e2-r17-semantic-transfer-v3-stage-a-r3-matched-censor-receipt-20260905.json";manifestp=ROOT/"generated/e2-r17-semantic-transfer-v3-stage-a-r3-execution-units-20260905.json";oppp=ROOT/"generated/e2-r17-semantic-transfer-v3-stage-a-r3-opportunity-manifest-20260905.json";contractp=ROOT/"generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3-recovery-20260905.json"
    now=datetime.now(timezone.utc).isoformat(timespec="seconds")
    burn={"schema_version":"1.0","artifact_type":"e2-r17-v3-stage-a-r3-terminal-technical-missing-receipt","created_at_utc":now,"status":"TERMINAL_TECHNICAL_MISSING_POST_DISPATCH","task_id":BURNED,"stream_id":"stv3-cgwb-00","pair_key":b["pair_key"],"block":21,"profile_index":0,"semantic_type":b["semantic_type"],"cause":"Ark AccountQuotaExceeded after provider dispatch","provider_reset_time":"2026-09-07 00:00:00 +0800","replay_allowed":False,"continuation_allowed":False,"replacement_allowed":False,"partial_content_scientific_use":False,"complete_k8_pool_exists":False,"support_read":False,"incident_artifacts":incident}
    atomic(burnp,burn)
    censor={"schema_version":"1.0","artifact_type":"e2-r17-v3-stage-a-r3-prospective-matched-exposure-censor","created_at_utc":now,"status":"PROSPECTIVE_MATCHED_EXPOSURE_CENSOR_NO_PROVIDER_EXECUTION","task_id":CENSOR,"stream_id":"stv3-cgwp-00","pair_key":c["pair_key"],"block":21,"profile_index":0,"semantic_type":c["semantic_type"],"matched_burned_task_id":BURNED,"matched_initial_xlsx_sha256":matched_sha,"selection_basis":"unique frozen semantic counterpart with same pair_key/block/profile/matched_skeleton and byte-identical initial XLSX","provider_calls_authorized":False,"provider_execution_eligible":False,"support_eligible":False,"mixedness_qualification_eligible":False,"treatment_selection_eligible":False,"router_scoring_eligible":False,"stage_b_update_eligible":False,"replacement":False,"additional_matched_censor_allowed":False}
    atomic(censorp,censor)

    provider_by={sid:[t for t in orig[sid] if t not in {BURNED,CENSOR}] for sid in stream_ids};flat=[t for sid in stream_ids for t in provider_by[sid]];req(len(flat)==len(set(flat))==158,"R3 provider universe not 158");req(len(provider_by["stv3-cgwb-00"])==len(provider_by["stv3-cgwp-00"])==7,"R3 matched 7/7 drift");req(all(len(v)==8 for k,v in provider_by.items() if k not in {"stv3-cgwb-00","stv3-cgwp-00"}),"R3 nonaffected opportunity drift")
    manifest={"schema_version":"1.0","artifact_type":"e2-r17-v3-stage-a-r3-provider-execution-units","created_at_utc":now,"status":"FROZEN_158_ORIGINAL_PROVIDER_UNITS_NO_REPLAY_NO_REPLACEMENT","source_r2_contract_sha256":R2_SHA,"original_planned_task_count":160,"terminal_technical_missing_task_id":BURNED,"matched_no_provider_censor_task_id":CENSOR,"provider_execution_task_count":158,"ordered_task_ids":flat,"replacement_task_ids":[],"replayed_task_ids":[]}
    atomic(manifestp,manifest)
    opp={"schema_version":"1.0","artifact_type":"e2-r17-v3-stage-a-r3-recovery-opportunity-manifest","created_at_utc":now,"status":"FROZEN_MATCHED_CENSOR_7_7_8_GEOMETRY","ordered_stream_ids":stream_ids,"provider_task_ids_by_stream":provider_by,"support_eligible_task_ids_by_stream":provider_by,"future_stage_b_eligible_task_ids_by_stream":provider_by,"eligible_opportunity_count_by_stream":{sid:len(provider_by[sid]) for sid in stream_ids},"support_required_mixed_per_stream":4,"treated_mixed_pools_per_stream_if_support_passes":4,"treated_pool_total_if_support_passes":80,"excluded_units":{"terminal_technical_missing":BURNED,"matched_no_provider_censor":CENSOR},"additional_exception_policy":"STOP","raw_count_secondary_router_scores_forbidden":True,"secondary_router_score_policy":{"difficulty_only":"successful rollout rate over eligible opportunities","mixedness_only":"mixed-pool rate over eligible opportunities"}}
    atomic(oppp,opp)

    code_paths={
      "actor":"scripts/run_e2_r17_semantic_transfer_v3_actor_pool_r3_recovery.py",
      "stage_a_runner":"scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py",
      "equal_dose_adjudicator":"scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py",
      "authorization_minter":"scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py",
      "preflight":"scripts/preflight_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py",
      "control_tests":"research_pipeline/test_e2_r17_semantic_transfer_v3_r3_recovery.py",
      "stage_b_order_helper":"research_pipeline/e2_r17_semantic_transfer_v3_stage_b_order_r3_recovery.py",
      "r2_actor_base":"scripts/run_e2_r17_semantic_transfer_v3_actor_pool.py",
      "r2_runner_base":"scripts/run_e2_r17_semantic_transfer_v3_stage_a.py",
      "legacy_stream_verifier":"scripts/run_e2_r17_e1_a_pool_support.py"
    }
    bound_code={k:{"path":v,"sha256":sha(ROOT/v)} for k,v in code_paths.items()}
    contract={
      "schema_version":"1.0","artifact_type":"e2-r17-semantic-transfer-v3-stage-a-contract-r3-matched-censor-recovery","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY","scientific_role":"versioned fail-closed Stage-A recovery only; one terminal post-dispatch missing plus one deterministic matched no-provider censor; support remains closed until terminal recovery",
      "parent_r2_contract":{"path":rel(R2_CONTRACT),"sha256":R2_SHA,"status":r2["status"]},
      "failed_r2_parent":{"run_root":str(R2_RUN),"global_lease_path":str(R2_LEASE),"immutable_files":incident,"support_inspected":False,"sealed_k8_pools":0,"completed_streams":0},
      "recovery_reviews":{"one_missing":{"path":rel(review1),"sha256":sha(review1),"verdict":"PASS_RECOVER_WITH_ONE_TERMINAL_TECHNICAL_MISSING"},"matched_censor":{"path":rel(review2),"sha256":sha(review2),"verdict":"PASS_R3_MATCHED_CENSOR_RECOVERY"}},
      "recovery_exceptions":{"burn_receipt":{"path":rel(burnp),"sha256":sha(burnp)},"matched_censor_receipt":{"path":rel(censorp),"sha256":sha(censorp)},"terminal_technical_missing":BURNED,"matched_no_provider_censor":CENSOR,"pair_key":b["pair_key"],"matched_initial_xlsx_sha256":matched_sha,"replacement_allowed":False,"replay_allowed":False,"additional_matched_censor_allowed":False,"additional_attempted_but_unsealed_policy":"STOP"},
      "suite":r2["suite"],"mindmemos":r2["mindmemos"],"runtime":r2["runtime"],"env_file_path":r2["env_file_path"],"provider_route":r2["provider_route"],"model_identity_policy":{**r2["model_identity_policy"],"fresh_requalification_required_after_exact_hash_r3_review":True},
      "bound_code":bound_code,"actor":r2["actor"],
      "budget":{"actor_rollouts":1264,"max_provider_calls":12640,"provider_calls_per_rollout_limit":10,"failed_r2_pre_io_claims_bound":4,"combined_claim_upper_bound_if_r3_maxed":12644,"original_r2_max_provider_calls":12800},
      "recovery_execution_manifest":{"path":rel(manifestp),"sha256":sha(manifestp),"unit_count":158},
      "recovery_opportunity_manifest":{"path":rel(oppp),"sha256":sha(oppp)},
      "exact_once_acquisition":{"required":True,"unit_manifest_path":rel(manifestp),"unit_manifest_sha256":sha(manifestp),"unit_count":158,"claim_root":str(R3_RUN/"checkpoints/stage_a_task_claims"),"attempt_before_any_provider_io":True,"attempt_marker_creation":"O_CREAT|O_EXCL + file fsync before provider I/O","attempt_marker_immutable":True,"sealed_receipt_after_frozen_k8_pool":True,"terminal_summary_requires_provider_attempted_units":158,"terminal_summary_requires_provider_sealed_units":158,"terminal_summary_requires_terminal_technical_missing":1,"terminal_summary_requires_matched_no_provider_censor":1,"replay_allowed":False,"ambiguous_recollection_allowed":False,"replacement_sampling_allowed":False,"additional_attempted_but_unsealed_policy":"STOP"},
      "equal_dose_support":{"required_mixed_pools_per_stream":4,"streams_required":20,"eligible_opportunity_count_by_stream":opp["eligible_opportunity_count_by_stream"],"treated_mixed_pools_per_stream":4,"treated_pool_total_if_pass":80,"candidate_domain":"mixed K8 pools inside prospectively frozen Stage-B-eligible opportunity set","unmixed_pool_eligible":False,"hash_rank_applied_only_within_candidate_domain":True,"all_158_provider_pools_must_be_sealed_before_support_read":True,"support_read_excludes_burned_and_matched_censor":True,"failure_status":"HOLD_SEMANTIC_TRANSFER_V3_R3_INSUFFICIENT_EQUAL_DOSE_SUPPORT"},
      "prelearning_baseline_router_policy":{"difficulty_only":"ascending successful-rollout RATE over eligible opportunities; SHA256(semantic-transfer-difficulty-v3-r3-rate|stream_id) tie-break; lowest 10 -> MRW4","mixedness_only":"descending mixed-pool RATE over eligible opportunities; SHA256(semantic-transfer-mixedness-v3-r3-rate|stream_id) tie-break; highest 10 -> MRW4","raw_count_scoring_forbidden_due_7_7_8_geometry":True,"freeze_only_after_terminal_158_pool_recovery":True,"freeze_before_stage_b_outcomes":True,"extra_provider_calls":0},
      "stage_b_plan_no_authority":{"replicates_per_stream":4,"paired_stream_replicate_units":80,"learned_states":160,"common_heldout_tasks":20,"heldout_evaluations":3200,"primary_independent_mechanism_units":5,"primary_unit":"matched_skeleton_interaction I_h","update_pool_count_by_stream":opp["eligible_opportunity_count_by_stream"],"affected_matched_streams":["stv3-cgwb-00","stv3-cgwp-00"],"treated_pools_per_stream":4,"treated_pool_total":80,"update_pool_order":{"key":"SHA256(semantic-transfer-v3-update-order|stream_id|replicate_index|task_id)","task_id_in_key":True,"arm_in_key":False,"identical_across_win_c_and_mrw4":True,"expected_task_count_is_contract_bound_7_or_8":True},"execution_authority":False},
      "run_root":str(R3_RUN),"global_lease_path":str(R3_LEASE),
      "exactly_once":{"authorized_runs":1,"first_run_only_recovery_runner":True,"provider_execution_units":158,"terminal_technical_missing_units":1,"matched_no_provider_censor_units":1,"completed_rollout_replay":False,"automatic_retry":False,"replacement_sampling":False,"failure_preserves_running_global_lease":True,"additional_attempted_but_unsealed_policy":"STOP"},
      "analysis_boundary":{"stage_a_support_only":True,"support_read_before_terminal_recovery":False,"partial_learning_effect_read":False,"scientific_learning_effect_read":False,"stage_b_effect_inference":False,"heldout_access":False},
      "review_policy":{"surface":"ChatGPT web","model":"GPT-5.6 Sol","thinking_level":"Extra High 4/5","fresh_exact_hash_review_after_contract_freeze":True,"required_verdict":"PASS_TO_SEPARATE_R3_RECOVERY_AUTHORIZATION","required_execution_recommendation":"ALLOW_SEPARATE_R3_RECOVERY_AUTHORIZATION","stage_b_authority":False,"paper_claim_authority":False},
      "authority":{"stage_a_provider_execution":False,"stage_b_learning_execution":False,"updater":False,"heldout_evaluation":False,"analyzer":False,"second_backbone":False,"public_benchmark":False,"paper_promotion":False,"submission":False},
      "next_gate":"ZERO_PROVIDER_R3_PREFLIGHT_THEN_FRESH_GPT56_SOL_EXTRA_HIGH_EXACT_HASH_REVIEW_THEN_FRESH_MODEL_IDENTITY_THEN_SEPARATE_R3_RECOVERY_AUTHORIZATION"
    }
    atomic(contractp,contract)
    print(json.dumps({"status":contract["status"],"contract_path":rel(contractp),"contract_sha256":sha(contractp),"provider_execution_tasks":158,"burned":BURNED,"matched_censor":CENSOR,"opportunity_counts":{"stv3-cgwb-00":7,"stv3-cgwp-00":7,"other":8},"next_gate":contract["next_gate"]},ensure_ascii=False,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
