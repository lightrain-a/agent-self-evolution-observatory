# E2-R17 State-Compiler Bridge — prospective zero-provider protocol

Status: **PROPOSAL_ONLY / ZERO_PROVIDER / NO_EXECUTION_AUTHORITY**  
Base lineage: `191ffd4e676cd3c748c61d53275b48e7722fc003`  
Branch: `research/e2-r17-state-compiler-bridge-proposal-20260903`

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

- **Evidence-source effect:** does replacing winner evidence with rejected First-Fail evidence on a fixed equal dose of four mixed pools improve future skill utility?
- **Generator effect:** holding the selected evidence fixed, does constrained compilation improve future utility relative to free-form state generation?
- **Interaction:** does constrained compilation specifically make rejected evidence more usable, rather than merely acting as a generic better prompt/state generator?

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
2. Original 18-task primary gate is applied without modification.
3. If primary PASS, the already-frozen 17-task provider-era sensitivity is positive.
4. Only G0 + the simplest passing selected arm are remeasured in exactly two fresh complete replicates.
5. No additional replicate is added because of an inconvenient result.
6. The selected state remains directionally useful across the frozen stability remeasurements.
7. The compiler vocabulary, diagnosis rules, composition, conflict resolution, state-budget rule, and bridge task split are frozen before bridge heldout outcomes are inspected.

If the current micro FAILs, or the selected state fails the fixed stability remeasurement, the COMPLETE/VERIFY/RECOVER compiler branch stops. No E3 opening is permitted.

## 4. Prospective fresh-development suite

Target design object: **108 fresh task artifacts**, disjoint from the reused S1 18-task panel and disjoint from untouched E3.

- 12 independent development streams.
- 8 update tasks per stream = 96 update tasks.
- 12 common fresh K=1 heldout tasks = 12 evaluation tasks.
- Total = 108 unique task artifacts.
- The 12 streams are frozen into:
  - 6-stream `SCREEN`
  - 6-stream `VALIDATION`
- Split assignment is deterministic from stream content SHA before any provider execution.
- Validation is not opened until the frozen SCREEN gate is adjudicated.
- Validation can confirm or reject the frozen bridge within development, but it cannot be used to tune the compiler or thresholds.

If the final 108-task suite is not yet available, suite construction is a separate zero-provider stage. No existing outcome-selected S1 task may enter this suite.

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

Thus the evidence-source contrast has a fixed 4-of-8 failure dose. A stream with 5–8 mixed pools does not receive a larger treatment dose.

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

## 10. Trajectory-blind generic-workflow falsifier

The strongest simple alternative is that the compiler merely injects generic good spreadsheet hygiene.

A zero-updater-control state is therefore frozen for SCREEN only:

`GENERIC_COMPLETE = S0 + COMPLETE_WORKFLOW`

It is trajectory-blind and identical across streams.

This control does not participate in the 2×2 primary selection. It is a falsifier:

- if `FF4_COMP` does not outperform or behaviorally differentiate from `GENERIC_COMPLETE`, evidence-conditioned diagnosis is not established;
- the bridge may still support generic persistent-state compilation, but not trajectory-conditioned repair learning.

Because this control needs only actor evaluation, it adds no state-generation provider cost.

## 11. SCREEN design and gates

SCREEN contains six pre-frozen fresh streams.

Per stream, build four primary states:

- `W_FREE`
- `FF4_FREE`
- `W_COMP`
- `FF4_COMP`

and one diagnostic `GENERIC_COMPLETE` state.

All are evaluated on the same 12 fresh heldout tasks with matched actor/runtime/model/verifier settings. Evaluation order is hash-balanced by task × state arm. No partial outcome is read before SCREEN completion and completion audit.

Define per-stream heldout utility `J` as mean binary success across the 12 heldout tasks.

Primary SCREEN contrasts:

- generator-on-failure: `G_F = J(FF4_COMP) - J(FF4_FREE)`
- source-under-compiler: `S_C = J(FF4_COMP) - J(W_COMP)`
- interaction: `I = [J(FF4_COMP)-J(FF4_FREE)] - [J(W_COMP)-J(W_FREE)]`

SCREEN is a development gate, not a confirmatory p-value stage. It passes only if all are true:

1. mean `G_F > 0`;
2. `G_F > 0` on at least 4/6 streams;
3. mean `S_C > 0`;
4. `S_C > 0` on at least 4/6 streams;
5. mean interaction `I > 0`;
6. `FF4_COMP` mean utility is strictly greater than `GENERIC_COMPLETE` mean utility;
7. no catastrophic arm-specific technical failure or hidden information-parity violation.

If SCREEN fails any primary condition, bridge status is `STOP_OR_PIVOT_BEFORE_VALIDATION`; VALIDATION remains sealed.

No threshold may be weakened after SCREEN reveal.

## 12. VALIDATION design and gates

If and only if SCREEN passes, freeze a validation authorization without changing:

- diagnosis schema;
- primitive vocabulary;
- compiler code;
- evidence-dose rule;
- state-generation implementations;
- heldout metric;
- thresholds.

Run the same four primary 2×2 states on the six pre-frozen VALIDATION streams and the same 12-task validation-compatible heldout protocol.

Validation requires:

1. mean `G_F > 0`;
2. mean `S_C > 0`;
3. mean interaction `I > 0`;
4. at least 4/6 validation streams have `G_F > 0`;
5. at least 4/6 validation streams have `S_C > 0`.

The generic-workflow falsifier may be evaluated in validation only if it was frozen before SCREEN; its result remains diagnostic and cannot rescue a failed primary 2×2 gate.

## 13. Decision table

After prospective bridge validation:

### A. Compiler does not beat free-form on First-Fail

If `G_F` fails:

`STOP_STATE_GENERATION_BOTTLENECK_METHOD_STORY`

Do not open E3 for the compiler claim.

### B. Compiler helps, but First-Fail is not better than Winner under compiler

If `G_F` passes but `S_C` fails:

`PIVOT_RELIABLE_PERSISTENT_STATE_COMPILATION_ONLY`

Drop the rejected-failure claim. The project may continue only as a state-compilation method.

### C. FF4_COMP is not better than trajectory-blind GENERIC_COMPLETE

If the primary 2×2 otherwise looks positive but `FF4_COMP <= GENERIC_COMPLETE` in SCREEN:

`PIVOT_GENERIC_WORKFLOW_HYGIENE_NOT_TRAJECTORY_CONDITIONED_REPAIR`

Do not claim automatic failure diagnosis is necessary.

### D. Generator, source, and interaction survive

Only if SCREEN and VALIDATION both pass the frozen rules:

`BRIDGE_PASS_ELIGIBLE_FOR_SEPARATE_E3_PROPOSAL`

This does not automatically authorize E3. A new E3 contract/review/authorization is still required.

## 14. Cost control

The compiler is zero-provider for state generation. Provider cost comes from:

- search-pool acquisition if the 96 update-task pools are not already prospectively acquired;
- two free-form updater states per stream;
- downstream actor evaluation.

SCREEN must run before VALIDATION. If SCREEN fails, all validation provider calls are avoided.

No second backbone, public benchmark, or E3 call is authorized by this protocol.

## 15. Current prototype qualification

Zero-provider unit tests required before any bridge contract can be drafted:

- successful winner -> no forced generic repair;
- incomplete failed trajectory -> COMPLETE_WORKFLOW;
- saved-but-unverified failure -> VERIFY_OUTPUT;
- unrecovered visible tool error -> RECOVER_TOOL_ERROR;
- clean recovery suppresses redundant recovery primitive;
- deterministic compilation;
- duplicate diagnoses do not inflate state;
- exact reproduction of frozen G1/G2/G3 surfaces for corresponding diagnoses;
- hidden arm/family/projection/task labels absent from compiler input API.

Current status at protocol drafting: **10/10 PASS**.

## 16. Authority boundary

This protocol grants **zero** authority for:

- provider calls;
- search-pool acquisition;
- updater execution;
- bridge actor evaluation;
- validation opening;
- E3;
- second backbone;
- public benchmark;
- paper promotion.

It is a prospective design object only. The active Recovery V3 remains the only relevant future scientific execution path under its own existing authority and quota schedule.
