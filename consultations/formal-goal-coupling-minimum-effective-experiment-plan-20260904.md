# Formal Goal Coupling — Minimum-Effective Experiment Plan V3

Date: 2026-09-04
Object: `SUCC-C-BEHAVIOR2026-TWO-FAMILY-SHARED-MULTITASK-PANEL`
Parent construct: `SUCC-C-FORMAL-GOAL-COUPLING`

## 0. Paper question and claim boundary

**Question.** With goal count and major logical structure exactly matched, is official BEHAVIOR task Q lower for the higher formal-goal-coupling member of a pair?

Formal Goal Coupling is defined on the BDDL success condition:

- one node per atomic goal-predicate occurrence;
- an edge connects predicates that share a ground object or scope-resolved bound variable;
- primary coupling measure: `shared_argument_edge_count`.

The paper tests a **matched association**, not a causal planning theory. Even a strong result does **not** authorize claims that coupling causes longer plans, deeper search, execution-order difficulty, or general policy failure.

The positive claim is deliberately narrow:

> Across two frozen shared multi-task VLA policy units, on a frozen 13-pair / 26-task panel exactly matched on goal count and major logical structure, higher shared-argument goal coupling is associated with lower official task Q.

Forbidden extrapolations:

- three-family / broad cross-policy generalization;
- causal planning- or execution-difficulty claims;
- projection back to the old strict task-specific parent;
- reopening `PORT-010`;
- intermediate-checkpoint selection;
- partial Q / effect / p-value peeking.

## 1. Frozen scientific unit

### Panel

- BEHAVIOR 2026 benchmark revision: `b1979916ec1549b10a4e65e630bc6504a9af1b00`
- official demo revision: `4f50b44796641a4d526a19d9aeadc8aa51e2f2c2`
- 26 tasks = 13 disjoint matched pairs
- exact matching variables:
  - `atomic_goal_count`
  - `branch_operator_count`
  - `goal_logic_depth`
  - `quantifier_count`
- treatment contrast inside a pair: unequal `shared_argument_edge_count`
- no pair replacement; no task replacement
- frozen task indices:
  `[8,10,12,13,14,17,33,41,42,46,51,56,59,62,65,67,68,73,74,77,81,84,85,88,89,94]`

The 26-task selection uses formal structure only and is outcome-blind.

### Data seal

- 5,200 frozen official demo episodes
- 1,380 scientific payload files
- 236,480,375,583 bytes
- host-231 whole-manifest re-seal SHA-256:
  `0538097f09aae41f407f1a923cd1d6249366566a2592b38ad30dcbe40d5de8a3`

## 2. Minimum sufficient evidence: one objection → one gate

| Gate | Reviewer objection / identification threat | Minimum evidence | Current state |
|---|---|---|---|
| G0 · Construct + pair design | “Coupling is just goal count / generic logical size.” | 13 exact structure-matched pairs; only shared-argument coupling differs. | **PASS** |
| G1 · Human-demo negative control | “High coupling only means humans take longer successful paths.” | Frozen human-demo horizon test conditional on goal count. | **CLOSED · NOT SUPPORTED** |
| G2 · π0.5 training realization | “The single-GPU recipe was tuned after outcome access.” | Outcome-blind resource ladder and one preregistered practical-batch ladder. | **PASS · batch16 selected** |
| G3 · π0.5 terminal model | “Training never reached the frozen evaluable model.” | One clean formal run to 50,000 optimizer updates; only terminal label 49999 is evaluable. | **RUNNING · run2** |
| G4 · Terminal checkpoint qualification | “Checkpoint shopping could create the effect.” | Content-address / serving-qualification of 49999 only; 10k/20k/30k/40k are recovery-only. | **LOCKED** |
| G5 · Two-family official outcomes | “One model or a few initializations could create a spurious pair effect.” | π0.5@49999 + GR00T@238000, each 26 tasks × 10 official instances × one rollout. | **LOCKED** |
| G6 · Final confirmatory statistic | “Partial peeking / post-hoc statistics could create significance.” | Close all 520 rollouts first, then compute the 13 pair contrasts and all 8192 exact sign flips once. | **LOCKED** |

This is the intended workload. Extra models, datasets, seeds, or ablations are not added unless they buy identification, precision, robustness against a concrete reviewer objection, or a scientifically distinct generalization claim.

## 3. Negative control already closed

Fresh tasks 2..99, 98 tasks:

- verdict: `DEMO_HORIZON_PRIMARY_NOT_SUPPORTED`
- edge coefficient: `-0.009792957356752403`
- exact stratified permutation p: `0.5342746572534275`

Interpretation:

> Higher formal coupling is not supported as a predictor of longer successful human demonstrations under the frozen test.

This is an **interpretive negative control only**. It is not a covariate, exclusion rule, rescue variable, or post-hoc mechanism switch.

## 4. Policy families and the role of “baselines”

The experiment is not a method-vs-baseline leaderboard. It is an identification experiment for a structural task property. Therefore the strongest comparisons are structural and cross-policy, not a large menu of training methods.

### Family A — π0.5

One frozen shared26 multi-task policy is trained prospectively.

Scientific invariants retained throughout resource repair:

- same π0.5 base checkpoint;
- same 5,200 frozen episodes;
- same seed 42;
- same AdamW configuration;
- same LR schedule;
- same EMA cadence (`0.99`);
- same 50,000 optimizer-update horizon;
- same action horizon 32;
- same normalization;
- no validation;
- no W&B;
- no loss-based model selection;
- terminal scientific checkpoint = label 49999 only.

### Family B — GR00T N1.7

- frozen checkpoint: `checkpoint-238000`
- **zero training jobs**
- evaluated on the same frozen 26 tasks and official instances

### Why this is a sufficient comparison set for the current claim

- exact matching removes goal-count / major-logic differences inside each pair;
- two independent policy families test whether the pair direction is shared rather than π0.5-specific;
- separate family medians are frozen support gates;
- adding a third family would buy a broader generalization claim, not identification of the current narrow claim, so it is not required here.

## 5. Why the original batch64 implementation was superseded for the practical child

This change is an **outcome-blind resource realization**, not a scientific-result-driven recipe search.

### Source batch64 single-A100 path

- step-0 state fits on one A100-80GB;
- real batch64 full gradient does not fit.

### Preregistered effective-batch64 accumulation ladder

| Physical batch × accumulation | Effective batch | What happened |
|---|---:|---|
| 16 × 4 | 64 | first micro-gradient completed; second backward OOM; extra allocation ≈ 17.06 GB |
| 8 × 8 | 64 | first micro-gradient completed; second backward OOM; extra allocation ≈ 15.82 GB |
| 4 × 16 | 64 | first micro-gradient completed; second backward OOM; extra allocation ≈ 15.21 GB |

Mechanism-level resource conclusion:

> The full FP32 all-parameter gradient accumulator (~12.49 GiB) remains resident while the next full backward needs another ~15–17 GB. Lowering the physical microbatch from 16 to 8 to 4 therefore does not remove the dominant coexistence peak.

The effective-batch64 accumulation route is **closed**. No additional microbatch-2 / exotic accumulation variant may be introduced as an unregistered rescue.

### Preregistered practical single-GPU batch ladder

`16 → 8 → 4`

Batch16, the first candidate, passed a complete synthetic source `train_step`:

- step 0 → 1;
- forward/backward PASS;
- AdamW update PASS;
- `apply_updates` PASS;
- EMA update PASS;
- resulting synthetic state discarded;
- BEHAVIOR data not accessed;
- real scientific optimizer updates remained 0.

Therefore **batch16 is selected** and batch8/4 are permanently not run.

This practical child must not be described as bitwise-equivalent to source batch64. It is a prospectively frozen single-GPU realization that preserves all other scientific variables and applies one recipe uniformly to all 26 tasks.

## 6. Runtime repairs vs. scientific variables

These are engineering/runtime repairs only:

- direct-device checkpoint restore;
- RGB metadata projection removing unused depth decode while keeping sealed RGB bytes unchanged;
- source-equivalent accelerated normalization;
- user-space FFmpeg 6 runtime for TorchCodec;
- `RLIMIT_NOFILE=65536` for the qualified video-decoder FD cache;
- state-first checkpoint restore;
- serialize old-batch completion before materializing the next batch.

None changes:

- task selection;
- policy base checkpoint;
- seed;
- optimizer;
- learning-rate schedule;
- EMA;
- normalization;
- action horizon;
- training update count;
- outcome protocol;
- statistical test;
- terminal checkpoint selection rule.

## 7. π0.5 formal-training lineage

### Formal run1 — closed infrastructure failure

- completed optimizer updates: 1
- terminal exception: `OSError: [Errno 24] Too many open files`
- no checkpoint existed
- no loss was read/reported
- no policy outcome was read
- no run1 model / optimizer / checkpoint state is reused
- disposition: `CLOSED_FAILED_INFRASTRUCTURE_NO_SCIENTIFIC_EVALUATION`

### FD qualification

The real video-decoder path can hold approximately 1,150 file descriptors. The repair raises only the process FD capacity:

- soft limit: 65,536
- scientific variables changed: false

### Formal run2 — current live run

Latest durable snapshot used by this plan:

- status: `PI05_PRACTICAL_BATCH16_FORMAL_RUN2_FDLIMIT_RUNNING`
- completed optimizer updates: **401 / 50,000**
- last completed loop label: 400
- progress timestamp: **2026-09-04 11:12:17 +08:00**
- GPU memory: ~73,535 MiB
- open FDs: ~1,183 / 65,536
- checkpoint labels present: none yet
- loss values read/reported: false
- policy outcomes read: false

Run2 is a fresh run from step 0. It does not resume run1.

Progress is a runtime status, not an outcome. No scientific inference is permitted from training progress.

## 8. Terminal checkpoint rule

Frozen checkpoint labels:

- 10,000
- 20,000
- 30,000
- 40,000
- **49,999**

The first four are **exact-state recovery only**. They may not be served, evaluated, compared, or selected scientifically.

Only label **49,999** may enter the policy-evaluation gate.

## 9. Outcome protocol — 520 official rollouts

Only after π0.5 label 49999 passes content-address and serving qualification:

### π0.5

- 26 tasks
- official public instances 0..9
- exactly one rollout per task-instance
- 260 rollouts

### GR00T N1.7

- same 26 tasks
- same official public instances 0..9
- exactly one rollout per task-instance
- 260 rollouts

Total:

\[
26 \times 10 \times 2 = 520
\]

Forbidden during execution:

- retry-to-success;
- task replacement;
- instance replacement;
- partial family contrast inspection;
- partial Q inspection;
- effect-size inspection;
- p-value inspection.

Progress/failure metadata is allowed only for operational integrity.

## 10. Final confirmatory analysis

For each family \(f\) and matched pair:

\[
\Delta_f = Q_{high} - Q_{low}
\]

Joint pair contrast:

\[
\Delta_{pair} = (\Delta_{\pi0.5} + \Delta_{GR00T}) / 2
\]

Primary statistic:

- mean of the 13 joint pair contrasts

Frozen test:

- all 8192 exact sign flips
- two-sided \(\alpha=.05\)

Positive support requires **all four**:

1. mean joint contrast < 0;
2. exact p < .05;
3. median π0.5 pair contrast < 0;
4. median GR00T pair contrast < 0.

No alternate primary statistic is selected after outcomes are opened.

## 11. What is enough for the paper — and what is not

### Minimum sufficient evidence set

1. formal construct + exact matching — done;
2. human-demo horizon negative control — done, not supported;
3. π0.5 clean terminal model — running;
4. frozen GR00T comparison checkpoint — ready, zero training;
5. complete two-family 520-rollout matrix — locked;
6. one exact preregistered final test — locked.

### Optional expansion policy

Do **not** add models, datasets, seeds, or ablations merely to resemble the experiment count of a larger paper. Add at most one expansion only if it changes a reviewer verdict by addressing a concrete remaining objection that the frozen evidence above cannot answer.

## 12. Immediate execution order

1. Keep run2 untouched until 50,000 optimizer updates or a genuine external/infrastructure failure.
2. At failure: stop and adjudicate exact-state recoverability before any restart; never auto-retry.
3. At completion: content-address terminal label 49999 and qualify serving.
4. Run the full 520 official rollouts without partial outcome peeking.
5. Close the rollout matrix.
6. Compute 13 pair contrasts + all 8192 exact sign flips once.
7. Only after that result is opened decide whether a new mechanism/generalization study is justified.
