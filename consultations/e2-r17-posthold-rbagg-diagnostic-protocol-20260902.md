# E2-R17 Post-HOLD RB-AGG Collision Diagnostic

## Status

`PREF0_PROTOCOL_READY_FOR_INDEPENDENT_REVIEW_ZERO_PROVIDER_AUTHORITY`

The parent scientific result remains immutable:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`

This child is a **secondary published-collision diagnostic**. It cannot rescue, enlarge, or recompute the parent MRW-vs-WIN confirmatory sample.

## 1. Question

The parent MRW intervention exposed one deterministic failed witness on mixed pools and produced a positive but inconclusive result. The pre-outcome V3 design already declared a ReasoningBank-style same-pool aggregation diagnostic.

The child asks:

> On the exact same frozen K=8 search pools, does a richer ReasoningBank-style aggregation of all success/failure trajectories produce better future frozen-skill utility than a fresh contemporaneous winner-only control?

This is not an official ReasoningBank reproduction. It is a collision diagnostic on the controlled spreadsheet substrate.

## 2. Parent evidence is not reopened

Parent closeout:

`generated/e2-r17-deepseek-v2-final-scientific-closeout-20260902.json`

Parent status stays HOLD for every possible child outcome.

Forbidden:

- append RB-AGG to the old MRW sample;
- rerun MRW;
- recompute the parent p-value;
- call RB-AGG a rescue;
- promote paper claims automatically;
- open Qwen/GPT/public benchmark automatically.

## 3. Frozen source pools

Use exactly the already-frozen E1-A pools:

- 12 streams;
- 8 update tasks per stream;
- 96 K=8 pools;
- 768 immutable source trajectories;
- 78/96 mixed pools;
- no actor/search rerun.

Pool SHAs are inherited from:

`generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json`.

## 4. RB aggregation semantics

For each task pool exactly once:

1. verify all eight source trajectory SHAs;
2. render each trajectory with the already-frozen 512-token cap;
3. bind its deterministic verifier label `SUCCESS`/`FAILURE`;
4. use the literal `PARALLEL_SI` prompt from ReasoningBank commit `ed80611788292ea739f1effd31f16c53823b8a0d`;
5. one aggregation provider call, temperature `0.7`, max output `1024`, retry limit `0`;
6. strict parser accepts only 1–5 contiguous official `# Memory Item i / ## Title / ## Description / ## Content` blocks;
7. malformed/empty output is fail-closed; no parse-correction provider retry;
8. freeze the normalized Markdown and all source provenance before updater execution.

The aggregation model is **not source-faithful ReasoningBank**. For this controlled collision diagnostic it must be the same freshly qualified DeepSeek route/model family used by the MindMemOS updater, with thinking disabled. The exact resolved model is contract-bound before provider I/O.

## 5. Semantic adapter into MindMemOS

ReasoningBank Memory Items are never represented as a single trajectory.

Each task creates:

- one explicit synthetic **K=8 search-session add record**;
- one 1:1 **precomputed SkillTraceSummary** whose text is the normalized RB Memory Items.

The matching precomputed summary must exist before `SkillEvolver.evolve` is entered. Direct MindMemOS trajectory summarization of the synthetic search-session record is forbidden.

### Score semantics

The summary score is the frozen K=8 search-session `acting_success`.

This is semantically truthful: it is the actual user-facing outcome of that search session. It is also exactly equal, task-by-task, to the WIN winner trajectory score under the frozen binary best-of-K selector.

The zero-provider semantic preflight proved:

`RB session score == WIN selected winner score` on `96/96` pools.

Therefore the scored-patch label vector is not an extra source of advantage for RB-AGG.

## 6. MindMemOS update semantics

After the eight RB summaries for one stream are frozen:

- same initial `SKILL.md` SHA as parent;
- first-party `SkillEvolver`;
- `min_aggregate=max_aggregate=8`;
- `use_trajectory_score=true`;
- same `PROPOSE_PATCH_SCORED_SYSTEM`;
- same apply-patch parser;
- same `rewrite_skill=false`;
- same `temperature=0` for MindMemOS patch calls;
- same retry limit `0`;
- at most one explicit parse/apply correction, exactly as Repair2;
- no first-party trajectory-summary calls, because PARALLEL_SI replaces that summary stage.

Nominal provider-call accounting per stream:

- 8 RB aggregation calls;
- 4 updater replicates × (1 propose + 1 apply) = 8 MindMemOS calls;
- total nominal = 16.

Hard maximum with one visible apply correction in every replicate:

- 8 aggregation + 4 × 3 updater calls = 20 per stream;
- 240 calls across all 12 streams before heldout evaluation.

The parent WIN updater also used nominally 10 calls per replicate (8 trajectory summaries + propose + apply). RB-AGG substitutes its 8 aggregation calls for the first-party per-trajectory summary stage; it does not stack a second updater pipeline.

## 7. Why a fresh WIN-D control is mandatory

Do **not** compare new RB-AGG states only to historical WIN-C. Provider/runtime behavior may drift with wall-clock time even under the same model identity.

The full diagnostic, if later authorized, must run contemporaneously:

- `WIN-D`: fresh winner-only updates using the already-frozen parent evidence renderer and first-party updater;
- `RB-AGG`: fresh same-pool aggregation updates;
- same stream/replicate schedule;
- hash-balanced arm order;
- same initial skill;
- same heldout evaluator;
- same resolved model identity.

Historical WIN-C/MRW results do not enter the child primary statistic.

## 8. Full diagnostic scientific unit — only if later authorized

Per arm:

- 12 streams;
- 4 fresh updater replicates per stream;
- 48 learned states;
- common 18 parent heldout tasks per state;
- K=1 evaluator;
- 864 heldout evaluations per arm.

Two-arm child total:

- 96 fresh learned states;
- 1728 heldout evaluations;
- zero new K=8 search trajectories.

For stream `s`:

`D_s^RB = mean_r [ J_{s,r}(RB-AGG) - J_{s,r}(WIN-D) ]`.

Independent units are the 12 stream effects.

## 9. Secondary diagnostic inference

Predeclare one RB-vs-WIN-D contrast only:

- exact one-sided sign-flip over `2^12` stream effects;
- alpha `0.05`;
- mean `D_s^RB > 0`;
- 95% paired-stream bootstrap lower bound > 0 for a strong positive diagnostic;
- paired TOST with `epsilon=1/18` reported to distinguish practical equivalence from unresolved noise.

This is **secondary collision evidence**, not the parent primary test.

Possible interpretations:

- RB superior: broader same-pool aggregation can have persistent-learning value where the minimal witness result was inconclusive; the paper must narrow away from a simple MRW method claim and acknowledge stronger ReasoningBank-style collision.
- RB practically equivalent: no evidence that this richer aggregation baseline improves the controlled substrate; parent MRW HOLD remains HOLD.
- RB harmful: aggregation itself can degrade persistent learning on this substrate; parent HOLD remains HOLD.
- neither superiority nor equivalence: diagnostic remains unresolved.

No outcome permits parent GO.

## 10. Zero-provider qualification already passed

Semantic adapter preflight:

`generated/e2-r17-posthold-rbagg-zero-provider-semantic-adapter-preflight-20260902.json`

- 96/96 pools verified;
- 78 mixed reproduced;
- score vector exact to WIN on 96/96;
- scored proposer on 12/12 streams;
- provider calls 0.

Actual first-party path preflight v2:

`generated/e2-r17-posthold-rbagg-zero-provider-actual-path-preflight-v2-20260902.json`

- fixed pilot stream `e1-agj-00`;
- 8 search-session add records;
- 8 precomputed summaries;
- 0 first-party trajectory-summary calls;
- real in-memory Qdrant + real `SkillEvolver`;
- fake propose/apply exactly 2 calls;
- real patch parser exercised;
- one evolved version;
- provider calls 0;
- heldout evaluations 0.

V1 actual-path preflight was superseded only because an over-strict byte-equality assertion did not account for first-party `.strip()` removing one trailing newline. Its root remains preserved.

## 11. Next gate: independent protocol review

Before any provider I/O, reviewers must answer:

1. Is session-level `acting_success` a truthful score for a multi-trajectory search-session summary?
2. Does exact score equality to WIN remove score-label confounding?
3. Is inserting PARALLEL_SI at the precomputed-summary boundary faithful enough to call this `ReasoningBank-style`, while explicitly not calling it source-faithful?
4. Does the 1:1 synthetic add-record/precomputed-summary construction preserve MindMemOS provenance rather than spoof a trajectory?
5. Is a fresh contemporaneous WIN-D control sufficient to close post-HOLD wall-clock drift?
6. Is one frozen RB aggregation per task, reused across four updater replicates, the correct way to isolate updater stochasticity?
7. Are call/token differences properly classified as part of the broader aggregation method rather than a matched-compute causal arm?
8. Does the interpretation strictly prevent RB-AGG from rescuing the parent HOLD?

Only after review PASS may a single fixed-stream **semantic provider pilot** be separately authorized.

## 12. Semantic provider pilot, if authorized

Fixed stream: `e1-agj-00` by lexicographic predeclared stream order.

Exactly:

- 8 PARALLEL_SI provider calls;
- strict parse of all eight outputs;
- one MindMemOS updater replicate from those eight summaries;
- nominal 2 MindMemOS calls, hard max 3 with one visible apply correction;
- total nominal 10, hard max 11 provider calls;
- zero heldout evaluation;
- zero skill-effect inference.

The pilot output skill is quarantine-only and can never enter the full diagnostic sample.

Pass requires:

- 8/8 aggregation outputs parse;
- exact required resolved model on every call;
- retry limit 0 and no hidden retry;
- 0 ambiguous provider responses;
- 8 precomputed summaries consumed;
- 0 MindMemOS trajectory-summary calls;
- exactly one evolved skill version;
- updater calls within frozen 2/3 bound;
- no heldout task touched.

Failure stops and requires explicit adjudication; no auto retry.
