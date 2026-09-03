# C1 PACTA-MSR fresh3 post-gate — independent Oracle review and Q08 adjudication

Date: 2026-09-03
Model: GPT-5.6 Sol
Thinking effort: Extra High (4/5 verified in browser DOM)
Oracle session: `c1-pacta-msr-fresh3-current-2`
Conversation: `6a99839b-349c-83e8-ab63-f6abc2008eef`
Transcript SHA256: `2eda0a83f8f9cf6edc89325863d9df55b898d9ba976b77d2404ed6fa47f872a1`
Decisive verdict: `REVISE_C1_P0_BEFORE_SUCCESSOR`
Scientific method-effect authority: none
Fresh3 retry/replacement/top-up authority: none

## What passed

The reviewer accepted the fresh3 governance and most of the downstream P0 design:

- Source 2 had already consumed six model-bearing provider calls before the provider-layer RuntimeError. It is therefore a consumed-invalid logical episode under the frozen exactly-once scientific unit.
- Because the preregistered source gate required all 10 fixed sources provenance-valid, the whole fresh3 pool was correctly retired immediately.
- Retrying source 2 would instantiate a new stochastic realization after a scientific realization had already been consumed; retry is scientifically invalid.
- A wholly new fresh4 successor is permissible only prospectively, with a fully disjoint source/future pool and stronger transport qualification frozen before any fresh4 outcome.
- `NO_MSR_METHOD_EFFECT_EVIDENCE` remains the only valid claim authority. One valid source does not license any method-effect inference.
- The 8-pilot / 2-sealed split is valid; sealed units must remain completely unused until separately authorized.
- One realized writer and binder draw per branch is valid only for the explicitly conditional realized-state estimand. It is not an average effect over writer/binder randomness.
- The shadow statistic `min(B1,B2)-max(WS,WF)` is acceptable as a frozen developmental localization gate.
- The mechanism gate is a preregistered qualification gate, not literal final-endpoint double dipping, provided the final stage is described as conditional on qualification.
- Rate-matched-random K equal to the observed G+ opening count is valid because the random ranking was frozen before shadow outcomes and K is exposure-frequency matching rather than outcome tuning.

## Verdict-changing defect

The final primary endpoint used raw plug-in empirical total variation between two exact-command histograms with only six samples per writer branch.

For a high-cardinality categorical action space, plug-in empirical TV has substantial finite-sample upward bias. Crucially, the bias changes with distributional concentration. An arm that merely makes actions more diffuse can show higher empirical success-vs-failure TV even when the two underlying distributions are identical. Therefore a positive `A3-A2` TV contrast can reflect arm-dependent stochastic diffuseness rather than preservation of writer-state information.

This is an identification defect, not merely an uncertainty/CI issue.

## Q08 repair

Fresh3 remains permanently retired. The historical Q07 contract is not mutated.

For any fresh successor, the final primary per-unit state-separation statistic is replaced by the unbiased exact-match-kernel MMD^2 / collision U-statistic:

`k(a,b)=1[a==b]`

`MMD_u^2 = within_success + within_failure - 2*cross`

with ordered-pair diagonals removed from the two within-branch terms.

Properties relevant to the repair:
- under identical underlying categorical action distributions, the estimator has expectation zero regardless of how diffuse that common distribution is;
- the finite-sample estimate is intentionally allowed to be negative; clipping at zero is forbidden because it would restore positive null bias;
- raw empirical TV may remain descriptive secondary output only.

Primary successor contrast:

`D_select = MMD_u^2(A3_PACTA_MSR) - MMD_u^2(A2_RATE_MATCHED_RANDOM)`

The A3-vs-A0 and A3-vs-A1 companion checks are computed on the same unbiased-MMD^2 scale.

## Zero-provider threshold refreeze

The old TV threshold `0.05` is not mechanically transferred to the new estimator.

A deterministic synthetic calibration was run with:
- Python 3.11.15 / NumPy 1.26.4;
- seed `20260903`;
- 200,000 repetitions;
- 8 scientific units;
- 6 success + 6 failure action samples per unit;
- predeclared threshold candidates `{0.15, 0.20, 0.25}`;
- null categorical support sizes `{2,4,8}`;
- gate = `mean D_select >= threshold` AND positive-D units > negative-D units;
- null requirement: worst gate rate <= 0.05;
- canonical-alternative requirement: gate rate >= 0.45 for A3 distributions `(2/3,1/3)` vs `(1/3,2/3)` while A2 remains `(1/2,1/2)` vs `(1/2,1/2)`.

Results:
- threshold 0.15: worst null 0.095145, alternative 0.617205 — FAIL;
- threshold 0.20: worst null 0.048225, alternative 0.517080 — PASS;
- threshold 0.25: worst null 0.022675, alternative 0.411135 — FAIL alternative-power floor.

Selected successor threshold: `mean D_select >= 0.20`.

Calibration artifact SHA256:
`b47cca6a6961f7961bdfa7e17267bc4e90e10ffd2bf5d9926df61afb124f86a6`

## Successor transport requirement

The fresh3 failure showed that the earlier synthetic multistep smoke was insufficient for long multi-step finalization. Before any fresh4 scientific source acquisition, the successor must pass a prospectively frozen non-scientific transport stress qualification that exercises repeated model-bearing bridge turns and successful final ordinary-JSON completion under the same provider/bridge envelope. This qualification cannot use a fresh4 scientific source task.

## Current authority

- fresh3: permanently retired;
- fresh3 retry/replacement/top-up: forbidden;
- writer/binder/probe/shadow/final on fresh3: forbidden;
- Q08 metric/statistical repair: completed, zero provider calls;
- fresh4 scientific source acquisition: **not authorized by this adjudication**;
- method-effect claim authority: `NO_MSR_METHOD_EFFECT_EVIDENCE`.
