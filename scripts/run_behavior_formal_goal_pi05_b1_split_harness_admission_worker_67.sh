#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PHASE="$ROOT/scripts/run_behavior_formal_goal_pi05_b1_split_harness_phase_67.sh"
REF="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-split-reference-result-67-20260905.json"
SAVE="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-split-save-stage-result-67-20260905.json"
RESULT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-split-harness-checkpoint-qualification-result-67-20260905.json"
OUT=/data/wyt/formal-goal-checkpoint-save-qualification-67-20260905/b1-split-repair1-8gb-96g
LOG=/data/wyt/formal-goal-b1-split-harness-admission-worker-67-20260905.log
MIN_AVAILABLE_KIB=$((104*1024*1024))
MAX_GPU_USED_MIB=1024
exec >>"$LOG" 2>&1

ts(){ date '+%Y-%m-%dT%H:%M:%S%z'; }
fail(){ echo "$(ts) STOP $*"; exit 2; }

# Waiting does not consume the authorized qualification attempt. Any pre-existing
# split-harness receipt/output means another actor already consumed or started it.
[[ -x "$PHASE" ]] || fail "phase launcher missing/not executable: $PHASE"
[[ ! -e "$REF" && ! -e "$SAVE" && ! -e "$RESULT" && ! -e "$OUT" ]] || fail "split-harness state already exists; refusing duplicate actor"

resource_ready(){
  local apps used avail mpsi iopsi
  apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | sed '/^[[:space:]]*$/d' | wc -l)
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -n1 | tr -d ' ')
  avail=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
  mpsi=$(awk '/^some/ {for(i=1;i<=NF;i++) if($i ~ /^avg10=/){split($i,a,"=");print a[2]}}' /proc/pressure/memory)
  iopsi=$(awk '/^some/ {for(i=1;i<=NF;i++) if($i ~ /^avg10=/){split($i,a,"=");print a[2]}}' /proc/pressure/io)
  python3 - "$apps" "$used" "$avail" "$mpsi" "$iopsi" "$MIN_AVAILABLE_KIB" "$MAX_GPU_USED_MIB" <<'PY'
import sys
apps,used,avail=int(sys.argv[1]),int(float(sys.argv[2])),int(sys.argv[3])
mpsi,iopsi=float(sys.argv[4] or 0),float(sys.argv[5] or 0)
min_avail,max_used=int(sys.argv[6]),int(sys.argv[7])
ok=(apps==0 and used<=max_used and avail>=min_avail and mpsi<1.0 and iopsi<5.0)
raise SystemExit(0 if ok else 1)
PY
}

wait_resources(){
  local label="$1"
  while ! resource_ready; do
    echo "$(ts) WAIT $label apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | sed '/^[[:space:]]*$/d' | wc -l) gpu_mib=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -n1 | tr -d ' ') mem_avail_kib=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)"
    sleep 30
  done
  echo "$(ts) READY $label"
}

run_phase(){
  local phase="$1" unit="pi05-b1-split-${phase}-67-20260905.service"
  echo "$(ts) START $phase"
  systemd-run --user --unit="$unit" --wait --collect --quiet \
    -p MemoryMax=96G -p MemorySwapMax=0 -p TasksMax=512 -p KillMode=control-group \
    /bin/bash "$PHASE" "$phase"
  echo "$(ts) EXIT0 $phase"
}

wait_resources reference
run_phase reference
python3 - "$REF" <<'PY'
import json,sys
p=sys.argv[1]; d=json.load(open(p))
assert d.get('status')=='PI05_B1_SPLIT_REFERENCE_PASS', d.get('status')
PY
[[ ! -e "$OUT" ]] || fail "reference phase unexpectedly created checkpoint output"

# Authority requires F's transient cgroup/processes to be gone before S.
wait_resources save
run_phase save
python3 - "$SAVE" <<'PY'
import json,sys
p=sys.argv[1]; d=json.load(open(p))
assert d.get('status')=='PI05_B1_SPLIT_SAVE_STAGE_PASS', d.get('status')
assert d.get('checkpoint_save_completed') is True
assert d.get('manager_steps')==[10000], d.get('manager_steps')
PY

wait_resources verify
run_phase verify
python3 - "$RESULT" <<'PY'
import json,sys
p=sys.argv[1]; d=json.load(open(p))
assert d.get('status')=='PI05_B1_SPLIT_HARNESS_CHECKPOINT_QUALIFICATION_PASS', d.get('status')
PY

echo "$(ts) PASS split-harness qualification complete; run3 remains unauthorized pending separate authority"
