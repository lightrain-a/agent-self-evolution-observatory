#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT=pi05-direct-device-no-update-model-load-20260902.service
RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-direct-device-no-update-model-load-result-20260902.json"
WORKER="$ROOT/scripts/run_behavior_formal_goal_coupling_pi05_direct_device_no_update_model_load_worker.sh"

[[ ! -e "$RECEIPT" ]] || { echo "Refusing replay: $RECEIPT" >&2; exit 2; }

if systemctl --user is-active --quiet "$UNIT"; then
  echo "$UNIT already active"
  exit 0
fi

systemd-run --user --unit="$UNIT" --collect --quiet \
  -p MemoryMax=20G \
  -p MemorySwapMax=0 \
  -p TasksMax=512 \
  -p KillMode=control-group \
  /bin/bash "$WORKER"

echo "queued $UNIT"
