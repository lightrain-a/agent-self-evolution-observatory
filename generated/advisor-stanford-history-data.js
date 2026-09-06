window.ADVISOR_STANFORD_HISTORY = {
  "schema_version": "1.0",
  "generated_at": "2026-09-06",
  "service": "Stanford Agentic Reviewer · paperreview.ai",
  "disclaimer_zh": "仅作 AI 外审参考，不是 Stanford 人工审稿，也不是 ICLR/NeurIPS 官方评分。只列当前仓库中能由 Stanford matrix、exact review receipt 或 Git 历史核验的分数。",
  "disclaimer_en": "AI external-review reference only; these are neither Stanford human reviews nor official venue scores. Only scores recoverable from review matrices, exact receipts, or Git history are shown.",
  "date_note_zh": "2026-08-23 的 R1/R2 来自统一 Stanford objection matrix；该矩阵保留轮次分数，但没有逐轮独立时间戳，因此同记为矩阵日期。",
  "date_note_en": "The 2026-08-23 R1/R2 entries come from the common Stanford objection matrix; it preserves round scores but not separate per-round timestamps, so both use the matrix date.",
  "papers": [
    {
      "paper_id": "E1",
      "name_zh": "E1 · STRI",
      "history": [
        {"date":"2026-08-23","round":"R1","score":5.8,"label_zh":"早期 STRI","lineage":"same"},
        {"date":"2026-08-23","round":"R2","score":6.1,"label_zh":"早期 STRI","lineage":"same"},
        {"date":"2026-09-05","round":"当前稿","score":6.5,"label_zh":"Skill-Taxonomy Representation Invariance","lineage":"current"}
      ],
      "note_zh": "同一 STRI 主线持续收窄、加强证据；当前 6.5 是 exact-current meeting PDF。"
    },
    {
      "paper_id": "B1",
      "name_zh": "B1 · Failure Memory Provenance",
      "history": [
        {"date":"2026-08-23","round":"R1","score":5.6,"label_zh":"早期 provenance 稿","lineage":"same"},
        {"date":"2026-08-23","round":"R2","score":5.4,"label_zh":"早期 provenance 稿","lineage":"same"},
        {"date":"2026-09-05","round":"当前稿","score":6.1,"label_zh":"显式 source-outcome field exposure","lineage":"current"}
      ],
      "note_zh": "正式历史矩阵为 5.6→5.4；此前口头汇总中的 3.2→4.3 未有可核验 receipt，故不展示。"
    },
    {
      "paper_id": "C1",
      "name_zh": "C1 · Feedback → Memory → Behavior",
      "history": [
        {"date":"2026-08-23","round":"R1","score":6.7,"label_zh":"旧 Proxy-Reward / Memory-Variance lineage","lineage":"old"},
        {"date":"2026-08-23","round":"R2","score":6.3,"label_zh":"旧 Proxy-Reward / Memory-Variance lineage","lineage":"old"},
        {"date":"2026-09-05","round":"Stage-resolved","score":5.2,"label_zh":"Memory Divergence Is Not Behavioral Divergence","lineage":"prior"},
        {"date":"2026-09-06","round":"当前统一稿","score":5.6,"label_zh":"From Feedback to Memory to Behavior","lineage":"current"}
      ],
      "note_zh": "6.7/6.3 是旧 scientific object；5.2→5.6 才是当前 stage-resolved→统一两幕故事的直接版本演化，不能把四个数当一条简单退步曲线。"
    },
    {
      "paper_id": "E2",
      "name_zh": "E2 · State Regeneration Instability",
      "history": [
        {"date":"2026-08-23","round":"R1","score":5.8,"label_zh":"旧 Temporal-Skill Causal Bottleneck lineage","lineage":"old"},
        {"date":"2026-08-23","round":"R2","score":5.4,"label_zh":"旧 Temporal-Skill Causal Bottleneck lineage","lineage":"old"},
        {"date":"2026-08-24","round":"R14","score":6.0,"label_zh":"Temporal Skill attribution-audit","lineage":"old"},
        {"date":"2026-09-05","round":"当前稿","score":5.4,"label_zh":"Same Evidence, Different Skill","lineage":"current"}
      ],
      "note_zh": "8 月评分对应旧 Temporal-Skill 对象；9 月 5 日 5.4 对应当前 state-regeneration paper，不能直接解释为同稿降分。"
    },
    {
      "paper_id": "PAPER_A",
      "name_zh": "论文 A · Influence–Fidelity",
      "history": [
        {"date":"2026-09-05","round":"当前预确证稿","score":5.7,"label_zh":"Influence → Source Fidelity","lineage":"current"}
      ],
      "note_zh": "当前只有这一轮；仍是 preconfirmatory advisor draft。"
    },
    {
      "paper_id": "PAPER_B",
      "name_zh": "论文 B · Embodied Persistent Memory",
      "history": [
        {"date":"2026-09-05","round":"当前预确证稿","score":5.6,"label_zh":"Persistent Memory Across Episodes","lineage":"current"}
      ],
      "note_zh": "当前只有这一轮；仍是 preconfirmatory advisor draft。"
    },
    {
      "paper_id": "G1",
      "name_zh": "G1 · ERTA",
      "history": [
        {"date":"2026-08-23","round":"R1","score":6.5,"label_zh":"早期 Agent Safety R9 lineage","lineage":"old"},
        {"date":"2026-08-23","round":"R2","score":6.3,"label_zh":"早期 Agent Safety R9 lineage","lineage":"old"},
        {"date":"2026-08-30","round":"当前 ERTA","score":6.3,"label_zh":"Temporal Safety Conclusions Are Evaluator-Relative","lineage":"current"}
      ],
      "note_zh": "2026-09-05 的 MCTA 4.8 属于 G2 candidate，不计入 G1/ERTA 评分轨迹。"
    },
    {
      "paper_id": "CONSTRAINT_EXTERNALITY",
      "name_zh": "约束外部性",
      "history": [
        {"date":"2026-09-05","round":"当前稿","score":6.2,"label_zh":"Constraint-Coupled Externalities","lineage":"current"}
      ],
      "note_zh": "当前只有这一轮；科学主实验尚未启动。"
    },
    {
      "paper_id": "3D",
      "name_zh": "3D · Relational Topology",
      "history": [
        {"date":"2026-09-05","round":"当前预确证稿","score":4.1,"label_zh":"Endpoint-Sharing Topology","lineage":"current"}
      ],
      "note_zh": "当前只有这一轮；主要被审的是 premise / identification / protocol，尚无 confirmatory outcome。"
    }
  ],
  "spinoffs": [
    {"paper_id":"G2_CANDIDATE","date":"2026-09-05","score":4.8,"label_zh":"MCTA · Capability Unlock vs Safety Drift","status":"HOLD_FOR_IDENTIFICATION","note_zh":"不属于当前九篇，不计入 G1/ERTA 主线。"}
  ],
  "sources": [
    "generated/stanford-r2-objection-matrix.json",
    "generated/temporal-skill-r14-stanford-review-result-20260824.json",
    "generated/stanford-*-review.json",
    "Git history for prior C1 5.2 and G1/MCTA lineage separation"
  ]
};
