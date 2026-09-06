# Fresh independent execution review — E2-R17 Bridge V4-R2 Stage A R3 external-signed SCREEN search/support

Date: 2026-09-07
Role: fresh independent adversarial senior agent-systems / experimental-control-plane reviewer.
Stage: AFTER M3R4 adjudication / BEFORE Bridge Stage-A structural authorization / ZERO Bridge scientific provider call.

## Why R3 exists

R1 and R2 were frozen but never independently reviewed, never scientifically authorized, and never executed. R2 already repaired exact runner-runtime and authorization-scope binding. Before sending R2 to a reviewer, a local adversarial audit identified a deeper authority-provenance gap: a host69 caller with ordinary write access could theoretically fabricate a field-complete JSON authorization and satisfy content/hash checks without proving that an accepted independent review actually authorized the object.

R3 closes only that provenance gap. It preserves every R2 scientific and execution-geometry property and adds an external Ed25519 capability rooted in a host52 root-only private key. Host69 contains only the hard-pinned public key. A structural authorization JSON is explicitly insufficient by itself; actual provider execution additionally requires a host52-signed capability that binds the exact contract, preflight, accepted review receipt, structural authorization, runner/runtime/support code, identity, run root, lease path, and one-shot consumption marker. The runner verifies this capability against the hard-pinned production public key and atomically consumes the marker before creating the run root or reaching provider I/O.

## Frozen scientific boundary

The already independently reviewed V4-R2 protocol remains unchanged. Stage A R3 is deliberately narrow:

1. six frozen SCREEN streams;
2. eight frozen update tasks per stream = 48 tasks;
3. K=8 search for every task = 384 search rollout units;
4. seal exactly one K=8 pool per task;
5. only after all 384 units are complete, inspect mixed-pool support;
6. every one of the six streams must have at least four mixed pools;
7. no stream/task/K replacement if support fails;
8. Stage A executes zero FREE updater calls, zero deterministic scientific-state materializations, zero heldout actor calls, zero SCREEN method-effect analysis, and zero VALIDATION calls.

M3R4 returned `M3R4_OBSERVED_EXCESS_ONLY_NO_PROPENSITY_LOCALIZATION`. Under the frozen V4-R2 orthogonal decision logic, this narrows prior realization/variance language but does not gate Q1 or replace the prospective Bridge Q3 result. A separate outcome-aware eligibility receipt binds that decision and grants zero execution authority.

## Exact R3 object

R3 executable-object commit:
`da519c675bb32f92f5f5882f923022bd7e68aca9`

R3 contract:
- `generated/e2-r17-bridge-v4r2-stage-a-contract-r3-20260907.json`
- SHA256 `fef57d88fcaece2b1cb2e4d3915dd4ca011ca4518b66cc2d1cf288dff9d256af`
- status `FROZEN_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_SUPPORT`
- control-plane revision `STAGE_A_R3_EXTERNAL_SIGNED_EXECUTION_CAPABILITY`
- all authority bits false.

R3 zero-provider preflight:
- `generated/e2-r17-bridge-v4r2-stage-a-preflight-r3-20260907.json`
- SHA256 `74b08914016c28f48042c3e408d9de39c2ed56314a1215b71e7fe83f83b3d042`
- status `PASS_ZERO_PROVIDER_BRIDGE_V4R2_STAGE_A_CONTRACT_PREFLIGHT`.

R2 supersession:
- `generated/e2-r17-bridge-v4r2-stage-a-r2-supersession-20260907.json`
- SHA256 `4c3f63a19326e8758677e999947341268aa355d5535e5b048fc314118b88b482`
- R2 review started: false;
- R2 authorization minted: false;
- R2 provider I/O: false;
- R2 run root / lease / capability marker: absent.

External controller trust root:
- production public key SHA256 `f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0`;
- host52 keypair qualification receipt SHA256 `c9a8db49f39174e0508487bda4d161cb7dedf42d1b1813003654a09fb18e4125`;
- qualification confirms host52 private key is root:root, mode 0600, derives the exact stored production public key, and no private-key content/path is included in the receipt;
- no Bridge Stage-A private key is Git-tracked.

Signature context:
`E2-R17-BRIDGE-V4R2-STAGE-A-EXECUTION-CAPABILITY-V1`

Bridge-specific fresh identity:
- `generated/e2-r17-bridge-v4r2-stage-a-model-identity-20260907.json`
- SHA256 `3ffc4cc3589022c3f513919a2c1dab10bfce512299c3004548a593b2a8da114d`
- exactly one qualification call;
- `deepseek-v4-pro -> deepseek-v4-pro-ga-260813`;
- Ark Plan route;
- retry=0; thinking disabled;
- non-scientific identity qualification only.

Deterministic search-unit audit from the exact bound execution-plan source:
- 384 unique unit IDs;
- 6 SCREEN streams;
- 48 unique update tasks;
- exact unit-ID order SHA256 `fc1bdaa474ae9918ea5e436743c5ed09936da7346aedcb0d0e6287ff1da3f630`.

Verification before review:
- 24/24 Stage-A R3 control-plane/adversarial tests PASS under frozen actor runtime;
- 63/63 adjacent Bridge evidence/compiler/preparation tests PASS under frozen updater runtime;
- all R3 contract-bound code SHA values match;
- attacker-generated Ed25519 key signing a field-complete capability is rejected by the production verifier;
- capability-consumption marker is atomic `O_CREAT|O_EXCL` and single-use;
- run root, lineage lease, and consumption marker remain absent.

## R3 authority chain to audit carefully

The intended chain is:

1. this independent review returns PASS while `scientific_authority_now=false`;
2. only then may the structural authorization minter create a JSON authorization that binds exact contract/preflight/review hashes;
3. structural authorization explicitly remains insufficient for provider execution;
4. host52 signs an exact capability using the external root-only Ed25519 private key;
5. host69 verifies the signature using a point-of-use hard-pinned public-key SHA;
6. the capability binds exact contract, preflight, accepted review, structural authorization, runner/runtime/support code, identity, run root, lease, marker, and authority surface;
7. stop-before-provider actual-path preflight may verify but does not consume the capability;
8. actual execution re-verifies it and atomically consumes the marker before run-root creation and before provider I/O;
9. a second execution cannot reuse the capability because the marker already exists.

The structural authorization minter itself requires the accepted review receipt to report PASS for `authority_provenance` and `r2_supersession_clean`, exact contract/preflight SHA acknowledgements, no blockers, `ALLOW_SEPARATE_AUTHORIZATION`, and `scientific_authority_now=false`.

## Audit scope

Audit only whether this exact R3 Stage-A execution object is safe/methodologically faithful enough for a separately minted structural authorization followed by a separately host52-signed single-use capability. Do not redesign V4-R2, add workload, reopen M3R4, or inspect any nonexistent Bridge outcome.

Return concise A-H:

A. Scientific geometry and frozen unit coverage — exact 6×8×K8 / 384 units, no task/K replacement.
B. Stage separation — confirm no updater, deterministic state, heldout actor, SCREEN method-effect, or VALIDATION execution path exists in Stage A.
C. Support gate — every stream >=4 mixed pools; inspection only after all 384; fail/HOLD without replacement.
D. Identity/runtime/provider controls — Bridge-scoped exact identity, Ark Plan, retry=0, exact frozen runner interpreter, exact authorization scope, provider budget.
E. Exactly-once/fail-closed behavior — fresh run root/lease/marker, unique per-unit roots, no automatic retry, failure behavior, content-addressed refs/pools, marker burn before provider I/O.
F. Information leakage / causal integrity — whether support inspection and pool sealing preserve the future six-arm same-pool design; no hidden use of heldout/method effects.
G. M3R4 dependency and supersession — whether `OBSERVED_EXCESS_ONLY` is correctly treated as mechanism narrowing but not a Q1 Stage-A veto, and whether R1/R2 supersessions are clean.
H. Authority provenance — audit the external Ed25519 trust root, structural-auth-only insufficiency, exact review/auth/code binding, production public-key hard pin, attacker-key rejection, and point-of-use single-use consumption. Report any remaining verdict-changing blocker.

Then emit these exact synthesis fields:

- `scientific_geometry`: PASS/FAIL
- `stage_separation`: PASS/FAIL
- `support_gate`: PASS/FAIL
- `identity_runtime_budget`: PASS/FAIL
- `exactly_once_fail_closed`: PASS/FAIL
- `causal_integrity`: PASS/FAIL
- `m3r4_dependency`: PASS/FAIL
- `r1_supersession_clean`: PASS/FAIL
- `r2_supersession_clean`: PASS/FAIL
- `authority_provenance`: PASS/FAIL
- `remaining_blockers`: array
- `stage_a_execution_recommendation`: ALLOW_SEPARATE_AUTHORIZATION / REVISE_BEFORE_AUTHORIZATION / STOP_STAGE_A
- `scientific_authority_now`: must remain false at review time
- `contract_sha256_acknowledged`: must equal `fef57d88fcaece2b1cb2e4d3915dd4ca011ca4518b66cc2d1cf288dff9d256af`
- `preflight_sha256_acknowledged`: must equal `74b08914016c28f48042c3e408d9de39c2ed56314a1215b71e7fe83f83b3d042`
- `control_plane_revision`: must equal `STAGE_A_R3_EXTERNAL_SIGNED_EXECUTION_CAPABILITY`

Finish with exactly one token:

`PASS_TO_SEPARATE_BRIDGE_V4R2_STAGE_A_AUTHORIZATION`

or

`REVISE_STAGE_A_BEFORE_AUTHORIZATION`

or

`STOP_BRIDGE_V4R2_STAGE_A`
