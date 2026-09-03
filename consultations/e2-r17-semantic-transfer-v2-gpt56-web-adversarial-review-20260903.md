# E2-R17 Semantic-Transfer V2 — independent GPT web adversarial review

Date: 2026-09-03
Reviewer surface: ChatGPT web, GPT-5.6 Sol, thinking level `极高`
Conversation: `https://chatgpt.com/c/6a993171-07d8-83ee-92be-ab0913403166`
Execution: prompt submitted exactly once; no Codex model inference was used for the review.

## Verdict

`REVISE_BEFORE_STAGE_A`

The reviewer did **not** reject Search-Projection Censoring as a scientific object. It judged the state-level causal intervention to be the strongest part of the design: with acting fixed, replacing only the persistent learner's projection is a coherent intervention on learner-visible search evidence.

The verdict changes because V2 overreaches from that clean intervention to a semantic mechanism and an automatic router without enough identification.

## Findings that must change the design

1. **Semantic causality is not identified by the current three pairings.** The three procedural families and three binding families remain family-specific generators. A pooled procedural-vs-binding contrast can therefore be explained by family identity or failure-trace information content. A genuinely crossed `semantic class × learning projection` test inside common skeleton/templates is required for a mechanism claim.
2. **Three skeletons cannot support an exact one-sided `.05` sign claim.** With three independent signs the smallest nonzero one-sided exact probability is `1/2^3 = 0.125`. At least five genuinely independent crossed skeletons are required even for an all-positive one-sided exact sign test (`1/2^5 = 0.03125`).
3. **The router currently has privileged construction information.** `reusable_transform_steps`, `binding_candidate_count`, family identity, template identity, and hidden semantic labels may define experimental strata but cannot be inputs to a deployable learning policy. A method router must be a deterministic function of information available before the update on the same observable task/search interface.
4. **The inferential unit and power argument are mismatched to the claim.** `R=7` reduces updater stochasticity but cannot create semantic-family replication. The old pooled within-stream replicate SD cannot justify power for a general semantic-law claim. Independent skeleton/family variation must control the mechanism inference.
5. **MRW4 must be specified as one reproducible intervention, not by an implicit historical rule.** The protocol must freeze the exact failed-nonwinner selector, treated-pool selector, updater order, and stochastic pairing semantics before acquisition.

## Important allowed interpretation

A new prospective suite can validly test a hypothesis discovered from the closed DeepSeek sample if the old sample remains discovery/calibration only and never enters the new confirmatory p-value. The claim must be bounded to the frozen prospective construction unless it is replicated across genuinely independent semantic realizations.

The strongest simpler explanation for the old heterogeneity is **failure-trace diagnosticity/informativeness**: procedural failures may preserve reusable intermediate transformations, whereas binding failures may encode a confidently wrong local binding. The new design therefore needs to distinguish semantic interaction from mere family identity; if that distinction fails, the paper should prefer a diagnosticity explanation rather than rescue the semantic story.

## Highest-information next experiment

A new prospective crossed design:

`matched skeleton × {PROCEDURAL_TRANSFORMATION, INSTANCE_BINDING_LOCALIZATION} × {WIN-C, MRW4}`

where both semantic cells are generated from the same skeleton/template and the primary mechanism statistic is

`I_h = D_{h,procedural} - D_{h,binding}`.

The automatic policy, if retained, must consume only pre-update observable information. Hidden generator annotations may be used for blinded experimental stratification but not deployment routing.

## Governance consequence

Semantic-Transfer V2 remains preserved but is superseded **before any provider Stage A**. This review grants no provider, updater, heldout, analyzer, second-backbone, benchmark, paper-promotion, or submission authority.
