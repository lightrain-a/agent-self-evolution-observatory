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
