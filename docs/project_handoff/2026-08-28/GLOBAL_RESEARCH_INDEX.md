# Global Research Index — Migration Snapshot

Snapshot date: 2026-08-28

This file is a **cross-project retrieval index** for durable work that appeared in the large ChatGPT project. It is not a live-status ledger. For every item, recover its own repository/artifacts before resuming experiments or making submission claims.

## A. VLM Fingerprint — CAVF (KDD 2027 direction)

### Durable object
Black-box/model-lineage fingerprinting for VLMs using controlled counterfactual/visual perturbation transfer rather than ordinary task accuracy.

### Frozen/repeated protocol facts from prior work
- four-choice readout;
- PNG replay;
- transforms including Identity, JPEG variants, and down-up perturbation;
- unified prompting;
- perturbation budget previously standardized around `L∞ = 8/255`;
- multiple source VLMs and derived-vs-independent model families were evaluated;
- important operational lesson: image-size/preprocessing mismatches can dominate a fingerprint evaluation and must be normalized before interpreting transfer.

### Durable evidence snapshot
Prior work reported very strong separation on several source/derived settings and low transfer to independent models, but exact current tables/artifacts must be recovered from the CAVF repository before use.

### Reusable lesson
Fingerprint claims require lineage/derivation controls, robust replay transformations, and a clear distinction between source-family transfer and generic VLM susceptibility.

---

## B. TPER — Task-Preserving Execution / Robot Safety

### Durable object
Whether a short-lived visual/intervention-induced deviation returns to a clean-compatible task trajectory, rather than merely reducing instantaneous action error.

### Durable distinctions
- phase alignment matters;
- “success” alone can hide residual trajectory divergence;
- recovery classes such as non-rejoin / rejoin-with-residual / full recovery are more informative than one scalar outcome;
- sustained compatibility for multiple steps is stronger evidence than a one-frame crossing.

### Reusable lesson
For embodied safety, evaluate task-preserving recovery over a temporal corridor, not only endpoint success or instantaneous action similarity.

---

## C. M³GT — Encrypted IoMT

### Durable object
Encrypted IoMT/security learning with multi-context/generalization evaluation.

### Snapshot
Previous work had strong A/B/D results and a more limited C component, with very high AUROC reported in a specific targetflow/peer/context setting. Recover the paper repository before quoting exact values.

### Reusable lesson
Separate in-distribution performance from context/peer/flow transfer and preserve the exact evaluation unit when comparing security models.

---

## D. Acoustic Latent Keys — AAAI-27 Direction

### Durable object
Audio/acoustic latent-key or ownership/fingerprint signal with owner-vs-independent discrimination and large-row evaluation.

### Snapshot
Prior work recorded a strong P0 AUC, owner/independent separation, and a large P4 row set. Exact values belong to the paper's canonical artifacts, not this index.

### Reusable lesson
Ownership/fingerprint work needs independent-model controls and should not treat same-family transfer as sufficient evidence of uniqueness.

---

## E. TCF — LLM Fingerprinting / NDSS-ArXiv Line

### Durable object
Black-box lineage/derivation auditing of LLMs using finite-answer counterfactual transfer.

### Durable comparisons
Prior work compared against or discussed fingerprint families such as Stemma, LLMPrint, TRAP, ProFLingo/ZeroPrint-like alternatives depending on the evaluation stage.

### Reusable lesson
The central claim should be lineage-sensitive transfer, not merely prompt memorization or one-model separability. Independent-model negatives and derived-model positives are essential.

---

## F. LLMPrint Reproduction / Figure Reconstruction

### Durable work
- reconstruction/alignment of figures and legends;
- OpenRouter-style cross-model comparison tables;
- distillation/teacher-student transfer checks.

### Reusable lesson
Reproduction artifacts should be clearly separated from novel-paper evidence. Figure rebuilding must bind plotted values to the exact recovered source table/run rather than manual visual approximation.

---

## G. STRI / ACV / Agent-Safety Paper Family

This family overlaps the more detailed `RESEARCH_PORTFOLIO.md`.

### Durable object
Authorization/evidence structure and representation invariance in self-evolving or embodied agents.

### Durable distinctions
- proposal vs execution authorization;
- typed evidence;
- fail-open behavior;
- structural correctness vs semantic correctness;
- representation/package identity vs semantic control;
- released metadata vs released behavioral outcome.

### Reusable lesson
A structural safety/authorization mechanism can be valid without solving semantic perception/reasoning; claims must not collapse these levels.

---

## H. Agent Self-Evolution — R9 Safety

### Durable object
Whether a state that is statically safe can evolve, under benign persistent-state updates, into a later first-violation hazard.

### Durable setup themes
- persistent memory/history state;
- benign appending/update rule;
- frozen substrate/backbone/evaluator per experiment;
- first-violation / future-hazard outcome rather than static safety only.

### Reusable lesson
Static safety is not automatically predictive of future safety under persistent self-evolution. Longitudinal state-level evaluation must avoid tuning guards or thresholds after seeing outcomes.

---

## I. Research Memory Graph / Observatory Site

### Durable purpose
A machine-readable research memory/control graph plus human-facing timeline/dashboard for claims, experiments, failures, closures, reopen conditions, and paper artifacts.

### Reusable lesson
Dashboards are valuable for navigation but must be generated from canonical state. The backend should update automatically from source state; the frontend can be refreshed/deployed separately without becoming scientific authority.

---

## J. Embodied VLA Memory & Self-Evolving Loop — Papers A/B/C

This is a major research program and should probably receive its **own new-project handoff** if active work continues.

### Paper A — Persistent Memory Channel / Provenance
Durable question: how far past experience influences future behavior, whether the influence faithfully replays the source experience, and whether future task success/recovery remains intact.

Important invariant: persistent influence, faithful replay, and downstream success are three different outcomes.

### Paper B — Embodied Self-Evolution / Memory Safety (AAMAS-oriented)
Durable structure:
- self-evolution risks can be organized across model/memory/tool/workflow;
- physical closed-loop systems amplify small deviations;
- task-preserving recovery/rejoin requires temporal evidence;
- memory admission/write, effect attribution, and transfer/reuse are distinct stages;
- a state-machine view of candidate/provisional/certified/conditional/reusable memory can make provenance explicit.

Critical anti-drift rule: do not let audit machinery become the main paper if the scientific question is about memory-mediated embodied evolution.

### Paper C — Residual Latent / RL Direction
Durable question: whether a learned residual/latent corrective mechanism adds value over direct RL or a simpler lightweight processor.

Critical baseline rule: direct RL and simple residual baselines must be strong enough to absorb cosmetic gains.

### Shared embodied infrastructure convention
A shared storage split has been used under `/data/zmy/exp/emise/` with `shared`, `policy`, and `belief` areas. Verify current state before use.

---

## K. ICASSP — ECG Withheld-Composition / PTB-XL

### Durable scientific object
Patient-disjoint evaluation does not test whether a model generalizes to unseen **label compositions**. Withheld-composition evaluation removes target joint positives while retaining individual label positives.

### Durable protocol
- patient separation remains;
- target pair joint positives are withheld in training;
- individual positives remain;
- vocabulary remains fixed;
- evaluate joint prediction explicitly, not only marginal AUROC/AUPRC.

### Snapshot insight
Prior experiments showed a meaningful exposed-vs-withheld gap and some improvement from hard-union-style intervention on later folds. Recover exact CIs/results before quoting.

### Reusable lesson
Distribution shift can live in **label composition topology**, not only patients/domains/classes. Evaluation should match the claimed compositional generalization object.

---

## L. EMNLP — DEMIA / Membership-Inference Auditing

### Durable object
Whether apparent membership signals in fine-tuned LLMs are genuine membership evidence or confounded by run/exposure/near-duplicate/regularization effects.

### Durable review concerns
- cross-run transfer;
- near-duplicate stress tests;
- TF-IDF/character n-gram or hashing-style duplication diagnostics;
- over-regularization evidence;
- uncertainty/95% confidence intervals;
- citation/reference integrity is high-risk and must be manually/externally verified.

### Reusable lesson
For MIA, separate **exposure topology** (exact, near-duplicate, semantic derivative, unseen) from a single binary membership score whenever the scientific claim concerns how data entered training.

---

## M. openPangu-2.0 Pro Long-Form Article

### Durable writing requirements
- explain first-use terminology but avoid overly conversational simplification;
- avoid first-person voice when inappropriate;
- use consistent model naming such as `505B` where required;
- organize from a reader/user perspective rather than mirroring the report section-by-section;
- verify official links and replace stale community links when necessary;
- figures should be consistently styled, largely redrawn rather than copied except for necessary screenshots;
- Word export and full factual/table/data audit are part of completion.

### Reusable lesson
Technical-report derivative writing should preserve source fidelity while improving narrative hierarchy, and every table/figure number should be checked against the primary report.

---

## N. ESWA / Other Submission-Readiness Reviews

The project has also included final-submission checks for journal/conference manuscripts. These should be treated as document-specific review tasks, not folded into the scientific evidence of the research-system papers.

Reusable checklist:
- formatting/venue compliance;
- reference integrity;
- figure/table readability;
- claim/evidence consistency;
- limitation and reproducibility statements;
- save reviewer-facing issues in a versioned revision checklist for later rounds.

---

# Cross-project retrieval rule

When a new project mentions one of these names, first identify the **paper-specific canonical repository/file bundle**. This global index is only the routing layer.

Do not continue an experiment solely from the numbers in this snapshot. Recover the exact current artifact, code revision, and experimental context first.
