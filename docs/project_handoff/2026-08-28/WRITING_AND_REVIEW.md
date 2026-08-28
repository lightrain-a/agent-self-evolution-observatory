# Writing and Review Workflow

This file turns the project's repeated writing/review lessons into a stable paper-production protocol.

## 1. Paper story comes from the scientific chain

A strong manuscript should make the following chain easy to recover:

```text
problem / scientific object
→ why existing evaluation or methods miss it
→ mechanism or formal model
→ falsifiable prediction / boundary
→ controlled experiment
→ evidence and ruling-out
→ implication / engineering decision
```

Do not write the paper as a chronological diary of experiments.

## 2. Audience bridge

For a paper that builds on an existing method:
- explain the general problem before naming the niche implementation;
- anchor experiments in methods/benchmarks the target community recognizes;
- use top-venue or otherwise strongly established baselines where appropriate;
- make clear which contribution is general and which evidence is substrate-specific.

A reviewer should be able to understand the paper's scientific object without already knowing the base method.

## 3. Main claim table

Maintain a compact claim ledger with at least:

```text
claim_id
claim text
primary evidence
audit/control evidence
scope
forbidden extrapolation
status
strongest reviewer objection
```

The manuscript should not contain a stronger statement than the ledger allows.

## 4. Related-work comparison table

A useful comparison table should compare **scientific capabilities/assumptions**, not just feature checkmarks chosen to favor the new method.

Good axes can include:
- scientific object/problem addressed;
- whether the method models the relevant mechanism;
- whether it provides controlled causal/intervention evidence;
- whether temporal/persistent state is represented;
- whether public benchmark/evaluation is available;
- whether claims are behavioral vs proxy-only;
- whether uncertainty/boundary conditions are explicit.

The proposed method belongs in the final row, but the axes should remain defensible if that row were removed.

## 5. Baseline-result presentation

When methods solve the same underlying problem with different internal mechanisms, map them to a common benchmark/evaluation outcome where scientifically valid.

Do not paste unrelated numbers from other papers into a table as if they were directly comparable. Check:
- same dataset/split;
- same unit of analysis;
- same metric definition;
- same evaluation protocol;
- compatible model setting;
- whether numbers are reproduced or quoted.

If direct comparison is impossible, label it as contextual rather than experimental superiority evidence.

## 6. Reviewer-driven experiment design

Before finalizing experiments, ask:
- what is the single strongest objection to novelty?;
- what is the single strongest confound?;
- what simple baseline could absorb the gain?;
- what result would force claim narrowing?;
- what evidence is missing for external validity?;

Use these questions to prioritize experiments. Do not add experiments just because a table has empty space.

## 7. Main text vs supplementary material

Main text should contain:
- scientific question;
- core mechanism/model;
- primary causal/behavioral evidence;
- strongest ruling-out/control;
- main comparison;
- essential limitation/boundary.

Supplement can contain:
- extended robustness;
- extra datasets/models;
- implementation detail;
- full prompts/configurations;
- complete per-case/qualitative examples;
- additional proofs and reviewer-oriented diagnostics.

Do not hide evidence necessary to understand the primary claim exclusively in supplement.

## 8. Figures and tables

Each major figure/table must answer a named scientific question. Useful roles include:
- overview/mechanism;
- main comparison;
- boundary/regime;
- controlled intervention;
- failure/ruling-out;
- sensitivity/uncertainty;
- traceability.

Avoid redundant visualizations that merely restate the same scalar result.

## 9. LaTeX/source hygiene

Use a clean task-specific worktree for manuscript edits. Do not let compiled PDFs, auxiliary files, or generated figures create ambiguous source diffs.

After substantive changes:
1. static source check;
2. compile;
3. inspect errors/warnings relevant to correctness;
4. visually inspect changed equations/tables/figures/pages;
5. check references/citations if changed;
6. verify anonymous/submission format constraints;
7. verify that manuscript claims still bind to evidence artifacts.

## 10. Citation integrity

Reference hallucination can cause desk rejection or reviewer distrust. For important related-work sections:
- verify paper existence;
- verify title/authors/venue/year;
- verify that the cited paper actually supports the statement;
- prefer DOI/arXiv/official proceedings metadata;
- flag uncertain references rather than guessing.

## 11. Adversarial review

Use independent reviewers/models as red-teamers rather than endorsers. Ask them to return:
- accept/weak accept/weak reject/reject-style judgment;
- top fatal objection;
- novelty collision;
- causal confound;
- external-validity concern;
- missing baseline;
- smallest experiment or rewrite that would change their judgment.

Keep their review artifacts separate from scientific evidence.

## 12. Interpretation discipline

After results:
- explain what changed scientifically;
- explicitly state what did not become supported;
- distinguish localization from causation;
- distinguish realized intervention from intended intervention;
- distinguish paper-quality QA from scientific sufficiency.

## 13. Submission readiness

A paper is not ready merely because:
- page count passes;
- QA scripts pass;
- a PDF compiles;
- reviewer models are positive;
- a prior version was marked ready.

Submission readiness requires current human author responsibility, valid evidence/claim alignment, venue compliance, and no unresolved contradiction between canonical state and manuscript.
