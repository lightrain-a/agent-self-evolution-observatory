# E2-R17 State-Compiler Bridge V3R — independent-manuscript-review repair

Status: **REVISED_AFTER_MANUSCRIPT_ADVERSARIAL_REVIEW / PROPOSAL_ONLY / ZERO_PROVIDER / NO_EXECUTION_AUTHORITY**  
Base lineage: `191ffd4e676cd3c748c61d53275b48e7722fc003`  
Branch: `research/e2-r17-manuscript-state-generation-20260903`

This document does not alter, supersede, or authorize the active single-case constrained-state Recovery V3. Recovery V3 remains frozen and must complete under its existing contract before this bridge can obtain scientific execution authority.

## 1. Scientific question

The bridge separates two factors that the historical E2-R17 experiments confounded:

1. **Evidence source** — what trajectory evidence reaches persistent learning?
2. **State generation** — how is that evidence converted into persistent skill state?

The prospective bridge is therefore a 2×2:

| Evidence source | Free-form state generation | Constrained state compiler |
|---|---|---|
| Winner | `W_FREE` | `W_COMP` |
| First-Fail-4 | `FF4_FREE` | `FF4_COMP` |

All four cells begin from the same initial skill and the same eight search pools for a stream. Acting/search is frozen before learning. The learning projection cannot alter the served acting winner.

The primary causal questions are:

- **Selected evidence-package effect:** does replacing four winner trajectory+score evidence packages with four rejected First-Fail trajectory+score packages improve future skill utility?
- **State-generation-method effect:** holding the selected evidence package fixed, does the frozen constrained compiler improve future utility relative to the native free-form updater?
- **Interaction:** does the constrained compiler specifically make the First-Fail evidence package more usable, rather than merely acting as a generic better state generator?
- **Prospective state-realization variation:** under byte-identical fresh FF4 evidence, does disagreement between two independently synthesized free-form states exceed within-frozen-state actor disagreement on the same tasks?

The protocol does **not** identify trajectory text separately from its verifier score, and it does **not** identify determinism/constraint separately from all other differences between the complete free-form and compiler methods. The small variance probe is a direct prospective localization, not a full variance-component estimate.

This bridge is development evidence. It is not E3 confirmation.

## 2. Evidence-level boundaries

Three evidence levels must remain separate:

1. **State-level mechanism evidence:** current G0–G3 micro and its frozen-state remeasurements.
2. **Automatic learning-method evidence:** this bridge, if the automatic diagnosis/compiler is frozen and prospective.
3. **Confirmatory generalization evidence:** untouched E3 only after the bridge passes.

No result from level 1 can be promoted to level 2 or 3 by wording alone.

## 3. Preconditions — hard gate before any bridge provider call

Bridge execution authority is forbidden unless all of the following are true:

1. Recovery V3 reaches 72/72 under its existing exactly-once contract.
2. The original 18-task M2 primary gate is applied without modification.
3. If the M2 primary passes, the already-frozen 17-task provider-era sensitivity is strictly positive. If either M2 gate fails, the COMPLETE/VERIFY/RECOVER compiler branch stops.
4. The revised M3R exact-evidence frozen-state regeneration audit is completed on the four already-existing states (`FF_HIST`, `FF_R1`, `FF_R2`, `WIN_COMMON`) under its separately frozen measurement authority; M3R makes zero updater calls and no outcome-conditioned extra actor replicate is allowed.
5. M3R adjudication is recorded before M4 provider authority. `D_U-D_A <= 0` removes the state-regeneration-instability mechanism claim, but does not rewrite M2 or silently change the M4 complete-method estimand.
6. The compiler vocabulary, diagnosis rules, composition, scope-matched and score-only generic controls, state-budget rule, bridge task split, hierarchical SCREEN/VALIDATION gates, and repeated-synthesis diagnostic are frozen before any M4 provider call.

No M3R result can rescue a failed M2 semantic gate. No M2 result can rescue a failed M3R regeneration claim. Neither stage grants E3 authority.

## 4. Prospective fresh-development suite

Target design object: **120 fresh task artifacts**, disjoint from the reused S1 18-task panel and disjoint from untouched E3.

- 12 independent development streams.
- 8 update tasks per stream = 96 update tasks.
- 12 fresh K=1 SCREEN heldout tasks.
- 12 different fresh K=1 VALIDATION heldout tasks.
- Total = 120 unique task artifacts.
- The 12 streams are frozen into:
  - 6-stream `SCREEN`
  - 6-stream `VALIDATION`
- Stream split assignment is deterministic from stream content SHA before any provider execution.
- SCREEN and VALIDATION heldout task IDs and content SHA-256 sets are disjoint and frozen before the first provider execution.
- Validation is not opened until the frozen SCREEN gate is adjudicated.
- Validation can confirm or reject the frozen bridge within development, but it cannot be used to tune the compiler, primitive vocabulary, code, or thresholds.

V2 intentionally superseded the earlier 108-task design because reusing one common heldout panel across the SCREEN decision and later VALIDATION would make the latter evaluation-dependent. V3 keeps the same already-qualified 120-task suite and adds only a pre-frozen variance-remeasurement view of six VALIDATION tasks; it does not create or replace task artifacts. No existing outcome-selected S1 task may enter this suite.

## 5. Exact 8-pool updater semantics

Each stream contains exactly eight frozen K=8 search pools. Search/acting is identical across all four bridge cells.

### 5.1 Winner source

`WINNER` uses the served winner trajectory on all eight pools.

### 5.2 First-Fail-4 source

`FIRST_FAIL_4` changes evidence on exactly four of the eight pools, never more and never fewer:

- A pool is eligible only if it is mixed: at least one success and at least one failure.
- The rejected trajectory is the deterministic `first_failed_nonwinner` already defined by the E2-R17 projection code.
- A stream is bridge-eligible only if at least four of its eight pools are mixed.
- Exactly four eligible pools are selected by the lowest SHA-256 of
  `E2-R17-BRIDGE-FF4-v1|stream_id|pool_id`.
- On those four pools, `FIRST_FAIL_4` exposes the selected failed nonwinner.
- On the other four pools, it exposes exactly the same winner evidence as `WINNER`.

Thus the evidence-source contrast has a fixed **4-of-8 replacement count**. A stream with 5–8 mixed pools does not receive more replacements. This is not described as equal information dose: failed and winning trajectories can differ in length, content, entropy, and semantic information.

### 5.3 Support gate

The set of SCREEN and VALIDATION streams is frozen before search-pool outcomes are inspected. If any required stream has fewer than four mixed pools, that stage is `HOLD_INSUFFICIENT_MIXED_SUPPORT`; no stream substitution, task replacement, K increase, model change, or outcome-conditioned rerun is allowed.

The support gate changes the estimand to streams for which a 4-of-8 First-Fail replacement is well-defined. It must not be described as an unconditional all-task effect.

## 6. Information parity between free-form and compiler arms

This is a hard causal-purity requirement.

For each stream/pool, both generator arms receive the **same selected evidence trajectory**, the same selected verifier score, and the same learner-visible evidence bytes.

The constrained path may use only:

- learner-visible trajectory text;
- selected binary verifier score.

It may not use:

- arm or projection label;
- stream/family/category identity;
- task family or matched-skeleton identity;
- rollout identity as a semantic feature;
- hidden golden answer;
- heldout outcome;
- historical S1 outcome;
- provider-era metadata;
- source SHA except for integrity receipts.

The current prototype enforces this by exposing `extract_visible_signals(evidence_text, selected_score)` and no arm/family/projection/task-ID argument.

Before execution, an automated parity audit must prove that the SHA-256 of compiler input evidence equals the free-form updater-visible evidence SHA for every corresponding update unit.

## 7. Constrained compiler v1

The compiler is an explicit algorithmic object, not a free-form writer.

### 7.1 Typed diagnosis

From each selected evidence unit, derive:

`d = (failure_stage, failed_invariants, observed_evidence, required_repairs)`

Only learner-visible content is used.

### 7.2 Frozen primitive vocabulary

Minimal v1 vocabulary:

- `VERIFY_OUTPUT`
- `COMPLETE_WORKFLOW`
- `RECOVER_TOOL_ERROR`

No new primitive may be added after SCREEN outcomes are visible. A compiler miss is a scientific failure, not permission to patch the vocabulary.

### 7.3 Selection semantics

A successful selected trajectory (`score=1`) is not force-labelled as needing a generic repair.

For a failed selected trajectory (`score=0`):

- no materialized write/save -> `COMPLETE_WORKFLOW`;
- materialized save but no reload/verification -> `VERIFY_OUTPUT`;
- visible tool error without visible clean recovery -> `RECOVER_TOOL_ERROR`.

Multiple repairs may compose.

### 7.4 Canonical compilation

Compilation is deterministic:

`C({d_i}, S0) -> S_compiled`

Rules:

- union requested primitives across the eight evidence units;
- fixed primitive order;
- duplicate diagnoses cannot increase state length;
- `COMPLETE_WORKFLOW` subsumes the separately rendered `VERIFY_OUTPUT` surface to avoid duplicate instructions;
- `RECOVER_TOOL_ERROR` composes after completion semantics;
- identical diagnosis bundles compile byte-identically;
- every diagnosis and compiled skill is content-addressed.

The current zero-provider prototype reproduces the frozen G1/G2/G3 skill surfaces byte-for-byte for the corresponding typed diagnoses.

## 8. Free-form generator

`W_FREE` and `FF4_FREE` use the same frozen first-party updater implementation, configuration, model, retry policy, evidence rendering, selected-score semantics, and eight-pool aggregation path.

The only allowed difference between W_FREE and FF4_FREE is the four pre-frozen evidence replacements.

The compiler cells do not call an LLM state writer. Therefore the 2×2 estimates the effect of the complete state-generation mechanism, not a token-for-token causal effect of 'determinism alone'. Any paper claim must use that scope.

## 9. State-budget and specificity controls

State size is a plausible confound and must be measured prospectively.

For every learned/compiled state record:

- full skill bytes/tokens;
- delta bytes/tokens relative to S0;
- number of distinct repair clauses/primitives;
- skill SHA-256.

Hard rule:

- compiler output may contain only frozen primitive blocks and cannot grow with duplicate evidence;
- no outcome-based pruning/expansion is allowed;
- free-form state is not post-hoc truncated after generation, because that would create an additional treatment.

Therefore the primary generator estimand is **native free-form updater versus frozen constrained compiler as complete methods**. State length is a measured mediator/confound diagnostic, not claimed to be perfectly matched.

If publication later needs a pure length-matched decomposition, it must be a separately preregistered experiment; it cannot be retrofitted into this bridge after outcomes.

## 10. Frozen stochasticity and runtime contract

The main 2×2 compares the first deployed realization of each free-form cell with the deterministic compiler. V3 separately freezes a small repeated-synthesis probe on VALIDATION so residual provider nondeterminism can be measured rather than merely discussed. Neither object should be confused with an isolated deterministic-generator causal effect.

Before any Stage-A provider call, freeze and content-address the following execution parameters.

### Search / actor

- requested model: `deepseek-v4-pro`;
- required resolved model: `deepseek-v4-pro-ga-260813`;
- thinking: disabled;
- temperature: 0;
- max turns: 10;
- max output tokens: 8192;
- provider retry limit: 0;
- K=8 for update-pool acquisition and K=1 for heldout evaluation;
- no outcome-conditioned rerun;
- fresh/reset task runtime for every state × heldout-task evaluation;
- task × arm execution order fixed by a pre-frozen hash salt.

### Free-form updater

- first-party updater: `mindmemos.pipelines.skill.evolution.SkillEvolver`;
- exact eight evidence units per state;
- requested model: `deepseek-v4-pro`;
- required resolved model: `deepseek-v4-pro-ga-260813`;
- thinking: disabled;
- temperature: 0;
- provider retry limit: 0;
- `max_parse_attempts=2` and `max_correction_attempts=1` only for the already-defined deterministic parse/apply correction path; the correction call is visible, claimed, and receipted and is not an outcome-based scientific retry;
- no second updater draw may be requested because the first scientific state is inconvenient.

The current Ark route does not provide a reliable user-controlled generation seed for all relevant calls. Therefore the protocol must not claim seed-level determinism. The main 2×2 estimand remains the performance of the **first prospectively drawn deployed free-form state** versus the deterministic compiled state. If residual provider nondeterminism remains, it is part of the deployed free-form method rather than silently averaged away.

V3 adds one and only one pre-authorized second free-form synthesis, `FF4_FREE_B`, for each of the six VALIDATION streams under the exact same frozen FF4 evidence package. This second draw exists solely for the predeclared variance probe in Section 14; it is not a retry, cannot replace `FF4_FREE_A`, and is generated regardless of whether the first state is favorable. No third draw is authorized.

Downstream actor execution uses the same temperature-0/retry-0 policy. The main validation evaluation remains one actor execution per state×task. On the six pre-frozen variance tasks, V3 additionally authorizes exactly one second actor execution for `FF4_FREE_A`, `FF4_FREE_B`, and `FF4_COMP`, regardless of the first outcome. No other repeated actor execution is authorized.

## 11. Score-matched trajectory-blind generic falsifier

The strongest simple alternative is not merely generic `COMPLETE_WORKFLOW`. It is that the compiler can ignore trajectory content, observe only that failures occurred, and inject the strongest generic evaluator-aligned repair bundle.

A zero-updater control is therefore frozen:

`SCORE_ONLY_GENERIC_MAX`

Inputs:

- the same ordered eight selected binary verifier scores as the corresponding evidence-source arm;
- **no trajectory text**;
- no task/family/arm/projection label.

Frozen semantics:

- if all eight selected scores are 1, compile no repair and return S0;
- if any selected score is 0, compile the maximal nonredundant v1 generic bundle `COMPLETE_WORKFLOW + RECOVER_TOOL_ERROR` (with verification already subsumed by the completion loop).

For FF4 this control therefore receives the same four-failure/four-success score pattern but none of the rejected trajectory content. The state is pre-determined by score pattern and cannot adapt to outcomes.

This control does not participate in the 2×2 primary arm selection. It is a falsifier:

- if `FF4_COMP` does not outperform `SCORE_ONLY_GENERIC_MAX`, trajectory-conditioned diagnosis is not established;
- the bridge may still support canonical/generic persistent-state compilation, but not learning a trajectory-specific repair from rejected trajectory content.

Because this control needs no state-writer call, it adds no state-generation provider cost.

## 12. Scope-matched generic falsifier

`SCORE_ONLY_GENERIC_MAX` is deliberately strong but can be longer than the trajectory-conditioned compiler state. Therefore a compiler win could still be explained by writing fewer irrelevant checklist clauses rather than selecting the correct repair semantics.

V3 freezes a second diagnostic control:

`SCOPE_MATCHED_GENERIC_MAX`

Inputs:

- the same ordered eight selected binary verifier scores;
- one scalar `k`, the number of repair blocks that the trajectory-conditioned compiler would render after canonical deduplication;
- **no trajectory text and no repair-primitive identity**;
- no task/family/arm/projection label.

Frozen semantics:

- `k=0` -> return S0;
- `k=1` -> compile the strongest coherent one-block generic v1 surface, `COMPLETE_WORKFLOW`;
- `k=2` -> compile `COMPLETE_WORKFLOW + RECOVER_TOOL_ERROR`.

Compiler v1 can render only 0, 1, or 2 nonredundant repair blocks. The control therefore matches **rendered repair-block count**, though not exact token count. Full state bytes/tokens remain reported. The scalar `k` is intentionally a narrow scope side-channel: it is allowed only so this control can ask whether the trajectory-conditioned compiler wins beyond sparsity/state-scope selection. It never receives which primitive(s) the compiler selected.

Trajectory-conditioned diagnosis is eligible only if `FF4_COMP` exceeds **both** `SCORE_ONLY_GENERIC_MAX` and `SCOPE_MATCHED_GENERIC_MAX` under the relevant frozen gate. If it beats the first but not the second, the result supports selective state scope/canonicalization at most, not semantic diagnosis from trajectory content.

Both generic controls are deterministic and add no state-generation provider cost.

## 13. SCREEN design and hierarchical gates

SCREEN contains six pre-frozen fresh streams. Per stream build the four primary 2×2 states (`W_FREE`, `FF4_FREE`, `W_COMP`, `FF4_COMP`) plus both deterministic FF4 controls (`SCORE_ONLY_GENERIC_MAX`, `SCOPE_MATCHED_GENERIC_MAX`). All are evaluated on the same **12 SCREEN heldout tasks**, disjoint from VALIDATION. Actor/runtime/model/verifier settings are matched, evaluation order is hash-balanced by task × state arm, and no partial outcome is read before completion audit.

Define per-stream utility `J` as mean binary success across the 12 heldout tasks and define:

- `G_F = J(FF4_COMP) - J(FF4_FREE)` — complete generator-method contrast under exactly matched FF4 evidence;
- `S_C = J(FF4_COMP) - J(W_COMP)` — evidence-package contrast under the compiler;
- `I = [J(FF4_COMP)-J(FF4_FREE)] - [J(W_COMP)-J(W_FREE)]` — evidence×generator interaction.

### 13.1 Primary matched-evidence generator SCREEN gate

`GENERATOR_SCREEN_PASS` tests only the complete generator-method contrast under matched FF4 evidence. It requires:

1. mean `G_F > 0`;
2. `G_F > 0` on at least 4/6 streams;
3. no catastrophic arm-specific technical failure or hidden information-parity violation.

### 13.2 Trajectory-conditioned-content SCREEN gate

Separately define `CONTENT_SCREEN_PASS` to require both:

1. mean `J(FF4_COMP) - J(SCORE_ONLY_GENERIC_MAX) > 0`;
2. mean `J(FF4_COMP) - J(SCOPE_MATCHED_GENERIC_MAX) > 0`, with no control-construction drift.

The first condition rules out score-only generic workflow hygiene; the second rules out a benefit explained only by writing fewer repair blocks. For this paper, VALIDATION authority requires both `GENERATOR_SCREEN_PASS` and `CONTENT_SCREEN_PASS`, because failure to beat the scope-matched generic control is a predeclared paper-level STOP condition. Neither gate depends on First-Fail being superior to Winner or on a positive Evidence×Generator interaction.

### 13.3 Secondary rejected-evidence SCREEN classification

Independently record whether the rejected-evidence-specific hypothesis is promising:

- mean `S_C > 0`;
- `S_C > 0` on at least 4/6 streams;
- mean interaction `I > 0`.

Failure of any of these conditions sets `REJECTED_SOURCE_SCREEN_FAIL` but **cannot veto generator VALIDATION** once `GENERATOR_SCREEN_PASS` holds. It only removes authority to promote a First-Fail-specific claim.

No threshold may be weakened after SCREEN reveal.

## 14. VALIDATION and direct variance probe

If and only if both `GENERATOR_SCREEN_PASS` and `CONTENT_SCREEN_PASS` hold, freeze a validation authorization without changing the diagnosis schema, primitive vocabulary, compiler code, evidence replacement rule, controls, heldout metric, or thresholds. Run the same four primary 2×2 states plus both frozen FF4 generic controls on the six pre-frozen VALIDATION streams and the **12 disjoint VALIDATION heldout tasks**.

### 14.1 Generator-method confirmation

For validation, `FF4_FREE_A` denotes the first prospectively drawn free-form state used by the ordinary 2×2. V3R additionally generates exactly one `FF4_FREE_B` state per validation stream from the **same byte-identical FF4 evidence package**. `FF4_FREE_B` is not a retry, cannot replace A, and does not change the primary generator estimand.

Define the primary validation contrast

`G_F_A = J(FF4_COMP) - J(FF4_FREE_A)`.

`GENERATOR_VALIDATION_PASS` requires:

1. mean `G_F_A > 0`;
2. `G_F_A > 0` on at least 4/6 validation streams;
3. no technical or evidence-parity contract violation.

Separately, `CONTENT_VALIDATION_PASS` requires mean `J(FF4_COMP) - J(SCORE_ONLY_GENERIC_MAX) > 0` and mean `J(FF4_COMP) - J(SCOPE_MATCHED_GENERIC_MAX) > 0` with no control-construction drift. A top-tier trajectory-conditioned generator claim requires both generator and content validation. `FF4_FREE_B` is reserved for the direct regeneration probe below rather than averaged into the primary method contrast.

### 14.2 Pre-frozen same-evidence synthesis × actor-remeasurement probe

The direct variance probe uses exactly six VALIDATION heldout tasks, one per controlled family, selected before any bridge provider execution by lowest SHA-256 under salt `E2-R17-BRIDGE-VARIANCE-PROBE-v1`:

- `r17-b9-agj-p1`
- `r17-b9-fmv-p8`
- `r17-b9-ioc-p8`
- `r17-b9-msp-p2`
- `r17-b9-ska-p2`
- `r17-b9-tsr-p6`

Sorted task-set SHA-256: `71f7f1ac01f72e187964a526f2e6e12247f90a9199f6a124f4b463b2381760f8`.

For every validation stream under the same exact FF4 evidence package:

- `FF4_FREE_A`: first prospectively drawn free-form state;
- `FF4_FREE_B`: one additional prospectively drawn free-form state;
- `FF4_COMP`: deterministic compiled state.

The ordinary validation evaluation supplies actor replicate 1 for all three states: A and COMP from the primary validation run, B from its full 12-task evaluation. On the six variance tasks only, execute exactly one additional actor replicate for A, B, and COMP. Thus each variance task has `(A1,A2,B1,B2,C1,C2)` and no third actor replicate.

For stream `s`, define:

`D_U(s) = mean_q | mean(A1,A2) - mean(B1,B2) |`

and

`D_A(s) = 0.5 * mean_q [ |A1-A2| + |B1-B2| ]`.

`D_U` measures outcome disagreement between two independently synthesized FREE states after averaging the two actor realizations; `D_A` measures within-frozen-state actor disagreement. Also record compiler actor disagreement

`D_C(s) = mean_q |C1-C2|`

as a diagnostic.

`VARIANCE_LOCALIZATION_PASS` requires:

1. mean `[D_U - D_A] > 0` across the six validation streams;
2. `D_U - D_A > 0` on at least 4/6 validation streams.

This is a small prospective localization, not a full population variance-component estimate. If it fails, the paper must drop claims that state-generation variance itself is the demonstrated bottleneck, even if the complete compiler method improves utility.

### 14.3 Rejected-evidence confirmation remains secondary

Independently evaluate on VALIDATION:

- mean `S_C > 0`;
- `S_C > 0` on at least 4/6 streams;
- mean interaction `I > 0`.

Failure sets `REJECTED_SOURCE_VALIDATION_FAIL` and removes the rejected-failure-specific claim. It does **not** invalidate an already-passed generator-method result.

## 15. Hierarchical decision table

After prospective VALIDATION, adjudicate claims independently rather than forcing one conjunctive paper story.

### A. Generator SCREEN fails

`STOP_AUTOMATIC_STATE_GENERATOR_METHOD_STORY`

VALIDATION remains sealed. No automatic compiler-method or fresh regeneration claim proceeds.

### B. Generator VALIDATION fails

`STOP_AUTOMATIC_STATE_GENERATOR_METHOD_STORY_AFTER_VALIDATION`

Do not open E3 for the compiler method.

### C. Generator SCREEN passes but content SCREEN fails

`STOP_TRAJECTORY_CONDITIONED_GENERATOR_PAPER_GENERIC_OR_SCOPE_EXPLAINS_EFFECT`

The observed benefit may come from generic evaluator-aligned workflow advice or state sparsity/scope. Under the manuscript review STOP rule, do not spend VALIDATION/E3 budget trying to rescue a trajectory-conditioned generator paper.

### D. Generator and content controls pass, but regeneration localization fails

`PASS_CANONICAL_STATE_GENERATION_METHOD_DROP_REGENERATION_MECHANISM_CLAIM`

A complete canonical state-generation method effect may remain, but the manuscript must drop claims that fresh same-evidence state regeneration itself is the demonstrated mechanism.

### E. Generator + content controls + regeneration probe pass, rejected-source confirmation fails

`PASS_STATE_GENERATION_METHOD_AND_REGENERATION_DROP_REJECTED_SOURCE_CLAIM`

This is eligible for a **separate state-generation E3 proposal**. Drop the claim that First-Fail evidence is uniquely or generally better than Winner evidence.

### F. Generator + content controls + regeneration + rejected-source/interaction all pass

`PASS_FULL_BRIDGE_ELIGIBLE_FOR_SEPARATE_E3_PROPOSAL`

Both the state-generation and rejected-evidence moderator stories are eligible for separate untouched confirmation. This still grants no E3 authority by itself.

## 16. Cost control

The compiler and both generic controls are zero-provider for state generation. Provider cost comes from:

- search-pool acquisition if the 96 update-task pools are not already prospectively acquired;
- SCREEN: two free-form updater states per stream (`W_FREE`, `FF4_FREE`);
- VALIDATION after both `GENERATOR_SCREEN_PASS` and `CONTENT_SCREEN_PASS`: the same two primary free-form states plus exactly one additional `FF4_FREE_B` state per validation stream;
- downstream actor evaluation.

Relative to V2, V3 adds only:

- 6 additional free-form updater states total (one `FF4_FREE_B` per validation stream);
- 144 actor units for the new scope-matched control across SCREEN+VALIDATION (12 tasks × 12 streams);
- 72 actor units for the full 12-task evaluation of the six `FF4_FREE_B` states;
- 108 second-actor-replicate units on the six variance tasks for A, B, and COMP (6 tasks × 3 states × 6 validation streams).

Thus the direct regeneration probe adds 6 state syntheses and 180 actor units; the scope control adds no state-writer calls. SCREEN still runs before VALIDATION, so all validation/regeneration cost is avoided if either the fresh generator gate or load-bearing content-control gate fails.

No second backbone, public benchmark, or E3 call is authorized by this protocol.

## 17. Current prototype qualification

Zero-provider unit tests required before any bridge contract can be drafted:

- successful winner -> no forced generic repair;
- incomplete failed trajectory -> COMPLETE_WORKFLOW;
- saved-but-unverified failure -> VERIFY_OUTPUT;
- unrecovered visible tool error -> RECOVER_TOOL_ERROR;
- clean recovery suppresses redundant recovery primitive;
- deterministic compilation;
- duplicate diagnoses do not inflate state;
- exact reproduction of frozen G1/G2/G3 surfaces for corresponding diagnoses;
- hidden arm/family/projection/task labels absent from compiler input API;
- score-only generic control receives exactly eight binary scores and no trajectory text;
- score-only generic control compiles the frozen maximal nonredundant generic surface on any failure and returns S0 on all-success input;
- canonical rendered repair-block count is deterministic and restricted to 0/1/2 under v1;
- scope-matched generic control receives only the score pattern plus rendered-block count, never trajectory text or primitive identity;
- scope-matched generic control returns S0 at `k=0`, G2-equivalent one-block generic state at `k=1`, and G3-equivalent two-block generic state at `k=2`.

Current status after V3 revision: **15/15 compiler tests PASS**.

## 18. Authority boundary

This protocol grants **zero** authority for:

- provider calls;
- search-pool acquisition;
- updater execution;
- repeated free-state synthesis;
- bridge actor evaluation;
- variance actor remeasurement;
- validation opening;
- E3;
- second backbone;
- public benchmark;
- paper promotion.

It is a prospective design object only. The active Recovery V3 remains the only relevant future scientific execution path under its own existing authority and quota schedule.
