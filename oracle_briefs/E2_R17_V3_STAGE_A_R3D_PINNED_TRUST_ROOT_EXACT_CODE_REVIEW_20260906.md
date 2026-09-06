# E2-R17 V3 Stage-A R3D point-of-use trust-root exact-code review

Date: 2026-09-06
Scope: fresh independent ZERO-PROVIDER exact-code closure review of the single R3C blocker.

R3C review verdict was `REVISE_R3C_BEFORE_PROVIDER_RECOVERY`. It PASSed scientific equivalence, runtime compatibility, and single-use semantics, but found one blocker: the adjudicator derived its Ed25519 trust root from the caller-supplied contract. R3D must close exactly that substituted-contract trust-root attack. Do not reopen R3 scientific geometry or request workload for appearance.

Hard gate remains `NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800`. PASS here grants no provider call and no Stage-B authority.


## Frozen hashes
```json
{
  "parent_r3_sha": "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085",
  "parent_r3c_sha": "03b2608872424da2bdf78408266a69b28ff565bc9d84bf929aa82ba7bc11e030",
  "r3d_contract_sha": "21f7a50f4e14f48a139ecfa122f7c8a443d4195a1ade0267ccececcb6e424717",
  "r3d_preflight_sha": "8894bf0e76d4f1b0a8f101ca55df0ff8728696bc29bf888e6287ab2046c724fa",
  "production_public_key_sha": "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0",
  "adjudicator_sha": "b26089a8184db4d1cde5c3fbe02549440d05958af74f405c858749d16d0b13a6",
  "verifier_sha": "28a32359e0005677da2900470eb3f41c0e847f048582fc12309000629bc5e093",
  "tests_sha": "790935b394dc3955f8b6b9cac9b83a96e2d717283fe9973135002c8e1a29c67e",
  "minter_sha": "c8b7490878937114e69e74d428a7ad90aee9eb85488a5890dcaa5eda96e17420",
  "gate_sha": "0abd0325414838bc0692caeed7908f5ab4be1d36126c44cca1ed587d2f343752"
}
```

## R3C blocker receipt
```json
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-v3-r3c-signed-capability-independent-review",
  "created_at_utc": "2026-09-06T03:48:00+00:00",
  "status": "COMPLETED_WITH_DUPLICATED_FINAL_DELIVERY_RETAINED_AS_REVISE_EVIDENCE_ONLY",
  "surface": "ChatGPT web",
  "model": "GPT-5.6 Sol",
  "thinking_level": "Extra High 4/5",
  "conversation_url": "https://chatgpt.com/c/6a9c4acc-4098-83ee-ae07-f8e422f0d25f",
  "prompt_packet_path": "oracle_briefs/E2_R17_V3_STAGE_A_R3C_SIGNED_CAPABILITY_EXACT_CODE_REVIEW_20260906.md",
  "prompt_packet_sha256": "0a5d7a4442e05be79f366bcb1facddeaff8361c2d6f1160baa321a17f6e502ed",
  "multipart_parts": 8,
  "parts_1_to_7_acknowledged_once": true,
  "final_part_duplicated": true,
  "response_sha256s": [
    "508cc69aed1ec97453b6673b4f4c8722ba901f32b62e0d07043399412ffe65c8",
    "f5aadb8a009f5e741818950cf79dbce35e3f0f968dcb48f0be77922afa1d4fb4"
  ],
  "responses_agree_on_verdict_and_blocker": true,
  "accepted_as_pass_authority_receipt": false,
  "verdict": "REVISE_R3C_BEFORE_PROVIDER_RECOVERY",
  "scientific_equivalence_to_parent_r3": "PASS",
  "external_trust_root_closed": "FAIL",
  "full_forged_chain_closed": "FAIL",
  "direct_bypass_closed": "FAIL",
  "single_use_gate": "PASS",
  "runtime_compatibility": "PASS",
  "provider_recovery_authority_affected": false,
  "r3_contract_redesign_required": false,
  "new_scientific_experiment_required": false,
  "stage_b_authority": false,
  "scientific_authority": false,
  "support_control_verdict": "FAIL_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE",
  "execution_recommendation": "DO_NOT_AUTHORIZE_R3C_RECOVERY",
  "remaining_blockers": [
    "Point-of-use trust-root substitution remains possible because the adjudicator derives the expected Ed25519 public-key path and fingerprint from the caller-supplied contract. Hard-pin the production trust root at point of use and add a substituted-contract plus attacker-key full-chain negative regression."
  ],
  "hard_provider_time_gate": "NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800"
}

```

## R3D contract
```json
{
  "actor": {
    "concurrency": 1,
    "hidden_semantic_or_skeleton_metadata_in_prompt": false,
    "k": 8,
    "legacy_failure_family_metadata": false,
    "max_output_tokens": 8192,
    "max_turns": 10,
    "prefix_ks": [
      1,
      2,
      4,
      8
    ],
    "provider_retry_limit": 0,
    "requested_model": "deepseek-v4-pro",
    "required_resolved_model": "deepseek-v4-pro-ga-260813",
    "temperature": 0,
    "thinking": "disabled"
  },
  "analysis_boundary": {
    "heldout_access": false,
    "partial_learning_effect_read": false,
    "scientific_learning_effect_read": false,
    "stage_a_support_only": true,
    "stage_b_effect_inference": false,
    "support_read_before_terminal_recovery": false
  },
  "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-contract-r3-matched-censor-recovery",
  "authority": {
    "analyzer": false,
    "heldout_evaluation": false,
    "paper_promotion": false,
    "public_benchmark": false,
    "second_backbone": false,
    "stage_a_provider_execution": false,
    "stage_b_learning_execution": false,
    "submission": false,
    "updater": false
  },
  "bound_code": {
    "actor": {
      "path": "scripts/run_e2_r17_semantic_transfer_v3_actor_pool_r3_recovery.py",
      "sha256": "1bffcc3c24e2240a918efa062d8cf6c0262503ce3358ed1265cdbce53736a1f6"
    },
    "authorization_minter": {
      "path": "scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py",
      "sha256": "9866bcffb09b4d6a6f31c5c8e947c6107a8bf35e09b8ddc81a6ef6350d6278df"
    },
    "control_tests": {
      "path": "research_pipeline/test_e2_r17_semantic_transfer_v3_r3_recovery.py",
      "sha256": "17d13bfe6852c9d51cf6be5f91752900c9cd32f54c046f463a563ab4024a4605"
    },
    "equal_dose_adjudicator": {
      "path": "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py",
      "sha256": "b26089a8184db4d1cde5c3fbe02549440d05958af74f405c858749d16d0b13a6"
    },
    "legacy_stream_verifier": {
      "path": "scripts/run_e2_r17_e1_a_pool_support.py",
      "sha256": "24ea070b08399d48af99294615a508874f851af941f5bb0efabe341b0854617d"
    },
    "post_terminal_support_gate": {
      "path": "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py",
      "sha256": "0abd0325414838bc0692caeed7908f5ab4be1d36126c44cca1ed587d2f343752"
    },
    "post_terminal_support_minter": {
      "path": "scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py",
      "sha256": "c8b7490878937114e69e74d428a7ad90aee9eb85488a5890dcaa5eda96e17420"
    },
    "post_terminal_support_tests": {
      "path": "research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py",
      "sha256": "790935b394dc3955f8b6b9cac9b83a96e2d717283fe9973135002c8e1a29c67e"
    },
    "preflight": {
      "path": "scripts/preflight_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py",
      "sha256": "320462d4e0b5033d1c97fb2575b883a377255ac558515018ae2b016caf3d463c"
    },
    "r2_actor_base": {
      "path": "scripts/run_e2_r17_semantic_transfer_v3_actor_pool.py",
      "sha256": "28a21f55c5f641d555eecf66f146fd1414720b19e1a5affbb422a0229a543500"
    },
    "r2_runner_base": {
      "path": "scripts/run_e2_r17_semantic_transfer_v3_stage_a.py",
      "sha256": "267d9dd31e197d6c1d4e7c7bebbbbf0127571a2d209c9e722ebfefbe7c1bcc96"
    },
    "r3b_contract_builder": {
      "path": "scripts/prepare_e2_r17_semantic_transfer_v3_stage_a_r3b_support_guard.py",
      "sha256": "19146c1e3b14d3262185bedc64a491919822fba6a26b6fe2a7d0e6b8eb5631d9"
    },
    "r3b_support_guard_preflight": {
      "path": "scripts/preflight_e2_r17_semantic_transfer_v3_stage_a_r3b_support_guard.py",
      "sha256": "f7b8c18e5f7ee02155252b9739d6f17ab2258227ba9fcb1bbde1e532cd26f606"
    },
    "r3d_contract_builder": {
      "path": "scripts/prepare_e2_r17_semantic_transfer_v3_stage_a_r3d_pinned_support_capability.py",
      "sha256": "b42c8fd9afe30ef7900b44b69b34f151a168b1c309b722f9484a2798ba612317"
    },
    "r3d_external_capability_signer": {
      "path": "scripts/sign_e2_r17_semantic_transfer_v3_stage_a_r3c_support_capability.py",
      "sha256": "aefdf214c92e2fbc6fb3735682de693368bc430dbf0c728a5bfb45b3a9472713"
    },
    "r3d_preflight": {
      "path": "scripts/preflight_e2_r17_semantic_transfer_v3_stage_a_r3d_pinned_support_capability.py",
      "sha256": "488ffd66f749669e38cf535f3a0edeec210635c10583bbd3d392119d8e76d7e9"
    },
    "r3d_signed_capability_verifier": {
      "path": "research_pipeline/e2_r17_r3c_signed_support_capability.py",
      "sha256": "28a32359e0005677da2900470eb3f41c0e847f048582fc12309000629bc5e093"
    },
    "stage_a_runner": {
      "path": "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py",
      "sha256": "491b2ae6e53fcfe732f15ef263cc365ce61846b3219d7a13fe70e3834f6d3c89"
    },
    "stage_b_order_helper": {
      "path": "research_pipeline/e2_r17_semantic_transfer_v3_stage_b_order_r3_recovery.py",
      "sha256": "9593d9abd69ff2198b7958f98f0191a0c886343d20dcdaa4ffe40620f1b793cf"
    }
  },
  "budget": {
    "actor_rollouts": 1264,
    "combined_claim_upper_bound_if_r3_maxed": 12644,
    "failed_r2_pre_io_claims_bound": 4,
    "max_provider_calls": 12640,
    "original_r2_max_provider_calls": 12800,
    "provider_calls_per_rollout_limit": 10
  },
  "control_plane_revision": "R3D_PINNED_EXTERNAL_SIGNED_SUPPORT_CAPABILITY",
  "created_at_utc": "2026-09-06T04:08:08+00:00",
  "env_file_path": "/home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/.env",
  "equal_dose_support": {
    "all_158_provider_pools_must_be_sealed_before_support_read": true,
    "candidate_domain": "mixed K8 pools inside prospectively frozen Stage-B-eligible opportunity set",
    "eligible_opportunity_count_by_stream": {
      "stv3-cgwb-00": 7,
      "stv3-cgwb-01": 8,
      "stv3-cgwp-00": 7,
      "stv3-cgwp-01": 8,
      "stv3-cjlb-00": 8,
      "stv3-cjlb-01": 8,
      "stv3-cjlp-00": 8,
      "stv3-cjlp-01": 8,
      "stv3-clrb-00": 8,
      "stv3-clrb-01": 8,
      "stv3-clrp-00": 8,
      "stv3-clrp-01": 8,
      "stv3-cmpb-00": 8,
      "stv3-cmpb-01": 8,
      "stv3-cmpp-00": 8,
      "stv3-cmpp-01": 8,
      "stv3-csbb-00": 8,
      "stv3-csbb-01": 8,
      "stv3-csbp-00": 8,
      "stv3-csbp-01": 8
    },
    "failure_status": "HOLD_SEMANTIC_TRANSFER_V3_R3_INSUFFICIENT_EQUAL_DOSE_SUPPORT",
    "hash_rank_applied_only_within_candidate_domain": true,
    "required_mixed_pools_per_stream": 4,
    "streams_required": 20,
    "support_read_excludes_burned_and_matched_censor": true,
    "treated_mixed_pools_per_stream": 4,
    "treated_pool_total_if_pass": 80,
    "unmixed_pool_eligible": false
  },
  "exact_once_acquisition": {
    "additional_attempted_but_unsealed_policy": "STOP",
    "ambiguous_recollection_allowed": false,
    "attempt_before_any_provider_io": true,
    "attempt_marker_creation": "O_CREAT|O_EXCL + file fsync before provider I/O",
    "attempt_marker_immutable": true,
    "claim_root": "/data/wyt/e2-r17-search-projection/runs/semantic-transfer-v3-stage-a-r3-matched-censor-20260905/checkpoints/stage_a_task_claims",
    "replacement_sampling_allowed": false,
    "replay_allowed": false,
    "required": true,
    "sealed_receipt_after_frozen_k8_pool": true,
    "terminal_summary_requires_matched_no_provider_censor": 1,
    "terminal_summary_requires_provider_attempted_units": 158,
    "terminal_summary_requires_provider_sealed_units": 158,
    "terminal_summary_requires_terminal_technical_missing": 1,
    "unit_count": 158,
    "unit_manifest_path": "generated/e2-r17-semantic-transfer-v3-stage-a-r3-execution-units-20260905.json",
    "unit_manifest_sha256": "e3ba3eba68523c087f475511e3b639721743fb63ee88e5ccdc5a13e06447ea86"
  },
  "exactly_once": {
    "additional_attempted_but_unsealed_policy": "STOP",
    "authorized_runs": 1,
    "automatic_retry": false,
    "completed_rollout_replay": false,
    "failure_preserves_running_global_lease": true,
    "first_run_only_recovery_runner": true,
    "matched_no_provider_censor_units": 1,
    "provider_execution_units": 158,
    "replacement_sampling": false,
    "terminal_technical_missing_units": 1
  },
  "failed_r2_parent": {
    "completed_streams": 0,
    "global_lease_path": "/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-semantic-transfer-v3-stage-a-r2.json",
    "immutable_files": {
      "burned_attempt": {
        "path": "/data/wyt/e2-r17-search-projection/runs/semantic-transfer-v3-stage-a-r2-20260903/checkpoints/stage_a_task_claims/4d2bb0107f8fadaac6de979d1efcb6b52b4acb00b08b8b3497955c5b92f31d92.attempt.json",
        "sha256": "db658bd5e13995f534987d7703c7f22dd874b96d9bbffcd6cc042295829c0092"
      },
      "failure_receipt": {
        "path": "/data/wyt/e2-r17-search-projection/runs/semantic-transfer-v3-stage-a-r2-20260903/checkpoints/failures/stv3-cgwb-00.json",
        "sha256": "fc7dfd6ba7a95e00aceddc0fdc16699ca4db0bafb91826b826978fa55dfd16af"
      },
      "partial_failure_artifact": {
        "path": "/data/wyt/e2-r17-search-projection/runs/semantic-transfer-v3-stage-a-r2-20260903/cases/r17-b21-cgwb-p0/rollout_0/r17_technical_failure.json",
        "sha256": "cca6c7de70db97c82fc650af00bc3972b1aa568dccbc7ca37eab57323aa4a6b0"
      },
      "provider_budget_ledger": {
        "path": "/data/wyt/e2-r17-search-projection/runs/semantic-transfer-v3-stage-a-r2-20260903/checkpoints/provider_budget.sqlite3",
        "sha256": "1b033c1012ab46a63d0eab3e1e2b8930d054499968d5db5d90761c8b4d5d4a15"
      },
      "r2_global_lease": {
        "path": "/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-semantic-transfer-v3-stage-a-r2.json",
        "sha256": "dc9471b2b9986967c66fa74be17e7bfec3afb30541a57c72847daa0a01c25a2d"
      },
      "r2_local_lock": {
        "path": "/data/wyt/e2-r17-search-projection/runs/semantic-transfer-v3-stage-a-r2-20260903/.exclusive.lock",
        "sha256": "9ce9907141564d200883db7af4a836724ce7dddffe24e8a780da3178a14e42d4"
      }
    },
    "run_root": "/data/wyt/e2-r17-search-projection/runs/semantic-transfer-v3-stage-a-r2-20260903",
    "sealed_k8_pools": 0,
    "support_inspected": false
  },
  "global_lease_path": "/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-semantic-transfer-v3-stage-a-r3-matched-censor.json",
  "mindmemos": {
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "initial_skill_path": "/data/wyt/evidence-substrates/MindMemOS-20260817/resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md",
    "initial_skill_sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb",
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817"
  },
  "model_identity_policy": {
    "fresh_requalification_required_after_exact_hash_r3_review": true,
    "fresh_requalification_required_before_authorization": true,
    "historical_identity_receipts_non_authoritative": true,
    "provider_retry_limit": 0,
    "requested_model": "deepseek-v4-pro",
    "required_resolved_model": "deepseek-v4-pro-ga-260813",
    "thinking": "disabled"
  },
  "next_gate": {
    "after_reset_and_r3d_pass": "EXACTLY_ONE_FRESH_DEEPSEEK_IDENTITY_THEN_LOCAL_ADJUDICATION_THEN_SEPARATE_R3D_RECOVERY_AUTHORIZATION",
    "before_provider_reset": "FRESH_GPT56_SOL_EXTRA_HIGH_R3D_EXACT_CODE_REVIEW_ONLY_NO_PROVIDER_CALL",
    "post_terminal": "MINT_STRUCTURAL_REQUEST_THEN_EXTERNAL_SIGNED_CAPABILITY_THEN_POINT_OF_USE_PIN_VERIFY_AND_CONSUME",
    "provider_recovery": "EXECUTE_ONLY_158_ORIGINAL_PROVIDER_TASKS_UNDER_R3D_CONTRACT",
    "stage_b": "SEPARATE_CONTRACT_REVIEW_AND_AUTHORITY_REQUIRED"
  },
  "parent_r2_contract": {
    "path": "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r2-20260903.json",
    "sha256": "f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234",
    "status": "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A"
  },
  "parent_r3_contract": {
    "path": "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3-recovery-20260905.json",
    "relationship": "control-plane-only successor; scientific geometry, provider task universe, and support estimand unchanged",
    "sha256": "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085",
    "status": "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
  },
  "parent_r3b_contract": {
    "path": "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3b-support-guard-20260905.json",
    "relationship": "control-plane-only successor replacing caller-writable provenance with an externally signed point-of-use capability",
    "sha256": "7454608db38e58f2b39b412045e5a2ffe6f2b26db0d012bb2983e37259cb2da9"
  },
  "parent_r3c_contract": {
    "path": "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3c-signed-support-capability-20260906.json",
    "relationship": "control-plane-only successor hard-pinning production Ed25519 trust root at adjudicator point of use",
    "sha256": "03b2608872424da2bdf78408266a69b28ff565bc9d84bf929aa82ba7bc11e030"
  },
  "post_terminal_support_read_control": {
    "actual_signed_capability_minted": false,
    "actual_support_read_authorization_minted": false,
    "automatic_retry_after_consumption": false,
    "contract_cannot_select_alternate_trust_root": true,
    "control_plane_revision": "R3D_PINNED_EXTERNAL_SIGNED_SUPPORT_CAPABILITY",
    "direct_adjudicator_invocation_without_valid_signed_capability_forbidden": true,
    "external_signed_capability_required": true,
    "gate_origin_is_not_a_trust_anchor": true,
    "heldout_authority": false,
    "paper_claim_authority": false,
    "point_of_use_consumption_in_adjudicator": true,
    "point_of_use_production_trust_root_pinned": true,
    "point_of_use_signature_verification_in_adjudicator": true,
    "production_public_key_path": "generated/e2-r17-r3c-support-signing-public-key-20260906.pem",
    "production_public_key_sha256": "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0",
    "provider_execution_authority": false,
    "required": true,
    "single_use_consumption_required": true,
    "stage_b_authority": false,
    "support_authorization_is_structural_request_only": true,
    "support_read_authority": "stage_a_support_read_only_with_external_signed_capability",
    "support_read_authorization_may_mint_only_after_terminal_recovery": true,
    "terminal_summary_status_required": "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION",
    "trusted_external_signer": {
      "algorithm": "Ed25519",
      "private_key_in_repository": false,
      "private_key_location_class": "external controller only; root-owned on host52",
      "public_key_path": "generated/e2-r17-r3c-support-signing-public-key-20260906.pem",
      "public_key_sha256": "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0",
      "signature_context": "E2-R17-R3D-POST-TERMINAL-SUPPORT-CAPABILITY-V1"
    },
    "updater_authority": false
  },
  "prelearning_baseline_router_policy": {
    "difficulty_only": "ascending successful-rollout RATE over eligible opportunities; SHA256(semantic-transfer-difficulty-v3-r3-rate|stream_id) tie-break; lowest 10 -> MRW4",
    "extra_provider_calls": 0,
    "freeze_before_stage_b_outcomes": true,
    "freeze_only_after_terminal_158_pool_recovery": true,
    "mixedness_only": "descending mixed-pool RATE over eligible opportunities; SHA256(semantic-transfer-mixedness-v3-r3-rate|stream_id) tie-break; highest 10 -> MRW4",
    "raw_count_scoring_forbidden_due_7_7_8_geometry": true
  },
  "provider_route": "https://ark.cn-beijing.volces.com/api/plan/v3",
  "recovery_exceptions": {
    "additional_attempted_but_unsealed_policy": "STOP",
    "additional_matched_censor_allowed": false,
    "burn_receipt": {
      "path": "generated/e2-r17-semantic-transfer-v3-stage-a-r3-burn-receipt-20260905.json",
      "sha256": "7a0628f2a28b4adaf82c81622d94abaaa2e7fc0a93dd88cdb98e6d6ba9f51d04"
    },
    "matched_censor_receipt": {
      "path": "generated/e2-r17-semantic-transfer-v3-stage-a-r3-matched-censor-receipt-20260905.json",
      "sha256": "653fe649dc21e08d056467c6cd0d7008d969d980378811c9adca2107f0104d92"
    },
    "matched_initial_xlsx_sha256": "66e26351d4f79e022d0988a20f8409a0364d0eead932f8c7e6f81698c8a1cd7d",
    "matched_no_provider_censor": "r17-b21-cgwp-p0",
    "pair_key": "semantic-transfer-v3-pair|b21|cross_group_window|p0",
    "replacement_allowed": false,
    "replay_allowed": false,
    "terminal_technical_missing": "r17-b21-cgwb-p0"
  },
  "recovery_execution_manifest": {
    "path": "generated/e2-r17-semantic-transfer-v3-stage-a-r3-execution-units-20260905.json",
    "sha256": "e3ba3eba68523c087f475511e3b639721743fb63ee88e5ccdc5a13e06447ea86",
    "unit_count": 158
  },
  "recovery_opportunity_manifest": {
    "path": "generated/e2-r17-semantic-transfer-v3-stage-a-r3-opportunity-manifest-20260905.json",
    "sha256": "2a63142123afe631e8a919de05c2cbec3be2b2b78c5b46cf3857ee13841d56f9"
  },
  "recovery_reviews": {
    "matched_censor": {
      "path": "generated/e2-r17-v3-r3-matched-censor-gpt56-review-20260905.json",
      "sha256": "160fc58517be215be56a0401d1198e7b6d8727ba4188bd63a04726c51cddfbf4",
      "verdict": "PASS_R3_MATCHED_CENSOR_RECOVERY"
    },
    "one_missing": {
      "path": "generated/e2-r17-v3-stage-a-technical-missing-recovery-gpt56-review-20260905.json",
      "sha256": "1317a1a4d3891150848cb8236e164e2a2012c49b9973c2dd701b449360d64edb",
      "verdict": "PASS_RECOVER_WITH_ONE_TERMINAL_TECHNICAL_MISSING"
    },
    "post_terminal_support_authority": {
      "path": "generated/e2-r17-v3-r3-post-terminal-support-authority-gpt56-review-20260905.json",
      "sha256": "575ab2f4535d994bfd23e2dedcd9effbc26d8d358f5c3b1b3d26411c7f0d6846",
      "verdict": "REQUIRE_SEPARATE_POST_TERMINAL_SUPPORT_READ_AUTHORIZATION"
    },
    "post_terminal_support_control_r1": {
      "path": "generated/e2-r17-v3-r3-support-control-exact-code-gpt56-review-r1-20260905.json",
      "sha256": "48bb7a5d51c99d2ed60fb844423eaa87c455d7f56ce49a1adecaeb9f6373c3e4",
      "verdict": "REVISE_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"
    },
    "post_terminal_support_control_r3b_v2": {
      "path": "generated/e2-r17-v3-r3b-support-control-gpt56-review-v2-20260906.json",
      "sha256": "d89b4abfff996eece666b3e0ad3378982b1f7666ca9a39902fcd2d496b3bc64a",
      "verdict": "REVISE_R3B_BEFORE_PROVIDER_RECOVERY"
    },
    "r3c_point_of_use_review": {
      "path": "generated/e2-r17-v3-r3c-signed-capability-gpt56-review-20260906.json",
      "sha256": "e8b1aab5a0c84e802c1f4b04aaa5af1ca0378acaf5293a22de56d130b47eb402",
      "verdict": "REVISE_R3C_BEFORE_PROVIDER_RECOVERY"
    }
  },
  "review_policy": {
    "fresh_exact_hash_review_after_contract_freeze": true,
    "model": "GPT-5.6 Sol",
    "paper_claim_authority": false,
    "required_execution_recommendation": "ALLOW_SEPARATE_R3_RECOVERY_AUTHORIZATION",
    "required_verdict": "PASS_TO_SEPARATE_R3_RECOVERY_AUTHORIZATION",
    "stage_b_authority": false,
    "surface": "ChatGPT web",
    "thinking_level": "Extra High 4/5"
  },
  "run_root": "/data/wyt/e2-r17-search-projection/runs/semantic-transfer-v3-stage-a-r3-matched-censor-20260905",
  "runtime": {
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt",
    "freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "qualification_path": "generated/e2-r17-runtime-dependency-qualification-r2-20260828.json",
    "qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv"
  },
  "schema_version": "1.0",
  "scientific_role": "R3D control-plane-only successor; parent R3 scientific geometry and provider execution universe unchanged",
  "stage_b_plan_no_authority": {
    "affected_matched_streams": [
      "stv3-cgwb-00",
      "stv3-cgwp-00"
    ],
    "common_heldout_tasks": 20,
    "execution_authority": false,
    "heldout_evaluations": 3200,
    "learned_states": 160,
    "paired_stream_replicate_units": 80,
    "primary_independent_mechanism_units": 5,
    "primary_unit": "matched_skeleton_interaction I_h",
    "replicates_per_stream": 4,
    "treated_pool_total": 80,
    "treated_pools_per_stream": 4,
    "update_pool_count_by_stream": {
      "stv3-cgwb-00": 7,
      "stv3-cgwb-01": 8,
      "stv3-cgwp-00": 7,
      "stv3-cgwp-01": 8,
      "stv3-cjlb-00": 8,
      "stv3-cjlb-01": 8,
      "stv3-cjlp-00": 8,
      "stv3-cjlp-01": 8,
      "stv3-clrb-00": 8,
      "stv3-clrb-01": 8,
      "stv3-clrp-00": 8,
      "stv3-clrp-01": 8,
      "stv3-cmpb-00": 8,
      "stv3-cmpb-01": 8,
      "stv3-cmpp-00": 8,
      "stv3-cmpp-01": 8,
      "stv3-csbb-00": 8,
      "stv3-csbb-01": 8,
      "stv3-csbp-00": 8,
      "stv3-csbp-01": 8
    },
    "update_pool_order": {
      "arm_in_key": false,
      "expected_task_count_is_contract_bound_7_or_8": true,
      "identical_across_win_c_and_mrw4": true,
      "key": "SHA256(semantic-transfer-v3-update-order|stream_id|replicate_index|task_id)",
      "task_id_in_key": true
    }
  },
  "status": "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY",
  "suite": {
    "core_semantic_split_path": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-semantic-transfer-v3/r17_semantic_transfer_v3_split_manifest.json",
    "core_semantic_split_sha256": "815977e908214b66a1106d623ca68f4707d56b117fb01740cadbd1edeab3679e",
    "crossed_skeletons": 5,
    "dataset_sha256": "be84cca6d75359b713a1d6f914c002f7f2be95bcef5f4b745e61908ac7d56b10",
    "generation_runtime": {
      "openpyxl_version": "3.1.5",
      "python_implementation": "CPython",
      "python_version": "3.12.3",
      "zlib_compile_version": "1.3",
      "zlib_runtime_version": "1.3"
    },
    "heldout_tasks_forbidden": 20,
    "metadata_path": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-semantic-transfer-v3/r17_controlled_metadata.json",
    "metadata_sha256": "1cd8fbe40ab84d9db32a6b4877a6aeb3949b4db0772cba04bf9d60ca901b612f",
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-semantic-transfer-v3",
    "semantic_cells_per_skeleton": 2,
    "split_manifest_path": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-semantic-transfer-v3/r17_split_manifest.json",
    "split_manifest_sha256": "a19a57cf1ee71a9af440b56cdf884faeac2ed27990e4fd72e54061be72094fe7",
    "stream_count": 20,
    "streams": [
      "stv3-cgwb-00",
      "stv3-cgwb-01",
      "stv3-cgwp-00",
      "stv3-cgwp-01",
      "stv3-cjlb-00",
      "stv3-cjlb-01",
      "stv3-cjlp-00",
      "stv3-cjlp-01",
      "stv3-clrb-00",
      "stv3-clrb-01",
      "stv3-clrp-00",
      "stv3-clrp-01",
      "stv3-cmpb-00",
      "stv3-cmpb-01",
      "stv3-cmpp-00",
      "stv3-cmpp-01",
      "stv3-csbb-00",
      "stv3-csbb-01",
      "stv3-csbp-00",
      "stv3-csbp-01"
    ],
    "streams_per_semantic_cell": 2,
    "suite_manifest_sha256": "9d57c0abc51758e3657484048e9a132a531ff2758d724b7be5cc6d14ae262338",
    "update_tasks": 160
  }
}

```

## R3D preflight
```json
{
  "artifact_type": "e2-r17-v3-stage-a-r3d-pinned-support-capability-zero-provider-preflight",
  "authority": {
    "heldout": false,
    "paper_claim": false,
    "provider_recovery": false,
    "stage_a_support_read": false,
    "stage_b_execution": false
  },
  "checks": {
    "all_bound_code_hashes_match": true,
    "fresh_r3d_recovery_lineage_absent": true,
    "point_of_use_production_trust_root_pinned": true,
    "provider_recovery_runner_and_authorizer_unchanged": true,
    "signed_capability_absent": true,
    "substituted_contract_attacker_key_full_chain_negative_test_present": true,
    "support_control_tests_10_of_10_pass": true
  },
  "contract_path": "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3d-pinned-support-capability-20260906.json",
  "contract_sha256": "21f7a50f4e14f48a139ecfa122f7c8a443d4195a1ade0267ccececcb6e424717",
  "created_at_utc": "2026-09-06T04:08:26+00:00",
  "fresh_identity_qualified": false,
  "hard_provider_time_gate": "NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800",
  "next_gate": "FRESH_GPT56_SOL_EXTRA_HIGH_R3D_EXACT_CODE_REVIEW_THEN_PROVIDER_RESET_THEN_FRESH_IDENTITY_THEN_SEPARATE_RECOVERY_AUTHORIZATION",
  "parent_r3_contract_sha256": "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085",
  "parent_r3c_contract_sha256": "03b2608872424da2bdf78408266a69b28ff565bc9d84bf929aa82ba7bc11e030",
  "provider_calls": 0,
  "r3c_review_sha256": "e8b1aab5a0c84e802c1f4b04aaa5af1ca0378acaf5293a22de56d130b47eb402",
  "r3d_recovery_authorization_minted": false,
  "schema_version": "1.0",
  "scientific_execution": false,
  "stage_b_authority": false,
  "status": "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_R3D_PINNED_SUPPORT_CAPABILITY_PREFLIGHT",
  "support_inspected": false,
  "trusted_public_key_sha256": "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0",
  "unit_tests": {
    "passed": 10,
    "total": 10
  }
}

```

## A. Adjudicator point-of-use constants + trust check
Whole-file SHA: `b26089a8184db4d1cde5c3fbe02549440d05958af74f405c858749d16d0b13a6`
```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, os, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_r3c_signed_support_capability import (
    CONTROL_PLANE_REVISION,
    HARD_PROVIDER_NOT_BEFORE,
    verify_document,
)
BURNED = "r17-b21-cgwb-p0"
CENSOR = "r17-b21-cgwp-p0"
CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
AUTH_STATUS = "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY"
SUMMARY_STATUS = "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION"
SUPPORT_AUTH_STATUS = "AUTHORIZED_E2_R17_V3_R3_POST_TERMINAL_SUPPORT_READ"
CONTROL_REVIEW_VERDICT = "PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"
CONSUMPTION_NAME = "post_terminal_support_read_authorization.consumed.json"
COMPLETION_NAME = "post_terminal_support_read_adjudication.completed.json"
PRODUCTION_TRUSTED_PUBLIC_KEY_RELATIVE = "generated/e2-r17-r3c-support-signing-public-key-20260906.pem"
PRODUCTION_TRUSTED_PUBLIC_KEY_PATH = ROOT / PRODUCTION_TRUSTED_PUBLIC_KEY_RELATIVE
PRODUCTION_TRUSTED_PUBLIC_KEY_SHA256 = "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def req(c: bool, m: str) -> None:
    if not c: raise RuntimeError(m)

def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    os.replace(tmp,path)


def exclusive_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw=(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode("utf-8")
    fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try:
        os.write(fd,raw); os.fsync(fd)
    finally:
        os.close(fd)
    dfd=os.open(path.parent,os.O_RDONLY)
    try: os.fsync(dfd)
    finally: os.close(dfd)

def bound(raw: str) -> Path:
    p=Path(raw); return p if p.is_absolute() else ROOT/p

def choose_four(stream_id: str, mixed: list[str]) -> list[str]:
    req(len(mixed)>=4,f"insufficient mixed pools: {stream_id}")
    return sorted(mixed,key=lambda t:hashlib.sha256(f"semantic-transfer-mrw4-v3|{stream_id}|{t}".encode()).hexdigest())[:4]

def choose_ten(scores: dict[str,float], *, descending: bool, salt: str) -> list[str]:
    req(len(scores)==20,"router stream universe drift")
    def key(s: str):
        primary=-scores[s] if descending else scores[s]
        return primary,hashlib.sha256(f"{salt}|{s}".encode()).hexdigest()
    return sorted(scores,key=key)[:10]

def failed_witness(rows: list[dict[str,Any]], winner: int) -> dict[str,Any]:
    xs=[r for r in rows if float(r["score"])==0.0 and int(r["rollout_index"])!=winner]
    req(bool(xs),"mixed pool lacks failed nonwinner")
    r=min(xs,key=lambda x:int(x["rollout_index"]))
    return {"rollout_index":int(r["rollout_index"]),"trajectory_path":str(r["trajectory_path"]),"trajectory_sha256":str(r["trajectory_sha256"]),"score":0.0,"selector":"lowest original rollout index among verifier-failure nonwinner trajectories"}


def validate_support_read_gate(*, contract: dict[str,Any], contract_path: Path, recovery_authorization_path: Path, summary_path: Path, support_authorization_path: Path, signed_capability_path: Path, output_path: Path, csha: str, asha: str) -> dict[str,Any]:
    req(contract.get("control_plane_revision")==CONTROL_PLANE_REVISION,"R3C support-control revision absent")
    support_auth=load(support_authorization_path)
    req(support_auth.get("status")==SUPPORT_AUTH_STATUS and support_auth.get("single_use") is True,"R3C support-read authorization invalid")
    req(support_auth.get("authority_requires_external_signed_capability") is True,"R3C support authorization does not require external capability")
    req(support_auth.get("contract_sha256")==csha,"R3C support-read contract SHA drift")
    req(support_auth.get("recovery_authorization_sha256")==asha,"R3C support-read recovery-authorization SHA drift")
    req(support_auth.get("terminal_summary_sha256")==sha(summary_path),"R3C support-read terminal-summary SHA drift")
    req(Path(str(support_auth.get("contract_path") or "")).resolve()==contract_path.resolve(),"R3C support-read contract path drift")
    req(Path(str(support_auth.get("recovery_authorization_path") or "")).resolve()==recovery_authorization_path.resolve(),"R3C support-read recovery-authorization path drift")
    req(Path(str(support_auth.get("terminal_summary_path") or "")).resolve()==summary_path.resolve(),"R3C support-read terminal-summary path drift")
    authority=support_auth.get("authority") or {}
    req(authority.get("stage_a_support_read") is True,"R3C Stage-A support-read authority absent")
    for key in ("stage_a_provider_execution","stage_b_learning_execution","updater","heldout_evaluation","analyzer","second_backbone","public_benchmark","paper_promotion","submission"):
        req(authority.get(key) is False,f"R3C support-read authorization overbroad: {key}")

    control=support_auth.get("bound_control_plane") or {}
    minter_path=Path(str(control.get("minter_path") or "")); gate_path=Path(str(control.get("gate_path") or "")); adjudicator_path=Path(str(control.get("support_adjudicator_path") or ""))
    req(minter_path.is_file() and control.get("minter_sha256")==sha(minter_path),"R3C minter provenance drift")
    req(gate_path.is_file() and control.get("gate_sha256")==sha(gate_path),"R3C gate provenance drift")
    req(adjudicator_path.resolve()==Path(__file__).resolve() and control.get("support_adjudicator_sha256")==sha(Path(__file__)),"R3C guarded adjudicator provenance drift")
    for key,path in (("post_terminal_support_minter",minter_path),("post_terminal_support_gate",gate_path),("equal_dose_adjudicator",Path(__file__))):
        row=(contract.get("bound_code") or {}).get(key) or {}
        req(bound(str(row.get("path") or "")).resolve()==path.resolve() and row.get("sha256")==sha(path),f"R3C contract bound-code drift: {key}")

    review_row=support_auth.get("control_review") or {}; review_path=Path(str(review_row.get("path") or ""))
    req(review_path.is_file() and review_row.get("sha256")==sha(review_path),"R3C control-review receipt binding drift")
    review=load(review_path)
    req(review.get("status")=="COMPLETED" and review.get("surface")=="ChatGPT web" and review.get("model")=="GPT-5.6 Sol","R3C control-review provenance drift")
    req(review.get("verdict")==CONTROL_REVIEW_VERDICT and review_row.get("verdict")==CONTROL_REVIEW_VERDICT,"R3C control-review verdict drift")
    req(review.get("control_plane_revision")==CONTROL_PLANE_REVISION,"R3C control-review revision drift")
    req(review.get("minter_sha256_acknowledged")==control.get("minter_sha256"),"R3C review/minter SHA drift")
    req(review.get("gate_sha256_acknowledged")==control.get("gate_sha256"),"R3C review/gate SHA drift")
    req(review.get("support_adjudicator_sha256_acknowledged")==control.get("support_adjudicator_sha256"),"R3C review/adjudicator SHA drift")
    req(review.get("stage_b_authority") is False and review.get("scientific_authority") is False,"R3C control review grants forbidden authority")

    scope=support_auth.get("execution_scope") or {}
    req(Path(str(scope.get("required_adjudication_output") or "")).resolve()==output_path.resolve(),"R3C support-adjudication output path drift")
    run_root=Path(str(scope.get("required_run_root") or "")); req(run_root.resolve()==Path(contract["run_root"]).resolve(),"R3C support-read run-root drift")

    trusted=((contract.get("post_terminal_support_read_control") or {}).get("trusted_external_signer") or {})
    req(trusted.get("algorithm")=="Ed25519","R3D trusted signer algorithm drift")
    # R3D point-of-use trust root: never derive the sole expected signer from a
    # caller-supplied contract. The production key path and fingerprint are
    # immutable adjudicator constants. A substituted contract may copy these
    # public values but cannot replace them with an attacker-controlled key.
    req(str(trusted.get("public_key_path") or "")==PRODUCTION_TRUSTED_PUBLIC_KEY_RELATIVE,"R3D contract signer path is not production trust root")
    req(str(trusted.get("public_key_sha256") or "")==PRODUCTION_TRUSTED_PUBLIC_KEY_SHA256,"R3D contract signer fingerprint is not production trust root")
    pub_path=PRODUCTION_TRUSTED_PUBLIC_KEY_PATH
    expected_pub_sha=PRODUCTION_TRUSTED_PUBLIC_KEY_SHA256
    req(pub_path.is_file() and sha(pub_path)==expected_pub_sha,"R3D production trusted signer public-key binding drift")
    req(trusted.get("private_key_in_repository") is False,"R3D trusted signer private key must remain external")
    req(signed_capability_path.is_file(),"R3C externally signed support capability absent")
    capability_doc=load(signed_capability_path)
    expected_capability={
        "contract_sha256":csha,
        "recovery_authorization_sha256":asha,
        "terminal_summary_sha256":sha(summary_path),
        "support_authorization_sha256":sha(support_authorization_path),
        "control_review_sha256":sha(review_path),
        "minter_sha256":control.get("minter_sha256"),
        "gate_sha256":control.get("gate_sha256"),
        "support_adjudicator_sha256":control.get("support_adjudicator_sha256"),
        "required_adjudication_output":str(output_path.resolve()),
        "required_run_root":str(run_root.resolve()),
    }
    capability_payload=verify_document(capability_doc,public_key_path=pub_path,expected_public_key_sha256=expected_pub_sha,expected_payload_fields=expected_capability)
    req(bool(str(capability_payload.get("capability_id") or "").strip()),"R3C signed capability id absent")
    return {
        "support_authorization":support_auth,
        "support_authorization_sha256":sha(support_authorization_path),
        "control_review_sha256":sha(review_path),
        "signed_capability_sha256":sha(signed_capability_path),
        "signed_capability_payload":capability_payload,
        "trusted_public_key_sha256":expected_pub_sha,
```

## B. Signed-capability verifier
Whole-file SHA: `28a32359e0005677da2900470eb3f41c0e847f048582fc12309000629bc5e093`
```python
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

CAPABILITY_ARTIFACT_TYPE = "e2-r17-v3-stage-a-r3d-externally-signed-support-read-capability"
SIGNATURE_ALGORITHM = "Ed25519"
SIGNATURE_CONTEXT = "E2-R17-R3D-POST-TERMINAL-SUPPORT-CAPABILITY-V1"
CONTROL_PLANE_REVISION = "R3D_PINNED_EXTERNAL_SIGNED_SUPPORT_CAPABILITY"
HARD_PROVIDER_NOT_BEFORE = "2026-09-07T00:00:00+08:00"
OPENSSL = "/usr/bin/openssl"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_payload_bytes(payload: dict[str, Any]) -> bytes:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return SIGNATURE_CONTEXT.encode("utf-8") + b"\x00" + body


def public_key_fingerprint(path: Path) -> str:
    return sha256_file(path)


def _openssl(args: list[str], *, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    cmd = [OPENSSL, *args]
    result = subprocess.run(cmd, input=input_bytes, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"OpenSSL command failed ({result.returncode}): {' '.join(cmd)}; stderr={result.stderr.decode(errors='replace')[-1200:]}")
    return result


def _derived_public_key(private_key_path: Path) -> bytes:
    return _openssl(["pkey", "-in", str(private_key_path), "-pubout"]).stdout


def sign_document(*, payload: dict[str, Any], private_key_path: Path, public_key_path: Path) -> dict[str, Any]:
    if not private_key_path.is_file() or not public_key_path.is_file():
        raise RuntimeError("R3C signing key material absent")
    if _derived_public_key(private_key_path) != public_key_path.read_bytes():
        raise RuntimeError("R3C private/public signing key mismatch")
    raw = canonical_payload_bytes(payload)
    with tempfile.TemporaryDirectory(prefix="e2-r17-r3c-sign-") as tmp:
        msg = Path(tmp) / "message.bin"
        sig = Path(tmp) / "signature.bin"
        msg.write_bytes(raw)
        _openssl(["pkeyutl", "-sign", "-rawin", "-inkey", str(private_key_path), "-in", str(msg), "-out", str(sig)])
        signature = sig.read_bytes()
    return {
        "schema_version": "1.0",
        "artifact_type": CAPABILITY_ARTIFACT_TYPE,
        "payload": payload,
        "signature": {
            "algorithm": SIGNATURE_ALGORITHM,
            "context": SIGNATURE_CONTEXT,
            "public_key_sha256": public_key_fingerprint(public_key_path),
            "signature_base64": base64.b64encode(signature).decode("ascii"),
        },
    }


def verify_document(
    document: dict[str, Any],
    *,
    public_key_path: Path,
    expected_public_key_sha256: str,
    expected_payload_fields: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if document.get("artifact_type") != CAPABILITY_ARTIFACT_TYPE:
        raise RuntimeError("R3C signed capability artifact type drift")
    payload = document.get("payload")
    signature_row = document.get("signature")
    if not isinstance(payload, dict) or not isinstance(signature_row, dict):
        raise RuntimeError("R3C signed capability payload/signature absent")
    if not public_key_path.is_file():
        raise RuntimeError("R3C trusted signer public key absent")
    actual_public_sha = public_key_fingerprint(public_key_path)
    if actual_public_sha != expected_public_key_sha256:
        raise RuntimeError("R3C trusted signer public-key SHA drift")
    if signature_row.get("algorithm") != SIGNATURE_ALGORITHM or signature_row.get("context") != SIGNATURE_CONTEXT:
        raise RuntimeError("R3C signed capability signature metadata drift")
    if signature_row.get("public_key_sha256") != expected_public_key_sha256:
        raise RuntimeError("R3C signed capability public-key fingerprint drift")
    try:
        signature = base64.b64decode(str(signature_row.get("signature_base64") or ""), validate=True)
    except Exception as exc:
        raise RuntimeError("R3C signed capability signature encoding invalid") from exc
    raw = canonical_payload_bytes(payload)
    with tempfile.TemporaryDirectory(prefix="e2-r17-r3c-verify-") as tmp:
        msg = Path(tmp) / "message.bin"
        sig = Path(tmp) / "signature.bin"
        msg.write_bytes(raw)
        sig.write_bytes(signature)
        result = subprocess.run(
            [OPENSSL, "pkeyutl", "-verify", "-rawin", "-pubin", "-inkey", str(public_key_path), "-in", str(msg), "-sigfile", str(sig)],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError("R3C signed capability signature verification failed")
    if payload.get("control_plane_revision") != CONTROL_PLANE_REVISION:
        raise RuntimeError("R3C signed capability revision drift")
    if payload.get("hard_provider_not_before") != HARD_PROVIDER_NOT_BEFORE:
        raise RuntimeError("R3C signed capability hard provider boundary drift")
    if payload.get("single_use") is not True or payload.get("stage_a_support_read") is not True:
        raise RuntimeError("R3C signed capability support-read/single-use scope invalid")
    for key in (
        "stage_a_provider_execution",
        "stage_b_learning_execution",
        "updater",
        "heldout_evaluation",
        "analyzer",
        "second_backbone",
        "public_benchmark",
        "paper_promotion",
        "submission",
        "scientific_authority",
    ):
        if payload.get(key) is not False:
            raise RuntimeError(f"R3C signed capability overbroad: {key}")
    if expected_payload_fields:
        for key, expected in expected_payload_fields.items():
            if payload.get(key) != expected:
                raise RuntimeError(f"R3C signed capability binding drift: {key}")
    return payload
```

## C. Exact adversarial regression
Whole-file SHA: `790935b394dc3955f8b6b9cac9b83a96e2d717283fe9973135002c8e1a29c67e`
```python
            "--summary",
            str(fixture["summary"]),
            "--output",
            str(fixture["adjudication_output"]),
        ]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--support-authorization", result.stderr)
        self.assertFalse(fixture["adjudication_output"].exists())

    def test_full_forged_review_permit_and_capability_cannot_directly_invoke_adjudicator(self) -> None:
        fixture = self.make_fixture()
        support_auth = self.build_auth(fixture)

        # Construct the verdict-changing adversarial path from the R3B reviewer:
        # a field-complete forged review plus a field-complete forged permit.
        genuine_review = json.loads(fixture["control_review"].read_text())
        forged_review = fixture["root"] / "field-complete-forged-review.json"
        write_json(forged_review, genuine_review)
        support_auth["control_review"]["path"] = str(forged_review.resolve())
        support_auth["control_review"]["sha256"] = sha(forged_review)
        write_json(fixture["support_auth"], support_auth)

        control = support_auth["bound_control_plane"]
        scope = support_auth["execution_scope"]
        payload = {
            "capability_id": "attacker-fabricated-capability",
            "issued_at_utc": "2026-09-07T00:01:00+08:00",
            "control_plane_revision": minter.CONTROL_PLANE_REVISION,
            "hard_provider_not_before": HARD_PROVIDER_NOT_BEFORE,
            "contract_sha256": sha(fixture["contract"]),
            "recovery_authorization_sha256": sha(fixture["recovery_auth"]),
            "terminal_summary_sha256": sha(fixture["summary"]),
            "support_authorization_sha256": sha(fixture["support_auth"]),
            "control_review_sha256": sha(forged_review),
            "minter_sha256": control["minter_sha256"],
            "gate_sha256": control["gate_sha256"],
            "support_adjudicator_sha256": control["support_adjudicator_sha256"],
            "required_adjudication_output": str(fixture["adjudication_output"].resolve()),
            "required_run_root": str(Path(scope["required_run_root"]).resolve()),
            "single_use": True,
            "stage_a_support_read": True,
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "updater": False,
            "heldout_evaluation": False,
            "analyzer": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
            "submission": False,
            "scientific_authority": False,
        }
        # The fixture contract itself is a fully substituted attacker contract:
        # its trusted signer is the fixture-local keypair, and every dependent
        # contract/auth/summary/permit hash was built consistently from it. Sign
        # with that matching attacker private key. R3D must reject this chain at
        # the adjudicator's immutable production trust-root pin, before consume.
        forged_capability = sign_document(
            payload=payload,
            private_key_path=fixture["private_key"],
            public_key_path=fixture["public_key"],
        )
        write_json(fixture["signed_capability"], forged_capability)

        command = [
            sys.executable,
            str(minter.EXPECTED_SUPPORT_ADJUDICATOR),
            "--contract", str(fixture["contract"]),
            "--authorization", str(fixture["recovery_auth"]),
            "--summary", str(fixture["summary"]),
            "--support-authorization", str(fixture["support_auth"]),
            "--signed-capability", str(fixture["signed_capability"]),
            "--output", str(fixture["adjudication_output"]),
        ]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("production trust root", result.stderr)
        self.assertFalse(fixture["adjudication_output"].exists())
        consumption = fixture["run"] / "checkpoints/post_terminal_support_read" / gate.CONSUMPTION_NAME
        self.assertFalse(consumption.exists())

    def test_gate_consumes_once_and_fail_closes_on_unexpected_adjudicator_error(self) -> None:
        fixture = self.make_fixture()
        self.build_auth(fixture)
        self.build_signed_capability(fixture)
```

## D. Required audit
A. Is the production Ed25519 trust root now independently pinned at adjudicator point of use, rather than selected by the supplied contract?
B. Can a substituted contract + attacker keypair + fully consistent dependent chain still reach semantic inspection/consumption?
C. Does a caller with the genuine signed capability have legitimate authority even when directly invoking the adjudicator, so wrapper origin is no longer a security assumption?
D. Is single-use consume-before-semantics still preserved?
E. Is the full forged-chain negative regression sufficient and run under the frozen scientific runtime?
F. Did R3D change any R3 scientific geometry/provider runner/authorizer?
G. Confirm no provider/Stage-B/scientific authority is granted and the Sep-7 time gate remains.
H. If PASS, is the only next consequence: after provider reset, one fresh identity qualification and then a separate R3D recovery-authorization decision?

## Required synthesis
Return exactly these fields:
- `contract_sha256_acknowledged`
- `preflight_sha256_acknowledged`
- `control_plane_revision`
- `production_public_key_sha256_acknowledged`
- `support_adjudicator_sha256_acknowledged`
- `capability_verifier_sha256_acknowledged`
- `tests_sha256_acknowledged`
- `scientific_equivalence_to_parent_r3`: PASS/FAIL
- `point_of_use_trust_root_closed`: PASS/FAIL
- `substituted_contract_attack_closed`: PASS/FAIL
- `direct_bypass_closed`: PASS/FAIL
- `single_use_gate`: PASS/FAIL
- `runtime_compatibility`: PASS/FAIL
- `tests_preflight`: PASS/FAIL
- `provider_recovery_authority_affected`: true/false
- `r3_contract_redesign_required`: true/false
- `new_scientific_experiment_required`: true/false
- `stage_b_authority`: false
- `scientific_authority`: false
- `support_control_verdict`: `PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE` or `FAIL_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE`
- `execution_recommendation`: `ALLOW_SEPARATE_R3D_RECOVERY_AUTHORIZATION_AFTER_RESET_AND_FRESH_IDENTITY` or `DO_NOT_AUTHORIZE_R3D_RECOVERY`
- `remaining_blockers`: [] or exact blockers

End with exactly one token: `PASS_TO_SEPARATE_R3_RECOVERY_AUTHORIZATION`, `REVISE_R3D_BEFORE_PROVIDER_RECOVERY`, or `STOP_R3_RECOVERY`.
