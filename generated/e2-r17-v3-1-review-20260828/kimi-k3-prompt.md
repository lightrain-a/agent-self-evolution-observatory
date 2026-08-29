You are an independent adversarial pre-execution reviewer for E2-R17 / Search-Projection Censoring. You are blind to the other reviewer. This consultation has zero scientific-experiment, GPU, provider-runtime, paper-promotion, frontend, or submission authority.

Requested reviewer endpoint: kimi-k3
Exact V3.1 repair SHA-256: 2b4589d704037c9dd781c4091d03b12dddf727b6d7a7aad765dc7536863a6880

Context: V3's zero-provider mechanical Pilot correctly failed before scientific-effect evaluation because nominal source-token parity became unequal after final BPE re-tokenization, and because legacy updater-visible packet labels could reveal arm identity. V3.1 is a new design; the failed V3 contract/root cannot be retried.

Published novelty threat: ReasoningBank/MaTTS (ICLR 2026) already learns from successful and failed experiences produced with test-time scaling. Do NOT grant novelty merely because R17 uses failures. R17 survives only if the exact-same-realized-pool acting-selection -> learner-visible-evidence -> future-skill causal object is genuinely distinct and identified.

Audit the actual bound code and the pinned first-party MindMemOS source, not only the authors' prose. In particular:

1. STREAM-LEVEL THEORY: E1 updates eight task packets jointly into one potentially nonlinear skill state. Is V3.1 correct to retract the task-level `Delta=M*delta` expression as an exact learning theorem and instead define `R_s=sum_j M_sj` only as treatment dose/support and `D_s=J_s(MRW)-J_s(WIN)` as the paired stream endpoint? Is `R_s=0 => identical learner inputs` the right exact implication, with no linearity/monotonicity assumed for `R_s>0`?

2. SAME-POOL IDENTIFICATION: under the frozen design, are task, initial skill, exact generated K=8 pools, acting winner, executor, updater implementation, and held-out probes fixed while learner-visible selected evidence changes? Is this enough to identify a learning-projection effect at stream level once hosted-updater stochasticity is screened by WIN-A/WIN-B?

3. SCORE SEMANTICS: inspect first-party MindMemOS `evolution.py` and `skill_patch.py`. The legacy wrapper used the served winner's acting score even for a failed MRW transcript. V3.1 instead places the selected evidence trajectory's verifier score into `payload['score']` while retaining served acting score only in provenance. Is this the scientifically correct treatment semantics, or does it create an impermissible second treatment beyond the evidence projection? Explain precisely. Consider that first-party scored patch prompts explicitly use the score as the primary outcome signal.

4. ARM BLINDING: verify from first-party source whether only `payload.messages` enters the trajectory transcript and whether R17 `r17_*` provenance fields remain outside model-visible prompts. Does the new `BlindedEvidenceUnit` path remove arm/projection/rollout/provenance labels from the actual transcript? Flag any remaining treatment cue.

5. TOKEN PARITY: does `ExactMatchedEvidenceBlockRenderer` correctly solve the V3 BPE splice bug by matching the actual final re-tokenized evidence blocks rather than nominal source slices? Is no-padding deterministic search acceptable?

6. SOURCE-BUDGET ASYMMETRY: historical replay sometimes needs a one-token difference in selected pre-decoding source budget to obtain exact equal final provider-visible token counts. Is the final provider-visible evidence token count the correct fairness budget, or does unequal source slicing create a P0 content-quantity confound requiring a stricter construction? If a repair is needed, specify it before Pilot.

7. DOWNSTREAM TRUNCATION: is freezing `transcript_max_chars>=100000` plus a per-unit assertion sufficient to prevent first-party `_render_transcript` from silently destroying token parity? Is there another truncation or transformation later in the summary/patch path that invalidates the causal comparison?

8. NEGATIVE CONTROL / SCORE: WIN-A and WIN-B are byte-identical treatments before independent hosted-model calls. Does changing selected-evidence scores in MRW interact with the negative-control logic in any problematic way? Negative-control equivalence must be evaluated before MRW.

9. NOVELTY: given the published ReasoningBank collision, is it defensible to position R17 as causal identification of acting-oriented selection changing the experience distribution available to persistent learning, rather than generic failure learning? State if this still looks cosmetic.

10. MECHANICAL PILOT: inspect the draft contract and runner. The fresh Pilot must use only the 12 frozen historical E0 pools, zero provider calls, zero new actor rollouts, no held-out future-skill evaluation, immediate content-addressed checkpointing, SHA-validated missing-unit resume, and a fresh root. Does the code respect this scope? This review may at most allow that fresh zero-provider Pilot.

11. AUTHORITY: even PASS must keep provider runtime Pilot, E1-A, E1-B, scientific outcomes, and paper promotion on HOLD. A later immutable contract is required for each.

Return exactly one JSON object and no markdown using this schema:
{
  "repair_sha256_acknowledged": "",
  "verdict": "PASS_TO_FRESH_ZERO_PROVIDER_MECHANICAL_PILOT|REVISE_V31_BEFORE_PILOT|STOP_PROGRAM",
  "stream_level_theory_assessment": "",
  "same_pool_estimand_assessment": "",
  "selected_evidence_score_semantics_assessment": "",
  "arm_blinding_and_upstream_dataflow_assessment": "",
  "exact_retokenized_parity_assessment": "",
  "source_budget_asymmetry_assessment": "",
  "downstream_truncation_assessment": "",
  "reasoningbank_novelty_boundary_assessment": "",
  "mechanical_pilot_scope_assessment": "",
  "checkpoint_resume_assessment": "",
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
  "mechanical_pilot_recommendation": "ALLOW_FRESH_ZERO_PROVIDER_MECHANICAL_PILOT|HOLD|STOP",
  "provider_runtime_pilot_recommendation": "HOLD|STOP",
  "e1_a_recommendation": "HOLD|STOP",
  "e1_b_recommendation": "HOLD|STOP",
  "paper_claim_authority": false,
  "single_sentence_verdict": ""
}

Set `repair_sha256_acknowledged` exactly to the SHA above. Keep `paper_claim_authority` false. A PASS authorizes only creation/execution of a separately SHA-bound fresh zero-provider mechanical Pilot contract. It does not authorize E1-A or E1-B.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START

===== BOUND ARTIFACT: v3_1_repair_json | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-v3-1-causal-purity-repair-20260828.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-v3-1-causal-purity-repair",
  "date": "2026-08-28",
  "status": "READY_FOR_INDEPENDENT_REVIEW_ONLY",
  "scientific_authority": false,
  "parents": {
    "v3_plan": {
      "path": "generated/e2-r17-experiment-plan-v3-20260828.json",
      "sha256": "b1a0224117f161ead9fccefa2c22a0f01dfa1d9e72ca1e98107418f21e3e04c5"
    },
    "v3_failure_adjudication": {
      "path": "generated/e2-r17-v3-runtime-pilot-failure-adjudication-20260828.json",
      "sha256": "fec66715370144f4b8c72c7afd32520f9f990ef466f988c0d77cf3a954aefcef",
      "same_contract_retry_allowed": false
    }
  },
  "design_note": {
    "path": "consultations/e2-r17-v3-1-causal-purity-repair-20260828.md",
    "sha256": "94490232790ec78cdcb5773b49bb9fcb509ca18b8cc5cc2842216d0becb25521"
  },
  "repairs": {
    "actual_retokenized_parity": {
      "renderer": "research_pipeline/e2_r17_evidence_window_v2.py",
      "renderer_sha256": "6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7",
      "tokenizer": "tiktoken==0.11.0/cl100k_base",
      "final_block_cap_tokens": 3072,
      "padding": false,
      "selection_rule": "largest common reachable final re-tokenized evidence-block length",
      "historical_zero_provider_replay": {
        "pools": 12,
        "mixed": 8,
        "nonmixed": 4,
        "exact_final_token_parity": "12/12",
        "nonmixed_byte_identity": "4/4",
        "matched_final_tokens_min": 995,
        "matched_final_tokens_max": 3072,
        "matched_final_tokens_mean": 2072.5,
        "max_selected_source_budget_gap": 1,
        "provider_calls": 0,
        "new_rollouts": 0,
        "scientific_effectiveness_evaluated": false
      }
    },
    "arm_blinding_and_score_semantics": {
      "updater": "research_pipeline/e2_r17_mindmemos_updater.py",
      "updater_sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d",
      "upstream_audit": "generated/e2-r17-v3-1-upstream-prompt-dataflow-audit-20260828.json",
      "upstream_audit_sha256": "ecd160e6c87b259c56e5a667fe94a9cc7310c37c5fca92ce514436c131d30d7c",
      "messages": "selected arm-blinded evidence only",
      "score": "selected evidence trajectory verifier score",
      "acting_score": "provenance only and fixed by exact served winner",
      "projection_metadata_in_model_visible_messages": false,
      "required_transcript_max_chars": 100000
    },
    "stream_level_theory": {
      "old_exact_learning_factorization_promotable": false,
      "reason": "actual updater aggregates eight tasks nonlinearly into one stream-level skill state",
      "mixed_witness_dose": "R_s=sum_j M_sj over eight frozen update tasks",
      "primary_effect": "D_s=J_s(MRW)-J_s(WIN)",
      "exact_zero_dose_implication": "R_s=0 implies identical WIN/MRW evidence inputs before residual updater/provider stochasticity",
      "linearity_assumed": false,
      "monotonicity_assumed": false,
      "family_additivity_assumed": false,
      "dose_response_role": "prospective mechanism/heterogeneity analysis only after primary E1"
    }
  },
  "e1_primary_inference": {
    "independent_units": 12,
    "tasks_per_update_stream": 8,
    "common_heldout_probes_per_state": 18,
    "negative_control_first": "WIN-B vs WIN-A equivalence",
    "primary_contrast": "MRW vs WIN-A paired stream effect",
    "later_diagnostics_cannot_rescue_primary_failure": true
  },
  "published_baseline_boundary": {
    "headline": [
      "ReasoningBank/MaTTS — ICLR 2026",
      "PolySkill — ICLR 2026",
      "ACE — ICLR 2026",
      "Agent Workflow Memory — ICML 2025"
    ],
    "extended": ["SAGE — ACL 2026 Long"],
    "arxiv_only_not_headline": ["SkillCAT", "Branch2Skill", "SkillOpt", "RethinkSkill", "TSR"],
    "generic_failure_learning_novelty_claim_forbidden": true
  },
  "tests_observed": {
    "evidence_window_v2_pinned_tokenizer": "5/5 PASS",
    "updater_v31": "4/4 PASS",
    "search_projection_runner_plus_theory": "20/20 PASS",
    "python_compile": "PASS"
  },
  "next_gate": "INDEPENDENT_KIMI_AND_DEEPSEEK_V3_1_REVIEW",
  "authority": {
    "independent_review": true,
    "fresh_zero_provider_mechanical_pilot": false,
    "provider_runtime_pilot": false,
    "e1_a": false,
    "e1_b": false,
    "paper_promotion": false,
    "submission": false
  }
}


===== BOUND ARTIFACT: v3_1_repair_md | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/consultations/e2-r17-v3-1-causal-purity-repair-20260828.md =====
# E2-R17 V3.1 — Causal-Purity and Theory Repair

Date: 2026-08-28
Status: **DESIGN_ONLY / ZERO SCIENTIFIC AUTHORITY**
Parent: Experiment Plan V3 (`b1a0224117f161ead9fccefa2c22a0f01dfa1d9e72ca1e98107418f21e3e04c5`)
Preserved V3 Pilot failure: `fec66715370144f4b8c72c7afd32520f9f990ef466f988c0d77cf3a954aefcef`

V3.1 does not retry the failed V3 contract and does not authorize E1-A pool generation, E1-B updater calls, paper promotion, or scientific claims. It repairs three P0 issues found before scientific effectiveness was evaluated.

## 1. Preserved V3 mechanical failure

The V3 mechanical Pilot stopped after three completed units with zero provider calls and zero new actor rollouts. On `r17-b1-fmv-p8`, nominal source-token parity was 2026/2026, but the final decoded and concatenated evidence blocks re-tokenized to 2025/2026 because BPE can create a new merge at the head/tail splice boundary.

This is retained as a protocol failure, not overwritten as a pass. The same V3 contract is not retryable.

## 2. Repair A — match actual updater-visible token count

V3.1 uses `research_pipeline/e2_r17_evidence_window_v2.py` SHA:

`6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7`

Frozen tokenizer:

- package: `tiktoken==0.11.0`;
- encoding: `cl100k_base`;
- final updater-visible evidence-block cap: 3072 tokens;
- no padding;
- deterministic 1/3 head + 2/3 tail evidence retention;
- search over source-token budgets and accept only a pair whose **final rendered UTF-8 evidence blocks re-encode to exactly the same token count**;
- choose the largest common reachable final block length under the cap.

A one-token difference in selected source budget may be required to achieve exact final provider-visible parity because the decoded boundary can change BPE segmentation. The scientific budget is the final updater-visible evidence block, not the pre-decoding slice count. The receipt records both source budgets and final token counts.

Historical zero-provider replay over all 12 E0 K=8 pools already established mechanical feasibility:

- 12/12 exact final WIN/MRW token parity;
- 8 mixed, 4 nonmixed;
- nonmixed WIN/MRW evidence byte-identical;
- final matched-token range 995–3072, mean 2072.5;
- maximum left/right selected-source-budget difference: 1 token;
- zero provider calls and zero new rollouts.

This historical replay is engineering evidence only and has no scientific-effect authority.

## 3. Repair B — blind arm identity and separate acting outcome from learning evidence

The legacy packet renderer placed strings such as `PROJECTION`, `ROLE`, and source rollout metadata inside the updater transcript. V3.1 forbids this.

The canonical selected evidence contains only branch-specific user/assistant/tool messages plus the selected trajectory's verifier score/message. System prompt, projection identity, arm name, rollout index, filesystem path, provider IDs, receipts, pool ID, and provenance hashes remain outside model-visible evidence.

V3.1 additionally fixes a more important semantic bug in the old MindMemOS wrapper. The old wrapper stored:

`payload['score'] = pool.acting_success`

for every arm. On a mixed pool this could show the updater a failed MRW transcript while labeling that observation with the served winner's success score. At the pinned MindMemOS implementation, the patch proposer explicitly uses trajectory scores as the primary signal, so this is not a harmless receipt mismatch.

V3.1 therefore separates:

- **acting provenance**: served winner SHA and acting score, identical across cloned arms and retained only in provenance;
- **learning evidence outcome**: verifier score of the selected learner-visible trajectory, stored as the MindMemOS add-record `score`.

Thus on a mixed pool WIN may expose a score-1 winner while MRW exposes a score-0 failed witness. That score difference is part of the learning projection treatment, not a change in the user-facing acting outcome.

Implementation path:

- `research_pipeline/e2_r17_mindmemos_updater.py` SHA `9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d`;
- V3.1 test SHA `874fc99106e2f85f67180f4962f50b50ad2d921c8ba5ad8fad54fb12f62ded9f`.

The new `BlindedEvidenceUnit` and `build_blinded_add_record_payload` path ensures that the MindMemOS `messages` field contains only the arm-blinded evidence block while `score` follows the selected evidence trajectory. Projection and provenance metadata remain in `r17_*` fields for audit only.

## 4. First-party MindMemOS source audit

Pinned first-party checkout:

- repository: `https://github.com/mindscale-noah/MindMemOS.git`;
- commit: `90491828726e1540442b17cd445d0308d0b8093c`;
- checkout observed clean during V3.1 audit.

Bound files:

- `pipelines/skill/evolution.py`: `37bb22da6d4e8485d824c3c31e48f200561b05834a8a6bf3c057b29613b2bca0`;
- `prompts/EN/skills/trajectory_summary.py`: `771a5dc2efc369ed8b4c6d90b5ee470339263780eaf26265be24561b7156b95e`;
- `prompts/EN/skills/skill_patch.py`: `48ab68ee3fbb6f115269679358cbcc1f08f9a28318a95438860eae1bbf5a3f4c`.

The source audit establishes the model-visible data path:

1. `_injected_candidates` obtains the transcript from `payload['messages']`, the outcome score from `payload['score']`, and stores `task_id` separately.
2. `_render_transcript` renders only the stored message role/content into the transcript.
3. `_summarize_one` sends the common summary system prompt and `skill_name + transcript` to the LLM.
4. `_propose_patch` receives the generated summaries and their stored scores. With `use_trajectory_score=True`, the scored system prompt treats high/low scores as the primary outcome signal.
5. The R17 `r17_*` provenance fields are not read into either prompt at this pinned commit.

Therefore arm identity may be retained in provenance only if the pinned source SHA is revalidated before any provider tranche.

## 5. Downstream truncation invariant

Exact token parity is meaningless if the first-party updater subsequently truncates the transcript differently. V3.1 therefore requires a pre-provider assertion that every rendered `[user] <evidence>` transcript fits under the frozen MindMemOS transcript limit with no truncation.

For V3.1 runtime qualification, set/freeze `transcript_max_chars >= 100000` and assert every complete rendered evidence block is strictly below the bound before inserting the add record. The common limit is not selected from scientific outcomes.

Historical E0 V3.1 evidence blocks ranged from 3134 to 9340 characters, so the proposed bound is mechanically nonbinding on known artifacts.

## 6. Repair C — correct the learning theory to the actual stream-level scientific unit

V3 wrote the task-level gated expression

`Delta_K = M_K * delta_K`.

That factorization is exact only when the effect difference is defined on the same unit on which the mixed event gates the treatment, or under additional aggregation assumptions. E1 does not update one task at a time: MindMemOS aggregates eight projected task packets into one nonlinear persistent-skill update. Consequently task-level mixed mass cannot be multiplied by one scalar `delta_K` and presented as an exact learning law for the real E1 updater.

For stream `s`, define:

`M_sj = 1` if task `j`'s K=8 pool is mixed, else `0`;

`R_s = sum_{j=1}^8 M_sj`, the pre-treatment mixed-witness dose in that stream;

`D_s = J_s(MRW) - J_s(WIN)`, the paired future frozen-skill effect after the eight-task update.

The only exact support implication required for E1 is:

`R_s = 0 => MRW updater input is identical to WIN updater input => D_s should differ only by residual updater/provider stochasticity.`

For `R_s > 0`, no linearity, additivity, or monotonicity of `D_s` in `R_s` is assumed. Interactions among multiple witnessed failures are allowed.

The primary E1 estimand remains the paired stream-level average of `D_s` over the 12 frozen streams, conditional on passing the pre-treatment support gate and the WIN-A/WIN-B stochasticity equivalence gate.

Dose-response, failure-family decomposition, or approximations such as `sum_z C_z delta_z` are prospective mechanism models for later validation, not identities used to authorize E1.

## 7. E1 inference remains unchanged where valid

Scientific unit: 12 cloned stream-level persistent states.

Repeated observations: the same 18 held-out probes per learned state; probes are not treated as 216 independent causal units.

Order of interpretation:

1. WIN-A vs WIN-B identical-treatment equivalence gate;
2. MRW vs WIN-A primary paired effect;
3. only after the primary result, RB-AGG and diagnostic controls interpret whether any effect is failure-specific, aggregation-sensitive, or generic branch diversity.

A null/harmful MRW result cannot be rescued by later benchmark expansion.

## 8. Published-baseline boundary remains frozen

Headline published baselines remain:

1. ReasoningBank/MaTTS — ICLR 2026;
2. PolySkill — ICLR 2026;
3. ACE — ICLR 2026;
4. Agent Workflow Memory — ICML 2025;
5. SAGE — ACL 2026 Long as extended baseline.

ArXiv-only SkillCAT, Branch2Skill, SkillOpt, RethinkSkill, and TSR remain collision/Related Work, not headline published baselines.

R17 still cannot claim novelty from learning from failures. The candidate contribution is the causal effect of acting-oriented search selection on learner-visible evidence and future persistent skill under an exact same realized search pool.

## 9. V3.1 gate

The next allowed operation is an **independent Kimi K3 + DeepSeek V4-Pro review of this V3.1 repair and bound code**. That review may at most authorize a fresh zero-provider, zero-new-rollout mechanical Pilot rooted separately from V3.

Even a passing V3.1 mechanical Pilot does not itself authorize E1-A or E1-B. A separate immutable E1-A contract must follow.


===== BOUND ARTIFACT: v3_1_upstream_audit | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-v3-1-upstream-prompt-dataflow-audit-20260828.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-v3-1-upstream-prompt-dataflow-audit",
  "date": "2026-08-28",
  "status": "PASS_SOURCE_BOUND_CAUSAL_PURITY_PATH",
  "scientific_authority": false,
  "provider_calls": 0,
  "new_actor_rollouts": 0,
  "mindmemos": {
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817",
    "remote": "https://github.com/mindscale-noah/MindMemOS.git",
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "checkout_clean_observed": true,
    "bound_files": {
      "src/mindmemos/mindmemos/pipelines/skill/evolution.py": "37bb22da6d4e8485d824c3c31e48f200561b05834a8a6bf3c057b29613b2bca0",
      "src/mindmemos/mindmemos/prompts/EN/skills/trajectory_summary.py": "771a5dc2efc369ed8b4c6d90b5ee470339263780eaf26265be24561b7156b95e",
      "src/mindmemos/mindmemos/prompts/EN/skills/skill_patch.py": "48ab68ee3fbb6f115269679358cbcc1f08f9a28318a95438860eae1bbf5a3f4c"
    }
  },
  "source_findings": {
    "candidate_transcript_source": "record.payload.messages only",
    "candidate_score_source": "record.payload.score",
    "candidate_task_id_source": "record.payload.task_id but not interpolated into trajectory-summary prompt",
    "transcript_renderer": "renders message role/content only",
    "summary_prompt": "common SUMMARY_SYSTEM plus skill_name and rendered transcript",
    "patch_prompt": "generated summaries plus stored scores; scored prompt treats scores as primary outcome signal",
    "r17_provenance_fields_model_visible": false
  },
  "v3_legacy_bug": {
    "present": true,
    "description": "Legacy R17 updater assigned pool.acting_success to payload.score even when MRW selected a failed trajectory, while MindMemOS scored patch semantics interpret this score as the selected session outcome.",
    "scientific_effectiveness_evaluated_under_bug": false
  },
  "v3_1_repair": {
    "updater_file_sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d",
    "test_file_sha256": "874fc99106e2f85f67180f4962f50b50ad2d921c8ba5ad8fad54fb12f62ded9f",
    "messages_semantics": "arm-blinded selected evidence only",
    "score_semantics": "selected evidence trajectory verifier score",
    "acting_outcome_semantics": "retained only as common provenance across cloned arms",
    "projection_and_provenance_semantics": "retained outside messages in r17_* audit fields",
    "downstream_truncation_rule": "pre-provider assertion required; transcript_max_chars must be frozen to at least 100000 for V3.1 qualification"
  },
  "tests": {
    "v3_1_updater_unit_tests": "4/4 PASS",
    "search_projection_runner_and_theory_regression": "20/20 PASS",
    "python_compile": "PASS"
  },
  "authority": {
    "v3_1_design": true,
    "independent_review": true,
    "fresh_zero_provider_mechanical_pilot": false,
    "provider_runtime_pilot": false,
    "e1_a": false,
    "e1_b": false,
    "paper_promotion": false,
    "submission": false
  }
}


===== BOUND ARTIFACT: v3_1_mechanical_draft_contract | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-v3-1-mechanical-pilot-draft-contract-20260828.json =====
{
  "schema_version": "1.0",
  "artifact_type": "e2-r17-v3-1-mechanical-pilot-contract",
  "date": "2026-08-28",
  "status": "DRAFT_ZERO_AUTHORITY_PENDING_INDEPENDENT_REVIEW",
  "run_root": "/data/wyt/e2-r17-search-projection/runtime-pilots/v3-1-mechanical-20260828",
  "runner": {
    "path": "scripts/run_e2_r17_v3_1_mechanical_pilot.py",
    "sha256": "3a486d529a9f2e0208d072a15de11c56bfd75ff92949af1b565e1adb012bc2f5"
  },
  "repair": {
    "path": "generated/e2-r17-v3-1-causal-purity-repair-20260828.json",
    "sha256": "2b4589d704037c9dd781c4091d03b12dddf727b6d7a7aad765dc7536863a6880"
  },
  "upstream_prompt_dataflow_audit": {
    "path": "generated/e2-r17-v3-1-upstream-prompt-dataflow-audit-20260828.json",
    "sha256": "ecd160e6c87b259c56e5a667fe94a9cc7310c37c5fca92ce514436c131d30d7c"
  },
  "historical_inputs": {
    "e0_root": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828",
    "e0_summary": "/data/wyt/e2-r17-search-projection/runs/e0-pilot-r4-r3-20260828/e0_pilot_summary.json",
    "e0_summary_sha256": "533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366",
    "expected_k8_pools": 12
  },
  "renderer": {
    "path": "research_pipeline/e2_r17_evidence_window_v2.py",
    "sha256": "6a79d4e671167a9c4b89fc0cfa8c4b95c1020a62043f409db07bb39a75d2a9f7",
    "tokenizer_package": "tiktoken",
    "tokenizer_version": "0.11.0",
    "tokenizer_encoding": "cl100k_base",
    "final_block_cap_tokens": 3072,
    "padding": false,
    "exact_final_retokenized_parity_required": true
  },
  "updater_wrapper": {
    "path": "research_pipeline/e2_r17_mindmemos_updater.py",
    "sha256": "9516ecfd54236d5ba22321cf96ebd897644396a87bc325fbd9632e12eefd004d",
    "test_path": "research_pipeline/test_e2_r17_mindmemos_updater_v31.py",
    "test_sha256": "874fc99106e2f85f67180f4962f50b50ad2d921c8ba5ad8fad54fb12f62ded9f",
    "transcript_max_chars": 100000,
    "score_semantics": "selected_evidence_trajectory"
  },
  "mindmemos": {
    "root": "/data/wyt/evidence-substrates/MindMemOS-20260817",
    "commit": "90491828726e1540442b17cd445d0308d0b8093c",
    "bound_files": {
      "src/mindmemos/mindmemos/pipelines/skill/evolution.py": "37bb22da6d4e8485d824c3c31e48f200561b05834a8a6bf3c057b29613b2bca0",
      "src/mindmemos/mindmemos/prompts/EN/skills/trajectory_summary.py": "771a5dc2efc369ed8b4c6d90b5ee470339263780eaf26265be24561b7156b95e",
      "src/mindmemos/mindmemos/prompts/EN/skills/skill_patch.py": "48ab68ee3fbb6f115269679358cbcc1f08f9a28318a95438860eae1bbf5a3f4c"
    }
  },
  "checks": [
    "revalidate every historical pool and trajectory SHA",
    "exact actual final WIN/MRW token parity on all 12 pools",
    "nonmixed WIN/MRW byte identity",
    "MRW differs from WIN only on mixed pools",
    "model-visible messages contain no projection/role/rollout/path/provider/provenance treatment labels",
    "selected evidence score equals selected trajectory verifier score",
    "served acting winner SHA and acting score remain identical across cloned WIN/MRW payload provenance",
    "no downstream first-party transcript truncation under frozen 100000-char limit",
    "pinned MindMemOS commit and bound source SHAs revalidate",
    "completed-unit receipts are content-addressed and revalidated on resume",
    "temporary corruption detector catches receipt SHA drift",
    "provider calls remain zero",
    "new actor rollouts remain zero",
    "scientific effectiveness is not evaluated"
  ],
  "checkpoint": {
    "unit": "historical K8 pool",
    "persist_immediately": true,
    "completed_manifest": "checkpoints/completed_units.jsonl",
    "resume": "revalidate completed receipt SHA then execute missing units only",
    "reuse_v3_failed_root": false
  },
  "forbidden": [
    "provider calls",
    "new actor rollouts",
    "held-out future-skill evaluation",
    "method effectiveness comparison",
    "scientific GO/HOLD/STOP from method outcome",
    "retrying the V3 failed contract/root",
    "E1-A generation",
    "E1-B updater execution",
    "paper promotion"
  ],
  "authority": {
    "independent_review": true,
    "execute_mechanical_pilot": false,
    "provider_runtime_pilot": false,
    "e1_a": false,
    "e1_b": false,
    "paper_promotion": false,
    "submission": false
  }
}


===== BOUND ARTIFACT: v3_failure_adjudication | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-v3-runtime-pilot-failure-adjudication-20260828.json =====
{
  "artifact_type": "e2-r17-v3-runtime-pilot-failure-adjudication",
  "schema_version": "1.0",
  "date": "2026-08-28",
  "status": "FAIL_MECHANICAL_TOKEN_PARITY",
  "contract": "generated/e2-r17-v3-runtime-pilot-contract-20260828.json",
  "run_root": "/data/wyt/e2-r17-search-projection/runtime-pilots/v3-mechanical-20260828",
  "provider_calls": 0,
  "new_actor_rollouts": 0,
  "scientific_effectiveness_evaluated": false,
  "completed_units_before_failure": 3,
  "completed_unit_receipts_preserved": true,
  "failed_unit": "r17-b1-fmv-p8",
  "failure": {
    "check": "re-encode rendered WIN/MRW text and require exact token parity",
    "winner_rollout_index": 0,
    "mrw_rollout_index": 2,
    "winner_raw_tokens": 2775,
    "mrw_raw_tokens": 2026,
    "nominal_selected_tokens_each": 2026,
    "winner_reencoded_tokens": 2025,
    "mrw_reencoded_tokens": 2026,
    "difference": -1,
    "cause": "Decoding separately selected head/tail token slices and concatenating them can create a new BPE merge at the splice boundary; nominal selected-token equality therefore does not imply equality of the actual text re-tokenized by the provider tokenizer."
  },
  "contract_behavior": "The frozen V3 Pilot correctly failed instead of weakening the parity check. The V3 renderer policy is not modified under the same contract.",
  "additional_causal_purity_finding": "The legacy projection-packet renderer exposes arm-specific PROJECTION/ROLE/rollout metadata to the updater. Even with matched source tokens, those labels are an avoidable treatment cue. V3.1 must blind arm/projection metadata from updater-visible text while retaining it in provenance receipts.",
  "next_step": "Create a new V3.1 renderer/protocol that matches the entire updater-visible evidence block by actual re-tokenized count, with deterministic no-padding search, then independently review and rerun a fresh mechanical Pilot root.",
  "authority": {
    "v3_runtime_pilot_retry_under_same_contract": false,
    "v3_1_design_work": true,
    "provider_runtime_pilot": false,
    "e1_a": false,
    "e1_b": false,
    "paper_promotion": false
  }
}


===== BOUND ARTIFACT: v3_plan | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/consultations/e2-r17-experiment-plan-v3-20260828.md =====
# E2-R17 Experiment Plan V3 — Pre-Pilot Frozen Design

Date: 2026-08-28
Status: **V3_DUAL_REVIEW_REQUIRED_BEFORE_RUNTIME_PILOT**
Scientific authority: **ZERO until a separate authorization contract exists**

This plan supersedes V2 for future execution only. It does not rewrite E0, V1, V2, or their reviews.

## 1. Paper-level scientific question

Search is optimized for present acting: generate several trajectories and serve a high-scoring winner. Persistent self-evolution introduces a second consumer of the same generated object: the learner that updates future skill.

E2-R17 tests whether:

> a search selector that is optimal for current acting systematically changes the evidence distribution visible to a persistent learner, creating **compute shielding**: current user-facing failure becomes less visible even while success/failure contrast remains available in the discarded search pool.

The paper must not claim the already-published statement that failed trajectories can improve memory. ReasoningBank/MaTTS (ICLR 2026) already occupies that territory.

The narrower candidate contribution is:

1. formal separation of acting projection and learning projection over the exact same generated search pool;
2. a search-compute evidence law showing how winner-visible failure and mixed-pool evidence move in opposite directions as K grows;
3. exact-same-pool causal identification of whether the hidden evidence changes future frozen skill;
4. a minimal one-witness repair if and only if the causal experiment supports it;
5. prospective regime prediction before confirmatory outcomes.

No abstract-level “compute-shielding law causes long-run degradation” claim is permitted until prospective E3 passes.

## 2. Theory and estimands

Let the exact K-pool be `T_1:K`, binary verifier outcomes `Y_i`, fixed initial persistent state `S`, acting selector `a`, learning projection `g`, frozen updater `U`, and future held-out value `J`.

### 2.1 Rescue identity

For arbitrary correlated joint rollout laws:

`A_K - A_1 = P(Y_1=0, max_i Y_i=1) = V_pre(K)-V_winner(K)`.

No rollout independence is required.

Under iid Bernoulli success probability `p`:

`Gamma_K(p)=(1-p)-(1-p)^K`.

This is an acting-side identity only.

### 2.2 Compute-shielding support law

Define:

- `A_K=P(any success)`;
- `W_K=P(all fail)` = failure visible through winner-only acting/learning;
- `F_K=P(any failure)` = failure available anywhere in the generated pool;
- `M_K=P(any success and any failure)` = mixed-pool contrast support.

For nested search pools, without iid:

- `A_K` nondecreasing in K;
- `W_K` nonincreasing;
- `F_K` nondecreasing;
- `M_K` nondecreasing.

Under iid:

- `A_K=1-(1-p)^K`;
- `W_K=(1-p)^K`;
- `F_K=1-p^K`;
- `M_K=1-p^K-(1-p)^K`.

For fixed `0<p<1`, K increasing drives `A_K->1`, `W_K->0`, `F_K->1`, `M_K->1`.

This law establishes **availability and visibility**, not learning utility.

### 2.3 Primary causal learning estimand

Define `g_MRW`:

- nonmixed pool: identical to `g_WIN`;
- mixed pool: expose the deterministic lowest-rollout-index failed nonwinner as the one updater-visible source trajectory;
- acting always serves exactly the same winner.

Then exactly by conditioning:

`Delta_K = E[J(U(S,g_MRW(T_1:K)))-J(U(S,g_WIN(T_1:K)))] = M_K * delta_K`,

where:

`delta_K = E[D | mixed pool]`.

No assumption `delta_K>0` is made.

- `delta_K>0`: hidden witness has reusable future value;
- `delta_K=0`: evidence shielding exists but is learning-irrelevant;
- `delta_K<0`: failed witness is harmful or misleading.

E1 is designed to identify this learning-side term.

## 3. Frozen historical E0

E0 summary SHA:

`533abf55359360bd408a4878235d24b5192d77f2471f0676bb8b10d570ad0366`

Historical E0 decision remains **HOLD** under its original rescue-count gate.

Observed K=8:

- 12/12 acting success;
- 8/12 mixed pools;
- 1/12 rescue events;
- 0/12 winner-visible failures;
- 16 hidden failed nonwinner trajectories;
- failure evidence across 5/6 frozen families.

The old 42-task rescue-quota extension is not authorized under V3 because rescue count is not the treatment-support quantity for MRW.

## 4. Frozen controlled split

Use exactly:

`/data/wyt/e2-r17-search-projection/controlled-spreadsheet-suite-v2`

Split manifest SHA:

`aca995b69b6dcd48ddde8aa92b0d14a278ee3194eac5e494feb9c986db4567d9`

Suite manifest SHA:

`2d02b2102778b898c6ff16074bfc2203b80f1d0f1441e13e66127a533b1d9ce4`

Selection is outcome-blind and SHA256/family-balanced.

E1 structure:

- 6 predeclared failure families;
- 2 independent update streams per family;
- 8 distinct update tasks per stream;
- 12 stream units, 96 update tasks total;
- 18 common held-out probes never fed to the updater.

No task substitution is allowed after E1 support is observed.

## 5. E1-A — exact pool generation and pre-treatment support gate

Generate exactly one K=8 pool for each of the 96 frozen update tasks from the same frozen initial skill state.

Actor rollouts:

`96 x 8 = 768`.

All rollout artifacts and K=1/2/4/8 nested prefix pools are persisted immediately and content-addressed. **No updater call is made during E1-A.**

### 5.1 Hard causal-identifiability gate

After all 96 K=8 pools are frozen:

1. `mixed_pool_count >= 24/96`;
2. at least `8/12 streams` each contain `>=2/8 mixed pools`;
3. protocol integrity is complete for every scientific unit;
4. completed-unit SHAs revalidate before the gate is evaluated.

These are hard floors. No rounding, waiver, or “close enough” adjudication exists:

- 23/96 -> fail;
- 7/12 exposed streams -> fail;
- a stream with only 1 mixed pool does not count as exposed for this gate.

A failed hard support gate stops E1 before updater calls. A redesign requires a new protocol and cannot replace individual tasks based on observed support.

### 5.2 Generalization qualification, separate from causal authorization

Failure-family coverage is not required to identify the pooled stream-level causal effect.

Record instead:

`family_support = number of predeclared families containing >=1 mixed pool`.

- `>=4/6`: family-heterogeneity description and later family-wise E3 prediction may proceed;
- `<4/6`: pooled E1 may still proceed if the hard gate passes, but broad family-generalization and E3 family-ranking claims are blocked.

This separation prevents an arbitrary family threshold from controlling the core causal estimand.

## 6. Frozen evidence renderer — fixed before Pilot

Primary WIN/MRW evidence matching is frozen now, not selected after Pilot.

Implementation:

`research_pipeline/e2_r17_evidence_window.py`

Frozen configuration:

- tokenizer package: `tiktoken==0.11.0`;
- encoding: `cl100k_base`;
- source-evidence cap: 3072 tokens;
- canonical evidence includes branch-specific user/assistant/tool messages plus verifier score/message;
- common system prompt and provenance/provider metadata are excluded from updater-visible source evidence;
- for each exact WIN/MRW task pair:
  `B_pair=min(3072, raw_tokens(WIN), raw_tokens(MRW))`;
- both arms receive exactly `B_pair` source-evidence tokens;
- when truncation is needed: first one-third + final two-thirds tokens;
- no padding and no additional semantic evidence;
- every rendered source is hash-bound with raw counts, matched count, tokenizer identity, cap, and rendered SHA.

Reason for head/tail preservation: the head retains task/intention context and the tail retains terminal execution/verifier/failure evidence. The same deterministic transform is applied to both arms.

If this exact renderer proves mechanically infeasible during the outcome-blind runtime Pilot, the Pilot fails. V3 does not authorize switching to raw evidence based on scientific outcome.

## 7. E1-B — updater causal tranche

E1-B is authorized only after E1-A support passes and a later immutable execution contract binds current model identity, updater revision, renderer revision, budgets, and run roots.

### 7.1 Core cloned arms

#### WIN-A — primary control

- exact same 8 pools in the stream;
- acting serves each frozen winner;
- updater receives one matched-window winner trajectory per task.

#### WIN-B — identical-treatment negative control

- exactly the same input projection as WIN-A;
- separate fresh cloned persistent state from the same initial skill;
- same updater configuration and model;
- independent provider calls.

Purpose: empirically measure residual updater/provider stochasticity even with temperature 0.

#### MRW — primary intervention

- exact same pools and served winners as WIN-A;
- nonmixed task: identical updater evidence as WIN;
- mixed task: one matched-window deterministic lowest-index failed nonwinner;
- no extra actor calls;
- one evidence trajectory per task, exactly as WIN.

#### RB-AGG — predeclared published-collision diagnostic

A ReasoningBank/MaTTS-style same-pool semantic adapter aggregates success/failure evidence from the exact frozen pool into updater evidence under a predeclared budget/accounting rule.

This arm runs regardless of MRW GO/HOLD, provided its mechanical semantic Pilot passes.

It is labeled `ReasoningBank-style same-pool aggregation`, **not** “official ReasoningBank reproduction,” because:

- the spreadsheet substrate is not the paper's native WebArena substrate;
- current public MaTTS launcher semantics require reproduction adjudication;
- official source-faithful ReasoningBank remains a later WebArena lane.

RB-AGG exists to prevent the paper from confusing a minimal failed-witness effect with the already-published broader idea of aggregating successful and failed trajectories.

### 7.2 Updater freeze

For all E1-B arms:

- first-party updater: MindMemOS `SkillEvolver` at a contract-bound commit;
- same initial SKILL.md SHA;
- same batch size: exactly 8 task packets;
- same updater prompt/parser/config;
- provider retries: 0;
- thinking: disabled;
- if first-party call omits temperature, adapter forces `temperature=0.0`;
- resolved updater identity requalified immediately before tranche authorization;
- parse-correction attempts remain explicit and counted, never hidden provider retries;
- every provider call persisted atomically without raw provider IDs or credentials.

The WIN-A/WIN-B control is required because temperature 0 does not imply mathematical determinism of a hosted model.

## 8. E1 held-out evaluation

For every learned stream state and every arm:

- freeze post-update SKILL.md and SHA;
- evaluate exactly the same 18 held-out probes;
- executor K=1;
- no search at evaluation;
- identical model/runtime/verifier;
- every probe output and verifier result persisted immediately.

Per-stream endpoint:

`J_s(arm)=mean success over 18 held-out probes`.

Independent units: 12 stream-level learned states. The 18 probes are repeated measurements, not independent causal units.

## 9. Statistical decision rules

### 9.1 Negative-control gate first

Before interpreting MRW:

`N_s = J_s(WIN-B)-J_s(WIN-A)`.

Practical equivalence margin:

`epsilon=1/18=0.055555...` absolute success.

Use paired TOST at alpha=.05:

- equivalently, the 90% paired-mean t interval must lie entirely within `[-epsilon,+epsilon]`;
- report a 90% paired-bootstrap interval as robustness.

If WIN-A and WIN-B do not establish equivalence, the causal tranche is:

`HOLD_UPDATER_STOCHASTICITY`

and MRW/RB differences are not promoted as evidence causality.

### 9.2 Primary superiority: MRW vs WIN-A

For 12 paired stream effects:

`D_s=J_s(MRW)-J_s(WIN-A)`.

Primary superiority test:

- exact one-sided sign-flip/randomization distribution over all `2^12=4096` within-pair sign assignments;
- alpha=.05;
- mean paired effect must be positive.

Report:

- exact p;
- mean and median `D_s`;
- 95% paired bootstrap CI over streams;
- per-stream mixed dose and effect;
- descriptive family grouping only.

Primary **GO** requires:

- negative-control equivalence passed;
- mean `D_s>0`;
- exact one-sided p<=.05;
- 95% paired-bootstrap lower bound >0;
- no evidence-rendering/provenance failure.

### 9.3 Qualified STOP vs HOLD

For MRW-vs-WIN, also perform paired TOST with `epsilon=1/18`, alpha=.05.

- equivalence supported -> `STOP_MRW_PRACTICALLY_NULL`;
- significantly negative effect -> `STOP_MRW_HARMFUL`;
- superiority fails and equivalence fails -> `HOLD_UNDERPOWERED_OR_HETEROGENEOUS`.

“Nonsignificant” alone is never interpreted as no effect.

### 9.4 Power disclosure

With n=12 paired stream units, one-sided alpha=.05 and 80% power under a paired-t approximation requires standardized paired effect approximately:

`d=0.7664`.

For equal-magnitude positive/negative pairs, 10/12 positive pairs are required for a one-sided sign probability below .05. Therefore E1 is intentionally decisive mainly for moderate-to-large repeatable effects; small effects may remain HOLD.

No later benchmark zoo is allowed to convert an inconclusive/negative core mechanism into a positive causal claim.

## 10. Predeclared collision interpretation including RB-AGG

After the WIN negative-control gate:

| MRW vs WIN | RB-AGG vs WIN | Interpretation |
|---|---|---|
| superior | superior | hidden search evidence has learning consequence; test whether one witness is practically equivalent to richer aggregation; never claim generic failure utility as novelty |
| superior | equivalent/null | minimal failed witness is specifically useful under this updater; investigate why richer aggregation diluted it |
| equivalent/null | superior | reject MRW as final repair; effect is aggregation-sensitive and overlaps ReasoningBank more strongly; novelty is narrowed substantially |
| equivalent | equivalent | central learning-consequence mechanism STOP for this substrate |
| negative | any | failed-witness repair rejected; do not promote MRW |

`RB-AGG` is a secondary collision diagnostic, not part of the primary MRW superiority alpha claim. Any inferential multiplicity beyond the primary contrast is labeled secondary/exploratory unless a later contract predeclares adjustment.

## 11. Additional diagnosis after primary results

Only after the primary and collision outcomes are frozen, diagnostic arms may be interpreted according to predeclared roles:

- Full Pool — information-retention upper bound, larger evidence budget;
- deterministic random nonwinner — generic branch-diversity control;
- success nonwinner when available — alternative-success control.

These cannot rescue a failed primary MRW claim. They only determine what aspect of nonwinner evidence mattered.

## 12. Published baseline hierarchy

Headline formally published baselines:

1. ReasoningBank/MaTTS — ICLR 2026;
2. PolySkill — ICLR 2026;
3. ACE — ICLR 2026;
4. Agent Workflow Memory — ICML 2025.

Extended:

5. SAGE — ACL 2026 Long.

ArXiv-only SkillCAT, Branch2Skill, SkillOpt, RethinkSkill, TSR remain collision/Related Work and are not counted as headline published baselines.

Pinned first-party repo SHAs and implementation caveats remain bound in:

`consultations/e2-r17-published-baseline-audit-v2-20260828.md`.

## 13. External evaluation uses two noninterchangeable lanes

### Lane A — source-faithful reproduction

Use first-party harness + stated/supported paper model where available. Record every deviation.

Current credential state on 69 means Gemini/OpenAI/Anthropic/SambaNova source lanes are not yet runtime-qualified. Model substitution is not allowed to masquerade as source-faithful reproduction.

If source-faithful reproduction remains blocked at submission:

> “We could not execute the first-party source-model lane for this baseline because the required provider/model route was unavailable in our execution environment; we therefore report only the separately labeled unified rerun and do not call it an exact reproduction.”

ReasoningBank additionally requires adjudication of the current public scaling launcher before any “source-faithful” label.

### Lane B — unified rerun

Direct quantitative ranking is allowed only under a matched substrate:

- same benchmark revision;
- same task IDs;
- same executor per comparison block;
- same environment/tool interface;
- same generated-pool accounting where applicable;
- explicit updater/context budgets;
- same held-out evaluator.

Cross-model robustness claims require at least:

- 2 independently qualified executor models;
- preferably >=2 model families.

If only one model qualifies, report a single-model result and make no cross-model robustness claim.

Model inclusion is based only on outcome-blind runtime/tool qualification, not R17 gain.

## 14. Public benchmark sequence after E1 GO

### E2-A WebArena — primary published-baseline lane

ReasoningBank, AWM, and PolySkill all expose first-party WebArena implementations.

Core matched methods after adapter Pilot:

- base/no persistent learning;
- Winner-only;
- final minimal E2-R17 projection if E1 GO;
- Full Pool where budget interpretation is explicit;
- AWM;
- ReasoningBank/MaTTS;
- PolySkill when semantic/runtime fairness passes.

Source-faithful scores and unified reruns appear in separate tables.

### E2-B AppWorld — second domain

Published anchors:

- ACE;
- SAGE extended.

Unified matched methods include base, Winner, final R17 projection, ACE adapter, and Full Pool where meaningful. SAGE is never forced into false equality with context-only methods; parametric training compute is reported separately.

### E2-C SpreadsheetBench Verified-400 — additional transport

Retain if budget permits because it is close to the controlled substrate, but it is not the only headline public comparison.

## 15. E3 prospective regime prediction

Only after E1 establishes a learning consequence.

On development/calibration streams estimate:

- `M_z(K)` availability;
- conditional diagnostic-value proxies/effect estimates;
- K ordering and null regions.

Before untouched future streams are evaluated, hash-freeze:

- effect sign;
- K ordering;
- family ranking if family-support qualification passed;
- predicted null cells.

Then compare prediction vs held-out future outcomes.

Required outputs:

- sign accuracy;
- rank correlation where identified;
- calibration of predicted vs observed effect;
- failed predictions retained.

If E3 fails, delete prospective regime-law claims and retain only the E1 causal finding.

## 16. E4 multi-round persistent evolution

Only after E1 + at least one public transport result pass.

Matched streams:

- low-search / winner learning;
- high-search / winner-only learning;
- high-search / final R17 learning projection;
- optional precommitted control.

After each update batch:

- freeze skill SHA;
- common K=1 evaluation;
- separately record current online acting reward and future frozen-skill value.

Question: can current search improve while future persistent learning degrades, and can a corrected learning projection prevent that divergence?

## 17. E5 topology

Only after earlier evidence chain passes.

Matched-call factorial:

`parallel best-of-K vs sequential refinement`

x

`winner/final-only learning vs history-preserving learning`.

This tests projection semantics rather than raw compute amount.

## 18. Runtime Pilot before any full scientific authorization

The runtime Pilot is **outcome-blind with respect to method effectiveness**. It may use development or frozen historical E0 artifacts but cannot inspect future E1 held-out skill outcomes.

It must validate:

1. exact tokenizer dependency and matched-window renderer;
2. exact token parity on WIN/MRW pairs;
3. no system/provenance leakage into updater source evidence;
4. MRW differs from WIN only on mixed pools;
5. WIN-A/WIN-B receive byte-identical updater input packets before provider calls;
6. temperature=0, retry=0, thinking disabled are present in receipts;
7. RB-AGG semantic adapter has fixed source-pool provenance and explicit evidence accounting;
8. updater calls/tokens/latency and parse-correction frequency are measured for budget purposes only;
9. crash-and-resume revalidates SHA and executes missing units only;
10. no model/baseline is promoted based on observed R17 performance.

The Pilot may fail a runtime/measurability condition. It may not select a renderer/model because one gives a better scientific effect.

## 19. Checkpoint and recovery

Every complete unit persists immediately:

- rollout raw trajectory / artifact / verifier / provider hashes;
- K-pool and nested prefix pools;
- projection packet and matched-window receipt;
- updater input/output, pre/post skill, adapter receipts;
- each held-out evaluation.

Three layers:

- `raw/` immutable;
- `checkpoints/` completed/missing/failed manifests;
- `summary/` rebuildable.

On resume:

1. load completed manifest;
2. re-hash every content-addressed completed unit;
3. quarantine any SHA mismatch and STOP rather than trust it;
4. execute only missing units.

After MCP 502/timeout/SSH disconnect, inspect process, lock, summary, and completed manifests before any relaunch.

## 20. Budget gate

No V3 full scientific run is authorized until the outcome-blind runtime Pilot freezes:

- actor calls / rollout;
- actor input/output tokens / rollout;
- updater provider calls / stream/arm;
- updater input/output tokens / stream/arm;
- parse-correction rate;
- held-out evaluation calls/tokens;
- wall time;
- hard ceiling and stop-on-budget behavior.

Known structural E1-A actor-rollout count is 768. Historical E0 token/call rates are planning references only and cannot substitute for the V3 Pilot budget receipt.

## 21. V3 pre-review decision table

Current status before V3 independent review:

- theory correction: implemented/tested;
- mixed-pool projection: implemented/tested;
- matched evidence renderer: implemented, exact tokenizer dependency intentionally not installed in shared environment yet;
- updater temperature default: frozen to 0 for future calls and tested;
- published baseline pins: audited;
- V2 dual review: both REVISE; adjudicated;
- V3 runtime Pilot: **NOT AUTHORIZED YET**;
- E1-A pool generation: **NOT AUTHORIZED**;
- E1-B updater: **NOT AUTHORIZED**;
- public benchmark full run: **NOT AUTHORIZED**.

Next gate: independent Kimi K3 + DeepSeek V4-Pro V3 review. Only if both allow outcome-blind runtime Pilot may the isolated renderer/updater/baseline-adapter Pilot contract be executed.


===== BOUND ARTIFACT: published_baseline_audit | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/consultations/e2-r17-published-baseline-audit-v2-20260828.md =====
# E2-R17 Published Baseline Audit V2

Date: 2026-08-28
Status: **PUBLISHED_TOP_VENUE_BASELINE_SET_FROZEN_FOR_V2_REVIEW**
Scope: baseline selection and implementation fidelity only; no scientific outcome authority

## 1. Selection rule

The main E2-R17 quantitative baseline set must prioritize methods that satisfy all three conditions:

1. formally published at a top-tier peer-reviewed venue by 2026-08-28;
2. directly relevant to persistent agent memory / skill / context self-improvement;
3. an official or first-party implementation can be pinned and audited.

ArXiv-only works may remain in collision review and Related Work, but they do not occupy the headline baseline slots in the main effectiveness table.

This V2 rule supersedes the V1 baseline ranking that elevated SkillCAT, Branch2Skill, SkillOpt, and RethinkSkill before publication status was treated as a hard primary-baseline criterion. Their prior audits are preserved as historical artifacts; they are not deleted.

## 2. Frozen official implementation pins

All repositories below were actually resolved from their upstream repositories on 69 and shallow-cloned under:

`/data/wyt/e2-r17-search-projection/baselines/published/`

| Method | Venue | Official / first-party repository | Pinned HEAD | Current role |
|---|---|---|---|---|
| ReasoningBank / MaTTS | ICLR 2026 | `google-research/reasoning-bank` | `ed80611788292ea739f1effd31f16c53823b8a0d` | **Primary collision + main published baseline** |
| PolySkill | ICLR 2026 | `simonucl/PolySkill` | `fff8807d7501d93188f9f658f4d0af2f29f35c23` | **Main published skill-learning baseline** |
| ACE | ICLR 2026 | `ace-agent/ace` | `82709de050e1db6e6ef2f07bcb0393560b94992a` | **Main published context-evolution baseline** |
| ACE AppWorld companion | ICLR 2026 | `ace-agent/ace-appworld` | `928e86877d34cd10eaba159606386f93a1765090` | Source-faithful AppWorld harness |
| Agent Workflow Memory (AWM) | ICML 2025 | `zorazrw/agent-workflow-memory` | `8c0ff8cd11d648c8fceb99e4e42f37e3b75381b1` | **Canonical published workflow-memory anchor** |
| SAGE | ACL 2026 Long | `amazon-science/SAGE` | `3c9244e82244abb1adc5467ee601a03ba0f433a0` | Extended published parametric/skill-library baseline |

Primary venue sources:

- ReasoningBank: ICLR 2026 conference paper / poster; official Google Research repository.
- PolySkill: ICLR 2026 conference proceedings; code linked from the paper.
- ACE: ICLR 2026; project page and first-party repositories.
- AWM: ICML 2025, PMLR 267.
- SAGE: ACL 2026 Long Paper, ACL Anthology 2026.acl-long.69.

## 3. Method and implementation audit

### 3.1 ReasoningBank / MaTTS — ICLR 2026

**Scientific overlap.** ReasoningBank explicitly distills generalizable reasoning strategies from both successful and failed experiences. MaTTS further couples memory to test-time scaling: scaling produces diverse trajectories, including successes and failures, and those experiences are aggregated to improve memory. Therefore E2-R17 cannot claim novelty from any of the following statements:

- failed trajectories can be useful;
- success/failure contrast can improve memory;
- test-time scaling can produce learning signal;
- memory and test-time scaling can be combined.

**Published experiment axis.** The ICLR paper includes WebArena and software-engineering experiments. The official WebArena scaling launcher defaults to `gemini-2.5-flash`.

**Official code pin.** `ed80611788292ea739f1effd31f16c53823b8a0d`.

**Implementation audit finding that must be resolved before source-faithful reproduction.** At this pinned commit:

1. `WebArena/pipeline_scaling.py` launches `num_trials` parallel rollouts into `results_0`, ..., `results_{K-1}`.
2. After the loop, the memory-induction call passes only `--result_dir results_{i}`, where `i` is the final loop index, together with `--num_samples K`.
3. `WebArena/induce_scaling.py` loops over `num_samples`, but inside the loop sets `res_dir = args.result_dir` without varying the directory.

Thus the current public launcher appears capable of repeatedly reading one results directory instead of explicitly iterating over K distinct rollout directories. This is an **implementation-reproduction caveat**, not a claim that the published scientific result is invalid. E2-R17 must not silently patch the baseline and call the patched result “exact reproduction.” The adapter must first establish which public code path corresponds to the published MaTTS experiment; any repair must be separately named and provenance-bound.

**E2-R17 collision boundary.** The remaining defensible novelty is not “failure-aware memory.” It is the causal object:

`same generated pool -> acting projection -> updater-visible evidence distribution -> future frozen skill`,

with the served winner, actor calls, initial persistent state, updater, and held-out evaluation held fixed.

### 3.2 PolySkill — ICLR 2026

**Scientific object.** PolySkill learns reusable web-agent skills by separating an abstract skill goal from concrete site-specific implementations, targeting generalizable and compositional skills.

**Paper models exposed in the public harness.** The current repository lists:

- GPT-4.1,
- Claude-3.7-Sonnet,
- Qwen3-Coder-480B-A35B,
- GLM-4.5.

**Benchmarks.** WebArena and Mind2Web.

**Official code pin.** `fff8807d7501d93188f9f658f4d0af2f29f35c23`.

**Important fidelity caveat.** The repository explicitly states that the 2026-07 public code is a **clean-room re-release**: the original experiment infrastructure depended on internal systems and the public harness was rebuilt on BrowserGym + LiteLLM. Therefore it is first-party and runnable, but it is not byte-for-byte the original internal experiment harness. This caveat must appear in the reproduction manifest.

**Use in E2-R17.** Strong published skill-induction comparison on WebArena. It is not an exact-same-pool causal control because its scientific object is polymorphic skill abstraction rather than projection of a frozen search pool.

### 3.3 Agent Workflow Memory — ICML 2025

**Scientific object.** AWM induces reusable workflows from past examples/experiences and retrieves them for future web tasks. Online AWM learns from prior executions judged correct by an evaluator.

**Published WebArena model.** The ICML version reports `gpt-4o-2024-05-13` with temperature 0.0. The current public WebArena runner also defaults to `openai/gpt-4o`; workflow induction supports GPT-3.5/GPT-4/GPT-4o.

**Benchmarks.** WebArena and Mind2Web.

**Official code pin.** `8c0ff8cd11d648c8fceb99e4e42f37e3b75381b1`.

**Use in E2-R17.** Canonical success-workflow memory anchor. Particularly useful as a contrast against ReasoningBank because ReasoningBank itself treats AWM as a successful-routine memory baseline.

### 3.4 ACE — ICLR 2026

**Scientific object.** ACE treats context as an evolving playbook and updates it through Generator -> Reflector -> Curator roles using execution feedback, with incremental delta updates designed to avoid context collapse and brevity bias.

**First-party AppWorld implementation.** The pinned companion repository provides online/offline AppWorld adaptation/evaluation configs and source code.

At `928e86877d34cd10eaba159606386f93a1765090`, `experiments/configs/ACE_online_no_GT.jsonnet` explicitly configures all three roles — generator, reflector, curator — as:

`DeepSeek-V3.1` via the SambaNova provider, temperature 0.

**Use in E2-R17.** Main published context-evolution baseline on AppWorld. It is especially relevant to long-lived context learning but does not isolate an acting-selector-induced evidence-distribution intervention.

### 3.5 SAGE — ACL 2026 Long

**Scientific object.** SAGE uses Skill-Augmented GRPO, sequential rollout, accumulated skill libraries, and skill-integrated reward for parametric self-improvement on AppWorld.

**Published/public model substrate.** The released SFT config points to `Qwen/Qwen2.5-32B-Instruct`. The README states that the expert-experience dataset was generated with Claude 3.5 Sonnet V2. The full SAGE training recipe requires multi-node H100-scale compute; AppWorld evaluation deploys the trained model via vLLM.

**Official code pin.** `3c9244e82244abb1adc5467ee601a03ba0f433a0`.

**Use in E2-R17.** Extended published baseline for the AppWorld long-term self-improvement story. Because SAGE changes model weights and reward optimization, it should not be treated as a matched projection-only control in E1.

## 4. Main baseline hierarchy for V2

### Tier P1 — headline published baselines

1. **ReasoningBank / MaTTS (ICLR 2026)** — closest collision and mandatory main baseline.
2. **PolySkill (ICLR 2026)** — strong continual skill-learning baseline on WebArena.
3. **ACE (ICLR 2026)** — strong context-evolution baseline on AppWorld.
4. **AWM (ICML 2025)** — canonical workflow-memory anchor, especially valuable because ReasoningBank directly contrasts against successful-routine memory.

### Tier P2 — published extended baseline

5. **SAGE (ACL 2026 Long)** — parametric RL + skill library; use for external long-horizon comparison, not exact-same-pool E1.

### Tier C — collision / related work, not headline baseline

- SkillCAT — arXiv-only at current audit time.
- Branch2Skill — arXiv-only at current audit time.
- SkillOpt — arXiv-only at current audit time.
- RethinkSkill / Rethinking Self-Evolving Agent Skills — arXiv-only at current audit time.
- TSR — search/training/topology context; not a matched persistent-skill baseline.

These works may still alter novelty wording and ablation design. They should not be used to inflate the published-baseline count.

## 5. Consequence for benchmark selection

The published baseline set changes the preferred external-validation benchmarks.

### Controlled Spreadsheet suite

Keep for E0/E1 mechanism identification because the exact same-pool invariants, artifact verifier, and failure families are already qualified. It is **not** the primary literature-comparison environment.

### WebArena — primary published-baseline transport lane

ReasoningBank, PolySkill, and AWM all have first-party WebArena implementations. Therefore WebArena is the strongest environment for a unified published-baseline comparison.

Recommended headline WebArena set after runtime qualification:

- No persistent learning / base agent,
- AWM,
- ReasoningBank / MaTTS,
- PolySkill,
- Winner-only search memory,
- Mixed-Rejected-Witness,
- Full Pool,
- final simplest E2-R17 projection.

Not every method is required on every executor. Use source-faithful and unified lanes below.

### AppWorld — second published-baseline transport lane

ACE and SAGE have first-party AppWorld implementations. AppWorld provides a complementary context/skill-evolution domain and is preferable to using an arXiv-only benchmark as the sole second headline environment.

Recommended AppWorld set after runtime qualification:

- base agent,
- ACE,
- SAGE where compute/weight-update scope is feasible,
- Winner-only,
- Mixed-Rejected-Witness,
- Full Pool / final method.

SAGE can be reported as source-faithful published reference plus a feasible unified evaluation if full retraining is prohibitively expensive; published numbers must never be mixed into the unified rerun table as if directly comparable.

### SpreadsheetBench Verified-400

Retain as an additional public transport domain if budget allows because it is already tightly connected to the controlled mechanism substrate. It should no longer be the only headline comparison domain.

## 6. Model fairness must use two lanes

There is no single executor model shared by all headline published baselines:

- ReasoningBank WebArena default: Gemini-2.5-Flash;
- AWM published WebArena: GPT-4o-2024-05-13;
- PolySkill: GPT-4.1 / Claude-3.7-Sonnet / Qwen3-Coder-480B-A35B / GLM-4.5;
- ACE AppWorld: DeepSeek-V3.1 in the first-party config;
- SAGE: Qwen2.5-32B-Instruct base with Claude-3.5-Sonnet-V2 expert-data generation.

Pretending there is a “common published model” would create a false comparison axis. V2 therefore adopts two separate lanes.

### Lane A — source-faithful reproduction

For each published baseline, first reproduce/qualify its first-party environment with its stated model or the closest explicitly supported model. Record exact repository SHA, model identity, dataset version, and any deviation. These results answer: **does our local reproduction agree with the published method under its intended substrate?**

### Lane B — unified causal/effectiveness rerun

Choose one or more executor/updater configurations that all candidate methods can actually support, then rerun the methods under:

- same benchmark version,
- same task IDs,
- same base executor,
- same action/environment interface,
- same actor-call accounting,
- matched update/context budget where scientifically meaningful,
- same held-out evaluator.

These results answer: **under a matched substrate, which learning policy performs better?**

Source-faithful and unified results must never be merged into one ranking column.

## 7. Model-matrix implication

The old V1 “pin Qwen3.5-35B-A3B or Qwen3.6-35B-A3B” P0 issue came from an arXiv-led baseline set. After the user-mandated published-baseline correction, that exact release choice is no longer a scientifically privileged common axis.

Therefore V2 should not simply choose one of those two models to satisfy the obsolete V1 gate. Instead it must freeze a new model matrix after checking availability for the **published** source-faithful lanes and a separate unified rerun lane.

Candidate practical anchors for the unified lane may still include a qualified Qwen open model plus the already qualified DeepSeek family, but their role must be described as a matched rerun/capability-spread axis, not as “the model used by the strongest baselines.”

## 8. Fairness requirements for the eventual main tables

1. Do not paste literature-reported scores into the unified-rerun main table.
2. Keep a separate “reported literature results” table, explicitly non-comparable across models/budgets.
3. For unified reruns, match task IDs and environment revision.
4. For memory/context methods, report updater-visible evidence tokens and update calls.
5. For search methods, report generated trajectories and actor calls, not just served trajectories.
6. For parametric RL methods such as SAGE, separately report training compute; do not force false token-budget equivalence with context-only methods.
7. Record whether each baseline receives success-only, failure-only, full-pool, or summarized evidence.
8. Record whether the baseline changes acting behavior during evidence generation; this matters for exact-same-pool interpretation.
9. Any adapter/patch to official code receives its own SHA and a label such as `source-faithful-adapter`, never “official exact” unless no scientific semantics changed.

## 9. V2 decision

Published-baseline selection is now:

`ReasoningBank + PolySkill + ACE + AWM` as headline published methods, with `SAGE` extended.

The closest novelty threat is ReasoningBank. E2-R17 remains scientifically viable only if E1 establishes more than “failure experiences help”: it must causally identify selection-induced evidence shielding under an exact same-pool intervention and show a precommitted, budget-matched learning projection changes future frozen skill.


===== BOUND ARTIFACT: renderer_v31 | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/e2_r17_evidence_window_v2.py =====
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import importlib.metadata
import json
from typing import Any, Mapping, Sequence


TOKENIZER_PACKAGE = "tiktoken"
TOKENIZER_VERSION = "0.11.0"
TOKENIZER_ENCODING = "cl100k_base"
FINAL_BLOCK_CAP_TOKENS = 3072
HEAD_FRACTION = 1.0 / 3.0
MIN_SELECTED_SOURCE_TOKENS = 64
BLOCK_HEADER = "E2-R17 SELECTED EXPERIENCE\n<EVIDENCE_HEAD>\n"
BLOCK_BOUNDARY = "\n</EVIDENCE_HEAD>\n<EVIDENCE_TAIL>\n"
BLOCK_FOOTER = "\n</EVIDENCE_TAIL>"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_trajectory_text(payload: Mapping[str, Any]) -> str:
    """Canonical branch evidence shown to the updater.

    Arm/projection identity, rollout index, provider metadata, paths, receipts and
    the common system prompt are deliberately absent.  The verifier score/message
    remain because whether the selected experience succeeded or failed is part of
    the scientific evidence treatment itself.
    """
    messages: list[dict[str, Any]] = []
    for message in payload.get("messages") or []:
        if not isinstance(message, Mapping):
            continue
        if str(message.get("role") or "") == "system":
            continue
        messages.append(dict(message))
    return json.dumps(
        {
            "messages": messages,
            "score": payload.get("score"),
            "score_message": payload.get("score_message"),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _safe_decode(encoding: Any, tokens: Sequence[int]) -> str:
    """Decode a token slice without inserting Unicode replacement characters."""
    if hasattr(encoding, "decode_bytes"):
        return encoding.decode_bytes(list(tokens)).decode("utf-8", errors="ignore")
    return encoding.decode(list(tokens))


def _candidate_block(encoding: Any, raw_tokens: Sequence[int], selected_budget: int) -> tuple[str, int]:
    if selected_budget < 2:
        raise ValueError("selected_budget must be at least two tokens")
    tokens = list(raw_tokens)
    selected_budget = min(int(selected_budget), len(tokens))
    head = max(1, int(selected_budget * HEAD_FRACTION))
    tail = selected_budget - head
    if tail < 1:
        tail = 1
        head = selected_budget - 1

    if selected_budget >= len(tokens):
        # Preserve all source tokens in order; the explicit boundary marker is
        # inserted at the deterministic one-third point for both arms.
        head_tokens = tokens[:head]
        tail_tokens = tokens[head:]
    else:
        head_tokens = tokens[:head]
        tail_tokens = tokens[-tail:]

    text = (
        BLOCK_HEADER
        + _safe_decode(encoding, head_tokens)
        + BLOCK_BOUNDARY
        + _safe_decode(encoding, tail_tokens)
        + BLOCK_FOOTER
    )
    actual = len(encoding.encode(text))
    return text, actual


@dataclass(frozen=True)
class ExactMatchedBlockReceipt:
    tokenizer_package: str
    tokenizer_version: str
    tokenizer_encoding: str
    final_block_cap_tokens: int
    head_fraction: float
    min_selected_source_tokens: int
    left_raw_source_tokens: int
    right_raw_source_tokens: int
    left_selected_source_tokens: int
    right_selected_source_tokens: int
    matched_final_block_tokens: int
    left_block_sha256: str
    right_block_sha256: str
    search_lower_bound: int
    search_candidates_left: int
    search_candidates_right: int
    padding_used: bool
    arm_metadata_visible: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ExactMatchedEvidenceBlockRenderer:
    """Render two evidence blocks to the same *actual re-tokenized* length.

    V3's nominal token slicing failed because decoding and concatenating head/tail
    slices can create a fresh BPE merge at the splice.  V3.1 therefore searches
    deterministic source-token budgets for each arm and accepts only a pair whose
    final rendered UTF-8 texts re-encode to exactly the same token count under the
    frozen tokenizer.  No padding is used.  The largest common reachable final
    token count not exceeding `final_block_cap_tokens` is selected.

    The updater-visible wrapper is identical and arm-blinded.  Projection name,
    role, rollout index and provenance remain in receipts rather than the text the
    updater reasons over.
    """

    def __init__(self, *, final_block_cap_tokens: int = FINAL_BLOCK_CAP_TOKENS) -> None:
        if final_block_cap_tokens < MIN_SELECTED_SOURCE_TOKENS:
            raise ValueError("final block cap is too small")
        try:
            observed = importlib.metadata.version(TOKENIZER_PACKAGE)
        except importlib.metadata.PackageNotFoundError as exc:
            raise RuntimeError(
                f"{TOKENIZER_PACKAGE}=={TOKENIZER_VERSION} is required for the frozen E2-R17 V3.1 renderer"
            ) from exc
        if observed != TOKENIZER_VERSION:
            raise RuntimeError(
                f"frozen E2-R17 V3.1 renderer requires {TOKENIZER_PACKAGE}=={TOKENIZER_VERSION}, observed {observed}"
            )
        import tiktoken  # type: ignore

        self.encoding = tiktoken.get_encoding(TOKENIZER_ENCODING)
        self.final_block_cap_tokens = int(final_block_cap_tokens)

    def _reachable(
        self,
        raw_tokens: Sequence[int],
        *,
        start_budget: int,
        lower_bound: int,
    ) -> dict[int, tuple[int, str]]:
        reachable: dict[int, tuple[int, str]] = {}
        for budget in range(start_budget, lower_bound - 1, -1):
            text, actual = _candidate_block(self.encoding, raw_tokens, budget)
            if actual > self.final_block_cap_tokens:
                continue
            # For a given actual provider-visible length, keep the largest source
            # budget so the deterministic rule retains maximal evidence.
            reachable.setdefault(actual, (budget, text))
        return reachable

    def render_pair(self, left_text: str, right_text: str) -> tuple[str, str, ExactMatchedBlockReceipt]:
        left_raw = self.encoding.encode(left_text)
        right_raw = self.encoding.encode(right_text)
        if len(left_raw) < MIN_SELECTED_SOURCE_TOKENS or len(right_raw) < MIN_SELECTED_SOURCE_TOKENS:
            raise ValueError("both source evidences must contain at least 64 tokens")

        start = min(len(left_raw), len(right_raw), self.final_block_cap_tokens)
        # Search progressively wider deterministic windows.  The result is the
        # maximum common actual re-tokenized length, never a first-hit dependent
        # on arm order.
        lower_bounds = []
        for width in (32, 128, 512, 1024, start):
            lower = max(MIN_SELECTED_SOURCE_TOKENS, start - int(width))
            if not lower_bounds or lower != lower_bounds[-1]:
                lower_bounds.append(lower)
        if lower_bounds[-1] != MIN_SELECTED_SOURCE_TOKENS:
            lower_bounds.append(MIN_SELECTED_SOURCE_TOKENS)

        chosen: tuple[int, int, str, str, int, int, int] | None = None
        for lower in lower_bounds:
            left_map = self._reachable(left_raw, start_budget=start, lower_bound=lower)
            right_map = self._reachable(right_raw, start_budget=start, lower_bound=lower)
            common = set(left_map).intersection(right_map)
            if common:
                matched = max(common)
                left_budget, left_block = left_map[matched]
                right_budget, right_block = right_map[matched]
                chosen = (
                    left_budget,
                    right_budget,
                    left_block,
                    right_block,
                    matched,
                    len(left_map),
                    len(right_map),
                )
                search_lower_bound = lower
                break
        if chosen is None:
            raise RuntimeError("no exact common re-tokenized evidence-block length is reachable without padding")

        left_budget, right_budget, left_block, right_block, matched, left_n, right_n = chosen
        left_actual = len(self.encoding.encode(left_block))
        right_actual = len(self.encoding.encode(right_block))
        if left_actual != right_actual or left_actual != matched:
            raise AssertionError("V3.1 exact re-tokenized parity invariant failed")
        if matched > self.final_block_cap_tokens:
            raise AssertionError("V3.1 final block exceeded frozen cap")

        receipt = ExactMatchedBlockReceipt(
            tokenizer_package=TOKENIZER_PACKAGE,
            tokenizer_version=TOKENIZER_VERSION,
            tokenizer_encoding=TOKENIZER_ENCODING,
            final_block_cap_tokens=self.final_block_cap_tokens,
            head_fraction=HEAD_FRACTION,
            min_selected_source_tokens=MIN_SELECTED_SOURCE_TOKENS,
            left_raw_source_tokens=len(left_raw),
            right_raw_source_tokens=len(right_raw),
            left_selected_source_tokens=left_budget,
            right_selected_source_tokens=right_budget,
            matched_final_block_tokens=matched,
            left_block_sha256=sha256_text(left_block),
            right_block_sha256=sha256_text(right_block),
            search_lower_bound=search_lower_bound,
            search_candidates_left=left_n,
            search_candidates_right=right_n,
            padding_used=False,
            arm_metadata_visible=False,
        )
        return left_block, right_block, receipt


===== BOUND ARTIFACT: renderer_v31_tests | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/test_e2_r17_evidence_window_v2.py =====
from __future__ import annotations

import importlib.metadata
import unittest

from research_pipeline.e2_r17_evidence_window_v2 import (
    BLOCK_BOUNDARY,
    BLOCK_HEADER,
    FINAL_BLOCK_CAP_TOKENS,
    TOKENIZER_ENCODING,
    TOKENIZER_VERSION,
    ExactMatchedEvidenceBlockRenderer,
    _candidate_block,
    canonical_trajectory_text,
)


class _CharEncoding:
    def encode(self, text: str) -> list[int]:
        return [ord(char) for char in text]

    def decode(self, tokens: list[int]) -> str:
        return "".join(chr(token) for token in tokens)

    def decode_bytes(self, tokens: list[int]) -> bytes:
        return self.decode(tokens).encode("utf-8")


class EvidenceWindowV2Test(unittest.TestCase):
    def test_canonical_text_is_arm_blinded(self) -> None:
        payload = {
            "rollout_index": 7,
            "projection": "mixed_rejected_witness",
            "trajectory_path": "/secret/path",
            "provider_receipt": "opaque",
            "score": 0.0,
            "score_message": "formula mismatch",
            "messages": [
                {"role": "system", "content": "common system"},
                {"role": "user", "content": "fix workbook"},
                {"role": "assistant", "content": "attempt"},
            ],
        }
        text = canonical_trajectory_text(payload)
        self.assertIn("formula mismatch", text)
        self.assertIn("fix workbook", text)
        for forbidden in ["mixed_rejected_witness", "rollout_index", "/secret/path", "opaque", "common system"]:
            self.assertNotIn(forbidden, text)

    def test_candidate_always_uses_same_arm_blinded_wrapper(self) -> None:
        encoding = _CharEncoding()
        text, actual = _candidate_block(encoding, encoding.encode("abcdefghijklmnopqrstuvwxyz" * 10), 120)
        self.assertTrue(text.startswith(BLOCK_HEADER))
        self.assertIn(BLOCK_BOUNDARY, text)
        self.assertEqual(actual, len(encoding.encode(text)))
        self.assertNotIn("WIN", text)
        self.assertNotIn("MRW", text)

    def test_actual_tiktoken_pair_is_exact_when_dependency_available(self) -> None:
        try:
            observed = importlib.metadata.version("tiktoken")
        except importlib.metadata.PackageNotFoundError:
            self.skipTest("pinned tiktoken is intentionally absent from shared Python")
        if observed != TOKENIZER_VERSION:
            self.skipTest(f"requires tiktoken {TOKENIZER_VERSION}, observed {observed}")
        renderer = ExactMatchedEvidenceBlockRenderer()
        left = "A short spreadsheet execution. " * 800
        right = "A different failure trajectory with formula mismatch. " * 500
        left_block, right_block, receipt = renderer.render_pair(left, right)
        self.assertEqual(len(renderer.encoding.encode(left_block)), len(renderer.encoding.encode(right_block)))
        self.assertEqual(len(renderer.encoding.encode(left_block)), receipt.matched_final_block_tokens)
        self.assertLessEqual(receipt.matched_final_block_tokens, FINAL_BLOCK_CAP_TOKENS)
        self.assertFalse(receipt.padding_used)
        self.assertFalse(receipt.arm_metadata_visible)

    def test_identical_sources_remain_identical(self) -> None:
        try:
            observed = importlib.metadata.version("tiktoken")
        except importlib.metadata.PackageNotFoundError:
            self.skipTest("pinned tiktoken is intentionally absent from shared Python")
        if observed != TOKENIZER_VERSION:
            self.skipTest(f"requires tiktoken {TOKENIZER_VERSION}, observed {observed}")
        renderer = ExactMatchedEvidenceBlockRenderer()
        source = "same evidence " * 1000
        left, right, receipt = renderer.render_pair(source, source)
        self.assertEqual(left, right)
        self.assertEqual(receipt.left_selected_source_tokens, receipt.right_selected_source_tokens)

    def test_frozen_constants(self) -> None:
        self.assertEqual(TOKENIZER_VERSION, "0.11.0")
        self.assertEqual(TOKENIZER_ENCODING, "cl100k_base")
        self.assertEqual(FINAL_BLOCK_CAP_TOKENS, 3072)


if __name__ == "__main__":
    unittest.main()


===== BOUND ARTIFACT: updater_wrapper_v31 | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/e2_r17_mindmemos_updater.py =====
from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Sequence

from research_pipeline.e2_r17_search_projection_runner import ProjectionPacket, SearchPool, StreamProjection

_ID_NAMESPACE = uuid.UUID("8a1cab2c-aef8-4eb6-bcdf-21a88b4e2f17")


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha(payload: Any) -> str:
    return sha_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def _truncate_middle(text: str, limit: int) -> str:
    if limit <= 0 or len(text) <= limit:
        return text
    marker = f"\n...[{len(text) - limit} chars deterministically elided]...\n"
    usable = max(0, limit - len(marker))
    head = usable // 2
    tail = usable - head
    return text[:head] + marker + text[-tail:]


def render_trajectory_evidence(path: Path, expected_sha256: str, *, char_budget: int = 6000) -> str:
    if sha_file(path) != expected_sha256:
        raise RuntimeError(f"trajectory SHA mismatch: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    lines = [
        f"TASK_ID: {payload['case_id']}",
        f"ROLLOUT_INDEX: {payload['rollout_index']}",
        f"VERIFIER_SCORE: {payload['score']}",
        f"VERIFIER_MESSAGE: {payload.get('score_message', '')}",
        "TRAJECTORY:",
    ]
    for message in payload.get("messages") or []:
        role = str(message.get("role") or "unknown").upper()
        content = message.get("content")
        if content:
            lines.append(f"[{role}] {content}")
        for call in message.get("tool_calls") or []:
            function = call.get("function") or {}
            lines.append(
                f"[ASSISTANT_TOOL_CALL name={function.get('name', '')}] {function.get('arguments', '{}')}"
            )
        if role == "TOOL":
            lines.append(
                f"[TOOL_BINDING id={message.get('tool_call_id', '')} name={message.get('name', '')}]"
            )
    return _truncate_middle("\n".join(lines), char_budget)


def render_projection_packet(
    pool: SearchPool,
    packet: ProjectionPacket,
    *,
    slot_char_budget: int = 6000,
) -> tuple[str, dict[str, Any]]:
    pool.validate()
    sections = [
        "E2-R17 LEARNING PROJECTION PACKET",
        f"PROJECTION: {packet.projection}",
        f"TASK_ID: {packet.task_id}",
        f"POOL_ID: {packet.pool_id}",
        f"ACTING_WINNER_INDEX: {packet.acting_winner_index}",
        f"ACTING_WINNER_SHA256: {packet.acting_winner_sha256}",
        f"RESCUE_EVENT: {str(packet.rescue_event).lower()}",
        "The user-facing acting outcome is fixed by the acting winner above. The following slots are the only evidence exposed to the persistent updater.",
    ]
    slot_rows: list[dict[str, Any]] = []
    for slot_index, slot in enumerate(packet.slots):
        evidence = render_trajectory_evidence(
            Path(slot.trajectory_path), slot.trajectory_sha256, char_budget=slot_char_budget
        )
        sections.extend(
            [
                f"\n--- EVIDENCE SLOT {slot_index} ---",
                f"ROLE: {slot.role}",
                f"SOURCE_ROLLOUT_INDEX: {slot.rollout_index}",
                f"SOURCE_TRAJECTORY_SHA256: {slot.trajectory_sha256}",
                f"SOURCE_VERIFIER_SCORE: {slot.score}",
                evidence,
            ]
        )
        slot_rows.append(
            {
                "slot_index": slot_index,
                "role": slot.role,
                "rollout_index": slot.rollout_index,
                "trajectory_sha256": slot.trajectory_sha256,
                "score": slot.score,
                "rendered_chars": len(evidence),
                "rendered_sha256": sha_text(evidence),
            }
        )
    text = "\n".join(sections)
    metadata = {
        "packet_sha256": packet.packet_sha256,
        "projection": str(packet.projection),
        "pool_id": packet.pool_id,
        "task_id": packet.task_id,
        "acting_score": pool.acting_success,
        "rescue_event": packet.rescue_event,
        "rendered_packet_sha256": sha_text(text),
        "rendered_packet_chars": len(text),
        "slots": slot_rows,
    }
    return text, metadata


@dataclass(frozen=True)
class BlindedEvidenceUnit:
    """One pre-rendered learner-visible evidence unit for the V3.1 causal path.

    Projection/arm identity and source provenance remain available to the experiment
    receipt, but ``evidence_text`` is the only trajectory text placed in the
    first-party MindMemOS add-record ``messages`` field. ``source_score`` is the
    verifier score of that selected evidence trajectory, not the served acting
    winner score.
    """

    task_id: str
    pool_id: str
    acting_winner_sha256: str
    source_rollout_index: int
    source_trajectory_sha256: str
    source_score: float
    evidence_text: str
    evidence_sha256: str
    evidence_tokens: int

    def validate(self) -> None:
        if not self.task_id or not self.pool_id:
            raise ValueError("blinded evidence must bind task_id and pool_id")
        if self.source_rollout_index < 0:
            raise ValueError("source_rollout_index must be nonnegative")
        if sha_text(self.evidence_text) != self.evidence_sha256:
            raise ValueError("blinded evidence SHA mismatch")
        if self.evidence_tokens <= 0:
            raise ValueError("blinded evidence token count must be positive")


def build_blinded_add_record_payload(
    *,
    unit: BlindedEvidenceUnit,
    pool: SearchPool,
    project_id: str,
    task_completed_at: str,
    initial_skill_sha256: str,
    root_version_id: str,
    projection_label: str,
) -> dict[str, Any]:
    """Build the first-party add-record payload for V3.1 without treatment-label leakage.

    At pinned MindMemOS commit 9049182..., ``SkillEvolver`` constructs the LLM
    transcript from ``payload['messages']`` and obtains the scored-patch label from
    ``payload['score']``. The ``r17_*`` fields below are provenance-only and are
    intentionally absent from model-visible messages.
    """
    unit.validate()
    pool.validate()
    if unit.task_id != pool.task_id or unit.pool_id != pool.pool_id:
        raise ValueError("blinded evidence task/pool binding mismatch")
    if unit.acting_winner_sha256 != pool.winner.trajectory_sha256:
        raise ValueError("blinded evidence acting-winner provenance mismatch")
    return {
        "project_id": project_id,
        "task_completed_at": task_completed_at,
        "messages": [{"role": "user", "content": unit.evidence_text}],
        "score": float(unit.source_score),
        "task_id": pool.task_id,
        "skill_bindings": [
            {
                "name": "xlsx",
                "content_hash": initial_skill_sha256,
                "version_id": root_version_id,
                "usage": "injected",
            }
        ],
        "r17_projection": projection_label,
        "r17_rendered_packet_sha256": unit.evidence_sha256,
        "r17_pool_id": pool.pool_id,
        "r17_rescue_event": pool.rescue_event,
        "r17_acting_score": pool.acting_success,
        "r17_acting_winner_sha256": unit.acting_winner_sha256,
        "r17_source_rollout_index": unit.source_rollout_index,
        "r17_source_trajectory_sha256": unit.source_trajectory_sha256,
        "r17_selected_evidence_score": float(unit.source_score),
        "r17_evidence_tokens": int(unit.evidence_tokens),
    }


@dataclass(frozen=True)
class ProjectionUpdateResult:
    stream_id: str
    projection: str
    update_receipt_path: str
    update_receipt_sha256: str
    skill_post_path: str
    skill_post_sha256: str
    evolved: bool
    new_version_ids: tuple[str, ...]
    provider_calls: int
    provider_total_tokens: int


def _trace_uuid(stream_id: str, projection: str, task_id: str) -> str:
    return str(uuid.uuid5(_ID_NAMESPACE, f"{stream_id}|{projection}|{task_id}"))


async def run_projection_update(
    *,
    stream: StreamProjection,
    pools: Sequence[SearchPool],
    initial_skill_md: str,
    run_dir: Path,
    llm_adapter: Any,
    mindmemos_commit: str,
    contract_sha256: str,
    authorization_sha256: str,
    slot_char_budget: int = 6000,
    transcript_max_chars: int = 16000,
    blinded_evidence_units: Sequence[BlindedEvidenceUnit] | None = None,
) -> ProjectionUpdateResult:
    """Run one cloned MindMemOS SkillEvolver update from eight projected task packets.

    ``blinded_evidence_units`` activates the V3.1 causal-purity path. In that mode
    the first-party updater receives only the pre-rendered arm-blinded evidence
    text plus the selected evidence trajectory's verifier score. Acting winner,
    projection label, rollout index and SHA provenance remain database/receipt
    metadata and are not placed in the model-visible transcript.
    """

    if len(stream.packets) != 8 or len(pools) != 8:
        raise ValueError("one E2-R17 update unit must contain exactly eight task pools")
    if [pool.pool_id for pool in pools] != [pool.pool_id for pool in stream.pools]:
        raise ValueError("stream pools differ from supplied exact pools")
    run_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = run_dir / "update_receipt.json"
    skill_path = run_dir / "skill_post" / "SKILL.md"
    if receipt_path.exists() and skill_path.exists():
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
        if sha_file(skill_path) != payload.get("skill_post_sha256"):
            raise RuntimeError("existing updater receipt failed skill content-address check")
        return ProjectionUpdateResult(
            stream_id=stream.stream_id,
            projection=str(stream.projection),
            update_receipt_path=str(receipt_path.resolve()),
            update_receipt_sha256=sha_file(receipt_path),
            skill_post_path=str(skill_path.resolve()),
            skill_post_sha256=sha_file(skill_path),
            evolved=bool(payload.get("evolved")),
            new_version_ids=tuple(payload.get("new_version_ids") or []),
            provider_calls=len(payload.get("adapter_receipts") or []),
            provider_total_tokens=sum(int(row.get("total_tokens") or 0) for row in payload.get("adapter_receipts") or []),
        )

    # Imports remain inside the function so the caller can bind the exact
    # MindMemOS source tree before loading this module.
    from mindmemos.components.skill import deserialize_bundle, serialize_bundle
    from mindmemos.config import QdrantConfig, SkillEvolutionConfig
    from mindmemos.infra.db import SkillVersionRepository
    from mindmemos.infra.db.models import AddRecordPoint
    from mindmemos.infra.db.qdrant import QdrantStore
    from mindmemos.pipelines.skill import SkillVersionStore
    from mindmemos.pipelines.skill import evolution as evolution_module
    from mindmemos.pipelines.skill.evolution import SkillEvolver
    from qdrant_client import AsyncQdrantClient

    packet_rows: list[dict[str, Any]] = []
    rendered_packets: list[tuple[str, dict[str, Any]]] = []
    blinded_rows: list[BlindedEvidenceUnit] | None = None
    if blinded_evidence_units is not None:
        blinded_rows = list(blinded_evidence_units)
        if len(blinded_rows) != len(pools):
            raise ValueError("blinded evidence cardinality must match the eight exact pools")
        for pool, unit in zip(pools, blinded_rows):
            unit.validate()
            if unit.task_id != pool.task_id or unit.pool_id != pool.pool_id:
                raise ValueError("blinded evidence task/pool binding mismatch")
            if unit.acting_winner_sha256 != pool.winner.trajectory_sha256:
                raise ValueError("blinded evidence acting-winner provenance mismatch")
            if len(f"[user] {unit.evidence_text}") > transcript_max_chars:
                raise ValueError("blinded evidence would be silently truncated by first-party transcript renderer")
            metadata = {
                "packet_sha256": sha_text(unit.evidence_text),
                "projection": str(stream.projection),
                "pool_id": unit.pool_id,
                "task_id": unit.task_id,
                "acting_score": pool.acting_success,
                "acting_winner_sha256": unit.acting_winner_sha256,
                "source_rollout_index": unit.source_rollout_index,
                "source_trajectory_sha256": unit.source_trajectory_sha256,
                "source_score": unit.source_score,
                "rendered_packet_sha256": unit.evidence_sha256,
                "rendered_packet_chars": len(unit.evidence_text),
                "rendered_packet_tokens": unit.evidence_tokens,
                "arm_metadata_visible": False,
                "score_semantics": "selected_evidence_trajectory",
            }
            rendered_packets.append((unit.evidence_text, metadata))
            packet_rows.append(metadata)
    else:
        for pool, packet in zip(pools, stream.packets):
            text, metadata = render_projection_packet(pool, packet, slot_char_budget=slot_char_budget)
            rendered_packets.append((text, metadata))
            packet_rows.append(metadata)

    client = AsyncQdrantClient(":memory:")
    qdrant_cfg = QdrantConfig(
        url="http://unused",
        add_record_collection="r17_add_record",
        skill_version_collection="r17_skill_version",
        skill_blob_collection="r17_skill_blob",
        skill_trace_pending_collection="r17_skill_trace_pending",
        skill_trace_summary_collection="r17_skill_trace_summary",
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
    project_id = f"e2-r17-{stream.stream_id}-{stream.projection}"
    root = await store.register(
        project_id=project_id,
        name="xlsx",
        content=serialize_bundle({"SKILL.md": initial_skill_md}),
    )
    base_time = datetime(2026, 8, 28, tzinfo=UTC)
    for index, ((packet_text, packet_meta), pool) in enumerate(zip(rendered_packets, pools)):
        selected_score = (
            float(blinded_rows[index].source_score)
            if blinded_rows is not None
            else float(pool.acting_success)
        )
        if blinded_rows is not None:
            payload = build_blinded_add_record_payload(
                unit=blinded_rows[index],
                pool=pool,
                project_id=project_id,
                task_completed_at=(base_time + timedelta(minutes=index)).isoformat(),
                initial_skill_sha256=stream.initial_skill_sha256,
                root_version_id=root.version_id,
                projection_label=str(stream.projection),
            )
            if float(payload["score"]) != selected_score:
                raise AssertionError("V3.1 selected-evidence score serialization drift")
        else:
            payload = {
                "project_id": project_id,
                "task_completed_at": (base_time + timedelta(minutes=index)).isoformat(),
                "messages": [{"role": "user", "content": packet_text}],
                "score": selected_score,
                "task_id": pool.task_id,
                "skill_bindings": [
                    {
                        "name": "xlsx",
                        "content_hash": stream.initial_skill_sha256,
                        "version_id": root.version_id,
                        "usage": "injected",
                    }
                ],
                "r17_projection": str(stream.projection),
                "r17_projection_packet_sha256": packet_meta["packet_sha256"],
                "r17_rendered_packet_sha256": packet_meta["rendered_packet_sha256"],
                "r17_pool_id": pool.pool_id,
                "r17_rescue_event": pool.rescue_event,
            }
        await qdrant.upsert_add_record(
            AddRecordPoint(
                add_record_id=_trace_uuid(stream.stream_id, str(stream.projection), pool.task_id),
                payload=payload,
            )
        )

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
        summaries = await evolver._existing_summaries(project_id, root.cloud_skill_id)
    finally:
        evolution_module.get_config = original_get_config

    try:
        if not update.evolved or not update.new_version_id:
            raise RuntimeError(
                f"first-party SkillEvolver did not mint a version: pending={update.pending_count}; "
                f"summarized={update.summarized_count}"
            )
        if len(update.new_version_ids) != 1 or update.consumed_count != 8:
            raise RuntimeError("R17 frozen updater must mint exactly one version from eight task packets")
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
                "summary": item.summary,
                "summary_sha256": sha_text(item.summary),
                "consumed_version_id": item.consumed_version_id,
            }
            for item in sorted(summaries.values(), key=lambda row: (str(row.task_id), row.summary_id))
        ]
        payload = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-cloned-state-mindmemos-update",
            "created_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
            "status": "COMPLETED",
            "stream_id": stream.stream_id,
            "stream_sha256": stream.stream_sha256,
            "projection": str(stream.projection),
            "initial_skill_sha256": stream.initial_skill_sha256,
            "skill_post_path": str(skill_path.resolve()),
            "skill_post_sha256": sha_file(skill_path),
            "mindmemos_commit": mindmemos_commit,
            "first_party_updater": "mindmemos.pipelines.skill.evolution.SkillEvolver",
            "updater_config": asdict(frozen_cfg),
            "project_id": project_id,
            "root_version_id": root.version_id,
            "cloud_skill_id": root.cloud_skill_id,
            "evolved": update.evolved,
            "new_version_id": update.new_version_id,
            "new_version_ids": update.new_version_ids,
            "summarized_count": update.summarized_count,
            "consumed_count": update.consumed_count,
            "pending_count": update.pending_count,
            "packets": packet_rows,
            "summaries": summary_rows,
            "adapter_receipts": adapter_receipts,
            "adapter_receipt_bundle_sha256": llm_adapter.receipt_bundle_sha256,
            "contract_sha256": contract_sha256,
            "authorization_sha256": authorization_sha256,
            "provider_retry_limit": 0,
            "hidden_provider_retry_used": False,
            "causal_purity_mode": "arm_blinded_selected_evidence" if blinded_rows is not None else "legacy_projection_packet",
            "updater_visible_score_semantics": "selected_evidence_trajectory" if blinded_rows is not None else "served_acting_outcome_legacy",
            "arm_metadata_visible_in_transcript": False if blinded_rows is not None else True,
            "private_credentials_included": False,
            "raw_response_ids_included": False,
        }
        atomic_json(receipt_path, payload)
    finally:
        await client.close()

    return ProjectionUpdateResult(
        stream_id=stream.stream_id,
        projection=str(stream.projection),
        update_receipt_path=str(receipt_path.resolve()),
        update_receipt_sha256=sha_file(receipt_path),
        skill_post_path=str(skill_path.resolve()),
        skill_post_sha256=sha_file(skill_path),
        evolved=True,
        new_version_ids=tuple(update.new_version_ids),
        provider_calls=len(adapter_receipts),
        provider_total_tokens=sum(int(row.get("total_tokens") or 0) for row in adapter_receipts),
    )


__all__ = [
    "BlindedEvidenceUnit",
    "build_blinded_add_record_payload",
    "ProjectionUpdateResult",
    "render_projection_packet",
    "render_trajectory_evidence",
    "run_projection_update",
]


===== BOUND ARTIFACT: updater_wrapper_v31_tests | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/test_e2_r17_mindmemos_updater_v31.py =====
from __future__ import annotations

import hashlib
import unittest

from research_pipeline.e2_r17_mindmemos_updater import (
    BlindedEvidenceUnit,
    build_blinded_add_record_payload,
    sha_text,
)
from research_pipeline.e2_r17_search_projection_runner import SearchPool, TrajectoryRef


def digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def trajectory(task: str, index: int, score: int) -> TrajectoryRef:
    return TrajectoryRef(
        task_id=task,
        rollout_index=index,
        score=float(score),
        trajectory_path=f"/frozen/{task}/rollout_{index}.json",
        trajectory_sha256=digest(f"trajectory:{task}:{index}:{score}"),
        input_sha256=digest(f"input:{task}"),
        prompt_sha256=digest(f"prompt:{task}"),
        skill_pre_sha256=digest("skill"),
        verifier_sha256=digest("verifier-v1"),
        requested_model="deepseek-v4-pro",
        resolved_model="deepseek-v4-pro-ga-260813",
        provider_call_id_sha256=digest(f"call:{task}:{index}"),
        evidence_tokens=100 + index,
        failure_code=None if score else "controlled_failure",
    )


def pool(task: str, scores: list[int]) -> SearchPool:
    return SearchPool.freeze([trajectory(task, index, score) for index, score in enumerate(scores)])


def unit_for(p: SearchPool, source_index: int, text: str) -> BlindedEvidenceUnit:
    source = p.trajectories[source_index]
    return BlindedEvidenceUnit(
        task_id=p.task_id,
        pool_id=p.pool_id,
        acting_winner_sha256=p.winner.trajectory_sha256,
        source_rollout_index=source.rollout_index,
        source_trajectory_sha256=source.trajectory_sha256,
        source_score=source.score,
        evidence_text=text,
        evidence_sha256=sha_text(text),
        evidence_tokens=321,
    )


class MindMemOSUpdaterV31Test(unittest.TestCase):
    def test_selected_evidence_score_is_separate_from_acting_score(self) -> None:
        p = pool("mixed", [1, 0, 1, 0])
        failure = unit_for(p, 1, "E2-R17 SELECTED EXPERIENCE\nfailed formula evidence")
        payload = build_blinded_add_record_payload(
            unit=failure,
            pool=p,
            project_id="internal-project-id-containing-mrw",
            task_completed_at="2026-08-28T00:00:00+00:00",
            initial_skill_sha256=digest("skill"),
            root_version_id="root-version",
            projection_label="mixed_rejected_witness",
        )
        self.assertEqual(payload["score"], 0.0)
        self.assertEqual(payload["r17_selected_evidence_score"], 0.0)
        self.assertEqual(payload["r17_acting_score"], 1.0)
        self.assertEqual(payload["messages"], [{"role": "user", "content": failure.evidence_text}])

    def test_projection_and_rollout_metadata_are_not_in_model_visible_messages(self) -> None:
        p = pool("mixed", [1, 0, 1, 0])
        failure = unit_for(p, 1, "E2-R17 SELECTED EXPERIENCE\nfailed formula evidence")
        payload = build_blinded_add_record_payload(
            unit=failure,
            pool=p,
            project_id="internal-project-id-containing-mrw",
            task_completed_at="2026-08-28T00:00:00+00:00",
            initial_skill_sha256=digest("skill"),
            root_version_id="root-version",
            projection_label="mixed_rejected_witness",
        )
        visible = payload["messages"][0]["content"]
        for forbidden in [
            "mixed_rejected_witness",
            "SOURCE_ROLLOUT_INDEX",
            "ROLE:",
            failure.source_trajectory_sha256,
            p.pool_id,
        ]:
            self.assertNotIn(forbidden, visible)
        self.assertEqual(payload["r17_projection"], "mixed_rejected_witness")
        self.assertEqual(payload["r17_source_rollout_index"], 1)

    def test_winner_and_failure_can_share_acting_provenance_but_not_learning_score(self) -> None:
        p = pool("mixed", [1, 0, 1, 0])
        winner = unit_for(p, 0, "E2-R17 SELECTED EXPERIENCE\nwinner evidence")
        failure = unit_for(p, 1, "E2-R17 SELECTED EXPERIENCE\nfailure evidence")
        common = dict(
            pool=p,
            project_id="internal",
            task_completed_at="2026-08-28T00:00:00+00:00",
            initial_skill_sha256=digest("skill"),
            root_version_id="root-version",
        )
        win_payload = build_blinded_add_record_payload(
            unit=winner, projection_label="winner_only", **common
        )
        mrw_payload = build_blinded_add_record_payload(
            unit=failure, projection_label="mixed_rejected_witness", **common
        )
        self.assertEqual(win_payload["r17_acting_winner_sha256"], mrw_payload["r17_acting_winner_sha256"])
        self.assertEqual(win_payload["r17_acting_score"], mrw_payload["r17_acting_score"])
        self.assertEqual(win_payload["score"], 1.0)
        self.assertEqual(mrw_payload["score"], 0.0)

    def test_sha_drift_is_rejected(self) -> None:
        p = pool("mixed", [1, 0])
        broken = BlindedEvidenceUnit(
            task_id=p.task_id,
            pool_id=p.pool_id,
            acting_winner_sha256=p.winner.trajectory_sha256,
            source_rollout_index=1,
            source_trajectory_sha256=p.trajectories[1].trajectory_sha256,
            source_score=0.0,
            evidence_text="failure evidence",
            evidence_sha256=digest("different text"),
            evidence_tokens=10,
        )
        with self.assertRaises(ValueError):
            broken.validate()


if __name__ == "__main__":
    unittest.main()


===== BOUND ARTIFACT: search_projection_runner | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/e2_r17_search_projection_runner.py =====
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable, Sequence


def canonical_sha256(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class ProjectionName(StrEnum):
    WINNER_ONLY = "winner_only"
    PRECOMMITTED_ALWAYS = "precommitted_always"
    REJECTED_WITNESS = "rejected_witness"
    MIXED_REJECTED_WITNESS = "mixed_rejected_witness"
    DUPLICATED_WINNER = "duplicated_winner"
    WINNER_RANDOM_NONWINNER = "winner_random_nonwinner"
    SKILLCAT_STYLE_CONTRAST = "skillcat_style_contrast"


@dataclass(frozen=True)
class TrajectoryRef:
    task_id: str
    rollout_index: int
    score: float
    trajectory_path: str
    trajectory_sha256: str
    input_sha256: str
    prompt_sha256: str
    skill_pre_sha256: str
    verifier_sha256: str
    requested_model: str
    resolved_model: str
    provider_call_id_sha256: str
    evidence_tokens: int
    technical_status: str = "COMPLETED"
    failure_code: str | None = None

    def validate(self) -> None:
        if self.rollout_index < 0:
            raise ValueError("rollout_index must be non-negative")
        if self.score not in (0.0, 1.0):
            raise ValueError("R4 primary verifier score must be binary")
        if self.evidence_tokens < 0:
            raise ValueError("evidence_tokens must be non-negative")
        if self.technical_status != "COMPLETED":
            raise ValueError("technical-incomplete trajectories cannot enter a frozen pool")
        for name in (
            "trajectory_sha256",
            "input_sha256",
            "prompt_sha256",
            "skill_pre_sha256",
            "verifier_sha256",
            "provider_call_id_sha256",
        ):
            value = getattr(self, name)
            if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise ValueError(f"{name} must be a lowercase SHA-256 hex digest")
        if not self.resolved_model:
            raise ValueError("resolved_model is required")


@dataclass(frozen=True)
class SearchPool:
    pool_id: str
    task_id: str
    k: int
    trajectories: tuple[TrajectoryRef, ...]
    search_topology: str = "parallel_best_of_k"

    def validate(self) -> None:
        if self.k < 1 or len(self.trajectories) != self.k:
            raise ValueError("pool cardinality must equal k")
        if self.search_topology != "parallel_best_of_k":
            raise ValueError("R4 primary pool topology is frozen to parallel_best_of_k")
        for trajectory in self.trajectories:
            trajectory.validate()
        indices = [trajectory.rollout_index for trajectory in self.trajectories]
        if indices != list(range(self.k)):
            raise ValueError("trajectory indices must be ordered and equal 0..k-1")
        invariant_fields = (
            "task_id",
            "input_sha256",
            "prompt_sha256",
            "skill_pre_sha256",
            "verifier_sha256",
            "requested_model",
            "resolved_model",
        )
        for field in invariant_fields:
            values = {getattr(trajectory, field) for trajectory in self.trajectories}
            if len(values) != 1:
                raise ValueError(f"pool invariant violated: {field}")
        if self.trajectories[0].task_id != self.task_id:
            raise ValueError("pool task_id does not match trajectories")
        expected_id = canonical_sha256(
            {
                "task_id": self.task_id,
                "k": self.k,
                "topology": self.search_topology,
                "trajectory_sha256": [trajectory.trajectory_sha256 for trajectory in self.trajectories],
            }
        )
        if self.pool_id != expected_id:
            raise ValueError("pool_id is not content-addressed to the exact pool")

    @classmethod
    def freeze(cls, trajectories: Sequence[TrajectoryRef]) -> "SearchPool":
        if not trajectories:
            raise ValueError("cannot freeze an empty pool")
        ordered = tuple(sorted(trajectories, key=lambda row: row.rollout_index))
        task_id = ordered[0].task_id
        k = len(ordered)
        pool_id = canonical_sha256(
            {
                "task_id": task_id,
                "k": k,
                "topology": "parallel_best_of_k",
                "trajectory_sha256": [trajectory.trajectory_sha256 for trajectory in ordered],
            }
        )
        pool = cls(pool_id=pool_id, task_id=task_id, k=k, trajectories=ordered)
        pool.validate()
        return pool

    @property
    def precommitted(self) -> TrajectoryRef:
        return self.trajectories[0]

    @property
    def winner(self) -> TrajectoryRef:
        # Frozen selector: maximum binary verifier score, then lowest rollout index.
        return min(self.trajectories, key=lambda row: (-row.score, row.rollout_index))

    @property
    def acting_success(self) -> float:
        return self.winner.score

    @property
    def precommitted_success(self) -> float:
        return self.precommitted.score

    @property
    def rescue_event(self) -> bool:
        return self.precommitted.score == 0.0 and self.winner.score == 1.0

    @property
    def rescue_censoring_mass(self) -> float:
        return float(self.rescue_event)

    @property
    def mixed_pool(self) -> bool:
        scores = {trajectory.score for trajectory in self.trajectories}
        return scores == {0.0, 1.0}

    @property
    def first_failed_nonwinner(self) -> TrajectoryRef:
        if not self.mixed_pool:
            raise ValueError("a failed non-winner exists only on mixed pools")
        failures = [
            trajectory
            for trajectory in self.trajectories
            if trajectory.score == 0.0 and trajectory.rollout_index != self.winner.rollout_index
        ]
        if not failures:
            raise ValueError("mixed pool does not contain a failed non-winner")
        return min(failures, key=lambda row: row.rollout_index)


@dataclass(frozen=True)
class EvidenceSlot:
    role: str
    rollout_index: int
    trajectory_sha256: str
    score: float
    trajectory_path: str
    evidence_tokens: int


@dataclass(frozen=True)
class ProjectionPacket:
    projection: ProjectionName
    pool_id: str
    task_id: str
    acting_winner_index: int
    acting_winner_sha256: str
    rescue_event: bool
    slots: tuple[EvidenceSlot, ...]
    rule_version: str
    randomization_salt: str | None = None

    @property
    def packet_sha256(self) -> str:
        return canonical_sha256(asdict(self))

    @property
    def selected_indices(self) -> tuple[int, ...]:
        return tuple(slot.rollout_index for slot in self.slots)

    @property
    def total_evidence_tokens(self) -> int:
        return sum(slot.evidence_tokens for slot in self.slots)


def _slot(role: str, trajectory: TrajectoryRef) -> EvidenceSlot:
    return EvidenceSlot(
        role=role,
        rollout_index=trajectory.rollout_index,
        trajectory_sha256=trajectory.trajectory_sha256,
        score=trajectory.score,
        trajectory_path=trajectory.trajectory_path,
        evidence_tokens=trajectory.evidence_tokens,
    )


def _random_nonwinner(pool: SearchPool, salt: str) -> TrajectoryRef:
    candidates = [trajectory for trajectory in pool.trajectories if trajectory.rollout_index != pool.winner.rollout_index]
    if not candidates:
        return pool.winner
    digest = hashlib.sha256(f"{salt}|{pool.pool_id}".encode("utf-8")).hexdigest()
    return candidates[int(digest[:16], 16) % len(candidates)]


def project(
    pool: SearchPool,
    projection: ProjectionName,
    *,
    randomization_salt: str = "e2-r17-r4-random-nonwinner-v1",
) -> ProjectionPacket:
    pool.validate()
    winner = pool.winner
    precommitted = pool.precommitted
    if projection is ProjectionName.WINNER_ONLY:
        slots = (_slot("served_winner", winner),)
        salt = None
    elif projection is ProjectionName.PRECOMMITTED_ALWAYS:
        slots = (_slot("precommitted_rollout_0", precommitted),)
        salt = None
    elif projection is ProjectionName.REJECTED_WITNESS:
        selected = precommitted if pool.rescue_event else winner
        role = "precommitted_rejected_failure" if pool.rescue_event else "served_winner_outside_rescue"
        slots = (_slot(role, selected),)
        salt = None
    elif projection is ProjectionName.MIXED_REJECTED_WITNESS:
        selected = pool.first_failed_nonwinner if pool.mixed_pool else winner
        role = "first_failed_nonwinner" if pool.mixed_pool else "served_winner_outside_mixed_pool"
        slots = (_slot(role, selected),)
        salt = None
    elif projection is ProjectionName.DUPLICATED_WINNER:
        slots = (_slot("served_winner_slot_1", winner), _slot("served_winner_slot_2", winner))
        salt = None
    elif projection is ProjectionName.WINNER_RANDOM_NONWINNER:
        random_nonwinner = _random_nonwinner(pool, randomization_salt)
        slots = (_slot("served_winner", winner), _slot("hash_selected_nonwinner", random_nonwinner))
        salt = randomization_salt
    elif projection is ProjectionName.SKILLCAT_STYLE_CONTRAST:
        # This freezes only the source trajectory pair. Any generated contrastive
        # summary is a downstream updater artifact and must retain both source SHAs.
        contrast = precommitted if pool.rescue_event else winner
        second_role = "precommitted_rejected_failure" if pool.rescue_event else "duplicated_winner_outside_rescue"
        slots = (_slot("served_winner", winner), _slot(second_role, contrast))
        salt = None
    else:  # pragma: no cover - StrEnum exhaustiveness guard
        raise ValueError(f"unsupported projection: {projection}")
    packet = ProjectionPacket(
        projection=projection,
        pool_id=pool.pool_id,
        task_id=pool.task_id,
        acting_winner_index=winner.rollout_index,
        acting_winner_sha256=winner.trajectory_sha256,
        rescue_event=pool.rescue_event,
        slots=slots,
        rule_version="E2-R17-R4-PROJECTION-V1",
        randomization_salt=salt,
    )
    validate_packet(pool, packet)
    return packet


def validate_packet(pool: SearchPool, packet: ProjectionPacket) -> None:
    pool.validate()
    if packet.pool_id != pool.pool_id or packet.task_id != pool.task_id:
        raise ValueError("projection packet is not bound to the exact pool")
    if packet.acting_winner_index != pool.winner.rollout_index:
        raise ValueError("acting winner changed across learning projections")
    if packet.acting_winner_sha256 != pool.winner.trajectory_sha256:
        raise ValueError("acting winner SHA changed across learning projections")
    if packet.rescue_event != pool.rescue_event:
        raise ValueError("rescue-event flag mismatch")
    by_index = {trajectory.rollout_index: trajectory for trajectory in pool.trajectories}
    for slot in packet.slots:
        source = by_index.get(slot.rollout_index)
        if source is None or source.trajectory_sha256 != slot.trajectory_sha256:
            raise ValueError("projection introduced evidence outside the frozen pool")
        if source.score != slot.score or source.trajectory_path != slot.trajectory_path:
            raise ValueError("projection slot altered source trajectory metadata")
    if packet.projection is ProjectionName.REJECTED_WITNESS:
        expected = pool.precommitted if pool.rescue_event else pool.winner
        if packet.selected_indices != (expected.rollout_index,):
            raise ValueError("Rejected-Witness violates its event-gated precommitment")
        if pool.rescue_event and not (packet.slots[0].score == 0.0 and pool.winner.score == 1.0):
            raise ValueError("Rejected-Witness must expose a rejected failure only on rescue events")
    if packet.projection is ProjectionName.MIXED_REJECTED_WITNESS:
        expected = pool.first_failed_nonwinner if pool.mixed_pool else pool.winner
        if packet.selected_indices != (expected.rollout_index,):
            raise ValueError("Mixed-Rejected-Witness violates its deterministic mixed-pool rule")
        if pool.mixed_pool and packet.slots[0].score != 0.0:
            raise ValueError("Mixed-Rejected-Witness must expose a failed non-winner on mixed pools")
    if packet.projection is ProjectionName.DUPLICATED_WINNER:
        expected = (pool.winner.rollout_index, pool.winner.rollout_index)
        if packet.selected_indices != expected:
            raise ValueError("duplicated-winner packet is not an exact duplicate")


def validate_primary_cloned_pair(pool: SearchPool, winner_packet: ProjectionPacket, witness_packet: ProjectionPacket) -> None:
    validate_packet(pool, winner_packet)
    validate_packet(pool, witness_packet)
    if winner_packet.projection is not ProjectionName.WINNER_ONLY:
        raise ValueError("first packet must be winner-only")
    if witness_packet.projection is not ProjectionName.REJECTED_WITNESS:
        raise ValueError("second packet must be Rejected-Witness")
    if winner_packet.pool_id != witness_packet.pool_id:
        raise ValueError("cloned pair does not use the exact same pool")
    if winner_packet.acting_winner_sha256 != witness_packet.acting_winner_sha256:
        raise ValueError("acting winner differs between cloned arms")
    if not pool.rescue_event and winner_packet.selected_indices != witness_packet.selected_indices:
        raise ValueError("g_RW must equal g_WIN outside the rescue event")
    if pool.rescue_event and winner_packet.selected_indices == witness_packet.selected_indices:
        raise ValueError("g_RW must differ from g_WIN on the rescue event")


@dataclass(frozen=True)
class StreamProjection:
    stream_id: str
    initial_skill_sha256: str
    pools: tuple[SearchPool, ...]
    packets: tuple[ProjectionPacket, ...]
    projection: ProjectionName

    @property
    def stream_sha256(self) -> str:
        return canonical_sha256(
            {
                "stream_id": self.stream_id,
                "initial_skill_sha256": self.initial_skill_sha256,
                "pool_ids": [pool.pool_id for pool in self.pools],
                "packet_sha256": [packet.packet_sha256 for packet in self.packets],
                "projection": self.projection,
            }
        )


def project_stream(
    *,
    stream_id: str,
    initial_skill_sha256: str,
    pools: Sequence[SearchPool],
    projection: ProjectionName,
) -> StreamProjection:
    if len(initial_skill_sha256) != 64:
        raise ValueError("initial skill SHA-256 is required")
    if len(pools) != 8:
        raise ValueError("MindMemOS R4 updater batch is frozen to exactly 8 task pools")
    if len({pool.task_id for pool in pools}) != 8:
        raise ValueError("one evolution stream must contain eight distinct tasks")
    if any(pool.trajectories[0].skill_pre_sha256 != initial_skill_sha256 for pool in pools):
        raise ValueError("all pools must be generated from the exact initial skill state")
    packets = tuple(project(pool, projection) for pool in pools)
    return StreamProjection(
        stream_id=stream_id,
        initial_skill_sha256=initial_skill_sha256,
        pools=tuple(pools),
        packets=packets,
        projection=projection,
    )


def validate_mixed_cloned_pair(pool: SearchPool, winner_packet: ProjectionPacket, witness_packet: ProjectionPacket) -> None:
    validate_packet(pool, winner_packet)
    validate_packet(pool, witness_packet)
    if winner_packet.projection is not ProjectionName.WINNER_ONLY:
        raise ValueError("first packet must be winner-only")
    if witness_packet.projection is not ProjectionName.MIXED_REJECTED_WITNESS:
        raise ValueError("second packet must be Mixed-Rejected-Witness")
    if winner_packet.pool_id != witness_packet.pool_id:
        raise ValueError("cloned pair does not use the exact same pool")
    if winner_packet.acting_winner_sha256 != witness_packet.acting_winner_sha256:
        raise ValueError("acting winner differs between cloned arms")
    if not pool.mixed_pool and winner_packet.selected_indices != witness_packet.selected_indices:
        raise ValueError("g_MRW must equal g_WIN outside the mixed-pool event")
    if pool.mixed_pool and winner_packet.selected_indices == witness_packet.selected_indices:
        raise ValueError("g_MRW must differ from g_WIN on the mixed-pool event")


def validate_cloned_streams(winner: StreamProjection, witness: StreamProjection) -> None:
    if winner.stream_id != witness.stream_id or winner.initial_skill_sha256 != witness.initial_skill_sha256:
        raise ValueError("cloned streams are not cloned from the same unit")
    if winner.projection is not ProjectionName.WINNER_ONLY:
        raise ValueError("winner stream projection mismatch")
    if witness.projection is not ProjectionName.REJECTED_WITNESS:
        raise ValueError("witness stream projection mismatch")
    if [pool.pool_id for pool in winner.pools] != [pool.pool_id for pool in witness.pools]:
        raise ValueError("cloned streams do not share exact pool IDs")
    for pool, win_packet, rw_packet in zip(winner.pools, winner.packets, witness.packets):
        validate_primary_cloned_pair(pool, win_packet, rw_packet)


def validate_mixed_cloned_streams(winner: StreamProjection, witness: StreamProjection) -> None:
    if winner.stream_id != witness.stream_id or winner.initial_skill_sha256 != witness.initial_skill_sha256:
        raise ValueError("cloned streams are not cloned from the same unit")
    if winner.projection is not ProjectionName.WINNER_ONLY:
        raise ValueError("winner stream projection mismatch")
    if witness.projection is not ProjectionName.MIXED_REJECTED_WITNESS:
        raise ValueError("mixed-witness stream projection mismatch")
    if [pool.pool_id for pool in winner.pools] != [pool.pool_id for pool in witness.pools]:
        raise ValueError("cloned streams do not share exact pool IDs")
    for pool, win_packet, rw_packet in zip(winner.pools, winner.packets, witness.packets):
        validate_mixed_cloned_pair(pool, win_packet, rw_packet)


def write_stream_receipt(path: Path, stream: StreamProjection) -> None:
    payload = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-search-projection-stream-receipt",
        "stream_id": stream.stream_id,
        "stream_sha256": stream.stream_sha256,
        "initial_skill_sha256": stream.initial_skill_sha256,
        "projection": stream.projection,
        "pool_ids": [pool.pool_id for pool in stream.pools],
        "packets": [asdict(packet) | {"packet_sha256": packet.packet_sha256} for packet in stream.packets],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def pools_from_jsonl(path: Path) -> tuple[SearchPool, ...]:
    pools: list[SearchPool] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        trajectories = tuple(TrajectoryRef(**row) for row in payload["trajectories"])
        pool = SearchPool(
            pool_id=payload["pool_id"],
            task_id=payload["task_id"],
            k=payload["k"],
            trajectories=trajectories,
            search_topology=payload.get("search_topology", "parallel_best_of_k"),
        )
        pool.validate()
        pools.append(pool)
    return tuple(pools)


def append_pool_jsonl(path: Path, pool: SearchPool) -> None:
    pool.validate()
    payload = {
        "pool_id": pool.pool_id,
        "task_id": pool.task_id,
        "k": pool.k,
        "search_topology": pool.search_topology,
        "trajectories": [asdict(row) for row in pool.trajectories],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


===== BOUND ARTIFACT: search_projection_theory | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/research_pipeline/e2_r17_search_projection_theory.py =====
from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Iterable, Mapping, Sequence


BinaryOutcome = tuple[int, ...]
ScoreOutcome = tuple[float, ...]


@dataclass(frozen=True)
class BinaryProjectionStats:
    acting_k: float
    acting_precommitted: float
    visible_failure_precommitted: float
    visible_failure_winner: float
    rescue_censoring_mass: float

    @property
    def acting_gain(self) -> float:
        return self.acting_k - self.acting_precommitted

    @property
    def visibility_gap(self) -> float:
        return self.visible_failure_precommitted - self.visible_failure_winner


@dataclass(frozen=True)
class ContinuousProjectionStats:
    acting_gain: float
    integrated_threshold_censoring: float


@dataclass(frozen=True)
class BinaryEvidenceStats:
    """Evidence quantities induced by best-of-K winner selection.

    Binary outcomes use 1=success and 0=failure. The acting selector serves a
    successful trajectory whenever one exists. `winner_failure_visibility`
    measures the probability that winner-only learning observes failure.
    `pool_failure_availability` measures whether the generated pool contains any
    failed trajectory, and `mixed_pool_mass` measures whether the same pool
    contains both success and failure evidence.
    """

    acting_success: float
    winner_failure_visibility: float
    pool_failure_availability: float
    mixed_pool_mass: float


def _validate_distribution(items: Iterable[tuple[Sequence[float], float]]) -> list[tuple[tuple[float, ...], float]]:
    rows = [(tuple(float(v) for v in outcome), float(probability)) for outcome, probability in items]
    if not rows:
        raise ValueError("distribution must be non-empty")
    width = len(rows[0][0])
    if width < 1 or any(len(outcome) != width for outcome, _ in rows):
        raise ValueError("all outcomes must have the same positive width")
    if any(probability < 0 for _, probability in rows):
        raise ValueError("probabilities must be non-negative")
    total = sum(probability for _, probability in rows)
    if not isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-10):
        raise ValueError(f"probabilities must sum to one, observed {total}")
    return rows


def binary_projection_stats(joint: Mapping[BinaryOutcome, float]) -> BinaryProjectionStats:
    """Compute the exact rescue-censoring quantities for an arbitrary joint law.

    Rollout 0 is the precommitted rollout. No independence or exchangeability is
    assumed. The acting selector succeeds iff any rollout succeeds.
    """
    rows = _validate_distribution(joint.items())
    if any(any(value not in (0.0, 1.0) for value in outcome) for outcome, _ in rows):
        raise ValueError("binary outcomes must contain only zero or one")

    acting_k = sum(max(outcome) * probability for outcome, probability in rows)
    acting_pre = sum(outcome[0] * probability for outcome, probability in rows)
    visible_pre = sum((outcome[0] == 0.0) * probability for outcome, probability in rows)
    visible_win = sum((max(outcome) == 0.0) * probability for outcome, probability in rows)
    rescue = sum(
        (outcome[0] == 0.0 and max(outcome) == 1.0) * probability
        for outcome, probability in rows
    )
    return BinaryProjectionStats(
        acting_k=acting_k,
        acting_precommitted=acting_pre,
        visible_failure_precommitted=visible_pre,
        visible_failure_winner=visible_win,
        rescue_censoring_mass=rescue,
    )


def binary_evidence_stats(joint: Mapping[BinaryOutcome, float]) -> BinaryEvidenceStats:
    """Compute winner-visible and pool-available failure evidence exactly.

    No independence or exchangeability is assumed. For nested pools, the
    pointwise events imply that acting success and mixed-pool support are
    non-decreasing with K, while winner-visible failure is non-increasing.
    """
    rows = _validate_distribution(joint.items())
    if any(any(value not in (0.0, 1.0) for value in outcome) for outcome, _ in rows):
        raise ValueError("binary outcomes must contain only zero or one")

    acting = sum((max(outcome) == 1.0) * probability for outcome, probability in rows)
    winner_failure = sum((max(outcome) == 0.0) * probability for outcome, probability in rows)
    pool_failure = sum((min(outcome) == 0.0) * probability for outcome, probability in rows)
    mixed = sum(
        (min(outcome) == 0.0 and max(outcome) == 1.0) * probability
        for outcome, probability in rows
    )
    return BinaryEvidenceStats(
        acting_success=acting,
        winner_failure_visibility=winner_failure,
        pool_failure_availability=pool_failure,
        mixed_pool_mass=mixed,
    )


def gamma_iid(p: float, k: int) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return (1.0 - p) - (1.0 - p) ** k


def winner_failure_iid(p: float, k: int) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return (1.0 - p) ** k


def pool_failure_iid(p: float, k: int) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return 1.0 - p**k


def mixed_pool_iid(p: float, k: int) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return 1.0 - p**k - (1.0 - p) ** k


def hidden_failed_branch_count_iid(p: float, k: int) -> float:
    """Expected failed branches omitted when the served winner succeeds."""
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    if k < 1:
        raise ValueError("k must be positive")
    return k * ((1.0 - p) - (1.0 - p) ** k)


def p_star(k: int) -> float:
    if k <= 1:
        raise ValueError("an interior rescue-censoring peak requires k > 1")
    return 1.0 - k ** (-1.0 / (k - 1))


def continuous_projection_stats(
    support: Mapping[ScoreOutcome, float],
) -> ContinuousProjectionStats:
    """Verify the continuous layer-cake identity on a finite-support joint law.

    For each atom r, the threshold-censoring integral equals max(r)-r[0]
    exactly. Summing over atoms yields the population identity without any
    rollout-independence assumption.
    """
    rows = _validate_distribution(support.items())
    if any(any(value < 0.0 or value > 1.0 for value in outcome) for outcome, _ in rows):
        raise ValueError("scores must lie in [0, 1]")

    acting_gain = sum((max(outcome) - outcome[0]) * probability for outcome, probability in rows)
    integrated = sum(
        max(0.0, max(outcome) - outcome[0]) * probability
        for outcome, probability in rows
    )
    return ContinuousProjectionStats(
        acting_gain=acting_gain,
        integrated_threshold_censoring=integrated,
    )


def gated_projection_factorization(
    rows: Iterable[tuple[bool, float, float]],
) -> tuple[float, float, float]:
    """Return (ATE, event mass, conditional diagnostic advantage).

    Each row is (mixed_event, probability, future_value_difference). The
    alternative projection is required to equal winner-only outside the mixed
    event; this function rejects violations. Under that gate, ATE = mass * delta.
    """
    normalized = [(bool(mixed), float(prob), float(diff)) for mixed, prob, diff in rows]
    if not normalized:
        raise ValueError("rows must be non-empty")
    if any(prob < 0 for _, prob, _ in normalized):
        raise ValueError("probabilities must be non-negative")
    total = sum(prob for _, prob, _ in normalized)
    if not isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-10):
        raise ValueError("probabilities must sum to one")
    if any((not mixed) and not isclose(diff, 0.0, abs_tol=1e-12) for mixed, _, diff in normalized):
        raise ValueError("gated projections must be identical outside the mixed event")

    ate = sum(prob * diff for _, prob, diff in normalized)
    mass = sum(prob for mixed, prob, _ in normalized if mixed)
    delta = (
        sum(prob * diff for mixed, prob, diff in normalized if mixed) / mass
        if mass > 0
        else 0.0
    )
    return ate, mass, delta


===== BOUND ARTIFACT: mechanical_pilot_runner | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/scripts/run_e2_r17_v3_1_mechanical_pilot.py =====
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_evidence_window_v2 import (
    TOKENIZER_ENCODING,
    TOKENIZER_PACKAGE,
    TOKENIZER_VERSION,
    ExactMatchedEvidenceBlockRenderer,
    canonical_trajectory_text,
)
from research_pipeline.e2_r17_mindmemos_updater import (
    BlindedEvidenceUnit,
    build_blinded_add_record_payload,
)
from research_pipeline.e2_r17_search_projection_runner import (
    ProjectionName,
    SearchPool,
    TrajectoryRef,
    project,
    validate_mixed_cloned_pair,
)

EXPECTED_STATUS = "AUTHORIZED_ZERO_PROVIDER_MECHANICAL_PILOT_ONLY"
FORBIDDEN_VISIBLE_MARKERS = (
    "PROJECTION:",
    "ROLE:",
    "SOURCE_ROLLOUT_INDEX",
    "SOURCE_TRAJECTORY_SHA256",
    "WINNER_ONLY",
    "MIXED_REJECTED_WITNESS",
    "mixed_rejected_witness",
    "winner_only",
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def append_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def reconstruct_pool(payload: dict[str, Any]) -> SearchPool:
    fields = set(TrajectoryRef.__dataclass_fields__.keys())
    trajectories = tuple(
        TrajectoryRef(**{key: row.get(key) for key in fields})
        for row in payload["trajectories"]
    )
    pool = SearchPool(
        pool_id=payload["pool_id"],
        task_id=payload["task_id"],
        k=int(payload["k"]),
        trajectories=trajectories,
        search_topology=payload["search_topology"],
    )
    pool.validate()
    return pool


def completed_rows(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[str(row["unit_id"])] = row
    return rows


def verify_completed(row: dict[str, Any]) -> bool:
    receipt = Path(row["receipt_path"])
    return receipt.exists() and sha_file(receipt) == row["receipt_sha256"]


def check_bound_path(path: Path, expected_sha: str, label: str) -> None:
    require(path.exists(), f"missing bound {label}: {path}")
    require(sha_file(path) == expected_sha, f"SHA drift for {label}: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    args = parser.parse_args()

    started = time.monotonic()
    contract = load_json(args.contract)
    require(contract.get("status") == EXPECTED_STATUS, "V3.1 mechanical pilot lacks execution authorization")
    authority = contract.get("authority") or {}
    require(authority.get("execute_mechanical_pilot") is True, "mechanical-pilot authority false")
    for forbidden_authority in ("provider_runtime_pilot", "e1_a", "e1_b", "paper_promotion", "submission"):
        require(authority.get(forbidden_authority) is False, f"forbidden inherited authority: {forbidden_authority}")

    for key in ("repair", "upstream_prompt_dataflow_audit", "review_adjudication"):
        bound = contract[key]
        check_bound_path(ROOT / bound["path"], bound["sha256"], key)

    renderer_cfg = contract["renderer"]
    check_bound_path(ROOT / renderer_cfg["path"], renderer_cfg["sha256"], "renderer")
    updater_cfg = contract["updater_wrapper"]
    check_bound_path(ROOT / updater_cfg["path"], updater_cfg["sha256"], "updater wrapper")
    check_bound_path(ROOT / updater_cfg["test_path"], updater_cfg["test_sha256"], "updater V3.1 tests")

    observed_tiktoken = importlib.metadata.version(TOKENIZER_PACKAGE)
    require(observed_tiktoken == TOKENIZER_VERSION == renderer_cfg["tokenizer_version"], "tokenizer version drift")
    require(TOKENIZER_ENCODING == renderer_cfg["tokenizer_encoding"], "tokenizer encoding drift")

    mind = contract["mindmemos"]
    mind_root = Path(mind["root"])
    head = subprocess.run(
        ["git", "-C", str(mind_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    require(head == mind["commit"], "MindMemOS commit drift")
    dirty = subprocess.run(
        ["git", "-C", str(mind_root), "status", "--short"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    require(not dirty, "MindMemOS pinned checkout is dirty")
    for rel, expected in mind["bound_files"].items():
        check_bound_path(mind_root / rel, expected, f"MindMemOS:{rel}")

    hist = contract["historical_inputs"]
    e0_root = Path(hist["e0_root"])
    e0_summary = Path(hist["e0_summary"])
    check_bound_path(e0_summary, hist["e0_summary_sha256"], "historical E0 summary")
    pool_files = sorted((e0_root / "cases").glob("*/pool_k8.json"))
    require(len(pool_files) == int(hist["expected_k8_pools"]), "historical K8 pool cardinality drift")

    renderer = ExactMatchedEvidenceBlockRenderer(final_block_cap_tokens=int(renderer_cfg["final_block_cap_tokens"]))
    transcript_max_chars = int(updater_cfg["transcript_max_chars"])
    require(transcript_max_chars >= 100000, "V3.1 transcript limit must be nonbinding by contract")

    run_root = Path(contract["run_root"])
    raw_root = run_root / "raw/pools"
    checkpoint = run_root / "checkpoints/completed_units.jsonl"
    summary_path = run_root / "summary/runtime_pilot_summary.json"
    completed = completed_rows(checkpoint)
    for unit_id, row in completed.items():
        require(verify_completed(row), f"resume SHA mismatch: {unit_id}")

    completed_now = 0
    reused = 0
    matched_tokens: list[int] = []
    selected_budget_gaps: list[int] = []
    visible_chars: list[int] = []
    mixed_count = 0
    nonmixed_count = 0

    for pool_file in pool_files:
        pool_payload = load_json(pool_file)
        pool = reconstruct_pool(pool_payload)
        unit_id = pool.pool_id
        if unit_id in completed:
            reused += 1
            continue

        payloads: dict[int, dict[str, Any]] = {}
        trajectories: dict[int, TrajectoryRef] = {}
        for trajectory in pool.trajectories:
            source_path = Path(trajectory.trajectory_path)
            require(sha_file(source_path) == trajectory.trajectory_sha256, f"trajectory SHA drift: {source_path}")
            source_payload = load_json(source_path)
            index = int(source_payload["rollout_index"])
            require(index == trajectory.rollout_index, "trajectory rollout index drift")
            payloads[index] = source_payload
            trajectories[index] = trajectory

        win = project(pool, ProjectionName.WINNER_ONLY)
        mrw = project(pool, ProjectionName.MIXED_REJECTED_WITNESS)
        validate_mixed_cloned_pair(pool, win, mrw)
        if pool.mixed_pool:
            mixed_count += 1
            require(win.selected_indices != mrw.selected_indices, "MRW failed to differ on mixed support")
        else:
            nonmixed_count += 1
            require(win.selected_indices == mrw.selected_indices, "MRW changed outside mixed support")

        win_idx = win.slots[0].rollout_index
        mrw_idx = mrw.slots[0].rollout_index
        win_source = trajectories[win_idx]
        mrw_source = trajectories[mrw_idx]
        win_text = canonical_trajectory_text(payloads[win_idx])
        mrw_text = canonical_trajectory_text(payloads[mrw_idx])
        win_block, mrw_block, block_receipt = renderer.render_pair(win_text, mrw_text)
        win_actual = len(renderer.encoding.encode(win_block))
        mrw_actual = len(renderer.encoding.encode(mrw_block))
        require(win_actual == mrw_actual == block_receipt.matched_final_block_tokens, "actual final token parity failed")
        if not pool.mixed_pool:
            require(win_block == mrw_block, "nonmixed evidence is not byte-identical")

        for visible in (win_block, mrw_block):
            require(len(f"[user] {visible}") <= transcript_max_chars, "first-party transcript would truncate V3.1 evidence")
            for marker in FORBIDDEN_VISIBLE_MARKERS:
                require(marker not in visible, f"arm/provenance marker leaked into updater evidence: {marker}")

        win_unit = BlindedEvidenceUnit(
            task_id=pool.task_id,
            pool_id=pool.pool_id,
            acting_winner_sha256=pool.winner.trajectory_sha256,
            source_rollout_index=win_idx,
            source_trajectory_sha256=win_source.trajectory_sha256,
            source_score=float(win_source.score),
            evidence_text=win_block,
            evidence_sha256=sha_bytes(win_block.encode("utf-8")),
            evidence_tokens=win_actual,
        )
        mrw_unit = BlindedEvidenceUnit(
            task_id=pool.task_id,
            pool_id=pool.pool_id,
            acting_winner_sha256=pool.winner.trajectory_sha256,
            source_rollout_index=mrw_idx,
            source_trajectory_sha256=mrw_source.trajectory_sha256,
            source_score=float(mrw_source.score),
            evidence_text=mrw_block,
            evidence_sha256=sha_bytes(mrw_block.encode("utf-8")),
            evidence_tokens=mrw_actual,
        )
        common = {
            "pool": pool,
            "project_id": "v31-mechanical-internal-project",
            "task_completed_at": "2026-08-28T00:00:00+00:00",
            "initial_skill_sha256": pool.trajectories[0].skill_pre_sha256,
            "root_version_id": "v31-mechanical-root-version",
        }
        win_payload = build_blinded_add_record_payload(unit=win_unit, projection_label="winner_only", **common)
        mrw_payload = build_blinded_add_record_payload(unit=mrw_unit, projection_label="mixed_rejected_witness", **common)

        require(win_payload["messages"] == [{"role": "user", "content": win_block}], "WIN model-visible payload drift")
        require(mrw_payload["messages"] == [{"role": "user", "content": mrw_block}], "MRW model-visible payload drift")
        require(float(win_payload["score"]) == float(win_source.score), "WIN selected-evidence score drift")
        require(float(mrw_payload["score"]) == float(mrw_source.score), "MRW selected-evidence score drift")
        require(win_payload["r17_acting_score"] == mrw_payload["r17_acting_score"] == pool.acting_success, "acting score differs across clones")
        require(win_payload["r17_acting_winner_sha256"] == mrw_payload["r17_acting_winner_sha256"] == pool.winner.trajectory_sha256, "acting winner differs across clones")
        if not pool.mixed_pool:
            require(win_payload["messages"] == mrw_payload["messages"], "nonmixed model-visible messages differ")
            require(win_payload["score"] == mrw_payload["score"], "nonmixed model-visible scores differ")
        else:
            require(float(win_payload["score"]) == 1.0, "mixed WIN should expose successful winner score")
            require(float(mrw_payload["score"]) == 0.0, "mixed MRW should expose failed witness score")

        matched_tokens.append(win_actual)
        selected_budget_gaps.append(abs(block_receipt.left_selected_source_tokens - block_receipt.right_selected_source_tokens))
        visible_chars.extend([len(win_block), len(mrw_block)])
        receipt = {
            "schema_version": "1.0",
            "artifact_type": "e2-r17-v3-1-mechanical-pilot-pool",
            "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "unit_id": unit_id,
            "task_id": pool.task_id,
            "pool_file": str(pool_file),
            "pool_file_sha256": sha_file(pool_file),
            "mixed_pool": pool.mixed_pool,
            "winner_index": win_idx,
            "mrw_index": mrw_idx,
            "matched_evidence": block_receipt.to_dict(),
            "win_model_visible_message_sha256": sha_bytes(json.dumps(win_payload["messages"], ensure_ascii=False, sort_keys=True).encode("utf-8")),
            "mrw_model_visible_message_sha256": sha_bytes(json.dumps(mrw_payload["messages"], ensure_ascii=False, sort_keys=True).encode("utf-8")),
            "win_selected_evidence_score": win_payload["score"],
            "mrw_selected_evidence_score": mrw_payload["score"],
            "acting_score_identical": win_payload["r17_acting_score"] == mrw_payload["r17_acting_score"],
            "acting_winner_identical": win_payload["r17_acting_winner_sha256"] == mrw_payload["r17_acting_winner_sha256"],
            "arm_metadata_visible_in_messages": False,
            "downstream_transcript_truncation": False,
            "provider_calls": 0,
            "new_actor_rollouts": 0,
            "scientific_effectiveness_evaluated": False
        }
        receipt_path = raw_root / f"{pool.task_id}.json"
        atomic_json(receipt_path, receipt)
        manifest_row = {
            "unit_id": unit_id,
            "task_id": pool.task_id,
            "receipt_path": str(receipt_path),
            "receipt_sha256": sha_file(receipt_path),
        }
        append_manifest(checkpoint, manifest_row)
        completed[unit_id] = manifest_row
        completed_now += 1

    for unit_id, row in completed.items():
        require(verify_completed(row), f"post-write completed receipt SHA mismatch: {unit_id}")

    if reused:
        matched_tokens = []
        selected_budget_gaps = []
        visible_chars = []
        mixed_count = 0
        nonmixed_count = 0
        for row in completed.values():
            receipt = load_json(Path(row["receipt_path"]))
            block = receipt["matched_evidence"]
            matched_tokens.append(int(block["matched_final_block_tokens"]))
            selected_budget_gaps.append(abs(int(block["left_selected_source_tokens"]) - int(block["right_selected_source_tokens"])))
            mixed_count += int(bool(receipt["mixed_pool"]))
            nonmixed_count += int(not bool(receipt["mixed_pool"]))

    sample = next(iter(completed.values()))
    with tempfile.TemporaryDirectory() as temp_dir:
        corrupt = Path(temp_dir) / "corrupt.json"
        source = Path(sample["receipt_path"])
        corrupt.write_bytes(source.read_bytes() + b"\nCORRUPTION")
        corruption_detected = sha_file(corrupt) != sample["receipt_sha256"]
    require(corruption_detected, "receipt corruption detector failed")

    def stats(values: list[int]) -> dict[str, Any]:
        ordered = sorted(values)
        return {
            "n": len(ordered),
            "min": ordered[0],
            "median": (ordered[(len(ordered) - 1) // 2] + ordered[len(ordered) // 2]) / 2,
            "max": ordered[-1],
            "mean": sum(ordered) / len(ordered),
        }

    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-v3-1-mechanical-pilot-summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS_ZERO_PROVIDER_MECHANICAL_PILOT",
        "contract": str(args.contract),
        "contract_sha256": sha_file(args.contract),
        "repair_sha256": contract["repair"]["sha256"],
        "upstream_prompt_dataflow_audit_sha256": contract["upstream_prompt_dataflow_audit"]["sha256"],
        "review_adjudication_sha256": contract["review_adjudication"]["sha256"],
        "historical_e0_summary_sha256": sha_file(e0_summary),
        "mindmemos_commit": head,
        "tokenizer": {
            "package": TOKENIZER_PACKAGE,
            "version": observed_tiktoken,
            "encoding": TOKENIZER_ENCODING,
        },
        "pools": len(completed),
        "mixed_pools": mixed_count,
        "nonmixed_pools": nonmixed_count,
        "completed_now": completed_now,
        "reused_after_sha_validation": reused,
        "matched_final_tokens": stats(matched_tokens),
        "selected_source_budget_gap": stats(selected_budget_gaps),
        "exact_final_retokenized_parity": True,
        "nonmixed_model_visible_identity": True,
        "arm_metadata_visible_in_messages": False,
        "selected_evidence_score_semantics": True,
        "acting_provenance_identical_across_clones": True,
        "downstream_transcript_truncation": False,
        "corruption_detection_simulation": corruption_detected,
        "provider_calls": 0,
        "new_actor_rollouts": 0,
        "scientific_effectiveness_evaluated": False,
        "wall_seconds": time.monotonic() - started,
        "next_authority": {
            "provider_runtime_pilot": False,
            "e1_a": False,
            "e1_b": False,
            "paper_promotion": False
        }
    }
    atomic_json(summary_path, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


===== BOUND ARTIFACT: review_model_identity | /home/wyt/code/agent-self-evolution-observatory-e2-r17-compute-shielding-20260825/generated/e2-r17-v3-1-model-identity-qualification-20260828.json =====
{
  "artifact_type": "e2-r17-current-ark-plan-model-identity-qualification",
  "authority": {
    "gpu": false,
    "paper_promotion": false,
    "preexecution_consultation": true,
    "scientific_experiment": false,
    "submission": false
  },
  "checks": {
    "all_protocol_calls_pass": true,
    "provider_retry_zero": true,
    "resolved_identities_distinct": true,
    "route_is_ark_plan": true
  },
  "compatibility_parent": null,
  "created_at_utc": "2026-08-28T13:07:35+00:00",
  "default_model": "ark-code-latest",
  "models": [
    {
      "benchmark_data_accessed": false,
      "checks": {
        "resolved_model_matches_requested_family": true,
        "resolved_model_present": true,
        "text_exact": true
      },
      "get_poll_recovery": false,
      "hidden_provider_retry_used": false,
      "max_output_tokens": 256,
      "poll_count": 0,
      "prompt_sha256": "7bfaf5897d7bbd7f972a67554ee32acc828cd8309e40822dfc05217e987776bf",
      "provider_generation_attempts": 1,
      "provider_retry_limit": 0,
      "provider_status": "completed",
      "raw_text": "PLAN_OK",
      "raw_text_sha256": "aa6b4c1b97751f326153c1927c1106bf5a927ec506a8066dfe0dded595992d7c",
      "requested_model": "deepseek-v4-pro",
      "resolved_model": "deepseek-v4-pro-ga-260813",
      "response_id_sha256": "dcb907dee411a2b8a22b3a85eba5b8f5b0af989e2f8b8f6b8fe82d774d86e627",
      "scientific_outcome": false,
      "status": "PASS",
      "thinking_requested": "disabled",
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
    {
      "benchmark_data_accessed": false,
      "checks": {
        "resolved_model_matches_requested_family": true,
        "resolved_model_present": true,
        "text_exact": true
      },
      "get_poll_recovery": false,
      "hidden_provider_retry_used": false,
      "max_output_tokens": 256,
      "poll_count": 0,
      "prompt_sha256": "7bfaf5897d7bbd7f972a67554ee32acc828cd8309e40822dfc05217e987776bf",
      "provider_generation_attempts": 1,
      "provider_retry_limit": 0,
      "provider_status": "completed",
      "raw_text": "PLAN_OK",
      "raw_text_sha256": "aa6b4c1b97751f326153c1927c1106bf5a927ec506a8066dfe0dded595992d7c",
      "requested_model": "kimi-k3",
      "resolved_model": "kimi-k3",
      "response_id_sha256": "7c5b53c247778d7b501aa3cee492d5df425508d038e462bd2039a360aa6a80e8",
      "scientific_outcome": false,
      "status": "PASS",
      "thinking_requested": "disabled",
      "usage": {
        "input_tokens": 41,
        "input_tokens_details": {
          "cached_tokens": 0
        },
        "output_tokens": 13,
        "output_tokens_details": {
          "reasoning_tokens": 0
        },
        "total_tokens": 54
      }
    }
  ],
  "private_credentials_included": false,
  "raw_response_ids_included": false,
  "release_drift_policy": "Observed resolved identities are frozen for this review tranche. Historical exact suffixes are not reused as authority. Any later execution tranche must requalify and bind its own observed identities.",
  "route": "https://ark.cn-beijing.volces.com/api/plan/v3",
  "schema_version": "1.0",
  "status": "PASS"
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


===== BOUND ARTIFACT: mindmemos_trajectory_summary_prompt_first_party | /data/wyt/evidence-substrates/MindMemOS-20260817/src/mindmemos/mindmemos/prompts/EN/skills/trajectory_summary.py =====
SUMMARY_SYSTEM = """You are a concise expert in AI trajectory analysis. Given an agent trajectory that used one or more skills, produce an analytical summary in 8–15 sentences.

The summary must cover at minimum:
1. Goal: the user-facing task the agent was trying to complete.
2. Trajectory flow: the agent's main sequence of actions, including what it tried, in what order, and why.
3. Turning points: the key moments where the agent changed strategy, especially after repeated tool failures, verification failures, unexpected errors, or new information; explain the trigger, the new strategy, and the effect.
4. Skill effectiveness: for each injected skill, explain whether it helped or hurt, which guidance was followed, and which guidance was missing, misleading, ignored, or especially useful. If multiple skills were used, describe how they interacted and whether any skill was more important than the others.
5. Tool usage patterns: which tools were used effectively, which caused problems, and whether verification caught or missed important issues.
6. Outcome: the final result quality, any unresolved risks, and your confidence based only on transcript evidence.

Write a compact evidence-based paragraph, not a checklist. Preserve causal relationships and mention concrete examples from the trajectory when they matter. Do not quote or summarize skill documents at length, do not propose a patch, and do not invent facts not supported by the transcript. Output only the plain-text summary, with no JSON and no markdown fences."""


def summarize_trajectory_user(skill_name: str, transcript: str) -> str:
    """Build the user prompt for summarizing one injected trajectory."""

    return f"# Injected skill\n{skill_name}\n\n# Complete agent session transcript\n{transcript}"


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


BOUND DOSSIER END
