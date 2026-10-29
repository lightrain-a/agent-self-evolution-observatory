# 第三章网页改写 → 综述回填交接

日期：2026-10-29。本文是编辑映射，不是新实验报告。

## 来源与本轮范围

- 用户指定综述：`https://github.com/lightrain-a/RSI_review2610`。
- 实际读取的 main 版本：`8f3eec2e370e251e7d72ec7e981ba44285f9f75a`。
- 实际读取文件：`README.md`、`sections/acquisition.tex`、`sections/foundations.tex`、`references.bib`。
- 通过用户工作站既有GitHub授权只读获取；未改变论文仓库任何分支。
- 网页唯一源：`scripts/rsi_pages/experience.py`，由 `rsi_framework.framework_pages` 调用。网址 `rsi/experience.html`、原 `question`、`section-3-1` 至 `section-3-4`、`research-directions`、`evidence-connection`、`representative-work` 锚点保留。
- 方法论：`docs/rsi/reader-first-research-writing.md`；完整复盘保存在用户Obsidian既有科研写作目录第26页。

## 原稿到网页的对应

| 原稿论证单元 | 网页位置 | 编辑变化与未来回填建议 |
|---|---|---|
| 3.1 p1：Self-Instruct / Voyager / SOAR分别补任务覆盖、行动经历和学习机会 | `section-3-1`主体与折叠例子 | 先问“没试到办法还是缺基础”，再用三项方法说明获取单位不同；不直接以数据集规模开篇 |
| 3.1 p2：RepExp搜索不足 vs Hirano专家子功能瓶颈 | `section-3-1`两个原文证据块 | 将对照写成同一失败的两种解释，补充扩大搜索/训练子能力/继续原练习的可证伪比较 |
| 3.2 p1：Self-Instruct生成问题 vs STaR生成轨迹 | `section-3-2`开头并列论文 | 明确问题分布和解法分布是两个处理变量，避免“自生成更多数据”一词笼统覆盖 |
| 3.2 p2：RepExp候选选择/训练奖励 vs ESamp解码干预 | `candidate-coverage` | 以“候选更多却不一定首答更准”开篇；分别记录主模型是否冻结和下一轮保留什么状态 |
| 3.2 p3：选择谁来验证，还是选择谁来标注以训练评价器 | 3.2末尾折叠 | 保留Let's Verify Step by Step；省验证调用不等于全流程省算力，评价器训练收益另测 |
| 3.3 p1：SOAR实际学习收益 + Bayesian教师的信息条件 | 网站拆分到3.3/3.4 | Bayesian教学用于“全知正确教师为何未必更好学”；SOAR用于“当前难度为何不是教学收益” |
| 3.3 p2：Ding的竞争策略与反例 | `novelty-not-volume` | 提前放到构造有信息量的经历；明确行为假设辨别，不误写快/慢脑回路 |
| 3.4 p1：Mosaic Memory与探索覆盖 | `novelty-not-volume`及3.4折叠 | 分开字面重复、表征覆盖与策略差异；文本记忆论文不直接证明推理训练无效 |
| 3.4 p2：替换数据的退化 vs 保留/累积条件 | `retain-or-replace` | 用两篇并列证据解释结论为何不同；保留、暴露量和成本都可能变化，不把未崩溃说成无限增长 |
| 3.4 p3：SPIN保留SFT目标 vs Absolute Zero执行器约束 | `external-information` | 放到网站3.3外部信息；“无新人工标签”不等于无任何外部信息 |

注意：网站保持既有3.3“教师、伙伴、工具”和3.4“经验选择”的分类职责，原论文3.3/3.4次序并不与之逐段一一对应。回填应按论证单元，不按小节编号直接覆盖。

## 新增的阅读入口

开头六组发现分别关联：尝试量/瓶颈、候选覆盖/首答质量、文本新颖/规则信息、教师正确/学生可学、难度代理/真实收益、新数据/旧覆盖。所有读者入口都回到相应小节；不新增研究Idea。

每节就近放原始文献与其贡献；末尾只保留来源索引。新增中文例子只是解释，不是新实验。LLM和RSI改进建议明确标为“待检验”。

## 后续修改论文时优先做什么

1. 保留原稿的事实和贡献边界，将问题句前置，减少连续抽象名词。
2. 对探索方法明确：改变任务、生成轨迹、筛候选、解码、奖励训练中的哪一处；下一轮保留的是样本、辅助状态还是主模型参数。
3. 教师比较要同时说明它拥有的信息和学生真正能观察到什么，不写成“错误答案比正确答案更好”。
4. 长期数据实验固定或清楚报告保留和训练暴露；“避免退化”与“产生新增能力”是不同结论。
5. 论文中无需复制网页卡片和全部提案；按段落职责回填最能支撑主问题的证据与对照。
6. 原论文结论仍从原始来源获得。网站与综述互相引用不会构成独立验证。

## 原文来源索引

既有来源：E380（Hirano）、E26（Ding）、M17（Mosaic）、S100（Bayesian Teaching）、S47（SOAR）、M52（RHO-LOSS）、S105（INTERACT）。

本轮新增稳定索引：S760 Self-Instruct；S761 STaR；S762 Voyager；S763 RepExp；S764 ESamp；S765 Let's Verify Step by Step；S766 Nature递归数据退化；S767 COLM累积数据对照；S768 SPIN；S769 Absolute Zero。

本轮做了内容、结构和站点检查；未运行上述论文的原始训练实验，未部署新的Agent自改进算法。
