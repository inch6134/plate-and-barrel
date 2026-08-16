import polars as pl
from fastapi import APIRouter

from app.data import batting, roster
from app.metrics import SAMPLE_COLUMNS, apply_floors, summarize
from app.schemas import LeaderboardEntry, Metric, SortOrder

router = APIRouter(prefix="/api", tags=["leaderboard"])


@router.get("/leaderboard")
def get_leaderboard(metric: Metric, order: SortOrder = SortOrder.DESC) -> list[LeaderboardEntry]:
    sample = SAMPLE_COLUMNS[metric]
    ranked = (
        apply_floors(summarize(batting(), ["batter_bam_id"]))
        .join(roster().select("batter_bam_id", "name_first", "name_last"), on="batter_bam_id")
        .drop_nulls(metric)
        .sort(metric, descending=order is SortOrder.DESC)
    )
    return ranked.select(
        "batter_bam_id",
        "name_first",
        "name_last",
        pl.col(metric).alias("value"),
        pl.col(sample).alias("sample"),
    ).to_dicts()
