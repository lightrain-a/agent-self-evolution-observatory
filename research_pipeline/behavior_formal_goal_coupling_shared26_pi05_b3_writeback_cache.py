from __future__ import annotations

import os
import pathlib
import re
from dataclasses import dataclass, asdict
from typing import Any

_OCDBT_BLOB_RE = re.compile(r"^[0-9a-f]{32}$")
_MEMORY_KEYS = ("anon", "file", "file_dirty", "file_writeback", "inactive_file", "active_file")


@dataclass(frozen=True)
class BlobStat:
    path: str
    size: int
    mtime_ns: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _resolved_item_root(item_root: str | os.PathLike[str]) -> pathlib.Path:
    root = pathlib.Path(item_root).resolve(strict=True)
    if not root.is_dir():
        raise RuntimeError(f"B3 item root is not a directory: {root}")
    return root


def self_cgroup_memory_snapshot() -> dict[str, Any]:
    rel = None
    for line in pathlib.Path("/proc/self/cgroup").read_text().splitlines():
        if line.startswith("0::"):
            rel = line.split("::", 1)[1].lstrip("/")
            break
    if rel is None:
        raise RuntimeError("B3 requires cgroup v2 memory accounting")
    cg = pathlib.Path("/sys/fs/cgroup") / rel
    stat = {}
    for line in (cg / "memory.stat").read_text().splitlines():
        key, value = line.split()
        if key in _MEMORY_KEYS:
            stat[key] = int(value)
    return {
        "cgroup": "/" + rel,
        "memory_current": int((cg / "memory.current").read_text().strip()),
        "memory_stat": {key: int(stat.get(key, 0)) for key in _MEMORY_KEYS},
    }


def snapshot_ocdbt_data_blobs(item_root: str | os.PathLike[str]) -> dict[str, BlobStat]:
    """Snapshots only OCDBT data blobs, never manifests/Orbax metadata."""
    root = _resolved_item_root(item_root)
    data_root = root / "ocdbt.process_0" / "d"
    if not data_root.exists():
        return {}
    if data_root.is_symlink() or not data_root.is_dir():
        raise RuntimeError(f"B3 OCDBT data root is unsafe: {data_root}")
    out: dict[str, BlobStat] = {}
    for path in data_root.iterdir():
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"B3 refuses non-regular OCDBT data entry: {path}")
        if not _OCDBT_BLOB_RE.fullmatch(path.name):
            raise RuntimeError(f"B3 refuses unexpected OCDBT data filename: {path.name}")
        resolved = path.resolve(strict=True)
        if resolved.parent != data_root.resolve(strict=True):
            raise RuntimeError(f"B3 path escaped OCDBT data root: {resolved}")
        st = resolved.stat()
        out[path.name] = BlobStat(str(resolved), int(st.st_size), int(st.st_mtime_ns))
    return out


def reclaim_completed_ocdbt_data_blobs(
    item_root: str | os.PathLike[str],
    before: dict[str, BlobStat],
) -> list[dict[str, Any]]:
    """Fsyncs then advises away only newly materialized immutable-style OCDBT blobs.

    Caller ordering is part of the B3 contract: TensorStore batch writes and the
    sharding transaction must already be awaited before this helper is invoked.
    Only new `ocdbt.process_0/d/<32hex>` regular files are eligible. Existing or
    changed files, manifests, metadata, symlinks, and path escapes are excluded.
    """
    root = _resolved_item_root(item_root)
    after = snapshot_ocdbt_data_blobs(root)
    events: list[dict[str, Any]] = []
    for name, post in sorted(after.items()):
        if name in before:
            continue
        path = pathlib.Path(post.path)
        fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
        try:
            pre_fd = os.fstat(fd)
            before_fsync = self_cgroup_memory_snapshot()
            os.fsync(fd)
            after_fsync = self_cgroup_memory_snapshot()
            sync_fd = os.fstat(fd)
            if (pre_fd.st_size, pre_fd.st_mtime_ns) != (sync_fd.st_size, sync_fd.st_mtime_ns):
                raise RuntimeError(f"B3 target changed during durability barrier: {path}")
            os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
            after_fadvise = self_cgroup_memory_snapshot()
            final_fd = os.fstat(fd)
            if (sync_fd.st_size, sync_fd.st_mtime_ns) != (final_fd.st_size, final_fd.st_mtime_ns):
                raise RuntimeError(f"B3 target changed during cache advice: {path}")
            events.append(
                {
                    "path": str(path),
                    "relative_to_item": str(path.relative_to(root)),
                    "size": int(final_fd.st_size),
                    "mtime_ns": int(final_fd.st_mtime_ns),
                    "durability_barrier": "fsync",
                    "advice": "POSIX_FADV_DONTNEED",
                    "memory_before_fsync": before_fsync,
                    "memory_after_fsync": after_fsync,
                    "memory_after_fadvise": after_fadvise,
                }
            )
        finally:
            os.close(fd)
    return events
