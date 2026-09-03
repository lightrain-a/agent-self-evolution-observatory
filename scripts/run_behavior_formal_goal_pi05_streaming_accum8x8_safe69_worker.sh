#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON=/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python
CHILD=/data/wyt/formal-goal-shared26-openpi-child-20260901
CACHE=/data/wyt/formal-goal-openpi-cache-v1
AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-streaming-accum8x8-safe69-authority-20260903.json"
DIRECT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-portable-direct-device-no-update-model-load-result-232-20260903.json"
RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-streaming-accum8x8-safe69-result-20260903.json"
LOG=/data/wyt/formal-goal-pi05-streaming-accum8x8-safe69-20260903.log

exec >>"$LOG" 2>&1
printf '[%s] safe69 streaming 8x8 worker start\n' "$(date --iso-8601=seconds)"
[[ -f "$AUTH" ]] || { echo "authority missing"; exit 3; }
[[ -f "$DIRECT" ]] || { echo "direct-device result missing"; exit 3; }
[[ ! -e "$RECEIPT" ]] || { echo "Refusing replay: $RECEIPT"; exit 2; }

psi_avg10() {
  awk '/^some / {for (i=1;i<=NF;i++) if ($i ~ /^avg10=/) {split($i,a,"="); print a[2]; exit}}' "$1"
}

while true; do
  [[ ! -e "$RECEIPT" ]] || { echo "receipt appeared while waiting; refusing replay"; exit 2; }
  apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null | awk 'NF {n++} END {print n+0}')
  gpu_used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk 'NR==1 {print int($1)}')
  avail=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
  mp=$(psi_avg10 /proc/pressure/memory)
  ip=$(psi_avg10 /proc/pressure/io)
  if awk -v a="$apps" -v g="$gpu_used" -v m="$avail" -v mp="$mp" -v ip="$ip" 'BEGIN {exit !(a==0 && g<1024 && m>=25165824 && mp<1.0 && ip<5.0)}'; then
    printf '[%s] admission PASS apps=%s gpu_used_mib=%s mem_available_kib=%s memory_psi=%s io_psi=%s\n' "$(date --iso-8601=seconds)" "$apps" "$gpu_used" "$avail" "$mp" "$ip"
    break
  fi
  printf '[%s] waiting apps=%s gpu_used_mib=%s mem_available_kib=%s memory_psi=%s io_psi=%s\n' "$(date --iso-8601=seconds)" "$apps" "$gpu_used" "$avail" "$mp" "$ip"
  sleep 30
done

exec /usr/bin/taskset -c 0-63 /usr/bin/env \
  HF_HUB_OFFLINE=1 \
  TRANSFORMERS_OFFLINE=1 \
  OPENPI_DATA_HOME="$CACHE" \
  OMP_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 \
  OPENBLAS_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 \
  TOKENIZERS_PARALLELISM=false \
  JAX_PLATFORMS=cuda \
  XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
  "$PYTHON" "$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_accum8x8_streaming_direct_device_dry_gradient.py" \
    --authority "$AUTH" \
    --preregistration "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-single-gpu-accumulation-child-preregistration-20260902.json" \
    --host-exit-adjudication "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum8x8-attempt1-host-exit-adjudication-20260902.json" \
    --data-order-qualification "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum8x8-data-order-qualification-20260902.json" \
    --resource-admission "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-resource-admission-20260902.json" \
    --model-load-result "$ROOT/generated/behavior-formal-goal-coupling-pi05-no-update-model-load-result-20260902.json" \
    --direct-device-model-load-result "$DIRECT" \
    --dataloader-smoke "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-normalized-dataloader-smoke-repair2-20260902.json" \
    --tokenizer-result "$ROOT/generated/behavior-formal-goal-coupling-paligemma-tokenizer-transport-repair1-result-20260902.json" \
    --base-receipt "$ROOT/generated/behavior-formal-goal-coupling-pi05-base-transport-repair1-result-20260902.json" \
    --openpi-child-root "$CHILD" \
    --params-root /data/wyt/formal-goal-pi05-base-params-v1 \
    --tokenizer-source /data/wyt/formal-goal-paligemma-tokenizer-v1/paligemma_tokenizer.model \
    --openpi-data-home "$CACHE" \
    --receipt "$RECEIPT"
