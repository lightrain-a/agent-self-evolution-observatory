# 完整科研图表知识库

## 本次修正

以前的 19 项是本系统的轻量本地渲染器，不是参考仓库的完整图集。本次把两个概念彻底分开：**参考知识库先决定想用什么图；本地渲染器或外部适配器再决定怎样实现。** 不再以已写好的 19 种代码限制选图。

入口：`figure-knowledge-base.html`。实验数据准备页已加上入口；原 19 种页面明确改称“本地渲染器示例”。

## 1. 可复核的完整范围

本次读取四个官方仓库的完整 Git tree，均 `truncated=false`；版本固定，逐个图像/PDF 路径对应知识条目。完整性是**指定提交内公开文件范围**的完整性，不是声称已经收录互联网上所有科研绘图库。

| 来源 | 条目 | 图例/配方候选 | 教程 | 配套条目 | 视觉文件 |
|---|---:|---:|---:|---:|---:|
| Vivid Figures | 191 | 146 | 0 | 45 | 355 |
| figures4papers | 45 | 39 | 6 | 0 | 42 |
| Python Graph Gallery | 1649 | 975 | 347 | 327 | 1303 |
| Great Tables | 196 | 32 | 51 | 113 | 145 |
| **合计** | **2081** | **1192** | **404** | **485** | **1845** |

统计口径：

- Vivid 的146张卡包含143个配方和3套组合模板；对应148张原始预览，另有148张缩略图。缩略图挂到同一条目，不算新图型。
- figures4papers 的39个图例中有3个额外 PDF 导出，故是42个视觉文件而非42种图。
- Python Graph Gallery 收录每个已发布图像变体、动画、表格示例和347个主 notebook；图标、分区示意等单列配套。临时 notebook checkpoint 不作独立教程。
- Great Tables 同时有示例、教程、文档镜像与图标；相同文件的副本标记出来，不能当成新的设计。
- **2081是索引条目数，1845是视觉文件路径数，1192是图例/配方候选记录数，都不是独立图型数。** 90个图型/用途标签是独立整理的检索分类，有交叉，不是论文结论。
- 91个条目没有可显示的上游图片预览，仍显示原始教程/文件入口，不用合成图替代。

机器审计：`generated/figure-knowledge-coverage.json` 含逐仓库计数和 `path_to_entry`；1845/1845均有归属。

## 2. 不是把图片堆成一面墙

知识库分两层：

**图型层**：中文名称、英语别名、用途、数据结构、必需输入、解释风险、本地渲染器是否适用。包含雨云、山脊、蜂群、排名变化、流向/弦图、SHAP组合、极坐标、三维场、相关性矩阵、事件研究、区间与多面板等。

**具体图例层**：保留仓库路径、源条目、作者、固定commit、图片原始哈希、原图/缩略图/PDF、相关脚本候选、许可、分类状态和收藏身份。

名称和第一轮分类主要来自上游文件名与可确认的目录关系，**不声称已人工审阅2081个条目或验证每个示例代码**。不明确的条目标为“待核对原图”；输入要求是自有的图型级指南，不冒充上游脚本实际 schema。前端详情中明确说明。

## 3. 浏览与选择

桌面四列，默认显示48项以避免一次加载大量远程图像。可以继续加载，也可以“展开全部结果”；搜索遍历完整目录，而非仅搜索已显示的48项。

支持仓库、图型/用途、数据结构、条目类型、有无预览、收藏筛选。点击图例显示该条目全部原始预览和源文件，不仅第一张。

收藏保存到本机浏览器。导出的 `figure-selection-brief.json` 包含稳定entry ID、content version、源commit、预览、数据要求、代码候选、许可和选中版本是否仍有效。不是服务器已批准，也不是自动执行许可。

预览由浏览器读取上游原始链接，**本仓库不重新托管外部图像，不复制模板源码**。图像若被网络环境拦截，会显示失败提示和原站入口；完整目录不会因某次网络失败删除条目。

## 4. 真实接入选图流程

`internal_research_skills.py` 的数据准备流程先查询完整知识库，再考虑本地渲染能力。流程为：

`已有数据/研究问题 → 知识库检索 → 看原图与源文件 → 选择并导出 → 核对数据与许可 → 本地渲染或专门适配 → 四联候选 → 正式论文尺寸检查`。

Python入口：

```bash
python3 -m research_pipeline.figure_knowledge_base --search 雨云 --data-kind samples --limit 20
python3 -m research_pipeline.figure_knowledge_base --search SHAP --limit 20
```

英语关键词按词匹配，避免 `SHAP` 误匹配 `shape`；中文支持子串检索。`search_knowledge()` 可由后续agent直接调用。

数据准备程序支持选图包：

```bash
python3 -m research_pipeline.experiment_data_preparation \
  --manifest /PATH/TO/preparation-manifest.json \
  --evidence-root /PATH/TO/evidence \
  --output /PATH/TO/output \
  --reference-brief /PATH/TO/figure-selection-brief.json
```

后端通过 `validate_reference_selection()` 核对ID、源commit和content version；旧版本需重选。材料包新增 `figure-reference-selection.json`，角色明确为 `DESIGN_REFERENCES_NOT_EXPERIMENTAL_RESULTS`。外部图例数字不会混入本项目结果。

并不是2081个条目全部能直接运行：安装、依赖、许可证、实际输入和图形复现仍需按选定条目确认。

## 5. 文件与更新

- `research_pipeline/figure_knowledge_taxonomy.py`：自有图型选用指南。
- `research_pipeline/figure_knowledge_base.py`：逐文件索引、检索、选图包和版本核对。
- `research_pipeline/figure_knowledge_source_receipts.json`：完整上游文件树快照，仅目录元数据，没有复制上游实现。
- `generated/figure-knowledge-base.json`：可由AI读取的完整索引。
- `generated/figure-knowledge-base.js`：前端索引。
- `generated/figure-knowledge-summary.json`：计数与来源概览。
- `generated/figure-knowledge-coverage.json`：逐文件覆盖关系。
- `docs/figure-knowledge-base-index.md`：图型指南和2081条完整Markdown入口。

```bash
# 使用已保存目录快照重建，无网络、无上游代码执行
python3 scripts/update_figure_knowledge_base.py

# 显式检查当前四仓库 HEAD 后重建；失败/截断时不替换成不完整索引
python3 scripts/update_figure_knowledge_base.py --refresh
```

没有新增定时抓取或自动安装任务。上游内容变化会改变对应content version，旧收藏不能默认为适用于新版本。

## 6. 来源与许可

固定版本：

- [Vivid Figures](https://github.com/yjz211/vivid-figures-skill/tree/c043f0553c7c3188b1bb8dcbf7db76d2adf98375)：限制性个人非商业许可；保留原站参考，不复制/再分发模板实现，后续复用需检查条款。
- [figures4papers](https://github.com/ChenLiu-1996/figures4papers/tree/f0bb7559abe90f5e1828797126d4d133c1bd47d7)：本次读实际LICENSE确认是CC BY-NC 4.0，修正之前仅记录API返回NOASSERTION的不足。
- [Python Graph Gallery](https://github.com/holtzy/The-Python-Graph-Gallery/tree/64424bccec3d0340a6dcf7763b37a78e468d45c9)：仓库层面0BSD，单个图例中的第三方资料仍单独核对。
- [Great Tables](https://github.com/posit-dev/great-tables/tree/f870830578dd32ed27624604a8c774c4d2d60f50)：仓库层面MIT，示例中的第三方内容不据此自动获得相同许可。

来源链接和许可提示不等于授予用户额外权利；本索引不声称获得作者背书。

## 7. 验证边界

测试包括：完整树/仓库/commit核对，148预览及缩略图对应146卡，PDF备用格式，所有视觉路径可追踪，搜索不限19类型，中英查询，SHAP/shape区分，重复文件保留，收藏版本失效，选图包接入，以及前端48项/展开全部/筛选/收藏导出。

这验证目录和软件行为，不等于对全部上游图像做了人工视觉或统计审核；最终选用前仍要查看具体图和源实现。
