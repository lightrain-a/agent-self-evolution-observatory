#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT=pi05-streaming-accum8x8-safe69-20260903.service
AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-streaming-accum8x8-safe69-authority-20260903.json"
RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-streaming-accum8x8-safe69-result-20260903.json"
WORKER="$ROOT/scripts/run_behavior_formal_goal_pi05_streaming_accum8x8_safe69_worker.sh"
[[ -f "$AUTH" ]] || { echo "authority missing: $AUTH" >&2; exit 3; }
[[ ! -e "$RECEIPT" ]] || { echo "Refusing replay: $RECEIPT" >&2; exit 2; }
if systemctl --user is-active --quiet "$UNIT"; then echo "$UNIT already active"; exit 0; fi
systemd-run --user --unit="$UNIT" --collect --quiet \
  -p MemoryMax=20G -p MemorySwapMax=0 -p TasksMax=512 -p KillMode=control-group \
  /bin/bash "$WORKER"
echo "queued $UNIT"
