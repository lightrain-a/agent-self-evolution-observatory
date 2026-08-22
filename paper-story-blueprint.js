window.PAPER_STORY_DATA={schema_version:"1.0",papers:{},blueprint:{steps:[
{id:"scene",zh:"场景与价值",en:"Scenario & value",q_zh:"谁在什么场景遇到什么问题？不解决有什么实际损失？",q_en:"Who faces what problem, and why does it matter?"},
{id:"failure",zh:"具体现象",en:"Concrete failure",q_zh:"先给一个能看懂的失败例子，再抽象问题。",q_en:"Show a concrete failure before abstraction."},
{id:"prior",zh:"现有方法",en:"Existing approaches",q_zh:"今天大家怎么做？最强简单方法是什么？每类方法卡在哪里？",q_en:"What do people do today, and where does each approach fail?"},
{id:"gaps",zh:"三个核心缺口",en:"Three gaps",q_zh:"把现有方法的问题压成三个可检验的 gap。",q_en:"Reduce prior limitations to three testable gaps."},
{id:"design",zh:"设计动机与方法",en:"Design motivation & method",q_zh:"每个组件为什么存在？解决哪个 gap？去掉会失去什么？",q_en:"Map every component to a gap and explain why it is necessary."},
{id:"experiments",zh:"实验论证",en:"Experimental argument",q_zh:"逐个回答：有效吗？比最强基线好吗？为什么好？哪里不成立？",q_en:"Answer effect, strongest baseline, mechanism, and boundary questions."},
{id:"mechanism",zh:"组件与机制",en:"Components & mechanism",q_zh:"用 control / ablation / mediator / null 说明是哪部分生效。",q_en:"Use controls, ablations, mediators, and nulls to identify what matters."},
{id:"boundary",zh:"边界与意义",en:"Boundary & significance",q_zh:"最后明确证明了什么、没证明什么、为什么值得知道。",q_en:"State what is established, what is not, and why it matters."}
],outline:[
{sec:"Abstract",zh:"场景1句 → gap1句 → 方法1–2句 → 最关键数字 → bounded takeaway。",en:"Setting → gap → method → decisive results → bounded takeaway."},
{sec:"1 · Introduction",zh:"真实场景与价值 → 一个具体失败 → 现有方法为什么不够 → 三个 gap → 设计原则 → contributions。",en:"Scenario/value → failure → prior limitations → three gaps → design principle → contributions."},
{sec:"2 · Problem & Prior Approaches",zh:"定义任务、干预对象、控制变量、strongest simple baseline；Related Work 围绕“差在哪”组织。",en:"Define task, intervention, controls, and strongest simple baseline; organize related work by missing capability."},
{sec:"3 · Method",zh:"先讲设计动机，再逐组件解释“解决哪个 gap”，最后给完整 pipeline。",en:"Start from design requirements, map components to gaps, then present the full pipeline."},
{sec:"4 · Experimental Design",zh:"RQ1主效应、RQ2强基线、RQ3机制/消融、RQ4 transfer/robustness；提前写 falsifier 和统计单位。",en:"RQ1 main effect, RQ2 strongest baseline, RQ3 mechanism/ablation, RQ4 transfer/robustness with falsifiers."},
{sec:"5 · Results",zh:"按 RQ 回答，不按数据集流水账；每节先一句答案，再给数字、图、统计与反例。",en:"Answer RQs rather than narrating datasets; lead with the answer and decisive evidence."},
{sec:"6 · Mechanism / Ablation",zh:"说明哪个组件生效、哪个替代解释被排除、哪些结果是 null。",en:"Show which component matters, what alternative explanation is ruled out, and which results are null."},
{sec:"7 · Limitations & Scope",zh:"明确 assumptions、统计分辨率、外部效度和缺失 baseline 如何限制 claim。",en:"State assumptions, statistical resolution, external validity, and missing baselines."},
{sec:"Appendix / Reproducibility",zh:"完整协议、prompt/skill、数据处理、统计、失败结果和复现命令放附录；主文只保留理解 claim 必需的信息。",en:"Put full protocols, prompts/skills, data processing, statistics, failures, and reproduction commands in appendices."}
]}};