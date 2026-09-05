#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY=/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python
CHILD=/data/wyt/formal-goal-portable-openpi-child-69-20260903
PARAMS=/data/wyt/formal-goal-pi05-base-params-v1
BASE_RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-pi05-base-transport-repair1-result-20260902.json"
AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-sync-checkpoint-save-64g-qualification-authority-20260905.json"
ADJ="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-async-checkpoint-resource-adjudication-20260905.json"
STAGE1="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-sync-checkpoint-save-40g-failure-adjudication-20260905.json"
OUT=/data/wyt/formal-goal-checkpoint-save-qualification-67-20260905/sync-save-64g
RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-sync-checkpoint-save-64g-qualification-result-67-20260905.json"
LOG=/data/wyt/formal-goal-sync-checkpoint-save-64g-qualification-67-20260905.log
exec >>"$LOG" 2>&1
[[ -f "$AUTH" && -f "$ADJ" && -f "$STAGE1" && -f "$BASE_RECEIPT" ]] || { echo "sync64 checkpoint authority/input missing"; exit 3; }
[[ "$(sha256sum "$STAGE1" | awk '{print $1}')" == "32fdee4f91b4bcb71af84d3b7d04ce8042b17c8535c7e057bea1b630ee963d32" ]] || { echo "sync40 failure lineage SHA drift"; exit 4; }
[[ ! -e "$OUT" && ! -e "$RECEIPT" ]] || { echo "Refusing sync64 checkpoint qualification replay: output/receipt already exists"; exit 2; }
exec /usr/bin/taskset -c 0-63 /usr/bin/env \
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  TOKENIZERS_PARALLELISM=false JAX_PLATFORMS=cuda XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  "$PY" "$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_sync_checkpoint_save_qualification.py" \
    --authority "$AUTH" --adjudication "$ADJ" \
    --openpi-child-root "$CHILD" --params-root "$PARAMS" --base-receipt "$BASE_RECEIPT" \
    --output-root "$OUT" --receipt "$RECEIPT" --expected-memory-max-gib 64
