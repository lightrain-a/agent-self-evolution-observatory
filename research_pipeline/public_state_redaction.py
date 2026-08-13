from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT, StorageSettings


def _replace_root(text: str, root: Path, scheme: str) -> str:
    raw = str(root.resolve())
    if not raw:
        return text
    if text == raw:
        return scheme.rstrip("/")
    prefix = raw.rstrip("/") + "/"
    if prefix in text:
        return text.replace(prefix, scheme)
    return text


def redact_private_paths(value: Any, *, storage: StorageSettings | None = None) -> Any:
    """Return a public-safe copy of a nested state object.

    Runtime/private absolute paths are never needed by the public site. Paths under
    the experiment data root become ``private-data://...`` and repository paths
    become ``repo://...``. Any other absolute POSIX path is reduced to a basename.
    URLs and ordinary prose are left unchanged.
    """
    storage = storage or StorageSettings.from_env()
    if isinstance(value, dict):
        return {str(key): redact_private_paths(item, storage=storage) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_private_paths(item, storage=storage) for item in value]
    if isinstance(value, tuple):
        return [redact_private_paths(item, storage=storage) for item in value]
    if not isinstance(value, str):
        return value

    text = value
    text = _replace_root(text, storage.data_root, "private-data://")
    text = _replace_root(text, PROJECT_ROOT, "repo://")
    if text.startswith("/"):
        return "private-data://external/" + Path(text).name
    return text
