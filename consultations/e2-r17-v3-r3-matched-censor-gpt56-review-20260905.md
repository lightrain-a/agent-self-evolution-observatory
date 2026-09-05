# Independent GPT-5.6 Sol review — E2-R17 V3 R3 matched-censor recovery

Date: 2026-09-05
Surface: ChatGPT web
Model: GPT-5.6 Sol
Thinking: Extra High (4/5)
Conversation: https://chatgpt.com/c/6a9c1c47-0194-83ee-b706-35f5d832acaf
Prompt packet SHA256: `dbac105ae0f9f2ee9da1846ec905efb6f28c691d9083de39e7d039362ce3fabd`

### A. Stage-B exposure-count confound assessment

`7-vs-8` is a **material alternative explanation** for the procedural-vs-binding interaction.

Within-stream WIN-C/MRW4 pairing protects the arm contrast *inside* each stream, but it does not remove a systematic difference in the number of Stage-B update opportunities between the two members of the affected procedural/binding matched skeleton. Because the scientific comparison includes procedural-vs-binding effects, retaining 7 opportunities for `stv3-cgwb-00` and 8 for `stv3-cgwp-00` leaves exposure count partially aliased with mechanism type.

Therefore literal 159 recovery is scientifically weaker than symmetric matched censoring.

### B. Matched-censor validity

Yes. Censoring `r17-b21-cgwp-p0` is sufficiently outcome-blind and scientifically justified because the censor is determined entirely from **pre-existing frozen metadata**:

* exact same pair key;
* block/profile correspondence;
* predefined procedural-vs-binding role;
* byte-identical initial XLSX;
* decision made before resumed provider execution or support inspection.

It does not depend on support, mixedness, router scores, or any outcome. The rule therefore removes an exposure asymmetry rather than selecting observations based on realized data.

### C. Provider execution unit count

The scientifically cleaner execution count is:

`158 provider-executable original tasks`

with:

* original planned = 160;
* burned technical missing = 1;
* prospective matched no-provider censor = 1;
* replacements = 0;
* replays = 0.

Executing the known-to-be-excluded counterpart would add provider cost and another post-censor artifact without contributing admissible evidence. Skipping acquisition entirely is cleaner.

### D. Support opportunity rule

The proposed rule is valid:

* `stv3-cgwb-00`: 7 eligible opportunities, absolute support threshold `>=4 mixed`;
* `stv3-cgwp-00`: 7 eligible opportunities, absolute support threshold `>=4 mixed`;
* all other 18 streams: 8 eligible opportunities, absolute threshold `>=4 mixed`.

This preserves the intended **absolute support requirement** rather than silently converting the threshold into a different proportional criterion. Most importantly for this recovery, the two members of the affected matched skeleton have identical support opportunity counts.

No support result is implied by this assessment.

### E. Stage-B update opportunity rule / treated-dose preservation

The R3 configuration is preferable:

* affected matched pair: `7 / 7` total Stage-B update opportunities;
* other streams: `8`;
* WIN-C and MRW4 use identical eligible pool IDs within every stream;
* MRW4 treats exactly 4 mixed pools per stream;
* total treated dose remains exactly `20 × 4 = 80`.

This preserves the causal projection contrast better than literal 159 because the procedural-vs-binding interaction is no longer accompanied by a 7-vs-8 exposure-count difference.

The fact that the affected pair has 7 rather than 8 opportunities does not itself invalidate the interaction: the reduction is **symmetric within the exact matched comparison**.

### F. Researcher degrees of freedom assessment

This is a **conservative deterministic censor**, not a replacement or opportunistic post-failure selection.

The distinction is important:

* nothing is substituted for the burned task;
* no new candidate is selected;
* no observed result determines which counterpart is removed;
* the counterpart is uniquely identified by frozen pairing metadata;
* the censor reduces usable data rather than recovering lost information;
* the exception is explicitly limited to one matched counterpart;
* any further attempted-but-unsealed recovery unit triggers STOP.

Those properties substantially constrain researcher degrees of freedom.

### G. Required anti-abuse fields/checks

The recovery record should enforce, at minimum:

* burned task ID and immutable status `r17-b21-cgwb-p0 = TERMINAL_TECHNICAL_MISSING_POST_DISPATCH`;
* matched-censor task ID and immutable status `r17-b21-cgwp-p0 = PROSPECTIVE_MATCHED_EXPOSURE_CENSOR_NO_PROVIDER_EXECUTION`;
* frozen `pair_key`, block, profile, stream, and semantic-role mapping;
* pre-recovery contract/version/hash establishing that the censor rule preceded resumed execution/support inspection;
* provider-call count for the censored task fixed at `0`;
* explicit prohibition on response acquisition, replay, reconstruction, or replacement for that task;
* exclusion flags for support, mixedness qualification, treatment selection, router scoring, and Stage-B updates;
* per-stream eligible-opportunity counts verifying affected streams are exactly `7/7`;
* Stage-B arm check verifying WIN-C/MRW4 use identical eligible pool IDs and identical arm-blind ordering within each stream;
* treated-count check enforcing exactly `4` treated mixed pools per stream and `80` total;
* recovery-exception counter enforcing exactly one burned unit plus exactly one deterministic matched censor;
* STOP invariant on any additional attempted-but-unsealed recovery unit.

### Required synthesis

- `stage_b_exposure_confound_assessment`: `MATERIAL_UNDER_LITERAL_159`
- `matched_censor_validity`: `VALID_OUTCOME_BLIND_DETERMINISTIC_MATCHED_CENSOR`
- `provider_execution_unit_count`: `158`
- `support_opportunity_rule`: affected exact matched streams = 7 opportunities each with absolute >=4 mixed; other 18 streams = 8 opportunities each with absolute >=4 mixed
- `stage_b_update_opportunity_rule`: if separately authorized later, affected matched streams use 7 eligible update pools in both arms; all other streams use 8; within-stream arm pool IDs/order remain identical
- `treated_dose_preservation`: exactly 4 treated mixed pools per stream; 80 treated total
- `researcher_degrees_of_freedom_assessment`: LOW/CONTROLLED
- `r2_burned_task_replay_allowed`: false
- `stage_b_authority`: false
- `fresh_identity_required`: true
- `immediate_action`: version the recovery contract with the exact matched censor frozen; mark the counterpart no-provider-execution; enforce 158 executable units and the 7/7 affected-pair opportunity geometry before any resumed provider call
- `verdict_changing_fixes`: none beyond making the stated matched-censor invariants machine/audit enforceable; literal 159 should not be retained if the frozen procedural-vs-binding interaction remains the target comparison

`PASS_R3_MATCHED_CENSOR_RECOVERY`
