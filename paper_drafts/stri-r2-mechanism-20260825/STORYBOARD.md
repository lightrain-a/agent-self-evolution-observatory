# STRI-R2 mechanism storyboard

## Working title

**Representation-Invariant Skill Evolution: Selection Geometry and Credit Fragmentation**

## Scientific question

A self-evolving agent stores reusable skills as named persistent objects. If one semantic skill is replaced by several exact-content identities, the agent has not gained capability. Should its future learning trajectory change anyway?

STRI-R2 asks a stricter question than R19: **does exact semantic refinement commute with the full skill-control loop, not merely with one retrieval or weighting step?**

## One-sentence answer

No in two separable ways: identity can be counted once when allocating selection mass and again when accumulating post-selection evidence; exact refinement therefore creates **selection duplication** and **credit fragmentation**, and full representation invariance requires quotienting both surfaces.

## Closed loop

### 1. Phenomenon

Released self-evolving skill systems treat identity as more than metadata. In Skill-SP, an identity is both (i) a selectable package and (ii) a persistent statistics/lifecycle unit. Exact semantic splitting can therefore alter immediate semantic mass and future active-library state without adding information or capability.

### 2. Mechanism isolation

Remove selection entirely. Feed the same eight byte-identical semantic feedback records to the released Skill-SP update/pruning code.

- one canonical identity: attempts=8 -> retired;
- exact split into two identities: attempts=(4,4) -> neither retires;
- semantic quotient-credit: aggregate to 8 before the same gate -> canonical retirement restored.

The residual survives after the selection channel is mechanically absent. This identifies a post-selection mechanism rather than strategic replication or retrieval opportunity.

### 3. Mechanism law

Let exact identities i map to semantic class c through quotient map pi. Identity-local evidence states are s_i and semantic aggregation is S_c = ⊕_i s_i. A lifecycle gate g is representation invariant only if applying the gate after semantic aggregation agrees with the class-level decision induced by applying it to refined identities.

For Skill-SP's retirement-eligible evidence with count threshold M:

- canonical / quotient-credit retirement: N >= M;
- balanced k-way exact split full retirement: N >= kM;
- fragmentation window: M <= N < kM;
- retirement lag: (k-1)M.

The released default is M=8. The deterministic grid k=1..6, N=0..48, p_hat in {0.1,0.5,0.9} contains 882 cells and has zero analytic mismatches.

### 4. Two-channel causal decomposition

2x2 intervention: selection handling {native, quotient} x credit handling {native, quotient}.

| Selection | Credit | Semantic selection | Lifecycle after 8 feedback | Full invariance |
|---|---|---:|---|---|
| native | native | 2/3 | active | no |
| native | quotient | 2/3 | retired | no |
| quotient | native | 1/2 | active | no |
| quotient | quotient | 1/2 | retired | yes |

Canonical reference: semantic selection=1/2 and retired after eight easy records.

This is the closure experiment: repairing either identity surface alone leaves the other defect; quotienting both restores both canonical semantic endpoints.

### 5. General selection geometry

Exact cloning is only the simplest selection-channel failure. Partial overlap cannot always be quotiented away. R19's support matrix A and target-realizability certificate R*(A;q) remain as the more general selection-side analysis:

- R*=1: target semantic allocation is package-realizable;
- R*>1: no same-information package router can realize it.

Skill-SP Level-1: R*=2, including heldout and LOO controls. Level-3 and the high-overlap logical compiler domain: R*=1. Hence overlap count is not the mechanism; support geometry is.

### 6. Cross-system structure

SkillsVote independently implements the same **partition-before-update** architecture. Evolvable feedback is grouped by `skill_linked`; each identity bucket becomes a separate edit request and updater invocation targeting the persistent working skill.

Zero-model counterfactual with eight semantically identical evidence records:

- canonical link -> 1 request with 8 records;
- exact identity split 4/4 -> 2 requests with 4+4 records;
- semantic quotient of links -> 1 request with 8 records.

This is structural corroboration only. SkillsVote has a model-based editor rather than Skill-SP's deterministic M-threshold gate, so we do not claim a second exact phase law.

RethinkSkill is a useful closest-work control: it studies multi-round validation-filtered skill revision, but its primary loop evolves one current skill against candidates rather than parallel exact-semantic identity buckets. It therefore does not instantiate the same partition counterfactual.

### 7. Downstream manifestation and boundary

AutoSkill P19 is retained only as a bounded downstream existence proof: exact identity splitting changes retrieval and one mechanical executed behavior, restored by ID-placebo/quotient and mediator add-back controls.

The preregistered R19 heldout pilot is equally important: 9/9 units are retrieval-sensitive, yet neither of two outcome-blind selected units passes the frozen split-specific behavior gate over 8/8 valid runs. Expansion stops. Therefore retrieval sensitivity is not sufficient for task-general behavior change.

### 8. Natural-prevalence boundary

The released Skill-SP loop truly updates identity-local attempts/avg_p_hat and then prunes, with default M=8 over five self-play iterations and a default 8000-record solver collection target. However runtime `skills.json` and retired ledgers are gitignored/not released, and three pinned local release mirrors contain no evolved runtime state.

Conclusion: mechanism code path and trigger opportunity are supported; endogenous prevalence is unresolved. Do not convert this into a frequency claim.

## Contribution hierarchy

1. **Scientific object:** representation invariance for a persistent skill-evolution loop, not merely a static skill router.
2. **Mechanism:** post-selection credit fragmentation under identity-local state followed by nonlinear lifecycle gating.
3. **Law:** exact multiplicity/evidence phase law M <= N < kM and lag (k-1)M on a released controller.
4. **Causal decomposition:** orthogonal selection and credit channels; two quotient interventions are separately necessary and jointly sufficient for the two frozen semantic endpoints.
5. **Cross-system corroboration and boundaries:** SkillsVote request topology, RethinkSkill negative structural control, AutoSkill bounded behavior manifestation, heldout behavior STOP, and unresolved natural prevalence.

## What moves out of the main story

- most heuristic package-weight baselines;
- 1387/366/200 perturbation inventory details;
- SkillRouter and AgentSkillOS analogues;
- solver timing;
- second-support-substrate tournament details;
- semantic-first as the apparent final solution.

These remain useful robustness/supplement evidence, but they should not interrupt the mechanism spine.

## Claim ceiling

STRI-R2 may claim:

- exact semantic identity refinement can alter released skill-control state through two distinct identity-indexed channels;
- Skill-SP's released post-selection update/pruning operator exhibits deterministic credit fragmentation with an exact phase law;
- quotient selection and quotient credit restore the corresponding frozen canonical semantic endpoints in the 2x2 decomposition;
- SkillsVote independently partitions update evidence by skill identity before persistent updating.

STRI-R2 may not claim:

- endogenous fragmentation prevalence in Skill-SP;
- task-utility gain from quotient interventions;
- a second exact phase law in SkillsVote;
- task-general behavioral propagation;
- universal self-evolution invariance across all agent architectures.

## Promotion rule

Keep R19 canonical. Promote R2 only after the new mechanism manuscript passes paper QA, integrity audit, closest-work review, and independent reviewer adjudication. A provider failure cannot count as reviewer agreement.
