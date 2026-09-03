# Paper outline — topology-first revision

## Working title

**Beyond Relation Count: Endpoint-Sharing Topology in Text-Guided 3D Scene Generation**

This outline is prospective. It contains no scientific result claim.

## Abstract logic

1. **Problem:** Multi-relation scene instructions are usually summarized by relation count, although constraints with the same count can have different endpoint-connectivity structure.
2. **Gap:** Recent systems already study relation-count scaling and graph-based generation, but do not isolate a same-count, same-object endpoint-sharing intervention together with an exact-identity same-decoder graph substitution.
3. **Protocol:** Compare matched CHAIN and HUB instructions at counts 3–4 in an InstructScene-style cascade while fixing scene, active objects, predicate/direction multiset, text budget and decoder. Then replace only the predicted relational graph with the ground-truth instructed graph under identical decoder randomness.
4. **Evidence required:** a within-SGP-14 CHAIN/HUB residual; the same direction upstream at text-to-graph; substantial reduction of the topology gap under exact-identity oracle substitution; replication across independent SGP-14 seeds on untouched test.
5. **Scope:** The study does not claim that relation-count degradation, graph-based generation, training-support causality, or a universal topology law is novel.

## 1. Introduction

### Paragraph 1 — Why relation count is insufficient

Text-guided 3D scene generators must satisfy several relational constraints simultaneously. Existing evaluation commonly treats the number of relations as the complexity axis. But three or four relations can be arranged as a chain of dependencies or concentrated around one shared anchor. Those instructions have the same edge count while inducing different endpoint-connectivity structure.

### Paragraph 2 — What prior work already covers

InstructScene establishes a semantic-graph-prior pipeline. SceneNAT already studies stronger relation-count regimes and beyond-training relation counts. GeoSceneGraph and other graph-based generators already establish that graph structure is useful in scene synthesis. Therefore the paper must not sell relation-count decline, graph priors, or graph-stage diagnostics as the contribution.

### Paragraph 3 — Missing controlled question

The unresolved question is whether endpoint sharing creates a residual difficulty when relation count, active objects, relation composition, text length and downstream decoder are held fixed. A second unresolved question is whether such a residual is already represented at the semantic-graph interface or arises only during graph-to-layout decoding.

### Paragraph 4 — What we do

We construct paired CHAIN/HUB counterfactual instructions at counts 3 and 4 over the same base scene and active object set. We evaluate them with an SGP whose count-3/4 inputs lie inside its training exposure regime and use one frozen shared graph-to-scene decoder. We then perform an exact-identity oracle graph substitution with paired decoder randomness.

### Paragraph 5 — Contribution statement, conditional on future results

The paper may claim only what the frozen evidence chain establishes: a controlled endpoint-sharing residual and, if the oracle gate passes, localization of a substantial part of that residual to at-or-before the semantic-graph interface under the fixed decoder.

## 2. Related work

### 2.1 Instruction-driven indoor 3D scene synthesis

Position InstructScene as the substrate, not as our contribution.

### 2.2 Relational-complexity evaluation

Discuss SceneNAT and related relation-count work. Explicitly state that count scaling and 5/6-relation extrapolation are prior territory.

### 2.3 Graph-structured scene generation and diagnostics

Discuss GeoSceneGraph and other graph/geometric guidance methods. Separate using graphs as a generator architecture from using a matched topology intervention as a diagnostic.

### 2.4 What remains

End Related Work with the narrow gap: fixed-count endpoint-connectivity counterfactuals plus exact-identity same-decoder graph substitution.

## 3. Method / controlled diagnostic

### 3.1 Cascaded generation interface

Define:

`instruction -> semantic graph predictor -> frozen shared graph-to-scene decoder -> layout`

The scientific object is not a new architecture; it is the behavior of this interface under controlled relation topology.

### 3.2 Endpoint-sharing topology intervention

Primary counts are 3 and 4 only.

- count 3 CHAIN: `P4`;
- count 3 HUB: `K1,3`;
- count 4 CHAIN: `P5`;
- count 4 HUB: `K1,4`.

Do not use count-2 CHAIN/HUB as topology evidence because the two graphs are isomorphic.

Within each pair hold fixed base scene, active object identities/classes/features/masks, count, predicate/direction multiset, instruction template, exact CLIP token count, tokenizer revision and no-truncation status.

### 3.3 Outcome-blind panel compiler

Describe the hash-based object selection, frozen predicate/direction library, frozen topology templates, role counterbalancing, exact token match, model-independent feasibility checker, pairwise rejection rule and final hash-sorted panel selection. The executable compiler and its final manifest are the sole authority; no manual tuple substitution is permitted.

### 3.4 Exact-identity graph intervention

For the same frozen instructions compare:

- predicted semantic graph -> shared decoder;
- oracle instructed graph -> the identical shared decoder.

Keep object/slot identity fields and downstream decoder randomness identical. Oracle receives correct relational information intentionally and is an intervention/upper bound, not a fair deployment baseline.

### 3.5 Stage observables

Report text-to-graph relation recall, conditional graph-to-scene retention and unconditional end-to-end iRecall. Do not multiply them into a mathematical waterfall. Localization comes from predicted-versus-oracle substitution.

## 4. Experimental protocol

### 4.1 Training objects

Primary: SGP-14 plus the frozen shared decoder.

Secondary context only: SGP-12 as a row-count-matched but exposure-different training regime. Do not attribute differences to support alone; the input audit shows different relation-edge and token doses.

### 4.2 Developmental validation screen

Use 40 matched CHAIN/HUB tuples at count 3 and 40 at count 4: 80 paired tuples / 160 instructions. Keep official test unopened.

### 4.3 Primary estimand

`Delta_topo = mean(iRecall_HUB - iRecall_CHAIN)`

Report count 3, count 4 and equally count-weighted pooled estimates. Use a physical-base-scene cluster bootstrap with 10,000 replicates; if a scene appears in both counts, resample all its observations together.

### 4.4 Frozen GO/STOP rule

Proceed to confirmation only if all five frozen gates pass: meaningful pooled topology effect, same-sign count-specific effects, upstream correspondence, at least 50% oracle gap reduction with small residual, and sufficiently complete/balanced exact-identity eligibility.

Any failure stops the standalone topology/localization confirmation. Do not rescue with count 5/6, new topology classes or changed thresholds.

### 4.5 Untouched-test confirmation

If validation GO passes, train two additional independent SGP-14 seeds for three total seeds and evaluate the unchanged compiler/analysis on untouched test. Keep claims explicitly conditional on the one frozen shared decoder.

## 5. Results structure — placeholders only

### 5.1 Does endpoint-sharing topology matter within SGP-14's training range?

Future Figure 2. No statement is allowed until the frozen screen is opened under separate authority.

### 5.2 Where is the topology residual visible?

Future stage-observable analysis. No causal claim from percentages alone.

### 5.3 Does exact graph substitution reduce the topology gap?

Future Figure 3. Report exact-identity eligibility alongside conditional oracle rescue.

### 5.4 Does the effect replicate across training seeds?

Future confirmatory table/figure on untouched test only if validation GO passes.

## 6. Discussion

Discuss endpoint sharing as a structural axis that relation count may hide, but avoid claiming a universal graph law. Discuss predicted-graph distribution shift into the decoder and the fact that the localization is conditional on the frozen decoder.

## 7. Limitations

- one scene-generation substrate;
- one frozen shared decoder in the minimal paper;
- topology intervention necessarily changes which object pairs are connected;
- feasibility filtering defines the supported counterfactual population;
- oracle localization is conditional on exact identity eligibility;
- three SGP seeds establish minimal reproducibility, not a full optimization-randomness distribution.

## Main evidence objects

1. **Figure 1:** matched CHAIN/HUB intervention and oracle substitution point;
2. **Figure 2:** count-3/count-4/pooled SGP-14 predicted topology effects plus text-to-graph direction;
3. **Figure 3:** predicted-versus-oracle gap and exact-identity eligibility;
4. **Table/Figure 4:** untouched-test multi-seed confirmation, only after developmental GO.

Exclude training-loss curves, checkpoint timelines, queue state and GPU allocation history from the main scientific evidence chain.
