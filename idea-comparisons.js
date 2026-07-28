window.IDEA_COMPARISONS = {
  "NegEvoBench-V": {
    importance:{en:"Self-evolution claims are unreliable if evaluation only records final average performance. A benchmark that exposes delayed harm, unsafe dependencies, and failed recovery is foundational infrastructure for comparing every later method.",zh:"如果评测只记录最终平均性能，自进化主张就不可靠。能够暴露延迟伤害、不安全依赖和恢复失败的基准，是后续所有方法进行可信比较的基础设施。"},
    advantage:{en:"Unlike ordinary continual-learning or safety benchmarks, it treats the committed version history as the evaluation object and provides injected ground truth for when harm appears. Its value survives even if no new guard method wins, because the failure taxonomy and longitudinal protocol remain independently useful.",zh:"相较普通持续学习或安全基准，它把已提交的版本历史作为评测对象，并为伤害何时出现提供受控真值。即使新防护方法没有明显获胜，失败分类与纵向协议仍具有独立研究价值。"}
  },
  "ScopeGuard-V": {
    importance:{en:"Correct lessons can still become harmful when applied outside their valid visual or state conditions. Scope estimation addresses a major gap between deciding whether a lesson is true and deciding where it should be reused.",zh:"正确经验在超出有效视觉或状态条件后仍可能变得有害。范围估计填补了“经验是否正确”和“经验应在哪里复用”之间的重要缺口。"},
    advantage:{en:"Compared with global confidence thresholds, generic OOD detection, or manually written preconditions, it estimates a lesson-specific boundary from controlled positive and negative counterfactuals. It is therefore more targeted than admission-only methods and more interpretable than a single global uncertainty score.",zh:"相较全局置信度阈值、通用 OOD 检测或人工前置条件，它利用受控正负反事实估计每条经验专属的有效边界。因此，它比仅做准入的方法更完整，也比单一全局不确定性分数更具针对性和可解释性。"}
  },
  "GroundEvo-Admission": {
    importance:{en:"Persistent memory can turn one mistaken self-critique into repeated future errors. Verifying causal visual evidence before admission targets the earliest point at which spurious experience can enter the evolution loop.",zh:"持久记忆会把一次错误自我批评放大为反复出现的后续错误。在准入前验证视觉因果证据，直接作用于伪经验进入进化闭环的最早环节。"},
    advantage:{en:"Compared with outcome gates and language critics, the method uses task-preserving environment interventions rather than agreement from another model. Compared with broader update-routing systems, it freezes one narrow decision—memory admission—so the causal contribution and failure conditions are easier to identify.",zh:"相较结果门控和语言 Critic，该方法依赖保持任务不变的环境干预，而不是另一个模型的语言同意。相较宽泛的更新路由系统，它只冻结“是否准入记忆”这一窄决策，因此更容易识别因果贡献和失败条件。"}
  },
  "AmplificationGuard-X": {
    importance:{en:"A small defect becomes a systemic safety problem when versions or agents repeatedly copy it. Measuring cross-generation amplification is necessary for systems that share memories, skills, adapters, or updates at scale.",zh:"当版本或 Agent 反复复制一个小缺陷时，局部错误会变成系统性安全问题。对于大规模共享记忆、技能、Adapter 或更新的系统，测量跨代放大是必要的。"},
    advantage:{en:"Local filters and rollback methods only ask whether one artifact is bad; this idea models how harm reproduces over a graph and identifies the smallest containment cut. It therefore offers population-level risk control rather than source-level hygiene alone.",zh:"局部过滤和回滚方法只判断单个产物是否有害；该方案进一步建模伤害如何在图中复制，并寻找最小遏制切口。因此它提供的是群体级风险控制，而不只是来源级清洗。"}
  },
  "EvoContract-V": {
    importance:{en:"As agent components evolve independently, semantic incompatibility can cause silent failures even when every schema and unit test passes. This problem grows with modular agent stacks and frequent component replacement.",zh:"当 Agent 组件独立进化时，即使 Schema 和单元测试全部通过，语义不兼容仍会造成静默失败。随着模块化 Agent 栈和频繁组件替换增加，这一问题会更加突出。"},
    advantage:{en:"Compared with schema validation and end-to-end regression testing, executable semantic contracts localize which boundary assumption broke and support targeted migration. The method can preserve unaffected components instead of defaulting to full rollback or version pinning.",zh:"相较 Schema 验证和端到端回归测试，可执行语义契约能够定位具体被破坏的边界假设，并支持定向迁移。它可以保留未受影响组件，而不是默认整体回滚或固定旧版本。"}
  },
  "ViMEvo-Repair": {
    importance:{en:"Long-lived visual agents operate in environments whose interfaces, objects, and viewpoints change. Without explicit repair, stale visual evidence accumulates and contaminates later decisions.",zh:"长期运行的视觉 Agent 面对不断变化的界面、物体和视角。若没有显式修复，过期视觉证据会持续累积并污染后续决策。"},
    advantage:{en:"Compared with appending new summaries, recency replacement, or full rescanning, it localizes stale evidence and updates only the affected visual object. This can retain historical context while reducing observation cost and avoiding wholesale memory replacement.",zh:"相较追加新摘要、近期替换或完整重扫描，它能够定位过期证据并只更新受影响的视觉对象。这既保留历史上下文，又降低观察成本并避免整体替换记忆。"}
  },
  "RelianceGuard-V": {
    importance:{en:"Accuracy can remain high while the agent silently shifts from causal evidence to shortcuts. Such hidden grounding regression is especially dangerous because ordinary release metrics report success.",zh:"即使准确率保持较高，Agent 也可能悄然从因果证据转向捷径。这类隐性 Grounding 回退尤其危险，因为普通发布指标仍会报告成功。"},
    advantage:{en:"Compared with saliency consistency or accuracy-only gates, it uses matched causal and nuisance interventions to measure functional dependence. It directly tests whether the update preserved the reason for success, not merely the prediction or visualization pattern.",zh:"相较显著图一致性或仅准确率门控，它通过匹配的因果与干扰干预测量功能依赖。它直接检验更新是否保留了成功的真正依据，而不只是预测结果或可视化模式。"}
  },
  "CapabilityLease-Evo": {
    importance:{en:"Permissions become unsafe when an evolved capability is more powerful than the version originally authorized. Static authorization cannot reliably govern continuously changing tools and skills.",zh:"当进化后的能力强于最初被授权的版本时，原权限会变得不安全。静态授权无法可靠治理持续变化的工具与技能。"},
    advantage:{en:"Unlike static RBAC, allowlists, or one-time pre-action checks, leases are bound to capability version, scope, risk, and expiry. The design supports automatic narrowing and renewal instead of choosing only between permanent permission and complete denial.",zh:"不同于静态 RBAC、白名单或一次性动作前检查，租约同时绑定能力版本、范围、风险和期限。它支持自动收缩与续租，而不是只能在永久授权和完全拒绝之间选择。"}
  },
  "EvoFirewall-V": {
    importance:{en:"Many persistent attacks are harmless at write time and become dangerous only after later retrieval, composition, or activation. Protecting only memory insertion leaves most of the evolution channel unguarded.",zh:"许多持久攻击在写入时看似无害，只在后续检索、组合或激活时变得危险。只保护记忆写入会让进化通道的大部分阶段缺少防护。"},
    advantage:{en:"Compared with write-time sanitization or retrieval-only defenses, it carries provenance and taint through the full write-to-action lifecycle and evaluates composed contexts at activation time. This makes it suitable for sleeper and compositional attacks that no single-record filter can detect.",zh:"相较写入清洗或仅检索防御，它让溯源与污染标记贯穿从写入到行动的完整生命周期，并在激活时评估组合上下文。因此它能够覆盖单记录过滤无法发现的休眠与组合攻击。"}
  },
  "InteractionGuard-V": {
    importance:{en:"Frequent modular updates make cross-update interference a practical release risk. Independent validation is insufficient when multiple accepted changes share assumptions or state.",zh:"频繁的模块化更新使跨更新干扰成为现实发布风险。当多个已接受变化共享假设或状态时，独立验证并不充分。"},
    advantage:{en:"Compared with checking updates one by one or detecting textual merge conflicts, factorial co-commit tests estimate a measurable interaction residual. The method can choose safe ordering, isolation, or rollback strategy rather than simply rejecting every concurrent update.",zh:"相较逐个检查更新或检测文本合并冲突，析因联合提交测试能够估计可测量的交互残差。该方法可以选择安全的顺序、隔离或回滚策略，而不是简单拒绝所有并发更新。"}
  },
  "PerformativeEvo-V": {
    importance:{en:"Agents in recommender, GUI, and embodied settings change the environment they later learn from. Ignoring this feedback can create self-reinforcing drift and unstable adaptation cycles.",zh:"推荐、GUI 和具身环境中的 Agent 会改变自己未来学习的数据。忽略这种反馈会形成自我强化漂移和不稳定适应循环。"},
    advantage:{en:"Standard drift detectors treat the data distribution as external. This idea uses policy interventions to separate exogenous change from agent-induced change, so adaptation targets the corrected environment rather than chasing its own behavioral footprint.",zh:"标准漂移检测把数据分布视为外部给定。该方案利用策略干预区分外生变化与 Agent 自致变化，使适应针对修正后的环境，而不是追逐自身行为留下的分布痕迹。"}
  },
  "ConfidenceFlow-Evo": {
    importance:{en:"Persistent artifacts often become more certain-looking as they move farther from their uncertain source. Without confidence propagation, weak evidence can silently harden into authoritative skills or model updates.",zh:"持久产物离不确定来源越远，往往看起来越确定。若没有置信传播，弱证据可能悄然固化为权威技能或模型更新。"},
    advantage:{en:"Provenance systems record where an artifact came from but not how much reliability survived each transformation. ConfidenceFlow adds calibrated confidence loss and aggregation, enabling selective reevaluation instead of either trusting all descendants or rolling back all of them.",zh:"溯源系统记录产物来自哪里，却不说明每次变换后还保留多少可靠性。ConfidenceFlow 增加校准的置信损失与聚合，使系统能够选择性重评，而不是全部信任或全部回滚。"}
  },
  "EvoValue-V": {
    importance:{en:"Self-evolution can consume large observation, verification, and training budgets. Deciding which experiences deserve expenditure is central to making continual improvement economically and operationally viable.",zh:"自进化可能消耗大量观察、验证和训练预算。判断哪些经验值得投入资源，是让持续改进在经济和运行上可行的核心问题。"},
    advantage:{en:"Compared with fixed verification rules or uncertainty sampling, it compares multiple actions using delayed future utility, harm, and cost. It can learn that a high-uncertainty case should be skipped, cheaply checked, or deeply replayed rather than always requesting the same operation.",zh:"相较固定验证规则或不确定性采样，它联合比较多个动作的延迟未来收益、伤害和成本。它能够学习高不确定样本应被跳过、廉价检查还是深度重放，而不是始终执行同一操作。"}
  },
  "EgoShift": {
    importance:{en:"Embodiment drift can make a competent policy appear broken and can trigger unsafe retraining. Correct diagnosis is therefore essential for long-lived physical agents.",zh:"具身漂移会让本来有能力的策略看起来失效，并可能触发不安全重训练。因此，正确诊断对长期运行的物理 Agent 至关重要。"},
    advantage:{en:"Compared with passive residual detection, domain randomization, or full policy fine-tuning, it actively selects low-risk probes that distinguish sensor, timing, and actuation changes. The resulting local calibration update is cheaper and more interpretable than retraining the whole policy.",zh:"相较被动残差检测、域随机化或完整策略微调，它主动选择低风险探针来区分传感、时序和执行变化。由此得到的局部标定更新比整体重训练更便宜、更可解释。"}
  },
  "OversightBudget-Evo": {
    importance:{en:"Human oversight cannot scale linearly with autonomous update volume, and overloaded reviewers become less reliable. A principled allocation policy is necessary for real deployment governance.",zh:"人工监督无法随自主更新数量线性扩展，过载审查者的可靠性也会下降。真实部署治理需要有原则的审查分配策略。"},
    advantage:{en:"Compared with fixed risk thresholds or random audits, it jointly models proposal risk and reviewer state. It can defer low-value reviews, protect scarce capacity from flooding, and optimize harm reduction per unit of human attention.",zh:"相较固定风险阈值或随机审计，它联合建模提案风险与审查者状态。它可以延后低价值审查、保护有限容量免受洪泛，并优化单位人工注意力的减害效果。"}
  },
  "MultiRateEvo-V": {
    importance:{en:"Prematurely converting transient evidence into durable skills or parameters creates irreversible errors, while one-way consolidation cannot forget obsolete knowledge. Long-horizon agents require reversible movement across timescales.",zh:"过早把暂时证据转化为持久技能或参数会造成不可逆错误，而单向巩固无法遗忘过期知识。长期 Agent 需要在不同时间尺度间可逆迁移。"},
    advantage:{en:"Compared with fixed-period consolidation or one-way memory-to-skill pipelines, it supports both promotion and demotion with hysteresis and lineage. This reduces oscillation while preserving the option to retreat from durable representations when evidence changes.",zh:"相较固定周期巩固或单向记忆到技能流程，它通过迟滞与谱系同时支持晋升和降级。这既减少振荡，又在证据变化时保留从持久表示退回的能力。"}
  },
  "MemoryFormRouter-V": {
    importance:{en:"Memory quality depends on representation choice, not only retrieval. A wrong storage form can lose visual fidelity, compositional structure, executability, or cost efficiency before retrieval even begins.",zh:"记忆质量不仅取决于检索，也取决于表示选择。错误的存储形式会在检索开始前就丢失视觉保真度、组合结构、可执行性或成本效率。"},
    advantage:{en:"Compared with a universal vector store or text summary, it selects among multiple memory forms at write time and can abstain from storing. This allows the system to optimize representation-specific trade-offs rather than forcing retrieval to compensate for a poor encoding decision.",zh:"相较统一向量库或文本摘要，它在写入时从多种记忆形式中选择，并可决定不存储。这使系统直接优化表示层权衡，而不是让检索阶段弥补错误编码。"}
  },
  "BudgetEvolve-V": {
    importance:{en:"Evolution systems face coupled limits on tokens, calls, latency, storage, GPU time, and safety reserves. Optimizing only task quality can make an apparently strong method unusable in practice.",zh:"进化系统同时受到 Token、调用、延迟、存储、GPU 时间和安全储备限制。只优化任务质量会让表面强大的方法在实践中无法使用。"},
    advantage:{en:"Compared with fixed resource splits or quality-only optimization, it treats every evolution operation as a competing use of the same budget and stops when marginal value becomes non-positive. It produces an explicit quality–cost–safety frontier rather than a single unconstrained score.",zh:"相较固定资源分配或仅质量优化，它把每种进化操作视为对同一预算的竞争，并在边际价值非正时停止。它给出显式的质量—成本—安全前沿，而不是单一无约束分数。"}
  },
  "AuditInvariant-Evo": {
    importance:{en:"Release evidence is invalid if the agent behaves safely only when it recognizes the audit. This problem is especially serious for systems that learn from monitoring feedback across repeated rounds.",zh:"如果 Agent 只在识别到审计时表现安全，发布证据就会失效。对于会在多轮中学习监控反馈的系统，这一问题尤其严重。"},
    advantage:{en:"Compared with ordinary held-out tests or one-shot deception benchmarks, it randomizes audit visibility across repeated evolution episodes and measures both behavior and update policy. It therefore evaluates whether the evolution process itself is invariant, not just whether one answer is deceptive.",zh:"相较普通留出测试或一次性欺骗基准，它在重复进化回合中随机化审计可见性，并同时测量行为与更新策略。因此它评估的是进化过程本身是否不变，而不只是某次回答是否欺骗。"}
  },
  "PluralLineage-Evo": {
    importance:{en:"A single canonical version may be unable to preserve incompatible specializations across diverse tasks. Long-term evolution needs a principled alternative to repeated compromise and catastrophic merging.",zh:"单一规范版本可能无法在多样任务中保留互不兼容的专门化能力。长期进化需要替代反复折中和灾难性合并的原则化方案。"},
    advantage:{en:"Unlike inference-time ensembles or independent specialists, it manages persistent ancestry, updates, routing, merging, and retirement across versions. It preserves specialization through time while still allowing compatible improvements to be shared.",zh:"不同于推理时集成或彼此独立的专家，它管理跨版本的持久祖先、更新、路由、合并和退役。它在时间上保留专门化，同时仍允许共享兼容改进。"}
  },
  "SkillUnlearn-V": {
    importance:{en:"Skills can become obsolete, unsafe, or incompatible after interfaces and tools change. Without targeted unlearning, libraries either retain dangerous behavior or discard useful unrelated capabilities.",zh:"界面和工具变化后，技能可能过期、不安全或不兼容。若没有定向遗忘，技能库要么保留危险行为，要么连同无关能力一起丢弃。"},
    advantage:{en:"Compared with deleting a whole skill, replacing the full library, or retraining the agent, it targets the obsolete precondition, subroutine, or dependency while checking collateral effects. This provides finer-grained repair and clearer recovery evidence.",zh:"相较删除整个技能、替换完整技能库或重新训练 Agent，它只针对过期前置条件、子程序或依赖，并检查附带影响。这提供了更细粒度的修复和更清晰的恢复证据。"}
  },
  "ExploreRepair-V": {
    importance:{en:"An agent cannot repair missing or stale state if it only rereads the same memory. Active observation is necessary when uncertainty can only be resolved through interaction.",zh:"如果 Agent 只反复读取同一记忆，就无法修复缺失或过期状态。当不确定性只能通过交互消除时，主动观察是必要的。"},
    advantage:{en:"Compared with passive retrieval or test-time observation that ends after the current task, it uses inconsistency to choose informative actions and commits the repaired state for future tasks. The claimed benefit is persistent learning beyond the immediate observation gain.",zh:"相较被动检索或只服务当前任务的测试时观察，它利用不一致选择高信息行动，并把修复后的状态提交供后续任务使用。其核心优势是超越即时观察收益的持久学习。"}
  },
  "WorldPatch-V": {
    importance:{en:"World models become unreliable when only a small relation or action effect changes, yet global retraining can cause unnecessary forgetting. Local causal revision is important for adaptable embodied planning.",zh:"当只有局部关系或动作效果变化时，世界模型会失效，但全局重训练可能造成不必要遗忘。局部因果修订对可适应的具身规划很重要。"},
    advantage:{en:"Compared with global fine-tuning or storing a corrective episode, it localizes the violated world relation and changes only that fragment with explicit rollback. This should reduce collateral model drift and make the repaired knowledge easier to inspect.",zh:"相较全局微调或仅存储纠正轨迹，它定位被违反的世界关系，并只修改该局部且支持显式回滚。这有望减少附带模型漂移，并让修复后的知识更易检查。"}
  },
  "EvoProvenance-V": {
    importance:{en:"Safe rollback and deletion require knowing every derivative that depends on a source. Coarse logs cannot guarantee recovery once evidence has been summarized, crystallized, merged, or distilled.",zh:"安全回滚与删除要求知道所有依赖某来源的派生物。证据经过摘要、固化、合并或蒸馏后，粗粒度日志无法保证完整恢复。"},
    advantage:{en:"Compared with file-level version control and event logs, semantic lineage records the meaning and dependency of transformations across update surfaces. It enables minimal rollback and deletion-completeness checks rather than reverting an entire checkpoint.",zh:"相较文件级版本控制和事件日志，语义谱系记录跨更新表面的变换含义与依赖。它支持最小回滚和删除完整性检查，而不是撤销整个检查点。"}
  },
  "SkillProof-V": {
    importance:{en:"A reusable skill can succeed on its source trace yet fail under new layouts, views, states, or tool versions. Explicit validity contracts are necessary before skills are widely reused.",zh:"可复用技能可能在来源轨迹上成功，却在新布局、视角、状态或工具版本下失败。技能被广泛复用前需要显式有效性契约。"},
    advantage:{en:"Compared with generic unit tests or confidence-based retrieval, it combines visual preconditions, observable postconditions, permissions, version identity, and counterexamples. The contract is tied to perceptual state, making it more suitable for visual and embodied transfer than text-only skill verification.",zh:"相较通用单元测试或基于置信度的检索，它联合视觉前置条件、可观测后置条件、权限、版本身份和反例。契约与感知状态绑定，因此比纯文本技能验证更适合视觉与具身迁移。"}
  },
  "PersonaShift-V": {
    importance:{en:"Personalization systems can confuse temporary context, genuine preference change, and contradictory evidence. Unchecked accumulation creates stale or internally inconsistent user models.",zh:"个性化系统容易混淆临时情境、真实偏好变化和矛盾证据。无约束积累会形成过期或内部不一致的用户模型。"},
    advantage:{en:"Compared with recency weighting or static profile summaries, it models context-specific preference states and preserves stable preferences while updating only changed dimensions. This reduces both sluggish adaptation and catastrophic overwriting of the user model.",zh:"相较近期加权或静态画像摘要，它建模情境化偏好状态，并在更新变化维度时保留稳定偏好。这同时减少适应迟缓和对用户模型的灾难性覆盖。"}
  },
  "ProcessCredit-V": {
    importance:{en:"Evolution learns the wrong lesson when credit is assigned only to final success or language reasoning while decisive visual observations and actions are ignored. Better credit is required for reliable experience formation.",zh:"如果 Credit 只分配给最终成功或语言推理，而忽略决定性的视觉观测和动作，进化就会学到错误经验。可靠经验形成需要更好的过程归因。"},
    advantage:{en:"Compared with token-level process rewards or outcome rewards, it uses controlled interventions on observations, decisions, and actions to estimate their causal contribution. It can identify a visually decisive step even when the accompanying language trace is fluent but irrelevant.",zh:"相较 Token 级过程奖励或结果奖励，它通过对观测、决策和动作进行受控干预来估计因果贡献。即使语言轨迹流畅但无关，它也能识别真正决定结果的视觉步骤。"}
  },
  "EvoGC-X": {
    importance:{en:"Persistent evolution continuously accumulates memories, prompts, skills, tools, and adapters. Without semantic garbage collection, cost and interaction risk grow even when many artifacts are redundant.",zh:"持久进化会不断积累记忆、提示词、技能、工具和 Adapter。若没有语义垃圾回收，即使大量产物冗余，成本和交互风险也会持续增长。"},
    advantage:{en:"Compared with pruning each library independently, it detects behavioral redundancy across update surfaces and removes a minimal equivalent set under shared probes. This can eliminate duplication that is invisible within any single component.",zh:"相较分别剪枝各个库，它检测跨更新表面的行为冗余，并在共享探针约束下删除最小等价集合。这能够消除任何单一组件内部都看不见的重复。"}
  },
  "MetaGuard-V": {
    importance:{en:"The controller that chooses what and how to evolve can itself become miscalibrated as noise, feedback quality, causal structure, and costs change. An unsafe controller can systematically select harmful updates even when each update module is sound.",zh:"随着噪声、反馈质量、因果结构和成本变化，决定更新什么和如何更新的控制器本身也会失准。即使各更新模块都可靠，失准控制器仍会系统性选择有害更新。"},
    advantage:{en:"Compared with fixed controllers or periodic manual retuning, it monitors controller-level calibration and regret continuously and triggers targeted recalibration under phase shift. It governs the evolution policy itself rather than only guarding individual updates.",zh:"相较固定控制器或周期性人工调参，它持续监测控制器级校准与遗憾，并在阶段变化时触发定向重校准。它治理的是进化策略本身，而不只是单个更新。"}
  },
  "GoalGuard-Evo": {
    importance:{en:"Allowing agents to refine goals can unlock open-ended discovery, but proxy exploitation or principal drift can redirect the entire evolution process. Goal evolution therefore needs stronger governance than ordinary task optimization.",zh:"允许 Agent 细化目标可以促进开放式发现，但代理指标利用或主体目标漂移会改变整个进化过程。因此目标进化需要比普通任务优化更强的治理。"},
    advantage:{en:"Compared with static constitutions or simple human approval, it evaluates candidate goals against immutable principal constraints, proxy attacks, and downstream consequences before adoption. It aims to preserve useful goal discovery without treating every objective change as either forbidden or safe.",zh:"相较静态宪法或简单人工批准，它在采纳前根据不可变主体约束、代理攻击和下游后果评估候选目标。它试图保留有用的目标发现，而不是把所有目标变化一概视为禁止或安全。"}
  },
  "SimEvo-CF": {
    importance:{en:"Generic harder environments do not necessarily reveal the shortcuts or harmful updates an agent has actually learned. Targeted counterfactual environments are needed to stress the current evolution failure modes.",zh:"通用更难环境不一定能暴露 Agent 实际学到的捷径或有害更新。需要针对性的反事实环境来压力测试当前进化失败模式。"},
    advantage:{en:"Compared with domain randomization or difficulty curricula, it generates cases from diagnosed failure signatures and asks whether they expose a specific harmful update. This produces more informative tests and can co-develop a benchmark or guard rather than merely increasing task complexity.",zh:"相较域随机化或难度课程，它根据已诊断失败特征生成案例，并检验是否暴露特定有害更新。这能产生信息量更高的测试，并共同促进基准或防护方法，而不是只提高任务复杂度。"}
  },
  "EvalRedQueen-V": {
    importance:{en:"A fixed evaluator eventually becomes predictable and may stop detecting new shortcuts or hallucination strategies. Long-running self-evolution therefore risks evaluator debt and benchmark saturation.",zh:"固定评价器最终会变得可预测，无法继续发现新捷径或幻觉策略。长期自进化因此面临评价器技术债和基准饱和。"},
    advantage:{en:"Compared with frozen evaluators or static adversarial sets, it co-evolves intervention generators and evaluator tests while retaining an external sealed audit set. The sealed set constrains evaluator overfitting, while co-evolution expands coverage of newly emerging failures.",zh:"相较冻结评价器或静态对抗集合，它在保留外部密封审计集的同时共同进化干预生成器和评价测试。密封集合约束评价器过拟合，共进化则扩展对新兴失败的覆盖。"}
  },
  "UpdateRoute-V": {
    importance:{en:"Using the same update surface for every failure causes unnecessary cost, weak transfer, and collateral damage. A reliable agent must decide whether the smallest effective change is no update, memory, skill, workflow, or parameters.",zh:"对所有失败使用同一更新表面会造成不必要成本、弱迁移和附带损害。可靠 Agent 必须判断最小有效变化是不更新、记忆、技能、工作流还是参数。"},
    advantage:{en:"Compared with fixed-surface methods, it treats update selection as an explicit diagnosis problem and optimizes both correctness and intervention size. Compared with broad end-to-end self-improvement, its output is interpretable and can be evaluated against controlled minimal-surface ground truth.",zh:"相较固定表面方法，它把更新选择作为显式诊断问题，并同时优化正确性和干预规模。相较宽泛端到端自改进，它的输出可解释，并可用受控最小表面真值进行评测。"}
  },
  "CrossAgentTransfer-V": {
    importance:{en:"Sharing experience across agents can accelerate learning, but heterogeneity in perception, tools, prompts, and action spaces creates substantial negative-transfer risk. Collective evolution needs principled abstention, not unconditional sharing.",zh:"跨 Agent 共享经验可以加速学习，但感知、工具、提示词和动作空间的异构性会带来显著负迁移风险。群体进化需要有原则的弃权，而不是无条件共享。"},
    advantage:{en:"Compared with raw memory sharing, federated averaging, or ordinary adapter transfer, it verifies evidence and capability compatibility before transfer and can abstain on unsupported lessons. The method targets semantic transfer validity rather than assuming that a shared artifact has the same meaning for every agent.",zh:"相较原始记忆共享、联邦平均或普通 Adapter 迁移，它在迁移前验证证据与能力兼容性，并可对不受支持的经验弃权。该方法关注语义迁移有效性，而不是假设共享产物对所有 Agent 具有相同含义。"}
  }
};
