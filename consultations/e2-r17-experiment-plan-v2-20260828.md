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
