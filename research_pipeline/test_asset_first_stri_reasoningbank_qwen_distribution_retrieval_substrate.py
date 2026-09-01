from pathlib import Path

import pytest

import research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_retrieval_substrate as substrate


def test_revision_metadata(tmp_path):
    metadata = tmp_path / ".cache/huggingface/download/x.metadata"
    metadata.parent.mkdir(parents=True)
    metadata.write_text(substrate.REVISION + "\netag\ntime\n")
    assert substrate.revision_metadata(tmp_path) == {substrate.REVISION}


def test_inventory_drift_fails_before_hashing(tmp_path):
    (tmp_path / "unexpected").write_text("x")
    with pytest.raises(RuntimeError, match="inventory drift"):
        substrate.verify_snapshot(tmp_path)
