import research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_extract as extract


def test_trajectory_input_excludes_system_and_evaluator():
    receipt = {"trajectory": {
        "messages": [
            {"role": "system", "content": "system memory"},
            {"role": "user", "content": "task"},
            {"role": "assistant", "content": "action"},
            {"role": "user", "content": "observation"},
        ],
        "R4_terminal_outcome": {"raw_output": "secret evaluator output"},
    }}
    text = extract.trajectory_input(receipt)
    assert text == "task\naction\nobservation"
    assert "system memory" not in text
    assert "secret evaluator output" not in text


def test_failed_preinteraction_source_has_deterministic_input():
    receipt = {"trajectory": {
        "messages": [], "failure": {"failure_layer": "runtime", "error_type": "X"}}}
    first = extract.trajectory_input(receipt)
    assert first == extract.trajectory_input(receipt)
    assert "runtime" in first
