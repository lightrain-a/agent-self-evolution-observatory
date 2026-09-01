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
