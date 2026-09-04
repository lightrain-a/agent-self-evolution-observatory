# Independent GPT-5.6 Sol review — latest E2-R17 plan + frontend

Date: 2026-09-04
Surface: ChatGPT web via Oracle Browser
Model: GPT-5.6 Sol
Thinking: Extra High (4/5)
Conversation: `https://chatgpt.com/g/g-p-6a6ad664d6508191bff6ecf4fde868f0-agent/c/6a9a38aa-7a10-83e8-b0c5-7d11683385db`
Frozen review brief commit: `13916d55c1523f01fdc6815ebe6abc3f1986a66d`
Brief SHA256: `2e9f7597019faf5b717e16fd954bedc34ca5b023e2f6a3ad43e63bb93662c96b`
Inline packet SHA256: `661932dd12ddca0ccd69391893de3dcbf4008aa388b6e1114aecc214fe9f030e`
Raw response SHA256: `48c85ef472b65db09863df6051cb2a84ec4c185916e6e0f2f89dc5a99979c6e5`
Oracle transcript SHA256: `dda2b18f10138a418d43e02f21893262eef57b162d388f10ee274999054c2298`
Verdict: `REVISE_ZERO_PROVIDER_PLAN_OR_FRONTEND`

## Independent adversarial review

### A. Scientific ladder

**A → B → C → D is the right minimal ladder**, with one qualification inside C.

* **A1** establishes evidence availability/censoring support only.
* **A2** establishes that the simple global universal-MRW hypothesis was not supported strongly enough; it motivates but does not prove heterogeneity.
* **B** is correctly the mandatory controlled causal identification layer.
* **C** is necessary for a standalone paper because the controlled suite alone does not provide natural-task external validity or reviewer-facing method comparison.
* **D** is correctly downstream and non-rescuing.

There is no missing controlled experiment between B and C, and requiring B3 before entering C would be unnecessarily restrictive: B2 interaction PASS is enough to justify transport testing even if the stronger B3 conjunction fails.

The qualification is that **C currently contains two scientifically distinct estimands—method competitiveness and causal transport—and only the former is presently fully specified**. That is a C-level repair, not a reason to reopen R2.

### B. Controlled workload sufficiency

**Sufficient.**

The completed A evidence plus the prospective Stage-A/Stage-B package is already substantial relative to the actual independent units:

* 5 preregistered matched skeletons;
* 20 streams;
* Stage A support qualification before any updater call;
* exact-same-pool paired interventions;
* five independent interaction units;
* 3200 heldout measurements.

Another synthetic model, another set of skeletons, or additional Stage-B replicates would mostly increase accounting volume rather than address a missing identified claim.

If B2 fails, the correct action is the frozen STOP for the strong mechanism story—not more controlled-search volume. If it passes, the missing information type is **external validity**, so moving to C is scientifically correct.

### C. Five independent skeletons

**Defensible for the stated bounded claim.**

Five skeletons would be weak evidence for a population-level statement such as “procedural tasks generally exhibit this moderator.” That is explicitly not the proposed claim.

For a prospective finite-suite claim in which:

* the five skeletons are independently constructed/crossed;
* the gate is frozen before outcomes;
* all five interaction directions and their magnitudes are reported;
* streams and R=4 replicates are not misrepresented as additional independent skeletons;
* no population-generalization language is used,

five independent matched interactions are methodologically defensible.

I would not request a sixth, tenth, or twentieth skeleton merely to obtain a conventional-looking sample size.

### D. Secondary 5/5 procedural gate

The B3 gate is **valid and appropriately separated from B2**.

`D_h,PROCEDURAL > 0` for all five skeletons is a conjunction defining a deliberately narrow finite-suite claim. The packet correctly avoids retroactively presenting 5/5 as an exact `p=1/32` hypothesis test.

It is conservative, but appropriately so: B2 can establish effect modification even if one procedural simple effect is nonpositive, whereas B3 demands evidence that the alternative projection is positively useful throughout the preregistered procedural suite.

There is, however, a **claim-language boundary**:

> 5/5 positive procedural effects establish that this alternative learner projection outperforms WIN-C learning across those five controlled procedural skeletons while serving is fixed.

They do **not** establish that the alternative is the globally **“best to learn”** projection. Nor does the experiment exhaust all possible serving rules. Therefore the frontend's stronger phrase **“best to act ≠ best to learn”** exceeds what B2+B3 identify.

### E. Public P1 design

Combining transport and closest-method comparison on SpreadsheetBench Verified-400 is efficient and scientifically sensible. There is no reason to create two benchmark campaigns merely to separate tables.

The proposed **80/40/280** split is also well motivated rather than arbitrary: SkillOpt's released SpreadsheetBench manifests already use exactly 80 training/evolution, 40 validation, and 280 test examples from Verified-400. Therefore there is **no inherent leakage problem** in the numerical split. The later C0 freeze should preferably pin an audited released manifest or an equally explicit deterministic pre-outcome rule, together with task/workbook version hashes, ordering, and any duplication/group-separation audit that the source structure requires.

The important defect is not the split. It is C4, discussed under H.

### F. Baseline sufficiency

**The method set is sufficient; I would not mandate another baseline.**

The combination has good explanatory coverage:

* No Skill / Parent: capability and persistent-state anchors.
* WIN-C: tied serving-learning projection.
* fixed alternative projection: mechanism-related anchor.
* RethinkSkill Normal / Success-only / Fail-only: directly probes feedback composition.
* SkillOpt: a strong current text-space skill optimizer.
* at least one credible trajectory-to-skill/contrastive reduction.

Adding GEPA, TextGrad, and EvoSkill merely to increase row count is not verdict-changing once a credible Trace2Skill-style comparator and SkillOpt are directly instantiated under the common harness. Source/adaptor fidelity matters more than one extra method name.

### G. Baseline fairness and replication

The current statement “one frozen evolution/selection run per method by default” is **not universally sufficient**.

Three heldout reruns of a single artifact only quantify **evaluation/execution noise**. They say nothing about variance induced by a stochastic updater, reflection call, candidate generation, validation selection, or evolving trajectory history.

Minimal rule:

* if a method's entire evolution procedure is deterministic once all seeds/decoding/randomness are pinned, one evolution realization is acceptable;
* if evolution itself remains stochastic, use a small common preregistered set of **full evolution seeds**—three paired seeds is a reasonable minimum—and treat those as evolution replicates;
* heldout-panel repetitions remain a separate measurement-noise layer.

### H. Transport endpoint

**This is the principal design blocker.**

As currently written, `Δ_transport = U_future(E2 alternative projection) - U_future(WIN-C)` on prospectively eligible units does **not by itself identify transport of the controlled projection-interface effect**.

In C1, different methods undergo their own evolution trajectories. Even with the same task IDs, actor family, harness, evaluator, and budgets, the realized evidence/search object can become method- and history-dependent. The E2 eligibility rule can additionally select particular natural units.

Consequently, a positive C4 difference could arise from eligibility/router selection, different realized search trajectories, different served actions, path-dependent persistent states, or the learner projection itself. That is a valid **policy-performance** quantity, but it is not external validity of the exact-same-pool, acting-fixed causal interface identified in B2.

Repair: for C4, prospectively select eligibility using pre-treatment observables, then on each eligible natural unit freeze a **common realized evidence/search object, common starting persistent state, and common served action**, and construct the WIN-C and alternative learner projections from that same frozen object. Only `g(T_K)` may differ before future utility is compared.

The unified C main table can remain a normal end-to-end method comparison. The C4 transport contrast must be a separately identified estimand inside the same public lane.

### I. Optional experiments

The D classification is correct. Second model is robustness only, failure-specific controls are required only for failure-specific claims, source-faithful reproductions are adapter-fidelity evidence, and SpreadsheetBench 2 is optional for a new workflow-level question.

### J. Frontend fidelity

**REVISE.**

Most frontend wording correctly distinguishes evidence, plans, and authority. Three semantics need repair:

1. Replace “best to act ≠ best to learn” with the identified alternative-vs-WIN-C learner-projection statement.
2. Rename the aggregate `0/5` from “scientific execution authority” to an execution/gate status label, because `fresh_identity_called` and `baseline_execution` are events/status flags, not authority objects.
3. Preserve the qualification “Universal MRW4 **or prospectively frozen public-compatible alternative**” rather than implying unconditional public MRW4 compatibility.

### K. Paper identity and strongest remaining objection

The causal-systems/interface identity is coherent. The strongest remaining pre-outcome objection is that the natural benchmark experiment does not yet preserve the intervention that makes B2 causal; without repair, P1 would validate a routed policy rather than transport the central interface effect. This is a C-level zero-provider repair, not an R2 defect.

### L. Immediate action

`ONE_ZERO_PROVIDER_FIX_BEFORE_IDENTITY`

### Verdict-changing required recommendations

1. **Repair C4 identification:** paired natural-unit causal transport with common starting state, exact realized object and serving; only `g(T_K)` differs. Keep end-to-end method ranking separate.
2. **Repair public replication:** deterministic evolution may use one realization; stochastic evolution requires a small preregistered common set of full-evolution replicates (e.g. three paired seeds), distinct from heldout measurement repeats.
3. **Repair frontend semantics:** remove “best to act ≠ best to learn”, rename the 0/5 aggregate to execution/gate status, and qualify the public alternative projection.

- `controlled_workload`: SUFFICIENT
- `public_baseline_surface`: NEEDS_ONE_FIX
- `frontend_fidelity`: REVISE
- `r2_redesign_required`: NO
- `additional_pre_stage_a_experiment_required`: NO
- `immediate_action`: ONE_ZERO_PROVIDER_FIX_BEFORE_IDENTITY

`REVISE_ZERO_PROVIDER_PLAN_OR_FRONTEND`
