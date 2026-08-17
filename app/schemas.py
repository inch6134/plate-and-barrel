from datetime import date
from enum import StrEnum

from pydantic import BaseModel

from app.metrics import COUNT_METRICS, RATE_METRICS

Metric = StrEnum("Metric", {metric: metric for metric in RATE_METRICS + COUNT_METRICS})


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class Player(BaseModel):
    batter_bam_id: int
    name_first: str
    name_last: str
    side: str
    number: str
    position: str
    height: str
    weight: int
    age: int
    debut_date: str
    throws: str


class StatLine(BaseModel):
    pitches: int
    zone_pitches: int
    out_of_zone_pitches: int
    swings: int
    zone_swings: int
    chases: int
    contacts: int
    whiffs: int
    batted_balls: int
    hard_hits: int
    sweet_spots: int
    barrels: int
    pulled: int
    up_the_middle: int
    opposite: int
    pa: int
    ab: int
    hits: int
    singles: int
    doubles: int
    triples: int
    home_runs: int
    walks: int
    intentional_walks: int
    total_walks: int
    hit_by_pitches: int
    strikeouts: int
    sac_flies: int
    sac_bunts: int
    total_bases: int
    swing_rate: float | None
    zone_swing_rate: float | None
    chase_rate: float | None
    whiff_rate: float | None
    contact_rate: float | None
    avg_exit_velo: float | None
    max_exit_velo: float | None
    avg_launch_angle: float | None
    hard_hit_rate: float | None
    sweet_spot_rate: float | None
    barrel_rate: float | None
    pull_rate: float | None
    center_rate: float | None
    oppo_rate: float | None
    avg_bat_speed: float | None
    avg_attack_angle: float | None
    avg: float | None
    obp: float | None
    slg: float | None
    ops: float | None
    k_rate: float | None
    bb_rate: float | None


class PlayerDetail(BaseModel):
    player: Player
    stats: StatLine


class LeaderboardEntry(BaseModel):
    batter_bam_id: int
    name_first: str
    name_last: str
    value: float
    sample: int


class PitchType(StrEnum):
    FOUR_SEAM = "4S"
    SINKER = "2S"
    CUTTER = "CT"
    SLIDER = "SL"
    SWEEPER = "SW"
    CURVEBALL = "CB"
    CHANGEUP = "CH"
    SPLITTER = "SP"


class PitchFamily(StrEnum):
    FASTBALL = "fastball"
    BREAKING = "breaking"
    OFFSPEED = "offspeed"


class Pitch(BaseModel):
    plate_x: float
    plate_z: float
    in_zone: bool
    pitch_type: str
    batter_side: str
    result: str
    bat_speed: float | None
    exit_velo: float | None


class FilterOption(BaseModel):
    code: str
    count: int


class BatterBox(BaseModel):
    side: str
    pitches: int


class Zone(BaseModel):
    top: float
    bottom: float
    half_width: float
    boxes: list[BatterBox]


class Split(BaseModel):
    bucket: str
    player: StatLine
    team: StatLine


class ContextSplit(BaseModel):
    context: str
    buckets: list[Split]


class SwingProfile(BaseModel):
    player: StatLine
    team: StatLine
    spread: dict[str, float | None]
    zone: Zone
    pitches: list[Pitch]
    contexts: list[ContextSplit]
    pitch_types: list[FilterOption]


class Trajectory(StrEnum):
    GROUND_BALL = "ground_ball"
    LINE_DRIVE = "line_drive"
    FLY_BALL = "fly_ball"
    POPUP = "popup"
    BUNT_GROUNDER = "bunt_grounder"


class Outcome(StrEnum):
    HIT = "hit"
    OUT = "out"


class BattedBall(BaseModel):
    bearing: float
    distance: float
    exit_velo: float
    launch_angle: float
    trajectory: str
    event_type: str
    pitch_type: str
    game_date: date
    is_hit: bool
    hard_hit: bool
    barrel: bool


class SprayChart(BaseModel):
    player: StatLine
    team: StatLine
    batted_balls: list[BattedBall]
    trajectories: list[FilterOption]


class Dimension(StrEnum):
    COUNT = "count"
    OUTS = "outs"
    BASES = "bases"
    INNING = "inning"
    HAND = "hand"
    ROLE = "role"


class Splits(BaseModel):
    dimension: Dimension
    splits: list[Split]


class View(StrEnum):
    SWING = "swing"
    SPRAY = "spray"
    SPLITS = "splits"


class Insight(BaseModel):
    metric: str
    dimension: str | None
    scope: str
    value: float
    baseline: float
    sample: int
    sample_column: str
