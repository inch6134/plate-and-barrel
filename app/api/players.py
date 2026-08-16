import polars as pl
from fastapi import APIRouter, HTTPException

from app.data import batting, roster
from app.metrics import SWING_DETAIL, summarize
from app.schemas import (
    PitchType,
    Player,
    PlayerDetail,
    StatLine,
    SwingProfile,
)

router = APIRouter(prefix="/api", tags=["players"])


def _rows_for(batter_id: int) -> pl.DataFrame:
    rows = batting().filter(pl.col("batter_bam_id") == batter_id)
    if rows.is_empty():
        raise HTTPException(status_code=404, detail=f"No batter with id {batter_id}")
    return rows


def _of_type(frame: pl.DataFrame, pitch_type: PitchType | None) -> pl.DataFrame:
    return (
        frame
        if pitch_type is None
        else frame.filter(pl.col("pitch_type") == pitch_type)
    )


@router.get("/players")
def list_players() -> list[Player]:
    return roster().to_dicts()


@router.get("/players/{batter_id}")
def get_player(batter_id: int) -> PlayerDetail:
    stats = summarize(_rows_for(batter_id), [])
    player = roster().filter(pl.col("batter_bam_id") == batter_id)
    return PlayerDetail(
        player=player.row(0, named=True), stats=stats.row(0, named=True)
    )


@router.get("/players/{batter_id}/swing-profile")
def get_swing_profile(
    batter_id: int, pitch_type: PitchType | None = None
) -> SwingProfile:
    rows = _rows_for(batter_id)
    scoped = _of_type(rows, pitch_type)
    swings = scoped.filter(
        pl.col("swing") & ~pl.col("bunt_attempt") & pl.col("bat_speed").is_not_null()
    )
    options = (
        rows.filter(pl.col("is_pitch"))
        .group_by(code="pitch_type")
        .agg(pitches=pl.len())
        .sort("pitches", descending=True)
    )
    return SwingProfile(
        player=summarize(scoped, []).row(0, named=True),
        team=summarize(_of_type(batting(), pitch_type), []).row(0, named=True),
        swings=swings.select(SWING_DETAIL).to_dicts(),
        pitch_types=options.to_dicts(),
    )


@router.get("/team")
def get_team() -> StatLine:
    return summarize(batting(), []).row(0, named=True)
