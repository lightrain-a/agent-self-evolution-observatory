# RSI 论文精读卡片 · 维护说明

本站长期积累的精读卡片在 `rsi/reading-cards.json`，与 `rsi/sources.tsv` 的广覆盖来源台账分开。一次新增论文只追加 `papers` 数组中的一个 JSON 对象，不要直接手改生成的 `rsi/reading-cards.html`。

## 一篇卡片应该留下什么

- **元信息**：`id`（唯一、稳定）、`arxiv`、`short_title`、`title`、`authors`、`first_posted`、`version`、`read_on`、`reading_level`、`links`。
- **作者署名单位**：`lead_institution`（卡片上显示的主要单位）、`institutions`（原文列出的全部单位）、`institution_source`（PDF 中核对位置）、`publication`（技术报告、预印本或正式发表状态）；不要把作者单位混写成录用会议。
- **五问框架（全库统一）**：根节点 `research_questions` 固定五个问题：信号对不对、有没有新东西、采不采得到、吸收了会不会丢、安全。每篇的 `research_coverage` 必须恰好包含 `signal` / `novelty` / `reach` / `retention` / `safety`，每项写 `level`、`contribution`（论文到底做了什么）和 `open_question`（留下了什么）。
- **分类边界**：`level` 仅取 `core`（重点研究）、`partial`（部分涉及）、`not_addressed`（未直接研究）。**覆盖不等于已经解决**：在候选集合里排序不代表扩展采样支持集；保留某个版本不等于不会遗忘旧能力；约束声明不代表对抗安全已验证。
- **记忆点**：`one_sentence`（一句话记住主张），`problem`（具体困难），`setup`（最重要的实验与系统设置）。
- **值得复用的机制**：`key_ideas` 数组，每条含 `name`、`summary`、`formula`（纯文本公式，避免直接插 HTML）。
- **证据与边界**：`evidence`、`boundaries`，分别区分论文报告结果、实现假设、未验证的局限。
- **研究转化**：`our_relevance`、`next_test`，写可验证的迁移实验，不能表述成原论文已证明的事情。
- **发现与检索**：`tags` 供归类，站内全局搜索索引和本页筛选由构建流程自动更新。
- **完整精读（可选）**：为深入读过的论文追加 `deep_read`，包括 `focus`、`summary` 和 `sections`。章节具有稳定 `id`、`title` 与 `blocks`；目前通用块类型为 `prose`（解释）、`steps`（过程）、`formula`（公式及边界）、`table`、`callout`（论文事实/示例/启发/提案）、`evidence`（实验和不能证明什么）、`bullets`、`tests`（决定性实验）。构建脚本自动生成 `rsi/reading-notes.html`，卡片出现“完整精读”入口，并为各章节建立搜索索引；只追加数据，不复制或手改 HTML。

**精读与原文分离**：完整精读严格区分论文原始结果、为解释公式构造的示例数值、本站的学术判断，以及尚未开展的实验构想。不能把“提出 Pair Gate”写成“已有充分的多轮 Pair Gate 因果消融”，也不能把固定 Coder 的代码修复结果当作 Coder 参数进化证据。

不要写未经核查的成绩或把相近数据集名称擅自扩大。优先固定 arXiv 的版本页面、论文代码链接和阅读日期。

## RSI 研究时间轴与会议 DDL

`rsi/timeline-data.json` 是会议与人工研究里程碑的唯一数据源：

- `venues` 中目前只有 CVPR 2027、ICML 2027、ACL 2027；每个节点保留 `source_url`、`verified_at`（顶层）、`date`、`due_at`、`status`。
- **已发布官方截止**使用 `status=official`、日期 `YYYY-MM-DD`，以及包含 `-12:00` 的准确 AoE 时间戳 `YYYY-MM-DDT23:59:00-12:00`。
- **尚未发布**必须设 `status=pending`、`date=null`、`due_at=null`，不可把往届时间或第三方估算写为正式 DDL。
- `research_events` 仅纳入有证据链接的研究记录；不得把方案、预期结果当成已完成实验。
- 论文阅读事件不需要重复记录：`scripts/rsi_pages/timeline.py` 自动读取 `rsi/reading-cards.json` 的 `read_on` 和一句话结论，并生成可点击记录。
- 设计和交互代码分别在 `rsi/timeline.css`、`rsi/timeline-view.js`，无需从 Agent 主站的复杂时间轴依赖。
- 新增会议时更新 `venues` 与经过核验的日期，执行 `python3 scripts/build_rsi_research.py` 重新生成静态时间轴与全站检索索引。

## 生成与核查

在仓库根目录执行：

```bash
python3 scripts/build_static_site.py      # Agent 站
python3 scripts/build_rsi_research.py      # 生成 RSI 页面与独立导航
python3 scripts/build_rsi_site.py          # RSI 独立站输出到 _site/rsi
python3 scripts/test_rsi_site.py
python3 scripts/test_rsi_browser.py
```

对应源文件是 `scripts/rsi_pages/reading-cards.py`（通用渲染器），`scripts/build_rsi_research.py`（左侧目录、HTML 和本地搜索索引），`rsi/research.js`（浏览器筛选）。只要字段符合当前 JSON schema，后续论文无需再修改这些程序。

RSI 站点使用独立的 `site-nav.js`，不再依赖 Agent 站的 `data.js`。双站架构、入口和单独导出方法参见根目录 `SITES.md`。部署仍使用仓库现有 GitHub Pages workflow：合入 `main` 后先构建 Agent、再构建 RSI；不要把 private 数据或本地路径写入公共卡片。
