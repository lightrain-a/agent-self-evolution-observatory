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


---
## Original R3 contract compact deterministic audit view

Original full R3 contract SHA256: `fef57d88fcaece2b1cb2e4d3915dd4ca011ca4518b66cc2d1cf288dff9d256af`. Only the repetitive 384 `unit_ids` strings are replaced here by count/order SHA; every other contract field is reproduced.

```json
{
  "actor": {
    "concurrency": 1,
    "max_output_tokens": 8192,
    "max_turns": 10,
    "provider_retry_limit": 0,
    "requested_model": "deepseek-v4-pro",
    "required_resolved_model": "deepseek-v4-pro-ga-260813",
    "search_k": 8,
    "temperature": 0,
    "thinking": "disabled"
  },
  "artifact_type": "e2-r17-bridge-v4r2-stage-a-screen-search-support-contract",
  "authority": {
    "actor_evaluation": false,
    "analysis": false,
    "deterministic_state_materialization": false,
    "free_updater": false,
    "paper_promotion": false,
    "provider_io": false,
    "scientific_experiment": false,
    "screen_outcome_opening": false,
    "search_pool_acquisition": false,
    "support_inspection": false,
    "validation_opening": false
  },
  "bound_code": {
    "actor_rollout": {
      "path": "research_pipeline/e2_r17_actor_pool.py",
      "sha256": "ade5f605f32056b7797dbcbcb7b3e839b9c18dce1c0f287f609d86cee3463ef4"
    },
    "ark_adapter": {
      "path": "research_pipeline/e2_r17_ark_plan_react.py",
      "sha256": "7a7a9c40774429ac3c9a7c8c003bbc46628a6ef574bd481e628668894e803fba"
    },
    "authorization_minter": {
      "path": "scripts/authorize_e2_r17_bridge_v4r2_stage_a.py",
      "sha256": "3f1778de2254f7a47acde4334f4f81dbf3086b2fc583fb808fa057b33bf5815c"
    },
    "capability_signer": {
      "path": "scripts/sign_e2_r17_bridge_v4r2_stage_a_capability.py",
      "sha256": "b31d2ece1fc3f4001e83ef20b72aaad0f4bcfdd97bb5639af2095d8ae4bf1942"
    },
    "capability_verifier": {
      "path": "research_pipeline/e2_r17_bridge_v4r2_stage_a_capability.py",
      "sha256": "4c2bac59ab85410240d2f8591c6f92a2cf66277b9720285bb30e76c7861d8622"
    },
    "execution_plan": {
      "path": "research_pipeline/e2_r17_bridge_v4r2_execution_plan.py",
      "sha256": "d048f0c27c040cb84f7ca157579ed8b099b8b93b0df111a59bf7ee59a0364709"
    },
    "provider_budget": {
      "path": "research_pipeline/e2_r17_provider_budget.py",
      "sha256": "df819b30a31e62e007e3f85ae76aa8d06faefaa56e9acefe71ceadb9f8fce444"
    },
    "runner": {
      "path": "scripts/run_e2_r17_bridge_v4r2_stage_a.py",
      "sha256": "b66b9ddd8b7464e929f2ff3270e937a094f93a5e7f35b9c5da00fd470ca1bc18"
    },
    "runtime": {
      "path": "research_pipeline/e2_r17_bridge_v4r2_stage_a_runtime.py",
      "sha256": "ccc76c67fdc0b03c737e2d333bf7a29a724d7ec26f5c954359d05f8de000fa52"
    },
    "support": {
      "path": "research_pipeline/e2_r17_bridge_v4r2_stage_a_support.py",
      "sha256": "c4df9611c7c1f8b95636532bb5fdc16dea4195b8a11c03c974b38d457564f149"
    }
  },
  "budget": {
    "heldout_actor_call_ceiling": 0,
    "per_search_unit_call_ceiling": 10,
    "removed_or_unused_calls_reallocatable": false,
    "search_provider_call_ceiling": 3840,
    "updater_call_ceiling": 0
  },
  "control_plane_revision": "STAGE_A_R3_EXTERNAL_SIGNED_EXECUTION_CAPABILITY",
  "created_at_utc": "2026-09-06T18:30:04+00:00",
  "env_file": "/home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/.env",
  "initial_skill": {
    "path": "/data/wyt/evidence-substrates/MindMemOS-20260817/resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md",
    "sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb"
  },
  "lineage_lease_path": "/data/wyt/e2-r17-search-projection/lineage-leases/e2-r17-bridge-v4r2-stage-a-screen-v1.json",
  "m3r4_eligibility": {
    "path": "generated/e2-r17-m3r4-to-bridge-v4r2-eligibility-adjudication-20260907.json",
    "sha256": "74a82e3398de56d4c7dd81744f7cee9ebfd6e2bfdeb4e7b9c7b96cd29f0465e0",
    "status": "PASS_M3R4_NARROWS_MECHANISM_BUT_DOES_NOT_BLOCK_BRIDGE_V4R2_STAGE_A_ELIGIBILITY"
  },
  "mindmemos": {
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817"
  },
  "model_identity": {
    "path": "generated/e2-r17-bridge-v4r2-stage-a-model-identity-20260907.json",
    "scientific_tranche": "E2-R17-BRIDGE-V4R2-STAGE-A",
    "sha256": "3ffc4cc3589022c3f513919a2c1dab10bfce512299c3004548a593b2a8da114d",
    "status": "PASS_BRIDGE_V4R2_STAGE_A_MODEL_IDENTITY"
  },
  "next_gate": "ZERO_PROVIDER_STAGE_A_CONTRACT_PREFLIGHT_THEN_INDEPENDENT_EXECUTION_REVIEW",
  "outcome_boundary": {
    "heldout_actor_calls": 0,
    "method_effect_read": false,
    "updater_calls": 0,
    "validation_open": false
  },
  "protocol": {
    "path": "generated/e2-r17-state-compiler-bridge-protocol-v4-r2-20260903.md",
    "review_path": "generated/e2-r17-state-compiler-bridge-v4r2-preexecution-rereview-20260904.json",
    "review_sha256": "fa4f4220ff8761dd675e114f50e2cb2e8b38c51776ccc396326713aa78c30136",
    "review_verdict": "PASS_PREEXECUTION_DESIGN",
    "sha256": "1bc74c6f98e38535cb3865dcd41fb244b7d17c295db0ee9835937cc1034f9ef7"
  },
  "run_root": "/data/wyt/e2-r17-search-projection/runs/bridge-v4r2-stage-a-screen-20260907",
  "runtime": {
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt",
    "freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "qualification_path": "/data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-bridge-v4r2-execution-prep-20260906/generated/e2-r17-runtime-dependency-qualification-r2-20260828.json",
    "qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "qualification_status": "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2",
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv"
  },
  "schema_version": "1.0",
  "scientific_object": "E2-R17-STATE-COMPILER-BRIDGE-V4R2",
  "search": {
    "exact_k": 8,
    "order": "frozen execution-plan SHA rank",
    "stream_ids": [
      "bridge-agj-01",
      "bridge-fmv-00",
      "bridge-ioc-01",
      "bridge-msp-00",
      "bridge-ska-00",
      "bridge-tsr-01"
    ],
    "task_ids": [
      "r17-b8-agj-p6",
      "r17-b7-agj-p2",
      "r17-b8-agj-p3",
      "r17-b7-agj-p5",
      "r17-b8-agj-p7",
      "r17-b8-agj-p4",
      "r17-b8-agj-p8",
      "r17-b7-agj-p7",
      "r17-b7-fmv-p6",
      "r17-b8-fmv-p2",
      "r17-b8-fmv-p4",
      "r17-b7-fmv-p5",
      "r17-b7-fmv-p7",
      "r17-b8-fmv-p8",
      "r17-b8-fmv-p5",
      "r17-b8-fmv-p7",
      "r17-b8-ioc-p2",
      "r17-b8-ioc-p6",
      "r17-b7-ioc-p0",
      "r17-b8-ioc-p8",
      "r17-b7-ioc-p3",
      "r17-b8-ioc-p0",
      "r17-b7-ioc-p4",
      "r17-b7-ioc-p5",
      "r17-b7-msp-p2",
      "r17-b8-msp-p2",
      "r17-b7-msp-p6",
      "r17-b8-msp-p3",
      "r17-b8-msp-p1",
      "r17-b7-msp-p7",
      "r17-b7-msp-p3",
      "r17-b7-msp-p8",
      "r17-b8-ska-p3",
      "r17-b7-ska-p4",
      "r17-b7-ska-p7",
      "r17-b7-ska-p3",
      "r17-b7-ska-p6",
      "r17-b8-ska-p1",
      "r17-b8-ska-p4",
      "r17-b7-ska-p1",
      "r17-b7-tsr-p3",
      "r17-b8-tsr-p2",
      "r17-b7-tsr-p2",
      "r17-b8-tsr-p8",
      "r17-b8-tsr-p1",
      "r17-b8-tsr-p4",
      "r17-b8-tsr-p0",
      "r17-b8-tsr-p7"
    ],
    "tasks_by_stream": {
      "bridge-agj-01": [
        "r17-b8-agj-p6",
        "r17-b7-agj-p2",
        "r17-b8-agj-p3",
        "r17-b7-agj-p5",
        "r17-b8-agj-p7",
        "r17-b8-agj-p4",
        "r17-b8-agj-p8",
        "r17-b7-agj-p7"
      ],
      "bridge-fmv-00": [
        "r17-b7-fmv-p6",
        "r17-b8-fmv-p2",
        "r17-b8-fmv-p4",
        "r17-b7-fmv-p5",
        "r17-b7-fmv-p7",
        "r17-b8-fmv-p8",
        "r17-b8-fmv-p5",
        "r17-b8-fmv-p7"
      ],
      "bridge-ioc-01": [
        "r17-b8-ioc-p2",
        "r17-b8-ioc-p6",
        "r17-b7-ioc-p0",
        "r17-b8-ioc-p8",
        "r17-b7-ioc-p3",
        "r17-b8-ioc-p0",
        "r17-b7-ioc-p4",
        "r17-b7-ioc-p5"
      ],
      "bridge-msp-00": [
        "r17-b7-msp-p2",
        "r17-b8-msp-p2",
        "r17-b7-msp-p6",
        "r17-b8-msp-p3",
        "r17-b8-msp-p1",
        "r17-b7-msp-p7",
        "r17-b7-msp-p3",
        "r17-b7-msp-p8"
      ],
      "bridge-ska-00": [
        "r17-b8-ska-p3",
        "r17-b7-ska-p4",
        "r17-b7-ska-p7",
        "r17-b7-ska-p3",
        "r17-b7-ska-p6",
        "r17-b8-ska-p1",
        "r17-b8-ska-p4",
        "r17-b7-ska-p1"
      ],
      "bridge-tsr-01": [
        "r17-b7-tsr-p3",
        "r17-b8-tsr-p2",
        "r17-b7-tsr-p2",
        "r17-b8-tsr-p8",
        "r17-b8-tsr-p1",
        "r17-b8-tsr-p4",
        "r17-b8-tsr-p0",
        "r17-b8-tsr-p7"
      ]
    },
    "unit_count": 384,
    "unit_ids_compacted": true,
    "unit_ids_count": 384,
    "unit_ids_order_sha256": "fc1bdaa474ae9918ea5e436743c5ed09936da7346aedcb0d0e6287ff1da3f630",
    "unit_ids_reconstruction": "Exact list is deterministically reconstructed by search_units(SCREEN) in the full bound execution-plan source included below; original R3 contract SHA is for the uncompacted JSON."
  },
  "signed_capability_control": {
    "algorithm": "Ed25519",
    "capability_consumed_before_provider_io": true,
    "consumption_marker_path": "/data/wyt/e2-r17-search-projection/capability-consumption/e2-r17-bridge-v4r2-stage-a-screen-v1.json",
    "control_plane_revision": "STAGE_A_R3_EXTERNAL_SIGNED_EXECUTION_CAPABILITY",
    "controller_keypair_qualification_path": "generated/e2-r17-bridge-v4r2-stage-a-controller-keypair-qualification-20260907.json",
    "controller_keypair_qualification_sha256": "c9a8db49f39174e0508487bda4d161cb7dedf42d1b1813003654a09fb18e4125",
    "controller_keypair_qualification_status": "PASS_HOST52_EXTERNAL_ED25519_CONTROLLER_KEYPAIR_QUALIFICATION",
    "external_controller": "host52 root-only Ed25519 private key; private key is never copied to host69 or Git",
    "production_public_key_path": "generated/e2-r17-bridge-v4r2-stage-a-controller-public-key-20260907.pem",
    "production_public_key_sha256": "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0",
    "signature_context": "E2-R17-BRIDGE-V4R2-STAGE-A-EXECUTION-CAPABILITY-V1",
    "signed_capability_required_at_runner_point_of_use": true,
    "structural_authorization_alone_is_insufficient": true
  },
  "stage": "SCREEN_STAGE_A_SEARCH_SUPPORT",
  "status": "FROZEN_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_SUPPORT",
  "suite": {
    "metadata_sha256": "c4a966e03cf9c0c0d1ff20d23e8be6f2cbdfbca6225182ca705a84e27d306992",
    "root": "/data/wyt/e2-r17-search-projection/state-compiler-bridge-suite-v1-20260903",
    "split_manifest_sha256": "d1606c6a5caeaabd35361fc573b8bf015f20e7c9d8a5e3adc0a85b032a5b041b",
    "suite_manifest_sha256": "ec26f9a899786d2c188f0324961b9a9b6eef28c39240fd5987b0145fb68bc9ba"
  },
  "support_gate": {
    "all_six_streams_must_pass": true,
    "inspection_after_all_384_search_units": true,
    "mixed_pools_per_stream_minimum": 4,
    "stream_task_or_k_replacement": false
  }
}
```


---
## R3 zero-provider preflight
Path: `generated/e2-r17-bridge-v4r2-stage-a-preflight-r3-20260907.json`
SHA256: `74b08914016c28f48042c3e408d9de39c2ed56314a1215b71e7fe83f83b3d042`

```json
{
  "artifact_type": "e2-r17-bridge-v4r2-stage-a-contract-preflight",
  "capability_consumption_marker_fresh": true,
  "contract_path": "/data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-bridge-v4r2-execution-prep-20260906/generated/e2-r17-bridge-v4r2-stage-a-contract-r3-20260907.json",
  "contract_sha256": "fef57d88fcaece2b1cb2e4d3915dd4ca011ca4518b66cc2d1cf288dff9d256af",
  "control_plane_revision": "STAGE_A_R3_EXTERNAL_SIGNED_EXECUTION_CAPABILITY",
  "controller_keypair_qualification_sha256": "c9a8db49f39174e0508487bda4d161cb7dedf42d1b1813003654a09fb18e4125",
  "controller_keypair_qualification_status": "PASS_HOST52_EXTERNAL_ED25519_CONTROLLER_KEYPAIR_QUALIFICATION",
  "created_at_utc": "2026-09-06T18:30:05+00:00",
  "heldout_actor_calls": 0,
  "heldout_overlap": 0,
  "lease_fresh": true,
  "method_effect_read": false,
  "next_gate": "FRESH_INDEPENDENT_STAGE_A_R3_EXECUTION_REVIEW_BEFORE_STRUCTURAL_AUTHORIZATION",
  "private_signing_key_tracked_in_git": false,
  "production_public_key_sha256": "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0",
  "provider_calls": 0,
  "provider_claims": 0,
  "run_root_fresh": true,
  "schema_version": "1.0",
  "scientific_outcomes_read": false,
  "search_k": 8,
  "search_units": 384,
  "signed_capability_required_at_runner_point_of_use": true,
  "status": "PASS_ZERO_PROVIDER_BRIDGE_V4R2_STAGE_A_CONTRACT_PREFLIGHT",
  "streams": 6,
  "structural_authorization_alone_is_insufficient": true,
  "support_mixed_minimum_per_stream": 4,
  "tasks": 48,
  "updater_calls": 0,
  "validation_open": false
}

```


---
## R2 supersession receipt
Path: `generated/e2-r17-bridge-v4r2-stage-a-r2-supersession-20260907.json`
SHA256: `4c3f63a19326e8758677e999947341268aa355d5535e5b048fc314118b88b482`

```json
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-bridge-v4r2-stage-a-r2-supersession",
  "date": "2026-09-07",
  "status": "PASS_STAGE_A_R3_SUPERSEDES_UNUSED_R2_EXTERNAL_AUTHORITY_PROVENANCE_REPAIR",
  "scientific_object": "E2-R17-STATE-COMPILER-BRIDGE-V4R2",
  "superseded_r2": {
    "contract_path": "generated/e2-r17-bridge-v4r2-stage-a-contract-r2-20260907.json",
    "contract_sha256": "80fc7a9a85fbb7607d7744048886030a0b55bff15c7463617f5e8bd38253967c",
    "preflight_path": "generated/e2-r17-bridge-v4r2-stage-a-preflight-r2-20260907.json",
    "preflight_sha256": "5f38353025aa1837ce154f74c61143362a71f90d0ee9e9c4eb67924ec3e76a1e",
    "review_packet_path": "oracle_briefs/E2_R17_BRIDGE_V4R2_STAGE_A_R2_EXECUTION_REVIEW_PACKET_COMPACT_20260907.md",
    "review_packet_sha256": "7e797a847a61766521f89baabaefe1cd0a9f89a7bbba7a578ffd513050128e9b",
    "review_packet_commit": "2e6255de",
    "independent_review_started": false,
    "scientific_authorization_minted": false,
    "provider_io": false,
    "run_root_created": false,
    "lineage_lease_created": false,
    "capability_consumption_marker_created": false
  },
  "replacement_r3": {
    "contract_path": "generated/e2-r17-bridge-v4r2-stage-a-contract-r3-20260907.json",
    "contract_sha256": "fef57d88fcaece2b1cb2e4d3915dd4ca011ca4518b66cc2d1cf288dff9d256af",
    "preflight_path": "generated/e2-r17-bridge-v4r2-stage-a-preflight-r3-20260907.json",
    "preflight_sha256": "74b08914016c28f48042c3e408d9de39c2ed56314a1215b71e7fe83f83b3d042",
    "control_plane_revision": "STAGE_A_R3_EXTERNAL_SIGNED_EXECUTION_CAPABILITY",
    "production_public_key_sha256": "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0"
  },
  "repair_scope": {
    "scientific_geometry_changed": false,
    "streams_changed": false,
    "tasks_changed": false,
    "search_k_changed": false,
    "support_threshold_changed": false,
    "model_identity_changed": false,
    "provider_budget_changed": false,
    "stage_separation_changed": false,
    "r2_point_of_use_runtime_binding_preserved": true,
    "r2_exact_authorization_scope_binding_preserved": true,
    "new_external_ed25519_controller_trust_root": true,
    "new_structural_authorization_insufficient_without_signature": true,
    "new_runner_point_of_use_signature_verification": true,
    "new_atomic_capability_consumption_before_provider_io": true
  },
  "interpretation_boundary": "R3 is a control-plane-only authority-provenance repair performed before R2 independent review, scientific authorization, run-root creation, capability consumption, or Bridge scientific provider I/O. It preserves the exact 6×8×K8 / 384-unit SCREEN search/support object and adds an external Ed25519 capability that a host69 write-capable caller cannot self-sign.",
  "authority": {
    "provider_io": false,
    "search_pool_acquisition": false,
    "support_inspection": false,
    "free_updater": false,
    "actor_evaluation": false,
    "validation_opening": false,
    "analysis": false,
    "paper_promotion": false
  },
  "next_gate": "QUALIFY_HOST52_KEYPAIR_MATCH_THEN_FREEZE_R3_EXECUTION_REVIEW_PACKET"
}

```


---
## Host52 external controller keypair qualification
Path: `generated/e2-r17-bridge-v4r2-stage-a-controller-keypair-qualification-20260907.json`
SHA256: `c9a8db49f39174e0508487bda4d161cb7dedf42d1b1813003654a09fb18e4125`

```json
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-bridge-v4r2-stage-a-controller-keypair-qualification",
  "created_at_utc": "2026-09-06T18:28:14Z",
  "status": "PASS_HOST52_EXTERNAL_ED25519_CONTROLLER_KEYPAIR_QUALIFICATION",
  "controller_host": "host52",
  "algorithm": "Ed25519",
  "production_public_key_sha256": "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0",
  "derived_public_key_sha256": "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0",
  "derived_public_equals_stored_public": true,
  "private_key_owner": "root:root",
  "private_key_mode": "600",
  "private_key_root_only": true,
  "public_key_owner": "root:root",
  "public_key_mode": "644",
  "private_key_content_included": false,
  "private_key_path_included": false,
  "provider_calls": 0,
  "scientific_execution": false,
  "interpretation_boundary": "This receipt establishes only that the external host52 root-only Ed25519 controller private key derives the exact production public key pinned by Bridge Stage-A. It grants no scientific authority and contains no private-key material or private-key path."
}

```


---
## Production Ed25519 public key
Path: `generated/e2-r17-bridge-v4r2-stage-a-controller-public-key-20260907.pem`
SHA256: `f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0`

```text
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEA9n5373I7pc5ubACIC2Bva46+2xZDWkrQao47EPbCx4w=
-----END PUBLIC KEY-----

```


---
## Bridge-specific fresh identity
Path: `generated/e2-r17-bridge-v4r2-stage-a-model-identity-20260907.json`
SHA256: `3ffc4cc3589022c3f513919a2c1dab10bfce512299c3004548a593b2a8da114d`

```json
{
  "artifact_type": "e2-r17-bridge-v4r2-stage-a-model-identity-qualification",
  "authority": {
    "actor_evaluation": false,
    "analysis": false,
    "free_updater": false,
    "paper_promotion": false,
    "preexecution_identity_qualification": true,
    "provider_scientific_io": false,
    "scientific_experiment": false,
    "search_pool_acquisition": false,
    "support_inspection": false,
    "validation": false
  },
  "checks": {
    "max_output_tokens_8192": true,
    "provider_retry_zero": true,
    "qualification_call_pass": true,
    "requested_model_exact": true,
    "resolved_model_exact": true,
    "route_is_ark_plan": true,
    "thinking_disabled": true
  },
  "created_at_utc": "2026-09-06T17:49:20+00:00",
  "default_model": "ark-code-latest",
  "drift_policy": "Any resolved-model, route, thinking, retry, or 8192-output compatibility drift is HOLD_REVIEW_REQUIRED; no automatic model substitution or repeated qualification until separately authorized.",
  "max_output_tokens_smoke": 8192,
  "private_credentials_included": false,
  "provider_retry_limit": 0,
  "qualification_call": {
    "benchmark_data_accessed": false,
    "checks": {
      "provider_status_completed": true,
      "resolved_model_exact": true,
      "text_exact": true
    },
    "hidden_provider_retry_used": false,
    "max_output_tokens": 8192,
    "prompt_sha256": "01b804a33c42d8fc0c75e7c2564a140104807322ba83afdf60e4054499374da9",
    "provider_generation_attempts": 1,
    "provider_retry_limit": 0,
    "provider_status": "completed",
    "raw_text": "BRIDGE_V4R2_STAGE_A_IDENTITY_OK",
    "raw_text_sha256": "649711d007044e61e50c097b7d3688da03b33abc3a42e53536beb6a132124836",
    "requested_model": "deepseek-v4-pro",
    "required_resolved_model": "deepseek-v4-pro-ga-260813",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "response_id_sha256": "bf383fd4bca85da89c2f2ac2e471a15ea889029489c21cdf911d2c3189dfd40b",
    "scientific_outcome": false,
    "status": "PASS",
    "temperature": 0,
    "thinking_requested": "disabled",
    "usage": {
      "input_tokens": 47,
      "input_tokens_details": {
        "cached_tokens": 0
      },
      "output_tokens": 13,
      "output_tokens_details": {
        "reasoning_tokens": 0
      },
      "total_tokens": 60
    }
  },
  "raw_response_ids_included": false,
  "requested_and_resolved": {
    "deepseek-v4-pro": {
      "requested": "deepseek-v4-pro",
      "resolved": "deepseek-v4-pro-ga-260813",
      "thinking_requested": "disabled"
    }
  },
  "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
  "schema_version": "1.0",
  "scientific_experiment": false,
  "scientific_tranche": "E2-R17-BRIDGE-V4R2-STAGE-A",
  "status": "PASS_BRIDGE_V4R2_STAGE_A_MODEL_IDENTITY"
}

```


---
## M3R4-to-Bridge eligibility adjudication
Path: `generated/e2-r17-m3r4-to-bridge-v4r2-eligibility-adjudication-20260907.json`
SHA256: `74a82e3398de56d4c7dd81744f7cee9ebfd6e2bfdeb4e7b9c7b96cd29f0465e0`

```json
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-m3r4-to-bridge-v4r2-eligibility-adjudication",
  "date": "2026-09-07",
  "status": "PASS_M3R4_NARROWS_MECHANISM_BUT_DOES_NOT_BLOCK_BRIDGE_V4R2_STAGE_A_ELIGIBILITY",
  "scientific_object": "E2-R17-STATE-COMPILER-BRIDGE-V4R2",
  "m3r4_result": {
    "source_branch": "research/e2-r17-m3r4-atomgit-engineering-20260906",
    "source_commit": "52de43a8",
    "path": "generated/e2-r17-m3r4-analysis-result-r2-20260907.json",
    "sha256": "7243e68343c0aa0e2da9d16c558a7d4f2fc1ccfd8fe68ae9a5726a79b3011c1a",
    "status": "M3R4_OBSERVED_EXCESS_ONLY_NO_PROPENSITY_LOCALIZATION",
    "e_real": 0.05555555555555555,
    "exact_one_sided_p": 0.3333333333333333,
    "bounded_localization_pass": false,
    "automatic_rerun": false,
    "population_generalization": false,
    "variance_component_claim": false
  },
  "frozen_bridge_protocol": {
    "path": "generated/e2-r17-state-compiler-bridge-protocol-v4-r2-20260903.md",
    "sha256": "1bc74c6f98e38535cb3865dcd41fb244b7d17c295db0ee9835937cc1034f9ef7",
    "independent_review_path": "generated/e2-r17-state-compiler-bridge-v4r2-preexecution-rereview-20260904.json",
    "independent_review_verdict": "PASS_PREEXECUTION_DESIGN",
    "frozen_logic": {
      "q1_primary_complete_method": true,
      "q3_realization_localization_secondary_mechanism": true,
      "q3_does_not_gate_q1": true,
      "raw_generator_screen_gate_uses_q1_not_realization_localization": true,
      "q1_pass_q3_fail_policy": "retain complete-method result and remove realization/variance-centered mechanism language"
    }
  },
  "adjudication": {
    "m3r4_propensity_localization_supported": false,
    "m3r4_observed_excess_descriptive_signal_present": true,
    "m3r4_result_rewritten_as_bridge_q3_result": false,
    "bridge_q3_remains_prospective_and_unobserved": true,
    "bridge_q1_stage_a_design_eligibility": true,
    "bridge_stage_a_execution_authority": false,
    "bridge_screen_open": false,
    "bridge_validation_open": false,
    "bridge_protocol_redesign_required": false,
    "additional_m3r4_actor_replicates_allowed": false,
    "second_model_or_task_rescue_allowed": false,
    "realization_variance_centered_claim_before_bridge_q3": false
  },
  "claim_boundary": "M3R4 supplies only a selected-case positive observed excess without exact propensity-localization support. Under the already-reviewed V4-R2 orthogonal decision table, this narrows prior mechanism language but does not veto the independent Q1 complete state-generation method experiment. Bridge Q3 must still be measured prospectively inside the Bridge object and cannot inherit a PASS or FAIL from M3R4.",
  "authority": {
    "provider_io": false,
    "search_pool_acquisition": false,
    "support_inspection": false,
    "free_updater": false,
    "actor_evaluation": false,
    "screen_opening": false,
    "validation_opening": false,
    "analysis": false,
    "e3": false,
    "second_backbone": false,
    "public_benchmark": false,
    "paper_promotion": false,
    "submission": false
  },
  "next_gate": "COMPLETE_ZERO_PROVIDER_BRIDGE_V4R2_STAGE_A_IMPLEMENTATION_BINDINGS_THEN_FREEZE_SEPARATE_STAGE_A_CONTRACT_AND_PREEXECUTION_AUTHORITY"
}

```


---
## Prior V4-R2 independent design rereview
Path: `generated/e2-r17-state-compiler-bridge-v4r2-preexecution-rereview-20260904.json`
SHA256: `fa4f4220ff8761dd675e114f50e2cb2e8b38c51776ccc396326713aa78c30136`

```json
{
  "artifact_type": "e2-r17-state-compiler-bridge-v4r2-independent-preexecution-rereview",
  "schema_version": "1.0",
  "review_date": "2026-09-04",
  "status": "PASS_V4R2_INDEPENDENT_PREEXECUTION_DESIGN",
  "reviewed_object": {
    "commit": "8970cf01df3a9b7bd9224ccbb66085b8acd8c53b",
    "path": "generated/e2-r17-state-compiler-bridge-protocol-v4-r2-20260903.md",
    "sha256": "1bc74c6f98e38535cb3865dcd41fb244b7d17c295db0ee9835937cc1034f9ef7"
  },
  "reviewer": {
    "route": "Oracle Browser / logged-in ChatGPT",
    "server": "52",
    "model": "GPT-5.6 Sol",
    "thinking_effort": "Extra High (4/5; DOM showed GPT-5.6 Sol selected and Extra High 4/5 in the parent rereview conversation)",
    "conversation_id": "6a9a187e-91d8-83ee-b21b-5dfbf3d1a63d",
    "final_session": "e2-r17-v4r2-m3r3-rereview-3",
    "prompt_submitted": true,
    "completed": true,
    "output_log_sha256": "1a47615fe8579ae66b3e50cc8609428dd7c85066608aba181ca9625373b82191",
    "meta_sha256": "c2cb533f6827b41ebf4cab3fe171e48b46cbd58d3f1a1208403ac7fec13b7ecd"
  },
  "review_history_note": "The first long rereview turn in the same conversation completed reasoning but rendered an empty final assistant node. It is not counted as a verdict. A short follow-up in the same conversation requested only the missing final verdict/fixes and returned a complete answer.",
  "verdict": "PASS_PREEXECUTION_DESIGN",
  "verdict_changing_fixes_remaining": [],
  "review_findings": {
    "balanced_generator_factor_estimand_valid": true,
    "q1_q4_authority_orthogonal": true,
    "free_b_sensitivity_only_for_q1": true,
    "universal_state_sha_aliasing_sufficient": true,
    "q2_ff4_only_scope_correct": true,
    "q3_observed_disagreement_bound_correct": true,
    "q3_propensity_interpretation_requires_iid_stationarity_model": true,
    "screen_validation_preserve_estimand": true
  },
  "scientific_execution": false,
  "provider_calls_in_scientific_pipeline": 0,
  "scientific_outcomes_read": false,
  "authority": {
    "bridge_stage_a": false,
    "screen_opening": false,
    "validation_opening": false,
    "e3": false,
    "second_backbone": false,
    "public_benchmark": false,
    "submission": false
  },
  "next_gate": "SEPARATE_STAGE_A_CONTRACT_PREFLIGHT_AND_EXPLICIT_EXECUTION_AUTHORIZATION_ONLY_AFTER_EXISTING_UPSTREAM_ELIGIBILITY_GATES",
  "interpretation_boundary": "This receipt records that the frozen V4-R2 protocol passed independent pre-execution methodology review. It does not itself grant scientific provider execution authority, open SCREEN/VALIDATION, or override Recovery V3 / other upstream eligibility gates."
}

```


---
## Exact R3 capability verifier
Path: `research_pipeline/e2_r17_bridge_v4r2_stage_a_capability.py`
SHA256: `4c2bac59ab85410240d2f8591c6f92a2cf66277b9720285bb30e76c7861d8622`

```python
from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CAPABILITY_ARTIFACT_TYPE = "e2-r17-bridge-v4r2-stage-a-r3-externally-signed-execution-capability"
SIGNATURE_ALGORITHM = "Ed25519"
SIGNATURE_CONTEXT = "E2-R17-BRIDGE-V4R2-STAGE-A-EXECUTION-CAPABILITY-V1"
CONTROL_PLANE_REVISION = "STAGE_A_R3_EXTERNAL_SIGNED_EXECUTION_CAPABILITY"
PRODUCTION_PUBLIC_KEY_RELATIVE = "generated/e2-r17-bridge-v4r2-stage-a-controller-public-key-20260907.pem"
PRODUCTION_PUBLIC_KEY_PATH = ROOT / PRODUCTION_PUBLIC_KEY_RELATIVE
PRODUCTION_PUBLIC_KEY_SHA256 = "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0"
OPENSSL = "/usr/bin/openssl"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_payload_bytes(payload: dict[str, Any]) -> bytes:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return SIGNATURE_CONTEXT.encode("utf-8") + b"\x00" + body


def _openssl(args: list[str]) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run([OPENSSL, *args], capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"OpenSSL command failed ({result.returncode}); stderr={result.stderr.decode(errors='replace')[-1200:]}"
        )
    return result


def _derived_public_key(private_key_path: Path) -> bytes:
    return _openssl(["pkey", "-in", str(private_key_path), "-pubout"]).stdout


def sign_document(*, payload: dict[str, Any], private_key_path: Path, public_key_path: Path) -> dict[str, Any]:
    if not private_key_path.is_file() or not public_key_path.is_file():
        raise RuntimeError("Bridge Stage-A signing key material absent")
    if _derived_public_key(private_key_path) != public_key_path.read_bytes():
        raise RuntimeError("Bridge Stage-A private/public signing key mismatch")
    raw = canonical_payload_bytes(payload)
    with tempfile.TemporaryDirectory(prefix="e2-r17-bridge-stage-a-sign-") as tmp:
        message = Path(tmp) / "message.bin"
        signature = Path(tmp) / "signature.bin"
        message.write_bytes(raw)
        _openssl(["pkeyutl", "-sign", "-rawin", "-inkey", str(private_key_path), "-in", str(message), "-out", str(signature)])
        signature_bytes = signature.read_bytes()
    return {
        "schema_version": "1.0",
        "artifact_type": CAPABILITY_ARTIFACT_TYPE,
        "payload": payload,
        "signature": {
            "algorithm": SIGNATURE_ALGORITHM,
            "context": SIGNATURE_CONTEXT,
            "public_key_sha256": PRODUCTION_PUBLIC_KEY_SHA256,
            "signature_base64": base64.b64encode(signature_bytes).decode("ascii"),
        },
    }


def verify_document(document: dict[str, Any], *, expected_payload_fields: dict[str, Any]) -> dict[str, Any]:
    if document.get("artifact_type") != CAPABILITY_ARTIFACT_TYPE:
        raise RuntimeError("Bridge Stage-A capability artifact type drift")
    payload = document.get("payload")
    signature_row = document.get("signature")
    if not isinstance(payload, dict) or not isinstance(signature_row, dict):
        raise RuntimeError("Bridge Stage-A capability payload/signature absent")
    if not PRODUCTION_PUBLIC_KEY_PATH.is_file():
        raise RuntimeError("Bridge Stage-A production public key absent")
    if sha256_file(PRODUCTION_PUBLIC_KEY_PATH) != PRODUCTION_PUBLIC_KEY_SHA256:
        raise RuntimeError("Bridge Stage-A production public-key SHA drift")
    if signature_row.get("algorithm") != SIGNATURE_ALGORITHM or signature_row.get("context") != SIGNATURE_CONTEXT:
        raise RuntimeError("Bridge Stage-A capability signature metadata drift")
    if signature_row.get("public_key_sha256") != PRODUCTION_PUBLIC_KEY_SHA256:
        raise RuntimeError("Bridge Stage-A capability public-key fingerprint drift")
    try:
        signature = base64.b64decode(str(signature_row.get("signature_base64") or ""), validate=True)
    except Exception as exc:
        raise RuntimeError("Bridge Stage-A capability signature encoding invalid") from exc
    raw = canonical_payload_bytes(payload)
    with tempfile.TemporaryDirectory(prefix="e2-r17-bridge-stage-a-verify-") as tmp:
        message = Path(tmp) / "message.bin"
        signature_path = Path(tmp) / "signature.bin"
        message.write_bytes(raw)
        signature_path.write_bytes(signature)
        result = subprocess.run(
            [
                OPENSSL,
                "pkeyutl",
                "-verify",
                "-rawin",
                "-pubin",
                "-inkey",
                str(PRODUCTION_PUBLIC_KEY_PATH),
                "-in",
                str(message),
                "-sigfile",
                str(signature_path),
            ],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError("Bridge Stage-A capability signature verification failed")
    if payload.get("control_plane_revision") != CONTROL_PLANE_REVISION:
        raise RuntimeError("Bridge Stage-A capability revision drift")
    if payload.get("single_use") is not True:
        raise RuntimeError("Bridge Stage-A capability must be single-use")
    expected_authority = {
        "scientific_experiment": True,
        "provider_io": True,
        "search_pool_acquisition": True,
        "support_inspection": True,
        "free_updater": False,
        "deterministic_state_materialization": False,
        "actor_evaluation": False,
        "screen_outcome_opening": False,
        "validation_opening": False,
        "analysis": False,
        "paper_promotion": False,
    }
    if payload.get("authority") != expected_authority:
        raise RuntimeError("Bridge Stage-A capability authority surface drift")
    if set(payload) != {
        "capability_id",
        "issued_at_utc",
        "control_plane_revision",
        "contract_sha256",
        "preflight_sha256",
        "review_receipt_sha256",
        "structural_authorization_sha256",
        "runner_sha256",
        "runtime_sha256",
        "support_sha256",
        "identity_sha256",
        "run_root",
        "lineage_lease_path",
        "consumption_marker_path",
        "single_use",
        "authority",
    }:
        raise RuntimeError("Bridge Stage-A capability payload field surface drift")
    for key, expected in expected_payload_fields.items():
        if payload.get(key) != expected:
            raise RuntimeError(f"Bridge Stage-A capability binding drift: {key}")
    return payload


__all__ = [
    "CAPABILITY_ARTIFACT_TYPE",
    "SIGNATURE_ALGORITHM",
    "SIGNATURE_CONTEXT",
    "CONTROL_PLANE_REVISION",
    "PRODUCTION_PUBLIC_KEY_RELATIVE",
    "PRODUCTION_PUBLIC_KEY_PATH",
    "PRODUCTION_PUBLIC_KEY_SHA256",
    "canonical_payload_bytes",
    "sha256_file",
    "sign_document",
    "verify_document",
]

```


---
## Exact structural authorization minter
Path: `scripts/authorize_e2_r17_bridge_v4r2_stage_a.py`
SHA256: `3f1778de2254f7a47acde4334f4f81dbf3086b2fc583fb808fa057b33bf5815c`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_bridge_v4r2_stage_a_capability import (
    CONTROL_PLANE_REVISION,
    PRODUCTION_PUBLIC_KEY_SHA256,
)

CONTRACT_STATUS = "FROZEN_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_SUPPORT"
PREFLIGHT_STATUS = "PASS_ZERO_PROVIDER_BRIDGE_V4R2_STAGE_A_CONTRACT_PREFLIGHT"
REVIEW_VERDICT = "PASS_TO_SEPARATE_BRIDGE_V4R2_STAGE_A_AUTHORIZATION"
AUTH_STATUS = "AUTHORIZED_E2_R17_BRIDGE_V4R2_STAGE_A_STRUCTURAL_REQUIRES_SIGNED_CAPABILITY"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_exclusive(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(fd, raw)
        os.fsync(fd)
    finally:
        os.close(fd)


def build_authorization(
    *,
    contract_path: Path,
    preflight_path: Path,
    review_path: Path,
) -> dict[str, Any]:
    contract = load_json(contract_path)
    preflight = load_json(preflight_path)
    review = load_json(review_path)
    contract_sha = sha256_file(contract_path)
    preflight_sha = sha256_file(preflight_path)
    review_sha = sha256_file(review_path)

    require(contract.get("status") == CONTRACT_STATUS, "Bridge Stage-A contract status drift")
    require(not any((contract.get("authority") or {}).values()), "Bridge Stage-A contract must remain zero-authority")
    require(preflight.get("status") == PREFLIGHT_STATUS, "Bridge Stage-A preflight status drift")
    require(preflight.get("contract_sha256") == contract_sha, "Bridge Stage-A preflight/contract SHA drift")
    require(preflight.get("provider_calls") == 0 and preflight.get("provider_claims") == 0, "Bridge Stage-A preflight touched provider")
    require(preflight.get("scientific_outcomes_read") is False and preflight.get("method_effect_read") is False, "Bridge Stage-A preflight outcome boundary drift")
    require(preflight.get("updater_calls") == 0 and preflight.get("heldout_actor_calls") == 0, "Bridge Stage-A preflight stage separation drift")

    require(review.get("status") == "COMPLETED", "Bridge Stage-A independent review receipt incomplete")
    require(review.get("surface") == "ChatGPT web", "Bridge Stage-A independent review surface drift")
    require(review.get("model") == "GPT-5.6 Sol", "Bridge Stage-A independent review model drift")
    require(review.get("verdict") == REVIEW_VERDICT, "Bridge Stage-A independent review did not PASS")
    require(review.get("control_plane_revision") == CONTROL_PLANE_REVISION, "Bridge Stage-A independent review control-plane revision drift")
    require(review.get("contract_sha256_acknowledged") == contract_sha, "Bridge Stage-A review contract acknowledgement drift")
    require(review.get("preflight_sha256_acknowledged") == preflight_sha, "Bridge Stage-A review preflight acknowledgement drift")
    require(review.get("scientific_authority_now") is False, "Bridge Stage-A review improperly grants authority directly")
    require(review.get("stage_a_execution_recommendation") == "ALLOW_SEPARATE_AUTHORIZATION", "Bridge Stage-A review recommendation drift")
    require(list(review.get("remaining_blockers") or []) == [], "Bridge Stage-A review retains blockers")
    for key in (
        "scientific_geometry",
        "stage_separation",
        "support_gate",
        "identity_runtime_budget",
        "exactly_once_fail_closed",
        "causal_integrity",
        "m3r4_dependency",
        "r1_supersession_clean",
        "r2_supersession_clean",
        "authority_provenance",
    ):
        require(review.get(key) == "PASS", f"Bridge Stage-A review field not PASS: {key}")

    run_root = Path(contract["run_root"])
    lease_path = Path(contract["lineage_lease_path"])
    consumption_path = Path(contract["signed_capability_control"]["consumption_marker_path"])
    require(not run_root.exists() and not lease_path.exists(), "Bridge Stage-A run root/lease no longer fresh")
    require(not consumption_path.exists(), "Bridge Stage-A capability already consumed")
    require(contract["signed_capability_control"]["production_public_key_sha256"] == PRODUCTION_PUBLIC_KEY_SHA256, "Bridge Stage-A contract trust-root drift")

    expected_authority = {
        "scientific_experiment": True,
        "provider_io": True,
        "search_pool_acquisition": True,
        "support_inspection": True,
        "free_updater": False,
        "deterministic_state_materialization": False,
        "actor_evaluation": False,
        "screen_outcome_opening": False,
        "validation_opening": False,
        "analysis": False,
        "paper_promotion": False,
    }
    scope = {
        "contract_sha256": contract_sha,
        "allowed_unit_ids": contract["search"]["unit_ids"],
        "allowed_task_ids": contract["search"]["task_ids"],
        "exact_k": 8,
        "required_resolved_model": contract["actor"]["required_resolved_model"],
        "identity_artifact_sha256": contract["model_identity"]["sha256"],
        "required_skill_pre_sha256": contract["initial_skill"]["sha256"],
        "max_turns": contract["actor"]["max_turns"],
        "max_output_tokens": contract["actor"]["max_output_tokens"],
        "automatic_retry": False,
        "run_root": contract["run_root"],
        "lineage_lease_path": contract["lineage_lease_path"],
        "consumption_marker_path": str(consumption_path),
        "provider_budget": {
            "required": True,
            "total_limit": contract["budget"]["search_provider_call_ceiling"],
            "per_unit_limit": contract["budget"]["per_search_unit_call_ceiling"],
        },
    }
    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-bridge-v4r2-stage-a-structural-authorization",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": AUTH_STATUS,
        "single_use": True,
        "control_plane_revision": CONTROL_PLANE_REVISION,
        "contract_path": str(contract_path.resolve()),
        "contract_sha256": contract_sha,
        "preflight_path": str(preflight_path.resolve()),
        "preflight_sha256": preflight_sha,
        "independent_review": {
            "path": str(review_path.resolve()),
            "sha256": review_sha,
            "verdict": REVIEW_VERDICT,
        },
        "authority_requires_external_signed_capability": True,
        "production_public_key_sha256": PRODUCTION_PUBLIC_KEY_SHA256,
        "authority": expected_authority,
        "execution_scope": scope,
        "interpretation_boundary": "This structural authorization is not sufficient authority by itself. Actual Stage-A provider execution additionally requires an externally Ed25519-signed single-use capability from the hard-pinned host52 controller trust root, verified and consumed at runner point of use before provider I/O.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "Bridge Stage-A structural authorization already exists")
    payload = build_authorization(contract_path=args.contract, preflight_path=args.preflight, review_path=args.review)
    atomic_exclusive(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```


---
## Exact host52 capability signer
Path: `scripts/sign_e2_r17_bridge_v4r2_stage_a_capability.py`
SHA256: `b31d2ece1fc3f4001e83ef20b72aaad0f4bcfdd97bb5639af2095d8ae4bf1942`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_bridge_v4r2_stage_a_capability import (
    CONTROL_PLANE_REVISION,
    PRODUCTION_PUBLIC_KEY_PATH,
    PRODUCTION_PUBLIC_KEY_SHA256,
    sha256_file,
    sign_document,
)
from scripts.authorize_e2_r17_bridge_v4r2_stage_a import AUTH_STATUS, REVIEW_VERDICT


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_exclusive(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(fd, raw)
        os.fsync(fd)
    finally:
        os.close(fd)


def build_payload(
    *,
    contract_path: Path,
    preflight_path: Path,
    review_path: Path,
    authorization_path: Path,
    issued_at_utc: str | None = None,
    capability_id: str | None = None,
) -> dict[str, Any]:
    contract = load_json(contract_path)
    preflight = load_json(preflight_path)
    review = load_json(review_path)
    authorization = load_json(authorization_path)
    contract_sha = sha256_file(contract_path)
    preflight_sha = sha256_file(preflight_path)
    review_sha = sha256_file(review_path)
    auth_sha = sha256_file(authorization_path)

    require(authorization.get("status") == AUTH_STATUS, "Bridge Stage-A structural authorization status drift")
    require(authorization.get("control_plane_revision") == CONTROL_PLANE_REVISION, "Bridge Stage-A structural authorization revision drift")
    require(authorization.get("contract_sha256") == contract_sha, "Bridge Stage-A structural authorization contract drift")
    require(authorization.get("preflight_sha256") == preflight_sha, "Bridge Stage-A structural authorization preflight drift")
    require((authorization.get("independent_review") or {}).get("sha256") == review_sha, "Bridge Stage-A structural authorization review drift")
    require((authorization.get("independent_review") or {}).get("verdict") == REVIEW_VERDICT, "Bridge Stage-A structural authorization review verdict drift")
    require(authorization.get("authority_requires_external_signed_capability") is True, "Bridge Stage-A structural authorization does not require signed capability")
    require(authorization.get("production_public_key_sha256") == PRODUCTION_PUBLIC_KEY_SHA256, "Bridge Stage-A structural authorization trust-root drift")
    require(review.get("status") == "COMPLETED" and review.get("verdict") == REVIEW_VERDICT, "Bridge Stage-A accepted review receipt drift")
    require(review.get("control_plane_revision") == CONTROL_PLANE_REVISION, "Bridge Stage-A accepted review revision drift")
    require(review.get("contract_sha256_acknowledged") == contract_sha, "Bridge Stage-A review contract acknowledgement drift")
    require(review.get("preflight_sha256_acknowledged") == preflight_sha, "Bridge Stage-A review preflight acknowledgement drift")
    require(preflight.get("contract_sha256") == contract_sha and preflight.get("provider_calls") == 0, "Bridge Stage-A preflight binding drift")
    require(PRODUCTION_PUBLIC_KEY_PATH.is_file() and sha256_file(PRODUCTION_PUBLIC_KEY_PATH) == PRODUCTION_PUBLIC_KEY_SHA256, "Bridge Stage-A production public key drift")

    scope = authorization["execution_scope"]
    expected_authority = authorization["authority"]
    return {
        "capability_id": capability_id or secrets.token_hex(32),
        "issued_at_utc": issued_at_utc or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "control_plane_revision": CONTROL_PLANE_REVISION,
        "contract_sha256": contract_sha,
        "preflight_sha256": preflight_sha,
        "review_receipt_sha256": review_sha,
        "structural_authorization_sha256": auth_sha,
        "runner_sha256": contract["bound_code"]["runner"]["sha256"],
        "runtime_sha256": contract["bound_code"]["runtime"]["sha256"],
        "support_sha256": contract["bound_code"]["support"]["sha256"],
        "identity_sha256": contract["model_identity"]["sha256"],
        "run_root": scope["run_root"],
        "lineage_lease_path": scope["lineage_lease_path"],
        "consumption_marker_path": scope["consumption_marker_path"],
        "single_use": True,
        "authority": expected_authority,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-key", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "Bridge Stage-A signed capability already exists")
    payload = build_payload(
        contract_path=args.contract,
        preflight_path=args.preflight,
        review_path=args.review,
        authorization_path=args.authorization,
    )
    document = sign_document(
        payload=payload,
        private_key_path=args.private_key,
        public_key_path=PRODUCTION_PUBLIC_KEY_PATH,
    )
    atomic_exclusive(args.output, document)
    print(
        json.dumps(
            {
                "status": "SIGNED_E2_R17_BRIDGE_V4R2_STAGE_A_CAPABILITY",
                "capability_id": payload["capability_id"],
                "public_key_sha256": PRODUCTION_PUBLIC_KEY_SHA256,
                "provider_calls": 0,
                "scientific_execution": False,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```


---
## Exact Stage-A CLI runner
Path: `scripts/run_e2_r17_bridge_v4r2_stage_a.py`
SHA256: `b66b9ddd8b7464e929f2ff3270e937a094f93a5e7f35b9c5da00fd470ca1bc18`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_bridge_v4r2_stage_a_runtime import run_stage_a


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--signed-capability", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--stop-before-provider-io", action="store_true")
    parser.add_argument("--preflight-output", type=Path)
    args = parser.parse_args()
    return asyncio.run(
        run_stage_a(
            root=ROOT,
            contract_path=args.contract,
            auth_path=args.authorization,
            signed_capability_path=args.signed_capability,
            env_file=args.env_file,
            stop_before_provider_io=args.stop_before_provider_io,
            preflight_output=args.preflight_output,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())

```


---
## Exact Stage-A R3 runtime
Path: `research_pipeline/e2_r17_bridge_v4r2_stage_a_runtime.py`
SHA256: `ccc76c67fdc0b03c737e2d333bf7a29a724d7ec26f5c954359d05f8de000fa52`

```python
from __future__ import annotations

import hashlib, json, os, sqlite3, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import ActorRolloutConfig, atomic_json, file_sha256, freeze_nested_pools, run_actor_rollout
from research_pipeline.e2_r17_ark_plan_react import ArkPlanReactLLM, PLAN_BASE_URL
from research_pipeline.e2_r17_bridge_v4r2_execution_plan import SCREEN, search_units, stage_stream_ids, update_tasks
from research_pipeline.e2_r17_bridge_v4r2_stage_a_capability import (
    CONTROL_PLANE_REVISION,
    PRODUCTION_PUBLIC_KEY_SHA256,
    sha256_file as capability_sha256_file,
    verify_document,
)
from research_pipeline.e2_r17_bridge_v4r2_stage_a_support import evaluate_screen_support
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger
from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef
from scripts.run_e2_r17_actor_pool import load_mindmemos
from scripts.run_e2_r17_e1_a_pool_support import validate_runtime

CONTRACT_STATUS="FROZEN_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_SUPPORT"
AUTH_STATUS="AUTHORIZED_E2_R17_BRIDGE_V4R2_STAGE_A_STRUCTURAL_REQUIRES_SIGNED_CAPABILITY"
IDENTITY_STATUS="PASS_BRIDGE_V4R2_STAGE_A_MODEL_IDENTITY"
RUNNING="RUNNING_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH"
FAIL="FAIL_CLOSED_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH"


def sha(path: Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path: Path)->dict[str,Any]:return json.loads(path.read_text(encoding="utf-8"))
def req(v:bool,m:str)->None:
    if not v: raise RuntimeError(m)
def append(path:Path,row:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a",encoding="utf-8") as f:f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n");f.flush();os.fsync(f.fileno())
def rows(path:Path)->list[dict[str,Any]]:return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []


def validate(contract_path:Path,auth_path:Path,capability_path:Path,root:Path)->tuple[dict[str,Any],dict[str,Any],dict[str,Any],str,str,str,dict[str,Path]]:
    c,a=load(contract_path),load(auth_path); cs,ahs=sha(contract_path),sha(auth_path)
    req(c.get("status")==CONTRACT_STATUS,"Stage-A contract drift");req(a.get("status")==AUTH_STATUS,"Stage-A auth drift");req(a.get("contract_sha256")==cs,"Stage-A auth/contract drift");req(a.get("control_plane_revision")==CONTROL_PLANE_REVISION,"Stage-A auth control-plane revision drift");req(a.get("authority_requires_external_signed_capability") is True,"Stage-A structural authorization does not require external signed capability");req(a.get("production_public_key_sha256")==PRODUCTION_PUBLIC_KEY_SHA256,"Stage-A auth production trust-root drift")
    au=a.get("authority") or {}; expected_authority={"scientific_experiment":True,"provider_io":True,"search_pool_acquisition":True,"support_inspection":True,"free_updater":False,"deterministic_state_materialization":False,"actor_evaluation":False,"screen_outcome_opening":False,"validation_opening":False,"analysis":False,"paper_promotion":False};req(au==expected_authority,"Stage-A authorization authority surface drift")
    for label,item in c["bound_code"].items():
        p=root/item["path"];req(p.is_file() and sha(p)==item["sha256"],f"bound code drift:{label}")
    for label,item in (("protocol",c["protocol"]),("m3r4",c["m3r4_eligibility"]),("identity",c["model_identity"])):
        p=root/item["path"];req(p.is_file() and sha(p)==item["sha256"],f"{label} drift")
    review=root/c["protocol"]["review_path"];req(review.is_file() and sha(review)==c["protocol"]["review_sha256"],"protocol review drift")
    ident=load(root/c["model_identity"]["path"]);req(ident.get("status")==IDENTITY_STATUS,"identity status drift"); mr=ident["requested_and_resolved"][c["actor"]["requested_model"]];req(mr["resolved"]==c["actor"]["required_resolved_model"],"resolved model drift");req(ident.get("provider_retry_limit")==0,"identity retry drift")
    suite=Path(c["suite"]["root"])
    for n,key in (("suite_manifest.json","suite_manifest_sha256"),("bridge_split_manifest.json","split_manifest_sha256"),("bridge_metadata.json","metadata_sha256")):req(sha(suite/n)==c["suite"][key],f"suite drift:{n}")
    mind=Path(c["mindmemos"]["root"]);head=subprocess.check_output(["git","-C",str(mind),"rev-parse","HEAD"],text=True).strip();req(head==c["mindmemos"]["commit"],"MindMemOS drift")
    skill=Path(c["initial_skill"]["path"]);req(skill.is_file() and sha(skill)==c["initial_skill"]["sha256"],"initial skill drift")
    expected=[u.unit_id for u in search_units(SCREEN)];req(c["search"]["unit_ids"]==expected and len(expected)==384,"search order drift")
    scope=a.get("execution_scope") or {};required_scope_keys={"contract_sha256","allowed_unit_ids","allowed_task_ids","exact_k","required_resolved_model","identity_artifact_sha256","required_skill_pre_sha256","max_turns","max_output_tokens","automatic_retry","run_root","lineage_lease_path","consumption_marker_path","provider_budget"};req(set(scope)==required_scope_keys,"Stage-A authorization execution-scope surface drift");req(a.get("single_use") is True,"Stage-A authorization must be single-use");req(scope.get("allowed_unit_ids")==expected,"auth unit scope drift");req(scope.get("allowed_task_ids")==c["search"]["task_ids"],"auth task scope drift");req(scope.get("contract_sha256")==cs,"scope contract drift");req(int(scope.get("exact_k",-1))==8,"auth K drift");req(scope.get("required_resolved_model")==c["actor"]["required_resolved_model"],"auth resolved-model drift");req(scope.get("identity_artifact_sha256")==c["model_identity"]["sha256"],"auth identity drift");req(scope.get("required_skill_pre_sha256")==c["initial_skill"]["sha256"],"auth initial-skill drift");req(int(scope.get("max_turns",-1))==c["actor"]["max_turns"],"auth max-turns drift");req(int(scope.get("max_output_tokens",-1))==c["actor"]["max_output_tokens"],"auth output-token drift");req(scope.get("automatic_retry") is False,"auth retry policy drift");req(scope.get("run_root")==c["run_root"] and scope.get("lineage_lease_path")==c["lineage_lease_path"],"auth lineage path drift");req(scope.get("consumption_marker_path")==c["signed_capability_control"]["consumption_marker_path"],"auth consumption-marker path drift")
    pb=scope.get("provider_budget") or {};req(pb.get("required") is True,"auth provider budget missing");req(int(pb.get("total_limit",-1))==c["budget"]["search_provider_call_ceiling"],"auth total budget drift");req(int(pb.get("per_unit_limit",-1))==c["budget"]["per_search_unit_call_ceiling"],"auth per-unit budget drift")
    capdoc=load(capability_path); expected_cap={"contract_sha256":cs,"preflight_sha256":a["preflight_sha256"],"review_receipt_sha256":a["independent_review"]["sha256"],"structural_authorization_sha256":ahs,"runner_sha256":c["bound_code"]["runner"]["sha256"],"runtime_sha256":c["bound_code"]["runtime"]["sha256"],"support_sha256":c["bound_code"]["support"]["sha256"],"identity_sha256":c["model_identity"]["sha256"],"run_root":c["run_root"],"lineage_lease_path":c["lineage_lease_path"],"consumption_marker_path":c["signed_capability_control"]["consumption_marker_path"]};cap=verify_document(capdoc,expected_payload_fields=expected_cap);caps=capability_sha256_file(capability_path)
    return c,a,cap,cs,ahs,caps,{"suite":suite,"mind":mind,"identity":root/c["model_identity"]["path"],"skill":skill}


def claim_count(path:Path)->int:
    if not path.exists():return 0
    db=sqlite3.connect(f"file:{path}?mode=ro",uri=True)
    try:return int(db.execute("select count(*) from claims").fetchone()[0])
    finally:db.close()


def consume_capability(*,marker_path:Path,capability_sha256:str,capability_id:str,contract_sha256:str,authorization_sha256:str)->None:
    marker_path.parent.mkdir(parents=True,exist_ok=True)
    payload={"schema_version":"1.0","artifact_type":"e2-r17-bridge-v4r2-stage-a-capability-consumption","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"capability_sha256":capability_sha256,"capability_id":capability_id,"contract_sha256":contract_sha256,"authorization_sha256":authorization_sha256,"consumed_before_provider_io":True}
    raw=(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode("utf-8")
    fd=os.open(marker_path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try:os.write(fd,raw);os.fsync(fd)
    finally:os.close(fd)


async def run_stage_a(*,root:Path,contract_path:Path,auth_path:Path,signed_capability_path:Path,env_file:Path,stop_before_provider_io:bool=False,preflight_output:Path|None=None)->int:
    c,a,cap,cs,ahs,caps,s=validate(contract_path,auth_path,signed_capability_path,root); runtime_python,_=validate_runtime({"runtime":c["runtime"]});req(Path(sys.executable).resolve()==runtime_python.resolve(),"Stage-A runner must execute under the exact frozen actor runtime Python")
    req(env_file.resolve()==Path(c["env_file"]).resolve(),"Stage-A env-file path drift");load_env_file(env_file); src=ArkSettings.from_env(required=True);req(src.base_url.rstrip("/")==PLAN_BASE_URL,"non-Ark Plan route")
    settings=ArkSettings(api_key=src.api_key,base_url=src.base_url,default_model=src.default_model,timeout_seconds=300,max_retries=0)
    if stop_before_provider_io:
        req(preflight_output is not None and not preflight_output.exists(),"preflight output not fresh")
        out={"schema_version":"1.0","artifact_type":"e2-r17-bridge-v4r2-stage-a-actual-path-preflight","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":"PASS_BRIDGE_V4R2_STAGE_A_ACTUAL_PATH_STOPPED_BEFORE_PROVIDER_IO","contract_sha256":cs,"authorization_sha256":ahs,"signed_capability_sha256":caps,"capability_id":cap["capability_id"],"capability_verified":True,"capability_consumed":False,"search_units":384,"streams":6,"tasks":48,"search_k":8,"provider_calls":0,"provider_claims":0,"support_inspected":False,"updater_calls":0,"heldout_actor_calls":0,"validation_open":False,"next_gate":"EXECUTE_EXACT_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_SEQUENCE"};atomic_json(preflight_output,out);print(json.dumps(out,indent=2,sort_keys=True));return 0
    rr=Path(c["run_root"]);leasep=Path(c["lineage_lease_path"]);markerp=Path(c["signed_capability_control"]["consumption_marker_path"]);req(not rr.exists() and not leasep.exists() and not markerp.exists(),"Stage-A root/lease/capability marker not fresh");consume_capability(marker_path=markerp,capability_sha256=caps,capability_id=str(cap["capability_id"]),contract_sha256=cs,authorization_sha256=ahs);rr.mkdir(parents=True)
    lease={"schema_version":"1.0","artifact_type":"e2-r17-bridge-v4r2-stage-a-lineage-lease","status":RUNNING,"created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"contract_sha256":cs,"authorization_sha256":ahs,"signed_capability_sha256":caps,"capability_id":cap["capability_id"],"capability_consumption_marker_path":str(markerp),"capability_consumption_marker_sha256":sha(markerp),"exactly_once":True,"completed_search_units":0,"support_inspected":False,"updater_calls":0,"heldout_actor_calls":0};atomic_json(leasep,lease)
    budgetp=rr/"provider_budget.sqlite3";budget=ProviderBudgetLedger(path=budgetp,contract_sha256=cs,authorization_sha256=ahs,total_limit=c["budget"]["search_provider_call_ceiling"],per_unit_limit=c["budget"]["per_search_unit_call_ceiling"],allow_create=True)
    manifest=rr/"completed_search_units.jsonl";ReactAgentFactory,SpreadsheetBenchEnv=load_mindmemos(s["mind"]);meta={str(x["id"]):x for x in load(s["suite"]/"bridge_metadata.json")};evsrc=[s["mind"]/"src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/evaluator.py",s["mind"]/"src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py"]
    units=search_units(SCREEN);initial_dir=s["skill"].parent
    try:
        for seq,u in enumerate(units):
            ur=rr/"units"/f"{seq:03d}_{u.stream_id}_{u.task_id}_k{u.candidate_index}";req(not ur.exists(),f"preexisting unit:{u.unit_id}");env=SpreadsheetBenchEnv(s["suite"],ur);case={x.id:x for x in env.load_cases("all")}[u.task_id]
            adapter=ArkPlanReactLLM(settings=settings,requested_model=c["actor"]["requested_model"],required_resolved_model=c["actor"]["required_resolved_model"],max_output_tokens=c["actor"]["max_output_tokens"],temperature=0,thinking="disabled",provider_budget_ledger=budget,provider_budget_unit_id=u.unit_id)
            factory=ReactAgentFactory(adapter,max_turns=c["actor"]["max_turns"],skill_sources=[initial_dir],python_path=str(runtime_python));cfg=ActorRolloutConfig(requested_model=c["actor"]["requested_model"],required_resolved_model=c["actor"]["required_resolved_model"],max_turns=c["actor"]["max_turns"],skill_source=str(initial_dir),skill_pre_sha256=c["initial_skill"]["sha256"],failure_family=str(meta[u.task_id].get("primary_failure_family") or ""),experiment_mode="bridge_v4r2_stage_a_search",contract_sha256=cs,authorization_sha256=ahs)
            ref=await run_actor_rollout(env=env,case=case,rollout_index=u.candidate_index-1,agent_factory=factory,adapter=adapter,config=cfg,evaluator_sources=evsrc);refp=Path(ref.trajectory_path).with_name("r17_trajectory_ref.json")
            append(manifest,{"sequence":seq,"unit_id":u.unit_id,"stream_id":u.stream_id,"task_id":u.task_id,"candidate_index":u.candidate_index,"trajectory_ref_path":str(refp),"trajectory_ref_sha256":file_sha256(refp),"provider_claim_count":ref.provider_budget_claim_count});lease["completed_search_units"]=seq+1;atomic_json(leasep,lease)
        done=rows(manifest);req(len(done)==384 and [x["unit_id"] for x in done]==[u.unit_id for u in units],"completed search order drift")
        bytask:dict[str,list[TrajectoryRef]]={}
        for x in done:
            rp=Path(x["trajectory_ref_path"]);req(rp.is_file() and file_sha256(rp)==x["trajectory_ref_sha256"],"trajectory ref drift");ref=TrajectoryRef(**load(rp));ref.validate();tp=Path(ref.trajectory_path);req(tp.is_file() and file_sha256(tp)==ref.trajectory_sha256,"trajectory drift");bytask.setdefault(x["task_id"],[]).append(ref)
        bystream:dict[str,tuple[SearchPool,...]]={};pm=[]
        for sid in stage_stream_ids(SCREEN):
            ps=[]
            for tid in update_tasks(sid):
                rs=sorted(bytask[tid],key=lambda r:r.rollout_index);req(len(rs)==8 and [r.rollout_index for r in rs]==list(range(8)),f"rollout geometry:{tid}");pr=rr/"sealed_pools"/sid/tid;pool=freeze_nested_pools(task_dir=pr,trajectories=rs,prefix_ks=(8,))[8];ps.append(pool);pp=pr/"pool_k8.json";pm.append({"stream_id":sid,"task_id":tid,"pool_id":pool.pool_id,"pool_path":str(pp),"pool_sha256":file_sha256(pp),"mixed_pool":pool.mixed_pool})
            bystream[sid]=tuple(ps)
        support=evaluate_screen_support(bystream);status="PASS_BRIDGE_V4R2_STAGE_A_SCREEN_SUPPORT" if support.all_streams_qualified else "HOLD_BRIDGE_V4R2_STAGE_A_INSUFFICIENT_MIXED_SUPPORT"
        sr={"schema_version":"1.0","artifact_type":"e2-r17-bridge-v4r2-stage-a-screen-support","created_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"status":status,"contract_sha256":cs,"authorization_sha256":ahs,"signed_capability_sha256":caps,"capability_consumption_marker_sha256":sha(markerp),"search_units":384,"streams":6,"tasks":48,"pool_manifest":pm,"support":support.to_dict(),"provider_budget":budget.snapshot().to_dict(),"support_inspected":True,"updater_calls":0,"deterministic_state_materializations":0,"heldout_actor_calls":0,"screen_outcomes_opened":False,"validation_open":False,"replacement_allowed":False,"next_gate":"SEPARATE_BRIDGE_V4R2_SCREEN_STATE_GENERATION_CONTRACT" if support.all_streams_qualified else "HOLD_BRIDGE_V4R2_NO_REPLACEMENT_NO_STATE_GENERATION"};sp=rr/"stage_a_support.json";atomic_json(sp,sr)
        lease.update({"status":"COMPLETED_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SUPPORT_PASS" if support.all_streams_qualified else "COMPLETED_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SUPPORT_HOLD","sealed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"completed_search_units":384,"support_inspected":True,"support_status":status,"support_receipt_path":str(sp),"support_receipt_sha256":sha(sp)});atomic_json(leasep,lease)
        final={"schema_version":"1.0","artifact_type":"e2-r17-bridge-v4r2-stage-a-run-summary","status":"COMPLETED_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_PENDING_SEPARATE_SUPPORT_DECISION","contract_sha256":cs,"authorization_sha256":ahs,"signed_capability_sha256":caps,"capability_consumption_marker_sha256":sha(markerp),"completed_search_units":384,"support_status":status,"support_receipt_path":str(sp),"support_receipt_sha256":sha(sp),"provider_budget":budget.snapshot().to_dict(),"scientific_method_effect_read":False,"updater_calls":0,"heldout_actor_calls":0,"validation_open":False};atomic_json(rr/"run_summary.json",final);print(json.dumps(final,indent=2,sort_keys=True));return 0
    except Exception as e:
        lease.update({"status":FAIL,"failed_at_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"error_type":type(e).__name__,"error":str(e)[:1600],"automatic_retry_authorized":False,"support_inspected":False,"updater_calls":0,"heldout_actor_calls":0});atomic_json(leasep,lease);raise

```


---
## Exact Stage-A support evaluator
Path: `research_pipeline/e2_r17_bridge_v4r2_stage_a_support.py`
SHA256: `c4df9611c7c1f8b95636532bb5fdc16dea4195b8a11c03c974b38d457564f149`

```python
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping, Sequence

from research_pipeline.e2_r17_bridge_v4r2_execution_plan import SCREEN, stage_stream_ids, update_tasks
from research_pipeline.e2_r17_search_projection_runner import SearchPool

MIXED_PER_STREAM_MINIMUM = 4


@dataclass(frozen=True)
class StreamSupport:
    stream_id: str
    pool_count: int
    mixed_pool_count: int
    qualifies: bool


@dataclass(frozen=True)
class ScreenSupportResult:
    stage: str
    streams: tuple[StreamSupport, ...]
    all_streams_qualified: bool
    required_mixed_pools_per_stream: int
    replacement_allowed: bool

    def to_dict(self) -> dict:
        return {
            "stage": self.stage,
            "streams": [asdict(row) for row in self.streams],
            "all_streams_qualified": self.all_streams_qualified,
            "required_mixed_pools_per_stream": self.required_mixed_pools_per_stream,
            "replacement_allowed": self.replacement_allowed,
        }


def evaluate_screen_support(
    pools_by_stream: Mapping[str, Sequence[SearchPool]],
) -> ScreenSupportResult:
    expected_streams = stage_stream_ids(SCREEN)
    if tuple(pools_by_stream) != expected_streams:
        raise ValueError("Bridge SCREEN support stream identity/order drift")
    rows: list[StreamSupport] = []
    for stream_id in expected_streams:
        pools = tuple(pools_by_stream[stream_id])
        expected_tasks = update_tasks(stream_id)
        if len(pools) != 8:
            raise ValueError(f"Bridge SCREEN support requires eight pools: {stream_id}")
        if tuple(pool.task_id for pool in pools) != expected_tasks:
            raise ValueError(f"Bridge SCREEN support task order drift: {stream_id}")
        for pool in pools:
            pool.validate()
            if pool.k != 8:
                raise ValueError(f"Bridge SCREEN support requires K=8: {stream_id}/{pool.task_id}")
        mixed = sum(int(pool.mixed_pool) for pool in pools)
        rows.append(
            StreamSupport(
                stream_id=stream_id,
                pool_count=8,
                mixed_pool_count=mixed,
                qualifies=mixed >= MIXED_PER_STREAM_MINIMUM,
            )
        )
    return ScreenSupportResult(
        stage=SCREEN,
        streams=tuple(rows),
        all_streams_qualified=all(row.qualifies for row in rows),
        required_mixed_pools_per_stream=MIXED_PER_STREAM_MINIMUM,
        replacement_allowed=False,
    )


__all__ = [
    "MIXED_PER_STREAM_MINIMUM",
    "StreamSupport",
    "ScreenSupportResult",
    "evaluate_screen_support",
]

```


---
## Exact frozen Bridge V4-R2 execution-plan source
Path: `research_pipeline/e2_r17_bridge_v4r2_execution_plan.py`
SHA256: `d048f0c27c040cb84f7ca157579ed8b099b8b93b0df111a59bf7ee59a0364709`

```python
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
SUITE_ROOT = Path("/data/wyt/e2-r17-search-projection/state-compiler-bridge-suite-v1-20260903")
SPLIT_PATH = SUITE_ROOT / "bridge_split_manifest.json"
SUITE_MANIFEST_PATH = SUITE_ROOT / "suite_manifest.json"
METADATA_PATH = SUITE_ROOT / "bridge_metadata.json"
PROTOCOL_PATH = ROOT / "generated/e2-r17-state-compiler-bridge-protocol-v4-r2-20260903.md"
REVIEW_PATH = ROOT / "generated/e2-r17-state-compiler-bridge-v4r2-preexecution-rereview-20260904.json"
SUITE_QUALIFICATION_PATH = ROOT / "generated/e2-r17-state-compiler-bridge-suite-qualification-20260903.json"

REQUESTED_MODEL = "deepseek-v4-pro"
REQUIRED_RESOLVED_MODEL = "deepseek-v4-pro-ga-260813"
PLAN_ROUTE = "https://ark.cn-beijing.volces.com/api/plan/v3"
MAX_TURNS = 10
MAX_OUTPUT_TOKENS = 8192
SEARCH_K = 8
HELDOUT_K = 1
PROVIDER_RETRY_LIMIT = 0
UPDATER_MAX_PROVIDER_CALLS = 11
ORDER_SALT = "E2-R17-BRIDGE-V4R2-EXECUTION-ORDER-v1"

SCREEN = "SCREEN"
VALIDATION = "VALIDATION"
STAGES = (SCREEN, VALIDATION)

SCREEN_ARMS = (
    "W_FREE",
    "W_COMP",
    "FF4_FREE_A",
    "FF4_COMP",
    "SCORE_ONLY_GENERIC_MAX",
    "SCOPE_MATCHED_GENERIC_MAX",
)
VALIDATION_ARMS = (
    "W_FREE",
    "W_COMP",
    "FF4_FREE_A",
    "FF4_FREE_B",
    "FF4_COMP",
    "SCORE_ONLY_GENERIC_MAX",
    "SCOPE_MATCHED_GENERIC_MAX",
)
FREE_STATE_ARMS = {
    SCREEN: ("W_FREE", "FF4_FREE_A"),
    VALIDATION: ("W_FREE", "FF4_FREE_A", "FF4_FREE_B"),
}
DETERMINISTIC_STATE_ARMS = {
    SCREEN: ("W_COMP", "FF4_COMP", "SCORE_ONLY_GENERIC_MAX", "SCOPE_MATCHED_GENERIC_MAX"),
    VALIDATION: ("W_COMP", "FF4_COMP", "SCORE_ONLY_GENERIC_MAX", "SCOPE_MATCHED_GENERIC_MAX"),
}
VALIDATION_REPLICATE2_ARMS = ("FF4_FREE_A", "FF4_FREE_B", "FF4_COMP")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _family_from_stream(stream_id: str) -> str:
    parts = stream_id.split("-")
    if len(parts) != 3 or parts[0] != "bridge":
        raise ValueError(f"invalid bridge stream id: {stream_id}")
    return parts[1]


def _family_from_task(task_id: str) -> str:
    parts = task_id.split("-")
    if len(parts) < 4 or parts[0] != "r17":
        raise ValueError(f"invalid bridge task id: {task_id}")
    return parts[2]


def _rank_key(kind: str, unit_id: str) -> str:
    return hashlib.sha256(f"{ORDER_SALT}|{kind}|{unit_id}".encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SearchUnit:
    stage: str
    stream_id: str
    task_id: str
    candidate_index: int
    unit_id: str
    max_provider_calls: int = MAX_TURNS


@dataclass(frozen=True)
class StateUnit:
    stage: str
    stream_id: str
    arm: str
    provider_required: bool
    unit_id: str
    max_provider_calls: int


@dataclass(frozen=True)
class ActorUnit:
    stage: str
    stream_id: str
    task_id: str
    arm: str
    actor_replicate: int
    unit_id: str
    exact_k: int = HELDOUT_K
    max_provider_calls: int = MAX_TURNS


def split_manifest() -> dict[str, Any]:
    return load_json(SPLIT_PATH)


def stage_stream_ids(stage: str) -> tuple[str, ...]:
    split = split_manifest()
    key = "screen_stream_ids" if stage == SCREEN else "validation_stream_ids" if stage == VALIDATION else None
    if key is None:
        raise ValueError(f"invalid stage: {stage}")
    return tuple(split[key])


def update_tasks(stream_id: str) -> tuple[str, ...]:
    rows = split_manifest()["update_streams"][stream_id]
    if len(rows) != 8 or len(set(rows)) != 8:
        raise RuntimeError(f"bridge update stream cardinality drift: {stream_id}")
    return tuple(rows)


def stage_heldout(stage: str) -> tuple[str, ...]:
    split = split_manifest()
    key = "screen_heldout" if stage == SCREEN else "validation_heldout" if stage == VALIDATION else None
    if key is None:
        raise ValueError(f"invalid stage: {stage}")
    return tuple(split[key])


def heldout_for_stream(stage: str, stream_id: str) -> tuple[str, ...]:
    family = _family_from_stream(stream_id)
    rows = tuple(task for task in stage_heldout(stage) if _family_from_task(task) == family)
    if len(rows) != 2:
        raise RuntimeError(f"bridge heldout family cardinality drift: {stage}/{stream_id}: {rows}")
    return rows


def search_units(stage: str) -> tuple[SearchUnit, ...]:
    units: list[SearchUnit] = []
    for stream_id in stage_stream_ids(stage):
        for task_id in update_tasks(stream_id):
            for candidate_index in range(1, SEARCH_K + 1):
                unit_id = f"{stage}/search/{stream_id}/{task_id}/k{candidate_index}"
                units.append(SearchUnit(stage, stream_id, task_id, candidate_index, unit_id))
    units.sort(key=lambda row: _rank_key("search", row.unit_id))
    return tuple(units)


def state_units(stage: str) -> tuple[StateUnit, ...]:
    units: list[StateUnit] = []
    for stream_id in stage_stream_ids(stage):
        for arm in FREE_STATE_ARMS[stage]:
            unit_id = f"{stage}/state/{stream_id}/{arm}"
            units.append(StateUnit(stage, stream_id, arm, True, unit_id, UPDATER_MAX_PROVIDER_CALLS))
        for arm in DETERMINISTIC_STATE_ARMS[stage]:
            unit_id = f"{stage}/state/{stream_id}/{arm}"
            units.append(StateUnit(stage, stream_id, arm, False, unit_id, 0))
    units.sort(key=lambda row: _rank_key("state", row.unit_id))
    return tuple(units)


def actor_units(stage: str) -> tuple[ActorUnit, ...]:
    arms = SCREEN_ARMS if stage == SCREEN else VALIDATION_ARMS if stage == VALIDATION else None
    if arms is None:
        raise ValueError(f"invalid stage: {stage}")
    units: list[ActorUnit] = []
    for stream_id in stage_stream_ids(stage):
        for task_id in heldout_for_stream(stage, stream_id):
            for arm in arms:
                unit_id = f"{stage}/actor/{stream_id}/{task_id}/{arm}/rep1"
                units.append(ActorUnit(stage, stream_id, task_id, arm, 1, unit_id))
            if stage == VALIDATION:
                for arm in VALIDATION_REPLICATE2_ARMS:
                    unit_id = f"{stage}/actor/{stream_id}/{task_id}/{arm}/rep2"
                    units.append(ActorUnit(stage, stream_id, task_id, arm, 2, unit_id))
    units.sort(key=lambda row: _rank_key("actor", row.unit_id))
    return tuple(units)


def stage_budget(stage: str) -> dict[str, int | bool | str]:
    searches = search_units(stage)
    states = state_units(stage)
    actors = actor_units(stage)
    search_calls = sum(row.max_provider_calls for row in searches)
    updater_calls = sum(row.max_provider_calls for row in states)
    actor_calls = sum(row.max_provider_calls for row in actors)
    actor_rep1_calls = sum(row.max_provider_calls for row in actors if row.actor_replicate == 1)
    actor_rep2_calls = sum(row.max_provider_calls for row in actors if row.actor_replicate == 2)
    return {
        "stage": stage,
        "search_rollout_units": len(searches),
        "search_k": SEARCH_K,
        "free_state_units": sum(row.provider_required for row in states),
        "deterministic_state_units": sum(not row.provider_required for row in states),
        "actor_logical_units_pre_alias": len(actors),
        "heldout_k": HELDOUT_K,
        "search_hard_max_provider_calls": search_calls,
        "free_updater_hard_max_provider_calls": updater_calls,
        "deterministic_compiler_provider_calls": 0,
        "heldout_actor_rep1_hard_max_provider_calls_pre_alias": actor_rep1_calls,
        "heldout_actor_rep2_hard_max_provider_calls_pre_alias": actor_rep2_calls,
        "heldout_actor_hard_max_provider_calls_pre_alias": actor_calls,
        "stage_hard_max_provider_calls_pre_alias": search_calls + updater_calls + actor_calls,
        "all_call_counts_are_structural_pre_alias_ceilings_not_expected_spend": True,
        "aliasing_can_only_reduce_actor_calls": True,
        "removed_alias_calls_reallocatable": False,
    }


def full_plan_payload() -> dict[str, Any]:
    split = split_manifest()
    suite = load_json(SUITE_MANIFEST_PATH)
    qualification = load_json(SUITE_QUALIFICATION_PATH)
    review = load_json(REVIEW_PATH)
    payload = {
        "schema_version": "1.0",
        "scientific_object": "E2-R17-STATE-COMPILER-BRIDGE-V4R2",
        "status": "ZERO_PROVIDER_EXECUTION_PLAN_ONLY",
        "order_salt": ORDER_SALT,
        "provider": {
            "route": PLAN_ROUTE,
            "requested_model": REQUESTED_MODEL,
            "required_resolved_model": REQUIRED_RESOLVED_MODEL,
            "thinking": "disabled",
            "temperature": 0,
            "provider_retry_limit": PROVIDER_RETRY_LIMIT,
            "max_turns": MAX_TURNS,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "search_k": SEARCH_K,
            "heldout_k": HELDOUT_K,
            "updater_max_provider_calls_per_state": UPDATER_MAX_PROVIDER_CALLS,
        },
        "bindings": {
            "protocol_path": str(PROTOCOL_PATH.relative_to(ROOT)),
            "protocol_sha256": sha256_file(PROTOCOL_PATH),
            "review_path": str(REVIEW_PATH.relative_to(ROOT)),
            "review_sha256": sha256_file(REVIEW_PATH),
            "suite_qualification_path": str(SUITE_QUALIFICATION_PATH.relative_to(ROOT)),
            "suite_qualification_sha256": sha256_file(SUITE_QUALIFICATION_PATH),
            "suite_root": str(SUITE_ROOT),
            "suite_manifest_sha256": sha256_file(SUITE_MANIFEST_PATH),
            "split_manifest_sha256": sha256_file(SPLIT_PATH),
            "metadata_sha256": sha256_file(METADATA_PATH),
        },
        "stage_rule": {
            "screen_executes_first": True,
            "validation_provider_io_before_raw_screen_pass": False,
            "validation_order_prefrozen_before_screen_outcomes": True,
            "screen_stream_ids": list(stage_stream_ids(SCREEN)),
            "validation_stream_ids": list(stage_stream_ids(VALIDATION)),
            "screen_heldout": list(stage_heldout(SCREEN)),
            "validation_heldout": list(stage_heldout(VALIDATION)),
        },
        "stages": {},
        "authority": {
            "provider_io": False,
            "search_pool_acquisition": False,
            "updater_execution": False,
            "actor_evaluation": False,
            "screen_opening": False,
            "validation_opening": False,
            "analysis": False,
            "e3": False,
            "public_benchmark": False,
            "second_backbone": False,
            "paper_promotion": False,
            "submission": False,
        },
        "scientific_outcomes_read": False,
    }
    for stage in STAGES:
        payload["stages"][stage] = {
            "stream_ids": list(stage_stream_ids(stage)),
            "update_tasks": {s: list(update_tasks(s)) for s in stage_stream_ids(stage)},
            "heldout_by_stream": {s: list(heldout_for_stream(stage, s)) for s in stage_stream_ids(stage)},
            "search_units": [asdict(row) for row in search_units(stage)],
            "state_units": [asdict(row) for row in state_units(stage)],
            "actor_units_pre_alias": [asdict(row) for row in actor_units(stage)],
            "budget": stage_budget(stage),
        }
    payload["sanity"] = {
        "suite_formal_tasks": suite["formal_task_count"],
        "split_outcome_blind": split["selection_is_outcome_blind"],
        "suite_qualification_status": qualification["status"],
        "independent_review_verdict": review["verdict"],
    }
    return payload


def canonical_sha256(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_plan() -> dict[str, Any]:
    payload = full_plan_payload()
    if payload["sanity"]["suite_formal_tasks"] != 120:
        raise RuntimeError("bridge formal task count drift")
    if payload["sanity"]["split_outcome_blind"] is not True:
        raise RuntimeError("bridge split no longer outcome-blind")
    if payload["sanity"]["suite_qualification_status"] != "PASS_ZERO_PROVIDER_FRESH_BRIDGE_SUITE_QUALIFICATION":
        raise RuntimeError("bridge suite qualification drift")
    if payload["sanity"]["independent_review_verdict"] != "PASS_PREEXECUTION_DESIGN":
        raise RuntimeError("bridge independent review verdict drift")
    if len(search_units(SCREEN)) != 384 or len(search_units(VALIDATION)) != 384:
        raise RuntimeError("bridge K=8 search cardinality drift")
    if len(state_units(SCREEN)) != 36 or len(state_units(VALIDATION)) != 42:
        raise RuntimeError("bridge state cardinality drift")
    if len(actor_units(SCREEN)) != 72 or len(actor_units(VALIDATION)) != 120:
        raise RuntimeError("bridge actor schedule cardinality drift")
    if stage_budget(SCREEN)["stage_hard_max_provider_calls_pre_alias"] != 4692:
        raise RuntimeError("bridge SCREEN budget derivation drift")
    if stage_budget(SCREEN)["heldout_actor_rep1_hard_max_provider_calls_pre_alias"] != 720:
        raise RuntimeError("bridge SCREEN heldout K=1/rep1 budget drift")
    if stage_budget(SCREEN)["heldout_actor_rep2_hard_max_provider_calls_pre_alias"] != 0:
        raise RuntimeError("bridge SCREEN must not have actor replicate2")
    if stage_budget(VALIDATION)["stage_hard_max_provider_calls_pre_alias"] != 5238:
        raise RuntimeError("bridge VALIDATION budget derivation drift")
    if stage_budget(VALIDATION)["heldout_actor_rep1_hard_max_provider_calls_pre_alias"] != 840:
        raise RuntimeError("bridge VALIDATION rep1 budget drift")
    if stage_budget(VALIDATION)["heldout_actor_rep2_hard_max_provider_calls_pre_alias"] != 360:
        raise RuntimeError("bridge VALIDATION Q3 rep2 budget drift")
    if set(stage_stream_ids(SCREEN)) & set(stage_stream_ids(VALIDATION)):
        raise RuntimeError("bridge stream stage overlap")
    if set(stage_heldout(SCREEN)) & set(stage_heldout(VALIDATION)):
        raise RuntimeError("bridge heldout stage overlap")
    return payload


__all__ = [
    "SCREEN", "VALIDATION", "STAGES", "SCREEN_ARMS", "VALIDATION_ARMS",
    "FREE_STATE_ARMS", "DETERMINISTIC_STATE_ARMS", "VALIDATION_REPLICATE2_ARMS",
    "SearchUnit", "StateUnit", "ActorUnit", "search_units", "state_units", "actor_units",
    "stage_stream_ids", "update_tasks", "stage_heldout", "heldout_for_stream", "stage_budget",
    "full_plan_payload", "canonical_sha256", "validate_plan", "sha256_file",
]

```


---
## R3 capability adversarial tests
Path: `research_pipeline/test_e2_r17_bridge_v4r2_stage_a_capability.py`
SHA256: `ce174f3a3e7872ebb232ff1d0bb7394f248d2072fa33aed3c9f75e4ccd79e501`

```python
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from research_pipeline.e2_r17_bridge_v4r2_stage_a_capability import (
    CONTROL_PLANE_REVISION,
    PRODUCTION_PUBLIC_KEY_PATH,
    PRODUCTION_PUBLIC_KEY_SHA256,
    SIGNATURE_CONTEXT,
    sha256_file,
    sign_document,
    verify_document,
)
from research_pipeline.e2_r17_bridge_v4r2_stage_a_runtime import consume_capability

ROOT = Path(__file__).resolve().parents[1]


def exact_authority() -> dict[str, bool]:
    return {
        "scientific_experiment": True,
        "provider_io": True,
        "search_pool_acquisition": True,
        "support_inspection": True,
        "free_updater": False,
        "deterministic_state_materialization": False,
        "actor_evaluation": False,
        "screen_outcome_opening": False,
        "validation_opening": False,
        "analysis": False,
        "paper_promotion": False,
    }


def payload() -> dict:
    return {
        "capability_id": "cap-test",
        "issued_at_utc": "2026-09-07T00:00:00+00:00",
        "control_plane_revision": CONTROL_PLANE_REVISION,
        "contract_sha256": "a" * 64,
        "preflight_sha256": "b" * 64,
        "review_receipt_sha256": "c" * 64,
        "structural_authorization_sha256": "d" * 64,
        "runner_sha256": "e" * 64,
        "runtime_sha256": "f" * 64,
        "support_sha256": "1" * 64,
        "identity_sha256": "2" * 64,
        "run_root": "/tmp/run",
        "lineage_lease_path": "/tmp/lease.json",
        "consumption_marker_path": "/tmp/consume.json",
        "single_use": True,
        "authority": exact_authority(),
    }


class BridgeV4R2StageACapabilityTests(unittest.TestCase):
    def test_production_public_key_is_hard_pinned(self) -> None:
        self.assertTrue(PRODUCTION_PUBLIC_KEY_PATH.is_file())
        self.assertEqual(sha256_file(PRODUCTION_PUBLIC_KEY_PATH), PRODUCTION_PUBLIC_KEY_SHA256)
        self.assertEqual(SIGNATURE_CONTEXT, "E2-R17-BRIDGE-V4R2-STAGE-A-EXECUTION-CAPABILITY-V1")

    def test_attacker_signed_field_complete_capability_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            private = root / "attacker-private.pem"
            public = root / "attacker-public.pem"
            subprocess.run(["/usr/bin/openssl", "genpkey", "-algorithm", "Ed25519", "-out", str(private)], check=True, capture_output=True)
            subprocess.run(["/usr/bin/openssl", "pkey", "-in", str(private), "-pubout", "-out", str(public)], check=True, capture_output=True)
            document = sign_document(payload=payload(), private_key_path=private, public_key_path=public)
            expected = {key: value for key, value in payload().items() if key not in {"capability_id", "issued_at_utc", "control_plane_revision", "single_use", "authority"}}
            with self.assertRaisesRegex(RuntimeError, "signature verification failed"):
                verify_document(document, expected_payload_fields=expected)

    def test_tampered_payload_is_rejected(self) -> None:
        # An attacker-signed document already fails at production signature verification;
        # mutating a signed field must not create an alternate accepted path.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            private = root / "attacker-private.pem"
            public = root / "attacker-public.pem"
            subprocess.run(["/usr/bin/openssl", "genpkey", "-algorithm", "Ed25519", "-out", str(private)], check=True, capture_output=True)
            subprocess.run(["/usr/bin/openssl", "pkey", "-in", str(private), "-pubout", "-out", str(public)], check=True, capture_output=True)
            document = sign_document(payload=payload(), private_key_path=private, public_key_path=public)
            document["payload"]["run_root"] = "/tmp/attacker-run"
            with self.assertRaises(RuntimeError):
                verify_document(document, expected_payload_fields={"run_root": "/tmp/run"})

    def test_consumption_marker_is_atomic_and_single_use(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            marker = Path(td) / "consume.json"
            consume_capability(
                marker_path=marker,
                capability_sha256="a" * 64,
                capability_id="cap-test",
                contract_sha256="b" * 64,
                authorization_sha256="c" * 64,
            )
            row = json.loads(marker.read_text(encoding="utf-8"))
            self.assertTrue(row["consumed_before_provider_io"])
            self.assertEqual(row["capability_id"], "cap-test")
            with self.assertRaises(FileExistsError):
                consume_capability(
                    marker_path=marker,
                    capability_sha256="a" * 64,
                    capability_id="cap-test",
                    contract_sha256="b" * 64,
                    authorization_sha256="c" * 64,
                )

    def test_cli_requires_signed_capability(self) -> None:
        source = (ROOT / "scripts/run_e2_r17_bridge_v4r2_stage_a.py").read_text(encoding="utf-8")
        self.assertIn('parser.add_argument("--signed-capability", type=Path, required=True)', source)
        self.assertIn("signed_capability_path=args.signed_capability", source)

    def test_runtime_consumes_capability_before_run_root_creation(self) -> None:
        source = (ROOT / "research_pipeline/e2_r17_bridge_v4r2_stage_a_runtime.py").read_text(encoding="utf-8")
        consume = source.index("consume_capability(marker_path=markerp")
        make_root = source.index("rr.mkdir(parents=True)")
        self.assertLess(consume, make_root)
        self.assertIn("os.O_CREAT|os.O_EXCL|os.O_WRONLY", source)


if __name__ == "__main__":
    unittest.main()

```


---
## R3 authority provenance tests
Path: `research_pipeline/test_e2_r17_bridge_v4r2_stage_a_authority_provenance.py`
SHA256: `d3012735654eafcd1a620f24308bfdc93c16a921277945f26992a397829c5b54`

```python
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.e2_r17_bridge_v4r2_stage_a_capability import CONTROL_PLANE_REVISION, PRODUCTION_PUBLIC_KEY_SHA256
from scripts.authorize_e2_r17_bridge_v4r2_stage_a import AUTH_STATUS, build_authorization
from scripts.sign_e2_r17_bridge_v4r2_stage_a_capability import build_payload


def dump(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BridgeStageAAuthorityProvenanceTests(unittest.TestCase):
    def fixture(self, root: Path):
        contract = root / "contract.json"
        preflight = root / "preflight.json"
        review = root / "review.json"
        auth = root / "auth.json"
        run_root = root / "run"
        lease = root / "lease.json"
        marker = root / "consume.json"
        contract_payload = {
            "status": "FROZEN_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_SUPPORT",
            "authority": {
                "scientific_experiment": False,
                "provider_io": False,
                "search_pool_acquisition": False,
                "support_inspection": False,
                "free_updater": False,
                "deterministic_state_materialization": False,
                "actor_evaluation": False,
                "screen_outcome_opening": False,
                "validation_opening": False,
                "analysis": False,
                "paper_promotion": False,
            },
            "control_plane_revision": CONTROL_PLANE_REVISION,
            "search": {"unit_ids": ["u1", "u2"], "task_ids": ["t1"]},
            "actor": {"required_resolved_model": "deepseek-v4-pro-ga-260813", "max_turns": 10, "max_output_tokens": 8192},
            "model_identity": {"sha256": "1" * 64},
            "initial_skill": {"sha256": "2" * 64},
            "budget": {"search_provider_call_ceiling": 3840, "per_search_unit_call_ceiling": 10},
            "run_root": str(run_root),
            "lineage_lease_path": str(lease),
            "signed_capability_control": {"consumption_marker_path": str(marker), "production_public_key_sha256": PRODUCTION_PUBLIC_KEY_SHA256},
            "bound_code": {
                "runner": {"sha256": "3" * 64},
                "runtime": {"sha256": "4" * 64},
                "support": {"sha256": "5" * 64},
            },
        }
        dump(contract, contract_payload)
        contract_sha = sha(contract)
        preflight_payload = {
            "status": "PASS_ZERO_PROVIDER_BRIDGE_V4R2_STAGE_A_CONTRACT_PREFLIGHT",
            "contract_sha256": contract_sha,
            "provider_calls": 0,
            "provider_claims": 0,
            "scientific_outcomes_read": False,
            "method_effect_read": False,
            "updater_calls": 0,
            "heldout_actor_calls": 0,
        }
        dump(preflight, preflight_payload)
        preflight_sha = sha(preflight)
        review_payload = {
            "status": "COMPLETED",
            "surface": "ChatGPT web",
            "model": "GPT-5.6 Sol",
            "verdict": "PASS_TO_SEPARATE_BRIDGE_V4R2_STAGE_A_AUTHORIZATION",
            "control_plane_revision": CONTROL_PLANE_REVISION,
            "contract_sha256_acknowledged": contract_sha,
            "preflight_sha256_acknowledged": preflight_sha,
            "scientific_authority_now": False,
            "stage_a_execution_recommendation": "ALLOW_SEPARATE_AUTHORIZATION",
            "remaining_blockers": [],
            "scientific_geometry": "PASS",
            "stage_separation": "PASS",
            "support_gate": "PASS",
            "identity_runtime_budget": "PASS",
            "exactly_once_fail_closed": "PASS",
            "causal_integrity": "PASS",
            "m3r4_dependency": "PASS",
            "r1_supersession_clean": "PASS",
            "r2_supersession_clean": "PASS",
            "authority_provenance": "PASS",
        }
        dump(review, review_payload)
        return contract, preflight, review, auth

    def test_structural_authorization_requires_exact_review_and_remains_capability_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            contract, preflight, review, _ = self.fixture(Path(td))
            auth = build_authorization(contract_path=contract, preflight_path=preflight, review_path=review)
            self.assertEqual(auth["status"], AUTH_STATUS)
            self.assertTrue(auth["authority_requires_external_signed_capability"])
            self.assertEqual(auth["production_public_key_sha256"], PRODUCTION_PUBLIC_KEY_SHA256)
            self.assertEqual(auth["independent_review"]["sha256"], sha(review))
            self.assertIn("consumption_marker_path", auth["execution_scope"])

    def test_review_with_remaining_blocker_cannot_mint_structural_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            contract, preflight, review, _ = self.fixture(Path(td))
            row = json.loads(review.read_text())
            row["remaining_blockers"] = ["forged blocker"]
            dump(review, row)
            with self.assertRaisesRegex(RuntimeError, "retains blockers"):
                build_authorization(contract_path=contract, preflight_path=preflight, review_path=review)

    def test_review_without_authority_provenance_pass_cannot_mint(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            contract, preflight, review, _ = self.fixture(Path(td))
            row = json.loads(review.read_text())
            row["authority_provenance"] = "FAIL"
            dump(review, row)
            with self.assertRaisesRegex(RuntimeError, "authority_provenance"):
                build_authorization(contract_path=contract, preflight_path=preflight, review_path=review)

    def test_signer_binds_exact_review_and_structural_authorization_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            contract, preflight, review, auth_path = self.fixture(Path(td))
            auth = build_authorization(contract_path=contract, preflight_path=preflight, review_path=review)
            dump(auth_path, auth)
            payload = build_payload(contract_path=contract, preflight_path=preflight, review_path=review, authorization_path=auth_path, capability_id="cap", issued_at_utc="2026-09-07T00:00:00Z")
            self.assertEqual(payload["contract_sha256"], sha(contract))
            self.assertEqual(payload["preflight_sha256"], sha(preflight))
            self.assertEqual(payload["review_receipt_sha256"], sha(review))
            self.assertEqual(payload["structural_authorization_sha256"], sha(auth_path))
            self.assertEqual(payload["control_plane_revision"], CONTROL_PLANE_REVISION)
            self.assertTrue(payload["single_use"])

    def test_signer_rejects_review_modified_after_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            contract, preflight, review, auth_path = self.fixture(Path(td))
            auth = build_authorization(contract_path=contract, preflight_path=preflight, review_path=review)
            dump(auth_path, auth)
            row = json.loads(review.read_text())
            row["nonblocking_note"] = "changed after structural authorization"
            dump(review, row)
            with self.assertRaisesRegex(RuntimeError, "review drift"):
                build_payload(contract_path=contract, preflight_path=preflight, review_path=review, authorization_path=auth_path)


if __name__ == "__main__":
    unittest.main()

```


---
## Stage-A support tests
Path: `research_pipeline/test_e2_r17_bridge_v4r2_stage_a_support.py`
SHA256: `ba3a08c4c1f251a7b383098ae593c77592938b660b75491ba17ff6c822ac9127`

```python
from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

from research_pipeline.e2_r17_bridge_v4r2_execution_plan import SCREEN, stage_stream_ids, update_tasks
from research_pipeline.e2_r17_bridge_v4r2_stage_a_support import MIXED_PER_STREAM_MINIMUM, evaluate_screen_support
from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef


def h(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def pool(task_id: str, *, mixed: bool) -> SearchPool:
    scores = (1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0) if mixed else (1.0,) * 8
    refs = tuple(
        TrajectoryRef(
            task_id=task_id,
            rollout_index=i,
            score=score,
            trajectory_path=f"/tmp/{task_id}/{i}.json",
            trajectory_sha256=h(f"traj|{task_id}|{i}"),
            input_sha256=h(f"input|{task_id}"),
            prompt_sha256=h(f"prompt|{task_id}"),
            skill_pre_sha256=h("skill"),
            verifier_sha256=h("verifier"),
            requested_model="deepseek-v4-pro",
            resolved_model="deepseek-v4-pro-ga-260813",
            provider_call_id_sha256=h(f"call|{task_id}|{i}"),
            evidence_tokens=100,
        )
        for i, score in enumerate(scores)
    )
    return SearchPool.freeze(refs)


def support_map(*, bad_stream: str | None = None, bad_mixed: int = 3) -> dict[str, tuple[SearchPool, ...]]:
    out = {}
    for sid in stage_stream_ids(SCREEN):
        n = bad_mixed if sid == bad_stream else 4
        out[sid] = tuple(pool(tid, mixed=i < n) for i, tid in enumerate(update_tasks(sid)))
    return out


class BridgeV4R2StageASupportTests(unittest.TestCase):
    def test_all_six_streams_with_four_mixed_pass(self) -> None:
        result = evaluate_screen_support(support_map())
        self.assertTrue(result.all_streams_qualified)
        self.assertEqual(len(result.streams), 6)
        self.assertTrue(all(row.mixed_pool_count == 4 and row.qualifies for row in result.streams))
        self.assertEqual(result.required_mixed_pools_per_stream, 4)
        self.assertFalse(result.replacement_allowed)

    def test_one_stream_with_three_mixed_holds_entire_stage(self) -> None:
        sid = stage_stream_ids(SCREEN)[2]
        result = evaluate_screen_support(support_map(bad_stream=sid, bad_mixed=3))
        self.assertFalse(result.all_streams_qualified)
        row = next(row for row in result.streams if row.stream_id == sid)
        self.assertEqual(row.mixed_pool_count, 3)
        self.assertFalse(row.qualifies)

    def test_support_threshold_is_frozen_at_four(self) -> None:
        self.assertEqual(MIXED_PER_STREAM_MINIMUM, 4)

    def test_stream_order_drift_is_rejected(self) -> None:
        mapping = support_map()
        reversed_mapping = dict(reversed(list(mapping.items())))
        with self.assertRaisesRegex(ValueError, "stream identity/order drift"):
            evaluate_screen_support(reversed_mapping)

    def test_task_order_drift_is_rejected(self) -> None:
        mapping = support_map()
        sid = stage_stream_ids(SCREEN)[0]
        mapping[sid] = tuple(reversed(mapping[sid]))
        with self.assertRaisesRegex(ValueError, "task order drift"):
            evaluate_screen_support(mapping)

    def test_stage_a_runtime_contains_no_state_or_heldout_execution_path(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "research_pipeline/e2_r17_bridge_v4r2_stage_a_runtime.py").read_text(encoding="utf-8")
        self.assertNotIn("run_bridge_free_update", source)
        self.assertNotIn("materialize_actor_visible_state", source)
        self.assertNotIn("stage_heldout", source)
        self.assertIn('"updater_calls":0', source)
        self.assertIn('"heldout_actor_calls":0', source)


if __name__ == "__main__":
    unittest.main()

```


---
## Stage-A contract/binding tests
Path: `research_pipeline/test_e2_r17_bridge_v4r2_stage_a_contract.py`
SHA256: `f4f2ae0fece2ff2113030a397e70dff6e05fb6f4a308b19a1bc5fe5f456e3200`

```python
from __future__ import annotations

import unittest
from pathlib import Path

from scripts.freeze_e2_r17_bridge_v4r2_stage_a_contract import build_contract

ROOT = Path(__file__).resolve().parents[1]


class BridgeV4R2StageAContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_contract()

    def test_contract_is_zero_authority(self) -> None:
        self.assertEqual(self.contract["status"], "FROZEN_E2_R17_BRIDGE_V4R2_STAGE_A_SCREEN_SEARCH_SUPPORT")
        self.assertFalse(any(self.contract["authority"].values()))

    def test_exact_screen_search_geometry(self) -> None:
        search = self.contract["search"]
        self.assertEqual(len(search["stream_ids"]), 6)
        self.assertEqual(len(search["task_ids"]), 48)
        self.assertEqual(len(search["unit_ids"]), 384)
        self.assertEqual(len(set(search["unit_ids"])), 384)
        self.assertEqual(search["exact_k"], 8)

    def test_stage_a_support_gate_has_no_replacement(self) -> None:
        gate = self.contract["support_gate"]
        self.assertEqual(gate["mixed_pools_per_stream_minimum"], 4)
        self.assertTrue(gate["all_six_streams_must_pass"])
        self.assertFalse(gate["stream_task_or_k_replacement"])
        self.assertTrue(gate["inspection_after_all_384_search_units"])

    def test_stage_a_budget_excludes_updater_and_heldout(self) -> None:
        budget = self.contract["budget"]
        self.assertEqual(budget["search_provider_call_ceiling"], 3840)
        self.assertEqual(budget["per_search_unit_call_ceiling"], 10)
        self.assertEqual(budget["updater_call_ceiling"], 0)
        self.assertEqual(budget["heldout_actor_call_ceiling"], 0)

    def test_r3_external_signed_capability_is_load_bearing(self) -> None:
        control = self.contract["signed_capability_control"]
        self.assertEqual(control["algorithm"], "Ed25519")
        self.assertEqual(control["signature_context"], "E2-R17-BRIDGE-V4R2-STAGE-A-EXECUTION-CAPABILITY-V1")
        self.assertEqual(control["production_public_key_sha256"], "f4b73b89716bee28902feb699d9ab81822a986ac8b89235cf768407c3e01fda0")
        self.assertTrue(control["structural_authorization_alone_is_insufficient"])
        self.assertTrue(control["signed_capability_required_at_runner_point_of_use"])
        self.assertTrue(control["capability_consumed_before_provider_io"])
        self.assertIn("capability_verifier", self.contract["bound_code"])
        self.assertIn("authorization_minter", self.contract["bound_code"])
        self.assertIn("capability_signer", self.contract["bound_code"])

    def test_runner_source_has_no_state_generation_or_heldout_path(self) -> None:
        source = (ROOT / "research_pipeline/e2_r17_bridge_v4r2_stage_a_runtime.py").read_text(encoding="utf-8")
        self.assertNotIn("run_bridge_free_update", source)
        self.assertNotIn("materialize_actor_visible_state", source)
        self.assertNotIn("stage_heldout", source)
        self.assertIn('"updater_calls":0', source)
        self.assertIn('"heldout_actor_calls":0', source)

    def test_point_of_use_binds_exact_runner_runtime_and_authorization_scope(self) -> None:
        source = (ROOT / "research_pipeline/e2_r17_bridge_v4r2_stage_a_runtime.py").read_text(encoding="utf-8")
        self.assertIn("Path(sys.executable).resolve()==runtime_python.resolve()", source)
        for witness in (
            'scope.get("allowed_task_ids")==c["search"]["task_ids"]',
            'int(scope.get("exact_k",-1))==8',
            'scope.get("identity_artifact_sha256")==c["model_identity"]["sha256"]',
            'scope.get("required_skill_pre_sha256")==c["initial_skill"]["sha256"]',
            'int(scope.get("max_turns",-1))==c["actor"]["max_turns"]',
            'int(scope.get("max_output_tokens",-1))==c["actor"]["max_output_tokens"]',
            'scope.get("automatic_retry") is False',
            'scope.get("run_root")==c["run_root"]',
            'pb.get("required") is True',
        ):
            self.assertIn(witness, source)


if __name__ == "__main__":
    unittest.main()

```


---
## Exact relevant V4-R2 protocol excerpts
Full protocol SHA256: `1bc74c6f98e38535cb3865dcd41fb244b7d17c295db0ee9835937cc1034f9ef7`

### Protocol lines 40-72
## 1. Paper hierarchy after canonical primary-line adjudication

The paper must keep four questions orthogonal.

### Q1 — complete state-generation method effect — PRIMARY

Across the two frozen evidence-source cells of the balanced 2×2, does the deterministic typed compiler produce more useful persistent states than the native free-form state generator, using the **first prospectively deployed** FF4 FREE realization?

This is the current primary paper line. Its stream-level estimand is the equal-weight generator-factor main effect:

`G_MAIN,A(s) = 0.5 * { [J_s(W_COMP)-J_s(W_FREE)] + [J_s(FF4_COMP)-J_s(FF4_FREE_A)] }`.

Thus Q1 asks whether the evidence→persistent-state conversion interface matters **averaged equally across Winner and FF4 evidence**. It does not require First-Fail to be superior to Winner, does not require an FF4-specific compiler advantage, and does not use the evidence×generator interaction as a gate.

### Q2 — FF4 trajectory-conditioned diagnosis interpretation — SECONDARY METHOD SUBSTANCE

Within the **FF4 compiler cell only**, does `FF4_COMP` outperform trajectory-text-blind generic canonicalization controls, including a control informed by repair-block cardinality?

This classifies whether the FF4 compiler branch shows method substance beyond generic/scope canonicalization. It does not decide whether the balanced Q1 complete-method effect exists, and it cannot explain or mediate a Q1 main effect that may be driven partly or entirely by the Winner cell.

### Q3 — observed same-evidence state-realization excess disagreement — SECONDARY MECHANISM

Under byte-identical FF4 evidence, do two separately produced FREE persistent states show greater **observed cross-state actor-outcome disagreement** than the observed within-frozen-state actor disagreement?

This is a prospective descriptive/localizing comparison. Under the additional model assumption that actor executions are conditionally iid/independent and stationary given frozen state, task, model, and runtime, the expectation of the statistic has a squared success-propensity interpretation. Because hidden provider randomness cannot be proven independent from logs alone, the protocol's unconditional claim is the observed excess-disagreement statement. Even under the stronger model, V4-R2 does **not** call it a population variance-component estimate and does **not** claim that variance reduction is the demonstrated causal mediator of compiler utility.

### Q4 — rejected-source / Search-Projection moderator — PARKED SECONDARY

Does First-Fail evidence outperform Winner evidence under the compiler, and is there evidence×generator interaction?

This remains scientifically useful but cannot veto Q1-Q3. It is the bridge to the parked Semantic-Transfer/Search-Projection moderator line, not the current paper headline.

## 2. Unchanged 2×2 scientific object

### Protocol lines 73-152

For each frozen stream, search/acting first produces and seals eight K=8 pools. Acting is identical across learning cells and uses the deterministic verifier-selected served winner.

The prospective 2×2 remains:

| Evidence package | Native FREE state generation | Typed constrained compiler |
|---|---|---|
| Winner | `W_FREE` | `W_COMP` |
| First-Fail-4 | `FF4_FREE_A` | `FF4_COMP` |

`FF4_FREE_A` is the first prospectively produced FREE state and is the deployed-realization reference for the primary complete-method estimand.

On VALIDATION only, exactly one additional state `FF4_FREE_B` is prospectively synthesized from the **same byte-identical FF4 evidence package**. B is never a retry, never replaces A, is generated regardless of A outcome, and no third draw exists. V4 calls A/B **separate provider realizations**, not guaranteed statistically independent draws.

The information-parity, runtime, retry-zero, evidence rendering, task split, heldout separation, state-budget measurements, and compiler hidden-metadata prohibitions remain as in the V3 prospective design.

## 3. Unchanged fresh development suite and stage separation

The bridge still uses 120 fresh task artifacts:

- 12 independent development streams;
- 8 update tasks per stream = 96 update tasks;
- 12 disjoint SCREEN heldout tasks;
- 12 different disjoint VALIDATION heldout tasks;
- six streams frozen to SCREEN and six to VALIDATION before provider execution.

No S1 outcome-selected task and no untouched E3 task enters the suite. Validation remains sealed until the raw generator SCREEN gate passes. SCREEN can never be used to alter the compiler vocabulary, diagnosis rules, thresholds, task split, controls, or V4 statistics.

## 4. FF4 evidence semantics and corrected score statement

For a stream, a pool is FF4-eligible iff it is mixed: at least one success and at least one failure. The failed evidence unit is the frozen deterministic first failed nonwinner. A stage is support-qualified only when every required frozen stream has at least four mixed pools.

Exactly four eligible pools are selected by the frozen FF4 hash and replaced; the other four pools retain the same served-winner evidence as Winner.

Therefore FF4 guarantees:

> **four forced failed replacements plus the four unchanged winner scores**.

It does **not** guarantee a universal four-failure/four-success score vector, because an unchanged winner score can itself be zero in an all-failure pool.

No stream/task/model/K replacement is permitted after support inspection.

## 5. Compiler and generic controls

The frozen compiler primitive vocabulary remains:

- `VERIFY_OUTPUT`;
- `COMPLETE_WORKFLOW`;
- `RECOVER_TOOL_ERROR`.

The compiler may use only learner-visible trajectory text plus the selected binary verifier score. It cannot use family, arm, projection, task identity, golden answers, heldout outcomes, or historical scientific outcomes.

### 5.1 `SCORE_ONLY_GENERIC_MAX`

Receives the exact ordered eight selected binary scores and **no trajectory text**. If any selected score is zero it emits the maximal nonredundant generic v1 surface `COMPLETE_WORKFLOW + RECOVER_TOOL_ERROR`; all-success returns S0.

It tests whether score/failure-count information plus maximal generic evaluator-aligned workflow advice already explains the effect.

### 5.2 `SCOPE_MATCHED_GENERIC_MAX`

Receives:

- the same ordered eight selected binary scores;
- scalar `k` = number of nonredundant repair blocks rendered by the typed compiler;
- no trajectory text;
- no repair primitive identity.

Frozen mapping:

- `k=0` -> S0;
- `k=1` -> generic `COMPLETE_WORKFLOW`;
- `k=2` -> generic `COMPLETE_WORKFLOW + RECOVER_TOOL_ERROR`.

The paper must describe this control exactly as:

> **trajectory-text-blind but diagnosis-cardinality-informed**.

`k` is a trajectory-derived repair-cardinality side channel. Passing this control supports benefit **beyond repair-block cardinality/scope**; it does not identify a pure semantic-diagnosis effect independent of every state-size or diagnosis-derived variable.

## 6. Universal state-SHA equivalence classes — mandatory before actor evaluation

### Protocol lines 294-352
Compiler actor disagreement remains a reported diagnostic, not a component subtracted from `E_REAL`.

## 10. VALIDATION FF4 generic-control classification — Q2 only

After the raw validation gate is adjudicated, independently classify the state-SHA-aware **FF4-only** `C_SCORE` and `C_SCOPE` means exactly as at SCREEN:

- both positive -> `FF4_TRAJECTORY_CONDITIONED_TYPED_DIAGNOSIS_SUPPORTED_BEYOND_REPAIR_CARDINALITY`;
- score positive / scope nonpositive -> `FF4_SCOPE_OR_SPARSITY_CANONICALIZATION_ONLY`;
- score nonpositive -> `FF4_GENERIC_CANONICALIZATION_NOT_REJECTED`.

A generic-control result narrows or strengthens the interpretation of the FF4 compiler branch. It cannot erase a separately passed balanced Q1 generator-method contrast and cannot be used to claim that typed FF4 diagnosis explains the Winner-side component of `G_MAIN,A`.

## 11. Rejected-source VALIDATION — Q4 remains independent

Independently evaluate the frozen rejected-source conditions using `S_C` and the 2×2 interaction. Failure removes First-Fail-specific promotion and leaves the Search-Projection/Semantic-Transfer line parked. It cannot invalidate Q1, Q2 classification, or Q3 localization.

## 12. Orthogonal decision table

V4 adjudicates a tuple, not one conjunctive PASS bit:

`(Q1_complete_method, Q2_ff4_diagnosis_class, Q3_observed_realization_excess, Q4_rejected_source)`.

### A. Raw generator SCREEN fails

`STOP_COMPLETE_STATE_GENERATION_METHOD_STORY_SCREEN`

VALIDATION remains sealed. No automatic typed-compiler E3 proposal.

### B. Raw generator VALIDATION fails

`STOP_COMPLETE_STATE_GENERATION_METHOD_STORY_VALIDATION`

Do not rescue with B, generic controls, realization probe, rejected-source result, or E3.

### C. Q1 passes; FF4 generic controls do not establish typed diagnosis

Keep the empirically supported balanced complete state-generation method effect. Separately label the FF4 branch as either:

- `FF4_SCOPE_OR_SPARSITY_CANONICALIZATION_ONLY`, or
- `FF4_GENERIC_CANONICALIZATION_NOT_REJECTED`.

Do not claim trajectory-conditioned typed diagnosis for FF4 and do not imply that either Q2 label explains the Winner-side contribution to Q1. Any E3 proposal for the complete method requires separate adjudication.

### D. Q1 passes; FF4 typed-diagnosis controls pass; Q3 observed excess fails

`PASS_COMPLETE_METHOD_WITH_FF4_TYPED_DIAGNOSIS_DROP_REALIZATION_EXCESS_CLAIM`

The balanced complete method effect remains eligible for a separately reviewed E3 proposal. The FF4 branch may support typed-diagnosis substance beyond the stated controls, but realization/variance-centered mechanism language is removed.

### E. Q1 + FF4 typed diagnosis + Q3 observed excess pass; Q4 fails

`PASS_COMPLETE_METHOD_WITH_FF4_DIAGNOSIS_AND_OBSERVED_REALIZATION_EXCESS_DROP_REJECTED_SOURCE_CLAIM`

This is a clean primary-paper outcome if the generator method helps but rejected evidence is not generally superior. Q2 remains an FF4-specific substance result and Q3 remains an observed excess-disagreement result unless the stronger iid/stationary actor model is explicitly invoked. A separate untouched E3 proposal is still required.

### F. Q1 + FF4 typed diagnosis + Q3 observed excess + Q4 pass

`PASS_FULL_BRIDGE_ELIGIBLE_FOR_SEPARATE_E3_PROPOSAL`


### Protocol lines 388-408
Current V4-R2 test count is recorded in the bound zero-provider audit after the full adjacent regression suite is run.

## 15. Current scientific authority

This V4-R2 document grants zero authority for:

- provider calls;
- bridge search-pool acquisition;
- updater execution;
- FREE_A or FREE_B synthesis;
- actor evaluation or actor remeasurement;
- SCREEN outcome opening;
- VALIDATION opening;
- E3;
- second backbone;
- public benchmark;
- paper promotion.

It is a prospective review-repair object only.

Before any Bridge Stage A execution, V4-R2 itself must be frozen/content-addressed and independently reviewed. The canonical primary-line resource rule remains in force: **do not execute the parked Semantic-Transfer Stage A while the State-Generator bridge remains unresolved.**
