# E2-R17 V3 recovery — Stage-B exposure-balance diagnostic

Date: 2026-09-05
Status: `ZERO_PROVIDER_OUTCOME_BLIND_DIAGNOSTIC`

## Finding

The first recovery review correctly established that the burned binding task must never be replayed or replaced and that a one-missing continuation can preserve the absolute Stage-A support threshold. A further inspection of the already-frozen V3 Stage-B protocol identified one additional exposure-balance issue that was not stated in that review packet.

The R2 Stage-B protocol does **not** update only on the four MRW4-treated pools. For every stream and replicate, both WIN-C and MRW4 consume the same full set of eight Stage-A pool IDs in the same arm-blind order. MRW4 replaces the learner-visible winner evidence on exactly four frozen treated mixed pools and uses winner evidence on the other four.

Therefore, a 159-pool recovery in which only the burned binding stream has seven pools would produce:

- binding stream `stv3-cgwb-00`: 7 update opportunities per Stage-B state;
- its exact procedural counterpart stream `stv3-cgwp-00`: 8 update opportunities per Stage-B state.

Although the WIN-C/MRW4 comparison inside each stream would still be paired, the primary procedural-vs-binding interaction for `cross_group_window` could then be affected by a one-update exposure-count difference between semantic cells.

## Exact matched counterpart

Burned task:

- task: `r17-b21-cgwb-p0`
- stream: `stv3-cgwb-00`
- semantic type: `INSTANCE_BINDING_LOCALIZATION`
- block: 21
- profile index: 0
- pair key: `semantic-transfer-v3-pair|b21|cross_group_window|p0`

Pre-existing exact semantic counterpart:

- task: `r17-b21-cgwp-p0`
- stream: `stv3-cgwp-00`
- semantic type: `PROCEDURAL_TRANSFORMATION`
- block: 21
- profile index: 0
- pair key: `semantic-transfer-v3-pair|b21|cross_group_window|p0`

Their initial XLSX files are byte-identical:

`66e26351d4f79e022d0988a20f8409a0364d0eead932f8c7e6f81698c8a1cd7d`

This counterpart relation was frozen in suite metadata before any V3 provider outcome.

## Candidate minimal repair

A stricter matched-censor recovery would prospectively exclude the untouched procedural counterpart from resumed provider execution as an **outcome-blind matched exposure censor**, not as a technical missing and not as a replacement.

The recovery would then have:

- 160 originally planned task units;
- 1 terminal post-dispatch technical missing: `r17-b21-cgwb-p0`;
- 1 prospectively matched-censored no-provider unit: `r17-b21-cgwp-p0`;
- 158 remaining provider-executable original task IDs;
- no replacement tasks;
- no replay;
- no support or scientific outcome read before this decision.

Both matched b21 cross_group_window streams would then have seven observable Stage-A pools, while the other 18 streams retain eight.

To guarantee Stage-B equal treatment dose after this symmetric censoring, Stage-A support would be evaluated on the **Stage-B-eligible opportunity set**:

- `stv3-cgwb-00`: >=4 mixed among its seven non-missing pools;
- `stv3-cgwp-00`: >=4 mixed among its seven non-censored pools;
- all other streams: >=4 mixed among eight pools.

If support passes, Stage B would use:

- seven update pools for each of the two matched cross_group_window b21 streams;
- eight update pools for every other stream;
- exactly four MRW4-treated mixed pools per stream;
- identical task IDs and arm-blind ordering across WIN-C and MRW4 within every stream;
- equal update-opportunity count between procedural and binding cells within the affected matched pair.

The matched-censored procedural task would receive **zero provider calls** in the recovery tranche and would not be used for support, treatment selection, router scores, or Stage-B updates.

## Why this requires a narrow re-review

The already-passed one-missing review stated that the missing pool changed only qualification opportunity and did not create unequal Stage-B dose. The frozen V3 protocol shows that Stage B originally consumes all eight pools, so that statement was based on an incomplete description of Stage-B total update exposure.

This diagnostic does not reopen the burned-task rule or any scientific outcome. It only asks whether symmetric matched censoring is required to keep the primary semantic interaction free of an update-count imbalance.
