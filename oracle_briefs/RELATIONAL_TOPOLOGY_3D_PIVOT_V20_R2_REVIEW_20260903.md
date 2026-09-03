# Independent adversarial re-review — RELATIONAL-TOPOLOGY-STAGE-3D Oracle pivot v20

## Role

Act as an independent senior top-tier 3D vision / generative-modeling / ML methodology reviewer. This is a **second review** after a first independent Oracle review returned `PIVOT`.

Your task is not to praise the revision. Determine whether the revised paper story and prospective experiment now remove the first review's verdict-changing blockers **before any scientific P1 output is opened**.

Do not recommend broad extra experiments. End with exactly one verdict:

- `PASS_ZERO_OUTCOME_P1_DESIGN`
- `REVISE_BEFORE_P1`
- `STOP_DESIGN`

Then list only verdict-changing fixes.

## Provenance and outcome boundary

Scientific object:

`RELATIONAL-TOPOLOGY-STAGE-3D-20260831`

Repository base before R1:

`11f0b76b85596dfd48823f1c8b6bc7dfde951e36`

R1 review brief commit:

`216cdbb849f5cf399d232335275e8cc0b3a94a18`

R1-corrected v20 commit:

`4ebb8aa1e1d862b81f7ec89a35105d7961a63546`

R1 was run in a genuinely independent ChatGPT browser conversation with:

- Oracle 0.18.0;
- browser engine;
- GPT-5.6 Sol DOM-selected;
- Extra High 4/5 DOM-verified;
- `promptSubmitted=true`;
- independent conversation ID `6a995dbf-9f40-83ee-b5eb-dbce39b51d74`;
- R1 verdict `PIVOT`.

No scientific P1 outcome has been opened. No training loss is scientific evidence. This re-review is prospective.

## R1 verdict-changing objections

R1 required four changes:

1. Stop calling SGP-12 versus SGP-14 a pure causal effect of training support. Treat them as matched **training exposure regimes** unless relation-edge/supervision dose is equalized.
2. Remove count-2 CHAIN-vs-HUB and `COMPONENT_BRIDGE_OPTIONAL` from the primary topology panel. Use matched CHAIN/HUB at counts 3–4.
3. Freeze an outcome-blind validation developmental panel plus exact GO/STOP rule before opening metrics; preserve official test as untouched multi-seed confirmation.
4. Pair downstream RNG/noise in predicted/oracle conditions; retain all materialized cases in primary end-to-end denominators; report exact-identity eligibility as an outcome; block localization rather than silently dropping topology-dependent identity failures.

The v20 artifacts attached to this review are intended to implement all four.

## Outcome-blind training-input audit added in v20

Both existing corpora have 12,240 rows, but:

### SGP-12

- relation counts: 6120 count-1 + 6120 count-2;
- total relation edges: 18,360;
- mean relation count: 1.5;
- mean exact CLIP token count: 25.996.

### SGP-14

- relation counts: 3060 each at counts 1/2/3/4;
- total relation edges: 30,600;
- mean relation count: 2.5;
- mean exact CLIP token count: 41.336.

Thus SGP-14 has 66.7% more relation-edge supervision opportunities at equal row count.

v20 therefore explicitly rejects:

`CAUSAL_EFFECT_OF_TRAINING_RELATION_COUNT_SUPPORT_ALONE`

and uses:

`MATCHED_TRAINING_EXPOSURE_REGIMES`

Existing training is retained because the decisive topology-first screen does not require a pure-support estimand.

## Revised paper thesis

Working title:

> Beyond Relation Count: Endpoint-Sharing Topology in Text-Guided 3D Scene Generation

Primary question:

> At fixed relation count and tightly controlled semantic and textual content, does relation-endpoint connectivity create a residual difficulty inside the model's training range, and can an exact-identity same-decoder graph intervention localize how much of that residual is introduced at or before the semantic-graph interface?

One-sentence thesis:

> In an InstructScene-style cascaded 3D generator, instructions with the same relation count, active object set, predicate composition, text budget, and decoder can nevertheless exhibit different relation realization depending on how relation endpoints are connected, and exact-identity replacement of the predicted semantic graph can test whether this topology-dependent attenuation is introduced primarily at the text-to-graph interface rather than by the shared graph-to-scene decoder.

Primary scientific model:

`SGP-14 + frozen shared SG2SC`

Primary counts:

`3, 4`

Primary topology contrast:

`CHAIN vs HUB`

SGP-12 is secondary exposure-regime context only and is not required for the first GO decision.

## Revised topology definition

Topology is the undirected endpoint-connectivity graph.

Count 3:

- CHAIN: P4, 4 active nodes;
- HUB: K1,3, 4 active nodes.

Count 4:

- CHAIN: P5, 5 active nodes;
- HUB: K1,4, 5 active nodes.

Primary exclusions:

- count 2 CHAIN/HUB: excluded because P3 = K1,2;
- DISJOINT: secondary only because active endpoint count differs;
- COMPONENT_BRIDGE_OPTIONAL: excluded because no frozen non-isomorphic definition exists.

## Revised developmental split and sample

Official validation becomes the **one-seed developmental P1 screen** after separate authority.

Official test remains the **untouched confirmatory multi-seed lockbox**.

Validation screen:

- count 3: 40 matched base-scene tuples, each produces CHAIN + HUB = 80 instructions;
- count 4: 40 matched tuples = 80 instructions;
- total: 80 paired tuples / 160 instructions.

If fewer than 40 valid outcome-blind pairs can be produced at either count, panel qualification fails. Matching may not be relaxed after model outputs are seen.

## Revised matched-pair contract

Exact within CHAIN/HUB pair:

- base scene;
- active object IDs;
- object classes;
- object-feature IDs;
- object masks;
- relation count;
- predicate multiset;
- direction multiset;
- instruction template;
- exact CLIP token count;
- tokenizer revision;
- no truncation;
- decoder checkpoint;
- decoder inference parameters;
- decoder random/noise seed.

Deterministically counterbalanced:

- object-to-topological-role assignment;
- predicate-to-edge assignment;
- hub-anchor identity across tuples.

Model-independent qualification only:

- semantic compatibility;
- geometric feasibility.

The whole pair is rejected if either topology fails qualification.

Forbidden panel filters include SGP output, SG2SC output, recall, success, oracle rescue, exact-identity eligibility, or any model-derived difficulty score.

## Revised deterministic panel compiler

Protocol version:

`RT3D-P1-TOPOLOGY-FIRST-V20`

For each split and count 3/4:

1. enumerate candidate scenes with at least c+1 eligible objects;
2. canonicalize objects by stable object ID;
3. score each object by SHA256 of a frozen salt + split SHA + scene ID + count + object ID; choose the c+1 lowest scores;
4. choose a permitted predicate/direction multiset from a frozen candidate library using only frozen hashes/metadata;
5. create CHAIN and HUB from frozen edge templates;
6. deterministically rotate object roles and predicate-to-edge assignment for counterbalancing;
7. use the same frozen instruction-template family;
8. require exact CLIP-token equality within pair and no truncation;
9. apply only frozen model-independent semantic/geometric feasibility checks;
10. reject the whole pair if either member fails;
11. hash-sort surviving tuples with a second frozen salt;
12. choose first 40 per count.

Before outcomes, freeze compiler commit/source SHA, salts, edge templates, candidate predicate/direction library, instruction templates, feasibility checker/thresholds, N=40, and final panel manifest SHA.

## Revised predicted-versus-oracle intervention

Predicted arm:

`instruction -> frozen SGP-14 -> predicted graph -> frozen shared SG2SC`

Oracle arm:

`same instruction/object scaffold -> ground-truth instructed relation graph -> same frozen shared SG2SC`

Exact identity fields:

- slot IDs;
- object IDs;
- object classes;
- object-feature IDs;
- object masks.

Paired downstream state additionally includes:

- SG2SC checkpoint;
- inference parameters;
- decoder sampling seed;
- decoder noise/randomness.

Every materialized instruction remains in primary text-to-graph and end-to-end denominators.

`exact_identity_eligible` is recorded on every instruction.

Oracle rescue is explicitly conditional on exact identity eligibility.

No Hungarian matching, semantic remapping, aliasing, or outcome-aware repair.

If eligibility is inadequate or topology-dependent, the localization claim is blocked rather than repaired by subset selection.

## Revised denominators

Text-to-graph recall:

- denominator = all instructed GT relations over all materialized instructions;
- identity/predicate failure counts as failure.

Predicted graph-to-scene retention:

- denominator = instructed relations correctly represented in predicted decoder input with required identities;
- explicitly conditional.

Oracle graph-to-scene retention:

- denominator = all instructed oracle relations.

End-to-end iRecall:

- denominator = all instructed GT relations over all materialized instructions;
- this is the primary endpoint.

Exact-all-success:

- all materialized instructions;
- secondary.

The three stage metrics are explicitly **not** presented as a multiplicative waterfall. Causal localization comes from the intervention.

## Revised primary estimand and statistics

Primary estimand in SGP-14 predicted arm:

`Delta_topo = mean_i(iRecall_HUB_i - iRecall_CHAIN_i)`

pooled over count 3–4 paired base-scene tuples.

Mandatory estimates:

- count 3 separately;
- count 4 separately;
- pooled 3–4.

Primary uncertainty:

- paired base-scene cluster bootstrap;
- 10,000 replicates;
- fixed bootstrap seed 20260903;
- two-sided 95% percentile CI.

The old four-way count × token × support × topology mixed model is no longer the developmental primary model. No seed random effect is used in a one-seed screen. Continuous topology statistics are descriptive/secondary.

## Frozen developmental GO/STOP rule

Multi-seed confirmation is eligible only if **all five** pass:

1. **Meaningful topology residual**: `abs(pooled predicted Delta_topo) >= 0.10` and 95% paired base-scene bootstrap CI excludes zero.
2. **Cross-count consistency**: count-3 and count-4 effects have the same sign and each absolute effect is at least 0.05.
3. **Upstream correspondence**: pooled text-to-graph topology effect has the same sign as pooled predicted end-to-end Delta_topo.
4. **Selective oracle recovery**: `1 - abs(Delta_oracle)/abs(Delta_predicted) >= 0.50` and `abs(pooled Delta_oracle) <= 0.05`.
5. **Oracle identification**: exact-identity eligibility >=95% in every count × topology cell and CHAIN/HUB eligibility-rate difference <=5 percentage points within each count.

If any gate fails:

`STOP_STANDALONE_TOPOLOGY_LOCALIZATION_CONFIRMATION; DO_NOT_RESCUE_POST_HOC`

Forbidden post-outcome rescues include count 5/6, another topology class, relaxed token matching, changed N, changed primary endpoint/thresholds/denominators, or making SGP-12 OOD behavior the primary thesis.

## Confirmation if developmental GO passes

- test split only;
- same frozen panel compiler and thresholds;
- at least three total independently trained SGP-14 seeds;
- two new independent SGP-14 seeds after the developmental seed;
- one frozen shared decoder, with claims explicitly conditional on it;
- SGP-12 multi-seed confirmation only if a secondary exposure-regime interaction is separately predeclared.

## Execution status — not scientific evidence

Current official developmental training is not changed by v20.

- SGP-14 has a durable 100k checkpoint and is queued for exact resume on 69 when the A100 becomes completely idle; no preemption/co-location.
- SGP-12 has a durable 100k checkpoint but is secondary under the revised thesis and is not currently prioritized over other GPU jobs.
- shared BEDROOM SG2SC is still training on 52 and has passed at least its 50k checkpoint.

No P1 metrics are open.

## Questions for R2

Audit the revision explicitly:

1. Does the topology-first thesis now form one coherent standalone contribution, given SceneNAT/GeoSceneGraph collision boundaries?
2. Has the pure-support causal identification problem been genuinely removed rather than merely renamed?
3. Is SGP-14 count 3/4 within-exposure CHAIN-vs-HUB the correct decisive developmental object?
4. Are count 3/4 CHAIN-vs-HUB valid topology contrasts under the frozen undirected definition?
5. Does the matched tuple contract sufficiently isolate endpoint-sharing structure, or does an unaddressed object/semantic/geometric confound remain fatal?
6. Is the deterministic panel compiler sufficiently outcome-blind and reproducible? Identify any underspecified step that could permit researcher discretion after outcomes.
7. Is N=40 matched tuples per count scientifically adequate as a **developmental screen** for the frozen effect-size/CI gate, or does the design become too low-power/unstable to support a GO/STOP decision?
8. Is the paired base-scene bootstrap estimand/statistical plan the smallest valid analysis? Audit the pooled count 3–4 definition and mandatory count-specific checks.
9. Are the five GO/STOP gates coherent and prospective, or do any create an invalid/arbitrary criterion that must be changed before P1?
10. Does the corrected oracle protocol solve post-treatment eligibility bias as far as possible? Is the >=95% / <=5pp eligibility gate defensible?
11. Is pairing decoder seed/noise sufficient for the same-decoder oracle comparison, and is the remaining localization claim correctly scoped?
12. Are the stage denominators correct and non-circular?
13. Is validation-development -> untouched-test confirmation scientifically clean? What exactly may be adapted after validation without contaminating test confirmation?
14. Are three total independent SGP-14 seeds enough for the minimal paper-level reproducibility claim, conditional on one shared decoder?
15. Does the existing SGP-14 training need to be restarted because its training exposure is not topology-balanced in some stronger sense, or is the fixed-count matched evaluation sufficient for the revised topology-first estimand?
16. Does SGP-12 now have an appropriately secondary role, or should it be removed entirely from the paper's main experimental narrative?
17. Are the proposed four main figures/tables minimal and sufficient if the gates pass?
18. Is there any remaining verdict-changing flaw that must be fixed **before** requesting developmental P1 authority?

## Required response

1. Give the decisive verdict first.
2. Answer questions 1–18 explicitly.
3. Give the smallest corrected protocol only if revision is still required.
4. Do not request broad extra experiments.
5. End with exactly one verdict line:

`PASS_ZERO_OUTCOME_P1_DESIGN`

or

`REVISE_BEFORE_P1`

or

`STOP_DESIGN`

After that line, list only verdict-changing fixes and nothing else.
