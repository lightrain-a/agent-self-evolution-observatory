from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping, Sequence

from research_pipeline.e2_r17_bridge_v4r2_execution_plan import SCREEN, stage_stream_ids, update_tasks
from research_pipeline.e2_r17_search_projection_runner import SearchPool

MIXED_PER_STREAM_MINIMUM = 4


@dataclass(frozen=True)
class StreamSupport:
    stream_id: str
    pool_count: int
    mixed_pool_count: int
    qualifies: bool


@dataclass(frozen=True)
class ScreenSupportResult:
    stage: str
    streams: tuple[StreamSupport, ...]
    all_streams_qualified: bool
    required_mixed_pools_per_stream: int
    replacement_allowed: bool

    def to_dict(self) -> dict:
        return {
            "stage": self.stage,
            "streams": [asdict(row) for row in self.streams],
            "all_streams_qualified": self.all_streams_qualified,
            "required_mixed_pools_per_stream": self.required_mixed_pools_per_stream,
            "replacement_allowed": self.replacement_allowed,
        }


def evaluate_screen_support(
    pools_by_stream: Mapping[str, Sequence[SearchPool]],
) -> ScreenSupportResult:
    expected_streams = stage_stream_ids(SCREEN)
    if tuple(pools_by_stream) != expected_streams:
        raise ValueError("Bridge SCREEN support stream identity/order drift")
    rows: list[StreamSupport] = []
    for stream_id in expected_streams:
        pools = tuple(pools_by_stream[stream_id])
        expected_tasks = update_tasks(stream_id)
        if len(pools) != 8:
            raise ValueError(f"Bridge SCREEN support requires eight pools: {stream_id}")
        if tuple(pool.task_id for pool in pools) != expected_tasks:
            raise ValueError(f"Bridge SCREEN support task order drift: {stream_id}")
        for pool in pools:
            pool.validate()
            if pool.k != 8:
                raise ValueError(f"Bridge SCREEN support requires K=8: {stream_id}/{pool.task_id}")
        mixed = sum(int(pool.mixed_pool) for pool in pools)
        rows.append(
            StreamSupport(
                stream_id=stream_id,
                pool_count=8,
                mixed_pool_count=mixed,
                qualifies=mixed >= MIXED_PER_STREAM_MINIMUM,
            )
        )
    return ScreenSupportResult(
        stage=SCREEN,
        streams=tuple(rows),
        all_streams_qualified=all(row.qualifies for row in rows),
        required_mixed_pools_per_stream=MIXED_PER_STREAM_MINIMUM,
        replacement_allowed=False,
    )


__all__ = [
    "MIXED_PER_STREAM_MINIMUM",
    "StreamSupport",
    "ScreenSupportResult",
    "evaluate_screen_support",
]
