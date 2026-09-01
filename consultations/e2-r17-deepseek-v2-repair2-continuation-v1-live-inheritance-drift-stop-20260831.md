# E2-R17 DeepSeek Repair2 continuation V1 terminal stop

Status: `STOP_CONTINUATION_V1_LIVE_INHERITANCE_DRIFT_AND_COMPLETED_UNIT_REPLAY`

This is a protocol-integrity stop, not a scientific result. No partial effect or score was read, and the frozen analyzer was not run.

## What happened

A separately authorized host-shutdown resume of the original V3 root started at 2026-08-31T10:38:23Z with PID/PGID 584224. Continuation V1 later started from the same frozen 17-pair snapshot with PID/PGID 832381. The V3 resume had already appended the six remaining heldout tasks for both arms of `e1-ioc-00/rep1`; V1 then executed those same 12 arm-task units under its child authorization.

The replay proof is content-addressed: each parent partial-boundary manifest grew from 12 to 18 rows, while its first 12 raw rows still hash to the frozen manifest SHA. The six appended task IDs exactly equal V1's six task IDs per arm.

## Terminal technical state

- Last uncontaminated frozen boundary: 17 pairs, 36 learned states, 636 heldout units, 609 provider claims.
- V1: 0 updater calls, 0 new learned states, 12 replayed heldout units, 78 provider claims, 17 valid manifest rows, no full summary.
- V3 resume: 28 completed manifest rows, 58 learned states including the incomplete next pair, 1037 heldout completions including the incomplete next pair, and 3306 claims.
- V3 resume then failed at `e1-msp-01/rep0 / win_c / r17-b4-ska-p8`: four provider responses completed; the fifth claim received an explicit HTTP 429 `AccountQuotaExceeded`. This is not an ambiguous response, but retry authority is zero.
- All relevant runner/actor/provider processes are now dead. Both run roots and locks remain immutable evidence.

## Root cause and disposition

The root cause is a concurrent continuation-authority collision across two worktrees. V1's prospective gate bound the frozen inheritance artifact but did not revalidate live parent-run liveness and live partial-boundary manifest hashes immediately before provider I/O.

Continuation V1 is quarantined and excluded from any final manifest. The V3 resume root is preserved pending separate protocol-integrity adjudication. No restart, retry, V2, analyzer, effect reading, second model, or public benchmark is authorized.

Machine-readable evidence is in `generated/e2-r17-deepseek-v2-repair2-continuation-v1-live-inheritance-drift-replay-blocker-20260831.json`.
