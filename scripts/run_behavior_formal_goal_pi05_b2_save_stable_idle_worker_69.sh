#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/wyt/agent-self-evolution-observatory/worktrees/formal-goal-pi05-resource-repair-20260902
PHASE="$ROOT/scripts/run_behavior_formal_goal_pi05_b2_checkpoint_phase_69.sh"
AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-leaf-batched-checkpoint-qualification-authority-69-repair1-20260905.json"
RACE_ADJ="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-host69-repair1-gpu-admission-race-adjudication-20260905.json"
OUT=/data/wyt/formal-goal-checkpoint-save-qualification-69-20260905/b2-leaf-batched-8gb-52g
SAVE="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-checkpoint-save-result-69-20260905.json"
DISK="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-disk-verify-result-69-20260905.json"
REST="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-standard-restore-result-69-20260905.json"
LOG=/data/wyt/formal-goal-b2-save-stable-idle-worker-69-20260905.log
EXPECTED_MACHINE_ID=c4046d3ca4454a958f5de081aac4dc2e
MIN_AVAILABLE_KIB=104857600
MAX_GPU_USED_MIB=1024
REQUIRED_STABLE=3
INTERVAL=30
exec >>"$LOG" 2>&1

ts(){ date '+%Y-%m-%dT%H:%M:%S%z'; }
stop(){ echo "$(ts) STOP $*"; exit 2; }

[[ "$(cat /etc/machine-id)" == "$EXPECTED_MACHINE_ID" ]] || stop "machine-id mismatch"
[[ -x "$PHASE" && -f "$AUTH" && -f "$RACE_ADJ" ]] || stop "control inputs missing"
[[ ! -e "$OUT" && ! -e "$SAVE" && ! -e "$DISK" && ! -e "$REST" ]] || stop "B2 state already exists; refusing duplicate actor"

stable=0
while true; do
  [[ ! -e "$OUT" && ! -e "$SAVE" && ! -e "$DISK" && ! -e "$REST" ]] || stop "B2 state appeared while waiting"
  if systemctl --user is-active --quiet pi05-b2-checkpoint-save-69-20260905.service 2>/dev/null; then
    stable=0; echo "$(ts) WAIT save_unit_active"; sleep "$INTERVAL"; continue
  fi
  apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | sed '/^[[:space:]]*$/d' | wc -l)
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -n1 | tr -d ' ')
  avail=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
  if pgrep -f '[d]ualiats_paraphrase' >/dev/null 2>&1; then paraphrase=1; else paraphrase=0; fi
  if [[ "$apps" -eq 0 && "${used:-999999}" -le "$MAX_GPU_USED_MIB" && "$avail" -ge "$MIN_AVAILABLE_KIB" && "$paraphrase" -eq 0 ]]; then
    stable=$((stable+1))
    echo "$(ts) STABLE $stable/$REQUIRED_STABLE apps=$apps gpu_mib=$used mem_avail_kib=$avail paraphrase=$paraphrase"
  else
    stable=0
    echo "$(ts) WAIT apps=$apps gpu_mib=${used:-NA} mem_avail_kib=$avail paraphrase=$paraphrase"
  fi
  if [[ "$stable" -ge "$REQUIRED_STABLE" ]]; then
    echo "$(ts) ADMIT repair1_save stable_checks=$stable"
    "$PHASE" save
    rc=$?
    echo "$(ts) SAVE_PHASE_EXIT rc=$rc"
    exit "$rc"
  fi
  sleep "$INTERVAL"
done
