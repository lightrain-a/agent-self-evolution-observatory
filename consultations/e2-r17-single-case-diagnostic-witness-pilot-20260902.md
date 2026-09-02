# E2-R17 — Single-Case Diagnostic Witness Pilot

Date: 2026-09-02
Status: **DESIGN_ONLY / ZERO EXECUTION AUTHORITY**
Scientific object: `E2-R17-SINGLE-CASE-DIAGNOSTIC-WITNESS-PILOT-20260902`

## 1. Goal

Before spending budget on a six-stream mechanism experiment or untouched E3 confirmation, first establish a clear, reproducible effect in one development case.

This pilot is intentionally not confirmatory. Its purpose is method/mechanism development:

> Can replacing the historical `first failed non-winner` with a progress-matched failed witness, and optionally pairing that witness with the successful winner as an explicit contrast, repair a stream where First-Fail MRW was neutral/slightly harmful?

The pilot must remain scientifically useful even if it fails: it separates witness-selection failure from missing-success-anchor failure.

## 2. Why a stream is the minimum valid "single case"

A literal one-task update would change the first-party SkillEvolver learning substrate from the historical eight-pool stream and would therefore confound mechanism with batch semantics.

The minimum valid case is one frozen update stream:

- eight exact K=8 pools;
- one initial skill;
- one updater invocation per arm;
- the same 18 development held-out tasks used by V2;
- fresh contemporaneous evaluation for all new arms.

Thus "single case" means **one stream**, not one isolated spreadsheet task.

## 3. Frozen development case

Use:

`e1-tsr-00`

This choice is explicitly outcome-informed and therefore development-only. It can never become E3 confirmatory evidence.

### Why this stream

Historical V2 First-Fail MRW effect:

`D = -0.0138888889`

Historical replicate differences:

`[-0.1111, -0.1667, +0.1111, +0.1111]`

Pre-treatment support:

- mixed pools: `7/8`;
- current First-Fail average absolute tool-call gap from winner: approximately `4.86`;
- progress-matched selector average gap: approximately `3.86`;
- progress-matched selector changes the selected failed rollout on `4/7` mixed pools.

This makes `e1-tsr-00` a better selector-repair case than `e1-ska-00`: the latter is more negative historically but only `1/7` mixed pools would change witness under the proposed selector, so it provides little treatment contrast for a selector experiment.

## 4. Frozen progress-matched failure selector

For every mixed K=8 pool, identify the same acting winner used by all arms.

For every failed non-winner trajectory `f`, compute only pre-treatment structural quantities:

- `n_tool(f)` = number of tool calls;
- `n_provider(f)` = number of provider calls;
- `LCP_tool(f,w)` = longest common prefix length of tool **names** with the winner trajectory `w`.

Select the failed witness lexicographically by:

1. minimize `|n_tool(f) - n_tool(w)|`;
2. then minimize `|n_provider(f) - n_provider(w)|`;
3. then maximize `LCP_tool(f,w)`;
4. then choose the lowest rollout index.

No LLM judge, learned scorer, held-out outcome, future utility, family coefficient, or manual choice enters selection.

For nonmixed pools, all arms use the acting winner exactly as historical V2 did.

## 5. Arm definitions

### A0 — WIN-C

Fresh contemporaneous matched-window acting-winner evidence.

Purpose: current strong control.

### A1 — FIRST-FAIL

Exact historical MRW semantics:

- on mixed pools: lowest-rollout-index failed non-winner;
- on nonmixed pools: same acting winner as A0.

Purpose: reproduce the current mechanism baseline contemporaneously.

### A2 — PROGRESS-FAIL

- on mixed pools: the frozen progress-matched failed witness above;
- on nonmixed pools: acting winner.

Purpose: isolate **witness selection** while keeping one selected trajectory per pool.

### A3 — PROGRESS-CONTRAST

- on mixed pools: the same progress-matched failure plus the exact acting winner;
- on nonmixed pools: acting winner only.

Purpose: test whether a failed witness needs an explicit successful reference branch to become diagnostic.

The updater-visible contrast representation must be arm-blinded apart from the evidence itself. Branch labels should be neutral (`BRANCH_A`, `BRANCH_B`); trajectory score remains visible because outcome is part of the intended learning evidence.

## 6. Exact evidence-budget parity

All four arms must expose exactly the same final re-tokenized evidence-block length for each pool.

Frozen tokenizer/runtime remain the V3.1 settings:

- tokenizer: `cl100k_base`;
- tiktoken: `0.11.0`;
- maximum final block: `3072` tokens;
- no padding.

Implement a four-way exact-matched renderer that finds the largest final token count reachable by **all four arm source representations** for the same pool.

For A3, the total visible budget remains the same as A0/A1/A2. Its paired evidence does not receive extra tokens.

Inside A3's source representation, allocate the available branch-source budget deterministically 50/50 between winner and failed witness before the outer exact-match step. Each branch uses the same frozen head/tail rule.

If exact four-way parity cannot be obtained without changing the treatment semantics, STOP before provider execution.

## 7. Frozen model and runtime

Keep the same qualified scientific stack as V2:

- model: DeepSeek V4 Pro (`deepseek-v4-pro-ga-260813` if identity qualification still binds);
- thinking: disabled;
- temperature: 0;
- provider retry: 0;
- same MindMemOS SkillEvolver commit;
- same initial skill SHA;
- same actor/evaluator runtime;
- same deterministic SpreadsheetBench verifier;
- same 18 `e1_common_heldout_probe` tasks.

Do not consume the untouched 36-task E3 held-out panel in this development pilot.

## 8. Stage S0 — zero-provider selector qualification

Before any scientific run, freeze a selector manifest for all eight pools of `e1-tsr-00` containing:

- pool ID/SHA;
- acting winner rollout;
- historical First-Fail rollout;
- progress-matched failed rollout;
- tool/provider counts;
- tool-name LCP;
- whether A1 and A2 differ.

Required gate:

- `7/8` pools mixed as expected;
- selector changes at least `4/7` mixed pools;
- all selected trajectories are content-addressed and technically complete;
- no outcome beyond the already-frozen pool success/failure label is read;
- zero new provider calls.

If this gate fails, do not run the pilot.

## 9. Stage S1 — one-replicate four-arm screen

Run exactly one fresh contemporaneous replicate of:

`A0 / A1 / A2 / A3`

State count:

`4`

Held-out measurement count:

`4 x 18 = 72`

All update order and held-out arm order must be hash-balanced with a new frozen salt.

### S1 endpoint

For each arm:

`J(A) = mean binary success across the 18 development held-out tasks`.

Define:

- `gain2 = J(A2) - J(A1)`;
- `gain3 = J(A3) - J(A1)`.

Select the candidate by:

1. larger of `gain2`, `gain3`;
2. exact tie -> choose A2 because it is the simpler intervention.

### S1 continuation gate

Proceed to S2 only if the selected candidate satisfies both:

1. candidate exceeds A1 by at least `1/18` (`+0.0556`);
2. candidate is not below fresh A0.

This is a development screen, not a significance test.

If neither candidate passes, STOP the single-case pilot and inspect only already-generated patch/evidence artifacts. Do not add another arm ad hoc.

## 10. Stage S2 — within-case replication of the selected repair

Run two additional fresh replicates for only:

- A0 WIN-C;
- A1 FIRST-FAIL;
- the S1-selected candidate.

Additional state count:

`6`

Additional held-out measurements:

`6 x 18 = 108`

Combined pilot maximum:

- learned states: `10`;
- held-out measurements: `180`.

This is about 10.4% of the V2 96-state / 1728-heldout execution scale.

## 11. Single-case success criterion

Using the three contemporaneous replicates available for A0, A1, and the selected candidate, define per-replicate 18-task success means.

Declare:

`SINGLE_CASE_MECHANISM_EFFECT_PASS`

only if all are true:

1. `mean(candidate - A1) >= 1/18`;
2. `candidate > A1` in at least `2/3` replicates;
3. `mean(candidate - A0) > 0`;
4. `candidate >= A0` in at least `2/3` replicates;
5. no technical failure, replay, treatment-budget mismatch, or selector drift occurred.

No p-value is claimed from one stream. This is a development effect demonstration only.

## 12. Interpretation matrix

### A2 beats A1, A3 does not add further value

Interpretation:

> First-Fail failed mainly because it selected a poor rejected branch; progress-matched witness selection is the repair mechanism.

Next method candidate: `PROGRESS-FAIL`.

### A3 beats A2 and A1

Interpretation:

> Failure quality matters, but an explicit successful reference is additionally required; contrastive diagnostic evidence is the repair mechanism.

Next method candidate: `PROGRESS-CONTRAST`.

### A2/A3 beat A1 but not A0

Interpretation:

> The repair removes harm from raw First-Fail but does not yet outperform winner-only learning. Do not promote the method; use patch-level diagnostics to decide whether one final development revision is justified.

### Neither A2 nor A3 beats A1

Interpretation:

> The near-miss/contrast hypothesis is not supported even in the selected repair case. Stop this mechanism route rather than scaling it.

## 13. Use of previous experiments

Historical V2 is used for:

- identifying First-Fail as heterogeneous;
- generating the post-hoc progress/diagnosticity hypothesis;
- choosing `e1-tsr-00` as a development repair case;
- fixing expected pool identities and treatment contrasts;
- preserving the original 18-task development evaluation panel.

Historical V2 outcomes are **not** counted as S1/S2 outcomes.

All A0/A1 baselines used for the pilot decision are fresh and contemporaneous with A2/A3.

The untouched E3 streams and 36-task E3 held-out panel remain sealed for later confirmation.

## 14. Current authority

This document grants zero execution authority.

Not authorized:

- provider calls;
- updater execution;
- held-out execution;
- scientific runner launch;
- second backbone;
- public benchmark;
- E3 confirmation;
- paper promotion;
- submission.

Next allowed action:

`IMPLEMENT_AND_ZERO-PROVIDER-QUALIFY_S0_SELECTOR_AND_FOUR-WAY_RENDERER`
