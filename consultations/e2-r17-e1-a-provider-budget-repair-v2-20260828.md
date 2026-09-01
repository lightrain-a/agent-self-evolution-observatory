# E2-R17 E1-A Provider-Budget Repair V2

Date: 2026-08-28
Status: DESIGN/ENGINEERING REPAIR ONLY — ZERO SCIENTIFIC AUTHORITY

## Trigger

The first E1-A pre-execution review had split verdicts: DeepSeek allowed a separately frozen E1-A authorization, while Kimi returned HOLD on one P0 issue. The blocker was not scientific outcome selection. It was that the declared 10 provider calls per rollout and 7680 calls globally were enforced only post hoc or by an unbound runtime component.

## Repair

A new fail-closed provider budget ledger is implemented in `research_pipeline/e2_r17_provider_budget.py`.

- SQLite `BEGIN IMMEDIATE` serializes concurrent claims.
- Every generation call must claim budget transactionally before provider I/O.
- Claims are bound to the exact contract SHA, authorization SHA, global limit, and per-unit limit.
- Claims are never released after provider error/crash, deliberately over-counting ambiguous calls so resume cannot reset possible provider consumption.
- `ArkPlanReactLLM` records the claim id, per-unit call index, and global claimed count in every successful provider receipt.
- Each completed trajectory records its claim bundle hash and the unit/global counter state in `r17_trajectory_ref.json`.
- Resume revalidates the ledger/ref binding before reusing a completed trajectory.
- The E1-A orchestrator uses one shared ledger at `RUN_ROOT/checkpoints/provider_budget.sqlite3` across all stream subprocesses.

## Defense-in-depth repairs

The revised contract also binds SHA-256 for the budget ledger, Ark adapter, actor-pool resume path, search-pool schema, actor runner, orchestrator, support adjudicator, and budget tests. Authorization scope additionally binds resolved model identity, identity-artifact SHA, max turns, max output tokens, and exact provider-budget limits.

The support adjudicator now recomputes per-stream mixed counts and per-family support directly from all 96 exact frozen K=8 pools rather than trusting summary intermediates.

## Zero-provider tests

Command:

`python3 -m unittest research_pipeline.test_e2_r17_provider_budget research_pipeline.test_e2_r17_ark_plan_react research_pipeline.test_e2_r17_search_projection_runner research_pipeline.test_e2_r17_actor_authority_scope`

Result: 21/21 PASS.

Specific P0 assertions:

- the 11th generation attempt for one rollout is rejected before provider I/O;
- after 7680 global claims, the 7681st generation attempt is rejected before provider I/O;
- contract/authorization drift on an existing ledger fails closed.

No benchmark outcome, updater effect, future-skill utility, or method comparison was inspected to design this repair.

## Current authority

The repair may be independently reviewed. It does not authorize E1-A execution. A fresh dual pre-execution PASS is required before minting a frozen E1-A contract and separate authorization.
