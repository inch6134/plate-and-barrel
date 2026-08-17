from functools import lru_cache

import polars as pl

from app.data import DIMENSIONS, batting
from app.metrics import (
    RATE_METRICS,
    SAMPLE_COLUMNS,
    SWING_METRICS,
    apply_floors,
    bucketed,
    summarize,
)
from app.schemas import View

VIEW_METRICS = {
    View.SWING: SWING_METRICS,
    View.SPRAY: [
        "pull_rate",
        "center_rate",
        "oppo_rate",
        "avg_exit_velo",
        "avg_launch_angle",
        "hard_hit_rate",
        "sweet_spot_rate",
        "barrel_rate",
    ],
    View.SPLITS: SWING_METRICS + ["avg_exit_velo", "hard_hit_rate", "barrel_rate"],
}


def _spread_of(frame: pl.DataFrame) -> dict[str, float | None]:
    return {metric: frame[metric].std() for metric in RATE_METRICS}


@lru_cache(maxsize=1)
def overall_spread() -> dict[str, float | None]:
    return _spread_of(apply_floors(summarize(batting(), ["batter_bam_id"])))


@lru_cache(maxsize=1)
def _bucket_spreads() -> dict[tuple[str, str], dict[str, float | None]]:
    spreads = {}
    for column, _ in DIMENSIONS.values():
        table = apply_floors(summarize(batting(), ["batter_bam_id", column]))
        for (bucket,), group in table.group_by(column):
            spreads[(column, bucket)] = _spread_of(group)
    return spreads


def _compare(
    metrics: list[str],
    dimension: str | None,
    scope: str,
    player: dict,
    team: dict,
    spread: dict[str, float | None],
) -> list[dict]:
    return [
        {
            "metric": metric,
            "dimension": dimension,
            "scope": scope,
            "value": player[metric],
            "baseline": team[metric],
            "sample": player[SAMPLE_COLUMNS[metric]],
            "sample_column": SAMPLE_COLUMNS[metric],
            "score": abs(player[metric] - team[metric]) / spread[metric],
        }
        for metric in metrics
        if player[metric] is not None and spread[metric]
    ]


def _overall(rows: pl.DataFrame, metrics: list[str]) -> list[dict]:
    return _compare(
        metrics,
        None,
        "overall",
        apply_floors(summarize(rows, [])).row(0, named=True),
        summarize(batting(), []).row(0, named=True),
        overall_spread(),
    )


def _across_dimensions(rows: pl.DataFrame, metrics: list[str]) -> list[dict]:
    found = []
    for dimension, (column, buckets) in DIMENSIONS.items():
        baseline = {row[column]: row for row in bucketed(batting(), column, buckets)}
        for row in bucketed(rows, column, buckets):
            found.extend(
                _compare(
                    metrics,
                    dimension,
                    row[column],
                    row,
                    baseline[row[column]],
                    _bucket_spreads()[(column, row[column])],
                )
            )
    return found


def _strongest_per_metric(found: list[dict], limit: int) -> list[dict]:
    ranked = sorted(found, key=lambda insight: insight["score"], reverse=True)
    seen: set[str] = set()
    picked = []
    for insight in ranked:
        if insight["metric"] not in seen:
            seen.add(insight["metric"])
            picked.append(insight)
    return picked[:limit]


def insights_for(rows: pl.DataFrame, view: View, limit: int = 3) -> list[dict]:
    metrics = VIEW_METRICS[view]
    found = (
        _across_dimensions(rows, metrics)
        if view is View.SPLITS
        else _overall(rows, metrics)
    )
    return _strongest_per_metric(found, limit)
