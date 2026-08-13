# 10.42.8.52 Storage Layout

The authoritative execution host is `10.42.8.52` (`admin01-NF5468M5`).

## Code disk

```text
/home/wyt/code/agent-self-evolution-observatory
```

Keep only source code, configuration templates, tests, documentation, and small browser-consumable generated snapshots here.

## Automation checkout

```text
/home/wyt/code/agent-self-evolution-observatory-automation
```

The daily and weekly systemd cycles run only from this detached Git worktree. The installer creates it from `origin/main`; every service invocation fetches and performs an `--ff-only` merge before starting. The canonical checkout remains available for human work and supplies the ignored `.env`, so uncommitted research files cannot block timer publication.

## Local data disk

```text
/data/wyt/agent-self-evolution-observatory
```

`/data` is the server-local 33 TB ext4 disk. It is the default location for all large or frequently accessed research artifacts:

```text
corpora/                 Semantic Scholar and future OpenAlex/full-text corpora
datasets/raw/            immutable downloaded datasets
datasets/processed/      derived and normalized datasets
datasets/external/       externally managed datasets
datasets/manifests/      checksums, licenses, splits, and provenance
papers/pdf/              locally retained open-access PDFs
papers/metadata/         parsed paper metadata
indexes/fulltext/         lexical/full-text indexes
indexes/embeddings/       vector indexes
indexes/citation-graph/   citation graph artifacts
runs/pilots/              bounded falsification pilots
runs/logs/                execution logs
runs/exports/             large analysis exports
cache/semantic-scholar/   API response cache
cache/huggingface/        model and dataset cache
cache/torch/              Torch cache
cache/xdg/                other tool caches
locks/                    process and provider locks
```

The NFS mounts under `/mnt` are reserved for long-term archive or cross-machine sharing. They are not used as the primary cache or index location because the local ext4 data disk is faster and currently has substantially more free space.

## Required execution wrapper

Run data-heavy tasks through:

```bash
cd /home/wyt/code/agent-self-evolution-observatory
./scripts/on-52.sh python3 -m research_pipeline --sync-s2
```

The wrapper refuses to execute on the wrong hostname, loads the ignored server `.env`, exports Hugging Face/Torch/XDG cache variables, and initializes the storage tree before running the command.

Inspect the active layout without exposing credentials:

```bash
./scripts/on-52.sh python3 -m research_pipeline --storage-status
./scripts/on-52.sh python3 -m research_pipeline --s2-status
```
