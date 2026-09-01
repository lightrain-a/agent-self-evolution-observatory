from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_pilot_gate import (
    pilot_metric_gate,
)


def sig(*atoms, hunks=1, fallbacks=0):
    return {
        "atoms": [{"relative_path": path, "qualified_symbol": symbol}
                  for path, symbol in atoms],
        "nonempty_python_diff_hunk_count": hunks,
        "python_fallback_hunk_count": fallbacks,
    }


def test_constant_distance_gate_fails_at_ninety_percent():
    same = sig(("a.py", "f"))
    tasks = {"t": {"A": [same] * 4, "D": [same] * 4}}
    result = pilot_metric_gate(tasks)
    assert result["modal_distance_rate"] == 1
    assert result["decision"] == "EDIT_TARGET_METRIC_UNQUALIFIED"


def test_symbol_fallback_gate_fails():
    values = [
        sig(("a.py", f"f{i}"), hunks=1, fallbacks=1)
        for i in range(8)
    ]
    result = pilot_metric_gate({"t": {"A": values[:4], "D": values[4:]}})
    assert result["python_fallback_rate"] == 1
    assert result["python_symbol_fallback_degeneracy"] is True


def test_varied_symbol_metric_qualifies():
    a = ("a.py", "f")
    b = ("b.py", "g")
    c = ("c.py", "h")
    values = [
        sig(a), sig(a, b), sig(b), sig(a, c),
        sig(c), sig(b, c), sig(a, b, c), sig(hunks=0),
    ]
    result = pilot_metric_gate({"t": {"A": values[:4], "D": values[4:]}})
    assert result["decision"] == "EDIT_TARGET_METRIC_QUALIFIED"
