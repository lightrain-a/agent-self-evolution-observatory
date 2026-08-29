You are an independent adversarial experiment-design reviewer for E2-R17 / Compute Shielding, a prospective top-conference paper. You are blind to the other reviewer. This consultation has zero scientific-experiment, GPU, paper-promotion, frontend, or submission authority.

Requested reviewer endpoint: deepseek-v4-pro
Exact Experiment Plan V2 SHA-256: 3a620eb791b2515b8498d9313698c51a50d59a0b03fb1684379b535e3a73ff08

Review only the bound dossier. Recommend STOP if the remaining contribution collapses to the already-published statement that failed trajectories can help memory. Do not reward experiment volume. Do not invent literature beyond the bound published-baseline audit.

The V2 theory correction distinguishes:
- rescue censoring, which exactly explains acting gain versus the precommitted rollout; and
- mixed-pool support M_K, on which a failure-aware learning projection can differ from winner-only even when rollout-0 already succeeds.

The proposed primary intervention is one-slot Mixed-Rejected-Witness (MRW): on mixed pools it exposes the deterministic lowest-index failed nonwinner to the updater; on non-mixed pools it equals Winner-only. Acting always serves the exact same winner. Therefore Delta_K = M_K * delta_K by conditioning, but theory does NOT assume delta_K > 0.

Published collision: ReasoningBank/MaTTS is ICLR 2026 and already learns from successful and failed trajectories generated with test-time scaling. Headline published baselines are ReasoningBank, PolySkill, ACE, and AWM, with SAGE extended. ArXiv-only works are related/collision context, not headline baselines.

Audit these exact issues:
1. Is the proposed novelty actually distinct from ReasoningBank, or is the exact-same-pool selector framing cosmetic?
2. Is mixed-pool mass M_K the correct treatment-support quantity for MRW? Is the factorization Delta=M*delta causal/identified under the stated cloned-stream design?
3. Does preserving the old E0 HOLD while superseding only the future support estimand avoid post-hoc rewriting?
4. Are the pre-treatment support thresholds (24/96 mixed, 8/12 exposed streams, 4/6 families) defensible, or arbitrary enough to require a different predeclared support rule?
5. Is 12 paired streams with 18 common held-out probes a valid independent-unit design? Is the exact 2^12 sign-flip test valid, and is there pseudoreplication anywhere?
6. Is +/-1/18 as the practical-equivalence margin scientifically defensible? Distinguish qualified STOP from merely underpowered HOLD.
7. Can the one-slot WIN vs MRW contrast still be explained by evidence-token length or truncation? State the cleanest pre-Pilot repair.
8. Are post-GO diagnostic controls (Full Pool, random nonwinner, success nonwinner, ReasoningBank-style aggregation) sufficient to distinguish failure-specific value from generic branch diversity or extra information?
9. Is the published baseline hierarchy fair and current? Are implementation caveats for ReasoningBank and PolySkill handled honestly?
10. Is splitting source-faithful reproduction from unified reruns necessary and sufficient given no common published model? Does current Ark-only credential availability create a fatal blocker or merely a source-lane blocker?
11. Are WebArena primary and AppWorld secondary the right external benchmarks after E1 GO? Should SpreadsheetBench remain additional rather than headline-only?
12. Does V2 keep model selection outcome-blind and avoid pretending Qwen/DeepSeek are common published models?
13. Are checkpoint, missing-unit resume, and no-relaunch-after-502 rules sufficient?
14. What exact P0/P1 changes must be made before any runtime Pilot or E1 pool-generation authorization?

Return exactly one JSON object and no markdown using this schema:
{
  "plan_sha256_acknowledged": "",
  "verdict": "PASS_TO_RUNTIME_PILOT|REVISE_V2_BEFORE_PILOT|STOP_PROGRAM",
  "novelty_against_reasoningbank": "",
  "theory_estimand_assessment": "",
  "historical_e0_preservation_assessment": "",
  "mixed_support_gate_assessment": "",
  "stream_unit_and_statistics_assessment": "",
  "equivalence_stop_rule_assessment": "",
  "evidence_token_budget_assessment": "",
  "published_baseline_fidelity_assessment": "",
  "source_faithful_vs_unified_lane_assessment": "",
  "benchmark_selection_assessment": "",
  "model_selection_assessment": "",
  "checkpoint_resume_assessment": "",
  "budget_assessment": "",
  "fatal_or_blocking_issues": [
    {
      "priority": "P0|P1",
      "issue": "",
      "why_blocking": "",
      "exact_v3_repair": ""
    }
  ],
  "required_v3_changes": [
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
  "runtime_pilot_recommendation": "ALLOW_OUTCOME_BLIND_RUNTIME_PILOTS|HOLD|STOP",
  "e1_pool_support_phase_recommendation": "ALLOW_ONLY_AFTER_V3_CONTRACT|HOLD|STOP",
  "e1_updater_recommendation": "HOLD_UNTIL_SUPPORT_GATE_AND_V3|STOP",
  "paper_claim_authority": false,
  "single_sentence_verdict": ""
}

Set `plan_sha256_acknowledged` exactly to the SHA above. Keep `paper_claim_authority` false. `PASS_TO_RUNTIME_PILOT` authorizes only separate outcome-blind runtime Pilot contracts; it never authorizes E1 scientific execution.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START

===== BOUND ARTIFACT: generated/e2-r17-experiment-plan-v2-20260828.json =====
{
  "artifact_type": "e2-r17-experiment-plan-v2",
  "schema_version": "1.0",
  "date": "2026-08-28",
  "status": "V2_REQUIRES_DUAL_REVIEW_BEFORE_ANY_NEW_SCIENTIFIC_PROVIDER_CALL",
  "supersedes_for_future_execution": "e2-r17-experiment-plan-v1",
  "preserves_historical_artifacts": true,
  "central_question": "Does an acting selector applied to a fixed best-of-K search pool systematically change updater-visible evidence so that winner-only acting projection is learning-suboptimal for future frozen skill?",
  "novelty_boundary": {
    "reasoningbank_collision": true,
    "cannot_claim": [
      "failed trajectories are useful",
      "success/failure contrast can improve memory",
      "test-time scaling can create learning signal",
      "memory and test-time scaling can be combined"
    ],
    "candidate_claim": "exact same-pool acting/learning projection separation, compute-shielding law, budget-matched causal intervention, and prospective regime prediction"
  },
  "theory": {
    "rescue_identity": "A_K-A_1=P(Y_1=0,max_i Y_i=1)=V_pre-V_winner",
    "mixed_support_iid": "M_K=1-p^K-(1-p)^K",
    "nested_monotonicity_without_iid": true,
    "learning_factorization": "Delta_K=M_K*delta_K",
    "delta_positive_assumed": false
  },
  "frozen_e0": {
    "summary_sha256": "533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366",
    "historical_decision": "HOLD",
    "historical_decision_rewritten": false,
    "k8": {
      "acting_success": "12/12",
      "mixed_pools": "8/12",
      "rescue_events": "1/12",
      "winner_visible_failures": "0/12",
      "hidden_failed_nonwinners": 16,
      "failure_family_support": "5/6"
    },
    "old_42_task_rescue_quota_tranche": "DO_NOT_LAUNCH_UNDER_OLD_RATIONALE"
  },
  "controlled_split": {
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2",
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4",
    "selection_is_outcome_blind": true,
    "e1_streams": 12,
    "tasks_per_stream": 8,
    "failure_families": 6,
    "streams_per_family": 2,
    "common_heldout_probes": 18
  },
  "e1_a_support_phase": {
    "k": 8,
    "actor_rollouts": 768,
    "updater_calls": 0,
    "freeze_all_pools_before_gate": true,
    "support_gate_for_review": {
      "minimum_mixed_pools": "24/96",
      "minimum_exposed_streams": "8/12 with >=1 mixed pool",
      "minimum_failure_families": "4/6",
      "task_or_pool_replacement": false,
      "protocol_integrity_required": true
    },
    "failure_action": "STOP_BEFORE_UPDATER_AND_REQUIRE_NEW_PROTOCOL"
  },
  "e1_b_primary": {
    "arms": ["winner_only", "mixed_rejected_witness"],
    "mixed_rejected_witness_rule": "On a mixed pool expose the lowest-rollout-index failed nonwinner; otherwise expose the served winner. Acting always serves the exact same winner.",
    "evidence_slots_per_task": {"winner_only": 1, "mixed_rejected_witness": 1},
    "extra_actor_calls_for_treatment": 0,
    "fixed_invariants": [
      "task IDs and order",
      "initial skill SHA",
      "exact pool IDs",
      "served winner SHA",
      "executor model",
      "verifier",
      "updater model and prompt",
      "update-call count",
      "acceptance/rollback rule",
      "held-out probes",
      "K=1 frozen evaluation",
      "retry policy",
      "software revisions"
    ],
    "primary_endpoint": "per-stream mean K=1 success over the same 18 held-out probes",
    "independent_units": 12,
    "statistics": [
      "exact one-sided paired sign-flip over 4096 sign assignments",
      "10000-draw paired bootstrap over streams",
      "mean and median paired effect",
      "descriptive family-stratified effects"
    ],
    "equivalence_margin": "1/18 = 0.0555556 absolute success",
    "go": "mean>0 AND exact p<=0.05 AND 95% paired-bootstrap CI lower>0 AND integrity/token-policy gates pass",
    "stop": "significantly negative OR predeclared equivalence test supports practical equivalence within +/-1/18",
    "hold": "interval spans both zero and effects larger than the equivalence margin"
  },
  "evidence_budget_policy": {
    "status": "MUST_BE_FROZEN_AFTER_RUNTIME_PILOT_BEFORE_FULL",
    "allowed_choices": [
      "deterministic common-window renderer under fixed public tokenizer",
      "raw one-trajectory evidence plus predeclared token-length robustness and matched-window secondary arm"
    ]
  },
  "e1_c_diagnosis_after_primary_go_only": [
    "Full Pool",
    "deterministic single random nonwinner",
    "success nonwinner when available",
    "ReasoningBank-style aggregation after source-semantic validation"
  ],
  "published_baselines": {
    "headline": ["ReasoningBank/MaTTS (ICLR 2026)", "PolySkill (ICLR 2026)", "ACE (ICLR 2026)", "AWM (ICML 2025)"],
    "extended": ["SAGE (ACL 2026 Long)"],
    "arxiv_only_related_not_headline": ["SkillCAT", "Branch2Skill", "SkillOpt", "RethinkSkill", "TSR"]
  },
  "evaluation_lanes": {
    "source_faithful": {
      "purpose": "reproduction/qualification under each first-party harness and stated model",
      "current_credential_blocker": "69 exposes Ark credentials only; Google/OpenAI/Anthropic/SambaNova source-lane endpoints are not presently configured"
    },
    "unified_rerun": {
      "purpose": "direct method comparison under common qualified executor/updater and identical task/environment accounting",
      "source_faithful_scores_mixed_into_ranking": false
    }
  },
  "public_benchmarks_after_e1_go": {
    "primary": "WebArena",
    "secondary": "AppWorld",
    "additional_if_budget": "SpreadsheetBench Verified-400"
  },
  "later_stages": {
    "e3": "prospective family/K mechanism prediction frozen before future outcomes",
    "e4": "multi-round persistent evolution with online acting vs frozen-skill endpoint separated",
    "e5": "parallel-vs-sequential topology x winner/history-preserving learning"
  },
  "checkpoint_policy": {
    "persist_immediately": ["rollout", "pool", "projection", "updater", "held-out evaluation"],
    "raw_immutable": true,
    "summary_rebuildable": true,
    "missing_unit_resume_only": true,
    "timeout_502_relaunch_without_inspection": false
  },
  "next_gate": [
    "independent Kimi K3 review of exact V2 + theory correction + published baseline audit",
    "independent DeepSeek V4-Pro review of same packet",
    "fix verdict-changing issues only",
    "runtime Pilot for projection renderer and baseline adapters",
    "freeze immutable V3 E1 contract before any new scientific updater outcome"
  ],
  "authority": {
    "new_scientific_provider_calls": false,
    "e1_updater_outcomes": false,
    "public_full_runs": false,
    "paper_promotion": false,
    "submission": false
  }
}


===== BOUND ARTIFACT: consultations/e2-r17-experiment-plan-v2-20260828.md =====
# E2-R17 Experiment Plan V2 — Compute Shielding / Search-Projection Censoring

Date: 2026-08-28
Status: **V2_REQUIRES_DUAL_REVIEW_BEFORE_ANY_NEW_SCIENTIFIC_PROVIDER_CALL**
Supersedes: Experiment Plan V1 for future execution only; V1 artifacts and the frozen E0 HOLD remain preserved.

## 1. Scientific object after theory correction

The paper is not about the generic statement that “failed trajectories are useful.” ReasoningBank (ICLR 2026) already demonstrates memory induction from successful and failed experiences and explicitly couples that learning to test-time scaling.

E2-R17 asks a narrower causal question:

> When search generates multiple trajectories for acting, does the **acting selector** systematically change the evidence distribution visible to a persistent learner, such that an acting-optimal winner-only projection can be learning-suboptimal for future frozen skill?

The generated search pool is the common object:

`exact pool T_1:K -> acting projection g_act -> served winner`

and independently:

`exact same pool T_1:K -> learning projection g_learn -> updater -> future frozen skill`.

The intervention must keep the acting result unchanged.

## 2. Theory: what is established and what remains empirical

### 2.1 Rescue identity

For arbitrary correlated K-rollout outcomes and a precommitted rollout 0:

`A_K - A_1 = P(Y_1=0, max_i Y_i=1) = V_pre(K)-V_winner(K)`.

This is an acting-side identity and was observed exactly in E0.

### 2.2 Mixed-pool compute shielding

Define:

- `A_K = P(any success)`;
- `W_K = P(all fail)` = failure visible through the served winner;
- `F_K = P(any failure)` = failure available in the full generated pool;
- `M_K = P(any success AND any failure)` = success/failure contrast available in the pool.

For nested pools, without an i.i.d. assumption:

- `A_K` nondecreasing in K;
- `W_K` nonincreasing;
- `F_K` nondecreasing;
- `M_K` nondecreasing.

Under i.i.d. success probability p:

`A_K = 1-(1-p)^K`

`W_K = (1-p)^K`

`F_K = 1-p^K`

`M_K = 1-p^K-(1-p)^K`.

For fixed `0<p<1`, increasing K can therefore drive `A_K -> 1` and `W_K -> 0` while `M_K -> 1`. Search can hide failures from the learner-facing winner exactly when the full pool contains increasingly rich success/failure contrast.

### 2.3 Learning factorization

Define `g_MRW`, Mixed-Rejected-Witness:

- non-mixed pool: identical to winner-only;
- mixed pool: select the precommitted deterministic lowest-rollout-index failed nonwinner as the single updater-visible trajectory;
- acting still serves the exact same winner.

Then:

`Delta_K = E[J(U(S,g_MRW(T_1:K)))-J(U(S,g_WIN(T_1:K)))] = M_K * delta_K`,

where `delta_K` is the conditional future-skill advantage on mixed pools.

Theory establishes the availability term `M_K`; it **does not** assume `delta_K>0`.

The central E1 experiment is therefore a direct test of `delta_K`.

## 3. Reinterpretation of frozen E0 without rewriting history

Frozen E0 summary SHA:

`533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366`

At K=8:

- acting success: `12/12`;
- winner-visible failures: `0/12`;
- mixed pools: `8/12`;
- rescue events: `1/12`;
- failed nonwinner trajectories hidden by winner-only: `16`;
- mixed/failure support: `5/6` predeclared failure families.

The old E0 contract required >=6 **rescue** tasks across >=3 families, so its historical decision remains `HOLD`.

For the corrected E1 estimand, rescue count is not the treatment-support quantity. The old 42-task E0-full tranche must **not** be launched merely to satisfy a rescue quota. V2 instead freezes treatment support on E1’s exact pools before any updater call.

## 4. Frozen controlled split

Use `controlled-spreadsheet-suite-v2` without task replacement.

- split manifest SHA: `aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9`
- suite manifest SHA: `2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4`
- selection: SHA256-based and outcome-blind.

E1 update design already contains:

`6 failure families x 2 independent streams/family x 8 distinct tasks/stream = 12 streams, 96 update tasks`.

The 18 common E1 held-out probes are never fed to the updater.

This family-balanced split is kept because it was produced outcome-blind before E1 learning outcomes and gives a clean heterogeneity structure.

## 5. E1-A — pre-treatment pool/support phase

Generate the exact E1 K=8 pools **once** from the frozen initial skill state and persist every rollout immediately.

Budget:

`12 streams x 8 tasks x K=8 = 768 actor rollouts`.

No updater is called during this phase.

All 96 K=8 pools are frozen and content-addressed before the support gate is evaluated.

### 5.1 Support gate

The gate uses only generated-pool treatment exposure, never future skill outcomes.

Proposed V2 thresholds for independent review:

- at least `24/96` pools are mixed;
- at least `8/12` streams contain at least one mixed pool;
- mixed pools appear in at least `4/6` predeclared failure families;
- no task/pool replacement after observing mixed support;
- protocol integrity 100%; technical failures are handled only by predeclared missing-unit resume.

Rationale: the primary inference unit is the stream. At least eight exposed streams ensures that a nontrivial majority of the 12 paired units receive a real learning treatment. The total-pool and family gates prevent an apparently large stream count from being driven by one isolated witness per stream or one narrow failure family.

Planning reference only, not an independence assumption: if per-task mixed probability q were independent within an 8-task stream, `P(stream has >=2 mixed)=1-(1-q)^8-8q(1-q)^7`, which equals approximately 0.50 at q=.20, 0.63 at q=.25, 0.74 at q=.30, 0.89 at q=.40, 0.96 at q=.50, and 0.997 at q=2/3. E0 observed 8/12 mixed pools, so the V2 support gate is plausible without difficulty-engineering toward rescue events.

If support fails, stop before any updater call. A future redesign requires a new contract; it cannot replace tasks after seeing support.

## 6. E1-B — exact same-pool causal intervention

Only if E1-A support and protocol gates pass.

### 6.1 Primary two-arm intervention

For every stream clone the same initial persistent state and use the exact same 8 frozen pools.

**WIN**

- acting: exact served winner;
- updater-visible evidence: the served winner, one slot per task.

**MRW**

- acting: exact same served winner;
- non-mixed pool: same winner evidence as WIN;
- mixed pool: deterministic lowest-index failed nonwinner, one slot per task.

Fixed across arms:

- task IDs and order;
- initial skill SHA;
- exact pool IDs;
- served winner SHA;
- executor model;
- verifier;
- updater model and prompt;
- update-call count;
- update acceptance/rollback rule;
- held-out probe IDs;
- held-out executor and K=1 evaluation;
- retry policy;
- software revisions.

No extra actor calls are permitted for MRW.

### 6.2 Evidence-budget audit

Both primary arms expose exactly one source trajectory per update task. Natural trajectory token lengths may differ, so token count is recorded as a possible mediator/alternative explanation.

Before Full E1 authorization, the runtime Pilot must freeze one of two policies:

1. a deterministic common-window renderer that gives both source trajectories the same evidence window under a fixed public tokenizer; or
2. raw one-trajectory evidence plus a predeclared token-length robustness analysis and a matched-window secondary arm.

This policy must be fixed before held-out outcomes.

### 6.3 Primary endpoint

For each of the 12 stream-level learned skills:

`J_s = mean K=1 success over the same 18 held-out probes`.

Primary paired difference:

`D_s = J_s(MRW) - J_s(WIN)`.

The 12 stream pairs are the independent inference units. The 18 probes are repeated measurements used to reduce endpoint variance, not 216 independent learned skills.

### 6.4 Primary inference

- exact one-sided sign-flip/randomization test over all `2^12=4096` paired sign assignments;
- 10,000-draw paired bootstrap over streams for the mean difference;
- mean and median paired effect;
- stream-level table with mixed-pool dose `m_s`;
- family-stratified effect shown descriptively; two streams/family are insufficient for standalone family significance claims.

### 6.5 GO / HOLD / STOP

**Mechanism GO** requires all of:

- mean paired effect > 0;
- exact one-sided p <= .05;
- 95% paired-bootstrap CI lower bound > 0;
- provenance/integrity gates pass;
- effect is not explained solely by a predeclared evidence-window violation.

**Qualified mechanism STOP** if either:

- the effect is significantly negative; or
- a predeclared equivalence test supports practical equivalence within `+/- 1/18 = +/-5.56 percentage points` of held-out success.

The equivalence margin corresponds to one held-out probe success per stream and is frozen before outcomes.

**HOLD / INCONCLUSIVE**, not false STOP, if the interval spans both zero and effects larger than the equivalence margin. In that case no benchmark zoo is opened to manufacture a positive story; the central claim remains unsupported.

## 7. E1-C — predeclared diagnosis after primary GO

Only if the primary WIN-vs-MRW causal contrast passes. The purpose is to identify the simplest repair, not to rescue a failed primary test.

On the already frozen pools, add predeclared diagnostic projections:

- Full Pool — upper-bound information retention, larger evidence budget;
- deterministic single random nonwinner — generic branch-diversity control;
- success-nonwinner when available — tests whether any alternative successful path suffices;
- ReasoningBank-style success/failure aggregation adapter — published collision baseline, only after source-semantic validation.

If MRW matches Full Pool / richer aggregation within the equivalence margin, the paper keeps the simple one-witness method and deletes unnecessary complexity.

If generic nonwinner matches MRW, the claim is narrowed from “failed witness” to “nonwinner evidence.”

## 8. Published baseline set

Headline baselines are now restricted to formally published top-venue methods with first-party implementations:

- ReasoningBank / MaTTS — ICLR 2026;
- PolySkill — ICLR 2026;
- ACE — ICLR 2026;
- Agent Workflow Memory — ICML 2025;
- SAGE — ACL 2026 Long, extended because it is parametric RL and substantially more expensive.

ArXiv-only SkillCAT, Branch2Skill, SkillOpt, RethinkSkill and TSR remain collision/Related Work references rather than headline main-table baselines.

Pinned implementation details are in `consultations/e2-r17-published-baseline-audit-v2-20260828.md` and its JSON companion.

## 9. Source-faithful vs unified evaluation lanes

The published baselines do not share one common model. V2 therefore forbids a fake “common published model” claim.

### Lane A — source-faithful reproduction

Qualify each baseline with its first-party harness/model where credentials and compute permit:

- ReasoningBank WebArena: Gemini-2.5-Flash;
- AWM WebArena: GPT-4o-2024-05-13;
- PolySkill: one of its four paper models, with exact model identity recorded;
- ACE AppWorld: DeepSeek-V3.1 via the first-party configuration;
- SAGE AppWorld: released Qwen2.5-32B substrate / trained checkpoint path.

Current 69 credentials expose only Ark, so Gemini/OpenAI/Anthropic/SambaNova source-lane runs are **not presently qualified**. This is a runtime limitation, not permission to silently substitute a model.

### Lane B — unified rerun

After baseline adapters pass semantic Pilot, rerun compatible methods under common qualified executors and updater roles. This lane is the only place where direct method ranking is allowed.

Candidate unified matrix is frozen only after outcome-blind runtime qualification. A reasonable capability spread is:

- one feasible open Qwen family model;
- one stronger open model if stable tool use is available;
- DeepSeek V4-Pro as an already qualified strong API family;
- Kimi K3 only as second-family robustness if it passes the same tool/artifact gate.

These are matched-rerun models, not “models used by all published baselines.”

## 10. E2 — public benchmark effectiveness after E1 GO

### 10.1 WebArena — primary literature-comparison environment

ReasoningBank, AWM and PolySkill all provide first-party WebArena implementations.

Core unified methods after Pilot:

- base/no persistent learning;
- Winner-only;
- MRW;
- Full Pool or final simplest projection;
- AWM;
- ReasoningBank/MaTTS;
- PolySkill where adapter fairness is defensible.

Source-faithful reproduction results are shown separately from unified reruns.

Primary metric: execution success rate, paired on identical task IDs per model/method where protocol permits. Report 95% CIs, call counts, generated trajectories, update tokens, and wall-clock/cost accounting.

### 10.2 AppWorld — secondary published-baseline environment

ACE is the headline context-evolution baseline; SAGE is an extended parametric baseline.

Core unified comparison after adapter Pilot:

- base;
- Winner-only;
- MRW/final projection;
- ACE;
- Full Pool where meaningful.

SAGE is included only with honest compute accounting and cannot be forced into a false context-token budget match.

### 10.3 SpreadsheetBench Verified-400

Retain as an additional public transport domain if E1 passes and budget permits. It is valuable because mechanism identification already uses spreadsheet tasks, but it is no longer the sole/main external baseline environment.

## 11. E3 — prospective mechanism prediction

Use calibration/development data only to estimate family-wise availability `M_z(K)` and diagnostic value proxies. Before opening the reserved future outcomes, hash-freeze:

- predicted effect sign;
- K ordering;
- family ranking;
- null/near-null cells.

Then evaluate against the untouched future streams.

The theory claim survives only if prediction is prospective. A post-hoc fit cannot be promoted to a regime law.

## 12. E4 — multi-round persistent evolution

Only after E1 and public one-step transport are positive.

Compare matched streams such as:

- low-search / winner learning;
- high-search / winner-only learning;
- high-search / MRW;
- high-search / final projection.

After every update batch, freeze skill SHA and run the same K=1 endpoint. Track online acting reward separately from future frozen-skill value.

This tests whether higher current search performance can coexist with poorer persistent learning and whether the projection repair prevents that divergence.

## 13. E5 — topology

Only after the earlier evidence chain passes.

Matched-call factorial:

`parallel best-of-K vs sequential refinement`

x

`winner/final-only learning vs history-preserving learning`.

This asks whether the effect follows the learning projection across search topologies rather than raw compute amount.

## 14. Checkpoint/recovery contract

Every scientific stage remains checkpoint-first:

`rollout complete -> persist raw trajectory/output/verifier/provider-hash`

`K rollouts complete -> freeze pool and prefix pools`

`projection selected -> freeze evidence packet + source SHAs`

`updater complete -> save pre/post skill, input/output, candidate/accepted state`

`held-out probe complete -> persist skill SHA, trajectory, output, verifier`.

Maintain immutable `raw/`, resumable `checkpoints/`, and rebuildable `summary/`.

After timeout/MCP 502, inspect processes/locks/completed manifests before any relaunch. Resume missing units only.

## 15. Budget ceilings before full authorization

V2 does not authorize a full run until runtime Pilot measures per-model calls/tokens/latency.

Known E1 pool-generation actor count if support phase is authorized: 768 rollouts.

Known E0 empirical rate for the qualified DeepSeek actor was approximately 5.896 provider calls and 17,830 total tokens per actor rollout. This is a planning reference only; V3 must bind measured Pilot ceilings for every selected model.

Before E1-B Full, freeze:

- maximum actor calls;
- maximum updater calls;
- maximum total input/output tokens;
- maximum wall-clock duration;
- missing-unit resume rules;
- no scientific retry beyond the frozen retry policy.

## 16. Immediate next gate

1. Kimi K3 and DeepSeek V4-Pro independently review **this exact V2** plus the theory-correction and published-baseline audit artifacts.
2. Review questions focus on novelty against ReasoningBank, mixed-pool estimand validity, support gate, 12-stream inference, equivalence margin, evidence-token confounding, published-baseline fairness, and source-faithful/unified separation.
3. Only verdict-changing issues may modify V2 into V3.
4. Then run zero/outcome-blind runtime Pilots for the new projection renderer and selected baseline adapters.
5. Only after those Pilots pass may an immutable E1-A/B full contract be created.

No E1 updater outcome has been generated under V2 at the time this plan is written.


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


===== BOUND ARTIFACT: consultations/e2-r17-theory-correction-mixed-pool-20260828.md =====
# E2-R17 Theory Correction — Rescue Censoring vs Mixed-Pool Learning Support

Date: 2026-08-28
Status: **THEORY_CORRECTION_BEFORE_E1**
Authority: planning/theory only; no E1 outcome authority

## 1. Why this correction is necessary

The frozen E0 analysis correctly established the rescue-censoring identity, but the subsequent V1 planning gate used **rescue-event count** as if it were the support set for the Rejected-Witness learning intervention. That is too narrow.

There are two distinct scientific quantities:

1. **Rescue censoring**: a precommitted failure is rescued by search and hidden by winner-only serving. This quantity exactly explains best-of-K acting gain relative to rollout-0.
2. **Mixed-pool censoring**: the generated pool contains both successful and failed trajectories, while winner-only learning exposes only the successful winner. This is the support set on which a failure-aware learning projection can differ from winner-only.

The first is an acting-side identity. The second is the treatment-support quantity for E1. They coincide only in a special subset of pools and must not be conflated.

This correction does **not** alter, delete, or reinterpret the frozen E0 receipts. It supersedes only the future support gate used to decide whether an updater-side intervention is identifiable.

## 2. Formal object

For a fixed task, initial persistent state, actor, verifier, and nested best-of-K search pool, let

- `T_1, ..., T_K` be the generated trajectories,
- `Y_i in {0,1}` be the binary verifier outcome,
- `W_K` be the served winner, chosen as a success whenever any success exists,
- `U(S, g(T_1:K))` be a frozen updater applied to learning projection `g`,
- `J(.)` be future frozen-skill value on held-out tasks.

The acting projection and learning projection are separate functions of the same frozen search object.

## 3. Theorem A — exact rescue-censoring identity

Let rollout-0/`T_1` be the precommitted no-search action. For an arbitrary joint law over the K rollouts, without independence or exchangeability,

`A_K - A_1 = P(Y_1=0, max_i Y_i=1)`.

Winner-only failure visibility is `P(max_i Y_i=0)`, while precommitted failure visibility is `P(Y_1=0)`. Therefore

`A_K - A_1 = V_pre(K) - V_winner(K)`.

This is the exact identity already validated by the frozen E0 analysis and by the unit tests in `research_pipeline/test_e2_r17_search_projection_theory.py`.

Under i.i.d. success probability `p`,

`Gamma_K(p) = (1-p) - (1-p)^K`.

This quantity peaks at `p* = 1 - K^(-1/(K-1))` for `K>1`.

**Interpretation:** every unit of best-of-K acting gain over the precommitted rollout corresponds to a rescued precommitted failure that winner-only serving no longer exposes.

## 4. Theorem B — nested-search evidence shielding

Define four events/quantities for the exact K-pool:

- `A_K = P(any success)` — acting success,
- `W_K = P(all fail)` — winner-visible failure,
- `F_K = P(any failure)` — full-pool failure availability,
- `M_K = P(any success AND any failure)` — mixed-pool contrast support.

For **nested pools**, pointwise set inclusion gives, with no i.i.d. assumption:

- `A_K` is non-decreasing in K,
- `W_K` is non-increasing in K,
- `F_K` is non-decreasing in K,
- `M_K` is non-decreasing in K.

Thus increasing search compute can simultaneously improve served outcomes while making failure nearly disappear from winner-only learning, even though failed counterevidence remains present in the generated pool.

Under i.i.d. success probability `p`:

- `A_K = 1 - (1-p)^K`,
- `W_K = (1-p)^K`,
- `F_K = 1 - p^K`,
- `M_K = 1 - p^K - (1-p)^K`.

For every fixed `p in (0,1)`, as `K -> infinity`:

- `A_K -> 1`,
- `W_K -> 0`,
- `F_K -> 1`,
- `M_K -> 1`.

This is the core **compute-shielding** regime: user-facing failures vanish while same-task success/failure contrast becomes almost surely available inside the discarded search pool.

`M_K(p)` is symmetric around `p=1/2` and peaks at `p=1/2`. This is different from the rescue-censoring peak `p*` above.

## 5. Expected hidden failed-branch mass

Under i.i.d. rollouts, the expected number of failed branches omitted on pools where the served winner succeeds is

`H_K(p) = K[(1-p) - (1-p)^K] = K Gamma_K(p)`.

This counts available failed branches, not their diagnostic utility. More failed branches do not imply better learning if they are redundant or misleading.

## 6. Theorem C — exact mixed-gated learning factorization

Define a deterministic one-slot projection `g_RW`:

- if the pool is not mixed, `g_RW = g_WIN`;
- if the pool is mixed, `g_RW` selects the lowest-rollout-index failed non-winner, according to a rule frozen before held-out outcomes;
- acting always serves the exact same winner in both arms.

Let

`D = J(U(S, g_RW(T_1:K))) - J(U(S, g_WIN(T_1:K)))`.

Because the two projections are identical outside the mixed event,

`Delta_K = E[D] = M_K * delta_K`,

where

`delta_K = E[D | mixed pool]`.

This factorization is exact by conditioning; it does not assume that `delta_K > 0`.

This separates the paper into two independently testable mechanisms:

1. **availability mechanism:** search changes `M_K`; E0/theory can establish this;
2. **diagnostic-value mechanism:** the censored witness changes future skill, i.e. `delta_K != 0`; only E1 can establish this.

The central learning claim requires `delta_K > 0` in a predeclared regime. If `delta_K = 0`, projection censoring is behaviorally real but learning-irrelevant. If `delta_K < 0`, failure-aware projection is harmful and the proposed repair is rejected.

## 7. Family-wise prospective prediction

For controlled tasks with one predeclared failure family `z` per task, define

- `M_z(K)` = mixed-pool support for family z,
- `delta_z` = conditional future-skill advantage of the mixed-gated witness over winner-only.

For a mutually exclusive family partition,

`Delta(K) = sum_z pi_z M_z(K) delta_z`.

This supports a prospective E3 test: estimate `delta_z` only on development/calibration streams, freeze signs/ranking/K-ordering, then predict held-out confirmatory effects from measured `M_z(K)`.

If failure-family labels overlap, this additive decomposition must not be used without a predeclared partition or another identified attribution scheme.

## 8. Reinterpretation of the frozen E0 pilot

The frozen E0 K=8 result is:

- acting success: `12/12`,
- winner-visible failure: `0/12`,
- mixed pools: `8/12`,
- rescue events: `1/12`,
- hidden failed non-winner trajectories: `16`,
- mixed/failure support spans `5/6` predeclared failure families.

Therefore:

- the **rescue identity** has only one observed task of support;
- the **mixed-pool learning intervention** has eight observed task pools of support;
- using `>=6 rescue tasks` as the E1 treatment-support gate is theoretically misaligned.

The previous E0 `HOLD` remains historically valid under its frozen contract. It must not be silently rewritten. Instead, V2 should record that the old rescue-count gate is superseded for the new mixed-gated estimand before any E1 updater outcome is generated.

## 9. Collision boundary with published ReasoningBank

ReasoningBank (ICLR 2026) already establishes that a memory system can distill from both successful and failed trajectories, and MaTTS aggregates successful and failed trajectories produced by test-time scaling. Its reported failure-trajectory ablation means E2-R17 cannot claim novelty from the statement “failed trajectories are useful.”

The defensible E2-R17 novelty target is narrower and more causal:

1. formally separate acting projection from learning projection on the **same generated search pool**;
2. quantify selection-induced evidence shielding as K changes;
3. keep the served winner, actor calls, initial persistent state, updater, and held-out evaluation fixed while changing only updater-visible evidence;
4. identify `M_K * delta_K` with precommitted projection rules;
5. test whether a **single budget-matched rejected witness** captures the useful information, rather than assuming that full-pool aggregation is necessary;
6. prospectively predict where the effect should vanish or strengthen.

If E1 only reproduces “success+failure memory beats success-only memory,” novelty is insufficient relative to ReasoningBank.

## 10. Null regimes and falsifiers

The theory explicitly predicts no useful R17 effect when any of the following holds:

- `M_K = 0` (all-success or all-failure pool; no success/failure contrast),
- `delta_K = 0` (failed witness is not reusable for future tasks),
- `delta_K < 0` (failed witness is misleading or updater cannot interpret it),
- the production learner already consumes the full search pool or equivalent contrastive evidence,
- future tasks do not share the latent failure mechanism exposed by the witness.

These are scientific boundaries, not implementation failures.

## 11. V2 design consequence

The 42-task E0-full tranche proposed only to satisfy the rescue-count quota should **not** be launched under the old rationale.

V2 should instead use a pre-treatment support gate on the exact pools that would feed E1, with no updater calls before the gate is evaluated. A defensible initial gate is:

- 12 streams x 8 controlled tasks, K=8, all pools frozen first;
- at least `24/96` pools are mixed;
- at least `8/12` streams contain at least two mixed pools;
- mixed support spans at least `4/6` predeclared failure families;
- no pool/task replacement after observing support;
- if the gate fails, stop before any updater call and redesign only under a new protocol.

These thresholds are support/identifiability thresholds, not effect thresholds. They must be independently reviewed before authorization.

## 12. Current scientific state after correction

- Search-induced visibility shift: **SUPPORTED**.
- Exact rescue-censoring identity: **SUPPORTED**.
- Mixed-pool compute-shielding law: **THEORETICALLY ESTABLISHED; E0 CONSISTENT**.
- Positive diagnostic value `delta_K`: **UNKNOWN**.
- Learning regret from winner-only projection: **UNKNOWN**.
- Final repair method: **UNDECIDED**.

The next verdict-changing experiment is still E1, but E1 should be a **mixed-pool-gated exact-same-pool intervention**, not a rescue-event-only intervention.


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


===== BOUND ARTIFACT: generated/e2-r17-e0-analysis-20260828.json =====
{
  "artifact_type": "e2-r17-e0-analysis",
  "schema_version": "1.0",
  "created_at_utc": "2026-08-28T08:23:21.819922+00:00",
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


===== BOUND ARTIFACT: generated/e2-r17-e0-go-hold-stop-20260828.json =====
{
  "artifact_type": "e2-r17-e0-go-hold-stop",
  "schema_version": "1.0",
  "created_at_utc": "2026-08-28T08:23:21.819922+00:00",
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


===== BOUND ARTIFACT: generated/e2-r17-experiment-plan-v2-model-identity-qualification-20260828.json =====
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
  "created_at_utc": "2026-08-28T08:37:34+00:00",
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
      "response_id_sha256": "3b426bbcc705b3015086036bab5fc8a9a5bad7b1e6b57b09bb88a9c4aa9d43a6",
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
      "response_id_sha256": "cad2d2686400b024fd6fd5c44daabcfb2a2c9d4bb0e4fd644177e8923107d7c0",
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
