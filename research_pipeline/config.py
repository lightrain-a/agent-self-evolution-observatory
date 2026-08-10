from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_S2_BASE_URL = "https://api.semanticscholar.org/graph/v1"
DEFAULT_DATA_ROOT = PROJECT_ROOT / "generated" / "research-data"


def load_env_file(path: Path = DEFAULT_ENV_FILE) -> None:
    """Load a small dotenv file without adding a third-party dependency.

    Existing process environment variables always win. The parser accepts
    KEY=value lines, optional single/double quotes, comments, and blank lines.
    """

    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _float_env(name: str, default: float, *, minimum: float | None = None) -> float:
    raw = os.getenv(name)
    value = default if raw is None else float(raw)
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {value}")
    return value


def _int_env(name: str, default: int, *, minimum: int | None = None) -> int:
    raw = os.getenv(name)
    value = default if raw is None else int(raw)
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {value}")
    return value


def _path_env(name: str, default: Path) -> Path:
    return Path(os.getenv(name, str(default))).expanduser()


def _disk_summary(path: Path) -> dict[str, object]:
    probe = path
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    try:
        usage = shutil.disk_usage(probe)
    except OSError:
        return {"probe": str(probe), "available": False}
    gib = 1024**3
    return {
        "probe": str(probe),
        "available": True,
        "total_gib": round(usage.total / gib, 1),
        "used_gib": round(usage.used / gib, 1),
        "free_gib": round(usage.free / gib, 1),
    }


@dataclass(frozen=True, slots=True)
class StorageSettings:
    """Separate small source artifacts from large research data.

    The repository remains under PROJECT_ROOT. Corpora, datasets, PDFs,
    indexes, caches, and experiment runs can be redirected to a large local
    data disk through RESEARCH_DATA_ROOT and the more specific overrides.
    """

    data_root: Path
    corpus_dir: Path
    dataset_dir: Path
    paper_dir: Path
    index_dir: Path
    run_dir: Path
    cache_dir: Path
    lock_dir: Path
    site_artifact_dir: Path

    @classmethod
    def from_env(cls, *, env_file: Path = DEFAULT_ENV_FILE) -> "StorageSettings":
        load_env_file(env_file)
        data_root = _path_env("RESEARCH_DATA_ROOT", DEFAULT_DATA_ROOT)
        return cls(
            data_root=data_root,
            corpus_dir=_path_env("RESEARCH_CORPUS_DIR", data_root / "corpora"),
            dataset_dir=_path_env("RESEARCH_DATASET_DIR", data_root / "datasets"),
            paper_dir=_path_env("RESEARCH_PAPER_DIR", data_root / "papers"),
            index_dir=_path_env("RESEARCH_INDEX_DIR", data_root / "indexes"),
            run_dir=_path_env("RESEARCH_RUN_DIR", data_root / "runs"),
            cache_dir=_path_env("RESEARCH_CACHE_DIR", data_root / "cache"),
            lock_dir=_path_env("RESEARCH_LOCK_DIR", data_root / "locks"),
            site_artifact_dir=_path_env("RESEARCH_SITE_ARTIFACT_DIR", PROJECT_ROOT / "generated"),
        )

    def directories(self) -> dict[str, Path]:
        return {
            "data_root": self.data_root,
            "corpora": self.corpus_dir,
            "datasets": self.dataset_dir,
            "dataset_raw": self.dataset_dir / "raw",
            "dataset_processed": self.dataset_dir / "processed",
            "dataset_external": self.dataset_dir / "external",
            "dataset_manifests": self.dataset_dir / "manifests",
            "papers": self.paper_dir,
            "paper_pdf": self.paper_dir / "pdf",
            "paper_metadata": self.paper_dir / "metadata",
            "indexes": self.index_dir,
            "index_fulltext": self.index_dir / "fulltext",
            "index_embeddings": self.index_dir / "embeddings",
            "index_citation_graph": self.index_dir / "citation-graph",
            "runs": self.run_dir,
            "run_pilots": self.run_dir / "pilots",
            "run_logs": self.run_dir / "logs",
            "run_exports": self.run_dir / "exports",
            "cache": self.cache_dir,
            "cache_semantic_scholar": self.cache_dir / "semantic-scholar",
            "cache_huggingface": self.cache_dir / "huggingface",
            "cache_torch": self.cache_dir / "torch",
            "cache_xdg": self.cache_dir / "xdg",
            "locks": self.lock_dir,
            "site_artifacts": self.site_artifact_dir,
        }

    def ensure(self) -> None:
        for path in self.directories().values():
            path.mkdir(parents=True, exist_ok=True)

    def safe_summary(self) -> dict[str, object]:
        return {
            "project_root": str(PROJECT_ROOT),
            "data_root": str(self.data_root),
            "directories": {key: str(value) for key, value in self.directories().items()},
            "data_disk": _disk_summary(self.data_root),
            "code_disk": _disk_summary(PROJECT_ROOT),
        }


def resolve_experiment_data_root(storage: StorageSettings | None = None) -> Path:
    """Resolve the machine-local experiment root used by runner/orchestrator.

    Literature/corpus storage and GPU experiment storage may differ. An explicit
    RESEARCH_EXPERIMENT_DATA_ROOT wins; otherwise the local orchestrator profile
    whose repo matches this checkout is authoritative. The generic research data
    root remains the safe fallback for machines without an execution profile.
    """
    storage = storage or StorageSettings.from_env()
    explicit = os.getenv("RESEARCH_EXPERIMENT_DATA_ROOT", "").strip()
    if explicit:
        return Path(explicit).expanduser()
    profile_path = PROJECT_ROOT / "research_pipeline" / "experiment_orchestrator_profiles.json"
    try:
        payload = json.loads(profile_path.read_text(encoding="utf-8"))
        current_repos = {str(PROJECT_ROOT.resolve())}
        # A deployment/repair may run from a clean git worktree whose checkout
        # path differs from the canonical profile repo.  Git stores the common
        # repository in the worktree's .git pointer; treat that canonical root
        # as an equivalent local checkout without weakening machine selection.
        git_pointer = PROJECT_ROOT / ".git"
        if git_pointer.is_file():
            first_line = git_pointer.read_text(encoding="utf-8").splitlines()[0].strip()
            if first_line.startswith("gitdir:"):
                git_dir = Path(first_line.split(":", 1)[1].strip()).expanduser().resolve()
                marker = f"{os.sep}.git{os.sep}worktrees{os.sep}"
                raw_git_dir = str(git_dir)
                if marker in raw_git_dir:
                    canonical_repo = raw_git_dir.split(marker, 1)[0]
                    current_repos.add(str(Path(canonical_repo).resolve()))
        for row in payload.get("servers") or []:
            repo = str(Path(str(row.get("repo") or "")).expanduser().resolve())
            if repo in current_repos and row.get("data_root"):
                return Path(str(row["data_root"])).expanduser()
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        pass
    return storage.data_root


@dataclass(frozen=True, slots=True)
class SemanticScholarSettings:
    api_key: str
    base_url: str = DEFAULT_S2_BASE_URL
    min_interval_seconds: float = 1.15
    timeout_seconds: float = 30.0
    max_retries: int = 4
    cache_ttl_hours: float = 168.0
    cache_dir: Path = DEFAULT_DATA_ROOT / "cache" / "semantic-scholar"

    @classmethod
    def from_env(cls, *, required: bool = True, env_file: Path = DEFAULT_ENV_FILE) -> "SemanticScholarSettings":
        load_env_file(env_file)
        storage = StorageSettings.from_env(env_file=env_file)
        api_key = os.getenv("S2_API_KEY", "").strip()
        if required and not api_key:
            raise RuntimeError(
                "S2_API_KEY is not configured. Copy .env.example to .env and add the approved key."
            )
        min_interval = _float_env("S2_MIN_INTERVAL_SECONDS", 1.15, minimum=1.01)
        return cls(
            api_key=api_key,
            base_url=os.getenv("S2_BASE_URL", DEFAULT_S2_BASE_URL).rstrip("/"),
            min_interval_seconds=min_interval,
            timeout_seconds=_float_env("S2_TIMEOUT_SECONDS", 30.0, minimum=1.0),
            max_retries=_int_env("S2_MAX_RETRIES", 4, minimum=0),
            cache_ttl_hours=_float_env("S2_CACHE_TTL_HOURS", 168.0, minimum=0.0),
            cache_dir=_path_env("S2_CACHE_DIR", storage.cache_dir / "semantic-scholar"),
        )

    @property
    def requests_per_second(self) -> float:
        return 1.0 / self.min_interval_seconds

    def safe_summary(self) -> dict[str, object]:
        return {
            "configured": bool(self.api_key),
            "base_url": self.base_url,
            "min_interval_seconds": self.min_interval_seconds,
            "requests_per_second": round(self.requests_per_second, 3),
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "cache_ttl_hours": self.cache_ttl_hours,
            "cache_dir": str(self.cache_dir),
        }
