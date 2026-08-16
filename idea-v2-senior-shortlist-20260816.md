# Multi-Idea Senior Shortlist — 2026-08-16

Source run: `shadow-20260816-v2-multiidea-r1`  
Discovery operator: `anomaly-first-deadend-inversion-v2`  
Control snapshot: `f07d7474d3bc69bda4d741a76e6bf20b57ba15e058ca53def14e819f8799e20f`  
Scientific authority: **0**. This is a senior-discussion shortlist, not canonical Problem-Gate PASS.

Search accounting: 43 raw seeds → 38 semantic-unique → 24 evolution parents → 14 selectively formulated branches → 2 machine `reduction_pending` provisional problems. One malformed `NEW_CAPABILITY_QUESTION` expansion was archived and not retried. STRI remains on a separate single-writer paper track.

## 1. Router-Capacity Saturation in Co-Evolving Skill Libraries — TOP PRIORITY

**Status:** `REDUCTION_PENDING`; evidence design PASS; independent evidence review `REVISE` (contract repair only, not scientific-object rejection).

**Problem.** Skill growth and router adaptation may be complementary only below a capacity-dependent crossover. Once semantically confusable executable skills exceed a fixed-capacity router's discriminability, adding skills can reverse from helping to hurting even when mean single-skill quality does not fall.

**Exact prediction.** For fixed query distribution, model/tool interface, and router capacity `C`, there is an `L*(C)` such that performance rises for `L < L*(C)` but falls for `L > L*(C)`, accompanied by higher top-1 confusion and lower selected-skill applicability. Raising router capacity or coverage-preserving pruning/dedup should move/recover the crossover. The effect should be substantially weaker under one-sided freeze controls.

**Strongest reduction.** Same-information non-stationary online routing / retrieval-utilization account: ordinary selector miscalibration, retrieval precision loss, or uptake failure may explain the reversal without a capacity threshold.

**Decisive falsifier.** Cross `library size/confusability × router capacity` with four evolution cells (both evolving / router frozen / skills frozen / both frozen), while matching query distribution, task coverage, compute, update count, and mean single-skill quality. Measure routing confusion, applicability, execution success, and final retrieval score.

**Evidence design.** Bounded contract: ≤128 units, ≤256 model calls, ≤1 GPU-hour. Independent reviewer accepted all scientific checks but requested one repair: remove mandatory dependency on specific Skill-SP/ERSkill source code and define the same frozen interface in a self-contained first-party simulation. This can be repaired without changing prediction or baseline.

**Why it is worth showing:** strongest current new candidate; directly about self-evolution, has a crossover mechanism rather than a generic ablation, and already survived machine formulation into the bounded-evidence path.

## 2. Trace-Authored Defense Persistence as Local-Commit / Global-Block Inconsistency

**Status:** `REDUCTION_PENDING`, but bounded evidence design currently INVALID; discussion-only until the experimental contract is cleaned.

**Problem.** A persistent runtime-defense patch may be locally justified by an attack trace and reduce current ASR, yet globally block future benign requests because the update-time replay set cannot represent the future benign distribution. The object is replay-incomplete persistence, not a scalar security–utility tradeoff.

**Exact prediction.** Holding patch text, model, attack traces, current ASR/UA, threshold, and rollback API fixed, more complete pre-persistence benign replay should reduce later global blocking; a same-information scalar threshold/rollback policy without representative future replay should not distinguish blocking from preserving patches.

**Strongest reductions.** Semantic transactions / rollback / irreversible-effect safety, plus snapshot-validity/adaptive-validation theory.

**Cheapest falsifier.** Matched defense patches with identical current state and different replay completeness; evaluate later benign UA and irreversible block rate.

**Current blocker.** Evidence designer introduced a forbidden method/hidden-tuning dependency. Do not execute until a cleaner outcome-independent replay-completeness intervention is compiled.

## 3. Note-Conditioned Evidence Debt in Mutable Document Agents

**Status:** high-potential `REVISE-SCHEMA + SUPPORT`; successful principle inversion of the failed P06 coverage idea.

**Opposite principle.** Evidence sufficiency is relevance-conditioned, not coverage-conditioned.

**Problem.** A mutable document agent can know what it read and what it wrote into notes, but page-count coverage cannot tell whether omitted evidence could change the answer. Define an observable evidence-debt state over `search results + read pages + notes + tree` that predicts answer change from read-but-unnoted evidence and is invariant to irrelevant unread/unnoted material.

**Exact prediction.** The debt statistic should rank units whose answer changes when omitted read evidence is restored above matched no-change units, while not increasing when irrelevant unread/unnoted content is added; it must beat same-information confidence/consistency/note-sparsity/coverage baselines without hidden evidence labels at decision time.

**Cheapest falsifier.** Query-level DocAtlas-style logs with controlled restoration of read-but-unnoted evidence; compare held-out answer-change prediction to the strongest generic uncertainty/conservatism baseline.

**Current blockers.** Formulation used non-canonical reduction aliases in `saturation_scan`, and released/provenance-audited query-level state logs are not yet established. Scientific content is promising; machine status is not PASS.

## 4. Shared-Budget vs Fixed-Width Latent Retrieval in On-Policy Self-Distillation

**Status:** high-potential `REVISE-SCHEMA`; exact reduction test defined.

**Problem.** Reported latent self-distillation shows a sharp token-width jump near 32 tokens and retrieval gains from 1→3 followed by plateau. The key question is whether the boundary is a minimum usable *per-experience* representation width, rather than total context capacity alone.

**Exact prediction.** At fixed total latent budget `B`, fixed-width allocation should fail when `w=B/k` falls below `w_min`, while a shared-pool allocator can outperform by giving ≥`w_min` tokens to the most useful experiences. If a smooth information-bottleneck/rate-distortion capacity model predicts the same curves, the new object disappears.

**Cheapest falsifier.** Factorial over retrieval count `{1,2,3,4,6,8}` at fixed total latent budget (e.g. 96), comparing fixed-width vs nonuniform shared-pool allocation on the same retrieved set.

**Current blocker.** Exact mature reduction remains unresolved and the formulation used a descriptive rather than canonical saturation-ledger key. No experimental negative exists.

## 5. Test-Time Compute Sign Reversal: Raw VLA Trajectories vs Skill-Harness Units

**Status:** `REVISE`; strong mechanism story, machine formulation blocked by incomplete mature-baseline coverage.

**Problem.** Under tied candidate budget, raw VLA selection/voting can underperform direct execution while full externalized skill/harness evolution strongly improves over the seed agent. Does the sign depend on candidate representation after matching candidate quality/diversity/verifier availability?

**Exact prediction.** The raw-versus-harness sign difference persists after matching candidate success, diversity, redundancy, verifier availability, and compute, but disappears when contract-bearing harness units are flattened into unstructured text/raw trajectories.

**Strongest current baseline.** Generic test-time scaling/search. A second mature theory baseline is still required before falsifier eligibility.

**Cheapest falsifier.** Matched raw-VLA and skill-harness candidate pools; direct execution vs MG-Select/VOTE in both layers plus a flattening control.

## 6. Dual-Use Skill Memory Under Fixed Retrieval Budget

**Status:** second-wave `REVISE`; interesting safety/memory story but still close to procedural-memory nonmonotonicity.

**Problem.** The same persistent skill-memory mechanism can turn failure history into useful guardrails while also preserving unsafe-success procedures. Under a fixed retrieval budget, harmful and protective procedures may compete for slots, creating a safety crossover rather than a monotone memory-benefit curve.

**Exact prediction.** There exists an intermediate retrieval regime where unsafe-success procedures displace guardrail/recovery procedures, raising carryover ASR while lowering avoided-error rate; larger budgets that retrieve both can restore guardrail benefit.

**Strongest reduction.** Nonmonotonic/defeasible rule conflict and priority semantics with the same retrieval information.

**Cheapest falsifier.** A versioned skill-state substrate with matched protective and unsafe-success artifacts; sweep top-k/priority under fixed tasks/model and measure carryover ASR plus avoided repeated-error rate.

**Current blocker.** Mature procedural-memory reduction remains unresolved and saturation-scan keys need canonicalization. Keep as a backup/safety-oriented discussion direction.

## Explicitly rejected / do not sell to the senior collaborator

- **Simple frozen-skill × frozen-router 2×2 interaction:** rejected as a standard component-interaction/co-evolution ablation already substantially implied by the cited papers.
- **Security–utility release from current ASR/UA alone:** rejected into existing contextual constrained-governance / accumulated-restrictiveness basins.
- **Unsafe authorship inferred from later carryover harm:** already covered by the source lifecycle-attribution object.
- **Harness small-n verification as a standalone problem:** current evidence supports small-n noise, not a new lineage-specific mechanism.

## Recommended discussion order

1. Router-Capacity Saturation — strongest and closest to a bounded falsifier.
2. Note-Conditioned Evidence Debt — strongest principle inversion; new observable needed.
3. Shared-Budget Latent Retrieval — cleanest low-cost factorial if source assets are runnable.
4. VLA vs Skill-Harness Sign Reversal — strongest embodied/ICLR story but support and baseline burden higher.
5. Trace-Authored Defense Persistence — strong systems/safety framing, experiment contract needs repair.
6. Dual-Use Skill Memory — backup, especially if a safety-oriented venue/line is desired.

STRI remains the only paper-writing track. These six are discovery/evidence candidates only; none receives canonical Problem-Gate, Method, P0, or GPU authority from this shortlist.
