#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY=/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python
CHILD=/data/wyt/formal-goal-portable-openpi-child-69-20260903
PARAMS=/data/wyt/formal-goal-pi05-base-params-v1
BASE_RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-pi05-base-transport-repair1-result-20260902.json"
AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-checkpoint-save-96g-resource-qualification-authority-20260905.json"
ADJ="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-throttled-sync-checkpoint-save-4gb-40g-failure-adjudication-20260905.json"
REVIEW="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-checkpoint-resource-independent-review-20260905.json"
OUT=/data/wyt/formal-goal-checkpoint-save-qualification-67-20260905/resource96-sync4gb
RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-checkpoint-save-96g-resource-qualification-result-67-20260905.json"
LOG=/data/wyt/formal-goal-checkpoint-save-96g-resource-qualification-67-20260905.log
exec >>"$LOG" 2>&1
[[ -f "$AUTH" && -f "$ADJ" && -f "$REVIEW" && -f "$BASE_RECEIPT" ]] || { echo "96G checkpoint resource authority/input missing"; exit 3; }
[[ ! -e "$OUT" && ! -e "$RECEIPT" ]] || { echo "Refusing 96G checkpoint resource qualification replay: output/receipt already exists"; exit 2; }
exec /usr/bin/taskset -c 0-63 /usr/bin/env \
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  TOKENIZERS_PARALLELISM=false JAX_PLATFORMS=cuda XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  "$PY" "$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_checkpoint_save_96g_resource_qualification.py" \
    --authority "$AUTH" --adjudication "$ADJ" --review "$REVIEW" \
    --openpi-child-root "$CHILD" --params-root "$PARAMS" --base-receipt "$BASE_RECEIPT" \
    --output-root "$OUT" --receipt "$RECEIPT"
