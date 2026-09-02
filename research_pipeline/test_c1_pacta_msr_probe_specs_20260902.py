from __future__ import annotations
from research_pipeline import prepare_c1_pacta_msr_probe_specs_20260902 as p


def test_probe_specs_cover_all_ten_future_units_without_provider():
    o=p.prepare()
    assert o['status']=='MSR_10_PROBE_SPECS_V2_FROZEN_PRE_SOURCE_OUTCOME'
    assert len(o['rows'])==10
    assert o['provider_calls']==0 and o['future_task_executions']==0
    assert len({x['future_task_id'] for x in o['rows']})==10
    assert all(len(x['tokens'])==3 for x in o['rows'])
    assert all(x['branch_blind'] and x['memory_blind'] and x['read_only'] for x in o['rows'])


def test_probe_compiler_is_deterministic_and_bounded():
    task='Fix `foo_bar()` and `ParserState` behavior in src/module.py when parser_state is missing.'
    h=p.sha(task)
    a=p.compile_tokens(task,h);b=p.compile_tokens(task,h)
    assert a==b and len(a)==3
    cmd=p.compile_command(a)
    assert cmd==p.compile_command(a)
    assert cmd.startswith('git status --short; git grep -n -I ')
    assert cmd.endswith('; git ls-files | head -n 40')
    assert '| head -n 80;' in cmd
    assert '>' not in cmd and 'tee ' not in cmd and 'xargs' not in cmd


def test_probe_token_stoplist_excludes_generic_words():
    task='This issue should fix the current problem with `specific_identifier` and `another_symbol` plus useful_token.'
    toks=p.compile_tokens(task,p.sha(task))
    assert 'issue' not in [x.lower() for x in toks]
    assert 'problem' not in [x.lower() for x in toks]
    assert set(toks).issubset({'specific_identifier','another_symbol','useful_token'})
