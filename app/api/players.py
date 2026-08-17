import polars as pl
from fastapi import APIRouter

from app.data import CONTEXTS, DIMENSIONS, ZONE_HALF_WIDTH_FT, batting, roster
from app.api.deps import player_rows
from app.insights import overall_spread
from app.metrics import (
    HIT_EVENTS,
    PITCH_DETAIL,
    SPRAY_DETAIL,
    summarize,
    bucketed,
)
from app.schemas import (
    ContextSplit,
    Dimension,
    Outcome,
    PitchFamily,
    PitchType,
    Player,
    PlayerDetail,
    Split,
    Splits,
    SprayChart,
    StatLine,
    SwingProfile,
    Trajectory,
    Zone,
)

router = APIRouter(prefix="/api", tags=["players"])


def _of_type(
    frame: pl.DataFrame, pitch_type: PitchType | None, family: PitchFamily | None
) -> pl.DataFrame:
    matches = []
    if pitch_type is not None:
        matches.append(pl.col("pitch_type") == pitch_type)
    if family is not None:
        matches.append(pl.col("pitch_family") == family)
    return frame.filter(*matches)


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


def _zone_of(rows: pl.DataFrame) -> Zone:
    thrown = rows.filter(pl.col("is_pitch"))
    boxes = (
        thrown.group_by(side="batter_side")
        .agg(pitches=pl.len())
        .sort("pitches", descending=True)
    )
    return Zone(
        top=thrown["strikezone_top"].max(),
        bottom=thrown["strikezone_bot"].min(),
        half_width=ZONE_HALF_WIDTH_FT,
        boxes=boxes.to_dicts(),
    )


def _contexts_of(rows: pl.DataFrame) -> list[ContextSplit]:
    thrown = rows.filter(pl.col("is_pitch"))
    league = batting().filter(pl.col("is_pitch"))
    contexts = []
    for context, (column, buckets) in CONTEXTS.items():
        baseline = {row[column]: row for row in bucketed(league, column, buckets)}
        contexts.append(
            ContextSplit(
                context=context,
                buckets=[
                    Split(bucket=row[column], player=row, team=baseline[row[column]])
                    for row in bucketed(thrown, column, buckets)
                ],
            )
        )
    return contexts


@router.get("/players/{batter_id}/swing-profile")
def get_swing_profile(
    batter_id: int,
    pitch_type: PitchType | None = None,
    family: PitchFamily | None = None,
) -> SwingProfile:
    rows = player_rows(batter_id)
    scoped = _of_type(rows, pitch_type, family)
    options = (
        rows.filter(pl.col("is_pitch"))
        .group_by(code="pitch_type")
        .agg(count=pl.len())
        .sort("count", descending=True)
    )
    return SwingProfile(
        player=summarize(scoped, []).row(0, named=True),
        team=summarize(_of_type(batting(), pitch_type, family), []).row(0, named=True),
        spread=overall_spread(),
        zone=_zone_of(rows),
        pitches=scoped.filter(pl.col("is_pitch")).select(PITCH_DETAIL).to_dicts(),
        contexts=_contexts_of(scoped),
        pitch_types=options.to_dicts(),
    )


@router.get("/players/{batter_id}/spray-chart")
def get_spray_chart(
    batter_id: int,
    trajectory: Trajectory | None = None,
    outcome: Outcome | None = None,
) -> SprayChart:
    matches = _spray_filters(trajectory, outcome)
    batted = player_rows(batter_id).filter(pl.col("batted_ball"))
    scoped = batted.filter(*matches)
    team = batting().filter(pl.col("batted_ball")).filter(*matches)
    trajectories = (
        batted.group_by(code="hit_trajectory")
        .agg(count=pl.len())
        .sort("count", descending=True)
    )
    return SprayChart(
        player=summarize(scoped, []).row(0, named=True),
        team=summarize(team, []).row(0, named=True),
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
