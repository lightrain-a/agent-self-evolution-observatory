# E2-R17 M3R — exact-evidence frozen-state regeneration audit

Status: **PROPOSAL_ONLY / ZERO_PROVIDER / NO_EXECUTION_AUTHORITY**

Purpose: replace the lower-information plan to remeasure only G0 plus an M2-selected manual state with a direct actor-noise/comparator audit of the already-existing exact-evidence states. This proposal does not modify or authorize M2 Recovery V3.

## 1. Scientific question

The completed exact-evidence replay generated two different First-Fail persistent states from reconstructed byte-identical learner-visible evidence, but each state was originally measured through a fresh actor realization and against a contemporaneous WIN-C run. M3R asks:

> Does the behavioral separation among the already-generated same-evidence First-Fail states persist when their bytes are frozen, the actor is re-run, and all states are compared against one common byte-identical WIN-C artifact?

No updater call is required.

## 2. Frozen states

All state files and updater receipts already exist and are content-addressed.

### Historical First-Fail (`FF_HIST`)

- skill path: `/data/wyt/e2-r17-search-projection/runs/single-case-diagnostic-witness-s1-20260902/states/e1-tsr-00/replicate_0/first_fail/update/skill_post/SKILL.md`
- skill SHA-256: `97e28b4862ed5817929fa6014eb1ba1401667875d80e03d18c0b54978a185252`
- update receipt SHA-256: `e5fefbe7070fc4afbad9a62a7d175806cab011b64578bca0ee52cfedc4999ab9`

### Fresh First-Fail realization 1 (`FF_R1`)

- skill path: `/data/wyt/e2-r17-search-projection/runs/single-case-first-fail-exact-replay-20260902/states/e1-tsr-00/replicate_1/first_fail/update/skill_post/SKILL.md`
- skill SHA-256: `596bd30b49935d16f35d51e9eed36e19567332cd8a9104ae50d832f91ffdf04f`
- update receipt SHA-256: `332fd5d3a265c01c3be5887fa3e8f40c37d1f0e5c5825840a8fddc257b83a5c1`

### Fresh First-Fail realization 2 (`FF_R2`)

- skill path: `/data/wyt/e2-r17-search-projection/runs/single-case-first-fail-exact-replay-updater-recovery-v2-20260902/states/e1-tsr-00/replicate_2/first_fail/update/skill_post/SKILL.md`
- skill SHA-256: `fb5454a27faf8182ba1b0d722273c4377d4762815cd1898c3780cc8ff336615e`
- update receipt SHA-256: `acf25c85f672010ccb0203365c309e53c574ea7840f81808c26a837f6d4e1cfa`

### Common WIN-C (`WIN_COMMON`)

- canonical skill path: `/data/wyt/e2-r17-search-projection/runs/single-case-diagnostic-witness-s1-20260902/states/e1-tsr-00/replicate_0/win_c/update/skill_post/SKILL.md`
- skill SHA-256: `6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649`
- historical receipt SHA-256: `eb1dfc4d2849205b7ddca2cc6f006031501770eb146a70076799e46266fbe08d`

The exact-replay replicate-1 and replicate-2 WIN-C updater artifacts independently resolve to the same skill SHA-256 `6df40f...c00649`. Therefore the comparator state is byte-identical across the historical and fresh updater lineages; M3R uses one canonical frozen artifact rather than allowing fresh comparator-state drift.

## 3. Frozen task panel

Use the exact same 18 development held-out tasks as the original exact-evidence replay measurement:

- `r17-b4-agj-p2`, `r17-b4-agj-p3`, `r17-b4-agj-p8`
- `r17-b4-fmv-p1`, `r17-b4-fmv-p2`, `r17-b4-fmv-p8`
- `r17-b4-ioc-p1`, `r17-b4-ioc-p4`, `r17-b4-ioc-p6`
- `r17-b4-msp-p0`, `r17-b4-msp-p7`, `r17-b4-msp-p8`
- `r17-b4-ska-p4`, `r17-b4-ska-p5`, `r17-b4-ska-p8`
- `r17-b4-tsr-p0`, `r17-b4-tsr-p6`, `r17-b4-tsr-p8`

Suite root: `/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2`

- suite manifest SHA-256: `2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4`
- split manifest SHA-256: `aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9`

This is still the outcome-selected development panel. M3R reduces actor/comparator ambiguity; it does not repair selected-case bias or create independent confirmation.

## 4. Actor/runtime contract

Reuse the exact actor measurement configuration:

- requested model: `deepseek-v4-pro`
- required resolved model: `deepseek-v4-pro-ga-260813`
- thinking: disabled
- temperature: 0
- K: 1
- max turns: 10
- max output tokens: 8192
- provider retry limit: 0
- same deterministic SpreadsheetBench verifier/runtime
- fresh/reset task runtime per state × task
- state order hash-balanced by task under a new pre-frozen salt
- no updater calls
- no extra actor replicate after outcomes

## 5. Minimal new measurement

Execute exactly **one new contemporaneous actor remeasurement** for every frozen state × held-out task:

- 4 frozen states × 18 tasks = **72 new actor units**.

The original exact-replay actor results remain the first observation for `FF_R1` and `FF_R2`; this one frozen-state remeasurement provides the second observation needed for a minimal between-state-vs-within-state diagnostic. Historical frozen-state measurements remain background evidence and are not replayed.

No new state synthesis is allowed.

## 6. Primary regeneration diagnostic

For each task `q`:

- `A1(q)`: original actor result for `FF_R1`;
- `A2(q)`: new M3R frozen-state result for `FF_R1`;
- `B1(q)`: original actor result for `FF_R2`;
- `B2(q)`: new M3R frozen-state result for `FF_R2`.

Define

`D_U = mean_q | mean(A1,A2) - mean(B1,B2) |`

and

`D_A = 0.5 * mean_q [ |A1-A2| + |B1-B2| ]`.

`D_U` is disagreement between two independently synthesized same-evidence First-Fail states after averaging their two actor observations. `D_A` is within-frozen-state actor disagreement.

Development-only support for state-regeneration instability requires:

`D_U - D_A > 0`.

Also report, without a separate claim gate:

- new-remeasurement aggregate utilities of `FF_HIST`, `FF_R1`, `FF_R2`, `WIN_COMMON`;
- each First-Fail state minus the same contemporaneous `WIN_COMMON` utility;
- whether the original aggregate ordering `FF_R1 > FF_R2` remains strict in the new remeasurement;
- task-level and family-level disagreement diagnostics.

The independent scientific unit remains the selected development stream, not 18 tasks or six families.

## 7. Interpretation

### If `D_U - D_A > 0`

The between-state behavioral difference from byte-identical evidence exceeds the observed within-state actor disagreement in this selected case. This strengthens the claim from a one-shot regeneration anomaly to a **local state-regeneration instability consistent with a state-generation bottleneck**. It still does not estimate population variance.

### If `D_U - D_A <= 0`

Classify:

`ACTOR_NOISE_NOT_EXCLUDED / DOWNGRADE_STATE_REGENERATION_MECHANISM`

The manuscript must stop claiming that the current exact-evidence evidence demonstrates state-regeneration instability beyond actor noise. M2 manual-state results cannot rescue this mechanistic claim. The automatic bridge may proceed only under a separately justified complete-method hypothesis if its frozen eligibility gates allow it; the manuscript title/abstract must remove regeneration-instability language.

## 8. Authority boundary

This document grants zero authority for:

- provider calls;
- actor measurement;
- updater calls;
- Recovery V3 modification;
- M4;
- E3;
- second backbone;
- public benchmark;
- paper submission.

It is an outcome-aware development proposal frozen after independent manuscript review and before any M3R provider execution. Any future execution requires separate preflight, provider-budget contract, completion audit, and explicit measurement authorization.
