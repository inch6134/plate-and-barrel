from functools import lru_cache
from pathlib import Path

import polars as pl

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PITCH_CSV = DATA_DIR / "padres_project_data.csv"
BIOS_JSON = DATA_DIR / "players.json"

TEAM = "San Diego Padres"

COLUMNS = [
    "game_date",
    "inning",
    "pre_balls",
    "pre_strikes",
    "pre_outs",
    "pre_basecode",
    "batter_team",
    "batter_bam_id",
    "batter_name_first",
    "batter_name_last",
    "batter_side",
    "pitcher_side",
    "pitcher_type",
    "is_pitch",
    "pitch_type",
    "plate_x",
    "plate_z",
    "strikezone_top",
    "strikezone_bot",
    "in_zone",
    "swing",
    "contact",
    "in_play",
    "chase",
    "swinging_strike",
    "called_strike",
    "foul",
    "ball",
    "bunt_attempt",
    "bat_speed",
    "vertical_bat_attack_angle",
    "hit_trajectory",
    "hit_exit_speed",
    "hit_vertical_angle",
    "hit_distance",
    "hit_bearing",
    "event_type",
    "terminating",
]

ZONE_HALF_WIDTH_FT = 0.83

FASTBALLS = ["4S", "2S", "CT"]
BREAKING = ["SL", "SW", "CB"]

CONTEXTS = {
    "location": ("zone_state", ["zone", "outside"]),
    "count": ("strike_state", ["under_two", "two_strikes"]),
    "family": ("pitch_family", ["fastball", "breaking", "offspeed"]),
}

DIMENSIONS = {
    "count": ("count_state", ["ahead", "even", "behind"]),
    "outs": ("out_state", ["0", "1", "2"]),
    "bases": ("base_state", ["empty", "on_base", "scoring"]),
    "inning": ("inning_band", ["early", "middle", "late"]),
    "hand": ("pitcher_side", ["L", "R"]),
    "role": ("pitcher_role", ["starter", "reliever"]),
}

BASERUNNING_EVENTS = [
    "caught_stealing_1b",
    "caught_stealing_2b",
    "caught_stealing_3b",
    "caught_stealing_home",
    "stolen_base_1b",
    "stolen_base_2b",
    "stolen_base_3b",
    "stolen_base_home",
    "pickoff_1b",
    "pickoff_2b",
    "pickoff_3b",
    "pickoff_caught_stealing_1b",
    "pickoff_caught_stealing_2b",
    "pickoff_caught_stealing_3b",
]


@lru_cache(maxsize=1)
def batting() -> pl.DataFrame:
    return (
        pl.read_csv(
            PITCH_CSV, columns=COLUMNS, try_parse_dates=True, infer_schema_length=None
        )
        .filter(pl.col("batter_team") == TEAM)
        .drop("batter_team")
        .with_columns(
            is_pa=pl.col("terminating")
            & ~pl.col("event_type").is_in(BASERUNNING_EVENTS),
            batted_ball=pl.col("in_play") & pl.col("hit_exit_speed").is_not_null(),
            spray_field=pl.when(pl.col("hit_bearing").abs() <= 15)
            .then(pl.lit("center"))
            .when((pl.col("batter_side") == "R") == (pl.col("hit_bearing") < 0))
            .then(pl.lit("pull"))
            .otherwise(pl.lit("oppo")),
            count_state=pl.when(pl.col("pre_balls") > pl.col("pre_strikes"))
            .then(pl.lit("ahead"))
            .when(pl.col("pre_balls") == pl.col("pre_strikes"))
            .then(pl.lit("even"))
            .otherwise(pl.lit("behind")),
            inning_band=pl.when(pl.col("inning") <= 3)
            .then(pl.lit("early"))
            .when(pl.col("inning") <= 6)
            .then(pl.lit("middle"))
            .otherwise(pl.lit("late")),
            base_state=pl.when(pl.col("pre_basecode") == 0)
            .then(pl.lit("empty"))
            .when(pl.col("pre_basecode") >= 10)
            .then(pl.lit("scoring"))
            .otherwise(pl.lit("on_base")),
            out_state=pl.col("pre_outs").cast(pl.Utf8),
            zone_state=pl.when(pl.col("in_zone"))
            .then(pl.lit("zone"))
            .when(pl.col("in_zone").is_not_null())
            .then(pl.lit("outside"))
            .otherwise(None),
            strike_state=pl.when(pl.col("pre_strikes") == 2)
            .then(pl.lit("two_strikes"))
            .otherwise(pl.lit("under_two")),
            pitch_family=pl.when(pl.col("pitch_type").is_in(FASTBALLS))
            .then(pl.lit("fastball"))
            .when(pl.col("pitch_type").is_in(BREAKING))
            .then(pl.lit("breaking"))
            .when(pl.col("pitch_type").is_not_null())
            .then(pl.lit("offspeed"))
            .otherwise(None),
            pitcher_role=pl.when(pl.col("pitcher_type") == "S")
            .then(pl.lit("starter"))
            .otherwise(pl.lit("reliever")),
        )
    )


@lru_cache(maxsize=1)
def roster() -> pl.DataFrame:
    as_of = batting()["game_date"].max()
    identity = (
        batting()
        .group_by("batter_bam_id")
        .agg(
            name_first=pl.col("batter_name_first").first(),
            name_last=pl.col("batter_name_last").first(),
            side=pl.when(pl.col("batter_side").n_unique() > 1)
            .then(pl.lit("S"))
            .otherwise(pl.col("batter_side").first()),
        )
    )
    return (
        identity.join(pl.read_json(BIOS_JSON), on="batter_bam_id", how="left")
        .with_columns(
            age=((as_of - pl.col("birth_date").str.to_date()).dt.total_days() / 365.25)
            .floor()
            .cast(pl.Int32)
        )
        .sort("name_last")
    )
