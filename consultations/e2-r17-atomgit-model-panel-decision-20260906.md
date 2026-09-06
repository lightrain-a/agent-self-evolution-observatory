# E2-R17 AtomGit model-panel decision — 2026-09-06

## Decision

Use AtomGit as a **separate model-subject pool**, not as a coding/review/repair agent for E2-R17 and not as a rescue path for the frozen R3D primary experiment.

Current locally qualified AtomGit models:

- `qwen3.8-27b`
- `GLM-5.2`
- `deepseek-v4-flash`

The current official CodingPlan page describes a rolling 5-hour request-count window and lists a Pro tier with approximately 500 requests/5h supporting these three models. The local AtomCode installation is v5.0.9 and the three profiles are actually routable on host69.

## Transport harness

Use only headless, ephemeral, no-external-tool runs:

```text
--ephemeral
--no-tools
--no-telemetry
--output-format jsonl
```

A scientific/model-qualification sample is `TRANSPORT_CLEAN` only if:

```text
usage rows == 1
rounds == 1
tool_calls == 0
no tool.started event
```

Otherwise mark it `TRANSPORT_VOID`; do not silently count the final answer as one clean independent model sample.

This rule matters because AtomCode 5.0.9 may expose its internal `schedule_wakeup` loop-control tool even under `--no-tools`. The E2 qualification panel reproduced this once on GLM-5.2: the internal call failed, AtomCode sent a second model request, and only then received the requested JSON.

## Qualification result 1 — fixed-output repeatability

Same JSON-only prompt, five invocations/model.

| Model | Transport clean | Semantic exact | Strict JSON | Byte-distinct outputs | Finding |
|---|---:|---:|---:|---:|---|
| Qwen3.8-27B | 5/5 | 5/5 | 5/5 | 1 | clean and byte-stable |
| DeepSeek-V4-Flash | 5/5 | 5/5 | 5/5 | 1 | clean, byte-stable, fastest in this harness |
| GLM-5.2 | 4/5 | 5/5 | 4/5 | 2 | one fenced answer; one `schedule_wakeup` transport VOID |

Do not interpret byte stability on this trivial prompt as general state-generation determinism.

## Qualification result 2 — synthetic evidence relevance

Six preregistered synthetic cases/model, no retry/replacement. No E2 task, pool, support, state, heldout, or effect artifact was exposed.

The panel tests only whether a model can distinguish:

1. procedural evidence relevant to a new task;
2. procedural evidence irrelevant to a new task;
3. same-instance binding evidence that remains relevant;
4. binding evidence that should be ignored for a different instance.

Results:

| Model | Transport clean | Semantic exact | Strict JSON |
|---|---:|---:|---:|
| Qwen3.8-27B | 6/6 | 6/6 | 6/6 |
| DeepSeek-V4-Flash | 6/6 | 6/6 | 6/6 |
| GLM-5.2 | 6/6 | 5/6 | 4/6 |

GLM's semantic miss was `B_CELL_SAME_INSTANCE`: the prompt explicitly described a fact bound to `Alpha.xlsx / Sheet3!B17`, and the future task remained in the same workbook/cell dependency. GLM correctly chose `use`, but classified the evidence as generic `procedural / RULE_REUSED` instead of `binding / SAME_INSTANCE_BINDING`.

This is relevant to E2's conceptual distinction: a future-task null is uninterpretable unless the future task actually needs the evidence; moreover, instance-binding evidence can be useful when the same binding recurs, even though it should not transfer across unrelated instances.

## Recommended role assignment

### Qwen3.8-27B — preferred AtomGit cross-family shadow candidate

Qwen3.8-27B is the strongest **AtomGit-pool candidate for a future cross-family shadow robustness pilot** because:

- it is not DeepSeek-family, unlike the primary DeepSeek V4-Pro;
- 5/5 repeatability invocations were transport-clean;
- 6/6 synthetic relevance cases were transport-clean and semantically exact;
- no observed `schedule_wakeup` leakage in these panels.

However, it is **not automatically the frozen official D1 backbone**. The current D1 roadmap specifies a qualified Qwen sparse 35B-class model or Kimi K3. Qwen3.8-27B is a 27B AtomGit model and may only be promoted into formal D1 through a prospective, outcome-blind D1 eligibility amendment/review after the primary B2 gate passes. No E2 effect may be consulted when making that amendment.

### DeepSeek-V4-Flash — fast shadow diagnostic / reviewer

Use for cheap-in-request-count shadow diagnostics, prompt/schema checks, or non-voting model-panel review. It was the fastest of the three in the observed AtomCode harness and was clean on both qualification panels.

It is not the first D1 choice because a same-family DeepSeek robustness result adds less family-level external validity than Qwen.

### GLM-5.2 — third triangulation model with strict VOID accounting

GLM remains useful as a non-voting third model, but every invocation must preserve the transport-VOID rule. Do not choose it as the first D1 backbone unless the runtime/tool-leakage and procedural-vs-binding classification instability are prospectively addressed.

## What NOT to do

Do not:

- replace the primary DeepSeek V4-Pro because an AtomGit model looks better;
- run AtomGit on unread R3D Stage-A support before the support gate;
- run it on Stage-B heldout/effect artifacts before Stage-B authority;
- add AtomGit models after a V3 FAIL as rescue;
- count a two-round `schedule_wakeup` invocation as one independent model sample;
- copy AtomCode JSONL final output without checking the full transport trace;
- inflate the paper by running all three models on every existing controlled experiment.

## Efficient use of the 5-hour window

Use request budget on **new evidence types**, not duplicated matrix volume:

1. model transport/semantic qualification (done for the three current models);
2. small non-voting shadow model panels when a mechanism question needs independent triangulation;
3. after B2 PASS, either keep the existing formal D1 candidate rule or prospectively review whether the qualified AtomGit Qwen3.8-27B can serve a clearly labeled smaller cross-family robustness tranche;
4. after Public P1 is frozen, optional low-cost cross-model public robustness if it changes a paper-level decision.

Do not spend the free quota simply to multiply R, skeletons, or benchmarks already adequately identified by the frozen experiment.

## Current authority boundary

AtomGit qualification consumed no E2 scientific object:

```text
R3D Stage A authority      unchanged / false until hard gate + fresh identity + authorization
support read               false
Stage B                    false
heldout read               false
Public P1                  false
primary model replacement  false
paper claim promotion      false
```

The qualification results are **shadow/operational evidence only** until an optional model-robustness experiment is separately frozen and authorized.
