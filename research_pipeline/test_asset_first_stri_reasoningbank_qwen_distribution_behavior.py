import pytest

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_behavior import (
    action_class, first_action_signature, trajectory_observables,
)


@pytest.mark.parametrize(("action", "expected"), [
    ("ls src", "LIST"), ("rg needle src/a.py", "SEARCH"),
    ("sed -n '1,4p' src/a.py", "READ"), ("pytest -q", "TEST"),
    ("apply_patch <<'PATCH'", "EDIT"),
    ("printf MINI_SWE_AGENT_FINAL_OUTPUT", "SUBMIT"), ("echo hi", "OTHER"),
])
def test_action_classes(action, expected):
    assert action_class(action) == expected


def test_first_action_fields_and_replay():
    actions = [{"type": "shell", "action": "rg needle src/a.py::Class.method"}]
    first = first_action_signature(actions)
    assert first["parse_valid"] is True
    assert first["action_class"] == "SEARCH"
    assert first["first_referenced_path"] == "src/a.py"
    assert first["first_referenced_python_symbol_or_module"] == "Class.method"
    assert first == first_action_signature(actions)


def test_invalid_first_action_is_preserved():
    first = first_action_signature([{"type": "format_error"}])
    assert first["parse_valid"] is False
    assert first["action_class"] == "OTHER"


def test_r3_automated_observables():
    actions = [{"type": "shell", "action": "pytest -q"}, {"type": "format_error"}]
    actual = trajectory_observables(
        actions=actions, patch="@@ -1 +1 @@\n-a\n+b\n",
        modified_files=["b.py", "b.py"], edit_target={"atoms": []},
        model_call_count=2, exit_status="Submitted")
    assert actual["modified_file_count"] == 1
    assert actual["diff_hunk_count"] == 1
    assert actual["tests_run_indicator"] is True
    assert actual["tests_run_count"] == 1
    assert actual["trajectory_length"] == 2
