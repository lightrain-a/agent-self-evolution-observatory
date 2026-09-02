You are an independent adversarial pre-execution reviewer for E2-R17 Selective-MRW Semantic-Transfer V1. You are a reviewer only. No Stage-A search-pool outcomes and no Stage-B learning outcomes are supplied. You may recommend at most a separately SHA-bound Stage-A pool-acquisition authorization. You may NOT authorize Stage B, heldout evaluation, analyzer, second backbone, public benchmark, or paper claims.

Reviewer endpoint: kimi-k3
Exact Stage-A contract SHA-256: 232d0085ff03ef76c1ff993082ea6b40aeb47382e9156cc821f0ee9a55d0cfa0

Scientific history and intent:
- The closed 48-pair DeepSeek experiment is immutable HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS.
- A previous same-family Selective-MRW V3 design was superseded before provider execution because family-ID lookup remained a reduction.
- This child uses SIX COMPLETELY NEW failure-family identities arranged as three matched structural skeletons. A mechanical pre-outcome semantic rule routes reusable procedural transformations to MRW4 and instance-binding/localization tasks to WIN-C.
- Stage A only acquires K=8 pools. It has no updater and no heldout evaluation.
- Stage B is not authorized. If later authorized, MRW4 would replace winner evidence on EXACTLY FOUR hash-frozen mixed pools per stream; every passing stream has the same treatment dose.
- The proposed selector earns a method claim only if, on untouched new family identities, (A) MRW4 beats WIN-C over six procedural streams AND (B) WIN-C beats MRW4 over six binding streams. Both exact one-sided 2^6 sign-flip tests plus positive bootstrap lower bounds must pass. This is an intersection-union claim.

Audit the exact dossier against these questions:
1. DISCOVERY -> CONFIRMATION: Is it scientifically legitimate to discover the procedural-vs-binding hypothesis after the closed HOLD, then test it only on new family identities without pooling old outcomes? Does the manuscript boundary make the post-hoc discovery transparent enough?
2. FAMILY-ID REDUCTION: Do the six new family identities plus the mechanical structural rule actually prevent an old-family lookup from routing TEST? Is there any hidden family label or metadata path that makes the test merely same-family memorization?
3. MATCHED SKELETONS: Are the three paired structural skeletons a meaningful control, or are procedural and binding families still so different that a task-class confound trivially explains the result? If a blocker remains, state the smallest pre-outcome repair.
4. EQUAL DOSE: Stage A requires every stream to have >=4 mixed pools, then chooses exactly four by frozen hash. Is this a valid pre-treatment support condition that equalizes learning-treatment dose, or does conditioning on mixedness create an unacceptable selection/collider problem for the intended claim? Note: no task/stream is dropped; if ANY stream fails support, the entire child HOLDS.
5. SUPPORT GATE: Is all-12-stream >=4 mixed support a legitimate identifiability gate, not an outcome-selected favorable subset? K/model/tasks/families cannot be changed after Stage A.
6. CAUSAL PURITY: Verify from the dossier that MRW is matched-budget branch replacement, NOT winner+failure; acting winner stays fixed; non-treated pools use winner; exact evidence-token parity is inherited from the frozen renderer. Does Stage A itself make no causal-effect claim?
7. STATISTICS: Are six independent procedural stream effects and six independent binding stream effects legitimate scientific units for their separate exact sign-flip tests? Is requiring both gates at alpha=.05 a valid intersection-union rule for the joint selector claim? Are two streams/family correctly prevented from becoming family-specific p-values?
8. SAME-INFORMATION FIXED POLICY BASELINES: Does the joint gate really establish that the structural selector beats BOTH always-WIN and universal-MRW4 without a third execution arm? Or is another same-information baseline required before Stage A?
9. ACTOR/RUNTIME SCOPE: Does the compatibility alias preserve exact task mappings? Does the unmodified generic actor enforce mode/task/K scope? The actual-path preflight says K=4, b16 heldout, and wrong mode are rejected before provider I/O. Check for a bypass.
10. BUDGET/CHECKPOINT/FAIL-CLOSED: Stage A is 96 pools x 8 rollouts, max 10 turns = <=7680 provider claims, retry=0. Is the proposed contract sufficiently fail-closed for exactly-once execution? Does any resume or quota failure need another control before authorization?
11. PAPER STORY: Is the coherent contribution now 'acting projection and learning projection should be decoupled, and rejected evidence should be selectively exposed when it carries reusable procedural information', rather than 'failures help'? Is that story supported if both future gates pass, while clearly NOT claiming a production-ready classifier or universal semantic law?
12. AUTHORITY: PASS can only recommend separately minting a single-use Stage-A authorization. Stage B and paper_claim_authority must remain false.

PASS only if remaining_blockers is exactly [] and there is no P0/P1 issue that must be repaired before spending the 768 Stage-A rollouts. Do not demand Stage-B results as a precondition for Stage A; review whether Stage A is a valid, necessary support-acquisition step.

Return exactly one JSON object and no markdown using this schema:
{
  "contract_sha256_acknowledged": "",
  "verdict": "PASS_TO_SEPARATE_STAGE_A_AUTHORIZATION|REVISE_BEFORE_STAGE_A|STOP_SEMANTIC_TRANSFER_CHILD",
  "discovery_confirmation_assessment": "",
  "family_identity_reduction_assessment": "",
  "matched_skeleton_assessment": "",
  "equal_dose_assessment": "",
  "stage_a_support_selection_assessment": "",
  "projection_causal_purity_assessment": "",
  "statistics_assessment": "",
  "actor_runtime_scope_assessment": "",
  "checkpoint_budget_failclosed_assessment": "",
  "paper_story_assessment": "",
  "remaining_blockers": [
    {
      "priority": "P0|P1",
      "issue": "",
      "why_blocking": "",
      "exact_repair": ""
    }
  ],
  "nonblocking_notes": [
    ""
  ],
  "execution_recommendation": "ALLOW_SEPARATE_STAGE_A_AUTHORIZATION|HOLD|STOP",
  "paper_claim_authority": false,
  "stage_b_authority": false,
  "single_sentence_verdict": ""
}
Set contract_sha256_acknowledged exactly to the SHA above.

BOUND DOSSIER START

===== BOUND ARTIFACT: paper_method_design | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-prospective-heterogeneity-pre-f0-20260902/consultations/e2-r17-selective-mrw-semantic-transfer-v1-20260902.md =====
# E2-R17 Selective-MRW Semantic-Transfer V1 — Pre-F0

Date: 2026-09-02

## 0. Scientific lineage

The closed DeepSeek Repair2 / Continuation V2 result remains immutable:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`.

The earlier same-family Selective-MRW V3 design reached only zero-provider static audit. It made zero provider calls and observed zero new TEST outcomes. It is superseded **before provider execution** because its TEST reused the same six failure-family identities as the discovery sample, leaving a family-ID lookup explanation unresolved.

Semantic-Transfer V1 is a new prospective child hypothesis. Old outcomes are discovery/calibration evidence only and can never be pooled with this child for confirmatory inference.

## 1. Paper question

Search produces a pool of candidate trajectories `T_K`. Current acting consumes a verifier-selected trajectory `a(T_K)`. Persistent learning consumes a possibly different evidence projection `g(T_K)`.

The paper asks:

> Is the branch worth serving necessarily the branch worth learning from, and can a pre-outcome structural rule determine when rejected evidence should replace winner evidence for persistent learning?

The child hypothesis is deliberately narrower than "failure trajectories help":

> Rejected evidence is more useful when it exposes a reusable transformation procedure, but not when it primarily exposes an instance-specific binding/localization choice.

This is a prospective hypothesis discovered from the closed sample and must transport to completely new failure-family identities to acquire authority.

## 2. Actual learning-projection data flow

For every update task:

`initial skill S0 -> K=8 search pool T_K -> deterministic verifier -> served winner a(T_K)`.

The acting channel is identical in all learning arms.

Learning arms are matched-budget branch projections:

- `WIN-C`: updater-visible evidence is the served winner;
- `MRW4`: on exactly four pre-frozen mixed pools per stream, updater-visible evidence is the deterministic failed nonwinner selected by the existing MRW rule; on every other pool, updater-visible evidence is the winner.

MRW4 is **not** `winner + failure`. It replaces the updater-visible winner branch on exactly four mixed pools while holding acting behavior fixed. The existing exact matched-window renderer must equalize final updater-visible token length for every paired evidence block.

Then:

`{g_WIN(T_K), g_MRW4(T_K)} -> same SkillEvolver -> frozen {S_WIN, S_MRW4} -> same unseen K=1 heldout panel`.

The only scientific treatment is which already-generated branch is shown to the updater on the four frozen mixed-pool positions.

## 3. Structural semantic rule — no old family lookup

The router is defined from two pre-outcome structural quantities:

- `reusable_transform_steps`: number of reusable state-transform operations required once bindings are explicit;
- `binding_candidate_count`: number of plausible instance-specific bindings among which the task must select.

Frozen routing rule:

- `PROCEDURAL_TRANSFORMATION` iff `reusable_transform_steps >= 2` and `binding_candidate_count == 1`;
- `INSTANCE_BINDING_LOCALIZATION` iff `binding_candidate_count >= 2` and `reusable_transform_steps <= 1`.

Selective-MRW policy:

- procedural -> use MRW4 learned state;
- binding/localization -> use WIN-C learned state.

The old six family IDs never occur in Semantic-Transfer TEST, so an old-family lookup table cannot route a TEST task.

## 4. Fully new TEST family identities with crossed structural skeletons

Use six new failure families arranged as three matched skeletons. No family occurred in the closed sample or same-family V3 TEST.

| matched skeleton | PROCEDURAL_TRANSFORMATION | INSTANCE_BINDING_LOCALIZATION |
|---|---|---|
| two-table join | `ordered_filter_rollup` | `foreign_key_binding` |
| single-table measure | `normalize_then_rank` | `header_source_binding` |
| snapshot table | `reconcile_then_aggregate` | `named_region_binding` |

Interpretation of the match:

- both sides operate on similar spreadsheet structures;
- procedural variants have explicit/unambiguous bindings and require multiple reusable transformation steps;
- binding variants have a simple post-binding computation but multiple plausible current/legacy/candidate binding choices;
- candidate key/column/region order is deterministically randomized to prevent a fixed-position shortcut.

This design changes failure-family identity while preserving the semantic distinction, so successful prediction is semantic transport rather than same-family replication.

## 5. Zero-provider semantic-transfer suite

Bound generator: `scripts/build_e2_r17_semantic_transfer_suite_v1.py`.

Output root:

`/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-semantic-transfer-v1`

Static shape:

- blocks b14/b15: update candidates;
- block b16: heldout candidates;
- 6 new families;
- 12 update streams, 2 per family;
- 8 update tasks per stream;
- 96 update tasks total;
- 18 common heldout tasks, 3 per family;
- 6 procedural streams and 6 binding streams;
- 4 streams per matched skeleton;
- old-suite task-ID overlap = 0;
- old-suite XLSX SHA-256 overlap = 0;
- provider calls = 0.

The heldout panel is never shown to the updater.

## 6. Stage A — search-pool acquisition and equal-dose qualification

Before any updater call:

- exact same DeepSeek identity is required: requested `deepseek-v4-pro`, resolved exactly `deepseek-v4-pro-ga-260813`;
- K = 8;
- 96 update tasks -> 96 K=8 pools -> 768 actor rollouts;
- no updater;
- no learned states;
- no heldout evaluation;
- no treatment-effect inference.

All pools are sealed and content-addressed before support inspection.

### Equal-dose support gate

Every one of the 12 streams must contain at least four mixed pools. If any stream has fewer than four, STOP with:

`HOLD_SEMANTIC_TRANSFER_INSUFFICIENT_EQUAL_DOSE_SUPPORT`.

No K/model/task/family replacement is allowed.

For every passing stream, choose exactly four mixed pools by the lowest SHA256 value of:

`semantic-transfer-mrw4-v1|stream_id|task_id`.

Freeze these 48 treated pool IDs before any Stage-B updater call.

Consequences:

- every stream receives exactly four MRW branch replacements;
- procedural and binding streams have identical treatment dose;
- extra mixed pools do not create extra MRW exposure;
- availability `M_z(K)` cannot by itself explain a semantic difference in Stage B.

Also require zero duplicate pool units, zero technical failures, and zero b16 heldout access.

## 7. Stage B — paired learning TEST

For each of the 12 new streams, run contemporaneous paired learning from the same initial skill and exact Stage-A pools:

- WIN-C;
- MRW4.

Freeze `R = 8` paired replicates per stream before any learning outcome.

Total Stage B:

- 12 streams;
- 8 paired replicates per stream;
- 96 paired units;
- 192 learned states;
- 18 common K=1 heldout tasks per state;
- 3456 heldout evaluations.

All arms share actor pools, acting winner, initial skill, updater implementation, provider identity, prompt, matched evidence tokens, verifier, heldout panel, K=1 evaluation, and decoding settings.

For stream `s`:

`D_s = mean_r [J_s,r(MRW4) - J_s,r(WIN-C)]`.

## 8. Selective-MRW is derived without a third execution arm

For procedural streams, Selective-MRW uses the already-created MRW4 learned state.

For binding streams, Selective-MRW uses the already-created WIN-C learned state.

Thus no third updater/evaluator arm is needed.

The selector must beat **both fixed policies** to earn a method claim.

### Gate A — procedural benefit over always-WIN

Use the six procedural stream effects `D_s`.

Require all:

1. mean procedural `D_s > 0`;
2. exact one-sided sign-flip test over the six procedural stream effects, alpha=.05;
3. paired-stream bootstrap 95% lower bound > 0.

Failure -> `STOP_NO_PROSPECTIVE_PROCEDURAL_MRW_BENEFIT`.

### Gate B — binding protection over universal MRW

Use the six binding stream effects with sign reversed, `-D_s`.

Require all:

1. mean binding `-D_s > 0` (WIN-C better than MRW4 in binding streams);
2. exact one-sided sign-flip test over the six binding stream effects, alpha=.05;
3. paired-stream bootstrap 95% lower bound > 0.

Failure after Gate A passes -> retain only procedural-MRW transport; **do not** claim a selective router beats universal MRW.

### Joint method verdict

Only if Gate A and Gate B both pass:

`GO_SELECTIVE_MRW_SEMANTIC_TRANSFER_SUPPORTED`.

Because the method claim requires both inequalities simultaneously, this is an intersection-union decision: both component tests must pass at alpha=.05. Neither component can rescue the other.

The joint claim is:

> On completely new failure-family identities and equal rejected-evidence dose, the frozen structural selector prospectively chooses the better learning projection: MRW4 for reusable procedural deficiencies and WIN-C for instance-binding deficiencies, outperforming both always-WIN and universal-MRW policies.

## 9. Secondary mechanism checks

Report without replacing the joint gates:

- stream-level effects for all 12 streams;
- per-family means;
- matched-skeleton procedural-minus-binding contrasts;
- global MRW4 vs WIN-C mean;
- Selective-MRW mean utility vs both fixed policies;
- failures and counterexamples retained.

Do not create family-specific significance claims from two streams/family.

The three matched skeletons are mechanism diagnostics, not independent confirmatory n for a 3-pair significance test.

## 10. Interpretation boundaries

If both gates pass:

- supported: semantic transport of the selective projection rule to unseen family identities under the controlled suite;
- supported: selection is not explainable by old-family lookup or unequal MRW dose;
- not yet supported: a production-ready classifier for arbitrary natural tasks;
- not yet supported: cross-backbone universality or public-benchmark generality.

If Gate A passes but Gate B fails:

- supported only: MRW4 benefits new procedural families;
- not supported: Selective-MRW beats universal MRW.

If Gate A fails:

- close this semantic-transfer child; do not add families/models/threshold changes as rescue.

## 11. Fail-closed execution rules

- closed 48-pair outcome remains HOLD and is never pooled into TEST inference;
- old six family IDs are forbidden from Semantic-Transfer scientific TEST;
- all 12 TEST streams are retained regardless of outcome;
- Stage-A mixedness may only determine equal-dose support and the predeclared four treated pool IDs;
- no b16 heldout task may be touched before learned states are frozen;
- no partial Stage-B treatment effect read;
- no automatic retry after provider/runtime failure;
- no second-backbone/public-benchmark rescue;
- no threshold/K/family modification after Stage A starts;
- full integrity audit precedes any analyzer.

## 12. Current authority

`PRE_F0_SEMANTIC_TRANSFER_ZERO_PROVIDER_ONLY`.

Allowed now:

- builder/static verification;
- deterministic regeneration check;
- old-suite disjointness audit;
- untouched-run-artifact audit;
- method/data-flow review;
- development-only current-provider identity qualification after static audit passes.

Not yet allowed:

- Stage-A 768 actor rollouts;
- Stage-B updater calls;
- heldout evaluation;
- analyzer;
- paper promotion;
- second backbone/public benchmark.


===== BOUND ARTIFACT: stage_a_contract | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-prospective-heterogeneity-pre-f0-20260902/generated/e2-r17-semantic-transfer-v1-stage-a-contract-20260902.json =====
{
  "actor": {
    "concurrency": 1,
    "k": 8,
    "max_output_tokens": 8192,
    "max_turns": 10,
    "prefix_ks": [
      1,
      2,
      4,
      8
    ],
    "provider_retry_limit": 0,
    "requested_model": "deepseek-v4-pro",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "temperature": 0,
    "thinking": "disabled"
  },
  "artifact_type": "e2-r17-selective-mrw-semantic-transfer-v1-stage-a-contract",
  "authority": {
    "analyzer": false,
    "heldout_evaluation": false,
    "paper_promotion": false,
    "public_benchmark": false,
    "second_backbone": false,
    "stage_a_provider_execution": false,
    "stage_b_learning_execution": false,
    "updater": false
  },
  "bound_code": {
    "actor": {
      "path": "scripts/run_e2_r17_actor_pool.py",
      "sha256": "20a81fbe06f3839cd17babfdb021407368493da61610bca33aae33df8d31ec14"
    }
  },
  "budget": {
    "actor_rollouts": 768,
    "max_provider_calls": 7680,
    "provider_calls_per_rollout_limit": 10
  },
  "created_at_utc": "2026-09-02T15:37:37+00:00",
  "equal_dose_support": {
    "failure_status": "HOLD_SEMANTIC_TRANSFER_INSUFFICIENT_EQUAL_DOSE_SUPPORT",
    "required_mixed_pools_per_stream": 4,
    "stage_b_treated_pool_ids_must_be_frozen_before_updater": true,
    "streams_required": 12,
    "treated_mixed_pools_per_stream": 4,
    "treated_pool_selection": "lowest SHA256(semantic-transfer-mrw4-v1|stream_id|task_id) among mixed pools"
  },
  "exactly_once": {
    "automatic_retry": false,
    "completed_rollout_replay": false,
    "replacement_sampling": false,
    "resume_requires_separate_adjudication": true
  },
  "mindmemos": {
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "initial_skill_path": "/data/wyt/evidence-substrates/MindMemOS-20260817/resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md",
    "initial_skill_sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb",
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817"
  },
  "model_identity": {
    "path": "generated/e2-r17-selective-mrw-semantic-transfer-v1-deepseek-identity-qualification-20260902.json",
    "requested": "deepseek-v4-pro",
    "resolved": "deepseek-v4-pro-ga-260813",
    "sha256": "78eeb2f58edd6c9f60d355afaf90a8adc5ae811f0434cc0ef59d2b31220b6c5d"
  },
  "partial_effect_read": false,
  "run_root": "/data/wyt/e2-r17-search-projection/runs/semantic-transfer-v1-stage-a-20260902",
  "runtime": {
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt",
    "freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "qualification_path": "generated/e2-r17-runtime-dependency-qualification-r2-20260828.json",
    "qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv"
  },
  "runtime_compat_audit": {
    "path": "generated/e2-r17-semantic-transfer-v1-runtime-compat-r1-audit-20260902.json",
    "sha256": "f63d9817dacedc1e1ec5ad3ed1e657875cdfcc436363929f0e8a9b30e360aa89"
  },
  "schema_version": "1.0",
  "scientific_role": "search-pool acquisition and equal-dose support qualification only",
  "scientific_scores_read": false,
  "status": "FROZEN_SEMANTIC_TRANSFER_V1_STAGE_A_PENDING_REVIEW",
  "suite": {
    "allowed_task_ids": [
      "r17-b14-fkb-p7",
      "r17-b14-fkb-p2",
      "r17-b14-fkb-p1",
      "r17-b14-fkb-p4",
      "r17-b14-fkb-p3",
      "r17-b14-fkb-p8",
      "r17-b14-fkb-p5",
      "r17-b14-fkb-p0",
      "r17-b15-fkb-p2",
      "r17-b15-fkb-p3",
      "r17-b15-fkb-p8",
      "r17-b15-fkb-p1",
      "r17-b15-fkb-p4",
      "r17-b15-fkb-p0",
      "r17-b15-fkb-p5",
      "r17-b15-fkb-p7",
      "r17-b14-hsb-p2",
      "r17-b14-hsb-p1",
      "r17-b14-hsb-p8",
      "r17-b14-hsb-p0",
      "r17-b14-hsb-p7",
      "r17-b14-hsb-p6",
      "r17-b14-hsb-p4",
      "r17-b14-hsb-p5",
      "r17-b15-hsb-p1",
      "r17-b15-hsb-p4",
      "r17-b15-hsb-p0",
      "r17-b15-hsb-p5",
      "r17-b15-hsb-p3",
      "r17-b15-hsb-p7",
      "r17-b15-hsb-p6",
      "r17-b15-hsb-p2",
      "r17-b14-nrb-p0",
      "r17-b14-nrb-p7",
      "r17-b14-nrb-p5",
      "r17-b14-nrb-p8",
      "r17-b14-nrb-p6",
      "r17-b14-nrb-p3",
      "r17-b14-nrb-p4",
      "r17-b14-nrb-p2",
      "r17-b15-nrb-p8",
      "r17-b15-nrb-p6",
      "r17-b15-nrb-p4",
      "r17-b15-nrb-p7",
      "r17-b15-nrb-p5",
      "r17-b15-nrb-p0",
      "r17-b15-nrb-p2",
      "r17-b15-nrb-p1",
      "r17-b14-ntr-p6",
      "r17-b14-ntr-p5",
      "r17-b14-ntr-p8",
      "r17-b14-ntr-p3",
      "r17-b14-ntr-p7",
      "r17-b14-ntr-p2",
      "r17-b14-ntr-p4",
      "r17-b14-ntr-p1",
      "r17-b15-ntr-p7",
      "r17-b15-ntr-p8",
      "r17-b15-ntr-p4",
      "r17-b15-ntr-p3",
      "r17-b15-ntr-p2",
      "r17-b15-ntr-p1",
      "r17-b15-ntr-p5",
      "r17-b15-ntr-p0",
      "r17-b14-ofr-p6",
      "r17-b14-ofr-p8",
      "r17-b14-ofr-p4",
      "r17-b14-ofr-p5",
      "r17-b14-ofr-p3",
      "r17-b14-ofr-p1",
      "r17-b14-ofr-p7",
      "r17-b14-ofr-p0",
      "r17-b15-ofr-p8",
      "r17-b15-ofr-p7",
      "r17-b15-ofr-p0",
      "r17-b15-ofr-p5",
      "r17-b15-ofr-p6",
      "r17-b15-ofr-p3",
      "r17-b15-ofr-p4",
      "r17-b15-ofr-p1",
      "r17-b14-rta-p4",
      "r17-b14-rta-p7",
      "r17-b14-rta-p3",
      "r17-b14-rta-p2",
      "r17-b14-rta-p1",
      "r17-b14-rta-p0",
      "r17-b14-rta-p5",
      "r17-b14-rta-p6",
      "r17-b15-rta-p6",
      "r17-b15-rta-p8",
      "r17-b15-rta-p5",
      "r17-b15-rta-p1",
      "r17-b15-rta-p2",
      "r17-b15-rta-p0",
      "r17-b15-rta-p4",
      "r17-b15-rta-p3"
    ],
    "heldout_task_ids_forbidden": [
      "r17-b16-fkb-p1",
      "r17-b16-fkb-p5",
      "r17-b16-fkb-p6",
      "r17-b16-hsb-p0",
      "r17-b16-hsb-p4",
      "r17-b16-hsb-p8",
      "r17-b16-nrb-p0",
      "r17-b16-nrb-p4",
      "r17-b16-nrb-p8",
      "r17-b16-ntr-p1",
      "r17-b16-ntr-p5",
      "r17-b16-ntr-p6",
      "r17-b16-ofr-p0",
      "r17-b16-ofr-p4",
      "r17-b16-ofr-p8",
      "r17-b16-rta-p1",
      "r17-b16-rta-p5",
      "r17-b16-rta-p6"
    ],
    "metadata_sha256": "5802f35a6fedaa843ba61887ad0a892b8a178b33c20fb6bc4ad0f05e9832476f",
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-semantic-transfer-v1",
    "split_manifest_sha256": "6ac03fd07391b2671e2e3cecd975395adff6c9fbd622751195a5a46b6a39af1c",
    "streams": [
      "st-fkb-00",
      "st-fkb-01",
      "st-hsb-00",
      "st-hsb-01",
      "st-nrb-00",
      "st-nrb-01",
      "st-ntr-00",
      "st-ntr-01",
      "st-ofr-00",
      "st-ofr-01",
      "st-rta-00",
      "st-rta-01"
    ],
    "suite_manifest_sha256": "a7ddee258ddc22cee3efe22bad44046faa20ba9d49762c98a66a843c2c9533a3"
  }
}


===== BOUND ARTIFACT: stage_a_preflight | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-prospective-heterogeneity-pre-f0-20260902/generated/e2-r17-semantic-transfer-v1-stage-a-preflight-20260902.json =====
{
  "actor_help_under_frozen_runtime_pass": true,
  "artifact_type": "e2-r17-selective-mrw-semantic-transfer-v1-stage-a-zero-provider-preflight",
  "authority": {
    "mint_stage_a_authorization": false,
    "paper_promotion": false,
    "stage_a_provider_execution": false,
    "stage_b_learning_execution": false
  },
  "contract_path": "generated/e2-r17-semantic-transfer-v1-stage-a-contract-20260902.json",
  "contract_sha256": "232d0085ff03ef76c1ff993082ea6b40aeb47382e9156cc821f0ee9a55d0cfa0",
  "created_at_utc": "2026-09-02T15:37:37+00:00",
  "exact_k": 8,
  "execution_scope_guard_checks": {
    "heldout_task_rejected": true,
    "valid_e1_k8_scope_passes": true,
    "wrong_k_rejected": true,
    "wrong_mode_rejected": true
  },
  "heldout_evaluation_authority": false,
  "heldout_forbidden_count": 18,
  "max_provider_calls": 7680,
  "new_test_outcomes_accessed": false,
  "next_gate": "INDEPENDENT_PREEXECUTION_REVIEW_BEFORE_SINGLE_USE_STAGE_A_AUTHORIZATION",
  "provider_calls": 0,
  "run_root_exists": false,
  "runtime_import_smoke_pass": true,
  "schema_version": "1.0",
  "scientific_execution": false,
  "status": "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_STAGE_A_ACTUAL_PATH_PREFLIGHT",
  "stream_count": 12,
  "task_count": 96,
  "updater_authority": false
}


===== BOUND ARTIFACT: runtime_compat_audit | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-prospective-heterogeneity-pre-f0-20260902/generated/e2-r17-semantic-transfer-v1-runtime-compat-r1-audit-20260902.json =====
{
  "actor": {
    "compatibility_mode": "existing_e1_mode",
    "path": "scripts/run_e2_r17_actor_pool.py",
    "sha256": "20a81fbe06f3839cd17babfdb021407368493da61610bca33aae33df8d31ec14"
  },
  "artifact_type": "e2-r17-semantic-transfer-v1-runtime-compat-r1-audit",
  "authority": {
    "analyzer": false,
    "heldout_evaluation": false,
    "paper_promotion": false,
    "stage_a_provider_execution": false,
    "stage_b_learning_execution": false,
    "zero_provider_stage_a_contract_preflight": true
  },
  "identity": {
    "path": "generated/e2-r17-selective-mrw-semantic-transfer-v1-deepseek-identity-qualification-20260902.json",
    "requested": "deepseek-v4-pro",
    "resolved": "deepseek-v4-pro-ga-260813",
    "sha256": "78eeb2f58edd6c9f60d355afaf90a8adc5ae811f0434cc0ef59d2b31220b6c5d",
    "usage": {
      "input_tokens": 27,
      "input_tokens_details": {
        "cached_tokens": 0
      },
      "output_tokens": 3,
      "output_tokens_details": {
        "reasoning_tokens": 0
      },
      "total_tokens": 30
    }
  },
  "new_test_outcomes_accessed": false,
  "next_gate": "FREEZE_STAGE_A_DRAFT_CONTRACT_AND_RUN_ZERO_PROVIDER_ACTUAL_PATH_PREFLIGHT",
  "parent_pre_f0": {
    "path": "generated/e2-r17-selective-mrw-semantic-transfer-v1-pre-f0-20260902.json",
    "sha256": "d30aadfc1991e63d9db604edbf38dac8203603c00edc3c5c103026bd9ff661a9"
  },
  "parent_static_audit": {
    "path": "generated/e2-r17-selective-mrw-semantic-transfer-v1-static-audit-20260902.json",
    "sha256": "30e2350447b190661c6ed20d40fd9e95d40f81d846a9fd2a172a6ec59d85f3f6"
  },
  "provider_calls_scientific": 0,
  "provider_calls_total_for_child": 1,
  "runtime": {
    "freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "initial_skill_sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb",
    "mindmemos_commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "mindmemos_root": "/data/wyt/evidence-substrates/MindMemOS-20260817",
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv"
  },
  "schema_version": "1.0",
  "scientific_execution": false,
  "status": "PASS_SEMANTIC_TRANSFER_V1_RUNTIME_COMPAT_R1",
  "suite": {
    "actor_compat_metadata_sha256": "5802f35a6fedaa843ba61887ad0a892b8a178b33c20fb6bc4ad0f05e9832476f",
    "actor_compat_split_sha256": "6ac03fd07391b2671e2e3cecd975395adff6c9fbd622751195a5a46b6a39af1c",
    "compat_alias_semantics_changed": false,
    "core_metadata_sha256": "5802f35a6fedaa843ba61887ad0a892b8a178b33c20fb6bc4ad0f05e9832476f",
    "core_split_sha256": "db911c2c088f3a5df08ffccc922ea8b68a6af31f0f8a1bb4372ce85e62b34033",
    "deterministic_regeneration_all_330_files_equal": true,
    "heldout_tasks": 18,
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-semantic-transfer-v1",
    "suite_manifest_sha256": "a7ddee258ddc22cee3efe22bad44046faa20ba9d49762c98a66a843c2c9533a3",
    "update_tasks": 96
  }
}


===== BOUND ARTIFACT: parent_static_audit | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-prospective-heterogeneity-pre-f0-20260902/generated/e2-r17-selective-mrw-semantic-transfer-v1-static-audit-20260902.json =====
{
  "artifact_type": "e2-r17-selective-mrw-semantic-transfer-v1-static-audit",
  "authority": {
    "analyzer": false,
    "current_provider_identity_qualification": true,
    "heldout_evaluation": false,
    "paper_promotion": false,
    "public_benchmark": false,
    "second_backbone": false,
    "stage_a_provider_execution": false,
    "stage_b_learning_execution": false,
    "zero_provider_stage_a_preflight": true
  },
  "new_test_outcomes_accessed": false,
  "next_gate": "CURRENT_DEEPSEEK_IDENTITY_QUALIFICATION_THEN_ZERO_PROVIDER_STAGE_A_PREFLIGHT",
  "prior_v3": {
    "disposition": "SUPERSEDED_PRE_PROVIDER_BY_SEMANTIC_TRANSFER_V1",
    "new_test_outcomes_accessed": false,
    "path": "generated/e2-r17-selective-mrw-v3-static-audit-20260902.json",
    "provider_calls": 0,
    "sha256": "03db418f29884d9370a5e5916f5f8c81db3bc52b026e83a4b965e9f7e780ede8"
  },
  "provider_calls": 0,
  "schema_version": "1.0",
  "scientific_execution": false,
  "semantic_identification": {
    "binding_streams": 6,
    "equal_dose_stage_b_requires_four_mixed_pools_per_stream": true,
    "family_id_lookup_from_closed_sample_can_route_test": false,
    "family_semantics": {
      "foreign_key_binding": "INSTANCE_BINDING_LOCALIZATION",
      "header_source_binding": "INSTANCE_BINDING_LOCALIZATION",
      "named_region_binding": "INSTANCE_BINDING_LOCALIZATION",
      "normalize_then_rank": "PROCEDURAL_TRANSFORMATION",
      "ordered_filter_rollup": "PROCEDURAL_TRANSFORMATION",
      "reconcile_then_aggregate": "PROCEDURAL_TRANSFORMATION"
    },
    "family_skeletons": {
      "foreign_key_binding": "two_table_join",
      "header_source_binding": "single_table_measure",
      "named_region_binding": "snapshot_table",
      "normalize_then_rank": "single_table_measure",
      "ordered_filter_rollup": "two_table_join",
      "reconcile_then_aggregate": "snapshot_table"
    },
    "matched_skeletons": {
      "single_table_measure": [
        "INSTANCE_BINDING_LOCALIZATION",
        "PROCEDURAL_TRANSFORMATION"
      ],
      "snapshot_table": [
        "INSTANCE_BINDING_LOCALIZATION",
        "PROCEDURAL_TRANSFORMATION"
      ],
      "two_table_join": [
        "INSTANCE_BINDING_LOCALIZATION",
        "PROCEDURAL_TRANSFORMATION"
      ]
    },
    "mechanical_rule_bound": true,
    "old_family_ids_disjoint": true,
    "procedural_streams": 6
  },
  "status": "PASS_SEMANTIC_TRANSFER_V1_ZERO_PROVIDER_STATIC_AUDIT",
  "suite": {
    "dataset_sha256": "5949612d35e308c1ef25534b26f14f925a2a33e2afb5d5145b2358e8baef96cd",
    "heldout_tasks": 18,
    "historical_run_refs": 0,
    "historical_trajectory_refs": 0,
    "metadata_sha256": "5802f35a6fedaa843ba61887ad0a892b8a178b33c20fb6bc4ad0f05e9832476f",
    "old_task_id_overlap": 0,
    "old_xlsx_sha256_overlap": 0,
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-semantic-transfer-v1",
    "split_manifest_sha256": "db911c2c088f3a5df08ffccc922ea8b68a6af31f0f8a1bb4372ce85e62b34033",
    "suite_manifest_sha256": "1d4e048c74839d96bb773859cfecd2d9193e7ed0bcdfd29711dadfbfc8b53717",
    "task_count": 162,
    "update_streams": 12,
    "update_tasks": 96,
    "workbook_pairs_checked": 162
  }
}


===== BOUND ARTIFACT: parent_pre_f0 | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-prospective-heterogeneity-pre-f0-20260902/generated/e2-r17-selective-mrw-semantic-transfer-v1-pre-f0-20260902.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-selective-mrw-semantic-transfer-v1-pre-f0",
  "status": "PRE_F0_SEMANTIC_TRANSFER_STATIC_PASS_AWAIT_PROVIDER_IDENTITY",
  "created_at_utc": "2026-09-02T15:28:40+00:00",
  "closed_parent": {
    "scientific_status": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
    "reuse_in_confirmatory_inference": false,
    "role": "discovery_calibration_only"
  },
  "superseded_same_family_v3": {
    "status": "SUPERSEDED_BEFORE_PROVIDER_EXECUTION",
    "provider_calls": 0,
    "new_test_outcomes_accessed": false,
    "static_audit_path": "generated/e2-r17-selective-mrw-v3-static-audit-20260902.json",
    "static_audit_sha256": "03db418f29884d9370a5e5916f5f8c81db3bc52b026e83a4b965e9f7e780ede8"
  },
  "design": {
    "path": "consultations/e2-r17-selective-mrw-semantic-transfer-v1-20260902.md",
    "sha256": "b12066714d39caddfbe85fcc71dcd94cc970122cec3d24fb1b9725a3c2708bbd",
    "scientific_question": "Can a pre-outcome structural semantic rule select between winner-only and equal-dose rejected-witness learning on completely new failure-family identities?",
    "routing_rule": {
      "PROCEDURAL_TRANSFORMATION": "MRW4",
      "INSTANCE_BINDING_LOCALIZATION": "WIN-C"
    },
    "equal_dose_mixed_pool_replacements_per_stream": 4,
    "old_family_lookup_can_route_new_test": false
  },
  "code": {
    "builders": {
      "path": "research_pipeline/e2_r17_semantic_transfer_builders.py",
      "sha256": "1736f6f7d768cee8f387b31d9249d832e4d221facc239a00df07c3024ec33e07"
    },
    "suite_builder": {
      "path": "scripts/build_e2_r17_semantic_transfer_suite_v1.py",
      "sha256": "a9b29a881b27cce4279f01472d2d7963c0cae13586164192491ef1b6272cb286"
    },
    "static_auditor": {
      "path": "scripts/audit_e2_r17_semantic_transfer_v1_static.py",
      "sha256": "34aa781a8d9188eda104986808d5245ca9e6c2d2d87876dee55e0556d74551eb"
    }
  },
  "suite": {
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-semantic-transfer-v1",
    "suite_manifest_sha256": "1d4e048c74839d96bb773859cfecd2d9193e7ed0bcdfd29711dadfbfc8b53717",
    "split_manifest_sha256": "db911c2c088f3a5df08ffccc922ea8b68a6af31f0f8a1bb4372ce85e62b34033",
    "metadata_sha256": "5802f35a6fedaa843ba61887ad0a892b8a178b33c20fb6bc4ad0f05e9832476f",
    "task_count": 162,
    "update_streams": 12,
    "update_tasks": 96,
    "heldout_tasks": 18,
    "procedural_streams": 6,
    "binding_streams": 6,
    "matched_skeletons": 3,
    "deterministic_regeneration_all_files_equal": true,
    "old_task_id_overlap": 0,
    "old_xlsx_sha256_overlap": 0,
    "historical_run_refs": 0,
    "historical_trajectory_refs": 0
  },
  "static_audit": {
    "path": "generated/e2-r17-selective-mrw-semantic-transfer-v1-static-audit-20260902.json",
    "sha256": "30e2350447b190661c6ed20d40fd9e95d40f81d846a9fd2a172a6ec59d85f3f6",
    "status": "PASS_SEMANTIC_TRANSFER_V1_ZERO_PROVIDER_STATIC_AUDIT",
    "workbook_pairs_checked": 162,
    "provider_calls": 0,
    "scientific_execution": false,
    "new_test_outcomes_accessed": false
  },
  "required_provider_identity": {
    "requested_model": "deepseek-v4-pro",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "thinking": "disabled",
    "provider_retry_limit": 0
  },
  "stage_a": {
    "authorized": false,
    "k": 8,
    "pools": 96,
    "actor_rollouts": 768,
    "updater_calls": 0,
    "heldout_evaluations": 0,
    "support_rule": "all 12 streams must have at least four mixed pools; exactly four mixed pools per passing stream are hash-selected and frozen for MRW4"
  },
  "stage_b": {
    "authorized": false,
    "replicates_per_stream": 8,
    "paired_units": 96,
    "learned_states": 192,
    "heldout_evaluations": 3456,
    "selective_extra_updater_calls": 0,
    "selective_extra_heldout_evaluations": 0
  },
  "confirmatory_decision": {
    "gate_a": "MRW4 > WIN-C over six procedural streams by positive mean, exact one-sided sign-flip p<=0.05, and 95% bootstrap lower bound>0",
    "gate_b": "WIN-C > MRW4 over six binding streams by positive mean of -D, exact one-sided sign-flip p<=0.05, and 95% bootstrap lower bound>0",
    "joint_go": "GO_SELECTIVE_MRW_SEMANTIC_TRANSFER_SUPPORTED only if both gates pass",
    "family_specific_p_values": false,
    "old_parent_outcomes_pooled": false
  },
  "authority": {
    "static_design": true,
    "suite_materialization": true,
    "static_audit": true,
    "current_provider_identity_qualification": true,
    "zero_provider_stage_a_preflight": true,
    "stage_a_provider_execution": false,
    "stage_b_learning_execution": false,
    "heldout_evaluation": false,
    "analyzer": false,
    "second_backbone": false,
    "public_benchmark": false,
    "paper_promotion": false
  },
  "next_gate": "CURRENT_DEEPSEEK_IDENTITY_QUALIFICATION_THEN_ZERO_PROVIDER_STAGE_A_PREFLIGHT"
}


===== BOUND ARTIFACT: semantic_builders | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-prospective-heterogeneity-pre-f0-20260902/research_pipeline/e2_r17_semantic_transfer_builders.py =====
from __future__ import annotations

import random
from typing import Any

from openpyxl import Workbook

from .e2_r17_controlled_suite_schema import answer_range


SEMANTIC_TYPES = ("PROCEDURAL_TRANSFORMATION", "INSTANCE_BINDING_LOCALIZATION")

FAMILY_SPECS: dict[str, dict[str, Any]] = {
    "ordered_filter_rollup": {
        "code": "ofr",
        "semantic_type": "PROCEDURAL_TRANSFORMATION",
        "matched_skeleton": "two_table_join",
        "reusable_transform_steps": 3,
        "binding_candidate_count": 1,
    },
    "foreign_key_binding": {
        "code": "fkb",
        "semantic_type": "INSTANCE_BINDING_LOCALIZATION",
        "matched_skeleton": "two_table_join",
        "reusable_transform_steps": 1,
        "binding_candidate_count": 3,
    },
    "normalize_then_rank": {
        "code": "ntr",
        "semantic_type": "PROCEDURAL_TRANSFORMATION",
        "matched_skeleton": "single_table_measure",
        "reusable_transform_steps": 3,
        "binding_candidate_count": 1,
    },
    "header_source_binding": {
        "code": "hsb",
        "semantic_type": "INSTANCE_BINDING_LOCALIZATION",
        "matched_skeleton": "single_table_measure",
        "reusable_transform_steps": 1,
        "binding_candidate_count": 3,
    },
    "reconcile_then_aggregate": {
        "code": "rta",
        "semantic_type": "PROCEDURAL_TRANSFORMATION",
        "matched_skeleton": "snapshot_table",
        "reusable_transform_steps": 3,
        "binding_candidate_count": 1,
    },
    "named_region_binding": {
        "code": "nrb",
        "semantic_type": "INSTANCE_BINDING_LOCALIZATION",
        "matched_skeleton": "snapshot_table",
        "reusable_transform_steps": 1,
        "binding_candidate_count": 3,
    },
}

FAMILIES = tuple(FAMILY_SPECS)
FAMILY_CODES = {name: str(spec["code"]) for name, spec in FAMILY_SPECS.items()}


def _semantic_expected(family: str, payload: dict[str, Any]) -> dict[str, Any]:
    spec = FAMILY_SPECS[family]
    return {
        **payload,
        "semantic_type": spec["semantic_type"],
        "matched_skeleton": spec["matched_skeleton"],
        "reusable_transform_steps": spec["reusable_transform_steps"],
        "binding_candidate_count": spec["binding_candidate_count"],
    }


def build_ordered_filter_rollup(
    wb: Workbook, rng: random.Random, depth: int, ambiguity: int, task_id: str
) -> tuple[str, str, dict[str, Any]]:
    del task_id
    orders = wb.create_sheet("Orders")
    accounts = wb.create_sheet("Accounts")
    orders.append(["order_id", "account_id", "units", "unit_price", "discount_rate", "status", "unit_price_old"])
    accounts.append(["account_id", "segment", "segment_previous"])
    account_rows = [(f"A{i:02d}", "Core" if i % 2 else "Other") for i in range(1, 9)]
    for key, segment in account_rows:
        accounts.append([key, segment, "Legacy" if ambiguity else "previous"])
    segment_by_account = dict(account_rows)
    retained: list[float] = []
    for i in range(14 + depth * 4):
        account = account_rows[(i * 3 + 1) % len(account_rows)][0]
        units = 1 + i % 5
        price = rng.randint(15, 95)
        discount = (i % 3) * 0.05
        status = "posted" if i % 4 else "void"
        orders.append([f"O{i+1:03d}", account, units, price, discount, status, price + 500])
        keep = status == "posted"
        if depth >= 1:
            keep = keep and segment_by_account[account] == "Core"
        value = float(units * price)
        if depth >= 2:
            value *= 1.0 - discount
        if keep:
            retained.append(round(value, 2))
    result = wb["Result"]
    result["B2"] = round(sum(retained), 2)
    result["B3"] = len(retained)
    result["B4"] = round(sum(retained) / len(retained), 2) if retained else 0.0
    instruction = "Start from Orders, keep only status posted, and compute units * unit_price for retained rows. "
    if depth >= 1:
        instruction += "Join Orders.account_id to Accounts.account_id and additionally keep only segment Core. "
    if depth >= 2:
        instruction += "Before aggregation, apply each retained row's discount_rate as value * (1 - discount_rate). "
    instruction += (
        "Write the materialized retained-value sum to Result!B2, retained row count to Result!B3, and retained-value mean "
        "rounded to 2 decimals to Result!B4. Ignore old/previous columns and save as output.xlsx."
    )
    return instruction, answer_range(4), _semantic_expected("ordered_filter_rollup", {"retained": retained})


def build_foreign_key_binding(
    wb: Workbook, rng: random.Random, depth: int, ambiguity: int, task_id: str
) -> tuple[str, str, dict[str, Any]]:
    del task_id
    ledger = wb.create_sheet("Ledger")
    mapping = wb.create_sheet("AccountMap")
    current_left = ("account_id", "account_code", "ledger_account_key")[ambiguity]
    current_right = ("account_id", "rate_account_code", "current_account_key")[ambiguity]
    legacy_left = ("legacy_id", "legacy_account_id", "account_key_previous")[ambiguity]
    candidate_left = ("candidate_id", "candidate_account_code", "account_key_candidate")[ambiguity]
    legacy_right = ("legacy_map_id", "legacy_rate_account", "rate_key_previous")[ambiguity]
    candidate_right = ("candidate_map_id", "candidate_rate_account", "rate_key_candidate")[ambiguity]
    left_candidates = [current_left, legacy_left, candidate_left]
    right_candidates = [current_right, legacy_right, candidate_right]
    rng.shuffle(left_candidates)
    rng.shuffle(right_candidates)
    ledger.append(["row_id", *left_candidates, "amount", "status"])
    mapping.append([*right_candidates, "multiplier"])
    keys = [f"K{i:02d}" for i in range(1, 7)]
    multipliers = {key: round(0.8 + i * 0.07, 2) for i, key in enumerate(keys)}
    for i, key in enumerate(keys):
        values = {
            current_right: key,
            legacy_right: f"MAP-L{i:02d}",
            candidate_right: f"MAP-C{i:02d}",
        }
        mapping.append([*(values[h] for h in right_candidates), multipliers[key]])
    converted: list[float] = []
    for i in range(10 + depth * 3):
        key = keys[i % len(keys)]
        amount = rng.randint(30, 220)
        status = "active" if i % 4 else "inactive"
        values = {
            current_left: key,
            legacy_left: f"LED-L{(i+2)%len(keys):02d}",
            candidate_left: f"LED-C{(i+3)%len(keys):02d}",
        }
        ledger.append([f"R{i+1:03d}", *(values[h] for h in left_candidates), amount, status])
        if depth == 0 or status == "active":
            converted.append(round(amount * multipliers[key], 2))
    result = wb["Result"]
    result["B2"] = round(sum(converted), 2)
    result["B3"] = len(converted)
    last = 3
    if depth >= 2:
        result["B4"] = max(converted) if converted else 0.0
        last = 4
    instruction = (
        "Identify the authoritative current account identifier in Ledger and bind it to the authoritative current account key "
        "in AccountMap; do not use legacy, previous, or candidate key columns. Multiply Ledger.amount by the matched "
        "AccountMap.multiplier. "
    )
    if depth >= 1:
        instruction += "Use only Ledger rows whose status is active. "
    instruction += "Write the materialized total to Result!B2 and retained row count to Result!B3. "
    if depth >= 2:
        instruction += "Write the maximum converted row amount to Result!B4. "
    instruction += "Save as output.xlsx."
    return instruction, answer_range(last), _semantic_expected(
        "foreign_key_binding",
        {
            "left_key": current_left,
            "right_key": current_right,
            "left_candidate_order": left_candidates,
            "right_candidate_order": right_candidates,
            "converted": converted,
        },
    )


def build_normalize_then_rank(
    wb: Workbook, rng: random.Random, depth: int, ambiguity: int, task_id: str
) -> tuple[str, str, dict[str, Any]]:
    del task_id, ambiguity
    ws = wb.create_sheet("Measures")
    ws.append(["item_id", "raw_amount", "scale", "active_flag", "raw_amount_old"])
    normalized: list[float] = []
    for i in range(9 + depth * 3):
        amount = rng.randint(80, 900)
        scale = (1, 10, 100)[i % 3]
        active = 0 if i % 5 == 0 else 1
        ws.append([f"M{i+1:02d}", amount, scale, active, amount + 1000])
        value = round(amount / scale, 2)
        if depth == 0 or active == 1:
            normalized.append(value)
    selected = list(normalized)
    if depth >= 2:
        selected = sorted(selected, reverse=True)[:3]
    result = wb["Result"]
    result["B2"] = round(sum(selected), 2)
    result["B3"] = max(selected) if selected else 0.0
    result["B4"] = len(selected)
    instruction = "For every Measures row, normalize raw_amount by dividing by scale. "
    if depth >= 1:
        instruction += "Then retain only rows with active_flag = 1. "
    if depth >= 2:
        instruction += "Then keep the three largest normalized values. "
    instruction += (
        "Write the materialized selected-value sum to Result!B2, maximum to Result!B3, and selected count to Result!B4. "
        "Ignore raw_amount_old and save as output.xlsx."
    )
    return instruction, answer_range(4), _semantic_expected("normalize_then_rank", {"selected": selected})


def build_header_source_binding(
    wb: Workbook, rng: random.Random, depth: int, ambiguity: int, task_id: str
) -> tuple[str, str, dict[str, Any]]:
    del task_id
    ws = wb.create_sheet("Metrics")
    authoritative = ("amount", "posted_amount", "recognized_amount")[ambiguity]
    estimate = ("amount_estimate", "posted_amount_estimate", "recognized_amount_estimate")[ambiguity]
    previous = ("amount_previous", "posted_amount_previous", "recognized_amount_previous")[ambiguity]
    amount_candidates = [authoritative, estimate, previous]
    rng.shuffle(amount_candidates)
    ws.append(["row_id", *amount_candidates, "status"])
    values: list[float] = []
    for i in range(10 + depth * 2):
        value = float(rng.randint(15, 180))
        status = "active" if i % 4 else "inactive"
        fields = {authoritative: value, estimate: value + 500, previous: value + 900}
        ws.append([f"H{i+1:02d}", *(fields[h] for h in amount_candidates), status])
        if depth == 0 or status == "active":
            values.append(value)
    result = wb["Result"]
    result["B2"] = round(sum(values), 2)
    result["B3"] = round(sum(values) / len(values), 2) if values else 0.0
    last = 3
    if depth >= 2:
        result["B4"] = sum(1 for value in values if value >= 100)
        last = 4
    instruction = (
        "Use the authoritative current amount field in Metrics, not its estimate or previous counterpart. "
    )
    if depth >= 1:
        instruction += "Use only rows whose status is active. "
    instruction += "Write the materialized amount sum to Result!B2 and arithmetic mean rounded to 2 decimals to Result!B3. "
    if depth >= 2:
        instruction += "Write the count of selected amounts at least 100 to Result!B4. "
    instruction += "Save as output.xlsx."
    return instruction, answer_range(last), _semantic_expected(
        "header_source_binding",
        {"authoritative_header": authoritative, "candidate_order": amount_candidates, "values": values},
    )


def build_reconcile_then_aggregate(
    wb: Workbook, rng: random.Random, depth: int, ambiguity: int, task_id: str
) -> tuple[str, str, dict[str, Any]]:
    del task_id
    snapshot = wb.create_sheet("Snapshot")
    corrections = wb.create_sheet("Corrections")
    snapshot.append(["record_id", "amount", "status", "amount_old"])
    corrections.append(["record_id", "replacement_amount", "replacement_status", "apply_flag", "replacement_amount_old"])
    state: dict[str, tuple[float, str]] = {}
    n = 10 + depth * 2
    for i in range(n):
        rid = f"S{i+1:02d}"
        amount = float(rng.randint(25, 210))
        status = "active" if i % 4 else "inactive"
        snapshot.append([rid, amount, status, amount + 800])
        state[rid] = (amount, status)
    for i in range(0, n, 3):
        rid = f"S{i+1:02d}"
        amount, status = state[rid]
        replacement_amount = amount + 10 + (i % 5)
        replacement_status = "active" if i % 2 == 0 else status
        apply_flag = 1 if i % 6 != 3 else 0
        corrections.append([rid, replacement_amount, replacement_status, apply_flag, replacement_amount + 900])
        if apply_flag == 1:
            state[rid] = (replacement_amount, replacement_status)
    values = list(state.values())
    if depth >= 1:
        values = [row for row in values if row[1] == "active"]
    amounts = [row[0] for row in values]
    if depth >= 2:
        amounts = [value for value in amounts if value >= 80]
    result = wb["Result"]
    result["B2"] = round(sum(amounts), 2)
    result["B3"] = len(amounts)
    result["B4"] = max(amounts) if amounts else 0.0
    instruction = (
        "Start from Snapshot. Apply Corrections rows with apply_flag = 1 by record_id, replacing both amount and status; "
        "ignore correction rows with apply_flag = 0. "
    )
    if depth >= 1:
        instruction += "After reconciliation, retain only active records. "
    if depth >= 2:
        instruction += "Then retain only reconciled amounts at least 80. "
    instruction += (
        "Write the materialized reconciled amount sum to Result!B2, retained record count to Result!B3, and retained maximum "
        "to Result!B4. Ignore old columns and save as output.xlsx."
    )
    return instruction, answer_range(4), _semantic_expected("reconcile_then_aggregate", {"amounts": amounts})


def build_named_region_binding(
    wb: Workbook, rng: random.Random, depth: int, ambiguity: int, task_id: str
) -> tuple[str, str, dict[str, Any]]:
    del task_id
    ws = wb.create_sheet("SnapshotBundle")
    starts = [1, 5, 9]
    if ambiguity == 0:
        region_defs = [
            ("CURRENT_ACTUAL", True),
            ("FORECAST_CANDIDATE", False),
            ("ARCHIVE_PREVIOUS", False),
        ]
    elif ambiguity == 1:
        region_defs = [
            ("AUTHORITATIVE_CURRENT", True),
            ("CURRENT_FORECAST", False),
            ("PREVIOUS_ACTUAL", False),
        ]
    else:
        region_defs = [
            ("FINAL_CURRENT_ACTUAL", True),
            ("FINAL_CANDIDATE", False),
            ("FINAL_PREVIOUS", False),
        ]
    rng.shuffle(region_defs)
    target_values: list[float] = []
    target_label = ""
    for idx, (label, is_target) in enumerate(region_defs):
        start = starts[idx]
        ws.cell(row=1, column=start, value=label)
        ws.cell(row=2, column=start, value="item_id")
        ws.cell(row=2, column=start + 1, value="amount")
        ws.cell(row=2, column=start + 2, value="status")
        values: list[float] = []
        for r in range(7 + depth):
            amount = float(rng.randint(20, 160) + idx * 400)
            status = "active" if r % 3 else "inactive"
            ws.cell(row=3 + r, column=start, value=f"B{idx}{r:02d}")
            ws.cell(row=3 + r, column=start + 1, value=amount)
            ws.cell(row=3 + r, column=start + 2, value=status)
            if depth == 0 or status == "active":
                values.append(amount)
        if is_target:
            target_values = values
            target_label = label
    result = wb["Result"]
    result["B2"] = round(sum(target_values), 2)
    result["B3"] = max(target_values) if target_values else 0.0
    last = 3
    if depth >= 2:
        result["B4"] = len(target_values)
        last = 4
    instruction = (
        "In SnapshotBundle, locate the authoritative current/actual region; do not use forecast, candidate, archive, or previous "
        "regions. Use that region's amount column. "
    )
    if depth >= 1:
        instruction += "Use only rows in that region whose status is active. "
    instruction += "Write the materialized amount sum to Result!B2 and maximum to Result!B3. "
    if depth >= 2:
        instruction += "Write the retained row count to Result!B4. "
    instruction += "Save as output.xlsx."
    return instruction, answer_range(last), _semantic_expected(
        "named_region_binding", {"region_label": target_label, "region_order": [x[0] for x in region_defs], "target_values": target_values}
    )


BUILDERS = {
    "ordered_filter_rollup": build_ordered_filter_rollup,
    "foreign_key_binding": build_foreign_key_binding,
    "normalize_then_rank": build_normalize_then_rank,
    "header_source_binding": build_header_source_binding,
    "reconcile_then_aggregate": build_reconcile_then_aggregate,
    "named_region_binding": build_named_region_binding,
}


===== BOUND ARTIFACT: suite_builder | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-prospective-heterogeneity-pre-f0-20260902/scripts/build_e2_r17_semantic_transfer_suite_v1.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_controlled_suite_schema import (
    DISTRACTOR_COUNTS,
    L9_PROFILES,
    add_distractors,
    answer_cells,
    canonical_sha,
    new_book,
    normalize_xlsx,
    seeded_rng,
    sha256_file,
    write_json,
)
from research_pipeline.e2_r17_semantic_transfer_builders import (
    BUILDERS,
    FAMILIES,
    FAMILY_CODES,
    FAMILY_SPECS,
)

SUITE_ID = "E2-R17-SEMANTIC-TRANSFER-SUITE-V1"
UPDATE_BLOCKS = (14, 15)
HELDOUT_BLOCK = 16


def build_task(root: Path, *, block: int, family: str, profile_index: int, role: str) -> dict[str, Any]:
    depth, distractor_level, ambiguity = L9_PROFILES[profile_index]
    task_id = f"r17-b{block}-{FAMILY_CODES[family]}-p{profile_index}"
    rng = seeded_rng(task_id)
    wb = new_book(task_id)
    distractors = add_distractors(wb, DISTRACTOR_COUNTS[distractor_level], rng, ambiguity)
    instruction, answer_position, expected = BUILDERS[family](wb, rng, depth, ambiguity, task_id)
    task_dir = root / "spreadsheetbench_verified_400" / "spreadsheet" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    init_path = task_dir / f"{task_id}_init.xlsx"
    golden_path = task_dir / f"{task_id}_golden.xlsx"
    expected_values = {f"{s}!{c}": wb[s][c].value for s, c in answer_cells(answer_position)}
    for s, c in answer_cells(answer_position):
        wb[s][c] = None
    wb.save(init_path)
    normalize_xlsx(init_path)
    for key, value in expected_values.items():
        sheet, cell = key.split("!", 1)
        wb[sheet][cell] = value
    wb.save(golden_path)
    normalize_xlsx(golden_path)
    wb.close()
    spec = FAMILY_SPECS[family]
    return {
        "record": {
            "id": task_id,
            "instruction": instruction,
            "spreadsheet_path": f"spreadsheet/{task_id}",
            "answer_position": answer_position,
            "answer_sheet": None,
            "instruction_type": family,
        },
        "metadata": {
            "id": task_id,
            "suite_id": SUITE_ID,
            "block": block,
            "role": role,
            "primary_failure_family": family,
            "semantic_type": spec["semantic_type"],
            "matched_skeleton": spec["matched_skeleton"],
            "reusable_transform_steps": spec["reusable_transform_steps"],
            "binding_candidate_count": spec["binding_candidate_count"],
            "profile_index": profile_index,
            "procedure_depth_level": depth,
            "distractor_level": distractor_level,
            "distractor_count": DISTRACTOR_COUNTS[distractor_level],
            "schema_ambiguity_level": ambiguity,
            "distractor_sheets": distractors,
            "answer_position": answer_position,
            "expected": expected,
            "golden_answer_cells": expected_values,
        },
        "init": init_path,
        "golden": golden_path,
    }


def manifest_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "suite_manifest.json":
            rows.append(
                {
                    "path": str(path.relative_to(root)),
                    "size": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    return rows


def _all_xlsx_hashes(root: Path) -> set[str]:
    base = root / "spreadsheetbench_verified_400" / "spreadsheet"
    if not base.is_dir():
        return set()
    return {sha256_file(path) for path in base.rglob("*.xlsx")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--old-suite-root", type=Path, action="append", default=[])
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    root = args.output_root
    if root.exists():
        if not args.overwrite:
            raise FileExistsError(root)
        shutil.rmtree(root)
    (root / "spreadsheetbench_verified_400").mkdir(parents=True)

    records: list[dict[str, Any]] = []
    metadata: list[dict[str, Any]] = []
    built: list[dict[str, Any]] = []
    for block in UPDATE_BLOCKS:
        for family in FAMILIES:
            for profile in range(len(L9_PROFILES)):
                item = build_task(root, block=block, family=family, profile_index=profile, role="semantic_transfer_update")
                records.append(item["record"])
                metadata.append(item["metadata"])
                built.append(item)
    for family in FAMILIES:
        for profile in range(len(L9_PROFILES)):
            item = build_task(root, block=HELDOUT_BLOCK, family=family, profile_index=profile, role="semantic_transfer_heldout")
            records.append(item["record"])
            metadata.append(item["metadata"])
            built.append(item)

    records.sort(key=lambda row: row["id"])
    metadata.sort(key=lambda row: row["id"])
    write_json(root / "spreadsheetbench_verified_400" / "dataset.json", records)
    write_json(root / "r17_semantic_transfer_metadata.json", metadata)
    by_id = {row["id"]: row for row in metadata}

    streams: dict[str, list[str]] = {}
    reserve: dict[str, list[str]] = {}
    for family in FAMILIES:
        code = FAMILY_CODES[family]
        family_reserve: list[str] = []
        for stream_index, block in enumerate(UPDATE_BLOCKS):
            ids = sorted(
                row["id"]
                for row in metadata
                if row["block"] == block and row["primary_failure_family"] == family
            )
            if len(ids) != 9:
                raise RuntimeError(f"unexpected update block shape: {family} b{block} {len(ids)}")
            order = sorted(ids, key=lambda task_id: hashlib.sha256(f"semantic-transfer-v1|{task_id}".encode()).hexdigest())
            streams[f"st-{code}-{stream_index:02d}"] = order[:8]
            family_reserve.extend(order[8:])
        reserve[family] = sorted(family_reserve)

    heldout: list[str] = []
    heldout_reserve: list[str] = []
    for family in FAMILIES:
        ids = sorted(
            row["id"]
            for row in metadata
            if row["block"] == HELDOUT_BLOCK and row["primary_failure_family"] == family
        )
        valid: list[tuple[str, ...]] = []
        for combo in itertools.combinations(ids, 3):
            rows = [by_id[task_id] for task_id in combo]
            if (
                len({row["procedure_depth_level"] for row in rows}) == 3
                and len({row["distractor_level"] for row in rows}) == 3
                and len({row["schema_ambiguity_level"] for row in rows}) == 3
            ):
                valid.append(combo)
        if not valid:
            raise RuntimeError(f"no orthogonal heldout triple for {family}")
        chosen = min(
            valid,
            key=lambda combo: hashlib.sha256((f"semantic-transfer-heldout-v1|{family}|" + "|".join(combo)).encode()).hexdigest(),
        )
        heldout.extend(chosen)
        heldout_reserve.extend(sorted(set(ids) - set(chosen)))
    heldout = sorted(heldout)

    semantic_streams: dict[str, list[str]] = {"PROCEDURAL_TRANSFORMATION": [], "INSTANCE_BINDING_LOCALIZATION": []}
    skeleton_streams: dict[str, list[str]] = {}
    for stream_id, task_ids in streams.items():
        rows = [by_id[task_id] for task_id in task_ids]
        families = {row["primary_failure_family"] for row in rows}
        semantic = {row["semantic_type"] for row in rows}
        skeleton = {row["matched_skeleton"] for row in rows}
        if len(families) != 1 or len(semantic) != 1 or len(skeleton) != 1:
            raise RuntimeError(f"non-homogeneous stream: {stream_id}")
        semantic_value = next(iter(semantic))
        skeleton_value = next(iter(skeleton))
        semantic_streams[semantic_value].append(stream_id)
        skeleton_streams.setdefault(skeleton_value, []).append(stream_id)

    split = {
        "schema_version": "1.0",
        "suite_id": SUITE_ID,
        "selection_is_outcome_blind": True,
        "selection_algorithm": "fixed SHA256 ordering over generated task IDs; no model outcomes",
        "semantic_routing_rule": {
            "PROCEDURAL_TRANSFORMATION": "MRW",
            "INSTANCE_BINDING_LOCALIZATION": "WIN-C",
            "mechanical_definition": (
                "PROCEDURAL_TRANSFORMATION iff reusable_transform_steps>=2 and binding_candidate_count==1; "
                "INSTANCE_BINDING_LOCALIZATION iff binding_candidate_count>=2 and reusable_transform_steps<=1"
            ),
        },
        "family_specs": FAMILY_SPECS,
        "update_streams": streams,
        "streams_by_semantic_type": {key: sorted(value) for key, value in semantic_streams.items()},
        "streams_by_matched_skeleton": {key: sorted(value) for key, value in skeleton_streams.items()},
        "update_reserve_integrity_only": reserve,
        "common_heldout_probe": heldout,
        "heldout_reserve_integrity_only": sorted(heldout_reserve),
        "rules": {
            "old_family_identity_lookup_cannot_route_new_families": True,
            "all_update_families_new_relative_to_closed_experiment": True,
            "all_scientific_task_ids_new": True,
            "heldout_never_fed_to_updater": True,
            "semantic_type_frozen_before_provider_execution": True,
            "reserve_never_replaces_bad_outcome_or_model_failure": True,
        },
    }
    write_json(root / "r17_semantic_transfer_split_manifest.json", split)
    # Compatibility aliases for the frozen generic actor. These files only
    # rename schema fields; they point to the exact same 96 update tasks and
    # 18 heldout tasks and do not alter any task or treatment semantics.
    compat_split = dict(split)
    compat_split["development"] = []
    compat_split["e1_update_streams"] = streams
    compat_split["e1_common_heldout_probe"] = heldout
    write_json(root / "r17_split_manifest.json", compat_split)
    write_json(root / "r17_controlled_metadata.json", metadata)

    new_ids = {row["id"] for row in metadata}
    new_hashes = {sha256_file(item[key]) for item in built for key in ("init", "golden")}
    old_id_overlap: dict[str, int] = {}
    old_content_overlap: dict[str, int] = {}
    for old_root in args.old_suite_root:
        meta_candidates = list(old_root.glob("*metadata*.json"))
        old_ids: set[str] = set()
        for path in meta_candidates:
            try:
                payload = json.loads(path.read_text())
            except Exception:
                continue
            if isinstance(payload, list):
                old_ids.update(str(row.get("id")) for row in payload if isinstance(row, dict) and row.get("id"))
        old_hashes = _all_xlsx_hashes(old_root)
        label = str(old_root)
        old_id_overlap[label] = len(new_ids & old_ids)
        old_content_overlap[label] = len(new_hashes & old_hashes)
        if old_id_overlap[label] or old_content_overlap[label]:
            raise RuntimeError(
                f"old-suite overlap with {old_root}: ids={old_id_overlap[label]} xlsx={old_content_overlap[label]}"
            )

    update_ids = {task_id for task_ids in streams.values() for task_id in task_ids}
    heldout_ids = set(heldout)
    if update_ids & heldout_ids:
        raise RuntimeError("update/heldout overlap")
    if len(streams) != 12 or any(len(task_ids) != 8 for task_ids in streams.values()):
        raise RuntimeError("stream shape mismatch")
    if len(update_ids) != 96 or len(heldout_ids) != 18:
        raise RuntimeError("scientific task cardinality mismatch")
    if any(len(value) != 6 for value in semantic_streams.values()):
        raise RuntimeError(f"semantic stream balance mismatch: {semantic_streams}")
    if any(len(value) != 4 for value in skeleton_streams.values()):
        raise RuntimeError(f"matched skeleton balance mismatch: {skeleton_streams}")

    files = manifest_rows(root)
    manifest = {
        "schema_version": "1.0",
        "suite_id": SUITE_ID,
        "status": "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_SUITE_MATERIALIZATION",
        "provider_calls": 0,
        "scientific_outcomes_accessed": False,
        "task_count": len(records),
        "families": list(FAMILIES),
        "family_specs": FAMILY_SPECS,
        "update_blocks": list(UPDATE_BLOCKS),
        "heldout_block": HELDOUT_BLOCK,
        "update_streams": 12,
        "update_tasks": 96,
        "heldout_tasks": 18,
        "semantic_stream_counts": {key: len(value) for key, value in semantic_streams.items()},
        "matched_skeleton_stream_counts": {key: len(value) for key, value in skeleton_streams.items()},
        "split_manifest_sha256": sha256_file(root / "r17_semantic_transfer_split_manifest.json"),
        "metadata_sha256": sha256_file(root / "r17_semantic_transfer_metadata.json"),
        "actor_compat_split_manifest_sha256": sha256_file(root / "r17_split_manifest.json"),
        "actor_compat_metadata_sha256": sha256_file(root / "r17_controlled_metadata.json"),
        "dataset_sha256": canonical_sha(files),
        "old_suite_disjointness": {
            "task_id_overlap": old_id_overlap,
            "xlsx_sha256_overlap": old_content_overlap,
        },
        "files": files,
    }
    write_json(root / "suite_manifest.json", manifest)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "task_count": manifest["task_count"],
                "update_streams": manifest["update_streams"],
                "update_tasks": manifest["update_tasks"],
                "heldout_tasks": manifest["heldout_tasks"],
                "semantic_stream_counts": manifest["semantic_stream_counts"],
                "matched_skeleton_stream_counts": manifest["matched_skeleton_stream_counts"],
                "old_suite_disjointness": manifest["old_suite_disjointness"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: stage_a_preparer | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-prospective-heterogeneity-pre-f0-20260902/scripts/prepare_e2_r17_semantic_transfer_stage_a_v1.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ACTOR = ROOT / "scripts/run_e2_r17_actor_pool.py"
EXPECTED_ACTOR_SHA = "20a81fbe06f3839cd17babfdb021407368493da61610bca33aae33df8d31ec14"
EXPECTED_SUITE_SHA = "a7ddee258ddc22cee3efe22bad44046faa20ba9d49762c98a66a843c2c9533a3"
EXPECTED_COMPAT_SPLIT_SHA = "6ac03fd07391b2671e2e3cecd975395adff6c9fbd622751195a5a46b6a39af1c"
EXPECTED_COMPAT_META_SHA = "5802f35a6fedaa843ba61887ad0a892b8a178b33c20fb6bc4ad0f05e9832476f"
EXPECTED_MINDMEMOS_COMMIT = "90491828726e1540442b17cd445d0308d0b8093c"
EXPECTED_INITIAL_SKILL_SHA = "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb"
EXPECTED_RUNTIME_FREEZE_SHA = "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e"
EXPECTED_RUNTIME_QUAL_SHA = "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b"
EXPECTED_RUNTIME_COMPAT_STATUS = "PASS_SEMANTIC_TRANSFER_V1_RUNTIME_COMPAT_R1"


def req(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def import_actor_module() -> Any:
    spec = importlib.util.spec_from_file_location("e2_r17_actor_stage_a_preflight", ACTOR)
    req(spec is not None and spec.loader is not None, "cannot load generic actor module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_scope_guards(actor: Any, split: dict[str, Any], all_tasks: list[str], heldout: list[str]) -> dict[str, bool]:
    synthetic = {
        "status": "AUTHORIZED_E1",
        "authority": {"scientific_experiment": True, "e1_a": True, "e1_b": False},
        "contract_sha256": "0" * 64,
        "execution_scope": {
            "allowed_modes": ["e1"],
            "allowed_task_ids": all_tasks,
            "exact_k": 8,
            "allow_noninitial_skill": False,
        },
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(synthetic, handle)
        auth_path = Path(handle.name)
    try:
        actor.validate_authority(mode="e1", authorization=auth_path, task_ids=all_tasks[:8], split=split, k=8)
        wrong_k_rejected = False
        try:
            actor.validate_authority(mode="e1", authorization=auth_path, task_ids=all_tasks[:8], split=split, k=4)
        except RuntimeError:
            wrong_k_rejected = True
        heldout_rejected = False
        try:
            actor.validate_authority(mode="e1", authorization=auth_path, task_ids=[heldout[0]], split=split, k=8)
        except RuntimeError:
            heldout_rejected = True
        wrong_mode_rejected = False
        try:
            actor.validate_authority(mode="e0", authorization=auth_path, task_ids=all_tasks[:8], split=split, k=8)
        except RuntimeError:
            wrong_mode_rejected = True
        return {
            "valid_e1_k8_scope_passes": True,
            "wrong_k_rejected": wrong_k_rejected,
            "heldout_task_rejected": heldout_rejected,
            "wrong_mode_rejected": wrong_mode_rejected,
        }
    finally:
        auth_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-compat-audit", type=Path, required=True)
    parser.add_argument("--suite-root", type=Path, required=True)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--mindmemos-root", type=Path, required=True)
    parser.add_argument("--runtime-venv", type=Path, required=True)
    parser.add_argument("--runtime-freeze", type=Path, required=True)
    parser.add_argument("--runtime-qualification", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--contract-output", type=Path, required=True)
    parser.add_argument("--preflight-output", type=Path, required=True)
    args = parser.parse_args()

    req(not args.contract_output.exists(), "Stage-A contract output already exists")
    req(not args.preflight_output.exists(), "Stage-A preflight output already exists")
    req(not args.run_root.exists(), "Stage-A run root must not exist before authorization")

    audit = load(args.runtime_compat_audit)
    identity = load(args.identity)
    suite_manifest_path = args.suite_root / "suite_manifest.json"
    split_path = args.suite_root / "r17_split_manifest.json"
    meta_path = args.suite_root / "r17_controlled_metadata.json"
    split = load(split_path)
    suite_manifest = load(suite_manifest_path)
    runtime_q = load(args.runtime_qualification)
    initial_skill = args.mindmemos_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md"
    runtime_python = args.runtime_venv / "bin/python"

    for path in (
        args.runtime_compat_audit,
        args.identity,
        suite_manifest_path,
        split_path,
        meta_path,
        ACTOR,
        initial_skill,
        runtime_python,
        args.runtime_freeze,
        args.runtime_qualification,
    ):
        req(path.is_file(), f"missing Stage-A bound artifact: {path}")

    req(audit["status"] == EXPECTED_RUNTIME_COMPAT_STATUS, "runtime-compat audit not passing")
    req(audit["provider_calls_scientific"] == 0 and audit["new_test_outcomes_accessed"] is False, "runtime-compat audit crossed science boundary")
    req(sha(ACTOR) == EXPECTED_ACTOR_SHA, "generic actor SHA drift")
    req(sha(suite_manifest_path) == EXPECTED_SUITE_SHA, "suite manifest drift")
    req(sha(split_path) == EXPECTED_COMPAT_SPLIT_SHA, "compat split drift")
    req(sha(meta_path) == EXPECTED_COMPAT_META_SHA, "compat metadata drift")
    req(sha(args.runtime_freeze) == EXPECTED_RUNTIME_FREEZE_SHA, "runtime freeze drift")
    req(sha(args.runtime_qualification) == EXPECTED_RUNTIME_QUAL_SHA, "runtime qualification drift")
    req(sha(initial_skill) == EXPECTED_INITIAL_SKILL_SHA, "initial skill drift")
    req(runtime_q["status"] == "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2", "runtime qualification not passing")
    req(runtime_q["venv_root"] == str(args.runtime_venv), "runtime venv drift")

    head = subprocess.run(
        ["git", "-C", str(args.mindmemos_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    req(head == EXPECTED_MINDMEMOS_COMMIT, "MindMemOS commit drift")

    req(identity["status"] == "PASS" and len(identity["models"]) == 1, "identity qualification invalid")
    model = identity["models"][0]
    req(model["requested_model"] == "deepseek-v4-pro", "requested model drift")
    req(model["resolved_model"] == "deepseek-v4-pro-ga-260813", "exact resolved model drift")
    req(model["provider_retry_limit"] == 0 and model["thinking_requested"] == "disabled", "identity flags drift")

    streams = {str(k): list(map(str, v)) for k, v in split["e1_update_streams"].items()}
    heldout = list(map(str, split["e1_common_heldout_probe"]))
    all_tasks = [task for tasks in streams.values() for task in tasks]
    req(len(streams) == 12 and all(len(tasks) == 8 for tasks in streams.values()), "Stage-A stream shape drift")
    req(len(all_tasks) == 96 and len(set(all_tasks)) == 96, "Stage-A task uniqueness drift")
    req(len(heldout) == 18 and set(all_tasks).isdisjoint(heldout), "Stage-A heldout separation drift")
    req(suite_manifest["provider_calls"] == 0 and suite_manifest["scientific_outcomes_accessed"] is False, "suite crossed provider/outcome boundary")

    actor_help = subprocess.run([str(runtime_python), str(ACTOR), "--help"], capture_output=True, text=True, check=False)
    req(actor_help.returncode == 0, "generic actor cannot import/parse under frozen runtime")
    actor = import_actor_module()
    guard_checks = check_scope_guards(actor, split, all_tasks, heldout)
    req(all(guard_checks.values()), f"actor execution-scope guard preflight failed: {guard_checks}")

    runtime_smoke = subprocess.run(
        [
            str(runtime_python),
            "-c",
            "from mindmemos_eval.skills.agents import ReactAgentFactory; from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv; import openpyxl",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    req(runtime_smoke.returncode == 0, "Stage-A frozen runtime smoke failed")

    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    contract = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-selective-mrw-semantic-transfer-v1-stage-a-contract",
        "created_at_utc": created_at,
        "status": "FROZEN_SEMANTIC_TRANSFER_V1_STAGE_A_PENDING_REVIEW",
        "scientific_role": "search-pool acquisition and equal-dose support qualification only",
        "runtime_compat_audit": {"path": str(args.runtime_compat_audit), "sha256": sha(args.runtime_compat_audit)},
        "model_identity": {
            "path": str(args.identity),
            "sha256": sha(args.identity),
            "requested": "deepseek-v4-pro",
            "resolved": "deepseek-v4-pro-ga-260813",
        },
        "suite": {
            "root": str(args.suite_root),
            "suite_manifest_sha256": sha(suite_manifest_path),
            "split_manifest_sha256": sha(split_path),
            "metadata_sha256": sha(meta_path),
            "streams": list(streams.keys()),
            "allowed_task_ids": all_tasks,
            "heldout_task_ids_forbidden": heldout,
        },
        "mindmemos": {
            "root": str(args.mindmemos_root),
            "commit": head,
            "initial_skill_path": str(initial_skill),
            "initial_skill_sha256": sha(initial_skill),
        },
        "runtime": {
            "venv_root": str(args.runtime_venv),
            "python_executable": str(runtime_python),
            "freeze_path": str(args.runtime_freeze),
            "freeze_sha256": sha(args.runtime_freeze),
            "qualification_path": str(args.runtime_qualification),
            "qualification_sha256": sha(args.runtime_qualification),
        },
        "bound_code": {
            "actor": {"path": "scripts/run_e2_r17_actor_pool.py", "sha256": sha(ACTOR)},
        },
        "actor": {
            "requested_model": "deepseek-v4-pro",
            "resolved_model": "deepseek-v4-pro-ga-260813",
            "k": 8,
            "prefix_ks": [1, 2, 4, 8],
            "temperature": 0,
            "thinking": "disabled",
            "provider_retry_limit": 0,
            "max_turns": 10,
            "max_output_tokens": 8192,
            "concurrency": 1,
        },
        "budget": {
            "actor_rollouts": 768,
            "max_provider_calls": 7680,
            "provider_calls_per_rollout_limit": 10,
        },
        "equal_dose_support": {
            "required_mixed_pools_per_stream": 4,
            "streams_required": 12,
            "treated_mixed_pools_per_stream": 4,
            "treated_pool_selection": "lowest SHA256(semantic-transfer-mrw4-v1|stream_id|task_id) among mixed pools",
            "stage_b_treated_pool_ids_must_be_frozen_before_updater": True,
            "failure_status": "HOLD_SEMANTIC_TRANSFER_INSUFFICIENT_EQUAL_DOSE_SUPPORT",
        },
        "run_root": str(args.run_root),
        "exactly_once": {
            "completed_rollout_replay": False,
            "automatic_retry": False,
            "replacement_sampling": False,
            "resume_requires_separate_adjudication": True,
        },
        "authority": {
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "updater": False,
            "heldout_evaluation": False,
            "analyzer": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
        },
        "partial_effect_read": False,
        "scientific_scores_read": False,
    }
    write_json(args.contract_output, contract)
    contract_sha = sha(args.contract_output)

    preflight = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-selective-mrw-semantic-transfer-v1-stage-a-zero-provider-preflight",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_ZERO_PROVIDER_SEMANTIC_TRANSFER_STAGE_A_ACTUAL_PATH_PREFLIGHT",
        "contract_path": str(args.contract_output),
        "contract_sha256": contract_sha,
        "provider_calls": 0,
        "scientific_execution": False,
        "new_test_outcomes_accessed": False,
        "run_root_exists": args.run_root.exists(),
        "actor_help_under_frozen_runtime_pass": True,
        "runtime_import_smoke_pass": True,
        "execution_scope_guard_checks": guard_checks,
        "stream_count": 12,
        "task_count": 96,
        "heldout_forbidden_count": 18,
        "exact_k": 8,
        "max_provider_calls": 7680,
        "updater_authority": False,
        "heldout_evaluation_authority": False,
        "authority": {
            "mint_stage_a_authorization": False,
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "paper_promotion": False,
        },
        "next_gate": "INDEPENDENT_PREEXECUTION_REVIEW_BEFORE_SINGLE_USE_STAGE_A_AUTHORIZATION",
    }
    req(preflight["run_root_exists"] is False, "preflight unexpectedly created run root")
    write_json(args.preflight_output, preflight)
    print(json.dumps({"contract_status": contract["status"], "contract_sha256": contract_sha, "preflight_status": preflight["status"], "scope_guards": guard_checks, "next_gate": preflight["next_gate"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: generic_actor | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-prospective-heterogeneity-pre-f0-20260902/scripts/run_e2_r17_actor_pool.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.ark_provider import ArkSettings
from research_pipeline.config import load_env_file
from research_pipeline.e2_r17_actor_pool import (
    ActorRolloutConfig,
    atomic_json,
    file_sha256,
    freeze_nested_pools,
    run_actor_rollout,
)
from research_pipeline.e2_r17_ark_plan_react import ArkPlanReactLLM, PLAN_BASE_URL
from research_pipeline.e2_r17_provider_budget import ProviderBudgetLedger


def load_mindmemos(root: Path) -> tuple[Any, Any]:
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    source_roots = [root / "src/mindmemos_eval", root / "src/mindmemos_sdk", root / "src/mindmemos"]
    for source in reversed(source_roots):
        if str(source) not in sys.path:
            sys.path.insert(0, str(source))
    from mindmemos_eval.skills.agents import ReactAgentFactory
    from mindmemos_eval.skills.envs.spreadsheetbench.env import SpreadsheetBenchEnv

    return ReactAgentFactory, SpreadsheetBenchEnv


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def task_ids_from_args(args: argparse.Namespace, split: dict[str, Any]) -> list[str]:
    if args.task_id:
        return [str(value) for value in args.task_id]
    if args.stream_id:
        for key in ("e1_update_streams", "e3_future_streams"):
            if args.stream_id in split.get(key, {}):
                return [str(value) for value in split[key][args.stream_id]]
        raise ValueError(f"unknown stream id: {args.stream_id}")
    if args.lane:
        value = split.get(args.lane)
        if not isinstance(value, list):
            raise ValueError(f"lane is not a task list: {args.lane}")
        return [str(item) for item in value]
    raise ValueError("one of --task-id, --stream-id, or --lane is required")


def validate_authority(
    *,
    mode: str,
    authorization: Path | None,
    task_ids: list[str],
    split: dict[str, Any],
    k: int,
) -> tuple[dict[str, Any] | None, str | None]:
    development = {str(item) for item in split.get("development") or []}
    if mode == "protocol_smoke":
        if not set(task_ids).issubset(development):
            raise RuntimeError("protocol smoke may access development tasks only")
        if authorization is not None:
            raise RuntimeError("protocol smoke must not borrow scientific authorization")
        return None, None
    if authorization is None:
        raise RuntimeError("scientific actor execution requires --authorization")
    payload = json.loads(authorization.read_text(encoding="utf-8"))
    if payload.get("status") not in {"AUTHORIZED_E0", "AUTHORIZED_E1", "AUTHORIZED_PUBLIC_EXTERNALITY"}:
        raise RuntimeError("authorization artifact does not authorize actor execution")
    if not payload.get("authority", {}).get("scientific_experiment"):
        raise RuntimeError("authorization has zero scientific authority")

    # New scoped authorizations fail closed. Historical artifacts without an
    # execution_scope remain readable/replayable, but any E1-A/E1-B tranche
    # minted after this guard must bind the exact mode, task IDs and K it grants.
    scope = payload.get("execution_scope")
    if scope is not None:
        allowed_modes = {str(value) for value in scope.get("allowed_modes") or []}
        if not allowed_modes or mode not in allowed_modes:
            raise RuntimeError(f"authorization does not allow mode={mode}")
        allowed_tasks = {str(value) for value in scope.get("allowed_task_ids") or []}
        if not allowed_tasks or not set(task_ids).issubset(allowed_tasks):
            raise RuntimeError("authorization does not allow one or more requested task IDs")
        exact_k = scope.get("exact_k")
        if exact_k is not None and int(exact_k) != int(k):
            raise RuntimeError(f"authorization requires exact K={exact_k}, requested K={k}")
        if scope.get("allow_noninitial_skill") is False and payload.get("authority", {}).get("e1_b"):
            raise RuntimeError("authorization scope is internally inconsistent about non-initial skills")
    return payload, sha256(authorization)


async def main_async(args: argparse.Namespace) -> dict[str, Any]:
    ReactAgentFactory, SpreadsheetBenchEnv = load_mindmemos(args.mindmemos_root)
    load_env_file(args.env_file)
    settings = ArkSettings.from_env(required=True)
    if settings.base_url.rstrip("/") != PLAN_BASE_URL:
        raise RuntimeError("E2-R17 actor refuses any non-Ark-Plan route")
    settings = ArkSettings(
        api_key=settings.api_key,
        base_url=settings.base_url,
        default_model=settings.default_model,
        timeout_seconds=300,
        max_retries=0,
    )
    identity = json.loads(args.identity.read_text(encoding="utf-8"))
    if identity.get("status") != "PASS_CURRENT_REVIEW_TRANCHE":
        raise RuntimeError("current model identity adjudication is not passing")
    model_row = identity["requested_and_resolved"][args.model]
    requested_model = str(model_row["requested"])
    required_resolved = str(model_row["resolved"])

    split_path = args.suite_root / "r17_split_manifest.json"
    split = json.loads(split_path.read_text(encoding="utf-8"))
    task_ids = task_ids_from_args(args, split)
    authorization_payload, authorization_sha = validate_authority(
        mode=args.mode,
        authorization=args.authorization,
        task_ids=task_ids,
        split=split,
        k=args.k,
    )
    contract_sha = (
        str(authorization_payload.get("contract_sha256") or "")
        if authorization_payload is not None
        else None
    )
    provider_budget_ledger: ProviderBudgetLedger | None = None
    budget_args_present = any(
        value is not None
        for value in (args.provider_budget_ledger, args.provider_total_call_limit, args.provider_per_unit_call_limit)
    )
    if budget_args_present:
        if authorization_payload is None or not authorization_sha or not contract_sha:
            raise RuntimeError("provider budget ledger is allowed only for a bound scientific authorization")
        if args.provider_budget_ledger is None or args.provider_total_call_limit is None or args.provider_per_unit_call_limit is None:
            raise RuntimeError("provider budget ledger path, total limit and per-unit limit must be supplied together")
        provider_budget_ledger = ProviderBudgetLedger(
            path=args.provider_budget_ledger,
            contract_sha256=contract_sha,
            authorization_sha256=authorization_sha,
            total_limit=int(args.provider_total_call_limit),
            per_unit_limit=int(args.provider_per_unit_call_limit),
            allow_create=not args.provider_budget_ledger.exists(),
        )
    if authorization_payload is not None:
        scope = authorization_payload.get("execution_scope") or {}
        provider_budget_scope = scope.get("provider_budget") or {}
        if provider_budget_scope.get("required") is True:
            if provider_budget_ledger is None:
                raise RuntimeError("authorization requires a fail-closed provider budget ledger")
            if int(provider_budget_scope.get("total_limit")) != int(args.provider_total_call_limit):
                raise RuntimeError("authorization provider total-call limit drift")
            if int(provider_budget_scope.get("per_unit_limit")) != int(args.provider_per_unit_call_limit):
                raise RuntimeError("authorization provider per-unit limit drift")
        expected_resolved = scope.get("required_resolved_model")
        if expected_resolved and str(expected_resolved) != required_resolved:
            raise RuntimeError("authorization resolved-model identity drift")
        expected_identity_sha = scope.get("identity_artifact_sha256")
        if expected_identity_sha and sha256(args.identity) != expected_identity_sha:
            raise RuntimeError("authorization model-identity artifact drift")
        if scope.get("max_turns") is not None and int(scope["max_turns"]) != int(args.max_turns):
            raise RuntimeError("authorization max_turns drift")
        if scope.get("max_output_tokens") is not None and int(scope["max_output_tokens"]) != int(args.max_output_tokens):
            raise RuntimeError("authorization max_output_tokens drift")
    metadata_rows = json.loads((args.suite_root / "r17_controlled_metadata.json").read_text(encoding="utf-8"))
    metadata = {str(row["id"]): row for row in metadata_rows}
    missing = [task_id for task_id in task_ids if task_id not in metadata]
    if missing:
        raise RuntimeError(f"tasks absent from controlled metadata: {missing}")

    env = SpreadsheetBenchEnv(args.suite_root, args.run_root)
    cases = {case.id: case for case in env.load_cases("all")}
    mindmemos_commit = __import__("subprocess").check_output(
        ["git", "-C", str(args.mindmemos_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if authorization_payload is not None and mindmemos_commit != authorization_payload.get("mindmemos_commit"):
        raise RuntimeError("MindMemOS commit drifted after scientific authorization")
    if authorization_payload is not None:
        scope = authorization_payload.get("execution_scope") or {}
        expected_suite_sha = scope.get("suite_manifest_sha256")
        expected_split_sha = scope.get("split_manifest_sha256")
        if expected_suite_sha and file_sha256(args.suite_root / "suite_manifest.json") != expected_suite_sha:
            raise RuntimeError("suite manifest drifted after scientific authorization")
        if expected_split_sha and file_sha256(split_path) != expected_split_sha:
            raise RuntimeError("split manifest drifted after scientific authorization")

    default_skill_source = args.mindmemos_root / "resources/skill_evolve/spreadsheetbench_init_skill/xlsx"
    skill_source = (args.skill_source or default_skill_source).resolve()
    skill_md = skill_source / "SKILL.md"
    if not skill_md.is_file():
        raise RuntimeError(f"skill source does not contain SKILL.md: {skill_source}")
    skill_sha = file_sha256(skill_md)
    if authorization_payload is not None:
        required_skill_sha = (authorization_payload.get("execution_scope") or {}).get("required_skill_pre_sha256")
        if required_skill_sha and skill_sha != required_skill_sha:
            raise RuntimeError("skill pre-state drifted after scientific authorization")
    updater_receipt_sha: str | None = None
    if skill_source != default_skill_source.resolve():
        if args.mode != "e1" or args.updater_receipt is None:
            raise RuntimeError("a non-initial skill is allowed only for E1 evaluation with --updater-receipt")
        updater_receipt = json.loads(args.updater_receipt.read_text(encoding="utf-8"))
        updater_receipt_sha = sha256(args.updater_receipt)
        if updater_receipt.get("status") != "COMPLETED":
            raise RuntimeError("updater receipt is not completed")
        if Path(updater_receipt.get("skill_post_path") or "").resolve() != skill_md.resolve():
            raise RuntimeError("updater receipt does not bind the supplied skill path")
        if updater_receipt.get("skill_post_sha256") != skill_sha:
            raise RuntimeError("updater receipt does not bind the supplied skill content")
        if updater_receipt.get("contract_sha256") != contract_sha:
            raise RuntimeError("updater receipt contract SHA differs from evaluation authorization")
        if updater_receipt.get("authorization_sha256") != authorization_sha:
            raise RuntimeError("updater receipt authorization SHA differs from evaluation authorization")
    elif args.updater_receipt is not None:
        raise RuntimeError("--updater-receipt must not be supplied for the frozen initial skill")
    evaluator_sources = [
        args.mindmemos_root / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/evaluator.py",
        args.mindmemos_root / "src/mindmemos_eval/mindmemos_eval/skills/envs/spreadsheetbench/env.py",
    ]
    semaphore = asyncio.Semaphore(max(1, args.concurrency))

    async def run_unit(task_id: str, rollout_index: int):
        async with semaphore:
            adapter = ArkPlanReactLLM(
                settings=settings,
                requested_model=requested_model,
                required_resolved_model=required_resolved,
                max_output_tokens=args.max_output_tokens,
                temperature=0,
                thinking="disabled",
                provider_budget_ledger=provider_budget_ledger,
                provider_budget_unit_id=(f"{task_id}/rollout_{rollout_index}" if provider_budget_ledger is not None else None),
            )
            factory = ReactAgentFactory(
                adapter,
                max_turns=args.max_turns,
                skill_sources=[skill_source],
                python_path=sys.executable,
            )
            config = ActorRolloutConfig(
                requested_model=requested_model,
                required_resolved_model=required_resolved,
                max_turns=args.max_turns,
                skill_source=str(skill_source),
                skill_pre_sha256=skill_sha,
                failure_family=str(metadata[task_id]["primary_failure_family"]),
                experiment_mode=args.mode,
                contract_sha256=contract_sha,
                authorization_sha256=authorization_sha,
            )
            return await run_actor_rollout(
                env=env,
                case=cases[task_id],
                rollout_index=rollout_index,
                agent_factory=factory,
                adapter=adapter,
                config=config,
                evaluator_sources=evaluator_sources,
            )

    task_rows: list[dict[str, Any]] = []
    prefix_ks = tuple(int(value) for value in args.prefix_ks.split(",") if value.strip())
    for task_id in task_ids:
        refs = await asyncio.gather(*(run_unit(task_id, index) for index in range(args.k)))
        task_dir = args.run_root / "cases" / task_id
        pools = freeze_nested_pools(task_dir=task_dir, trajectories=refs, prefix_ks=prefix_ks)
        task_rows.append(
            {
                "task_id": task_id,
                "failure_family": metadata[task_id]["primary_failure_family"],
                "scores": [ref.score for ref in refs],
                "provider_calls": sum(
                    len(json.loads(Path(ref.trajectory_path).read_text(encoding="utf-8"))["adapter_receipts"])
                    for ref in refs
                ),
                "pools": {
                    str(k): {
                        "pool_id": pool.pool_id,
                        "acting_success": pool.acting_success,
                        "precommitted_success": pool.precommitted_success,
                        "rescue_event": pool.rescue_event,
                        "winner_index": pool.winner.rollout_index,
                    }
                    for k, pool in pools.items()
                },
            }
        )
    return {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-actor-pool-run-summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "COMPLETED",
        "mode": args.mode,
        "suite_root": str(args.suite_root),
        "suite_manifest_sha256": file_sha256(args.suite_root / "suite_manifest.json"),
        "split_manifest_sha256": file_sha256(split_path),
        "mindmemos_root": str(args.mindmemos_root),
        "mindmemos_commit": mindmemos_commit,
        "identity_artifact": str(args.identity),
        "identity_artifact_sha256": sha256(args.identity),
        "requested_model": requested_model,
        "resolved_model": required_resolved,
        "provider_retry_limit": 0,
        "thinking": "disabled",
        "k": args.k,
        "prefix_ks": list(prefix_ks),
        "max_turns": args.max_turns,
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "skill_source": str(skill_source),
        "skill_pre_sha256": skill_sha,
        "updater_receipt_path": str(args.updater_receipt) if args.updater_receipt else None,
        "updater_receipt_sha256": updater_receipt_sha,
        "contract_sha256": contract_sha,
        "authorization_sha256": authorization_sha,
        "provider_budget": provider_budget_ledger.snapshot().to_dict() if provider_budget_ledger is not None else None,
        "tasks": task_rows,
        "scientific_outcome": args.mode != "protocol_smoke",
        "authority": {
            "paper_promotion": False,
            "submission": False,
        },
        "private_credentials_included": False,
        "raw_response_ids_included": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--suite-root", type=Path, required=True)
    parser.add_argument("--mindmemos-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--identity", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--skill-source", type=Path)
    parser.add_argument("--updater-receipt", type=Path)
    parser.add_argument("--mode", choices=("protocol_smoke", "e0", "e1", "public_externality"), required=True)
    parser.add_argument("--model", choices=("deepseek-v4-pro",), default="deepseek-v4-pro")
    parser.add_argument("--task-id", action="append")
    parser.add_argument("--lane")
    parser.add_argument("--stream-id")
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--prefix-ks", default="1,2,4,8")
    parser.add_argument("--max-turns", type=int, default=10)
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--provider-budget-ledger", type=Path)
    parser.add_argument("--provider-total-call-limit", type=int)
    parser.add_argument("--provider-per-unit-call-limit", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.k < 1 or args.k > 8:
        raise SystemExit("K must be in 1..8")
    summary = asyncio.run(main_async(args))
    atomic_json(args.output, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: semantic_builder_tests | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-prospective-heterogeneity-pre-f0-20260902/research_pipeline/test_e2_r17_semantic_transfer_builders.py =====
from __future__ import annotations

import unittest
from collections import Counter

from .e2_r17_controlled_suite_schema import (
    DISTRACTOR_COUNTS,
    L9_PROFILES,
    add_distractors,
    answer_cells,
    new_book,
    seeded_rng,
)
from .e2_r17_semantic_transfer_builders import BUILDERS, FAMILY_SPECS


class SemanticTransferBuilderTest(unittest.TestCase):
    def _build(self, family: str, profile: int):
        depth, distractor_level, ambiguity = L9_PROFILES[profile]
        task_id = f"semantic-transfer-test-{family}-{profile}"
        wb = new_book(task_id)
        rng = seeded_rng(task_id)
        add_distractors(wb, DISTRACTOR_COUNTS[distractor_level], rng, ambiguity)
        instruction, answer_position, expected = BUILDERS[family](wb, rng, depth, ambiguity, task_id)
        return wb, instruction, answer_position, expected

    def test_all_profiles_build_and_obey_semantic_rule(self) -> None:
        for family, spec in FAMILY_SPECS.items():
            for profile in range(len(L9_PROFILES)):
                with self.subTest(family=family, profile=profile):
                    wb, instruction, answer_position, expected = self._build(family, profile)
                    try:
                        self.assertTrue(instruction)
                        self.assertTrue(answer_cells(answer_position))
                        self.assertEqual(spec["semantic_type"], expected["semantic_type"])
                        self.assertEqual(spec["matched_skeleton"], expected["matched_skeleton"])
                        if spec["semantic_type"] == "PROCEDURAL_TRANSFORMATION":
                            self.assertGreaterEqual(int(expected["reusable_transform_steps"]), 2)
                            self.assertEqual(1, int(expected["binding_candidate_count"]))
                        else:
                            self.assertLessEqual(int(expected["reusable_transform_steps"]), 1)
                            self.assertGreaterEqual(int(expected["binding_candidate_count"]), 2)
                    finally:
                        wb.close()

    def test_each_skeleton_crosses_both_semantic_types(self) -> None:
        skeletons: dict[str, set[str]] = {}
        for spec in FAMILY_SPECS.values():
            skeletons.setdefault(str(spec["matched_skeleton"]), set()).add(str(spec["semantic_type"]))
        self.assertEqual(3, len(skeletons))
        for semantic_types in skeletons.values():
            self.assertEqual({"PROCEDURAL_TRANSFORMATION", "INSTANCE_BINDING_LOCALIZATION"}, semantic_types)

    def test_binding_shortcuts_do_not_have_fixed_position(self) -> None:
        positions = {
            "foreign_key_binding_left": Counter(),
            "foreign_key_binding_right": Counter(),
            "header_source_binding": Counter(),
            "named_region_binding": Counter(),
        }
        for family in ("foreign_key_binding", "header_source_binding", "named_region_binding"):
            for profile in range(len(L9_PROFILES)):
                wb, _, _, expected = self._build(family, profile)
                try:
                    if family == "foreign_key_binding":
                        positions["foreign_key_binding_left"][expected["left_candidate_order"].index(expected["left_key"])] += 1
                        positions["foreign_key_binding_right"][expected["right_candidate_order"].index(expected["right_key"])] += 1
                    elif family == "header_source_binding":
                        positions["header_source_binding"][expected["candidate_order"].index(expected["authoritative_header"])] += 1
                    else:
                        positions["named_region_binding"][expected["region_order"].index(expected["region_label"])] += 1
                finally:
                    wb.close()
        for label, counts in positions.items():
            with self.subTest(label=label):
                self.assertGreaterEqual(len(counts), 2)


if __name__ == "__main__":
    unittest.main()


BOUND DOSSIER END
