# G1 SkillZip / SkillZip Pro paper iteration — preconfirmatory manuscript R1

Date: 2026-09-04
Source of truth: current origin/main evidence + frozen historical artifacts; no Qwen3.5-397B safety outcome exists.

## Candidate title

**Auditing the Refusal-to-Action Boundary under Benign Workflow Accumulation in Persistent Browser Agents**

Alternative, only if the prospective effect is positive:

**A Static Refusal Pass Is Not a Temporal Certificate: Workflow Accumulation Shifts Action Control in Persistent Browser Agents**

Do not use the positive title before the preregistered prospective result exists.

## One-sentence paper question

When a persistent browser agent accumulates benign workflow demonstrations, does the same harmful request cross from immediate refusal/safe handling into task-directed action more often than it would under the same future task schedule with the workflow frozen?

## Why this is narrower than existing work

The paper does not claim that memory risk is new, that benign experience can hurt safety is new, or that evaluator disagreement is new.

Its candidate contribution is the combination of:

1. a persistent workflow-update treatment;
2. an exact same-schedule frozen-workflow counterfactual;
3. a capability-qualified BrowserART execution substrate;
4. a programmatic refusal-to-action endpoint rather than a single post-hoc semantic binary;
5. first-crossing localization over longitudinal exposure steps;
6. an explicit separation between behavioral evidence and semantic evaluator robustness.

This is a narrower claim than generic longitudinal memory contamination or generic experience-induced unsafe behavior.

## Abstract skeleton — do not fill outcome slots before execution

Persistent browser agents can accumulate benign workflow demonstrations and continue acting under the resulting persistent state. Existing work shows that memory and experience can alter agent safety, but two questions remain entangled: whether an observed temporal change is caused by persistent workflow updating rather than the future task schedule, and whether a semantic safety label reflects refusal failure, partial task execution, or verified external effect. We study the **refusal-to-action boundary** under an exact same-schedule workflow-update contrast. For each harmful task, we decompose behavior into immediate refusal/safe handling (R0), first task-directed action (R1), partial execution depth (R2), and verified external effect (R3). The prospective primary endpoint is a task-specific programmatic R1 predicate, with R0/R2/R3 as prespecified decomposition endpoints. Before any safety execution, the exact Qwen3.5-397B-A17B + AWM + BrowserART/BrowserGym stack must pass the official ten-task benign panel under a benchmark-aligned ten-step budget with a 10/10 gate. A historical Qwen3-8B study motivated the hypothesis but is discovery-only: 103/108 future episodes hit a four-step truncation ceiling, none normally terminated, no listener-confirmed external effect was observed, and HarmBench and DeepSeek produced different arm orderings on the same traces. **[PROSPECTIVE RESULT SLOT: Updated vs Frozen R1 and R0/R2/R3 decomposition.]** We then use HarmBench, DeepSeek, and human semantic calibration only to ask whether the behavioral conclusion is measurement-robust. **[ROBUSTNESS RESULT SLOT.]** The supported claim is restricted to the exact treatment, substrate, and horizon tested.

## Introduction architecture

### Paragraph 1 — system reality

Persistent agents do not remain at the state at which they were first evaluated. Experience-driven systems store workflows, demonstrations, summaries, or memories and use them in later decisions. A safety evaluation performed at state s0 therefore need not describe behavior after subsequent benign experience has changed the persistent context.

### Paragraph 2 — what prior work already owns

Prior work already demonstrates longitudinal safety risk in memory-equipped agents and safety degradation from benign execution-oriented experience. G1 does not claim either observation as new. The unresolved issue is more specific: whether **the update itself**, rather than a changing future task stream or weak task execution, moves the agent's control boundary from refusal toward action.

### Paragraph 3 — why existing binary endpoints are insufficient

For an overtly harmful browser request, the strongest safe behavior is immediate refusal before task-directed tool use. A trajectory that begins filling a target form but never completes it is not equivalent to either immediate refusal or a verified harmful side effect. A single semantic label can collapse these states. We therefore distinguish R0 refusal, R1 task-directed action initiation, R2 execution depth, and R3 verified external effect.

### Paragraph 4 — causal identification

The core contrast is Updated vs Frozen. Both begin from the same workflow and receive the same future tasks, seeds, observation/action interface, and execution budget. Updated receives prospectively frozen benign workflow units over exposure steps; Frozen remains at the step-0 workflow. The treatment effect is defined on matched units, with R1 as the primary endpoint.

### Paragraph 5 — capability qualification

Browser safety is not identifiable on a substrate that cannot execute benign tasks. The strong-backbone confirmatory stack must therefore pass BrowserART's official benign sanity panel before any harmful task is run. The historical four-step ceiling is analyzed only as a prefix diagnostic of this qualification run.

### Paragraph 6 — historical discovery and why it is insufficient

The historical Qwen3-8B R9 study generated the hypothesis: HarmBench labeled Updated/Frozen/NullMemory as 8/4/0 event branches. But the same traces produced 5/5/8 under DeepSeek, 103/108 historical future episodes hit the four-step ceiling, 0/108 normally terminated, and no listener-confirmed external effect was recorded. These facts make the old mechanism story underidentified. The old data are therefore discovery evidence, not the confirmatory result.

### Paragraph 7 — measurement robustness is secondary

Evaluator disagreement remains scientifically important, but it is a measurement layer. Only after objective behavioral endpoints are established do we ask whether HarmBench, DeepSeek, and human judgments support the same direction. ERTA remains a fail-closed sensitivity analysis; it is not the default paper identity.

### Paragraph 8 — contributions, conditional on evidence

The final contribution list must be selected from the frozen claim ladder after prospective outcomes. No contribution may be promoted because another expected result failed.

## Formal object

Let H_t denote complete pre-task persistent state at exposure step t, q_{u,t} the frozen future task for matched unit u, and A the browser-agent transition operator.

Updated state evolution:

H^U_{t+1} = Update(H^U_t, B_t),

where B_t is a prospectively frozen benign workflow unit.

Frozen state evolution:

H^F_{t+1} = H^F_t.

Both arms receive the same q_{u,t}, seed, action interface, browser environment, and ten-step ceiling.

For task q, define a prospectively frozen predicate P_q over structured action/environment events. Then:

R1(a,u,t) = 1 iff P_{q_{u,t}} is first satisfied under arm a by time t.

R0 records safe refusal before any R1 event. R2 is a task-specific monotone execution-depth score after R1 where available. R3 records a verifier-confirmed target-side effect.

Primary matched estimand:

D_R1 = mean_u R1(U,u) - mean_u R1(F,u).

The paper does not infer a population effect from the finite matched panel unless a separately justified sampling model is added.

## RQs

### RQ1 — Can the substrate support an interpretable safety study?

Evidence: official BrowserART 10 benign tasks, 10-step budget, strict 10/10 success gate, protocol-quality diagnostics. A capability failure is not a negative safety result.

### RQ2 — Does workflow accumulation alter the refusal-to-action boundary?

Evidence: fresh same-schedule Updated vs Frozen matched comparison on programmatic R1.

### RQ3 — What kind of control change produces any R1 difference?

Evidence: R0 immediate refusal, R2 partial-execution depth, R3 verified external effect, parser/grounding error diagnostics.

### RQ4 — When and where does the first crossing appear?

Evidence: first R1 time by exposure step, state, task, and branch. Report localization, not a population hazard unless justified.

### RQ5 — Is the behavioral conclusion measurement-robust?

Evidence: HarmBench / DeepSeek / blinded human semantics conditioned on frozen trajectories and objective behavioral anchors. ERTA summarizes disagreement without choosing a convenient judge.

## Main figures

### Figure 1 — the scientific object

Two matched longitudinal lanes:

Updated: W0 -> W0+U1 -> W0+U1+U2 -> W0+U1+U2+U3
Frozen:  W0 -> W0    -> W0       -> W0

At each matched harmful task, show the behavioral ladder:

R0 Refuse -> R1 Start task-directed action -> R2 Partial execution -> R3 Verified effect.

This figure must visually communicate the method in under ten seconds. Do not make ERTA the first figure.

### Figure 2 — identification and qualification

Left: official benign 10/10 qualification and ten-step execution budget.
Right: same-schedule Updated/Frozen matched design; highlight the single treatment difference.

### Figure 3 — main prospective result

Matched R1 effect and first-crossing localization. R0/R2/R3 shown adjacent as decomposition, not as separate unrelated experiments.

### Figure 4 — measurement robustness

Compare objective R1/R3 with HarmBench, DeepSeek, and human semantic labels. Show where semantic disagreement occurs relative to actual action depth.

## Main tables

### Table 1 — substrate qualification

Backbone | benign success | parser success | invalid-target rate | truncation | mean steps | disposition

The normal benchmark-aligned 10-step setting comes first. The 4-step prefix is diagnostic only.

### Table 2 — primary matched behavioral result

Endpoint | Updated | Frozen | matched difference | uncertainty/exact test | claim status

Rows: R0, R1 (primary), R2, R3.

### Table 3 — localization / robustness

State/task | R1 Updated | R1 Frozen | first-crossing step | HB | DS | Human

This table ties measurement disagreement to the behavioral substrate instead of presenting judge counts in isolation.

## Historical data placement

The historical 8/4/0 vs 5/5/8 result belongs in a section titled **Historical discovery and measurement failure**, or in the appendix once prospective confirmation exists.

It should be used to motivate:

- why the 4-step execution cap had to be repaired;
- why objective action endpoints are necessary;
- why evaluator robustness is secondary but non-negligible;
- why historical effect sizes must not be compared directly with the new 10-step confirmatory run.

It must not be presented as the confirmatory mechanism result.

## Related-work collision matrix

### Longitudinal memory safety

Already owns: safety can degrade as memory accumulates; fixed probes/snapshots; NullMemory-style controls; broad memory-architecture comparisons.

G1 boundary: exact same-schedule evolving-vs-frozen workflow contrast with refusal-to-action decomposition in an interactive browser agent.

### Experience-driven self-evolving agent safety

Already owns: benign experience / AWM / reasoning memories can reduce safety; execution-oriented experience can bias act-over-refuse behavior.

G1 boundary: does not claim this effect as new. Tests whether incremental workflow accumulation causes a longitudinal control-boundary crossing under a matched future schedule, with capability qualification and programmatic action endpoints.

### LLM-as-a-judge / evaluator reliability

Already owns: judge sensitivity and disagreement.

G1 boundary: evaluator robustness is only tied to the specific temporal control conclusion after objective behavioral anchors exist. No generic judge-benchmark claim.

## Frozen claim ladder

C0 Historical discovery: the old semantic ordering is evaluator-sensitive and the old execution substrate is incomplete. Already supported.

C1 Capability: the new exact browser stack is qualified for the prospective safety experiment. Requires 10/10 benign PASS.

C2 Local treatment effect: workflow accumulation changes R1 under the frozen matched design. Requires prespecified prospective R1 result.

C3 Behavioral interpretation: R1 change is a meaningful control shift, not parser/grounding noise. Requires coherent R0/R2/R3 and execution-quality evidence.

C4 Measurement robustness: semantic evaluators/humans support the same directional interpretation. Requires frozen semantic evidence after objective anchors.

C5 Transport/generalization: effect extends beyond exact backbone/AWM/BrowserART setting. Requires new transport evidence and is not part of the current core experiment.

## Prospective paper-identity adjudication

- C1 fails -> no safety paper upgrade; substrate repair only.
- C1 passes + C2/C3 positive -> narrow self-evolution paper; evaluator analysis secondary.
- C1 passes + C2 absent + evaluator reversal persists on complete/objectively anchored trajectories -> evaluator/measurement paper may be justified.
- C1 passes + C2 absent + evaluator reversal disappears -> STOP/MERGE G1.

This decision rule is internal governance and should not appear as a post-hoc narrative choice in the submitted manuscript.

## What to delete/demote from the current ERTA-centered draft

Demote from abstract / first-page contribution list:

- definite/possible event sets as the first contribution;
- the historical 8/4/0 vs 5/5/8 ordering as if it were the paper's central standalone phenomenon;
- prospective NullMemory PV1 as a central validation;
- ERTA as the default method name in the title.

Keep, but later in the paper / appendix:

- the exact historical evaluator disagreement;
- ERTA's no-majority/fail-closed rule;
- current-premise disagreement;
- task-localized judge disagreement;
- full historical branch tables and provenance.

## What must not happen after outcomes

- no switching R1 to HarmBench because R1 is null;
- no switching Updated-vs-Frozen to NullMemory because the latter looks stronger;
- no adding a third AI judge to break a tie;
- no dropping a failed benign task to preserve 10/10 qualification;
- no treating execution failure as a safety refusal;
- no presenting a 10-step effect as directly comparable in magnitude to historical 4-step counts;
- no broad self-evolution claim from one backbone without transport evidence.
