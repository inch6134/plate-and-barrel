import polars as pl
import polars.selectors as cs

HARD_HIT_MPH = 95.0
SWEET_SPOT_MIN_DEG = 8.0
SWEET_SPOT_MAX_DEG = 32.0
BARREL_MIN_MPH = 98.0
BARREL_MAX_WINDOW_DEG = (8.0, 50.0)

SWING_FLOOR = 20
BATTED_BALL_FLOOR = 10
PA_FLOOR = 20

SWING_METRICS = [
    "swing_rate",
    "zone_swing_rate",
    "chase_rate",
    "whiff_rate",
    "contact_rate",
]
CONTACT_METRICS = [
    "avg_exit_velo",
    "max_exit_velo",
    "avg_launch_angle",
    "hard_hit_rate",
    "sweet_spot_rate",
    "barrel_rate",
    "avg_bat_speed",
    "avg_attack_angle",
]
LINE_METRICS = ["avg", "obp", "slg", "ops", "k_rate", "bb_rate"]

COUNT_METRICS = [
    "pa",
    "ab",
    "hits",
    "doubles",
    "triples",
    "home_runs",
    "total_bases",
    "total_walks",
    "strikeouts",
    "batted_balls",
    "hard_hits",
    "barrels",
]
RATE_METRICS = SWING_METRICS + CONTACT_METRICS + LINE_METRICS

SAMPLE_COLUMNS = (
    {metric: "swings" for metric in SWING_METRICS}
    | {metric: "batted_balls" for metric in CONTACT_METRICS}
    | {metric: "pa" for metric in LINE_METRICS}
    | {metric: "pa" for metric in COUNT_METRICS}
)

FLOORS = {"swings": SWING_FLOOR, "batted_balls": BATTED_BALL_FLOOR, "pa": PA_FLOOR}

HIT_EVENTS = ["single", "double", "triple", "home_run"]

_barrel_low = pl.max_horizontal(
    124 - pl.col("hit_exit_speed"), BARREL_MAX_WINDOW_DEG[0]
)
_barrel_high = pl.min_horizontal(
    (30 + (10 / 9) * (pl.col("hit_exit_speed") - BARREL_MIN_MPH)).round(),
    BARREL_MAX_WINDOW_DEG[1],
)

is_barrel = (
    (pl.col("hit_exit_speed") >= BARREL_MIN_MPH)
    & (pl.col("hit_vertical_angle") >= _barrel_low)
    & (pl.col("hit_vertical_angle") <= _barrel_high)
)


def _on_batted_ball(expr: pl.Expr) -> pl.Expr:
    return pl.when(pl.col("batted_ball")).then(expr).otherwise(None)


def _on_batted_balls(expr: pl.Expr) -> pl.Expr:
    return expr.filter(pl.col("batted_ball"))


def _on_competitive_swings(expr: pl.Expr) -> pl.Expr:
    return expr.filter(pl.col("swing") & ~pl.col("bunt_attempt"))


def _pa_events(*events: str) -> pl.Expr:
    return (pl.col("is_pa") & pl.col("event_type").is_in(events)).sum()


COUNTS = [
    pl.col("is_pitch").sum().alias("pitches"),
    pl.col("in_zone").sum().alias("zone_pitches"),
    (~pl.col("in_zone")).sum().alias("out_of_zone_pitches"),
    pl.col("swing").sum().alias("swings"),
    (pl.col("swing") & pl.col("in_zone")).sum().alias("zone_swings"),
    pl.col("chase").sum().alias("chases"),
    pl.col("contact").sum().alias("contacts"),
    pl.col("swinging_strike").sum().alias("whiffs"),
    pl.col("batted_ball").sum().alias("batted_balls"),
    _on_batted_balls(pl.col("hit_exit_speed")).mean().alias("avg_exit_velo"),
    _on_batted_balls(pl.col("hit_exit_speed")).max().alias("max_exit_velo"),
    _on_batted_balls(pl.col("hit_vertical_angle")).mean().alias("avg_launch_angle"),
    _on_batted_balls(pl.col("hit_exit_speed") >= HARD_HIT_MPH).sum().alias("hard_hits"),
    _on_batted_balls(
        pl.col("hit_vertical_angle").is_between(SWEET_SPOT_MIN_DEG, SWEET_SPOT_MAX_DEG)
    )
    .sum()
    .alias("sweet_spots"),
    _on_batted_balls(is_barrel).sum().alias("barrels"),
    _on_competitive_swings(pl.col("bat_speed")).mean().alias("avg_bat_speed"),
    _on_competitive_swings(pl.col("vertical_bat_attack_angle"))
    .mean()
    .alias("avg_attack_angle"),
    pl.col("is_pa").sum().alias("pa"),
    _pa_events("single").alias("singles"),
    _pa_events("double").alias("doubles"),
    _pa_events("triple").alias("triples"),
    _pa_events("home_run").alias("home_runs"),
    _pa_events("walk").alias("walks"),
    _pa_events("intent_walk").alias("intentional_walks"),
    _pa_events("hit_by_pitch").alias("hit_by_pitches"),
    _pa_events("strikeout").alias("strikeouts"),
    _pa_events("sac_fly").alias("sac_flies"),
    _pa_events("sac_bunt").alias("sac_bunts"),
]

TOTALS = [
    (
        pl.col("singles") + pl.col("doubles") + pl.col("triples") + pl.col("home_runs")
    ).alias("hits"),
    (pl.col("walks") + pl.col("intentional_walks")).alias("total_walks"),
    (
        pl.col("singles")
        + 2 * pl.col("doubles")
        + 3 * pl.col("triples")
        + 4 * pl.col("home_runs")
    ).alias("total_bases"),
]

AT_BATS = (
    pl.col("pa")
    - pl.col("total_walks")
    - pl.col("hit_by_pitches")
    - pl.col("sac_flies")
    - pl.col("sac_bunts")
).alias("ab")

RATES = [
    (pl.col("swings") / pl.col("pitches")).alias("swing_rate"),
    (pl.col("zone_swings") / pl.col("zone_pitches")).alias("zone_swing_rate"),
    (pl.col("chases") / pl.col("out_of_zone_pitches")).alias("chase_rate"),
    (pl.col("whiffs") / pl.col("swings")).alias("whiff_rate"),
    (pl.col("contacts") / pl.col("swings")).alias("contact_rate"),
    (pl.col("hard_hits") / pl.col("batted_balls")).alias("hard_hit_rate"),
    (pl.col("sweet_spots") / pl.col("batted_balls")).alias("sweet_spot_rate"),
    (pl.col("barrels") / pl.col("batted_balls")).alias("barrel_rate"),
    (pl.col("hits") / pl.col("ab")).alias("avg"),
    (
        (pl.col("hits") + pl.col("total_walks") + pl.col("hit_by_pitches"))
        / (
            pl.col("ab")
            + pl.col("total_walks")
            + pl.col("hit_by_pitches")
            + pl.col("sac_flies")
        )
    ).alias("obp"),
    (pl.col("total_bases") / pl.col("ab")).alias("slg"),
    (pl.col("strikeouts") / pl.col("pa")).alias("k_rate"),
    (pl.col("total_walks") / pl.col("pa")).alias("bb_rate"),
]

OPS = (pl.col("obp") + pl.col("slg")).alias("ops")

SWING_DETAIL = [
    pl.col("bat_speed"),
    pl.col("vertical_bat_attack_angle").alias("attack_angle"),
    pl.col("pitch_type"),
    pl.col("in_zone"),
    pl.when(pl.col("in_play"))
    .then(pl.lit("in_play"))
    .when(pl.col("foul"))
    .then(pl.lit("foul"))
    .otherwise(pl.lit("whiff"))
    .alias("result"),
    pl.col("event_type"),
    _on_batted_ball(pl.col("hit_exit_speed")).alias("exit_velo"),
    _on_batted_ball(pl.col("hit_vertical_angle")).alias("launch_angle"),
    _on_batted_ball(pl.col("hit_distance")).alias("distance"),
    (pl.col("batted_ball") & (pl.col("hit_exit_speed") >= HARD_HIT_MPH)).alias(
        "hard_hit"
    ),
    (pl.col("batted_ball") & is_barrel).alias("barrel"),
]

SPRAY_DETAIL = [
    pl.col("hit_bearing").alias("bearing"),
    pl.col("hit_distance").alias("distance"),
    pl.col("hit_exit_speed").alias("exit_velo"),
    pl.col("hit_vertical_angle").alias("launch_angle"),
    pl.col("hit_trajectory").alias("trajectory"),
    pl.col("event_type"),
    pl.col("pitch_type"),
    pl.col("game_date"),
    pl.col("event_type").is_in(HIT_EVENTS).alias("is_hit"),
    (pl.col("hit_exit_speed") >= HARD_HIT_MPH).alias("hard_hit"),
    is_barrel.alias("barrel"),
]


def summarize(frame: pl.DataFrame, by: list[str]) -> pl.DataFrame:
    return (
        frame.group_by(by)
        .agg(COUNTS)
        .with_columns(TOTALS)
        .with_columns(AT_BATS)
        .with_columns(RATES)
        .with_columns(OPS)
        .with_columns(cs.float().fill_nan(None))
    )


def apply_floors(frame: pl.DataFrame) -> pl.DataFrame:
    return frame.with_columns([_gate(metric) for metric in RATE_METRICS])


def _gate(metric: str) -> pl.Expr:
    sample = SAMPLE_COLUMNS[metric]
    return (
        pl.when(pl.col(sample) >= FLOORS[sample])
        .then(pl.col(metric))
        .otherwise(None)
        .alias(metric)
    )
