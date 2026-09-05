# E2-R17 V3 R3 matched-censor recovery — concise independent review

Date: 2026-09-05
Role: fresh independent senior ICLR/NeurIPS/ICML agent-systems reviewer.

A prior review already PASSed the following and these are not being reopened: burned task `r17-b21-cgwb-p0` is one exogenous post-dispatch Ark-quota technical missing; replay/reconstruction/replacement are forbidden; no Stage-A support/outcome has been read; recovery is possible under a new versioned contract; fresh identity is required before resumed provider execution; Stage-B authority=false.

This narrow review asks only whether an exact semantic counterpart should also be prospectively censored because frozen Stage B consumes the full per-stream Stage-A pool set.

End with exactly one verdict:
- `PASS_R3_MATCHED_CENSOR_RECOVERY`
- `KEEP_159_RECOVERY_WITHOUT_MATCHED_CENSOR`
- `REQUIRE_FRESH_PANEL_OR_STOP`

## Frozen Stage-B fact

Original V3 Stage B uses all Stage-A pools in each stream:
- WIN-C exposes winner evidence on all 8 update pools;
- MRW4 replaces winner evidence on exactly 4 treated mixed pools and uses winner evidence on the other 4;
- within each stream/replicate, WIN-C and MRW4 consume identical pool IDs in one arm-blind task-ID-keyed order.

Thus Stage B originally has 8 update opportunities per stream/state, not only 4.

## Burned task and exact counterpart

Burned binding task:
- `r17-b21-cgwb-p0`
- stream `stv3-cgwb-00`
- `INSTANCE_BINDING_LOCALIZATION`
- block 21, profile 0
- pair key `semantic-transfer-v3-pair|b21|cross_group_window|p0`

Exact procedural counterpart frozen before provider execution:
- `r17-b21-cgwp-p0`
- stream `stv3-cgwp-00`
- `PROCEDURAL_TRANSFORMATION`
- block 21, profile 0
- same pair key

Their initial XLSX files are byte-identical, SHA256:
`66e26351d4f79e022d0988a20f8409a0364d0eead932f8c7e6f81698c8a1cd7d`

No support/mixedness/task outcome has been inspected.

## Literal 159 recovery problem

If all other 159 tasks execute:
- binding stream `stv3-cgwb-00` has 7 Stage-B update opportunities;
- matched procedural stream `stv3-cgwp-00` has 8.

WIN-C/MRW4 remain paired within each stream, but the primary mechanism compares procedural-vs-binding effects inside the matched skeleton. A 7-vs-8 update-count difference could therefore be an alternative explanation for the interaction.

## Proposed matched-censor R3

Before any resumed provider call or support read:

1. `r17-b21-cgwb-p0` = `TERMINAL_TECHNICAL_MISSING_POST_DISPATCH`; never replay/replace/use partial content.
2. `r17-b21-cgwp-p0` = `PROSPECTIVE_MATCHED_EXPOSURE_CENSOR_NO_PROVIDER_EXECUTION`; zero provider calls, not a technical missing, no replacement; excluded solely because frozen pairing metadata makes it the exact counterpart.
3. Original planned tasks=160; burned=1; matched no-provider censor=1; remaining provider-executable original tasks=158; replacements=0; replays=0.
4. Stage-A support opportunity sets are Stage-B-eligible pools:
   - `stv3-cgwb-00`: 7 opportunities, require absolute >=4 mixed;
   - `stv3-cgwp-00`: 7 opportunities, require absolute >=4 mixed;
   - other 18 streams: 8 opportunities, require absolute >=4 mixed.
5. If support later passes under a separate Stage-B contract:
   - both affected matched streams use 7 update pools in both arms;
   - other streams use 8;
   - exactly 4 treated mixed pools per stream = 80 treated total;
   - within every stream WIN-C/MRW4 use identical pool IDs and arm-blind task-ID-keyed order.
6. Any additional attempted-but-unsealed recovery unit causes STOP. No second missingness accommodation or additional matched censor.
7. The matched-censored task is never used for support, treatment selection, router scores, or Stage-B updates.

Purpose: not to equalize every skeleton globally, but to prevent the technical failure from introducing a procedural-vs-binding update-count asymmetry inside the exact affected matched pair.

## Alternative

Keep prior literal 159 recovery: only `stv3-cgwb-00` has 7 pools; `stv3-cgwp-00` has 8; absolute >=4 support and 4 treated/stream remain.

## Questions

A. Is 7-vs-8 total update exposure a material alternative explanation for the procedural-vs-binding interaction despite within-stream arm pairing?
B. Is censoring the exact frozen counterpart sufficiently outcome-blind and scientifically justified?
C. Is it cleaner to skip its provider acquisition entirely (158 execution units) than spend calls on a prospectively excluded pool?
D. Does absolute >=4 support over 7/7 matched opportunities and 8 elsewhere preserve the support gate?
E. Does 7/7 matched Stage-B exposure plus 4 treated/stream preserve the causal projection contrast and interaction better than literal 159?
F. Is this a conservative deterministic censor rather than impermissible post-failure replacement/selection?
G. What fields/checks must prevent later abuse of this one matched-censor exception?

Return:
- `stage_b_exposure_confound_assessment`
- `matched_censor_validity`
- `provider_execution_unit_count`
- `support_opportunity_rule`
- `stage_b_update_opportunity_rule`
- `treated_dose_preservation`
- `researcher_degrees_of_freedom_assessment`
- `r2_burned_task_replay_allowed` = false
- `stage_b_authority` = false
- `fresh_identity_required` = true
- `immediate_action`
- `verdict_changing_fixes`

End with exactly one verdict token listed above.
