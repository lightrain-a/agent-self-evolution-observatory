# HEIRS 经验：Idea 发现与方法形成

核对日期：2026-09-26。开发基线：主分支 `0764bdc8dc16876c13a9c76378f48661fc6c2ba3`。

## 目标与边界

把“已有系统与文献 → 异常 → 结构类比 → 竞争假设 → 最低成本区分实验 → 限定范围的证据判断 → 最小方法 → 前瞻验证 → 主张与证据闭合”接到现有系统。

朱老师这类导师的经验、问题价值和方向判断保留为外部人类咨询，不建立导师模拟 Agent。聊天回顾只提炼工作方法；未回查的 HEIRS 日期、候选编号、成功率、相关系数和停止阈值不进入科学证据库。

## 现有系统已有的能力

| 能力 | 实际代码 | 本次处理 |
|---|---|---|
| 原始证据、异常、四类发现通道 | `paper_first_problem_generator_prompts.py`、`paper_first_problem_discovery_contract.py` | 保留科学门控 |
| 跨域搜索、分支细化、formulation | `paper_first_problem_search_portfolio.py` | 新增结构路线和统一工作卡 |
| 成熟理论碰撞、分层贡献 | `research_reasoning_layer.py` | 保留方法与现象贡献的区别 |
| 限定范围的失败记忆 | `failure_asset_library.py`、`research_memory_wiki.py` 等 | 复用，不另建重复科学台账 |
| pre-F0、P0、预算和执行权限 | 现有状态机与执行组件 | 不改变权限或裁决 |
| 周期刷新、页面 | `automation_cycle.py`、`app.js` | 增加确定性摘要与默认折叠展示 |

真正缺口是：类比往往停留在领域名，没有在同一候选里稳定绑定“结构映射—失效点—竞争预测—实验成本—缺失证据”。不是缺少更多 Agent。

## 最新 GitHub 组件核对

以下为核对日实际获取的默认分支 HEAD，不表示所有项目近期都有新版本。检查范围是官方 README、模块入口说明、GitHub 元数据及必要许可证。**采用工作流模式、自行实现适配层；未复制上游源码、未安装依赖、未启动上游执行器。**

| 项目 | 固定提交 / 提交日 | 采用方式与限制 |
|---|---|---|
| [MOOSE-Chem2](https://github.com/ZonglinY/MOOSE-Chem2/tree/5b289372fe7722df33bfc49c4c329671967f8822) | `5b289372` / 2025-12-03 / MIT | 借鉴从粗假设到可测试细节的分层细化；不启动长时层级搜索，不把模型排名当实验验证 |
| [HypoGeniC / HypoRefine](https://github.com/ChicagoHAI/hypothesis-generation/tree/bd37a3129a2f98ee586f545a57b10b59496eedad) | `bd37a312` / 2025-07-17 / MIT | 借鉴文献与数据分离、并列假设库；不把面向标注文本的准确率机制当通用科学真值 |
| [RD-Agent](https://github.com/microsoft/RD-Agent/tree/484776c211e4fbbeef03e0ec00d6bbee7362a4f4) | `484776c2` / 2026-09-23 / MIT | 复用现有研究/实现分层，在计划中区分技术失败与科学结果；不安装平行框架 |
| [AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2/tree/96bd51617cfdbb494a9fc283af00fe090edfae48) | `96bd5161` / 2025-12-19 / 自定义许可证 | 现有方法树已有相似结构，不重复引入执行器；当前许可证不是普通 MIT，没有复制代码 |

原始 MOOSE-Chem 的“背景与灵感语料分离”已在 `idea_discovery_v3.py` 中作为模式出现，不把这项旧能力重新计算为新增功能。

## 本次工作卡

`method_formation` 包括：

1. **直觉与例子**：普通语言解释，假想例子与已观察事实分开。
2. **观察与系统**：证据引用、范围，以及对象、更新、反馈、选择、部署变化、预算六项。
3. **结构类比**：至多两条；逐项 source→target 映射、源引用、不能迁移的假设、目标域可证伪预测。可明确记录未找到合理类比。
4. **竞争假设**：两至四条，至少一个非偏好替代解释；每条有预测、反证和范围。
5. **P0 计划**：干预、控制、简单基线、观测量、不同预测、数据来源、候选×任务×重复预算、时长及依据、决策/不确定/停止规则、完整性检查。
6. **主张与确认边界**：不声称什么；确认前必须冻结和留出什么。

默认两条假设、一条类比，整卡约 500 词以内。不增加 provider 子调用。未知时间保留 null 并列为待补，不能编造。

预算区分逻辑任务评估与实际模型调用：`逻辑评估 = 候选 × 任务 × 重复`；`预计 provider 调用 = 逻辑评估 × 每次评估调用数 + 重试预留`。多轮 agent 的一次任务评估不等于一次模型调用。离线重放的新增调用预算必须为零。

## 代码接入

新模块 `research_pipeline/discovery_method_formation.py`：

- `formation_shape()` / `formation_prompt()`：legacy generator 与 canonical portfolio formulation 共用。
- `normalize_formation()`：字段白名单。忽略模型提交的 PASS、实测收益、已执行状态和权限。
- `audit_formation()`：检查字段、竞争预测、引用是否在 registry、预算一致性，输出待补项。
- `write_method_formation_state()`：确定性公开摘要，不公开私有卡片正文，无模型调用、无实验启动。

`paper_first_problem_generator._normalize()` 保留卡与审计结果；`automation_cycle._run_discovery_frontier_control()` 刷新摘要。Idea 页面增加中英双语、默认折叠的“​​Idea 发现 → 方法形成”面板。

原有候选缺卡只标记待补，不自动撤销、升级或重开原裁决；没有改科学阈值、预算权限或历史饱和条件。

## 状态语义

`NEEDS_PLAN`、`NEEDS_PLAN_OR_RETRIEVAL`、`PLAN_FIELDS_COMPLETE` 只表示**计划字段完整度**。

字段完整不等于科学有效、创新通过、引用语义已验证、P0 获得权限、前瞻验证已完成。引用检查是 registry presence 检查，来源语义仍由原 grounding 流程独立核验。

生成假设统一为 `PROPOSED`，计划为 `NOT_EXECUTED`，科学状态为 `NOT_EVALUATED`。真实结果继续由既有实验记录、失败记忆与科学裁决处理，不由模型写入本卡。

弱相关、低功效、不显著不是自动否证；工程失败不是科学原则失败。前瞻验证要冻结协议、代码、配置和数据身份；看过的结果不能重新标为 untouched。

**本次实现的是发现与 P0 计划交接层，不是新建完整自动实验系统。** 结果接收、跨数据前瞻执行、科学判决与论文取数继续走原系统；方法论全流程与已实现范围分开理解。

## 测试

```bash
python3 -m unittest research_pipeline.test_discovery_method_formation -v
python3 -m research_pipeline.discovery_method_formation
node --check discovery-method-formation-view.js
```

第二条只编译现有状态，无模型或 GPU 调用。测试覆盖缺卡、缺引用、伪造权限/结果、类比无失效点、相同预测、重复 ID、预算不足、未知时间、幂等、公开文本脱敏、无效输入保持旧文件，以及两条 prompt 和 normalization 接入。

## 系统效果的下一层验收

代码测试不等于科研产出改善。获得新的合法发现任务和预算后，冻结比较协议，再看加入工作卡前后的结构类比质量、P0 辨识性、引用错误率、无效实验比例、调用成本与人类阅读负担。不要只按候选数或 PASS 数评价。
