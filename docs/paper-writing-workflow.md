# 从图表到逐章成稿：HEIRS 写作经验的系统接入

更新：2026-09-27。此页描述已经实现的写作执行层，不发布私有 HEIRS 正文、原始实验或完整聊天。

## 一、不是“一次生成全文，再不断润色”

这轮复盘核对了 HEIRS 的实际版本历史和既有写作笔记。最重要的经验是：先解决研究主线与章节职责，再做局部表达，最后检查真实PDF版式。三类问题不能混成同一个“Improve the paper”。

HEIRS 的改稿路径可概括为：

1. 先建立值得继续改的完整初稿，实验未完时保留框架而不虚报结果。
2. 从实验日志转为问题驱动的论证，参考论文只借架构、节奏和信息分工。
3. 分清方法针对的现象与方法自身产生的效果，先具体解释再形式化。
4. 重排背景、现象与方法；每节、图表和段落有独立的读者问题。
5. 主实验直接回答效果；后续分析解释损失、边界和成本，不平铺运行日志。
6. 逐章诊断、改写与核对，摘要/结论随当前正文和证据回写。
7. 正文附录对账，统一术语、模型方向、分母和比较阶段，去掉无职责的重复。
8. 语言、图例、表注、孤行与引用链接最后处理，不靠改官方边距或字号凑页。
9. GitHub/Overleaf/并发填表以当前快照为准，不能恢复旧结果来通过过期检查。

详细的用户沟通轨迹和对应私有仓库版本保存在 Obsidian：`HEIRS论文写作复盘 - 沟通轨迹与逐章改稿方法`。

## 二、当前系统已有组件与本次增量

保留原 `paper_development_guidance`、`iclr_agent_paper_template`、`figure_claim_graph`、`manuscript_integrity_audit`、`paper_acceptance`，不另造科学裁决或自动导师。

新增：

| 文件 | 可执行功能 |
|---|---|
| `paper_writing_contracts.py` | 10阶段写作流程、9种语义章节职责、7种修改模式、反馈分流 |
| `paper_writing_sources.py` | 活跃LaTeX include清单、精确文件版本、按角色的参考材料、图表交接与原始数据核对 |
| `paper_writing_visuals.py` | 将当前选中实验表/图转换成允许插入的LaTeX片段，不把图库样例当结果 |
| `paper_writing_loop.py` | prepare、单次生成或导入、候选diff、独立审阅包、显式确认后版本安全写回 |

既有 `evidence-first-manuscript` skill 已路由到该执行入口；`paper_development_guidance` 记录新流程与图表入口。没有替换原有实验、科学审核或投稿审核规则。

## 三、写作输入包

每个任务按**一个语义章节或明确行范围**处理，不以过时章节号猜文件。

输入包括：当前 `main.tex` 与include文件快照；当前目标段；一页主线卡（问题、直觉、方法边界、关键证据、非主张、章节职责）；少量核心参考；当前 claim graph；已确认的图表交接；本次用户意见和允许修改范围。

参考材料必须注明角色：`writing_exemplar`、`scientific_related_work`、`baseline`、`method_source`、`venue_template`、`notation`、`protocol`、`result_analysis`。范文中的结果不能移入本文；不按“资料越多越好”无限扩上下文。

`CURRENT_EVIDENCE` 模式下的实质改写要绑定当前 claim graph；`FRAMEWORK` 模式允许未完实验框架，但不允许将计划写成已完成结果。来源存在性/哈希核对不是语义真值认证。

## 四、图表接入不是只给一张缩略图

上阶段的 `preparation.json` 和 `handoff.json` 同时绑定，核对 paper ID、snapshot、选中图ID、产物哈希和原始数据。表格带入每格的display/value/delta与来源，分组均值不由写作者重新算。

原始数据路径通过 `evidence_root_relative` 映射到论文工作区；原数据变化、表格更新或图像重导出会使旧任务失效，阻止旧候选覆盖新结果。

`visual_placements` 可指定选中图表、LaTeX label、图注事实和布局。表格使用已经核对的数值体；图片必须已经通过原绘图导出流程得到PDF/PNG等可用产物。只有SVG时明确返回“需要LaTeX导出”，不谎称graphicx可以直接包含SVG。

图库中的2081条记录只作为设计选择，不能充当论文结果。正式选择后需要用本项目真实数据完成上阶段的绘制与交接。写作阶段不重画、重算或编数字。

## 五、修改模式与交互

| 模式 | 用途 | 默认产物 |
|---|---|---|
| OUTLINE | 主线不清、章节职责和合并方案 | 结构诊断与计划，不写回 |
| DRAFT | 当前章节的首次成稿 | 该章节候选LaTeX |
| REWRITE | 有明确诊断后的章节重写 | 候选与diff，保护图表/引用身份 |
| LOCAL_POLISH | 小幅表达、语法、措辞 | 保留数字、引用、章节、公式和图表块 |
| APPENDIX_ALIGN | 正文附录的定义、协议、证据冲突 | 冲突与定向修订清单，不自动删证据 |
| SUMMARY_SYNC | 将摘要或结论对齐已稳定正文 | 摘要/结论候选 |
| LAYOUT_QA | 孤行、空白、图例、表注等 | 待实际PDF核对的建议，不伪造视觉通过 |

“结构问题”不会自动变成全文重写；“补实验”只是证据请求，不授权实验。章节合并/迁移先走OUTLINE，再对当前文件显式修订，当前apply接口一次只写一个目标文件/行范围。

## 六、命令与API

```bash
# 读取真实当前稿，完全不修改
python3 -m research_pipeline.paper_writing_loop inventory \
  --root PAPER_ROOT --main main.tex --output PRIVATE_WORK/inventory.json

# 从明确任务和来源建立模型输入；此步无模型调用
python3 -m research_pipeline.paper_writing_loop prepare \
  --root PAPER_ROOT --manifest task.json --output PRIVATE_WORK/job

# 使用已有网页/工具模型返回的JSON（不伪造为API调用）
python3 -m research_pipeline.paper_writing_loop candidate \
  --job PRIVATE_WORK/job/job.json --response response.json --output PRIVATE_WORK/candidates

# 或显式调用既有模型接入；模型名必须明确，最多一次POST，不自动重试
python3 -m research_pipeline.paper_writing_loop candidate \
  --job PRIVATE_WORK/job/job.json --generate --model CONFIGURED_MODEL \
  --max-output-tokens 4096 --output PRIVATE_WORK/candidates

# 给独立审阅者准备精确版本；输出不代表审阅已执行
python3 -m research_pipeline.paper_writing_loop review-packet \
  --job PRIVATE_WORK/job/job.json --candidate CANDIDATE/candidate.json \
  --output PRIVATE_WORK/independent-review.json

# 根据实际审阅决定写回；不自动commit/push、不编译、不授权新实验
python3 -m research_pipeline.paper_writing_loop apply \
  --root PAPER_ROOT --job PRIVATE_WORK/job/job.json \
  --candidate CANDIDATE/candidate.json --decision decision.json \
  --receipts PRIVATE_WORK/apply-receipts
```

最小 `task.json` 结构：

```json
{
  "paper_id": "YOUR-PAPER",
  "main": "main.tex",
  "section_id": "introduction",
  "section_role": "introduction",
  "mode": "LOCAL_POLISH",
  "evidence_mode": "CURRENT_EVIDENCE",
  "user_instruction": "只小幅修改表达，保持结论范围、数字和引用。",
  "target": {"path": "sec/01_introduction.tex", "sha256": "EXACT_FILE_SHA256"},
  "argument": {"problem": "...", "intuition": "...", "method_boundary": "...", "nonclaims": ["..."]},
  "references": [],
  "protected_refs": [],
  "must_preserve_phrases": []
}
```

实质改写再提供 `claim_graph_ref`。有图表时加 `preparation_ref`、`handoff_ref`、`evidence_root_relative` 和 `visual_placements`。所有ref为相对路径加sha256，必须由当前真实文件计算，示例字符串不是有效哈希。

`decision.json` 绑定候选sha256、`action=ACCEPT`、真实reviewer标识，以及 `read_diff / scope_reviewed / evidence_reviewed`。Reviewer可以是用户，也可以是既有授权范围内的独立编辑/验证角色；不是要求每个局部修订都重新询问用户。写作者不能伪造自己的独立审阅通过。对大型工作区，provider输入超预算时要求缩小材料，不自动截断核心证据或发超长请求。

## 七、写回与审阅边界

生成只写私有候选目录：job、response、replacement.tex和revision.diff，不改真实稿件。写回时重新检查所有include文件、参考、图表与原数据的hash；并发更新或旧候选哈希不一致时停止并要求重新读取，绝不回滚新数据。

apply有独占锁和写前备份，输出写回回执。结束状态仍是 `APPLIED_PENDING_POST_EDIT_CHECKS`：独立事实/逻辑/claim-evidence复核、完整LaTeX编译、实际PDF检查以及Git提交分别执行。

这些检查不自动证明自然语言语义等价或科学真值。它们能发现错版本、改数字/引用、保护对象被移除等确定性问题；因果语言、量词、必要/充分关系仍需要独立阅读。

## 八、本次实际做了什么，没有做什么

已实现并测试当前源读取、角色化上下文、图表交接、单章节生成接口、导入候选、diff、独立审阅包及安全写回。接入既有provider是可运行代码，但本轮没有擅自开启付费生成，也没有重写HEIRS终稿或更改原论文科学结果。

实际HEIRS最新Git版本已回查，详细交流轨迹保存在Obsidian。本次来源清点是只读，私有稿件与源聊天不会因网站构建被公开。公共页面只展示方法与执行入口。

本轮验证：36项新写作测试，连同既有图表知识库、数据准备、稿件完整性和论文接收等相关回归，共195项通过；新页面行为检查及完整静态站点构建通过。对HEIRS当前Git版本进行了只读源码清点：14个活动源文件，无缺失include，未改原工作区。以上不是实际PDF视觉审查或生成论文质量评估。

原先参考的Orchestra ML-paper-writing和K-Dense scientific-writing属于写作/证据组织知识，不是科学证据。本轮不安装其完整自动科研套件，不导入其他领域的写作模板覆盖已有风格。复用的是现有研究系统与HEIRS的实际编辑经验。
