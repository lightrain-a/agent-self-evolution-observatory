"""Canonical RSI learning-function taxonomy; stable I identifiers are not ranks.

Primary placement follows the contribution; related functions are cross references.
Background, evidence and resources support chapters 2/7, never a fifth function.
"""

FUNCTIONS = [
    {"id":"experience", "chapter":3, "section":"3", "title":"经验获取", "en":"Acquiring Learning Experiences", "question":"下一步经历什么，才可能学到有用的东西？", "summary":"识别能力缺口，构造有信息量的任务与交互，从教师、伙伴和工具获得新信息，选择与当前学习者相适配的经历。", "subsections":[
        {"id":"3.1","title":"能力缺口与学习需求","question":"欠缺什么，哪些缺口当前可能被修复？"},
        {"id":"3.2","title":"任务与交互的信息价值","question":"哪些经历提供原先缺少的信息，区分竞争解释？"},
        {"id":"3.3","title":"教师、伙伴与工具","question":"外部信息是否超出学习者已有的知识与盲点？"},
        {"id":"3.4","title":"经验选择与可学习性","question":"难度、新颖性和覆盖度何时对应实际学习价值？"}]},
    {"id":"signal", "chapter":4, "section":"4", "title":"学习信号", "en":"Learning Signals and Credit Assignment", "question":"这次经历说明了什么，应该改进哪里？", "summary":"判断反馈是否可信，从结果诊断失败原因，归因步骤与记忆的作用，区分任务评价与实际学习收益。", "subsections":[
        {"id":"4.1","title":"信号来源与可靠性","question":"环境、自己与同伴提供的评价何时可信？"},
        {"id":"4.2","title":"从结果到失败诊断","question":"相同错误终点是否来自不同的可修复原因？"},
        {"id":"4.3","title":"步骤、经验与记忆归因","question":"哪些步骤或记忆真正促成了当前决策？"},
        {"id":"4.4","title":"从任务评价到学习收益","question":"正确反馈是否能被吸收，并改善未来表现？"}]},
    {"id":"capability", "chapter":5, "section":"5", "title":"能力形成", "en":"Forming Knowledge and Updating Capabilities", "question":"如何把经历变成以后能够使用的能力？", "summary":"从实例形成规则与技能，在外部状态中保存和调用知识，将经验巩固到参数，协调外部支持与内部学习。", "subsections":[
        {"id":"5.1","title":"从经历形成知识","question":"保留什么、抽象什么，形成的规则适用于何处？"},
        {"id":"5.2","title":"外部状态中的能力","question":"记忆、技能与工具怎样改变后续行为？"},
        {"id":"5.3","title":"经验的参数巩固","question":"什么信号与更新机制形成可迁移的能力？"},
        {"id":"5.4","title":"外部支持与内部学习","question":"何时查询、保留实例或内化规则，怎样支持吸收？"}]},
    {"id":"regulation", "chapter":6, "section":"6", "title":"学习调控", "en":"Regulating Sustained Self-Improvement", "question":"如何使多次改进相互支持，并持续积累？", "summary":"协调新旧知识、学习顺序与后续可学习性，动态分配学习动作和资源，改进教师、协同机制与更新规则。", "subsections":[
        {"id":"6.1","title":"兼容、冲突与修订","question":"怎样保留旧能力，修复新旧规则的适用边界？"},
        {"id":"6.2","title":"学习顺序与未来可学习性","question":"当前表现接近时，学习历史是否改变继续学习的能力？"},
        {"id":"6.3","title":"学习动作与资源分配","question":"何时探索、总结、更新、复习、停止或接纳候选更新？"},
        {"id":"6.4","title":"学习机制自身的改进","question":"教师策略、伙伴协同与更新规则能否从实际学习效果中改善？"}]},
]

IDEAS = {
 "I1":{"title":"脚手架学习与内外取舍","href":"ideas.html#idea-1","primary":"capability","section":"5.4","related":["regulation"],"tags":["外部记忆","参数巩固","独立能力","长期成本"],"reason":"经验保存在内部能力还是外部支持，以及它如何在未来发挥作用。"},
 "I2":{"title":"因材施教与师生共进化","href":"idea-i2.html","primary":"regulation","section":"6.4","related":["experience","signal","capability"],"tags":["教师策略","师生共进化","实际学习收益"],"reason":"教师根据学生实际学习回应逐轮改进教法，而非教师信息来源本身。"},
 "I3":{"title":"新旧规则的适用边界修复","href":"ideas.html#idea-3","primary":"regulation","section":"6.1","related":["signal","capability"],"tags":["知识冲突","回放","保持","规则边界"],"reason":"研究多次更新间的干扰，修复有效的新旧规则的适用条件。"},
 "I4":{"title":"辨别性探索与总结时机","href":"ideas.html#idea-4","primary":"regulation","section":"6.3","related":["experience","signal","capability"],"tags":["假设检验","主动试验","停止策略","Skill"],"reason":"主问题是何时继续辨别性试验、何时证据足够可以总结；经验构造关联第3.2节。"},
 "I5":{"title":"十模型互教与动态换伴","href":"idea-i5.html","primary":"regulation","section":"6.4","related":["experience","signal"],"tags":["多智能体","动态伙伴","独立净学习收益","资源分配"],"reason":"主要变量是跨轮伙伴关系、交流时长和重配策略。"},
 "I6":{"title":"失败过程的学习价值","href":"idea-i6-failure-value.html","primary":"signal","section":"4.4","related":["experience","regulation"],"tags":["失败诊断","轨迹归因","收益预测","停止与重访"],"reason":"识别相同错误结果下失败过程的增量信息，估计固定纠错后的独立收益。"},
 "I7":{"title":"先独立尝试还是先看示范","href":"idea-i7-learning-order.html","primary":"regulation","section":"6.2","related":["experience","capability"],"tags":["教学顺序","生产性失败","独立能力","迁移"],"reason":"固定材料和预算，仅改变尝试与示范的顺序，检验持续学习。"},
 "I8":{"title":"错误规则的可学习性与迁移","href":"i8.html","primary":"signal","section":"4.4","related":["experience","capability"],"tags":["知识准备","错误规则","收益预测","规则迁移"],"reason":"通过知识准备、规则范围与更新兼容性诊断跨题纠错收益。"},
 "I9":{"title":"课程顺序与未来可学习性","href":"idea-i9-practice-switching.html","primary":"regulation","section":"6.2","related":["capability"],"tags":["集中与交错","训练历史","未来可学习性","干扰"],"reason":"学习顺序和切换时机如何影响保持，以及随后学习新规则的曲线。"},
 "I10":{"title":"区分性反例与规则组合学习","href":"idea-i10-learning-novelty.html","primary":"experience","section":"3.2","related":["capability","signal"],"tags":["反例","规则区分","参数吸收","组合泛化"],"reason":"主要变量是追加经历能否区分真实规则与竞争捷径。"},
 "I11":{"title":"反馈语气与持续学习收益","href":"idea-i11-emotional-rsi.html","primary":"signal","section":"4.1","related":["regulation"],"tags":["反馈语气","自评校准","学习动作","跨轮净收益"],"reason":"固定反馈事实，仅改变信号表达，检验其对学习决策与持久收益的作用。"},
 "I12":{"title":"共同前置瓶颈与学习解锁","href":"idea-i12-prerequisite-bottleneck.html","primary":"regulation","section":"6.2","related":["experience","capability","signal"],"tags":["因果前置","知识准备","未来可学习性","多任务"],"reason":"决定性主张是补P后再学T的第二阶段学习增量；缺口与吸收关联第3.1与5.4节。"},
 "I13":{"title":"安全更新接纳与有限预算验证","href":"learning-admission.html","primary":"regulation","section":"6.3","related":["signal"],"tags":["更新接纳","选择性测试","安全","验证成本"],"reason":"在独立约束下动态选择验证和接纳动作，检验跨代风险。"},
 "I14":{"title":"学习规则自进化","href":"learning-rule-evolution.html","primary":"regulation","section":"6.4","related":["signal","capability"],"tags":["元学习","更新规则","实际学习收益","未来可学习性"],"reason":"固定学生、材料与顺序，研究更新机制能否从实际学习效果中改进。"},
}

_SOURCE_ROWS = """
S01|background||综述用于界定自我改进范围与修改对象。
S02|capability|regulation,signal|将执行经验写入可继承代码，版本搜索提供持续更新。
S03|capability|signal,regulation|从轨迹反思产生提示修改，并组合互补经验。
S04|capability|signal,regulation|生成自编辑数据与指令，将经验写入模型参数。
S05|regulation|capability|任务Agent和改进它的Meta-Agent共同成为可修改对象。
S06|regulation|capability|通过快慢时间尺度协调任务技能与元技能演化。
S07|capability|signal|从失败轨迹学习生成可执行Harness修改。
S08|regulation|capability|跨任务学习可迁移的Harness适应策略。
S09|capability|signal|把成败轨迹对照转化为模块化Harness能力。
S10|regulation|signal|正则化跨轮修改提议与选择，约束搜索过拟合。
S11|regulation|experience|用历史发现树回放改善后续探索策略。
S12|regulation|capability|协调任务内Harness修改与跨任务改进经验。
S13|experience|signal,regulation|借助世界模型预测行动后果并构造后续探索机会。
S14|evidence|regulation|以等反馈和等推理预算检验Harness演化主张。
S15|signal|capability|检验失败反馈能否指引有迁移价值的自修改。
S16|regulation|experience,signal|用学习进展动态分配失败模式的训练优先级。
S17|regulation|experience,signal|以学生实际更新收益训练课程生成教师。
S18|regulation|experience,signal|预测课程决策的后续可学习性与迁移后果。
S19|regulation|experience,signal|学习多轮教学中的帮助方式和帮助程度。
M01|regulation|capability|将优化器本身作为可学习的更新规则。
M02|regulation|capability|慢速跨任务训练塑造快速适应算法。
M03|regulation|experience,signal|按学习进展以非平稳bandit安排课程。
M04|regulation|experience,signal|联合调度学习进展和退化任务的重访。
M05|signal|experience|从交互历史估计学习者知识状态。
M06|regulation|signal,capability|教师依据学生阶段学习动态损失函数。
M07|regulation|experience,signal|统筹行动回报与获取未知动力学信息的价值。
M08|regulation|experience,signal|按优先级安排旧经验的重放。
M09|regulation|experience|选择受当前更新干扰的旧样本进行回放。
E01|regulation|signal|自我调节学习协调前瞻、监控与反思。
E02|regulation|experience,signal|依据可取得进展的材料分配学习时间。
E03|capability|regulation|比较检索练习与重复阅读的长期记忆形成。
E04|regulation|capability|检验练习间隔与保持时长的关系。
E05|capability|regulation,experience|逐步撤去例题步骤以支持自主能力形成。
E06|regulation|experience,capability|研究先探索失败、后整理巩固的教学次序。
E07|regulation|experience|研究何时提供何种程度的教学帮助。
E08|evidence|regulation,capability|区分当场成功失败与后续学习收益。
B01|resource||状态化工具执行基准与评估协议。
B02|resource||版本化工具任务基准及官方代码。
B03|resource||可执行终端任务基准。
B04|resource||候选学习者模型的官方模型资源。
B05|resource||同家族强模型对照资源。
B06|resource||跨模型家族实验资源。
S20|regulation|signal,capability|用学生反馈更新教师解释与偏好。
S21|capability|experience,signal|利用Socratic多智能体对话改善可复用提示。
S22|capability|signal|对比教师成功和学生失败，将经验蒸馏为技能。
S23|capability|experience|研究文本和代码技能的抽象层次与跨任务复用。
S24|experience|regulation|学习向教师主动提问以获得所需信息。
S25|experience|capability|通过解释和回教提供学生可用的上下文知识。
E09|regulation|signal,capability|教师从学生自主应用的递归反馈中改善理解。
E10|signal|regulation|用教学对话中的知识建构诊断教师学习。
B07|resource||可执行应用生态基准与数据划分。
S26|capability|experience,regulation|自博弈经验先提炼为技能，再巩固到参数并撤去支架。
S27|capability|regulation|训练支架随策略能力调整并在部署时撤除。
S28|regulation|signal,capability|诊断瓶颈并学习选择模型、Harness或产物更新流程。
S29|regulation|capability|协调新Harness收益与历史能力保持。
S30|regulation|signal,capability|在回归约束下平衡技能探索、利用与修改接纳。
S31|capability|signal|从多条执行轨迹抽象可复用技能。
S32|regulation|experience,capability|协调LoRA群体的匹配、自博弈与演化。
S33|capability|experience,signal|将受门控同伴反馈巩固进双方模型参数。
S34|experience|regulation|通过结构化同伴探索获得互补协作信息。
S35|signal|capability|研究生成与验证能力差距如何约束自提升。
S36|signal|experience,regulation|以中途干预诊断知识和执行瓶颈并选择查询。
S37|signal|capability,regulation|区分训练未吸收的不同原因并针对性干预。
S38|regulation|signal,capability|按样本状态协调GRPO与自蒸馏更新。
S39|regulation|signal,capability|根据正确率和置信度动态路由后训练配方。
E11|regulation|experience|考察中等难度材料与有限学习时间分配。
E12|signal|capability|比较置信度与正确反馈后的错误修复。
E13|signal|capability|课堂中检验高置信度错误接受反馈后的纠正。
E14|signal|capability|比较已有知识与主观置信度对纠错的解释力。
E15|signal|capability|分析诊断题置信度与后续表现的关系。
S40|experience|signal,capability|从错误类型构造并筛选可用于训练的新数据。
S41|evidence|capability|以规则编辑基准区分规则文本修复与实例迁移。
S42|capability|signal|通过分布式更新改善规则知识及其应用。
S43|signal|capability|以置信度重加权构造全错RL组的训练信号。
S44|signal|capability|对高置信度错误设计非对称纠正惩罚。
M10|signal|experience|用优化器感知梯度估计候选数据对目标的影响。
M11|signal|experience,capability|利用训练动态识别记忆与可泛化学习价值。
E16|regulation|experience,signal|以主观学习速率解释何时离开当前材料。
E17|regulation|signal|学习元认知干预和不干预动作。
E18|signal|capability|研究可信反馈引发的语义预测误差与知识更新。
E19|regulation|experience,signal|人类依据表现和学习进展选择探索活动。
S45|regulation|experience,signal|以自步调bandit分配难度和学习进展不同的样本。
S46|regulation|signal,experience|检测平台期后调整支架以恢复训练信号。
S47|regulation|experience,signal|用同起点学生的实际学习增益训练教师课程。
S48|regulation|signal|按额外采样的预期收益与成本停止推理。
S49|experience|regulation|依据当前能力构造渐进挑战。
M12|regulation|experience,signal|按学习进展和非平稳bandit调度课程预算。
M13|signal|experience|在训练前预测监督数据集的迁移收益。
S90|regulation|experience,capability|协调异构Agent之间的数据交换和互惠学习。
E90|regulation|capability|比较群体交流顺序对记忆传播与对齐的影响。
E91|experience|regulation|通过网络知识与能力分布提供互补解题信息。
E92|experience|regulation|操纵多样性和模块化以改变群体信息获取。
E93|regulation|experience,capability|研究跨代示范者选择与策略长期传播。
E94|regulation|experience,signal|社会学习策略随历史收益调整。
E95|experience|regulation|比较复制现有解和组合知识获得新解。
E96|regulation|experience,signal|根据可信收益信息调整对同伴的注意与信息流。
E97|background|experience,regulation|Jigsaw互教组织方式的系统综述。
S100|capability|experience|通过模仿规范Bayesian示范形成可迁移推理能力。
S101|regulation|signal,experience|学习生成适合学生吸收的教学解释。
S102|experience|signal|依据学生学习成本从正确教师答案中选择监督。
S103|regulation|signal,experience|训练教师适应学生状态并调整多轮教法。
S104|regulation|signal,capability|学习可被学生吸收的教师输出并协调学生更新。
M100|regulation|signal|通过学生反馈优化教师策略。
S200|regulation|experience,capability|协调双模型联合训练和周期性角色交换。
S201|regulation|experience|学习动态伙伴关系以改善合作。
S202|regulation|signal,capability|路由机制与持续学习Agent共同更新。
S203|regulation|capability|以交叉、变异、选择和继承协调模型群体演化。
S204|experience|signal|检验外部正确和错误轨迹能提供何种协作信息。
S205|experience|regulation|维持技能层面的新信息并缓解自博弈多样性幻觉。
B200|resource||十模型实验所需的官方模型规格与发布资源。
E20|regulation|capability|比较集中与交错练习对保持和新题的影响。
E21|regulation|capability|比较多规则学习中集中与交错的先后作用。
E22|regulation|signal|比较按混淆自适应排序与随机交错。
E23|regulation|experience|综合交错效应及材料相似度的调节作用。
E24|regulation|capability|比较人类和LLM在交错与间隔示例下的学习。
M15|regulation|experience|控制预训练排序、节奏和交错课程。
M16|regulation|experience|检验模型状态如何改变数学后训练最佳顺序。
E25|regulation|signal|依据学习者与项目历史、时间成本安排复习。
M17|capability|experience|解释模糊重复怎样形成参数中的文本记忆。
E26|experience|signal,capability|用目标几何与辨别性试探研究竞争规则的探索。
M18|regulation|signal|用更新场几何预测任务先后对学习结果的影响。
M19|regulation|capability|研究多任务持续学习的最佳顺序。
M20|signal|regulation,capability|诊断数据影响、遗忘和未来可塑性的学习动态。
M21|regulation|capability|学习能快速适应未来任务的初始化。
M22|regulation|capability|检验并缓解持续训练后获得新能力的可塑性损失。
M23|regulation|capability|共同协调旧知识、当前更新和未来学习容量。
M24|capability|experience|先记忆关系再赋予语义，检验记忆向可用知识的转换。
M25|capability|signal|解释原子事实掌握为何未必形成两跳组合能力。
M26|capability|signal|研究记忆与中间推理机制如何共存。
E27|signal|capability,regulation|区分忽略、复制与实际应用反馈的学习响应。
S105|experience|capability|通过主动提问获得概念信息。
S106|experience|signal|依据学生误解选择有针对性的示例。
S107|capability|signal|用错误推理和修正说明训练推理能力。
M27|signal|capability,regulation|诊断未被SFT吸收的样本并区分不同补救机制。
R01|signal|regulation|用人工锚与独立审计约束共演化评价器。
R02|signal|regulation|通过rubric dropout缓解学习奖励代理过拟合。
R03|experience|capability|生成可计算的结构化训练数据。
R04|experience|signal|依据层级错误记忆构造针对性练习。
R05|capability|signal|定位RLVR后可用解法覆盖缩减的形成位置。
R06|regulation|capability|研究策略分布改变与旧能力遗忘之间的关系。
R07|evidence|regulation|用多阶段任务评价Harness变化后的能力保持。
R08|evidence|capability,regulation|比较历史、摘要和参数训练对自提升的独立作用。
R09|regulation|capability,signal|研究恶意技能在后续自写更新中的持续传播。
R10|signal|regulation|研究群体评分漏洞、共同偏差与自主审计。
R11|evidence|regulation|检验持续数据研究后最终版本是否优于历史最好版本。
E98|experience|capability|研究先前能力与自主产生解法的信息价值。
S310|regulation|signal|以历史支系后代潜力而非当前得分选择演化分支。
E28|signal|regulation,capability|比较元认知、情感与中性反馈的学习作用。
M28|signal|regulation|检验情绪措辞对模型当前推理和生成的影响。
M29|signal||以配对情绪扰动检验输入表达的可靠性影响。
M30|signal|regulation|研究情绪框架及按题自适应表达。
M31|signal|regulation|用情绪线索和验证器支持同题自纠错。
M32|signal|regulation|比较鼓励、批评与模型自评校准。
M33|signal|regulation|检验情绪诱导对序贯探索和惩罚敏感性的影响。
M34|capability|signal,regulation|研究风格微调形成的行为及事实准确性副作用。
M35|regulation|signal,experience|元学习如何主动询问并利用语言反馈。
M36|signal|regulation|通过情绪提示和外部验证支持视觉语言自纠错。
E99|regulation|capability|研究任务结构相似性对学习干扰与表征分离的作用。
E100|regulation|capability|研究顺序学习中规则复用的迁移与干扰权衡。
E101|regulation|capability|研究练习引发的表征专门化与干扰降低。
E102|capability|regulation|研究多任务学习如何形成共享与专门化表示。
E103|capability|experience|用任务状态表征选择相关观察和隐变量。
E310|regulation|signal|通过元认知干预改善自主课程安排。
E29|signal|regulation|研究局部真实反馈如何扭曲整体能力自评。
E311|regulation|signal|根据后果学习更新对整种决策策略的使用。
E312|regulation|signal|学习依据历史结果选择推断策略。
E313|regulation|signal|依据收益和计算成本学习策略选择。
E314|background|signal,regulation|道德决策机制的理论背景，不能代替策略选择实验。
E315|background|signal,regulation|行动与后果价值双系统的理论背景。
M320|regulation|signal,capability|按置信冲突调控梯度以减少遗忘。
M321|regulation|signal,capability|按层级冲突选择持续学习中的更新范围。
M322|regulation|capability|依据探针协调专家扩展和持续能力增长。
M323|capability|regulation|将梯度存为可检索的临时可逆适配状态。
M324|regulation|experience,signal|在当前输入上选择自行预测或委托专家。
M325|regulation|experience,signal|专家变化时动态决定代价敏感委托。
M326|background|capability,regulation|模块化内外记忆的持续学习概念框架。
M327|regulation|capability|比较知识漂移下检索与学习的时间一致性。
S320|regulation|capability|递归修改元技能以改进任务技能优化过程。
E320|regulation|capability|研究经验结构复用如何影响新任务学习与反转适应。
M311|regulation|capability|用共享与专有分支协调迁移和旧能力保持。
M312|regulation|capability,signal|依据属性归因与软正交约束调节共享与隔离。
M313|regulation|capability|元学习兼顾新能力与旧任务保持的更新算法。
S311|regulation|capability|任务技能及可重写元技能跨轮共同改进。
S312|capability|experience|将技能抽象目标和具体实现分离以支持迁移。
S313|capability|regulation|形成并改进可复用准符号推理抽象。
S314|evidence|capability,regulation|区分持续技能能力与上下文及反馈带来的表现提升。
E401|regulation|experience,capability|检验前置网络结构学习如何帮助后续知识获取。
S401|capability|regulation,experience|以可演化技能图组织和调用前置及协同关系。
S402|capability|signal,regulation|在外部图中保存技能前置、冲突与调用证据。
S403|capability|regulation|持续修订技能检索图以改善能力调用。
S404|signal|experience|从文本预测技能前置关系，提供缺口诊断候选。
S405|regulation|experience,capability|协调出题、求解和技能控制器共同演化。
S406|capability|experience|分析已掌握技能怎样形成可组合推理能力。
M450|regulation|capability|分析局部参数学习造成的跨领域行为副作用。
M451|regulation|capability|检验狭窄微调对广泛对齐行为的干扰。
M452|capability|signal,regulation|识别并干预导致广泛失准的行为表示。
M453|regulation|capability|检验微调如何损害已有安全行为。
E701|signal|capability|以行为基础模型估计认知响应；对学习者诊断提供跨领域工具启发。
E702|signal|regulation|模拟学生接受指导后的响应，并作为教师训练反馈。
E703|signal|capability|用行为数据训练认知模型以预测任务响应。
E704|evidence|signal|检验模拟学生是否具有合理能力与学习轨迹。
S450|regulation|signal|研究版本继承、完整验证与恢复策略中的安全持续性。
S451|regulation|capability,signal|控制不安全技能的写入、检索与跨轮继承。
S452|regulation|capability,signal|检验自主技能演化中的持久污染和后续激活。
S453|regulation|signal|以跨版本固定约束调控更新发布与接纳。
S454|background|regulation,signal|可信RSI的范围、风险与证据层级综述。
M454|regulation|capability,signal|在训练期间约束行为漂移并比较安全保持机制。
E350|capability|regulation,experience|通过跨语法元训练形成词汇组合能力，另检验结构外推边界。
E351|evidence|capability|通过SCAN分割检验组合泛化及其失败。
E352|evidence|capability|以COGS区分词汇与结构泛化证据。
M50|experience|regulation,signal|按照当前模型状态和多样性选择训练经历。
M51|capability|experience|研究固定预算重复训练如何形成推理能力。
M52|experience|signal|依据可约化损失选择可学且尚未学会的数据。
M53|regulation|experience,signal|利用技能前置依赖在线分配训练数据。
M54|experience||通过去重和表示多样性构造训练语料。
M55|experience||识别语义重复以选择有效训练材料。
M56|experience|signal|比较梯度表示与预算条件下的指令选择策略。
M57|signal|experience|估计样本上下文贡献并用于训练数据选择。
M58|signal|experience|用holdout上下文损失代理估计候选更新价值。
M59|experience|capability|通过近重复清除改变训练材料与记忆行为。
M60|signal|experience|归因样本组的冗余、互补和交互影响。
M61|experience|signal|主动选择能排除潜在任务歧义的样本。
M62|experience|signal|依据Fisher信息增益选择SFT经历。
M63|background|experience,signal|讨论自生成循环中可学习信息增益的必要性。
M64|capability|experience|通过规范推理示范训练可迁移概率推理。
M65|experience|signal|交互选择能教会黑盒学习者的示例。
E353|capability|regulation|研究学习如何形成可区分潜在状态的表示。
E354|capability|experience|以克隆结构图表达状态别名并支持灵活推断。
M66|capability|regulation|研究不同训练经历形成的状态追踪机制。
M67|capability|experience|从推理轨迹形成可重组原子技能与路由模块。
M68|capability|signal|比较实体状态变化的内部跟踪与查询时聚合机制。
E360|capability|experience,regulation|数据分布改变记忆与规则形成，课程顺序影响二者竞争。
M500|capability|experience,regulation|解释数据分布怎样决定上下文学习和权重记忆。
M501|regulation|experience|比较后训练数据顺序与模型状态的相互作用。
M502|regulation|experience,capability|比较分阶段和整库混合训练安排。
M503|experience|signal|依据梯度空间多样性构造有泛化价值的训练数据。
M504|evidence|regulation|逐样本测量后训练遗忘与逆向迁移。
M505|evidence|regulation,capability|以多模态连续任务检验保持和指令对齐。
M506|regulation|capability|逐级压缩整合LoRA以协调连续学习与保持。
M507|regulation|signal,capability|用梯度代理和有限重放调控稳定性与可塑性。
M508|signal|experience|预测多模态监督数据的实际迁移价值。
M509|evidence|regulation,capability|排除答案记忆与任务先验对持续学习评估的混淆。
M510|capability|regulation|用兼容的动作语言表示形成VLA能力并保持VLM能力。
M511|regulation|capability|在SFT中保留输出多样性以兼顾泛化和旧能力。
M512|experience|signal|研究预算与训练难度如何共同决定泛化和外推。
M513|regulation|capability|比较学习率、LoRA与混合数据的能力保持作用。
M514|capability|experience|研究重复长推理样本在固定更新预算下的巩固收益。
E370|capability|signal|用历史潜状态表达记忆，解释多时间尺度奖励学习。
M530|regulation|capability,signal|以奖励学习记忆新增、更新、删除和筛选策略。
M531|background|capability,regulation|综述外部记忆由存储、反思到经验的演变。
M532|signal|capability,regulation|检验记忆对不同搜索结构的条件贡献。
M533|regulation|capability|研究过时记忆、规则冲突与长期更新失败。
M534|capability|signal,regulation|以证据和适用条件把episode提炼为可调用技能。
E355|regulation|experience,capability|学习何时付出额外规划成本并使用重放。
E356|regulation|signal,capability|按未来需求与收益分配记忆访问和重放。
E380|signal|experience,capability|检验主动触觉训练与反馈能否改变专家学习瓶颈。
E381|signal|experience,capability|研究传入感觉与预测信息权重对训练收益的作用。
E710|regulation|experience,capability|检验自主生成经历如何准备随后从新资源继续学习。
E711|background|capability,regulation|综述即时训练表现与保持、迁移的区别。
M550|capability|regulation|通过消融区分元学习中的特征复用与快速表示更新。
M551|regulation|capability|联合优化未来适应与连续学习中的干扰抑制。
M552|regulation|capability|研究后续训练中上下文学习机制消失与保持。
M553|capability|signal|区分记忆、泛化电路形成和清理的内部学习阶段。
M554|regulation|capability|研究预训练历史如何改变后续微调可学习性。
M555|regulation|capability|在回放充足但计算受限时协调新任务可塑性与保持。
M556|background|capability,regulation|从激励和练习讨论泛化、遗忘与少样本学习的综述视角。
S760|experience|capability|从种子指令扩展任务分布，再用于参数学习。
S761|capability|experience,signal|用筛选的自生成推理持续更新模型，给定题目的轨迹构造关联经验获取。
S762|capability|experience,regulation|环境交互形成持久可调用程序，探索经历与自动课程关联经验获取。
S763|experience|signal,capability|在响应表示中选择更广候选，并区分推理时选择与训练奖励。
S764|experience|signal|冻结语言模型，通过在线辅助蒸馏改变解码探索和候选覆盖。
S765|signal|experience|用过程监督训练评价器，主动选取有说服力的错误解法提供标注。
S766|regulation|experience,capability|递归替换与有限重采样引发跨轮分布信息丢失。
S767|regulation|experience,capability|比较数据累积与替换对长期覆盖和误差的影响。
S768|capability|experience,signal|保留目标数据并与自生成样本对比，持续进行模型微调。
S769|experience|signal,regulation|自生成可执行程序任务，借环境验证获得新约束。
"""

SOURCE_MAP = {}
for _line in _SOURCE_ROWS.strip().splitlines():
    _id, _placement, _related, _reason = _line.split("|", 3)
    if _id in SOURCE_MAP:
        raise ValueError("Duplicate taxonomy source: " + _id)
    _role = _placement if _placement in {"background", "resource", "evidence"} else "research"
    SOURCE_MAP[_id] = {"primary": _placement if _role == "research" else None,
                       "related": _related.split(",") if _related else [],
                       "role": _role, "reason": _reason}
_PAPER_ROWS = """
scienceadv2020-expert-haptic-ceiling-hirano|signal|4.1|experience,capability|E380|主动触觉与反馈改变专家可用的训练信号；不是单纯增加练习量。
hattori-ofc-metarl-nn2023|regulation|6.4|capability||跨时间尺度区分快速任务适应与慢速学习机制的形成。
nhb2026-hybrid-memory-eckstein|capability|5.2|signal|E370|保留历史状态的记忆表示怎样支持后续奖励学习。
nhb2025-distribution-curriculum-pesnot-lerousseau|capability|5.4|experience,regulation|E360|分布与课程改变上下文规则和参数记忆的形成及竞争。
nhb2025-transfer-interference-holton|regulation|6.1|capability|E100|顺序任务中的规则复用同时带来迁移与干扰。
faulty-memory-arxiv2026-zhang|regulation|6.1|capability,signal||连续修订会使原本有用的记忆逐步失真，属于跨轮修订问题。
memory-management-acl2026-xiong|capability|5.2|regulation,signal||检验外部执行记忆的录入、删除和调用怎样改变后续行为。
sharp-wave-ripples-science2024-yang|capability|5.1|experience,regulation||研究相似经历如何被标记并选择用于之后的记忆巩固。
lake-baroni-mlc-nature2023|capability|5.3|regulation,experience|E350|元训练形成可组合映射能力；主问题是能力形成及其泛化边界。
nonlocal-replay-science2021-liu|capability|5.1|signal,regulation||研究经验重放如何将反馈传播为非局部知识更新。
nature2026-narrow-misalignment-betley|regulation|6.1|capability|M450|局部训练怎样干扰其他领域的行为约束。
nature2024-loss-plasticity-dohare|regulation|6.2|capability|M22|持续训练历史怎样影响后来获取新能力的速度。
discorl-nature2025-oh|regulation|6.4|signal,capability||根据实际学习结果发现可迁移的RL更新规则。
recover-or-discover-npj2026-zhang|regulation|6.1|signal,capability||区分旧策略表达受到反馈抑制、重新恢复与学习新策略。
reward-compression-nc2026-molinaro|signal|4.1|capability||从抽象结果构造可用奖励信号；压缩奖励规则支持后续学习。
onan-self-organized-interleaving-2024|regulation|6.2|signal|E310|改变自主安排学习顺序的元认知策略。
hgm-2510-21614|regulation|6.3|signal|S310|按后代潜力和有限补评预算选择演化分支。
inventive-production-pf-2023-kapur|experience|3.2|capability|E98|研究自主产生不同解法的经历与随后学习收益之间的关系。
r2orch-2610-22740|capability|5.4|experience,regulation|S26|自博弈经验经技能抽象再内化到参数，结合技能撤除检验。
rsi-anything-2610-13912|experience|3.2|signal,regulation|S13|世界模型提供行动后果预测并支持后续探索与反馈修正。
optimal-practice-2020-eglington|regulation|6.3|signal|E25|按个体项目历史和时间成本分配复习。
mosaic-memory-2026-shilov|capability|5.3|experience|M17|模糊重复如何累积为模型参数中的文本记忆。
hypothesis-testing-2026-ding|experience|3.2|signal,capability|E26|辨别性目标和结构化尝试能区分竞争规则。
acl2026-good-curriculum-jia|regulation|6.2|experience|M16,M501|模型与任务状态如何改变相同数据排序的学习收益。
rote-learning-iclr2026-wu|capability|5.1|experience|M24|研究先记忆关系再语义化的两阶段能力形成。
soar-2601-18778|regulation|6.4|experience,signal|S17,S47|以实际学生学习增益更新出题教师，学习机制本身发生改变。
acl2026-sft-ilp-xue|signal|4.2|capability,regulation|S37,M27|对未吸收样本作失败诊断，并比较针对性补救。
nc2025-task-similarity-menghi|regulation|6.1|capability|E99|研究任务相似性、跨任务干扰与表征分离。
nc2025-metacognition-underconfidence-katyal|signal|4.1|regulation|E29|局部真实反馈与整体能力判断之间可能产生系统偏差。
nhb2025-moral-strategy-maier|regulation|6.4|signal|E311|根据行动后果更新对整种策略的依赖。
nc2026-schema-reuse-tian|regulation|6.2|capability|E320|结构复用怎样改变新任务学习及规则反转后的适应。
nature2025-centaur-binz|signal|4.2|capability|E701|预测认知响应，为学习者状态建模提供跨领域机制参照。
nature2025-orthogonalized-state-machine-sun|capability|5.1|regulation|E353|学习经历形成可区分潜在状态的知识表示。
nn2024-planning-replay-jensen|regulation|6.3|experience,capability|E355|学习何时付出规划成本，以及何时使用记忆重放。
"""

PAPER_MAP = {}
for _line in _PAPER_ROWS.strip().splitlines():
    _id, _primary, _section, _related, _sources, _reason = _line.split("|", 5)
    if _id in PAPER_MAP:
        raise ValueError("Duplicate taxonomy paper: " + _id)
    PAPER_MAP[_id] = {"primary": _primary, "section": _section,
                      "related": _related.split(",") if _related else [],
                      "source_ids": _sources.split(",") if _sources else [],
                      "role": "research", "reason": _reason}

# These eight papers already have official links in reading-cards.json but no
# matching row in the inherited sources.tsv. Do not invent source identifiers.
PAPER_MAP["hattori-ofc-metarl-nn2023"]["official_url"] = "https://www.nature.com/articles/s41593-023-01485-3"
PAPER_MAP["discorl-nature2025-oh"]["official_url"] = "https://www.nature.com/articles/s41586-025-09761-x"
PAPER_MAP["faulty-memory-arxiv2026-zhang"]["official_url"] = "https://arxiv.org/abs/2605.12978"
PAPER_MAP["memory-management-acl2026-xiong"]["official_url"] = "https://aclanthology.org/2026.acl-long.27/"
PAPER_MAP["sharp-wave-ripples-science2024-yang"]["official_url"] = "https://www.science.org/doi/10.1126/science.adk8261"
PAPER_MAP["nonlocal-replay-science2021-liu"]["official_url"] = "https://www.science.org/doi/10.1126/science.abf1357"
PAPER_MAP["recover-or-discover-npj2026-zhang"]["official_url"] = "https://www.nature.com/articles/s41539-026-00414-w"
PAPER_MAP["reward-compression-nc2026-molinaro"]["official_url"] = "https://www.nature.com/articles/s41467-026-78295-1"

FEATURED_SOURCE_IDS = {
 "experience": ["E26","S24","S40","S102","S205","M61","M62","M503"],
 "signal": ["M27","E29","E380","E18","M60","M508","S35","R01"],
 "capability": ["S26","M24","M17","E370","E350","E353","S31","M534"],
 "regulation": ["S47","M22","E100","M501","E310","E320","S310","E355","S06"],
}

def source_for_paper(paper_id):
    """Return existing reference IDs; deep reads without TSV entries use their own links."""
    return list(PAPER_MAP.get(paper_id, {}).get("source_ids", []))
