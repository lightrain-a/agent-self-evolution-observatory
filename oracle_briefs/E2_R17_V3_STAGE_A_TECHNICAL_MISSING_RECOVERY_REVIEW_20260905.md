# Independent adversarial recovery review — E2-R17 V3 Stage-A post-dispatch technical missing

Date: 2026-09-05
Role requested: fresh independent senior ICLR/NeurIPS/ICML agent-systems methodology reviewer

## 0. Review rule

This is a ZERO-PROVIDER recovery adjudication after the first authorized V3 Stage-A execution failed closed because the Ark Plan account hit a weekly quota. Do not infer any Stage-A support outcome, Stage-B learning effect, or paper claim. No complete K=8 pool exists and support has not been inspected.

Review only the scientifically valid recovery action. Do not reward extra workload for appearance. Do not permit replay of an already attempted provider-facing unit merely because the failure was technical.

End with exactly one verdict token:

- `PASS_RECOVER_WITH_ONE_TERMINAL_TECHNICAL_MISSING`
- `REQUIRE_FRESH_160_UNIT_R3_PANEL`
- `STOP_V3_STAGE_A_AFTER_TECHNICAL_FAILURE`

Then list only verdict-changing required fixes.

## 1. Frozen scientific object before execution

Branch HEAD at authorization freeze:
`5b0a0ae274b1d4a18d308dba66c071e99a15e0c1`

Frozen R2 scientific contract:
- path: `generated/e2-r17-semantic-transfer-v3-stage-a-contract-r2-20260903.json`
- SHA256: `f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234`

Frozen preflight:
- SHA256: `e257438bd482d4f2209a8321d4a222bd97acf2c03bff46a1d5513b55a42ca766`

Fresh model identity qualification:
- one DeepSeek generation call only
- requested: `deepseek-v4-pro`
- resolved: `deepseek-v4-pro-ga-260813`
- retry: 0
- thinking: disabled
- benchmark data accessed: false
- scientific outcome accessed: false
- qualification SHA256: `fafb9606edc436823876ec5b9c4e2a1fe9628a12968b14099d29407a5f2f0a0a`

Local exact-identity adjudication:
- status: `PASS_CURRENT_REVIEW_TRANCHE`
- SHA256: `5e8e81a79828832b3c976ec1827ce54911cfd335be8dad35d459634b4d32ffd6`

Single-use Stage-A authorization:
- status: `AUTHORIZED_SEMANTIC_TRANSFER_V3_STAGE_A`
- SHA256: `3693c535fde74d31f51970bba079d73500fa9f37e092032617aeaad2d263ddbb`
- Stage-A provider execution: true
- updater: false
- heldout: false
- analyzer: false
- Stage B: false
- public benchmark: false

## 2. Original exact-once invariant

The frozen R2 contract requires:

- 160 predeclared Stage-A task units;
- immutable attempt marker created with `O_CREAT|O_EXCL` + fsync before any provider I/O;
- one frozen K=8 pool and immutable sealed receipt for every task;
- all 160 pools sealed before any support read;
- replay forbidden;
- ambiguous recollection forbidden;
- replacement sampling forbidden;
- attempted-but-unsealed unit is burned and requires separate adjudication.

Equal-dose support gate:

- 20 streams;
- 8 task pools per stream under the original design;
- each stream must have at least 4 mixed K=8 pools;
- exactly 4 mixed pools per stream are then selected by the frozen hash rule;
- no updater or heldout access occurs in Stage A.

## 3. What actually happened

Stage-A first-run runner was started under the exact authorization above.

The first stream was `stv3-cgwb-00`.
The first task was `r17-b21-cgwb-p0`.

Before provider I/O, its immutable task attempt marker was successfully created.

The provider budget ledger then recorded four pre-I/O claims:

- `r17-b21-cgwb-p0/rollout_0`, call indexes 1, 2, 3;
- `r17-b21-cgwb-p0/rollout_1`, call index 1.

The run then failed with Ark HTTP 429:

`AccountQuotaExceeded`: weekly plan usage quota exhausted; provider message states reset at `2026-09-07 00:00:00 +0800`.

This is definitely post-dispatch. It must NOT be treated as a request that never reached the provider.

Fail-closed state at diagnosis:

- attempt markers: 1
- sealed task receipts: 0
- frozen `pool_k8.json` files: 0
- completed stream summaries: 0
- completed-stream manifest: absent
- terminal Stage-A summary: absent
- global lease preserved as `RUNNING_STAGE_A_V3`
- local lock preserved
- support inspected: false
- updater calls: 0
- heldout access: 0
- Stage-B execution: 0

Failure receipt SHA256:
`fc7dfd6ba7a95e00aceddc0fdc16699ca4db0bafb91826b826978fa55dfd16af`

Attempt marker SHA256:
`db658bd5e13995f534987d7703c7f22dd874b96d9bbffcd6cc042295829c0092`

Provider-budget ledger SHA256 at diagnosis:
`1b033c1012ab46a63d0eab3e1e2b8930d054499968d5db5d90761c8b4d5d4a15`

No K=8 pool outcome exists for the burned task and no other task has been attempted.

## 4. Recovery options under review

### Option A — versioned recovery with one terminal technical missing

Create a NEW R3 recovery contract/runner/authorization that binds the existing R2 failure state and does all of the following prospectively, before any further provider execution or support read:

1. `r17-b21-cgwb-p0` becomes exactly one `TERMINAL_TECHNICAL_MISSING_POST_DISPATCH` task.
2. It is never replayed.
3. It is never replaced by another task.
4. No partial trajectory/content from that task is used scientifically.
5. The remaining 159 predeclared task IDs are unchanged and may execute exactly once after a fresh model identity qualification and separate recovery authorization.
6. The affected stream therefore has at most 7 observable K=8 pools; all other streams retain 8.
7. The original support COUNT threshold is NOT relaxed: every one of the 20 streams must still contain at least 4 mixed observed pools. In the affected stream, this means >=4 mixed among the remaining 7.
8. The frozen treated dose remains exactly 4 mixed pools per stream if the gate passes, so Stage B remains 80 treated pools total.
9. Any second post-dispatch technical missing anywhere in Stage A causes STOP; no additional missingness relaxation is permitted.
10. Support is not read until all 159 remaining task units are terminal and the one fixed technical-missing receipt is sealed.
11. The terminal Stage-A summary reports 160 planned units = 159 sealed K8 pools + 1 terminal technical missing, and never pretends that 160 pools exist.
12. Stage B remains separately unauthorized.

Scientific rationale proposed for review:

- missingness was caused by a provider-wide weekly quota boundary, not by observed task success/failure or mixedness;
- execution order was frozen before outcomes;
- no pool/support outcome was read before the failure;
- keeping the same >=4 mixed-pool count makes the affected stream's support gate weakly harder, not easier;
- equal Stage-B treatment dose remains 4 pools/stream if Stage A passes;
- no replacement avoids outcome-conditioned panel substitution.

### Option B — fresh 160-unit R3 panel

Declare current R2 Stage A permanently aborted. Before any support read, create a new outcome-blind 160-unit Stage-A panel using a deterministic, prospectively documented rule from the original untouched task universe, excluding every task with prior provider exposure. Run the new panel from scratch under a new contract, identity qualification, independent review, and authorization.

This avoids unequal 7-vs-8 Stage-A opportunity counts, but changes the frozen task panel after a technical failure and costs a full new acquisition tranche. Any deterministic replacement/panel rule must be fixed without using task outcomes, hidden semantic labels, or support statistics.

### Option C — stop V3 Stage A

Treat the exact-once burn as terminal for the whole V3 experiment and do not attempt recovery.

## 5. Explicitly forbidden recovery

The following is NOT an admissible option:

- wait for quota reset and rerun `r17-b21-cgwb-p0`;
- reconstruct or continue its partially exposed rollout;
- swap API/provider/model/account opportunistically to finish that unit;
- inspect any partial model content or task score to decide recovery;
- replace the missing task based on convenience or favorable similarity;
- relax the >=4 mixed-pools-per-stream threshold after seeing support.

## 6. Questions to adjudicate

A. Is Option A scientifically valid given the exact-once purpose, or does changing `160 sealed pools` to `159 sealed pools + 1 fixed terminal technical missing` destroy the confirmatory design?

B. Does keeping the absolute support threshold at >=4 mixed pools in every stream sufficiently prevent the affected 7-pool stream from receiving a favorable relaxation?

C. Is the one-missing-only cap plus STOP on any second post-dispatch technical missing sufficient to prevent iterative missingness accommodation?

D. Does Option A preserve Stage-B equal dose and the five-skeleton causal interaction if the support gate passes?

E. Would Option B actually be scientifically cleaner, or would changing the frozen task panel after a provider failure create more researcher degrees of freedom than Option A?

F. Is a fresh model identity qualification required immediately before any resumed provider tranche because the existing qualification was consumed for the failed R2 attempt?

G. What exact recovery artifacts/checks must exist before any new provider execution?

## 7. Required output synthesis

Return:

- `missingness_mechanism_assessment`
- `option_a_validity`
- `option_b_validity`
- `equal_dose_preservation`
- `support_gate_preservation`
- `fresh_identity_required`
- `r2_replay_allowed` = must remain false
- `stage_b_authority` = false
- `additional_scientific_experiment_required_before_recovery` = yes/no
- `immediate_action`
- `verdict_changing_fixes`

End with exactly one verdict token from section 0.
