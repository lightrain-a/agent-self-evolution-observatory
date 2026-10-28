PAGE = {
"slug":"experiments", "title":"实验方案与推进门槛", "en":"Parallel evidence collection before expensive meta-RL", "lead":"资源充足时，优先购买可辨别证据：同版本分叉、多模型重复、长期测试。不要首先把预算花在叠加全部模块上。",
"sections":[
("assets","少量主环境，明确版本",'''<div class="table-wrap"><table><thead><tr><th>资产</th><th>角色</th><th>要求</th></tr></thead><tbody><tr><td>ToolSandbox [[B01]]</td><td>状态依赖、缺信息、工具流程的机制实验。</td><td>先跑官方基线；派生训练任务单独命名，按根任务族去重划分。</td></tr><tr><td>τ 系列文本交互 [[B02]]</td><td>规则遵循、用户交互、领域迁移。</td><td>锁定 commit、任务 manifest、模拟器和文本协议；当前 main 不与历史 τ² 表混用。</td></tr><tr><td>Terminal-Bench 2.1 [[B03]]</td><td>冻结外部测试。</td><td>固定容器、工具、网络、verifier；不进入课程或元奖励。</td></tr><tr><td>ModularRSI 资源 [[S09]]</td><td>可执行编辑的候选训练来源。</td><td>先审查许可及任务/仓库重叠；本地预检待做。</td></tr><tr><td>Qwen3.5-9B / 27B [[B04]][[B05]]</td><td>主学习者与规模对照；9B 可初始化控制器。</td><td>冻结权重 revision、采样模式、上下文和额度。</td></tr><tr><td>Gemma 4 31B IT [[B06]]</td><td>跨家族验证。</td><td>先过工具解析和基础成功率预检；服务兼容问题不当能力缺陷。</td></tr></tbody></table></div><p>这是<strong>官方页面核对过的候选资产</strong>，不是已经跑通的组合；选型为保证可比性，不声称最新最强。首轮暂不引入 GUI 与具身平台，减少额外环境故障。</p>'''),
("updates","先固定“学习发生在哪里”",'''<div class="table-wrap"><table><thead><tr><th>轨道</th><th>允许写入</th><th>后测复位</th><th>允许结论</th></tr></thead><tbody><tr><td>A · 系统学习</td><td>有长度上限的技能、Harness 或记忆。</td><td>清空任务对话，只装载版本化产物。</td><td>系统持久适应，不称权重增长。</td></tr><tr><td>B · 参数学习</td><td>固定配置 LoRA 等更新。</td><td>清空对话、示范与新增技能；同基础 Harness。</td><td>参数载体的保持与迁移。</td></tr><tr><td>C · 上下文对照</td><td>只保留会话。</td><td>分别保留 / 清空上下文。</td><td>定位暂时适应与答案泄漏。</td></tr></tbody></table></div><p>先做 A，B 检验跨持久载体成立与否；分轨报告。共享 GEPA 或固定编辑模型可减少实现，编辑器差异不能混入支持策略贡献。[[S03]][[S04]][[S07]]</p>'''),
("pilot","P0：一个足以否定主线的问题",'''<p><b>即时最优帮助，是否经常不是延迟独立能力最优帮助？</b>若排序基本一致，就没有理由先训练复杂长程策略。</p><p><b>计划规模：</b>一个环境、12 个原始任务族、2 个学习者、4 个支持条件、3 个重复，共 <code>12×2×4×3=288</code> 个学习分支。各分支用 2 个近迁移、2 个远迁移、2 个旧能力探针，即时和两次干扰后各测一次，共 <code>288×6×2=3,456</code> 次后测。训练、干扰、前测另计。这是计划数，不是已有数据。</p><p>先在 4 族做管线预检，再扩展。任务族是独立统计单位，多个 Probe 不是多个独立样本。用开发集选支持动作、用另一批 Probe 评分，避免同一噪声既选冠军又评价冠军。只在人工故障上出现则不进入大规模 RL。</p>'''),
("splits","数据隔离：不止一个 Held-out",'''<div class="flow"><div><b>D_train</b><small>练习与候选生成</small></div><div><b>D_meta</b><small>训练元策略的延迟奖励</small></div><div><b>D_gate</b><small>版本选择与停止</small></div><div><b>D_test</b><small>最终冻结评测</small></div></div><p>按根任务、模板、仓库、语义近重复分组隔离，不随机打散同模板。课程生成器不可读测试答案、verifier、轨迹。反复查询的 D_gate 也会过拟合；记录次数，使用滚动窗口或预限频次，不永远称其未见。</p><p>新任务、新模型、新错误机制分别评价；换几个参数不等于跨机制泛化。旧正确任务必须进入回归评估，正常与困难任务都展示。</p>'''),
("controls","主实验与强基线",'''<div class="table-wrap"><table><thead><tr><th>对照</th><th>保持一致</th><th>排除解释</th></tr></thead><tbody><tr><td>无更新、强示范、固定渐隐</td><td>学习器和后测。</td><td>简单教学规则足够。</td></tr><tr><td>学习进展 bandit / ActiveSaddler 风格</td><td>轨迹、编辑器、任务、预算。</td><td>只是课程选择收益。[[M03]][[M04]][[S16]]</td></tr><tr><td>短程教学 / SOAR 风格学习奖励</td><td>教师、可用支持动作。</td><td>近迁移目标已充分。[[S17]][[S19]]</td></tr><tr><td>同容量预测器 + contextual bandit</td><td>全部数据与特征，不故意减配。</td><td>复杂结构没必要。</td></tr><tr><td>普通多采样 / 顺序精修</td><td>累计推理和执行预算。</td><td>额外计算带来提升。[[S14]]</td></tr><tr><td>冻结元策略、打乱历史、重置学习者</td><td>底层仍允许更新。</td><td>误把任务能力当元能力。</td></tr></tbody></table></div><p>改造基线标成“基于原方法的本环境适配版”，披露复现差异；不能拿论文原表与新环境结果横比。</p><p>完整实验建议起点：2 个学习者 × 2 个环境 × 4 个核心策略 × 5 条独立学习流 × 8 轮 = <code>640</code> 个更新轮。每轮含多次执行，不是 640 次调用。第三家族用于冻结外推，不重复全部调参。</p>'''),
("metrics","指标、统计与总成本",'''<div class="table-wrap"><table><thead><tr><th>指标</th><th>定义</th></tr></thead><tbody><tr><td>即时 / 延迟独立增益</td><td>清空任务对话后比较新旧版；延迟按干扰更新定义。</td></tr><tr><td>近 / 远迁移</td><td>同机制新实例与新组合、机制分开，报告族覆盖。</td></tr><tr><td>回归与净收益</td><td>原成功变失败比例和所有任务总增益同时报。</td></tr><tr><td>Meta-reset 曲线</td><td>重置相同学习者，仅改变元策略，比较等预算曲线。</td></tr><tr><td>帮助依赖</td><td>有无帮助差值仅作诊断；小差值可能两边都失败。</td></tr><tr><td>选择 regret / 校准</td><td>在独立分叉数据上评价选动作损失及预测误差。</td></tr><tr><td>总成本</td><td>训练 GPU 时、Token、教师、verifier、环境调用与墙钟时间。</td></tr></tbody></table></div><p>成对任务流与随机种子；按族/流聚类区间，报告每条流。预定主终点和检查点，负迁移与失败修改全部保留。元训练成本与部署摊销分开，不能隐去前期数据生成。</p>'''),
("protocol","实现的数据契约",'''<pre><code>{
  "learner_revision": "weight-and-artifact-hash",
  "meta_policy_revision": "policy-hash",
  "task_family": "grouped-before-splitting",
  "split": "train | meta | gate | test",
  "environment_revision": "commit-and-image-digest",
  "parent_state_id": "shared-by-paired-branches",
  "intervention": {"support": "hint", "update": "skill"},
  "environment_seed": 0, "update_seed": 0,
  "persistent_artifact_hash": "post-update-hash",
  "teacher_visible_at_test": false,
  "intervening_updates": [],
  "independent_outcomes": {}, "regressions": [],
  "cost": {"tokens": 0, "gpu_seconds": 0, "env_calls": 0}
}</code></pre><p>这是 schema 示意，零值不是测量。真实运行保存复位检查、解析错误、验证器版本、失败证据与随机分配记录。只在授权沙箱执行，编辑器不得改最终审计代码。</p>'''),
("teaching-track","新候选 I5：教学反馈自进化的独立实验轨道",'''<p>独立候选 <a href="teaching.html"><b>I5：Learner-Induced Blindspot Discovery</b></a> 不仅需要学生得到更高分，更需要 Student 的独立应用能触发<strong>对 Teacher 本身的可验证技能修正</strong>。</p><p>前两周先按 <code>Teacher T0</code>、<code>Student S0/S1/S2</code> 四臂执行，在相同环境与调用预算下定位知识/表达/学生容量/环境问题；P0 必须对比 Teacher Self-Probe、Self-Reflection、NeurIPS 2024 LbT 和教师→学生技能蒸馏。详见方法页中的 24 个任务族预实验与否定条件。[[S20]][[S22]][[E09]]</p><p>这条路线不与 I1 原有的“支持渐隐”实验直接混成一个分数。后续仅在 Student 反馈相比 Teacher 自探更有独特信息、教师自己确实改善时，才尝试学习元级教学策略。</p>'''),
("i2-coevolution","I2：师生共进化的独立验证轨道",'''<p><b>首要问题：</b>教师的教法能否跟随学生成长而改进？第一阶段固定伙伴、教材、教师参考知识和教学顺序，不同时改变课程或更新表面。</p><p>先在相同学生快照上做等预算试教，真实更新后清空课堂上下文测新题；保留学生能力，并用真实学习反馈更新教师的教学策略。原有任务 Skill 写入器作为系统学习轨道；教学 LoRA 与解题 LoRA 的双参数更新作为独立轨道，不混合解释。</p><p><b>新增 E0：双向回应的独立信息价值。</b>先冻结教师，比较 <strong>A 单向完整解释 / B 固定多轮但不读取回应 / C 根据该学生真实回应调整反馈 / D 根据相近学生的错配回应调整反馈</strong>。C−D 是关键：教师轮数、知识范围、学生起点、更新器和预算匹配，D 的回应来自同题相近水平学生。所有学生更新后清空课堂对话，比较未见题真实净迁移，而非当场复述或后测才标出的 Apply。[[E27]][[S105]][[S106]] <a href="idea-i2.html#dialogue-p0">查看四组对照和否定条件</a>。</p><p><b>原有三项实验保留：</b>学生不同阶段的教法收益排序；教师版本 × 冻结学生快照交叉教学；固定教师、仅上下文适应、固定学生库训练教师与当前学生反馈驱动教师的等总成本比较。E0 与这些分支分别计成本，不能把更多反馈/Probe 误当作教学改进。</p><p>教师的开发奖励集与最终审计严格隔离；全部学生副本训练、教师更新、诊断和后测计入预算。当前仅为方案整理，未开始本项目训练。<a href="idea-i2.html#experiments">查看 I2 完整实验和基线</a>。</p>'''),
("i9-practice","I9：集中与交错练习的受控验证",'''
<p><b>研究问题：</b>同样的 A/B/C 训练题，是否因集中、随机交错或不同切换时点而改变无提示新题能力？更进一步，规则已经掌握到什么程度，能否预测下一段日程中哪一种方法更好？<a href="idea-i9-practice-switching.html#experiments">I9 详情页包含原始证据、最近邻及 P0/P1/P2 门槛</a>。</p>
<div class="table-wrap"><table><thead><tr><th>实验阶段</th><th>主要处理变量</th><th>最少需要观察</th></tr></thead><tbody>
<tr><td>P0 · 确认反转与异质性</td><td>固定集中 / 随机交错 / 循环交错 / 集中后交错 / 交错后集中</td><td>两种模型知识状态、规则间相似度；训练表现 vs 独立新题；区别规则形成与选规则</td></tr>
<tr><td>机制对照</td><td>类别相似度、同类重复间隔、最近练习时间的补充匹配</td><td>不能把间隔复习收益误写为只由交错辨别造成</td></tr>
<tr><td>P1 · 切换预测</td><td>只用分叉前的单主题/混合题/保持率探针选日程</td><td>在冻结的未见规则族上超过固定切换与随机交错；全部探针和分叉成本计入</td></tr>
<tr><td>P2 · Agent 技能</td><td>工具调用或代码技能的多个训练主题</td><td>撤除教师与训练上下文后的独立成功和旧技能保持</td></tr>
</tbody></table></div>
<p>固定题目集合、样本出现次数、每题教学顺序、LoRA 结构、优化器和总更新步数；任务按规则族隔离 train / diagnostic / test。I9 不改变 I6 的失败选择、I7 的示范顺序、I8 的错误规则选择，也不使用 I5 的换伴策略。</p>
<p><b>推进门槛：</b>没有稳定规则状态异质性时只报告课程效应；随机交错已经最优，或差异仅由时间间隔解释时，不增加状态 Router。这是实验方案，不是已经完成的结果。</p>
'''),
("i9-future-learnability","I9 扩展：A/B 当前能力匹配后的第三任务 C 学习曲线",'''
<p><b>独立科学问题：</b>同起点、相同 A/B 材料与更新量，不同先后顺序是否改变 C 的未来学习速度，即使 A/B 保持和 C 前测在开发集预注册容差内一致？最近邻是 Sweeney 的 Lie-bracket 目标损失排序、MAML 和 LLM readout plasticity 诊断；不能把这些问题声明为第一次研究。[[M18]][[M20]][[M21]]</p>
<div class="table-wrap"><table><thead><tr><th>阶段</th><th>不许改变的条件</th><th>决定性观察</th></tr></thead><tbody>
<tr><td>P0 · AB 对 BA</td><td>相同起点、材料、Token、更新器、总梯度步；仅反转课程顺序</td><td>先匹配 A/B 保持与 C 初始独立能力，保留全部未匹配失败样本及匹配覆盖率</td></tr>
<tr><td>P1 · 两者真学 C</td><td>相同 C 数据流和步数；主实验重置 AdamW 优化器状态</td><td>0/1/5/10/20/40 步的 C 新题学习曲线面积、达标步数、A/B 回归和组合规则迁移</td></tr>
<tr><td>P2 · 三类 C + 竞争机制</td><td>同等初始能力及诊断预算；共享规则 C₁、排除旧捷径 C₂、无关规则 C₃ 分开预注册，训练/测试规则族隔离</td><td>比较规则关系 × 历史顺序的交互或交叉反转；控制梯度曲率、Sweeney 当前损失排序、readout plasticity 等已有解释</td></tr>
</tbody></table></div>
<p><b>避免泄漏：</b>如果 C 在 A/B 顺序决策前未知，则不得使用任何 C 梯度和最终测试答案决定顺序；目标 C 已知并允许少量开发示例时，可以单独报告目标条件化的几何预测，绝不能混成未知 C 的泛化结果。</p>
<p><b>Go 门槛：</b>当前能力相近且优化器状态重置后，未来 C 学习曲线仍有跨种子/跨规则族顺序差异；若差异仅是 C 初始 loss、历史遗忘或优化器动量，则保留现象并退回 I9，不增加新的调度器。<a href="idea-i9-practice-switching.html#future-p0">详细协议、公式与强基线 →</a></p>
'''),
("i11-emotional-rsi","I11：情绪反馈怎样改变真实的 Agent 自我迭代？",'''
<p><b>首要假设：</b>鼓励、冷静批评、紧迫与中性反馈，可能改变 Agent 的自评、核验、继续探索和是否写回 Skill；这些变化若改善多轮独立净能力才构成 RSI 贡献。ICML 2024 EmotionPrompt、HEART 的多轮同题纠错，以及 COLM 2026 的情绪鲁棒性和序贯决策均为直接强前作，不能重复它们的单次答案评价。[[M28]][[M29]][[M31]][[M33]]</p>
<div class="table-wrap"><table><thead><tr><th>阶段</th><th>处理变量</th><th>要测的独立证据</th></tr></thead><tbody>
<tr><td><b>P0 · 当代表现预检</b></td><td>相同目标题、同 token 语义，五种反馈语气</td><td>首次答案、信心与客观正确率的配对差；P0 不算 RSI 结果</td></tr>
<tr><td><b>P1 · 错误后的学习决定</b></td><td>相同事实反馈下，语气与是否锁定行动两因素对照</td><td>有效探索、核验、过早停止、错误写回、校准偏差，计入调用成本</td></tr>
<tr><td><b>P2 · 多轮持久学习</b></td><td>预设任务流、同编辑器与 Skill/LoRA 更新预算；6–8 轮</td><td>撤辅独立新任务净能力曲线、旧能力回归与错误版本接纳率</td></tr>
<tr><td><b>第二阶段 · 学会选反馈</b></td><td>只读取训练前状态/历史，选择反馈语气；固定/随机/EmotionRL 风格强基线</td><td>重置同一起始 Agent，仅比较新版反馈控制策略带来的未来学习增益</td></tr>
</tbody></table></div>
<p><b>关键区分：</b>在锁定动作协议中只变情绪，检验直接影响；在自由动作协议中比较语气引发的核验/停学/写回差异和持久收益。真实答案由独立验证器提供，学习控制器不读取最终测试反馈。所有诊断、探索、试训与后测按相同总预算计费，不将 P2 的版本更新简单等同于 HEART 的同题多轮再回答。<a href="idea-i11-emotional-rsi.html#p0"><b>查看 I11 最近邻矩阵、P0–P2 详情与停止条件 →</b></a>。</p>
<p class="status">I11 是研究方案，尚无本站新模型复现或持续自迭代实验结果。I10 编号仍待对应独立研究页面，不因本项占用而重排。</p>
'''),
("schedule","按最短证据路径推进",'''<div class="timeline-rsi"><div><b>第 1 周</b><p>固定版本、官方基线、4 族预检；核验最近邻运行资产。</p></div><div><b>第 2 周</b><p>P0 分叉与统计，筛查 I1 / I2。没有自然失败证据则停。</p></div><div><b>第 3–4 周</b><p>只训练一个核心策略，加入强简单基线，扩第二环境。</p></div><div><b>第 5–6 周</b><p>冻结方法，跨模型、Meta-reset、消融，同步形成初稿。</p></div><div><b>缓冲</b><p>独立重跑、失败案例、来源及许可；证据不足就延长。</p></div></div><div class="note">这是执行目标，不是实验已启动或六周必能投稿的承诺。先判断固定强基线是否足够，比先实现庞大系统更接近明确论文。</div>''')]
}
