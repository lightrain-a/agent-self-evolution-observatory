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
