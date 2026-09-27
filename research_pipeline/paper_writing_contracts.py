"""Section-specific writing tasks distilled from HEIRS author interactions.

These contracts guide exposition; they cannot grant scientific validity or invent
results. Section roles are semantic, never fixed ordinal chapter numbers.
"""
from __future__ import annotations
import re

VERSION = '1.0'
STAGES = (
    ('CURRENT_SOURCE', '读取当前稿与同步版本', 'Read current manuscript and versions'),
    ('EVIDENCE_HANDOFF', '接收当前数据、主表和选中图', 'Bind current data, tables and selected figures'),
    ('REFERENCE_ROLES', '核心参考材料按角色整理', 'Separate exemplar, baseline and evidence roles'),
    ('ARGUMENT_ARCHITECTURE', '先确认主线和章节职责', 'Confirm argument and section ownership'),
    ('FRAMEWORK', '建立完整但不虚报结果的框架', 'Build a complete scaffold without invented results'),
    ('SECTION_LOOP', '逐章诊断、修订与局部核对', 'Diagnose, revise and check one section at a time'),
    ('GLOBAL_RECONCILIATION', '图文、章节与正文附录对账', 'Reconcile text, visuals and appendix'),
    ('SUMMARY_SYNC', '回写标题、摘要和结论', 'Synchronize title, abstract and conclusion'),
    ('INDEPENDENT_REVIEW', '独立检查事实、逻辑与证据范围', 'Independent fact, logic and evidence review'),
    ('LAYOUT_AND_RELEASE', '实际尺寸排版检查与版本交付', 'Actual-size layout review and versioned delivery'),
)
ROLES = {
    'introduction': {
        'question': 'Why is this problem worth studying, and why does the proposed idea address it?',
        'order': ['concrete setting and stake', 'existing deployment practice', 'specific unresolved difficulty', 'evidence-backed intuition', 'minimal method', 'bounded contributions'],
        'avoid': ['implementation diary', 'formal definitions before motivation', 'contributions as a module inventory'],
    },
    'background': {
        'question': 'What must a new reader know before understanding the phenomenon and method?',
        'order': ['only needed preliminaries', 'method families and what they solve', 'closest work and exact residual question'],
        'avoid': ['citation catalogue without comparison', 'treating every adjacent method as a fair baseline'],
    },
    'phenomenon': {
        'question': 'What observation establishes the problem, and what is explanation rather than fact?',
        'order': ['plain finding', 'matched evidence', 'concrete case', 'scope and alternative explanation', 'transition to method'],
        'avoid': ['attributing a pre-existing phenomenon to our selector', 'equating correlation with mechanism', 'moving essential motivation to appendix'],
    },
    'method': {
        'question': 'What happens from input to output, and why is each necessary operation present?',
        'order': ['intuition', 'inputs and held-fixed objects', 'design requirements', 'operations in execution order', 'output and non-claims', 'cost and limitations'],
        'avoid': ['invented operations', 'renaming a standard primitive as a new theory', 'equations without an explanatory role'],
    },
    'theory': {
        'question': 'Which concrete relationship needs formal explanation, under which assumptions?',
        'order': ['scientific relationship', 'definitions and assumptions', 'derivation', 'interpretation', 'observability and limits'],
        'avoid': ['decorative theorem count', 'sufficient condition written as necessary', 'weight-space assumptions silently transferred to text'],
    },
    'experiments': {
        'question': 'What do completed evaluations establish, compared with which alternative?',
        'order': ['concise setup', 'main effect and counterexamples', 'mechanism or component questions', 'budget and cost', 'boundary'],
        'avoid': ['execution chronology', 'cell-by-cell repetition', 'win/loss/tie scoreboard replacing effect sizes', 'mixing screening and end-to-end cost'],
    },
    'abstract': {
        'question': 'What is the problem, idea, completed evidence and bounded conclusion?',
        'order': ['setting and missed choice', 'specific gap', 'intuition and method', 'representative current evidence', 'bounded conclusion'],
        'avoid': ['results from a superseded table', 'promising planned experiments as findings', 'copying exemplar sentences'],
    },
    'conclusion': {
        'question': 'What was learned, where does it apply, and what remains unresolved?',
        'order': ['return to the question', 'current supported findings', 'limitations', 'broader impact when required'],
        'avoid': ['universalizing migration-specific results', 'claiming a future controller already exists', 'padding to fill space'],
    },
    'appendix': {
        'question': 'What additional material is needed to reproduce, verify or delimit the main argument?',
        'order': ['protocols and identities', 'proofs and assumptions', 'full supporting results', 'diagnostics and reproducibility'],
        'avoid': ['duplicate main table without a distinct purpose', 'author repair diary', 'conflicting definitions or populations'],
    },
}
MODES = {
    'OUTLINE': 'Return a one-page argument and section-ownership plan. Do not rewrite LaTeX or invent outcomes.',
    'DRAFT': 'Draft only the named section from the bound packet. Framework-mode results remain explicit missing inputs, not affirmative findings.',
    'REWRITE': 'Diagnose the named section, then rewrite only that section. Keep evidence identities and approved scope fixed.',
    'LOCAL_POLISH': 'Make local wording corrections only. Preserve section structure, numeric facts, definitions, citations, figure/table calls and venue layout.',
    'APPENDIX_ALIGN': 'Compare main and appendix claims, definitions, protocols and costs. Return conflicts and targeted edits; no silent evidence deletion.',
    'SUMMARY_SYNC': 'Update the named abstract or conclusion to current section evidence. Do not add a result or strengthen the claim to improve the story.',
    'LAYOUT_QA': 'Prepare local wording/layout suggestions. A source check cannot certify page count, orphan lines or visual legibility without an actual rendered-page review.',
}
COMMON = (
    'Serve the reader, not the author or research log. Prefer ordinary syntax, concrete subjects and verbs. ',
    'Open result paragraphs with a bounded answer, then evidence, then explanation. Preserve necessary qualifications without repeating them everywhere. ',
    'Do not reproduce table cells in prose or hide adverse/inconclusive evidence. Distinguish observed facts, definitions, protocols, literature and tentative interpretation. ',
    'An exemplar supplies structure, never our empirical facts. A gallery image is a design reference, never a result figure. ',
    'Do not change methods, data, source/target direction, denominators, comparison phases or venue style to satisfy prose. ',
    'A need for new evidence returns an experiment/evidence request; it is not permission to execute. ',
    'Do not write internal iteration IDs, repair diaries, PASS stamps or “we have now corrected” explanations into the paper. ',
    'Keep meaningful negative results. Do not force the draft into the final page limit before its argument is coherent. ',
    'Abstract and conclusion summarize current evidence. Formatting polish cannot substitute for independent fact/logic/evidence review. ',
)


def classify_feedback(text: str) -> dict:
    """Routing suggestions only; explicit user scope/mode remains authoritative."""
    t = text.lower()
    routes = []
    patterns = (
        ('STRUCTURE', r'实验报告|主线|架构|章节顺序|合并.*章|background|preliminar|related work.*前|phenomenon'),
        ('EVIDENCE_CHANGE', r'新数据|更新数据|结果更新|分母|数据集|重跑|baseline|成本口径|screening|数字.*错'),
        ('APPENDIX_ALIGN', r'附录|appendix|重复.*表|冲突'),
        ('FIGURE_PREPARATION', r'图例|子图|画图|图库|四联|四个|figure|fig\.?\s*\d'),
        ('CITATION_CHECK', r'参考文献|引用|citation|bibtex'),
        ('SUMMARY_SYNC', r'摘要|结论|abstract|conclusion|标题'),
        ('LAYOUT_QA', r'末行|最后一行|孤行|页眉|页头|页数|间距|字号|空白|排版|overfull'),
        ('LOCAL_POLISH', r'小幅|微调|不.*大改|语法|拼写|清晰|直白|润色|grammar|spelling'),
    )
    for name, pattern in patterns:
        if re.search(pattern,t): routes.append(name)
    return {'routes': routes or ['SECTION_DIAGNOSIS'],
            'local_scope_requested': bool(re.search(r'小幅|微调|不.*大改|only.*polish',t)),
            'automatic_full_rewrite': False, 'automatic_experiment_execution': False}
