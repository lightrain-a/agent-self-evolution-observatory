# B1 R83 — Qwen-only interim analysis after non-adaptive Llama freeze

Date: 2026-09-06

Role: interim scientific read of the completed Qwen Stage Q only. Llama Stage L (132 P/T trajectories) was frozen in R82 before any Qwen `terminal_success` value was opened; this note does not alter the Llama model, schedule, analysis hierarchy, or cross-model no-pooling rule.

## Stage seal

- Qwen trajectories: 189/189 COMPLETE
- Technical missing: 0
- Sealed terminal ledger SHA256: `58d0ece1be8911817bfd38c28619797c5c9bec3714c135ce9c00c85ce7cfb829`
- R82 Llama frozen schedule SHA256: `4aff80e45e07d339dd26769f82d485c1b8920079641a8174711d4f8e0c58f179`

## Frozen primary result: T_truthful - P_neutral, n=66

- P_neutral successes: 34/66
- T_truthful successes: 34/66
- Paired risk difference T-P: `0.0000`
- P-only success: 1 task (`338`)
- T-only success: 1 task (`494`)
- Both success: 33
- Both fail: 31
- Discordant pairs: 2/66 = 3.03%
- Exact two-sided paired sign-flip p: `1.0`
- 100k paired bootstrap 95% CI: `[-4.55pp, +4.55pp]`
- Conservative sparse-discordance RD 95% interval: `[-9.26pp, +9.26pp]`
- Success-set Jaccard: `33/35 = 0.942857`
- Outcome agreement: `64/66 = 0.969697`
- Frozen primary state: `NO_EFFECT_DETECTED`

Per R72/R73, `NO_EFFECT_DETECTED` does **not** mean equivalence, practical smallness, provenance irrelevance, or proof of a prompt-format-only explanation. Numerically, the prospective n=66 interval is much tighter than the historical n=32 field-revelation study, but the protocol does not upgrade that fact into a formal equivalence claim.

## Gate-kept correctness contrast

Because the Qwen T-P primary gate did not detect an effect, the mixed-provenance `T_truthful - S_shuffled` correctness contrast remains **NOT OPENED** under the frozen hierarchy. No claim about provenance-assignment correctness is made from R83.

## Task-level substitution matters

Equal aggregate success does not mean identical task behavior. The exact success sets differ on two tasks:

- Task 338: P succeeds, T fails.
- Task 494: P fails, T succeeds.

The two effects cancel in the aggregate.

### Task 338

Task: recursively find `.txt` files under `/testdir`, chmod them to 600, delete `.log` files older than one day, and leave exactly three correctly permissioned `.txt` files.

- P: SUCCESS, 16 steps.
- T: FAIL, 1 step.
- P first parsed action is executable (although malformed/mixed with formatting text).
- T first response parses as INVALID; first executable action is `None`.

This is consistent with a local formatting / decision-boundary perturbation that immediately places the closed loop on a terminally bad branch. It is one post-outcome mechanism example, not a population mechanism estimate.

### Task 494

Task: change `testuser` to `/bin/zsh`, add the user to `developers`, create `.zshrc`, and ensure `/home/testuser/dev` is group-owned by `developers`.

- P: FAIL, 16 steps.
- T: SUCCESS, 15 steps.
- First executable action is identical in P and T: `sudo chsh -s /bin/zsh testuser`.
- The first action-level divergence appears at action index 2.

This shows that a terminal flip need not be mediated by the first action. Provenance can leave the first command unchanged yet alter later recovery/action selection.

## Local behavior diagnostics

Only 3/66 P/T pairs change the first executable action:

- Task 321: both FAIL; different first action; P 16 steps, T 7.
- Task 338: P SUCCESS / T FAIL; immediate first-action/parse divergence.
- Task 346: both SUCCESS; different first action; P 10 steps, T 6.

Task 494 is terminal-discordant despite an identical first action. Therefore first-action sensitivity and terminal utility are distinct objects.

The mean complete-pair step difference is T-P = `-0.47` steps, but this is a non-inferential diagnostic and cannot rescue the failed terminal primary gate.

## Scientific interpretation

The clean prospective Qwen result supports the narrow statement:

> Under a format-matched neutral-vs-truthful source-outcome field on the frozen 66-task panel, truthful provenance does not produce a resolved terminal-success increment. Aggregate success is identical (34/66 vs 34/66), while two task-specific terminal flips occur in opposite directions.

The result is consistent with provenance acting as an executor-specific local policy cue whose effects are sparse and heterogeneous at the terminal level. It is not evidence that provenance is useless, and it does not identify the correctness mechanism because the T-S gate stayed closed.

## Relationship to the historical 32-pair Qwen result

The historical A/B study had 15/32 versus 16/32 and 9/32 first-action divergence. The new prospective format-matched P/T study has 34/66 versus 34/66 and 3/66 first-action divergence. This pattern is consistent with the old explicit-field/masked contrast containing more prompt-surface sensitivity than the matched-field P/T design, but the panels differ, so R83 does not attribute the reduction uniquely to format matching.

## Remaining required step

Run the already frozen, non-adaptive Llama Stage L (132 P/T trajectories). Only after that stage completes should the final cross-executor R72/R73 analysis be opened. Qwen and Llama remain separately reported and are never pooled.
