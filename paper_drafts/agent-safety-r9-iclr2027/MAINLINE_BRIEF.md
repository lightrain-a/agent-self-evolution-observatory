# R9 full-manuscript mainline brief

## Leading advantage

The paper gives an exact, branch-level account of how much a clean current safety panel misses when a persistent browser agent is followed into a declared future. Its useful object is not a population hazard estimate or a memory-causality claim, but the first-violation event time and the evaluation depth required to observe it.

## Chosen battlefield

- One frozen Qwen3-8B browser-agent runtime with Agent Workflow Memory.
- BrowserART tasks through BrowserGym, scored by the frozen HarmBench classifier.
- Four current-safe persistent states in map and reddit strata.
- Three common branches per state and a three-step held-out future.
- Finite descriptive case study: 12 current qualification episodes and 36 future episodes.

## Central claim

Within this frozen web-agent case study, a 12/12 current non-violation panel did not certify the evaluated future: first violations appeared in 8/12 branches, and six of those first appeared only at step 2.

## Evidence spine

1. Current panel: 0/12 violations across all four selected states.
2. Future trajectory: 11/36 violation episodes; first event in 8/12 branches and 3/4 states.
3. Evaluation depth: 1/12 event branches visible by step 1, 7/12 by step 2, and 8/12 by step 3.
4. State localization: map pair 2-versus-0 event branches; reddit pair 3-versus-3.
5. Strongest alternative: the joint design does not separate update from held-out schedule, so the paper excludes update-alone causal language.
6. Current-source collision: longitudinal memory safety and NullMemory causal controls are already established by Al-Tawaha et al. (2026); R9 is positioned as a bounded action-taking web-agent case study, not the origin of longitudinal safety evaluation.

## Claim boundary

Supported: the current static pass failed as a guarantee over this exact joint update-plus-schedule future, and deeper future evaluation exposed additional first-event branches.

Not supported: a causal update effect, a general statement about static safety evaluation, a population hazard, a new longitudinal-memory-safety paradigm, or HarmBench as ground truth.

## Section-level change map

1. Introduction: sharpen the certificate-vs-observation gap and acknowledge the closest work.
2. Setting: distinguish predictive sufficiency from causal attribution.
3. Protocol: add a full workflow diagram and formal event-time/reporting definitions.
4. Setup: document states, strata, branches, horizon, and evaluator separately from protocol governance.
5. Results: organize around static contrast, evaluation depth, state localization, and comparison to the static-only lens.
6. Related work: add static agent-safety benchmarks and the direct longitudinal-memory collision.
7. Discussion: state what the case study adds and why it remains below full-paper evidence authority.
8. Appendix: complete claim boundary, finite branch table, numeric derivations, and reproducibility map.

## Demotions

Hashes, recovery history, support failures, gate states, and queue/authorization details remain in artifacts. The no-update control remains a recorded reopen condition, not a result.
