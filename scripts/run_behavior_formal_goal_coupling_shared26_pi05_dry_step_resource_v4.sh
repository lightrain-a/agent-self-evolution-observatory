#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python"
CHILD="/data/wyt/formal-goal-shared26-openpi-child-20260901"
OPENPI_DATA_HOME="/data/wyt/formal-goal-openpi-cache-v1"
RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-dry-step-resource-v4-result-20260902.json"
LOG="/data/wyt/formal-goal-pi05-dry-step-resource-v4-20260902.log"

if [[ -e "$RECEIPT" ]]; then
  echo "Refusing to replay exactly-once resource-v4 receipt: $RECEIPT" >&2
  exit 2
fi

exec systemd-run --user --scope --quiet \
  -p MemoryMax=72G \
  -p MemorySwapMax=0 \
  -p TasksMax=512 \
  /usr/bin/taskset -c 0-63 /usr/bin/env \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    OPENPI_DATA_HOME="$OPENPI_DATA_HOME" \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false \
    JAX_PLATFORMS=cuda \
    "$PYTHON" "$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_dry_step_resource_v4.py" \
      --authority "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-dry-step-resource-v4-authority-20260902.json" \
      --failure-adjudication "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-dry-step-resource-v3-compile-thread-failure-adjudication-20260902.json" \
      --adapter-qualification "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-dataloader-resource-adapter-qualification-20260902.json" \
      --resource-admission "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-resource-admission-20260902.json" \
      --model-load-result "$ROOT/generated/behavior-formal-goal-coupling-pi05-no-update-model-load-result-20260902.json" \
      --dataloader-smoke "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-normalized-dataloader-smoke-repair2-20260902.json" \
      --tokenizer-result "$ROOT/generated/behavior-formal-goal-coupling-paligemma-tokenizer-transport-repair1-result-20260902.json" \
      --base-receipt "$ROOT/generated/behavior-formal-goal-coupling-pi05-base-transport-repair1-result-20260902.json" \
      --openpi-child-root "$CHILD" \
      --params-root /data/wyt/formal-goal-pi05-base-params-v1 \
      --tokenizer-source /data/wyt/formal-goal-paligemma-tokenizer-v1/paligemma_tokenizer.model \
      --openpi-data-home "$OPENPI_DATA_HOME" \
      --receipt "$RECEIPT" \
  >"$LOG" 2>&1
