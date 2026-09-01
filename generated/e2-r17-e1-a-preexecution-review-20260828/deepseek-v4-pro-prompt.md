You are an independent adversarial pre-execution reviewer for E2-R17 E1-A. You are blind to the other reviewer. This review has zero authority by itself. It may at most recommend minting a separately SHA-bound authorization for E1-A pool generation/support measurement. It cannot authorize E1-B updater calls, held-out future-skill evaluation, paper claims, frontend promotion, or submission.

Reviewer endpoint: deepseek-v4-pro
Exact E1-A draft contract SHA-256: bc9d4eb464cd289cbf71d0fe0772b2bc71daee0ce137d27b2337dc1c3b1f3c92

E1-A's scientific role is deliberately narrow: freeze the predeclared 96 update-task search pools (12 streams x 8 tasks, K=8 = 768 actor rollouts) and evaluate only a pre-treatment identifiability/support gate. No updater call, MRW/WIN comparison, RB aggregation, future-skill evaluation, or method-effectiveness statistic occurs in E1-A.

Audit the actual code and frozen split. Answer these questions:

1. SUPPORT GATE: Is `mixed>=24/96 AND exposed_streams>=8/12 with each exposed stream >=2 mixed pools` a legitimate predeclared identifiability/support gate rather than method-outcome selection, given that all 96 pools must be frozen before the gate, no task/pool may be replaced/dropped afterward, borderline values fail, and the thresholds were frozen in V3 before E1-A outcomes? The separate >=4/6 family gate must not control pooled E1-B authority.

2. OUTCOME SELECTION: Identify any path in the orchestrator or adjudicator that could inspect mixed/support outcomes early and selectively stop, replace, rerun, or omit tasks to improve support. Technical failures may stop execution but cannot be treated as scientific failures or replaced based on scores.

3. UNITS/SPLIT: Verify the bound split contains exactly 12 e1_update_streams, 8 unique tasks each, 96 unique tasks total, and that it is separated from development and held-out future probes as represented in the bound suite artifacts.

4. AUTHORITY SCOPE: Inspect the new fail-closed execution_scope check in run_e2_r17_actor_pool.py. A final E1-A authorization must bind allowed_modes=['e1'], the exact 96 allowed_task_ids, exact_k=8, suite/split SHAs, initial-skill SHA, e1_a=true and e1_b=false. Can the proposed authorization still be trivially misused to run out-of-scope tasks/K/noninitial skills?

5. CHECKPOINT/RESUME: Inspect both layers. run_actor_rollout should immediately persist a trajectory and content-addressed ref and reuse it if valid. The E1-A orchestrator should persist per-task prefix/K pools, per-stream summaries, append+fsync completed_streams.jsonl, SHA-revalidate completed streams/rollouts before reuse, and execute only missing work. If interrupted inside an 8-rollout task, would resuming after explicit stale-lock adjudication avoid duplicate completed provider calls?

6. STALE LOCK: The orchestrator intentionally leaves `.exclusive.lock` after any failed subprocess so an operator must inspect process/checkpoints before resuming. Is this appropriately fail-closed for known MCP 502/timeout semantics? Flag if successful completion or ordinary exception handling can accidentally remove a lock that should remain.

7. BUDGET: K=8, max_turns=10, retry=0 gives 768 actor rollouts and a declared ceiling of 7680 provider calls with max_output_tokens=4096 per call. Is that ceiling structurally enforced by the agent runtime, or does the contract/runner need another pre-call accounting guard before scientific execution? If P0, specify a repair.

8. MODEL IDENTITY: The E1-A qualification immediately before this review resolves deepseek-v4-pro to deepseek-v4-pro-ga-260813 and retry=0/thinking disabled. Does the bound actor runner enforce that resolved identity on every provider receipt and fail on drift?

9. SUPPORT ADJUDICATOR: Does adjudicate_e2_r17_e1_a_pool_support.py independently recompute the 96 exact K=8 pools, trajectory SHAs, mixed total, exposed streams, and no-updater condition before returning support PASS/STOP? Does it accidentally grant E1-B execution authority?

10. UPDATER SEPARATION: Verify E1-A cannot call MindMemOS SkillEvolver or evaluate learned skills. Its output is only frozen pools + support. Even a support PASS must require a separate immutable E1-B contract with fresh updater identity and WIN-A/WIN-B negative-control-first logic.

11. SELECTION DISCIPLINE: Do not recommend changing the support thresholds, tasks, K, or model based on E1-A outcomes. If the frozen support gate fails, the current E1 mechanism is not identifiable on this controlled substrate and E1 must stop before updater calls.

Return exactly one JSON object and no markdown using this schema:
{
  "draft_contract_sha256_acknowledged": "",
  "repair_sha256_acknowledged": "",
  "verdict": "PASS_TO_SEPARATELY_BOUND_E1_A_AUTHORIZATION|REVISE_E1_A_BEFORE_AUTHORIZATION|STOP_E1_A",
  "support_gate_assessment": "",
  "outcome_selection_assessment": "",
  "split_and_unit_assessment": "",
  "authorization_scope_assessment": "",
  "checkpoint_resume_assessment": "",
  "stale_lock_assessment": "",
  "provider_budget_assessment": "",
  "model_identity_assessment": "",
  "support_adjudicator_assessment": "",
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

Set both `draft_contract_sha256_acknowledged` and the transport-alias field `repair_sha256_acknowledged` exactly to the SHA above. Keep `paper_claim_authority` false and `e1_b_recommendation` HOLD on any PASS. A PASS recommends only that a final contract/authorization be minted with the reviewed semantics and exact code/data bindings.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START

===== BOUND ARTIFACT: e1_a_draft_contract | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-pool-support-draft-contract-20260828.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-e1-a-pool-support-contract",
  "date": "2026-08-28",
  "status": "DRAFT_PENDING_INDEPENDENT_PREEXECUTION_REVIEW",
  "scientific_role": "PRE_TREATMENT_SUPPORT_AND_POOL_FREEZE_ONLY",
  "parents": {
    "v3_plan": {
      "path": "generated/e2-r17-experiment-plan-v3-20260828.json",
      "sha256": "b1a0224117f161ead9fccefa2c22a0f01dfa1d9e72ca1e98107418f21e3e04c5"
    },
    "v3_1_mechanical_adjudication": {
      "path": "generated/e2-r17-v3-1-mechanical-pilot-adjudication-20260828.json",
      "sha256": "9b02d870f808c5f61e42b87b9bf09c8028192207267ef56bf65f40fa988b3a10",
      "status": "PASS_MECHANICAL_ONLY_NO_E1_AUTHORITY"
    }
  },
  "run_root": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-20260828",
  "suite": {
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4",
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "metadata_sha256": "12d6eb876e2a230e7990be3e61fed108d45f6ddec00bac5c9b88585a04111b04",
    "split_is_outcome_blind": true,
    "task_replacement_after_support_observation": false
  },
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
  "scientific_units": {
    "streams": 12,
    "tasks_per_stream": 8,
    "unique_update_tasks": 96,
    "search_k": 8,
    "actor_rollouts": 768,
    "nested_prefixes": [1, 2, 4, 8],
    "updater_calls": 0,
    "heldout_future_skill_evaluations": 0
  },
  "actor": {
    "requested_model": "deepseek-v4-pro",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "max_turns": 10,
    "max_output_tokens": 4096,
    "temperature": 0,
    "thinking": "disabled",
    "provider_retry_limit": 0,
    "concurrency": 4,
    "search_topology": "parallel_best_of_k"
  },
  "model_identity": {
    "path": "generated/e2-r17-e1-a-model-identity-adjudication-20260828.json",
    "sha256": "602d8e8cb7544700e2ce74e5915d54069930fb483a522f9d397d2883b9f39b7c",
    "status": "PASS_CURRENT_REVIEW_TRANCHE",
    "qualification_path": "generated/e2-r17-e1-a-model-identity-qualification-20260828.json",
    "qualification_sha256": "f734dd4c5815a447e6fbf2bfacae26c5b60a10ac359d03e5838760793e077c9a"
  },
  "mindmemos": {
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817",
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "initial_skill_sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb",
    "skill_mutation_allowed": false
  },
  "support_gate": {
    "evaluate_only_after_all_96_k8_pools_are_frozen": true,
    "mixed_pool_count_minimum": 24,
    "mixed_pool_total": 96,
    "exposed_stream_minimum": 8,
    "stream_total": 12,
    "mixed_pools_per_exposed_stream_minimum": 2,
    "supported_families_minimum": 4,
    "family_gate_controls_primary_e1_b": false,
    "borderline_is_failure": true,
    "rounding_or_waiver": false,
    "replace_or_drop_tasks_after_support_observation": false,
    "hard_gate_failure": "STOP_E1_BEFORE_ANY_UPDATER_CALL"
  },
  "budget": {
    "actor_rollouts_exact": 768,
    "max_provider_calls": 7680,
    "max_output_tokens_per_provider_call": 4096,
    "theoretical_max_output_tokens": 31457280,
    "provider_retry_limit": 0,
    "duplicate_completed_rollout_calls": 0,
    "updater_calls": 0
  },
  "checkpoint": {
    "exclusive_lock": ".exclusive.lock",
    "leave_lock_on_failure_for_manual_inspection": true,
    "stream_manifest": "checkpoints/completed_streams.jsonl",
    "unit_level_rollout_refs": "cases/<task>/rollout_<i>/r17_trajectory_ref.json",
    "unit_level_pool_freeze": "cases/<task>/pool_k{1,2,4,8}.json",
    "stream_summary": "summary/streams/<stream>.json",
    "revalidate_completed_stream_and_rollout_sha_before_resume": true,
    "resume_missing_only": true,
    "blind_relaunch_after_timeout_or_502": false
  },
  "bound_code": {
    "actor_runner": {
      "path": "scripts/run_e2_r17_actor_pool.py",
      "sha256": "a1bf2dded7f632af21fcf107614d9776cb9c148a43e4391fa36c0a47ffd836f0"
    },
    "e1_a_orchestrator": {
      "path": "scripts/run_e2_r17_e1_a_pool_support.py",
      "sha256": "0fb636eb6cd00fe96c5a88365fa7d0530ac02f19c5362ff1eed91027fadde688"
    },
    "support_adjudicator": {
      "path": "scripts/adjudicate_e2_r17_e1_a_pool_support.py",
      "sha256": "7b63a526cf2c695daf69dbe1cfefd41df4e635bc8c1609cf193e39e11c4197dc"
    },
    "authority_scope_test": {
      "path": "research_pipeline/test_e2_r17_actor_authority_scope.py",
      "sha256": "4c383aed93bb4d20d0726bc02c3fbba72baead62cc55838850b4f12061b2a1a0"
    }
  },
  "authorization_scope_required": {
    "status": "AUTHORIZED_E1",
    "authority.scientific_experiment": true,
    "authority.e1_a": true,
    "authority.e1_b": false,
    "allowed_modes": ["e1"],
    "allowed_task_ids": "exact 96 task IDs from the bound e1_update_streams split",
    "exact_k": 8,
    "allow_noninitial_skill": false,
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4",
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "required_skill_pre_sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb"
  },
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
  "post_run": {
    "runner_status": "COMPLETED_ALL_96_POOLS_PENDING_SEPARATE_SUPPORT_ADJUDICATION",
    "adjudicator": "scripts/adjudicate_e2_r17_e1_a_pool_support.py",
    "primary_support_pass": "mixed>=24/96 AND exposed_streams>=8/12 where each exposed stream has >=2 mixed pools",
    "if_primary_support_fail": "STOP_E1_BEFORE_UPDATER",
    "if_primary_support_pass": "may prepare a separate immutable E1-B contract; E1-B remains unauthorized until separately reviewed"
  },
  "authority": {
    "independent_preexecution_review": true,
    "execute_e1_a": false,
    "execute_e1_b": false,
    "provider_runtime_updater_pilot": false,
    "paper_promotion": false,
    "submission": false
  }
}


===== BOUND ARTIFACT: v3_plan | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/consultations/e2-r17-experiment-plan-v3-20260828.md =====
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


===== BOUND ARTIFACT: v3_1_mechanical_adjudication | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-v3-1-mechanical-pilot-adjudication-20260828.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-v3-1-mechanical-pilot-adjudication",
  "date": "2026-08-28",
  "status": "PASS_MECHANICAL_ONLY_NO_E1_AUTHORITY",
  "contract": {
    "path": "generated/e2-r17-v3-1-mechanical-pilot-contract-20260828.json",
    "sha256": "46606d33c3d6b7694279bbaf4d1e4469fee40820ab8ca64a06d1fbdc6bafa6e9"
  },
  "run": {
    "root": "/data/wyt/e2-r17-search-projection/runtime-pilots/v3-1-mechanical-20260828",
    "summary": "summary/runtime_pilot_summary.json",
    "summary_sha256": "f24743f2c70bcc914060a432a7ec6833145546e7946e25cb73bb62e556c10807",
    "completed_manifest": "checkpoints/completed_units.jsonl",
    "completed_manifest_sha256": "14002142e56eed1e081f108f170445e9de97a69c0459c09f135f130f9c1738df",
    "raw_pool_receipts": 12,
    "completed_manifest_rows": 12
  },
  "observed": {
    "pools": 12,
    "mixed_pools": 8,
    "nonmixed_pools": 4,
    "exact_final_retokenized_parity": true,
    "matched_final_tokens_min": 995,
    "matched_final_tokens_median": 2057.5,
    "matched_final_tokens_mean": 2072.5,
    "matched_final_tokens_max": 3072,
    "selected_source_budget_gap_max": 1,
    "nonmixed_model_visible_identity": true,
    "arm_metadata_visible_in_messages": false,
    "selected_evidence_score_semantics": true,
    "acting_provenance_identical_across_clones": true,
    "downstream_transcript_truncation": false,
    "corruption_detection_simulation": true,
    "provider_calls": 0,
    "new_actor_rollouts": 0,
    "scientific_effectiveness_evaluated": false
  },
  "resume_check": {
    "intentional_second_invocation": true,
    "completed_now": 0,
    "reused_after_sha_validation": 12,
    "duplicate_provider_calls": 0,
    "duplicate_actor_rollouts": 0,
    "status": "PASS"
  },
  "interpretation": "V3.1 repairs the mechanical causal-purity defects that stopped V3. This is engineering qualification only. It does not establish that MRW changes future skill utility and cannot promote the paper mechanism.",
  "next_gate": "SEPARATE_IMMUTABLE_E1_A_POOL_SUPPORT_CONTRACT_AND_INDEPENDENT_PREEXECUTION_REVIEW",
  "authority": {
    "prepare_e1_a_contract": true,
    "review_e1_a_contract": true,
    "execute_e1_a": false,
    "provider_runtime_pilot": false,
    "e1_b": false,
    "scientific_effectiveness": false,
    "paper_promotion": false,
    "submission": false
  }
}


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


def verify_stream_receipt(row: dict[str, Any], run_root: Path) -> None:
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
    lock_fd = acquire_lock(lock_path, contract_sha=contract_sha, authorization_sha=auth_sha)
    success = False
    try:
        completed = manifest_rows(manifest_path)
        for row in completed.values():
            verify_stream_receipt(row, run_root)

        for stream_id in frozen_stream_ids:
            if stream_id in completed:
                continue
            output = summary_root / f"{stream_id}.json"
            command = [
                sys.executable,
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
                "--output", str(output),
            ]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
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
            verify_stream_receipt(row, run_root)
            append_jsonl(manifest_path, row)
            completed[stream_id] = row

        require(len(completed) == 12, "E1-A did not complete all 12 streams")
        for row in completed.values():
            verify_stream_receipt(row, run_root)

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
        require(total_provider_calls <= int(contract["budget"]["max_provider_calls"]), "provider call hard ceiling exceeded")
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
            "streams": 12,
            "tasks": 96,
            "actor_rollouts": total_rollouts,
            "provider_calls": total_provider_calls,
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

    recomputed_exposed = sum(int(int(row["mixed_pools"]) >= min_per_stream) for row in stream_rows)
    require(recomputed_exposed == exposed, "exposed-stream count does not recompute")
    require(bool(support.get("primary_hard_gate_pass")) == (mixed >= min_mixed and exposed >= min_exposed), "hard-gate flag is inconsistent")
    require(bool(support.get("family_generalization_gate_pass")) == (supported_families >= min_families), "family gate flag is inconsistent")

    run_root = Path(contract["run_root"])
    split = load_json(Path(contract["suite"]["root"]) / "r17_split_manifest.json")
    frozen_streams = list(contract["streams"])
    require(list(split["e1_update_streams"].keys()) == frozen_streams, "stream manifest drift")
    expected_tasks = [str(task) for stream_id in frozen_streams for task in split["e1_update_streams"][stream_id]]
    require(len(expected_tasks) == 96 and len(set(expected_tasks)) == 96, "frozen update set must contain 96 unique tasks")

    pool_sha: dict[str, str] = {}
    mixed_recomputed = 0
    for task_id in expected_tasks:
        pool_path = run_root / "cases" / task_id / "pool_k8.json"
        require(pool_path.exists(), f"missing frozen K8 pool: {task_id}")
        pool = load_json(pool_path)
        require(pool.get("task_id") == task_id and int(pool.get("k") or 0) == 8, f"invalid K8 pool identity: {task_id}")
        trajectories = pool.get("trajectories") or []
        require(len(trajectories) == 8, f"K8 pool missing trajectory refs: {task_id}")
        scores = [float(row["score"]) for row in trajectories]
        mixed_recomputed += int(min(scores) < 1.0 and max(scores) >= 1.0)
        for row in trajectories:
            trajectory = Path(row["trajectory_path"])
            require(trajectory.exists() and sha_file(trajectory) == row["trajectory_sha256"], f"trajectory SHA drift: {task_id}/{row['rollout_index']}")
        pool_sha[task_id] = sha_file(pool_path)
    require(mixed_recomputed == mixed, "mixed-pool total does not recompute from exact frozen pools")

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
            "pass": hard_pass,
        },
        "family_generalization": {
            "supported_families": supported_families,
            "required_supported_families": min_families,
            "pass": family_pass,
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


===== BOUND ARTIFACT: authority_scope_tests | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/test_e2_r17_actor_authority_scope.py =====
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_e2_r17_actor_pool import validate_authority


class ActorAuthorityScopeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.split = {"development": ["dev-1"], "e1_update_streams": {"s0": ["t0", "t1"]}}

    def _auth(self, root: Path, *, tasks: list[str], exact_k: int = 8) -> Path:
        path = root / "auth.json"
        path.write_text(
            json.dumps(
                {
                    "status": "AUTHORIZED_E1",
                    "authority": {"scientific_experiment": True, "e1_b": False},
                    "execution_scope": {
                        "allowed_modes": ["e1"],
                        "allowed_task_ids": tasks,
                        "exact_k": exact_k,
                        "allow_noninitial_skill": False,
                    },
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_scoped_authority_accepts_exact_task_subset_and_k(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = self._auth(Path(tmp), tasks=["t0", "t1"])
            payload, digest = validate_authority(
                mode="e1", authorization=auth, task_ids=["t0"], split=self.split, k=8
            )
            self.assertEqual(payload["status"], "AUTHORIZED_E1")
            self.assertEqual(len(digest), 64)

    def test_scoped_authority_rejects_out_of_scope_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = self._auth(Path(tmp), tasks=["t0"])
            with self.assertRaises(RuntimeError):
                validate_authority(
                    mode="e1", authorization=auth, task_ids=["t1"], split=self.split, k=8
                )

    def test_scoped_authority_rejects_wrong_k_or_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = self._auth(Path(tmp), tasks=["t0"])
            with self.assertRaises(RuntimeError):
                validate_authority(
                    mode="e1", authorization=auth, task_ids=["t0"], split=self.split, k=4
                )
            with self.assertRaises(RuntimeError):
                validate_authority(
                    mode="public_externality", authorization=auth, task_ids=["t0"], split=self.split, k=8
                )

    def test_protocol_smoke_still_requires_development_only(self) -> None:
        payload, digest = validate_authority(
            mode="protocol_smoke", authorization=None, task_ids=["dev-1"], split=self.split, k=1
        )
        self.assertIsNone(payload)
        self.assertIsNone(digest)
        with self.assertRaises(RuntimeError):
            validate_authority(
                mode="protocol_smoke", authorization=None, task_ids=["t0"], split=self.split, k=1
            )


if __name__ == "__main__":
    unittest.main()


===== BOUND ARTIFACT: actor_model_identity_adjudication | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-model-identity-adjudication-20260828.json =====
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
      "path": "generated/e2-r17-e1-a-model-identity-qualification-20260828.json",
      "sha256": "f734dd4c5815a447e6fbf2bfacae26c5b60a10ac359d03e5838760793e077c9a",
      "status": "PASS"
    }
  ],
  "created_at_utc": "2026-08-28T13:17:46+00:00",
  "private_credentials_included": false,
  "raw_response_ids_included": false,
  "requested_and_resolved": {
    "deepseek-v4-pro": {
      "requested": "deepseek-v4-pro",
      "resolved": "deepseek-v4-pro-ga-260813",
      "source_artifact": "generated/e2-r17-e1-a-model-identity-qualification-20260828.json",
      "source_artifact_sha256": "f734dd4c5815a447e6fbf2bfacae26c5b60a10ac359d03e5838760793e077c9a",
      "thinking_requested": "disabled"
    },
    "kimi-k3": {
      "requested": "kimi-k3",
      "resolved": "kimi-k3",
      "source_artifact": "generated/e2-r17-e1-a-model-identity-qualification-20260828.json",
      "source_artifact_sha256": "f734dd4c5815a447e6fbf2bfacae26c5b60a10ac359d03e5838760793e077c9a",
      "thinking_requested": "disabled"
    }
  },
  "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
  "schema_version": "1.0",
  "status": "PASS_CURRENT_REVIEW_TRANCHE"
}


===== BOUND ARTIFACT: review_identity_qualification | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-e1-a-model-identity-qualification-20260828.json =====
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
  "created_at_utc": "2026-08-28T13:17:46+00:00",
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
      "response_id_sha256": "8013c97cde61d073ce13284e9f78044fc0e08f63ec2704b49e040f6f137766d4",
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
      "response_id_sha256": "9498fda451dfcf1288e08071a4ebeadd10d3e6edc018b628273511ed166d320e",
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


===== BOUND ARTIFACT: controlled_metadata | /data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2/r17_controlled_metadata.json =====
[
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        69.0,
        102.0,
        115.0,
        130.0,
        172.0,
        54.0,
        144.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 786.0,
      "Result!B3": 7
    },
    "id": "r17-b0-agj-p0",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        49.0,
        33.0,
        55.0,
        60.0,
        300.0,
        23.0,
        144.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 664.0,
      "Result!B3": 7
    },
    "id": "r17-b0-agj-p1",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        29.0,
        177.0,
        215.0,
        34.0,
        316.0,
        43.0,
        126.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 940.0,
      "Result!B3": 7
    },
    "id": "r17-b0-agj-p2",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        64.0,
        85.0,
        82.0,
        68.0,
        60.0,
        156.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 515.0,
      "Result!B3": 6
    },
    "id": "r17-b0-agj-p3",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        11.0,
        60.0,
        128.0,
        66.0,
        102.0,
        160.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 527.0,
      "Result!B3": 6
    },
    "id": "r17-b0-agj-p4",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        20.0,
        280.0,
        66.0,
        31.0,
        240.0,
        66.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 703.0,
      "Result!B3": 6
    },
    "id": "r17-b0-agj-p5",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        62.0,
        80.0,
        128.0,
        78.0,
        57.0,
        52.0,
        80.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 537.0,
      "Result!B3": 7,
      "Result!B4": 76.71
    },
    "id": "r17-b0-agj-p6",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        65.0,
        180.0,
        154.0,
        29.0,
        63.0,
        36.0,
        92.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 619.0,
      "Result!B3": 7,
      "Result!B4": 88.43
    },
    "id": "r17-b0-agj-p7",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        26.0,
        335.0,
        112.0,
        45.0,
        132.0,
        128.0,
        208.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 986.0,
      "Result!B3": 7,
      "Result!B4": 140.86
    },
    "id": "r17-b0-agj-p8",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        21,
        64,
        189,
        244,
        135,
        132
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 21,
      "Result!B3": 64,
      "Result!B4": 189,
      "Result!B5": 244,
      "Result!B6": 135,
      "Result!B7": 132
    },
    "id": "r17-b0-fmv-p0",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "row_values": [
        13,
        58,
        39,
        256,
        170,
        210
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 13,
      "Result!B3": 58,
      "Result!B4": 39,
      "Result!B5": 256,
      "Result!B6": 170,
      "Result!B7": 210
    },
    "id": "r17-b0-fmv-p1",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "row_values": [
        47,
        72,
        126,
        252,
        105,
        330
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 47,
      "Result!B3": 72,
      "Result!B4": 126,
      "Result!B5": 252,
      "Result!B6": 105,
      "Result!B7": 330
    },
    "id": "r17-b0-fmv-p2",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        12.0,
        45.6,
        78.3,
        112.0,
        76.0,
        329.4,
        14.0,
        95.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 12.0,
      "Result!B3": 45.6,
      "Result!B4": 78.3,
      "Result!B5": 112.0,
      "Result!B6": 76.0,
      "Result!B7": 329.4,
      "Result!B8": 14.0,
      "Result!B9": 95.0
    },
    "id": "r17-b0-fmv-p3",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "row_values": [
        48.0,
        96.9,
        64.8,
        132.0,
        237.5,
        237.6,
        51.0,
        79.8
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 48.0,
      "Result!B3": 96.9,
      "Result!B4": 64.8,
      "Result!B5": 132.0,
      "Result!B6": 237.5,
      "Result!B7": 237.6,
      "Result!B8": 51.0,
      "Result!B9": 79.8
    },
    "id": "r17-b0-fmv-p4",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "row_values": [
        39.0,
        95.0,
        110.7,
        248.0,
        242.25,
        129.6,
        62.0,
        95.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 39.0,
      "Result!B3": 95.0,
      "Result!B4": 110.7,
      "Result!B5": 248.0,
      "Result!B6": 242.25,
      "Result!B7": 129.6,
      "Result!B8": 62.0,
      "Result!B9": 95.0
    },
    "id": "r17-b0-fmv-p5",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        15.12,
        96.14,
        93.31,
        154.0,
        297.54,
        83.16,
        34.56,
        77.33,
        26.24,
        39.6
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 26.24,
      "Result!B11": 39.6,
      "Result!B2": 15.12,
      "Result!B3": 96.14,
      "Result!B4": 93.31,
      "Result!B5": 154.0,
      "Result!B6": 297.54,
      "Result!B7": 83.16,
      "Result!B8": 34.56,
      "Result!B9": 77.33
    },
    "id": "r17-b0-fmv-p6",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "row_values": [
        15.12,
        48.07,
        29.16,
        242.0,
        251.37,
        273.24,
        36.72,
        60.61,
        160.38,
        154.0
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 160.38,
      "Result!B11": 154.0,
      "Result!B2": 15.12,
      "Result!B3": 48.07,
      "Result!B4": 29.16,
      "Result!B5": 242.0,
      "Result!B6": 251.37,
      "Result!B7": 273.24,
      "Result!B8": 36.72,
      "Result!B9": 60.61
    },
    "id": "r17-b0-fmv-p7",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "row_values": [
        69.12,
        35.53,
        52.49,
        176.0,
        87.21,
        267.3,
        10.8,
        123.31,
        186.62,
        74.8
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 186.62,
      "Result!B11": 74.8,
      "Result!B2": 69.12,
      "Result!B3": 35.53,
      "Result!B4": 52.49,
      "Result!B5": 176.0,
      "Result!B6": 87.21,
      "Result!B7": 267.3,
      "Result!B8": 10.8,
      "Result!B9": 123.31
    },
    "id": "r17-b0-fmv-p8",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 361,
      "checksum": 412,
      "row_count": 7,
      "sentinel": "KEEP-r17-b0-ioc-p0"
    },
    "golden_answer_cells": {
      "Result!B2": 412,
      "Result!B3": "KEEP-r17-b0-ioc-p0"
    },
    "id": "r17-b0-ioc-p0",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "active_sum": 258,
      "checksum": 362,
      "row_count": 7,
      "sentinel": "KEEP-r17-b0-ioc-p1"
    },
    "golden_answer_cells": {
      "Result!B2": 362,
      "Result!B3": "KEEP-r17-b0-ioc-p1"
    },
    "id": "r17-b0-ioc-p1",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "active_sum": 235,
      "checksum": 321,
      "row_count": 7,
      "sentinel": "KEEP-r17-b0-ioc-p2"
    },
    "golden_answer_cells": {
      "Result!B2": 321,
      "Result!B3": "KEEP-r17-b0-ioc-p2"
    },
    "id": "r17-b0-ioc-p2",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 266,
      "checksum": 443,
      "row_count": 9,
      "sentinel": "KEEP-r17-b0-ioc-p3"
    },
    "golden_answer_cells": {
      "Result!B2": 443,
      "Result!B3": "KEEP-r17-b0-ioc-p3",
      "Result!B4": 266
    },
    "id": "r17-b0-ioc-p3",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "active_sum": 222,
      "checksum": 342,
      "row_count": 9,
      "sentinel": "KEEP-r17-b0-ioc-p4"
    },
    "golden_answer_cells": {
      "Result!B2": 342,
      "Result!B3": "KEEP-r17-b0-ioc-p4",
      "Result!B4": 222
    },
    "id": "r17-b0-ioc-p4",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "active_sum": 368,
      "checksum": 493,
      "row_count": 9,
      "sentinel": "KEEP-r17-b0-ioc-p5"
    },
    "golden_answer_cells": {
      "Result!B2": 493,
      "Result!B3": "KEEP-r17-b0-ioc-p5",
      "Result!B4": 368
    },
    "id": "r17-b0-ioc-p5",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 358,
      "checksum": 513,
      "row_count": 11,
      "sentinel": "KEEP-r17-b0-ioc-p6"
    },
    "golden_answer_cells": {
      "Result!B2": 513,
      "Result!B3": "KEEP-r17-b0-ioc-p6",
      "Result!B4": 358,
      "Result!B5": 11
    },
    "id": "r17-b0-ioc-p6",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "active_sum": 321,
      "checksum": 456,
      "row_count": 11,
      "sentinel": "KEEP-r17-b0-ioc-p7"
    },
    "golden_answer_cells": {
      "Result!B2": 456,
      "Result!B3": "KEEP-r17-b0-ioc-p7",
      "Result!B4": 321,
      "Result!B5": 11
    },
    "id": "r17-b0-ioc-p7",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "active_sum": 309,
      "checksum": 440,
      "row_count": 11,
      "sentinel": "KEEP-r17-b0-ioc-p8"
    },
    "golden_answer_cells": {
      "Result!B2": 440,
      "Result!B3": "KEEP-r17-b0-ioc-p8",
      "Result!B4": 309,
      "Result!B5": 11
    },
    "id": "r17-b0-ioc-p8",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": [
        [
          2,
          84.0
        ],
        [
          3,
          203.0
        ],
        [
          4,
          137.0
        ],
        [
          5,
          110.0
        ],
        [
          7,
          132.0
        ],
        [
          1,
          38.0
        ],
        [
          2,
          143.0
        ],
        [
          3,
          68.0
        ],
        [
          5,
          148.0
        ],
        [
          6,
          190.0
        ],
        [
          7,
          55.0
        ],
        [
          1,
          51.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1359.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b0-msp-p0",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "kept": [
        [
          2,
          47.0
        ],
        [
          3,
          174.0
        ],
        [
          4,
          114.0
        ],
        [
          5,
          173.0
        ],
        [
          7,
          89.0
        ],
        [
          1,
          34.0
        ],
        [
          2,
          124.0
        ],
        [
          3,
          43.0
        ],
        [
          5,
          81.0
        ],
        [
          6,
          181.0
        ],
        [
          7,
          39.0
        ],
        [
          1,
          196.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1295.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b0-msp-p1",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "kept": [
        [
          2,
          86.0
        ],
        [
          3,
          119.0
        ],
        [
          4,
          67.0
        ],
        [
          5,
          213.0
        ],
        [
          7,
          204.0
        ],
        [
          1,
          202.0
        ],
        [
          2,
          225.0
        ],
        [
          3,
          201.0
        ],
        [
          5,
          59.0
        ],
        [
          6,
          169.0
        ],
        [
          7,
          191.0
        ],
        [
          1,
          212.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1948.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b0-msp-p2",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": [
        [
          2,
          205.0
        ],
        [
          4,
          203.0
        ],
        [
          1,
          40.0
        ],
        [
          3,
          237.0
        ],
        [
          5,
          35.0
        ],
        [
          7,
          185.0
        ],
        [
          4,
          113.0
        ],
        [
          6,
          193.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1211.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b0-msp-p3",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "kept": [
        [
          2,
          121.0
        ],
        [
          4,
          158.0
        ],
        [
          1,
          39.0
        ],
        [
          3,
          194.0
        ],
        [
          5,
          164.0
        ],
        [
          7,
          105.0
        ],
        [
          4,
          83.0
        ],
        [
          6,
          179.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1043.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b0-msp-p4",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "kept": [
        [
          2,
          64.0
        ],
        [
          4,
          91.0
        ],
        [
          1,
          40.0
        ],
        [
          3,
          164.0
        ],
        [
          5,
          175.0
        ],
        [
          7,
          129.0
        ],
        [
          4,
          137.0
        ],
        [
          6,
          59.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 859.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b0-msp-p5",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b0-msp-p6",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b0-msp-p7",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b0-msp-p8",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        108.75,
        131.58,
        151.32,
        98.28,
        291.55,
        295.1,
        30.0,
        202.1,
        214.37,
        243.0
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1766.05
    },
    "id": "r17-b0-ska-p0",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        103.5,
        149.64,
        181.39,
        180.36,
        285.6,
        293.8,
        92.25,
        43.86,
        125.13,
        66.96
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1522.49
    },
    "id": "r17-b0-ska-p1",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        119.25,
        60.2,
        242.5,
        43.2,
        74.97,
        254.8,
        22.5,
        41.28,
        102.82,
        86.4
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 1047.92
    },
    "id": "r17-b0-ska-p2",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        135.0,
        155.66,
        24.25,
        135.0,
        276.08,
        262.6,
        108.75,
        159.96,
        221.16,
        140.4,
        147.56,
        105.3,
        69.0
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1940.72,
      "Result!B3": 1239.48
    },
    "id": "r17-b0-ska-p3",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        112.5,
        50.74,
        46.56,
        138.24,
        138.04,
        54.6,
        46.5,
        206.4,
        116.4,
        232.2,
        259.42,
        36.4,
        45.75
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 1483.75,
      "Result!B3": 1071.06
    },
    "id": "r17-b0-ska-p4",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        185.25,
        18.92,
        70.81,
        232.2,
        141.61,
        292.5,
        186.0,
        214.14,
        39.77,
        64.8,
        254.66,
        273.0,
        15.75
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1989.41,
      "Result!B3": 1607.03
    },
    "id": "r17-b0-ska-p5",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        31.5,
        55.04,
        232.8,
        84.24,
        165.41,
        196.3,
        108.0,
        206.4,
        133.86,
        223.56,
        80.92,
        145.6,
        40.5,
        159.1,
        94.09,
        223.56
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 2180.88,
      "Result!B3": 1809.61,
      "Result!B4": 232.8
    },
    "id": "r17-b0-ska-p6",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        162.0,
        190.92,
        173.63,
        231.12,
        33.32,
        59.8,
        96.0,
        92.02,
        105.73,
        187.92,
        148.75,
        136.5,
        156.0,
        115.24,
        123.19,
        163.08
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 2175.22,
      "Result!B3": 1718.17,
      "Result!B4": 231.12
    },
    "id": "r17-b0-ska-p7",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        138.75,
        26.66,
        46.56,
        158.76,
        295.12,
        185.9,
        111.75,
        110.08,
        26.19,
        144.72,
        259.42,
        283.4,
        52.5,
        42.14,
        153.26,
        54.0
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 2089.21,
      "Result!B3": 1576.65,
      "Result!B4": 295.12
    },
    "id": "r17-b0-ska-p8",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        58,
        62,
        77,
        177,
        125,
        101
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 600,
      "Result!B3": 177
    },
    "id": "r17-b0-tsr-p0",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "target_sheet": "Quarter_2_FINAL",
      "target_values": [
        54,
        36,
        62,
        23,
        27,
        52
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 254,
      "Result!B3": 62
    },
    "id": "r17-b0-tsr-p1",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "target_sheet": "Quarter_3_FINAL",
      "target_values": [
        176,
        130,
        113,
        28,
        113,
        134
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 694,
      "Result!B3": 176
    },
    "id": "r17-b0-tsr-p2",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_4_FINAL",
      "target_values": [
        162,
        72,
        72,
        134,
        85,
        29,
        118,
        76
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 748,
      "Result!B3": 162,
      "Result!B4": 93.5
    },
    "id": "r17-b0-tsr-p3",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        109,
        149,
        105,
        149,
        41,
        127,
        28,
        53
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 761,
      "Result!B3": 149,
      "Result!B4": 95.12
    },
    "id": "r17-b0-tsr-p4",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "target_sheet": "Quarter_2_FINAL",
      "target_values": [
        62,
        72,
        82,
        148,
        64,
        28,
        124,
        34
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 614,
      "Result!B3": 148,
      "Result!B4": 76.75
    },
    "id": "r17-b0-tsr-p5",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 0,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_3_FINAL",
      "target_values": [
        75,
        106,
        55,
        129,
        95,
        34,
        24,
        29,
        143,
        96
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 786,
      "Result!B3": 143,
      "Result!B4": 78.6,
      "Result!B5": 3
    },
    "id": "r17-b0-tsr-p6",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "development",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 0,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "target_sheet": "Quarter_4_FINAL",
      "target_values": [
        70,
        64,
        164,
        77,
        45,
        168,
        106,
        84,
        121,
        22
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 921,
      "Result!B3": 168,
      "Result!B4": 92.1,
      "Result!B5": 4
    },
    "id": "r17-b0-tsr-p7",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "development",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 0,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        74,
        97,
        31,
        144,
        146,
        20,
        55,
        131,
        51,
        97
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 846,
      "Result!B3": 146,
      "Result!B4": 84.6,
      "Result!B5": 3
    },
    "id": "r17-b0-tsr-p8",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "development",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        61.0,
        225.0,
        380.0,
        108.0,
        292.0,
        60.0,
        147.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1273.0,
      "Result!B3": 7
    },
    "id": "r17-b1-agj-p0",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        15.0,
        240.0,
        110.0,
        36.0,
        192.0,
        13.0,
        183.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 789.0,
      "Result!B3": 7
    },
    "id": "r17-b1-agj-p1",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        75.0,
        231.0,
        295.0,
        112.0,
        32.0,
        75.0,
        27.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 847.0,
      "Result!B3": 7
    },
    "id": "r17-b1-agj-p2",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        49.0,
        165.0,
        114.0,
        79.0,
        171.0,
        156.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 734.0,
      "Result!B3": 6
    },
    "id": "r17-b1-agj-p3",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        36.0,
        375.0,
        122.0,
        23.0,
        168.0,
        148.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 872.0,
      "Result!B3": 6
    },
    "id": "r17-b1-agj-p4",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        74.0,
        340.0,
        32.0,
        51.0,
        42.0,
        152.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 691.0,
      "Result!B3": 6
    },
    "id": "r17-b1-agj-p5",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        14.0,
        80.0,
        110.0,
        46.0,
        201.0,
        80.0,
        108.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 639.0,
      "Result!B3": 7,
      "Result!B4": 91.29
    },
    "id": "r17-b1-agj-p6",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        54.0,
        135.0,
        154.0,
        12.0,
        159.0,
        24.0,
        80.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 618.0,
      "Result!B3": 7,
      "Result!B4": 88.29
    },
    "id": "r17-b1-agj-p7",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        49.0,
        180.0,
        112.0,
        42.0,
        93.0,
        60.0,
        96.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 632.0,
      "Result!B3": 7,
      "Result!B4": 90.29
    },
    "id": "r17-b1-agj-p8",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        59,
        36,
        117,
        240,
        110,
        150
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 59,
      "Result!B3": 36,
      "Result!B4": 117,
      "Result!B5": 240,
      "Result!B6": 110,
      "Result!B7": 150
    },
    "id": "r17-b1-fmv-p0",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "row_values": [
        32,
        52,
        72,
        236,
        265,
        264
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 32,
      "Result!B3": 52,
      "Result!B4": 72,
      "Result!B5": 236,
      "Result!B6": 265,
      "Result!B7": 264
    },
    "id": "r17-b1-fmv-p1",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "row_values": [
        46,
        30,
        105,
        220,
        225,
        228
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 46,
      "Result!B3": 30,
      "Result!B4": 105,
      "Result!B5": 220,
      "Result!B6": 225,
      "Result!B7": 228
    },
    "id": "r17-b1-fmv-p2",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        10.0,
        15.2,
        175.5,
        152.0,
        66.5,
        81.0,
        65.0,
        57.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 10.0,
      "Result!B3": 15.2,
      "Result!B4": 175.5,
      "Result!B5": 152.0,
      "Result!B6": 66.5,
      "Result!B7": 81.0,
      "Result!B8": 65.0,
      "Result!B9": 57.0
    },
    "id": "r17-b1-fmv-p3",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "row_values": [
        28.0,
        39.9,
        62.1,
        44.0,
        285.0,
        334.8,
        51.0,
        72.2
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 28.0,
      "Result!B3": 39.9,
      "Result!B4": 62.1,
      "Result!B5": 44.0,
      "Result!B6": 285.0,
      "Result!B7": 334.8,
      "Result!B8": 51.0,
      "Result!B9": 72.2
    },
    "id": "r17-b1-fmv-p4",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "row_values": [
        47.0,
        108.3,
        153.9,
        224.0,
        266.0,
        318.6,
        9.0,
        66.5
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 47.0,
      "Result!B3": 108.3,
      "Result!B4": 153.9,
      "Result!B5": 224.0,
      "Result!B6": 266.0,
      "Result!B7": 318.6,
      "Result!B8": 9.0,
      "Result!B9": 66.5
    },
    "id": "r17-b1-fmv-p5",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        30.24,
        110.77,
        128.3,
        211.2,
        282.15,
        190.08,
        54.0,
        37.62,
        160.38,
        74.8
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 160.38,
      "Result!B11": 74.8,
      "Result!B2": 30.24,
      "Result!B3": 110.77,
      "Result!B4": 128.3,
      "Result!B5": 211.2,
      "Result!B6": 282.15,
      "Result!B7": 190.08,
      "Result!B8": 54.0,
      "Result!B9": 37.62
    },
    "id": "r17-b1-fmv-p6",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "row_values": [
        17.28,
        37.62,
        128.3,
        242.0,
        92.34,
        368.28,
        69.12,
        45.98,
        174.96,
        189.2
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 174.96,
      "Result!B11": 189.2,
      "Result!B2": 17.28,
      "Result!B3": 37.62,
      "Result!B4": 128.3,
      "Result!B5": 242.0,
      "Result!B6": 92.34,
      "Result!B7": 368.28,
      "Result!B8": 69.12,
      "Result!B9": 45.98
    },
    "id": "r17-b1-fmv-p7",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "row_values": [
        21.6,
        110.77,
        148.72,
        154.0,
        87.21,
        53.46,
        36.72,
        16.72,
        37.91,
        198.0
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 37.91,
      "Result!B11": 198.0,
      "Result!B2": 21.6,
      "Result!B3": 110.77,
      "Result!B4": 148.72,
      "Result!B5": 154.0,
      "Result!B6": 87.21,
      "Result!B7": 53.46,
      "Result!B8": 36.72,
      "Result!B9": 16.72
    },
    "id": "r17-b1-fmv-p8",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 209,
      "checksum": 328,
      "row_count": 7,
      "sentinel": "KEEP-r17-b1-ioc-p0"
    },
    "golden_answer_cells": {
      "Result!B2": 328,
      "Result!B3": "KEEP-r17-b1-ioc-p0"
    },
    "id": "r17-b1-ioc-p0",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "active_sum": 211,
      "checksum": 374,
      "row_count": 7,
      "sentinel": "KEEP-r17-b1-ioc-p1"
    },
    "golden_answer_cells": {
      "Result!B2": 374,
      "Result!B3": "KEEP-r17-b1-ioc-p1"
    },
    "id": "r17-b1-ioc-p1",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "active_sum": 155,
      "checksum": 244,
      "row_count": 7,
      "sentinel": "KEEP-r17-b1-ioc-p2"
    },
    "golden_answer_cells": {
      "Result!B2": 244,
      "Result!B3": "KEEP-r17-b1-ioc-p2"
    },
    "id": "r17-b1-ioc-p2",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 306,
      "checksum": 518,
      "row_count": 9,
      "sentinel": "KEEP-r17-b1-ioc-p3"
    },
    "golden_answer_cells": {
      "Result!B2": 518,
      "Result!B3": "KEEP-r17-b1-ioc-p3",
      "Result!B4": 306
    },
    "id": "r17-b1-ioc-p3",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "active_sum": 216,
      "checksum": 318,
      "row_count": 9,
      "sentinel": "KEEP-r17-b1-ioc-p4"
    },
    "golden_answer_cells": {
      "Result!B2": 318,
      "Result!B3": "KEEP-r17-b1-ioc-p4",
      "Result!B4": 216
    },
    "id": "r17-b1-ioc-p4",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "active_sum": 284,
      "checksum": 406,
      "row_count": 9,
      "sentinel": "KEEP-r17-b1-ioc-p5"
    },
    "golden_answer_cells": {
      "Result!B2": 406,
      "Result!B3": "KEEP-r17-b1-ioc-p5",
      "Result!B4": 284
    },
    "id": "r17-b1-ioc-p5",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 324,
      "checksum": 529,
      "row_count": 11,
      "sentinel": "KEEP-r17-b1-ioc-p6"
    },
    "golden_answer_cells": {
      "Result!B2": 529,
      "Result!B3": "KEEP-r17-b1-ioc-p6",
      "Result!B4": 324,
      "Result!B5": 11
    },
    "id": "r17-b1-ioc-p6",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "active_sum": 400,
      "checksum": 498,
      "row_count": 11,
      "sentinel": "KEEP-r17-b1-ioc-p7"
    },
    "golden_answer_cells": {
      "Result!B2": 498,
      "Result!B3": "KEEP-r17-b1-ioc-p7",
      "Result!B4": 400,
      "Result!B5": 11
    },
    "id": "r17-b1-ioc-p7",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "active_sum": 448,
      "checksum": 564,
      "row_count": 11,
      "sentinel": "KEEP-r17-b1-ioc-p8"
    },
    "golden_answer_cells": {
      "Result!B2": 564,
      "Result!B3": "KEEP-r17-b1-ioc-p8",
      "Result!B4": 448,
      "Result!B5": 11
    },
    "id": "r17-b1-ioc-p8",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": [
        [
          2,
          92.0
        ],
        [
          3,
          230.0
        ],
        [
          4,
          119.0
        ],
        [
          5,
          64.0
        ],
        [
          7,
          109.0
        ],
        [
          1,
          43.0
        ],
        [
          2,
          105.0
        ],
        [
          3,
          163.0
        ],
        [
          5,
          118.0
        ],
        [
          6,
          167.0
        ],
        [
          7,
          79.0
        ],
        [
          1,
          127.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1416.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b1-msp-p0",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "kept": [
        [
          2,
          186.0
        ],
        [
          3,
          81.0
        ],
        [
          4,
          120.0
        ],
        [
          5,
          73.0
        ],
        [
          7,
          222.0
        ],
        [
          1,
          136.0
        ],
        [
          2,
          239.0
        ],
        [
          3,
          110.0
        ],
        [
          5,
          75.0
        ],
        [
          6,
          149.0
        ],
        [
          7,
          77.0
        ],
        [
          1,
          212.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1680.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b1-msp-p1",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "kept": [
        [
          2,
          118.0
        ],
        [
          3,
          119.0
        ],
        [
          4,
          174.0
        ],
        [
          5,
          35.0
        ],
        [
          7,
          57.0
        ],
        [
          1,
          156.0
        ],
        [
          2,
          174.0
        ],
        [
          3,
          41.0
        ],
        [
          5,
          92.0
        ],
        [
          6,
          224.0
        ],
        [
          7,
          42.0
        ],
        [
          1,
          199.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1431.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b1-msp-p2",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": [
        [
          2,
          220.0
        ],
        [
          4,
          203.0
        ],
        [
          1,
          218.0
        ],
        [
          3,
          222.0
        ],
        [
          5,
          221.0
        ],
        [
          7,
          178.0
        ],
        [
          4,
          91.0
        ],
        [
          6,
          202.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1555.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b1-msp-p3",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "kept": [
        [
          2,
          132.0
        ],
        [
          4,
          123.0
        ],
        [
          1,
          201.0
        ],
        [
          3,
          218.0
        ],
        [
          5,
          113.0
        ],
        [
          7,
          165.0
        ],
        [
          4,
          162.0
        ],
        [
          6,
          104.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1218.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b1-msp-p4",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "kept": [
        [
          2,
          119.0
        ],
        [
          4,
          157.0
        ],
        [
          1,
          32.0
        ],
        [
          3,
          225.0
        ],
        [
          5,
          195.0
        ],
        [
          7,
          68.0
        ],
        [
          4,
          120.0
        ],
        [
          6,
          106.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1022.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b1-msp-p5",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b1-msp-p6",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b1-msp-p7",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b1-msp-p8",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        94.5,
        115.24,
        100.88,
        223.56,
        140.42,
        325.0,
        23.25,
        72.24,
        178.48,
        95.04
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1368.61
    },
    "id": "r17-b1-ska-p0",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        28.5,
        131.58,
        108.64,
        225.72,
        277.27,
        57.2,
        168.75,
        53.32,
        77.6,
        100.44
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1229.02
    },
    "id": "r17-b1-ska-p1",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        175.5,
        168.56,
        112.52,
        119.88,
        159.46,
        67.6,
        100.5,
        54.18,
        45.59,
        261.36
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 1265.15
    },
    "id": "r17-b1-ska-p2",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        93.75,
        70.52,
        149.38,
        35.64,
        271.32,
        180.7,
        59.25,
        177.16,
        77.6,
        177.12,
        174.93,
        145.6,
        80.25
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1693.22,
      "Result!B3": 1170.3
    },
    "id": "r17-b1-ska-p3",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        148.5,
        80.84,
        159.08,
        147.96,
        218.96,
        273.0,
        114.0,
        99.76,
        197.88,
        244.08,
        153.51,
        197.6,
        129.0
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 2164.17,
      "Result!B3": 1469.83
    },
    "id": "r17-b1-ska-p4",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        39.75,
        56.76,
        218.25,
        36.72,
        273.7,
        179.4,
        132.75,
        33.54,
        156.17,
        113.4,
        90.44,
        321.1,
        134.25
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1786.23,
      "Result!B3": 1182.36
    },
    "id": "r17-b1-ska-p5",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        22.5,
        118.68,
        56.26,
        43.2,
        232.05,
        44.2,
        39.75,
        135.02,
        60.14,
        250.56,
        289.17,
        258.7,
        136.5,
        141.04,
        38.8,
        30.24
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 1896.81,
      "Result!B3": 1445.62,
      "Result!B4": 289.17
    },
    "id": "r17-b1-ska-p6",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        144.0,
        176.3,
        232.8,
        111.24,
        226.1,
        33.8,
        48.75,
        35.26,
        164.9,
        71.28,
        239.19,
        132.6,
        70.5,
        166.84,
        183.33,
        45.36
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 2082.25,
      "Result!B3": 1476.75,
      "Result!B4": 239.19
    },
    "id": "r17-b1-ska-p7",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        146.25,
        91.16,
        191.09,
        98.28,
        166.6,
        150.8,
        33.0,
        163.4,
        195.94,
        92.88,
        132.09,
        119.6,
        54.75,
        73.96,
        46.56,
        211.68
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1968.04,
      "Result!B3": 1404.5,
      "Result!B4": 211.68
    },
    "id": "r17-b1-ska-p8",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        81,
        122,
        53,
        24,
        20,
        118
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 418,
      "Result!B3": 122
    },
    "id": "r17-b1-tsr-p0",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "target_sheet": "Quarter_2_FINAL",
      "target_values": [
        54,
        142,
        108,
        109,
        137,
        58
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 608,
      "Result!B3": 142
    },
    "id": "r17-b1-tsr-p1",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "target_sheet": "Quarter_3_FINAL",
      "target_values": [
        33,
        153,
        149,
        44,
        57,
        93
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 529,
      "Result!B3": 153
    },
    "id": "r17-b1-tsr-p2",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_4_FINAL",
      "target_values": [
        21,
        29,
        66,
        29,
        109,
        40,
        112,
        73
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 479,
      "Result!B3": 112,
      "Result!B4": 59.88
    },
    "id": "r17-b1-tsr-p3",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        126,
        61,
        43,
        58,
        65,
        109,
        165,
        132
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 759,
      "Result!B3": 165,
      "Result!B4": 94.88
    },
    "id": "r17-b1-tsr-p4",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "target_sheet": "Quarter_2_FINAL",
      "target_values": [
        102,
        119,
        176,
        56,
        159,
        149,
        123,
        84
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 968,
      "Result!B3": 176,
      "Result!B4": 121.0
    },
    "id": "r17-b1-tsr-p5",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 1,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_3_FINAL",
      "target_values": [
        65,
        58,
        151,
        138,
        149,
        20,
        163,
        146,
        48,
        162
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1100,
      "Result!B3": 163,
      "Result!B4": 110.0,
      "Result!B5": 6
    },
    "id": "r17-b1-tsr-p6",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e0_calibration",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 1,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "target_sheet": "Quarter_4_FINAL",
      "target_values": [
        27,
        116,
        76,
        83,
        135,
        94,
        127,
        117,
        155,
        26
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 956,
      "Result!B3": 155,
      "Result!B4": 95.6,
      "Result!B5": 5
    },
    "id": "r17-b1-tsr-p7",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e0_calibration",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 1,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        43,
        76,
        133,
        29,
        88,
        130,
        59,
        27,
        108,
        118
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 811,
      "Result!B3": 133,
      "Result!B4": 81.1,
      "Result!B5": 4
    },
    "id": "r17-b1-tsr-p8",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e0_calibration",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        34.0,
        237.0,
        340.0,
        102.0,
        120.0,
        77.0,
        51.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 961.0,
      "Result!B3": 7
    },
    "id": "r17-b2-agj-p0",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        53.0,
        57.0,
        40.0,
        114.0,
        304.0,
        63.0,
        96.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 727.0,
      "Result!B3": 7
    },
    "id": "r17-b2-agj-p1",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        28.0,
        45.0,
        170.0,
        16.0,
        100.0,
        66.0,
        111.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 536.0,
      "Result!B3": 7
    },
    "id": "r17-b2-agj-p2",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        42.0,
        355.0,
        74.0,
        39.0,
        201.0,
        20.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 731.0,
      "Result!B3": 6
    },
    "id": "r17-b2-agj-p3",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        63.0,
        230.0,
        126.0,
        38.0,
        219.0,
        86.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 762.0,
      "Result!B3": 6
    },
    "id": "r17-b2-agj-p4",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        31.0,
        125.0,
        20.0,
        31.0,
        60.0,
        122.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 389.0,
      "Result!B3": 6
    },
    "id": "r17-b2-agj-p5",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        28.0,
        60.0,
        64.0,
        12.0,
        186.0,
        112.0,
        220.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 682.0,
      "Result!B3": 7,
      "Result!B4": 97.43
    },
    "id": "r17-b2-agj-p6",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        65.0,
        215.0,
        90.0,
        27.0,
        66.0,
        58.0,
        304.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 825.0,
      "Result!B3": 7,
      "Result!B4": 117.86
    },
    "id": "r17-b2-agj-p7",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        54.0,
        325.0,
        32.0,
        37.0,
        63.0,
        104.0,
        32.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 647.0,
      "Result!B3": 7,
      "Result!B4": 92.43
    },
    "id": "r17-b2-agj-p8",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        8,
        34,
        165,
        32,
        95,
        138
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 8,
      "Result!B3": 34,
      "Result!B4": 165,
      "Result!B5": 32,
      "Result!B6": 95,
      "Result!B7": 138
    },
    "id": "r17-b2-fmv-p0",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "row_values": [
        50,
        130,
        87,
        188,
        230,
        156
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 50,
      "Result!B3": 130,
      "Result!B4": 87,
      "Result!B5": 188,
      "Result!B6": 230,
      "Result!B7": 156
    },
    "id": "r17-b2-fmv-p1",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "row_values": [
        28,
        76,
        120,
        156,
        240,
        348
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 28,
      "Result!B3": 76,
      "Result!B4": 120,
      "Result!B5": 156,
      "Result!B6": 240,
      "Result!B7": 348
    },
    "id": "r17-b2-fmv-p2",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        40.0,
        34.2,
        167.4,
        220.0,
        133.0,
        297.0,
        41.0,
        49.4
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 40.0,
      "Result!B3": 34.2,
      "Result!B4": 167.4,
      "Result!B5": 220.0,
      "Result!B6": 133.0,
      "Result!B7": 297.0,
      "Result!B8": 41.0,
      "Result!B9": 49.4
    },
    "id": "r17-b2-fmv-p3",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "row_values": [
        51.0,
        95.0,
        94.5,
        256.0,
        42.75,
        48.6,
        59.0,
        110.2
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 51.0,
      "Result!B3": 95.0,
      "Result!B4": 94.5,
      "Result!B5": 256.0,
      "Result!B6": 42.75,
      "Result!B7": 48.6,
      "Result!B8": 59.0,
      "Result!B9": 110.2
    },
    "id": "r17-b2-fmv-p4",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "row_values": [
        34.0,
        117.8,
        37.8,
        176.0,
        90.25,
        43.2,
        59.0,
        117.8
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 34.0,
      "Result!B3": 117.8,
      "Result!B4": 37.8,
      "Result!B5": 176.0,
      "Result!B6": 90.25,
      "Result!B7": 43.2,
      "Result!B8": 59.0,
      "Result!B9": 117.8
    },
    "id": "r17-b2-fmv-p5",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        50.76,
        110.77,
        122.47,
        286.0,
        261.63,
        255.42,
        46.44,
        18.81,
        107.89,
        184.8
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 107.89,
      "Result!B11": 184.8,
      "Result!B2": 50.76,
      "Result!B3": 110.77,
      "Result!B4": 122.47,
      "Result!B5": 286.0,
      "Result!B6": 261.63,
      "Result!B7": 255.42,
      "Result!B8": 46.44,
      "Result!B9": 18.81
    },
    "id": "r17-b2-fmv-p6",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "row_values": [
        59.4,
        18.81,
        157.46,
        39.6,
        112.86,
        344.52,
        66.96,
        100.32,
        61.24,
        145.2
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 61.24,
      "Result!B11": 145.2,
      "Result!B2": 59.4,
      "Result!B3": 18.81,
      "Result!B4": 157.46,
      "Result!B5": 39.6,
      "Result!B6": 112.86,
      "Result!B7": 344.52,
      "Result!B8": 66.96,
      "Result!B9": 100.32
    },
    "id": "r17-b2-fmv-p7",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "row_values": [
        44.28,
        104.5,
        174.96,
        30.8,
        159.03,
        332.64,
        12.96,
        22.99,
        128.3,
        88.0
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 128.3,
      "Result!B11": 88.0,
      "Result!B2": 44.28,
      "Result!B3": 104.5,
      "Result!B4": 174.96,
      "Result!B5": 30.8,
      "Result!B6": 159.03,
      "Result!B7": 332.64,
      "Result!B8": 12.96,
      "Result!B9": 22.99
    },
    "id": "r17-b2-fmv-p8",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 190,
      "checksum": 323,
      "row_count": 7,
      "sentinel": "KEEP-r17-b2-ioc-p0"
    },
    "golden_answer_cells": {
      "Result!B2": 323,
      "Result!B3": "KEEP-r17-b2-ioc-p0"
    },
    "id": "r17-b2-ioc-p0",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "active_sum": 305,
      "checksum": 375,
      "row_count": 7,
      "sentinel": "KEEP-r17-b2-ioc-p1"
    },
    "golden_answer_cells": {
      "Result!B2": 375,
      "Result!B3": "KEEP-r17-b2-ioc-p1"
    },
    "id": "r17-b2-ioc-p1",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "active_sum": 279,
      "checksum": 341,
      "row_count": 7,
      "sentinel": "KEEP-r17-b2-ioc-p2"
    },
    "golden_answer_cells": {
      "Result!B2": 341,
      "Result!B3": "KEEP-r17-b2-ioc-p2"
    },
    "id": "r17-b2-ioc-p2",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 130,
      "checksum": 224,
      "row_count": 9,
      "sentinel": "KEEP-r17-b2-ioc-p3"
    },
    "golden_answer_cells": {
      "Result!B2": 224,
      "Result!B3": "KEEP-r17-b2-ioc-p3",
      "Result!B4": 130
    },
    "id": "r17-b2-ioc-p3",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "active_sum": 205,
      "checksum": 284,
      "row_count": 9,
      "sentinel": "KEEP-r17-b2-ioc-p4"
    },
    "golden_answer_cells": {
      "Result!B2": 284,
      "Result!B3": "KEEP-r17-b2-ioc-p4",
      "Result!B4": 205
    },
    "id": "r17-b2-ioc-p4",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "active_sum": 277,
      "checksum": 380,
      "row_count": 9,
      "sentinel": "KEEP-r17-b2-ioc-p5"
    },
    "golden_answer_cells": {
      "Result!B2": 380,
      "Result!B3": "KEEP-r17-b2-ioc-p5",
      "Result!B4": 277
    },
    "id": "r17-b2-ioc-p5",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 351,
      "checksum": 431,
      "row_count": 11,
      "sentinel": "KEEP-r17-b2-ioc-p6"
    },
    "golden_answer_cells": {
      "Result!B2": 431,
      "Result!B3": "KEEP-r17-b2-ioc-p6",
      "Result!B4": 351,
      "Result!B5": 11
    },
    "id": "r17-b2-ioc-p6",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "active_sum": 296,
      "checksum": 385,
      "row_count": 11,
      "sentinel": "KEEP-r17-b2-ioc-p7"
    },
    "golden_answer_cells": {
      "Result!B2": 385,
      "Result!B3": "KEEP-r17-b2-ioc-p7",
      "Result!B4": 296,
      "Result!B5": 11
    },
    "id": "r17-b2-ioc-p7",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "active_sum": 351,
      "checksum": 452,
      "row_count": 11,
      "sentinel": "KEEP-r17-b2-ioc-p8"
    },
    "golden_answer_cells": {
      "Result!B2": 452,
      "Result!B3": "KEEP-r17-b2-ioc-p8",
      "Result!B4": 351,
      "Result!B5": 11
    },
    "id": "r17-b2-ioc-p8",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": [
        [
          2,
          186.0
        ],
        [
          3,
          76.0
        ],
        [
          4,
          100.0
        ],
        [
          5,
          123.0
        ],
        [
          7,
          45.0
        ],
        [
          1,
          222.0
        ],
        [
          2,
          136.0
        ],
        [
          3,
          149.0
        ],
        [
          5,
          57.0
        ],
        [
          6,
          32.0
        ],
        [
          7,
          185.0
        ],
        [
          1,
          87.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1398.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b2-msp-p0",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "kept": [
        [
          2,
          228.0
        ],
        [
          3,
          214.0
        ],
        [
          4,
          110.0
        ],
        [
          5,
          175.0
        ],
        [
          7,
          192.0
        ],
        [
          1,
          200.0
        ],
        [
          2,
          239.0
        ],
        [
          3,
          207.0
        ],
        [
          5,
          38.0
        ],
        [
          6,
          166.0
        ],
        [
          7,
          229.0
        ],
        [
          1,
          226.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 2224.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b2-msp-p1",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "kept": [
        [
          2,
          51.0
        ],
        [
          3,
          160.0
        ],
        [
          4,
          218.0
        ],
        [
          5,
          193.0
        ],
        [
          7,
          65.0
        ],
        [
          1,
          98.0
        ],
        [
          2,
          42.0
        ],
        [
          3,
          80.0
        ],
        [
          5,
          212.0
        ],
        [
          6,
          163.0
        ],
        [
          7,
          123.0
        ],
        [
          1,
          200.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1605.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b2-msp-p2",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": [
        [
          2,
          79.0
        ],
        [
          4,
          205.0
        ],
        [
          1,
          169.0
        ],
        [
          3,
          73.0
        ],
        [
          5,
          104.0
        ],
        [
          7,
          64.0
        ],
        [
          4,
          82.0
        ],
        [
          6,
          152.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 928.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b2-msp-p3",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "kept": [
        [
          2,
          60.0
        ],
        [
          4,
          166.0
        ],
        [
          1,
          215.0
        ],
        [
          3,
          199.0
        ],
        [
          5,
          110.0
        ],
        [
          7,
          41.0
        ],
        [
          4,
          232.0
        ],
        [
          6,
          107.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1130.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b2-msp-p4",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "kept": [
        [
          2,
          179.0
        ],
        [
          4,
          140.0
        ],
        [
          1,
          173.0
        ],
        [
          3,
          128.0
        ],
        [
          5,
          113.0
        ],
        [
          7,
          169.0
        ],
        [
          4,
          224.0
        ],
        [
          6,
          46.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1172.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b2-msp-p5",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b2-msp-p6",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b2-msp-p7",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b2-msp-p8",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        17.25,
        61.06,
        136.77,
        264.6,
        201.11,
        200.2,
        35.25,
        126.42,
        96.03,
        54.0
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1192.69
    },
    "id": "r17-b2-ska-p0",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        39.0,
        30.96,
        24.25,
        182.52,
        39.27,
        149.5,
        71.25,
        141.04,
        166.84,
        220.32
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1064.95
    },
    "id": "r17-b2-ska-p1",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        66.0,
        52.46,
        86.33,
        261.36,
        155.89,
        26.0,
        119.25,
        130.72,
        163.93,
        38.88
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 1100.82
    },
    "id": "r17-b2-ska-p2",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        67.5,
        85.14,
        230.86,
        238.68,
        184.45,
        106.6,
        50.25,
        29.24,
        86.33,
        157.68,
        220.15,
        72.8,
        114.0
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1643.68,
      "Result!B3": 1191.4
    },
    "id": "r17-b2-ska-p3",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        26.25,
        30.1,
        202.73,
        193.32,
        145.18,
        58.5,
        134.25,
        144.48,
        196.91,
        200.88,
        296.31,
        93.6,
        49.5
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 1772.01,
      "Result!B3": 1354.17
    },
    "id": "r17-b2-ska-p4",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        133.5,
        147.06,
        115.43,
        222.48,
        260.61,
        256.1,
        185.25,
        132.44,
        51.41,
        267.84,
        241.57,
        117.0,
        137.25
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 2267.94,
      "Result!B3": 1685.17
    },
    "id": "r17-b2-ska-p5",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        165.0,
        141.9,
        160.05,
        167.4,
        255.85,
        296.4,
        75.0,
        52.46,
        21.34,
        206.28,
        248.71,
        128.7,
        49.5,
        35.26,
        240.56,
        29.16
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 2273.57,
      "Result!B3": 1781.88,
      "Result!B4": 296.4
    },
    "id": "r17-b2-ska-p6",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        59.25,
        70.52,
        127.07,
        65.88,
        274.89,
        109.2,
        46.5,
        156.52,
        118.34,
        219.24,
        234.43,
        128.7,
        26.25,
        26.66,
        136.77,
        115.56
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1915.78,
      "Result!B3": 1437.05,
      "Result!B4": 274.89
    },
    "id": "r17-b2-ska-p7",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        173.25,
        17.2,
        179.45,
        259.2,
        184.45,
        97.5,
        50.25,
        19.78,
        110.58,
        174.96,
        103.53,
        198.9,
        98.25,
        153.08,
        230.86,
        128.52
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 2179.76,
      "Result!B3": 1613.23,
      "Result!B4": 259.2
    },
    "id": "r17-b2-ska-p8",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        73,
        82,
        124,
        121,
        172,
        122
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 694,
      "Result!B3": 172
    },
    "id": "r17-b2-tsr-p0",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "target_sheet": "Quarter_2_FINAL",
      "target_values": [
        101,
        36,
        54,
        71,
        48,
        173
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 483,
      "Result!B3": 173
    },
    "id": "r17-b2-tsr-p1",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "target_sheet": "Quarter_3_FINAL",
      "target_values": [
        107,
        42,
        51,
        176,
        163,
        88
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 627,
      "Result!B3": 176
    },
    "id": "r17-b2-tsr-p2",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_4_FINAL",
      "target_values": [
        172,
        39,
        24,
        180,
        115,
        157,
        169,
        33
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 889,
      "Result!B3": 180,
      "Result!B4": 111.12
    },
    "id": "r17-b2-tsr-p3",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        155,
        165,
        49,
        116,
        131,
        62,
        78,
        77
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 833,
      "Result!B3": 165,
      "Result!B4": 104.12
    },
    "id": "r17-b2-tsr-p4",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "target_sheet": "Quarter_2_FINAL",
      "target_values": [
        84,
        179,
        168,
        52,
        89,
        116,
        138,
        134
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 960,
      "Result!B3": 179,
      "Result!B4": 120.0
    },
    "id": "r17-b2-tsr-p5",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 2,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_3_FINAL",
      "target_values": [
        80,
        142,
        41,
        171,
        47,
        38,
        172,
        160,
        26,
        64
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 941,
      "Result!B3": 172,
      "Result!B4": 94.1,
      "Result!B5": 4
    },
    "id": "r17-b2-tsr-p6",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 2,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "target_sheet": "Quarter_4_FINAL",
      "target_values": [
        124,
        123,
        33,
        32,
        25,
        123,
        52,
        104,
        35,
        36
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 687,
      "Result!B3": 124,
      "Result!B4": 68.7,
      "Result!B5": 4
    },
    "id": "r17-b2-tsr-p7",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 2,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        149,
        43,
        124,
        90,
        77,
        163,
        145,
        50,
        34,
        166
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1041,
      "Result!B3": 166,
      "Result!B4": 104.1,
      "Result!B5": 5
    },
    "id": "r17-b2-tsr-p8",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        38.0,
        240.0,
        230.0,
        26.0,
        268.0,
        25.0,
        141.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 968.0,
      "Result!B3": 7
    },
    "id": "r17-b3-agj-p0",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        45.0,
        129.0,
        50.0,
        136.0,
        208.0,
        16.0,
        27.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 611.0,
      "Result!B3": 7
    },
    "id": "r17-b3-agj-p1",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        64.0,
        42.0,
        195.0,
        128.0,
        188.0,
        16.0,
        93.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 726.0,
      "Result!B3": 7
    },
    "id": "r17-b3-agj-p2",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        65.0,
        390.0,
        158.0,
        52.0,
        144.0,
        120.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 929.0,
      "Result!B3": 6
    },
    "id": "r17-b3-agj-p3",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        53.0,
        145.0,
        88.0,
        22.0,
        207.0,
        100.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 615.0,
      "Result!B3": 6
    },
    "id": "r17-b3-agj-p4",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        54.0,
        260.0,
        74.0,
        11.0,
        213.0,
        146.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 758.0,
      "Result!B3": 6
    },
    "id": "r17-b3-agj-p5",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        58.0,
        190.0,
        92.0,
        10.0,
        123.0,
        70.0,
        44.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 587.0,
      "Result!B3": 7,
      "Result!B4": 83.86
    },
    "id": "r17-b3-agj-p6",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        19.0,
        325.0,
        86.0,
        12.0,
        141.0,
        148.0,
        240.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 971.0,
      "Result!B3": 7,
      "Result!B4": 138.71
    },
    "id": "r17-b3-agj-p7",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        30.0,
        215.0,
        104.0,
        12.0,
        201.0,
        70.0,
        176.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 808.0,
      "Result!B3": 7,
      "Result!B4": 115.43
    },
    "id": "r17-b3-agj-p8",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        19,
        122,
        72,
        208,
        285,
        384
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 19,
      "Result!B3": 122,
      "Result!B4": 72,
      "Result!B5": 208,
      "Result!B6": 285,
      "Result!B7": 384
    },
    "id": "r17-b3-fmv-p0",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "row_values": [
        29,
        78,
        171,
        100,
        305,
        138
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 29,
      "Result!B3": 78,
      "Result!B4": 171,
      "Result!B5": 100,
      "Result!B6": 305,
      "Result!B7": 138
    },
    "id": "r17-b3-fmv-p1",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "row_values": [
        8,
        100,
        159,
        156,
        195,
        240
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 8,
      "Result!B3": 100,
      "Result!B4": 159,
      "Result!B5": 156,
      "Result!B6": 195,
      "Result!B7": 240
    },
    "id": "r17-b3-fmv-p2",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        37.0,
        100.7,
        175.5,
        64.0,
        90.25,
        151.2,
        47.0,
        89.3
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 37.0,
      "Result!B3": 100.7,
      "Result!B4": 175.5,
      "Result!B5": 64.0,
      "Result!B6": 90.25,
      "Result!B7": 151.2,
      "Result!B8": 47.0,
      "Result!B9": 89.3
    },
    "id": "r17-b3-fmv-p3",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "row_values": [
        41.0,
        51.3,
        153.9,
        116.0,
        199.5,
        259.2,
        11.0,
        108.3
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 41.0,
      "Result!B3": 51.3,
      "Result!B4": 153.9,
      "Result!B5": 116.0,
      "Result!B6": 199.5,
      "Result!B7": 259.2,
      "Result!B8": 11.0,
      "Result!B9": 108.3
    },
    "id": "r17-b3-fmv-p4",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "row_values": [
        36.0,
        121.6,
        75.6,
        80.0,
        232.75,
        307.8,
        40.0,
        79.8
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 36.0,
      "Result!B3": 121.6,
      "Result!B4": 75.6,
      "Result!B5": 80.0,
      "Result!B6": 232.75,
      "Result!B7": 307.8,
      "Result!B8": 40.0,
      "Result!B9": 79.8
    },
    "id": "r17-b3-fmv-p5",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        66.96,
        66.88,
        23.33,
        272.8,
        225.72,
        100.98,
        46.44,
        35.53,
        131.22,
        48.4
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 131.22,
      "Result!B11": 48.4,
      "Result!B2": 66.96,
      "Result!B3": 66.88,
      "Result!B4": 23.33,
      "Result!B5": 272.8,
      "Result!B6": 225.72,
      "Result!B7": 100.98,
      "Result!B8": 46.44,
      "Result!B9": 35.53
    },
    "id": "r17-b3-fmv-p6",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "row_values": [
        54.0,
        81.51,
        81.65,
        158.4,
        200.07,
        41.58,
        10.8,
        108.68,
        26.24,
        246.4
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 26.24,
      "Result!B11": 246.4,
      "Result!B2": 54.0,
      "Result!B3": 81.51,
      "Result!B4": 81.65,
      "Result!B5": 158.4,
      "Result!B6": 200.07,
      "Result!B7": 41.58,
      "Result!B8": 10.8,
      "Result!B9": 108.68
    },
    "id": "r17-b3-fmv-p7",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "row_values": [
        42.12,
        35.53,
        46.66,
        132.0,
        87.21,
        362.34,
        34.56,
        100.32,
        90.4,
        220.0
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 90.4,
      "Result!B11": 220.0,
      "Result!B2": 42.12,
      "Result!B3": 35.53,
      "Result!B4": 46.66,
      "Result!B5": 132.0,
      "Result!B6": 87.21,
      "Result!B7": 362.34,
      "Result!B8": 34.56,
      "Result!B9": 100.32
    },
    "id": "r17-b3-fmv-p8",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 149,
      "checksum": 305,
      "row_count": 7,
      "sentinel": "KEEP-r17-b3-ioc-p0"
    },
    "golden_answer_cells": {
      "Result!B2": 305,
      "Result!B3": "KEEP-r17-b3-ioc-p0"
    },
    "id": "r17-b3-ioc-p0",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "active_sum": 265,
      "checksum": 330,
      "row_count": 7,
      "sentinel": "KEEP-r17-b3-ioc-p1"
    },
    "golden_answer_cells": {
      "Result!B2": 330,
      "Result!B3": "KEEP-r17-b3-ioc-p1"
    },
    "id": "r17-b3-ioc-p1",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "active_sum": 247,
      "checksum": 386,
      "row_count": 7,
      "sentinel": "KEEP-r17-b3-ioc-p2"
    },
    "golden_answer_cells": {
      "Result!B2": 386,
      "Result!B3": "KEEP-r17-b3-ioc-p2"
    },
    "id": "r17-b3-ioc-p2",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 294,
      "checksum": 438,
      "row_count": 9,
      "sentinel": "KEEP-r17-b3-ioc-p3"
    },
    "golden_answer_cells": {
      "Result!B2": 438,
      "Result!B3": "KEEP-r17-b3-ioc-p3",
      "Result!B4": 294
    },
    "id": "r17-b3-ioc-p3",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "active_sum": 268,
      "checksum": 496,
      "row_count": 9,
      "sentinel": "KEEP-r17-b3-ioc-p4"
    },
    "golden_answer_cells": {
      "Result!B2": 496,
      "Result!B3": "KEEP-r17-b3-ioc-p4",
      "Result!B4": 268
    },
    "id": "r17-b3-ioc-p4",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "active_sum": 286,
      "checksum": 441,
      "row_count": 9,
      "sentinel": "KEEP-r17-b3-ioc-p5"
    },
    "golden_answer_cells": {
      "Result!B2": 441,
      "Result!B3": "KEEP-r17-b3-ioc-p5",
      "Result!B4": 286
    },
    "id": "r17-b3-ioc-p5",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 421,
      "checksum": 529,
      "row_count": 11,
      "sentinel": "KEEP-r17-b3-ioc-p6"
    },
    "golden_answer_cells": {
      "Result!B2": 529,
      "Result!B3": "KEEP-r17-b3-ioc-p6",
      "Result!B4": 421,
      "Result!B5": 11
    },
    "id": "r17-b3-ioc-p6",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "active_sum": 483,
      "checksum": 594,
      "row_count": 11,
      "sentinel": "KEEP-r17-b3-ioc-p7"
    },
    "golden_answer_cells": {
      "Result!B2": 594,
      "Result!B3": "KEEP-r17-b3-ioc-p7",
      "Result!B4": 483,
      "Result!B5": 11
    },
    "id": "r17-b3-ioc-p7",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "active_sum": 401,
      "checksum": 538,
      "row_count": 11,
      "sentinel": "KEEP-r17-b3-ioc-p8"
    },
    "golden_answer_cells": {
      "Result!B2": 538,
      "Result!B3": "KEEP-r17-b3-ioc-p8",
      "Result!B4": 401,
      "Result!B5": 11
    },
    "id": "r17-b3-ioc-p8",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": [
        [
          2,
          85.0
        ],
        [
          3,
          75.0
        ],
        [
          4,
          108.0
        ],
        [
          5,
          160.0
        ],
        [
          7,
          113.0
        ],
        [
          1,
          167.0
        ],
        [
          2,
          130.0
        ],
        [
          3,
          76.0
        ],
        [
          5,
          76.0
        ],
        [
          6,
          51.0
        ],
        [
          7,
          137.0
        ],
        [
          1,
          51.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1229.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b3-msp-p0",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "kept": [
        [
          2,
          179.0
        ],
        [
          3,
          85.0
        ],
        [
          4,
          172.0
        ],
        [
          5,
          157.0
        ],
        [
          7,
          86.0
        ],
        [
          1,
          91.0
        ],
        [
          2,
          166.0
        ],
        [
          3,
          68.0
        ],
        [
          5,
          121.0
        ],
        [
          6,
          158.0
        ],
        [
          7,
          215.0
        ],
        [
          1,
          65.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1563.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b3-msp-p1",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "kept": [
        [
          2,
          220.0
        ],
        [
          3,
          123.0
        ],
        [
          4,
          111.0
        ],
        [
          5,
          227.0
        ],
        [
          7,
          147.0
        ],
        [
          1,
          195.0
        ],
        [
          2,
          204.0
        ],
        [
          3,
          219.0
        ],
        [
          5,
          182.0
        ],
        [
          6,
          125.0
        ],
        [
          7,
          224.0
        ],
        [
          1,
          82.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 2059.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b3-msp-p2",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": [
        [
          2,
          239.0
        ],
        [
          4,
          61.0
        ],
        [
          1,
          110.0
        ],
        [
          3,
          203.0
        ],
        [
          5,
          41.0
        ],
        [
          7,
          216.0
        ],
        [
          4,
          42.0
        ],
        [
          6,
          180.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1092.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b3-msp-p3",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "kept": [
        [
          2,
          96.0
        ],
        [
          4,
          174.0
        ],
        [
          1,
          143.0
        ],
        [
          3,
          130.0
        ],
        [
          5,
          49.0
        ],
        [
          7,
          120.0
        ],
        [
          4,
          90.0
        ],
        [
          6,
          52.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 854.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b3-msp-p4",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "kept": [
        [
          2,
          77.0
        ],
        [
          4,
          121.0
        ],
        [
          1,
          144.0
        ],
        [
          3,
          36.0
        ],
        [
          5,
          170.0
        ],
        [
          7,
          112.0
        ],
        [
          4,
          37.0
        ],
        [
          6,
          190.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 887.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b3-msp-p5",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b3-msp-p6",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b3-msp-p7",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b3-msp-p8",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        101.25,
        212.42,
        156.17,
        149.04,
        205.87,
        174.2,
        122.25,
        132.44,
        24.25,
        86.4
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1364.29
    },
    "id": "r17-b3-ska-p0",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        154.5,
        23.22,
        171.69,
        131.76,
        246.33,
        195.0,
        57.75,
        81.7,
        88.27,
        54.0
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1204.22
    },
    "id": "r17-b3-ska-p1",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        138.75,
        147.06,
        49.47,
        154.44,
        176.12,
        42.9,
        77.25,
        43.0,
        138.71,
        243.0
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 1210.7
    },
    "id": "r17-b3-ska-p2",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        91.5,
        54.18,
        179.45,
        192.24,
        208.25,
        213.2,
        109.5,
        129.0,
        114.46,
        173.88,
        265.37,
        72.8,
        47.25
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1851.08,
      "Result!B3": 1389.62
    },
    "id": "r17-b3-ska-p3",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        126.0,
        192.64,
        189.15,
        126.36,
        188.02,
        141.7,
        47.25,
        206.4,
        124.16,
        207.36,
        127.33,
        280.8,
        42.75
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 1999.92,
      "Result!B3": 1518.99
    },
    "id": "r17-b3-ska-p4",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        168.0,
        184.04,
        41.71,
        97.2,
        42.84,
        143.0,
        178.5,
        122.98,
        67.9,
        270.0,
        27.37,
        232.7,
        19.5
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1595.74,
      "Result!B3": 1297.5
    },
    "id": "r17-b3-ska-p5",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        135.0,
        123.84,
        234.74,
        165.24,
        61.88,
        105.3,
        153.0,
        43.0,
        57.23,
        39.96,
        243.95,
        39.0,
        56.25,
        138.46,
        145.5,
        63.72
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 1806.07,
      "Result!B3": 1495.71,
      "Result!B4": 243.95
    },
    "id": "r17-b3-ska-p6",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        84.75,
        35.26,
        224.07,
        102.6,
        96.39,
        250.9,
        138.75,
        60.2,
        37.83,
        127.44,
        24.99,
        270.4,
        156.0,
        203.82,
        32.01,
        118.8
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1964.21,
      "Result!B3": 1589.24,
      "Result!B4": 270.4
    },
    "id": "r17-b3-ska-p7",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        84.75,
        193.5,
        82.45,
        122.04,
        84.49,
        150.8,
        102.0,
        29.24,
        156.17,
        27.0,
        262.99,
        35.1,
        123.0,
        151.36,
        183.33,
        133.92
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1922.14,
      "Result!B3": 1473.73,
      "Result!B4": 262.99
    },
    "id": "r17-b3-ska-p8",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        144,
        64,
        57,
        117,
        60,
        63
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 505,
      "Result!B3": 144
    },
    "id": "r17-b3-tsr-p0",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "target_sheet": "Quarter_2_FINAL",
      "target_values": [
        79,
        43,
        104,
        64,
        40,
        35
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 365,
      "Result!B3": 104
    },
    "id": "r17-b3-tsr-p1",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "target_sheet": "Quarter_3_FINAL",
      "target_values": [
        51,
        44,
        133,
        126,
        69,
        47
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 470,
      "Result!B3": 133
    },
    "id": "r17-b3-tsr-p2",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_4_FINAL",
      "target_values": [
        97,
        128,
        51,
        129,
        32,
        127,
        149,
        172
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 885,
      "Result!B3": 172,
      "Result!B4": 110.62
    },
    "id": "r17-b3-tsr-p3",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        41,
        92,
        151,
        93,
        76,
        148,
        70,
        91
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 762,
      "Result!B3": 151,
      "Result!B4": 95.25
    },
    "id": "r17-b3-tsr-p4",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "target_sheet": "Quarter_2_FINAL",
      "target_values": [
        108,
        28,
        111,
        20,
        131,
        38,
        127,
        83
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 646,
      "Result!B3": 131,
      "Result!B4": 80.75
    },
    "id": "r17-b3-tsr-p5",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 3,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_3_FINAL",
      "target_values": [
        143,
        146,
        39,
        109,
        67,
        166,
        38,
        95,
        114,
        132
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1049,
      "Result!B3": 166,
      "Result!B4": 104.9,
      "Result!B5": 6
    },
    "id": "r17-b3-tsr-p6",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 3,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "target_sheet": "Quarter_4_FINAL",
      "target_values": [
        35,
        157,
        136,
        132,
        150,
        117,
        58,
        36,
        120,
        78
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1019,
      "Result!B3": 157,
      "Result!B4": 101.9,
      "Result!B5": 6
    },
    "id": "r17-b3-tsr-p7",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 3,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        95,
        50,
        22,
        34,
        59,
        20,
        146,
        69,
        119,
        97
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 711,
      "Result!B3": 146,
      "Result!B4": 71.1,
      "Result!B5": 2
    },
    "id": "r17-b3-tsr-p8",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_update_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        23.0,
        57.0,
        130.0,
        76.0,
        252.0,
        19.0,
        162.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 719.0,
      "Result!B3": 7
    },
    "id": "r17-b4-agj-p0",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        74.0,
        198.0,
        310.0,
        62.0,
        300.0,
        55.0,
        96.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1095.0,
      "Result!B3": 7
    },
    "id": "r17-b4-agj-p1",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        37.0,
        57.0,
        85.0,
        122.0,
        252.0,
        59.0,
        186.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 798.0,
      "Result!B3": 7
    },
    "id": "r17-b4-agj-p2",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        35.0,
        145.0,
        82.0,
        60.0,
        99.0,
        132.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 553.0,
      "Result!B3": 6
    },
    "id": "r17-b4-agj-p3",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        33.0,
        155.0,
        100.0,
        54.0,
        42.0,
        50.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 434.0,
      "Result!B3": 6
    },
    "id": "r17-b4-agj-p4",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        36.0,
        130.0,
        68.0,
        47.0,
        45.0,
        68.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 394.0,
      "Result!B3": 6
    },
    "id": "r17-b4-agj-p5",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        69.0,
        355.0,
        70.0,
        44.0,
        42.0,
        20.0,
        104.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 704.0,
      "Result!B3": 7,
      "Result!B4": 100.57
    },
    "id": "r17-b4-agj-p6",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        21.0,
        315.0,
        146.0,
        39.0,
        75.0,
        128.0,
        104.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 828.0,
      "Result!B3": 7,
      "Result!B4": 118.29
    },
    "id": "r17-b4-agj-p7",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        28.0,
        315.0,
        144.0,
        12.0,
        96.0,
        64.0,
        208.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 867.0,
      "Result!B3": 7,
      "Result!B4": 123.86
    },
    "id": "r17-b4-agj-p8",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        54,
        110,
        174,
        224,
        190,
        294
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 54,
      "Result!B3": 110,
      "Result!B4": 174,
      "Result!B5": 224,
      "Result!B6": 190,
      "Result!B7": 294
    },
    "id": "r17-b4-fmv-p0",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "row_values": [
        57,
        86,
        78,
        188,
        100,
        114
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 57,
      "Result!B3": 86,
      "Result!B4": 78,
      "Result!B5": 188,
      "Result!B6": 100,
      "Result!B7": 114
    },
    "id": "r17-b4-fmv-p1",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "row_values": [
        12,
        26,
        54,
        120,
        235,
        78
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 12,
      "Result!B3": 26,
      "Result!B4": 54,
      "Result!B5": 120,
      "Result!B6": 235,
      "Result!B7": 78
    },
    "id": "r17-b4-fmv-p2",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        29.0,
        15.2,
        118.8,
        80.0,
        104.5,
        162.0,
        53.0,
        108.3
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 29.0,
      "Result!B3": 15.2,
      "Result!B4": 118.8,
      "Result!B5": 80.0,
      "Result!B6": 104.5,
      "Result!B7": 162.0,
      "Result!B8": 53.0,
      "Result!B9": 108.3
    },
    "id": "r17-b4-fmv-p3",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "row_values": [
        21.0,
        108.3,
        78.3,
        148.0,
        242.25,
        167.4,
        59.0,
        85.5
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 21.0,
      "Result!B3": 108.3,
      "Result!B4": 78.3,
      "Result!B5": 148.0,
      "Result!B6": 242.25,
      "Result!B7": 167.4,
      "Result!B8": 59.0,
      "Result!B9": 85.5
    },
    "id": "r17-b4-fmv-p4",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "row_values": [
        31.0,
        104.5,
        167.4,
        80.0,
        161.5,
        118.8,
        12.0,
        81.7
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 31.0,
      "Result!B3": 104.5,
      "Result!B4": 167.4,
      "Result!B5": 80.0,
      "Result!B6": 161.5,
      "Result!B7": 118.8,
      "Result!B8": 12.0,
      "Result!B9": 81.7
    },
    "id": "r17-b4-fmv-p5",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        27.0,
        52.25,
        84.56,
        198.0,
        323.19,
        148.5,
        63.72,
        123.31,
        186.62,
        39.6
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 186.62,
      "Result!B11": 39.6,
      "Result!B2": 27.0,
      "Result!B3": 52.25,
      "Result!B4": 84.56,
      "Result!B5": 198.0,
      "Result!B6": 323.19,
      "Result!B7": 148.5,
      "Result!B8": 63.72,
      "Result!B9": 123.31
    },
    "id": "r17-b4-fmv-p6",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "row_values": [
        9.72,
        35.53,
        139.97,
        224.4,
        277.02,
        243.54,
        23.76,
        108.68,
        75.82,
        74.8
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 75.82,
      "Result!B11": 74.8,
      "Result!B2": 9.72,
      "Result!B3": 35.53,
      "Result!B4": 139.97,
      "Result!B5": 224.4,
      "Result!B6": 277.02,
      "Result!B7": 243.54,
      "Result!B8": 23.76,
      "Result!B9": 108.68
    },
    "id": "r17-b4-fmv-p7",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "row_values": [
        39.96,
        119.13,
        139.97,
        237.6,
        61.56,
        243.54,
        19.44,
        131.67,
        40.82,
        281.6
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 40.82,
      "Result!B11": 281.6,
      "Result!B2": 39.96,
      "Result!B3": 119.13,
      "Result!B4": 139.97,
      "Result!B5": 237.6,
      "Result!B6": 61.56,
      "Result!B7": 243.54,
      "Result!B8": 19.44,
      "Result!B9": 131.67
    },
    "id": "r17-b4-fmv-p8",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 206,
      "checksum": 285,
      "row_count": 7,
      "sentinel": "KEEP-r17-b4-ioc-p0"
    },
    "golden_answer_cells": {
      "Result!B2": 285,
      "Result!B3": "KEEP-r17-b4-ioc-p0"
    },
    "id": "r17-b4-ioc-p0",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "active_sum": 215,
      "checksum": 276,
      "row_count": 7,
      "sentinel": "KEEP-r17-b4-ioc-p1"
    },
    "golden_answer_cells": {
      "Result!B2": 276,
      "Result!B3": "KEEP-r17-b4-ioc-p1"
    },
    "id": "r17-b4-ioc-p1",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "active_sum": 222,
      "checksum": 340,
      "row_count": 7,
      "sentinel": "KEEP-r17-b4-ioc-p2"
    },
    "golden_answer_cells": {
      "Result!B2": 340,
      "Result!B3": "KEEP-r17-b4-ioc-p2"
    },
    "id": "r17-b4-ioc-p2",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 260,
      "checksum": 431,
      "row_count": 9,
      "sentinel": "KEEP-r17-b4-ioc-p3"
    },
    "golden_answer_cells": {
      "Result!B2": 431,
      "Result!B3": "KEEP-r17-b4-ioc-p3",
      "Result!B4": 260
    },
    "id": "r17-b4-ioc-p3",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "active_sum": 181,
      "checksum": 350,
      "row_count": 9,
      "sentinel": "KEEP-r17-b4-ioc-p4"
    },
    "golden_answer_cells": {
      "Result!B2": 350,
      "Result!B3": "KEEP-r17-b4-ioc-p4",
      "Result!B4": 181
    },
    "id": "r17-b4-ioc-p4",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "active_sum": 245,
      "checksum": 421,
      "row_count": 9,
      "sentinel": "KEEP-r17-b4-ioc-p5"
    },
    "golden_answer_cells": {
      "Result!B2": 421,
      "Result!B3": "KEEP-r17-b4-ioc-p5",
      "Result!B4": 245
    },
    "id": "r17-b4-ioc-p5",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 445,
      "checksum": 527,
      "row_count": 11,
      "sentinel": "KEEP-r17-b4-ioc-p6"
    },
    "golden_answer_cells": {
      "Result!B2": 527,
      "Result!B3": "KEEP-r17-b4-ioc-p6",
      "Result!B4": 445,
      "Result!B5": 11
    },
    "id": "r17-b4-ioc-p6",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "active_sum": 407,
      "checksum": 567,
      "row_count": 11,
      "sentinel": "KEEP-r17-b4-ioc-p7"
    },
    "golden_answer_cells": {
      "Result!B2": 567,
      "Result!B3": "KEEP-r17-b4-ioc-p7",
      "Result!B4": 407,
      "Result!B5": 11
    },
    "id": "r17-b4-ioc-p7",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "active_sum": 276,
      "checksum": 368,
      "row_count": 11,
      "sentinel": "KEEP-r17-b4-ioc-p8"
    },
    "golden_answer_cells": {
      "Result!B2": 368,
      "Result!B3": "KEEP-r17-b4-ioc-p8",
      "Result!B4": 276,
      "Result!B5": 11
    },
    "id": "r17-b4-ioc-p8",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": [
        [
          2,
          109.0
        ],
        [
          3,
          175.0
        ],
        [
          4,
          144.0
        ],
        [
          5,
          220.0
        ],
        [
          7,
          31.0
        ],
        [
          1,
          178.0
        ],
        [
          2,
          48.0
        ],
        [
          3,
          173.0
        ],
        [
          5,
          72.0
        ],
        [
          6,
          98.0
        ],
        [
          7,
          207.0
        ],
        [
          1,
          49.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1504.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b4-msp-p0",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "kept": [
        [
          2,
          114.0
        ],
        [
          3,
          71.0
        ],
        [
          4,
          178.0
        ],
        [
          5,
          148.0
        ],
        [
          7,
          188.0
        ],
        [
          1,
          203.0
        ],
        [
          2,
          90.0
        ],
        [
          3,
          175.0
        ],
        [
          5,
          216.0
        ],
        [
          6,
          56.0
        ],
        [
          7,
          70.0
        ],
        [
          1,
          232.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1741.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b4-msp-p1",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "kept": [
        [
          2,
          38.0
        ],
        [
          3,
          202.0
        ],
        [
          4,
          50.0
        ],
        [
          5,
          98.0
        ],
        [
          7,
          51.0
        ],
        [
          1,
          83.0
        ],
        [
          2,
          233.0
        ],
        [
          3,
          216.0
        ],
        [
          5,
          214.0
        ],
        [
          6,
          90.0
        ],
        [
          7,
          81.0
        ],
        [
          1,
          166.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1522.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b4-msp-p2",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": [
        [
          2,
          191.0
        ],
        [
          4,
          114.0
        ],
        [
          1,
          136.0
        ],
        [
          3,
          96.0
        ],
        [
          5,
          238.0
        ],
        [
          7,
          240.0
        ],
        [
          4,
          72.0
        ],
        [
          6,
          217.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1304.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b4-msp-p3",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "kept": [
        [
          2,
          170.0
        ],
        [
          4,
          192.0
        ],
        [
          1,
          137.0
        ],
        [
          3,
          164.0
        ],
        [
          5,
          200.0
        ],
        [
          7,
          156.0
        ],
        [
          4,
          55.0
        ],
        [
          6,
          131.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1205.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b4-msp-p4",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "kept": [
        [
          2,
          102.0
        ],
        [
          4,
          162.0
        ],
        [
          1,
          161.0
        ],
        [
          3,
          141.0
        ],
        [
          5,
          185.0
        ],
        [
          7,
          236.0
        ],
        [
          4,
          166.0
        ],
        [
          6,
          47.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1200.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b4-msp-p5",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b4-msp-p6",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b4-msp-p7",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b4-msp-p8",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        145.5,
        62.78,
        20.37,
        260.28,
        190.4,
        157.3,
        144.75,
        81.7,
        79.54,
        172.8
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1315.42
    },
    "id": "r17-b4-ska-p0",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        146.25,
        109.22,
        64.02,
        73.44,
        79.73,
        72.8,
        141.0,
        156.52,
        164.9,
        110.16
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1118.04
    },
    "id": "r17-b4-ska-p1",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        154.5,
        44.72,
        132.89,
        129.6,
        26.18,
        317.2,
        40.5,
        137.6,
        185.27,
        204.12
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 1372.58
    },
    "id": "r17-b4-ska-p2",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        24.0,
        38.7,
        241.53,
        81.0,
        161.84,
        96.2,
        118.5,
        61.92,
        82.45,
        173.88,
        29.75,
        312.0,
        108.0
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1529.77,
      "Result!B3": 1153.48
    },
    "id": "r17-b4-ska-p3",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        186.75,
        34.4,
        55.29,
        31.32,
        183.26,
        104.0,
        160.5,
        121.26,
        81.48,
        183.6,
        296.31,
        165.1,
        120.0
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 1723.27,
      "Result!B3": 1151.78
    },
    "id": "r17-b4-ska-p4",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        173.25,
        134.16,
        211.46,
        262.44,
        123.76,
        325.0,
        85.5,
        157.38,
        189.15,
        79.92,
        247.52,
        39.0,
        48.0
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 2076.54,
      "Result!B3": 1542.38
    },
    "id": "r17-b4-ska-p5",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        24.0,
        213.28,
        115.43,
        124.2,
        107.1,
        306.8,
        138.75,
        113.52,
        71.78,
        91.8,
        105.91,
        169.0,
        135.0,
        79.12,
        102.82,
        208.44
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 2106.95,
      "Result!B3": 1769.07,
      "Result!B4": 306.8
    },
    "id": "r17-b4-ska-p6",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        101.25,
        154.8,
        134.83,
        224.64,
        158.27,
        167.7,
        153.0,
        98.9,
        70.81,
        193.32,
        73.78,
        153.4,
        118.5,
        85.14,
        176.54,
        171.72
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 2236.6,
      "Result!B3": 1787.77,
      "Result!B4": 224.64
    },
    "id": "r17-b4-ska-p7",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        27.0,
        136.74,
        241.53,
        96.12,
        290.36,
        70.2,
        139.5,
        97.18,
        132.89,
        32.4,
        29.75,
        45.5,
        180.0,
        36.12,
        174.6,
        192.24
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1922.13,
      "Result!B3": 1291.88,
      "Result!B4": 290.36
    },
    "id": "r17-b4-ska-p8",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        81,
        157,
        111,
        127,
        100,
        98
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 674,
      "Result!B3": 157
    },
    "id": "r17-b4-tsr-p0",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "target_sheet": "Quarter_2_FINAL",
      "target_values": [
        53,
        43,
        154,
        165,
        20,
        167
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 602,
      "Result!B3": 167
    },
    "id": "r17-b4-tsr-p1",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "target_sheet": "Quarter_3_FINAL",
      "target_values": [
        48,
        24,
        43,
        159,
        37,
        61
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 372,
      "Result!B3": 159
    },
    "id": "r17-b4-tsr-p2",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_4_FINAL",
      "target_values": [
        108,
        148,
        43,
        94,
        35,
        142,
        119,
        90
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 779,
      "Result!B3": 148,
      "Result!B4": 97.38
    },
    "id": "r17-b4-tsr-p3",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        92,
        171,
        150,
        58,
        85,
        31,
        71,
        155
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 813,
      "Result!B3": 171,
      "Result!B4": 101.62
    },
    "id": "r17-b4-tsr-p4",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "target_sheet": "Quarter_2_FINAL",
      "target_values": [
        121,
        89,
        149,
        155,
        74,
        36,
        79,
        148
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 851,
      "Result!B3": 155,
      "Result!B4": 106.38
    },
    "id": "r17-b4-tsr-p5",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 4,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_3_FINAL",
      "target_values": [
        57,
        36,
        87,
        99,
        95,
        179,
        38,
        133,
        133,
        82
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 939,
      "Result!B3": 179,
      "Result!B4": 93.9,
      "Result!B5": 3
    },
    "id": "r17-b4-tsr-p6",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 4,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "target_sheet": "Quarter_4_FINAL",
      "target_values": [
        127,
        57,
        90,
        143,
        40,
        83,
        42,
        29,
        42,
        151
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 804,
      "Result!B3": 151,
      "Result!B4": 80.4,
      "Result!B5": 3
    },
    "id": "r17-b4-tsr-p7",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 4,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        168,
        113,
        73,
        67,
        125,
        172,
        66,
        118,
        82,
        38
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1022,
      "Result!B3": 172,
      "Result!B4": 102.2,
      "Result!B5": 5
    },
    "id": "r17-b4-tsr-p8",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e1_heldout_probe_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        42.0,
        201.0,
        120.0,
        106.0,
        248.0,
        13.0,
        42.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 772.0,
      "Result!B3": 7
    },
    "id": "r17-b5-agj-p0",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        30.0,
        60.0,
        265.0,
        38.0,
        144.0,
        53.0,
        99.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 689.0,
      "Result!B3": 7
    },
    "id": "r17-b5-agj-p1",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        15.0,
        201.0,
        305.0,
        52.0,
        112.0,
        21.0,
        36.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 742.0,
      "Result!B3": 7
    },
    "id": "r17-b5-agj-p2",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        16.0,
        190.0,
        152.0,
        12.0,
        81.0,
        142.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 593.0,
      "Result!B3": 6
    },
    "id": "r17-b5-agj-p3",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        14.0,
        180.0,
        84.0,
        18.0,
        231.0,
        16.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 543.0,
      "Result!B3": 6
    },
    "id": "r17-b5-agj-p4",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        38.0,
        285.0,
        62.0,
        31.0,
        123.0,
        48.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 587.0,
      "Result!B3": 6
    },
    "id": "r17-b5-agj-p5",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        50.0,
        190.0,
        136.0,
        70.0,
        81.0,
        124.0,
        260.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 911.0,
      "Result!B3": 7,
      "Result!B4": 130.14
    },
    "id": "r17-b5-agj-p6",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        37.0,
        120.0,
        42.0,
        58.0,
        105.0,
        26.0,
        264.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 652.0,
      "Result!B3": 7,
      "Result!B4": 93.14
    },
    "id": "r17-b5-agj-p7",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        78.0,
        190.0,
        108.0,
        75.0,
        51.0,
        48.0,
        220.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 770.0,
      "Result!B3": 7,
      "Result!B4": 110.0
    },
    "id": "r17-b5-agj-p8",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        29,
        34,
        75,
        96,
        65,
        300
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 29,
      "Result!B3": 34,
      "Result!B4": 75,
      "Result!B5": 96,
      "Result!B6": 65,
      "Result!B7": 300
    },
    "id": "r17-b5-fmv-p0",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "row_values": [
        37,
        14,
        96,
        52,
        290,
        114
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 37,
      "Result!B3": 14,
      "Result!B4": 96,
      "Result!B5": 52,
      "Result!B6": 290,
      "Result!B7": 114
    },
    "id": "r17-b5-fmv-p1",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "row_values": [
        15,
        20,
        93,
        40,
        300,
        228
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 15,
      "Result!B3": 20,
      "Result!B4": 93,
      "Result!B5": 40,
      "Result!B6": 300,
      "Result!B7": 228
    },
    "id": "r17-b5-fmv-p2",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        17.0,
        28.5,
        118.8,
        192.0,
        137.75,
        70.2,
        48.0,
        95.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 17.0,
      "Result!B3": 28.5,
      "Result!B4": 118.8,
      "Result!B5": 192.0,
      "Result!B6": 137.75,
      "Result!B7": 70.2,
      "Result!B8": 48.0,
      "Result!B9": 95.0
    },
    "id": "r17-b5-fmv-p3",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "row_values": [
        7.0,
        100.7,
        116.1,
        124.0,
        99.75,
        307.8,
        65.0,
        114.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 7.0,
      "Result!B3": 100.7,
      "Result!B4": 116.1,
      "Result!B5": 124.0,
      "Result!B6": 99.75,
      "Result!B7": 307.8,
      "Result!B8": 65.0,
      "Result!B9": 114.0
    },
    "id": "r17-b5-fmv-p4",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "row_values": [
        22.0,
        104.5,
        140.4,
        232.0,
        109.25,
        178.2,
        22.0,
        30.4
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 22.0,
      "Result!B3": 104.5,
      "Result!B4": 140.4,
      "Result!B5": 232.0,
      "Result!B6": 109.25,
      "Result!B7": 178.2,
      "Result!B8": 22.0,
      "Result!B9": 30.4
    },
    "id": "r17-b5-fmv-p5",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        60.48,
        83.6,
        169.13,
        202.4,
        56.43,
        374.22,
        29.16,
        83.6,
        52.49,
        118.8
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 52.49,
      "Result!B11": 118.8,
      "Result!B2": 60.48,
      "Result!B3": 83.6,
      "Result!B4": 169.13,
      "Result!B5": 202.4,
      "Result!B6": 56.43,
      "Result!B7": 374.22,
      "Result!B8": 29.16,
      "Result!B9": 83.6
    },
    "id": "r17-b5-fmv-p6",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "row_values": [
        43.2,
        129.58,
        134.14,
        264.0,
        92.34,
        178.2,
        44.28,
        35.53,
        110.81,
        198.0
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 110.81,
      "Result!B11": 198.0,
      "Result!B2": 43.2,
      "Result!B3": 129.58,
      "Result!B4": 134.14,
      "Result!B5": 264.0,
      "Result!B6": 92.34,
      "Result!B7": 178.2,
      "Result!B8": 44.28,
      "Result!B9": 35.53
    },
    "id": "r17-b5-fmv-p7",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "row_values": [
        70.2,
        58.52,
        110.81,
        70.4,
        71.82,
        386.1,
        43.2,
        45.98,
        104.98,
        259.6
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 104.98,
      "Result!B11": 259.6,
      "Result!B2": 70.2,
      "Result!B3": 58.52,
      "Result!B4": 110.81,
      "Result!B5": 70.4,
      "Result!B6": 71.82,
      "Result!B7": 386.1,
      "Result!B8": 43.2,
      "Result!B9": 45.98
    },
    "id": "r17-b5-fmv-p8",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 216,
      "checksum": 319,
      "row_count": 7,
      "sentinel": "KEEP-r17-b5-ioc-p0"
    },
    "golden_answer_cells": {
      "Result!B2": 319,
      "Result!B3": "KEEP-r17-b5-ioc-p0"
    },
    "id": "r17-b5-ioc-p0",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "active_sum": 226,
      "checksum": 328,
      "row_count": 7,
      "sentinel": "KEEP-r17-b5-ioc-p1"
    },
    "golden_answer_cells": {
      "Result!B2": 328,
      "Result!B3": "KEEP-r17-b5-ioc-p1"
    },
    "id": "r17-b5-ioc-p1",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "active_sum": 222,
      "checksum": 341,
      "row_count": 7,
      "sentinel": "KEEP-r17-b5-ioc-p2"
    },
    "golden_answer_cells": {
      "Result!B2": 341,
      "Result!B3": "KEEP-r17-b5-ioc-p2"
    },
    "id": "r17-b5-ioc-p2",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 315,
      "checksum": 498,
      "row_count": 9,
      "sentinel": "KEEP-r17-b5-ioc-p3"
    },
    "golden_answer_cells": {
      "Result!B2": 498,
      "Result!B3": "KEEP-r17-b5-ioc-p3",
      "Result!B4": 315
    },
    "id": "r17-b5-ioc-p3",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "active_sum": 228,
      "checksum": 307,
      "row_count": 9,
      "sentinel": "KEEP-r17-b5-ioc-p4"
    },
    "golden_answer_cells": {
      "Result!B2": 307,
      "Result!B3": "KEEP-r17-b5-ioc-p4",
      "Result!B4": 228
    },
    "id": "r17-b5-ioc-p4",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "active_sum": 373,
      "checksum": 490,
      "row_count": 9,
      "sentinel": "KEEP-r17-b5-ioc-p5"
    },
    "golden_answer_cells": {
      "Result!B2": 490,
      "Result!B3": "KEEP-r17-b5-ioc-p5",
      "Result!B4": 373
    },
    "id": "r17-b5-ioc-p5",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 391,
      "checksum": 611,
      "row_count": 11,
      "sentinel": "KEEP-r17-b5-ioc-p6"
    },
    "golden_answer_cells": {
      "Result!B2": 611,
      "Result!B3": "KEEP-r17-b5-ioc-p6",
      "Result!B4": 391,
      "Result!B5": 11
    },
    "id": "r17-b5-ioc-p6",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "active_sum": 414,
      "checksum": 537,
      "row_count": 11,
      "sentinel": "KEEP-r17-b5-ioc-p7"
    },
    "golden_answer_cells": {
      "Result!B2": 537,
      "Result!B3": "KEEP-r17-b5-ioc-p7",
      "Result!B4": 414,
      "Result!B5": 11
    },
    "id": "r17-b5-ioc-p7",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "active_sum": 364,
      "checksum": 523,
      "row_count": 11,
      "sentinel": "KEEP-r17-b5-ioc-p8"
    },
    "golden_answer_cells": {
      "Result!B2": 523,
      "Result!B3": "KEEP-r17-b5-ioc-p8",
      "Result!B4": 364,
      "Result!B5": 11
    },
    "id": "r17-b5-ioc-p8",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": [
        [
          2,
          208.0
        ],
        [
          3,
          186.0
        ],
        [
          4,
          225.0
        ],
        [
          5,
          95.0
        ],
        [
          7,
          240.0
        ],
        [
          1,
          84.0
        ],
        [
          2,
          46.0
        ],
        [
          3,
          214.0
        ],
        [
          5,
          63.0
        ],
        [
          6,
          68.0
        ],
        [
          7,
          72.0
        ],
        [
          1,
          171.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1672.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b5-msp-p0",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "kept": [
        [
          2,
          42.0
        ],
        [
          3,
          58.0
        ],
        [
          4,
          216.0
        ],
        [
          5,
          108.0
        ],
        [
          7,
          221.0
        ],
        [
          1,
          64.0
        ],
        [
          2,
          137.0
        ],
        [
          3,
          223.0
        ],
        [
          5,
          36.0
        ],
        [
          6,
          63.0
        ],
        [
          7,
          200.0
        ],
        [
          1,
          35.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1403.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b5-msp-p1",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "kept": [
        [
          2,
          212.0
        ],
        [
          3,
          74.0
        ],
        [
          4,
          225.0
        ],
        [
          5,
          134.0
        ],
        [
          7,
          167.0
        ],
        [
          1,
          174.0
        ],
        [
          2,
          110.0
        ],
        [
          3,
          140.0
        ],
        [
          5,
          206.0
        ],
        [
          6,
          183.0
        ],
        [
          7,
          77.0
        ],
        [
          1,
          217.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1919.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b5-msp-p2",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": [
        [
          2,
          152.0
        ],
        [
          4,
          178.0
        ],
        [
          1,
          129.0
        ],
        [
          3,
          208.0
        ],
        [
          5,
          50.0
        ],
        [
          7,
          186.0
        ],
        [
          4,
          203.0
        ],
        [
          6,
          100.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1206.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b5-msp-p3",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "kept": [
        [
          2,
          205.0
        ],
        [
          4,
          221.0
        ],
        [
          1,
          175.0
        ],
        [
          3,
          175.0
        ],
        [
          5,
          51.0
        ],
        [
          7,
          114.0
        ],
        [
          4,
          33.0
        ],
        [
          6,
          165.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1139.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b5-msp-p4",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "kept": [
        [
          2,
          89.0
        ],
        [
          4,
          149.0
        ],
        [
          1,
          229.0
        ],
        [
          3,
          214.0
        ],
        [
          5,
          91.0
        ],
        [
          7,
          197.0
        ],
        [
          4,
          73.0
        ],
        [
          6,
          100.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1142.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b5-msp-p5",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b5-msp-p6",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b5-msp-p7",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b5-msp-p8",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        28.5,
        148.78,
        32.01,
        85.32,
        223.72,
        140.4,
        179.25,
        138.46,
        122.22,
        204.12
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1302.78
    },
    "id": "r17-b5-ska-p0",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        80.25,
        71.38,
        39.77,
        244.08,
        249.9,
        306.8,
        126.75,
        211.56,
        50.44,
        259.2
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1640.13
    },
    "id": "r17-b5-ska-p1",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        152.25,
        119.54,
        123.19,
        52.92,
        149.94,
        241.8,
        184.5,
        168.56,
        117.37,
        183.6
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 1493.67
    },
    "id": "r17-b5-ska-p2",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        60.75,
        211.56,
        231.83,
        61.56,
        41.65,
        72.8,
        17.25,
        182.32,
        95.06,
        120.96,
        94.01,
        269.1,
        151.5
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1610.35,
      "Result!B3": 1261.39
    },
    "id": "r17-b5-ska-p3",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        173.25,
        25.8,
        163.93,
        151.2,
        153.51,
        323.7,
        136.5,
        208.98,
        171.69,
        159.84,
        127.33,
        141.7,
        98.25
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 2035.68,
      "Result!B3": 1438.98
    },
    "id": "r17-b5-ska-p4",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        45.75,
        121.26,
        75.66,
        70.2,
        63.07,
        26.0,
        18.0,
        168.56,
        131.92,
        252.72,
        278.46,
        78.0,
        78.75
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1408.35,
      "Result!B3": 1088.86
    },
    "id": "r17-b5-ska-p5",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        177.0,
        54.18,
        219.22,
        83.16,
        30.94,
        243.1,
        63.75,
        112.66,
        118.34,
        264.6,
        176.12,
        37.7,
        97.5,
        190.92,
        175.57,
        174.96
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 2219.72,
      "Result!B3": 1795.94,
      "Result!B4": 264.6
    },
    "id": "r17-b5-ska-p6",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        70.5,
        196.94,
        127.07,
        257.04,
        69.02,
        215.8,
        63.75,
        93.74,
        31.04,
        198.72,
        242.76,
        280.8,
        70.5,
        27.52,
        225.04,
        77.76
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 2248.0,
      "Result!B3": 2006.94,
      "Result!B4": 280.8
    },
    "id": "r17-b5-ska-p7",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        78.75,
        69.66,
        155.2,
        82.08,
        241.57,
        63.7,
        65.25,
        185.76,
        94.09,
        135.0,
        207.06,
        250.9,
        99.75,
        124.7,
        95.06,
        119.88
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 2068.41,
      "Result!B3": 1554.25,
      "Result!B4": 250.9
    },
    "id": "r17-b5-ska-p8",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        26,
        31,
        79,
        22,
        92,
        168
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 418,
      "Result!B3": 168
    },
    "id": "r17-b5-tsr-p0",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "target_sheet": "Quarter_2_FINAL",
      "target_values": [
        80,
        116,
        178,
        75,
        123,
        94
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 666,
      "Result!B3": 178
    },
    "id": "r17-b5-tsr-p1",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "target_sheet": "Quarter_3_FINAL",
      "target_values": [
        168,
        176,
        82,
        139,
        155,
        50
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 770,
      "Result!B3": 176
    },
    "id": "r17-b5-tsr-p2",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_4_FINAL",
      "target_values": [
        137,
        173,
        108,
        111,
        50,
        178,
        143,
        116
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1016,
      "Result!B3": 178,
      "Result!B4": 127.0
    },
    "id": "r17-b5-tsr-p3",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        89,
        47,
        31,
        67,
        125,
        42,
        173,
        24
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 598,
      "Result!B3": 173,
      "Result!B4": 74.75
    },
    "id": "r17-b5-tsr-p4",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "target_sheet": "Quarter_2_FINAL",
      "target_values": [
        22,
        20,
        82,
        152,
        46,
        92,
        112,
        61
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 587,
      "Result!B3": 152,
      "Result!B4": 73.38
    },
    "id": "r17-b5-tsr-p5",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 5,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_3_FINAL",
      "target_values": [
        27,
        105,
        44,
        47,
        74,
        47,
        177,
        179,
        145,
        55
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 900,
      "Result!B3": 179,
      "Result!B4": 90.0,
      "Result!B5": 4
    },
    "id": "r17-b5-tsr-p6",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 5,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "target_sheet": "Quarter_4_FINAL",
      "target_values": [
        98,
        111,
        29,
        117,
        177,
        171,
        173,
        25,
        21,
        60
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 982,
      "Result!B3": 177,
      "Result!B4": 98.2,
      "Result!B5": 5
    },
    "id": "r17-b5-tsr-p7",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 5,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        48,
        162,
        45,
        25,
        92,
        116,
        115,
        133,
        95,
        98
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 929,
      "Result!B3": 162,
      "Result!B4": 92.9,
      "Result!B5": 4
    },
    "id": "r17-b5-tsr-p8",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        70.0,
        225.0,
        360.0,
        110.0,
        40.0,
        42.0,
        195.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1042.0,
      "Result!B3": 7
    },
    "id": "r17-b6-agj-p0",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        63.0,
        192.0,
        240.0,
        124.0,
        252.0,
        14.0,
        189.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1074.0,
      "Result!B3": 7
    },
    "id": "r17-b6-agj-p1",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        32.0,
        63.0,
        345.0,
        38.0,
        308.0,
        62.0,
        219.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1067.0,
      "Result!B3": 7
    },
    "id": "r17-b6-agj-p2",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        11.0,
        65.0,
        128.0,
        62.0,
        27.0,
        110.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 403.0,
      "Result!B3": 6
    },
    "id": "r17-b6-agj-p3",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        72.0,
        325.0,
        80.0,
        64.0,
        183.0,
        40.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 764.0,
      "Result!B3": 6
    },
    "id": "r17-b6-agj-p4",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "retained_count": 6,
      "retained_values": [
        47.0,
        205.0,
        92.0,
        31.0,
        105.0,
        64.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 544.0,
      "Result!B3": 6
    },
    "id": "r17-b6-agj-p5",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        25.0,
        195.0,
        152.0,
        76.0,
        24.0,
        132.0,
        100.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 704.0,
      "Result!B3": 7,
      "Result!B4": 100.57
    },
    "id": "r17-b6-agj-p6",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        24.0,
        350.0,
        110.0,
        60.0,
        240.0,
        124.0,
        64.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 972.0,
      "Result!B3": 7,
      "Result!B4": 138.86
    },
    "id": "r17-b6-agj-p7",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "retained_count": 7,
      "retained_values": [
        25.0,
        375.0,
        132.0,
        78.0,
        138.0,
        106.0,
        48.0
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 902.0,
      "Result!B3": 7,
      "Result!B4": 128.86
    },
    "id": "r17-b6-agj-p8",
    "primary_failure_family": "aggregation_join",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        35,
        38,
        78,
        200,
        135,
        342
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 35,
      "Result!B3": 38,
      "Result!B4": 78,
      "Result!B5": 200,
      "Result!B6": 135,
      "Result!B7": 342
    },
    "id": "r17-b6-fmv-p0",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "row_values": [
        32,
        118,
        186,
        48,
        115,
        270
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 32,
      "Result!B3": 118,
      "Result!B4": 186,
      "Result!B5": 48,
      "Result!B6": 115,
      "Result!B7": 270
    },
    "id": "r17-b6-fmv-p1",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B7",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "row_values": [
        16,
        100,
        45,
        248,
        75,
        246
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 16,
      "Result!B3": 100,
      "Result!B4": 45,
      "Result!B5": 248,
      "Result!B6": 75,
      "Result!B7": 246
    },
    "id": "r17-b6-fmv-p2",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        35.0,
        81.7,
        148.5,
        144.0,
        270.75,
        226.8,
        52.0,
        72.2
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 35.0,
      "Result!B3": 81.7,
      "Result!B4": 148.5,
      "Result!B5": 144.0,
      "Result!B6": 270.75,
      "Result!B7": 226.8,
      "Result!B8": 52.0,
      "Result!B9": 72.2
    },
    "id": "r17-b6-fmv-p3",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "row_values": [
        61.0,
        62.7,
        62.1,
        224.0,
        137.75,
        280.8,
        37.0,
        93.1
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 61.0,
      "Result!B3": 62.7,
      "Result!B4": 62.1,
      "Result!B5": 224.0,
      "Result!B6": 137.75,
      "Result!B7": 280.8,
      "Result!B8": 37.0,
      "Result!B9": 93.1
    },
    "id": "r17-b6-fmv-p4",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B9",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "row_values": [
        36.0,
        115.9,
        156.6,
        52.0,
        261.25,
        108.0,
        26.0,
        28.5
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 36.0,
      "Result!B3": 115.9,
      "Result!B4": 156.6,
      "Result!B5": 52.0,
      "Result!B6": 261.25,
      "Result!B7": 108.0,
      "Result!B8": 26.0,
      "Result!B9": 28.5
    },
    "id": "r17-b6-fmv-p5",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "row_values": [
        39.96,
        112.86,
        137.05,
        140.8,
        164.16,
        344.52,
        35.64,
        119.13,
        75.82,
        96.8
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 75.82,
      "Result!B11": 96.8,
      "Result!B2": 39.96,
      "Result!B3": 112.86,
      "Result!B4": 137.05,
      "Result!B5": 140.8,
      "Result!B6": 164.16,
      "Result!B7": 344.52,
      "Result!B8": 35.64,
      "Result!B9": 119.13
    },
    "id": "r17-b6-fmv-p6",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "row_values": [
        38.88,
        79.42,
        64.15,
        162.8,
        333.45,
        59.4,
        19.44,
        22.99,
        69.98,
        237.6
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 69.98,
      "Result!B11": 237.6,
      "Result!B2": 38.88,
      "Result!B3": 79.42,
      "Result!B4": 64.15,
      "Result!B5": 162.8,
      "Result!B6": 333.45,
      "Result!B7": 59.4,
      "Result!B8": 19.44,
      "Result!B9": 22.99
    },
    "id": "r17-b6-fmv-p7",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B11",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "row_values": [
        24.84,
        114.95,
        46.66,
        145.2,
        112.86,
        291.06,
        65.88,
        60.61,
        137.05,
        272.8
      ]
    },
    "golden_answer_cells": {
      "Result!B10": 137.05,
      "Result!B11": 272.8,
      "Result!B2": 24.84,
      "Result!B3": 114.95,
      "Result!B4": 46.66,
      "Result!B5": 145.2,
      "Result!B6": 112.86,
      "Result!B7": 291.06,
      "Result!B8": 65.88,
      "Result!B9": 60.61
    },
    "id": "r17-b6-fmv-p8",
    "primary_failure_family": "formula_materialization",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 297,
      "checksum": 445,
      "row_count": 7,
      "sentinel": "KEEP-r17-b6-ioc-p0"
    },
    "golden_answer_cells": {
      "Result!B2": 445,
      "Result!B3": "KEEP-r17-b6-ioc-p0"
    },
    "id": "r17-b6-ioc-p0",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "active_sum": 134,
      "checksum": 212,
      "row_count": 7,
      "sentinel": "KEEP-r17-b6-ioc-p1"
    },
    "golden_answer_cells": {
      "Result!B2": 212,
      "Result!B3": "KEEP-r17-b6-ioc-p1"
    },
    "id": "r17-b6-ioc-p1",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "active_sum": 237,
      "checksum": 349,
      "row_count": 7,
      "sentinel": "KEEP-r17-b6-ioc-p2"
    },
    "golden_answer_cells": {
      "Result!B2": 349,
      "Result!B3": "KEEP-r17-b6-ioc-p2"
    },
    "id": "r17-b6-ioc-p2",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 168,
      "checksum": 279,
      "row_count": 9,
      "sentinel": "KEEP-r17-b6-ioc-p3"
    },
    "golden_answer_cells": {
      "Result!B2": 279,
      "Result!B3": "KEEP-r17-b6-ioc-p3",
      "Result!B4": 168
    },
    "id": "r17-b6-ioc-p3",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "active_sum": 302,
      "checksum": 459,
      "row_count": 9,
      "sentinel": "KEEP-r17-b6-ioc-p4"
    },
    "golden_answer_cells": {
      "Result!B2": 459,
      "Result!B3": "KEEP-r17-b6-ioc-p4",
      "Result!B4": 302
    },
    "id": "r17-b6-ioc-p4",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "active_sum": 276,
      "checksum": 416,
      "row_count": 9,
      "sentinel": "KEEP-r17-b6-ioc-p5"
    },
    "golden_answer_cells": {
      "Result!B2": 416,
      "Result!B3": "KEEP-r17-b6-ioc-p5",
      "Result!B4": 276
    },
    "id": "r17-b6-ioc-p5",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "active_sum": 337,
      "checksum": 456,
      "row_count": 11,
      "sentinel": "KEEP-r17-b6-ioc-p6"
    },
    "golden_answer_cells": {
      "Result!B2": 456,
      "Result!B3": "KEEP-r17-b6-ioc-p6",
      "Result!B4": 337,
      "Result!B5": 11
    },
    "id": "r17-b6-ioc-p6",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "active_sum": 356,
      "checksum": 429,
      "row_count": 11,
      "sentinel": "KEEP-r17-b6-ioc-p7"
    },
    "golden_answer_cells": {
      "Result!B2": 429,
      "Result!B3": "KEEP-r17-b6-ioc-p7",
      "Result!B4": 356,
      "Result!B5": 11
    },
    "id": "r17-b6-ioc-p7",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "active_sum": 462,
      "checksum": 526,
      "row_count": 11,
      "sentinel": "KEEP-r17-b6-ioc-p8"
    },
    "golden_answer_cells": {
      "Result!B2": 526,
      "Result!B3": "KEEP-r17-b6-ioc-p8",
      "Result!B4": 462,
      "Result!B5": 11
    },
    "id": "r17-b6-ioc-p8",
    "primary_failure_family": "input_output_contract",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": [
        [
          2,
          212.0
        ],
        [
          3,
          240.0
        ],
        [
          4,
          105.0
        ],
        [
          5,
          143.0
        ],
        [
          7,
          168.0
        ],
        [
          1,
          221.0
        ],
        [
          2,
          132.0
        ],
        [
          3,
          145.0
        ],
        [
          5,
          237.0
        ],
        [
          6,
          46.0
        ],
        [
          7,
          236.0
        ],
        [
          1,
          192.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 2077.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b6-msp-p0",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "kept": [
        [
          2,
          132.0
        ],
        [
          3,
          117.0
        ],
        [
          4,
          108.0
        ],
        [
          5,
          74.0
        ],
        [
          7,
          196.0
        ],
        [
          1,
          226.0
        ],
        [
          2,
          56.0
        ],
        [
          3,
          235.0
        ],
        [
          5,
          116.0
        ],
        [
          6,
          106.0
        ],
        [
          7,
          188.0
        ],
        [
          1,
          223.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1777.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b6-msp-p1",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "kept": [
        [
          2,
          188.0
        ],
        [
          3,
          82.0
        ],
        [
          4,
          162.0
        ],
        [
          5,
          115.0
        ],
        [
          7,
          220.0
        ],
        [
          1,
          56.0
        ],
        [
          2,
          93.0
        ],
        [
          3,
          93.0
        ],
        [
          5,
          98.0
        ],
        [
          6,
          75.0
        ],
        [
          7,
          82.0
        ],
        [
          1,
          198.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1462.0,
      "Result!B3": 46,
      "Result!B4": 12
    },
    "id": "r17-b6-msp-p2",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": [
        [
          2,
          164.0
        ],
        [
          4,
          145.0
        ],
        [
          1,
          103.0
        ],
        [
          3,
          38.0
        ],
        [
          5,
          225.0
        ],
        [
          7,
          223.0
        ],
        [
          4,
          139.0
        ],
        [
          6,
          222.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1259.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b6-msp-p3",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "kept": [
        [
          2,
          182.0
        ],
        [
          4,
          151.0
        ],
        [
          1,
          58.0
        ],
        [
          3,
          99.0
        ],
        [
          5,
          60.0
        ],
        [
          7,
          109.0
        ],
        [
          4,
          237.0
        ],
        [
          6,
          31.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 927.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b6-msp-p4",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "kept": [
        [
          2,
          223.0
        ],
        [
          4,
          128.0
        ],
        [
          1,
          113.0
        ],
        [
          3,
          216.0
        ],
        [
          5,
          42.0
        ],
        [
          7,
          109.0
        ],
        [
          4,
          140.0
        ],
        [
          6,
          42.0
        ]
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1013.0,
      "Result!B3": 32,
      "Result!B4": 8
    },
    "id": "r17-b6-msp-p5",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b6-msp-p6",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b6-msp-p7",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "kept": []
    },
    "golden_answer_cells": {
      "Result!B2": 0,
      "Result!B3": 0,
      "Result!B4": 0
    },
    "id": "r17-b6-msp-p8",
    "primary_failure_family": "multi_step_pipeline",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        45.0,
        189.2,
        91.18,
        208.44,
        260.61,
        55.9,
        118.5,
        166.84,
        133.86,
        52.92
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1322.45
    },
    "id": "r17-b6-ska-p0",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        114.0,
        116.1,
        31.04,
        216.0,
        73.78,
        167.7,
        140.25,
        143.62,
        75.66,
        86.4
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1164.55
    },
    "id": "r17-b6-ska-p1",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B2",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        104.25,
        152.22,
        234.74,
        177.12,
        117.81,
        170.3,
        86.25,
        81.7,
        173.63,
        70.2
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 1368.22
    },
    "id": "r17-b6-ska-p2",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        27.75,
        105.78,
        146.47,
        74.52,
        224.91,
        27.3,
        157.5,
        184.9,
        23.28,
        117.72,
        45.22,
        270.4,
        73.5
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1479.25,
      "Result!B3": 1129.81
    },
    "id": "r17-b6-ska-p3",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        24.75,
        153.08,
        166.84,
        162.0,
        46.41,
        209.3,
        76.5,
        61.92,
        37.83,
        49.68,
        27.37,
        171.6,
        92.25
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 1279.53,
      "Result!B3": 1078.29
    },
    "id": "r17-b6-ska-p4",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        45.75,
        112.66,
        30.07,
        29.16,
        270.13,
        314.6,
        29.25,
        79.98,
        229.89,
        90.72,
        254.66,
        42.9,
        91.5
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 1621.27,
      "Result!B3": 984.0
    },
    "id": "r17-b6-ska-p5",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "amount_header": "recognized_amount",
      "converted": [
        180.75,
        121.26,
        45.59,
        237.6,
        192.78,
        301.6,
        36.75,
        205.54,
        127.07,
        156.6,
        138.04,
        287.3,
        147.0,
        206.4,
        212.43,
        190.08
      ],
      "key_header": "account_identifier",
      "rate_key_header": "rate_key"
    },
    "golden_answer_cells": {
      "Result!B2": 2786.79,
      "Result!B3": 2139.19,
      "Result!B4": 301.6
    },
    "id": "r17-b6-ska-p6",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "amount_header": "amount_usd",
      "converted": [
        57.75,
        165.12,
        118.34,
        244.08,
        64.26,
        302.9,
        54.75,
        104.92,
        59.17,
        136.08,
        197.54,
        179.4,
        103.5,
        183.18,
        96.03,
        70.2
      ],
      "key_header": "account_code",
      "rate_key_header": "account_code"
    },
    "golden_answer_cells": {
      "Result!B2": 2137.22,
      "Result!B3": 1852.54,
      "Result!B4": 302.9
    },
    "id": "r17-b6-ska-p7",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "amount_header": "posted_amount",
      "converted": [
        165.0,
        106.64,
        113.49,
        159.84,
        185.64,
        42.9,
        33.75,
        162.54,
        95.06,
        219.24,
        230.86,
        270.4,
        109.5,
        190.06,
        28.13,
        106.92
      ],
      "key_header": "acct_code",
      "rate_key_header": "ledger_code"
    },
    "golden_answer_cells": {
      "Result!B2": 2219.97,
      "Result!B3": 1664.77,
      "Result!B4": 270.4
    },
    "id": "r17-b6-ska-p8",
    "primary_failure_family": "schema_key_alignment",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        27,
        41,
        78,
        41,
        115,
        142
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 444,
      "Result!B3": 142
    },
    "id": "r17-b6-tsr-p0",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 0,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "target_sheet": "Quarter_2_FINAL",
      "target_values": [
        49,
        106,
        163,
        53,
        124,
        26
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 521,
      "Result!B3": 163
    },
    "id": "r17-b6-tsr-p1",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 1,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B3",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate",
      "Data_C_candidate",
      "Data_D_candidate",
      "Data_E_candidate"
    ],
    "expected": {
      "target_sheet": "Quarter_3_FINAL",
      "target_values": [
        100,
        150,
        85,
        124,
        149,
        138
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 746,
      "Result!B3": 150
    },
    "id": "r17-b6-tsr-p2",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 0,
    "profile_index": 2,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_4_FINAL",
      "target_values": [
        81,
        136,
        85,
        75,
        44,
        34,
        61,
        178
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 694,
      "Result!B3": 178,
      "Result!B4": 86.75
    },
    "id": "r17-b6-tsr-p3",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 3,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Data_A_candidate",
      "Data_B_candidate"
    ],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        27,
        20,
        155,
        145,
        90,
        113,
        136,
        62
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 748,
      "Result!B3": 155,
      "Result!B4": 93.5
    },
    "id": "r17-b6-tsr-p4",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 4,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B4",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "target_sheet": "Quarter_2_FINAL",
      "target_values": [
        143,
        116,
        33,
        128,
        32,
        134,
        60,
        166
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 812,
      "Result!B3": 166,
      "Result!B4": 101.5
    },
    "id": "r17-b6-tsr-p5",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 1,
    "profile_index": 5,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 6,
    "distractor_count": 0,
    "distractor_level": 0,
    "distractor_sheets": [],
    "expected": {
      "target_sheet": "Quarter_3_FINAL",
      "target_values": [
        129,
        136,
        73,
        79,
        95,
        59,
        48,
        75,
        73,
        96
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 863,
      "Result!B3": 136,
      "Result!B4": 86.3,
      "Result!B5": 2
    },
    "id": "r17-b6-tsr-p6",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 6,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 2,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 6,
    "distractor_count": 2,
    "distractor_level": 1,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B"
    ],
    "expected": {
      "target_sheet": "Quarter_4_FINAL",
      "target_values": [
        74,
        77,
        27,
        28,
        21,
        158,
        82,
        95,
        74,
        167
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 803,
      "Result!B3": 167,
      "Result!B4": 80.3,
      "Result!B5": 2
    },
    "id": "r17-b6-tsr-p7",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 7,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 0,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  },
  {
    "answer_position": "Result!B2:B5",
    "block": 6,
    "distractor_count": 5,
    "distractor_level": 2,
    "distractor_sheets": [
      "Archive_A",
      "Archive_B",
      "Archive_C",
      "Archive_D",
      "Archive_E"
    ],
    "expected": {
      "target_sheet": "Quarter_1_FINAL",
      "target_values": [
        99,
        130,
        81,
        66,
        63,
        90,
        176,
        88,
        73,
        158
      ]
    },
    "golden_answer_cells": {
      "Result!B2": 1024,
      "Result!B3": 176,
      "Result!B4": 102.4,
      "Result!B5": 3
    },
    "id": "r17-b6-tsr-p8",
    "primary_failure_family": "target_sheet_range",
    "procedure_depth_level": 2,
    "profile_index": 8,
    "role": "e3_future_candidate",
    "schema_ambiguity_level": 1,
    "suite_id": "E2-R17-CONTROLLED-SPREADSHEET-SUITE-V2"
  }
]


BOUND DOSSIER END
