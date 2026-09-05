#!/usr/bin/env bash
set -euo pipefail
PHASE=${1:?phase required: save|disk|restore}
ROOT=/data/wyt/formal-goal-pi05-resource-repair-20260902
PY=/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python
CHILD=/data/wyt/formal-goal-portable-openpi-child-231-20260903
PARAMS=/data/wyt/formal-goal-pi05-base-params-v1
BASE="$ROOT/generated/behavior-formal-goal-coupling-pi05-base-transport-repair1-result-20260902.json"
NORM=/data/wyt/behavior-formal-goal-shared26-norm-v1/norm_stats.json
AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-leaf-batched-checkpoint-qualification-authority-231-20260905.json"
REVIEW="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-leaf-batched-checkpoint-independent-review-20260905.json"
SMOKE="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-leaf-batched-orbax-cpu-smoke-20260905.json"
PARENT_A="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-checkpoint-save-96g-resource-failure-adjudication-20260905.json"
REVOKE67="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-host67-user-exclusion-and-authority-revocation-20260905.json"
SERIALIZER="$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_b2_leaf_batched_orbax.py"
SAVE_RUNNER="$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_b2_checkpoint_save_qualification.py"
VERIFY_RUNNER="$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_b2_checkpoint_verify.py"
OUT=/data/wyt/formal-goal-checkpoint-save-qualification-231-20260905/b2-leaf-batched-8gb-52g
SAVE_RESULT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-checkpoint-save-result-231-20260905.json"
DISK_RESULT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-disk-verify-result-231-20260905.json"
RESTORE_RESULT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b2-standard-restore-result-231-20260905.json"
TMPROOT=/data/wyt/formal-goal-b2-tmp-231-20260905
mkdir -p "$TMPROOT"

common_env=(
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  TOKENIZERS_PARALLELISM=false HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
  OPENPI_DATA_HOME=/data/wyt/formal-goal-openpi-cache-v1
  TMPDIR="$TMPROOT" TMP="$TMPROOT" TEMP="$TMPROOT"
  PYTHONPATH="$ROOT"
)

run_unit(){
  local unit=$1 platform=$2; shift 2
  systemd-run --user --unit="$unit" --collect --wait --quiet \
    -p MemoryMax=52G -p MemorySwapMax=0 -p TasksMax=512 -p KillMode=control-group \
    /usr/bin/taskset -c 0-63 /usr/bin/env \
      "${common_env[@]}" JAX_PLATFORMS="$platform" XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
      "$@"
}

case "$PHASE" in
  save)
    [[ ! -e "$OUT" && ! -e "$SAVE_RESULT" && ! -e "$DISK_RESULT" && ! -e "$RESTORE_RESULT" ]] || { echo "B2 save state already exists"; exit 2; }
    run_unit pi05-b2-checkpoint-save-231-20260905.service cuda \
      "$PY" "$SAVE_RUNNER" \
      --authority "$AUTH" --review "$REVIEW" --cpu-smoke "$SMOKE" \
      --parent-a-failure "$PARENT_A" --host67-revocation "$REVOKE67" --serializer "$SERIALIZER" \
      --openpi-child-root "$CHILD" --params-root "$PARAMS" --base-receipt "$BASE" --norm-stats "$NORM" \
      --output-root "$OUT" --result "$SAVE_RESULT"
    ;;
  disk)
    [[ -f "$SAVE_RESULT" && ! -e "$DISK_RESULT" && ! -e "$RESTORE_RESULT" ]] || { echo "B2 disk admission failed"; exit 2; }
    run_unit pi05-b2-disk-verify-231-20260905.service cpu \
      "$PY" "$VERIFY_RUNNER" --mode disk --authority "$AUTH" --save-result "$SAVE_RESULT" \
      --disk-result "$DISK_RESULT" --output-root "$OUT" --result "$DISK_RESULT"
    ;;
  restore)
    [[ -f "$SAVE_RESULT" && -f "$DISK_RESULT" && ! -e "$RESTORE_RESULT" ]] || { echo "B2 restore admission failed"; exit 2; }
    run_unit pi05-b2-standard-restore-231-20260905.service cuda \
      "$PY" "$VERIFY_RUNNER" --mode restore --authority "$AUTH" --save-result "$SAVE_RESULT" \
      --disk-result "$DISK_RESULT" --output-root "$OUT" --result "$RESTORE_RESULT"
    ;;
  *) echo "unknown phase: $PHASE"; exit 2 ;;
esac
