# RSI 论文精读卡片 · 维护说明

本站长期积累的精读卡片在 `rsi/reading-cards.json`，与 `rsi/sources.tsv` 的广覆盖来源台账分开。一次新增论文只追加 `papers` 数组中的一个 JSON 对象，不要直接手改生成的 `rsi/reading-cards.html`。

## 外部长综述如何进入本站（2026-10-28 规则）

- **先做来源核查，不要全文搬运**：公众号、博客等二手综述保留作者、日期和标题，提炼独立导读；不重发原文、整段长引用和作者配图。原文没有确认公开链接时，不伪造链接。
- **归入领域全景，不伪装成学术论文卡片**：现有四问 + 安全标签照旧；综述的独特贡献是跨问题的证据组织和近期缺失来源。相关入口在 `literature.html#rsi-landscape-20261003`。
- **只补核查过的原始文献**：`rsi/sources.tsv` 的 R01–R11 是首轮精选；参考论文的原始页或正式会议页，并标明仅摘要核验、没有独立复现实验。剩余引用须分批核实、去重后增量入库。
- **按时间窗口限制结论**：2026-10-03 的长文属于该日的证据快照；关于严格 RSI、RL 是否真正拓宽采样支持集、厂商 R&D 自动化和安全事故的结论，须标成特定定义、实验设置或当时报告，不写成全领域已经证明的通则。

## 一篇卡片应该留下什么

- **元信息**：`id`（唯一、稳定）、`short_title`、`title`、`authors`、`first_posted`、`version`、`read_on`、`reading_level`、`links`，并且恰好选择一种主来源：arXiv 预印本使用 `arxiv`；正式期刊论文使用 `doi` + `official_url`，后者必须与 `links.html` 一致。可另附 `links.pdf`（PDF）、`links.code`（作者代码）、`links.data`（公开数据，如 Figshare）、`links.adapter`（公开可复用的 LoRA/QLoRA 权重）或 `links.full_text`（开放全文）。不要将数据集链接冒充源码仓库。不应给期刊文章编造 arXiv ID。
- **作者署名单位**：`lead_institution`（卡片上显示的主要单位）、`institutions`（原文列出的全部单位）、`institution_source`（PDF 中核对位置）、`publication`（技术报告、预印本或正式发表状态）；不要把作者单位混写成录用会议。
- **五问框架（全库统一）**：根节点 `research_questions` 固定五个问题：信号对不对、有没有新东西、采不采得到、吸收了会不会丢、安全。每篇的 `research_coverage` 必须恰好包含 `signal` / `novelty` / `reach` / `retention` / `safety`，每项写 `level`、`contribution`（论文到底做了什么）和 `open_question`（留下了什么）。
- **分类边界**：`level` 仅取 `core`（重点研究）、`partial`（部分涉及）、`not_addressed`（未直接研究）。**覆盖不等于已经解决**：在候选集合里排序不代表扩展采样支持集；保留某个版本不等于不会遗忘旧能力；约束声明不代表对抗安全已验证。
- **速览必须是 C-I-D-R 四句话**：`one_sentence` 保留一句最直白的印象（不超过 100 字），`story` 必须按 `challenge`、`insight`、`design`、`result` 顺序填全，每段不超过 130 字。Challenge 写具体困难，不要提前讲方法；Insight 讲为什么这种思路有用，不复述模块名称；Design 用可想象的动作顺序介绍做法；Result 必须给出作者实际报告的对照或明确说明证据不充分。旧 `problem` / `setup` 字段仅作为扩展记录与检索。
- **值得复用的机制**：`key_ideas` 数组，每条含 `name`、`summary`、`formula`（纯文本公式，避免直接插 HTML）。
- **证据与边界**：`evidence`、`boundaries`，分别区分论文报告结果、实现假设、未验证的局限。
- **研究转化**：`our_relevance`、`next_test`，写可验证的迁移实验，不能表述成原论文已证明的事情。
- **发现与检索**：`tags` 供归类，站内全局搜索索引和本页筛选由构建流程自动更新。
- **五类指标/五类原因速览（可选）**：要保留的五种实验维度可在 `deep_read.metric_summary` 提供恰好五项 `family` / `metrics` / `meaning` / `result`。`metric_summary_title` / `metric_summary_intro` 可以改成适合论文的白话标题；页面先给读者看“是什么 + 原文对应结果”，详细公式和反例折叠在 Design。ACL 2026 Curriculum 的五类是难度量；ACL 2026 Why SFT Fails to Learn 的五类是诊断模式，不能当成相互独立、完整覆盖的根因标签。不同数据集/模型的增益不可直接横向排名。
- **完整精读（可选）**：为深入读过的论文追加 `deep_read`（`focus`、`terms` 术语白话解释、`sections`）。每章填写稳定 `id`、短中文 `title`、`stage`（`challenge` / `insight` / `design` / `result` / `next`）及内容 `blocks`，同组可用 `order` 控制显示顺序。正文按四段主线展示短解释，例子、公式、实验证据折叠在相应段落中；`next` 单独承载局限与我们的延伸。通用块类型仍为 `prose`、`steps`、`formula`、`table`、`callout`、`evidence`、`bullets`、`tests`。构建脚本自动生成 `rsi/reading-notes.html`、卡片跳转和章节搜索索引。
- **Closest Related Work（可选）**：`rsi/related-work.json` 独立于广覆盖来源台账，按论文 `paper_id` 保存经过原文核验的最近邻比较。采用 Obsidian《AI审稿时代的Related Work与Novelty前置》的 `closest work → shared → different → why → decisive evidence`；每行还要保存问题、更新对象、反馈来源、原论文/正式发表状态、与被精读论文的比较关系和是否具有公平直接对照。最近邻仅保留 3–8 项，其余放“领域脉络补充”。网页自动将表格放在 **Result 之后、研究延伸之前**，速览卡片显示直接跳转。

**先说人话，再引入术语**：第一屏应该能让首次阅读者在 60 秒内复述“难在哪里—为什么可解—怎么做—结果怎样”；出现 Policy / World Model / Pair Gate 等术语时，先给一个常见场景和一句白话解释。标题优先用问题句（如“为什么两个模型都变好，系统反而变差？”），不要用“Section 2.5 · 多模态自适应组合增益”式空泛标题。公式放到读者已经理解其必要性之后。

**精读与原文分离**：论文原始实验、解释公式的假设数字、本站的学术判断和待做实验必须清楚标注。特别要区别“已掌握项目随时间遗忘、进入复习阈值”与“原本不会的新任务因其他知识学习而提高可学习性”；前者是记忆复习调度，后者需要真实跨任务训练与独立后测，等待本身不是新机制。不能把“提出 Pair Gate”写成“已经充分证明它有独立收益”，也不能把固定代码生成器的结果当作代码模型本身持续学习的证据。

不要写未经核查的成绩或把相近数据集名称擅自扩大。优先固定 arXiv 的版本页面、论文代码链接和阅读日期。

## 可长期引用的理论笔记（2026-10-28 新增）

- **理论唯一源**：`rsi/theory-notes.json`，可逐条追加 `entries`；`scripts/rsi_pages/theory-notes.py` 自动生成 `rsi/theory-notes.html`，并更新导航和全站搜索。每条理论具有唯一 `id`，在线稳定链接为 `/rsi/theory-notes.html#<id>`。不要修改已公开的旧 `id`，以免破坏后续 Idea 的引用。
- **四重内容**：清晰的科学问题、原始论文的机制位置与链接、LaTeX 及可直接读的公式、逐步推导和可迁移边界；特别标记 `paper-mechanism`（作者证据）、`teaching-derivation`（自己推导）和 `rsi-hypothesis`（待验证）。
- **来源双向引用**：每条 `source_paper_id` 必须存在于 `reading-cards.json`；`source_anchor` 必须是该论文 `deep_read.sections` 的真实章节 ID。理论页自动链接到对应的论文精读，论文精读自动加入返回理论页的快捷入口。
- **第一批内容**：DiscoRL · Nature 2025，共七条：更新目标生成、半梯度表达能力、元梯度递推、快慢时间尺度、自举预测与消融、跨 Agent 稳定化、以及标为未验证的 RSI 未来可学习性目标。不要把教学二维反例和未来 C 任务公式说成论文原式。
- **第二批理论（2026-10-28）**：Science 2021 非局部信用分配与 Need × Gain（理论原出处 Mattar & Daw, Nature Neuroscience 2018）、GradSim（EMNLP 2024）一阶梯度传播推导、I8 的未见题净迁移候选指标。共 11 条理论主题，新增 `additional_sources` 可直接链接理论原始论文（避免只链回Science）。
- **LLM 最近邻证据记录**：Science 完整阅读卡片 `nonlocal-replay-science2021-liu` + `rsi/related-work.json` 中八篇对照；I8 在 `science2021-nonlocal` 和 `nonlocal-p0` 章节保留机制实验与碰撞边界。One-Shot RLVR/OPD 的“一训练题”与 Science 的“一次当前反馈”不可混报；B 无训练监督与主动知识簇更新也是不同操作。
- **第三批理论（2026-10-29）**：Science 2024 Yang 等小鼠海马清醒 SPW-R—事后睡眠选择性重放，理论链接 `#awake-ripple-memory-tagging`，另有明确标为本站假设的经验标签 vs 真实巩固效用 `#experience-tag-vs-consolidation-utility`。务必写出分析层级：6只小鼠/26会话/4,469细胞；Fig.4H为5只/16会话，R=0.86。原文没直接测长期行为能力也没对不同成功/失败类型做随机选择实验。I6以 `science2024-memory-tagging` 章节建立入口；本次仅发表该 Science 精读，ACL2026 与 arXiv2026 作为最近邻指路。
- **验证**：执行 `python3 scripts/build_rsi_research.py && python3 scripts/build_rsi_site.py && python3 scripts/test_rsi_site.py`，会检测唯一 ID、公式/LaTeX、论文锚点、双向链接以及公开输出。

## RSI 记忆研究地图：暂不编号（2026-10-29）

NHB 2026《Hybrid neural–cognitive models reveal how memory shapes human reward learning》已纳入完整十节精读 `nhb2026-hybrid-memory-eckstein`（正式 Nature DOI、Google DeepMind 代码、OSF 数据均有链接）。作者用862名人的四臂奖励行为对照传统Q、Context-ANN、Memory-ANN；得到的是**人类行为拟合**，并未测LLM未来LoRA净学习。Figure 3i / 4g 的历史滞后系数设计已留绘图字段，不能拿人类数据冒充本站LLM成果。

`scripts/rsi_pages/memory-research-map.py` 为未编号研究候选池，按正交控制变量整理：A 学习历史作为**状态预测信号**（最接近I9）；B 外部Episode的**随机检索因果收益**；C 正确经验的**Raw/Abstract/Skill/LoRA巩固方式**（保留已有 `experience-consolidation.py`）；D Meta-Agent依据历史做**读写/检索/停止/写回选择**。I14（学习规则自进化）已经独立编号；本页A/B/C/D记忆候选没有另外占用I15及后续编号。候选拆分只有在独立现象、可证伪机制、明确最近邻和同预算真实更新结果成立时进行。

特别注意：历史日志帮助预测当前参数状态，与Meta-controller**实际读取历史并改变学习动作**是两条不同因果路径；必须保留当前梯度、优化器状态、简单窗口统计等强基线。Memory-R1（ACL 2026）已有学习记忆读写；Memory→Skill相关系统亦有先例，不因换一个记忆名称声明创新。

## 经验到长期能力研究候选（2026-10-29 新增）

- **两篇原论文精读**：`memory-management-acl2026-xiong` 是 ACL 2026 正式论文（4 Agent 的 Add/Delete、严格评估Oracle、历史效用与误召回）；`faulty-memory-arxiv2026-zhang` 是 arXiv:2605.12978v2（固定正确轨迹的压缩日程、Force/Auto、ARC 19/33任务、Table 5 固定输入消融）。两者必须标明外部Memory而非权重更新。
- **数字冲突注记**：2605.12978v2 摘要“fails on 54%”与正文“accuracy 100%→54%”不一致。正文Fig.2支持下降 **46 pp**，公开笔记保留矛盾，不以摘要替换正文。
- **理论扩充**：`memory-retrieval-causal-utility`（ACL 2026 的经验跟随/历史效用 vs 本站独立随机调用效应）与 `memory-consolidation-fidelity`（2026 v2 的初次压缩、旧摘要污染、原地修改；不把残余差距全部归因于初次损失）。两个主题均有固定锚点。
- **未编号研究提案**：`scripts/rsi_pages/experience-consolidation.py` → `rsi/experience-consolidation.html`，P0/P1/P2 设计分别验证固定正确Episode下巩固正负效应、Memory选择与巩固的正交因果作用、Skill/LoRA撤辅后的独立能力。与I6错误轨迹价值、I8单点非局部迁移、I13安全接纳保持边界；不能把已有Auto/Force/History-Deletion包装成首创。
- **测试契约**：`scripts/test_rsi_site.py` 检查新论文/版本、原始结果统计口径、Theory对应来源、候选页及导航，生成产物统一来自结构源与页面源，不直接编辑静态HTML。

## Science Advances 2020 · 高水平学习者的训练信号瓶颈（2026-10-29）

- 完整精读的唯一源：`rsi/reading-cards.json` 中 `scienceadv2020-expert-haptic-ceiling-hirano`，正式 DOI `10.1126/sciadv.abd2558`，2024 后续 iScience 用 `E381` 单独注明。正文实验必须保留：Exp1专家36（AHT/普通练习/休息各12）；AHT400组二择≈800按键、普通重复400按键，任务/反馈/数量并未严格配平；Exp2专家13+13/非音乐家13，训练指有反馈组效果与食指不迁移；Exp3专家12/非音乐家12，直接100次误差练习专家p=0.95、非音乐家p<0.01。30分钟保持不能宣称跨月保持。
- 未编号独立候选：`scripts/rsi_pages/learning-signal-bottlenecks.py` → `/rsi/learning-signal-bottlenecks.html`。目标不是“更密奖励通用有效”，而是事前确认高能力平台、诊断可训练但尚未掌握的相关辨别能力，再在同样模型/样本/LoRA成本下比较 **直接执行反馈、更多普通练习、对症辨别+正确反馈、对症辨别无反馈、非诊断性辨别+反馈**。撤辅后必须测原任务未见对象/组合规则/旧能力。
- 边界：I9变课程顺序、I10变规则区分样本D、I12变前置知识，学习规则自进化候选变更新规则/元目标，本候选只改变监督目标及任务相关反馈。SOAR（ICML 2026）已经研究低成功稀疏奖励的stepping stones；本候选研究目标任务已高水平但保留细微残余错误的诊断性训练。没有P0因果机制前不占新的I编号，也不修改当前已发布的研究方向排序。
- 上线入口应由生成器自动产生；构建、站内链接、RSI浏览器与移动端检查全部通过才推送。

## 快慢Meta-RL及学习规则自进化候选（2026-10-29）

- **Hattori 完整精读**：`hattori-ofc-metarl-nn2023`，Nature Neuroscience 2023（小鼠OFC + 5个A2C-RNN，13节）。实验标准：奖励概率反转任务与baiting；每个session 500trial时RNN权重冻结、跨session才更新；早期5+5只小鼠用paAIP2阻断慢可塑性、专家另5只做交替同类阻断、活动抑制再测快RL；不把“没有显著差异”写成证明绝对没有可塑性。
- **DiscoRL 已存在，不重复建档**：`discorl-nature2025-oh`的完整精读（Nature 2025）和原来的七条理论保留；只新增一个Hattori对照章节，区分OFC机制证据与Meta-gradient目标发现。
- **三条理论笔记**：`#metarl-two-timescale-learning`、`#policy-history-kernel-measurement`、`#meta-improvement-intervention-contract`。Eq.(12)历史回归以及Policy Axis来自Hattori，未来任务C的AULC是本站未验证指标；作者原证据与教学简式分开。
- **I14 正式管理编号（2026-10-29）**：`scripts/rsi_pages/learning-rule-evolution.py` → `/rsi/learning-rule-evolution.html`，左侧导航与研究池统一标记为 I14 · 学习规则自进化。只改变学习规则 η / 更新目标，固定学生、数据、教材顺序、教师及预算；P0 检验未来可学习性差异，P1 以 Old/New/Best Fixed/Shuffled History/No Student Update 做冻结与重置干预。I2改变教师，I9改变课程；I14是否独立成稿由Go/缩题/降级证据决定，编号本身不意味着已经验证。历史I1–I13排名留存，I14待同口径打分。
- **测试**：`scripts/test_rsi_site.py` 校验两篇论文、两者关系章节、理论锚点、候选P0/P1和目录仍只有I1–I13正式编号。数据链接采用原论文官方Zenodo `10.5281/zenodo.8378063`、代码 `ryhattori/MetaRL-PRL`。

## RSI 研究时间轴与会议 DDL

`rsi/timeline-data.json` 是会议与人工研究里程碑的唯一数据源：

- `venues` 中目前只有 CVPR 2027、ICML 2027、ACL 2027；每个节点保留 `source_url`、`verified_at`（顶层）、`date`、`due_at`、`status`。
- **已发布官方截止**使用 `status=official`、日期 `YYYY-MM-DD`，以及包含 `-12:00` 的准确 AoE 时间戳 `YYYY-MM-DDT23:59:00-12:00`。
- **尚未发布**必须设 `status=pending`、`date=null`、`due_at=null`，不可把往届时间或第三方估算写为正式 DDL。
- `research_events` 仅纳入有证据链接的研究记录；不得把方案、预期结果当成已完成实验。
- 论文阅读事件不需要重复记录：`scripts/rsi_pages/timeline.py` 自动读取 `rsi/reading-cards.json` 的 `read_on` 和一句话结论，并生成可点击记录。
- 设计和交互代码分别在 `rsi/timeline.css`、`rsi/timeline-view.js`，无需从 Agent 主站的复杂时间轴依赖。
- **2026-10-29 交互版本**：官方 AoE 日期倒计时每秒更新、同步换算北京时间；待公布节点仍显示“待公布”且不生成计时器。月历连续覆盖有记录的月份（包括无记录的中间月份），日期格显示记录量和三类事件标记；点击日期进入该日记录，再次点击或“清除日期筛选”恢复。事件类型、截止状态、主题标签、全文关键词可组合筛选，研究标签可点按；研究事件可在 `research_events[].tags` 中追加明确标签，阅读事件自动继承论文的全部 `tags`。精读时间轴条目可展开原始 `story.challenge/design/result`，且精读卡片回链 `timeline.html#reading-<paper-id>`。用户可据此快速理解论文内容，不能把本站的研究设想写成作者实验结论。
- 自动化检查：`scripts/test_rsi_site.py` 保证结构/来源/锚点；`scripts/test_rsi_browser.py` 覆盖日历切换、标签筛选、跳秒、北京时间与移动端（需先完成 Agent 和 RSI 两站静态构建）。
- 新增会议时更新 `venues` 与经过核验的日期，执行 `python3 scripts/build_rsi_research.py` 重新生成静态时间轴与全站检索索引。

## 已公开 I1–I9 与 I11 研究卡片的统一写作结构

源文件为 `scripts/rsi_pages/ideas.py`，生成后展示在 `rsi/ideas.html`，不要直接编辑生成的 HTML。每条 Idea 固定五段，保持自然语言、清楚的前作边界：

1. **Challenge（难在哪里）**：用一个真实任务里的困难说明为什么现有做法不够，避免堆叠抽象词。
2. **现有工作**：写成“某工作研究的是……；我们希望研究的是……”，指出已经覆盖的机制，不靠换名称声称创新。
3. **Insight（为何可解）**：一句能被实验推翻的判断，解释为什么新的观察或对照有机会解决 Challenge。
4. **Design（如何做）**：解释 Agent 真正会做的 3–4 步，说明修改什么（Skill / Memory / Harness / 参数），但不把控制图当贡献。
5. **实验设计**：相同任务、学习器与预算下的强基线、独立测试、关键指标，以及效果不出现时如何解释。

I5 当前主线是**十模型双向互教与动态交换伙伴**；`teaching.py` 保存早期教学反馈诊断教师盲点的支线。当前 I6 只研究**同题不同失败轨迹的学习价值、停止与重访**（`idea-i6-failure-value.py`）；I7 只改变**先独立尝试还是先看同一示范**（`idea-i7-learning-order.py`）；I8 只研究**当前错误在固定纠错后能否迁移到同规则新题**（`i8.py`）；I9 只改变**不同主题之间的集中/交错练习顺序与切换时机**（`idea-i9-practice-switching.py`）。四条在 `ideas.html` 都完整显示五段，同时保留独立详情页。旧 `idea-i6.py` 是历史跨轮瓶颈切换草案，不能冒充当前 I6。

自动核查必须覆盖 I1–I9 的五段顺序、相关工作出处、四步方法流程、同页入口、独立详情页，以及 I6/I7/I8/I9 的处理变量互不混淆。I11 研究情绪反馈语气是否通过改变 Agent 的学习控制、版本写回与真实长期净增益而影响自我迭代；独立页为 \`idea-i11-emotional-rsi.py\`。I10 当前没有独立站点页面，保留编号不补假内容。后续修改先运行 RSI 生成、独立站构建、静态断言和浏览器检查。

## 生成与核查

在仓库根目录执行：

```bash
python3 scripts/build_static_site.py      # Agent 站
python3 scripts/build_rsi_research.py      # 生成 RSI 页面与独立导航
python3 scripts/build_rsi_site.py          # RSI 独立站输出到 _site/rsi
python3 scripts/test_rsi_site.py
python3 scripts/test_rsi_browser.py
```

对应源文件是 `scripts/rsi_pages/reading-cards.py`（四步卡片）、`scripts/rsi_pages/reading-notes.py`（四段精读与细节折叠）、`scripts/build_rsi_research.py`（目录与索引）、`rsi/research.js`（浏览器筛选）。后续新增论文只需要写好统一数据；页面不应退回大段摘要堆砌。

RSI 站点使用独立的 `site-nav.js`，不再依赖 Agent 站的 `data.js`。在左侧“研究方向与实验”中，先显示“研究方向总览”，再按 I1→I9 与 I11 各保留一个编号入口（I10 保留未发布），最后是实验执行方案。I1–I4 跳到 `ideas.html#idea-1` 等完整卡片，I5–I9 保留详情页；`ideas.html` 同时为 I1–I9 都提供完整的五段式内容，页面顶部 I6–I9 的速览入口指向同页卡片，正文仍可进入详情页。浏览器对同页锚点动态更新当前高亮。**I5 教学反馈诊断**和**历史跨轮瓶颈切换**只作为归档页面保留，从所属研究页进入，不在导航重复编号。修改目录必须更新 `scripts/build_rsi_research.py` 和两个 RSI 站点测试，并验证旧 URL 不失效。

双站架构、入口和单独导出方法参见根目录 `SITES.md`。部署仍使用仓库现有 GitHub Pages workflow：合入 `main` 后先构建 Agent、再构建 RSI；不要把 private 数据或本地路径写入公共卡片。

## I2 师生共进化（2026-10-27 合并）

`idea-i2.py` 是当前 I2 的完整方案，`ideas.py#idea-2` 保留五段摘要和旧锚点。教师学习教法，学生学习解题；主要目标分别为冻结学生库上的教学增益和撤辅后的学生独立能力。原 Skill 更新轨道保留，双 LoRA 参数更新单列，不能混报。固定伙伴、教材和教学顺序，保持 I5/I6/I7/I8/I9 边界。侧栏 I2 指向 `idea-i2.html`，仍按 I1–I9 单次编号。旧 `idea-i6.py` 是历史瓶颈方案，不是当前失败价值 I6。

## I9 2026-10-28 扩展：相同能力、不同历史，学习新任务 C 的速度是否不同？

I9 的集中/交错主问题继续保留。\`idea-i9-practice-switching.py\` 中新增 \`future-question\`、\`future-geometry\`、\`future-related\`、\`future-p0\`、\`future-gate\` 五节，研究在相同初始检查点和 A/B 材料、学习后当前 A/B/C 能力相近时，A→B 与 B→A 是否仍改变新任务 C 的真实学习曲线。最相近的顺序几何是 Sweeney ICML 2026，未来可塑性近邻为 Ren et al. 2026、MAML 2017、Nature 2024 与 ACL 2026 PaRSP。npj 2026 人类运动假设检验仅作为规则可辨识性机制启发。公式只属小步长 SGD 局部推导，不是原论文实测。

实验有两个不可混淆的轨道：C 已知、允许少量开发支持样本的几何诊断；C 完全未知、不允许顺序选择器读取 C 任何样例的泛化测试。主实验进入 C 前重置 AdamW 优化器状态，分别报告 A/B 保持、C 前测匹配覆盖率、C 独立测试曲线、旧技能回归和总成本。此新增研究内容不改变左侧 I1–I9 的唯一编号，不另设 I10。
