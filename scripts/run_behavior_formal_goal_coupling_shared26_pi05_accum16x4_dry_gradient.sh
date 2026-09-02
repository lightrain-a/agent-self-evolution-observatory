#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON=/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python
CHILD=/data/wyt/formal-goal-shared26-openpi-child-20260901
CACHE=/data/wyt/formal-goal-openpi-cache-v1
RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum16x4-dry-gradient-result-20260902.json"
LOG=/data/wyt/formal-goal-pi05-accum16x4-dry-gradient-20260902.log
[[ ! -e "$RECEIPT" ]] || { echo "Refusing replay: $RECEIPT" >&2; exit 2; }
exec systemd-run --user --scope --quiet -p MemoryMax=72G -p MemorySwapMax=0 -p TasksMax=512 \
  /usr/bin/taskset -c 0-63 /usr/bin/env \
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 OPENPI_DATA_HOME="$CACHE" \
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false \
  JAX_PLATFORMS=cuda XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
  "$PYTHON" "$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_accum16x4_dry_gradient.py" \
  --authority "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum16x4-dry-gradient-authority-20260902.json" \
  --preregistration "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-single-gpu-accumulation-child-preregistration-20260902.json" \
  --v4-adjudication "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-resource-v4-oom-adjudication-20260902.json" \
  --data-order-qualification "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum16x4-data-order-qualification-20260902.json" \
  --resource-admission "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-resource-admission-20260902.json" \
  --model-load-result "$ROOT/generated/behavior-formal-goal-coupling-pi05-no-update-model-load-result-20260902.json" \
  --dataloader-smoke "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-normalized-dataloader-smoke-repair2-20260902.json" \
  --tokenizer-result "$ROOT/generated/behavior-formal-goal-coupling-paligemma-tokenizer-transport-repair1-result-20260902.json" \
  --base-receipt "$ROOT/generated/behavior-formal-goal-coupling-pi05-base-transport-repair1-result-20260902.json" \
  --openpi-child-root "$CHILD" --params-root /data/wyt/formal-goal-pi05-base-params-v1 \
  --tokenizer-source /data/wyt/formal-goal-paligemma-tokenizer-v1/paligemma_tokenizer.model \
  --openpi-data-home "$CACHE" --receipt "$RECEIPT" >"$LOG" 2>&1
