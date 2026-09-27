# Skill安全第一轮：攻击面调研知识库

调研截止：2026-09-27。本轮是资料与问题发现，不是已验证漏洞集。防御开发留到第二轮。

## 范围与状态

第三方Skill从被发现到产生副作用，哪些具体可信边界会失效，哪些只是已授予能力的正常使用？

公开页面只有来源、攻击面与已知边界；未发表候选及验证细节保留在私有库。不是自动转载payload，也不安装攻击性Skill。

## 攻击面地图

| 环节 | 可信边界 | 问题 | 来源 |
|---|---|---|---|
| 来源与获取 | 发布者/仓库信号 → 安装者信任 | 仿冒、名称混淆、评价伪造、来源/签名不等于行为安全 | P02, P07, P18, D01, P23, P24 |
| 检索与Skill选择 | 非可信描述 → 规划器选择 | 语义伪装、元数据诱导、重复发布影响曝光 | P07, P11, P03, D08 |
| 安装与打包 | 归档/目录 → 宿主文件与依赖 | 资源遗漏、依赖不完整、路径/身份解析变化 | D01, D03, P04, P10, P16, P23, P24 |
| 激活与预处理 | Skill元数据/模板 → 模型推理之前的宿主动作 | 同意范围和求值时间不一致；效果可能早于模型工具轨迹 | D02, D04, P04, P20, P22, D08 |
| 权限与隔离 | 声明/同意 → 实际执行权限 | 预批准被误当白名单、作用域/期限差异、权限委托未保留来源 | D01, D02, D03, D04, P15, P16, P22 |
| 脚本与间接代码执行 | 自然语言/例子/资源 → 执行器副作用 | 文档示例复用、无显式载荷诱导、语言和代码组合、内嵌模型 | P04, P05, P08, P09, P10 |
| 数据泄露与密钥生命周期 | 数据/密钥持有者 → 另一个目的、主体或接收方 | 非任务数据流、凭据继承、日志/提示暴露；跨Skill共享能力需明确实际边界 | P02, P03, D03, D06, D07, A01, A02, P22 |
| 委托与跨工具 | 调用者的身份/任务 → 子Agent、MCP或进程 | 权限衰减遗漏、凭据来源混淆、以可信代理执行另一来源指令 | D05, P15, P16, A02 |
| 持久记忆与演化 | 一次低信任交互 → 未来高信任Skill/记忆 | 成功轨迹污染、后续任务复用、跨版本传播 | P12, P19, P11 |
| 更新与撤销 | 旧批准/禁用决定 → 新闭包及残留载体 | 批准后变化、依赖延迟加载、撤销后重建 | P16, P17, D03 |
| 可用性与资源消耗 | 有限任务预算 → 被Skill引导的额外工作 | 任务仍成功但不必要委托/重试/上下文消耗 | P13, P11 |
| 审计与标签 | 执行事实与授权上下文 → 扫描器/轨迹分类结论 | 漏掉激活期效果、来源信息不足、未触发判安全、训练测试同源、正常高权限误报 | P14, P20, P03, P11, T01, P23, P24 |

## 阅读等级与证据边界

ABSTRACT_REVIEWED仅代表看过原论文摘要，不冒充逐段复核。原生文档行为不是漏洞；issue不是维护者确认；作者的扫描率不等于在野利用率。
多数2026工作仍按预印本对待，只有明确核对的venue另记；本轮不比较来自不同数据/分母的ASR或F1大小。

## 文献、官方文档、实现与公告

### D01 · Agent Skills specification
来源：https://agentskills.io/specification
类型：SPECIFICATION；阅读：RELEVANT_SECTIONS_REVIEWED；角色：SOURCE_OR_CONTEXT。
支持：Skill目录含元数据、指令及可选脚本/资源；渐进加载。allowed-tools是实验性预批准字段，支持随实现变化。
不支持：格式兼容不等于统一隔离保证；allowed-tools不能无条件解读为能力上限。

### D02 · Claude Code: Extend Claude with skills
来源：https://code.claude.com/docs/en/skills
类型：RUNTIME_DOC；阅读：RELEVANT_SECTIONS_REVIEWED；角色：SOURCE_OR_CONTEXT。
支持：当前文档区分持续留在上下文的Skill内容与只在调用turn有效的工具预批准；动态上下文可在内容送入模型之前求值。
不支持：不能把文档明确允许的行为称作未披露漏洞；全局deny/ask、版本和安装来源必须一起核对。

### D03 · OpenClaw: Skills
来源：https://docs.openclaw.ai/tools/skills
类型：RUNTIME_DOC；阅读：RELEVANT_SECTIONS_REVIEWED；角色：SOURCE_OR_CONTEXT。
支持：有效Skill先按gating/allowlist确定；env/apiKey按宿主run注入再恢复；宿主注入不自动进入sandbox。支持安装策略和固定revision等控制。
不支持：宿主共享权限不是每个Skill天然隔离；不能把已配置能力的使用直接叫提权。

### D04 · Gemini CLI: Agent Skills
来源：https://geminicli.com/docs/cli/skills/
类型：RUNTIME_DOC；阅读：RELEVANT_SECTIONS_REVIEWED；角色：SOURCE_OR_CONTEXT。
支持：发现、激活、用户同意与资源访问有明确阶段；同意后Skill内容和目录结构进入历史，目录加入可读路径；命名冲突按层级处理。
不支持：授权目录不等于授权任何后续副作用；不能以其他客户端字段的含义推断该宿主。

### D05 · MCP Security Best Practices, 2026-07-28
来源：https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices
类型：SPECIFICATION；阅读：RELEVANT_SECTIONS_REVIEWED；角色：SOURCE_OR_CONTEXT。
支持：MCP侧的授权、混淆代理与令牌边界是Skill调用工具时需要保持的相邻信任边界。
不支持：MCP不是Skill格式，已有MCP漏洞不能只换名称就成为新的Skill论文。

### D06 · OpenClaw skill environment implementation
来源：https://github.com/openclaw/openclaw/blob/6fb2c424e8ad2084bbf6054856f6af544a267745/src/skills/runtime/env-overrides.ts
类型：SOURCE_CODE；阅读：SELECTED_SOURCE_READ；角色：SOURCE_OR_CONTEXT。
支持：读取的固定版本包含危险环境变量过滤、active-key引用计数及子进程过滤接口注释；广义环境继承并非未研究的新问题。
不支持：未在本轮执行该实现，未验证全部调用路径；源码片段不是当前可利用性证据。
固定代码版本：`6fb2c424e8ad2084bbf6054856f6af544a267745`；内容SHA256：`d2afe96761c17e87dd546554029e0c18c5565c8b5ce3618f3a6bb6b4260e8f48`。

### D07 · OpenClaw SECURITY.md: operator and execution trust boundaries
来源：https://github.com/openclaw/openclaw/blob/6fb2c424e8ad2084bbf6054856f6af544a267745/SECURITY.md
类型：THREAT_MODEL；阅读：SELECTED_SOURCE_READ；角色：SOURCE_OR_CONTEXT。
支持：固定版本明确区分可信operator/本地代码、非隔离的共享会话和真正auth/policy/sandbox边界；prompt-only或可信插件已有权限内行为不自动算漏洞。
不支持：维护者报告范围不等于所有部署风险不存在；论文测量部署假设失配时要如实命名，不能伪报权限绕过。
固定代码版本：`6fb2c424e8ad2084bbf6054856f6af544a267745`；内容SHA256：`12dfbe925573cb1da636b54d7ef01c3f4fe4acf1643ef1700ffa84acbaf8e2b2`。

### A01 · Skill env override host env injection — GHSA-82g8-464f-2mv7
来源：https://github.com/openclaw/openclaw/security/advisories/GHSA-82g8-464f-2mv7
类型：MAINTAINER_ADVISORY；阅读：RELEVANT_SECTIONS_REVIEWED；角色：SOURCE_OR_CONTEXT。
支持：历史公告：本地配置env覆盖未应用宿主安全策略；需要修改本地可信配置；公告给出受影响和已修复版本。
不支持：不是任意第三方Skill零权限攻击；不是本轮新漏洞；不应默认在最新版本仍然存在。

### A02 · OpenClaw issue #36280: Skill API key inherited by ACP child process
来源：https://github.com/openclaw/openclaw/issues/36280
类型：ISSUE_REPORT；阅读：ISSUE_AND_LINKED_SOURCE_REVIEWED；角色：SOURCE_OR_CONTEXT。
支持：公开issue记录Skill密钥被子进程继承导致认证/计费来源变化；当前env模块注释明确引用该issue并提供移除key的接口。
不支持：issue不是已确认安全公告；未追完所有修复调用链；不能把相同现象当原创发现。

### P01 · Agent Skills in the Wild: An Empirical Study of Security Vulnerabilities at Scale
来源：https://arxiv.org/abs/2601.10338v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：大规模SkillScan静态/语义审计形成注入、泄露、提权和供应链分类。
不支持：扫描标记比例不是动态确认的在野利用率；作者统计未由我们复现。
作者报告（未复现）：`{"collected": 42447, "analyzed": 31132, "flagged_percent": 26.1, "interpretation": "scanner-derived flags, not independently reproduced exploit prevalence"}`

### P02 · Do Not Mention This to the User: Detecting and Understanding Malicious Agent Skills in the Wild
来源：https://arxiv.org/abs/2602.06547v4
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：在野恶意Skill测量及动态确认，是区分风险特征与恶意行为的直接最近邻。
不支持：样本和确认规则决定统计范围，不能和另一篇扫描率直接相减；不是当前registry全体的普查。
出版状态核对：USENIX Security 2026 (arXiv comments)
作者报告（未复现）：`{"audited": 98380, "dynamically_confirmed_malicious": 157, "interpretation": "author-reported"}`

### P03 · Skill-Inject: Measuring Agent Vulnerability to Skill File Attacks
来源：https://arxiv.org/abs/2602.20156v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：202个注入—任务配对，包括显式和上下文依赖指令，同时评价安全与正常任务效用。
不支持：再造一批恶意SKILL.md或泛称情境重要，不足以构成新问题。
作者报告（未复现）：`{"injection_task_pairs": 202, "interpretation": "benchmark cardinality, not our executions"}`

### P04 · Supply-Chain Poisoning Attacks Against LLM Coding Agent Skill Ecosystems
来源：https://arxiv.org/abs/2604.03081v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：DDIPE研究文档示例/配置被编码Agent复用后形成执行危害。
不支持：文档到代码的污染与模板内隐载荷已被研究；论文报告的漏洞不能当本轮发现。

### P05 · BadSkill: Backdoor Attacks on Agent Skills via Model-in-Skill Poisoning
来源：https://arxiv.org/abs/2604.09378v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：Skill携带的学习模型可以成为隐蔽后门载体，实验使用OpenClaw-inspired受控环境。
不支持：不是原生OpenClaw所有版本的漏洞证明；内嵌分类器后门不是空白方向。

### P06 · HarmfulSkillBench: How Do Harmful Skills Weaponize Your Agents?
来源：https://arxiv.org/abs/2604.15415v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：区分有害能力及其被用户使用的风险，提供200个harmful skills的评测材料。
不支持：harmful capability不等于第三方劫持良性用户任务；仅有害样本集不能计算benign FPR。

### P07 · Under the Hood of SKILL.md: Semantic Supply-chain Attacks on AI Agent Skill Registry
来源：https://arxiv.org/abs/2605.11418v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：Skill描述/语义元数据影响检索选择及registry治理。
不支持：描述优化、语义伪装、抢占选择率不宜作为新的独立主题。

### P08 · Exploiting LLM Agent Supply Chains via Payload-less Skills
来源：https://arxiv.org/abs/2605.14460v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：研究不含直接恶意代码而借任务合规理由诱导Agent生成偏离行为。
不支持：没有显式payload不意味着该路径没人研究；需要额外的宿主边界差异。

### P09 · SkillMutator: Benchmarking and Defending Language-and-Code Cross-modal Attacks on LLM Agent Skills
来源：https://arxiv.org/abs/2606.14154v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：语言与代码联合决定风险，含扫描反馈驱动变体的测试。
不支持：跨模态拼接、普通扫描器规避不再当作新颖性；本轮不实现规避攻击器。

### P10 · PhantomSkill: Malicious Code Injection in Agent Skill Ecosystems
来源：https://arxiv.org/abs/2606.19191v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：辅助脚本/资源中的代码注入与伪装成实现缺陷的路径。
不支持：只扫描SKILL.md而遗漏资源不是新的核心发现；需具体未覆盖机制。

### P11 · Agent Skill Security: Threat Models, Attacks, Defenses, and Evaluation (SkillSec-Eval)
来源：https://arxiv.org/abs/2607.13987v1
类型：PAPER；阅读：THREAT_MODEL_METHOD_LIMITATIONS_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：327个真实Skill构成受控生命周期评测，覆盖准入、检索、规划、组合、执行和演化。
不支持：完整生命周期分类已存在；受控框架结果不证明原生产品同样可利用；长期历史与跨宿主语义尚需单独验证。

### P12 · When Experience Becomes Instruction: Trajectory Poisoning in Self-Evolving Agent Skill Systems
来源：https://arxiv.org/abs/2608.05563v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：PoisonedEvolution研究受污染成功轨迹被写成持久Skill；用可控指令/无害标记刻画继承。
不支持：指令进入Skill不等于发生真实执行危害；普通轨迹投毒已碰撞。

### P13 · Convergent Detour Hijacking: Task-Preserving Resource Amplification in Skill-Based LLM Agents
来源：https://arxiv.org/abs/2608.12273v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：在完成原任务同时增加不必要流程和资源消耗的Skill攻击。
不支持：正常任务仍成功但成本增加，已有专门工作；不能重新命名为新漏洞。

### P14 · MaliciousSkillBench: A Comprehensive Benchmark for Malicious Agent Skill Detection
来源：https://arxiv.org/abs/2608.19901v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：跨13来源整理，核心集9740个Skill；强调结构/来源不相交评测与正常样本误报。
不支持：随机切分好成绩不表示跨来源有效；来源分布偏移的检测基准已被研究。
作者报告（未复现）：`{"skills": 9740, "malicious": 7505, "benign": 2235, "interpretation": "author-reported normalized primary benchmark"}`

### P15 · SkillGuard: A Permission-Centric Framework for Agent Skill Security
来源：https://arxiv.org/abs/2606.03024v2
类型：PAPER；阅读：METHOD_SECTIONS_REVIEWED；角色：DEFENSE_NEAREST_NEIGHBOR。
支持：权限中心的静态与运行时治理，涉及最小权限和委托；是权限类题目的强最近邻。
不支持：本轮不再提出泛化permission manifest或通用reference monitor作为攻击论文创新。

### P16 · Versioned Transitive Dependency-Closure Binding and Operation-Time Effect Governance for Agent Skills: ClosureBound
来源：https://arxiv.org/abs/2609.05920v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：DEFENSE_NEAREST_NEIGHBOR。
支持：对递归/延迟依赖闭包、版本、用途、权限及效果路径绑定；声明一组假设下的性质与无provider内核验证。
不支持：依赖TOCTOU与授权沿旧版本转移已被明确提出；其证明不等同完整原生生态部署验证。

### P17 · OBLIVION: Workflow-Level Operational Skill Unlearning for Deployed Agents
来源：https://arxiv.org/abs/2608.08264v1
类型：PAPER；阅读：PRIMARY_ABSTRACT_SEARCH_REVIEWED；角色：ATTACK_AND_DEFENSE_NEAREST_NEIGHBOR。
支持：删除registry条目后从档案、会话或memory重建被撤销Skill的工作流；含受控基准与缓解。
不支持：卸载后复活不是新发现；不能仅换一个残留载体重复该问题。

### P18 · After the Party: Growth, Governance, and Security Scanning in the OpenClaw Agent Skill Ecosystem
来源：https://arxiv.org/abs/2609.17274v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：对当前Skill生态的增长、治理与扫描能力开展测量；是近期生态审计碰撞项。
不支持：再爬一次ClawHub加普通扫描统计不自动形成独立研究；需额外识别对象。

### P19 · Safety in Self-Evolving LLM Agent Systems: Threats, Amplification, and Case Studies
来源：https://arxiv.org/abs/2606.23075v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：跨模块生命周期分析持久化和放大风险，比较自进化系统案例。
不支持：普通安全债务或污染跨代传播并非未研究；个案不能推广所有Agent。

### P20 · SkillSentry: Adaptive Honey Worlds for Dynamic Safety Testing of Agent Skills
来源：https://arxiv.org/abs/2608.03485v1
类型：PAPER；阅读：METHOD_AND_EVALUATION_SECTIONS_REVIEWED；角色：DEFENSE_AND_EVALUATION_NEAREST_NEIGHBOR。
支持：LLM模拟honey worlds中有/无Skill配对、实际效果验证和双重用途复核，而非只凭可疑文本下结论。
不支持：动态诱发、无害标记、因果差分与context-aware安全判断已有方法；原生宿主遥测覆盖不能由模拟器假定。

### P21 · AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents
来源：https://arxiv.org/abs/2406.13352v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ADJACENT_BENCHMARK。
支持：状态化任务、非可信工具输出与安全/效用分开评价的可复用环境。
不支持：它不是原生Skill安装器、权限和生命周期的完整复现。
出版状态核对：NeurIPS 2024 Datasets and Benchmarks (official repository citation)

### T01 · Cisco AI Defense skill-scanner
来源：https://github.com/cisco-ai-defense/skill-scanner
类型：TOOL；阅读：README_REVIEWED；角色：BASELINE_CANDIDATE。
支持：可作为已有静态/语义/数据流扫描基线；支持不同分析配置和可集成输出。
不支持：本轮仅查看，未安装、未扫描恶意包、未得到复现分数。

### T02 · SKILL-INJECT implementation
来源：https://github.com/aisa-group/skill-inject
类型：BENCHMARK_REPO；阅读：README_REVIEWED；角色：SOURCE_OR_CONTEXT。
支持：官方公开实现可用于有来源的攻击—良性任务匹配与既有基线比较。
不支持：数据中有危险样本，不能把仓库直接加载为本机Skill；先只读隔离审计。

### T03 · AgentDojo implementation
来源：https://github.com/ethz-spylab/agentdojo
类型：BENCHMARK_REPO；阅读：README_REVIEWED；角色：SOURCE_OR_CONTEXT。
支持：官方任务环境可复用安全与正常任务效用的分离评分接口。
不支持：尚未审查依赖与许可证适配；不宣称已运行或可替代原生宿主。

### T04 · MaliciousSkillBench project page
来源：https://protectskills.github.io/MaliciousSkillBench/
类型：BENCHMARK_PROJECT；阅读：PROJECT_PAGE_REVIEWED；角色：SOURCE_OR_CONTEXT。
支持：可追溯整合数据及来源/结构分组切分的官方入口。
不支持：本轮没下载或执行载荷；访问页面不等于所有数据许可证和样本完整性通过。

### I01 · Cisco: Personal AI Agents like OpenClaw Are a Security Nightmare
来源：https://blogs.cisco.com/ai/personal-ai-agents-like-openclaw-are-a-security-nightmare
类型：RESEARCHER_REPORT；阅读：SEARCH_AND_ARTICLE_SECTIONS_REVIEWED；角色：SOURCE_OR_CONTEXT。
支持：研究者报告说明流行度和Skill供应链风险不能等同可信度，提供现实生态动机。
不支持：单个研究者案例不是完整生态恶意比例；优先以原生版本和维护者边界确认实际影响。

### D08 · OpenAI: Build skills — Codex invocation and loading
来源：https://learn.chatgpt.com/docs/build-skills
类型：RUNTIME_DOC；阅读：RELEVANT_SECTIONS_REVIEWED；角色：SOURCE_OR_CONTEXT。
支持：官方页面描述显式/隐式调用、仓库/用户/管理/系统加载位置、同名Skill不合并，以及agents/openai.yaml中的调用策略和工具依赖。
不支持：调用策略和依赖声明不是逐Skill权限沙箱保证；本轮没有检查Codex所有平台实现。

### P22 · Agent Skills Enable a New Class of Realistic and Trivially Simple Prompt Injections
来源：https://arxiv.org/abs/2510.26328v1
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：早期直接研究Skill指令/脚本中的注入和任务批准被延伸到相邻有害动作；必须作为基础最近邻。
不支持：泛称恶意SKILL.md、长文藏指令或一次批准后复用，并非2026年的全新问题。

### P23 · Context Matters: Repository-Aware Security Analysis of the Agent Skill Ecosystem
来源：https://arxiv.org/abs/2603.16572v2
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：ATTACK_OR_MEASUREMENT。
支持：加入所属仓库上下文后重新判断可疑Skill，区分误报并研究废弃仓库劫持；版本v2标题与v1不同。
不支持：“检测要加上下文”、泛化供应链劫持或重新计算扫描率都已有工作；remaining suspicious不是confirmed malicious。
出版状态核对：AgentSkills 2026 workshop at CAIS, Best Paper Award (author arXiv comments; not a main-track security-conference acceptance)

### P24 · GitSkills: A Dataset of Agent Skills on GitHub
来源：https://arxiv.org/abs/2608.10906v3
类型：PAPER；阅读：ABSTRACT_REVIEWED；角色：CORPUS_CANDIDATE。
支持：以仓库、路径、内容hash和部分历史组织大规模Skill语料，可做去重和来源/版本分组取样的参考。
不支持：数据体量不是安全标签；本轮未下载SQLite、未验证所有样本许可、不得自动执行其中代码。
出版状态核对：MSR 2027 to appear per author arXiv comments; not yet treated as a published proceedings record

## 原生源码/文档检查改变了什么

- N01 [D01, D02, D04] 同一SKILL.md规范并未定义统一的权限沙箱；不同宿主的激活、同意和权限生效方式明确不同。 状态：DOCUMENTED_SEMANTIC_DIFFERENCE。
- N02 [D02] 技能内容与授权有不同生命周期，且动态上下文求值早于把内容发给模型。 状态：DOCUMENTED_STAGE_DIFFERENCE。
- N03 [D03, D06, D07, A02] 密钥按宿主run注入是已说明的行为；源码已有引用计数和子进程过滤相关接口，不能再以无条件继承作为新颖性。 状态：CANDIDATE_DOWNGRADED_BY_SOURCE。
- N04 [A01] 危险宿主环境变量注入为已修复历史公告，且攻击前提包含本地配置写权限。 状态：KNOWN_FIXED_ADVISORY。

## 评测规则

- 先记录N_total_user_tasks，再记录候选可见、Skill激活、到达效果、实际越界；条件成功率和端到端成功率均可报告，不混分母。
- malicious intent、harmful capability、可疑静态模式、允许但敏感动作、完成的未授权效果是不同标签。
- 正常任务效用、benign FPR、未触发/超时比例与安全指标并列；不能只报告攻击成功的子集。
- 使用相同任务、初态、模型和预算作配对；源/结构家族跨训练测试留出；多seed不能替代来源留出。
- 事件真值来自受控资源变化和策略记录，不由攻击生成器自评，也不只依赖被测Agent的叙述。
- 迁移测量固定Skill字节和声明条件；不同平台的承诺范围分开，不能预设不存在的逐Skill隔离。
- 同一根因下的多个方向/载体优先合并成一篇充分的研究，不为论文数量拆碎。

## 本轮局限

这是按Skill生命周期和最近邻扩展的第一轮范围调研，不宣称系统性综述已达到文献穷尽。少数工作仅摘要筛查、部分实现尚未核验发布包；这些不能被记成全文或代码复现。
没有运行未知Skill、真实外传、公共目标探测、GPU训练或付费provider。当前仍为0条本轮复现漏洞；真实候选须经过原生支持资格、最小无害反例和来源查重。
原生文档会变；源码仅对记录的commit成立，下一轮实验必须再次冻结实际版本。
