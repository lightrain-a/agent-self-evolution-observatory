# Independent GPT-5.6 Sol exact-code review — E2-R17 V3 R3 post-terminal support control R1

Date: 2026-09-05
Surface: ChatGPT web
Model: GPT-5.6 Sol
Thinking: Extra High 4/5
Conversation: https://chatgpt.com/c/6a9c2a67-10f8-83ee-bd27-4f299ab50f64
Prompt packet: `oracle_briefs/E2_R17_V3_R3_POST_TERMINAL_SUPPORT_CONTROL_EXACT_CODE_REVIEW_20260905.md`
Prompt packet SHA256: `5a3717fa113af320becb0837bd3e08c740f0a54a8b175e5dbff87fdab2171a62`
Response SHA256: `48531c864c7218acd227632aae55045e92f9e23518099959cb04ed0e06b929f1`
Oracle transcript SHA256: `03d86cb389da6e4f419e589d2efc7239ad5049db4ae4ee818db256ced3efbacb`

## Verdict

`REVISE_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE`

## Reviewer findings

### A. Separation of authority from scientific read — PASS

The minter is structural-only. It validates contract/auth/summary/lease/manifests/claim metadata and only computes byte-level SHA-256 over `pool_k8.json`; it does not parse pool contents or compute mixed/success support. Hashing pool bytes is lineage verification, not scientific inspection.

### B. Terminal-state sufficiency — PASS

The minter sufficiently binds exact terminal summary status and counts; `support_inspected=false`; zero updater/heldout/scientific-score reads; summary/auth/contract hashes; terminal lease/summary binding; exact 158-unit manifest; 20-stream 7/7/8 geometry; 158 attempts and seals; attempt→seal→pool hashes; and absence of burned/censored cases.

### C. Authority narrowness — PASS

The permit grants only `stage_a_support_read=true`; provider execution, Stage-B, updater, heldout, analyzer, second backbone, public benchmark, paper promotion, and submission remain false.

### D. Single-use consumption — FAIL

The gate-internal O_CREAT|O_EXCL consumption-before-adjudication rule is sound, and unexpected return codes correctly leave the permit consumed. However, the frozen support adjudicator remains directly invocable with the recovery authorization and terminal summary. Therefore the wrapper is an authorized one-shot route but not an enforceable exclusive route. Direct invocation bypasses the support-read permit and consumption marker.

### E. No scientific-code redesign — PASS

The additive layer does not reproduce or alter the scientific support computation; it exact-hash checks and invokes the frozen adjudicator.

### F. Review binding — FAIL

The minter requires a completed GPT-5.6 Sol review receipt acknowledging exact minter/gate/adjudicator hashes, but the gate does not validate the permit's `minter_sha256` or reload/validate the embedded control-review receipt and its SHA/verdict. A permit-shaped JSON could therefore bypass the reviewed minter provenance.

### G. Tests/preflight — FAIL

The seven tests cover the major local failure cases, but do not cover:

1. direct invocation of the support adjudicator bypassing the gate/permit;
2. gate acceptance of a support authorization lacking demonstrable provenance from the exact reviewed minter/control-review receipt.

### H. Execution consequence — FAIL for this revision

The underlying R3 scientific design and provider-recovery object are not invalidated, but provider recovery should not start under this exact control-plane revision because the prior authority review required this ambiguity to be resolved before provider recovery.

## Required synthesis

- `minter_structural_only`: PASS
- `terminal_binding`: PASS
- `support_authority_narrowness`: PASS
- `single_use_gate`: FAIL
- `frozen_adjudicator_preserved`: PASS
- `exact_code_review_binding`: FAIL
- `tests_preflight`: FAIL
- `provider_recovery_authority_affected`: false
- `r3_contract_redesign_required`: false
- `new_scientific_experiment_required`: false
- `stage_b_authority`: false
- `remaining_blockers`:
  1. Make the support adjudicator enforceably reachable only through the support-read-authorized one-shot gate, without changing its scientific support semantics; direct invocation must not remain an authority bypass.
  2. Make the gate verify provenance/binding to the exact reviewed minter and control-review receipt, not merely gate/adjudicator hashes in a permit-shaped JSON; add zero-provider regression tests for both bypasses.
- `execution_recommendation`: Revise only the authority control plane, freeze new exact hashes, obtain a fresh exact-code control-plane review, and only after PASS proceed with the separate R3 provider-recovery authorization path. Do not change the recovery geometry, workload, support-analysis semantics, or Stage-B authority.

REVISE_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE
