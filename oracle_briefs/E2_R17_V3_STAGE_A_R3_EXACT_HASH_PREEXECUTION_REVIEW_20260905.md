# Independent exact-hash pre-execution review — E2-R17 V3 Stage-A R3 matched-censor recovery

Date: 2026-09-05
Role: fresh independent senior ICLR/NeurIPS/ICML agent-systems methodology reviewer

## 0. Review rule

This is a ZERO-PROVIDER exact-hash review of the fully implemented R3 recovery object after the first R2 Stage-A provider-facing unit was burned by an Ark weekly-quota 429.

Do not infer Stage-A support, Stage-B effect, or paper outcome. No complete R2 K=8 pool exists and support has never been inspected. Do not reopen the already-adjudicated no-replay rule unless the frozen R3 implementation violates it. Do not request optional workload for appearance.

Review whether the exact frozen R3 contract/code/preflight safely permits a **separate future recovery authorization only after a fresh model-identity qualification**. This review itself grants no provider authority.

Required final verdict token, exactly one:
- `PASS_TO_SEPARATE_R3_RECOVERY_AUTHORIZATION`
- `REVISE_R3_RECOVERY_BEFORE_IDENTITY`
- `STOP_R3_RECOVERY`

If PASS, required execution recommendation:
`ALLOW_SEPARATE_R3_RECOVERY_AUTHORIZATION`

## 1. Exact frozen lineage

Repository commit:
`ed7bf44103037c3fe6dd525056a4ca03da31e610`

Frozen R2 scientific parent contract SHA256:
`f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234`

Frozen R2 preflight SHA256:
`e257438bd482d4f2209a8321d4a222bd97acf2c03bff46a1d5513b55a42ca766`

Frozen R3 recovery contract:
`generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3-recovery-20260905.json`

R3 contract SHA256:
`3d0db7078c073613a27bc643675aa8755c7b2f241345ef6371570be48f2dd085`

R3 zero-provider preflight:
`generated/e2-r17-semantic-transfer-v3-stage-a-preflight-r3-recovery-20260905.json`

R3 preflight SHA256:
`56208e171b2524a01ec429618c7b018a4fee1a9a785028f024fee5a40bd10df2`

Current R3 contract authority:
- stage_a_provider_execution=false
- stage_b_learning_execution=false
- updater=false
- heldout=false
- analyzer=false
- public benchmark=false
- paper promotion=false

R3 run root: absent.
R3 global lease: absent.
Failed R2 run root and its local lock remain preserved.

## 2. Frozen incident facts

Original authorized R2 Stage A executed exactly one first task attempt:

- stream: `stv3-cgwb-00`
- task: `r17-b21-cgwb-p0`
- semantic type: `INSTANCE_BINDING_LOCALIZATION`

Its exact-once attempt marker was written before provider I/O. The provider-budget ledger then recorded four pre-I/O claims across rollout 0 and rollout 1. The run failed with Ark `AccountQuotaExceeded`; provider message states reset at:

`2026-09-07 00:00:00 +0800`.

This is post-dispatch. The task is permanently burned.

Frozen incident SHAs:
- failure receipt: `fc7dfd6ba7a95e00aceddc0fdc16699ca4db0bafb91826b826978fa55dfd16af`
- burned attempt: `db658bd5e13995f534987d7703c7f22dd874b96d9bbffcd6cc042295829c0092`
- R2 provider-budget ledger: `1b033c1012ab46a63d0eab3e1e2b8930d054499968d5db5d90761c8b4d5d4a15`
- R2 local lock: `9ce9907141564d200883db7af4a836724ce7dddffe24e8a780da3178a14e42d4`
- R2 global lease: `dc9471b2b9986967c66fa74be17e7bfec3afb30541a57c72847daa0a01c25a2d`

R2 terminal scientific state at recovery design time:
- attempted markers=1
- sealed receipts=0
- complete K8 pools=0
- completed streams=0
- support inspected=false
- updater=0
- heldout=0
- Stage-B execution=0

No partial provider/model content, task score, mixedness, support result, or learning effect was used to choose recovery.

## 3. Independent recovery adjudications already completed

First recovery review verdict:
`PASS_RECOVER_WITH_ONE_TERMINAL_TECHNICAL_MISSING`

Second narrow exposure-balance review verdict:
`PASS_R3_MATCHED_CENSOR_RECOVERY`

The second review identified that literal 159 continuation would create a 7-vs-8 total Stage-B update-opportunity difference between the affected binding stream and its exact procedural counterpart, which is a material alternative explanation for the procedural-vs-binding interaction.

The exact frozen counterpart is:

- `r17-b21-cgwp-p0`
- stream `stv3-cgwp-00`
- semantic type `PROCEDURAL_TRANSFORMATION`
- same pair key `semantic-transfer-v3-pair|b21|cross_group_window|p0`
- same block/profile
- byte-identical initial XLSX with burned task, SHA256 `66e26351d4f79e022d0988a20f8409a0364d0eead932f8c7e6f81698c8a1cd7d`

The matched censor decision was made before any support/mixedness/task outcome read.

## 4. Frozen R3 geometry

Original planned Stage-A tasks: 160.

Exactly two prospectively frozen exceptions:

1. `r17-b21-cgwb-p0`
   = `TERMINAL_TECHNICAL_MISSING_POST_DISPATCH`
   - never replay
   - never continue/reconstruct
   - never replace
   - partial content scientifically unused

2. `r17-b21-cgwp-p0`
   = `PROSPECTIVE_MATCHED_EXPOSURE_CENSOR_NO_PROVIDER_EXECUTION`
   - zero provider calls
   - not a technical missing
   - not a replacement
   - support-ineligible
   - mixedness-ineligible
   - treatment-selection-ineligible
   - router-score-ineligible
   - Stage-B-update-ineligible

Provider-executable original tasks: exactly 158 unique IDs.
Replacement tasks: 0.
Replay tasks: 0.

Opportunity geometry:
- `stv3-cgwb-00`: 7 eligible pools
- `stv3-cgwp-00`: 7 eligible pools
- other 18 streams: 8 eligible pools each
- total provider-executable tasks: 158

Stage-A support rule remains an absolute count:
- every stream requires >=4 mixed eligible K8 pools
- no proportional reinterpretation
- support cannot be read until all 158 provider units are terminal/sealed

If support later passes under a separate Stage-B contract:
- affected matched streams each use 7 update pools in both WIN-C/MRW4
- other streams use 8
- WIN-C and MRW4 use identical eligible task IDs within every stream
- update order remains task-ID-keyed and arm-blind
- exactly 4 MRW4-treated mixed pools per stream = 80 treated pools total
- Stage-B authority remains false now

Any additional attempted-but-unsealed R3 provider-facing unit => `STOP`; no second missingness accommodation or further matched censor is allowed.

## 5. Secondary router repair

Because two streams prospectively have 7 opportunities rather than 8, the R3 secondary pre-learning reduction routers no longer rank raw counts.

Frozen before any R3 provider result:
- difficulty-only score = successful-rollout **rate** over Stage-B-eligible Stage-A opportunities
- mixedness-only score = mixed-pool **rate** over eligible opportunities
- raw-count scoring is forbidden in R3

This affects only secondary reduction-router baselines, not the primary absolute >=4 support gate or the five-skeleton interaction estimand.

## 6. R3 budget and exact-once boundary

R3 provider tranche:
- 158 tasks × K=8 = 1264 actor rollouts
- provider-call ceiling = 12,640
- per-rollout call ceiling = 10

Failed R2 tranche had 4 pre-I/O claims.
Even at the full R3 maximum, combined claims are bounded by 12,644, below the original R2 ceiling of 12,800.

R3 actor requires:
- exact authorization status `AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY`
- recovery mode `MATCHED_CENSOR_158`
- exactly 158 allowed task IDs
- exact K=8
- exact prefix K=(1,2,4,8)
- concurrency=1
- initial skill only
- resolved model `deepseek-v4-pro-ga-260813`
- exact R3 run root and active R3 lease
- 158-unit exact-once manifest

The actor rejects the burned task and matched-censor task because neither exists in the allowed execution universe.

R3 runner:
- explicitly passes only the per-stream allowed task IDs
- writes new exact-once attempt markers before provider I/O
- accepts 7 tasks for the two affected streams and 8 for the other streams
- any new attempted-but-unsealed failure is fail-closed with STOP policy
- no automatic resume
- no task replacement
- no support read

R3 support adjudicator:
- runs only after terminal 158-pool recovery summary
- verifies 7/7/8 opportunity geometry
- keeps absolute >=4 support
- freezes exactly four treated mixed pools per stream if PASS
- emits 80 treated pools total if PASS
- never grants Stage-B execution authority

## 7. Exact bound-code hashes

All contract-bound code hashes were rechecked after contract creation and match exactly:

- R3 actor: `1bffcc3c24e2240a918efa062d8cf6c0262503ce3358ed1265cdbce53736a1f6`
- R3 authorization minter: `9866bcffb09b4d6a6f31c5c8e947c6107a8bf35e09b8ddc81a6ef6350d6278df`
- R3 control tests: `17d13bfe6852c9d51cf6be5f91752900c9cd32f54c046f463a563ab4024a4605`
- R3 equal-dose adjudicator: `e326ee92f7765aa68856c6fe09610996209d4aa3d3ad464a65d391a88a4cbae4`
- legacy stream verifier: `24ea070b08399d48af99294615a508874f851af941f5bb0efabe341b0854617d`
- R3 preflight: `320462d4e0b5033d1c97fb2575b883a377255ac558515018ae2b016caf3d463c`
- frozen R2 actor base: `28a21f55c5f641d555eecf66f146fd1414720b19e1a5affbb422a0229a543500`
- frozen R2 runner base: `267d9dd31e197d6c1d4e7c7bebbbbf0127571a2d209c9e722ebfefbe7c1bcc96`
- R3 Stage-A runner: `491b2ae6e53fcfe732f15ef263cc365ce61846b3219d7a13fe70e3834f6d3c89`
- R3 Stage-B order helper: `9593d9abd69ff2198b7958f98f0191a0c886343d20dcdaa4ffe40620f1b793cf`

Control tests: 3/3 PASS.
All R3 Python files compile.
`git diff --check`: PASS.

## 8. R3 preflight result

Preflight status:
`PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_V3_STAGE_A_R3_RECOVERY_PREFLIGHT`

All checks true:
- parent_incident_binding_pass
- matched_censor_binding_pass
- provider_manifest_pass
- opportunity_geometry_pass
- actor_scope_guards_pass
- runner_compile_pass
- adjudicator_compile_pass
- authorizer_compile_pass
- actor_compile_pass
- stage_b_order_compile_pass
- stage_b_order_7_8_pass

Preflight provider calls: 0.
Scientific execution: false.
Support inspected: false.
Fresh identity qualified for R3: false.

## 9. Current provider constraint

The provider explicitly reported that the weekly plan quota resets at:
`2026-09-07 00:00:00 +0800`.

Therefore, even if this review passes, the immediate safe control-plane action on 2026-09-05 is **not** to issue a fresh identity call while the quota is known exhausted. The fresh identity must occur only after the provider quota is available again, and must be fresh relative to this exact-hash review.

## 10. Audit questions

A. Does the exact frozen R3 geometry preserve the primary procedural-vs-binding interaction better than literal 159 continuation, without creating outcome-conditioned selection?

B. Are the burn + exact matched no-provider censor safeguards sufficiently narrow and machine-enforced?

C. Does support remain confirmatory under 7/7/8 opportunities with an unchanged absolute >=4 mixed threshold?

D. Does the future Stage-B 7/7 matched exposure geometry preserve the within-stream projection contrast and the matched-skeleton interaction, assuming Stage A support later passes and Stage B is separately frozen/reviewed?

E. Is opportunity-normalizing only the two secondary reduction-router scores the correct way to avoid 7/8 raw-count bias without weakening the primary support gate?

F. Are exact-once, STOP-on-second-missing, provider-budget, no-replay/no-replacement, heldout/updater/Stage-B authority boundaries adequately enforced by the frozen code/preflight?

G. Is any verdict-changing zero-provider defect still present before a future fresh identity qualification?

H. Given the known provider reset time, should the PASS path be: exact-hash review PASS now -> no provider call before reset -> fresh identity after reset -> local identity adjudication -> separate R3 recovery authorization?

## 11. Required output schema

Return exactly these fields before the final verdict:

- `contract_sha256_acknowledged`
- `preflight_sha256_acknowledged`
- `matched_censor_geometry`
- `support_gate_validity`
- `stage_b_exposure_balance`
- `secondary_router_normalization`
- `exact_once_recovery_integrity`
- `provider_budget_integrity`
- `remaining_blockers`
- `scientific_authority` = false
- `experiment_authority` = false
- `stage_b_authority` = false
- `paper_claim_authority` = false
- `execution_recommendation`
- `immediate_control_plane_action`

If and only if no verdict-changing blocker remains:
- `remaining_blockers` must be `[]`
- `execution_recommendation` must be `ALLOW_SEPARATE_R3_RECOVERY_AUTHORIZATION`
- `immediate_control_plane_action` should preserve the known provider-reset boundary and require a fresh identity after reset.

End with exactly one verdict token from section 0.
