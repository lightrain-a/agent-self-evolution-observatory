from __future__ import annotations

import pytest

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_edit_targets import (
    atoms_from_signature, edit_target_set, jaccard_distance,
)

FENCE = ""


def diff(path: str, header: str, body: str = "-old\n+new") -> str:
    return f"""diff --git a/{path} b/{path}
--- a/{path}
+++ b/{path}
@@ {header} @@
{body}
"""


BASE = """x = 1

def top():
    value = 1
    def nested():
        return value
    return nested()

class Outer:
    class Inner:
        def method(self):
            return 1

async def coro():
    return 2
"""


@pytest.mark.parametrize(("header", "expected"), [
    ("-4 +4", "top"),
    ("-6 +6", "top.nested"),
    ("-10 +10", "Outer.Inner"),
    ("-11 +11", "Outer.Inner.method"),
    ("-1 +1", "<module_or_file>"),
    ("-14 +14", "coro"),
])
def test_python_symbol_resolution(header, expected):
    result = edit_target_set(diff("pkg/mod.py", header), {"pkg/mod.py": BASE})
    assert result["atoms"] == [{"relative_path": "pkg/mod.py", "qualified_symbol": expected}]


def test_new_python_file():
    patch = """diff --git a/new.py b/new.py
new file mode 100644
--- /dev/null
+++ b/new.py
@@ -0,0 +1,2 @@
+def x():
+    pass
"""
    assert edit_target_set(patch, {})["atoms"][0]["qualified_symbol"] == "<module_or_file>"


def test_deleted_python_file_uses_base_ast():
    patch = """diff --git a/pkg/mod.py b/pkg/mod.py
deleted file mode 100644
--- a/pkg/mod.py
+++ /dev/null
@@ -4,2 +0,0 @@
-def top():
-    value = 1
"""
    actual = edit_target_set(patch, {"pkg/mod.py": BASE})["atoms"]
    assert actual == [{"relative_path": "pkg/mod.py", "qualified_symbol": "top"}]


def test_unparsable_python_and_non_python():
    bad = edit_target_set(diff("bad.py", "-1 +1"), {"bad.py": "def ("})
    txt = edit_target_set(diff("README.md", "-1 +1"), {"README.md": "old"})
    assert bad["atoms"][0]["qualified_symbol"] == "<module_or_file>"
    assert bad["nonempty_python_diff_hunk_count"] == 1
    assert bad["python_fallback_hunk_count"] == 1
    assert txt["atoms"][0]["qualified_symbol"] == "<file>"
    assert txt["nonempty_python_diff_hunk_count"] == 0


def test_multiple_hunks_same_symbol_deduplicate():
    patch = diff("pkg/mod.py", "-4 +4") + "@@ -7 +7 @@\n-old\n+new\n"
    result = edit_target_set(patch, {"pkg/mod.py": BASE})
    assert result["atom_count"] == 1
    assert result["hunk_count"] == 2


def test_multiple_symbols_same_file_and_replay_hash():
    patch = diff("pkg/mod.py", "-4 +4") + "@@ -14 +14 @@\n-old\n+new\n"
    first = edit_target_set(patch, {"pkg/mod.py": BASE})
    second = edit_target_set(patch, {"pkg/mod.py": BASE})
    assert first == second
    assert first["atom_count"] == 2


def test_empty_patch_and_jaccard_special_cases():
    empty = edit_target_set("", {})
    assert empty["atoms"] == []
    assert jaccard_distance(set(), set()) == 0
    assert jaccard_distance(set(), {("a.py", "f")}) == 1
    assert jaccard_distance({("a", "f")}, {("a", "f"), ("b", "g")}) == .5
    assert atoms_from_signature(empty) == set()
