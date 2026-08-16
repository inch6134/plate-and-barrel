import polars as pl
from fastapi import HTTPException

from app.data import batting


def player_rows(batter_id: int) -> pl.DataFrame:
    rows = batting().filter(pl.col("batter_bam_id") == batter_id)
    if rows.is_empty():
        raise HTTPException(status_code=404, detail=f"No batter with id {batter_id}")
    return rows
