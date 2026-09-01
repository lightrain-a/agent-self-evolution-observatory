You are an independent final pre-Pilot design reviewer for E2-R17 / Compute Shielding. You are blind to the other reviewer. This consultation has zero scientific-experiment, GPU, paper-promotion, frontend, or submission authority.

Requested reviewer endpoint: deepseek-v4-pro
Exact Experiment Plan V3 SHA-256: b1a0224117f161ead9fccefa2c22a0f01dfa1d9e72ca1e98107418f21e3e04c5

V2 was independently reviewed by DeepSeek and Kimi and both returned REVISE before Pilot. V3 claims to repair the verdict-changing issues before any E1 updater outcome. Audit the actual bound artifacts and code, not the authors' assertion that they are fixed.

Published novelty threat: ReasoningBank/MaTTS (ICLR 2026) already learns memory from successful and failed trajectories generated with test-time scaling. E2-R17 survives only if exact-same-pool projection censoring and its causal/regime consequences are genuinely more specific than that known result.

The proposed V3 chain is:
1. theory distinguishes rescue censoring from mixed-pool treatment support;
2. E1-A freezes 96 exact K=8 pools before any updater call;
3. hard support gate is >=24/96 mixed AND >=8/12 streams with >=2 mixed each, with no waivers/replacement;
4. family coverage is now a separate generalization qualification, not a pooled-identifiability requirement;
5. WIN/MRW source evidence is token matched with a frozen tiktoken==0.11.0 cl100k_base renderer, cap 3072, pair budget=min(cap,left,right), 1/3 head + 2/3 tail;
6. WIN-A vs byte-identical WIN-B is an updater stochasticity negative control; unspecified first-party updater temperature is forced to 0.0;
7. MRW vs WIN-A is primary; ReasoningBank-style same-pool aggregation is a predeclared secondary collision arm that runs regardless of MRW GO/HOLD after semantic Pilot;
8. equivalence uses paired TOST alpha=.05 and +/-1/18 margin; nonsignificant superiority without equivalence is HOLD, not STOP;
9. source-faithful baseline reproduction and unified rerun stay separate;
10. this review can at most permit an outcome-blind runtime/mechanical Pilot. It cannot authorize E1-A pool generation or E1-B updater outcomes.

Audit these exact questions:
- Did V3 fully repair the V2 >=1-vs->=2 stream inconsistency, and are all support thresholds hard/non-waivable before outcomes?
- Is separating >=4/6 family coverage from pooled identifiability scientifically correct?
- Does the frozen matched-window renderer eliminate the evidence-length confound without creating a new arm-specific budget advantage? Is fixing the dependency/version before Pilot sufficient?
- Is the 1/3 head + 2/3 tail rule acceptable as a precommitted renderer, or is there a P0 semantic problem that makes the primary treatment uninterpretable?
- Does WIN-A/WIN-B plus forced temperature=0 adequately handle hosted-updater stochasticity? Is the equivalence gate operational?
- Are paired TOST, exact 2^12 sign-flip, paired bootstrap, n=12 unit definition, and explicit d~0.766 power limitation coherent?
- Does the always-predeclared RB-AGG collision arm prevent the simple claim from collapsing into ReasoningBank? Is labeling it 'ReasoningBank-style' rather than source-faithful correct?
- Is the interpretation table safe against post-hoc story rescue if MRW is null but RB-AGG is positive?
- Is the two-lane published-baseline design honest under the current credential blocker?
- Are WebArena/AppWorld deferred until E1 GO and are source-faithful scores prohibited from entering unified rankings?
- Does V3 prevent an E1-only result from being promoted into a prospective compute-shielding regime law before E3?
- Is the proposed runtime Pilot genuinely outcome-blind and mechanical? Name any specific check that would leak scientific effectiveness into method/model selection.
- Are SHA revalidation, missing-unit resume, retry=0, and pre-Full budget measurement sufficient?

Return exactly one JSON object and no markdown using this schema:
{
  "plan_sha256_acknowledged": "",
  "verdict": "PASS_TO_OUTCOME_BLIND_RUNTIME_PILOT|REVISE_V3_BEFORE_PILOT|STOP_PROGRAM",
  "v2_p0_repairs_complete": false,
  "mixed_support_gate_assessment": "",
  "matched_window_renderer_assessment": "",
  "updater_stochasticity_control_assessment": "",
  "primary_statistics_and_power_assessment": "",
  "reasoningbank_collision_assessment": "",
  "published_baseline_and_two_lane_assessment": "",
  "claim_scope_assessment": "",
  "runtime_pilot_scope_assessment": "",
  "checkpoint_and_budget_assessment": "",
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
  "runtime_pilot_recommendation": "ALLOW_OUTCOME_BLIND_RUNTIME_PILOT|HOLD|STOP",
  "e1_a_recommendation": "HOLD_UNTIL_SEPARATE_IMMUTABLE_CONTRACT|STOP",
  "e1_b_recommendation": "HOLD_UNTIL_SUPPORT_GATE_AND_SEPARATE_CONTRACT|STOP",
  "paper_claim_authority": false,
  "single_sentence_verdict": ""
}

Set plan_sha256_acknowledged exactly to the SHA above. Keep paper_claim_authority false. A PASS only means a separate zero-effect-selection runtime Pilot may be contracted; E1-A and E1-B remain HOLD pending their own contracts.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START

===== BOUND ARTIFACT: generated/e2-r17-experiment-plan-v3-20260828.json =====
{
  "artifact_type": "e2-r17-experiment-plan-v3",
  "schema_version": "1.0",
  "date": "2026-08-28",
  "status": "V3_DUAL_REVIEW_REQUIRED_BEFORE_RUNTIME_PILOT",
  "scientific_authority": false,
  "supersedes_for_future_execution": "e2-r17-experiment-plan-v2",
  "preserves_history": true,
  "central_question": "Does best-of-K acting selection change the updater-visible evidence distribution on an exact frozen search pool so that winner-only learning is suboptimal for future frozen skill?",
  "novelty_boundary": {
    "published_collision": "ReasoningBank/MaTTS (ICLR 2026)",
    "cannot_claim": [
      "failed trajectories can improve memory",
      "successful and failed trajectories can be aggregated for learning",
      "test-time scaling creates additional learning signal",
      "memory and test-time scaling can be combined"
    ],
    "candidate_claims": [
      "exact same-pool separation of acting projection and learning projection",
      "compute-shielding evidence law as K changes",
      "budget-matched causal learning-projection intervention",
      "prospective regime prediction before confirmatory outcomes"
    ],
    "abstract_regime_law_requires_e3": true
  },
  "theory": {
    "rescue_identity": "A_K-A_1=P(Y_1=0,max_i Y_i=1)=V_pre(K)-V_winner(K)",
    "iid_rescue_mass": "Gamma_K(p)=(1-p)-(1-p)^K",
    "mixed_support": "M_K=P(any success AND any failure)",
    "iid_mixed_support": "M_K=1-p^K-(1-p)^K",
    "nested_pool_no_iid_monotonicity": {
      "acting_success": "nondecreasing",
      "winner_visible_failure": "nonincreasing",
      "full_pool_failure_availability": "nondecreasing",
      "mixed_pool_support": "nondecreasing"
    },
    "learning_factorization": "Delta_K=M_K*delta_K",
    "delta_positive_assumed": false
  },
  "historical_e0": {
    "summary_sha256": "533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366",
    "historical_decision": "HOLD",
    "rewritten": false,
    "k8": {
      "acting_success": "12/12",
      "mixed_pools": "8/12",
      "rescue_events": "1/12",
      "winner_visible_failures": "0/12",
      "hidden_failed_nonwinners": 16,
      "failure_family_support": "5/6"
    },
    "old_rescue_quota_extension_authorized": false
  },
  "controlled_split": {
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2",
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4",
    "outcome_blind": true,
    "failure_families": 6,
    "streams_per_family": 2,
    "e1_streams": 12,
    "tasks_per_stream": 8,
    "update_tasks": 96,
    "common_heldout_probes": 18
  },
  "e1_a_pool_support": {
    "k": 8,
    "actor_rollouts": 768,
    "updater_calls": 0,
    "freeze_all_96_pools_before_gate": true,
    "hard_gate": {
      "mixed_pool_count_minimum": "24/96",
      "exposed_stream_minimum": "8/12 streams",
      "mixed_pools_per_exposed_stream_minimum": "2/8",
      "protocol_integrity": "100%",
      "completed_unit_sha_revalidation": true,
      "rounding_or_waiver": false,
      "task_or_pool_replacement_after_support": false
    },
    "borderline_examples_are_failures": ["23/96", "7/12 exposed streams", "one mixed pool in an otherwise exposed stream"],
    "family_generalization_qualification": {
      "minimum_supported_families": "4/6",
      "controls_primary_e1_authorization": false,
      "if_failed": "pooled E1 may proceed if hard gate passes, but family-generalization and E3 family-ranking claims are blocked"
    }
  },
  "evidence_renderer": {
    "implementation": "research_pipeline/e2_r17_evidence_window.py",
    "tokenizer_package": "tiktoken",
    "tokenizer_version": "0.11.0",
    "encoding": "cl100k_base",
    "cap_tokens": 3072,
    "canonical_evidence": "non-system user/assistant/tool messages plus verifier score/message; provenance/provider metadata excluded",
    "pair_budget": "min(3072, raw_tokens(WIN), raw_tokens(MRW))",
    "truncation": "first one-third plus final two-thirds tokens",
    "padding": false,
    "exact_pair_token_parity_required": true,
    "dependency_or_version_drift": "FAIL_PILOT",
    "policy_selection_after_pilot": false
  },
  "e1_b_arms": {
    "WIN_A": {
      "role": "primary control",
      "source_trajectories_per_task": 1,
      "projection": "served winner"
    },
    "WIN_B": {
      "role": "identical-treatment updater stochasticity negative control",
      "source_trajectories_per_task": 1,
      "projection": "byte-identical updater input to WIN_A before provider calls"
    },
    "MRW": {
      "role": "primary causal intervention",
      "source_trajectories_per_task": 1,
      "projection": "served winner on nonmixed pool; deterministic lowest-index failed nonwinner on mixed pool",
      "extra_actor_calls": 0
    },
    "RB_AGG": {
      "role": "predeclared ReasoningBank collision diagnostic",
      "runs_regardless_of_mrw_go_hold": true,
      "label": "ReasoningBank-style same-pool aggregation",
      "official_source_faithful_reproduction": false,
      "requires_semantic_runtime_pilot": true
    }
  },
  "updater": {
    "substrate": "MindMemOS SkillEvolver",
    "batch_tasks": 8,
    "provider_retry": 0,
    "thinking": "disabled",
    "default_temperature_if_first_party_omits": 0.0,
    "resolved_model_must_be_requalified_per_execution_tranche": true,
    "parse_corrections": "explicit and counted",
    "historical_receipts_regenerated": false
  },
  "evaluation": {
    "probes_per_stream": 18,
    "k": 1,
    "same_probes_all_arms": true,
    "independent_causal_units": 12,
    "probe_rows_independent_units": false,
    "endpoint": "per-stream mean held-out success"
  },
  "statistics": {
    "equivalence_margin_absolute": "1/18 = 0.0555555556",
    "negative_control_first": {
      "contrast": "WIN_B-WIN_A",
      "test": "paired TOST alpha=0.05",
      "operational_ci": "90% paired-mean t CI entirely within [-1/18,+1/18]",
      "bootstrap_robustness": "90% paired bootstrap",
      "failure": "HOLD_UPDATER_STOCHASTICITY"
    },
    "primary_superiority": {
      "contrast": "MRW-WIN_A",
      "test": "exact one-sided sign-flip over all 4096 within-pair sign assignments",
      "alpha": 0.05,
      "paired_bootstrap": "10000 draws, 95% CI",
      "go": "negative-control equivalence AND mean>0 AND exact p<=0.05 AND bootstrap lower>0 AND integrity pass"
    },
    "qualified_null": {
      "test": "paired TOST alpha=0.05",
      "margin": "+/-1/18",
      "equivalent": "STOP_MRW_PRACTICALLY_NULL",
      "significantly_negative": "STOP_MRW_HARMFUL",
      "neither_superior_nor_equivalent": "HOLD_UNDERPOWERED_OR_HETEROGENEOUS"
    },
    "power_disclosure": {
      "paired_units": 12,
      "one_sided_alpha": 0.05,
      "target_power": 0.8,
      "paired_t_standardized_effect_required_approx": 0.7664,
      "equal_magnitude_sign_reference": "10/12 positive pairs required for one-sided sign probability below .05"
    }
  },
  "collision_interpretation": {
    "MRW_superior_RB_superior": "hidden search evidence has learning consequence; test minimal witness vs richer aggregation practical equivalence",
    "MRW_superior_RB_null": "minimal failed witness specifically useful under this updater; diagnose aggregation dilution",
    "MRW_null_RB_superior": "reject minimal witness as final repair; aggregation-sensitive effect overlaps ReasoningBank more strongly; narrow novelty",
    "MRW_equivalent_RB_equivalent": "central learning-consequence mechanism STOP on this substrate",
    "MRW_negative": "failed-witness repair rejected"
  },
  "published_baselines": {
    "headline": [
      "ReasoningBank/MaTTS — ICLR 2026",
      "PolySkill — ICLR 2026",
      "ACE — ICLR 2026",
      "Agent Workflow Memory — ICML 2025"
    ],
    "extended": ["SAGE — ACL 2026 Long"],
    "arxiv_only_not_headline": ["SkillCAT", "Branch2Skill", "SkillOpt", "RethinkSkill", "TSR"]
  },
  "external_lanes": {
    "source_faithful": {
      "model_substitution_allowed_under_source_faithful_label": false,
      "current_credential_state": "Ark configured; Google/OpenAI/Anthropic/SambaNova not configured on 69",
      "unavailable_at_submission_disclosure": "report unified rerun only and explicitly state source-model route was unavailable; never call it exact reproduction"
    },
    "unified_rerun": {
      "direct_method_ranking_allowed": true,
      "minimum_models_for_cross_model_claim": 2,
      "prefer_minimum_model_families": 2,
      "single_model_fallback": "report single-model result without robustness claim",
      "model_selection_uses_r17_gain": false
    }
  },
  "public_benchmarks_after_e1_go": {
    "primary": "WebArena",
    "secondary": "AppWorld",
    "additional": "SpreadsheetBench Verified-400 if budget permits"
  },
  "later_stages": {
    "e3": "prospective K/family prediction frozen before future outcomes; failure deletes regime-law claims",
    "e4": "multi-round persistent evolution separating online acting from frozen-skill value",
    "e5": "parallel-vs-sequential topology x winner/history-preserving learning"
  },
  "runtime_pilot": {
    "authorized_by_this_plan": false,
    "outcome_blind_effectiveness": true,
    "must_validate": [
      "exact tiktoken dependency and matched-window parity",
      "no system/provenance evidence leakage",
      "MRW changes projection only on mixed pools",
      "WIN_A/WIN_B byte-identical updater input before provider calls",
      "temperature=0/retry=0/thinking disabled receipts",
      "RB_AGG source-pool provenance and evidence accounting",
      "updater calls/tokens/latency/parse corrections for budget only",
      "SHA revalidation and missing-unit resume",
      "no model or method selection from R17 effectiveness"
    ]
  },
  "checkpoint_policy": {
    "immediate_persist": ["rollout", "prefix and K pools", "projection", "matched-window receipt", "updater", "held-out evaluation"],
    "raw_immutable": true,
    "summary_rebuildable": true,
    "resume_rehashes_completed_units": true,
    "sha_mismatch": "QUARANTINE_AND_STOP",
    "missing_unit_resume_only": true,
    "blind_relaunch_after_502_timeout": false
  },
  "budget": {
    "full_scientific_run_authorized": false,
    "known_e1_a_rollouts": 768,
    "must_be_measured_in_runtime_pilot": [
      "actor calls and tokens per rollout",
      "updater calls and tokens per stream/arm",
      "parse-correction rate",
      "held-out evaluation calls/tokens",
      "wall time",
      "hard budget ceiling"
    ]
  },
  "current_state": {
    "theory_tests": "PASS",
    "mixed_projection_tests": "PASS",
    "evidence_renderer_static_tests": "PASS",
    "updater_temperature_default_tests": "PASS",
    "targeted_tests_passed_total_at_v3_write": 29,
    "runtime_pilot": "NOT_AUTHORIZED",
    "e1_a": "NOT_AUTHORIZED",
    "e1_b": "NOT_AUTHORIZED",
    "public_full_runs": "NOT_AUTHORIZED"
  },
  "next_gate": "independent Kimi K3 + DeepSeek V4-Pro review of exact V3 before any outcome-blind runtime Pilot"
}


===== BOUND ARTIFACT: consultations/e2-r17-experiment-plan-v3-20260828.md =====
# E2-R17 Experiment Plan V3 — Pre-Pilot Frozen Design

Date: 2026-08-28
Status: **V3_DUAL_REVIEW_REQUIRED_BEFORE_RUNTIME_PILOT**
Scientific authority: **ZERO until a separate authorization contract exists**

This plan supersedes V2 for future execution only. It does not rewrite E0, V1, V2, or their reviews.

## 1. Paper-level scientific question

Search is optimized for present acting: generate several trajectories and serve a high-scoring winner. Persistent self-evolution introduces a second consumer of the same generated object: the learner that updates future skill.

E2-R17 tests whether:

> a search selector that is optimal for current acting systematically changes the evidence distribution visible to a persistent learner, creating **compute shielding**: current user-facing failure becomes less visible even while success/failure contrast remains available in the discarded search pool.

The paper must not claim the already-published statement that failed trajectories can improve memory. ReasoningBank/MaTTS (ICLR 2026) already occupies that territory.

The narrower candidate contribution is:

1. formal separation of acting projection and learning projection over the exact same generated search pool;
2. a search-compute evidence law showing how winner-visible failure and mixed-pool evidence move in opposite directions as K grows;
3. exact-same-pool causal identification of whether the hidden evidence changes future frozen skill;
4. a minimal one-witness repair if and only if the causal experiment supports it;
5. prospective regime prediction before confirmatory outcomes.

No abstract-level “compute-shielding law causes long-run degradation” claim is permitted until prospective E3 passes.

## 2. Theory and estimands

Let the exact K-pool be `T_1:K`, binary verifier outcomes `Y_i`, fixed initial persistent state `S`, acting selector `a`, learning projection `g`, frozen updater `U`, and future held-out value `J`.

### 2.1 Rescue identity

For arbitrary correlated joint rollout laws:

`A_K - A_1 = P(Y_1=0, max_i Y_i=1) = V_pre(K)-V_winner(K)`.

No rollout independence is required.

Under iid Bernoulli success probability `p`:

`Gamma_K(p)=(1-p)-(1-p)^K`.

This is an acting-side identity only.

### 2.2 Compute-shielding support law

Define:

- `A_K=P(any success)`;
- `W_K=P(all fail)` = failure visible through winner-only acting/learning;
- `F_K=P(any failure)` = failure available anywhere in the generated pool;
- `M_K=P(any success and any failure)` = mixed-pool contrast support.

For nested search pools, without iid:

- `A_K` nondecreasing in K;
- `W_K` nonincreasing;
- `F_K` nondecreasing;
- `M_K` nondecreasing.

Under iid:

- `A_K=1-(1-p)^K`;
- `W_K=(1-p)^K`;
- `F_K=1-p^K`;
- `M_K=1-p^K-(1-p)^K`.

For fixed `0<p<1`, K increasing drives `A_K->1`, `W_K->0`, `F_K->1`, `M_K->1`.

This law establishes **availability and visibility**, not learning utility.

### 2.3 Primary causal learning estimand

Define `g_MRW`:

- nonmixed pool: identical to `g_WIN`;
- mixed pool: expose the deterministic lowest-rollout-index failed nonwinner as the one updater-visible source trajectory;
- acting always serves exactly the same winner.

Then exactly by conditioning:

`Delta_K = E[J(U(S,g_MRW(T_1:K)))-J(U(S,g_WIN(T_1:K)))] = M_K * delta_K`,

where:

`delta_K = E[D | mixed pool]`.

No assumption `delta_K>0` is made.

- `delta_K>0`: hidden witness has reusable future value;
- `delta_K=0`: evidence shielding exists but is learning-irrelevant;
- `delta_K<0`: failed witness is harmful or misleading.

E1 is designed to identify this learning-side term.

## 3. Frozen historical E0

E0 summary SHA:

`533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366`

Historical E0 decision remains **HOLD** under its original rescue-count gate.

Observed K=8:

- 12/12 acting success;
- 8/12 mixed pools;
- 1/12 rescue events;
- 0/12 winner-visible failures;
- 16 hidden failed nonwinner trajectories;
- failure evidence across 5/6 frozen families.

The old 42-task rescue-quota extension is not authorized under V3 because rescue count is not the treatment-support quantity for MRW.

## 4. Frozen controlled split

Use exactly:

`/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2`

Split manifest SHA:

`aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9`

Suite manifest SHA:

`2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4`

Selection is outcome-blind and SHA256/family-balanced.

E1 structure:

- 6 predeclared failure families;
- 2 independent update streams per family;
- 8 distinct update tasks per stream;
- 12 stream units, 96 update tasks total;
- 18 common held-out probes never fed to the updater.

No task substitution is allowed after E1 support is observed.

## 5. E1-A — exact pool generation and pre-treatment support gate

Generate exactly one K=8 pool for each of the 96 frozen update tasks from the same frozen initial skill state.

Actor rollouts:

`96 x 8 = 768`.

All rollout artifacts and K=1/2/4/8 nested prefix pools are persisted immediately and content-addressed. **No updater call is made during E1-A.**

### 5.1 Hard causal-identifiability gate

After all 96 K=8 pools are frozen:

1. `mixed_pool_count >= 24/96`;
2. at least `8/12 streams` each contain `>=2/8 mixed pools`;
3. protocol integrity is complete for every scientific unit;
4. completed-unit SHAs revalidate before the gate is evaluated.

These are hard floors. No rounding, waiver, or “close enough” adjudication exists:

- 23/96 -> fail;
- 7/12 exposed streams -> fail;
- a stream with only 1 mixed pool does not count as exposed for this gate.

A failed hard support gate stops E1 before updater calls. A redesign requires a new protocol and cannot replace individual tasks based on observed support.

### 5.2 Generalization qualification, separate from causal authorization

Failure-family coverage is not required to identify the pooled stream-level causal effect.

Record instead:

`family_support = number of predeclared families containing >=1 mixed pool`.

- `>=4/6`: family-heterogeneity description and later family-wise E3 prediction may proceed;
- `<4/6`: pooled E1 may still proceed if the hard gate passes, but broad family-generalization and E3 family-ranking claims are blocked.

This separation prevents an arbitrary family threshold from controlling the core causal estimand.

## 6. Frozen evidence renderer — fixed before Pilot

Primary WIN/MRW evidence matching is frozen now, not selected after Pilot.

Implementation:

`research_pipeline/e2_r17_evidence_window.py`

Frozen configuration:

- tokenizer package: `tiktoken==0.11.0`;
- encoding: `cl100k_base`;
- source-evidence cap: 3072 tokens;
- canonical evidence includes branch-specific user/assistant/tool messages plus verifier score/message;
- common system prompt and provenance/provider metadata are excluded from updater-visible source evidence;
- for each exact WIN/MRW task pair:
  `B_pair=min(3072, raw_tokens(WIN), raw_tokens(MRW))`;
- both arms receive exactly `B_pair` source-evidence tokens;
- when truncation is needed: first one-third + final two-thirds tokens;
- no padding and no additional semantic evidence;
- every rendered source is hash-bound with raw counts, matched count, tokenizer identity, cap, and rendered SHA.

Reason for head/tail preservation: the head retains task/intention context and the tail retains terminal execution/verifier/failure evidence. The same deterministic transform is applied to both arms.

If this exact renderer proves mechanically infeasible during the outcome-blind runtime Pilot, the Pilot fails. V3 does not authorize switching to raw evidence based on scientific outcome.

## 7. E1-B — updater causal tranche

E1-B is authorized only after E1-A support passes and a later immutable execution contract binds current model identity, updater revision, renderer revision, budgets, and run roots.

### 7.1 Core cloned arms

#### WIN-A — primary control

- exact same 8 pools in the stream;
- acting serves each frozen winner;
- updater receives one matched-window winner trajectory per task.

#### WIN-B — identical-treatment negative control

- exactly the same input projection as WIN-A;
- separate fresh cloned persistent state from the same initial skill;
- same updater configuration and model;
- independent provider calls.

Purpose: empirically measure residual updater/provider stochasticity even with temperature 0.

#### MRW — primary intervention

- exact same pools and served winners as WIN-A;
- nonmixed task: identical updater evidence as WIN;
- mixed task: one matched-window deterministic lowest-index failed nonwinner;
- no extra actor calls;
- one evidence trajectory per task, exactly as WIN.

#### RB-AGG — predeclared published-collision diagnostic

A ReasoningBank/MaTTS-style same-pool semantic adapter aggregates success/failure evidence from the exact frozen pool into updater evidence under a predeclared budget/accounting rule.

This arm runs regardless of MRW GO/HOLD, provided its mechanical semantic Pilot passes.

It is labeled `ReasoningBank-style same-pool aggregation`, **not** “official ReasoningBank reproduction,” because:

- the spreadsheet substrate is not the paper's native WebArena substrate;
- current public MaTTS launcher semantics require reproduction adjudication;
- official source-faithful ReasoningBank remains a later WebArena lane.

RB-AGG exists to prevent the paper from confusing a minimal failed-witness effect with the already-published broader idea of aggregating successful and failed trajectories.

### 7.2 Updater freeze

For all E1-B arms:

- first-party updater: MindMemOS `SkillEvolver` at a contract-bound commit;
- same initial SKILL.md SHA;
- same batch size: exactly 8 task packets;
- same updater prompt/parser/config;
- provider retries: 0;
- thinking: disabled;
- if first-party call omits temperature, adapter forces `temperature=0.0`;
- resolved updater identity requalified immediately before tranche authorization;
- parse-correction attempts remain explicit and counted, never hidden provider retries;
- every provider call persisted atomically without raw provider IDs or credentials.

The WIN-A/WIN-B control is required because temperature 0 does not imply mathematical determinism of a hosted model.

## 8. E1 held-out evaluation

For every learned stream state and every arm:

- freeze post-update SKILL.md and SHA;
- evaluate exactly the same 18 held-out probes;
- executor K=1;
- no search at evaluation;
- identical model/runtime/verifier;
- every probe output and verifier result persisted immediately.

Per-stream endpoint:

`J_s(arm)=mean success over 18 held-out probes`.

Independent units: 12 stream-level learned states. The 18 probes are repeated measurements, not independent causal units.

## 9. Statistical decision rules

### 9.1 Negative-control gate first

Before interpreting MRW:

`N_s = J_s(WIN-B)-J_s(WIN-A)`.

Practical equivalence margin:

`epsilon=1/18=0.055555...` absolute success.

Use paired TOST at alpha=.05:

- equivalently, the 90% paired-mean t interval must lie entirely within `[-epsilon,+epsilon]`;
- report a 90% paired-bootstrap interval as robustness.

If WIN-A and WIN-B do not establish equivalence, the causal tranche is:

`HOLD_UPDATER_STOCHASTICITY`

and MRW/RB differences are not promoted as evidence causality.

### 9.2 Primary superiority: MRW vs WIN-A

For 12 paired stream effects:

`D_s=J_s(MRW)-J_s(WIN-A)`.

Primary superiority test:

- exact one-sided sign-flip/randomization distribution over all `2^12=4096` within-pair sign assignments;
- alpha=.05;
- mean paired effect must be positive.

Report:

- exact p;
- mean and median `D_s`;
- 95% paired bootstrap CI over streams;
- per-stream mixed dose and effect;
- descriptive family grouping only.

Primary **GO** requires:

- negative-control equivalence passed;
- mean `D_s>0`;
- exact one-sided p<=.05;
- 95% paired-bootstrap lower bound >0;
- no evidence-rendering/provenance failure.

### 9.3 Qualified STOP vs HOLD

For MRW-vs-WIN, also perform paired TOST with `epsilon=1/18`, alpha=.05.

- equivalence supported -> `STOP_MRW_PRACTICALLY_NULL`;
- significantly negative effect -> `STOP_MRW_HARMFUL`;
- superiority fails and equivalence fails -> `HOLD_UNDERPOWERED_OR_HETEROGENEOUS`.

“Nonsignificant” alone is never interpreted as no effect.

### 9.4 Power disclosure

With n=12 paired stream units, one-sided alpha=.05 and 80% power under a paired-t approximation requires standardized paired effect approximately:

`d=0.7664`.

For equal-magnitude positive/negative pairs, 10/12 positive pairs are required for a one-sided sign probability below .05. Therefore E1 is intentionally decisive mainly for moderate-to-large repeatable effects; small effects may remain HOLD.

No later benchmark zoo is allowed to convert an inconclusive/negative core mechanism into a positive causal claim.

## 10. Predeclared collision interpretation including RB-AGG

After the WIN negative-control gate:

| MRW vs WIN | RB-AGG vs WIN | Interpretation |
|---|---|---|
| superior | superior | hidden search evidence has learning consequence; test whether one witness is practically equivalent to richer aggregation; never claim generic failure utility as novelty |
| superior | equivalent/null | minimal failed witness is specifically useful under this updater; investigate why richer aggregation diluted it |
| equivalent/null | superior | reject MRW as final repair; effect is aggregation-sensitive and overlaps ReasoningBank more strongly; novelty is narrowed substantially |
| equivalent | equivalent | central learning-consequence mechanism STOP for this substrate |
| negative | any | failed-witness repair rejected; do not promote MRW |

`RB-AGG` is a secondary collision diagnostic, not part of the primary MRW superiority alpha claim. Any inferential multiplicity beyond the primary contrast is labeled secondary/exploratory unless a later contract predeclares adjustment.

## 11. Additional diagnosis after primary results

Only after the primary and collision outcomes are frozen, diagnostic arms may be interpreted according to predeclared roles:

- Full Pool — information-retention upper bound, larger evidence budget;
- deterministic random nonwinner — generic branch-diversity control;
- success nonwinner when available — alternative-success control.

These cannot rescue a failed primary MRW claim. They only determine what aspect of nonwinner evidence mattered.

## 12. Published baseline hierarchy

Headline formally published baselines:

1. ReasoningBank/MaTTS — ICLR 2026;
2. PolySkill — ICLR 2026;
3. ACE — ICLR 2026;
4. Agent Workflow Memory — ICML 2025.

Extended:

5. SAGE — ACL 2026 Long.

ArXiv-only SkillCAT, Branch2Skill, SkillOpt, RethinkSkill, TSR remain collision/Related Work and are not counted as headline published baselines.

Pinned first-party repo SHAs and implementation caveats remain bound in:

`consultations/e2-r17-published-baseline-audit-v2-20260828.md`.

## 13. External evaluation uses two noninterchangeable lanes

### Lane A — source-faithful reproduction

Use first-party harness + stated/supported paper model where available. Record every deviation.

Current credential state on 69 means Gemini/OpenAI/Anthropic/SambaNova source lanes are not yet runtime-qualified. Model substitution is not allowed to masquerade as source-faithful reproduction.

If source-faithful reproduction remains blocked at submission:

> “We could not execute the first-party source-model lane for this baseline because the required provider/model route was unavailable in our execution environment; we therefore report only the separately labeled unified rerun and do not call it an exact reproduction.”

ReasoningBank additionally requires adjudication of the current public scaling launcher before any “source-faithful” label.

### Lane B — unified rerun

Direct quantitative ranking is allowed only under a matched substrate:

- same benchmark revision;
- same task IDs;
- same executor per comparison block;
- same environment/tool interface;
- same generated-pool accounting where applicable;
- explicit updater/context budgets;
- same held-out evaluator.

Cross-model robustness claims require at least:

- 2 independently qualified executor models;
- preferably >=2 model families.

If only one model qualifies, report a single-model result and make no cross-model robustness claim.

Model inclusion is based only on outcome-blind runtime/tool qualification, not R17 gain.

## 14. Public benchmark sequence after E1 GO

### E2-A WebArena — primary published-baseline lane

ReasoningBank, AWM, and PolySkill all expose first-party WebArena implementations.

Core matched methods after adapter Pilot:

- base/no persistent learning;
- Winner-only;
- final minimal E2-R17 projection if E1 GO;
- Full Pool where budget interpretation is explicit;
- AWM;
- ReasoningBank/MaTTS;
- PolySkill when semantic/runtime fairness passes.

Source-faithful scores and unified reruns appear in separate tables.

### E2-B AppWorld — second domain

Published anchors:

- ACE;
- SAGE extended.

Unified matched methods include base, Winner, final R17 projection, ACE adapter, and Full Pool where meaningful. SAGE is never forced into false equality with context-only methods; parametric training compute is reported separately.

### E2-C SpreadsheetBench Verified-400 — additional transport

Retain if budget permits because it is close to the controlled substrate, but it is not the only headline public comparison.

## 15. E3 prospective regime prediction

Only after E1 establishes a learning consequence.

On development/calibration streams estimate:

- `M_z(K)` availability;
- conditional diagnostic-value proxies/effect estimates;
- K ordering and null regions.

Before untouched future streams are evaluated, hash-freeze:

- effect sign;
- K ordering;
- family ranking if family-support qualification passed;
- predicted null cells.

Then compare prediction vs held-out future outcomes.

Required outputs:

- sign accuracy;
- rank correlation where identified;
- calibration of predicted vs observed effect;
- failed predictions retained.

If E3 fails, delete prospective regime-law claims and retain only the E1 causal finding.

## 16. E4 multi-round persistent evolution

Only after E1 + at least one public transport result pass.

Matched streams:

- low-search / winner learning;
- high-search / winner-only learning;
- high-search / final R17 learning projection;
- optional precommitted control.

After each update batch:

- freeze skill SHA;
- common K=1 evaluation;
- separately record current online acting reward and future frozen-skill value.

Question: can current search improve while future persistent learning degrades, and can a corrected learning projection prevent that divergence?

## 17. E5 topology

Only after earlier evidence chain passes.

Matched-call factorial:

`parallel best-of-K vs sequential refinement`

x

`winner/final-only learning vs history-preserving learning`.

This tests projection semantics rather than raw compute amount.

## 18. Runtime Pilot before any full scientific authorization

The runtime Pilot is **outcome-blind with respect to method effectiveness**. It may use development or frozen historical E0 artifacts but cannot inspect future E1 held-out skill outcomes.

It must validate:

1. exact tokenizer dependency and matched-window renderer;
2. exact token parity on WIN/MRW pairs;
3. no system/provenance leakage into updater source evidence;
4. MRW differs from WIN only on mixed pools;
5. WIN-A/WIN-B receive byte-identical updater input packets before provider calls;
6. temperature=0, retry=0, thinking disabled are present in receipts;
7. RB-AGG semantic adapter has fixed source-pool provenance and explicit evidence accounting;
8. updater calls/tokens/latency and parse-correction frequency are measured for budget purposes only;
9. crash-and-resume revalidates SHA and executes missing units only;
10. no model/baseline is promoted based on observed R17 performance.

The Pilot may fail a runtime/measurability condition. It may not select a renderer/model because one gives a better scientific effect.

## 19. Checkpoint and recovery

Every complete unit persists immediately:

- rollout raw trajectory / artifact / verifier / provider hashes;
- K-pool and nested prefix pools;
- projection packet and matched-window receipt;
- updater input/output, pre/post skill, adapter receipts;
- each held-out evaluation.

Three layers:

- `raw/` immutable;
- `checkpoints/` completed/missing/failed manifests;
- `summary/` rebuildable.

On resume:

1. load completed manifest;
2. re-hash every content-addressed completed unit;
3. quarantine any SHA mismatch and STOP rather than trust it;
4. execute only missing units.

After MCP 502/timeout/SSH disconnect, inspect process, lock, summary, and completed manifests before any relaunch.

## 20. Budget gate

No V3 full scientific run is authorized until the outcome-blind runtime Pilot freezes:

- actor calls / rollout;
- actor input/output tokens / rollout;
- updater provider calls / stream/arm;
- updater input/output tokens / stream/arm;
- parse-correction rate;
- held-out evaluation calls/tokens;
- wall time;
- hard ceiling and stop-on-budget behavior.

Known structural E1-A actor-rollout count is 768. Historical E0 token/call rates are planning references only and cannot substitute for the V3 Pilot budget receipt.

## 21. V3 pre-review decision table

Current status before V3 independent review:

- theory correction: implemented/tested;
- mixed-pool projection: implemented/tested;
- matched evidence renderer: implemented, exact tokenizer dependency intentionally not installed in shared environment yet;
- updater temperature default: frozen to 0 for future calls and tested;
- published baseline pins: audited;
- V2 dual review: both REVISE; adjudicated;
- V3 runtime Pilot: **NOT AUTHORIZED YET**;
- E1-A pool generation: **NOT AUTHORIZED**;
- E1-B updater: **NOT AUTHORIZED**;
- public benchmark full run: **NOT AUTHORIZED**.

Next gate: independent Kimi K3 + DeepSeek V4-Pro V3 review. Only if both allow outcome-blind runtime Pilot may the isolated renderer/updater/baseline-adapter Pilot contract be executed.


===== BOUND ARTIFACT: consultations/e2-r17-v2-review-adjudication-20260828.md =====
# E2-R17 V2 Dual-Review Adjudication

Date: 2026-08-28
Status: **REVISE_BEFORE_RUNTIME_PILOT**
Scientific authority: **ZERO**

## Bound V2 review

Experiment Plan V2 SHA-256:

`3a620eb791b2515b8498d9313698c51a50d59a0b03fb1684379b535e3a73ff08`

Independent reviewers:

- `deepseek-v4-pro` -> `deepseek-v4-pro-ga-260813`
- `kimi-k3` -> `kimi-k3`

Both reviews completed after a transport-level MCP 502. The process and output directory were inspected before any relaunch; both reviewer JSONs and the summary were already complete, so **no duplicate provider call was issued**.

Both verdicts:

`REVISE_V2_BEFORE_PILOT`

No E1 actor pool, updater outcome, held-out evaluation, public benchmark result, paper-promotion decision, or submission action was authorized by these consultations.

## Findings accepted as verdict-changing

### P0-1 — evidence budget must be frozen before Pilot

Both reviewers independently identified trajectory-length/truncation as a causal confound. V2 allowed choosing an evidence policy after runtime Pilot, which is too late.

**V3 repair:** freeze before Pilot:

- tokenizer package: `tiktoken==0.11.0`;
- encoding: `cl100k_base`;
- cap: `3072` tokens per source trajectory;
- canonical evidence excludes the common system prompt and provenance/provider metadata, but retains branch-specific user/assistant/tool messages and verifier score/message;
- for each exact WIN/MRW pair, matched budget `B_pair=min(3072, tokens(WIN), tokens(MRW))`;
- if truncation is needed, retain exactly one-third head and two-thirds tail tokens;
- no padding or extra semantic material;
- both arms receive exactly `B_pair` source-evidence tokens;
- every rendered artifact receives a hash-bound token-window receipt.

The renderer is implemented in `research_pipeline/e2_r17_evidence_window.py`. It refuses to run if the exact tokenizer dependency is unavailable or version-drifted.

### P0-2 — stream support gate must be internally consistent and non-waivable

The theory-correction artifact required at least two mixed pools per exposed stream, while V2 said at least one. This discrepancy is real.

**V3 repair:** use the stricter rule:

- `mixed_pool_count >= 24/96`;
- `>=8/12 streams` each contain `>=2/8 mixed pools`;
- all 96 exact pools frozen before evaluating the gate;
- no threshold rounding, relaxation, or task/pool replacement after support is observed;
- a borderline value such as 23/96 or 7/12 is a gate failure, not an adjudication opportunity.

Failure-family coverage is removed from the **primary causal-identifiability gate** because the pooled stream-level causal contrast is identified without requiring four families. Family support remains a separate generalization qualification:

- `>=4/6 families` with mixed support permits family-heterogeneity / prospective-family claims;
- `<4/6` does not prevent the pooled E1 causal test, but blocks broad family-generalization claims and E3 family-ranking promotion.

### P1-1 — ReasoningBank collision must be adjudicable regardless of MRW GO/HOLD

ReasoningBank/MaTTS is already an ICLR 2026 published method that learns from successful and failed trajectories generated with test-time scaling. A positive MRW result alone cannot be advertised as the novelty “failures help memory.”

**V3 repair:** predeclare a secondary `RB-AGG` semantic adapter on the same frozen pool and run it in the causal tranche regardless of MRW GO/HOLD, once its paper-spec semantics and evidence accounting pass runtime Pilot. This is **not** called an official source-faithful ReasoningBank reproduction on the spreadsheet substrate; official source-faithful reproduction remains a separate WebArena lane.

The role of `RB-AGG` is collision diagnosis:

- if MRW and RB-AGG both beat WIN, compare whether one witness is practically equivalent to richer aggregation;
- if MRW is null/equivalent but RB-AGG beats WIN, reject the minimal-witness repair and narrow the claim to aggregation-sensitive projection;
- if both are equivalent to WIN, the learning-consequence mechanism is unsupported/STOP subject to the frozen equivalence rule.

### P1-2 — updater stochasticity must be measured, not assumed away

MindMemOS SkillEvolver's first-party summary/patch calls do not currently supply an explicit temperature to the adapter.

**V3 repair:** future V3 updater calls freeze unspecified temperature to `0.0`, retry to zero, thinking disabled, and resolved model identity to a tranche-qualified value. In addition, create a separate `WIN-B` cloned updater stream with the **same one-slot WIN input as WIN-A**. WIN-A vs WIN-B is an identical-treatment negative control. If their future frozen skills fail the predeclared equivalence/noise criterion, the MRW contrast is not interpreted.

The temperature default is now explicit in `research_pipeline/e2_r17_mindmemos_ark_adapter.py`; historical receipts are not regenerated.

### P1-3 — equivalence STOP must be operational

**V3 repair:** practical equivalence margin remains `epsilon=1/18=0.055555...` absolute held-out success. Use paired TOST at alpha=0.05; equivalently, the 90% paired-mean confidence interval must lie wholly inside `[-epsilon,+epsilon]`. A paired bootstrap 90% CI is reported as robustness. Superiority remains a separate one-sided exact sign-flip test plus 95% paired bootstrap.

- equivalence supported -> qualified null/STOP for that contrast;
- significant negative -> STOP/reject repair;
- neither superiority nor equivalence -> HOLD/underpowered, never “no effect.”

### P1-4 — 12-stream power limitation must be explicit

For `n=12` paired stream units, one-sided alpha=.05 and 80% power under a paired t approximation requires standardized effect `d ~= 0.7664`. With equal-magnitude signs, 10/12 positive pairs are required before a one-sided sign test falls below .05. Therefore E1 is designed to identify moderate-to-large repeatable effects; a wide null interval is HOLD rather than evidence of absence.

### P1-5 — source-faithful vs unified baseline fallback

Current 69 environment exposes Ark credentials but not Google/OpenAI/Anthropic/SambaNova credentials. V3 explicitly treats this as a source-faithful-lane blocker rather than silently substituting models.

If a source-faithful lane remains unavailable at submission time, the paper must state that limitation and report only the clearly labeled unified rerun for that method. Source-faithful and unified results never share one ranking column.

### P1-6 — minimum unified model breadth

Cross-model robustness claims require at least two independently qualified executor models and at least two model families where feasible. If only one unified model qualifies, the paper reports a single-model result and makes no cross-model robustness claim.

## Findings accepted as nonblocking but frozen for V3

- updater token/call ceilings must be measured in runtime Pilot before E1-B authorization;
- resume must re-hash completed units before trusting the completed manifest;
- E1 alone can establish `delta_K` under exact same-pool control, but prospective compute-shielding regime-law claims require later E3 to pass;
- family effects with two streams/family remain descriptive in E1; no family-specific significance claim.

## Adjudication

`V2 = REVISE_BEFORE_RUNTIME_PILOT`

The theory is not rejected. The next legitimate artifact is V3 with the above repairs. No scientific execution may use V2 as authority.


===== BOUND ARTIFACT: generated/e2-r17-experiment-plan-v2-review-20260828/deepseek-v4-pro.json =====
{
  "artifact_type": "e2-r17-experiment-plan-v2-independent-review",
  "created_at_utc": "2026-08-28T08:41:11+00:00",
  "dossier_file_sha256": {
    "consultations/e2-r17-experiment-plan-v2-20260828.md": "c59ac5fda591efb0658571dc0db77bbe2e54f70f928917c4768c19153f9ce4ad",
    "consultations/e2-r17-published-baseline-audit-v2-20260828.md": "2e83bb09f7f2cc01b2250bc07e9d6cf1c117efbc9454b54c7799a819e6110d24",
    "consultations/e2-r17-theory-correction-mixed-pool-20260828.md": "9a45b28c33081a88e7453a9b3a608736e7b60e4ddcdde559d981321156a2f0db",
    "generated/e2-r17-e0-analysis-20260828.json": "40670a5d07d3af2b0d64723cc7d3bacc23ad55efd468f204872cf5820e03e562",
    "generated/e2-r17-e0-go-hold-stop-20260828.json": "abedaa851694635d9416c408e4e60bf819eb0815a37891d20d4ed305e0b42ec8",
    "generated/e2-r17-experiment-plan-v2-20260828.json": "3a620eb791b2515b8498d9313698c51a50d59a0b03fb1684379b535e3a73ff08",
    "generated/e2-r17-experiment-plan-v2-model-identity-qualification-20260828.json": "42030107ae538a97f9087a9489fe417a910a17be635c8576120c96ccec225ccc",
    "generated/e2-r17-published-baseline-audit-v2-20260828.json": "fc355a7423f3b99352be7bcf953814c3a7d8b51792b91e76860f81374cfd0025",
    "generated/e2-r17-theory-correction-mixed-pool-20260828.json": "1ca596bbf27e18fe34e1f2515fa99eea8e6dfbff500568d6cc2bf6c452a5e360"
  },
  "expected_resolved_model": "deepseek-v4-pro-ga-260813",
  "experiment_authority": false,
  "exposed_to_other_review": false,
  "get_poll_recovery": false,
  "hidden_provider_retry_used": false,
  "independent": true,
  "max_output_tokens": 6000,
  "missing_required_fields": [],
  "paper_promotion_authority": false,
  "parse_valid": true,
  "plan_sha256": "3a620eb791b2515b8498d9313698c51a50d59a0b03fb1684379b535e3a73ff08",
  "poll_count": 0,
  "prompt_path": "generated/e2-r17-experiment-plan-v2-review-20260828/deepseek-v4-pro-prompt.md",
  "prompt_sha256": "a5b9f72a0c37d91ec9633c23aa29631e51d2c18274e0deb252ace0b7f75ac790",
  "provider_generation_attempts": 1,
  "provider_retry_limit": 0,
  "provider_status": "completed",
  "raw_text": "{\n  \"plan_sha256_acknowledged\": \"3a620eb791b2515b8498d9313698c51a50d59a0b03fb1684379b535e3a73ff08\",\n  \"verdict\": \"REVISE_V2_BEFORE_PILOT\",\n  \"novelty_against_reasoningbank\": \"The novelty boundary is defensible but fragile. ReasoningBank/MaTTS already establishes success+failure memory induction from test-time-scaled trajectories, so the plan correctly disclaims that statement. The remaining candidate claim—exact same-pool acting/learning projection separation with a budget-matched one-slot causal intervention—is genuinely narrower and not established by the cited published work. However, the plan does not yet prove the intervention is distinguishable from ReasoningBank-style aggregation in practice: the primary MRW arm is a single deterministic failed nonwinner, while ReasoningBank aggregates success and failure. The diagnostic E1-C ReasoningBank adapter is post-GO only, so a null or weak primary result cannot distinguish 'failure-specific value' from 'generic aggregation value' without opening the diagnostic gate. The novelty is real as a causal object but the evidentiary path to claiming it is under-specified.\",\n  \"theory_estimand_assessment\": \"M_K is the correct treatment-support quantity for the MRW contrast: MRW differs from WIN only on mixed pools, so Delta_K = M_K * delta_K holds exactly by conditioning under the stated cloned-stream design. The factorization is identified because the same frozen pool is used for both arms, acting is identical, and the only manipulated variable is the learning projection. The cloned-stream design removes the usual SUTVA concern about acting/learning interference within a stream. The main residual threat is that delta_K is a conditional effect on a post-treatment (pool-composition) event, so it is not a purely pre-treatment causal estimand; this is acceptable for a mechanism experiment but must not be promoted to a population-average policy effect without the M_K weighting being made explicit. The plan does make this explicit.\",\n  \"historical_e0_preservation_assessment\": \"The plan preserves the frozen E0 HOLD and its rescue-count gate while superseding only the future support estimand. This is the correct way to avoid post-hoc rewriting. The E0 summary SHA is pinned and the old 42-task rescue-quota tranche is explicitly forbidden. No retroactive reinterpretation of E0 receipts is performed. This is clean.\",\n  \"mixed_support_gate_assessment\": \"The thresholds (24/96 mixed pools, 8/12 exposed streams, 4/6 families) are plausible but not derived from a predeclared statistical principle. The stream-level gate is the most defensible because the stream is the inference unit. The 24/96 total-pool gate is a floor on treatment dose and is reasonable. The 4/6 family gate is the weakest: with only 2 streams per family, family coverage is a descriptive heterogeneity check, not an identifiability requirement, and requiring 4/6 families does not obviously protect the primary stream-level test. The gate is not arbitrary enough to be fatal, but V3 should predeclare the exact decision rule for borderline cases (e.g., 23/96 mixed or 7/12 streams) and justify why family coverage is a support requirement rather than a descriptive covariate.\",\n  \"stream_unit_and_statistics_assessment\": \"The 12 paired streams are the correct independent units because the updater state evolves within a stream and is cloned across arms. The 18 held-out probes are repeated measurements within a stream, not independent units, and the plan correctly treats them as such. The exact 2^12 sign-flip test is valid for a paired design under the null of exchangeable within-pair signs, which holds under the cloned-stream randomization. No pseudoreplication is apparent in the primary analysis. The bootstrap over 12 streams is coarse but acceptable as a secondary interval. The main weakness is power: with 12 units and a binary-ish endpoint averaged over 18 probes, the minimum detectable effect is large, and the plan's HOLD region is likely to be wide. This is an underpowering concern, not a validity defect.\",\n  \"equivalence_stop_rule_assessment\": \"The +/-1/18 margin is defensible as a practical-equivalence bound because it corresponds to one held-out probe success per stream and is predeclared. The plan correctly distinguishes qualified STOP (significantly negative or within the equivalence margin) from HOLD (interval spans zero and larger effects). This is the right structure. The risk is that with 12 streams the equivalence test will be underpowered, so the plan may land in HOLD rather than a clean STOP even when the true effect is near zero. That is acceptable and honest, but V3 should predeclare the exact equivalence test procedure (e.g., TOST on the paired mean with the same bootstrap or a predeclared CI-based rule) so the STOP decision is not post-hoc.\",\n  \"evidence_token_budget_assessment\": \"The one-slot WIN vs MRW contrast can still be confounded by evidence-token length: a failed nonwinner trajectory may be longer or shorter than the served winner, and the updater may respond to length rather than failure content. The plan acknowledges this and defers the fix to the runtime Pilot. The cleanest pre-Pilot repair is to freeze the deterministic common-window renderer as the primary policy, with raw-trajectory plus matched-window secondary as a robustness arm. V3 should predeclare that the common-window renderer is the default unless the Pilot shows it destroys semantic content, and should specify the exact tokenizer and windowing rule before any held-out outcome.\",\n  \"published_baseline_fidelity_assessment\": \"The baseline hierarchy is fair and current given the bound audit. ReasoningBank, PolySkill, ACE, and AWM as headline with SAGE extended is defensible. The implementation caveats are handled honestly: the ReasoningBank launcher/inducer directory bug is flagged as requiring adjudication before source-faithful reproduction, and PolySkill's clean-room re-release is disclosed. The plan does not silently patch baselines. The main gap is that the ReasoningBank adapter is only a post-GO diagnostic, so the primary collision baseline is not directly tested in the primary causal contrast. This is acceptable for E1 mechanism identification but must be addressed before any public-benchmark claim.\",\n  \"source_faithful_vs_unified_lane_assessment\": \"The two-lane separation is necessary and sufficient given no common published model. The plan correctly forbids merging source-faithful and unified rankings. The Ark-only credential availability is a source-lane blocker, not a fatal program blocker, because the unified rerun lane can proceed with qualified Ark models and the source-faithful lane can be deferred or run when credentials are configured. V3 should predeclare which source-faithful lanes are mandatory for the paper claim and which can be omitted without invalidating the central mechanism result.\",\n  \"benchmark_selection_assessment\": \"WebArena primary and AppWorld secondary are the right external benchmarks after E1 GO because they host the headline published baselines. SpreadsheetBench as additional is appropriate because it is transport-relevant but not the sole external lane. This is a sound correction from the V1 arXiv-led benchmark choice.\",\n  \"model_selection_assessment\": \"The plan keeps model selection outcome-blind and does not pretend Qwen/DeepSeek are common published models. The unified lane is described as a matched-rerun capability spread, not a false common axis. The model-identity qualification artifact shows the Ark plan route resolves distinct identities with no hidden retries. This is clean.\",\n  \"checkpoint_resume_assessment\": \"The checkpoint policy is sufficient: immediate persistence of rollout/pool/projection/updater/held-out artifacts, immutable raw, rebuildable summary, missing-unit resume only, and no blind relaunch after 502. The no-relaunch-without-inspection rule is important and correctly stated.\",\n  \"budget_assessment\": \"The plan does not authorize full runs and correctly defers budget ceilings to the runtime Pilot. The 768 actor rollouts for E1-A are known and bounded. The E0 planning reference of ~5.9 calls and ~17.8k tokens per rollout is disclosed as a planning reference only. V3 must bind measured Pilot ceilings before E1-B, which the plan already requires.\",\n  \"fatal_or_blocking_issues\": [\n    {\n      \"priority\": \"P0\",\n      \"issue\": \"The evidence-budget policy is not frozen before the runtime Pilot, leaving the primary causal contrast vulnerable to token-length confounding.\",\n      \"why_blocking\": \"If the failed nonwinner trajectory differs systematically in token length from the served winner, the primary WIN vs MRW effect cannot be attributed to failure content. The plan defers this to the Pilot, but the Pilot itself must have a predeclared default policy or it will be outcome-informed.\",\n      \"exact_v3_repair\": \"Predeclare in V3 that the deterministic common-window renderer under a fixed public tokenizer is the primary evidence policy, with raw-trajectory plus matched-window secondary as a predeclared robustness arm. Specify the exact tokenizer, window size, and truncation/padding rule before any held-out outcome. The Pilot may only validate feasibility, not choose between policies after seeing outcomes.\"\n    },\n    {\n      \"priority\": \"P0\",\n      \"issue\": \"The support gate thresholds are not derived from a predeclared statistical principle and the family-coverage requirement is not justified as a support condition.\",\n      \"why_blocking\": \"The gate determines whether E1-B is authorized at all. If the gate is arbitrary, a borderline failure (e.g., 23/96 mixed or 7/12 streams) could be adjudicated post-hoc, undermining the pre-registration.\",\n      \"exact_v3_repair\": \"Predeclare the exact decision rule for borderline cases and justify each threshold. Specifically: (a) state whether 24/96 is a hard floor or a rounded planning target; (b) justify why 4/6 family coverage is a support requirement rather than a descriptive covariate, or demote it to a descriptive check; (c) predeclare that no threshold may be relaxed after observing support.\"\n    },\n    {\n      \"priority\": \"P1\",\n      \"issue\": \"The primary MRW arm is not directly compared against ReasoningBank-style aggregation in the primary test, so a positive MRW result cannot distinguish failure-specific value from generic aggregation value without opening the post-GO diagnostic gate.\",\n      \"why_blocking\": \"The central novelty claim requires showing that a single budget-matched failed witness captures the useful information, not just that failure evidence helps. If the ReasoningBank adapter is only post-GO, a weak or null primary result leaves the novelty claim unresolved.\",\n      \"exact_v3_repair\": \"Add a predeclared secondary arm or pre-specified diagnostic trigger that runs the ReasoningBank-style aggregation adapter on the same frozen pools regardless of primary GO/HOLD, with the explicit purpose of testing whether MRW is distinguishable from aggregation. This must be predeclared before held-out outcomes, not gated on primary success.\"\n    }\n  ],\n  \"required_v3_changes\": [\n    {\n      \"priority\": \"P0\",\n      \"target\": \"evidence_budget_policy\",\n      \"change\": \"Freeze the common-window renderer as the primary policy with exact tokenizer/window/truncation rules before the runtime Pilot; raw-trajectory plus matched-window becomes a predeclared secondary robustness arm.\",\n      \"verdict_relevance\": \"Directly affects whether the primary causal contrast is interpretable as failure-content rather than token-length.\"\n    },\n    {\n      \"priority\": \"P0\",\n      \"target\": \"e1_a_support_phase.support_gate_for_review\",\n      \"change\": \"Predeclare exact borderline decision rules and justify or demote the 4/6 family-coverage requirement; state that no threshold may be relaxed after observing support.\",\n      \"verdict_relevance\": \"Determines whether E1-B authorization is pre-registered or post-hoc.\"\n    },\n    {\n      \"priority\": \"P1\",\n      \"target\": \"e1_c_diagnosis_after_primary_go_only\",\n      \"change\": \"Move the ReasoningBank-style aggregation adapter to a predeclared secondary arm or pre-specified diagnostic trigger that runs regardless of primary GO/HOLD, to test distinguishability from aggregation.\",\n      \"verdict_relevance\": \"Affects whether the central novelty claim can be established from the primary experiment.\"\n    },\n    {\n      \"priority\": \"P1\",\n      \"target\": \"e1_b_primary.equivalence_margin\",\n      \"change\": \"Predeclare the exact equivalence test procedure (e.g., TOST or CI-based rule) so the qualified STOP decision is not post-hoc.\",\n      \"verdict_relevance\": \"Affects the integrity of the STOP/HOLD decision.\"\n    }\n  ],\n  \"nonblocking_improvements\": [\n    \"Predeclare the exact bootstrap CI method (percentile vs BCa) and the tie-breaking rule for the sign-flip test when D_s = 0.\",\n    \"Add a predeclared sensitivity analysis for the lowest-index failed nonwinner rule, e.g., a random failed nonwinner arm, to test whether the deterministic index choice matters.\",\n    \"Specify the exact updater prompt and acceptance/rollback rule in the V3 contract rather than deferring to the Pilot.\",\n    \"Predeclare how actor_finished_false units (as seen in E0) are handled in E1-A pool generation.\"\n  ],\n  \"runtime_pilot_recommendation\": \"ALLOW_OUTCOME_BLIND_RUNTIME_PILOTS\",\n  \"e1_pool_support_phase_recommendation\": \"ALLOW_ONLY_AFTER_V3_CONTRACT\",\n  \"e1_updater_recommendation\": \"HOLD_UNTIL_SUPPORT_GATE_AND_V3\",\n  \"paper_claim_authority\": false,\n  \"single_sentence_verdict\": \"The V2 theory correction is sound and the causal object is genuinely narrower than ReasoningBank, but the evidence-budget policy, support-gate decision rule, and ReasoningBank distinguishability test must be predeclared in V3 before any runtime Pilot or E1 pool-generation authorization.\"\n}",
  "raw_text_sha256": "e179e3ad797b0ddbff862aba92f60c7484b1121dc3c7e61b0300f4c419cf3c59",
  "requested_model": "deepseek-v4-pro",
  "resolved_model": "deepseek-v4-pro-ga-260813",
  "resolved_model_matches_qualification": true,
  "response_id_sha256": "b217e7fd701643fb41a0831d5ff9f3c502d313da7114b63f437d74f6dbf0fdc5",
  "review": {
    "benchmark_selection_assessment": "WebArena primary and AppWorld secondary are the right external benchmarks after E1 GO because they host the headline published baselines. SpreadsheetBench as additional is appropriate because it is transport-relevant but not the sole external lane. This is a sound correction from the V1 arXiv-led benchmark choice.",
    "budget_assessment": "The plan does not authorize full runs and correctly defers budget ceilings to the runtime Pilot. The 768 actor rollouts for E1-A are known and bounded. The E0 planning reference of ~5.9 calls and ~17.8k tokens per rollout is disclosed as a planning reference only. V3 must bind measured Pilot ceilings before E1-B, which the plan already requires.",
    "checkpoint_resume_assessment": "The checkpoint policy is sufficient: immediate persistence of rollout/pool/projection/updater/held-out artifacts, immutable raw, rebuildable summary, missing-unit resume only, and no blind relaunch after 502. The no-relaunch-without-inspection rule is important and correctly stated.",
    "e1_pool_support_phase_recommendation": "ALLOW_ONLY_AFTER_V3_CONTRACT",
    "e1_updater_recommendation": "HOLD_UNTIL_SUPPORT_GATE_AND_V3",
    "equivalence_stop_rule_assessment": "The +/-1/18 margin is defensible as a practical-equivalence bound because it corresponds to one held-out probe success per stream and is predeclared. The plan correctly distinguishes qualified STOP (significantly negative or within the equivalence margin) from HOLD (interval spans zero and larger effects). This is the right structure. The risk is that with 12 streams the equivalence test will be underpowered, so the plan may land in HOLD rather than a clean STOP even when the true effect is near zero. That is acceptable and honest, but V3 should predeclare the exact equivalence test procedure (e.g., TOST on the paired mean with the same bootstrap or a predeclared CI-based rule) so the STOP decision is not post-hoc.",
    "evidence_token_budget_assessment": "The one-slot WIN vs MRW contrast can still be confounded by evidence-token length: a failed nonwinner trajectory may be longer or shorter than the served winner, and the updater may respond to length rather than failure content. The plan acknowledges this and defers the fix to the runtime Pilot. The cleanest pre-Pilot repair is to freeze the deterministic common-window renderer as the primary policy, with raw-trajectory plus matched-window secondary as a robustness arm. V3 should predeclare that the common-window renderer is the default unless the Pilot shows it destroys semantic content, and should specify the exact tokenizer and windowing rule before any held-out outcome.",
    "fatal_or_blocking_issues": [
      {
        "exact_v3_repair": "Predeclare in V3 that the deterministic common-window renderer under a fixed public tokenizer is the primary evidence policy, with raw-trajectory plus matched-window secondary as a predeclared robustness arm. Specify the exact tokenizer, window size, and truncation/padding rule before any held-out outcome. The Pilot may only validate feasibility, not choose between policies after seeing outcomes.",
        "issue": "The evidence-budget policy is not frozen before the runtime Pilot, leaving the primary causal contrast vulnerable to token-length confounding.",
        "priority": "P0",
        "why_blocking": "If the failed nonwinner trajectory differs systematically in token length from the served winner, the primary WIN vs MRW effect cannot be attributed to failure content. The plan defers this to the Pilot, but the Pilot itself must have a predeclared default policy or it will be outcome-informed."
      },
      {
        "exact_v3_repair": "Predeclare the exact decision rule for borderline cases and justify each threshold. Specifically: (a) state whether 24/96 is a hard floor or a rounded planning target; (b) justify why 4/6 family coverage is a support requirement rather than a descriptive covariate, or demote it to a descriptive check; (c) predeclare that no threshold may be relaxed after observing support.",
        "issue": "The support gate thresholds are not derived from a predeclared statistical principle and the family-coverage requirement is not justified as a support condition.",
        "priority": "P0",
        "why_blocking": "The gate determines whether E1-B is authorized at all. If the gate is arbitrary, a borderline failure (e.g., 23/96 mixed or 7/12 streams) could be adjudicated post-hoc, undermining the pre-registration."
      },
      {
        "exact_v3_repair": "Add a predeclared secondary arm or pre-specified diagnostic trigger that runs the ReasoningBank-style aggregation adapter on the same frozen pools regardless of primary GO/HOLD, with the explicit purpose of testing whether MRW is distinguishable from aggregation. This must be predeclared before held-out outcomes, not gated on primary success.",
        "issue": "The primary MRW arm is not directly compared against ReasoningBank-style aggregation in the primary test, so a positive MRW result cannot distinguish failure-specific value from generic aggregation value without opening the post-GO diagnostic gate.",
        "priority": "P1",
        "why_blocking": "The central novelty claim requires showing that a single budget-matched failed witness captures the useful information, not just that failure evidence helps. If the ReasoningBank adapter is only post-GO, a weak or null primary result leaves the novelty claim unresolved."
      }
    ],
    "historical_e0_preservation_assessment": "The plan preserves the frozen E0 HOLD and its rescue-count gate while superseding only the future support estimand. This is the correct way to avoid post-hoc rewriting. The E0 summary SHA is pinned and the old 42-task rescue-quota tranche is explicitly forbidden. No retroactive reinterpretation of E0 receipts is performed. This is clean.",
    "mixed_support_gate_assessment": "The thresholds (24/96 mixed pools, 8/12 exposed streams, 4/6 families) are plausible but not derived from a predeclared statistical principle. The stream-level gate is the most defensible because the stream is the inference unit. The 24/96 total-pool gate is a floor on treatment dose and is reasonable. The 4/6 family gate is the weakest: with only 2 streams per family, family coverage is a descriptive heterogeneity check, not an identifiability requirement, and requiring 4/6 families does not obviously protect the primary stream-level test. The gate is not arbitrary enough to be fatal, but V3 should predeclare the exact decision rule for borderline cases (e.g., 23/96 mixed or 7/12 streams) and justify why family coverage is a support requirement rather than a descriptive covariate.",
    "model_selection_assessment": "The plan keeps model selection outcome-blind and does not pretend Qwen/DeepSeek are common published models. The unified lane is described as a matched-rerun capability spread, not a false common axis. The model-identity qualification artifact shows the Ark plan route resolves distinct identities with no hidden retries. This is clean.",
    "nonblocking_improvements": [
      "Predeclare the exact bootstrap CI method (percentile vs BCa) and the tie-breaking rule for the sign-flip test when D_s = 0.",
      "Add a predeclared sensitivity analysis for the lowest-index failed nonwinner rule, e.g., a random failed nonwinner arm, to test whether the deterministic index choice matters.",
      "Specify the exact updater prompt and acceptance/rollback rule in the V3 contract rather than deferring to the Pilot.",
      "Predeclare how actor_finished_false units (as seen in E0) are handled in E1-A pool generation."
    ],
    "novelty_against_reasoningbank": "The novelty boundary is defensible but fragile. ReasoningBank/MaTTS already establishes success+failure memory induction from test-time-scaled trajectories, so the plan correctly disclaims that statement. The remaining candidate claim—exact same-pool acting/learning projection separation with a budget-matched one-slot causal intervention—is genuinely narrower and not established by the cited published work. However, the plan does not yet prove the intervention is distinguishable from ReasoningBank-style aggregation in practice: the primary MRW arm is a single deterministic failed nonwinner, while ReasoningBank aggregates success and failure. The diagnostic E1-C ReasoningBank adapter is post-GO only, so a null or weak primary result cannot distinguish 'failure-specific value' from 'generic aggregation value' without opening the diagnostic gate. The novelty is real as a causal object but the evidentiary path to claiming it is under-specified.",
    "paper_claim_authority": false,
    "plan_sha256_acknowledged": "3a620eb791b2515b8498d9313698c51a50d59a0b03fb1684379b535e3a73ff08",
    "published_baseline_fidelity_assessment": "The baseline hierarchy is fair and current given the bound audit. ReasoningBank, PolySkill, ACE, and AWM as headline with SAGE extended is defensible. The implementation caveats are handled honestly: the ReasoningBank launcher/inducer directory bug is flagged as requiring adjudication before source-faithful reproduction, and PolySkill's clean-room re-release is disclosed. The plan does not silently patch baselines. The main gap is that the ReasoningBank adapter is only a post-GO diagnostic, so the primary collision baseline is not directly tested in the primary causal contrast. This is acceptable for E1 mechanism identification but must be addressed before any public-benchmark claim.",
    "required_v3_changes": [
      {
        "change": "Freeze the common-window renderer as the primary policy with exact tokenizer/window/truncation rules before the runtime Pilot; raw-trajectory plus matched-window becomes a predeclared secondary robustness arm.",
        "priority": "P0",
        "target": "evidence_budget_policy",
        "verdict_relevance": "Directly affects whether the primary causal contrast is interpretable as failure-content rather than token-length."
      },
      {
        "change": "Predeclare exact borderline decision rules and justify or demote the 4/6 family-coverage requirement; state that no threshold may be relaxed after observing support.",
        "priority": "P0",
        "target": "e1_a_support_phase.support_gate_for_review",
        "verdict_relevance": "Determines whether E1-B authorization is pre-registered or post-hoc."
      },
      {
        "change": "Move the ReasoningBank-style aggregation adapter to a predeclared secondary arm or pre-specified diagnostic trigger that runs regardless of primary GO/HOLD, to test distinguishability from aggregation.",
        "priority": "P1",
        "target": "e1_c_diagnosis_after_primary_go_only",
        "verdict_relevance": "Affects whether the central novelty claim can be established from the primary experiment."
      },
      {
        "change": "Predeclare the exact equivalence test procedure (e.g., TOST or CI-based rule) so the qualified STOP decision is not post-hoc.",
        "priority": "P1",
        "target": "e1_b_primary.equivalence_margin",
        "verdict_relevance": "Affects the integrity of the STOP/HOLD decision."
      }
    ],
    "runtime_pilot_recommendation": "ALLOW_OUTCOME_BLIND_RUNTIME_PILOTS",
    "single_sentence_verdict": "The V2 theory correction is sound and the causal object is genuinely narrower than ReasoningBank, but the evidence-budget policy, support-gate decision rule, and ReasoningBank distinguishability test must be predeclared in V3 before any runtime Pilot or E1 pool-generation authorization.",
    "source_faithful_vs_unified_lane_assessment": "The two-lane separation is necessary and sufficient given no common published model. The plan correctly forbids merging source-faithful and unified rankings. The Ark-only credential availability is a source-lane blocker, not a fatal program blocker, because the unified rerun lane can proceed with qualified Ark models and the source-faithful lane can be deferred or run when credentials are configured. V3 should predeclare which source-faithful lanes are mandatory for the paper claim and which can be omitted without invalidating the central mechanism result.",
    "stream_unit_and_statistics_assessment": "The 12 paired streams are the correct independent units because the updater state evolves within a stream and is cloned across arms. The 18 held-out probes are repeated measurements within a stream, not independent units, and the plan correctly treats them as such. The exact 2^12 sign-flip test is valid for a paired design under the null of exchangeable within-pair signs, which holds under the cloned-stream randomization. No pseudoreplication is apparent in the primary analysis. The bootstrap over 12 streams is coarse but acceptable as a secondary interval. The main weakness is power: with 12 units and a binary-ish endpoint averaged over 18 probes, the minimum detectable effect is large, and the plan's HOLD region is likely to be wide. This is an underpowering concern, not a validity defect.",
    "theory_estimand_assessment": "M_K is the correct treatment-support quantity for the MRW contrast: MRW differs from WIN only on mixed pools, so Delta_K = M_K * delta_K holds exactly by conditioning under the stated cloned-stream design. The factorization is identified because the same frozen pool is used for both arms, acting is identical, and the only manipulated variable is the learning projection. The cloned-stream design removes the usual SUTVA concern about acting/learning interference within a stream. The main residual threat is that delta_K is a conditional effect on a post-treatment (pool-composition) event, so it is not a purely pre-treatment causal estimand; this is acceptable for a mechanism experiment but must not be promoted to a population-average policy effect without the M_K weighting being made explicit. The plan does make this explicit.",
    "verdict": "REVISE_V2_BEFORE_PILOT"
  },
  "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
  "schema_version": "1.0",
  "scientific_authority": false,
  "status": "COMPLETED",
  "submission_authority": false,
  "temperature": 0,
  "thinking_requested": "disabled",
  "usage": {
    "input_tokens": 20201,
    "input_tokens_details": {
      "cached_tokens": 18432
    },
    "output_tokens": 3033,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 23234
  }
}


===== BOUND ARTIFACT: generated/e2-r17-experiment-plan-v2-review-20260828/kimi-k3.json =====
{
  "artifact_type": "e2-r17-experiment-plan-v2-independent-review",
  "created_at_utc": "2026-08-28T08:42:00+00:00",
  "dossier_file_sha256": {
    "consultations/e2-r17-experiment-plan-v2-20260828.md": "c59ac5fda591efb0658571dc0db77bbe2e54f70f928917c4768c19153f9ce4ad",
    "consultations/e2-r17-published-baseline-audit-v2-20260828.md": "2e83bb09f7f2cc01b2250bc07e9d6cf1c117efbc9454b54c7799a819e6110d24",
    "consultations/e2-r17-theory-correction-mixed-pool-20260828.md": "9a45b28c33081a88e7453a9b3a608736e7b60e4ddcdde559d981321156a2f0db",
    "generated/e2-r17-e0-analysis-20260828.json": "40670a5d07d3af2b0d64723cc7d3bacc23ad55efd468f204872cf5820e03e562",
    "generated/e2-r17-e0-go-hold-stop-20260828.json": "abedaa851694635d9416c408e4e60bf819eb0815a37891d20d4ed305e0b42ec8",
    "generated/e2-r17-experiment-plan-v2-20260828.json": "3a620eb791b2515b8498d9313698c51a50d59a0b03fb1684379b535e3a73ff08",
    "generated/e2-r17-experiment-plan-v2-model-identity-qualification-20260828.json": "42030107ae538a97f9087a9489fe417a910a17be635c8576120c96ccec225ccc",
    "generated/e2-r17-published-baseline-audit-v2-20260828.json": "fc355a7423f3b99352be7bcf953814c3a7d8b51792b91e76860f81374cfd0025",
    "generated/e2-r17-theory-correction-mixed-pool-20260828.json": "1ca596bbf27e18fe34e1f2515fa99eea8e6dfbff500568d6cc2bf6c452a5e360"
  },
  "expected_resolved_model": "kimi-k3",
  "experiment_authority": false,
  "exposed_to_other_review": false,
  "get_poll_recovery": false,
  "hidden_provider_retry_used": false,
  "independent": true,
  "max_output_tokens": 6000,
  "missing_required_fields": [],
  "paper_promotion_authority": false,
  "parse_valid": true,
  "plan_sha256": "3a620eb791b2515b8498d9313698c51a50d59a0b03fb1684379b535e3a73ff08",
  "poll_count": 0,
  "prompt_path": "generated/e2-r17-experiment-plan-v2-review-20260828/kimi-k3-prompt.md",
  "prompt_sha256": "7909828d73e149a45809ecf56ca85b5fb6da5a4962e61edb725e4b14513f7503",
  "provider_generation_attempts": 1,
  "provider_retry_limit": 0,
  "provider_status": "completed",
  "raw_text": "{\n  \"plan_sha256_acknowledged\": \"3a620eb791b2515b8498d9313698c51a50d59a0b03fb1684379b535e3a73ff08\",\n  \"verdict\": \"REVISE_V2_BEFORE_PILOT\",\n  \"novelty_against_reasoningbank\": \"The V2 theory correction successfully carves out a defensible niche: ReasoningBank learns from successes and failures broadly, whereas E2-R17 tests whether the acting selector's censoring of same-pool failures specifically harms future skill via a budget-matched, exact-same-pool intervention. However, the novelty claim remains fragile because the MRW contrast (winner vs. lowest-index failed nonwinner) is still vulnerable to the critique that it merely instantiates a specific case of 'failure helps' rather than establishing a general compute-shielding law. The candidate claim is distinct only if E1 demonstrates that the shielding effect (M_K) and the diagnostic value (delta_K) are separable and that delta_K is nonzero specifically due to the censoring mechanism, not just because failure information is generically useful.\",\n  \"theory_estimand_assessment\": \"The factorization Delta_K = M_K * delta_K is causally valid under the stated cloned-stream design because MRW and WIN are identical on non-mixed pools by construction, making the mixed-pool event the correct treatment-support quantity. The design correctly identifies that rescue censoring (acting gain) and mixed-pool support (learning intervention support) are distinct. However, the causal identification of delta_K relies on the assumption that the updater treats the failed nonwinner evidence exchangeably with winner evidence conditional on the rendering policy; if the updater has prior biases toward failure text, the estimand captures an updater-evidence interaction rather than pure search-projection censoring.\",\n  \"historical_e0_preservation_assessment\": \"The preservation of the E0 HOLD decision while superseding the rescue-count gate for future E1 support is methodologically sound and avoids post-hoc rewriting. The distinction between the acting-side rescue identity (V_pre - V_winner) and the learning-side mixed-pool support (M_K) is clearly articulated. The old 42-task rescue-quota tranche is correctly deprecated. This maintains the integrity of the frozen E0 receipts while allowing the theory to evolve.\",\n  \"mixed_support_gate_assessment\": \"The thresholds (24/96 mixed pools, 8/12 exposed streams, 4/6 families) are pragmatically defensible but lack a formal power analysis linking them to the detectability of delta_K. The planning reference using i.i.d. assumptions (q=0.2 to 0.5) suggests the gate is achievable, but the choice of 24/96 (25%) and 8/12 (67%) appears arbitrary rather than derived from a minimum detectable effect size calculation. The gate should be justified by a predeclared support rule based on the desired precision for estimating delta_K, not just face-valid coverage.\",\n  \"stream_unit_and_statistics_assessment\": \"The 12 paired streams with 18 common held-out probes is a valid independent-unit design; the streams are the independent experimental units, and the probes are repeated measures to reduce variance, avoiding pseudoreplication. The exact 2^12 sign-flip test (4096 assignments) is valid for testing the null hypothesis of no effect across the 12 paired units. However, with only 12 streams, the test has limited power to detect small effects, and the family-stratified analysis (2 streams/family) is underpowered for standalone claims, which the plan correctly acknowledges.\",\n  \"equivalence_stop_rule_assessment\": \"The +/-1/18 (5.56 percentage points) equivalence margin is scientifically defensible as a practical equivalence bound corresponding to one held-out probe success per stream, but it is wide relative to typical subtle learning effects. The distinction between qualified STOP (equivalence established) and underpowered HOLD (interval spans zero and the margin) is correctly maintained. However, the margin should be justified by a predeclared clinical/practical significance argument rather than just the granularity of the probe set.\",\n  \"evidence_token_budget_assessment\": \"The one-slot WIN vs MRW contrast is vulnerable to confounding by evidence-token length or truncation if failed trajectories are systematically longer or shorter than winners. The plan correctly identifies this risk and proposes freezing either a deterministic common-window renderer or a raw-plus-matched-window secondary arm before the runtime Pilot. This is the cleanest repair: the common-window renderer ensures that any observed delta_K is attributable to content (failure vs. success) rather than differential information quantity.\",\n  \"published_baseline_fidelity_assessment\": \"The baseline hierarchy is fair and current, correctly elevating ReasoningBank/MaTTS, PolySkill, ACE, and AWM as headline published baselines while relegating arXiv-only works to related context. The implementation caveats for ReasoningBank (potential bug in pipeline_scaling.py where only the final results directory is passed to induction) and PolySkill (clean-room re-release vs. original internal infrastructure) are handled honestly and transparently. The two-lane approach (source-faithful vs. unified rerun) is necessary given the lack of a common published model.\",\n  \"source_faithful_vs_unified_lane_assessment\": \"Splitting source-faithful reproduction from unified reruns is necessary and sufficient to avoid false claims of a common published model. The current Ark-only credential availability (blocking Gemini, OpenAI, Anthropic, and SambaNova source-lane endpoints) is a source-lane blocker, not a fatal blocker for the entire program, because the unified rerun lane can proceed with available models (DeepSeek, Qwen, Kimi) while source-faithful lanes are documented as pending credential availability.\",\n  \"benchmark_selection_assessment\": \"WebArena as primary and AppWorld as secondary are appropriate given the published baseline implementations (ReasoningBank, PolySkill, AWM on WebArena; ACE, SAGE on AppWorld). SpreadsheetBench Verified-400 should remain additional rather than headline-only because it is the mechanism-identification substrate; using it as the sole headline benchmark would conflate mechanism validation with literature comparison.\",\n  \"model_selection_assessment\": \"V2 correctly avoids pretending that Qwen or DeepSeek are common published models across all baselines. The two-lane structure explicitly separates source-faithful models (Gemini-2.5-Flash, GPT-4o, etc.) from unified rerun candidates (Qwen, DeepSeek V4-Pro, Kimi K3). Model selection for the unified lane is outcome-blind and based on capability spread and availability, not on pretending these are the models used in the original baseline papers.\",\n  \"checkpoint_resume_assessment\": \"The checkpoint policy (persist immediately, raw immutable, summary rebuildable, missing-unit resume only, no relaunch after 502 without inspection) is sufficient to ensure reproducibility and prevent data loss. The prohibition on task/pool replacement after observing support is critical for maintaining the outcome-blind integrity of the support gate.\",\n  \"budget_assessment\": \"The budget ceilings (768 actor rollouts for E1-A, reference to E0 empirical rates) are reasonable planning references. However, the plan lacks a predeclared power analysis justifying the 12-stream, 96-task sample size in terms of the minimum detectable delta_K. The budget should be tied to the precision required for the equivalence test and the sign-flip test.\",\n  \"fatal_or_blocking_issues\": [\n    {\n      \"priority\": \"P1\",\n      \"issue\": \"Support gate thresholds lack formal statistical justification\",\n      \"why_blocking\": \"The 24/96, 8/12, and 4/6 thresholds appear arbitrary and are not derived from a power analysis or minimum detectable effect size calculation for delta_K. This weakens the predeclared nature of the support rule.\",\n      \"exact_v3_repair\": \"Replace the ad-hoc thresholds with a predeclared support rule derived from a power analysis: specify the minimum number of mixed pools required to detect a delta_K of a specified magnitude (e.g., 0.1) with 80% power at alpha=0.05, given the 12-stream design, and set the pool/stream/family thresholds accordingly.\"\n    },\n    {\n      \"priority\": \"P1\",\n      \"issue\": \"ReasoningBank implementation caveat unresolved\",\n      \"why_blocking\": \"The identified bug in the pinned ReasoningBank WebArena pipeline (passing only the final results directory to induce_scaling.py) must be adjudicated before any source-faithful reproduction or unified rerun comparison to ensure the baseline is implemented correctly.\",\n      \"exact_v3_repair\": \"Before any runtime Pilot, execute a source-semantic validation of the ReasoningBank adapter: either confirm the bug exists and patch it with a separately named adapter SHA, or confirm the intended behavior and document the adjudication. This must be completed before any E1 scientific execution.\"\n    },\n    {\n      \"priority\": \"P1\",\n      \"issue\": \"Evidence-token budget policy not yet frozen\",\n      \"why_blocking\": \"The choice between the deterministic common-window renderer and the raw-plus-matched-window approach must be frozen before the runtime Pilot to prevent post-hoc selection based on Pilot outcomes.\",\n      \"exact_v3_repair\": \"Amend V3 to mandate that the runtime Pilot must freeze the evidence-budget policy (common-window renderer vs. raw-plus-robustness) before any E1 pool generation, and that this policy is immutable for the E1-B primary contrast.\"\n    }\n  ],\n  \"required_v3_changes\": [\n    {\n      \"priority\": \"P1\",\n      \"target\": \"e1_a_support_phase.support_gate_for_review\",\n      \"change\": \"Replace the fixed thresholds (24/96, 8/12, 4/6) with a power-analysis-derived rule specifying the minimum mixed-pool count required to detect a predeclared minimum delta_K with specified power, and adjust stream/family coverage requirements accordingly.\",\n      \"verdict_relevance\": \"Ensures the support gate is statistically principled rather than arbitrary, strengthening the predeclared nature of the experiment.\"\n    },\n    {\n      \"priority\": \"P1\",\n      \"target\": \"published_baselines.headline[0].implementation_caveat\",\n      \"change\": \"Add a mandatory pre-Pilot step: adjudicate the ReasoningBank pipeline_scaling.py bug by either (a) confirming the bug and creating a patched adapter with a new SHA labeled 'source-faithful-adapter', or (b) documenting why the behavior is correct as-is.\",\n      \"verdict_relevance\": \"Prevents contamination of the primary collision baseline by an implementation artifact.\"\n    },\n    {\n      \"priority\": \"P1\",\n      \"target\": \"evidence_budget_policy\",\n      \"change\": \"Change status from 'MUST_BE_FROZEN_AFTER_RUNTIME_PILOT' to 'MUST_BE_FROZEN_BEFORE_RUNTIME_PILOT', and require the Pilot to validate the chosen renderer without altering it.\",\n      \"verdict_relevance\": \"Eliminates the risk of post-hoc evidence-budget selection based on Pilot results.\"\n    },\n    {\n      \"priority\": \"P2\",\n      \"target\": \"e1_b_primary.statistics\",\n      \"change\": \"Add a sensitivity analysis for the equivalence margin: report results for +/-1/18 and a narrower margin (e.g., +/-1/36) to assess robustness of the STOP/HOLD decision to the margin choice.\",\n      \"verdict_relevance\": \"Strengthens the scientific defensibility of the equivalence stop rule.\"\n    },\n    {\n      \"priority\": \"P2\",\n      \"target\": \"e1_c_diagnosis_after_primary_go_only\",\n      \"change\": \"Predeclare that the ReasoningBank-style aggregation diagnostic must use the adjudicated/patched adapter from the source-faithful lane, not the raw pinned commit, if the bug is confirmed.\",\n      \"verdict_relevance\": \"Ensures diagnostic controls are comparable to the headline baseline.\"\n    }\n  ],\n  \"nonblocking_improvements\": [\n    \"Add a predeclared analysis for heterogeneity of delta_K across failure families, even if underpowered, to inform E3 prospective prediction.\",\n    \"Include a null-control arm where the updater receives a success nonwinner on mixed pools to distinguish failure-specific value from generic nonwinner diversity.\",\n    \"Document the exact token-counting procedure for the evidence-budget audit to ensure reproducibility.\",\n    \"Add a requirement to report the distribution of mixed-pool counts per stream to verify the support gate assumptions.\"\n  ],\n  \"runtime_pilot_recommendation\": \"HOLD\",\n  \"e1_pool_support_phase_recommendation\": \"ALLOW_ONLY_AFTER_V3_CONTRACT\",\n  \"e1_updater_recommendation\": \"HOLD_UNTIL_SUPPORT_GATE_AND_V3\",\n  \"paper_claim_authority\": false,\n  \"single_sentence_verdict\": \"V2 successfully corrects the theory and preserves E0 integrity, but requires V3 amendments to statistically justify the support gate, adjudicate the ReasoningBank implementation caveat, and freeze the evidence-budget policy before any runtime Pilot or E1 execution.\"\n}",
  "raw_text_sha256": "6da8d73c0fce66d801eb77a8a49a9bef768b6b822ac120e01a0c2b76f76624f4",
  "requested_model": "kimi-k3",
  "resolved_model": "kimi-k3",
  "resolved_model_matches_qualification": true,
  "response_id_sha256": "60195631734216c8539ed73f345d4923345bdbac2c9d5d3c2c9f0e3836943a20",
  "review": {
    "benchmark_selection_assessment": "WebArena as primary and AppWorld as secondary are appropriate given the published baseline implementations (ReasoningBank, PolySkill, AWM on WebArena; ACE, SAGE on AppWorld). SpreadsheetBench Verified-400 should remain additional rather than headline-only because it is the mechanism-identification substrate; using it as the sole headline benchmark would conflate mechanism validation with literature comparison.",
    "budget_assessment": "The budget ceilings (768 actor rollouts for E1-A, reference to E0 empirical rates) are reasonable planning references. However, the plan lacks a predeclared power analysis justifying the 12-stream, 96-task sample size in terms of the minimum detectable delta_K. The budget should be tied to the precision required for the equivalence test and the sign-flip test.",
    "checkpoint_resume_assessment": "The checkpoint policy (persist immediately, raw immutable, summary rebuildable, missing-unit resume only, no relaunch after 502 without inspection) is sufficient to ensure reproducibility and prevent data loss. The prohibition on task/pool replacement after observing support is critical for maintaining the outcome-blind integrity of the support gate.",
    "e1_pool_support_phase_recommendation": "ALLOW_ONLY_AFTER_V3_CONTRACT",
    "e1_updater_recommendation": "HOLD_UNTIL_SUPPORT_GATE_AND_V3",
    "equivalence_stop_rule_assessment": "The +/-1/18 (5.56 percentage points) equivalence margin is scientifically defensible as a practical equivalence bound corresponding to one held-out probe success per stream, but it is wide relative to typical subtle learning effects. The distinction between qualified STOP (equivalence established) and underpowered HOLD (interval spans zero and the margin) is correctly maintained. However, the margin should be justified by a predeclared clinical/practical significance argument rather than just the granularity of the probe set.",
    "evidence_token_budget_assessment": "The one-slot WIN vs MRW contrast is vulnerable to confounding by evidence-token length or truncation if failed trajectories are systematically longer or shorter than winners. The plan correctly identifies this risk and proposes freezing either a deterministic common-window renderer or a raw-plus-matched-window secondary arm before the runtime Pilot. This is the cleanest repair: the common-window renderer ensures that any observed delta_K is attributable to content (failure vs. success) rather than differential information quantity.",
    "fatal_or_blocking_issues": [
      {
        "exact_v3_repair": "Replace the ad-hoc thresholds with a predeclared support rule derived from a power analysis: specify the minimum number of mixed pools required to detect a delta_K of a specified magnitude (e.g., 0.1) with 80% power at alpha=0.05, given the 12-stream design, and set the pool/stream/family thresholds accordingly.",
        "issue": "Support gate thresholds lack formal statistical justification",
        "priority": "P1",
        "why_blocking": "The 24/96, 8/12, and 4/6 thresholds appear arbitrary and are not derived from a power analysis or minimum detectable effect size calculation for delta_K. This weakens the predeclared nature of the support rule."
      },
      {
        "exact_v3_repair": "Before any runtime Pilot, execute a source-semantic validation of the ReasoningBank adapter: either confirm the bug exists and patch it with a separately named adapter SHA, or confirm the intended behavior and document the adjudication. This must be completed before any E1 scientific execution.",
        "issue": "ReasoningBank implementation caveat unresolved",
        "priority": "P1",
        "why_blocking": "The identified bug in the pinned ReasoningBank WebArena pipeline (passing only the final results directory to induce_scaling.py) must be adjudicated before any source-faithful reproduction or unified rerun comparison to ensure the baseline is implemented correctly."
      },
      {
        "exact_v3_repair": "Amend V3 to mandate that the runtime Pilot must freeze the evidence-budget policy (common-window renderer vs. raw-plus-robustness) before any E1 pool generation, and that this policy is immutable for the E1-B primary contrast.",
        "issue": "Evidence-token budget policy not yet frozen",
        "priority": "P1",
        "why_blocking": "The choice between the deterministic common-window renderer and the raw-plus-matched-window approach must be frozen before the runtime Pilot to prevent post-hoc selection based on Pilot outcomes."
      }
    ],
    "historical_e0_preservation_assessment": "The preservation of the E0 HOLD decision while superseding the rescue-count gate for future E1 support is methodologically sound and avoids post-hoc rewriting. The distinction between the acting-side rescue identity (V_pre - V_winner) and the learning-side mixed-pool support (M_K) is clearly articulated. The old 42-task rescue-quota tranche is correctly deprecated. This maintains the integrity of the frozen E0 receipts while allowing the theory to evolve.",
    "mixed_support_gate_assessment": "The thresholds (24/96 mixed pools, 8/12 exposed streams, 4/6 families) are pragmatically defensible but lack a formal power analysis linking them to the detectability of delta_K. The planning reference using i.i.d. assumptions (q=0.2 to 0.5) suggests the gate is achievable, but the choice of 24/96 (25%) and 8/12 (67%) appears arbitrary rather than derived from a minimum detectable effect size calculation. The gate should be justified by a predeclared support rule based on the desired precision for estimating delta_K, not just face-valid coverage.",
    "model_selection_assessment": "V2 correctly avoids pretending that Qwen or DeepSeek are common published models across all baselines. The two-lane structure explicitly separates source-faithful models (Gemini-2.5-Flash, GPT-4o, etc.) from unified rerun candidates (Qwen, DeepSeek V4-Pro, Kimi K3). Model selection for the unified lane is outcome-blind and based on capability spread and availability, not on pretending these are the models used in the original baseline papers.",
    "nonblocking_improvements": [
      "Add a predeclared analysis for heterogeneity of delta_K across failure families, even if underpowered, to inform E3 prospective prediction.",
      "Include a null-control arm where the updater receives a success nonwinner on mixed pools to distinguish failure-specific value from generic nonwinner diversity.",
      "Document the exact token-counting procedure for the evidence-budget audit to ensure reproducibility.",
      "Add a requirement to report the distribution of mixed-pool counts per stream to verify the support gate assumptions."
    ],
    "novelty_against_reasoningbank": "The V2 theory correction successfully carves out a defensible niche: ReasoningBank learns from successes and failures broadly, whereas E2-R17 tests whether the acting selector's censoring of same-pool failures specifically harms future skill via a budget-matched, exact-same-pool intervention. However, the novelty claim remains fragile because the MRW contrast (winner vs. lowest-index failed nonwinner) is still vulnerable to the critique that it merely instantiates a specific case of 'failure helps' rather than establishing a general compute-shielding law. The candidate claim is distinct only if E1 demonstrates that the shielding effect (M_K) and the diagnostic value (delta_K) are separable and that delta_K is nonzero specifically due to the censoring mechanism, not just because failure information is generically useful.",
    "paper_claim_authority": false,
    "plan_sha256_acknowledged": "3a620eb791b2515b8498d9313698c51a50d59a0b03fb1684379b535e3a73ff08",
    "published_baseline_fidelity_assessment": "The baseline hierarchy is fair and current, correctly elevating ReasoningBank/MaTTS, PolySkill, ACE, and AWM as headline published baselines while relegating arXiv-only works to related context. The implementation caveats for ReasoningBank (potential bug in pipeline_scaling.py where only the final results directory is passed to induction) and PolySkill (clean-room re-release vs. original internal infrastructure) are handled honestly and transparently. The two-lane approach (source-faithful vs. unified rerun) is necessary given the lack of a common published model.",
    "required_v3_changes": [
      {
        "change": "Replace the fixed thresholds (24/96, 8/12, 4/6) with a power-analysis-derived rule specifying the minimum mixed-pool count required to detect a predeclared minimum delta_K with specified power, and adjust stream/family coverage requirements accordingly.",
        "priority": "P1",
        "target": "e1_a_support_phase.support_gate_for_review",
        "verdict_relevance": "Ensures the support gate is statistically principled rather than arbitrary, strengthening the predeclared nature of the experiment."
      },
      {
        "change": "Add a mandatory pre-Pilot step: adjudicate the ReasoningBank pipeline_scaling.py bug by either (a) confirming the bug and creating a patched adapter with a new SHA labeled 'source-faithful-adapter', or (b) documenting why the behavior is correct as-is.",
        "priority": "P1",
        "target": "published_baselines.headline[0].implementation_caveat",
        "verdict_relevance": "Prevents contamination of the primary collision baseline by an implementation artifact."
      },
      {
        "change": "Change status from 'MUST_BE_FROZEN_AFTER_RUNTIME_PILOT' to 'MUST_BE_FROZEN_BEFORE_RUNTIME_PILOT', and require the Pilot to validate the chosen renderer without altering it.",
        "priority": "P1",
        "target": "evidence_budget_policy",
        "verdict_relevance": "Eliminates the risk of post-hoc evidence-budget selection based on Pilot results."
      },
      {
        "change": "Add a sensitivity analysis for the equivalence margin: report results for +/-1/18 and a narrower margin (e.g., +/-1/36) to assess robustness of the STOP/HOLD decision to the margin choice.",
        "priority": "P2",
        "target": "e1_b_primary.statistics",
        "verdict_relevance": "Strengthens the scientific defensibility of the equivalence stop rule."
      },
      {
        "change": "Predeclare that the ReasoningBank-style aggregation diagnostic must use the adjudicated/patched adapter from the source-faithful lane, not the raw pinned commit, if the bug is confirmed.",
        "priority": "P2",
        "target": "e1_c_diagnosis_after_primary_go_only",
        "verdict_relevance": "Ensures diagnostic controls are comparable to the headline baseline."
      }
    ],
    "runtime_pilot_recommendation": "HOLD",
    "single_sentence_verdict": "V2 successfully corrects the theory and preserves E0 integrity, but requires V3 amendments to statistically justify the support gate, adjudicate the ReasoningBank implementation caveat, and freeze the evidence-budget policy before any runtime Pilot or E1 execution.",
    "source_faithful_vs_unified_lane_assessment": "Splitting source-faithful reproduction from unified reruns is necessary and sufficient to avoid false claims of a common published model. The current Ark-only credential availability (blocking Gemini, OpenAI, Anthropic, and SambaNova source-lane endpoints) is a source-lane blocker, not a fatal blocker for the entire program, because the unified rerun lane can proceed with available models (DeepSeek, Qwen, Kimi) while source-faithful lanes are documented as pending credential availability.",
    "stream_unit_and_statistics_assessment": "The 12 paired streams with 18 common held-out probes is a valid independent-unit design; the streams are the independent experimental units, and the probes are repeated measures to reduce variance, avoiding pseudoreplication. The exact 2^12 sign-flip test (4096 assignments) is valid for testing the null hypothesis of no effect across the 12 paired units. However, with only 12 streams, the test has limited power to detect small effects, and the family-stratified analysis (2 streams/family) is underpowered for standalone claims, which the plan correctly acknowledges.",
    "theory_estimand_assessment": "The factorization Delta_K = M_K * delta_K is causally valid under the stated cloned-stream design because MRW and WIN are identical on non-mixed pools by construction, making the mixed-pool event the correct treatment-support quantity. The design correctly identifies that rescue censoring (acting gain) and mixed-pool support (learning intervention support) are distinct. However, the causal identification of delta_K relies on the assumption that the updater treats the failed nonwinner evidence exchangeably with winner evidence conditional on the rendering policy; if the updater has prior biases toward failure text, the estimand captures an updater-evidence interaction rather than pure search-projection censoring.",
    "verdict": "REVISE_V2_BEFORE_PILOT"
  },
  "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
  "schema_version": "1.0",
  "scientific_authority": false,
  "status": "COMPLETED",
  "submission_authority": false,
  "temperature": 0,
  "thinking_requested": "disabled",
  "usage": {
    "input_tokens": 19351,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 2772,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 22123
  }
}


===== BOUND ARTIFACT: generated/e2-r17-theory-correction-mixed-pool-20260828.json =====
{
  "artifact_type": "e2-r17-theory-correction-mixed-pool",
  "schema_version": "1.0",
  "date": "2026-08-28",
  "status": "THEORY_CORRECTION_BEFORE_E1",
  "authority": {
    "planning_and_theory": true,
    "retroactive_e0_rewrite": false,
    "e1_scientific_experiment": false,
    "paper_promotion": false,
    "submission": false
  },
  "historical_e0": {
    "summary_sha256": "533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366",
    "historical_decision": "HOLD",
    "historical_gate": "at least 6 rescue tasks and >=3 families",
    "historical_decision_preserved": true
  },
  "correction": {
    "old_support_event": "precommitted rescue event: rollout0 fails and at least one later rollout succeeds",
    "new_e1_support_event": "mixed pool: at least one success and at least one failure in the exact generated K-pool",
    "why": "Rescue censoring exactly identifies acting gain relative to rollout0, but a failure-aware learning projection can differ from winner-only on any mixed pool, including pools where rollout0 itself succeeds.",
    "old_gate_status_for_future_e1": "SUPERSEDED",
    "retroactive_change_to_e0_receipts": false
  },
  "theory": {
    "rescue_identity": "A_K-A_1=P(Y_1=0,max_i Y_i=1)=V_pre(K)-V_winner(K)",
    "iid_rescue_mass": "Gamma_K(p)=(1-p)-(1-p)^K",
    "mixed_support": "M_K=P(min_i Y_i=0,max_i Y_i=1)",
    "iid_mixed_support": "M_K(p)=1-p^K-(1-p)^K",
    "iid_winner_failure": "W_K(p)=(1-p)^K",
    "iid_pool_failure_availability": "F_K(p)=1-p^K",
    "iid_hidden_failed_branch_count": "H_K(p)=K[(1-p)-(1-p)^K]",
    "nested_pool_monotonicity_without_iid": {
      "acting_success_A_K": "nondecreasing",
      "winner_visible_failure_W_K": "nonincreasing",
      "pool_failure_availability_F_K": "nondecreasing",
      "mixed_pool_support_M_K": "nondecreasing"
    },
    "asymptotic_iid_fixed_p_in_0_1": {
      "A_K": "->1",
      "W_K": "->0",
      "F_K": "->1",
      "M_K": "->1"
    }
  },
  "primary_projection_candidate": {
    "name": "mixed_rejected_witness",
    "acting_projection": "unchanged exact served winner",
    "learning_projection_on_nonmixed_pool": "same one-slot served winner as winner-only",
    "learning_projection_on_mixed_pool": "lowest-rollout-index failed nonwinner, deterministically precommitted",
    "extra_actor_calls": 0,
    "evidence_slot_count_vs_winner": "1 vs 1",
    "reason": "maximally clean exact-same-pool causal contrast without giving the treatment extra trajectories or extra actor compute"
  },
  "learning_factorization": {
    "equation": "Delta_K=M_K*delta_K",
    "delta_definition": "E[J(U(S,g_MRW(T_1:K)))-J(U(S,g_WIN(T_1:K))) | mixed pool]",
    "delta_positive_assumed": false,
    "delta_zero_interpretation": "evidence shielding exists but is learning-irrelevant; central mechanism STOP",
    "delta_negative_interpretation": "failed witness harms future skill; proposed repair rejected"
  },
  "frozen_e0_reinterpretation": {
    "k": 8,
    "acting_success": "12/12",
    "winner_visible_failure": "0/12",
    "mixed_pools": "8/12",
    "rescue_events": "1/12",
    "hidden_failed_nonwinner_trajectories": 16,
    "mixed_failure_families": "5/6",
    "conclusion": "The old rescue identity has sparse support, but the mixed-gated learning treatment has materially larger observed support."
  },
  "preliminary_v2_support_gate_for_review": {
    "streams": 12,
    "tasks_per_stream": 8,
    "k": 8,
    "freeze_all_pools_before_any_updater_call": true,
    "minimum_mixed_pools": "24/96",
    "minimum_exposed_streams": "8/12 streams with >=2 mixed pools",
    "minimum_failure_family_coverage": "4/6",
    "task_or_pool_replacement_after_support_observation": false,
    "failure_action": "STOP_BEFORE_UPDATER_AND_REDRAFT_UNDER_NEW_PROTOCOL"
  },
  "current_scientific_state": {
    "search_induced_visibility_shift": "SUPPORTED",
    "exact_rescue_identity": "SUPPORTED",
    "mixed_pool_compute_shielding_law": "THEORETICALLY_ESTABLISHED_E0_CONSISTENT",
    "positive_diagnostic_value_delta_K": "UNKNOWN",
    "winner_only_learning_regret": "UNKNOWN",
    "final_repair_method": "UNDECIDED"
  },
  "implementation": {
    "theory_module": "research_pipeline/e2_r17_search_projection_theory.py",
    "runner_module": "research_pipeline/e2_r17_search_projection_runner.py",
    "new_projection_enum": "MIXED_REJECTED_WITNESS",
    "old_REJECTED_WITNESS_semantics_preserved": true,
    "targeted_tests_passed": 20
  }
}


===== BOUND ARTIFACT: consultations/e2-r17-published-baseline-audit-v2-20260828.md =====
# E2-R17 Published Baseline Audit V2

Date: 2026-08-28
Status: **PUBLISHED_TOP_VENUE_BASELINE_SET_FROZEN_FOR_V2_REVIEW**
Scope: baseline selection and implementation fidelity only; no scientific outcome authority

## 1. Selection rule

The main E2-R17 quantitative baseline set must prioritize methods that satisfy all three conditions:

1. formally published at a top-tier peer-reviewed venue by 2026-08-28;
2. directly relevant to persistent agent memory / skill / context self-improvement;
3. an official or first-party implementation can be pinned and audited.

ArXiv-only works may remain in collision review and Related Work, but they do not occupy the headline baseline slots in the main effectiveness table.

This V2 rule supersedes the V1 baseline ranking that elevated SkillCAT, Branch2Skill, SkillOpt, and RethinkSkill before publication status was treated as a hard primary-baseline criterion. Their prior audits are preserved as historical artifacts; they are not deleted.

## 2. Frozen official implementation pins

All repositories below were actually resolved from their upstream repositories on 69 and shallow-cloned under:

`/data/wyt/e2-r17-search-projection/baselines/published/`

| Method | Venue | Official / first-party repository | Pinned HEAD | Current role |
|---|---|---|---|---|
| ReasoningBank / MaTTS | ICLR 2026 | `google-research/reasoning-bank` | `ed80611788292ea739f1effd31f16c53823b8a0d` | **Primary collision + main published baseline** |
| PolySkill | ICLR 2026 | `simonucl/PolySkill` | `fff8807d7501d93188f9f658f4d0af2f29f35c23` | **Main published skill-learning baseline** |
| ACE | ICLR 2026 | `ace-agent/ace` | `82709de050e1db6e6ef2f07bcb0393560b94992a` | **Main published context-evolution baseline** |
| ACE AppWorld companion | ICLR 2026 | `ace-agent/ace-appworld` | `928e86877d34cd10eaba159606386f93a1765090` | Source-faithful AppWorld harness |
| Agent Workflow Memory (AWM) | ICML 2025 | `zorazrw/agent-workflow-memory` | `8c0ff8cd11d648c8fceb99e4e42f37e3b75381b1` | **Canonical published workflow-memory anchor** |
| SAGE | ACL 2026 Long | `amazon-science/SAGE` | `3c9244e82244abb1adc5467ee601a03ba0f433a0` | Extended published parametric/skill-library baseline |

Primary venue sources:

- ReasoningBank: ICLR 2026 conference paper / poster; official Google Research repository.
- PolySkill: ICLR 2026 conference proceedings; code linked from the paper.
- ACE: ICLR 2026; project page and first-party repositories.
- AWM: ICML 2025, PMLR 267.
- SAGE: ACL 2026 Long Paper, ACL Anthology 2026.acl-long.69.

## 3. Method and implementation audit

### 3.1 ReasoningBank / MaTTS — ICLR 2026

**Scientific overlap.** ReasoningBank explicitly distills generalizable reasoning strategies from both successful and failed experiences. MaTTS further couples memory to test-time scaling: scaling produces diverse trajectories, including successes and failures, and those experiences are aggregated to improve memory. Therefore E2-R17 cannot claim novelty from any of the following statements:

- failed trajectories can be useful;
- success/failure contrast can improve memory;
- test-time scaling can produce learning signal;
- memory and test-time scaling can be combined.

**Published experiment axis.** The ICLR paper includes WebArena and software-engineering experiments. The official WebArena scaling launcher defaults to `gemini-2.5-flash`.

**Official code pin.** `ed80611788292ea739f1effd31f16c53823b8a0d`.

**Implementation audit finding that must be resolved before source-faithful reproduction.** At this pinned commit:

1. `WebArena/pipeline_scaling.py` launches `num_trials` parallel rollouts into `results_0`, ..., `results_{K-1}`.
2. After the loop, the memory-induction call passes only `--result_dir results_{i}`, where `i` is the final loop index, together with `--num_samples K`.
3. `WebArena/induce_scaling.py` loops over `num_samples`, but inside the loop sets `res_dir = args.result_dir` without varying the directory.

Thus the current public launcher appears capable of repeatedly reading one results directory instead of explicitly iterating over K distinct rollout directories. This is an **implementation-reproduction caveat**, not a claim that the published scientific result is invalid. E2-R17 must not silently patch the baseline and call the patched result “exact reproduction.” The adapter must first establish which public code path corresponds to the published MaTTS experiment; any repair must be separately named and provenance-bound.

**E2-R17 collision boundary.** The remaining defensible novelty is not “failure-aware memory.” It is the causal object:

`same generated pool -> acting projection -> updater-visible evidence distribution -> future frozen skill`,

with the served winner, actor calls, initial persistent state, updater, and held-out evaluation held fixed.

### 3.2 PolySkill — ICLR 2026

**Scientific object.** PolySkill learns reusable web-agent skills by separating an abstract skill goal from concrete site-specific implementations, targeting generalizable and compositional skills.

**Paper models exposed in the public harness.** The current repository lists:

- GPT-4.1,
- Claude-3.7-Sonnet,
- Qwen3-Coder-480B-A35B,
- GLM-4.5.

**Benchmarks.** WebArena and Mind2Web.

**Official code pin.** `fff8807d7501d93188f9f658f4d0af2f29f35c23`.

**Important fidelity caveat.** The repository explicitly states that the 2026-07 public code is a **clean-room re-release**: the original experiment infrastructure depended on internal systems and the public harness was rebuilt on BrowserGym + LiteLLM. Therefore it is first-party and runnable, but it is not byte-for-byte the original internal experiment harness. This caveat must appear in the reproduction manifest.

**Use in E2-R17.** Strong published skill-induction comparison on WebArena. It is not an exact-same-pool causal control because its scientific object is polymorphic skill abstraction rather than projection of a frozen search pool.

### 3.3 Agent Workflow Memory — ICML 2025

**Scientific object.** AWM induces reusable workflows from past examples/experiences and retrieves them for future web tasks. Online AWM learns from prior executions judged correct by an evaluator.

**Published WebArena model.** The ICML version reports `gpt-4o-2024-05-13` with temperature 0.0. The current public WebArena runner also defaults to `openai/gpt-4o`; workflow induction supports GPT-3.5/GPT-4/GPT-4o.

**Benchmarks.** WebArena and Mind2Web.

**Official code pin.** `8c0ff8cd11d648c8fceb99e4e42f37e3b75381b1`.

**Use in E2-R17.** Canonical success-workflow memory anchor. Particularly useful as a contrast against ReasoningBank because ReasoningBank itself treats AWM as a successful-routine memory baseline.

### 3.4 ACE — ICLR 2026

**Scientific object.** ACE treats context as an evolving playbook and updates it through Generator -> Reflector -> Curator roles using execution feedback, with incremental delta updates designed to avoid context collapse and brevity bias.

**First-party AppWorld implementation.** The pinned companion repository provides online/offline AppWorld adaptation/evaluation configs and source code.

At `928e86877d34cd10eaba159606386f93a1765090`, `experiments/configs/ACE_online_no_GT.jsonnet` explicitly configures all three roles — generator, reflector, curator — as:

`DeepSeek-V3.1` via the SambaNova provider, temperature 0.

**Use in E2-R17.** Main published context-evolution baseline on AppWorld. It is especially relevant to long-lived context learning but does not isolate an acting-selector-induced evidence-distribution intervention.

### 3.5 SAGE — ACL 2026 Long

**Scientific object.** SAGE uses Skill-Augmented GRPO, sequential rollout, accumulated skill libraries, and skill-integrated reward for parametric self-improvement on AppWorld.

**Published/public model substrate.** The released SFT config points to `Qwen/Qwen2.5-32B-Instruct`. The README states that the expert-experience dataset was generated with Claude 3.5 Sonnet V2. The full SAGE training recipe requires multi-node H100-scale compute; AppWorld evaluation deploys the trained model via vLLM.

**Official code pin.** `3c9244e82244abb1adc5467ee601a03ba0f433a0`.

**Use in E2-R17.** Extended published baseline for the AppWorld long-term self-improvement story. Because SAGE changes model weights and reward optimization, it should not be treated as a matched projection-only control in E1.

## 4. Main baseline hierarchy for V2

### Tier P1 — headline published baselines

1. **ReasoningBank / MaTTS (ICLR 2026)** — closest collision and mandatory main baseline.
2. **PolySkill (ICLR 2026)** — strong continual skill-learning baseline on WebArena.
3. **ACE (ICLR 2026)** — strong context-evolution baseline on AppWorld.
4. **AWM (ICML 2025)** — canonical workflow-memory anchor, especially valuable because ReasoningBank directly contrasts against successful-routine memory.

### Tier P2 — published extended baseline

5. **SAGE (ACL 2026 Long)** — parametric RL + skill library; use for external long-horizon comparison, not exact-same-pool E1.

### Tier C — collision / related work, not headline baseline

- SkillCAT — arXiv-only at current audit time.
- Branch2Skill — arXiv-only at current audit time.
- SkillOpt — arXiv-only at current audit time.
- RethinkSkill / Rethinking Self-Evolving Agent Skills — arXiv-only at current audit time.
- TSR — search/training/topology context; not a matched persistent-skill baseline.

These works may still alter novelty wording and ablation design. They should not be used to inflate the published-baseline count.

## 5. Consequence for benchmark selection

The published baseline set changes the preferred external-validation benchmarks.

### Controlled Spreadsheet suite

Keep for E0/E1 mechanism identification because the exact same-pool invariants, artifact verifier, and failure families are already qualified. It is **not** the primary literature-comparison environment.

### WebArena — primary published-baseline transport lane

ReasoningBank, PolySkill, and AWM all have first-party WebArena implementations. Therefore WebArena is the strongest environment for a unified published-baseline comparison.

Recommended headline WebArena set after runtime qualification:

- No persistent learning / base agent,
- AWM,
- ReasoningBank / MaTTS,
- PolySkill,
- Winner-only search memory,
- Mixed-Rejected-Witness,
- Full Pool,
- final simplest E2-R17 projection.

Not every method is required on every executor. Use source-faithful and unified lanes below.

### AppWorld — second published-baseline transport lane

ACE and SAGE have first-party AppWorld implementations. AppWorld provides a complementary context/skill-evolution domain and is preferable to using an arXiv-only benchmark as the sole second headline environment.

Recommended AppWorld set after runtime qualification:

- base agent,
- ACE,
- SAGE where compute/weight-update scope is feasible,
- Winner-only,
- Mixed-Rejected-Witness,
- Full Pool / final method.

SAGE can be reported as source-faithful published reference plus a feasible unified evaluation if full retraining is prohibitively expensive; published numbers must never be mixed into the unified rerun table as if directly comparable.

### SpreadsheetBench Verified-400

Retain as an additional public transport domain if budget allows because it is already tightly connected to the controlled mechanism substrate. It should no longer be the only headline comparison domain.

## 6. Model fairness must use two lanes

There is no single executor model shared by all headline published baselines:

- ReasoningBank WebArena default: Gemini-2.5-Flash;
- AWM published WebArena: GPT-4o-2024-05-13;
- PolySkill: GPT-4.1 / Claude-3.7-Sonnet / Qwen3-Coder-480B-A35B / GLM-4.5;
- ACE AppWorld: DeepSeek-V3.1 in the first-party config;
- SAGE: Qwen2.5-32B-Instruct base with Claude-3.5-Sonnet-V2 expert-data generation.

Pretending there is a “common published model” would create a false comparison axis. V2 therefore adopts two separate lanes.

### Lane A — source-faithful reproduction

For each published baseline, first reproduce/qualify its first-party environment with its stated model or the closest explicitly supported model. Record exact repository SHA, model identity, dataset version, and any deviation. These results answer: **does our local reproduction agree with the published method under its intended substrate?**

### Lane B — unified causal/effectiveness rerun

Choose one or more executor/updater configurations that all candidate methods can actually support, then rerun the methods under:

- same benchmark version,
- same task IDs,
- same base executor,
- same action/environment interface,
- same actor-call accounting,
- matched update/context budget where scientifically meaningful,
- same held-out evaluator.

These results answer: **under a matched substrate, which learning policy performs better?**

Source-faithful and unified results must never be merged into one ranking column.

## 7. Model-matrix implication

The old V1 “pin Qwen3.5-35B-A3B or Qwen3.6-35B-A3B” P0 issue came from an arXiv-led baseline set. After the user-mandated published-baseline correction, that exact release choice is no longer a scientifically privileged common axis.

Therefore V2 should not simply choose one of those two models to satisfy the obsolete V1 gate. Instead it must freeze a new model matrix after checking availability for the **published** source-faithful lanes and a separate unified rerun lane.

Candidate practical anchors for the unified lane may still include a qualified Qwen open model plus the already qualified DeepSeek family, but their role must be described as a matched rerun/capability-spread axis, not as “the model used by the strongest baselines.”

## 8. Fairness requirements for the eventual main tables

1. Do not paste literature-reported scores into the unified-rerun main table.
2. Keep a separate “reported literature results” table, explicitly non-comparable across models/budgets.
3. For unified reruns, match task IDs and environment revision.
4. For memory/context methods, report updater-visible evidence tokens and update calls.
5. For search methods, report generated trajectories and actor calls, not just served trajectories.
6. For parametric RL methods such as SAGE, separately report training compute; do not force false token-budget equivalence with context-only methods.
7. Record whether each baseline receives success-only, failure-only, full-pool, or summarized evidence.
8. Record whether the baseline changes acting behavior during evidence generation; this matters for exact-same-pool interpretation.
9. Any adapter/patch to official code receives its own SHA and a label such as `source-faithful-adapter`, never “official exact” unless no scientific semantics changed.

## 9. V2 decision

Published-baseline selection is now:

`ReasoningBank + PolySkill + ACE + AWM` as headline published methods, with `SAGE` extended.

The closest novelty threat is ReasoningBank. E2-R17 remains scientifically viable only if E1 establishes more than “failure experiences help”: it must causally identify selection-induced evidence shielding under an exact same-pool intervention and show a precommitted, budget-matched learning projection changes future frozen skill.


===== BOUND ARTIFACT: generated/e2-r17-published-baseline-audit-v2-20260828.json =====
{
  "artifact_type": "e2-r17-published-baseline-audit-v2",
  "schema_version": "1.0",
  "date": "2026-08-28",
  "status": "PUBLISHED_TOP_VENUE_BASELINE_SET_FROZEN_FOR_V2_REVIEW",
  "authority": {
    "planning": true,
    "baseline_selection": true,
    "runtime_pilot": false,
    "scientific_experiment": false,
    "paper_promotion": false,
    "submission": false
  },
  "selection_rule": {
    "top_peer_reviewed_venue_required_for_headline": true,
    "first_party_or_official_implementation_required": true,
    "arxiv_only_headline_baseline_allowed": false,
    "arxiv_only_related_work_allowed": true
  },
  "headline_published_baselines": [
    {
      "method": "ReasoningBank/MaTTS",
      "venue": "ICLR 2026",
      "repository": "https://github.com/google-research/reasoning-bank",
      "pinned_head": "ed80611788292ea739f1effd31f16c53823b8a0d",
      "benchmarks": ["WebArena", "SWE-Bench"],
      "published_or_public_model_anchor": ["gemini-2.5-flash"],
      "role": "PRIMARY_COLLISION_AND_HEADLINE_BASELINE",
      "failure_evidence": "explicitly distills from successful and failed trajectories",
      "same_pool_exact_causal_control": false,
      "implementation_caveat": "Pinned WebArena pipeline_scaling.py launches K results_i directories but passes only the final results_i directory to induce_scaling.py; induce_scaling.py loops num_samples without varying result_dir. Source-faithful reproduction requires adjudication before any adapter patch."
    },
    {
      "method": "PolySkill",
      "venue": "ICLR 2026",
      "repository": "https://github.com/simonucl/PolySkill",
      "pinned_head": "fff8807d7501d93188f9f658f4d0af2f29f35c23",
      "benchmarks": ["WebArena", "Mind2Web"],
      "published_or_public_model_anchor": ["gpt-4.1", "claude-3-7-sonnet-20250219", "qwen3-coder-480b-a35b", "glm-4.5"],
      "role": "HEADLINE_SKILL_LEARNING_BASELINE",
      "failure_evidence": "not the central scientific axis",
      "same_pool_exact_causal_control": false,
      "implementation_caveat": "Official repository states the 2026-07 public harness is a clean-room re-release rebuilt on BrowserGym + LiteLLM rather than the original internal experiment infrastructure."
    },
    {
      "method": "ACE",
      "venue": "ICLR 2026",
      "repository": "https://github.com/ace-agent/ace",
      "pinned_head": "82709de050e1db6e6ef2f07bcb0393560b94992a",
      "companion_repository": "https://github.com/ace-agent/ace-appworld",
      "companion_pinned_head": "928e86877d34cd10eaba159606386f93a1765090",
      "benchmarks": ["AppWorld"],
      "published_or_public_model_anchor": ["DeepSeek-V3.1"],
      "role": "HEADLINE_CONTEXT_EVOLUTION_BASELINE",
      "failure_evidence": "Reflector extracts lessons from execution successes/errors",
      "same_pool_exact_causal_control": false,
      "implementation_caveat": "First-party AppWorld online no-GT config uses DeepSeek-V3.1 via SambaNova for generator, reflector, and curator at temperature 0."
    },
    {
      "method": "Agent Workflow Memory",
      "venue": "ICML 2025",
      "repository": "https://github.com/zorazrw/agent-workflow-memory",
      "pinned_head": "8c0ff8cd11d648c8fceb99e4e42f37e3b75381b1",
      "benchmarks": ["WebArena", "Mind2Web"],
      "published_or_public_model_anchor": ["gpt-4o-2024-05-13"],
      "role": "CANONICAL_WORKFLOW_MEMORY_ANCHOR",
      "failure_evidence": "online workflow induction is centered on executions judged correct; ReasoningBank uses AWM as a successful-routine contrast",
      "same_pool_exact_causal_control": false,
      "implementation_caveat": null
    }
  ],
  "extended_published_baselines": [
    {
      "method": "SAGE",
      "venue": "ACL 2026 Long",
      "repository": "https://github.com/amazon-science/SAGE",
      "pinned_head": "3c9244e82244abb1adc5467ee601a03ba0f433a0",
      "benchmarks": ["AppWorld"],
      "published_or_public_model_anchor": ["Qwen/Qwen2.5-32B-Instruct"],
      "expert_data_teacher": "Claude 3.5 Sonnet V2",
      "role": "EXTENDED_PARAMETRIC_SKILL_LIBRARY_BASELINE",
      "same_pool_exact_causal_control": false,
      "compute_caveat": "Full training recipe requires multi-node H100-scale compute and changes model weights, so it is not a matched projection-only E1 control."
    }
  ],
  "collision_or_related_only": [
    "SkillCAT",
    "Branch2Skill",
    "SkillOpt",
    "RethinkSkill / Rethinking Self-Evolving Agent Skills",
    "TSR"
  ],
  "benchmark_recommendation": {
    "mechanism_identification": "controlled spreadsheet suite",
    "primary_external_published_baseline_lane": "WebArena",
    "secondary_external_published_baseline_lane": "AppWorld",
    "additional_transport_lane": "SpreadsheetBench Verified-400 if budget permits"
  },
  "model_fairness": {
    "single_common_published_model_exists": false,
    "policy": "two_lane",
    "source_faithful_lane": "use each published baseline's stated/supported model and first-party harness with exact deviations logged",
    "unified_rerun_lane": "rerun compatible methods under a common qualified executor/updater and identical benchmark/task/environment accounting",
    "merge_source_faithful_and_unified_rankings": false
  },
  "v1_model_gate_supersession": {
    "old_gate": "pin Qwen3.5-35B-A3B or Qwen3.6-35B-A3B as common published axis",
    "status": "SUPERSEDED_BY_PUBLISHED_BASELINE_SET_CHANGE",
    "reason": "The old common-Qwen axis was derived mainly from arXiv-only baseline choices and is not shared by the headline published baselines."
  },
  "novelty_boundary": {
    "cannot_claim": [
      "failed trajectories are useful",
      "success/failure contrast can improve memory",
      "test-time scaling can produce learning signal",
      "memory and test-time scaling can be combined"
    ],
    "candidate_claim": "selection-induced evidence shielding under exact same-pool acting/learning projection separation, followed by a budget-matched causal intervention and prospective regime prediction"
  }
}


===== BOUND ARTIFACT: research_pipeline/e2_r17_evidence_window.py =====
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import importlib.metadata
import json
from typing import Any, Mapping, Sequence


TOKENIZER_PACKAGE = "tiktoken"
TOKENIZER_VERSION = "0.11.0"
TOKENIZER_ENCODING = "cl100k_base"
DEFAULT_CAP_TOKENS = 3072
HEAD_FRACTION = 1.0 / 3.0


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_trajectory_text(payload: Mapping[str, Any]) -> str:
    """Render updater evidence while excluding execution/provenance boilerplate.

    The system message is common across arms and consumes budget without carrying
    branch-specific evidence, so it is excluded. User/assistant/tool messages and
    verifier outcome are kept. Provider receipts, paths, timing, and identifiers
    remain in immutable raw artifacts but are not shown to the updater.
    """
    messages = []
    for message in payload.get("messages") or []:
        if not isinstance(message, Mapping):
            continue
        if str(message.get("role") or "") == "system":
            continue
        messages.append(dict(message))
    evidence = {
        "messages": messages,
        "score": payload.get("score"),
        "score_message": payload.get("score_message"),
    }
    return json.dumps(evidence, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def select_head_tail(tokens: Sequence[int], budget: int, *, head_fraction: float = HEAD_FRACTION) -> list[int]:
    if budget < 1:
        raise ValueError("budget must be positive")
    if not 0.0 < head_fraction < 1.0:
        raise ValueError("head_fraction must lie in (0,1)")
    values = list(tokens)
    if len(values) <= budget:
        return values
    head = max(1, int(budget * head_fraction))
    tail = budget - head
    if tail < 1:
        return values[:budget]
    return values[:head] + values[-tail:]


@dataclass(frozen=True)
class MatchedWindowReceipt:
    tokenizer_package: str
    tokenizer_version: str
    tokenizer_encoding: str
    cap_tokens: int
    head_fraction: float
    left_raw_tokens: int
    right_raw_tokens: int
    matched_tokens: int
    left_rendered_sha256: str
    right_rendered_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MatchedEvidenceWindowRenderer:
    """Pairwise-match evidence length before an updater sees either branch.

    For each WIN/MRW pair the budget is

        min(cap_tokens, len(WIN), len(MRW)).

    Both trajectories are then rendered to exactly that many cl100k_base tokens
    using the same one-third-head / two-thirds-tail rule. No padding or extra
    semantic content is introduced. The pairwise budget is a deterministic
    function of the already frozen search pool and therefore cannot depend on a
    downstream learning outcome.
    """

    def __init__(self, *, cap_tokens: int = DEFAULT_CAP_TOKENS) -> None:
        if cap_tokens < 1:
            raise ValueError("cap_tokens must be positive")
        try:
            observed_version = importlib.metadata.version(TOKENIZER_PACKAGE)
        except importlib.metadata.PackageNotFoundError as exc:
            raise RuntimeError(
                f"{TOKENIZER_PACKAGE}=={TOKENIZER_VERSION} is required for the frozen E2-R17 evidence renderer"
            ) from exc
        if observed_version != TOKENIZER_VERSION:
            raise RuntimeError(
                f"frozen E2-R17 renderer requires {TOKENIZER_PACKAGE}=={TOKENIZER_VERSION}, observed {observed_version}"
            )
        import tiktoken  # type: ignore

        self.encoding = tiktoken.get_encoding(TOKENIZER_ENCODING)
        self.cap_tokens = int(cap_tokens)

    def render_pair(self, left_text: str, right_text: str) -> tuple[str, str, MatchedWindowReceipt]:
        left_tokens = self.encoding.encode(left_text)
        right_tokens = self.encoding.encode(right_text)
        matched = min(self.cap_tokens, len(left_tokens), len(right_tokens))
        if matched < 1:
            raise ValueError("both evidence texts must contain at least one token")
        left_window = select_head_tail(left_tokens, matched)
        right_window = select_head_tail(right_tokens, matched)
        if len(left_window) != matched or len(right_window) != matched:
            raise AssertionError("pairwise evidence window is not token matched")
        left_rendered = self.encoding.decode(left_window)
        right_rendered = self.encoding.decode(right_window)
        receipt = MatchedWindowReceipt(
            tokenizer_package=TOKENIZER_PACKAGE,
            tokenizer_version=TOKENIZER_VERSION,
            tokenizer_encoding=TOKENIZER_ENCODING,
            cap_tokens=self.cap_tokens,
            head_fraction=HEAD_FRACTION,
            left_raw_tokens=len(left_tokens),
            right_raw_tokens=len(right_tokens),
            matched_tokens=matched,
            left_rendered_sha256=sha256_text(left_rendered),
            right_rendered_sha256=sha256_text(right_rendered),
        )
        return left_rendered, right_rendered, receipt


===== BOUND ARTIFACT: research_pipeline/e2_r17_search_projection_theory.py =====
from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Iterable, Mapping, Sequence


BinaryOutcome = tuple[int, ...]
ScoreOutcome = tuple[float, ...]


@dataclass(frozen=True)
class BinaryProjectionStats:
    acting_k: float
    acting_precommitted: float
    visible_failure_precommitted: float
    visible_failure_winner: float
    rescue_censoring_mass: float

    @property
    def acting_gain(self) -> float:
        return self.acting_k - self.acting_precommitted

    @property
    def visibility_gap(self) -> float:
        return self.visible_failure_precommitted - self.visible_failure_winner


@dataclass(frozen=True)
class ContinuousProjectionStats:
    acting_gain: float
    integrated_threshold_censoring: float


@dataclass(frozen=True)
class BinaryEvidenceStats:
    """Evidence quantities induced by best-of-K winner selection.

    Binary outcomes use 1=success and 0=failure. The acting selector serves a
    successful trajectory whenever one exists. `winner_failure_visibility`
    measures the probability that winner-only learning observes failure.
    `pool_failure_availability` measures whether the generated pool contains any
    failed trajectory, and `mixed_pool_mass` measures whether the same pool
    contains both success and failure evidence.
    """

    acting_success: float
    winner_failure_visibility: float
    pool_failure_availability: float
    mixed_pool_mass: float


def _validate_distribution(items: Iterable[tuple[Sequence[float], float]]) -> list[tuple[tuple[float, ...], float]]:
    rows = [(tuple(float(v) for v in outcome), float(probability)) for outcome, probability in items]
    if not rows:
        raise ValueError("distribution must be non-empty")
    width = len(rows[0][0])
    if width < 1 or any(len(outcome) != width for outcome, _ in rows):
        raise ValueError("all outcomes must have the same positive width")
    if any(probability < 0 for _, probability in rows):
        raise ValueError("probabilities must be non-negative")
    total = sum(probability for _, probability in rows)
    if not isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-10):
        raise ValueError(f"probabilities must sum to one, observed {total}")
    return rows


def binary_projection_stats(joint: Mapping[BinaryOutcome, float]) -> BinaryProjectionStats:
    """Compute the exact rescue-censoring quantities for an arbitrary joint law.

    Rollout 0 is the precommitted rollout. No independence or exchangeability is
    assumed. The acting selector succeeds iff any rollout succeeds.
    """
    rows = _validate_distribution(joint.items())
    if any(any(value not in (0.0, 1.0) for value in outcome) for outcome, _ in rows):
        raise ValueError("binary outcomes must contain only zero or one")

    acting_k = sum(max(outcome) * probability for outcome, probability in rows)
    acting_pre = sum(outcome[0] * probability for outcome, probability in rows)
    visible_pre = sum((outcome[0] == 0.0) * probability for outcome, probability in rows)
    visible_win = sum((max(outcome) == 0.0) * probability for outcome, probability in rows)
    rescue = sum(
        (outcome[0] == 0.0 and max(outcome) == 1.0) * probability
        for outcome, probability in rows
    )
    return BinaryProjectionStats(
        acting_k=acting_k,
        acting_precommitted=acting_pre,
        visible_failure_precommitted=visible_pre,
        visible_failure_winner=visible_win,
        rescue_censoring_mass=rescue,
    )


def binary_evidence_stats(joint: Mapping[BinaryOutcome, float]) -> BinaryEvidenceStats:
    """Compute winner-visible and pool-available failure evidence exactly.

    No independence or exchangeability is assumed. For nested pools, the
    pointwise events imply that acting success and mixed-pool support are
    non-decreasing with K, while winner-visible failure is non-increasing.
    """
    rows = _validate_distribution(joint.items())
    if any(any(value not in (0.0, 1.0) for value in outcome) for outcome, _ in rows):
        raise ValueError("binary outcomes must contain only zero or one")

    acting = sum((max(outcome) == 1.0) * probability for outcome, probability in rows)
    winner_failure = sum((max(outcome) == 0.0) * probability for outcome, probability in rows)
    pool_failure = sum((min(outcome) == 0.0) * probability for outcome, probability in rows)
    mixed = sum(
        (min(outcome) == 0.0 and max(outcome) == 1.0) * probability
        for outcome, probability in rows
    )
    return BinaryEvidenceStats(
        acting_success=acting,
        winner_failure_visibility=winner_failure,
        pool_failure_availability=pool_failure,
        mixed_pool_mass=mixed,
    )


def gamma_iid(p: float, k: int) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return (1.0 - p) - (1.0 - p) ** k


def winner_failure_iid(p: float, k: int) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return (1.0 - p) ** k


def pool_failure_iid(p: float, k: int) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return 1.0 - p**k


def mixed_pool_iid(p: float, k: int) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return 1.0 - p**k - (1.0 - p) ** k


def hidden_failed_branch_count_iid(p: float, k: int) -> float:
    """Expected failed branches omitted when the served winner succeeds."""
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return k * ((1.0 - p) - (1.0 - p) ** k)


def p_star(k: int) -> float:
    if k <= 1:
        raise ValueError("an interior rescue-censoring peak requires k > 1")
    return 1.0 - k ** (-1.0 / (k - 1))


def continuous_projection_stats(
    support: Mapping[ScoreOutcome, float],
) -> ContinuousProjectionStats:
    """Verify the continuous layer-cake identity on a finite-support joint law.

    For each atom r, the threshold-censoring integral equals max(r)-r[0]
    exactly. Summing over atoms yields the population identity without any
    rollout-independence assumption.
    """
    rows = _validate_distribution(support.items())
    if any(any(value < 0.0 or value > 1.0 for value in outcome) for outcome, _ in rows):
        raise ValueError("scores must lie in [0, 1]")

    acting_gain = sum((max(outcome) - outcome[0]) * probability for outcome, probability in rows)
    integrated = sum(
        max(0.0, max(outcome) - outcome[0]) * probability
        for outcome, probability in rows
    )
    return ContinuousProjectionStats(
        acting_gain=acting_gain,
        integrated_threshold_censoring=integrated,
    )


def gated_projection_factorization(
    rows: Iterable[tuple[bool, float, float]],
) -> tuple[float, float, float]:
    """Return (ATE, event mass, conditional diagnostic advantage).

    Each row is (mixed_event, probability, future_value_difference). The
    alternative projection is required to equal winner-only outside the mixed
    event; this function rejects violations. Under that gate, ATE = mass * delta.
    """
    normalized = [(bool(mixed), float(prob), float(diff)) for mixed, prob, diff in rows]
    if not normalized:
        raise ValueError("rows must be non-empty")
    if any(prob < 0 for _, prob, _ in normalized):
        raise ValueError("probabilities must be non-negative")
    total = sum(prob for _, prob, _ in normalized)
    if not isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-10):
        raise ValueError("probabilities must sum to one")
    if any((not mixed) and not isclose(diff, 0.0, abs_tol=1e-12) for mixed, _, diff in normalized):
        raise ValueError("gated projections must be identical outside the mixed event")

    ate = sum(prob * diff for _, prob, diff in normalized)
    mass = sum(prob for mixed, prob, _ in normalized if mixed)
    delta = (
        sum(prob * diff for mixed, prob, diff in normalized if mixed) / mass
        if mass > 0
        else 0.0
    )
    return ate, mass, delta


===== BOUND ARTIFACT: research_pipeline/e2_r17_search_projection_runner.py =====
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable, Sequence


def canonical_sha256(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class ProjectionName(StrEnum):
    WINNER_ONLY = "winner_only"
    PRECOMMITTED_ALWAYS = "precommitted_always"
    REJECTED_WITNESS = "rejected_witness"
    MIXED_REJECTED_WITNESS = "mixed_rejected_witness"
    DUPLICATED_WINNER = "duplicated_winner"
    WINNER_RANDOM_NONWINNER = "winner_random_nonwinner"
    SKILLCAT_STYLE_CONTRAST = "skillcat_style_contrast"


@dataclass(frozen=True)
class TrajectoryRef:
    task_id: str
    rollout_index: int
    score: float
    trajectory_path: str
    trajectory_sha256: str
    input_sha256: str
    prompt_sha256: str
    skill_pre_sha256: str
    verifier_sha256: str
    requested_model: str
    resolved_model: str
    provider_call_id_sha256: str
    evidence_tokens: int
    technical_status: str = "COMPLETED"
    failure_code: str | None = None

    def validate(self) -> None:
        if self.rollout_index < 0:
            raise ValueError("rollout_index must be non-negative")
        if self.score not in (0.0, 1.0):
            raise ValueError("R4 primary verifier score must be binary")
        if self.evidence_tokens < 0:
            raise ValueError("evidence_tokens must be non-negative")
        if self.technical_status != "COMPLETED":
            raise ValueError("technical-incomplete trajectories cannot enter a frozen pool")
        for name in (
            "trajectory_sha256",
            "input_sha256",
            "prompt_sha256",
            "skill_pre_sha256",
            "verifier_sha256",
            "provider_call_id_sha256",
        ):
            value = getattr(self, name)
            if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise ValueError(f"{name} must be a lowercase SHA-256 hex digest")
        if not self.resolved_model:
            raise ValueError("resolved_model is required")


@dataclass(frozen=True)
class SearchPool:
    pool_id: str
    task_id: str
    k: int
    trajectories: tuple[TrajectoryRef, ...]
    search_topology: str = "parallel_best_of_k"

    def validate(self) -> None:
        if self.k < 1 or len(self.trajectories) != self.k:
            raise ValueError("pool cardinality must equal k")
        if self.search_topology != "parallel_best_of_k":
            raise ValueError("R4 primary pool topology is frozen to parallel_best_of_k")
        for trajectory in self.trajectories:
            trajectory.validate()
        indices = [trajectory.rollout_index for trajectory in self.trajectories]
        if indices != list(range(self.k)):
            raise ValueError("trajectory indices must be ordered and equal 0..k-1")
        invariant_fields = (
            "task_id",
            "input_sha256",
            "prompt_sha256",
            "skill_pre_sha256",
            "verifier_sha256",
            "requested_model",
            "resolved_model",
        )
        for field in invariant_fields:
            values = {getattr(trajectory, field) for trajectory in self.trajectories}
            if len(values) != 1:
                raise ValueError(f"pool invariant violated: {field}")
        if self.trajectories[0].task_id != self.task_id:
            raise ValueError("pool task_id does not match trajectories")
        expected_id = canonical_sha256(
            {
                "task_id": self.task_id,
                "k": self.k,
                "topology": self.search_topology,
                "trajectory_sha256": [trajectory.trajectory_sha256 for trajectory in self.trajectories],
            }
        )
        if self.pool_id != expected_id:
            raise ValueError("pool_id is not content-addressed to the exact pool")

    @classmethod
    def freeze(cls, trajectories: Sequence[TrajectoryRef]) -> "SearchPool":
        if not trajectories:
            raise ValueError("cannot freeze an empty pool")
        ordered = tuple(sorted(trajectories, key=lambda row: row.rollout_index))
        task_id = ordered[0].task_id
        k = len(ordered)
        pool_id = canonical_sha256(
            {
                "task_id": task_id,
                "k": k,
                "topology": "parallel_best_of_k",
                "trajectory_sha256": [trajectory.trajectory_sha256 for trajectory in ordered],
            }
        )
        pool = cls(pool_id=pool_id, task_id=task_id, k=k, trajectories=ordered)
        pool.validate()
        return pool

    @property
    def precommitted(self) -> TrajectoryRef:
        return self.trajectories[0]

    @property
    def winner(self) -> TrajectoryRef:
        # Frozen selector: maximum binary verifier score, then lowest rollout index.
        return min(self.trajectories, key=lambda row: (-row.score, row.rollout_index))

    @property
    def acting_success(self) -> float:
        return self.winner.score

    @property
    def precommitted_success(self) -> float:
        return self.precommitted.score

    @property
    def rescue_event(self) -> bool:
        return self.precommitted.score == 0.0 and self.winner.score == 1.0

    @property
    def rescue_censoring_mass(self) -> float:
        return float(self.rescue_event)

    @property
    def mixed_pool(self) -> bool:
        scores = {trajectory.score for trajectory in self.trajectories}
        return scores == {0.0, 1.0}

    @property
    def first_failed_nonwinner(self) -> TrajectoryRef:
        if not self.mixed_pool:
            raise ValueError("a failed non-winner exists only on mixed pools")
        failures = [
            trajectory
            for trajectory in self.trajectories
            if trajectory.score == 0.0 and trajectory.rollout_index != self.winner.rollout_index
        ]
        if not failures:
            raise ValueError("mixed pool does not contain a failed non-winner")
        return min(failures, key=lambda row: row.rollout_index)


@dataclass(frozen=True)
class EvidenceSlot:
    role: str
    rollout_index: int
    trajectory_sha256: str
    score: float
    trajectory_path: str
    evidence_tokens: int


@dataclass(frozen=True)
class ProjectionPacket:
    projection: ProjectionName
    pool_id: str
    task_id: str
    acting_winner_index: int
    acting_winner_sha256: str
    rescue_event: bool
    slots: tuple[EvidenceSlot, ...]
    rule_version: str
    randomization_salt: str | None = None

    @property
    def packet_sha256(self) -> str:
        return canonical_sha256(asdict(self))

    @property
    def selected_indices(self) -> tuple[int, ...]:
        return tuple(slot.rollout_index for slot in self.slots)

    @property
    def total_evidence_tokens(self) -> int:
        return sum(slot.evidence_tokens for slot in self.slots)


def _slot(role: str, trajectory: TrajectoryRef) -> EvidenceSlot:
    return EvidenceSlot(
        role=role,
        rollout_index=trajectory.rollout_index,
        trajectory_sha256=trajectory.trajectory_sha256,
        score=trajectory.score,
        trajectory_path=trajectory.trajectory_path,
        evidence_tokens=trajectory.evidence_tokens,
    )


def _random_nonwinner(pool: SearchPool, salt: str) -> TrajectoryRef:
    candidates = [trajectory for trajectory in pool.trajectories if trajectory.rollout_index != pool.winner.rollout_index]
    if not candidates:
        return pool.winner
    digest = hashlib.sha256(f"{salt}|{pool.pool_id}".encode("utf-8")).hexdigest()
    return candidates[int(digest[:16], 16) % len(candidates)]


def project(
    pool: SearchPool,
    projection: ProjectionName,
    *,
    randomization_salt: str = "e2-r17-r4-random-nonwinner-v1",
) -> ProjectionPacket:
    pool.validate()
    winner = pool.winner
    precommitted = pool.precommitted
    if projection is ProjectionName.WINNER_ONLY:
        slots = (_slot("served_winner", winner),)
        salt = None
    elif projection is ProjectionName.PRECOMMITTED_ALWAYS:
        slots = (_slot("precommitted_rollout_0", precommitted),)
        salt = None
    elif projection is ProjectionName.REJECTED_WITNESS:
        selected = precommitted if pool.rescue_event else winner
        role = "precommitted_rejected_failure" if pool.rescue_event else "served_winner_outside_rescue"
        slots = (_slot(role, selected),)
        salt = None
    elif projection is ProjectionName.MIXED_REJECTED_WITNESS:
        selected = pool.first_failed_nonwinner if pool.mixed_pool else winner
        role = "first_failed_nonwinner" if pool.mixed_pool else "served_winner_outside_mixed_pool"
        slots = (_slot(role, selected),)
        salt = None
    elif projection is ProjectionName.DUPLICATED_WINNER:
        slots = (_slot("served_winner_slot_1", winner), _slot("served_winner_slot_2", winner))
        salt = None
    elif projection is ProjectionName.WINNER_RANDOM_NONWINNER:
        random_nonwinner = _random_nonwinner(pool, randomization_salt)
        slots = (_slot("served_winner", winner), _slot("hash_selected_nonwinner", random_nonwinner))
        salt = randomization_salt
    elif projection is ProjectionName.SKILLCAT_STYLE_CONTRAST:
        # This freezes only the source trajectory pair. Any generated contrastive
        # summary is a downstream updater artifact and must retain both source SHAs.
        contrast = precommitted if pool.rescue_event else winner
        second_role = "precommitted_rejected_failure" if pool.rescue_event else "duplicated_winner_outside_rescue"
        slots = (_slot("served_winner", winner), _slot(second_role, contrast))
        salt = None
    else:  # pragma: no cover - StrEnum exhaustiveness guard
        raise ValueError(f"unsupported projection: {projection}")
    packet = ProjectionPacket(
        projection=projection,
        pool_id=pool.pool_id,
        task_id=pool.task_id,
        acting_winner_index=winner.rollout_index,
        acting_winner_sha256=winner.trajectory_sha256,
        rescue_event=pool.rescue_event,
        slots=slots,
        rule_version="E2-R17-R4-PROJECTION-V1",
        randomization_salt=salt,
    )
    validate_packet(pool, packet)
    return packet


def validate_packet(pool: SearchPool, packet: ProjectionPacket) -> None:
    pool.validate()
    if packet.pool_id != pool.pool_id or packet.task_id != pool.task_id:
        raise ValueError("projection packet is not bound to the exact pool")
    if packet.acting_winner_index != pool.winner.rollout_index:
        raise ValueError("acting winner changed across learning projections")
    if packet.acting_winner_sha256 != pool.winner.trajectory_sha256:
        raise ValueError("acting winner SHA changed across learning projections")
    if packet.rescue_event != pool.rescue_event:
        raise ValueError("rescue-event flag mismatch")
    by_index = {trajectory.rollout_index: trajectory for trajectory in pool.trajectories}
    for slot in packet.slots:
        source = by_index.get(slot.rollout_index)
        if source is None or source.trajectory_sha256 != slot.trajectory_sha256:
            raise ValueError("projection introduced evidence outside the frozen pool")
        if source.score != slot.score or source.trajectory_path != slot.trajectory_path:
            raise ValueError("projection slot altered source trajectory metadata")
    if packet.projection is ProjectionName.REJECTED_WITNESS:
        expected = pool.precommitted if pool.rescue_event else pool.winner
        if packet.selected_indices != (expected.rollout_index,):
            raise ValueError("Rejected-Witness violates its event-gated precommitment")
        if pool.rescue_event and not (packet.slots[0].score == 0.0 and pool.winner.score == 1.0):
            raise ValueError("Rejected-Witness must expose a rejected failure only on rescue events")
    if packet.projection is ProjectionName.MIXED_REJECTED_WITNESS:
        expected = pool.first_failed_nonwinner if pool.mixed_pool else pool.winner
        if packet.selected_indices != (expected.rollout_index,):
            raise ValueError("Mixed-Rejected-Witness violates its deterministic mixed-pool rule")
        if pool.mixed_pool and packet.slots[0].score != 0.0:
            raise ValueError("Mixed-Rejected-Witness must expose a failed non-winner on mixed pools")
    if packet.projection is ProjectionName.DUPLICATED_WINNER:
        expected = (pool.winner.rollout_index, pool.winner.rollout_index)
        if packet.selected_indices != expected:
            raise ValueError("duplicated-winner packet is not an exact duplicate")


def validate_primary_cloned_pair(pool: SearchPool, winner_packet: ProjectionPacket, witness_packet: ProjectionPacket) -> None:
    validate_packet(pool, winner_packet)
    validate_packet(pool, witness_packet)
    if winner_packet.projection is not ProjectionName.WINNER_ONLY:
        raise ValueError("first packet must be winner-only")
    if witness_packet.projection is not ProjectionName.REJECTED_WITNESS:
        raise ValueError("second packet must be Rejected-Witness")
    if winner_packet.pool_id != witness_packet.pool_id:
        raise ValueError("cloned pair does not use the exact same pool")
    if winner_packet.acting_winner_sha256 != witness_packet.acting_winner_sha256:
        raise ValueError("acting winner differs between cloned arms")
    if not pool.rescue_event and winner_packet.selected_indices != witness_packet.selected_indices:
        raise ValueError("g_RW must equal g_WIN outside the rescue event")
    if pool.rescue_event and winner_packet.selected_indices == witness_packet.selected_indices:
        raise ValueError("g_RW must differ from g_WIN on the rescue event")


@dataclass(frozen=True)
class StreamProjection:
    stream_id: str
    initial_skill_sha256: str
    pools: tuple[SearchPool, ...]
    packets: tuple[ProjectionPacket, ...]
    projection: ProjectionName

    @property
    def stream_sha256(self) -> str:
        return canonical_sha256(
            {
                "stream_id": self.stream_id,
                "initial_skill_sha256": self.initial_skill_sha256,
                "pool_ids": [pool.pool_id for pool in self.pools],
                "packet_sha256": [packet.packet_sha256 for packet in self.packets],
                "projection": self.projection,
            }
        )


def project_stream(
    *,
    stream_id: str,
    initial_skill_sha256: str,
    pools: Sequence[SearchPool],
    projection: ProjectionName,
) -> StreamProjection:
    if len(initial_skill_sha256) != 64:
        raise ValueError("initial skill SHA-256 is required")
    if len(pools) != 8:
        raise ValueError("MindMemOS R4 updater batch is frozen to exactly 8 task pools")
    if len({pool.task_id for pool in pools}) != 8:
        raise ValueError("one evolution stream must contain eight distinct tasks")
    if any(pool.trajectories[0].skill_pre_sha256 != initial_skill_sha256 for pool in pools):
        raise ValueError("all pools must be generated from the exact initial skill state")
    packets = tuple(project(pool, projection) for pool in pools)
    return StreamProjection(
        stream_id=stream_id,
        initial_skill_sha256=initial_skill_sha256,
        pools=tuple(pools),
        packets=packets,
        projection=projection,
    )


def validate_mixed_cloned_pair(pool: SearchPool, winner_packet: ProjectionPacket, witness_packet: ProjectionPacket) -> None:
    validate_packet(pool, winner_packet)
    validate_packet(pool, witness_packet)
    if winner_packet.projection is not ProjectionName.WINNER_ONLY:
        raise ValueError("first packet must be winner-only")
    if witness_packet.projection is not ProjectionName.MIXED_REJECTED_WITNESS:
        raise ValueError("second packet must be Mixed-Rejected-Witness")
    if winner_packet.pool_id != witness_packet.pool_id:
        raise ValueError("cloned pair does not use the exact same pool")
    if winner_packet.acting_winner_sha256 != witness_packet.acting_winner_sha256:
        raise ValueError("acting winner differs between cloned arms")
    if not pool.mixed_pool and winner_packet.selected_indices != witness_packet.selected_indices:
        raise ValueError("g_MRW must equal g_WIN outside the mixed-pool event")
    if pool.mixed_pool and winner_packet.selected_indices == witness_packet.selected_indices:
        raise ValueError("g_MRW must differ from g_WIN on the mixed-pool event")


def validate_cloned_streams(winner: StreamProjection, witness: StreamProjection) -> None:
    if winner.stream_id != witness.stream_id or winner.initial_skill_sha256 != witness.initial_skill_sha256:
        raise ValueError("cloned streams are not cloned from the same unit")
    if winner.projection is not ProjectionName.WINNER_ONLY:
        raise ValueError("winner stream projection mismatch")
    if witness.projection is not ProjectionName.REJECTED_WITNESS:
        raise ValueError("witness stream projection mismatch")
    if [pool.pool_id for pool in winner.pools] != [pool.pool_id for pool in witness.pools]:
        raise ValueError("cloned streams do not share exact pool IDs")
    for pool, win_packet, rw_packet in zip(winner.pools, winner.packets, witness.packets):
        validate_primary_cloned_pair(pool, win_packet, rw_packet)


def validate_mixed_cloned_streams(winner: StreamProjection, witness: StreamProjection) -> None:
    if winner.stream_id != witness.stream_id or winner.initial_skill_sha256 != witness.initial_skill_sha256:
        raise ValueError("cloned streams are not cloned from the same unit")
    if winner.projection is not ProjectionName.WINNER_ONLY:
        raise ValueError("winner stream projection mismatch")
    if witness.projection is not ProjectionName.MIXED_REJECTED_WITNESS:
        raise ValueError("mixed-witness stream projection mismatch")
    if [pool.pool_id for pool in winner.pools] != [pool.pool_id for pool in witness.pools]:
        raise ValueError("cloned streams do not share exact pool IDs")
    for pool, win_packet, rw_packet in zip(winner.pools, winner.packets, witness.packets):
        validate_mixed_cloned_pair(pool, win_packet, rw_packet)


def write_stream_receipt(path: Path, stream: StreamProjection) -> None:
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-search-projection-stream-receipt",
        "stream_id": stream.stream_id,
        "stream_sha256": stream.stream_sha256,
        "initial_skill_sha256": stream.initial_skill_sha256,
        "projection": stream.projection,
        "pool_ids": [pool.pool_id for pool in stream.pools],
        "packets": [asdict(packet) | {"packet_sha256": packet.packet_sha256} for packet in stream.packets],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def pools_from_jsonl(path: Path) -> tuple[SearchPool, ...]:
    pools: list[SearchPool] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        trajectories = tuple(TrajectoryRef(**row) for row in payload["trajectories"])
        pool = SearchPool(
            pool_id=payload["pool_id"],
            task_id=payload["task_id"],
            k=payload["k"],
            trajectories=trajectories,
            search_topology=payload.get("search_topology", "parallel_best_of_k"),
        )
        pool.validate()
        pools.append(pool)
    return tuple(pools)


def append_pool_jsonl(path: Path, pool: SearchPool) -> None:
    pool.validate()
    payload = {
        "pool_id": pool.pool_id,
        "task_id": pool.task_id,
        "k": pool.k,
        "search_topology": pool.search_topology,
        "trajectories": [asdict(row) for row in pool.trajectories],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


===== BOUND ARTIFACT: research_pipeline/e2_r17_mindmemos_ark_adapter.py =====
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from research_pipeline.ark_provider import ArkResponseStateError, ArkResponsesClient, ArkSettings

PLAN_BASE_URL = "https://ark.cn-beijing.volces.com/api/plan/v3"
REQUESTED_MODEL = "deepseek-v4-pro"
# Historical default retained only for backward-compatible callers. Every new
# E2-R17 execution tranche must pass its freshly qualified resolved identity.
REQUIRED_RESOLVED_MODEL = "deepseek-v4-pro-260425"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _flatten_messages(messages: list[dict[str, Any]]) -> str:
    """Render MindMemOS chat messages into a deterministic Responses prompt.

    This adapter changes transport only. Role boundaries and content are preserved
    explicitly; SkillEvolver prompts, parsers, and update semantics remain first-party.
    """

    parts: list[str] = []
    for message in messages:
        role = str(message.get("role") or "user").upper()
        content = message.get("content")
        text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False, sort_keys=True)
        parts.append(f"<{role}>\n{text}\n</{role}>")
    return "\n".join(parts)


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def _safe_task_name(task: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", task).strip("-")
    return cleaned or "call"


@dataclass
class AdapterUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass
class AdapterChatResponse:
    finish_reason: str
    content: str
    model: str
    usage: AdapterUsage = field(default_factory=AdapterUsage)
    parsed: Any = None
    raw_response: dict[str, Any] = field(default_factory=dict)


@dataclass
class CallReceipt:
    call_index: int
    created_at_utc: str
    task: str
    attempt: int
    requested_model: str
    resolved_model: str
    prompt_sha256: str
    response_sha256: str
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    response_id_sha256: str
    provider_status: str
    thinking_requested: str | None
    temperature_requested: float
    provider_retry_limit: int
    message_count: int
    parse_error: str = ""
    record_path: str | None = None
    hidden_provider_retry_used: bool = False


class MindMemOSArkPlanChatAdapter:
    """Async MindMemOS ``LLMClient.chat`` adapter over Ark Plan Responses.

    Provider retries are disabled. Parse-correction attempts are explicit and are
    counted separately because they are part of the frozen SkillEvolver updater
    policy, not part of acting compute K. When ``record_dir`` is supplied, every
    updater call is written atomically with the full prompt and response text;
    raw provider response identifiers are never persisted.
    """

    def __init__(
        self,
        *,
        settings: ArkSettings | None = None,
        requested_model: str = REQUESTED_MODEL,
        required_resolved_model: str = REQUIRED_RESOLVED_MODEL,
        max_parse_attempts: int = 3,
        record_dir: Path | str | None = None,
    ) -> None:
        raw = settings or ArkSettings.from_env(required=True)
        if raw.base_url.rstrip("/") != PLAN_BASE_URL:
            raise RuntimeError("R17 adapter refuses non-Plan Ark route")
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
        self.max_parse_attempts = max(1, int(max_parse_attempts))
        self.record_dir = Path(record_dir) if record_dir is not None else None
        self.receipts: list[CallReceipt] = []

    async def chat(
        self,
        task: str,
        messages: list[dict[str, Any]],
        format_parser: Callable[[str], Any] | None = None,
        *,
        model: str | None = None,
        feedback_on_parse_error: bool = False,
        **kwargs: Any,
    ) -> AdapterChatResponse:
        target = model or self.requested_model
        convo = list(messages)
        max_attempts = self.max_parse_attempts if format_parser is not None else 1
        last_error: Exception | None = None
        for attempt in range(max_attempts):
            prompt = _flatten_messages(convo)
            result = self._respond(prompt, target=target, kwargs=kwargs)
            content = str(result.get("text") or "")
            resolved = str(result.get("resolved_model") or "")
            usage = result.get("usage") or {}
            receipt = CallReceipt(
                call_index=len(self.receipts),
                created_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                task=task,
                attempt=attempt,
                requested_model=target,
                resolved_model=resolved,
                prompt_sha256=_sha(prompt),
                response_sha256=_sha(content),
                prompt_tokens=usage.get("input_tokens"),
                completion_tokens=usage.get("output_tokens"),
                total_tokens=usage.get("total_tokens"),
                response_id_sha256=_sha(str(result.get("response_id") or "")),
                provider_status=str(result.get("status") or ""),
                thinking_requested=result.get("thinking_requested") or kwargs.get("thinking") or "disabled",
                temperature_requested=float(result.get("temperature_requested", 0.0)),
                provider_retry_limit=self.settings.max_retries,
                message_count=len(convo),
            )
            parsed: Any = None
            if format_parser is not None:
                try:
                    parsed = format_parser(content)
                except Exception as exc:
                    last_error = exc
                    receipt.parse_error = f"{type(exc).__name__}: {exc}"
                    self._persist_call(
                        receipt=receipt,
                        messages=convo,
                        prompt=prompt,
                        content=content,
                        result=result,
                        parser_applied=True,
                        parsed=None,
                    )
                    self.receipts.append(receipt)
                    if feedback_on_parse_error and attempt + 1 < max_attempts:
                        convo.append({"role": "assistant", "content": content})
                        convo.append(
                            {
                                "role": "user",
                                "content": (
                                    "Your previous reply could not be applied:\n"
                                    f"{exc}\n\nFix exactly that problem and resend the COMPLETE corrected output "
                                    "in the same format as before. Do not apologize or add commentary."
                                ),
                            }
                        )
                    continue
            self._persist_call(
                receipt=receipt,
                messages=convo,
                prompt=prompt,
                content=content,
                result=result,
                parser_applied=format_parser is not None,
                parsed=parsed,
            )
            self.receipts.append(receipt)
            if resolved != self.required_resolved_model:
                raise RuntimeError(
                    f"resolved-model-drift:requested={target};required={self.required_resolved_model};observed={resolved}"
                )
            return AdapterChatResponse(
                finish_reason=str(result.get("status") or "completed"),
                content=content,
                model=resolved,
                usage=AdapterUsage(
                    prompt_tokens=usage.get("input_tokens"),
                    completion_tokens=usage.get("output_tokens"),
                    total_tokens=usage.get("total_tokens"),
                ),
                parsed=parsed,
                raw_response={
                    "response_id_sha256": receipt.response_id_sha256,
                    "prompt_sha256": receipt.prompt_sha256,
                    "response_sha256": receipt.response_sha256,
                    "status": result.get("status"),
                    "thinking_requested": result.get("thinking_requested"),
                    "thinking_effective": result.get("thinking_effective"),
                    "record_path": receipt.record_path,
                },
            )
        assert last_error is not None
        raise last_error

    def _persist_call(
        self,
        *,
        receipt: CallReceipt,
        messages: list[dict[str, Any]],
        prompt: str,
        content: str,
        result: dict[str, Any],
        parser_applied: bool,
        parsed: Any,
    ) -> None:
        if self.record_dir is None:
            return
        filename = f"{receipt.call_index:03d}-{_safe_task_name(receipt.task)}-attempt{receipt.attempt}.json"
        path = self.record_dir / filename
        payload = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-mindmemos-updater-provider-call",
            "created_at_utc": receipt.created_at_utc,
            "task": receipt.task,
            "attempt": receipt.attempt,
            "messages": messages,
            "prompt": prompt,
            "prompt_sha256": receipt.prompt_sha256,
            "response_text": content,
            "response_sha256": receipt.response_sha256,
            "requested_model": receipt.requested_model,
            "resolved_model": receipt.resolved_model,
            "usage": result.get("usage") or {},
            "provider_status": result.get("status"),
            "response_id_sha256": receipt.response_id_sha256,
            "thinking_requested": result.get("thinking_requested") or receipt.thinking_requested,
            "thinking_effective": result.get("thinking_effective"),
            "temperature_requested": receipt.temperature_requested,
            "provider_retry_limit": self.settings.max_retries,
            "hidden_provider_retry_used": False,
            "parser_applied": parser_applied,
            "parse_error": receipt.parse_error,
            "parsed_type": type(parsed).__name__ if parsed is not None else None,
            "parsed_sha256": _sha(str(parsed)) if parsed is not None else None,
            "private_credentials_included": False,
            "raw_response_id_included": False,
        }
        _atomic_json(path, payload)
        receipt.record_path = str(path.resolve())

    def _respond(self, prompt: str, *, target: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        max_output_tokens = int(kwargs.get("max_tokens") or kwargs.get("max_completion_tokens") or 4096)
        temperature = kwargs.get("temperature")
        if temperature is None:
            # SkillEvolver's first-party summary/patch calls do not currently pass
            # an explicit temperature. Future E2-R17 causal tranches freeze that
            # otherwise provider-defined default to zero; historical receipts are
            # never regenerated under this rule.
            temperature = 0.0
        thinking = kwargs.get("thinking") or "disabled"
        try:
            result = self.client.respond(
                prompt,
                model=target,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
                thinking=thinking,
                allow_thinking_compatibility_fallback=False,
            )
            result["thinking_requested"] = thinking
            result["temperature_requested"] = float(temperature)
            result.setdefault("thinking_effective", thinking)
            return result
        except ArkResponseStateError as exc:
            if not exc.response_id:
                raise
            polled = self.client.poll_response(exc.response_id, max_polls=3, interval_seconds=1.0)
            if not polled.get("text"):
                raise
            return {
                "requested_model": target,
                "resolved_model": polled.get("resolved_model"),
                "text": polled.get("text"),
                "usage": polled.get("usage") or {},
                "response_id": polled.get("response_id") or exc.response_id,
                "status": polled.get("status"),
                "thinking_requested": thinking,
                "thinking_effective": thinking,
                "get_poll_recovery": True,
            }

    def public_receipts(self) -> list[dict[str, Any]]:
        return [asdict(receipt) for receipt in self.receipts]

    @property
    def receipt_bundle_sha256(self) -> str:
        raw = json.dumps(self.public_receipts(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return _sha(raw)


===== BOUND ARTIFACT: generated/e2-r17-experiment-plan-v3-model-identity-qualification-20260828.json =====
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
  "created_at_utc": "2026-08-28T08:53:55+00:00",
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
      "response_id_sha256": "aaaac6ac11b01dd6e658eb10a1d17db8fcff6f84dc59f10d64b6668c142d7d4c",
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
      "response_id_sha256": "40c72a1e745837bc95d9ec8df80f995490f16b1c6766ea97f1a569ae5f31b7ef",
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
