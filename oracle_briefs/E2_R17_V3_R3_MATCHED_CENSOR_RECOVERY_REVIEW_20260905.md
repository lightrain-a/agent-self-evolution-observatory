# Independent adversarial narrow re-review — E2-R17 V3 recovery matched-censor exposure balance

Date: 2026-09-05
Role: fresh independent senior ICLR/NeurIPS/ICML agent-systems methodology reviewer

## Review scope

A prior independent recovery review already established:

- the burned task `r17-b21-cgwb-p0` is a valid single post-dispatch technical missing;
- it must never be replayed, reconstructed, or replaced;
- no Stage-A support/outcome has been read;
- a versioned recovery is scientifically possible;
- fresh model identity is required before resumed provider execution;
- Stage-B authority remains false.

Do NOT reopen those points unless the exposure-balance finding below directly invalidates them.

This review asks one new question only: because frozen Stage B consumes the full per-stream Stage-A pool set, should the exact semantic counterpart of the burned task also be prospectively censored to prevent a 7-vs-8 update-count difference from contaminating the procedural-vs-binding interaction?

End with exactly one verdict:

- `PASS_R3_MATCHED_CENSOR_RECOVERY`
- `KEEP_159_RECOVERY_WITHOUT_MATCHED_CENSOR`
- `REQUIRE_FRESH_PANEL_OR_STOP`

Then list only verdict-changing required fixes.

## 1. Frozen Stage-B fact omitted from the prior recovery packet

The frozen V3 scientific protocol states:

- WIN-C updater-visible evidence is the served winner on all eight update pools;
- MRW4 replaces winner evidence with a frozen rejected witness on exactly four treated mixed pools;
- on the other four pools MRW4 uses the same winner evidence as WIN-C;
- for each stream and replicate, both arms consume the same full Stage-A task/pool IDs in the same task-ID-keyed, arm-blind order.

Thus the original Stage B has 8 update opportunities per stream/state, not only 4.

## 2. Current missing unit and exact frozen counterpart

Burned task:
- `r17-b21-cgwb-p0`
- stream `stv3-cgwb-00`
- semantic type `INSTANCE_BINDING_LOCALIZATION`
- block 21
- profile index 0
- pair key `semantic-transfer-v3-pair|b21|cross_group_window|p0`

Exact pre-existing semantic counterpart:
- `r17-b21-cgwp-p0`
- stream `stv3-cgwp-00`
- semantic type `PROCEDURAL_TRANSFORMATION`
- block 21
- profile index 0
- same pair key `semantic-transfer-v3-pair|b21|cross_group_window|p0`

The two initial XLSX files are byte-identical:
`66e26351d4f79e022d0988a20f8409a0364d0eead932f8c7e6f81698c8a1cd7d`

This match was frozen in the suite metadata before any V3 provider execution or outcome.

## 3. Problem with literal 159 continuation

Under the already-approved literal one-missing continuation:

- `stv3-cgwb-00` would have 7 Stage-A pools and therefore 7 Stage-B update opportunities;
- `stv3-cgwp-00` would have 8 Stage-A pools and therefore 8 Stage-B update opportunities.

WIN-C and MRW4 remain paired within each stream, but the primary mechanism compares procedural and binding effects inside the matched skeleton. A semantic-cell difference in total update opportunities could therefore become an alternative explanation for the interaction in `cross_group_window`.

No support/mixedness/task outcome has been inspected; this issue was discovered solely by rereading the frozen Stage-B protocol after the provider quota failure.

## 4. Proposed R3 matched-censor recovery

Before any resumed provider call or support read, freeze a NEW R3 recovery object with:

### Terminal/excluded units

1. `r17-b21-cgwb-p0` = `TERMINAL_TECHNICAL_MISSING_POST_DISPATCH`
   - never replay
   - never replace
   - no partial content scientific use

2. `r17-b21-cgwp-p0` = `PROSPECTIVE_MATCHED_EXPOSURE_CENSOR_NO_PROVIDER_EXECUTION`
   - zero provider calls in recovery
   - not a technical missing
   - not a replacement
   - excluded deterministically because it is the exact frozen semantic counterpart of the burned task
   - excluded before any support or outcome read

### Recovery execution universe

- original planned tasks: 160
- burned missing: 1
- matched no-provider censor: 1
- remaining provider-executable original tasks: 158
- replacement tasks: 0
- replayed tasks: 0

### Stage-A support opportunity sets

Support is evaluated only over Stage-B-eligible observed pools:

- `stv3-cgwb-00`: 7 opportunities, require >=4 mixed;
- `stv3-cgwp-00`: 7 opportunities, require >=4 mixed;
- every other stream: 8 opportunities, require >=4 mixed.

The absolute count threshold remains 4 everywhere. No proportional reinterpretation is allowed.

### Stage-B if support later passes under a separate contract

- WIN-C and MRW4 use exactly the same task IDs within every stream;
- `stv3-cgwb-00`: 7 update pools in both arms;
- `stv3-cgwp-00`: 7 update pools in both arms;
- other 18 streams: 8 update pools in both arms;
- exactly 4 MRW4-treated mixed pools per stream = 80 treated pools total;
- untreated pools use WIN-C evidence in both arms;
- task order remains arm-blind and task-ID keyed;
- no Stage-B execution authority is granted by this recovery review.

The purpose is not to equalize every skeleton globally. It is to prevent the technical missing from creating a procedural-vs-binding update-count asymmetry inside the exact affected matched pair.

### Failure rule

Any additional attempted-but-unsealed provider-facing recovery unit causes STOP; no second missingness accommodation, replacement, or further matched censor is permitted.

## 5. Alternative: keep literal 159 recovery

The alternative is to keep the prior approved design:

- execute all 159 untouched original tasks;
- only binding stream `stv3-cgwb-00` has 7 pools;
- counterpart procedural stream `stv3-cgwp-00` has 8;
- preserve >=4 mixed per stream and 4 treated per stream.

Question: is within-stream WIN-C/MRW4 pairing sufficient to make this 7-vs-8 semantic-cell exposure difference harmless for the five-skeleton interaction, or is it a verdict-changing confound that should be eliminated prospectively?

## 6. Audit questions

A. Does the 7-vs-8 total Stage-B update-opportunity difference create a material alternative explanation for the procedural-vs-binding interaction even though each arm is paired within stream?

B. Is exact matched-censoring of `r17-b21-cgwp-p0` scientifically justified and sufficiently outcome-blind given the frozen pair key, block, profile index, matched skeleton, and byte-identical initial workbook?

C. Is it cleaner to skip the counterpart at provider acquisition entirely (158 execution units) rather than spend provider calls on a pool that is prospectively excluded from support and Stage B?

D. Does evaluating support on 7/7 opportunities for the matched binding/procedural streams and 8 for all others, with the absolute >=4 rule unchanged, preserve the confirmatory support gate?

E. If support passes, does the proposed 7/7 matched Stage-B pool count plus exactly 4 treated mixed pools per stream preserve the causal projection contrast and five-skeleton interaction better than literal 159 continuation?

F. Does this matched censor count as impermissible post-failure task replacement/selection, or is it a conservative deterministic censor that reduces researcher degrees of freedom because it is fixed solely by pre-existing pairing metadata?

G. What exact zero-provider fields/checks should be frozen in the R3 contract to prevent later abuse of the matched-censor exception?

## Required synthesis

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
