#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON=/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python
CHILD=/data/wyt/formal-goal-shared26-openpi-child-20260901
RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-direct-device-no-update-model-load-result-20260902.json"
LOG=/data/wyt/formal-goal-pi05-direct-device-no-update-model-load-20260902.log
[[ ! -e "$RECEIPT" ]] || { echo "Refusing replay: $RECEIPT" >&2; exit 2; }
exec systemd-run --user --scope --quiet \
  -p MemoryMax=20G \
  -p MemorySwapMax=0 \
  -p TasksMax=512 \
  /usr/bin/taskset -c 0-63 /usr/bin/env \
    JAX_PLATFORMS=cuda \
    XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false \
    "$PYTHON" "$ROOT/research_pipeline/behavior_formal_goal_coupling_pi05_direct_device_no_update_model_load.py" \
      --openpi-child-root "$CHILD" \
      --params-root /data/wyt/formal-goal-pi05-base-params-v1 \
      --base-receipt "$ROOT/generated/behavior-formal-goal-coupling-pi05-base-transport-repair1-result-20260902.json" \
      --authority "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-direct-device-no-update-model-load-authority-20260902.json" \
      --host-exit-adjudication "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum8x8-attempt1-host-exit-adjudication-20260902.json" \
      --static-qualification "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-direct-device-checkpoint-loader-static-qualification-20260902.json" \
      --receipt "$RECEIPT" \
  >"$LOG" 2>&1
