import polars as pl
from fastapi import APIRouter, HTTPException

from app.data import batting, roster
from app.metrics import summarize
from app.schemas import Player, PlayerDetail, StatLine

router = APIRouter(prefix="/api", tags=["players"])


@router.get("/players")
def list_players() -> list[Player]:
    return roster().to_dicts()


@router.get("/players/{batter_id}")
def get_player(batter_id: int) -> PlayerDetail:
    player = roster().filter(pl.col("batter_bam_id") == batter_id)
    if player.is_empty():
        raise HTTPException(status_code=404, detail=f"No batter with id {batter_id}")
    stats = summarize(batting().filter(pl.col("batter_bam_id") == batter_id), [])
    return PlayerDetail(player=player.row(0, named=True), stats=stats.row(0, named=True))


@router.get("/team")
def get_team() -> StatLine:
    return summarize(batting(), []).row(0, named=True)
