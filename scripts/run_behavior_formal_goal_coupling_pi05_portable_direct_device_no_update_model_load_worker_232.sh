#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXEC="$ROOT/scripts/run_behavior_formal_goal_coupling_pi05_portable_direct_device_no_update_model_load_232.sh"
RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-portable-direct-device-no-update-model-load-result-232-20260903.json"
ACQ=/data/wyt/formal-goal-pi05-base-acquire-232-repair1-result.json
ENV=/data/wyt/formal-goal-shared26-openpi-env-20260901
CONFIG=/data/wyt/formal-goal-policy-contracts-20260828/openpi/src/openpi/training/config.py
EXPECTED_CONFIG_SHA=4a50bb5f3579ed0035e19d2fc2a5d33821c0cc115c6e8c441eac497e74b02e99
LOG=/data/wyt/formal-goal-pi05-portable-direct-device-no-update-model-load-232.log
exec >>"$LOG" 2>&1
printf '[%s] portable direct-device admission worker start\n' "$(date --iso-8601=seconds)"
while true; do
  [[ ! -e "$RECEIPT" ]] || { echo "result receipt already exists; exit without replay"; exit 0; }
  if [[ ! -x "$ENV/bin/python" ]]; then echo "[$(date --iso-8601=seconds)] waiting frozen env"; sleep 30; continue; fi
  GOT_CONFIG_SHA=$(sha256sum "$CONFIG" 2>/dev/null | awk '{print $1}')
  if [[ "$GOT_CONFIG_SHA" != "$EXPECTED_CONFIG_SHA" ]]; then echo "[$(date --iso-8601=seconds)] waiting portable config sha=$GOT_CONFIG_SHA"; sleep 30; continue; fi
  if [[ ! -f "$ACQ" ]]; then echo "[$(date --iso-8601=seconds)] waiting checkpoint acquisition receipt"; sleep 30; continue; fi
  ACQ_OK=$($ENV/bin/python - "$ACQ" <<'PY'
import json,sys
p=json.load(open(sys.argv[1]))
print('1' if p.get('status')=='PI05_BASE_LOCAL_CONTENT_ADDRESS_REPAIR1_COMPLETE' and p.get('verified_object_count')==20 and p.get('verified_bytes')==12441721931 and p.get('error') is None else '0')
PY
)
  if [[ "$ACQ_OK" != 1 ]]; then echo "[$(date --iso-8601=seconds)] checkpoint acquisition not complete"; sleep 30; continue; fi
  APPS=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null | sed '/^$/d' | wc -l)
  GPU_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
  MEM_AVAIL=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
  MEM_PSI=$(awk '/^some / {for(i=1;i<=NF;i++) if($i ~ /^avg10=/){split($i,a,"="); print a[2]}}' /proc/pressure/memory)
  IO_PSI=$(awk '/^some / {for(i=1;i<=NF;i++) if($i ~ /^avg10=/){split($i,a,"="); print a[2]}}' /proc/pressure/io)
  OK=$(python3 - "$APPS" "$GPU_USED" "$MEM_AVAIL" "$MEM_PSI" "$IO_PSI" <<'PY'
import sys
apps=int(sys.argv[1]); gpu=int(sys.argv[2]); mem=int(sys.argv[3]); mp=float(sys.argv[4]); io=float(sys.argv[5])
print('1' if apps==0 and gpu<1024 and mem>=22*1024*1024 and mp<1.0 and io<5.0 else '0')
PY
)
  if [[ "$OK" == 1 ]]; then
    printf '[%s] admission PASS apps=%s gpu_used_mib=%s mem_available_kib=%s memory_psi=%s io_psi=%s; consuming portable qualification\n' "$(date --iso-8601=seconds)" "$APPS" "$GPU_USED" "$MEM_AVAIL" "$MEM_PSI" "$IO_PSI"
    exec "$EXEC"
  fi
  printf '[%s] waiting apps=%s gpu_used_mib=%s mem_available_kib=%s memory_psi=%s io_psi=%s\n' "$(date --iso-8601=seconds)" "$APPS" "$GPU_USED" "$MEM_AVAIL" "$MEM_PSI" "$IO_PSI"
  sleep 30
done
