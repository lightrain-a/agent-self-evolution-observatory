# E2-R17 V3 Stage-A technical-missing recovery — concise independent review brief

Date: 2026-09-05
Role: fresh independent senior ICLR/NeurIPS/ICML agent-systems methodology reviewer.

Review ONLY the recovery protocol after a post-dispatch Ark quota failure. No Stage-A support outcome exists; no K=8 pool is sealed; support was never inspected; updater/heldout/Stage-B remain untouched. Do not request extra workload for appearance.

End with exactly one verdict:
- `PASS_RECOVER_WITH_ONE_TERMINAL_TECHNICAL_MISSING`
- `REQUIRE_FRESH_160_UNIT_R3_PANEL`
- `STOP_V3_STAGE_A_AFTER_TECHNICAL_FAILURE`

## Frozen pre-failure object

R2 contract SHA: `f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234`
Preflight SHA: `e257438bd482d4f2209a8321d4a222bd97acf2c03bff46a1d5513b55a42ca766`
Fresh identity: exactly one DeepSeek call, requested `deepseek-v4-pro`, resolved `deepseek-v4-pro-ga-260813`, retry=0, thinking disabled, no benchmark/scientific outcome access.
Identity adjudication: `PASS_CURRENT_REVIEW_TRANCHE`.
Stage-A authorization SHA: `3693c535fde74d31f51970bba079d73500fa9f37e092032617aeaad2d263ddbb`.
Stage-A only; updater=false, heldout=false, analyzer=false, Stage-B=false, public=false.

Original Stage-A design:
- 20 streams × 8 tasks = 160 task units;
- K=8 each;
- attempt marker written before provider I/O;
- replay=false; ambiguous recollection=false; replacement=false;
- all 160 pools sealed before support read;
- every stream must have >=4 mixed pools;
- exactly 4 mixed pools/stream selected by frozen hash rule if support passes.

## Failure facts

First stream/task: `stv3-cgwb-00` / `r17-b21-cgwb-p0`.
Attempt marker was created before provider I/O.
Provider-budget ledger then recorded four pre-I/O claims: rollout_0 call indexes 1,2,3; rollout_1 call index 1.
Run failed with Ark `AccountQuotaExceeded`; provider states weekly quota reset at `2026-09-07 00:00:00 +0800`.
This is definitely post-dispatch, so the task is burned under R2 exact-once semantics.

Fail-closed state:
- attempts=1
- sealed receipts=0
- K8 pools=0
- completed streams=0
- completed-stream manifest absent
- terminal Stage-A summary absent
- support inspected=false
- updater=0
- heldout=0
- Stage-B=0
- global lease + local lock preserved

No scientific task score, mixedness, support, or partial effect has been read.

## Option A — versioned one-missing recovery

Create a NEW R3 recovery contract before any more provider execution or support read:
1. permanently classify `r17-b21-cgwb-p0` as one `TERMINAL_TECHNICAL_MISSING_POST_DISPATCH`;
2. never replay it;
3. never replace it;
4. use none of its partial provider/model content scientifically;
5. keep the other 159 original task IDs unchanged;
6. after a fresh identity qualification + separate recovery authorization, run those remaining 159 exactly once;
7. affected stream has 7 observable pools; all other streams 8;
8. DO NOT relax the support count: every stream still needs >=4 mixed pools, so affected stream needs >=4 among 7;
9. if support passes, Stage-B treated dose stays exactly 4 pools/stream = 80 total;
10. any second post-dispatch technical missing causes STOP;
11. support stays closed until all 159 remaining units are terminal and the one technical-missing receipt is frozen;
12. terminal summary must say 160 planned = 159 sealed K8 pools + 1 technical missing, never “160 pools”.

Rationale: missingness came from provider-wide weekly quota on frozen execution order, before any support read; keeping >=4 as an absolute count makes the affected stream's gate weakly harder, not easier; no replacement avoids outcome-conditioned panel substitution.

## Option B — fresh 160-unit R3 panel

Abort R2 permanently and freeze a new outcome-blind 160-unit panel from untouched tasks, excluding all prior provider-exposed tasks, under a deterministic rule fixed before outcomes. Requires new contract/identity/review/authorization. This restores 8 opportunities per stream but changes the task panel after a technical failure.

## Option C — stop

Stop V3 Stage A entirely.

## Forbidden

Do NOT permit:
- replay/continue the burned task after quota reset;
- reconstruct its partial rollout;
- opportunistically switch provider/model/account to finish it;
- inspect partial content/task outcome/support before recovery choice;
- convenience/favorable replacement;
- post-outcome support-threshold relaxation.

## Questions

A. Is Option A confirmatorily valid, or does 159 pools + one fixed technical missing invalidate the design?
B. Does retaining >=4 mixed pools per stream prevent favorable relaxation of the 7-pool stream?
C. Is “one missing only, second missing => STOP” sufficient against iterative accommodation?
D. Does Option A preserve Stage-B equal dose and the five-skeleton interaction if support passes?
E. Is Option B scientifically cleaner, or does task-panel replacement create more researcher degrees of freedom?
F. Must the resumed tranche obtain a fresh model identity qualification?
G. What exact zero-provider recovery artifacts/checks are required before execution?

Return:
- `missingness_mechanism_assessment`
- `option_a_validity`
- `option_b_validity`
- `equal_dose_preservation`
- `support_gate_preservation`
- `fresh_identity_required`
- `r2_replay_allowed` (must be false)
- `stage_b_authority` (false)
- `additional_scientific_experiment_required_before_recovery`
- `immediate_action`
- `verdict_changing_fixes`

End with exactly one required verdict token.
