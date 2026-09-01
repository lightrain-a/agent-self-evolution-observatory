You are an independent adversarial experiment-design reviewer for E2-R17, a prospective ICLR paper. You are blind to the other reviewer. This consultation has zero experiment, GPU, paper-promotion, front-end, or submission authority.

Requested reviewer endpoint: deepseek-v4-pro
Exact Experiment Plan V1 SHA-256: 928ae3e9eac9259dba47d08cca3d91309f2bedb4692d597b89806f0313625549

Evaluate the bound plan, not an imagined broader project. Recommend STOP when the central chain is incoherent. Do not reward experiment volume. Do not invent citations or claim outside web access; the bound primary-source audit is the literature record for this review.

Central object: a best-of-K acting selector and an updater-visible learning projection operate on the same generated trajectory pool. E0 has one rescue task in one family, so E1 is HOLD pending the predeclared 54-task support gate. The plan proposes E1 exact-same-pool causality, public benchmark transport, prospective prediction, multi-round closure, and topology controls.

Audit these exact issues:
1. Is V1 genuinely sequential, or can later public results leak back to rescue E1?
2. Does model selection follow baseline/common-model/capability-spread logic without choosing models by R17 gain?
3. Are actor and updater roles separated and is freezing DeepSeek as updater justified or confounded?
4. Which baselines are exact official implementations versus paper-spec reconstructions, and are labels fair?
5. Is the proposed Verified-400 16/160/24/200 split defensible and non-shopping? Does the one-step 20-stream design estimate the claimed public effectiveness?
6. Is SkillEvolBench scientifically compatible with the same-pool object, especially because it uses a native updater?
7. Are scientific units, sample sizes, paired tests, hierarchical bootstrap, repeated partitions/seeds, and cross-model averages valid without pseudoreplication?
8. Are Pilot thresholds outcome-blind and sufficient? Flag any threshold that still permits model cherry-picking.
9. Is checkpoint/resume granular enough to prevent duplicated provider calls and lost results?
10. Are call/token/GPU/API budgets realistic enough to decide scope? Identify any hidden multiplicative cost.
11. Are E0, E1, public, prediction, multi-round, and topology STOP conditions decisive rather than movable?
12. Name only verdict-relevant V2 changes. Do not demand a benchmark/model zoo for breadth.

Return exactly one JSON object and no markdown using this schema:
{
  "plan_sha256_acknowledged": "",
  "verdict": "PASS_TO_V2|REVISE_BEFORE_ANY_PILOT|STOP_PROGRAM",
  "scientific_chain_coherent": false,
  "pilot_is_outcome_blind": false,
  "e0_hold_respected": false,
  "model_selection_assessment": "",
  "baseline_fidelity_assessment": "",
  "benchmark_and_split_assessment": "",
  "sample_size_and_statistics_assessment": "",
  "checkpoint_and_resume_assessment": "",
  "budget_and_matrix_assessment": "",
  "decisive_experiment_and_stop_assessment": "",
  "fatal_or_blocking_issues": [
    {
      "priority": "P0|P1",
      "issue": "",
      "why_blocking": "",
      "exact_v2_repair": ""
    }
  ],
  "required_v2_changes": [
    {
      "priority": "P0|P1|P2",
      "target": "",
      "change": "",
      "verdict_relevance": ""
    }
  ],
  "nonblocking_improvements": [
    ""
  ],
  "pilot_recommendation_after_v2": "ALLOW_OUTCOME_BLIND_RUNTIME_PILOTS|HOLD|STOP",
  "e0_full_extension_recommendation": "REVIEW_SEPARATE_CONTRACT|HOLD|STOP",
  "e1_recommendation": "HOLD_UNTIL_E0_FULL_AND_V3|STOP",
  "paper_claim_authority": false,
  "single_sentence_verdict": ""
}

Set `plan_sha256_acknowledged` to the exact SHA above. Keep `paper_claim_authority` false. A PASS_TO_V2 verdict means the plan may be revised and then receive separate Pilot contracts; it does not authorize any scientific execution.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START

===== BOUND ARTIFACT: generated/e2-r17-experiment-plan-v1-20260828.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-experiment-plan-v1",
  "created_at_utc": "2026-08-28T07:45:00+00:00",
  "status": "V1_REQUIRES_DUAL_REVIEW_AND_RUNTIME_PILOTS",
  "working_title": "When Better Search Teaches Less: Serving-Induced Observation Kernels in Self-Evolving Agents",
  "scientific_question": "When a self-evolving agent generates a best-of-K search pool, does coupling the acting selector to winner-only learning censor reusable failed evidence and make the acting-optimal trajectory learning-suboptimal?",
  "scientific_object": "SERVING_INDUCED_OBSERVATION_KERNEL_FOR_PERSISTENT_SKILL_LEARNING",
  "story": {
    "acting_projection": "Serve the highest-verifier trajectory from the generated pool.",
    "learning_projection": "Choose which content-addressed evidence from that same pool reaches the persistent updater.",
    "central_claim": "On precommitted rescue events, winner-only serving removes exactly the failed witness that rollout-0 would have exposed; if that witness has positive reusable diagnostic value, changing only the learning projection changes future frozen skill.",
    "minimal_method": "Act from the winner; on a frozen rescue event learn from the precommitted rejected witness, otherwise learn from the winner.",
    "nonclaims": [
      "more compute inherently harms learning",
      "failures are newly discovered to be useful",
      "success/failure contrast or first divergence is novel",
      "the iid reference curve is an empirical law",
      "Rejected-Witness is necessarily more complex than existing contrastive skill methods"
    ]
  },
  "current_evidence": {
    "e0_summary_sha256": "533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366",
    "independent_analysis": "generated/e2-r17-e0-pilot-analysis-20260828.json",
    "canonical_parallel_analysis": "generated/e2-r17-e0-analysis-20260828.json",
    "decision": "HOLD_FOR_PREDECLARED_E0_FULL",
    "success_at_k": {"1": 0.9166666666666666, "2": 0.9166666666666666, "4": 1.0, "8": 1.0},
    "rescue_tasks_k8": 1,
    "rescue_families_k8": 1,
    "identity": "A_K-A_1 = V_pre(K)-V_winner(K) = Gamma_K holds exactly on the frozen pools",
    "e1_authorized": false
  },
  "hypotheses": {
    "H0_support": "The frozen 54-task calibration lane contains at least six precommitted rescue tasks spanning at least three mutually exclusive failure families.",
    "H1_causal": "Under identical initial skill, exact K=8 pool, acting winner, updater, budget, and held-out probes, Rejected-Witness yields higher future frozen K=1 success than Winner-only.",
    "H1_controls": "The primary gain is not reproduced by duplicated-winner token matching or deterministic random-nonwinner diversity; SkillCAT-style contrast determines whether the minimal witness is sufficient or a richer contrast is needed.",
    "H2_public": "The simplest mechanism-qualified projection improves average frozen K=1 success over Winner-only on public benchmarks across qualified executor backbones.",
    "H3_prediction": "Pre-outcome family-level censoring mass times cloned diagnostic value predicts held-out effect sign, family rank, K ordering, and preregistered null cells.",
    "H4_longitudinal": "High-K online acting can rise while Winner-only frozen skill lags; a history-preserving learning projection reduces that divergence over multiple rounds.",
    "H5_topology": "At matched actor-call budget, learning projection explains the persistent-skill difference more directly than parallel versus sequential search topology."
  },
  "global_design_rules": {
    "sequence": [
      "Pilot",
      "Protocol Audit",
      "Scientific Identifiability Qualification",
      "Freeze Full Contract",
      "Full Run",
      "Integrity Audit",
      "Statistical Analysis",
      "Belief Update"
    ],
    "pilot_is_not_effect_selection": true,
    "full_contract_is_immutable_after_outcomes": true,
    "models_selected_only_by_protocol_validity_headroom_stability_and_cost": true,
    "no_task_replacement_for_model_outcome": true,
    "no_benchmark_shopping": true,
    "same_pool_reused_across_projection_arms_when_scientifically_possible": true,
    "actor_and_updater_roles_separate": true,
    "core_updater_frozen_before_executor_matrix": true,
    "resolved_model_drift_stops_tranche": true,
    "provider_retry_limit": 0,
    "thinking": "disabled",
    "temperature": 0,
    "credentials_in_public_artifacts": false
  },
  "model_plan": {
    "source": "generated/e2-r17-baseline-model-choice-audit-20260828.json",
    "core_candidates_before_pilot": [
      {"role": "weak_open", "model": "Qwen3.5-4B", "status": "PILOT_REQUIRED"},
      {"role": "common_open", "model": "exact available Qwen3.5-35B-A3B or Qwen3.6-35B-A3B", "status": "AVAILABILITY_AND_PILOT_REQUIRED"},
      {"role": "strong_api", "model": "deepseek-v4-pro -> deepseek-v4-pro-ga-260813", "status": "E0_QUALIFIED_REQUALIFY_EACH_TRANCHE"},
      {"role": "second_api_family", "model": "kimi-k3", "status": "PILOT_REQUIRED"}
    ],
    "executor_target": ">=4 qualified models and >=2 model families for the public core matrix",
    "core_updater_v1": "deepseek-v4-pro -> deepseek-v4-pro-ga-260813",
    "updater_robustness": "One second qualified updater only after E1 GO; no full actor x updater cross-product.",
    "model_pilot": {
      "development_tasks": 12,
      "primary_run": "K=1 on all 12 fixed development tasks",
      "search_smoke": "K=4 nested prefixes on four predeclared tasks",
      "promotion_checks": {
        "task_loading_rate": 1.0,
        "resolved_identity_stability": 1.0,
        "tool_call_parse_rate_min": 0.95,
        "artifact_write_rate_min": 0.90,
        "verifier_completion_rate_min": 0.95,
        "technical_failure_rate_max": 0.05,
        "k1_headroom_rule": "Neither all-zero nor all-one on the 12 fixed tasks; used only to reject structurally uninformative capability regimes, never to select larger R17 gain.",
        "resume_replay_check": "Interrupt one predeclared technical smoke unit and verify missing-unit-only resume without repeating completed provider calls."
      }
    }
  },
  "baseline_plan": {
    "fidelity_tiers": {
      "official_core": ["MindMemOS", "RethinkSkill"],
      "official_extended": ["SkillOpt", "SkillEvolBench"],
      "paper_spec_reconstruction": ["SkillCAT-style contrast", "Branch2Skill-style branch evidence"],
      "context_not_direct_baseline": ["TSR"]
    },
    "e1_arms": [
      "Winner-only",
      "Precommitted rollout-0",
      "Rejected-Witness",
      "Duplicated Winner",
      "Random Nonwinner",
      "SkillCAT-style contrast"
    ],
    "public_core_methods": [
      "Winner-only",
      "Rejected-Witness",
      "Full Pool",
      "Final simplest R17 method; replace with Precommitted or SkillCAT-style if identical to Rejected-Witness"
    ],
    "public_extended_methods": [
      "Initial Skill",
      "No Skill",
      "Precommitted rollout-0",
      "Duplicated Winner",
      "Random Nonwinner",
      "RethinkSkill Normal/Fail-only/Success-only",
      "SkillOpt official implementation",
      "SkillCAT-style reconstruction",
      "Branch2Skill-style reconstruction"
    ],
    "baseline_pilot": {
      "development_tasks": 8,
      "qualified_executor_count": 1,
      "gate": "Implementation fidelity, input-information parity, actor/update budget accounting, valid artifacts, common verifier, checkpoint/resume, and source-label accuracy. No method-effect threshold is allowed."
    }
  },
  "stages": {
    "S0_E0_full_support": {
      "purpose": "Complete the already frozen support qualification before any updater intervention.",
      "benchmark": "Controlled Spreadsheet Suite V2",
      "tasks": 54,
      "completed_tasks": 12,
      "extension_tasks": 42,
      "search_k": 8,
      "nested_prefixes": [1, 2, 4, 8],
      "updater": null,
      "verifier": "Frozen deterministic binary workbook verifier",
      "scientific_unit": "Task-level exact nested search pool",
      "primary_metrics": ["Success@K", "A_K-A_1", "mixed-pool rate", "rescue-event rate", "V_pre-V_winner", "failure-family coverage"],
      "full_gate": {"rescue_tasks_min": 6, "rescue_families_min": 3},
      "go": "All integrity checks pass and the 54-task combined result meets both support thresholds.",
      "stop": "Protocol failure or insufficient frozen rescue support. Do not open public benchmarks or alter taxonomy to rescue the mechanism on this substrate.",
      "execution": "Run only missing units from the 42-task extension; never rerun the completed 12 tasks."
    },
    "E1_causal_identification": {
      "entry": "S0 GO plus a new content-addressed full contract and authorization.",
      "benchmark": "Controlled Spreadsheet Suite V2",
      "pool_tasks": 96,
      "streams": 12,
      "tasks_per_stream": 8,
      "search_k": 8,
      "arms": 6,
      "heldout_probes_per_state": 18,
      "evaluation_k": 1,
      "actor": "Frozen DeepSeek V4-Pro executor in the primary identification run",
      "updater": "Pinned MindMemOS SkillEvolver, DeepSeek V4-Pro, exact config and initial skill SHA",
      "verifier": "Frozen deterministic binary workbook verifier",
      "scientific_unit": "One independently evolved eight-task cloned stream-state",
      "primary_estimand": "Delta_s = J_s(Rejected-Witness)-J_s(Winner-only)",
      "statistics": {
        "summary": "Mean paired stream-level Delta_s",
        "test": "Exact one-sided 2^12 sign-flip test",
        "ci": "95% percentile bootstrap over 12 streams, 10000 draws",
        "secondary": ["RW-Duplicate", "RW-RandomNonwinner", "SkillCAT-style-Winner", "Precommitted-Winner", "Delta versus rescue count"],
        "no_pseudoreplication": true
      },
      "support_gate": {"rescue_task_packets_min": 8, "exposed_streams_min": 6, "drop_streams": false},
      "go": "Provenance passes; mean RW-Winner > 0; one-sided p <= 0.05; 95% CI lower > 0; duplicated winner does not reproduce the gain.",
      "downgrade": [
        "Random Nonwinner matches RW => generic diversity explanation",
        "SkillCAT-style dominates => retain prior contrast method and narrow R17 to mechanism",
        "RW is sufficient => delete any more complex CADP label"
      ],
      "stop": "No reproducible directional difference under exact same-pool cloned states, duplicated-winner equivalence, post-outcome witness selection, or any cloned invariant failure."
    },
    "E2_public_effectiveness": {
      "entry": "E1 GO only.",
      "primary_benchmark": {
        "name": "SpreadsheetBench Verified-400",
        "hashes": {
          "archive": "10ef893dd29cb13ab97143ea787e68cdc9574a13873ab9a54e50b31dc03fc949",
          "dataset_json": "bcecaa89a005bd4e3bbe98da150a86e8062c27f262e575d5e47bd9861b3525e7"
        },
        "preoutcome_split_v1": {
          "runtime_development": 16,
          "evolution": 160,
          "validation": 24,
          "test": 200,
          "rule": "Deterministic content-hash split, stratified only by released metadata/instruction type; exact IDs frozen before any candidate-model outcome."
        },
        "one_step_public_design": {
          "evolution_streams": 20,
          "tasks_per_stream": 8,
          "test_tasks_per_stream": 10,
          "test_coverage": 200,
          "validation_tasks_per_candidate_state": 8,
          "search_k": 8,
          "pool_sharing": "All projection arms for a model/stream use the exact same initial skill, pool, and acting winner.",
          "rationale": "Preserves the central one-step causal object on a public benchmark; repeated path-dependent evolution is reserved for E4."
        }
      },
      "secondary_benchmark": {
        "name": "SkillEvolBench",
        "design": "Use the official 30 environment-by-skill-family cells; T1-T3 are acquisition and T4-T6 frozen K=1 evaluation. Generate nested K pools for acquisition, keep pools common across projection arms, and use the native updater only after adapter Pilot.",
        "scientific_unit": "Environment-by-latent-skill cell (n=30)",
        "adapter_gate": "Official validators, harness identity, tool artifacts, acquisition/evaluation separation, and missing-unit resume must pass before any full run."
      },
      "models": ">=4 Pilot-qualified executors across >=2 families",
      "methods": "Four core methods on all models; extended baseline matrix on one weak/common and one strong representative executor.",
      "primary_metric": "Average frozen K=1 success rate",
      "statistics": {
        "primary_unit_verified": "20 paired stream-state blocks; compute each block's mean over its ten test tasks before inference",
        "ci": "Paired hierarchical bootstrap over stream blocks, stratified by model; report model-specific 95% CIs and paired Delta versus Winner-only",
        "cross_model": "Report descriptive mean, range, and model-stratified bootstrap; do not treat four models as a large-n significance test",
        "replication": "One primary frozen partition for all four models; two additional provider/order replications on two representative models, clustered rather than counted as independent tasks."
      },
      "go": "The qualified simplest method has positive paired gain over Winner-only on the primary public benchmark, no material safe/valid-task regression, and directionally consistent support on the secondary benchmark or a predeclared bounded transport statement.",
      "hold": "Primary positive but model/benchmark heterogeneity prevents a general claim; report the bounded regime without adding a rescue benchmark.",
      "stop": "Primary public transport is null/negative under the frozen design; do not open SpreadsheetBench 2 as rescue."
    },
    "E3_prospective_prediction": {
      "entry": "E1 GO; calibration and confirmatory IDs frozen before confirmatory outcomes are opened.",
      "calibration": "Estimate c_z(K), delta_z, and Lambda_K only from development/calibration cloned units.",
      "frozen_predictions": ["effect sign", "failure-family rank", "K ordering", "null cells"],
      "confirmatory_design_v1": "Use a disjoint controlled-suite reserve with six mutually exclusive families and nested K={1,2,4,8}; exact stream/cell counts finalized in V3 after outcome-blind support simulation, never after effect results.",
      "metrics": ["sign accuracy", "Spearman rank correlation", "calibration slope/intercept", "absolute prediction error", "null-cell false-positive rate"],
      "go": "Predeclared sign and rank predictions pass their frozen thresholds and calibration is not contradicted by held-out cells.",
      "stop": "Prediction only fits observed/calibration data or fails sign/rank/null-cell tests; delete predictive-theory claim regardless of public method gain."
    },
    "E4_multi_round": {
      "entry": "E1 and E2 GO; separate full contract.",
      "arms": ["L/L", "H/Winner", "H/Precommitted", "H/Rejected", "H/Final simplest method"],
      "pilot": "Two rounds on two fixed development streams; runtime and state/checkpoint qualification only.",
      "full_v1": {"independent_streams": 8, "rounds": 5, "tasks_per_round": 8, "common_frozen_probe_tasks_per_round": 24},
      "metrics": ["online R_t", "frozen J_t", "R_t-J_t divergence", "accepted/rejected patch rate", "skill interference", "cumulative cost"],
      "statistics": "Paired stream-level trajectories with simultaneous confidence bands; report first-round causal effect separately from later path-dependent divergence.",
      "go": "Winner-only shows a reproducible online/frozen divergence and the history-preserving projection reduces it without current-acting degradation.",
      "stop": "No longitudinal divergence or repair after the one-step mechanism qualified; do not rewrite the one-step result as a longitudinal claim."
    },
    "E5_topology_external_validation": {
      "entry": "E1-E4 support the central chain.",
      "topology_factorial": {
        "factor_A": ["parallel best-of-8", "sequential refinement with matched eight actor calls"],
        "factor_B": ["winner/final-only learning", "history-preserving final method"],
        "primary_unit": "Independent cloned stream-state",
        "pilot": "Two streams, one update, outcome-blind runtime qualification",
        "full_v1": "Eight streams per cell, common K=1 probes"
      },
      "optional_benchmark": "SpreadsheetBench 2 only after Verified-400 GO and a pre-outcome subset/evaluator contract; visualization remains secondary because it changes the evaluator substrate.",
      "purpose": "Separate learning projection from compute amount/topology; no universal claim that parallel search is harmful."
    }
  },
  "checkpoint_contract": {
    "principle": "unit-complete -> immediately persist -> atomic checkpoint",
    "raw_immutable": true,
    "summary_rebuildable": true,
    "exclusive_lock": true,
    "resume_missing_units_only": true,
    "layers": {
      "raw": ["rollout trajectory", "provider receipt hashes", "output artifact", "verifier", "pool", "projection packet", "updater input/output", "skill pre/post", "frozen evaluation"],
      "checkpoints": ["completed_units.jsonl", "missing_units.json", "failed_units.jsonl", "lock metadata"],
      "summary": ["integrity report", "per-unit table", "statistics", "belief update", "GO/HOLD/STOP"]
    },
    "rollout_fields": ["task_id", "benchmark", "split", "requested/resolved model", "rollout index", "seed", "K", "input/prompt/skill SHA", "raw trajectory", "tool calls", "output SHA", "verifier", "receipt hash", "tokens", "wall time", "technical status"],
    "pool_fields": ["pool_id", "task_id", "exact rollout hashes", "winner index/score", "nested prefix pools", "mixed flag", "rescue flag"],
    "projection_fields": ["rule", "source pool SHA", "selected indices", "evidence packet SHA", "token count"],
    "update_fields": ["skill_pre/post and SHAs", "updater input/receipt", "candidate patch SHA", "validation", "accept/reject"],
    "timeout_rule": "After MCP 502, message timeout, or SSH disconnect, inspect process, lock, completed manifest, checkpoint, and summary before any launch; duplicate launch is forbidden."
  },
  "budget": {
    "empirical_rate_source": "E0-r3: 96 actor rollouts, 566 provider calls, 1711693 total tokens",
    "empirical_actor_rate": {"provider_calls_per_rollout": 5.895833333333333, "tokens_per_rollout": 17830.135416666668},
    "S0_extension_estimate": {"actor_rollouts": 336, "provider_calls": 1981, "actor_tokens": 5990926, "gpu": "none for Ark actor; CPU workbook execution on 69"},
    "E1_estimate": {
      "pool_actor_rollouts": 768,
      "frozen_eval_rollouts": 1296,
      "actor_rollouts_total": 2064,
      "actor_provider_calls_estimate": 12169,
      "actor_tokens_estimate": 36801400,
      "updater_units": 72,
      "updater_calls": 720,
      "updater_tokens": "Freeze from live updater Pilot; do not extrapolate from the zero-provider mock receipt.",
      "gpu": "none for Ark actor/updater; CPU workbook execution on 69"
    },
    "E2_verified_core_primary_partition_formula": {
      "pool_rollouts": "M * 160 * 8, shared across methods within each one-step stream",
      "update_calls": "M * 20 streams * C core methods * 10 MindMemOS updater calls",
      "validation_and_test_rollouts": "M * 20 * C * (8 validation + 10 test)",
      "example_M4_C4": {"pool_rollouts": 5120, "updater_calls": 3200, "validation_and_test_rollouts": 5760},
      "replications": "Additional complete replications are limited to two representative models and budgeted only after Pilot token/latency measurements."
    },
    "E2_skill_evolbench_formula": {
      "acquisition_rollouts": "M * 30 cells * 3 acquisition tasks * K",
      "evaluation_rollouts": "M * 30 * C * 3 frozen evaluation tasks",
      "example_M4_C4_K8": {"acquisition_rollouts": 2880, "evaluation_rollouts": 1440},
      "updater_budget": "Native-updater calls and tokens frozen after adapter Pilot."
    },
    "open_model_gpu_plan": {
      "Qwen3.5-4B": "60 or 52 for Pilot; exact serving engine and GPU binding recorded",
      "Qwen_sparse_35B": "232 A100 preferred, or qualified tensor-parallel deployment on 52; availability and tool-use Pilot required",
      "DeepSeek_and_Kimi": "Ark API from 69; no local GPU claim"
    },
    "cost_rule": "No monetary estimate is published until per-model input/output token prices and live Pilot receipts are bound to the full contract. Calls and tokens are the primary auditable budget."
  },
  "manuscript_integration": {
    "live_branch": true,
    "sequence": [
      "E0 -> Mechanism Calibration",
      "E1 -> Causal Identification",
      "E2 -> Public Main Results and baseline comparison",
      "E3 -> Prospective Mechanism Prediction",
      "E4 -> Longitudinal Evolution",
      "E5 -> Topology and external validity"
    ],
    "no_hand_copied_numbers": true,
    "every_table_figure_binds_data_analysis_script_figure_script_sha": true
  },
  "review_required": {
    "reviewers": ["kimi-k3", "deepseek-v4-pro"],
    "questions": ["model selection", "baseline fairness", "benchmark roles", "Pilot nonselection", "sample size", "statistics", "checkpoint/recovery", "cost", "decisive STOP experiments"],
    "next_version": "V2 addresses only verdict-changing issues; runtime Pilot then freezes V3 full contracts."
  },
  "authority": {
    "planning": true,
    "dual_review": true,
    "outcome_blind_runtime_pilots": false,
    "S0_full_calls": false,
    "E1_calls": false,
    "public_full_calls": false,
    "paper_promotion": false,
    "frontend_promotion": false,
    "submission": false
  }
}


===== BOUND ARTIFACT: consultations/e2-r17-experiment-plan-v1-20260828.md =====
# E2-R17 Experiment Plan V1

Date: 2026-08-28T07:45:00+00:00
Status: **V1_REQUIRES_DUAL_REVIEW_AND_RUNTIME_PILOTS**

## 1. Scientific question and evidence chain

When a self-evolving agent generates a best-of-K search pool, does coupling the acting selector to winner-only learning censor reusable failed evidence and make the acting-optimal trajectory learning-suboptimal?

The paper separates two projections over the same generated search object:

- **Acting projection:** Serve the highest-verifier trajectory from the generated pool.
- **Learning projection:** Choose which content-addressed evidence from that same pool reaches the persistent updater.

Central claim: On precommitted rescue events, winner-only serving removes exactly the failed witness that rollout-0 would have exposed; if that witness has positive reusable diagnostic value, changing only the learning projection changes future frozen skill.

Minimal intervention: **Act from the winner; on a frozen rescue event learn from the precommitted rejected witness, otherwise learn from the winner.**

The evidence chain is deliberately sequential:

`S0 support -> E1 exact-same-pool causality -> E2 public effectiveness -> E3 prospective prediction -> E4 multi-round closure -> E5 topology/external validity`.

A failed earlier gate blocks later evidence. A benchmark zoo cannot rescue a failed exact-same-pool mechanism.

## 2. Current E0 status

The frozen E0 summary is `533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366`. Success@1 is 11/12 and Success@4/8 is 12/12. One rescue task in one family makes censoring nonzero, and the exact observed-pool identity holds, but the frozen threshold is at least six rescue tasks across at least three families.

Decision: **HOLD_FOR_PREDECLARED_E0_FULL**. E1 remains unauthorized.

Two independently generated analyses are retained rather than overwritten:

- `generated/e2-r17-e0-analysis-20260828.json`
- `generated/e2-r17-e0-pilot-analysis-20260828.json`

## 3. Global design rules

- Every stage follows Pilot -> protocol audit -> identifiability qualification -> immutable full contract -> full run -> integrity audit -> statistical analysis -> belief update.
- Pilot may reject an unusable runtime or degenerate capability regime; it may not select a model or baseline because R17 looks better.
- Executor and updater are separate roles. The executor matrix is run first with one frozen updater; a second updater is a later robustness check.
- Requested and resolved model identities, retry=0, thinking disabled, prompts, tool harness, verifier, budgets, and split hashes are frozen per tranche.
- Every completed rollout, pool, projection, update, and frozen evaluation is persisted immediately and content-addressed.
- After any timeout or MCP 502, inspect processes, locks, completed-unit manifests, and summaries before launching anything.

## 4. Model Choice Audit -> candidate matrix

The model matrix follows the closest baselines rather than server convenience. Qwen 4B supplies a weak open target, a precisely named Qwen sparse 35B release supplies the common open axis, DeepSeek V4-Pro supplies a strong literature-backed API axis, and Kimi K3 supplies a second family rather than a direct baseline-match claim.

| Role | Candidate | Status before Pilot |
|---|---|---|
| weak_open | Qwen3.5-4B | PILOT_REQUIRED |
| common_open | exact available Qwen3.5-35B-A3B or Qwen3.6-35B-A3B | AVAILABILITY_AND_PILOT_REQUIRED |
| strong_api | deepseek-v4-pro -> deepseek-v4-pro-ga-260813 | E0_QUALIFIED_REQUALIFY_EACH_TRANCHE |
| second_api_family | kimi-k3 | PILOT_REQUIRED |

Each candidate receives K=1 on 12 fixed development tasks and K=4 on four predeclared search-smoke tasks. Promotion requires 100% task loading and identity stability, >=95% tool parsing and verifier completion, >=90% artifact writing, <=5% technical failures, a verified missing-unit-only resume, and a K=1 result that is neither all-zero nor all-one. No R17 effect size is consulted.

The V1 core updater is `deepseek-v4-pro -> deepseek-v4-pro-ga-260813`. This is a proposal for review, not a frozen full-contract choice.

## 5. Baseline fidelity and placement

| Tier | Methods | Use |
|---|---|---|
| Official core | MindMemOS; RethinkSkill | substrate and matched feedback controls |
| Official extended | SkillOpt; SkillEvolBench | extended quantitative comparison / external validation |
| Paper-spec reconstruction | SkillCAT-style; Branch2Skill-style | explicitly labelled reconstruction, never exact reproduction |
| Context only | TSR | search/topology and compute-control related work |

E1 uses six arms: Winner-only, Precommitted rollout-0, Rejected-Witness, Duplicated Winner, Random Nonwinner, and SkillCAT-style contrast. The public core matrix uses Winner-only, Rejected-Witness, Full Pool, and the simplest surviving method. Extended methods run on one weak/common and one strong representative executor.

## 6. Stage contracts

### S0 — E0-full support qualification

Run only the 42 missing predeclared tasks; never rerun the completed 12. All tasks use K=8 once and derive K=1/2/4/8 from nested prefixes. GO requires >=6 rescue tasks across >=3 families with all integrity checks passing. Insufficient support stops this substrate before any updater intervention.

### E1 — Exact same-pool causal identification

Twelve independent eight-task streams generate 96 exact K=8 pools. Six cloned arms share task, initial-skill SHA, pool, served winner, actor, verifier, updater, budget, and 18 common held-out K=1 probes. The only treatment is the updater-visible evidence packet.

Primary estimand: `Delta_s = J_s(Rejected-Witness)-J_s(Winner-only)`. Inference uses the 12 stream states, an exact one-sided 2^12 sign-flip test, and a 10,000-draw paired bootstrap. Rollouts and probes are not independent replicates.

GO requires positive mean Delta, p<=0.05, a positive 95% CI lower bound, valid provenance, enough rescue support, and no duplicated-winner equivalence. A same-pool null is a central STOP, not a reason to add benchmarks.

### E2 — Public benchmark effectiveness

#### SpreadsheetBench Verified-400

Before outcomes, split the released 400 tasks by content hash and released metadata only:

| Lane | Tasks | Role |
|---|---:|---|
| Runtime development | 16 | model/baseline qualification; never confirmatory |
| Evolution | 160 | twenty one-step streams of eight tasks |
| Validation | 24 | common candidate-skill acceptance/rollback support |
| Test | 200 | untouched frozen K=1 endpoint |

Each evolution stream starts from the same initial skill across methods, generates one exact K=8 pool per task, updates one cloned state per method, and is paired with ten disjoint test tasks. The 20 stream means are the primary paired units; the 200 test tasks are not treated as 200 independent learned skills.

All four qualified executors run the four core methods. Extended baselines run on two representative executors. The primary metric is average frozen K=1 success with paired model-specific confidence intervals and Delta versus Winner-only. Cross-model averages are descriptive/model-stratified rather than an inflated significance test over four models.

#### SkillEvolBench

Use the official 30 environment-by-skill-family cells. T1-T3 are acquisition and T4-T6 are frozen evaluation. Nested acquisition pools are common across projection arms, while the native updater is used only after official adapter/validator qualification. The cell, not each task, is the scientific unit.

A null/negative Verified-400 transport result cannot be rescued by opening SpreadsheetBench 2.

### E3 — Prospective mechanism prediction

Estimate family-level censoring mass and diagnostic value on calibration units, then hash-freeze effect signs, family ranking, K ordering, and null cells before confirmatory outcomes are opened. Evaluate sign accuracy, rank correlation, calibration, absolute error, and null-cell false positives. A post-hoc fit is not predictive theory.

### E4 — Multi-round persistent evolution

Run L/L, H/Winner, H/Precommitted, H/Rejected, and H/final-method arms. V1 proposes eight independent streams, five rounds, eight tasks per round, and 24 common K=1 probes after each frozen skill state. Report online reward and frozen skill separately; first-round causality is not conflated with later path dependence.

### E5 — Topology and external validity

A 2x2 matched-call factorial compares parallel best-of-8 versus sequential refinement and winner/final-only versus history-preserving learning. This tests whether persistent differences arise from the learning projection rather than compute amount. SpreadsheetBench 2 is optional only after prior GO and a separate pre-outcome evaluator contract.

## 7. Checkpoint-first execution

- `raw/` is immutable and contains every provider-hash-bound trajectory, output workbook, verifier receipt, pool, projection packet, updater input/output, skill pre/post state, and frozen evaluation.
- `checkpoints/` contains completed, missing, and failed unit manifests plus lock metadata.
- `summary/` is fully rebuildable from raw artifacts.
- A pool is frozen immediately after K rollouts; a projection is frozen before update; an update stores candidate/accepted/rejected states; each skill-by-held-out-task evaluation is persisted immediately.
- Resume verifies SHA-256 and executes only missing units. Completed provider calls are never repeated after timeout, disconnect, or duplicate launcher invocation.

## 8. Calls, tokens, and compute budget

Empirical E0 rate: E0-r3: 96 actor rollouts, 566 provider calls, 1711693 total tokens, or 5.896 provider calls and 17830 tokens per actor rollout.

| Stage | Actor rollouts | Provider/update calls | Actor tokens | Compute placement |
|---|---:|---:|---:|---|
| S0 missing 42 tasks | 336 | ~1981 actor calls | ~5990926 | Ark + CPU workbook execution on 69 |
| E1 pools + frozen evaluation | 2064 | ~12169 actor + 720 updater calls | ~36801400 actor tokens | Ark + CPU workbook execution on 69 |
| Verified core, 4 models x 4 methods, primary partition | 10880 | 3200 updater calls plus actor-call expansion measured in Pilot | fixed after per-model Pilot | API models on 69; Qwen 4B on 60/52; Qwen 35B preferably 232 |
| SkillEvolBench example, 4 models x 4 methods, K=8 | 4320 | native updater budget frozen after adapter Pilot | fixed after Pilot | official harness-qualified placement |

The plan deliberately does not invent monetary cost or live-updater token estimates. V3 binds current model prices and Pilot receipts before a full authorization.

## 9. GO / HOLD / STOP discipline

- S0 insufficient support: STOP this substrate before E1.
- E1 exact-same-pool null or duplicated-winner equivalence: central mechanism STOP.
- Public positive only in a bounded model/benchmark regime: HOLD and report the boundary; do not add a rescue benchmark.
- Prospective prediction failure: delete predictive-theory claim even if the method improves average success.
- Rejected-Witness matches any complex variant: keep Rejected-Witness and delete the extra method name.

## 10. Next gate

Kimi K3 and DeepSeek V4-Pro independently review this exact V1 artifact for model selection, baseline fidelity, benchmark roles, Pilot nonselection, sample size, inference, checkpoint/recovery, cost, and decisive STOP rules. V2 changes only verdict-relevant defects. Runtime Pilots and every full experiment remain unauthorized until their own content-addressed contracts are frozen.


===== BOUND ARTIFACT: generated/e2-r17-baseline-model-choice-audit-20260828.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-baseline-model-choice-audit",
  "created_at_utc": "2026-08-28T07:30:00+00:00",
  "status": "V1_PRIMARY_SOURCE_AUDIT_COMPLETE",
  "question": "Which executor and updater models are actually used by the strongest adjacent baselines, and which comparisons can be reproduced faithfully in E2-R17?",
  "rows": [
    {
      "work": "MindMemOS",
      "benchmark": ["SpreadsheetBench Verified-400"],
      "actor_executor": "Released evaluation CLI and default use gpt-5.4-mini; the public result table itself does not bind its numbers to an explicit model identifier.",
      "updater_teacher": "Configured MindMemOS chat endpoint; the released public result table does not expose a distinct updater model identity.",
      "interface": "OpenAI-compatible API plus MindMemOS service",
      "model_size": "Closed/API; undisclosed",
      "why_this_model": "First-party released runtime default and reproduction command.",
      "reusable_in_r17": "YES_CORE_SUBSTRATE. Exact runtime is locally pinned; model-role claims must be limited to what the released config binds.",
      "implementation_fidelity": "OFFICIAL_CODE_LOCAL_PIN",
      "source": {
        "local_repo": "/data/wyt/evidence-substrates/MindMemOS-20260817",
        "commit": "90491828726e1540442b17cd445d0308d0b8093c",
        "files": [
          "docs/eval/README.md",
          "src/mindmemos_eval/mindmemos_eval/skills/args.py",
          "README.md"
        ]
      }
    },
    {
      "work": "SkillCAT",
      "benchmark": ["SpreadsheetBench", "WikiTableQuestions", "DocVQA"],
      "actor_executor": "Qwen3.5-35B-A3B and Qwen3.5-122B-A10B as skill users; transfer users Gemma-4-31B-it and GPT-5.4-mini.",
      "updater_teacher": "Qwen3.5-35B-A3B and Qwen3.5-122B-A10B as skill authors.",
      "interface": "Open-weight Qwen/Gemma plus API GPT; ReAct filesystem and spreadsheet tools",
      "model_size": "35B sparse, 122B sparse, 31B, closed/API",
      "why_this_model": "Matches Trace2Skill-style settings and tests matched author/user plus cross-model transfer.",
      "reusable_in_r17": "PARTIAL. Reuse CCE as a SkillCAT-style same-task success/failure contrast arm; full CCE+AAE+TTE requires a separate faithful implementation and source-task replay budget.",
      "implementation_fidelity": "PAPER_SPEC_ONLY_NO_OFFICIAL_REPO_FOUND_IN_AUDIT",
      "source": {
        "paper": "https://arxiv.org/html/2606.13317v2",
        "evidence": ["Section 4.1 models and baselines", "CCE K=5", "AAE source-task clone validation", "TTE Top-k=7"]
      }
    },
    {
      "work": "Branch2Skill",
      "benchmark": ["SearchQA", "SpreadsheetBench", "OfficeQA", "DocVQA", "LiveMath", "ALFWorld"],
      "actor_executor": "GPT-5.5, GPT-5.4, GPT-5.4-mini, GPT-5.4-nano, Qwen3.6-35B-A3B.",
      "updater_teacher": "GPT-5.5 for all main-table results except the model-role analysis.",
      "interface": "API/Qwen target model plus MCTS reasoning-tree construction",
      "model_size": "35B sparse and closed/API models",
      "why_this_model": "Separates target and skill model and tests transfer of branch evidence across model identities.",
      "reusable_in_r17": "PAPER_SPEC_EXTENDED_ONLY. Map elite-path versus shared-prefix sibling evidence into the common projection abstraction, but do not claim exact reproduction until code is released.",
      "implementation_fidelity": "CODE_NOT_RELEASED_AS_OF_AUDIT",
      "source": {
        "paper": "https://arxiv.org/html/2608.08677v1",
        "evidence": ["Section 4.1 target/skill models", "elite path plus same-parent siblings", "validation rollback", "paper states code will be published"]
      }
    },
    {
      "work": "SkillOpt",
      "benchmark": ["SearchQA", "SpreadsheetBench", "OfficeQA", "DocVQA", "LiveMath", "ALFWorld"],
      "actor_executor": "GPT-5.5, GPT-5.4, GPT-5.4-mini, GPT-5.4-nano, GPT-5.2, Qwen3.5-4B, Qwen3.6-35B-A3B.",
      "updater_teacher": "Separate optimizer model; paper-style examples commonly use GPT-5.5, while matched self-optimizer settings are also supported.",
      "interface": "OpenAI/Azure/Claude/Qwen/MiniMax backends; direct chat, Codex, Claude Code",
      "model_size": "4B, 35B sparse, closed/API",
      "why_this_model": "Deliberately spans weak-to-frontier targets and keeps the optimizer role independent.",
      "reusable_in_r17": "YES_EXTENDED_STRONG_BASELINE. Official implementation can be adapted to the same benchmark/split and fixed actor/updater roles; rollout, edit, validation, and token budgets must be matched and logged.",
      "implementation_fidelity": "OFFICIAL_CODE_AVAILABLE",
      "source": {
        "repo": "https://github.com/microsoft/SkillOpt",
        "project": "https://microsoft.github.io/SkillOpt/",
        "evidence": ["separate frozen target and optimizer", "seven target models", "bounded add/delete/replace edits", "held-out validation gate"]
      }
    },
    {
      "work": "Rethinking Self-Evolving Agent Skills / RethinkSkill",
      "benchmark": ["SearchQA", "OfficeQA", "SpreadsheetBench", "LiveMath", "DocVQA"],
      "actor_executor": "GPT-5.5, Gemini 3.1 Pro, DeepSeek V4-Pro.",
      "updater_teacher": "Same model configuration as executor in the primary paper; released framework can configure target and optimizer backends separately.",
      "interface": "OpenAI-compatible HTTP, Codex, Claude Code, Gemini CLI",
      "model_size": "Closed/API; DeepSeek V4-Pro 1.6T total / 49B active per official model release",
      "why_this_model": "Controlled feedback-view study across strong model families; directly tests Normal, Fail-only, and Success-only.",
      "reusable_in_r17": "YES_CORE_CONTROL_AND_MULTIROUND. Official code supports matched feedback arms and complete candidate/rollback logging; R17 must retain exact same-pool acting winner to isolate projection more tightly.",
      "implementation_fidelity": "OFFICIAL_CODE_AVAILABLE",
      "source": {
        "paper": "https://arxiv.org/html/2608.02636v1",
        "repo": "https://github.com/HKUST-KnowComp/rethinkskill",
        "evidence": ["42 matched feedback runs", "three primary models", "same executor/optimizer configuration in paper", "provider-role separation in released code"]
      }
    },
    {
      "work": "TSR",
      "benchmark": ["Sokoban", "FrozenLake", "WebShop"],
      "actor_executor": "Qwen2.5-0.5B and Qwen2.5-3B; WebShop uses Qwen2.5-3B.",
      "updater_teacher": "PPO or GRPO parameter update; no external natural-language skill updater.",
      "interface": "Open-weight policy training with best-of-N, beam, or shallow lookahead search",
      "model_size": "0.5B and 3B",
      "why_this_model": "Studies search-shaped training trajectories in small parametric RL agents.",
      "reusable_in_r17": "NO_AS_MAIN_SKILL_BASELINE. Use as search/topology and compute-control context, not as a directly comparable projection method on SpreadsheetBench.",
      "implementation_fidelity": "PAPER_SPEC_CODE_PROMISED_UPON_ACCEPTANCE",
      "source": {
        "paper": "https://arxiv.org/html/2602.11767",
        "evidence": ["Qwen2.5 model scales", "Sokoban/FrozenLake/WebShop", "PPO/GRPO", "code release promised upon acceptance"]
      }
    },
    {
      "work": "SkillEvolBench",
      "benchmark": ["180 tasks: 6 environments x 5 latent skill families x 6 tasks"],
      "actor_executor": "Claude Code Opus/Sonnet 4.5/4.6, Codex GPT-5.2/5.3-Codex and GPT-5.4, Gemini CLI 2.5 Pro/3 Flash/3.1 Pro; repository also provides Kimi-style provider presets.",
      "updater_teacher": "Condition-dependent self-generated or curated revision within each harness/model configuration.",
      "interface": "Harbor plus Claude Code, Codex, Gemini CLI, Kimi CLI adapters",
      "model_size": "Closed/API",
      "why_this_model": "Cross-harness public testbed with frozen acquisition/evaluation task structure.",
      "reusable_in_r17": "YES_SECONDARY_EXTERNAL_VALIDATION_AFTER_ADAPTER_PILOT. It is not a drop-in same-pool spreadsheet causal test; use its learning T1-T3 and frozen evaluation T4-T6 structure for external validation.",
      "implementation_fidelity": "OFFICIAL_CODE_AVAILABLE",
      "source": {
        "repo": "https://github.com/AIoT-MLSys-Lab/SkillEvolBench",
        "project": "https://skillevolbench.github.io/",
        "evidence": ["180-task fixed stratified design", "model/provider presets", "canonical baseline ladder", "preflight and run validators"]
      }
    }
  ],
  "cross_work_findings": {
    "common_executor_anchor": "A Qwen sparse 35B-class executor is the strongest open/common comparison axis: Qwen3.5-35B-A3B in SkillCAT and Qwen3.6-35B-A3B in Branch2Skill/SkillOpt. These are different released models and must not be conflated.",
    "weak_anchor": "Qwen3.5-4B is the literature-backed weak open target from SkillOpt; it enters R17 only if outcome-blind tool-use/headroom qualification passes.",
    "strong_non_qwen_anchor": "DeepSeek V4-Pro is directly used in RethinkSkill and is already qualified in E0; it is a defensible strong cross-family executor and frozen updater candidate.",
    "diversity_anchor": "Kimi K3 is not a common baseline model in the closest methods. It may enter as a second API/model-family robustness axis only after tool qualification, and must not be presented as direct baseline matching.",
    "role_separation": "Actor/executor and updater/skill author are distinct scientific roles in SkillOpt and Branch2Skill. R17 core experiments should freeze one updater while varying executors, then test updater robustness only after the mechanism passes.",
    "implementation_tiers": {
      "core_official": ["MindMemOS", "RethinkSkill"],
      "extended_official": ["SkillOpt", "SkillEvolBench"],
      "paper_spec_only": ["SkillCAT", "Branch2Skill", "TSR"]
    }
  },
  "candidate_model_matrix_v1": [
    {
      "role": "weak_open_candidate",
      "model": "Qwen3.5-4B",
      "justification": "SkillOpt weak target; capability-spread anchor",
      "status": "PILOT_REQUIRED_NOT_FROZEN"
    },
    {
      "role": "common_open_candidate",
      "model": "Qwen3.5-35B-A3B or Qwen3.6-35B-A3B, exact available release to be chosen before Pilot",
      "justification": "Closest common open axis across SkillCAT, Branch2Skill, and SkillOpt",
      "status": "AVAILABILITY_AND_TOOL_PILOT_REQUIRED"
    },
    {
      "role": "strong_api_qualified",
      "model": "deepseek-v4-pro -> deepseek-v4-pro-ga-260813",
      "justification": "RethinkSkill primary model and completed E0 runtime qualification",
      "status": "E0_QUALIFIED_REQUALIFY_PER_TRANCHE"
    },
    {
      "role": "second_family_api_candidate",
      "model": "kimi-k3",
      "justification": "Family diversity and available Ark route; not a direct baseline-match claim",
      "status": "PILOT_REQUIRED_NOT_FROZEN"
    }
  ],
  "updater_policy_v1": {
    "core": "Freeze DeepSeek V4-Pro as updater for the executor matrix because its identity and MindMemOS runtime are already qualified; keep updater prompts, token budget, validation, and skill initialization fixed.",
    "robustness": "After E1 passes, repeat the primary contrast with one second updater backend (Kimi K3 or the qualified Qwen 35B model), not a full actor x updater cross-product.",
    "limitation": "The closest papers often use GPT-5.5 as a strong optimizer; current infrastructure does not provide that route, so R17 must report this mismatch rather than imply exact reproduction."
  },
  "authority": {
    "model_matrix_freeze": false,
    "model_calls": false,
    "gpu": false,
    "e0_full": false,
    "e1": false,
    "paper_promotion": false,
    "submission": false
  }
}


===== BOUND ARTIFACT: consultations/e2-r17-baseline-model-choice-audit-20260828.md =====
# E2-R17 Baseline and Model Choice Audit — V1

Date: 2026-08-28
Status: **primary-source audit complete; model matrix not yet frozen**

## 1. Audit question

The purpose of this audit is not to list fashionable models. It asks which executor and updater models the closest methods actually use, which implementations are available, and which comparisons can be mapped fairly into the E2-R17 projection protocol.

The closest works agree on two design facts:

1. executor/target and updater/skill author are separate scientific roles;
2. a Qwen sparse 35B-class model is the most credible open/common comparison axis, while strong API models provide capability and family diversity.

## 2. Model Choice Audit Table

| Work | Benchmark | Actor / Executor | Updater / Teacher | Open/API | Model size | Why this model | Reusable in our protocol? |
|---|---|---|---|---|---|---|---|
| MindMemOS | SpreadsheetBench Verified-400 | Released CLI/default: `gpt-5.4-mini`; the public result table itself does not bind its numbers to an explicit model ID | Configured MindMemOS chat endpoint; public table does not expose a distinct updater ID | API | undisclosed | First-party released runtime and reproduction command | **Yes, core substrate.** The locally pinned runtime is exact; model claims must follow the released config rather than infer a hidden table setting. |
| SkillCAT | SpreadsheetBench, WikiTQ, DocVQA | Qwen3.5-35B-A3B and Qwen3.5-122B-A10B; transfer users Gemma-4-31B-it and GPT-5.4-mini | The two Qwen models are also skill authors | open + API | 35B sparse, 122B sparse, 31B, closed | Matched author/user and cross-model transfer | **Partial.** CCE maps to a same-task success/failure contrast arm. Full CCE+AAE+TTE needs source-task replay and routing; no official code was found in this audit. |
| Branch2Skill | SearchQA, SpreadsheetBench, OfficeQA, DocVQA, LiveMath, ALFWorld | GPT-5.5, GPT-5.4, GPT-5.4-mini, GPT-5.4-nano, Qwen3.6-35B-A3B | GPT-5.5 in all main-table runs except model-role analysis | open + API | 35B sparse + closed | Explicitly tests branch-evidence transfer across target/skill identities | **Paper-spec extended baseline only.** Map elite path and same-parent siblings to the common projection interface; do not claim exact reproduction before code release. |
| SkillOpt | Six benchmarks above | GPT-5.5, GPT-5.4, GPT-5.4-mini, GPT-5.4-nano, GPT-5.2, Qwen3.5-4B, Qwen3.6-35B-A3B | Separate optimizer model, commonly GPT-5.5; matched self-optimizer also supported | open + API | 4B, 35B sparse + closed | Deliberate weak-to-frontier spread and independent optimizer role | **Yes, extended strong baseline.** Official code is available. Match benchmark, split, actor/updater roles, rollout/edit/validation budgets, and receipts. |
| Rethinking Self-Evolving Agent Skills / RethinkSkill | SearchQA, OfficeQA, SpreadsheetBench, LiveMath, DocVQA | GPT-5.5, Gemini 3.1 Pro, DeepSeek V4-Pro | Same model configuration as executor in the primary paper; released code allows separate backends | API | DeepSeek V4-Pro: 1.6T total / 49B active; other sizes undisclosed | Controlled Normal/Fail-only/Success-only feedback study across model families | **Yes, core control and multi-round baseline.** Official code and complete rollback/candidate logging exist. R17 adds a stricter same-pool/same-winner intervention. |
| TSR | Sokoban, FrozenLake, WebShop | Qwen2.5-0.5B and Qwen2.5-3B; WebShop uses 3B | PPO/GRPO parameter update, no external skill updater | open | 0.5B, 3B | Tests search-shaped training rollouts in small policies | **No as a main skill baseline.** Use for search/topology and compute-control context, not direct SpreadsheetBench projection comparison. |
| SkillEvolBench | 180 tasks: 6 environments × 5 skill families × 6 tasks | Claude Code Opus/Sonnet 4.5/4.6; Codex GPT-5.2/5.3-Codex and GPT-5.4; Gemini 2.5 Pro/3 Flash/3.1 Pro; Kimi-style presets | Condition-dependent revision in the same harness/model configuration | API/CLI | undisclosed | Public cross-harness acquisition/evaluation testbed | **Yes, secondary external validation after adapter Pilot.** Its T1–T3 learning and T4–T6 frozen evaluation structure is useful, but it is not a drop-in same-pool spreadsheet causal test. |

## 3. Fidelity tiers

### Tier A — official implementation suitable for a quantitative table

- **MindMemOS**: exact local commit `90491828726e1540442b17cd445d0308d0b8093c`.
- **RethinkSkill**: official implementation of matched feedback arms and multi-round validation.
- **SkillOpt**: official implementation of target/optimizer separation, bounded edits, and held-out validation.
- **SkillEvolBench**: official benchmark and adapters, subject to runtime qualification.

### Tier B — paper-spec method mapping only

- **SkillCAT**: use a clearly labelled `SkillCAT-style contrast` arm unless an official repository is released and pinned.
- **Branch2Skill**: the paper states that code will be published; current E2-R17 implementation can only be a protocol-aligned reconstruction.
- **TSR**: code is promised upon acceptance and the scientific object is parametric RL, not external skills.

A paper-spec reconstruction must never be labelled as an exact reproduction.

## 4. Cross-work conclusions

### 4.1 Common model axis

The strongest open/common axis is a **Qwen sparse 35B-class executor**:

- SkillCAT: Qwen3.5-35B-A3B;
- Branch2Skill and SkillOpt: Qwen3.6-35B-A3B.

These are different releases. E2-R17 must pick the exact available model after runtime qualification and name it exactly; it must not merge them into a generic “Qwen-35B” result.

### 4.2 Weak-model axis

Qwen3.5-4B is the clearest literature-backed weak target because SkillOpt reports it across the full benchmark family. It is only a candidate. It enters the main matrix if an outcome-blind Pilot confirms valid tool calls, artifact writing, verifier completion, and nondegenerate K=1 headroom.

The 0.5B/3B TSR models are not appropriate SpreadsheetBench anchors: they were trained with RL on Sokoban/FrozenLake/WebShop and answer a different question.

### 4.3 Strong cross-family axis

DeepSeek V4-Pro is a primary RethinkSkill model and the E0 actor already resolved stably to `deepseek-v4-pro-ga-260813`. It is therefore a defensible strong executor and frozen-updater candidate, subject to a light identity qualification for every new tranche.

Kimi K3 contributes a second API/model family and is available through the current Ark route, but it is not the common model used by the closest baselines. It should be described as robustness/diversity, not as baseline matching.

### 4.4 Actor and updater policy

The core public matrix should first vary executor while freezing the updater:

```text
executor ∈ {weak Qwen candidate, common Qwen-35B candidate, DeepSeek V4-Pro, Kimi K3}
updater  = one frozen, qualified strong updater
```

The V1 updater choice is DeepSeek V4-Pro because its Ark identity and MindMemOS runtime are already qualified. A second updater is a robustness experiment only after E1 passes. Do not run a 4×4 actor/updater cross-product.

The closest papers often use GPT-5.5 as the optimizer. That endpoint is not available in the current infrastructure, so the manuscript must report the mismatch instead of implying an exact model-level reproduction.

## 5. Candidate model matrix before Pilot

| Role | Candidate | Literature basis | Current status | Promotion gate |
|---|---|---|---|---|
| Weak open | Qwen3.5-4B | SkillOpt weak target | not qualified | valid-task/tool/file/verifier rate; useful K=1 headroom; stable identity |
| Common open | exact available Qwen3.5-35B-A3B **or** Qwen3.6-35B-A3B | SkillCAT / Branch2Skill / SkillOpt | availability unresolved | exact release pinned; tool qualification; no model-name substitution |
| Strong API | DeepSeek V4-Pro → `deepseek-v4-pro-ga-260813` | RethinkSkill + completed E0 | E0 qualified | light requalification per tranche |
| Second-family API | Kimi K3 | diversity and available Ark route | adapter qualified earlier, scientific tranche pending | tool/artifact/verifier/headroom and resolved identity |

A model cannot be selected because R17 gains look larger in Pilot. Promotion is based only on protocol validity, identifiability, headroom, stability, latency, and cost.

## 6. Baseline placement in the eventual paper

### Core methods across all qualified executors

- Winner-only
- Rejected Witness
- Full Pool
- final simplest R17 method, unless it is identical to Rejected Witness

### Extended methods on one or two representative executors

- Initial Skill / No Skill
- Precommitted rollout-0
- Duplicated Winner
- Random Nonwinner
- SkillCAT-style contrast
- RethinkSkill feedback arms
- SkillOpt
- Branch2Skill-style reconstruction

SkillEvolBench belongs in external validation, not in the exact-same-pool E1 causal table. TSR belongs in related work and the topology/compute-control analysis.

## 7. Primary sources audited

- MindMemOS local official checkout, commit `90491828726e1540442b17cd445d0308d0b8093c`: `docs/eval/README.md`, `skills/args.py`, and `README.md`.
- SkillCAT v2: <https://arxiv.org/html/2606.13317v2>.
- Branch2Skill v1: <https://arxiv.org/html/2608.08677v1>.
- SkillOpt official code/project: <https://github.com/microsoft/SkillOpt> and <https://microsoft.github.io/SkillOpt/>.
- RethinkSkill paper/code: <https://arxiv.org/html/2608.02636v1> and <https://github.com/HKUST-KnowComp/rethinkskill>.
- TSR: <https://arxiv.org/html/2602.11767>.
- SkillEvolBench: <https://github.com/AIoT-MLSys-Lab/SkillEvolBench> and <https://skillevolbench.github.io/>.

## 8. Decision

**The model matrix remains unfrozen until runtime Pilot.** The audit authorizes creation of Experiment Plan V1 and outcome-blind model qualification; it does not authorize E0-full, E1, public-benchmark full runs, paper promotion, or submission.


===== BOUND ARTIFACT: generated/e2-r17-e0-analysis-20260828.json =====
{
  "artifact_type": "e2-r17-e0-analysis",
  "schema_version": "1.0",
  "created_at_utc": "2026-08-28T07:17:33.012687+00:00",
  "read_only_source": true,
  "source": {
    "run_root": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828",
    "summary_path": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/e0_pilot_summary.json",
    "summary_sha256": "533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366",
    "contract_path": "generated/e2-r17-f0-r4-frozen-candidate-contract-20260828.json",
    "contract_sha256": "f4019646b653f41abe056fdd7b746ff6cb4749ce4d2771c2ef90af6845631508",
    "authorization_path": "generated/e2-r17-e0-pilot-authorization-r3-20260828.json",
    "authorization_sha256": "5033c226b7248c3d9f72caa2b574f84ffa4ae9c3097175bde87e9b469c9fdff4"
  },
  "protocol_integrity": {
    "tasks_complete": 12,
    "expected_tasks": 12,
    "trajectory_files": 96,
    "trajectory_ref_files": 96,
    "pool_files": 48,
    "unique_rollout_units": 96,
    "technical_failures": 0,
    "actor_finished_false_unit_count": 1,
    "actor_finished_false_units": [
      {
        "case_id": "r17-b1-ioc-p2",
        "rollout_index": 7,
        "score": 1.0,
        "turns": 10,
        "output_sha256": "cb3af592123ac32d229a48f773dc47f2bd79f6f0594baee361bb231125a4fef6"
      }
    ],
    "resolved_models": {
      "deepseek-v4-pro-ga-260813": 96
    },
    "provider_calls_reconstructed": 566,
    "total_tokens_reconstructed": 1711693,
    "k": 8,
    "prefix_ks": [
      1,
      2,
      4,
      8
    ]
  },
  "acting": {
    "success_at_k": {
      "1": 0.9166666666666666,
      "2": 0.9166666666666666,
      "4": 1.0,
      "8": 1.0
    },
    "delta_vs_success_at_1": {
      "1": 0.0,
      "2": 0.0,
      "4": 0.08333333333333337,
      "8": 0.08333333333333337
    },
    "mixed_pool_count": {
      "1": 0,
      "2": 1,
      "4": 6,
      "8": 8
    },
    "mixed_pool_rate": {
      "1": 0.0,
      "2": 0.08333333333333333,
      "4": 0.5,
      "8": 0.6666666666666666
    },
    "rescue_event_count": {
      "1": 0,
      "2": 0,
      "4": 1,
      "8": 1
    },
    "rescue_event_rate": {
      "1": 0.0,
      "2": 0.0,
      "4": 0.08333333333333333,
      "8": 0.08333333333333333
    }
  },
  "visibility": {
    "V_pre": {
      "1": 0.08333333333333333,
      "2": 0.08333333333333333,
      "4": 0.08333333333333333,
      "8": 0.08333333333333333
    },
    "V_winner": {
      "1": 0.08333333333333333,
      "2": 0.08333333333333333,
      "4": 0.0,
      "8": 0.0
    },
    "Gamma": {
      "1": 0.0,
      "2": 0.0,
      "4": 0.08333333333333333,
      "8": 0.08333333333333333
    },
    "identity_check_max_abs_error": 4.163336342344337e-17
  },
  "iid_special_case_reference": {
    "pooled_rollout_success_p": 0.8333333333333334,
    "formula": "Gamma_K(p)=(1-p)-(1-p)^K",
    "Gamma": {
      "1": 0.0,
      "2": 0.13888888888888887,
      "4": 0.16589506172839502,
      "8": 0.16666607129248587
    },
    "interpretation": "reference only; observed task pools are heterogeneous and need not be iid"
  },
  "failure_support": {
    "k8_failure_families_with_any_failed_rollout": [
      "aggregation_join",
      "formula_materialization",
      "input_output_contract",
      "schema_key_alignment",
      "target_sheet_range"
    ],
    "k8_mixed_pool_families": [
      "aggregation_join",
      "formula_materialization",
      "input_output_contract",
      "schema_key_alignment",
      "target_sheet_range"
    ],
    "k8_rescue_tasks": [
      {
        "task_id": "r17-b1-tsr-p7",
        "failure_family": "target_sheet_range",
        "scores": [
          0.0,
          0.0,
          1.0,
          1.0,
          1.0,
          1.0,
          0.0,
          1.0
        ],
        "winner_index": 2
      }
    ],
    "k8_rescue_task_count": 1,
    "k8_rescue_families": [
      "target_sheet_range"
    ],
    "k8_rescue_family_count": 1
  },
  "interpretation": {
    "search_improves_acting": true,
    "winner_only_censors_precommitted_failure_on_rescueable_pool": true,
    "ceiling_warning": true,
    "observed_regime": "one rescueable intermediate cell inside an otherwise high-success/ceiling-heavy pilot",
    "alternative_explanations": [
      "task-level capability heterogeneity makes the pooled-iid reference overpredict censoring mass",
      "the 12-task pilot is ceiling-heavy, so rescue support is sparse",
      "E0 identifies visibility structure only; it does not establish future learning utility"
    ]
  },
  "promotion_gate": {
    "frozen_text": "at least 6 rescue tasks and >=3 families; otherwise HOLD/STOP before updater",
    "required_rescue_tasks": 6,
    "required_failure_families": 3,
    "observed_rescue_tasks": 1,
    "observed_failure_families": 1,
    "pass": false
  },
  "belief_update": "Search-projection censoring is empirically nonzero in the frozen E0 pilot, but support is too sparse to authorize the updater intervention. The correct update is HOLD, not mechanism rejection: one precommitted failure is rescued and hidden by the winner at K>=4, while the frozen E1 support gate requires at least six rescue tasks spanning at least three failure families.",
  "decision": "HOLD",
  "authority": {
    "E1_scientific_experiment": false,
    "paper_promotion": false,
    "submission": false
  },
  "next": "Freeze and independently review a non-selective support-qualification tranche using only actor/verifier rescueability structure; do not select on projection or downstream learning outcomes. Planning, baseline/model audit, and outcome-blind runtime pilots may proceed while E1 remains blocked."
}


===== BOUND ARTIFACT: generated/e2-r17-e0-pilot-analysis-20260828.json =====
{
  "artifact_type": "e2-r17-e0-pilot-analysis",
  "authority": {
    "e0_full_calls": false,
    "e1_calls": false,
    "frontend_promotion": false,
    "paper_promotion": false,
    "submission": false,
    "support_qualification": true
  },
  "authorization_sha256": "5033c226b7248c3d9f72caa2b574f84ffa4ae9c3097175bde87e9b469c9fdff4",
  "contract_sha256": "f4019646b653f41abe056fdd7b746ff6cb4749ce4d2771c2ef90af6845631508",
  "created_at_utc": "2026-08-28T07:08:40+00:00",
  "decision": {
    "belief_update": "Rescue censoring is observable and the exact joint-pool identity holds, but support is one task in one family and cannot authorize E1.",
    "central_mechanism_stopped": false,
    "e0_full_gate": {
      "frozen_tasks": 54,
      "rescue_families_min": 3,
      "rescue_tasks_min": 6
    },
    "e1_authorized": false,
    "execution_rule": "Do not rerun the completed 12 tasks. Run only the 42 frozen extension tasks, then combine both content-addressed tranches.",
    "next": "E0_FULL_EXTENSION_ONLY",
    "pilot_support": {
      "rescue_families": [
        "target_sheet_range"
      ],
      "rescue_tasks": 1
    },
    "verdict": "HOLD_FOR_PREDECLARED_E0_FULL"
  },
  "failed_rollouts": {
    "count": 16,
    "families": [
      "aggregation_join",
      "formula_materialization",
      "input_output_contract",
      "schema_key_alignment",
      "target_sheet_range"
    ],
    "winner_visible_failed_tasks_k8": 0
  },
  "failure_families": {
    "aggregation_join": {
      "failures": 1,
      "mixed_k8": 1,
      "rescue_k8": 0,
      "successes": 15,
      "tasks": 2
    },
    "formula_materialization": {
      "failures": 5,
      "mixed_k8": 2,
      "rescue_k8": 0,
      "successes": 11,
      "tasks": 2
    },
    "input_output_contract": {
      "failures": 2,
      "mixed_k8": 1,
      "rescue_k8": 0,
      "successes": 14,
      "tasks": 2
    },
    "multi_step_pipeline": {
      "failures": 0,
      "mixed_k8": 0,
      "rescue_k8": 0,
      "successes": 16,
      "tasks": 2
    },
    "schema_key_alignment": {
      "failures": 4,
      "mixed_k8": 2,
      "rescue_k8": 0,
      "successes": 12,
      "tasks": 2
    },
    "target_sheet_range": {
      "failures": 4,
      "mixed_k8": 2,
      "rescue_k8": 1,
      "successes": 12,
      "tasks": 2
    }
  },
  "iid_reference_only": {
    "by_k": {
      "1": {
        "observed_gamma": 0.0,
        "pooled_curve": 0.0,
        "task_plugin_mean": 0.0
      },
      "2": {
        "observed_gamma": 0.0,
        "pooled_curve": 0.13888888888888887,
        "task_plugin_mean": 0.1171875
      },
      "4": {
        "observed_gamma": 0.08333333333333333,
        "pooled_curve": 0.16589506172839502,
        "task_plugin_mean": 0.1610107421875
      },
      "8": {
        "observed_gamma": 0.08333333333333333,
        "pooled_curve": 0.16666607129248587,
        "task_plugin_mean": 0.16656634211540222
      }
    },
    "note": "Reference only; exact analysis assumes neither independence nor exchangeability.",
    "pooled_p": 0.8333333333333334
  },
  "integrity": {
    "checks": {
      "credentials_absent": true,
      "k_8": true,
      "no_incomplete_dirs": true,
      "no_technical_failures": true,
      "outputs_match_successes": true,
      "prefixes_1_2_4_8": true,
      "provider_response_shas_unique": true,
      "raw_response_ids_absent": true,
      "retry_0": true,
      "rollout_count_96": true,
      "scientific_outcome": true,
      "status_completed": true,
      "summary_sha": true,
      "task_count_12": true,
      "thinking_disabled": true,
      "trajectory_shas_unique": true
    },
    "errors": [],
    "outputs": 80,
    "provider_calls": 566,
    "rollouts": 96,
    "status": "PASS",
    "tasks": 12,
    "total_tokens": 1711693
  },
  "metrics_by_k": {
    "1": {
      "gain_vs_k1": 0.0,
      "identity_exact": true,
      "mixed_count": 0,
      "mixed_families": [],
      "mixed_rate": 0.0,
      "n": 12,
      "pre_failure_visibility": 0.08333333333333333,
      "precommitted_success_rate": 0.9166666666666666,
      "rescue_count": 0,
      "rescue_families": [],
      "rescue_rate": 0.0,
      "success_count": 11,
      "success_rate": 0.9166666666666666,
      "visibility_gap": 0.0,
      "winner_failure_visibility": 0.08333333333333333
    },
    "2": {
      "gain_vs_k1": 0.0,
      "identity_exact": true,
      "mixed_count": 1,
      "mixed_families": [
        "input_output_contract"
      ],
      "mixed_rate": 0.08333333333333333,
      "n": 12,
      "pre_failure_visibility": 0.08333333333333333,
      "precommitted_success_rate": 0.9166666666666666,
      "rescue_count": 0,
      "rescue_families": [],
      "rescue_rate": 0.0,
      "success_count": 11,
      "success_rate": 0.9166666666666666,
      "visibility_gap": 0.0,
      "winner_failure_visibility": 0.08333333333333333
    },
    "4": {
      "gain_vs_k1": 0.08333333333333333,
      "identity_exact": true,
      "mixed_count": 6,
      "mixed_families": [
        "formula_materialization",
        "input_output_contract",
        "schema_key_alignment",
        "target_sheet_range"
      ],
      "mixed_rate": 0.5,
      "n": 12,
      "pre_failure_visibility": 0.08333333333333333,
      "precommitted_success_rate": 0.9166666666666666,
      "rescue_count": 1,
      "rescue_families": [
        "target_sheet_range"
      ],
      "rescue_rate": 0.08333333333333333,
      "success_count": 12,
      "success_rate": 1.0,
      "visibility_gap": 0.08333333333333333,
      "winner_failure_visibility": 0.0
    },
    "8": {
      "gain_vs_k1": 0.08333333333333333,
      "identity_exact": true,
      "mixed_count": 8,
      "mixed_families": [
        "aggregation_join",
        "formula_materialization",
        "input_output_contract",
        "schema_key_alignment",
        "target_sheet_range"
      ],
      "mixed_rate": 0.6666666666666666,
      "n": 12,
      "pre_failure_visibility": 0.08333333333333333,
      "precommitted_success_rate": 0.9166666666666666,
      "rescue_count": 1,
      "rescue_families": [
        "target_sheet_range"
      ],
      "rescue_rate": 0.08333333333333333,
      "success_count": 12,
      "success_rate": 1.0,
      "visibility_gap": 0.08333333333333333,
      "winner_failure_visibility": 0.0
    }
  },
  "model": {
    "requested": "deepseek-v4-pro",
    "resolved": "deepseek-v4-pro-ga-260813"
  },
  "regimes_k8": {
    "ceiling": 4,
    "mixed_pre_success": 7,
    "rescueable": 1
  },
  "run_root": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828",
  "schema_version": "1.0",
  "summary_sha256": "533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366",
  "task_rows": [
    {
      "family": "aggregation_join",
      "pools": {
        "1": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "ce121fd6b4c1fe47a2ba4109b815193ab83149c1b2b45b25536e505eb7eecb58",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "2": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "6878fe76199ad2c963852a9c6bcc4ce931fe266008abfb5a5d6adeb8a060ef11",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "4": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "90711f4f4ea985e9515e91fb400a00dc0f85087ca16e1244cba76c911f283b96",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "8": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "6da9aad96104496f767e5d8ca726db9dd3e3385762ea5b6f1ea6f155e2089238",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        }
      },
      "scores": [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1
      ],
      "task_id": "r17-b1-agj-p1"
    },
    {
      "family": "aggregation_join",
      "pools": {
        "1": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "151ae10513b1a7548fd1ee98b6349e7fd93c7891fcba31941674b6a60a0d0ef6",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "2": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "e2412d250219c6d16a646552b88a8cc55d7973a5482730ba682a6cec5a7c692e",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "4": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "3f46a44fbac7abb91a0eae302a9c6076a499c9bec7199d9f160b5a4ee113aae3",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "8": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "2c09a71ba2b0087f5f2aaa1388e24f647d743f303a325a92a7f6480e58490adc",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        }
      },
      "scores": [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        0
      ],
      "task_id": "r17-b1-agj-p4"
    },
    {
      "family": "formula_materialization",
      "pools": {
        "1": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "dc1c7c446b51329cdd1a443c1cfea3214a235885b9c8bd6ea45be77ad8c53f01",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "2": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "e872e293a64c68c4cacd4842ce22c64ad14c7aeeb628ab27e5bacd51ab7ac30d",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "4": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "fac7963d9eaee39fa72b4199ef563c79bc9be83a629b3d1b35bbf1c0b7289d9a",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "8": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "41a1682b4549606d20d29e83975b33e2e3055f60117efc7b337d0829e317741d",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        }
      },
      "scores": [
        1,
        1,
        1,
        0,
        0,
        1,
        1,
        1
      ],
      "task_id": "r17-b1-fmv-p4"
    },
    {
      "family": "formula_materialization",
      "pools": {
        "1": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "efa863de4e0b25add7a047cc6dcf687ee7808a7ad5f67b96d21adc3ac4259ad0",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "2": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "6ab486271c1d209f5972cb25e1e329c5c0efde5e656b98269e9f708de9a9cc98",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "4": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "dc65671a66974be7cc2fc0c345dd59374e5e28af6c257d54fbc90d85b88b3b08",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "8": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "d8ae6396f1023d163883003da3f0702e331017818c873c57533bdf5a66f4c48f",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        }
      },
      "scores": [
        1,
        1,
        0,
        0,
        1,
        1,
        0,
        1
      ],
      "task_id": "r17-b1-fmv-p8"
    },
    {
      "family": "input_output_contract",
      "pools": {
        "1": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "87c2f0374de011fd25d0609d77142fe91eba6f99ececa815add9c5c7e731702a",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "2": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "63ba2b79a524b62a3874bcdd87a3e1a168f5b2d54c196b7271aa1c14edbfe15c",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "4": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "864fac732cb583379a809d0875f4b09ad909ae017a9a6281c6b392b5780e5565",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "8": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "7218b73fc571d36f1620bf3a99ac1056f856f51b6952274b8fe4707cbc86b28c",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        }
      },
      "scores": [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1
      ],
      "task_id": "r17-b1-ioc-p5"
    },
    {
      "family": "input_output_contract",
      "pools": {
        "1": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "4c70e7db19034630f7c3fe3b7364b7f7ce8b00dff97cf0e34ddc47a3829d052f",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "2": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "1729d5fdf2c44bc123eb28c63a09e937e1ffa7829d5caaad02b1d440fad1cf66",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "4": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "52ee12139655263543742d80bd47527830d8dda8d59f2e45bc73c9aaaf4e51d5",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "8": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "c416114a426f4dc8807c00dfddebe685f69d02d4f2311817d3e60aa0276bb267",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        }
      },
      "scores": [
        1,
        0,
        1,
        1,
        1,
        1,
        0,
        1
      ],
      "task_id": "r17-b1-ioc-p2"
    },
    {
      "family": "multi_step_pipeline",
      "pools": {
        "1": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "684a5a819f40351b7f8787a8210145b8000155bbd1df02d67986f9d8def62f4e",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "2": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "c32fc9f21ac5479c419be487a8912a83085e1bd15c34e20be3c67dcd311ce855",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "4": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "131120cb9e691d6c3322c1535582757c515a119725a98f026ff65c625c87c72e",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "8": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "6fb44f9d5b16031941cbd5500fe57e1629774e445202a25944b27f416a5dca72",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        }
      },
      "scores": [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1
      ],
      "task_id": "r17-b1-msp-p2"
    },
    {
      "family": "multi_step_pipeline",
      "pools": {
        "1": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "e8e53256d036fec078b9d1c642a66f6bb4b297b3b1b23186d9ae9d88da5b9f64",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "2": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "4d9107d3a215b227b8ada02651698a72a47a61ef40c83c09ef900f16444e0425",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "4": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "d57d90e5c59baf97192df2e327e8b63997bf8fad98fdbac10a468fd129f4c69f",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "8": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "4d714c6d20dd831d68f216a8a694b179eab2396a709795edeb5aa5661820cf6f",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        }
      },
      "scores": [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1
      ],
      "task_id": "r17-b1-msp-p0"
    },
    {
      "family": "schema_key_alignment",
      "pools": {
        "1": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "7a6486c51e8ac19b4a148e412f792beb9c40a33b13080e047daaee86d9ad8bde",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "2": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "ef701dc35b1f74e4462febdb95b3bbdf558c14bed3119df2e0fa4a1b6252b5bf",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "4": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "077c39ede802a78096f27588eed48073edb097b0ce44d44a9095956520aa4be9",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "8": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "8d6fcbb1c11a0ed601aa297030b69bbd00ce858bfeac3e394f9c331adc49a2cf",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        }
      },
      "scores": [
        1,
        1,
        0,
        1,
        1,
        0,
        0,
        1
      ],
      "task_id": "r17-b1-ska-p0"
    },
    {
      "family": "schema_key_alignment",
      "pools": {
        "1": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "72cf681ce7eed0d58ae8979d4ba32a25478cf60d3731ffba3bbb59c75969619f",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "2": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "6d19a0a7465cd894760261f183f28b79feb8bb7f7bfc6d4415c6993fc20c4b3b",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "4": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "786a983454c5d7536d7c8f9934a9587f9c9bf45b7a9e448f2a29420a9779f5e4",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "8": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "c8503e970c09ea72028f9dbc43eb05bba449268250b122221c5637593c61a493",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        }
      },
      "scores": [
        1,
        1,
        1,
        1,
        1,
        0,
        1,
        1
      ],
      "task_id": "r17-b1-ska-p4"
    },
    {
      "family": "target_sheet_range",
      "pools": {
        "1": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "45884741a63288990fffc9c97ed8b1e409d3a02517a1db04fcee125a6e37c53a",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "2": {
          "acting_success": 1,
          "mixed": false,
          "pool_id": "c4016284172ee1cf4a392adee02ed493ed467cf84a4f35e72311e57b7f17b7d1",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "4": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "6301491900cdea3adbb8d10244a8d1f5ceabed6044ee15b50b1dc2896031d747",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        },
        "8": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "88bc5cd529c8352270a63efe9015958053d51a353d1672e2242baf33789c20e5",
          "precommitted_success": 1,
          "rescue": false,
          "winner_index": 0
        }
      },
      "scores": [
        1,
        1,
        0,
        1,
        1,
        1,
        1,
        1
      ],
      "task_id": "r17-b1-tsr-p8"
    },
    {
      "family": "target_sheet_range",
      "pools": {
        "1": {
          "acting_success": 0,
          "mixed": false,
          "pool_id": "ffa294d3dd073fd9ef7b9b09f4919a32aba6225518e8f76191be3938637eed1c",
          "precommitted_success": 0,
          "rescue": false,
          "winner_index": 0
        },
        "2": {
          "acting_success": 0,
          "mixed": false,
          "pool_id": "c2b731a7717ede46aa20a62cf528228ae4e8e279c8f7a4de5c35192069904af1",
          "precommitted_success": 0,
          "rescue": false,
          "winner_index": 0
        },
        "4": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "97ce5a2da79a9aa41c7e9f501d10486d05022d11078c8f27768b1456e7832930",
          "precommitted_success": 0,
          "rescue": true,
          "winner_index": 2
        },
        "8": {
          "acting_success": 1,
          "mixed": true,
          "pool_id": "49c28d82e403f67ffa62bca7cfab8be12d4229ce84018c3e878040a198aaf01b",
          "precommitted_success": 0,
          "rescue": true,
          "winner_index": 2
        }
      },
      "scores": [
        0,
        0,
        1,
        1,
        1,
        1,
        0,
        1
      ],
      "task_id": "r17-b1-tsr-p7"
    }
  ]
}


===== BOUND ARTIFACT: generated/e2-r17-e0-go-hold-stop-20260828.json =====
{
  "artifact_type": "e2-r17-e0-go-hold-stop",
  "schema_version": "1.0",
  "created_at_utc": "2026-08-28T07:17:33.012687+00:00",
  "analysis_path": "generated/e2-r17-e0-analysis-20260828.json",
  "source_summary_sha256": "533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366",
  "frozen_contract_sha256": "f4019646b653f41abe056fdd7b746ff6cb4749ce4d2771c2ef90af6845631508",
  "decision": "HOLD",
  "mechanism_signal": "NONZERO",
  "E1_support_gate": {
    "required": {
      "rescue_tasks": 6,
      "failure_families": 3
    },
    "observed": {
      "rescue_tasks": 1,
      "failure_families": 1
    },
    "pass": false
  },
  "reason": "Nonzero rescue/censoring signal is present, but the frozen E1 support threshold is not met.",
  "forbidden_while_hold": [
    "launch E1 updater intervention",
    "promote an E1 causal claim",
    "select support tasks by downstream projection outcome",
    "rerun or replace the completed E0-r3 outcome"
  ],
  "allowed_while_hold": [
    "experiment-plan drafting/review",
    "primary-source baseline/model audit",
    "outcome-blind model and baseline runtime qualification",
    "separately reviewed and frozen support-qualification design"
  ],
  "authority": {
    "scientific_experiment_E1": false,
    "paper_promotion": false,
    "submission": false
  }
}


===== BOUND ARTIFACT: generated/e2-r17-f0-r4-frozen-candidate-contract-20260828.json =====
{
  "arms": {
    "duplicated_winner": "winner twice",
    "precommitted_always": "rollout0",
    "rejected_witness": "rollout0 on M, winner otherwise",
    "skillcat_style_contrast": "winner+rollout0 failure on M, duplicate winner otherwise; matched control, not full SkillCAT reproduction",
    "winner_only": "winner",
    "winner_random_nonwinner": "winner + SHA-selected nonwinner"
  },
  "artifact_type": "e2-r17-f0-r4-frozen-candidate-contract",
  "assets": {
    "actor_smoke": {
      "path": "generated/e2-r17-actor-protocol-smoke-20260828.json",
      "sha256": "c6be7877dc63c63ae843490504b6cb333deb07f27f5173fcb8d7a8e11645df79"
    },
    "debate": {
      "path": "generated/e2-r17-search-projection-debate-adjudication-20260827.json",
      "sha256": "f743a97e6436c209bb73cabedb51405c56059688202f94f8fb6465374f544c1f"
    },
    "identity": {
      "path": "generated/e2-r17-current-plan-model-identity-adjudication-20260828.json",
      "sha256": "287fdcc4dc193adfac677f417dd382637e6c4b8fe6134377465e10fd5f4fb30b"
    },
    "pilot": {
      "path": "generated/e2-r17-e0-pilot-manifest-20260828.json",
      "sha256": "e6653ee7cd2d7391b555086adb1a9d2bf660a7df25455f8c0215b35fa85b893f"
    },
    "public_audit": {
      "path": "consultations/e2-r17-public-dataset-and-baseline-audit-20260828.md",
      "sha256": "2e86fbdf8b985e9d710043dfeccf964d8fcc17ee2f90a483e41b745c33a21126"
    },
    "source_audit": {
      "path": "consultations/e2-r17-search-projection-current-source-and-theory-audit-20260827.md",
      "sha256": "e66a400505bc5cb83c3ed1d804f5ab4eb01e5914e840e400a95404bb02d49d45"
    },
    "suite_qualification": {
      "path": "generated/e2-r17-controlled-suite-v2-mindmemos-qualification-20260827.json",
      "sha256": "b4e9a03c3dcb46f9775b3db8852b9e5141023357b37c2ca573e0ee3b8991ae90"
    },
    "updater_qualification": {
      "path": "generated/e2-r17-cloned-state-first-party-updater-qualification-20260828.json",
      "sha256": "e26337e1d5c7839248fb227ce763f35a70e2c10648a4aad496dd43f412fc0af4"
    }
  },
  "authority": {
    "front_end_claim": false,
    "gpu": false,
    "paper_promotion": false,
    "preexecution_review": true,
    "scientific_experiment": false,
    "submission": false
  },
  "branch": "research/e2-r17-compute-shielding-20260825",
  "claim": "A best-of-K serving selector can improve current acting while a tied winner-only logging policy removes a generated and verified failed witness from an external persistent updater; changing only that projection on an identical pool can change future frozen skill.",
  "code": {
    "research_pipeline/e2_r17_actor_pool.py": "386144c61bab17326d9f1a09d1cb0f926cef26295eb3f6c402038c519cac14db",
    "research_pipeline/e2_r17_ark_plan_react.py": "17c735e24ddf5c089240d6b4083cf00dc12154191b13c0def48a8a9def60e1e0",
    "research_pipeline/e2_r17_mindmemos_ark_adapter.py": "3670b8aa3c96ff3cd5dc2474312346f05aaeedeb2f6ca587bfcbcc99c9250992",
    "research_pipeline/e2_r17_mindmemos_updater.py": "323ada88c837c2e57b6f71aa4cf6a17b1ae1f01b278a7eb0c19bee8c702be004",
    "research_pipeline/e2_r17_search_projection_runner.py": "5cd5caf1b382a2378959ccbcdab8965e67f6b596033cb2a9a00bbe565ccaed4f",
    "research_pipeline/e2_r17_search_projection_theory.py": "8ec701b2059eb7ae7d8c1eac1394cd0ab78100916934370b227ca08bec3fbf06",
    "scripts/freeze_e2_r17_e0_pilot_manifest.py": "1d0de766571141b3783039f359478c0cde681c27d1cfb34b1b8fabbe6b08f92b",
    "scripts/run_e2_r17_actor_pool.py": "e5c504b016b98a5ccd4f7d40b56e307b6810c6cc6a0bff3dee64a0fd6c7f6706",
    "scripts/run_e2_r17_cloned_state_updates.py": "37818964d14bba27d3a7b61d0593e8f56377ee9d344e5bef67570feb850491cd"
  },
  "created_at_utc": "2026-08-28T03:41:27+00:00",
  "data": {
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
    "development_never_promoted": true,
    "e0_all_count": 54,
    "e0_pilot": [
      "r17-b1-agj-p1",
      "r17-b1-agj-p4",
      "r17-b1-fmv-p4",
      "r17-b1-fmv-p8",
      "r17-b1-ioc-p5",
      "r17-b1-ioc-p2",
      "r17-b1-msp-p2",
      "r17-b1-msp-p0",
      "r17-b1-ska-p0",
      "r17-b1-ska-p4",
      "r17-b1-tsr-p8",
      "r17-b1-tsr-p7"
    ],
    "e1_probes": [
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
    "e1_streams": {
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
    "integrity_reserve": [
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
    "metadata": {
      "path": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2/r17_controlled_metadata.json",
      "sha256": "12d6eb876e2a230e7990be3e61fed108d45f6ddec00bac5c9b88585a04111b04"
    },
    "public": {
      "archive_sha256": "10ef893dd29cb13ab97143ea787e68cdc9574a13873ab9a54e50b31dc03fc949",
      "audit": {
        "path": "consultations/e2-r17-public-dataset-and-baseline-audit-20260828.md",
        "sha256": "2e86fbdf8b985e9d710043dfeccf964d8fcc17ee2f90a483e41b745c33a21126"
      },
      "dataset_sha256": "bcecaa89a005bd4e3bbe98da150a86e8062c27f262e575d5e47bd9861b3525e7",
      "primary": "SpreadsheetBench Verified-400",
      "secondary": "SpreadsheetBench 2 only after controlled+Verified GO"
    },
    "split": {
      "path": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2/r17_split_manifest.json",
      "sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9"
    },
    "suite": {
      "path": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2/suite_manifest.json",
      "sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4"
    },
    "suite_root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2"
  },
  "execution": {
    "forbidden": [
      "task replacement",
      "dev promotion",
      "taxonomy/threshold retuning",
      "benchmark shopping",
      "/api/v3",
      "credential/raw response-id logging"
    ],
    "no_gpu_required": true,
    "pilot_first": true,
    "raw_assets": [
      "provider JSON",
      "trajectory JSONL/JSON",
      "pool+projection hashes",
      "skill pre/post hashes",
      "verifier",
      "token ledger",
      "CSV summary",
      "integrity receipt",
      "belief update"
    ],
    "resume_missing_only": true,
    "server": "69"
  },
  "gates": {
    "Identification_GO": [
      "E0 and E1 support pass",
      "provenance pass",
      "mean RW-WIN>0",
      "one-sided p<=0.05",
      "95% CI lower>0",
      "duplicated winner does not reproduce gain"
    ],
    "STOP": [
      "projection null/negative",
      "duplicated-winner equivalence",
      "post-outcome selection required",
      "insufficient frozen rescue support",
      "any cloned invariant fails"
    ],
    "downgrade": [
      "random nonwinner matches RW => generic diversity",
      "SkillCAT-style dominates => keep prior method",
      "RW sufficient => delete CADP"
    ],
    "paper": "Identification+Prediction+longitudinal Closure required; E1 alone is insufficient"
  },
  "graph": {
    "act": "tau+=a(T_K)",
    "endpoint": "J(S') at common frozen K=1",
    "learn": "E=g(T_K)",
    "search": "T_K~Q_K(.|x,S)",
    "update": "S'=U(S,E)"
  },
  "head_before_contract": "b8162c84be2edb736fe685088e20b1f94d1c91db",
  "invariants": [
    "same task/input/prompt/initial-skill/verifier/requested+resolved actor model within pool",
    "same exact K=8 pool and served winner across cloned arms",
    "selector=max binary score then lowest rollout index",
    "Rejected-Witness=rollout0 on M and winner outside M",
    "same MindMemOS updater/model/batch/evaluation probes across arms",
    "one add-record per task and same top-level acting-winner score; only evidence packet differs",
    "scientific unit is independently evolved eight-task stream-state, not rollout/probe"
  ],
  "models": {
    "actor_updater": {
      "requested": "deepseek-v4-pro",
      "resolved": "deepseek-v4-pro-ga-260813"
    },
    "drift": "stop tranche on any resolved-id change",
    "reviewers": {
      "deepseek": "deepseek-v4-pro-ga-260813",
      "kimi": "kimi-k3"
    }
  },
  "next": "independent DeepSeek and Kimi reviews bound to exact contract SHA",
  "not_claimed": [
    "more compute inherently harms learning",
    "failure utility is novel",
    "success/failure contrast is novel",
    "first divergence is novel",
    "validation-gated editing is novel",
    "CADP is novel"
  ],
  "prerequisite_checks": {
    "debate": true,
    "identity": true,
    "mindmemos": true,
    "pilot": true,
    "smoke": true,
    "split": true,
    "suite": true,
    "suite_hash": true,
    "updater": true
  },
  "r16": {
    "mutated": false,
    "preserve": true,
    "superseded": false
  },
  "review_questions": [
    "identifiable under provider stochasticity?",
    "support gates non-selective?",
    "evidence packet only treatment?",
    "controls separate tokens/diversity?",
    "n=12 statistics adequate?",
    "closest-work reduction?"
  ],
  "route": {
    "base_url": "https://ark.cn-beijing.volces.com/api/plan/v3",
    "config_default": "ark-code-latest",
    "forbidden": "https://ark.cn-beijing.volces.com/api/v3",
    "retry": 0,
    "temperature": 0,
    "thinking": "disabled"
  },
  "schema_version": "1.0",
  "scientific_object": "SERVING_INDUCED_OBSERVATION_KERNEL_FOR_PERSISTENT_SKILL_LEARNING",
  "search": {
    "actor_max_output_tokens": 4096,
    "actor_max_turns": 10,
    "generate_once_k": 8,
    "nested_prefixes": [
      1,
      2,
      4,
      8
    ],
    "random_nonwinner_salt": "e2-r17-r4-random-nonwinner-v1",
    "topology": "parallel_best_of_k"
  },
  "stages": {
    "E0_full": {
      "E1_support": "at least 6 rescue tasks and >=3 families; otherwise HOLD/STOP before updater",
      "tasks": 54
    },
    "E0_pilot": {
      "run": "K8 then derive prefixes",
      "stop": "zero rescue events or protocol failure; otherwise predeclared extension allowed",
      "tasks": 12
    },
    "E1_eval": {
      "K": 1,
      "endpoint": "mean success across common probes",
      "probes_per_state": 18
    },
    "E1_pool_freeze": {
      "pools": 96,
      "streams": 12,
      "support": "at least 8 rescue task-packets and >=6 streams exposed; drop no stream; pass all or stop",
      "tasks_per_stream": 8
    },
    "E1_update": {
      "arm_order": "SHA256(E2-R17-F0-R4-CLONED-ARM-ORDER-v1|stream|arm)",
      "arms": 6,
      "post_versions": "one content-addressed version per stream-arm"
    },
    "later_only_on_GO": [
      "prospective prediction",
      "multi-round evolution",
      "Verified-400",
      "topology x projection",
      "SpreadsheetBench 2"
    ]
  },
  "statistics": {
    "ci": "95% percentile bootstrap over streams, 10000 draws",
    "controls": [
      "RW-DUP",
      "RW-random-nonwinner",
      "SkillCAT-style-WIN",
      "PRE-WIN",
      "Delta versus rescue count"
    ],
    "no_pseudoreplication": true,
    "primary": "Delta_s=J_s(rejected_witness)-J_s(winner_only)",
    "summary": "mean Delta_s",
    "test": "exact one-sided 2^12 sign-flip",
    "unit": "12 independently evolved stream-states"
  },
  "status": "CANDIDATE_REQUIRES_DUAL_PREEXECUTION_REVIEW",
  "substrate": {
    "batch_tasks": 8,
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "config": {
      "max_aggregate": 8,
      "max_parse_attempts": 1,
      "min_aggregate": 8,
      "rewrite_skill": false,
      "slot_char_budget": 6000,
      "summary_concurrency": 4,
      "transcript_max_chars": 16000,
      "use_trajectory_score": true
    },
    "initial_skill": {
      "path": "/data/wyt/evidence-substrates/MindMemOS-20260817/resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md",
      "sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb"
    },
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817",
    "updater": "mindmemos.pipelines.skill.evolution.SkillEvolver"
  },
  "theory": {
    "Gamma": "P(M)",
    "M": "Y_0=0 and max_i Y_i=1",
    "Y": "binary deterministic verifier",
    "families": "mutually exclusive primary_failure_family; overlapping post-hoc tags forbidden",
    "gated_effect": "g_RW=g_WIN outside M, hence E[D]=Gamma*E[D|M]",
    "identity": "A_K-A_1=V_pre-V_win=Gamma_K(Q), arbitrary rollout dependence",
    "iid_reference": "Gamma_K(p)=(1-p)-(1-p)^K; p*=1-K^(-1/(K-1))",
    "role": "measurement structure; novelty requires prospective prediction and causal intervention"
  },
  "working_title": "When Better Search Teaches Less: Serving-Induced Observation Kernels in Self-Evolving Agents"
}


===== BOUND ARTIFACT: consultations/e2-r17-public-dataset-and-baseline-audit-20260828.md =====
# E2-R17 public-dataset and baseline audit

Date: 2026-08-28  
Status: PRE-OUTCOME / ZERO SCIENTIFIC AUTHORITY  
Branch: `research/e2-r17-compute-shielding-20260825`  
Purpose: freeze which datasets and baselines can test the serving-induced observation-kernel claim without turning the paper into a benchmark or method zoo.

## 1. Decision

E2-R17 will use a three-layer evidence design:

1. **Controlled Spreadsheet Suite V2** — mechanism identification only. This is a locally generated, SpreadsheetBench-compatible suite with deterministic validators and preregistered reusable failure families. It must never be described as a public benchmark.
2. **SpreadsheetBench Verified-400** — primary public realistic externality and longitudinal validation, after the exact-same-pool cloned-state mechanism passes on the controlled suite.
3. **SpreadsheetBench 2** — late workflow-level transfer only, after the mechanism and the public V1 result pass. It cannot be introduced to rescue a negative result.

The strongest direct method baseline is **SkillCAT-style same-task success/failure contrast**. The strongest feedback-dynamics baselines are the **Normal / Fail-only / Success-only** conditions from *Rethinking Self-Evolving Agent Skills*. The E1 identification experiment additionally requires projection-specific controls that are not optional method baselines: winner-only, precommitted rollout-0, Rejected-Witness, duplicated winner, and random nonwinner.

## 2. Dataset audit

### 2.1 Controlled Spreadsheet Suite V2

Role: causal identification, law qualification, prospective family prediction.

Frozen local substrate:

- root: `/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2`
- total tasks: 378
- deterministic failure families: 6
  - input/output contract
  - target sheet/range
  - schema/key alignment
  - aggregation/join
  - formula/materialization
  - multi-step pipeline
- suite manifest SHA-256: `2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4`
- split manifest SHA-256: `aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9`
- qualification: 378/378 golden self-check PASS and 378/378 initialized negative-control PASS
- public status: **not public; do not use for external benchmark claims**

Why it is required: the central estimand changes only the learning projection on an identical generated search pool. A public benchmark alone cannot guarantee enough mixed success/failure pools, a disjoint pre-outcome failure-family partition, or deterministic family-level interventions.

### 2.2 SpreadsheetBench Verified-400

Primary sources:

- SpreadsheetBench official repository, NeurIPS 2024 Datasets and Benchmarks track.
- SpreadsheetBench Verified release announcement from the original benchmark collaboration.

Source-supported facts:

- SpreadsheetBench contains 912 real-world spreadsheet questions and 2,729 test cases, with OJ-style evaluation over multiple workbooks per instruction.
- In December 2025 the project released SpreadsheetBench Verified, an expert-annotated 400-instance subset intended to improve automated evaluation reliability.
- The benchmark supports multi-round ReAct plus code-execution feedback, matching the first-party MindMemOS spreadsheet-agent setting more closely than a static formula benchmark.

Frozen local copy:

- archive: `/data/wyt/e2-r17-compute-shielding/SpreadsheetBench/spreadsheetbench_verified_400.tar.gz`
- archive SHA-256: `10ef893dd29cb13ab97143ea787e68cdc9574a13873ab9a54e50b31dc03fc949`
- dataset JSON SHA-256: `bcecaa89a005bd4e3bbe98da150a86e8062c27f262e575d5e47bd9861b3525e7`
- rows: 400
- workbook members: 800 `.xlsx` files
- metadata fields: `id`, `instruction`, `spreadsheet_path`, `instruction_type`, `answer_position`, `answer_sheet`, `data_position`

Role in E2-R17:

- public test of whether the controlled same-pool mechanism transports to real forum-derived tasks;
- public multi-round comparison of online acting performance and frozen persistent-skill performance;
- source-faithful SkillCAT-style contrast and RethinkSkill feedback-view baselines;
- never used to tune the controlled-suite family taxonomy, witness rule, score threshold, or STOP condition.

Required public protocol:

- publish exact evolution/validation/test IDs;
- bind the official evaluator and workbook archive hashes;
- rerun no-skill and initial-skill baselines under the exact same actor, model identity, prompt, turn limit, formula-recalculation policy, and evaluator;
- do not import scores from papers whose split or harness differs;
- keep development IDs permanently excluded from confirmatory promotion;
- classify public tasks only with a pre-outcome metadata/instruction rule, never by observed model failure.

### 2.3 SpreadsheetBench 2

Primary sources:

- official SpreadsheetBench 2 repository and project page, released in 2026;
- the official project describes 321 end-to-end workflow tasks across financial modeling/template, debugging, and visualization, with complex multi-sheet workbooks and deliverable-level evaluation.

Role in E2-R17:

- late externality test of the already-frozen observation-kernel prediction on workflow-level tasks;
- primary deterministic categories: Debugging, Financial Model, and Template;
- Visualization is secondary because it introduces a VLM checklist evaluator and a Windows COM rendering dependency, which confounds the first mechanism test.

Entry condition:

- exact-same-pool E1 passes;
- prospective sign/rank prediction passes;
- Verified-400 public result passes its preregistered criterion;
- the SpreadsheetBench 2 subset and evaluation policy are frozen before any model outcomes are inspected.

STOP discipline: a negative Verified-400 result is not a reason to open SpreadsheetBench 2. That would be benchmark shopping.

## 3. Baseline and control audit

### 3.1 Mandatory E1 causal controls

| Arm | What the updater sees | Scientific purpose |
|---|---|---|
| Winner-only | served winner | current tied acting/learning default |
| Precommitted rollout-0 | rollout 0 from the exact same pool | alternative fixed observation kernel; not a no-censoring oracle |
| Rejected-Witness | winner outside rescue; preregistered failed witness on rescue | minimal causal repair naturally implied by the mechanism |
| Duplicated winner | winner twice under matched packet structure | token/context-length control |
| Random nonwinner | winner plus deterministic hash-selected nonwinner | generic diversity control |
| SkillCAT-style contrast | same-task winner/failure contrast | strongest direct method-reduction baseline |

All arms must preserve:

- identical task;
- identical initial skill SHA;
- identical K=8 search pool and served winner;
- identical actor, verifier, updater implementation, updater model, update batch size, and evaluation probes;
- one task-level add-record per pool and identical top-level acting score;
- only the embedded evidence packet may differ.

### 3.2 Mandatory longitudinal feedback baselines

Source-faithful baselines from *Rethinking Self-Evolving Agent Skills*:

- Normal: successful and failed trajectories;
- Fail-only;
- Success-only;
- initial/no-evolution skill;
- test-time parallel sampling and sequential refinement as acting-compute controls where budget matching is possible.

These baselines test feedback dynamics, but they do not replace the exact-same-pool E1 intervention. They change the available feedback set across rounds rather than isolating the serving-induced projection on the same pool.

### 3.3 Closest-work reduction boundary

**SkillCAT** already performs multi-seed same-task success/failure pairing, divergence extraction, source-task replay validation, and persistent skill evolution on SpreadsheetBench. Therefore E2-R17 cannot claim novelty for any of those components. SkillCAT-style contrast is mandatory, and a source-faithful implementation must be reported separately from the minimal Rejected-Witness projection.

**Rethinking Self-Evolving Agent Skills** already shows that feedback composition matters over multiple rounds and that selected evolved skills depend on failed trajectories. Therefore E2-R17 cannot claim that “failures help skill learning” or that persistent evolution differs from test-time scaling. The residual causal claim is narrower: a serving selector changes the observation kernel of the updater by hiding a generated and verifiable failed witness.

**SkillOpt / related skill-optimization systems** already use bounded edits and held-out validation. Validation-gated text editing is substrate machinery, not a contribution.

**Selective labels, performative prediction, and DAgger** are conceptual reductions. E2-R17 must present itself as a specialized causal mechanism in a generated search set with fully observed but selectively logged candidate trajectories, not as a new general theory of selective data.

## 4. Frozen experiment sequence

1. E0 pilot on a predeclared family-balanced subset of the controlled calibration lane.
2. E0 full nested K=1/2/4/8 pool-law qualification.
3. E1 exact-same-pool cloned-state intervention, one independently evolved eight-task stream as the scientific unit.
4. Common K=1 held-out probe evaluation, identical across arms.
5. Prospective family/regime prediction on unseen controlled streams.
6. Only after GO: multi-round controlled evolution.
7. Only after GO: Verified-400 public validation and source-faithful baselines.
8. Only after public GO: SpreadsheetBench 2 workflow transfer.

## 5. No-benchmark-shopping rules

- No task may move from development to confirmation.
- Integrity reserves replace files only after a pre-execution integrity failure; they never replace a bad model outcome.
- No failure-family definition may be changed after actor outcomes are visible.
- No public split may be changed after any public result is visible.
- No second benchmark may be opened to rescue a failed central mechanism.
- No paper claim may cite controlled-suite performance as public external validity.
- No published baseline score may be copied without an exact-harness rerun; benchmark version, split, prompting, evaluator, and formula-recalculation differences can dominate reported gains.

## 6. Current decision

`PUBLIC_DATASET_AND_BASELINE_PLAN_PASS_FOR_PREEXECUTION_REVIEW`

This audit authorizes incorporation into the F0-R4 candidate contract. It does not authorize scientific calls, GPU use, paper promotion, manuscript claims, front-end claims, or submission.

## 7. Primary-source registry

- SpreadsheetBench: Ma et al., NeurIPS 2024 Datasets and Benchmarks, arXiv:2406.14991; official repository `RUCKBReasoning/SpreadsheetBench`.
- SpreadsheetBench Verified: official repository release notice and the original-team collaboration announcement dated 2025-12-02.
- SpreadsheetBench 2: official repository `RUCKBReasoning/SpreadsheetBench-2` and project page, released in 2026.
- SkillCAT: Chen et al., arXiv:2606.13317v2.
- Rethinking Self-Evolving Agent Skills: Liu et al., arXiv:2608.02636.


===== BOUND ARTIFACT: generated/e2-r17-experiment-plan-v1-model-identity-qualification-20260828.json =====
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
  "compatibility_parent": {
    "path": "generated/e2-r17-experiment-plan-v1-20260828.json",
    "separate_generation_calls_declared": true,
    "sha256": "928ae3e9eac9259dba47d08cca3d91309f2bedb4692d597b89806f0313625549"
  },
  "created_at_utc": "2026-08-28T07:28:28+00:00",
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
      "max_output_tokens": 128,
      "poll_count": 0,
      "prompt_sha256": "7bfaf5897d7bbd7f972a67554ee32acc828cd8309e40822dfc05217e987776bf",
      "provider_generation_attempts": 1,
      "provider_retry_limit": 0,
      "provider_status": "completed",
      "raw_text": "PLAN_OK",
      "raw_text_sha256": "aa6b4c1b97751f326153c1927c1106bf5a927ec506a8066dfe0dded595992d7c",
      "requested_model": "deepseek-v4-pro",
      "resolved_model": "deepseek-v4-pro-ga-260813",
      "response_id_sha256": "5288cc3186d3577b04e04da63d346dac36ca9166d70a9a3942ba6bb6504ac870",
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
      "max_output_tokens": 128,
      "poll_count": 0,
      "prompt_sha256": "7bfaf5897d7bbd7f972a67554ee32acc828cd8309e40822dfc05217e987776bf",
      "provider_generation_attempts": 1,
      "provider_retry_limit": 0,
      "provider_status": "completed",
      "raw_text": "PLAN_OK",
      "raw_text_sha256": "aa6b4c1b97751f326153c1927c1106bf5a927ec506a8066dfe0dded595992d7c",
      "requested_model": "kimi-k3",
      "resolved_model": "kimi-k3",
      "response_id_sha256": "3e7d9d1e1f25cc70a2ec5dc95bc13bbecfeb0e2e2cd129f7519db178214d793e",
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


BOUND DOSSIER END
