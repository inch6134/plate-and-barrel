import polars as pl
from fastapi import APIRouter

from app.data import DIMENSIONS, batting, roster
from app.api.deps import player_rows
from app.metrics import (
    HIT_EVENTS,
    SPRAY_DETAIL,
    SWING_DETAIL,
    summarize,
    bucketed,
)
from app.schemas import (
    Dimension,
    Outcome,
    PitchType,
    Player,
    PlayerDetail,
    Split,
    Splits,
    SprayChart,
    StatLine,
    SwingProfile,
    Trajectory,
)

router = APIRouter(prefix="/api", tags=["players"])


def _of_type(frame: pl.DataFrame, pitch_type: PitchType | None) -> pl.DataFrame:
    return (
        frame
        if pitch_type is None
        else frame.filter(pl.col("pitch_type") == pitch_type)
    )


def _spray_filters(
    trajectory: Trajectory | None, outcome: Outcome | None
) -> list[pl.Expr]:
    matches = []
    if trajectory is not None:
        matches.append(pl.col("hit_trajectory") == trajectory)
    if outcome is not None:
        matches.append(
            pl.col("event_type").is_in(HIT_EVENTS) == (outcome is Outcome.HIT)
        )
    return matches


@router.get("/players")
def list_players() -> list[Player]:
    return roster().to_dicts()


@router.get("/players/{batter_id}")
def get_player(batter_id: int) -> PlayerDetail:
    stats = summarize(player_rows(batter_id), [])
    player = roster().filter(pl.col("batter_bam_id") == batter_id)
    return PlayerDetail(
        player=player.row(0, named=True), stats=stats.row(0, named=True)
    )


@router.get("/players/{batter_id}/swing-profile")
def get_swing_profile(
    batter_id: int, pitch_type: PitchType | None = None
) -> SwingProfile:
    rows = player_rows(batter_id)
    scoped = _of_type(rows, pitch_type)
    swings = scoped.filter(
        pl.col("swing") & ~pl.col("bunt_attempt") & pl.col("bat_speed").is_not_null()
    )
    options = (
        rows.filter(pl.col("is_pitch"))
        .group_by(code="pitch_type")
        .agg(count=pl.len())
        .sort("count", descending=True)
    )
    return SwingProfile(
        player=summarize(scoped, []).row(0, named=True),
        team=summarize(_of_type(batting(), pitch_type), []).row(0, named=True),
        swings=swings.select(SWING_DETAIL).to_dicts(),
        pitch_types=options.to_dicts(),
    )


@router.get("/players/{batter_id}/spray-chart")
def get_spray_chart(
    batter_id: int,
    trajectory: Trajectory | None = None,
    outcome: Outcome | None = None,
) -> SprayChart:
    batted = player_rows(batter_id).filter(pl.col("batted_ball"))
    scoped = batted.filter(*_spray_filters(trajectory, outcome))
    trajectories = (
        batted.group_by(code="hit_trajectory")
        .agg(count=pl.len())
        .sort("count", descending=True)
    )
    return SprayChart(
        batted_balls=scoped.select(SPRAY_DETAIL).to_dicts(),
        trajectories=trajectories.to_dicts(),
    )


@router.get("/players/{batter_id}/splits")
def get_splits(batter_id: int, dimension: Dimension = Dimension.COUNT) -> Splits:
    column, buckets = DIMENSIONS[dimension]
    baseline = {row[column]: row for row in bucketed(batting(), column, buckets)}
    return Splits(
        dimension=dimension,
        splits=[
            Split(bucket=row[column], player=row, team=baseline[row[column]])
            for row in bucketed(player_rows(batter_id), column, buckets)
        ],
    )


@router.get("/team")
def get_team() -> StatLine:
    return summarize(batting(), []).row(0, named=True)
