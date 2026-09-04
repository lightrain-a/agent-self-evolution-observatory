# Agent Constraint Externality — Mainline Brief

## Working title

**Do Local Repairs Stay Local? Constraint-Coupled Externalities in Self-Evolving Agents**

## One-sentence object

A persistent repair may be target-local in intent but non-local in effect; this paper asks whether a successful target repair causes previously satisfied non-target constraints to regress, and whether outcome-blind shared-state/prerequisite topology causally moderates and prospectively predicts that risk.

## SkillZip / SkillZip Pro transfer

The paper adopts four reusable principles from the existing SkillZip notes:

1. **Define the real execution object before proposing a method.** Here the object is not “a memory string” but a repair family with target failure, frozen repair bytes, previously satisfied non-target constraints, matched snapshots, and an outcome-blind coupling graph.
2. **Expose the abstraction mismatch first.** Capability PASS does not imply source-failure availability; local repair intent does not imply local effect; mechanism contrast does not substitute for phenomenon existence.
3. **Use hard invariants to defend the object.** Exact repair bytes, same-snapshot UPDATE/NO_UPDATE, outcome-blind edges, no replay after durable dispatch, and disjoint development/confirmatory cases are scientific invariants rather than engineering details.
4. **Let the minimum method follow from evidence.** GTCC is conditional on phenomenon + topology mechanism + prospective held-out prediction; if Random-k is equivalent, the method claim stops.

## Claim ladder

`valid semantic source failure`
→ `positive target repair`
→ `pooled update-attributable collateral phenomenon`
→ `same-update topology causal contrast`
→ `prospective held-out structural prediction`
→ `minimum GTCC mitigation`
→ optional `cross-model / longitudinal generalization`

No layer may be promoted by evidence from a later or invalid layer.

## Current evidence

- Historical MiMo 2.5 Pro capability gate: PASS (`7/8` target success; `7/8` tool-loop completion; `8/8` non-target preservation).
- Old F0 source: `8/8` target success → `0` target failures → `0` repair families → `0` mechanism probes. Classification: source-substrate stop, not topology negative.
- SQ0-V5: six usable semantic FG failures before TNF-01 invoked AtomCode-native `read_file`; the whole qualification is invalid under the frozen non-semantic-failure rule. Development evidence only.
- Direct-SFQ-A0: 12 fresh cases, 12/12 public-oracle reachable; max public path `48/80`; min headroom `32`; zero overlap in case IDs, instruction hashes, fixture hashes, and target-resource hashes vs SQ0 V1–V5 + old F0. Model execution pending.
- Collateral externality outcomes: `0`.
- Topology mechanism outcomes: `0`.
- GTCC outcomes: `0`.

## RQs

### Gate 0 — Capability
Can the actor operate the representative AppWorld tasks under a clean, interpretable harness?

### Gate 1 — Source-failure qualification
Do fresh cases yield normally terminated semantic target failures that can legally generate repairs?

### RQ1 — Phenomenon
When target repair succeeds, does UPDATE increase non-target collateral regression relative to NO_UPDATE from the same snapshot?

Primary object: pooled update externality `UE = CRR_UPDATE - CRR_NO_UPDATE`.

### RQ2 — Mechanism
Conditional on the phenomenon, does constraint coupling causally moderate it?

Primary contrast: `UE_HIGH - UE_INDEPENDENT`; LOW is an ordered secondary arm.

### RQ3 — Prospective prediction
Can an outcome-blind, parameter-free ExposureRank enrich future collateral regressions in top-k on untouched held-out families versus same-k random ranking?

### RQ4 — Minimum mitigation
If RQ1–RQ3 pass, does GTCC reduce collateral regression at matched probe budget versus Always Commit, Target-Only Validation, Random-k, and a coarse Same-App-k heuristic? Full Non-target Check is an oracle/upper bound, not a same-cost baseline.

## Minimum sufficient experiment workload (proposal only; no execution authority)

The current engineering/qualification history is large, but it does **not** count as submission-ready scientific breadth. The minimum useful workload should be claim-aligned rather than a benchmark/model grid for its own sake.

### Must-have A — Primary controlled mechanism panel
- `24` fresh confirmatory repair families, balanced `12 FG + 12 TNF`.
- Family is the scientific unit; episodes are technical repeats.
- Each eligible family: `3 topology arms × 2 UPDATE/NO_UPDATE branches × 3 fixed repeats = 18` probe episodes.
- Maximum primary probe envelope: `24 × 18 = 432` episodes, plus one source episode and one frozen repair generation per family.
- This single panel answers RQ1 and RQ2; do not create separate mechanism datasets unless the protocol itself changes.

Why 24 rather than the old 8: the old design leaves too little independent family-level support after source-failure and repair-uptake exclusions. Twenty-four gives balanced family types and room for invalid/ineligible families without treating repeated episodes as independent `n`.

### Must-have B — Prospective prediction panel
- `16` untouched families, balanced `8 FG + 8 TNF`, disjoint from source-development and RQ1/RQ2 families.
- ExposureRank, all ablation rankings, tie-breaks, and `k` are frozen before outcomes.
- Only the UPDATE/NO_UPDATE evidence needed to label update-attributable regression is executed; the full three-arm causal matrix is not repeated unless required by the prediction estimand.
- Recommended envelope: `16 families × 2 branches × 3 repeats = 96` probe episodes.
- Offline baselines/ablations on the same outcomes: Random rank, Same-App rank, shared-resource-count-only, distance-only, full ExposureRank, plus a post-hoc oracle ranking reported only as an upper bound.

### Must-have C — Mitigation panel
- `16` additional fresh families, disjoint from RQ3 held-out families.
- Same frozen repair opportunity and snapshot are evaluated under five fair policies: Always Commit, Target-Only Validation, Random-k, Same-App-k, GTCC.
- `k` and total probe budget are identical for Random-k / Same-App-k / GTCC.
- `3` fixed repeats per policy: `16 × 5 × 3 = 240` policy episodes.
- Full Non-target Check is run on a prespecified smaller subset (e.g. `8` families) as an oracle/upper bound rather than inflating the main budget.
- Report target success/repair gain, collateral regression rate, commit rate, paired utility/gain with CI, LLM requests, tool calls, and wall-clock cost.

### Must-have D — One clean cross-model robustness check
- Do **not** repeat the entire paper across seven models.
- Use `2` additional capability-qualified actors on a pre-frozen stratified subset of `12` primary mechanism families.
- Reduced robust check: `12 families × 3 topology arms × 2 branches × 2 repeats × 2 secondary actors = 288` episodes.
- This is supporting external validity; the primary causal unit remains the family, and model cells are not pooled as extra `n`.

### High-value optional expansion — external updater compatibility
Instead of adding many more models, prefer one established self-evolution updater that is close to the deployment story. ACE is especially suitable because it already supports AppWorld-style evolving playbooks. Freeze the external updater output first, then audit the same UPDATE/NO_UPDATE and topology logic on a small balanced panel (e.g. `8` fresh families). Treat this as compatibility/generalization evidence, not a baseline that changes the repair bytes in the main causal comparison.

### Conditional longitudinal expansion
Only if the paper claims persistent multi-update self-evolution rather than single-update externality: use a small pre-frozen panel (e.g. `8` families, `5` update rounds) and compare only Always Commit / Target-Only / GTCC. The purpose is accumulated collateral risk, not another full baseline table.

## Baseline hierarchy

### Causal baselines (mandatory for RQ1/RQ2)
1. `NO_UPDATE` from the same snapshot — identifies update-attributable harm.
2. `INDEPENDENT` topology with exact same repair bytes — identifies the structural topology contrast.
3. `LOW` topology — ordered secondary dose-response arm, not a replacement for the independent control.

### Mitigation baselines (mandatory for RQ4)
1. `Always Commit` — naive persistent local repair.
2. `Target-Only Validation` — common default that checks only whether the repaired target improves.
3. `Random-k Collateral Check` — strongest budget-matched control for “checking something helps.”
4. `Same-App-k` — coarse locality heuristic; tests whether the full graph adds value beyond app identity.
5. `GTCC` — proposed topology-aware policy.
6. `Full Non-target Check` — oracle/upper bound, explicitly excluded from same-cost ranking.

### Existing self-evolution methods
ACE, SkillOpt, SkillRevise, Memory-R1, etc. should **not** be forced into the main causal baseline table if they change update generation, edit acceptance, or memory semantics: doing so destroys the exact-same-update treatment. Use at most one compatible existing updater as a secondary plug-in/generalization experiment. The main baselines must preserve the causal object.

## Paper architecture

1. Introduction — local intent ≠ local effect.
2. Problem formulation — update-attributable collateral regression and outcome-blind topology.
3. Experimental object & Gate 0/Gate 1.
4. RQ1 phenomenon.
5. RQ2 same-update topology mechanism.
6. RQ3 prospective prediction.
7. Conditional GTCC.
8. Main public AppWorld results (only after evidence exists).
9. Heterogeneity / optional cross-model and longitudinal expansion.
10. Related Work, Limitations, Conclusion.

Transport archaeology, provider credit, void runs, and qualification debugging belong in the appendix/reproducibility ledger, not the main story.

## Novelty boundary

Do **not** claim novelty for:
- “memory updates can hurt future behavior”;
- “continuous consolidation can degrade memory”;
- “constraints can be coupled”;
- “graphs can guide repair”.

Defended residual:

**positive target repair × previously-satisfied non-target regression × exact-same-update matched topology × outcome-blind prospective structural prediction.**

If the experiment only recovers generic memory degradation without this treatment-level residual, pivot or stop.
