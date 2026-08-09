window.FINAL20_MERGE_AUDIT={
 review_date:"2026-08-09",
 summary:{final_sources:20,merged_into_discussed:15,standalone_source_records:4,standalone_current_ideas:3,component_only:1},
 decisions:{
  "contradiction-preserving-consolidation":{decision:"merge",target:"B-2"},
  "compositional-update-compatibility":{decision:"merge",target:"A-4"},
  "update-trust-region":{decision:"merge",target:"A-1"},
  "correction-action-causal-compiler":{decision:"merge",target:"C-6"},
  "memory-interaction-clause-learner":{decision:"merge",target:"B-3"},
  "probe-mutation-retirement-policy":{decision:"merge",target:"A-3"},
  "update-composition-repair-compiler":{decision:"merge",target:"A-4"},
  "monotone-applicability-specializer-v4":{decision:"merge",target:"B-5"},
  "api-error-semantic-adapter":{decision:"standalone-combine",target:"E-3"},
  "workflow-repair-grammar-v5":{decision:"merge",target:"E-2"},
  "restoration-clause-induction-v5":{decision:"merge",target:"A-4"},
  "rubric-intervention-sparse-solver":{decision:"merge",target:"C-2"},
  "update-history-semantic-compactor":{decision:"merge",target:"A-5"},
  "bounded-probe-api-transition-operator":{decision:"standalone-combine",target:"E-3"},
  "interventional-permission-triage-under-ceiling":{decision:"standalone",target:"E-4"},
  "nested-pathway-memory-repair":{decision:"merge",target:"B-3"},
  "constraint-complete-typed-memory-order-logic":{decision:"standalone",target:"B-8"},
  "certified-out-of-span-interaction-inverter-v53":{decision:"component-only",target:"A-4"},
  "compiler-residual-contract-editor-v53":{decision:"merge",target:"E-2"},
  "filtered-chronological-evaluator-state-v53":{decision:"merge",target:"C-2"}
 },
 standalone_ideas:[
  {id:"typed-memory-order-logic",code:"B-8",group:"B",source_ids:["constraint-complete-typed-memory-order-logic"],status:"new-review",title:{zh:"类型化记忆顺序逻辑",en:"Typed Memory-Order Logic"},purpose:{zh:"多条记忆共同检索时，正确执行顺序可能由高阶、上下文相关约束决定，而不是简单的相似度或两两先后偏好。",en:"When multiple memories are retrieved together, correct execution order can depend on higher-order, context-dependent constraints rather than similarity or pairwise precedence."},core_intuition:{zh:"逐条记忆都正确，不代表组合使用就正确。系统需要学习哪些记忆类型可交换、哪些必须先后、哪些上下文会反转顺序。",en:"Individually correct memories need not compose correctly. The system must learn which types commute, which require precedence, and when context reverses the order."},core_idea:{zh:"从随机置换干预中学习最小类型化顺序约束程序，并与同等表达力的 n 元因子模型做表征×解码器对比；学习后编译为冻结免搜索执行策略。",en:"Learn a minimal typed ordering-constraint program from randomized permutation interventions, compare it against an equally expressive n-ary factor model, and compile it into a frozen search-free execution policy."},strongest_baseline:{zh:"相同类型、数据、容量和精确求解器的 n 元因子模型。",en:"An n-ary factor model with the same types, data, capacity, and exact solver."}},
  {id:"bounded-probe-api-transition-semantics",code:"E-3",group:"E",source_ids:["api-error-semantic-adapter","bounded-probe-api-transition-operator"],status:"new-review",title:{zh:"限探针 API 转移语义适配",en:"Bounded-Probe API Transition-Semantics Adaptation"},purpose:{zh:"工作流迁移到新 API 时，名称和 schema 相似的操作仍可能在前置条件、状态副作用和错误恢复语义上不同，导致主路径可运行但恢复分支静默失效。",en:"Across API migrations, similar names and schemas may hide different preconditions, state effects, and recovery semantics, so the happy path runs while recovery branches fail."},core_intuition:{zh:"工作流真正依赖的是“什么时候能调用、成功后状态怎么变、失败后如何恢复”。把这些统一成 P/E/X 转移结构，并只用少量目标 API Probe 校准，比直接重写整个工作流更容易跨供应商复用。",en:"Workflows depend on when an operation is callable, what success changes, and how failures recover. A shared P/E/X transition structure calibrated with a few target probes should transfer better than whole-workflow rewriting."},core_idea:{zh:"学习类型化转移算子 T=(P,E,X)：P 为前置状态谓词，E 为成功状态增量，X 为学习得到的规范错误/恢复状态；迁移时只允许 N 次目标 API Probe，随后冻结并重新编译恢复分支。",en:"Learn typed transition operators T=(P,E,X): pre-state predicate P, success-state delta E, and learned canonical error/recovery state X; allow only N target-API probes, then freeze and recompile recovery branches."},strongest_baseline:{zh:"同构 P/E/X 表示但不跨源学习，仅从目标文档、schema 与同样 N Probe 用确定性规则实例化。",en:"The same P/E/X representation without cross-source learning, instantiated deterministically from target docs/schema and the same N probes."}},
  {id:"post-update-permission-reauthorization-triage",code:"E-4",group:"E",source_ids:["interventional-permission-triage-under-ceiling"],status:"new-review",title:{zh:"更新后权限重授权筛选",en:"Post-Update Permission Reauthorization Triage"},purpose:{zh:"Agent 更新后若全部权限重新授权成本很高；只看代码/配置 diff 又可能漏掉表面没变、可达行为却改变的权限。",en:"Full reauthorization after every agent update is costly, while code/config diffs can miss permissions whose surface is unchanged but reachable behavior changed."},core_intuition:{zh:"更新不能自动扩大权限。真正需要复验的，是新版本中对可达行为产生新影响的既有权限；训练期权限干预可以学习哪些“更新差异×权限”组合会产生新风险。",en:"An update must not expand authority automatically. Revalidation is needed only for existing grants that acquire new reachable effects; training-time permission interventions can learn which update-difference × permission combinations create new risk."},core_idea:{zh:"固定不可突破的权限上限，学习 q(diff,permission) 新诱发风险概率；只有高风险授权进入 canary 重授权，其他授权最多保留旧权限、绝不升级。",en:"Keep an immutable authority ceiling and learn q(diff,permission), the probability of newly induced risk; only high-risk grants enter canary reauthorization, while all others can at most retain prior authority."},strongest_baseline:{zh:"同样固定权限上限下，仅依据 manifest、依赖图或可达效果差异做确定性重授权筛选。",en:"Deterministic reauthorization using manifest/dependency/reachable-effect diffs under the same fixed authority ceiling."}}
 ]
};
