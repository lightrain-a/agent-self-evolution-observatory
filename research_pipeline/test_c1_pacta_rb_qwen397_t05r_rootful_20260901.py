from pathlib import Path
import inspect

from research_pipeline import run_c1_pacta_rb_qwen397_t05r_rootful_20260901 as t05r


def complete_row(**changes):
    row = {key: True for key in (
        "import_pass", "digest_inspect_pass", "container_start_pass", "testbed_exists",
        "base_commit_exists", "base_is_ancestor", "initial_working_tree_clean",
        "runtime_tools_pass", "reset_pass", "post_reset_head_exact", "post_reset_working_tree_clean",
    )}
    row.update(changes)
    return row


def test_rootful_docker_detection_rejects_rootless():
    assert t05r.is_rootful_metadata({
        "docker_host": "unix:///var/run/docker.sock", "docker_root_dir": "/var/lib/docker",
        "architecture": "x86_64", "security_options": ["name=seccomp"],
    })
    assert not t05r.is_rootful_metadata({
        "docker_host": "unix:///run/user/1006/docker.sock", "docker_root_dir": "/data/rootless",
        "architecture": "x86_64", "security_options": ["name=rootless"],
    })


def test_initial_head_equality_is_not_required():
    row = complete_row(observed_initial_head="descendant", frozen_base_commit="base",
                       post_reset_head="base")
    assert t05r.normalization_pass(row)


def test_ancestry_and_reset_are_required():
    assert not t05r.normalization_pass(complete_row(base_is_ancestor=False))
    assert not t05r.normalization_pass(complete_row(post_reset_head_exact=False))
    assert not t05r.normalization_pass(complete_row(post_reset_working_tree_clean=False))


def test_fixed_pool_has_eleven_and_matplotlib():
    assert len(t05r.SPECS) == 11
    assert any(x[0] == "matplotlib__matplotlib-24627" for x in t05r.SPECS)


def test_t05r_has_no_scientific_entrypoints():
    source = inspect.getsource(t05r)
    for forbidden in ("SUCCESSFUL_SI", "FAILED_SI", "shadow_policy", "A3_PACTA"):
        assert forbidden not in source
    assert set(inspect.signature(t05r.main).parameters) == set()


def test_historical_root_is_read_only_input():
    source = inspect.getsource(t05r)
    assert "OLD_T05" in source
    assert "DEFAULT_ROOT" in source
    assert t05r.OLD_T05 != t05r.DEFAULT_ROOT
