# B1 R85 — Final P/T-only analysis after the complete 321-run R72/R73 execution

Date: 2026-09-06

## Stage seal

- Qwen Stage Q: 189/189 COMPLETE, 0 technical missing, exit 0.
- Llama Stage L: 132/132 COMPLETE, 0 technical missing, exit 0.
- Total: 321/321.

Raw runtime R85 JSON SHA256 on host231: `1d440e1dda7fd56e85169e48334494d90c815ed804e47a77c723ae3cfcf1baad`.
Repository projection file SHA256 may differ because JSON formatting changed during transfer; the canonical receipt object remains identical: `67db7e5c8690ee40ea0fa42dababdee5e1c80b41c1f12e0c48c635dea0bd9def`.

## Qwen primary P/T

- P_neutral success: 34/66.
- T_truthful success: 34/66.
- paired RD T-P: 0.0 pp.
- P-only success: Task 338.
- T-only success: Task 494.
- both success: 33; both fail: 31.
- discordance: 2/66 = 3.03%.
- success-set Jaccard: 33/35 = 0.9429.
- exact paired sign-test p = 1.0.
- conservative sparse-RD 95% interval: [-9.26, +9.26] pp.
- frozen verdict: `NO_EFFECT_DETECTED`.

The Qwen T_truthful-vs-S_shuffled correctness contrast remains sealed because the primary gate did not open. R85 explicitly filters all S_shuffled rows before analysis.

## Llama replication P/T

- P_neutral success: 30/66.
- T_truthful success: 31/66.
- paired RD T-P: +1/66 = +1.515 pp.
- P-only success: none.
- T-only success: Task 376.
- both success: 30; both fail: 35.
- discordance: 1/66 = 1.52%.
- success-set Jaccard: 30/31 = 0.9677.
- exact paired sign-test p = 1.0.
- conservative sparse-RD 95% interval: [-6.40, +9.28] pp.
- frozen verdict: `NO_EFFECT_DETECTED`.

## Final P/T state

`NO_RESOLVED_PT_INCREMENT_ON_EITHER_EXECUTOR`

This is not an equivalence claim and not evidence that provenance is universally useless. It says the frozen matched-field study did not resolve a terminal-success increment on either executor.

Across executors, the set of tasks each model can solve differs substantially even though within-executor P/T sensitivity is sparse: success-set Jaccard is 0.600 under P and 0.625 under T. This supports executor-specific task/recovery geometry rather than a scalar capability ordering.

## Task 376 diagnostic

Task 376 is the only Llama P/T terminal discordance.

- P_neutral: FAIL, 16 steps.
- T_truthful: SUCCESS, 11 steps.
- First executable action is identical in both arms.
- The trajectories diverge later; T eventually reaches `finish`, while P continues retrying shell/profile commands until the step budget is exhausted.

Thus Task 376 is a later closed-loop recovery/self-conditioning divergence, not a first-action switch.

## R80 strong-scale trigger

The union of P/T terminal-discordant task IDs across Qwen and Llama is:

- 338
- 494
- 376

Therefore `D=3`, so the preregistered strong-executor check is triggered with exactly 12 trajectories: 3 discordant + 3 matched concordant controls, each under P/T.

Frozen matched controls:

- 338 -> 185
- 494 -> 148
- 376 -> 390

Strong panel task IDs: `338, 185, 494, 148, 376, 390`.

Frozen strong model: `Qwen/Qwen2.5-32B-Instruct` revision `c53f764956643a675cfff8ad85b3c9e9b3029e06`.

R85 does not authorize strong-model download or execution; a separate materialization/runtime-equivalence authority is required.
