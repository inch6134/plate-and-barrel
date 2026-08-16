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


class Swing(BaseModel):
    bat_speed: float
    attack_angle: float | None
    pitch_type: str
    in_zone: bool
    result: str
    event_type: str | None
    exit_velo: float | None
    launch_angle: float | None
    distance: float | None
    hard_hit: bool
    barrel: bool


class PitchTypeOption(BaseModel):
    code: str
    pitches: int


class SwingProfile(BaseModel):
    player: StatLine
    team: StatLine
    swings: list[Swing]
    pitch_types: list[PitchTypeOption]
