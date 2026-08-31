You are an independent protocol reviewer for E2-R17 DeepSeek V2 Repair2. You are a reviewer only, not a scientific backbone. No partial MRW/WIN-C effect or score is supplied or may be inferred. Review the exact bound dossier, not a summary.

Reviewer endpoint: kimi-k3
Exact Repair2 draft SHA-256: 999498499649f873f1f0eff32593d9d2a2c788f843f0484af77cf8868ce89e26

The frozen history is: Repair1 completed 14/48 paired units (28 learned states, 504 heldout units). A later partial MRW state e1-fmv-01/rep2 completed 10/10 provider responses but deterministic SkillEvolver patch application failed with SkillEditError before skill_post/update_completed/heldout; paired WIN-C never started. Provider ambiguity is FALSE, scientific endpoint FALSE, belief update NONE. That state is quarantined.

Audit all eight gates:
A. SELECTION BIAS: The 14 inherited pairs are selected only by pre-outcome completeness/provenance and attempt0-success prefix identity. The treatment-dependent failed pair is not completed or analyzed and Repair2 fresh-runs both arms. Does this avoid unacceptable post-treatment selection/protocol-version bias? If not, return STOP_REPAIR2_INHERITANCE with a P0 blocker.
B. PREFIX COMPATIBILITY: For an attempt0-success state, max_parse_attempts=1 and =2 follow the identical execution path through the endpoint; the extra branch exists only after attempt0 fails. Is inheritance scientifically valid?
C. SYMMETRY: max_parse_attempts=2 and budgets apply identically to WIN-C and MRW, without arm/stream/failure-conditioned allowance.
D. FRESH FAILED PAIR: Repair2 never resumes old MRW; it fresh-runs both WIN-C and MRW for e1-fmv-01/rep2 under the same current identity, pools, initial skill, policy, and time-balanced schedule.
E. MANIFEST: Only the frozen 14-pair compatibility manifest may seed inheritance. Analysis reads a content-addressed valid_replicates manifest that must contain exactly 48 complete paired rows and exactly four per stream. No directory discovery or single-arm row is allowed.
F. RELIABILITY: correction required/success/failure counts are secondary runtime reliability outcomes by arm, cannot filter the primary estimand, and the Repair1 MRW patch-apply failure remains separately reported.
G. BUDGET: nominal updater=10, one explicit correction yields max=11, actor remains <=180 (18 probes x 10 turns), state max=191; claims are visible and fail-closed, provider retry=0, no third attempt.
H. CARDINALITY/SCIENCE: exactly 12 stream D_s, four valid pairs per stream, same treatment/control/pools/initial skill/renderer/updater/verifier/heldout/K=1/8192/statistics/epsilon. GPT/Kimi/Qwen scientific execution and public benchmark remain forbidden.

PASS only if all gates pass and remaining_blockers is exactly []. PASS authorizes only a separately SHA-bound Repair2 contract/authorization after zero-provider preflight. If either inheritance or protocol versioning is unacceptable, STOP_REPAIR2_INHERITANCE; do not recommend silently rerunning or cherry-picking.

Return exactly one JSON object and no markdown using this schema:
{
  "draft_contract_sha256_acknowledged": "",
  "verdict": "PASS_TO_SEPARATELY_AUTHORIZED_REPAIR2|REVISE_REPAIR2|STOP_REPAIR2_INHERITANCE",
  "selection_bias_assessment": "",
  "prefix_compatibility_assessment": "",
  "arm_symmetry_assessment": "",
  "fresh_failed_pair_assessment": "",
  "valid_manifest_assessment": "",
  "runtime_reliability_reporting_assessment": "",
  "provider_budget_assessment": "",
  "scientific_cardinality_assessment": "",
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
  "execution_recommendation": "ALLOW_SEPARATE_REPAIR2_AUTHORIZATION|HOLD|STOP",
  "second_backbone_recommendation": "HOLD",
  "paper_claim_authority": false,
  "single_sentence_verdict": ""
}
Set draft_contract_sha256_acknowledged exactly to the SHA above.

BOUND DOSSIER START

===== BOUND ARTIFACT: repair2_draft | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-deepseek-v2-repair2-draft-contract-20260831.json =====
{
  "actor": {
    "concurrency_per_probe": 1,
    "k": 1,
    "max_output_tokens": 8192,
    "max_turns": 10,
    "provider_retry_limit": 0,
    "requested_model": "deepseek-v4-pro",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "temperature": 0,
    "thinking": "disabled"
  },
  "actor_runtime": {
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt",
    "freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "qualification_path": "generated/e2-r17-runtime-dependency-qualification-r2-20260828.json",
    "qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "required_status": "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2",
    "role": "actor_evaluator",
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv"
  },
  "artifact_type": "e2-r17-deepseek-v2-repair2-continuation-contract",
  "authority": {
    "dual_preexecution_review": false,
    "execute_deepseek_v2": false,
    "gpt_scientific_execution": false,
    "kimi_scientific_execution": false,
    "paper_promotion": false,
    "public_benchmark": false,
    "qwen_scientific_execution": false,
    "repair2_continuation": false,
    "scientific_experiment": false,
    "submission": false
  },
  "bound_code": {
    "actor_runner": {
      "path": "scripts/run_e2_r17_actor_pool.py",
      "sha256": "20a81fbe06f3839cd17babfdb021407368493da61610bca33aae33df8d31ec14"
    },
    "analysis": {
      "path": "scripts/analyze_e2_r17_deepseek_v2_repair2.py",
      "sha256": "9b3c7f0aed465b69a19476138a00882a268b59f47460e8a2abb1bb39dd37eec8"
    },
    "preflight": {
      "path": "scripts/preflight_e2_r17_deepseek_v2_repair2.py",
      "sha256": "d4ff983111f61a802443f456d53d1693375e5d30ed6f90fb6c3a74d6ff89fa13"
    },
    "provider_budget": {
      "path": "research_pipeline/e2_r17_provider_budget.py",
      "sha256": "df819b30a31e62e007e3f85ae76aa8d06faefaa56e9acefe71ceadb9f8fce444"
    },
    "renderer": {
      "path": "research_pipeline/e2_r17_evidence_window_v2.py",
      "sha256": "6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7"
    },
    "repair2_manifest": {
      "path": "research_pipeline/e2_r17_repair2_manifest.py",
      "sha256": "ad358c792136ee247d0d6e0116c850af0cf678e3de88f04474af3e5466c74371"
    },
    "repair2_review": {
      "path": "scripts/run_e2_r17_deepseek_v2_repair2_review.py",
      "sha256": "250f4a5d2bb8cac4f877c37172e154f9201610b008826bb7862a69f89b97ab13"
    },
    "repair2_tests": {
      "path": "research_pipeline/test_e2_r17_deepseek_v2_repair2.py",
      "sha256": "1735ac87979afc83092a0ce0e5851761197a530c53d91fd6c2392c73332cd1b3"
    },
    "runner": {
      "path": "scripts/run_e2_r17_deepseek_v2_repair2_continuation.py",
      "sha256": "63206799b017b159b425053b31617bad010b00b6c8df0bcdf9e40a8e68101a2a"
    },
    "updater_adapter": {
      "path": "research_pipeline/e2_r17_mindmemos_ark_adapter.py",
      "sha256": "b3fb2bfbd98b185a9905d744c41fe6ca5cde1a2b52a0c7554cb8c28e2b48fcc8"
    },
    "updater_wrapper": {
      "path": "research_pipeline/e2_r17_mindmemos_updater.py",
      "sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d"
    }
  },
  "budget": {
    "actor_structural_max_calls_per_state": 180,
    "claim_before_provider_io": true,
    "claims_never_released": true,
    "hard_max_provider_calls_structural": 18336,
    "max_provider_calls_per_state": 191,
    "max_provider_calls_per_unit": 11,
    "planning_note": "V1 call rates are planning references only; hard ceiling is structural and symmetric across arms.",
    "states": 96,
    "updater_correction_max_calls": 11,
    "updater_nominal_calls": 10
  },
  "checkpoint": {
    "ambiguous_partial_provider_unit": "STOP_AND_ADJUDICATE",
    "automatic_relaunch": false,
    "completed_replicates": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-20260831/checkpoints/completed_replicates.jsonl",
    "immediate": true,
    "valid_replicates": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-20260831/checkpoints/valid_replicates.jsonl"
  },
  "compatibility_manifest": {
    "path": "generated/e2-r17-deepseek-v2-repair1-compatibility-manifest-20260831.json",
    "required_status": "PASS_REPAIR1_PREFIX_COMPATIBILITY_14_COMPLETE_PAIRS",
    "sha256": "61e243027e6d42f7923e249f6c88267e6db07ed4bccb32d5a50c8d13bf1695bb"
  },
  "date": "2026-08-31",
  "e1_a_pool_root": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-1-20260828",
  "e1_a_support": {
    "path": "generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json",
    "required_status": "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT",
    "sha256": "b2c611285c20377d77af7ea62448c6fee0d5973cd657687f6dde7f7fce6be6d7"
  },
  "env_file": ".env",
  "forbidden": [
    "GPT execution",
    "GPT/Kimi/Qwen scientific execution",
    "Kimi scientific execution",
    "Qwen scientific execution",
    "Repair1 relaunch or resume",
    "changing verifier",
    "deleting streams/replicates based on score",
    "directory-discovered inheritance",
    "margin widening",
    "operator semantic patch",
    "paper promotion or submission",
    "public benchmark execution",
    "public benchmark execution before DeepSeek V2 GO",
    "result-driven K/task/model changes",
    "score-based inheritance",
    "second scientific backbone",
    "single-arm resume",
    "third parse/apply attempt",
    "using V1 WIN-A/WIN-B as primary control"
  ],
  "freeze_note": "Repair1 freezes the exact previously reviewed DeepSeek V2 science with one executable-schema repair: top-level env_file=.env plus a bound fail-closed preflight. No scientific variable changed.",
  "heldout": {
    "evaluation_k": 1,
    "never_fed_to_updater": true,
    "source_split": "e1_common_heldout_probe",
    "task_ids": [
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
    ]
  },
  "inheritance_policy": {
    "failed_pair": "e1-fmv-01/rep2",
    "failed_pair_action": "fresh-run both WIN-C and MRW",
    "fallback_if_any_reviewer_p0": "STOP_REPAIR2_INHERITANCE; propose but do not execute full-fresh 48-pair Repair2",
    "frozen_candidate_pairs": 14,
    "provider_calls_for_inheritance": 0,
    "score_fields_read": false,
    "selection_basis": "pre-outcome integrity/completeness and attempt0 prefix identity only",
    "single_arm_resume": false
  },
  "initial_skill": {
    "path": "/data/wyt/evidence-substrates/MindMemOS-20260817/resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md",
    "sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb"
  },
  "mindmemos": {
    "bound_files": {
      "src/mindmemos/mindmemos/pipelines/skill/evolution.py": "37bb22da6d4e8485d824c3c31e48f200561b05834a8a6bf3c057b29613b2bca0",
      "src/mindmemos/mindmemos/prompts/EN/skills/skill_patch.py": "48ab68ee3fbb6f115269679358cbcc1f08f9a28318a95438860eae1bbf5a3f4c",
      "src/mindmemos/mindmemos/prompts/EN/skills/trajectory_summary.py": "771a5dc2efc369ed8b4c6d90b5ee470339263780eaf26265be24561b7156b95e"
    },
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817"
  },
  "model_identity": {
    "fresh_max_output_tokens_smoke": 8192,
    "path": "generated/e2-r17-deepseek-v2-repair2-model-identity-adjudication-20260831.json",
    "provider_retry_limit": 0,
    "qualification_path": "generated/e2-r17-deepseek-v2-repair2-deepseek-identity-qualification-20260831.json",
    "qualification_sha256": "6f7305554f710ce56d07e86cbc786ab5d4618327f5b6c0161c7259067cae59ac",
    "required_status": "PASS_CURRENT_REVIEW_TRANCHE",
    "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
    "sha256": "491e4aa738260fab7c6331ee5a1e9a0d57b87df8411a01471c1df0564adf15ee",
    "thinking": "disabled"
  },
  "protocol_memo": {
    "path": "consultations/e2-r17-deepseek-v2-protocol-20260830.md",
    "sha256": "546981b691fda58a700d2b3c5af458eace92391810080d2b531c5ae111cf0300"
  },
  "protocol_v2_correction": {
    "path": "consultations/e2-r17-api-backbone-verifier-design-correction-20260830.md",
    "sha256": "8dc373ad86d09da993a3bc8e34926b267c48ff75d31a4cf4e6772de2a54d493f"
  },
  "protocol_version": "E2-R17-DEEPSEEK-V2-REPAIR2-CONTINUATION-v1",
  "purpose": "Outcome-blind continuation after deterministic updater patch-apply failure, with prefix-compatible inheritance and one explicit symmetric correction generation.",
  "renderer": {
    "arm_metadata_visible": false,
    "exact_final_retokenized_parity_required": true,
    "final_block_cap_tokens": 3072,
    "padding": false,
    "path": "research_pipeline/e2_r17_evidence_window_v2.py",
    "sha256": "6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7",
    "tokenizer_encoding": "cl100k_base",
    "tokenizer_package": "tiktoken",
    "tokenizer_version": "0.11.0"
  },
  "repair1_parent": {
    "authorization_path": "generated/e2-r17-deepseek-v2-replicated-paired-repair1-authorization-20260830.json",
    "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
    "completed_pairs": 14,
    "contract_path": "generated/e2-r17-deepseek-v2-replicated-paired-repair1-contract-20260830.json",
    "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
    "heldout_units": 504,
    "learned_states": 28,
    "scientific_scores_read": false,
    "terminal_state": "STOP_AND_ADJUDICATE_UPDATER_PATCH_APPLY_FAILURE"
  },
  "repair_lineage": {
    "all_scientific_variables_unchanged": true,
    "parent_contract_path": "generated/e2-r17-deepseek-v2-replicated-paired-repair1-contract-20260830.json",
    "parent_contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
    "repair_type": "single-variable explicit parse/apply correction policy"
  },
  "repair_note": "Only max_parse_attempts 1->2 and fail-close structural budgets 10->11, 190->191 change. Failed pair fresh-runs both arms; 14 complete pairs are inherited only if dual review passes.",
  "replication": {
    "approx_90pct_ci_halfwidth_at_null": 0.03605,
    "approx_power_at_delta_1_over_18_alpha_0_05": 0.828,
    "learned_states": 96,
    "nuisance_sd": 0.13905713715032014,
    "paired_replicate_units": 48,
    "replicates_per_stream": 4,
    "sample_size_prior_source": "V1 identical-treatment nuisance SD only",
    "scientific_independent_units": 12,
    "unit_definition": "D_s is the mean of four independent contemporaneous replicate differences within stream s"
  },
  "review_binding": {
    "remaining_p0_p1_blockers_required": [],
    "required_verdict": "PASS_TO_SEPARATELY_AUTHORIZED_REPAIR2",
    "reviewers": [
      "deepseek-v4-pro",
      "kimi-k3"
    ],
    "status": "PENDING_DEEPSEEK_KIMI_2_OF_2"
  },
  "run_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-20260831",
  "runtime_reliability": {
    "cannot_filter_primary_estimand": true,
    "repair1_mrw_patch_apply_failure_count": 1,
    "report_by_arm": [
      "attempt0_success_count",
      "correction_required_count",
      "correction_success_count",
      "correction_failure_count"
    ],
    "secondary_only": true
  },
  "schema_version": "2.0",
  "statistics": {
    "alpha": 0.05,
    "bootstrap": {
      "interval": "95% paired stream bootstrap",
      "reps": 100000,
      "seed": 1718
    },
    "decision_priority": [
      "TOST equivalence -> STOP_MRW_PRACTICALLY_NULL",
      "otherwise positive sign-flip p<=.05 + bootstrap lower>0 -> GO",
      "otherwise significant negative sign-flip -> STOP_MRW_HARMFUL",
      "otherwise HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS"
    ],
    "epsilon": 0.05555555555555555,
    "no_probe_or_replicate_pseudoreplication": true,
    "practical_null": "paired TOST; 90% t-CI strictly inside [-1/18,+1/18]",
    "primary_estimand": "Delta=mean_s D_s over 12 frozen streams",
    "primary_test": "exact one-sided sign-flip over 2^12 stream effects",
    "replicate_effect": "d_sr=J_sr(MRW)-J_sr(WIN-C)",
    "replicates_per_stream": 4,
    "stream_effect": "D_s=mean_r d_sr"
  },
  "status": "DRAFT_PENDING_DUAL_REPAIR2_REVIEW",
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
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2",
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4"
  },
  "superseding_failure_analysis": {
    "path": "generated/e2-r17-deepseek-v2-repair1-updater-patch-apply-failure-20260831.json",
    "sha256": "c21ce2ef3fb4f4573c3f6f45cab8842fbb75dab8d61d256ee3985f24932b38fa"
  },
  "technical_quarantine": {
    "path": "generated/e2-r17-deepseek-v2-repair1-technical-quarantine-20260831.json",
    "required_status": "TECHNICAL_QUARANTINE_UPDATER_PATCH_APPLY_FAILURE",
    "sha256": "1908a3dfc472f835c204f7f9d5a66a9ee4b37093adb09a8d0c0f297b4b1abd7a"
  },
  "test_adjudication": {
    "path": "generated/e2-r17-deepseek-v2-repair2-test-adjudication-20260831.json",
    "required_status": "PASS_REPAIR2_TESTS_9_OF_9",
    "sha256": "ab86fef9695aafc355d7e91a20db9752724cdf646987c2efe73b0b586582920d"
  },
  "time_balance": {
    "contemporaneous_pairing_required": true,
    "evaluation_order": "SHA256(E2-R17-DEEPSEEK-V2-EVAL-PAIR-ORDER-v1|stream|replicate|task|arm)",
    "update_order": "SHA256(E2-R17-DEEPSEEK-V2-UPDATE-ORDER-v1|stream|replicate|arm)"
  },
  "treatment": {
    "arms": [
      "win_c",
      "mrw"
    ],
    "historical_win_a_win_b_excluded_from_primary_estimand": true,
    "mrw": "V3.1 arm-blinded deterministic first failed nonwinner on mixed pools and exact WIN-C evidence on nonmixed pools",
    "same_deterministic_workbook_verifier": true,
    "same_exact_search_pools": true,
    "same_heldout_probes": true,
    "same_initial_skill": true,
    "same_served_winner": true,
    "same_updater_config": true,
    "win_c": "V3.1 arm-blinded matched-window winner evidence"
  },
  "updater": {
    "adapter_path": "research_pipeline/e2_r17_mindmemos_ark_adapter.py",
    "adapter_sha256": "b3fb2bfbd98b185a9905d744c41fe6ca5cde1a2b52a0c7554cb8c28e2b48fcc8",
    "batch_size": 8,
    "correction_policy": "Only after skill_patch_apply attempt0 deterministic parse/apply failure: feed the exact error and complete prior response to the same model; attempt1 is visible, claimed, receipted; failure stops; no attempt2.",
    "first_party": "mindmemos.pipelines.skill.evolution.SkillEvolver",
    "max_correction_attempts": 1,
    "max_parse_attempts": 2,
    "provider_retry_limit": 0,
    "requested_model": "deepseek-v4-pro",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "score_semantics": "selected_evidence_trajectory",
    "temperature": 0.0,
    "thinking": "disabled",
    "transcript_max_chars": 100000,
    "wrapper_path": "research_pipeline/e2_r17_mindmemos_updater.py",
    "wrapper_sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d"
  },
  "updater_runtime": {
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv.freeze.txt",
    "freeze_sha256": "80cd6fdd8eb672e41252c099766fd171a5a7a4b90c284d87da87d09f0d559731",
    "litellm_local_model_cost_map": true,
    "post_lock_compatibility_override": {
      "disclosed": true,
      "package": "tiktoken",
      "reason": "pre-frozen V3.1 ExactMatchedEvidenceBlockRenderer compatibility",
      "version": "0.11.0"
    },
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv/bin/python",
    "qualification_path": "generated/e2-r17-updater-runtime-qualification-20260829.json",
    "qualification_sha256": "f2319815cdcd7caf248c498c470720d4e3f6c9b5e579fad59914df687cdf5b6d",
    "required_entrypoint": "mindmemos.pipelines.skill.evolution.SkillEvolver",
    "required_status": "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_UPDATER_RUNTIME",
    "role": "persistent_skill_updater",
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv"
  },
  "v1_identifiability_hold": {
    "mrw_outcomes_observed_in_v1": false,
    "paired_nuisance_sd": 0.13905713715032014,
    "path": "generated/e2-r17-e1-b-negative-control-adjudication-20260829.json",
    "required_status": "HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY",
    "scientific_role": "preserved V1 scientific-identifiability result and nuisance-SD prior only; never a V2 control arm",
    "sha256": "758d7514518216c6913d623b9175f237a35a63c4f2f523fa24a3097d07515a2e"
  },
  "valid_replicate_manifest": {
    "allowed_sources": [
      "repair1_inherited",
      "repair2_fresh"
    ],
    "directory_discovery_forbidden": true,
    "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-20260831/checkpoints/valid_replicates.jsonl",
    "quarantine_excluded": true,
    "required_per_stream": 4,
    "required_rows": 48
  }
}


===== BOUND ARTIFACT: repair1_contract | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-deepseek-v2-replicated-paired-repair1-contract-20260830.json =====
{
  "actor": {
    "concurrency_per_probe": 1,
    "k": 1,
    "max_output_tokens": 8192,
    "max_turns": 10,
    "provider_retry_limit": 0,
    "requested_model": "deepseek-v4-pro",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "temperature": 0,
    "thinking": "disabled"
  },
  "actor_runtime": {
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt",
    "freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "qualification_path": "generated/e2-r17-runtime-dependency-qualification-r2-20260828.json",
    "qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "required_status": "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2",
    "role": "actor_evaluator",
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv"
  },
  "artifact_type": "e2-r17-deepseek-v2-replicated-paired-contract",
  "authority": {
    "dual_preexecution_review": true,
    "execute_deepseek_v2": false,
    "paper_promotion": false,
    "scientific_experiment": false,
    "submission": false
  },
  "bound_code": {
    "actor_runner": {
      "path": "scripts/run_e2_r17_actor_pool.py",
      "sha256": "20a81fbe06f3839cd17babfdb021407368493da61610bca33aae33df8d31ec14"
    },
    "analysis": {
      "path": "scripts/analyze_e2_r17_deepseek_v2_replicated_paired.py",
      "sha256": "52904ef3e4498cdb133efe4bf590a3bc0db130cf178960d2bf8b9b8277956707"
    },
    "preflight": {
      "path": "scripts/preflight_e2_r17_deepseek_v2.py",
      "sha256": "7455c00bdf00a02390d9f44e42e4231f660770c69c91aaa6d58c0801d612ff82"
    },
    "provider_budget": {
      "path": "research_pipeline/e2_r17_provider_budget.py",
      "sha256": "df819b30a31e62e007e3f85ae76aa8d06faefaa56e9acefe71ceadb9f8fce444"
    },
    "renderer": {
      "path": "research_pipeline/e2_r17_evidence_window_v2.py",
      "sha256": "6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7"
    },
    "runner": {
      "path": "scripts/run_e2_r17_deepseek_v2_replicated_paired_full.py",
      "sha256": "4ea3ecbb44b4143e28c144b1e19df20921dab81451c455b5800085f8b71e6ac3"
    },
    "updater_adapter": {
      "path": "research_pipeline/e2_r17_mindmemos_ark_adapter.py",
      "sha256": "b3fb2bfbd98b185a9905d744c41fe6ca5cde1a2b52a0c7554cb8c28e2b48fcc8"
    },
    "updater_wrapper": {
      "path": "research_pipeline/e2_r17_mindmemos_updater.py",
      "sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d"
    }
  },
  "budget": {
    "claim_before_provider_io": true,
    "claims_never_released": true,
    "hard_max_provider_calls_structural": 18240,
    "max_provider_calls_per_state": 190,
    "max_provider_calls_per_unit": 10,
    "planning_note": "V1 call rates are planning references only; hard ceiling is structural and symmetric across arms.",
    "states": 96
  },
  "checkpoint": {
    "completed_manifest": "checkpoints/completed_replicates.jsonl",
    "exclusive_lock": ".exclusive.lock",
    "partial_ambiguous_unit_auto_rerun": false,
    "persist_each_heldout_probe_immediately": true,
    "persist_each_update_immediately": true,
    "resume_after_sha_revalidation_only": true
  },
  "date": "2026-08-30",
  "e1_a_pool_root": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-1-20260828",
  "e1_a_support": {
    "path": "generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json",
    "required_status": "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT",
    "sha256": "b2c611285c20377d77af7ea62448c6fee0d5973cd657687f6dde7f7fce6be6d7"
  },
  "env_file": ".env",
  "forbidden": [
    "second scientific backbone",
    "GPT execution",
    "Kimi scientific execution",
    "Qwen scientific execution",
    "changing verifier",
    "using V1 WIN-A/WIN-B as primary control",
    "deleting streams/replicates based on score",
    "margin widening",
    "result-driven K/task/model changes",
    "public benchmark execution before DeepSeek V2 GO"
  ],
  "freeze_note": "Repair1 freezes the exact previously reviewed DeepSeek V2 science with one executable-schema repair: top-level env_file=.env plus a bound fail-closed preflight. No scientific variable changed.",
  "heldout": {
    "evaluation_k": 1,
    "never_fed_to_updater": true,
    "source_split": "e1_common_heldout_probe",
    "task_ids": [
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
    ]
  },
  "initial_skill": {
    "path": "/data/wyt/evidence-substrates/MindMemOS-20260817/resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md",
    "sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb"
  },
  "mindmemos": {
    "bound_files": {
      "src/mindmemos/mindmemos/pipelines/skill/evolution.py": "37bb22da6d4e8485d824c3c31e48f200561b05834a8a6bf3c057b29613b2bca0",
      "src/mindmemos/mindmemos/prompts/EN/skills/skill_patch.py": "48ab68ee3fbb6f115269679358cbcc1f08f9a28318a95438860eae1bbf5a3f4c",
      "src/mindmemos/mindmemos/prompts/EN/skills/trajectory_summary.py": "771a5dc2efc369ed8b4c6d90b5ee470339263780eaf26265be24561b7156b95e"
    },
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817"
  },
  "model_identity": {
    "fresh_max_output_tokens_smoke": 8192,
    "path": "generated/e2-r17-deepseek-v2-model-identity-adjudication-20260830.json",
    "qualification_path": "generated/e2-r17-deepseek-v2-model-identity-qualification-20260830.json",
    "qualification_sha256": "718b07875702945b008e68fb1a8dd48670a44a8c17aec433bbb4bca0cebffdd1",
    "required_status": "PASS_CURRENT_REVIEW_TRANCHE",
    "sha256": "15e9e194e4c4e5ff3197f6ab8cbb30423e8e12f647d6a04db36f4c0a7153b53b"
  },
  "protocol_memo": {
    "path": "consultations/e2-r17-deepseek-v2-protocol-20260830.md",
    "sha256": "546981b691fda58a700d2b3c5af458eace92391810080d2b531c5ae111cf0300"
  },
  "protocol_v2_correction": {
    "path": "consultations/e2-r17-api-backbone-verifier-design-correction-20260830.md",
    "sha256": "8dc373ad86d09da993a3bc8e34926b267c48ff75d31a4cf4e6772de2a54d493f"
  },
  "protocol_version": "R17_DEEPSEEK_V2_R4",
  "purpose": "DeepSeek-only replicated contemporaneous exact-same-pool causal test of learning projection under hosted stochasticity, with deterministic SpreadsheetBench workbook verification.",
  "renderer": {
    "arm_metadata_visible": false,
    "exact_final_retokenized_parity_required": true,
    "final_block_cap_tokens": 3072,
    "padding": false,
    "path": "research_pipeline/e2_r17_evidence_window_v2.py",
    "sha256": "6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7",
    "tokenizer_encoding": "cl100k_base",
    "tokenizer_package": "tiktoken",
    "tokenizer_version": "0.11.0"
  },
  "repair_lineage": {
    "blocker_path": "generated/e2-r17-deepseek-v2-execution-blocker-20260830.json",
    "blocker_sha256": "fd84dd43718508151050f5e7c872ebf2dfbd453e8ccfae41b1e30081f986d22a",
    "failure_registry_path": "generated/e2-r17-failure-differential-registry-v10-20260830.json",
    "failure_registry_sha256": "3cda4fae6c0505a9340ced99b7728cfa2ce8d57ba795cf5e7428d671b1413e4e",
    "parent_contract_path": "generated/e2-r17-deepseek-v2-replicated-paired-full-contract-20260830.json",
    "parent_contract_sha256": "54f37f073881fe676064ec738676b1b869d1625b2bdd8fe11980b9abf801f2bc",
    "provider_calls_before_repair": 0,
    "repair_delta": "Add top-level env_file=.env required by the already-frozen runner and bind a preflight that fail-closes on missing/empty/nonexistent env_file. No scientific variable changed.",
    "run_root_created_before_repair": false,
    "scientific_outcomes_before_repair": 0
  },
  "repair_note": "V2 review round1 Kimi P0: corrected final-success status string checked by main(); no scientific outcome existed and no other protocol field changed.",
  "replication": {
    "approx_90pct_ci_halfwidth_at_null": 0.03605,
    "approx_power_at_delta_1_over_18_alpha_0_05": 0.828,
    "learned_states": 96,
    "nuisance_sd": 0.13905713715032014,
    "paired_replicate_units": 48,
    "replicates_per_stream": 4,
    "sample_size_prior_source": "V1 identical-treatment nuisance SD only",
    "scientific_independent_units": 12,
    "unit_definition": "D_s is the mean of four independent contemporaneous replicate differences within stream s"
  },
  "review_binding": {
    "all_allow_separate_deepseek_v2_authorization": true,
    "dual_review_summary_path": "generated/e2-r17-deepseek-v2-protocol-review-20260830-round2/summary.json",
    "dual_review_summary_sha256": "8b2bb35d833791221f825b38502c2f78fdf9f0c59ff32b69e89aa3db4be6bd2e",
    "paper_claim_authority": false,
    "repair_review_status": "PASS",
    "repair_review_summary_path": "generated/e2-r17-deepseek-v2-repair1-review-20260830/summary.json",
    "repair_review_summary_sha256": "75b3d9007aeff0451bc5a53312bb4dfc0edad8b41031c799c6217f33b96de497",
    "repaired_draft_path": "generated/e2-r17-deepseek-v2-replicated-paired-repair1-draft-contract-20260830.json",
    "repaired_draft_sha256": "ad9c4b2f00a7e05db12641d6da418987d468b00c9a5ad97d8d3f05f6fb6bea59",
    "reviewed_draft_path": "generated/e2-r17-deepseek-v2-replicated-paired-draft-contract-20260830.json",
    "reviewed_draft_sha256": "3aa8a3909d41238389dfbdc2f5b00840175038cb34295050803391a03d202ffc",
    "second_backbone_authority": false,
    "verdicts": {
      "deepseek-v4-pro": "PASS_TO_SEPARATELY_AUTHORIZED_DEEPSEEK_V2",
      "kimi-k3": "PASS_TO_SEPARATELY_AUTHORIZED_DEEPSEEK_V2"
    }
  },
  "run_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830",
  "schema_version": "1.0",
  "statistics": {
    "alpha": 0.05,
    "bootstrap": {
      "interval": "95% paired stream bootstrap",
      "reps": 100000,
      "seed": 1718
    },
    "decision_priority": [
      "TOST equivalence -> STOP_MRW_PRACTICALLY_NULL",
      "otherwise positive sign-flip p<=.05 + bootstrap lower>0 -> GO",
      "otherwise significant negative sign-flip -> STOP_MRW_HARMFUL",
      "otherwise HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS"
    ],
    "epsilon": 0.05555555555555555,
    "no_probe_or_replicate_pseudoreplication": true,
    "practical_null": "paired TOST; 90% t-CI strictly inside [-1/18,+1/18]",
    "primary_estimand": "Delta=mean_s D_s over 12 frozen streams",
    "primary_test": "exact one-sided sign-flip over 2^12 stream effects",
    "replicate_effect": "d_sr=J_sr(MRW)-J_sr(WIN-C)",
    "replicates_per_stream": 4,
    "stream_effect": "D_s=mean_r d_sr"
  },
  "status": "FROZEN_E2_R17_DEEPSEEK_V2_REPLICATED_PAIRED_FULL",
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
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2",
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4"
  },
  "time_balance": {
    "contemporaneous_pairing_required": true,
    "evaluation_order": "SHA256(E2-R17-DEEPSEEK-V2-EVAL-PAIR-ORDER-v1|stream|replicate|task|arm)",
    "update_order": "SHA256(E2-R17-DEEPSEEK-V2-UPDATE-ORDER-v1|stream|replicate|arm)"
  },
  "treatment": {
    "arms": [
      "win_c",
      "mrw"
    ],
    "historical_win_a_win_b_excluded_from_primary_estimand": true,
    "mrw": "V3.1 arm-blinded deterministic first failed nonwinner on mixed pools and exact WIN-C evidence on nonmixed pools",
    "same_deterministic_workbook_verifier": true,
    "same_exact_search_pools": true,
    "same_heldout_probes": true,
    "same_initial_skill": true,
    "same_served_winner": true,
    "same_updater_config": true,
    "win_c": "V3.1 arm-blinded matched-window winner evidence"
  },
  "updater": {
    "adapter_path": "research_pipeline/e2_r17_mindmemos_ark_adapter.py",
    "adapter_sha256": "b3fb2bfbd98b185a9905d744c41fe6ca5cde1a2b52a0c7554cb8c28e2b48fcc8",
    "batch_size": 8,
    "first_party": "mindmemos.pipelines.skill.evolution.SkillEvolver",
    "max_parse_attempts": 1,
    "provider_retry_limit": 0,
    "requested_model": "deepseek-v4-pro",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "score_semantics": "selected_evidence_trajectory",
    "temperature": 0.0,
    "thinking": "disabled",
    "transcript_max_chars": 100000,
    "wrapper_path": "research_pipeline/e2_r17_mindmemos_updater.py",
    "wrapper_sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d"
  },
  "updater_runtime": {
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv.freeze.txt",
    "freeze_sha256": "80cd6fdd8eb672e41252c099766fd171a5a7a4b90c284d87da87d09f0d559731",
    "litellm_local_model_cost_map": true,
    "post_lock_compatibility_override": {
      "disclosed": true,
      "package": "tiktoken",
      "reason": "pre-frozen V3.1 ExactMatchedEvidenceBlockRenderer compatibility",
      "version": "0.11.0"
    },
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv/bin/python",
    "qualification_path": "generated/e2-r17-updater-runtime-qualification-20260829.json",
    "qualification_sha256": "f2319815cdcd7caf248c498c470720d4e3f6c9b5e579fad59914df687cdf5b6d",
    "required_entrypoint": "mindmemos.pipelines.skill.evolution.SkillEvolver",
    "required_status": "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_UPDATER_RUNTIME",
    "role": "persistent_skill_updater",
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv"
  },
  "v1_identifiability_hold": {
    "mrw_outcomes_observed_in_v1": false,
    "paired_nuisance_sd": 0.13905713715032014,
    "path": "generated/e2-r17-e1-b-negative-control-adjudication-20260829.json",
    "required_status": "HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY",
    "scientific_role": "preserved V1 scientific-identifiability result and nuisance-SD prior only; never a V2 control arm",
    "sha256": "758d7514518216c6913d623b9175f237a35a63c4f2f523fa24a3097d07515a2e"
  }
}


===== BOUND ARTIFACT: repair1_authorization | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-deepseek-v2-replicated-paired-repair1-authorization-20260830.json =====
{
  "artifact_type": "e2-r17-deepseek-v2-replicated-paired-repair1-authorization",
  "authority": {
    "deepseek_v2": true,
    "e1_b": true,
    "frontend_promotion": false,
    "mrw_causal_comparison": true,
    "paper_promotion": false,
    "scientific_experiment": true,
    "second_backbone": false,
    "submission": false
  },
  "contract_path": "generated/e2-r17-deepseek-v2-replicated-paired-repair1-contract-20260830.json",
  "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
  "date": "2026-08-30",
  "execution_scope": {
    "allow_noninitial_skill": true,
    "allowed_modes": [
      "e1"
    ],
    "allowed_task_ids": [
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
    "env_file": ".env",
    "exact_k": 1,
    "frozen_arms": [
      "win_c",
      "mrw"
    ],
    "frozen_heldout_task_ids": [
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
    "frozen_stream_ids": [
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
    "identity_artifact_sha256": "15e9e194e4c4e5ff3197f6ab8cbb30423e8e12f647d6a04db36f4c0a7153b53b",
    "max_output_tokens": 8192,
    "max_turns": 10,
    "provider_budget": {
      "per_unit_limit": 10,
      "required": true,
      "total_limit": 190
    },
    "replicates_per_stream": 4,
    "required_resolved_model": "deepseek-v4-pro-ga-260813",
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4"
  },
  "interpretation_boundary": "Authorized only for DeepSeek V2 replicated contemporaneous WIN-C vs MRW on the frozen controlled substrate. GPT/Kimi/Qwen scientific execution, public benchmarks, paper promotion and submission remain unauthorized.",
  "mindmemos_commit": "90491828726e1540442b17cd445d0308d0b8093c",
  "private_credentials_included": false,
  "raw_response_ids_included": false,
  "repair_lineage": {
    "execution_blocker_path": "generated/e2-r17-deepseek-v2-execution-blocker-20260830.json",
    "execution_blocker_sha256": "fd84dd43718508151050f5e7c872ebf2dfbd453e8ccfae41b1e30081f986d22a",
    "parent_authorization_path": "generated/e2-r17-deepseek-v2-replicated-paired-full-authorization-20260830.json",
    "parent_authorization_sha256": "fbe5c0ce0b033c0bebc10d5f9b14230c740b838da5dbf33ea676c9f54a809ac4",
    "provider_calls_before_repair": 0,
    "repair_review_summary_sha256": "75b3d9007aeff0451bc5a53312bb4dfc0edad8b41031c799c6217f33b96de497",
    "repaired_contract_draft_sha256": "ad9c4b2f00a7e05db12641d6da418987d468b00c9a5ad97d8d3f05f6fb6bea59",
    "scientific_outcomes_before_repair": 0
  },
  "review_summary_path": "generated/e2-r17-deepseek-v2-repair1-review-20260830/summary.json",
  "review_summary_sha256": "75b3d9007aeff0451bc5a53312bb4dfc0edad8b41031c799c6217f33b96de497",
  "schema_version": "1.0",
  "status": "AUTHORIZED_E1"
}


===== BOUND ARTIFACT: compatibility_manifest | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-deepseek-v2-repair1-compatibility-manifest-20260831.json =====
{
  "artifact_type": "e2-r17-deepseek-v2-repair1-prefix-compatibility-manifest",
  "completed_pair_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/checkpoints/completed_replicates.jsonl",
  "completed_pair_manifest_sha256": "480eb910c17f45a33def8074f1e030388757d4e27159372cf11a675c3867d6c8",
  "created_at_utc": "2026-08-31T03:45:09+00:00",
  "eligibility_rule": "Complete paired unit; both arms nominal attempt0 success; exact receipt/SHA/budget bindings; 18/18 heldout integrity; no parse error.",
  "inherited_heldout_unit_count": 504,
  "inherited_pair_count": 14,
  "inherited_state_count": 28,
  "pairs": [
    {
      "arms": {
        "mrw": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "86b1686d441027fbad48d0203737450fdedebdbac0c6026c9c77b8e10754bf46",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/checkpoints/provider_budget.sqlite3",
            "sha256": "5146ab261b5ddba059f7b7e153a43f690e54643856a675b4b9665bf53b2b591d",
            "total_claimed": 117,
            "unit_claimed": {
              "e1-agj-00/rep0/mrw/update": 10,
              "r17-b4-agj-p2/rollout_0": 7,
              "r17-b4-agj-p3/rollout_0": 7,
              "r17-b4-agj-p8/rollout_0": 4,
              "r17-b4-fmv-p1/rollout_0": 4,
              "r17-b4-fmv-p2/rollout_0": 4,
              "r17-b4-fmv-p8/rollout_0": 5,
              "r17-b4-ioc-p1/rollout_0": 5,
              "r17-b4-ioc-p4/rollout_0": 8,
              "r17-b4-ioc-p6/rollout_0": 7,
              "r17-b4-msp-p0/rollout_0": 3,
              "r17-b4-msp-p7/rollout_0": 10,
              "r17-b4-msp-p8/rollout_0": 9,
              "r17-b4-ska-p4/rollout_0": 7,
              "r17-b4-ska-p5/rollout_0": 4,
              "r17-b4-ska-p8/rollout_0": 5,
              "r17-b4-tsr-p0/rollout_0": 6,
              "r17-b4-tsr-p6/rollout_0": 7,
              "r17-b4-tsr-p8/rollout_0": 5
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "58e348c6e48889c9580aa83101cd6cecf2126157e88f92a062d8e9fd963cbd42",
              "provider_status": "completed",
              "response_sha256": "79a1eeeda16b9ba93af8a9fb0c66fc95e0f2afa05f0eba16964944fbc5068331",
              "sha256": "8218cf86143c9eba66dc7e4906d23f063b5fa843973be3f635d93c97180307a7",
              "task": "skill_trajectory_summary",
              "total_tokens": 3858
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "0684ac92b67a81d6e0a4673db91efbc9a0be2624a3a79beb536ec752d1de3ee1",
              "provider_status": "completed",
              "response_sha256": "2cdb3c3a36bebef9e71635d190be92efbe02651b3fd0e6b484fed4b7fab9b316",
              "sha256": "24fb5296bad74282d293854b6d604f1c81a231ce954b79bc846f8505c5e03ae7",
              "task": "skill_trajectory_summary",
              "total_tokens": 4024
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "30b5b0838400d3038536448b1278d6f2a826331789157412c80022233a99ce9d",
              "provider_status": "completed",
              "response_sha256": "148079391c9e2f86cbc8a6aa8f204ba9e70b3f65fb0993379566579bf4b74a59",
              "sha256": "c4e384a60194f29c2824c746b8f5f4a828bdbd9e4e47ed946e1d1d2a37950406",
              "task": "skill_trajectory_summary",
              "total_tokens": 4069
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c8e09de95c6da653bcbd181fffc13c3a6a6c4d1a32d417709bc7660a47e2012d",
              "provider_status": "completed",
              "response_sha256": "f11148764abe1ddd00d69f5165acdadf396faa66baa7f3c727c054c0d0e9f219",
              "sha256": "d60fe024adc164d44f09bee6a04dcda9d340ab5cbc6114c2af27b9a2b2cc2c33",
              "task": "skill_trajectory_summary",
              "total_tokens": 3933
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "9a7711f7a8b619b9668009c2b3a58093c0aa3565c3825f2983844683eedba1fe",
              "provider_status": "completed",
              "response_sha256": "8ec8a1fc42ec99937de9a25d7004b1f9529bd0a598bb55bc15c3bcdd84887f05",
              "sha256": "5611a55649dc781408a3edf3298f8227efc49e648da360305db03536629e31a2",
              "task": "skill_trajectory_summary",
              "total_tokens": 3895
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "4e81f724402262971d0e4dc22c83de6b712e61a7b3fb9cd86e680cf9bbefe537",
              "provider_status": "completed",
              "response_sha256": "3d5ca039eaa6e9fd0fe7a0a00e9c4f33a6295e6d7b0d33b02d43d7dc4cb661b0",
              "sha256": "87b6976fd5d87a358c36befe3c3232bf36461bfe3738b4769088442137c53b33",
              "task": "skill_trajectory_summary",
              "total_tokens": 1712
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d4100506ddd401ae118d1e16b0f68e07bb23fa5f8f4b3e93c7c337894c6b166a",
              "provider_status": "completed",
              "response_sha256": "1d2ea313df2d2244a484ac3e4dda9d1abba229b68dfadeed88d6afca3cb0b903",
              "sha256": "4c59d8c9f97035e5abc659e8c90cbf1564eaf584c6c77a026d122c27b4baa61e",
              "task": "skill_trajectory_summary",
              "total_tokens": 2167
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c0c923d3c3d5d5a33f20ade124e824a53183fa30e57f72b6bdcb871d5318c20e",
              "provider_status": "completed",
              "response_sha256": "35eb14c77c183b2e198b44fb2b25a138dea733a0aace1d2b3c64ac25601662b6",
              "sha256": "ef001b0fce888cbe82572b14d9db75ae0c98b0eb366e6f142058d17229e440ea",
              "task": "skill_trajectory_summary",
              "total_tokens": 2113
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "3effb4180a364cc0d6881bb408ca5a6bfa4345131df2a211c6de3cf34afb9c15",
              "provider_status": "completed",
              "response_sha256": "42c4abdc7896aa0bc9d6b441e627a3524a5ad12fd8d3d6914f77f8ea71a1a1e4",
              "sha256": "39ea781663cd6641edbd6324c957ecfb084d88dd255538fb409982df61c46b2d",
              "task": "skill_patch_propose",
              "total_tokens": 4677
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "2059c83ce68b220752510fdb7fd8f2787f236dba69b3b817721a5b7c8cbfa644",
              "provider_status": "completed",
              "response_sha256": "10c01a4d05562e9893aa733733e062f152df85b4597525434c6b9e01af6c352c",
              "sha256": "853a0a607f7c6100635f1537f2db136bf96150ec05a197009544986901a7bade",
              "task": "skill_patch_apply",
              "total_tokens": 2146
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 32594,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/update/skill_post/SKILL.md",
          "skill_post_sha256": "21cde8505220d3184ec4de8011a90d38418a77a2033dd6db6208aa2e41e3f168",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "e44fb1545cbcdd743b6f096aee325c76ff2ffc4c21253f8e01b3e1f6b9c3feb9",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/mrw/update/update_receipt.json",
          "update_receipt_sha256": "2e21c7d71b32eaca8dbafb21e513653a346b8d7255f40070571224e734f2c657"
        },
        "win_c": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "5e99dee2fd327fd083a189a17b141a39332fb0ab4422369df989676962a85001",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/checkpoints/provider_budget.sqlite3",
            "sha256": "37b00503785748cb553544c9fa670e083503abce360bb87efb53c38ed5fc010a",
            "total_claimed": 109,
            "unit_claimed": {
              "e1-agj-00/rep0/win_c/update": 10,
              "r17-b4-agj-p2/rollout_0": 5,
              "r17-b4-agj-p3/rollout_0": 6,
              "r17-b4-agj-p8/rollout_0": 6,
              "r17-b4-fmv-p1/rollout_0": 4,
              "r17-b4-fmv-p2/rollout_0": 5,
              "r17-b4-fmv-p8/rollout_0": 4,
              "r17-b4-ioc-p1/rollout_0": 9,
              "r17-b4-ioc-p4/rollout_0": 6,
              "r17-b4-ioc-p6/rollout_0": 6,
              "r17-b4-msp-p0/rollout_0": 3,
              "r17-b4-msp-p7/rollout_0": 7,
              "r17-b4-msp-p8/rollout_0": 8,
              "r17-b4-ska-p4/rollout_0": 3,
              "r17-b4-ska-p5/rollout_0": 7,
              "r17-b4-ska-p8/rollout_0": 3,
              "r17-b4-tsr-p0/rollout_0": 5,
              "r17-b4-tsr-p6/rollout_0": 6,
              "r17-b4-tsr-p8/rollout_0": 6
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "58e348c6e48889c9580aa83101cd6cecf2126157e88f92a062d8e9fd963cbd42",
              "provider_status": "completed",
              "response_sha256": "c9ee9a8ce8fb4c982ebfbd1f70ea8bcf8d4718ab5501daec21e148f711a8339d",
              "sha256": "00ebb5b72167faff2e011502ad6127b23163dbd85800a73a767f0651d05a30dc",
              "task": "skill_trajectory_summary",
              "total_tokens": 3917
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "0684ac92b67a81d6e0a4673db91efbc9a0be2624a3a79beb536ec752d1de3ee1",
              "provider_status": "completed",
              "response_sha256": "f4628a5c5a9d5a916ddaeb6f78eda64ea76ceb18adf6f4228ed4f6b6f63f17ec",
              "sha256": "2ef7080a457f3cf058612dfa7c7c128abd0be8308710d40b85a192345de286d5",
              "task": "skill_trajectory_summary",
              "total_tokens": 3959
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "7cbdb74c510be8affe57688401d15833c39c759374bfd0dbaf31f35eeabdeed7",
              "provider_status": "completed",
              "response_sha256": "4dd4959ff9ace5783a678ac68ec7adb6188e53b0f15529675418761b3a19d7f7",
              "sha256": "562b3a69ab1f40bfc9bacee96e2312f96430240d2e59072fc3882ab8992d20fc",
              "task": "skill_trajectory_summary",
              "total_tokens": 3939
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c8e09de95c6da653bcbd181fffc13c3a6a6c4d1a32d417709bc7660a47e2012d",
              "provider_status": "completed",
              "response_sha256": "0dd6508dbd748a1157b42a2eed15c176d3f70f1a466d2919d096d3851a342a2c",
              "sha256": "fd0f45e07dfee78631deb49ffd64f505f719f64ae96d3f703766589b643e1dd8",
              "task": "skill_trajectory_summary",
              "total_tokens": 3939
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "9a7711f7a8b619b9668009c2b3a58093c0aa3565c3825f2983844683eedba1fe",
              "provider_status": "completed",
              "response_sha256": "e7e0ec8f80f97bfd97ba32edf8d16e1430d0babc66faac64ea3253d7e0ba845b",
              "sha256": "1e17e6f962657070b2706550510963559dbcc946cf6b03dbd00d4a01e7e75654",
              "task": "skill_trajectory_summary",
              "total_tokens": 3917
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "11f9d79e9d20f132d8b3ddddae2155b04d49c6d38398ac4dec60835e97541b55",
              "provider_status": "completed",
              "response_sha256": "5107db990bcf14a3bf7d833f999598f59f3947e0466cbd80c5e0b16d436dc6ec",
              "sha256": "09a0c55404c0e38677c2e9b6844b7cb99fabbb7fb3b286ddb43c62b3eb03a07f",
              "task": "skill_trajectory_summary",
              "total_tokens": 1890
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "f3486e893207b6fe2a708fe244f6d88c5cffca7aa8ad14491a7586df4329d2ef",
              "provider_status": "completed",
              "response_sha256": "15795c9021a0c9a8d3a08f73808c03a4ddd99b3830a278a7f8bca58cf2cfb252",
              "sha256": "3a58cf6b6d1d32e25f1b5272e6104bd02a6b1d2dfdd367a0ad83f452f03f19e2",
              "task": "skill_trajectory_summary",
              "total_tokens": 2124
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "0af39593578d41b10edba5ef0e128edb61f2ad2bc04e1f39bafabb89d4f17f7e",
              "provider_status": "completed",
              "response_sha256": "dca638335045506002b9a6579780081a043fd2d12cbf1fc7372add1be34d1fc0",
              "sha256": "43639b818ca854849a978478bceffc01d0e20d88aac82219af4e50e9ae390a26",
              "task": "skill_trajectory_summary",
              "total_tokens": 1991
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "ffc013374bb383b1a961a99b570f4e40b2f0a045cb7707dbcefe43562be83363",
              "provider_status": "completed",
              "response_sha256": "e90b9aa81199b9cfec1797b00c11ecfa4dc493bababf2c3ea287ffa78eb904e5",
              "sha256": "1003b0b9469dbdfde6b829c23e3e320004042e7480d6044f32c1ff37313ca461",
              "task": "skill_patch_propose",
              "total_tokens": 4248
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "2fb0509cfd265fed6af346732372896bd18b24ef25bebfe45b89bb03bca42e8d",
              "provider_status": "completed",
              "response_sha256": "4b12bf954c0d3306aa4c6dc6aa8b2e43fee3d13445c42f74d340ea4cb29bf349",
              "sha256": "665b6b85cbb651e3b13767f019c7268f70a26dd47e26bc33e59fc992ae20fe8e",
              "task": "skill_patch_apply",
              "total_tokens": 1514
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 31438,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/update/skill_post/SKILL.md",
          "skill_post_sha256": "6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "1737dbf47d3adff5cd537873530828182c548a7577119b1ca50a29a3611728a2",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_0/win_c/update/update_receipt.json",
          "update_receipt_sha256": "363edd7f0bfb9d6f47bb608f4ad867fb5e23a69d2a28f1b6481e7128b8330e90"
        }
      },
      "evidence_windows_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/evidence_windows.json",
      "evidence_windows_sha256": "e5509065e0ec23b9045f1b67ee2b55df1fe23004a420f7b7a28a3c759af3a24b",
      "pair_summary_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/summary/replicates/e1-agj-00-rep0.json",
      "pair_summary_sha256": "e0eca4f68e2f651bc53bc77949b7898c9aeb44f622eccbfd341a483b56824b9e",
      "prefix_compatibility": "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL",
      "replicate_id": 0,
      "source": "inherited_repair1",
      "stream_id": "e1-agj-00",
      "unit_id": "e1-agj-00/rep0"
    },
    {
      "arms": {
        "mrw": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "5b080491e4a70ead3fc1c422038f786b775ee67fe8f84eba6d93ef0813bbc5c8",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/checkpoints/provider_budget.sqlite3",
            "sha256": "627b32c1059c4d78a0089da8bd8752041a7c0212459cf11db4898cf3d4993c10",
            "total_claimed": 116,
            "unit_claimed": {
              "e1-agj-00/rep1/mrw/update": 10,
              "r17-b4-agj-p2/rollout_0": 5,
              "r17-b4-agj-p3/rollout_0": 5,
              "r17-b4-agj-p8/rollout_0": 7,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 5,
              "r17-b4-fmv-p8/rollout_0": 6,
              "r17-b4-ioc-p1/rollout_0": 3,
              "r17-b4-ioc-p4/rollout_0": 5,
              "r17-b4-ioc-p6/rollout_0": 10,
              "r17-b4-msp-p0/rollout_0": 8,
              "r17-b4-msp-p7/rollout_0": 10,
              "r17-b4-msp-p8/rollout_0": 5,
              "r17-b4-ska-p4/rollout_0": 5,
              "r17-b4-ska-p5/rollout_0": 5,
              "r17-b4-ska-p8/rollout_0": 7,
              "r17-b4-tsr-p0/rollout_0": 7,
              "r17-b4-tsr-p6/rollout_0": 5,
              "r17-b4-tsr-p8/rollout_0": 3
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "58e348c6e48889c9580aa83101cd6cecf2126157e88f92a062d8e9fd963cbd42",
              "provider_status": "completed",
              "response_sha256": "2df352f412849d901d4ee7c3ab4e4d1ed5ba7e11b0e25600325cfc93816e333a",
              "sha256": "950ec4c6b90cd26d9ae408b6eed266d6cf21f8fdf4df07f2275a123f285ad885",
              "task": "skill_trajectory_summary",
              "total_tokens": 3896
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "0684ac92b67a81d6e0a4673db91efbc9a0be2624a3a79beb536ec752d1de3ee1",
              "provider_status": "completed",
              "response_sha256": "634b7eca79c4cefe1f8b2b45e656d19c91bbadbfe63cfa50ff6e16ec330c8014",
              "sha256": "7287262be5b3ba51ad599afb71f1d9208e6dea5983c2a5ea2285e89fc8f4389b",
              "task": "skill_trajectory_summary",
              "total_tokens": 4042
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "30b5b0838400d3038536448b1278d6f2a826331789157412c80022233a99ce9d",
              "provider_status": "completed",
              "response_sha256": "6133cdf6f367d78471332b279376281267f49cd4f687342724155ea01495bfde",
              "sha256": "4b8fffb2db3a054a1526206333c5f1943d1bac694d04777046eb210018e45a07",
              "task": "skill_trajectory_summary",
              "total_tokens": 4020
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c8e09de95c6da653bcbd181fffc13c3a6a6c4d1a32d417709bc7660a47e2012d",
              "provider_status": "completed",
              "response_sha256": "119c3df7c3ff5c58712e044708f4d63812600512cc1d8b20b3d0efdde1833101",
              "sha256": "0f967e056bb7e004e906b0f1bbaf90bb376615b27bfd75c786f4f9e74feb6100",
              "task": "skill_trajectory_summary",
              "total_tokens": 3926
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "9a7711f7a8b619b9668009c2b3a58093c0aa3565c3825f2983844683eedba1fe",
              "provider_status": "completed",
              "response_sha256": "7aa1f1418264a4efad80936987c5c8a9ab7e70fa03eb78dbd913bee95b620d2e",
              "sha256": "ad73612b97838b5d6147540f2b4ca4487840be3c916d858b0e7bdfe1b77b04f5",
              "task": "skill_trajectory_summary",
              "total_tokens": 3921
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "4e81f724402262971d0e4dc22c83de6b712e61a7b3fb9cd86e680cf9bbefe537",
              "provider_status": "completed",
              "response_sha256": "eb0dcfca9d01aaed39f6794d94a7665efee2e65601bcc0d9df6791f58f0085ed",
              "sha256": "42165865a664a6eafe03364e2d6a5ca0171918a4665f1939dcd7b10e100b8acf",
              "task": "skill_trajectory_summary",
              "total_tokens": 1833
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d4100506ddd401ae118d1e16b0f68e07bb23fa5f8f4b3e93c7c337894c6b166a",
              "provider_status": "completed",
              "response_sha256": "d7053b90b3b1957514bcbed3306cde7b794a0ab9bd6ad074154d4d222c977dff",
              "sha256": "ab50d90328225904333f376ad6f1474ff6d6a5ab06ec94d1b140453797cf12db",
              "task": "skill_trajectory_summary",
              "total_tokens": 2201
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c0c923d3c3d5d5a33f20ade124e824a53183fa30e57f72b6bdcb871d5318c20e",
              "provider_status": "completed",
              "response_sha256": "48deb6e22f2a166ab407db0c1446465109b9589b4a01d3202934f236acc35af6",
              "sha256": "1644163f7772e375cbadafb56949257aa15e628d1dde1fb13d095e1ebf148fd7",
              "task": "skill_trajectory_summary",
              "total_tokens": 2082
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "f2af166e5f85cf31db83ff3b94ef3ccc35c990ad11aed2a8ced18a8571766e52",
              "provider_status": "completed",
              "response_sha256": "12e898afd0a006cd5e04aaad60b088b367e8bf18b09910fe532eda961f8f8782",
              "sha256": "74cd8af5c201274d04849341fcec184ae3916ce5bf0b66dbadab683a890cb86a",
              "task": "skill_patch_propose",
              "total_tokens": 4957
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "d75ecdef5ec8f12465cdc71f8a5030a7c8c33887e8c8770cd25aeae0be7ca94d",
              "provider_status": "completed",
              "response_sha256": "275e2eccfcc5766e9dfbf9566e637f9d7ceeae0b036babc3459ff4a48dff8b8f",
              "sha256": "7ad098318ad74dccdf5930fb7dc7b4e60996d10711b42fe2a52a89190b3000d1",
              "task": "skill_patch_apply",
              "total_tokens": 2332
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 33210,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/update/skill_post/SKILL.md",
          "skill_post_sha256": "2ba32f8574584505ea0fdadb1e2ce2bf519cf1597d65af33ffa40e35fed8b224",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "80804a90c0a004ab83cfcd7ed0c1a0d1e4d6a961b1833ef80fe616bb13581773",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/mrw/update/update_receipt.json",
          "update_receipt_sha256": "c1f74c0152e340e458deed973033b2500a390c79a1e889c4c564aa206fd9eae7"
        },
        "win_c": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "72ce3cd5fbaa693c9364bfdbd83fc31fda7087a416e91bcc1c03f257f0a0bad0",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/checkpoints/provider_budget.sqlite3",
            "sha256": "28f8f851988b38dcc512327a07055e92aafbfbbe24d3744f5a690660bdb7a384",
            "total_claimed": 120,
            "unit_claimed": {
              "e1-agj-00/rep1/win_c/update": 10,
              "r17-b4-agj-p2/rollout_0": 6,
              "r17-b4-agj-p3/rollout_0": 5,
              "r17-b4-agj-p8/rollout_0": 3,
              "r17-b4-fmv-p1/rollout_0": 7,
              "r17-b4-fmv-p2/rollout_0": 4,
              "r17-b4-fmv-p8/rollout_0": 4,
              "r17-b4-ioc-p1/rollout_0": 3,
              "r17-b4-ioc-p4/rollout_0": 7,
              "r17-b4-ioc-p6/rollout_0": 6,
              "r17-b4-msp-p0/rollout_0": 6,
              "r17-b4-msp-p7/rollout_0": 10,
              "r17-b4-msp-p8/rollout_0": 10,
              "r17-b4-ska-p4/rollout_0": 7,
              "r17-b4-ska-p5/rollout_0": 5,
              "r17-b4-ska-p8/rollout_0": 7,
              "r17-b4-tsr-p0/rollout_0": 6,
              "r17-b4-tsr-p6/rollout_0": 7,
              "r17-b4-tsr-p8/rollout_0": 7
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "58e348c6e48889c9580aa83101cd6cecf2126157e88f92a062d8e9fd963cbd42",
              "provider_status": "completed",
              "response_sha256": "6a5c30d86c86422574ac621b96913dab2bdf393a885b2542d00b36fd36810a55",
              "sha256": "df07b0009c7fb8e4a47fc886fbb0547ef81ce51d370efbd439cf5113686e8763",
              "task": "skill_trajectory_summary",
              "total_tokens": 3889
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "0684ac92b67a81d6e0a4673db91efbc9a0be2624a3a79beb536ec752d1de3ee1",
              "provider_status": "completed",
              "response_sha256": "5ac81605ca8472bd63dbda2b1d1623a639af3cc4a90ba98582551852df7f28b6",
              "sha256": "627d8b2221eb43aabb015ee5a9d4b57d15e718ae5357400b03254896413af533",
              "task": "skill_trajectory_summary",
              "total_tokens": 3983
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "7cbdb74c510be8affe57688401d15833c39c759374bfd0dbaf31f35eeabdeed7",
              "provider_status": "completed",
              "response_sha256": "f0bcc11e052f410ade71ccad6af36409cc810d0c5ee6d2443deae240ace3215c",
              "sha256": "efa667b972770ccd4b0bdb231734aa1400507c2f6ce90ad5c45f48f1fd747437",
              "task": "skill_trajectory_summary",
              "total_tokens": 3997
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c8e09de95c6da653bcbd181fffc13c3a6a6c4d1a32d417709bc7660a47e2012d",
              "provider_status": "completed",
              "response_sha256": "1eb178ae9a079b5008701cf03863c9509d44453172040a78baeeab0a0c2c220a",
              "sha256": "5f14210dcd851adcbba6870f74352e0b6ef854371fcb78d5d603b6d72fea5b36",
              "task": "skill_trajectory_summary",
              "total_tokens": 3964
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "9a7711f7a8b619b9668009c2b3a58093c0aa3565c3825f2983844683eedba1fe",
              "provider_status": "completed",
              "response_sha256": "89a2f6607005a9f8d797cfc2dca84179f9c3a23a4b5ea9e28cb21a278c0db47b",
              "sha256": "f5445cf5b53b7477a3284184cd39bbb92681871a37eb7d60810796aa0602ec92",
              "task": "skill_trajectory_summary",
              "total_tokens": 3955
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "11f9d79e9d20f132d8b3ddddae2155b04d49c6d38398ac4dec60835e97541b55",
              "provider_status": "completed",
              "response_sha256": "54f63179629c83d5b7fa01e37c514fce9f3971e6d52a2ad66abd0def826704dd",
              "sha256": "467e653ca7819c01bd3e4728fe189a449294911f88986df009777a7ba4a4aa97",
              "task": "skill_trajectory_summary",
              "total_tokens": 1872
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "f3486e893207b6fe2a708fe244f6d88c5cffca7aa8ad14491a7586df4329d2ef",
              "provider_status": "completed",
              "response_sha256": "6d4bd9660b87f80981d7821dc7b03c5758d692e22e7f8a41d8299c88bc469b22",
              "sha256": "8b7b2b7ae6d4f71f3ad59f54216d56e1b8643d4acdc9fd3c85738a0c5831e4bb",
              "task": "skill_trajectory_summary",
              "total_tokens": 2062
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "0af39593578d41b10edba5ef0e128edb61f2ad2bc04e1f39bafabb89d4f17f7e",
              "provider_status": "completed",
              "response_sha256": "54b98dfbc2ae77fae237efd359cead9f4a82e6f9297d2c115558663a4cad0001",
              "sha256": "c7c69224e5bddb7092d98fcc38af57fa509b13e86295f4eb05613fb28dd4a7fb",
              "task": "skill_trajectory_summary",
              "total_tokens": 2051
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "74b2e372f981153365ba1a31c1f01b1e2341c28a71047325aa016b444e462e49",
              "provider_status": "completed",
              "response_sha256": "c43e35cdcbce763a233adef8a85ec6e91d2db82632845b97bbc9e5c089f535d9",
              "sha256": "3e9e65cce0046977ebd2d3af30bb170622891711a4309afda47024be49a75ce8",
              "task": "skill_patch_propose",
              "total_tokens": 4263
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "e57559c424c48ebb56a250a8550edb8930462e1b35e6238cfd5c4b11aa501dfc",
              "provider_status": "completed",
              "response_sha256": "4b12bf954c0d3306aa4c6dc6aa8b2e43fee3d13445c42f74d340ea4cb29bf349",
              "sha256": "70552b4659d5ad5078f419ef9a3f90a1ae0e65a6007788f0dc32003d8d1c6055",
              "task": "skill_patch_apply",
              "total_tokens": 1432
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 31468,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/update/skill_post/SKILL.md",
          "skill_post_sha256": "6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "a75153e6e49c2b0537898a54a1baa8ad5433e15e08c78c412870ad4c72522909",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_1/win_c/update/update_receipt.json",
          "update_receipt_sha256": "6483bf1cd49e274dda0ae03092ae5bdfba791fe709cec66c6397acfe1db70e01"
        }
      },
      "evidence_windows_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/evidence_windows.json",
      "evidence_windows_sha256": "e5509065e0ec23b9045f1b67ee2b55df1fe23004a420f7b7a28a3c759af3a24b",
      "pair_summary_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/summary/replicates/e1-agj-00-rep1.json",
      "pair_summary_sha256": "ad90ec23d84310c3daffae4848a8ac6f448fcc2970ea598fb560fcfe4d29dd85",
      "prefix_compatibility": "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL",
      "replicate_id": 1,
      "source": "inherited_repair1",
      "stream_id": "e1-agj-00",
      "unit_id": "e1-agj-00/rep1"
    },
    {
      "arms": {
        "mrw": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "a769e2809aa6196b3e21688c569ce71b028c112cc587d258dabe5089fd8a3818",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/checkpoints/provider_budget.sqlite3",
            "sha256": "726a42a2fd15d796a8661b67e32ba81ba51837c2a17fe3d15a730f2756b948ea",
            "total_claimed": 114,
            "unit_claimed": {
              "e1-agj-00/rep2/mrw/update": 10,
              "r17-b4-agj-p2/rollout_0": 5,
              "r17-b4-agj-p3/rollout_0": 5,
              "r17-b4-agj-p8/rollout_0": 6,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 5,
              "r17-b4-fmv-p8/rollout_0": 3,
              "r17-b4-ioc-p1/rollout_0": 8,
              "r17-b4-ioc-p4/rollout_0": 7,
              "r17-b4-ioc-p6/rollout_0": 7,
              "r17-b4-msp-p0/rollout_0": 3,
              "r17-b4-msp-p7/rollout_0": 9,
              "r17-b4-msp-p8/rollout_0": 7,
              "r17-b4-ska-p4/rollout_0": 7,
              "r17-b4-ska-p5/rollout_0": 3,
              "r17-b4-ska-p8/rollout_0": 6,
              "r17-b4-tsr-p0/rollout_0": 6,
              "r17-b4-tsr-p6/rollout_0": 6,
              "r17-b4-tsr-p8/rollout_0": 6
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "58e348c6e48889c9580aa83101cd6cecf2126157e88f92a062d8e9fd963cbd42",
              "provider_status": "completed",
              "response_sha256": "8d985044c223e04b2f04b7c6c0f975ac5779242f0e3fc2f7479d6fa8d49a8cf6",
              "sha256": "5014f052d61a1111867457f2643bc9f28ad3e5d64e2e604a99079e5b94f53afb",
              "task": "skill_trajectory_summary",
              "total_tokens": 3906
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "0684ac92b67a81d6e0a4673db91efbc9a0be2624a3a79beb536ec752d1de3ee1",
              "provider_status": "completed",
              "response_sha256": "25ab09cb3ab8d5173cc1b798e9767ce07fa03667a0b154d0e5c57f5e03827422",
              "sha256": "6147cdbb4712e1a844b4f39492ac7fa85d34e74f64bb6e201132d011a87073a5",
              "task": "skill_trajectory_summary",
              "total_tokens": 3924
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "30b5b0838400d3038536448b1278d6f2a826331789157412c80022233a99ce9d",
              "provider_status": "completed",
              "response_sha256": "bec3fd6e83dd56011094da41b5054c5b0b05a4bb3a2281f91911c6c8f912c94d",
              "sha256": "fd59215f5488d0a5c9a8223ad4df976a4949dfd94bc85d5206ca9bc27b3a2388",
              "task": "skill_trajectory_summary",
              "total_tokens": 3930
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c8e09de95c6da653bcbd181fffc13c3a6a6c4d1a32d417709bc7660a47e2012d",
              "provider_status": "completed",
              "response_sha256": "4cbc09b2eac790c8d511e3277402946083d76e3db67d5d430c4ff84964037f11",
              "sha256": "24b5c93ca9e9544e1978e147cbd0e34acb112632ddf55f26153195f4b22dabbc",
              "task": "skill_trajectory_summary",
              "total_tokens": 3903
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "9a7711f7a8b619b9668009c2b3a58093c0aa3565c3825f2983844683eedba1fe",
              "provider_status": "completed",
              "response_sha256": "eeacec4d9ccc4f9b4e4011ea9874c511446d117976660e58872fdf4a770751eb",
              "sha256": "a457fc7d4ff5381c9f0a51328316e8df77aa6bd4b6432d184d9fe2bc46120e77",
              "task": "skill_trajectory_summary",
              "total_tokens": 3911
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "4e81f724402262971d0e4dc22c83de6b712e61a7b3fb9cd86e680cf9bbefe537",
              "provider_status": "completed",
              "response_sha256": "26f3d27a427999a590f0aa2db2047d486468d4c09eab0089a0c8941ba4bb309c",
              "sha256": "095f8b8f09fe25bdca2c4fdf459062d6c3b5b7be5b216ec9ee3fa7d718361c20",
              "task": "skill_trajectory_summary",
              "total_tokens": 1731
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d4100506ddd401ae118d1e16b0f68e07bb23fa5f8f4b3e93c7c337894c6b166a",
              "provider_status": "completed",
              "response_sha256": "4bd3ee7db0ab3f7885bbe01867bc2b4de085c184a0ec4c5b675d0056fdebabc9",
              "sha256": "6980d05f7b7f4430544fff62dcae48e408d0d1c73ef2935137431e8975f6ece0",
              "task": "skill_trajectory_summary",
              "total_tokens": 2076
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c0c923d3c3d5d5a33f20ade124e824a53183fa30e57f72b6bdcb871d5318c20e",
              "provider_status": "completed",
              "response_sha256": "604455ec03f2a82eb3798487f332cd1da6f2e0cb7a8622df05cfbf3d3980caa1",
              "sha256": "addfe6edbac46b567057a07c9e34bedf3d947a6c776ec70c59d6141a495daed4",
              "task": "skill_trajectory_summary",
              "total_tokens": 2073
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "3fb62f126e985801fc8d84cc471b0f7c13a4ad68fc17279f223ddd5a20ad21d3",
              "provider_status": "completed",
              "response_sha256": "cce5b8210f0da848b5480fce9acf2c4acaffefa8c4ed507e89466ecc794e7eb1",
              "sha256": "bd08261916d6d7e26851d7fb508e476ecb84dd88365a780c941e37c884a44e03",
              "task": "skill_patch_propose",
              "total_tokens": 4388
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "f459d4ec709a60a5df23af7c9e938315d9d94bbeca7edb00d23d84abf992a2ae",
              "provider_status": "completed",
              "response_sha256": "540f691f03523a33ecdb4c60b3f535d60930ec2b9cc205b309330726af6dcd08",
              "sha256": "559ffb70ff83d37e488b2c71f8d26d91699e329a113d5a6955138eb779f98f11",
              "task": "skill_patch_apply",
              "total_tokens": 2160
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 32002,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/update/skill_post/SKILL.md",
          "skill_post_sha256": "e248285aec62fdf8941cdc1bdc76ac00178774867b17bda1df2dd6af5c28e96a",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "2d6fe60fad148ff06430a202f7368b5f8538896c7c1f0559ce94cea81005d02d",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/mrw/update/update_receipt.json",
          "update_receipt_sha256": "ca9ce2c2317f21fea21ae55fbdad90c7f0a21c11ea0fdc25f0b0c43fee456638"
        },
        "win_c": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "c4d5d7cacd44615678b4f3a8f9bae58f18456d30c47e0db3b3f9f6469a00ec11",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/checkpoints/provider_budget.sqlite3",
            "sha256": "32552f85d9dec0cbbeaa49a1faabca55d26e8cbb804feec5dd95a01e04c56cb9",
            "total_claimed": 118,
            "unit_claimed": {
              "e1-agj-00/rep2/win_c/update": 10,
              "r17-b4-agj-p2/rollout_0": 7,
              "r17-b4-agj-p3/rollout_0": 6,
              "r17-b4-agj-p8/rollout_0": 6,
              "r17-b4-fmv-p1/rollout_0": 4,
              "r17-b4-fmv-p2/rollout_0": 7,
              "r17-b4-fmv-p8/rollout_0": 5,
              "r17-b4-ioc-p1/rollout_0": 3,
              "r17-b4-ioc-p4/rollout_0": 4,
              "r17-b4-ioc-p6/rollout_0": 3,
              "r17-b4-msp-p0/rollout_0": 6,
              "r17-b4-msp-p7/rollout_0": 7,
              "r17-b4-msp-p8/rollout_0": 10,
              "r17-b4-ska-p4/rollout_0": 6,
              "r17-b4-ska-p5/rollout_0": 6,
              "r17-b4-ska-p8/rollout_0": 9,
              "r17-b4-tsr-p0/rollout_0": 5,
              "r17-b4-tsr-p6/rollout_0": 6,
              "r17-b4-tsr-p8/rollout_0": 8
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "58e348c6e48889c9580aa83101cd6cecf2126157e88f92a062d8e9fd963cbd42",
              "provider_status": "completed",
              "response_sha256": "a378c86272a66a581a322486c90e253e0fdb90c5ce5b86cc808cee882255933f",
              "sha256": "cb4294eb28f84abe10af94c6a10caf220a983de631a4fb2e643ba125b41cd074",
              "task": "skill_trajectory_summary",
              "total_tokens": 3893
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "0684ac92b67a81d6e0a4673db91efbc9a0be2624a3a79beb536ec752d1de3ee1",
              "provider_status": "completed",
              "response_sha256": "5ff3a6722b0568b6ff008c592aa7d78d4cf08c292d4e3133aad67dc3c3aaac3a",
              "sha256": "eedd4eb6281300bfd9c41629a705cb25d909a17be63c6ec69bb80619c38a1c09",
              "task": "skill_trajectory_summary",
              "total_tokens": 3943
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "7cbdb74c510be8affe57688401d15833c39c759374bfd0dbaf31f35eeabdeed7",
              "provider_status": "completed",
              "response_sha256": "1ebdda4b249714aae38d9393d96810d224985fd4c5add230743f8ea8db22bd20",
              "sha256": "aa52413926a0de6c8499befd716c5c996518e92db46c3203e434a05d77cb4754",
              "task": "skill_trajectory_summary",
              "total_tokens": 3922
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c8e09de95c6da653bcbd181fffc13c3a6a6c4d1a32d417709bc7660a47e2012d",
              "provider_status": "completed",
              "response_sha256": "c2ff45b878244d910d40c2b6df304a8027ca47a81bfc9e73f2d91403b12d9b7c",
              "sha256": "b0d248de6b0fd483c984ced98e124c7577780ca5d0678931ace1c0586a6b21fd",
              "task": "skill_trajectory_summary",
              "total_tokens": 4018
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "9a7711f7a8b619b9668009c2b3a58093c0aa3565c3825f2983844683eedba1fe",
              "provider_status": "completed",
              "response_sha256": "5d6a4efdf3b6e2e72ab3d235d54089d8dff70d968744be826f1927940b9adb9e",
              "sha256": "b313668f3c6d8fe249b571a8b6bcb0ac243dff43428d64c557bce20f9b227a7c",
              "task": "skill_trajectory_summary",
              "total_tokens": 3866
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "11f9d79e9d20f132d8b3ddddae2155b04d49c6d38398ac4dec60835e97541b55",
              "provider_status": "completed",
              "response_sha256": "eab80a158de512900b51af6931fd8ac3a9a6ca0666f5350598839037e32c74a3",
              "sha256": "2e66d1ab3b404ac1aa56951e46726e09332a0646abd7004afd365bb930e04240",
              "task": "skill_trajectory_summary",
              "total_tokens": 1874
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "f3486e893207b6fe2a708fe244f6d88c5cffca7aa8ad14491a7586df4329d2ef",
              "provider_status": "completed",
              "response_sha256": "14e9c9909e1f5329f7447ca3b2f1738e8be3cacde440fb3c0108fc9beece1de5",
              "sha256": "fa4c00d0a3f6ac6ecf37eb686cabb2bd5720ca5fdc068b1211685fba7bba9119",
              "task": "skill_trajectory_summary",
              "total_tokens": 2023
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "0af39593578d41b10edba5ef0e128edb61f2ad2bc04e1f39bafabb89d4f17f7e",
              "provider_status": "completed",
              "response_sha256": "542f24071f9b5569af420c6505549918d58572e7d24cc8b54fe911cecca41f04",
              "sha256": "cea88dcbad3d16acf1a458913b9da99133361126c707b5fb6b535e920a69c8a5",
              "task": "skill_trajectory_summary",
              "total_tokens": 2048
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "37ac225f482a3eba0adfcf8317a8c027e2703e5d9b98447558d6c01a28445c9e",
              "provider_status": "completed",
              "response_sha256": "0a56ec112cbfe3645eb10a3327c236b260e98f7de74f35fa76bc152205e999f5",
              "sha256": "3a5adbcc1054a7308393d26349106feb9ac8dec8d21d0110db05703e1ed749aa",
              "task": "skill_patch_propose",
              "total_tokens": 4124
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "bdf0ac5229bb0b50f0481baae25254b7f895ad7b885d879258a564b6a6f17f6d",
              "provider_status": "completed",
              "response_sha256": "4b12bf954c0d3306aa4c6dc6aa8b2e43fee3d13445c42f74d340ea4cb29bf349",
              "sha256": "46097fa168e184dd1efc25b9c29f6c0a3b30f09244275fb15c139ee6650e0a83",
              "task": "skill_patch_apply",
              "total_tokens": 1479
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 31190,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/update/skill_post/SKILL.md",
          "skill_post_sha256": "6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "1dadae1ab3f0a95143bb2def3518a0e315b6a8385096e3ec853d819550b1cf77",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_2/win_c/update/update_receipt.json",
          "update_receipt_sha256": "4a9f5f92a83efa438ec3115fae55387c2d235b2dde389e83e8fb90d16f06aa9d"
        }
      },
      "evidence_windows_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/evidence_windows.json",
      "evidence_windows_sha256": "e5509065e0ec23b9045f1b67ee2b55df1fe23004a420f7b7a28a3c759af3a24b",
      "pair_summary_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/summary/replicates/e1-agj-00-rep2.json",
      "pair_summary_sha256": "675701d1e14798c7848a04648feb064b34791029c4ae72b887358c4a1ffd1c0c",
      "prefix_compatibility": "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL",
      "replicate_id": 2,
      "source": "inherited_repair1",
      "stream_id": "e1-agj-00",
      "unit_id": "e1-agj-00/rep2"
    },
    {
      "arms": {
        "mrw": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "f2c5bc797954590f90ef128183d390c38dc450c3abfca79d3a01bfcc31bf1288",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/checkpoints/provider_budget.sqlite3",
            "sha256": "4c632d5314a2b89ce733fda46f67b3695fe3966156bc656367fffb65a82a89ea",
            "total_claimed": 106,
            "unit_claimed": {
              "e1-agj-00/rep3/mrw/update": 10,
              "r17-b4-agj-p2/rollout_0": 5,
              "r17-b4-agj-p3/rollout_0": 7,
              "r17-b4-agj-p8/rollout_0": 5,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 9,
              "r17-b4-fmv-p8/rollout_0": 5,
              "r17-b4-ioc-p1/rollout_0": 4,
              "r17-b4-ioc-p4/rollout_0": 6,
              "r17-b4-ioc-p6/rollout_0": 4,
              "r17-b4-msp-p0/rollout_0": 6,
              "r17-b4-msp-p7/rollout_0": 3,
              "r17-b4-msp-p8/rollout_0": 7,
              "r17-b4-ska-p4/rollout_0": 5,
              "r17-b4-ska-p5/rollout_0": 6,
              "r17-b4-ska-p8/rollout_0": 5,
              "r17-b4-tsr-p0/rollout_0": 6,
              "r17-b4-tsr-p6/rollout_0": 6,
              "r17-b4-tsr-p8/rollout_0": 2
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "58e348c6e48889c9580aa83101cd6cecf2126157e88f92a062d8e9fd963cbd42",
              "provider_status": "completed",
              "response_sha256": "6e555e51f834481124577478a9ecbd9ae22441d3c03070205ff60dbc0edddefe",
              "sha256": "e10d3ed9921b088b74b6994d54983bbf111f27ebc573c3489ed941447aad66df",
              "task": "skill_trajectory_summary",
              "total_tokens": 3888
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "0684ac92b67a81d6e0a4673db91efbc9a0be2624a3a79beb536ec752d1de3ee1",
              "provider_status": "completed",
              "response_sha256": "21779e247da2739e34fd682dadc369c79e5900bea35494f5c14900b792dbc228",
              "sha256": "cd7852ce841ffb8a24b4c432cb2fa3643c361c1bf9162942b1aad0ade9ba7345",
              "task": "skill_trajectory_summary",
              "total_tokens": 3914
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "30b5b0838400d3038536448b1278d6f2a826331789157412c80022233a99ce9d",
              "provider_status": "completed",
              "response_sha256": "e7820d908715e06b0daf629f280248b5e00fde81c3f5e59f3097c5a754c97693",
              "sha256": "8d416e549eb0cd84e80bafed2488259cedafe38ca2e56dba68b6b7437cf5e65c",
              "task": "skill_trajectory_summary",
              "total_tokens": 3994
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c8e09de95c6da653bcbd181fffc13c3a6a6c4d1a32d417709bc7660a47e2012d",
              "provider_status": "completed",
              "response_sha256": "190dfc248401a9abcc82a46b5ca9b0070cec5fd80a362c4ef0e8edc3e3401761",
              "sha256": "c0a1d9efa68a74775cebfe90f522090c2b3fdf1e246cf9cef1c1e8054aad4209",
              "task": "skill_trajectory_summary",
              "total_tokens": 3936
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "9a7711f7a8b619b9668009c2b3a58093c0aa3565c3825f2983844683eedba1fe",
              "provider_status": "completed",
              "response_sha256": "b9db3471723578cfa61a4d5466a0eb0218a9f43fd88b4f61df996d498c70a9dd",
              "sha256": "6c26525c9a86116e5057601913be1916d98df77c9453b1ca2889634da038db49",
              "task": "skill_trajectory_summary",
              "total_tokens": 3913
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "4e81f724402262971d0e4dc22c83de6b712e61a7b3fb9cd86e680cf9bbefe537",
              "provider_status": "completed",
              "response_sha256": "5b46a9a302c95b9fe820319eaed4e72db5edc5bc93fb9da48de72defb6692872",
              "sha256": "c0af306770901fb6e385a49003b53ddd2328c9380cf392f8eaf5b026abe18372",
              "task": "skill_trajectory_summary",
              "total_tokens": 1795
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d4100506ddd401ae118d1e16b0f68e07bb23fa5f8f4b3e93c7c337894c6b166a",
              "provider_status": "completed",
              "response_sha256": "a9d71fb20fbf9c7a0a9c783bb9a1ba79821ef027f330b257cfa07f6d63bfbc92",
              "sha256": "6a24f9442f7b93575489225437997ae522b279d732205738bfa62b0e6d79985b",
              "task": "skill_trajectory_summary",
              "total_tokens": 2163
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c0c923d3c3d5d5a33f20ade124e824a53183fa30e57f72b6bdcb871d5318c20e",
              "provider_status": "completed",
              "response_sha256": "718a031a3544f604a10e82c3ea993b0c410652966fae6f5a73bc143a4086dde7",
              "sha256": "2835870b783fd55b12a4ab7fbc7a33d068850a6362c3c6f1f6517d9a2e1a34da",
              "task": "skill_trajectory_summary",
              "total_tokens": 2131
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "76ef27a7ba1d029b6945dff3f83de2f630988153f0c6a8731c95a1fcca865d45",
              "provider_status": "completed",
              "response_sha256": "baabede47a100a5635113072a48b5356cd6e58ec3d555e2e1103a69d66d5dfe4",
              "sha256": "dd67fca3f26430a7f1d1c9e19d64c2f8ab7652cfccd22f55cbfe941a55275609",
              "task": "skill_patch_propose",
              "total_tokens": 4533
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "08014721e4b2d77bae7e09bb8437f5f8970fe5beb1f44a0b1843eafa07e1948d",
              "provider_status": "completed",
              "response_sha256": "16e05b890410ac2f66c20596b53dd6c33ff8d681ce616131f8902e9b6282dc80",
              "sha256": "bd3a51c7c8ba38bae00c31f19e48c217f4753f4a9758fb8389dc9e4f3b6bcf26",
              "task": "skill_patch_apply",
              "total_tokens": 1843
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 32110,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/update/skill_post/SKILL.md",
          "skill_post_sha256": "783ac49d7473f8acf2310103f5ee63b42c63d1ecf586d4a4b9a06dcb95438cb3",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "c837f5cbeba6b6557d541dbae682ca248f63497528bff9385fde68ef0d232fe1",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/mrw/update/update_receipt.json",
          "update_receipt_sha256": "5585fd213115df71e52e1ea6c0883b230a21721de0533e78510560fda63e8107"
        },
        "win_c": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "075f2763032be679ff545bc6f00d8d251e6c577983e63337754499da5babfded",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/checkpoints/provider_budget.sqlite3",
            "sha256": "2c3befcc954f09de8e60f4ce05d71df1f59b71aafb250a1603b9e7979b294ba2",
            "total_claimed": 117,
            "unit_claimed": {
              "e1-agj-00/rep3/win_c/update": 10,
              "r17-b4-agj-p2/rollout_0": 6,
              "r17-b4-agj-p3/rollout_0": 4,
              "r17-b4-agj-p8/rollout_0": 8,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 3,
              "r17-b4-fmv-p8/rollout_0": 5,
              "r17-b4-ioc-p1/rollout_0": 4,
              "r17-b4-ioc-p4/rollout_0": 7,
              "r17-b4-ioc-p6/rollout_0": 6,
              "r17-b4-msp-p0/rollout_0": 7,
              "r17-b4-msp-p7/rollout_0": 10,
              "r17-b4-msp-p8/rollout_0": 3,
              "r17-b4-ska-p4/rollout_0": 7,
              "r17-b4-ska-p5/rollout_0": 8,
              "r17-b4-ska-p8/rollout_0": 6,
              "r17-b4-tsr-p0/rollout_0": 4,
              "r17-b4-tsr-p6/rollout_0": 7,
              "r17-b4-tsr-p8/rollout_0": 7
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "58e348c6e48889c9580aa83101cd6cecf2126157e88f92a062d8e9fd963cbd42",
              "provider_status": "completed",
              "response_sha256": "057213339574ac47df6300bf1af8ba6d4f175b454d96aeb388acb7f54f087fae",
              "sha256": "ce47085f09a614b27a86b1156ac915803d1a4895690d504b74a8ed380e5ca07f",
              "task": "skill_trajectory_summary",
              "total_tokens": 3946
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "0684ac92b67a81d6e0a4673db91efbc9a0be2624a3a79beb536ec752d1de3ee1",
              "provider_status": "completed",
              "response_sha256": "c6c0c9cf66d39d0ceee5141f3f42338a2c0255589e26fb321715b3d50903395f",
              "sha256": "9c7aff9f1530d578db584f06f4ff89713fae4366426dadbba055e145d2b9fb50",
              "task": "skill_trajectory_summary",
              "total_tokens": 3913
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "7cbdb74c510be8affe57688401d15833c39c759374bfd0dbaf31f35eeabdeed7",
              "provider_status": "completed",
              "response_sha256": "aeb271da9d90717be9fbfe9fdf51bb1eaeb072477bae89f88f0e0a9460a9f8df",
              "sha256": "a82db331988f77b35070dee8b807d12b979beec7f647786027e477d71d847829",
              "task": "skill_trajectory_summary",
              "total_tokens": 3883
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c8e09de95c6da653bcbd181fffc13c3a6a6c4d1a32d417709bc7660a47e2012d",
              "provider_status": "completed",
              "response_sha256": "24e5c2bc72508dd2893715380c5554538fb3901c5f05f9e2c2057cac500ef28e",
              "sha256": "c23117e4b50269c15876b4f22896d4ef7be26a2a41870367ab4d228766303044",
              "task": "skill_trajectory_summary",
              "total_tokens": 4001
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "9a7711f7a8b619b9668009c2b3a58093c0aa3565c3825f2983844683eedba1fe",
              "provider_status": "completed",
              "response_sha256": "ddc58ec6a8b385fb7aab2c99110ad3e11d37856db145e161859253cc2c53dcc3",
              "sha256": "7d21d1d0091dd1cd17ca5e35da85c8443a82f13e55c3b7127bb9b3446322d5c3",
              "task": "skill_trajectory_summary",
              "total_tokens": 3869
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "11f9d79e9d20f132d8b3ddddae2155b04d49c6d38398ac4dec60835e97541b55",
              "provider_status": "completed",
              "response_sha256": "e9d4c7da369a7607e5fdf3ab1065982ac284cbdd053c34dee80b1a778e19f2a1",
              "sha256": "74b36ea127ef5dd1a7354ec5dd70bedefad6b79ce7da1419c62c72f9bf5d092f",
              "task": "skill_trajectory_summary",
              "total_tokens": 1829
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "f3486e893207b6fe2a708fe244f6d88c5cffca7aa8ad14491a7586df4329d2ef",
              "provider_status": "completed",
              "response_sha256": "e3e17aa0e14d67993a238cc4f5922cdef58d03a33993b1991e7f794f8276c61a",
              "sha256": "67ba2a6ad7137dfaf6c6fa338c71014897c9e79064542f7f0feb0245c3c40253",
              "task": "skill_trajectory_summary",
              "total_tokens": 2159
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "0af39593578d41b10edba5ef0e128edb61f2ad2bc04e1f39bafabb89d4f17f7e",
              "provider_status": "completed",
              "response_sha256": "4d7d36b3720c854ca546d1804ca699c5c9c906512f455b716103ea289078022d",
              "sha256": "887f547d26edca17ea2bf659938a63a007ca17fdeec454f09a78db1eb0af1ee9",
              "task": "skill_trajectory_summary",
              "total_tokens": 1979
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "9992cba93c45fb9b9d92357b3a8a985d306feb3ccab34bffc36471c09770c378",
              "provider_status": "completed",
              "response_sha256": "e448040299969be8341215fcec55106b6c8c44c521f60b3e1ab1cbd6b07788c1",
              "sha256": "dfdbf1b8fef071e4b9fafebd7e1151bf68a78787f429220ee1c4470650a31a6e",
              "task": "skill_patch_propose",
              "total_tokens": 4042
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "ea91d4fc3c9b34c43eebb789f55d609f5a0d3534a7791d7efeb952bcc01f2ed8",
              "provider_status": "completed",
              "response_sha256": "4b12bf954c0d3306aa4c6dc6aa8b2e43fee3d13445c42f74d340ea4cb29bf349",
              "sha256": "74e0f90eba6a9b20cd77516dbc1607fc7ce2205e2063164bcf1b6c566301f70d",
              "task": "skill_patch_apply",
              "total_tokens": 1405
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 31026,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/update/skill_post/SKILL.md",
          "skill_post_sha256": "6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "00df87cdfc00190f190470c33d83a79e2c1ed78b2481ad9f6e67f75ba4ae3c5c",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/replicate_3/win_c/update/update_receipt.json",
          "update_receipt_sha256": "372dcda42366cdf50e3b17a4d9dcd68a614d060c9a2600164ef8a4493e889e28"
        }
      },
      "evidence_windows_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-00/evidence_windows.json",
      "evidence_windows_sha256": "e5509065e0ec23b9045f1b67ee2b55df1fe23004a420f7b7a28a3c759af3a24b",
      "pair_summary_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/summary/replicates/e1-agj-00-rep3.json",
      "pair_summary_sha256": "131ced887dae08f99327c32ed558b9fdd85290dbba6e982ba830fea093bdd030",
      "prefix_compatibility": "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL",
      "replicate_id": 3,
      "source": "inherited_repair1",
      "stream_id": "e1-agj-00",
      "unit_id": "e1-agj-00/rep3"
    },
    {
      "arms": {
        "mrw": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "701970e04242c874d7b00db1515ec01e9251f996a3b385088e1f96e98afb30c3",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/checkpoints/provider_budget.sqlite3",
            "sha256": "3f1f771dc8f96afc526d37c40572649ca9774c121999b350b247876dfe35d1d0",
            "total_claimed": 121,
            "unit_claimed": {
              "e1-agj-01/rep0/mrw/update": 10,
              "r17-b4-agj-p2/rollout_0": 3,
              "r17-b4-agj-p3/rollout_0": 5,
              "r17-b4-agj-p8/rollout_0": 7,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 5,
              "r17-b4-fmv-p8/rollout_0": 6,
              "r17-b4-ioc-p1/rollout_0": 6,
              "r17-b4-ioc-p4/rollout_0": 6,
              "r17-b4-ioc-p6/rollout_0": 6,
              "r17-b4-msp-p0/rollout_0": 7,
              "r17-b4-msp-p7/rollout_0": 7,
              "r17-b4-msp-p8/rollout_0": 8,
              "r17-b4-ska-p4/rollout_0": 6,
              "r17-b4-ska-p5/rollout_0": 7,
              "r17-b4-ska-p8/rollout_0": 6,
              "r17-b4-tsr-p0/rollout_0": 6,
              "r17-b4-tsr-p6/rollout_0": 9,
              "r17-b4-tsr-p8/rollout_0": 6
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "7bd4fce10599f4fe8de26f19b72378569676df1397addde93eb4e194077a820b",
              "provider_status": "completed",
              "response_sha256": "ad56a5388544517965706030917bc2195a485a29209948f7b65d7c1b3b7673aa",
              "sha256": "ca60dfa17d88bf85babf59142279478544f06f8431401fcfc45e6000474d78b7",
              "task": "skill_trajectory_summary",
              "total_tokens": 1646
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "6619d317ff645bc8cc5cf8efd7a2faf8827ba0c941ec3a5e1337134b0316b3df",
              "provider_status": "completed",
              "response_sha256": "fa1edeb3711d6bb83c452caa3653ae671bf271f9e2990819dd03046a90572453",
              "sha256": "8f9cd290817fef90545a9371657ef70286ade73a4cc0f27c1b781b7c28d7d508",
              "task": "skill_trajectory_summary",
              "total_tokens": 1977
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "1bbcbb2d4af4bd491b6e89003b5351b656aa983662131cb76e3ff2c0fb6dbb31",
              "provider_status": "completed",
              "response_sha256": "037feb6ad3e08d550832af4bb087345ffb24fbcb3e8cc33f0dbefacbbb03ba37",
              "sha256": "d5b0ada1aa6be807fe09ca39e5f2c8d820363162903713b7b4bd00c1f9d5c754",
              "task": "skill_trajectory_summary",
              "total_tokens": 3955
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d45418ffd0adc6bf882c4da5f98b92eeba03afc5453084ab1f5d4202c2cb1147",
              "provider_status": "completed",
              "response_sha256": "eb6233daedddefede1c28fb62dfab5a8af8c40c90d5c0f595df15167a2484c0f",
              "sha256": "e6f1d973aaa3cec4a6146e6ceac159ce63f69db16e6c9f6985c1da4683ee2e3e",
              "task": "skill_trajectory_summary",
              "total_tokens": 3863
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "cf165c54a5b811a3388926f7125f2755884b940a52a892cc31c80d80144cc099",
              "provider_status": "completed",
              "response_sha256": "8ff1cf50d3b467ff644dddf0d6d74744d3786c9561d01edfc1960927ea6dca56",
              "sha256": "022c52af62b37446a1858d6e16b0d4fe93f430913cf4cab82df106397d999830",
              "task": "skill_trajectory_summary",
              "total_tokens": 3859
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a0a12117647c06cb1698e2666a9284805b85aa08971131c251057f989698130d",
              "provider_status": "completed",
              "response_sha256": "48784aace8300ee181129c9d9127f868232e512d07d36d578eab0cfd6f3c010b",
              "sha256": "43ecb6c5c029f0eb7230ff549503220107d2b09c1bd81940e6a3d54b1ad4ec9f",
              "task": "skill_trajectory_summary",
              "total_tokens": 1805
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "61a0993b780e2d06f22c865385c37b72c05735dcbe8f814f1d8e5728ebc006e9",
              "provider_status": "completed",
              "response_sha256": "c6afda71fe2fda209d78a9089d951cefd822193b35013b8c357110b6760e6b03",
              "sha256": "4539e26d61f680eec39ddff0d3e8b213f13415b3824b578158d792690574b519",
              "task": "skill_trajectory_summary",
              "total_tokens": 2046
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "b8f24518f24f3a433ba856b79762d07b3dc1bf4d6169c7d7e6fd51b221aeaf10",
              "provider_status": "completed",
              "response_sha256": "0cf71eac93ec4fca3dc8a6eb602eea7877d9bac606db3fae66b72e7dc7521aa0",
              "sha256": "c1532e92e5e159b4f24b0f7e5e271348d5c3e0d72866d58d953d47220853611b",
              "task": "skill_trajectory_summary",
              "total_tokens": 2636
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "8c796edfb6a1ea3ee79890f4af03eaac2451fa53c929d1c0ca8ab50bf81ebb0e",
              "provider_status": "completed",
              "response_sha256": "1ab59e3df4fe6406247835855f1d739ee2208daa973f13d59eb4b3d39f6b6fd2",
              "sha256": "b9c9b22f9e34f0e2f2f3bc05be74afefcc313499819345c3ecb91663f53a36c8",
              "task": "skill_patch_propose",
              "total_tokens": 4125
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "bd730ca6c150c50230cf002684d4d4560730808322c939882cfd29a51b0ed067",
              "provider_status": "completed",
              "response_sha256": "20f2477501738013af4e8daff04eb7e7cd6621a4084ce22d2c8ab7c999f716c9",
              "sha256": "1cdf9a8d351ae961ef60b0b9b0a0f2f80f7a673554299e7375de9d6c1604a358",
              "task": "skill_patch_apply",
              "total_tokens": 2188
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 28100,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/update/skill_post/SKILL.md",
          "skill_post_sha256": "04759f7bf900f58709887f3d913337b5bac0bd2cce6dbcb297f93768e0e2b40f",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "ed1bb21b16e0a16e973b32cf107bfdd5c6c2d909ea0211fe1cfa3c8e78b4ff08",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/mrw/update/update_receipt.json",
          "update_receipt_sha256": "a6886ac7fd0dd53d3fab8410bd243ab67c57c741d881a224d506d4e24071ef23"
        },
        "win_c": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "75e1375837938a55548f59e6f18e1dda3a94064b40cc2f5ab384458150e1e2bd",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/checkpoints/provider_budget.sqlite3",
            "sha256": "0ae299f180ee40037c784036d99081e4381dd8c307f1a2fafb8f2759a92c3c86",
            "total_claimed": 115,
            "unit_claimed": {
              "e1-agj-01/rep0/win_c/update": 10,
              "r17-b4-agj-p2/rollout_0": 6,
              "r17-b4-agj-p3/rollout_0": 6,
              "r17-b4-agj-p8/rollout_0": 6,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 5,
              "r17-b4-fmv-p8/rollout_0": 5,
              "r17-b4-ioc-p1/rollout_0": 5,
              "r17-b4-ioc-p4/rollout_0": 5,
              "r17-b4-ioc-p6/rollout_0": 5,
              "r17-b4-msp-p0/rollout_0": 7,
              "r17-b4-msp-p7/rollout_0": 7,
              "r17-b4-msp-p8/rollout_0": 9,
              "r17-b4-ska-p4/rollout_0": 7,
              "r17-b4-ska-p5/rollout_0": 6,
              "r17-b4-ska-p8/rollout_0": 6,
              "r17-b4-tsr-p0/rollout_0": 5,
              "r17-b4-tsr-p6/rollout_0": 5,
              "r17-b4-tsr-p8/rollout_0": 5
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a68d4d6a65de9ee6c3b15eb1a741d7fac8d4411b4026f5c70d49593383c52daf",
              "provider_status": "completed",
              "response_sha256": "83c008a31297c350d9cf2d4e423e434e70b20287df10e4218a8478a177da00d0",
              "sha256": "d4e21a99bff6a61303bf69585fa0d31fc48d7fa0d9c421e84a3294b0d67325fd",
              "task": "skill_trajectory_summary",
              "total_tokens": 1781
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "003805d22bcea74b97d508d9595201bcd63bfe886d080f49bd2026029957b15d",
              "provider_status": "completed",
              "response_sha256": "ea1b6b89894ee1fd174d733f4af35ea4795a88aa72d008cd17f49852761f73db",
              "sha256": "bae6b89b9c06767d642af7aeee1b5517239bf94ced973f518f5ec36d058bf555",
              "task": "skill_trajectory_summary",
              "total_tokens": 2025
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "1bbcbb2d4af4bd491b6e89003b5351b656aa983662131cb76e3ff2c0fb6dbb31",
              "provider_status": "completed",
              "response_sha256": "dac45860840f369871ce2f86076bdcd25fd83fcb9582c31c402af2169a3475c1",
              "sha256": "dd6b306afb1a88e40fbaa04e632fcca42519d0edfd13468775029e25050ad213",
              "task": "skill_trajectory_summary",
              "total_tokens": 3942
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d45418ffd0adc6bf882c4da5f98b92eeba03afc5453084ab1f5d4202c2cb1147",
              "provider_status": "completed",
              "response_sha256": "d674836f2e41636aa72c23c896595885c46929d2c3817144c68d99bcb42195cc",
              "sha256": "74003a65cae4a91f71594c5365fa1ebb167b079aebca5e671b5bc9bdd7cbce17",
              "task": "skill_trajectory_summary",
              "total_tokens": 3790
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "cf165c54a5b811a3388926f7125f2755884b940a52a892cc31c80d80144cc099",
              "provider_status": "completed",
              "response_sha256": "ca7d7bc5477811849c578c0fe31cc7bc216b0209e1b82a177b07c0e93b370908",
              "sha256": "c4b1000c16d78729ff9ca42014b3c15482823ddf4c5187910d5f7d2448ec7353",
              "task": "skill_trajectory_summary",
              "total_tokens": 3878
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "3ada4685fa4e8b0c1655d095d0cd6c5edec15a2e6882787a315c01d4186f359c",
              "provider_status": "completed",
              "response_sha256": "aea1b5f35e9c70181b9d3fc825346f8bbf4f37c5eef89cfdd6e31995bec721ad",
              "sha256": "f671ce5453402f208d77b0e687deea11f535f067450f40db6f70dba894fb61dd",
              "task": "skill_trajectory_summary",
              "total_tokens": 1883
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "1f4fe2897f6a8abe14ff95446776b3cbae0767e85a00b5aca6a18ca6b5f0dade",
              "provider_status": "completed",
              "response_sha256": "8eab41596bdb5e36a20a190627b981eeff4112b09bf25b7bcf8991d6fb7d419a",
              "sha256": "5f274f06236c1671a8ff4e5157cf1b3b3845b2e1498200c59a1955c5ffcf6fa8",
              "task": "skill_trajectory_summary",
              "total_tokens": 2026
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "779bef0c8969681af089191016f148bf2d219a28da25be9a3019e5c993164c8d",
              "provider_status": "completed",
              "response_sha256": "ccf0e6bb33e97eb603b912f118feacb30f6a9b91eb0f263ccdd7ee02aee458f6",
              "sha256": "6e2b8e8451159623173b228e3479402cf51bc5d50d38c2c7055c61688a02be93",
              "task": "skill_trajectory_summary",
              "total_tokens": 2591
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "c7833277e32838a793756b5e9b24d572519279469ae6e427dc19e11f67d4b624",
              "provider_status": "completed",
              "response_sha256": "eed4adb6167e4dd4803ec0e21ccb9a44d98e013c508a474ddc768c5c639d551e",
              "sha256": "d7ae6d88cc442343e5f1be456cc43d4cf5e4077ee6e222365ae7ee8a44e075b1",
              "task": "skill_patch_propose",
              "total_tokens": 3832
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "1e931fff4ac455736d487c7fe0c9807147ac1651c34812ed0e49a4b582ce048e",
              "provider_status": "completed",
              "response_sha256": "4b12bf954c0d3306aa4c6dc6aa8b2e43fee3d13445c42f74d340ea4cb29bf349",
              "sha256": "735d9dc0d3f4def315502c87e83497c02ee99fc9edab432f4db601fd95d4c61f",
              "task": "skill_patch_apply",
              "total_tokens": 1414
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 27162,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/update/skill_post/SKILL.md",
          "skill_post_sha256": "6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "8ea6ead976c9f172529bd74955147190a91ffa4ee1354fb8e2b326704ff39116",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_0/win_c/update/update_receipt.json",
          "update_receipt_sha256": "2f464c7a1875abe80946f4846a4b3da4485f4b25a5b647dd49aa55a513a6ed50"
        }
      },
      "evidence_windows_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/evidence_windows.json",
      "evidence_windows_sha256": "3fe4b64fbba9c94f081be5986c93ee78243ec80daaab187ed27ce2fb07489fe9",
      "pair_summary_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/summary/replicates/e1-agj-01-rep0.json",
      "pair_summary_sha256": "d239aff7e71ed700cc82fabcd42cea894e09770000f82d8ef3757058fd8cf52a",
      "prefix_compatibility": "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL",
      "replicate_id": 0,
      "source": "inherited_repair1",
      "stream_id": "e1-agj-01",
      "unit_id": "e1-agj-01/rep0"
    },
    {
      "arms": {
        "mrw": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "b9afad035af3ae9aa3d9cf9a1a4bcab9688d4c9674ac60995ce037039c5719d3",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/checkpoints/provider_budget.sqlite3",
            "sha256": "a686795f9a7a5be810971be981c0c01e5797db065f354c00bd0448f87e60b2ae",
            "total_claimed": 100,
            "unit_claimed": {
              "e1-agj-01/rep1/mrw/update": 10,
              "r17-b4-agj-p2/rollout_0": 7,
              "r17-b4-agj-p3/rollout_0": 6,
              "r17-b4-agj-p8/rollout_0": 5,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 3,
              "r17-b4-fmv-p8/rollout_0": 4,
              "r17-b4-ioc-p1/rollout_0": 6,
              "r17-b4-ioc-p4/rollout_0": 5,
              "r17-b4-ioc-p6/rollout_0": 5,
              "r17-b4-msp-p0/rollout_0": 6,
              "r17-b4-msp-p7/rollout_0": 3,
              "r17-b4-msp-p8/rollout_0": 9,
              "r17-b4-ska-p4/rollout_0": 5,
              "r17-b4-ska-p5/rollout_0": 5,
              "r17-b4-ska-p8/rollout_0": 4,
              "r17-b4-tsr-p0/rollout_0": 5,
              "r17-b4-tsr-p6/rollout_0": 2,
              "r17-b4-tsr-p8/rollout_0": 5
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "7bd4fce10599f4fe8de26f19b72378569676df1397addde93eb4e194077a820b",
              "provider_status": "completed",
              "response_sha256": "0621e5955a64e3c5639c4b4a8c9ce5450426cce4d4d193c7d7ccf8818549a419",
              "sha256": "e0b74e4d854681ffbc05dee0128d7ebcc0f3409dce750bbe76e0bab922ef08eb",
              "task": "skill_trajectory_summary",
              "total_tokens": 1650
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "6619d317ff645bc8cc5cf8efd7a2faf8827ba0c941ec3a5e1337134b0316b3df",
              "provider_status": "completed",
              "response_sha256": "ba788ad2e10631fdb1db55fcf72ce42b5a3f8666c6b28b4ce2e6d87d2d9ffd92",
              "sha256": "84287c6228471304029cb3dc0c784e2edfe6c55e831324ce773f5169d89202d3",
              "task": "skill_trajectory_summary",
              "total_tokens": 2034
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "1bbcbb2d4af4bd491b6e89003b5351b656aa983662131cb76e3ff2c0fb6dbb31",
              "provider_status": "completed",
              "response_sha256": "a89f6a9c48f604b9e329b70269a9f3f2013a693e3e3528fa8fcc6784efd90e3f",
              "sha256": "2545a1ce596ee74c615cec18d0ab06d76b965a6976d6a527e803a4027815a151",
              "task": "skill_trajectory_summary",
              "total_tokens": 3976
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d45418ffd0adc6bf882c4da5f98b92eeba03afc5453084ab1f5d4202c2cb1147",
              "provider_status": "completed",
              "response_sha256": "6ff2c9c622b52a699ec8d7abff3d75bfbdc3ab36f694bac15fbdb7474ff47ea5",
              "sha256": "2b8bebb6384a41b6350eb6aec4e6361e9eba695fa19eab9dfb9f5e4cff50c360",
              "task": "skill_trajectory_summary",
              "total_tokens": 3869
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "cf165c54a5b811a3388926f7125f2755884b940a52a892cc31c80d80144cc099",
              "provider_status": "completed",
              "response_sha256": "7e796e75390626acb603a75620268da0aa31e12143d682dce33c7b13d0f0dc91",
              "sha256": "369fe6fe290b2ab9683eeef57e1d7d9b076395cd4f44b29e7dbcad1d1a8b466f",
              "task": "skill_trajectory_summary",
              "total_tokens": 3956
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a0a12117647c06cb1698e2666a9284805b85aa08971131c251057f989698130d",
              "provider_status": "completed",
              "response_sha256": "bf08fd20b79fff40077726afa10455188a28c545f373139f4d796c1099d7bab3",
              "sha256": "578e1862c8732574c38b6d19cc268ae1bd7f82aba62dfe7ca685fe68cbfea49e",
              "task": "skill_trajectory_summary",
              "total_tokens": 1802
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "61a0993b780e2d06f22c865385c37b72c05735dcbe8f814f1d8e5728ebc006e9",
              "provider_status": "completed",
              "response_sha256": "5eb25aef23378fe35ae1276423a3edf7190be9fff8edbc88949fb56610f53482",
              "sha256": "259746c492691adb50345e79d97ccc561e144bc97bc508f99e7360b245cbf071",
              "task": "skill_trajectory_summary",
              "total_tokens": 1944
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "b8f24518f24f3a433ba856b79762d07b3dc1bf4d6169c7d7e6fd51b221aeaf10",
              "provider_status": "completed",
              "response_sha256": "e68a82e8db5c6d40361cac735c500be3066e4b92d58bf9069fb96ab12f4fbcab",
              "sha256": "137e33dcae94aefcf49ddcc0d77565db63e631beec298c324244f13055c3d2e2",
              "task": "skill_trajectory_summary",
              "total_tokens": 2541
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "3f400d3602f8942328266172012ad07bf2e176b12809c318ba353bcdce5a9ad2",
              "provider_status": "completed",
              "response_sha256": "23aa808501d3bd7bb458899dca5e9dde90aa3f3ed5f00d0193025a0bba1f0844",
              "sha256": "42afec3682b62af4b1d0694e54d39db4154d8e8d34a76fcb42cbfeda904afed2",
              "task": "skill_patch_propose",
              "total_tokens": 4133
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "234151d65a7d525a5667e25423cd635409ebfeeac6ceaaafb5103f49ea19dd85",
              "provider_status": "completed",
              "response_sha256": "ffa07a41fa5050863929d3a2e9d894b3dc609296b39429e043f95393e54d0883",
              "sha256": "e06f2cec2335c503b3c0d5457770fa4ba3943ef1651eb5517471a46145d8f451",
              "task": "skill_patch_apply",
              "total_tokens": 2296
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 28201,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/update/skill_post/SKILL.md",
          "skill_post_sha256": "14fa2d1e3ba67c77f4a2a7a208e856798a571818801bae5ed4146b7985171ab4",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "ccfd2c94213114b94126aa8cbae228b3da3122699c38403d4b4ab189286615fb",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/mrw/update/update_receipt.json",
          "update_receipt_sha256": "ef6d0c726ed73e76a9e9004eda753ae93322b766be99deca4574476226597f03"
        },
        "win_c": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "7777d38c79c64c0c55a943cf9250f6b2ab6182309af87de4ced335a21d7836d8",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/checkpoints/provider_budget.sqlite3",
            "sha256": "686d16e093840881f4439c203297391b011555022d865366133709b04203d021",
            "total_claimed": 107,
            "unit_claimed": {
              "e1-agj-01/rep1/win_c/update": 10,
              "r17-b4-agj-p2/rollout_0": 3,
              "r17-b4-agj-p3/rollout_0": 6,
              "r17-b4-agj-p8/rollout_0": 3,
              "r17-b4-fmv-p1/rollout_0": 4,
              "r17-b4-fmv-p2/rollout_0": 5,
              "r17-b4-fmv-p8/rollout_0": 5,
              "r17-b4-ioc-p1/rollout_0": 7,
              "r17-b4-ioc-p4/rollout_0": 4,
              "r17-b4-ioc-p6/rollout_0": 8,
              "r17-b4-msp-p0/rollout_0": 7,
              "r17-b4-msp-p7/rollout_0": 8,
              "r17-b4-msp-p8/rollout_0": 3,
              "r17-b4-ska-p4/rollout_0": 6,
              "r17-b4-ska-p5/rollout_0": 4,
              "r17-b4-ska-p8/rollout_0": 5,
              "r17-b4-tsr-p0/rollout_0": 5,
              "r17-b4-tsr-p6/rollout_0": 7,
              "r17-b4-tsr-p8/rollout_0": 7
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a68d4d6a65de9ee6c3b15eb1a741d7fac8d4411b4026f5c70d49593383c52daf",
              "provider_status": "completed",
              "response_sha256": "90301717b3b23c3da90717123d6866a698b7bbb0deb42b73e696ba018a997d7c",
              "sha256": "2fc82911a78c5ba00782110d8ea3334bacc2d98ba640f715410941fe5bd9e2c5",
              "task": "skill_trajectory_summary",
              "total_tokens": 1787
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "003805d22bcea74b97d508d9595201bcd63bfe886d080f49bd2026029957b15d",
              "provider_status": "completed",
              "response_sha256": "8f8954ad694c5f7ed891a793460a52c3684ff2a0e78d1687e0bc0a6c23d982d9",
              "sha256": "129dff50a1af6b66dc15675887117b63298a02b4b9e86ec0cd4ef9597c5ec7f4",
              "task": "skill_trajectory_summary",
              "total_tokens": 1969
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "1bbcbb2d4af4bd491b6e89003b5351b656aa983662131cb76e3ff2c0fb6dbb31",
              "provider_status": "completed",
              "response_sha256": "6db6082052675fc65691ee1826c360d9f82a4694260cf0c02974ae29594bea33",
              "sha256": "7de117bf2b7f8444832ea8a72e37e077272f952e44ecc62242da5b2d74343478",
              "task": "skill_trajectory_summary",
              "total_tokens": 3943
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d45418ffd0adc6bf882c4da5f98b92eeba03afc5453084ab1f5d4202c2cb1147",
              "provider_status": "completed",
              "response_sha256": "8e8e3ad561e78a0d8ed8b0053107dadc43bc52a3d054d7a3a89bcf8a0cee6d84",
              "sha256": "b5adcf70d1131d97985c838080f0a88dbbb743288813eafb77443c90bf77237a",
              "task": "skill_trajectory_summary",
              "total_tokens": 3845
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "cf165c54a5b811a3388926f7125f2755884b940a52a892cc31c80d80144cc099",
              "provider_status": "completed",
              "response_sha256": "75d4dfcee56edcc67aa241579d5487de945c7f439fb906356411d923cdefad6a",
              "sha256": "a43fb7fe23124875dc25478fac379ba51c3f6f2b71889b286d830ee9df19461f",
              "task": "skill_trajectory_summary",
              "total_tokens": 3852
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "3ada4685fa4e8b0c1655d095d0cd6c5edec15a2e6882787a315c01d4186f359c",
              "provider_status": "completed",
              "response_sha256": "24df3eb18c2047bad3fc74e12ce2c3de3f51fcd455d782d7669d42194795c657",
              "sha256": "d9d7eac53dae50c3d2b9252e2ea3d9a0af8dc14610974714ea6fab9678b74eb9",
              "task": "skill_trajectory_summary",
              "total_tokens": 1837
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "1f4fe2897f6a8abe14ff95446776b3cbae0767e85a00b5aca6a18ca6b5f0dade",
              "provider_status": "completed",
              "response_sha256": "6e767cea586166b97bc89c2e60ec8e0b6865415bafcbe6d24df174ea5d7e985d",
              "sha256": "9c1571568dfd20c2ae057aa11575a106ce52ed54a1e242b0e82d4538e3226819",
              "task": "skill_trajectory_summary",
              "total_tokens": 1947
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "779bef0c8969681af089191016f148bf2d219a28da25be9a3019e5c993164c8d",
              "provider_status": "completed",
              "response_sha256": "3d1d67893983d0bb501085632d8427f712c5d2637d75200b42b3f6755bc61ba5",
              "sha256": "0331bbaf6b7c3fcd63579425fe748e0bec198cb215c85d05601ae429e6f30163",
              "task": "skill_trajectory_summary",
              "total_tokens": 2593
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "5b1eeef1bda8601f6f5a4cdc9b3533588080f0e3180572f7f19ce3416c85aa9d",
              "provider_status": "completed",
              "response_sha256": "9eabaf9bf074823e37d5957bae562d6bc968672e6eaf8ce55dd239366b760235",
              "sha256": "ff4032535edb92efa8472a4e669a12a14f3be7f20059673c1050df0cd9b4a23a",
              "task": "skill_patch_propose",
              "total_tokens": 3697
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "6b3e617d60b394fe86a4c574bdb0de73b3f8249035b4ce1506d6065ddda2bd26",
              "provider_status": "completed",
              "response_sha256": "4b12bf954c0d3306aa4c6dc6aa8b2e43fee3d13445c42f74d340ea4cb29bf349",
              "sha256": "a957136e749adbff656475cb4ee0c4f26c46e88bbb728d7830cd58b770c02937",
              "task": "skill_patch_apply",
              "total_tokens": 1422
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 26892,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/update/skill_post/SKILL.md",
          "skill_post_sha256": "6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "f1c16ec6194a5cb339ec5ed54a9665a1b354f01ce5e4b9d80ffdec9e0251bf86",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_1/win_c/update/update_receipt.json",
          "update_receipt_sha256": "8d3ff00a30dbf8779fc908015d028441841e3a5f829baa87ca72e58f0c3ff6ad"
        }
      },
      "evidence_windows_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/evidence_windows.json",
      "evidence_windows_sha256": "3fe4b64fbba9c94f081be5986c93ee78243ec80daaab187ed27ce2fb07489fe9",
      "pair_summary_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/summary/replicates/e1-agj-01-rep1.json",
      "pair_summary_sha256": "478dbc72fa63508896bede498af055736c31cb4c6168075353172554e59650e5",
      "prefix_compatibility": "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL",
      "replicate_id": 1,
      "source": "inherited_repair1",
      "stream_id": "e1-agj-01",
      "unit_id": "e1-agj-01/rep1"
    },
    {
      "arms": {
        "mrw": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "841a5a9a99e87baba5cc99456e2c8cb2fab94adca7f1bdfa2018c9de1d5e7dcd",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/checkpoints/provider_budget.sqlite3",
            "sha256": "08ca738ed5313d3cb52bc1eb29405b54d91005d9fc282d5a7a3d30237043bbbc",
            "total_claimed": 117,
            "unit_claimed": {
              "e1-agj-01/rep2/mrw/update": 10,
              "r17-b4-agj-p2/rollout_0": 5,
              "r17-b4-agj-p3/rollout_0": 5,
              "r17-b4-agj-p8/rollout_0": 6,
              "r17-b4-fmv-p1/rollout_0": 4,
              "r17-b4-fmv-p2/rollout_0": 6,
              "r17-b4-fmv-p8/rollout_0": 4,
              "r17-b4-ioc-p1/rollout_0": 9,
              "r17-b4-ioc-p4/rollout_0": 6,
              "r17-b4-ioc-p6/rollout_0": 6,
              "r17-b4-msp-p0/rollout_0": 6,
              "r17-b4-msp-p7/rollout_0": 7,
              "r17-b4-msp-p8/rollout_0": 9,
              "r17-b4-ska-p4/rollout_0": 8,
              "r17-b4-ska-p5/rollout_0": 5,
              "r17-b4-ska-p8/rollout_0": 6,
              "r17-b4-tsr-p0/rollout_0": 5,
              "r17-b4-tsr-p6/rollout_0": 5,
              "r17-b4-tsr-p8/rollout_0": 5
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "7bd4fce10599f4fe8de26f19b72378569676df1397addde93eb4e194077a820b",
              "provider_status": "completed",
              "response_sha256": "d234dc67b77f9f23d68cbe7171a02446bf098fffdf4a77a2d1f17546c27e1d81",
              "sha256": "9a42af1f34c566b824a539ad65695dce0498bb3b86972830dfa2ff51aaea6eee",
              "task": "skill_trajectory_summary",
              "total_tokens": 1651
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "6619d317ff645bc8cc5cf8efd7a2faf8827ba0c941ec3a5e1337134b0316b3df",
              "provider_status": "completed",
              "response_sha256": "6c21e022e1b1d324bc441f1029a4455be867ce5c8e31357bb1bd589e290a880f",
              "sha256": "bc0d1e2d9d80b522decd5314eac8c80a7f1d640b6b522cccd4a6fcae34e70e81",
              "task": "skill_trajectory_summary",
              "total_tokens": 2235
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "1bbcbb2d4af4bd491b6e89003b5351b656aa983662131cb76e3ff2c0fb6dbb31",
              "provider_status": "completed",
              "response_sha256": "c7d7b2359508efd9d24050ff7bc863cf0c38450bcc1aff511d4e5c6e88eb6dee",
              "sha256": "b44c31d44eb0fd7471c2b8f1b0339aa2a88bc2f3c41fcde25655b0c57b3862c1",
              "task": "skill_trajectory_summary",
              "total_tokens": 3959
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d45418ffd0adc6bf882c4da5f98b92eeba03afc5453084ab1f5d4202c2cb1147",
              "provider_status": "completed",
              "response_sha256": "73426268c09b6f3df9fe79594833efa9ff8dc6191df7690152e3f3eb0a99103f",
              "sha256": "2b55e0c522fe10e8b37aede82da045ba4a1cd5c0a7c06f24ef380a78b5ae3f89",
              "task": "skill_trajectory_summary",
              "total_tokens": 3785
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "cf165c54a5b811a3388926f7125f2755884b940a52a892cc31c80d80144cc099",
              "provider_status": "completed",
              "response_sha256": "665b49c81b9c7969359b6f3b24a0e1e9b94068c4ff20064c1efc9a2843a037e8",
              "sha256": "6b0a24e6956c2fbcb974cc77ae9017dfae7917242028abe842e43102f2cd8ed9",
              "task": "skill_trajectory_summary",
              "total_tokens": 3885
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a0a12117647c06cb1698e2666a9284805b85aa08971131c251057f989698130d",
              "provider_status": "completed",
              "response_sha256": "dceaaf945c2f947b1c2aae660d005872b11f1064e6ed68a30d8450e9c507f625",
              "sha256": "e365d8cbee111f614a8a0c25179132960979f76b55090a3d9b62832ba4d6b964",
              "task": "skill_trajectory_summary",
              "total_tokens": 1766
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "61a0993b780e2d06f22c865385c37b72c05735dcbe8f814f1d8e5728ebc006e9",
              "provider_status": "completed",
              "response_sha256": "712eb549db3cb6497910cda2a0edeaf649b971653b88c06922de7880873e5767",
              "sha256": "14eee66f176bb0b9950720ddb77bbb419c7e090d1e06f4de9fff8f3ce860f1ad",
              "task": "skill_trajectory_summary",
              "total_tokens": 2020
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "b8f24518f24f3a433ba856b79762d07b3dc1bf4d6169c7d7e6fd51b221aeaf10",
              "provider_status": "completed",
              "response_sha256": "bff3f269d54280e843a9c78cefcabf68258d8e920e81d3dc3d14df7829c56e27",
              "sha256": "8d3c35ac683bebe54f2d9ab6b5397d768395992acb0ea8b7cd4ca5b9abfc702a",
              "task": "skill_trajectory_summary",
              "total_tokens": 2685
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "7a6bc89b6e2c0982ec1e5a10b4c0909cc62ed8ec14398ef8336e0cc85d157717",
              "provider_status": "completed",
              "response_sha256": "559016b44b9bbe64f435e1e590fbe025a80e7f1f8db7582773410ffbf75fda8a",
              "sha256": "43adcb0c206ee7b0226f303ed191a15df12116a56ebb0db2829c188e6eea5770",
              "task": "skill_patch_propose",
              "total_tokens": 4316
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "f31249732ad9992bac476bf7ad346e575729b3765095de563a158990e2dae949",
              "provider_status": "completed",
              "response_sha256": "fae5ebb2851b71d4c46d1670175ce1dbec5f15c136e3785ecf498a0bb240831e",
              "sha256": "843383a5b2fef68a6c52fc5bfa7834398098108c6e87445d231fbc050980bd4b",
              "task": "skill_patch_apply",
              "total_tokens": 2140
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 28442,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/update/skill_post/SKILL.md",
          "skill_post_sha256": "d3ba1f2547383aa9128f243edba57b32b0c5f9c8fd7f9646094b9a361af48d15",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "169034bf4c9105db656c4d9e37f73c09734f4c8c3611daf99acb63ff5313ff53",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/mrw/update/update_receipt.json",
          "update_receipt_sha256": "5ada423beb2abda3dfc65151a0dfcad0d7fa13f96cf47c0de29962bf23873ae3"
        },
        "win_c": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "db4b8c37a5e5c13bf7d08746ea701d1c0253a10b61541aef83bd3fe87923fdf3",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/checkpoints/provider_budget.sqlite3",
            "sha256": "f43a7546551cc3a90816fb636386f9a3807e3c45dd3446b57745184ad13b736b",
            "total_claimed": 97,
            "unit_claimed": {
              "e1-agj-01/rep2/win_c/update": 10,
              "r17-b4-agj-p2/rollout_0": 5,
              "r17-b4-agj-p3/rollout_0": 7,
              "r17-b4-agj-p8/rollout_0": 5,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 5,
              "r17-b4-fmv-p8/rollout_0": 6,
              "r17-b4-ioc-p1/rollout_0": 4,
              "r17-b4-ioc-p4/rollout_0": 3,
              "r17-b4-ioc-p6/rollout_0": 5,
              "r17-b4-msp-p0/rollout_0": 7,
              "r17-b4-msp-p7/rollout_0": 5,
              "r17-b4-msp-p8/rollout_0": 3,
              "r17-b4-ska-p4/rollout_0": 4,
              "r17-b4-ska-p5/rollout_0": 6,
              "r17-b4-ska-p8/rollout_0": 5,
              "r17-b4-tsr-p0/rollout_0": 6,
              "r17-b4-tsr-p6/rollout_0": 3,
              "r17-b4-tsr-p8/rollout_0": 3
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a68d4d6a65de9ee6c3b15eb1a741d7fac8d4411b4026f5c70d49593383c52daf",
              "provider_status": "completed",
              "response_sha256": "cb4b41d96012ef0d98d07c27e88fa1e03472f3d8b579281c205422f31dca4d86",
              "sha256": "0764d86384fa3a25b9de018ec512ddfba7402f76bca764107fd82ed523b7c517",
              "task": "skill_trajectory_summary",
              "total_tokens": 1763
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "003805d22bcea74b97d508d9595201bcd63bfe886d080f49bd2026029957b15d",
              "provider_status": "completed",
              "response_sha256": "b980df89cdca331489ffdc2d7fb5e96495f0aca7e73fd6129274ee25664b276b",
              "sha256": "74b60302d570e8bab16b9b6ff2d239828dc4c4b20d3123a301d279c533f76fa4",
              "task": "skill_trajectory_summary",
              "total_tokens": 2042
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "1bbcbb2d4af4bd491b6e89003b5351b656aa983662131cb76e3ff2c0fb6dbb31",
              "provider_status": "completed",
              "response_sha256": "51fc131380e87963440c56744e2beaa96e3839d792df7c353462658407d464d1",
              "sha256": "553bfb6ca1dabdf20a6945baf1a057bab42a7c89df33c394ca5e2c8070745ac7",
              "task": "skill_trajectory_summary",
              "total_tokens": 3938
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d45418ffd0adc6bf882c4da5f98b92eeba03afc5453084ab1f5d4202c2cb1147",
              "provider_status": "completed",
              "response_sha256": "8b010e8400532cd7676adf2592c95b09a07d26c7c62742d510665e6ea6168e6e",
              "sha256": "0162b2a26d3225c3e273fc2605947261e05e7a754e55282a4f1b6aa9789871f3",
              "task": "skill_trajectory_summary",
              "total_tokens": 3782
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "cf165c54a5b811a3388926f7125f2755884b940a52a892cc31c80d80144cc099",
              "provider_status": "completed",
              "response_sha256": "471bf0c21cb0f66bbb51452114e34940c0d02da9b5f31ec7673efa0f1f003447",
              "sha256": "45a25003f473d82bab080d49efa156cb9c37aa7f7f24a48c9f894312cbfd805b",
              "task": "skill_trajectory_summary",
              "total_tokens": 3942
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "3ada4685fa4e8b0c1655d095d0cd6c5edec15a2e6882787a315c01d4186f359c",
              "provider_status": "completed",
              "response_sha256": "b3c05a532ab6a453841dc30f173acc436d6fb429cfeecab14465c801ca6326a4",
              "sha256": "87fbc8248129a7509713f91790f8674edd2aa24b63591199f4436807d974bb4d",
              "task": "skill_trajectory_summary",
              "total_tokens": 1831
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "1f4fe2897f6a8abe14ff95446776b3cbae0767e85a00b5aca6a18ca6b5f0dade",
              "provider_status": "completed",
              "response_sha256": "806e8bc28f6669a1daa0a235a8de12cd374c03af92f1475bfea74c1b4536e530",
              "sha256": "1d04a11113c6815eeca3f05659e011a3c0a71feaca3bc767fea8e81b6d5f8dc5",
              "task": "skill_trajectory_summary",
              "total_tokens": 1992
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "779bef0c8969681af089191016f148bf2d219a28da25be9a3019e5c993164c8d",
              "provider_status": "completed",
              "response_sha256": "4a4b4c6f9a6cf934d1fb3ce36c4f504e7beb2185c73d157c36c8a24f2d7e0841",
              "sha256": "d87937c5f53c875ce99b01c6a2b9d06317e8f287be4741bd1b4f6e8b4af80cd7",
              "task": "skill_trajectory_summary",
              "total_tokens": 2616
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "9c12ea23235f809e3da4bca26c4f45c4572d9d821915d823bdac7d1005e82d5c",
              "provider_status": "completed",
              "response_sha256": "4ed4b4d40460b2dfb6939cc9fe25f828fcd6001e41a8c8490ff11b38565813ea",
              "sha256": "8211fd741c3019267f47825e334267bb482a38069bdc21b64f3c8eca2f658a87",
              "task": "skill_patch_propose",
              "total_tokens": 3955
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "31c32e20b9097bcb77c420e2990325730aeb3524b3bc44707802805eb15972f0",
              "provider_status": "completed",
              "response_sha256": "4b12bf954c0d3306aa4c6dc6aa8b2e43fee3d13445c42f74d340ea4cb29bf349",
              "sha256": "7eb7368d4cb7904f30a184b10ce93b775aadb83761573f3bba6c4a6d96788f12",
              "task": "skill_patch_apply",
              "total_tokens": 1547
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 27408,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/update/skill_post/SKILL.md",
          "skill_post_sha256": "6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "4264884af2b6c370fe0c04c84306b3b09f2d7039481dd878607384927fbfd38c",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_2/win_c/update/update_receipt.json",
          "update_receipt_sha256": "f9ff162ce389cdb1a495a83f87ca0d20f1b03923b94c55eadbc9e08c4e346c84"
        }
      },
      "evidence_windows_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/evidence_windows.json",
      "evidence_windows_sha256": "3fe4b64fbba9c94f081be5986c93ee78243ec80daaab187ed27ce2fb07489fe9",
      "pair_summary_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/summary/replicates/e1-agj-01-rep2.json",
      "pair_summary_sha256": "ac14a10c50cd171b6e3eabbe4de9e2c6a6cbdeee1f47162559aa9fdcb384a81b",
      "prefix_compatibility": "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL",
      "replicate_id": 2,
      "source": "inherited_repair1",
      "stream_id": "e1-agj-01",
      "unit_id": "e1-agj-01/rep2"
    },
    {
      "arms": {
        "mrw": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "38e30318a328e296a499fc1d0e8e64c2e3260e27b76cd57b69a2676d84add63c",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/checkpoints/provider_budget.sqlite3",
            "sha256": "a83c6c7de84cfd61339c58b76bf92ce4cc39539542ab70fbf8183a3cb24ff3fb",
            "total_claimed": 108,
            "unit_claimed": {
              "e1-agj-01/rep3/mrw/update": 10,
              "r17-b4-agj-p2/rollout_0": 5,
              "r17-b4-agj-p3/rollout_0": 5,
              "r17-b4-agj-p8/rollout_0": 6,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 4,
              "r17-b4-fmv-p8/rollout_0": 5,
              "r17-b4-ioc-p1/rollout_0": 10,
              "r17-b4-ioc-p4/rollout_0": 6,
              "r17-b4-ioc-p6/rollout_0": 3,
              "r17-b4-msp-p0/rollout_0": 6,
              "r17-b4-msp-p7/rollout_0": 3,
              "r17-b4-msp-p8/rollout_0": 6,
              "r17-b4-ska-p4/rollout_0": 6,
              "r17-b4-ska-p5/rollout_0": 6,
              "r17-b4-ska-p8/rollout_0": 5,
              "r17-b4-tsr-p0/rollout_0": 3,
              "r17-b4-tsr-p6/rollout_0": 8,
              "r17-b4-tsr-p8/rollout_0": 6
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "7bd4fce10599f4fe8de26f19b72378569676df1397addde93eb4e194077a820b",
              "provider_status": "completed",
              "response_sha256": "b348b3b0e083f5d47e7c3521a065b765ea06d8b63b443619f85940031e33a910",
              "sha256": "2a29ad73e0296803f9dd8310cd48229438ea18e4088e9bb0214327c628e9901c",
              "task": "skill_trajectory_summary",
              "total_tokens": 1641
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "6619d317ff645bc8cc5cf8efd7a2faf8827ba0c941ec3a5e1337134b0316b3df",
              "provider_status": "completed",
              "response_sha256": "61f5d41fb11410e3dc639dac49462e41e1b0f2f3be18eba74b4c06acca4d3d7e",
              "sha256": "65fdde41793404433ee6229bab22d111ae956ac33d403df7e065ba439d11ba2d",
              "task": "skill_trajectory_summary",
              "total_tokens": 2047
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "1bbcbb2d4af4bd491b6e89003b5351b656aa983662131cb76e3ff2c0fb6dbb31",
              "provider_status": "completed",
              "response_sha256": "5ed6f839d2c458f67c9e6d976ba4b1bc2dbed95c92dded23e613619e23b1ba99",
              "sha256": "397e7e7b085b7e6a63a2bef39c104ea13298b116c98a541a8c2954ffaf1f4fb5",
              "task": "skill_trajectory_summary",
              "total_tokens": 3950
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d45418ffd0adc6bf882c4da5f98b92eeba03afc5453084ab1f5d4202c2cb1147",
              "provider_status": "completed",
              "response_sha256": "ba3087a42a124deab2a31eb6558e7f4d63b9ed0c15e1417879446f422101c29c",
              "sha256": "9c0ff595d32cc6bdf62f59ff1fa81670291ecccff6192d9ecd7c729857625654",
              "task": "skill_trajectory_summary",
              "total_tokens": 3789
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "cf165c54a5b811a3388926f7125f2755884b940a52a892cc31c80d80144cc099",
              "provider_status": "completed",
              "response_sha256": "dfba3996a8e2477974de66c225e08020f0862dee2d6136b16268fbb337878674",
              "sha256": "b7ae6ea6ac85a07bb5630b979f5948afee26e5005e9dfb71ea2ed8add0e555c3",
              "task": "skill_trajectory_summary",
              "total_tokens": 3911
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a0a12117647c06cb1698e2666a9284805b85aa08971131c251057f989698130d",
              "provider_status": "completed",
              "response_sha256": "d623617e4d466897a30b3b5dac55e545b2e24789410a90d9209ff8330367ccf2",
              "sha256": "bd0bf2811d0c3d186ab0cd03ad971144af126fefa661a264e1a8fb683f7439d7",
              "task": "skill_trajectory_summary",
              "total_tokens": 1776
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "61a0993b780e2d06f22c865385c37b72c05735dcbe8f814f1d8e5728ebc006e9",
              "provider_status": "completed",
              "response_sha256": "68f253e47ff7edbfea5e092dd3446ad58648dae082189ac285747e00c3956cca",
              "sha256": "0c67c5cfa332e56deb1c066d19fd734986ce355364d5fe21eef7d613bba910b8",
              "task": "skill_trajectory_summary",
              "total_tokens": 1992
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "b8f24518f24f3a433ba856b79762d07b3dc1bf4d6169c7d7e6fd51b221aeaf10",
              "provider_status": "completed",
              "response_sha256": "6976ff9baa7f2efd37cbe97624ff6f8097a2233d97be7f51162437d5a56c18f0",
              "sha256": "8ef522b8c34611d5787623bd1c8cd0b7cd24918d017b83572bb3759e72f967cf",
              "task": "skill_trajectory_summary",
              "total_tokens": 2536
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "95e3b6e8e9ae7ce373014fb26f44401973aef7cb59e10a616a2fbf9506f75aaa",
              "provider_status": "completed",
              "response_sha256": "36761e0963786d5c3620ac02276ab1051549e0dd81ee633f29123fffe17188dc",
              "sha256": "94154a1bb64c702a988a143933b34c9f2625c862ce4664e13dbed7e4f0122c40",
              "task": "skill_patch_propose",
              "total_tokens": 4004
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "0ee58de32c011c55d4ada0a326e24cba09d9f20b0e05dad26208577db0a1e8b3",
              "provider_status": "completed",
              "response_sha256": "fc72697656f9965fb9bfad188ccbe66a194b73447c433b046281fdce804ba595",
              "sha256": "49c49f1c05c696422bd1f016938073d6de0182c39201317a8faa2cfa77eeb676",
              "task": "skill_patch_apply",
              "total_tokens": 2199
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 27845,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/update/skill_post/SKILL.md",
          "skill_post_sha256": "b11f21b392915c6f586a060160f718b768be67f3c968c933bda8edf544eebdaa",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "5e3f7958201807bf598539b9712085342378ab08a5009581dac97ee867380711",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/mrw/update/update_receipt.json",
          "update_receipt_sha256": "c186a608bc1315dfa709372176ca347838c409ab77313515653bc838fcb25c03"
        },
        "win_c": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "006ecd0cb43a316a04ab1a733ace6c661fa376a93ec24675aa2b072dbb20e030",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/checkpoints/provider_budget.sqlite3",
            "sha256": "2e8632dc0187c3d3453d0dc33420c48191c5530f3cf7d05e5d5bb3cf4963a7cd",
            "total_claimed": 109,
            "unit_claimed": {
              "e1-agj-01/rep3/win_c/update": 10,
              "r17-b4-agj-p2/rollout_0": 6,
              "r17-b4-agj-p3/rollout_0": 6,
              "r17-b4-agj-p8/rollout_0": 5,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 5,
              "r17-b4-fmv-p8/rollout_0": 6,
              "r17-b4-ioc-p1/rollout_0": 6,
              "r17-b4-ioc-p4/rollout_0": 5,
              "r17-b4-ioc-p6/rollout_0": 6,
              "r17-b4-msp-p0/rollout_0": 8,
              "r17-b4-msp-p7/rollout_0": 7,
              "r17-b4-msp-p8/rollout_0": 9,
              "r17-b4-ska-p4/rollout_0": 3,
              "r17-b4-ska-p5/rollout_0": 7,
              "r17-b4-ska-p8/rollout_0": 5,
              "r17-b4-tsr-p0/rollout_0": 5,
              "r17-b4-tsr-p6/rollout_0": 2,
              "r17-b4-tsr-p8/rollout_0": 3
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a68d4d6a65de9ee6c3b15eb1a741d7fac8d4411b4026f5c70d49593383c52daf",
              "provider_status": "completed",
              "response_sha256": "a386d1c0ab767b168ffe0d55f7ead341ad43fde80ea1d36bb914ee4383e34717",
              "sha256": "bbe1862272ac68e4a5e581f1b3d1cbefc4dba48a1d79d56507fa531637165528",
              "task": "skill_trajectory_summary",
              "total_tokens": 1742
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "003805d22bcea74b97d508d9595201bcd63bfe886d080f49bd2026029957b15d",
              "provider_status": "completed",
              "response_sha256": "da5c62722a51a715240171e4bac091ade2f8bc49a5e11553bb2c4b75b1a94b8d",
              "sha256": "18050de43f490592c0a7fc3dae005f2eaaeae8291e8de19447a1cfb2f8af2119",
              "task": "skill_trajectory_summary",
              "total_tokens": 2127
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "1bbcbb2d4af4bd491b6e89003b5351b656aa983662131cb76e3ff2c0fb6dbb31",
              "provider_status": "completed",
              "response_sha256": "b4e24942fb6b204561adb8fbf5df1803768ec46573007d0f937a847fd3a96cca",
              "sha256": "370142097fe9562457466b5394e86b2ad760bdcfe0d1dd39ecd2269895cc47cc",
              "task": "skill_trajectory_summary",
              "total_tokens": 3959
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d45418ffd0adc6bf882c4da5f98b92eeba03afc5453084ab1f5d4202c2cb1147",
              "provider_status": "completed",
              "response_sha256": "0f4dc57d727fe3c6896904b8056b80dbc438f2ffc3fc43b1e92a83eb56214aa8",
              "sha256": "4d73a6db9a735277f8bcec3f2c66f8084a223ad37e33fc53a1571d4998736692",
              "task": "skill_trajectory_summary",
              "total_tokens": 3818
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "cf165c54a5b811a3388926f7125f2755884b940a52a892cc31c80d80144cc099",
              "provider_status": "completed",
              "response_sha256": "591b3fda590e7d5e5ee4e72df05a44ca229d33565649954bec43de6ce581be70",
              "sha256": "0e3f22153f841d11a1d0d8e7dbaff2a363c25c748784f0f3140913560c7528df",
              "task": "skill_trajectory_summary",
              "total_tokens": 3937
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "3ada4685fa4e8b0c1655d095d0cd6c5edec15a2e6882787a315c01d4186f359c",
              "provider_status": "completed",
              "response_sha256": "50c3fca89f6b3c1267443fa100f8c81297119f1b556761b4803550978b0883b9",
              "sha256": "df47afec534870e92dde95a0e9ef42b85d550b82830c694c5aa5fed3b2bf97b6",
              "task": "skill_trajectory_summary",
              "total_tokens": 1890
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "1f4fe2897f6a8abe14ff95446776b3cbae0767e85a00b5aca6a18ca6b5f0dade",
              "provider_status": "completed",
              "response_sha256": "73375cb9ad3ec1c0399ce820b9e74b1d52eab7eaec445213a9a76aa5ce376139",
              "sha256": "d3c88a4823831e77b35e2c40034d9e867838e4b1df8d324b90dbaf488acdfe1b",
              "task": "skill_trajectory_summary",
              "total_tokens": 1978
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "779bef0c8969681af089191016f148bf2d219a28da25be9a3019e5c993164c8d",
              "provider_status": "completed",
              "response_sha256": "74b5d440f20707b29833235d6674922617d65f36617af0eba7ead072a3615be8",
              "sha256": "0cdb79c1e6e8770115da3fc3d5234377f1ada665b307550f0168bf7aa74a5783",
              "task": "skill_trajectory_summary",
              "total_tokens": 2629
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "8ec1195511dd88569793480f9cef46ea4d80a2f4dd8b0d32b6e95099e48f2b02",
              "provider_status": "completed",
              "response_sha256": "9fdf23195b912523d91c291228863000af944ff7fd5761fb8e48f88d6c6192af",
              "sha256": "44de3fd66688c00fee087173403d0c9b5182d7cb1bdbabd9fcaedd4b3c426275",
              "task": "skill_patch_propose",
              "total_tokens": 4059
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "6f89b6f782a79ca979a4c3fe8514caab482c19dd58f6223b4ccbbcf9501c0e96",
              "provider_status": "completed",
              "response_sha256": "4b12bf954c0d3306aa4c6dc6aa8b2e43fee3d13445c42f74d340ea4cb29bf349",
              "sha256": "0461c3e05065cb7ec4ddab44c15e6341e9eeca2d375cd132f8ccddf1c24b0fcb",
              "task": "skill_patch_apply",
              "total_tokens": 1477
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 27616,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/update/skill_post/SKILL.md",
          "skill_post_sha256": "6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "842d17f5a05de197b073ad0c6e14e97d42a5deb0e751362fdaae3ccbeae08fc0",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/replicate_3/win_c/update/update_receipt.json",
          "update_receipt_sha256": "209e22c14d6c393374ae363418cd4cb9d8de0744bb779251ec0e945c1cf9e9dc"
        }
      },
      "evidence_windows_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-agj-01/evidence_windows.json",
      "evidence_windows_sha256": "3fe4b64fbba9c94f081be5986c93ee78243ec80daaab187ed27ce2fb07489fe9",
      "pair_summary_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/summary/replicates/e1-agj-01-rep3.json",
      "pair_summary_sha256": "c4d6720ca66ff3517e482a7ece9d67a642b79505a2215c3bb3bac441d0e78adc",
      "prefix_compatibility": "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL",
      "replicate_id": 3,
      "source": "inherited_repair1",
      "stream_id": "e1-agj-01",
      "unit_id": "e1-agj-01/rep3"
    },
    {
      "arms": {
        "mrw": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "30232ac0dd7b723a994bbabf810705c6b84bdd295159f7f74986e3eb97b72591",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/checkpoints/provider_budget.sqlite3",
            "sha256": "782d512d06f4b5229cc7111db8828fc32e727a0422867a5870ef56db3eff03ad",
            "total_claimed": 167,
            "unit_claimed": {
              "e1-fmv-00/rep0/mrw/update": 10,
              "r17-b4-agj-p2/rollout_0": 8,
              "r17-b4-agj-p3/rollout_0": 10,
              "r17-b4-agj-p8/rollout_0": 9,
              "r17-b4-fmv-p1/rollout_0": 9,
              "r17-b4-fmv-p2/rollout_0": 8,
              "r17-b4-fmv-p8/rollout_0": 9,
              "r17-b4-ioc-p1/rollout_0": 7,
              "r17-b4-ioc-p4/rollout_0": 9,
              "r17-b4-ioc-p6/rollout_0": 10,
              "r17-b4-msp-p0/rollout_0": 9,
              "r17-b4-msp-p7/rollout_0": 10,
              "r17-b4-msp-p8/rollout_0": 10,
              "r17-b4-ska-p4/rollout_0": 9,
              "r17-b4-ska-p5/rollout_0": 10,
              "r17-b4-ska-p8/rollout_0": 8,
              "r17-b4-tsr-p0/rollout_0": 7,
              "r17-b4-tsr-p6/rollout_0": 7,
              "r17-b4-tsr-p8/rollout_0": 8
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "02fa91fb404136c600e2bf55c985f876b480c973a002941be3d80f90580d5339",
              "provider_status": "completed",
              "response_sha256": "45fea1db31f06eb4b982b207b6b0d57e235cdd90018b4bb1407877fdea7dbde9",
              "sha256": "700a65e116c41b78c75408922b5ab65216098a794898990ccbb9060d48cc806d",
              "task": "skill_trajectory_summary",
              "total_tokens": 2015
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "3ebcbd7e70faf12b578dc2d574ac1d3a75014bfc9875683682febe664c166ccf",
              "provider_status": "completed",
              "response_sha256": "b1797aab5d7ffaf3171588075bc201958fdf4734003d94122cf815dadcb4c025",
              "sha256": "5bd9217f8fd6dc9c79ed91ff031d7671570ffa7177454267a6d302fb28e18734",
              "task": "skill_trajectory_summary",
              "total_tokens": 2058
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "426af7b9b0bac4b9ece4f3d032dfbbc73406898e37a1f5039474b87afefb1d56",
              "provider_status": "completed",
              "response_sha256": "aef91ed1fa2dadb0df11cce64d837c29353538c754bac9c7a8caa8debd2fdc50",
              "sha256": "bbb5b97877690d3e71696df35cd27bbb4ee72a25ba667c478d37cec73355d92b",
              "task": "skill_trajectory_summary",
              "total_tokens": 1981
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "68b823d674a410758bc070c6310c0d28ae1ccfd9c1020f77bb9e96f09baab4ba",
              "provider_status": "completed",
              "response_sha256": "81d3e697f4fd708071ec99d9e90c64c4b30211823cdea5864f34269ccf8fbbc8",
              "sha256": "c06e9b1f187d699b58e67cb9d9f8bbbd2de735b9dc415d7e87e547adf34f715e",
              "task": "skill_trajectory_summary",
              "total_tokens": 2161
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a97dad740bfb3e1f973357832e6ce212c2abf2622cf3dcf536ae3dc5eced2592",
              "provider_status": "completed",
              "response_sha256": "f2f1ba3ac345b8d40830fd0930a864aee0926c27bd5bfd30315a8238e6ca4e1d",
              "sha256": "1e9c1ae9d717dc5ea04dfba21098d2ce51ce363b304e7ad55b01074eedc38f75",
              "task": "skill_trajectory_summary",
              "total_tokens": 1677
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c3f6824a50b77269ff1099d87421e16b86a19f990f0ac0a95c5ff23d2ab40c1d",
              "provider_status": "completed",
              "response_sha256": "37d1600544e1d15bc9b6bdc91d1e99567c08ead924f969d15386bad5b5d073df",
              "sha256": "ecdf35d1a4c68052585a568e959226bd247e6428a6d6a1b1581b550636ca7dcb",
              "task": "skill_trajectory_summary",
              "total_tokens": 1978
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "f8c229e052ff8416684f4cea46873a7f4051451dc93e7ea61e88949b9687f9e4",
              "provider_status": "completed",
              "response_sha256": "ba752fd4e76d4dcf121db381177e776e26e0552dd4037ef31dfee677ab6349a6",
              "sha256": "505aba0d569b89a8bb5bcbfb2da920c272fb842f85274479a1982916ee83084a",
              "task": "skill_trajectory_summary",
              "total_tokens": 1618
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "f98001396d207ae59f1661154c017aafbd5149b35f9bf73811c1966f6df43ced",
              "provider_status": "completed",
              "response_sha256": "b51b6a0eb2a0a4503516b7985bd0dd894864bce4bca8ffe4cc03ffa2a87e5c99",
              "sha256": "66f116f16bde481e7062ace5aabfe234cd9413dac45487b4d82029a69c4b9a7a",
              "task": "skill_trajectory_summary",
              "total_tokens": 1951
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "e37816e2dd83f7560cbcb51a6e3b3ea0736abdd424986f1511c33ff50b87a3ce",
              "provider_status": "completed",
              "response_sha256": "fa4ab776c1143a38e0c31340a9ecfcd1e9ff3a63e550a21ed54052b7863a4fd8",
              "sha256": "e4b0231429131def60f5eced889cd9ee7a61bd19eae5c10f3bdb1d5cec4df857",
              "task": "skill_patch_propose",
              "total_tokens": 3942
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "70235da15f2238adb60d672d01e9c284a2d563ce1f2051d22a08cb9c3bc456cd",
              "provider_status": "completed",
              "response_sha256": "1ca8903b7f5b4d45feb7f187327902b1c674914cad6a0d30a1c3b55997beb4be",
              "sha256": "cda6875c55ab7004e8cf8eb600a02ee985b86b297b15e7e46fa111af46f26a37",
              "task": "skill_patch_apply",
              "total_tokens": 2483
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 21864,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/update/skill_post/SKILL.md",
          "skill_post_sha256": "bbbb03f7ab295f4d62db5f7a862b6a378873e71f03490a40b6ae39d6fa4428aa",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "74109479ff30bb349643b0ca05b27ff5b7477064dc7525c1016728293e017684",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/mrw/update/update_receipt.json",
          "update_receipt_sha256": "e0678a302b1b240e0a311abd39e34720332844bd9c446ee95f7ee4650860ff10"
        },
        "win_c": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "39205b9ab508e09b76dd670c433a8ca2e6e55cb7f6547022a8f02d423de2b014",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/checkpoints/provider_budget.sqlite3",
            "sha256": "5457fd696aa10d471942d73ee0c5cd44f86474506ae29c8e6cfd413835e614cc",
            "total_claimed": 123,
            "unit_claimed": {
              "e1-fmv-00/rep0/win_c/update": 10,
              "r17-b4-agj-p2/rollout_0": 6,
              "r17-b4-agj-p3/rollout_0": 4,
              "r17-b4-agj-p8/rollout_0": 8,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 6,
              "r17-b4-fmv-p8/rollout_0": 5,
              "r17-b4-ioc-p1/rollout_0": 7,
              "r17-b4-ioc-p4/rollout_0": 5,
              "r17-b4-ioc-p6/rollout_0": 6,
              "r17-b4-msp-p0/rollout_0": 7,
              "r17-b4-msp-p7/rollout_0": 3,
              "r17-b4-msp-p8/rollout_0": 10,
              "r17-b4-ska-p4/rollout_0": 5,
              "r17-b4-ska-p5/rollout_0": 6,
              "r17-b4-ska-p8/rollout_0": 9,
              "r17-b4-tsr-p0/rollout_0": 5,
              "r17-b4-tsr-p6/rollout_0": 10,
              "r17-b4-tsr-p8/rollout_0": 6
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "5a11533b62ab949fdb17f4ba82264cd7f61131e5cf641cf6a032ebe11324c4a3",
              "provider_status": "completed",
              "response_sha256": "f6f1e8d1cd0cd45752f10ba2dbae47606d2b981af68d8afbf66f1e1a5fb869b4",
              "sha256": "6bd4e98bc44bd3118fc0ce5b71525e64273d0580e9838def9cc32cc3a705cc94",
              "task": "skill_trajectory_summary",
              "total_tokens": 2033
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "3465577b1d60375b6cbc4b141d725fdceafddb73731d005cb8140b7b35353746",
              "provider_status": "completed",
              "response_sha256": "10e3e885c2cef1f91a19d36532def9e44d3935f8dc5f978c5755dca50acd683b",
              "sha256": "c47fad69031f03191918dd81fe5b3c08b22074b09bc52902984b357a778fa492",
              "task": "skill_trajectory_summary",
              "total_tokens": 2118
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "02de21f70c664b4839b5bf2c54be41697c7450b0a192a8f2513de7c6b70ed2b6",
              "provider_status": "completed",
              "response_sha256": "42a5fb46089d427d02699476bf06c042133b987f679a3154af18aec5a7607417",
              "sha256": "4a4a90caadcb4f64a6611fc88d4351d5e4d6d46dc7beb70d570114e7f49ff0ff",
              "task": "skill_trajectory_summary",
              "total_tokens": 2048
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "adc9198614d74b076fdfa302f1f4fc9caef8b42c3a63630d5f5a75ad9b630b78",
              "provider_status": "completed",
              "response_sha256": "81065783f1555557399c911affa5ec42d97cd730307965c1ac11c2d80f0fc5fa",
              "sha256": "71a1bb859106a830cfe3db9d80a3d63b239668ff5e4d8b27ab71345f16fd935b",
              "task": "skill_trajectory_summary",
              "total_tokens": 2035
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "188bcac0fd9aca2ea0dcc2835956e8b6835f1df234902b5ac47c50588d7b80a3",
              "provider_status": "completed",
              "response_sha256": "c347f9d4307d84486d486501bbbb599d53f42a2ca5f2d88a8a3bac0902060c12",
              "sha256": "c9e63d9b8fe4157ed15789075c2fb81f4842f2c3998c97e6015e3821db1b52b4",
              "task": "skill_trajectory_summary",
              "total_tokens": 1788
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d7fdfabbcce57cf84196913d8e96cdc72770ee316302181dd13d5ec597d7116d",
              "provider_status": "completed",
              "response_sha256": "3ff48bd1da77951e523c21d5341211ae0675b838dbca3f9727b74bc9b186e2d0",
              "sha256": "eeb3fc92539dce2dfadf06bbd09a58236301e6bcd961554a16accea05b267c66",
              "task": "skill_trajectory_summary",
              "total_tokens": 2055
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "2a1ba9b796bd50a3037416a192017b43de4419d384b96dbab8db1ca8bc7e2994",
              "provider_status": "completed",
              "response_sha256": "cecf016b9a3073eed02dafa17a0d5029fb80ea3e25d3b97fce422df780925ec9",
              "sha256": "1a703512fcf59cde59d839f42de2a01ee23785002be65178624253caa4cabf77",
              "task": "skill_trajectory_summary",
              "total_tokens": 1733
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "2adbc4b9517285bedd0b1f54d55591b453ad545b88d7f3d176cba49cd422e8db",
              "provider_status": "completed",
              "response_sha256": "6e40f3a8be81f394a0b3e5c9a11c481ba6a5942d0512a0be7d978138e8b698cc",
              "sha256": "8bbdff984fb12f003218be89b94c435e2e800700d99195ad81365d86713e2dbd",
              "task": "skill_trajectory_summary",
              "total_tokens": 1988
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "48fc12179c5bf17d19a9dbe49ca8eb61db04cb4e69315f1728ddf36d60e4006b",
              "provider_status": "completed",
              "response_sha256": "abd0048b337c9fd7b90e22c8db1e91f2ee26457d9c15ba02494a3059fef9d583",
              "sha256": "281c8cbfa99777eae3336e83b7b2f069924479413e88d553fda8b70baa394b7e",
              "task": "skill_patch_propose",
              "total_tokens": 3903
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "b427cd86cab3917cfdf6416239b79db6faf14fd58d878786635849e5424ade4a",
              "provider_status": "completed",
              "response_sha256": "4b12bf954c0d3306aa4c6dc6aa8b2e43fee3d13445c42f74d340ea4cb29bf349",
              "sha256": "6409d12078f6f49535c2ec7ff7d5ad0a03a21ccae56d76dbd5de63482468221f",
              "task": "skill_patch_apply",
              "total_tokens": 1514
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 21215,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/update/skill_post/SKILL.md",
          "skill_post_sha256": "6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "c01586198795d8df57b467920e52f65588224aa6d58b1edac1832789e1ccd248",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_0/win_c/update/update_receipt.json",
          "update_receipt_sha256": "cf1aaa341280e3d0421f468bbb2195295598b94378cbcf1ab3f72d2e42aabbc9"
        }
      },
      "evidence_windows_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/evidence_windows.json",
      "evidence_windows_sha256": "ea141c4b8ec4f0d592f450fb82c9e3723b9077b9f24edb5215f1e6885f3ce0b3",
      "pair_summary_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/summary/replicates/e1-fmv-00-rep0.json",
      "pair_summary_sha256": "d33c6c2be7f28c7d109b11e2180670b1bc9ee7b44e900055a67045a6ef1629bc",
      "prefix_compatibility": "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL",
      "replicate_id": 0,
      "source": "inherited_repair1",
      "stream_id": "e1-fmv-00",
      "unit_id": "e1-fmv-00/rep0"
    },
    {
      "arms": {
        "mrw": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "38921a7fc05347506f115dec1cff1c8d5b5a355d0a0174931985d491ad0ccb06",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/checkpoints/provider_budget.sqlite3",
            "sha256": "2403de6f136482fdefbae6b8e9fbb5b4a9a380de34853d4d29ea0b5f959766d8",
            "total_claimed": 132,
            "unit_claimed": {
              "e1-fmv-00/rep1/mrw/update": 10,
              "r17-b4-agj-p2/rollout_0": 8,
              "r17-b4-agj-p3/rollout_0": 8,
              "r17-b4-agj-p8/rollout_0": 7,
              "r17-b4-fmv-p1/rollout_0": 8,
              "r17-b4-fmv-p2/rollout_0": 6,
              "r17-b4-fmv-p8/rollout_0": 6,
              "r17-b4-ioc-p1/rollout_0": 7,
              "r17-b4-ioc-p4/rollout_0": 8,
              "r17-b4-ioc-p6/rollout_0": 4,
              "r17-b4-msp-p0/rollout_0": 7,
              "r17-b4-msp-p7/rollout_0": 7,
              "r17-b4-msp-p8/rollout_0": 10,
              "r17-b4-ska-p4/rollout_0": 4,
              "r17-b4-ska-p5/rollout_0": 8,
              "r17-b4-ska-p8/rollout_0": 7,
              "r17-b4-tsr-p0/rollout_0": 4,
              "r17-b4-tsr-p6/rollout_0": 7,
              "r17-b4-tsr-p8/rollout_0": 6
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "02fa91fb404136c600e2bf55c985f876b480c973a002941be3d80f90580d5339",
              "provider_status": "completed",
              "response_sha256": "974339d278f2f882544944f1211a27a5a6e046a5586ab76e8a7d433054e7b7ec",
              "sha256": "f4c98fd8ea6db49a3ea2a9a04fc2b351a18e2e1e5ed7965f0c4e2d5b8ba1b0ca",
              "task": "skill_trajectory_summary",
              "total_tokens": 2032
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "3ebcbd7e70faf12b578dc2d574ac1d3a75014bfc9875683682febe664c166ccf",
              "provider_status": "completed",
              "response_sha256": "fba66b5d9f4f0803192cbe26cf9c27a2fafcaa8d4721e425018c322326a7eae0",
              "sha256": "78085ba4dd3e6245656166e8fe1627d3aff1ed5132d993108fd5fd9a75a4ef45",
              "task": "skill_trajectory_summary",
              "total_tokens": 2053
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "426af7b9b0bac4b9ece4f3d032dfbbc73406898e37a1f5039474b87afefb1d56",
              "provider_status": "completed",
              "response_sha256": "9f492ab7d169ae762863937fddbebab7f65aee848012b5f589d63f931b5d95c8",
              "sha256": "e44aaa2cdb794e8ec383dc771bb138c0a8fcb4492fd8606eec21509ea69daeb3",
              "task": "skill_trajectory_summary",
              "total_tokens": 2028
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "68b823d674a410758bc070c6310c0d28ae1ccfd9c1020f77bb9e96f09baab4ba",
              "provider_status": "completed",
              "response_sha256": "fbc2d5b64727ee2cb0d8af60db89aa4e5e8c31ea5518b3bd073c24fb37856b33",
              "sha256": "939611b6c4fbcd94dfe3c0670e75456d7b9044cbb1b694a736bdc35b83e0fa3d",
              "task": "skill_trajectory_summary",
              "total_tokens": 2190
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a97dad740bfb3e1f973357832e6ce212c2abf2622cf3dcf536ae3dc5eced2592",
              "provider_status": "completed",
              "response_sha256": "2bed0c3784f61b258edd4cd8856a8a0f203d1bc1d7f7e92a449f22d8bd0003dc",
              "sha256": "5183025d990254221956617fdf6a2c53d5c89e9b8ab78ebf2bbb266f4dcd7f84",
              "task": "skill_trajectory_summary",
              "total_tokens": 1669
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c3f6824a50b77269ff1099d87421e16b86a19f990f0ac0a95c5ff23d2ab40c1d",
              "provider_status": "completed",
              "response_sha256": "a5d668b1a71b00d3acbd216245ed12a81af298535a81a108475f7ef1b5977110",
              "sha256": "2c704eb75f52a78f24bbbd03246928897f7e8d88657bbc424bb32dc1a789a5e5",
              "task": "skill_trajectory_summary",
              "total_tokens": 2013
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "f8c229e052ff8416684f4cea46873a7f4051451dc93e7ea61e88949b9687f9e4",
              "provider_status": "completed",
              "response_sha256": "78e1333a6ed62f13ea424b88c3c07cf7328be9cc84cb62ab05517ec97c200bc5",
              "sha256": "200d88d2c9b862039c5367dfd40ca138aa5e6b254daaa038bd53c016d23dc1af",
              "task": "skill_trajectory_summary",
              "total_tokens": 1658
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "f98001396d207ae59f1661154c017aafbd5149b35f9bf73811c1966f6df43ced",
              "provider_status": "completed",
              "response_sha256": "c4a803b7d60852a54cdc85a65d98f088c3df17b682fa7a6c3fd6d8837bee8a72",
              "sha256": "cafcbcd91529e5cb89e7348fd937bc61095d09e3b68d85927e30ccc439620f77",
              "task": "skill_trajectory_summary",
              "total_tokens": 2009
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "f52470247b795832f63625fead4f42cd4a005807ae388f9661ba6ecbf19f33bb",
              "provider_status": "completed",
              "response_sha256": "aa6cd6b7702ec45cfe9f34991573567b8befc1a1487b80e22cb32bbfaea0bac8",
              "sha256": "a8b3be13175d11383e8ac0e6263f274c32df199545f5c37880539a53c2483edf",
              "task": "skill_patch_propose",
              "total_tokens": 4130
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "e2dc2a4ade9aad8ec7a39138691a63e2dfb6a7776e377f728e1d2b564ca9dbe8",
              "provider_status": "completed",
              "response_sha256": "120f2bdcaf5e4d6b75b7dace95138812646b78a8d640d6f7f1448238a0df635b",
              "sha256": "06f28d7e7e53383e018fae3cabf3f7be1861ead3346eb7d163774512ce39dbb0",
              "task": "skill_patch_apply",
              "total_tokens": 2310
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 22092,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/update/skill_post/SKILL.md",
          "skill_post_sha256": "741b49cd89c05ec0bce5d20e43aabe0463a09b446af19a271bf774ec441bd75d",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "d36f7c7b07d70c689871562f038bfb6dabe7257dddb4ce2e873ed6ec731353a1",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/mrw/update/update_receipt.json",
          "update_receipt_sha256": "c92ed5f74cd67c56b8556650e289531539f8f7d58e14693589148ee203652933"
        },
        "win_c": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "c28d0c177ff49ff6a0c5377deac8c83ed439f0b8acf794033c314c34b354cd74",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/checkpoints/provider_budget.sqlite3",
            "sha256": "f80358b50d511dd71997819ba2a4439f787cd4b6a578e713c9ff5dc159ab8589",
            "total_claimed": 115,
            "unit_claimed": {
              "e1-fmv-00/rep1/win_c/update": 10,
              "r17-b4-agj-p2/rollout_0": 6,
              "r17-b4-agj-p3/rollout_0": 7,
              "r17-b4-agj-p8/rollout_0": 6,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 5,
              "r17-b4-fmv-p8/rollout_0": 5,
              "r17-b4-ioc-p1/rollout_0": 2,
              "r17-b4-ioc-p4/rollout_0": 5,
              "r17-b4-ioc-p6/rollout_0": 7,
              "r17-b4-msp-p0/rollout_0": 3,
              "r17-b4-msp-p7/rollout_0": 3,
              "r17-b4-msp-p8/rollout_0": 10,
              "r17-b4-ska-p4/rollout_0": 7,
              "r17-b4-ska-p5/rollout_0": 7,
              "r17-b4-ska-p8/rollout_0": 9,
              "r17-b4-tsr-p0/rollout_0": 6,
              "r17-b4-tsr-p6/rollout_0": 6,
              "r17-b4-tsr-p8/rollout_0": 6
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "5a11533b62ab949fdb17f4ba82264cd7f61131e5cf641cf6a032ebe11324c4a3",
              "provider_status": "completed",
              "response_sha256": "389c52236d69c7d00e4f4992d33c6f1afc29d216e4323f347479e2da53222584",
              "sha256": "2236e0d3381ecd3304db766a5028cff1a09ea78bdf5483333030c0d0cb501e8a",
              "task": "skill_trajectory_summary",
              "total_tokens": 2024
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "3465577b1d60375b6cbc4b141d725fdceafddb73731d005cb8140b7b35353746",
              "provider_status": "completed",
              "response_sha256": "307cf0db26c0d4b9e414dd53c1381b38434ee24dfaf3f62e61216f3743188577",
              "sha256": "11f71e9349c298b1e7e1a33fe97718f40ee2c458cec9791d6e1e7d9c60052e90",
              "task": "skill_trajectory_summary",
              "total_tokens": 2082
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "02de21f70c664b4839b5bf2c54be41697c7450b0a192a8f2513de7c6b70ed2b6",
              "provider_status": "completed",
              "response_sha256": "534e872b3dff10d983a469ea565a371b75ad7c57dfcee682b4dd21e563580503",
              "sha256": "87f6d6b8395f55738c96c9667b5bc7a502f3d7fb30d6b88d19453d104ea84d7b",
              "task": "skill_trajectory_summary",
              "total_tokens": 2081
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "adc9198614d74b076fdfa302f1f4fc9caef8b42c3a63630d5f5a75ad9b630b78",
              "provider_status": "completed",
              "response_sha256": "86113fd4673b2b1e802f11a24379176601de7df394e0edd71634405bcdb17ac5",
              "sha256": "335bd07eb00a98d967aa4f11fe3cbed123820a54ce7ee95b70f6b6bcdb64c9c8",
              "task": "skill_trajectory_summary",
              "total_tokens": 2035
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "188bcac0fd9aca2ea0dcc2835956e8b6835f1df234902b5ac47c50588d7b80a3",
              "provider_status": "completed",
              "response_sha256": "e2503b3ea00b6d49fb3e703817ba4d435255271408bd5fe4d086f32e8dd695ed",
              "sha256": "33220cba28bb457d55283017c8a690bda1ee21fbffd24ae6d65da9b388387259",
              "task": "skill_trajectory_summary",
              "total_tokens": 1753
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d7fdfabbcce57cf84196913d8e96cdc72770ee316302181dd13d5ec597d7116d",
              "provider_status": "completed",
              "response_sha256": "375f24ad25ace032d09f5155cfd62e0915158063f47b3d3d3b411da5787ab45e",
              "sha256": "389f8d950b116aa68607ca2e5f1de28ca99b9345cffaa2d2ffaa99974049edfe",
              "task": "skill_trajectory_summary",
              "total_tokens": 2047
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "2a1ba9b796bd50a3037416a192017b43de4419d384b96dbab8db1ca8bc7e2994",
              "provider_status": "completed",
              "response_sha256": "c4c3403afe451ca54f8d715465d3a3823c06e2290feef4df14c6bc67b6e5046b",
              "sha256": "9b23d4df8f9148ae1eaf55c9583dff467b8670fa40ded717738fc6b5d6fb4483",
              "task": "skill_trajectory_summary",
              "total_tokens": 1716
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "2adbc4b9517285bedd0b1f54d55591b453ad545b88d7f3d176cba49cd422e8db",
              "provider_status": "completed",
              "response_sha256": "9e6f9f8e05d0afef645261a9c17e1ee9994983cd63f3b3592dc8cd8d143999e6",
              "sha256": "15d031cfc28cc98e37805190ceb72f21a589ee55b6e436e222c54146d38be170",
              "task": "skill_trajectory_summary",
              "total_tokens": 2015
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "fce047f9b5ecff4d588e2d35c76dfe911d75188781a2687d07622f5e38fc0588",
              "provider_status": "completed",
              "response_sha256": "bb1c61761d5ae4ab23f3debbe6256c9515958bc0c51097e3cc34c50d5ad4b8f5",
              "sha256": "526fb0c343e2c39f11dc045921fa2f9e58bb2ca2be894ce7badd2abd7e602d06",
              "task": "skill_patch_propose",
              "total_tokens": 4329
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "c2cde9cab6c9ad4117e25088c959244efdf3178f0b45b95d4f853cd18c915289",
              "provider_status": "completed",
              "response_sha256": "2524b03062ceb386775ca93b2deec1ad2b63012a144ef33c0801276c9d7e646f",
              "sha256": "87c7df31033e1bd761462c0f0b4ca5f18bd4e20ba63f9d80a96e4ab185950f42",
              "task": "skill_patch_apply",
              "total_tokens": 2394
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 22476,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/update/skill_post/SKILL.md",
          "skill_post_sha256": "e9c09e04c247d6defcb789a852ccab6de3185ab0931a41b1290a31b596734a27",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "92cbd38255b363af9b4d9c088895187f2d92cfcd3797745d2208fe9039b36726",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_1/win_c/update/update_receipt.json",
          "update_receipt_sha256": "74b306f068148370bc388e9c6b26f4f8156e445ff3390ce35ef034c34552d3f3"
        }
      },
      "evidence_windows_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/evidence_windows.json",
      "evidence_windows_sha256": "ea141c4b8ec4f0d592f450fb82c9e3723b9077b9f24edb5215f1e6885f3ce0b3",
      "pair_summary_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/summary/replicates/e1-fmv-00-rep1.json",
      "pair_summary_sha256": "00619f7c1925de9b9959cf7a61d62d226f6b3f61626b3f01bc769bec3ecc1343",
      "prefix_compatibility": "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL",
      "replicate_id": 1,
      "source": "inherited_repair1",
      "stream_id": "e1-fmv-00",
      "unit_id": "e1-fmv-00/rep1"
    },
    {
      "arms": {
        "mrw": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "4d8d6c6ae93e67e77247404ebecd6a7bdfb17c2e58ffa3b59d2c30db188e6ad4",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/checkpoints/provider_budget.sqlite3",
            "sha256": "77bbf354da62f49873364b5d5fd1ab7f04f6ab50db37c2b813dd74dcf83ff7c8",
            "total_claimed": 118,
            "unit_claimed": {
              "e1-fmv-00/rep2/mrw/update": 10,
              "r17-b4-agj-p2/rollout_0": 6,
              "r17-b4-agj-p3/rollout_0": 3,
              "r17-b4-agj-p8/rollout_0": 7,
              "r17-b4-fmv-p1/rollout_0": 6,
              "r17-b4-fmv-p2/rollout_0": 4,
              "r17-b4-fmv-p8/rollout_0": 3,
              "r17-b4-ioc-p1/rollout_0": 10,
              "r17-b4-ioc-p4/rollout_0": 6,
              "r17-b4-ioc-p6/rollout_0": 7,
              "r17-b4-msp-p0/rollout_0": 7,
              "r17-b4-msp-p7/rollout_0": 8,
              "r17-b4-msp-p8/rollout_0": 4,
              "r17-b4-ska-p4/rollout_0": 5,
              "r17-b4-ska-p5/rollout_0": 3,
              "r17-b4-ska-p8/rollout_0": 10,
              "r17-b4-tsr-p0/rollout_0": 7,
              "r17-b4-tsr-p6/rollout_0": 6,
              "r17-b4-tsr-p8/rollout_0": 6
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "02fa91fb404136c600e2bf55c985f876b480c973a002941be3d80f90580d5339",
              "provider_status": "completed",
              "response_sha256": "a09fea08440fbf66059ba7ed3a9ce5d7b3c0f9dd548224463f05ef1463fe3ba7",
              "sha256": "3c3b793f876742b6e1a9b2238db1c0194764b04db4d4ec7348b1c6cddf92ca06",
              "task": "skill_trajectory_summary",
              "total_tokens": 2032
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "3ebcbd7e70faf12b578dc2d574ac1d3a75014bfc9875683682febe664c166ccf",
              "provider_status": "completed",
              "response_sha256": "0f4d47c2341599a10eee7465729323df1b4d25a7b2f8832eead30a24029a90c5",
              "sha256": "f84d71acc76f4a7b8116116e1ba4320fdde33e69b637bafde19be438748baf9f",
              "task": "skill_trajectory_summary",
              "total_tokens": 2007
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "426af7b9b0bac4b9ece4f3d032dfbbc73406898e37a1f5039474b87afefb1d56",
              "provider_status": "completed",
              "response_sha256": "0dabe4367b06ff5bfc3ca195aaa7a422c5970ef3bc57eaf6de7394a970bf3a94",
              "sha256": "370a8b5d12a6a0345d9664f4050be42ef092deefa12508a3f91e80828a266fa5",
              "task": "skill_trajectory_summary",
              "total_tokens": 2057
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "68b823d674a410758bc070c6310c0d28ae1ccfd9c1020f77bb9e96f09baab4ba",
              "provider_status": "completed",
              "response_sha256": "facf7f934e4b044806da482b5c96abaa920196704f1cbf6f2785c759488852bd",
              "sha256": "8b2871767ba0015afc69dcfd619c997aa24357bf852ddd92a6345494517f1983",
              "task": "skill_trajectory_summary",
              "total_tokens": 2131
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a97dad740bfb3e1f973357832e6ce212c2abf2622cf3dcf536ae3dc5eced2592",
              "provider_status": "completed",
              "response_sha256": "f62f97b03cf689a4a1bc172f0881b8be1bdb81c2a99d199de459f797edd6bee9",
              "sha256": "f6a7730a8f3c18928147c3de7b1917be86fb394cec0f1a5a144cd46639844188",
              "task": "skill_trajectory_summary",
              "total_tokens": 1689
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c3f6824a50b77269ff1099d87421e16b86a19f990f0ac0a95c5ff23d2ab40c1d",
              "provider_status": "completed",
              "response_sha256": "2877d676e94d897b1218fa334a748480d31654154adbb910211f47ec1b22df03",
              "sha256": "c5a675456d88afa0dbbc64a62ba5d5e8cc56e78ca650dff721ba76bb0e648c27",
              "task": "skill_trajectory_summary",
              "total_tokens": 1952
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "f8c229e052ff8416684f4cea46873a7f4051451dc93e7ea61e88949b9687f9e4",
              "provider_status": "completed",
              "response_sha256": "86dc2d47c12a17adab27a4903eae2089d7448adef4c982a540461688cb729565",
              "sha256": "468542d606e91e995ae0098d911a33c41adaadba092de5de65abfb4efc9a6b24",
              "task": "skill_trajectory_summary",
              "total_tokens": 1736
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "f98001396d207ae59f1661154c017aafbd5149b35f9bf73811c1966f6df43ced",
              "provider_status": "completed",
              "response_sha256": "757a5de757bd0e06d2ea2ba16ad088a58ff798fb2ff1923853f8041fda158d24",
              "sha256": "cd8512cfb355e286478d0952630520e9dba897617024f0ff7f8d50da29368a90",
              "task": "skill_trajectory_summary",
              "total_tokens": 1986
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "0b43bfe1f740d69bd92f317a3e7783f0db11449f8165ff953b164683c45c5d03",
              "provider_status": "completed",
              "response_sha256": "372e4c32835e0c4fef7dbe33a882b64a57548d469a5b4cc6e09bf283dd59da11",
              "sha256": "a71ac1040e4a5a3c377103aa2a15f44dc2c30da2551044c703bfa4257f390cdd",
              "task": "skill_patch_propose",
              "total_tokens": 4137
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "ce85883fe8780d414a4191c89aec78e607f83e935d9578c909f1ab8b1283b66b",
              "provider_status": "completed",
              "response_sha256": "015541b71f2c88a909aaf768390cf079bf5b71172d5455203c091a4395687e7f",
              "sha256": "6ee7a7b9fece98d788d2d59b57670882855bc115293609c35ff9f57bdb887d61",
              "task": "skill_patch_apply",
              "total_tokens": 2516
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 22243,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/update/skill_post/SKILL.md",
          "skill_post_sha256": "f377716d68f67e622fbc1f90d31a365c7fc7a4a237beca0b753a5c59b9c7162a",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "30e1a063200de0a1f8d690383b2d1d236b8e8e20970fcba050d4f633109d6d9b",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/mrw/update/update_receipt.json",
          "update_receipt_sha256": "3f15193babe853b7701c89600b04ef9ca40d4e48c4f8809bbb75acacd42a23ff"
        },
        "win_c": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "65dea4837b2fec33a30b5be86a227fe0c38b1f2b84b562b673a60fc1c22382d9",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/checkpoints/provider_budget.sqlite3",
            "sha256": "9e5f49008c038cf0bd975f9e0b9f38c0710c27cdfee3a44950a82d25b52329f1",
            "total_claimed": 100,
            "unit_claimed": {
              "e1-fmv-00/rep2/win_c/update": 10,
              "r17-b4-agj-p2/rollout_0": 5,
              "r17-b4-agj-p3/rollout_0": 3,
              "r17-b4-agj-p8/rollout_0": 3,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 4,
              "r17-b4-fmv-p8/rollout_0": 6,
              "r17-b4-ioc-p1/rollout_0": 3,
              "r17-b4-ioc-p4/rollout_0": 9,
              "r17-b4-ioc-p6/rollout_0": 3,
              "r17-b4-msp-p0/rollout_0": 7,
              "r17-b4-msp-p7/rollout_0": 3,
              "r17-b4-msp-p8/rollout_0": 5,
              "r17-b4-ska-p4/rollout_0": 6,
              "r17-b4-ska-p5/rollout_0": 6,
              "r17-b4-ska-p8/rollout_0": 6,
              "r17-b4-tsr-p0/rollout_0": 4,
              "r17-b4-tsr-p6/rollout_0": 6,
              "r17-b4-tsr-p8/rollout_0": 6
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "5a11533b62ab949fdb17f4ba82264cd7f61131e5cf641cf6a032ebe11324c4a3",
              "provider_status": "completed",
              "response_sha256": "bc342d0f7334afebbbbc6604410fded21191d90dab7ba9908acfbbc060bacace",
              "sha256": "e1cb06fa038078e2d736da42c329f3570434e97d4662b8229d85c04d480d24d5",
              "task": "skill_trajectory_summary",
              "total_tokens": 2042
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "3465577b1d60375b6cbc4b141d725fdceafddb73731d005cb8140b7b35353746",
              "provider_status": "completed",
              "response_sha256": "34bf4f39b00438478e9fb675864be5a7abf26d3453a94eac254a80a4d4f1e97c",
              "sha256": "cc438382daa2b88e5782599d46d55c50d0e7d2775bb32e3e49c27c3a01ab1f8a",
              "task": "skill_trajectory_summary",
              "total_tokens": 2161
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "02de21f70c664b4839b5bf2c54be41697c7450b0a192a8f2513de7c6b70ed2b6",
              "provider_status": "completed",
              "response_sha256": "70625c1efa61f9c49ce8336b837067b8eaf3328f8951bf438fc638e06ea3c6a4",
              "sha256": "b8171ab9b91fcc495e833f54b7be81b5554c6001e6f4cc9bc7a14ff99d103c91",
              "task": "skill_trajectory_summary",
              "total_tokens": 2076
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "adc9198614d74b076fdfa302f1f4fc9caef8b42c3a63630d5f5a75ad9b630b78",
              "provider_status": "completed",
              "response_sha256": "7e32da4462d5006be9555f039a9e57a4c12e61f357459eb5e6907565c3f3956f",
              "sha256": "3bc6db26b0d4dfaf87f54cf87d98f26fe1fb60e38f15f3402dd0d247eb6b8ded",
              "task": "skill_trajectory_summary",
              "total_tokens": 2034
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "188bcac0fd9aca2ea0dcc2835956e8b6835f1df234902b5ac47c50588d7b80a3",
              "provider_status": "completed",
              "response_sha256": "f13657cfd0f2def8b56cea203dbdbc5035a5845971a28c34d8facd360a3b19e6",
              "sha256": "af8301d84d4b0930772d7b5259bb07e166df36174b526b464463e525055c165d",
              "task": "skill_trajectory_summary",
              "total_tokens": 1753
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d7fdfabbcce57cf84196913d8e96cdc72770ee316302181dd13d5ec597d7116d",
              "provider_status": "completed",
              "response_sha256": "99c5399151dbd00919e3e453671af632f683364944cdbcebf24ddf3e2794e1fe",
              "sha256": "f15a9691ad6a2422c982eeaa7087df80528d735a23ebafc98c6d3b8aa67bbc4b",
              "task": "skill_trajectory_summary",
              "total_tokens": 2044
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "2a1ba9b796bd50a3037416a192017b43de4419d384b96dbab8db1ca8bc7e2994",
              "provider_status": "completed",
              "response_sha256": "4d301178b05d3d84856c861badfd49d993704fdf10ffbb066d1ece59c9564fe7",
              "sha256": "a1cfbd7dc9f9f55fc972f8f7599e086990081de74341f0db53876537195f3168",
              "task": "skill_trajectory_summary",
              "total_tokens": 1727
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "2adbc4b9517285bedd0b1f54d55591b453ad545b88d7f3d176cba49cd422e8db",
              "provider_status": "completed",
              "response_sha256": "96fce95bec0fd6f3dd27c8d2ab198073262826581ec65572a249182b1ca308c9",
              "sha256": "ee9c121ab393cf5848784df4a87631552f554d7fbe3e4d6a521694af331a1100",
              "task": "skill_trajectory_summary",
              "total_tokens": 1972
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "25c625d4cbd914eb10c9534b409595d53163df5065bae09ddd2197828b749a9b",
              "provider_status": "completed",
              "response_sha256": "b436ca89c680da3bea0922edda7d803fc5f7f1f2dbc0b946f560ec704e181e53",
              "sha256": "a46809224324fff81a653605b3ced09eaabd12571761b1509b027e7d78dd600f",
              "task": "skill_patch_propose",
              "total_tokens": 4249
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "fce9a49ca64451aa9f540eaa22fd92b92a7225479c2d9fa56117d09549cdeb82",
              "provider_status": "completed",
              "response_sha256": "8bccb1c776aa3210326bfa598b850f5f5c1e17d1bebe181d1946f1941812c289",
              "sha256": "67c012c63b6ad6c7e01600109d67cefe8271b2051532ca51d6be67643cced4e5",
              "task": "skill_patch_apply",
              "total_tokens": 2093
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 22151,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/update/skill_post/SKILL.md",
          "skill_post_sha256": "a1375876668ec1b102173f67c4f0d96319ff0ff2e1b0641b5d72ec5aa31410bc",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "fc8310e95ddeb8ee20634a32a04d8a5f300ed1cd08859ed506b03903d0f49cfc",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_2/win_c/update/update_receipt.json",
          "update_receipt_sha256": "13c85c8f62887bea95e05ad66058b2a14f985cf64fd90a429461c3fbc743daaa"
        }
      },
      "evidence_windows_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/evidence_windows.json",
      "evidence_windows_sha256": "ea141c4b8ec4f0d592f450fb82c9e3723b9077b9f24edb5215f1e6885f3ce0b3",
      "pair_summary_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/summary/replicates/e1-fmv-00-rep2.json",
      "pair_summary_sha256": "627b2e88d5dbc3124ef2f45cc25fff882522572cfeadcff918638e5121749250",
      "prefix_compatibility": "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL",
      "replicate_id": 2,
      "source": "inherited_repair1",
      "stream_id": "e1-fmv-00",
      "unit_id": "e1-fmv-00/rep2"
    },
    {
      "arms": {
        "mrw": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "8bf25477f28f749c51517a072d47bf4080be73eea5c17510851d0a58d29d0e95",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/checkpoints/provider_budget.sqlite3",
            "sha256": "e14cf93a678db503c1fcf951056b2fa058977e3bafc19f45ddd05baf3625e4c1",
            "total_claimed": 106,
            "unit_claimed": {
              "e1-fmv-00/rep3/mrw/update": 10,
              "r17-b4-agj-p2/rollout_0": 5,
              "r17-b4-agj-p3/rollout_0": 6,
              "r17-b4-agj-p8/rollout_0": 5,
              "r17-b4-fmv-p1/rollout_0": 3,
              "r17-b4-fmv-p2/rollout_0": 9,
              "r17-b4-fmv-p8/rollout_0": 7,
              "r17-b4-ioc-p1/rollout_0": 3,
              "r17-b4-ioc-p4/rollout_0": 3,
              "r17-b4-ioc-p6/rollout_0": 5,
              "r17-b4-msp-p0/rollout_0": 6,
              "r17-b4-msp-p7/rollout_0": 4,
              "r17-b4-msp-p8/rollout_0": 8,
              "r17-b4-ska-p4/rollout_0": 7,
              "r17-b4-ska-p5/rollout_0": 7,
              "r17-b4-ska-p8/rollout_0": 3,
              "r17-b4-tsr-p0/rollout_0": 8,
              "r17-b4-tsr-p6/rollout_0": 5,
              "r17-b4-tsr-p8/rollout_0": 2
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "02fa91fb404136c600e2bf55c985f876b480c973a002941be3d80f90580d5339",
              "provider_status": "completed",
              "response_sha256": "c201602ac996170b6e375432917d58c9873b5e6695ae9c3925846656b6cac12a",
              "sha256": "43244765d35dcd846fcd1cc94749b55232564ebab38cae650c3505614e134aff",
              "task": "skill_trajectory_summary",
              "total_tokens": 1976
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "3ebcbd7e70faf12b578dc2d574ac1d3a75014bfc9875683682febe664c166ccf",
              "provider_status": "completed",
              "response_sha256": "4f812f0be65cabd0f89efdd7fbdba6f0acea7ce5b5e5ae5d22390208b079907d",
              "sha256": "f411a236a7c3a344d861945818f966c6471c225c9e5cd2fd7946b2dfabe50e7e",
              "task": "skill_trajectory_summary",
              "total_tokens": 2063
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "426af7b9b0bac4b9ece4f3d032dfbbc73406898e37a1f5039474b87afefb1d56",
              "provider_status": "completed",
              "response_sha256": "50f05cc155984850484f3bbb6e19b3e266e9a8c17d6b1e8fb3ece088118c8648",
              "sha256": "7d37d2b627547c7afa5d6ef8165334911667202d9205f82b64d6fa7591c31ee0",
              "task": "skill_trajectory_summary",
              "total_tokens": 2068
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "68b823d674a410758bc070c6310c0d28ae1ccfd9c1020f77bb9e96f09baab4ba",
              "provider_status": "completed",
              "response_sha256": "0273daf078a13171b27a6def7a2f9b1d148db184be66e1ca150866ebb7b3c838",
              "sha256": "b163149c20b61a9418d97926031f3e1258a3c751eb6bad9e984a01366f1bef9f",
              "task": "skill_trajectory_summary",
              "total_tokens": 2177
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a97dad740bfb3e1f973357832e6ce212c2abf2622cf3dcf536ae3dc5eced2592",
              "provider_status": "completed",
              "response_sha256": "a2db76755004f08fa10717840404c1592fb1bcf29c843902cd53ef7d7fff9e23",
              "sha256": "22c697d7e97bea963ec80f6170b0e3f53f8d68ae34bbfebc7d70d14da7927e1a",
              "task": "skill_trajectory_summary",
              "total_tokens": 1659
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c3f6824a50b77269ff1099d87421e16b86a19f990f0ac0a95c5ff23d2ab40c1d",
              "provider_status": "completed",
              "response_sha256": "8b51186be3c7bce0423ca9762c1ef0f0fcfe9544a44bb4156ec81751745e8b88",
              "sha256": "f18488f581ad6cecce54d34bbb312b419489693caeb91f8c37c60ddc095c4dda",
              "task": "skill_trajectory_summary",
              "total_tokens": 2011
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "f8c229e052ff8416684f4cea46873a7f4051451dc93e7ea61e88949b9687f9e4",
              "provider_status": "completed",
              "response_sha256": "9c92848bdda10e9597f3bb9477ee44b0c1075a278cb58e7a0651c2ac1a8ecc48",
              "sha256": "d286de64b6e26efd61cb7f5ef080489644e3407ee97cb7e01c7d68cc50e0b059",
              "task": "skill_trajectory_summary",
              "total_tokens": 1678
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "f98001396d207ae59f1661154c017aafbd5149b35f9bf73811c1966f6df43ced",
              "provider_status": "completed",
              "response_sha256": "d28f00519120e620181167c827ce79af618e618bae3a9ae085bb76573678a27b",
              "sha256": "ecb819cadfad7bdd950e78ff2354b78ee4f1cc5437e4bb3e2e1b47e1dbb0a6f0",
              "task": "skill_trajectory_summary",
              "total_tokens": 1964
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "d72961d5bd5832c5c129be005b5282ec09435a01d3f19f543e72f2bd9154fcfd",
              "provider_status": "completed",
              "response_sha256": "e7f3f461ab8e7a9db3c36b9e368b8f2ee8aa19a7c544d159ce5658cc2082d388",
              "sha256": "1dff7699d29f10886a9a5055d0b09d1b4eef9ebe8f9427703a5c41e33f81ce9c",
              "task": "skill_patch_propose",
              "total_tokens": 4198
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "3f269c79e289f0544ac5081a6827b236ae78f4138bb6d70dc9a8e82f30ba3f50",
              "provider_status": "completed",
              "response_sha256": "775638bb8118145e41d66df2754bf88c8a3e2e9764994ed04126110a4e39fa93",
              "sha256": "7f4906a2d7464752238838fff7d502d3239f04722fd317500b3941de3bc99cbc",
              "task": "skill_patch_apply",
              "total_tokens": 2371
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 22165,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/update/skill_post/SKILL.md",
          "skill_post_sha256": "f48af9deba58e134a828ed3990eec7700daf2b11702e23a9abd29ca18adcf3cf",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "bacaedb7939d4c9729f4683f1c609087419783d6831599c8251605119d3ae5ff",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/mrw/update/update_receipt.json",
          "update_receipt_sha256": "2794cbce578cdccba139f967d5d9206fd5e1db12abe6851739f20790d42c76be"
        },
        "win_c": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "00a28396ec6b744dc82f18685ead223ab10f65c028bf953b718826def6c22d45",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/checkpoints/provider_budget.sqlite3",
            "sha256": "e66fd0e93498307a3644165b5fa570830feec473bdd370fc56a4d46afe742333",
            "total_claimed": 109,
            "unit_claimed": {
              "e1-fmv-00/rep3/win_c/update": 10,
              "r17-b4-agj-p2/rollout_0": 7,
              "r17-b4-agj-p3/rollout_0": 6,
              "r17-b4-agj-p8/rollout_0": 5,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 5,
              "r17-b4-fmv-p8/rollout_0": 4,
              "r17-b4-ioc-p1/rollout_0": 4,
              "r17-b4-ioc-p4/rollout_0": 8,
              "r17-b4-ioc-p6/rollout_0": 6,
              "r17-b4-msp-p0/rollout_0": 8,
              "r17-b4-msp-p7/rollout_0": 8,
              "r17-b4-msp-p8/rollout_0": 6,
              "r17-b4-ska-p4/rollout_0": 6,
              "r17-b4-ska-p5/rollout_0": 4,
              "r17-b4-ska-p8/rollout_0": 3,
              "r17-b4-tsr-p0/rollout_0": 6,
              "r17-b4-tsr-p6/rollout_0": 2,
              "r17-b4-tsr-p8/rollout_0": 6
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "5a11533b62ab949fdb17f4ba82264cd7f61131e5cf641cf6a032ebe11324c4a3",
              "provider_status": "completed",
              "response_sha256": "a1bbc7ba6587ac2c4efe80a850dcbbdf0757004a37b24921d7c33e1eee1d95fe",
              "sha256": "d737094ac279af4ecac74ac7ddd94cd3d22a0b829169ad63fb2e79a38bc6f13e",
              "task": "skill_trajectory_summary",
              "total_tokens": 2066
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "3465577b1d60375b6cbc4b141d725fdceafddb73731d005cb8140b7b35353746",
              "provider_status": "completed",
              "response_sha256": "8b8a9301fb92f6638c96fec6dda9abd444a6550fe055b023a45b16e7df97c667",
              "sha256": "60e998067bd01eeb4672c502d85bb030acdae94df29c20dcfdf80a4599bee73c",
              "task": "skill_trajectory_summary",
              "total_tokens": 2139
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "02de21f70c664b4839b5bf2c54be41697c7450b0a192a8f2513de7c6b70ed2b6",
              "provider_status": "completed",
              "response_sha256": "3323902d148116c02b264b0f24cd04f8823c30db3095333dfbfa657879b07bcd",
              "sha256": "f296ea9e5ed90a65f6fa8aba2b0c0c072c23c495a982b284461626047186da93",
              "task": "skill_trajectory_summary",
              "total_tokens": 2100
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "adc9198614d74b076fdfa302f1f4fc9caef8b42c3a63630d5f5a75ad9b630b78",
              "provider_status": "completed",
              "response_sha256": "240b3a757e214d54a94affc2fa5b198165584db99978cc6b6147ad4d1bd0c4b8",
              "sha256": "23e86a02cfbe7f9b1887f8fa5ec906e568c335c0ad028d180b90826ad8be7ff7",
              "task": "skill_trajectory_summary",
              "total_tokens": 2033
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "188bcac0fd9aca2ea0dcc2835956e8b6835f1df234902b5ac47c50588d7b80a3",
              "provider_status": "completed",
              "response_sha256": "32011bd8ae5329e5793b37dd848503f4f1ad255b23cb79bdd0c63f9367657721",
              "sha256": "ad26044e439a0be5fc14c84003fb6e2d9317ba1984db2230c67ee4e0aed2e344",
              "task": "skill_trajectory_summary",
              "total_tokens": 1797
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "d7fdfabbcce57cf84196913d8e96cdc72770ee316302181dd13d5ec597d7116d",
              "provider_status": "completed",
              "response_sha256": "ba1898c70865bcd97aaf0745eb8f23925c84232847c99df4c219d13a348d68d8",
              "sha256": "44675d52f45ed526ddf2d330963b292215a5911ff45b5a664108b14cb3fa7371",
              "task": "skill_trajectory_summary",
              "total_tokens": 2098
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "2a1ba9b796bd50a3037416a192017b43de4419d384b96dbab8db1ca8bc7e2994",
              "provider_status": "completed",
              "response_sha256": "a27b0ce380bd94a45d2817d2d06e0cd02a8f9ea3d1b65fc43deaeedd8caf1470",
              "sha256": "c2f0fa893013e087bba44f3ecad59aa16a0b16ad3b0630660489eb871493dd9c",
              "task": "skill_trajectory_summary",
              "total_tokens": 1718
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "2adbc4b9517285bedd0b1f54d55591b453ad545b88d7f3d176cba49cd422e8db",
              "provider_status": "completed",
              "response_sha256": "8f0df6e90e3bb408288e37ffc7758b710a2f84a6febad9ea7a9b5a796b51106e",
              "sha256": "54d56310ffac228ece85d08601dda948f1c1f110c3d234b1c07aaf0c5e23b596",
              "task": "skill_trajectory_summary",
              "total_tokens": 1948
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "d4ec1ae67f6e16c19f87c3866b777649358efae174138e0aadf0e6b225d106f2",
              "provider_status": "completed",
              "response_sha256": "423f4bc86a59ee9a0d98b7ab733ff419ee3470a332b7d08fd700a78aa9ac7659",
              "sha256": "d1b356bb6864d7db1e9f4eac81127c026a5a37229ff84e535dd316445a799de9",
              "task": "skill_patch_propose",
              "total_tokens": 4442
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "f08ea2c8402410b21a069fd65fea83869bfa02b7507ca5f38bd41bd597e180f8",
              "provider_status": "completed",
              "response_sha256": "f0c44c0f124af4ea9d6c0613b9646934b78a0b25197557577f76a891adb1050d",
              "sha256": "5a4e377ff7a41f9281c23705ec041df8609d225f84f26f38a52bc09025a86927",
              "task": "skill_patch_apply",
              "total_tokens": 2252
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 22593,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/update/skill_post/SKILL.md",
          "skill_post_sha256": "362e0b561ab070e16d6213fd40f69307e8215a7c010e85d9059b9cd8bcfcd3df",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "044359bca844b472581c6155b434ed576da35e643411509421636c2f4e0c8105",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/replicate_3/win_c/update/update_receipt.json",
          "update_receipt_sha256": "631139ae200ad624039d2997ddf67bf5252e8acca11067e7835910c5809ab243"
        }
      },
      "evidence_windows_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-00/evidence_windows.json",
      "evidence_windows_sha256": "ea141c4b8ec4f0d592f450fb82c9e3723b9077b9f24edb5215f1e6885f3ce0b3",
      "pair_summary_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/summary/replicates/e1-fmv-00-rep3.json",
      "pair_summary_sha256": "c1587b30aaab300eb05439e9f4656dced5ce3d1455dae878084053e68696c31b",
      "prefix_compatibility": "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL",
      "replicate_id": 3,
      "source": "inherited_repair1",
      "stream_id": "e1-fmv-00",
      "unit_id": "e1-fmv-00/rep3"
    },
    {
      "arms": {
        "mrw": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "a2a732b0a167a53f7371065e48781cdbb85adb3e0c9ae164455a0e4365addc10",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/checkpoints/provider_budget.sqlite3",
            "sha256": "91071af934810e98692ee00fdb6abbf5f84af719b73ec654c7f4ec22f33fdfcb",
            "total_claimed": 119,
            "unit_claimed": {
              "e1-fmv-01/rep0/mrw/update": 10,
              "r17-b4-agj-p2/rollout_0": 7,
              "r17-b4-agj-p3/rollout_0": 7,
              "r17-b4-agj-p8/rollout_0": 5,
              "r17-b4-fmv-p1/rollout_0": 6,
              "r17-b4-fmv-p2/rollout_0": 7,
              "r17-b4-fmv-p8/rollout_0": 6,
              "r17-b4-ioc-p1/rollout_0": 5,
              "r17-b4-ioc-p4/rollout_0": 5,
              "r17-b4-ioc-p6/rollout_0": 6,
              "r17-b4-msp-p0/rollout_0": 6,
              "r17-b4-msp-p7/rollout_0": 3,
              "r17-b4-msp-p8/rollout_0": 9,
              "r17-b4-ska-p4/rollout_0": 7,
              "r17-b4-ska-p5/rollout_0": 6,
              "r17-b4-ska-p8/rollout_0": 7,
              "r17-b4-tsr-p0/rollout_0": 4,
              "r17-b4-tsr-p6/rollout_0": 7,
              "r17-b4-tsr-p8/rollout_0": 6
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "7068350d8ca97b9a93952305b55d70ead279d9983e26eda65e5ca3b4de594f67",
              "provider_status": "completed",
              "response_sha256": "4131bada2498e6c9e27e98572c2f36c464ebcd2df8c42d57a27b3c9aec211557",
              "sha256": "b34b84c2e0a7909c848830799ba5087f77ca13230d9cda2802b01a9c07dc0366",
              "task": "skill_trajectory_summary",
              "total_tokens": 2164
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c56ded56f3b51afab70b610e9eff7d05cbd73729fb6acdbe6746210cd5602428",
              "provider_status": "completed",
              "response_sha256": "321b4c837edde91ffd6c00827dac1384ef159e1f1fa6395442ef3154c75ac958",
              "sha256": "f920707b91886d4a8e37e2f3e40936174849bf0ca501c6c5d190809e41def9d1",
              "task": "skill_trajectory_summary",
              "total_tokens": 1700
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a01c112ddf3ad1df4e5c8eb5bb7a6c83d61e4dd5dddfbdc4ca253d7ae804e6f9",
              "provider_status": "completed",
              "response_sha256": "cfa32e1857224a983e208079bb1a29c4b446018cc5b447b75930f497f6bbbacd",
              "sha256": "44d1fe41188039abb41f85d1e90ed17d0e792ec828bb56c52cf787a2552f332a",
              "task": "skill_trajectory_summary",
              "total_tokens": 3911
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "42c4f457d06eee8794885c2001e60372ca01f8de8ec6bf143d650d77d09d8c55",
              "provider_status": "completed",
              "response_sha256": "7ce2b1d478d9bfc216635b6f735f327e83a083db3513d905742a8451e97796cf",
              "sha256": "8ec0cd97b2cb14df1affe01a979098574f2d24a8558f374d1704776138c20363",
              "task": "skill_trajectory_summary",
              "total_tokens": 2155
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "1b41d7a985151d8f6fcd281b533bc0d27bf89de3ebdec5c2085197fe29c10282",
              "provider_status": "completed",
              "response_sha256": "560f6d7addfda1df8b6668643cfb6eb6c5b2227149c41619a4ee592b4c7bb335",
              "sha256": "f2a4e3721426b6048c1ba5d5c85b60bc67767ee1bd96f26854d92bbbf930dcb1",
              "task": "skill_trajectory_summary",
              "total_tokens": 1939
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "afbfd136d5399b9504e9cfe974b1cdfc43eb4995e3ab79384247be9ace141c3a",
              "provider_status": "completed",
              "response_sha256": "c7cd42e73a0db693bb33b7a41c07d759dc2b869a368e735a4cbfb852da6583c3",
              "sha256": "92c611062b0b46e863ac31093cc0776f21391a76e253a73c49aadbba64ec9e68",
              "task": "skill_trajectory_summary",
              "total_tokens": 3836
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "3210bf3a6e21a41775f499b53c89f0f4050b8a7b0572a2b873bcc5adfeaa2ace",
              "provider_status": "completed",
              "response_sha256": "1254758549b03f5fd39a4cc7cac2e62a06aba3cb2b4c0a360d39ee8d9c318812",
              "sha256": "17105c0fe6d335a95067a56884459a4866298a9d31085156cdb83c5d0eefa1e9",
              "task": "skill_trajectory_summary",
              "total_tokens": 3553
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "fcfca75330677aa51e90278820ea9f327eb3be78aaf121fb55ba126d455b6561",
              "provider_status": "completed",
              "response_sha256": "3477f1f6a3c0d872638eb3d77a7a79978ff2560e88d489264fe9108ec0be09e4",
              "sha256": "519e5843f0db3d9d9c3ee4497930bcd3ee55b1728b1a6c266d0e77f2e25d6fb0",
              "task": "skill_trajectory_summary",
              "total_tokens": 1635
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "5262718a67fd6bab59ab1c4fc67818d1a2511b62550acc854e3eef90471f4388",
              "provider_status": "completed",
              "response_sha256": "6881130755dcb2ba8cacd3a235c74f945c7b8268b2ec1b1c28c13a94b0253512",
              "sha256": "66ceb3aca804f62916330731ef4a01a6929dff67304ec5347fe1239b0d649c88",
              "task": "skill_patch_propose",
              "total_tokens": 4485
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "df6ac56535d353f68baaf6d5ae5187c20890111cd507baf28c159866e46b5ea9",
              "provider_status": "completed",
              "response_sha256": "e681eb227e95786f8f4a60be1c0b8190a5c691f03f6936a259c12ee7af1476b4",
              "sha256": "4ef60045a5135495133dbad0943d52d82f569102c02b6ec0b31fab1824b7c3fe",
              "task": "skill_patch_apply",
              "total_tokens": 2464
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 27842,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/update/skill_post/SKILL.md",
          "skill_post_sha256": "ce3f9c7c4fb93e8d01ba8be319c3de2b9e397db761994ef2a3e7abc5ea05d501",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "5019488e78ad01c7ee16ce8bedffefe46df599b664eeabd591a464567ff32791",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/mrw/update/update_receipt.json",
          "update_receipt_sha256": "3f54ed2a1959f8189897e9e9a5d7eaddfa494602e21250c866859680e0901f5f"
        },
        "win_c": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "231ea0e8969e064bf2c9f0910827f75c3024d5dbb62734764d5b5ad772023e61",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/checkpoints/provider_budget.sqlite3",
            "sha256": "f00ffe6d4f5d9e4493837b57307ec1cc83825129db246c934eb1745c3d0e060a",
            "total_claimed": 113,
            "unit_claimed": {
              "e1-fmv-01/rep0/win_c/update": 10,
              "r17-b4-agj-p2/rollout_0": 6,
              "r17-b4-agj-p3/rollout_0": 5,
              "r17-b4-agj-p8/rollout_0": 7,
              "r17-b4-fmv-p1/rollout_0": 7,
              "r17-b4-fmv-p2/rollout_0": 5,
              "r17-b4-fmv-p8/rollout_0": 5,
              "r17-b4-ioc-p1/rollout_0": 2,
              "r17-b4-ioc-p4/rollout_0": 6,
              "r17-b4-ioc-p6/rollout_0": 8,
              "r17-b4-msp-p0/rollout_0": 8,
              "r17-b4-msp-p7/rollout_0": 9,
              "r17-b4-msp-p8/rollout_0": 5,
              "r17-b4-ska-p4/rollout_0": 7,
              "r17-b4-ska-p5/rollout_0": 5,
              "r17-b4-ska-p8/rollout_0": 8,
              "r17-b4-tsr-p0/rollout_0": 3,
              "r17-b4-tsr-p6/rollout_0": 2,
              "r17-b4-tsr-p8/rollout_0": 5
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "b9c29acca0e4f0c57b83755bb8403447b8c503e95cda0c345ddd6c7d3c7ee16b",
              "provider_status": "completed",
              "response_sha256": "b93da7360782dbcabf8a41424073d5bc7d7914f44fb5378e6ac6326b18c7ef85",
              "sha256": "30f3fe1249ce4260b6ad6cb602c0d1ba18813e8b6373d83c61d2c5e2305042aa",
              "task": "skill_trajectory_summary",
              "total_tokens": 2224
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "8d176467e3373abad9edcab672e72313ee3f893cce801164eb976802b88e41a2",
              "provider_status": "completed",
              "response_sha256": "74ab867214c49b56b09f262c5db71911da6c4eba4d0433637d59bc0b1dfb0b4e",
              "sha256": "b5894b096e7f59b0dae97ed4790d7b0b9564ed7af42f244d331b5341a3289017",
              "task": "skill_trajectory_summary",
              "total_tokens": 1760
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a01c112ddf3ad1df4e5c8eb5bb7a6c83d61e4dd5dddfbdc4ca253d7ae804e6f9",
              "provider_status": "completed",
              "response_sha256": "79a930fa3de8b4a5fd74ae77e091b26ccbd0e4ffe0d377149a69fd6acea316a9",
              "sha256": "7bf4e50a0ed4dab22b19190781d44e964df4d19560de750c03163ded4a332f06",
              "task": "skill_trajectory_summary",
              "total_tokens": 3900
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "9cecaa9373563a803daf75d2fc78b5a245185c00d3766fd9983c02484aa29d51",
              "provider_status": "completed",
              "response_sha256": "c5e4b5a96d8b55657052a5cf7b89ffac4f4ef4789789ed2f635eadc14bd5b9aa",
              "sha256": "de3a98d7015b96d17748374a8a58c66adf889cf44c8d960180065eeaaffb2f80",
              "task": "skill_trajectory_summary",
              "total_tokens": 2088
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "387d58561bd67e54f3894b0a2849300144bd51700abfab3013fafef683b133b1",
              "provider_status": "completed",
              "response_sha256": "bcb9ff5ccaf53e1a021e6070600449cd1480d1ae459def949f1e053b0aee0f66",
              "sha256": "3300c31accdf2c8ac43c7cdc8110b8f4cd6e3b016b1ad05937221178f20668ed",
              "task": "skill_trajectory_summary",
              "total_tokens": 2011
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "7c263d4c964b7b124d45d487f54ef0cd6657a3a50ff6383273bcb96856360dc1",
              "provider_status": "completed",
              "response_sha256": "e4afd485a16352bc540111664d4dfbbdfb29cb3c7a727da2fee427c8117f1869",
              "sha256": "310a7b221091b75bfda1479d9f89d0a139b6e841964b447fa9478da5bea6a2e5",
              "task": "skill_trajectory_summary",
              "total_tokens": 3797
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c941689763b8c3b335b2d6bb1dae125893408b11a78463b245894e81a72ec62a",
              "provider_status": "completed",
              "response_sha256": "4f5a7e7f7b637b036d640ed33425755796c46cf11be25ba4e1dd509f5180fdb1",
              "sha256": "26423380b56f532e76ce362199349407a0b23c74d802a53ae0cb909cc57ff490",
              "task": "skill_trajectory_summary",
              "total_tokens": 3589
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "77f7cdd5170b936805a04ccfebd7350ee7fd92b1df7657d924defb1bf198556f",
              "provider_status": "completed",
              "response_sha256": "462d6610844268ddc217662c6e8024737a3b72c01a80fafb6dc9c9af029d2c18",
              "sha256": "5028dd39a2e7ef8d9fda816290ff08c4b70fb266910703f88f651d2771fbba23",
              "task": "skill_trajectory_summary",
              "total_tokens": 1728
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "970a4ea946a749a4a879a56e0368fb24a2353432ae902854b98fc3f6b075f93b",
              "provider_status": "completed",
              "response_sha256": "c001dc9173975b8c49d662e3a2000dc18facc223f767be00a81e1d768fb2ddfe",
              "sha256": "ec77857fb601a116b77cfbb449b02f2fc0d405033d7c5dda8545294bab33c9d5",
              "task": "skill_patch_propose",
              "total_tokens": 4137
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "fba0ee0f0ae8085dfabd33f41612c8f36b8c5c69ec6c2def3b5b1e1bd836d483",
              "provider_status": "completed",
              "response_sha256": "4b12bf954c0d3306aa4c6dc6aa8b2e43fee3d13445c42f74d340ea4cb29bf349",
              "sha256": "be5a913e5b52913fc59731e359854fc6274191b8227684c85e0c0c8350613d5e",
              "task": "skill_patch_apply",
              "total_tokens": 1457
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 26691,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/update/skill_post/SKILL.md",
          "skill_post_sha256": "6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "67d606c075b69b47b085312ed51030d266ba03371402198ae635d747770a3a54",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_0/win_c/update/update_receipt.json",
          "update_receipt_sha256": "3220880b3b2e6c9e1b4dda0188215167ca3e2d154f73ff7b5b19b199e17fcf5c"
        }
      },
      "evidence_windows_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/evidence_windows.json",
      "evidence_windows_sha256": "5355118b362f269ff567704168ca92310eec6a5149a73ffa11fc4e906e92d7c4",
      "pair_summary_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/summary/replicates/e1-fmv-01-rep0.json",
      "pair_summary_sha256": "8e1779bfbda3454ad67b782dc9ccb4b9b7b94729367335c2bbfa670e770decdf",
      "prefix_compatibility": "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL",
      "replicate_id": 0,
      "source": "inherited_repair1",
      "stream_id": "e1-fmv-01",
      "unit_id": "e1-fmv-01/rep0"
    },
    {
      "arms": {
        "mrw": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "fc9b1510e83fab123807982a2db4c77eaa5b0a278878d00e7eb3fac47a4d1dcc",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/checkpoints/provider_budget.sqlite3",
            "sha256": "f18f870ec68d86ddc714380f68e771e37dfe1423440080c95f775230b139e9aa",
            "total_claimed": 113,
            "unit_claimed": {
              "e1-fmv-01/rep1/mrw/update": 10,
              "r17-b4-agj-p2/rollout_0": 5,
              "r17-b4-agj-p3/rollout_0": 5,
              "r17-b4-agj-p8/rollout_0": 5,
              "r17-b4-fmv-p1/rollout_0": 5,
              "r17-b4-fmv-p2/rollout_0": 4,
              "r17-b4-fmv-p8/rollout_0": 5,
              "r17-b4-ioc-p1/rollout_0": 6,
              "r17-b4-ioc-p4/rollout_0": 5,
              "r17-b4-ioc-p6/rollout_0": 9,
              "r17-b4-msp-p0/rollout_0": 6,
              "r17-b4-msp-p7/rollout_0": 6,
              "r17-b4-msp-p8/rollout_0": 7,
              "r17-b4-ska-p4/rollout_0": 5,
              "r17-b4-ska-p5/rollout_0": 5,
              "r17-b4-ska-p8/rollout_0": 8,
              "r17-b4-tsr-p0/rollout_0": 5,
              "r17-b4-tsr-p6/rollout_0": 5,
              "r17-b4-tsr-p8/rollout_0": 7
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "7068350d8ca97b9a93952305b55d70ead279d9983e26eda65e5ca3b4de594f67",
              "provider_status": "completed",
              "response_sha256": "27d72a572a263ab47646bebb08137929e3c8bf48c59ccd3176914597bc8ab636",
              "sha256": "f328e18be08ffab886c1852479ed0bddd5142099f9b60cd38a7fc0839b5fe055",
              "task": "skill_trajectory_summary",
              "total_tokens": 2126
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c56ded56f3b51afab70b610e9eff7d05cbd73729fb6acdbe6746210cd5602428",
              "provider_status": "completed",
              "response_sha256": "83b622b78f917617b5a5442a94deb266ce03d6f20d3aeaa4188180445d0210aa",
              "sha256": "e95817d207f5a5c4b48dbd9897bae120e3aa124c889d5b8bf8483756d84919ed",
              "task": "skill_trajectory_summary",
              "total_tokens": 1730
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a01c112ddf3ad1df4e5c8eb5bb7a6c83d61e4dd5dddfbdc4ca253d7ae804e6f9",
              "provider_status": "completed",
              "response_sha256": "bfdf8c7023230e6e0393b66f99b7cace5c7b3e8bf013a23ace6091309b590569",
              "sha256": "8896abe2ec366a0296ec4a289ae31c2bc3f2fc5e0aeb6bb413b8b4a5492de7d0",
              "task": "skill_trajectory_summary",
              "total_tokens": 3861
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "42c4f457d06eee8794885c2001e60372ca01f8de8ec6bf143d650d77d09d8c55",
              "provider_status": "completed",
              "response_sha256": "192aa3b3b76d5df332c5f1f3258d49bef7debac72521456e0169a7f37f770772",
              "sha256": "bad2312c06b1e64627cb1427f03198dd310c48a10139703a2cec0b3e68a0cfa3",
              "task": "skill_trajectory_summary",
              "total_tokens": 2018
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "1b41d7a985151d8f6fcd281b533bc0d27bf89de3ebdec5c2085197fe29c10282",
              "provider_status": "completed",
              "response_sha256": "6bbe34f1b7c91430a16f68816e89f5621abd83134f6d8f1e3d2f67adc20aa3ae",
              "sha256": "9dedd096896c98ebd5eba4aaca0cef0e6d373e290c216a23473411e30c22ccfc",
              "task": "skill_trajectory_summary",
              "total_tokens": 1981
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "afbfd136d5399b9504e9cfe974b1cdfc43eb4995e3ab79384247be9ace141c3a",
              "provider_status": "completed",
              "response_sha256": "50aa8f29f7f52a03da2d168eca9edfa00067cfa7abda660cc561b565a930c052",
              "sha256": "d77352d449dee3a80bc096981f41eec1349f6a58897d87af006909999d9c71de",
              "task": "skill_trajectory_summary",
              "total_tokens": 3773
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "3210bf3a6e21a41775f499b53c89f0f4050b8a7b0572a2b873bcc5adfeaa2ace",
              "provider_status": "completed",
              "response_sha256": "3abfecb43e8320626abe14c3913502061f28603ce833b8cf1c346220df7f9ae1",
              "sha256": "d14d013b65b84d407c838c393188fe3825932ba62faece5e487b6f36a7b86064",
              "task": "skill_trajectory_summary",
              "total_tokens": 3561
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "fcfca75330677aa51e90278820ea9f327eb3be78aaf121fb55ba126d455b6561",
              "provider_status": "completed",
              "response_sha256": "48f094fa3044d95b22255273e67c95014c008f30bda2836ab048d4a843edd3cd",
              "sha256": "72fc89455dbbd4d2e97e30068cc5daa4762023c08499a9c4ee180b611896da7e",
              "task": "skill_trajectory_summary",
              "total_tokens": 1641
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "e0397f372bdb3dcc4db3a0729db237f8d25212d652f87887f1f715c2428083ee",
              "provider_status": "completed",
              "response_sha256": "f995435c644c060e6e8cdce0d14e9d490499f358f9bab699218495bb1fbef88c",
              "sha256": "d7fd153cc8e0ba41dd6cc34f3fc0e9d81f63729c4f27792e5280499709f25767",
              "task": "skill_patch_propose",
              "total_tokens": 4005
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "e231e0333a6efc2e3219e597b933ad56981f35d7b91c053fb1caaa58edac36c8",
              "provider_status": "completed",
              "response_sha256": "1038a966b93019cf23f92d7b56ff89f3c0a8eed8bcba4aac02f678e00c2ae82d",
              "sha256": "d3a4a0685652c7c8787383b1dd2e57a8e79a2c6617aa81ce28d99eb081915bc6",
              "task": "skill_patch_apply",
              "total_tokens": 2061
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 26757,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/update/skill_post/SKILL.md",
          "skill_post_sha256": "6bc2ee7668c55520fd249b1fa3692cd0c64cb1a9399c82b05e437f91a5c5e42d",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "17171f86c26a89ea0916545d3ea9b86e5038ce6d8f6f23b139e91ccb9fb17e27",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/mrw/update/update_receipt.json",
          "update_receipt_sha256": "2bff971f424be3a0f2646b4f59bc9defb927b77f08e6a1a21cdd24e17fd95efd"
        },
        "win_c": {
          "completed_heldout_tasks": 18,
          "eval_manifest_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/checkpoints/completed_eval_tasks.jsonl",
          "eval_manifest_sha256": "9367e1d4a07dda02da0230a25b304bd492ea4934adc12ea8211d34b5c05d6490",
          "parse_errors": 0,
          "patch_apply_correction_required": false,
          "provider_budget": {
            "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
            "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
            "max_unit_claimed": 10,
            "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/checkpoints/provider_budget.sqlite3",
            "sha256": "88e2f59e6e6a2175a57829da72e536953aff3211de47c4825169a81e5869f325",
            "total_claimed": 108,
            "unit_claimed": {
              "e1-fmv-01/rep1/win_c/update": 10,
              "r17-b4-agj-p2/rollout_0": 6,
              "r17-b4-agj-p3/rollout_0": 6,
              "r17-b4-agj-p8/rollout_0": 5,
              "r17-b4-fmv-p1/rollout_0": 3,
              "r17-b4-fmv-p2/rollout_0": 3,
              "r17-b4-fmv-p8/rollout_0": 5,
              "r17-b4-ioc-p1/rollout_0": 2,
              "r17-b4-ioc-p4/rollout_0": 7,
              "r17-b4-ioc-p6/rollout_0": 7,
              "r17-b4-msp-p0/rollout_0": 7,
              "r17-b4-msp-p7/rollout_0": 9,
              "r17-b4-msp-p8/rollout_0": 3,
              "r17-b4-ska-p4/rollout_0": 5,
              "r17-b4-ska-p5/rollout_0": 6,
              "r17-b4-ska-p8/rollout_0": 8,
              "r17-b4-tsr-p0/rollout_0": 4,
              "r17-b4-tsr-p6/rollout_0": 5,
              "r17-b4-tsr-p8/rollout_0": 7
            }
          },
          "provider_call_receipts": [
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "b9c29acca0e4f0c57b83755bb8403447b8c503e95cda0c345ddd6c7d3c7ee16b",
              "provider_status": "completed",
              "response_sha256": "6e0cb24e20dc946a4fb230b560f94f5ad5ae416b3b45ffd37461b491d04ffe40",
              "sha256": "df35306d783fc6f274342ad390d558c347a1d5d3ed7ee4366c8dcb89e0a3a76d",
              "task": "skill_trajectory_summary",
              "total_tokens": 2111
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "8d176467e3373abad9edcab672e72313ee3f893cce801164eb976802b88e41a2",
              "provider_status": "completed",
              "response_sha256": "804a7bc087775fe7baf4cafdc3aaf92a4ded81a6281b074421f8524211903909",
              "sha256": "862a5c839cee50c0810c2b8cd1d6fffa6be23001587473be1c1a78f37ecb797b",
              "task": "skill_trajectory_summary",
              "total_tokens": 1752
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "a01c112ddf3ad1df4e5c8eb5bb7a6c83d61e4dd5dddfbdc4ca253d7ae804e6f9",
              "provider_status": "completed",
              "response_sha256": "88467852dbc9bd21399e25efbc848296027c4d593f0d5175efb4bea3db10f8da",
              "sha256": "7bdd21b62f8fedcffccc0b75ccbc6de98be590d3a69293010c9be5dc45e65b2d",
              "task": "skill_trajectory_summary",
              "total_tokens": 3883
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "9cecaa9373563a803daf75d2fc78b5a245185c00d3766fd9983c02484aa29d51",
              "provider_status": "completed",
              "response_sha256": "4410e6e1b4dde5d2022c36f9a6a85096c546325bca9a716b515f06e093398b80",
              "sha256": "7405c1969c71af5b409f10f43a8be6a13b7778c4df8e318a8e61886c9fd22e36",
              "task": "skill_trajectory_summary",
              "total_tokens": 2079
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "387d58561bd67e54f3894b0a2849300144bd51700abfab3013fafef683b133b1",
              "provider_status": "completed",
              "response_sha256": "c4f0461a63f771ccca53ac02f6172cf956b276efcfe5fab21547f75dc50faa10",
              "sha256": "47fed76b6462d426be5a0ea8d7b3f0a147079b33f273dc1b998b0c45911db206",
              "task": "skill_trajectory_summary",
              "total_tokens": 1980
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "7c263d4c964b7b124d45d487f54ef0cd6657a3a50ff6383273bcb96856360dc1",
              "provider_status": "completed",
              "response_sha256": "4727c88efc030c8ead10f84919f81d58463ebd6a965050668c6c557a9ecbf5e2",
              "sha256": "29d4dae49ab26958967c56e282c1bf733d044d494ceaf5f25f94c320c78374eb",
              "task": "skill_trajectory_summary",
              "total_tokens": 3831
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "c941689763b8c3b335b2d6bb1dae125893408b11a78463b245894e81a72ec62a",
              "provider_status": "completed",
              "response_sha256": "6830c2ef1079afb1d3f160c53023ef6000ce2482c2267f7d92db1e7d9112f87e",
              "sha256": "bd46d0ac78a5144e7ea8ebf05bf10781b232e7af87f25669673f6321a7244a01",
              "task": "skill_trajectory_summary",
              "total_tokens": 3554
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
              "prompt_sha256": "77f7cdd5170b936805a04ccfebd7350ee7fd92b1df7657d924defb1bf198556f",
              "provider_status": "completed",
              "response_sha256": "ab9bae6e450b60fe89e15e4d6e99cd37bd834085e859039e0f9e70209501c1d1",
              "sha256": "eaf3c4a1d6a2f1fbc2a8e5919c45e3244d5245364e271115f10dd2534b44a62b",
              "task": "skill_trajectory_summary",
              "total_tokens": 1785
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/update/provider_calls/008-skill_patch_propose-attempt0.json",
              "prompt_sha256": "d9796c59f485269c55e9ff4471a80e70f2d512111180503556805dd3d91d9c5b",
              "provider_status": "completed",
              "response_sha256": "da358ff89db125fc2e651357063f58c067f1f616a389126fde30ba720ab74c47",
              "sha256": "a036e828f93558e7d4abf3bf0ee6f4abb39d606e6d0a2bb900be3387e2685e1e",
              "task": "skill_patch_propose",
              "total_tokens": 4009
            },
            {
              "attempt": 0,
              "parse_error": "",
              "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/update/provider_calls/009-skill_patch_apply-attempt0.json",
              "prompt_sha256": "4958e3bfcad72eab542c5010534506bacfa7dbd13e35aea9f30f76b7e34f280c",
              "provider_status": "completed",
              "response_sha256": "4b12bf954c0d3306aa4c6dc6aa8b2e43fee3d13445c42f74d340ea4cb29bf349",
              "sha256": "a41798c25b702ad98d3172f6694c6b535f36cd650519a0c59a54adeef30083b8",
              "task": "skill_patch_apply",
              "total_tokens": 1451
            }
          ],
          "provider_calls": 10,
          "provider_tokens": 26435,
          "skill_post_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/update/skill_post/SKILL.md",
          "skill_post_sha256": "6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649",
          "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c",
          "update_checkpoint_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/checkpoints/update_completed.json",
          "update_checkpoint_sha256": "6cc8d423e9e552a6facd1699b75a82a3b55663d2a555f8a920f32431204f23a6",
          "update_receipt_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_1/win_c/update/update_receipt.json",
          "update_receipt_sha256": "c85edd91835bcd5426906175af71208700ac58c213ce4dd471e75707841fbf23"
        }
      },
      "evidence_windows_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/evidence_windows.json",
      "evidence_windows_sha256": "5355118b362f269ff567704168ca92310eec6a5149a73ffa11fc4e906e92d7c4",
      "pair_summary_path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/summary/replicates/e1-fmv-01-rep1.json",
      "pair_summary_sha256": "a817ad9bb087c52262cc1f2fa21b91bdae57694717d2094aeae30f417b289ed2",
      "prefix_compatibility": "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL",
      "replicate_id": 1,
      "source": "inherited_repair1",
      "stream_id": "e1-fmv-01",
      "unit_id": "e1-fmv-01/rep1"
    }
  ],
  "repair1_authorization_path": "generated/e2-r17-deepseek-v2-replicated-paired-repair1-authorization-20260830.json",
  "repair1_authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
  "repair1_contract_path": "generated/e2-r17-deepseek-v2-replicated-paired-repair1-contract-20260830.json",
  "repair1_contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
  "repair1_run_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830",
  "schema_version": "1.0",
  "scientific_scores_read": false,
  "selection_basis": "pre-outcome integrity/completeness and prefix identity only; no score read or favorable-arm filtering",
  "status": "PASS_REPAIR1_PREFIX_COMPATIBILITY_14_COMPLETE_PAIRS"
}


===== BOUND ARTIFACT: technical_quarantine | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-deepseek-v2-repair1-technical-quarantine-20260831.json =====
{
  "artifact_type": "e2-r17-deepseek-v2-repair1-technical-quarantine",
  "created_at_utc": "2026-08-31T03:45:10+00:00",
  "disposition": "PRESERVE; EXCLUDE FROM VALID MANIFEST; REPAIR2 FRESH-RUNS BOTH ARMS",
  "failed_arm": "mrw",
  "failed_call": {
    "attempt": 0,
    "parse_error": "SkillEditError: edit #0: line 12 does not match 'old_string_prefix', so the line number is likely off. Line 12 is actually '```python', but you gave '```python from openpyxl import load_workbook'. Re-read the N| gutter and fix the line number.",
    "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_2/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
    "prompt_sha256": "4e6385428dcffcd6f434e92d37ccc0e93e787e0271e431e9106fb90dbd632241",
    "provider_status": "completed",
    "response_sha256": "f0e9c07ad4791ff1d58f897639dda318d924a375ef43ca80584fc786c5ae152c",
    "sha256": "00a2b668f3298e97bb3477df97c8ef4ffb5cd8db117f7b3475214f579863054a",
    "task": "skill_patch_apply",
    "total_tokens": 2353
  },
  "heldout_evaluation_units": 0,
  "ledger": {
    "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
    "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
    "max_unit_claimed": 10,
    "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_2/mrw/checkpoints/provider_budget.sqlite3",
    "sha256": "bafca24700c9a3e7cdd529995ce57c243e719b1a8e464041b7e9215a76100c4c",
    "total_claimed": 10,
    "unit_claimed": {
      "e1-fmv-01/rep2/mrw/update": 10
    }
  },
  "operator_semantic_patch_authorized": false,
  "paired_win_c_started": false,
  "provider_call_receipts": [
    {
      "attempt": 0,
      "parse_error": "",
      "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_2/mrw/update/provider_calls/000-skill_trajectory_summary-attempt0.json",
      "prompt_sha256": "7068350d8ca97b9a93952305b55d70ead279d9983e26eda65e5ca3b4de594f67",
      "provider_status": "completed",
      "response_sha256": "db63ff8bde845c2f5d1c1d635c70a2ddf1ab7299314ff29abd65c011adf4e092",
      "sha256": "1d262309d61b5e870ecb131cbea4c2f17f4feeab59738aff48d160634b578271",
      "task": "skill_trajectory_summary",
      "total_tokens": 2094
    },
    {
      "attempt": 0,
      "parse_error": "",
      "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_2/mrw/update/provider_calls/001-skill_trajectory_summary-attempt0.json",
      "prompt_sha256": "c56ded56f3b51afab70b610e9eff7d05cbd73729fb6acdbe6746210cd5602428",
      "provider_status": "completed",
      "response_sha256": "bfae48b0c6635fbbf367e8de3d29ecb27abe3bcb4b48db76e7308026af5ff590",
      "sha256": "3d73f6b6f662da23ce0f92d01bb955f6285e261bae817694d8f7c29503567138",
      "task": "skill_trajectory_summary",
      "total_tokens": 1738
    },
    {
      "attempt": 0,
      "parse_error": "",
      "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_2/mrw/update/provider_calls/002-skill_trajectory_summary-attempt0.json",
      "prompt_sha256": "a01c112ddf3ad1df4e5c8eb5bb7a6c83d61e4dd5dddfbdc4ca253d7ae804e6f9",
      "provider_status": "completed",
      "response_sha256": "a6cb4d7f2d8c6ee3ffcef8535bdf3a4495b6b4530de71cd94ec89ba3efb4d2a5",
      "sha256": "9cb60abbc833467fc565de7c55e7545167539ac48e5a484d95b6b48bf4a15b91",
      "task": "skill_trajectory_summary",
      "total_tokens": 3907
    },
    {
      "attempt": 0,
      "parse_error": "",
      "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_2/mrw/update/provider_calls/003-skill_trajectory_summary-attempt0.json",
      "prompt_sha256": "42c4f457d06eee8794885c2001e60372ca01f8de8ec6bf143d650d77d09d8c55",
      "provider_status": "completed",
      "response_sha256": "63af3101af99a387ab0d9246fec4fdaf3940b3bac370364a3d213195cdd4feca",
      "sha256": "f706d38ce58e5dab310fa94432ad6560321b645dc38dea5b139f5568b3fa008d",
      "task": "skill_trajectory_summary",
      "total_tokens": 2063
    },
    {
      "attempt": 0,
      "parse_error": "",
      "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_2/mrw/update/provider_calls/004-skill_trajectory_summary-attempt0.json",
      "prompt_sha256": "1b41d7a985151d8f6fcd281b533bc0d27bf89de3ebdec5c2085197fe29c10282",
      "provider_status": "completed",
      "response_sha256": "4e2b563894afad8f0deee67d5b9d81a1c5649d9cda8f1a95f4b00f37cf7f4545",
      "sha256": "933f3c6d80a86f724958ab7b5e1f138bda5ed7bd25996cfe4af0ba4e4ba30ca1",
      "task": "skill_trajectory_summary",
      "total_tokens": 1992
    },
    {
      "attempt": 0,
      "parse_error": "",
      "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_2/mrw/update/provider_calls/005-skill_trajectory_summary-attempt0.json",
      "prompt_sha256": "afbfd136d5399b9504e9cfe974b1cdfc43eb4995e3ab79384247be9ace141c3a",
      "provider_status": "completed",
      "response_sha256": "a0cb79770809bf680e9bb4a51024adda81c8e882dfccf0234fb3b13546a1a437",
      "sha256": "78bcf82f50382d662b9d8ab13a056207d6dfa39467f2b472ab88bb0498fb988a",
      "task": "skill_trajectory_summary",
      "total_tokens": 3714
    },
    {
      "attempt": 0,
      "parse_error": "",
      "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_2/mrw/update/provider_calls/006-skill_trajectory_summary-attempt0.json",
      "prompt_sha256": "3210bf3a6e21a41775f499b53c89f0f4050b8a7b0572a2b873bcc5adfeaa2ace",
      "provider_status": "completed",
      "response_sha256": "33ab3994b56835de85a6e4ab82d78eaea7b6b790d436e983b6f0c5e4ab190e9a",
      "sha256": "2ccaf1236a26097bff2646ebc3c1e8e9734306aa81bcb4d558348093e9b8ad95",
      "task": "skill_trajectory_summary",
      "total_tokens": 3573
    },
    {
      "attempt": 0,
      "parse_error": "",
      "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_2/mrw/update/provider_calls/007-skill_trajectory_summary-attempt0.json",
      "prompt_sha256": "fcfca75330677aa51e90278820ea9f327eb3be78aaf121fb55ba126d455b6561",
      "provider_status": "completed",
      "response_sha256": "c1fdd99c00edae95d70c1bc878317cd85536b0924ac295d1a2da55ef75d3ac74",
      "sha256": "eb5b7a65d3a09128fb00db56df857f6d9cd3b0593a0881467aac05e279254bbe",
      "task": "skill_trajectory_summary",
      "total_tokens": 1672
    },
    {
      "attempt": 0,
      "parse_error": "",
      "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_2/mrw/update/provider_calls/008-skill_patch_propose-attempt0.json",
      "prompt_sha256": "17fd5dc3f0010f0de831047ca4ab68f295bab3198f80e656a65984b4962c3e4b",
      "provider_status": "completed",
      "response_sha256": "c907c24931d081337b259fb857f616f446dcbb5940eddee9a65baacca4a04458",
      "sha256": "fcbdef40e1148d00bf5424eb89165b5d1695db9d12a9a29a4fbba86c370f11c0",
      "task": "skill_patch_propose",
      "total_tokens": 4189
    },
    {
      "attempt": 0,
      "parse_error": "SkillEditError: edit #0: line 12 does not match 'old_string_prefix', so the line number is likely off. Line 12 is actually '```python', but you gave '```python from openpyxl import load_workbook'. Re-read the N| gutter and fix the line number.",
      "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_2/mrw/update/provider_calls/009-skill_patch_apply-attempt0.json",
      "prompt_sha256": "4e6385428dcffcd6f434e92d37ccc0e93e787e0271e431e9106fb90dbd632241",
      "provider_status": "completed",
      "response_sha256": "f0e9c07ad4791ff1d58f897639dda318d924a375ef43ca80584fc786c5ae152c",
      "sha256": "00a2b668f3298e97bb3477df97c8ef4ffb5cd8db117f7b3475214f579863054a",
      "task": "skill_patch_apply",
      "total_tokens": 2353
    }
  ],
  "provider_calls": 10,
  "provider_response_ambiguity": false,
  "provider_statuses_completed": 10,
  "provider_tokens": 27295,
  "repair1_authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
  "repair1_contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
  "replicate_id": 2,
  "schema_version": "1.0",
  "scientific_belief_update": "NONE",
  "scientific_endpoint_reached": false,
  "scientific_pair_outcome_exists": false,
  "scientific_scores_read": false,
  "single_arm_resume_authorized": false,
  "skill_post_exists": false,
  "state_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-mrw-r4-20260830/states/e1-fmv-01/replicate_2/mrw",
  "status": "TECHNICAL_QUARANTINE_UPDATER_PATCH_APPLY_FAILURE",
  "stream_id": "e1-fmv-01",
  "unit_id": "e1-fmv-01/rep2",
  "update_completed_exists": false
}


===== BOUND ARTIFACT: superseding_failure | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-deepseek-v2-repair1-updater-patch-apply-failure-20260831.json =====
{
  "artifact_type": "e2-r17-deepseek-v2-repair1-superseding-failure-analysis",
  "classification": [
    "IMPLEMENTATION",
    "RUNTIME_INFRA"
  ],
  "created_at_utc": "2026-08-31T03:45:10+00:00",
  "forbidden_recovery": [
    "resume failed MRW",
    "manual semantic edit of provider patch",
    "replacement MRW only",
    "rerun all completed pairs"
  ],
  "heldout_evaluation_units": 0,
  "paired_win_c_started": false,
  "primary_classification": "IMPLEMENTATION / UPDATER_PATCH_APPLY_FAILURE",
  "provider_calls": 10,
  "provider_response_ambiguity": false,
  "provider_statuses_completed": "10/10",
  "repair1_compatibility_manifest_path": "generated/e2-r17-deepseek-v2-repair1-compatibility-manifest-20260831.json",
  "repair1_compatibility_manifest_sha256": "61e243027e6d42f7923e249f6c88267e6db07ed4bccb32d5a50c8d13bf1695bb",
  "repair1_completed_pairs_preserved": 14,
  "repair1_runner_log_path": "/data/wyt/e2-r17-search-projection/deepseek-v2-mrw-r4-repair1-full-20260830.log",
  "repair1_runner_log_sha256": "9e6c20a9eab7cd1c3d9a293e6344f1aab8a451b0471ea2c2aef0c256cbb94ffd",
  "repair2_permitted_delta": {
    "actor_max_turns": 10,
    "all_scientific_variables_unchanged": true,
    "max_correction_attempts": 1,
    "max_parse_attempts": {
      "from": 1,
      "to": 2
    },
    "state_provider_limit": {
      "from": 190,
      "to": 191
    },
    "updater_provider_unit_limit": {
      "from": 10,
      "to": 11
    }
  },
  "root_cause": "SkillEditError: edit #0: line 12 does not match 'old_string_prefix', so the line number is likely off. Line 12 is actually '```python', but you gave '```python from openpyxl import load_workbook'. Re-read the N| gutter and fix the line number.",
  "schema_version": "1.0",
  "scientific_belief_update": "NONE",
  "scientific_endpoint_reached": false,
  "skill_post": false,
  "status": "STOP_AND_ADJUDICATE_UPDATER_PATCH_APPLY_FAILURE",
  "supersedes_operational_classification": "RUNTIME / AMBIGUOUS_PARTIAL_PROVIDER_UNIT",
  "technical_quarantine_path": "generated/e2-r17-deepseek-v2-repair1-technical-quarantine-20260831.json",
  "technical_quarantine_sha256": "1908a3dfc472f835c204f7f9d5a66a9ee4b37093adb09a8d0c0f297b4b1abd7a",
  "update_completed": false
}


===== BOUND ARTIFACT: runner | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/run_e2_r17_deepseek_v2_repair2_continuation.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
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

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import load_frozen_pool
from research_pipeline.e2_r17_mindmemos_ark_adapter import MindMemOSArkPlanChatAdapter, PLAN_BASE_URL
from research_pipeline.e2_r17_mindmemos_updater import run_projection_update
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from research_pipeline.e2_r17_repair2_manifest import (
    validate_compatibility_manifest,
    validate_quarantine,
    validate_valid_rows,
)
from research_pipeline.e2_r17_search_projection_runner import ProjectionName, project_stream
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_v31_provider_runtime_pilot import bind_mindmemos, evidence_units, validate_updater_runtime
from scripts.run_e2_r17_e1_b_transition_runtime_pilot import sha_file, load_json, atomic_json, require

ARMS = ("win_c", "mrw")
REPLICATES = (0, 1, 2, 3)
UPDATE_ORDER_SALT = "E2-R17-DEEPSEEK-V2-UPDATE-ORDER-v1"
EVAL_ORDER_SALT = "E2-R17-DEEPSEEK-V2-EVAL-PAIR-ORDER-v1"


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def rows_by(path: Path, key: str) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out[str(row[key])] = row
    return out


def canonical_sha(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def ordered_arms(stream_id: str, replicate: int, salt: str, task_id: str = "") -> list[str]:
    return sorted(ARMS, key=lambda arm: hashlib.sha256(f"{salt}|{stream_id}|rep{replicate}|{task_id}|{arm}".encode()).hexdigest())


def acquire_lock(path: Path, contract_sha: str, auth_sha: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError(f"MRW causal-tranche lock exists: {path}; inspect checkpoints before resume") from exc
    os.write(fd, (json.dumps({"pid": os.getpid(), "contract_sha256": contract_sha, "authorization_sha256": auth_sha}, sort_keys=True) + "\n").encode())
    os.fsync(fd)
    return fd


def validate_contract_auth(contract_path: Path, auth_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = load_json(contract_path)
    auth = load_json(auth_path)
    require(contract.get("status") == "FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION", "DeepSeek V2 Repair2 contract not frozen")
    require(auth.get("status") == "AUTHORIZED_E2_R17_DEEPSEEK_V2_REPAIR2", "Repair2 authorization invalid")
    require(auth.get("contract_sha256") == sha_file(contract_path), "authorization/contract mismatch")
    authority = auth.get("authority") or {}
    require(authority.get("scientific_experiment") is True, "MRW causal scientific authority absent")
    require(authority.get("deepseek_v2") is True, "DeepSeek V2 authority bit absent")
    require(authority.get("repair2_continuation") is True, "Repair2 continuation authority absent")
    require(authority.get("gpt_scientific_execution") is False and authority.get("kimi_scientific_execution") is False and authority.get("qwen_scientific_execution") is False, "second scientific backbone forbidden")
    require(authority.get("public_benchmark") is False, "public benchmark forbidden")
    require(authority.get("mrw_causal_comparison") is True, "DeepSeek V2 MRW comparison authority absent")
    require(authority.get("paper_promotion") is False, "MRW causal tranche cannot promote paper")
    scope = auth.get("execution_scope") or {}
    require(scope.get("allowed_modes") == ["e1"], "mode scope drift")
    require(scope.get("allowed_task_ids") == contract["heldout"]["task_ids"], "heldout scope drift")
    require(int(scope.get("exact_k")) == 1 and scope.get("allow_noninitial_skill") is True, "K/noninitial scope drift")
    require(int(scope.get("replicates_per_stream")) == len(REPLICATES), "replicate-count authorization drift")
    bscope = scope.get("provider_budget") or {}
    require(bscope.get("required") is True, "provider budget must be required")
    require(int(bscope.get("total_limit")) == int(contract["budget"]["max_provider_calls_per_state"]), "state total budget drift")
    require(int(bscope.get("per_unit_limit")) == int(contract["budget"]["max_provider_calls_per_unit"]), "state unit budget drift")
    require(int(contract["updater"]["max_parse_attempts"]) == 2, "Repair2 must allow exactly one explicit correction attempt")
    require(int(contract["budget"]["max_provider_calls_per_unit"]) == 11, "Repair2 updater unit limit must be 11")
    require(int(contract["budget"]["max_provider_calls_per_state"]) == 191, "Repair2 state limit must be 191")
    require(int(contract["actor"]["max_turns"]) == 10, "actor max_turns must remain 10")
    prior = contract["v1_identifiability_hold"]
    prior_path = ROOT / prior["path"]
    require(prior_path.is_file() and sha_file(prior_path) == prior["sha256"], "V1 identifiability artifact drift")
    prior_payload = load_json(prior_path)
    require(prior_payload.get("status") == "HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY", "V1 HOLD provenance drift")
    correction = contract["protocol_v2_correction"]
    correction_path = ROOT / correction["path"]
    require(correction_path.is_file() and sha_file(correction_path) == correction["sha256"], "V2 correction memo drift")
    return contract, auth


def load_stream_pools(contract: dict[str, Any], stream_id: str, split: dict[str, Any], support: dict[str, Any]) -> list[Any]:
    pools = []
    for task_id in map(str, split["e1_update_streams"][stream_id]):
        path = Path(contract["e1_a_pool_root"]) / "cases" / task_id / "pool_k8.json"
        require(path.is_file() and sha_file(path) == support["pool_sha256"][task_id], f"E1-A pool SHA drift: {task_id}")
        pool = load_frozen_pool(path)
        require(pool.task_id == task_id and pool.k == 8, f"invalid frozen pool: {task_id}")
        pools.append(pool)
    require(len(pools) == 8, f"stream {stream_id} must have eight pools")
    return pools


def verify_update(path: Path, contract_sha: str, auth_sha: str) -> dict[str, Any]:
    row = load_json(path)
    receipt = Path(row["update_receipt_path"]); skill = Path(row["skill_post_path"])
    require(receipt.is_file() and skill.is_file(), "completed update artifacts missing")
    require(sha_file(receipt) == row["update_receipt_sha256"] and sha_file(skill) == row["skill_post_sha256"], "completed update SHA drift")
    payload = load_json(receipt)
    require(payload.get("contract_sha256") == contract_sha and payload.get("authorization_sha256") == auth_sha, "update receipt binding drift")
    require(payload.get("causal_purity_mode") == "arm_blinded_selected_evidence" and payload.get("arm_metadata_visible_in_transcript") is False, "update causal-purity drift")
    return row


async def ensure_update(*, contract: dict[str, Any], contract_sha: str, auth_sha: str, base_stream_id: str, execution_stream_id: str, replicate: int, arm: str, pools: list[Any], evidence_units_for_arm: list[Any], projection: ProjectionName, initial_skill: str, initial_sha: str, mind_head: str, requested: str, resolved: str, settings: ArkSettings, state_root: Path, ledger: ProviderBudgetLedger) -> dict[str, Any]:
    checkpoint = state_root / "checkpoints/update_completed.json"
    if checkpoint.exists():
        return verify_update(checkpoint, contract_sha, auth_sha)
    update_dir = state_root / "update"
    if update_dir.exists() and any(update_dir.rglob("*")):
        raise RuntimeError(f"partial ambiguous update exists: {base_stream_id}/rep{replicate}/{arm}; no auto-rerun")
    stream = project_stream(stream_id=execution_stream_id, initial_skill_sha256=initial_sha, pools=pools, projection=projection)
    adapter = MindMemOSArkPlanChatAdapter(settings=settings, requested_model=requested, required_resolved_model=resolved, max_parse_attempts=int(contract["updater"]["max_parse_attempts"]), record_dir=update_dir / "provider_calls", provider_budget_ledger=ledger, provider_budget_unit_id=f"{base_stream_id}/rep{replicate}/{arm}/update")
    result = await run_projection_update(stream=stream, pools=pools, initial_skill_md=initial_skill, run_dir=update_dir, llm_adapter=adapter, mindmemos_commit=mind_head, contract_sha256=contract_sha, authorization_sha256=auth_sha, transcript_max_chars=int(contract["updater"]["transcript_max_chars"]), blinded_evidence_units=evidence_units_for_arm)
    receipts = adapter.public_receipts()
    require(result.provider_calls == len(receipts) and result.provider_calls in (10, 11), "Repair2 update must use 10 nominal calls or one explicit 11th correction call")
    parse_errors = [r for r in receipts if r.get("parse_error")]
    correction_used = result.provider_calls == 11
    if correction_used:
        require(len(parse_errors) == 1, "Repair2 correction path must contain exactly one parse error")
        require(parse_errors[0].get("task") == "skill_patch_apply" and int(parse_errors[0].get("attempt")) == 0, "Repair2 correction must follow patch-apply attempt0 failure")
        require(receipts[-1].get("task") == "skill_patch_apply" and int(receipts[-1].get("attempt")) == 1 and not receipts[-1].get("parse_error"), "Repair2 correction attempt1 must succeed")
    else:
        require(not parse_errors and all(int(r.get("attempt")) == 0 for r in receipts), "nominal Repair2 path must be attempt0-only")
    require(all(r.get("provider_status") == "completed" and r.get("hidden_provider_retry_used") is False for r in receipts), "Repair2 provider completion/retry drift")
    row = {"status":"COMPLETED","stream_id":base_stream_id,"execution_stream_id":execution_stream_id,"replicate":replicate,"arm":arm,"update_receipt_path":result.update_receipt_path,"update_receipt_sha256":result.update_receipt_sha256,"skill_post_path":result.skill_post_path,"skill_post_sha256":result.skill_post_sha256,"provider_calls":result.provider_calls,"provider_tokens":result.provider_total_tokens,"attempt0_success":not correction_used,"correction_required":correction_used,"correction_success":correction_used,"correction_failure":False}
    atomic_json(checkpoint, row)
    return verify_update(checkpoint, contract_sha, auth_sha)

def verify_eval(row: dict[str, Any], state_root: Path, skill_sha: str, receipt_sha: str) -> None:
    summary_path = Path(row["summary_path"])
    require(summary_path.is_file() and sha_file(summary_path) == row["summary_sha256"], "eval summary SHA drift")
    summary = load_json(summary_path)
    require(summary.get("status") == "COMPLETED" and summary.get("k") == 1, "eval summary status/K drift")
    require(summary.get("skill_pre_sha256") == skill_sha and summary.get("updater_receipt_sha256") == receipt_sha, "eval learned-skill/receipt binding drift")
    require([str(x["task_id"]) for x in summary.get("tasks") or []] == [row["task_id"]], "eval task drift")
    ref = state_root / "evaluation" / row["task_id"] / "cases" / row["task_id"] / "rollout_0" / "r17_trajectory_ref.json"
    require(ref.is_file() and sha_file(ref) == row["trajectory_ref_sha256"], "eval trajectory-ref SHA drift")
    ref_payload = load_json(ref); trajectory = Path(ref_payload["trajectory_path"])
    require(trajectory.is_file() and sha_file(trajectory) == ref_payload["trajectory_sha256"], "eval trajectory SHA drift")


def ensure_eval(*, contract: dict[str, Any], auth_path: Path, identity_path: Path, actor_python: Path, actor_env: dict[str, str], stream_id: str, arm: str, task_id: str, state_root: Path, update: dict[str, Any], ledger_path: Path) -> dict[str, Any]:
    manifest = state_root / "checkpoints/completed_eval_tasks.jsonl"
    existing = rows_by(manifest, "task_id")
    if task_id in existing:
        verify_eval(existing[task_id], state_root, update["skill_post_sha256"], update["update_receipt_sha256"])
        return existing[task_id]
    eval_root = state_root / "evaluation" / task_id
    summary_path = eval_root / "evaluation_summary.json"
    if eval_root.exists() and any(eval_root.rglob("*")):
        raise RuntimeError(f"partial ambiguous evaluation exists: {stream_id}/{arm}/{task_id}; no auto-rerun")
    command = [str(actor_python), str(ROOT / "scripts/run_e2_r17_actor_pool.py"), "--env-file", contract["env_file"], "--suite-root", contract["suite"]["root"], "--mindmemos-root", contract["mindmemos"]["root"], "--run-root", str(eval_root), "--identity", str(identity_path), "--authorization", str(auth_path), "--skill-source", str(Path(update["skill_post_path"]).parent), "--updater-receipt", update["update_receipt_path"], "--mode", "e1", "--model", contract["actor"]["requested_model"], "--task-id", task_id, "--k", "1", "--prefix-ks", "1", "--max-turns", str(contract["actor"]["max_turns"]), "--max-output-tokens", str(contract["actor"]["max_output_tokens"]), "--concurrency", "1", "--provider-budget-ledger", str(ledger_path), "--provider-total-call-limit", str(contract["budget"]["max_provider_calls_per_state"]), "--provider-per-unit-call-limit", str(contract["budget"]["max_provider_calls_per_unit"]), "--output", str(summary_path)]
    result = subprocess.run(command, cwd=ROOT, env=actor_env, capture_output=True, text=True)
    if result.returncode != 0:
        atomic_json(state_root / "checkpoints" / f"eval_failure_{task_id}.json", {"status":"TECHNICAL_FAILURE","stream_id":stream_id,"arm":arm,"task_id":task_id,"returncode":result.returncode,"stdout_tail":result.stdout[-3000:],"stderr_tail":result.stderr[-3000:],"provider_relaunch_authorized":False})
        raise RuntimeError(f"heldout evaluation technical failure: {stream_id}/{arm}/{task_id}")
    require(summary_path.is_file(), "actor returned without eval summary")
    ref = eval_root / "cases" / task_id / "rollout_0" / "r17_trajectory_ref.json"
    require(ref.is_file(), "actor returned without trajectory ref")
    row = {"task_id":task_id,"summary_path":str(summary_path),"summary_sha256":sha_file(summary_path),"trajectory_ref_path":str(ref),"trajectory_ref_sha256":sha_file(ref),"completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")}
    verify_eval(row, state_root, update["skill_post_sha256"], update["update_receipt_sha256"])
    append_jsonl(manifest, row)
    return row


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    contract, auth = validate_contract_auth(args.contract, args.authorization)
    contract_sha = sha_file(args.contract); auth_sha = sha_file(args.authorization)
    updater_python, _ = validate_updater_runtime({"runtime":contract["updater_runtime"],"mindmemos":contract["mindmemos"]})
    require(Path(sys.executable) == updater_python, "MRW causal runner must use dedicated updater runtime")
    actor_python, actor_env = validate_actor_runtime({"runtime":contract["actor_runtime"]}); actor_env["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    for label, item in contract["bound_code"].items():
        path = ROOT / item["path"]; require(path.is_file() and sha_file(path) == item["sha256"], f"bound code drift: {label}")
    suite_root = Path(contract["suite"]["root"]); split_path = suite_root / "r17_split_manifest.json"
    require(sha_file(suite_root / "suite_manifest.json") == contract["suite"]["suite_manifest_sha256"] and sha_file(split_path) == contract["suite"]["split_manifest_sha256"], "suite/split drift")
    split = load_json(split_path)
    require(list(split["e1_update_streams"].keys()) == contract["streams"], "stream manifest drift")
    require([str(x) for x in split["e1_common_heldout_probe"]] == contract["heldout"]["task_ids"], "heldout list drift")
    support_path = ROOT / contract["e1_a_support"]["path"]; require(support_path.is_file() and sha_file(support_path) == contract["e1_a_support"]["sha256"], "E1-A support artifact drift")
    support = load_json(support_path); require(support.get("status") == "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT", "E1-A support no longer passing")
    mind_root = Path(contract["mindmemos"]["root"]); mind_head = subprocess.check_output(["git","-C",str(mind_root),"rev-parse","HEAD"],text=True).strip()
    require(mind_head == contract["mindmemos"]["commit"] and not subprocess.check_output(["git","-C",str(mind_root),"status","--short"],text=True).strip(), "MindMemOS drift/dirty")
    bind_mindmemos(mind_root)
    identity_path = ROOT / contract["model_identity"]["path"]; require(identity_path.is_file() and sha_file(identity_path) == contract["model_identity"]["sha256"], "identity artifact drift")
    identity = load_json(identity_path); require(identity.get("status") == "PASS_CURRENT_REVIEW_TRANCHE", "model identity not qualified")
    model_row = identity["requested_and_resolved"][contract["updater"]["requested_model"]]; requested=str(model_row["requested"]); resolved=str(model_row["resolved"])
    require(resolved == contract["updater"]["resolved_model"] == contract["actor"]["resolved_model"], "resolved-model drift")
    load_env_file(Path(contract["env_file"])); raw=ArkSettings.from_env(required=True); require(raw.base_url.rstrip("/") == PLAN_BASE_URL, "non-Ark-Plan route")
    settings=ArkSettings(api_key=raw.api_key,base_url=raw.base_url,default_model=raw.default_model,timeout_seconds=300.0,max_retries=0)
    initial_path=Path(contract["initial_skill"]["path"]); require(initial_path.is_file() and sha_file(initial_path)==contract["initial_skill"]["sha256"], "initial skill drift")
    initial_skill=initial_path.read_text(encoding="utf-8"); initial_sha=sha_file(initial_path)
    repair1 = contract["repair1_parent"]
    compatibility_item = contract["compatibility_manifest"]
    quarantine_item = contract["technical_quarantine"]
    compatibility_path = ROOT / compatibility_item["path"]
    quarantine_path = ROOT / quarantine_item["path"]
    inherited_rows = validate_compatibility_manifest(
        path=compatibility_path,
        expected_sha=compatibility_item["sha256"],
        repair1_contract_sha=repair1["contract_sha256"],
        repair1_authorization_sha=repair1["authorization_sha256"],
        heldout_task_ids=contract["heldout"]["task_ids"],
    )
    quarantine = validate_quarantine(quarantine_path, quarantine_item["sha256"])
    run_root=Path(contract["run_root"]); lock_path=run_root/".exclusive.lock"; lock_fd=acquire_lock(lock_path,contract_sha,auth_sha); success=False
    unit_manifest=run_root/"checkpoints/completed_replicates.jsonl"
    valid_manifest=Path(contract["valid_replicate_manifest"]["path"])
    completed_units=rows_by(unit_manifest,"unit_id")
    valid_units=rows_by(valid_manifest,"unit_id")
    if not completed_units and not valid_units:
        for inherited in inherited_rows:
            append_jsonl(valid_manifest, inherited)
            valid_units[inherited["unit_id"]] = inherited
            completed = {"unit_id":inherited["unit_id"],"stream_id":inherited["stream_id"],"replicate":inherited["replicate_id"],"summary_path":inherited["pair_summary_path"],"summary_sha256":inherited["pair_summary_sha256"],"source":"repair1_inherited","completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")}
            append_jsonl(unit_manifest, completed)
            completed_units[completed["unit_id"]] = completed
    require({row["unit_id"] for row in inherited_rows} == {unit_id for unit_id,row in valid_units.items() if row.get("source") == "repair1_inherited"}, "runtime inherited set differs from frozen compatibility manifest")
    validate_valid_rows(list(valid_units.values()), streams=contract["streams"], quarantine=quarantine, require_complete=False)

    try:
        for row in completed_units.values():
            path=Path(row["summary_path"]); require(path.is_file() and sha_file(path)==row["summary_sha256"], f"completed replicate summary drift: {row['unit_id']}")
        for stream_id in contract["streams"]:
            pools=load_stream_pools(contract,stream_id,split,support)
            win_units,mrw_units,evidence_receipts=evidence_units(pools,final_block_cap_tokens=int(contract["renderer"]["final_block_cap_tokens"]),transcript_max_chars=int(contract["updater"]["transcript_max_chars"]))
            stream_root=run_root/"states"/stream_id; evidence_path=stream_root/"evidence_windows.json"
            win_bundle_sha=canonical_sha([u.__dict__ for u in win_units]); mrw_bundle_sha=canonical_sha([u.__dict__ for u in mrw_units])
            evidence_payload={"stream_id":stream_id,"win_c_evidence_bundle_sha256":win_bundle_sha,"mrw_evidence_bundle_sha256":mrw_bundle_sha,"receipts":evidence_receipts,"mrw_provider_execution_authorized":True,"primary_control":"fresh_contemporaneous_win_c","replicates_per_stream":len(REPLICATES)}
            if evidence_path.exists():
                existing=load_json(evidence_path)
                require(existing.get("win_c_evidence_bundle_sha256")==win_bundle_sha and existing.get("mrw_evidence_bundle_sha256")==mrw_bundle_sha, "frozen evidence-window drift")
            else:
                atomic_json(evidence_path,evidence_payload)
            arm_inputs={
                "win_c": (win_units, ProjectionName.WINNER_ONLY),
                "mrw": (mrw_units, ProjectionName.MIXED_REJECTED_WITNESS),
            }
            for replicate in REPLICATES:
                unit_id=f"{stream_id}/rep{replicate}"
                if unit_id in completed_units:
                    continue
                rep_root=stream_root/f"replicate_{replicate}"
                execution_stream_id=f"{stream_id}::rep{replicate}"
                updates: dict[str,dict[str,Any]]={}
                for arm in ordered_arms(stream_id,replicate,UPDATE_ORDER_SALT):
                    state_root=rep_root/arm; ledger_path=state_root/"checkpoints/provider_budget.sqlite3"
                    ledger=ProviderBudgetLedger(path=ledger_path,contract_sha256=contract_sha,authorization_sha256=auth_sha,total_limit=int(contract["budget"]["max_provider_calls_per_state"]),per_unit_limit=int(contract["budget"]["max_provider_calls_per_unit"]),allow_create=not ledger_path.exists())
                    units_for_arm, projection_for_arm = arm_inputs[arm]
                    updates[arm]=await ensure_update(contract=contract,contract_sha=contract_sha,auth_sha=auth_sha,base_stream_id=stream_id,execution_stream_id=execution_stream_id,replicate=replicate,arm=arm,pools=pools,evidence_units_for_arm=units_for_arm,projection=projection_for_arm,initial_skill=initial_skill,initial_sha=initial_sha,mind_head=mind_head,requested=requested,resolved=resolved,settings=settings,state_root=state_root,ledger=ledger)
                for task_id in contract["heldout"]["task_ids"]:
                    for arm in ordered_arms(stream_id,replicate,EVAL_ORDER_SALT,task_id):
                        state_root=rep_root/arm
                        ensure_eval(contract=contract,auth_path=args.authorization,identity_path=identity_path,actor_python=actor_python,actor_env=actor_env,stream_id=execution_stream_id,arm=arm,task_id=task_id,state_root=state_root,update=updates[arm],ledger_path=state_root/"checkpoints/provider_budget.sqlite3")
                states=[]
                for arm in ARMS:
                    state_root=rep_root/arm; eval_manifest=state_root/"checkpoints/completed_eval_tasks.jsonl"; eval_rows=rows_by(eval_manifest,"task_id")
                    require(set(eval_rows)==set(contract["heldout"]["task_ids"]), f"heldout completion set invalid: {unit_id}/{arm}")
                    for row in eval_rows.values(): verify_eval(row,state_root,updates[arm]["skill_post_sha256"],updates[arm]["update_receipt_sha256"])
                    ledger=ProviderBudgetLedger(path=state_root/"checkpoints/provider_budget.sqlite3",contract_sha256=contract_sha,authorization_sha256=auth_sha,total_limit=int(contract["budget"]["max_provider_calls_per_state"]),per_unit_limit=int(contract["budget"]["max_provider_calls_per_unit"]),allow_create=False)
                    states.append({"arm":arm,"update_receipt_sha256":updates[arm]["update_receipt_sha256"],"skill_post_sha256":updates[arm]["skill_post_sha256"],"completed_heldout_tasks":len(eval_rows),"eval_manifest_path":str(eval_manifest),"eval_manifest_sha256":sha_file(eval_manifest),"provider_budget":ledger.snapshot().to_dict()})
                rep_summary={"schema_version":"1.0","artifact_type":"e2-r17-deepseek-v2-replicated-paired-unit","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"COMPLETED","unit_id":unit_id,"stream_id":stream_id,"execution_stream_id":execution_stream_id,"replicate":replicate,"pool_ids":[p.pool_id for p in pools],"evidence_windows_sha256":sha_file(evidence_path),"update_order":ordered_arms(stream_id,replicate,UPDATE_ORDER_SALT),"heldout_task_ids":contract["heldout"]["task_ids"],"states":states,"mrw_executed":True,"primary_control":"win_c","paper_promotion_authority":False}
                rep_summary_path=run_root/"summary/replicates"/f"{stream_id}-rep{replicate}.json"; atomic_json(rep_summary_path,rep_summary)
                manifest_row={"unit_id":unit_id,"stream_id":stream_id,"replicate":replicate,"summary_path":str(rep_summary_path),"summary_sha256":sha_file(rep_summary_path),"source":"repair2_fresh","completed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")}
                valid_row={"unit_id":unit_id,"stream_id":stream_id,"replicate_id":replicate,"source":"repair2_fresh","pair_summary_path":str(rep_summary_path),"pair_summary_sha256":sha_file(rep_summary_path),"arms":{}}
                for arm in ARMS:
                    state_root=rep_root/arm
                    update=updates[arm]
                    valid_row["arms"][arm]={"state_root":str(state_root),"skill_sha256":update["skill_post_sha256"],"update_receipt_sha256":update["update_receipt_sha256"],"eval_manifest_path":str(state_root/"checkpoints/completed_eval_tasks.jsonl"),"eval_manifest_sha256":sha_file(state_root/"checkpoints/completed_eval_tasks.jsonl"),"updater_calls":int(update["provider_calls"]),"attempt0_success":bool(update.get("attempt0_success",int(update["provider_calls"])==10)),"correction_required":bool(update.get("correction_required",int(update["provider_calls"])==11))}
                if unit_id not in valid_units:
                    append_jsonl(valid_manifest,valid_row); valid_units[unit_id]=valid_row
                append_jsonl(unit_manifest,manifest_row); completed_units[unit_id]=manifest_row
        expected={f"{stream}/rep{rep}" for stream in contract["streams"] for rep in REPLICATES}
        require(set(completed_units)==expected, "DeepSeek V2 Repair2 did not complete all 48 paired replicate units")
        validate_valid_rows(list(valid_units.values()), streams=contract["streams"], quarantine=quarantine, require_complete=True)
        reliability={arm:{"attempt0_success_count":0,"correction_required_count":0,"correction_success_count":0,"correction_failure_count":0} for arm in ARMS}
        for row in valid_units.values():
            for arm in ARMS:
                a=row["arms"][arm]
                if a.get("correction_required"):
                    reliability[arm]["correction_required_count"]+=1; reliability[arm]["correction_success_count"]+=1
                else:
                    reliability[arm]["attempt0_success_count"]+=1
        final={"schema_version":"1.0","artifact_type":"e2-r17-deepseek-v2-repair2-continuation-summary","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION","contract_sha256":contract_sha,"authorization_sha256":auth_sha,"streams":len(contract["streams"]),"replicates_per_stream":len(REPLICATES),"paired_replicate_units":len(expected),"inherited_paired_units":sum(row.get("source")=="repair1_inherited" for row in valid_units.values()),"fresh_paired_units":sum(row.get("source")=="repair2_fresh" for row in valid_units.values()),"arms":list(ARMS),"learned_states":len(expected)*2,"heldout_tasks_per_state":len(contract["heldout"]["task_ids"]),"heldout_rollout_units":len(expected)*2*len(contract["heldout"]["task_ids"]),"mrw_executed":True,"primary_control":"win_c","inference_performed":False,"paper_promotion_authority":False,"completed_replicate_manifest":str(unit_manifest),"completed_replicate_manifest_sha256":sha_file(unit_manifest),"valid_replicate_manifest":str(valid_manifest),"valid_replicate_manifest_sha256":sha_file(valid_manifest),"runtime_reliability":reliability,"repair1_quarantined_patch_apply_failures":{"win_c":0,"mrw":1}}
        atomic_json(run_root/"summary/deepseek_v2_repair2_continuation_summary.json",final); success=True; return final
    finally:
        os.close(lock_fd)
        if success: lock_path.unlink(missing_ok=True)


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--contract",type=Path,required=True); parser.add_argument("--authorization",type=Path,required=True); args=parser.parse_args()
    payload=asyncio.run(main_async(args)); print(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)); return 0 if payload["status"]=="COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION" else 2


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: analyzer | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/analyze_e2_r17_deepseek_v2_repair2.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_repair2_manifest import validate_quarantine, validate_valid_rows

T_CRITICAL_095_DF11 = 1.7958848187036691
ALPHA = 0.05
EPSILON = 1.0 / 18.0
BOOTSTRAP_SEED = 1718
BOOTSTRAP_REPS = 100000
ARMS = ("win_c", "mrw")
REPLICATES = (0, 1, 2, 3)


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rows_by(path: Path, key: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[str(row[key])] = row
    return rows


def quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lo = int(math.floor(position)); hi = int(math.ceil(position))
    if lo == hi:
        return ordered[lo]
    frac = position - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def bootstrap_ci_95(differences: list[float]) -> tuple[float, float]:
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(differences)
    means = [statistics.fmean(differences[rng.randrange(n)] for _ in range(n)) for _ in range(BOOTSTRAP_REPS)]
    return quantile(means, 0.025), quantile(means, 0.975)


def paired_t_ci_90(differences: list[float]) -> tuple[float, float, float, float]:
    n = len(differences)
    mean = statistics.fmean(differences)
    sd = statistics.stdev(differences) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else float("nan")
    half = T_CRITICAL_095_DF11 * se
    return mean, sd, mean - half, mean + half


def exact_sign_flip_p(differences: list[float], *, direction: str) -> float:
    observed = statistics.fmean(differences)
    values = []
    for signs in itertools.product((-1.0, 1.0), repeat=len(differences)):
        values.append(statistics.fmean(sign * value for sign, value in zip(signs, differences)))
    tol = 1e-15
    if direction == "positive":
        return sum(value >= observed - tol for value in values) / len(values)
    if direction == "negative":
        return sum(value <= observed + tol for value in values) / len(values)
    raise ValueError(direction)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--run-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    contract = load_json(args.contract); auth = load_json(args.authorization); summary = load_json(args.run_summary)
    contract_sha = sha_file(args.contract); auth_sha = sha_file(args.authorization)
    require(contract.get("status") == "FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION", "DeepSeek V2 Repair2 contract not frozen")
    require(auth.get("contract_sha256") == contract_sha, "authorization contract binding drift")
    require(summary.get("status") == "COMPLETED_PENDING_SEPARATE_DEEPSEEK_V2_ADJUDICATION", "DeepSeek V2 run incomplete")
    require(summary.get("contract_sha256") == contract_sha and summary.get("authorization_sha256") == auth_sha, "MRW summary binding drift")
    require(summary.get("mrw_executed") is True and summary.get("primary_control") == "win_c", "DeepSeek V2 summary treatment/control drift")
    require(summary.get("inference_performed") is False, "runner must not perform DeepSeek V2 inference")
    require(int(summary.get("replicates_per_stream")) == len(REPLICATES), "replicate count drift")

    prior = contract["v1_identifiability_hold"]
    prior_path = Path(prior["path"])
    require(prior_path.is_file() and sha_file(prior_path) == prior["sha256"], "V1 identifiability artifact drift")
    require(load_json(prior_path).get("status") == "HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY", "V1 HOLD provenance drift")

    valid_path = Path(summary["valid_replicate_manifest"])
    require(valid_path.is_file() and sha_file(valid_path) == summary["valid_replicate_manifest_sha256"], "valid manifest SHA drift")
    require(str(valid_path) == str(contract["valid_replicate_manifest"]["path"]), "valid manifest path drift")
    valid_map = rows_by(valid_path, "unit_id")
    quarantine_item = contract["technical_quarantine"]
    quarantine = validate_quarantine(ROOT / quarantine_item["path"], quarantine_item["sha256"])
    validate_valid_rows(list(valid_map.values()), streams=contract["streams"], quarantine=quarantine, require_complete=True)
    heldout = [str(x) for x in contract["heldout"]["task_ids"]]
    stream_rows: list[dict[str, Any]] = []
    differences: list[float] = []
    for stream_id in contract["streams"]:
        replicate_rows: list[dict[str, Any]] = []
        replicate_diffs: list[float] = []
        for replicate in REPLICATES:
            unit_id = f"{stream_id}/rep{replicate}"
            require(unit_id in valid_map, f"valid manifest missing pair: {unit_id}")
            valid_pair = valid_map[unit_id]
            arm_scores: dict[str, list[float]] = {}
            for arm in ARMS:
                arm_binding = valid_pair["arms"][arm]
                state_root = Path(arm_binding["state_root"])
                checkpoint_path = state_root / "checkpoints/update_completed.json"
                require(checkpoint_path.is_file(), f"missing update checkpoint: {unit_id}/{arm}")
                checkpoint = load_json(checkpoint_path)
                require(sha_file(Path(checkpoint["skill_post_path"])) == arm_binding["skill_sha256"], f"skill SHA drift: {unit_id}/{arm}")
                require(sha_file(Path(checkpoint["update_receipt_path"])) == arm_binding["update_receipt_sha256"], f"receipt SHA drift: {unit_id}/{arm}")
                manifest_path = Path(arm_binding["eval_manifest_path"])
                require(manifest_path.is_file() and sha_file(manifest_path) == arm_binding["eval_manifest_sha256"], f"eval manifest drift: {unit_id}/{arm}")
                manifest = rows_by(manifest_path, "task_id")
                require(set(manifest) == set(heldout), f"heldout completion mismatch: {stream_id}/rep{replicate}/{arm}")
                scores: list[float] = []
                for task_id in heldout:
                    row = manifest[task_id]
                    require(sha_file(Path(row["summary_path"])) == row["summary_sha256"], "eval summary SHA drift")
                    ref_path = Path(row["trajectory_ref_path"])
                    require(ref_path.is_file() and sha_file(ref_path) == row["trajectory_ref_sha256"], "trajectory-ref SHA drift")
                    ref = load_json(ref_path)
                    trajectory = Path(ref["trajectory_path"])
                    require(trajectory.is_file() and sha_file(trajectory) == ref["trajectory_sha256"], "trajectory SHA drift")
                    score = float(ref["score"])
                    require(score in (0.0, 1.0), "DeepSeek V2 endpoint score must be binary")
                    scores.append(score)
                arm_scores[arm] = scores
            j_win = statistics.fmean(arm_scores["win_c"])
            j_mrw = statistics.fmean(arm_scores["mrw"])
            diff = j_mrw - j_win
            replicate_diffs.append(diff)
            replicate_rows.append({
                "replicate": replicate,
                "j_win_c": j_win,
                "j_mrw": j_mrw,
                "difference_mrw_minus_win_c": diff,
                "win_c_successes": int(sum(arm_scores["win_c"])),
                "mrw_successes": int(sum(arm_scores["mrw"])),
            })
        stream_diff = statistics.fmean(replicate_diffs)
        differences.append(stream_diff)
        stream_rows.append({
            "stream_id": stream_id,
            "replicate_differences": replicate_diffs,
            "mean_difference_mrw_minus_win_c": stream_diff,
            "replicates": replicate_rows,
        })

    require(len(differences) == 12, "MRW causal analysis requires exactly 12 paired stream units")
    mean, sd, tost_low, tost_high = paired_t_ci_90(differences)
    bootstrap_low, bootstrap_high = bootstrap_ci_95(differences)
    p_positive = exact_sign_flip_p(differences, direction="positive")
    p_negative = exact_sign_flip_p(differences, direction="negative")
    equivalent = tost_low > -EPSILON and tost_high < EPSILON
    # A statistically positive but TOST-equivalent effect is practically null by
    # the predeclared 1/18 margin and must not be promoted as a method GO.
    superiority = mean > 0 and p_positive <= ALPHA and bootstrap_low > 0 and not equivalent
    harmful = mean < 0 and p_negative <= ALPHA and not equivalent

    if superiority:
        status = "GO_MRW_CAUSAL_EFFECT_SUPPORTED"
        interpretation = "Contemporaneous exact-same-pool MRW improves future frozen-skill utility over fresh WIN-C under the preregistered paired superiority rule."
    elif equivalent:
        status = "STOP_MRW_PRACTICALLY_NULL"
        interpretation = "MRW and contemporaneous WIN-C are practically equivalent within the preregistered ±1/18 margin; the central MRW repair is stopped as practically null on this controlled substrate."
    elif harmful:
        status = "STOP_MRW_HARMFUL"
        interpretation = "MRW is significantly harmful relative to contemporaneous WIN-C under the preregistered negative-direction sign-flip test; the central MRW repair is stopped."
    else:
        status = "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS"
        interpretation = "MRW superiority is not established and practical equivalence is not established; the causal result remains inconclusive without changing the frozen experiment post hoc."

    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-deepseek-v2-repair2-adjudication",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "contract_sha256": contract_sha,
        "authorization_sha256": auth_sha,
        "run_summary_path": str(args.run_summary),
        "run_summary_sha256": sha_file(args.run_summary),
        "valid_replicate_manifest_path": str(valid_path),
        "valid_replicate_manifest_sha256": sha_file(valid_path),
        "runtime_reliability": summary.get("runtime_reliability"),
        "repair1_quarantined_patch_apply_failures": summary.get("repair1_quarantined_patch_apply_failures"),
        "v1_identifiability_hold_path": str(prior_path),
        "v1_identifiability_hold_sha256": prior["sha256"],
        "replicates_per_stream": len(REPLICATES),
        "scientific_unit": "12 stream-level effects; each stream effect averages four independent contemporaneous WIN-C/MRW replicate pairs, each evaluated on the same 18 deterministic-workbook-verifier probes",
        "primary_estimand": "mean_s[(1/4) sum_r (J_sr(MRW)-J_sr(WIN-C))] over the 12 frozen streams",
        "n_pairs": 12,
        "mean_difference": mean,
        "median_difference": statistics.median(differences),
        "sd_difference": sd,
        "positive_streams": sum(value > 0 for value in differences),
        "zero_streams": sum(value == 0 for value in differences),
        "negative_streams": sum(value < 0 for value in differences),
        "primary_superiority": {
            "alpha": ALPHA,
            "exact_one_sided_sign_flip_p": p_positive,
            "mean_positive": mean > 0,
            "paired_bootstrap_95_ci": [bootstrap_low, bootstrap_high],
            "bootstrap_seed": BOOTSTRAP_SEED,
            "bootstrap_reps": BOOTSTRAP_REPS,
            "pass": superiority,
        },
        "practical_null": {
            "epsilon": EPSILON,
            "paired_t_90_ci": [tost_low, tost_high],
            "t_critical_0_95_df11": T_CRITICAL_095_DF11,
            "paired_tost_equivalence_pass": equivalent,
        },
        "harm_check": {
            "exact_one_sided_negative_sign_flip_p": p_negative,
            "significantly_harmful": harmful,
        },
        "per_stream": stream_rows,
        "historical_win_a_win_b_role": "V1 nuisance-variance/sample-size prior only; excluded from the primary V2 estimand and decision rule",
        "interpretation": interpretation,
        "authority": {
            "central_mechanism_adjudicated": status in {"GO_MRW_CAUSAL_EFFECT_SUPPORTED", "STOP_MRW_PRACTICALLY_NULL", "STOP_MRW_HARMFUL"},
            "prepare_public_benchmark_contract": status == "GO_MRW_CAUSAL_EFFECT_SUPPORTED",
            "execute_public_benchmark": False,
            "paper_promotion": False,
            "submission": False,
        },
    }
    atomic_json(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if status == "GO_MRW_CAUSAL_EFFECT_SUPPORTED" else (3 if status.startswith("STOP_") else 4)


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: preflight | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/preflight_e2_r17_deepseek_v2_repair2.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_repair2_manifest import (
    validate_compatibility_manifest,
    validate_quarantine,
    validate_valid_rows,
)
from scripts.run_e2_r17_deepseek_v2_repair2_continuation import (
    ARMS,
    REPLICATES,
    load_stream_pools,
    validate_contract_auth,
)
from scripts.run_e2_r17_v31_provider_runtime_pilot import validate_updater_runtime
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime as validate_actor_runtime
from scripts.run_e2_r17_e1_b_transition_runtime_pilot import load_json, sha_file


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--review-summary", type=Path)
    parser.add_argument("--stage", choices=("draft", "frozen"), required=True)
    args = parser.parse_args()

    contract_path = resolve(args.contract)
    contract = load_json(contract_path)
    if args.stage == "draft":
        require(contract.get("status") == "DRAFT_PENDING_DUAL_REPAIR2_REVIEW", "Repair2 draft status drift")
        require(args.authorization is None, "draft preflight must not accept scientific authorization")
        authority = contract.get("authority") or {}
        require(authority and all(value is False for value in authority.values()), "draft authority must remain all false")
        if args.review_summary:
            review_path = resolve(args.review_summary)
            review = load_json(review_path)
            require(review.get("all_pass_to_separately_authorized_repair2") is True, "dual review did not authorize freezing")
            require(review.get("draft_contract_sha256") == sha_file(contract_path), "dual review draft binding drift")
    else:
        require(args.authorization is not None, "frozen preflight requires authorization")
        auth_path = resolve(args.authorization)
        contract, _ = validate_contract_auth(contract_path, auth_path)

    env_file = contract.get("env_file")
    require(isinstance(env_file, str) and env_file.strip(), "contract env_file missing/empty")
    env_path = Path(env_file)
    if not env_path.is_absolute():
        env_path = ROOT / env_path
    require(env_path.is_file(), f"contract env_file not found: {env_path}")

    updater_python, _ = validate_updater_runtime({"runtime": contract["updater_runtime"], "mindmemos": contract["mindmemos"]})
    actor_python, _ = validate_actor_runtime({"runtime": contract["actor_runtime"]})
    require(Path(sys.executable) == updater_python, f"preflight must run under updater runtime: observed={sys.executable} expected={updater_python}")

    for label, item in contract["bound_code"].items():
        path = ROOT / item["path"]
        require(path.is_file() and sha_file(path) == item["sha256"], f"bound code drift: {label}")

    repair1 = contract["repair1_parent"]
    repair1_contract = ROOT / repair1["contract_path"]
    repair1_auth = ROOT / repair1["authorization_path"]
    require(repair1_contract.is_file() and sha_file(repair1_contract) == repair1["contract_sha256"], "Repair1 contract drift")
    require(repair1_auth.is_file() and sha_file(repair1_auth) == repair1["authorization_sha256"], "Repair1 authorization drift")

    compatibility_item = contract["compatibility_manifest"]
    inherited = validate_compatibility_manifest(
        path=ROOT / compatibility_item["path"],
        expected_sha=compatibility_item["sha256"],
        repair1_contract_sha=repair1["contract_sha256"],
        repair1_authorization_sha=repair1["authorization_sha256"],
        heldout_task_ids=contract["heldout"]["task_ids"],
    )
    quarantine_item = contract["technical_quarantine"]
    quarantine = validate_quarantine(ROOT / quarantine_item["path"], quarantine_item["sha256"])
    validate_valid_rows(inherited, streams=contract["streams"], quarantine=quarantine, require_complete=False)
    require(len(inherited) == 14, "preflight requires exactly 14 frozen inherited pairs")
    require(f"{quarantine['stream_id']}/rep{int(quarantine['replicate_id'])}" not in {row["unit_id"] for row in inherited}, "quarantine leaked into inherited set")

    failure_item = contract["superseding_failure_analysis"]
    failure_path = ROOT / failure_item["path"]
    require(failure_path.is_file() and sha_file(failure_path) == failure_item["sha256"], "superseding failure analysis drift")
    failure = load_json(failure_path)
    require(failure.get("primary_classification") == "IMPLEMENTATION / UPDATER_PATCH_APPLY_FAILURE", "failure classification drift")
    require(failure.get("provider_response_ambiguity") is False and failure.get("scientific_belief_update") == "NONE", "failure semantics drift")

    split = load_json(Path(contract["suite"]["root"]) / "r17_split_manifest.json")
    support = load_json(ROOT / contract["e1_a_support"]["path"])
    for stream in contract["streams"]:
        require(len(load_stream_pools(contract, stream, split, support)) == 8, f"pool count drift: {stream}")

    require(len(contract["streams"]) == 12 and len(REPLICATES) == 4 and len(ARMS) == 2, "design cardinality drift")
    require(int(contract["replication"]["paired_replicate_units"]) == 48 and int(contract["replication"]["learned_states"]) == 96, "replication summary drift")
    require(len(contract["heldout"]["task_ids"]) == 18, "heldout task count drift")
    require(int(contract["updater"]["max_parse_attempts"]) == 2, "max_parse_attempts must be 2")
    require(int(contract["budget"]["max_provider_calls_per_unit"]) == 11, "provider unit budget must be 11")
    require(int(contract["budget"]["max_provider_calls_per_state"]) == 191, "state budget must be 191")
    require(int(contract["budget"]["hard_max_provider_calls_structural"]) == 96 * 191, "budget structure drift")
    require(int(contract["actor"]["max_turns"]) == 10 and int(contract["actor"]["max_output_tokens"]) == 8192, "actor protocol drift")
    require(contract["updater"]["provider_retry_limit"] == 0 and contract["actor"]["provider_retry_limit"] == 0, "provider retry drift")
    require(contract["updater"]["requested_model"] == "deepseek-v4-pro" and contract["actor"]["requested_model"] == "deepseek-v4-pro", "scientific model drift")

    identity_item = contract["model_identity"]
    identity_path = ROOT / identity_item["path"]
    require(identity_path.is_file() and sha_file(identity_path) == identity_item["sha256"], "fresh model identity drift")
    identity = load_json(identity_path)
    require(identity.get("status") == identity_item["required_status"], "fresh model identity not qualified")
    model_row = identity["requested_and_resolved"]["deepseek-v4-pro"]
    require(model_row["requested"] == "deepseek-v4-pro", "requested model identity drift")
    require(model_row["resolved"] == contract["updater"]["resolved_model"] == contract["actor"]["resolved_model"], "resolved family drift")
    qualification_path = ROOT / identity_item["qualification_path"]
    require(qualification_path.is_file() and sha_file(qualification_path) == identity_item["qualification_sha256"], "fresh DeepSeek qualification drift")
    qualification = load_json(qualification_path)
    deep_rows = [row for row in qualification.get("models") or [] if row.get("requested_model") == "deepseek-v4-pro"]
    require(len(deep_rows) == 1 and deep_rows[0].get("status") == "PASS", "fresh DeepSeek identity call not PASS")
    deep = deep_rows[0]
    require(deep.get("resolved_model") == model_row["resolved"], "fresh DeepSeek resolved suffix drift")
    require(int(deep.get("max_output_tokens")) == 8192 and deep.get("thinking_requested") == "disabled", "fresh DeepSeek output/thinking qualification drift")
    require(int(deep.get("provider_retry_limit")) == 0 and deep.get("hidden_provider_retry_used") is False, "identity provider retry drift")
    require(deep.get("benchmark_data_accessed") is False and deep.get("scientific_outcome") is False, "identity qualification crossed scientific boundary")

    process_text = subprocess.run(
        ["ps", "-eo", "pid,ppid,etime,stat,cmd"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    active = [
        line for line in process_text.splitlines()
        if ("run_e2_r17_deepseek_v2_repair2_continuation.py" in line or "run_e2_r17_actor_pool.py" in line)
        and str(Path(__file__).name) not in line
    ]
    require(not active, f"active duplicate Repair2/actor process: {active}")

    run_root = Path(contract["run_root"])
    require(not run_root.exists() or not any(run_root.rglob("*")), f"Repair2 run root not fresh: {run_root}")
    valid_path = Path(contract["valid_replicate_manifest"]["path"])
    require(not valid_path.exists(), f"valid manifest already exists before Repair2 execution: {valid_path}")

    print("PREFLIGHT_PASS")
    print("stage", args.stage)
    print("updater_python", updater_python)
    print("actor_python", actor_python)
    print("streams", 12, "replicates", 4, "valid_pairs", 48, "states", 96, "heldout_rollouts", 1728)
    print("inherited_pairs", len(inherited), "fresh_pairs", 34)
    print("quarantine", quarantine["status"])
    print("max_parse_attempts", 2, "updater_budget", 11, "state_budget", 191, "actor_max_turns", 10)
    print("run_root", run_root)
    print("contract_sha", sha_file(contract_path))
    if args.stage == "frozen":
        print("authorization_sha", sha_file(resolve(args.authorization)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: manifest_validator | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/e2_r17_repair2_manifest.py =====
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

ARMS = ("win_c", "mrw")
REPLICATES = (0, 1, 2, 3)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rows_by(path: Path, key: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        value = str(row[key])
        require(value not in rows, f"duplicate {key}: {value}")
        rows[value] = row
    return rows


def _validate_eval_manifest(path: Path, expected_sha: str, heldout: set[str]) -> None:
    require(path.is_file() and sha_file(path) == expected_sha, f"eval manifest SHA drift: {path}")
    rows = rows_by(path, "task_id")
    require(set(rows) == heldout, f"heldout set drift: {path}")
    for task_id, row in rows.items():
        summary_path = Path(row["summary_path"])
        require(summary_path.is_file() and sha_file(summary_path) == row["summary_sha256"], f"eval summary drift: {task_id}")
        summary = load_json(summary_path)
        require(summary.get("status") == "COMPLETED" and int(summary.get("k")) == 1, f"eval status/K drift: {task_id}")
        ref_path = Path(row["trajectory_ref_path"])
        require(ref_path.is_file() and sha_file(ref_path) == row["trajectory_ref_sha256"], f"trajectory ref drift: {task_id}")
        ref = load_json(ref_path)
        trajectory = Path(ref["trajectory_path"])
        require(trajectory.is_file() and sha_file(trajectory) == ref["trajectory_sha256"], f"trajectory drift: {task_id}")
        # Deliberately do not read ref["score"] here. Inheritance is pre-outcome.


def validate_compatibility_manifest(
    *,
    path: Path,
    expected_sha: str,
    repair1_contract_sha: str,
    repair1_authorization_sha: str,
    heldout_task_ids: Iterable[str],
) -> list[dict[str, Any]]:
    require(path.is_file() and sha_file(path) == expected_sha, "compatibility manifest SHA drift")
    payload = load_json(path)
    require(payload.get("status") == "PASS_REPAIR1_PREFIX_COMPATIBILITY_14_COMPLETE_PAIRS", "compatibility status not PASS")
    require(payload.get("scientific_scores_read") is False, "compatibility audit read scientific scores")
    require(payload.get("repair1_contract_sha256") == repair1_contract_sha, "Repair1 contract binding drift")
    require(payload.get("repair1_authorization_sha256") == repair1_authorization_sha, "Repair1 authorization binding drift")
    pairs = payload.get("pairs") or []
    require(len(pairs) == 14 and int(payload.get("inherited_pair_count")) == 14, "inherited pair cardinality drift")
    heldout = set(map(str, heldout_task_ids))
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for pair in pairs:
        unit_id = str(pair["unit_id"])
        require(unit_id not in seen, f"duplicate inherited pair: {unit_id}")
        seen.add(unit_id)
        require(pair.get("source") == "inherited_repair1", f"inheritance source drift: {unit_id}")
        require(pair.get("prefix_compatibility") == "PASS_ATTEMPT0_SUCCESS_PATH_IDENTICAL", f"prefix incompatibility: {unit_id}")
        summary_path = Path(pair["pair_summary_path"])
        require(summary_path.is_file() and sha_file(summary_path) == pair["pair_summary_sha256"], f"pair summary drift: {unit_id}")
        summary = load_json(summary_path)
        require(summary.get("status") == "COMPLETED" and summary.get("unit_id") == unit_id, f"pair summary invalid: {unit_id}")
        evidence_path = Path(pair["evidence_windows_path"])
        require(evidence_path.is_file() and sha_file(evidence_path) == pair["evidence_windows_sha256"], f"evidence window drift: {unit_id}")
        arms = pair.get("arms") or {}
        require(set(arms) == set(ARMS), f"paired arms missing: {unit_id}")
        out_arms: dict[str, Any] = {}
        for arm in ARMS:
            state = arms[arm]
            require(int(state.get("provider_calls")) == 10 and int(state.get("parse_errors")) == 0, f"non-prefix provider path: {unit_id}/{arm}")
            require(state.get("patch_apply_correction_required") is False, f"correction used in Repair1 prefix: {unit_id}/{arm}")
            checkpoint = Path(state["update_checkpoint_path"])
            receipt = Path(state["update_receipt_path"])
            skill = Path(state["skill_post_path"])
            require(checkpoint.is_file() and sha_file(checkpoint) == state["update_checkpoint_sha256"], f"update checkpoint drift: {unit_id}/{arm}")
            require(receipt.is_file() and sha_file(receipt) == state["update_receipt_sha256"], f"update receipt drift: {unit_id}/{arm}")
            require(skill.is_file() and sha_file(skill) == state["skill_post_sha256"], f"skill drift: {unit_id}/{arm}")
            receipt_payload = load_json(receipt)
            require(receipt_payload.get("contract_sha256") == repair1_contract_sha, f"receipt contract drift: {unit_id}/{arm}")
            require(receipt_payload.get("authorization_sha256") == repair1_authorization_sha, f"receipt auth drift: {unit_id}/{arm}")
            calls = state.get("provider_call_receipts") or []
            require(len(calls) == 10, f"nominal call count drift: {unit_id}/{arm}")
            require(all(c.get("provider_status") == "completed" and int(c.get("attempt")) == 0 and not c.get("parse_error") for c in calls), f"provider prefix drift: {unit_id}/{arm}")
            eval_path = Path(state["eval_manifest_path"])
            _validate_eval_manifest(eval_path, state["eval_manifest_sha256"], heldout)
            out_arms[arm] = {
                "state_root": state["state_root"],
                "skill_sha256": state["skill_post_sha256"],
                "update_receipt_sha256": state["update_receipt_sha256"],
                "eval_manifest_path": state["eval_manifest_path"],
                "eval_manifest_sha256": state["eval_manifest_sha256"],
                "updater_calls": 10,
                "attempt0_success": True,
                "correction_required": False,
            }
        rows.append({
            "unit_id": unit_id,
            "stream_id": str(pair["stream_id"]),
            "replicate_id": int(pair["replicate_id"]),
            "source": "repair1_inherited",
            "pair_summary_path": pair["pair_summary_path"],
            "pair_summary_sha256": pair["pair_summary_sha256"],
            "arms": out_arms,
        })
    return sorted(rows, key=lambda row: (row["stream_id"], row["replicate_id"]))


def validate_quarantine(path: Path, expected_sha: str) -> dict[str, Any]:
    require(path.is_file() and sha_file(path) == expected_sha, "quarantine SHA drift")
    payload = load_json(path)
    require(payload.get("status") == "TECHNICAL_QUARANTINE_UPDATER_PATCH_APPLY_FAILURE", "quarantine status drift")
    require(payload.get("provider_response_ambiguity") is False, "provider response incorrectly ambiguous")
    require(payload.get("scientific_pair_outcome_exists") is False, "quarantined scientific outcome exists")
    require(payload.get("single_arm_resume_authorized") is False, "single-arm resume must remain forbidden")
    require(payload.get("operator_semantic_patch_authorized") is False, "operator semantic patch must remain forbidden")
    return payload


def validate_valid_rows(
    rows: list[dict[str, Any]],
    *,
    streams: Iterable[str],
    quarantine: dict[str, Any],
    require_complete: bool,
) -> None:
    expected_streams = list(map(str, streams))
    seen: set[str] = set()
    counts: Counter[str] = Counter()
    quarantine_unit = f"{quarantine['stream_id']}/rep{int(quarantine['replicate_id'])}"
    quarantine_root = str(quarantine["state_root"])
    for row in rows:
        unit_id = str(row["unit_id"])
        require(unit_id not in seen, f"duplicate valid pair: {unit_id}")
        seen.add(unit_id)
        stream = str(row["stream_id"])
        replicate = int(row["replicate_id"])
        require(stream in expected_streams and replicate in REPLICATES, f"out-of-design pair: {unit_id}")
        require(unit_id == f"{stream}/rep{replicate}", f"unit id mismatch: {unit_id}")
        require(row.get("source") in {"repair1_inherited", "repair2_fresh"}, f"invalid source: {unit_id}")
        arms = row.get("arms") or {}
        require(set(arms) == set(ARMS), f"incomplete pair: {unit_id}")
        if row.get("source") == "repair1_inherited":
            require(unit_id != quarantine_unit, "quarantined pair cannot be inherited")
        for arm in ARMS:
            require(str(arms[arm].get("state_root")) != quarantine_root, "quarantined state cannot enter valid manifest")
            require(all(arms[arm].get(key) for key in ("skill_sha256", "update_receipt_sha256", "eval_manifest_path", "eval_manifest_sha256")), f"incomplete arm binding: {unit_id}/{arm}")
        counts[stream] += 1
    if require_complete:
        require(len(rows) == 48, "valid manifest must contain exactly 48 pairs")
        require(set(counts) == set(expected_streams), "valid manifest stream set drift")
        require(all(counts[stream] == 4 for stream in expected_streams), "valid manifest must contain exactly four pairs per stream")


===== BOUND ARTIFACT: tests | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/test_e2_r17_deepseek_v2_repair2.py =====
from __future__ import annotations

import ast
import asyncio
import inspect
import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.e2_r17_mindmemos_ark_adapter import MindMemOSArkPlanChatAdapter
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from research_pipeline.e2_r17_repair2_manifest import (
    _validate_eval_manifest,
    validate_compatibility_manifest,
    validate_quarantine,
    validate_valid_rows,
)

ROOT = Path(__file__).resolve().parents[1]
COMPAT = ROOT / "generated/e2-r17-deepseek-v2-repair1-compatibility-manifest-20260831.json"
QUARANTINE = ROOT / "generated/e2-r17-deepseek-v2-repair1-technical-quarantine-20260831.json"
COMPAT_SHA = "61e243027e6d42f7923e249f6c88267e6db07ed4bccb32d5a50c8d13bf1695bb"
QUARANTINE_SHA = "1908a3dfc472f835c204f7f9d5a66a9ee4b37093adb09a8d0c0f297b4b1abd7a"
REPAIR1_CONTRACT_SHA = "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80"
REPAIR1_AUTH_SHA = "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5"


class Repair2Tests(unittest.TestCase):
    def settings(self) -> ArkSettings:
        return ArkSettings(
            api_key="test-key",
            base_url="https://ark.cn-beijing.volces.com/api/plan/v3",
            default_model="deepseek-v4-pro",
            timeout_seconds=30,
            max_retries=0,
        )

    def adapter(self, root: Path, outputs: list[str]) -> tuple[MindMemOSArkPlanChatAdapter, list[str]]:
        ledger = ProviderBudgetLedger(
            path=root / "budget.sqlite3",
            contract_sha256="a" * 64,
            authorization_sha256="b" * 64,
            total_limit=191,
            per_unit_limit=11,
            allow_create=True,
        )
        adapter = MindMemOSArkPlanChatAdapter(
            settings=self.settings(),
            requested_model="deepseek-v4-pro",
            required_resolved_model="deepseek-v4-pro-ga-260813",
            max_parse_attempts=2,
            record_dir=root / "calls",
            provider_budget_ledger=ledger,
            provider_budget_unit_id="s/rep0/win_c/update",
        )
        prompts: list[str] = []
        iterator = iter(outputs)

        def respond(prompt: str, *args, **kwargs):
            prompts.append(prompt)
            return {
                "resolved_model": "deepseek-v4-pro-ga-260813",
                "text": next(iterator),
                "usage": {"input_tokens": 2, "output_tokens": 1, "total_tokens": 3},
                "response_id": f"id-{len(prompts)}",
                "status": "completed",
            }

        adapter.client.respond = respond
        return adapter, prompts

    def nine_nominal_calls(self, adapter: MindMemOSArkPlanChatAdapter) -> None:
        for index in range(9):
            task = "skill_trajectory_summary" if index < 8 else "skill_patch_propose"
            asyncio.run(adapter.chat(task=task, messages=[{"role": "user", "content": "x"}]))

    def test_a_first_attempt_success_exactly_ten_calls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adapter, _ = self.adapter(Path(tmp), ["ok"] * 9 + ['{"ok":true}'])
            self.nine_nominal_calls(adapter)
            result = asyncio.run(adapter.chat(
                task="skill_patch_apply",
                messages=[{"role": "user", "content": "apply"}],
                format_parser=json.loads,
                feedback_on_parse_error=True,
            ))
            self.assertEqual(result.parsed, {"ok": True})
            receipts = adapter.public_receipts()
            self.assertEqual(len(receipts), 10)
            self.assertFalse(any(row["parse_error"] for row in receipts))
            self.assertEqual(receipts[-1]["attempt"], 0)

    def test_b_one_explicit_correction_exactly_eleven_calls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adapter, prompts = self.adapter(Path(tmp), ["ok"] * 9 + ["bad", '{"ok":true}'])
            self.nine_nominal_calls(adapter)
            exact_error = "line 12 does not match old_string_prefix"

            def parser(text: str):
                if text == "bad":
                    raise ValueError(exact_error)
                return json.loads(text)

            result = asyncio.run(adapter.chat(
                task="skill_patch_apply",
                messages=[{"role": "user", "content": "apply"}],
                format_parser=parser,
                feedback_on_parse_error=True,
            ))
            self.assertEqual(result.parsed, {"ok": True})
            receipts = adapter.public_receipts()
            self.assertEqual(len(receipts), 11)
            self.assertEqual([receipts[-2]["attempt"], receipts[-1]["attempt"]], [0, 1])
            self.assertIn(exact_error, prompts[-1])
            self.assertTrue(receipts[-2]["parse_error"])
            self.assertFalse(receipts[-1]["parse_error"])
            self.assertTrue(all(not row["hidden_provider_retry_used"] for row in receipts))

    def test_c_second_failure_stops_without_third_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adapter, prompts = self.adapter(Path(tmp), ["ok"] * 9 + ["bad0", "bad1"])
            self.nine_nominal_calls(adapter)

            def parser(text: str):
                raise ValueError(f"cannot apply {text}")

            with self.assertRaisesRegex(ValueError, "cannot apply bad1"):
                asyncio.run(adapter.chat(
                    task="skill_patch_apply",
                    messages=[{"role": "user", "content": "apply"}],
                    format_parser=parser,
                    feedback_on_parse_error=True,
                ))
            self.assertEqual(len(adapter.public_receipts()), 11)
            self.assertEqual(len(prompts), 11)
            self.assertEqual([row["attempt"] for row in adapter.public_receipts()[-2:]], [0, 1])

    def test_d_real_repair1_prefix_manifest_revalidates_without_provider_call(self) -> None:
        contract = json.loads((ROOT / "generated/e2-r17-deepseek-v2-replicated-paired-repair1-contract-20260830.json").read_text())
        rows = validate_compatibility_manifest(
            path=COMPAT,
            expected_sha=COMPAT_SHA,
            repair1_contract_sha=REPAIR1_CONTRACT_SHA,
            repair1_authorization_sha=REPAIR1_AUTH_SHA,
            heldout_task_ids=contract["heldout"]["task_ids"],
        )
        self.assertEqual(len(rows), 14)
        self.assertEqual(sum(len(row["arms"]) for row in rows), 28)
        self.assertTrue(all(row["source"] == "repair1_inherited" for row in rows))

    def test_e_partial_repair1_state_is_quarantined_not_inherited(self) -> None:
        quarantine = validate_quarantine(QUARANTINE, QUARANTINE_SHA)
        self.assertFalse(quarantine["update_completed_exists"])
        self.assertFalse(quarantine["skill_post_exists"])
        self.assertFalse(quarantine["paired_win_c_started"])
        self.assertEqual(quarantine["disposition"], "PRESERVE; EXCLUDE FROM VALID MANIFEST; REPAIR2 FRESH-RUNS BOTH ARMS")

    def row(self, stream: str, replicate: int, source: str = "repair2_fresh") -> dict:
        arms = {}
        for arm in ("win_c", "mrw"):
            arms[arm] = {
                "state_root": f"/fresh/{stream}/replicate_{replicate}/{arm}",
                "skill_sha256": "a" * 64,
                "update_receipt_sha256": "b" * 64,
                "eval_manifest_path": f"/fresh/{stream}/replicate_{replicate}/{arm}/eval.jsonl",
                "eval_manifest_sha256": "c" * 64,
            }
        return {
            "unit_id": f"{stream}/rep{replicate}",
            "stream_id": stream,
            "replicate_id": replicate,
            "source": source,
            "arms": arms,
        }

    def quarantine(self) -> dict:
        return {
            "stream_id": "s0",
            "replicate_id": 2,
            "state_root": "/repair1/s0/replicate_2/mrw",
        }

    def test_f_quarantine_state_cannot_enter_valid_manifest(self) -> None:
        row = self.row("s0", 2, "repair1_inherited")
        row["arms"]["mrw"]["state_root"] = self.quarantine()["state_root"]
        with self.assertRaisesRegex(RuntimeError, "quarantined"):
            validate_valid_rows([row], streams=["s0"], quarantine=self.quarantine(), require_complete=False)

    def test_g_incomplete_pair_is_not_scientific_valid(self) -> None:
        row = self.row("s0", 0)
        del row["arms"]["mrw"]
        with self.assertRaisesRegex(RuntimeError, "incomplete pair"):
            validate_valid_rows([row], streams=["s0"], quarantine=self.quarantine(), require_complete=False)

    def test_h_exactly_four_pairs_per_stream_and_48_total(self) -> None:
        streams = [f"s{i}" for i in range(12)]
        rows = [self.row(stream, replicate) for stream in streams for replicate in range(4)]
        validate_valid_rows(rows, streams=streams, quarantine=self.quarantine(), require_complete=True)
        with self.assertRaisesRegex(RuntimeError, "exactly 48|exactly four"):
            validate_valid_rows(rows[:-1], streams=streams, quarantine=self.quarantine(), require_complete=True)

    def test_i_inheritance_validator_never_reads_score_field(self) -> None:
        tree = ast.parse(inspect.getsource(_validate_eval_manifest))
        score_subscripts = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Subscript)
            and isinstance(node.slice, ast.Constant)
            and node.slice.value in {"score", "effect", "J", "D", "success_count"}
        ]
        self.assertEqual(score_subscripts, [])


if __name__ == "__main__":
    unittest.main()


===== BOUND ARTIFACT: test_adjudication | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-deepseek-v2-repair2-test-adjudication-20260831.json =====
{
  "artifact_type": "e2-r17-deepseek-v2-repair2-test-adjudication",
  "created_at_utc": "2026-08-31T04:11:25+00:00",
  "logical_test_count": 8,
  "provider_calls": 0,
  "real_prefix_revalidation_test_count": 1,
  "schema_version": "1.0",
  "scientific_scores_read": false,
  "status": "PASS_REPAIR2_TESTS_9_OF_9",
  "test_d_log_path": "/data/wyt/e2-r17-search-projection/repair2-test-d-20260831.log",
  "test_d_log_sha256": "e56f11172ae2ebdb97508ea3bc9f8e0dd5dfa29e6128eab603b2c56e9429a69d",
  "test_source_path": "research_pipeline/test_e2_r17_deepseek_v2_repair2.py",
  "test_source_sha256": "1735ac87979afc83092a0ce0e5851761197a530c53d91fd6c2392c73332cd1b3",
  "tests": {
    "A": "PASS_FIRST_ATTEMPT_10_CALLS",
    "B": "PASS_ONE_EXPLICIT_CORRECTION_11_CALLS_EXACT_ERROR_FEEDBACK",
    "C": "PASS_SECOND_FAILURE_STOPS_NO_THIRD_ATTEMPT",
    "D": "PASS_REAL_14_PAIR_504_HELDOUT_SHA_REVALIDATION_ZERO_PROVIDER",
    "E": "PASS_PARTIAL_STATE_QUARANTINED",
    "F": "PASS_QUARANTINE_EXCLUDED",
    "G": "PASS_INCOMPLETE_PAIR_INVALID",
    "H": "PASS_EXACT_48_AND_FOUR_PER_STREAM",
    "I": "PASS_NO_SCORE_BASED_INHERITANCE"
  },
  "total_fail": 0,
  "total_pass": 9
}


===== BOUND ARTIFACT: model_identity | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-deepseek-v2-repair2-model-identity-adjudication-20260831.json =====
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
      "path": "generated/e2-r17-deepseek-v2-repair2-deepseek-identity-qualification-20260831.json",
      "sha256": "6f7305554f710ce56d07e86cbc786ab5d4618327f5b6c0161c7259067cae59ac",
      "status": "PASS"
    },
    {
      "path": "generated/e2-r17-deepseek-v2-repair2-kimi-reviewer-identity-qualification-20260831.json",
      "sha256": "438fd94e5b9eba442204d7e9ba5bf2092e4512c2fef50875d58238959da4cf5a",
      "status": "PASS"
    }
  ],
  "created_at_utc": "2026-08-31T04:07:18+00:00",
  "private_credentials_included": false,
  "raw_response_ids_included": false,
  "requested_and_resolved": {
    "deepseek-v4-pro": {
      "requested": "deepseek-v4-pro",
      "resolved": "deepseek-v4-pro-ga-260813",
      "source_artifact": "generated/e2-r17-deepseek-v2-repair2-deepseek-identity-qualification-20260831.json",
      "source_artifact_sha256": "6f7305554f710ce56d07e86cbc786ab5d4618327f5b6c0161c7259067cae59ac",
      "thinking_requested": "disabled"
    },
    "kimi-k3": {
      "requested": "kimi-k3",
      "resolved": "kimi-k3",
      "source_artifact": "generated/e2-r17-deepseek-v2-repair2-kimi-reviewer-identity-qualification-20260831.json",
      "source_artifact_sha256": "438fd94e5b9eba442204d7e9ba5bf2092e4512c2fef50875d58238959da4cf5a",
      "thinking_requested": "disabled"
    }
  },
  "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
  "schema_version": "1.0",
  "status": "PASS_CURRENT_REVIEW_TRANCHE"
}


BOUND DOSSIER END
