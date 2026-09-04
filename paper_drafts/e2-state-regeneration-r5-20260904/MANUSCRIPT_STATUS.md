# E2-R17 manuscript R5 — M3R4 + Bridge V4-R2 pre-execution alignment — 2026-09-04

## Working title

> Same Evidence, Different Skill: State-Regeneration Instability in Self-Evolving Agents

The title remains intentionally narrower than `Diagnosing State-Generation Variance`. Completed evidence supports a local selected-case regeneration instability consistent with a persistent-state generation bottleneck; it does not establish a population variance component or prove that state-generation variance causally mediates downstream utility.

## Strongest completed claim

> In one controlled outcome-selected development case, reconstructed byte-identical trajectory evidence did not reliably regenerate the historical behaviorally useful skill through the native free-form updater, while the historical state itself remained directionally useful when frozen and re-evaluated. This is local state-regeneration instability consistent with a persistent-state generation bottleneck; it does not isolate generator variation from downstream actor noise at population scale.

The manuscript still does **not** claim that:

- the typed compiler improves downstream utility;
- First-Fail-4 is superior to Winner evidence;
- state-realization variation dominates actor noise generally;
- the FF4 typed diagnosis beats its generic controls;
- the mechanism generalizes to untouched E3, another backbone, or a public benchmark.

## Completed evidence ladder

1. DeepSeek V2: 48 pairs / 96 states / 1,728 held-out units; mean rejected-witness-minus-WIN-C = `+0.023148`, bootstrap CI crosses zero; verdict `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.
2. S1 selected development case: WIN-C 13/18, First-Fail 17/18, Progress-Fail 14/18, Progress-Contrast 14/18; verdict `S1_SIGNAL_FAIL_STOP_NO_S2`.
3. Historical strong First-Fail state frozen remeasurement: 15/18 vs 14/18 and 16/18 vs 12/18; verdict `FIRST_FAIL_FROZEN_STATE_STABILITY_PASS`.
4. Exact byte-identical First-Fail evidence replay: two new updater states yield 15/18 vs 15/18 and 11/18 vs 12/18; the historical useful advantage does not reliably regenerate.

These outcomes are unchanged by R5.

## M2 Recovery V3 remains separate

Authoritative M2 Recovery V3 lineage:

- branch `research/e2-r17-e3-family-prediction-proposal-20260901`;
- commit `191ffd4e676cd3c748c61d53275b48e7722fc003`;
- 45/72 valid completed before the Ark weekly-quota stop;
- 27 unresolved units frozen in exact hash-balanced recovery order;
- original 18-task primary gate plus frozen 17-task provider-era veto unchanged.

Latest check on 2026-09-04 found the V3 child run root and lease absent, so no premature recovery execution occurred. R5 does not read partial M2 outcomes or modify this object.

## M3R4 — current actor-noise localization design

Authoritative repair branch:

`research/e2-r17-m3r-metric-repair-20260903`

Frozen M3R4 design commit:

`6fb5b0e9c52fa27fbb6e4dd876ce7112b67650e5`

Protocol:

`generated/e2-r17-exact-evidence-frozen-state-regeneration-m3r4-proposal-20260904.md`

Protocol SHA-256:

`2ee4d928725fbb6a3dbe02b81ca4e8fcc69fe618c995593ed050e5e8c35381b6`

Independent pre-execution PASS receipt:

`generated/e2-r17-m3r4-preexecution-review-pass-20260904.json`

Authoritative review-pass commit:

`ee202c5173a7b7467922113c1c658cc3cdd58d25`

### M3R4 measurement

- primary frozen states: FF_R1 and FF_R2 only;
- fixed selected panel: 18 tasks;
- two fully new post-freeze actor replicates per state×task;
- `2 states × 18 tasks × 2 replicates = 72 actor units`;
- updater calls = 0;
- historical FF_HIST, WIN_COMMON, and original exact-replay actor outcomes are descriptive only.

Primary observed statistic:

`E_REAL = D_X - D_A`

where `D_X` is pairwise cross-state disagreement and `D_A` is within-frozen-state actor disagreement.

### M3R4 stochastic inference qualifications

A stronger propensity interpretation requires two explicit levels of qualification:

1. within each frozen state/task, actor realizations are conditionally iid/independent and stationary Bernoulli under the frozen model/runtime;
2. conditional on the fixed panel and observed task totals, informative task-block state-label indicators factorize across tasks.

For tasks with exactly two successes, task-wise same-state separation probability is `1/3`. Only if cross-task factorization is qualified may the aggregate law be interpreted as:

`X | n2, {task totals} ~ Binomial(n2, 1/3)`.

A bounded localization PASS requires distinct state SHAs, `E_REAL>0`, `p_exact<=0.05`, and both inference qualifications. Equal task-specific success probabilities and exchangeability of task identities are not required. Detected cross-task coupling blocks the exact inferential label and does not authorize rerun.

Independent GPT-5.6 Sol / Extra High reviewer verdict:

`M3R4=PASS_PREEXECUTION_DESIGN`.

This PASS qualifies design only and grants zero actor/provider authority.

## Bridge V4-R2 — current automatic method design

Authoritative bridge branch:

`research/e2-r17-state-compiler-bridge-v4-review-repair-20260903`

Frozen V4-R2 design commit:

`8970cf01df3a9b7bd9224ccbb66085b8acd8c53b`

Protocol:

`generated/e2-r17-state-compiler-bridge-protocol-v4-r2-20260903.md`

Protocol SHA-256:

`1bc74c6f98e38535cb3865dcd41fb244b7d17c295db0ee9835937cc1034f9ef7`

Independent pre-execution PASS receipt:

`generated/e2-r17-state-compiler-bridge-v4r2-preexecution-rereview-20260904.json`

Authoritative review-pass commit:

`7c01efd275d9d9a0b68b8f832e7dc610a325b552`

Independent GPT-5.6 Sol / Extra High reviewer verdict:

`BRIDGE=PASS_PREEXECUTION_DESIGN`.

### V4-R2 Q1 — primary complete generator-method effect

Balanced 2×2:

| Evidence | FREE | COMP |
|---|---|---|
| Winner | W_FREE | W_COMP |
| First-Fail-4 | FF4_FREE_A | FF4_COMP |

Primary per-stream estimand:

`G_MAIN,A = 0.5 * [(W_COMP-W_FREE) + (FF4_COMP-FF4_FREE_A)]`.

The same estimand and directional gate are frozen from SCREEN to disjoint VALIDATION. FF4_FREE_B never enters Q1 and cannot rescue it.

### V4-R2 Q2 — FF4-specific method substance

`SCORE_ONLY_GENERIC_MAX` and `SCOPE_MATCHED_GENERIC_MAX` are explicitly FF4-specific controls. They classify whether an FF4 compiler advantage supports trajectory-conditioned typed diagnosis versus scope/generic canonicalization. They do not explain or mediate the Winner-side contribution to balanced Q1 and cannot erase a passed Q1 complete-method effect.

### V4-R2 Q3 — FF4 same-evidence realization localization

Bridge Q3 uses `E_REAL=D_X-D_A` on the pre-frozen VALIDATION realization panel. The unconditional claim is observed cross-state disagreement exceeding within-state actor disagreement. The squared-propensity interpretation is available only under the explicit conditionally iid/independent stationary actor model given state/task/model/runtime.

### V4-R2 Q4 — rejected-source moderator

First-Fail source superiority and the Evidence×Generator interaction remain parked secondary hypotheses. They cannot veto Q1--Q3.

### Universal state identity

All FREE, COMP, and generic-control artifacts are grouped by full persistent-state SHA. Any identical-SHA arms share actor observations and have exact-zero causal state-treatment contrast. This includes FREE↔COMP, COMP↔generic, FREE↔generic, and FREE_A↔FREE_B collisions.

Bridge V4-R2 methodology review PASS does not grant search-pool, updater, actor, SCREEN, VALIDATION, or E3 authority.

## Fresh Bridge suite

Already qualified zero-provider substrate:

- 120 formal tasks;
- 96 update tasks in 12 streams × 8;
- 12 SCREEN held-out tasks;
- 12 disjoint VALIDATION held-out tasks;
- six SCREEN streams and six VALIDATION streams, one stream per controlled family;
- blocks 7--9 only;
- zero task-ID and XLSX-SHA overlap with the earlier controlled suite;
- untouched E3 blocks 5--6 not used.

Qualification status remains:

`PASS_ZERO_PROVIDER_FRESH_BRIDGE_SUITE_QUALIFICATION`.

## Independent-review chronology

Counted reviews only:

1. Manuscript R1: GPT-5.6 Sol / Extra High, verdict `REVISE_DESIGN_BEFORE_NEXT_PROVIDER_STAGE`.
2. Bridge V3: GPT-5.6 Sol / Extra High, verdict `REVISE_BEFORE_STAGE_A`.
3. Combined V4-R1 + M3R2 pre-execution review: both required repair; this produced V4-R2 and M3R3.
4. V4-R2 + M3R3 rereview in conversation `6a9a187e-91d8-83ee-b21b-5dfbf3d1a63d`: `BRIDGE=PASS_PREEXECUTION_DESIGN`, `M3R3=REVISE_BEFORE_EXECUTION` due solely to missing cross-task conditional factorization for the Binomial aggregation.
5. Same-reviewer M3R4 targeted continuation: the blocker is fully fixed, no new verdict-changing defect, `M3R4=PASS_PREEXECUTION_DESIGN`.

Empty-render or pre-submission Oracle turns are not counted as reviewer verdicts.

## R5 manuscript alignment

R5 updates only prospective/design text relative to R4:

- M3R2 is superseded by fully prospective M3R4;
- historical actor outcomes and common WIN are removed from the new M3 gate;
- M3 exact Binomial inference explicitly requires cross-task conditional factorization;
- Bridge V4-R1 is superseded by independently passed V4-R2;
- state-SHA aliasing is universal across all Bridge arms;
- Q2 generic controls are explicitly FF4-specific;
- Bridge Q3 propensity interpretation is conditioned on iid/independent stationary actor assumptions;
- both current designs are labeled pre-execution-reviewed but still non-authorized.

Completed scientific outcomes and the paper title are unchanged.

## R5 static qualification

After M3R4 + Bridge V4-R2 alignment:

- R5 current-object alignment tests: 11/11 PASS;
- combined adjacent E2 regression: 115/115 PASS;
- LaTeX compile: PASS;
- PDF pages: 16;
- overfull boxes: 0;
- undefined references/citations: 0;
- PDF SHA-256: `6194ac7a97a34bdb7f21c36ed2fa5b6f14c4c7184007d5418c643ff11b1c3f15`;
- 100-dpi render preflight: 16/16 pages rendered;
- rendered edge-touch pages within an 8-pixel page boundary: 0;
- extracted word bounding boxes outside the PDF page: 0.

These checks qualify manuscript consistency/layout only. They do not grant M3R4, Bridge, Recovery V3, or E3 execution authority.

## Current authority boundary

R5 is manuscript/design alignment only. It does **not** authorize:

- Recovery V3 modification or early replay;
- M3R4 actor execution;
- M4/Bridge search-pool acquisition;
- FREE_A/FREE_B updater execution;
- Bridge actor evaluation;
- SCREEN or VALIDATION outcome opening;
- parked Semantic-Transfer Stage A while the primary state-generator line is unresolved;
- E3;
- second backbone;
- public benchmark;
- submission.

The active Recovery V3 automation remains the only scheduled scientific continuation and is still bound to its original exactly-once authority.
