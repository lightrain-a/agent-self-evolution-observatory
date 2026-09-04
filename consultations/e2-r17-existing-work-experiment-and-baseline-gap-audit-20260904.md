# E2-R17 Existing-Work Experiment & Baseline Gap Audit

Date: 2026-09-04
Status: `ZERO_PROVIDER_DESIGN_AUDIT_ONLY`
Frozen R2 scientific object remains unchanged.

## 1. Question

Does E2-R17 have enough experimental work relative to current self-evolving-agent / skill-learning papers, and is its baseline comparison surface sufficient?

## 2. Existing-work experimental patterns

### ReasoningBank / MaTTS (ICLR 2026)

Experimental shape:

- three public benchmark families: WebArena, Mind2Web, SWE-Bench-Verified;
- multiple backbone LLMs;
- external baselines including No Memory, Synapse, AWM;
- scaling controls: MaTTS without memory, without aggregation, parallel/sequential scaling at multiple `k`;
- efficiency (steps), generalization, ablation and case studies.

Lesson for E2: a causal/interface paper still needs a clearly recognizable external comparison lane; internal ablations alone do not replace method baselines.

### SkillCAT (2026)

Experimental shape:

- SpreadsheetBench-Verified with disjoint evolution/test split;
- full SpreadsheetBench Soft/Hard metrics;
- WikiTableQuestions OOD transfer;
- DocVQA multimodal transfer;
- matched Qwen author/user models plus cross-model Gemma/GPT users;
- baselines: No Skill, Human-Written, Parametric, Trace2Skill variants;
- component ablations for contrastive extraction, validation, and topology routing.

Lesson for E2: SpreadsheetBench is already a recognized common comparison substrate for persistent external skills. Closest-method comparison should occur there rather than adding unrelated benchmarks merely for breadth.

### SkillOpt (2026)

Experimental shape:

- six benchmarks;
- seven target models;
- three execution harnesses (direct chat, Codex, Claude Code);
- 52 model/benchmark/harness cells;
- baselines including human skill, one-shot LLM, Trace2Skill, TextGrad, GEPA, EvoSkill;
- transfer across model scales, harnesses, and a nearby benchmark.

Lesson for E2: this is a method paper and therefore needs broad horizontal ranking. E2 should not imitate this full matrix unless it becomes a method/policy paper.

### Rethinking Self-Evolving Agent Skills / RethinkSkill (2026)

Experimental shape:

- five primary benchmarks;
- three primary models;
- 42 matched feedback runs over 14 supported model-benchmark settings;
- 388 evaluated candidates;
- Parent, Normal (success+failure), Fail-only, Success-only;
- test-time parallel sampling / sequential refinement controls;
- released test, repeated evaluation, robustness and transfer;
- broader SearchQA analysis over eight models.

Lesson for E2: RethinkSkill is the strongest source-faithful feedback-composition baseline because it has official code, includes DeepSeek V4-Pro, and uses SpreadsheetBench.

### Branch2Skill (2026)

Experimental shape:

- six benchmarks spanning reasoning, spreadsheet, document, math and embodied tasks;
- several target models;
- strong comparison to SkillOpt;
- explicit evolution-token efficiency accounting;
- reasoning-tree ablations.

Lesson for E2: Branch2Skill is close conceptually because it extracts learning evidence from multiple branches, but it changes search generation and currently lacks a stable source-faithful code lane. It is Related Work / optional paper-spec reconstruction, not a mandatory quantitative main-table baseline.

### SkillZip (Xiaofan Bai et al., 2026)

Experimental shape:

- three procedural benchmarks: BFCL-V4, LiveMathematicianBench, SpreadsheetBench;
- three agent backbones (nine model-benchmark cells);
- uncompressed evolved-skill reference and SkillReducer baseline;
- compression/fidelity, cost, cross-model transfer, continual Zip-on-Write evolution.

Lesson for E2: strong work does not need dozens of baselines if the scientific object is sharply defined, but each major claim must have a corresponding evaluation axis.

### SkillZip Pro (2026)

Experimental shape is narrower but systems-deep:

- production multi-round harness and multi-entry bundle tests;
- storage/per-run/routing metrics rather than one aggregate ratio;
- protected vs unsafe/unprotected variants expose the exact failure mode.

Lesson for E2: causal depth can substitute for benchmark breadth only if the paper also shows the effect survives at least one realistic external setting.

## 3. Where E2-R17 currently stands

### Controlled scientific work — SUFFICIENT

Completed or frozen volume is already substantial:

- historical support: 96 exact K=8 pools / 768 rollout references;
- closed global exact-same-pool causal study: 12 streams / 48 paired replicates / 96 learned states / 1728 heldout units;
- V3/R2: 5 matched skeletons, 20 streams, 160 update tasks, 1280 actor rollouts;
- planned Stage B after support/authorization: 80 paired stream-replicate units, 160 learned states, 3200 heldout evaluations.

This is not under-sized in compute or repeated measurement.

### Independent mechanism breadth — MINIMAL BUT DEFENSIBLE

The confirmatory mechanism sample is five independent skeleton interactions. The 20 streams, 80 paired replicates and 3200 heldout evaluations are not independent semantic/mechanism units.

Five is enough for the frozen bounded finite-suite claim but is the low end. Adding more synthetic skeletons after this pre-outcome freeze is lower-value than external transport and risks expanding researcher degrees of freedom.

### Public/natural externality — MISSING

The controlled suite remains author-constructed. A single public natural transport is the highest-value missing evidence type.

SpreadsheetBench Verified-400 is the preferred anchor because:

- it is an official expert-annotated 400-instance public subset;
- SkillCAT, SkillOpt and RethinkSkill all have SpreadsheetBench lanes;
- local data/evaluator assets are already pinned;
- it is much more useful for fair baseline comparison than opening several unrelated benchmarks.

### Method-level baseline comparison — CURRENTLY INSUFFICIENT

Current V3 comparisons:

- WIN-C;
- MRW4;
- difficulty-only routing;
- mixedness-only routing;
- frozen observable router if mechanism passes.

These are strong **causal controls and reduction baselines**, but not enough as the only baseline surface for a standalone paper. There are no completed E2-R17 result artifacts for SkillOpt, RethinkSkill, Trace2Skill/SkillCAT, or other closest external methods.

## 4. Two baseline tables, not one mixed table

### Table A — Controlled causal/mechanism table

Purpose: identify the serving-to-learning projection effect, not rank whole self-evolution systems.

Rows already compatible with the frozen scientific object:

1. WIN-C — served winner is learner-visible evidence;
2. MRW4 — same acting/search, alternative rejected-witness projection;
3. Difficulty-only router — same learned states, simple observable reduction;
4. Mixedness-only router — same learned states, simple availability reduction;
5. Frozen observable router — only if the separate method gate passes.

Do not add new Stage-B treatment arms before the current frozen V3 outcome.

Post-V3 diagnostic controls such as duplicated winner, random nonwinner, successful-nonwinner or full-pool aggregation should be added only if the corresponding failure-specific / generic-alternative claim is pursued.

### Table B — Public realistic method-comparison table

Run only after controlled GO and after a new outcome-blind public contract is frozen.

Preferred public substrate: SpreadsheetBench Verified-400.

Preferred common executor/updater anchor: DeepSeek V4-Pro first, because it is already the E2 strong model and a primary RethinkSkill model.

#### Mandatory common-harness rows

1. No Skill;
2. Initial / Parent Skill;
3. Winner-coupled evolution (WIN-C);
4. Universal MRW4;
5. RethinkSkill Success-only;
6. RethinkSkill Fail-only;
7. RethinkSkill Normal (success + failure);
8. SkillOpt;
9. one closest trajectory-distillation baseline: Trace2Skill if the official implementation can be pinned, otherwise a clearly labelled SkillCAT-style success/failure contrast reconstruction;
10. E2-R17 frozen projection policy, only if its policy/method authority has been earned prospectively.

#### Optional rows

- SkillCAT full pipeline if a stable first-party implementation is available and can be pinned;
- ReasoningBank-style same-pool aggregation as a projection-level comparator, clearly labelled as an adaptation rather than official ReasoningBank;
- test-time Parallel Sampling / Sequential Refinement as acting-compute controls;
- Branch2Skill-style reconstruction only if code is unavailable and the paper explicitly labels it non-source-faithful.

## 5. Fair comparison policy

Do not copy published scores into the E2 main table. Current papers use different splits/harnesses:

- SkillCAT uses a 200 evolution / 200 held-out Verified split;
- SkillOpt releases an 80 / 40 / 280 SpreadsheetBench Verified split;
- RethinkSkill uses its own matched validation/test protocol.

Therefore use two lanes:

### Unified rerun lane — main quantitative table

Freeze one E2 public split, actor, updater role, turn budget, tool harness, evaluator and compute/accounting policy, then rerun all implementable baselines under that same contract. Only this lane supports direct row-to-row ranking.

### Source-faithful lane — appendix / implementation validation

For methods with official code, also reproduce the released protocol/split where feasible. These results verify implementation fidelity but must not be directly ranked against rows evaluated on a different split.

Every reconstruction must be labelled precisely (`SkillCAT-style`, `ReasoningBank-style`, `Branch2Skill-style`) and never called an exact reproduction.

## 6. How much breadth is enough for E2-R17?

E2 is a causal systems/interface paper, not a broad method-optimization paper. Therefore the minimum strong package is:

1. existing controlled support/censoring evidence;
2. completed global same-pool causal study;
3. V3 five-skeleton primary interaction;
4. secondary controlled-divergence gate;
5. one public natural SpreadsheetBench Verified transport;
6. one common-harness public baseline table with No/Parent + RethinkSkill views + SkillOpt + one trajectory-distillation/contrast baseline + E2 policy;
7. optional second model family as robustness, not as a rescue.

This is enough experimental breadth if the causal gates are positive. A five-benchmark or seven-model expansion is not required unless the paper is reframed as a general method/policy paper.

## 7. Priority order

### Before V3 outcomes

- do not alter R2;
- do not launch public baselines;
- prepare source-faithful baseline adapters and qualification tests only.

### After V3 primary GO

- freeze one public SpreadsheetBench Verified contract;
- **merge RQ5 natural transport and the method-baseline main table into this same public lane** rather than opening two separate experimental campaigns;
- qualify RethinkSkill, SkillOpt and Trace2Skill/SkillCAT-style adapters;
- run unified no-skill/parent and external baselines on the same frozen IDs/harness;
- include the E2 policy only if the policy gate is prospectively valid.

If no E2 public split has already been content-addressed and frozen, prefer an externally released reproducible split rather than inventing one after controlled outcomes; SkillOpt currently releases an 80/40/280 train/validation/test split for SpreadsheetBench Verified-400. The final split choice must be made outcome-blind and must not be changed after any public result is seen.

### After controlled-divergence GO

- the memorable act/learn-divergence thesis is available on the controlled suite;
- the public transport + baseline table becomes external validation/strengthening rather than rescue.

### If V3 FAILS

- do not spend the baseline budget to rescue E2-R17 as a standalone paper.

## 8. Source registry used for this audit

- ReasoningBank / MaTTS, ICLR 2026, OpenReview / Google Research.
- SkillCAT, arXiv:2606.13317.
- SkillOpt, arXiv:2605.23904; official Microsoft repository.
- Rethinking Self-Evolving Agent Skills / RethinkSkill, arXiv:2608.02636; official HKUST-KnowComp repository.
- Branch2Skill, arXiv:2608.08677.
- Trace2Skill, arXiv:2603.25158; Qwen-Applications repository.
- SkillZip, arXiv:2608.11079.
- SkillZip Pro, arXiv:2608.30785.
- SpreadsheetBench / SpreadsheetBench Verified-400, RUCKBReasoning official repository.

## 9. Verdict

`CONTROLLED_WORKLOAD_SUFFICIENT_BUT_PUBLIC_METHOD_BASELINE_LANE_REQUIRED_FOR_STRONG_STANDALONE_PAPER`
