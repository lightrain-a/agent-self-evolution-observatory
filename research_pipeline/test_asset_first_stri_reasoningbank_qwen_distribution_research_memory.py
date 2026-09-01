from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_research_memory import (
    lesson_catalog,
)


def test_scientific_memory_preserves_all_eight_predeclared_lessons():
    lessons = lesson_catalog()
    assert len(lessons) == 8
    assert len(set(lessons)) == 8
    assert lessons[0].startswith("implementation/operationalization failure")
    assert "same-state stochastic dispersion" in lessons[6]
    assert "prospectively" in lessons[7]
