#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/wyt/agent-self-evolution-observatory/worktrees/formal-goal-pi05-resource-repair-20260902
PHASE="$ROOT/scripts/run_behavior_formal_goal_pi05_b2_checkpoint_phase_69.sh"
SAVE="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-checkpoint-save-result-69-20260905.json"
DISK="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-disk-verify-result-69-20260905.json"
REST="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-standard-restore-result-69-20260905.json"
LOG=/data/wyt/formal-goal-b2-postsave-chain-69-20260905.log
MIN_AVAILABLE_KIB=104857600
MAX_GPU_USED_MIB=1024
REQUIRED_STABLE=3
INTERVAL=30
exec >>"$LOG" 2>&1

ts(){ date '+%Y-%m-%dT%H:%M:%S%z'; }
stop(){ echo "$(ts) STOP $*"; exit 2; }
status_of(){ python3 - "$1" <<'PY'
import json,sys
print(json.load(open(sys.argv[1])).get('status',''))
PY
}

[[ "$(cat /etc/machine-id)" == "c4046d3ca4454a958f5de081aac4dc2e" ]] || stop "machine-id mismatch"
[[ -x "$PHASE" ]] || stop "phase launcher missing"
[[ ! -e "$REST" ]] || stop "restore result already exists"

while [[ ! -e "$SAVE" ]]; do
  echo "$(ts) WAIT save_result"
  sleep "$INTERVAL"
done
[[ "$(status_of "$SAVE")" == "PI05_B2_CHECKPOINT_SAVE_QUALIFICATION_PASS" ]] || stop "save result not PASS: $(status_of "$SAVE")"

echo "$(ts) SAVE_PASS"
if [[ ! -e "$DISK" ]]; then
  echo "$(ts) START disk_verify"
  "$PHASE" disk
fi
[[ -e "$DISK" ]] || stop "disk result missing after phase"
[[ "$(status_of "$DISK")" == "PI05_B2_DISK_VERIFY_PASS" ]] || stop "disk result not PASS: $(status_of "$DISK")"
echo "$(ts) DISK_PASS"

stable=0
while true; do
  [[ ! -e "$REST" ]] || stop "restore result appeared before admission"
  if systemctl --user is-active --quiet pi05-b2-checkpoint-save-69-20260905.service 2>/dev/null; then
    stable=0; echo "$(ts) WAIT save_unit_active"; sleep "$INTERVAL"; continue
  fi
  apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | sed '/^[[:space:]]*$/d' | wc -l)
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -n1 | tr -d ' ')
  avail=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
  if pgrep -f '[d]ualiats_paraphrase' >/dev/null 2>&1; then paraphrase=1; else paraphrase=0; fi
  if [[ "$apps" -eq 0 && "${used:-999999}" -le "$MAX_GPU_USED_MIB" && "$avail" -ge "$MIN_AVAILABLE_KIB" && "$paraphrase" -eq 0 ]]; then
    stable=$((stable+1)); echo "$(ts) RESTORE_STABLE $stable/$REQUIRED_STABLE apps=$apps gpu_mib=$used mem_avail_kib=$avail"
  else
    stable=0; echo "$(ts) WAIT_RESTORE apps=$apps gpu_mib=${used:-NA} mem_avail_kib=$avail paraphrase=$paraphrase"
  fi
  if [[ "$stable" -ge "$REQUIRED_STABLE" ]]; then
    echo "$(ts) START standard_restore"
    "$PHASE" restore
    break
  fi
  sleep "$INTERVAL"
done
[[ -e "$REST" ]] || stop "restore result missing after phase"
[[ "$(status_of "$REST")" == "PI05_B2_STANDARD_RESTORE_PASS" ]] || stop "restore result not PASS: $(status_of "$REST")"
echo "$(ts) B2_QUALIFICATION_COMPLETE_PASS"
exit 0
