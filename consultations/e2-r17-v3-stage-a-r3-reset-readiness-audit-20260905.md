# E2-R17 V3 Stage-A R3 provider-reset readiness audit

Date: 2026-09-05
Class: ZERO-PROVIDER CONTROL-PLANE AUDIT
Scientific outcome authority: false
Stage-A support-read authority: false
Stage-B authority: false

## Verdict

`PASS_ZERO_PROVIDER_R3_RESET_READINESS_WAIT_PROVIDER_RESET`

The R3 matched-censor recovery object is structurally ready for the already-reviewed post-reset sequence, but no provider call, fresh R3 identity, recovery authorization, recovery runner, support read, or Stage-B action is legal before the frozen provider-reset boundary:

`2026-09-07 00:00:00 +0800`

This audit does not inspect Stage-A support or any scientific outcome.

## Canonical exact-hash bindings

- R3 recovery contract: `generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3-recovery-20260905.json`
  - SHA256 `3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085`
- R3 zero-provider preflight: `generated/e2-r17-semantic-transfer-v3-stage-a-preflight-r3-recovery-20260905.json`
  - SHA256 `56208e171b2524a01ec429618c7b018a4fee1a9a785028f024fee5a40bd10df2`
- R3 execution-unit manifest: `generated/e2-r17-semantic-transfer-v3-stage-a-r3-execution-units-20260905.json`
  - SHA256 `e3ba3eba68523c087f475511e3b639721743fb63ee88e5ccdc5a13e06447ea86`
- R3 opportunity manifest: `generated/e2-r17-semantic-transfer-v3-stage-a-r3-opportunity-manifest-20260905.json`
  - SHA256 `2a63142123afe631e8a919de05c2cbec3be2b2b78c5b46cf3857ee13841d56f9`
- exact-hash independent review receipt: `generated/e2-r17-v3-stage-a-r3-exact-hash-gpt56-review-20260905.json`
  - SHA256 `6fb37037cb6cb850a99da155fd65aff42b7fffb9a4a8e3bb658f32d557835c99`
- exact-hash PASS gate: `generated/e2-r17-v3-stage-a-r3-exact-hash-pass-gate-20260905.json`
  - SHA256 `a4ade82e32bbc33cc701c4cd20e94e700b39f739ce51494bf0855d8ed1071907`
- independent verdict: `PASS_TO_SEPARATE_R3_RECOVERY_AUTHORIZATION`, conditional on a fresh post-reset identity and local adjudication.

## Recovery geometry

The original Stage-A plan contains 160 task opportunities. R3 freezes exactly two exceptional units and preserves the remaining original task IDs:

- terminal post-dispatch technical missing: `r17-b21-cgwb-p0`;
- exact semantic-counterpart matched no-provider censor: `r17-b21-cgwp-p0`;
- provider-facing recovery task IDs: 158 unique original IDs;
- replacement task IDs: 0;
- replayed task IDs: 0;
- actor rollouts if all 158 recovery tasks seal at K=8: 1264;
- provider-interaction ceiling: 12640, because the frozen contract permits at most 10 provider interactions per rollout. The number 158 is a task count, not an API-call count.

Opportunity geometry is 7/7 only for the exact matched affected streams and 8 elsewhere. The absolute support threshold remains 4 mixed pools per stream. No support was inspected in this audit.

## Exact-once / lineage readiness

Static checks passed:

- R3 run root is absent: `/data/wyt/e2-r17-search-projection/runs/semantic-transfer-v3-stage-a-r3-matched-censor-20260905`;
- R3 global lease is absent: `/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-semantic-transfer-v3-stage-a-r3-matched-censor.json`;
- all frozen bound-code SHA256 values match the current files;
- frozen split-manifest binding matches;
- burn receipt binding matches;
- matched-censor receipt binding matches;
- one-missing independent recovery-review receipt binding matches;
- matched-censor independent review receipt binding matches;
- the old R2 lease is preserved as historical incident evidence, but its recorded PID/PGID are both dead; R3 uses a distinct run root and distinct lease and does not resume the old R2 runner.

The R3 runner requires the new R3 run root and lease to be absent before launch. It creates an exclusive lease and exact-once claim root, refuses overwrite/replay, and preserves the new R3 lease/lock on failure. There is no automatic recovery-of-recovery path.

## Static control tests

`research_pipeline.test_e2_r17_semantic_transfer_v3_r3_recovery`:

- `test_exact_once_scope_requires_158_manifest`: PASS
- `test_r3_authority_rejects_burned_and_censor`: PASS
- `test_stage_b_order_accepts_7_and_8_only`: PASS

Additional stale-identity negative test:

- supplied the already-passed R2 identity adjudication to the R3 authorizer;
- authorizer failed closed with `fresh R3 identity must be qualified after exact-hash preexecution review`;
- no R3 authorization file was minted.

All frozen R3 authorizer/runner/adjudicator/identity-adjudicator sources compile successfully without provider I/O.

## Reset-time boundary

The exact-hash review and PASS gate freeze:

`NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800`

This time boundary is a frozen control-plane policy gate rather than a newly added check inside the already-reviewed authorizer. The bound authorizer code must not be edited merely to hard-code the time, because doing so would change its frozen SHA and invalidate the exact-hash review. Execution must therefore check the wall-clock/reset condition externally before the one permitted fresh identity qualification.

## Exact post-reset sequence

Only after the reset boundary is satisfied:

1. perform exactly one fresh DeepSeek identity qualification for requested `deepseek-v4-pro`, with thinking disabled and provider retry limit 0;
2. require resolved identity exactly `deepseek-v4-pro-ga-260813`;
3. locally adjudicate that qualification to `PASS_CURRENT_REVIEW_TRANCHE`;
4. require the adjudicated identity timestamp to be later than the exact-hash independent review;
5. only if identity PASS, mint a separate single-use R3 recovery authorization with `scripts/authorize_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py`;
6. execute only the frozen 158-task provider universe with `scripts/run_e2_r17_semantic_transfer_v3_stage_a_r3_recovery.py`;
7. on successful terminal freeze, run the separately scoped equal-dose recovery adjudicator;
8. do not read Stage-A support until the recovery terminal boundary permits it;
9. Stage B remains separately closed and requires its own future freeze/review/authority.

## Current authority

Before the reset:

- fresh R3 identity provider call: forbidden;
- R3 recovery authorization: forbidden;
- R3 provider execution: forbidden;
- Stage-A support read: forbidden;
- updater: forbidden;
- heldout evaluation: forbidden;
- Stage-B execution: forbidden;
- public benchmark: forbidden.

No additional experiment, model, task replacement, replay, or workload expansion is justified before the reset.
