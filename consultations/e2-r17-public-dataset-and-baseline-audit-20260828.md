# E2-R17 public-dataset and baseline audit

Date: 2026-08-28  
Status: PRE-OUTCOME / ZERO SCIENTIFIC AUTHORITY  
Branch: `research/e2-r17-compute-shielding-20260825`  
Purpose: freeze which datasets and baselines can test the serving-induced observation-kernel claim without turning the paper into a benchmark or method zoo.

## 1. Decision

E2-R17 will use a three-layer evidence design:

1. **Controlled Spreadsheet Suite V2** — mechanism identification only. This is a locally generated, SpreadsheetBench-compatible suite with deterministic validators and preregistered reusable failure families. It must never be described as a public benchmark.
2. **SpreadsheetBench Verified-400** — primary public realistic externality and longitudinal validation, after the exact-same-pool cloned-state mechanism passes on the controlled suite.
3. **SpreadsheetBench 2** — late workflow-level transfer only, after the mechanism and the public V1 result pass. It cannot be introduced to rescue a negative result.

The strongest direct method baseline is **SkillCAT-style same-task success/failure contrast**. The strongest feedback-dynamics baselines are the **Normal / Fail-only / Success-only** conditions from *Rethinking Self-Evolving Agent Skills*. The E1 identification experiment additionally requires projection-specific controls that are not optional method baselines: winner-only, precommitted rollout-0, Rejected-Witness, duplicated winner, and random nonwinner.

## 2. Dataset audit

### 2.1 Controlled Spreadsheet Suite V2

Role: causal identification, law qualification, prospective family prediction.

Frozen local substrate:

- root: `/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2`
- total tasks: 378
- deterministic failure families: 6
  - input/output contract
  - target sheet/range
  - schema/key alignment
  - aggregation/join
  - formula/materialization
  - multi-step pipeline
- suite manifest SHA-256: `2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4`
- split manifest SHA-256: `aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9`
- qualification: 378/378 golden self-check PASS and 378/378 initialized negative-control PASS
- public status: **not public; do not use for external benchmark claims**

Why it is required: the central estimand changes only the learning projection on an identical generated search pool. A public benchmark alone cannot guarantee enough mixed success/failure pools, a disjoint pre-outcome failure-family partition, or deterministic family-level interventions.

### 2.2 SpreadsheetBench Verified-400

Primary sources:

- SpreadsheetBench official repository, NeurIPS 2024 Datasets and Benchmarks track.
- SpreadsheetBench Verified release announcement from the original benchmark collaboration.

Source-supported facts:

- SpreadsheetBench contains 912 real-world spreadsheet questions and 2,729 test cases, with OJ-style evaluation over multiple workbooks per instruction.
- In December 2025 the project released SpreadsheetBench Verified, an expert-annotated 400-instance subset intended to improve automated evaluation reliability.
- The benchmark supports multi-round ReAct plus code-execution feedback, matching the first-party MindMemOS spreadsheet-agent setting more closely than a static formula benchmark.

Frozen local copy:

- archive: `/data/wyt/e2-r17-compute-shielding/SpreadsheetBench/spreadsheetbench_verified_400.tar.gz`
- archive SHA-256: `10ef893dd29cb13ab97143ea787e68cdc9574a13873ab9a54e50b31dc03fc949`
- dataset JSON SHA-256: `bcecaa89a005bd4e3bbe98da150a86e8062c27f262e575d5e47bd9861b3525e7`
- rows: 400
- workbook members: 800 `.xlsx` files
- metadata fields: `id`, `instruction`, `spreadsheet_path`, `instruction_type`, `answer_position`, `answer_sheet`, `data_position`

Role in E2-R17:

- public test of whether the controlled same-pool mechanism transports to real forum-derived tasks;
- public multi-round comparison of online acting performance and frozen persistent-skill performance;
- source-faithful SkillCAT-style contrast and RethinkSkill feedback-view baselines;
- never used to tune the controlled-suite family taxonomy, witness rule, score threshold, or STOP condition.

Required public protocol:

- publish exact evolution/validation/test IDs;
- bind the official evaluator and workbook archive hashes;
- rerun no-skill and initial-skill baselines under the exact same actor, model identity, prompt, turn limit, formula-recalculation policy, and evaluator;
- do not import scores from papers whose split or harness differs;
- keep development IDs permanently excluded from confirmatory promotion;
- classify public tasks only with a pre-outcome metadata/instruction rule, never by observed model failure.

### 2.3 SpreadsheetBench 2

Primary sources:

- official SpreadsheetBench 2 repository and project page, released in 2026;
- the official project describes 321 end-to-end workflow tasks across financial modeling/template, debugging, and visualization, with complex multi-sheet workbooks and deliverable-level evaluation.

Role in E2-R17:

- late externality test of the already-frozen observation-kernel prediction on workflow-level tasks;
- primary deterministic categories: Debugging, Financial Model, and Template;
- Visualization is secondary because it introduces a VLM checklist evaluator and a Windows COM rendering dependency, which confounds the first mechanism test.

Entry condition:

- exact-same-pool E1 passes;
- prospective sign/rank prediction passes;
- Verified-400 public result passes its preregistered criterion;
- the SpreadsheetBench 2 subset and evaluation policy are frozen before any model outcomes are inspected.

STOP discipline: a negative Verified-400 result is not a reason to open SpreadsheetBench 2. That would be benchmark shopping.

## 3. Baseline and control audit

### 3.1 Mandatory E1 causal controls

| Arm | What the updater sees | Scientific purpose |
|---|---|---|
| Winner-only | served winner | current tied acting/learning default |
| Precommitted rollout-0 | rollout 0 from the exact same pool | alternative fixed observation kernel; not a no-censoring oracle |
| Rejected-Witness | winner outside rescue; preregistered failed witness on rescue | minimal causal repair naturally implied by the mechanism |
| Duplicated winner | winner twice under matched packet structure | token/context-length control |
| Random nonwinner | winner plus deterministic hash-selected nonwinner | generic diversity control |
| SkillCAT-style contrast | same-task winner/failure contrast | strongest direct method-reduction baseline |

All arms must preserve:

- identical task;
- identical initial skill SHA;
- identical K=8 search pool and served winner;
- identical actor, verifier, updater implementation, updater model, update batch size, and evaluation probes;
- one task-level add-record per pool and identical top-level acting score;
- only the embedded evidence packet may differ.

### 3.2 Mandatory longitudinal feedback baselines

Source-faithful baselines from *Rethinking Self-Evolving Agent Skills*:

- Normal: successful and failed trajectories;
- Fail-only;
- Success-only;
- initial/no-evolution skill;
- test-time parallel sampling and sequential refinement as acting-compute controls where budget matching is possible.

These baselines test feedback dynamics, but they do not replace the exact-same-pool E1 intervention. They change the available feedback set across rounds rather than isolating the serving-induced projection on the same pool.

### 3.3 Closest-work reduction boundary

**SkillCAT** already performs multi-seed same-task success/failure pairing, divergence extraction, source-task replay validation, and persistent skill evolution on SpreadsheetBench. Therefore E2-R17 cannot claim novelty for any of those components. SkillCAT-style contrast is mandatory, and a source-faithful implementation must be reported separately from the minimal Rejected-Witness projection.

**Rethinking Self-Evolving Agent Skills** already shows that feedback composition matters over multiple rounds and that selected evolved skills depend on failed trajectories. Therefore E2-R17 cannot claim that “failures help skill learning” or that persistent evolution differs from test-time scaling. The residual causal claim is narrower: a serving selector changes the observation kernel of the updater by hiding a generated and verifiable failed witness.

**SkillOpt / related skill-optimization systems** already use bounded edits and held-out validation. Validation-gated text editing is substrate machinery, not a contribution.

**Selective labels, performative prediction, and DAgger** are conceptual reductions. E2-R17 must present itself as a specialized causal mechanism in a generated search set with fully observed but selectively logged candidate trajectories, not as a new general theory of selective data.

## 4. Frozen experiment sequence

1. E0 pilot on a predeclared family-balanced subset of the controlled calibration lane.
2. E0 full nested K=1/2/4/8 pool-law qualification.
3. E1 exact-same-pool cloned-state intervention, one independently evolved eight-task stream as the scientific unit.
4. Common K=1 held-out probe evaluation, identical across arms.
5. Prospective family/regime prediction on unseen controlled streams.
6. Only after GO: multi-round controlled evolution.
7. Only after GO: Verified-400 public validation and source-faithful baselines.
8. Only after public GO: SpreadsheetBench 2 workflow transfer.

## 5. No-benchmark-shopping rules

- No task may move from development to confirmation.
- Integrity reserves replace files only after a pre-execution integrity failure; they never replace a bad model outcome.
- No failure-family definition may be changed after actor outcomes are visible.
- No public split may be changed after any public result is visible.
- No second benchmark may be opened to rescue a failed central mechanism.
- No paper claim may cite controlled-suite performance as public external validity.
- No published baseline score may be copied without an exact-harness rerun; benchmark version, split, prompting, evaluator, and formula-recalculation differences can dominate reported gains.

## 6. Current decision

`PUBLIC_DATASET_AND_BASELINE_PLAN_PASS_FOR_PREEXECUTION_REVIEW`

This audit authorizes incorporation into the F0-R4 candidate contract. It does not authorize scientific calls, GPU use, paper promotion, manuscript claims, front-end claims, or submission.

## 7. Primary-source registry

- SpreadsheetBench: Ma et al., NeurIPS 2024 Datasets and Benchmarks, arXiv:2406.14991; official repository `RUCKBReasoning/SpreadsheetBench`.
- SpreadsheetBench Verified: official repository release notice and the original-team collaboration announcement dated 2025-12-02.
- SpreadsheetBench 2: official repository `RUCKBReasoning/SpreadsheetBench-2` and project page, released in 2026.
- SkillCAT: Chen et al., arXiv:2606.13317v2.
- Rethinking Self-Evolving Agent Skills: Liu et al., arXiv:2608.02636.
