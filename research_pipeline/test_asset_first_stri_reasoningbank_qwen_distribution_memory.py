from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_memory import (
    adjudicate_fidelity, audit_sample, parse_official_memory_items,
)


def test_official_parser_is_exact_blank_line_split():
    raw = "# Memory Item 1\n## Title One\n\n## Content A\n\n# Memory Item 2\n## Title Two"
    assert parse_official_memory_items(raw) == [
        "# Memory Item 1\n## Title One", "## Content A", "# Memory Item 2\n## Title Two",
    ]


def test_audit_sample_is_exact_quarter_and_deterministic():
    tasks = [f"task-{i:02d}" for i in range(32)]
    first = audit_sample(tasks, experiment_id="experiment")
    assert len(first) == 8
    assert first == audit_sample(list(reversed(tasks)), experiment_id="experiment")


def test_fidelity_threshold_is_strictly_greater_than_quarter():
    two = [{"SEVERE_FIDELITY_FAILURE": i < 2} for i in range(8)]
    three = [{"SEVERE_FIDELITY_FAILURE": i < 3} for i in range(8)]
    assert adjudicate_fidelity(two)["decision"] == "SOURCE_BANK_FIDELITY_QUALIFIED"
    assert adjudicate_fidelity(three)["decision"] == "SOURCE_BANK_FIDELITY_UNQUALIFIED"
