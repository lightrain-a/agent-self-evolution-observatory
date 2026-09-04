# E2-R17 Paper Outline — SkillZip/Pro-Inspired Iteration

Date: 2026-09-03
Status: `OUTCOME_NEUTRAL_DRAFT_STRUCTURE`

## Working title

**Decoupling Serving and Persistent Learning over Test-Time Search**

Subtitle: *Exact-Same-Pool Causal Tests of Search-Projection Censoring in Self-Evolving Agents*

Do not use a global “best to act vs best to learn” title: even a secondary-gate PASS compares WIN-C with one prospectively defined alternative and does not optimize over the full learner-projection class. Any stronger post-outcome title must remain bounded to **served-winner versus the tested alternative learner projection** on the supported controlled regime.

---

## Abstract skeleton

Self-evolving agents increasingly combine test-time search with persistent memory or skill updates. Search produces multiple candidate trajectories, but serving typically selects one winner; when persistent learning consumes that same selected trace, the serving decision also defines which already-generated evidence reaches the learner. We study this **serving-to-persistent-learning projection interface**.

We formalize a realized search object `T_K` with separate serving and learning projections `a(T_K)` and `g(T_K)`, and introduce an exact-same-pool causal design that keeps search output, served behavior, initial state, updater, budget, and update order fixed while changing only learner-visible evidence. Historical support establishes that winner-coupled learning can omit evidence that exists in the search pool; a completed global rejected-witness comparison does not establish a reliable universal benefit, motivating a prospectively frozen structural moderator test.

[Populate after V3 only:] report the five-skeleton interaction result. Unlock the stronger act/learn-divergence sentence only if the frozen procedural simple-effect gate passes. Report natural transport only if separately authorized and completed.

---

# 1 Introduction

### P1 — System practice

Self-evolving agents increasingly combine two mechanisms: test-time search for stronger current behavior and persistent updates for stronger future behavior. Search generates several trajectories; the system serves one and later converts observed experience into reusable memory/skill.

### P2 — Hidden interface mismatch

The literature asks how to learn from successes, failures, or multiple trajectories. A prior interface is less examined: after a rich search object has already been generated, **which projection crosses from serving into persistent learning?** A winner selected for current execution may also become the only trajectory the learner sees.

### P3 — Why one metric / one extreme is insufficient

Winner-only serving can censor alternatives already present in the pool, but this does not prove those alternatives are useful. Conversely, the completed universal-MRW study did not establish a reliable global rejected-witness benefit. Therefore neither “learn from the winner” nor “always learn from a failure” is a sufficient universal rule.

### P4 — Scientific object

Define:

```text
T_K -> a(T_K) -> served current behavior
T_K -> g(T_K) -> persistent updater -> future frozen skill
```

The central question is whether `g` can be causally manipulated independently of `a`.

### P5 — Identification and prospective hypothesis

Introduce exact-same-pool, acting-fixed intervention. Then state the prospectively frozen V3 structural hypothesis: the projection effect should be larger in reusable procedural-transformation cells than in instance-binding/localization cells.

### P6 — Evidence/claim ladder

Outcome-neutral before execution:

1. availability/censoring is measurable;
2. global universal-MRW benefit is not established;
3. V3 tests structural effect modification prospectively;
4. a separate predeclared procedural simple-effect gate controls whether the stronger act/learn-divergence thesis is unlocked;
5. one natural transport experiment is the only planned claim expansion if needed.

### Contributions — only use claims actually supported at submission

1. **Causal interface identification:** exact same realized search object and served behavior are held fixed while learner-visible projection is changed.
2. **Search-projection evidence:** quantify the serving-induced observation boundary and separate evidence availability from learning consequence.
3. **Prospective structural effect modification:** include only if V3 primary gate passes. Add controlled act/learn divergence only if the secondary procedural gate passes.

---

# 2 Related Work

## 2.1 Self-evolving agents and persistent skills/memory

Position ReasoningBank/MaTTS, SkillCAT, SkillRevise, Rethinking Self-Evolving Agent Skills, WikiSkill, SkillOpt and related work as different ways to acquire/use experience.

Key boundary:

> These works mainly study what experience to summarize, contrast, store, or update from. E2-R17 isolates an earlier systems interface: how the serving decision over an already-realized search object determines the learner-visible projection.

## 2.2 Test-time search and experience reuse

Acknowledge search distillation/recycling work explicitly. Do not claim that search generally hurts learning.

## 2.3 Logging, replay, selection, and curation analogy

Concede the reduction: `g(T_K)` resembles a replay/logging/data-selection policy. Then explain the irreducible empirical contribution: exact same realized pool + served behavior fixed + prospective effect modification.

## 2.4 Related-work comparison table

Columns:

- multi-trajectory object generated;
- persistent object updated;
- learner-visible experience controlled;
- served behavior held fixed;
- exact realized pool held fixed;
- causal projection intervention;
- prospective moderator.

E2-R17 last.

---

# 3 Problem Formulation

## 3.1 Realized search object

Define `T_K` as the exact realized candidate set/pool generated from frozen state `S0` under frozen actor/search conditions.

## 3.2 Serving projection

`a(T_K)` selects the trajectory used for current action/response. In the controlled experiments this is the verifier-selected winner and is identical across learning arms.

## 3.3 Persistent-learning projection

`g(T_K)` specifies what evidence enters the persistent updater.

Primary controlled projections:

- `g_WIN`: winner evidence;
- `g_MRW4`: frozen rejected-witness replacement on designated mixed pools, winner otherwise.

## 3.4 Four system layers

Distinguish:

1. generated evidence;
2. served evidence/current acting utility;
3. learner-visible evidence;
4. future frozen-skill utility.

State explicitly: improvement at layer 2 does not logically imply improvement at layer 4.

## 3.5 Search-projection censoring

Define observable evidence availability loss without defining “censored” by downstream usefulness.

---

# 4 Causal Identification

## 4.1 Exact-same-pool intervention

Hold fixed:

- initial `S0`;
- exact realized `T_K`;
- verifier;
- served winner `a(T_K)`;
- updater implementation/config;
- token/evidence budget;
- update task order;
- downstream heldout evaluation.

Change only `g(T_K)`.

## 4.2 Estimands

For stream `s`:

`D_s = mean_r[J_s,r(MRW4) - J_s,r(WIN-C)]`.

For skeleton `h`, cell `z`:

`D_h,z = mean_{s in (h,z)} D_s`.

Primary interaction:

`I_h = D_h,PROCEDURAL - D_h,BINDING`.

## 4.3 Primary V3 gate

Five independent skeletons; all five `I_h > 0`; exact one-sided sign resolution `1/32`.

`R=4` is measurement replication only.

## 4.4 Secondary controlled-divergence gate

Evaluate only after primary gate:

`D_h,PROCEDURAL > 0` for all five frozen skeletons.

PASS unlocks only the controlled-suite divergence statement. FAIL does not alter primary interaction PASS but keeps the memorable thesis/title locked.

---

# 5 Prospective Structural Hypothesis

## 5.1 Procedural transformation

Define operationally; do not claim a universal semantic category.

## 5.2 Instance binding/localization

Define operationally; same boundary.

## 5.3 Crossed matched skeletons

Explain byte-identical paired initial workbooks, nuisance control, same search/acting, and separate learning projections.

## 5.4 Router is downstream

The hand-engineered observable router is proof-of-implementability only. It does not define the mechanism and cannot rescue a failed interaction.

---

# 6 Experiments

## 6.1 Experimental setup

Describe controlled suite, DeepSeek actor/updater identity only after actual execution; exact provider/runtime details in appendix/reproducibility.

Use scientific units, not provider-call counts, to organize the main text.

## RQ1 — Does serving create a measurable learning-observation boundary?

Report censoring/support metrics and applicable theory prediction. No method-effect language.

## RQ2 — Does learner projection causally matter?

Report the completed global exact-same-pool DeepSeek study prominently:

- WIN-C ≈ 79.05%;
- universal MRW ≈ 81.37%;
- +2.3148 pp;
- CI crosses zero;
- `p=0.171875`;
- global benefit not established.

Interpretation: motivates a fresh moderator hypothesis; does not itself prove heterogeneity.

## RQ3 — Is the projection effect prospectively structure-dependent?

Main V3 table: one row per skeleton.

Columns:

| Skeleton | `D_PROC` | `D_BIND` | `I_h` | primary sign |

Do not aggregate away the five units.

## RQ4 — Is there a controlled region of true act/learn divergence?

Report the secondary 5/5 procedural simple-effect gate separately from the interaction.

If FAIL, say so plainly. No cherry-picked positive cell.

## RQ5 — Does it transport to a natural/out-of-family setting?

Only after separate authorization. One natural transport experiment; ordinary pre-update observables; same pool and acting fixed; positive future-skill simple effect is primary endpoint.

Hard stop if negative/non-supportive.

## 6.x Policy consequence

Only after RQ3 PASS:

- always WIN-C;
- universal MRW4;
- difficulty-only;
- mixedness-only;
- frozen observable router.

This is not allowed to rescue mechanism failure.

## 6.x Public method-baseline table — only after controlled GO

Use one common public substrate rather than a benchmark zoo: **SpreadsheetBench Verified-400**.

Keep two evaluation lanes separate.

### Unified common-harness lane — main quantitative table

Freeze one public split, actor/updater roles, tool harness, turn budget, evaluator, and accounting policy, then rerun:

- No Skill;
- Initial / Parent Skill;
- WIN-C;
- universal MRW4;
- RethinkSkill Success-only;
- RethinkSkill Fail-only;
- RethinkSkill Normal (success + failure);
- SkillOpt;
- Trace2Skill if a pinned official implementation is usable, otherwise a clearly labelled SkillCAT-style same-task success/failure contrast reconstruction;
- E2-R17 frozen projection policy only if its method/policy authority has been prospectively earned.

Only this common-harness lane supports direct row-to-row ranking.

### Source-faithful lane — appendix / fidelity check

Where first-party code exists, also rerun the released protocol/split. These results verify implementation fidelity but must not be directly ranked against common-harness rows evaluated on a different split.

Never copy published scores into the main table. Never call a paper-spec reconstruction an exact reproduction.

### Optional baseline controls

- ReasoningBank-style same-pool aggregation: projection-level comparator, explicitly labelled as an adaptation rather than official ReasoningBank;
- Parallel Sampling / Sequential Refinement: acting-compute controls;
- full SkillCAT pipeline only if a stable first-party implementation can be pinned;
- Branch2Skill-style reconstruction only as optional extended comparison if no official code exists.

The baseline budget must not be opened to rescue a failed V3 mechanism result.

---

# 7 Theory and Predictions

## 7.1 What not to oversell

Two projections existing is not the theorem. Winner-only dropping nonwinners is not enough for novelty.

## 7.2 Availability prediction

Where valid, emphasize a falsifiable rescueable/intermediate-regime prediction for censoring mass.

## 7.3 Value/moderator prediction

Explain why reusable-transformation evidence is hypothesized to have higher cross-instance update value than instance-local binding evidence.

Tie the theory directly to V3's direction before results.

---

# 8 Discussion

## 8.1 What is causally identified

Projection effect under exact pool/acting invariance and frozen updater/environment.

## 8.2 What is not identified

- failure-specific unique value;
- globally optimal projection;
- universal procedural/binding law;
- natural-task generality unless transport passes;
- cross-model generality unless later tested.

## 8.3 Why the global MRW result matters

It prevents the paper from becoming a simplistic failure-learning method paper.

## 8.4 If V3 fails

Do not rescue. Standalone E2-R17 strong thesis stops; merge the interface/negative evidence into the broader self-evolution program if appropriate.

---

# 9 Main figures and tables

## Figure 1

Scientific object: `T_K` splits into `a` and `g`; intervention holds `T_K`/`a` fixed and changes `g`.

## Figure 2

Four layers: generated → served/current → learner-visible → future skill. “One metric is not enough.”

## Figure 3

Five-skeleton crossed V3 design and two separate gates: interaction and controlled divergence.

## Table 1

Related-work scientific-object matrix.

## Table 2

Current acting and future learning read together; causal invariance columns shown explicitly.

## Table 3

Five skeleton effects; no hidden averaging.

---

# 10 Execution roadmap and baseline plan

The current paper-level roadmap is frozen in:

- `consultations/e2-r17-experiment-plan-v4-20260904.md`;
- `generated/e2-r17-experiment-plan-v4-20260904.json`.

Key sequencing:

1. execute the already-reviewed V3 controlled causal core without redesign;
2. evaluate the primary five-skeleton interaction gate;
3. separately evaluate the frozen secondary 5/5 procedural controlled-divergence claim gate;
4. only after primary V3 PASS, freeze and independently review one SpreadsheetBench Verified-400 public lane;
5. use that same public lane simultaneously for natural transport and a unified closest-method baseline table;
6. primary unified rerun baselines: No Skill, Parent Skill, WIN-C, Universal MRW4 or a prospectively frozen public-compatible alternative, RethinkSkill Normal/Success-only/Fail-only, SkillOpt, and at least one credible trajectory-to-skill/contrastive baseline; include the E2 policy only if its public policy gate passes;
7. use one common qualified primary model/harness first; a second model is robustness only after the main public table is frozen.

The public lane must use one frozen split and common evaluator/harness for direct ranking. Source-faithful baseline reproductions with different original splits/models belong in an appendix fidelity lane and are not directly ranked against unified-rerun results.

# Appendix priorities

- exact Stage-A/Stage-B governance and SHA-bound execution receipts;
- exact-once provider-acquisition logic;
- matched-window renderer and token-budget audit;
- full task/skeleton construction;
- all ten cell effects and all replicate-level measurement details;
- router implementation and policy baselines;
- failure registry / implementation incidents only where useful for reproducibility.
