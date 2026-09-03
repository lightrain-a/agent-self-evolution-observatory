# E2-R17 manuscript R3 — V4-R1 protocol alignment — 2026-09-03

## Current manuscript title

> Same Evidence, Different Skill: State-Regeneration Instability in Self-Evolving Agents

The title remains deliberately narrower than the earlier `Diagnosing State-Generation Variance` wording because completed evidence establishes only a selected-case regeneration instability, not a population variance component or a causal variance decomposition.

## Completed-evidence boundary

Strongest currently supported statement:

> In one controlled outcome-selected development case, reconstructed byte-identical trajectory evidence did not reliably regenerate the historical behaviorally useful skill through the native free-form updater, while the historical state itself remained directionally useful when frozen and re-evaluated. This is local state-regeneration instability consistent with a persistent-state generation bottleneck; it is not a population variance decomposition and does not establish that updater variance dominates actor variance.

The manuscript does **not** currently claim:

- that the typed compiler improves downstream utility;
- that First-Fail-4 is superior to Winner evidence;
- that state-realization variation dominates actor noise;
- that trajectory-conditioned typed diagnosis is better than generic/scope canonicalization;
- that any mechanism generalizes to untouched E3, another backbone, or a public benchmark.

## Independent reviews already counted

### Manuscript R1

Frozen R1 commit:

`b93a93d084b4e84504fdcf2d2bb22fc489ea51a2`

Oracle Browser reviewer:

- GPT-5.6 Sol
- Extra High (4/5 verified from ChatGPT DOM)
- session `e2-r17-manuscript-r1-review-3`
- conversation `6a9976ea-7908-83e8-acf0-b57b0b203ca5`
- verdict `REVISE_DESIGN_BEFORE_NEXT_PROVIDER_STAGE`

This review caused the claim/title narrowing, revised M3 frozen-state audit, stronger generic controls, and separation of generator authority from rejected-source superiority.

### Bridge V3 pre-execution review

Oracle Browser reviewer:

- GPT-5.6 Sol
- Extra High
- session `e2-r17-bridge-v3-final`
- conversation `6a996756-fb94-83e8-b886-0a40e84b9388`
- verdict `REVISE_BEFORE_STAGE_A`

The accepted repairs include:

1. separate raw complete-method authority from generic-control interpretation;
2. preserve first deployed FREE realization A as the primary reference and keep B as sensitivity;
3. replace noncommensurate bridge `D_U-D_A` with cross-state-versus-within-state `D_X-D_A`;
4. collapse byte-identical persistent states by SHA so actor noise cannot manufacture state-treatment effects;
5. describe scope control `k` as a diagnosis-cardinality side channel and bound its interpretation.

## V4-R1 prospective bridge object

Frozen review object:

- branch `research/e2-r17-state-compiler-bridge-v4-review-repair-20260903`
- commit `51edbda1bd18ed6585def50dc8e5c12143d8b0bd`
- protocol `generated/e2-r17-state-compiler-bridge-protocol-v4-r1-20260903.md`
- protocol SHA-256 `6ee0768ce8ef9418250935de2153dde5837266753d63b64cf4d9e99eedf53697`

The primary M4 question is now the generator factor of the balanced 2×2 rather than an FF4-only contrast:

`G_MAIN,A = 0.5 * [(W_COMP-W_FREE) + (FF4_COMP-FF4_FREE_A)]`

The four prospective questions are orthogonal:

1. **Q1 / primary:** complete state-generation method effect via `G_MAIN,A`;
2. **Q2 / interpretation:** typed trajectory-conditioned diagnosis versus score-only/scope generic canonicalization;
3. **Q3 / mechanism:** same-evidence FREE state-realization localization beyond within-frozen-state actor disagreement;
4. **Q4 / parked moderator:** First-Fail source superiority and Evidence×Generator interaction.

Generic-control failure may narrow Q2 without erasing a passed Q1. Q3 failure removes realization/variance-centered mechanism language. Q4 failure drops the rejected-source story while leaving the primary state-generation paper intact.

## Fresh bridge suite

Already qualified zero-provider substrate:

- 120 formal tasks;
- 96 update tasks in 12 streams × 8;
- 12 SCREEN heldout tasks;
- 12 disjoint VALIDATION heldout tasks;
- six SCREEN streams and six VALIDATION streams, one per controlled family;
- blocks 7--9 only;
- zero task-ID and XLSX-SHA collision with the earlier controlled suite;
- untouched E3 blocks 5--6 not used.

Qualification status:

`PASS_ZERO_PROVIDER_FRESH_BRIDGE_SUITE_QUALIFICATION`

No bridge provider authority follows from this qualification.

## Revised M3 remains separate

M3R freezes four already-existing states and proposes 72 new actor units with **zero updater calls**:

- historical First-Fail SHA `97e28b4862ed5817929fa6014eb1ba1401667875d80e03d18c0b54978a185252`;
- fresh First-Fail 1 SHA `596bd30b49935d16f35d51e9eed36e19567332cd8a9104ae50d832f91ffdf04f`;
- fresh First-Fail 2 SHA `fb5454a27faf8182ba1b0d722273c4377d4762815cd1898c3780cc8ff336615e`;
- common WIN-C SHA `6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649`.

The M3R metric is a separately frozen development object. The bridge V4-R1 change from `D_U-D_A` to `D_X-D_A` must **not** silently rewrite the M3R contract; any M3 metric change would require explicit supersession/adjudication before execution.

## R3 manuscript alignment applied

R3 prospective text now follows V4-R1:

- Q1 is the equal-weight generator-factor main effect across Winner and FF4;
- Winner-side and FF4-side generator contrasts are components, not primary gates;
- generic controls classify Q2 interpretation rather than VALIDATION authority;
- FREE_B is sensitivity/mechanism only and cannot replace FREE_A;
- bridge realization localization uses commensurate `D_X-D_A` / `E_REAL`;
- byte-identical state SHA forces zero causal state/realization contrast;
- First-Fail superiority and interaction are independent parked moderators;
- failure of Q1 stops the automatic state-generation-method story without E3/backbone/benchmark rescue;
- failure of Q2/Q3/Q4 narrows only the corresponding claim.

Completed scientific result sections remain unchanged in substance.

## V4-R1 independent review status

A fresh V4-R1 Oracle review has **not** produced a valid reviewer verdict yet.

Two attempts on 2026-09-03 are not counted:

1. model-picker automation failed before prompt submission;
2. a retry verified GPT-5.6 Sol + Extra High and reported `promptSubmitted=true`, but the message never produced an assistant turn; harvest showed zero assistant turns.

Therefore do **not** record `PASS_V4_R1_PREEXECUTION_DESIGN` or any other V4-R1 reviewer verdict unless a later independent session returns a complete answer.

## R3 static qualification

After V4-R1 text alignment:

- manuscript/V4-R1 alignment tests: 10/10 PASS;
- combined adjacent E2 regression: 73/73 PASS;
- LaTeX compile: PASS;
- PDF pages: 15;
- overfull boxes: 0;
- undefined references/citations: 0;
- PDF SHA-256: `2462bdf33c26c2cf01e47e03d6774822ff86cd1efa157432d10e6c0ed7ef9392`.

These checks qualify manuscript consistency only; they do not create scientific execution authority or a V4-R1 independent-review verdict.

## Current authority boundary

R3 is manuscript/design alignment only. It does not authorize:

- Recovery V3 modification or early replay;
- M3 actor measurement;
- M4 search-pool acquisition;
- FREE_A/FREE_B updater execution;
- bridge actor evaluation;
- SCREEN/VALIDATION outcome opening;
- Semantic-Transfer Stage A while the primary state-generator bridge is unresolved;
- E3;
- second backbone;
- public benchmark;
- submission.

Recovery V3 remains under its existing frozen exactly-once authority and quota-reset continuation. No partial M2 outcome is imported into this manuscript revision.
