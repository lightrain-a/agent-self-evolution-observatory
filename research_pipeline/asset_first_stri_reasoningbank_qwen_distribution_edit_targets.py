"""Deterministic EditTargetSet extraction against a frozen base tree."""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Any, Mapping

from research_pipeline.asset_first_stri_reasoningbank_p1_core import canonical_json, sha256_text

DIFF_RE = re.compile(r"^diff --git a/(.+) b/(.+)$")
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


@dataclass(frozen=True, slots=True)
class Hunk:
    old_path: str
    new_path: str
    old_start: int
    old_count: int
    new_start: int
    new_count: int

    @property
    def path(self) -> str:
        return self.new_path if self.new_path != "/dev/null" else self.old_path


@dataclass(frozen=True, slots=True)
class SymbolSpan:
    qualified_name: str
    start: int
    end: int
    depth: int


def parse_hunks(diff_text: str) -> list[Hunk]:
    hunks: list[Hunk] = []
    old_path = new_path = ""
    for line in diff_text.splitlines():
        match = DIFF_RE.match(line)
        if match:
            old_path, new_path = match.groups()
            continue
        if line.startswith("--- "):
            value = line[4:].split("\t", 1)[0]
            old_path = "/dev/null" if value == "/dev/null" else value.removeprefix("a/")
            continue
        if line.startswith("+++ "):
            value = line[4:].split("\t", 1)[0]
            new_path = "/dev/null" if value == "/dev/null" else value.removeprefix("b/")
            continue
        match = HUNK_RE.match(line)
        if match and old_path and new_path:
            old_start, old_count, new_start, new_count = match.groups()
            hunks.append(Hunk(
                old_path=old_path, new_path=new_path,
                old_start=int(old_start), old_count=int(old_count or 1),
                new_start=int(new_start), new_count=int(new_count or 1),
            ))
    return hunks


def symbol_spans(source: str) -> list[SymbolSpan]:
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, TypeError):
        return []
    spans: list[SymbolSpan] = []

    def walk(body: list[ast.stmt], parents: tuple[str, ...]) -> None:
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = ".".join((*parents, node.name))
                decorators = [int(d.lineno) for d in getattr(node, "decorator_list", [])]
                start = min([int(node.lineno), *decorators])
                end = int(getattr(node, "end_lineno", node.lineno))
                spans.append(SymbolSpan(name, start, end, len(parents) + 1))
                walk(list(node.body), (*parents, node.name))
            elif isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While,
                                   ast.With, ast.AsyncWith, ast.Try)):
                nested: list[ast.stmt] = list(node.body) + list(getattr(node, "orelse", []))
                nested += list(getattr(node, "finalbody", []))
                for handler in getattr(node, "handlers", []):
                    nested += list(handler.body)
                walk(nested, parents)
    walk(list(tree.body), ())
    return spans


def enclosing_symbol(source: str, old_start: int, old_count: int) -> str:
    spans = symbol_spans(source)
    if not spans:
        return "<module_or_file>"
    if old_count == 0:
        start = end = max(1, old_start)
    else:
        start, end = old_start, old_start + old_count - 1
    containing = [s for s in spans if s.start <= start and s.end >= end]
    if not containing:
        return "<module_or_file>"
    containing.sort(key=lambda s: (-s.depth, s.end - s.start, s.qualified_name))
    return containing[0].qualified_name


def edit_target_set(diff_text: str, base_files: Mapping[str, str]) -> dict[str, Any]:
    atoms: set[tuple[str, str]] = set()
    hunks = parse_hunks(diff_text)
    python_hunk_count = 0
    python_fallback_hunk_count = 0
    for hunk in hunks:
        path = hunk.path
        if not path:
            continue
        if not path.endswith(".py"):
            atom = (path, "<file>")
        elif hunk.old_path == "/dev/null":
            python_hunk_count += 1
            python_fallback_hunk_count += 1
            atom = (path, "<module_or_file>")
        else:
            python_hunk_count += 1
            source = base_files.get(hunk.old_path)
            symbol = "<module_or_file>" if source is None else enclosing_symbol(
                source, hunk.old_start, hunk.old_count)
            if symbol == "<module_or_file>":
                python_fallback_hunk_count += 1
            atom = (path, symbol)
        atoms.add(atom)
    ordered = [{"relative_path": path, "qualified_symbol": symbol}
               for path, symbol in sorted(atoms)]
    return {
        "schema_version": 1,
        "atom_count": len(ordered),
        "atoms": ordered,
        "signature_sha256": sha256_text(canonical_json(ordered)),
        "hunk_count": len(hunks),
        "nonempty_python_diff_hunk_count": python_hunk_count,
        "python_fallback_hunk_count": python_fallback_hunk_count,
    }


def jaccard_distance(left: set[tuple[str, str]], right: set[tuple[str, str]]) -> float:
    if not left and not right:
        return 0.0
    if not left or not right:
        return 1.0
    return 1.0 - len(left & right) / len(left | right)


def atoms_from_signature(signature: Mapping[str, Any]) -> set[tuple[str, str]]:
    return {(str(row["relative_path"]), str(row["qualified_symbol"]))
            for row in signature["atoms"]}
