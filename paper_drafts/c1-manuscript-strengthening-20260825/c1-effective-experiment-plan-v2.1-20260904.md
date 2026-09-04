# C1 effective experiment plan V2.1 — reuse-before-rerun execution refinement

Date: 2026-09-04
Status: **FROZEN BEFORE COLLISION/MMD2 OUTCOME OPENING**
Parent design: `c1-effective-experiment-plan-v2-20260904.md`
Parent design SHA256: `fb43c9d0f1cb552bcf41970b351c2e4ff121d06385eefd0f64828677cae4c43d`
Parent machine plan SHA256: `8c015d275ad01e39cdfbfff21bf955a230108a536d1a3d002aa86e581f92017f`
A2.0 raw-replay qualification: **PASS**
A2.0 receipt SHA256: `2bac711b6ebec8b77568bdca3cd0ea47d62d2dde52add8e34f44493703ff88d7`
Paper archetype: **measurement / identification**
PACTA-MSR: **independent optional successor; not a current-paper closure requirement**

## 0. Why V2.1 exists

V2 correctly froze exact-match-kernel unbiased MMD2 / collision U-statistics as the preferred stochasticity-aware first-action estimand before any new A2 outcome was opened. The subsequent zero-provider provenance qualification recovered an additional historical fact that changes execution cost, not the scientific question:

- the frozen Shopping B10 object contains **36 matched branch-comparison states**;
- each state already has **4 success-memory + 4 failure-memory + 4 no-memory first-action draws**;
- the historical B10 result is content-addressed at SHA256 `e779c19a6a73bdb4b551f0739453a014fe9fc3cafc17cb4fbaa8b70a5137d8e6`;
- all 432 raw provider texts, stage records, and provider-response receipts remain present under the private run root;
- raw text re-parsed with the frozen historical normalizer reproduces all 432 saved action signatures;
- the historical primary statistic replays exactly: mean S/F TV `0.06944444444444445`, permutation `p=0.5800941990580094`, and `0/36` modal S/F changes.

Therefore the cheapest valid next step is **not** to issue another 144--576 first-action calls. It is to use the already frozen repeated-decoding support for a zero-provider stochasticity-aware diagnostic first.

This refinement does not reinterpret provider calls as scientific units. The scientific unit remains the matched frozen Shopping state (`n=36`); repeated decodes are nested measurements within a state.

---

# 1. Admission rule: every experiment must buy a reviewer-facing distinction

An experiment is admitted only if all four tests pass:

1. **Claim link** — it targets one named claim or reviewer objection.
2. **Decision differential** — different outcomes lead to different manuscript/adjudication decisions.
3. **Matched estimand** — the control changes only the factor needed for the objection.
4. **Minimum sufficient cost** — no already-collected evidence can answer the same question with adequate validity.

Under this rule, the current default program contains one first-action objection audit and no default model/domain expansion.

---

# 2. Frozen evidence that must not be rerun

Retain without replacement or outcome relabeling:

- Shopping paired write divergence: `20/20`;
- combined Shopping+Reddit write lineage: `24/24`;
- same-mode wording control: between-minus-within `0.104978`, exact one-sided sign-flip `p=0.007812`;
- forced fixed-evidence terminal leverage: `|Delta|=0.15625`, `p=0.00074`;
- native Shopping source-item exposure: `125/172`;
- historical Shopping first-action: mean empirical TV `0.06944`, `p=0.5801`, `0/36` modal changes;
- native Shopping terminal: `|S-F|=0.02083`, `p=0.4289`, `34/36` zero;
- Reddit write: `4/4` divergent; native terminal `|S-F|=0.125`, `p=0.2253`, `6/8` zero with opposite signs in the two nonzero cells;
- existing structural sensitivity audit.

The current paper may say that stable first-action branch uptake was **not established by the frozen primary TV test**. It may not infer a zero effect, latent irrelevance, latent authority failure, or a causal mediation coefficient.

---

# 3. M0 — historical first-action provenance replay: COMPLETE / PASS

## Objection addressed

> The claim audit binds first-action evidence through summary artifacts; a new stochasticity analysis must not be built on opaque or unreplayable historical records.

## Qualification result

`qualify_b10_first_action_raw_replay_20260904.py` verifies:

- B10 contract file SHA256 `c2a54c928d74ccb7a153166a02ef0ef7a1504a93b5895952380a95b0277a3436`;
- B10 contract payload SHA256 `a6983c0fe46c649a187bc60954614dfc489b2de903928a452cf0494034b0b3c5`;
- B10 result SHA256 `e779c19a6a73bdb4b551f0739453a014fe9fc3cafc17cb4fbaa8b70a5137d8e6`;
- historical runner SHA256 `87214f92c2a11ea9ff139535ca6d7d272680ec5ed7da8b86880475bbb66cb98a` at commit `f400a9e218c869a447110f3e3e00de6449550985`;
- `432/432` complete stage records;
- `432/432` content-addressed raw provider texts;
- `432/432` raw-to-normalized action-signature matches under the historical parser;
- exact historical metric/permutation replay.

**Gate:** PASS. Zero new provider calls were made.

---

# 4. M1 — evaluation-surface baseline package: zero calls

The current paper is a measurement/identification paper, so the strongest relevant baselines are evaluation surfaces and matched controls, not a memory-method leaderboard.

| Baseline | Observable | Alternative explanation tested |
|---|---|---|
| Write-only | `W` | persistent state change alone is sufficient evidence of learning |
| Retrieval-only | `E` | memory availability is sufficient evidence of policy use |
| Native endpoint-only | `O` | a small endpoint is enough to localize where transport failed |
| Forced-only | side `F` | downstream leverage under supplied memory equals native transport |
| **Stage-resolved C1** | `W,E,U,O` + side `F` | preserves stage identity and exposes observational aliases |

Existing matched controls remain the only other required baselines:

- same-mode wording control at `W` -> generic prompt-wording sensitivity;
- forced fixed-evidence control -> global downstream memory insensitivity;
- outcome-blind structured-memory control -> generic structure/prompting alternative;
- structural stage ablation -> whether the stage localization depends on removing/merging a load-bearing measurement boundary.

Do not add SAMem, MemArbiter, AWM, ExpeL, or a broad method zoo to Track A unless the paper changes from measurement to method comparison.

---

# 5. M2 — first-action stochasticity objection audit

## 5.1 Scientific unit and frozen support

Primary support is the existing B10 `success_memory` versus `failure_memory` first-action panel:

- 36 frozen matched Shopping states;
- 4 repeated success-memory first actions per state;
- 4 repeated failure-memory first actions per state;
- same policy model/snapshot, state-selection rule, temperature, parser, and action identity used by historical B10;
- no-memory draws are retained as historical descriptives but are **not** part of the primary S/F stochasticity-adjusted statistic.

Repeated calls are nested measurements, never `n=288` scientific units.

## 5.2 Primary zero-provider diagnostic — frozen before opening its outcome

Use the exact action identity already replay-qualified:

> first structured action name; `click_element` additionally includes the interactive-element index.

Kernel:

`k(a,b) = 1[a == b]`.

For state `i`, with success actions `S_i={s_1,...,s_m}` and failure actions `F_i={f_1,...,f_n}`, here `m=n=4`, define the unbiased collision estimator

`U_i = 1/(m(m-1)) * sum_{j != l} k(s_j,s_l) + 1/(n(n-1)) * sum_{j != l} k(f_j,f_l) - 2/(mn) * sum_{j,l} k(s_j,f_l)`.

This is unbiased for squared MMD under the exact-match kernel. It directly uses **within-condition collision/concentration** terms to correct the between-condition comparison. Finite-sample negative `U_i` values are legal and must not be clipped.

Why this replaces a small-sample empirical-TV "noise floor": plug-in empirical TV in a sparse/high-cardinality categorical space has concentration-dependent upward bias. The collision U-statistic estimates the same-distribution null at zero in expectation without requiring an arbitrary split into two tiny TV blocks.

### Frozen inference

Primary global statistic: mean `U_i` across the 36 frozen states.

Null:

> Conditional on each frozen state, the success/failure branch labels are exchangeable for the normalized first-action draws.

Randomization test:

- within each state pool the 8 S/F action signatures;
- independently shuffle and assign 4/4 pseudo-branch labels per state;
- recompute all `U_i` and their 36-state mean;
- Monte Carlo repetitions: `100000`;
- RNG semantics: Python `random.Random`;
- seed: `20260824`;
- one-sided tail: randomized mean `U >= observed mean U`;
- p-value: `(ge + 1)/(R + 1)`.

The repetitions, seed, and state-stratified permutation scheme deliberately reuse historical B10 choices to avoid adding outcome-dependent analytical degrees of freedom.

Report, without population-generalization language:

- all 36 `U_i` values;
- mean and median `U_i`;
- within-success collision, within-failure collision, and between-branch collision per state;
- counts of positive / zero / negative `U_i`;
- fixed-state bootstrap interval for the mean as descriptive uncertainty only;
- the frozen randomization-test p-value;
- normalized action-frequency tables.

### Authority of this diagnostic

This is a **post-hoc zero-provider diagnostic on prospectively collected historical B10 draws**. The MMD2/collision estimand was frozen in V2 before this diagnostic outcome is opened, but the historical data themselves are not a newly prospective confirmation set.

Therefore this diagnostic may determine whether additional calls are scientifically necessary and may refine limitations. By itself it must not be presented as an independent prospective replication.

## 5.3 Decision rule after the zero-provider diagnostic

### D1 — clear stochasticity-adjusted S/F separation

If the frozen collision test supports positive branch-distribution separation:

- the historical panel contains evidence that S/F first-action distributions differ after correcting for within-condition concentration;
- revise any wording that treats the first-action boundary as strictly pre-action;
- keep the result explicitly post-hoc unless independently replicated;
- authorize a fresh prospective replicate **only if** making stochasticity-controlled action divergence a primary claim is verdict-changing for submission.

### D2 — no supported stochasticity-adjusted separation

If the frozen collision test does not support S/F separation:

- retain first-action uptake as the first unsupported measured native stage;
- wording may be sharpened only to: "not established above stochasticity under the replay-qualified collision diagnostic on this frozen panel";
- do not infer equality or a zero effect;
- do not issue more calls merely to chase significance.

A fresh replicate is justified only if reviewers require a prospective stochasticity-controlled test to resolve a material ambiguity rather than accept the conservative boundary claim.

### D3 — estimator precision is decision-inconclusive

If the 4+4 support is too imprecise to distinguish reviewer-relevant alternatives:

- run the zero-provider calibration in Section 5.4;
- do not inspect a sequence of larger samples and stop when significance appears.

## 5.4 Prospective fresh replicate — conditional only

A new provider experiment is **not default** after discovering the historical 4+4 repeated-decoding geometry.

It becomes authorized only when both conditions hold:

1. the zero-provider diagnostic/calibration shows that the current 4+4 support cannot resolve a reviewer-verdict-changing distinction; and
2. a fresh independent stochasticity-controlled result is needed for the intended manuscript claim.

If triggered, sample size is frozen **before fresh outcomes** using replay-qualified historical concentration structure plus synthetic null/alternative stress distributions. Candidate fresh draws per branch are `n in {2,4,6,8}`; choose the smallest `n` meeting predeclared false-positive and sensitivity requirements.

Fresh call envelopes:

- `n=2`: `36 x 2 x 2 = 144` calls;
- `n=4`: `288` calls;
- `n=6`: `432` calls;
- `n=8`: `576` calls.

No no-memory condition and no terminal rollout are required for this confirmatory question. Stop after the first normalized structured action.

The fresh replicate is a new independent block; do not silently mix old and new draws into one confirmatory sample or adaptively top up after inspecting interim effects.

---

# 6. M3 — figure / claim / submission gate

After M1 and the zero-provider M2 diagnostic:

1. update Figure 1 as an evidence-status stage diagram;
2. keep forced capacity on a side bypass rather than the native chain;
3. show stochasticity qualification at the first-action stage with prospective/post-hoc status explicit;
4. keep PACTA-MSR in a small prospective successor box only;
5. run machine claim/evidence audit;
6. obtain a fresh independent submission-level review.

Only that review may trigger broader execution.

---

# 7. Conditional extensions only

## C1 — complete existing Reddit E/U before any third domain

Default: **do not run**.

First conduct a zero-provider feasibility audit of whether existing Reddit frozen writes/tasks can support Shopping-compatible native exposure `E` and first-action `U` instrumentation.

Execute only if post-M2 submission review says cross-domain replication of the stage boundary is a verdict-changing objection. If the existing Reddit substrate cannot support matched semantics without changing the scientific object, stop rather than invent a third benchmark for table size.

## C2 — one additional executor/backbone

Default: **do not run**.

Execute only if, after M2, an independent reviewer identifies model/configuration specificity as a verdict-changing limitation. Change the executor only; keep writer, frozen state panel, retrieval, and action canonicalization fixed.

## C3 — PACTA-MSR

Independent method-expansion track. It is not required to close or rescue the current C1 measurement paper.

If deliberately opened later, its minimal internal baselines remain:

- native raw memory;
- SCB always;
- rate-matched random authorization;
- PACTA-MSR selective authorization.

External method baselines are considered only after a genuine P0 effect exists.

---

# 8. Current priority and stop rules

## Mandatory now

- **M0 DONE:** raw/provenance replay PASS, zero calls.
- **M1:** compile evaluation-surface baseline table from existing evidence, zero calls.
- **M2-Z:** run the frozen collision/MMD2 diagnostic on existing 4+4 S/F draws, zero calls.
- **M3:** claim/figure audit and independent submission review, zero provider calls.

## Conditional only

- **M2-P:** fresh prospective first-action replicate only if M2-Z is precision/verdict insufficient.
- **C1:** Reddit E/U only if cross-domain replication remains verdict-changing.
- **C2:** second executor only if model specificity remains verdict-changing.
- **C3:** PACTA-MSR only as deliberate method expansion.

## Explicitly rejected workload inflation

Do not automatically:

- rerun B10 merely because the old primary metric was TV;
- count the 288 S/F repeated decodes as independent scientific units;
- add three or more models because SkillZip Pro had broad model coverage;
- add a third benchmark before exhausting the existing Reddit substrate;
- run a memory-method zoo with mismatched estimands;
- run terminal trajectories for a first-action-only question;
- perform adaptive sample-size top-up after inspecting significance;
- select positive state subgroups post hoc;
- use PACTA-MSR as a rescue experiment for the measurement paper.

The stopping criterion is reviewer-facing identification, not experimental table size.
