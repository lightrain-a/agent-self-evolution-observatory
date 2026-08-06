from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .idea_discovery_v3 import bi, child

DEFAULT_JSON = PROJECT_ROOT / "generated" / "idea-discovery-v31.json"
DEFAULT_JS = PROJECT_ROOT / "generated" / "idea-discovery-v31.js"
DEFAULT_EXTERNAL_JSON = PROJECT_ROOT / "generated" / "idea-discovery-v31-external-reviews.json"


CHILDREN: tuple[dict[str,Any], ...] = (
    child("restoration-clause-learning","active-causal-minimal-rollback",bi("恢复子句学习","Restoration-Clause Learning"),"shortlist",
          bi("当前回滚方法只定位一次故障集合，不能把本次干预转化为未来更新组合的持久约束。","Current rollback methods localize one fault set but do not convert interventions into persistent constraints for future update compositions."),
          bi("回滚输出不再只是组件集合，而是可泛化到未来更新描述符的持久 no-good／compatibility 子句。","Rollback outputs persistent no-good and compatibility clauses over update descriptors rather than only a component set."),
          bi("以稀疏高阶因子图表示更新原子及交互，使用 Beta-Bernoulli 结果模型估计回归概率；按单位 rollout 的期望互信息选择启用／禁用干预；通过最小成本 0-1 解码器求解满足回归风险上界的回滚集合；成功恢复后把最小不满足核编译为带来源和置信度的更新兼容子句，约束未来 commit。","Represent update atoms and interactions with a sparse higher-order factor graph and a Beta-Bernoulli outcome model; select enable/disable interventions by expected mutual information per rollout; decode the minimum-cost rollback set under a regression-risk bound; after restoration, compile the minimal unsatisfied core into provenance- and confidence-bearing compatibility clauses that constrain future commits."),
          "persistent update-compatibility clause registry",
          bi("组件组合的随机 rollout 成败、回归幅度和干预成本。","Stochastic rollout success, regression magnitude, and intervention cost for update combinations."),
          bi("注入故障真值；真实历史中以独立回归集是否恢复为可观测真值，未来组合以子句是否提前阻断回退为真值。","Planted fault truth; independent regression-suite restoration for real histories; future-composition regressions prevented by learned clauses."),
          bi("ProbDD、PMA、Delta Debugging、Causal Agent Replay，以及拿到同一历史先验但不学习兼容子句的版本。","ProbDD, PMA, delta debugging, Causal Agent Replay, and a matched-history variant that does not learn compatibility clauses."),
          bi("第一阶段匹配干预预算定位当前故障；第二阶段冻结已学子句，在未见更新组合与第二模型上测量回退率、所需干预数和错误阻断率。","Match intervention budgets for current localization, then freeze learned clauses and test regressions, interventions, and false blocks on unseen update combinations and a second model."),
          bi("若同历史先验的 ProbDD/PMA 在未来组合上达到相同回退率，或子句错误阻断率超过 5%，则停止。","Stop if ProbDD/PMA with the same history matches future-composition regression rate or clause false-block rate exceeds 5%."),
          ("versioned update harness","ALFWorld","WebArena-Lite","two open models"),("reviewer-vector-repair","method-tree-search","experiment-feedback-induction"),(4,5,5,4,5,4)),
    child("randomized-memory-action-policy","future-reuse-harm-predictor",bi("随机化记忆动作策略","Randomized Memory-Action Policy"),"shortlist",
          bi("写入、摘要、隔离和删除对未来复用有不同潜在结果，但现有记忆准入只观察被选择动作。","Write, summarize, quarantine, and drop have different future potential outcomes, while current admission observes only the chosen action."),
          bi("在检索发生前对候选条目动作进行受支持随机化，直接学习动作特异的未来复用效应。","Randomize candidate-entry actions before retrieval exposure and directly learn action-specific future reuse effects."),
          bi("使用分层探索策略在 write／summarize／quarantine／drop 间随机化；以跨拟合 doubly-robust 估计器学习每个动作的未来效用与伤害；用带支持约束的悲观策略目标最大化效用下界，并以固定 margin 和不确定性阈值执行动作或弃判。","Randomize among write/summarize/quarantine/drop with stratified exploration; learn future utility and harm using cross-fitted doubly robust estimators; optimize a support-constrained pessimistic lower bound and execute or abstain with frozen margin and uncertainty thresholds."),
          "bounded memory-action policy and entry registry",
          bi("预检索随机动作、未来任务检索暴露、环境回报、回退和 Token 成本。","Pre-retrieval randomized actions, future retrieval exposure, environment reward, regression, and token cost."),
          bi("随机化产生的动作特异潜在结果估计；留出时间任务上的环境真值。","Randomization-supported action-specific potential outcomes and environment truth on chronological holdout tasks."),
          bi("A-MAC、未来效用保留、风险敏感 contextual bandit、成功即写入和只删除策略。","A-MAC, future-utility retention, risk-sensitive contextual bandits, success-only write, and deletion-only policies."),
          bi("固定探索、记忆容量、检索次数和 Token 预算，在两个任务域训练并冻结到第三任务域；主表报告效用下界、负迁移和有效覆盖。","Fix exploration, capacity, retrieval, and token budgets; train on two domains and freeze to a third; report utility lower bound, negative transfer, and valid coverage."),
          bi("若悲观策略不优于标准 contextual bandit，或跨域有效覆盖低于 40%，则停止。","Stop if the pessimistic policy does not beat a standard contextual bandit or cross-domain valid coverage is below 40%."),
          ("ALFWorld","WebArena-Lite","ToolBench subset","two open models"),("reviewer-vector-repair","resource-grounded-design"),(4,5,5,3,4,3)),
    child("placebo-calibrated-memory-effects","replicated-effect-memory-gate",bi("安慰剂校准的记忆效应模型","Placebo-Calibrated Memory Effects"),"shortlist",
          bi("无记忆对照无法区分语义帮助与单纯增加上下文、位置或执行难度的效应。","A no-memory control cannot separate semantic help from context-length, position, or execution-difficulty effects."),
          bi("使用预注册、Token 与位置匹配、任务不相交的无关记忆作为负对照，并把负对照泄漏显式纳入后验。","Use preregistered token/position-matched task-disjoint irrelevant memories as negative controls and model placebo leakage explicitly."),
          bi("对成功率使用 motif 随机截距的 Beta-Binomial 分层模型，对连续回报使用共享方差层次模型；估计 retrieved−no-memory 的总效应与 placebo−no-memory 的非语义效应，语义效应为二者差；仅当伤害后验超过阈值且 placebo 校准误差在界内时隔离或删除，否则弃判。","Use a Beta-Binomial hierarchical model with motif random intercepts for success and a shared-variance hierarchy for continuous reward; estimate total retrieved-minus-none and nonsemantic placebo-minus-none effects, defining semantic effect as their difference; quarantine/delete only when harm posterior exceeds a frozen threshold and placebo calibration error is bounded, otherwise abstain."),
          "memory effect posterior and quarantine registry",
          bi("检索、无记忆和受控无关记忆三臂的 matched future-task replay。","Matched future-task replay under retrieved, no-memory, and controlled irrelevant-memory arms."),
          bi("预注册安慰剂池的任务不相交性、环境回报和跨 seed 重复效应。","Preregistered task-disjoint placebo pool, environment rewards, and cross-seed replicated effects."),
          bi("两臂经验贝叶斯、SkillCAT、普通三臂均值差、A-MAC。","Two-arm empirical Bayes, SkillCAT, ordinary three-arm mean differences, and A-MAC."),
          bi("冻结安慰剂池、似然、先验和阈值，在第二模型和第二任务域复用；匹配总回放、上下文和存储预算。","Freeze placebo pool, likelihood, prior, and thresholds, then reuse on a second model/domain under matched replay, context, and storage budgets."),
          bi("若受控安慰剂不改变伤害归因，或第二模型上不优于两臂经验贝叶斯，则停止。","Stop if controlled placebo does not change harm attribution or fails to beat two-arm empirical Bayes on a second model."),
          ("ALFWorld","WebArena-Lite","task-disjoint placebo generator"),("reviewer-vector-repair","resource-grounded-design"),(4,5,5,4,4,3)),
    child("conformal-effect-transport-gate","cross-task-effect-transport-certificate",bi("Conformal 效应迁移门控","Conformal Effect-Transport Gate"),"shortlist",
          bi("经验效应在源任务上可估计，但目标任务族没有标签且支持可能不重叠。","Lesson effects are estimable on source tasks, while target families are unlabeled and may lack support overlap."),
          bi("只在可证明支持重叠的区域输出效应符号，并对错误迁移提供有限样本风险控制。","Predict effect sign only within verified support overlap and provide finite-sample risk control for harmful transfer."),
          bi("用交叉拟合 R-learner 估计条目处理效应；通过跨环境 IRM 惩罚学习不变状态—约束表示；以密度比和最近邻半径执行 positivity／support 检查；在源环境 leave-one-family-out 残差上校准 conformal 风险集合，部署时仅在效应符号风险低于冻结 α 时准入。","Estimate entry-level effects with a cross-fitted R-learner; learn invariant state-constraint representations with an across-environment IRM penalty; enforce positivity/support using density ratios and neighbor radii; calibrate conformal risk sets on leave-one-family-out source residuals and admit only when frozen sign-error risk is below alpha."),
          "lesson transport certificate and admission registry",
          bi("源任务族中的随机化或 matched replay、环境描述和条目效应。","Randomized or matched replay, environment descriptors, and entry effects in source families."),
          bi("完全留出任务族的效应符号；部署不读取目标标签或额外 replay。","Effect sign on fully held-out task families with no target labels or deployment replay."),
          bi("带 conformal 弃判的 R-learner、语义相似度、SkillCAT、可迁移记忆方法。","Conformal-abstaining R-learner, semantic similarity, SkillCAT, and transferable-memory methods."),
          bi("四源任务族 leave-one-out 校准，第五任务族与第二模型双重冻结；相同记忆与 replay 预算下测符号错误风险和覆盖。","Use leave-one-out calibration on four source families and double-freeze to a fifth family and second model; measure sign-error risk and coverage under matched budgets."),
          bi("若有限样本风险上界失效，或在覆盖≥40% 时不优于 conformal R-learner，则停止。","Stop if finite-sample risk control fails or it does not beat conformal R-learning at at least 40% coverage."),
          ("four source task families","one held-out family","two open models"),("reviewer-vector-repair","concept-path-bridging"),(4,5,5,2,5,2)),
    child("verified-risk-predicate-grammar","simulator-distilled-risk-memory",bi("验证器约束的风险谓词语法","Verifier-Constrained Risk-Predicate Grammar"),"shortlist",
          bi("反事实安全轨迹可以由模拟器验证，但自由文本记忆无法保证可靠性、最小性或冲突一致性。","Counterfactual safety traces can be verified, but free-text memory does not guarantee reliability, minimality, or conflict consistency."),
          bi("持久更新对象是固定 DSL 中可执行、可验证、带弃权的风险谓词语法，而不是自然语言经验。","The persistent update is an executable, verifiable, abstaining risk-predicate grammar in a fixed DSL rather than free-text experience."),
          bi("预定义状态谓词、动作谓词和时序窗口 DSL；优化 MDL 目标：谓词复杂度 + λ_FN·验证器假阴性 + λ_FP·验证器假阳性；用逐步约束添加生成候选，以独立转移验证器接受；冲突按条件蕴含形成 specificity lattice，仅在唯一最具体规则存在时执行，否则弃判。","Define a DSL of state predicates, action predicates, and temporal windows; optimize an MDL objective combining grammar complexity, verifier false negatives, and false positives; generate candidates by incremental constraint addition and accept them with an independent transition verifier; resolve conflicts through an implication-based specificity lattice and abstain unless a unique most-specific rule exists."),
          "versioned executable risk grammar",
          bi("反事实状态替换、动作后果、验证器标签和谓词复杂度。","Counterfactual state substitutions, action outcomes, verifier labels, and predicate complexity."),
          bi("独立转移验证器；跨 seed 与跨转移系统的安全违反和弃判。","Independent transition verifier and safety violations/abstention across seeds and transition systems."),
          bi("CLIN、Memory-as-a-Tool、ICAL、决策树规则、无压缩验证轨迹库。","CLIN, Memory-as-a-Tool, ICAL, decision-tree rules, and an uncompressed verified-trace store."),
          bi("在一个系统归纳语法，冻结 DSL、λ 和冲突规则，迁移到第二转移系统且关闭模拟器；匹配记忆和推理 Token。","Induce on one system, freeze DSL/lambdas/conflict rules, transfer to a second transition system with simulator disabled, and match memory/inference tokens."),
          bi("若第二系统上安全召回不优于验证轨迹检索，或规则弃判率>50%，则停止。","Stop if safety recall on the second system does not beat verified-trace retrieval or abstention exceeds 50%."),
          ("PDDL-style transition verifier","two transition systems","Qwen2.5-7B-Instruct"),("reviewer-vector-repair","resource-grounded-design","concept-path-bridging"),(5,5,5,4,4,4)),
    child("paired-regret-update-policy","counterfactual-evolution-decision-controller",bi("配对后悔更新策略","Paired-Regret Update Policy"),"shortlist",
          bi("标准离线控制器不能利用同一进化状态下 continue／commit／rollback／stop 的完整配对结果。","Standard offline controllers do not exploit complete paired outcomes for continue/commit/rollback/stop from the same evolution state."),
          bi("学习目标从值函数拟合改为同状态动作对之间的后悔上界，并禁止数据支持外动作。","Replace value fitting with within-state pairwise regret bounds and forbid unsupported actions."),
          bi("对每个冻结状态—候选序列执行四动作得到 Y_a；训练共享表示和成对后悔 r(a,b|s)=Y_b−Y_a，使用非对称 Huber 排序损失；策略选择最小悲观后悔上界的动作，并施加 kNN 支持半径与回退风险约束；所有阈值在校准流冻结。","Execute all four actions for each frozen state-candidate sequence to obtain Y_a; train shared representations and pairwise regrets r(a,b|s)=Y_b−Y_a with an asymmetric Huber ranking loss; choose the action minimizing a pessimistic regret bound under kNN support and regression-risk constraints; freeze thresholds on a calibration stream."),
          "persistent evolution decision policy",
          bi("同一状态和候选序列下四动作的配对结果、成本和未来回退。","Paired outcomes, costs, and future regressions for four actions from the same state/candidate sequence."),
          bi("独立冻结任务流上的真实累计效用、最坏回退和候选不变性。","True cumulative utility, worst regression, and candidate invariance on a frozen independent stream."),
          bi("CQL/IQL 类离线 RL、阈值策略、Bandit、固定轮数和标准 pairwise ranking。","CQL/IQL-style offline RL, thresholds, bandits, fixed rounds, and standard pairwise ranking."),
          bi("在一个更新表面生成完整四动作数据，固定候选序列；跨第二模型和任务域冻结，比较同等数据支持下的 regret 与回退。","Generate complete four-action data for one update surface with fixed candidate sequences; freeze across a second model/domain and compare regret/regression under identical support."),
          bi("若不优于标准离线 RL 或阈值策略，或收益依赖重新生成候选，则停止。","Stop if it does not beat standard offline RL or thresholds, or if gains require regenerated candidates."),
          ("complete four-action replay dataset","two open models","two task domains"),("reviewer-vector-repair","experiment-feedback-induction"),(4,5,5,3,4,3)),
)


def _load_reviews() -> dict[str,list[dict[str,Any]]]:
    if not DEFAULT_EXTERNAL_JSON.exists(): return {}
    try: payload=json.loads(DEFAULT_EXTERNAL_JSON.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): return {}
    return payload.get("reviews",{}) if isinstance(payload.get("reviews",{}),dict) else {}


def build_idea_discovery_v31() -> dict[str,Any]:
    external=_load_reviews();rows=[]
    for rank,item in enumerate(CHILDREN,1):
        row=dict(item); reviews=external.get(row["id"],[]); latest=reviews[-1] if reviews else {}
        row.update(internal_rank=rank,external_reviews=reviews,external_review_status="reviewed" if reviews else "pending",external_verdict=latest.get("verdict","pending"),external_confidence=latest.get("confidence",""));rows.append(row)
    verdicts=[row["external_verdict"] for row in rows if row["external_review_status"]=="reviewed"]
    return {"schema_version":"1.0","generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"round":"v3.1","status":"external-reviewed" if len(verdicts)==len(rows) else "reviewer-vector-repair","policy":{"parents_only_from_v3_revise":True,"blocked_parents_stopped":True,"main_bank_unchanged":True,"external_review_required_before_reconciliation":True},"summary":{"children":len(rows),"external_reviewed":len(verdicts),"external_pending":len(rows)-len(verdicts),"external_pass":verdicts.count("pass"),"external_revise":verdicts.count("revise"),"external_block":verdicts.count("block")},"children":rows}


def validate(payload:dict[str,Any])->list[str]:
    errors=[];rows=payload.get("children",[])
    if len(rows)!=6: errors.append("expected six v3.1 children")
    for row in rows:
        if not row.get("exact_mechanism",{}).get("zh") or not row.get("update_surface") or not row.get("independent_ground_truth",{}).get("en"): errors.append(f"incomplete child: {row.get('id')}")
    return errors


def write_idea_discovery_v31(json_path:Path=DEFAULT_JSON,js_path:Path=DEFAULT_JS)->dict[str,Any]:
    payload=build_idea_discovery_v31();errors=validate(payload)
    if errors: raise ValueError("Invalid idea discovery v3.1: "+"; ".join(errors))
    json_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    js_path.write_text("window.IDEA_DISCOVERY_V31 = "+json.dumps(payload,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return payload


if __name__=="__main__": print(json.dumps(write_idea_discovery_v31()["summary"],ensure_ascii=False))
