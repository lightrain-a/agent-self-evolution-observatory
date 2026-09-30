# 实验数据准备：大表迭代与精选绘图

> **2026-09-30 默认流程修订**：默认入口改为 Figures4Papers-first 的6个精选参考，最多2个参考、一个主方案和一个备选。原19种renderer和3×4合成演示保留为显式功能档案，不再作为默认选图任务。完整清洗规则见[figure-curation.md](figure-curation.md)。以下2026-09-26记录中四列、多轮部分描述旧功能与历史决定，不覆盖新的默认检索规则。

核对日期：2026-09-26。开发基线：`c241022046ef791f2ba38fe3efbab8829f1ca211`。

## 阶段边界

论文准备分为两个小阶段：**实验数据准备 → 正文写作**。本次只实现前者，可在实验尚未全部完成时启动。没有修改科学裁决、安排 GPU/API 实验、代替人类导师或生成论文段落。

当前默认流程：结果与版本清点 → 大表骨架 → 逐批验证回填 → 小改大表 → 数据—问题映射 → 精选参考匹配 → 一个主方案与一个备选 → 沿用脚本与局部修订 → 实际尺寸复核 → 写作输入材料包。

## 现有系统核对与增量

原系统已有 `result_analysis.py`（观察/解释/边界）、`figure_claim_graph.py`（图表—证据—论点绑定）、`paper_visual_evidence.py`（视觉计划与完成状态），以及内部科研 skill 路由和实验状态机。

本次补足的是它们之间的产物生成和交互层，而不是再建一批 Agent：

| 新增文件 | 作用 |
|---|---|
| `data_preparation_tables.py` | 表格骨架、来源哈希检查、逐格回填、分组 Avg、未舍入增量、CSV/LaTeX 导出、展示与实验变更识别 |
| `data_preparation_figures.py` | 7 类数据结构、19 种图型、输入条件审计、每行四个不同结构候选 |
| `data_preparation_svg.py` | 独立的标准库 SVG 数值渲染，不复制外部模板，不安装新运行依赖 |
| `experiment_data_preparation.py` | 材料包编译、HTML 比较板、本地反馈导出、版本核对导入、修改队列和选中材料交付 |
| `data_preparation_registry.json` | 显式登记真实论文材料包；空登记不虚构数据 |
| `data_preparation_components.json` | 外部库固定版本、许可证与实际采用边界 |

接入点：

- `internal_research_skills.py` 新增 `evidence-bound-data-preparation`，匹配 `experiment-data-preparation / table-preparation / figure-candidate-selection`；不取代正文写作 skill。
- `paper_visual_evidence.py` 输出新增只读 `data_preparation` 视图；不改变原科学通过/失败状态。
- 静态构建和周期刷新读取显式登记的材料包，只更新摘要，不自动渲染私有结果。
- 页面：`experiment-data-preparation.html`；从实验页和 Idea 方法形成页可进入。

## 一、大表的处理细节

先给完整 TableSpec，明确行列、分组、指标、单位、增量参考和 Avg 成员；每格由稳定 method/column ID 绑定结果，不能靠屏幕位置抄数。

结果输入是**显式规范化 JSON**，绑定文件 SHA256 与 JSON pointer；各实验原有 CSV/日志适配器可以先生成这一结构。本次没有声称实现对任意 CSV、日志或论文 PDF 的自动语义解析。

仅 `COMPLETE` 且模型条件、dataset、protocol、split、cohort、metric、unit、analysis_unit 匹配的结果进入数值单元格。`PARTIAL / RUNNING / INVALID / PENDING` 不变成零；真实零保留。分子分母重新计算百分比，增量从未舍入值计算。`NOT_APPLICABLE` 要有原因。

分组均值要求预定成员全部齐全，不对不同方法各自已完成的不同子集求“最终 Avg”。macro 等权、micro 按分母加权；不能混指标/单位。主表结构改变时沿稳定 ID 重排，不重跑实验。

`layout_change()` 区分单纯布局与任务/协议/分母/指标/成员变化；后者要求回实验架构 Change Ledger，不自动授权重跑。新增或删除表也明确记录。表中若需要加粗、下划线或显著性，仍由既有论文格式与统计审查流程处理；本次不凭预览自动宣称显著。

图资产可以提供 `table_bindings`，逐字段核对同一表格单元格的 value 或 delta；不匹配时该图标记 INVALID。没有显式绑定的图不声称已完成跨表语义核验。

## 二、图型与多组候选

旧版演示支持3组×4个；仅作为按需功能测试，不再默认执行。已存在的渲染能力如下：

| 数据结构 | 已实现图型 |
|---|---|
| categorical | 点图、棒棒糖、横向条形、数值条带 |
| paired | 哑铃、斜率、恒等线配对散点、配对差值 |
| samples | ECDF、箱线、直方、样本散点分布 |
| series | 折线、阶梯 |
| xy | 散点、气泡（额外要求真实 size 和单位） |
| matrix | 热力、气泡矩阵 |
| interval | Forest（明确 SD/SE/CI 来源，CI 要有水平） |

配对数据要求明确配对定义和唯一观测 ID；重复 x 的序列先要求明确聚合；缺失矩阵格不画零。没有原始样本就不做分布图，没有区间来源就不画误差条。阶梯拐角不是实测点，不额外画采样标记。条形图从零编码。气泡面积而非半径对应第三量。

历史三组演示在数据足够时形成12个图型；新的默认只比较一个主方案和一个有意义的备选，不保留为了凑四联而出现的空位。可以通过 `preview_rounds` 调整组数；这是渲染预算，不是科学通过门槛。候选图 ID 绑定 data/spec/renderer hash，而不是临时位置。

炫酷主要靠不同图形结构、真实信息层次、紧凑布局和一致颜色语义；不增加虚假 3D、平滑前沿或显著性。每个 SVG 单独生成，再由 HTML 排成四列。选择板不是最终论文版面，最终尺寸仍需人类实际查看。

## 三、交互闭环

| 用户请求 | 系统处理 |
|---|---|
| 先给大表框架 | 输出完整骨架与待补格 |
| 已跑完的先填进去 | 验证来源、逐格填入、刷新均值依赖 |
| 调分组、Avg 位置、标题 | 只改 TableSpec，保留结果身份 |
| 多画几组、类型不同 | 保持同一数据与问题，增加可适配图型，不改数据子集 |
| 保留第二组第三张 | 当前快照位置解析为稳定 Figure ID，记录 KEEP |
| 换图型/图例/间距 | REVISE 队列保留文字反馈，产生新 spec；不自动改实验 |
| 不采用 | REJECT 仅为展示选择，不能否定科学结果或隐藏反例 |
| 数据补齐或更正 | 新哈希使旧确认过期，重新核对，不覆盖旧快照 |

比较板提供 KEEP / REVISE / REJECT 与修改意见。浏览器 localStorage 只是本机草稿，页面明确写“未写服务器”；点击导出得到 JSON。后端导入核对 paper ID、snapshot、candidate/data/spec hash；旧反馈拒绝覆盖新版本。导入幂等，写入有独占锁，不能覆盖另一位操作人的正在写入。

`feedback_summary()` 返回选中项、重画队列、未选项与过期事件。`handoff.json` 核对选中 SVG 文件哈希和表格缺口；输出 `MATERIALS_SELECTED_VISUAL_REVIEW_PENDING`，不是自动视觉通过、科学通过或可投稿。

## 四、外部组件核对

这次核对的是默认分支的实际 HEAD，不将“当前版本”混成“最近都有新发布”。元数据与具体入口记录在 `data_preparation_components.json`。

- [Vivid Figures](https://github.com/yjz211/vivid-figures-skill/tree/c043f0553c7c3188b1bb8dcbf7db76d2adf98375)：参考按数据/目的选图、查看实图的原则。其个人非商业许可证限制改编和再分发；不复制源码、模板或截图。
- [figures4papers](https://github.com/ChenLiu-1996/figures4papers/tree/f0bb7559abe90f5e1828797126d4d133c1bd47d7)：参考论文排版和多面板习惯。读取技能入口；不从 GitHub 的 NOASSERTION 推导复用许可，没有复制代码。
- [Great Tables](https://github.com/posit-dev/great-tables/tree/f870830578dd32ed27624604a8c774c4d2d60f50)：参考分组显示表结构，数值计算与展示分开；没有安装额外表格框架。
- [Python Graph Gallery](https://github.com/holtzy/The-Python-Graph-Gallery/tree/64424bccec3d0340a6dcf7763b37a78e468d45c9)：补充图型索引来源；不是将其全部图库复制进来。

旧的渲染器预览是独立生成的合成示例。当前 `figure-gallery.html` 已作为 `figure-knowledge-base.html` 的兼容入口；默认页只加载精选参考，上游完整文件目录转至 `figure-source-archive.html`，不自动进入Agent上下文。

## 五、运行方式

```bash
# 仅刷新公开清单：不触发模型、实验或私有数据渲染
python3 -m research_pipeline.experiment_data_preparation

# 用显式的规范化结果 manifest 生成一个私有材料包
python3 -m research_pipeline.experiment_data_preparation \
  --manifest /PATH/TO/preparation-manifest.json \
  --evidence-root /PATH/TO/evidence \
  --output /PATH/TO/preparation-output

# 后续改表：记录与上版的结构/协议差异
python3 -m research_pipeline.experiment_data_preparation \
  --manifest /PATH/TO/new-manifest.json \
  --previous-manifest /PATH/TO/old-manifest.json \
  --evidence-root /PATH/TO/evidence --output /PATH/TO/preparation-output

# 导入用户从 HTML 导出的反馈，生成选择材料清单
python3 -m research_pipeline.experiment_data_preparation \
  --manifest /PATH/TO/preparation-manifest.json \
  --evidence-root /PATH/TO/evidence --output /PATH/TO/preparation-output \
  --feedback /PATH/TO/figure-feedback.json --ledger /PATH/TO/operator-selections.json

# 无模型调用的 3×4 合成演示
python3 scripts/build_data_preparation_demo.py
```

输出：表格 CSV/LaTeX、每个候选 SVG、HTML 比较板、input-manifest、preparation/provenance JSON；导入反馈后增加 handoff JSON。原始输入数据和字体文件不会自动打包或公开；provenance 明确写明复现仍需原 evidence root。没有声称生成 PDF/PNG：这两类格式继续交给原有正式出图/排版导出流程。

## 六、实际接入的验证与剩余边界

测试覆盖来源哈希、路径边界、缺失与真实零、增量、macro/micro、协议错配、完整覆盖均值、重排、配对与区间要求、19 种 SVG、12 个不同候选、XSS 转义、选择过期/幂等/独占写、表图字段绑定以及渲染产物漂移。

新模块是确定性的数据呈现层，不代替统计设计、原始证据语义审查、图型科学意义判断或最终论文尺寸视觉验收。实际科研数据的自动适配仍使用各项目原有日志适配器并显式登记；目前真实材料包登记为空，不能把合成演示说成真实论文已迁移完成。
