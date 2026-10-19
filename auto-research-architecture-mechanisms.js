window.AUTO_RESEARCH_MECHANISMS = {
idea:{
scope:{why:"先把研究对象与边界固定下来，避免模型一开始就跳到熟悉的方法，最后解决了一个并非真实需求的问题。",decision:"对象、场景、目标和限制是否足够明确？不明确就补问/收窄；不因写出一段漂亮问题描述而自动通过。",flow:"Scope 产物成为文献检索和问题卡片的约束；后续若发现目标错位，可回到 Scope 修订。",framework:"问题定界 + 显式状态；先定义研究空间，再让候选生成在空间内工作。"},
evidence:{why:"把文献发现、文献主张和真正读过/核验的证据分开，避免把检索命中误当成研究空白。",decision:"当前证据能否支持某项判断？记录来源、阅读深度、限制；缺证据就继续检索或标记 UNKNOWN。",flow:"来源与证据片段供 Cards / Collision 复用；来源身份与限制必须随结论一起传递。",framework:"Evidence ledger + 来源溯源；不是把检索结果直接喂给一个无状态总结器。"},
cards:{why:"将零散观察变成可以比较的研究问题，保留条件与竞争解释，避免过早锁定单一故事。",decision:"是否存在可描述的现象、适用条件和可被反驳的解释？没有就回到证据补齐。",flow:"问题卡片作为 Match 的输入，也作为后续 Collision 对照的固定对象。",framework:"问题地图 / 问题卡片；把 observation、question、hypothesis 和 evidence 分开建模。"},
match:{why:"把问题与机制连接起来，要求机制能产生不同于简单替代的可观察预测。",decision:"机制是否解释关键现象，并产生可区分的预测？若只是给现有方法换名字或重述目标，退回 Cards。",flow:"候选机制、预测与简单替代一起交给 Collision，而不是只传一个 idea title。",framework:"假设生成 + 预测合同；候选不等于结论，预测用于设计区分实验。"},
collision:{why:"在投入实验前检查最接近的已有工作，识别真正的科学差异，而不是靠表面术语差异制造新颖性。",decision:"最近邻是否已经覆盖同一对象、机制和结论？若是则合并、收窄或停止；若证据不足则补读。",flow:"Collision boundary 决定 Design 需要区分哪些方法、假设和适用条件。",framework:"最近邻矩阵 + novelty boundary；对比对象、假设、机制、证据和边界。"},
design:{why:"让实验能够区分竞争解释，避免只证明新方法可运行或只比较最终分数。",decision:"最便宜的 decisive test 是什么？成功与失败分别会改变什么判断？对照、预算、停止条件是否明确？",flow:"冻结后的设计进入 Review 与 P0；实验结果应能回扣到原假设。",framework:"可证伪假设 + 最小区分实验 + matched controls；先设计判别力，再扩大规模。"},
review:{why:"执行前由独立视角挑战问题价值、近邻差异、替代解释和资源成本。",decision:"是否存在致命缺口？需要修订、补证据还是停止？审阅通过和实验授权是两个不同门。",flow:"审阅意见回写到指定阶段；通过后才允许进入 P0 授权流程。",framework:"独立 review gate + 人类确认；不把模型自评当作独立批准。"},
p0:{why:"用受控、可追溯的小实验检验关键预测，而不是直接启动大型实验或让失败自动重跑。",decision:"先授权；执行后将结果分类为支持、范围内证伪、不确定、执行无效或支持阻塞，并保留原始证据。",flow:"结果与失败层级写入交接；只有真实结果经操作方确认后，才能标记 pilot 通过。",framework:"有界执行器 + budget/grant + run receipt；计划、授权、执行、记录、接受分离。"},
handoff:{why:"把研究定义、真实结果、证据和决策一起交给下一套系统，防止下游只接到一个摘要而丢失前提。",decision:"问题/贡献/保留决策是否完整？pilot 是否经确认？证据路径与哈希是否有效？否则导出未通过计划或拒收。",flow:"导出 handoff.json、evidence/、packet-manifest.json、README；Flow Ink 独立初始化后由 W0 再核验。",framework:"跨系统契约 + provenance manifest；不共享隐式内存、不自动调用下游、不伪造 passed 标志。"}
},
ink:{
w0:{why:"先检查上游研究交接是否真实、完整、可追溯；Ink 不再重新发现 Idea，也不替上游补造实验结果。",decision:"idea_passed、pilot_passed、question、contribution、decisions 和 evidence 是否齐全且证据文件存在？失败则 HOLD。",flow:"通过后初始化当前研究的 constitution / project snapshot，作为 W1 的唯一有效研究起点。",framework:"Contract validation + project bootstrap；把上游结论作为明确输入而非聊天上下文。"},
w1:{why:"在跑正式实验前冻结科学主线、最近邻差异、任务矩阵、指标和分母，防止结果出来后再改比较规则。",decision:"数据集、模型、评价器、指标、源代码版本与任务全集是否明确？最近邻差异是否能在正文中被读者看见？",flow:"产生 outline、experiment matrix、table spec、positioning ledger；W2 以冻结协议为输入。",framework:"协议冻结 + positioning ledger + table contract；协议或输入漂移时，下游阶段失效并需重新验收。"},
w2:{why:"将固定实验矩阵转成可控执行图，使每项任务有依赖、授权、预算、输出和覆盖责任。",decision:"依赖是否满足、命令是否在允许列表、覆盖是否恰好覆盖预定义单元？中断/失败先检查副作用，再显式恢复或重置。",flow:"每个任务产出原始结果与 run receipt；W3 只消费当前有效、可追溯的结果。",framework:"有界 DAG + idempotent resume + execution grant + run/artifact lineage；不等于 OS 级沙箱。"},
w3:{why:"把原始结果变成可以审计的主表，而不是从论文草稿、聊天记录或手工复制的数字中构造结果。",decision:"每个任务×方法单元是否有真实源文件、哈希、重复身份、样本数/评测 ID 和核验者？缺项保持缺失而非填零。",flow:"输出 registry 和 Table 1，记录每个表格单元的来源；W4 与 W5 引用同一核验版本。",framework:"显式结果台账 + 固定覆盖集 + source/hash validation；结果完整性与科学正确性分别判断。"},
w4:{why:"让每张图和每段分析回答一个具体研究问题，区分实测统计图与概念框架图，避免图形生成改变数据含义。",decision:"图的输入是否是已核验数据？统计图走代码生成，概念图走框架图工作流，混合图拆分两条路线。",flow:"产出 analysis report 与图文件，并将图绑定到结果版本和读者问题；W5 使用这些稳定证据。",framework:"reader-question-first + typed figure route + artifact binding；可视化路线取决于图的语义类型。"},
w5:{why:"把已经确认的研究逻辑和证据组织成论文，而不是让写作模型自行补足缺失结果或重塑研究主张。",decision:"每项关键主张是否有来源/实验工件支持？未完成实验对应的结论是否保持待定？Prompt 是否与当前章节任务匹配？",flow:"章节草稿和 LaTeX 引用已核验表格/图表；变更结果或协议后，相关主张和稿件需重审。",framework:"Claim–Evidence binding + task-specific prompt + staged drafting；先事实与逻辑，再语言和版式。"},
w6:{why:"将科学问题和最关键的审稿风险优先处理，避免把修辞润色误当成解决科学缺陷。",decision:"关键弱点是否影响贡献成立？最便宜的决定性修复/反证是什么？修订是否越过原始协议或证据边界？",flow:"每轮修改保留版本和审阅记录；影响主张、结果或协议的修改会触发下游重新检查。",framework:"独立 review + critical-weakness prioritization + revision lineage；评审身份不同本身不证明独立性。"},
w7:{why:"验证最终编译出来的真实 PDF，而不是仅确认源文件存在或编译命令返回成功。",decision:"是否检查每一页的图表、公式、引用、空白、声明与证据一致性？源文件/PDF 哈希变化后旧检查是否失效？",flow:"生成精确 PDF 快照和逐页检查记录；W8 只接受与当前源快照一致的审查。",framework:"Build artifact + page-level visual/content QA + snapshot invalidation。"},
w8:{why:"保证最终 PDF、源码、实验结果、主张台账和审查记录指向同一版本，避免交付包和审过的版本不一致。",decision:"release-strength audit 是否无 blocker？必需版本、主张、工件、逐页审查和作者确认是否齐全？",flow:"输出 release manifest 与审计包；最后的投稿操作仍由作者执行。",framework:"Research OS release gate + immutable lineage + human submission boundary。"}
}
};