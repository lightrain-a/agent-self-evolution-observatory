# B1 R77 — Why do the same 4 Llama tasks flip under provenance?

Date: 2026-09-05  
Status: POST-HOC MECHANISM DIAGNOSTIC COMPLETE  
Paper: `D2-PAPER-FAILURE-MEMORY-PROVENANCE`

## Question

R75 showed that Llama's aggregate terminal success is 17/32 under both historical arms, but the successful task IDs differ:

- content-only-only successes: 125, 327;
- truthful-provenance-only successes: 136, 193.

R76 then reran those four task pairs under the exact same local Llama substrate with `temperature=0`, `do_sample=false`. All four A/B terminal-flip patterns reproduced.

R77 asks what mechanism can produce a repeatable terminal flip when ordinary sampling noise is absent.

## M1 — locate the first real executable divergence

| Task | First normalized-action divergence | Shared external transitions before divergence | History identical at target? |
|---|---:|---:|---|
| 125 | action index 5 | 5 | yes |
| 136 | action index 1 | 1 | no; assistant wording diverged earlier |
| 193 | action index 0 | 0 | yes |
| 327 | action index 1 | 1 | no; assistant wording diverged earlier |

The distinction is important:

- 125 and 193 permit a clean same-transcript prompt comparison at the decision point.
- 136 and 327 already contain treatment-induced differences in the assistant's own prior text even though the external action/state is initially the same. Two natural-history anchors are therefore retained.

## M2A — exact-runtime greedy replay fidelity

The first logit probe attempt was invalidated because its tokenization path did not exactly match the historical runtime. R77 therefore reran the target responses open-loop using the exact R59/R61 construction:

`apply_chat_template(tokenize=False) -> tokenizer(text) -> model.generate(do_sample=false)`

with the historical attention mask and frozen Meta-Llama-3.1-8B-Instruct weights.

Eight natural target responses were replayed:

- 4 tasks × A/B;
- 8/8 normalized executable actions match the historical branch action;
- 0 OS/environment interactions.

Only after this gate passed were native replay token IDs used for the logit analysis.

## M2B — same-state logit probe

At each frozen transcript state, only the system-prompt provenance surface is changed. The probe compares the two faithfully replayed A/B branch continuations.

### Task 125 — fragile direct decision-boundary flip

At the first branch token:

- A prompt: log-odds(B-like minus A-like) = `-0.015625`;
- B prompt: `+0.015625`.

The sign flips under the prompt swap, but the margin is extremely small.

Interpretation: this is a narrow deterministic tie-break. Under greedy decoding the small provenance perturbation is sufficient to choose the other branch; under nonzero sampling it should be fragile.

### Task 193 — stronger direct decision-boundary flip

At the first branch token:

- A prompt: `-0.0625`;
- B prompt: `+0.5625000596`.

The sign flips and the shift is about `+0.625 nat`.

Interpretation: provenance produces a substantially stronger direct local policy shift than on task 125.

### Task 136 — transcript/self-conditioning dominates current prompt

Using the A-history anchor:

- A prompt: `-1.03125`;
- B prompt: `-1.015625`.

Using the B-history anchor:

- A prompt: `+3.34375`;
- B prompt: `+3.28125`.

Within a fixed history, changing the current system prompt barely moves the boundary and never changes its sign. Changing the prior assistant transcript flips the branch preference by several nats.

Interpretation: provenance first changes the model's own prior text; those self-generated words enter the next context and dominate the later action choice.

### Task 327 — weaker history-anchor sensitivity

A-history anchor:

- A prompt: `-0.140625`;
- B prompt: `-0.171875`.

B-history anchor:

- A prompt: `+0.046875`;
- B prompt: `+0.09375`.

Again, the branch sign follows history more than the current provenance prompt, although the margins are much smaller than task 136.

## M3 — branch-response mediation

R77 then asks whether the first divergent branch response is sufficient to redirect the closed-loop terminal outcome.

Each run:

1. resets a fresh OSInteraction Docker environment;
2. replays the native historical pre-divergence assistant responses;
3. requires each actual OS observation before the target to match the historical native prefix;
4. injects the opposite arm's exact-greedy natural branch response at the first executable divergence;
5. resumes freely under the original native system prompt.

This swaps the full assistant branch response (reasoning + action), not action alone.

| Task | Historical A/B | A prompt + B branch | B prompt + A branch | Interpretation |
|---|---|---|---|---|
| 125 | success / fail | **fail** | **success** | full bidirectional mediation |
| 136 | fail / success | **success** | **fail** | full bidirectional mediation |
| 193 | fail / success | **success** | **success** | B branch can rescue A; B condition can recover after forced A branch |
| 327 | success / fail | **success** | **success** | first divergence alone is not sufficient for the historical B failure |

Thus terminal flips are not all generated by the same causal geometry:

- 125: direct narrow boundary shift + branch-mediated closed-loop amplification;
- 136: prior-text self-conditioning + branch-mediated amplification;
- 193: stronger direct shift + asymmetric recovery;
- 327: prior-text/history sensitivity, but the first divergent branch is not terminally sufficient; later closed-loop accumulation is required.

## M4 — analytic temperature sensitivity

Temperature does not change the raw logits. R77 therefore first asks, analytically, how the observed two-candidate branch margin would translate into sampling probability under temperature scaling:

`P(B | {A,B}, T) = sigmoid((z_B - z_A)/T)`.

This is a two-candidate branchpoint calculation, not a full-response sampling experiment.

### Task 125

| T | P(B) under A prompt | P(B) under B prompt | shift |
|---:|---:|---:|---:|
| 0.05 | 0.423 | 0.577 | +0.155 |
| 0.10 | 0.461 | 0.539 | +0.078 |
| 0.20 | 0.480 | 0.520 | +0.039 |
| 0.50 | 0.492 | 0.508 | +0.016 |
| 1.00 | 0.496 | 0.504 | +0.008 |

The deterministic greedy flip is real but sampling-fragile.

### Task 193

| T | P(B) under A prompt | P(B) under B prompt | shift |
|---:|---:|---:|---:|
| 0.05 | 0.223 | 1.000 | +0.777 |
| 0.10 | 0.349 | 0.996 | +0.648 |
| 0.20 | 0.423 | 0.943 | +0.521 |
| 0.50 | 0.469 | 0.755 | +0.286 |
| 1.00 | 0.484 | 0.637 | +0.153 |

Task 193 retains a much larger provenance-induced branch shift under sampling.

For 136/327, current-prompt temperature is not the main mechanism because branch sign is primarily determined by the already-diverged transcript history.

## Mechanism statement supported by R76 + R77

The current evidence supports a heterogeneous mechanism:

> Explicit provenance can alter local policy either directly at a narrow decision boundary or indirectly through self-conditioned transcript differences. These local changes then enter a closed-loop environment, where they may be amplified into a terminal flip, recovered from, or overridden by later interaction depending on the task.

The evidence does **not** support the simpler statement that the four flips are ordinary temperature/sampling noise.

## What R77 does not prove

1. These four tasks were selected post hoc because they were historically terminally discordant.
2. R77 does not estimate how common any mechanism is over the full 32-task or future 66-task population.
3. M3 swaps a full branch response, not the action alone.
4. The hypothesis that these are capability-boundary tasks remains plausible but unisolated; a stronger-backbone comparison would be needed for a causal capability claim.
5. R77 does not modify R72/R73's 321-run prospective experiment, primary statistics, or execution authority.

## Recommended next step

Do **not** run a broad temperature grid.

If an empirical stochastic follow-up is later needed, prioritize only tasks 125 and 193:

- 125 tests whether a deterministic tie-break dissolves under sampling;
- 193 tests whether a stronger provenance-induced branch shift remains observable under sampling.

A broad 4-task × many-temperature × many-seed closed-loop sweep would add much more cost than mechanism information at this stage.
