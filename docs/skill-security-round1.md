# Skill安全第一轮：知识库与发现通道

截至2026-09-27，按Skill获取、安装、激活、授权、执行、数据、委托、演化、更新撤销和审计建立一手来源库。第一轮是攻击面调研与Idea发现；防御机制开发留到第二轮。

## 本轮产物

- `skill_security_round1_sources.py`：39条一手来源、24篇论文；每条有阅读深度、支持内容、不能推出的结论和版本信息。
- `skill_security_round1_scope.json`：12类攻击面、攻击者控制范围、证据阶梯、评测分母与安全边界。
- `skill_security_round1.py`：来源和私有候选验证；公开投影；将合格的“待原生核对”候选转成既有 `discovery_method_formation` 工作卡。
- `generated/skill-security-round1.json/js`：只含公共文献和已知攻击面，不含未发表候选、private path或攻击载荷。
- `docs/skill-security-round1-survey.md`：全部来源的可读说明。
- `skill-security-research.html`：来源检索、按阶段/类型过滤、原生文档观察和证据阶梯。

私有Idea保存在用户指定的Obsidian知识库与后端私有研究目录。公共GitHub源码、生成状态和页面中不包含具体候选题目或新意设计。

## 范围与检索方法

按三层组织：① Skill直接研究；② 官方标准、宿主实现/安全模型、公告；③ 相关工具/状态化Agent benchmark。按照恶意Skill、供应链、权限、泄露、检索、持久化、撤销、审计与评测来源等问题检索，并从最接近的工作继续查重。

已核对的宿主资料覆盖Agent Skills格式、Claude Code、OpenClaw、Gemini CLI与Codex。并非这些平台的实现全部都已复现；OpenClaw有固定commit下的源码检查，其他原生实现仍需执行前资格审查。

此为第一轮范围调研，不宣称系统综述达到文献穷尽。摘要已读、方法章节已读、源码已读、公告已核对和真正实验复现是不同状态。少数venue来自作者arXiv备注，不能扩称已在安全四大主会正式出版。

## 来源与事实的分层

“静态可疑”“具有危险能力”“与任务目的不一致”“真实效果发生”“真实边界被绕过”“维护者确认漏洞”分开记。

例如预批准字段并非通用权限白名单；可信operator本地配置能力并不等于第三方包已突破安全边界；历史修复公告和公开issue不能当新发现或最新可利用性的证据。维护者的报告范围与学术部署风险范围也不混淆。

作者给出的扫描flag率、动态确认率、ASR/F1及正常效用分母可能不同，不横向组成性能排行榜。本轮0条复现漏洞、0次科研模型调用、0次GPU实验。

## 私有候选接入

候选只有在具备明确最近邻、条件性差异、攻击者能力、相反预测、原生测试方案和停止条件时，才允许导出一个**仍未验证**的工作卡。已有碰撞、已知问题和第二轮防御不能被生成器自动提升为主方法。

```bash
# 无网络、模型、实验启动：重建公开参考界面
python3 -m research_pipeline.skill_security_round1 --public

# PRIVATE_PROGRAM 与输出必须是用户的私有研究目录，不能进入公开仓库
python3 -m research_pipeline.skill_security_round1 \
  --private-program /PRIVATE_PATH/research-program.json \
  --output /PRIVATE_PATH/discovery-packets

# 导出单个被列为待原生资格的候选；ID来自私有manifest
python3 -m research_pipeline.skill_security_round1 \
  --private-program /PRIVATE_PATH/research-program.json \
  --output /PRIVATE_PATH/discovery-packets \
  --candidate CANDIDATE_ID
```

工作卡保存来源、竞争假设与数据/实验缺口；它不是模型响应、原生实验receipt或科学PASS。没有自动写入/替换旧canonical候选队列，也没有改变历史人工parent裁决或正在运行的论文实验。

## Round 1 到 Round 2

先确认真实低信任入口、文档承诺、当前实现、无害实际效果、匹配对照和根因，再根据证据选择漏洞、风险测量或审计研究的正确论文类型。若差异完全是已知机制或正常文档行为，记录降级而非改名复活。

只有真实根因确定后，第二轮才选择防御设计；现有SkillGuard、ClosureBound、SkillSentry等只作为最近邻/对照，不伪装成本轮创新。

## 执行安全

不把未知Skill加入本Agent技能目录，不下载后直接执行样本，不用真实credentials，不向外发真实文档，不对公开目标做未授权测试。后续沙箱仅使用可恢复的临时资源和无害标记；真实未公开漏洞先按负责披露流程处理，公开页面不发布武器化细节。

## 验证与局限

测试覆盖来源ID/日期、私有候选不出现在公开投影、文献/公告/issue分层、竞争预测与停止条件、禁止无回执提升新颖性或执行状态、接入既有计划schema，以及全文档出处。

这些检查验证数据结构和工作流，不代表研究问题科学成立。新的首轮候选保持 `UNCONFIRMED / NOT_RUN`；模型调用、实验和投稿权限均未自动开启。
