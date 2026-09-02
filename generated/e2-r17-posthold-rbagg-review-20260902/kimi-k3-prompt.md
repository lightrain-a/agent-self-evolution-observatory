You are an independent adversarial protocol reviewer for a POST-HOLD secondary diagnostic in E2-R17 Search-Projection Censoring. You are a reviewer only. You receive no new RB-AGG scientific effectiveness outcome. This consultation has zero experiment, updater, heldout, paper-promotion, public-benchmark, or submission authority.

Reviewer endpoint: kimi-k3
Exact RB-AGG Pre-F0 adjudication SHA-256: d44270cb73529b87d2f71a68825ced93ee615102dee6b6cef4c969ba5ae6699b

Historical fact that MUST remain immutable: the complete DeepSeek parent result is `HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`. RB-AGG is not allowed to rescue it, append samples to it, or recompute the parent p-value.

The pre-outcome V3 design had already named `RB_AGG` as a ReasoningBank collision diagnostic that could run regardless of MRW GO/HOLD after a semantic runtime pilot. However the final closeout correctly disabled any AUTOMATIC RB-AGG rescue. This new child is therefore independently preregistered and may at most diagnose whether richer same-pool aggregation collides with the minimal failed-witness story.

Audit the ACTUAL bound code and first-party source. Be especially hostile to semantic spoofing.

1. PARENT BOUNDARY: Does the new protocol unambiguously preserve the parent HOLD for every possible RB result? Is this truly a secondary collision diagnostic rather than disguised sample-size rescue?

2. PREDECLARED ROLE: Given the old V3 plan, is it legitimate to revisit RB-AGG now as a separately preregistered post-HOLD diagnostic, provided it never changes the parent decision? Or should post-outcome timing alone STOP the diagnostic?

3. REASONINGBANK SEMANTICS: The pinned ReasoningBank `PARALLEL_SI` output is a set of Memory Items directly used as memory in the source system. The child explicitly labels itself `ReasoningBank-style`, NOT source-faithful. Is the proposed use of literal PARALLEL_SI over all eight frozen trajectories with 512-token/source cap, success/failure labels, temperature .7, strict 1–5 item parser and exact source provenance a defensible semantic adapter? Flag any material deviation that makes the label misleading.

4. SESSION SCORE: MindMemOS scored patch prompts say each summary has a trajectory evaluation score and higher score means the session went better. The child does NOT score the generated Memory Items. Instead it defines the originating record as the complete frozen K=8 search session and sets score=`acting_success`, the actual best-of-K user-facing session outcome. Is that truthful or is it still a semantic misrepresentation requiring STOP/repair?

5. SCORE EQUIVALENCE: Zero-provider preflight proved on 96/96 pools that the RB session score equals WIN's selected winner trajectory score under the frozen binary selector. Does this remove score-label confounding for RB-vs-WIN-D? Explain whether any residual score semantics asymmetry remains.

6. 1:1 PROVENANCE: First-party `SkillTraceSummary` is documented as 1:1 with an originating add trace. The adapter creates one explicit synthetic K=8 SEARCH-SESSION add record and one matching precomputed summary. It proves the summary exists before `SkillEvolver.evolve`, and forbids direct trajectory summarization of that synthetic source. Actual-path preflight on in-memory Qdrant confirms 8 precomputed summaries, 0 new trajectory-summary calls, exactly one evolved version. Is this a scientifically honest boundary substitution, or does it spoof first-party MindMemOS semantics enough to invalidate the diagnostic?

7. SAME PATCH PATH: After precomputed summaries exist, RB uses the same first-party `PROPOSE_PATCH_SCORED_SYSTEM`, same patch parser, same config, initial skill, batch size 8, temperature 0, correction rule and no rewrite. Is the diagnostic adequately isolated at the summary/evidence stage?

8. SUMMARY-STAGE SUBSTITUTION: Parent WIN nominally makes 8 first-party trajectory-summary calls then propose+apply. RB substitutes 8 PARALLEL_SI calls for those summary calls, then the same propose+apply. Nominal provider call count therefore remains 10 per one updater realization, though RB input/token content is richer and aggregation temperature differs. Is this acceptable for a METHOD/COLLISION diagnostic if token/compute differences are reported, or is a matched-token control mandatory before any result is interpretable?

9. CONTEMPORANEOUS CONTROL: The child refuses to compare new RB only against historical WIN-C and instead preregisters a fresh concurrent WIN-D, with same pools, initial skill, heldout, 4 updater replicates, model identity, and interleaved execution. Does this adequately close wall-clock/provider drift?

10. AGGREGATION STOCHASTICITY: The proposed full diagnostic generates one RB aggregate per task exactly once, freezes it, and reuses the same eight aggregate summaries across four updater replicates. This isolates updater stochasticity but not aggregation stochasticity. Is that the right scientific unit for this secondary method diagnostic, or must aggregation also be replicated? If repair is required, specify it BEFORE provider pilot.

11. INFERENCE: Full diagnostic would compare fresh RB-AGG vs fresh WIN-D at the same 12 stream units, four replicates/stream and same 18 heldout tasks. One exact stream-level sign-flip contrast plus paired bootstrap and TOST is predeclared. Historical MRW/WIN outcomes do not enter the child primary statistic. Is this statistically and causally acceptable as secondary collision evidence?

12. PILOT SCOPE: Review may at most allow a separately authorized fixed-stream `e1-agj-00` semantic provider pilot: 8 aggregation calls + one updater realization (2 nominal, hard max 3) = 10 nominal / 11 hard max, zero heldout, no effectiveness inference, pilot skill permanently excluded. Is that scope minimal and sufficient?

13. FAILURE DISCIPLINE: Aggregator parse is strict, retry=0, malformed output fail-closes, model identity is exact, no hidden retry, no provider ambiguity tolerated. Pilot failure cannot be automatically retried. Does the code/protocol preserve this?

PASS only if there are no P0/P1 blockers and `remaining_blockers` is exactly []. Even PASS MUST set `full_diagnostic_recommendation=HOLD`, `paper_claim_authority=false`, and only recommend a SEPARATE single-stream semantic-pilot authorization. Do not authorize that pilot directly.

Return exactly one JSON object and no markdown using this schema:
{
  "pref0_sha256_acknowledged": "",
  "verdict": "PASS_TO_SEPARATE_SINGLE_STREAM_SEMANTIC_PILOT|REVISE_RBAGG_BEFORE_PROVIDER|STOP_RBAGG_DIAGNOSTIC",
  "parent_hold_boundary_assessment": "",
  "predeclared_diagnostic_role_assessment": "",
  "reasoningbank_semantic_boundary_assessment": "",
  "session_score_semantics_assessment": "",
  "win_score_equivalence_assessment": "",
  "add_record_summary_provenance_assessment": "",
  "mindmemos_scored_path_assessment": "",
  "summary_stage_substitution_assessment": "",
  "fresh_win_d_control_assessment": "",
  "aggregation_reuse_across_replicates_assessment": "",
  "provider_budget_and_compute_assessment": "",
  "secondary_inference_assessment": "",
  "semantic_pilot_scope_assessment": "",
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
  "semantic_pilot_recommendation": "ALLOW_SEPARATE_SINGLE_STREAM_SEMANTIC_PILOT_AUTHORIZATION|HOLD|STOP",
  "full_diagnostic_recommendation": "HOLD|STOP",
  "parent_scientific_status_must_remain": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
  "paper_claim_authority": false,
  "single_sentence_verdict": ""
}
Set `pref0_sha256_acknowledged` exactly to the SHA above.

BOUND DOSSIER START

===== BOUND ARTIFACT: pref0_adjudication | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-posthold-rbagg-diagnostic-20260902/generated/e2-r17-posthold-rbagg-diagnostic-pref0-adjudication-20260902.json =====
{
  "artifact_type": "e2-r17-posthold-rbagg-diagnostic-pref0-adjudication",
  "authority": {
    "heldout_evaluation": false,
    "paper_promotion": false,
    "provider_io": false,
    "public_benchmark": false,
    "rbagg_full_diagnostic": false,
    "scientific_experiment": false,
    "second_backbone": false,
    "semantic_provider_pilot": false
  },
  "created_at_utc": "2026-09-02T04:17:00+00:00",
  "design": {
    "protocol_path": "consultations/e2-r17-posthold-rbagg-diagnostic-protocol-20260902.md",
    "protocol_sha256": "97151b5f9bbf7c3132bab3d25b78d98d709fd4e7375158b40cd74f54dca8c248",
    "role": "secondary published-collision diagnostic; never a parent-HOLD rescue"
  },
  "full_diagnostic_candidate": {
    "arms": [
      "fresh_contemporaneous_win_d",
      "fresh_reasoningbank_style_rb_agg"
    ],
    "heldout_evaluations_per_arm": 864,
    "historical_parent_outcomes_in_primary_statistic": false,
    "k8_search_rerun": false,
    "learned_states_per_arm": 48,
    "paired_replicates_per_stream": 4,
    "parent_hold_reclassification": false,
    "stream_level_units": 12
  },
  "parent": {
    "closeout_path": "generated/e2-r17-deepseek-v2-final-scientific-closeout-20260902.json",
    "closeout_sha256": "0c4d2e485db09046c6f34147a2ae4ab808f0ccc67e95179fadf76319106848ca",
    "primary_status": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
    "status_is_immutable": true,
    "v3_plan_path": "generated/e2-r17-experiment-plan-v3-20260828.json",
    "v3_plan_sha256": "b1a0224117f161ead9fccefa2c22a0f01dfa1d9e72ca1e98107418f21e3e04c5"
  },
  "semantic_adapter": {
    "add_record_summary_cardinality": "1:1 per frozen K=8 task session",
    "aggregate_is_not_single_trajectory": true,
    "aggregation_replaces_first_party_trajectory_summary_stage": true,
    "direct_mindmemos_trajectory_summary_forbidden": true,
    "mindmemos_patch_prompt": "PROPOSE_PATCH_SCORED_SYSTEM",
    "mindmemos_patch_prompt_parser_config_changed": false,
    "rb_output_role": "precomputed search-session SkillTraceSummary",
    "reasoningbank_source_faithful_reproduction": false,
    "score_semantics": "frozen K=8 search-session acting_success",
    "score_vector_exact_to_win": true
  },
  "semantic_preflight": {
    "path": "generated/e2-r17-posthold-rbagg-zero-provider-semantic-adapter-preflight-20260902.json",
    "sha256": "ddbd8fbb8d89ce31870f85ed97f844ee61414277005f8c4fad97c5f1a50e1e7f",
    "status": "PASS_RBAGG_ZERO_PROVIDER_SEMANTIC_ADAPTER_PREFLIGHT",
    "pool_count": 96,
    "score_equal_to_win": "96/96",
    "provider_calls": 0
  },
  "actual_path_preflight": {
    "path": "generated/e2-r17-posthold-rbagg-zero-provider-actual-path-preflight-v2-20260902.json",
    "sha256": "1987b002a88442ae98e87990ca896e4614ca4b2ae13fe9bcb5a1e118fddf5bbc",
    "status": "PASS_RBAGG_ZERO_PROVIDER_ACTUAL_MINDMEMOS_PATH",
    "precomputed_summaries": 8,
    "first_party_trajectory_summary_calls": 0,
    "fake_patch_interface_calls": 2,
    "provider_calls": 0,
    "heldout_evaluations": 0
  },
  "superseded_preflight": {
    "path": "generated/e2-r17-posthold-rbagg-zero-provider-actual-path-v1-assertion-blocker-20260902.json",
    "sha256": "7c20a658f07c8992ba1a6d2f1cb588012a545286c6213bf1ea181bb2b78e6e80",
    "status": "SUPERSEDED_IMPLEMENTATION_ASSERTION_TOO_STRICT_ZERO_PROVIDER",
    "provider_calls": 0
  },
  "bound_code": {
    "semantic_adapter": {
      "path": "research_pipeline/e2_r17_rbagg_posthold.py",
      "sha256": "17652c2db62a355ab44a485f8d358803846b9ec02ee66461aa048d6612aa81cf"
    },
    "mindmemos_adapter": {
      "path": "research_pipeline/e2_r17_rbagg_mindmemos_updater.py",
      "sha256": "7d9ef1247ac2f0d7175b82efe195ae33932ff6b896bcfbc1062646469ca2b043"
    },
    "tests": {
      "path": "research_pipeline/test_e2_r17_rbagg_posthold.py",
      "sha256": "4e661833d1dd1f5d585d4f4dcbe5944bd923dd566eb9676a974bfc2040d7b4b1"
    },
    "semantic_preflight_runner": {
      "path": "scripts/preflight_e2_r17_posthold_rbagg_semantic_adapter.py",
      "sha256": "78ebcc9ded84a16612bd3eaf0be4aa2b6ec393908a72008816e52ce0085b9665"
    },
    "actual_path_preflight_runner": {
      "path": "scripts/preflight_e2_r17_posthold_rbagg_actual_path.py",
      "sha256": "38b4998559796a9ad51cde56ec7291112d3ea5cf8c493f700b9a21a4c10e0384"
    }
  },
  "provider_pilot_candidate": {
    "fixed_stream": "e1-agj-00",
    "aggregation_calls": 8,
    "mindmemos_nominal_calls": 2,
    "mindmemos_hard_max_calls": 3,
    "total_nominal_calls": 10,
    "total_hard_max_calls": 11,
    "heldout_evaluations": 0,
    "pilot_skill_scientific_inclusion": false,
    "automatic_retry": false
  },
  "required_next_gate": [
    "independent DeepSeek reviewer PASS or explicit repair",
    "independent Kimi reviewer PASS or explicit repair",
    "both reviewers acknowledge exact protocol/adjudication SHA and keep parent HOLD immutable",
    "fresh review-only provider calls may not grant semantic-pilot authority by themselves",
    "after review PASS create a separate SHA-bound semantic-pilot contract and authorization"
  ],
  "schema_version": "1.0",
  "status": "PREF0_RBAGG_REVIEW_REQUIRED_ZERO_PROVIDER_AUTHORITY",
  "tests": {
    "rbagg_unit_tests": "10/10 PASS including existing ReasoningBank-style tests",
    "diff_check": "PASS"
  }
}


===== BOUND ARTIFACT: protocol | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-posthold-rbagg-diagnostic-20260902/consultations/e2-r17-posthold-rbagg-diagnostic-protocol-20260902.md =====
# E2-R17 Post-HOLD RB-AGG Collision Diagnostic

## Status

`PREF0_PROTOCOL_READY_FOR_INDEPENDENT_REVIEW_ZERO_PROVIDER_AUTHORITY`

The parent scientific result remains immutable:

`HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS`

This child is a **secondary published-collision diagnostic**. It cannot rescue, enlarge, or recompute the parent MRW-vs-WIN confirmatory sample.

## 1. Question

The parent MRW intervention exposed one deterministic failed witness on mixed pools and produced a positive but inconclusive result. The pre-outcome V3 design already declared a ReasoningBank-style same-pool aggregation diagnostic.

The child asks:

> On the exact same frozen K=8 search pools, does a richer ReasoningBank-style aggregation of all success/failure trajectories produce better future frozen-skill utility than a fresh contemporaneous winner-only control?

This is not an official ReasoningBank reproduction. It is a collision diagnostic on the controlled spreadsheet substrate.

## 2. Parent evidence is not reopened

Parent closeout:

`generated/e2-r17-deepseek-v2-final-scientific-closeout-20260902.json`

Parent status stays HOLD for every possible child outcome.

Forbidden:

- append RB-AGG to the old MRW sample;
- rerun MRW;
- recompute the parent p-value;
- call RB-AGG a rescue;
- promote paper claims automatically;
- open Qwen/GPT/public benchmark automatically.

## 3. Frozen source pools

Use exactly the already-frozen E1-A pools:

- 12 streams;
- 8 update tasks per stream;
- 96 K=8 pools;
- 768 immutable source trajectories;
- 78/96 mixed pools;
- no actor/search rerun.

Pool SHAs are inherited from:

`generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json`.

## 4. RB aggregation semantics

For each task pool exactly once:

1. verify all eight source trajectory SHAs;
2. render each trajectory with the already-frozen 512-token cap;
3. bind its deterministic verifier label `SUCCESS`/`FAILURE`;
4. use the literal `PARALLEL_SI` prompt from ReasoningBank commit `ed80611788292ea739f1effd31f16c53823b8a0d`;
5. one aggregation provider call, temperature `0.7`, max output `1024`, retry limit `0`;
6. strict parser accepts only 1–5 contiguous official `# Memory Item i / ## Title / ## Description / ## Content` blocks;
7. malformed/empty output is fail-closed; no parse-correction provider retry;
8. freeze the normalized Markdown and all source provenance before updater execution.

The aggregation model is **not source-faithful ReasoningBank**. For this controlled collision diagnostic it must be the same freshly qualified DeepSeek route/model family used by the MindMemOS updater, with thinking disabled. The exact resolved model is contract-bound before provider I/O.

## 5. Semantic adapter into MindMemOS

ReasoningBank Memory Items are never represented as a single trajectory.

Each task creates:

- one explicit synthetic **K=8 search-session add record**;
- one 1:1 **precomputed SkillTraceSummary** whose text is the normalized RB Memory Items.

The matching precomputed summary must exist before `SkillEvolver.evolve` is entered. Direct MindMemOS trajectory summarization of the synthetic search-session record is forbidden.

### Score semantics

The summary score is the frozen K=8 search-session `acting_success`.

This is semantically truthful: it is the actual user-facing outcome of that search session. It is also exactly equal, task-by-task, to the WIN winner trajectory score under the frozen binary best-of-K selector.

The zero-provider semantic preflight proved:

`RB session score == WIN selected winner score` on `96/96` pools.

Therefore the scored-patch label vector is not an extra source of advantage for RB-AGG.

## 6. MindMemOS update semantics

After the eight RB summaries for one stream are frozen:

- same initial `SKILL.md` SHA as parent;
- first-party `SkillEvolver`;
- `min_aggregate=max_aggregate=8`;
- `use_trajectory_score=true`;
- same `PROPOSE_PATCH_SCORED_SYSTEM`;
- same apply-patch parser;
- same `rewrite_skill=false`;
- same `temperature=0` for MindMemOS patch calls;
- same retry limit `0`;
- at most one explicit parse/apply correction, exactly as Repair2;
- no first-party trajectory-summary calls, because PARALLEL_SI replaces that summary stage.

Nominal provider-call accounting per stream:

- 8 RB aggregation calls;
- 4 updater replicates × (1 propose + 1 apply) = 8 MindMemOS calls;
- total nominal = 16.

Hard maximum with one visible apply correction in every replicate:

- 8 aggregation + 4 × 3 updater calls = 20 per stream;
- 240 calls across all 12 streams before heldout evaluation.

The parent WIN updater also used nominally 10 calls per replicate (8 trajectory summaries + propose + apply). RB-AGG substitutes its 8 aggregation calls for the first-party per-trajectory summary stage; it does not stack a second updater pipeline.

## 7. Why a fresh WIN-D control is mandatory

Do **not** compare new RB-AGG states only to historical WIN-C. Provider/runtime behavior may drift with wall-clock time even under the same model identity.

The full diagnostic, if later authorized, must run contemporaneously:

- `WIN-D`: fresh winner-only updates using the already-frozen parent evidence renderer and first-party updater;
- `RB-AGG`: fresh same-pool aggregation updates;
- same stream/replicate schedule;
- hash-balanced arm order;
- same initial skill;
- same heldout evaluator;
- same resolved model identity.

Historical WIN-C/MRW results do not enter the child primary statistic.

## 8. Full diagnostic scientific unit — only if later authorized

Per arm:

- 12 streams;
- 4 fresh updater replicates per stream;
- 48 learned states;
- common 18 parent heldout tasks per state;
- K=1 evaluator;
- 864 heldout evaluations per arm.

Two-arm child total:

- 96 fresh learned states;
- 1728 heldout evaluations;
- zero new K=8 search trajectories.

For stream `s`:

`D_s^RB = mean_r [ J_{s,r}(RB-AGG) - J_{s,r}(WIN-D) ]`.

Independent units are the 12 stream effects.

## 9. Secondary diagnostic inference

Predeclare one RB-vs-WIN-D contrast only:

- exact one-sided sign-flip over `2^12` stream effects;
- alpha `0.05`;
- mean `D_s^RB > 0`;
- 95% paired-stream bootstrap lower bound > 0 for a strong positive diagnostic;
- paired TOST with `epsilon=1/18` reported to distinguish practical equivalence from unresolved noise.

This is **secondary collision evidence**, not the parent primary test.

Possible interpretations:

- RB superior: broader same-pool aggregation can have persistent-learning value where the minimal witness result was inconclusive; the paper must narrow away from a simple MRW method claim and acknowledge stronger ReasoningBank-style collision.
- RB practically equivalent: no evidence that this richer aggregation baseline improves the controlled substrate; parent MRW HOLD remains HOLD.
- RB harmful: aggregation itself can degrade persistent learning on this substrate; parent HOLD remains HOLD.
- neither superiority nor equivalence: diagnostic remains unresolved.

No outcome permits parent GO.

## 10. Zero-provider qualification already passed

Semantic adapter preflight:

`generated/e2-r17-posthold-rbagg-zero-provider-semantic-adapter-preflight-20260902.json`

- 96/96 pools verified;
- 78 mixed reproduced;
- score vector exact to WIN on 96/96;
- scored proposer on 12/12 streams;
- provider calls 0.

Actual first-party path preflight v2:

`generated/e2-r17-posthold-rbagg-zero-provider-actual-path-preflight-v2-20260902.json`

- fixed pilot stream `e1-agj-00`;
- 8 search-session add records;
- 8 precomputed summaries;
- 0 first-party trajectory-summary calls;
- real in-memory Qdrant + real `SkillEvolver`;
- fake propose/apply exactly 2 calls;
- real patch parser exercised;
- one evolved version;
- provider calls 0;
- heldout evaluations 0.

V1 actual-path preflight was superseded only because an over-strict byte-equality assertion did not account for first-party `.strip()` removing one trailing newline. Its root remains preserved.

## 11. Next gate: independent protocol review

Before any provider I/O, reviewers must answer:

1. Is session-level `acting_success` a truthful score for a multi-trajectory search-session summary?
2. Does exact score equality to WIN remove score-label confounding?
3. Is inserting PARALLEL_SI at the precomputed-summary boundary faithful enough to call this `ReasoningBank-style`, while explicitly not calling it source-faithful?
4. Does the 1:1 synthetic add-record/precomputed-summary construction preserve MindMemOS provenance rather than spoof a trajectory?
5. Is a fresh contemporaneous WIN-D control sufficient to close post-HOLD wall-clock drift?
6. Is one frozen RB aggregation per task, reused across four updater replicates, the correct way to isolate updater stochasticity?
7. Are call/token differences properly classified as part of the broader aggregation method rather than a matched-compute causal arm?
8. Does the interpretation strictly prevent RB-AGG from rescuing the parent HOLD?

Only after review PASS may a single fixed-stream **semantic provider pilot** be separately authorized.

## 12. Semantic provider pilot, if authorized

Fixed stream: `e1-agj-00` by lexicographic predeclared stream order.

Exactly:

- 8 PARALLEL_SI provider calls;
- strict parse of all eight outputs;
- one MindMemOS updater replicate from those eight summaries;
- nominal 2 MindMemOS calls, hard max 3 with one visible apply correction;
- total nominal 10, hard max 11 provider calls;
- zero heldout evaluation;
- zero skill-effect inference.

The pilot output skill is quarantine-only and can never enter the full diagnostic sample.

Pass requires:

- 8/8 aggregation outputs parse;
- exact required resolved model on every call;
- retry limit 0 and no hidden retry;
- 0 ambiguous provider responses;
- 8 precomputed summaries consumed;
- 0 MindMemOS trajectory-summary calls;
- exactly one evolved skill version;
- updater calls within frozen 2/3 bound;
- no heldout task touched.

Failure stops and requires explicit adjudication; no auto retry.


===== BOUND ARTIFACT: semantic_preflight | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-posthold-rbagg-diagnostic-20260902/generated/e2-r17-posthold-rbagg-zero-provider-semantic-adapter-preflight-20260902.json =====
{
  "aggregator_provider_calls": 0,
  "artifact_type": "e2-r17-posthold-rbagg-zero-provider-semantic-adapter-preflight",
  "authority": {
    "heldout_evaluation": false,
    "paper_promotion": false,
    "provider_io": false,
    "rbagg_full_diagnostic": false,
    "semantic_provider_pilot": false
  },
  "created_at_utc": "2026-09-02T04:07:33+00:00",
  "fixture_only_fields": {
    "memory_items_output_is_synthetic_fixture": true,
    "purpose": "strict parser/add-summary/scored-patch structural validation only; no semantic effectiveness or provider output was observed"
  },
  "heldout_evaluations": 0,
  "mindmemos_provider_calls": 0,
  "mixed_pool_count": 78,
  "next_gate": "INDEPENDENT_REVIEW_OF_SESSION_SCORE_SEMANTICS_AND_PRECOMPUTED_SUMMARY_ADAPTER_BEFORE_ANY_PROVIDER_IO",
  "parent_closeout_path": "generated/e2-r17-deepseek-v2-final-scientific-closeout-20260902.json",
  "parent_closeout_sha256": "0c4d2e485db09046c6f34147a2ae4ab808f0ccc67e95179fadf76319106848ca",
  "parent_pool_support_path": "generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json",
  "parent_pool_support_sha256": "b2c611285c20377d77af7ea62448c6fee0d5973cd657687f6dde7f7fce6be6d7",
  "parent_primary_status": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
  "parent_rbagg_rescue_authority": false,
  "parent_status_changed": false,
  "pool_count": 96,
  "pool_root": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-1-20260828",
  "provider_calls": 0,
  "rb_prompt_input_tokens_total_over_96_pools": 443486,
  "reasoningbank_aggregator_max_output_tokens": 1024,
  "reasoningbank_aggregator_temperature": 0.7,
  "reasoningbank_commit": "ed80611788292ea739f1effd31f16c53823b8a0d",
  "reasoningbank_per_trajectory_cap_tokens": 512,
  "reasoningbank_prompt": "PARALLEL_SI",
  "schema_version": "1.0",
  "scientific_effectiveness_evaluated": false,
  "semantic_adapter": {
    "aggregate_role": "precomputed task-level K=8 search-session SkillTraceSummary; never represented as a single rollout trajectory",
    "aggregation_provider_layer_is_extra_and_separately_accounted": true,
    "direct_trajectory_summarization_of_synthetic_session_record": "forbidden",
    "mindmemos_patch_prompt_parser_config_changed": false,
    "mindmemos_patch_proposer": "PROPOSE_PATCH_SCORED_SYSTEM",
    "reasoningbank_source_faithful_label": false,
    "score_semantics": "frozen best-of-K search-session acting_success",
    "score_vector_exactly_equal_to_win_selected_winner_scores": true,
    "source_record_cardinality": "one explicit search-session add record per task, one-to-one with its precomputed summary"
  },
  "status": "PASS_RBAGG_ZERO_PROVIDER_SEMANTIC_ADAPTER_PREFLIGHT",
  "stream_count": 12,
  "stream_receipts": [
    {
      "mindmemos_scored_path": true,
      "score_vector": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ],
      "score_vector_sha256": "91d86f0162c9c8c39e2750833a71b6a366e5a532e386a7520086ab811c70c990",
      "scored_patch_system_sha256": "b1bc66660aef255923dab7a83570b8c566326a3dd2517a7d9a87419de2c2fc82",
      "scored_patch_user_fixture_sha256": "797d854fa6b1b5aaf6197f1ec451bcdf62ae5b044aad4a3319305e9962b4d613",
      "stream_id": "e1-agj-00",
      "summary_count": 8,
      "task_ids": [
        "r17-b2-agj-p2",
        "r17-b2-agj-p5",
        "r17-b2-agj-p7",
        "r17-b3-agj-p0",
        "r17-b2-agj-p3",
        "r17-b3-agj-p3",
        "r17-b2-agj-p8",
        "r17-b3-agj-p8"
      ]
    },
    {
      "mindmemos_scored_path": true,
      "score_vector": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ],
      "score_vector_sha256": "91d86f0162c9c8c39e2750833a71b6a366e5a532e386a7520086ab811c70c990",
      "scored_patch_system_sha256": "b1bc66660aef255923dab7a83570b8c566326a3dd2517a7d9a87419de2c2fc82",
      "scored_patch_user_fixture_sha256": "797d854fa6b1b5aaf6197f1ec451bcdf62ae5b044aad4a3319305e9962b4d613",
      "stream_id": "e1-agj-01",
      "summary_count": 8,
      "task_ids": [
        "r17-b2-agj-p0",
        "r17-b3-agj-p6",
        "r17-b3-agj-p2",
        "r17-b3-agj-p5",
        "r17-b2-agj-p6",
        "r17-b3-agj-p7",
        "r17-b3-agj-p1",
        "r17-b2-agj-p4"
      ]
    },
    {
      "mindmemos_scored_path": true,
      "score_vector": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ],
      "score_vector_sha256": "91d86f0162c9c8c39e2750833a71b6a366e5a532e386a7520086ab811c70c990",
      "scored_patch_system_sha256": "b1bc66660aef255923dab7a83570b8c566326a3dd2517a7d9a87419de2c2fc82",
      "scored_patch_user_fixture_sha256": "797d854fa6b1b5aaf6197f1ec451bcdf62ae5b044aad4a3319305e9962b4d613",
      "stream_id": "e1-fmv-00",
      "summary_count": 8,
      "task_ids": [
        "r17-b3-fmv-p4",
        "r17-b2-fmv-p8",
        "r17-b2-fmv-p1",
        "r17-b2-fmv-p0",
        "r17-b3-fmv-p5",
        "r17-b2-fmv-p5",
        "r17-b3-fmv-p7",
        "r17-b2-fmv-p6"
      ]
    },
    {
      "mindmemos_scored_path": true,
      "score_vector": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ],
      "score_vector_sha256": "91d86f0162c9c8c39e2750833a71b6a366e5a532e386a7520086ab811c70c990",
      "scored_patch_system_sha256": "b1bc66660aef255923dab7a83570b8c566326a3dd2517a7d9a87419de2c2fc82",
      "scored_patch_user_fixture_sha256": "797d854fa6b1b5aaf6197f1ec451bcdf62ae5b044aad4a3319305e9962b4d613",
      "stream_id": "e1-fmv-01",
      "summary_count": 8,
      "task_ids": [
        "r17-b3-fmv-p0",
        "r17-b2-fmv-p7",
        "r17-b2-fmv-p2",
        "r17-b3-fmv-p2",
        "r17-b3-fmv-p1",
        "r17-b3-fmv-p8",
        "r17-b3-fmv-p3",
        "r17-b2-fmv-p3"
      ]
    },
    {
      "mindmemos_scored_path": true,
      "score_vector": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ],
      "score_vector_sha256": "91d86f0162c9c8c39e2750833a71b6a366e5a532e386a7520086ab811c70c990",
      "scored_patch_system_sha256": "b1bc66660aef255923dab7a83570b8c566326a3dd2517a7d9a87419de2c2fc82",
      "scored_patch_user_fixture_sha256": "797d854fa6b1b5aaf6197f1ec451bcdf62ae5b044aad4a3319305e9962b4d613",
      "stream_id": "e1-ioc-00",
      "summary_count": 8,
      "task_ids": [
        "r17-b3-ioc-p3",
        "r17-b2-ioc-p2",
        "r17-b2-ioc-p5",
        "r17-b2-ioc-p8",
        "r17-b2-ioc-p0",
        "r17-b3-ioc-p6",
        "r17-b3-ioc-p7",
        "r17-b2-ioc-p3"
      ]
    },
    {
      "mindmemos_scored_path": true,
      "score_vector": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ],
      "score_vector_sha256": "91d86f0162c9c8c39e2750833a71b6a366e5a532e386a7520086ab811c70c990",
      "scored_patch_system_sha256": "b1bc66660aef255923dab7a83570b8c566326a3dd2517a7d9a87419de2c2fc82",
      "scored_patch_user_fixture_sha256": "797d854fa6b1b5aaf6197f1ec451bcdf62ae5b044aad4a3319305e9962b4d613",
      "stream_id": "e1-ioc-01",
      "summary_count": 8,
      "task_ids": [
        "r17-b3-ioc-p0",
        "r17-b3-ioc-p5",
        "r17-b2-ioc-p6",
        "r17-b2-ioc-p7",
        "r17-b3-ioc-p4",
        "r17-b2-ioc-p1",
        "r17-b3-ioc-p1",
        "r17-b3-ioc-p8"
      ]
    },
    {
      "mindmemos_scored_path": true,
      "score_vector": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ],
      "score_vector_sha256": "91d86f0162c9c8c39e2750833a71b6a366e5a532e386a7520086ab811c70c990",
      "scored_patch_system_sha256": "b1bc66660aef255923dab7a83570b8c566326a3dd2517a7d9a87419de2c2fc82",
      "scored_patch_user_fixture_sha256": "797d854fa6b1b5aaf6197f1ec451bcdf62ae5b044aad4a3319305e9962b4d613",
      "stream_id": "e1-msp-00",
      "summary_count": 8,
      "task_ids": [
        "r17-b2-msp-p4",
        "r17-b3-msp-p4",
        "r17-b2-msp-p8",
        "r17-b3-msp-p3",
        "r17-b3-msp-p2",
        "r17-b2-msp-p6",
        "r17-b3-msp-p0",
        "r17-b3-msp-p8"
      ]
    },
    {
      "mindmemos_scored_path": true,
      "score_vector": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ],
      "score_vector_sha256": "91d86f0162c9c8c39e2750833a71b6a366e5a532e386a7520086ab811c70c990",
      "scored_patch_system_sha256": "b1bc66660aef255923dab7a83570b8c566326a3dd2517a7d9a87419de2c2fc82",
      "scored_patch_user_fixture_sha256": "797d854fa6b1b5aaf6197f1ec451bcdf62ae5b044aad4a3319305e9962b4d613",
      "stream_id": "e1-msp-01",
      "summary_count": 8,
      "task_ids": [
        "r17-b3-msp-p5",
        "r17-b2-msp-p1",
        "r17-b3-msp-p1",
        "r17-b2-msp-p2",
        "r17-b2-msp-p7",
        "r17-b3-msp-p7",
        "r17-b2-msp-p5",
        "r17-b3-msp-p6"
      ]
    },
    {
      "mindmemos_scored_path": true,
      "score_vector": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ],
      "score_vector_sha256": "91d86f0162c9c8c39e2750833a71b6a366e5a532e386a7520086ab811c70c990",
      "scored_patch_system_sha256": "b1bc66660aef255923dab7a83570b8c566326a3dd2517a7d9a87419de2c2fc82",
      "scored_patch_user_fixture_sha256": "797d854fa6b1b5aaf6197f1ec451bcdf62ae5b044aad4a3319305e9962b4d613",
      "stream_id": "e1-ska-00",
      "summary_count": 8,
      "task_ids": [
        "r17-b2-ska-p3",
        "r17-b2-ska-p1",
        "r17-b2-ska-p4",
        "r17-b3-ska-p8",
        "r17-b3-ska-p2",
        "r17-b3-ska-p6",
        "r17-b2-ska-p6",
        "r17-b2-ska-p7"
      ]
    },
    {
      "mindmemos_scored_path": true,
      "score_vector": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ],
      "score_vector_sha256": "91d86f0162c9c8c39e2750833a71b6a366e5a532e386a7520086ab811c70c990",
      "scored_patch_system_sha256": "b1bc66660aef255923dab7a83570b8c566326a3dd2517a7d9a87419de2c2fc82",
      "scored_patch_user_fixture_sha256": "797d854fa6b1b5aaf6197f1ec451bcdf62ae5b044aad4a3319305e9962b4d613",
      "stream_id": "e1-ska-01",
      "summary_count": 8,
      "task_ids": [
        "r17-b2-ska-p8",
        "r17-b3-ska-p1",
        "r17-b3-ska-p7",
        "r17-b3-ska-p0",
        "r17-b2-ska-p5",
        "r17-b3-ska-p5",
        "r17-b3-ska-p3",
        "r17-b2-ska-p0"
      ]
    },
    {
      "mindmemos_scored_path": true,
      "score_vector": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ],
      "score_vector_sha256": "91d86f0162c9c8c39e2750833a71b6a366e5a532e386a7520086ab811c70c990",
      "scored_patch_system_sha256": "b1bc66660aef255923dab7a83570b8c566326a3dd2517a7d9a87419de2c2fc82",
      "scored_patch_user_fixture_sha256": "797d854fa6b1b5aaf6197f1ec451bcdf62ae5b044aad4a3319305e9962b4d613",
      "stream_id": "e1-tsr-00",
      "summary_count": 8,
      "task_ids": [
        "r17-b3-tsr-p7",
        "r17-b3-tsr-p0",
        "r17-b2-tsr-p3",
        "r17-b2-tsr-p8",
        "r17-b2-tsr-p2",
        "r17-b2-tsr-p5",
        "r17-b2-tsr-p4",
        "r17-b3-tsr-p8"
      ]
    },
    {
      "mindmemos_scored_path": true,
      "score_vector": [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0
      ],
      "score_vector_sha256": "91d86f0162c9c8c39e2750833a71b6a366e5a532e386a7520086ab811c70c990",
      "scored_patch_system_sha256": "b1bc66660aef255923dab7a83570b8c566326a3dd2517a7d9a87419de2c2fc82",
      "scored_patch_user_fixture_sha256": "797d854fa6b1b5aaf6197f1ec451bcdf62ae5b044aad4a3319305e9962b4d613",
      "stream_id": "e1-tsr-01",
      "summary_count": 8,
      "task_ids": [
        "r17-b2-tsr-p0",
        "r17-b2-tsr-p6",
        "r17-b2-tsr-p1",
        "r17-b3-tsr-p3",
        "r17-b3-tsr-p1",
        "r17-b3-tsr-p4",
        "r17-b3-tsr-p6",
        "r17-b3-tsr-p5"
      ]
    }
  ],
  "task_receipts": [
    {
      "acting_score": 1.0,
      "add_record_id": "81832f55-799f-5c7c-a475-33aec1b467de",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "33bf333d7fe02a6569c69cc2fd782f1eebeb74f72cc39411795af08456630c58",
      "pool_sha256": "6bb134e333f83aff68308b28bf4802d17babd04d0036d3141c652f8a48c82ecb",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "130cc7b719b60b24f68fee03481c4e49872132ceedfc256097ec4bc17a1709ca",
      "rb_prompt_tokens": 4604,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-00",
      "task_id": "r17-b2-agj-p2",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "2384b1b9-83a7-5a7a-99b0-fb5085cc3f25",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "39d97d96d1eb6ec471c9f8dd6b4a8e3359fb3e1777bd02a475fc53b187d58fbe",
      "pool_sha256": "e85119a85cbd8addf87540c97ff36c166250f7c641b7c566530a45ccefee6dbf",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "980cc7b6413b4baae61a953af3b1f5ed10802c6e44bb1dbb13f5282dad5d657e",
      "rb_prompt_tokens": 4615,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-00",
      "task_id": "r17-b2-agj-p5",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "49c865de-e391-5b97-8437-24e3718324a0",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "be85bc1b03c0bce4301e06c48ff2e9a3e28994a05ef58ed5d2b0c89a0fddb499",
      "pool_sha256": "5be18be58545d9dc3a9a3767770596e6588eb21183059481407746c118b28542",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "5bc8037f5c52e10f6835775cb5fdc41fd7a9b4349e9b3031b78c7aaf54d812be",
      "rb_prompt_tokens": 4633,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-00",
      "task_id": "r17-b2-agj-p7",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "d8b14e34-0d4e-54a4-8503-9cbf4e5f7089",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "a99e05cb09a50c3c0cd41e72cd2d43224781af9c99ba312eaeb3d10135b8c653",
      "pool_sha256": "f5b8130bdd069944cc496778bcf0069ace535255542fb80d46345f04cc64b5f6",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "4087f6d4083164673179dcdf003e0db6c48f2cdef77f57be052c881c7e3d5e38",
      "rb_prompt_tokens": 4604,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-00",
      "task_id": "r17-b3-agj-p0",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "2e4e8d94-d2ec-5e91-a34a-4877f94747f1",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "a43840435d40718b8cdccacc8dd068cd7d25e67d91e89eb4b12711a9c21f6687",
      "pool_sha256": "80a8cb85525eca0ad019442979e675259df8435b2fc73e58def52ae899546b2a",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "676edd40609b126dffcfe6f0110c206359b81c1699ed9a922849f8639a0dbd75",
      "rb_prompt_tokens": 4620,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-00",
      "task_id": "r17-b2-agj-p3",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "6ce4ac63-d85b-5e7f-8faa-23a0b6b2ae37",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "38f82eb3419e98805e2645e3b7457de97c8e45a8cce051b397e3d0a07d489212",
      "pool_sha256": "bb979598543063189ccabecc4709ee53e6fd65c2626f32e738269c5f904575ce",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "be600c13011d272cefc37e5d2c786f5594fbe9afee4dcb1727490f4f08cbeefa",
      "rb_prompt_tokens": 4618,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-00",
      "task_id": "r17-b3-agj-p3",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "25287ae5-fe92-526b-9b20-775595a36262",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "2d63853e77be71bb3359e612dcec3ea6514cad36b6f96fa2d72988e7387698f2",
      "pool_sha256": "8a37c0684dde8122bf38c46b4f9ef242de0d0c7c249c19db68399e647538b319",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "418c1bedb00f84e3cb260b0c2b07d1e23a7556994dd36c106b3f2d6b474d2109",
      "rb_prompt_tokens": 4637,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-00",
      "task_id": "r17-b2-agj-p8",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "9100cc03-9afc-569a-a782-6fb8c1d69f57",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "29d807afc9761f16952eac9243c9f9228652bbf6fcebac643c2073638cd63b19",
      "pool_sha256": "3c10937593f08179e8e0f6e149dd31526d2a51df44ddcaf4c7d9d35266d88235",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "f7825fb18cfa8cdd064f5bd915ec9fd7d268608d9cfaf05e30cabfe0095ac069",
      "rb_prompt_tokens": 4636,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-00",
      "task_id": "r17-b3-agj-p8",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "ba98aea1-5b34-5abc-a450-189ebc9d89c3",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "5482e7903fe20060bb86041ff00f0df4c42f2747dd7884b803ebddeb02f8b114",
      "pool_sha256": "1e6902bb1a3e097f33dc1b6473719a67bf1299a06993c614d4a27b9198f54c35",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "0bd9cf047f54c20c6f6306c2c157bb6b9829cd0dd97671afe7bfd07e0660ac80",
      "rb_prompt_tokens": 4604,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-01",
      "task_id": "r17-b2-agj-p0",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "e6b4fee0-90bf-5bd3-8d7f-eead5d14d81a",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "8f91fae8838f153e751d74ddbe3869d86b91de5e51d8d6ba802b440e30b6a9d7",
      "pool_sha256": "d23aa4d3ee3940ab6988f752432c3b19f804a1c698f0a9d8d86eacdde6c29a1b",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "584e960fed6b773cf8ab2be3187c42d6f86cdecde7bfb6f524cbffab32db2775",
      "rb_prompt_tokens": 4632,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-01",
      "task_id": "r17-b3-agj-p6",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "d9e8138a-307f-51b2-b04e-cb3dce94015f",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "733034373e1ed4f5a0968a34eb4f66033e4fdcd64a8a0ca02a4c0222604889d5",
      "pool_sha256": "b124d8c84183c6928785e3c31151c892815a4610d4ada8bc9236f5e9cf1e191f",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "6181d61577d39d70f861a186371e93b79f031f0ce5d7605dbe87cf4f3092d7f2",
      "rb_prompt_tokens": 4603,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-01",
      "task_id": "r17-b3-agj-p2",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "06bc0fc9-d8dd-59a7-baf3-d7c6e90b6df3",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "8f72936c26169b76f54291e579c4eea9c1df0af1e441e81e3d0375d34b08d96b",
      "pool_sha256": "f30a24f0c0306ed74a29ada88ba0d35e02a5d6842e9bed3f9811fc2b825160f9",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "12802b57d57f3cf52c26372162e7d6dff1cace8a870130b24fc60e116f6347d3",
      "rb_prompt_tokens": 4618,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-01",
      "task_id": "r17-b3-agj-p5",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "004d1655-680e-54dd-bbca-0b369a4a6b71",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "5d8b66a6e075fabaec3bbe804f961e5b0a6019bd5cfeeb3f02b97e0a29e828cf",
      "pool_sha256": "16342f5e80b92d96117d735bb98ee1936c0a58f161ab58e4b371c286d6314120",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "d33d7c25cd743a64c08ac68d210728715a788849fa465d3b278eac92af44827d",
      "rb_prompt_tokens": 4632,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-01",
      "task_id": "r17-b2-agj-p6",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "7240c283-8516-50eb-8375-75ea5af6aa8f",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "3c8295fd28aacbbdd29c39c8bac5b7ff5a60e9201f31748ce6cf63114d409d98",
      "pool_sha256": "dd643b2837c809e89266354217c98deb3f35177e0613d3d02541c0768244574d",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "60aed08a01b4fb9fcd0a562be6743693d8b3120c43b4bc330e5ccb98317bb906",
      "rb_prompt_tokens": 4633,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-01",
      "task_id": "r17-b3-agj-p7",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "bd39884b-538c-5e9b-bded-1e01d064e270",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "a1025281b5ba34600934f1d78d478b361003106c688d0ededffe40cffa2f297a",
      "pool_sha256": "717a4fe8b845778864ed721f692d2e00c6fe6edd01cadb7fdac1bde8c4ee70f8",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "716def55856293dca9e5084f1ac92b775b3daa4347a002def68c0370109e395e",
      "rb_prompt_tokens": 4605,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-01",
      "task_id": "r17-b3-agj-p1",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "a1e68937-89ce-53ec-a303-b7139506ebbc",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "3c9d108cddada13b8df70fb57104a2f8c7f5b4350d2fb7872502fe531724825b",
      "pool_sha256": "ea6fa00351c74465ff0a85a1ccb1f70bc3a8b42a9bc74b38d6539637fee15092",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "937218210f1e208a80096daa62521b4fbe146937008add4b922c17da25c5cdcf",
      "rb_prompt_tokens": 4618,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-agj-01",
      "task_id": "r17-b2-agj-p4",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "c01ab7e2-4cd5-51fa-b24a-441d3a2fa663",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "43bd35795fe12281a0469b33af1f2db3df723b75acab630dc0187fef7db849e0",
      "pool_sha256": "c977806d6aa3fe35a86c59114b6d9316476017a64400867b99888b0edf33a797",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "95b8273d22d8273f8b0ee2712e9ecb5b4aff0825fdff4932f7364acae46c639e",
      "rb_prompt_tokens": 4607,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-00",
      "task_id": "r17-b3-fmv-p4",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "966c6df3-26a7-5036-a54d-ecbe2fc9bfc4",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "f718aee209955d424ae69f6074826ca325c5a7458861099a2c961352561cbcdd",
      "pool_sha256": "cac193e8a5cf02923a36c1193361fe69129228223aaa473b4c99e5b5115bbf2c",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "938464de4319e5182d972cfb78e5a18fc1ab600a433beaa8e87baaf4b8d7f64d",
      "rb_prompt_tokens": 4612,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-00",
      "task_id": "r17-b2-fmv-p8",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "eb6d712f-5b41-5d01-a1d2-67f6e2a869cc",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "9a453a1de0f523d654ac877f9dc69a8adac066b0ce466db149d397ab9c41be8c",
      "pool_sha256": "036519dae0bc3fe27b28308bafff70cfa6d7fb4c8b19f2186b62dd7f23a80ed9",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "5f15b225e016bd3181ad0dd7963cdf72832982a71eb6d523ee322b65bfe3b879",
      "rb_prompt_tokens": 4600,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-00",
      "task_id": "r17-b2-fmv-p1",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "2c2a4031-a9e6-57b6-a416-0f2537503d97",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "ba3ae37797286941165e20431ab0eb2e4d7c080bc3256a8b55814b1843a910a9",
      "pool_sha256": "23ec56fc83b56f22b1061ce06eed424f81af889563b6d1307418975290d39705",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "056172b50c6ea94a697b74093898904a894be0df8cf0895b80655b9cda63a8a6",
      "rb_prompt_tokens": 4601,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-00",
      "task_id": "r17-b2-fmv-p0",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "ade27c77-af0f-55ac-8dfd-85399b3f7127",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "8b5d7eed181a92a6794640679cdb0a3d2f080d61f4e4fd204e3ac8ef5b262ca3",
      "pool_sha256": "c6aa1978c86b02147f9da88c1a2d331fa3e141696ce16720e7eb50b46c907fb4",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "d06f80603f1745b747b9112ef2c3cb2ed28e29939f121645212d877fe89b4648",
      "rb_prompt_tokens": 4606,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-00",
      "task_id": "r17-b3-fmv-p5",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "ed9c46bf-eaf0-5b9a-afc4-096722467f7b",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "acecf66bfe1e810559d6ce95067537f03144670567bbfabac9f7aac9b15fb902",
      "pool_sha256": "cc550cbc5d5367fbc76446d25dabf722068540d47d7acf17aa8e241550f6ed3e",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "5613f68292ec8bca36cba0c58c8b9c28aa2efa1088cca3df341d03c7db8af986",
      "rb_prompt_tokens": 4607,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-00",
      "task_id": "r17-b2-fmv-p5",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "af0ad482-7949-5b41-b991-6103efe8dd1d",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "b00970a89ad3c99a3a5f2c75c8a83adddac17a7bb64dabbc7744e43ae0cffe11",
      "pool_sha256": "5fb29370edbe86d825bbc64fa10b808c065d311bb28def9360fda3bfc276e655",
      "rb_failure_sources": 5,
      "rb_prompt_sha256": "032876b681feb5112ec9bf216228c8079f120fde866478dac49505e871511659",
      "rb_prompt_tokens": 4611,
      "rb_source_count": 8,
      "rb_success_sources": 3,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-00",
      "task_id": "r17-b3-fmv-p7",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "398ca1a4-313d-549e-afe1-bc4f53f4c461",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "05dd176c1d5296bc4eee9dd12ea10d657adb17615f98df44b2e8b607a15e73f5",
      "pool_sha256": "b9fd2b30a712efc1d26863657e9606fab8506f584fda827649c33096d0ea495b",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "ef33a6993486725ee6e1ccf5f878737bc9bec4e8ff424181eac4d298e6c0b8e8",
      "rb_prompt_tokens": 4612,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-00",
      "task_id": "r17-b2-fmv-p6",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "910460d8-08b3-58f6-b707-46b0489a47ca",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "b8c00ee70121133da2d9e91435b0229e3dd851f4277b7ce6412a1adcbd912317",
      "pool_sha256": "2e5cb6d399c0e1dc8fb0267803a9f9729ba205349cb6ef0917677abaad61a2ef",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "3c393dad15234aaf30cd8970225daf245185fe9edda6b4eb24fd866ef2aa89e9",
      "rb_prompt_tokens": 4601,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-01",
      "task_id": "r17-b3-fmv-p0",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "1f05bc46-b9f8-5e72-b656-f4a487e57f63",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "28d575a4d4eac6c2c054297be43449dee1cb1aaa73c950d4cee7198699747b07",
      "pool_sha256": "2fb9f47bc96b30d293f5a469394fd78ec6dd7ed733834d43c461f11ccb8cdeec",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "359754573264ca079f2736d37925c24726655c74a743db12c0f7e8b3154520d7",
      "rb_prompt_tokens": 4612,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-01",
      "task_id": "r17-b2-fmv-p7",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "b29d5cfd-036f-52ef-ba74-fde0593f7c79",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "02672868eb51bf132724266a77a04fb1ee15281219ee68657eee91f4539b448f",
      "pool_sha256": "db66d85187df26140620477517869f26e2d2e4f46714c6d68392d10da7373ec1",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "adadbdcd6df2aae68994f9bf67466fe69d3910d491045bce43a36e4329eab32c",
      "rb_prompt_tokens": 4603,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-01",
      "task_id": "r17-b2-fmv-p2",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "7241889f-dc2b-5aec-9a0e-df93f04f5fe2",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "137f9b00157829c5c8a741f921fef1177a0a8113a4f181e443c25b3a83973c6b",
      "pool_sha256": "300a94e47f366314be37667610aa2e24369fcd11050bec2e8347967da9033cc2",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "f3d4ee808981147216688948da9604afd5ecbda68b86fb4e2b0ac77f1e6885f6",
      "rb_prompt_tokens": 4603,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-01",
      "task_id": "r17-b3-fmv-p2",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "e82d5d12-1ffb-55a2-9be0-d70a5b9d2207",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "ecd80e94d2816b3faf65b7f82f400175d78fbd76e2f97e7c16ce8b3e7512efe2",
      "pool_sha256": "c1411e2dda57b231c328afb1bdd6ac9d15ed7301759456ad8c29e2cffe315198",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "99a6ff8a9b9fffbbb329f653ced5e8e0ab8d58e703af8397ff4f6f0d7f9f7140",
      "rb_prompt_tokens": 4600,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-01",
      "task_id": "r17-b3-fmv-p1",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "741a2338-1625-5502-8eb2-eef1ad7b546b",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "bef4754fb38f1a3e5d1bf92cae4f43247caaba6b8aa02cc62aa09207182b4d99",
      "pool_sha256": "9db88a383f686ac799ad18c6bd8c48f7522ccb65a9ffcc84a446e227a3a8dfa7",
      "rb_failure_sources": 6,
      "rb_prompt_sha256": "25f96e647b2652e6801d98bd4b90278651542048be0d8450ffc211388af301ce",
      "rb_prompt_tokens": 4612,
      "rb_source_count": 8,
      "rb_success_sources": 2,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-01",
      "task_id": "r17-b3-fmv-p8",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "77ae0f32-d2f4-5e46-90eb-9513da85ec66",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "0448811d87c0c40ef01125d6175045915c463fd92bc749d71e7e1c40db21735c",
      "pool_sha256": "ba66f94bc70a7e29b5dde847e1fd3660fe9d76fb1446accf22264ac0ead77a70",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "f3930f75be810d48b79ea22f9dcf6f4ebd62665df2aacf455eef5332021e2f95",
      "rb_prompt_tokens": 4606,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-01",
      "task_id": "r17-b3-fmv-p3",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "7d0bbf9a-935b-5c7c-af62-dfe50c449913",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "8ec7c718e20281c01979fb03712e899afc4a7a3e3901151f895c8a3fa1cdb076",
      "pool_sha256": "143bf0be3a8b93643626f714cdf07dd84b2fbd8e6bad24c085a1264b8f9a34d6",
      "rb_failure_sources": 4,
      "rb_prompt_sha256": "3d1f0982ee27a657a7af929fe880cb552d2fdf051a1d57b1e126b9edb2a3b7bd",
      "rb_prompt_tokens": 4607,
      "rb_source_count": 8,
      "rb_success_sources": 4,
      "score_equal_to_win": true,
      "stream_id": "e1-fmv-01",
      "task_id": "r17-b2-fmv-p3",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "e2198b2c-e3a4-5380-858d-725635ac38dd",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "b31174741231a7a0de1ce49a0a723e76787d848a2838418628e443654fb2fb3f",
      "pool_sha256": "5a60c8bd0b20a20dac0be2478b17d477a85cf7da18532a9953cb056fed1ccea2",
      "rb_failure_sources": 4,
      "rb_prompt_sha256": "594f910d12bce6c62dc887ce0e9c67fca48fa7bf9a9bb5f10ab0d1c6617c9840",
      "rb_prompt_tokens": 4638,
      "rb_source_count": 8,
      "rb_success_sources": 4,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-00",
      "task_id": "r17-b3-ioc-p3",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "4d05bcfe-40c7-5aab-bc21-10dbfeb215f1",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "0def3eaf5a14a2dc7036ea2f9527fdfeaba1e0b77032206e80bc9a49d30bc22a",
      "pool_sha256": "2ef9e6dbf0f5e10f508c36966151382afe002417e267e784dc1edf6e95d9a9d6",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "f2e4a6373f88e577f792819a8d9e5bff3438202533925f387d81a16e9d441ba8",
      "rb_prompt_tokens": 4617,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-00",
      "task_id": "r17-b2-ioc-p2",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "c6e3fc7f-acf1-5ce3-8038-b74a4049654e",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "925ca82d16447526d272a32b4a13d85d718e6c1cff5b73ffcbf06bf3da3372fa",
      "pool_sha256": "787d3c46a713a989fa0eb14c8fda89adf577187b1161abf9aaa457471b31ba39",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "520c7d383aac23133b1e49c9c2192ec919b2a8e2daf8f2446a75946d8adb0c56",
      "rb_prompt_tokens": 4636,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-00",
      "task_id": "r17-b2-ioc-p5",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "1492b7c8-5621-552a-9e65-ea343bcac002",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "ea9c8392951b55d52459d1ef0d9394fe05c3f522711e94fbf497650332bc4245",
      "pool_sha256": "a0183b03443671fc7a4a18fcab1c29c5787e5586f37975348091548ed978defc",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "30c8627bb58d76cf7c55b2758e79bf9899196afda943dd5dd68fd0228359de9e",
      "rb_prompt_tokens": 4646,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-00",
      "task_id": "r17-b2-ioc-p8",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "16dbd876-597e-5a19-8b03-b79fc3f7ef40",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "703ae6542c778152c938fa921eb424cb70a369296f3aa87529aaf59f546bf46a",
      "pool_sha256": "59d3ce067b69c9361da8c7af22e1defb67e273b3110e23befc27301d323e6ef3",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "cce0e24d40f8db4db37e6b485f9c383d8ef155a7d4f50aed4306fe9a35088126",
      "rb_prompt_tokens": 4617,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-00",
      "task_id": "r17-b2-ioc-p0",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "bfbbf382-e6ee-59f7-a54a-f1df0836d232",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "b20635adc57d08eb6bf3979c33a4188b76f93e572e86984e88710c9e5e1d9cd1",
      "pool_sha256": "2d409ff2826b54c8f2201ca60fd7e445f7ea3bf729897df3da81e576dc1c8b41",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "9470abdf1a76678a8d86ad67a3574c8ab540de119f339d1f160665d2c5d53d4d",
      "rb_prompt_tokens": 4647,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-00",
      "task_id": "r17-b3-ioc-p6",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "0cb8b834-e230-500c-82ec-40eb21f921fa",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "6358eb4c2b2e8bc8ddb441be714e1233d68bba576993e7df0a9e1d3cdbb02637",
      "pool_sha256": "eb08e0a291340d2655f68b80994b911d9abb3651d87a2faf5f273cf6564103e6",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "09873aeabe80d2e375d46e3ed3b3627e419e8f975f428c2466408103afbc9e65",
      "rb_prompt_tokens": 4647,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-00",
      "task_id": "r17-b3-ioc-p7",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "b60710f8-b3ec-5b73-86db-a5e7b7b977e8",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "a0e69387838ec2e4f94078714e19087db4d7143a2961f86be55b29d0f16e51aa",
      "pool_sha256": "369e898a1e978794df9d64ea310740a8afadceb15ca8fc7679e55e3bbe6cbaf1",
      "rb_failure_sources": 4,
      "rb_prompt_sha256": "2933d968faa9f4acfd41a26efb48f46d11605f28b6e5174836a3571c1ac7232c",
      "rb_prompt_tokens": 4636,
      "rb_source_count": 8,
      "rb_success_sources": 4,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-00",
      "task_id": "r17-b2-ioc-p3",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "af4238af-62ef-50ae-95f3-a8167b1e4ba4",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "58ad3bf50a77612ce0f239ffc605bb2cf7653eaa4f885c1910deefaee435a9c4",
      "pool_sha256": "5407d2318a6d053bde52cb6c4de6f7079a8f1fe8c6acb42ef0020b82b66e2bac",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "9d893ffdf4077873427ae268244a39e3da78175a2e0d77a9eb137faf109c9fd3",
      "rb_prompt_tokens": 4617,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-01",
      "task_id": "r17-b3-ioc-p0",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "e7ac8334-dbdc-5ade-bf19-e0cafa00ba4c",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "28bb796c7581bda2d2ba84fd58f63a7d2ed7417f87d46de190e4a0f735523460",
      "pool_sha256": "0858dee963758fb641f31ed788c55ec1682385139f1b28a96ce901a709705ba7",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "eff8d255d67d9605d73a35c68d1657e8ad879742b59a237e56ff556bca5e9a17",
      "rb_prompt_tokens": 4631,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-01",
      "task_id": "r17-b3-ioc-p5",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "44705070-baf2-5c4e-a2d9-b43037c2a56d",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "6a75f10d9f4b044c3e18a8a5b55856d84a782f770994fa1248a0987b3ef6beee",
      "pool_sha256": "3872f0d870c5499271ea00c0f1cee26e2975dcb7ed7fb4b68c44f8e8ab3a7a6c",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "f45657dc118dbbf86611f4af3dee79eda212f9efc08e94d7d6ef142e88a3cdd3",
      "rb_prompt_tokens": 4647,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-01",
      "task_id": "r17-b2-ioc-p6",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "a852ab4b-5734-5bf1-91c4-b66cebdb1c89",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "b4ae4bba57e946543a718030d9622e26a2391ddf100e3183af3af8c46ff4013b",
      "pool_sha256": "ce9d08ad623af78288e0290de2f62669c924f1fc455a42233e01a1b704445546",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "40dd8d663c872f08139fd05d8a4ee7246ed72090d59068b2e9f23623e912caa4",
      "rb_prompt_tokens": 4646,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-01",
      "task_id": "r17-b2-ioc-p7",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "493f0b68-3391-5245-881e-0ea5c6639de9",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "b054af077357a678ccfac740a7f5863355a4368099f2e54202f8e8fb39858252",
      "pool_sha256": "53cc55ec3b5df3e475a813a05d11652fdcf6d697c09f007b32e99d6677f439f3",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "4d301b7ee57775995eb7a15a8841707142eac3d74203c5ef5a8ed401e7549824",
      "rb_prompt_tokens": 4639,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-01",
      "task_id": "r17-b3-ioc-p4",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "fb1b2b32-ed7f-5af6-9234-15ff8b1cdd74",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "12af5e6d16c1ef821349ffea52f2e90287b3d73ccc95706a4bc386ceafeb8569",
      "pool_sha256": "112ec9c04ea158a9fece4c1451201c1c6fe7699cd340d198f8d10d31253f7ce5",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "7e4c35d84e86a2a730ac58a06ba18d159c2bf14296c2b4c26d206130563224b6",
      "rb_prompt_tokens": 4618,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-01",
      "task_id": "r17-b2-ioc-p1",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "d400d47c-2ae9-5a36-a04d-e899a476cf10",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "55a3c88ba272c3d21d3c86df091f0cb0acb5b8a4e46d8dd0366802d1e5acc94e",
      "pool_sha256": "da3925602042081560c415664ce41309d36a93ba498575c8b8dec0d6f0dd2589",
      "rb_failure_sources": 4,
      "rb_prompt_sha256": "8b7a5dd1249d8dbae572060c7e4ddc5da2a0c13d43e4575fbc35eb1a25211e55",
      "rb_prompt_tokens": 4616,
      "rb_source_count": 8,
      "rb_success_sources": 4,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-01",
      "task_id": "r17-b3-ioc-p1",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "c03939d1-7deb-5b10-8f5b-fcfe366b8ae6",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "0e78db53ec29b42e2687260eeca36ff8dfbc67a8562eb7db66dfe60829b8e401",
      "pool_sha256": "4e4802cc4410bad1ea60b0901632ead3fbff1adb753b34fc58fe54375715389d",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "3ab8d37ba83a7cd71e8690faafb9e34f77611443d4fb71511c1e77fcc5f5af6e",
      "rb_prompt_tokens": 4648,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-ioc-01",
      "task_id": "r17-b3-ioc-p8",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "e8a45bb7-9c28-5e88-8413-8ef1e73ade50",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "8bcbd96e4119330d24f587bf0cf2331b07211772104cb09f214bcac745d2bef3",
      "pool_sha256": "7f8215c093ac7f6ff4723bbbdf2eedc2ff571773bd4165e566bb8fb811986cfb",
      "rb_failure_sources": 4,
      "rb_prompt_sha256": "95de5b6d16f3e2c8dea1ccfa17225666a7aa3927c23090fc08706082faeeed53",
      "rb_prompt_tokens": 4619,
      "rb_source_count": 8,
      "rb_success_sources": 4,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-00",
      "task_id": "r17-b2-msp-p4",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "a05898fa-0db2-5bcd-af98-2ece944f6a4f",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "19de975c98b4e4330b422953cfd81b1437ec5d56862a1e0c2d44d43b3b21bd86",
      "pool_sha256": "e52d3b41e6cd3dda34b40f603b594ac3f2dbcc08adeb3584f67ec610fb05cbf9",
      "rb_failure_sources": 5,
      "rb_prompt_sha256": "6954af42f631fe6c3adaa3533f45df6687db20613b3a6170281c162bb9ce6cc4",
      "rb_prompt_tokens": 4619,
      "rb_source_count": 8,
      "rb_success_sources": 3,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-00",
      "task_id": "r17-b3-msp-p4",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "51e8671b-3bcd-55bd-a0e7-f7ea58bf631e",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "5f0c2461c2c89b881195cec025700068e8aa7c8baa07c93c51bfffdbd1afa72f",
      "pool_sha256": "ee4555eac647b133cfcb3cb29e0ce1924d3c8d7ab19069642baf122688049ba4",
      "rb_failure_sources": 4,
      "rb_prompt_sha256": "b760c5624e17cf1914d56f53bb65db4afb8ba4d80d53331630e1672fe706261a",
      "rb_prompt_tokens": 4632,
      "rb_source_count": 8,
      "rb_success_sources": 4,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-00",
      "task_id": "r17-b2-msp-p8",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "4e7a816e-5f74-5a60-b929-46a3f98a5669",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "67780d5ca57991afcdb7b37851780d8308e1dde0cb8315332d0590bfef3102ab",
      "pool_sha256": "3a1e1405dad812b1d1605f3f07da920dfca26d7432e79298a4c2ad44429a34a8",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "73e7471f105e3c7e9fa3c7ffb6987001a79118645749fabc0bd824e9959f1752",
      "rb_prompt_tokens": 4618,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-00",
      "task_id": "r17-b3-msp-p3",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "d4fbf203-325d-52b3-8138-792b489e8f04",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "5e3f0cc96543ffe8aaef6464e78732376ab319c1df8d2d7aa52c03b70e87fa45",
      "pool_sha256": "1390be4ff1d570a17b2aeebd6c0b8e481cf6486bec98da124468a4178b935fc6",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "53168ed275cfffe007f2e68321e3eebdb9783d9c35b290abeb7fae2fe7968f05",
      "rb_prompt_tokens": 4602,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-00",
      "task_id": "r17-b3-msp-p2",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "f0c46844-533e-5fa5-a830-bbb14e8d3695",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "a68627c2f23eb02d5a84e3f02978afbff3e0dad5b473a4313b3540b5de037bce",
      "pool_sha256": "7235b9e297a27eaef0c88619f07f0061fab79f089096539ba048c12e6bd97d92",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "60b0f02b5683b4e14d8fe2643c60e21835dba9dbdf8f1ae1fd4104b1322ebb7f",
      "rb_prompt_tokens": 4634,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-00",
      "task_id": "r17-b2-msp-p6",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "b123cd9c-c587-51d0-ad54-ebc5b82fb05a",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "1dd1298de0bcf003c5388071dd8e7c51d94fac90400f6e4e3de925cd2309d61f",
      "pool_sha256": "ff061ca5f682d0bb220e5338136407d32a3ab837a65d21e8bb83f964443a4e6d",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "6c4054514543e7521c1ddb4f9e5f1c5cc5579d6cceb64a86c2e4a19feb2a9438",
      "rb_prompt_tokens": 4601,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-00",
      "task_id": "r17-b3-msp-p0",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "ee622dd3-be30-540a-91b3-f4e36e7be14a",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "483d333ffa2be90b98b01f61f5464e99c905f911ed1c806eebe92cb86e522985",
      "pool_sha256": "4c84e7a2412927fadb452c805846c9750668c506cf34ccb534a2b5476d4fa571",
      "rb_failure_sources": 4,
      "rb_prompt_sha256": "e79cac8f4b73a85e36d0c8042592670570209c6b57a3794fb4755f15bbdc0813",
      "rb_prompt_tokens": 4634,
      "rb_source_count": 8,
      "rb_success_sources": 4,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-00",
      "task_id": "r17-b3-msp-p8",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "03e0e837-c5fd-546e-a032-bf7ac6b1dcff",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "77874b4381a13cbfe0678a01220bdc4ab73088a8de9f82ce9057dc6b88722097",
      "pool_sha256": "ecf628a6ac526eda6b7c978b4e7b51ab1a95403238487c4fcda8b20afeae8418",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "6839b7e8f49aa23240a761b7b2a1561be3a3475b1d1fc2d722e5edf639863b2c",
      "rb_prompt_tokens": 4618,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-01",
      "task_id": "r17-b3-msp-p5",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "ed458c6f-0452-53cd-ad31-979d3e695bd6",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "a607bb20c7022487472ba4e32e0d6b1edf8b5e8e8237950dd9939cc63156b118",
      "pool_sha256": "fbae337d7c6ea228c2f6d359a8f3d9ed5647030eb85396d360a8ea70d2d8945f",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "35b4b5f1d2610e6391b3579b51a3454ab8ca64f387b9511b2be914d5a79b221e",
      "rb_prompt_tokens": 4602,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-01",
      "task_id": "r17-b2-msp-p1",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "dcb02849-94b6-5433-9bd8-1b566760caf1",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "a7c1f1dbbaf075124cd450ab5ead99afb9491ca4c912c8438e02bc1d52f9a89d",
      "pool_sha256": "473c55a55e0b6c85596176e07f608bd6a3533215c42f188177a448f5e355a040",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "f65d0fe0961647161653356fc857b77b75d9c52a59f3c5723e4f4d561ee691c6",
      "rb_prompt_tokens": 4601,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-01",
      "task_id": "r17-b3-msp-p1",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "e67126f9-eb70-5f59-bef4-ee20d352865b",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "081d90c84ca717ff2e1108125f8366768c118757754a8eaf7ff14381aab6f127",
      "pool_sha256": "258e9ef7819912d726c92534d859510f3f525f1936928b1a1db7264f851ab325",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "d4d80d34bef157e991775f0c894fe612f7639c7f66c7c770891d56cfd33eb65a",
      "rb_prompt_tokens": 4600,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-01",
      "task_id": "r17-b2-msp-p2",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "312d4747-ed46-5981-8c40-e10edfeeade9",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "289b58b97b02ffe18f2cfbd57bc40bfe13bb8580a06c54912e8f9c8d00289988",
      "pool_sha256": "dc8501f34a24ff528a8493fac9ae2b0f41a9b59db7317b57016b42f977b12502",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "96b9dab594f98e8befca8f9e0df6c48636d60216f4375beaeb727b7c8ba28de2",
      "rb_prompt_tokens": 4634,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-01",
      "task_id": "r17-b2-msp-p7",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "8c41b932-6ad6-579f-8ac1-dfe6acaa79c1",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "6d87e0e0bd4733e81714ff9b5b70ce9bfe32a49ed972547d18577975c9a1f2ef",
      "pool_sha256": "5613132d9b0792353995c79b2d9339de6250da8287944ea1ce434dda7de477a9",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "8564b114592b11ac487bae1db10c1665c881d117eb1614e9d40816f79e0656dc",
      "rb_prompt_tokens": 4633,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-01",
      "task_id": "r17-b3-msp-p7",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "29842f4f-07c2-563c-9e1e-88e4acf5ce9c",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "2f67025ec30df77dc943f5c0950e834afe7c0112bdc043fa224843d4958ad59d",
      "pool_sha256": "43db62f847808a9b7160dcb14682f2d71d3464dbdccbc724fdf2ed8f8c0edb75",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "79e72166f661a934b8ad93f432a61298282d752942801025b4a5a35c3ac3f916",
      "rb_prompt_tokens": 4618,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-01",
      "task_id": "r17-b2-msp-p5",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "10d8fa57-4a26-5a8d-9e64-820e079788ee",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "d31bf19f540b2c9085fbc63d409eae11a936315aca44e14bc85254a693bd349a",
      "pool_sha256": "9157867f046ad31eaadc919914222a7b3e27bcb266475116a5571c0c9ece5c29",
      "rb_failure_sources": 5,
      "rb_prompt_sha256": "853f952414f7db42cc6281b9729f8eacb387631fdd2d6812f7181094e3ef7201",
      "rb_prompt_tokens": 4634,
      "rb_source_count": 8,
      "rb_success_sources": 3,
      "score_equal_to_win": true,
      "stream_id": "e1-msp-01",
      "task_id": "r17-b3-msp-p6",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "c9d149ca-26ad-5d5f-8511-38c771cfddf7",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "6890e680b7809ef26e604ea5c56e5474e484de5d43ecc7898c20e1d1dd4ce402",
      "pool_sha256": "e94180c1358472f37ec9392fabe27933dfa4eef3d4e2a203a8aeee1a69f4cea1",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "5d5589897308a63ec54e024ae2585c7fdde4dd83d2984e42ba28fd096f573db3",
      "rb_prompt_tokens": 4624,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-00",
      "task_id": "r17-b2-ska-p3",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "5f92aaf0-a1e7-55d5-a303-43a1150d213e",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "094726223de273c610007fbcd1ea29b3f615f129d675de253762c0b8d748ed2c",
      "pool_sha256": "d7ce5380af0a22d41ef086f76dffe4506880dd5f635eed36a3643c8183b002cc",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "e401570642537b6ee275ae5425f6b2bd9ee195b83d4c6470896400d4f048d6ae",
      "rb_prompt_tokens": 4608,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-00",
      "task_id": "r17-b2-ska-p1",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "23b86293-d76a-574e-a223-d51cde50cf2e",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "1226008d6e39be4bc3d9cda35b4859cd9392da1929b3061f54d42699feddd4ba",
      "pool_sha256": "bf8ae65a983b3b787cc2e652ed39ac90610d50ff31e2b8dbe6ff563e17745ad0",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "d6817b3224dec90b7ccd420d9a21b77034e3340e00053cd0a37665e623374cce",
      "rb_prompt_tokens": 4622,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-00",
      "task_id": "r17-b2-ska-p4",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "8b86b67c-51c3-5861-bf13-b43779c26a69",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "82d661509d75a389f49c66da89680158760202e2269b7495dcb290ae37482ba8",
      "pool_sha256": "4e6e4dede165a6f304438f72d084953483c37169a7b6054359b7ab4afc7e44ee",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "76a9aae093898bee9bd0a8d9390830a35869e9040dfda13e20dd7c44642b0a75",
      "rb_prompt_tokens": 4636,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-00",
      "task_id": "r17-b3-ska-p8",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "028bb017-d7f2-5f61-8b1d-e199e19fcd4c",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "a9008dcc3f1fede65ad644228b18d7ee690d7dad3620f201b7204bc11c9f774d",
      "pool_sha256": "cc77ee33688c739cf9e0522115761c0bb6a843f5560a9c574563ddbcf40d663c",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "b5acc71dc4bf7e97aac5c6b22991b005cbed5f9fcf496c8982c4baab42313a86",
      "rb_prompt_tokens": 4606,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-00",
      "task_id": "r17-b3-ska-p2",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "7da44e9b-b2fb-5838-839e-892e4e76db46",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "f6635a38f29947bfe23c8d1b2ed73cefda4a8375b7ff5c1dbd10011f93ef4093",
      "pool_sha256": "0a23e630167af078242ed0cd2e4b233d32928f02879696e52ae43736f2f6470e",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "0f46fa25953d44d2c0d0dd34a156393ef6f36174b1497fdec3dd1bf07bf00c86",
      "rb_prompt_tokens": 4635,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-00",
      "task_id": "r17-b3-ska-p6",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "95127e27-21cf-5c6c-bbe3-94513bf1121b",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "42d8eba81f90f998bc6c0000bf5bb1e5cd47231bf9eda345b1c4db76506c9b09",
      "pool_sha256": "f8727a2cba0b75f2941eb828c212f9ab538c1ae9f55e31c06960d17488aec925",
      "rb_failure_sources": 4,
      "rb_prompt_sha256": "46906530ed85b418be8136505ff51ed48365131ab13ab67d7bc1b32e443f49a9",
      "rb_prompt_tokens": 4637,
      "rb_source_count": 8,
      "rb_success_sources": 4,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-00",
      "task_id": "r17-b2-ska-p6",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "ce8e724b-241e-5544-bbe5-862b5de3c618",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "94d09c87f8acb815500ae4539ef36a42048c4541f65b39b12c7965db14028f0e",
      "pool_sha256": "44654dc3802ead8dcf6d2bfeed817bf662d2b43deb63227c18f9030808189491",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "5540fffaddd1630c86d6d2f5cc15d429af9efc46e0f08309e1ac001661477454",
      "rb_prompt_tokens": 4632,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-00",
      "task_id": "r17-b2-ska-p7",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "58492431-7e85-55f7-a8e6-f2b5d1f41ce8",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "9a53886ea1d313b72e225cc9654c52f8ec553d10d1eeb9e3b52156472700dcba",
      "pool_sha256": "ad64441334ef865061bcb5ab498bc9ef986d719b36bf52999ccf382ab65fa433",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "7c11bb13ae672c6c6b574b216dfe6705f05a61e749cda7350d7b36267c9d8959",
      "rb_prompt_tokens": 4636,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-01",
      "task_id": "r17-b2-ska-p8",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "37d498e7-11ca-56a3-9b0f-32ccbf680a71",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "bc5c7c7bac8f6916b54795ddb4d600636b499f012e773243364b5815a2d4f673",
      "pool_sha256": "47b29f7c9e7028031073706297548456bc7dbe6d379bf7a9f163daf76d7e5f00",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "91865e72280679379b02bc64394c4dd0d4e1f5b151564cfc2017f07ee1e0ada5",
      "rb_prompt_tokens": 4607,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-01",
      "task_id": "r17-b3-ska-p1",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "fae161cd-dc43-5128-9d1e-a2c408c22a4e",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "6290dce63ae44248b2940502c83e30272a6d2b1ac71591c0ad1876ce83f9a779",
      "pool_sha256": "c07b632ac118fb0f62210475947bd6e98651b2d1c696c79a50f0424d471304e6",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "72e66b17f860af7058aa161930d0dac0b07bb20fd818d9aaca9d1edead8a2734",
      "rb_prompt_tokens": 4632,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-01",
      "task_id": "r17-b3-ska-p7",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "209b5d11-2a3c-562a-8510-01328af1a002",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "25d6f68ba88c2a48054818b087e031e99c8e8551c06aeb89c0f661804a6c24f7",
      "pool_sha256": "3815b59fa03f76701e9141e2cb220443031956cb92f6561f1c94ec8f6a06d662",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "1b03eaa735976d58a1f0243d33de2d7f29bb6e22404a6f446985b144daf3d00f",
      "rb_prompt_tokens": 4605,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-01",
      "task_id": "r17-b3-ska-p0",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "c297ffce-cf7b-565a-8463-33921e8ede57",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "e80ea93e33bf2d3a86ad8bb8e497aa6f7a9037bb46fb69dbea4245a94376f631",
      "pool_sha256": "03cc59702d4252aedd4e8ead9f33cf9f7adf51e7df7a8dd43cfaf5d1251a55b6",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "55bc8589c089cac101f04c091d35f81ea262b8485399159c3a96b77cfba51c04",
      "rb_prompt_tokens": 4622,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-01",
      "task_id": "r17-b2-ska-p5",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "785c7138-f66a-5cf5-90bf-a60986796ebe",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "0f96642d078622fcff3bd97e7e5dbdf15e1beda2e1de322190d7fd2a1b6ce8d1",
      "pool_sha256": "f96291b324f9cd6419a6747ca5a7c14514ff226150de82b1132939ef2f677b6f",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "37a85e704f349683928fe806ef9b2373dc8b4aaa3070796d564b731baa4637fe",
      "rb_prompt_tokens": 4621,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-01",
      "task_id": "r17-b3-ska-p5",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "20da3fcb-00f9-562a-b13b-403092e1c2d4",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "82136e384e86bcd7576b7d7d0f588ca2b6ec0c14177ad1a94476ee9147b28d07",
      "pool_sha256": "9a8e802336f46e692b679d4cb8eb60e46ac679df915ec67a9ebc8ab0fc78d544",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "addcafdba4a8bd2df27c785f561165b1f7f91c1909e5225b26e4e6860c1c24d4",
      "rb_prompt_tokens": 4624,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-01",
      "task_id": "r17-b3-ska-p3",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "6270654f-234b-5a40-9370-77cfa6e5c75d",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "be1c71ed79eae6e66be6fca0407a0bd5c26cf61fc7c13385d96c8c5145526f74",
      "pool_sha256": "ffd0d0d406d9b1872193bb4fa23d970b32eb8d7b3a0c2ae3d9df131736be699f",
      "rb_failure_sources": 1,
      "rb_prompt_sha256": "d4a5c6d4a3c210e2f59ea2b6837fded8b7a406c87b1727e664509e339b13140a",
      "rb_prompt_tokens": 4605,
      "rb_source_count": 8,
      "rb_success_sources": 7,
      "score_equal_to_win": true,
      "stream_id": "e1-ska-01",
      "task_id": "r17-b2-ska-p0",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "eec344aa-0a4b-510e-a3da-73287c4aa698",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "4cd7e3ec496f6f46068a07adbb6bf210cbdb479ecb3683ac0ad33aa8c06dc404",
      "pool_sha256": "53d9abbbce1a5fb4bf48906a273785e9f8f280b637f9ad8f6d577f610e9db6b6",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "d0dd6ebb893b9e758b06adb69b193b14960301009d312b70519e92e61be2ff1f",
      "rb_prompt_tokens": 4632,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-00",
      "task_id": "r17-b3-tsr-p7",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "437d03ff-8460-5bca-a6d6-d077194117ad",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "8adb17d5d33e8a3d7799bdbae65ddb2151c23a3d86f71eecf72ca9679ea15c9c",
      "pool_sha256": "2629ce7090a3f5b6142bd996e50366ff1bf8cac709d482a636844f6c5b28511c",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "dfecb191f3ec6c7f8e406b8cd5f561e1094046629180b4d5b66d5d4320fafa4a",
      "rb_prompt_tokens": 4602,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-00",
      "task_id": "r17-b3-tsr-p0",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "ae9139e0-2c6d-5815-af6b-1f9973f2096b",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "6257eecdb7f9aac53d2ff91c1da5f582b587aff51413cbd54227b7f43fc07230",
      "pool_sha256": "565ca49b5b75be18b38351bce67975808f5103f7dc5d80449717b524d298b798",
      "rb_failure_sources": 6,
      "rb_prompt_sha256": "98720ac60470f87b558faedb5bc5ebf31012e0f92d6ea04eb18384357e4923f3",
      "rb_prompt_tokens": 4616,
      "rb_source_count": 8,
      "rb_success_sources": 2,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-00",
      "task_id": "r17-b2-tsr-p3",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "1832c961-18a6-5c46-9016-85fc67c1f76f",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "51bf9e9a1f2e84212c1e1854f885ad0606e169634d8de31d848535645857cfa3",
      "pool_sha256": "5001ce346851199f40616f4f78531e1f6b5b6aff929ba8c7a9cc73b4303b2d97",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "4a50e7d67b14d8ab72c749a6084428f0860b1d5e211ac036dfa426a61df488de",
      "rb_prompt_tokens": 4632,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-00",
      "task_id": "r17-b2-tsr-p8",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "4e2fc375-f5cf-5837-ab99-d2989b03feac",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "47ee8035cf14cb7a0f7ce3877f120e5b8771bdb0810d5df290b8c15ea78aef56",
      "pool_sha256": "b36a3799cd74647d7bb8859b024f3fd3bab6063e4e54fda5620279aca13cbefc",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "50e59d6c29e89dd787c2c6974e48eb13fa778965e648e96263a9d65141ce046b",
      "rb_prompt_tokens": 4602,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-00",
      "task_id": "r17-b2-tsr-p2",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "6f31aff7-42be-5daa-beb6-22b7a2c7a0fe",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "2febf527afae2f6fe089edf4902b66b7abd85bcfb8e44b2fe823d1523e1bae3d",
      "pool_sha256": "d86c7832efbbfdb11b3e5539740a5e02491f8ad4488462939ba721612d0d653c",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "3c03e8bc85ee0acb90df6561c4a57a65d2ecd553c9b24421877b3e4be8c8b22a",
      "rb_prompt_tokens": 4617,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-00",
      "task_id": "r17-b2-tsr-p5",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "bef74921-91a7-5089-af9b-08d261769bb6",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "45592ca13a16ab6c8de32194aea53534a80a28050dbc9f2d0e6bfe75de7f071c",
      "pool_sha256": "0080b3e0da0786ef1dfcc51d704c041b287c4917323fd9d570d0f42ab2091811",
      "rb_failure_sources": 5,
      "rb_prompt_sha256": "5c33de0eaec192a3db9988bfa413a6e8dced13b741f38129b9fecc91b7fcb223",
      "rb_prompt_tokens": 4617,
      "rb_source_count": 8,
      "rb_success_sources": 3,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-00",
      "task_id": "r17-b2-tsr-p4",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "9cc8d848-6e99-52cc-9c33-d63ffd1d3495",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "ad8bba4b6f4634d8435f619f4ff79b485e74c33fecdb858094b444129c338cf4",
      "pool_sha256": "ca70f41358fd2a586f0980a4a2bf81951833956a497a446126f5d6df081af501",
      "rb_failure_sources": 4,
      "rb_prompt_sha256": "aed53d128a4f6f39b869b980a7b7015e9e940a3aeb71ab8d692455975cfb6cb8",
      "rb_prompt_tokens": 4634,
      "rb_source_count": 8,
      "rb_success_sources": 4,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-00",
      "task_id": "r17-b3-tsr-p8",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "faedb314-3c2d-51c7-af61-b214f513372a",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "0d8e89193fb3d740493bb1e58d5daa90809465a7abf190692eba9efc2aaa6904",
      "pool_sha256": "663a34241988cb1d1c68d9a9baf7c5d576bcef0e85ca08eb7420a1ebb486cfdf",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "528e357b27f623305a147c346afdd6f7d67ff5cfe5a4dd5dc50d83cecafe994d",
      "rb_prompt_tokens": 4602,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-01",
      "task_id": "r17-b2-tsr-p0",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "9b8b4c2f-f246-5a25-a73c-9b2379f28141",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "b099fb8b5c32e3153ebc2add7bbdeb902cd5bb0683b33b4edc68e99f0031e548",
      "pool_sha256": "b636c1d63aee3877e8326a5fe477abdc6381722792f99bd8847a05b681cce0e5",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "55b5c5ac17741a400c60c5a831c183c4091537d227e75f79b37147ad91e47ce1",
      "rb_prompt_tokens": 4633,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-01",
      "task_id": "r17-b2-tsr-p6",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "df6d0460-960e-532c-aeff-ae5ae2c60e6b",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "c30e7609a0be84d7ed41c453bfe951940c8294e641ecef077c7489bf37a6dd06",
      "pool_sha256": "a3e1ef9524f3575a66cc40ccf1b6cc088f297e9a18d7505c2a622198e60c671c",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "cc23b8eb2d33b787e2360099f28838c9f0a0461bdb3776bb6aeb6c395ddf3e46",
      "rb_prompt_tokens": 4603,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-01",
      "task_id": "r17-b2-tsr-p1",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "304b9a1e-a8d8-521d-bf53-c444f6134378",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "c68bedf36703eaceca3ce70372d7b3c1e7535efa98a59474b91dcfd0092f1817",
      "pool_sha256": "0e1c97e4f4554b27eb2463e0d0b937198e67b267a8b38f967d598875e90da2b0",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "6115ca025369ba6ebca5e811074a33c3d11df4e950bb0e0f465966927c27c9b9",
      "rb_prompt_tokens": 4616,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-01",
      "task_id": "r17-b3-tsr-p3",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "4b17f870-f851-50a4-b23e-e52339ce2ab3",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": false,
      "pool_id": "baeb22877cc3e5f36283f909995d062c12f630183bde574f584561848a9f43bd",
      "pool_sha256": "e82d66f5f0b906925a5eafe69fba670d0c524abc1b0db81dc5c7ac3d0d80b5fa",
      "rb_failure_sources": 0,
      "rb_prompt_sha256": "0a0d82022dbdb30359638f4c777492a3b2b849e2a8bb2c8d37d28ba93cde3f5b",
      "rb_prompt_tokens": 4603,
      "rb_source_count": 8,
      "rb_success_sources": 8,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-01",
      "task_id": "r17-b3-tsr-p1",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "ac7a8093-7e71-560a-b421-e01f0b9ab09c",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "b3705d103d0a0fd94fc275f9c903340f42979c51279dab58e7d9e63cdfb77b36",
      "pool_sha256": "2ca13720131c23499d9058371510668376e4a7346d51ad811609132950718ec3",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "399e674e33e8bd830ec241ab1daaf541a1243acc0c3226f176b7070e403896d4",
      "rb_prompt_tokens": 4617,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-01",
      "task_id": "r17-b3-tsr-p4",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "96fff271-4d11-5ca8-985f-770ce24f3644",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "5ec6ef566ed841fc37878938d9b48449a71764ea5d4b3744a558c72279692e88",
      "pool_sha256": "935f4e3f6793ad81d69e9f39c0b0a5279a3ad995306f994a6e36e995b13b5610",
      "rb_failure_sources": 2,
      "rb_prompt_sha256": "bd6a48bf7f024e98f794eeda74a877f5a72deefd23b7afb3d27e008c790a9b67",
      "rb_prompt_tokens": 4634,
      "rb_source_count": 8,
      "rb_success_sources": 6,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-01",
      "task_id": "r17-b3-tsr-p6",
      "win_selected_score": 1.0
    },
    {
      "acting_score": 1.0,
      "add_record_id": "c418f591-937a-501b-af3c-ea74d5e22b62",
      "add_summary_one_to_one": true,
      "fixture_memory_sha256": "f83fc2c4c73c170874421c777b720c80064d179917a9f8320e1f136c585a903f",
      "mixed_pool": true,
      "pool_id": "73567e156240a9f10ef7be39e0e20ddb9c4af9c230ca3914833d585679bf6774",
      "pool_sha256": "4d8da1f5c4c69da2eb8ad1535eef854d2e583c14bb7d46af06954321294ba6ff",
      "rb_failure_sources": 3,
      "rb_prompt_sha256": "1ce25c7efd3e343e3547b2a5fd3524ded5e42339880bd5ecc854872782be3d47",
      "rb_prompt_tokens": 4617,
      "rb_source_count": 8,
      "rb_success_sources": 5,
      "score_equal_to_win": true,
      "stream_id": "e1-tsr-01",
      "task_id": "r17-b3-tsr-p5",
      "win_selected_score": 1.0
    }
  ],
  "tasks_per_stream": 8
}


===== BOUND ARTIFACT: actual_path_preflight | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-posthold-rbagg-diagnostic-20260902/generated/e2-r17-posthold-rbagg-zero-provider-actual-path-preflight-v2-20260902.json =====
{
  "aggregator_provider_calls": 0,
  "artifact_type": "e2-r17-posthold-rbagg-zero-provider-actual-path-preflight",
  "authority": {
    "heldout_evaluation": false,
    "paper_promotion": false,
    "provider_io": false,
    "rbagg_full_diagnostic": false,
    "semantic_provider_pilot": false
  },
  "created_at_utc": "2026-09-02T04:12:18+00:00",
  "direct_trajectory_summarization_forbidden_and_absent": true,
  "first_party_patch_interface_calls_fake": 2,
  "first_party_trajectory_summary_calls": 0,
  "fixture_skill_byte_change_is_trailing_whitespace_only": true,
  "fixture_skill_semantically_unchanged": true,
  "heldout_evaluations": 0,
  "mindmemos_provider_calls": 0,
  "next_gate": "INDEPENDENT_REVIEW_THEN_SEPARATE_SINGLE_STREAM_SEMANTIC_PROVIDER_PILOT",
  "parent_primary_status": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
  "parent_status_changed": false,
  "patch_parser_calls_fake": 1,
  "pilot_stream_id": "e1-agj-00",
  "pilot_task_count": 8,
  "precomputed_summary_count": 8,
  "provider_calls": 0,
  "schema_version": "1.0",
  "semantic_preflight_path": "generated/e2-r17-posthold-rbagg-zero-provider-semantic-adapter-preflight-20260902.json",
  "semantic_preflight_sha256": "ddbd8fbb8d89ce31870f85ed97f844ee61414277005f8c4fad97c5f1a50e1e7f",
  "skill_post_path": "/data/wyt/e2-r17-search-projection/runtime-pilots/posthold-rbagg-zero-provider-actual-path-v2-20260902/skill_post/SKILL.md",
  "skill_post_sha256": "6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649",
  "status": "PASS_RBAGG_ZERO_PROVIDER_ACTUAL_MINDMEMOS_PATH",
  "update_receipt_path": "/data/wyt/e2-r17-search-projection/runtime-pilots/posthold-rbagg-zero-provider-actual-path-v2-20260902/update_receipt.json",
  "update_receipt_sha256": "36fb825982604f7dc4bcef63b558055a324c9c409ffe8bf57818397bdccb8df5"
}


===== BOUND ARTIFACT: actual_path_v1_blocker | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-posthold-rbagg-diagnostic-20260902/generated/e2-r17-posthold-rbagg-zero-provider-actual-path-v1-assertion-blocker-20260902.json =====
{
  "artifact_type": "e2-r17-posthold-rbagg-zero-provider-actual-path-v1-assertion-blocker",
  "created_at_utc": "2026-09-02T04:11:00+00:00",
  "status": "SUPERSEDED_IMPLEMENTATION_ASSERTION_TOO_STRICT_ZERO_PROVIDER",
  "provider_calls": 0,
  "scientific_effectiveness_evaluated": false,
  "heldout_evaluations": 0,
  "pilot_root": "/data/wyt/e2-r17-search-projection/runtime-pilots/posthold-rbagg-zero-provider-actual-path-20260902",
  "observed": {
    "skill_post_sha256": "6df40f61707494793289aa95cc89f5ac99da9eb0aa062cf9ad0fbffd71c00649",
    "initial_skill_sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb",
    "byte_difference": "one trailing newline removed by first-party SkillEvolver .strip()",
    "semantic_text_equal_after_strip": true,
    "summary_count": 8,
    "new_first_party_trajectory_summaries": 0,
    "precomputed_summary_consumed_count": 8,
    "fake_patch_interface_calls": 2
  },
  "diagnosis": "The actual MindMemOS path completed successfully. The preflight script then incorrectly required byte-identical SKILL.md despite first-party _mint_version stripping surrounding whitespace from every patch result, including an edits=[] no-op. The assertion is repaired to require exact semantic text equality after the already-frozen first-party strip behavior. The v1 root is preserved and not reused.",
  "authority": {
    "provider_io": false,
    "semantic_provider_pilot": false,
    "rbagg_full_diagnostic": false,
    "paper_promotion": false
  }
}


===== BOUND ARTIFACT: semantic_adapter | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-posthold-rbagg-diagnostic-20260902/research_pipeline/e2_r17_rbagg_posthold.py =====
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
import re
from typing import Any, Mapping, Sequence


_MEMORY_ITEM_RE = re.compile(
    r"(?ms)^# Memory Item (?P<index>[1-5])\s*\n"
    r"## Title\s+(?P<title>[^\n]+)\s*\n"
    r"## Description\s+(?P<description>[^\n]+)\s*\n"
    r"## Content\s+(?P<content>.*?)(?=^# Memory Item [1-5]\s*$|\Z)"
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RBMemoryItem:
    index: int
    title: str
    description: str
    content: str

    def normalized(self) -> str:
        return (
            f"# Memory Item {self.index}\n"
            f"## Title {self.title.strip()}\n"
            f"## Description {self.description.strip()}\n"
            f"## Content {self.content.strip()}"
        )


@dataclass(frozen=True)
class RBAggregatedSessionEvidence:
    """One ReasoningBank-style summary of a frozen K=8 search session.

    The object is deliberately NOT called a trajectory.  It represents one
    task-level search session whose eight source trajectories are separately
    content-addressed by ``aggregation_receipt``. ``acting_score`` is the frozen
    user-facing best-of-K session outcome. It is the only score permitted when
    the precomputed aggregate is handed to MindMemOS's scored patch proposer.
    """

    task_id: str
    pool_id: str
    acting_score: float
    memory_items_markdown: str
    memory_items_sha256: str
    memory_item_count: int
    aggregation_receipt: Mapping[str, Any]

    def validate(self) -> None:
        if not self.task_id or not self.pool_id:
            raise ValueError("RB aggregate must bind task_id and pool_id")
        if self.acting_score not in (0.0, 1.0):
            raise ValueError("RB aggregate acting score must be binary")
        parsed = parse_rb_memory_items(self.memory_items_markdown)
        if len(parsed) != self.memory_item_count:
            raise ValueError("RB aggregate item count drift")
        normalized = normalize_rb_memory_items(parsed)
        if normalized != self.memory_items_markdown:
            raise ValueError("RB aggregate Markdown is not canonical")
        if sha256_text(self.memory_items_markdown) != self.memory_items_sha256:
            raise ValueError("RB aggregate Markdown SHA drift")
        sources = list(self.aggregation_receipt.get("sources") or [])
        if len(sources) != 8:
            raise ValueError("RB aggregate must bind exactly eight source trajectories")
        if len({int(row["rollout_index"]) for row in sources}) != 8:
            raise ValueError("RB aggregate rollout indices are not unique")
        if any(float(row["verifier_score"]) not in (0.0, 1.0) for row in sources):
            raise ValueError("RB aggregate source score is non-binary")
        observed = max(float(row["verifier_score"]) for row in sources)
        if observed != self.acting_score:
            raise ValueError("RB aggregate session score differs from frozen best-of-K outcome")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["aggregation_receipt"] = dict(self.aggregation_receipt)
        return payload


def parse_rb_memory_items(text: str) -> tuple[RBMemoryItem, ...]:
    """Strictly parse the official PARALLEL_SI Memory Item surface.

    We intentionally reject prose before/after the item blocks, skipped indices,
    duplicated indices, empty fields and more than five items. There is no parse
    correction or hidden retry in the scientific adapter.
    """

    raw = (text or "").strip()
    if not raw:
        raise ValueError("RB aggregation returned empty text")
    matches = list(_MEMORY_ITEM_RE.finditer(raw))
    if not matches:
        raise ValueError("RB aggregation did not emit official Memory Item blocks")
    prefix = raw[: matches[0].start()].strip()
    suffix = raw[matches[-1].end() :].strip()
    if prefix or suffix:
        raise ValueError("RB aggregation contains text outside Memory Item blocks")
    covered = "".join(match.group(0) for match in matches)
    # Normalizing whitespace by concatenation is not a reliable full-coverage
    # check, so verify every gap between matched blocks is whitespace only.
    previous = 0
    for match in matches:
        if raw[previous : match.start()].strip():
            raise ValueError("RB aggregation contains unparsed inter-item text")
        previous = match.end()
    if raw[previous:].strip():
        raise ValueError("RB aggregation contains unparsed trailing text")

    items: list[RBMemoryItem] = []
    for expected, match in enumerate(matches, start=1):
        index = int(match.group("index"))
        if index != expected:
            raise ValueError("RB Memory Item indices must be contiguous from one")
        title = match.group("title").strip()
        description = match.group("description").strip()
        content = match.group("content").strip()
        if not title or not description or not content:
            raise ValueError("RB Memory Item fields must be nonempty")
        items.append(RBMemoryItem(index=index, title=title, description=description, content=content))
    if not 1 <= len(items) <= 5:
        raise ValueError("RB aggregation must emit one to five Memory Items")
    return tuple(items)


def normalize_rb_memory_items(items: Sequence[RBMemoryItem]) -> str:
    if not items:
        raise ValueError("cannot normalize an empty RB Memory Item list")
    if len(items) > 5:
        raise ValueError("RB Memory Item list exceeds official cap")
    return "\n\n".join(item.normalized() for item in items)


def build_rb_aggregated_session_evidence(
    *,
    task_id: str,
    pool_id: str,
    acting_score: float,
    raw_memory_items: str,
    aggregation_receipt: Mapping[str, Any],
) -> RBAggregatedSessionEvidence:
    items = parse_rb_memory_items(raw_memory_items)
    normalized = normalize_rb_memory_items(items)
    unit = RBAggregatedSessionEvidence(
        task_id=task_id,
        pool_id=pool_id,
        acting_score=float(acting_score),
        memory_items_markdown=normalized,
        memory_items_sha256=sha256_text(normalized),
        memory_item_count=len(items),
        aggregation_receipt=dict(aggregation_receipt),
    )
    unit.validate()
    return unit


def build_rb_search_session_add_payload(
    *,
    unit: RBAggregatedSessionEvidence,
    project_id: str,
    task_completed_at: str,
    initial_skill_sha256: str,
    root_version_id: str,
    deterministic_add_record_id: str,
) -> dict[str, Any]:
    """Construct the 1:1 source record paired with a precomputed RB summary.

    The record explicitly says it represents a multi-trajectory search session.
    A runtime supervisor must assert that the matching precomputed summary exists
    before SkillEvolver is entered; direct trajectory summarization of this record
    is forbidden for the diagnostic child.
    """

    unit.validate()
    if not deterministic_add_record_id:
        raise ValueError("RB aggregate requires a deterministic add-record id")
    return {
        "add_record_id": deterministic_add_record_id,
        "project_id": project_id,
        "task_completed_at": task_completed_at,
        "messages": [
            {
                "role": "user",
                "content": (
                    "E2-R17 RB-AGG SEARCH-SESSION EVIDENCE\n"
                    "This is a precomputed ReasoningBank-style aggregation of one frozen K=8 task session, "
                    "not a single execution trajectory.\n\n"
                    + unit.memory_items_markdown
                ),
            }
        ],
        "score": float(unit.acting_score),
        "task_id": unit.task_id,
        "skill_bindings": [
            {
                "name": "xlsx",
                "content_hash": initial_skill_sha256,
                "version_id": root_version_id,
                "usage": "injected",
            }
        ],
        "r17_rbagg": True,
        "r17_rbagg_pool_id": unit.pool_id,
        "r17_rbagg_memory_items_sha256": unit.memory_items_sha256,
        "r17_rbagg_source_count": 8,
        "r17_rbagg_precomputed_summary_required": True,
        "r17_rbagg_direct_trajectory_summarization_forbidden": True,
    }


def build_rb_precomputed_summary_payload(
    *,
    unit: RBAggregatedSessionEvidence,
    project_id: str,
    cloud_skill_id: str,
    skill_name: str,
    deterministic_add_record_id: str,
    created_at: datetime,
) -> dict[str, Any]:
    """Build the payload corresponding to MindMemOS ``SkillTraceSummary``.

    The aggregate is inserted at the summary boundary, not misrepresented as a
    single rollout. Its score is the frozen best-of-K session outcome; therefore
    the standard scored patch proposer remains semantically truthful at the
    *session* level.
    """

    unit.validate()
    if not deterministic_add_record_id:
        raise ValueError("RB aggregate requires a deterministic add-record id")
    return {
        "summary_id": deterministic_add_record_id,
        "project_id": project_id,
        "cloud_skill_id": cloud_skill_id,
        "add_record_id": deterministic_add_record_id,
        "skill_name": skill_name,
        "summary": unit.memory_items_markdown,
        "created_at": created_at,
        "consumed_version_id": None,
        "score": float(unit.acting_score),
        "task_id": unit.task_id,
        "r17_semantic_role": "reasoningbank_style_precomputed_search_session_summary",
        "r17_pool_id": unit.pool_id,
        "r17_memory_items_sha256": unit.memory_items_sha256,
    }


def validate_rb_add_summary_pair(add_payload: Mapping[str, Any], summary_payload: Mapping[str, Any]) -> None:
    if add_payload.get("add_record_id") != summary_payload.get("summary_id"):
        raise ValueError("RB add/summary point id mismatch")
    if add_payload.get("add_record_id") != summary_payload.get("add_record_id"):
        raise ValueError("RB summary does not bind originating add record")
    if add_payload.get("task_id") != summary_payload.get("task_id"):
        raise ValueError("RB add/summary task mismatch")
    if float(add_payload.get("score")) != float(summary_payload.get("score")):
        raise ValueError("RB add/summary score mismatch")
    if add_payload.get("r17_rbagg_memory_items_sha256") != summary_payload.get("r17_memory_items_sha256"):
        raise ValueError("RB add/summary aggregate SHA mismatch")
    if add_payload.get("r17_rbagg_precomputed_summary_required") is not True:
        raise ValueError("RB add record does not require precomputed summary")
    if add_payload.get("r17_rbagg_direct_trajectory_summarization_forbidden") is not True:
        raise ValueError("RB add record does not forbid direct trajectory summarization")


===== BOUND ARTIFACT: mindmemos_adapter | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-posthold-rbagg-diagnostic-20260902/research_pipeline/e2_r17_rbagg_mindmemos_updater.py =====
from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Sequence

from research_pipeline.e2_r17_mindmemos_updater import sha_file, sha_text
from research_pipeline.e2_r17_rbagg_posthold import (
    RBAggregatedSessionEvidence,
    build_rb_precomputed_summary_payload,
    build_rb_search_session_add_payload,
    validate_rb_add_summary_pair,
)
from research_pipeline.e2_r17_search_projection_runner import SearchPool

_ID_NAMESPACE = uuid.UUID("24631de6-d366-445b-815d-f931786abb17")


@dataclass(frozen=True)
class RBAggUpdateResult:
    stream_id: str
    update_receipt_path: str
    update_receipt_sha256: str
    skill_post_path: str
    skill_post_sha256: str
    evolved: bool
    new_version_ids: tuple[str, ...]
    mindmemos_provider_calls: int
    mindmemos_provider_total_tokens: int


def rb_trace_uuid(stream_id: str, task_id: str, pool_id: str) -> str:
    return str(uuid.uuid5(_ID_NAMESPACE, f"{stream_id}|{task_id}|{pool_id}|rbagg"))


async def run_rbagg_update(
    *,
    stream_id: str,
    pools: Sequence[SearchPool],
    aggregates: Sequence[RBAggregatedSessionEvidence],
    initial_skill_md: str,
    initial_skill_sha256: str,
    run_dir: Path,
    llm_adapter: Any,
    mindmemos_commit: str,
    contract_sha256: str,
    authorization_sha256: str,
    transcript_max_chars: int = 100000,
) -> RBAggUpdateResult:
    """Run the first-party MindMemOS patch stage on eight precomputed RB summaries.

    ReasoningBank's PARALLEL_SI call replaces MindMemOS's per-trajectory summary
    stage; it does not add a second evolution stage. Each aggregate is represented
    by a 1:1 explicit search-session add record plus a precomputed
    ``SkillTraceSummary``. The standard first-party scored patch proposer and
    deterministic patch applier remain unchanged.

    The synthetic search-session record is never summarized by MindMemOS. Before
    ``SkillEvolver.evolve`` is entered this function proves all eight matching
    summaries already exist, so ``_injected_candidates`` must skip all eight add
    records. Any mismatch is fail-closed.
    """

    if len(pools) != 8 or len(aggregates) != 8:
        raise ValueError("RB-AGG requires exactly eight frozen task pools and eight aggregates")
    if [pool.task_id for pool in pools] != [unit.task_id for unit in aggregates]:
        raise ValueError("RB-AGG pool/aggregate task order mismatch")
    for pool, unit in zip(pools, aggregates):
        pool.validate()
        unit.validate()
        if unit.pool_id != pool.pool_id:
            raise ValueError("RB-AGG pool identity mismatch")
        if float(unit.acting_score) != float(pool.acting_success):
            raise ValueError("RB-AGG session score differs from frozen acting outcome")

    run_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = run_dir / "update_receipt.json"
    skill_path = run_dir / "skill_post" / "SKILL.md"
    if receipt_path.exists() and skill_path.exists():
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        if sha_file(skill_path) != payload.get("skill_post_sha256"):
            raise RuntimeError("existing RB-AGG updater receipt failed skill content-address check")
        return RBAggUpdateResult(
            stream_id=stream_id,
            update_receipt_path=str(receipt_path.resolve()),
            update_receipt_sha256=sha_file(receipt_path),
            skill_post_path=str(skill_path.resolve()),
            skill_post_sha256=sha_file(skill_path),
            evolved=bool(payload.get("evolved")),
            new_version_ids=tuple(payload.get("new_version_ids") or []),
            mindmemos_provider_calls=len(payload.get("adapter_receipts") or []),
            mindmemos_provider_total_tokens=sum(int(row.get("total_tokens") or 0) for row in payload.get("adapter_receipts") or []),
        )

    from mindmemos.components.skill import deserialize_bundle, serialize_bundle
    from mindmemos.config import QdrantConfig, SkillEvolutionConfig
    from mindmemos.infra.db import SkillVersionRepository
    from mindmemos.infra.db.models import AddRecordPoint
    from mindmemos.infra.db.qdrant import QdrantStore
    from mindmemos.mappers import to_skill_trace_summary_point
    from mindmemos.pipelines.skill import SkillVersionStore
    from mindmemos.pipelines.skill import evolution as evolution_module
    from mindmemos.pipelines.skill.evolution import SkillEvolver
    from mindmemos.typing import SkillTraceSummary
    from qdrant_client import AsyncQdrantClient

    client = AsyncQdrantClient(":memory:")
    qdrant_cfg = QdrantConfig(
        url="http://unused",
        add_record_collection="r17_rbagg_add_record",
        skill_version_collection="r17_rbagg_skill_version",
        skill_blob_collection="r17_rbagg_skill_blob",
        skill_trace_pending_collection="r17_rbagg_skill_trace_pending",
        skill_trace_summary_collection="r17_rbagg_skill_trace_summary",
        vector_size=2,
    )
    qdrant = QdrantStore(qdrant_cfg, client=client)
    await qdrant.ensure_schema()
    skill_repo = SkillVersionRepository(qdrant_cfg, engine=qdrant.engine)
    await skill_repo.ensure_schema()
    store = SkillVersionStore(skill_repo=skill_repo, add_record_repo=qdrant.add_record)
    evolver = SkillEvolver(
        store=store,
        skill_repo=skill_repo,
        add_record_repo=qdrant.add_record,
        llm_client=llm_adapter,
    )

    project_id = f"e2-r17-rbagg-{stream_id}"
    root = await store.register(
        project_id=project_id,
        name="xlsx",
        content=serialize_bundle({"SKILL.md": initial_skill_md}),
    )
    base_time = datetime(2026, 9, 2, tzinfo=UTC)
    provenance_rows: list[dict[str, Any]] = []

    for index, (pool, unit) in enumerate(zip(pools, aggregates)):
        add_id = rb_trace_uuid(stream_id, pool.task_id, pool.pool_id)
        created_at = base_time + timedelta(minutes=index)
        add_payload = build_rb_search_session_add_payload(
            unit=unit,
            project_id=project_id,
            task_completed_at=created_at.isoformat(),
            initial_skill_sha256=initial_skill_sha256,
            root_version_id=root.version_id,
            deterministic_add_record_id=add_id,
        )
        summary_payload = build_rb_precomputed_summary_payload(
            unit=unit,
            project_id=project_id,
            cloud_skill_id=root.cloud_skill_id,
            skill_name="xlsx",
            deterministic_add_record_id=add_id,
            created_at=created_at,
        )
        validate_rb_add_summary_pair(add_payload, summary_payload)
        await qdrant.upsert_add_record(AddRecordPoint(add_record_id=add_id, payload=add_payload))
        summary = SkillTraceSummary(
            summary_id=summary_payload["summary_id"],
            project_id=summary_payload["project_id"],
            cloud_skill_id=summary_payload["cloud_skill_id"],
            add_record_id=summary_payload["add_record_id"],
            skill_name=summary_payload["skill_name"],
            summary=summary_payload["summary"],
            created_at=summary_payload["created_at"],
            consumed_version_id=None,
            score=float(summary_payload["score"]),
            task_id=summary_payload["task_id"],
        )
        await skill_repo.upsert_summary(to_skill_trace_summary_point(summary))
        provenance_rows.append(
            {
                "task_id": pool.task_id,
                "pool_id": pool.pool_id,
                "add_record_id": add_id,
                "aggregate_memory_items_sha256": unit.memory_items_sha256,
                "aggregate_memory_item_count": unit.memory_item_count,
                "session_score": float(unit.acting_score),
                "source_trajectory_count": 8,
                "direct_mindmemos_trajectory_summary_call": False,
            }
        )

    # Fail closed if any search-session source record is not already represented
    # by exactly one precomputed summary before the first-party evolver is entered.
    existing = await evolver._existing_summaries(project_id, root.cloud_skill_id)
    expected_ids = {rb_trace_uuid(stream_id, pool.task_id, pool.pool_id) for pool in pools}
    if set(existing) != expected_ids or len(existing) != 8:
        raise RuntimeError("RB-AGG precomputed summary set is incomplete or contains extras")
    for summary_id, item in existing.items():
        if item.add_record_id != summary_id or item.score is None:
            raise RuntimeError("RB-AGG precomputed summary provenance/score drift")

    frozen_cfg = SkillEvolutionConfig(
        min_aggregate=8,
        max_aggregate=8,
        summary_concurrency=4,
        rewrite_skill=False,
        use_trajectory_score=True,
        evolved_status="draft",
        transcript_max_chars=transcript_max_chars,
        max_trace_scan=100,
    )

    class _Algo:
        skill_evolution = frozen_cfg

    class _Config:
        algo_config = _Algo()

    original_get_config = evolution_module.get_config
    evolution_module.get_config = lambda: _Config()
    try:
        update = await evolver.evolve(project_id=project_id, cloud_skill_id=root.cloud_skill_id)
        post_existing = await evolver._existing_summaries(project_id, root.cloud_skill_id)
    finally:
        evolution_module.get_config = original_get_config

    try:
        if not update.evolved or not update.new_version_id:
            raise RuntimeError(
                f"RB-AGG first-party SkillEvolver did not mint a version: pending={update.pending_count}; summarized={update.summarized_count}"
            )
        if update.summarized_count != 0:
            raise RuntimeError("RB-AGG unexpectedly invoked first-party trajectory summarization")
        if len(update.new_version_ids) != 1 or update.consumed_count != 8:
            raise RuntimeError("RB-AGG must mint exactly one version from eight precomputed summaries")
        post = await store.get_content(
            project_id=project_id,
            cloud_skill_id=root.cloud_skill_id,
            version_id=update.new_version_id,
        )
        skill_post_md = deserialize_bundle(post.content)["SKILL.md"]
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        temp_skill = skill_path.with_suffix(".md.tmp")
        temp_skill.write_text(skill_post_md, encoding="utf-8")
        os.replace(temp_skill, skill_path)
        adapter_receipts = llm_adapter.public_receipts()
        summary_rows = [
            {
                "summary_id": item.summary_id,
                "add_record_id": item.add_record_id,
                "task_id": item.task_id,
                "score": item.score,
                "summary_sha256": sha_text(item.summary),
                "consumed_version_id": item.consumed_version_id,
            }
            for item in sorted(post_existing.values(), key=lambda row: (str(row.task_id), row.summary_id))
        ]
        payload = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-rbagg-cloned-state-mindmemos-update",
            "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
            "status": "COMPLETED",
            "stream_id": stream_id,
            "semantic_role": "reasoningbank_style_precomputed_search_session_summaries_to_first_party_scored_patch",
            "mindmemos_commit": mindmemos_commit,
            "contract_sha256": contract_sha256,
            "authorization_sha256": authorization_sha256,
            "initial_skill_sha256": initial_skill_sha256,
            "summary_count": len(summary_rows),
            "new_first_party_trajectory_summaries": int(update.summarized_count),
            "precomputed_summary_consumed_count": int(update.consumed_count),
            "score_semantics": "search_session_best_of_k_acting_success_equal_to_win_winner_score",
            "provenance_rows": provenance_rows,
            "summaries": summary_rows,
            "evolved": bool(update.evolved),
            "new_version_ids": list(update.new_version_ids),
            "skill_post_path": str(skill_path.resolve()),
            "skill_post_sha256": sha_file(skill_path),
            "adapter_receipts": adapter_receipts,
            "mindmemos_provider_calls": len(adapter_receipts),
            "mindmemos_provider_total_tokens": sum(int(row.get("total_tokens") or 0) for row in adapter_receipts),
            "heldout_evaluations": 0,
            "scientific_effectiveness_evaluated": False,
        }
        temp_receipt = receipt_path.with_suffix(".json.tmp")
        temp_receipt.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temp_receipt, receipt_path)
        return RBAggUpdateResult(
            stream_id=stream_id,
            update_receipt_path=str(receipt_path.resolve()),
            update_receipt_sha256=sha_file(receipt_path),
            skill_post_path=str(skill_path.resolve()),
            skill_post_sha256=sha_file(skill_path),
            evolved=bool(update.evolved),
            new_version_ids=tuple(update.new_version_ids),
            mindmemos_provider_calls=len(adapter_receipts),
            mindmemos_provider_total_tokens=sum(int(row.get("total_tokens") or 0) for row in adapter_receipts),
        )
    finally:
        await client.close()


===== BOUND ARTIFACT: adapter_tests | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-posthold-rbagg-diagnostic-20260902/research_pipeline/test_e2_r17_rbagg_posthold.py =====
from __future__ import annotations

from datetime import datetime, timezone
import unittest

from research_pipeline.e2_r17_rbagg_posthold import (
    build_rb_aggregated_session_evidence,
    build_rb_precomputed_summary_payload,
    build_rb_search_session_add_payload,
    normalize_rb_memory_items,
    parse_rb_memory_items,
    validate_rb_add_summary_pair,
)


VALID = """# Memory Item 1
## Title Verify output structure
## Description Check the workbook structure before finalizing.
## Content Inspect the relevant sheet, cells, and formulas before returning the result.

# Memory Item 2
## Title Avoid stale references
## Description Re-resolve references after structural edits.
## Content After moving or inserting cells, verify that dependent formulas still point to the intended ranges."""


class RBAggPostholdTest(unittest.TestCase):
    def receipt(self):
        return {
            "sources": [
                {
                    "rollout_index": i,
                    "trajectory_sha256": f"sha-{i}",
                    "verifier_score": 1.0 if i == 3 else 0.0,
                    "verifier_label": "SUCCESS" if i == 3 else "FAILURE",
                    "raw_tokens": 1000 + i,
                    "rendered_tokens": 512,
                    "rendered_sha256": f"rendered-{i}",
                }
                for i in range(8)
            ]
        }

    def test_parser_and_canonicalization(self):
        items = parse_rb_memory_items(VALID)
        self.assertEqual(2, len(items))
        self.assertEqual(VALID, normalize_rb_memory_items(items))

    def test_parser_rejects_extra_prose(self):
        with self.assertRaises(ValueError):
            parse_rb_memory_items("Here are the memories:\n" + VALID)

    def test_parser_rejects_index_gap(self):
        with self.assertRaises(ValueError):
            parse_rb_memory_items(VALID.replace("# Memory Item 2", "# Memory Item 3"))

    def test_session_score_must_match_pool_source_max(self):
        with self.assertRaises(ValueError):
            build_rb_aggregated_session_evidence(
                task_id="task",
                pool_id="pool",
                acting_score=0.0,
                raw_memory_items=VALID,
                aggregation_receipt=self.receipt(),
            )

    def test_add_summary_pair_is_one_to_one_and_scored(self):
        unit = build_rb_aggregated_session_evidence(
            task_id="task",
            pool_id="pool",
            acting_score=1.0,
            raw_memory_items=VALID,
            aggregation_receipt=self.receipt(),
        )
        add = build_rb_search_session_add_payload(
            unit=unit,
            project_id="project",
            task_completed_at="2026-09-02T00:00:00+00:00",
            initial_skill_sha256="skill-sha",
            root_version_id="root-version",
            deterministic_add_record_id="rbagg-id",
        )
        summary = build_rb_precomputed_summary_payload(
            unit=unit,
            project_id="project",
            cloud_skill_id="cloud",
            skill_name="xlsx",
            deterministic_add_record_id="rbagg-id",
            created_at=datetime(2026, 9, 2, tzinfo=timezone.utc),
        )
        validate_rb_add_summary_pair(add, summary)
        self.assertEqual(1.0, add["score"])
        self.assertEqual(1.0, summary["score"])
        self.assertTrue(add["r17_rbagg_precomputed_summary_required"])
        self.assertTrue(add["r17_rbagg_direct_trajectory_summarization_forbidden"])

    def test_add_summary_pair_rejects_score_drift(self):
        unit = build_rb_aggregated_session_evidence(
            task_id="task",
            pool_id="pool",
            acting_score=1.0,
            raw_memory_items=VALID,
            aggregation_receipt=self.receipt(),
        )
        add = build_rb_search_session_add_payload(
            unit=unit,
            project_id="project",
            task_completed_at="2026-09-02T00:00:00+00:00",
            initial_skill_sha256="skill-sha",
            root_version_id="root-version",
            deterministic_add_record_id="rbagg-id",
        )
        summary = build_rb_precomputed_summary_payload(
            unit=unit,
            project_id="project",
            cloud_skill_id="cloud",
            skill_name="xlsx",
            deterministic_add_record_id="rbagg-id",
            created_at=datetime(2026, 9, 2, tzinfo=timezone.utc),
        )
        summary["score"] = 0.0
        with self.assertRaises(ValueError):
            validate_rb_add_summary_pair(add, summary)


if __name__ == "__main__":
    unittest.main()


===== BOUND ARTIFACT: rb_style_renderer | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-posthold-rbagg-diagnostic-20260902/research_pipeline/e2_r17_reasoningbank_style.py =====
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from research_pipeline.e2_r17_evidence_window import (
    MatchedEvidenceWindowRenderer,
    canonical_trajectory_text,
    select_head_tail,
)


RB_PINNED_COMMIT = "ed80611788292ea739f1effd31f16c53823b8a0d"
RB_PROMPT_RELATIVE_PATH = "WebArena/prompts/memory_instruction.py"
RB_PROMPT_NAME = "PARALLEL_SI"
RB_PER_TRAJECTORY_CAP_TOKENS = 512
RB_AGGREGATOR_MAX_OUTPUT_TOKENS = 1024
RB_AGGREGATOR_TEMPERATURE = 0.7


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def extract_literal_assignment(path: Path, name: str) -> str:
    """Extract a top-level literal string without importing the baseline module."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        value = ast.literal_eval(node.value)
        if not isinstance(value, str):
            raise RuntimeError(f"{name} in {path} is not a literal string")
        return value
    raise RuntimeError(f"literal assignment {name} not found in {path}")


def _task_text(payload: Mapping[str, Any]) -> str:
    for message in payload.get("messages") or []:
        if isinstance(message, Mapping) and str(message.get("role") or "") == "user":
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()
    raise ValueError("trajectory does not contain a user task message")


@dataclass(frozen=True)
class RBAggregationSourceReceipt:
    rollout_index: int
    trajectory_sha256: str
    verifier_score: float
    verifier_label: str
    raw_tokens: int
    rendered_tokens: int
    rendered_sha256: str


@dataclass(frozen=True)
class RBAggregationPromptReceipt:
    baseline_commit: str
    baseline_prompt_relative_path: str
    baseline_prompt_source_sha256: str
    baseline_system_prompt_sha256: str
    task_text_sha256: str
    per_trajectory_cap_tokens: int
    aggregator_temperature: float
    aggregator_max_output_tokens: int
    user_prompt_sha256: str
    sources: tuple[RBAggregationSourceReceipt, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["sources"] = [asdict(row) for row in self.sources]
        return payload


def render_rb_style_aggregation_prompt(
    *,
    trajectory_payloads: Sequence[Mapping[str, Any]],
    trajectory_sha256s: Sequence[str],
    reasoningbank_root: Path,
    renderer: MatchedEvidenceWindowRenderer,
) -> tuple[str, str, RBAggregationPromptReceipt]:
    """Build a provenance-bound paper-spec ReasoningBank-style aggregation input.

    This deliberately does NOT claim source-faithful ReasoningBank execution.
    It binds the official PARALLEL_SI prompt from a pinned checkout, but it makes
    per-trajectory verifier labels explicit because the public prompt describes
    successful/failed contrast while the public scaling concatenation does not
    clearly attach those labels. Every trajectory receives the same fixed 512
    token source cap; this richer aggregation arm is accounted separately from
    the one-slot WIN/MRW primary causal contrast.
    """
    if len(trajectory_payloads) != len(trajectory_sha256s):
        raise ValueError("payload/SHA lengths differ")
    if len(trajectory_payloads) < 2:
        raise ValueError("RB-AGG requires at least two trajectories")

    prompt_path = reasoningbank_root / RB_PROMPT_RELATIVE_PATH
    if not prompt_path.exists():
        raise FileNotFoundError(prompt_path)
    system_prompt = extract_literal_assignment(prompt_path, RB_PROMPT_NAME)

    task_text = _task_text(trajectory_payloads[0])
    if any(_task_text(payload) != task_text for payload in trajectory_payloads[1:]):
        raise ValueError("RB-AGG pool contains multiple task texts")

    parts = [f"**Query:** {task_text}"]
    source_rows: list[RBAggregationSourceReceipt] = []
    for index, (payload, trajectory_sha) in enumerate(zip(trajectory_payloads, trajectory_sha256s)):
        if sha256_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))) == trajectory_sha:
            # Some callers may bind canonical JSON rather than file bytes. This
            # branch is intentionally a no-op; the supplied SHA is still recorded.
            pass
        text = canonical_trajectory_text(payload)
        raw_tokens = renderer.encoding.encode(text)
        rendered_tokens = select_head_tail(raw_tokens, RB_PER_TRAJECTORY_CAP_TOKENS)
        rendered = renderer.encoding.decode(rendered_tokens)
        score = float(payload.get("score") or 0.0)
        label = "SUCCESS" if score >= 1.0 else "FAILURE"
        rollout_index = int(payload.get("rollout_index", index))
        parts.extend(
            [
                f"\n**Trajectory {index + 1} (rollout_index={rollout_index}, verifier={label}):**",
                rendered,
            ]
        )
        source_rows.append(
            RBAggregationSourceReceipt(
                rollout_index=rollout_index,
                trajectory_sha256=str(trajectory_sha),
                verifier_score=score,
                verifier_label=label,
                raw_tokens=len(raw_tokens),
                rendered_tokens=len(rendered_tokens),
                rendered_sha256=sha256_text(rendered),
            )
        )

    user_prompt = "\n".join(parts)
    receipt = RBAggregationPromptReceipt(
        baseline_commit=RB_PINNED_COMMIT,
        baseline_prompt_relative_path=RB_PROMPT_RELATIVE_PATH,
        baseline_prompt_source_sha256=sha256_bytes(prompt_path.read_bytes()),
        baseline_system_prompt_sha256=sha256_text(system_prompt),
        task_text_sha256=sha256_text(task_text),
        per_trajectory_cap_tokens=RB_PER_TRAJECTORY_CAP_TOKENS,
        aggregator_temperature=RB_AGGREGATOR_TEMPERATURE,
        aggregator_max_output_tokens=RB_AGGREGATOR_MAX_OUTPUT_TOKENS,
        user_prompt_sha256=sha256_text(user_prompt),
        sources=tuple(source_rows),
    )
    return system_prompt, user_prompt, receipt


===== BOUND ARTIFACT: parent_closeout | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-posthold-rbagg-diagnostic-20260902/generated/e2-r17-deepseek-v2-final-scientific-closeout-20260902.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-deepseek-v2-final-scientific-closeout",
  "date": "2026-09-02",
  "status": "HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS",
  "execution_status": "COMPLETE",
  "protocol_integrity_status": "PASS_REPAIR2_CONTINUATION_V2_FULL_INTEGRITY_READY_FOR_SINGLE_USE_ANALYSIS",
  "sample": {
    "paired_units": 48,
    "learned_states": 96,
    "heldout_units": 1728,
    "win_c_successes": 683,
    "mrw_successes": 703,
    "n_per_arm": 864
  },
  "primary_result": {
    "win_c_mean": 0.7905092592592593,
    "mrw_mean": 0.8136574074074074,
    "mean_difference_mrw_minus_win_c": 0.02314814814814815,
    "percentage_point_difference": 2.314814814814815,
    "exact_one_sided_sign_flip_p": 0.171875,
    "paired_stream_bootstrap_95_ci": [-0.018518518518518507, 0.06597222222222222],
    "paired_t_90_ci": [-0.017273596987843382, 0.06356989328413969],
    "equivalence_margin": 0.05555555555555555,
    "superiority_pass": false,
    "practical_equivalence_pass": false,
    "harm_pass": false
  },
  "direction_counts": {
    "streams_positive": 7,
    "streams_zero": 1,
    "streams_negative": 4,
    "replicates_positive": 25,
    "replicates_zero": 5,
    "replicates_negative": 18
  },
  "predeclared_descriptive_heterogeneity": {
    "allowed": true,
    "role": "per-stream mixed dose and effect; descriptive family grouping only",
    "new_significance_tests": false,
    "family_specific_significance_claim": false,
    "primary_status_changed": false
  },
  "artifact_bindings": {
    "full_integrity_audit": {
      "path": "generated/e2-r17-deepseek-v2-repair2-continuation-v2-final-integrity-audit-20260902.json",
      "sha256": "02c750de1141e3723542f8674aca6f993e919e9ddf83c1537196872fce4b7039"
    },
    "analysis_authorization": {
      "path": "generated/e2-r17-deepseek-v2-repair2-continuation-v2-analysis-authorization-20260902.json",
      "sha256": "cbf6afba1a62b7a574c153dbb24d8ea513ebec0de86882187c252abb3746fc7c"
    },
    "primary_analysis": {
      "path": "generated/e2-r17-deepseek-v2-repair2-continuation-v2-analysis-20260902.json",
      "sha256": "f736cf7107d4439105bc8d24ae4519f34f742b26439113d97b56f6a0c1dbd0ab"
    },
    "descriptive_heterogeneity": {
      "path": "generated/e2-r17-deepseek-v2-repair2-descriptive-heterogeneity-20260902.json",
      "sha256": "b0a62e80cb0c7d9815f4e0a8d443eb1a7f4b1fa493d4d7866da360e7be7dfae4"
    },
    "closeout_memo": {
      "path": "consultations/e2-r17-deepseek-v2-final-scientific-closeout-20260902.md",
      "sha256": "717b296579e6970b73b94554c12752423ec9aeff2b5391c1c1ddadebae34fde0"
    }
  },
  "claim_authority": {
    "numerically_positive_point_estimate": true,
    "mrw_causal_superiority": false,
    "practical_equivalence": false,
    "harm": false,
    "family_specific_effect": false,
    "mixed_dose_monotone_law": false,
    "prospective_regime_law": false
  },
  "execution_authority": {
    "additional_deepseek_tasks": false,
    "second_backbone": false,
    "public_benchmark": false,
    "rb_agg_rescue": false,
    "e3_regime_prediction": false,
    "paper_promotion": false,
    "submission": false
  },
  "next_scientific_state": "CURRENT_CONFIRMATORY_SAMPLE_CLOSED_FUTURE_WORK_REQUIRES_NEW_INDEPENDENT_PREREGISTRATION",
  "interpretation": "The integrity-audited DeepSeek confirmatory sample has a +2.31 percentage-point aggregate MRW point estimate, but the preregistered stream-level superiority test and positive bootstrap lower-bound gate do not pass. Practical equivalence and harm are also not established. Predeclared descriptive stream/family variation is compatible with heterogeneity but cannot rescue or reclassify the frozen HOLD result."
}


===== BOUND ARTIFACT: old_v3_plan | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-posthold-rbagg-diagnostic-20260902/generated/e2-r17-experiment-plan-v3-20260828.json =====
{
  "artifact_type": "e2-r17-experiment-plan-v3",
  "schema_version": "1.0",
  "date": "2026-08-28",
  "status": "V3_DUAL_REVIEW_REQUIRED_BEFORE_RUNTIME_PILOT",
  "scientific_authority": false,
  "supersedes_for_future_execution": "e2-r17-experiment-plan-v2",
  "preserves_history": true,
  "central_question": "Does best-of-K acting selection change the updater-visible evidence distribution on an exact frozen search pool so that winner-only learning is suboptimal for future frozen skill?",
  "novelty_boundary": {
    "published_collision": "ReasoningBank/MaTTS (ICLR 2026)",
    "cannot_claim": [
      "failed trajectories can improve memory",
      "successful and failed trajectories can be aggregated for learning",
      "test-time scaling creates additional learning signal",
      "memory and test-time scaling can be combined"
    ],
    "candidate_claims": [
      "exact same-pool separation of acting projection and learning projection",
      "compute-shielding evidence law as K changes",
      "budget-matched causal learning-projection intervention",
      "prospective regime prediction before confirmatory outcomes"
    ],
    "abstract_regime_law_requires_e3": true
  },
  "theory": {
    "rescue_identity": "A_K-A_1=P(Y_1=0,max_i Y_i=1)=V_pre(K)-V_winner(K)",
    "iid_rescue_mass": "Gamma_K(p)=(1-p)-(1-p)^K",
    "mixed_support": "M_K=P(any success AND any failure)",
    "iid_mixed_support": "M_K=1-p^K-(1-p)^K",
    "nested_pool_no_iid_monotonicity": {
      "acting_success": "nondecreasing",
      "winner_visible_failure": "nonincreasing",
      "full_pool_failure_availability": "nondecreasing",
      "mixed_pool_support": "nondecreasing"
    },
    "learning_factorization": "Delta_K=M_K*delta_K",
    "delta_positive_assumed": false
  },
  "historical_e0": {
    "summary_sha256": "533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366",
    "historical_decision": "HOLD",
    "rewritten": false,
    "k8": {
      "acting_success": "12/12",
      "mixed_pools": "8/12",
      "rescue_events": "1/12",
      "winner_visible_failures": "0/12",
      "hidden_failed_nonwinners": 16,
      "failure_family_support": "5/6"
    },
    "old_rescue_quota_extension_authorized": false
  },
  "controlled_split": {
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2",
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4",
    "outcome_blind": true,
    "failure_families": 6,
    "streams_per_family": 2,
    "e1_streams": 12,
    "tasks_per_stream": 8,
    "update_tasks": 96,
    "common_heldout_probes": 18
  },
  "e1_a_pool_support": {
    "k": 8,
    "actor_rollouts": 768,
    "updater_calls": 0,
    "freeze_all_96_pools_before_gate": true,
    "hard_gate": {
      "mixed_pool_count_minimum": "24/96",
      "exposed_stream_minimum": "8/12 streams",
      "mixed_pools_per_exposed_stream_minimum": "2/8",
      "protocol_integrity": "100%",
      "completed_unit_sha_revalidation": true,
      "rounding_or_waiver": false,
      "task_or_pool_replacement_after_support": false
    },
    "borderline_examples_are_failures": ["23/96", "7/12 exposed streams", "one mixed pool in an otherwise exposed stream"],
    "family_generalization_qualification": {
      "minimum_supported_families": "4/6",
      "controls_primary_e1_authorization": false,
      "if_failed": "pooled E1 may proceed if hard gate passes, but family-generalization and E3 family-ranking claims are blocked"
    }
  },
  "evidence_renderer": {
    "implementation": "research_pipeline/e2_r17_evidence_window.py",
    "tokenizer_package": "tiktoken",
    "tokenizer_version": "0.11.0",
    "encoding": "cl100k_base",
    "cap_tokens": 3072,
    "canonical_evidence": "non-system user/assistant/tool messages plus verifier score/message; provenance/provider metadata excluded",
    "pair_budget": "min(3072, raw_tokens(WIN), raw_tokens(MRW))",
    "truncation": "first one-third plus final two-thirds tokens",
    "padding": false,
    "exact_pair_token_parity_required": true,
    "dependency_or_version_drift": "FAIL_PILOT",
    "policy_selection_after_pilot": false
  },
  "e1_b_arms": {
    "WIN_A": {
      "role": "primary control",
      "source_trajectories_per_task": 1,
      "projection": "served winner"
    },
    "WIN_B": {
      "role": "identical-treatment updater stochasticity negative control",
      "source_trajectories_per_task": 1,
      "projection": "byte-identical updater input to WIN_A before provider calls"
    },
    "MRW": {
      "role": "primary causal intervention",
      "source_trajectories_per_task": 1,
      "projection": "served winner on nonmixed pool; deterministic lowest-index failed nonwinner on mixed pool",
      "extra_actor_calls": 0
    },
    "RB_AGG": {
      "role": "predeclared ReasoningBank collision diagnostic",
      "runs_regardless_of_mrw_go_hold": true,
      "label": "ReasoningBank-style same-pool aggregation",
      "official_source_faithful_reproduction": false,
      "requires_semantic_runtime_pilot": true
    }
  },
  "updater": {
    "substrate": "MindMemOS SkillEvolver",
    "batch_tasks": 8,
    "provider_retry": 0,
    "thinking": "disabled",
    "default_temperature_if_first_party_omits": 0.0,
    "resolved_model_must_be_requalified_per_execution_tranche": true,
    "parse_corrections": "explicit and counted",
    "historical_receipts_regenerated": false
  },
  "evaluation": {
    "probes_per_stream": 18,
    "k": 1,
    "same_probes_all_arms": true,
    "independent_causal_units": 12,
    "probe_rows_independent_units": false,
    "endpoint": "per-stream mean held-out success"
  },
  "statistics": {
    "equivalence_margin_absolute": "1/18 = 0.0555555556",
    "negative_control_first": {
      "contrast": "WIN_B-WIN_A",
      "test": "paired TOST alpha=0.05",
      "operational_ci": "90% paired-mean t CI entirely within [-1/18,+1/18]",
      "bootstrap_robustness": "90% paired bootstrap",
      "failure": "HOLD_UPDATER_STOCHASTICITY"
    },
    "primary_superiority": {
      "contrast": "MRW-WIN_A",
      "test": "exact one-sided sign-flip over all 4096 within-pair sign assignments",
      "alpha": 0.05,
      "paired_bootstrap": "10000 draws, 95% CI",
      "go": "negative-control equivalence AND mean>0 AND exact p<=0.05 AND bootstrap lower>0 AND integrity pass"
    },
    "qualified_null": {
      "test": "paired TOST alpha=0.05",
      "margin": "+/-1/18",
      "equivalent": "STOP_MRW_PRACTICALLY_NULL",
      "significantly_negative": "STOP_MRW_HARMFUL",
      "neither_superior_nor_equivalent": "HOLD_UNDERPOWERED_OR_HETEROGENEOUS"
    },
    "power_disclosure": {
      "paired_units": 12,
      "one_sided_alpha": 0.05,
      "target_power": 0.8,
      "paired_t_standardized_effect_required_approx": 0.7664,
      "equal_magnitude_sign_reference": "10/12 positive pairs required for one-sided sign probability below .05"
    }
  },
  "collision_interpretation": {
    "MRW_superior_RB_superior": "hidden search evidence has learning consequence; test minimal witness vs richer aggregation practical equivalence",
    "MRW_superior_RB_null": "minimal failed witness specifically useful under this updater; diagnose aggregation dilution",
    "MRW_null_RB_superior": "reject minimal witness as final repair; aggregation-sensitive effect overlaps ReasoningBank more strongly; narrow novelty",
    "MRW_equivalent_RB_equivalent": "central learning-consequence mechanism STOP on this substrate",
    "MRW_negative": "failed-witness repair rejected"
  },
  "published_baselines": {
    "headline": [
      "ReasoningBank/MaTTS — ICLR 2026",
      "PolySkill — ICLR 2026",
      "ACE — ICLR 2026",
      "Agent Workflow Memory — ICML 2025"
    ],
    "extended": ["SAGE — ACL 2026 Long"],
    "arxiv_only_not_headline": ["SkillCAT", "Branch2Skill", "SkillOpt", "RethinkSkill", "TSR"]
  },
  "external_lanes": {
    "source_faithful": {
      "model_substitution_allowed_under_source_faithful_label": false,
      "current_credential_state": "Ark configured; Google/OpenAI/Anthropic/SambaNova not configured on 69",
      "unavailable_at_submission_disclosure": "report unified rerun only and explicitly state source-model route was unavailable; never call it exact reproduction"
    },
    "unified_rerun": {
      "direct_method_ranking_allowed": true,
      "minimum_models_for_cross_model_claim": 2,
      "prefer_minimum_model_families": 2,
      "single_model_fallback": "report single-model result without robustness claim",
      "model_selection_uses_r17_gain": false
    }
  },
  "public_benchmarks_after_e1_go": {
    "primary": "WebArena",
    "secondary": "AppWorld",
    "additional": "SpreadsheetBench Verified-400 if budget permits"
  },
  "later_stages": {
    "e3": "prospective K/family prediction frozen before future outcomes; failure deletes regime-law claims",
    "e4": "multi-round persistent evolution separating online acting from frozen-skill value",
    "e5": "parallel-vs-sequential topology x winner/history-preserving learning"
  },
  "runtime_pilot": {
    "authorized_by_this_plan": false,
    "outcome_blind_effectiveness": true,
    "must_validate": [
      "exact tiktoken dependency and matched-window parity",
      "no system/provenance evidence leakage",
      "MRW changes projection only on mixed pools",
      "WIN_A/WIN_B byte-identical updater input before provider calls",
      "temperature=0/retry=0/thinking disabled receipts",
      "RB_AGG source-pool provenance and evidence accounting",
      "updater calls/tokens/latency/parse corrections for budget only",
      "SHA revalidation and missing-unit resume",
      "no model or method selection from R17 effectiveness"
    ]
  },
  "checkpoint_policy": {
    "immediate_persist": ["rollout", "prefix and K pools", "projection", "matched-window receipt", "updater", "held-out evaluation"],
    "raw_immutable": true,
    "summary_rebuildable": true,
    "resume_rehashes_completed_units": true,
    "sha_mismatch": "QUARANTINE_AND_STOP",
    "missing_unit_resume_only": true,
    "blind_relaunch_after_502_timeout": false
  },
  "budget": {
    "full_scientific_run_authorized": false,
    "known_e1_a_rollouts": 768,
    "must_be_measured_in_runtime_pilot": [
      "actor calls and tokens per rollout",
      "updater calls and tokens per stream/arm",
      "parse-correction rate",
      "held-out evaluation calls/tokens",
      "wall time",
      "hard budget ceiling"
    ]
  },
  "current_state": {
    "theory_tests": "PASS",
    "mixed_projection_tests": "PASS",
    "evidence_renderer_static_tests": "PASS",
    "updater_temperature_default_tests": "PASS",
    "targeted_tests_passed_total_at_v3_write": 29,
    "runtime_pilot": "NOT_AUTHORIZED",
    "e1_a": "NOT_AUTHORIZED",
    "e1_b": "NOT_AUTHORIZED",
    "public_full_runs": "NOT_AUTHORIZED"
  },
  "next_gate": "independent Kimi K3 + DeepSeek V4-Pro review of exact V3 before any outcome-blind runtime Pilot"
}


===== BOUND ARTIFACT: parent_repair2_contract | /data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-posthold-rbagg-diagnostic-20260902/generated/e2-r17-deepseek-v2-repair2-contract-20260831.json =====
{
  "actor": {
    "concurrency_per_probe": 1,
    "k": 1,
    "max_output_tokens": 8192,
    "max_turns": 10,
    "provider_retry_limit": 0,
    "requested_model": "deepseek-v4-pro",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "temperature": 0,
    "thinking": "disabled"
  },
  "actor_runtime": {
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv.freeze.txt",
    "freeze_sha256": "ed0e582bdd2ac7bac376d4287b3d38e6e3bf28a522016c14891b4f037635044e",
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv/bin/python",
    "qualification_path": "generated/e2-r17-runtime-dependency-qualification-r2-20260828.json",
    "qualification_sha256": "38a1614b049ed328165c85584017ae8f48340afea9cf247bb1dd20958265ef9b",
    "required_status": "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_RUNTIME_R2",
    "role": "actor_evaluator",
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-eval-venv"
  },
  "artifact_type": "e2-r17-deepseek-v2-repair2-continuation-contract",
  "authority": {
    "dual_preexecution_review": true,
    "execute_deepseek_v2": false,
    "gpt_scientific_execution": false,
    "kimi_scientific_execution": false,
    "paper_promotion": false,
    "public_benchmark": false,
    "qwen_scientific_execution": false,
    "repair2_continuation": false,
    "scientific_experiment": false,
    "submission": false
  },
  "bound_code": {
    "actor_runner": {
      "path": "scripts/run_e2_r17_actor_pool.py",
      "sha256": "20a81fbe06f3839cd17babfdb021407368493da61610bca33aae33df8d31ec14"
    },
    "analysis": {
      "path": "scripts/analyze_e2_r17_deepseek_v2_repair2.py",
      "sha256": "9b3c7f0aed465b69a19476138a00882a268b59f47460e8a2abb1bb39dd37eec8"
    },
    "preflight": {
      "path": "scripts/preflight_e2_r17_deepseek_v2_repair2.py",
      "sha256": "d4ff983111f61a802443f456d53d1693375e5d30ed6f90fb6c3a74d6ff89fa13"
    },
    "provider_budget": {
      "path": "research_pipeline/e2_r17_provider_budget.py",
      "sha256": "df819b30a31e62e007e3f85ae76aa8d06faefaa56e9acefe71ceadb9f8fce444"
    },
    "renderer": {
      "path": "research_pipeline/e2_r17_evidence_window_v2.py",
      "sha256": "6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7"
    },
    "repair2_manifest": {
      "path": "research_pipeline/e2_r17_repair2_manifest.py",
      "sha256": "ad358c792136ee247d0d6e0116c850af0cf678e3de88f04474af3e5466c74371"
    },
    "repair2_review": {
      "path": "scripts/run_e2_r17_deepseek_v2_repair2_review.py",
      "sha256": "250f4a5d2bb8cac4f877c37172e154f9201610b008826bb7862a69f89b97ab13"
    },
    "repair2_tests": {
      "path": "research_pipeline/test_e2_r17_deepseek_v2_repair2.py",
      "sha256": "1735ac87979afc83092a0ce0e5851761197a530c53d91fd6c2392c73332cd1b3"
    },
    "runner": {
      "path": "scripts/run_e2_r17_deepseek_v2_repair2_continuation.py",
      "sha256": "63206799b017b159b425053b31617bad010b00b6c8df0bcdf9e40a8e68101a2a"
    },
    "updater_adapter": {
      "path": "research_pipeline/e2_r17_mindmemos_ark_adapter.py",
      "sha256": "b3fb2bfbd98b185a9905d744c41fe6ca5cde1a2b52a0c7554cb8c28e2b48fcc8"
    },
    "updater_wrapper": {
      "path": "research_pipeline/e2_r17_mindmemos_updater.py",
      "sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d"
    }
  },
  "budget": {
    "actor_structural_max_calls_per_state": 180,
    "claim_before_provider_io": true,
    "claims_never_released": true,
    "hard_max_provider_calls_structural": 18336,
    "max_provider_calls_per_state": 191,
    "max_provider_calls_per_unit": 11,
    "planning_note": "V1 call rates are planning references only; hard ceiling is structural and symmetric across arms.",
    "states": 96,
    "updater_correction_max_calls": 11,
    "updater_nominal_calls": 10
  },
  "checkpoint": {
    "ambiguous_partial_provider_unit": "STOP_AND_ADJUDICATE",
    "automatic_relaunch": false,
    "completed_replicates": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-20260831/checkpoints/completed_replicates.jsonl",
    "immediate": true,
    "valid_replicates": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-20260831/checkpoints/valid_replicates.jsonl"
  },
  "compatibility_manifest": {
    "path": "generated/e2-r17-deepseek-v2-repair1-compatibility-manifest-20260831.json",
    "required_status": "PASS_REPAIR1_PREFIX_COMPATIBILITY_14_COMPLETE_PAIRS",
    "sha256": "61e243027e6d42f7923e249f6c88267e6db07ed4bccb32d5a50c8d13bf1695bb"
  },
  "date": "2026-08-31",
  "e1_a_pool_root": "/data/wyt/e2-r17-search-projection/runs/e1-a-v31-pool-support-v2-1-20260828",
  "e1_a_support": {
    "path": "generated/e2-r17-e1-a-pool-support-v2-1-adjudication-20260828.json",
    "required_status": "PASS_E1_A_SUPPORT_READY_FOR_SEPARATE_E1_B_CONTRACT",
    "sha256": "b2c611285c20377d77af7ea62448c6fee0d5973cd657687f6dde7f7fce6be6d7"
  },
  "env_file": ".env",
  "forbidden": [
    "GPT execution",
    "GPT/Kimi/Qwen scientific execution",
    "Kimi scientific execution",
    "Qwen scientific execution",
    "Repair1 relaunch or resume",
    "changing verifier",
    "deleting streams/replicates based on score",
    "directory-discovered inheritance",
    "margin widening",
    "operator semantic patch",
    "paper promotion or submission",
    "public benchmark execution",
    "public benchmark execution before DeepSeek V2 GO",
    "result-driven K/task/model changes",
    "score-based inheritance",
    "second scientific backbone",
    "single-arm resume",
    "third parse/apply attempt",
    "using V1 WIN-A/WIN-B as primary control"
  ],
  "freeze_note": "Repair2 freezes the reviewed outcome-blind continuation: 14 manifest-bound Repair1 pairs are inherited; 34 pairs are run fresh; max_parse_attempts=2 permits exactly one explicit receipted skill_patch_apply correction; updater/state budgets are 11/191; all scientific variables and frozen statistics remain unchanged.",
  "heldout": {
    "evaluation_k": 1,
    "never_fed_to_updater": true,
    "source_split": "e1_common_heldout_probe",
    "task_ids": [
      "r17-b4-agj-p2",
      "r17-b4-agj-p3",
      "r17-b4-agj-p8",
      "r17-b4-fmv-p1",
      "r17-b4-fmv-p2",
      "r17-b4-fmv-p8",
      "r17-b4-ioc-p1",
      "r17-b4-ioc-p4",
      "r17-b4-ioc-p6",
      "r17-b4-msp-p0",
      "r17-b4-msp-p7",
      "r17-b4-msp-p8",
      "r17-b4-ska-p4",
      "r17-b4-ska-p5",
      "r17-b4-ska-p8",
      "r17-b4-tsr-p0",
      "r17-b4-tsr-p6",
      "r17-b4-tsr-p8"
    ]
  },
  "inheritance_policy": {
    "failed_pair": "e1-fmv-01/rep2",
    "failed_pair_action": "fresh-run both WIN-C and MRW",
    "fallback_if_any_reviewer_p0": "STOP_REPAIR2_INHERITANCE; propose but do not execute full-fresh 48-pair Repair2",
    "frozen_candidate_pairs": 14,
    "provider_calls_for_inheritance": 0,
    "score_fields_read": false,
    "selection_basis": "pre-outcome integrity/completeness and attempt0 prefix identity only",
    "single_arm_resume": false
  },
  "initial_skill": {
    "path": "/data/wyt/evidence-substrates/MindMemOS-20260817/resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md",
    "sha256": "bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb"
  },
  "mindmemos": {
    "bound_files": {
      "src/mindmemos/mindmemos/pipelines/skill/evolution.py": "37bb22da6d4e8485d824c3c31e48f200561b05834a8a6bf3c057b29613b2bca0",
      "src/mindmemos/mindmemos/prompts/EN/skills/skill_patch.py": "48ab68ee3fbb6f115269679358cbcc1f08f9a28318a95438860eae1bbf5a3f4c",
      "src/mindmemos/mindmemos/prompts/EN/skills/trajectory_summary.py": "771a5dc2efc369ed8b4c6d90b5ee470339263780eaf26265be24561b7156b95e"
    },
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817"
  },
  "model_identity": {
    "fresh_max_output_tokens_smoke": 8192,
    "path": "generated/e2-r17-deepseek-v2-repair2-model-identity-adjudication-20260831.json",
    "provider_retry_limit": 0,
    "qualification_path": "generated/e2-r17-deepseek-v2-repair2-deepseek-identity-qualification-20260831.json",
    "qualification_sha256": "6f7305554f710ce56d07e86cbc786ab5d4618327f5b6c0161c7259067cae59ac",
    "required_status": "PASS_CURRENT_REVIEW_TRANCHE",
    "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
    "sha256": "491e4aa738260fab7c6331ee5a1e9a0d57b87df8411a01471c1df0564adf15ee",
    "thinking": "disabled"
  },
  "protocol_memo": {
    "path": "consultations/e2-r17-deepseek-v2-protocol-20260830.md",
    "sha256": "546981b691fda58a700d2b3c5af458eace92391810080d2b531c5ae111cf0300"
  },
  "protocol_v2_correction": {
    "path": "consultations/e2-r17-api-backbone-verifier-design-correction-20260830.md",
    "sha256": "8dc373ad86d09da993a3bc8e34926b267c48ff75d31a4cf4e6772de2a54d493f"
  },
  "protocol_version": "E2-R17-DEEPSEEK-V2-REPAIR2-CONTINUATION-v1",
  "purpose": "Outcome-blind continuation after deterministic updater patch-apply failure, with prefix-compatible inheritance and one explicit symmetric correction generation.",
  "renderer": {
    "arm_metadata_visible": false,
    "exact_final_retokenized_parity_required": true,
    "final_block_cap_tokens": 3072,
    "padding": false,
    "path": "research_pipeline/e2_r17_evidence_window_v2.py",
    "sha256": "6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7",
    "tokenizer_encoding": "cl100k_base",
    "tokenizer_package": "tiktoken",
    "tokenizer_version": "0.11.0"
  },
  "repair1_parent": {
    "authorization_path": "generated/e2-r17-deepseek-v2-replicated-paired-repair1-authorization-20260830.json",
    "authorization_sha256": "8301fa9d96768a86c802c06fbe04a02be552c5fa68195f709011b73c83b8dac5",
    "completed_pairs": 14,
    "contract_path": "generated/e2-r17-deepseek-v2-replicated-paired-repair1-contract-20260830.json",
    "contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
    "heldout_units": 504,
    "learned_states": 28,
    "scientific_scores_read": false,
    "terminal_state": "STOP_AND_ADJUDICATE_UPDATER_PATCH_APPLY_FAILURE"
  },
  "repair_lineage": {
    "all_scientific_variables_unchanged": true,
    "parent_contract_path": "generated/e2-r17-deepseek-v2-replicated-paired-repair1-contract-20260830.json",
    "parent_contract_sha256": "a4ce14dea5c5b0ab5509d97a072013a9924b592ae18c049b05d4edf707201f80",
    "repair_type": "single-variable explicit parse/apply correction policy"
  },
  "repair_note": "Only max_parse_attempts 1->2 and fail-close structural budgets 10->11, 190->191 change. Failed pair fresh-runs both arms; 14 complete pairs are inherited only if dual review passes.",
  "replication": {
    "approx_90pct_ci_halfwidth_at_null": 0.03605,
    "approx_power_at_delta_1_over_18_alpha_0_05": 0.828,
    "learned_states": 96,
    "nuisance_sd": 0.13905713715032014,
    "paired_replicate_units": 48,
    "replicates_per_stream": 4,
    "sample_size_prior_source": "V1 identical-treatment nuisance SD only",
    "scientific_independent_units": 12,
    "unit_definition": "D_s is the mean of four independent contemporaneous replicate differences within stream s"
  },
  "review_binding": {
    "status": "PASS_DEEPSEEK_KIMI_2_OF_2",
    "reviewers": [
      "deepseek-v4-pro",
      "kimi-k3"
    ],
    "required_verdict": "PASS_TO_SEPARATELY_AUTHORIZED_REPAIR2",
    "draft_contract_path": "generated/e2-r17-deepseek-v2-repair2-draft-contract-20260831.json",
    "draft_contract_sha256": "999498499649f873f1f0eff32593d9d2a2c788f843f0484af77cf8868ce89e26",
    "dual_review_summary_path": "generated/e2-r17-deepseek-v2-repair2-review-20260831/summary.json",
    "dual_review_summary_sha256": "d5ec1abdf52e0631c971fce56c24dd25032279ff5d0eefb1b7d5a797d2d83b24",
    "all_pass_to_separately_authorized_repair2": true,
    "verdicts": {
      "deepseek-v4-pro": "PASS_TO_SEPARATELY_AUTHORIZED_REPAIR2",
      "kimi-k3": "PASS_TO_SEPARATELY_AUTHORIZED_REPAIR2"
    },
    "resolved_models": {
      "deepseek-v4-pro": "deepseek-v4-pro-ga-260813",
      "kimi-k3": "kimi-k3"
    },
    "remaining_p0_p1_blockers": [],
    "scientific_backbone": "deepseek-v4-pro only",
    "second_backbone_authority": false,
    "paper_claim_authority": false,
    "freeze_transition_delta": [
      "status DRAFT_PENDING_DUAL_REPAIR2_REVIEW -> FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION",
      "dual_preexecution_review false -> true",
      "bind completed 2/2 review summary and verdicts",
      "correct stale Repair1-only freeze_note to describe the reviewed Repair2 continuation; no executable or statistical field changed"
    ]
  },
  "run_root": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-20260831",
  "runtime_reliability": {
    "cannot_filter_primary_estimand": true,
    "repair1_mrw_patch_apply_failure_count": 1,
    "report_by_arm": [
      "attempt0_success_count",
      "correction_required_count",
      "correction_success_count",
      "correction_failure_count"
    ],
    "secondary_only": true
  },
  "schema_version": "2.0",
  "statistics": {
    "alpha": 0.05,
    "bootstrap": {
      "interval": "95% paired stream bootstrap",
      "reps": 100000,
      "seed": 1718
    },
    "decision_priority": [
      "TOST equivalence -> STOP_MRW_PRACTICALLY_NULL",
      "otherwise positive sign-flip p<=.05 + bootstrap lower>0 -> GO",
      "otherwise significant negative sign-flip -> STOP_MRW_HARMFUL",
      "otherwise HOLD_MRW_UNDERPOWERED_OR_HETEROGENEOUS"
    ],
    "epsilon": 0.05555555555555555,
    "no_probe_or_replicate_pseudoreplication": true,
    "practical_null": "paired TOST; 90% t-CI strictly inside [-1/18,+1/18]",
    "primary_estimand": "Delta=mean_s D_s over 12 frozen streams",
    "primary_test": "exact one-sided sign-flip over 2^12 stream effects",
    "replicate_effect": "d_sr=J_sr(MRW)-J_sr(WIN-C)",
    "replicates_per_stream": 4,
    "stream_effect": "D_s=mean_r d_sr"
  },
  "status": "FROZEN_E2_R17_DEEPSEEK_V2_REPAIR2_CONTINUATION",
  "streams": [
    "e1-agj-00",
    "e1-agj-01",
    "e1-fmv-00",
    "e1-fmv-01",
    "e1-ioc-00",
    "e1-ioc-01",
    "e1-msp-00",
    "e1-msp-01",
    "e1-ska-00",
    "e1-ska-01",
    "e1-tsr-00",
    "e1-tsr-01"
  ],
  "suite": {
    "root": "/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2",
    "split_manifest_sha256": "aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9",
    "suite_manifest_sha256": "2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4"
  },
  "superseding_failure_analysis": {
    "path": "generated/e2-r17-deepseek-v2-repair1-updater-patch-apply-failure-20260831.json",
    "sha256": "c21ce2ef3fb4f4573c3f6f45cab8842fbb75dab8d61d256ee3985f24932b38fa"
  },
  "technical_quarantine": {
    "path": "generated/e2-r17-deepseek-v2-repair1-technical-quarantine-20260831.json",
    "required_status": "TECHNICAL_QUARANTINE_UPDATER_PATCH_APPLY_FAILURE",
    "sha256": "1908a3dfc472f835c204f7f9d5a66a9ee4b37093adb09a8d0c0f297b4b1abd7a"
  },
  "test_adjudication": {
    "path": "generated/e2-r17-deepseek-v2-repair2-test-adjudication-20260831.json",
    "required_status": "PASS_REPAIR2_TESTS_9_OF_9",
    "sha256": "ab86fef9695aafc355d7e91a20db9752724cdf646987c2efe73b0b586582920d"
  },
  "time_balance": {
    "contemporaneous_pairing_required": true,
    "evaluation_order": "SHA256(E2-R17-DEEPSEEK-V2-EVAL-PAIR-ORDER-v1|stream|replicate|task|arm)",
    "update_order": "SHA256(E2-R17-DEEPSEEK-V2-UPDATE-ORDER-v1|stream|replicate|arm)"
  },
  "treatment": {
    "arms": [
      "win_c",
      "mrw"
    ],
    "historical_win_a_win_b_excluded_from_primary_estimand": true,
    "mrw": "V3.1 arm-blinded deterministic first failed nonwinner on mixed pools and exact WIN-C evidence on nonmixed pools",
    "same_deterministic_workbook_verifier": true,
    "same_exact_search_pools": true,
    "same_heldout_probes": true,
    "same_initial_skill": true,
    "same_served_winner": true,
    "same_updater_config": true,
    "win_c": "V3.1 arm-blinded matched-window winner evidence"
  },
  "updater": {
    "adapter_path": "research_pipeline/e2_r17_mindmemos_ark_adapter.py",
    "adapter_sha256": "b3fb2bfbd98b185a9905d744c41fe6ca5cde1a2b52a0c7554cb8c28e2b48fcc8",
    "batch_size": 8,
    "correction_policy": "Only after skill_patch_apply attempt0 deterministic parse/apply failure: feed the exact error and complete prior response to the same model; attempt1 is visible, claimed, receipted; failure stops; no attempt2.",
    "first_party": "mindmemos.pipelines.skill.evolution.SkillEvolver",
    "max_correction_attempts": 1,
    "max_parse_attempts": 2,
    "provider_retry_limit": 0,
    "requested_model": "deepseek-v4-pro",
    "resolved_model": "deepseek-v4-pro-ga-260813",
    "score_semantics": "selected_evidence_trajectory",
    "temperature": 0,
    "thinking": "disabled",
    "transcript_max_chars": 100000,
    "wrapper_path": "research_pipeline/e2_r17_mindmemos_updater.py",
    "wrapper_sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d"
  },
  "updater_runtime": {
    "freeze_path": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv.freeze.txt",
    "freeze_sha256": "80cd6fdd8eb672e41252c099766fd171a5a7a4b90c284d87da87d09f0d559731",
    "litellm_local_model_cost_map": true,
    "post_lock_compatibility_override": {
      "disclosed": true,
      "package": "tiktoken",
      "reason": "pre-frozen V3.1 ExactMatchedEvidenceBlockRenderer compatibility",
      "version": "0.11.0"
    },
    "python_executable": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv/bin/python",
    "qualification_path": "generated/e2-r17-updater-runtime-qualification-20260829.json",
    "qualification_sha256": "f2319815cdcd7caf248c498c470720d4e3f6c9b5e579fad59914df687cdf5b6d",
    "required_entrypoint": "mindmemos.pipelines.skill.evolution.SkillEvolver",
    "required_status": "PASS_ZERO_PROVIDER_FULL_MINDMEMOS_UPDATER_RUNTIME",
    "role": "persistent_skill_updater",
    "venv_root": "/data/wyt/e2-r17-search-projection/mindmemos-updater-venv"
  },
  "v1_identifiability_hold": {
    "mrw_outcomes_observed_in_v1": false,
    "paired_nuisance_sd": 0.13905713715032014,
    "path": "generated/e2-r17-e1-b-negative-control-adjudication-20260829.json",
    "required_status": "HOLD_UPDATER_OR_EVALUATOR_STOCHASTICITY",
    "scientific_role": "preserved V1 scientific-identifiability result and nuisance-SD prior only; never a V2 control arm",
    "sha256": "758d7514518216c6913d623b9175f237a35a63c4f2f523fa24a3097d07515a2e"
  },
  "valid_replicate_manifest": {
    "allowed_sources": [
      "repair1_inherited",
      "repair2_fresh"
    ],
    "directory_discovery_forbidden": true,
    "path": "/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-20260831/checkpoints/valid_replicates.jsonl",
    "quarantine_excluded": true,
    "required_per_stream": 4,
    "required_rows": 48
  }
}


===== BOUND ARTIFACT: mindmemos_evolution_first_party | /data/wyt/evidence-substrates/MindMemOS-20260817/src/mindmemos/mindmemos/pipelines/skill/evolution.py =====
"""Skill self-evolution pipeline (design ``docs/skill``).

Flow for one ``cloud_skill_id`` (triggered by ``POST /v1/skills/evolve``):

1. Find every ``/v1/memory/add`` trace that ``injected`` this skill (a binding
   whose ``version_id`` belongs to the skill's lineage).
2. Count how many of those traces are *pending* — already-stored unconsumed
   summaries plus traces not yet summarized. If the count is below the evolution
   threshold, stop and report the shortfall (we summarize nothing).
3. Otherwise summarize the not-yet-summarized traces in parallel (bounded
   concurrency) with an LLM, storing each summary 1:1 with its add trace.
4. In add-time order, batch the pending summaries (``min_aggregate``..
   ``max_aggregate`` each) and, per batch, propose a patch against the current
   ``SKILL.md`` and apply it (optionally reformat), minting a new draft/cloud
   version chained on the previous head. Batches that would leave fewer than
   ``min_aggregate`` summaries are deferred to a later call.

Offline ``skill-rl`` aggregates many rollouts of ONE task; online we cannot
re-run a task, so summaries are aggregated ACROSS different tasks that injected
the same skill (see ``prompts/EN/skills``).
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Iterator, Sequence
from datetime import datetime
from typing import Any

from ...components.skill import apply_patch_ops, deserialize_bundle
from ...config import SkillEvolutionConfig, get_config
from ...errors import SkillBundleError
from ...infra.db import get_database_clients
from ...llm import get_llm_client, require_model_endpoint
from ...logging import get_logger, traced
from ...mappers import skill_trace_summary_from_record, to_skill_trace_summary_point
from ...prompts.EN.skills import (
    APPLY_PATCH_SYSTEM,
    PROPOSE_PATCH_SCORED_SYSTEM,
    PROPOSE_PATCH_SYSTEM,
    REWRITE_SKILL_SYSTEM,
    SUMMARY_SYSTEM,
    apply_patch_user,
    propose_patch_user,
    rewrite_skill_user,
    summarize_trajectory_user,
)
from ...typing import (
    SkillEvolveResult,
    SkillTraceSummary,
    SkillUsage,
    SkillVersion,
    SkillVersionStatus,
)
from ..memory_db import utcnow
from ..registry import create_pipeline, register
from .version_store import SkillVersionStore, get_skill_version_store

logger = get_logger(__name__)


class _Candidate:
    """One injected add trace eligible for summarization."""

    __slots__ = ("add_record_id", "created_at", "skill_name", "transcript", "score", "task_id")

    def __init__(
        self,
        add_record_id: str,
        created_at: datetime,
        skill_name: str,
        transcript: str,
        *,
        score: float | None = None,
        task_id: str | None = None,
    ) -> None:
        self.add_record_id = add_record_id
        self.created_at = created_at
        self.skill_name = skill_name
        self.transcript = transcript
        self.score = score
        self.task_id = task_id


@register(type="skill_evolve", name="trace_v2_summary")
class SkillEvolver:
    """Orchestrates summarize -> aggregate -> patch -> mint version for one skill.

    Registered as the ``trace_v2_summary`` evolve algorithm version (adapted from
    ``skill-rl``'s offline ``trace_v2_summary``); the active version is chosen via
    ``get_config().pipelines["skill_evolve"]``, like the ``add`` / ``search``
    pipeline families. Add new algorithm versions by registering another class
    under ``type="skill_evolve"``.

    Repositories and the LLM client are resolved lazily from the process globals
    so the evolver survives ``reset_*`` in tests/config reloads; they can be
    injected for unit tests.
    """

    def __init__(
        self,
        *,
        store: SkillVersionStore | None = None,
        skill_repo: Any = None,
        add_record_repo: Any = None,
        llm_client: Any = None,
    ) -> None:
        self._store = store
        self._skill_repo = skill_repo
        self._add_record_repo = add_record_repo
        self._llm = llm_client

    @property
    def store(self) -> SkillVersionStore:
        """Return the configured skill version store."""
        return self._store if self._store is not None else get_skill_version_store()

    @property
    def _skill(self):
        return self._skill_repo if self._skill_repo is not None else get_database_clients().skill

    @property
    def _add_record(self):
        return self._add_record_repo if self._add_record_repo is not None else get_database_clients().qdrant.add_record

    @property
    def llm(self):
        """Return the configured LLM client."""
        if self._llm is not None:
            return self._llm
        require_model_endpoint("chat")
        return get_llm_client()

    @traced("skill_evolver.evolve")
    async def evolve(self, *, project_id: str, cloud_skill_id: str) -> SkillEvolveResult:
        """Run one evolution pass for ``cloud_skill_id`` (see module docstring).

        Raises:
            SkillNotFoundError: If the cloud skill does not exist in this project.
        """

        cfg = get_config().algo_config.skill_evolution

        # Head version + current SKILL.md text (published head wins, else latest).
        summary = await self.store.get_skill(project_id=project_id, cloud_skill_id=cloud_skill_id)
        head = summary.published_head or summary.latest_version
        head_md = await self._head_skill_md(project_id, cloud_skill_id, head)

        version_ids = await self._lineage_version_ids(project_id, cloud_skill_id)
        existing = await self._existing_summaries(project_id, cloud_skill_id)
        candidates = await self._injected_candidates(project_id, version_ids, existing.keys(), cfg)
        unconsumed = [s for s in existing.values() if s.consumed_version_id is None]

        pending_count = len(unconsumed) + len(candidates)
        if pending_count < cfg.min_aggregate:
            logger.info(
                "skill evolution below threshold",
                cloud_skill_id=cloud_skill_id,
                pending_count=pending_count,
                threshold=cfg.min_aggregate,
            )
            return SkillEvolveResult(
                cloud_skill_id=cloud_skill_id,
                evolved=False,
                pending_count=pending_count,
                threshold=cfg.min_aggregate,
            )

        new_summaries = await self._summarize_candidates(project_id, cloud_skill_id, candidates, cfg)
        pending = sorted([*unconsumed, *new_summaries], key=lambda s: s.created_at)
        if len(pending) < cfg.min_aggregate:
            # Summarization failures dropped us back under the threshold.
            return SkillEvolveResult(
                cloud_skill_id=cloud_skill_id,
                evolved=False,
                pending_count=len(pending),
                threshold=cfg.min_aggregate,
                summarized_count=len(new_summaries),
            )

        new_versions: list[SkillVersion] = []
        consumed = 0
        parent_id = head.version_id
        skill_md = head_md
        status = self._evolved_status(cfg)
        for batch in _batches(pending, cfg.min_aggregate, cfg.max_aggregate):
            version, skill_md = await self._mint_version(
                project_id=project_id,
                parent_version_id=parent_id,
                skill_name=head.skill_name,
                skill_md=skill_md,
                batch=batch,
                status=status,
                cfg=cfg,
            )
            if version is None:
                break
            for item in batch:
                await self._skill.mark_summary_consumed(item.summary_id, version.version_id)
            new_versions.append(version)
            consumed += len(batch)
            parent_id = version.version_id

        if not new_versions:
            return SkillEvolveResult(
                cloud_skill_id=cloud_skill_id,
                evolved=False,
                pending_count=len(pending),
                threshold=cfg.min_aggregate,
                summarized_count=len(new_summaries),
            )

        return SkillEvolveResult(
            cloud_skill_id=cloud_skill_id,
            evolved=True,
            pending_count=len(pending),
            threshold=cfg.min_aggregate,
            new_version_id=new_versions[-1].version_id,
            new_version_ids=[v.version_id for v in new_versions],
            summarized_count=len(new_summaries),
            consumed_count=consumed,
        )

    async def _lineage_version_ids(self, project_id: str, cloud_skill_id: str) -> set[str]:
        versions = await self.store.versions_since(project_id=project_id, cloud_skill_id=cloud_skill_id)
        return {v.version_id for v in versions}

    async def _existing_summaries(self, project_id: str, cloud_skill_id: str) -> dict[str, SkillTraceSummary]:
        out: dict[str, SkillTraceSummary] = {}
        cursor = None
        while True:
            records, cursor = await self._skill.scroll_summaries(project_id, cloud_skill_id, cursor=cursor)
            for record in records:
                item = skill_trace_summary_from_record(record)
                out[item.add_record_id] = item
            if cursor is None:
                break
        return out

    async def _injected_candidates(
        self,
        project_id: str,
        version_ids: set[str],
        summarized_ids: Any,
        cfg: SkillEvolutionConfig,
    ) -> list[_Candidate]:
        """Scroll add traces, keeping injected, not-yet-summarized ones (oldest-first).

        Note: Qdrant disables cursor pagination when ``order_by`` is set (it always
        returns ``next_page_offset=None``), which would silently cap the scan at one
        page. We therefore paginate with the point-id cursor and sort the surviving
        candidates by ``task_completed_at`` in Python instead.
        """

        summarized = set(summarized_ids)
        candidates: list[_Candidate] = []
        scanned = 0
        cursor = None
        while scanned < cfg.max_trace_scan:
            page_limit = min(200, cfg.max_trace_scan - scanned)
            records, cursor = await self._add_record.scroll(project_id, limit=page_limit, cursor=cursor)
            for record in records:
                scanned += 1
                add_record_id = record.point_id
                if add_record_id in summarized:
                    continue
                skill_name = self._injected_skill_name(record.payload, version_ids)
                if skill_name is None:
                    continue
                transcript = _render_transcript(record.payload.get("messages") or [], cfg.transcript_max_chars)
                candidates.append(
                    _Candidate(
                        add_record_id=add_record_id,
                        created_at=_parse_dt(record.payload.get("task_completed_at")),
                        skill_name=skill_name,
                        transcript=transcript,
                        score=record.payload.get("score"),
                        task_id=record.payload.get("task_id"),
                    )
                )
            if cursor is None:
                break
        candidates.sort(key=lambda c: c.created_at)
        return candidates

    @staticmethod
    def _injected_skill_name(payload: dict[str, Any], version_ids: set[str]) -> str | None:
        for binding in payload.get("skill_bindings") or []:
            if binding.get("usage") == SkillUsage.INJECTED.value and binding.get("version_id") in version_ids:
                return binding.get("name") or ""
        return None

    async def _summarize_candidates(
        self,
        project_id: str,
        cloud_skill_id: str,
        candidates: Sequence[_Candidate],
        cfg: SkillEvolutionConfig,
    ) -> list[SkillTraceSummary]:
        if not candidates:
            return []
        semaphore = asyncio.Semaphore(max(1, cfg.summary_concurrency))

        async def run(candidate: _Candidate) -> SkillTraceSummary | None:
            async with semaphore:
                text = await self._summarize_one(candidate, cfg)
            if not text:
                return None
            item = SkillTraceSummary(
                summary_id=candidate.add_record_id,
                project_id=project_id,
                cloud_skill_id=cloud_skill_id,
                add_record_id=candidate.add_record_id,
                skill_name=candidate.skill_name,
                summary=text,
                created_at=candidate.created_at,
                score=candidate.score,
                task_id=candidate.task_id,
            )
            await self._skill.upsert_summary(to_skill_trace_summary_point(item))
            return item

        results = await asyncio.gather(*(run(c) for c in candidates))
        return [item for item in results if item is not None]

    async def _summarize_one(self, candidate: _Candidate, cfg: SkillEvolutionConfig) -> str | None:
        messages = [
            {"role": "system", "content": SUMMARY_SYSTEM},
            {"role": "user", "content": summarize_trajectory_user(candidate.skill_name, candidate.transcript)},
        ]
        try:
            reply = await self.llm.chat(task=cfg.summary_task, messages=messages)
        except Exception as exc:
            logger.warning("skill trajectory summary failed", add_record_id=candidate.add_record_id, error=str(exc))
            return None
        return (reply.content or "").strip() or None

    async def _mint_version(
        self,
        *,
        project_id: str,
        parent_version_id: str,
        skill_name: str,
        skill_md: str,
        batch: Sequence[SkillTraceSummary],
        status: SkillVersionStatus,
        cfg: SkillEvolutionConfig,
    ) -> tuple[SkillVersion | None, str]:
        """Propose+apply a patch for one batch and mint a child version.

        Returns ``(version, new_skill_md)``; ``(None, skill_md)`` if the LLM stage
        or registration failed (the caller stops and leaves the batch unconsumed).
        """

        try:
            patch = await self._propose_patch(skill_name, skill_md, batch, cfg)
            new_md = await self._apply_patch(skill_md, patch, cfg)
            if cfg.rewrite_skill:
                new_md = await self._rewrite(new_md, cfg)
        except Exception as exc:
            logger.warning("skill patch generation failed", parent_version_id=parent_version_id, error=str(exc))
            return None, skill_md

        new_md = (new_md or "").strip()
        if not new_md:
            logger.warning("skill patch produced empty content", parent_version_id=parent_version_id)
            return None, skill_md

        try:
            version = await self.store.create_evolved_version(
                project_id=project_id,
                parent_version_id=parent_version_id,
                name=skill_name,
                content=new_md,
                status=status,
            )
        except SkillBundleError as exc:
            logger.warning("evolved skill content rejected", parent_version_id=parent_version_id, error=str(exc))
            return None, skill_md
        return version, new_md

    async def _propose_patch(
        self, skill_name: str, skill_md: str, batch: Sequence[SkillTraceSummary], cfg: SkillEvolutionConfig
    ) -> str:
        """Propose a skill patch from trajectory summaries."""

        summaries = [s.summary for s in batch]
        scores = [s.score for s in batch]
        use_scores = cfg.use_trajectory_score and any(score is not None for score in scores)
        system = PROPOSE_PATCH_SCORED_SYSTEM if use_scores else PROPOSE_PATCH_SYSTEM
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": propose_patch_user(skill_name, skill_md, summaries, scores if use_scores else None),
            },
        ]
        reply = await self.llm.chat(task=cfg.patch_task, messages=messages)
        return (reply.content or "").strip()

    async def _apply_patch(self, skill_md: str, patch: str, cfg: SkillEvolutionConfig) -> str:
        """Apply the change plan as structured edit ops and return the new SKILL.md.

        The model emits only the changed spans (replace/insert/delete); the ops are
        applied deterministically to ``skill_md`` via the chat ``format_parser``. When
        an edit fails to apply (e.g. a non-unique anchor), ``feedback_on_parse_error``
        feeds the failed reply plus the ``SkillEditError`` back into the conversation
        so the retry can self-correct (add surrounding context, fix JSON) instead of
        re-running the identical prompt; the failure is also recorded to ClickHouse via
        the ``llm.chat.parse_error`` span event.
        """

        messages = [
            {"role": "system", "content": APPLY_PATCH_SYSTEM},
            {"role": "user", "content": apply_patch_user(skill_md, patch)},
        ]
        reply = await self.llm.chat(
            task=cfg.apply_task,
            messages=messages,
            format_parser=lambda content: apply_patch_ops(skill_md, content),
            feedback_on_parse_error=True,
        )
        return reply.parsed if reply.parsed is not None else (reply.content or "")

    async def _rewrite(self, skill_md: str, cfg: SkillEvolutionConfig) -> str:
        messages = [
            {"role": "system", "content": REWRITE_SKILL_SYSTEM},
            {"role": "user", "content": rewrite_skill_user(skill_md)},
        ]
        reply = await self.llm.chat(task=cfg.rewrite_task, messages=messages)
        return reply.content or ""

    async def _head_skill_md(self, project_id: str, cloud_skill_id: str, head: SkillVersion) -> str:
        content = await self.store.get_content(
            project_id=project_id, cloud_skill_id=cloud_skill_id, version_id=head.version_id
        )
        files = deserialize_bundle(content.content)
        # The canonical bundle keys are basenames; SKILL.md is the only whitelisted file.
        return files.get("SKILL.md", "")

    @staticmethod
    def _evolved_status(cfg: SkillEvolutionConfig) -> SkillVersionStatus:
        try:
            return SkillVersionStatus(cfg.evolved_status)
        except ValueError:
            logger.warning("invalid evolved_status, defaulting to draft", value=cfg.evolved_status)
            return SkillVersionStatus.DRAFT


def _batches(items: Sequence[SkillTraceSummary], min_size: int, max_size: int) -> Iterator[list[SkillTraceSummary]]:
    """Yield consecutive batches of ``min_size``..``max_size`` in order.

    Greedy: each batch takes up to ``max_size``; the loop stops once fewer than
    ``min_size`` items remain, leaving the remainder for a later evolve call. So
    10 items (min=4, max=8) yields one batch of 8 (2 deferred); 12 yields 8 + 4.
    """

    i = 0
    n = len(items)
    while n - i >= min_size:
        size = min(max_size, n - i)
        yield list(items[i : i + size])
        i += size


def _render_transcript(messages: list[Any], max_chars: int) -> str:
    """Render stored add ``messages`` into a compact transcript for the LLM."""

    lines: list[str] = []
    for message in messages:
        if not isinstance(message, dict):
            lines.append(_truncate(str(message), max_chars))
            continue
        if "role" in message and "content" in message:
            lines.append(f"[{message.get('role', '?')}] {_truncate(str(message.get('content', '')), max_chars)}")
        elif "text" in message:
            lines.append(f"[text] {_truncate(str(message.get('text', '')), max_chars)}")
        elif "url" in message:
            lines.append(f"[url] {message.get('url', '')}")
        elif "file_name" in message:
            lines.append(f"[file] {message.get('file_name', '')}")
        else:
            lines.append(_truncate(json.dumps(message, ensure_ascii=False), max_chars))
    return "\n".join(lines)


def _truncate(text: str, n: int) -> str:
    text = text.strip()
    if n <= 0 or len(text) <= n:
        return text
    head = text[: n // 2]
    tail = text[-n // 2 :]
    return f"{head}\n…[{len(text) - n} chars elided]…\n{tail}"


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass
    return utcnow()


_evolver: Any = None
_evolver_name: str | None = None


def get_skill_evolver() -> Any:
    """Process-global skill-evolve pipeline, selected by config.

    Builds the algorithm version named in ``get_config().pipelines["skill_evolve"]``
    via the pipeline registry, rebuilding if that name changes (config reload).
    """

    global _evolver, _evolver_name
    name = get_config().pipelines["skill_evolve"]
    if _evolver is None or _evolver_name != name:
        _evolver = create_pipeline(type="skill_evolve", name=name)
        _evolver_name = name
    return _evolver


===== BOUND ARTIFACT: mindmemos_skill_typing_first_party | /data/wyt/evidence-substrates/MindMemOS-20260817/src/mindmemos/mindmemos/typing/skill.py =====
"""Skill version-store DTOs (design `docs/skill/design-human.md`).

These are pure business contracts for the lightweight git-like skill version
store. They describe the identity, lineage and lifecycle of a skill version plus
the per-turn ``skill_context`` reference carried by ``/v1/memory/add``.

Identity recap (design §1):

- ``content_hash`` is the "tree": SHA-256 over the whitelisted, normalized bundle
  files. It only says "is the content the same", it does not carry name/version.
- ``version_id`` is the "commit": the authoritative primary key. It is derived
  deterministically from ``(project_id, content_hash, parent_version_id)``.
- ``cloud_skill_id`` is the "repo": it groups all versions of one skill by
  lineage (parent chain), not by name.
- ``version_label`` is the "tag": display-only, may repeat, never part of
  identity.

DTOs here never import ``mindmemos.infra.db`` and never touch Qdrant; the
business <-> DB mapping lives in ``mindmemos.mappers``.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class SkillVersionStatus(str, Enum):
    """Lifecycle status of a skill version (design §3 state machine).

    ``observed ─┐``
    ``draft     ┴─→ evaluating ─→ published ─→ superseded``
    ``                                 └──────→ rolled_back``
    """

    OBSERVED = "observed"
    DRAFT = "draft"
    EVALUATING = "evaluating"
    PUBLISHED = "published"
    SUPERSEDED = "superseded"
    ROLLED_BACK = "rolled_back"


class SkillOrigin(str, Enum):
    """Where a skill version came from (design §3)."""

    EDGE = "edge"
    CLOUD = "cloud"


class SkillUsage(str, Enum):
    """How a skill was used within the recognized turn (design §4.3 / §5.1)."""

    INJECTED = "injected"
    MODIFIED = "modified"


class SkillVersion(BaseModel):
    """Purpose: Version metadata of one skill version (the "commit").

    Used in: skill version-store repository, ``/v1/skills/register`` and
    ``/v1/skills/*`` read endpoints. ``version_id`` is the authoritative key;
    ``parent_version_id`` is the lineage link (``None`` for a root version);
    ``cloud_skill_id`` groups the whole lineage. The actual bundle text lives in
    a separate ``SkillBlob`` keyed by ``content_hash``.
    """

    version_id: str
    project_id: str
    cloud_skill_id: str
    skill_name: str
    content_hash: str
    parent_version_id: str | None = None
    version_label: str | None = None
    status: SkillVersionStatus
    origin: SkillOrigin
    created_at: datetime


class SkillBlob(BaseModel):
    """Purpose: Deduplicated bundle content keyed by ``(project_id, content_hash)``.

    Used in: skill version-store repository and ``.../versions/{id}/content``.
    ``content`` is the canonical text representation of the whitelisted bundle
    files (see ``components/skill``); identical content is stored once per
    project.
    """

    project_id: str
    content_hash: str
    content: str
    created_at: datetime


class SkillContext(BaseModel):
    """Purpose: Per-turn reference to a hit skill, carried by ``/v1/memory/add``.

    Used in: ``/v1/memory/add`` request and trace binding (design §2.1 / §5.1).
    Carries no full bundle text — only the connecting keys. ``base_version_id``
    is the version the local skill derived from and is an empty string before the
    first registration.
    """

    name: NonEmptyStr
    content_hash: NonEmptyStr
    base_version_id: str = ""
    version_label: NonEmptyStr | None = None
    usage: SkillUsage | None = None


class SkillBinding(BaseModel):
    """Purpose: Resolved per-skill binding recorded on one add trace.

    Used in: ``/v1/memory/add`` trace binding (design §2.1 / §5.1). One add can
    carry several ``SkillContext`` entries, so the trace (the ``add_record_v1``
    point) stores a list of these bindings rather than a single ``version_id``.
    ``version_id`` is ``None`` while the skill content is not yet registered: the
    trace is parked in ``skill_trace_pending_v1`` and the binding is filled in by
    rebind once ensure/register uploads the content.
    """

    name: str
    content_hash: str
    base_version_id: str = ""
    version_id: str | None = None
    version_label: str | None = None
    usage: SkillUsage | None = None


class SkillTracePending(BaseModel):
    """Purpose: A trace whose skill content is not yet registered (design §2.1).

    Used in: ``skill_trace_pending_v1``. When add carries a ``content_hash`` that
    has no matching version under ``base_version_id`` yet, the trace is parked
    here; once ensure registers the content, all same-key pending traces are
    rebound in batch. ``add_record_id`` points back at the ``add_record_v1`` point
    whose ``skill_bindings`` entry must be filled in on rebind; ``trace_id`` is the
    pending point's own unique id (so several skills missed in the same add do not
    collide).
    """

    trace_id: str
    project_id: str
    content_hash: str
    base_version_id: str = ""
    add_record_id: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SkillTraceSummary(BaseModel):
    """Purpose: Analytical summary of one injected add trajectory (self-evolution).

    Used in: ``skill_trace_summary_v1`` and the ``SkillEvolver`` pipeline. Stored
    1:1 with the originating ``/v1/memory/add`` trace (``add_record_id`` is the
    point id), so re-summarizing the same trace overwrites rather than
    duplicates. ``consumed_version_id`` is set once the summary has been folded
    into an evolved skill version, so a later evolve call does not re-use it;
    ``created_at`` mirrors the add's completion time and drives the add-order
    batching of multiple versions. ``score`` and ``task_id`` are copied from the
    originating add trace: ``score`` is the trajectory evaluation grade and
    ``task_id`` groups multiple rollout trajectories of the same task; both stay
    ``None`` when the add did not carry them.
    """

    summary_id: str
    project_id: str
    cloud_skill_id: str
    add_record_id: str
    skill_name: str
    summary: str
    created_at: datetime
    consumed_version_id: str | None = None
    score: float | None = None
    task_id: str | None = None


class SkillEvolveResult(BaseModel):
    """Purpose: Outcome of one ``POST /v1/skills/evolve`` call.

    Used in: the skill evolution endpoint. ``evolved`` is false when the pending
    summary count did not meet the threshold; the caller then reads
    ``pending_count`` / ``threshold`` to know how many more trajectories are
    needed. When ``evolved`` is true, ``new_version_id`` is the newest minted
    version and ``new_version_ids`` lists every version minted this call (one per
    serial batch, oldest-first).
    """

    cloud_skill_id: str
    status: Literal["ok", "queued"] = "ok"
    evolved: bool
    pending_count: int
    threshold: int
    new_version_id: str | None = None
    new_version_ids: list[str] = Field(default_factory=list)
    summarized_count: int = 0
    consumed_count: int = 0


class SkillSummary(BaseModel):
    """Purpose: Project-scoped summary of one managed cloud skill.

    Used in: ``GET /v1/skills`` and ``POST /v1/skills/{cloud_skill_id}/get``.
    ``latest_version`` is the newest metadata row for display and history
    anchoring; ``published_head`` is the version SDKs may checkout by default and
    can be ``None`` while only observed/edge versions exist.
    """

    cloud_skill_id: str
    skill_name: str
    latest_version: SkillVersion
    published_head: SkillVersion | None = None


class SkillContent(BaseModel):
    """Purpose: Full canonical bundle text for one skill version.

    Used in: ``GET .../versions/{version_id}/content``. The metadata stays next
    to the content so callers can update local registries without an extra
    lookup.
    """

    version: SkillVersion
    content: str


class SkillSyncRequestItem(BaseModel):
    """Purpose: One local skill state reported by SDK sync.

    Used in: ``POST /v1/skills/sync``. ``local_version_id`` is the version the
    edge currently has checked out; the cloud compares it with the published
    head for the same ``cloud_skill_id``.
    """

    cloud_skill_id: NonEmptyStr
    local_version_id: NonEmptyStr


class SkillSyncResult(BaseModel):
    """Purpose: Published-head diff result for one skill during sync.

    Used in: ``POST /v1/skills/sync``. ``has_update`` is true only when a
    published head exists and differs from the local version. ``gating_status``
    remains explicit so SDKs can distinguish "no published candidate yet" from
    a clean up-to-date state.
    """

    cloud_skill_id: str
    local_version_id: str
    has_update: bool
    published_head: SkillVersion | None = None
    gating_status: str


===== BOUND ARTIFACT: mindmemos_skill_patch_prompt_first_party | /data/wyt/evidence-substrates/MindMemOS-20260817/src/mindmemos/mindmemos/prompts/EN/skills/skill_patch.py =====
"""Skill-patch prompts: propose a patch from summaries, then apply it.

Adapted from ``skill_rl.evolve.prompts`` (``propose_multi_from_summary_user`` +
the skill-quality principles). The offline algorithm pools rollouts of ONE task;
online we cannot re-run a task, so the proposer reasons ACROSS several different
tasks that all injected the same skill and keeps only what generalizes.

Three stages:

- ``PROPOSE_PATCH_SYSTEM`` / ``PROPOSE_PATCH_SCORED_SYSTEM`` /
  :func:`propose_patch_user` -> a human-readable patch describing the minimal,
  general edits to make. The scored variant is selected when the batch carries
  trajectory evaluation scores, so the proposer can reinforce behaviors from
  high-score sessions and discourage those recurring in low-score ones; without
  scores it falls back to the unsupervised variant.
- ``APPLY_PATCH_SYSTEM`` / :func:`apply_patch_user` -> a small list of
  LINE-ADDRESSED edit ops (replace / insert / delete by line number) that are
  applied deterministically by ``components.skill.edit``. The model is shown the
  SKILL.md with a ``N|`` gutter and emits line numbers, the NEW text, and a short
  prefix of the addressed old line as a guard against line-number mistakes.
- ``REWRITE_SKILL_SYSTEM`` / :func:`rewrite_skill_user` -> an optional
  format-repair pass, gated by config.
"""

from __future__ import annotations

# Three principles that distinguish a high-quality skill edit from vague advice
# (verbatim intent from skill_rl's SKILL_QUALITY_PRINCIPLES).
_SKILL_QUALITY_PRINCIPLES = (
    "Follow these three principles for a GOOD skill edit:\n"
    "1. Failure Mechanism Encoding -- explain WHY an agent fails, not just that "
    "it should be careful. State the concrete mechanism, not a vague 'remember to "
    "validate'.\n"
    "2. Actionable Specificity -- give an executable action, not an attitude. "
    "Every warning should come with the concrete step that avoids it.\n"
    "3. High-Risk Action Blacklist -- explicitly forbid dangerous behaviors. Name "
    "the prohibited action and the failure it causes."
)

PROPOSE_PATCH_SYSTEM = (
    "You maintain a reusable SKILL.md that guides an autonomous agent on a class "
    "of tasks. You are given the current skill and a batch of analytical "
    "summaries drawn from SEVERAL DIFFERENT real sessions that all used this "
    "skill. There is no success/failure label.\n\n"
    "Treat the batch as field observations. Reading ACROSS the different tasks, "
    "infer recurring behaviors that look reliably helpful, mistakes or dead-ends "
    "that show up repeatedly, and missing general guidance that would make FUTURE "
    "agents more reliable. Favor patterns that GENERALIZE across tasks; never "
    "overfit to one task's values, filenames, contents, or exact answers.\n\n"
    "Propose a MINIMAL, GENERAL patch as a human-readable change plan: a short "
    "list of concrete edits (add / revise / remove guidance), each with the "
    "exact text to add or change and a one-line rationale. If the current skill "
    "already covers the useful lessons, say so and propose NO edits.\n\n" + _SKILL_QUALITY_PRINCIPLES
)


PROPOSE_PATCH_SCORED_SYSTEM = (
    "You maintain a reusable SKILL.md that guides an autonomous agent on a class "
    "of tasks. You are given the current skill and a batch of analytical "
    "summaries drawn from SEVERAL DIFFERENT real sessions that all used this "
    "skill. EACH summary is LABELED with a trajectory evaluation score: higher "
    "means the session went better, lower means it went worse. Scores are "
    "comparable within this batch; treat them as relative reward, not absolute "
    "grades.\n\n"
    "Use the scores as your PRIMARY signal. Reading ACROSS the different tasks, "
    "identify behaviors that recur in HIGH-score sessions and reinforce them as "
    "guidance, and identify mistakes, dead-ends, or risky actions that recur in "
    "LOW-score sessions and add guidance that steers FUTURE agents away from "
    "them. When a behavior appears in both high- and low-score sessions, it does "
    "not discriminate outcome -- do not encode it. Favor patterns that GENERALIZE "
    "across tasks; never overfit to one task's values, filenames, contents, or "
    "exact answers, and never hard-code a single session's score into the skill.\n\n"
    "Propose a MINIMAL, GENERAL patch as a human-readable change plan: a short "
    "list of concrete edits (add / revise / remove guidance), each with the "
    "exact text to add or change and a one-line rationale tied to the score "
    "evidence (e.g. 'recurs in low-score sessions'). If the current skill "
    "already covers the lessons the scores point to, say so and propose NO "
    "edits.\n\n" + _SKILL_QUALITY_PRINCIPLES
)


def propose_patch_user(
    skill_name: str,
    skill_md: str,
    summaries: list[str],
    scores: list[float | None] | None = None,
) -> str:
    """Handle propose patch user."""

    blocks = []
    for i, summary in enumerate(summaries, start=1):
        score = scores[i - 1] if scores is not None and i - 1 < len(scores) else None
        header = f"## Observation {i}"
        if score is not None:
            header += f" (score: {score:g})"
        blocks.append(f"{header}\n{summary.strip()}")
    joined = "\n\n".join(blocks) if blocks else "(no summaries)"
    has_scores = scores is not None and any(s is not None for s in scores)
    signal = "Using the scores as the PRIMARY signal" if has_scores else "Using the summaries as the PRIMARY signal"
    return (
        f"# Skill name\n{skill_name}\n\n"
        f"# Current SKILL.md\n{skill_md}\n\n"
        f"# Trajectory summaries from {len(summaries)} different sessions\n{joined}\n\n"
        f"{signal}, propose a minimal, general "
        "change plan for SKILL.md per your instructions. If nothing worth changing "
        "recurs across the sessions, state that no edits are needed."
    )


APPLY_PATCH_SYSTEM = (
    "You apply an approved change plan to a SKILL.md file using LINE-ADDRESSED "
    "EDIT OPERATIONS instead of rewriting the whole document. You are given the "
    "current SKILL.md with a line-number gutter (each line is prefixed by its "
    "number and a '|', e.g. '12| - Validate input'). The gutter is NOT part of "
    "the document -- never reproduce it in your output.\n\n"
    "Output a single JSON object with an 'edits' array. Each edit is one of:\n"
    '  {"op": "replace", "start": <line>, "end": <line>, "new": "<replacement text>", "old_string_prefix": "<first 40-120 chars of line `start` without its number>"}\n'
    '  {"op": "delete",  "start": <line>, "end": <line>, "old_string_prefix": "<first 40-120 chars of line `start` without its number>"}\n'
    '  {"op": "insert",  "after": <line>, "new": "<text>"}\n\n'
    "Line numbers are 1-based and INCLUSIVE: replace/delete with start=6,end=8 "
    "act on lines 6, 7 and 8. 'insert' places 'new' AFTER the given line; use "
    '"after": 0 to prepend at the very top, and "after": <last line number> to '
    "append at the end.\n\n"
    "Rules:\n"
    "1. Reference line numbers from the gutter. On replace/delete, include "
    "'old_string_prefix' -- a short prefix copied from the line at 'start' "
    "(without its 'N| ' prefix) to catch a wrong number. Use enough text to "
    "identify the line, usually 40-120 characters; do NOT copy a very long line "
    "in full. If the prefix does not match, you will be asked to fix the number.\n"
    "2. Apply exactly the edits in the plan; do not invent unrelated changes and "
    "do not touch the frontmatter unless the plan says so.\n"
    "3. Prefer the smallest edit that does the job: replace one line or a short "
    "run of lines, insert a new bullet after a related one, delete an obsolete "
    "line. Keep the result coherent, non-redundant, and concise.\n"
    "4. 'new' is the literal replacement/inserted text WITHOUT any line-number "
    "prefix. Write it as one or more whole lines; for multiple lines embed '\\n' "
    "between them. The system owns line separators -- it places 'new' on its own "
    "line(s), so you do NOT need leading/trailing newlines to avoid fusing onto "
    "neighbors. To insert a blank line (e.g. before a new '## ' heading), include "
    "an empty line inside 'new' (e.g. \"\\n## Blacklist\\n- ...\").\n"
    "5. replace/delete ranges MUST NOT overlap each other. To both change a line "
    "and add nearby guidance, use one 'replace' plus a separate 'insert'.\n"
    "6. To add a new bullet to a list, 'insert' after the last existing bullet's "
    "line. To add a brand-new section, 'insert' after the line where it belongs "
    '(or "after": <last line> for the end).\n'
    '7. If the plan says no edits are needed, return {"edits": []}.\n'
    "Output ONLY the JSON object -- no commentary and no markdown code fences."
)


def apply_patch_user(skill_md: str, patch: str) -> str:
    """Build the apply prompt from the current skill and the proposed patch.

    The SKILL.md is rendered with a line-number gutter so the model can address
    edits by line; :func:`mindmemos.components.skill.edit.format_numbered` produces
    the same numbering the applier uses.
    """

    from ....components.skill import format_numbered

    return (
        f"# Current SKILL.md (with line-number gutter; the 'N| ' prefix is NOT part of the file)\n"
        f"{format_numbered(skill_md)}\n\n"
        f"# Change plan to apply\n{patch}\n\n"
        "Return the JSON 'edits' object that applies this change plan to the "
        "SKILL.md above. Reference lines by their gutter numbers and put the new "
        "text in 'new'; include 'old_string_prefix' on every replace/delete."
    )


REWRITE_SKILL_SYSTEM = (
    "You are a Markdown format-repair editor for a SKILL.md file. Your ONLY job "
    "is to repair presentation damage introduced by automated edits: missing "
    "newlines between bullets or sentences, bullets fused onto previous lines, "
    "headings fused onto paragraphs, malformed list spacing, and accidental "
    "paragraph wrapping problems.\n\n"
    "This is NOT a content rewrite. Treat every existing instruction as frozen "
    "text. Do not improve, simplify, deduplicate, merge, reorder, reinterpret, "
    "or remove guidance. Do not add new guidance, examples, tools, strategies, "
    "warnings, rationales, headings, or sections. Do not change terminology or "
    "wording except for the minimum punctuation/whitespace needed to separate "
    "already-present text into valid Markdown lines.\n\n"
    "Rules:\n"
    "1. Preserve the complete YAML frontmatter exactly, including all fields and "
    "values.\n"
    "2. Preserve code blocks exactly, including language tags and code text. You "
    "may only add missing blank lines before or after a code block if needed.\n"
    "3. Split fused bullets such as 'range.- Be careful' into separate Markdown "
    "lines, preserving the words of both pieces.\n"
    "4. Split fused headings such as 'rows.## Data Entry' so the heading starts "
    "on its own line, preserving the heading text.\n"
    "5. Split fused sentences only when the missing boundary is clear. Preserve "
    "the sentence wording exactly.\n"
    "6. Keep the original order of all guidance. If two adjacent instructions "
    "repeat each other, leave both in place.\n"
    "7. Output the complete SKILL.md after format repair only.\n\n"
    "Output ONLY the full SKILL.md text -- no commentary, no JSON, no markdown "
    "code fences around the whole document."
)


def rewrite_skill_user(skill_md: str) -> str:
    """Build the optional reformatting prompt for a patched skill."""

    return (
        f"# SKILL.md to reformat\n{skill_md}\n\n"
        "Return the complete SKILL.md after a format-only repair pass. Do not "
        "add, delete, merge, deduplicate, reorder, summarize, or rewrite any "
        "instruction; only fix Markdown line breaks, list boundaries, heading "
        "boundaries, and spacing."
    )


===== BOUND ARTIFACT: reasoningbank_memory_instruction | /data/wyt/e2-r17-search-projection/baselines/published/reasoning-bank/WebArena/prompts/memory_instruction.py =====
# Copyright 2026 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

SUCCESSFUL_SI = """
You are an expert in web navigation. You will be given a user query, the corresponding trajectory that represents **how an agent successfully accomplished the task**. 

## Guidelines
You need to extract and summarize useful insights in the format of memory items based on the agent's successful trajectory.
The goal of summarized memory items is to be helpful and generalizable for future similar tasks.

## Important notes
  - You must first think why the trajectory is successful, and then summarize the insights.
  - You can extract *at most 3* memory items from the trajectory.
  - You must not repeat similar or overlapping items.
  - Prefer concrete, actionable procedures over abstract principles. Do not embed specific product names, queries, or literal string contents from the task.

## Output Format
Your output must strictly follow the Markdown format shown below:

```
# Memory Item i
## Title <the title of the memory item>
## Description <one sentence summary describing when or when NOT to use the memory item>
## Content <1-3 sentences describing the insights learned to successfully accomplishing similar tasks in the future>
```
"""

FAILED_SI = """
You are an expert in web navigation. You will be given a user query, the corresponding trajectory that represents **how an agent attempted to resolve the task but failed**. 

## Guidelines
You need to extract and summarize useful insights in the format of memory items based on the agent's failed trajectory.
The goal of summarized memory items is to be helpful and generalizable for future similar tasks.

## Important notes
  - You must first reflect and think why the trajectory failed, and then summarize what lessons you have learned or strategies to prevent the failure in the future.
  - You can extract *at most 3* memory items from the trajectory.
  - You must not repeat similar or overlapping items.
  - Prefer concrete, actionable recovery procedures over abstract principles. Do not embed specific product names, queries, or literal string contents from the task.

## Output Format
Your output must strictly follow the Markdown format shown below:

```
# Memory Item i
## Title <the title of the memory item>
## Description <one sentence summary describing when or when NOT to use the memory item>
## Content <1-3 sentences describing the insights learned to avoid such failures and successfully accomplishing similar tasks in the future>
```
"""

PARALLEL_SI = """
You are an expert in web navigation. You will be given a user query and multiple trajectories showing how an agent attempted the task. 
Some trajectories may be successful, and others may have failed.

## Guidelines
Your goal is to **compare and contrast** these trajectories to identify the most useful and generalizable strategies as memory items.
Use **self-contrast reasoning**:
  - Identify patterns and strategies that consistently led to success.
  - Identify mistakes or inefficiencies from failed trajectories and formulate preventative strategies.
  - Prefer strategies that generalize beyond specific pages or exact wording.

## Important notes
  - Think first: Why did some trajectories succeed while others failed?
  - You can extract *at most 5* memory items from all trajectories combined.
  - Do not repeat similar or overlapping items.
  - Do not mention specific websites, queries, or string contents — focus on generalizable behaviors and reasoning patterns.
  - Make sure each memory item captures **actionable** and **transferable** insights.

## Output Format
Your output must strictly follow the Markdown format shown below:

```
# Memory Item i
## Title <the title of the memory item>
## Description <one sentence summary describing when or when NOT to use the memory item>
## Content <1-5 sentences describing the insights learned to avoid such failures and successfully accomplishing similar tasks in the future>
```
"""

PARALLEL_AWM_SI = """
You are an expert in web navigation. You will be given a user query and multiple trajectories showing how an agent attempted the task. 
Some trajectories may be successful, and others may have failed.

## Guidelines
Your goal is to extract the common workflows to solve these tasks.
**Workflow extraction process**:
  - Examine all given trajectories (both successful and failed).
  - Look for repetitive subsets of actions that occur across multiple tasks.
  - Focus on action sequences that are critical to completing parts of the task, not trivial or one-off actions.

## Important notes
  - Think first: Why did some trajectories succeed while others failed?
  - You can extract *at most 5* workflow items from all trajectories combined.
  - Do not repeat similar or overlapping items.
  - **Each workflow must have at least 2 steps (i.e., 2 <think><action> sequences)**.
  - Do not mention specific websites, queries, or string contents — focus on generalizable behaviors and reasoning patterns.
  - Ensure workflows are actionable and can be reused in similar tasks.

## Output Format
Your output must strictly follow the following example format:

```
Workflow i: Find all orders
<think>
To find the date of the first purchase, I need to navigate to the order history section of the user's account. I will start by clicking on the "My Account" link.
</think>
<action>
click('227')
</action>

<think>
To find the date of the first purchase, I need to navigate to the "My Orders" section where the order history is listed. From there, I can look for the earliest order date. I will start by clicking on the "My Orders" link in the left sidebar.
</think>
<action>
click('1843')
</action>
```
"""

SEQUENTIAL_PROMPT = """
Important: Let's carefully re-examine the previous trajectory, including your reasoning steps and actions taken.
Pay special attention to whether you used the correct elements on the page, and whether your response addresses the user query.
If you find inconsistencies, correct them. If everything seems correct, confirm your final answer.
Output must stay in the same “<think>...</think><action></action>” format as previous trajectories.
"""

SEQUENTIAL_FOLLOWING_PROMPT = """
Let's check again. 
Output must stay in the same “<think>...</think><action></action>” format as previous trajectories.
"""

AWM_INSTRUCTION = """
Given a list of web navigation tasks, your task is to extract the common workflows to solve these tasks.
Each given task contains a natural language instruction, and a series of actions to solve the task. You need to find the repetitive subset of actions across multiple tasks, and extract each of them out as a workflow.
Each workflow should be a commonly-reused sub-routine of the tasks. Do not generate similar or overlapping workflows. Each workflow should have at least two steps. Represent the non-fixed elements (input text, button strings) with descriptive variable names as shown in the example.
Keep the values of invariant elements, e.g., id of "Search" or "Customers", as they will share and stay invariant across tasks.
Try to generate as many workflows that can cover all the tasks in the input list.
"""

AWM_EXAMPLE = """
## Concrete Examples

Query: What is the date when I made my first purchase on this site?
Actions:
<think>
To find the date of the first purchase, I need to navigate to the order history section of the user's account. I will start by clicking on the "My Account" link.
</think>
<action>
click('227')
</action>

<think>
To find the date of the first purchase, I need to navigate to the "My Orders" section where the order history is listed. From there, I can look for the earliest order date. I will start by clicking on the "My Orders" link in the left sidebar.
</think>
<action>
click('1843')
</action>

<think>
To find the date of the first purchase, I need to look at the earliest date in the "Date" column of the "Orders" table. The current page shows the first 10 orders, but there are multiple pages. I will navigate to the last page to find the earliest order date.
</think>
<action>
click('1788')
</action>

<think>
To find the date of the first purchase, I need to look for the earliest date in the "Date" column of the "My Orders" table. From the current view, the earliest date visible is "5/2/23". However, there might be more orders on other pages. I will navigate to the last page to ensure I find the earliest date.
</think>
<action>
click('1784')
</action>

<think>
To find the earliest purchase date, I need to look at the "Date" column in the "Orders" table and identify the earliest date listed. The dates currently visible are: 4/27/22, 4/5/22, 3/10/22, 3/2/22, 3/2/22. The earliest date visible is 3/2/22. I will respond with this date.
</think>
<action>
send_msg_to_user('The earliest purchase date is 3/2/22.')
</action>

Query: I want to browse the products in the Cabinets, Racks & Shelves category
Actions:
<think>
To browse the products in the Cabinets, Racks & Shelves category, I need to navigate to the "Home & Kitchen" section, which likely contains the Cabinets, Racks & Shelves category. I will start by hovering over the "Home & Kitchen" menu item to reveal the subcategories.
</think>
<action>
hover('735')
</action>

<think>
To browse the products in the Cabinets, Racks & Shelves category, I need to navigate to the "Storage & Organization" section under the "Home & Kitchen" menu. I will start by hovering over the "Storage & Organization" menu item to reveal the subcategories.
</think>
<action>
hover('786')
</action>

<think>
To browse the products in the Cabinets, Racks & Shelves category, I need to click on the "Racks, Shelves & Drawers" link under the "Storage & Organization" menu. This will take me to the desired category.
</think>
<action>
click('797')
</action>

<think>
The current page is displaying the "Racks, Shelves & Drawers" category under "Storage & Organization" in the "Home & Kitchen" section. The user wants to browse products in the "Cabinets, Racks & Shelves" category. Since "Racks, Shelves & Drawers" is already a subcategory of "Storage & Organization," I will confirm with the user if this is the correct category they want to browse.
</think>
<action>
send_msg_to_user('You are currently viewing the "Racks, Shelves & Drawers" category under "Storage & Organization." Is this the correct category you want to browse, or are you looking for a different category?')
</action>


Query: Get the order number of my most recent cancelled order 
Actions:
<think>
To get the order number of the most recent cancelled order, I need to navigate to the "My Account" section where order history is typically managed. From the current page, I can see the "My Account" link in the top right corner. I will click on the "My Account" link to proceed.
</think>
<action>
click('227')
</action>

<think>
To get the order number of the most recent cancelled order, I need to navigate to the "My Orders" section. From there, I can filter or sort the orders to find the most recent cancelled order. I will start by clicking on the "My Orders" link in the left sidebar.
</think>
<action>
click('1843')
</action>

<think>
To get the order number of the most recent cancelled order, I need to look for the order with the status "Canceled" and note its order number. From the current page, I can see that the most recent cancelled order is order number 000000170.
</think>
<action>
send_msg_to_user('The order number of your most recent cancelled order is 000000170.')
</action>


## Summary Workflows

Workflow 1: Find all orders
<think>
To find the date of the first purchase, I need to navigate to the order history section of the user's account. I will start by clicking on the "My Account" link.
</think>
<action>
click('my_account_id')
</action>

<think>
To find the date of the first purchase, I need to navigate to the "My Orders" section where the order history is listed. From there, I can look for the earliest order date. I will start by clicking on the "My Orders" link in the left sidebar.
</think>
<action>
click('my_orders_id')
</action>

Workflow 2: Obtain order information, such as date or order number
<think>
To find the earliest purchase date, I need to look at the "Date" column in the "Orders" table and identify the earliest date listed. The dates currently visible are: 4/27/22, 4/5/22, 3/10/22, 3/2/22, 3/2/22. The earliest date visible is 3/2/22. I will respond with this date.
</think>
<action>
send_msg_to_user('The earliest purchase date is 3/2/2022.')
</action>

Workflow 3: Browse products in a specific (sub-)category
<think>
To browse the products in the Cabinets, Racks & Shelves category, I need to navigate to the "Home & Kitchen" section, which likely contains the Cabinets, Racks & Shelves category. I will start by hovering over the "Home & Kitchen" menu item to reveal the subcategories.
</think>
<action>
hover('home_kitchen_id')
</action>

<think>
To browse the products in the Cabinets, Racks & Shelves category, I need to navigate to the "Storage & Organization" section under the "Home & Kitchen" menu. I will start by hovering over the "Storage & Organization" menu item to reveal the subcategories.
</think>
<action>
hover('storage_organization_id')
</action>

<think>
To browse the products in the Cabinets, Racks & Shelves category, I need to click on the "Racks, Shelves & Drawers" link under the "Storage & Organization" menu. This will take me to the desired category.
</think>
<action>
click('racks_shelves_drawers_id')
</action>
"""

===== BOUND ARTIFACT: reasoningbank_induce_scaling | /data/wyt/e2-r17-search-projection/baselines/published/reasoning-bank/WebArena/induce_scaling.py =====
# Copyright 2026 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import json
import random
import argparse
import re
import gzip
import pickle

from google import genai
from functools import partial
import time
from memory_management import select_memory

from prompts.memory_instruction import PARALLEL_SI, PARALLEL_AWM_SI

# %% load examples
def load_blocks(path: str) -> list[list[str]]:
    """Load blank-line separated blocks from the log file."""
    blocks, block = [], []
    for line in open(path, 'r'):
        if line.strip() == "":
            blocks.append(block)
            block = []
        else:
            if line.strip():
                block.append(line.strip())
    assert len(blocks) % 2 == 0
    return blocks

def remove_invalid_steps(actions: list[str]) -> list[str]:
    """Remove invalid steps from the action sequence."""
    valid_actions = []
    for a in actions:
        if "click(" in a:
            arg = a[a.index("(")+1: a.index(")")]
            try:
                if type(eval(arg)) == str and type(eval(arg[1:-1])) == int:
                    valid_actions.append(a)
            except:
                continue
        elif "fill(" in a:
            arg = a[a.index("(")+1: a.index(",")].strip()
            if type(eval(arg)) == str:
                valid_actions.append(a)
        elif "scroll(" in a or "noop(" in a:
            continue
        else:
            valid_actions.append(a)
    return valid_actions

def load_step_pkl(path):
    with gzip.open(path, 'rb') as f:
        data = pickle.load(f)
    msgs = data.agent_info.get("chat_messages", [])[:3]
    return [str(m) for m in msgs]


def load_trajectory(folder):
    step_files = sorted(
        [f for f in os.listdir(folder) if re.match(r"step_\d+\.pkl\.gz", f)],
        key=lambda f: int(re.findall(r"\d+", f)[0])
    )
    traj = []
    for f in step_files:
        try:
            msgs = load_step_pkl(os.path.join(folder, f))
            traj.append(msgs[2])
        except Exception as e:
            continue
    return traj

def extract_think_and_action(path: str) -> tuple[list[str], list[list[str]]]:
    """Extract the task trajectory from the log file."""
    log_text = open(path, 'r').read()
    lines = log_text.splitlines()
    think_list = []
    action_list = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("action:"):
            # Parse the full action block (can span multiple lines)
            action_lines = []
            if line.strip() != "action:":
                action_lines.append(line[len("action:"):].strip())
            i += 1
            while i < len(lines) and lines[i].strip() != "":
                action_lines.append(lines[i].strip())
                i += 1
            action_text = "".join(action_lines).strip()

            # Now look backward for the most recent loop-INFO thinking block
            thinking_lines = []
            for j in range(i - 1, -1, -1):
                if "browsergym.experiments.loop - INFO -" in lines[j]:
                    thinking = lines[j].split("browsergym.experiments.loop - INFO -", 1)[-1].strip()
                    thinking_lines.insert(0, thinking)
                    break
            thinking_text = "\n".join(thinking_lines).strip()
            think_list.append(thinking_text)
            action_list.append(action_text)
        else:
            i += 1

    assert len(think_list) == len(action_list)
    return think_list, action_list

def format_trajectory(think_list: list[str], action_list: list[list[str]]) -> str:
    trajectory = []
    for t, a in zip(think_list, action_list):
        # acts = '\n'.join(a)
        acts = a
        trajectory.append(f"<think>\n{t}\n</think>\n<action>\n{acts}\n</action>")
    return '\n\n'.join(trajectory)


def format_examples(examples: list[dict], flag=False) -> str:
    """Format examples to the prompt."""
    formatted_examples = []
    for ex in examples:
        trajectory = format_trajectory(ex["think_list"], ex["action_list"])
        formatted_examples.append(f"Query: {ex['query']}\nTrajectory:\n{trajectory}")
    # return '\n\n'.join(["## Concrete Examples"] + formatted_examples + ["## Summary Workflow"])
    if flag:
        return '\n\n'.join(["## Query and Trajectory Generated Using Previous Memory"] + formatted_examples + ["## Correctness Signal"]+ ["The result is CORRECT."] + ["## Updated Memory"])
    else:
        return '\n\n'.join(["## Query and Trajectory Generated Using Previous Memory"] + formatted_examples + ["## Correctness Signal"]+ ["The result is INCORRECT."] + ["## Updated Memory"])


def get_info(f: str, status: str = None) -> dict:
        
    # get query -> task objective
    task_id = f.split('/')[-1].split("_")[0].split(".")[1]
    config_path = os.path.join("config_files", f"{task_id}.json")
    config = json.load(open(config_path))
    query = config["intent"]

    template_id = config["intent_template_id"]  # for deduplication
    traj = load_trajectory(f)

    # add to template dict
    if status == 'success':
        wdict = {"query": query, "template_id": template_id, "steps": traj, "status": "success"}
    elif status == 'fail':
        wdict = {"query": query, "template_id": template_id, "steps": traj, "status": "fail"}

    return wdict

def main():

    trajectories = ""

    for i in range(int(args.num_samples)):

        res_dir = args.result_dir
        cur_task = os.path.join(res_dir, args.task)

        # load feedback from auto-evaluation
        if args.criteria == "gt":
            reward = json.load(open(os.path.join(cur_task, "summary_info.json")))["cum_reward"]
        elif args.criteria == "autoeval":
            reward = json.load(open(os.path.join(cur_task, f"{args.model}_autoeval.json")))[0]["rm"]
        else:
            raise ValueError(f"Invalid criteria: {args.criteria}.")

        if reward == 0:
            status = "success"
        else:
            status = "fail"

        ex = get_info(cur_task, status)

        if i == 0:
            trajectories += f"**Query:** {ex['query']}\n\n"
        trajectories += f"**Trajectory {i+1} :**\n"
        trajectories += "\n\n".join(ex["steps"]) + "\n\n"

    from utils.clients import CLIENT_DICT
    client = CLIENT_DICT[args.model]
    
    generated_memory_item = client.one_step_chat(trajectories, system_msg=PARALLEL_SI, temperature=0.7)

    # write to jsonl file 
    with open(args.output_path, 'a') as f:
        f.write(json.dumps({
            "task_id": args.task.split(".")[-1],
            "query": ex["query"],
            "memory_items": generated_memory_item,
            "template_id": ex["template_id"]
        }) + '\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--result_dir", type=str, default="results_base_new",
                        help="Path to the result directory. Support multiple directories separated by space.")
    parser.add_argument("--output_path", type=str, default=None, required=True,
                        help="Path to the output file.")
    parser.add_argument("--criteria", type=str, default="gt", 
                        choices=["gt", "autoeval"],
                        help="'gt': only use examples with gold reward, 'autoeval': use examples with autoeval reward.")
    parser.add_argument("--model", type=str, default="gemini-2.5-flash",
                        choices=["gpt-3.5", "gpt-4", "gpt-4o", "gemini-2.5-flash"])
    parser.add_argument("--task", type=str, default="webarena.21")
    parser.add_argument("--num_samples", type=int, default=1, help="samples per task")
    args = parser.parse_args()

    main()

BOUND DOSSIER END
