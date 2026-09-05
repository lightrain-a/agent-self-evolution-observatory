# Independent GPT-5.6 Sol review — E2-R17 R3B support-control closure v2

Conversation: https://chatgpt.com/c/6a9c4238-ae54-83e8-84c4-6f6a97de24c9
Delivery object: `oracle_briefs/E2_R17_V3_STAGE_A_R3B_SUPPORT_GUARD_CLOSURE_REVIEW_V2_20260905.md`
Delivery object SHA256: `9c74c3f7eeb5a830c9fc2aeacc6973e29b4e5943a7de4e2369c348bb9ab4c082`
Reviewer model: GPT-5.6 Sol
Thinking: Extra High (4/5)
Scope: zero-provider exact-code closure of the two R1 support-control blockers only.

## Reviewer response

A–H audit

A. Direct adjudicator bypass — FAIL.
The naked CLI bypass is closed in the narrow sense: the adjudicator now requires both --support-authorization and --consumption-marker, and validate_support_read_gate() checks their bindings, paths, hashes, authority scope, terminal summary, bound code, review receipt, and canonical marker location.

However, this is not yet an enforceable provenance boundary. A direct caller with ordinary write access can construct a syntactically complete support-authorization JSON and canonical consumption-marker JSON containing all publicly derivable hashes/paths, then invoke the adjudicator directly. The adjudicator verifies artifact contents, but does not establish that the permit was actually emitted by the reviewed minter or that the marker was actually emitted by the gate.

B. Review/minter/gate/adjudicator provenance — FAIL.
The exact minter, gate, and adjudicator binaries are strongly hash-bound once a permit is accepted. That closes code-drift/stale-code substitution.

The remaining problem is the provenance root. control_review.path and control_review.sha256 come from the support permit itself. The loaded review is then checked for expected fields and acknowledged code hashes, but no independently trusted artifact pins the exact accepted review receipt SHA. Therefore a fully populated forged review can self-assert:

COMPLETED

ChatGPT web

GPT-5.6 Sol

the required verdict/revision

the exact known minter/gate/adjudicator hashes

stage_b_authority=false

scientific_authority=false

and the current checks have no independent authenticity anchor with which to distinguish it from the genuine reviewed receipt.

The same issue propagates to the support permit: it is hash-consistent, but its origin from the reviewed minter is not independently authenticated.

C. Single-use consumption / fail-closed behavior — PASS.
The gate correctly creates the canonical consumption artifact before invocation using O_CREAT | O_EXCL, fsyncs it and its directory, rejects pre-existing consumption/completion artifacts, and leaves the permit consumed when the adjudicator exits outside {0,3}. Concurrent attempts race safely at the exclusive create. Automatic retry is correctly forbidden.

This PASS concerns one-shot mechanics after entering the legitimate gate path; it does not cure the provenance problem in A/B.

D. Regression tests — FAIL for blocker closure.
The supplied suite directly exercises:

missing support permit on direct adjudicator invocation;

invalid stage_a_support_read;

a forged/incomplete review;

consume-before-invoke;

fail-closed unexpected adjudicator failure;

retry refusal;

terminal PASS without Stage-B execution authority.

The reported 9/9 execution is internally consistent with the frozen preflight.

But the verdict-changing adversarial case is absent: there is no regression that creates a field-complete forged review + field-complete forged support permit + forged canonical consumption marker and then attempts direct adjudicator invocation. The present direct-invocation test succeeds as a negative test because it omits the two required CLI arguments; it does not establish that those arguments cannot themselves be fabricated.

E. Scientific equivalence to parent R3 — PASS.
The supplied parent-equality table preserves all stated science keys, including recovery exceptions, opportunity manifest, exact-once acquisition, equal-dose support, actor/budget, analysis boundary, Stage-B no-authority plan, runtime, run root, and lease. The provider runner/authorization components are reported unchanged. Adding support-control guards around adjudication does not alter the frozen 158 + 1 matched censor + 1 terminal technical missing, K=8, 7/7/8, or >=4 mixed-pool scientific geometry.

No R3 scientific redesign is justified by this review.

F. Forbidden authority expansion — PASS.
On the intended path, the support authorization grants only stage_a_support_read=true; provider execution, Stage-B learning execution, updater, heldout evaluation, analyzer, second backbone, public benchmark, paper promotion, and submission remain false. The shown terminal PASS test also preserves stage_b_authority=false. Nothing here authorizes scientific effect inference.

G. Hard provider time gate — CONFIRMED.
NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800 remains binding. This review neither relaxes that timestamp nor grants provider execution. The support-control code shown is zero-provider control-plane machinery; the hard provider reset boundary remains external and mandatory.

H. Next consequence — NOT YET ALLOWED.
The intended sequencing is correct: only after the provider reset and a fresh identity should a separate R3 recovery authorization be considered; support read should remain unavailable until the exact terminal 158-pool state, and Stage-B execution must remain false.

But because A/B are not fully closed, that consequence cannot yet be authorized from this review. The required repair is control-plane-only: anchor the accepted review/permit to a provenance source that the caller cannot self-author, and add the complete forged-permit/direct-adjudicator regression. No scientific workload or R3 geometry change is warranted.

Required synthesis
contract_sha256_acknowledged: 7454608db38e58f2b39b412045e5a2ffe6f2b26db0d012bb2983e37259cb2da9
support_guard_preflight_sha256_acknowledged: 94043973e6b89edf0e0132e8c503854063ab3ea32801ccc2766359554264084f
control_plane_revision: R3B_POST_TERMINAL_SUPPORT_GUARD
minter_sha256_acknowledged: 0e7bf96b3e6274de8c6e5738b46924990de8b8897c04bb3871fce0e5fdd06d43
gate_sha256_acknowledged: 333c3ef89746c4d7e44b20769e068b0520140dffb4fa79f32da1f9e981cefb10
support_adjudicator_sha256_acknowledged: d8ad232562b5f88f7394555c158d83b7e00dd235f2ef8631c89a3cabe6b896eb
scientific_equivalence_to_parent_r3: PASS
direct_bypass_closed: FAIL
review_provenance_closed: FAIL
single_use_gate: PASS
minter_structural_only: PASS
tests_preflight: FAIL
provider_recovery_authority_affected: false
r3_contract_redesign_required: false
new_scientific_experiment_required: false
stage_b_authority: false
scientific_authority: false
support_control_verdict: FAIL_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE
execution_recommendation: DO_NOT_AUTHORIZE_R3B_RECOVERY
remaining_blockers:
  - The support authorization and consumption marker are content-validated but not origin-authenticated; a field-complete caller-fabricated permit/marker pair can still satisfy the guarded adjudicator without proving passage through the reviewed minter/gate.
  - The control-review receipt lacks an independently trusted exact-SHA/provenance anchor, and the regression suite does not test a fully populated forged review + forged permit + forged canonical marker against direct adjudicator invocation.

REVISE_R3B_BEFORE_PROVIDER_RECOVERY
