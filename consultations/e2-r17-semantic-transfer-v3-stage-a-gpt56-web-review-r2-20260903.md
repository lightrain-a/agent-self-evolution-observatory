Independent adversarial R2 pre-execution review

I acknowledge the frozen R2 object at contract SHA256 f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234. I assess only prospective scientific/protocol validity. No Stage-A or Stage-B scientific outcome exists, and nothing in this review should be interpreted as evidence about the mechanism hypothesis.

A. Core projection-only scientific object

PASS.

The causal object remains coherent and appropriately narrow. Stage A freezes the realized K=8 search pools; acting continues to use the deterministic verifier-selected winner; the later intervention changes only the learner-visible projection on the designated update pools. R2's three repairs do not alter search, acting, initial state, semantic assignment, update-pool universe, or treatment dose.

Importantly, the new mixed-pool qualification is based exclusively on properties of the already-sealed pre-update search pool—presence of verifier-success and verifier-failure trajectories. It does not inspect downstream persistent-skill utility and therefore does not introduce outcome-conditioned treatment assignment.

The valid estimand remains conditional on the realized, support-qualified frozen pools. It is not an estimand about arbitrary search pools or semantic categories in general.

B. MRW4 mixed-only candidate domain

PASS.

R2 removes the R1 ambiguity. The sequence is now unambiguous:

sealed K8 pools → C_s = mixed pools → support gate |C_s| >= 4 → hash-rank within C_s → four treated pools.

The combination of:

explicit unmixed_pool_eligible = false,

hash_rank_applied_only_within_candidate_domain = true,

code-level use of mixed_tasks_by_stream[stream_id],

the explicit selected-set subset assertion,

eliminates a legitimate protocol path by which an unmixed pool could enter T_s.

The hash rule is therefore a deterministic selector within the scientifically admissible support domain rather than a selector over all eight pools.

C. Actor-level atomic exactly-once acquisition

PASS.

For the stated process-failure/concurrent-invocation threat model, the O_CREAT | O_EXCL attempt burn before provider I/O closes the important R1 replay hole.

For two concurrent valid invocations of the same task under the same authorization, only one can create the attempt pathname successfully. The losing invocation encounters the already-created pathname and fails before reaching provider I/O. This remains true even while the winning invocation is still in flight and has not produced a seal.

The protection is correctly actor-side rather than merely runner-side, so bypassing the normal runner does not restore same-task replay authority.

D. Crash and ambiguous-call semantics

PASS.

Refusing to recollect an attempted-but-unsealed task is the scientifically correct fail-closed choice.

Once any provider exposure for a scientific unit may have happened, replacing that unit with a fresh realization would change the sampling process conditional on execution success and could silently introduce replacement-selection bias. Burning the unit instead preserves the first-run-only interpretation.

The cost—that an interrupted Stage-A run may become scientifically unusable—is appropriate. Operational recoverability must not take precedence over preservation of the prospective sampling protocol.

Separate adjudication of such a run is also correctly distinguished from automatic retry.

E. Seal and terminal-universe completeness

PASS.

The combination is sufficient for the planned first-run-only Stage A:

immutable task attempt,

immutable task seal tied to the exact attempt SHA,

seal tied to the exact frozen pool_k8.json SHA,

exact expected-vs-actual attempt filename universe,

exact expected-vs-actual seal filename universe,

exact 160-task manifest equality and bindings.

This blocks the relevant silent-success failures.

A duplicated scientific unit cannot substitute for an omitted one because terminal success requires the exact expected ID sets rather than merely a count of 160. A post-provider/pre-seal crash cannot be converted into a replacement draw because its attempt remains burned, while absence of the corresponding seal prevents the terminal state. Substitution of a different pool artifact is caught by the task/path/SHA binding.

Thus failure can produce an incomplete run, but it cannot legitimately produce a falsely complete 160-unit run.

F. Remaining same-task race / exactly-once hole

PASS.

I do not identify a remaining same-authorization, same-scientific-task replay path in the acquisition logic described.

The critical ordering is:

validate scope → exclusive attempt burn → provider acquisition → freeze pool → exclusive seal.

The attempt file, rather than the final seal, is what arbitrates concurrency. Consequently, two actors cannot both reach provider acquisition merely because neither has yet generated a seal.

Likewise, an already sealed task still has its immutable attempt marker, so completion does not reopen acquisition.

This conclusion depends on the frozen execution path actually maintaining the stated prohibition on provider relaunch/replacement/ambiguous recollection; the supplied source-order audit and preflight state that this is the bound implementation being reviewed. There is therefore no additional immediate blocker to infer from the brief.

G. Stage-B arm-blind update ordering

PASS.

The R1 sequencing confound is fixed.

Using

SHA256("semantic-transfer-v3-update-order|stream_id|replicate_index|task_id")

provides a genuine permutation over the eight task IDs for a given stream/replicate. Because arm is absent, WIN-C and MRW4 receive the same update pools in the same positions.

This is materially different from the defective R1 formula: task identity now determines the permutation, rather than an arm-associated quantity determining ordering.

Separating this from the wall-clock state-arm scheduling function is scientifically correct. The two objects answer different questions:

within-arm update order must be identical across treatment arms because updater state is path-dependent;

which state arm happens to execute first in wall-clock time can be independently frozen without changing that within-arm sequence.

Accordingly, projection is no longer structurally confounded with update-pool order.

H. Heldout ordering and R=4 stochasticity

PASS for prospective Stage-B specification; no Stage-B authority granted.

The heldout schedule is adequately frozen over stream, replicate, heldout task identity, and arm. Because heldout evaluation is specified as non-mutating, its schedule cannot alter the persistent states being compared.

R=4 is also interpreted correctly. The four realizations are repeated stochastic measurements associated with a skeleton-level semantic interaction; they do not multiply the semantic sample size.

Therefore an analysis treating 20 streams or the replicate-expanded observations as independent semantic units would be invalid, but the frozen specification explicitly rules that out.

I. Claim boundaries

PASS.

R2 preserves the essential restrictions.

The semantic claim remains about five frozen operationalized skeleton interactions, each crossing the specified procedural-transformation and instance-binding-localization conditions. It is not elevated into evidence for a universal semantic taxonomy.

The directional mechanism statement remains based on the five skeleton interactions. Under the stated finite-five-unit interpretation, an all-positive pattern has the stated 1/32 sign resolution; it cannot be repackaged as conventional population-level power, broad generalization, or evidence from 20/80 independent semantic units.

The router remains explicitly a frozen hand-engineered, actor-visible policy. Success of that router cannot establish learned semantic discovery and, correctly, cannot override failure of the primary mechanism gate.

J. Present authority and fail-closed control plane

PASS.

The reviewed state remains zero-authority.

At review time:

no provider call exists;

scientific execution is false;

R2 run root is absent;

R2 lease is absent;

Stage-A provider authority is false;

Stage-B/updater/heldout/analyzer/paper authority is false.

Most importantly, this PASS does not authorize Stage A. The next permitted transition is the separately required fresh actor-model identity qualification against the frozen R2 object. Only after that identity qualification passes may the separately scoped single-use Stage-A authorization be minted.

No review artifact, test result, contract, preflight receipt, or this review itself substitutes for that authorization.

K. Must-fix defects before the first Stage-A provider call

None identified.

The three R1 verdict-changing failures have been repaired at the appropriate layers:

treatment eligibility is now mixed-only and deterministic;

task acquisition now has pre-provider actor-side atomic consumption with fail-closed ambiguity semantics and exact terminal-universe validation;

Stage-B update sequencing is now task-ID keyed and arm-blind.

I do not find a remaining defect in the frozen R2 description that is sufficiently causal or protocol-critical to justify another pre-Stage-A revision. Broader experiments, additional semantic skeletons, extra models, or optional operational hardening are not prerequisites for the first Stage-A call and therefore are intentionally not proposed here.

Decisive verdict

PASS_TO_SEPARATE_STAGE_A_AUTHORIZATION

Execution recommendation: ALLOW_SEPARATE_STAGE_A_AUTHORIZATION.

This verdict permits only the next fresh actor-model identity qualification step and, conditional on that qualification passing, minting of the already-scoped single-use Stage-A authorization. It conveys no Stage-B, scientific-result, paper-claim, or experiment authority.

JSON
{
  "contract_sha256_acknowledged": "f5382c552f2e6644e4cbda408510119664a8c6f8502628586c9ff5583abd1234",
  "verdict": "PASS_TO_SEPARATE_STAGE_A_AUTHORIZATION",
  "execution_recommendation": "ALLOW_SEPARATE_STAGE_A_AUTHORIZATION",
  "remaining_blockers": [],
  "stage_b_authority": false,
  "paper_claim_authority": false,
  "scientific_authority": false,
  "experiment_authority": false
}
