# Agent Constraint Externality — Minimum Effective Experiment Plan

Date: 2026-09-04
Scientific object: `AGENT-CONSTRAINT-EXTERNALITY-20260831`
Status: **PROPOSAL ONLY — NO NEW EXECUTION AUTHORITY**

## 0. Design principle

The objective is not to maximize trajectories. Every experimental unit must reduce a predeclared scientific uncertainty.

Deletion test:

> If removing an experiment would not leave any core claim, confound, precision requirement, or external-validity question unsupported, do not run it.

Scientific sample size is counted at the **family** level. Repeats, topology arms, and policy branches are technical executions, not independent `n`.

## 1. Current prerequisite chain

Current valid state:

1. AppWorld substrate / evaluator / exactly-once protocol: qualified.
2. Historical CodingPlan/MiMo capability: useful design evidence, but its actor harness is retired and cannot be inherited as clean-direct evidence.
3. Old F0 source: `8/8` target success → zero repair families → source-substrate stop, not a topology result.
4. SQ0-V5: development evidence only; invalidated by native-tool transport contamination.
5. Direct-SFQ-A0: 12 fresh cases, 12/12 public-oracle reachable, execution blocked by direct-provider credit.
6. Direct Qwen3.7-Flash V4-R1: provider `insufficient_credit`, zero valid capability measurements; any recovery requires a fresh R2 ledger.

No collateral-externality / topology / GTCC scientific result exists yet.

## 2. Gate 0 — clean direct actor capability

Run only after a separate provider-credit readiness check passes.

- New R2 execution ID and new exactly-once ledger.
- Repaired V4 substrate and frozen 16-tool budget.
- No inheritance of the failed R1 unit as a successful measurement.
- No automatic model search based on capability outcomes.

If the selected direct actor fails floor/ceiling/interface, stop and adjudicate before any source-failure or mechanism work.

## 3. Gate 1 — Direct-SFQ-A0

Purpose: establish that fresh cases produce **normal, semantic, repairable target failures**.

Frozen current development set:

- 12 cases = 6 FG + 6 TNF.
- 12/12 public-oracle reachability.
- Max oracle path 48 / development cap 80; min headroom 32.
- Zero case/instruction/fixture/resource hash overlap vs SQ0 V1–V5 + old F0.

A valid failure requires:

- normal scientific terminal;
- target evaluator false;
- no provider / transport / harness / malformed-tool / forced-cap failure;
- complete target-relevant trajectory available.

If this gate does not yield a usable repair-opportunity regime under a clean actor, stop. Do not keep making new challenge versions until one passes.

## 4. Repeat/stochasticity qualification — development only

Before any confirmatory collateral outcome, use a small disjoint development-only matched set to determine repeat count.

Proposal:

- 4–6 development families, permanently excluded from confirmatory analysis;
- repeated identical conditions sufficient to estimate endpoint agreement / within-family execution variance;
- freeze `R* ∈ {2,3}` before confirmatory outcomes;
- default preference is `R*=2`; use 3 only if the preregistered stability criterion fails under two repeats.

The exact stability threshold must be frozen in a pre-execution review. Repeat count may not change because an effect is near a significance or magnitude threshold.

## 5. RQ1/RQ2 primary confirmatory panel

### 5.1 Candidate pool and eligibility

Prospectively generate a 24-family reserve pool, balanced across FG/TNF, before any confirmatory collateral result.

Family eligibility is determined only by pre-topology / pre-collateral facts:

1. valid semantic source failure;
2. valid frozen repair artifact;
3. positive repair uptake on one topology-neutral `TARGET_ONLY_VERIFICATION` surface instantiated from the common pre-update snapshot with the exact frozen repair bytes;
4. no interface/measurement invalidity.

The target-only verification is completed before INDEPENDENT/LOW/HIGH assignment is evaluated. Its outcome may determine family eligibility because it is pre-treatment for the topology question. Once a family enters the confirmatory topology panel, later target success/failure inside INDEPENDENT/LOW/HIGH is a treatment-responsive outcome and never a reason to drop that family.

After development-only precision analysis, freeze:

- `N* ∈ {12,16,20,24}` eligible families;
- `R* ∈ {2,3}` repeats.

Select the first `N*` eligible families in a frozen stable-hash order. Reserve families are activated only for preregistered eligibility attrition. Never backfill after seeing non-target outcomes.

Operational default for budgeting only: `N*=16, R*=2`.

### 5.2 RQ1 — collateral phenomenon

For every eligible family:

- same pre-update snapshot;
- `NO_UPDATE`;
- `REAL_REPAIR` with exact frozen bytes;
- retain the family in every frozen topology arm regardless of post-treatment target success;
- report target-repair retention jointly with collateral outcomes;
- report family-level pooled update externality `UE = CRR_UPDATE - CRR_NO_UPDATE` over the full prequalified panel.

A stronger claim specifically about collateral regressions from a *still-effective* local repair requires a prospectively frozen panel-level target-retention falsifier; it must not be obtained by deleting topology arms/families whose target repair later fails. If HIGH or another topology materially destroys target efficacy, report that as part of the topology treatment and narrow the externality interpretation rather than conditioning it away.

Default budget at `N*=16,R*=2`:

`16 families × 3 topology arms × 2 branches × 2 repeats = 192 probes`.

Absolute reserve envelope at `N*=24,R*=3`: 432 probes.

### 5.3 High-information sham control

Predesignate a balanced subset before outcomes (default first 8 primary families by stable hash).

Add `SHAM_UPDATE`:

- same persistent update surface;
- same general formatting and approximate length budget as real repair;
- no target-specific action rule;
- generated/frozen before collateral outcomes;
- run only on INDEPENDENT and HIGH topology extremes.

Readout:

- REAL vs NO_UPDATE;
- SHAM vs NO_UPDATE;
- REAL vs SHAM.

Purpose: rule out the alternative that collateral changes arise merely from extra persistent text/context rather than repair semantics.

Default extra budget with `R*=2`: `8 × 2 topology × 2 repeats = 32` episodes.

### 5.4 RQ2 — topology mechanism

Only if RQ1 establishes a meaningful collateral phenomenon.

Primary contrast:

`UE_HIGH - UE_INDEPENDENT`.

Secondary:

- ordered HIGH / LOW / INDEPENDENT pattern;
- graph distance;
- shared-resource exposure;
- heterogeneity by FG/TNF family type.

No new dataset is created for RQ2; it reuses the RQ1 matched panel.

## 6. RQ3 — untouched prospective prediction

Pre-generate 16 held-out candidate families, disjoint from all source-development and RQ1/RQ2 families.

Before outcomes freeze:

- eligible target `H* ∈ {12,16}`;
- ExposureRank;
- tie-breaks;
- `k` from the allowed future probe budget;
- all ablation rankings.

Run only the UPDATE/NO_UPDATE evidence needed to label update-attributable regression.

Default efficient budget: `H*=12 × 2 branches × R*=2 = 48` probes.
Maximum planned budget: `16 × 2 × 3 = 96`.

Offline baselines on the **same outcomes** (zero extra actor calls):

- Random ranking;
- Same-App ranking;
- shared-resource-count only;
- graph-distance only;
- full ExposureRank;
- outcome-aware oracle ranking as upper bound only.

If held-out enrichment fails, stop the topology-prediction claim and do not open GTCC.

## 7. RQ4 — conditional mitigation

Open only after RQ1, RQ2, and RQ3 pass.

Pre-generate 16 fresh policy-evaluation candidates. Freeze `M* ∈ {8,12,16}` before policy outcomes; default budget target is 12.

Policies:

1. Always Commit;
2. Target-Only Validation;
3. Random-k Collateral Check;
4. Same-App-k;
5. GTCC.

Fairness:

- Random-k / Same-App-k / GTCC use the exact same `k` and total probe budget;
- paired family/snapshot evaluation;
- Full Non-target Check only on a prespecified small subset (default 6 families) as an oracle/upper bound.

Default budget: `12 × 5 policies × R*=2 = 120` policy episodes.
Maximum planned budget: `16 × 5 × 3 = 240`.

Report:

- target success / repair gain;
- collateral regression rate;
- commit rate;
- paired policy delta + CI;
- LLM requests;
- tool calls;
- wall-clock cost.

If GTCC is practically equivalent to Random-k or Same-App-k under the frozen meaningful-effect margin, stop the GTCC novelty claim instead of enlarging the sample to chase significance.

## 8. External validity — conditional, minimal

### 8.1 Secondary actor

Only after the primary RQ1/RQ2 result is established.

Start with one additional capability-qualified actor on 8 stratified primary families:

`8 × 3 topology × 2 branches × R*=2 = 96` episodes by default.

A second actor is authorized only if the first secondary actor leaves a material model-dependence ambiguity that changes claim scope.

### 8.2 Existing updater compatibility

Higher information value than adding many more models:

- choose one AppWorld-compatible existing self-evolution updater (ACE is the preferred candidate);
- generate/freeze its update bytes first;
- run the same collateral audit on ~6–8 fresh families;
- treat this as compatibility/generalization, not a causal baseline against a different writer.

## 9. Longitudinal — only if claim expands

Do not run by default.

Only if the paper claims repeated self-evolution rather than single-update externality:

- small pre-frozen family set;
- repeated local repairs over a fixed horizon;
- compare Always Commit / Target-Only / GTCC;
- read accumulated collateral regression, recovery, and target utility.

The longitudinal panel exists to support a persistence claim, not to increase experiment count.

## 10. Baseline taxonomy

### Causal controls

- NO_UPDATE;
- SHAM_UPDATE subset;
- INDEPENDENT topology;
- LOW / HIGH topology.

### Mitigation baselines

- Always Commit;
- Target-Only Validation;
- Random-k;
- Same-App-k;
- GTCC;
- Full Check upper bound.

### Generalization checks

- one secondary actor first;
- one real external updater plug-in if needed.

Do not place ACE / SkillOpt / SkillRevise / Memory-R1 in the main causal baseline table when they change update generation or acceptance semantics; that would destroy exact-same-update identification.

## 11. Precision and expansion rules

Before confirmatory execution, freeze:

- smallest scientifically meaningful effect for RQ1 / RQ2 / RQ4;
- desired family-level CI precision;
- paired analysis procedure;
- missingness/invalidity handling;
- `N*`, `R*`, `H*`, `M*` selection rules;
- reserve-family ordering.

Expansion is allowed only from **confirmatory-effect-independent** quantities. Pre-topology target-only eligibility may be used, but target retention inside topology arms and all non-target/topology effect directions may not. Allowed inputs include:

- development-only variance/stability;
- preregistered source-failure / topology-neutral target-only repair-uptake eligibility attrition;
- missingness/interface invalidity;
- preregistered precision calculation performed before confirmatory collateral outcome access.

Forbidden reasons to expand:

- p-value is almost significant;
- effect has the desired sign but CI is inconvenient;
- HIGH-LOW difference is smaller than hoped;
- one baseline performs unexpectedly well.

## 12. Claim-aligned stop ladder

`clean capability`
→ `valid semantic source failure`
→ `positive topology-neutral target-only repair uptake`
→ `freeze confirmatory family panel`
→ `RQ1 collateral phenomenon + joint target-retention readout`
→ `RQ2 topology mechanism`
→ `RQ3 held-out prediction`
→ `RQ4 GTCC`
→ optional `secondary actor / external updater / longitudinal`.

A failed layer closes dependent layers. This is scientific identification discipline, not merely cost saving.
