#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIRECT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-direct-device-no-update-model-load-result-20260902.json"
AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-streaming-accum8x8-safe69-authority-20260903.json"
FINAL="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-streaming-accum8x8-safe69-result-20260903.json"
LOG=/data/wyt/formal-goal-pi05-direct-to-streaming8x8-safe69-chain-20260903.log
exec >>"$LOG" 2>&1
printf '[%s] chain start\n' "$(date --iso-8601=seconds)"
while [[ ! -e "$DIRECT" ]]; do sleep 30; done
STATUS=$(python3 -c "import json; print(json.load(open('$DIRECT')).get('status',''))")
if [[ "$STATUS" != PI05_DIRECT_DEVICE_NO_UPDATE_MODEL_LOAD_PASS ]]; then
  echo "direct-device gate failed/held: $STATUS; no streaming authority"; exit 4
fi
if [[ ! -e "$AUTH" ]]; then
  python3 "$ROOT/research_pipeline/compile_behavior_formal_goal_pi05_streaming_accum8x8_safe69_authority.py" \
    --direct-result "$DIRECT" \
    --runner "$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_accum8x8_streaming_direct_device_dry_gradient.py" \
    --worker "$ROOT/scripts/run_behavior_formal_goal_pi05_streaming_accum8x8_safe69_worker.sh" \
    --launcher "$ROOT/scripts/run_behavior_formal_goal_pi05_streaming_accum8x8_safe69.sh" \
    --design "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum8x8-streaming-direct-device-repair2-design-20260903.json" \
    --output "$AUTH"
fi
[[ ! -e "$FINAL" ]] || { echo "streaming result already exists; no replay"; exit 0; }
exec "$ROOT/scripts/run_behavior_formal_goal_pi05_streaming_accum8x8_safe69.sh"
