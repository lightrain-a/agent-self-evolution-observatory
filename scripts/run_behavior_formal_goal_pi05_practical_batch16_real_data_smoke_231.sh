#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY=/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python
CHILD=/data/wyt/formal-goal-portable-openpi-child-231-20260903
PARAMS=/data/wyt/formal-goal-pi05-base-params-v1
PROJ=/data/wyt/behavior-2026-shared26-v3.0-rgb-runtime-repair2
NORM=/data/wyt/behavior-formal-goal-shared26-norm-v1/norm_stats.json
TOKEN=/data/wyt/formal-goal-paligemma-tokenizer-v1/paligemma_tokenizer.model
CACHE=/data/wyt/formal-goal-openpi-cache-v1
SEAL=/data/wyt/formal-goal-231-shared26-whole-manifest-final-seal-20260903.json
AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-practical-batch16-real-data-zero-update-smoke-authority-20260903.json"
RESULT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-practical-batch16-real-data-zero-update-smoke-result-20260903.json"
LOG=/data/wyt/formal-goal-pi05-practical-batch16-real-data-smoke-20260903.log
exec >>"$LOG" 2>&1
[[ -f "$AUTH" && -f "$SEAL" ]] || { echo "authority/seal missing"; exit 3; }
[[ ! -e "$RESULT" ]] || { echo "Refusing replay: $RESULT"; exit 2; }
exec /usr/bin/taskset -c 0-63 /usr/bin/env \
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  TOKENIZERS_PARALLELISM=false JAX_PLATFORMS=cuda XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 OPENPI_DATA_HOME="$CACHE" \
  "$PY" "$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_practical_batch16_real_data_zero_update_smoke.py" \
    --authority "$AUTH" \
    --preregistration "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-practical-single-gpu-batch-preregistration-20260903.json" \
    --synthetic-batch16-result "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-practical-batch16-synthetic-full-step-result-20260903.json" \
    --dataset-seal "$SEAL" \
    --base-receipt "$ROOT/generated/behavior-formal-goal-coupling-pi05-base-transport-repair1-result-20260902.json" \
    --openpi-child-root "$CHILD" --params-root "$PARAMS" --projection-root "$PROJ" \
    --norm-stats "$NORM" --tokenizer "$TOKEN" --receipt "$RESULT"
