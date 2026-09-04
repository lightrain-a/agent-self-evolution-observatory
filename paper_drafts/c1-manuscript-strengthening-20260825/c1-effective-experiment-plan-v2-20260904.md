# C1 effective experiment plan V2 — minimum sufficient evidence, not workload accumulation

Date: 2026-09-04  
Status: **FROZEN DESIGN PROGRAM / NO NEW SCIENTIFIC OUTCOME**  
Supersedes: `c1-post-oracle-experiment-plan-20260904.md` as the active experiment-priority plan  
Parent-plan SHA256: `f541a21a5421d4858d1bb1a77c954d092350f1de0ddc949a77417f0357a9a684`  
Independent Oracle-review summary SHA256: `7c650f1167bf4a4be0beeec5c30a82d2efca5f73936fb3d80bed1e7424672053`  
Paper archetype: **measurement / identification**  
PACTA-MSR status: **optional successor hypothesis; not required for current-paper closure**

## 0. Design principle learned from strong systems/method papers

Do **not** copy the absolute workload of SkillZip / SkillZip Pro. Copy the useful experimental logic:

1. every experiment must answer one named research question or reviewer objection;
2. every baseline must instantiate a concrete alternative explanation, not merely add another method name;
3. every ablation must remove one load-bearing component/measurement boundary;
4. every new scientific call must have a result-dependent decision that changes the paper;
5. use prospective calibration to choose the smallest sample size that can answer the question;
6. do not broaden models/domains until the current claim actually requires that generality.

A proposed experiment is admitted only if all four gates pass:

- **Claim link:** which current claim/objection does it test?
- **Decision differential:** would a positive and a negative result lead to different manuscript/adjudication decisions?
- **Matched estimand:** does the control measure the same object under a single changed factor?
- **Minimum sufficient cost:** is this the cheapest design that preserves identifiability and useful precision?

If any gate fails, do not run the experiment.

---

# Track A — current C1 measurement paper

## A0. Freeze completed evidence — no rerun

Retain the current completed scientific object:

- Shopping paired write divergence: 20/20;
- combined Shopping+Reddit write lineage: 24/24;
- stronger same-mode wording control: between-minus-within `0.104978`, exact one-sided sign-flip `p=0.007812`;
- forced fixed-evidence terminal leverage: `|Delta|=0.15625`, `p=0.00074`;
- native Shopping source-item exposure: `125/172`;
- frozen Shopping first-action contrast: TV `0.06944`, `p=0.5801`, `0/36` modal branch-action changes;
- native Shopping terminal: `|S-F|=0.02083`, `p=0.4289`, `34/36` zero;
- Reddit write 4/4 divergent; native terminal `|S-F|=0.125`, `p=0.2253`, `6/8` zero with opposite signs in the two nonzero cells;
- existing structural sensitivity audit.

No replacement, top-up, outcome relabeling, scalar transport efficiency, or causal-mediation reinterpretation.

The current strongest claim remains operational:

> On the frozen C1 system, durable branch-conditioned state divergence and substantial source-item exposure do not by themselves establish a stable branch-conditioned first-action distribution shift.

Do not claim direct observation of latent relevance or latent behavioral authority.

---

## A1. Formal baseline package from existing evidence — zero new provider calls

### A1.1 Evaluation-surface baselines

The relevant baselines for a measurement paper are coarsened evaluators applied to the same frozen system:

| Baseline evaluator | Observable | Apparent conclusion | Alternative it cannot distinguish |
|---|---|---|---|
| Write-only | `W` | persistent update is strong | downstream use unknown |
| Retrieval-only | `E` | reuse is active | availability vs policy uptake |
| Native endpoint-only | `O` | effect is almost absent | writer/retrieval/uptake failure are aliased |
| Forced-only | `F` | memory has downstream leverage | native retrieval/transport bypassed |
| **Stage-resolved C1** | `W,E,U,O` + side `F` | identifies the first unsupported measured native stage | preserves stage identity |

This is the primary baseline table. It tests the paper's core evaluation-coarsening claim directly.

### A1.2 Existing control baselines mapped to alternatives

- **Same-mode wording control at W:** tests generic prompt-wording sensitivity.
- **Forced fixed-evidence at F:** tests global downstream insensitivity under supplied memory.
- **Outcome-blind structured-memory control:** tests whether generic structured prompting alone explains the forced effect; retain with its existing interpretation and practical-floor boundary.
- **Structural stage ablation:** existing evidence shows that dropping terminal outcome, Reddit, or forced capacity does not move the Shopping first-unsupported stage, while merging exposure with uptake destroys the diagnostic distinction.

Do not add SAMem/MemArbiter/AWM/ExpeL as algorithm rankings to Track A: they optimize a different object and would turn a measurement paper into an incoherent method leaderboard.

**Decision:** A1 is mandatory and zero-call. It should appear as one main-table baseline package plus one structural-ablation panel.

---

# A2. One mandatory high-information experiment: first-action same-condition stochasticity audit

This is the only new scientific experiment admitted by default in V2.

## A2.0 Zero-provider provenance/replay qualification — mandatory before any new call

Current claim-audit provenance binds the first-action statistic to a summarized stage artifact. Before new execution, recover and content-address the exact raw support needed to replay the historical first-action result:

1. exact 36 frozen Shopping matched branch-comparison state IDs;
2. exact branch-specific memory/context rendered to the policy for every state;
3. exact policy model/snapshot and sampling configuration;
4. raw first-action responses used by the historical statistic;
5. deterministic first-structured-action parser/normalizer;
6. exact analysis code and randomization/permutation seed.

Zero-provider replay must reproduce, under the frozen historical analysis semantics:

- mean first-action TV `0.06944`;
- `p=0.5801`;
- `0/36` modal branch-action changes.

If byte/content-addressed raw support is insufficient, or replay does not reproduce these values, **STOP before new scientific calls**. Repair provenance/analysis transparency first. Do not cover an unreplayable historical result with a new experiment.

## A2.1 Freeze the new estimand before provider execution

Scientific unit: the same frozen Shopping matched branch-comparison **state**, not an individual model call.

For state `i`, draw fresh independent first actions from the success-writer and failure-writer conditions under identical state/context/model/sampling configuration:

`S_i = {S_i1,...,S_in}` and `F_i = {F_i1,...,F_in}`.

Primary action identity uses the replay-qualified existing normalized first-structured-action representation. Before execution, audit the normalizer for deterministic replay and verify that it does not use branch/outcome labels.

Primary per-state statistic is the unbiased exact-match-kernel MMD2 / collision U-statistic:

`U_i = MMD_u^2(S_i, F_i)` with `k(a,b)=1[a==b]`.

Why this is the right new statistic:

- within-condition collisions estimate stochastic variability directly;
- between-condition collisions estimate branch separation;
- unlike plug-in empirical TV at small `n`, the U-statistic has a clean zero expectation under identical action distributions;
- finite-sample negative values are legal and must not be clipped;
- it answers the missing question: does branch-conditioned action separation exceed same-condition stochasticity?

Historical TV remains the original frozen result and is reported alongside this audit; it is not retroactively replaced.

## A2.2 Sample-size calibration — zero scientific outcome

Do **not** copy PACTA's `6+6` or SkillZip Pro's workload mechanically.

Before any new first-action draw:

1. use the replay-qualified historical action support plus synthetic null/alternative stress distributions;
2. evaluate candidate draws per branch `n in {2,4,6,8}`;
3. simulate the frozen state-stratified randomization test and estimator variance;
4. publish the operating-characteristic curves;
5. freeze the **smallest n** that gives acceptable false-positive control and useful sensitivity for a decision-changing action-distribution contrast under the stress family.

The calibration artifact must specify its sensitivity target before the new outcomes are generated. It may use the already-public historical C1 effect scale for design, but it may not inspect new A2 outcomes or adapt `n` after unblinding.

If no candidate up to `n=8` gives useful sensitivity, STOP and reconsider the endpoint rather than automatically spending more calls.

Expected call envelope after calibration:

`36 states x 2 branches x n` = `144 / 288 / 432 / 576` first-action calls for `n=2/4/6/8` respectively.

No terminal rollout is required: stop immediately after the normalized first structured action, because the scientific question is U-stage stochasticity.

## A2.3 Inference

Primary global null:

> Within each frozen state, success/failure branch labels do not change the normalized first-action distribution beyond same-condition stochasticity.

Use a prospectively frozen state-stratified branch-label randomization/permutation test on the mean `U_i`; repeated model calls are measurements nested within each state, not scientific units.

Report:

- all 36 `U_i` values;
- mean and median `U_i`;
- positive/negative finite-sample counts;
- fixed-state bootstrap interval for the mean as descriptive panel uncertainty;
- randomization-test p-value;
- raw normalized-action frequency tables for auditability.

Do not claim population generalization from the 36-state panel.

## A2.4 Falsification-capable decision rule

This experiment must be allowed to change the paper in either direction.

### Outcome A — branch sensitivity exceeds same-condition stochasticity

If the frozen test supports a positive branch-distribution contrast:

- revise the stage signature: first-action branch sensitivity is now supported under replicated stochasticity control;
- do **not** retain the old strong wording that the evidence boundary is strictly pre-action;
- the remaining attenuation question moves toward later policy/terminal integration;
- PACTA-MSR is still not automatically validated.

### Outcome B — branch sensitivity is not supported beyond same-condition stochasticity

If the frozen test does not support a branch-distribution contrast:

- retain first-action uptake as the first unsupported measured native stage;
- strengthen the interpretation only to “not established above same-condition stochastic variation on this frozen panel”;
- do not make an equivalence/zero-effect claim unless a separately preregistered equivalence margin is justified and excluded.

### Outcome C — severe state heterogeneity

If the aggregate is weak but a preregistered heterogeneity audit reveals clear reproducible state subgroups:

- report heterogeneity descriptively;
- do not select positive states post hoc as a new primary cohort;
- any subgroup mechanism becomes a new prospective experiment, not a rescue of A2.

**Decision:** A2 is mandatory because it closes a named current limitation and is falsification-capable. It is not a workload-expansion experiment.

---

# A3. Cross-domain full-chain replication — conditional, not automatic

Do **not** immediately add a third benchmark.

First run a zero-provider feasibility audit asking whether the existing Reddit substrate can support the missing native `E` and `U` instrumentation under the same scientific semantics as Shopping.

### Trigger to execute Reddit E/U completion

Execute only if, after A2 and the next independent submission review, **cross-domain replication of the stage boundary is a verdict-changing remaining objection**.

If triggered:

1. freeze the existing Reddit paired writes; no source re-selection;
2. add source-item exposure measurement `E` on held-out native opportunities;
3. add first-action replicated stochasticity measurement `U` using the same normalized-action/MMD2 framework as A2;
4. retain the existing terminal `O` evidence;
5. analyze `W -> E -> U -> O` without forcing Shopping's stage verdict onto Reddit.

If Reddit cannot support matched E/U instrumentation without changing the substrate, stop this extension rather than inventing a third domain merely to increase benchmark count.

A new third domain is authorized only by a separate claim-expansion decision after Reddit feasibility is exhausted.

---

# A4. Second backbone/model — explicitly not default

Do not add another executor merely for breadth.

A second model becomes justified only if an independent reviewer says the current paper's central measurement conclusion is blocked specifically by model/configuration specificity **after A2**.

If triggered, use exactly one additional frozen executor on the same already-frozen state panel and measurement surfaces. Do not change writer, task pool, retrieval, or action canonicalization simultaneously.

Purpose: portability of the measurement signature, not a new model leaderboard.

---

# A5. Figure / claim / submission gate

After A1 and A2:

1. build Figure 1 as an evidence-status stage diagram;
2. place forced capacity on a side bypass, not in the native chain;
3. show the A2 stochasticity audit at the first-action stage;
4. keep PACTA-MSR in a small dashed prospective box only;
5. run machine claim/evidence audit;
6. run a fresh independent submission-level review.

The submission reviewer determines whether A3 is actually needed. Do not pre-commit to A3/A4 for workload appearance.

---

# Track B — PACTA-MSR successor, independent of current-paper closure

PACTA-MSR remains optional and does not block Track A.

## B0. Only open if we deliberately want a method-expansion paper/result

Question:

> Does a selector based on stable matched-state branch sensitivity produce stronger decision-level branch transport than an equally sparse outcome-blind random authorization rule?

This is not a task-accuracy/reward claim.

## B1. Required causal baselines if opened

- `A0`: native raw branch memory;
- `A1`: existing state-conditioned binding / SCB always;
- `A2`: rate-matched random authorization;
- `A3`: PACTA-MSR selective authorization.

These four are mandatory because each removes one concrete alternative explanation. They are more important than adding many external methods.

## B2. External algorithmic baselines only after a genuine P0 PASS

If P0 passes and we want a method paper/claim expansion, add at most:

1. one strong decision-time memory arbitration baseline (MemArbiter-like if reproducible and fairly matchable);
2. optionally one state-aware relevance/retrieval baseline (SAMem-like) if it isolates a distinct comparator not already represented by A1.

Do not run a broad memory-method zoo before P0 establishes that the proposed selector itself has an effect.

## B3. Preserve the existing post-Oracle statistical repairs

Before any new PACTA scientific pool:

- deterministic outcome-blind canonical action identity;
- shadow/final sample independence;
- nondegenerate `2 <= K <= 6`;
- scientific-unit inference over source/future units;
- recalibrated combined MMD2/sign-flip gate;
- Q0.9 long-horizon provider qualification before consuming another fresh pool.

Fresh4 remains permanently retired and is not a negative PACTA method result.

---

# Final experiment priority and stop conditions

## Mandatory now

**M0 — provenance replay:** recover/replay the 36-state historical first-action result. Zero provider calls.  
**M1 — evaluation baselines:** write-only / retrieval-only / endpoint-only / forced-only / stage-resolved + existing controls. Zero calls.  
**M2 — same-condition first-action stochasticity audit:** only after M0 and zero-provider sample-size calibration. New calls only to first action.  
**M3 — Figure/claim audit + independent submission review.** Zero scientific calls.

## Conditional only

**C1 — complete Reddit E/U:** only if submission reviewer identifies cross-domain stage-boundary replication as verdict-changing.  
**C2 — one second executor:** only if model specificity is verdict-changing after M2.  
**C3 — PACTA-MSR successor:** only as a deliberate method-expansion project, never as rescue for the measurement paper.

## Explicitly rejected workload inflation

Do not automatically run:

- three or more models because SkillZip Pro did;
- three or more benchmarks because another systems paper did;
- a long list of memory algorithms with mismatched estimands;
- terminal rollouts for a question that stops at first action;
- new domains before exhausting the existing Reddit replication substrate;
- PACTA final experiments before provider/statistical qualification;
- post-hoc subgroup selection or sample-size top-up after effect inspection.

The criterion for “enough experiments” is not table size. It is whether the remaining credible alternative explanations to the paper's **actual claim** have a matched, falsifiable, efficiently powered test.
