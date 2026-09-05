#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/wyt/formal-goal-pi05-resource-repair-20260902
PHASE="$ROOT/scripts/run_behavior_formal_goal_pi05_b2_checkpoint_phase_231.sh"
AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-leaf-batched-checkpoint-qualification-authority-231-20260905.json"
OUT=/data/wyt/formal-goal-checkpoint-save-qualification-231-20260905/b2-leaf-batched-8gb-52g
SAVE="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-checkpoint-save-result-231-20260905.json"
DISK="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-disk-verify-result-231-20260905.json"
REST="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-standard-restore-result-231-20260905.json"
LOG=/data/wyt/formal-goal-b2-save-admission-worker-231-20260905.log
EXPECTED_MACHINE_ID=6fd433c546c241218ccd29813f304aee
MIN_AVAILABLE_KIB=$((56*1024*1024))
MAX_GPU_USED_MIB=1024
exec >>"$LOG" 2>&1

ts(){ date '+%Y-%m-%dT%H:%M:%S%z'; }
stop(){ echo "$(ts) STOP $*"; exit 2; }

[[ "$(cat /etc/machine-id)" == "$EXPECTED_MACHINE_ID" ]] || stop "machine-id mismatch"
[[ -x "$PHASE" && -f "$AUTH" ]] || stop "B2 phase launcher/authority missing"

while true; do
  # Existence means this exactly-once qualification was already consumed or started.
  if [[ -e "$OUT" || -e "$SAVE" || -e "$DISK" || -e "$REST" ]]; then
    stop "B2 state already exists; refusing duplicate save actor"
  fi
  apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | sed '/^[[:space:]]*$/d' | wc -l)
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -n1 | tr -d ' ')
  avail=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
  mpsi=$(awk '/^some/ {for(i=1;i<=NF;i++) if($i ~ /^avg10=/){split($i,a,"=");print a[2]}}' /proc/pressure/memory)
  iopsi=$(awk '/^some/ {for(i=1;i<=NF;i++) if($i ~ /^avg10=/){split($i,a,"=");print a[2]}}' /proc/pressure/io)
  if python3 - "$apps" "${used:-999999}" "$avail" "$mpsi" "$iopsi" "$MIN_AVAILABLE_KIB" "$MAX_GPU_USED_MIB" <<'PY'
import sys
apps, used, avail = int(sys.argv[1]), int(float(sys.argv[2])), int(sys.argv[3])
mpsi, iopsi = float(sys.argv[4] or 0), float(sys.argv[5] or 0)
min_avail, max_used = int(sys.argv[6]), int(sys.argv[7])
ok = apps == 0 and used <= max_used and avail >= min_avail and mpsi < 1.0 and iopsi < 5.0
raise SystemExit(0 if ok else 1)
PY
  then
    echo "$(ts) ADMIT save apps=$apps gpu_mib=$used mem_avail_kib=$avail mpsi=$mpsi iopsi=$iopsi"
    "$PHASE" save
    rc=$?
    echo "$(ts) SAVE_PHASE_EXIT rc=$rc"
    exit "$rc"
  fi
  echo "$(ts) WAIT save apps=$apps gpu_mib=${used:-NA} mem_avail_kib=$avail mpsi=$mpsi iopsi=$iopsi"
  sleep 30
done
