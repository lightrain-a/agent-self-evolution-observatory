# Independent GPT-5.6 Sol review — E2-R17 V3 R3C signed capability

Date: 2026-09-06
Surface: ChatGPT web
Model: GPT-5.6 Sol
Thinking: Extra High 4/5
Conversation: https://chatgpt.com/c/6a9c4acc-4098-83ee-ae07-f8e422f0d25f
Frozen packet: `oracle_briefs/E2_R17_V3_STAGE_A_R3C_SIGNED_CAPABILITY_EXACT_CODE_REVIEW_20260906.md`
Frozen packet SHA256: `0a5d7a4442e05be79f366bcb1facddeaff8361c2d6f1160baa321a17f6e502ed`

## Delivery note

The packet was delivered as eight exact source chunks. Chunks 1–7 were individually ACKed. Due a UI/tool retry at the final turn, chunk 8 was submitted twice. Therefore this review is **not accepted as a clean PASS/authority receipt**. It is retained as adversarial review evidence only. Both resulting full assistant responses independently identified the same verdict-changing blocker and ended with the same token.

Response SHA256s:
- duplicate final response 1: `508cc69aed1ec97453b6673b4f4c8722ba901f32b62e0d07043399412ffe65c8`
- duplicate final response 2: `f5aadb8a009f5e741818950cf79dbce35e3f0f968dcb48f0be77922afa1d4fb4`

## Verdict

`REVISE_R3C_BEFORE_PROVIDER_RECOVERY`

## Reviewer synthesis

- `contract_sha256_acknowledged`: `03b2608872424da2bdf78408266a69b28ff565bc9d84bf929aa82ba7bc11e030`
- `preflight_sha256_acknowledged`: `5a82c3916fd883cdfe5fcfc542d531e16592b03fe65a74db8fa68c663d2bb021`
- `control_plane_revision`: `R3C_EXTERNAL_SIGNED_SUPPORT_CAPABILITY`
- `trusted_public_key_sha256_acknowledged`: `f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0`
- `capability_verifier_sha256_acknowledged`: `20b589917ea2ae8b8e00fb40cc008f11ce6d1f3853816fb30eb3cc56928f269a`
- `external_signer_sha256_acknowledged`: `aefdf214c92e2fbc6fb3735682de693368bc430dbf0c728a5bfb45b3a9472713`
- `minter_sha256_acknowledged`: `2c9af8fca89916e928b2219c6f87a455568ec1bb55db1494bcbe8bc6ddb71e67`
- `gate_sha256_acknowledged`: `0abd0325414838bc0692caeed7908f5ab4be1d36126c44cca1ed587d2f343752`
- `support_adjudicator_sha256_acknowledged`: `93006d803f27b79142d803b1a43fe7210f876c20d7c518be8ef6e54a67b3b90c`
- `tests_sha256_acknowledged`: `34ba48994eb8c9c208b6c16a1bc8be7aa7e41fa730f317cee98bcf3513852749`
- `scientific_equivalence_to_parent_r3`: `PASS`
- `external_trust_root_closed`: `FAIL`
- `full_forged_chain_closed`: `FAIL`
- `direct_bypass_closed`: `FAIL`
- `single_use_gate`: `PASS`
- `review_provenance_closed`: `FAIL`
- `runtime_compatibility`: `PASS`
- `provider_recovery_authority_affected`: `false`
- `r3_contract_redesign_required`: `false`
- `new_scientific_experiment_required`: `false`
- `stage_b_authority`: `false`
- `scientific_authority`: `false`
- `support_control_verdict`: `FAIL_R3_POST_TERMINAL_SUPPORT_CONTROL_PLANE`
- `execution_recommendation`: `DO_NOT_AUTHORIZE_R3C_RECOVERY`

## Exact remaining blocker

The Ed25519 primitive and host52 private-key separation are sound, but the guarded adjudicator derives `public_key_path` and `public_key_sha256` from the caller-supplied contract. Under the field-complete caller-writable threat model, a caller can substitute the contract trust root with an attacker keypair, rebuild the dependent JSON lineage consistently, sign the capability with the matching attacker private key, and satisfy the current verifier.

The minimum sufficient repair is control-plane-only:
1. independently hard-pin the production Ed25519 public-key fingerprint at point of use;
2. require the contract signer declaration and actual public-key bytes to equal that immutable production pin;
3. add a substituted-contract + attacker-keypair + fully consistent dependent-chain negative regression that must fail before consumption/output.

The reviewer explicitly did **not** request R3 scientific redesign, new scientific workload, provider execution, or Stage-B authority. The hard boundary remains `NO_PROVIDER_CALL_BEFORE_2026-09-07 00:00:00 +0800`.
