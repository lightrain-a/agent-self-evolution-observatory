# E1/STRI Qwen ReasoningBank — mainline brief

## Leading advantage

The experiment isolates whether a representation boundary changes downstream agent behavior after accounting for the policy's ordinary same-state stochasticity.

## Chosen battlefield

A prospectively frozen, multi-repository SWE-bench Verified population evaluated with task-specific Qwen-generated ReasoningBank memory and a fixed qwen3-coder-next policy backend.

## Central claim

ReasoningBank natively reunites within-case fragments before policy consumption, whereas cross-case partitioning under top-1 consumption can remove part of the same underlying evidence from the model-visible decision state and thereby shift the distribution of edit-target behavior.

## Evidence spine

1. Exact request equality for canonical, within-case-fragmented, and case-ID-placebo representations.
2. Exact request inequality for the cross-case partition, constructed from the same underlying memory items.
3. Repeated canonical runs to measure same-state stochastic dispersion.
4. Task-blocked A-versus-D EditTargetSet distribution separation.
5. No-memory uptake and terminal SWE-bench outcomes as secondary localization evidence.

## Claim boundary

The confirmatory claim is limited to the frozen Qwen-generated memory bank, selected SWE-bench Verified task population, ReasoningBank top-1 boundary, and qwen3-coder-next provider configuration. Behavioral propagation at R3 does not require an R4 performance difference.

## Demotions

Content hashes, execution states, retry bookkeeping, quota receipts, failure differentials, and exact artifact paths belong in the reproducibility appendix. Historical DeepSeek runs motivate the repeated-trial design but do not enter confirmatory inference.

## Section-level change map

- **Introduction:** add the distinction between same-state stochasticity and representation-induced distribution shift.
- **Method:** define the three-carrier boundary and the ReasoningBank A/D/N intervention.
- **Experimental setup:** describe fresh task splits, prospective source-memory construction, structural controls, and repeated trials.
- **Results:** populate only after scientific adjudication with primary task-blocked separation, uptake, terminal outcomes, and relevance sensitivity.
- **Limitations:** state the Qwen/backend/population scope once and relate null interpretation to the frozen precision range.
- **Appendix:** place exact manifests, artifact hashes, evaluator receipts, execution order, resource accounting, and failure differentials.
