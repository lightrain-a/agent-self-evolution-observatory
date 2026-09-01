# E2-R17 Failure Differential Registry

Date: 2026-08-29  
Status: ACTIVE

## Principle

Every experiment, review, preflight, adjudication, and scientific tranche must terminate as either:

1. a **qualified success** that enters the evidence chain; or
2. a **classified failure** that enters this failure chain.

A failure is not disposable noise. It must answer four questions:

- Did the frozen scientific endpoint actually run?
- If not, which layer failed first?
- Is a rerun scientifically legitimate, and what exact variable changed?
- Does the failure update belief in the scientific mechanism?

The key separation is:

> **implementation/protocol/measurement failure != scientific-mechanism failure.**

A protocol-invalid or technically incomplete run cannot count as evidence against the mechanism. Conversely, once a frozen primary experiment reaches a valid endpoint and rejects/equates/harms the mechanism, that scientific negative cannot be reclassified as an engineering problem merely because the result is inconvenient.

## Failure classes

| Class | Meaning | Scientific belief update | Rerun policy |
|---|---|---|---|
| IMPLEMENTATION | launcher, parser, harness, checkpoint, accounting, local-code defect | none before endpoint | repair exact defect, new version/contract if execution semantics changed |
| RUNTIME_INFRA | dependency, executable, environment, provider-route, role-runtime defect | none before endpoint | qualify exact role runtime, then new bound execution |
| PROTOCOL_CAUSAL_PURITY | treatment leakage, treatment conflation, scope/authority defect | invalidates affected causal result | redesign before causal experiment; old result never promoted |
| MEASUREMENT_ANALYSIS | renderer, estimator, token/accounting, adjudicator defect | none until valid measurement | re-adjudicate same frozen raw data if possible |
| SCIENTIFIC_MECHANISM | protocol-valid primary endpoint contradicts/equates/harms mechanism | **yes** | obey frozen STOP/HOLD; no benchmark/model-zoo rescue |

## Permanent execution rules

1. Technical/runtime/protocol/measurement failure before the valid endpoint causes **zero scientific belief update**.
2. Preserve the failed run root, raw receipt, stale lock, raw reviewer answer, or negative result whenever available.
3. Repairs occur under a new version/contract/root; do not silently mutate the failed artifact into a PASS.
4. Every rerun must state: failure class, root cause, exact repair delta, unchanged scientific variables, and why a rerun is legitimate.
5. A valid scientific negative cannot later be relabeled technical without concrete evidence that the original execution was invalid.
6. A central SCIENTIFIC_MECHANISM failure triggers the preregistered STOP/HOLD rule; adding models, benchmarks, subsets, or changing thresholds cannot rescue the claim.
7. Model generation and local review parsing are separate evidence layers. If raw model output is complete but a parser fails, preserve and re-adjudicate the exact response instead of paying for a new answer.
8. Runtime qualification is **role-specific**. Actor/evaluator, persistent updater, and source-faithful baseline harnesses each require their own exact-entrypoint qualification.
9. A preflight is authoritative only if it reproduces the executable, source binding, environment variables, and entrypoint of the scientific runner.
10. Any post-lock dependency override must be disclosed, versioned, hashed, justified, and requalified.
11. Successful runs also need a terminal receipt: protocol integrity, endpoint, authority, interpretation, and next gate.

## Current failure history

### R17-F001 — V3 BPE parity failure

**Class:** MEASUREMENT_ANALYSIS / PROTOCOL_CAUSAL_PURITY  
**Endpoint:** not reached; 0 provider calls.  
**Cause:** equal source-token slices could re-tokenize to unequal final updater-visible lengths after head/tail splice because BPE can introduce a fresh boundary merge.  
**Repair:** V3.1 `ExactMatchedEvidenceBlockRenderer` matches the *actual final re-tokenized block*, uses deterministic no-padding search, and keeps the failed V3 contract/root preserved.  
**Belief update:** none.

Reusable lesson: fairness must bind the representation the model actually receives, not an upstream proxy count.

### R17-F002 — Legacy projection causal leak

**Class:** PROTOCOL_CAUSAL_PURITY.  
**Endpoint:** old path disqualified from E1 causality.  
**Cause:** legacy packets exposed projection/role/rollout/provenance labels and could pair a failed MRW transcript with the served winner's success score.  
**Repair:** V3.1 `BlindedEvidenceUnit`; only evidence text enters `messages`, selected trajectory verifier score is the learner-visible outcome, acting/projection information remains audit-only provenance.  
**Belief update:** none; legacy outputs are non-authoritative for the causal claim.

Reusable lesson: audit provenance is not automatically legitimate treatment content.

### R17-F003 — E1-A budget guard was post-hoc

**Class:** IMPLEMENTATION.  
**Endpoint:** execution held before E1-A authorization.  
**Cause:** provider-call ceiling could be detected after calls rather than claimed before I/O.  
**Repair:** SQLite `BEGIN IMMEDIATE` append-only provider-budget ledger, contract/authorization binding, ambiguous claims never released; 11th per-unit and 7681st total attempts fail before I/O.  
**Belief update:** none.

Reusable lesson: a provider budget is a pre-I/O invariant, not a reporting statistic.

### R17-F004 — E1-A V2 ambient-Python failure

**Class:** RUNTIME_INFRA / IMPLEMENTATION.  
**Endpoint:** failed before first rollout, 0 provider claims, 0 completed refs.  
**Cause:** E1-A orchestrator used ambient `/usr/bin/python3` rather than the frozen actor/evaluator venv.  
**Repair:** V2.1 binds exact venv Python, `VIRTUAL_ENV/PATH`, runtime freeze SHA and qualification SHA.  
**Preservation:** failed V2 root and stale lock remain intact.  
**Belief update:** none.

Reusable lesson: runtime provenance must bind the actual executable.

### R17-F005 — Support adjudicator interpreted zero as missing

**Class:** MEASUREMENT_ANALYSIS / IMPLEMENTATION.  
**Endpoint:** first adjudication failed mechanically after the 96 pools were already frozen.  
**Cause:** `int(summary.get("updater_calls") or -1)` maps valid `0` to `-1`.  
**Repair:** versioned adjudicator changed only zero/missing parsing, was independently reviewed, then re-adjudicated the same frozen pool artifacts.  
**Belief update:** none before repair; no new rollouts were allowed.

Reusable lesson: never use truthiness as missingness for scientific counters where zero is meaningful.

### R17-F006 — Review harness false FAIL_SCHEMA

**Class:** IMPLEMENTATION / REVIEW-HARNESS.  
**Endpoint:** raw Kimi and DeepSeek reviews completed, but local validation failed.  
**Cause:** shared validator hard-coded historical `repair_sha256_acknowledged`; new schema correctly used `draft_contract_sha256_acknowledged`.  
**Repair:** schema-aware `*_sha256_acknowledged` validation with backward compatibility and fail-closed wrong/missing SHA tests. Exact original model outputs were reparsed with **0 new provider calls**.  
**Re-adjudicated result:** both models PASS the separately authorized provider-runtime Pilot; both keep E1-B HOLD; no blocker.  
**Belief update:** none.

Reusable lesson: preserve model output independently from parser verdict; prefer deterministic reparsing over regeneration.

### R17-F007 — Reparse script import-path failure

**Class:** IMPLEMENTATION.  
**Endpoint:** no review data read, 0 provider calls.  
**Cause:** standalone script omitted repo-root `sys.path` binding.  
**Repair:** explicit ROOT insertion; same raw reviews reparsed.  
**Belief update:** none.

Reusable lesson: evidence-processing utilities need their own reproducible launcher/import contract.

### R17-F008 — Updater runtime qualification coverage gap

**Class:** RUNTIME_INFRA / IMPLEMENTATION.  
**Endpoint:** provider-runtime Pilot held before first provider call.  
**Cause:** the existing `mindmemos-eval-venv` was qualified for actor/evaluator entrypoints, but the provider Pilot requires first-party `mindmemos.pipelines.skill.evolution.SkillEvolver`; the actor venv lacked `omegaconf`.  
**Repair:** create a dedicated updater runtime from the pinned MindMemOS `uv.lock` / `mindmemos` package, then explicitly apply the already frozen R17 renderer compatibility override `tiktoken==0.11.0`. First-party SkillEvolver import, six-arm zero-provider updater qualification and V3.1 regression tests pass.  
**Belief update:** none.

Reusable lesson: **runtime qualification is role-specific and must exercise the exact scientific entrypoint.** Passing actor/evaluator qualification never authorizes updater execution.

### R17-F009 — Non-faithful manual preflight

**Class:** IMPLEMENTATION / PREFLIGHT_MISMATCH.  
**Endpoint:** diagnostic only.  
**Cause:** an initial manual import check did not reproduce MindMemOS source-tree binding and therefore could not find `mindmemos`.  
**Repair:** rerun with the exact execution source binding; this authoritative preflight then revealed F008, the real missing `omegaconf` dependency.  
**Belief update:** none.

Reusable lesson: a preflight that does not reproduce execution binding is diagnostic noise, not authority.

## Qualified success chain so far

The failure ledger does not replace the positive evidence chain.

- **E0:** valid controlled pilot; search-projection censoring exists, but learning consequence remains untested.
- **E1-A V2.1:** valid, complete, 96 exact K=8 pools / 768 rollout refs / 0 technical failures / 0 updater calls.
- **E1-A support:** 78/96 mixed pools, 12/12 exposed streams, 6/6 failure families. This is strong causal-treatment support, **not method-effect evidence**.
- **Current:** provider-runtime Pilot is held until a dedicated updater-runtime V2 contract is independently reviewed.
- **E1-B WIN-A/WIN-B:** not authorized.
- **E1-B MRW causal effect:** unknown.

## Scientific STOP boundary

The first result that can truly kill the central mechanism is a **qualified E1-B endpoint**, not any of the engineering failures above.

If, after valid WIN-A/WIN-B stochasticity control, exact-same-pool MRW vs WIN shows practical equivalence or harm under the frozen decision rule, record it as `SCIENTIFIC_MECHANISM` and STOP the central R17 mechanism on this substrate. Do not relabel it technical, change tasks, or expand to a benchmark zoo to rescue the paper.

## 2026-08-29 continuation

### R17-F010 — Duplicate-launch guard self-match

**Class:** IMPLEMENTATION.  
**Endpoint:** launch not attempted; 0 provider calls.  
**Cause:** a naive `pgrep -af` pattern was embedded in the invoking shell command and matched itself, falsely returning `ALREADY_RUNNING`.  
**Repair:** explicit real-process inspection plus run-root/lock/checkpoint verification showed a zero state; the unchanged frozen contract was then launched exactly once.  
**Belief update:** none.

Reusable lesson: duplicate-launch guards must themselves be self-match safe; the strongest state evidence is the combination of actual runner PID, contract-bound lock, run root and completed-unit/checkpoint manifests.

### R17-S001 — Hosted provider-runtime Pilot V2 PASS

This is a **qualified runtime/measurability success**, not a method-effect success.

- 3/3 arms completed: WIN-A, WIN-B, MRW.
- 30/30 provider-call receipts; exactly 10 per arm.
- 90,608 provider tokens total.
- 0 parse errors; retry=0; thinking disabled; temperature=0.
- 8 trajectory summaries + 1 patch proposal + 1 patch application per arm.
- WIN-A/WIN-B pre-provider evidence byte-identical.
- all arms used `arm_blinded_selected_evidence` and `selected_evidence_trajectory` score semantics.
- arm/projection metadata remained outside model-visible transcript.
- 0 new actor rollouts, 0 held-out evaluations, 0 learned-skill quality comparisons.
- budget ledger reached exactly 30/30 and never exceeded the ceiling.
- exclusive lock was released only after full success.

This validates the repair for R17-F008: the dedicated updater runtime is operational with the real first-party hosted SkillEvolver. It does **not** establish WIN-A/WIN-B behavioral equivalence and does **not** establish an MRW benefit.

Next legitimate gate: separately freeze and independently review the **E1-B WIN-A/WIN-B negative-control-only** contract. MRW scientific comparison remains unauthorized until that negative-control gate passes.
