# E2-R17 Baseline and Model Choice Audit — V1

Date: 2026-08-28
Status: **primary-source audit complete; model matrix not yet frozen**

## 1. Audit question

The purpose of this audit is not to list fashionable models. It asks which executor and updater models the closest methods actually use, which implementations are available, and which comparisons can be mapped fairly into the E2-R17 projection protocol.

The closest works agree on two design facts:

1. executor/target and updater/skill author are separate scientific roles;
2. a Qwen sparse 35B-class model is the most credible open/common comparison axis, while strong API models provide capability and family diversity.

## 2. Model Choice Audit Table

| Work | Benchmark | Actor / Executor | Updater / Teacher | Open/API | Model size | Why this model | Reusable in our protocol? |
|---|---|---|---|---|---|---|---|
| MindMemOS | SpreadsheetBench Verified-400 | Released CLI/default: `gpt-5.4-mini`; the public result table itself does not bind its numbers to an explicit model ID | Configured MindMemOS chat endpoint; public table does not expose a distinct updater ID | API | undisclosed | First-party released runtime and reproduction command | **Yes, core substrate.** The locally pinned runtime is exact; model claims must follow the released config rather than infer a hidden table setting. |
| SkillCAT | SpreadsheetBench, WikiTQ, DocVQA | Qwen3.5-35B-A3B and Qwen3.5-122B-A10B; transfer users Gemma-4-31B-it and GPT-5.4-mini | The two Qwen models are also skill authors | open + API | 35B sparse, 122B sparse, 31B, closed | Matched author/user and cross-model transfer | **Partial.** CCE maps to a same-task success/failure contrast arm. Full CCE+AAE+TTE needs source-task replay and routing; no official code was found in this audit. |
| Branch2Skill | SearchQA, SpreadsheetBench, OfficeQA, DocVQA, LiveMath, ALFWorld | GPT-5.5, GPT-5.4, GPT-5.4-mini, GPT-5.4-nano, Qwen3.6-35B-A3B | GPT-5.5 in all main-table runs except model-role analysis | open + API | 35B sparse + closed | Explicitly tests branch-evidence transfer across target/skill identities | **Paper-spec extended baseline only.** Map elite path and same-parent siblings to the common projection interface; do not claim exact reproduction before code release. |
| SkillOpt | Six benchmarks above | GPT-5.5, GPT-5.4, GPT-5.4-mini, GPT-5.4-nano, GPT-5.2, Qwen3.5-4B, Qwen3.6-35B-A3B | Separate optimizer model, commonly GPT-5.5; matched self-optimizer also supported | open + API | 4B, 35B sparse + closed | Deliberate weak-to-frontier spread and independent optimizer role | **Yes, extended strong baseline.** Official code is available. Match benchmark, split, actor/updater roles, rollout/edit/validation budgets, and receipts. |
| Rethinking Self-Evolving Agent Skills / RethinkSkill | SearchQA, OfficeQA, SpreadsheetBench, LiveMath, DocVQA | GPT-5.5, Gemini 3.1 Pro, DeepSeek V4-Pro | Same model configuration as executor in the primary paper; released code allows separate backends | API | DeepSeek V4-Pro: 1.6T total / 49B active; other sizes undisclosed | Controlled Normal/Fail-only/Success-only feedback study across model families | **Yes, core control and multi-round baseline.** Official code and complete rollback/candidate logging exist. R17 adds a stricter same-pool/same-winner intervention. |
| TSR | Sokoban, FrozenLake, WebShop | Qwen2.5-0.5B and Qwen2.5-3B; WebShop uses 3B | PPO/GRPO parameter update, no external skill updater | open | 0.5B, 3B | Tests search-shaped training rollouts in small policies | **No as a main skill baseline.** Use for search/topology and compute-control context, not direct SpreadsheetBench projection comparison. |
| SkillEvolBench | 180 tasks: 6 environments × 5 skill families × 6 tasks | Claude Code Opus/Sonnet 4.5/4.6; Codex GPT-5.2/5.3-Codex and GPT-5.4; Gemini 2.5 Pro/3 Flash/3.1 Pro; Kimi-style presets | Condition-dependent revision in the same harness/model configuration | API/CLI | undisclosed | Public cross-harness acquisition/evaluation testbed | **Yes, secondary external validation after adapter Pilot.** Its T1–T3 learning and T4–T6 frozen evaluation structure is useful, but it is not a drop-in same-pool spreadsheet causal test. |

## 3. Fidelity tiers

### Tier A — official implementation suitable for a quantitative table

- **MindMemOS**: exact local commit `90491828726e1540442b17cd445d0308d0b8093c`.
- **RethinkSkill**: official implementation of matched feedback arms and multi-round validation.
- **SkillOpt**: official implementation of target/optimizer separation, bounded edits, and held-out validation.
- **SkillEvolBench**: official benchmark and adapters, subject to runtime qualification.

### Tier B — paper-spec method mapping only

- **SkillCAT**: use a clearly labelled `SkillCAT-style contrast` arm unless an official repository is released and pinned.
- **Branch2Skill**: the paper states that code will be published; current E2-R17 implementation can only be a protocol-aligned reconstruction.
- **TSR**: code is promised upon acceptance and the scientific object is parametric RL, not external skills.

A paper-spec reconstruction must never be labelled as an exact reproduction.

## 4. Cross-work conclusions

### 4.1 Common model axis

The strongest open/common axis is a **Qwen sparse 35B-class executor**:

- SkillCAT: Qwen3.5-35B-A3B;
- Branch2Skill and SkillOpt: Qwen3.6-35B-A3B.

These are different releases. E2-R17 must pick the exact available model after runtime qualification and name it exactly; it must not merge them into a generic “Qwen-35B” result.

### 4.2 Weak-model axis

Qwen3.5-4B is the clearest literature-backed weak target because SkillOpt reports it across the full benchmark family. It is only a candidate. It enters the main matrix if an outcome-blind Pilot confirms valid tool calls, artifact writing, verifier completion, and nondegenerate K=1 headroom.

The 0.5B/3B TSR models are not appropriate SpreadsheetBench anchors: they were trained with RL on Sokoban/FrozenLake/WebShop and answer a different question.

### 4.3 Strong cross-family axis

DeepSeek V4-Pro is a primary RethinkSkill model and the E0 actor already resolved stably to `deepseek-v4-pro-ga-260813`. It is therefore a defensible strong executor and frozen-updater candidate, subject to a light identity qualification for every new tranche.

Kimi K3 contributes a second API/model family and is available through the current Ark route, but it is not the common model used by the closest baselines. It should be described as robustness/diversity, not as baseline matching.

### 4.4 Actor and updater policy

The core public matrix should first vary executor while freezing the updater:

```text
executor ∈ {weak Qwen candidate, common Qwen-35B candidate, DeepSeek V4-Pro, Kimi K3}
updater  = one frozen, qualified strong updater
```

The V1 updater choice is DeepSeek V4-Pro because its Ark identity and MindMemOS runtime are already qualified. A second updater is a robustness experiment only after E1 passes. Do not run a 4×4 actor/updater cross-product.

The closest papers often use GPT-5.5 as the optimizer. That endpoint is not available in the current infrastructure, so the manuscript must report the mismatch instead of implying an exact model-level reproduction.

## 5. Candidate model matrix before Pilot

| Role | Candidate | Literature basis | Current status | Promotion gate |
|---|---|---|---|---|
| Weak open | Qwen3.5-4B | SkillOpt weak target | not qualified | valid-task/tool/file/verifier rate; useful K=1 headroom; stable identity |
| Common open | exact available Qwen3.5-35B-A3B **or** Qwen3.6-35B-A3B | SkillCAT / Branch2Skill / SkillOpt | availability unresolved | exact release pinned; tool qualification; no model-name substitution |
| Strong API | DeepSeek V4-Pro → `deepseek-v4-pro-ga-260813` | RethinkSkill + completed E0 | E0 qualified | light requalification per tranche |
| Second-family API | Kimi K3 | diversity and available Ark route | adapter qualified earlier, scientific tranche pending | tool/artifact/verifier/headroom and resolved identity |

A model cannot be selected because R17 gains look larger in Pilot. Promotion is based only on protocol validity, identifiability, headroom, stability, latency, and cost.

## 6. Baseline placement in the eventual paper

### Core methods across all qualified executors

- Winner-only
- Rejected Witness
- Full Pool
- final simplest R17 method, unless it is identical to Rejected Witness

### Extended methods on one or two representative executors

- Initial Skill / No Skill
- Precommitted rollout-0
- Duplicated Winner
- Random Nonwinner
- SkillCAT-style contrast
- RethinkSkill feedback arms
- SkillOpt
- Branch2Skill-style reconstruction

SkillEvolBench belongs in external validation, not in the exact-same-pool E1 causal table. TSR belongs in related work and the topology/compute-control analysis.

## 7. Primary sources audited

- MindMemOS local official checkout, commit `90491828726e1540442b17cd445d0308d0b8093c`: `docs/eval/README.md`, `skills/args.py`, and `README.md`.
- SkillCAT v2: <https://arxiv.org/html/2606.13317v2>.
- Branch2Skill v1: <https://arxiv.org/html/2608.08677v1>.
- SkillOpt official code/project: <https://github.com/microsoft/SkillOpt> and <https://microsoft.github.io/SkillOpt/>.
- RethinkSkill paper/code: <https://arxiv.org/html/2608.02636v1> and <https://github.com/HKUST-KnowComp/rethinkskill>.
- TSR: <https://arxiv.org/html/2602.11767>.
- SkillEvolBench: <https://github.com/AIoT-MLSys-Lab/SkillEvolBench> and <https://skillevolbench.github.io/>.

## 8. Decision

**The model matrix remains unfrozen until runtime Pilot.** The audit authorizes creation of Experiment Plan V1 and outcome-blind model qualification; it does not authorize E0-full, E1, public-benchmark full runs, paper promotion, or submission.
