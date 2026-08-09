# P0 execution runbook

This document separates five different notions of readiness:

1. **Scientific gate** — the current human/review state allows the P0.
2. **Harness gate** — deterministic collection/analysis code and frozen configs exist.
3. **Runtime gate** — the selected Python environment, model, ALFWorld package/data, GPU, and data disk pass preflight.
4. **Smoke gate** — one real no-update ALFWorld OOD episode completes through the local model and admissible-action adapter.
5. **Execution state** — formal P0 collection has actually started.

Formal collection may start only after the first four gates pass. Installing dependencies or passing preflight does not count as starting an experiment. Synthetic fixtures are testing artifacts only and must never be written into the Pilot Registry.

## Current runnable candidates

- A-1 `update-trust-region`: scientific gate PASS; harness implemented.
- A-2 `budgeted-evolution-controller`: scientific gate PASS; harness implemented.
- B-1: method redesign after fresh 2026-08-09 collision recheck; do not run.
- E-1: current certificate form stopped after fresh 2026-08-09 collision recheck; do not run.
- F-1: wait for real-scenario confirmation and then rerun collision audit; do not run.

## Runtime paths

- Runtime Python: `/data/wyt/envs/vlm_test/bin/python`
- Local model: `/data/wyt/models/indept/Qwen2.5-7B`
- Experiment root: `/data/wyt/agent-self-evolution-observatory`
- P0 registry: `${RESEARCH_RUN_DIR:-<experiment-root>/runs}/pilots/results`

Run the read-only preflight from the repository:

```bash
python -m research_pipeline.p0_runner preflight --write-site
```

The preflight publishes only safe readiness metadata to `generated/p0-runtime-readiness.{json,js}`. It does not launch a model or an environment.

## Dependency target

Use an isolated environment under `/data`; do not install into the repository Python or `/home`.

Pinned experiment dependencies:

- ALFWorld `0.4.2` (text-only mode is sufficient for the first P0)
- TextWorld `1.7.0` (`ALFWorld 0.4.2` requires `textworld[pddl]>=1.6.1`; the selected runtime is Python 3.12)
- existing PyTorch `2.12.1+cu130`
- existing Transformers `4.45.0`

The existing runtime already loads the local Qwen2.5-7B tokenizer and sees the A100. Only ALFWorld plus its game/PDDL data is currently missing.

An audited setup script is provided but is **not** run by the repository build/test path:

```bash
bash research_pipeline/setup_p0_runtime.sh
```

It installs ALFWorld/TextWorld into `/data/wyt/envs/agent_evolution_p0_site` rather than modifying the existing CUDA environment, appends that target after the working runtime packages, and downloads game/PDDL data to the experiment disk. After setup, rerun `preflight --write-site`, then run exactly one smoke episode:

```bash
/data/wyt/envs/vlm_test/bin/python -m research_pipeline.p0_runner smoke
python -m research_pipeline.p0_runner preflight --write-site
```

The smoke artifact is `/data/wyt/agent-self-evolution-observatory/p0-runtime-smoke.json`. It only proves the model/environment/action-parser chain can execute a non-empty episode; task success is not required. The artifact is bound to a runtime contract hash covering the adapter source, ALFWorld config, selected Python/model paths, and detected torch/transformers/alfworld/textworld versions, so relevant code or dependency changes automatically invalidate stale smoke results. `collect` stays locked until the current contract has a PASS smoke artifact.

When formal collection starts, the runner writes `/data/wyt/agent-self-evolution-observatory/p0-execution-state.json` with `running`, then updates it to `completed` or `failed`. This marker is operational state only and is never treated as a scientific P0 result; only validated Pilot Registry results populate measured effects.

## A-1 normalized input

The analyzer consumes one JSON object per candidate prompt update:

```json
{
  "candidate_id": "u0001",
  "current_task_gain": 0.08,
  "edit_size": 0.14,
  "probe_features_before": {
    "action_sequence_distance": 0.0,
    "invalid_action_rate": 0.02,
    "instruction_choice_shift": 0.0,
    "plan_length": 15.0
  },
  "probe_features_after": {
    "action_sequence_distance": 0.21,
    "invalid_action_rate": 0.03,
    "instruction_choice_shift": 0.18,
    "plan_length": 17.0
  },
  "hidden_before": [1, 1, 0, 1],
  "hidden_after": [1, 0, 0, 1]
}
```

Rules:

- Candidate generation is structurally isolated: `generate_a1_candidates()` accepts only the frozen policy, discovery failure traces, target count, and seed. It has no probe or hidden input, and it completes before any probe/hidden execution.
- The same frozen behavior-probe set is used for every candidate.
- Freeze **8 behavior probes** and a **24-task hidden original-task pool**. Each candidate receives a preregistered balanced subset of **8 hidden tasks**, not the full pool.
- Freeze **20–24 candidate prompt updates** after collecting about 20 discovery failures (with at most 32 discovery episodes). With 24 candidates the nominal plan is 460 environment episodes; even the 32-episode discovery ceiling keeps the worst case at 472, below the 500-episode cap.
- Assignment is deterministic from `candidate_id × task_id × seed`, and each hidden task must receive approximately equal exposure across candidates.
- `hidden_before` and `hidden_after` are environment success indicators from the exact same assigned tasks.
- `edit_size` is computed before hidden evaluation.
- The final proposed admission rule is **current-task gain + behavioral drift**: positive-gain candidates are preferred, then lower drift breaks risk among them. Pure behavioral drift remains an ablation; it is not the final admission policy.

Analysis:

```bash
python -m research_pipeline.p0_runner analyze update-trust-region \
  --input <candidate-evaluation.jsonl> \
  --config research_pipeline/p0_a1_config.json \
  --output-dir <run-dir>
```

For manual debugging, analysis may run without registration. A real registry write additionally requires `--cost <run>/cost.json --manifest <run>/manifest.json --register`; cost and provenance are hard-validated before the registry write.

Once ALFWorld package/data **and the real smoke episode** pass, the preferred formal A-1 command is the transactional `execute` path:

```bash
export ALFWORLD_DATA=/data/wyt/agent-self-evolution-observatory/alfworld
/data/wyt/envs/vlm_test/bin/python -m research_pipeline.p0_runner execute update-trust-region \
  --output-dir /data/wyt/agent-self-evolution-observatory/runs/p0-a1
```

`execute` performs collection → cost/manifest audit → analysis → Pilot Registry registration → local research-system refresh. A PASS still ends at `await-human-approval`; it cannot launch P1.

For collection-only debugging, use:

```bash
export ALFWORLD_DATA=/data/wyt/agent-self-evolution-observatory/alfworld
/data/wyt/envs/vlm_test/bin/python -m research_pipeline.p0_runner collect update-trust-region \
  --output-dir /data/wyt/agent-self-evolution-observatory/runs/p0-a1
```

The collector writes raw traces and `candidate-evaluation.jsonl`; it does **not** register a Pilot result.

## A-2 normalized input

The analyzer consumes fixed candidate sequences. Every competing controller sees the exact same sequence and may only decide where to stop/rollback; it cannot regenerate a candidate.

```json
{
  "task_id": "alfworld-task-001",
  "split": "hidden",
  "rounds": [
    {
      "round": 1,
      "marginal_gain": 0.11,
      "probe_regression": 0.02,
      "disagreement": 0.12,
      "cumulative_calls": 3,
      "success": 0,
      "regression": 0
    }
  ]
}
```

Rules:

- Candidate sequences are generated once and persisted before controller fitting. They are **policy-conditioned**: each next patch is proposed from the previous executed trace, but no controller participates during generation.
- Discovery/calibration sequences fit both the tuned heuristic and learned controller.
- Hidden sequences are generated by the same frozen updater but are never used to tune thresholds, feature scales, or controller weights.
- Fixed-1, fixed-2, fixed-4, tuned heuristic, and learned controller all reuse identical saved candidate sequences.
- Cost is charged through the last **observed** round. If round 3 reveals a bad update and the policy rolls back to round 2, success/regression are measured at round 2 but round-3 generation/execution/probe calls remain in the cost. The main table reports both selected and observed rounds.

The frozen P0 uses **8 discovery + 8 calibration + 12 hidden sequences**, at most four update rounds per task, and the same **2 regression probes** per round. The collection plan is 366 environment episodes under a 420-episode cap.

Once runtime preflight and the real smoke episode pass, the preferred formal A-2 command is:

```bash
export ALFWORLD_DATA=/data/wyt/agent-self-evolution-observatory/alfworld
/data/wyt/envs/vlm_test/bin/python -m research_pipeline.p0_runner execute budgeted-evolution-controller \
  --output-dir /data/wyt/agent-self-evolution-observatory/runs/p0-a2
```

For collection-only debugging, use:

```bash
export ALFWORLD_DATA=/data/wyt/agent-self-evolution-observatory/alfworld
/data/wyt/envs/vlm_test/bin/python -m research_pipeline.p0_runner collect budgeted-evolution-controller \
  --output-dir /data/wyt/agent-self-evolution-observatory/runs/p0-a2
```

Then analyze manually if needed:

```bash
python -m research_pipeline.p0_runner analyze budgeted-evolution-controller \
  --input <run-dir>/fixed-sequences.jsonl \
  --config research_pipeline/p0_a2_config.json \
  --output-dir <run-dir> \
  --cost <run-dir>/cost.json \
  --manifest <run-dir>/manifest.json
```

Adding `--register` to that manual command is allowed only after the same cost/manifest audit passes.

## Result registration and human gate

A real `decision.json` must contain the code commit, config hash, datasets, models, seeds, metrics, and measured cost. A P0 PASS must have:

```json
"next_action": "await-human-approval"
```

The registry rejects a P0 result that requests `execute-P1`. P1 remains `execution_authorized=false` until a separate human approval artifact is present.
