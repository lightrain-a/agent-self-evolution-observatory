from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_calibration import (
    quantile,
)


def test_quantile_and_empty():
    assert quantile([], .5) is None
    assert quantile([1, 2, 3], .5) == 2
    assert quantile([0, 10], .9) == 9
