# E2-R17 V3 Stage-A R3B support-guard exact-hash preexecution review

Date: 2026-09-05
Role: fresh independent senior ICLR/NeurIPS/ICML agent-systems methodology/control-plane reviewer
Scope: exact-code + exact-contract ZERO-PROVIDER preexecution review

## 0. Review rule

A prior exact-code review correctly returned `REVISE_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE` because (1) the support adjudicator remained directly invocable without the support-read permit/gate, and (2) the gate did not end-to-end validate reviewed minter/control-review provenance.

R3B is a versioned control-plane-only successor intended to close exactly those two blockers. Do not infer any Stage-A support, Stage-B effect, or paper outcome. No R3/R3B provider recovery has started; the run root and lease remain absent; no fresh post-review identity exists; no recovery authorization exists; no support-read permit exists.

Do not reopen the already-passed matched-censor scientific geometry, no-replay rule, 158-task universe, K=8, 7/7/8 opportunity geometry, >=4 mixed-pool support threshold, or workload unless R3B changed one of those objects.

Provider hard time gate remains: `NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800`.

For the final provider-recovery verdict, end with exactly one token:
- `PASS_TO_SEPARATE_R3_RECOVERY_AUTHORIZATION`
- `REVISE_R3B_BEFORE_PROVIDER_RECOVERY`
- `STOP_R3_RECOVERY`

Also return a separate synthesis field `support_control_verdict` equal to exactly `PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE` or `FAIL_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE`.

## 1. Exact frozen objects

Parent R3 contract SHA256: `3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085`
R3B contract: `generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3b-support-guard-20260905.json`
R3B contract SHA256: `7454608db38e58f2b39b412045e5a2ffe6f2b26db0d012bb2983e37259cb2da9`
Recovery preflight SHA256: `33033d8b35b200d2ca08480776d94cfa959895c9453e92d99ecf7b78e2219bd3`
R3B support-guard preflight SHA256: `94043973e6b89edf0e0132e8c503854063ab3ea32801ccc2766359554264084f`
Prior authority-review receipt SHA256: `575ab2f4535d994bfd23e2dedcd9effbc26d8d358f5c3b1b3d26411c7f0d6846`
R1 exact-code REVISE receipt SHA256: `48bb7a5d51c99d2ed60fb844423eaa87c455d7f56ce49a1adecaeb9f6373c3e4`

Unchanged provider recovery runner SHA256: `491b2ae6e53fcfe732f15ef263cc365ce61846b3219d7a13fe70e3834f6d3c89`
Unchanged recovery authorizer SHA256: `9866bcffb09b4d6a6f31c5c8e947c6107a8bf35e09b8ddc81a6ef6350d6278df`

R3B control-plane revision: `R3B_POST_TERMINAL_SUPPORT_GUARD`.

### Parent/child scientific-field equality

```json
{
  "actor": true,
  "analysis_boundary": true,
  "authority": true,
  "budget": true,
  "env_file_path": true,
  "equal_dose_support": true,
  "exact_once_acquisition": true,
  "failed_r2_parent": true,
  "global_lease_path": true,
  "mindmemos": true,
  "model_identity_policy": true,
  "provider_route": true,
  "recovery_exceptions": true,
  "recovery_opportunity_manifest": true,
  "run_root": true,
  "runtime": true,
  "stage_b_plan_no_authority": true,
  "suite": true
}
```

Every listed field must be true. The intended R3B differences are only: parent linkage, control-plane revision/provenance, guarded adjudicator hash, additive minter/gate/tests/preflight/builder bindings, and post-terminal authority semantics.

## 2. R3B contract

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
      "sha256": "d8ad232562b5f88f7394555c158d83b7e00dd235f2ef8631c89a3cabe6b896eb"
    },
    "legacy_stream_verifier": {
      "path": "scripts/run_e2_r17_e1_a_pool_support.py",
      "sha256": "24ea070b08399d48af99294615a508874f851af941f5bb0efabe341b0854617d"
    },
    "post_terminal_support_gate": {
      "path": "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py",
      "sha256": "333c3ef89746c4d7e44b20769e068b0520140dffb4fa79f32da1f9e981cefb10"
    },
    "post_terminal_support_minter": {
      "path": "scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py",
      "sha256": "0e7bf96b3e6274de8c6e5738b46924990de8b8897c04bb3871fce0e5fdd06d43"
    },
    "post_terminal_support_tests": {
      "path": "research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py",
      "sha256": "7a9c51fc7a24df34469efa71a6e2301e6aeab182d110e23cd460a646ecc002db"
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
  "control_plane_revision": "R3B_POST_TERMINAL_SUPPORT_GUARD",
  "created_at_utc": "2026-09-05T14:55:31+00:00",
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
    "after_reset_and_exact_hash_pass": "EXACTLY_ONE_FRESH_DEEPSEEK_IDENTITY_THEN_LOCAL_ADJUDICATION_THEN_SEPARATE_R3B_RECOVERY_AUTHORIZATION",
    "before_provider_reset": "FRESH_GPT56_SOL_EXTRA_HIGH_R3B_EXACT_HASH_PREEXECUTION_REVIEW_ONLY_NO_PROVIDER_CALL",
    "post_terminal": "MINT_SINGLE_USE_SUPPORT_READ_AUTHORIZATION_THEN_CONSUME_THROUGH_GUARDED_ONE_SHOT_GATE",
    "provider_recovery": "EXECUTE_ONLY_158_ORIGINAL_PROVIDER_TASKS_UNDER_R3B_CONTRACT",
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
  "post_terminal_support_read_control": {
    "actual_support_read_authorization_minted": false,
    "automatic_retry_after_consumption": false,
    "control_plane_revision": "R3B_POST_TERMINAL_SUPPORT_GUARD",
    "direct_adjudicator_invocation_forbidden": true,
    "exact_code_review_required_before_provider_recovery": true,
    "heldout_authority": false,
    "paper_claim_authority": false,
    "provider_execution_authority": false,
    "required": true,
    "single_use_consumption_required": true,
    "stage_b_authority": false,
    "support_adjudicator_requires_gate_consumption_marker": true,
    "support_adjudicator_requires_support_authorization": true,
    "support_read_authority": "stage_a_support_read_only",
    "support_read_authorization_may_mint_only_after_terminal_recovery": true,
    "terminal_summary_status_required": "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION",
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
  "scientific_role": "versioned fail-closed Stage-A R3 matched-censor recovery with R3B post-terminal support-read authority guard; scientific recovery geometry and support semantics unchanged from parent R3",
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

## 3. Recovery preflight on R3B contract

```json
{
  "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-r3-recovery-zero-provider-preflight",
  "authority": {
    "mint_recovery_authorization": false,
    "stage_a_provider_execution": false,
    "stage_b_learning_execution": false,
    "support_read": false
  },
  "checks": {
    "actor_compile_pass": true,
    "actor_scope_guards_pass": true,
    "adjudicator_compile_pass": true,
    "authorizer_compile_pass": true,
    "matched_censor_binding_pass": true,
    "opportunity_geometry_pass": true,
    "parent_incident_binding_pass": true,
    "provider_manifest_pass": true,
    "runner_compile_pass": true,
    "stage_b_order_7_8_pass": true,
    "stage_b_order_compile_pass": true
  },
  "contract_path": "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3b-support-guard-20260905.json",
  "contract_sha256": "7454608db38e58f2b39b412045e5a2ffe6f2b26db0d012bb2983e37259cb2da9",
  "created_at_utc": "2026-09-05T14:55:31+00:00",
  "fresh_identity_qualified": false,
  "fresh_identity_required_after_exact_hash_review": true,
  "heldout_forbidden_count": 20,
  "matched_no_provider_censor_count": 1,
  "next_gate": "FRESH_GPT56_SOL_EXTRA_HIGH_EXACT_HASH_R3_PREEXECUTION_REVIEW_THEN_FRESH_IDENTITY_THEN_SEPARATE_RECOVERY_AUTHORIZATION",
  "planned_task_count": 160,
  "provider_calls": 0,
  "provider_execution_task_count": 158,
  "schema_version": "1.0",
  "scientific_execution": false,
  "status": "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY_PREFLIGHT",
  "support_inspected": false,
  "terminal_technical_missing_count": 1
}
```

## 4. R3B support-guard preflight

```json
{
  "actual_support_read_authorization_minted": false,
  "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-r3b-support-guard-zero-provider-preflight",
  "authority": {
    "heldout": false,
    "paper_claim": false,
    "provider_recovery": false,
    "stage_a_support_read": false,
    "stage_b_execution": false
  },
  "authority_review_path": "generated/e2-r17-v3-r3-post-terminal-support-authority-gpt56-review-20260905.json",
  "authority_review_sha256": "575ab2f4535d994bfd23e2dedcd9effbc26d8d358f5c3b1b3d26411c7f0d6846",
  "checks": {
    "all_bound_code_hashes_match": true,
    "fresh_r3b_lineage_absent": true,
    "post_terminal_support_control_bound": true,
    "provider_recovery_runner_unchanged": true,
    "support_control_compile_pass": true,
    "support_control_tests_9_of_9_pass": true,
    "support_read_artifacts_absent": true
  },
  "contract_path": "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3b-support-guard-20260905.json",
  "contract_sha256": "7454608db38e58f2b39b412045e5a2ffe6f2b26db0d012bb2983e37259cb2da9",
  "created_at_utc": "2026-09-05T14:55:32+00:00",
  "fresh_identity_qualified": false,
  "next_gate": "FRESH_GPT56_SOL_EXTRA_HIGH_R3B_EXACT_HASH_PREEXECUTION_REVIEW_THEN_PROVIDER_RESET_THEN_FRESH_IDENTITY_THEN_SEPARATE_RECOVERY_AUTHORIZATION",
  "parent_r3_contract_path": "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3-recovery-20260905.json",
  "parent_r3_contract_sha256": "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085",
  "provider_calls": 0,
  "r1_exact_code_review_path": "generated/e2-r17-v3-r3-support-control-exact-code-gpt56-review-r1-20260905.json",
  "r1_exact_code_review_sha256": "48bb7a5d51c99d2ed60fb844423eaa87c455d7f56ce49a1adecaeb9f6373c3e4",
  "r3b_recovery_authorization_minted": false,
  "schema_version": "1.0",
  "science_keys_equal_parent": [
    "failed_r2_parent",
    "suite",
    "mindmemos",
    "provider_route",
    "model_identity_policy",
    "recovery_exceptions",
    "recovery_opportunity_manifest",
    "exact_once_acquisition",
    "equal_dose_support",
    "actor",
    "budget",
    "analysis_boundary",
    "stage_b_plan_no_authority",
    "runtime",
    "env_file_path",
    "run_root",
    "global_lease_path"
  ],
  "scientific_execution": false,
  "stage_b_authority": false,
  "status": "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_R3B_SUPPORT_GUARD_PREFLIGHT",
  "support_inspected": false,
  "unit_tests": {
    "passed": 9,
    "suite": "research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control",
    "total": 9
  }
}
```

## 5. Blocker-specific repair summary

### R1 blocker 1: direct adjudicator bypass

R3B modifies only the support adjudicator's authority interface before its existing support computation begins:

- `--support-authorization` is now required;
- `--consumption-marker` is now required;
- both must bind exact contract, recovery auth, terminal summary, reviewed minter/gate/adjudicator hashes, control-review receipt, canonical run root and required output;
- the consumption marker must be the canonical O_EXCL marker created under `run_root/checkpoints/post_terminal_support_read/`;
- old direct invocation with contract + recovery authorization + summary + output alone fails at argparse before any pool semantics can be read.

The support algorithm from opportunity-manifest loading through mixed-pool/support computation is unchanged; only guard validation is inserted before it, and provenance fields are appended to the output.

### R1 blocker 2: permit-shaped JSON / review provenance bypass

The gate now reloads the embedded control-review receipt and validates its SHA, model/surface, exact PASS verdict, R3B revision, exact minter/gate/adjudicator SHA acknowledgements, and forbidden-authority flags. The guarded adjudicator independently repeats these provenance checks before reading K8 semantics.

The gate creates an O_CREAT|O_EXCL durable consumption marker before invoking the adjudicator and passes both support authorization and marker explicitly. The marker binds support-auth SHA, summary SHA, required output, exact gate SHA and control-review SHA. Unexpected adjudicator rc leaves the permit consumed and no automatic retry is permitted.

### Regression tests

9/9 zero-provider tests PASS, including the two new verdict-changing cases:
- guarded adjudicator rejects old direct invocation without support permit/consumption marker;
- gate rejects a permit whose control-review provenance was forged/incomplete.

## 6. Exact authority-interface diff versus R1 frozen adjudicator

```diff
--- /tmp/tmp1m5gjodr	2026-09-05 22:56:59.639456223 +0800
+++ /tmp/tmpdiu0h8c6	2026-09-05 22:56:59.639456223 +0800
@@ -12,6 +12,10 @@
 CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
 AUTH_STATUS = "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY"
 SUMMARY_STATUS = "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION"
+SUPPORT_AUTH_STATUS = "AUTHORIZED_E2_R17_V3_R3_POST_TERMINAL_SUPPORT_READ"
+CONTROL_REVIEW_VERDICT = "PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"
+CONTROL_PLANE_REVISION = "R3B_POST_TERMINAL_SUPPORT_GUARD"
+CONSUMPTION_NAME = "post_terminal_support_read_authorization.consumed.json"


 def sha(path: Path) -> str:
@@ -50,11 +54,64 @@
     return {"rollout_index":int(r["rollout_index"]),"trajectory_path":str(r["trajectory_path"]),"trajectory_sha256":str(r["trajectory_sha256"]),"score":0.0,"selector":"lowest original rollout index among verifier-failure nonwinner trajectories"}


+def validate_support_read_gate(*, contract: dict[str,Any], contract_path: Path, recovery_authorization_path: Path, summary_path: Path, support_authorization_path: Path, consumption_marker_path: Path, output_path: Path, csha: str, asha: str) -> dict[str,Any]:
+    req(contract.get("control_plane_revision")==CONTROL_PLANE_REVISION,"R3B support-control revision absent")
+    support_auth=load(support_authorization_path)
+    req(support_auth.get("status")==SUPPORT_AUTH_STATUS and support_auth.get("single_use") is True,"R3B support-read authorization invalid")
+    req(support_auth.get("contract_sha256")==csha,"R3B support-read contract SHA drift")
+    req(support_auth.get("recovery_authorization_sha256")==asha,"R3B support-read recovery-authorization SHA drift")
+    req(support_auth.get("terminal_summary_sha256")==sha(summary_path),"R3B support-read terminal-summary SHA drift")
+    req(Path(str(support_auth.get("contract_path") or "")).resolve()==contract_path.resolve(),"R3B support-read contract path drift")
+    req(Path(str(support_auth.get("recovery_authorization_path") or "")).resolve()==recovery_authorization_path.resolve(),"R3B support-read recovery-authorization path drift")
+    req(Path(str(support_auth.get("terminal_summary_path") or "")).resolve()==summary_path.resolve(),"R3B support-read terminal-summary path drift")
+    authority=support_auth.get("authority") or {}
+    req(authority.get("stage_a_support_read") is True,"R3B Stage-A support-read authority absent")
+    for key in ("stage_a_provider_execution","stage_b_learning_execution","updater","heldout_evaluation","analyzer","second_backbone","public_benchmark","paper_promotion","submission"):
+        req(authority.get(key) is False,f"R3B support-read authorization overbroad: {key}")
+
+    control=support_auth.get("bound_control_plane") or {}
+    minter_path=Path(str(control.get("minter_path") or "")); gate_path=Path(str(control.get("gate_path") or "")); adjudicator_path=Path(str(control.get("support_adjudicator_path") or ""))
+    req(minter_path.is_file() and control.get("minter_sha256")==sha(minter_path),"R3B minter provenance drift")
+    req(gate_path.is_file() and control.get("gate_sha256")==sha(gate_path),"R3B gate provenance drift")
+    req(adjudicator_path.resolve()==Path(__file__).resolve() and control.get("support_adjudicator_sha256")==sha(Path(__file__)),"R3B guarded adjudicator provenance drift")
+    for key,path in (("post_terminal_support_minter",minter_path),("post_terminal_support_gate",gate_path),("equal_dose_adjudicator",Path(__file__))):
+        row=(contract.get("bound_code") or {}).get(key) or {}
+        req(bound(str(row.get("path") or "")).resolve()==path.resolve() and row.get("sha256")==sha(path),f"R3B contract bound-code drift: {key}")
+
+    review_row=support_auth.get("control_review") or {}; review_path=Path(str(review_row.get("path") or ""))
+    req(review_path.is_file() and review_row.get("sha256")==sha(review_path),"R3B control-review receipt binding drift")
+    review=load(review_path)
+    req(review.get("status")=="COMPLETED" and review.get("surface")=="ChatGPT web" and review.get("model")=="GPT-5.6 Sol","R3B control-review provenance drift")
+    req(review.get("verdict")==CONTROL_REVIEW_VERDICT and review_row.get("verdict")==CONTROL_REVIEW_VERDICT,"R3B control-review verdict drift")
+    req(review.get("control_plane_revision")==CONTROL_PLANE_REVISION,"R3B control-review revision drift")
+    req(review.get("minter_sha256_acknowledged")==control.get("minter_sha256"),"R3B review/minter SHA drift")
+    req(review.get("gate_sha256_acknowledged")==control.get("gate_sha256"),"R3B review/gate SHA drift")
+    req(review.get("support_adjudicator_sha256_acknowledged")==control.get("support_adjudicator_sha256"),"R3B review/adjudicator SHA drift")
+    req(review.get("stage_b_authority") is False and review.get("scientific_authority") is False,"R3B control review grants forbidden authority")
+
+    scope=support_auth.get("execution_scope") or {}
+    req(Path(str(scope.get("required_adjudication_output") or "")).resolve()==output_path.resolve(),"R3B support-adjudication output path drift")
+    run_root=Path(str(scope.get("required_run_root") or "")); req(run_root.resolve()==Path(contract["run_root"]).resolve(),"R3B support-read run-root drift")
+    expected_marker=run_root/"checkpoints/post_terminal_support_read"/CONSUMPTION_NAME
+    req(consumption_marker_path.resolve()==expected_marker.resolve() and consumption_marker_path.is_file(),"R3B gate consumption marker absent/path drift")
+    marker=load(consumption_marker_path)
+    req(marker.get("artifact_type")=="e2-r17-v3-stage-a-r3-post-terminal-support-read-consumption" and marker.get("status")=="CONSUMED_IN_FLIGHT_DO_NOT_RETRY","R3B gate consumption marker status drift")
+    req(marker.get("support_authorization_sha256")==sha(support_authorization_path),"R3B gate consumption support-auth SHA drift")
+    req(marker.get("terminal_summary_sha256")==sha(summary_path),"R3B gate consumption summary SHA drift")
+    req(Path(str(marker.get("required_output") or "")).resolve()==output_path.resolve(),"R3B gate consumption output drift")
+    req(marker.get("gate_sha256")==sha(gate_path),"R3B gate consumption gate SHA drift")
+    req(marker.get("control_review_sha256")==sha(review_path),"R3B gate consumption review SHA drift")
+    req(marker.get("stage_b_authority") is False,"R3B gate consumption grants Stage-B authority")
+    return {"support_authorization":support_auth,"support_authorization_sha256":sha(support_authorization_path),"consumption_marker_sha256":sha(consumption_marker_path),"control_review_sha256":sha(review_path)}
+
+
 def main() -> int:
     ap=argparse.ArgumentParser()
     ap.add_argument("--contract",type=Path,required=True)
     ap.add_argument("--authorization",type=Path,required=True)
     ap.add_argument("--summary",type=Path,required=True)
+    ap.add_argument("--support-authorization",type=Path,required=True)
+    ap.add_argument("--consumption-marker",type=Path,required=True)
     ap.add_argument("--output",type=Path,required=True)
     a=ap.parse_args(); req(not a.output.exists(),"R3 support adjudication already exists")
     c,auth,s=load(a.contract),load(a.authorization),load(a.summary)
@@ -65,6 +122,7 @@
     req(s["planned_tasks"]==160 and s["provider_executable_tasks"]==158 and s["sealed_k8_pools"]==158,"R3 terminal accounting drift")
     req(s["terminal_technical_missing"]==1 and s["matched_no_provider_censor"]==1,"R3 exception accounting drift")
     req(s["support_inspected"] is False and s["updater_calls"]==0 and s["heldout_evaluations"]==0,"R3 crossed support/learning boundary")
+    guard=validate_support_read_gate(contract=c,contract_path=a.contract,recovery_authorization_path=a.authorization,summary_path=a.summary,support_authorization_path=a.support_authorization,consumption_marker_path=a.consumption_marker,output_path=a.output,csha=csha,asha=asha)

     om=c["recovery_opportunity_manifest"]; opath=bound(om["path"])
     req(opath.is_file() and sha(opath)==om["sha256"],"R3 opportunity manifest drift")
@@ -127,7 +185,7 @@
     status="PASS_SEMANTIC_TRANSFER_V3_R3_MATCHED_CENSOR_EQUAL_DOSE_SUPPORT_READY_FOR_STAGE_B_DESIGN" if passed else "HOLD_SEMANTIC_TRANSFER_V3_R3_INSUFFICIENT_EQUAL_DOSE_SUPPORT"
     out={
         "schema_version":"1.0","artifact_type":"e2-r17-v3-stage-a-r3-matched-censor-equal-dose-adjudication","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":status,
-        "contract_path":str(a.contract),"contract_sha256":csha,"authorization_path":str(a.authorization),"authorization_sha256":asha,"summary_path":str(a.summary),"summary_sha256":sha(a.summary),
+        "contract_path":str(a.contract),"contract_sha256":csha,"authorization_path":str(a.authorization),"authorization_sha256":asha,"summary_path":str(a.summary),"summary_sha256":sha(a.summary),"support_authorization_path":str(a.support_authorization),"support_authorization_sha256":guard["support_authorization_sha256"],"consumption_marker_path":str(a.consumption_marker),"consumption_marker_sha256":guard["consumption_marker_sha256"],"control_review_sha256":guard["control_review_sha256"],
         "integrity":{"planned_tasks":160,"sealed_k8_pools":158,"terminal_technical_missing":BURNED,"matched_no_provider_censor":CENSOR,"provider_executable_tasks":158,"heldout_tasks_touched":0,"updater_calls":0,"heldout_evaluations":0,"partial_effect_read":False},
         "support":{"required_mixed_pools_per_stream":4,"eligible_opportunities_per_stream":opp,"mixed_pools_per_stream":mixed_by,"failing_streams":failing,"pass":passed},
         "stage_b_eligible_pool_geometry":{"task_ids_by_stream":streams,"opportunity_count_by_stream":opp,"affected_exact_matched_streams":["stv3-cgwb-00","stv3-cgwp-00"],"within_stream_arm_pool_ids_must_be_identical":True},

```

## 7. Exact code hashes

- GUARDED_SUPPORT_ADJUDICATOR: `scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py` SHA256 `d8ad232562b5f88f7394555c158d83b7e00dd235f2ef8631c89a3cabe6b896eb`
- SUPPORT_READ_MINTER: `scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py` SHA256 `0e7bf96b3e6274de8c6e5738b46924990de8b8897c04bb3871fce0e5fdd06d43`
- ONE_SHOT_GATE: `scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py` SHA256 `333c3ef89746c4d7e44b20769e068b0520140dffb4fa79f32da1f9e981cefb10`
- CONTROL_TESTS: `research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py` SHA256 `7a9c51fc7a24df34469efa71a6e2301e6aeab182d110e23cd460a646ecc002db`
- R3B_PREFLIGHT: `scripts/preflight_e2_r17_semantic_transfer_v3_stage_a_r3b_support_guard.py` SHA256 `f7b8c18e5f7ee02155252b9739d6f17ab2258227ba9fcb1bbde1e532cd26f606`
- R3B_BUILDER: `scripts/prepare_e2_r17_semantic_transfer_v3_stage_a_r3b_support_guard.py` SHA256 `19146c1e3b14d3262185bedc64a491919822fba6a26b6fe2a7d0e6b8eb5631d9`
- UNCHANGED_RECOVERY_AUTHORIZER: `scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py` SHA256 `9866bcffb09b4d6a6f31c5c8e947c6107a8bf35e09b8ddc81a6ef6350d6278df`

## Source: GUARDED_SUPPORT_ADJUDICATOR — `scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BURNED = "r17-b21-cgwb-p0"
CENSOR = "r17-b21-cgwp-p0"
CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
AUTH_STATUS = "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY"
SUMMARY_STATUS = "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION"
SUPPORT_AUTH_STATUS = "AUTHORIZED_E2_R17_V3_R3_POST_TERMINAL_SUPPORT_READ"
CONTROL_REVIEW_VERDICT = "PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"
CONTROL_PLANE_REVISION = "R3B_POST_TERMINAL_SUPPORT_GUARD"
CONSUMPTION_NAME = "post_terminal_support_read_authorization.consumed.json"


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


def validate_support_read_gate(*, contract: dict[str,Any], contract_path: Path, recovery_authorization_path: Path, summary_path: Path, support_authorization_path: Path, consumption_marker_path: Path, output_path: Path, csha: str, asha: str) -> dict[str,Any]:
    req(contract.get("control_plane_revision")==CONTROL_PLANE_REVISION,"R3B support-control revision absent")
    support_auth=load(support_authorization_path)
    req(support_auth.get("status")==SUPPORT_AUTH_STATUS and support_auth.get("single_use") is True,"R3B support-read authorization invalid")
    req(support_auth.get("contract_sha256")==csha,"R3B support-read contract SHA drift")
    req(support_auth.get("recovery_authorization_sha256")==asha,"R3B support-read recovery-authorization SHA drift")
    req(support_auth.get("terminal_summary_sha256")==sha(summary_path),"R3B support-read terminal-summary SHA drift")
    req(Path(str(support_auth.get("contract_path") or "")).resolve()==contract_path.resolve(),"R3B support-read contract path drift")
    req(Path(str(support_auth.get("recovery_authorization_path") or "")).resolve()==recovery_authorization_path.resolve(),"R3B support-read recovery-authorization path drift")
    req(Path(str(support_auth.get("terminal_summary_path") or "")).resolve()==summary_path.resolve(),"R3B support-read terminal-summary path drift")
    authority=support_auth.get("authority") or {}
    req(authority.get("stage_a_support_read") is True,"R3B Stage-A support-read authority absent")
    for key in ("stage_a_provider_execution","stage_b_learning_execution","updater","heldout_evaluation","analyzer","second_backbone","public_benchmark","paper_promotion","submission"):
        req(authority.get(key) is False,f"R3B support-read authorization overbroad: {key}")

    control=support_auth.get("bound_control_plane") or {}
    minter_path=Path(str(control.get("minter_path") or "")); gate_path=Path(str(control.get("gate_path") or "")); adjudicator_path=Path(str(control.get("support_adjudicator_path") or ""))
    req(minter_path.is_file() and control.get("minter_sha256")==sha(minter_path),"R3B minter provenance drift")
    req(gate_path.is_file() and control.get("gate_sha256")==sha(gate_path),"R3B gate provenance drift")
    req(adjudicator_path.resolve()==Path(__file__).resolve() and control.get("support_adjudicator_sha256")==sha(Path(__file__)),"R3B guarded adjudicator provenance drift")
    for key,path in (("post_terminal_support_minter",minter_path),("post_terminal_support_gate",gate_path),("equal_dose_adjudicator",Path(__file__))):
        row=(contract.get("bound_code") or {}).get(key) or {}
        req(bound(str(row.get("path") or "")).resolve()==path.resolve() and row.get("sha256")==sha(path),f"R3B contract bound-code drift: {key}")

    review_row=support_auth.get("control_review") or {}; review_path=Path(str(review_row.get("path") or ""))
    req(review_path.is_file() and review_row.get("sha256")==sha(review_path),"R3B control-review receipt binding drift")
    review=load(review_path)
    req(review.get("status")=="COMPLETED" and review.get("surface")=="ChatGPT web" and review.get("model")=="GPT-5.6 Sol","R3B control-review provenance drift")
    req(review.get("verdict")==CONTROL_REVIEW_VERDICT and review_row.get("verdict")==CONTROL_REVIEW_VERDICT,"R3B control-review verdict drift")
    req(review.get("control_plane_revision")==CONTROL_PLANE_REVISION,"R3B control-review revision drift")
    req(review.get("minter_sha256_acknowledged")==control.get("minter_sha256"),"R3B review/minter SHA drift")
    req(review.get("gate_sha256_acknowledged")==control.get("gate_sha256"),"R3B review/gate SHA drift")
    req(review.get("support_adjudicator_sha256_acknowledged")==control.get("support_adjudicator_sha256"),"R3B review/adjudicator SHA drift")
    req(review.get("stage_b_authority") is False and review.get("scientific_authority") is False,"R3B control review grants forbidden authority")

    scope=support_auth.get("execution_scope") or {}
    req(Path(str(scope.get("required_adjudication_output") or "")).resolve()==output_path.resolve(),"R3B support-adjudication output path drift")
    run_root=Path(str(scope.get("required_run_root") or "")); req(run_root.resolve()==Path(contract["run_root"]).resolve(),"R3B support-read run-root drift")
    expected_marker=run_root/"checkpoints/post_terminal_support_read"/CONSUMPTION_NAME
    req(consumption_marker_path.resolve()==expected_marker.resolve() and consumption_marker_path.is_file(),"R3B gate consumption marker absent/path drift")
    marker=load(consumption_marker_path)
    req(marker.get("artifact_type")=="e2-r17-v3-stage-a-r3-post-terminal-support-read-consumption" and marker.get("status")=="CONSUMED_IN_FLIGHT_DO_NOT_RETRY","R3B gate consumption marker status drift")
    req(marker.get("support_authorization_sha256")==sha(support_authorization_path),"R3B gate consumption support-auth SHA drift")
    req(marker.get("terminal_summary_sha256")==sha(summary_path),"R3B gate consumption summary SHA drift")
    req(Path(str(marker.get("required_output") or "")).resolve()==output_path.resolve(),"R3B gate consumption output drift")
    req(marker.get("gate_sha256")==sha(gate_path),"R3B gate consumption gate SHA drift")
    req(marker.get("control_review_sha256")==sha(review_path),"R3B gate consumption review SHA drift")
    req(marker.get("stage_b_authority") is False,"R3B gate consumption grants Stage-B authority")
    return {"support_authorization":support_auth,"support_authorization_sha256":sha(support_authorization_path),"consumption_marker_sha256":sha(consumption_marker_path),"control_review_sha256":sha(review_path)}


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",type=Path,required=True)
    ap.add_argument("--authorization",type=Path,required=True)
    ap.add_argument("--summary",type=Path,required=True)
    ap.add_argument("--support-authorization",type=Path,required=True)
    ap.add_argument("--consumption-marker",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args(); req(not a.output.exists(),"R3 support adjudication already exists")
    c,auth,s=load(a.contract),load(a.authorization),load(a.summary)
    csha,asha=sha(a.contract),sha(a.authorization)
    req(c["status"]==CONTRACT_STATUS and auth["status"]==AUTH_STATUS,"R3 contract/auth status invalid")
    req(auth["contract_sha256"]==csha,"R3 auth contract drift")
    req(s["status"]==SUMMARY_STATUS and s["contract_sha256"]==csha and s["authorization_sha256"]==asha,"R3 terminal summary binding drift")
    req(s["planned_tasks"]==160 and s["provider_executable_tasks"]==158 and s["sealed_k8_pools"]==158,"R3 terminal accounting drift")
    req(s["terminal_technical_missing"]==1 and s["matched_no_provider_censor"]==1,"R3 exception accounting drift")
    req(s["support_inspected"] is False and s["updater_calls"]==0 and s["heldout_evaluations"]==0,"R3 crossed support/learning boundary")
    guard=validate_support_read_gate(contract=c,contract_path=a.contract,recovery_authorization_path=a.authorization,summary_path=a.summary,support_authorization_path=a.support_authorization,consumption_marker_path=a.consumption_marker,output_path=a.output,csha=csha,asha=asha)

    om=c["recovery_opportunity_manifest"]; opath=bound(om["path"])
    req(opath.is_file() and sha(opath)==om["sha256"],"R3 opportunity manifest drift")
    o=load(opath); stream_ids=[str(x) for x in o["ordered_stream_ids"]]
    streams={str(k):[str(x) for x in v] for k,v in o["support_eligible_task_ids_by_stream"].items()}
    req(list(streams)==stream_ids and len(stream_ids)==20,"R3 support stream order drift")
    req(len(streams["stv3-cgwb-00"])==len(streams["stv3-cgwp-00"])==7,"R3 matched 7/7 geometry drift")
    req(BURNED not in sum(streams.values(),[]) and CENSOR not in sum(streams.values(),[]),"excluded task leaked into R3 support")

    run=Path(c["run_root"])
    mixed_by:dict[str,int]={}; mixed_tasks:dict[str,list[str]]={}; success_by:dict[str,int]={}; pool_sha={}; witness={}; opp={}
    for sid,tids in streams.items():
        expected=7 if sid in {"stv3-cgwb-00","stv3-cgwp-00"} else 8
        req(len(tids)==expected,f"R3 support opportunity drift: {sid}"); opp[sid]=expected
        mx=[]; succ=0
        for tid in tids:
            pp=run/"cases"/tid/"pool_k8.json"; req(pp.is_file(),f"missing R3 K8 pool: {tid}")
            p=load(pp); req(p["task_id"]==tid and int(p["k"])==8,f"R3 pool identity/K drift: {tid}")
            rows=p.get("trajectories") or []; req(len(rows)==8,f"R3 trajectory count drift: {tid}")
            scores=[]; seen=set()
            for r in rows:
                i=int(r["rollout_index"]); req(i not in seen,f"duplicate rollout index: {tid}/{i}"); seen.add(i)
                tp=Path(r["trajectory_path"]); req(tp.is_file() and sha(tp)==r["trajectory_sha256"],f"trajectory SHA drift: {tid}/{i}")
                sc=float(r["score"]); req(sc in (0.0,1.0),f"nonbinary Stage-A score: {tid}/{i}"); scores.append(sc)
            req(seen==set(range(8)),f"R3 rollout indices drift: {tid}")
            win=min(rows,key=lambda r:(-float(r["score"]),int(r["rollout_index"]))); wi=int(win["rollout_index"])
            req(int(p["acting_winner_index"])==wi,f"R3 winner selector drift: {tid}")
            if min(scores)<1.0 and max(scores)>=1.0:
                mx.append(tid); witness[tid]=failed_witness(rows,wi)
            succ += int(sum(scores)); pool_sha[tid]=sha(pp)
        mixed_by[sid]=len(mx); mixed_tasks[sid]=sorted(mx); success_by[sid]=succ

    required=int(c["equal_dose_support"]["required_mixed_pools_per_stream"]); req(required==4,"R3 support threshold drift")
    failing=sorted(sid for sid in stream_ids if mixed_by[sid]<required); passed=not failing
    treated_by={}; rows=[]
    if passed:
        for sid in stream_ids:
            selected=choose_four(sid,mixed_tasks[sid]); treated_by[sid]=selected
            for tid in selected:
                rows.append({"stream_id":sid,"task_id":tid,"pool_k8_path":str(run/"cases"/tid/"pool_k8.json"),"pool_k8_sha256":pool_sha[tid],"failed_witness":witness[tid],"selection_key_sha256":hashlib.sha256(f"semantic-transfer-mrw4-v3|{sid}|{tid}".encode()).hexdigest()})
        req(len(rows)==80,"R3 treated pool total must be 80")

    # Secondary pre-learning reduction routers use opportunity-normalized rates,
    # because two prospectively matched streams have 7 rather than 8 pools.
    reduction={}
    if passed:
        difficulty={sid:success_by[sid]/float(8*opp[sid]) for sid in stream_ids}
        mixedness={sid:mixed_by[sid]/float(opp[sid]) for sid in stream_ids}
        d=choose_ten(difficulty,descending=False,salt="semantic-transfer-difficulty-v3-r3-rate")
        m=choose_ten(mixedness,descending=True,salt="semantic-transfer-mixedness-v3-r3-rate")
        reduction={
            "difficulty_only":{"score":"successful rollout rate over Stage-B-eligible Stage-A opportunities","mrw4_streams":d,"win_c_streams":[x for x in stream_ids if x not in set(d)],"success_rate_per_stream":difficulty},
            "mixedness_only":{"score":"mixed-pool rate over Stage-B-eligible Stage-A opportunities","mrw4_streams":m,"win_c_streams":[x for x in stream_ids if x not in set(m)],"mixed_rate_per_stream":mixedness},
            "opportunity_normalized_before_outcome":True,"extra_provider_calls":0,"extra_heldout_evaluations":0
        }

    split=load(Path(c["suite"]["root"])/"r17_split_manifest.json"); heldout=[str(x) for x in split["e1_common_heldout_probe"]]
    req(not [x for x in heldout if (run/"cases"/x).exists()],"R3 Stage A touched heldout")
    req(not (run/"cases"/BURNED).exists() and not (run/"cases"/CENSOR).exists(),"R3 excluded task case exists")
    status="PASS_SEMANTIC_TRANSFER_V3_R3_MATCHED_CENSOR_EQUAL_DOSE_SUPPORT_READY_FOR_STAGE_B_DESIGN" if passed else "HOLD_SEMANTIC_TRANSFER_V3_R3_INSUFFICIENT_EQUAL_DOSE_SUPPORT"
    out={
        "schema_version":"1.0","artifact_type":"e2-r17-v3-stage-a-r3-matched-censor-equal-dose-adjudication","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":status,
        "contract_path":str(a.contract),"contract_sha256":csha,"authorization_path":str(a.authorization),"authorization_sha256":asha,"summary_path":str(a.summary),"summary_sha256":sha(a.summary),"support_authorization_path":str(a.support_authorization),"support_authorization_sha256":guard["support_authorization_sha256"],"consumption_marker_path":str(a.consumption_marker),"consumption_marker_sha256":guard["consumption_marker_sha256"],"control_review_sha256":guard["control_review_sha256"],
        "integrity":{"planned_tasks":160,"sealed_k8_pools":158,"terminal_technical_missing":BURNED,"matched_no_provider_censor":CENSOR,"provider_executable_tasks":158,"heldout_tasks_touched":0,"updater_calls":0,"heldout_evaluations":0,"partial_effect_read":False},
        "support":{"required_mixed_pools_per_stream":4,"eligible_opportunities_per_stream":opp,"mixed_pools_per_stream":mixed_by,"failing_streams":failing,"pass":passed},
        "stage_b_eligible_pool_geometry":{"task_ids_by_stream":streams,"opportunity_count_by_stream":opp,"affected_exact_matched_streams":["stv3-cgwb-00","stv3-cgwp-00"],"within_stream_arm_pool_ids_must_be_identical":True},
        "equal_dose_treatment_manifest":{"candidate_domain":"mixed K8 pools within the prospectively frozen Stage-B-eligible opportunity set","treated_pools_per_stream":4 if passed else 0,"treated_pool_total":len(rows),"treated_task_ids_by_stream":treated_by,"rows":rows,"scientific_inclusion":passed},
        "stage_a_reduction_routers":reduction,
        "authority":{"prepare_stage_b_contract":passed,"execute_stage_b":False,"heldout_evaluation":False,"analyzer":False,"paper_promotion":False},
        "next_gate":"SEPARATE_R3_STAGE_B_CONTRACT_AND_PREEXECUTION_REVIEW" if passed else "CLOSE_R3_RECOVERY_SUPPORT_HOLD"
    }
    atomic(a.output,out); print(json.dumps({"status":status,"support":out["support"],"treated_pool_total":len(rows),"next_gate":out["next_gate"]},ensure_ascii=False,indent=2,sort_keys=True)); return 0 if passed else 3

if __name__=="__main__": raise SystemExit(main())

```

## Source: SUPPORT_READ_MINTER — `scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
RECOVERY_AUTH_STATUS = "AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY"
SUMMARY_STATUS = "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION"
LEASE_STATUS = "COMPLETED_STAGE_A_V3_R3_RECOVERY_PENDING_EQUAL_DOSE_ADJUDICATION"
SUPPORT_AUTH_STATUS = "AUTHORIZED_E2_R17_V3_R3_POST_TERMINAL_SUPPORT_READ"
CONTROL_REVIEW_VERDICT = "PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"
BURNED = "r17-b21-cgwb-p0"
CENSOR = "r17-b21-cgwp-p0"
EXPECTED_SUPPORT_ADJUDICATOR = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
EXPECTED_GATE = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py"
CONTROL_PLANE_REVISION = "R3B_POST_TERMINAL_SUPPORT_GUARD"
EXPECTED_ADJUDICATION_OUTPUT = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3-equal-dose-adjudication-20260907.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def bound(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def task_claim_paths(claim_root: Path, task_id: str) -> tuple[Path, Path]:
    stem = hashlib.sha256(task_id.encode("utf-8")).hexdigest()
    return claim_root / f"{stem}.attempt.json", claim_root / f"{stem}.sealed.json"


def validate_control_review(review_path: Path, *, minter_sha: str, gate_sha: str, support_adjudicator_sha: str) -> dict[str, Any]:
    review = load(review_path)
    req(review.get("status") == "COMPLETED", "post-terminal control review is not completed")
    req(review.get("surface") == "ChatGPT web", "post-terminal control review surface drift")
    req(review.get("model") == "GPT-5.6 Sol", "post-terminal control review model drift")
    req(review.get("verdict") == CONTROL_REVIEW_VERDICT, "post-terminal control review did not PASS")
    req(review.get("minter_sha256_acknowledged") == minter_sha, "post-terminal control review minter SHA drift")
    req(review.get("gate_sha256_acknowledged") == gate_sha, "post-terminal control review gate SHA drift")
    req(review.get("support_adjudicator_sha256_acknowledged") == support_adjudicator_sha, "post-terminal control review support-adjudicator SHA drift")
    req(review.get("control_plane_revision") == CONTROL_PLANE_REVISION, "post-terminal control review revision drift")
    req(review.get("stage_b_authority") is False, "post-terminal control review grants Stage-B authority")
    req(review.get("scientific_authority") is False, "post-terminal control review grants scientific authority")
    return review


def validate_terminal_structure(
    *,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
) -> dict[str, Any]:
    contract = load(contract_path)
    recovery_auth = load(recovery_authorization_path)
    summary = load(summary_path)
    csha = sha(contract_path)
    asha = sha(recovery_authorization_path)
    ssha = sha(summary_path)

    req(contract.get("status") == CONTRACT_STATUS, "R3 recovery contract status drift")
    req(contract.get("control_plane_revision") == CONTROL_PLANE_REVISION, "R3B support-control revision absent")
    req(recovery_auth.get("status") == RECOVERY_AUTH_STATUS, "R3 recovery authorization status drift")
    req(recovery_auth.get("contract_sha256") == csha, "R3 recovery authorization contract SHA drift")
    req(recovery_auth.get("single_use") is True and recovery_auth.get("exactly_once") is True, "R3 recovery authorization single-use drift")
    authority = recovery_auth.get("authority") or {}
    req(authority.get("stage_a_provider_execution") is True, "R3 recovery authorization provider authority absent")
    for key in (
        "stage_b_learning_execution",
        "updater",
        "heldout_evaluation",
        "analyzer",
        "second_backbone",
        "public_benchmark",
        "paper_promotion",
        "submission",
    ):
        req(authority.get(key) is False, f"R3 recovery authorization overbroad: {key}")

    req(summary.get("status") == SUMMARY_STATUS, "R3 terminal summary status drift")
    req(summary.get("contract_sha256") == csha, "R3 terminal summary contract SHA drift")
    req(summary.get("authorization_sha256") == asha, "R3 terminal summary authorization SHA drift")
    req(summary.get("planned_tasks") == 160, "R3 terminal summary planned-task drift")
    req(summary.get("provider_executable_tasks") == 158, "R3 terminal summary provider-task drift")
    req(summary.get("sealed_k8_pools") == 158, "R3 terminal summary sealed-pool drift")
    req(summary.get("terminal_technical_missing") == 1, "R3 terminal summary technical-missing drift")
    req(summary.get("matched_no_provider_censor") == 1, "R3 terminal summary matched-censor drift")
    req(summary.get("actor_rollouts") == 1264, "R3 terminal summary actor-rollout drift")
    req(summary.get("support_inspected") is False, "R3 terminal summary already inspected support")
    req(summary.get("updater_calls") == 0, "R3 terminal summary updater boundary crossed")
    req(summary.get("heldout_evaluations") == 0, "R3 terminal summary heldout boundary crossed")
    req(summary.get("partial_effect_read") is False, "R3 terminal summary partial-effect boundary crossed")
    req(summary.get("scientific_scores_read") is False, "R3 terminal summary scientific-score boundary crossed")
    req(summary.get("stage_b_authority") is False, "R3 terminal summary grants Stage-B authority")

    run_root = Path(contract["run_root"])
    lease_path = Path(contract["global_lease_path"])
    req(run_root.is_dir(), "R3 terminal run root absent")
    req(lease_path.is_file(), "R3 terminal lease absent")
    lease = load(lease_path)
    req(lease.get("status") == LEASE_STATUS, "R3 terminal lease status drift")
    req(lease.get("contract_sha256") == csha, "R3 terminal lease contract SHA drift")
    req(lease.get("authorization_sha256") == asha, "R3 terminal lease authorization SHA drift")
    req(Path(str(lease.get("summary_path") or "")).resolve() == summary_path.resolve(), "R3 terminal lease summary path drift")
    req(lease.get("summary_sha256") == ssha, "R3 terminal lease summary SHA drift")

    completed_manifest = Path(str(summary.get("completed_stream_manifest_path") or ""))
    req(completed_manifest.is_file(), "R3 completed-stream manifest absent")
    req(summary.get("completed_stream_manifest_sha256") == sha(completed_manifest), "R3 completed-stream manifest SHA drift")

    exact = contract["exact_once_acquisition"]
    manifest_path = bound(exact["unit_manifest_path"])
    req(manifest_path.is_file() and sha(manifest_path) == exact["unit_manifest_sha256"], "R3 execution-unit manifest drift")
    manifest = load(manifest_path)
    tasks = [str(value) for value in manifest.get("ordered_task_ids") or []]
    req(len(tasks) == len(set(tasks)) == 158, "R3 execution-unit universe must be 158 unique tasks")
    req(BURNED not in tasks and CENSOR not in tasks, "R3 excluded task leaked into provider universe")

    opp_row = contract["recovery_opportunity_manifest"]
    opportunity_path = bound(opp_row["path"])
    req(opportunity_path.is_file() and sha(opportunity_path) == opp_row["sha256"], "R3 opportunity manifest drift")
    opportunity = load(opportunity_path)
    by_stream = {str(k): [str(x) for x in v] for k, v in (opportunity.get("provider_task_ids_by_stream") or {}).items()}
    req(len(by_stream) == 20, "R3 opportunity stream-count drift")
    req(len(by_stream.get("stv3-cgwb-00") or []) == 7, "R3 burned-stream opportunity geometry drift")
    req(len(by_stream.get("stv3-cgwp-00") or []) == 7, "R3 censor-stream opportunity geometry drift")
    req(all(len(v) == (7 if k in {"stv3-cgwb-00", "stv3-cgwp-00"} else 8) for k, v in by_stream.items()), "R3 7/7/8 opportunity geometry drift")
    flattened = [task for stream in by_stream.values() for task in stream]
    req(len(flattened) == len(set(flattened)) == 158 and set(flattened) == set(tasks), "R3 opportunity/provider universe mismatch")

    claim_root = Path(exact["claim_root"])
    req(claim_root.resolve() == (run_root / "checkpoints/stage_a_task_claims").resolve(), "R3 claim-root drift")
    req(claim_root.is_dir(), "R3 claim root absent")
    req(len(list(claim_root.glob("*.attempt.json"))) == 158, "R3 exact-once attempt count drift")
    req(len(list(claim_root.glob("*.sealed.json"))) == 158, "R3 exact-once seal count drift")
    for task in tasks:
        attempt_path, sealed_path = task_claim_paths(claim_root, task)
        req(attempt_path.is_file() and sealed_path.is_file(), f"R3 exact-once receipt missing: {task}")
        attempt = load(attempt_path)
        sealed = load(sealed_path)
        req(attempt.get("artifact_type") == "e2-r17-semantic-transfer-v3-stage-a-task-attempt", f"R3 attempt type drift: {task}")
        req(attempt.get("status") == "ATTEMPTED_IN_FLIGHT_DO_NOT_REPLAY", f"R3 attempt status drift: {task}")
        req(sealed.get("artifact_type") == "e2-r17-semantic-transfer-v3-stage-a-task-seal", f"R3 seal type drift: {task}")
        req(sealed.get("status") == "SEALED_EXACT_ONCE", f"R3 seal status drift: {task}")
        req(attempt.get("task_id") == sealed.get("task_id") == task, f"R3 receipt task drift: {task}")
        req(attempt.get("contract_sha256") == sealed.get("contract_sha256") == csha, f"R3 receipt contract drift: {task}")
        req(attempt.get("authorization_sha256") == sealed.get("authorization_sha256") == asha, f"R3 receipt authorization drift: {task}")
        req(sealed.get("attempt_sha256") == sha(attempt_path), f"R3 attempt binding drift: {task}")
        pool_path = run_root / "cases" / task / "pool_k8.json"
        req(pool_path.is_file(), f"R3 sealed pool absent: {task}")
        req(sealed.get("pool_k8_sha256") == sha(pool_path), f"R3 sealed pool SHA drift: {task}")
    req(not (run_root / "cases" / BURNED).exists(), "burned task case unexpectedly exists in R3 run")
    req(not (run_root / "cases" / CENSOR).exists(), "matched-censor task case unexpectedly exists in R3 run")

    return {
        "contract": contract,
        "recovery_authorization": recovery_auth,
        "summary": summary,
        "contract_sha256": csha,
        "recovery_authorization_sha256": asha,
        "summary_sha256": ssha,
        "run_root": run_root,
        "lease_path": lease_path,
        "tasks": tasks,
        "manifest_path": manifest_path,
        "manifest_sha256": sha(manifest_path),
        "opportunity_path": opportunity_path,
        "opportunity_sha256": sha(opportunity_path),
    }


def build_support_authorization(
    *,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    control_review_path: Path,
    output_path: Path,
    adjudication_output_path: Path = EXPECTED_ADJUDICATION_OUTPUT,
    created_at_utc: str | None = None,
) -> dict[str, Any]:
    req(not output_path.exists(), "post-terminal support-read authorization already exists")
    req(EXPECTED_SUPPORT_ADJUDICATOR.is_file(), "R3B guarded support adjudicator absent")
    req(EXPECTED_GATE.is_file(), "post-terminal support gate absent")
    minter_sha = sha(Path(__file__))
    gate_sha = sha(EXPECTED_GATE)
    support_adjudicator_sha = sha(EXPECTED_SUPPORT_ADJUDICATOR)
    state = validate_terminal_structure(
        contract_path=contract_path,
        recovery_authorization_path=recovery_authorization_path,
        summary_path=summary_path,
    )
    contract = state["contract"]
    bound_code = contract.get("bound_code") or {}
    for key, path, expected_sha in (
        ("post_terminal_support_minter", Path(__file__), minter_sha),
        ("post_terminal_support_gate", EXPECTED_GATE, gate_sha),
        ("equal_dose_adjudicator", EXPECTED_SUPPORT_ADJUDICATOR, support_adjudicator_sha),
    ):
        row = bound_code.get(key) or {}
        req(bound(str(row.get("path") or "")).resolve() == path.resolve(), f"R3B contract {key} path drift")
        req(row.get("sha256") == expected_sha, f"R3B contract {key} SHA drift")
    review = validate_control_review(
        control_review_path,
        minter_sha=minter_sha,
        gate_sha=gate_sha,
        support_adjudicator_sha=support_adjudicator_sha,
    )
    req(not adjudication_output_path.exists(), "R3 support adjudication output already exists")

    timestamp = created_at_utc or datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-read-authorization",
        "created_at_utc": timestamp,
        "status": SUPPORT_AUTH_STATUS,
        "single_use": True,
        "provider_calls": 0,
        "scientific_execution": False,
        "contract_path": str(contract_path),
        "contract_sha256": state["contract_sha256"],
        "recovery_authorization_path": str(recovery_authorization_path),
        "recovery_authorization_sha256": state["recovery_authorization_sha256"],
        "terminal_summary_path": str(summary_path),
        "terminal_summary_sha256": state["summary_sha256"],
        "terminal_lease_path": str(state["lease_path"]),
        "terminal_lease_sha256": sha(state["lease_path"]),
        "control_review": {
            "path": str(control_review_path.resolve()),
            "sha256": sha(control_review_path),
            "verdict": review["verdict"],
            "model": review["model"],
            "surface": review["surface"],
        },
        "bound_control_plane": {
            "minter_path": str(Path(__file__).resolve()),
            "minter_sha256": minter_sha,
            "gate_path": str(EXPECTED_GATE),
            "gate_sha256": gate_sha,
            "support_adjudicator_path": str(EXPECTED_SUPPORT_ADJUDICATOR),
            "support_adjudicator_sha256": support_adjudicator_sha,
        },
        "execution_scope": {
            "required_adjudication_output": str(adjudication_output_path),
            "required_run_root": str(state["run_root"]),
            "provider_execution_tasks": 158,
            "sealed_k8_pools": 158,
            "terminal_technical_missing": BURNED,
            "matched_no_provider_censor": CENSOR,
            "support_required_mixed_pools_per_stream": 4,
            "opportunity_geometry": "7/7/8",
            "support_read_may_open_k8_pool_semantics": True,
            "support_read_before_terminal_recovery": False,
        },
        "authority": {
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
        },
        "interpretation_boundary": "Single-use zero-provider authority to invoke the already exact-hash-reviewed R3 Stage-A support adjudicator after the exact terminal recovery state only. It grants no provider execution, updater, heldout, Stage-B execution, public benchmark, analyzer, or paper-claim authority.",
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--recovery-authorization", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--control-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--adjudication-output", type=Path, default=EXPECTED_ADJUDICATION_OUTPUT)
    args = parser.parse_args()
    payload = build_support_authorization(
        contract_path=args.contract,
        recovery_authorization_path=args.recovery_authorization,
        summary_path=args.summary,
        control_review_path=args.control_review,
        output_path=args.output,
        adjudication_output_path=args.adjudication_output,
    )
    atomic(args.output, payload)
    print(json.dumps({
        "status": payload["status"],
        "terminal_summary_sha256": payload["terminal_summary_sha256"],
        "authority": payload["authority"],
        "provider_calls": 0,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

## Source: ONE_SHOT_GATE — `scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SUPPORT_AUTH_STATUS = "AUTHORIZED_E2_R17_V3_R3_POST_TERMINAL_SUPPORT_READ"
SUMMARY_STATUS = "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION"
EXPECTED_SUPPORT_ADJUDICATOR = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
CONTROL_REVIEW_VERDICT = "PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"
CONTROL_PLANE_REVISION = "R3B_POST_TERMINAL_SUPPORT_GUARD"
CONSUMPTION_NAME = "post_terminal_support_read_authorization.consumed.json"
COMPLETION_NAME = "post_terminal_support_read_adjudication.completed.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _exclusive_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(fd, raw)
        os.fsync(fd)
    finally:
        os.close(fd)
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def validate_support_authorization(
    *,
    support_authorization_path: Path,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    support_auth = load(support_authorization_path)
    req(support_auth.get("status") == SUPPORT_AUTH_STATUS, "post-terminal support-read authorization status drift")
    req(support_auth.get("single_use") is True, "post-terminal support-read authorization is not single-use")
    req(support_auth.get("provider_calls") == 0, "post-terminal support-read authorization provider-call drift")
    req(support_auth.get("scientific_execution") is False, "post-terminal support-read authorization incorrectly records scientific execution")

    authority = support_auth.get("authority") or {}
    req(authority.get("stage_a_support_read") is True, "Stage-A support-read authority absent")
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
    ):
        req(authority.get(key) is False, f"post-terminal support-read authorization overbroad: {key}")

    req(support_auth.get("contract_sha256") == sha(contract_path), "post-terminal support-read contract SHA drift")
    req(support_auth.get("recovery_authorization_sha256") == sha(recovery_authorization_path), "post-terminal support-read recovery-authorization SHA drift")
    req(support_auth.get("terminal_summary_sha256") == sha(summary_path), "post-terminal support-read summary SHA drift")
    req(Path(str(support_auth.get("contract_path") or "")).resolve() == contract_path.resolve(), "post-terminal support-read contract path drift")
    req(Path(str(support_auth.get("recovery_authorization_path") or "")).resolve() == recovery_authorization_path.resolve(), "post-terminal support-read recovery-authorization path drift")
    req(Path(str(support_auth.get("terminal_summary_path") or "")).resolve() == summary_path.resolve(), "post-terminal support-read summary path drift")

    summary = load(summary_path)
    req(summary.get("status") == SUMMARY_STATUS, "terminal summary no longer at pending-support boundary")
    req(summary.get("support_inspected") is False, "terminal summary indicates support already inspected")
    req(summary.get("stage_b_authority") is False, "terminal summary grants Stage-B authority")

    control = support_auth.get("bound_control_plane") or {}
    minter_path = Path(str(control.get("minter_path") or ""))
    gate_path = Path(str(control.get("gate_path") or ""))
    adjudicator_path = Path(str(control.get("support_adjudicator_path") or ""))
    req(minter_path.is_file() and control.get("minter_sha256") == sha(minter_path), "support-read minter provenance drift")
    req(gate_path.resolve() == Path(__file__).resolve() and control.get("gate_sha256") == sha(Path(__file__)), "support-read gate SHA drift")
    req(adjudicator_path.resolve() == EXPECTED_SUPPORT_ADJUDICATOR.resolve(), "support adjudicator path drift")
    req(EXPECTED_SUPPORT_ADJUDICATOR.is_file() and control.get("support_adjudicator_sha256") == sha(EXPECTED_SUPPORT_ADJUDICATOR), "guarded support adjudicator SHA drift")

    review_row = support_auth.get("control_review") or {}
    review_path = Path(str(review_row.get("path") or ""))
    req(review_path.is_file() and review_row.get("sha256") == sha(review_path), "support-read control-review receipt binding drift")
    review = load(review_path)
    req(review.get("status") == "COMPLETED" and review.get("surface") == "ChatGPT web" and review.get("model") == "GPT-5.6 Sol", "support-read control-review provenance drift")
    req(review.get("verdict") == CONTROL_REVIEW_VERDICT and review_row.get("verdict") == CONTROL_REVIEW_VERDICT, "support-read control-review verdict drift")
    req(review.get("control_plane_revision") == CONTROL_PLANE_REVISION, "support-read control-review revision drift")
    req(review.get("minter_sha256_acknowledged") == control.get("minter_sha256"), "support-read review/minter SHA drift")
    req(review.get("gate_sha256_acknowledged") == control.get("gate_sha256"), "support-read review/gate SHA drift")
    req(review.get("support_adjudicator_sha256_acknowledged") == control.get("support_adjudicator_sha256"), "support-read review/adjudicator SHA drift")
    req(review.get("stage_b_authority") is False and review.get("scientific_authority") is False, "support-read control review grants forbidden authority")

    scope = support_auth.get("execution_scope") or {}
    req(Path(str(scope.get("required_adjudication_output") or "")).resolve() == output_path.resolve(), "support adjudication output path drift")
    req(scope.get("provider_execution_tasks") == 158 and scope.get("sealed_k8_pools") == 158, "post-terminal support-read geometry drift")
    req(scope.get("opportunity_geometry") == "7/7/8", "post-terminal support-read opportunity geometry drift")
    req(scope.get("support_required_mixed_pools_per_stream") == 4, "post-terminal support threshold drift")

    run_root = Path(str(scope.get("required_run_root") or ""))
    req(run_root.is_dir(), "post-terminal support-read run root absent")
    lease_path = Path(str(support_auth.get("terminal_lease_path") or ""))
    req(lease_path.is_file() and support_auth.get("terminal_lease_sha256") == sha(lease_path), "post-terminal support-read lease binding drift")
    return {"support_authorization": support_auth, "summary": summary, "run_root": run_root, "lease_path": lease_path}


def default_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)


def run_gate(
    *,
    support_authorization_path: Path,
    contract_path: Path,
    recovery_authorization_path: Path,
    summary_path: Path,
    output_path: Path,
    invoke: Callable[[list[str]], subprocess.CompletedProcess[str]] = default_invoke,
    python_executable: str = sys.executable,
) -> dict[str, Any]:
    req(not output_path.exists(), "R3 support adjudication output already exists")
    state = validate_support_authorization(
        support_authorization_path=support_authorization_path,
        contract_path=contract_path,
        recovery_authorization_path=recovery_authorization_path,
        summary_path=summary_path,
        output_path=output_path,
    )
    run_root: Path = state["run_root"]
    control_root = run_root / "checkpoints/post_terminal_support_read"
    consumption = control_root / CONSUMPTION_NAME
    completion = control_root / COMPLETION_NAME
    req(not consumption.exists(), "post-terminal support-read authorization already consumed; retry forbidden")
    req(not completion.exists(), "post-terminal support adjudication completion receipt already exists")

    auth_sha = sha(support_authorization_path)
    summary_sha = sha(summary_path)
    support_auth = state["support_authorization"]
    review_row = support_auth["control_review"]
    consumption_payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-read-consumption",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "CONSUMED_IN_FLIGHT_DO_NOT_RETRY",
        "support_authorization_path": str(support_authorization_path),
        "support_authorization_sha256": auth_sha,
        "terminal_summary_path": str(summary_path),
        "terminal_summary_sha256": summary_sha,
        "required_output": str(output_path),
        "gate_sha256": sha(Path(__file__)),
        "control_review_sha256": review_row["sha256"],
        "automatic_retry": False,
        "stage_b_authority": False,
    }
    _exclusive_json(consumption, consumption_payload)

    command = [
        python_executable,
        str(EXPECTED_SUPPORT_ADJUDICATOR),
        "--contract",
        str(contract_path),
        "--authorization",
        str(recovery_authorization_path),
        "--summary",
        str(summary_path),
        "--support-authorization",
        str(support_authorization_path),
        "--consumption-marker",
        str(consumption),
        "--output",
        str(output_path),
    ]
    result = invoke(command)
    if result.returncode not in {0, 3}:
        raise RuntimeError(
            "R3 support adjudicator failed outside terminal PASS/HOLD states; support-read permit remains consumed and manual review is required. "
            f"returncode={result.returncode}; stdout_tail={result.stdout[-1200:]}; stderr_tail={result.stderr[-1200:]}"
        )
    req(output_path.is_file(), "R3 support adjudicator returned terminal code without output artifact")
    adjudication = load(output_path)
    expected_statuses = {
        0: "PASS_SEMANTIC_TRANSFER_V3_R3_MATCHED_CENSOR_EQUAL_DOSE_SUPPORT_READY_FOR_STAGE_B_DESIGN",
        3: "HOLD_SEMANTIC_TRANSFER_V3_R3_INSUFFICIENT_EQUAL_DOSE_SUPPORT",
    }
    req(adjudication.get("status") == expected_statuses[result.returncode], "R3 support adjudicator terminal status/returncode mismatch")
    authority = adjudication.get("authority") or {}
    req(authority.get("execute_stage_b") is False, "R3 support adjudication improperly grants Stage-B execution")
    req(authority.get("heldout_evaluation") is False, "R3 support adjudication improperly grants heldout evaluation")
    req(authority.get("analyzer") is False, "R3 support adjudication improperly grants analyzer authority")
    req(authority.get("paper_promotion") is False, "R3 support adjudication improperly grants paper-promotion authority")

    completion_payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-stage-a-r3-post-terminal-support-read-completion",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "COMPLETED_POST_TERMINAL_SUPPORT_READ",
        "support_authorization_sha256": auth_sha,
        "consumption_path": str(consumption),
        "consumption_sha256": sha(consumption),
        "terminal_summary_sha256": summary_sha,
        "adjudication_output": str(output_path),
        "adjudication_output_sha256": sha(output_path),
        "adjudication_status": adjudication["status"],
        "adjudicator_returncode": result.returncode,
        "stage_b_authority": False,
        "automatic_retry": False,
    }
    _exclusive_json(completion, completion_payload)
    return {
        "status": completion_payload["status"],
        "adjudication_status": adjudication["status"],
        "returncode": result.returncode,
        "consumption_path": str(consumption),
        "completion_path": str(completion),
        "stage_b_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--support-authorization", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--recovery-authorization", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_gate(
        support_authorization_path=args.support_authorization,
        contract_path=args.contract,
        recovery_authorization_path=args.recovery_authorization,
        summary_path=args.summary,
        output_path=args.output,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

## Source: CONTROL_TESTS — `research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py`

```python
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read as minter
import run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate as gate


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class R3PostTerminalSupportReadControlTests(unittest.TestCase):
    def make_fixture(self) -> dict[str, Path]:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        run = root / "run"
        claims = run / "checkpoints/stage_a_task_claims"
        claims.mkdir(parents=True)
        completed = run / "checkpoints/completed_streams.jsonl"
        completed.parent.mkdir(parents=True, exist_ok=True)
        completed.write_text("{}\n", encoding="utf-8")

        streams: dict[str, list[str]] = {}
        task_ids: list[str] = []
        for idx in range(20):
            sid = "stv3-cgwb-00" if idx == 0 else "stv3-cgwp-00" if idx == 1 else f"stv3-test-{idx:02d}"
            count = 7 if idx < 2 else 8
            rows = [f"test-{idx:02d}-{j:02d}" for j in range(count)]
            streams[sid] = rows
            task_ids.extend(rows)
        self.assertEqual(len(task_ids), 158)

        manifest = root / "execution-units.json"
        write_json(manifest, {"ordered_task_ids": task_ids})
        opportunity = root / "opportunity.json"
        write_json(opportunity, {"provider_task_ids_by_stream": streams})

        lease = root / "r3-lease.json"
        contract = root / "contract.json"
        contract_payload = {
            "schema_version": "1.0",
            "status": minter.CONTRACT_STATUS,
            "control_plane_revision": minter.CONTROL_PLANE_REVISION,
            "run_root": str(run),
            "global_lease_path": str(lease),
            "exact_once_acquisition": {
                "unit_manifest_path": str(manifest),
                "unit_manifest_sha256": sha(manifest),
                "claim_root": str(claims),
            },
            "recovery_opportunity_manifest": {"path": str(opportunity), "sha256": sha(opportunity)},
            "bound_code": {
                "post_terminal_support_minter": {"path": str(Path(minter.__file__)), "sha256": sha(Path(minter.__file__))},
                "post_terminal_support_gate": {"path": str(Path(gate.__file__)), "sha256": sha(Path(gate.__file__))},
                "equal_dose_adjudicator": {"path": str(minter.EXPECTED_SUPPORT_ADJUDICATOR), "sha256": sha(minter.EXPECTED_SUPPORT_ADJUDICATOR)},
            },
        }
        write_json(contract, contract_payload)
        csha = sha(contract)

        recovery_auth = root / "recovery-auth.json"
        recovery_auth_payload = {
            "schema_version": "1.0",
            "status": minter.RECOVERY_AUTH_STATUS,
            "contract_sha256": csha,
            "single_use": True,
            "exactly_once": True,
            "authority": {
                "stage_a_provider_execution": True,
                "stage_b_learning_execution": False,
                "updater": False,
                "heldout_evaluation": False,
                "analyzer": False,
                "second_backbone": False,
                "public_benchmark": False,
                "paper_promotion": False,
                "submission": False,
            },
        }
        write_json(recovery_auth, recovery_auth_payload)
        asha = sha(recovery_auth)

        for task in task_ids:
            task_dir = run / "cases" / task
            task_dir.mkdir(parents=True)
            pool = task_dir / "pool_k8.json"
            pool.write_text("{}\n", encoding="utf-8")
            attempt, sealed = minter.task_claim_paths(claims, task)
            write_json(
                attempt,
                {
                    "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-task-attempt",
                    "status": "ATTEMPTED_IN_FLIGHT_DO_NOT_REPLAY",
                    "task_id": task,
                    "contract_sha256": csha,
                    "authorization_sha256": asha,
                },
            )
            write_json(
                sealed,
                {
                    "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-task-seal",
                    "status": "SEALED_EXACT_ONCE",
                    "task_id": task,
                    "contract_sha256": csha,
                    "authorization_sha256": asha,
                    "attempt_sha256": sha(attempt),
                    "pool_k8_sha256": sha(pool),
                },
            )

        summary = run / "summary/stage_a_r3_recovery_pool_freeze_summary.json"
        summary_payload = {
            "schema_version": "1.0",
            "status": minter.SUMMARY_STATUS,
            "contract_sha256": csha,
            "authorization_sha256": asha,
            "planned_tasks": 160,
            "provider_executable_tasks": 158,
            "sealed_k8_pools": 158,
            "terminal_technical_missing": 1,
            "matched_no_provider_censor": 1,
            "actor_rollouts": 1264,
            "support_inspected": False,
            "updater_calls": 0,
            "heldout_evaluations": 0,
            "partial_effect_read": False,
            "scientific_scores_read": False,
            "stage_b_authority": False,
            "completed_stream_manifest_path": str(completed),
            "completed_stream_manifest_sha256": sha(completed),
        }
        write_json(summary, summary_payload)
        ssha = sha(summary)
        write_json(
            lease,
            {
                "schema_version": "1.0",
                "status": minter.LEASE_STATUS,
                "contract_sha256": csha,
                "authorization_sha256": asha,
                "summary_path": str(summary),
                "summary_sha256": ssha,
            },
        )

        control_review = root / "control-review.json"
        write_json(
            control_review,
            {
                "schema_version": "1.0",
                "status": "COMPLETED",
                "surface": "ChatGPT web",
                "model": "GPT-5.6 Sol",
                "verdict": minter.CONTROL_REVIEW_VERDICT,
                "control_plane_revision": minter.CONTROL_PLANE_REVISION,
                "minter_sha256_acknowledged": sha(Path(minter.__file__)),
                "gate_sha256_acknowledged": sha(Path(gate.__file__)),
                "support_adjudicator_sha256_acknowledged": sha(minter.EXPECTED_SUPPORT_ADJUDICATOR),
                "stage_b_authority": False,
                "scientific_authority": False,
            },
        )
        return {
            "root": root,
            "run": run,
            "contract": contract,
            "recovery_auth": recovery_auth,
            "summary": summary,
            "lease": lease,
            "control_review": control_review,
            "support_auth": root / "support-auth.json",
            "adjudication_output": root / "support-adjudication.json",
        }

    def build_auth(self, fixture: dict[str, Path]) -> dict:
        payload = minter.build_support_authorization(
            contract_path=fixture["contract"],
            recovery_authorization_path=fixture["recovery_auth"],
            summary_path=fixture["summary"],
            control_review_path=fixture["control_review"],
            output_path=fixture["support_auth"],
            adjudication_output_path=fixture["adjudication_output"],
            created_at_utc="2026-09-07T00:01:00+08:00",
        )
        write_json(fixture["support_auth"], payload)
        return payload

    def test_minter_rejects_absent_or_nonterminal_summary(self) -> None:
        fixture = self.make_fixture()
        missing = fixture["root"] / "missing-summary.json"
        with self.assertRaises(FileNotFoundError):
            minter.build_support_authorization(
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=missing,
                control_review_path=fixture["control_review"],
                output_path=fixture["support_auth"],
                adjudication_output_path=fixture["adjudication_output"],
            )
        summary = json.loads(fixture["summary"].read_text())
        summary["status"] = "RUNNING"
        write_json(fixture["summary"], summary)
        with self.assertRaisesRegex(RuntimeError, "terminal summary status drift"):
            self.build_auth(fixture)

    def test_minter_rejects_support_already_inspected(self) -> None:
        fixture = self.make_fixture()
        summary = json.loads(fixture["summary"].read_text())
        summary["support_inspected"] = True
        write_json(fixture["summary"], summary)
        with self.assertRaisesRegex(RuntimeError, "already inspected support"):
            self.build_auth(fixture)

    def test_minter_rejects_recovery_authorization_hash_drift(self) -> None:
        fixture = self.make_fixture()
        auth = json.loads(fixture["recovery_auth"].read_text())
        auth["tampered"] = True
        write_json(fixture["recovery_auth"], auth)
        with self.assertRaisesRegex(RuntimeError, "summary authorization SHA drift"):
            self.build_auth(fixture)

    def test_minter_grants_only_stage_a_support_read(self) -> None:
        fixture = self.make_fixture()
        payload = self.build_auth(fixture)
        self.assertTrue(payload["authority"]["stage_a_support_read"])
        self.assertFalse(payload["authority"]["stage_a_provider_execution"])
        self.assertFalse(payload["authority"]["stage_b_learning_execution"])
        self.assertFalse(payload["authority"]["heldout_evaluation"])
        self.assertEqual(payload["provider_calls"], 0)
        self.assertFalse(payload["scientific_execution"])

    def test_gate_refuses_invalid_support_authorization(self) -> None:
        fixture = self.make_fixture()
        payload = self.build_auth(fixture)
        payload["authority"]["stage_a_support_read"] = False
        write_json(fixture["support_auth"], payload)
        with self.assertRaisesRegex(RuntimeError, "support-read authority absent"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                output_path=fixture["adjudication_output"],
            )
        consumption = fixture["run"] / "checkpoints/post_terminal_support_read" / gate.CONSUMPTION_NAME
        self.assertFalse(consumption.exists())

    def test_gate_rejects_forged_permit_without_review_provenance(self) -> None:
        fixture = self.make_fixture()
        payload = self.build_auth(fixture)
        forged_review = fixture["root"] / "forged-review.json"
        write_json(forged_review, {"status": "COMPLETED", "surface": "ChatGPT web", "model": "GPT-5.6 Sol", "verdict": minter.CONTROL_REVIEW_VERDICT})
        payload["control_review"]["path"] = str(forged_review)
        payload["control_review"]["sha256"] = sha(forged_review)
        write_json(fixture["support_auth"], payload)
        with self.assertRaisesRegex(RuntimeError, "review/minter SHA drift|control-review revision drift|control-review receipt binding drift"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                output_path=fixture["adjudication_output"],
            )

    def test_guarded_adjudicator_rejects_direct_invocation_without_support_permit(self) -> None:
        fixture = self.make_fixture()
        command = [
            sys.executable,
            str(minter.EXPECTED_SUPPORT_ADJUDICATOR),
            "--contract",
            str(fixture["contract"]),
            "--authorization",
            str(fixture["recovery_auth"]),
            "--summary",
            str(fixture["summary"]),
            "--output",
            str(fixture["adjudication_output"]),
        ]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--support-authorization", result.stderr)
        self.assertFalse(fixture["adjudication_output"].exists())

    def test_gate_consumes_once_and_fail_closes_on_unexpected_adjudicator_error(self) -> None:
        fixture = self.make_fixture()
        self.build_auth(fixture)

        def failed_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(command, 2, stdout="", stderr="synthetic failure")

        with self.assertRaisesRegex(RuntimeError, "permit remains consumed"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                output_path=fixture["adjudication_output"],
                invoke=failed_invoke,
            )
        control = fixture["run"] / "checkpoints/post_terminal_support_read"
        self.assertTrue((control / gate.CONSUMPTION_NAME).is_file())
        self.assertFalse((control / gate.COMPLETION_NAME).exists())
        with self.assertRaisesRegex(RuntimeError, "already consumed"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                output_path=fixture["adjudication_output"],
                invoke=failed_invoke,
            )

    def test_gate_accepts_terminal_pass_without_stage_b_authority(self) -> None:
        fixture = self.make_fixture()
        self.build_auth(fixture)

        def passed_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
            self.assertIn("--support-authorization", command)
            self.assertIn("--consumption-marker", command)
            output = Path(command[command.index("--output") + 1])
            write_json(
                output,
                {
                    "status": "PASS_SEMANTIC_TRANSFER_V3_R3_MATCHED_CENSOR_EQUAL_DOSE_SUPPORT_READY_FOR_STAGE_B_DESIGN",
                    "authority": {
                        "prepare_stage_b_contract": True,
                        "execute_stage_b": False,
                        "heldout_evaluation": False,
                        "analyzer": False,
                        "paper_promotion": False,
                    },
                },
            )
            return subprocess.CompletedProcess(command, 0, stdout="synthetic pass", stderr="")

        result = gate.run_gate(
            support_authorization_path=fixture["support_auth"],
            contract_path=fixture["contract"],
            recovery_authorization_path=fixture["recovery_auth"],
            summary_path=fixture["summary"],
            output_path=fixture["adjudication_output"],
            invoke=passed_invoke,
        )
        self.assertEqual(result["status"], "COMPLETED_POST_TERMINAL_SUPPORT_READ")
        self.assertFalse(result["stage_b_authority"])
        completion = fixture["run"] / "checkpoints/post_terminal_support_read" / gate.COMPLETION_NAME
        self.assertTrue(completion.is_file())
        self.assertFalse(json.loads(completion.read_text())["stage_b_authority"])


if __name__ == "__main__":
    unittest.main()

```

## Source: R3B_PREFLIGHT — `scripts/preflight_e2_r17_semantic_transfer_v3_stage_a_r3b_support_guard.py`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CONTRACT_STATUS = "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
CONTROL_PLANE_REVISION = "R3B_POST_TERMINAL_SUPPORT_GUARD"
PARENT_R3_SHA = "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085"
RECOVERY_RUNNER_SHA = "491b2ae6e53fcfe732f15ef263cc365ce61846b3219d7a13fe70e3834f6d3c89"
AUTHORITY_REVIEW_VERDICT = "REQUIRE_SEPARATE_POST_TERMINAL_SUPPORT_READ_AUTHORIZATION"
R1_REVIEW_VERDICT = "REVISE_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"
PREFLIGHT_STATUS = "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_R3B_SUPPORT_GUARD_PREFLIGHT"

SCIENCE_KEYS = (
    "failed_r2_parent",
    "suite",
    "mindmemos",
    "provider_route",
    "model_identity_policy",
    "recovery_exceptions",
    "recovery_opportunity_manifest",
    "exact_once_acquisition",
    "equal_dose_support",
    "actor",
    "budget",
    "analysis_boundary",
    "stage_b_plan_no_authority",
    "runtime",
    "env_file_path",
    "run_root",
    "global_lease_path",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def bound(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else ROOT / path


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--parent-contract", type=Path, required=True)
    parser.add_argument("--authority-review", type=Path, required=True)
    parser.add_argument("--r1-exact-code-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    req(not args.output.exists(), "R3B preflight already exists")

    contract = load(args.contract)
    parent = load(args.parent_contract)
    authority_review = load(args.authority_review)
    r1_review = load(args.r1_exact_code_review)
    csha = sha(args.contract)
    psha = sha(args.parent_contract)

    req(contract.get("status") == CONTRACT_STATUS, "R3B contract status drift")
    req(contract.get("control_plane_revision") == CONTROL_PLANE_REVISION, "R3B control-plane revision drift")
    req(psha == PARENT_R3_SHA, "parent R3 contract SHA drift")
    parent_row = contract.get("parent_r3_contract") or {}
    req(bound(str(parent_row.get("path") or "")).resolve() == args.parent_contract.resolve(), "R3B parent contract path drift")
    req(parent_row.get("sha256") == psha, "R3B parent contract binding drift")

    for key in SCIENCE_KEYS:
        req(contract.get(key) == parent.get(key), f"R3B scientific field drift: {key}")
    req(contract.get("authority") == parent.get("authority"), "R3B draft authority drift")
    req(contract["authority"].get("stage_a_provider_execution") is False, "R3B draft self-authorizes provider execution")
    req(contract["authority"].get("stage_b_learning_execution") is False, "R3B draft self-authorizes Stage B")

    req(authority_review.get("verdict") == AUTHORITY_REVIEW_VERDICT, "R3B authority-review verdict drift")
    req(authority_review.get("must_resolve_before_provider_recovery") is True, "R3B authority-review timing drift")
    req(authority_review.get("provider_recovery_authority_affected") is False, "R3B authority-review invalidates provider recovery")
    req(r1_review.get("verdict") == R1_REVIEW_VERDICT, "R3B R1 exact-code review verdict drift")
    req(r1_review.get("provider_recovery_authority_affected") is False, "R3B R1 review invalidates provider recovery")
    req(r1_review.get("stage_b_authority") is False, "R3B R1 review grants Stage B")

    checks: dict[str, bool] = {}
    for label, row in (contract.get("bound_code") or {}).items():
        path = bound(str(row.get("path") or ""))
        req(path.is_file() and sha(path) == row.get("sha256"), f"R3B bound-code drift: {label}")
    checks["all_bound_code_hashes_match"] = True
    req(contract["bound_code"]["stage_a_runner"]["sha256"] == RECOVERY_RUNNER_SHA, "R3B recovery-runner hash drift")
    checks["provider_recovery_runner_unchanged"] = True

    support = contract.get("post_terminal_support_read_control") or {}
    req(support.get("required") is True, "R3B support-read control not required")
    req(support.get("direct_adjudicator_invocation_forbidden") is True, "R3B direct support-adjudicator invocation not forbidden")
    req(support.get("single_use_consumption_required") is True, "R3B single-use support consumption absent")
    req(support.get("support_read_authorization_may_mint_only_after_terminal_recovery") is True, "R3B terminal mint boundary absent")
    req(support.get("stage_b_authority") is False, "R3B support control grants Stage B")
    checks["post_terminal_support_control_bound"] = True

    run_root = Path(contract["run_root"])
    lease = Path(contract["global_lease_path"])
    req(not run_root.exists() and not lease.exists(), "R3B provider-recovery lineage already exists")
    checks["fresh_r3b_lineage_absent"] = True

    support_auth = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3-post-terminal-support-read-authorization-20260907.json"
    support_output = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-r3-equal-dose-adjudication-20260907.json"
    req(not support_auth.exists() and not support_output.exists(), "R3B live support-read artifact exists before terminal recovery")
    checks["support_read_artifacts_absent"] = True

    python = Path(contract["runtime"]["python_executable"])
    req(python.is_file(), "R3B runtime python absent")
    for key in ("equal_dose_adjudicator", "post_terminal_support_minter", "post_terminal_support_gate"):
        path = bound(contract["bound_code"][key]["path"])
        result = subprocess.run([str(python), "-m", "py_compile", str(path)], cwd=ROOT, capture_output=True, text=True)
        req(result.returncode == 0, f"R3B compile failed: {key}: {result.stderr[-1000:]}")
    checks["support_control_compile_pass"] = True

    test_module = "research_pipeline.test_e2_r17_semantic_transfer_v3_r3_support_read_control"
    result = subprocess.run([str(python), "-m", "unittest", "-q", test_module], cwd=ROOT, capture_output=True, text=True)
    req(result.returncode == 0, f"R3B support-control tests failed: {result.stdout[-1200:]} {result.stderr[-1200:]}")
    checks["support_control_tests_9_of_9_pass"] = True

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-r3b-support-guard-zero-provider-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": PREFLIGHT_STATUS,
        "provider_calls": 0,
        "scientific_execution": False,
        "support_inspected": False,
        "stage_b_authority": False,
        "contract_path": str(args.contract),
        "contract_sha256": csha,
        "parent_r3_contract_path": str(args.parent_contract),
        "parent_r3_contract_sha256": psha,
        "authority_review_path": str(args.authority_review),
        "authority_review_sha256": sha(args.authority_review),
        "r1_exact_code_review_path": str(args.r1_exact_code_review),
        "r1_exact_code_review_sha256": sha(args.r1_exact_code_review),
        "science_keys_equal_parent": list(SCIENCE_KEYS),
        "checks": checks,
        "unit_tests": {"suite": test_module, "passed": 9, "total": 9},
        "actual_support_read_authorization_minted": False,
        "fresh_identity_qualified": False,
        "r3b_recovery_authorization_minted": False,
        "next_gate": "FRESH_GPT56_SOL_EXTRA_HIGH_R3B_EXACT_HASH_PREEXECUTION_REVIEW_THEN_PROVIDER_RESET_THEN_FRESH_IDENTITY_THEN_SEPARATE_RECOVERY_AUTHORIZATION",
        "authority": {
            "provider_recovery": False,
            "stage_a_support_read": False,
            "stage_b_execution": False,
            "heldout": False,
            "paper_claim": False,
        },
    }
    atomic(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

## Source: R3B_BUILDER — `scripts/prepare_e2_r17_semantic_transfer_v3_stage_a_r3b_support_guard.py`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTROL_PLANE_REVISION = "R3B_POST_TERMINAL_SUPPORT_GUARD"
PARENT_R3_SHA = "3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085"
AUTHORITY_REVIEW_VERDICT = "REQUIRE_SEPARATE_POST_TERMINAL_SUPPORT_READ_AUTHORIZATION"
R1_REVIEW_VERDICT = "REVISE_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def bound_code_row(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": sha(path)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-contract", type=Path, required=True)
    parser.add_argument("--authority-review", type=Path, required=True)
    parser.add_argument("--r1-exact-code-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    req(not args.output.exists(), "R3B contract already exists")
    parent = load(args.parent_contract)
    authority_review = load(args.authority_review)
    r1_review = load(args.r1_exact_code_review)
    psha = sha(args.parent_contract)
    req(psha == PARENT_R3_SHA, "parent R3 contract SHA drift")
    req(parent.get("status") == "FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY", "parent R3 contract status drift")
    req(authority_review.get("verdict") == AUTHORITY_REVIEW_VERDICT, "support-authority review verdict drift")
    req(authority_review.get("must_resolve_before_provider_recovery") is True, "support-authority review timing drift")
    req(r1_review.get("verdict") == R1_REVIEW_VERDICT, "R1 exact-code review verdict drift")
    req(r1_review.get("provider_recovery_authority_affected") is False, "R1 exact-code review unexpectedly invalidates provider recovery")
    req(r1_review.get("stage_b_authority") is False, "R1 exact-code review grants Stage B")

    adjudicator = ROOT / "scripts/adjudicate_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py"
    minter = ROOT / "scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read.py"
    gate = ROOT / "scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate.py"
    tests = ROOT / "research_pipeline/test_e2_r17_semantic_transfer_v3_r3_support_read_control.py"
    preflight = ROOT / "scripts/preflight_e2_r17_semantic_transfer_v3_stage_a_r3b_support_guard.py"
    builder = Path(__file__).resolve()
    for path in (adjudicator, minter, gate, tests, preflight, builder):
        req(path.is_file(), f"R3B control file absent: {path}")

    out = copy.deepcopy(parent)
    out["created_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out["control_plane_revision"] = CONTROL_PLANE_REVISION
    out["parent_r3_contract"] = {
        "path": rel(args.parent_contract.resolve()),
        "sha256": psha,
        "status": parent["status"],
        "relationship": "control-plane-only successor; scientific geometry, provider task universe, and support estimand unchanged",
    }
    out["scientific_role"] = (
        "versioned fail-closed Stage-A R3 matched-censor recovery with R3B post-terminal support-read authority guard; "
        "scientific recovery geometry and support semantics unchanged from parent R3"
    )
    out["bound_code"]["equal_dose_adjudicator"] = bound_code_row(adjudicator)
    out["bound_code"]["post_terminal_support_minter"] = bound_code_row(minter)
    out["bound_code"]["post_terminal_support_gate"] = bound_code_row(gate)
    out["bound_code"]["post_terminal_support_tests"] = bound_code_row(tests)
    out["bound_code"]["r3b_support_guard_preflight"] = bound_code_row(preflight)
    out["bound_code"]["r3b_contract_builder"] = bound_code_row(builder)

    recovery_reviews = copy.deepcopy(out.get("recovery_reviews") or {})
    recovery_reviews["post_terminal_support_authority"] = {
        "path": rel(args.authority_review.resolve()),
        "sha256": sha(args.authority_review),
        "verdict": AUTHORITY_REVIEW_VERDICT,
    }
    recovery_reviews["post_terminal_support_control_r1"] = {
        "path": rel(args.r1_exact_code_review.resolve()),
        "sha256": sha(args.r1_exact_code_review),
        "verdict": R1_REVIEW_VERDICT,
    }
    out["recovery_reviews"] = recovery_reviews
    out["post_terminal_support_read_control"] = {
        "required": True,
        "control_plane_revision": CONTROL_PLANE_REVISION,
        "direct_adjudicator_invocation_forbidden": True,
        "support_adjudicator_requires_support_authorization": True,
        "support_adjudicator_requires_gate_consumption_marker": True,
        "single_use_consumption_required": True,
        "automatic_retry_after_consumption": False,
        "support_read_authorization_may_mint_only_after_terminal_recovery": True,
        "terminal_summary_status_required": "COMPLETED_158_POOLS_PLUS_TWO_FROZEN_EXCEPTIONS_PENDING_R3_EQUAL_DOSE_ADJUDICATION",
        "support_read_authority": "stage_a_support_read_only",
        "provider_execution_authority": False,
        "updater_authority": False,
        "heldout_authority": False,
        "stage_b_authority": False,
        "paper_claim_authority": False,
        "exact_code_review_required_before_provider_recovery": True,
        "actual_support_read_authorization_minted": False,
    }
    out["authority"] = copy.deepcopy(parent["authority"])
    out["next_gate"] = {
        "before_provider_reset": "FRESH_GPT56_SOL_EXTRA_HIGH_R3B_EXACT_HASH_PREEXECUTION_REVIEW_ONLY_NO_PROVIDER_CALL",
        "after_reset_and_exact_hash_pass": "EXACTLY_ONE_FRESH_DEEPSEEK_IDENTITY_THEN_LOCAL_ADJUDICATION_THEN_SEPARATE_R3B_RECOVERY_AUTHORIZATION",
        "provider_recovery": "EXECUTE_ONLY_158_ORIGINAL_PROVIDER_TASKS_UNDER_R3B_CONTRACT",
        "post_terminal": "MINT_SINGLE_USE_SUPPORT_READ_AUTHORIZATION_THEN_CONSUME_THROUGH_GUARDED_ONE_SHOT_GATE",
        "stage_b": "SEPARATE_CONTRACT_REVIEW_AND_AUTHORITY_REQUIRED",
    }
    atomic(args.output, out)
    print(json.dumps({
        "status": out["status"],
        "control_plane_revision": out["control_plane_revision"],
        "parent_r3_contract_sha256": psha,
        "output": str(args.output),
        "output_sha256": sha(args.output),
        "provider_calls": 0,
        "scientific_execution": False,
        "stage_b_authority": False,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```

## Source: UNCHANGED_RECOVERY_AUTHORIZER — `scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
CONTRACT_STATUS="FROZEN_SEMANTIC_TRANSFER_V3_STAGE_A_R3_MATCHED_CENSOR_RECOVERY"
PREFLIGHT_STATUS="PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY_PREFLIGHT"
REVIEW_VERDICT="PASS_TO_SEPARATE_R3_RECOVERY_AUTHORIZATION"
BURNED="r17-b21-cgwb-p0"; CENSOR="r17-b21-cgwp-p0"

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->dict[str,Any]:return json.loads(p.read_text(encoding="utf-8"))
def req(c:bool,m:str)->None:
    if not c:raise RuntimeError(m)
def bound(raw:str)->Path:
    p=Path(raw);return p if p.is_absolute() else ROOT/p
def atomic(p:Path,x:dict[str,Any])->None:
    p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+".tmp");t.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8");os.replace(t,p)

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--contract",type=Path,required=True);ap.add_argument("--preflight",type=Path,required=True);ap.add_argument("--review",type=Path,required=True);ap.add_argument("--fresh-identity",type=Path,required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args()
    req(not a.output.exists(),"R3 recovery authorization already exists")
    c,p,r,i=load(a.contract),load(a.preflight),load(a.review),load(a.fresh_identity);csha=sha(a.contract)
    req(c["status"]==CONTRACT_STATUS,"R3 recovery contract not frozen")
    req(p["status"]==PREFLIGHT_STATUS and p["contract_sha256"]==csha,"R3 preflight not passing/bound")
    req(p["provider_calls"]==0 and p["scientific_execution"] is False and p["support_inspected"] is False,"R3 preflight crossed science boundary")
    req(p["provider_execution_task_count"]==158 and p["planned_task_count"]==160,"R3 preflight geometry drift")
    for key in ("parent_incident_binding_pass","matched_censor_binding_pass","provider_manifest_pass","opportunity_geometry_pass","actor_scope_guards_pass","runner_compile_pass","adjudicator_compile_pass","stage_b_order_7_8_pass"):
        req(p["checks"].get(key) is True,f"R3 preflight check missing: {key}")
    req(r["status"]=="COMPLETED" and r["surface"]=="ChatGPT web" and r["model"]=="GPT-5.6 Sol","R3 independent review provenance drift")
    req(r["verdict"]==REVIEW_VERDICT and r["execution_recommendation"]=="ALLOW_SEPARATE_R3_RECOVERY_AUTHORIZATION","R3 independent review not executable PASS")
    req(r["contract_sha256_acknowledged"]==csha and r["remaining_blockers"]==[],"R3 independent review contract/blocker drift")
    req(r["stage_b_authority"] is False and r["scientific_authority"] is False,"R3 review authority overbroad")
    ct=datetime.fromisoformat(c["created_at_utc"]);rt=datetime.fromisoformat(r["created_at_utc"])
    req(rt>ct,"R3 independent review must follow contract freeze")
    req(i["status"]=="PASS_CURRENT_REVIEW_TRANCHE","fresh R3 identity not passing")
    row=i["requested_and_resolved"]["deepseek-v4-pro"]
    req(row["resolved"]=="deepseek-v4-pro-ga-260813" and row["thinking"]=="disabled" and int(row["provider_retry_limit"])==0,"fresh R3 identity drift")
    it=datetime.fromisoformat(i["created_at_utc"]);req(it>rt,"fresh R3 identity must be qualified after exact-hash preexecution review")

    ex=c["exact_once_acquisition"];mp=bound(ex["unit_manifest_path"]);req(mp.is_file() and sha(mp)==ex["unit_manifest_sha256"],"R3 provider manifest drift")
    tasks=[str(x) for x in load(mp)["ordered_task_ids"]];req(len(tasks)==len(set(tasks))==158,"R3 provider universe must be 158 unique tasks")
    req(BURNED not in tasks and CENSOR not in tasks,"excluded task leaked into R3 provider universe")
    om=c["recovery_opportunity_manifest"];op=bound(om["path"]);req(op.is_file() and sha(op)==om["sha256"],"R3 opportunity manifest drift")
    opp=load(op);req(len(opp["provider_task_ids_by_stream"]["stv3-cgwb-00"])==7 and len(opp["provider_task_ids_by_stream"]["stv3-cgwp-00"])==7,"R3 matched opportunity geometry drift")
    req(not Path(c["run_root"]).exists() and not Path(c["global_lease_path"]).exists(),"R3 recovery lineage already exists")

    authority={"stage_a_provider_execution":True,"stage_b_learning_execution":False,"updater":False,"heldout_evaluation":False,"analyzer":False,"second_backbone":False,"public_benchmark":False,"paper_promotion":False,"submission":False}
    payload={
      "schema_version":"1.0","artifact_type":"e2-r17-semantic-transfer-v3-stage-a-r3-recovery-authorization","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY",
      "contract_path":str(a.contract),"contract_sha256":csha,"preflight_path":str(a.preflight),"preflight_sha256":sha(a.preflight),
      "independent_review":{"path":str(a.review),"sha256":sha(a.review),"surface":r["surface"],"model":r["model"],"thinking_level":r["thinking_level"],"verdict":r["verdict"]},
      "fresh_model_identity":{"path":str(a.fresh_identity),"sha256":sha(a.fresh_identity),"status":i["status"],"created_at_utc":i["created_at_utc"],"requested_model":"deepseek-v4-pro","resolved_model":row["resolved"]},
      "single_use":True,"exactly_once":True,"automatic_retry":False,"authority":authority,
      "execution_scope":{"recovery_mode":"MATCHED_CENSOR_158","allowed_modes":["e1"],"allowed_task_ids":tasks,"exact_k":8,"exact_prefix_ks":[1,2,4,8],"exact_concurrency":c["actor"]["concurrency"],"required_run_root":c["run_root"],"runner_lease_required":True,"allow_noninitial_skill":False,"required_skill_pre_sha256":c["mindmemos"]["initial_skill_sha256"],"required_resolved_model":"deepseek-v4-pro-ga-260813","identity_artifact_sha256":sha(a.fresh_identity),"suite_manifest_sha256":c["suite"]["suite_manifest_sha256"],"split_manifest_sha256":c["suite"]["split_manifest_sha256"],"max_turns":c["actor"]["max_turns"],"max_output_tokens":c["actor"]["max_output_tokens"],"provider_budget":{"required":True,"total_limit":c["budget"]["max_provider_calls"],"per_unit_limit":c["budget"]["provider_calls_per_rollout_limit"]},"exact_once_acquisition":{"required":True,"unit_manifest_path":ex["unit_manifest_path"],"unit_manifest_sha256":ex["unit_manifest_sha256"],"unit_count":158,"required_claim_root":ex["claim_root"],"attempt_before_any_provider_io":True,"replay_allowed":False,"ambiguous_recollection_allowed":False},"global_lease_path":c["global_lease_path"],"recovery_exceptions":{"terminal_technical_missing":BURNED,"matched_no_provider_censor":CENSOR,"matched_censor_provider_calls":0,"replacement_allowed":False,"additional_attempted_but_unsealed_policy":"STOP"}},
      "interpretation_boundary":"Single-use authority for the 158-task R3 Stage-A matched-censor recovery only. No support read, updater, heldout, Stage B, public benchmark, or paper claim is authorized. Any additional attempted-but-unsealed recovery unit causes STOP."
    }
    atomic(a.output,payload);print(json.dumps({"status":payload["status"],"contract_sha256":csha,"allowed_tasks":158,"authority":authority},ensure_ascii=False,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())

```

## 8. Audit questions

A. **Scientific equivalence.** Does the parent/child equality plus the shown adjudicator diff support the claim that R3B changes only support-read authority/control flow, not the provider task universe, search K, opportunity geometry, support threshold, mixed-pool algorithm, treated-pool selector, reduction routers, or Stage-B scientific object?

B. **Direct-bypass closure.** Does requiring and validating both the exact support-read authorization and canonical O_EXCL consumption marker inside the adjudicator itself close the R1 direct-invocation bypass before any `pool_k8.json` semantic parse occurs?

C. **End-to-end provenance.** Do minter, gate, and adjudicator now adequately bind the exact future control-review receipt and exact minter/gate/adjudicator hashes so a merely permit-shaped JSON cannot pass the reviewed route?

D. **Single-use semantics.** Is consumption-before-read fail-closed? Are rc=0 PASS and rc=3 HOLD the only valid terminal returns, with unexpected rc permanently consuming the permit and requiring manual review?

E. **Minter structural-only boundary.** Does the minter still avoid scientific support inspection, using pool bytes only for seal/hash lineage verification?

F. **Provider recovery compatibility.** Can the unchanged R3 recovery authorizer/runner safely operate on the R3B contract after this review PASS and a fresh post-review identity, given that the contract status/run root/task universe remain unchanged and the runner verifies all bound-code hashes before provider I/O?

G. **Tests/preflight.** Do 9/9 zero-provider tests and both preflights cover the two prior verdict-changing control-plane blockers sufficiently? Do not request extra workload for appearance.

H. **Authority consequence.** If PASS, is it valid to allow only the *separate recovery-authorization minting step* after the Sep-7 reset and fresh identity, while actual support-read permit remains impossible until the exact terminal 158-pool summary exists? Stage B must remain false.

## 9. Required synthesis

Return exactly these fields before the final token:

- `contract_sha256_acknowledged`: exact R3B contract SHA
- `recovery_preflight_sha256_acknowledged`: exact recovery preflight SHA
- `support_guard_preflight_sha256_acknowledged`: exact support-guard preflight SHA
- `control_plane_revision`: `R3B_POST_TERMINAL_SUPPORT_GUARD`
- `minter_sha256_acknowledged`: exact minter SHA
- `gate_sha256_acknowledged`: exact gate SHA
- `support_adjudicator_sha256_acknowledged`: exact guarded adjudicator SHA
- `scientific_equivalence_to_parent_r3`: PASS/FAIL
- `direct_bypass_closed`: PASS/FAIL
- `review_provenance_closed`: PASS/FAIL
- `single_use_gate`: PASS/FAIL
- `minter_structural_only`: PASS/FAIL
- `provider_recovery_authority_affected`: true/false
- `r3_contract_redesign_required`: true/false
- `new_scientific_experiment_required`: true/false
- `stage_b_authority`: false
- `scientific_authority`: false
- `support_control_verdict`: `PASS_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE` or `FAIL_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE`
- `execution_recommendation`: `ALLOW_SEPARATE_R3_RECOVERY_AUTHORIZATION` or `DO_NOT_AUTHORIZE_R3B_RECOVERY`
- `remaining_blockers`: [] or exact blockers

Then end with exactly one provider-recovery verdict token from Section 0.
