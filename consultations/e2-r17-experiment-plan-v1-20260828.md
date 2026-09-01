# E2-R17 Experiment Plan V1

Date: 2026-08-28T07:45:00+00:00
Status: **V1_REQUIRES_DUAL_REVIEW_AND_RUNTIME_PILOTS**

## 1. Scientific question and evidence chain

When a self-evolving agent generates a best-of-K search pool, does coupling the acting selector to winner-only learning censor reusable failed evidence and make the acting-optimal trajectory learning-suboptimal?

The paper separates two projections over the same generated search object:

- **Acting projection:** Serve the highest-verifier trajectory from the generated pool.
- **Learning projection:** Choose which content-addressed evidence from that same pool reaches the persistent updater.

Central claim: On precommitted rescue events, winner-only serving removes exactly the failed witness that rollout-0 would have exposed; if that witness has positive reusable diagnostic value, changing only the learning projection changes future frozen skill.

Minimal intervention: **Act from the winner; on a frozen rescue event learn from the precommitted rejected witness, otherwise learn from the winner.**

The evidence chain is deliberately sequential:

`S0 support -> E1 exact-same-pool causality -> E2 public effectiveness -> E3 prospective prediction -> E4 multi-round closure -> E5 topology/external validity`.

A failed earlier gate blocks later evidence. A benchmark zoo cannot rescue a failed exact-same-pool mechanism.

## 2. Current E0 status

The frozen E0 summary is `533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366`. Success@1 is 11/12 and Success@4/8 is 12/12. One rescue task in one family makes censoring nonzero, and the exact observed-pool identity holds, but the frozen threshold is at least six rescue tasks across at least three families.

Decision: **HOLD_FOR_PREDECLARED_E0_FULL**. E1 remains unauthorized.

Two independently generated analyses are retained rather than overwritten:

- `generated/e2-r17-e0-analysis-20260828.json`
- `generated/e2-r17-e0-pilot-analysis-20260828.json`

## 3. Global design rules

- Every stage follows Pilot -> protocol audit -> identifiability qualification -> immutable full contract -> full run -> integrity audit -> statistical analysis -> belief update.
- Pilot may reject an unusable runtime or degenerate capability regime; it may not select a model or baseline because R17 looks better.
- Executor and updater are separate roles. The executor matrix is run first with one frozen updater; a second updater is a later robustness check.
- Requested and resolved model identities, retry=0, thinking disabled, prompts, tool harness, verifier, budgets, and split hashes are frozen per tranche.
- Every completed rollout, pool, projection, update, and frozen evaluation is persisted immediately and content-addressed.
- After any timeout or MCP 502, inspect processes, locks, completed-unit manifests, and summaries before launching anything.

## 4. Model Choice Audit -> candidate matrix

The model matrix follows the closest baselines rather than server convenience. Qwen 4B supplies a weak open target, a precisely named Qwen sparse 35B release supplies the common open axis, DeepSeek V4-Pro supplies a strong literature-backed API axis, and Kimi K3 supplies a second family rather than a direct baseline-match claim.

| Role | Candidate | Status before Pilot |
|---|---|---|
| weak_open | Qwen3.5-4B | PILOT_REQUIRED |
| common_open | exact available Qwen3.5-35B-A3B or Qwen3.6-35B-A3B | AVAILABILITY_AND_PILOT_REQUIRED |
| strong_api | deepseek-v4-pro -> deepseek-v4-pro-ga-260813 | E0_QUALIFIED_REQUALIFY_EACH_TRANCHE |
| second_api_family | kimi-k3 | PILOT_REQUIRED |

Each candidate receives K=1 on 12 fixed development tasks and K=4 on four predeclared search-smoke tasks. Promotion requires 100% task loading and identity stability, >=95% tool parsing and verifier completion, >=90% artifact writing, <=5% technical failures, a verified missing-unit-only resume, and a K=1 result that is neither all-zero nor all-one. No R17 effect size is consulted.

The V1 core updater is `deepseek-v4-pro -> deepseek-v4-pro-ga-260813`. This is a proposal for review, not a frozen full-contract choice.

## 5. Baseline fidelity and placement

| Tier | Methods | Use |
|---|---|---|
| Official core | MindMemOS; RethinkSkill | substrate and matched feedback controls |
| Official extended | SkillOpt; SkillEvolBench | extended quantitative comparison / external validation |
| Paper-spec reconstruction | SkillCAT-style; Branch2Skill-style | explicitly labelled reconstruction, never exact reproduction |
| Context only | TSR | search/topology and compute-control related work |

E1 uses six arms: Winner-only, Precommitted rollout-0, Rejected-Witness, Duplicated Winner, Random Nonwinner, and SkillCAT-style contrast. The public core matrix uses Winner-only, Rejected-Witness, Full Pool, and the simplest surviving method. Extended methods run on one weak/common and one strong representative executor.

## 6. Stage contracts

### S0 — E0-full support qualification

Run only the 42 missing predeclared tasks; never rerun the completed 12. All tasks use K=8 once and derive K=1/2/4/8 from nested prefixes. GO requires >=6 rescue tasks across >=3 families with all integrity checks passing. Insufficient support stops this substrate before any updater intervention.

### E1 — Exact same-pool causal identification

Twelve independent eight-task streams generate 96 exact K=8 pools. Six cloned arms share task, initial-skill SHA, pool, served winner, actor, verifier, updater, budget, and 18 common held-out K=1 probes. The only treatment is the updater-visible evidence packet.

Primary estimand: `Delta_s = J_s(Rejected-Witness)-J_s(Winner-only)`. Inference uses the 12 stream states, an exact one-sided 2^12 sign-flip test, and a 10,000-draw paired bootstrap. Rollouts and probes are not independent replicates.

GO requires positive mean Delta, p<=0.05, a positive 95% CI lower bound, valid provenance, enough rescue support, and no duplicated-winner equivalence. A same-pool null is a central STOP, not a reason to add benchmarks.

### E2 — Public benchmark effectiveness

#### SpreadsheetBench Verified-400

Before outcomes, split the released 400 tasks by content hash and released metadata only:

| Lane | Tasks | Role |
|---|---:|---|
| Runtime development | 16 | model/baseline qualification; never confirmatory |
| Evolution | 160 | twenty one-step streams of eight tasks |
| Validation | 24 | common candidate-skill acceptance/rollback support |
| Test | 200 | untouched frozen K=1 endpoint |

Each evolution stream starts from the same initial skill across methods, generates one exact K=8 pool per task, updates one cloned state per method, and is paired with ten disjoint test tasks. The 20 stream means are the primary paired units; the 200 test tasks are not treated as 200 independent learned skills.

All four qualified executors run the four core methods. Extended baselines run on two representative executors. The primary metric is average frozen K=1 success with paired model-specific confidence intervals and Delta versus Winner-only. Cross-model averages are descriptive/model-stratified rather than an inflated significance test over four models.

#### SkillEvolBench

Use the official 30 environment-by-skill-family cells. T1-T3 are acquisition and T4-T6 are frozen evaluation. Nested acquisition pools are common across projection arms, while the native updater is used only after official adapter/validator qualification. The cell, not each task, is the scientific unit.

A null/negative Verified-400 transport result cannot be rescued by opening SpreadsheetBench 2.

### E3 — Prospective mechanism prediction

Estimate family-level censoring mass and diagnostic value on calibration units, then hash-freeze effect signs, family ranking, K ordering, and null cells before confirmatory outcomes are opened. Evaluate sign accuracy, rank correlation, calibration, absolute error, and null-cell false positives. A post-hoc fit is not predictive theory.

### E4 — Multi-round persistent evolution

Run L/L, H/Winner, H/Precommitted, H/Rejected, and H/final-method arms. V1 proposes eight independent streams, five rounds, eight tasks per round, and 24 common K=1 probes after each frozen skill state. Report online reward and frozen skill separately; first-round causality is not conflated with later path dependence.

### E5 — Topology and external validity

A 2x2 matched-call factorial compares parallel best-of-8 versus sequential refinement and winner/final-only versus history-preserving learning. This tests whether persistent differences arise from the learning projection rather than compute amount. SpreadsheetBench 2 is optional only after prior GO and a separate pre-outcome evaluator contract.

## 7. Checkpoint-first execution

- `raw/` is immutable and contains every provider-hash-bound trajectory, output workbook, verifier receipt, pool, projection packet, updater input/output, skill pre/post state, and frozen evaluation.
- `checkpoints/` contains completed, missing, and failed unit manifests plus lock metadata.
- `summary/` is fully rebuildable from raw artifacts.
- A pool is frozen immediately after K rollouts; a projection is frozen before update; an update stores candidate/accepted/rejected states; each skill-by-held-out-task evaluation is persisted immediately.
- Resume verifies SHA-256 and executes only missing units. Completed provider calls are never repeated after timeout, disconnect, or duplicate launcher invocation.

## 8. Calls, tokens, and compute budget

Empirical E0 rate: E0-r3: 96 actor rollouts, 566 provider calls, 1711693 total tokens, or 5.896 provider calls and 17830 tokens per actor rollout.

| Stage | Actor rollouts | Provider/update calls | Actor tokens | Compute placement |
|---|---:|---:|---:|---|
| S0 missing 42 tasks | 336 | ~1981 actor calls | ~5990926 | Ark + CPU workbook execution on 69 |
| E1 pools + frozen evaluation | 2064 | ~12169 actor + 720 updater calls | ~36801400 actor tokens | Ark + CPU workbook execution on 69 |
| Verified core, 4 models x 4 methods, primary partition | 10880 | 3200 updater calls plus actor-call expansion measured in Pilot | fixed after per-model Pilot | API models on 69; Qwen 4B on 60/52; Qwen 35B preferably 232 |
| SkillEvolBench example, 4 models x 4 methods, K=8 | 4320 | native updater budget frozen after adapter Pilot | fixed after Pilot | official harness-qualified placement |

The plan deliberately does not invent monetary cost or live-updater token estimates. V3 binds current model prices and Pilot receipts before a full authorization.

## 9. GO / HOLD / STOP discipline

- S0 insufficient support: STOP this substrate before E1.
- E1 exact-same-pool null or duplicated-winner equivalence: central mechanism STOP.
- Public positive only in a bounded model/benchmark regime: HOLD and report the boundary; do not add a rescue benchmark.
- Prospective prediction failure: delete predictive-theory claim even if the method improves average success.
- Rejected-Witness matches any complex variant: keep Rejected-Witness and delete the extra method name.

## 10. Next gate

Kimi K3 and DeepSeek V4-Pro independently review this exact V1 artifact for model selection, baseline fidelity, benchmark roles, Pilot nonselection, sample size, inference, checkpoint/recovery, cost, and decisive STOP rules. V2 changes only verdict-relevant defects. Runtime Pilots and every full experiment remain unauthorized until their own content-addressed contracts are frozen.
