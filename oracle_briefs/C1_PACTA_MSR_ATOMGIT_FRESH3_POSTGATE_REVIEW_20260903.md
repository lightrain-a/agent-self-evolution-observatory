# Independent adversarial review — C1 PACTA-MSR AtomGit/Qwen3.8 fresh3 post-source-gate

Date: 2026-09-03
Role: independent senior ICLR/NeurIPS/ICML agent-systems methodology reviewer

## 0. Exact current object

Review the CURRENT frozen C1 object after source acquisition has already failed closed. Do not review it as a hypothetical pre-execution design and do not infer any method effect.

- Worktree: `experiment/c1-pacta-msr-atomgit-qwen38-q07-fresh3-p0-20260903`
- Frozen P0 commit: `34d5d39be336e0e71316c3cf1c0e6afdbe7baeae`
- Model condition: AtomGit CodingPlan / AtomCode-mediated `qwen3.8-27b`
- Active manuscript: R9
- Claim authority at all relevant gates: `NO_MSR_METHOD_EFFECT_EVIDENCE`
- Downstream scientific writer/binder/probe/shadow/final calls: all zero.

The scientific question behind the prospective PACTA-MSR pilot is whether a state-conditional selector can preserve distinct first-action distributions induced by success-writer vs failure-writer memory states better than native, always-on, and rate-matched-random controls. The current question is narrower: is the source-gate retirement scientifically correct, and is the already-frozen downstream pilot design valid enough to reuse unchanged on a genuinely fresh successor substrate?

## 1. Frozen fresh3 source contract

Before any fresh3 provider outcome, the source runner froze:

- source pool: 10 source/future pairs, one pair per repository, selected outcome-blind from frozen SWE-bench Verified local data;
- all historical/fresh1/fresh2 task IDs excluded;
- pilot split: 8 pilot + 2 sealed, frozen pre-provider;
- sealed units forbidden from probe/writer/binder/shadow/final;
- source order frozen by content-addressed schedule;
- exact-base container normalization;
- provider: AtomCode `qwen3.8-27b` through strict ordinary-JSON text bridge;
- source max completion tokens: 32768;
- first-decision budget: 2048;
- AtomCode subprocess timeout: 900 s;
- `provider_wrapper_retries = 0`;
- one logical attempt per scientific source;
- every raw provider response persisted;
- source trajectory + writer-input trajectory content-addressed;
- future tasks are never executed during source acquisition.

The frozen source gate is explicit:

> all 10 sources must be provenance-valid; any consumed-invalid source or consumed incomplete epoch retires the entire fresh3 pool; no replacement, top-up, or retry.

Explicit forbidden actions include:
- retry a consumed scientific source logical attempt;
- replace or top up a consumed-invalid source;
- change bridge/system prompt/config after a fresh3 outcome;
- switch model/provider to rescue fresh3;
- execute downstream scientific phases during acquisition.

This exactly-once rule was intentionally defined at the logical multi-step episode level, not at the final provider packet level, because earlier source attempts showed that a later provider failure may occur only after substantial model-content-bearing steps have already been consumed.

## 2. Pre-source qualifications

Before fresh3 scientific acquisition:

### Runtime qualification
The re-bound runtime-v2 passed its frozen 20/20 normalization qualification (10 source + 10 future containers). This was zero-provider and content-addressed.

### Source prelaunch
All 10 source containers passed prelaunch with zero provider calls.

### Non-scientific multistep smoke
A synthetic multistep source-carrier through the same Q0.3 ordinary-JSON bridge passed before scientific acquisition.

### Source budget / bridge qualifications
Prior outcome-independent qualification froze:
- Q0.2 source envelope: 32768 completion tokens, 2048 first-decision budget;
- Q0.3 strict ordinary-JSON bridge;
- no temperature-equivalence claim; sampling is provider-managed.

These qualifications were designed before fresh3 source outcomes.

## 3. What actually happened on fresh3

Source root:
`/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-atomgit-qwen38-fresh3-source-20260903-v2`

Frozen support audit now says:

- attempted: `2`
- valid: `1`
- valid repositories: `1`
- pool retired: `true`
- replacement: `false`
- top-up: `false`
- decision: `HOLD_FRESH3_ATOMGIT_MSR_SOURCE_POOL_RETIRED_OR_INCOMPLETE`
- claim authority: `NO_MSR_METHOD_EFFECT_EVIDENCE`
- writer/binder/probe/shadow/final calls: all `0`
- future-task executions: `0`

### Source 1 — psf__requests-6028
- logical attempt: 1
- provider logical calls: 22
- provider transport attempts: 22
- all raw responses persisted
- terminal status: `Submitted`
- validity: `TRAJECTORY_BACKED_VALID`
- source trajectory SHA and writer-input SHA recorded.

### Source 2 — sympy__sympy-15875
- logical attempt: 1
- provider logical calls: 6
- provider transport attempts: 6
- all raw responses persisted
- terminal status: `RuntimeError`
- failure layer: `provider`
- validity: `INVALID`
- source trajectory and writer-input trajectory were still persisted/content-addressed.

The failure occurred only after six model-bearing calls, so this was not a zero-content connection failure before the logical source episode began. Under the frozen contract, the source was consumed-invalid and the whole fresh3 pool retired immediately. The remaining eight source units were not executed.

No source replacement, retry, or top-up was performed. No downstream P0 phase was executed. The observed fresh3 outcomes have not been used to alter downstream thresholds, sample counts, salts, writer/binder budgets, or model choice.

## 4. Frozen downstream P0 object (prepared, not executed)

The downstream contract was frozen before the fresh3 source-gate verdict. Its root contains only preparation artifacts (contract, configs, bound deterministic probe specs, shadow schedule); no scientific downstream result exists.

### Units
- 8 pilot units
- 2 sealed units, completely forbidden from downstream execution
- source gate is revalidated before every non-prepare phase.

### Probe
- deterministic exact-base probe
- 8 executed units if authorized
- provider calls: 0
- post-probe HEAD/clean-tree invariant
- timeout 60 s.

### Writer
For each pilot unit:
- two branches: `SUCCESSFUL_SI`, `FAILED_SI`
- exactly same source trajectory within the pair
- 16 calls total
- ordinary JSON/plain-text bridge
- max_tokens 4096
- exactly one provider-valid realized draw per branch
- persist/content-address before binder
- no semantic reroll
- output: 1..3 ReasoningBank memory items.

### Binder
- contexts: `G0_STEP0`, `GPLUS_MATCHED_REVEAL`
- 32 calls total
- max_tokens 2048
- exactly one realized content-addressed draw per branch/context
- no semantic reroll
- output: nonempty one-line state, <=60 whitespace words.

### Shadow measurement
- selectors: G0 and G+
- 384 calls = 8 units x 2 selectors x 2 writer branches x 2 blocks x 6 samples
- action signature: exact first fenced bash command; no post-hoc canonicalization
- within each branch/selector empirical action distributions are estimated from the frozen sampling geometry.

For each selector the separation statistic uses the two independent six-sample blocks:

`margin = min(B1,B2) - max(WS,WF)`

where B1/B2 are between-writer separations across blocks and WS/WF are within-writer block-instability terms.

### Mechanism gate
Final measurement is forbidden unless:
- all shadow calls complete;
- G+ opens in 2..6 of 8 units;
- mean margin improvement `(G+ - G0) >= 0.05`;
- positive margin improvement in at least 5/8 units.

Failure action: STOP before final.

### Rate-matched random control
- random ranking frozen before shadow outcomes;
- K equals the observed G+ open count;
- no reroll.

### Final, only after mechanism-gate PASS
384 calls across:
- A0_NATIVE
- A1_SCB_ALWAYS
- A2_RATE_MATCHED_RANDOM
- A3_PACTA_MSR

Endpoint: per-unit empirical total-variation distance between success-writer and failure-writer first-action distributions.

Primary:
`D_select = U_A3 - U_A2`

Pilot PASS requires all of:
- all final calls complete;
- mean D_select >= 0.05;
- positive D_select units > negative units;
- mean A3-A0 > 0;
- mean A3-A1 >= 0.

### Estimand boundary
The scientific estimand is explicitly conditional on:
- exactly one realized, content-addressed writer draw per branch;
- exactly one realized, content-addressed binder draw per branch/context.

Writer/binder stochasticity is part of the realized state. This is NOT an average causal effect over writer/binder randomness and NOT a temperature-matched replication of the older Qwen397 lane.

## 5. Outcome-independent downstream qualifications

Q0.5 froze the first sufficient completion ceilings before downstream science:
- writer 4096: 6/6 synthetic fixtures PASS at first candidate;
- binder 2048: 512 truncates; 1024 truncates; 2048 6/6 PASS; 4096 not run.

Q0.6 froze the conditional realized-state estimand and action envelope:
- action max_tokens 4096;
- 12/12 exact bridge fixtures transport-valid;
- native tool runtime events 0;
- provider-managed action diversity observed;
- no fresh3 source outcome used as a fixture;
- no scientific writer/binder/shadow/final call.

The exact downstream resource geometry is frozen:
- max requests if final runs: 816;
- pre-mechanism requests: 432;
- no threshold/budget/model switching after outcomes.

## 6. Questions to audit

Audit A–L explicitly.

A. Given that source 2 had already consumed six model-bearing provider calls before a provider-layer RuntimeError, is treating it as a consumed-invalid logical episode scientifically correct under exactly-once semantics?

B. Is retiring the entire fixed 10-source pool, rather than retrying source 2 or continuing the other eight and replacing/top-upping later, the correct fail-closed action for the preregistered all-10 source-support gate?

C. Would retrying the same source episode after this failure change the scientific object because the retry would realize a new stochastic trajectory after the first realization was already partially observed/consumed?

D. Is it scientifically acceptable that a future fresh4 successor may improve transport qualification prospectively, provided it uses a wholly new disjoint source/future pool and does not reuse or top up fresh3?

E. Does the current fresh3 support audit correctly preserve `NO_MSR_METHOD_EFFECT_EVIDENCE`, or is any method-effect interpretation accidentally licensed by the one valid source?

F. Is the 8-pilot/2-sealed downstream split legitimate, with sealed units completely excluded from all pilot/gate/final execution?

G. Does the writer/binder one-realized-draw design support the stated conditional realized-state estimand, or is the paper still implicitly claiming an average effect over writer/binder randomness that the design cannot identify?

H. Is the shadow margin `min(B1,B2)-max(WS,WF)` a defensible small-sample localization statistic for whether between-writer action separation exceeds within-writer sampling instability, given two independent blocks of six per branch?

I. Is the mechanism gate logically independent enough from the final A3-vs-A2 endpoint to serve as an outcome-blind promotion gate rather than double-dipping on the final estimand?

J. Is choosing rate-matched-random K equal to the observed G+ open count valid when the random ranking itself was frozen pre-shadow and there is no reroll, or does this create post-treatment control tuning that invalidates A3-vs-A2?

K. Are the final criteria scientifically coherent for an eight-unit developmental pilot, or do any of them accidentally encourage significance-chasing / pseudo-replication from the 384 model calls?

L. What is the smallest scientifically valid next action now: hold fresh3 permanently and preregister a new fresh4 source substrate, revise the downstream P0 contract before any successor, or stop the C1 PACTA-MSR direction?

## 7. Required verdict

Choose exactly one:

`HOLD_C1_FRESH3_RETIREMENT_CORRECT`

`REVISE_C1_P0_BEFORE_SUCCESSOR`

`STOP_C1_PACTA_MSR`

Interpretation:
- `HOLD_C1_FRESH3_RETIREMENT_CORRECT`: fresh3 retirement is scientifically correct; no downstream fresh3 execution is allowed; the frozen P0 design has no verdict-changing defect that must be repaired before a wholly new prospectively qualified successor substrate. Report any successor-only transport qualification requirement separately.
- `REVISE_C1_P0_BEFORE_SUCCESSOR`: fresh3 must remain retired, and at least one verdict-changing causal/statistical defect in the downstream design must be fixed before any fresh successor source acquisition/P0.
- `STOP_C1_PACTA_MSR`: even with a new substrate, the experiment cannot support a coherent standalone mechanism/method contribution.

Do not authorize a retry, replacement, or top-up of fresh3 unless you can demonstrate that the already consumed six-call source episode was scientifically zero-content, which the frozen evidence contradicts. Do not request a model zoo or broad benchmark expansion. Do not infer any downstream outcome.
