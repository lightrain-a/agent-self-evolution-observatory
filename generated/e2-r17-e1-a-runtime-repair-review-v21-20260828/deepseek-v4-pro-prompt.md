You are an independent adversarial pre-execution reviewer for E2-R17 E1-A V2.1. You are blind to the other reviewer. This review has zero execution authority by itself. It may at most recommend minting a separately SHA-bound E1-A pool-generation authorization. It cannot authorize E1-B updater calls, held-out future-skill evaluation, paper claims, frontend promotion, or submission.

Reviewer endpoint: deepseek-v4-pro
Exact V2.1 draft contract SHA-256: 34bb95012dac2c7efc186d0ab9a4839efeddd21b2179b086fb38c49e48dd9fec

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
{
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
    {
      "priority": "P0|P1",
      "issue": "",
      "why_blocking": "",
      "exact_repair": ""
    }
  ],
  "nonblocking_notes": [
    ""
  ],
  "e1_a_recommendation": "ALLOW_SEPARATE_FROZEN_E1_A_AUTHORIZATION|HOLD|STOP",
  "e1_b_recommendation": "HOLD|STOP",
  "paper_claim_authority": false,
  "single_sentence_verdict": ""
}

Set both `draft_contract_sha256_acknowledged` and `repair_sha256_acknowledged` exactly to the SHA above. Keep `paper_claim_authority` false.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START

===== BOUND ARTIFACT: e1_a_v21_draft_contract | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-pool-support-v2-1-draft-contract-20260828.json =====
{
  "actor": {
    "concurrency": 4,
    "max_output_tokens": 4096,
    "max_turns": 10,
    "provider_retry_limit": 0,
    "requested_model": "deepseek-v4-pro",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "search_topology": "parallel_best_of_k",
    "temperature": 0,
    "thinking": "disabled"
  },
  "artifact_type": "e2-r17-e1-a-pool-support-contract",
  "authority": {
    "execute_e1_a": false,
    "execute_e1_b": false,
    "independent_preexecution_review": true,
    "paper_promotion": false,
    "provider_runtime_updater_pilot": false,
    "submission": false
  },
  "authorization_scope_required": {
    "allow_noninitial_skill": false,
    "allowed_modes": [
      "e1"
    ],
    "allowed_task_ids": "exact 96 task IDs from the bound e1_update_streams split",
    "authority.e1_a": true,
    "authority.e1_b": false,
    "authority.scientific_experiment": true,
    "exact_k": 8,
    "identity_artifact_sha256": "7fb73c09bc96288438989f4b773abbe3bcb37c43d150b78a9c66da80d1b66ae4",
    "max_output_tokens": 4096,
    "max_turns": 10,
    "provider_budget": {
      "claim_before_provider_io": true,
      "claims_never_released": true,
      "ledger_relative_path": "checkpoints/provider_budget.sqlite3",
      "per_unit_limit": 10,
      "required": true,
      "total_limit": 7680
    },
    "required_resolved_model": "deepseek-v4-pro-ga-260813",
    "required_skill_pre_sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb",
    "runtime_freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "runtime_python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "runtime_qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "status": "AUTHORIZED_E1",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4"
  },
  "bound_code": {
    "actor_pool": {
      "path": "research_pipeline/e2_r17_actor_pool.py",
      "sha256": "ade5f605f32056b7797dbcbcb7b3e839b9c18dce1c0f287f609d86cee3463ef4"
    },
    "actor_runner": {
      "path": "scripts/run_e2_r17_actor_pool.py",
      "sha256": "20a81fbe06f3839cd17babfdb021407368493da61610bca33aae33df8d31ec14"
    },
    "ark_plan_react": {
      "path": "research_pipeline/e2_r17_ark_plan_react.py",
      "sha256": "7a7a9c40774429ac3c9a7c8c003bbc46628a6ef574bd481e628668894e803fba"
    },
    "authority_scope_test": {
      "path": "research_pipeline/test_e2_r17_actor_authority_scope.py",
      "sha256": "4c383aed93bb4d20d0726bc02c3fbba72baead62cc55838850b4f12061b2a1a0"
    },
    "e1_a_orchestrator": {
      "path": "scripts/run_e2_r17_e1_a_pool_support.py",
      "sha256": "24ea070b08399d48af99294615a508874f851af941f5bb0efabe341b0854617d"
    },
    "provider_budget_ledger": {
      "path": "research_pipeline/e2_r17_provider_budget.py",
      "sha256": "df819b30a31e62e007e3f85ae76aa8d06faefaa56e9acefe71ceadb9f8fce444"
    },
    "provider_budget_tests": {
      "path": "research_pipeline/test_e2_r17_provider_budget.py",
      "sha256": "443b0377941a4fbba1a6eaf7fa5af8e33615511b43890bd73da19a8ec94b61eb"
    },
    "search_projection_runner": {
      "path": "research_pipeline/e2_r17_search_projection_runner.py",
      "sha256": "91f5545fe6def937ddee231e71295cc2539bfbb6ea1cf8292f8daef81b4272bc"
    },
    "support_adjudicator": {
      "path": "scripts/adjudicate_e2_r17_e1_a_pool_support.py",
      "sha256": "9972296dfc140a3cbd29bc6f475dddb46822353a1f9ae56b5f5b243c13b722ea"
    }
  },
  "budget": {
    "actor_rollouts_exact": 768,
    "claim_semantics": "transactional claim before provider generation I/O; claims are never released after error/crash",
    "duplicate_completed_rollout_calls": 0,
    "fail_closed_pre_io": true,
    "ledger_relative_path": "checkpoints/provider_budget.sqlite3",
    "max_output_tokens_per_provider_call": 4096,
    "max_provider_calls": 7680,
    "provider_retry_limit": 0,
    "theoretical_max_output_tokens": 31457280,
    "updater_calls": 0
  },
  "checkpoint": {
    "blind_relaunch_after_timeout_or_502": false,
    "exclusive_lock": ".exclusive.lock",
    "leave_lock_on_failure_for_manual_inspection": true,
    "resume_missing_only": true,
    "revalidate_completed_stream_and_rollout_sha_before_resume": true,
    "stream_manifest": "checkpoints/completed_streams.jsonl",
    "stream_summary": "summary/streams/<stream>.json",
    "unit_level_pool_freeze": "cases/<task>/pool_k{1,2,4,8}.json",
    "unit_level_rollout_refs": "cases/<task>/rollout_<i>/r17_trajectory_ref.json"
  },
  "date": "2026-08-28",
  "forbidden_during_e1_a": [
    "updater calls",
    "MRW/WIN/RB-AGG skill updates",
    "held-out future-skill evaluation",
    "method-effectiveness selection",
    "task replacement or dropping after mixed-pool support is observed",
    "changing K/model/skill/prompt/verifier after launch",
    "paper promotion",
    "automatic E1-B authority inheritance"
  ],
  "mindmemos": {
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "initial_skill_sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb",
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817",
    "skill_mutation_allowed": false
  },
  "model_identity": {
    "path": "generated/e2-r17-e1-a-v2-1-model-identity-adjudication-20260828.json",
    "qualification_path": "generated/e2-r17-e1-a-v2-1-model-identity-qualification-20260828.json",
    "qualification_sha256": "08982d439f46bea48b73d1dc09d7af1504eda5ba725738bcf4d785a2fa32fa54",
    "sha256": "7fb73c09bc96288438989f4b773abbe3bcb37c43d150b78a9c66da80d1b66ae4",
    "status": "PASS_CURRENT_REVIEW_TRANCHE"
  },
  "parent_review_summary": {
    "decision": "REVISE_ONE_P0_PROVIDER_BUDGET_GUARD",
    "path": "generated/e2-r17-e1-a-preexecution-review-20260828/summary.json",
    "sha256": "5bc47a53a56fa2a11d0e715c9d1c7131aacb045084266a259ff55090eb52071c"
  },
  "parent_runtime_failure": {
    "path": "generated/e2-r17-e1-a-v2-runtime-failure-adjudication-20260828.json",
    "sha256": "3ad8b73ce13f8b5bc0e51f109a8e910e0894656d3bdd94f10290126a3388a399",
    "status": "TECHNICAL_FAILURE_ZERO_PROVIDER_ZERO_SCIENTIFIC_OUTCOME"
  },
  "parents": {
    "v3_1_mechanical_adjudication": {
      "path": "generated/e2-r17-v3-1-mechanical-pilot-adjudication-20260828.json",
      "sha256": "9b02d870f808c5f61e42b87b9bf09c8028192207267ef56bf65f40fa988b3a10",
      "status": "PASS_MECHANICAL_ONLY_NO_E1_AUTHORITY"
    },
    "v3_plan": {
      "path": "generated/e2-r17-experiment-plan-v3-20260828.json",
      "sha256": "b1a0224117f161ead9fccefa2c22a0f01dfa1d9e72ca1e98107418f21e3e04c5"
    }
  },
  "post_run": {
    "adjudicator": "scripts/adjudicate_e2_r17_e1_a_pool_support.py",
    "if_primary_support_fail": "STOP_E1_BEFORE_UPDATER",
    "if_primary_support_pass": "may prepare a separate immutable E1-B contract; E1-B remains unauthorized until separately reviewed",
    "primary_support_pass": "mixed>=24/96 AND exposed_streams>=8/12 where each exposed stream has >=2 mixed pools",
    "runner_status": "COMPLETED_ALL_96_POOLS_PENDING_SEPARATE_SUPPORT_ADJUDICATION"
  },
  "repair_tests": {
    "command": "python3 -m unittest research_pipeline.test_e2_r17_provider_budget research_pipeline.test_e2_r17_ark_plan_react research_pipeline.test_e2_r17_search_projection_runner research_pipeline.test_e2_r17_actor_authority_scope",
    "eleventh_call_pre_io_blocked": true,
    "global_7681st_call_pre_io_blocked": true,
    "provider_io_used": false,
    "status": "PASS_21_TESTS"
  },
  "revision": "V2_1_EXPLICIT_FROZEN_RUNTIME_BINDING",
  "run_root": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-1-20260828",
  "runtime": {
    "ambient_sys_executable_for_actor_forbidden": true,
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt",
    "freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "qualification_path": "generated/e2-r17-runtime-dependency-qualification-r2-20260828.json",
    "qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "required_imports": [
      "pydantic",
      "openpyxl==3.1.5",
      "mindmemos_eval.skills.agents.ReactAgentFactory",
      "mindmemos_eval.skills.envs.spreadsheetbench.env.SpreadsheetBenchEnv"
    ],
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv"
  },
  "schema_version": "1.0",
  "scientific_role": "PRE_TREATMENT_SUPPORT_AND_POOL_FREEZE_ONLY",
  "scientific_units": {
    "actor_rollouts": 768,
    "heldout_future_skill_evaluations": 0,
    "nested_prefixes": [
      1,
      2,
      4,
      8
    ],
    "search_k": 8,
    "streams": 12,
    "tasks_per_stream": 8,
    "unique_update_tasks": 96,
    "updater_calls": 0
  },
  "status": "DRAFT_V2_1_PENDING_INDEPENDENT_PREEXECUTION_REVIEW",
  "streams": [
    "e1-agj-00",
    "e1-agj-01",
    "e1-fmv-00",
    "e1-fmv-01",
    "e1-ioc-00",
    "e1-ioc-01",
    "e1-msp-00",
    "e1-msp-01",
    "e1-ska-00",
    "e1-ska-01",
    "e1-tsr-00",
    "e1-tsr-01"
  ],
  "suite": {
    "metadata_sha256": "12d6eb876e2a230e7990be3e61fed108d45f6ddec00bac5c9b88585a04111b04",
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2",
    "split_is_outcome_blind": true,
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4",
    "task_replacement_after_support_observation": false
  },
  "support_gate": {
    "borderline_is_failure": true,
    "evaluate_only_after_all_96_k8_pools_are_frozen": true,
    "exposed_stream_minimum": 8,
    "family_gate_controls_primary_e1_b": false,
    "hard_gate_failure": "STOP_E1_BEFORE_ANY_UPDATER_CALL",
    "mixed_pool_count_minimum": 24,
    "mixed_pool_total": 96,
    "mixed_pools_per_exposed_stream_minimum": 2,
    "replace_or_drop_tasks_after_support_observation": false,
    "rounding_or_waiver": false,
    "stream_total": 12,
    "supported_families_minimum": 4
  },
  "technical_repair_gate": {
    "VIRTUAL_ENV_and_PATH_must_bind_contract_venv": true,
    "actor_must_spawn_with_contract_runtime_python": true,
    "failed_v2_provider_budget_claims": 0,
    "failed_v2_root_must_remain_untouched": true,
    "failed_v2_stale_lock_must_remain": true,
    "fresh_run_root_required": true,
    "runtime_import_smoke_before_actor_spawn": true
  }
}


===== BOUND ARTIFACT: failed_v2_runtime_adjudication | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-v2-runtime-failure-adjudication-20260828.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-e1-a-runtime-failure-adjudication",
  "date": "2026-08-28",
  "status": "TECHNICAL_FAILURE_ZERO_PROVIDER_ZERO_SCIENTIFIC_OUTCOME",
  "failed_contract": {
    "path": "generated/e2-r17-e1-a-pool-support-v2-contract-20260828.json",
    "sha256": "e886abe909ef73873f4d7a808157a580c13de9ed052668f7fb77b8157583fc9e"
  },
  "failed_authorization": {
    "path": "generated/e2-r17-e1-a-pool-support-v2-authorization-20260828.json",
    "sha256": "f82d993589ad82629475f12285e3df0ad2bfc5af7f68971bb22df25bdbe95024"
  },
  "failed_run_root": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-20260828",
  "failure_receipt": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-20260828/checkpoints/failures/e1-agj-00.json",
  "diagnosis": "The E1-A orchestrator spawned the actor with ambient sys.executable (/usr/bin/python3) instead of the previously qualified MindMemOS virtual environment. Import failed at mindmemos_sdk -> pydantic before actor rollout execution.",
  "observed": {
    "active_r17_process_after_failure": false,
    "completed_streams": 0,
    "completed_trajectory_refs": 0,
    "provider_budget_claims": 0,
    "provider_calls": 0,
    "new_actor_rollouts": 0,
    "mixed_or_rescue_support_inspected": false,
    "updater_calls": 0,
    "future_skill_evaluations": 0,
    "scientific_effectiveness_evaluated": false,
    "stale_lock_preserved": true
  },
  "runtime_evidence": {
    "qualified_venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv",
    "qualified_venv_python": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "runtime_freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt",
    "runtime_freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "runtime_qualification_path": "generated/e2-r17-runtime-dependency-qualification-r2-20260828.json",
    "runtime_qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "fresh_import_smoke": "PASS",
    "pydantic_in_qualified_venv": "2.13.4",
    "openpyxl_in_qualified_venv": "3.1.5"
  },
  "adjudication": "This is a pre-provider runtime-binding failure, not a scientific negative result. The failed V2 run root, ledger, failure receipt, and stale lock must remain untouched. The exact V2 authorization is not retryable after code/runtime repair. A fresh V2.1 contract and authorization on a fresh run root are required.",
  "authority": {
    "repair_runtime_binding": true,
    "prepare_fresh_e1_a_contract": true,
    "execute_failed_v2_contract": false,
    "execute_e1_b": false,
    "paper_promotion": false,
    "submission": false
  }
}


===== BOUND ARTIFACT: prior_v2_dual_review | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-preexecution-review-v2-20260828/summary.json =====
{
  "all_allow_separate_e1_a_authorization": true,
  "all_completed": true,
  "artifact_type": "e2-r17-e1-a-dual-preexecution-review-summary",
  "created_at_utc": "2026-08-28T14:12:44+00:00",
  "draft_contract_sha256": "79192371199a07bcfdf79227a0d12f9f9955f715576f73fe55122549a3dd3012",
  "e1_a_recommendations": {
    "deepseek-v4-pro": "ALLOW_SEPARATE_FROZEN_E1_A_AUTHORIZATION",
    "kimi-k3": "ALLOW_SEPARATE_FROZEN_E1_A_AUTHORIZATION"
  },
  "e1_b_recommendations": {
    "deepseek-v4-pro": "HOLD",
    "kimi-k3": "HOLD"
  },
  "exposed_to_other_review": false,
  "independent": true,
  "paper_claim_authority": false,
  "resolved_models": {
    "deepseek-v4-pro": "deepseek-v4-pro-ga-260813",
    "kimi-k3": "kimi-k3"
  },
  "schema_version": "1.0",
  "scientific_authority": false,
  "statuses": {
    "deepseek-v4-pro": "COMPLETED",
    "kimi-k3": "COMPLETED"
  },
  "verdicts": {
    "deepseek-v4-pro": "PASS_TO_SEPARATELY_BOUND_E1_A_AUTHORIZATION",
    "kimi-k3": "PASS_TO_SEPARATELY_BOUND_E1_A_AUTHORIZATION"
  }
}


===== BOUND ARTIFACT: runtime_qualification | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-runtime-dependency-qualification-r2-20260828.json =====
{
  "artifact_type": "e2-r17-runtime-dependency-qualification",
  "authority": {
    "e0_full": false,
    "e0_pilot": false,
    "e1": false,
    "front_end_claim": false,
    "paper_promotion": false,
    "public_externality": false,
    "scientific_experiment": false,
    "submission": false
  },
  "created_at_utc": "2026-08-28T04:13:26+00:00",
  "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt",
  "freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
  "import_smoke": {
    "imports": [
      "mindmemos_eval.skills.agents.ReactAgentFactory",
      "mindmemos_eval.skills.envs.spreadsheetbench.env.SpreadsheetBenchEnv"
    ],
    "status": "PASS"
  },
  "installed_distribution_count": 69,
  "mindmemos_uv_lock_path": "/data/wyt/evidence-substrates/MindMemOS-20260817/uv.lock",
  "mindmemos_uv_lock_sha256": "867495f270aa3c44d7f0409feb03a8838642f7f1eb6b3552ae79e837ec164cae",
  "pilot_case_preflight": {
    "pilot_manifest_path": "generated/e2-r17-e0-pilot-manifest-20260828.json",
    "pilot_manifest_sha256": "e6653ee7cd2d7391b555086adb1a9d2bf660a7df25455f8c0215b35fa85b893f",
    "provider_calls": 0,
    "status": "PASS",
    "task_count": 12,
    "task_execution": false
  },
  "private_credentials_included": false,
  "provider_calls": 0,
  "python_executable": "/usr/bin/python3.12",
  "python_version": "3.12.3",
  "raw_response_ids_included": false,
  "repair_trigger_path": "generated/e2-r17-e0-pilot-launch-failure-r1-20260828.json",
  "schema_version": "2.0",
  "scientific_outcome": false,
  "status": "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2",
  "supersedes": "generated/e2-r17-runtime-dependency-qualification-20260828.json",
  "tests": {
    "errors": 0,
    "failed": 0,
    "passed": 28,
    "status": "PASS",
    "suites": [
      "search_projection_theory",
      "search_projection_runner",
      "controlled_spreadsheet_suite",
      "ark_plan_react",
      "mindmemos_ark_adapter"
    ]
  },
  "uv_executable": "/data/wyt/e2-r17-search-projection/uv-bootstrap/bin/uv",
  "uv_sync_command": "UV_PROJECT_ENVIRONMENT=<venv> uv sync --project <MindMemOS> --package mindmemos-eval --frozen --no-dev --python /usr/bin/python3.12",
  "uv_version": "0.12.7",
  "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv"
}


===== BOUND ARTIFACT: runtime_freeze | /data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt =====
-e file:///data/wyt/evidence-substrates/MindMemOS-20260817/src/mindmemos_eval
-e file:///data/wyt/evidence-substrates/MindMemOS-20260817/src/mindmemos_sdk
absl-py==2.4.0
aiohappyeyeballs==2.6.2
aiohttp==3.14.1
aiosignal==1.4.0
annotated-doc==0.0.4
annotated-types==0.7.0
anyio==4.13.0
attrs==26.1.0
certifi==2026.5.20
charset-normalizer==3.4.7
click==8.4.1
datasets==5.0.0
dill==0.4.1
distro==1.9.0
et-xmlfile==2.0.0
filelock==3.29.4
frozenlist==1.8.0
fsspec==2026.4.0
grpcio==1.81.1
h11==0.16.0
h2==4.3.0
hf-xet==1.5.1
hpack==4.1.0
httpcore==1.0.9
httpx==0.28.1
huggingface-hub==1.19.0
hyperframe==6.1.0
idna==3.18
jiter==0.15.0
joblib==1.5.3
markdown-it-py==4.2.0
mdurl==0.1.2
multidict==6.7.1
multiprocess==0.70.19
neo4j==6.2.0
nltk==3.9.4
numpy==2.4.6
openai==2.41.1
openpyxl==3.1.5
packaging==26.2
pandas==3.0.3
portalocker==3.2.0
propcache==0.5.2
protobuf==6.33.6
pyarrow==24.0.0
pydantic-core==2.46.4
pydantic==2.13.4
pygments==2.20.0
python-dateutil==2.9.0.post0
pytz==2026.2
pyyaml==6.0.3
qdrant-client==1.18.0
regex==2026.5.9
requests==2.34.2
rich==15.0.0
rouge-score==0.1.2
shellingham==1.5.4
six==1.17.0
sniffio==1.3.1
tiktoken==0.13.0
tqdm==4.68.2
typer==0.25.1
typing-extensions==4.15.0
typing-inspection==0.4.2
urllib3==2.7.0
xxhash==3.7.0
yarl==1.24.2


===== BOUND ARTIFACT: provider_budget_ledger | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/e2_r17_provider_budget.py =====
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Any


SCHEMA_VERSION = "1.0"


class ProviderBudgetExceeded(RuntimeError):
    """Raised before provider I/O when a frozen call ceiling would be exceeded."""


class ProviderBudgetBindingError(RuntimeError):
    """Raised when a persisted ledger does not match the frozen execution binding."""


@dataclass(frozen=True)
class ProviderBudgetClaim:
    claim_id: int
    unit_id: str
    unit_call_index: int
    total_claimed_after: int
    per_unit_limit: int
    total_limit: int
    claimed_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProviderBudgetSnapshot:
    ledger_path: str
    contract_sha256: str
    authorization_sha256: str
    total_limit: int
    per_unit_limit: int
    total_claimed: int
    unit_claimed: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ProviderBudgetLedger:
    """SQLite-backed fail-closed provider-call budget ledger.

    A claim is committed transactionally *before* provider I/O. Claims are never
    released, even when the subsequent provider request errors or the process
    crashes. This deliberately over-counts ambiguous calls so a resume cannot
    reset or reuse budget that may already have reached the provider.

    SQLite ``BEGIN IMMEDIATE`` serializes concurrent claims from the per-stream
    actor workers. The ledger is bound to one exact contract/authorization pair
    and fixed global/per-unit limits; any drift fails closed.
    """

    def __init__(
        self,
        *,
        path: Path,
        contract_sha256: str,
        authorization_sha256: str,
        total_limit: int,
        per_unit_limit: int,
        allow_create: bool,
    ) -> None:
        if total_limit <= 0 or per_unit_limit <= 0:
            raise ValueError("provider budget limits must be positive")
        self.path = Path(path)
        self.contract_sha256 = str(contract_sha256)
        self.authorization_sha256 = str(authorization_sha256)
        self.total_limit = int(total_limit)
        self.per_unit_limit = int(per_unit_limit)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        existed = self.path.exists()
        if not existed and not allow_create:
            raise ProviderBudgetBindingError(f"provider budget ledger does not exist: {self.path}")
        self._initialize_or_validate(allow_create=allow_create)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.path), timeout=30.0, isolation_level=None)
        connection.execute("PRAGMA busy_timeout=30000")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _initialize_or_validate(self, *, allow_create: bool) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS claims (
                    claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id TEXT NOT NULL,
                    unit_call_index INTEGER NOT NULL,
                    claimed_at_utc TEXT NOT NULL,
                    UNIQUE(unit_id, unit_call_index)
                )
                """
            )
            current = dict(connection.execute("SELECT key, value FROM metadata").fetchall())
            expected = {
                "schema_version": SCHEMA_VERSION,
                "contract_sha256": self.contract_sha256,
                "authorization_sha256": self.authorization_sha256,
                "total_limit": str(self.total_limit),
                "per_unit_limit": str(self.per_unit_limit),
            }
            if not current:
                if not allow_create:
                    connection.execute("ROLLBACK")
                    raise ProviderBudgetBindingError("refusing to initialize missing provider budget metadata on resume")
                connection.executemany(
                    "INSERT INTO metadata(key, value) VALUES (?, ?)", expected.items()
                )
            elif current != expected:
                connection.execute("ROLLBACK")
                raise ProviderBudgetBindingError(
                    f"provider budget binding drift: observed={current!r}; expected={expected!r}"
                )
            connection.execute("COMMIT")

    def claim(self, unit_id: str) -> ProviderBudgetClaim:
        unit_id = str(unit_id)
        if not unit_id:
            raise ValueError("provider budget unit_id is required")
        claimed_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            metadata = dict(connection.execute("SELECT key, value FROM metadata").fetchall())
            expected = {
                "schema_version": SCHEMA_VERSION,
                "contract_sha256": self.contract_sha256,
                "authorization_sha256": self.authorization_sha256,
                "total_limit": str(self.total_limit),
                "per_unit_limit": str(self.per_unit_limit),
            }
            if metadata != expected:
                connection.execute("ROLLBACK")
                raise ProviderBudgetBindingError("provider budget metadata drift before claim")
            total_claimed = int(connection.execute("SELECT COUNT(*) FROM claims").fetchone()[0])
            unit_claimed = int(
                connection.execute("SELECT COUNT(*) FROM claims WHERE unit_id=?", (unit_id,)).fetchone()[0]
            )
            if total_claimed >= self.total_limit:
                connection.execute("ROLLBACK")
                raise ProviderBudgetExceeded(
                    f"provider total call budget exhausted before I/O: {total_claimed}/{self.total_limit}"
                )
            if unit_claimed >= self.per_unit_limit:
                connection.execute("ROLLBACK")
                raise ProviderBudgetExceeded(
                    f"provider per-unit call budget exhausted before I/O: unit={unit_id}; "
                    f"{unit_claimed}/{self.per_unit_limit}"
                )
            unit_call_index = unit_claimed + 1
            cursor = connection.execute(
                "INSERT INTO claims(unit_id, unit_call_index, claimed_at_utc) VALUES (?, ?, ?)",
                (unit_id, unit_call_index, claimed_at),
            )
            claim_id = int(cursor.lastrowid)
            connection.execute("COMMIT")
        return ProviderBudgetClaim(
            claim_id=claim_id,
            unit_id=unit_id,
            unit_call_index=unit_call_index,
            total_claimed_after=total_claimed + 1,
            per_unit_limit=self.per_unit_limit,
            total_limit=self.total_limit,
            claimed_at_utc=claimed_at,
        )

    def snapshot(self) -> ProviderBudgetSnapshot:
        with self._connect() as connection:
            metadata = dict(connection.execute("SELECT key, value FROM metadata").fetchall())
            expected = {
                "schema_version": SCHEMA_VERSION,
                "contract_sha256": self.contract_sha256,
                "authorization_sha256": self.authorization_sha256,
                "total_limit": str(self.total_limit),
                "per_unit_limit": str(self.per_unit_limit),
            }
            if metadata != expected:
                raise ProviderBudgetBindingError("provider budget metadata drift while reading snapshot")
            total_claimed = int(connection.execute("SELECT COUNT(*) FROM claims").fetchone()[0])
            unit_rows = connection.execute(
                "SELECT unit_id, COUNT(*) FROM claims GROUP BY unit_id ORDER BY unit_id"
            ).fetchall()
        return ProviderBudgetSnapshot(
            ledger_path=str(self.path),
            contract_sha256=self.contract_sha256,
            authorization_sha256=self.authorization_sha256,
            total_limit=self.total_limit,
            per_unit_limit=self.per_unit_limit,
            total_claimed=total_claimed,
            unit_claimed={str(unit_id): int(count) for unit_id, count in unit_rows},
        )

    def assert_completed_receipts_covered(self, completed_receipt_counts: dict[str, int]) -> None:
        snapshot = self.snapshot()
        for unit_id, observed_receipts in completed_receipt_counts.items():
            claimed = int(snapshot.unit_claimed.get(str(unit_id), 0))
            if claimed < int(observed_receipts):
                raise ProviderBudgetBindingError(
                    f"persisted provider receipts exceed budget claims: unit={unit_id}; "
                    f"receipts={observed_receipts}; claims={claimed}"
                )


__all__ = [
    "ProviderBudgetBindingError",
    "ProviderBudgetClaim",
    "ProviderBudgetExceeded",
    "ProviderBudgetLedger",
    "ProviderBudgetSnapshot",
    "SCHEMA_VERSION",
]


===== BOUND ARTIFACT: ark_plan_react | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/e2_r17_ark_plan_react.py =====
from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings
from research_pipeline.e2_r17_provider_budget import ProviderBudgetClaim, ProviderBudgetLedger

PLAN_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_sha(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _sha_text(raw)


def _responses_tools(chat_tools: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in chat_tools or []:
        if item.get("type") != "function":
            raise ValueError("E2-R17 actor accepts function tools only")
        function = item.get("function") or {}
        name = str(function.get("name") or "")
        if not name:
            raise ValueError("tool function name is required")
        out.append(
            {
                "type": "function",
                "name": name,
                "description": str(function.get("description") or ""),
                "parameters": function.get("parameters") or {"type": "object", "properties": {}},
            }
        )
    return out


def _render_messages(messages: list[dict[str, Any]]) -> str:
    """Render a tool-use transcript without dropping role or call identity.

    Ark Plan's Responses endpoint accepts a text input plus native tools.  The
    first-party MindMemOS ReAct loop stores Chat-Completions-shaped messages, so
    this adapter serializes the complete conversation deterministically on every
    turn.  Tool calls and tool outputs remain explicitly paired by call id.
    """

    chunks: list[str] = [
        "The following is the complete conversation transcript. Respect the role tags, "
        "continue from the latest message, and use the supplied native functions when needed."
    ]
    for index, message in enumerate(messages):
        role = str(message.get("role") or "user").upper()
        content = message.get("content")
        if content is not None:
            if not isinstance(content, str):
                content = json.dumps(content, ensure_ascii=False, sort_keys=True)
            chunks.append(f"<{role} index={index}>\n{content}\n</{role}>")
        for call in message.get("tool_calls") or []:
            function = call.get("function") or {}
            arguments = function.get("arguments") or "{}"
            if not isinstance(arguments, str):
                arguments = json.dumps(arguments, ensure_ascii=False, sort_keys=True)
            chunks.append(
                "<ASSISTANT_FUNCTION_CALL "
                f"id={call.get('id', '')} name={function.get('name', '')}>\n"
                f"{arguments}\n</ASSISTANT_FUNCTION_CALL>"
            )
        if role == "TOOL":
            chunks.append(
                "<FUNCTION_RESULT_BINDING "
                f"call_id={message.get('tool_call_id', '')} name={message.get('name', '')}/>"
            )
    return "\n\n".join(chunks)


@dataclass(frozen=True)
class ArkPlanReactReceipt:
    call_index: int
    created_at_utc: str
    requested_model: str
    resolved_model: str
    prompt_sha256: str
    tool_schema_sha256: str
    response_id_sha256: str
    provider_status: str
    function_call_names: tuple[str, ...]
    input_tokens: int
    output_tokens: int
    total_tokens: int
    thinking_requested: str | None
    get_poll_recovery: bool
    provider_retry_limit: int
    hidden_provider_retry_used: bool = False
    provider_budget_claim_id: int | None = None
    provider_budget_unit_call_index: int | None = None
    provider_budget_total_claimed_after: int | None = None


class ArkPlanReactLLM:
    """MindMemOS ``LLMCallable`` adapter over Ark Plan Responses API.

    The adapter is intentionally narrow: one requested/resolved model pair,
    provider retry zero, deterministic transcript rendering, native function
    calls, and public receipts with response identifiers hashed.  Scientific
    runners should instantiate one adapter per rollout so receipt attribution is
    unambiguous and requests sessions are not shared across concurrent rollouts.
    """

    def __init__(
        self,
        *,
        settings: ArkSettings | None = None,
        requested_model: str,
        required_resolved_model: str,
        max_output_tokens: int = 4096,
        temperature: float | None = 0,
        thinking: str | None = "disabled",
        provider_budget_ledger: ProviderBudgetLedger | None = None,
        provider_budget_unit_id: str | None = None,
    ) -> None:
        raw = settings or ArkSettings.from_env(required=True)
        if raw.base_url.rstrip("/") != PLAN_BASE_URL:
            raise RuntimeError("E2-R17 actor refuses any non-Ark-Plan route")
        self.settings = ArkSettings(
            api_key=raw.api_key,
            base_url=raw.base_url,
            default_model=raw.default_model,
            timeout_seconds=max(180.0, raw.timeout_seconds),
            max_retries=0,
        )
        self.client = ArkResponsesClient(self.settings)
        self.requested_model = requested_model
        self.required_resolved_model = required_resolved_model
        self.max_output_tokens = int(max_output_tokens)
        self.temperature = temperature
        self.thinking = thinking
        if (provider_budget_ledger is None) != (provider_budget_unit_id is None):
            raise ValueError("provider budget ledger and unit id must be supplied together")
        self.provider_budget_ledger = provider_budget_ledger
        self.provider_budget_unit_id = str(provider_budget_unit_id) if provider_budget_unit_id is not None else None
        self.provider_budget_claims: list[ProviderBudgetClaim] = []
        self.receipts: list[ArkPlanReactReceipt] = []

    async def __call__(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        prompt = _render_messages(messages)
        response_tools = _responses_tools(tools)
        result = await asyncio.to_thread(self._respond, prompt, response_tools)
        raw_calls = result.get("function_calls") or []
        tool_calls = []
        for index, call in enumerate(raw_calls):
            call_id = str(call.get("call_id") or call.get("id") or f"call_{index}")
            arguments = call.get("arguments") or "{}"
            if not isinstance(arguments, str):
                arguments = json.dumps(arguments, ensure_ascii=False, sort_keys=True)
            tool_calls.append(
                {
                    "id": call_id,
                    "type": "function",
                    "function": {
                        "name": str(call.get("name") or ""),
                        "arguments": arguments,
                    },
                }
            )
        message: dict[str, Any] = {
            "role": "assistant",
            "content": str(result.get("text") or "") or None,
        }
        if tool_calls:
            message["tool_calls"] = tool_calls
        return message

    def _respond(self, prompt: str, tools: list[dict[str, Any]]) -> dict[str, Any]:
        budget_claim: ProviderBudgetClaim | None = None
        if self.provider_budget_ledger is not None:
            assert self.provider_budget_unit_id is not None
            budget_claim = self.provider_budget_ledger.claim(self.provider_budget_unit_id)
            self.provider_budget_claims.append(budget_claim)
        try:
            result = self.client.respond(
                prompt,
                model=self.requested_model,
                max_output_tokens=self.max_output_tokens,
                temperature=self.temperature,
                tools=tools or None,
                thinking=self.thinking,
                allow_thinking_compatibility_fallback=False,
            )
        except ArkResponseStateError as exc:
            if not exc.response_id:
                raise
            polled = self.client.poll_response(exc.response_id, max_polls=4, interval_seconds=1.0)
            if not polled.get("text") and not polled.get("function_calls"):
                raise
            result = {
                "requested_model": self.requested_model,
                "resolved_model": polled.get("resolved_model"),
                "text": polled.get("text"),
                "function_calls": polled.get("function_calls") or [],
                "usage": polled.get("usage") or {},
                "response_id": polled.get("response_id") or exc.response_id,
                "status": polled.get("status"),
                "get_poll_recovery": True,
            }
        resolved = str(result.get("resolved_model") or "")
        if resolved != self.required_resolved_model:
            raise RuntimeError(
                f"resolved-model-drift: requested={self.requested_model}; "
                f"required={self.required_resolved_model}; observed={resolved}"
            )
        usage = result.get("usage") or {}
        calls = result.get("function_calls") or []
        receipt = ArkPlanReactReceipt(
            call_index=len(self.receipts),
            created_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            requested_model=self.requested_model,
            resolved_model=resolved,
            prompt_sha256=_sha_text(prompt),
            tool_schema_sha256=_canonical_sha(tools),
            response_id_sha256=_sha_text(str(result.get("response_id") or "")),
            provider_status=str(result.get("status") or ""),
            function_call_names=tuple(str(call.get("name") or "") for call in calls),
            input_tokens=int(usage.get("input_tokens") or 0),
            output_tokens=int(usage.get("output_tokens") or 0),
            total_tokens=int(usage.get("total_tokens") or 0),
            thinking_requested=self.thinking,
            get_poll_recovery=bool(result.get("get_poll_recovery", False)),
            provider_retry_limit=self.settings.max_retries,
            provider_budget_claim_id=budget_claim.claim_id if budget_claim else None,
            provider_budget_unit_call_index=budget_claim.unit_call_index if budget_claim else None,
            provider_budget_total_claimed_after=budget_claim.total_claimed_after if budget_claim else None,
        )
        self.receipts.append(receipt)
        return result

    def public_receipts(self) -> list[dict[str, Any]]:
        return [asdict(receipt) for receipt in self.receipts]

    def public_budget_claims(self) -> list[dict[str, Any]]:
        return [claim.to_dict() for claim in self.provider_budget_claims]

    @property
    def receipt_bundle_sha256(self) -> str:
        return _canonical_sha(self.public_receipts())


__all__ = [
    "ArkPlanReactLLM",
    "ArkPlanReactReceipt",
    "PLAN_BASE_URL",
]


===== BOUND ARTIFACT: actor_pool | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/e2_r17_actor_pool.py =====
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef, canonical_sha256


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _safe_error(exc: BaseException) -> str:
    text = f"{type(exc).__name__}: {exc}"
    # Provider response identifiers are never required for a public failure receipt.
    import re

    text = re.sub(r"resp_[A-Za-z0-9_]+", "resp_[REDACTED]", text)
    text = re.sub(r"Request id:\s*[A-Za-z0-9_]+", "Request id: [REDACTED]", text)
    return text[:2000]


def _load_ref(path: Path) -> TrajectoryRef:
    payload = json.loads(path.read_text(encoding="utf-8"))
    ref = TrajectoryRef(**payload)
    ref.validate()
    trajectory = Path(ref.trajectory_path)
    if not trajectory.exists() or file_sha256(trajectory) != ref.trajectory_sha256:
        raise RuntimeError(f"stored trajectory receipt failed content-address check: {path}")
    return ref


def _quarantine_partial(workdir: Path) -> Path | None:
    if not workdir.exists():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    candidate = workdir.with_name(f"{workdir.name}.incomplete-{stamp}")
    suffix = 0
    while candidate.exists():
        suffix += 1
        candidate = workdir.with_name(f"{workdir.name}.incomplete-{stamp}-{suffix}")
    workdir.rename(candidate)
    return candidate


@dataclass(frozen=True)
class ActorRolloutConfig:
    requested_model: str
    required_resolved_model: str
    max_turns: int
    skill_source: str
    skill_pre_sha256: str
    failure_family: str | None
    experiment_mode: str
    contract_sha256: str | None = None
    authorization_sha256: str | None = None


async def run_actor_rollout(
    *,
    env: Any,
    case: Any,
    rollout_index: int,
    agent_factory: Any,
    adapter: Any,
    config: ActorRolloutConfig,
    evaluator_sources: Sequence[Path],
) -> TrajectoryRef:
    """Run or resume one content-addressed SpreadsheetBench actor rollout."""

    workdir = Path(env.case_workdir(case, rollout_index))
    ref_path = workdir / "r17_trajectory_ref.json"
    raw_path = workdir / "r17_trajectory.json"
    if ref_path.exists():
        ref = _load_ref(ref_path)
        ledger = getattr(adapter, "provider_budget_ledger", None)
        unit_id = getattr(adapter, "provider_budget_unit_id", None)
        if ref.provider_budget_claim_count:
            if ledger is None or not unit_id:
                raise RuntimeError("budgeted trajectory ref cannot be reused without its bound provider budget ledger")
            if ref.provider_budget_unit_id != str(unit_id):
                raise RuntimeError("budgeted trajectory ref unit id drift on resume")
            snapshot = ledger.snapshot()
            observed = int(snapshot.unit_claimed.get(str(unit_id), 0))
            if observed != int(ref.provider_budget_unit_claimed_after or -1):
                raise RuntimeError(
                    f"provider budget ledger/ref drift on resume: unit={unit_id}; "
                    f"ledger={observed}; ref={ref.provider_budget_unit_claimed_after}"
                )
            if snapshot.total_claimed < int(ref.provider_budget_total_claimed_after or -1):
                raise RuntimeError("provider budget total counter regressed below completed trajectory ref")
        return ref
    quarantined = _quarantine_partial(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    env.setup_case(case, workdir)
    input_path = workdir / env.input_name
    messages = env.build_messages(case)
    prompt_sha = canonical_sha256(
        {
            "system_prompt": env.system_prompt(),
            "messages": messages,
            "skill_pre_sha256": config.skill_pre_sha256,
            "max_turns": config.max_turns,
            "requested_model": config.requested_model,
            "required_resolved_model": config.required_resolved_model,
        }
    )
    golden = env._workbook(case.data["src_dir"], "golden")
    verifier_sha = canonical_sha256(
        {
            "evaluator_source_sha256": {str(path): file_sha256(path) for path in evaluator_sources},
            "golden_workbook_sha256": file_sha256(golden),
            "answer_position": env.answer_position(case),
        }
    )
    started_at = time.time()
    technical_error: str | None = None
    try:
        agent, _ = agent_factory.build(workdir, env.system_prompt())
        agent_result = await agent.run(messages)
        score, score_message = env.score(case, workdir)
    except Exception as exc:  # noqa: BLE001 - persist exact failed unit for resume
        technical_error = _safe_error(exc)
        failure = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-actor-rollout-technical-failure",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "case_id": case.id,
            "rollout_index": rollout_index,
            "workdir": str(workdir),
            "error": technical_error,
            "quarantined_previous_partial": str(quarantined) if quarantined else None,
            "adapter_receipts": adapter.public_receipts(),
            "provider_budget_claims": adapter.public_budget_claims() if hasattr(adapter, "public_budget_claims") else [],
            "provider_retry_limit": 0,
            "scientific_outcome": False,
        }
        atomic_json(workdir / "r17_technical_failure.json", failure)
        raise RuntimeError(technical_error) from exc

    ended_at = time.time()
    output_path = workdir / env.output_name
    output_sha = file_sha256(output_path) if output_path.exists() else None
    receipts = adapter.public_receipts()
    if not receipts:
        raise RuntimeError("actor rollout completed without provider receipts")
    budget_claims = adapter.public_budget_claims() if hasattr(adapter, "public_budget_claims") else []
    if getattr(adapter, "provider_budget_ledger", None) is not None and len(budget_claims) != len(receipts):
        raise RuntimeError("successful budgeted rollout must bind exactly one pre-I/O budget claim per provider receipt")
    observed = {str(row.get("resolved_model") or "") for row in receipts}
    if observed != {config.required_resolved_model}:
        raise RuntimeError(f"actor rollout contains resolved-model drift: {sorted(observed)}")
    raw_payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-actor-rollout",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "case_id": case.id,
        "split": case.split,
        "rollout_index": rollout_index,
        "score": float(score),
        "score_message": score_message,
        "finished": bool(agent_result.finished),
        "turns": int(agent_result.turns),
        "messages": agent_result.messages,
        "workdir": str(workdir),
        "input_sha256": file_sha256(input_path),
        "output_sha256": output_sha,
        "prompt_sha256": prompt_sha,
        "skill_source": config.skill_source,
        "skill_pre_sha256": config.skill_pre_sha256,
        "verifier_sha256": verifier_sha,
        "requested_model": config.requested_model,
        "resolved_model": config.required_resolved_model,
        "adapter_receipts": receipts,
        "adapter_receipt_bundle_sha256": adapter.receipt_bundle_sha256,
        "provider_budget_claims": budget_claims,
        "provider_budget_claim_bundle_sha256": canonical_sha256(budget_claims) if budget_claims else None,
        "provider_retry_limit": 0,
        "hidden_provider_retry_used": False,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_seconds": ended_at - started_at,
        "failure_family": config.failure_family if float(score) < 1.0 else None,
        "experiment_mode": config.experiment_mode,
        "contract_sha256": config.contract_sha256,
        "authorization_sha256": config.authorization_sha256,
        "quarantined_previous_partial": str(quarantined) if quarantined else None,
    }
    atomic_json(raw_path, raw_payload)
    provider_call_id_sha = canonical_sha256([row["response_id_sha256"] for row in receipts])
    ref = TrajectoryRef(
        task_id=str(case.id),
        rollout_index=rollout_index,
        score=float(score),
        trajectory_path=str(raw_path.resolve()),
        trajectory_sha256=file_sha256(raw_path),
        input_sha256=file_sha256(input_path),
        prompt_sha256=prompt_sha,
        skill_pre_sha256=config.skill_pre_sha256,
        verifier_sha256=verifier_sha,
        requested_model=config.requested_model,
        resolved_model=config.required_resolved_model,
        provider_call_id_sha256=provider_call_id_sha,
        evidence_tokens=sum(int(row.get("total_tokens") or 0) for row in receipts),
        technical_status="COMPLETED",
        failure_code=config.failure_family if float(score) < 1.0 else None,
        provider_budget_unit_id=(str(budget_claims[-1]["unit_id"]) if budget_claims else None),
        provider_budget_claim_count=len(budget_claims),
        provider_budget_claim_bundle_sha256=(canonical_sha256(budget_claims) if budget_claims else None),
        provider_budget_unit_claimed_after=(int(budget_claims[-1]["unit_call_index"]) if budget_claims else None),
        provider_budget_total_claimed_after=(int(budget_claims[-1]["total_claimed_after"]) if budget_claims else None),
    )
    ref.validate()
    atomic_json(ref_path, asdict(ref))
    return ref


def freeze_nested_pools(
    *,
    task_dir: Path,
    trajectories: Sequence[TrajectoryRef],
    prefix_ks: Sequence[int] = (1, 2, 4, 8),
) -> dict[int, SearchPool]:
    ordered = tuple(sorted(trajectories, key=lambda row: row.rollout_index))
    if [row.rollout_index for row in ordered] != list(range(len(ordered))):
        raise ValueError("nested pool trajectories must be exactly indexed 0..K-1")
    pools: dict[int, SearchPool] = {}
    for k in sorted(set(int(value) for value in prefix_ks)):
        if k < 1 or k > len(ordered):
            continue
        pool = SearchPool.freeze(ordered[:k])
        payload = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-frozen-search-pool",
            "pool_id": pool.pool_id,
            "task_id": pool.task_id,
            "k": pool.k,
            "search_topology": pool.search_topology,
            "acting_winner_index": pool.winner.rollout_index,
            "acting_success": pool.acting_success,
            "precommitted_success": pool.precommitted_success,
            "rescue_event": pool.rescue_event,
            "trajectories": [asdict(row) for row in pool.trajectories],
        }
        atomic_json(task_dir / f"pool_k{k}.json", payload)
        pools[k] = pool
    return pools


def load_frozen_pool(path: Path) -> SearchPool:
    payload = json.loads(path.read_text(encoding="utf-8"))
    trajectories = tuple(TrajectoryRef(**row) for row in payload["trajectories"])
    pool = SearchPool(
        pool_id=payload["pool_id"],
        task_id=payload["task_id"],
        k=int(payload["k"]),
        trajectories=trajectories,
        search_topology=payload.get("search_topology", "parallel_best_of_k"),
    )
    pool.validate()
    return pool


__all__ = [
    "ActorRolloutConfig",
    "atomic_json",
    "file_sha256",
    "freeze_nested_pools",
    "load_frozen_pool",
    "run_actor_rollout",
]


===== BOUND ARTIFACT: actor_runner | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/run_e2_r17_actor_pool.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import (
    ActorRolloutConfig,
    atomic_json,
    file_sha256,
    freeze_nested_pools,
    run_actor_rollout,
)
from research_pipeline.e2_r17_ark_plan_react import ArkPlanReactLLM, PLAN_BASE_URL
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger


def load_mindmemos(root: Path) -> tuple[Any, Any]:
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    source_roots = [root / "src/mindmemos_eval", root / "src/mindmemos_sdk", root / "src/mindmemos"]
    for source in reversed(source_roots):
        if str(source) not in sys.path:
            sys.path.insert(0, str(source))
    from mindmemos_eval.skills.agents import ReactAgentFactory
    from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv

    return ReactAgentFactory, SpreadsheetBenchEnv


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def task_ids_from_args(args: argparse.Namespace, split: dict[str, Any]) -> list[str]:
    if args.task_id:
        return [str(value) for value in args.task_id]
    if args.stream_id:
        for key in ("e1_update_streams", "e3_future_streams"):
            if args.stream_id in split.get(key, {}):
                return [str(value) for value in split[key][args.stream_id]]
        raise ValueError(f"unknown stream id: {args.stream_id}")
    if args.lane:
        value = split.get(args.lane)
        if not isinstance(value, list):
            raise ValueError(f"lane is not a task list: {args.lane}")
        return [str(item) for item in value]
    raise ValueError("one of --task-id, --stream-id, or --lane is required")


def validate_authority(
    *,
    mode: str,
    authorization: Path | None,
    task_ids: list[str],
    split: dict[str, Any],
    k: int,
) -> tuple[dict[str, Any] | None, str | None]:
    development = {str(item) for item in split.get("development") or []}
    if mode == "protocol_smoke":
        if not set(task_ids).issubset(development):
            raise RuntimeError("protocol smoke may access development tasks only")
        if authorization is not None:
            raise RuntimeError("protocol smoke must not borrow scientific authorization")
        return None, None
    if authorization is None:
        raise RuntimeError("scientific actor execution requires --authorization")
    payload = json.loads(authorization.read_text(encoding="utf-8"))
    if payload.get("status") not in {"AUTHORIZED_E0", "AUTHORIZED_E1", "AUTHORIZED_PUBLIC_EXTERNALITY"}:
        raise RuntimeError("authorization artifact does not authorize actor execution")
    if not payload.get("authority", {}).get("scientific_experiment"):
        raise RuntimeError("authorization has zero scientific authority")

    # New scoped authorizations fail closed. Historical artifacts without an
    # execution_scope remain readable/replayable, but any E1-A/E1-B tranche
    # minted after this guard must bind the exact mode, task IDs and K it grants.
    scope = payload.get("execution_scope")
    if scope is not None:
        allowed_modes = {str(value) for value in scope.get("allowed_modes") or []}
        if not allowed_modes or mode not in allowed_modes:
            raise RuntimeError(f"authorization does not allow mode={mode}")
        allowed_tasks = {str(value) for value in scope.get("allowed_task_ids") or []}
        if not allowed_tasks or not set(task_ids).issubset(allowed_tasks):
            raise RuntimeError("authorization does not allow one or more requested task IDs")
        exact_k = scope.get("exact_k")
        if exact_k is not None and int(exact_k) != int(k):
            raise RuntimeError(f"authorization requires exact K={exact_k}, requested K={k}")
        if scope.get("allow_noninitial_skill") is False and payload.get("authority", {}).get("e1_b"):
            raise RuntimeError("authorization scope is internally inconsistent about non-initial skills")
    return payload, sha256(authorization)


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    ReactAgentFactory, SpreadsheetBenchEnv = load_mindmemos(args.mindmemos_root)
    load_env_file(args.env_file)
    settings = ArkSettings.from_env(required=True)
    if settings.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("E2-R17 actor refuses any non-Ark-Plan route")
    settings = ArkSettings(
        api_key=settings.api_key,
        base_url=settings.base_url,
        default_model=settings.default_model,
        timeout_seconds=300,
        max_retries=0,
    )
    identity = json.loads(args.identity.read_text(encoding="utf-8"))
    if identity.get("status") != "PASS_CURRENT_REVIEW_TRANCHE":
        raise RuntimeError("current model identity adjudication is not passing")
    model_row = identity["requested_and_resolved"][args.model]
    requested_model = str(model_row["requested"])
    required_resolved = str(model_row["resolved"])

    split_path = args.suite_root / "r17_split_manifest.json"
    split = json.loads(split_path.read_text(encoding="utf-8"))
    task_ids = task_ids_from_args(args, split)
    authorization_payload, authorization_sha = validate_authority(
        mode=args.mode,
        authorization=args.authorization,
        task_ids=task_ids,
        split=split,
        k=args.k,
    )
    contract_sha = (
        str(authorization_payload.get("contract_sha256") or "")
        if authorization_payload is not None
        else None
    )
    provider_budget_ledger: ProviderBudgetLedger | None = None
    budget_args_present = any(
        value is not None
        for value in (args.provider_budget_ledger, args.provider_total_call_limit, args.provider_per_unit_call_limit)
    )
    if budget_args_present:
        if authorization_payload is None or not authorization_sha or not contract_sha:
            raise RuntimeError("provider budget ledger is allowed only for a bound scientific authorization")
        if args.provider_budget_ledger is None or args.provider_total_call_limit is None or args.provider_per_unit_call_limit is None:
            raise RuntimeError("provider budget ledger path, total limit and per-unit limit must be supplied together")
        provider_budget_ledger = ProviderBudgetLedger(
            path=args.provider_budget_ledger,
            contract_sha256=contract_sha,
            authorization_sha256=authorization_sha,
            total_limit=int(args.provider_total_call_limit),
            per_unit_limit=int(args.provider_per_unit_call_limit),
            allow_create=not args.provider_budget_ledger.exists(),
        )
    if authorization_payload is not None:
        scope = authorization_payload.get("execution_scope") or {}
        provider_budget_scope = scope.get("provider_budget") or {}
        if provider_budget_scope.get("required") is True:
            if provider_budget_ledger is None:
                raise RuntimeError("authorization requires a fail-closed provider budget ledger")
            if int(provider_budget_scope.get("total_limit")) != int(args.provider_total_call_limit):
                raise RuntimeError("authorization provider total-call limit drift")
            if int(provider_budget_scope.get("per_unit_limit")) != int(args.provider_per_unit_call_limit):
                raise RuntimeError("authorization provider per-unit limit drift")
        expected_resolved = scope.get("required_resolved_model")
        if expected_resolved and str(expected_resolved) != required_resolved:
            raise RuntimeError("authorization resolved-model identity drift")
        expected_identity_sha = scope.get("identity_artifact_sha256")
        if expected_identity_sha and sha256(args.identity) != expected_identity_sha:
            raise RuntimeError("authorization model-identity artifact drift")
        if scope.get("max_turns") is not None and int(scope["max_turns"]) != int(args.max_turns):
            raise RuntimeError("authorization max_turns drift")
        if scope.get("max_output_tokens") is not None and int(scope["max_output_tokens"]) != int(args.max_output_tokens):
            raise RuntimeError("authorization max_output_tokens drift")
    metadata_rows = json.loads((args.suite_root / "r17_controlled_metadata.json").read_text(encoding="utf-8"))
    metadata = {str(row["id"]): row for row in metadata_rows}
    missing = [task_id for task_id in task_ids if task_id not in metadata]
    if missing:
        raise RuntimeError(f"tasks absent from controlled metadata: {missing}")

    env = SpreadsheetBenchEnv(args.suite_root, args.run_root)
    cases = {case.id: case for case in env.load_cases("all")}
    mindmemos_commit = __import__("subprocess").check_output(
        ["git", "-C", str(args.mindmemos_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if authorization_payload is not None and mindmemos_commit != authorization_payload.get("mindmemos_commit"):
        raise RuntimeError("MindMemOS commit drifted after scientific authorization")
    if authorization_payload is not None:
        scope = authorization_payload.get("execution_scope") or {}
        expected_suite_sha = scope.get("suite_manifest_sha256")
        expected_split_sha = scope.get("split_manifest_sha256")
        if expected_suite_sha and file_sha256(args.suite_root / "suite_manifest.json") != expected_suite_sha:
            raise RuntimeError("suite manifest drifted after scientific authorization")
        if expected_split_sha and file_sha256(split_path) != expected_split_sha:
            raise RuntimeError("split manifest drifted after scientific authorization")

    default_skill_source = args.mindmemos_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx"
    skill_source = (args.skill_source or default_skill_source).resolve()
    skill_md = skill_source / "SKILL.md"
    if not skill_md.is_file():
        raise RuntimeError(f"skill source does not contain SKILL.md: {skill_source}")
    skill_sha = file_sha256(skill_md)
    if authorization_payload is not None:
        required_skill_sha = (authorization_payload.get("execution_scope") or {}).get("required_skill_pre_sha256")
        if required_skill_sha and skill_sha != required_skill_sha:
            raise RuntimeError("skill pre-state drifted after scientific authorization")
    updater_receipt_sha: str | None = None
    if skill_source != default_skill_source.resolve():
        if args.mode != "e1" or args.updater_receipt is None:
            raise RuntimeError("a non-initial skill is allowed only for E1 evaluation with --updater-receipt")
        updater_receipt = json.loads(args.updater_receipt.read_text(encoding="utf-8"))
        updater_receipt_sha = sha256(args.updater_receipt)
        if updater_receipt.get("status") != "COMPLETED":
            raise RuntimeError("updater receipt is not completed")
        if Path(updater_receipt.get("skill_post_path") or "").resolve() != skill_md.resolve():
            raise RuntimeError("updater receipt does not bind the supplied skill path")
        if updater_receipt.get("skill_post_sha256") != skill_sha:
            raise RuntimeError("updater receipt does not bind the supplied skill content")
        if updater_receipt.get("contract_sha256") != contract_sha:
            raise RuntimeError("updater receipt contract SHA differs from evaluation authorization")
        if updater_receipt.get("authorization_sha256") != authorization_sha:
            raise RuntimeError("updater receipt authorization SHA differs from evaluation authorization")
    elif args.updater_receipt is not None:
        raise RuntimeError("--updater-receipt must not be supplied for the frozen initial skill")
    evaluator_sources = [
        args.mindmemos_root / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/evaluator.py",
        args.mindmemos_root / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py",
    ]
    semaphore = asyncio.Semaphore(max(1, args.concurrency))

    async def run_unit(task_id: str, rollout_index: int):
        async with semaphore:
            adapter = ArkPlanReactLLM(
                settings=settings,
                requested_model=requested_model,
                required_resolved_model=required_resolved,
                max_output_tokens=args.max_output_tokens,
                temperature=0,
                thinking="disabled",
                provider_budget_ledger=provider_budget_ledger,
                provider_budget_unit_id=(f"{task_id}/rollout_{rollout_index}" if provider_budget_ledger is not None else None),
            )
            factory = ReactAgentFactory(
                adapter,
                max_turns=args.max_turns,
                skill_sources=[skill_source],
                python_path=sys.executable,
            )
            config = ActorRolloutConfig(
                requested_model=requested_model,
                required_resolved_model=required_resolved,
                max_turns=args.max_turns,
                skill_source=str(skill_source),
                skill_pre_sha256=skill_sha,
                failure_family=str(metadata[task_id]["primary_failure_family"]),
                experiment_mode=args.mode,
                contract_sha256=contract_sha,
                authorization_sha256=authorization_sha,
            )
            return await run_actor_rollout(
                env=env,
                case=cases[task_id],
                rollout_index=rollout_index,
                agent_factory=factory,
                adapter=adapter,
                config=config,
                evaluator_sources=evaluator_sources,
            )

    task_rows: list[dict[str, Any]] = []
    prefix_ks = tuple(int(value) for value in args.prefix_ks.split(",") if value.strip())
    for task_id in task_ids:
        refs = await asyncio.gather(*(run_unit(task_id, index) for index in range(args.k)))
        task_dir = args.run_root / "cases" / task_id
        pools = freeze_nested_pools(task_dir=task_dir, trajectories=refs, prefix_ks=prefix_ks)
        task_rows.append(
            {
                "task_id": task_id,
                "failure_family": metadata[task_id]["primary_failure_family"],
                "scores": [ref.score for ref in refs],
                "provider_calls": sum(
                    len(json.loads(Path(ref.trajectory_path).read_text(encoding="utf-8"))["adapter_receipts"])
                    for ref in refs
                ),
                "pools": {
                    str(k): {
                        "pool_id": pool.pool_id,
                        "acting_success": pool.acting_success,
                        "precommitted_success": pool.precommitted_success,
                        "rescue_event": pool.rescue_event,
                        "winner_index": pool.winner.rollout_index,
                    }
                    for k, pool in pools.items()
                },
            }
        )
    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-actor-pool-run-summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "COMPLETED",
        "mode": args.mode,
        "suite_root": str(args.suite_root),
        "suite_manifest_sha256": file_sha256(args.suite_root / "suite_manifest.json"),
        "split_manifest_sha256": file_sha256(split_path),
        "mindmemos_root": str(args.mindmemos_root),
        "mindmemos_commit": mindmemos_commit,
        "identity_artifact": str(args.identity),
        "identity_artifact_sha256": sha256(args.identity),
        "requested_model": requested_model,
        "resolved_model": required_resolved,
        "provider_retry_limit": 0,
        "thinking": "disabled",
        "k": args.k,
        "prefix_ks": list(prefix_ks),
        "max_turns": args.max_turns,
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "skill_source": str(skill_source),
        "skill_pre_sha256": skill_sha,
        "updater_receipt_path": str(args.updater_receipt) if args.updater_receipt else None,
        "updater_receipt_sha256": updater_receipt_sha,
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "provider_budget": provider_budget_ledger.snapshot().to_dict() if provider_budget_ledger is not None else None,
        "tasks": task_rows,
        "scientific_outcome": args.mode != "protocol_smoke",
        "authority": {
            "paper_promotion": False,
            "submission": False,
        },
        "private_credentials_included": False,
        "raw_response_ids_included": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--suite-root", type=Path, required=True)
    parser.add_argument("--mindmemos-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--skill-source", type=Path)
    parser.add_argument("--updater-receipt", type=Path)
    parser.add_argument("--mode", choices=("protocol_smoke", "e0", "e1", "public_externality"), required=True)
    parser.add_argument("--model", choices=("deepseek-v4-pro",), default="deepseek-v4-pro")
    parser.add_argument("--task-id", action="append")
    parser.add_argument("--lane")
    parser.add_argument("--stream-id")
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--prefix-ks", default="1,2,4,8")
    parser.add_argument("--max-turns", type=int, default=10)
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--provider-budget-ledger", type=Path)
    parser.add_argument("--provider-total-call-limit", type=int)
    parser.add_argument("--provider-per-unit-call-limit", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.k < 1 or args.k > 8:
        raise SystemExit("K must be in 1..8")
    summary = asyncio.run(main_async(args))
    atomic_json(args.output, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: e1_a_orchestrator | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/run_e2_r17_e1_a_pool_support.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger

ACTOR = ROOT / "scripts/run_e2_r17_actor_pool.py"
EXPECTED_AUTH_STATUS = "AUTHORIZED_E1"
EXPECTED_CONTRACT_STATUS = "FROZEN_E1_A_POOL_SUPPORT"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def manifest_rows(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[str(row["stream_id"])] = row
    return rows


def verify_stream_receipt(
    row: dict[str, Any],
    run_root: Path,
    provider_budget_ledger: ProviderBudgetLedger | None = None,
) -> None:
    summary_path = Path(row["summary_path"])
    require(summary_path.exists(), f"missing completed stream summary: {summary_path}")
    require(sha_file(summary_path) == row["summary_sha256"], f"completed stream summary SHA drift: {row['stream_id']}")
    summary = load_json(summary_path)
    require(summary.get("status") == "COMPLETED", f"stream summary not completed: {row['stream_id']}")
    tasks = summary.get("tasks") or []
    require(len(tasks) == 8, f"completed stream does not contain eight tasks: {row['stream_id']}")
    for task in tasks:
        task_id = str(task["task_id"])
        task_dir = run_root / "cases" / task_id
        for k in (1, 2, 4, 8):
            pool = task_dir / f"pool_k{k}.json"
            require(pool.exists(), f"missing frozen K={k} pool for {task_id}")
        for rollout in range(8):
            ref = task_dir / f"rollout_{rollout}" / "r17_trajectory_ref.json"
            require(ref.exists(), f"missing trajectory ref {task_id}/{rollout}")
            ref_payload = load_json(ref)
            trajectory = Path(ref_payload["trajectory_path"])
            require(trajectory.exists(), f"missing trajectory bound by {ref}")
            require(sha_file(trajectory) == ref_payload["trajectory_sha256"], f"trajectory SHA drift: {task_id}/{rollout}")
            if provider_budget_ledger is not None:
                unit_id = f"{task_id}/rollout_{rollout}"
                require(ref_payload.get("provider_budget_unit_id") == unit_id, f"provider budget unit id drift: {unit_id}")
                claim_count = int(ref_payload.get("provider_budget_claim_count") or 0)
                require(claim_count >= 1, f"completed E1-A rollout lacks provider budget claims: {unit_id}")
                raw = load_json(trajectory)
                claims = raw.get("provider_budget_claims") or []
                require(len(claims) == claim_count, f"provider budget claim count drift: {unit_id}")
                claim_sha = hashlib.sha256(
                    json.dumps(claims, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
                ).hexdigest()
                require(claim_sha == ref_payload.get("provider_budget_claim_bundle_sha256"), f"provider budget claim SHA drift: {unit_id}")
                snapshot = provider_budget_ledger.snapshot()
                unit_claimed = int(snapshot.unit_claimed.get(unit_id, 0))
                require(
                    unit_claimed == int(ref_payload.get("provider_budget_unit_claimed_after") or -1),
                    f"provider budget ledger/ref unit count drift: {unit_id}",
                )
                require(
                    snapshot.total_claimed >= int(ref_payload.get("provider_budget_total_claimed_after") or -1),
                    f"provider budget total counter regressed: {unit_id}",
                )


def acquire_lock(path: Path, *, contract_sha: str, authorization_sha: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError(
            f"exclusive lock already exists: {path}; inspect process/checkpoints before any resume"
        ) from exc
    payload = {
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
    }
    os.write(fd, (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8"))
    os.fsync(fd)
    return fd


def validate_runtime(contract: dict[str, Any]) -> tuple[Path, dict[str, str]]:
    runtime = contract.get("runtime") or {}
    venv = Path(str(runtime.get("venv_root") or ""))
    python = Path(str(runtime.get("python_executable") or ""))
    freeze = Path(str(runtime.get("freeze_path") or ""))
    qualification = Path(str(runtime.get("qualification_path") or ""))
    require(venv.is_dir(), f"frozen runtime venv missing: {venv}")
    require(python.is_file(), f"frozen runtime python missing: {python}")
    require(python == venv / "bin/python", "runtime python must be exact venv/bin/python")
    require(freeze.is_file(), f"runtime freeze missing: {freeze}")
    require(sha_file(freeze) == runtime.get("freeze_sha256"), "runtime freeze SHA drift")
    require(qualification.is_file(), f"runtime qualification artifact missing: {qualification}")
    require(sha_file(qualification) == runtime.get("qualification_sha256"), "runtime qualification SHA drift")
    q = load_json(qualification)
    require(q.get("status") == "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2", "runtime qualification status invalid")
    require(q.get("venv_root") == str(venv), "runtime qualification venv drift")
    require(q.get("freeze_sha256") == runtime.get("freeze_sha256"), "runtime qualification freeze drift")
    env = os.environ.copy()
    env["VIRTUAL_ENV"] = str(venv)
    env["PATH"] = str(venv / "bin") + os.pathsep + env.get("PATH", "")
    smoke = subprocess.run(
        [
            str(python),
            "-c",
            (
                "import openpyxl,pydantic; "
                "assert openpyxl.__version__ == '3.1.5'; "
                "from mindmemos_eval.skills.agents import ReactAgentFactory; "
                "from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv"
            ),
        ],
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    require(smoke.returncode == 0, "frozen full MindMemOS runtime import smoke failed")
    return python, env


def validate_contract_and_auth(contract_path: Path, auth_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = load_json(contract_path)
    auth = load_json(auth_path)
    require(contract.get("status") == EXPECTED_CONTRACT_STATUS, "E1-A contract is not frozen")
    require(auth.get("status") == EXPECTED_AUTH_STATUS, "E1-A authorization status invalid")
    require(auth.get("authority", {}).get("scientific_experiment") is True, "E1-A scientific authority false")
    require(auth.get("authority", {}).get("e1_a") is True, "E1-A authority bit false")
    require(auth.get("authority", {}).get("e1_b") is False, "E1-A authorization must not inherit E1-B")
    require(auth.get("authority", {}).get("paper_promotion") is False, "E1-A authorization must not promote paper")
    require(auth.get("contract_sha256") == sha_file(contract_path), "authorization does not bind exact E1-A contract")
    return contract, auth


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    args = parser.parse_args()

    contract, auth = validate_contract_and_auth(args.contract, args.authorization)
    contract_sha = sha_file(args.contract)
    auth_sha = sha_file(args.authorization)

    for label, item in (contract.get("bound_code") or {}).items():
        path = ROOT / item["path"]
        require(path.exists() and sha_file(path) == item["sha256"], f"bound code drift: {label}")
    identity = ROOT / contract["model_identity"]["path"]
    require(identity.exists() and sha_file(identity) == contract["model_identity"]["sha256"], "model identity artifact drift")
    identity_payload = load_json(identity)
    require(identity_payload.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "actor model identity adjudication not passing")

    suite_root = Path(contract["suite"]["root"])
    split_path = suite_root / "r17_split_manifest.json"
    require(sha_file(suite_root / "suite_manifest.json") == contract["suite"]["suite_manifest_sha256"], "suite manifest drift")
    require(sha_file(split_path) == contract["suite"]["split_manifest_sha256"], "split manifest drift")
    require(sha_file(suite_root / "r17_controlled_metadata.json") == contract["suite"]["metadata_sha256"], "controlled metadata drift")
    split = load_json(split_path)
    streams = split["e1_update_streams"]
    frozen_stream_ids = list(contract["streams"])
    require(list(streams.keys()) == frozen_stream_ids, "stream ordering/content drift from frozen contract")
    all_tasks = [str(task) for stream_id in frozen_stream_ids for task in streams[stream_id]]
    require(len(all_tasks) == 96 and len(set(all_tasks)) == 96, "E1-A must bind 96 unique update tasks")
    scope = auth.get("execution_scope") or {}
    require(set(scope.get("allowed_task_ids") or []) == set(all_tasks), "authorization task scope does not equal frozen 96 tasks")
    require(scope.get("allowed_modes") == ["e1"], "authorization mode scope must be exactly e1")
    require(int(scope.get("exact_k")) == 8, "authorization must bind exact K=8")
    runtime = contract.get("runtime") or {}
    require(
        scope.get("runtime_python_executable") == runtime.get("python_executable"),
        "authorization runtime python drift",
    )
    require(scope.get("runtime_freeze_sha256") == runtime.get("freeze_sha256"), "authorization runtime freeze drift")
    require(
        scope.get("runtime_qualification_sha256") == runtime.get("qualification_sha256"),
        "authorization runtime qualification drift",
    )

    runtime_python, runtime_env = validate_runtime(contract)

    mind_root = Path(contract["mindmemos"]["root"])
    head = subprocess.run(["git", "-C", str(mind_root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    require(head == contract["mindmemos"]["commit"], "MindMemOS commit drift")
    initial_skill = mind_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md"
    require(sha_file(initial_skill) == contract["mindmemos"]["initial_skill_sha256"], "initial skill drift")

    run_root = Path(contract["run_root"])
    lock_path = run_root / ".exclusive.lock"
    manifest_path = run_root / "checkpoints/completed_streams.jsonl"
    summary_root = run_root / "summary/streams"
    failure_root = run_root / "checkpoints/failures"
    budget_ledger_path = run_root / "checkpoints/provider_budget.sqlite3"
    lock_fd = acquire_lock(lock_path, contract_sha=contract_sha, authorization_sha=auth_sha)
    provider_budget_ledger = ProviderBudgetLedger(
        path=budget_ledger_path,
        contract_sha256=contract_sha,
        authorization_sha256=auth_sha,
        total_limit=int(contract["budget"]["max_provider_calls"]),
        per_unit_limit=int(contract["actor"]["max_turns"]),
        allow_create=not budget_ledger_path.exists(),
    )
    success = False
    try:
        completed = manifest_rows(manifest_path)
        for row in completed.values():
            verify_stream_receipt(row, run_root, provider_budget_ledger)

        for stream_id in frozen_stream_ids:
            if stream_id in completed:
                continue
            output = summary_root / f"{stream_id}.json"
            command = [
                str(runtime_python),
                str(ACTOR),
                "--env-file", str(args.env_file),
                "--suite-root", str(suite_root),
                "--mindmemos-root", str(mind_root),
                "--run-root", str(run_root),
                "--identity", str(identity),
                "--authorization", str(args.authorization),
                "--mode", "e1",
                "--model", contract["actor"]["requested_model"],
                "--stream-id", stream_id,
                "--k", "8",
                "--prefix-ks", "1,2,4,8",
                "--max-turns", str(contract["actor"]["max_turns"]),
                "--max-output-tokens", str(contract["actor"]["max_output_tokens"]),
                "--concurrency", str(contract["actor"]["concurrency"]),
                "--provider-budget-ledger", str(budget_ledger_path),
                "--provider-total-call-limit", str(contract["budget"]["max_provider_calls"]),
                "--provider-per-unit-call-limit", str(contract["actor"]["max_turns"]),
                "--output", str(output),
            ]
            result = subprocess.run(command, cwd=ROOT, env=runtime_env, capture_output=True, text=True)
            if result.returncode != 0:
                failure = {
                    "schema_version": "1.0",
                    "artifact_type": "e2-r17-e1-a-stream-technical-failure",
                    "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "stream_id": stream_id,
                    "returncode": result.returncode,
                    "stdout_tail": result.stdout[-4000:],
                    "stderr_tail": result.stderr[-4000:],
                    "provider_relaunch_authorized": False,
                    "instruction": "Inspect process, lock, rollout refs, technical failures and completed manifests before any resume. Do not blindly relaunch.",
                }
                atomic_json(failure_root / f"{stream_id}.json", failure)
                raise RuntimeError(f"E1-A stream failed: {stream_id}; stale lock intentionally preserved")
            require(output.exists(), f"actor stream returned success without summary: {stream_id}")
            summary = load_json(output)
            require(summary.get("status") == "COMPLETED", f"actor stream summary not completed: {stream_id}")
            require(summary.get("authorization_sha256") == auth_sha, "actor stream authorization SHA drift")
            require(summary.get("contract_sha256") == contract_sha, "actor stream contract SHA drift")
            row = {
                "stream_id": stream_id,
                "summary_path": str(output),
                "summary_sha256": sha_file(output),
                "task_ids": [str(v) for v in streams[stream_id]],
                "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            verify_stream_receipt(row, run_root, provider_budget_ledger)
            append_jsonl(manifest_path, row)
            completed[stream_id] = row

        require(len(completed) == 12, "E1-A did not complete all 12 streams")
        for row in completed.values():
            verify_stream_receipt(row, run_root, provider_budget_ledger)

        mixed = 0
        exposed_streams = 0
        family_mixed: dict[str, int] = {}
        stream_rows: list[dict[str, Any]] = []
        metadata = {str(r["id"]): r for r in load_json(suite_root / "r17_controlled_metadata.json")}
        total_provider_calls = 0
        total_rollouts = 0
        for stream_id in frozen_stream_ids:
            stream_mixed = 0
            stream_calls = 0
            for task_id in streams[stream_id]:
                pool = load_json(run_root / "cases" / task_id / "pool_k8.json")
                scores = [float(row["score"]) for row in pool["trajectories"]]
                is_mixed = min(scores) < 1.0 and max(scores) >= 1.0
                stream_mixed += int(is_mixed)
                mixed += int(is_mixed)
                family = str(metadata[task_id]["primary_failure_family"])
                family_mixed[family] = family_mixed.get(family, 0) + int(is_mixed)
                total_rollouts += len(scores)
                for trajectory in pool["trajectories"]:
                    raw = load_json(Path(trajectory["trajectory_path"]))
                    stream_calls += len(raw.get("adapter_receipts") or [])
            total_provider_calls += stream_calls
            qualifies = stream_mixed >= int(contract["support_gate"]["mixed_pools_per_exposed_stream_minimum"])
            exposed_streams += int(qualifies)
            stream_rows.append({
                "stream_id": stream_id,
                "mixed_pools": stream_mixed,
                "qualifies_as_exposed_stream": qualifies,
                "provider_calls": stream_calls,
            })

        require(total_rollouts == 768, f"unexpected frozen rollout count: {total_rollouts}")
        require(total_provider_calls <= int(contract["budget"]["max_provider_calls"]), "provider receipt count hard ceiling exceeded")
        provider_budget_snapshot = provider_budget_ledger.snapshot()
        require(
            provider_budget_snapshot.total_claimed <= int(contract["budget"]["max_provider_calls"]),
            "provider budget claim hard ceiling exceeded",
        )
        require(
            provider_budget_snapshot.total_claimed >= total_provider_calls,
            "provider receipts exceed fail-closed pre-I/O budget claims",
        )
        supported_families = sum(int(value > 0) for value in family_mixed.values())
        support = {
            "mixed_pool_count": mixed,
            "mixed_pool_total": 96,
            "exposed_stream_count": exposed_streams,
            "stream_total": 12,
            "stream_rows": stream_rows,
            "family_mixed_counts": dict(sorted(family_mixed.items())),
            "supported_families": supported_families,
            "primary_hard_gate_pass": (
                mixed >= int(contract["support_gate"]["mixed_pool_count_minimum"])
                and exposed_streams >= int(contract["support_gate"]["exposed_stream_minimum"])
            ),
            "family_generalization_gate_pass": supported_families >= int(contract["support_gate"]["supported_families_minimum"]),
        }
        final = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-e1-a-pool-freeze-summary",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "COMPLETED_ALL_96_POOLS_PENDING_SEPARATE_SUPPORT_ADJUDICATION",
            "contract_sha256": contract_sha,
            "authorization_sha256": auth_sha,
            "model_identity_sha256": sha_file(identity),
            "mindmemos_commit": head,
            "runtime_python": str(runtime_python),
            "runtime_freeze_sha256": contract["runtime"]["freeze_sha256"],
            "runtime_qualification_sha256": contract["runtime"]["qualification_sha256"],
            "streams": 12,
            "tasks": 96,
            "actor_rollouts": total_rollouts,
            "provider_calls": total_provider_calls,
            "provider_budget": provider_budget_snapshot.to_dict(),
            "support": support,
            "updater_calls": 0,
            "e1_b_authority": False,
            "paper_promotion_authority": False,
        }
        atomic_json(run_root / "summary/e1_a_pool_freeze_summary.json", final)
        success = True
        print(json.dumps(final, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    finally:
        os.close(lock_fd)
        if success:
            lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: support_adjudicator | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/adjudicate_e2_r17_e1_a_pool_support.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    contract = load_json(args.contract)
    authorization = load_json(args.authorization)
    summary = load_json(args.summary)
    contract_sha = sha_file(args.contract)
    authorization_sha = sha_file(args.authorization)

    require(contract.get("status") == "FROZEN_E1_A_POOL_SUPPORT", "E1-A contract status invalid")
    require(authorization.get("status") == "AUTHORIZED_E1", "E1-A authorization status invalid")
    require(authorization.get("contract_sha256") == contract_sha, "authorization does not bind exact E1-A contract")
    require(summary.get("status") == "COMPLETED_ALL_96_POOLS_PENDING_SEPARATE_SUPPORT_ADJUDICATION", "E1-A pool freeze incomplete")
    require(summary.get("contract_sha256") == contract_sha, "summary contract SHA mismatch")
    require(summary.get("authorization_sha256") == authorization_sha, "summary authorization SHA mismatch")
    require(int(summary.get("streams") or 0) == 12, "E1-A stream cardinality invalid")
    require(int(summary.get("tasks") or 0) == 96, "E1-A task cardinality invalid")
    require(int(summary.get("actor_rollouts") or 0) == 768, "E1-A rollout cardinality invalid")
    require(int(summary.get("updater_calls") or -1) == 0, "E1-A must contain zero updater calls")
    require(summary.get("e1_b_authority") is False, "E1-A summary cannot inherit E1-B authority")

    support = summary.get("support") or {}
    stream_rows = support.get("stream_rows") or []
    require(len(stream_rows) == 12, "support summary must include 12 stream rows")
    mixed = int(support.get("mixed_pool_count") or 0)
    exposed = int(support.get("exposed_stream_count") or 0)
    supported_families = int(support.get("supported_families") or 0)
    thresholds = contract["support_gate"]
    min_mixed = int(thresholds["mixed_pool_count_minimum"])
    min_exposed = int(thresholds["exposed_stream_minimum"])
    min_per_stream = int(thresholds["mixed_pools_per_exposed_stream_minimum"])
    min_families = int(thresholds["supported_families_minimum"])

    run_root = Path(contract["run_root"])
    split = load_json(Path(contract["suite"]["root"]) / "r17_split_manifest.json")
    frozen_streams = list(contract["streams"])
    require(list(split["e1_update_streams"].keys()) == frozen_streams, "stream manifest drift")
    expected_tasks = [str(task) for stream_id in frozen_streams for task in split["e1_update_streams"][stream_id]]
    require(len(expected_tasks) == 96 and len(set(expected_tasks)) == 96, "frozen update set must contain 96 unique tasks")
    task_to_stream = {
        str(task): stream_id
        for stream_id in frozen_streams
        for task in split["e1_update_streams"][stream_id]
    }
    metadata_rows = load_json(Path(contract["suite"]["root"]) / "r17_controlled_metadata.json")
    metadata = {str(row["id"]): row for row in metadata_rows}

    pool_sha: dict[str, str] = {}
    mixed_recomputed = 0
    per_stream_mixed = {stream_id: 0 for stream_id in frozen_streams}
    per_family_mixed: dict[str, int] = {}
    for task_id in expected_tasks:
        pool_path = run_root / "cases" / task_id / "pool_k8.json"
        require(pool_path.exists(), f"missing frozen K8 pool: {task_id}")
        pool = load_json(pool_path)
        require(pool.get("task_id") == task_id and int(pool.get("k") or 0) == 8, f"invalid K8 pool identity: {task_id}")
        trajectories = pool.get("trajectories") or []
        require(len(trajectories) == 8, f"K8 pool missing trajectory refs: {task_id}")
        scores = [float(row["score"]) for row in trajectories]
        is_mixed = int(min(scores) < 1.0 and max(scores) >= 1.0)
        mixed_recomputed += is_mixed
        per_stream_mixed[task_to_stream[task_id]] += is_mixed
        family = str(metadata[task_id]["primary_failure_family"])
        per_family_mixed[family] = per_family_mixed.get(family, 0) + is_mixed
        for row in trajectories:
            trajectory = Path(row["trajectory_path"])
            require(trajectory.exists() and sha_file(trajectory) == row["trajectory_sha256"], f"trajectory SHA drift: {task_id}/{row['rollout_index']}")
        pool_sha[task_id] = sha_file(pool_path)
    require(mixed_recomputed == mixed, "mixed-pool total does not recompute from exact frozen pools")
    exposed_recomputed = sum(int(value >= min_per_stream) for value in per_stream_mixed.values())
    require(exposed_recomputed == exposed, "exposed-stream count does not recompute directly from exact frozen pools")
    supported_families_recomputed = sum(int(value > 0) for value in per_family_mixed.values())
    require(supported_families_recomputed == supported_families, "supported-family count does not recompute directly from exact frozen pools")
    summary_stream_map = {str(row["stream_id"]): int(row["mixed_pools"]) for row in stream_rows}
    require(summary_stream_map == per_stream_mixed, "summary per-stream mixed counts drift from exact frozen pools")
    require(dict(sorted((support.get("family_mixed_counts") or {}).items())) == dict(sorted(per_family_mixed.items())), "summary family mixed counts drift from exact frozen pools")
    require(bool(support.get("primary_hard_gate_pass")) == (mixed >= min_mixed and exposed >= min_exposed), "hard-gate flag is inconsistent")
    require(bool(support.get("family_generalization_gate_pass")) == (supported_families >= min_families), "family gate flag is inconsistent")

    hard_pass = mixed >= min_mixed and exposed >= min_exposed
    family_pass = supported_families >= min_families
    status = "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT" if hard_pass else "STOP_E1_SUPPORT_INSUFFICIENT"
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-e1-a-pool-support-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "summary_path": str(args.summary),
        "summary_sha256": sha_file(args.summary),
        "integrity": {
            "streams": 12,
            "tasks": 96,
            "actor_rollouts": 768,
            "frozen_k8_pools": 96,
            "all_trajectory_shas_revalidated": True,
            "task_replacement_after_support_observation": False,
            "waiver_or_rounding": False,
            "updater_calls": 0,
        },
        "primary_support": {
            "mixed_pools": mixed,
            "required_mixed_pools": min_mixed,
            "exposed_streams": exposed,
            "required_exposed_streams": min_exposed,
            "mixed_per_exposed_stream": min_per_stream,
            "per_stream_mixed_recomputed": per_stream_mixed,
            "pass": hard_pass,
        },
        "family_generalization": {
            "supported_families": supported_families,
            "required_supported_families": min_families,
            "pass": family_pass,
            "per_family_mixed_recomputed": dict(sorted(per_family_mixed.items())),
            "controls_primary_e1_b_authorization": False,
            "claim_if_failed": "Block family-generalization and prospective family-ranking claims; pooled E1-B may still be contracted only if primary support passes."
        },
        "pool_sha256": pool_sha,
        "interpretation": (
            "This adjudication evaluates only pre-treatment mixed-pool support and protocol integrity. "
            "It does not evaluate MRW, WIN, RB-AGG, future skill utility, or paper effectiveness."
        ),
        "authority": {
            "prepare_e1_b_contract": hard_pass,
            "execute_e1_b": False,
            "provider_runtime_pilot": False,
            "paper_promotion": False,
            "submission": False,
        },
        "next_gate": (
            "SEPARATE_IMMUTABLE_E1_B_CONTRACT_WITH_FRESH_UPDATER_IDENTITY_AND_NEGATIVE_CONTROL_FIRST"
            if hard_pass
            else "STOP_CENTRAL_R17_ON_CURRENT_CONTROLLED_SUBSTRATE_SUPPORT"
        ),
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if hard_pass else 3


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: provider_budget_tests | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/test_e2_r17_provider_budget.py =====
from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.e2_r17_ark_plan_react import ArkPlanReactLLM
from research_pipeline.e2_r17_provider_budget import (
    ProviderBudgetBindingError,
    ProviderBudgetExceeded,
    ProviderBudgetLedger,
)


class ProviderBudgetTests(unittest.TestCase):
    def settings(self) -> ArkSettings:
        return ArkSettings(
            api_key="test-key",
            base_url="https://ark.cn-beijing.volces.com/api/plan/v3",
            default_model="ark-code-latest",
            timeout_seconds=30,
            max_retries=0,
        )

    @staticmethod
    def successful_response() -> dict[str, object]:
        return {
            "requested_model": "deepseek-v4-pro",
            "resolved_model": "deepseek-v4-pro-ga-260813",
            "text": "done",
            "function_calls": [],
            "usage": {"input_tokens": 2, "output_tokens": 1, "total_tokens": 3},
            "response_id": "resp-secret",
            "status": "completed",
        }

    def make_ledger(self, root: Path, *, total: int, per_unit: int) -> ProviderBudgetLedger:
        return ProviderBudgetLedger(
            path=root / "provider_budget.sqlite3",
            contract_sha256="a" * 64,
            authorization_sha256="b" * 64,
            total_limit=total,
            per_unit_limit=per_unit,
            allow_create=True,
        )

    def test_eleventh_rollout_call_is_rejected_before_provider_io(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = self.make_ledger(Path(tmp), total=100, per_unit=10)
            llm = ArkPlanReactLLM(
                settings=self.settings(),
                requested_model="deepseek-v4-pro",
                required_resolved_model="deepseek-v4-pro-ga-260813",
                provider_budget_ledger=ledger,
                provider_budget_unit_id="task-1/rollout_0",
            )
            provider_calls = 0

            def fake_respond(*args, **kwargs):
                nonlocal provider_calls
                provider_calls += 1
                return self.successful_response()

            llm.client.respond = fake_respond
            for _ in range(10):
                asyncio.run(llm([{"role": "user", "content": "x"}], []))
            self.assertEqual(provider_calls, 10)
            with self.assertRaisesRegex(ProviderBudgetExceeded, "per-unit call budget exhausted before I/O"):
                asyncio.run(llm([{"role": "user", "content": "x"}], []))
            self.assertEqual(provider_calls, 10)
            snapshot = ledger.snapshot()
            self.assertEqual(snapshot.unit_claimed["task-1/rollout_0"], 10)
            self.assertEqual(snapshot.total_claimed, 10)
            receipts = llm.public_receipts()
            self.assertEqual(receipts[-1]["provider_budget_unit_call_index"], 10)
            self.assertEqual(receipts[-1]["provider_budget_total_claimed_after"], 10)

    def test_7681st_global_call_is_rejected_before_provider_io(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = self.make_ledger(Path(tmp), total=7680, per_unit=10)
            for index in range(7680):
                ledger.claim(f"prefill-{index // 10}")
            self.assertEqual(ledger.snapshot().total_claimed, 7680)

            llm = ArkPlanReactLLM(
                settings=self.settings(),
                requested_model="deepseek-v4-pro",
                required_resolved_model="deepseek-v4-pro-ga-260813",
                provider_budget_ledger=ledger,
                provider_budget_unit_id="new-task/rollout_0",
            )
            provider_calls = 0

            def fake_respond(*args, **kwargs):
                nonlocal provider_calls
                provider_calls += 1
                return self.successful_response()

            llm.client.respond = fake_respond
            with self.assertRaisesRegex(ProviderBudgetExceeded, "total call budget exhausted before I/O"):
                asyncio.run(llm([{"role": "user", "content": "x"}], []))
            self.assertEqual(provider_calls, 0)
            self.assertEqual(ledger.snapshot().total_claimed, 7680)

    def test_contract_or_authorization_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "provider_budget.sqlite3"
            ProviderBudgetLedger(
                path=path,
                contract_sha256="a" * 64,
                authorization_sha256="b" * 64,
                total_limit=20,
                per_unit_limit=10,
                allow_create=True,
            )
            with self.assertRaises(ProviderBudgetBindingError):
                ProviderBudgetLedger(
                    path=path,
                    contract_sha256="c" * 64,
                    authorization_sha256="b" * 64,
                    total_limit=20,
                    per_unit_limit=10,
                    allow_create=False,
                )


if __name__ == "__main__":
    unittest.main()


===== BOUND ARTIFACT: fresh_model_identity_adjudication | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-v2-1-model-identity-adjudication-20260828.json =====
{
  "adjudication": "The initial Kimi Auto/default-thinking smokes are retained as explicit incomplete-length protocol failures. The passing Kimi qualification is a separately declared compatibility call with thinking disabled. DeepSeek resolves to the current GA release rather than the historical 260425 suffix. These observed identities are frozen only for the current pre-execution review tranche and must be requalified before any later scientific tranche.",
  "artifact_type": "e2-r17-current-plan-model-identity-adjudication",
  "authority": {
    "gpu": false,
    "paper_promotion": false,
    "preexecution_consultation": true,
    "scientific_experiment": false,
    "submission": false
  },
  "checks": {
    "deepseek_pass": true,
    "kimi_pass": true,
    "no_hidden_provider_retry": true,
    "provider_retry_zero": true,
    "resolved_identities_distinct": true,
    "route_is_ark_plan": true
  },
  "compatibility_history": [
    {
      "path": "generated/e2-r17-e1-a-v2-1-model-identity-qualification-20260828.json",
      "sha256": "08982d439f46bea48b73d1dc09d7af1504eda5ba725738bcf4d785a2fa32fa54",
      "status": "PASS"
    }
  ],
  "created_at_utc": "2026-08-28T14:19:07+00:00",
  "private_credentials_included": false,
  "raw_response_ids_included": false,
  "requested_and_resolved": {
    "deepseek-v4-pro": {
      "requested": "deepseek-v4-pro",
      "resolved": "deepseek-v4-pro-ga-260813",
      "source_artifact": "generated/e2-r17-e1-a-v2-1-model-identity-qualification-20260828.json",
      "source_artifact_sha256": "08982d439f46bea48b73d1dc09d7af1504eda5ba725738bcf4d785a2fa32fa54",
      "thinking_requested": "disabled"
    },
    "kimi-k3": {
      "requested": "kimi-k3",
      "resolved": "kimi-k3",
      "source_artifact": "generated/e2-r17-e1-a-v2-1-model-identity-qualification-20260828.json",
      "source_artifact_sha256": "08982d439f46bea48b73d1dc09d7af1504eda5ba725738bcf4d785a2fa32fa54",
      "thinking_requested": "disabled"
    }
  },
  "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
  "schema_version": "1.0",
  "status": "PASS_CURRENT_REVIEW_TRANCHE"
}


===== BOUND ARTIFACT: fresh_model_identity_qualification | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-v2-1-model-identity-qualification-20260828.json =====
{
  "artifact_type": "e2-r17-current-ark-plan-model-identity-qualification",
  "authority": {
    "gpu": false,
    "paper_promotion": false,
    "preexecution_consultation": true,
    "scientific_experiment": false,
    "submission": false
  },
  "checks": {
    "all_protocol_calls_pass": true,
    "provider_retry_zero": true,
    "resolved_identities_distinct": true,
    "route_is_ark_plan": true
  },
  "compatibility_parent": null,
  "created_at_utc": "2026-08-28T14:19:07+00:00",
  "default_model": "ark-code-latest",
  "models": [
    {
      "benchmark_data_accessed": false,
      "checks": {
        "resolved_model_matches_requested_family": true,
        "resolved_model_present": true,
        "text_exact": true
      },
      "get_poll_recovery": false,
      "hidden_provider_retry_used": false,
      "max_output_tokens": 256,
      "poll_count": 0,
      "prompt_sha256": "7bfaf5897d7bbd7f972a67554ee32acc828cd8309e40822dfc05217e987776bf",
      "provider_generation_attempts": 1,
      "provider_retry_limit": 0,
      "provider_status": "completed",
      "raw_text": "PLAN_OK",
      "raw_text_sha256": "aa6b4c1b97751f326153c1927c1106bf5a927ec506a8066dfe0dded595992d7c",
      "requested_model": "deepseek-v4-pro",
      "resolved_model": "deepseek-v4-pro-ga-260813",
      "response_id_sha256": "e9a99ca16f994e16908f91a7dd0f9f4fe48ac7bcc08271f81cc6098c62c8c49a",
      "scientific_outcome": false,
      "status": "PASS",
      "thinking_requested": "disabled",
      "usage": {
        "input_tokens": 27,
        "input_tokens_details": {
          "cached_tokens": 0
        },
        "output_tokens": 3,
        "output_tokens_details": {
          "reasoning_tokens": 0
        },
        "total_tokens": 30
      }
    },
    {
      "benchmark_data_accessed": false,
      "checks": {
        "resolved_model_matches_requested_family": true,
        "resolved_model_present": true,
        "text_exact": true
      },
      "get_poll_recovery": false,
      "hidden_provider_retry_used": false,
      "max_output_tokens": 256,
      "poll_count": 0,
      "prompt_sha256": "7bfaf5897d7bbd7f972a67554ee32acc828cd8309e40822dfc05217e987776bf",
      "provider_generation_attempts": 1,
      "provider_retry_limit": 0,
      "provider_status": "completed",
      "raw_text": "PLAN_OK",
      "raw_text_sha256": "aa6b4c1b97751f326153c1927c1106bf5a927ec506a8066dfe0dded595992d7c",
      "requested_model": "kimi-k3",
      "resolved_model": "kimi-k3",
      "response_id_sha256": "ab55e1b1cff02303d5f4d36fa532a36e341267c2cb5fd0f78a6b624a9c0c892d",
      "scientific_outcome": false,
      "status": "PASS",
      "thinking_requested": "disabled",
      "usage": {
        "input_tokens": 41,
        "input_tokens_details": {
          "cached_tokens": 0
        },
        "output_tokens": 13,
        "output_tokens_details": {
          "reasoning_tokens": 0
        },
        "total_tokens": 54
      }
    }
  ],
  "private_credentials_included": false,
  "raw_response_ids_included": false,
  "release_drift_policy": "Observed resolved identities are frozen for this review tranche. Historical exact suffixes are not reused as authority. Any later execution tranche must requalify and bind its own observed identities.",
  "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
  "schema_version": "1.0",
  "status": "PASS"
}


===== BOUND ARTIFACT: suite_manifest | /data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2/suite_manifest.json =====
{
  "blocks": {
    "0": "development",
    "1": "e0_calibration",
    "2": "e1_update_candidate",
    "3": "e1_update_candidate",
    "4": "e1_heldout_probe_candidate",
    "5": "e3_future_candidate",
    "6": "e3_future_candidate"
  },
  "dataset_json_sha256": "1c19789dd25238c326ad32125de05dcf09ae9db627e735285717b439fe8afe47",
  "dataset_sha256": "4b5ec329f32855e1d358bcf63dd1781a8861f9f0d44f8f0b12af8a798da0a87a",
  "factor_names": [
    "procedure_depth_level",
    "distractor_level",
    "schema_ambiguity_level"
  ],
  "families": [
    "input_output_contract",
    "target_sheet_range",
    "schema_key_alignment",
    "aggregation_join",
    "formula_materialization",
    "multi_step_pipeline"
  ],
  "family_count": 6,
  "files": [
    {
      "path": "r17_controlled_metadata.json",
      "sha256": "12d6eb876e2a230e7990be3e61fed108d45f6ddec00bac5c9b88585a04111b04",
      "size": 311568
    },
    {
      "path": "r17_split_manifest.json",
      "sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
      "size": 8086
    },
    {
      "path": "spreadsheetbench_id_split/test/items.json",
      "sha256": "ddf5eb6d9085d20d34f445af62b9e883ff908681bf3dd6c5e2fe3e9d55e93cd4",
      "size": 3783
    },
    {
      "path": "spreadsheetbench_id_split/train/items.json",
      "sha256": "7872c137cf7042fefa4ebf9eb33ecdff477bad495a3ac9e1a34a2cb7c9e01e4f",
      "size": 6093
    },
    {
      "path": "spreadsheetbench_id_split/val/items.json",
      "sha256": "527325806a3481b7d59319cdbad21fe9d6721aa3eb0945b963990cd58b4986ea",
      "size": 633
    },
    {
      "path": "spreadsheetbench_verified_400/dataset.json",
      "sha256": "1c19789dd25238c326ad32125de05dcf09ae9db627e735285717b439fe8afe47",
      "size": 200728
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p0/r17-b0-agj-p0_golden.xlsx",
      "sha256": "c3ea57a6257d4e94d02a1b78c5f0cf050087c800d4f0dbd837e93836b157f63d",
      "size": 7218
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p0/r17-b0-agj-p0_init.xlsx",
      "sha256": "ae9ca3f7b88db1d413ccb9816f2c40430206acd65bc639b5fb37a33eaa89e422",
      "size": 7197
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p1/r17-b0-agj-p1_golden.xlsx",
      "sha256": "73dc3bc9576f5dd366c3df8d88ca4011a2f7fb7aa2df08d95b9c66300664ce59",
      "size": 8602
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p1/r17-b0-agj-p1_init.xlsx",
      "sha256": "42c1e49f24b73b830a7f09685fd7d6fd3c6ed5c09969f90e79b63c9491209e91",
      "size": 8581
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p2/r17-b0-agj-p2_golden.xlsx",
      "sha256": "23ee6f911cd71540c7433d0a331ec47ac9955a93e5294e262fabe1350c7773de",
      "size": 10705
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p2/r17-b0-agj-p2_init.xlsx",
      "sha256": "4da2dfcf474f0d1ac3aa0a3f0cd9a946f6caf44bbaad931dca76b1401735933b",
      "size": 10684
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p3/r17-b0-agj-p3_golden.xlsx",
      "sha256": "2d9c9c4a39a8dbf23f12ad9cb38cc9353e863c5d26bd847f2944bade9d84fb0b",
      "size": 7319
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p3/r17-b0-agj-p3_init.xlsx",
      "sha256": "53b047d3f01648fe30337598cd6f6ad0a9c533966a90a51874045db36f228ad8",
      "size": 7299
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p4/r17-b0-agj-p4_golden.xlsx",
      "sha256": "55f0d7b0b4c14782e7a8121337e08803fa2b099becd6349970f51e81ec6ad92b",
      "size": 8734
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p4/r17-b0-agj-p4_init.xlsx",
      "sha256": "bd7f9433a477399b958f7a65cd9907205baf656cf4985cf6a17e24afccb57395",
      "size": 8713
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p5/r17-b0-agj-p5_golden.xlsx",
      "sha256": "8c9822a647d97f59e89a7eaa919a939b5b64150d4c71482ff58ece0403ba70ae",
      "size": 10798
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p5/r17-b0-agj-p5_init.xlsx",
      "sha256": "bd80df63e9736842013ec4f4085bad5729053f37b05d6ae18668f30bb3cb416c",
      "size": 10778
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p6/r17-b0-agj-p6_golden.xlsx",
      "sha256": "bf35830bc94eff9cbe14863e0eba2feb9fc1ec56b801351debe3042f0e51b755",
      "size": 7459
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p6/r17-b0-agj-p6_init.xlsx",
      "sha256": "30ebf66352d63148562b0ce35b1ca6ed0f0597cbf943d78dd37ac2b5a254550e",
      "size": 7427
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p7/r17-b0-agj-p7_golden.xlsx",
      "sha256": "aa9be6d7535e991ffc3b70363cf0518b9c5e523fb19408eabac2cdd47184e48e",
      "size": 8847
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p7/r17-b0-agj-p7_init.xlsx",
      "sha256": "e6ba4e94a36c2309668ba63e636dba66a8f4c5f816e5bc97060a10233336aa81",
      "size": 8813
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p8/r17-b0-agj-p8_golden.xlsx",
      "sha256": "3805cdf6c74ae1b7f3bd857b219e90de80c8951418708a07a339cc5cf56055de",
      "size": 10913
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-agj-p8/r17-b0-agj-p8_init.xlsx",
      "sha256": "e8686fddd95a8880529e5498c79af1dc0805100d57f1cafe29ae1608c2be6637",
      "size": 10883
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p0/r17-b0-fmv-p0_golden.xlsx",
      "sha256": "ae2d7ec0164378e854aee43fa046977ec91fa4bf26b720141bfcffbe09a910d2",
      "size": 5704
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p0/r17-b0-fmv-p0_init.xlsx",
      "sha256": "2f64ba132ae0244f87caf4df983d6e37e9c54fd14f564c8a8cdeb61ea94aa7dd",
      "size": 5657
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p1/r17-b0-fmv-p1_golden.xlsx",
      "sha256": "8e0b53bcfe7f6f3477e47b3e61d37d213e57cbde7cb2793a9a3086cafe0123f9",
      "size": 7141
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p1/r17-b0-fmv-p1_init.xlsx",
      "sha256": "582a951e0b0c701ec8cb1626989484a7597316e9377aac73fba508cbe983e7a6",
      "size": 7092
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p2/r17-b0-fmv-p2_golden.xlsx",
      "sha256": "03e8f2b74924b909ef464c516538a24c7df23829b85a2113921cef7cc8c8b2eb",
      "size": 9289
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p2/r17-b0-fmv-p2_init.xlsx",
      "sha256": "39b9db99c02aa989d6c5c87470a509e10a032495f8c0e5ea05894053c8cad6f8",
      "size": 9241
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p3/r17-b0-fmv-p3_golden.xlsx",
      "sha256": "0a9320c177037de8e97ce6757658ce2f37e962b518589cd49632d5daf68fbc30",
      "size": 5821
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p3/r17-b0-fmv-p3_init.xlsx",
      "sha256": "ad84af352f62690541bf07f75cdd9642a529994fa3444edccb68896fc0dbf9d4",
      "size": 5759
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p4/r17-b0-fmv-p4_golden.xlsx",
      "sha256": "563c67f7a0cc4297be11d59b3bb1d66bf1c3635c875101c5f981a7f046eb3ba1",
      "size": 7298
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p4/r17-b0-fmv-p4_init.xlsx",
      "sha256": "9462f9f7cca4f850895944a9084c76db843b15b937cec3fb9e31886f3cb483fc",
      "size": 7231
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p5/r17-b0-fmv-p5_golden.xlsx",
      "sha256": "f340e1ef95c481b098c4169567b52e296c4a9d35879a98fa26b330e3a6279414",
      "size": 9259
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p5/r17-b0-fmv-p5_init.xlsx",
      "sha256": "e576821365f3f497f404843ab23c9ce3d4c298196b5659fea827d924325b2670",
      "size": 9198
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p6/r17-b0-fmv-p6_golden.xlsx",
      "sha256": "b87db975934a163fb161b901a77c282de02b8e77668bf28210fb958b61ef9517",
      "size": 5987
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p6/r17-b0-fmv-p6_init.xlsx",
      "sha256": "27c83ea9d8bc5e54c4722026156fe825c220dad5c2b3d80e5b827ce5b34b8616",
      "size": 5901
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p7/r17-b0-fmv-p7_golden.xlsx",
      "sha256": "6a353c6f64a15594a9d941f4df06ca8cbb6bec60471796384394f8959cd0e45a",
      "size": 7261
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p7/r17-b0-fmv-p7_init.xlsx",
      "sha256": "6f13283541e7a39f5866f673694fbcf89ee66e5c7f4887e07958f11f1a407f84",
      "size": 7174
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p8/r17-b0-fmv-p8_golden.xlsx",
      "sha256": "28098852f0fa28af12e9ecdebbc77eb33619f516233a8c52ae63b39c4475cfa8",
      "size": 9406
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-fmv-p8/r17-b0-fmv-p8_init.xlsx",
      "sha256": "bee435ddbf9663a7783df40af59f61a1ec1f0607a2ad77b95c55a56261af85f4",
      "size": 9315
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p0/r17-b0-ioc-p0_golden.xlsx",
      "sha256": "0a0e1393bf17ff0ee23496be60f1dec56c1a2aa86e0daa7bae63b1204125142c",
      "size": 5646
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p0/r17-b0-ioc-p0_init.xlsx",
      "sha256": "4e004924f5ef4ffe1b37768a6dbb0e3ed4645ba542eca6a7d9f74e31faaf1783",
      "size": 5620
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p1/r17-b0-ioc-p1_golden.xlsx",
      "sha256": "fcd5f113e239ee29beea947ecc179e33358a4a25c4d647755289991b0239bc3b",
      "size": 7103
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p1/r17-b0-ioc-p1_init.xlsx",
      "sha256": "c10267f9aff81ef31242ab2e0ade661f44913d5de9d2b82946500f8cead97c5a",
      "size": 7076
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p2/r17-b0-ioc-p2_golden.xlsx",
      "sha256": "38dfac360111a605585888f5c7bc81787d060cf13a73567240a7d0e71034ca2a",
      "size": 9274
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p2/r17-b0-ioc-p2_init.xlsx",
      "sha256": "6f56cd48c670623c94e6b8d257efb7d28fd7dcb79c34feea92c58db738d41eb0",
      "size": 9248
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p3/r17-b0-ioc-p3_golden.xlsx",
      "sha256": "43884c7a7ddf6961b2fd7e9cb3dd9f63a652994a1a8a49f99c735e8da7576eb8",
      "size": 5756
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p3/r17-b0-ioc-p3_init.xlsx",
      "sha256": "e778589f84b63f49f3a31a6fde1553e6b68135b0587c20c3dc34d3c1fe9521fd",
      "size": 5723
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p4/r17-b0-ioc-p4_golden.xlsx",
      "sha256": "bab2fd4dec1b00e1b07a8f26da83a603002ce1b332ca204223f72cbfbb101e7c",
      "size": 7268
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p4/r17-b0-ioc-p4_init.xlsx",
      "sha256": "b9d711e77a9baee90c86f976078071f939958336ab904acb6a450008ccca8fd8",
      "size": 7237
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p5/r17-b0-ioc-p5_golden.xlsx",
      "sha256": "d092d64a15312ca40fff7268a4d679b6d498135e11aa33264cbd0558193b6b9e",
      "size": 9182
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p5/r17-b0-ioc-p5_init.xlsx",
      "sha256": "b5919e0fcee36b1b6edbf89098c979cc3aedf84dba243f0817ab480db42c2dbf",
      "size": 9149
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p6/r17-b0-ioc-p6_golden.xlsx",
      "sha256": "1c3581d3ef6b74770b14c94aa85f3ee4e9180d8de8b7fa10846ed0061928c8c7",
      "size": 5938
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p6/r17-b0-ioc-p6_init.xlsx",
      "sha256": "ec2cc3eb4e5d0c57526d192e4a72a8a5ad7b2e66069ca8d5e13f7f3117e62f05",
      "size": 5900
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p7/r17-b0-ioc-p7_golden.xlsx",
      "sha256": "1651fc9dcab3f85d8ffc154e373e534149ee549dc28275c625dc7a8185828894",
      "size": 7140
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p7/r17-b0-ioc-p7_init.xlsx",
      "sha256": "536fe9e06094302ad372c002b8e37661dee3b5f155f824166f50f7a2572ca459",
      "size": 7103
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p8/r17-b0-ioc-p8_golden.xlsx",
      "sha256": "3de0f92040436393449b3ff2d88d0bd7bed74f5e40b9cf5b4b4c1222eb75c183",
      "size": 9294
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ioc-p8/r17-b0-ioc-p8_init.xlsx",
      "sha256": "b34691f21654093d913e069baeb22a94f9cea327d5394374ca71478d17db8263",
      "size": 9256
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p0/r17-b0-msp-p0_golden.xlsx",
      "sha256": "460f43a5db4421e3c180e2ac2c2974398effa91db16a40b5428bdcf0988d692b",
      "size": 7426
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p0/r17-b0-msp-p0_init.xlsx",
      "sha256": "a504787b623a35ca693bf0ae2017185748a0820bf6eb84ef3adb34a5e7146951",
      "size": 7397
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p1/r17-b0-msp-p1_golden.xlsx",
      "sha256": "c7a2a4783fdb6be8679c74ae78b98c030a92c8acc461f795b6e8ec892957c94e",
      "size": 8856
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p1/r17-b0-msp-p1_init.xlsx",
      "sha256": "e5f63ebeae922d423946383f4e8336d05ded8871500e6465d292b298bffe4bb4",
      "size": 8826
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p2/r17-b0-msp-p2_golden.xlsx",
      "sha256": "3681254ee86b86d8c7e5f2e6b751832daf4cbe515b269b7561ecb89f0bec070c",
      "size": 10957
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p2/r17-b0-msp-p2_init.xlsx",
      "sha256": "dd58eef56e12fda2b2edd6a887dedd61afe84d0cc764340be5eed40fd10b7818",
      "size": 10927
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p3/r17-b0-msp-p3_golden.xlsx",
      "sha256": "ce76cf696292a366a8417618483cece4577fb61bcaadabe39ae09f438cf80a76",
      "size": 7613
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p3/r17-b0-msp-p3_init.xlsx",
      "sha256": "d1a87030ce55940da8d42025841b23f69a888e11b4436a402ba50dd322ba99fe",
      "size": 7584
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p4/r17-b0-msp-p4_golden.xlsx",
      "sha256": "6e6b46ec625199405d630026b1785b1bba71e7259e3a11b2838193feec2abbde",
      "size": 9020
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p4/r17-b0-msp-p4_init.xlsx",
      "sha256": "0026843d5d9aced425ddfda08c9b5be7f6e83a3e10d80cc1b2d6f733c21c1da8",
      "size": 8992
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p5/r17-b0-msp-p5_golden.xlsx",
      "sha256": "395b8931fa79b491f4e26c9c101df384919605d4fbd87e9e6f06dbf1300d8334",
      "size": 11040
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p5/r17-b0-msp-p5_init.xlsx",
      "sha256": "4ab5b9033e67d5b22e8de0338a976140e6a2220d807021ab51b7fdc57084c88a",
      "size": 11012
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p6/r17-b0-msp-p6_golden.xlsx",
      "sha256": "e09a58a415e63462c2ea1ed3a726c788395034c64b457b6bc8b8a5ccb53182f8",
      "size": 7740
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p6/r17-b0-msp-p6_init.xlsx",
      "sha256": "84f59c270d3e26e593f80d3ecd8d59741c199e01a9728cda19729b1a2b89b081",
      "size": 7719
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p7/r17-b0-msp-p7_golden.xlsx",
      "sha256": "00983357021f92871aaabe9c8991d9c4884170c50762514dd14faf76f67d17cb",
      "size": 9093
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p7/r17-b0-msp-p7_init.xlsx",
      "sha256": "28e40b200a5cfb6302390050d98e60c1fc533ddc166dc9e3ed5a105e33f0bbfc",
      "size": 9073
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p8/r17-b0-msp-p8_golden.xlsx",
      "sha256": "f0c8ecf0e6f1a436d700a35678efa7475137a3deb19fd144b9be7cb4708b4714",
      "size": 11209
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-msp-p8/r17-b0-msp-p8_init.xlsx",
      "sha256": "95cbfe9f968be09557dcd3a3745403bbe9bda4fa12a57cd76d47484e91abed3b",
      "size": 11188
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p0/r17-b0-ska-p0_golden.xlsx",
      "sha256": "e98912126a535eee9dd2e8f6d9c8f42c9d6be338c6f9dddf16221dc2df109721",
      "size": 6310
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p0/r17-b0-ska-p0_init.xlsx",
      "sha256": "649735b9885398a4f648b7577329d46b51880567f4f570e0265df185444acfc8",
      "size": 6293
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p1/r17-b0-ska-p1_golden.xlsx",
      "sha256": "04d7c71c70c05a2b4811362efd461b929d495a8a54489bab1bb4bd78fabc8030",
      "size": 7782
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p1/r17-b0-ska-p1_init.xlsx",
      "sha256": "aa68399f6b87c4005246835aefbd5405e4e7ee6f5160b6b3c8e4df63b629c926",
      "size": 7763
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p2/r17-b0-ska-p2_golden.xlsx",
      "sha256": "30ca3ef8c14110205c72b9de868f3eb2e4d671e32c91cecc46636d93d22ad1b1",
      "size": 9942
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p2/r17-b0-ska-p2_init.xlsx",
      "sha256": "0258fefc8f0c9d917ddc29af8bba8c02cb8197e0539686269bcaf3fddfbd84ef",
      "size": 9924
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p3/r17-b0-ska-p3_golden.xlsx",
      "sha256": "73db10f6a42351c0b19170e6455d9476fd42c4e65e14d27ab95e955e9ea3c5ad",
      "size": 6472
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p3/r17-b0-ska-p3_init.xlsx",
      "sha256": "2a1c63fb99d6a9cad02db45c66409a11e9f7b3dd8ef4c9f89f323d609a599719",
      "size": 6444
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p4/r17-b0-ska-p4_golden.xlsx",
      "sha256": "3df0606c3e3f1c36959ac40202d6f7812b6900c4f9a99ac6ef2e46c5977723d3",
      "size": 7961
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p4/r17-b0-ska-p4_init.xlsx",
      "sha256": "59c0b201a5a149a1fe9bf7a5d8014393b41468314ca75fca6fa31376da2dab2d",
      "size": 7933
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p5/r17-b0-ska-p5_golden.xlsx",
      "sha256": "dcc55600c4d3c636d0121f797563c011eb52324c15564e6f7500fc5687a79b06",
      "size": 9858
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p5/r17-b0-ska-p5_init.xlsx",
      "sha256": "be368c4ecd29383783ca68aa34b0dacf89c9b1f746a14d8b5032bf6a533fad7a",
      "size": 9830
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p6/r17-b0-ska-p6_golden.xlsx",
      "sha256": "2bdd643a1a9e67c3079ab9e36c56a86a54f24dc765b8b8fef764b87846391388",
      "size": 6648
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p6/r17-b0-ska-p6_init.xlsx",
      "sha256": "d2d29f3d9efe17682895fcb328fdd49633d774839b3800fbb4af742cd254f00e",
      "size": 6611
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p7/r17-b0-ska-p7_golden.xlsx",
      "sha256": "50a016cc1a2e847e41bbc36cac1d8d35de35b543e9bf47b5c30af8a2a0de1410",
      "size": 7836
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p7/r17-b0-ska-p7_init.xlsx",
      "sha256": "bcc46a121bbe5d0c22ef80426c6f1083dad3af43345818da7367b218867b4260",
      "size": 7798
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p8/r17-b0-ska-p8_golden.xlsx",
      "sha256": "f6bb9a9b8fadfe024b4917fad5117104bd1d6b358675d313bd650845daa22b80",
      "size": 10023
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-ska-p8/r17-b0-ska-p8_init.xlsx",
      "sha256": "d4f07e4a1319a5d7b904f530fd22bd5d192f771b1443e5532270f1f2e293418e",
      "size": 9984
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p0/r17-b0-tsr-p0_golden.xlsx",
      "sha256": "6295c429450664e1095533f2df61c6d53f1ca10bfc9374361cc87459bae7afac",
      "size": 5614
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p0/r17-b0-tsr-p0_init.xlsx",
      "sha256": "eeaca484c1b18c7fe8cf2ffe0f6c9914bdb45d17ccab28787a7ef41d12416b4e",
      "size": 5592
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p1/r17-b0-tsr-p1_golden.xlsx",
      "sha256": "abb7949c134c8416d6242c9112817dcb882e8a95a6f1e1caa1f111d85647b2dc",
      "size": 7641
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p1/r17-b0-tsr-p1_init.xlsx",
      "sha256": "87a09e95db8bcc8d709a4450deaa884bad4639fd9c5a733d4ba172a4fcc5f272",
      "size": 7618
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p2/r17-b0-tsr-p2_golden.xlsx",
      "sha256": "6f3b9e307cd56f20338362a19df7c276c3fbbe1690e9db3921b00e5e57a77a6e",
      "size": 10986
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p2/r17-b0-tsr-p2_init.xlsx",
      "sha256": "0d0cfb05fb1d8992526fe410939926b747c1aa2c0e13c1cac7e215ce2d8754fc",
      "size": 10963
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p3/r17-b0-tsr-p3_golden.xlsx",
      "sha256": "cb0298c2a8f65eecc39529b4c2cfa4d973fa307d362e0586ed9174f4ebd4be82",
      "size": 6325
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p3/r17-b0-tsr-p3_init.xlsx",
      "sha256": "8cb76618d2b2b0cd69c05087e11e8a744bcb143890ace48189ca9f2759758e13",
      "size": 6293
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p4/r17-b0-tsr-p4_golden.xlsx",
      "sha256": "3247b171aa934663ce6276e82746212cf14d0d70de7d9fb8b6bc7d908945f79a",
      "size": 9057
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p4/r17-b0-tsr-p4_init.xlsx",
      "sha256": "93fb80f8d91d1dbd54029510fd30cace405ca10714b40738831c9c05212689c7",
      "size": 9025
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p5/r17-b0-tsr-p5_golden.xlsx",
      "sha256": "ff807ec32d1ab479c4d144dc888e6c52ead7626b0f288655872ef1ac04d888f3",
      "size": 9144
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p5/r17-b0-tsr-p5_init.xlsx",
      "sha256": "09374a4b64ea9b5a37c1448f0028e5f3898ef779934e378fbd7a3000aa323c4b",
      "size": 9111
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p6/r17-b0-tsr-p6_golden.xlsx",
      "sha256": "7a19f7b4f36bc0dd55e41188303fabd0604321665a3167e1420d0068b501beaf",
      "size": 7843
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p6/r17-b0-tsr-p6_init.xlsx",
      "sha256": "fababeca05ab5645f60d41be890a75dc02b987c77fa149f3d856fc01e8c8184e",
      "size": 7806
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p7/r17-b0-tsr-p7_golden.xlsx",
      "sha256": "4765ca4f009da98db03c4a084fa3f1b17786c994f83ab1df68e58be25764eca1",
      "size": 7111
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p7/r17-b0-tsr-p7_init.xlsx",
      "sha256": "80bb4897a484d3a2e8913c0a787dfb294c2d9df64f67e601b8c170fb6a897ffb",
      "size": 7072
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p8/r17-b0-tsr-p8_golden.xlsx",
      "sha256": "0b36d9e74a772f676fc44b19ac5ae9a2fcc41d5048d627d9963409771149f633",
      "size": 9894
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b0-tsr-p8/r17-b0-tsr-p8_init.xlsx",
      "sha256": "c10a042251575d6b74ea8125b81ab54558bdaf648f31bf73ca1cbe70ea4b491a",
      "size": 9857
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p0/r17-b1-agj-p0_golden.xlsx",
      "sha256": "d46af7d682b0327a57b179db1917264b90b78decb7ab16febfcb847bf29751c0",
      "size": 7219
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p0/r17-b1-agj-p0_init.xlsx",
      "sha256": "575bbac00d55ae4521655965dc781e48a2a40ec32d434125167f7d56ec99d9a3",
      "size": 7197
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p1/r17-b1-agj-p1_golden.xlsx",
      "sha256": "0c75ca43b1ef8e8a08c302272ed4a53a2535a4acef8289c9581131e28aa5ae00",
      "size": 8602
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p1/r17-b1-agj-p1_init.xlsx",
      "sha256": "81418f417db5f432ac4ce0dc224daca5a0eb46be1d14e32d23c3ec355975dc1c",
      "size": 8580
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p2/r17-b1-agj-p2_golden.xlsx",
      "sha256": "22b90c10f45a9b6138eb7037ddbd0ae16c8f1de5edd2d5581d9237b4326a325a",
      "size": 10710
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p2/r17-b1-agj-p2_init.xlsx",
      "sha256": "c37389e523bdd2bee5aec5e2e79a877de6aea50d700e7ffbfca268cc01208e77",
      "size": 10689
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p3/r17-b1-agj-p3_golden.xlsx",
      "sha256": "e4648b0006e23159f73beca1852c748e29c8d4d2f0eeaf3e9bc74b4dec235b1c",
      "size": 7315
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p3/r17-b1-agj-p3_init.xlsx",
      "sha256": "8cbacfdba939e07063991748ca0b1b8be0c4d3927d88df099a89530b3c0b7b7e",
      "size": 7295
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p4/r17-b1-agj-p4_golden.xlsx",
      "sha256": "ede411eeff32a843e65e55402cab7b46b316faf6d0eaab345580acfeeb5cbdd6",
      "size": 8742
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p4/r17-b1-agj-p4_init.xlsx",
      "sha256": "311a41f5d083a61db4baadf29bda2f3f97dd73e73f9964f97218c6c543ef7a9d",
      "size": 8721
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p5/r17-b1-agj-p5_golden.xlsx",
      "sha256": "1bc643c75a133b1412be1fe559b8397f492f91000dc8cf95562e92c4d390d6c5",
      "size": 10796
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p5/r17-b1-agj-p5_init.xlsx",
      "sha256": "95c71ad27ca956a92996a2cb46804e64a17b7d3e11f4316bd4a70be5f84fc125",
      "size": 10776
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p6/r17-b1-agj-p6_golden.xlsx",
      "sha256": "2f191c00e8f2207fbb7f4ddca87cf6c7576d58c5344cf731542e599f64c8b1cb",
      "size": 7464
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p6/r17-b1-agj-p6_init.xlsx",
      "sha256": "07393bf939005d4acaa26dd1405bce3027f3d9f2e36eb7c4f6bffa8faf9bc326",
      "size": 7428
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p7/r17-b1-agj-p7_golden.xlsx",
      "sha256": "fc79b5369160a897365b0923a4ce9270b35a81f6b9c3957702c3f30bdc0e095a",
      "size": 8846
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p7/r17-b1-agj-p7_init.xlsx",
      "sha256": "650a4d8e3b5b3f2382485cd41bb4739b032b4f333c02615cf664433cbb56cc12",
      "size": 8811
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p8/r17-b1-agj-p8_golden.xlsx",
      "sha256": "0e8cae15d19478fefe7b03a39f11ede8d465c8b93b089121b25eff429ab5317e",
      "size": 10915
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-agj-p8/r17-b1-agj-p8_init.xlsx",
      "sha256": "428430ce49b282c9e252fed05703f76995112d8b50400571e335544d94ec73ca",
      "size": 10879
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p0/r17-b1-fmv-p0_golden.xlsx",
      "sha256": "7ea5e23b822b360f4d14529ff93405932b8451028a714696ca5bd6cd07d38ca1",
      "size": 5706
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p0/r17-b1-fmv-p0_init.xlsx",
      "sha256": "2521ebbbe858afcac8b3bb081c98f45f31f596b017ddd3e3c8df93f48b77e86b",
      "size": 5660
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p1/r17-b1-fmv-p1_golden.xlsx",
      "sha256": "431eb13183743f86e48ae212d8cab8bce34f414df41e1aea7c7e5e08652af846",
      "size": 7139
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p1/r17-b1-fmv-p1_init.xlsx",
      "sha256": "caaa4b5713f644fc25ea1b687901b971edb44fc083128b688be7078202db2985",
      "size": 7093
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p2/r17-b1-fmv-p2_golden.xlsx",
      "sha256": "11945afe75de9344eada5ef0ebb9461c232cf650fec8075be77b93ded75082ce",
      "size": 9280
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p2/r17-b1-fmv-p2_init.xlsx",
      "sha256": "d92c5af5116d72aa522f9a9ae8d524687d64a4c266eee072ece3af81bbeb5018",
      "size": 9234
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p3/r17-b1-fmv-p3_golden.xlsx",
      "sha256": "c8c1bf68b6bb5ab592ac18f8c693731eee988d5db58d0bafdb33a701545b441c",
      "size": 5815
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p3/r17-b1-fmv-p3_init.xlsx",
      "sha256": "65250decd87ad8d903aa6b294b8c71ad9a1cdb33250ac28773fad06430621678",
      "size": 5756
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p4/r17-b1-fmv-p4_golden.xlsx",
      "sha256": "e17ab177f7bf60302549e5b515db52c0511a2a0461141c2c8b8aea69f956efbd",
      "size": 7294
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p4/r17-b1-fmv-p4_init.xlsx",
      "sha256": "1d51bd9c6bf1ede91e9931c4949da7dc171037b1f9cff8ebdd7bc127a00246f8",
      "size": 7229
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p5/r17-b1-fmv-p5_golden.xlsx",
      "sha256": "6a1aea8deb828e12f6ab5c3ef5f232ae7a8100c2527d14b719c663e55b23b9a4",
      "size": 9259
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p5/r17-b1-fmv-p5_init.xlsx",
      "sha256": "4bc550ad1defc845eea03443a1c9d8628d06468cce9406a2bda4d2c075cb9002",
      "size": 9195
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p6/r17-b1-fmv-p6_golden.xlsx",
      "sha256": "b9bc58cc0fefa2bfbc3e45da3dca77521363d2eb79e1db8721deeaad6f5d7efe",
      "size": 5991
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p6/r17-b1-fmv-p6_init.xlsx",
      "sha256": "c251f810df72d014cbe2e06d4239b7d681b09a4843bc86aabd250dd1e3f8e562",
      "size": 5903
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p7/r17-b1-fmv-p7_golden.xlsx",
      "sha256": "fda692e0a039b850b3fd49dead12870dfd9844bb77cd586b54495877f7615c50",
      "size": 7263
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p7/r17-b1-fmv-p7_init.xlsx",
      "sha256": "f2f908f03d128636f27bbccb176a04f10910dc30061e5f1373f1fbdfeaffa507",
      "size": 7176
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p8/r17-b1-fmv-p8_golden.xlsx",
      "sha256": "022934ec0bbd8129479b4b8eb779526abaf6ba24bf2c2165ccb14abbaf1165cc",
      "size": 9395
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-fmv-p8/r17-b1-fmv-p8_init.xlsx",
      "sha256": "7f2855d99c78bd466634d3c04d582ec36b50a2ef002fb2bbf2ae356c8e3dc29d",
      "size": 9311
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p0/r17-b1-ioc-p0_golden.xlsx",
      "sha256": "ba86db82904d2fffdf9894d6bab76ab436109a2af9c52a8739e11185c4a58427",
      "size": 5649
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p0/r17-b1-ioc-p0_init.xlsx",
      "sha256": "541afc1c971872c21d49315ef8bc670f240fe1541384a7d25909c67a350bfb14",
      "size": 5622
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p1/r17-b1-ioc-p1_golden.xlsx",
      "sha256": "3d059c5045180f5b00941e403c1571e30fa995551e862a480d1e270a44e01a72",
      "size": 7104
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p1/r17-b1-ioc-p1_init.xlsx",
      "sha256": "54c7f4f8b308245a3e31ad0facc4e05f9c9d46fe4bce39fec514de09735c997a",
      "size": 7076
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p2/r17-b1-ioc-p2_golden.xlsx",
      "sha256": "c9af7a874695ad60c4fca9b8bdfb2c1e686ac030df306b19e29ca0a45903c2e1",
      "size": 9274
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p2/r17-b1-ioc-p2_init.xlsx",
      "sha256": "4940b67f149711f9563b03d4c1ac2dae41f13fdc0f65b89d67f4c67acae6ec5d",
      "size": 9248
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p3/r17-b1-ioc-p3_golden.xlsx",
      "sha256": "9f48c004fbe2029738dc5981d257e8d0d770c6de627c439c95baa057da479334",
      "size": 5760
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p3/r17-b1-ioc-p3_init.xlsx",
      "sha256": "ea675de58cbab83018ff5f290e8d102e9676c4330896fc0d54a105bfdcc453d3",
      "size": 5726
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p4/r17-b1-ioc-p4_golden.xlsx",
      "sha256": "cafeae5570e0f657b1cdf1d35e684d0d1869a90bd51eb9390f7625a0539eb34e",
      "size": 7265
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p4/r17-b1-ioc-p4_init.xlsx",
      "sha256": "b292216cb7ef2276b822135e47059ee0256be6cc8578844291f0cdccda0d92be",
      "size": 7232
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p5/r17-b1-ioc-p5_golden.xlsx",
      "sha256": "08042f45bd51248df4709fa08e9a532dbef0b5bf5f62410f3a2be25afafbe08b",
      "size": 9179
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p5/r17-b1-ioc-p5_init.xlsx",
      "sha256": "eeebaeb0edcd35f2e887ea58144b05c64fdffce312e0bc41f4fdf95a63645896",
      "size": 9146
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p6/r17-b1-ioc-p6_golden.xlsx",
      "sha256": "5500c2204ee743fe48f9fe9166c653a6ff6a588f6b2a0e55e41b72802e66d0d5",
      "size": 5938
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p6/r17-b1-ioc-p6_init.xlsx",
      "sha256": "2cb44d1d927ae624cdd1a8aa7188d6337a90244fce7adca184965aea924b3523",
      "size": 5900
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p7/r17-b1-ioc-p7_golden.xlsx",
      "sha256": "807f960477d5a3b441c9052e16617d40e808486a617eb510256a67b009cf6997",
      "size": 7139
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p7/r17-b1-ioc-p7_init.xlsx",
      "sha256": "26af883fc5e2858da3b2b2240de159eb03637b5ebd71c6e8ce55049c1a2eac0e",
      "size": 7101
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p8/r17-b1-ioc-p8_golden.xlsx",
      "sha256": "9a4d960b18f4f405bcb960029225ba4dce3c85c9aa73b113c15ad636b91de960",
      "size": 9294
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ioc-p8/r17-b1-ioc-p8_init.xlsx",
      "sha256": "cf5b527731672ddfd9d6f516e72b4f33938c7ce9b83f222afa49b38a3cb8cefb",
      "size": 9256
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p0/r17-b1-msp-p0_golden.xlsx",
      "sha256": "f658685e8c7937574f995f2afff3dfa908ded7ea4d35f808c7422a29cd8d1b73",
      "size": 7421
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p0/r17-b1-msp-p0_init.xlsx",
      "sha256": "3fb6a8d1996b2f64b3bc11df584498e27a7105c80180f498f38ac38d759a8a5a",
      "size": 7393
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p1/r17-b1-msp-p1_golden.xlsx",
      "sha256": "872dc6fe49a8fd85d0abe8ff79cb5188eacec64dc545fc9e451295dee11f3ab4",
      "size": 8867
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p1/r17-b1-msp-p1_init.xlsx",
      "sha256": "c83636416fa627f8d861b082927dc89915e61a78c340d84c06ca40b3099cac18",
      "size": 8837
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p2/r17-b1-msp-p2_golden.xlsx",
      "sha256": "0bf7f1914d9b807ceb81211707d70643921e1dda452d2b8eba38b5b040220074",
      "size": 10953
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p2/r17-b1-msp-p2_init.xlsx",
      "sha256": "b91aef5cd6dc5b348a5702b621d92ebf3d78dfded4fa76a39fdda79c11174173",
      "size": 10924
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p3/r17-b1-msp-p3_golden.xlsx",
      "sha256": "8090a1e5246247913609dfbd870c59dfee2d37ce3fbcdebbc685788bf86f19c7",
      "size": 7606
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p3/r17-b1-msp-p3_init.xlsx",
      "sha256": "50e8ee302b9754e380f93086d5712d29ea7c03869b4883364cbc20bd2c01d072",
      "size": 7577
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p4/r17-b1-msp-p4_golden.xlsx",
      "sha256": "235fd3efda485bb6158afb73fc1ff8533f3cbb00500bc1617b801f45ffc39bde",
      "size": 9015
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p4/r17-b1-msp-p4_init.xlsx",
      "sha256": "39d01e1f7b0b185f17ae1457b54314fc2cd0c8a3fa72927c5f841707e8749914",
      "size": 8987
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p5/r17-b1-msp-p5_golden.xlsx",
      "sha256": "a07629cc813c660c63293cbf604680bf22e8fc48d078ebd415dad613414b2c3d",
      "size": 11040
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p5/r17-b1-msp-p5_init.xlsx",
      "sha256": "ee4a7557049d7c9dddb57dc292215bc31782e8d655ec197ff38068ac9d9a1b0a",
      "size": 11011
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p6/r17-b1-msp-p6_golden.xlsx",
      "sha256": "3b594a7351b4c4caf54d110ddb595c6f9a3c05e5ad5b445a125a2d5afeaa783c",
      "size": 7743
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p6/r17-b1-msp-p6_init.xlsx",
      "sha256": "43b98be31a380a041251b3ae05bb73a0416ebc10475f408ce344c7cc2ffb966f",
      "size": 7722
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p7/r17-b1-msp-p7_golden.xlsx",
      "sha256": "3c08c57e693fa48d3425b5de92fb8dee2c9b978c4eaa348a354e7968ab5ffba8",
      "size": 9086
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p7/r17-b1-msp-p7_init.xlsx",
      "sha256": "cbb7c15d87710373bcbb4b2752740275d01bacbce70b677f8fe408125b9308da",
      "size": 9065
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p8/r17-b1-msp-p8_golden.xlsx",
      "sha256": "53aa31c26df3eb5e40d8db3395195a61c652c98c4890deceed0757fbf4ad17b1",
      "size": 11208
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-msp-p8/r17-b1-msp-p8_init.xlsx",
      "sha256": "3192d11a3384d59c5524427c2e549757a8ec06558f14bce809c9ef1725353ed0",
      "size": 11187
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p0/r17-b1-ska-p0_golden.xlsx",
      "sha256": "d67eb3abbbf50c73395b7773b33d72838f6afb1dba22e4cefb5cd9559b86b077",
      "size": 6309
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p0/r17-b1-ska-p0_init.xlsx",
      "sha256": "0beb9da72da8af985a049ef03a3e40c77d106ec8342e5fe07cf130aceeea6d18",
      "size": 6293
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p1/r17-b1-ska-p1_golden.xlsx",
      "sha256": "5198274f5c50a7d05216ebc39cc8aac087fa726b864438bc232f12dcc915e308",
      "size": 7785
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p1/r17-b1-ska-p1_init.xlsx",
      "sha256": "ce9386939d1b10402f0a184347719b2ac84e06bd725187f20655eb9b03e43489",
      "size": 7766
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p2/r17-b1-ska-p2_golden.xlsx",
      "sha256": "6de48ef2c7a166ff778a3c20b8feceb5244d485a5ecbf225d269daca439af749",
      "size": 9940
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p2/r17-b1-ska-p2_init.xlsx",
      "sha256": "9b178d68d497361631c6e223482f7a7e1bdd585a0f145b0a67b82b8dce0a46ae",
      "size": 9922
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p3/r17-b1-ska-p3_golden.xlsx",
      "sha256": "32ecba6438f42ed85d8540d99238ae7f181e07e461523203856d0fa27a558679",
      "size": 6477
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p3/r17-b1-ska-p3_init.xlsx",
      "sha256": "aa4d50899749178ed4ec11b9af103f17074ce59aee05b7a40e1299e78eaf5922",
      "size": 6449
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p4/r17-b1-ska-p4_golden.xlsx",
      "sha256": "97fa517a4f29922ebf7a9046072ba2742cffccd848d82fde0b9d62a3447b14a5",
      "size": 7957
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p4/r17-b1-ska-p4_init.xlsx",
      "sha256": "d070d468603e0fb35ca986236b06b467d35d4e7fef7864236d31827e0ede8b45",
      "size": 7926
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p5/r17-b1-ska-p5_golden.xlsx",
      "sha256": "46dbb70e92bb5c42d0c31b4ab4002429db546262e70db042e9dc6b0127ff6076",
      "size": 9853
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p5/r17-b1-ska-p5_init.xlsx",
      "sha256": "292725ae2040d0bfac01b3fd35d1b816a2749280a6d8a95904b4943d4368f283",
      "size": 9825
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p6/r17-b1-ska-p6_golden.xlsx",
      "sha256": "5f7c674f49f634960ffcc33fefb11dfaa68df22a4962b2c85aa774c9dc79b74c",
      "size": 6653
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p6/r17-b1-ska-p6_init.xlsx",
      "sha256": "f3f1ed9b2bbd828225aafcb9470db62a3ad5de370bc29a892007da5275a5d899",
      "size": 6615
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p7/r17-b1-ska-p7_golden.xlsx",
      "sha256": "75389815a92f20d67378d0dcd389b47a5513308b00a60d8a9156b38f8db61da3",
      "size": 7841
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p7/r17-b1-ska-p7_init.xlsx",
      "sha256": "041ec7eb8de21cea5a8fd0394d3ee5676d8f10c32f8ba7e7118b863f95b50e39",
      "size": 7802
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p8/r17-b1-ska-p8_golden.xlsx",
      "sha256": "c61bc532e154f583d009de8f88a6507fadd4e89b9a7f9f1254bef2fc928a2021",
      "size": 10032
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-ska-p8/r17-b1-ska-p8_init.xlsx",
      "sha256": "cffe52c29cfd4a4bbf13be0f88389f1fd9a394545da54c7e1a31b8b2bdf36d2f",
      "size": 9994
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p0/r17-b1-tsr-p0_golden.xlsx",
      "sha256": "94ac72cf0783763e9ad546a422bf594211633f4b851a37daffa57f2c602ed515",
      "size": 5615
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p0/r17-b1-tsr-p0_init.xlsx",
      "sha256": "4ea78b84328b44b4b9e67c3760b7c2cfc5755d0f7ae63674acfd8a429078c5c1",
      "size": 5592
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p1/r17-b1-tsr-p1_golden.xlsx",
      "sha256": "1177fd4523003b2573d875c1cb5719145ee85562f689d95b2cfb294c4405fddf",
      "size": 7634
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p1/r17-b1-tsr-p1_init.xlsx",
      "sha256": "180c63a769932bdb298c5b3e236961ddbc9e827a778932ed64f106404ad00172",
      "size": 7611
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p2/r17-b1-tsr-p2_golden.xlsx",
      "sha256": "8e98c7da2a04bacac9dce97bd717685d61329f0026246ec03ac906f929a8bf7e",
      "size": 10982
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p2/r17-b1-tsr-p2_init.xlsx",
      "sha256": "d570272aad73fa95c341c4492fe39bec0235838a5dc6cec3dc98ff4bef18d30e",
      "size": 10959
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p3/r17-b1-tsr-p3_golden.xlsx",
      "sha256": "568ce26013fb86362e3efdc96e30739d78efb19ac9dd0b91c72b3dcebb31f894",
      "size": 6325
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p3/r17-b1-tsr-p3_init.xlsx",
      "sha256": "dd1459050f4e277df272a8697b31446f924d3becec3ec92f2a82743ced5b1149",
      "size": 6291
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p4/r17-b1-tsr-p4_golden.xlsx",
      "sha256": "b6625fcd0e53e0f7dcde65d422ce1e3347e23a61a605f22023175c83fa8475ea",
      "size": 9061
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p4/r17-b1-tsr-p4_init.xlsx",
      "sha256": "9fdeeddd1078c11cf14d4da77ada21a78fa3711df6800a062bf64d11c255e7a6",
      "size": 9028
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p5/r17-b1-tsr-p5_golden.xlsx",
      "sha256": "5be9e24407e4411acad0ab75e1d70c15f78dca5740645ad7efade52236cd5757",
      "size": 9142
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p5/r17-b1-tsr-p5_init.xlsx",
      "sha256": "5060533438556be85ffcc427ade5801e535e1a30685c0be07ef08cc538439191",
      "size": 9112
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p6/r17-b1-tsr-p6_golden.xlsx",
      "sha256": "71d290f222f71a385ab0895dd1846b428f734f784912550801943450fde717fb",
      "size": 7833
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p6/r17-b1-tsr-p6_init.xlsx",
      "sha256": "ee945945f0065c445c84404eac72406fc86327787ec72333c0a32f8abd783614",
      "size": 7799
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p7/r17-b1-tsr-p7_golden.xlsx",
      "sha256": "57d8e011f417eb88a4d36fdd247ab5185c9704644c41999b146d8ec280e02a2d",
      "size": 7117
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p7/r17-b1-tsr-p7_init.xlsx",
      "sha256": "3b2524e0a7ff69c38537ff1d2bcf2b08ca664955c57ef91c009ce0b9750a1af6",
      "size": 7078
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p8/r17-b1-tsr-p8_golden.xlsx",
      "sha256": "2b5de09338f9bb44aab9bd891d94e4c66dfaa38925f8c56d8c5b90081971c42d",
      "size": 9904
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b1-tsr-p8/r17-b1-tsr-p8_init.xlsx",
      "sha256": "da0582de232703d2111c23e624dd5236b354600b47abf1e408047da69e531630",
      "size": 9867
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p0/r17-b2-agj-p0_golden.xlsx",
      "sha256": "5f7ba1779d6a2c83c1d1e32f9ef680ff9fce7c228abe8ba111b5990b42a4a6fe",
      "size": 7217
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p0/r17-b2-agj-p0_init.xlsx",
      "sha256": "af5bbeeb3dcf4b1761180a5659021760d46071efdfd5c695347b3b1ef6c2cdac",
      "size": 7196
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p1/r17-b2-agj-p1_golden.xlsx",
      "sha256": "8bf8127ba8483a8b4dfc286aab1d4d1b4a92570bc169abb4d481d67f583f8755",
      "size": 8605
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p1/r17-b2-agj-p1_init.xlsx",
      "sha256": "7326f33dd46b1dae4df510e26e8963a4b88e23d5476e6172ed9943152f881cae",
      "size": 8584
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p2/r17-b2-agj-p2_golden.xlsx",
      "sha256": "a95ebbd1d955f904956960b5fe09ab9cb7c9e1698489872b332afc4e942b6bb4",
      "size": 10709
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p2/r17-b2-agj-p2_init.xlsx",
      "sha256": "0624701d80e1b157492b2a8f6b7c7b1e584d265b7e28476095973de87ed30dca",
      "size": 10688
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p3/r17-b2-agj-p3_golden.xlsx",
      "sha256": "d5ff9be2235b797cb2a8818135af448b062db32566958833641589cfd63f6033",
      "size": 7319
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p3/r17-b2-agj-p3_init.xlsx",
      "sha256": "5fe57c10246f8574f7e7a4c87c0b52bab9ccfeaf524975b95266c175a278e27b",
      "size": 7300
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p4/r17-b2-agj-p4_golden.xlsx",
      "sha256": "e75e5e9ce3608db8fac37e0d64d5e1115ff2da58278b39084d50a9faee7288ee",
      "size": 8733
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p4/r17-b2-agj-p4_init.xlsx",
      "sha256": "2c25bfc0f19b72c090cb09864d7a0b29afb113d7043475ea81685952ba064c4b",
      "size": 8712
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p5/r17-b2-agj-p5_golden.xlsx",
      "sha256": "01e8e25070d51b61263622c3a3b59b54913ca304426f562faf23742fb5e4eddd",
      "size": 10810
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p5/r17-b2-agj-p5_init.xlsx",
      "sha256": "55cc1964118ac036ea95fe290fb5657cabb7ecee934d339aaadbcd5d915ac82d",
      "size": 10788
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p6/r17-b2-agj-p6_golden.xlsx",
      "sha256": "20973024c5ca700358d00b0272ec3d306aff8bf0a3c1fcd1c1c4e48b6cd89c82",
      "size": 7465
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p6/r17-b2-agj-p6_init.xlsx",
      "sha256": "fe57a57c55006c73ee533ce0dd8dddbceef1fc8134c7f3b1a5b119b98346fafc",
      "size": 7430
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p7/r17-b2-agj-p7_golden.xlsx",
      "sha256": "5b7d96e2e038fcba03258cee6709323a9f500831835d8e3449fb052534598950",
      "size": 8846
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p7/r17-b2-agj-p7_init.xlsx",
      "sha256": "606d2382e1bc4ef2f79912e7d8dfacd916ac7cd814ea897b00edaf3c02e9b2e4",
      "size": 8814
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p8/r17-b2-agj-p8_golden.xlsx",
      "sha256": "e1055dba4ca63777ad91e1f3178fdf356fcd93d569b888e92b39913bae84f343",
      "size": 10928
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-agj-p8/r17-b2-agj-p8_init.xlsx",
      "sha256": "a4fcc0bc436563120cad9fbef382ffc2345600f70c823b424ac4eb903e305da2",
      "size": 10894
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p0/r17-b2-fmv-p0_golden.xlsx",
      "sha256": "c8e0a18c7ba1b26b476a79b0d0b3f1868f48d14462064a35031d3d483855a3cb",
      "size": 5704
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p0/r17-b2-fmv-p0_init.xlsx",
      "sha256": "7bfa9105bb465595e430843dd256ab71017c648c8ebb9acffa39e54c24c475e5",
      "size": 5658
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p1/r17-b2-fmv-p1_golden.xlsx",
      "sha256": "82ffaa708b51d69cee41c377f492f6d1575c346cf939c8b6d02f7392381217e1",
      "size": 7140
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p1/r17-b2-fmv-p1_init.xlsx",
      "sha256": "920149f26c69e8c89e921af1bc05476b1c44ec45beb0ae8aedf2ce7af13afd76",
      "size": 7092
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p2/r17-b2-fmv-p2_golden.xlsx",
      "sha256": "6b3b978aba3823e5753ebd0dc78db28fd74a0006afc3395d20307dc9bbbc3f0a",
      "size": 9287
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p2/r17-b2-fmv-p2_init.xlsx",
      "sha256": "a64f52684307b160e029183f11f9788a291d9a93e660c04862b372d418be22cf",
      "size": 9239
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p3/r17-b2-fmv-p3_golden.xlsx",
      "sha256": "74aaaa3828a7c9396f9020ac8758b4dbdfeac54139ea0449733836beb1fea8d0",
      "size": 5820
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p3/r17-b2-fmv-p3_init.xlsx",
      "sha256": "be21327cfc0d08c38615daed0eb540092e440149cbefb612f5182f70e83439d8",
      "size": 5756
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p4/r17-b2-fmv-p4_golden.xlsx",
      "sha256": "d9e4bb32ede439f6eb058a185dd5c6687d273abb54a1a4bd87e507e4174b2c9b",
      "size": 7285
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p4/r17-b2-fmv-p4_init.xlsx",
      "sha256": "321acb07debc102a11b0f3b3ce263b80b674fb889e0201375593ca92a19b2b1a",
      "size": 7223
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p5/r17-b2-fmv-p5_golden.xlsx",
      "sha256": "44031a3e32bdbff1ba7798ae44eb3d21cda77c2d50c64f82dfb26ee868d85a35",
      "size": 9257
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p5/r17-b2-fmv-p5_init.xlsx",
      "sha256": "f17ba51c4642a8c0f0c4bb30a6822cdd6d408ff45f489ac1137fbe414be396fc",
      "size": 9196
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p6/r17-b2-fmv-p6_golden.xlsx",
      "sha256": "9554f45d3c590556a838a852a029960da2facf8471c188a870d5129bec02e356",
      "size": 5991
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p6/r17-b2-fmv-p6_init.xlsx",
      "sha256": "2ef72c07e7771f34b8975a3e0f18d55f915f288111f247831c814c17d11e80c6",
      "size": 5904
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p7/r17-b2-fmv-p7_golden.xlsx",
      "sha256": "ccb8b012fec1339580beafffb99a6d1f6652f1b4ef08f07c206d80a5cf2c2e4c",
      "size": 7265
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p7/r17-b2-fmv-p7_init.xlsx",
      "sha256": "ff1b827d2bf5d3d6f86f0818a7be2bb5839b10d65e854bf83e1c60eb7a0b6611",
      "size": 7175
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p8/r17-b2-fmv-p8_golden.xlsx",
      "sha256": "7f008461fdae56716dfeb7975530ea7bafca03c26e2b3f210b712ef91fc67d24",
      "size": 9391
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-fmv-p8/r17-b2-fmv-p8_init.xlsx",
      "sha256": "dce074f0222ba9616a0a471ecbaae0ccc3264557afe58d0cdf0be2d67ecdf8cb",
      "size": 9308
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p0/r17-b2-ioc-p0_golden.xlsx",
      "sha256": "881e584b7025b9c9c85344249ac1050b8c1d28381d1c02130626b370afea1b4d",
      "size": 5647
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p0/r17-b2-ioc-p0_init.xlsx",
      "sha256": "0bd881b09cee1e1c35425a8f65e8f5634112959f804ea940ee69a2a723fcb1bc",
      "size": 5620
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p1/r17-b2-ioc-p1_golden.xlsx",
      "sha256": "c738cea432e683ba582fb1dac4098489c2552e222e2f45ddcb786951402eba5f",
      "size": 7101
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p1/r17-b2-ioc-p1_init.xlsx",
      "sha256": "a3f4031d33cfaa9e737633b3f9544b33b58a3a5278678583ba601fc56beca08e",
      "size": 7073
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p2/r17-b2-ioc-p2_golden.xlsx",
      "sha256": "5885b3460bece252f2a17ff15ca5b7ad4f95fd43a2e172d3c784e533a53ca621",
      "size": 9272
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p2/r17-b2-ioc-p2_init.xlsx",
      "sha256": "da1d13d4004ed4abfde6280a69fb1f8e8e6d31bc257daed37e86807a0e608cff",
      "size": 9246
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p3/r17-b2-ioc-p3_golden.xlsx",
      "sha256": "0e8d3acfe9431882f963d3927b80753c02c0e5cdde35c01412ede58824a162f7",
      "size": 5741
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p3/r17-b2-ioc-p3_init.xlsx",
      "sha256": "3020cc76e47dda16ea270e0f4b0d04e84c7050bcb52db0125b1ad3eb34a6f6c9",
      "size": 5708
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p4/r17-b2-ioc-p4_golden.xlsx",
      "sha256": "248bb65b1c33e3cb6fc8069de595cd27243c06b72df1de362959ae50189410fd",
      "size": 7263
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p4/r17-b2-ioc-p4_init.xlsx",
      "sha256": "39c56c443cb47a9f82d6ebabd244c97a66f377f4fa0f6eeaa9e54ff9e8e3c151",
      "size": 7232
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p5/r17-b2-ioc-p5_golden.xlsx",
      "sha256": "9acdffdfc84b5afca8482825f8b269e5cdeb0cf155f6cb71e90af4f762b7df28",
      "size": 9174
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p5/r17-b2-ioc-p5_init.xlsx",
      "sha256": "af153b27568bfd58b63252e00062ac41bc220cb140d017f569cdc37f9932bb1c",
      "size": 9141
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p6/r17-b2-ioc-p6_golden.xlsx",
      "sha256": "d1d3a753e5351f1a273a1cabfd5be26be8ca8c44e31ea0b5d7d5df10e61fd53e",
      "size": 5923
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p6/r17-b2-ioc-p6_init.xlsx",
      "sha256": "e20754d0c83de51086d45e7d5d0dd052e1e04c2c5ce9ca34ba67fad53809e17e",
      "size": 5887
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p7/r17-b2-ioc-p7_golden.xlsx",
      "sha256": "ee29c12196ddbb416ea08af63855173cce18cb138346309f786186aa0115fbd8",
      "size": 7141
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p7/r17-b2-ioc-p7_init.xlsx",
      "sha256": "37a2400e9cbb9f97d605336d31c29debacc5a83653c43cfa087bddd5227d11c4",
      "size": 7101
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p8/r17-b2-ioc-p8_golden.xlsx",
      "sha256": "457c1ae91b612ec56f5c06c900c75b90f7eb13c6b5d7c78496e73ce3d3ac4896",
      "size": 9288
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ioc-p8/r17-b2-ioc-p8_init.xlsx",
      "sha256": "46308d540d087a43362b0322c186215d8ecdf8c5426a76f02a7f72207a2f976b",
      "size": 9251
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p0/r17-b2-msp-p0_golden.xlsx",
      "sha256": "eff7ac452fa3b2233aa9a6e0a3604fa8dccb6a61f208c5b5c361f32ab9212376",
      "size": 7427
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p0/r17-b2-msp-p0_init.xlsx",
      "sha256": "a1e658435a8c9189ad8550daee1450cbecae83f545317dda75a813a022fbe733",
      "size": 7397
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p1/r17-b2-msp-p1_golden.xlsx",
      "sha256": "a31c354c35a3f798c32362a9ba5f0de2ad37ea6bf62d8917eefb91537c2678d4",
      "size": 8867
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p1/r17-b2-msp-p1_init.xlsx",
      "sha256": "3fbe524b327428c3b22db786f4d4ffa947f36aee7ab4d771c13a02e647eb99c8",
      "size": 8837
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p2/r17-b2-msp-p2_golden.xlsx",
      "sha256": "c0126f56c1afef7917e605256c21d8284b1a550d0c99f8c157f0f6d22aed50ca",
      "size": 10954
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p2/r17-b2-msp-p2_init.xlsx",
      "sha256": "a50bd457e0855e07bec9d6cf1017488c06fc9ba8cccd7d6ad0c179ce13cfa735",
      "size": 10924
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p3/r17-b2-msp-p3_golden.xlsx",
      "sha256": "69b3865aba3e1f5134ad95dd521f967ed3a286143d5cad566a9e194bdc5a9859",
      "size": 7611
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p3/r17-b2-msp-p3_init.xlsx",
      "sha256": "2f67ec3a95ada75d8d5e972dd3d62bcb5f5a0d220c128a624b289579eb02b9f3",
      "size": 7582
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p4/r17-b2-msp-p4_golden.xlsx",
      "sha256": "b27950fe73320541f01c2e51b789db66465df5e13033dfa7f07fafb3ecdd6e40",
      "size": 9005
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p4/r17-b2-msp-p4_init.xlsx",
      "sha256": "c59f24c0a8888571585cc6460e286db7f586ee6ca39f634f08ea6e29411e368f",
      "size": 8976
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p5/r17-b2-msp-p5_golden.xlsx",
      "sha256": "351ad53729576f1cf718419c0516a70e5f7dfa089016f9228975db4f730c3fa0",
      "size": 11040
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p5/r17-b2-msp-p5_init.xlsx",
      "sha256": "b2f9a5e9ff4fcca084891327df928cf624ffed03e8753e901d78e042ab199530",
      "size": 11011
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p6/r17-b2-msp-p6_golden.xlsx",
      "sha256": "1d15efd2b53966763b7d2e0d1b1efa17d6489dc5df5a18894383dd5cae3b606b",
      "size": 7739
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p6/r17-b2-msp-p6_init.xlsx",
      "sha256": "6774916de92944f674eec925c61cb76467eca01eac21a330ba70885cd6ccc24e",
      "size": 7718
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p7/r17-b2-msp-p7_golden.xlsx",
      "sha256": "33ca9fac4a70565baef8f29ad571f56c625fc48a95e855d8d914126f0385d1ad",
      "size": 9089
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p7/r17-b2-msp-p7_init.xlsx",
      "sha256": "d81874b07f79801f96daeeaa516eae036dd28359aabe7367267fb75331f30937",
      "size": 9068
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p8/r17-b2-msp-p8_golden.xlsx",
      "sha256": "2947b727626f1a32063eed5b84650825b3728ca941a238b71d8320fc85cc5bc8",
      "size": 11203
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-msp-p8/r17-b2-msp-p8_init.xlsx",
      "sha256": "b2a81afe5d8d950d91aa1f19c74c840578278525819dee473a26b4e012661509",
      "size": 11182
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p0/r17-b2-ska-p0_golden.xlsx",
      "sha256": "09a6daae2beb0e435699bd397e00dcd441a33fbda53c1d485ea89f0ef36936f6",
      "size": 6311
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p0/r17-b2-ska-p0_init.xlsx",
      "sha256": "b7cd8e97137629e584a8c4ef3920cce037e799cb3cff635e8ea7b0625b83b378",
      "size": 6293
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p1/r17-b2-ska-p1_golden.xlsx",
      "sha256": "a990b1cfa9533f794e12d289edb3a3d45b5cbdf495d3bbf6fa2c1e6de90cafae",
      "size": 7787
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p1/r17-b2-ska-p1_init.xlsx",
      "sha256": "7920c2b48188b2c51db4ee43410ca73005d377d40c96352df78d745b99c74d9a",
      "size": 7768
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p2/r17-b2-ska-p2_golden.xlsx",
      "sha256": "99624d2bca4daa75abcae7a37b9298264e58e458fa5c4207c1b57da037b545ef",
      "size": 9947
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p2/r17-b2-ska-p2_init.xlsx",
      "sha256": "dd81bdb0b7c9a35dedf79a4d49190f357bb4212202e7462d595726f8e3edf226",
      "size": 9929
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p3/r17-b2-ska-p3_golden.xlsx",
      "sha256": "2f1b437b2e0752cefada4568eb99da6deddd817bb8823d0eb59d00a6dd6916ec",
      "size": 6474
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p3/r17-b2-ska-p3_init.xlsx",
      "sha256": "555a05178ec59d356b477d6b870977cffd3faa241050b67491e43c4d0d7e2b19",
      "size": 6446
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p4/r17-b2-ska-p4_golden.xlsx",
      "sha256": "9156e782b4dbc2889dca0412c3ae19ce08a2fdedec63f7c446ea5c074fbd3170",
      "size": 7953
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p4/r17-b2-ska-p4_init.xlsx",
      "sha256": "707ef06d4be5f2c3751398327c2b44dd525606b58785c8dee0fca2d3c5157e09",
      "size": 7925
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p5/r17-b2-ska-p5_golden.xlsx",
      "sha256": "19e21f64137034fcc168360b31a600decb910ca86227b8dca131af7bf971690e",
      "size": 9858
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p5/r17-b2-ska-p5_init.xlsx",
      "sha256": "292b2e3e4c8a1cb59195466c25288e974de56971b16b2f828f91affdbf449c00",
      "size": 9828
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p6/r17-b2-ska-p6_golden.xlsx",
      "sha256": "20a1fb5bf78f282b92688d655411cc48385105a024a005f00cd822315958d559",
      "size": 6646
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p6/r17-b2-ska-p6_init.xlsx",
      "sha256": "a66c4dba631a1cc552168e69b58506747d7c32e8981774cc140a8c342246cfa3",
      "size": 6608
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p7/r17-b2-ska-p7_golden.xlsx",
      "sha256": "2562f10f483b9e4889fd78839501345368b9b141a2eb8f155016fa7699c6b0e6",
      "size": 7830
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p7/r17-b2-ska-p7_init.xlsx",
      "sha256": "ffc0a9d02f0ffbc80ea575e0d2cdc29daf24f1c9975b5ba0f6f70fddb9425008",
      "size": 7791
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p8/r17-b2-ska-p8_golden.xlsx",
      "sha256": "e26f6fc2d9b8ac0b9dec32da882cd6502b1acf1b7ec227ed9c38f03e98c870ab",
      "size": 10025
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-ska-p8/r17-b2-ska-p8_init.xlsx",
      "sha256": "ccf63ad3dfb312d26680b78281882274d15bd173bd9b1682064ec2c8ad4f936f",
      "size": 9986
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p0/r17-b2-tsr-p0_golden.xlsx",
      "sha256": "af28a557031adffdecdac95196a5ca915ace7dfb8efcf02e3ed1add4c7226352",
      "size": 5614
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p0/r17-b2-tsr-p0_init.xlsx",
      "sha256": "2b28a611b303338fbfde0af0a8d76438a7f448effeaacc9ce0ebe604d8e329eb",
      "size": 5591
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p1/r17-b2-tsr-p1_golden.xlsx",
      "sha256": "8f61342884bde580f6ff1be2b711c707b87e3fa41aa9f56fa38d8fe65b341562",
      "size": 7637
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p1/r17-b2-tsr-p1_init.xlsx",
      "sha256": "54ff5914155e574dda499ff40304b5c56dc92f709ccb7340831710f9b1c3e748",
      "size": 7615
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p2/r17-b2-tsr-p2_golden.xlsx",
      "sha256": "902e9e1dbd9b04ee6906f673278643e9ff6fd9f8b4b3703976e1d2bc95d8cceb",
      "size": 10993
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p2/r17-b2-tsr-p2_init.xlsx",
      "sha256": "a42e999db7f219563f84478eff194f91a62c6fa811b11426e7e91d66e56f3be1",
      "size": 10970
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p3/r17-b2-tsr-p3_golden.xlsx",
      "sha256": "13cdc76ee47bd1182e4fdeb404484fb387a0b3fe7af599f9119381e5625c1850",
      "size": 6330
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p3/r17-b2-tsr-p3_init.xlsx",
      "sha256": "e7f39eae38117940a7138d5b1ce8494b83bc5308145dfe4e0d312d23f4ec04ba",
      "size": 6297
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p4/r17-b2-tsr-p4_golden.xlsx",
      "sha256": "c3545649495ee88df1d202bf956ae7fcbeb2a61446663ada8b9a4b5491245fba",
      "size": 9066
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p4/r17-b2-tsr-p4_init.xlsx",
      "sha256": "9b43a5b766640f0454036ae812d1ac9e37c4204d4ee6b1e3f44322861d40ed7c",
      "size": 9034
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p5/r17-b2-tsr-p5_golden.xlsx",
      "sha256": "1c635c869935d53fbd33e152f8f9d510676b228fe4904d0f480d3bcaa0fc17a1",
      "size": 9140
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p5/r17-b2-tsr-p5_init.xlsx",
      "sha256": "345101d7721b418b79b2aa78c01c80f77313252fea9e356d0b6fa8bbccd4435b",
      "size": 9109
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p6/r17-b2-tsr-p6_golden.xlsx",
      "sha256": "a22a19b6542d8f8975a639af5cd6037f75a2c08609dd02cd4d5d5a55fd9986e3",
      "size": 7837
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p6/r17-b2-tsr-p6_init.xlsx",
      "sha256": "dae6ce19ae87523cdc5dcc1b6e4d8c14a6cf3968066760cca715dada9c3a29c5",
      "size": 7798
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p7/r17-b2-tsr-p7_golden.xlsx",
      "sha256": "641c20d7cdba7c3443ec751da5abd7326bcb929301105fbd3605a13772ca8933",
      "size": 7107
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p7/r17-b2-tsr-p7_init.xlsx",
      "sha256": "3b0277ef30159c510f400a36996465a0561bf79b148f55c67da7a206bc3bc945",
      "size": 7073
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p8/r17-b2-tsr-p8_golden.xlsx",
      "sha256": "00f67313dad23e24dc2fe154f868d62eae20329d1c6ce6f561af3be84bf13aa4",
      "size": 9901
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b2-tsr-p8/r17-b2-tsr-p8_init.xlsx",
      "sha256": "c76a1f9e78df735faa8472bfead4b4d55d6ea161990abc034e8ae578a602c41b",
      "size": 9868
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p0/r17-b3-agj-p0_golden.xlsx",
      "sha256": "2a8b7b91b60cca068de9cfb4eefd5bf9719a9b134a1fd62f55830b00b13e0d4e",
      "size": 7218
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p0/r17-b3-agj-p0_init.xlsx",
      "sha256": "6ea1dc6037d6f932d967d07a98b72dbfb1408bc0e0169fc06bae8e2e91f40a71",
      "size": 7197
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p1/r17-b3-agj-p1_golden.xlsx",
      "sha256": "8da3c60ec5276071ac2c70fccdcaa4ff15d774f9e44847556189c4b0c51da184",
      "size": 8606
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p1/r17-b3-agj-p1_init.xlsx",
      "sha256": "cdd0e2720e53cf6715db92e92ce2f424370b255a1df8f650e2c7da724831ced3",
      "size": 8586
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p2/r17-b3-agj-p2_golden.xlsx",
      "sha256": "9dede2f764c40e62dc97b999d1d7405965cffcbb8109a8f94b8a3c92364b89fe",
      "size": 10710
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p2/r17-b3-agj-p2_init.xlsx",
      "sha256": "f8fb5c488f58fbabe84615631546b2c0ac35f436ca6c2715dfe48df393c7b066",
      "size": 10690
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p3/r17-b3-agj-p3_golden.xlsx",
      "sha256": "a48f97b33db8e28c7805122f4cb1935105a56bdb9252bca1506337adf1d2065b",
      "size": 7320
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p3/r17-b3-agj-p3_init.xlsx",
      "sha256": "6a6958042b901b3f044916ea9f18f892994f7aa6452f756a887fd44aba864439",
      "size": 7299
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p4/r17-b3-agj-p4_golden.xlsx",
      "sha256": "fab37cae11877aa2209fc10ecfbc5941a3772ace1096dd9c03bb8abb81b7d760",
      "size": 8732
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p4/r17-b3-agj-p4_init.xlsx",
      "sha256": "3d4052286fb3b2fe6f6ea6bfe40d29f54445b63ef93c5800d079b2ceab36b1c7",
      "size": 8712
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p5/r17-b3-agj-p5_golden.xlsx",
      "sha256": "855b9128760792a4f40f5cb3cf878f80ded57f5c7dd99db3db56f8265b48d62e",
      "size": 10803
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p5/r17-b3-agj-p5_init.xlsx",
      "sha256": "e4d989b245e50806f7d7eb6b4790ac4560778c52ce40838ed560d9a7d509d6b1",
      "size": 10781
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p6/r17-b3-agj-p6_golden.xlsx",
      "sha256": "4c71db797ff9b8939cd31f94734c89469ff4b929f464e94f6a3af0580c7b49d0",
      "size": 7453
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p6/r17-b3-agj-p6_init.xlsx",
      "sha256": "7cccc51dc73a30c2dde144b570abdcec9bf6b38704470e033b800cd888021c22",
      "size": 7422
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p7/r17-b3-agj-p7_golden.xlsx",
      "sha256": "ee1b907d831446a5a0c57941d3ba4c743cc8de3dd929e20cc745724983d05523",
      "size": 8839
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p7/r17-b3-agj-p7_init.xlsx",
      "sha256": "145e65eb28a1d26591aabadec9a511f468812194991f0a87f9f5cf6c2fcae7b7",
      "size": 8809
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p8/r17-b3-agj-p8_golden.xlsx",
      "sha256": "29ac036d033e1b06f90ba909249f2b8858935a6c82d80cb6943e6e994fd09479",
      "size": 10918
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-agj-p8/r17-b3-agj-p8_init.xlsx",
      "sha256": "8d26bd561266e7a5f483692bd901fb19f1f139eef8002e6c036b623241fd4171",
      "size": 10888
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p0/r17-b3-fmv-p0_golden.xlsx",
      "sha256": "7fd96a20d6fac4f944193328a7aac74b577c16ca5af455dfbc05b523aae7fee7",
      "size": 5706
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p0/r17-b3-fmv-p0_init.xlsx",
      "sha256": "9a791914f0f9aa1c634672ab28841f17a77dbc4192bfe900a617fb2c6171a18e",
      "size": 5658
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p1/r17-b3-fmv-p1_golden.xlsx",
      "sha256": "803421ec08282f85a480e187bd2898128cb29e465e50f60192c2c0f07be42896",
      "size": 7146
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p1/r17-b3-fmv-p1_init.xlsx",
      "sha256": "56a95e5e483f70fffee937fe813c19809835915b73662741603afb43f6335087",
      "size": 7096
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p2/r17-b3-fmv-p2_golden.xlsx",
      "sha256": "a0ea2a4103a70d38433b36da74826b680ad7e17610b0638c1a00f3987158e551",
      "size": 9284
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p2/r17-b3-fmv-p2_init.xlsx",
      "sha256": "2ab29e7e6d358b9f38e579ef655b4325aa07671ffd7a1fdc27a4d042c9da5726",
      "size": 9237
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p3/r17-b3-fmv-p3_golden.xlsx",
      "sha256": "8632838db221a741556c4555955b2f4468df40ef0df2eeacbcf6d397d415965f",
      "size": 5822
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p3/r17-b3-fmv-p3_init.xlsx",
      "sha256": "49e97ef4fd19fb1f773b0bf801ac704fdf74fba955a9fba24c97026ae3d71439",
      "size": 5755
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p4/r17-b3-fmv-p4_golden.xlsx",
      "sha256": "7273f1ebf574f20b57a275142cdc721aab9c629171a6ac7520d79fbaed9f6314",
      "size": 7293
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p4/r17-b3-fmv-p4_init.xlsx",
      "sha256": "1ecb86517be06683ceec4a25c803ad17bf3051752fb02b4efe288f46d9239348",
      "size": 7228
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p5/r17-b3-fmv-p5_golden.xlsx",
      "sha256": "5c80e7696acbbb96aa1a092d053d2042bbcd2d5b46352e5c3594f144755b9d8e",
      "size": 9261
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p5/r17-b3-fmv-p5_init.xlsx",
      "sha256": "97630699b4543983cd3af8be621d5e13f511fe22a65b0e212aaf3e2057d4ff85",
      "size": 9192
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p6/r17-b3-fmv-p6_golden.xlsx",
      "sha256": "9189fa85ef718bb48eb847aa115c4eba38837a5a54fb6a8ecdc66e10443d1dbd",
      "size": 5989
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p6/r17-b3-fmv-p6_init.xlsx",
      "sha256": "76aca91c5079f59fd59972ee1e4ae9c058423f65c37e6f0fd57b4233b114b4b8",
      "size": 5898
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p7/r17-b3-fmv-p7_golden.xlsx",
      "sha256": "fa279a793044885f542a9879bcc8687fa619c5f68d4cd15a3bb02648a536d84f",
      "size": 7258
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p7/r17-b3-fmv-p7_init.xlsx",
      "sha256": "68aac738961f5acbb4377a89043dabde0946bec52a63f4cd3494f2b8c65981a7",
      "size": 7170
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p8/r17-b3-fmv-p8_golden.xlsx",
      "sha256": "f473c0f4f7111490d01c8b2f91dc9873ca7bd05d554db68abd8cf744820f6a45",
      "size": 9413
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-fmv-p8/r17-b3-fmv-p8_init.xlsx",
      "sha256": "c54213c2f0b466590c10ce44fcd4e01002e09d8d1f65784e79f55a62f3ce0f5f",
      "size": 9321
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p0/r17-b3-ioc-p0_golden.xlsx",
      "sha256": "d231683abd2eec6402e863f673e0bcaa34181c84f9e7755065f4eb2c924d6bff",
      "size": 5649
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p0/r17-b3-ioc-p0_init.xlsx",
      "sha256": "b811169f16ebe9ef029c405e76fff9f55eb25cd006a0e8401294e888dbc22bf5",
      "size": 5623
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p1/r17-b3-ioc-p1_golden.xlsx",
      "sha256": "9e352a30c9148a4985c621519bafe7c6bb6390f364db1cdcd10b2d2d4abc2bb4",
      "size": 7101
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p1/r17-b3-ioc-p1_init.xlsx",
      "sha256": "f537134973924ae680415612588c96d9b29cca73e4d0bc8eb81e468689796453",
      "size": 7074
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p2/r17-b3-ioc-p2_golden.xlsx",
      "sha256": "15f6362df55d55d9a6497ba9c454d60d4d50af2f6326af5db3251448f6e0f375",
      "size": 9275
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p2/r17-b3-ioc-p2_init.xlsx",
      "sha256": "492d32fe54c898f86513326e71d68ce4812a06b40ef7a9b9e58cdbd1b5e6c71d",
      "size": 9247
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p3/r17-b3-ioc-p3_golden.xlsx",
      "sha256": "125a266b1c395c1664c1480d033bb2cc49fc4a0928103c7d3744cdd79abed2c0",
      "size": 5757
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p3/r17-b3-ioc-p3_init.xlsx",
      "sha256": "0b5d78de4d3af063c90fd78dae703c6e28d78473deb90d1be2981447406a4c91",
      "size": 5723
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p4/r17-b3-ioc-p4_golden.xlsx",
      "sha256": "2b65293f96dd9ebede175cf88794dd64c4fbf276a410f447edf3097c3c0ebbf0",
      "size": 7265
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p4/r17-b3-ioc-p4_init.xlsx",
      "sha256": "989294fce23fd971dd89b64bc723b64c7cb5ef180c0a130965c645c4d3f8c17b",
      "size": 7232
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p5/r17-b3-ioc-p5_golden.xlsx",
      "sha256": "5bb4c46412ddb0bf8b3920e455a7e9235010be0f59104863a3dc2fb162aa2083",
      "size": 9179
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p5/r17-b3-ioc-p5_init.xlsx",
      "sha256": "70757c809bf789b9d34f6d2b3533024667130ac55a19dac8b2029205a5f26f55",
      "size": 9146
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p6/r17-b3-ioc-p6_golden.xlsx",
      "sha256": "6c63f6e58d287044dd6b58092f14616933a2112a46d1f43876c47e5c6f7ac24f",
      "size": 5928
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p6/r17-b3-ioc-p6_init.xlsx",
      "sha256": "722446eca7cf683d3b0a8504fdadad01f5d4afa6a5bc7e2556966f79abaf24d6",
      "size": 5891
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p7/r17-b3-ioc-p7_golden.xlsx",
      "sha256": "fe0500442e107cd841854122d63b0a7e36c62f5b4736e1b4cc65b2999aab0983",
      "size": 7143
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p7/r17-b3-ioc-p7_init.xlsx",
      "sha256": "f05ffc6644f1250c74ff6e22fedb67aa7f2321f99af6673bd96dc98d9b7485c9",
      "size": 7104
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p8/r17-b3-ioc-p8_golden.xlsx",
      "sha256": "e9a7f5abe762591f53c406dd9346378c619b802875243393e7b567bc8a822029",
      "size": 9294
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ioc-p8/r17-b3-ioc-p8_init.xlsx",
      "sha256": "970a38f320ec25f5473e59e919b68c32700ecf07f7754930c7876fec40ae1e1f",
      "size": 9258
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p0/r17-b3-msp-p0_golden.xlsx",
      "sha256": "9da2ad35c277459ce092620275bd94d8824913c29dd2de3d575eed8ca72686d5",
      "size": 7419
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p0/r17-b3-msp-p0_init.xlsx",
      "sha256": "9a634e222542eb54f79dca5c9d9624adb6c01e7c13fa653072e4195cbd0f0d47",
      "size": 7390
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p1/r17-b3-msp-p1_golden.xlsx",
      "sha256": "96a63089e7942eafb37a41b379441f205e03d454b9c1e40f5e219927aa103d33",
      "size": 8860
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p1/r17-b3-msp-p1_init.xlsx",
      "sha256": "5bb0159d61dac1fb826165803010c990dc75dc9b244e993597994352576af271",
      "size": 8830
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p2/r17-b3-msp-p2_golden.xlsx",
      "sha256": "013bc4fdb932955562a3c4ea2ae9d20a98382130b52788c45606a8a8487bcae7",
      "size": 10963
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p2/r17-b3-msp-p2_init.xlsx",
      "sha256": "ffd72b2b1a78a5db59881fcb167895bc5ab4abbd83e3b062e60c5e1477bfa674",
      "size": 10932
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p3/r17-b3-msp-p3_golden.xlsx",
      "sha256": "0fa6f929f58cbb2b08279fdcec9230a1ba46cb6f1ddf2fdaa9aa144eb9409ca2",
      "size": 7603
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p3/r17-b3-msp-p3_init.xlsx",
      "sha256": "384fca4f60ae6ddc6a04ee57864d20fa0e0a8d36de7adc6d5e4e4ae5c3a322e6",
      "size": 7574
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p4/r17-b3-msp-p4_golden.xlsx",
      "sha256": "01ba52d0bdf510cc86da47727ba1f0acc474c4bdc06288dadbd4d65d0902d144",
      "size": 9013
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p4/r17-b3-msp-p4_init.xlsx",
      "sha256": "8b72eb52ac096f28df8258e54b5e484c5782b92aba81d3eb7f73186478088e84",
      "size": 8986
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p5/r17-b3-msp-p5_golden.xlsx",
      "sha256": "fcd907e497a8957d46ce469d1be1b00e0dfa76810657f55de51aa8ddd5d1ca65",
      "size": 11029
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p5/r17-b3-msp-p5_init.xlsx",
      "sha256": "c4d4565015919611854e6032bfd49f8da6493b2baac7c03be988e7a1c614e820",
      "size": 11001
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p6/r17-b3-msp-p6_golden.xlsx",
      "sha256": "b533cec05241938021f56e49fa343c07c2776cfc6bd0b099bb5a1e4ead2ab455",
      "size": 7746
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p6/r17-b3-msp-p6_init.xlsx",
      "sha256": "2a659727b9b0caaefa560ae5b20be48bb6872fd8ffa6fd11bf8ffd5f70d9d919",
      "size": 7725
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p7/r17-b3-msp-p7_golden.xlsx",
      "sha256": "3ba443fd13838d7967553b99cb27fa18ce663501ef2d079eceee578e9a03793f",
      "size": 9088
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p7/r17-b3-msp-p7_init.xlsx",
      "sha256": "ea6a3b22ce209c60840a84bcaac1c28f176d0db94985c3761e818f74b24b16d9",
      "size": 9068
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p8/r17-b3-msp-p8_golden.xlsx",
      "sha256": "c81cc4fbfe71472cfed7323a0b992ff7a5362c8b498021d335621870797589c8",
      "size": 11216
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-msp-p8/r17-b3-msp-p8_init.xlsx",
      "sha256": "f3e7ba38805721f1aabbeb32d6300fbb29e76de47ee950eb6033eb7a63acac13",
      "size": 11195
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p0/r17-b3-ska-p0_golden.xlsx",
      "sha256": "536a15124a35ccf22699c85ee25aa1df9256018de28d68a7d0fd74976b213de9",
      "size": 6312
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p0/r17-b3-ska-p0_init.xlsx",
      "sha256": "ee2a097384c0e1631a0325adca66a7f8dce22868b82af0b8de1da7cc4d2a661f",
      "size": 6294
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p1/r17-b3-ska-p1_golden.xlsx",
      "sha256": "538a0c909cc1a7c009be36465b87e80df3fdced6df7a59db46f2237549201af3",
      "size": 7778
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p1/r17-b3-ska-p1_init.xlsx",
      "sha256": "2257fc8c2cf1d336a555f1df9ec83b9b4429fe3bdac4970f8857a821bb106031",
      "size": 7760
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p2/r17-b3-ska-p2_golden.xlsx",
      "sha256": "128f7c5a4c4d16f974acca4622134357ec319100942fb779dbc220613561dee0",
      "size": 9933
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p2/r17-b3-ska-p2_init.xlsx",
      "sha256": "9bdd2470bf6325e7a1fed1b18ee9aeac5756d77e13629518a521e92f8b77e9e3",
      "size": 9917
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p3/r17-b3-ska-p3_golden.xlsx",
      "sha256": "9173567a9dd1a9c6f295b151795b0312529e890a05e4cdb102d717fc38ff9dc9",
      "size": 6472
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p3/r17-b3-ska-p3_init.xlsx",
      "sha256": "ef713df8ca0b7a02a5249806abc1c21251c089c1cefc8a3e5afe2e125c1b93cb",
      "size": 6443
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p4/r17-b3-ska-p4_golden.xlsx",
      "sha256": "490ec84b267c542ab53a9685d3f2916639f2e21582910707140f96f6cca79d09",
      "size": 7959
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p4/r17-b3-ska-p4_init.xlsx",
      "sha256": "0b56cbe8ced8d5cf5b8270548d7a75cff0456eef1d26ca7fc17684bb6af76a97",
      "size": 7929
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p5/r17-b3-ska-p5_golden.xlsx",
      "sha256": "51fe8a7d2f2528922a4bdf75ebb22607f70fadf93c34fc3017bfd73e9fb70168",
      "size": 9858
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p5/r17-b3-ska-p5_init.xlsx",
      "sha256": "ee555893d58db088332e481c76135a429968fd9f909fdf4407e2e5e84ad15d9a",
      "size": 9830
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p6/r17-b3-ska-p6_golden.xlsx",
      "sha256": "fca130d15fd31370e444670c07f46fd81c4d52d223b52ed212d863350f6b838f",
      "size": 6658
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p6/r17-b3-ska-p6_init.xlsx",
      "sha256": "0a848ebc4ea2a9b8efc6af929c82aad52da368e2edfe8a125dd788bee2e45c89",
      "size": 6619
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p7/r17-b3-ska-p7_golden.xlsx",
      "sha256": "738dcfdd2addc0de0da71cad124e47657762b9674d5e9f78830ac96e586fcf3a",
      "size": 7833
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p7/r17-b3-ska-p7_init.xlsx",
      "sha256": "641c75de9f36b7bea610ed9809200a28e42abf288611fc1b1986f16a1b7ede03",
      "size": 7796
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p8/r17-b3-ska-p8_golden.xlsx",
      "sha256": "1efa37b368a25b0abebfbc2aeaaa71bd13feb0e55007262ce0e0dd43dca224d7",
      "size": 10026
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-ska-p8/r17-b3-ska-p8_init.xlsx",
      "sha256": "a927c5454629b99b7d183694b70e0ed36b8e626ef3ec3321dff3c9e662197c56",
      "size": 9987
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p0/r17-b3-tsr-p0_golden.xlsx",
      "sha256": "53c534d140dc20cde94cecd01a7e0432d749636c4f37d9849f49d89161f33b75",
      "size": 5613
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p0/r17-b3-tsr-p0_init.xlsx",
      "sha256": "033e5a4321bc40dfec411677537f7d4aac25e03cd9bda1e474d1b1df4ebfd7dc",
      "size": 5591
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p1/r17-b3-tsr-p1_golden.xlsx",
      "sha256": "4ac4629e31075b4c62f08a9f7af31f61e05f49bd6363668ebed3814faa1c9dab",
      "size": 7636
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p1/r17-b3-tsr-p1_init.xlsx",
      "sha256": "e0b111a9e99a712db1c99908b2fa4e3c319df5714153715b5ac591a4d8a37e4a",
      "size": 7612
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p2/r17-b3-tsr-p2_golden.xlsx",
      "sha256": "7064ba2dd65d2b963a40d478c71a690dd197377e221628cc11ace462abfccccf",
      "size": 10985
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p2/r17-b3-tsr-p2_init.xlsx",
      "sha256": "3db19fc9f830913f1192000a2b25b3a2dd1596563b5d37e2db42133eb57b1d9c",
      "size": 10962
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p3/r17-b3-tsr-p3_golden.xlsx",
      "sha256": "4f294c7803c24a9ceafb1be6c61802b80e21dfec99e860ddf37757e3d7ab8077",
      "size": 6327
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p3/r17-b3-tsr-p3_init.xlsx",
      "sha256": "93cca590e1dd53e3b68839b5602702ba420516eed16f2f0d77893b300ff00c37",
      "size": 6295
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p4/r17-b3-tsr-p4_golden.xlsx",
      "sha256": "0b706dbf315ba491829682feb90e502982c0a786ae863de51142cf68b158c8d8",
      "size": 9063
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p4/r17-b3-tsr-p4_init.xlsx",
      "sha256": "09daee6f913cec6cedd0302c4a59c3e16a7cda3ad766d8221752d63e25dfe259",
      "size": 9031
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p5/r17-b3-tsr-p5_golden.xlsx",
      "sha256": "c8cbcabc60bdecbccf80007753797f30a5ff97ebb517429b83f0e19710ec3775",
      "size": 9144
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p5/r17-b3-tsr-p5_init.xlsx",
      "sha256": "2b3d6fe168f97cfb0a97deaf9c74fc64d855bec9b2cf3e0f256e2278d79a8bc7",
      "size": 9113
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p6/r17-b3-tsr-p6_golden.xlsx",
      "sha256": "838ad2c3ee94d011a4fb2cbc7bbcc0c51266dec73dff26ff2be9d171f9fdf303",
      "size": 7827
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p6/r17-b3-tsr-p6_init.xlsx",
      "sha256": "9e9270970a0bc49e9035cd318010caa4b0013eb89ba24f0894bd97887e6c8d24",
      "size": 7793
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p7/r17-b3-tsr-p7_golden.xlsx",
      "sha256": "e50d013e09870e1696fb5b42fa8c418411ba91664bab66df61c6b8a6f88e03c0",
      "size": 7119
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p7/r17-b3-tsr-p7_init.xlsx",
      "sha256": "10c438eedfb7dc8c27e2326f9a4cfa284b4c9816a3cce8eb209643ba6c81066d",
      "size": 7083
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p8/r17-b3-tsr-p8_golden.xlsx",
      "sha256": "998e94b9db73d55e0e6f1e44cd2fb75a59ae0d2dcdcef3ef57d72fdc3d82ab20",
      "size": 9904
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b3-tsr-p8/r17-b3-tsr-p8_init.xlsx",
      "sha256": "b5265c10802123dee7a5155e3d27f9cf9f0c9b3ad0c07900633e02cf20c2fc75",
      "size": 9866
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p0/r17-b4-agj-p0_golden.xlsx",
      "sha256": "a2099a9c99e662c286fae5b183f39189c3c3d131f4ce28b618bb4c7bf9af3945",
      "size": 7217
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p0/r17-b4-agj-p0_init.xlsx",
      "sha256": "711b9e8c9746feafd9abbab9fa4fe7b23f9dc9695c30c891ea8a453ed1b6a564",
      "size": 7197
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p1/r17-b4-agj-p1_golden.xlsx",
      "sha256": "bd94e30c1f49a668285a024fb404a3368ebff93cea18a69ee84305095ac7f885",
      "size": 8611
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p1/r17-b4-agj-p1_init.xlsx",
      "sha256": "df7897704f0a016160f6f90379f976fb32c09dff5a35d468e1bc89fb89144efe",
      "size": 8589
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p2/r17-b4-agj-p2_golden.xlsx",
      "sha256": "c4f49fa8ec67261783e30c249ef3c49f30c9abf131fa0e211250720096a929f7",
      "size": 10708
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p2/r17-b4-agj-p2_init.xlsx",
      "sha256": "705b2ddadd701b50c61af5bcc2f92f7cba4e0a933eaec1bd80d6097dfc7d50b3",
      "size": 10687
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p3/r17-b4-agj-p3_golden.xlsx",
      "sha256": "66d90cc7fa81627ac274b6d68bb720119d5cd556c8bbfd2cb9a9850e6c316e08",
      "size": 7318
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p3/r17-b4-agj-p3_init.xlsx",
      "sha256": "00393a8a963cca0a9f900f5a103a6d42b486dae1f6b22976877f590712b05a1c",
      "size": 7298
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p4/r17-b4-agj-p4_golden.xlsx",
      "sha256": "998b6f0f3a1bf0394d06f33ab90cb11fc2668e16cbe3416b06833bea23faf67d",
      "size": 8737
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p4/r17-b4-agj-p4_init.xlsx",
      "sha256": "dc809368651cee95c6b2da19b491676936834c072834ebacac4f8a7807bf69ae",
      "size": 8717
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p5/r17-b4-agj-p5_golden.xlsx",
      "sha256": "0dfcc78862a761ed1346b49a7ba104cd0751dd409e7db8b2e6f5b91125742907",
      "size": 10802
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p5/r17-b4-agj-p5_init.xlsx",
      "sha256": "2ff8ac1113da203a4631f4d85285a2a30ccafa3ec583a340722005517efd8628",
      "size": 10780
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p6/r17-b4-agj-p6_golden.xlsx",
      "sha256": "e6aca97c27153efd6249407de54c65bf34fb1f8b67c9bd2e65a22dcb4d51e0a9",
      "size": 7460
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p6/r17-b4-agj-p6_init.xlsx",
      "sha256": "0514141c911379db1a7513efd05c9e41fe49e4a0c6daede793183584bc751115",
      "size": 7430
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p7/r17-b4-agj-p7_golden.xlsx",
      "sha256": "812dda4d546de097416a1f98673a7c46979afdef20c5c0252cb5a7c8af8eb58e",
      "size": 8844
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p7/r17-b4-agj-p7_init.xlsx",
      "sha256": "7949462fe3a785bb34bbd2686decd73c4aacc9114a3e55ae5efeb31300114295",
      "size": 8812
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p8/r17-b4-agj-p8_golden.xlsx",
      "sha256": "3d4d86d709a5b555b270a3b7cd119b2ea697c00952d8c534d73143fd718b8d11",
      "size": 10919
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-agj-p8/r17-b4-agj-p8_init.xlsx",
      "sha256": "b8d08f38bda9c659575af2e472d7c51f130c954fcbeab1955775c52e2ec72cde",
      "size": 10888
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p0/r17-b4-fmv-p0_golden.xlsx",
      "sha256": "7b53fd72d9d7a763560aaa8918520535b77d34e2f4ab070446ed380343947cab",
      "size": 5707
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p0/r17-b4-fmv-p0_init.xlsx",
      "sha256": "d0116b24144808538f282fd06b4152dc2578a0398c9dd96192deb72ddcf1bc10",
      "size": 5661
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p1/r17-b4-fmv-p1_golden.xlsx",
      "sha256": "644100bdea59682a6657186d24798f29658bf229b1aa9c93658ef7514c257b74",
      "size": 7145
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p1/r17-b4-fmv-p1_init.xlsx",
      "sha256": "e316d64e0c4dbb48f10baf0f0b8093b41c3b8282c116487d2f10c4e56bbe375e",
      "size": 7098
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p2/r17-b4-fmv-p2_golden.xlsx",
      "sha256": "7b24a079f85b1dd87f7b0c3f6a5a9132d3b6ec5efa758b4f2c30c5be12497af9",
      "size": 9285
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p2/r17-b4-fmv-p2_init.xlsx",
      "sha256": "c2d4e4602621e3f4ffc1cd2cc1dee39823b9322c0aa885b889d7c3d25248565c",
      "size": 9239
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p3/r17-b4-fmv-p3_golden.xlsx",
      "sha256": "008ab93f03b2df0560a0e75d8d9a34cfbd1920366afd99589889634d39ecbe3b",
      "size": 5825
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p3/r17-b4-fmv-p3_init.xlsx",
      "sha256": "4ab0538941738d9ec7172d526f40e3b5d32391235b768820f23c0a029f8b074b",
      "size": 5761
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p4/r17-b4-fmv-p4_golden.xlsx",
      "sha256": "71e1eb386da2ad6c77301d9e6781e347d693ae7fba37406097f052cf3d607441",
      "size": 7291
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p4/r17-b4-fmv-p4_init.xlsx",
      "sha256": "a33de390589f7a153c33066318badef7dbf4b177e2106371b8f13ea47a5fc0bb",
      "size": 7226
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p5/r17-b4-fmv-p5_golden.xlsx",
      "sha256": "60c54a91df7d75cfe07a5ad2062baba65e7331cb51629296f82ffbd32bd376af",
      "size": 9260
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p5/r17-b4-fmv-p5_init.xlsx",
      "sha256": "f5f38f61573bc512d74452c0ba0513495368c83940dd0168239201c8fd5dad03",
      "size": 9198
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p6/r17-b4-fmv-p6_golden.xlsx",
      "sha256": "81efbf2996ce3c175c0c8116f1580aa5bb56fb13b6c414ddc494b1c7c5244391",
      "size": 5979
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p6/r17-b4-fmv-p6_init.xlsx",
      "sha256": "ee141b656791b0807d31937ef93f87059058a5af0564f1c8192ba7952a9a96cd",
      "size": 5893
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p7/r17-b4-fmv-p7_golden.xlsx",
      "sha256": "eb5ac3498b4a516485d9516e2a27115b36e1c434933762a39b62bef488071371",
      "size": 7268
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p7/r17-b4-fmv-p7_init.xlsx",
      "sha256": "19df7d7e0964b850b9d1fe0faf6cf037fd3c2d5fa49240656cd864539678d998",
      "size": 7175
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p8/r17-b4-fmv-p8_golden.xlsx",
      "sha256": "6b07f62f8fae1afd98338bbde7bd2427dd6a5fad22fec6399ca95f97b586cfcc",
      "size": 9400
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-fmv-p8/r17-b4-fmv-p8_init.xlsx",
      "sha256": "d37e012354b46499c3cfe224890b5b7bfbbeebad5ee12fe58b43b2f25e7207c0",
      "size": 9312
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p0/r17-b4-ioc-p0_golden.xlsx",
      "sha256": "fe3fd83bc4c29269b366748b5a2d02afdf823ae148fbc4707e0218567e803ce2",
      "size": 5649
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p0/r17-b4-ioc-p0_init.xlsx",
      "sha256": "2e6fe54eaba3d7f72f3d6e2a84df6d9b5268f1cbb032f917878612975fca4cef",
      "size": 5623
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p1/r17-b4-ioc-p1_golden.xlsx",
      "sha256": "149caf320cfbff8f3732d9d551fd2d36efadcf7fb373d4bfa1a1cf8e6c8ae664",
      "size": 7099
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p1/r17-b4-ioc-p1_init.xlsx",
      "sha256": "e9deb486aea98a637499605408e22b12dea3a47e1557dcec75dee33359f96a64",
      "size": 7072
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p2/r17-b4-ioc-p2_golden.xlsx",
      "sha256": "2d9afd1796e2d85d54ff86fb7e06ad03fe44c7519812a689c67a82852e0f8ba4",
      "size": 9273
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p2/r17-b4-ioc-p2_init.xlsx",
      "sha256": "6b7bdbcff817dbe1a9bc9effcd6e6349137fa3e5c33ecfac6d01e40027b32656",
      "size": 9246
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p3/r17-b4-ioc-p3_golden.xlsx",
      "sha256": "311d210f811591a024774fc3c7c94098f98ae48157c8a285c6576c8b05e521d7",
      "size": 5754
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p3/r17-b4-ioc-p3_init.xlsx",
      "sha256": "8650bd09d326dcad32ad636f105e87b2bd9d2dc2f343a12c2e5db8faef229aae",
      "size": 5722
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p4/r17-b4-ioc-p4_golden.xlsx",
      "sha256": "e3844f90b72463a2453d38ac0c4e3155e683725e4c37e52dd528ee163e459572",
      "size": 7268
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p4/r17-b4-ioc-p4_init.xlsx",
      "sha256": "602dabd490279ef4a39afc11060ee0772a8e9462d9d1c1dddaf54dd9e5c6d997",
      "size": 7236
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p5/r17-b4-ioc-p5_golden.xlsx",
      "sha256": "9c295024fdd4094f7b1c11e44a8eecb1ee80ef82c31b41cb31f1b1bf3f1f0d25",
      "size": 9182
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p5/r17-b4-ioc-p5_init.xlsx",
      "sha256": "638b7262ff09e7c0748921b5fe7f701924ed68d9b43de636df2a9a917aa3d5dd",
      "size": 9150
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p6/r17-b4-ioc-p6_golden.xlsx",
      "sha256": "b40151350c808a3d1d6952ecc235585e0f3747abf6705c76cd60a8380220b7fd",
      "size": 5935
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p6/r17-b4-ioc-p6_init.xlsx",
      "sha256": "b0ab494e043fd39f5fe81515edee893441e5dafaa006bd3521ebfa7874894573",
      "size": 5897
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p7/r17-b4-ioc-p7_golden.xlsx",
      "sha256": "ce1ec764cf44fb00aa4b59ca5cc209beef654ffb53795e72dbea8a5d80ef2302",
      "size": 7140
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p7/r17-b4-ioc-p7_init.xlsx",
      "sha256": "7246f3830862c6860ef36f11889eda5b22306d3b774609a58978b16de6640b43",
      "size": 7103
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p8/r17-b4-ioc-p8_golden.xlsx",
      "sha256": "7cf785c8e94daa7801197b901752839c20a77425c0ae8b54c9f75cbc32fb45c6",
      "size": 9295
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ioc-p8/r17-b4-ioc-p8_init.xlsx",
      "sha256": "9692539117949fc0810ebaff586bdc88c9cf1727f33906ebc2cc007ae0774ef8",
      "size": 9257
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p0/r17-b4-msp-p0_golden.xlsx",
      "sha256": "6dcd09306b97a29b8d626ae7d4dbcdb35c8626afb960cd674153ef38fb059b06",
      "size": 7427
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p0/r17-b4-msp-p0_init.xlsx",
      "sha256": "8dc9ee64dd8f9776a4f68e81d51e01d0eb86c075c8be725545e16084e0ddf57c",
      "size": 7398
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p1/r17-b4-msp-p1_golden.xlsx",
      "sha256": "6bc10a304c51f7442f0e0b6f74742031254d0a1f84ff27f3e495de3688cf0eb3",
      "size": 8864
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p1/r17-b4-msp-p1_init.xlsx",
      "sha256": "8c2b3c5e48fd50c671b15e7821a0e0832bd51612bdf29eb6b88e328a051e2686",
      "size": 8835
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p2/r17-b4-msp-p2_golden.xlsx",
      "sha256": "12da3c6648e3958b86de5c8b77a6d648974af0612d5fea77c09415a62b314a49",
      "size": 10953
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p2/r17-b4-msp-p2_init.xlsx",
      "sha256": "6b25e6495156a806f9b5f49bd51e1abf19fff1e06e369ff13fce2db9398947b2",
      "size": 10924
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p3/r17-b4-msp-p3_golden.xlsx",
      "sha256": "7ee5e729eb589b49c57e115d2753bc0fd2507146014e3c86987cab1e2ad92b70",
      "size": 7614
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p3/r17-b4-msp-p3_init.xlsx",
      "sha256": "edd80bb16e18f6905cf6c5cd85594896b4a6a85efeaec2905d1dac9ad95b467c",
      "size": 7585
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p4/r17-b4-msp-p4_golden.xlsx",
      "sha256": "8ea31c42e843c06b266e78d75a686f9f6fcb1d9bd02361ce9e64b7f0fb129d9f",
      "size": 9006
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p4/r17-b4-msp-p4_init.xlsx",
      "sha256": "1b84704e50394e0ff8e60952ae0e0791ca061e28d1032529d01f133e70825dc3",
      "size": 8977
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p5/r17-b4-msp-p5_golden.xlsx",
      "sha256": "d691c652c4af08f00b73648fc7f01e3f381883592b58d3cc91a2a4917f6f4e0b",
      "size": 11044
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p5/r17-b4-msp-p5_init.xlsx",
      "sha256": "995671593aa092cb3ae121f57a11d45bde4db1c149b0e47f835c1ee0ce321486",
      "size": 11016
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p6/r17-b4-msp-p6_golden.xlsx",
      "sha256": "0b332f6e37e30a60ec8fbd747f835c387c818354828569461b1fa18767055f3b",
      "size": 7745
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p6/r17-b4-msp-p6_init.xlsx",
      "sha256": "d5addc5729c8bf23bb06c09be18898a937ebf0702517e5dfd575d00bd4f3f92f",
      "size": 7725
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p7/r17-b4-msp-p7_golden.xlsx",
      "sha256": "91a1253668a2cb508926bcb62b8853107a9d258e0e6d928aab8db4e1856fa629",
      "size": 9081
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p7/r17-b4-msp-p7_init.xlsx",
      "sha256": "611e107ea0b6a719c68904e6443100b07cc2623304136055fcd5eeb79974e692",
      "size": 9061
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p8/r17-b4-msp-p8_golden.xlsx",
      "sha256": "3aeb1b21647eba779189ed5d23494fdd02a205e3d59dad6444ae9be350eba500",
      "size": 11214
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-msp-p8/r17-b4-msp-p8_init.xlsx",
      "sha256": "110d63291ea153b603f3b934a3d9f263a6ae625324e55743f1a9eca43421b1fe",
      "size": 11194
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p0/r17-b4-ska-p0_golden.xlsx",
      "sha256": "9adba1253d6776cd2704e533d4de1c840bc9a77bf46e9966aa3f4becf2c899fa",
      "size": 6307
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p0/r17-b4-ska-p0_init.xlsx",
      "sha256": "6c1239a2fbcb1f79b1e01364ff0235c1a9a1000d6e7213730a277aea29121d1d",
      "size": 6290
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p1/r17-b4-ska-p1_golden.xlsx",
      "sha256": "15e87280443076be8332a415aeaaf4f0a3f529b3baaa58d4bf53e89c9b14b84e",
      "size": 7781
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p1/r17-b4-ska-p1_init.xlsx",
      "sha256": "fc99a6d1a9b6deb196e08cf9c8d8149070f69f6b1f83f0efa8e10e1d81771766",
      "size": 7763
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p2/r17-b4-ska-p2_golden.xlsx",
      "sha256": "027ce8d3172b601575485b1a455657e24ea5b1b388f8f51512a3b7c18a04ddbf",
      "size": 9940
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p2/r17-b4-ska-p2_init.xlsx",
      "sha256": "f9b7b8378dd5febf24b8f92dc8760c215543a10c90d95f1dfd2628fbe2fae08a",
      "size": 9922
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p3/r17-b4-ska-p3_golden.xlsx",
      "sha256": "2361d27bf8559936a123b9be116465c9f56b73094776a69aac8d275563950b56",
      "size": 6477
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p3/r17-b4-ska-p3_init.xlsx",
      "sha256": "2c94b4e124dea4f40a1414133d922ae58a0a6e632aa96a756f032ff75c839eab",
      "size": 6448
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p4/r17-b4-ska-p4_golden.xlsx",
      "sha256": "3a6adcfd7ccc651853683407a75bb8365c7e8eaf5769107b9b5596bde5068261",
      "size": 7956
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p4/r17-b4-ska-p4_init.xlsx",
      "sha256": "12db3dae36e40d54392ff2b0a9a33e6f68580f6d44e622970f4cee60ad1dce5a",
      "size": 7927
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p5/r17-b4-ska-p5_golden.xlsx",
      "sha256": "f33672154126233eae69743d18f48fce1fa6f00b50ffa092544a06bb65cc35de",
      "size": 9863
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p5/r17-b4-ska-p5_init.xlsx",
      "sha256": "1eed9c23d4c60df2c3d5c052aeb4ca3000a965e2ec1916d126a5d13dfb87e19b",
      "size": 9834
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p6/r17-b4-ska-p6_golden.xlsx",
      "sha256": "69e72e4aa32a19e0e3cabd78d0c50036e2dbddece252321b818ce977da02ad61",
      "size": 6659
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p6/r17-b4-ska-p6_init.xlsx",
      "sha256": "aabdbdeed0ae73ba9691d2745951c2c89e255df1c4e44779b4d41f1c7843bbc4",
      "size": 6620
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p7/r17-b4-ska-p7_golden.xlsx",
      "sha256": "44e7cf531aa0794e48680c31647cdba0d42d611a7d272bfeafdc0ea159a2bf29",
      "size": 7838
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p7/r17-b4-ska-p7_init.xlsx",
      "sha256": "3af9aae3ea68789e74948b4fa1cc4701957d71892a5001fde9f5dbb20cf58f88",
      "size": 7801
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p8/r17-b4-ska-p8_golden.xlsx",
      "sha256": "a1d33a824e3bad111a4e69777f228ffde6bc8e78b3db5508e79b86ea6063a244",
      "size": 10023
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-ska-p8/r17-b4-ska-p8_init.xlsx",
      "sha256": "cc6a06605653330f906e2a0f4038bd5fe1fbe9601cf3cb8e14385492f3a54694",
      "size": 9984
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p0/r17-b4-tsr-p0_golden.xlsx",
      "sha256": "db29284e5d688631b0a057aa55b48c6d45ea4f25d23c55c4eb32ec4bf0529dc2",
      "size": 5615
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p0/r17-b4-tsr-p0_init.xlsx",
      "sha256": "2ba9077e478900d86c6f935d885aac3000fb9297b43fab992ba99f3d7166c792",
      "size": 5592
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p1/r17-b4-tsr-p1_golden.xlsx",
      "sha256": "ae0801fcbe3bb27cd5f9155e9e3871fa52ece4a1adfc36b7603c6a284ed4c54d",
      "size": 7634
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p1/r17-b4-tsr-p1_init.xlsx",
      "sha256": "0ce3582dfe22fb632a95399b71c2aa2f8005cea301ba411104e6111879fe37db",
      "size": 7611
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p2/r17-b4-tsr-p2_golden.xlsx",
      "sha256": "dab164f81ac5f93253dff8925f2889026f39914e4237040fd9f63b85a7367835",
      "size": 10980
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p2/r17-b4-tsr-p2_init.xlsx",
      "sha256": "615c0ebd16548268abb2e008a1c8f99d7620179ebf90fa02c9b77238a138c021",
      "size": 10957
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p3/r17-b4-tsr-p3_golden.xlsx",
      "sha256": "cad7af357d2b1fd19b19def3b05c5686953f8098bb0a0c9614ca2dd0b16148d1",
      "size": 6325
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p3/r17-b4-tsr-p3_init.xlsx",
      "sha256": "d548659d6d80af0f726638f3a929b0db05012c3667a0246e60a56909f28458e3",
      "size": 6292
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p4/r17-b4-tsr-p4_golden.xlsx",
      "sha256": "bd048c7150518616e200ff01cb6e4ba0da8ed508e7984b14032ecd4c65717643",
      "size": 9067
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p4/r17-b4-tsr-p4_init.xlsx",
      "sha256": "9f5b587cfc364433e16307a82d204785924595362e13290b4b54a65f2ab0258f",
      "size": 9035
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p5/r17-b4-tsr-p5_golden.xlsx",
      "sha256": "b5d4fe5d4d8c734f6bd3b936e78512df873544a713cf05c17cddd9936af79656",
      "size": 9143
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p5/r17-b4-tsr-p5_init.xlsx",
      "sha256": "4b1a3837b181c0797048e4d3f9618ea46db5d4a7f19e9d1a1d46bb2b563cc8d0",
      "size": 9111
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p6/r17-b4-tsr-p6_golden.xlsx",
      "sha256": "15c28a7bd5b1aecef7ef0f882b75007abbeb1d9d8eeedd4dd4539bd2c49eb7ae",
      "size": 7846
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p6/r17-b4-tsr-p6_init.xlsx",
      "sha256": "3a6483b71f051babfb1a9090285d6498400fd5efd421da60f52adb0e87e88028",
      "size": 7808
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p7/r17-b4-tsr-p7_golden.xlsx",
      "sha256": "8d08143022646fdbe2778696dcad6448cef7a72ffc4710bef0fba283c5be3d7b",
      "size": 7110
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p7/r17-b4-tsr-p7_init.xlsx",
      "sha256": "a7df28e3cd681b7b7f3de41cdadaa5f97f521d7404e5e56b090680936b3c140c",
      "size": 7073
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p8/r17-b4-tsr-p8_golden.xlsx",
      "sha256": "8815037301c755af9ef2afc9aa9681d2f84ce8bc0b4543bf0afdf2eb6c872818",
      "size": 9905
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b4-tsr-p8/r17-b4-tsr-p8_init.xlsx",
      "sha256": "9d5d0c633cda8aac5f668564747a28c9bdece0b168bdfea1cb98ff0eb6088162",
      "size": 9872
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p0/r17-b5-agj-p0_golden.xlsx",
      "sha256": "8d0def8c714d054be150388fd12619ffd43b89a2cc379d57510bdf7272509fa5",
      "size": 7216
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p0/r17-b5-agj-p0_init.xlsx",
      "sha256": "afb494d465b48026df267af17986fc7bc4448837497a5d85235238000e2ecbaf",
      "size": 7197
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p1/r17-b5-agj-p1_golden.xlsx",
      "sha256": "df456a6e654b575c9c754b8b47e6023dc3b94a5ab9192f6b0f9159651a7de831",
      "size": 8607
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p1/r17-b5-agj-p1_init.xlsx",
      "sha256": "5a70bc3f9bf063bb5f352a09c18dddda4b40c8bb06a71e83758456ded8e121b9",
      "size": 8585
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p2/r17-b5-agj-p2_golden.xlsx",
      "sha256": "85ec9ac833df78271de2ab9d19a84d9c70d4794c160cfbaa48f8fd3fc149ec4c",
      "size": 10710
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p2/r17-b5-agj-p2_init.xlsx",
      "sha256": "0a4e797a0baf884dd6b52d35bb117b725140f03999b5229ecb621d53b4294e0d",
      "size": 10690
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p3/r17-b5-agj-p3_golden.xlsx",
      "sha256": "9df2f4be7916e56b1023f7f602e93b346a1c378402adc1157a4cbf8d1d8f25b7",
      "size": 7315
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p3/r17-b5-agj-p3_init.xlsx",
      "sha256": "0fee46ca98398d0a63bfa4f6ed29c4e4dabe738144a9eaa62d7bcd9df5b32b52",
      "size": 7295
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p4/r17-b5-agj-p4_golden.xlsx",
      "sha256": "e52cb24cf022d74aed6354ad3020e3cc0903b3200126fde47d2a388555fde464",
      "size": 8729
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p4/r17-b5-agj-p4_init.xlsx",
      "sha256": "d13bf90452687339928784db89300596fba35c008caf307bffa59a3501d3dbde",
      "size": 8708
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p5/r17-b5-agj-p5_golden.xlsx",
      "sha256": "f23569ff9cf2054c6f7d02b4d31f723aa81ca263dff515b2c8d5291a950988e9",
      "size": 10806
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p5/r17-b5-agj-p5_init.xlsx",
      "sha256": "ebfa2dd7e359b514fe65021c733ed4486ac3187e73fb0dba4e967e6bdd4411bd",
      "size": 10786
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p6/r17-b5-agj-p6_golden.xlsx",
      "sha256": "d0bffddd127356f0a95140991b47227a6d686ad04857a4e816b29b6ff219d77a",
      "size": 7457
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p6/r17-b5-agj-p6_init.xlsx",
      "sha256": "8c5319cec2556c6331c0a1f2a94eb222dfe808147285b4f50f90bf2b2ba93654",
      "size": 7426
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p7/r17-b5-agj-p7_golden.xlsx",
      "sha256": "f91a7e35832bbb49e77757226a1f2fa01f07b30a997f341fc60f21ec33c337b3",
      "size": 8842
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p7/r17-b5-agj-p7_init.xlsx",
      "sha256": "94a67d0689abdd9a49ab3550a646dbc43dd9b00e8474e348d72a37d99d69e5c4",
      "size": 8811
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p8/r17-b5-agj-p8_golden.xlsx",
      "sha256": "f267df76ef7573c2a0dff754db110859a650f2e069c5f5bee173bbecb4894d3c",
      "size": 10920
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-agj-p8/r17-b5-agj-p8_init.xlsx",
      "sha256": "72977665d041a15b8d4f39d129e70df2112c860f56ed87b361c4a26d81fc2060",
      "size": 10892
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p0/r17-b5-fmv-p0_golden.xlsx",
      "sha256": "15eb08ecfc86b37983dad399b9452a549e6907bfff504774c25537331473fb4d",
      "size": 5708
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p0/r17-b5-fmv-p0_init.xlsx",
      "sha256": "f698322656b7c50153d9bfc827d706bf65be2ebd97fca58edeca650f33039b7f",
      "size": 5661
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p1/r17-b5-fmv-p1_golden.xlsx",
      "sha256": "20f1e5fda70f620ca4ca70bdcb333185cdf944d1fd388edaf6f59b040787e4e2",
      "size": 7140
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p1/r17-b5-fmv-p1_init.xlsx",
      "sha256": "226cd0da80168e646001d3354eb05d43bf19fe876898f2047139d57cec09cf7e",
      "size": 7092
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p2/r17-b5-fmv-p2_golden.xlsx",
      "sha256": "b39bfe73a5fe493c9b6bf7eac30e0c010201ef756e4a9dac7ba3a57bff352974",
      "size": 9279
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p2/r17-b5-fmv-p2_init.xlsx",
      "sha256": "56450cc820e11e3092399b691fe8fabbb4631540cc04b0f7fc9cf6c18235c6cd",
      "size": 9232
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p3/r17-b5-fmv-p3_golden.xlsx",
      "sha256": "7abf3209147b174506d1e6e381aa730a3b80c68ae5fd8f6e711ffd2168d146bc",
      "size": 5821
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p3/r17-b5-fmv-p3_init.xlsx",
      "sha256": "96ef53352af856e7fb8f73047887d7333759e2ac616f74c1185c567417a0180a",
      "size": 5757
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p4/r17-b5-fmv-p4_golden.xlsx",
      "sha256": "773b54fa87ca782e111f3071da5df503aa9bb0356d82e65cf88cabbdeaef2945",
      "size": 7296
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p4/r17-b5-fmv-p4_init.xlsx",
      "sha256": "af52a4c8215bb74ee2b5ada00753cfc4ab2673bfc3bafda38ffdcf26828216a1",
      "size": 7232
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p5/r17-b5-fmv-p5_golden.xlsx",
      "sha256": "d0091ffb166639c26b36691dbb9debe0007a5327e6f8ff1dfb39dfb93d11f300",
      "size": 9254
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p5/r17-b5-fmv-p5_init.xlsx",
      "sha256": "5f39c711362210b1dd0dbf4df2d867d6c43180bd35c047153a08cc484904bffb",
      "size": 9191
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p6/r17-b5-fmv-p6_golden.xlsx",
      "sha256": "22143ad103813294e73305b358a9663342b6222d91a75fc907e892233f5c9c92",
      "size": 5997
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p6/r17-b5-fmv-p6_init.xlsx",
      "sha256": "637210f5963bd2893f560cccd5c93ef895c8167bfb6668c78a0ed53e037385a0",
      "size": 5906
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p7/r17-b5-fmv-p7_golden.xlsx",
      "sha256": "f59d9b61c2ef2936356f5f3005ddd1ab827462f1411bc7a31dbc809257bb7194",
      "size": 7256
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p7/r17-b5-fmv-p7_init.xlsx",
      "sha256": "b225c16767aaa4c63fb066ac30299f5e043e7f9f06eba5ee101b295a135476c9",
      "size": 7170
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p8/r17-b5-fmv-p8_golden.xlsx",
      "sha256": "0814f4c156c627c6e6527d73fc871062f52da935110ec37d7ee9efb1c2af2454",
      "size": 9396
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-fmv-p8/r17-b5-fmv-p8_init.xlsx",
      "sha256": "5ceb4683a078d426bc4fe73cdfa3240d7c8654c74aa2ee4740617e2bec85ac5e",
      "size": 9307
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p0/r17-b5-ioc-p0_golden.xlsx",
      "sha256": "553288a8538e5e2bcfc6cf750e927d04f5eddb3bbace20a571a1778bf9993420",
      "size": 5650
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p0/r17-b5-ioc-p0_init.xlsx",
      "sha256": "e1dce1040708b30bfb71f8f229f0b464557c5ce56ec5f348cacbdd7f2613bc74",
      "size": 5623
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p1/r17-b5-ioc-p1_golden.xlsx",
      "sha256": "5954023f53e7694a5e9f98a5ce5d6f0b43be8400458ec0017f3de29e49475719",
      "size": 7102
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p1/r17-b5-ioc-p1_init.xlsx",
      "sha256": "b13ad0dd9c12f64c58a5f8d70b3ca574194f3b53a23e1745d88beebaa720c6fe",
      "size": 7075
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p2/r17-b5-ioc-p2_golden.xlsx",
      "sha256": "6da8ff86b9da51b432304c1b60ec3dfa2036e1eb61d926549aa9e2b0902bfa7a",
      "size": 9271
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p2/r17-b5-ioc-p2_init.xlsx",
      "sha256": "d1b7cdff7c0687325ea887f83341f21d61e127094588b5d79b4121798e961481",
      "size": 9244
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p3/r17-b5-ioc-p3_golden.xlsx",
      "sha256": "e32cdd9ef6d3393d5b498efb9726db4ebd2f23433ea982429e48e880285b446c",
      "size": 5755
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p3/r17-b5-ioc-p3_init.xlsx",
      "sha256": "d712c8cca5ec9e8c6480621fdd8fe1a5b212aefd01c3387080d62abdc465141b",
      "size": 5721
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p4/r17-b5-ioc-p4_golden.xlsx",
      "sha256": "1f13754e8d050e5cf5ea87c3c69c3a5e2aba912f67e0124cb97c40b4ddc318c5",
      "size": 7262
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p4/r17-b5-ioc-p4_init.xlsx",
      "sha256": "4ec7c71976e12d331e907dbe6e43a7eb19d30d45db3e25ccb5c8a87bc6326720",
      "size": 7229
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p5/r17-b5-ioc-p5_golden.xlsx",
      "sha256": "b1baa501e415acd05e0d83c92654521db84235d6b5baf4483d42ab4ef1f088a4",
      "size": 9181
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p5/r17-b5-ioc-p5_init.xlsx",
      "sha256": "b63236378c4e72a11d515f941ee0ca0c78e69787c9bd6b8cfd18e817e6ae1f29",
      "size": 9149
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p6/r17-b5-ioc-p6_golden.xlsx",
      "sha256": "1645567e8f7446d01c7a1817bb7d9efd7efc5e6dd92cc001adde393ef7bfc6ff",
      "size": 5934
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p6/r17-b5-ioc-p6_init.xlsx",
      "sha256": "ab7472d92e656e84c8e703f81d82a23614c69762c632e81a9a503bd31e7f38ac",
      "size": 5896
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p7/r17-b5-ioc-p7_golden.xlsx",
      "sha256": "157694df5dd3d2c5c00dbf766f67740756b2e9adc1a077dd1118cb3ba080f53e",
      "size": 7143
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p7/r17-b5-ioc-p7_init.xlsx",
      "sha256": "c7f219fa08886d3822d0e043586922d5eb476094db11621afffcf435087b75b0",
      "size": 7105
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p8/r17-b5-ioc-p8_golden.xlsx",
      "sha256": "61cde561eab54d6155a91496222de06bf4bf4c6932f4f0db6c6704fac27594e2",
      "size": 9301
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ioc-p8/r17-b5-ioc-p8_init.xlsx",
      "sha256": "f45a964e7eef43fc63f29a11d464d523158b722ee7473a391943cd247487d307",
      "size": 9263
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p0/r17-b5-msp-p0_golden.xlsx",
      "sha256": "097aee4c9a500080d8efcefa14b7f82622ac3558a8aa90847b98aeaf0f51046f",
      "size": 7423
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p0/r17-b5-msp-p0_init.xlsx",
      "sha256": "1ac241fb80c4f240d4513c94a2f9efe4c58b2c9551338b40a91edf9027ec73e9",
      "size": 7394
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p1/r17-b5-msp-p1_golden.xlsx",
      "sha256": "7cda0619b16ef15e6ba803faccd12cdc5e90eb5774466867fd9aff00d3df8dbb",
      "size": 8871
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p1/r17-b5-msp-p1_init.xlsx",
      "sha256": "a47bdd8e0083234c5833d9ccf7c07e2ac17a010ba6325b1137e376f042c6ab93",
      "size": 8841
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p2/r17-b5-msp-p2_golden.xlsx",
      "sha256": "007facee25dd5336e7019cfe5e790370850fe6c4c9781f78e1963709b4227c92",
      "size": 10950
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p2/r17-b5-msp-p2_init.xlsx",
      "sha256": "87198b6fab16f734c78f2329d339dca80f01a6a23d2f583c74b6c240abfab038",
      "size": 10919
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p3/r17-b5-msp-p3_golden.xlsx",
      "sha256": "d124041468ab7cbf43be5de81f2096efafd94c6b42a244bcc1fe2391914453e3",
      "size": 7601
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p3/r17-b5-msp-p3_init.xlsx",
      "sha256": "964f61bd2310a37cef3b9b428e230e56bcc6d84aae51498261d7f2f5e05409ed",
      "size": 7571
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p4/r17-b5-msp-p4_golden.xlsx",
      "sha256": "f325fa9624ebeedc334c29c2c42c8e7a8330c97ce4c6add32ff849dfdf8050dc",
      "size": 9018
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p4/r17-b5-msp-p4_init.xlsx",
      "sha256": "d76906f2081ab7f86e172081be053808e8406d8cfeeab89b4a50205bc35fc122",
      "size": 8989
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p5/r17-b5-msp-p5_golden.xlsx",
      "sha256": "c8980c22ac8b0e5117c91ef53bd7bb0d933ab5c02f30ef429c1e7e472818b553",
      "size": 11032
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p5/r17-b5-msp-p5_init.xlsx",
      "sha256": "573239471b9c09046cfab0d68daa7f1f45718e0bf8ec7d16e1b4ef47bdd3c19c",
      "size": 11004
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p6/r17-b5-msp-p6_golden.xlsx",
      "sha256": "609cf378f3d0b346151754b44e2e6181ee2eb81c829ffe308e0bf175da04c46a",
      "size": 7753
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p6/r17-b5-msp-p6_init.xlsx",
      "sha256": "44796cf2b1e839c66817aff7fc57c1c6811db40fd45ec2655a90c865c9556041",
      "size": 7732
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p7/r17-b5-msp-p7_golden.xlsx",
      "sha256": "cdd2ba4f96d1c3af106bce48340c4bed1c529afa6ecec2634a2da380335a87b4",
      "size": 9087
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p7/r17-b5-msp-p7_init.xlsx",
      "sha256": "10234f30642cc59bb5029dfc2ea0e150468ad8f0a740291873ae5fad8b23cb98",
      "size": 9067
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p8/r17-b5-msp-p8_golden.xlsx",
      "sha256": "9d526c405dff2275982903cf378b2e8f6f39cccc04dfba1ce27ed91bbe33b0df",
      "size": 11215
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-msp-p8/r17-b5-msp-p8_init.xlsx",
      "sha256": "73ddad5df76d2f65fdcf9e0f50a4bdbb001429cab0ad55c2005fff25ddd0fb31",
      "size": 11194
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p0/r17-b5-ska-p0_golden.xlsx",
      "sha256": "8827bdf2921929db03e86bee723170f15484da8a2ccbe9e9b8d17d078539896b",
      "size": 6312
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p0/r17-b5-ska-p0_init.xlsx",
      "sha256": "321d43b3e3293f691552c1b59edc544af5e41837414dc7e8cd6a769cd9ae0f5e",
      "size": 6294
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p1/r17-b5-ska-p1_golden.xlsx",
      "sha256": "35204b45b78c1b0fb0107ccb35fa62b75a0d290c82f7bf12887a790a00330ceb",
      "size": 7785
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p1/r17-b5-ska-p1_init.xlsx",
      "sha256": "ac87d7d52463bc2e9dfba2fca61fe318eb647cea0bc58366a3475a2ed1da61b8",
      "size": 7766
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p2/r17-b5-ska-p2_golden.xlsx",
      "sha256": "254c1c6e666d797a8cc5e5940a2b49371f4fc20f6dae9173c62a01d9cb692b8d",
      "size": 9935
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p2/r17-b5-ska-p2_init.xlsx",
      "sha256": "e2ac3482bfd7f9c9773844894ee0f84311861723d07713938c8c1d0002159eaf",
      "size": 9916
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p3/r17-b5-ska-p3_golden.xlsx",
      "sha256": "685a5876d3c2d11d97f2051b09e3e8a31a1cf636039da5c4cbeb413486ee3fc4",
      "size": 6473
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p3/r17-b5-ska-p3_init.xlsx",
      "sha256": "1a11c7c11770e92e8bcbcf9d71d0a07b434cc4de8e1df100659624b84e555fa0",
      "size": 6444
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p4/r17-b5-ska-p4_golden.xlsx",
      "sha256": "85a2b70331ebcf22641621a2b47228d8acc085e41a069feb9d88b764f81227b8",
      "size": 7963
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p4/r17-b5-ska-p4_init.xlsx",
      "sha256": "ec2af47760142a76338487958dd113293e6127b591a08c44db6b78c1367f8ddf",
      "size": 7933
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p5/r17-b5-ska-p5_golden.xlsx",
      "sha256": "a96dc1e40a28da0068fff7618c4f53350e1792bb2f2eb1f3c1efdcec9d9973ea",
      "size": 9857
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p5/r17-b5-ska-p5_init.xlsx",
      "sha256": "cfb8823cd4122d9a04a3ea87214e9d2ccbd0c23c9f5d2e580918c558a0846dab",
      "size": 9829
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p6/r17-b5-ska-p6_golden.xlsx",
      "sha256": "996785a0368e8e1583b9cef2dda33dfe2224af28a7e8b3bf92e23397bcc8ce65",
      "size": 6659
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p6/r17-b5-ska-p6_init.xlsx",
      "sha256": "b7941977868ca6303b93da51b4a1559be93061131886098ee440de8d98e20313",
      "size": 6621
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p7/r17-b5-ska-p7_golden.xlsx",
      "sha256": "b6a9eb13f73d3d0dfc7d5f9b2a73aff0b47d1057c0cd844d9c47cd6613547166",
      "size": 7828
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p7/r17-b5-ska-p7_init.xlsx",
      "sha256": "b770a570b83f2e3f41276328d798e47b38fbde5a9eb069c5148e2f35be7e3cac",
      "size": 7794
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p8/r17-b5-ska-p8_golden.xlsx",
      "sha256": "f280cf8c1db24661a336ccf344a7c21b0a5232aefa45c62bc8e954158b8f1cc1",
      "size": 10031
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-ska-p8/r17-b5-ska-p8_init.xlsx",
      "sha256": "358a2ca06a1043d5b365d95d4c942f86f1cff7fcb54c5d186816fe610d675d47",
      "size": 9993
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p0/r17-b5-tsr-p0_golden.xlsx",
      "sha256": "73a792b1c562410a410dca9eb5577a6df5732d2202586238674ab3fb8b62b26f",
      "size": 5614
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p0/r17-b5-tsr-p0_init.xlsx",
      "sha256": "2a07f70cf46e66804e1c1516bf30ebff447ef15a1d086a51ab2ae9e6d6c926ca",
      "size": 5592
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p1/r17-b5-tsr-p1_golden.xlsx",
      "sha256": "68d740ad2d28015ff7985c4213c520ba792ca53356f15eaa81816ef43f7d1401",
      "size": 7637
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p1/r17-b5-tsr-p1_init.xlsx",
      "sha256": "8cef3a0f2680d7752920bef7f8e7c8ef31b330964de71e4b95216ffd8a705975",
      "size": 7614
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p2/r17-b5-tsr-p2_golden.xlsx",
      "sha256": "738e514ff463d78e2437274c66497a71fd29c04f89e252514acedbccbcb0306c",
      "size": 10981
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p2/r17-b5-tsr-p2_init.xlsx",
      "sha256": "7b63c0a0ebd6af1725148604d941dbac87f39b55b27baa41908aad327923af64",
      "size": 10958
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p3/r17-b5-tsr-p3_golden.xlsx",
      "sha256": "f636cf4500f2241cd55d2ab340da328c4aa992ebf90d086bab538563d828d847",
      "size": 6325
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p3/r17-b5-tsr-p3_init.xlsx",
      "sha256": "ffbe0ad5090aabd79c6105bed9af3a268f4c4fe207c6c3ae5d2ee9e84ccd4dc1",
      "size": 6295
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p4/r17-b5-tsr-p4_golden.xlsx",
      "sha256": "f32b7ab9a47b5acd2564fb6dbeaad60102a3fd7355306a44ba77e005b10ce9b8",
      "size": 9058
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p4/r17-b5-tsr-p4_init.xlsx",
      "sha256": "550fa585fa945122423be6aa53cd31b59cc977360c48e3c49231f1d65970d48b",
      "size": 9026
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p5/r17-b5-tsr-p5_golden.xlsx",
      "sha256": "22c38a88ce41a6d7db3c2c3142fad89b7ac54a73c6c871eb187f53d7d8e76e53",
      "size": 9144
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p5/r17-b5-tsr-p5_init.xlsx",
      "sha256": "56720506f59a80100b5d8d601372890ade36ce0debf951296e0f814c6ed95303",
      "size": 9111
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p6/r17-b5-tsr-p6_golden.xlsx",
      "sha256": "3b71791bc737786ae0f20a2034558b3fe4f5438949136f34c271881d762a0fae",
      "size": 7832
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p6/r17-b5-tsr-p6_init.xlsx",
      "sha256": "956b646090c3e6e9bd76c9499c58d74b1af8d10ccafbc73a3dea48be79dd11af",
      "size": 7798
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p7/r17-b5-tsr-p7_golden.xlsx",
      "sha256": "da0f0d12171b4d19e34c9fcb0b52080bdd9d30db48b38904b7aa0e8ed17ccece",
      "size": 7111
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p7/r17-b5-tsr-p7_init.xlsx",
      "sha256": "08230ee949e0ecde7c1ae889faef242af56607fb8bd2eb67a92991d24f53ce0a",
      "size": 7075
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p8/r17-b5-tsr-p8_golden.xlsx",
      "sha256": "b65c843ea1737886d31a56bd0ad35cf91d0ad178f667902d3aeb9747c6d500d0",
      "size": 9894
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b5-tsr-p8/r17-b5-tsr-p8_init.xlsx",
      "sha256": "551fcafe075c7974383efe538d389a51af5f98209a9ef4bb912ad2911fdc27a3",
      "size": 9855
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p0/r17-b6-agj-p0_golden.xlsx",
      "sha256": "ac3b58eaef8958c34dae0782679abb06eebec47593344a5ed99ffe7f19793031",
      "size": 7221
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p0/r17-b6-agj-p0_init.xlsx",
      "sha256": "6a12b8aa4a440521115c4c3cbf3abf7d1ea493f566ca78de8964d9f41e7c595a",
      "size": 7200
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p1/r17-b6-agj-p1_golden.xlsx",
      "sha256": "11fe5b1fe7765a2fbc3c5d38d45601ebedf83c6d70c7ca2d9c208fcf8b07cb09",
      "size": 8604
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p1/r17-b6-agj-p1_init.xlsx",
      "sha256": "a4c3479b5a1aaac2f5edb2861c4a017140c1b6b238668bbe0933cda35e36e68a",
      "size": 8582
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p2/r17-b6-agj-p2_golden.xlsx",
      "sha256": "e2d451389f2d31d3179ca84ac6776d7dbb7921a439b00a832d2e3366ef9947fc",
      "size": 10710
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p2/r17-b6-agj-p2_init.xlsx",
      "sha256": "9c102b402cb6a2335227e97cbe2856954fe6bb60c717e5e51e0423b447ef97f4",
      "size": 10689
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p3/r17-b6-agj-p3_golden.xlsx",
      "sha256": "60df3cdec5237d47ea757985f85a5bfe046d5e8de065f91084807aae2f0cda74",
      "size": 7319
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p3/r17-b6-agj-p3_init.xlsx",
      "sha256": "e867494113049623ed5c773bdf1b1a0f16cc6d6ff193c2147a3da430f48c425f",
      "size": 7300
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p4/r17-b6-agj-p4_golden.xlsx",
      "sha256": "2c38bc64e8ab120d30f5c84e55a60c08aa7ec913de366cf7a60759f1d86ca6f2",
      "size": 8732
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p4/r17-b6-agj-p4_init.xlsx",
      "sha256": "7f0ae9f6e7f4f9cd0a3b68ee6f470cddc0f6ae78e9f1b8b63c8b65d948217101",
      "size": 8712
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p5/r17-b6-agj-p5_golden.xlsx",
      "sha256": "250f6e43e26e5a5ba0325c6f63795a1d44142f5d0b8f4b3eca7a41b43f68ec88",
      "size": 10804
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p5/r17-b6-agj-p5_init.xlsx",
      "sha256": "f751bed38d80c58a230d755e5e80a279a239a722ca6dbd13bad14b77f1133a95",
      "size": 10783
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p6/r17-b6-agj-p6_golden.xlsx",
      "sha256": "3541095ccf42d01d4f9b264c68bf8722ac061fe80cfae823a4ef929ba2bb9d30",
      "size": 7451
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p6/r17-b6-agj-p6_init.xlsx",
      "sha256": "03e87bf216fe5737cc49db0c6005413a6481211d2989678cfce030188f797500",
      "size": 7421
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p7/r17-b6-agj-p7_golden.xlsx",
      "sha256": "05feeebf7c21125525bb16af6bc5398bb3e87a5e4a7889a7de5381767d05b16c",
      "size": 8842
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p7/r17-b6-agj-p7_init.xlsx",
      "sha256": "9e6a7602beca786c7226ab844f0d2bf625d7ecff0a013e12274c6ee488541c8f",
      "size": 8809
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p8/r17-b6-agj-p8_golden.xlsx",
      "sha256": "b51e44b176421af1bc92ba2dfaf0d67c7f521bdd3f18dd00af498293c441bfb5",
      "size": 10923
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-agj-p8/r17-b6-agj-p8_init.xlsx",
      "sha256": "f0821b5f1b24d9714fa3a4c7811de7be20dfc5bab08ffa11eadf125dac2e3d4c",
      "size": 10893
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p0/r17-b6-fmv-p0_golden.xlsx",
      "sha256": "605614a5fdb890b9015a654af31ca39bff904656c41de7443afca17beb48716b",
      "size": 5706
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p0/r17-b6-fmv-p0_init.xlsx",
      "sha256": "48023a5b198699d51238014827acedcb73133ad6ac5c602dedc779e58df99edd",
      "size": 5660
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p1/r17-b6-fmv-p1_golden.xlsx",
      "sha256": "754a8f1a4fd70ca20d776ce5cb59533437239192a6ee89864234f35a085987eb",
      "size": 7142
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p1/r17-b6-fmv-p1_init.xlsx",
      "sha256": "075c28967b6323eaf5b632457874aff79db7c9bc2a93a8023644294f7e746a7d",
      "size": 7094
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p2/r17-b6-fmv-p2_golden.xlsx",
      "sha256": "8fb7ab97b40bf07be1d761a9c548ed80bee235697da5a27a168c7e40798b70a7",
      "size": 9285
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p2/r17-b6-fmv-p2_init.xlsx",
      "sha256": "5715f64add1e7af53b767009ee053a59741217df55cfbbb4cf3b1e52cf8f7c72",
      "size": 9238
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p3/r17-b6-fmv-p3_golden.xlsx",
      "sha256": "ffb6bc821d2b104374a84b68df766d0a09abbd14e688549a4bf864036a15e764",
      "size": 5825
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p3/r17-b6-fmv-p3_init.xlsx",
      "sha256": "5f77baecb32aaafe98c6c10a6ec081b56f4e6617f74941897aab3df31a128a9b",
      "size": 5759
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p4/r17-b6-fmv-p4_golden.xlsx",
      "sha256": "c6b3b0a089236992600bb28f2c4c768ba7c0046c5a1d5cbb849bb2bf67787e3c",
      "size": 7292
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p4/r17-b6-fmv-p4_init.xlsx",
      "sha256": "d1d81e25ad752fdd40d58f686b325567b5757c78d220e8957ee8ec6603e7d886",
      "size": 7225
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p5/r17-b6-fmv-p5_golden.xlsx",
      "sha256": "a0216d8cad3cf940bb068eccbc6455315da24b4218bb1e4ef274771b7ae4baa3",
      "size": 9257
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p5/r17-b6-fmv-p5_init.xlsx",
      "sha256": "b60bd8f442a13c4535b69a6f5f9c49265b3ccb83ca00d0b919a41789801cec39",
      "size": 9193
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p6/r17-b6-fmv-p6_golden.xlsx",
      "sha256": "f088bb412b2cc5747247bac66a8affb22514b5f07ccb572a197d16528a7e0ef2",
      "size": 5998
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p6/r17-b6-fmv-p6_init.xlsx",
      "sha256": "f5386229d1f724391778e2932f08c8211f2849c214fbbe408e086a32e99bb930",
      "size": 5906
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p7/r17-b6-fmv-p7_golden.xlsx",
      "sha256": "26de9ce8234926889e1f8fc11b556b61d6d865767d791c2c5ca0faa15176414d",
      "size": 7266
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p7/r17-b6-fmv-p7_init.xlsx",
      "sha256": "ba4892b219af75b2f32a71ccfc664de42fc7af05aa032fe6b0c725be67ddab3b",
      "size": 7173
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p8/r17-b6-fmv-p8_golden.xlsx",
      "sha256": "15a6e50a573cf371a46261dcf2fbb5b82f40dba38fa0c86b2a922511a3802cf5",
      "size": 9401
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-fmv-p8/r17-b6-fmv-p8_init.xlsx",
      "sha256": "67187b51b85f319ebaab658aa845d81c5fa80fbdcba1d7414437016368595f04",
      "size": 9308
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p0/r17-b6-ioc-p0_golden.xlsx",
      "sha256": "3f6642c2b48190acdbd0b7f5abc9894db02ea29f1df7366ee4ac315d21a2df5e",
      "size": 5645
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p0/r17-b6-ioc-p0_init.xlsx",
      "sha256": "9523da76ae6c2aae6b1943f91aa82dc5eae745671097257053dab0bca877437e",
      "size": 5619
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p1/r17-b6-ioc-p1_golden.xlsx",
      "sha256": "52dad3d9e6c169e7ea7925404a5a012a43104eede051f8e869b9ad07e383762a",
      "size": 7093
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p1/r17-b6-ioc-p1_init.xlsx",
      "sha256": "abff4b7848a36e81c89530284a44878767e5eebdac48604dc00efde4dc0ada37",
      "size": 7066
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p2/r17-b6-ioc-p2_golden.xlsx",
      "sha256": "7217ceaedfd52fc9ae406b0292481b37c869614b34072f27e6af63edfa35ef22",
      "size": 9265
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p2/r17-b6-ioc-p2_init.xlsx",
      "sha256": "12afd4f23f63e437b09b1f9e89bc8abe067f90fd29df921c102364698a287ff1",
      "size": 9237
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p3/r17-b6-ioc-p3_golden.xlsx",
      "sha256": "578f2b2ddabf22da81d852fb273afa2bb29b915d74eb84d743d14bd826ffecdf",
      "size": 5756
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p3/r17-b6-ioc-p3_init.xlsx",
      "sha256": "41e45300af92004b518fea36dc63845006d347cfbb8b16fb7b750ba26ee39e57",
      "size": 5722
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p4/r17-b6-ioc-p4_golden.xlsx",
      "sha256": "9f6633db28c361f00bdb626dcfd236146ed93f42607745feecd94616d19a8d4a",
      "size": 7268
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p4/r17-b6-ioc-p4_init.xlsx",
      "sha256": "e2b970ba4e7770b577b05d342529cd6409a098c28ff1cbbb442604e85fdb4ac1",
      "size": 7235
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p5/r17-b6-ioc-p5_golden.xlsx",
      "sha256": "f887922645ec0ce576cba90c03940e66f05029e6f25b429d21f863144d53f769",
      "size": 9175
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p5/r17-b6-ioc-p5_init.xlsx",
      "sha256": "4a12a63f0e5504a9863fa93cb5fd8a80234e258cefae8dbbbb91f4c48bbfda14",
      "size": 9143
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p6/r17-b6-ioc-p6_golden.xlsx",
      "sha256": "bce8142501797cbd2ded13c711da4f9ae8b475768e843fbb1b4ee84b0edb5baa",
      "size": 5930
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p6/r17-b6-ioc-p6_init.xlsx",
      "sha256": "f72847573c1dcbde2705cc31f03796b0448157d1207c183e8e970532ab0e14cb",
      "size": 5893
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p7/r17-b6-ioc-p7_golden.xlsx",
      "sha256": "8575c62aa7304c644b9da39e104ae37754fe785591b0089add9a6f76f8ed172e",
      "size": 7141
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p7/r17-b6-ioc-p7_init.xlsx",
      "sha256": "0768bb12a42a9f5994a33f200606580e2b31eb142162cf2b4e0ff97d8c088bd4",
      "size": 7103
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p8/r17-b6-ioc-p8_golden.xlsx",
      "sha256": "84c2585b1736cf1bdfaaedd4bb64b4f2aa85cafdaea7eb8173fba007260708f0",
      "size": 9292
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ioc-p8/r17-b6-ioc-p8_init.xlsx",
      "sha256": "8b229a5bda7ef10f7c339b5daf3021b0f3146239258e3d4351fb00e516621bed",
      "size": 9254
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p0/r17-b6-msp-p0_golden.xlsx",
      "sha256": "e473b47008c6b0d0b5890e8a2d279ea9c850e5f1ae720a9b3bc45e2ebf433350",
      "size": 7424
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p0/r17-b6-msp-p0_init.xlsx",
      "sha256": "1729b705aed3d6046d1df459f155e2eb92290eb19db6482322ce4df704f96780",
      "size": 7395
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p1/r17-b6-msp-p1_golden.xlsx",
      "sha256": "5484549e102aa849c6606f73524dfc10639e8d394692515b4842272411dd5d38",
      "size": 8854
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p1/r17-b6-msp-p1_init.xlsx",
      "sha256": "93f5370079b6fbd58ac78623bb3179be2469f07f6cc09808c8fae103e7ce4ce3",
      "size": 8824
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p2/r17-b6-msp-p2_golden.xlsx",
      "sha256": "fb1163dbb6d9c473ce7ddf5687219c2400e38609ecfc0490f2c957597621f42c",
      "size": 10949
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p2/r17-b6-msp-p2_init.xlsx",
      "sha256": "ddcbcf05f04e692ad5779983546388f0a684dd5bbaf4152416a4c0a6a89528b3",
      "size": 10920
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p3/r17-b6-msp-p3_golden.xlsx",
      "sha256": "07601c30f5057c20b82b46d99cbe21b9a9b27926c0e9aa4a6ded4faff935eeff",
      "size": 7606
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p3/r17-b6-msp-p3_init.xlsx",
      "sha256": "14b409d72fa8dba72072f84131aacd09ed406c622198c649fd31c1917d041ca3",
      "size": 7576
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p4/r17-b6-msp-p4_golden.xlsx",
      "sha256": "9f22879729fad643c386b5c48346f741d3286f553f1a68d475bfb02e8da447d2",
      "size": 9008
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p4/r17-b6-msp-p4_init.xlsx",
      "sha256": "6625d3b12aaa23d224fbbbaf54072e1dcfbd87b9f7901321cdf440c558f10582",
      "size": 8980
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p5/r17-b6-msp-p5_golden.xlsx",
      "sha256": "028c0ae766a5de968a73f3b73aeee0db28f270221d6ab6b2ea94caa3e1b251e0",
      "size": 11036
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p5/r17-b6-msp-p5_init.xlsx",
      "sha256": "401ece0564bd39cad25f411cfde104ffece242097d5d83be00aaaad48bdf58e9",
      "size": 11007
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p6/r17-b6-msp-p6_golden.xlsx",
      "sha256": "058b1a3acf80608b86bbe1418b1fbdfb8c6a0b5e7516988bca4404bdeb41e13f",
      "size": 7748
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p6/r17-b6-msp-p6_init.xlsx",
      "sha256": "4918d5bea25155c9871695937bd81524cf6e3cb49b17b73a2a2462a16fe34736",
      "size": 7728
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p7/r17-b6-msp-p7_golden.xlsx",
      "sha256": "0f84e1b5bbb912ddcac0d7f430bf7d03571ec1d9a44aff8988f1974c5cd9fa8d",
      "size": 9086
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p7/r17-b6-msp-p7_init.xlsx",
      "sha256": "2d236aab1b430329d7e12b0798f71d1d3068c2d62a9c12065cd55eaca7729c02",
      "size": 9065
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p8/r17-b6-msp-p8_golden.xlsx",
      "sha256": "f31579d341144ec489483350b7d0eaecb9c8a5723bded0ed002701df0414c54e",
      "size": 11216
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-msp-p8/r17-b6-msp-p8_init.xlsx",
      "sha256": "24e3af1d94aa091624ee48e5378043301cd373e68c4e9f971b1f20fbe106ed83",
      "size": 11195
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p0/r17-b6-ska-p0_golden.xlsx",
      "sha256": "4f02f60dea78d406fc63c8901e03d3697fef189e8ee276df115d433c8be37d0a",
      "size": 6311
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p0/r17-b6-ska-p0_init.xlsx",
      "sha256": "7a14e0b6c41f82c509775de11a093247ff6c349eba18e80003dd33b68f4aee83",
      "size": 6293
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p1/r17-b6-ska-p1_golden.xlsx",
      "sha256": "82d698559aded12159e7134a9fd68d7e67e8c4d49abf208cae080f5ef8093fdb",
      "size": 7787
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p1/r17-b6-ska-p1_init.xlsx",
      "sha256": "71896e62e85a6ecdf8f0f9d0eedd0efd4774dc7ceb0532281742808bd6e41470",
      "size": 7768
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p2/r17-b6-ska-p2_golden.xlsx",
      "sha256": "c9468aebeedb933d82b8e5776ce6d2dd40f5cef599e58ac56146e0e3d0d83ec5",
      "size": 9948
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p2/r17-b6-ska-p2_init.xlsx",
      "sha256": "0b3adbe53dd6a5de5fa85e396eb7bfa18647cf2e0aad580a30b1b147604d12a6",
      "size": 9931
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p3/r17-b6-ska-p3_golden.xlsx",
      "sha256": "701bb184b5947f661e4cb130f6c075f91753497bf2d115466255fdbcc0a80418",
      "size": 6469
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p3/r17-b6-ska-p3_init.xlsx",
      "sha256": "1f6937691bfc77caaa748a6f8688421d978c5f7e6dbc8e1ba1ce46ba89aa382d",
      "size": 6440
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p4/r17-b6-ska-p4_golden.xlsx",
      "sha256": "ff89760c0a785a04e585515440badf09101762223684017b9a1ec260c567b740",
      "size": 7958
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p4/r17-b6-ska-p4_init.xlsx",
      "sha256": "ca4771e67b39bb329bac95c3240ed4568fd0f9f4446517fc9ef6e2a2f384217d",
      "size": 7929
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p5/r17-b6-ska-p5_golden.xlsx",
      "sha256": "59efc6e53e1a0e733d62a611ac3b58ba9524f2f716a48f4a779c956cb87a157c",
      "size": 9857
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p5/r17-b6-ska-p5_init.xlsx",
      "sha256": "d1bf2c8b3b76f4061ad170d084810a01f3a8bbe38ee2c98d2a66f0cdae3891d4",
      "size": 9831
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p6/r17-b6-ska-p6_golden.xlsx",
      "sha256": "6775ab7cd3b8023b1056785c958eb71260b3e5576f913d976c2b344ac6dd7869",
      "size": 6659
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p6/r17-b6-ska-p6_init.xlsx",
      "sha256": "af5085f418a9f7e7d3df08b9ad71d184c6f8a90478fcc956ba786811f69f6705",
      "size": 6621
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p7/r17-b6-ska-p7_golden.xlsx",
      "sha256": "4cf9d044e2243a73ff44d66c2e9f00f05c018deb19dc46bf66a20c5f47d14d12",
      "size": 7833
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p7/r17-b6-ska-p7_init.xlsx",
      "sha256": "5321e18b8555d31473be583bc492a1b175b4022d0728b1f2e77c0d57e8f3b3fc",
      "size": 7794
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p8/r17-b6-ska-p8_golden.xlsx",
      "sha256": "27623ce5ef54f6e9eb5bded6e19d7ffb5daf1aace88f254239483b4ed61d81e5",
      "size": 10034
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-ska-p8/r17-b6-ska-p8_init.xlsx",
      "sha256": "065fdccf9ff99058096f76ade93c065381f11596362a6b76c8e1cb7afe94b2b9",
      "size": 9996
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p0/r17-b6-tsr-p0_golden.xlsx",
      "sha256": "9473fb7088cc9772eb8888074ce8134982e81e818ee202a33d078c0939380478",
      "size": 5612
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p0/r17-b6-tsr-p0_init.xlsx",
      "sha256": "cbefedd63c82ff743c7751eff17a6912e0858df762dd3e97b8c40e8d305c1a35",
      "size": 5590
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p1/r17-b6-tsr-p1_golden.xlsx",
      "sha256": "555d6a95db08d0177d1eea8498ee5132ce5068ad2fdfe7abd0023ac3f36288cd",
      "size": 7639
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p1/r17-b6-tsr-p1_init.xlsx",
      "sha256": "9fa80b993e94d000cc078fcfeac2b5cd9eae406cc8199759c0a9e7be1cbed8fa",
      "size": 7617
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p2/r17-b6-tsr-p2_golden.xlsx",
      "sha256": "59011693dc4a267920a47373dd5a8ee8517dba3d4b03420d2f00d7379efa6597",
      "size": 10970
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p2/r17-b6-tsr-p2_init.xlsx",
      "sha256": "29dd09a245002d59d12b8223618d8f1fa9f39111a829749732d399abbb584b69",
      "size": 10947
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p3/r17-b6-tsr-p3_golden.xlsx",
      "sha256": "a64a1410af43efdfbb12a5700a92807ad015219cd5809959160dd3e7635f4d45",
      "size": 6327
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p3/r17-b6-tsr-p3_init.xlsx",
      "sha256": "f3926d410dcdf5ac442e888a82db0117e790e7f48bd7c7fa7f174898c6bb818d",
      "size": 6294
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p4/r17-b6-tsr-p4_golden.xlsx",
      "sha256": "5bc0e549389a3ff6068ab11540397dc2e0785b81d68d562fb37ad26dff71a453",
      "size": 9069
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p4/r17-b6-tsr-p4_init.xlsx",
      "sha256": "b2e785041614777d9b31abeed91caef19d14f1795385a9054bcb9819c1251fed",
      "size": 9038
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p5/r17-b6-tsr-p5_golden.xlsx",
      "sha256": "e1e63fd047fde079102ebe466a9774dcd76f467d3f808ada8e584d7c837035c4",
      "size": 9148
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p5/r17-b6-tsr-p5_init.xlsx",
      "sha256": "f94af9351659655a57985211efe3fbcffb2b595a772234dafe165f69058df14d",
      "size": 9117
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p6/r17-b6-tsr-p6_golden.xlsx",
      "sha256": "2a5983ecc44978a9e13c087d9e93d61f670cdfc94847528dc4a055faf821fbb4",
      "size": 7835
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p6/r17-b6-tsr-p6_init.xlsx",
      "sha256": "795f1b7728b8294d120550db539ebfc4362837e6bcd110b64c185ddb5e1e2304",
      "size": 7799
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p7/r17-b6-tsr-p7_golden.xlsx",
      "sha256": "176eecc2f3030b2d92091d50df8a2009f137ae8a6c730ae19f8d0b56fa4a044e",
      "size": 7106
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p7/r17-b6-tsr-p7_init.xlsx",
      "sha256": "9ef9badc46f2a691b60f1d9e92297f935ef49cbf42d8f28e391312cbf724a6df",
      "size": 7071
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p8/r17-b6-tsr-p8_golden.xlsx",
      "sha256": "73db98f8fc0a899d0a45c27e2c972ce20bb33f03b8a3cbecd7e9d1c32db8eaa6",
      "size": 9898
    },
    {
      "path": "spreadsheetbench_verified_400/spreadsheet/r17-b6-tsr-p8/r17-b6-tsr-p8_init.xlsx",
      "sha256": "ec111572fa3ad432f05ed82cbcae67c58635c1ece2e13dda77de5dffd0352933",
      "size": 9864
    }
  ],
  "l9_profiles": [
    [
      0,
      0,
      0
    ],
    [
      0,
      1,
      1
    ],
    [
      0,
      2,
      2
    ],
    [
      1,
      0,
      1
    ],
    [
      1,
      1,
      2
    ],
    [
      1,
      2,
      0
    ],
    [
      2,
      0,
      2
    ],
    [
      2,
      1,
      0
    ],
    [
      2,
      2,
      1
    ]
  ],
  "metadata_sha256": "12d6eb876e2a230e7990be3e61fed108d45f6ddec00bac5c9b88585a04111b04",
  "schema_version": "1.0",
  "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
  "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2",
  "task_count": 378
}


===== BOUND ARTIFACT: split_manifest | /data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2/r17_split_manifest.json =====
{
  "development": [
    "r17-b0-agj-p4",
    "r17-b0-agj-p6",
    "r17-b0-fmv-p1",
    "r17-b0-fmv-p5",
    "r17-b0-ioc-p3",
    "r17-b0-ioc-p7",
    "r17-b0-msp-p3",
    "r17-b0-msp-p5",
    "r17-b0-ska-p3",
    "r17-b0-ska-p7",
    "r17-b0-tsr-p3",
    "r17-b0-tsr-p7"
  ],
  "e0_calibration": [
    "r17-b1-agj-p0",
    "r17-b1-agj-p1",
    "r17-b1-agj-p2",
    "r17-b1-agj-p3",
    "r17-b1-agj-p4",
    "r17-b1-agj-p5",
    "r17-b1-agj-p6",
    "r17-b1-agj-p7",
    "r17-b1-agj-p8",
    "r17-b1-fmv-p0",
    "r17-b1-fmv-p1",
    "r17-b1-fmv-p2",
    "r17-b1-fmv-p3",
    "r17-b1-fmv-p4",
    "r17-b1-fmv-p5",
    "r17-b1-fmv-p6",
    "r17-b1-fmv-p7",
    "r17-b1-fmv-p8",
    "r17-b1-ioc-p0",
    "r17-b1-ioc-p1",
    "r17-b1-ioc-p2",
    "r17-b1-ioc-p3",
    "r17-b1-ioc-p4",
    "r17-b1-ioc-p5",
    "r17-b1-ioc-p6",
    "r17-b1-ioc-p7",
    "r17-b1-ioc-p8",
    "r17-b1-msp-p0",
    "r17-b1-msp-p1",
    "r17-b1-msp-p2",
    "r17-b1-msp-p3",
    "r17-b1-msp-p4",
    "r17-b1-msp-p5",
    "r17-b1-msp-p6",
    "r17-b1-msp-p7",
    "r17-b1-msp-p8",
    "r17-b1-ska-p0",
    "r17-b1-ska-p1",
    "r17-b1-ska-p2",
    "r17-b1-ska-p3",
    "r17-b1-ska-p4",
    "r17-b1-ska-p5",
    "r17-b1-ska-p6",
    "r17-b1-ska-p7",
    "r17-b1-ska-p8",
    "r17-b1-tsr-p0",
    "r17-b1-tsr-p1",
    "r17-b1-tsr-p2",
    "r17-b1-tsr-p3",
    "r17-b1-tsr-p4",
    "r17-b1-tsr-p5",
    "r17-b1-tsr-p6",
    "r17-b1-tsr-p7",
    "r17-b1-tsr-p8"
  ],
  "e1_common_heldout_probe": [
    "r17-b4-agj-p2",
    "r17-b4-agj-p3",
    "r17-b4-agj-p8",
    "r17-b4-fmv-p1",
    "r17-b4-fmv-p2",
    "r17-b4-fmv-p8",
    "r17-b4-ioc-p1",
    "r17-b4-ioc-p4",
    "r17-b4-ioc-p6",
    "r17-b4-msp-p0",
    "r17-b4-msp-p7",
    "r17-b4-msp-p8",
    "r17-b4-ska-p4",
    "r17-b4-ska-p5",
    "r17-b4-ska-p8",
    "r17-b4-tsr-p0",
    "r17-b4-tsr-p6",
    "r17-b4-tsr-p8"
  ],
  "e1_update_reserve_integrity_only": [
    "r17-b2-agj-p1",
    "r17-b2-fmv-p4",
    "r17-b2-ioc-p4",
    "r17-b2-msp-p0",
    "r17-b2-msp-p3",
    "r17-b2-ska-p2",
    "r17-b2-tsr-p7",
    "r17-b3-agj-p4",
    "r17-b3-fmv-p6",
    "r17-b3-ioc-p2",
    "r17-b3-ska-p4",
    "r17-b3-tsr-p2"
  ],
  "e1_update_streams": {
    "e1-agj-00": [
      "r17-b2-agj-p2",
      "r17-b2-agj-p5",
      "r17-b2-agj-p7",
      "r17-b3-agj-p0",
      "r17-b2-agj-p3",
      "r17-b3-agj-p3",
      "r17-b2-agj-p8",
      "r17-b3-agj-p8"
    ],
    "e1-agj-01": [
      "r17-b2-agj-p0",
      "r17-b3-agj-p6",
      "r17-b3-agj-p2",
      "r17-b3-agj-p5",
      "r17-b2-agj-p6",
      "r17-b3-agj-p7",
      "r17-b3-agj-p1",
      "r17-b2-agj-p4"
    ],
    "e1-fmv-00": [
      "r17-b3-fmv-p4",
      "r17-b2-fmv-p8",
      "r17-b2-fmv-p1",
      "r17-b2-fmv-p0",
      "r17-b3-fmv-p5",
      "r17-b2-fmv-p5",
      "r17-b3-fmv-p7",
      "r17-b2-fmv-p6"
    ],
    "e1-fmv-01": [
      "r17-b3-fmv-p0",
      "r17-b2-fmv-p7",
      "r17-b2-fmv-p2",
      "r17-b3-fmv-p2",
      "r17-b3-fmv-p1",
      "r17-b3-fmv-p8",
      "r17-b3-fmv-p3",
      "r17-b2-fmv-p3"
    ],
    "e1-ioc-00": [
      "r17-b3-ioc-p3",
      "r17-b2-ioc-p2",
      "r17-b2-ioc-p5",
      "r17-b2-ioc-p8",
      "r17-b2-ioc-p0",
      "r17-b3-ioc-p6",
      "r17-b3-ioc-p7",
      "r17-b2-ioc-p3"
    ],
    "e1-ioc-01": [
      "r17-b3-ioc-p0",
      "r17-b3-ioc-p5",
      "r17-b2-ioc-p6",
      "r17-b2-ioc-p7",
      "r17-b3-ioc-p4",
      "r17-b2-ioc-p1",
      "r17-b3-ioc-p1",
      "r17-b3-ioc-p8"
    ],
    "e1-msp-00": [
      "r17-b2-msp-p4",
      "r17-b3-msp-p4",
      "r17-b2-msp-p8",
      "r17-b3-msp-p3",
      "r17-b3-msp-p2",
      "r17-b2-msp-p6",
      "r17-b3-msp-p0",
      "r17-b3-msp-p8"
    ],
    "e1-msp-01": [
      "r17-b3-msp-p5",
      "r17-b2-msp-p1",
      "r17-b3-msp-p1",
      "r17-b2-msp-p2",
      "r17-b2-msp-p7",
      "r17-b3-msp-p7",
      "r17-b2-msp-p5",
      "r17-b3-msp-p6"
    ],
    "e1-ska-00": [
      "r17-b2-ska-p3",
      "r17-b2-ska-p1",
      "r17-b2-ska-p4",
      "r17-b3-ska-p8",
      "r17-b3-ska-p2",
      "r17-b3-ska-p6",
      "r17-b2-ska-p6",
      "r17-b2-ska-p7"
    ],
    "e1-ska-01": [
      "r17-b2-ska-p8",
      "r17-b3-ska-p1",
      "r17-b3-ska-p7",
      "r17-b3-ska-p0",
      "r17-b2-ska-p5",
      "r17-b3-ska-p5",
      "r17-b3-ska-p3",
      "r17-b2-ska-p0"
    ],
    "e1-tsr-00": [
      "r17-b3-tsr-p7",
      "r17-b3-tsr-p0",
      "r17-b2-tsr-p3",
      "r17-b2-tsr-p8",
      "r17-b2-tsr-p2",
      "r17-b2-tsr-p5",
      "r17-b2-tsr-p4",
      "r17-b3-tsr-p8"
    ],
    "e1-tsr-01": [
      "r17-b2-tsr-p0",
      "r17-b2-tsr-p6",
      "r17-b2-tsr-p1",
      "r17-b3-tsr-p3",
      "r17-b3-tsr-p1",
      "r17-b3-tsr-p4",
      "r17-b3-tsr-p6",
      "r17-b3-tsr-p5"
    ]
  },
  "e3_future_reserve_integrity_only": [
    "r17-b5-agj-p8",
    "r17-b5-msp-p3",
    "r17-b5-ska-p7",
    "r17-b5-tsr-p8",
    "r17-b6-agj-p7",
    "r17-b6-fmv-p0",
    "r17-b6-fmv-p7",
    "r17-b6-ioc-p2",
    "r17-b6-ioc-p7",
    "r17-b6-msp-p8",
    "r17-b6-ska-p3",
    "r17-b6-tsr-p3"
  ],
  "e3_future_streams": {
    "e3-agj-00": [
      "r17-b5-agj-p4",
      "r17-b5-agj-p6",
      "r17-b5-agj-p3",
      "r17-b5-agj-p7",
      "r17-b6-agj-p5",
      "r17-b6-agj-p1",
      "r17-b6-agj-p3",
      "r17-b6-agj-p0"
    ],
    "e3-agj-01": [
      "r17-b5-agj-p0",
      "r17-b5-agj-p1",
      "r17-b5-agj-p5",
      "r17-b6-agj-p6",
      "r17-b6-agj-p8",
      "r17-b5-agj-p2",
      "r17-b6-agj-p4",
      "r17-b6-agj-p2"
    ],
    "e3-fmv-00": [
      "r17-b5-fmv-p6",
      "r17-b5-fmv-p3",
      "r17-b5-fmv-p5",
      "r17-b6-fmv-p1",
      "r17-b6-fmv-p5",
      "r17-b5-fmv-p0",
      "r17-b5-fmv-p1",
      "r17-b6-fmv-p6"
    ],
    "e3-fmv-01": [
      "r17-b6-fmv-p3",
      "r17-b5-fmv-p8",
      "r17-b5-fmv-p4",
      "r17-b5-fmv-p2",
      "r17-b6-fmv-p2",
      "r17-b5-fmv-p7",
      "r17-b6-fmv-p8",
      "r17-b6-fmv-p4"
    ],
    "e3-ioc-00": [
      "r17-b5-ioc-p5",
      "r17-b6-ioc-p1",
      "r17-b5-ioc-p3",
      "r17-b6-ioc-p4",
      "r17-b6-ioc-p3",
      "r17-b5-ioc-p0",
      "r17-b6-ioc-p5",
      "r17-b6-ioc-p0"
    ],
    "e3-ioc-01": [
      "r17-b5-ioc-p4",
      "r17-b5-ioc-p2",
      "r17-b5-ioc-p6",
      "r17-b5-ioc-p8",
      "r17-b6-ioc-p8",
      "r17-b5-ioc-p1",
      "r17-b6-ioc-p6",
      "r17-b5-ioc-p7"
    ],
    "e3-msp-00": [
      "r17-b6-msp-p6",
      "r17-b5-msp-p6",
      "r17-b6-msp-p4",
      "r17-b5-msp-p0",
      "r17-b5-msp-p5",
      "r17-b6-msp-p3",
      "r17-b5-msp-p8",
      "r17-b6-msp-p0"
    ],
    "e3-msp-01": [
      "r17-b6-msp-p1",
      "r17-b6-msp-p7",
      "r17-b6-msp-p2",
      "r17-b5-msp-p4",
      "r17-b5-msp-p1",
      "r17-b6-msp-p5",
      "r17-b5-msp-p2",
      "r17-b5-msp-p7"
    ],
    "e3-ska-00": [
      "r17-b5-ska-p2",
      "r17-b6-ska-p8",
      "r17-b5-ska-p8",
      "r17-b6-ska-p7",
      "r17-b5-ska-p5",
      "r17-b6-ska-p5",
      "r17-b5-ska-p6",
      "r17-b6-ska-p4"
    ],
    "e3-ska-01": [
      "r17-b6-ska-p2",
      "r17-b6-ska-p0",
      "r17-b5-ska-p0",
      "r17-b6-ska-p1",
      "r17-b5-ska-p3",
      "r17-b5-ska-p4",
      "r17-b5-ska-p1",
      "r17-b6-ska-p6"
    ],
    "e3-tsr-00": [
      "r17-b5-tsr-p7",
      "r17-b6-tsr-p6",
      "r17-b6-tsr-p4",
      "r17-b5-tsr-p2",
      "r17-b6-tsr-p2",
      "r17-b6-tsr-p1",
      "r17-b5-tsr-p4",
      "r17-b6-tsr-p7"
    ],
    "e3-tsr-01": [
      "r17-b5-tsr-p1",
      "r17-b5-tsr-p5",
      "r17-b6-tsr-p0",
      "r17-b5-tsr-p0",
      "r17-b6-tsr-p5",
      "r17-b6-tsr-p8",
      "r17-b5-tsr-p3",
      "r17-b5-tsr-p6"
    ]
  },
  "rules": {
    "development_never_promoted": true,
    "e1_probe_never_fed_to_updater": true,
    "e1_streams_are_single_family": true,
    "e3_future_unseen_until_prediction_freeze": true,
    "e3_streams_are_single_family": true,
    "reserve_never_replaces_model_failure_or_bad_outcome": true,
    "reserve_only_for_preexecution_file_integrity_failure": true
  },
  "schema_version": "1.0",
  "selection_algorithm": "SHA256(salt|task_id); family-balanced where stated",
  "selection_is_outcome_blind": true,
  "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
}


BOUND DOSSIER END
