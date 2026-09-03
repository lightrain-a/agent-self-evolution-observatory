#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY=/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python
CHILD=/data/wyt/formal-goal-portable-openpi-child-69-20260903
PARAMS=/data/wyt/formal-goal-pi05-base-params-v1
R="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum4x16-synthetic-fused-direct-device-result-20260903.json"
LOG=/data/wyt/formal-goal-pi05-accum4x16-synthetic-20260903.log
[[ ! -e "$R" ]] || { echo "Refusing replay: $R"; exit 2; }
exec >>"$LOG" 2>&1
echo "[$(date --iso-8601=seconds)] synthetic accum4x16 start"
exec /usr/bin/taskset -c 0-63 /usr/bin/env \
  OMP_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 \
  OPENBLAS_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 \
  TOKENIZERS_PARALLELISM=false \
  JAX_PLATFORMS=cuda \
  XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
  HF_HUB_OFFLINE=1 \
  TRANSFORMERS_OFFLINE=1 \
  "$PY" "$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_accum4x16_synthetic_fused_direct_device_dry_gradient.py" \
    --authority "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum4x16-synthetic-fused-direct-device-authority-20260903.json" \
    --preregistration "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-single-gpu-accumulation-child-preregistration-20260902.json" \
    --prev-resource-adjudication "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-synthetic-fused-accum8x8-resource-failure-adjudication-20260903.json" \
    --data-order-qualification "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum4x16-data-order-qualification-20260903.json" \
    --portable-direct-device-result "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-portable-direct-device-no-update-model-load-result-232-20260903.json" \
    --openpi-child-root "$CHILD" \
    --params-root "$PARAMS" \
    --receipt "$R"
