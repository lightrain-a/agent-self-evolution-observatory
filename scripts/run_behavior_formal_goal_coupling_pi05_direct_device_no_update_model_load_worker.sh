#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON=/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python
CHILD=/data/wyt/formal-goal-shared26-openpi-child-20260901
CACHE=/data/wyt/formal-goal-openpi-cache-v1
RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-direct-device-no-update-model-load-result-20260902.json"
LOG=/data/wyt/formal-goal-pi05-direct-device-no-update-model-load-20260902.log

exec >>"$LOG" 2>&1

echo "[$(date --iso-8601=seconds)] detached direct-device qualification worker started"

psi_avg10() {
  awk '/^some / {for (i=1;i<=NF;i++) if ($i ~ /^avg10=/) {split($i,a,"="); print a[2]; exit}}' "$1"
}

while true; do
  if [[ -e "$RECEIPT" ]]; then
    echo "[$(date --iso-8601=seconds)] receipt already exists; refusing replay: $RECEIPT"
    exit 2
  fi

  compute_apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null | awk 'NF {n++} END {print n+0}')
  gpu_used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk 'NR==1 {print int($1)}')
  mem_available_kib=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
  memory_psi=$(psi_avg10 /proc/pressure/memory)
  io_psi=$(psi_avg10 /proc/pressure/io)

  if awk -v apps="$compute_apps" -v used="$gpu_used" -v avail="$mem_available_kib" -v mp="$memory_psi" -v ip="$io_psi" \
      'BEGIN {exit ! (apps == 0 && used < 1024 && avail >= 23068672 && mp < 1.0 && ip < 5.0)}'; then
    echo "[$(date --iso-8601=seconds)] admission PASS apps=$compute_apps gpu_used_mib=$gpu_used mem_available_kib=$mem_available_kib memory_psi=$memory_psi io_psi=$io_psi"
    break
  fi

  echo "[$(date --iso-8601=seconds)] waiting apps=$compute_apps gpu_used_mib=$gpu_used mem_available_kib=$mem_available_kib memory_psi=$memory_psi io_psi=$io_psi"
  sleep 30
done

exec /usr/bin/taskset -c 0-63 /usr/bin/env \
  JAX_PLATFORMS=cuda \
  XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
  XLA_PYTHON_CLIENT_PREALLOCATE=true \
  OMP_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 \
  OPENBLAS_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 \
  TOKENIZERS_PARALLELISM=false \
  HF_HUB_OFFLINE=1 \
  TRANSFORMERS_OFFLINE=1 \
  OPENPI_DATA_HOME="$CACHE" \
  "$PYTHON" "$ROOT/research_pipeline/behavior_formal_goal_coupling_pi05_direct_device_no_update_model_load.py" \
    --openpi-child-root "$CHILD" \
    --params-root /data/wyt/formal-goal-pi05-base-params-v1 \
    --base-receipt "$ROOT/generated/behavior-formal-goal-coupling-pi05-base-transport-repair1-result-20260902.json" \
    --authority "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-direct-device-no-update-model-load-authority-20260902.json" \
    --host-exit-adjudication "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum8x8-attempt1-host-exit-adjudication-20260902.json" \
    --static-qualification "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-direct-device-checkpoint-loader-static-qualification-20260902.json" \
    --receipt "$RECEIPT"
