#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON=/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python
CHILD=/data/wyt/formal-goal-shared26-openpi-child-20260901
RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-source-train-compile-probe-v5b-result-20260902.json"
LOG=/data/wyt/formal-goal-pi05-source-train-compile-probe-v5b-20260902.log
[[ ! -e "$RECEIPT" ]] || { echo "receipt exists: $RECEIPT" >&2; exit 2; }
exec systemd-run --user --scope --quiet \
  -p MemoryMax=72G -p MemorySwapMax=0 -p TasksMax=512 \
  /usr/bin/taskset -c 0-63 /usr/bin/env \
    HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
    OPENPI_DATA_HOME=/data/wyt/formal-goal-openpi-cache-v1 \
    OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false JAX_PLATFORMS=cuda \
    XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 XLA_PYTHON_CLIENT_PREALLOCATE=true \
    "$PYTHON" "$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_source_train_compile_probe_v5b.py" \
      --authority "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-source-train-compile-probe-v5b-authority-20260902.json" \
      --openpi-child-root "$CHILD" \
      --params-root /data/wyt/formal-goal-pi05-base-params-v1 \
      --receipt "$RECEIPT" \
  >"$LOG" 2>&1
