# E2 R17 Compute Shielding — research decision chain

Date: 2026-08-25
Status: F0 scientific child; R16 remains the stable fallback.
Parent paper: `D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK`

## 1. Why this child exists

R16 established a reusable-skill attribution audit. Follow-up discussion asked whether apparent skill gains could be reproduced by generic deliberation or test-time compute. Several broader reframings were explored and deliberately rejected before R17:

1. **Skill vs. Planning** — rejected as a headline because the old planning prompt leaked task-specific temporal cues and used an unmatched extra LLM call.
2. **Skill–Compute Frontier / Compile-or-Deliberate** — demoted because it reduces too easily to Snell-style test-time compute allocation plus amortized inference and a deployment router.
3. **Trajectory basin / hidden-state geometry** — rejected as the headline after collision with reasoning-trajectory geometry / steering work; hidden-state route geometry is not the defended novelty.
4. **Procedural commitment** — rejected as an explanation of the existing EIA/BLS evidence because a model debate incorrectly interpreted BLS as longitudinal stability; here BLS means Bureau of Labor Statistics CPI.
5. **History necessity / persistence identifiability** — retained only as background because its formal core reduces to POMDP/meta-RL/value-of-information and sufficient-statistic theory.
6. **Procedure identification / version spaces** — retained only as a possible diagnostic because its core reduces to active learning, teaching dimension, program synthesis, and system identification.

The surviving question is therefore not *Skill versus Compute*. It is whether inference-time assistance changes the **data-generating process for self-evolution**.

## 2. Surviving thesis

> **Stronger test-time compute can improve immediate acting performance while degrading the quality of the persistent skill learned later, because test-time rescue censors reusable failures that the skill updater would otherwise observe.**

The defended novelty boundary is the coupling

`execution-time compute -> observed experience / failure distribution -> persistent skill update -> future frozen-skill capability`.

Snell-style work optimizes compute for the current answer. Rethinking-style skill work shows that failure feedback can matter for evolution. R17 asks whether the executor's compute budget **endogenously removes that feedback before the updater can learn from it**.

## 3. Minimal causal model

Let `C` denote the executor's test-time compute budget, `tau_C` the resulting trajectory, `S_t` the persistent skill state, and `U` a fixed skill updater:

`S_{t+1} = U(S_t, tau_C)`.

For reusable failure family `z`, let `p_z` be its latent incidence, `r_z(C)` the probability that extra test-time computation rescues it before the final trajectory is recorded, and `w_z` its future reusable value. Its visible probability is

`p_z * (1 - r_z(C))`,

and after `n` evolution episodes the probability that the updater has seen the failure at least once is

`P_z(C,n) = 1 - [1 - p_z(1-r_z(C))]^n`.

A minimal reusable-learning coverage statistic is

`L(C,n) = sum_z w_z P_z(C,n)`.

Thus online reward can increase with `C` while reusable failure coverage decreases.

## 4. Load-bearing falsifiable predictions

### H1 — acting benefit

For fixed task stream, model, initial skill, verifier, updater, and evolution budget:

`R_online(H) > R_online(L)`.

If high compute does not improve acting, the shielding question is not identified on that substrate.

### H2 — shielding reversal

After evolution, freeze the learned skill and evaluate every arm with the same low-compute executor `C_eval = L`:

`G_frozen(H/H) < G_frozen(L/L)`.

This is the core reversal: acting-optimal compute is learning-suboptimal.

### H3 — counterfactual recovery

Serve with high compute, but feed the updater a low-compute counterfactual rollout on the same task:

`G_frozen(H/L-shadow) > G_frozen(H/H)`.

This isolates the trajectory/feedback channel rather than an intrinsic harmful effect of high compute.

### H4 — missing-information vs. weighting control

Compare low-compute shadow feedback against hard mining/reweighting of failures that remain visible in the high-compute stream:

- if `H/H-hardmine ~= H/L-shadow`, downgrade to ordinary feedback weighting;
- if `H/L-shadow > H/H-hardmine`, support the stronger claim that high compute removed reusable failure information that cannot be recovered by reweighting observed high-compute trajectories.

## 5. Minimal F1 arm semantics

| Arm | Acting executor | Updater input | Purpose |
|---|---|---|---|
| `L/L` | low compute | observed low-C trajectory | learning-rich reference |
| `H/H` | high compute | observed high-C trajectory | shielding treatment |
| `H/L-shadow` | high compute | counterfactual low-C trajectory on same task | causal feedback-channel intervention |
| `H/H-hardmine` | high compute | high-C stream with pre-frozen failure reweighting | strongest simpler explanation |

Scientific unit: **one complete evolution run / final learned skill state**, not individual episodes or repeated LLM calls.

Pilot promotion must depend only on runtime/protocol/checkpoint integrity. Scientific outcomes cannot decide which endpoint/task is retained.

## 6. Primary F0 substrate decision

### Selected first substrate: MindMemOS + SpreadsheetBench

First-party snapshot inspected at:

`/data/wyt/evidence-substrates/MindMemOS-20260817`

Source commit:

`90491828726e1540442b17cd445d0308d0b8093c`

Relevant frozen source hashes:

- `mindmemos_eval/skills/runners.py`: `a0b7dd1071148f570b65f53963ff5843beeaeded5aaf82f0846182bb55d61732`
- `mindmemos_eval/skills/agents/react.py`: `aeff09d26829307c1362356802b668d12b9d9c47f6372583bbeb93d245b5bf24`
- `mindmemos_eval/skills/evolve/algo.py`: `2d2264b712e788b7f7e4aa988085ae943ac230a2ef7b4ae6c750d9887a6cf2ad`
- `mindmemos/pipelines/skill/evolution.py`: `37bb22da6d4e8485d824c3c31e48f200561b05834a8a6bf3c057b29613b2bca0`
- initial Spreadsheet skill `resources/skill_evolve/spreadsheetbench_init_skill/xlsx/SKILL.md`: `bcb738e9141a462c2afc854c5b17cb2ff039af5e1346510c271e6894267a26bb`

Why it qualifies:

1. acting compute has an explicit, task-level knob: `ReactAgent(max_turns=...)`;
2. each case records the full agent messages and verifier score;
3. `FastAPISkillEvolutionClient.record_case` feeds exactly those messages, score, task id and injected skill binding into the first-party evolution service;
4. the server `SkillEvolver` summarizes traces, aggregates them, proposes/applies a patch, and mints a new skill version;
5. evolved content is downloaded and written back to the live skill directory;
6. the final `SKILL.md` is therefore an explicit persistent artifact that can be copied/frozen and evaluated with `evolve=False` and common `max_turns=L`;
7. high-C acting and low-C shadow feedback can be separated without changing the updater implementation by changing which same-task rollout is passed to `record_case`.

Current limitation: a MindMemOS service is not currently running on the inspected host, and the full SpreadsheetBench dataset is not yet cached locally. These are infrastructure qualifications, not scientific negatives.

### Secondary substrate: SkillEvolBench

First-party SkillEvolBench snapshot provides a real learning block, `SkillAuthor`, frozen T4–T6 deployment and within-env replays. It is valuable as a second substrate, but its first-party Harbor configuration fixes `n_attempts=1`; a clean acting-compute manipulation would require an additional agent-level control or a new wrapper. Therefore it is not the first F1 substrate.

## 7. F0 execution invariants

Before any scientific provider call:

- exact MindMemOS source commit and source hashes above are frozen;
- exact initial `SKILL.md` hash is frozen;
- task order/seed and task subset are frozen before outcomes;
- `U` (skill evolution implementation and prompts) is identical across arms;
- verifier and scoring semantics are identical across arms;
- acting model identity is identical across arms;
- only `max_turns` changes between L and H during evolution;
- frozen evaluation uses the same acting model and `max_turns=L` for every learned skill;
- the shadow arm uses the same task input and pre-task skill state as the paired high-C acting rollout;
- shadow rollout does not serve the user and does not mutate skill state by itself;
- hardmine policy is frozen before scientific outcomes;
- all model/provider calls use the approved Ark Plan route when an Ark-backed adapter is used;
- each call/trajectory/evolution batch persists raw receipt + CSV/JSONL + atomic checkpoint before proceeding;
- resume executes missing units only;
- no outcome-driven endpoint retention or expansion.

## 8. Kill / downgrade rules

Kill the R17 Compute Shielding thesis if any decisive condition holds on a qualified substrate and planned replication:

1. no acting benefit: `R_online(H) <= R_online(L)`;
2. no shielding reversal: frozen skill quality is monotone non-decreasing with evolution-time compute;
3. low-C shadow feedback does not improve frozen skill relative to `H/H`;
4. failure visibility/type distribution does not materially change across L/H;
5. the apparent effect is explained by unequal task stream, model identity, verifier, updater, total evolution opportunities, or evaluator compute;
6. a simple hard-mining/reweighting control fully matches shadow feedback, in which case the strong missing-counterfactual-information claim is rejected and the result is downgraded to ordinary feedback weighting/curriculum;
7. the effect appears only after selecting tasks or failure types based on observed outcomes.

R16 remains untouched unless the new child passes its own scientific gates.

## 9. Rollback point

If R17 fails, retain R16 as the canonical E2 paper. Do not rewrite R16 claims to imply Compute Shielding. Preserve R17 outcomes as negative research memory and failure assets.
