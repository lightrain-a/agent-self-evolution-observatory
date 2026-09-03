I treated every execution/result statement in the brief as a frozen protocol fact only; I did not infer any Stage-A or Stage-B scientific outcome. I explicitly acknowledge contract SHA256 6104caa0d797b3a6bdb94988626f8715ea697fe1c896ef839fa1837a80513fdd.

Edit
Independent adversarial pre-execution review — E2-R17 Semantic-Transfer V3 Stage A
A. Scientific object

Coherent in principle.

The intended causal object is clean: for a given search pool (T_K), acting is always determined by the same verifier-selected winner (a(T_K)), while only learner-visible evidence (g(T_K)) changes. If both learning arms start from the same (S_0), use the same acquired pools, and differ only in WIN-C versus MRW4 projection, later persistent-skill utility can identify a projection effect.

However, this identification requires the later Stage-B implementation to hold update sequencing fixed as well. The currently written Stage-B order specification does not yet guarantee that; see I.

B. Five-skeleton semantic crossing

Substantially better identified than V2 and scientifically usable for a narrow operationalized semantic contrast.

V3 fixes the central V2 problem: procedural-versus-binding is crossed inside each of five common skeletons, rather than inferred by contrasting unrelated task families. Matching workbook topology, sentinels, nuisance profile, distractor schedule, row-count schedule, output locations, RNG seed, and initial workbook bytes removes a large class of family-level nuisance explanations.

The remaining differences—natural-language instructions and golden answers—are unavoidable because they instantiate the semantic cell itself. They do mean that the estimand is not an abstract causal effect of a latent variable called “semantics.” It is the interaction for these explicitly operationalized procedural-transformation versus instance-binding-localization task constructions.

That narrower interpretation is valid before Stage A. A broad claim that V3 has isolated “semantic type independent of instruction form/task complexity” would not be justified.

C. Byte-identical initialization and semantic-blind profiles

Adequate for the intended matched interaction, with the same claim limitation as B.

Byte-identical XLSX initialization is a strong control: neither arm nor semantic cell can inherit a different workbook state before the instruction is applied. Semantic-blind update-profile and heldout-profile selection further prevents profile selection from encoding the semantic label.

This is sufficient for a controlled comparison of the two constructed semantic cells. It does not somehow make the cells identical except for a metaphysical semantic variable: instruction requirements and answer mappings necessarily change. Those constitute the experimental semantic manipulation rather than an uncontrolled workbook nuisance.

D. Five mechanism units and exact sign gate

The unit accounting is correct; the p-value interpretation needs to remain narrow.

The five skeleton-level interactions (I_h), not the 20 streams and not the (R=4) stochastic repetitions, are the five confirmatory mechanism units. Treating streams or replicates as additional semantic-generalization (n) would be pseudoreplication; V3 correctly does not do that.

For five pre-specified independent skeleton-level signs, an all-positive result has probability (1/32=0.03125) under the explicit directional sign null in which each unit has no greater than one-half probability of being positive and the five signs are independent. That number must not be presented as a conventional well-powered test of a population mean, nor as evidence that the five named skeletons are a random sample from all possible workflows.

Also, the sign gate does not itself test mean_h I_h > 0; all five (I_h>0) already implies a positive sample mean. The mean condition is therefore logically redundant under the all-positive gate.

This is not a Stage-A acquisition blocker, but any later confirmatory write-up must state the finite five-unit directional interpretation rather than inflate the p-value into broad semantic generalization.

E. Claim boundary and power

Appropriate if kept deliberately narrow.

With only five independent mechanism units, V3 should claim prospective consistency across the five frozen matched skeletons, not high-powered estimation of a general population effect. Explicitly declining an “80% power” claim is correct because no independent pre-outcome estimate of between-skeleton interaction variance exists.

The appropriate evidence would be the five individual (I_h) values, their magnitudes, the frozen all-positive gate, and the resulting finite-resolution directional test. No conventional power rhetoric should be retrofitted afterward.

F. Observable router

No hidden runtime-information advantage is apparent, but this is an engineered observable policy, not learned semantic discovery.

The deployed function receives only the instruction available to the actor and is explicitly denied family, template, task, semantic, hidden-value, and later-outcome metadata. On that runtime information boundary, it is legitimate.

But the router is extremely close to a hand-coded decoder of the benchmark construction: procedural cells are deliberately characterized by many visible transformation clauses and few binding alternatives, while binding cells have the opposite structure, and the parser recovers the hidden cells perfectly on all 270 generated tasks.

Therefore a successful router evaluation could support:

a frozen hand-engineered, actor-observable routing rule can exploit these visible task characteristics.

It could not by itself support:

the system learned semantic structure;
the router discovered the causal mechanism automatically; or
this is a generally deployable semantic classifier outside the frozen construction.

That distinction does not invalidate Stage A.

G. Equal-dose MRW4

Conceptually sound, but the frozen treated-pool selection rule is not sufficiently specified. This is a Stage-A blocker.

The support logic itself is good: acquire all pools first, inspect support only afterward, require at least four mixed pools per stream, prohibit replacement, and use exactly four failed-witness substitutions so failure dose is controlled.

The defect is the selection domain. The frozen text says that once a stream has at least four mixed pools, “exactly 4 treated pools per stream are selected by ascending SHA256(...)”. It does not explicitly say that the hash ranking is performed only over the mixed pools.

That matters. A stream can contain, for example, five mixed and three unmixed pools. Ranking all eight can select an unmixed pool, for which the frozen failed-witness selector is undefined. More importantly, leaving the candidate domain unstated allows the treatment-set semantics to be resolved after mixedness is observed.

The rule must be frozen before acquisition as:

[
C_s={p:;p\text{ is mixed in stream }s}
]

and, iff (|C_s|\ge4), choose exactly the four elements of (C_s) with smallest frozen hash values. No unmixed pool is eligible.

H. Conditioning on all-stream support

Scientifically acceptable for an explicitly support-qualified estimand.

The gate conditions on a pre-learning property of the frozen Stage-A search pools rather than on Stage-B treatment effects. Because there is no stream/task/model replacement after inspection, this is not conventional outcome-driven cherry-picking.

The resulting estimand is nevertheless conditional:

the WIN-C/MRW4 comparison for this frozen 20-stream suite conditional on every stream having sufficient mixed-pool positivity.

If the gate fails, the only scientifically clean action is the specified HOLD. If it passes, results must not be generalized to streams lacking mixed-search support.

That narrow conditional estimand is defensible.

I. Update order, evaluation order, stochasticity, and (R=4)

Stochastic-replication semantics are mostly sound, but the update-order specification is not sufficient for the later causal experiment. This should be repaired before Stage-A acquisition is allowed under this frozen prospective design.

The seed semantics are reasonable: when an actual provider seed exists, paired arms can share seed_sr; otherwise explicitly record that common-random-number pairing was unavailable. (R=4) is correctly treated as measurement replication rather than four new semantic units. No silent retry is also correct.

The update-order line is problematic:

SHA256("semantic-transfer-v3-update-order|s|r|arm")

There are two possible readings, and neither establishes the necessary causal control.

If it is intended to determine the order of the eight update pools, it contains no task/pool identifier and therefore cannot produce a unique ordering among those eight items. In addition, including arm would make the update sequence arm-dependent, causing WIN-C and MRW4 to differ in both evidence projection and sequence.

If instead it specifies only which arm is run first, then the within-arm ordering of the eight update pools remains unspecified.

For the state-level causal claim in A, both arms need the same pre-frozen eight-pool update order for each ((s,r)), generated from a key containing the pool/task identifier but not the treatment arm.

The heldout evaluation ordering is less fundamental because evaluation should not mutate learned state, but its exact task and arm ordering should still be unambiguous and frozen to control temporal/provider-order effects.

J. Stage-A fail-closed control plane

Most forbidden authority appears closed, but exact-once acquisition/replay is not established by the described controls. This is a Stage-A blocker.

The stated scope controls are strong against wrong mode, wrong K, heldout invocation, non-initial skills, unauthorized updater use, wrong run root, wrong concurrency, and missing/wrong lease context. Retry limit zero prevents a normal automatic provider retry.

What is not specified is an atomic exact-once rule for each of the 160 authorized task acquisitions.

An authorization containing the correct task set, a valid run root, and a valid global lease does not by itself prevent a second direct actor call for the same already-attempted task while that valid context remains active. Similarly, if a provider call succeeds but the local process dies before its sealed pool receipt is durably committed, restarting the runner can accidentally create a replacement pool even though provider_retry_limit=0.

A total provider-budget ceiling does not solve this: duplicated task A plus omitted task B can still satisfy the same global budget.

Thus the current description does not prove prevention of replacement sampling or replay.

The acquisition layer needs an immutable per-task call manifest and an atomic state transition before the external provider call. Once a task enters an attempted/in-flight state, no second provider call for that task may ever be permitted under the authorization. An ambiguous/crashed in-flight call must fail the entire run closed rather than be regenerated.

K. Previously repaired bypasses and remaining scope hole

The two stated bypasses appear closed at the protocol level, but an additional exactly-once hole remains.

The non-initial-skill compatibility bypass is explicitly closed by rejecting every non-initial skill and every updater receipt.

The cross-context direct-actor bypass is also substantially closed because the actor now requires the contract-bound run root, exact prefix-K list, exact concurrency, and an active lease bound simultaneously to contract SHA, authorization SHA, and run root.

The remaining hole is re-entry inside an otherwise valid context. A caller that already possesses the correct authorization, root, and active lease can apparently attempt the same authorized task again unless there is a per-task consumed/attempted ledger checked atomically by the actor itself.

This is precisely the kind of hole that a global lease does not eliminate.

L. Must-fix defects before the first Stage-A provider call

There are three verdict-changing repairs, all small and protocol-local:

Freeze the MRW4 treatment candidate domain. Hash-select the four treated pools exclusively from the support-qualified mixed-pool set; make unmixed pools ineligible by contract and code.

Add actor-enforced atomic exact-once task consumption. Predeclare all 160 acquisition units; atomically burn/mark each task before its provider call; reject every replay; if an attempted call has ambiguous completion, invalidate/abort the run rather than recollect it.

Correct and freeze the future Stage-B update ordering prospectively. Each ((s,r)) must use one identical deterministic order of its eight Stage-A pools in WIN-C and MRW4, with the pool/task ID in the hash and treatment arm excluded from the ordering key. This is necessary to make the claimed “projection is the only changed learning variable” true.

These repairs do not require broader experiments, new skeletons, new models, or more provider calls. They should be made in a newly frozen contract/control-plane object before any Stage-A acquisition, after which the existing fresh-review and model-identity qualification requirements apply again.

Decisive verdict

REVISE_BEFORE_STAGE_A

The core V3 scientific idea is not rejected. The crossed five-skeleton construction, support-qualified estimand, and separation between mechanism and router claims are substantially improved. But the current frozen object still leaves one ambiguous equal-dose treatment-selection rule, one acquisition replay/replacement hole, and one downstream order confound that violates the stated projection-only causal intervention. Those are protocol-identification defects rather than requests for additional experimentation.

JSON
{
  "contract_sha256_acknowledged": "6104caa0d797b3a6bdb94988626f8715ea697fe1c896ef839fa1837a80513fdd",
  "verdict": "REVISE_BEFORE_STAGE_A",
  "execution_recommendation": "DO_NOT_AUTHORIZE_STAGE_A_UNTIL_REVISED",
  "remaining_blockers": [
    "Freeze MRW4 treated-pool selection to the mixed-pool candidate set only.",
    "Add actor-enforced atomic per-task exact-once acquisition with fail-closed handling of ambiguous or interrupted calls.",
    "Freeze one identical task-ID-keyed Stage-B update order across WIN-C and MRW4, excluding arm from the ordering key."
  ],
  "stage_b_authority": false,
  "paper_claim_authority": false,
  "scientific_authority": false,
  "experiment_authority": false
}
