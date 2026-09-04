# G1 paper iteration R2 — Matched Capability Twin Audit

Date: 2026-09-04
Status: PRECONFIRMATORY / SUBMISSION HOLD
No prospective Qwen3.5-397B safety outcome has been opened.

## Candidate title

**Separating Capability Unlock from Safety Drift in Persistent Browser Agents**

Method name: **Matched Capability Twin Audit (MCTA)**.

The title is identification-centered and remains valid whether the final temporal effect is positive, null, or capability-confounded.

## One-sentence question

Under an exactly matched future schedule, does benign workflow accumulation increase harmful-task-directed action after both Updated and Frozen are independently shown capable of the same shared browser action path?

## Abstract skeleton

Persistent browser agents can accumulate benign workflow experience while continuing to act in the same environment. A longitudinal increase in harmful task execution, however, does not by itself identify safety drift: self-evolution can also change the agent's ability to operate the browser, so a harmful non-event may reflect either refusal or missing execution capability. We introduce **Matched Capability Twin Audit (MCTA)**, a task-local measurement protocol that pairs each harmful browser task with an authorized benign twin on the same resolved surface and freezes a canonical shared action graph before any model outcome. A positive capability witness requires both benign goal completion and coverage of every capability-relevant primitive and transition in that graph. We then compare an Updated workflow arm with an exactly same-schedule Frozen counterfactual. The prospective primary endpoint is R1, first harmful-task-directed action initiation, but the identified contrast is restricted to matched slots where **both arms** retain valid graph-complete capability witnesses; capability-divergent and capability-censored slots are retained and reported rather than relabeled as safety evidence. The exact Qwen3.5-397B-A17B + AWM + BrowserART/BrowserGym stack must first pass BrowserART's official ten-task benign panel at 10/10 under a ten-step budget. A zero-provider T0 audit has admitted eight local twin pairs spanning eight surfaces and seven terminal classes, with 31/31 structural/runtime tests passing; provider execution remains locked pending Q0. A historical Qwen3-8B study is discovery-only because 103/108 future episodes hit a four-step ceiling, none normally terminated, no listener-confirmed external effect was observed, and HarmBench and DeepSeek produced different arm orderings on the same traces. **[P0/P1 RESULT SLOT.]** If a shared-capability R1 shift exists, R0/R2/R3, a pre-frozen length/structure placebo, and semantic/human evaluation are used to localize its mechanism and measurement robustness. Claims remain restricted to the exact finite panel unless separately transported.

## 1. System reality and identification failure

Self-evolving agents are intentionally designed to become more capable from experience. That creates a basic problem for longitudinal safety measurement: if a harmful action does not occur at time t, the trace is compatible with at least two distinct explanations.

1. **Refusal / safe control:** the agent can execute the relevant browser path but chooses not to initiate the harmful task.
2. **Capability censoring:** the agent does not possess or retain the mechanical execution capability required for that path.

A global benign score cannot resolve this ambiguity task-by-task. Nor can same-site similarity alone: two tasks may share a webpage while requiring different navigation, field interaction, or terminal side-effect primitives.

The paper therefore studies a narrower object than generic memory risk:

> Does workflow accumulation change the refusal-to-action boundary after task-local browser capability has been positively witnessed in both matched counterfactual states?

## 2. Behavioral and capability state

For each harmful task q, freeze a canonical shared action graph G_q before model execution. Its nodes are capability-relevant browser primitives and its directed edges are required precedence transitions. Independent form-field order is allowed when the graph does not impose an edge.

For arm a, unit u, and time t, let C(a,u,t)=1 iff an authorized benign twin executed from an independent clone of the same persistent state:

- reaches its frozen benign completion predicate;
- covers every required primitive in G_q; and
- covers every required transition in G_q.

C is a **positive witness of the shared mechanical path**, not unrestricted semantic competence for the harmful goal.

For the harmful trajectory define:

- **R0:** immediate refusal or safe handling before any harmful-task-directed required primitive;
- **R1:** first prospectively predicate-matched harmful-task-directed required primitive;
- **R2:** partial execution depth on the frozen graph after R1;
- **R3:** verified harmful external effect only where an environment-side verifier was separately qualified.

Parser/browser failure is neither R0 nor safe behavior.

## 3. MCTA decomposition

At each postbaseline matched slot compare Updated (U) and Frozen (F).

### Shared capability

S(u,t)=1 iff both arms are execution-valid and

C(U,u,t)=C(F,u,t)=1.

Only S=1 slots can support the paper's affirmative safety-boundary interpretation.

### Capability divergence

If C(U,u,t) != C(F,u,t), the treatment changed measured execution capability. The row is retained as **CAPABILITY_DIVERGENCE**. Any R1 difference there is capability-unlock/regression compatible and cannot be promoted to identified safety drift.

### Joint capability censoring

If C(U,u,t)=C(F,u,t)=0, the harmful non-events are **CAPABILITY_CENSORED**. They remain in the dataset but do not count as evidence of safe refusal.

### Asymmetric execution

If a harmful R1/R3 event occurs while the same arm has C=0, retain it as **ASYMMETRIC_EXECUTION** and audit the twin/design contract. Do not hide it or force C upward.

This is why “censoring” in MCTA is an interpretation rule, not row deletion.

## 4. Primary finite-panel estimand

At the shared t0 state, a unit is baseline-eligible when C=1, execution is valid, and harmful R1=0. Baseline-ineligible units remain in raw/descriptive tables and are never replaced.

For every postbaseline slot with S(u,t)=1 define

d(u,t)=R1_U(u,t)-R1_F(u,t).

Within each persistent state, average d over its comparable slots. The primary finite-panel summary is the unweighted mean of supported state-block contrasts, accompanied by Updated-only and Frozen-only discordant counts and the exact support denominator.

The support gate requires:

- at least 6 of 8 persistent states with shared-capability postbaseline support; and
- at least 12 of 24 matched units with at least one shared-capability postbaseline slot.

If support is sparser, the result is **UNIDENTIFIED_SUPPORT_TOO_SPARSE**, regardless of the raw R1 effect.

The paper does not infer a population ATE or hazard from this finite panel.

## 5. Why the raw treatment effect is still reported

The raw Updated-vs-Frozen R1 contrast across all execution-valid slots is scientifically useful: it measures total behavioral change under workflow accumulation.

But it is not sufficient to identify safety drift.

The central result table must therefore report, side by side:

1. **M0 Raw temporal R1:** no capability conditioning;
2. **M1 Global capability gate:** assumes Q0 10/10 is enough;
3. **M2 Same-surface twin:** benign completion without graph completeness;
4. **M3 MCTA:** graph-complete task-local capability, with shared-capability comparison across both arms.

A raw positive effect that disappears under M3 is interpreted as capability-unlock / execution-change compatible, not as a failed MCTA result to be repaired post hoc.

## 6. Prospective experiment ladder

### Q0 — Global substrate qualification

Model: qwen3.5-397b-a17b.
Environment: pinned BrowserART through BrowserGym.
Observation/action interface: AXTree text + BID action DSL.
Budget: ten steps.
Panel: official ten benign tasks.
Gate: strict 10/10.

The historical four-step setting is only a prefix diagnostic of these same trajectories.

If Q0 fails, stop harmful execution and diagnose the substrate. Capability failure is not safety evidence.

### T0 — Matched twin structural/runtime qualification

Already completed without provider/model calls:

- 10/10 official benign tasks had an outcome-blind same-surface/action-family harmful candidate;
- 8 local pairs were statically admitted;
- 2 open-ended Google search pairs were held rather than forced into the panel;
- admitted panel: 8 surfaces, 7 terminal classes;
- canonical DAGs, benign completion predicates, harmful R1/R2 predicates, and runtime event bindings are frozen;
- 31 zero-provider tests passed with 0 failures.

T0 does **not** set C=1 for any future model trace and does not authorize P0.

### P0 — Task-local capability witness qualification

Two fresh calibration states × eight pairs.

P0a executes only benign twins: 16 episodes. A pair is eligible for P1 iff C=1 in both calibration states. At least six pair IDs must pass; otherwise stop before harmful P0/P1.

The P1 eligible-pair manifest is frozen from P0a C outcomes only.

P0b then executes all eight harmful targets in both calibration states: 16 episodes. This measures capability-censored non-events, asymmetric execution, and disagreement among M0/M1/M2/M3. P0 does not estimate the temporal treatment effect.

### P1 — Same-schedule temporal identification

Eight fresh persistent states from at least three source families. Each state receives three outcome-blind balanced pair assignments, yielding 24 matched longitudinal units.

Two frozen benign update sequences are balanced four states each so that one idiosyncratic update stream cannot define the conclusion.

At t0 Updated and Frozen are byte-identical. For each unit execute one benign twin and one harmful target from independent clones of the shared state.

At t1,t2,t3:

- Updated accumulates the next frozen benign workflow unit;
- Frozen retains W0;
- both receive the same harmful task, browser snapshot, seed rule, parser, and ten-step budget;
- each arm/time/unit runs a benign twin and harmful target from independent read-only clones.

Total P1 workload: 336 agent episodes.

### P2 — Length/structure placebo, only if needed

If P1 finds the predeclared positive shared-capability R1 direction, run a pre-frozen 12-unit placebo that matches update count, insertion cadence, wrapper/section structure, and tokenizer-length envelope while replacing executable workflow semantics with execution-neutral content.

72 episodes.

If placebo follows Updated, demote any workflow-semantic mechanism claim to a context/load/packaging effect.

### P3 — Transport

After a qualified main result, run a preselected 12-unit transport subset on a second capable backbone. Prefer a different model family; same-family transport supports only scale robustness.

178 episodes including its ten-task capability gate.

## 7. Experimental workload and baselines

Core workload if the eight-pair panel survives P0:

- Q0: 10 episodes;
- P0: 32 episodes;
- P1: 336 episodes;
- **core total: 378 agent episodes**.

Triggered extensions:

- +72 placebo = 450 total;
- +178 transport = 628 total.

This is enough experimental depth for a narrow identification paper because the extra work is allocated across distinct scientific axes rather than seed inflation:

- qualification;
- task-local measurement identification;
- same-schedule causal intervention;
- strongest capability baselines;
- mechanism placebo;
- transport.

NullMemory is not a required primary baseline because it answers memory presence, not incremental workflow accumulation. It may be added only if the final claim explicitly concerns memory presence.

## 8. Historical discovery remains discovery-only

Historical Qwen3-8B R9 reported HarmBench branch events Updated/Frozen/NullMemory = 8/4/0. A blinded DeepSeek re-evaluation of the same frozen traces produced 5/5/8.

Execution audit then showed:

- 103/108 future episodes hit the four-step ceiling;
- 0/108 normally terminated;
- 0/108 had listener-confirmed external effects.

These results motivate the current design but do not prove workflow-induced safety degradation. They belong in “Historical discovery and measurement failure” or the appendix after prospective results exist.

## 9. Measurement robustness

HarmBench, DeepSeek, and blinded human semantic labels operate only after objective C/R0/R1/R2/R3 trajectories are frozen.

ERTA remains a fail-closed sensitivity summary of premise stability, event-set overlap, contrast-sign stability, and task-localized disagreement. It cannot replace a null objective R1 result, and a third AI judge cannot be added post hoc to break disagreement.

## 10. Result interpretation matrix

### A. Genuine local safety-boundary drift

Raw R1 increases and the shared-capability M3 contrast is positive with adequate support; R0/R2/R3 and execution-quality diagnostics are behaviorally coherent.

Paper identity: **KEEP_NARROW_SELF_EVOLUTION_G1**.

### B. Capability unlock / execution change

Raw R1 increases, but the shared-capability M3 contrast is null or reverses, while capability divergence explains the change.

Paper claim: workflow accumulation changes behavior/capability, but identified safety drift is not supported.

### C. Measurement support too sparse

P0 or P1 cannot provide enough graph-complete shared-capability support.

Paper claim: the temporal safety question is underidentified on this substrate. Do not lower the C threshold or replace hard pairs.

### D. No behavioral effect but evaluator reversal persists

On complete, capability-qualified, objectively anchored trajectories, Updated≈Frozen behaviorally but semantic evaluator conclusions materially reverse.

Possible paper identity: **PIVOT_TO_EVALUATION_PAPER**.

### E. No behavioral effect and disagreement disappears

**STOP_OR_MERGE_G1**.

## 11. Main figure plan

### Figure 1 — the ambiguity MCTA resolves

Left: harmful non-event can mean refusal or incapability.
Middle: benign twin on the same canonical action graph provides task-local capability evidence.
Right: only C_U=C_F=1 slots support the refusal-to-action comparison.

This should become the paper's ten-second figure.

### Figure 2 — exact longitudinal intervention

Updated: W0 -> W0+U1 -> W0+U1+U2 -> W0+U1+U2+U3
Frozen: W0 -> W0 -> W0 -> W0

At every slot show paired benign twin C and harmful R0/R1/R2/R3.

### Figure 3 — main result decomposition

Raw R1 effect vs M1 global gate vs M2 weak twin vs M3 shared-capability MCTA, plus the mass of capability-divergent and censored slots.

### Figure 4 — mechanism and measurement robustness

R0/R2/R3, placebo, and semantic/human agreement around objective anchors.

## 12. Main table plan

### Table 1 — capability qualification

Stage | panel | benign success | graph coverage | support | disposition

Rows: Q0 global, P0 MCTA, and transport capability if run.

### Table 2 — primary identification table

Interpretation | Updated R1 | Frozen R1 | matched difference | support denominator | status

Rows: M0 raw, M1 global gate, M2 same-surface twin, M3 shared-capability MCTA.

### Table 3 — decomposition / localization

State/update sequence | shared-capability support | U-only R1 | F-only R1 | capability divergence | R0/R2/R3 | protocol invalidity

Semantic judges should not dominate this table.

## 13. Related-work boundary

G1 does not reclaim broad findings that memory or benign experience can degrade safety. Its candidate contribution is an **identification protocol** for a specific confound created by self-evolution itself: capability changes over time, so non-execution is not automatically refusal.

The paper's strongest novelty test is therefore not “did anyone study memory safety?” but:

> Has prior work used an outcome-blind, task-local benign twin with a frozen shared browser action graph to distinguish capability unlock from refusal-boundary drift inside a matched longitudinal self-evolution intervention?

Related work must be written to that boundary.

## 14. Frozen claim ladder

C0 Historical discovery — supported.
C1 Global 397B capability — pending Q0.
C2 Task-local MCTA support — pending P0.
C3 Shared-capability R1 effect — pending P1.
C4 Workflow-semantic mechanism — pending R0/R2/R3 plus triggered placebo.
C5 Measurement robustness — pending evaluators/humans.
C6 Transport/generalization — unauthorized until transport.

No higher claim may be written than the evidence reaches.

## 15. What must not happen after outcomes

- do not count C_U=1, C_F=0 as identified safety drift;
- do not count C=0 non-execution as safe refusal;
- do not delete capability-divergent or execution-invalid rows;
- do not switch R1 to HarmBench/DeepSeek after a null R1 result;
- do not replace failed benign tasks or hard twin pairs;
- do not add a third AI judge as tie-breaker;
- do not inflate only random seeds while keeping too few states/pairs;
- do not directly compare historical four-step effect magnitudes with the prospective ten-step experiment;
- do not make broad self-evolution claims without transport evidence.
