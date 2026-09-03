#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV=/data/wyt/formal-goal-shared26-openpi-env-20260901
CHILD=/data/wyt/formal-goal-portable-openpi-child-69-20260903
PARAMS=/data/wyt/formal-goal-pi05-base-params-v1
RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum8x8-synthetic-fused-direct-device-result-20260903.json"
LOG=/data/wyt/formal-goal-pi05-synthetic-fused-accum8x8-safe69-20260903.log
exec >>"$LOG" 2>&1

echo "[$(date --iso-8601=seconds)] safe69 synthetic fused 8x8 worker started"
psi_avg10() {
  awk '/^some / {for (i=1;i<=NF;i++) if ($i ~ /^avg10=/) {split($i,a,"="); print a[2]; exit}}' "$1"
}
while true; do
  if [[ -e "$RECEIPT" ]]; then
    echo "[$(date --iso-8601=seconds)] receipt exists; refusing replay"
    exit 2
  fi
  apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null | awk 'NF{n++} END{print n+0}')
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk 'NR==1{print int($1)}')
  avail=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
  mp=$(psi_avg10 /proc/pressure/memory)
  ip=$(psi_avg10 /proc/pressure/io)
  if awk -v apps="$apps" -v used="$used" -v avail="$avail" -v mp="$mp" -v ip="$ip" 'BEGIN{exit !(apps==0 && used<1024 && avail>=23068672 && mp<1.0 && ip<5.0)}'; then
    echo "[$(date --iso-8601=seconds)] admission PASS apps=$apps used=$used avail=$avail mp=$mp ip=$ip"
    break
  fi
  echo "[$(date --iso-8601=seconds)] waiting apps=$apps used=$used avail=$avail mp=$mp ip=$ip"
  sleep 30
done

exec systemd-run --user --scope --quiet \
  -p MemoryMax=20G -p MemorySwapMax=0 -p TasksMax=512 \
  /usr/bin/taskset -c 0-63 /usr/bin/env \
    OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false JAX_PLATFORMS=cuda XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
    HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
    "$ENV/bin/python" "$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_accum8x8_synthetic_fused_direct_device_dry_gradient.py" \
      --authority "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum8x8-synthetic-fused-direct-device-authority-20260903.json" \
      --preregistration "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-single-gpu-accumulation-child-preregistration-20260902.json" \
      --host-exit-adjudication "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum8x8-attempt1-host-exit-adjudication-20260902.json" \
      --data-order-qualification "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum8x8-data-order-qualification-20260902.json" \
      --portable-direct-device-result "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-portable-direct-device-no-update-model-load-result-232-20260903.json" \
      --openpi-child-root "$CHILD" \
      --params-root "$PARAMS" \
      --receipt "$RECEIPT"
