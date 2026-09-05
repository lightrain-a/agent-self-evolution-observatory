# E2-R17 V3 Stage-A first-run technical failure record

Date: 2026-09-05

## Canonical execution state

The previously approved fresh DeepSeek identity boundary was crossed exactly once.

- qualification status: `PASS`
- requested model: `deepseek-v4-pro`
- resolved model: `deepseek-v4-pro-ga-260813`
- provider generation attempts: 1
- provider retry limit: 0
- thinking: disabled
- scientific outcome accessed during identity qualification: false
- benchmark data accessed during identity qualification: false

The local identity adjudication returned:

`PASS_CURRENT_REVIEW_TRANCHE`

A single-use Stage-A authorization was then minted:

`AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A`

Stage-B, updater, heldout, analyzer, public benchmark, paper-promotion, and submission authority all remained false.

## First Stage-A run

The authorized first-run-only V3 Stage-A runner was launched on 2026-09-05.

The first predeclared task was:

`r17-b21-cgwb-p0`

Its immutable exact-once attempt marker was created before provider I/O, as required.

The provider budget ledger then recorded four pre-I/O claims across rollout 0 and rollout 1. The run terminated during the first task with Ark HTTP 429 `AccountQuotaExceeded`. The provider message states the weekly quota resets at:

`2026-09-07 00:00:00 +0800`

Because provider dispatch had already occurred, this task is a burned attempted-but-unsealed unit under the frozen exact-once policy. It must not be replayed under the R2 contract.

## Fail-closed integrity state

At diagnosis:

- attempted task markers: 1
- sealed task receipts: 0
- frozen K=8 pools: 0
- completed streams: 0
- completed-stream manifest: absent
- Stage-A terminal summary: absent
- support inspected: false
- updater calls: 0
- heldout access: 0
- Stage-B execution: 0
- partial scientific effect read: false
- global lease: preserved as `RUNNING_STAGE_A_V3`
- local exclusive lock: preserved

No task replacement, replay, threshold change, or support inspection has occurred.

## Recovery boundary

The frozen R2 contract explicitly states that an attempted-but-unsealed unit is burned and requires separate adjudication. Therefore the current R2 Stage-A runner must not be relaunched.

A zero-provider independent recovery-review packet has been frozen at:

`oracle_briefs/E2_R17_V3_STAGE_A_TECHNICAL_MISSING_RECOVERY_REVIEW_20260905.md`

Primary proposed minimal recovery under review:

- one fixed `TERMINAL_TECHNICAL_MISSING_POST_DISPATCH` task;
- no replay;
- no replacement;
- execute only the remaining 159 original task IDs under a new versioned recovery contract after a fresh identity qualification and separate authorization;
- preserve the original absolute support threshold of >=4 mixed pools in every stream;
- affected stream must satisfy >=4 mixed pools among its remaining 7 observable pools;
- treated Stage-B dose remains exactly 4 mixed pools per stream if support passes;
- any second post-dispatch technical missing causes STOP;
- no support read until all remaining 159 units are terminal and the fixed technical-missing receipt is sealed.

This proposal has no execution authority until independently adjudicated.
