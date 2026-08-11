function fourDirectionExperimentEvidence(id){
  const latest=(p0FourDirectionIteration().ideas||{})[id]; if(!latest)return null;
  const zh=language==="zh", n=experimentNumber;
  if(id==="update-trust-region"){
    const m=latest.metrics||{};
    return {current_started:true,category:"p0-stop",tone:"check",label:zh?"最新迭代 · 并入 B-9 诊断":"Latest iteration · merge diagnostic into B-9",detail:zh?`zero-reward blast-radius：harm AUROC=${n(m.harm_auc)} < ${n(m.required_harm_auc)}；pick_cool family gap=${n(m.pick_cool_family_gap)}，方向翻转。A-1 standalone 停止，scope score 仅保留诊断。`:`Zero-reward blast-radius: harm AUROC=${n(m.harm_auc)} < ${n(m.required_harm_auc)}; pick_cool family gap=${n(m.pick_cool_family_gap)} reverses direction. Stop standalone A-1; retain scope score only as a diagnostic.`,next:latest.next_action,evidence:`${latest.decision} · ${latest.failure_class}`};
  }
  if(id==="budgeted-evolution-controller"){
    const m=latest.metrics||{};
    return {current_started:true,category:"p0-hold",tone:"check",label:zh?"最新迭代 · KEEP 问题 / upstream HOLD":"Latest iteration · KEEP problem / upstream HOLD",detail:zh?`最佳 fixed horizon 与 oracle checkpoint 完全等价仅 ${n(m.best_fixed_oracle_equivalence)}，远低于 ${n(m.fixed_horizon_ceiling)} ceiling；sequential-control 仍有 headroom，但当前没有合格 persistent updater/admission stream，禁止 controller training。`:`Best fixed horizon matches the oracle checkpoint on only ${n(m.best_fixed_oracle_equivalence)}, far below the ${n(m.fixed_horizon_ceiling)} ceiling; sequential-control headroom remains, but controller training is blocked until a qualified persistent updater/admission stream exists.`,next:latest.next_action,evidence:`${latest.decision} · ${latest.failure_class}`};
  }
  if(id==="replicated-effect-memory-gate"){
    const m=latest.metrics||{};
    return {current_started:true,category:"p0-stop",tone:"check",label:zh?"最新迭代 · standalone STOP / 并入 B-9":"Latest iteration · standalone STOP / merge into B-9",detail:zh?`12 candidates 已够，但 replicated stable harm=${m.replicated_stable_harm_candidates}/${m.required_harm_candidates}、benefit=${m.replicated_stable_benefit_candidates}/${m.required_benefit_candidates}。冻结 complementary repair 后仍未过 candidate-level replication gate；当前 substrate 不再扩样。`:`Candidate count is sufficient, but replicated stable harm=${m.replicated_stable_harm_candidates}/${m.required_harm_candidates} and benefit=${m.replicated_stable_benefit_candidates}/${m.required_benefit_candidates}. The frozen complementary repair still fails candidate-level replication; no more same-substrate expansion.`,next:latest.next_action,evidence:`${latest.decision} · ${latest.failure_class}`};
  }
  if(id==="cross-task-effect-transport-certificate"){
    const s=latest.support_metrics||{},m=latest.final_method_metrics||{};
    return {current_started:true,category:"p0-stop",tone:"fail",label:zh?"最新迭代 · Support PASS / Method development STOP":"Latest iteration · Support PASS / Method development STOP",detail:zh?`P0-Support：stable nonzero=${s.stable_controlled_nonzero}/${s.required_stable_controlled_nonzero}，eligible folds=${s.eligible_target_family_folds}/${s.required_target_family_folds}，均 PASS。但最终 response-signature×target-structure child 的 sign AUC=${n(m.nonzero_sign_auc)}，最强 simple baseline=${n(m.strongest_baseline_auc)}，advantage=${n(m.auc_advantage)}，permutation p=${n(m.permutation_p)}；不打开 fresh-heldout GPU。`:`P0-Support passed at stable nonzero=${s.stable_controlled_nonzero}/${s.required_stable_controlled_nonzero} and eligible folds=${s.eligible_target_family_folds}/${s.required_target_family_folds}. The final response-signature × target-structure child has sign AUC=${n(m.nonzero_sign_auc)} vs strongest simple baseline=${n(m.strongest_baseline_auc)}, advantage=${n(m.auc_advantage)}, permutation p=${n(m.permutation_p)}; no fresh-heldout GPU is opened.`,next:latest.next_action,evidence:`${latest.decision} · Support=${latest.p0_support_status} · formal method result=LOCKED`};
  }
  return null;
}
