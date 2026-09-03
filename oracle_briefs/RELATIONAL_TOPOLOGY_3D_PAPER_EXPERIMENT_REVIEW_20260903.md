# Independent adversarial review brief — RELATIONAL-TOPOLOGY-STAGE-3D-20260831

## Reviewer role

Act as an independent senior top-tier 3D vision / generative modeling / machine-learning reviewer and methodologist. Treat this as a prospective paper-and-experiment review before any scientific outcome is opened. Do **not** assume the team's current story, causal interpretation, topology construction, or planned P1 is correct. Be adversarial and precise.

The goal is not to make the project larger. Identify the **smallest scientifically valid corrected paper story and experiment**. Do not recommend broad extra experiments unless they are verdict-changing.

End with exactly one paper-direction verdict:

- `KEEP`
- `PIVOT`
- `STOP`

Then list **only verdict-changing fixes**.

## Scientific object and current source of truth

Scientific object:

`RELATIONAL-TOPOLOGY-STAGE-3D-20260831`

Current repository source of truth used for this review:

`origin/main = 11f0b76b85596dfd48823f1c8b6bc7dfde951e36`

This is an independent 3D indoor scene-generation paper. It must not borrow claims from the team's agent/self-evolution paper or PORT-010.

No scientific P1 outcome is available for this review. Training loss, checkpoint state, or runtime progress must not be interpreted as paper evidence.

## Current proposed paper question

Current exact question:

> What makes relationally complex 3D scene instructions difficult when raw relation count, surface length, training support, and relation composition are controlled, and at which generation stage does the attenuation emerge?

Current decisive-experiment description:

`MATCHED_SUPPORT_TOPOLOGY_RESPONSE_SURFACE_WITH_SAME_DECODER_ORACLE_GRAPH`

Current intended figures:

1. count × exact-token-count × training-support × topology response surface;
2. within-count topology contrasts;
3. three-observable stage waterfall;
4. paired predicted-graph versus oracle-graph intervention.

## Claims the team has already rejected

The paper is **not allowed** to claim any of the following as novelty:

- more relations imply lower iRecall;
- relation-aware models win at high relation count;
- another ATISS / DiffuScene / InstructScene count curve;
- decline at 3–6 relations proves intrinsic capacity;
- a mandatory scalar breakpoint C*;
- merely locating where attenuation occurs explains why it occurs.

## Current surviving candidate claims

1. **Matched training-support crossover** under matched architecture, initialization policy, corpus size, scene pool, tokenizer, optimizer, training horizon, and one shared downstream decoder.
2. **Fixed-count / fixed-token topology residual** after training-support regime is controlled.
3. **Predicted-versus-oracle graph stage localization** with exact object/slot/feature identity pairing and the same downstream decoder.

The team currently intends to stop the standalone paper if the future support crossover has no meaningful residual, or if any residual cannot be selectively localized/recovered by the exact-identity oracle intervention.

## Nearest-work collision boundary already identified

### SceneNAT (2026, arXiv 2601.07218v2, revised 2026-08-11)

Known overlap:

- extended InstructScene substrate;
- up to four relations during training;
- iRecall versus relation-count;
- evaluation at 5/6 relations beyond training support.

Consequence already accepted by the team:

> Do not claim relation-count curves, training-to-5/6 extrapolation, generic relational reasoning, or four-relation instructions as novelty.

### GeoSceneGraph (2026)

Known overlap:

- graph-based text-to-scene generation;
- InstructScene reproduction;
- graph-stage versus final-layout relation-recall discrepancy.

Consequence already accepted:

> Merely reporting graph-stage versus final-layout attenuation is not novel. The only potentially distinct stage claim is an exact-identity intervention using the same downstream decoder.

### Other adjacent 2026 work already considered

- Global Graph-Validated Optimization for VLM-based 3D Indoor Scene Generation;
- SDGScenes;
- SPREAD;
- SceneEval.

The team does not intend to claim graph structure, global consistency, relation-aware reasoning, or fine-grained relation evaluation itself as novelty.

## Model pipeline

The relevant InstructScene-style pipeline is conceptually:

`instruction -> semantic graph predictor (SGP) -> shared graph-to-scene decoder (SG2SC) -> generated layout`

The experimental design trains:

- `SGP-12`: semantic graph predictor trained only on relation counts `{1,2}`;
- `SGP-14`: semantic graph predictor trained on relation counts `{1,2,3,4}`;
- `BEDROOM-SG2SC-SHARED`: one graph-to-scene decoder trained on official BEDROOM train scenes using ground-truth semantic graphs.

Later scientific evaluation must use the **same frozen SG2SC decoder** for both SGP arms.

## Current training-support intervention

### SGP-12

- train relation-count support `{1,2}`;
- 12,240 real corpus rows;
- corpus SHA `9884b2afd58e05ed0eb80864154765e55551e5f77632d4fbd6308d0af50dd58b`.

### SGP-14

- train relation-count support `{1,2,3,4}`;
- 12,240 real corpus rows;
- corpus SHA `51e9e6011250970c660d91c75843919f55192b800423d8ad59a2cfb5c08c4b05`.

### Frozen shared invariants

The two SGP arms are required to share:

- architecture;
- parameter count: `51,156,834`;
- initial model state SHA: `efd8ee84bf36e5ebfc9a191155495d5c540f289e20a117356c4b490a4c2fb3f3`;
- CLIP text encoder and revision;
- optimizer and LR / weight decay;
- batch size `128`;
- gradient accumulation `1`;
- one training seed `20260901` for the current developmental tranche;
- 1,000,000 logical optimizer steps;
- same checkpoint schedule, every 50,000 steps;
- same scene pool;
- same total row count;
- same structural example-key order;
- same shared SG2SC decoder;
- frozen augmentation replay invariants.

The training plan currently describes the only intentionally varied factor as:

`TRAINING_RELATION_COUNT_SUPPORT`

However, note carefully: because SGP-14 contains relation-count 3–4 examples and SGP-12 does not, the **marginal relation-count distribution / total relation-edge dose / instruction complexity distribution may also necessarily differ as part of that support regime**, even with equal row count and matched conditional marginals. This is a core causal-identification question for the reviewer.

The static design says the corpora are matched by distribution on:

- relation-family proportions;
- direction proportions;
- instruction style;
- token-length bins conditional on relation count;
- topology policy conditional on relation count.

And exactly matched on architecture, parameterization, room type, dataset revision, split, corpus example count, scene pool, object-count strata, vocabularies, tokenizer revision, optimizer, schedule, training steps, checkpoint policy, seed policy, and shared decoder.

The design explicitly acknowledges one inherent difference:

`COUNT_INDUCED_TOPOLOGY_SUPPORT`: counts 3–4 cannot occur in SGP-12 by definition.

## Current developmental training status — execution only, not scientific evidence

As of 2026-09-03 around 19:40 UTC+8:

### SGP-12 / 232 A100

- no live training actor at the instant checked;
- last heartbeat `107,905` in `segment-0002`;
- latest **durable committed scientific-free checkpoint is step 100,000**;
- checkpoints: 0, 50k, 100k;
- failure ledger: 0;
- no scientific outcome opened.

The run had previously resumed from the exact 100k checkpoint under the recovery contract; the later actor is currently absent. Do not use the non-durable 107,905 heartbeat as a scientific or final training state.

### SGP-14 / 69 A100

- no live training actor at the instant checked;
- latest **durable committed checkpoint is step 100,000**;
- checkpoints: 0, 50k, 100k;
- failure ledger: 0;
- no scientific outcome opened.

### BEDROOM-SG2SC-SHARED / 52 RTX 3090

- live training actor;
- heartbeat around `65,595`;
- latest durable committed checkpoint 50k;
- failure ledger: 0;
- no scientific outcome opened.

The 3090 resource preflight matched the frozen decoder invariants:

- config SHA `429301d308ee6d99c479cc6d7e4a55dca7661f3bec2c29a128e3586e4ea17b7a`;
- content SHA `e1c8be1dad5d02db5aafadaadbbd4f8c69a18aeff100b46938492ffb9f388ce2`;
- first-batch SHA `4adf677d39a155af6175344cf2062074c8ade4c0ce95bcee9f4eeab40ded6695`;
- initial model SHA `929865a36d4a0369e8f1d6d9089809022256946bdbfa567445f6f3d5243b6cd2`;
- params `25,872,904`;
- batch 128 forward/backward finite;
- optimizer steps 0 at preflight.

Again, none of this is scientific outcome evidence.

## Evaluation split lockbox

Official BEDROOM split file SHA:

`f8f144f2380668b7db999d1b21b0331ade27b72f7e4892b43da068559ffb6d79`

Official counts:

- train 6037;
- val 249;
- test 248.

Materialized preprocessed intersection:

- train 3722;
- val 157;
- test 162;
- 2 unmapped materialized directories.

Current roles:

- train: training only;
- val: future reproduction qualification lockbox only;
- test: future scientific P1 lockbox only.

No validation or test metrics are allowed during current training. No checkpoint is selected from val/test.

## Planned P1 schema

Current frozen high-level schema says:

Models:

- `SGP-12 + SHARED`;
- `SGP-14 + SHARED`.

Interventions:

- predicted graph;
- oracle graph.

Relation counts:

- 2;
- 3;
- 4.

Topology labels currently named:

- `DISJOINT`;
- `CHAIN`;
- `HUB`;
- `COMPONENT_BRIDGE_OPTIONAL`.

Observables:

1. `text_to_graph_relation_recall`;
2. `graph_to_scene_relation_retention`;
3. `end_to_end_relation_iRecall`.

No P1 cases are materialized yet.

## Topology definition used by the current compiler

Topology statistics are computed on an **undirected graph** formed from relation endpoints. The current synthetic construction defines:

- DISJOINT: edges `(A,B), (C,D), ...`;
- CHAIN: `(A,B), (B,C), (C,D), ...`;
- HUB: `(A,B), (A,C), (A,D), ...`.

The statistics include:

- connected / active component count;
- max degree;
- degree concentration;
- largest-component diameter;
- shared-anchor edge-pair fraction;
- largest component size;
- graph density.

Important challenge to audit rather than assume: at relation count **2**, the undirected CHAIN `(A,B),(B,C)` and HUB `(A,B),(A,C)` are graph-isomorphic and have the same usual topology statistics up to node relabeling. Decide whether count=2 can legitimately support a CHAIN-vs-HUB topology contrast under the current topology definition. If direction/semantic relation labels are needed to distinguish them, determine whether that ceases to be a pure topology contrast.

## Planned topology matching

Current intended matching for a topology contrast:

- same object universe;
- same relation count;
- same relation-family multiset;
- same exact CLIP token count;
- no truncation;
- same topology policy conditional on relation count across support arms;
- outcome-blind sampling.

Token matching policy currently says exact token count where feasible; otherwise same one-token bin within relation-count and topology strata, with token count modeled continuously.

## Oracle graph intervention

Planned arms:

1. `text -> predicted graph -> shared layout decoder`;
2. `ground-truth instructed graph -> same shared layout decoder`.

Exact identity fields required between paired predicted/oracle decoder inputs:

- slot IDs;
- object IDs;
- object classes;
- object-feature IDs;
- object masks.

Forbidden pairing repairs:

- Hungarian matching;
- semantic remapping;
- heuristic aliasing;
- outcome-aware pairing.

Any identity mismatch makes the pair ineligible; inability to form exact pairs blocks the intervention.

The intent is to ask whether replacing only the graph relation structure with an exact-identity oracle graph selectively restores the downstream relation-retention / end-to-end behavior.

Audit whether this intervention genuinely localizes a bottleneck, what it can and cannot causally establish, and whether there is any hidden information advantage or distribution shift in the oracle condition.

## Current statistical analysis plan

Primary model:

`binomial mixed-effects response surface at relation level`

Current formula:

`realized ~ relation_count_c * exact_clip_token_count_c * training_support_regime * topology_class + relation_family + (1 + relation_count_c | base_scene_id) + (1 | instruction_template_id) + (1 | seed_id)`

Secondary endpoint:

`exact_all_success` with the same fixed-factor/random-effects strategy.

Continuous topology sensitivity candidates:

- maximum degree;
- degree concentration;
- active component count;
- largest active component diameter;
- shared-anchor edge-pair fraction;
- cycle rank;
- edge density.

Shape assumption:

- smooth degradation by default;
- segmented / change-point C* only secondary if supported.

Stage analysis:

- same response surface per observable;
- paired oracle-minus-predicted contrasts.

Capability masking rules:

- unsupported observable is NA, never zero;
- denominators include only predeclared observable-capable pairs;
- oracle/structured-access rows are upper bounds, not normal model ranks;
- no average rank across different input access or output representations.

## Developmental versus confirmatory scope

The current official training tranche is deliberately one seed and developmental.

Not yet authorized:

- confirmatory multi-seed replication;
- reproduction evaluation;
- P1 test evaluation;
- oracle-graph intervention.

A future multi-seed confirmatory tranche would be separately authorized only after a frozen developmental decision rule. Audit whether this sequencing creates unacceptable selection bias / HARKing risk, and what must be frozen **before** any developmental scientific outcome is opened so that later confirmation remains interpretable.

## Questions you must audit explicitly

1. **Paper thesis:** Is there a coherent single paper-level scientific claim here, or is this three loosely connected observations (support, topology, oracle localization)? State the strongest defensible one-sentence thesis.
2. **Novelty:** Given SceneNAT and GeoSceneGraph overlap, is the surviving contribution substantively novel enough for a standalone paper if the planned effects are real? What exact wording is defensible and what wording would be rejected as collision/overclaim?
3. **Treatment identification:** Does `SGP-12` versus `SGP-14` identify a causal effect of training **support**, or only the effect of a bundled training-distribution regime that includes different relation-count / relation-edge dose? Do not accept the label `only_intentionally_varied_factor` at face value.
4. **Dose confound:** Equal row count does not imply equal total number of relation edges, average relation count, sequence complexity, or optimization signal. Is this a fatal confound for the intended claim? If so, give the smallest control/reframing that fixes it.
5. **Support crossover logic:** Are counts 2/3/4 sufficient to identify the intended crossover (`in-support-both`, `out-12/in-14`) without using the already-collided 5/6 extrapolation story as novelty?
6. **Training corpus matching:** Are conditional relation-family, direction, token, topology, scene, object-count and template matching sufficient? Which matching constraints are scientifically essential versus governance overhead?
7. **Topology identifiability:** Under the team's undirected topology statistics, can CHAIN and HUB be distinguished at relation count 2? Audit all topology classes for each proposed relation count 2/3/4 and specify the minimal valid count×topology panel.
8. **Topology versus semantics:** Does matching relation-family multiset and exact token count actually isolate topology, or can object identity / relation semantic compatibility / geometric feasibility still confound the contrast? Give the smallest defensible panel-construction rule.
9. **Topology as categorical factor:** Is `topology_class` the right primary representation, or should the scientific claim be about continuous graph statistics with named classes only as illustrative anchors? Which choice is more robust and reviewer-proof?
10. **Mixed model:** Is the current four-way interaction mixed-effects model identifiable and sensible for the planned panel, especially with one developmental training seed? What is the smallest corrected primary analysis? Avoid a giant statistics wishlist.
11. **Seed logic:** What evidence can one developmental training seed support? What must be replicated before a paper-level causal claim? Distinguish developmental mechanism discovery from confirmatory evidence.
12. **Shared decoder:** Does one SG2SC decoder trained on ground-truth graphs create a clean downstream control, or does predicted-graph distribution shift complicate interpretation? What claim remains valid?
13. **Oracle intervention:** Does predicted-vs-oracle exact-identity pairing isolate graph quality, or does the oracle arm receive extra information / a different input distribution? What causal localization claim is valid versus invalid?
14. **Oracle eligibility:** If predicted graphs fail exact object/slot identity more often under one support regime/topology, conditioning on exact-pair eligibility could create selection bias. Is the current `ineligible -> drop` rule acceptable? If not, give the minimum correction.
15. **Stage observables:** Are text-to-graph recall, graph-to-scene retention, and end-to-end iRecall sufficient to distinguish where attenuation occurs without conflating denominators or survivorship?
16. **Panel selection:** Specify an outcome-blind deterministic rule for materializing test topology cases so the team cannot tune the panel after seeing development results.
17. **Development -> confirmation:** What exact pass/stop rule must be frozen before opening any scientific development output to prevent later confirmatory multi-seed selection from becoming post-hoc?
18. **Execution interruptions:** SGP-12/14 currently have durable 100k checkpoints but no active actors; BEDROOM is still training. Are resume events scientifically benign under the exact checkpoint/RNG/sampler contract, and what evidence should be reported versus omitted from the paper?
19. **Paper figures:** If the direction survives, what are the minimum 3–4 main-paper figures/tables that directly establish the claim? Remove anything that is merely process/governance evidence.
20. **Highest-information experiment:** What is the single smallest P1 experiment that would most decisively tell us KEEP/PIVOT/STOP before spending on multi-seed confirmation?

## Required response structure

### A. Decisive verdict

Choose `KEEP`, `PIVOT`, or `STOP`, with a short justification.

### B. Corrected one-sentence paper thesis

Give the strongest defensible one-sentence thesis, or say no standalone thesis survives.

### C. Audit 1–20

Answer every numbered question explicitly. Separate:

- fatal identification problems;
- major but fixable methodology issues;
- paper-writing / claim-scope issues.

### D. Smallest corrected scientific workflow

Give the exact minimal workflow from current completed/ongoing training to a valid developmental P1 and, only if warranted, confirmation. Do not recommend broad side experiments.

### E. Smallest corrected P1 panel

Specify:

- valid relation counts;
- valid topology contrasts by count;
- matching variables;
- predicted/oracle handling;
- denominators / missingness;
- primary endpoint and minimal analysis;
- exact stop/go rule.

### F. Paper-story rewrite at the conceptual level

State:

1. motivation;
2. gap in prior work;
3. method/experimental intervention;
4. main evidence chain;
5. what the paper explicitly does **not** claim.

### G. Highest-information next experiment

Give exactly one next scientific experiment, with the minimum sample structure needed to make it decisive.

### H. Final line

End with exactly one of:

`KEEP`

`PIVOT`

`STOP`

After that final verdict line, list only **verdict-changing fixes** and nothing else.
