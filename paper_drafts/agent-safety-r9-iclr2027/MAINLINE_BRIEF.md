# R9 paper mainline brief

## Leading advantage

This paper shows that, in a fixed persistent-agent evaluation, a clean current safety panel is not a temporal certificate. Measuring the first future violation reveals failures that a current-state snapshot does not contain.

## Battlefield

- Persistent substrate: Agent Workflow Memory (AWM) workflow memory and history.
- Agent backbone: Qwen3-8B.
- Environment: BrowserART tasks implemented through BrowserGym.
- Safety evaluator: HarmBench-Llama-2-13b-cls.
- Frozen evaluation: four selected persistent states in two task strata, three branches per state, and a three-step future horizon.
- Current-state qualification: three probes per state (12 episodes total).
- Future evaluation: 36 completed episodes.

## Central claim

Within this operationalization, passing the current safety panel did not guarantee the absence of a first violation during a three-step persistent-update and held-out-task schedule.

## Evidence spine

1. All 12 current-state qualification episodes were classified as non-violations.
2. The future evaluation completed all 36 planned episodes and contained 11 violation episodes.
3. A first violation occurred in 8 of 12 branches and in 3 of 4 persistent states.
4. First events occurred at step 1 in one branch, step 2 in six branches, and step 3 in one branch; four branches were censored at the three-step horizon.
5. State-by-branch outcomes were heterogeneous, including a 2-versus-0 split between the paired map states and a 3-versus-3 result between the paired reddit states.
6. The design does not isolate update-alone causality because persistent updating and the held-out task schedule co-vary.

## Claim boundary

Supported: a current static non-violation panel did not guarantee future non-violation under the frozen joint update-plus-schedule evaluation.

Not supported: an update-only causal effect; universal failure of static safety evaluation; a population hazard estimate; state identity as a statistically established predictor; HarmBench as a noiseless safety oracle.

Limitation: the decisive missing contrast is the same held-out task schedule without persistent updates.

## Main-text exclusions and demotions

- Runtime recovery history, support failures, execution metadata, and evidence-receipt mechanics belong in the artifact documentation or reproducibility appendix.
- The same-schedule/no-update contrast is the recorded reopen condition, not a completed experiment.
- Failure taxonomy is retained in the research record but does not organize the paper narrative.
