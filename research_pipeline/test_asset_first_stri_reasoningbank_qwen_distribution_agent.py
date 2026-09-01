from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_agent import (
    model_visible_task_sha256, modified_files_from_status, request_body,
)


def test_task_hash_binds_all_model_visible_task_identity_fields():
    row = {"instance_id": "repo__1", "problem_statement": "fix it",
           "base_commit": "abc", "repo": "org/repo", "version": "1"}
    first = model_visible_task_sha256(row)
    assert len(first) == 64
    assert model_visible_task_sha256(row) == first
    assert model_visible_task_sha256({**row, "problem_statement": "change"}) != first


def test_request_uses_q0_sampling_and_no_retry_fields():
    body = request_body(
        [{"role": "user", "content": "task"}],
        {"temperature": 1.0, "top_p": .95, "top_k": 40, "max_output_tokens": 32768})
    assert body == {
        "model": "qwen3-coder-next",
        "messages": [{"role": "user", "content": "task"}],
        "temperature": 1.0, "top_p": .95, "top_k": 40,
        "max_completion_tokens": 32768, "n": 1, "stream": False,
    }
    assert "seed" not in body
    assert "max_retries" not in body


def test_request_omits_unqualified_top_k():
    body = request_body([], {
        "temperature": 1.0, "top_p": .95,
        "top_k": "OMITTED_UNPROVEN_OR_UNSUPPORTED", "max_output_tokens": 32768})
    assert "top_k" not in body


def test_modified_files_are_deduplicated_and_rename_uses_new_path():
    status = " M src/a.py\n?? src/new.py\nR  old.py -> new.py\n M src/a.py\n"
    assert modified_files_from_status(status) == ["new.py", "src/a.py", "src/new.py"]
