#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/wyt/agent-self-evolution-observatory/worktrees/formal-goal-pi05-resource-repair-20260902
PHASE="$ROOT/scripts/run_behavior_formal_goal_pi05_b3_checkpoint_phase_69.sh"
SAVE="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b3-checkpoint-save-result-69-20260905.json"
DISK="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b3-disk-verify-result-69-20260905.json"
REST="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b3-standard-restore-result-69-20260905.json"
OUT=/data/wyt/formal-goal-checkpoint-save-qualification-69-20260905/b3-writeback-aware-8gb-52g
LOG=/data/wyt/formal-goal-b3-chain-69-20260905.log
EXPECTED_MACHINE_ID=c4046d3ca4454a958f5de081aac4dc2e
MIN_AVAILABLE_KIB=104857600
MAX_GPU_USED_MIB=1024
REQUIRED_STABLE=3
INTERVAL=30
exec >>"$LOG" 2>&1

ts(){ date '+%Y-%m-%dT%H:%M:%S%z'; }
stop(){ echo "$(ts) STOP $*"; exit 2; }
status_of(){ python3 - "$1" <<'PY'
import json,sys
try: print(json.load(open(sys.argv[1])).get('status',''))
except Exception: print('')
PY
}

[[ "$(cat /etc/machine-id)" == "$EXPECTED_MACHINE_ID" ]] || stop "machine-id mismatch"
[[ -x "$PHASE" ]] || stop "phase launcher missing"
[[ ! -e "$OUT" && ! -e "$SAVE" && ! -e "$DISK" && ! -e "$REST" ]] || stop "B3 state already exists"

echo "$(ts) START B3 chain; formal_run3=UNAUTHORIZED host67=FORBIDDEN"
if ! "$PHASE" save; then stop "S unit failed"; fi
[[ "$(status_of "$SAVE")" == "PI05_B3_CHECKPOINT_SAVE_QUALIFICATION_PASS" ]] || stop "S not terminal PASS"
echo "$(ts) S_PASS"

if ! "$PHASE" disk; then stop "V1 disk unit failed"; fi
[[ "$(status_of "$DISK")" == "PI05_B3_DISK_VERIFY_PASS" ]] || stop "V1 not PASS"
echo "$(ts) V1_PASS"

stable=0
while [[ "$stable" -lt "$REQUIRED_STABLE" ]]; do
  [[ "$(status_of "$SAVE")" == "PI05_B3_CHECKPOINT_SAVE_QUALIFICATION_PASS" ]] || stop "S changed after PASS"
  [[ "$(status_of "$DISK")" == "PI05_B3_DISK_VERIFY_PASS" ]] || stop "V1 changed after PASS"
  [[ ! -e "$REST" ]] || stop "V2 result appeared before admission"
  apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | sed '/^[[:space:]]*$/d' | wc -l)
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -n1 | tr -d ' ')
  avail=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
  if pgrep -f '[d]ualiats_paraphrase' >/dev/null 2>&1; then paraphrase=1; else paraphrase=0; fi
  if [[ "$apps" -eq 0 && "${used:-999999}" -le "$MAX_GPU_USED_MIB" && "$avail" -ge "$MIN_AVAILABLE_KIB" && "$paraphrase" -eq 0 ]]; then
    stable=$((stable+1)); echo "$(ts) V2_STABLE $stable/$REQUIRED_STABLE apps=$apps gpu_mib=$used mem_avail_kib=$avail"
  else
    stable=0; echo "$(ts) V2_WAIT apps=$apps gpu_mib=${used:-NA} mem_avail_kib=$avail paraphrase=$paraphrase"
  fi
  [[ "$stable" -ge "$REQUIRED_STABLE" ]] || sleep "$INTERVAL"
done

if ! "$PHASE" restore; then stop "V2 restore unit failed"; fi
[[ "$(status_of "$REST")" == "PI05_B3_STANDARD_RESTORE_PASS" ]] || stop "V2 not PASS"
echo "$(ts) V2_PASS; QUALIFICATION_COMPLETE; formal_run3=UNAUTHORIZED"
