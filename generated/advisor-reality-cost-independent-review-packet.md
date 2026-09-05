# Independent audit packet — Advisor Meeting Reality Support + Resource Ledger

Date: 2026-09-05
Role: fresh independent senior ML/agent-systems research advisor and experimental-program auditor.

## Scope
Audit ONLY two overlays prepared for a 3-hour advisor meeting across nine papers:
1. REALITY SUPPORT: whether cited public systems/work genuinely support the stated real-world premise without overclaiming.
2. RESOURCE LEDGER: whether `AUTHORIZED NOW -> NEXT IF PASS -> CONDITIONAL LATER` correctly separates committed resources from contingent future work and whether any major dependency/cost class is missing.

Do NOT reopen paper scientific conclusions, redesign experiments, demand extra models/benchmarks for appearance, or turn this into nine full paper reviews. Stanford external reviews already exist separately. Recommend changes only if they would materially improve the advisor meeting decision surface.

## Audit criteria
For each paper, return:
- REALITY_SUPPORT: PASS / NARROW / REPLACE_CASE
- RESOURCE_LEDGER: PASS / FIX
- ONE_VERDICT_CHANGING_FIX: `NONE` or one concise fix

Then return:
- PORTFOLIO_REALITY_ISSUE: the single most important cross-paper premise issue, or NONE
- PORTFOLIO_RESOURCE_ISSUE: the single most important resource-accounting issue, or NONE
- MEETING_SURFACE_FIXES: at most 5, only if materially decision-improving
- FINAL_VERDICT: exactly one of `PASS_REALITY_COST_OVERLAY`, `REVISE_REALITY_COST_OVERLAY`

## Portfolio policy
- Nine papers continue by default; this is not an elimination exercise.
- Only `AUTHORIZED NOW` is a current resource commitment.
- `NEXT IF PASS` and `CONDITIONAL LATER` are explicitly contingent and must not be treated as already budgeted.
- API cash, local-GPU opportunity cost, human time, provider/credential dependencies, and calendar latency are separate dimensions.
- Running frozen experiments must not be interrupted based on interim scientific outcome inspection.

## E1 — STRI
Reality support:
- SkillZip (arXiv:2608.11079): self-evolving agents continually accumulate reusable skills/failure fixes; growing skill libraries need maintenance.
- SkillZip Pro (arXiv:2608.30785): production skills as directory bundles with progressive loading/routing boundaries.
- HyperSkill (arXiv:2608.16114): structured skill memory with retrieval ranking, pruning, merging.
Claimed support: dynamic skill libraries, routing/retrieval and selective loading are real system operations.
Does NOT prove: package identity or finite access budget causes STRI instability.
Strongest escape: semantic dedup/canonical IDs or semantic-first retrieval may make package identity irrelevant.
Resources: AUTHORIZED NOW = 0 GPU/API; human submission/signoff. NEXT IF PASS = none for narrow paper. CONDITIONAL = optional V4 first gate ~12-24 hosted trajectories only if explicitly reopened.

## B1 — Failure Memory Provenance
Reality support:
- From Agent Traces to Trust (arXiv:2606.04990): evidence/execution provenance and provenance-bearing memory for explaining later decisions.
- MemoryArena (arXiv:2602.16313): multi-session memory-agent-environment loop; historical actions/feedback reused later.
- Agentic Memory / AgeMem (ACL 2026): agent actively stores/retrieves/updates/summarizes/discards memory.
Does NOT prove: explicit truthful source-outcome field has standalone terminal value beyond identical content.
Strongest escape: prompt-surface sensitivity, implicit failure wording, executor decision boundary.
Resources: AUTHORIZED NOW = 1x local A100-80GB, Qwen stage 189 trajectories, API cash 0. Live operational snapshot 22:20: 31/189 completed, rough remaining ~5.5h if current average holds; no interim scientific analysis. NEXT IF PASS = Llama 132 only under separate authority. CONDITIONAL = later analysis; strong-scale 4D only if future discordance triggers and separately authorized.

## C1 — Stage-Resolved Memory Transport
Reality support:
- MemoryArena: distinguishes memory acquired earlier from later action use.
- MemoryLake on MemoryArena (arXiv:2608.13883): write/retrieval/consolidation/budgeting/prompt assembly as separable backend components.
- From Agent Traces to Trust: process-level provenance/failure localization.
Does NOT prove: C1 exact write->exposure->uptake->endpoint ladder is unique or sufficient standalone.
Strongest escape: simpler end-to-end matched intervention + forced-exposure diagnostic may answer practical question.
Resources: AUTHORIZED NOW = 0 GPU/API, manuscript convergence. No new current experiment.

## G1 — MCTA Safety Evaluation
Reality support:
- ST-WebAgentBench (arXiv:2410.06703): separates task completion from policy compliance.
- BrowserART: refusal-trained LLMs safe in chat can still pursue harmful browser behavior.
- Safety in Self-Evolving LLM Agent Systems (arXiv:2606.23075): persistent updates can amplify/preserve safety failures.
Does NOT prove: post-treatment shared-capability conditioning with one canonical action graph is unbiased/necessary.
Strongest escape: simpler benign-twin capability gate may suffice; overly rigid canonical graphs can reject alternate valid paths.
Resources: AUTHORIZED NOW = Q0 only, 10 benign agent episodes once exact provider credential/authority exists; no local GPU. Planning cash is tiny (order << CNY 1 under first-tier qwen3.5-397b-a17b assumptions; not a billing guarantee). NEXT IF PASS = P0 32 episodes. CONDITIONAL = P1 336 only if P0 has >=6 supported pair IDs and fresh authority. Historical much-larger 2.8M input +0.28M output envelope would be ~CNY 5.4 first-tier planning order, exact billing per call/route.

## E2 — State Regeneration Instability
Reality support:
- Agentic Memory: persistent state generation/update is an explicit active operation.
- HyperSkill: periodically restructures/prunes/merges persistent skill memory.
- Robo-Cortex (arXiv:2605.18729): trajectories distilled into reusable heuristics/long-term principle memory.
Does NOT prove: same-evidence regeneration instability or generator variance > actor variance.
Strongest escape: actor repeats or generic canonicalization may explain disagreement.
Resources: AUTHORIZED NOW = one non-scientific DeepSeek model-identity qualification; no GPU. Recent actor average ~2991 input +188 output tokens/call; token-route reference gives ~CNY 0.016/call, but Ark AFP may differ. NEXT IF PASS = M3R4 72 logical actor units with structural hard cap 720 provider calls under separate authority. CONDITIONAL planning order if usage/route resembled recent tranche ~CNY 11.5 for 720 calls, not current commitment.

## Paper A — Influence/Fidelity
Reality support:
- MemoryVLA (ICLR 2026): memory bank retrieves decision-relevant perceptual/cognitive entries for long-horizon robotic action.
- From Agent Traces to Trust: traces how memory/evidence support later actions.
- MemoryArena: memory distilled from earlier interactions guides later decisions.
Does NOT prove: source fidelity is separable from generic memory influence under proposed controls.
Strongest escape: no-op/unrelated edits cause comparable action changes.
Resources: AUTHORIZED NOW = formalize fidelity signatures/endpoints/no-op tolerance/replay contract; 0 GPU/API. NEXT IF PASS = base 32x4 =128 local VLA runs. CONDITIONAL = expansion to 64 units only by predeclared precision rule.

## Constraint Externality
Reality support:
- AgentDevel (arXiv:2601.04620): treats pass->fail regressions as first-class update evidence and uses non-regression gating.
- Safety in Self-Evolving LLM Agent Systems: persistent updates can have cross-cutting safety effects.
Does NOT prove: graph coupling topology causally moderates collateral regression under identical repair.
Strongest escape: strong regression testing/target-local interfaces may control most collateral effects without topology mechanism.
Resources: AUTHORIZED NOW = restore same provider credit/interface + one non-scientific readiness request after explicit authority; no provider/model substitution. Current token cash expected << CNY 1 if first tier, but exact billing unknown. NEXT IF PASS = later Gate0 / Direct-SFQ-A0 separately authorized. CONDITIONAL = mechanism ~192 probes + ~32 sham only after source/repair gates. Historical full-plan 8-16M input +0.5-1M output at qwen3.7-plus first-tier planning rates ~CNY 19-39; not current commitment.

## Paper B — Persistent Embodied Memory
Reality support:
- MemoryArena: multi-session memory use across later tasks.
- Agentic Memory: explicit long-term store/retrieve/update/discard operations.
- Robo-Cortex: long-term principle memory in reflection/adaptation loop.
- MemoryVLA: memory-conditioned long-horizon robotic manipulation.
Does NOT prove: exact persistent-state fork and longitudinal identification standard are novel/necessary; generic persistent embodied memory already has strong prior art.
Strongest escape: if committed-update vs frozen-preupdate fork cannot be reproduced exactly or native retrieval transport is weak, simpler multi-session memory evaluation may suffice.
Resources: AUTHORIZED NOW = formalize SCM/estimand/randomization/state-hash-RNG fork; 0 GPU/API. NEXT IF PASS = Phase A 32x4=128 local VLA runs. CONDITIONAL = Phase B 24x3=72 only after Phase A PASS; full base 200 is not current commitment.

## 3D — Endpoint-Sharing Topology
Reality support:
- InstructScene (arXiv:2402.04717): semantic graph prior + layout decoder for instruction-driven 3D scene synthesis.
- SceneNAT (arXiv:2601.07218): explicit subject-predicate-object triplets for relational scene synthesis.
- GeoSceneGraph (arXiv:2511.14884): scene-graph structure/geometric symmetries for text-guided 3D synthesis.
Does NOT prove: fixed-count endpoint-sharing effect or localization to text->graph vs graph->scene.
Strongest escape: lexical repetition, hub-object salience/size or predicate implication explains Chain/Hub residual.
Resources: AUTHORIZED NOW = 2x local RTX3090, developmental SGP-14 + shared SG2SC training to 1M optimizer steps each, API cash 0. Live 22:20 heartbeat: SGP-14 29,071/1M; shared decoder 276,919/1M. Rough operational remaining if current averages hold: ~11.6 and ~7.5 GPU-days respectively; not scientific outcome or guarantee. NEXT IF PASS = separate P1 authority after both training seals. CONDITIONAL = extra seeds only after P1 GO and fresh compute authority.

## Portfolio scheduling proposal
A — cheap closure: E1, C1. Finish manuscript/advisor decisions immediately.
B — already-running compute: B1, 3D. Do not interrupt; operational receipts only, no interim science.
C — near-zero qualification: G1, E2, Constraint. Resolve credential/identity/credit gates one at a time, spend only next-gate budget.
D — formalize before compute: Paper A, Paper B. Freeze causal objects before allocating VLA GPUs.
