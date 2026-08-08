window.REVIEW_FINDING_ZH = {
  "regression-gated-self-evolution":"在低资源 ICLR 设置下，最强且最清楚的论文边界是把自进化写成受约束策略改进：回归测试与当前任务收益相互隔离，成本严格匹配，每次持久更新都必须经过可审计的 commit／rollback 决策。",
  "contradiction-preserving-consolidation":"通用记忆巩固已经较拥挤，但收窄后仍有独立边界：在完全相同的存储与检索预算下，用‘保留或删除某条记忆是否会改变下游结论’来因果定义记忆价值，并优化最小的结论改变证据集。这比覆盖率、相似度、矛盾检测或完整历史重访更具体。",
  "compositional-update-compatibility":"仍存在一个较窄的独立主张：现有工作流搜索和模块组合工作并未直接预测多个持久更新之间的顺序敏感回归。论文必须限定在‘单独有效、已版本化更新的未见组合’上，并证明模型能够预测留出顺序和高阶组合，而不是退化为普通图性能预测。",
  "update-trust-region":"收窄后的独立边界仍成立：已有工作覆盖参数更新的 trust region、Prompt 小步变异或技能编辑的 held-out gate，但尚未直接定义并验证针对持久非参数 Agent 更新的 occupancy-level trust region，同时联合轨迹、动作、工具路由和记忆检索分布，并检验该距离是否比文本编辑量或当前任务收益更能预测未来回归。"
};

window.REVIEW_ACTION_ZH = {
  "regression-gated-self-evolution":"在每一轮进化后，以相同的交互、Token、模型调用和训练预算报告持久能力增益与能力回退。",
  "contradiction-preserving-consolidation":"将宽泛的三领域 Pilot 改为固定容量基准，加入可由 Oracle 验证、确实会改变结论的证据，并在相同存储与检索 Token 预算下对比近期记忆巩固方法。",
  "compositional-update-compatibility":"把更新表面冻结为版本化的 Prompt、记忆或工作流提交，预注册留出的更新顺序对与三更新组合测试，并在相同执行和测试预算下对比任务条件化图预测器。",
  "update-trust-region":"在宣称统一适用于 Prompt、记忆和工作流的信赖域前，预注册一个非参数更新表面和一个独立采样的占用分布差异估计器。",
  "retrieval-interference-auditor":"定义条目级准入／隔离策略，唯一更新信号来自检索记忆、打乱记忆和无记忆三臂重放的重复效应估计，再在按时间划分的留出任务流上冻结测试。",
  "irreversible-action-counterfactuals":"收窄到一个具有精确独立状态转移验证器的环境，采用先发现后冻结的协议：在固定模拟器调用预算下学习反事实风险记忆，评测时关闭模拟器。",
  "self-label-confidence-flow":"预注册多轮 Pilot，在完全相同的生成样本和评价器调用下，对比形式化的谱系置信度模型、当前轮置信度、CREAM 类一致性和独立 Judge 校准。",
  "evaluator-coadaptation-guard":"实现一个学习式的“执行者版本×评价器版本”交互残差门控器，并在未来留出轮次上对比冻结 Reward、最新版本配对和等调用预算的 Reward Ensemble。",
  "recovery-conditioned-experience":"把更新表面固定为有容量上限的外部经验记忆，根据独立测量的未来复用伤害学习恢复完整度，而不是手工规定终点、重新汇合和残差检查。",
  "counterexample-generating-curriculum":"将 Pilot 限定在一个验证器充分的环境中，并通过约束删除或针对显式策略规则的 Delta Debugging 操作化定义反例最小性。",
  "workflow-generalization-certificate":"在独立生成的工作流候选上定义并校准提交前接受统计量，再在相同总评测预算下验证它对未见工具 API 和任务图模式的未来性能预测。",
  "budgeted-evolution-controller":"为一个持久更新表面构建可做反事实比较的重放数据集，使继续、提交、回滚和停止能从同一个进化状态比较，而不是重新生成不同候选序列。",
  "lineage-aware-rollback":"将工作重构为因果最小集合回滚：显式识别依赖、处理交互，并建立带真值的回滚基准，而不是把谱系存储本身当作主要贡献。",
  "failure-frontier-curriculum":"用形式化的相邻 Checkpoint 判别分数替代宽泛的失败前沿主张，并直接检验它是否比成功概率、失败重放和验证梯度对齐更能预测留出改进。",
  "causally-verified-experience-admission":"将源任务上的因果准入改为机制上不同的跨任务可迁移性证书，预测一条经验的效果能否跨任务族保持，并直接对比 SCORE、SkillCAT 和 A-MAC。",
  "reward-invariance-audit":"不要把审计本身作为论文主线；转向学习式 Reward 更新机制，使用独立认证的因果与中性干预，并证明其下游策略选择优于 CROME 和 PRISM。",
  "local-counterexample-memory-repair":"只有在形式化单调的适用集合专化算子、保存可执行的例外谱系，并在等编辑预算下优于 SkillTracer 和 SkillAdaptor 地保留未受影响正例时，才重新推进。",
  "self-correction-collapse-detector":"停止把独立检测器作为主线，只把反事实敏感性作为消融或门控信号，嵌入一个具有新持久学习机制的自纠错方法。",
  "intervention-validated-self-correction":"重构为失败分析基准，在匹配的干预和 Rollout 预算下识别 InT 与 REFLECT 类受控重放会产生错误纠正归因的场景。",
  "workflow-branch-credit":"把分支归因并入组合更新兼容性，作为归因与评测子系统，停止将其作为独立论文推进。",
  "world-model-error-gated-learning":"停止当前独立 Idea；只有在能定义形式上不同且可校准的动作排序变化目标，并用独立干预真值评测 LLM 世界模型时再重启。",
  "memory-half-life":"停止独立方法开发，将其并入一个具有干预真值的记忆陈旧风险估计受控基准。",
  "correction-policy-credit":"停止独立方法开发，重构为类型化纠正动作归因基准，并使用可执行的逐动作留一干预真值。",
  "curriculum-drift-controller":"停止作为独立论文主线，只作为具有真正新更新机制的方法中的评测或治理组件。",
  "outcome-equivalent-trajectory-contrast":"停止当前提案；只有在用独立验证的反事实过程干预替代结果匹配、从而得到可识别的不变性证据后才重启。",
  "applicability-bounded-lessons":"停止独立 Idea，将其反例或弃权表示并入 Assay 类因果技能选择基线；除非能提出形式化且可校准的支持集合学习器。",
  "regression-probe-half-life":"预注册按时间顺序、版本不重叠的 Probe 效用模型，唯一持久更新对象为 Probe Registry，并在相同 Probe 预算下对比最近优先、IRT、PACE 类选择、随机退役和全部保留。",
  "version-differential-failure-localization":"用学习式预算受限干预策略替代通用最小子集替换；策略在历史版本回退上训练，并在未见模型、版本和故障组合上对比 Delta Debugging。",
  "model-swap-compatibility-certificate":"明确并训练带不确定性和弃权的资产级校准预测器，同时要求在留出目标模型家族和留出资产类别上泛化。",
  "update-aware-permission-downgrade":"引入校准的更新到权限影响模型，输出临时权限集合和重新授权 Probe，并在训练中未出现的更新算子上评测。",
  "cross-form-capability-transfer-gap":"先从规范化潜在程序构建任务组，并机械验证分类、生成和执行三种渲染器，再训练任何更新表面路由器。",
  "delayed-regression-exams":"形式化并实现带来源信息的回退发生时间风险模型，以迁移到留出的更新顺序作为主实验。",
  "privilege-recovery-curriculum":"用校准的失败到 Probe 策略替代手写恢复阶梯，预测最小安全权限增量，并以留出失败族迁移作为主评测。",
  "behavior-triggered-privilege-lease":"用学习式、版本条件化的租约控制器替代手工续租与撤销规则；控制器由独立 Canary 结果训练，并在相同权限上限下对比任务条件动态授权和提交时重新认证。",
  "recurrent-failure-contract-compilation":"停止作为独立 Idea，将带过期条件的契约验证并入更广义的轨迹到技能或行为契约项目。",
  "change-triggered-regression-exams":"用因果可识别的更新到失败模型替代普通测试选择机制，并证明其具有预测式测试选择无法提供的迁移或覆盖性质。",
  "swap-aware-regression-localization":"将因子替换协议并入模型替换兼容性证书，作为真值标签生成器和评测 Oracle，停止独立推进。"
};

window.localizedReviewFinding = function localizedReviewFinding(ideaId, review, lang) {
  if (!review) return "";
  if (lang === "zh") return review.finding_zh || window.REVIEW_FINDING_ZH[ideaId] || review.finding || "";
  return review.finding || review.finding_en || review.finding_zh || "";
};

window.localizedReviewAction = function localizedReviewAction(ideaId, review, lang) {
  if (!review) return "";
  if (lang === "zh") return review.required_action_zh || window.REVIEW_ACTION_ZH[ideaId] || review.required_action || "";
  return review.required_action || review.required_action_en || "";
};
