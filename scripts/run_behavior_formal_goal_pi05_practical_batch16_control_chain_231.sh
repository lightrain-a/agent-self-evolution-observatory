#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY=/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python
READY=/data/wyt/formal-goal-231-shared26-batch16.READY
SEAL=/data/wyt/formal-goal-231-shared26-whole-manifest-final-seal-20260903.json
SMOKE_AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-practical-batch16-real-data-zero-update-smoke-authority-20260903.json"
SMOKE_RESULT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-practical-batch16-real-data-zero-update-smoke-result-20260903.json"
TRAIN_AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-practical-batch16-formal-training-authority-20260903.json"
TRAIN_PROGRESS="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-practical-batch16-formal-training-progress-20260903.json"
TRAIN_RESULT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-practical-batch16-formal-training-result-20260903.json"
SMOKE_RUNNER="$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_practical_batch16_real_data_zero_update_smoke.py"
SMOKE_COMPILER="$ROOT/research_pipeline/compile_behavior_formal_goal_pi05_practical_batch16_real_data_smoke_authority.py"
SMOKE_LAUNCHER="$ROOT/scripts/run_behavior_formal_goal_pi05_practical_batch16_real_data_smoke_231.sh"
TRAIN_RUNNER="$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_practical_batch16_formal_train.py"
TRAIN_COMPILER="$ROOT/research_pipeline/compile_behavior_formal_goal_pi05_practical_batch16_formal_training_authority.py"
TRAIN_LAUNCHER="$ROOT/scripts/run_behavior_formal_goal_pi05_practical_batch16_formal_train_231.sh"
LOG=/data/wyt/formal-goal-pi05-practical-batch16-control-chain-231-20260903.log
exec >>"$LOG" 2>&1
printf '[%s] practical batch16 control chain start\n' "$(date --iso-8601=seconds)"

psi_avg10() {
  awk '/^some / {for(i=1;i<=NF;i++) if($i~/^avg10=/){split($i,a,"=");print a[2];exit}}' "$1"
}
wait_resource() {
  local min_avail_kib="$1"
  while true; do
    apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null | awk 'NF{n++} END{print n+0}')
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk 'NR==1{print int($1)}')
    avail=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
    mp=$(psi_avg10 /proc/pressure/memory); ip=$(psi_avg10 /proc/pressure/io)
    if awk -v a="$apps" -v g="$used" -v m="$avail" -v need="$min_avail_kib" -v mp="$mp" -v ip="$ip" 'BEGIN{exit !(a==0 && g<1024 && m>=need && mp<1.0 && ip<5.0)}'; then
      printf '[%s] resource admission PASS apps=%s gpu_mib=%s avail_kib=%s mp=%s ip=%s\n' "$(date --iso-8601=seconds)" "$apps" "$used" "$avail" "$mp" "$ip"
      return 0
    fi
    printf '[%s] resource wait apps=%s gpu_mib=%s avail_kib=%s mp=%s ip=%s\n' "$(date --iso-8601=seconds)" "$apps" "$used" "$avail" "$mp" "$ip"
    sleep 30
  done
}
json_status() {
  "$PY" - "$1" <<'PY'
import json,sys
try: print(json.load(open(sys.argv[1])).get('status',''))
except Exception: print('')
PY
}

while [[ ! -f "$READY" || ! -f "$SEAL" ]]; do
  printf '[%s] waiting shared26 READY/seal\n' "$(date --iso-8601=seconds)"
  sleep 30
done
printf '[%s] shared26 READY: %s\n' "$(date --iso-8601=seconds)" "$(cat "$READY")"

if [[ ! -e "$SMOKE_RESULT" ]]; then
  if [[ ! -e "$SMOKE_AUTH" ]]; then
    "$PY" "$SMOKE_COMPILER" --dataset-seal "$SEAL" --runner "$SMOKE_RUNNER" --launcher "$SMOKE_LAUNCHER" --output "$SMOKE_AUTH"
  fi
  wait_resource 41943040
  systemd-run --user --unit=pi05-practical-batch16-real-data-smoke-231-20260903.service --collect \
    -p MemoryMax=40G -p MemorySwapMax=0 -p TasksMax=512 -p KillMode=control-group \
    /bin/bash "$SMOKE_LAUNCHER"
  while systemctl --user is-active --quiet pi05-practical-batch16-real-data-smoke-231-20260903.service; do sleep 10; done
fi
SMOKE_STATUS=$(json_status "$SMOKE_RESULT")
printf '[%s] smoke status=%s\n' "$(date --iso-8601=seconds)" "$SMOKE_STATUS"
if [[ "$SMOKE_STATUS" != PI05_PRACTICAL_BATCH16_REAL_DATA_ZERO_UPDATE_PASS ]]; then
  echo "real-data smoke not PASS; chain stops"
  exit 4
fi

if [[ -e "$TRAIN_PROGRESS" || -e "$TRAIN_RESULT" ]]; then
  echo "formal training progress/result already exists; refusing replay"
  exit 0
fi
if [[ ! -e "$TRAIN_AUTH" ]]; then
  "$PY" "$TRAIN_COMPILER" --dataset-seal "$SEAL" --real-data-smoke "$SMOKE_RESULT" --trainer "$TRAIN_RUNNER" --launcher "$TRAIN_LAUNCHER" --output "$TRAIN_AUTH"
fi
wait_resource 41943040
systemd-run --user --unit=pi05-practical-batch16-formal-train-231-20260903.service --collect \
  -p MemoryMax=40G -p MemorySwapMax=0 -p TasksMax=512 -p KillMode=control-group \
  /bin/bash "$TRAIN_LAUNCHER"
printf '[%s] formal training launched; chain exits\n' "$(date --iso-8601=seconds)"
