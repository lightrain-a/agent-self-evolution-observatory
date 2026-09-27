#!/usr/bin/env python3
"""Publish workflow metadata only. Never publish private manuscripts or model jobs."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from research_pipeline.paper_writing_loop import portfolio_state,write_json,atomic_text
import json


def build(root=ROOT):
    state=portfolio_state()
    state['retrospective']=[
        {'phase':'先搭可改的初稿','period':'09-14—09-17','problem':'材料和实验很多，但缺少一条统一问题线。','change':'以研究对象、直觉、方法边界和待验证问题初始化；允许实验框架空位，不虚报结果。'},
        {'phase':'从实验报告转为论文','period':'09-15—09-20','problem':'按执行历史写作，段落有记录但没有科学论证。','change':'先规定问题、观察、方法与证据的关系，参考论文只借结构，不移植结果。'},
        {'phase':'分清现象与方法','period':'09-20—09-23','problem':'容易把方法所针对的现象写成方法带来的机制。','change':'现象先行；具体例子与可观测量先解释，再进入方法及必要公式。'},
        {'phase':'图表和正文共同收束','period':'09-22—09-23','problem':'图表重复、文字逐格复述，核心信息被实现细节稀释。','change':'保留直接证据；多图型四联比较；每节与图表各自有明确论证任务。'},
        {'phase':'章节职责重新安排','period':'09-23','problem':'背景、现象、方法和相关工作顺序不利于首次阅读。','change':'Background/Preliminaries前移；按理解依赖组织，精简重复内容。'},
        {'phase':'逐章Improve与摘要回写','period':'09-23—09-26','problem':'全文笼统润色不能修复具体问题。','change':'先诊断、再局部改写、核对；摘要和结论随当前证据同步。'},
        {'phase':'正文附录、成本与术语对齐','period':'09-24—09-26','problem':'相同符号、表格、比较阶段在不同位置容易漂移。','change':'核对分母、模型方向、screening与完整成本；删重复表，保留必要证明与协议。'},
        {'phase':'语言、实际版式和协作收尾','period':'09-24—09-26','problem':'孤行、图例、表注、引用链接和多窗口更新互相影响。','change':'不改官方布局凑页；实际PDF复核；保存新数据，按当前快照合并提交。'},
    ]
    state['boundaries']={'private_manuscript_published':False,'private_conversation_published':False,'live_heirs_rewritten':False,
                         'real_provider_quality_evaluation_completed':False,'deterministic_checks_are_not_semantic_or_pdf_review':True,
                         'figure_library_size_is_not_renderer_limit':True}
    write_json(root/'generated'/'paper-writing-workflow.json',state)
    atomic_text(root/'generated'/'paper-writing-workflow.js','window.PAPER_WRITING_WORKFLOW='+json.dumps(state,ensure_ascii=False,separators=(',',':'))+';\n')
    return state

if __name__=='__main__':
    s=build();print(json.dumps({'status':s['status'],'stages':len(s['stages']),'modes':len(s['modes']),'provider_calls':0}))
